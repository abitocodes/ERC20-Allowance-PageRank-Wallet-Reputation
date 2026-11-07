#!/usr/bin/env python3
"""Run one SQL file on BigQuery with a dry run first and a running cost ledger.

Every job is dry-run, checked against the remaining budget of the configuration of the
variant (config/contract_reputation.yaml with the overlay of CONTRACT_REP_VARIANT, see
scripts/common.py: USD 50, and USD 60 for the contract-graph variant), run, and written to
data/bq_ledger.json with the bytes it billed. A job whose estimate would push the ledger
past the budget is refused unless --force is given.

Usage:
    python scripts/run_bq.py sql/01_materialize_logs.sql --dest contract_rep.logs_obs \
        --param start_ts=2023-10-01T00:00:00Z --param end_ts=2026-07-01T00:00:00Z [--dry-run]

Options for reusing a file on other tables (the twelve-month variant of
docs/revision_one_year_window.md); without them nothing changes:
    --rename OLD=NEW      replace the table contract_rep.OLD by contract_rep.NEW after the
                          --sub substitutions (each rename must match at least once)
    --require-prefix P    refuse unless every table or view the file creates starts with P; then
                          also unless every table is named `project.dataset.table` (backquoted,
                          plain names) and no statement writes in another way than CREATE
    --allow-read NAME     a contract_rep table without prefix P that the file may read
    --allow-public FQN    a table or view outside the project dataset that the file may read,
                          named in full (project.dataset.table); every other one is refused
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

from google.cloud import bigquery

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import VARIANT, load_config  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data" / "bq_ledger.json"
USD_PER_TIB = 6.25


def settings(cfg: dict | None = None) -> tuple[str, str, float]:
    """Project, dataset and budget (USD) of the configuration of the variant (common.load_config)."""
    bq = (load_config() if cfg is None else cfg)["bigquery"]
    return bq["project_id"], bq["dataset"], float(bq["budget_usd"])


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


# Statements other than CREATE that write to or change a table, or run other code.
WRITES = ("INSERT", "UPDATE", "DELETE", "MERGE", "DROP", "TRUNCATE", "ALTER", "LOAD", "EXPORT", "CALL", "EXECUTE",
          "GRANT", "REVOKE", "UNDROP")
# String literals, backquoted names and comments, each matched where it starts.
_LEXEMES = re.compile(r"""'(?:[^'\\\n]|\\.)*'|"(?:[^"\\\n]|\\.)*"|`[^`]*`|--[^\n]*|#[^\n]*|/\*.*?\*/""", re.S)
_FULL_NAME = re.compile(r"`[A-Za-z0-9-]+\.\w+\.\w+`")


def name_problems(sql: str, project: str, dataset: str) -> list[str]:
    """Where a file names a table in another way than `project.dataset.table` (backquoted, with plain names) or
    creates something other than a table or view of the project dataset or a temporary table or function; the
    checks of check_tables() see only those full names. Comments and string literals are left out."""
    body = _LEXEMES.sub(lambda m: m.group(0) if m.group(0).startswith("`") else " ", sql)
    out = [m.group(0).strip() for m in re.finditer(r"(\.\s*)?(`[^`]*`)(\s*\.)?", body)
           if m.group(1) or m.group(3) or not _FULL_NAME.fullmatch(m.group(2))]  # wildcards, split quotes, ...
    allowed = (rf"CREATE\s+(?:OR\s+REPLACE\s+)?(?:(?:TABLE|VIEW)\s+`{re.escape(project)}\.{re.escape(dataset)}\.\w+`"
               r"|TEMP(?:ORARY)?\s+(?:TABLE|FUNCTION)\b)")
    for m in re.finditer(r"\bCREATE\b", body, flags=re.I):
        if not re.match(allowed, body[m.start():], flags=re.I):
            out.append(" ".join(body[m.start():m.start() + 60].split()))
    bare = re.sub(r"`[^`]*`", " __table__ ", body)
    bare = re.sub(r"(EXTRACT\s*\(\s*\w+(?:\s*\(\s*\w+\s*\))?\s+)FROM\b", r"\1OF", bare, flags=re.I)
    bare = re.sub(r"\bDISTINCT\s+FROM\b", "DISTINCT OF", bare, flags=re.I)
    for pattern in (rf"(?<![\w-]){re.escape(dataset)}(?![\w-])", rf"(?<![\w-]){re.escape(project)}(?![\w-])",
                    r"\b[A-Za-z]\w*(?:-\w+)+\s*\.\s*[A-Za-z_]\w*\s*\.\s*[A-Za-z_*][\w*$]*",  # an unquoted project path
                    r"\b(?:FROM|JOIN|TABLE|CLONE|COPY)\s+[A-Za-z_][\w-]*\s*\.\s*\S+",  # a dotted name read as a table
                    r"\bSET\s+@@\w+"):                                                 # such as a default dataset
        out += [" ".join(m.group(0).split()) for m in re.finditer(pattern, bare, flags=re.I)]
    return list(dict.fromkeys(out))


