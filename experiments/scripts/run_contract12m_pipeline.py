#!/usr/bin/env python3
"""BigQuery and RPC steps of the contract-graph revision (docs/revision_contract_graph.md), in order.

Every query goes through scripts/run_bq.py with the checks of this variant: a job creates only c12_* tables,
reads only the project tables and public views named here, is labelled "contract12m: ..." and is refused if the
jobs of the campaign would pass the cap of the overlay (USD 14) or the ledger the budget of the variant (USD 60).
Each job carries an estimate of the bytes it bills, for its first statement and for the whole job, since the dry
run of a file with several statements counts only the first: the dry runs of 7 November 2026 for the parts that
read the public views, logs_obs and logs_w1, plus the rows of every project table it reads (table metadata)
times the billed widths of the columns read (at least 10 MB per table). A job whose first statement dry-runs
above 1.25 times its estimate is refused, and after a job that billed more than 1.5 times its estimate the
driver stops. An estimate that needs a table that does not exist yet is computed when its step runs. Gate A:

  check      free checks: the windows of the configuration against the revision, no expiration on the
             dataset, the source tables and the public views with the columns the jobs read, the five token
             literals of sql/32 against u_tokens, no c12_* table before the first job of the manifest, the
             ledger and the campaign; prints the estimate of every job whose inputs exist and the jobs that
             wait for an earlier one, and fails if the known estimates would pass the cap. It is recorded in
             the run manifest only once the files in COMMITTED are committed; before that it writes nothing
  subset     job 24: the five-token events of the typing window (c12_logs5)
  ends       job 25: their pairs and the ends E (c12_pairs5, c12_ends)
  activity   jobs 26 to 28: the transaction senders, decoded-log emitters and created contracts among E
  queue      job 29: the RPC queue K (c12_rpc_queue)
  typing     local: downloads the queue to contract-types/c12_rpc_queue and reads the account types with
             scripts/check_account_code.py at the pinned block (contract-types/c12_account_types); stops
             unless its JSON records a complete run. A run again resumes the output on disk only if the
             script, its rules and the queue are those it was written with (check_account_code.py refuses
             otherwise, and the output must be moved away to be read afresh)
  load       job 30: loads the complete account types into c12_account_types (a load job, not billed)
  contracts  job 31: the node set, the typed user accounts and the events between contracts
  balances   jobs 32 and 33: the net flow before 2023-10-01 and the balances at t1, T_obs and 2026-09-30
  anchors    job 34: the last block at or before each anchor
  audit      job 43, then the balanceOf check of scripts/balance_audit.py
  structure  job 35, then the structure pilot (scripts/run_discovery.py --window t1 --feasibility); the
             capped allowance edges are counted as the pilot counts them, distinct pairs without self-pairs

The gate B steps (constants, pairs, rest, checks, download) are not yet written and refuse to run. Every step
but check refuses to run unless the files in COMMITTED are committed without local changes (a --dry-run only
warns). data/2-.../revised-contract-12m/run_manifest.json records the commit, the hashes of those files, every
job and the results of every step.

The steps run in this order. Each step from subset on refuses to run unless the last check found no problem
and every step before it has a last run that passed, the last runs in this order: a step run again makes the
steps after it wait until they are run again (a check run again only by what it finds). A step passes when its jobs succeed, and anchors, audit
and structure only when their checks hold (the typing block after 30 September; the balance check; a pilot whose
record names every file of PILOT_COMMITTED as committed, without a stop), so that a balance check below its
threshold stops the run until the cause is understood, and one that gave no result (no endpoint gave the T_obs or the
latest block) is run again (revision section 6). A step records only the balance_audit.json or feasibility_t1.json that its own run wrote.
--author-decision TEXT lets a step go on all the same; its run in the manifest records the text and what was
missing. A --dry-run only warns.

Usage: python scripts/run_contract12m_pipeline.py STEP [STEP ...] [--dry-run] [--author-decision TEXT]
"""

from __future__ import annotations

import argparse
import hashlib
import math
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

os.environ.setdefault("CONTRACT_REP_VARIANT", "contract12m")
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (GRAPH, PROC, ROOT, TYPES, TYPES_DIR, VARIANT, load_config, load_json, part_paths,  # noqa: E402
                    read_parts, save_json)

# The c12_ tables, folders and constants belong to this variant; any other would mix them up.
if VARIANT != "contract12m":
    raise SystemExit("run_contract12m_pipeline.py belongs to the contract-graph variant "
                     "(CONTRACT_REP_VARIANT=contract12m)")

STEPS = ("check", "subset", "ends", "activity", "queue", "typing", "load", "contracts", "balances", "anchors",
         "audit", "structure", "constants", "pairs", "rest", "checks", "download")
GATE_B = {"constants": "job 36", "pairs": "job 37", "rest": "jobs 38 to 41", "checks": "job 42",
          "download": "the downloads of the gate B tables"}
# The gate A steps after check, each of which runs only after the ones before it have passed, in this order.
CHAIN = STEPS[1:STEPS.index("structure") + 1]
# The text of --author-decision: a step goes on although the steps before it did not all pass (main() sets it).
AUTHOR_DECISION: str | None = None
PREFIX, CAMPAIGN = "c12_", "contract12m:"
CAP_USD = float(load_config()["contract_graph"]["campaign_cap_usd"])
DRY_RATIO, BILL_RATIO = 1.25, 1.5
LEDGER = ROOT / "data" / "bq_ledger.json"
MANIFEST = PROC / "run_manifest.json"
QUEUE = TYPES_DIR / "c12_rpc_queue"
BAL_AUDIT, ANCHOR_BLOCKS, STRUCT_T1 = GRAPH / "bal_audit", GRAPH / "anchor_blocks", GRAPH / "struct_t1"
BALANCE_AUDIT = PROC / "typing" / "balance_audit.json"
FEASIBILITY = PROC / "discovery" / "feasibility_t1.json"

SQL_FILES = ("24_c12_logs5.sql", "25_c12_ends.sql", "26_c12_tx_senders.sql", "27_c12_emitters.sql",
             "28_c12_creations.sql", "29_c12_rpc_queue.sql", "31_c12_contracts.sql", "32_c12_bal_pre.sql",
             "33_c12_bal.sql", "34_c12_anchor_blocks.sql", "35_c12_structure.sql", "43_c12_bal_audit.sql")
# The first file is the revision: the commit that added it is the reference point of the revision (gate A). The
# files are those of revision section 12: the documents and configurations, the scripts and the gate A SQL files.
COMMITTED = ("docs/revision_contract_graph.md", "docs/discovery_protocol.md", "config/overlay_contract12m.yaml",
             "config/contract_reputation.yaml", "scripts/run_contract12m_pipeline.py", "scripts/run_bq.py",
             "scripts/common.py", "scripts/check_account_code.py", "scripts/balance_audit.py",
             "scripts/download_table.py", "scripts/crawl.py", "scripts/run_discovery.py", "scripts/scoring.py",
             "scripts/stats.py", "scripts/graphs.py", *(f"sql/{f}" for f in SQL_FILES))
