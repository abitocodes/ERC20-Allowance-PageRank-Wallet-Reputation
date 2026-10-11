#!/usr/bin/env python3
"""Extract the June-August 2026 logs for the registered fresh holdout.

Each month of each kind goes to its own parquet file in the folders named in
config/fresh_holdout_2026q3.yaml, with a separate manifest. The registration
names the folders as they were before 1 October 2026; project_paths.current_path
gives their present names. The spring raw files, the combined parquet files and
data/2-processed-tables-and-evaluations/extraction_manifest.json are not touched.

Kinds (same SQL and parameters as the spring extraction):
  approvals  ERC-20 Approval logs with an owner or spender in the matched cohort
  transfers  ERC-20 Transfer logs with a sender or receiver in the matched cohort
  gmx        GMX V2 PositionDecrease logs from the EventEmitter (all accounts)

Usage (from 1-Dissertation-Works/ERC20-Allowance-PageRank-Wallet-Reputation/dissertation/wallet-reputation-experiments, with the project venv):
  python scripts/extract_fresh_window.py --dry-run
  python scripts/extract_fresh_window.py --extract --yes
  python scripts/extract_fresh_window.py --decode-only

--extract refuses to run until the registration file and the plan are committed
with status 'registered'. A finished month is skipped on a re-run, so the same
command resumes after an interruption. If a month is above the per-query byte
budget, --split 2 queries each month in two halves.
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import format_bytes, load_config, load_json, read_sql, save_json  # noqa: E402
from fresh_holdout import (  # noqa: E402
    REGISTRATION_PATH,
    load_registration,
    registration_check,
)

KINDS = ("approvals", "transfers", "gmx")
SQL_FILES = {
    "approvals": "arbitrum_approvals.sql",
    "transfers": "arbitrum_transfers.sql",
    "gmx": "gmx_event_logs.sql",
}
PREFIX = {"approvals": "approvals_", "transfers": "transfers_", "gmx": "gmx_event_logs_"}
DIR_KEY = {"approvals": "raw_approvals_dir", "transfers": "raw_transfers_dir", "gmx": "raw_gmx_dir"}


def split_month(label: str, start_ts: str, end_ts: str, parts: int) -> list[tuple[str, str, str]]:
    """Split [start, end) into equal parts; labels get a, b, c ... suffixes."""
    if parts <= 1:
        return [(label, start_ts, end_ts)]
    start = pd.Timestamp(start_ts.replace(" UTC", ""), tz="UTC")
    end = pd.Timestamp(end_ts.replace(" UTC", ""), tz="UTC")
    edges = [start + (end - start) * i / parts for i in range(parts + 1)]
    edges = [e.floor("s") for e in edges]
    edges[-1] = end
    out = []
    for i in range(parts):
        suffix = chr(ord("a") + i)
        out.append(
            (
                f"{label}{suffix}",
                edges[i].strftime("%Y-%m-%d %H:%M:%S UTC"),
                edges[i + 1].strftime("%Y-%m-%d %H:%M:%S UTC"),
            )
        )
    return out


def plan_steps(reg: dict[str, Any], kinds: tuple[str, ...] = KINDS, split: int = 1) -> list[dict[str, Any]]:
    ex = reg["extraction"]
    steps: list[dict[str, Any]] = []
    for label, start_ts, end_ts in reg["window"]["months"]:
        for part_label, s, e in split_month(label, start_ts, end_ts, split):
            for kind in kinds:
                out = Path(ex[DIR_KEY[kind]]) / f"{PREFIX[kind]}{part_label}.parquet"
                steps.append(
                    {
                        "id": f"{kind}:{part_label}",
                        "kind": kind,
                        "label": part_label,
                        "month": label,
                        "start_ts": s,
                        "end_ts": e,
                        "out_path": str(out),
                    }
                )
    return steps


def whole_month_path(step: dict[str, Any]) -> Path:
    return Path(step["out_path"]).parent / f"{PREFIX[step['kind']]}{step['month']}.parquet"


def month_done(step: dict[str, Any]) -> bool:
    """A step is done when its file exists, or when the whole month is already merged."""
    if Path(step["out_path"]).exists():
        return True
    return step["label"] != step["month"] and whole_month_path(step).exists()


def stray_parts(steps: list[dict[str, Any]]) -> list[str]:
    """Part files left by an earlier --split run that this (unsplit) run would ignore."""
    stray = []
    for step in steps:
        if step["label"] != step["month"] or month_done(step):
            continue
        folder = Path(step["out_path"]).parent
        stray += [p.name for p in folder.glob(f"{PREFIX[step['kind']]}{step['month']}[a-z].parquet")]
    return stray


def merge_parts(steps: list[dict[str, Any]]) -> list[str]:
    """Join the parts of each split month into one monthly file, then remove the parts."""
    merged = []
    groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for step in steps:
        if step["label"] != step["month"]:
            groups.setdefault((step["kind"], step["month"]), []).append(step)
    for (kind, month), parts in groups.items():
        target = whole_month_path(parts[0])
        paths = [Path(p["out_path"]) for p in parts]
        if target.exists() or not all(p.exists() for p in paths):
            continue
        frames = [pd.read_parquet(p) for p in paths]
        _write_atomic(pd.concat(frames, ignore_index=True), target)
        for p in paths:
            p.unlink()
        merged.append(target.name)
    return merged


def _query_params(kind: str, config: dict[str, Any], wallets: list[str], start_ts: str, end_ts: str) -> list:
    if kind == "gmx":
        from extract_margin_week import query_params as gmx_params

        return gmx_params(config, start_ts, end_ts)
    from extract_reputation_data import query_params as rep_params

    return rep_params(config, wallets, start_ts, end_ts)


def _normalize(kind: str, df: pd.DataFrame) -> pd.DataFrame:
    if kind == "gmx":
        return df
    from extract_reputation_data import normalize_approvals, normalize_transfers

    return normalize_approvals(df) if kind == "approvals" else normalize_transfers(df)


def _write_atomic(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".parquet.tmp")
    df.to_parquet(tmp, index=False)
    os.replace(tmp, path)


def decode_gmx(config: dict[str, Any], reg: dict[str, Any]) -> dict[str, Any]:
    """Decode every fresh GMX month with the spring decoder into one parquet."""
    from concurrent.futures import ProcessPoolExecutor, as_completed

    from decode_gmx_events import _decode_records

    ex = reg["extraction"]
    folder = Path(ex["raw_gmx_dir"])
    files = sorted(folder.glob(f"{PREFIX['gmx']}*.parquet"))
    if not files:
        raise FileNotFoundError(f"No GMX month files in {folder}")
    raw = pd.concat([pd.read_parquet(p) for p in files], ignore_index=True)
    rows = raw.to_dict(orient="records")
    chunks = [rows[i : i + 10000] for i in range(0, len(rows), 10000)]
    gmx = config["gmx_arbitrum"]
    decoded: list[dict] = []
    errors = 0
    with ProcessPoolExecutor(max_workers=min(8, max(1, len(chunks)))) as pool:
        futures = [
            pool.submit(_decode_records, chunk, gmx["liquidation_handler"], gmx["order_type_liquidation"])
            for chunk in chunks
        ]
        for fut in as_completed(futures):
            part, err = fut.result()
            decoded.extend(part)
            errors += err
    out_df = pd.DataFrame(decoded)
    _write_atomic(out_df, Path(ex["decoded_gmx"]))
    return {
        "at": datetime.now(timezone.utc).isoformat(),
        "input_files": [p.name for p in files],
        "input_rows": int(len(raw)),
        "decoded_rows": int(len(out_df)),
        "decode_errors": int(errors),
        "output": ex["decoded_gmx"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--registration", type=Path, default=REGISTRATION_PATH)
    parser.add_argument("--dry-run", action="store_true", help="estimate bytes only")
    parser.add_argument("--extract", action="store_true", help="run the queries")
    parser.add_argument("--decode-only", action="store_true", help="decode the GMX month files already on disk")
    parser.add_argument("--yes", action="store_true", help="skip the confirmation prompt")
    parser.add_argument("--split", type=int, default=1, help="query each month in N parts")
    parser.add_argument("--kinds", default=",".join(KINDS), help="comma list of approvals,transfers,gmx")
    parser.add_argument(
        "--allow-unregistered",
        action="store_true",
        help="testing only: extract before the registration is committed (recorded in the manifest)",
    )
    args = parser.parse_args()
    if not (args.dry_run or args.extract or args.decode_only):
        parser.error("Specify --dry-run, --extract or --decode-only")

    config = load_config()
    reg = load_registration(args.registration)
    manifest_path = Path(reg["extraction"]["manifest"])
    manifest = load_json(manifest_path)
    manifest.setdefault("registration", {})
    manifest["registration"].update(
        {"id": reg["registration"]["id"], "sha256": reg.get("_sha256"), "plan_sha256": reg.get("_plan_sha256")}
    )

    if args.decode_only:
        manifest["decode"] = decode_gmx(config, reg)
        save_json(manifest_path, manifest)
        print(f"Decoded {manifest['decode']['decoded_rows']} GMX events -> {reg['extraction']['decoded_gmx']}")
        return 0

    kinds = tuple(k.strip() for k in args.kinds.split(",") if k.strip())
    unknown = set(kinds) - set(KINDS)
    if unknown:
        parser.error(f"unknown kinds: {sorted(unknown)}")

    from extract_reputation_data import load_wallet_addresses

    wallets = load_wallet_addresses(config, None)
    expected = int(reg["extraction"]["expected_wallets"])
    if len(wallets) != expected:
        print(f"Wallet filter has {len(wallets)} addresses; the registration expects {expected}. Stopping.")
        return 1

    if args.extract:
        ok, problems, states = registration_check(reg)
        manifest["registration"]["git"] = states
        if not ok:
            if not args.allow_unregistered:
                print("The registration is not in place, so nothing will be extracted:")
                for p in problems:
                    print(f"  - {p}")
                print("Commit config/fresh_holdout_2026q3.yaml (status: registered) and the plan first.")
                return 1
            print("WARNING: extracting without a committed registration (--allow-unregistered).")
            manifest["registration"]["unregistered_extraction"] = True

    from google.cloud import bigquery
    from google.cloud.bigquery import QueryJobConfig

    client = bigquery.Client(project=config.get("bigquery", {}).get("project_id"))
    logs_fqn = config["bigquery"]["logs_fqn"]
    sql = {k: read_sql(SQL_FILES[k]).replace("__LOGS_FQN__", logs_fqn) for k in kinds}
    budget = int(config.get("budget", {}).get("max_bytes_per_query", 0))

    steps = plan_steps(reg, kinds, args.split)
    leftovers = stray_parts(steps)
    if leftovers:
        print(f"Part files from an earlier --split run are on disk: {leftovers}. Re-run with the same --split.")
        return 1
    pending = [s for s in steps if not month_done(s)]
    print(f"{len(steps)} steps, {len(steps) - len(pending)} already on disk")
    total = 0
    over_budget = []
    for step in pending:
        params = _query_params(step["kind"], config, wallets, step["start_ts"], step["end_ts"])
        job = client.query(sql[step["kind"]], job_config=QueryJobConfig(dry_run=True, use_query_cache=False, query_parameters=params))
        step["dry_run_bytes"] = int(job.total_bytes_processed or 0)
        total += step["dry_run_bytes"]
        flag = ""
        if budget and step["dry_run_bytes"] > budget:
            over_budget.append(step["id"])
            flag = "  OVER BUDGET"
        print(f"  {step['id']:22s} {format_bytes(step['dry_run_bytes'])}{flag}")
    print(f"Dry-run total: {format_bytes(total)}")
    manifest["dry_run"] = {
        "at": datetime.now(timezone.utc).isoformat(),
        "split": args.split,
        "steps": [{k: s[k] for k in ("id", "start_ts", "end_ts", "dry_run_bytes")} for s in pending],
        "total_bytes": total,
    }
    save_json(manifest_path, manifest)
    if over_budget:
        print(f"Above the per-query budget ({format_bytes(budget)}): {over_budget}. Re-run with --split 2.")
        return 1
    if args.dry_run and not args.extract:
        return 0

    if not args.yes:
        answer = input(f"Extract {len(pending)} steps, about {format_bytes(total)}? [y/N] ")
        if answer.strip().lower() != "y":
            print("Aborted.")
            return 0

    done = manifest.setdefault("steps", {})
    for step in pending:
        params = _query_params(step["kind"], config, wallets, step["start_ts"], step["end_ts"])
        print(f"Extracting {step['id']} ...", flush=True)
        job = client.query(sql[step["kind"]], job_config=QueryJobConfig(use_query_cache=False, query_parameters=params))
        df = _normalize(step["kind"], job.to_dataframe())
        _write_atomic(df, Path(step["out_path"]))
        done[step["id"]] = {
            "rows": int(len(df)),
            "bytes_billed": int(job.total_bytes_billed or 0),
            "job_id": job.job_id,
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "output": step["out_path"],
        }
        save_json(manifest_path, manifest)
        print(f"  {len(df)} rows -> {step['out_path']}")

    joined = merge_parts(steps)
    if joined:
        manifest["merged_parts"] = sorted(set(manifest.get("merged_parts", [])) | set(joined))
        save_json(manifest_path, manifest)
        print(f"Merged split months: {joined}")

    if "gmx" in kinds:
        manifest["decode"] = decode_gmx(config, reg)
        save_json(manifest_path, manifest)
        print(f"Decoded {manifest['decode']['decoded_rows']} GMX events -> {reg['extraction']['decoded_gmx']}")
    print(f"Manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
