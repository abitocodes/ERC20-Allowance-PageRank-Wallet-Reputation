#!/usr/bin/env python3
"""Extract Aave V3 Pool lending logs (Borrow/Repay/LiquidationCall) from BigQuery."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from google.cloud import bigquery
from google.cloud.bigquery import ArrayQueryParameter, QueryJobConfig, ScalarQueryParameter

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402
    format_bytes,
    load_config,
    load_json,
    merge_extraction_wallets,
    read_sql,
    save_extraction_wallet_set,
    save_json,
)
from extract_reputation_data import OBSERVATION_MONTHS, dry_run_bytes, get_client, load_wallet_addresses, run_query  # noqa: E402


def query_params(config: dict, wallets: list[str], start_ts: str, end_ts: str) -> list:
    aave = config["aave_arbitrum"]
    topics = aave["event_topics"]
    pools = [p.lower() for p in aave["pool_addresses"]]
    return [
        ScalarQueryParameter("start_ts", "STRING", start_ts),
        ScalarQueryParameter("end_ts", "STRING", end_ts),
        ScalarQueryParameter("borrow_topic0", "STRING", topics["borrow"]),
        ScalarQueryParameter("repay_topic0", "STRING", topics["repay"]),
        ScalarQueryParameter("liquidation_topic0", "STRING", topics["liquidation_call"]),
        ArrayQueryParameter("pool_addresses", "STRING", pools),
        ArrayQueryParameter("wallet_addresses", "STRING", wallets),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wallets", type=Path, help="Parquet with wallet column")
    parser.add_argument(
        "--gmx-only",
        action="store_true",
        help="Extract for GMX-qualified wallets only (skip benchmark seed merge)",
    )
    parser.add_argument("--resume", action="store_true", help="Skip month files that already exist")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--extract", action="store_true")
    parser.add_argument("--yes", action="store_true")
    parser.add_argument(
        "--include-delegation",
        action="store_true",
        help="Record Credit Delegation (BorrowAllowanceDelegated) extract intent in manifest; BQ SQL deferred",
    )
    args = parser.parse_args()

    if not args.dry_run and not args.extract:
        parser.error("Specify --dry-run or --extract")

    config = load_config()
    gmx_wallets = load_wallet_addresses(config, args.wallets)
    wallets, wallet_meta = merge_extraction_wallets(
        gmx_wallets,
        config,
        include_benchmark=not args.gmx_only,
    )
    print(
        f"Wallet set: {len(wallets)} addresses "
        f"(GMX {wallet_meta['gmx_wallet_count']}, "
        f"supplemental {wallet_meta.get('supplemental_count', 0)})"
    )
    wallet_set_path = save_extraction_wallet_set(wallets, config)
    if wallet_set_path:
        print(f"Saved extraction wallet set -> {wallet_set_path}")

    logs_fqn = config["bigquery"]["logs_fqn"]
    sql = read_sql("aave_lending_logs.sql").replace("__LOGS_FQN__", logs_fqn)

    raw_dir = Path(config["paths"]["raw_lending_dir"])
    manifest_path = Path(config["paths"]["manifest"])
    budget_limit = config.get("budget", {}).get("max_bytes_per_query", 0)

    try:
        client = get_client(config)
    except Exception as exc:
        print(f"BigQuery client error: {exc}")
        return 1

    month_plans: list[dict] = []
    total_bytes = 0
    for label, start_ts, end_ts in OBSERVATION_MONTHS:
        params = query_params(config, wallets, start_ts, end_ts)
        bytes_aave = dry_run_bytes(client, sql, params)
        total_bytes += bytes_aave
        print(f"  {label}: aave {format_bytes(bytes_aave)}")
        if budget_limit and bytes_aave > budget_limit:
            print(f"ERROR: {label} exceeds per-query budget ({format_bytes(budget_limit)})")
            return 1
        month_plans.append(
            {
                "label": label,
                "start_ts": start_ts,
                "end_ts": end_ts,
                "bytes_aave": bytes_aave,
            }
        )

    print(f"Dry-run total ({len(month_plans)} months): {format_bytes(total_bytes)}")

    manifest = load_json(manifest_path)
    manifest["aave_extract"] = {
        "at": datetime.now(timezone.utc).isoformat(),
        "wallet_count": len(wallets),
        "wallet_meta": wallet_meta,
        "dry_run_bytes_total": total_bytes,
        "months": month_plans,
    }
    save_json(manifest_path, manifest)

    if args.include_delegation:
        delegation_topic = config.get("aave_arbitrum", {}).get("event_topics", {}).get(
            "borrow_allowance_delegated"
        )
        delegation_out = Path(config["paths"]["aave_delegation_events"])
        manifest["aave_delegation_extract"] = {
            "at": datetime.now(timezone.utc).isoformat(),
            "status": "deferred",
            "topic0": delegation_topic,
            "output_path": str(delegation_out),
            "note": (
                "BorrowAllowanceDelegated BQ SQL not run in this study; "
                "Delegation-PR scores degenerate until extract is implemented."
            ),
        }
        save_json(manifest_path, manifest)
        print(
            f"Credit Delegation: deferred (topic {delegation_topic}); "
            f"expected output {delegation_out}"
        )

    if args.dry_run:
        print("Dry-run complete.")
        return 0

    if not args.yes:
        resp = input(f"Extract ~{format_bytes(total_bytes)}? [y/N] ")
        if resp.strip().lower() != "y":
            print("Aborted.")
            return 0

    raw_dir.mkdir(parents=True, exist_ok=True)
    frames: list[pd.DataFrame] = []
    bytes_processed = 0

    for mo in month_plans:
        label = mo["label"]
        month_path = raw_dir / f"aave_events_{label}.parquet"
        params = query_params(config, wallets, mo["start_ts"], mo["end_ts"])
        print(f"Extracting {label}...")

        if args.resume and month_path.exists():
            print("  skip (exists)")
            df = pd.read_parquet(month_path)
        else:
            df = run_query(client, sql, params)
            df.to_parquet(month_path, index=False)
            print(f"  rows: {len(df)}")
        frames.append(df)
        bytes_processed += mo["bytes_aave"]

    df_all = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    combined_path = raw_dir / "aave_events_arbitrum.parquet"
    if not df_all.empty:
        df_all.to_parquet(combined_path, index=False)

    manifest["aave_extract"].update(
        {
            "extracted_at": datetime.now(timezone.utc).isoformat(),
            "rows": len(df_all),
            "bytes_processed": bytes_processed,
            "output_path": str(combined_path),
        }
    )
    save_json(manifest_path, manifest)
    print(f"Aave events: {len(df_all)} rows -> {combined_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