# The files whose state the structure pilot records (run_discovery.COMMITTED, protocol section 8), all of them in
# COMMITTED: the structure step passes only when the pilot's record names each of them as committed.
PILOT_COMMITTED = ("docs/discovery_protocol.md", "docs/revision_contract_graph.md", "config/overlay_contract12m.yaml",
                   "scripts/crawl.py", "scripts/run_discovery.py", "scripts/scoring.py", "scripts/stats.py",
                   "scripts/graphs.py", "scripts/common.py", "config/contract_reputation.yaml")

# The public views the jobs may read (always named in full), and the columns each job reads from them.
PUBLIC = "bigquery-public-data.goog_blockchain_arbitrum_one_us"
VIEWS = {name: f"{PUBLIC}.{name}" for name in ("transactions", "receipts", "decoded_events", "blocks", "logs")}
VIEW_COLUMNS = {"transactions": ("from_address", "block_timestamp"),
                "receipts": ("contract_address", "block_timestamp"),
                "decoded_events": ("address", "event_signature", "block_timestamp"),
                "blocks": ("block_number", "block_timestamp"),
                "logs": ("address", "topics", "data", "block_timestamp")}
# Project tables of the earlier builds that the jobs read; they must exist, and must not have changed since
# the revision was written.
SOURCES = ("logs_obs", "logs_w1", "u_tokens", "u_prices", "u12_cohort_tobs", "u12_cohort_t1", "u12_labels_w0",
           "u12_labels_w1")
SOURCES_BEFORE = "2026-11-07"

# The windows of docs/revision_contract_graph.md section 3 (ends exclusive) and its anchors (inclusive); the
# configuration with the overlay must give exactly these. obs_start and mid are where logs_obs begins and where
# it hands over to logs_w1.
WINDOWS = {
    "typing_start": "2025-04-01 00:00:00 UTC", "typing_end": "2026-10-01 00:00:00 UTC",
    "tobs_start": "2025-07-01 00:00:00 UTC", "tobs_end": "2026-07-01 00:00:00 UTC",
    "t1_start": "2025-04-01 00:00:00 UTC", "t1_end": "2026-04-01 00:00:00 UTC",
    "w0_end": "2026-07-01 00:00:00 UTC", "w1_end": "2026-10-01 00:00:00 UTC",
    "obs_start": "2023-10-01 00:00:00 UTC", "mid": "2026-07-01 00:00:00 UTC",
}
ANCHORS = {"t1": "2026-03-31 23:59:59 UTC", "tobs": "2026-06-30 23:59:59 UTC", "end_0930": "2026-09-30 23:59:59 UTC"}

# Byte widths that BigQuery bills: a 20-byte address (2 + 20), a one-character STRING (2 + 1), a 0x hex address
# STRING (2 + 42), a timestamp, integer, float or date, and an account class (at most 'smart_account', 2 + 13).
A, KIND, HEX, NUM, CLASS = 22, 3, 44, 8, 15
LOGS5_ALL = 3 * A + KIND + 6 * NUM  # every column of c12_logs5
MIN_TABLE = 10 * 2**20  # at least 10 MB is billed for every table a query reads
USD_PER_TIB = 6.25


@dataclass(frozen=True)
class Measured:
    """Bytes of a free dry run of 7 November 2026, and the tables or views whose columns it counted."""
    bytes: int
    covers: tuple[str, ...]


@dataclass(frozen=True)
class Read:
    """A project table read by a statement: its rows (table metadata) times the bytes of the columns read."""
    table: str
    width: int


