#!/usr/bin/env python3
"""Sample active Arbitrum wallets for Tier-2 benchmark pool (BQ or local parquet fallback)."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from google.cloud import bigquery
from google.cloud.bigquery import QueryJobConfig, ScalarQueryParameter
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402
    ROOT,
    build_tier2_wallet_pool,
    derive_wallets_from_reputation_parquet,
    format_bytes,
    load_config,
    load_json,
    rank_wallets_by_activity,
    read_sql,
    save_extraction_wallet_set,
    save_json,
)
from project_paths import PROCESSED  # noqa: E402

OBSERVATION_MONTHS = [
    ("2025-12", "2025-12-01 00:00:00 UTC", "2026-01-01 00:00:00 UTC"),
    ("2026-01", "2026-01-01 00:00:00 UTC", "2026-02-01 00:00:00 UTC"),
    ("2026-02", "2026-02-01 00:00:00 UTC", "2026-03-01 00:00:00 UTC"),
    ("2026-03", "2026-03-01 00:00:00 UTC", "2026-04-01 00:00:00 UTC"),
    ("2026-04", "2026-04-01 00:00:00 UTC", "2026-05-01 00:00:00 UTC"),
    ("2026-05", "2026-05-01 00:00:00 UTC", "2026-06-01 00:00:00 UTC"),
]


def get_client(config: dict) -> bigquery.Client:
    project = config.get("bigquery", {}).get("project_id")
    return bigquery.Client(project=project)


def sample_from_parquet(config: dict, limit: int) -> pd.DataFrame:
    rep = config["reputation"]["paths"]
    allowances = pd.read_parquet(rep["latest_allowances"])
    transfers = pd.read_parquet(rep["transfer_events"])
    derived = derive_wallets_from_reputation_parquet(allowances, transfers)
    ranked = rank_wallets_by_activity(derived, transfers, allowances)
    return pd.DataFrame({"wallet": ranked[:limit]})


def monthly_cache_dir(config: dict) -> Path:
    bench = config.get("benchmark") or {}
    rel = bench.get("active_wallet_cache_dir", f"{PROCESSED}/active-wallet-sampling-cache")
    path = Path(rel)
    if not path.is_absolute():
        path = ROOT / path
    return path


def sample_from_bigquery_batched(
    config: dict, limit: int, dry_run: bool, resume: bool = False
) -> tuple[pd.DataFrame, int]:
    """Monthly batched active-wallet sampling (stays under per-query byte cap)."""
    client = get_client(config)
    rep = config["reputation"]
    logs_fqn = config["bigquery"]["logs_fqn"]
    sql = read_sql("arbitrum_active_wallets_month.sql").replace("__LOGS_FQN__", logs_fqn)
    budget_limit = config.get("budget", {}).get("max_bytes_per_query", 0)
    cache_dir = monthly_cache_dir(config)
    activity: dict[str, int] = {}
    total_bytes = 0

    for label, start_ts, end_ts in tqdm(OBSERVATION_MONTHS, desc="Active wallets", unit="month"):
        cache_path = cache_dir / f"{label}.parquet"
        params = [
            ScalarQueryParameter("start_ts", "STRING", start_ts),
            ScalarQueryParameter("end_ts", "STRING", end_ts),
            ScalarQueryParameter("transfer_topic0", "STRING", rep["transfer_topic0"]),
        ]
        job_config = QueryJobConfig(
            dry_run=dry_run,
            use_query_cache=False,
            query_parameters=params,
        )
        if dry_run:
            job = client.query(sql, job_config=job_config)
            month_bytes = int(job.total_bytes_processed or 0)
            total_bytes += month_bytes
            print(f"  {label}: {format_bytes(month_bytes)}")
            if budget_limit and month_bytes > budget_limit:
                raise RuntimeError(
                    f"{label} exceeds per-query budget ({format_bytes(budget_limit)})"
                )
            continue

        if resume and cache_path.exists():
            df = pd.read_parquet(cache_path)
            print(f"  {label}: loaded cache ({len(df)} rows)")
        else:
            job = client.query(sql, job_config=job_config)
            month_bytes = int(job.total_bytes_processed or 0)
            total_bytes += month_bytes
            print(f"  {label}: {format_bytes(month_bytes)}")
            if budget_limit and month_bytes > budget_limit:
                raise RuntimeError(
                    f"{label} exceeds per-query budget ({format_bytes(budget_limit)})"
                )
            df = job.to_dataframe(progress_bar_type="tqdm")
            if not df.empty:
                cache_dir.mkdir(parents=True, exist_ok=True)
                df.to_parquet(cache_path, index=False)
                print(f"  {label}: cached -> {cache_path}")
        if df.empty:
            continue
        for wallet, act in zip(df["wallet"].astype(str).str.lower(), df["activity"]):
            activity[wallet] = activity.get(wallet, 0) + int(act)

    if dry_run:
        return pd.DataFrame(columns=["wallet"]), total_bytes

    ranked = sorted(activity.keys(), key=lambda w: (-activity[w], w))
    return pd.DataFrame({"wallet": ranked[:limit]}), total_bytes


def sample_from_bigquery(
    config: dict, limit: int, dry_run: bool, resume: bool = False
) -> tuple[pd.DataFrame, int]:
    return sample_from_bigquery_batched(config, limit, dry_run, resume=resume)


def load_gmx_wallets(config: dict) -> list[str]:
    path = Path(config["paths"]["wallet_rankings"])
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}; run compute_rankings.py first.")
    df = pd.read_parquet(path)
    return sorted(df["wallet"].astype(str).str.lower().unique().tolist())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--from-parquet",
        action="store_true",
        help="Derive supplemental wallets from existing reputation parquet (no BQ)",
    )
    parser.add_argument("--dry-run", action="store_true", help="BQ dry-run only")
    parser.add_argument("--extract", action="store_true", help="Write supplemental + extraction wallet sets")
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Reuse cached monthly BQ parquet under active_wallet_cache_dir",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Supplemental wallet count (default: target_wallets - gmx_count)",
    )
    args = parser.parse_args()

    if not args.from_parquet and not args.dry_run and not args.extract:
        parser.error("Specify --from-parquet, --dry-run, or --extract")

    config = load_config()
    bench = config.get("benchmark") or {}
    target = int(bench.get("target_wallets", 100000))
    gmx_wallets = load_gmx_wallets(config)
    supplemental_limit = args.limit or max(0, target - len(gmx_wallets))

    manifest_path = Path(config["paths"]["manifest"])
    manifest = load_json(manifest_path)
    sample_meta: dict = {
        "at": datetime.now(timezone.utc).isoformat(),
        "gmx_wallet_count": len(gmx_wallets),
        "target_wallets": target,
        "supplemental_limit": supplemental_limit,
    }

    if args.from_parquet:
        supplemental_df = sample_from_parquet(config, supplemental_limit)
        sample_meta["source"] = "reputation_parquet"
        sample_meta["bytes_processed"] = 0
        print(f"Derived {len(supplemental_df)} supplemental wallets from local parquet")
    else:
        try:
            supplemental_df, bytes_processed = sample_from_bigquery(
                config, supplemental_limit, dry_run=args.dry_run, resume=args.resume
            )
            sample_meta["source"] = "bigquery_monthly"
            sample_meta["bytes_processed"] = bytes_processed
            print(f"BQ dry-run total: {format_bytes(bytes_processed)}")
        except Exception as exc:
            print(f"BigQuery error: {exc}")
            print("Fallback: use --from-parquet for offline wallet pool derivation.")
            return 1

    if args.dry_run:
        manifest["supplemental_wallet_sample"] = sample_meta
        save_json(manifest_path, manifest)
        print("Dry-run complete.")
        return 0

    if not args.extract:
        return 0

    supplemental_path = Path(bench["supplemental_path"])
    supplemental_path.parent.mkdir(parents=True, exist_ok=True)
    supplemental_df.to_parquet(supplemental_path, index=False)
    print(f"Wrote supplemental wallets -> {supplemental_path} ({len(supplemental_df)} rows)")

    rep = config["reputation"]["paths"]
    allowances = pd.read_parquet(rep["latest_allowances"])
    transfers = pd.read_parquet(rep["transfer_events"])
    pool, pool_meta = build_tier2_wallet_pool(
        gmx_wallets, allowances, transfers, config, supplemental_path=supplemental_path
    )
    wallet_set_path = save_extraction_wallet_set(pool, config)
    sample_meta["pool_meta"] = pool_meta
    sample_meta["supplemental_path"] = str(supplemental_path)
    sample_meta["extraction_wallet_set_path"] = str(wallet_set_path) if wallet_set_path else None
    manifest["supplemental_wallet_sample"] = sample_meta
    save_json(manifest_path, manifest)
    print(f"Tier-2 wallet pool: {len(pool)} wallets -> {wallet_set_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