def check_tables(sql: str, project: str, dataset: str, prefix: str, allow_read: list[str],
                 allow_public: list[str] | tuple[str, ...] = ()) -> None:
    """Refuse a file that creates a table without the prefix or reads a table it may not.

    A table or view outside the project dataset may be read only if ``allow_public`` names it in
    full (project.dataset.table). Every table must be named so, in backquotes with plain names
    (name_problems), and no statement may write in another way than CREATE (WRITES)."""
    ds = rf"`{re.escape(project)}\.{re.escape(dataset)}\.(\w+)`"
    created = set(re.findall(rf"CREATE\s+(?:OR\s+REPLACE\s+)?(?:TABLE|VIEW)\s+{ds}", sql, flags=re.I))
    bad = sorted(t for t in created if not t.startswith(prefix))
    if bad:
        raise SystemExit(f"refused: the file creates tables without the prefix {prefix}: {bad}")
    if re.search(rf"\b({'|'.join(WRITES)})\b", re.sub(r"--[^\n]*", "", sql), flags=re.I):
        raise SystemExit("refused: the file writes to tables in another way than CREATE")
    names = name_problems(sql, project, dataset)
    if names:
        raise SystemExit("refused: the file names tables in another way than `project.dataset.table` with plain "
                         f"names, or creates something else: {names[:5]}")
    read = set(re.findall(ds, sql)) - created
    stray = sorted(t for t in read if not t.startswith(prefix) and t not in set(allow_read))
    if stray:
        raise SystemExit(f"refused: the file reads tables outside {prefix}* that are not allowed: {stray}")
    outside = {f"{p}.{t}" for p, t in re.findall(r"`([\w-]+\.[\w-]+)\.(\w+)`", sql) if p != f"{project}.{dataset}"}
    other = sorted(outside - set(allow_public))
    if other:
        raise SystemExit(f"refused: the file reads tables of other datasets that are not allowed: {other}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("sql")
    ap.add_argument("--dest", help="dataset.table substituted for __DEST__")
    ap.add_argument("--param", action="append", default=[], help="name=value (string parameters)")
    ap.add_argument("--sub", action="append", default=[], help="KEY=VALUE text substituted for __KEY__")
    ap.add_argument("--rename", action="append", default=[], help="OLD=NEW table renamed after --sub")
    ap.add_argument("--require-prefix", default="", help="every created table must start with this")
    ap.add_argument("--allow-read", action="append", default=[], help="table outside the prefix that may be read")
    ap.add_argument("--allow-public", action="append", default=[],
                    help="project.dataset.table outside the project dataset that may be read")
    ap.add_argument("--expect-bytes", type=int, default=0, help="realistic bytes for the budget checks")
    ap.add_argument("--max-dry-bytes", type=int, default=0, help="refuse if the dry run counts more bytes")
    ap.add_argument("--campaign", default="", help="label prefix of the jobs of one campaign")
    ap.add_argument("--campaign-cap", type=float, default=0.0, help="USD cap of the campaign")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--label", default="")
    args = ap.parse_args()

    project, dataset, budget = settings()
    sql = Path(args.sql).read_text(encoding="utf-8")
    if args.dest:
        sql = sql.replace("__DEST__", f"{project}.{args.dest}")
    for sub in args.sub:
        key, value = sub.split("=", 1)
        sql = sql.replace(f"__{key}__", value)
    sql = apply_renames(sql, args.rename, project, dataset)
    if args.require_prefix:
        check_tables(sql, project, dataset, args.require_prefix, args.allow_read, args.allow_public)
    elif args.allow_public:
        raise SystemExit("--allow-public needs --require-prefix")
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
        "variant": VARIANT,
        "budget_usd": budget,
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