# Dry runs of 7 November 2026 with the parameters of jobs() (upper bounds: a dry run does not skip the blocks that
# clustering prunes). The public tables are views; jobs 26 to 28 were dry-run with c12_ends, which does not exist
# yet, renamed to u12_cohort_tobs (an address column of 142,626 bytes, subtracted here), and job 32 as its CTE over
# the public logs alone. The logs_obs part of job 33 is not re-measured (the job reads c12_ tables): it is the dry
# run of the revision's cost check of the same day, 140.09 GB with emitter, a, b, val and block_timestamp, raised
# by the kind column that the job also reads (3 bytes per row of 108).
DRY_24 = Measured(226_193_664_203, ("logs_obs", "logs_w1", "u_tokens", "u_prices"))
DRY_26 = Measured(149_373_374_072, (VIEWS["transactions"],))
DRY_27 = Measured(260_741_041_900, (VIEWS["decoded_events"],))
DRY_28 = Measured(23_034_321_352, (VIEWS["receipts"],))
DRY_32 = Measured(547_023_844_600, (VIEWS["logs"],))
DRY_33 = Measured(140_090_000_000 * (108 + KIND) // 108, ("logs_obs",))
DRY_34 = Measured(33_562_960, (VIEWS["blocks"],))

# The statements of every query job in order, each with what it reads. BigQuery bills a table read several times
# in one statement once, for the union of its columns.
READS: dict[str, list[list[Measured | Read]]] = {
    "logs5": [[DRY_24]],
    # c12_pairs5 from a, b, kind and block_timestamp; c12_ends from a, b and the two counts of c12_pairs5
    "ends": [[Read("c12_logs5", 2 * A + KIND + NUM)], [Read("c12_pairs5", 2 * A + 2 * NUM)]],
    "tx_senders": [[DRY_26, Read("c12_ends", A)]],
    "emitters": [[DRY_27, Read("c12_ends", A)]],
    "creations": [[DRY_28, Read("c12_ends", A)]],
    "rpc_queue": [[Read("c12_ends", A), Read("c12_tx_senders", A), Read("c12_pairs5", 2 * A),
                   Read("u12_cohort_tobs", A), Read("u12_cohort_t1", A), Read("u12_labels_w0", HEX),
                   Read("u12_labels_w1", HEX), Read("c12_emitters", A), Read("c12_creations", A)]],
    # address and account_class of the types and the senders, twice; then every column of c12_logs5
    "contracts": [[Read("c12_account_types", HEX + CLASS), Read("c12_tx_senders", A)],
                  [Read("c12_account_types", HEX + CLASS), Read("c12_tx_senders", A)],
                  [Read("c12_logs5", LOGS5_ALL), Read("c12_contracts", A)]],
    # the population: token, a, kind and block_timestamp of c12_logs5
    "bal_pre": [[DRY_32, Read("c12_logs5", 2 * A + KIND + NUM)]],
    # c12_logs5: kind, token, a, b, value, block_timestamp; c12_bal_pre: token, address, net, n
    "bal": [[DRY_33, Read("u_tokens", A), Read("c12_logs5", 3 * A + KIND + 2 * NUM),
             Read("c12_bal_pre", 2 * A + 2 * NUM)]],
    "anchor_blocks": [[DRY_34]],
    # c12_bal: token, address, bal_tobs, bal_0930, n_w1; u_tokens: token, decimals
    "bal_audit": [[Read("c12_bal", 2 * A + 3 * NUM), Read("u_tokens", A + NUM)]],
    # c12_events_cc: kind, token, a, b, value, block_number, log_index, block_timestamp, usd; c12_bal: token,
    # address, bal_t1; u_prices: token, day, price_usd
    "structure": [[Read("c12_events_cc", 3 * A + KIND + 5 * NUM), Read("c12_bal", 2 * A + NUM),
                   Read("u_tokens", A + NUM), Read("u_prices", A + 2 * NUM)]],
}
# A table that one statement creates and a later statement of the same job reads is bounded by the table it is
# made from: c12_pairs5 has at most one row per row of c12_logs5, c12_contracts one per typed address.
BOUND = {"ends": {"c12_pairs5": "c12_logs5"}, "contracts": {"c12_contracts": "c12_account_types"}}
ESTIMATE_TABLES = tuple(sorted({t.table for sts in READS.values() for st in sts for t in st if isinstance(t, Read)}))


# --------------------------------------------------------------------------- windows and jobs


def _ts(s: str) -> datetime:
    return datetime.fromisoformat(str(s).replace(" UTC", ""))


def windows(cfg: dict) -> dict:
    """The windows and anchors of the configuration, checked against docs/revision_contract_graph.md section 3."""
    p, h, r, bq, g = cfg["period"], cfg["holdout"], cfg["registered_window"], cfg["bigquery"], cfg["contract_graph"]
    w = {"typing_start": g["typing_start"], "typing_end": g["typing_end"],
         "tobs_start": p["start_ts"], "tobs_end": p["end_ts"], "t1_start": h["start_ts"], "t1_end": h["outcome_start"],
         "w0_end": p["end_ts"], "w1_end": bq["scan_b"]["end_ts"],
         "obs_start": bq["scan_a"]["start_ts"], "mid": bq["scan_b"]["start_ts"]}
    a = {"t1": h["score_end"], "tobs": p["observation_end"], "end_0930": r["outcome_end"]}
    if w != WINDOWS or a != ANCHORS:
        raise SystemExit(f"the configuration gives the windows {w} and anchors {a}, not those of the revision")
    one = timedelta(seconds=1)
    for anchor, end in ((a["t1"], w["t1_end"]), (a["tobs"], w["tobs_end"]), (a["end_0930"], w["typing_end"]),
                        (h["outcome_end"], w["w0_end"]), (r["score_end"], w["tobs_end"])):
        if _ts(anchor) + one != _ts(end):
            raise SystemExit(f"{anchor} is not the last second before {end}")
    if bq["scan_a"]["end_ts"] != w["mid"] or r["outcome_start"] != w["mid"]:
        raise SystemExit("logs_obs does not end where logs_w1 and the W1 label window begin")
    return {**w, **a}


def system_range(top: int) -> tuple[str, str]:
    """The system addresses 0x...01 to 0x...<top> (section 4.1) as 0x hex bounds of a BYTES range."""
    if not 1 <= int(top) <= 255:
        raise SystemExit(f"contract_graph.system_address_max must be from 1 to 255, not {top}")
    return "0x" + "00" * 19 + "01", "0x" + "00" * 19 + f"{int(top):02x}"


def dust_digits(dust_token: float) -> int:
    """k with 10^-k tokens the dust threshold (balance.dust_token = 1e-6 gives 6), so that SQL compares exactly."""
    k = round(-math.log10(float(dust_token)))
    if not math.isclose(10.0 ** -k, float(dust_token), rel_tol=1e-9):
        raise SystemExit(f"contract_graph.balance.dust_token must be a power of ten, not {dust_token}")
    return k


@dataclass
class Job:
    key: str
    no: int
    sql: str
    label: str
    params: dict = field(default_factory=dict)
    subs: dict = field(default_factory=dict)
    allow: tuple = ()   # project tables outside c12_ that the job may read
    public: tuple = ()  # public views, named in full, that the job may read


def jobs(cfg: dict) -> dict[str, list[Job]]:
    """The query jobs of every gate A step."""
    w, g = windows(cfg), cfg["contract_graph"]
    first, last = system_range(g["system_address_max"])
    dust = str(dust_digits(g["balance"]["dust_token"]))
    population = {"start_ts": w["typing_start"], "tobs_end": w["tobs_end"]}
    return {
        "subset": [Job("logs5", 24, "24_c12_logs5.sql", "five-token events of the typing window",
                       params={"start_ts": w["typing_start"], "mid_ts": w["mid"], "end_ts": w["typing_end"]},
                       allow=("logs_obs", "logs_w1", "u_tokens", "u_prices"))],
        "ends": [Job("ends", 25, "25_c12_ends.sql", "pairs and ends of the five-token events")],
        "activity": [
            Job("tx_senders", 26, "26_c12_tx_senders.sql", "transaction senders among the ends",
                params={"end_ts": w["typing_end"]}, public=(VIEWS["transactions"],)),
            Job("emitters", 27, "27_c12_emitters.sql", "decoded-log emitters among the ends",
                params={"start_ts": w["typing_start"], "end_ts": w["typing_end"]}, public=(VIEWS["decoded_events"],)),
            Job("creations", 28, "28_c12_creations.sql", "contracts created by a transaction among the ends",
                params={"end_ts": w["typing_end"]}, public=(VIEWS["receipts"],)),
        ],
        "queue": [Job("rpc_queue", 29, "29_c12_rpc_queue.sql", "RPC queue",
                      params={"sender_salt": g["audit"]["sender_salt"], "untyped_salt": g["audit"]["untyped_salt"]},
                      subs={"AUDIT_SENDERS": str(int(g["audit"]["senders"])),
                            "AUDIT_UNTYPED": str(int(g["audit"]["untyped"]))},
                      allow=("u12_cohort_tobs", "u12_cohort_t1", "u12_labels_w0", "u12_labels_w1"))],
        "contracts": [Job("contracts", 31, "31_c12_contracts.sql",
                          "contracts, user accounts and events between contracts",
                          params={"system_first": first, "system_last": last})],
        "balances": [
            Job("bal_pre", 32, "32_c12_bal_pre.sql", "net flow before 2023-10-01 of the balance population",
                params={"obs_start": w["obs_start"], **population}, public=(VIEWS["logs"],)),
            Job("bal", 33, "33_c12_bal.sql", "balances at t1, T_obs and 2026-09-30",
                params={"obs_start": w["obs_start"], **population, "t1": w["t1"], "tobs": w["tobs"],
                        "end_0930": w["end_0930"], "mid_ts": w["mid"], "end_ts": w["typing_end"]},
                allow=("logs_obs", "u_tokens")),
        ],
        "anchors": [Job("anchor_blocks", 34, "34_c12_anchor_blocks.sql", "last block at or before each anchor",
                        params={"t1": w["t1"], "tobs": w["tobs"], "end_0930": w["end_0930"]},
                        public=(VIEWS["blocks"],))],
        "audit": [Job("bal_audit", 43, "43_c12_bal_audit.sql", "sample of the balance check",
                      params={"audit_salt": g["balance"]["audit_salt"],
                              "per_cell": str(int(g["balance"]["audit_per_cell"])), "dust_digits": dust},
                      allow=("u_tokens",))],
        "structure": [Job("structure", 35, "35_c12_structure.sql", "structure of the contract graph at t1",
                          params={"start_ts": w["t1_start"], "t1": w["t1"], "dust_digits": dust},
                          allow=("u_tokens", "u_prices"))],
    }


def all_jobs(cfg: dict) -> list[Job]:
    return [j for js in jobs(cfg).values() for j in js]


def sql_text(job: Job) -> str:
    """The SQL of a job after its text substitutions, as run_bq.py sends it."""
    sql = (ROOT / "sql" / job.sql).read_text(encoding="utf-8")
    for k, v in job.subs.items():
        sql = sql.replace(f"__{k}__", v)
    return sql


def tables_of(job: Job, cfg: dict) -> tuple[set[str], set[str]]:
    """The project tables a job creates and the ones it reads without creating them."""
    project, dataset = cfg["bigquery"]["project_id"], cfg["bigquery"]["dataset"]
    ds = rf"`{re.escape(project)}\.{re.escape(dataset)}\.(\w+)`"
    body = re.sub(r"--[^\n]*", "", sql_text(job))
    created = set(re.findall(rf"CREATE\s+(?:OR\s+REPLACE\s+)?(?:TABLE|VIEW)\s+{ds}", body, flags=re.I))
    return created, set(re.findall(ds, body)) - created


def creators(cfg: dict) -> dict[str, str]:
    """The job that creates each c12_ table."""
    out = {f"{PREFIX}account_types": "account_types (job 30)"}
    for job in all_jobs(cfg):
        for t in tables_of(job, cfg)[0]:
            out[t] = f"{job.key} (job {job.no})"
    return out


# --------------------------------------------------------------------------- estimates


@dataclass(frozen=True)
class Estimate:
    first: int                       # billed bytes of the first statement
    whole: int                       # billed bytes of the whole job
    missing: tuple[str, ...] = ()    # tables that do not exist yet; first and whole then hold the known part only


def estimates(rows: dict[str, int | None]) -> dict[str, Estimate]:
    """The estimate of every query job from the rows of the project tables it reads (None or absent: the table
    does not exist yet)."""
    out = {}
    for key, statements in READS.items():
        bound, missing, totals = BOUND.get(key, {}), set(), []
        for statement in statements:
            total = 0
            for term in statement:
                if isinstance(term, Measured):
                    total += term.bytes
                    continue
                table = term.table
                if rows.get(table) is None and table in bound:
                    table = bound[table]
                if rows.get(table) is None:
                    missing.add(table)
                else:
                    total += max(MIN_TABLE, int(rows[table]) * term.width)
            totals.append(total)
        out[key] = Estimate(totals[0], sum(totals), tuple(sorted(missing)))
    return out


def usd(nbytes: float) -> float:
    return nbytes / 2**40 * USD_PER_TIB


def cap_problems(est: dict[str, Estimate], campaign: float, spent: float, budget: float,
                 done: set[str] = frozenset()) -> list[str]:
    """The known estimates of the jobs not yet run (whole jobs, and the known part of those that wait for a
    table) against the campaign cap and the budget of the variant."""
    total = usd(sum(e.whole for k, e in est.items() if k not in done))
    out = []
    if campaign + total > CAP_USD:
        out.append(f"the campaign so far (USD {campaign:.2f}) and the known estimates (USD {total:.2f}) pass the cap "
                   f"of USD {CAP_USD:.2f}")
    if spent + total > budget:
        out.append(f"the ledger (USD {spent:.2f}) and the known estimates (USD {total:.2f}) pass the budget of USD "
                   f"{budget:.2f}")
    return out


def command(job: Job, est: Estimate, dry: bool) -> list[str]:
    cmd = [sys.executable, "scripts/run_bq.py", f"sql/{job.sql}", "--label", f"{CAMPAIGN} {job.label}",
           "--require-prefix", PREFIX, "--campaign", CAMPAIGN, "--campaign-cap", str(CAP_USD),
           "--expect-bytes", str(est.whole), "--max-dry-bytes", str(int(DRY_RATIO * est.first))]
    for k, v in job.params.items():
        cmd += ["--param", f"{k}={v}"]
    for k, v in job.subs.items():
        cmd += ["--sub", f"{k}={v}"]
    for name in job.allow:
        cmd += ["--allow-read", name]
    for name in job.public:
        cmd += ["--allow-public", name]
    if dry:
        cmd.append("--dry-run")
    return cmd


# --------------------------------------------------------------------------- BigQuery metadata and ledger


def client_and_dataset(cfg: dict):
    from google.cloud import bigquery
    project = cfg["bigquery"]["project_id"]
    return bigquery.Client(project=project), f"{project}.{cfg['bigquery']['dataset']}"


def table_meta(client, ds: str, names) -> dict[str, dict | None]:
    """Free metadata of each table; None for a table that does not exist."""
    from google.api_core.exceptions import NotFound
    out = {}
    for name in names:
        try:
            t = client.get_table(f"{ds}.{name}" if "." not in name else name)
        except NotFound:
            out[name] = None
            continue
        tp = t.time_partitioning
        out[name] = {"rows": int(t.num_rows or 0), "bytes": int(t.num_bytes or 0),
                     "partitioning": f"{tp.type_}/{tp.field}" if tp else None,
                     "modified": t.modified.isoformat(timespec="seconds"), "expires": t.expires,
                     "schema": {f.name: f.field_type for f in t.schema}}
    return out


def table_rows(client, ds: str, names) -> dict[str, int | None]:
    return {k: (v["rows"] if v else None) for k, v in table_meta(client, ds, names).items()}


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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def uncommitted() -> list[str]:
    """The files in COMMITTED that are missing, have local changes or were never committed."""
    return [rel for rel in COMMITTED
            if not (ROOT / rel).exists() or git("status", "--porcelain", "--", rel)
            or not git("log", "-1", "--format=%H", "--", rel)]


def inputs(dry: bool) -> dict:
    """Refuse (or, for a dry run, warn) unless every file in COMMITTED is committed without local changes."""
    bad = uncommitted()
    if bad:
        msg = "not committed without local changes: " + ", ".join(bad)
        if not dry:
            raise SystemExit("refused: " + msg)
        print("warning:", msg)
    return {
        "head": git("rev-parse", "HEAD"),
        "revision_commit": git("log", "--diff-filter=A", "-1", "--format=%H %cI", "--", COMMITTED[0]),
        "sha256": {rel: sha256(ROOT / rel) if (ROOT / rel).exists() else None for rel in COMMITTED},
    }


def manifest() -> dict:
    return load_json(MANIFEST) if MANIFEST.exists() else {"variant": VARIANT, "steps": [], "jobs": [], "results": {}}


def prerequisites(step: str, m: dict) -> list[str]:
    """What ``step`` still waits for in the manifest ``m`` (nothing: it may run). Every step of CHAIN needs a last
    check without problems (check is the first step of gate A, revision section 12) and a last run that passed of
    each step of CHAIN before it, those last runs in the order of CHAIN (a step run again after a later step makes
    the later one stale). Of the checks only the outcome of the last one counts, not when it ran: a check run again
    does not make subset or the steps after it stale."""
    if step not in CHAIN:
        return []
    out = []
    checks = m.get("checks_run") or []
    if not checks or checks[-1].get("problems"):
        out.append("a check without problems" + (" (the last one found some)" if checks else ""))
    last = {entry["step"]: (i, entry) for i, entry in enumerate(m["steps"])}
    before, at = None, -1
    for s in CHAIN[:CHAIN.index(step)]:
        if s not in last:
            out.append(f"a run of {s}")
            continue
        i, entry = last[s]
        if entry.get("passed") is not True:
            out.append(f"a run of {s} that passes (the last one did not)")
        elif i < at:
            out.append(f"a run of {s} after the last run of {before}")
        if i > at:
            before, at = s, i
    return out


def stamp(path: Path) -> tuple[int, str] | None:
    """The modification time (ns) and the SHA-256 of a file, or None if it does not exist."""
    return (path.stat().st_mtime_ns, sha256(path)) if path.exists() else None


def written(path: Path, before: tuple[int, str] | None) -> bool:
    """Whether a local script wrote ``path`` since its stamp() was ``before``: an earlier file is never taken as the
    result of a run that failed before writing one."""
    after = stamp(path)
    return after is not None and after != before


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sh(cmd: list[str]) -> None:
    """Run a local command from the experiments folder; stop if it fails."""
    rc = subprocess.run(cmd, cwd=ROOT).returncode
    if rc != 0:
        raise SystemExit(f"stopped: {Path(cmd[1]).name} exited with {rc}")


def download(table: str, stem: Path) -> list[str]:
    return [sys.executable, "scripts/download_table.py", f"contract_rep.{table}", str(stem)]


class Run:
    """One step: its jobs go through run_bq.py, and the manifest records them. It does not start while the steps
    before it have not all passed (prerequisites), unless the author decided otherwise."""

    def __init__(self, step: str, cfg: dict, dry: bool):
        self.step, self.cfg, self.dry = step, cfg, dry
        self.client, self.ds = client_and_dataset(cfg)
        self.inputs = inputs(dry)
        self.m = manifest()
        waits = prerequisites(step, self.m)
        if waits:
            msg = f"{step} waits for " + "; ".join(waits)
            if dry or AUTHOR_DECISION:
                print(f"warning: {msg}" + ("" if dry else f"; going on by the author's decision: {AUTHOR_DECISION}"))
            else:
                raise SystemExit(f"refused: {msg} (the steps run in the order of STEPS; --author-decision TEXT goes "
                                 "on all the same and is recorded)")
        if not dry:
            entry = {"step": step, "started_at": now(), **self.inputs}
            if waits:
                entry.update(waited_for=waits, author_decision=AUTHOR_DECISION)
            self.m["steps"].append(entry)
            save_json(self.m, MANIFEST)

    def job(self, job: Job) -> None:
        """Estimate a job from the current table metadata, run it and record it; a dry run skips a job whose
        input tables do not exist yet."""
        need = sorted(t for t in tables_of(job, self.cfg)[1] if t.startswith(PREFIX))
        rows = table_rows(self.client, self.ds, sorted(set(need) | set(ESTIMATE_TABLES)))
        absent = [t for t in need if rows[t] is None]
        if absent:
            made = creators(self.cfg)
            msg = f"{job.key} (job {job.no}) waits for " + ", ".join(f"{t} from {made.get(t, '?')}" for t in absent)
            if self.dry:
                print("skipped:", msg)
                return
            raise SystemExit("refused: " + msg)
        est = estimates(rows)[job.key]
        if est.missing:
            raise SystemExit(f"refused: no estimate of {job.key}: {list(est.missing)} have no rows")
        cmd = command(job, est, self.dry)
        print("$", " ".join(cmd[1:]), flush=True)
        before = len(ledger_jobs())
        rc = subprocess.run(cmd, cwd=ROOT).returncode
        if self.dry:
            if rc != 0:
                raise SystemExit(f"stopped: run_bq.py refused the dry run of {job.key} (exit {rc})")
            return
        ledger = ledger_jobs()
        if len(ledger) == before:
            raise SystemExit(f"refused: run_bq.py ran no job for {job.key} (exit {rc})")
        entry = ledger[-1]
        if len(ledger) != before + 1 or entry.get("label") != f"{CAMPAIGN} {job.label}":
            raise SystemExit("stopped: the last ledger entry is not the job just run")
        self.m["jobs"].append({"step": self.step, "key": job.key, "no": job.no, "job_id": entry["job_id"],
                               "at": entry["at"], "bytes_dry_run": entry["bytes_estimated"],
                               "bytes_expected": est.whole, "bytes_first_expected": est.first,
                               "bytes_billed": entry["bytes_billed"], "usd": entry["usd"],
                               **({"error": entry["error"]} if entry.get("error") else {})})
        save_json(self.m, MANIFEST)
        if rc != 0 or entry.get("error"):
            raise SystemExit(f"stopped: {job.key} failed (exit {rc}); see the ledger entry {entry['job_id']}")
        if entry["bytes_billed"] > BILL_RATIO * est.whole:
            raise SystemExit(f"stopped: {job.key} billed {entry['bytes_billed']/1e9:,.1f} GB, more than {BILL_RATIO} "
                             f"times its estimate of {est.whole/1e9:,.1f} GB; find the cause before the next job")

    def run_jobs(self, step: str) -> None:
        for job in jobs(self.cfg)[step]:
            self.job(job)

    def result(self, value, passed: bool = True) -> None:
        """Record the result of the step and whether it passed (the steps after it wait for a run that passed)."""
        if self.dry:
            return
        self.m["results"][self.step] = value
        self.m["steps"][-1].update(finished_at=now(), passed=bool(passed))
        save_json(self.m, MANIFEST)

    def sizes(self, *names: str) -> dict[str, int]:
        rows = table_rows(self.client, self.ds, names)
        missing = [n for n, r in rows.items() if r is None]
        if missing:
            raise SystemExit(f"stopped: {missing} were not created")
        return rows


# --------------------------------------------------------------------------- steps


def step_check(cfg: dict, dry: bool) -> None:
    w = windows(cfg)
    client, ds = client_and_dataset(cfg)
    problems = []
    preview = uncommitted()  # before gate A the check only warns and records nothing
    if preview:
        print("warning: not committed without local changes:", ", ".join(preview))
    d = client.get_dataset(ds)
    if d.default_table_expiration_ms or d.default_partition_expiration_ms:
        problems.append("the dataset has a default expiration")
    names = [t.table_id for t in client.list_tables(ds, max_results=10000)]
    existing = sorted(n for n in names if n.startswith(PREFIX))
    m = manifest()
    if existing and not m["jobs"]:
        problems.append(f"c12_ tables exist before any job of this driver: {existing}")
    meta = table_meta(client, ds, SOURCES)
    for name, v in meta.items():
        if v is None:
            problems.append(f"the source table {name} does not exist")
        elif v["modified"][:10] >= SOURCES_BEFORE or v["expires"]:
            problems.append(f"{name} was modified on {v['modified'][:10]} or expires")
    if meta["u_tokens"] and meta["u_tokens"]["rows"] != 5:
        problems.append(f"u_tokens has {meta['u_tokens']['rows']} rows, not 5")
    for name in ("logs_obs", "logs_w1"):
        if meta[name] and meta[name]["partitioning"] != "MONTH/block_timestamp":
            problems.append(f"{name} is not partitioned by month on block_timestamp")
    for name in ("u12_labels_w0", "u12_labels_w1"):
        if meta[name] and meta[name]["schema"].get("wallet") != "STRING":
            problems.append(f"{name} has no STRING column wallet (the spender)")
    # The token literals of sql/32 must be the five tokens of u_tokens.
    if meta["u_tokens"]:
        tokens = {"0x" + bytes(r["token"]).hex() for r in list_rows(client, ds, "u_tokens")}
        sql32 = (ROOT / "sql" / "32_c12_bal_pre.sql").read_text(encoding="utf-8")
        literals = set(re.findall(r"'(0x[0-9a-f]{40})'", sql32))
        if tokens != literals:
            problems.append(f"the token literals of sql/32 {sorted(literals)} are not u_tokens {sorted(tokens)}")
    views = table_meta(client, ds, list(VIEWS.values()))
    for name, cols in VIEW_COLUMNS.items():
        v = views[VIEWS[name]]
        lacking = [c for c in cols if v is None or c not in v["schema"]]
        if lacking:
            problems.append(f"the public view {name} lacks {lacking}")
    spent, camp = sum(j.get("usd", 0.0) for j in ledger_jobs()), campaign_usd()
    budget = float(cfg["bigquery"]["budget_usd"])
    rows = table_rows(client, ds, ESTIMATE_TABLES)
    est = estimates(rows)
    done = {j["key"] for j in m["jobs"] if not j.get("error")}
    made, waits = creators(cfg), {}
    for job in all_jobs(cfg):
        absent = sorted(t for t in tables_of(job, cfg)[1] if t.startswith(PREFIX) and rows.get(t) is None)
        if absent:
            waits[job.key] = ", ".join(f"{t} from {made.get(t, '?')}" for t in absent)
    print(f"windows: typing {w['typing_start'][:10]} to {w['typing_end'][:10]}, T_obs {w['tobs_start'][:10]} to "
          f"{w['tobs_end'][:10]}, W0 {w['t1_start'][:10]} to {w['t1_end'][:10]} (ends exclusive)")
    print(f"ledger: USD {spent:.3f} in {len(ledger_jobs())} jobs of USD {budget:.0f}; campaign {CAMPAIGN!r} "
          f"USD {camp:.3f} of {CAP_USD:.2f}")
    print(f"{'job':<15}{'no':>4}{'first GB':>11}{'whole GB':>11}{'USD':>8}  status")
    numbers = {j.key: j.no for j in all_jobs(cfg)}
    for key, e in est.items():
        status = "run" if key in done else (f"waits for {waits[key]}; known part only" if key in waits else "ready")
        print(f"{key:<15}{numbers[key]:>4}{e.first/1e9:>11.1f}{e.whole/1e9:>11.1f}{usd(e.whole):>8.3f}  {status}")
    print(f"{'account_types':<15}{30:>4}{0:>11.1f}{0:>11.1f}{0:>8.3f}  a load job, not billed")
    pending = sum(e.whole for k, e in est.items() if k not in done)
    print(f"{'not yet run':<19}{'':>11}{pending/1e9:>11.1f}{usd(pending):>8.3f}  (a lower bound while jobs wait)")
    problems += cap_problems(est, camp, spent, budget, done)
    if preview:
        print(f"not recorded in {MANIFEST.name}: the files above are not committed (a preview before gate A)")
    else:
        m.setdefault("checks_run", []).append({
            "at": now(), "head": git("rev-parse", "HEAD"), "problems": problems, "ledger_usd": round(spent, 4),
            "campaign_usd": round(camp, 4), "existing_c12": existing, "waits": waits,
            "estimates": {k: {"first": e.first, "whole": e.whole, "missing": list(e.missing)} for k, e in est.items()}})
        save_json(m, MANIFEST)
    if problems:
        raise SystemExit("check failed:\n  " + "\n  ".join(problems))
    print("check passed")


def step_subset(cfg: dict, dry: bool) -> None:
    run = Run("subset", cfg, dry)
    run.run_jobs("subset")
    if not dry:
        run.result(run.sizes("c12_logs5"))


def step_ends(cfg: dict, dry: bool) -> None:
    run = Run("ends", cfg, dry)
    run.run_jobs("ends")
    if not dry:
        run.result(run.sizes("c12_pairs5", "c12_ends"))


def step_activity(cfg: dict, dry: bool) -> None:
    run = Run("activity", cfg, dry)
    run.run_jobs("activity")
    if not dry:
        run.result(run.sizes("c12_tx_senders", "c12_emitters", "c12_creations"))


def step_queue(cfg: dict, dry: bool) -> None:
    run = Run("queue", cfg, dry)
    run.run_jobs("queue")
    if not dry:
        run.result(run.sizes("c12_rpc_queue"))


CLASSES = ("eoa", "eoa_7702", "contract", "smart_account")
REASONS = ("cohort", "spender", "counterparty", "audit_sender", "audit_untyped")


def types_against_queue(types, queue) -> dict:
    """Refuse account types that are not exactly one row of a known class per queue address; return the counts
    by reason and class and the cross-checks of the decoded-log emitters and the created contracts."""
    problems = []
    if types["address"].duplicated().any():
        problems.append(f"{int(types['address'].duplicated().sum()):,} duplicate addresses")
    typed, queued = set(types["address"]), set(queue["address"])
    if typed != queued:
        problems.append(f"{len(queued - typed):,} queue addresses untyped, {len(typed - queued):,} typed addresses "
                        "not in the queue")
    unknown = sorted(set(types["account_class"]) - set(CLASSES))
    if unknown:
        problems.append(f"unknown account classes {unknown}")
    unknown = sorted(set(queue["reason"]) - set(REASONS))
    if unknown:
        problems.append(f"unknown reasons {unknown}")
    if problems:
        raise SystemExit("stopped: the account types do not match the queue: " + "; ".join(problems))
    q = queue.merge(types[["address", "account_class"]], on="address", how="left")

    def counts(frame) -> dict:
        return {c: int(n) for c, n in frame["account_class"].value_counts().sort_index().items()}

    return {
        "addresses": int(len(q)),
        "by_class": counts(q),
        "by_reason": {r: counts(q[q["reason"] == r]) for r in REASONS},
        "emitters_by_class": counts(q[q["is_emitter"].astype(bool)]),
        "created_by_class": counts(q[q["is_created"].astype(bool)]),
        # EIP-3607: a transaction sender has no code other than an EIP-7702 delegation
        "audit_senders_with_code": int(((q["reason"] == "audit_sender")
                                        & ~q["account_class"].isin(["eoa", "eoa_7702"])).sum()),
    }


def typing_command(cfg: dict) -> list[str]:
    """The account-type reads of the queue (revision sections 4.2 and 4.3): at the pinned block, or the latest
    block at the first read if no endpoint serves it, with the smart-account probes, over the public endpoints
    of the overlay in order (CONTRACT_REP_RPC_URL, if set, is tried first by check_account_code.py itself)."""
    g = cfg["contract_graph"]
    return [sys.executable, "scripts/check_account_code.py", str(QUEUE), str(TYPES), "--input-parquet",
            "--block", str(int(g["pinned_block"])), "--fallback-latest", "--probe-wallets", "--workers", "4",
            "--batch", "25", *[x for url in g["rpc_urls"] for x in ("--rpc", str(url))]]


def typing_meta() -> dict | None:
    """TYPES.json of check_account_code.py (block, hosts, counts, complete), or None before the reads."""
    info = TYPES.with_suffix(".json")
    return load_json(info) if info.exists() else None


def typing_complete(meta: dict | None) -> bool:
    """Whether every queue address was read and probed: a resumable run that stopped leaves complete false."""
    return bool(meta) and meta.get("complete") is True


def step_typing(cfg: dict, dry: bool) -> None:
    run = Run("typing", cfg, dry)
    fetch = download("c12_rpc_queue", QUEUE)
    typing = typing_command(cfg)
    for cmd in (fetch, typing):
        print("$", " ".join(cmd[1:]), flush=True)
    if dry:
        return
    queued = run.sizes("c12_rpc_queue")["c12_rpc_queue"]
    sh(fetch)
    queue = read_parts(QUEUE)
    if len(queue) != queued:
        raise SystemExit(f"stopped: {len(queue):,} queue rows downloaded, the table has {queued:,}")
    sh(typing)
    meta = typing_meta()
    if not typing_complete(meta):
        raise SystemExit(f"stopped: {TYPES.name}.json does not record a complete run; run the typing step again "
                         "to resume the reads at the same block")
    out = types_against_queue(read_parts(TYPES), queue)
    out["types_json"] = meta
    out["types_sha256"] = {p.name: sha256(p) for p in sorted(TYPES.parent.glob(f"{TYPES.name}.part*.parquet"))}
    print("account types:", out["by_class"])
    run.result(out)


def step_load(cfg: dict, dry: bool) -> None:
    run = Run("load", cfg, dry)
    import pyarrow as pa
    import pyarrow.parquet as pq
    if not part_paths(TYPES) or not part_paths(QUEUE) or not typing_complete(typing_meta()):
        msg = f"account_types (job 30) waits for a complete {TYPES.name} and {QUEUE.name} from the typing step"
        if dry:
            print("skipped:", msg)
            return
        raise SystemExit("refused: " + msg)
    types, queue = read_parts(TYPES), read_parts(QUEUE)
    types_against_queue(types, queue)
    table = f"{run.ds}.{PREFIX}account_types"
    print(f"load: {len(types):,} rows of {TYPES.name} into {table} (a load job, not billed; replaces the table)")
    if dry:
        return
    from google.cloud import bigquery
    config = bigquery.LoadJobConfig(source_format=bigquery.SourceFormat.PARQUET,
                                    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE)
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / f"{PREFIX}account_types.parquet"
        pq.write_table(pa.Table.from_pandas(types, preserve_index=False), path)
        with path.open("rb") as f:
            job = run.client.load_table_from_file(f, table, job_config=config, location=cfg["bigquery"]["location"])
        job.result()
    t = run.client.get_table(table)
    schema = {f.name: f.field_type for f in t.schema}
    if int(t.num_rows or 0) != len(types) or schema.get("address") != "STRING":
        raise SystemExit(f"stopped: {table} has {t.num_rows} rows and address {schema.get('address')}, not "
                         f"{len(types):,} rows and STRING")
    run.m["jobs"].append({"step": "load", "key": "account_types", "no": 30, "job_id": job.job_id, "at": now(),
                          "bytes_billed": 0, "usd": 0.0})
    run.result({"job_id": job.job_id, "rows": int(t.num_rows), "schema": schema,
                "source_sha256": {p.name: sha256(p) for p in sorted(TYPES.parent.glob(f"{TYPES.name}.part*.parquet"))}})


def step_contracts(cfg: dict, dry: bool) -> None:
    run = Run("contracts", cfg, dry)
    run.run_jobs("contracts")
    if not dry:
        run.result(run.sizes("c12_contracts", "c12_user_accounts", "c12_events_cc"))


def step_balances(cfg: dict, dry: bool) -> None:
    run = Run("balances", cfg, dry)
    run.run_jobs("balances")
    if not dry:
        run.result(run.sizes("c12_bal_pre", "c12_bal"))


def step_anchors(cfg: dict, dry: bool) -> None:
    run = Run("anchors", cfg, dry)
    run.run_jobs("anchors")
    if dry:
        return
    rows = sorted(list_rows(run.client, run.ds, "c12_anchor_blocks"), key=lambda r: r["ts"])
    blocks = [{"anchor": r["anchor"], "ts": r["ts"].isoformat(),
               "block_number": None if r["block_number"] is None else int(r["block_number"])} for r in rows]
    numbers = [b["block_number"] for b in blocks]
    if [b["anchor"] for b in blocks] != list(ANCHORS) or None in numbers or numbers != sorted(set(numbers)):
        raise SystemExit(f"stopped: c12_anchor_blocks is not one increasing block per anchor: {blocks}")
    # The code reads of section 4.2 answer for the end of the data only at a block after 30 September 2026.
    typed = (typing_meta() or {}).get("block_number")
    after = None if typed is None else int(typed) > numbers[-1]
    run.result({"blocks": blocks, "typing_block": typed, "typing_block_after_end_0930": after}, passed=after is True)
    print("anchor blocks:", {b["anchor"]: b["block_number"] for b in blocks})
    if after is None:
        raise SystemExit(f"stopped: {TYPES.name}.json records no block, so the typing block cannot be checked")
    if after is False:
        raise SystemExit(f"stopped: the account types were read at block {typed}, not after block {numbers[-1]}")


def step_audit(cfg: dict, dry: bool) -> None:
    run = Run("audit", cfg, dry)
    run.run_jobs("audit")
    check = [sys.executable, "scripts/balance_audit.py", "--sample", str(BAL_AUDIT), "--anchors", str(ANCHOR_BLOCKS)]
    cmds = [download("c12_bal_audit", BAL_AUDIT), download("c12_anchor_blocks", ANCHOR_BLOCKS)]
    for cmd in (*cmds, check):
        print("$", " ".join(cmd[1:]), flush=True)
    if dry:
        return
    sizes = run.sizes("c12_bal_audit")
    for cmd in cmds:
        sh(cmd)
    before = stamp(BALANCE_AUDIT)
    rc = subprocess.run(check, cwd=ROOT).returncode
    summary = load_json(BALANCE_AUDIT) if written(BALANCE_AUDIT, before) else None  # never an earlier verdict
    keep = ("mode", "block", "hosts", "rows", "judged", "matched", "share", "threshold", "passed")
    passed = rc == 0 and summary is not None and summary.get("passed") is True
    run.result({**sizes, "exit_code": rc, "balance_audit": {k: summary.get(k) for k in keep} if summary else None},
               passed=passed)
    if not passed:
        if rc == 2 and summary is None:   # no endpoint gave the T_obs block or the latest block: no check was made
            raise SystemExit(f"stopped: the balance check gave no result (exit 2, no new {BALANCE_AUDIT.name}: no "
                             "endpoint gave the T_obs block or the latest block); run the audit step again "
                             "(docs/revision_contract_graph.md section 6)")
        raise SystemExit(f"stopped: the balance check did not pass (exit {rc}, "
                         f"{BALANCE_AUDIT.name if summary else 'no new ' + BALANCE_AUDIT.name}); the run waits until "
                         "the cause is understood (docs/revision_contract_graph.md section 6)")


def structure_counts(struct) -> tuple[dict[str, int], dict[str, int]]:
    """The distinct pairs of each layer of c12_struct_t1 without self-pairs, and the self-pairs of each layer: the
    edges the structure pilot counts, since self-loops are ignored for the structure (protocol section 2)."""
    s = struct[["a", "b", "layer"]].astype(str)
    s = s.assign(a=s["a"].str.lower(), b=s["b"].str.lower()).drop_duplicates()
    loop = s["a"] == s["b"]

    def per_layer(part) -> dict[str, int]:
        return {k: int(v) for k, v in part["layer"].value_counts().sort_index().items()}

    return per_layer(s[~loop]), per_layer(s[loop])


def step_structure(cfg: dict, dry: bool) -> None:
    run = Run("structure", cfg, dry)
    run.run_jobs("structure")
    fetch = download("c12_struct_t1", STRUCT_T1)
    pilot = [sys.executable, "scripts/run_discovery.py", "--window", "t1", "--feasibility"]
    for cmd in (fetch, pilot):
        print("$", " ".join(cmd[1:]), flush=True)
    if dry:
        return
    sizes = run.sizes("c12_struct_t1")
    sh(fetch)
    layers, self_pairs = structure_counts(read_parts(STRUCT_T1, columns=["a", "b", "layer"]))
    print("structure at t1 (distinct pairs without self-pairs):", layers, "self-pairs:", self_pairs)
    before = stamp(FEASIBILITY)
    rc = subprocess.run(pilot, cwd=ROOT).returncode
    report, dirty = None, []
    if written(FEASIBILITY, before):  # an earlier report (perhaps pinned at gate B) is never this run's result
        body = load_json(FEASIBILITY)
        report = {"path": FEASIBILITY.relative_to(ROOT).as_posix(), "sha256": sha256(FEASIBILITY),
                  **{k: v for k, v in body.items() if isinstance(v, (int, float, str, bool))}}
        # A main run refuses a pilot that records files with local changes (run_discovery.check_fixed). The record
        # must name every file of PILOT_COMMITTED; a file it lacks counts as not committed.
        state = (body.get("code") or {}).get("committed") or {}
        dirty = sorted({rel for rel, ok in state.items() if ok is not True}
                       | ({rel for rel in PILOT_COMMITTED if rel not in state} if state else set()))
        dirty = dirty or ([] if state else ["no record"])
    stop_edges = int(cfg["discovery"]["stop_min_allow_edges"])
    below = layers.get("allow_capped", 0) < stop_edges
    run.result({**sizes, "layers": layers, "self_pairs": self_pairs, "pilot_exit_code": rc, "feasibility": report,
                "pilot_not_committed": dirty, "allow_capped_below_stop": below},
               passed=rc == 0 and report is not None and not dirty and not below)
    if rc == 2 and report is not None:
        raise SystemExit(f"stopped: the structure pilot set a stop flag of docs/discovery_protocol.md section 7 (see "
                         f"{FEASIBILITY.name}); the author decides before gate B")
    if rc != 0 or report is None:
        raise SystemExit(f"stopped: the structure pilot exited with {rc} or wrote no {FEASIBILITY.name}")
    if dirty:
        raise SystemExit(f"stopped: the structure pilot did not run on committed files ({', '.join(dirty)}), and a "
                         "main run refuses such a pilot; commit them and run structure again")
    if below:
        raise SystemExit(f"stopped: {layers.get('allow_capped', 0):,} capped allowance edges between contracts at t1, "
                         f"fewer than {stop_edges:,}; the author decides (docs/discovery_protocol.md section 7)")


def gate_b(step: str):
    def refuse(cfg: dict, dry: bool) -> None:
        raise SystemExit(f"refused: {step} is a gate B step ({GATE_B[step]}); gate B: not yet written. It is "
                         "committed after the structure pilot (docs/revision_contract_graph.md section 12)")
    return refuse


step_constants, step_pairs, step_rest, step_checks, step_download = (gate_b(s) for s in GATE_B)


def main() -> int:
    global AUTHOR_DECISION
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("steps", nargs="+", choices=STEPS)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--author-decision", metavar="TEXT",
                    help="run the steps although the steps before them did not all pass; the manifest records TEXT")
    args = ap.parse_args()
    if args.author_decision is not None and not args.author_decision.strip():
        ap.error("--author-decision needs a text")
    AUTHOR_DECISION = args.author_decision
    for s in args.steps:  # refuse a gate B step before any other step runs
        if s in GATE_B:
            gate_b(s)(None, args.dry_run)
    cfg = load_config()
    for s in args.steps:
        globals()[f"step_{s}"](cfg, args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
