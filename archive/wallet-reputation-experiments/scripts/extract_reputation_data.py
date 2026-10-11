#!/usr/bin/env python3
"""Extract Arbitrum ERC-20 Approval and Transfer logs for reputation scoring."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Callable

import pandas as pd
import pyarrow.parquet as pq
from google.cloud import bigquery
from google.cloud.bigquery import ArrayQueryParameter, QueryJobConfig, ScalarQueryParameter

sys.path.insert(0, str(Path(__file__).resolve().parent))

from bq_progress import (  # noqa: E402
    ExtractionStep,
    StepProgressBar,
    count_completed_steps,
    download_query_to_parquet,
    get_checkpoint_block,
    save_checkpoint,
    should_skip_dry_run,
    step_is_completed,
    upsert_step_record,
    utc_now_iso,
)
from common import (  # noqa: E402
    format_bytes,
    load_config,
    load_json,
    merge_extraction_wallets,
    read_sql,
    save_extraction_wallet_set,
    save_json,
)

OBSERVATION_MONTHS = [
    ("2025-12", "2025-12-01 00:00:00 UTC", "2026-01-01 00:00:00 UTC"),
    ("2026-01", "2026-01-01 00:00:00 UTC", "2026-02-01 00:00:00 UTC"),
    ("2026-02", "2026-02-01 00:00:00 UTC", "2026-03-01 00:00:00 UTC"),
    ("2026-03", "2026-03-01 00:00:00 UTC", "2026-04-01 00:00:00 UTC"),
    ("2026-04", "2026-04-01 00:00:00 UTC", "2026-05-01 00:00:00 UTC"),
    ("2026-05", "2026-05-01 00:00:00 UTC", "2026-06-01 00:00:00 UTC"),
]


def build_extraction_steps() -> list[ExtractionStep]:
    steps: list[ExtractionStep] = []
    for label, _, _ in OBSERVATION_MONTHS:
        steps.append(ExtractionStep(label, "approvals"))
        steps.append(ExtractionStep(label, "transfers"))
    return steps


def get_client(config: dict) -> bigquery.Client:
    project = config.get("bigquery", {}).get("project_id")
    return bigquery.Client(project=project)


def load_wallet_addresses(config: dict, wallets_path: Path | None) -> list[str]:
    path = wallets_path or Path(config["paths"]["wallet_rankings"])
    if not path.exists():
        raise FileNotFoundError(
            f"Wallet rankings not found: {path}\n"
            "Run compute_rankings.py or generate_synthetic_rankings.py first."
        )
    df = pd.read_parquet(path)
    if "wallet" not in df.columns:
        raise ValueError(f"Missing wallet column in {path}")
    wallets = df["wallet"].astype(str).str.lower().unique().tolist()
    return sorted(wallets)


def _topic_to_address(topic: str | None) -> str | None:
    if topic is None or (isinstance(topic, float) and pd.isna(topic)):
        return None
    s = str(topic).lower().strip()
    if len(s) >= 42:
        return "0x" + s[-40:]
    return None


def _parse_uint256_data(data: str | None) -> str:
    if data is None or (isinstance(data, float) and pd.isna(data)):
        return "0"
    s = str(data).strip()
    if not s or s in ("0x", "0X"):
        return "0"
    try:
        return str(int(s, 16))
    except ValueError:
        return "0"


def normalize_approvals(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["owner"] = out["owner_topic"].map(_topic_to_address)
    out["spender"] = out["spender_topic"].map(_topic_to_address)
    out["token_address"] = out["token_address"].astype(str).str.lower()
    out["value"] = out["value_data"].map(_parse_uint256_data)
    return out.dropna(subset=["owner", "spender"])


def normalize_transfers(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["from_address"] = out["from_topic"].map(_topic_to_address)
    out["to_address"] = out["to_topic"].map(_topic_to_address)
    out["token_address"] = out["token_address"].astype(str).str.lower()
    out["value"] = out["value_data"].map(_parse_uint256_data)
    return out.dropna(subset=["from_address", "to_address"])


def query_params(
    config: dict,
    wallets: list[str],
    start_ts: str,
    end_ts: str,
) -> list:
    rep = config["reputation"]
    return [
        ScalarQueryParameter("start_ts", "STRING", start_ts),
        ScalarQueryParameter("end_ts", "STRING", end_ts),
        ScalarQueryParameter("approval_topic0", "STRING", rep["approval_topic0"]),
        ScalarQueryParameter("transfer_topic0", "STRING", rep["transfer_topic0"]),
        ArrayQueryParameter("wallet_addresses", "STRING", wallets),
    ]


def dry_run_bytes(client: bigquery.Client, sql: str, params: list) -> int:
    job_config = QueryJobConfig(dry_run=True, use_query_cache=False, query_parameters=params)
    job = client.query(sql, job_config=job_config)
    return int(job.total_bytes_processed or 0)


def merge_parquet_paths(paths: list[Path], out_path: Path) -> int:
    """Merge monthly parquet files without loading entire dataset into RAM."""
    writer: pq.ParquetWriter | None = None
    total = 0
    for path in paths:
        if not path.exists():
            continue
        pf = pq.ParquetFile(path)
        for rg in range(pf.num_row_groups):
            table = pf.read_row_group(rg)
            if writer is None:
                out_path.parent.mkdir(parents=True, exist_ok=True)
                writer = pq.ParquetWriter(out_path, table.schema)
            writer.write_table(table)
            total += table.num_rows
    if writer is not None:
        writer.close()
    return total


def month_path(
    step: ExtractionStep,
    approvals_dir: Path,
    transfers_dir: Path,
) -> Path:
    if step.kind == "approvals":
        return approvals_dir / f"approvals_{step.month}.parquet"
    return transfers_dir / f"transfers_{step.month}.parquet"


def month_plan_for(label: str, month_plans: list[dict]) -> dict:
    for mo in month_plans:
        if mo["label"] == label:
            return mo
    raise KeyError(label)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(line_buffering=True)

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wallets", type=Path, help="Parquet with wallet column")
    parser.add_argument(
        "--gmx-only",
        action="store_true",
        help="Extract reputation for GMX-qualified wallets only (skip benchmark seed merge)",
    )
    parser.add_argument(
        "--tier2",
        action="store_true",
        help="Write raw outputs to benchmark.tier2_paths (preserves Tier-1 raw); uses extraction_wallet_set if present",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Skip completed steps; reuse in-progress BQ job_id when possible",
    )
    parser.add_argument(
        "--skip-dry-run",
        action="store_true",
        help="Skip byte-estimate dry-run (use manifest or proceed without estimate)",
    )
    parser.add_argument(
        "--dry-run-first",
        action="store_true",
        help="With --extract, always run dry-run before extraction",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--extract", action="store_true")
    parser.add_argument("--yes", action="store_true")
    args = parser.parse_args()

    if not args.dry_run and not args.extract:
        parser.error("Specify --dry-run or --extract")

    config = load_config()
    gmx_wallets = load_wallet_addresses(config, args.wallets)

    if args.tier2:
        wallet_set_path = Path(config.get("benchmark", {}).get("wallet_set_path", ""))
        if wallet_set_path.exists():
            df_ws = pd.read_parquet(wallet_set_path)
            wallets = sorted(df_ws["wallet"].astype(str).str.lower().unique().tolist())
            wallet_meta = {
                "gmx_wallet_count": len(gmx_wallets),
                "target_wallets": len(wallets),
                "extraction_wallet_count": len(wallets),
                "supplemental_source": str(wallet_set_path),
                "supplemental_count": max(0, len(wallets) - len(gmx_wallets)),
                "tier2": True,
            }
        else:
            wallets, wallet_meta = merge_extraction_wallets(
                gmx_wallets, config, include_benchmark=True
            )
            wallet_meta["tier2"] = True
    else:
        wallets, wallet_meta = merge_extraction_wallets(
            gmx_wallets,
            config,
            include_benchmark=not args.gmx_only,
        )
    print(
        f"Wallet set: {len(wallets)} addresses "
        f"(GMX {wallet_meta['gmx_wallet_count']}, "
        f"supplemental {wallet_meta.get('supplemental_count', 0)}, "
        f"source={wallet_meta.get('supplemental_source', 'none')})"
    )
    if not args.dry_run:
        wallet_set_path = save_extraction_wallet_set(wallets, config)
        if wallet_set_path:
            print(f"Saved extraction wallet set -> {wallet_set_path}")
    else:
        wallet_set_path = None

    logs_fqn = config["bigquery"]["logs_fqn"]
    sql_approvals = read_sql("arbitrum_approvals.sql").replace("__LOGS_FQN__", logs_fqn)
    sql_transfers = read_sql("arbitrum_transfers.sql").replace("__LOGS_FQN__", logs_fqn)

    rep_paths = config["reputation"]["paths"]
    if args.tier2:
        tier2_paths = config.get("benchmark", {}).get("tier2_paths") or {}
        if tier2_paths.get("raw_approvals_dir"):
            rep_paths = {**rep_paths, "raw_approvals_dir": tier2_paths["raw_approvals_dir"]}
        if tier2_paths.get("raw_transfers_dir"):
            rep_paths = {**rep_paths, "raw_transfers_dir": tier2_paths["raw_transfers_dir"]}
    approvals_dir = Path(rep_paths["raw_approvals_dir"])
    transfers_dir = Path(rep_paths["raw_transfers_dir"])
    manifest_path = Path(config["paths"]["manifest"])
    budget_limit = config.get("budget", {}).get("max_bytes_per_query", 0)
    manifest_key = "tier2_reputation_extract" if args.tier2 else "reputation_extract"

    try:
        client = get_client(config)
    except Exception as exc:
        print(f"BigQuery client error: {exc}")
        print("Use: python scripts/generate_synthetic_reputation.py for offline mode.")
        return 1

    manifest = load_json(manifest_path)
    block = get_checkpoint_block(manifest, manifest_key)
    checkpoint = block["checkpoint"]

    skip_dry = should_skip_dry_run(
        manifest,
        len(wallets),
        force_dry_run=args.dry_run_first,
        skip_dry_run_flag=args.skip_dry_run,
        resume=args.resume,
        extract=args.extract,
    )

    month_plans: list[dict] = []
    total_bytes = 0

    if skip_dry and manifest.get("reputation_extract", {}).get("months"):
        month_plans = manifest["reputation_extract"]["months"]
        total_bytes = int(manifest["reputation_extract"].get("dry_run_bytes_total") or 0)
        print(
            f"Skipping dry-run (manifest wallet_count={manifest['reputation_extract'].get('wallet_count')}, "
            f"total {format_bytes(total_bytes)})"
        )
    else:
        for label, start_ts, end_ts in OBSERVATION_MONTHS:
            params = query_params(config, wallets, start_ts, end_ts)
            bytes_app = dry_run_bytes(client, sql_approvals, params)
            bytes_tx = dry_run_bytes(client, sql_transfers, params)
            month_total = bytes_app + bytes_tx
            total_bytes += month_total
            print(
                f"  {label}: approvals {format_bytes(bytes_app)}, "
                f"transfers {format_bytes(bytes_tx)}"
            )
            if budget_limit and max(bytes_app, bytes_tx) > budget_limit:
                print(
                    f"ERROR: {label} exceeds per-query budget "
                    f"({format_bytes(budget_limit)})"
                )
                return 1
            month_plans.append(
                {
                    "label": label,
                    "start_ts": start_ts,
                    "end_ts": end_ts,
                    "bytes_approvals": bytes_app,
                    "bytes_transfers": bytes_tx,
                }
            )
        print(f"Dry-run total ({len(month_plans)} months): {format_bytes(total_bytes)}")

    manifest["reputation_extract"] = {
        "at": utc_now_iso(),
        "wallet_count": len(wallets),
        "wallet_meta": wallet_meta,
        "extraction_wallet_set_path": str(wallet_set_path) if wallet_set_path else None,
        "dry_run_bytes_total": total_bytes,
        "months": month_plans,
        "observation": {
            "start": config["reputation"]["observation_start_ts"],
            "end": config["reputation"]["observation_end_ts"],
        },
    }
    save_json(manifest_path, manifest)

    if args.dry_run:
        print("Dry-run complete.")
        return 0

    if not args.yes:
        resp = input(f"Extract ~{format_bytes(total_bytes)}? [y/N] ")
        if resp.strip().lower() != "y":
            print("Aborted.")
            return 0

    steps = build_extraction_steps()

    def path_for_step(step: ExtractionStep) -> Path:
        return month_path(step, approvals_dir, transfers_dir)

    progress = StepProgressBar(steps, initial=0)

    approvals_dir.mkdir(parents=True, exist_ok=True)
    transfers_dir.mkdir(parents=True, exist_ok=True)

    block["status"] = "in_progress"
    block["wallet_pool_size"] = len(wallets)
    block["started_at"] = block.get("started_at") or utc_now_iso()
    save_checkpoint(manifest_path, manifest_key, manifest, block)

    sql_for_kind: dict[str, tuple[str, Callable[[pd.DataFrame], pd.DataFrame], str]] = {
        "approvals": (sql_approvals, normalize_approvals, "bytes_approvals"),
        "transfers": (sql_transfers, normalize_transfers, "bytes_transfers"),
    }

    try:
        for step in steps:
            out_path = path_for_step(step)
            progress.set_step(step)
            mo = month_plan_for(step.month, month_plans)
            params = query_params(config, wallets, mo["start_ts"], mo["end_ts"])
            sql, normalize_fn, bytes_key = sql_for_kind[step.kind]
            step_bytes = int(mo.get(bytes_key) or 0)

            if args.resume and step_is_completed(step, out_path, checkpoint):
                print(f"  {step.step_id}: skip (exists)", flush=True)
                upsert_step_record(
                    checkpoint,
                    step.step_id,
                    status="completed",
                    finished_at=utc_now_iso(),
                )
                progress.advance(step)
                save_checkpoint(manifest_path, manifest_key, manifest, block)
                continue

            download_query_to_parquet(
                client,
                sql,
                params,
                out_path,
                normalize_fn,
                checkpoint,
                step.step_id,
                bytes_scanned=step_bytes,
                reporter=progress,
                manifest_path=manifest_path,
                manifest_key=manifest_key,
                manifest=manifest,
                block=block,
            )
            progress.advance(step)
            save_checkpoint(manifest_path, manifest_key, manifest, block)
    except KeyboardInterrupt:
        done = count_completed_steps(steps, path_for_step, checkpoint)
        block["status"] = "in_progress"
        save_checkpoint(manifest_path, manifest_key, manifest, block)
        print("\nInterrupted.", flush=True)
        print(f"  Progress: {done}/{len(steps)} steps completed.", flush=True)
        print("  Chunks and job_id saved. Re-run:", flush=True)
        print(
            "  python -u scripts/extract_reputation_data.py --tier2 --extract --yes --resume",
            flush=True,
        )
        return 130
    finally:
        progress.close()

    all_done = count_completed_steps(steps, path_for_step, checkpoint) == len(steps)
    if not all_done:
        block["status"] = "in_progress"
        save_checkpoint(manifest_path, manifest_key, manifest, block)
        done = count_completed_steps(steps, path_for_step, checkpoint)
        print(
            f"Incomplete: {done}/{len(steps)} steps. "
            "Re-run with --extract --yes --resume to continue."
        )
        return 0

    approval_paths = [
        approvals_dir / f"approvals_{mo['label']}.parquet" for mo in month_plans
    ]
    transfer_paths = [
        transfers_dir / f"transfers_{mo['label']}.parquet" for mo in month_plans
    ]
    bytes_processed = sum(
        mo["bytes_approvals"] + mo["bytes_transfers"] for mo in month_plans
    )

    app_path = approvals_dir / "approvals_arbitrum.parquet"
    tx_path = transfers_dir / "transfers_arbitrum.parquet"
    approval_rows = merge_parquet_paths(approval_paths, app_path)
    transfer_rows = merge_parquet_paths(transfer_paths, tx_path)

    manifest["reputation_extract"].update(
        {
            "extracted_at": utc_now_iso(),
            "approval_rows": approval_rows,
            "transfer_rows": transfer_rows,
            "bytes_processed": bytes_processed,
            "approvals_path": str(app_path),
            "transfers_path": str(tx_path),
        }
    )
    block.update(
        {
            "status": "completed",
            "at": utc_now_iso(),
            "wallet_pool_size": len(wallets),
            "approval_rows": approval_rows,
            "transfer_rows": transfer_rows,
            "bytes_processed": bytes_processed,
            "approvals_path": str(app_path),
            "transfers_path": str(tx_path),
            "monthly_approvals_dir": str(approvals_dir),
            "monthly_transfers_dir": str(transfers_dir),
        }
    )
    save_checkpoint(manifest_path, manifest_key, manifest, block)
    print(f"Approvals: {approval_rows} rows -> {app_path}")
    print(f"Transfers: {transfer_rows} rows -> {tx_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nInterrupted.", flush=True)
        raise SystemExit(130) from None
