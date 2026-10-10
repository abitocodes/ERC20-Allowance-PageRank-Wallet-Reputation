#!/usr/bin/env python3
"""BigQuery steps of the revised analysis (docs/revision_price_weighting.md), in order.

Every query goes through scripts/run_bq.py, which dry-runs it, checks the budget of the
configuration and writes the bytes it billed to data/bq_ledger.json. Steps:

  load       load data/0-usd-token-list-and-prices/{listed_tokens,daily_prices_usd}.csv into
             contract_rep.u_tokens and contract_rep.u_prices (load jobs are not billed; the
             conversion of the hex addresses to BYTES is a query on the two small tables)
  ego        sql/12_usd_ego.sql: revised cohort and listed-token ego tables
  constants  sql/13_usd_constants.sql, then the rounded constants into constants.json
  pairs      sql/14_usd_anchor_pairs.sql at T_obs and at t1
  rest       sql/15 (proxies), sql/16 (labels W0 and W1), sql/17 (node ids), sql/18 (description)
  download   the tables the local scripts read, into graph-tables-usd (Storage Read API)

Usage: python scripts/run_usd_pipeline.py STEP [STEP ...] [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("CONTRACT_REP_VARIANT", "usd")
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import PROC, PROC_SHARED, RAW, REVISED, ROOT, USD_INPUTS, load_config, read_parts, save_json, write_parts  # noqa: E402
from usd import UNLIMITED_BASE_UNITS, round_sig, slope_for_median  # noqa: E402

if not REVISED:
    raise SystemExit("run_usd_pipeline.py belongs to the revised analysis (CONTRACT_REP_VARIANT=usd)")

GRAPH_USD = RAW / "graph-tables-usd"
CONSTANTS = USD_INPUTS / "constants.json"
STEPS = ("load", "ego", "constants", "pairs", "rest", "download")


def bq_run(sql: str, *, params: dict[str, str] | None = None, subs: dict[str, str] | None = None,
           label: str, dry: bool) -> None:
    cmd = [sys.executable, "scripts/run_bq.py", f"sql/{sql}", "--label", label]
    for k, v in (params or {}).items():
        cmd += ["--param", f"{k}={v}"]
    for k, v in (subs or {}).items():
        cmd += ["--sub", f"{k}={v}"]
    if dry:
        cmd.append("--dry-run")
    print("$", " ".join(cmd[1:]), flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True)


def bq_cli(*args: str) -> str:
    return subprocess.run(["bq", *args], cwd=ROOT, capture_output=True, text=True, check=True, shell=True).stdout


def constants() -> dict:
    if not CONSTANTS.exists():
        raise SystemExit(f"{CONSTANTS} is missing; run the 'constants' step first")
    return json.loads(CONSTANTS.read_text(encoding="utf-8"))


def step_load(cfg: dict, dry: bool) -> None:
    project, ds = cfg["bigquery"]["project_id"], cfg["bigquery"]["dataset"]
    tokens, prices = USD_INPUTS / "listed_tokens.csv", USD_INPUTS / "daily_prices_usd.csv"
    for f in (tokens, prices):
        if not f.exists():
            raise SystemExit(f"{f} is missing; run scripts/usd_inputs.py first")
    # Only the selected tokens (listed, priced, the TOP_N by rows) enter the revised SQL.
    import pandas as pd
    lst = pd.read_csv(tokens)
    priced = lst[lst["selected"].astype(str).str.lower() == "true"][["address", "symbol", "name", "decimals"]]
    work = ROOT / "data" / "_work" / "usd"
    work.mkdir(parents=True, exist_ok=True)
    priced.to_csv(work / "u_tokens_load.csv", index=False)
    print(f"load: {len(priced)} selected tokens of {len(lst)} listed")
    if dry:
        print("load: would load", tokens.name, "and", prices.name)
        return
    bq_cli("load", "--replace", "--source_format=CSV", "--skip_leading_rows=1", "--ignore_unknown_values",
           f"{project}:{ds}.u_tokens_hex", str(work / "u_tokens_load.csv"),
           "address:STRING,symbol:STRING,name:STRING,decimals:INTEGER")
    bq_cli("load", "--replace", "--source_format=CSV", "--skip_leading_rows=1", "--ignore_unknown_values",
           f"{project}:{ds}.u_prices_hex", str(prices),
           "address:STRING,day:DATE,price_usd:FLOAT,confidence:FLOAT,filled:BOOLEAN,filled_from:DATE")
    bq_run("19_usd_load.sql", label="revised: token list and prices to BYTES", dry=False)


def step_ego(cfg: dict, dry: bool) -> None:
    p = cfg["period"]
    bq_run("12_usd_ego.sql", params={"start_ts": p["start_ts"], "end_ts": p["end_ts"]},
           label="revised: cohort and listed-token ego tables", dry=dry)


def step_constants(cfg: dict, dry: bool) -> None:
    bq_run("13_usd_constants.sql",
           params={"start_ts": cfg["period"]["start_ts"], "t1": cfg["holdout"]["score_end"],
                   "unlimited": repr(UNLIMITED_BASE_UNITS)},
           label="revised: USD scale constants up to t1", dry=dry)
    if dry:
        return
    ds = f"{cfg['bigquery']['project_id']}.{cfg['bigquery']['dataset']}"
    out = bq_cli("query", "--use_legacy_sql=false", "--format=json", f"SELECT * FROM `{ds}.u_constants`")
    row = {k: float(v) for k, v in json.loads(out[out.index("["):])[0].items()}
    m_t, m_a, cap = (round_sig(row["m_transfer"]), round_sig(row["m_allowance"]), round_sig(row["p99_transfer"]))
    save_json({
        "computed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "sql/13_usd_constants.sql (contract_rep.u_constants), events up to t1",
        "raw": row,
        "m_transfer_usd": m_t, "m_allowance_usd": m_a, "cap_allowance_usd": cap,
        "b_transfer": slope_for_median(m_t), "b_allowance": slope_for_median(m_a),
        "unlimited_base_units": UNLIMITED_BASE_UNITS,
        "rule": "b = ln 3 / m with m the median rounded to two significant digits; the allowance cap U is the "
                "99th percentile of the USD values of the transfers up to t1, rounded to two significant digits",
    }, CONSTANTS)
    print(json.dumps(json.loads(CONSTANTS.read_text(encoding="utf-8")), indent=1))


def step_pairs(cfg: dict, dry: bool) -> None:
    c = constants() if not dry else {"b_transfer": 0.01, "b_allowance": 0.01, "cap_allowance_usd": 1e6}
    for tag, anchor in (("tobs", cfg["period"]["observation_end"]), ("t1", cfg["holdout"]["score_end"])):
        bq_run("14_usd_anchor_pairs.sql", subs={"TAG": tag},
               params={"start_ts": cfg["period"]["start_ts"], "anchor_ts": anchor,
                       "b_transfer": repr(c["b_transfer"]), "b_allowance": repr(c["b_allowance"]),
                       "cap_allowance": repr(c["cap_allowance_usd"])},
               label=f"revised: pairs at {tag}", dry=dry)


def step_rest(cfg: dict, dry: bool) -> None:
    p, h, w = cfg["period"], cfg["holdout"], cfg["registered_window"]
    c = constants() if not dry else {"cap_allowance_usd": 1e6}
    bq_run("15_usd_proxies.sql", params={"start_ts": p["start_ts"], "anchor_ts": p["observation_end"]},
           label="revised: same-window proxies", dry=dry)
    bq_run("16_usd_labels.sql",
           params={"start_ts": p["start_ts"], "t1": h["score_end"], "out_start": h["outcome_start"],
                   "out_end": h["outcome_end"]},
           subs={"TAG": "w0", "FREEZE": "t1", "APPROVALS": "u_approvals", "TRANSFERS": "u_transfers",
                 "LOGS": "logs_obs"},
           label="revised: W0 labels", dry=dry)
    bq_run("16_usd_labels.sql",
           params={"start_ts": p["start_ts"], "t1": w["score_end"], "out_start": w["outcome_start"],
                   "out_end": w["outcome_end"]},
           subs={"TAG": "w1", "FREEZE": "tobs", "APPROVALS": "u_approvals_w1", "TRANSFERS": "u_transfers_w1",
                 "LOGS": "logs_w1"},
           label="revised: W1 labels", dry=dry)
    bq_run("17_usd_export_ids.sql", label="revised: node ids and export tables", dry=dry)
    bq_run("18_usd_describe.sql",
           params={"unlimited": repr(UNLIMITED_BASE_UNITS), "cap_allowance": repr(c["cap_allowance_usd"])},
           label="revised: descriptive statistics", dry=dry)


def cohort_summary(cfg: dict) -> None:
    """The revised cohort against the registered one, as cohort/matched_cohort.json of the revised analysis."""
    u = read_parts(GRAPH_USD / "cohort")
    u["wallet"] = u["address"].map(lambda b: "0x" + bytes(b).hex())
    reg = read_parts(PROC_SHARED / "cohort" / "matched_cohort")
    reg_set, new_set = set(reg["wallet"]), set(u["wallet"])
    if not new_set <= reg_set:
        raise SystemExit(f"{len(new_set - reg_set)} revised cohort contracts are not in the registered cohort")
    out = u[["wallet", "owners_nonzero", "approval_logs"]].sort_values("wallet").reset_index(drop=True)
    write_parts(out, PROC / "cohort" / "matched_cohort")
    save_json({
        "rule": f"contracts of the registered cohort with non-zero approvals of a listed token from >= "
                f"{cfg['cohort']['min_owners']} distinct owners, {cfg['period']['start_ts']} to "
                f"{cfg['period']['observation_end']}",
        "registered_cohort": int(len(reg_set)),
        "cohort": int(len(new_set)),
        "left_out_of_registered": int(len(reg_set - new_set)),
        "source": "contract_rep.u_cohort (sql/12_usd_ego.sql)",
    }, PROC / "cohort" / "matched_cohort.json")
    print(f"revised cohort: {len(new_set):,} of {len(reg_set):,} registered cohort contracts")


def step_download(cfg: dict, dry: bool) -> None:
    tables = [("u_cohort", "cohort"), ("u_x_nodes", "nodes"), ("u_x_allow_pairs_tobs", "allow_pairs_tobs"),
              ("u_x_transfer_pairs_tobs", "transfer_pairs_tobs"), ("u_x_allow_pairs_t1", "allow_pairs_t1"),
              ("u_x_transfer_pairs_t1", "transfer_pairs_t1"), ("u_proxies_tobs", "proxies_tobs"),
              ("u_labels_w0", "labels_w0"), ("u_labels_w1", "labels_w1")]
    for table, stem in tables:
        cmd = [sys.executable, "scripts/download_table.py", f"contract_rep.{table}", str(GRAPH_USD / stem)]
        print("$", " ".join(cmd[1:]), flush=True)
        if not dry:
            subprocess.run(cmd, cwd=ROOT, check=True)
    if not dry:
        cohort_summary(cfg)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("steps", nargs="+", choices=STEPS)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    cfg = load_config()
    for s in args.steps:
        globals()[f"step_{s}"](cfg, args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
