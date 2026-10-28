#!/usr/bin/env python3
"""BigQuery steps of the twelve-month revised analysis (docs/revision_one_year_window.md), in order.

Every query goes through scripts/run_bq.py with the checks of this variant: a job creates only
u12_* tables, reads only the tables named here, is labelled "usd12m: ..." and is refused if the
jobs of the campaign would pass USD 4.00. Each job carries an estimate of the bytes it bills: the
rows of the monthly partitions it scans times the widths of the columns it reads (a 20-byte
address takes 22 bytes; a timestamp, integer or float 8), since the dry run of a file with several
statements counts only the first. A job whose first statement dry-runs above 1.25 times its
estimate is refused, and after a job that billed more than 1.5 times its estimate the driver stops.
Steps:

  check      free metadata checks: the windows of the overlay, no expiration on the dataset, the
             source tables of the 33-month build with their row counts, no u12_* table before the
             first job, the ledger; prints the estimate of every job
  tokens     sql/20: rows of every token of the registered ego data in the T_obs score window,
             ranked locally into data/0-usd-token-list-and-prices/usd-12m/token_rows.json
             (reported only; the five selected tokens stay)
  cohorts    sql/21: the cohort of each freeze and the views of its ego events
  constants  sql/13 on the W0 views, then the rounded constants into usd-12m/constants.json
  pairs      sql/14 at T_obs and at t1
  rest       sql/15 (proxies), sql/16 (labels W0 and W1), sql/17 (node ids), sql/22 (description)
  checks     sql/23: invariants against the 33-month tables; every count must be zero
  download   the tables the local scripts read, into graph-tables-usd-12m (Storage Read API), and
             the cohort summaries

Every step but check refuses to run unless the files in COMMITTED are committed without local
changes (a --dry-run only warns). data/2-.../revised-usd-12m/run_manifest.json records the
commit, the hashes of those files, every job and the results of every step.

Usage: python scripts/run_usd12m_pipeline.py STEP [STEP ...] [--dry-run]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

os.environ.setdefault("CONTRACT_REP_VARIANT", "usd12m")
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (GRAPH, PROC, PROC_SHARED, RAW, ROOT, USD_CONSTANTS, USD_INPUTS, VARIANT,  # noqa: E402
                    load_config, load_json, read_parts, save_json, write_parts)
from usd import UNLIMITED_BASE_UNITS, round_sig, slope_for_median  # noqa: E402

# The 33-month tables, folders and constants belong to scripts/run_usd_pipeline.py.
if VARIANT != "usd12m":
    raise SystemExit("run_usd12m_pipeline.py belongs to the twelve-month variant (CONTRACT_REP_VARIANT=usd12m)")

STEPS = ("check", "tokens", "cohorts", "constants", "pairs", "rest", "checks", "download")
PREFIX, CAMPAIGN, CAP_USD = "u12_", "usd12m:", 4.0
DRY_RATIO, BILL_RATIO = 1.25, 1.5
LEDGER = ROOT / "data" / "bq_ledger.json"
MANIFEST = PROC / "run_manifest.json"
TOKEN_ROWS = USD_INPUTS / "usd-12m" / "token_rows.json"
SQL_FILES = ("13_usd_constants.sql", "14_usd_anchor_pairs.sql", "15_usd_proxies.sql", "16_usd_labels.sql",
             "17_usd_export_ids.sql", "20_usd12m_token_rows.sql", "21_usd12m_cohorts.sql",
             "22_usd12m_describe.sql", "23_usd12m_checks.sql")
COMMITTED = ("docs/revision_one_year_window.md", "config/overlay_usd12m.yaml", "config/contract_reputation.yaml",
             "scripts/run_usd12m_pipeline.py", "scripts/run_bq.py", "scripts/common.py",
             *(f"sql/{f}" for f in SQL_FILES))

# The windows of docs/revision_one_year_window.md section 3 (ends exclusive); the configuration with
# the overlay must give exactly these.
WINDOWS = {
    "tobs_start": "2025-07-01 00:00:00 UTC", "tobs_end": "2026-07-01 00:00:00 UTC",
    "t1_start": "2025-04-01 00:00:00 UTC", "t1_end": "2026-04-01 00:00:00 UTC",
    "w0_end": "2026-07-01 00:00:00 UTC",
}
# Bounds counted before this revision from the 33-month pair tables, by the latest event of each pair.
# Cohort floor: u_cohort contracts with at least three owners whose latest positive allowance at the
# anchor was set inside the window (each of them approved the contract inside the window). Pair
# ceilings: 33-month pairs whose latest event falls inside the window, rounded up at the last digit
# shown in the preview; every twelve-month pair is one of them.
COHORT_FLOOR = {"tobs": 5_577, "t1": 5_421}
PAIR_CEILING = {"allow_pairs_tobs": 3_815_000, "allow_pairs_t1": 4_125_000,
                "transfer_pairs_tobs": 8_785_000, "transfer_pairs_t1": 9_735_000}

# Byte widths that BigQuery bills: an address (BYTES of 20: 2 + 20) and a timestamp, integer or float.
W_ADDR, W_NUM = 22, 8
MIN_TABLE = 10 * 2**20  # at least 10 MB is billed for every table a query reads
USD_PER_TIB = 6.25

# Tables whose row counts the estimates and the checks read from the table metadata.
META_TABLES = ("u_approvals", "u_transfers", "u_approvals_w1", "u_transfers_w1", "u_cohort", "u_tokens", "u_prices",
               "u_allow_triples_tobs", "u_allow_triples_t1", "u_allow_pairs_tobs", "u_allow_pairs_t1",
               "u_transfer_pairs_tobs", "u_transfer_pairs_t1", "u_nodes", "approvals_ego", "transfers_ego",
               "approvals_w1ego", "transfers_w1ego", "logs_obs", "logs_w1")
MONTHLY = ("u_approvals", "u_transfers", "u_approvals_w1", "u_transfers_w1", "approvals_ego", "transfers_ego",
           "approvals_w1ego", "transfers_w1ego", "logs_obs", "logs_w1")
# 33-month jobs whose bills calibrate the estimates of the same SQL here.
CALIBRATION = {"labels_w0": "revised: W0 labels", "labels_w1": "revised: W1 labels",
               "node_ids": "revised: node ids and export tables"}


# --------------------------------------------------------------------------- windows and sources


def windows(cfg: dict) -> dict:
    """The score windows from the configuration, checked against docs/revision_one_year_window.md."""
    p, h = cfg["period"], cfg["holdout"]
    w = {"tobs_start": p["start_ts"], "tobs_end": p["end_ts"], "t1_start": h["start_ts"],
         "t1_end": h["outcome_start"], "w0_end": p["end_ts"]}
    if w != WINDOWS:
        raise SystemExit(f"the configuration gives the windows {w}, not those of the revision {WINDOWS}")
    if _ts(h["outcome_end"]) + timedelta(seconds=1) != _ts(w["w0_end"]):
        raise SystemExit("the W0 label window does not end where the T_obs score window ends")
    return w


def _ts(s: str) -> datetime:
    return datetime.fromisoformat(str(s).replace(" UTC", ""))


def month_list(start: str, end: str) -> list[str]:
    """The months of [start, end); both bounds are the first second of a month."""
    a, b = _ts(start), _ts(end)
    if a.day != 1 or b.day != 1 or a.time() != datetime.min.time() or b.time() != datetime.min.time():
        raise ValueError(f"{start} or {end} is not the start of a month")
    out, y, m = [], a.year, a.month
    while (y, m) < (b.year, b.month):
        out.append(f"{y:04d}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


class Sources:
    """Rows of the tables the jobs read: per month from the describe files of the 33-month build (the
    rows of the monthly partitions), otherwise all rows from the table metadata."""

    def __init__(self, table_rows: dict[str, int]):
        rev = load_json(PROC_SHARED / "revised-usd" / "describe" / "describe.json")
        reg = load_json(PROC_SHARED / "describe" / "describe.json")
        self.monthly = {}
        for table, d, stream in (("u_approvals", rev, "approval_ego"), ("u_transfers", rev, "transfer_ego"),
                                 ("approvals_ego", reg, "approval_ego"), ("transfers_ego", reg, "transfer_ego")):
            self.monthly[table] = {r["month"]: int(r["n"]) for r in d["monthly_counts"] if r["stream"] == stream}
        self.table_rows = dict(table_rows)

    def rows(self, table: str, start: str | None = None, end: str | None = None) -> int:
        if start is None:
            return int(self.table_rows[table])
        months = month_list(start, end)
        missing = [m for m in months if m not in self.monthly[table]]
        if missing:
            raise SystemExit(f"no monthly count of {table} for {missing}")
        return sum(self.monthly[table][m] for m in months)


def w_(addr: int, num: int) -> int:
    return addr * W_ADDR + num * W_NUM


def calibration() -> dict:
    jobs = load_json(LEDGER)["jobs"]
    out = {}
    for key, label in CALIBRATION.items():
        hits = [j for j in jobs if j.get("label") == label]
        if len(hits) != 1:
            raise SystemExit(f"the ledger has {len(hits)} jobs labelled {label!r}, not one")
        out[key] = hits[0]
    return out


def estimates(src: Sources, cfg: dict, cal: dict) -> dict[str, tuple[int, int]]:
    """(first statement, whole job) billed bytes of every job. A u12_ table that a job reads is bounded by
    its 33-month counterpart, since each twelve-month table is a subset of it. sql/16 scans the logs of
    the label window for the drain heuristic exactly as the 33-month job did; that scan is the 33-month
    bill minus the rest of its formula. sql/17 reads only subsets of what the 33-month job read, so its
    33-month dry run and bill bound it."""
    w, base = windows(cfg), cfg["bigquery"]["scan_a"]["start_ts"]
    tobs, t1, w0 = (w["tobs_start"], w["tobs_end"]), (w["t1_start"], w["t1_end"]), (w["t1_end"], w["w0_end"])

    def a(win):
        return src.rows("u_approvals", *win)

    def t(win):
        return src.rows("u_transfers", *win)

    n = src.rows

    def drain(tag: str) -> int:
        if tag == "w0":
            rest = (n("u_allow_triples_t1") * w_(2, 1) + a(w0) * w_(3, 2)
                    + t((base, w["t1_end"])) * w_(2, 2) + t(w0) * w_(2, 2))
        else:
            rest = (n("u_allow_triples_tobs") * w_(2, 1) + n("u_approvals_w1") * w_(3, 2)
                    + t((base, w["tobs_end"])) * w_(2, 2) + n("u_transfers_w1") * w_(2, 2))
        out = int(cal[f"labels_{tag}"]["bytes_billed"]) - rest - MIN_TABLE
        if out <= 0:
            raise SystemExit(f"the 33-month {tag} labels job billed less than its formula without the logs")
        return out

    stmts = {
        # transfers_ego: token, time; approvals_ego: token, owner, spender, time, block, log index, value
        "tokens": [src.rows("transfers_ego", *tobs) * w_(1, 1) + src.rows("approvals_ego", *tobs) * w_(3, 4)],
        # spender, owner, value, time
        "cohorts": [a(tobs) * w_(2, 2) + MIN_TABLE, a(t1) * w_(2, 2) + MIN_TABLE],
        # transfers: usd, time, sender, recipient; approvals: every column
        "constants": [t(t1) * w_(2, 2) + a(t1) * w_(3, 5) + 2 * MIN_TABLE],
        "pairs_tobs": [a(tobs) * w_(3, 5) + 2 * MIN_TABLE, n("u_allow_triples_tobs") * w_(2, 3),
                       t(tobs) * w_(2, 2) + MIN_TABLE],
        "pairs_t1": [a(t1) * w_(3, 5) + 2 * MIN_TABLE, n("u_allow_triples_t1") * w_(2, 3),
                     t(t1) * w_(2, 2) + MIN_TABLE],
        "proxies": [t(tobs) * w_(2, 2) + MIN_TABLE],
        # snapshot pairs; label-window approvals; senders seen in the score window; label-window senders
        "labels_w0": [n("u_allow_triples_t1") * w_(2, 1) + a(w0) * w_(3, 2) + t(t1) * w_(2, 2) + t(w0) * w_(2, 2)
                      + drain("w0") + 2 * MIN_TABLE],
        "labels_w1": [n("u_allow_triples_tobs") * w_(2, 1) + n("u_approvals_w1") * w_(3, 2) + t(tobs) * w_(2, 2)
                      + n("u_transfers_w1") * w_(2, 2) + drain("w1") + 2 * MIN_TABLE],
        "describe": [
            src.rows("approvals_ego", *tobs) * w_(1, 1) + src.rows("transfers_ego", *tobs) * w_(1, 1)
            + n("approvals_w1ego") * w_(1, 0) + n("transfers_w1ego") * w_(1, 0)
            + a(tobs) * w_(3, 1) + t(tobs) * w_(3, 2) + n("u_approvals_w1") * w_(3, 0)
            + n("u_transfers_w1") * w_(3, 1) + 2 * MIN_TABLE,
            (a(tobs) + t(tobs) + a(t1) + t(t1)) * w_(2, 1),
            2 * n("u_allow_triples_tobs") * w_(1, 2) + t(tobs) * w_(2, 2)],
        # each allowance table is read twice (EXCEPT in both directions)
        "checks": [4 * (n("u_allow_triples_tobs") + n("u_allow_triples_t1")) * w_(3, 2)
                   + (n("u_transfer_pairs_tobs") + n("u_transfer_pairs_t1")) * (w_(2, 2) + w_(2, 1))
                   + 3 * MIN_TABLE],
    }
    out = {k: (int(v[0]), int(sum(v))) for k, v in stmts.items()}
    out["node_ids"] = (int(cal["node_ids"]["bytes_estimated"]), int(cal["node_ids"]["bytes_billed"]))
    return out


def usd(nbytes: float) -> float:
    return nbytes / 2**40 * USD_PER_TIB


# --------------------------------------------------------------------------- jobs


@dataclass
class Job:
    key: str
    sql: str
    label: str
    params: dict = field(default_factory=dict)
    subs: dict = field(default_factory=dict)
    renames: dict = field(default_factory=dict)
    allow: tuple = ()


def constants() -> dict:
    if not USD_CONSTANTS.exists():
        raise SystemExit(f"{USD_CONSTANTS} is missing; run the 'constants' step first")
    return load_json(USD_CONSTANTS)


def jobs(cfg: dict, c: dict | None = None) -> dict[str, list[Job]]:
    """The jobs of every step. ``c`` holds the twelve-month constants (placeholders before they exist)."""
    c = c or {"b_transfer": 0.01, "b_allowance": 0.01, "cap_allowance_usd": 1e6}
    w, p, h, r = windows(cfg), cfg["period"], cfg["holdout"], cfg["registered_window"]
    views = {tag: {"u_approvals": f"u12_approvals_{tag}", "u_transfers": f"u12_transfers_{tag}"}
             for tag in ("tobs", "t1")}
    weights = {"b_transfer": repr(c["b_transfer"]), "b_allowance": repr(c["b_allowance"]),
               "cap_allowance": repr(c["cap_allowance_usd"])}
    pairs = []
    for tag, start, anchor in (("tobs", w["tobs_start"], p["observation_end"]), ("t1", w["t1_start"], h["score_end"])):
        pairs.append(Job(f"pairs_{tag}", "14_usd_anchor_pairs.sql", f"pairs at {tag}", subs={"TAG": tag},
                         params={"start_ts": start, "anchor_ts": anchor, **weights},
                         renames={**views[tag], **{f"u_{x}_{tag}": f"u12_{x}_{tag}"
                                                   for x in ("allow_triples", "allow_pairs", "transfer_pairs")}},
                         allow=("u_prices",)))
    node_tables = ("allow_pairs_tobs", "allow_pairs_t1", "transfer_pairs_tobs", "transfer_pairs_t1", "nodes",
                   "x_nodes", "x_allow_pairs_tobs", "x_allow_pairs_t1", "x_transfer_pairs_tobs",
                   "x_transfer_pairs_t1")
    return {
        "tokens": [Job("tokens", "20_usd12m_token_rows.sql", "token rows of the T_obs score window",
                       params={"start_ts": w["tobs_start"], "end_ts": w["tobs_end"], "anchor_ts": p["observation_end"]},
                       allow=("approvals_ego", "transfers_ego"))],
        "cohorts": [Job("cohorts", "21_usd12m_cohorts.sql", "cohorts of T_obs and t1 and their ego views",
                        subs={k.upper(): v for k, v in w.items()},
                        allow=("u_approvals", "u_transfers", "u_cohort", "u_approvals_w1", "u_transfers_w1"))],
        "constants": [Job("constants", "13_usd_constants.sql", "USD scale constants on the W0 score window",
                          params={"start_ts": w["t1_start"], "t1": h["score_end"],
                                  "unlimited": repr(UNLIMITED_BASE_UNITS)},
                          renames={**views["t1"], "u_constants": "u12_constants"}, allow=("u_prices",))],
        "pairs": pairs,
        "rest": [
            Job("proxies", "15_usd_proxies.sql", "same-window proxies",
                params={"start_ts": w["tobs_start"], "anchor_ts": p["observation_end"]},
                renames={"u_cohort": "u12_cohort_tobs", "u_transfers": "u12_transfers_tobs",
                         "u_proxies_tobs": "u12_proxies_tobs"}),
            Job("labels_w0", "16_usd_labels.sql", "W0 labels",
                params={"start_ts": w["t1_start"], "t1": h["score_end"], "out_start": h["outcome_start"],
                        "out_end": h["outcome_end"]},
                subs={"TAG": "w0", "FREEZE": "t1", "APPROVALS": "u12_approvals_t1", "TRANSFERS": "u12_transfers_t1",
                      "LOGS": "logs_obs"},
                renames={"u_transfers": "u12_transfers_t1", "u_allow_triples_t1": "u12_allow_triples_t1",
                         "u_labels_w0": "u12_labels_w0"},
                allow=("u_tokens", "logs_obs")),
            Job("labels_w1", "16_usd_labels.sql", "W1 labels",
                params={"start_ts": w["tobs_start"], "t1": r["score_end"], "out_start": r["outcome_start"],
                        "out_end": r["outcome_end"]},
                subs={"TAG": "w1", "FREEZE": "tobs", "APPROVALS": "u12_approvals_w1",
                      "TRANSFERS": "u12_transfers_w1", "LOGS": "logs_w1"},
                renames={"u_transfers": "u12_transfers_tobs", "u_allow_triples_tobs": "u12_allow_triples_tobs",
                         "u_labels_w1": "u12_labels_w1"},
                allow=("u_tokens", "logs_w1")),
            Job("node_ids", "17_usd_export_ids.sql", "node ids and export tables",
                renames={**{f"u_{x}": f"u12_{x}" for x in node_tables}, "u_cohort": "u12_cohort_tobs"}),
            Job("describe", "22_usd12m_describe.sql", "descriptive statistics of the score windows",
                params={"tobs_start": w["tobs_start"], "tobs_end": w["tobs_end"], "t1_start": w["t1_start"],
                        "t1_end": w["t1_end"], "unlimited": repr(UNLIMITED_BASE_UNITS),
                        "cap_allowance": repr(c["cap_allowance_usd"])},
                allow=("u_tokens", "approvals_ego", "transfers_ego", "approvals_w1ego", "transfers_w1ego")),
        ],
        "checks": [Job("checks", "23_usd12m_checks.sql", "invariants against the 33-month tables",
                       params={"tobs_start": w["tobs_start"], "t1_start": w["t1_start"]},
                       allow=("u_allow_triples_tobs", "u_allow_triples_t1", "u_transfer_pairs_tobs",
                              "u_transfer_pairs_t1", "u_cohort"))],
    }


def command(job: Job, est: tuple[int, int], dry: bool) -> list[str]:
    first, whole = est
    cmd = [sys.executable, "scripts/run_bq.py", f"sql/{job.sql}", "--label", f"{CAMPAIGN} {job.label}",
           "--require-prefix", PREFIX, "--campaign", CAMPAIGN, "--campaign-cap", str(CAP_USD),
           "--expect-bytes", str(whole), "--max-dry-bytes", str(int(DRY_RATIO * first))]
    for k, v in job.params.items():
        cmd += ["--param", f"{k}={v}"]
    for k, v in job.subs.items():
        cmd += ["--sub", f"{k}={v}"]
    for k, v in job.renames.items():
        cmd += ["--rename", f"{k}={v}"]
    for name in job.allow:
        cmd += ["--allow-read", name]
    if dry:
        cmd.append("--dry-run")
    return cmd


# --------------------------------------------------------------------------- BigQuery metadata and ledger


def client_and_dataset(cfg: dict):
    from google.cloud import bigquery
    project = cfg["bigquery"]["project_id"]
    return bigquery.Client(project=project), f"{project}.{cfg['bigquery']['dataset']}"


def table_meta(client, ds: str, names) -> dict[str, dict]:
    out = {}
    for name in names:
        t = client.get_table(f"{ds}.{name}")
        tp = t.time_partitioning
        out[name] = {"rows": int(t.num_rows or 0), "bytes": int(t.num_bytes or 0),
                     "partitioning": f"{tp.type_}/{tp.field}" if tp else None,
                     "modified": t.modified.isoformat(timespec="seconds"), "expires": t.expires}
    return out


def list_rows(client, ds: str, table: str) -> list[dict]:
    """A small table through tabledata.list, which is not billed."""
    return [dict(r.items()) for r in client.list_rows(f"{ds}.{table}")]


def ledger_jobs() -> list[dict]:
    return load_json(LEDGER)["jobs"] if LEDGER.exists() else []


def campaign_usd() -> float:
    return sum(j.get("usd", 0.0) for j in ledger_jobs() if j.get("label", "").startswith(CAMPAIGN))


# --------------------------------------------------------------------------- manifest and inputs


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()


def inputs(dry: bool) -> dict:
    """Refuse (or, for a dry run, warn) unless every file in COMMITTED is committed without local changes."""
    bad = [rel for rel in COMMITTED
           if git("status", "--porcelain", "--", rel) or not git("log", "-1", "--format=%H", "--", rel)]
    if bad:
        msg = "not committed without local changes: " + ", ".join(bad)
        if not dry:
            raise SystemExit("refused: " + msg)
        print("warning:", msg)
    return {
        "head": git("rev-parse", "HEAD"),
        "revision_commit": git("log", "--diff-filter=A", "-1", "--format=%H %cI", "--", COMMITTED[0]),
        "sha256": {rel: hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() for rel in COMMITTED},
    }


def manifest() -> dict:
    return load_json(MANIFEST) if MANIFEST.exists() else {"variant": VARIANT, "steps": [], "jobs": [], "results": {}}


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Run:
    """One step: its jobs go through run_bq.py, and the manifest records them."""

    def __init__(self, step: str, cfg: dict, dry: bool):
        self.step, self.cfg, self.dry = step, cfg, dry
        self.client, self.ds = client_and_dataset(cfg)
        self.inputs = inputs(dry)
        self.meta = table_meta(self.client, self.ds, META_TABLES)
        self.est = estimates(Sources({k: v["rows"] for k, v in self.meta.items()}), cfg, calibration())
        self.m = manifest()
        if not dry:
            self.m["steps"].append({"step": step, "started_at": now(), **self.inputs})
            save_json(self.m, MANIFEST)

    def job(self, job: Job) -> None:
        cmd = command(job, self.est[job.key], self.dry)
        print("$", " ".join(cmd[1:]), flush=True)
        subprocess.run(cmd, cwd=ROOT, check=True)
        if self.dry:
            return
        entry = ledger_jobs()[-1]
        if entry.get("label") != f"{CAMPAIGN} {job.label}":
            raise SystemExit("the last ledger entry is not the job just run")
        first, whole = self.est[job.key]
        self.m["jobs"].append({"step": self.step, "key": job.key, "job_id": entry["job_id"], "at": entry["at"],
                               "bytes_dry_run": entry["bytes_estimated"], "bytes_expected": whole,
                               "bytes_first_expected": first, "bytes_billed": entry["bytes_billed"],
                               "usd": entry["usd"]})
        save_json(self.m, MANIFEST)
        if entry["bytes_billed"] > BILL_RATIO * whole:
            raise SystemExit(f"stopped: {job.key} billed {entry['bytes_billed']/1e9:,.1f} GB, more than {BILL_RATIO} "
                             f"times its estimate of {whole/1e9:,.1f} GB; find the cause before the next job")

    def result(self, value) -> None:
        if self.dry:
            return
        self.m["results"][self.step] = value
        self.m["steps"][-1]["finished_at"] = now()
        save_json(self.m, MANIFEST)

    def table_rows(self, name: str) -> int:
        return int(self.client.get_table(f"{self.ds}.{name}").num_rows or 0)


# --------------------------------------------------------------------------- steps


def step_check(cfg: dict, dry: bool) -> None:
    w = windows(cfg)
    client, ds = client_and_dataset(cfg)
    problems = []
    inputs(dry=True)
    d = client.get_dataset(ds)
    if d.default_table_expiration_ms or d.default_partition_expiration_ms:
        problems.append("the dataset has a default expiration")
    names = [t.table_id for t in client.list_tables(ds, max_results=10000)]
    existing = sorted(n for n in names if n.startswith(PREFIX))
    m = manifest()
    if existing and not m["jobs"]:
        problems.append(f"u12_ tables exist before any job of this driver: {existing}")
    meta = table_meta(client, ds, META_TABLES)
    rev = load_json(PROC_SHARED / "revised-usd" / "describe" / "describe.json")
    src = Sources({k: v["rows"] for k, v in meta.items()})
    expected = {
        "u_approvals": sum(src.monthly["u_approvals"].values()),
        "u_transfers": sum(src.monthly["u_transfers"].values()),
        "approvals_ego": sum(src.monthly["approvals_ego"].values()),
        "transfers_ego": sum(src.monthly["transfers_ego"].values()),
        "u_approvals_w1": rev["rows"]["revised_ego"]["approvals_w1"],
        "u_transfers_w1": rev["rows"]["revised_ego"]["transfers_w1"],
        "approvals_w1ego": reg_ego(rev, "approvals_w1"),
        "transfers_w1ego": reg_ego(rev, "transfers_w1"),
        "u_cohort": load_json(PROC_SHARED / "revised-usd" / "cohort" / "matched_cohort.json")["cohort"],
        "u_tokens": 5,
    }
    for name, n in expected.items():
        if meta[name]["rows"] != n:
            problems.append(f"{name} has {meta[name]['rows']:,} rows, the 33-month build {n:,}")
    for name in MONTHLY:
        if meta[name]["partitioning"] != "MONTH/block_timestamp":
            problems.append(f"{name} is not partitioned by month on block_timestamp")
    for name, v in meta.items():  # the 33-month build ended on 10 October 2026
        if v["modified"] > "2026-10-11" or v["expires"]:
            problems.append(f"{name} was modified on {v['modified'][:10]} or expires")
    spent, camp = sum(j.get("usd", 0.0) for j in ledger_jobs()), campaign_usd()
    est = estimates(src, cfg, calibration())
    total = sum(v[1] for v in est.values())
    print(f"windows: T_obs {w['tobs_start']} to {w['tobs_end']}, W0 {w['t1_start']} to {w['t1_end']} (ends exclusive)")
    print(f"ledger: USD {spent:.3f} in {len(ledger_jobs())} jobs; campaign {CAMPAIGN!r} USD {camp:.3f} of {CAP_USD:.2f}")
    print(f"{'job':<12}{'first GB':>10}{'whole GB':>10}{'USD':>8}")
    for k, (first, whole) in est.items():
        print(f"{k:<12}{first/1e9:>10.1f}{whole/1e9:>10.1f}{usd(whole):>8.3f}")
    print(f"{'total':<12}{'':>10}{total/1e9:>10.1f}{usd(total):>8.3f}")
    if camp + usd(total) > CAP_USD:
        problems.append(f"the estimates (USD {usd(total):.2f}) and the campaign so far pass the cap")
    m.setdefault("checks_run", []).append({"at": now(), "problems": problems, "estimates": est,
                                           "ledger_usd": round(spent, 4), "existing_u12": existing})
    save_json(m, MANIFEST)
    if problems:
        raise SystemExit("check failed:\n  " + "\n  ".join(problems))
    print("check passed")


def reg_ego(rev: dict, key: str) -> int:
    return int(rev["rows"]["registered_ego"][key])


def step_tokens(cfg: dict, dry: bool) -> None:
    run = Run("tokens", cfg, dry)
    for job in jobs(cfg)["tokens"]:
        run.job(job)
    if dry:
        return
    import pandas as pd
    rows = pd.DataFrame(list_rows(run.client, run.ds, "u12_token_rows"))
    lst = pd.read_csv(USD_INPUTS / "listed_tokens.csv")
    lst["address"] = lst["address"].str.lower()
    flag = lambda s: s.astype(str).str.lower() == "true"  # noqa: E731
    per = lst[["symbol", "address"]].assign(priced=flag(lst["priced"]), selected=flag(lst["selected"])).merge(
        rows.rename(columns={"token": "address"}), on="address", how="left")
    for col in ("transfers", "latest_allowances", "rows_total"):
        per[col] = per[col].fillna(0).astype(int)
    priced = per[per["priced"]].sort_values("rows_total", ascending=False).reset_index(drop=True)
    priced["rank_by_rows"] = range(1, len(priced) + 1)
    per = per.merge(priced[["address", "rank_by_rows"]], on="address", how="left")
    records = [{"symbol": r["symbol"], "address": r["address"], "priced": bool(r["priced"]),
                "selected": bool(r["selected"]), "transfers": int(r["transfers"]),
                "latest_allowances": int(r["latest_allowances"]), "rows_total": int(r["rows_total"]),
                "rank_by_rows": None if pd.isna(r["rank_by_rows"]) else int(r["rank_by_rows"])}
               for r in per.sort_values("rows_total", ascending=False).to_dict(orient="records")]
    top = priced.head(int(per["selected"].sum()))
    out = {
        "computed_at": now(),
        "source": "sql/20_usd12m_token_rows.sql (contract_rep.u12_token_rows)",
        "window": [cfg["period"]["start_ts"], cfg["period"]["end_ts"]],
        "anchor": cfg["period"]["observation_end"],
        "rule": "rows = ego transfers of the registered cohort in the T_obs score window plus positive latest "
                "allowances at T_obs set inside it (the count of docs/revision_price_weighting.md section 3); "
                "reported only, the five selected tokens are kept (docs/revision_one_year_window.md section 4)",
        "selected": per.loc[per["selected"], "symbol"].tolist(),
        "top_priced_by_rows": top["symbol"].tolist(),
        "same_as_selected": bool(set(top["symbol"]) == set(per.loc[per["selected"], "symbol"])),
        "tokens_in_window": int(len(rows)),
        "rows_in_window": int(rows["rows_total"].astype(int).sum()),
        "per_listed_token": records,
    }
    save_json(out, TOKEN_ROWS)
    print("top priced tokens by twelve-month rows:", out["top_priced_by_rows"], "same as the five:", out["same_as_selected"])
    run.result({k: out[k] for k in ("selected", "top_priced_by_rows", "same_as_selected", "tokens_in_window")})


def step_cohorts(cfg: dict, dry: bool) -> None:
    run = Run("cohorts", cfg, dry)
    for job in jobs(cfg)["cohorts"]:
        run.job(job)
    if dry:
        return
    sizes = {tag: run.table_rows(f"u12_cohort_{tag}") for tag in ("tobs", "t1")}
    ceiling = run.meta["u_cohort"]["rows"]
    for tag, n in sizes.items():
        if not COHORT_FLOOR[tag] <= n <= ceiling:
            raise SystemExit(f"the {tag} cohort has {n:,} contracts, outside [{COHORT_FLOOR[tag]:,}, {ceiling:,}]")
    print("cohorts:", sizes)
    run.result(sizes)


def step_constants(cfg: dict, dry: bool) -> None:
    run = Run("constants", cfg, dry)
    for job in jobs(cfg)["constants"]:
        run.job(job)
    if dry:
        return
    row = {k: float(v) for k, v in list_rows(run.client, run.ds, "u12_constants")[0].items()}
    m_t, m_a, cap = round_sig(row["m_transfer"]), round_sig(row["m_allowance"]), round_sig(row["p99_transfer"])
    if not all(math.isfinite(x) and x > 0 for x in (m_t, m_a, cap)):
        raise SystemExit(f"constants not positive and finite: {row}")
    out = {
        "computed_at": now(),
        "source": "sql/13_usd_constants.sql on the W0 views of sql/21_usd12m_cohorts.sql (contract_rep.u12_constants): "
                  f"events of the W0 cohort from {cfg['holdout']['start_ts']} to t1",
        "raw": row,
        "m_transfer_usd": m_t, "m_allowance_usd": m_a, "cap_allowance_usd": cap,
        "b_transfer": slope_for_median(m_t), "b_allowance": slope_for_median(m_a),
        "unlimited_base_units": UNLIMITED_BASE_UNITS,
        "rule": "b = ln 3 / m with m the median rounded to two significant digits; the allowance cap U is the "
                "99th percentile of the USD values of the transfers of the W0 score window, rounded to two "
                "significant digits",
    }
    save_json(out, USD_CONSTANTS)
    print(json.dumps(out, indent=1))
    run.result({k: out[k] for k in ("m_transfer_usd", "m_allowance_usd", "cap_allowance_usd")})


def step_pairs(cfg: dict, dry: bool) -> None:
    run = Run("pairs", cfg, dry)
    for job in jobs(cfg, None if dry else constants())["pairs"]:
        run.job(job)
    if dry:
        return
    sizes = {k: run.table_rows(f"u12_{k}") for k in PAIR_CEILING}
    for k, n in sizes.items():
        if n > PAIR_CEILING[k]:
            raise SystemExit(f"u12_{k} has {n:,} rows, more than the {PAIR_CEILING[k]:,} pairs of the window")
    print("pairs:", sizes)
    run.result(sizes)


def step_rest(cfg: dict, dry: bool) -> None:
    run = Run("rest", cfg, dry)
    for job in jobs(cfg, None if dry else constants())["rest"]:
        run.job(job)
    if dry:
        return
    run.result({k: run.table_rows(f"u12_{k}") for k in ("proxies_tobs", "labels_w0", "labels_w1", "nodes")})


def step_checks(cfg: dict, dry: bool) -> None:
    run = Run("checks", cfg, dry)
    for job in jobs(cfg)["checks"]:
        run.job(job)
    if dry:
        return
    checks = {r["check_name"]: int(r["violations"]) for r in list_rows(run.client, run.ds, "u12_checks")}
    run.result(checks)
    print("checks:", checks)
    if len(checks) != 6 or any(checks.values()):
        raise SystemExit("an invariant of sql/23 does not hold")


DOWNLOADS = (("u12_cohort_tobs", "cohort"), ("u12_cohort_t1", "cohort_t1"), ("u12_x_nodes", "nodes"),
             ("u12_x_allow_pairs_tobs", "allow_pairs_tobs"), ("u12_x_transfer_pairs_tobs", "transfer_pairs_tobs"),
             ("u12_x_allow_pairs_t1", "allow_pairs_t1"), ("u12_x_transfer_pairs_t1", "transfer_pairs_t1"),
             ("u12_proxies_tobs", "proxies_tobs"), ("u12_labels_w0", "labels_w0"), ("u12_labels_w1", "labels_w1"))


def cohort_summary(cfg: dict) -> dict:
    """The cohort of each freeze against the registered cohort: cohort/matched_cohort (T_obs, the matched
    cohort of the same-window evaluation) and cohort/cohort_t1 (W0) of the twelve-month analysis."""
    w = windows(cfg)
    hexed = lambda col: col.map(lambda b: "0x" + bytes(b).hex())  # noqa: E731
    reg = set(read_parts(PROC_SHARED / "cohort" / "matched_cohort")["wallet"])
    usd33 = set(hexed(read_parts(RAW / "graph-tables-usd" / "cohort")["address"]))
    sets, out = {}, {}
    for tag, stem, start, end in (("tobs", "cohort", w["tobs_start"], w["tobs_end"]),
                                  ("t1", "cohort_t1", w["t1_start"], w["t1_end"])):
        u = read_parts(GRAPH / stem)
        u["wallet"] = hexed(u["address"])
        s = set(u["wallet"])
        if not s <= usd33 or not s <= reg:
            raise SystemExit(f"the {tag} cohort is not a subset of the 33-month and registered cohorts")
        sets[tag] = s
        name = "matched_cohort" if tag == "tobs" else "cohort_t1"
        write_parts(u[["wallet", "owners_nonzero", "approval_logs"]].sort_values("wallet").reset_index(drop=True),
                    PROC / "cohort" / name)
        out[tag] = {
            "rule": f"contracts of the registered cohort with non-zero approvals of a selected token (WETH, USDC, "
                    f"USDT0, ARB, WBTC) from >= {cfg['cohort']['min_owners']} distinct owners, {start} to {end} "
                    "(end exclusive)",
            "registered_cohort": len(reg), "cohort": len(s), "left_out_of_registered": len(reg - s),
            "source": f"contract_rep.u12_cohort_{tag} (sql/21_usd12m_cohorts.sql)",
        }
    out["t1"]["in_tobs_cohort"] = len(sets["t1"] & sets["tobs"])
    save_json(out["tobs"], PROC / "cohort" / "matched_cohort.json")
    save_json(out["t1"], PROC / "cohort" / "cohort_t1.json")
    print(f"cohorts: T_obs {len(sets['tobs']):,}, W0 {len(sets['t1']):,} ({out['t1']['in_tobs_cohort']:,} in both)")
    return {tag: v["cohort"] for tag, v in out.items()}


def step_download(cfg: dict, dry: bool) -> None:
    run = Run("download", cfg, dry)
    for table, stem in DOWNLOADS:
        cmd = [sys.executable, "scripts/download_table.py", f"contract_rep.{table}", str(GRAPH / stem)]
        print("$", " ".join(cmd[1:]), flush=True)
        if not dry:
            subprocess.run(cmd, cwd=ROOT, check=True)
    if not dry:
        run.result(cohort_summary(cfg))


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
