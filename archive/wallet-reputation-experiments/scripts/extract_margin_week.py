#!/usr/bin/env python3
"""Extract GMX PositionDecrease logs from BigQuery for the observation window.

Uses ``period`` in margin_config.yaml (default: 2025-12-01 through 2026-05-31).
Queries run in monthly batches to stay under the per-query byte budget.
Run ``--dry-run`` before ``--extract``; bytes are recorded in extraction_manifest.json.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from google.cloud import bigquery
from google.cloud.bigquery import QueryJobConfig, ScalarQueryParameter

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402
    format_bytes,
    load_config,
    load_json,
    read_sql,
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


def get_client(config: dict) -> bigquery.Client:
    project = config.get("bigquery", {}).get("project_id")
    return bigquery.Client(project=project)


def query_params(config: dict, start_ts: str, end_ts: str) -> list:
    gmx = config["gmx_arbitrum"]
    ev = config["events"]
    return [
        ScalarQueryParameter("start_ts", "STRING", start_ts),
        ScalarQueryParameter("end_ts", "STRING", end_ts),
        ScalarQueryParameter("event_emitter", "STRING", gmx["event_emitter"]),
        ScalarQueryParameter("event_log1_topic0", "STRING", ev["event_log1_topic0"]),
        ScalarQueryParameter(
            "position_decrease_hash", "STRING", ev["position_decrease_hash"]
        ),
    ]


def dry_run_bytes(client: bigquery.Client, sql: str, params: list) -> int:
    job_config = QueryJobConfig(dry_run=True, use_query_cache=False, query_parameters=params)
    job = client.query(sql, job_config=job_config)
    return int(job.total_bytes_processed or 0)


def run_query(client: bigquery.Client, sql: str, params: list) -> pd.DataFrame:
    job_config = QueryJobConfig(use_query_cache=False, query_parameters=params)
    job = client.query(sql, job_config=job_config)
    return job.to_dataframe()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Dry-run only")
    parser.add_argument("--extract", action="store_true", help="Run extraction")
    parser.add_argument("--yes", action="store_true", help="Skip confirmation")
    parser.add_argument(
        "--month",
        action="append",
        metavar="LABEL",
        help="Extract only these month labels (e.g. 2026-05); may be repeated",
    )
    parser.add_argument(
        "--merge-only",
        action="store_true",
        help="Merge existing monthly parquets into combined output (no BigQuery)",
    )
    args = parser.parse_args()

    if not args.dry_run and not args.extract and not args.merge_only:
        parser.error("Specify --dry-run or --extract (or --merge-only)")

    config = load_config()
    sql = read_sql("gmx_event_logs.sql").replace(
        "__LOGS_FQN__", config["bigquery"]["logs_fqn"]
    )
    out_path = Path(config["paths"]["raw_logs"])
    raw_month_dir = Path(config["paths"].get("raw_gmx_dir") or out_path.parent / "gmx")
    manifest_path = Path(config["paths"]["manifest"])
    budget_limit = config.get("budget", {}).get("max_bytes_per_query", 0)

    try:
        client = get_client(config)
    except Exception as exc:
        print(f"BigQuery client error: {exc}")
        print("Use: python scripts/generate_synthetic_rankings.py for offline mode.")
        return 1

    month_plans: list[dict] = []
    total_bytes = 0
    selected = set(args.month) if args.month else None
    for label, start_ts, end_ts in OBSERVATION_MONTHS:
        if selected and label not in selected:
            continue
        params = query_params(config, start_ts, end_ts)
        bytes_est = dry_run_bytes(client, sql, params)
        total_bytes += bytes_est
        print(f"  {label}: {format_bytes(bytes_est)}")
        if budget_limit and bytes_est > budget_limit and not args.extract:
            print(
                f"ERROR: {label} exceeds per-query budget ({format_bytes(budget_limit)})"
            )
            return 1
        month_plans.append(
            {
                "label": label,
                "start_ts": start_ts,
                "end_ts": end_ts,
                "dry_run_bytes": bytes_est,
            }
        )

    if not month_plans and not args.merge_only:
        parser.error("No months matched --month filter")

    if month_plans:
        print(f"Dry-run total ({len(month_plans)} months): {format_bytes(total_bytes)}")

    manifest = load_json(manifest_path)
    manifest.update(
        {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "synthetic": False,
            "period": config["period"],
            "protocol": config["protocol"],
            "gmx_extract": {
                "at": datetime.now(timezone.utc).isoformat(),
                "dry_run_bytes_total": total_bytes,
                "months": month_plans,
            },
        }
    )
    save_json(manifest_path, manifest)

    if args.dry_run and not args.merge_only:
        print("Dry-run complete.")
        return 0

    if args.merge_only:
        month_plans = []

    if not args.merge_only:
        if not args.yes:
            resp = input(f"Extract ~{format_bytes(total_bytes)}? [y/N] ")
            if resp.strip().lower() != "y":
                print("Aborted.")
                return 0

        raw_month_dir.mkdir(parents=True, exist_ok=True)
        bytes_processed = 0

        for mo in month_plans:
            label = mo["label"]
            month_path = raw_month_dir / f"gmx_event_logs_{label}.parquet"
            params = query_params(config, mo["start_ts"], mo["end_ts"])
            print(f"Extracting {label}...")
            df = run_query(client, sql, params)
            df.to_parquet(month_path, index=False)
            bytes_processed += mo["dry_run_bytes"]
            print(f"  {label}: {len(df)} rows -> {month_path}")

    raw_month_dir.mkdir(parents=True, exist_ok=True)
    on_disk = sorted(raw_month_dir.glob("gmx_event_logs_*.parquet"))
    if not on_disk:
        print("ERROR: no monthly parquet files to merge")
        return 1
    frames = [pd.read_parquet(p) for p in on_disk]
    df_all = pd.concat(frames, ignore_index=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df_all.to_parquet(out_path, index=False)

    manifest["gmx_extract"].update(
        {
            "extracted_at": datetime.now(timezone.utc).isoformat(),
            "rows": len(df_all),
            "bytes_processed": total_bytes if not args.merge_only else manifest.get(
                "gmx_extract", {}
            ).get("bytes_processed", 0),
            "output": str(out_path),
            "monthly_dir": str(raw_month_dir),
            "merged_months": [p.name for p in on_disk],
        }
    )
    save_json(manifest_path, manifest)
    print(f"Merged {len(on_disk)} months, {len(df_all)} rows -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
