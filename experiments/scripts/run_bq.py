#!/usr/bin/env python3
"""Run one SQL file on BigQuery with a dry run first and a running cost ledger.

Every job is dry-run, checked against the remaining budget of
config/contract_reputation.yaml, run, and written to data/bq_ledger.json with the
bytes it billed. A job whose estimate would push the ledger past the budget is
refused unless --force is given.

Usage:
    python scripts/run_bq.py sql/01_materialize_logs.sql --dest contract_rep.logs_obs \
        --param start_ts=2023-10-01T00:00:00Z --param end_ts=2026-07-01T00:00:00Z [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml
from google.cloud import bigquery

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "contract_reputation.yaml"
LEDGER = ROOT / "data" / "bq_ledger.json"
USD_PER_TIB = 6.25


def load_ledger() -> dict:
    if LEDGER.exists():
        return json.loads(LEDGER.read_text(encoding="utf-8"))
    return {"usd_per_tib": USD_PER_TIB, "jobs": []}


def spent_usd(ledger: dict) -> float:
    return sum(j.get("usd", 0.0) for j in ledger["jobs"])


def usd(nbytes: int) -> float:
    return nbytes / 2**40 * USD_PER_TIB


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("sql")
    ap.add_argument("--dest", help="dataset.table substituted for __DEST__")
    ap.add_argument("--param", action="append", default=[], help="name=value (string parameters)")
    ap.add_argument("--sub", action="append", default=[], help="KEY=VALUE text substituted for __KEY__")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--label", default="")
    args = ap.parse_args()

    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    project = cfg["bigquery"]["project_id"]
    budget = float(cfg["bigquery"]["budget_usd"])
    sql = Path(args.sql).read_text(encoding="utf-8")
    if args.dest:
        sql = sql.replace("__DEST__", f"{project}.{args.dest}")
    for sub in args.sub:
        key, value = sub.split("=", 1)
        sql = sql.replace(f"__{key}__", value)
    params = []
    for p in args.param:
        name, value = p.split("=", 1)
        params.append(bigquery.ScalarQueryParameter(name, "STRING", value))

    client = bigquery.Client(project=project)
    dry = client.query(sql, job_config=bigquery.QueryJobConfig(
        dry_run=True, use_query_cache=False, query_parameters=params))
    est = int(dry.total_bytes_processed or 0)
    ledger = load_ledger()
    spent = spent_usd(ledger)
    print(f"dry run: {est/1e9:,.1f} GB, about USD {usd(est):.2f}; ledger so far USD {spent:.2f} of {budget:.0f}")
    if args.dry_run:
        return 0
    if spent + usd(est) > budget and not args.force:
        print("refused: the estimate would exceed the budget (use --force after asking)")
        return 2

    job = client.query(sql, job_config=bigquery.QueryJobConfig(query_parameters=params))
    job.result()
    billed = int(job.total_bytes_billed or 0)
    entry = {
        "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "job_id": job.job_id,
        "sql": str(Path(args.sql).as_posix()),
        "dest": args.dest,
        "params": {p.name: p.value for p in params},
        "subs": args.sub,
        "label": args.label,
        "bytes_estimated": est,
        "bytes_billed": billed,
        "usd": round(usd(billed), 4),
    }
    ledger["jobs"].append(entry)
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    LEDGER.write_text(json.dumps(ledger, indent=2), encoding="utf-8")
    print(f"done: billed {billed/1e9:,.1f} GB, USD {entry['usd']:.2f}; ledger USD {spent_usd(ledger):.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
