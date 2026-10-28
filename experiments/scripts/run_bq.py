#!/usr/bin/env python3
"""Run one SQL file on BigQuery with a dry run first and a running cost ledger.

Every job is dry-run, checked against the remaining budget of
config/contract_reputation.yaml, run, and written to data/bq_ledger.json with the
bytes it billed. A job whose estimate would push the ledger past the budget is
refused unless --force is given.

Usage:
    python scripts/run_bq.py sql/01_materialize_logs.sql --dest contract_rep.logs_obs \
        --param start_ts=2023-10-01T00:00:00Z --param end_ts=2026-07-01T00:00:00Z [--dry-run]

Options for reusing a file on other tables (the twelve-month variant of
docs/revision_one_year_window.md); without them nothing changes:
    --rename OLD=NEW      replace the table contract_rep.OLD by contract_rep.NEW after the
                          --sub substitutions (each rename must match at least once)
    --require-prefix P    refuse unless every table or view the file creates starts with P
    --allow-read NAME     a contract_rep table without prefix P that the file may read
    --expect-bytes N      a realistic estimate; the budget checks use the larger of it and the
                          dry run, which counts only the first statement of a script
    --max-dry-bytes N     refuse (also with --dry-run) if the dry run counts more than N bytes,
                          as when a partition filter does not prune
    --campaign L --campaign-cap USD
                          refuse if the ledger jobs whose label starts with L, plus this job,
                          would pass USD
"""

from __future__ import annotations

import argparse
import json
import re
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


def apply_renames(sql: str, renames: list[str], project: str, dataset: str) -> str:
    """Replace whole table names; a rename that matches nothing is an error."""
    for r in renames:
        old, new = r.split("=", 1)
        pat = re.compile(rf"`{re.escape(project)}\.{re.escape(dataset)}\.{re.escape(old)}`")
        sql, n = pat.subn(f"`{project}.{dataset}.{new}`", sql)
        if n == 0:
            raise SystemExit(f"--rename {r}: table {old} does not occur in the file")
    return sql


def check_tables(sql: str, project: str, dataset: str, prefix: str, allow_read: list[str]) -> None:
    """Refuse a file that creates a table without the prefix or reads a table it may not."""
    ds = rf"`{re.escape(project)}\.{re.escape(dataset)}\.(\w+)`"
    created = set(re.findall(rf"CREATE\s+(?:OR\s+REPLACE\s+)?(?:TABLE|VIEW)\s+{ds}", sql, flags=re.I))
    bad = sorted(t for t in created if not t.startswith(prefix))
    if bad:
        raise SystemExit(f"refused: the file creates tables without the prefix {prefix}: {bad}")
    if re.search(r"\b(INSERT|UPDATE|DELETE|MERGE|DROP|TRUNCATE)\b", re.sub(r"--[^\n]*", "", sql), flags=re.I):
        raise SystemExit("refused: the file writes to tables in another way than CREATE")
    read = set(re.findall(ds, sql)) - created
    stray = sorted(t for t in read if not t.startswith(prefix) and t not in set(allow_read))
    if stray:
        raise SystemExit(f"refused: the file reads tables outside {prefix}* that are not allowed: {stray}")
    other = sorted(set(re.findall(r"`([\w-]+\.[\w-]+)\.\w+`", sql)) - {f"{project}.{dataset}"})
    if other:
        raise SystemExit(f"refused: the file reads other datasets: {other}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("sql")
    ap.add_argument("--dest", help="dataset.table substituted for __DEST__")
    ap.add_argument("--param", action="append", default=[], help="name=value (string parameters)")
    ap.add_argument("--sub", action="append", default=[], help="KEY=VALUE text substituted for __KEY__")
    ap.add_argument("--rename", action="append", default=[], help="OLD=NEW table renamed after --sub")
    ap.add_argument("--require-prefix", default="", help="every created table must start with this")
    ap.add_argument("--allow-read", action="append", default=[], help="table outside the prefix that may be read")
    ap.add_argument("--expect-bytes", type=int, default=0, help="realistic bytes for the budget checks")
    ap.add_argument("--max-dry-bytes", type=int, default=0, help="refuse if the dry run counts more bytes")
    ap.add_argument("--campaign", default="", help="label prefix of the jobs of one campaign")
    ap.add_argument("--campaign-cap", type=float, default=0.0, help="USD cap of the campaign")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--label", default="")
    args = ap.parse_args()

    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    project = cfg["bigquery"]["project_id"]
    dataset = cfg["bigquery"]["dataset"]
    budget = float(cfg["bigquery"]["budget_usd"])
    sql = Path(args.sql).read_text(encoding="utf-8")
    if args.dest:
        sql = sql.replace("__DEST__", f"{project}.{args.dest}")
    for sub in args.sub:
        key, value = sub.split("=", 1)
        sql = sql.replace(f"__{key}__", value)
    sql = apply_renames(sql, args.rename, project, dataset)
    if args.require_prefix:
        check_tables(sql, project, dataset, args.require_prefix, args.allow_read)
    if args.campaign and not args.label.startswith(args.campaign):
        raise SystemExit(f"--label must start with the campaign {args.campaign!r}")
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
    check = max(est, args.expect_bytes)
    if args.expect_bytes:
        print(f"expected: {args.expect_bytes/1e9:,.1f} GB, about USD {usd(args.expect_bytes):.2f}")
    if args.campaign:
        camp = sum(j.get("usd", 0.0) for j in ledger["jobs"] if j.get("label", "").startswith(args.campaign))
        print(f"campaign {args.campaign!r}: USD {camp:.2f} of {args.campaign_cap:.2f}")
    if args.max_dry_bytes and est > args.max_dry_bytes:
        print(f"refused: the dry run counts more than {args.max_dry_bytes/1e9:,.1f} GB")
        return 2
    if args.dry_run:
        return 0
    if spent + usd(check) > budget and not args.force:
        print("refused: the estimate would exceed the budget (use --force after asking)")
        return 2
    if args.campaign and camp + usd(check) > args.campaign_cap:
        print("refused: the estimate would exceed the campaign cap")
        return 2

    job = client.query(sql, job_config=bigquery.QueryJobConfig(query_parameters=params))
    error = None
    try:
        job.result()
    except Exception as exc:  # the bytes a failed job billed are recorded as well
        error = str(exc)[:500]
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
    if args.rename:
        entry["renames"] = args.rename
    if args.expect_bytes:
        entry["bytes_expected"] = args.expect_bytes
    if error:
        entry["error"] = error
    ledger["jobs"].append(entry)
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    LEDGER.write_text(json.dumps(ledger, indent=2), encoding="utf-8")
    if error:
        print(f"failed: {error}\nbilled {billed/1e9:,.1f} GB, USD {entry['usd']:.2f}; ledger USD {spent_usd(ledger):.2f}")
        return 1
    print(f"done: billed {billed/1e9:,.1f} GB, USD {entry['usd']:.2f}; ledger USD {spent_usd(ledger):.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
