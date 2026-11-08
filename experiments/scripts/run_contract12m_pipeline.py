#!/usr/bin/env python3
"""BigQuery and RPC steps of the contract-graph revision (docs/revision_contract_graph.md), in order.

Every query goes through scripts/run_bq.py with the checks of this variant: a job creates only c12_* tables,
reads only the project tables and public views named here, is labelled "contract12m: ..." and is refused if the
jobs of the campaign would pass the cap of the overlay (contract_graph.campaign_cap_usd: USD 14, raised to USD 15 by
the gate B amendment of revision section 13) or the ledger the budget of the variant (USD 60).
Each job carries an estimate of the bytes it bills, for its first statement and for the whole job, since the dry
run of a file with several statements counts only the first: the dry runs of 7 November 2026 for the parts that
read the public views, logs_obs and logs_w1, the bills of the twelve-month label jobs for the parts of job 39 that
read the same tables, plus the rows of every project table it reads (table metadata) times the billed widths of the
columns read (at least 10 MB per table). A job whose first statement dry-runs above 1.25 times its estimate is
refused, and after a job that billed more than 1.5 times its estimate the driver stops. An estimate that needs a
table that does not exist yet is computed when its step runs. Gate A:

  check      free checks: the windows of the configuration against the revision, no expiration on the
             dataset, the source tables and the public views with the columns the jobs read, the inputs that
             the measured terms of job 39 calibrate (CALIBRATED), the five token literals of sql/32 against
             u_tokens, no c12_* table before the first job of the manifest, the ledger and the campaign; prints
             the estimate of every job whose inputs exist and the jobs that wait for an earlier one, and fails
             if the known estimates of the gate A jobs would pass the cap. It also prints the projection of the
             gate B jobs not yet run (every table made inside gate B at an upper bound), the cap and the budget
             that the campaign and the ledger with that projection need (rounded up to the cent), and whether
             'Protocol fixed' holds a block; the gate B jobs are judged by that projection alone, and once
             'Protocol fixed' holds a block, a projection that would pass the cap or the budget fails the
             check. It is recorded in the run manifest only once the files in COMMITTED are committed; before
             that it writes nothing
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
  contracts  job 31: the node set, the typed user accounts and the events between contracts, with the
             contracts that the amendment of 9 November 2026 counts as smart accounts (common.
             SMART_ACCOUNT_CODE_HASHES and SMART_ACCOUNT_IMPLEMENTATIONS) among the user accounts; checks the lists
             against the typing output before the job and the size of c12_contracts after it
  balances   jobs 32 and 33: the net flow before 2023-10-01 and the balances at t1, T_obs and 2026-09-30
  anchors    job 34: the last block at or before each anchor
  audit      job 43, then the balanceOf check of scripts/balance_audit.py
  structure  job 35, then the structure pilot (scripts/run_discovery.py --window t1 --feasibility); the
             capped allowance edges are counted as the pilot counts them, distinct pairs without self-pairs

Gate B (revision sections 7 and 12 and the gate B amendment of section 13):

  constants  the three jobs 36: the latest allowances between contracts at both freezes, valued at the anchor
             day's price and capped at the owner's balance (c12_allow_triples), the events of user accounts
             toward contracts and untyped addresses (c12_user_events) and the constants of the W0 score window
             (c12_constants), rounded to two significant digits into
             data/0-usd-token-list-and-prices/contract-12m/constants.json. That file is committed on its own,
             with the run manifest and the ledger, before pairs; once it is committed the step does not run again
  pairs      job 37: the capped and uncapped allowance pairs and the transfer pairs of both freezes
  rest       jobs 38 to 41: the cohorts without user accounts and the members of the twelve-month lists with
             their class, the same-window proxies, the label parts of W0 and W1 by account class, the node ids
             and the export tables, importance, the untyped inflow and the description of the allowances; the
             t1 pairs must be those of the structure pilot
  checks     job 42: the invariants of sql/42, every one 0
  download   the gate B tables into graph-tables-contract-12m, read back as the discovery runner reads them and
             compared with the pinned pilot, and the cohort summaries of revised-contract-12m/cohort

Every step but check refuses to run unless the files in COMMITTED are committed without local changes (a dry run
of a gate A step only warns). A gate B step, its dry run too, also refuses unless the section 'Protocol fixed' of
docs/discovery_protocol.md passes run_discovery.check_fixed and pins the pilot that the last structure run wrote,
the file on disk being that pilot, and unless the files in COMMITTED_B are committed without local changes. Every
gate B step after constants refuses unless constants.json is committed on its own, in a commit that holds exactly
it, the run manifest and the ledger (its dry run warns and takes placeholder constants); rest and checks refuse if
a source table does not exist, was modified on SOURCES_BEFORE or later or expires, or if an input that the
measured terms of job 39 calibrate (CALIBRATED: SOURCES_B, logs_obs, logs_w1 and u_tokens) was modified after the
first bill that calibrates them (CALIBRATED_AT); and a gate B step refuses when the campaign and the projection of
the gate B jobs from it on would pass the cap, or the ledger and that projection the budget. Once 'Protocol fixed'
holds a block, every gate A step from subset to structure refuses. A command line with several steps is refused
before any of them runs if one of them would be refused for a reason that preflight checks: a gate A step once
'Protocol fixed' holds a block; a gate B step without 'Protocol fixed' on the pilot of the structure step, or with
a file of COMMITTED or COMMITTED_B not committed without local changes; constants once constants.json is
committed; and, unless it is a dry run, a later gate B step without the constants committed on their own. The
source check of rest and checks and the cap projection of a later step are checked when that step starts (the
projection depends on the bills and the tables of the steps before it).
data/2-.../revised-contract-12m/run_manifest.json records the commit, the hashes of those files, every job and the
results of every step.

The steps run in this order. Each step from subset on refuses to run unless the last check found no problem
and every step before it has a last run that passed, the last runs in this order: a step run again makes the
steps after it wait until they are run again (a check run again only by what it finds). A step passes when its jobs succeed, and anchors, audit
and structure only when their checks hold (the typing block after 30 September; the balance check; a pilot whose
record names every file of PILOT_COMMITTED as committed, without a stop), so that a balance check below its
threshold stops the run until the cause is understood, and one that gave no result (no endpoint gave the T_obs or the
latest block) is run again (revision section 6). A step records only the balance_audit.json or feasibility_t1.json that its own run wrote.
--author-decision TEXT lets a step go on all the same; its run in the manifest records the text and what was
missing. It passes only the order of the steps, none of the refusals above; after gate B the run manifest marks
such a decision (after_gate_b), the published digest of this variant names it (revision section 13) and the change
record records it. A gate B step needs no new decision for the waits
that decisions taken before gate B already cover (revision section 13, amendment of 9 November 2026): the waits
that the last structure run recorded under its author's decision, and, when 'Protocol fixed' carries an
author_decision, the wait for a structure run that passes. They cover them only while that run is the last of
gate A: it recorded its result (so the pilot that 'Protocol fixed' pins is its own), no step of gate A ran after
it, and, for the wait for a check, no check ran after it started. The run in the manifest records those waits as
a gate A decision (gate_a_decision: the index of that structure entry, its started_at and the waits), not as
after_gate_b; any other wait still needs --author-decision. A --dry-run of a step that waits only warns.

Usage: python scripts/run_contract12m_pipeline.py STEP [STEP ...] [--dry-run] [--author-decision TEXT]
"""

from __future__ import annotations

import argparse
import hashlib
import json
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
from common import (GRAPH, PROC, ROOT, SMART_ACCOUNT_CODE_HASHES, SMART_ACCOUNT_TYPED, TYPES,  # noqa: E402
                    TYPES_DIR, USD_CONSTANTS, VARIANT, load_config, load_json, part_paths, read_parts,
                    save_json, smart_account_extension, smart_account_sql_params)
from usd import UNLIMITED_BASE_UNITS, round_sig, slope_for_median  # noqa: E402

# The c12_ tables, folders and constants belong to this variant; any other would mix them up.
if VARIANT != "contract12m":
    raise SystemExit("run_contract12m_pipeline.py belongs to the contract-graph variant "
                     "(CONTRACT_REP_VARIANT=contract12m)")

STEPS = ("check", "subset", "ends", "activity", "queue", "typing", "load", "contracts", "balances", "anchors",
         "audit", "structure", "constants", "pairs", "rest", "checks", "download")
GATE_B = {"constants": "jobs 36", "pairs": "job 37", "rest": "jobs 38 to 41", "checks": "job 42",
          "download": "the downloads of the gate B tables"}
# The gate A steps after check: none of them runs again once docs/discovery_protocol.md holds 'Protocol fixed'.
CHAIN_A = STEPS[1:STEPS.index("structure") + 1]
# The steps after check, each of which runs only after the ones before it have passed, in this order.
CHAIN = STEPS[1:]
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
PROTOCOL = ROOT / "docs" / "discovery_protocol.md"

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

SQL_FILES_B = ("36_c12_allow_triples.sql", "36_c12_user_events.sql", "36_c12_constants.sql", "37_c12_pairs.sql",
               "38_c12_cohorts.sql", "38_c12_proxies.sql", "39_c12_label_parts.sql", "40_c12_export_ids.sql",
               "41_c12_importance.sql", "42_c12_checks.sql")
# The evaluation code that the gate B amendment of revision section 13 names file by file; those already in
# COMMITTED are checked there.
EVAL_FILES_B = ("scripts/common.py", "scripts/labels.py", "scripts/graphs.py", "scripts/usd.py",
                "scripts/run_same_window.py", "scripts/run_holdout.py", "scripts/run_registered.py",
                "scripts/run_robustness.py", "scripts/run_discovery.py")
FEASIBILITY_REL = FEASIBILITY.relative_to(ROOT).as_posix()
# Checked by every gate B step in addition to COMMITTED, which stays the gate A list of revision section 12: the SQL
# files of the gate B steps, the evaluation code and the structure pilot that 'Protocol fixed' pins.
COMMITTED_B = (*(f"sql/{f}" for f in SQL_FILES_B), *(f for f in EVAL_FILES_B if f not in COMMITTED), FEASIBILITY_REL)
CONSTANTS_REL = USD_CONSTANTS.relative_to(ROOT).as_posix()
MANIFEST_REL, LEDGER_REL = MANIFEST.relative_to(ROOT).as_posix(), LEDGER.relative_to(ROOT).as_posix()
# The only files the commit of constants.json may hold (precedent 77a1e49): the constants, the run manifest that
# records their run and the ledger that bills it.
CONSTANTS_COMMIT = (CONSTANTS_REL, MANIFEST_REL, LEDGER_REL)
# The constants a dry run of a gate B step passes to its jobs before constants.json is committed.
PLACEHOLDER_CONSTANTS = {"b_transfer": 0.01, "b_allowance": 0.01, "cap_allowance_usd": 1e6, "cap_user_usd": 1e6}
CONSTANT_KEYS = ("m_transfer_usd", "m_allowance_usd", "cap_allowance_usd", "cap_user_usd", "b_transfer",
                 "b_allowance")
# The columns of c12_constants (sql/36_c12_constants.sql), in order.
CONSTANT_COLUMNS = ("m_transfer", "p99_transfer", "p10_transfer", "p90_transfer", "n_transfers", "m_allowance",
                    "p99_allowance", "p10_allowance", "p90_allowance", "n_latest_allowances", "n_positive_allowances",
                    "n_capped_to_zero", "n_capped_below_allowance", "n_unlimited_positive", "m_user_transfer",
                    "p99_user_transfer", "p10_user_transfer", "p90_user_transfer", "n_user_transfers")

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
# The twelve-month tables that job 39 reads, with the base tables under its views: its estimate is the bill of the
# twelve-month label jobs on them, which holds only while they are as they were.
SOURCES_B = ("u12_allow_triples_t1", "u12_allow_triples_tobs", "u12_approvals_t1", "u12_approvals_w1",
             "u12_transfers_t1", "u12_transfers_tobs", "u12_transfers_w1", "u_approvals", "u_transfers",
             "u_approvals_w1", "u_transfers_w1")
# The inputs whose reads the measured terms of job 39 calibrate (CAL_39_W0, CAL_39_W1): SOURCES_B, and logs_obs,
# logs_w1 and u_tokens, which the twelve-month label jobs read as well; and the time at which the ledger records the
# first bill that calibrates them (92c0b37c-0659-4f63-8aa7-0f335265d9fe, "usd12m: W0 labels"). The check reports an
# input modified after it, and the steps rest and checks refuse it (the gate B amendment of revision section 13).
CALIBRATED = (*SOURCES_B, "logs_obs", "logs_w1", "u_tokens")
CALIBRATED_AT = "2026-10-28T09:09:32+00:00"
U12_LISTS = ("u12_cohort_tobs", "u12_cohort_t1", "u12_labels_w0", "u12_labels_w1")
X_PAIRS = ("c12_x_allow_pairs_tobs", "c12_x_allow_pairs_t1", "c12_x_allow_pairs_unc_tobs",
           "c12_x_allow_pairs_unc_t1", "c12_x_transfer_pairs_tobs", "c12_x_transfer_pairs_t1")
# The gate B tables the download step writes into GRAPH, with their stems.
DOWNLOADS = (("c12_x_nodes", "nodes"),
             ("c12_x_allow_pairs_tobs", "allow_pairs_tobs"), ("c12_x_transfer_pairs_tobs", "transfer_pairs_tobs"),
             ("c12_x_allow_pairs_t1", "allow_pairs_t1"), ("c12_x_transfer_pairs_t1", "transfer_pairs_t1"),
             ("c12_x_allow_pairs_unc_tobs", "allow_pairs_uncapped_tobs"),
             ("c12_x_allow_pairs_unc_t1", "allow_pairs_uncapped_t1"),
             ("c12_importance_tobs", "importance_tobs"), ("c12_importance_t1", "importance_t1"),
             ("c12_inflow_untyped_tobs", "inflow_untyped_tobs"), ("c12_inflow_untyped_t1", "inflow_untyped_t1"),
             ("c12_proxies_tobs", "proxies_tobs"),
             ("c12_x_label_split_w0", "label_split_w0"), ("c12_x_label_split_w1", "label_split_w1"),
             ("c12_x_members", "members"), ("c12_describe_allowances", "describe_allowances"))
# The tables the rest step makes, and the twelve-month lists their rows are compared with.
REST_TABLES = ("c12_cohort_tobs", "c12_cohort_t1", "c12_members", "c12_proxies_tobs", "c12_label_parts_w0",
               "c12_label_parts_w1", "c12_x_label_split_w0", "c12_x_label_split_w1", "c12_nodes", "c12_x_nodes",
               "c12_x_members", *X_PAIRS, "c12_importance_raw", "c12_importance_tobs", "c12_importance_t1",
               "c12_inflow_untyped_tobs", "c12_inflow_untyped_t1", "c12_describe_allowances", *U12_LISTS)
# The check names of sql/42, in its order.
EXPECTED_CHECKS = (
    "contracts_user_accounts_overlap", "user_accounts_zero_address", "contracts_system_or_zero",
    "pair_ends_not_contract_tobs", "pair_ends_not_contract_t1", "pair_ends_user_account_tobs",
    "pair_ends_user_account_t1", "pairs_duplicate", "tags_known", "nodes_not_contract", "nodes_ids", "nodes_set",
    "node_flags", "x_nodes_rows", "x_rows_tobs", "x_rows_t1", "x_weights", "capped_pairs_nonpositive",
    "cap_above_uncapped_triples", "cap_above_uncapped_pairs", "triples_without_balance", "dust_rule",
    "anchor_prices", "triples_unique", "triples_window_tobs", "triples_window_t1", "struct_allow_capped_t1",
    "struct_allow_uncapped_t1", "struct_transfer_t1", "transfer_pairs_window_tobs", "transfer_pairs_window_t1",
    "pairs5_tobs", "pairs5_t1", "constants_rows_t1", "constants_values", "members_rows", "members_class",
    "cohort_user_accounts_tobs", "cohort_user_accounts_t1", "cohort_not_contract_tobs", "cohort_not_contract_t1",
    "cohort_rows_tobs", "cohort_rows_t1", "spender_untyped_w0", "spender_untyped_w1", "proxies_rows",
    "labels_recount_w0", "labels_recount_w1", "label_parts_sum_w0", "label_parts_sum_w1", "label_split_rows_w0",
    "label_split_rows_w1", "label_spender_class_w0", "label_spender_class_w1", "importance_not_contract_tobs",
    "importance_not_contract_t1", "importance_ids_tobs", "importance_ids_t1", "importance_rows_tobs",
    "importance_rows_t1", "importance_raw_rows", "inflow_rows_tobs", "inflow_rows_t1", "describe_rows")

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
CODE_HASH = 2 + 66  # a 0x hex code hash STRING (sql/31 reads it with the implementation, a HEX, since 9 November 2026)
LOGS5_ALL = 3 * A + KIND + 6 * NUM  # every column of c12_logs5
# The gate B columns: a tag ('tobs'), a boolean, a list name ('cohort_tobs'), a member class ('user_account'), a
# user-account source ('rpc_smart_account'), a part ('contract') and a layer ('allow_uncapped').
TAG, BOOL, LIST, MCLASS, SOURCE, PART, LAYER = 6, 1, 13, 14, 19, 10, 16
MIN_TABLE = 10 * 2**20  # at least 10 MB is billed for every table a query reads
USD_PER_TIB = 6.25


@dataclass(frozen=True)
class Measured:
    """Bytes measured once (a free dry run of 7 November 2026, or the bill of an earlier job on the same, unchanged
    tables, named by its ledger job id) and the tables or views whose columns it counted."""
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
# Job 39 reads the inputs of the twelve-month label jobs with the definitions of sql/16 (the same tables, columns and
# parameters): their bills of 28 October 2026 are the measured parts (the gate B amendment of revision section 13),
# valid while those tables are unchanged (SOURCES, SOURCES_B). Ledger job 92c0b37c-0659-4f63-8aa7-0f335265d9fe
# ("usd12m: W0 labels") billed 53,868,494,848 B after a dry run of 53,867,600,671 B, and
# f66a1ca1-d501-4011-ac63-3f46e0815825 ("usd12m: W1 labels") 49,754,931,200 B after 49,754,705,176 B.
CAL_39_W0 = Measured(53_868_494_848, ("u12_allow_triples_t1", "u12_approvals_t1", "u12_transfers_t1", "logs_obs",
                                      "u_tokens"))
CAL_39_W1 = Measured(49_754_931_200, ("u12_allow_triples_tobs", "u12_approvals_w1", "u12_transfers_w1",
                                      "u12_transfers_tobs", "logs_w1", "u_tokens"))

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
    # address, account_class, code_hash and implementation of the types and the senders, twice; then every column
    # of c12_logs5
    "contracts": [[Read("c12_account_types", HEX + CLASS + CODE_HASH + HEX), Read("c12_tx_senders", A)],
                  [Read("c12_account_types", HEX + CLASS + CODE_HASH + HEX), Read("c12_tx_senders", A)],
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
# The gate B jobs, one entry per CREATE statement in file order. A month-partitioned table is counted once per
# statement over the union of the partitions its references read (free dry runs of 8 November 2026 on c12_logs5 with
# token, a, b, kind, usd and block_timestamp: the W0 and T_obs score windows 89.10 GB whether one reference or two
# read them, the whole table 103.99 GB), so the whole-table rows bound a first statement that reads c12_events_cc or
# c12_user_events under both windows.
READS.update({
    # kind, token, a, b, value, block_number, log_index, block_timestamp; token, address, bal_t1, bal_tobs
    "triples": [[Read("c12_events_cc", KIND + 3 * A + 4 * NUM), Read("c12_bal", 2 * A + 2 * NUM),
                 Read("u_tokens", A + NUM), Read("u_prices", A + 2 * NUM)]],
    # every column of c12_logs5 but amount; the address of the node and queue tables
    "user_events": [[Read("c12_logs5", KIND + 3 * A + 5 * NUM), Read("c12_user_accounts", A), Read("c12_contracts", A),
                     Read("c12_ends", A), Read("c12_rpc_queue", HEX), Read("c12_tx_senders", A)]],
    # kind, usd, block_timestamp; tag, value, usd_allow, usd_eff; kind, usd, block_timestamp, to_contract
    "constants": [[Read("c12_events_cc", KIND + 2 * NUM), Read("c12_allow_triples", TAG + 3 * NUM),
                   Read("c12_user_events", KIND + 2 * NUM + BOOL)]],
    # kind, a, b, usd, block_timestamp; tag, owner, spender, usd_eff (usd_allow), age_days, block_timestamp
    "pairs": [[Read("c12_events_cc", KIND + 2 * A + 2 * NUM)], [Read("c12_allow_triples", TAG + 2 * A + 3 * NUM)],
              [Read("c12_allow_triples", TAG + 2 * A + 3 * NUM)]],
    "cohorts": [[Read("u12_cohort_tobs", A + 2 * NUM), Read("c12_user_accounts", A)],
                [Read("u12_cohort_t1", A + 2 * NUM), Read("c12_user_accounts", A)],
                [Read("u12_cohort_tobs", A), Read("u12_cohort_t1", A), Read("u12_labels_w0", HEX),
                 Read("u12_labels_w1", HEX), Read("c12_contracts", A), Read("c12_user_accounts", A + SOURCE)]],
    "proxies": [[Read("c12_events_cc", KIND + 2 * A + 2 * NUM), Read("c12_cohort_tobs", A)]],
    "labels_w0": [[CAL_39_W0, Read("c12_contracts", A), Read("c12_user_accounts", A),
                   Read("c12_members", LIST + A + MCLASS)],
                  [Read("c12_label_parts_w0", HEX + MCLASS + 25 * NUM)]],
    "labels_w1": [[CAL_39_W1, Read("c12_contracts", A), Read("c12_user_accounts", A),
                   Read("c12_members", LIST + A + MCLASS)],
                  [Read("c12_label_parts_w1", HEX + MCLASS + 25 * NUM)]],
    "node_ids": [[Read("c12_allow_pairs", 2 * A), Read("c12_allow_pairs_unc", 2 * A), Read("c12_transfer_pairs", 2 * A),
                  Read("c12_members", LIST + A + MCLASS), Read("c12_contracts", A)],
                 [Read("c12_nodes", NUM + HEX + 4 * BOOL)],
                 [Read("c12_members", LIST + HEX + MCLASS + SOURCE)],
                 [Read("c12_allow_pairs", TAG + 2 * A + 6 * NUM), Read("c12_nodes", A + NUM)],
                 [Read("c12_allow_pairs", TAG + 2 * A + 4 * NUM), Read("c12_nodes", A + NUM)],
                 [Read("c12_allow_pairs_unc", TAG + 2 * A + 4 * NUM), Read("c12_nodes", A + NUM)],
                 [Read("c12_allow_pairs_unc", TAG + 2 * A + 4 * NUM), Read("c12_nodes", A + NUM)],
                 [Read("c12_transfer_pairs", TAG + 2 * A + 6 * NUM), Read("c12_nodes", A + NUM)],
                 [Read("c12_transfer_pairs", TAG + 2 * A + 4 * NUM), Read("c12_nodes", A + NUM)]],
    "importance": [[Read("c12_user_events", KIND + 3 * A + 5 * NUM + BOOL), Read("c12_bal", 2 * A + 2 * NUM),
                    Read("u_tokens", A + NUM), Read("u_prices", A + 2 * NUM)],
                   [Read("c12_importance_raw", TAG + PART + A + 4 * NUM), Read("c12_nodes", A + NUM)],
                   [Read("c12_importance_raw", TAG + PART + A + 4 * NUM), Read("c12_nodes", A + NUM)],
                   [Read("c12_importance_raw", TAG + PART + NUM)],
                   [Read("c12_importance_raw", TAG + PART + NUM)],
                   [Read("c12_allow_triples", TAG + A + 3 * NUM)]],
    "checks": [[Read("c12_contracts", A), Read("c12_user_accounts", A), Read("c12_nodes", NUM + HEX + A + 4 * BOOL),
                Read("c12_x_nodes", NUM + HEX + 4 * BOOL), Read("c12_members", LIST + HEX + A + MCLASS),
                Read("c12_allow_triples", TAG + 3 * A + 10 * NUM), Read("c12_allow_pairs", TAG + 2 * A + 5 * NUM),
                Read("c12_allow_pairs_unc", TAG + 2 * A + 5 * NUM), Read("c12_transfer_pairs", TAG + 2 * A + 3 * NUM),
                Read("c12_x_allow_pairs_tobs", 8 * NUM), Read("c12_x_allow_pairs_t1", 6 * NUM),
                Read("c12_x_allow_pairs_unc_tobs", 6 * NUM), Read("c12_x_allow_pairs_unc_t1", 6 * NUM),
                Read("c12_x_transfer_pairs_tobs", 8 * NUM), Read("c12_x_transfer_pairs_t1", 6 * NUM),
                Read("c12_struct_t1", 2 * HEX + LAYER), Read("c12_pairs5", 2 * A + 3 * NUM),
                Read("u_tokens", A), Read("u_prices", A + 2 * NUM), Read("c12_constants", 7 * NUM),
                Read("c12_cohort_tobs", A), Read("c12_cohort_t1", A), Read("u12_cohort_tobs", A),
                Read("u12_cohort_t1", A), Read("u12_labels_w0", HEX + 7 * NUM), Read("u12_labels_w1", HEX + 7 * NUM),
                Read("c12_label_parts_w0", HEX + MCLASS + 32 * NUM), Read("c12_label_parts_w1", HEX + MCLASS + 32 * NUM),
                Read("c12_x_label_split_w0", HEX + MCLASS + 25 * NUM),
                Read("c12_x_label_split_w1", HEX + MCLASS + 25 * NUM), Read("c12_proxies_tobs", HEX + 7 * NUM),
                Read("c12_importance_tobs", NUM + HEX + 4 * NUM), Read("c12_importance_t1", NUM + HEX + 4 * NUM),
                Read("c12_importance_raw", TAG + PART + A + 2 * NUM), Read("c12_inflow_untyped_tobs", NUM),
                Read("c12_inflow_untyped_t1", NUM), Read("c12_describe_allowances", NUM)]],
})
# A table that one statement creates and a later statement of the same job reads is bounded by the table it is
# made from: c12_pairs5 has at most one row per row of c12_logs5, c12_contracts one per typed address. A bound is
# a table, or (table, factor, extra) for factor times its rows plus extra.
BOUND = {"ends": {"c12_pairs5": "c12_logs5"}, "contracts": {"c12_contracts": "c12_account_types"}}
BOUND.update({
    "labels_w0": {"c12_label_parts_w0": "u12_labels_w0"},   # one row per spender of the u12 labels
    "labels_w1": {"c12_label_parts_w1": "u12_labels_w1"},
    "node_ids": {"c12_nodes": "c12_contracts"},              # nodes are contracts
    "importance": {"c12_importance_raw": ("c12_contracts", 2, 2)},  # a row per contract and tag, two untyped rows
})
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


def jobs(cfg: dict, c: dict | None = None) -> dict[str, list[Job]]:
    """The query jobs of every step. ``c`` holds the constants of constants.json; without it the gate B jobs take
    PLACEHOLDER_CONSTANTS (a dry run before the constants are committed; the estimates do not depend on them)."""
    w, g = windows(cfg), cfg["contract_graph"]
    disc, h, r = cfg["discovery"], cfg["holdout"], cfg["registered_window"]
    c = c or PLACEHOLDER_CONSTANTS
    first, last = system_range(g["system_address_max"])
    dust = str(dust_digits(g["balance"]["dust_token"]))
    population = {"start_ts": w["typing_start"], "tobs_end": w["tobs_end"]}
    freezes = {"start_ts": w["t1_start"], "t1": w["t1"], "tobs_start": w["tobs_start"], "tobs": w["tobs"]}
    weights = {"b_transfer": repr(float(c["b_transfer"])), "b_allowance": repr(float(c["b_allowance"])),
               "cap_allowance": repr(float(c["cap_allowance_usd"]))}
    unlimited = repr(UNLIMITED_BASE_UNITS)
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
                          params={"system_first": first, "system_last": last, **smart_account_sql_params()})],
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
        "constants": [
            Job("triples", 36, "36_c12_allow_triples.sql", "latest allowances between contracts at both freezes",
                params={**freezes, "dust_digits": dust}, allow=("u_tokens", "u_prices")),
            Job("user_events", 36, "36_c12_user_events.sql",
                "events of user accounts toward contracts and untyped addresses",
                params={"start_ts": w["t1_start"], "tobs": w["tobs"]}),
            Job("constants", 36, "36_c12_constants.sql", "constants of the contract graph on the W0 score window",
                params={"start_ts": w["t1_start"], "t1": w["t1"], "unlimited": unlimited}),
        ],
        "pairs": [Job("pairs", 37, "37_c12_pairs.sql", "pair tables of both freezes", params={**freezes, **weights})],
        "rest": [
            Job("cohorts", 38, "38_c12_cohorts.sql", "cohorts without user accounts and members of the u12 lists",
                params={"system_first": first, "system_last": last},
                allow=("u12_cohort_tobs", "u12_cohort_t1", "u12_labels_w0", "u12_labels_w1")),
            Job("proxies", 38, "38_c12_proxies.sql", "same-window proxies from the transfers between contracts",
                params={"start_ts": w["tobs_start"], "anchor_ts": w["tobs"]}),
            Job("labels_w0", 39, "39_c12_label_parts.sql", "W0 label parts by account class",
                params={"start_ts": w["t1_start"], "t1": h["score_end"], "out_start": h["outcome_start"],
                        "out_end": h["outcome_end"]},
                subs={"TAG": "w0", "FREEZE": "t1", "APPROVALS": "u12_approvals_t1", "TRANSFERS": "u12_transfers_t1",
                      "SEEN": "u12_transfers_t1", "LOGS": "logs_obs"},
                allow=("u12_allow_triples_t1", "u12_approvals_t1", "u12_transfers_t1", "logs_obs", "u_tokens")),
            Job("labels_w1", 39, "39_c12_label_parts.sql", "W1 label parts by account class",
                params={"start_ts": w["tobs_start"], "t1": r["score_end"], "out_start": r["outcome_start"],
                        "out_end": r["outcome_end"]},
                subs={"TAG": "w1", "FREEZE": "tobs", "APPROVALS": "u12_approvals_w1",
                      "TRANSFERS": "u12_transfers_w1", "SEEN": "u12_transfers_tobs", "LOGS": "logs_w1"},
                allow=("u12_allow_triples_tobs", "u12_approvals_w1", "u12_transfers_w1", "u12_transfers_tobs",
                       "logs_w1", "u_tokens")),
            Job("node_ids", 40, "40_c12_export_ids.sql", "node ids and export tables"),
            Job("importance", 41, "41_c12_importance.sql", "importance, untyped inflow and allowance description",
                params={**freezes, "dust_digits": dust, "cap_user": repr(float(c["cap_user_usd"])),
                        "min_usd": repr(float(disc["min_usd_account"])), "unlimited": unlimited,
                        "cap_allowance": repr(float(c["cap_allowance_usd"]))},
                allow=("u_tokens", "u_prices")),
        ],
        "checks": [Job("checks", 42, "42_c12_checks.sql", "invariants of the gate B tables",
                       params={**freezes, "dust_digits": dust, "system_first": first, "system_last": last},
                       allow=("u_tokens", "u_prices", "u12_cohort_tobs", "u12_cohort_t1", "u12_labels_w0",
                              "u12_labels_w1"))],
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
                table, factor, extra = term.table, 1, 0
                if rows.get(table) is None and table in bound:
                    b = bound[table]
                    table, factor, extra = (b, 1, 0) if isinstance(b, str) else b
                if rows.get(table) is None:
                    missing.add(table)
                else:
                    total += max(MIN_TABLE, (factor * int(rows[table]) + extra) * term.width)
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


def priced_rows(rows: int | None, nbytes: int | None) -> int | None:
    """The rows of c12_logs5 or c12_events_cc with a usd value, from the table's logical bytes: every column but usd
    has a fixed size (LOGS5_ALL - NUM = 109 bytes a row: BYTES(20) 22, a one-letter STRING 3, the rest 8) and usd adds
    NUM bytes where it is not NULL (BigQuery counts a NULL as 0 bytes); None unless that gives an exact count."""
    if rows is None or nbytes is None:
        return None
    extra = int(nbytes) - int(rows) * (LOGS5_ALL - NUM)
    if extra < 0 or extra % NUM or extra // NUM > rows:
        return None
    return extra // NUM


def projected_rows(meta: dict[str, dict | None], m: dict) -> dict[str, int] | None:
    """Upper bounds of the rows of the gate B tables that do not exist yet, from tables that do (revision section 12
    and its gate B amendment): with N rows of c12_events_cc, T* of them with a usd value and A* = N - T* (A rows with
    the T rows without a price), and the pilot's t1 pairs (S_c capped, S_u uncapped, S_t transfer, self-pairs
    included): triples <= min(A*, 5 S_u) + A*, capped pairs <= S_c + A*, uncapped <= S_u + A*, transfer pairs <= S_t
    + min(T*, rows(c12_pairs5)), user events <= rows(c12_logs5) - N, nodes <= rows(c12_contracts), importance rows
    <= 2 rows(c12_contracts) + 2. Without an exact count of the priced rows of both c12_events_cc and c12_logs5, A*
    and T* are both N. The keys _n_events_cc, _priced_rows (None without an exact count) and _a_rows_bound report
    the inputs. None while c12_events_cc or another input does not exist."""
    rows = {k: (v["rows"] if v else None) for k, v in meta.items()}
    need = ("c12_events_cc", "c12_logs5", "c12_pairs5", "c12_contracts", *U12_LISTS)
    if any(rows.get(k) is None for k in need):
        return None
    n = rows["c12_events_cc"]
    t = priced_rows(n, (meta["c12_events_cc"] or {}).get("bytes"))
    if t is None or priced_rows(rows["c12_logs5"], (meta["c12_logs5"] or {}).get("bytes")) is None:
        t = None                     # the logical sizes are not those assumed: count every row on both sides
    a, t = (n, n) if t is None else (n - t, t)
    st = (m.get("results") or {}).get("structure") or {}
    lay, loop = st.get("layers") or {}, st.get("self_pairs") or {}
    s = {k: int(lay.get(k, 0)) + int(loop.get(k, 0)) for k in ("allow_capped", "allow_uncapped", "transfer")}
    p5, c = rows["c12_pairs5"], rows["c12_contracts"]
    tri_t1 = min(a, 5 * s["allow_uncapped"]) if lay else a
    cap = (s["allow_capped"] if lay else tri_t1) + a
    unc = (s["allow_uncapped"] if lay else tri_t1) + a
    tp = (s["transfer"] if lay else min(t, p5)) + min(t, p5)
    members = sum(rows[k] for k in U12_LISTS)
    bounds = {"c12_allow_triples": tri_t1 + a, "c12_user_events": rows["c12_logs5"] - n, "c12_constants": 1,
              "c12_transfer_pairs": tp, "c12_allow_pairs": cap, "c12_allow_pairs_unc": unc,
              "c12_cohort_tobs": rows["u12_cohort_tobs"], "c12_cohort_t1": rows["u12_cohort_t1"],
              "c12_members": members, "c12_proxies_tobs": rows["u12_cohort_tobs"],
              "c12_label_parts_w0": rows["u12_labels_w0"], "c12_label_parts_w1": rows["u12_labels_w1"],
              "c12_x_label_split_w0": rows["u12_labels_w0"], "c12_x_label_split_w1": rows["u12_labels_w1"],
              "c12_nodes": c, "c12_x_nodes": c, "c12_x_members": members,
              "c12_x_allow_pairs_tobs": cap, "c12_x_allow_pairs_t1": cap, "c12_x_allow_pairs_unc_tobs": unc,
              "c12_x_allow_pairs_unc_t1": unc, "c12_x_transfer_pairs_tobs": tp, "c12_x_transfer_pairs_t1": tp,
              "c12_importance_raw": 2 * c + 2, "c12_importance_tobs": c, "c12_importance_t1": c,
              "c12_inflow_untyped_tobs": 1, "c12_inflow_untyped_t1": 1, "c12_describe_allowances": 10}
    out = {k: int(v) for k, v in bounds.items() if rows.get(k) is None}
    out["_n_events_cc"], out["_priced_rows"], out["_a_rows_bound"] = n, (None if t == n and a == n else t), a
    return out


def gate_b_keys(cfg: dict, start: str | None = None) -> list[str]:
    """The job keys of the gate B steps, from the step ``start`` on (all of them without it)."""
    js = jobs(cfg)
    steps = [s for s in GATE_B if s in js]
    steps = steps[steps.index(start):] if start in steps else ([] if start else steps)
    return [j.key for s in steps for j in js[s]]


# In closed form, with every proportional read above its 10 MB floor and the gate A tables at their rows
# (c12_logs5 1,240,275,042, c12_ends 25,537,280, c12_rpc_queue 6,230,270, c12_tx_senders 17,477,779, c12_pairs5
# 73,058,133), the projection of all the gate B jobs is within 0.1 GB of
#     245,368,823,448 + 246 N + 130 UE + 382 TR + 426 AP + 394 APU + 410 TP + 120 BAL + 1,214 C + 173 UA + 104 ST
# bytes: N, UE, TR, AP, APU and TP the rows of c12_events_cc and the bounds of c12_user_events, c12_allow_triples,
# c12_allow_pairs, c12_allow_pairs_unc and c12_transfer_pairs; BAL, C, UA and ST the rows of c12_bal, c12_contracts,
# c12_user_accounts and c12_struct_t1. The constant is the fixed reads of user_events (136,410,442,756), the two
# measured terms of job 39 (103,623,426,048), the read of c12_pairs5 by job 42 (73,058,133 x 68 = 4,967,953,044) and
# 35 reads at the floor (367,001,600).
def gate_b_projection(meta: dict[str, dict | None], m: dict, keys: list[str]) -> dict:
    """The estimates of the gate B jobs ``keys`` with every table they read that does not exist yet at its bound
    (projected_rows), their sum in bytes and US dollars; complete is False while a table they read has neither rows
    nor a bound."""
    bounds = projected_rows(meta, m)
    if bounds is None:
        return {"complete": False, "missing": ["c12_events_cc and the other tables of job 31"], "usd": None}
    rows = {k: (v["rows"] if v else None) for k, v in meta.items()}
    est = estimates({**rows, **{k: v for k, v in bounds.items() if not k.startswith("_")}})
    sub = {k: est[k] for k in keys}
    missing = sorted({t for e in sub.values() for t in e.missing})
    whole = sum(e.whole for e in sub.values())
    return {"complete": not missing, "missing": missing, "bounds": bounds,
            "jobs": {k: {"first": e.first, "whole": e.whole} for k, e in sub.items()},
            "bytes": whole, "usd": round(usd(whole), 4)}


def over_cap(projected: float, campaign: float, spent: float, budget: float) -> list[str]:
    """What a projected cost would pass: the campaign cap with the campaign so far, the budget with the ledger."""
    return ([f"with the campaign so far (USD {campaign:.2f}) it passes the cap of USD {CAP_USD:.2f}"]
            if campaign + projected > CAP_USD else []) + \
           ([f"with the ledger (USD {spent:.2f}) it passes the budget of USD {budget:.2f}"]
            if spent + projected > budget else [])


def cents_needed(total: float) -> float:
    """``total`` rounded up to the cent, math.ceil(total * 100 - 1e-9) / 100: the least amount in whole cents that
    ``total`` does not pass in the comparison of over_cap (a float sum just above a whole cent takes the next one)."""
    need = math.ceil(total * 100 - 1e-9) / 100
    while total > need:
        need = round(need + 0.01, 2)
    return need


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


def uncommitted(files=None) -> list[str]:
    """The files (COMMITTED by default) that are missing, have local changes or were never committed."""
    files = COMMITTED if files is None else files
    return [rel for rel in files
            if not (ROOT / rel).exists() or git("status", "--porcelain", "--", rel)
            or not git("log", "-1", "--format=%H", "--", rel)]


def inputs(dry: bool, gate_b: bool = False) -> dict:
    """Refuse unless every file in COMMITTED (and, for a gate B step, in COMMITTED_B) is committed without local
    changes; a dry run of a gate A step only warns, a gate B step refuses whether it is a dry run or not."""
    files = COMMITTED + COMMITTED_B if gate_b else COMMITTED
    bad = uncommitted(files)
    if bad:
        msg = "not committed without local changes: " + ", ".join(bad)
        if not dry or gate_b:
            raise SystemExit("refused: " + msg)
        print("warning:", msg)
    return {
        "head": git("rev-parse", "HEAD"),
        "revision_commit": git("log", "--diff-filter=A", "-1", "--format=%H %cI", "--", COMMITTED[0]),
        "sha256": {rel: sha256(ROOT / rel) if (ROOT / rel).exists() else None for rel in files},
    }


def manifest() -> dict:
    return load_json(MANIFEST) if MANIFEST.exists() else {"variant": VARIANT, "steps": [], "jobs": [], "results": {}}


def prerequisites(step: str, m: dict) -> list[str]:
    """What ``step`` still waits for in the manifest ``m`` (nothing: it may run). Every step of CHAIN needs a last
    check without problems (check is the first step of gate A, revision section 12) and a last run that passed of
    each step of CHAIN before it, those last runs in the order of CHAIN (a step run again after a later step makes
    the later one stale). Of the checks only the outcome of the last one counts, not when it ran: a check run again
    does not make subset or the steps after it stale. Of the waits of a gate B step, gate_a_decision takes out those
    that decisions taken before gate B cover."""
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


# What a step waits for after a structure run that did not pass (prerequisites).
STRUCTURE_NOT_PASSED = "a run of structure that passes (the last one did not)"


def gate_a_decision(waits: list[str], m: dict, fixed: dict) -> tuple[list[str], dict | None]:
    """Split the waits of a gate B step (prerequisites) into those that decisions taken before gate B already cover
    and the rest (revision section 13, amendment of 9 November 2026: jobs 32 to 34 and 43 are not run again after
    job 31, and the run goes on after the stop of the structure pilot). The last structure run covers the waits it
    recorded in waited_for under an author_decision. 'Protocol fixed' with an author_decision (``fixed``, from
    check_fixed) covers the wait for a structure run that passes, since gate_b_ready checked that it pins the pilot
    of that run. They cover them only while that run is the last of gate A: it recorded its result (so the pilot is
    its own), no step of gate A ran after it, and, for the wait for a check, no check ran after it started (a check
    that cannot be placed in time counts as later). Returns the waits left, which still need --author-decision, and
    the record for the manifest (None when no wait is covered): the index of that structure entry in the steps, its
    started_at and the waits covered, in the order of prerequisites."""
    runs = [i for i, e in enumerate(m["steps"]) if e["step"] == "structure"]
    if not waits or not runs:
        return waits, None
    j = runs[-1]
    entry = m["steps"][j]
    if "passed" not in entry or any(e["step"] in CHAIN_A for e in m["steps"][j + 1:]):
        return waits, None
    recorded = set(entry.get("waited_for") or []) if entry.get("author_decision") else set()
    started, checks = entry.get("started_at"), m.get("checks_run") or []
    check_since = bool(checks) and not (started and checks[-1].get("at")
                                        and utc_time(checks[-1]["at"]) <= utc_time(started))

    def covered(wait: str) -> bool:
        if wait == STRUCTURE_NOT_PASSED:
            return bool(fixed.get("author_decision"))
        return wait in recorded and not (check_since and wait.startswith("a check without problems"))

    took = [w for w in waits if covered(w)]
    if not took:
        return waits, None
    return [w for w in waits if not covered(w)], {"structure_index": j, "structure_started_at": started,
                                                   "waited_for": took}


def gate_a_note(step: str, decided: dict) -> str:
    """The line that a gate B step prints for the waits that decisions taken before gate B cover."""
    by = []
    if set(decided["waited_for"]) - {STRUCTURE_NOT_PASSED}:
        by.append(f"the author's decision of the last structure run (steps[{decided['structure_index']}] of the run "
                  f"manifest, started at {decided['structure_started_at']})")
    if STRUCTURE_NOT_PASSED in decided["waited_for"]:
        by.append("the author_decision of 'Protocol fixed' on its pilot")
    return (f"note: {step} waits for " + "; ".join(decided["waited_for"]) + ", which decisions taken before gate B "
            f"cover ({' and '.join(by)}); the run manifest records them as a gate A decision (gate_a_decision), not "
            "as taken after gate B")


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


# --------------------------------------------------------------------------- gate B refusals


def protocol_fixed_block() -> dict | None:
    """The object of the section 'Protocol fixed' of docs/discovery_protocol.md, or None while it holds none."""
    import run_discovery as rd
    return rd.protocol_fixed(PROTOCOL)


def refuse_gate_a_again(step: str) -> None:
    """A gate A step from subset to structure does not run again once 'Protocol fixed' holds a block: gate B, which
    pins the structure pilot, comes after them (revision section 12)."""
    if step in CHAIN_A and protocol_fixed_block() is not None:
        raise SystemExit(f"refused: {step} is a gate A step, and docs/discovery_protocol.md holds 'Protocol fixed': "
                         "no step from subset to structure runs again after gate B "
                         "(docs/revision_contract_graph.md section 12)")


def gate_b_ready(cfg: dict) -> tuple[dict, dict]:
    """Refuse a gate B step unless 'Protocol fixed' passes run_discovery.check_fixed in full and pins the pilot that
    the last structure run wrote, the file on disk being that pilot (also when 'Protocol fixed' carries an
    author_decision); return check_fixed's result and the record for the manifest."""
    import run_discovery as rd
    block = rd.protocol_fixed(PROTOCOL)
    fixed = rd.check_fixed(block, FEASIBILITY, ROOT, cfg.get("discovery"))
    rec = (((manifest().get("results") or {}).get("structure") or {}).get("feasibility") or {})
    if not rec.get("sha256"):
        raise SystemExit("refused: the run manifest records no pilot written by the structure step "
                         "(results.structure.feasibility); gate B pins that pilot (docs/revision_contract_graph.md "
                         "section 12)")
    if rec.get("path") != FEASIBILITY_REL or not (fixed["pinned_sha256"] == fixed["feasibility_sha256"]
                                                  == str(rec["sha256"]).lower()):
        raise SystemExit(f"refused: 'Protocol fixed' pins {fixed['pinned_sha256'][:12]}, {FEASIBILITY_REL} on disk "
                         f"is {fixed['feasibility_sha256'][:12]} and the structure step wrote "
                         f"{str(rec['sha256'])[:12]} at {rec.get('path')}; gate B runs only on the pilot of the "
                         "structure step")
    record = {"date": fixed["date"], "pinned_sha256": fixed["pinned_sha256"], "rho": block["rho"], "q": block["q"],
              "primary_mode": fixed["primary_mode"], "author_decision": fixed["author_decision"],
              "decision_covers": fixed.get("decision_covers"),
              "sizes": fixed["sizes"]}
    return fixed, record


def committed_hash(rel: str) -> str:
    """The last commit that touched ``rel`` ('' if none did)."""
    return git("log", "-1", "--format=%H", "--", rel)


def refuse_constants_again() -> None:
    """The constants are computed once: the constants step refuses, a dry run too, once constants.json is
    committed."""
    h = committed_hash(CONSTANTS_REL)
    if h:
        raise SystemExit(f"refused: {CONSTANTS_REL} is committed ({h[:12]}); the constants are computed once, and the "
                         "constants step does not run again (docs/revision_contract_graph.md section 7)")


def constants_problems(m: dict) -> list[str]:
    """What keeps the constants of the constants step from being committed on their own: the file is missing, is
    not the one the last passing run of constants wrote, has local changes or is not committed, or its commit does
    not hold exactly the files of CONSTANTS_COMMIT (the constants, the run manifest and the ledger)."""
    path = ROOT / CONSTANTS_REL
    if not path.exists():
        return [f"{CONSTANTS_REL} is missing; run the 'constants' step first"]
    out = []
    last = next((e for e in reversed(m["steps"]) if e["step"] == "constants"), None)
    rec = (m.get("results") or {}).get("constants") or {}
    if last is None or last.get("passed") is not True or not rec.get("constants_sha256"):
        out.append("the last run of constants did not pass")
    elif rec["constants_sha256"] != sha256(path):
        out.append(f"{CONSTANTS_REL} is not the file the last run of constants wrote")
    h = committed_hash(CONSTANTS_REL)
    if git("status", "--porcelain", "--", CONSTANTS_REL) or not h:
        out.append(f"{CONSTANTS_REL} has local changes or is not committed")
    else:
        prefix = git("rev-parse", "--show-prefix")
        files = set(git("diff-tree", "--no-commit-id", "--name-only", "-r", h).splitlines())
        allowed = {prefix + rel for rel in CONSTANTS_COMMIT}
        if files != allowed:
            out.append(f"the commit {h[:12]} that holds {CONSTANTS_REL} must hold exactly it, {MANIFEST_REL} and "
                       f"{LEDGER_REL}: missing {sorted(allowed - files)}, extra {sorted(files - allowed)}; commit "
                       "the constants on their own with the run manifest and the ledger (precedent 77a1e49)")
    return out


def committed_constants(m: dict, dry: bool) -> tuple[dict | None, dict | None]:
    """The constants of constants.json and their record (path, SHA-256, commit) once they are committed on their
    own; before that a gate B step refuses, and its dry run warns and returns (None, None) for the placeholders."""
    problems = constants_problems(m)
    if problems:
        msg = "the constants must be committed on their own before this step: " + "; ".join(problems)
        if not dry:
            raise SystemExit("refused: " + msg)
        print("warning:", msg, "(the dry run takes placeholder constants)")
        return None, None
    return load_json(ROOT / CONSTANTS_REL), {"path": CONSTANTS_REL, "sha256": sha256(ROOT / CONSTANTS_REL),
                                             "commit": committed_hash(CONSTANTS_REL)}


def utc_time(iso: str) -> datetime:
    """A full ISO time as an aware datetime (UTC when it names no offset), so that times compare as times."""
    t = datetime.fromisoformat(str(iso))
    return t if t.tzinfo else t.replace(tzinfo=timezone.utc)


def source_problems(meta: dict[str, dict | None], calibrated: tuple[str, ...] = ()) -> list[str]:
    """The source tables of the metadata ``meta`` that do not exist, were modified on SOURCES_BEFORE or later, or
    expire; and, of the tables named in ``calibrated`` (CALIBRATED for the check and for rest and checks), those
    modified after CALIBRATED_AT, the first bill that calibrates the measured terms of job 39 (full ISO times
    compared). Each table is named once."""
    out, at = [], utc_time(CALIBRATED_AT)
    for name, v in meta.items():
        if v is None:
            out.append(f"the source table {name} does not exist")
        elif v["modified"][:10] >= SOURCES_BEFORE or v["expires"]:
            out.append(f"{name} was modified on {v['modified'][:10]} or expires")
        elif name in calibrated and utc_time(v["modified"]) > at:
            out.append(f"{name} was modified at {v['modified']}, after the first bill that calibrates job 39, at "
                       f"{CALIBRATED_AT}")
    return out


def refuse_projected_cap(client, ds: str, m: dict, step: str, cfg: dict) -> dict | None:
    """Refuse a gate B step when the campaign and the projection of the gate B jobs from this step on would pass
    the cap, or the ledger and that projection the budget; no decision passes it. Returns the projection for the
    manifest (None for a step without jobs)."""
    keys = gate_b_keys(cfg, step)
    if not keys:
        return None
    proj = gate_b_projection(table_meta(client, ds, ESTIMATE_TABLES), m, keys)
    if not proj["complete"]:
        raise SystemExit(f"refused: no projection of the gate B jobs from {step} on: {proj['missing']} have no rows")
    camp, spent = campaign_usd(), sum(j.get("usd", 0.0) for j in ledger_jobs())
    budget = float(cfg["bigquery"]["budget_usd"])
    over = over_cap(proj["usd"], camp, spent, budget)
    if over:
        raise SystemExit(f"refused: the gate B jobs from {step} on are projected at up to USD {proj['usd']:.2f} (their "
                         "estimates with every table made inside gate B at its upper bound); " + "; ".join(over) +
                         ". The cap is set in the gate B commit (docs/revision_contract_graph.md sections 12 and 13), "
                         "and no decision passes it")
    return {"usd": proj["usd"], "campaign_usd": round(camp, 4), "ledger_usd": round(spent, 4),
            "jobs": proj["jobs"], "bounds": proj["bounds"]}


class Run:
    """One step: its jobs go through run_bq.py, and the manifest records them. It does not start while the steps
    before it have not all passed (prerequisites), unless the author decided otherwise: for a gate B step, the
    decisions taken before gate B may already cover some of the waits (gate_a_decision), and only the others need
    --author-decision, which the manifest marks after_gate_b. A gate A step from subset to structure does not start
    once the protocol is fixed. A gate B step starts only when the protocol is fixed on the structure pilot, its
    files are committed, the constants are committed on their own (from pairs on) and the projection of the gate B
    jobs stays within the cap and the budget; no decision passes these."""

    def __init__(self, step: str, cfg: dict, dry: bool):
        self.step, self.cfg, self.dry = step, cfg, dry
        refuse_gate_a_again(step)
        self.fixed = self.fixed_record = self.constants = self.constants_record = self.projection = None
        gate_b = step in GATE_B
        if gate_b:
            self.fixed, self.fixed_record = gate_b_ready(cfg)
            if step == "constants":
                refuse_constants_again()
            else:
                self.constants, self.constants_record = committed_constants(manifest(), dry)
        self.client, self.ds = client_and_dataset(cfg)
        self.inputs = inputs(dry, gate_b=True) if gate_b else inputs(dry)
        if step in ("rest", "checks"):
            problems = source_problems(table_meta(self.client, self.ds, SOURCES + SOURCES_B), CALIBRATED)
            if problems:
                raise SystemExit("refused: " + "; ".join(problems) + " (the gate B jobs read these tables as they "
                                 "were; job 39 is estimated from the bills of the twelve-month label jobs on them)")
        self.m = manifest()
        if gate_b and not dry:
            self.projection = refuse_projected_cap(self.client, self.ds, self.m, step, cfg)
        waits, decided = prerequisites(step, self.m), None
        if gate_b:
            waits, decided = gate_a_decision(waits, self.m, self.fixed)
            if decided:
                print(gate_a_note(step, decided))
        if waits:
            msg = f"{step} waits for " + "; ".join(waits)
            if dry or AUTHOR_DECISION:
                print(f"warning: {msg}" + ("" if dry else f"; going on by the author's decision: {AUTHOR_DECISION}"))
                if gate_b and not dry:
                    print("note: this decision is taken after gate B; the run manifest marks it (after_gate_b), the "
                          "change record (_change-record-contract-graph.md) must name it; the later publish step "
                          "lists it; the revision does not change")
            else:
                raise SystemExit(f"refused: {msg} (the steps run in the order of STEPS; --author-decision TEXT goes "
                                 "on all the same and is recorded)")
        if not dry:
            entry = {"step": step, "started_at": now(), **self.inputs}
            if gate_b:
                entry["gate_b"] = {"protocol_fixed": self.fixed_record, "constants": self.constants_record,
                                   "projection": self.projection}
            if decided:
                entry["gate_a_decision"] = decided
            if waits:
                entry.update(waited_for=waits, author_decision=AUTHOR_DECISION)
                if gate_b:
                    entry["after_gate_b"] = True
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
        for job in jobs(self.cfg, self.constants)[step]:
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


def print_projection(proj: dict, numbers: dict[str, int], campaign: float, spent: float, budget: float) -> None:
    """The projection of the gate B jobs not yet run, as the check step prints it; whenever the logical bytes give no
    exact count of the priced rows, a line says that the projection falls back to the loose bound. A complete
    projection ends with the lines 'cap needed' and 'budget needed': the campaign and the ledger with the projection,
    rounded up to the cent (cents_needed), within or above the cap and the budget as over_cap judges them."""
    b = proj.get("bounds") or {}
    fallback = ("projection: fallback (no exact priced-row count): each of the "
                f"{b.get('_n_events_cc', 0):,} rows of c12_events_cc counts as an A row and as a transfer with a usd "
                "value, a loose bound")
    if not proj["complete"]:
        if b and b["_priced_rows"] is None:
            print(fallback)
        print("projection: waits for " + ", ".join(proj["missing"]))
        return
    print("projection of the gate B jobs not yet run (the tables they make at their upper bounds):")
    if b["_priced_rows"] is None:
        print("  " + fallback)
    else:
        print(f"  c12_events_cc {b['_n_events_cc']:,} rows, {b['_priced_rows']:,} with a usd value (logical bytes); A "
              f"rows at most {b['_a_rows_bound']:,}")
    print("  bounds: " + ", ".join(f"{k} <= {v:,}" for k, v in b.items() if not k.startswith("_")))
    print(f"{'job':<15}{'no':>4}{'first GB':>11}{'whole GB':>11}{'USD':>8}")
    for key, e in proj["jobs"].items():
        print(f"{key:<15}{numbers[key]:>4}{e['first']/1e9:>11.1f}{e['whole']/1e9:>11.1f}{usd(e['whole']):>8.3f}")
    print(f"gate B projected: {proj['bytes']/1e9:,.1f} GB, USD {proj['usd']:.3f}; campaign USD {campaign:.2f} + "
          f"{proj['usd']:.2f} = {campaign + proj['usd']:.2f} of {CAP_USD:.2f}; ledger USD {spent:.2f} + "
          f"{proj['usd']:.2f} = {spent + proj['usd']:.2f} of {budget:.0f}")
    # The cap and the budget that the unrounded sums need, in whole cents, each judged within or above exactly as
    # over_cap judges it: the gate B amendment of revision section 13 sets the cap from these two lines.
    cap_sum, budget_sum = campaign + proj["usd"], spent + proj["usd"]
    print(f"cap needed: USD {cents_needed(cap_sum):.2f} ({'above' if cap_sum > CAP_USD else 'within'} the cap of USD "
          f"{CAP_USD:.2f})")
    print(f"budget needed: USD {cents_needed(budget_sum):.2f}, {'above' if budget_sum > budget else 'within'} the "
          f"budget of USD {budget:g}")


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
    meta = table_meta(client, ds, SOURCES + SOURCES_B)
    problems += source_problems(meta, CALIBRATED)
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
    emeta = table_meta(client, ds, ESTIMATE_TABLES)
    rows = {k: (v["rows"] if v else None) for k, v in emeta.items()}
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
    # The gate A jobs not yet run against the cap and the budget by their known estimates; the gate B jobs are judged
    # by the projection below alone, which only warns until 'Protocol fixed' holds a block.
    gate_b = set(gate_b_keys(cfg))
    problems += cap_problems({k: e for k, e in est.items() if k not in gate_b}, camp, spent, budget, done)
    # Gate B: the projection of the gate B jobs not yet run, which the check makes for free before the gate B commit,
    # and whether the protocol is fixed; once it is, a projection above the cap or the budget is a problem.
    try:
        block, unreadable = protocol_fixed_block(), None
    except SystemExit as exc:
        block, unreadable = None, str(exc).removeprefix("refused: ")
        problems.append(f"docs/discovery_protocol.md: {unreadable}")
    proj = gate_b_projection(emeta, m, [k for k in gate_b_keys(cfg) if k not in done])
    print_projection(proj, numbers, camp, spent, budget)
    if proj["complete"]:
        over = over_cap(proj["usd"], camp, spent, budget)
        if over:
            msg = f"the gate B jobs not yet run are projected at up to USD {proj['usd']:.2f}; " + "; ".join(over)
            if block is not None:
                problems.append(msg)
            else:
                print(f"warning: {msg}; the gate B commit sets the cap (docs/revision_contract_graph.md sections 12 "
                      "and 13)")
    fixed = None if block is None else {"date": block.get("date"), "pinned_sha256": block.get("sha256")}
    if unreadable:
        print(f"gate B: {unreadable}")
    elif fixed is None:
        print("gate B: docs/discovery_protocol.md holds no 'Protocol fixed' block yet")
    else:
        print(f"gate B: 'Protocol fixed' of {fixed['date']} pins {str(fixed['pinned_sha256'])[:12]}")
    if preview:
        print(f"not recorded in {MANIFEST.name}: the files above are not committed (a preview before gate A)")
    else:
        m.setdefault("checks_run", []).append({
            "at": now(), "head": git("rev-parse", "HEAD"), "problems": problems, "ledger_usd": round(spent, 4),
            "campaign_usd": round(camp, 4), "existing_c12": existing, "waits": waits,
            "estimates": {k: {"first": e.first, "whole": e.whole, "missing": list(e.missing)} for k, e in est.items()},
            "projection": proj, "gate_b": {"protocol_fixed": fixed}})
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


def extension_counts(types) -> dict[str, int]:
    """The typed contracts that the lists of the amendment of 9 November 2026 move (revision section 13), by list,
    and the typed contracts they leave (contracts_after)."""
    moved = smart_account_extension(types)
    contract = types["account_class"].astype(str) == "contract"
    by_hash = moved & types["code_hash"].fillna("").astype(str).str.lower().isin(SMART_ACCOUNT_CODE_HASHES)
    return {"typed_contracts": int(contract.sum()), "moved": int(moved.sum()), "moved_by_code_hash": int(by_hash.sum()),
            "moved_by_implementation": int((moved & ~by_hash).sum()), "contracts_after": int((contract & ~moved).sum())}


def typed_extension(m: dict) -> tuple[dict | None, str]:
    """The counts of extension_counts on the typing output, with what keeps them from describing the table that job 30
    loaded (empty when nothing does): the parts must be on disk and must be the files of the last load (its
    source_sha256). Counts are None when the parts are missing."""
    paths = part_paths(TYPES)
    if not paths:
        return None, f"{TYPES.name} is not on disk"
    loaded = ((m.get("results") or {}).get("load") or {}).get("source_sha256") or {}
    on_disk = {p.name: sha256(p) for p in paths}
    if isinstance(loaded, dict) and loaded and loaded != on_disk:
        return None, f"the parts of {TYPES.name} on disk are not those job 30 loaded"
    ext = extension_counts(read_parts(TYPES, columns=["address", "account_class", "code_hash", "implementation"]))
    expected = {"moved_by_code_hash": SMART_ACCOUNT_TYPED["code_hashes"],
                "moved_by_implementation": SMART_ACCOUNT_TYPED["implementations"]}
    if any(ext[k] != v for k, v in expected.items()):
        return ext, f"the smart-account lists move {ext}, not {expected}"
    return ext, ""


def expected_sizes(previous: dict, ext: dict, sizes: dict) -> tuple[dict, bool]:
    """What job 31 must give, and whether ``sizes`` gives it. Moving an address from the contracts to the user
    accounts leaves their sum as it was, and the inputs of job 31 other than the lists do not change between its
    runs: so the last run (``previous``, with the counts it moved, 0 before the lists) fixes both sizes exactly.
    Without a last run, c12_contracts can hold no more than the typed contracts the lists leave."""
    if previous:
        before = int((previous.get("smart_account_extension") or {}).get("moved", 0))
        want = {"c12_contracts": previous["c12_contracts"] + before - ext["moved"],
                "c12_user_accounts": previous["c12_user_accounts"] - before + ext["moved"]}
        return want, all(sizes[k] == v for k, v in want.items())
    return {"c12_contracts": f"at most {ext['contracts_after']}"}, sizes["c12_contracts"] <= ext["contracts_after"]


def step_contracts(cfg: dict, dry: bool) -> None:
    # Once 'Protocol fixed' holds a block this gate A step refuses before anything else (revision section 12).
    refuse_gate_a_again("contracts")
    # The lists must move exactly the typed contracts the amendment of 9 November 2026 counts (common.
    # SMART_ACCOUNT_TYPED) in the typing output that job 30 loaded; checked before the step is recorded.
    m = manifest()
    ext, problem = typed_extension(m)
    if problem:
        if not dry:
            raise SystemExit(f"refused: {problem} (revision section 13, amendment of 9 November 2026)")
        print(f"skipped: the smart-account check ({problem})")
    else:
        print("smart-account extension (revision section 13, amendment of 9 November 2026):", ext)
    # The sizes of the last run that passed. A run that stopped before its result was recorded left the result as it
    # was; a run whose result was recorded without passing kept the result it replaced as 'previous'.
    previous = dict(m["results"].get("contracts") or {})
    recorded = [e for e in m["steps"] if e["step"] == "contracts" and "passed" in e]
    if recorded and recorded[-1]["passed"] is not True and "previous" in previous:
        previous = dict(previous["previous"] or {})
    run = Run("contracts", cfg, dry)
    run.run_jobs("contracts")
    if dry:
        return
    sizes = run.sizes("c12_contracts", "c12_user_accounts", "c12_events_cc")
    want, passed = expected_sizes(previous, ext, sizes)
    kept = {k: previous[k] for k in ("c12_contracts", "c12_user_accounts", "c12_events_cc", "smart_account_extension")
            if k in previous}
    run.result({**sizes, "smart_account_extension": ext, "expected": want, "previous": kept or None}, passed=passed)
    if not passed:
        raise SystemExit(f"stopped: job 31 gave {sizes}, not {want} (revision section 13, amendment of "
                         "9 November 2026)")


def lists_applied(m: dict) -> str:
    """Why the last run of contracts does not stand for the smart-account lists (empty when it does): it must have
    passed and must record the counts that the lists give on the typing output (the counts of 8 November 2026 had
    none). The structure step refuses without it, whatever the author's decision."""
    last = [e for e in m["steps"] if e["step"] == "contracts"]
    if not last or last[-1].get("passed") is not True:
        return "the last run of contracts did not pass"
    ext, problem = typed_extension(m)
    if problem:
        return problem
    if ((m.get("results") or {}).get("contracts") or {}).get("smart_account_extension") != ext:
        return "the last run of contracts was not made with the smart-account lists"
    return ""


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
    # Once 'Protocol fixed' holds a block this gate A step refuses before anything else (revision section 12).
    refuse_gate_a_again("structure")
    # Job 35 reads c12_events_cc, which job 31 builds: the structure must be that of the node set with the
    # smart-account lists (revision section 13, amendment of 9 November 2026). No author's decision passes this.
    why = lists_applied(manifest())
    if why:
        if not dry:
            raise SystemExit(f"refused: {why}; run contracts first (revision section 13, amendment of "
                             "9 November 2026)")
        print(f"warning: {why}")
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


def step_constants(cfg: dict, dry: bool) -> None:
    run = Run("constants", cfg, dry)
    run.run_jobs("constants")                      # triples, user_events, constants
    if dry:
        return
    rows = list_rows(run.client, run.ds, "c12_constants")
    sizes = run.sizes("c12_allow_triples", "c12_user_events", "c12_constants")
    if len(rows) != 1:
        run.result({"rows": sizes}, passed=False)
        raise SystemExit(f"stopped: c12_constants holds {len(rows)} rows, not one")
    if list(rows[0]) != list(CONSTANT_COLUMNS):
        run.result({"rows": sizes, "columns": list(rows[0])}, passed=False)
        raise SystemExit(f"stopped: c12_constants has the columns {list(rows[0])}, not CONSTANT_COLUMNS")
    raw = {k: (v if isinstance(v, int) or v is None else float(v)) for k, v in rows[0].items()}
    out, problems = constants_file(raw, cfg)
    if problems:
        run.result({"raw": raw, "problems": problems, "rows": sizes}, passed=False)
        raise SystemExit("stopped: the constants are not usable (" + "; ".join(problems) + "); nothing was written")
    path = ROOT / CONSTANTS_REL
    save_json(out, path)
    digest = sha256(path)
    run.result({"constants": {k: out[k] for k in CONSTANT_KEYS}, "path": CONSTANTS_REL, "constants_sha256": digest,
                "rows": sizes})
    print(json.dumps(out, indent=1))
    print(f"commit {CONSTANTS_REL}, {MANIFEST_REL} and {LEDGER_REL} on their own (precedent 77a1e49) before the "
          "pairs step; the constants step does not run again once the file is committed")


RULE = ("b = ln 3 / m with m the median rounded to two significant digits (usd.round_sig); U is the 99th percentile "
        "of the US-dollar values of the transfers between contracts and U_user that of the transfers from user "
        "accounts to contracts, both of the W0 score window and rounded to two significant digits; m_A is the median "
        "of the positive usd_eff of the latest allowances between contracts at t1, unlimited ones included "
        "(docs/revision_contract_graph.md section 7)")


def constants_file(raw: dict, cfg: dict) -> tuple[dict, list[str]]:
    """constants.json from the row of c12_constants (revision section 7): m_T, m_A, U and U_user rounded to two
    significant digits and b = ln 3 / m; with the problems that keep it from being written (a value that is not
    positive and finite, U_user below discovery.min_usd_account)."""
    w, g = windows(cfg), cfg["contract_graph"]
    names = {"m_transfer_usd": "m_transfer", "m_allowance_usd": "m_allowance", "cap_allowance_usd": "p99_transfer",
             "cap_user_usd": "p99_user_transfer"}
    vals, problems = {}, []
    for key, col in names.items():
        x = raw.get(col)
        v = round_sig(float(x)) if isinstance(x, (int, float)) and math.isfinite(float(x)) else None
        if v is None or not v > 0:
            problems.append(f"{col} = {x!r}")
        vals[key] = v
    floor = float(cfg["discovery"]["min_usd_account"])
    if not problems and vals["cap_user_usd"] < floor:
        problems.append(f"U_user = {vals['cap_user_usd']} is below discovery.min_usd_account = {floor}")
    if problems:
        return {}, problems
    return {
        "computed_at": now(),
        "source": "sql/36_c12_constants.sql (contract_rep.c12_constants): the transfers between contracts "
                  "(c12_events_cc), the latest allowances between contracts at t1 (c12_allow_triples, "
                  "sql/36_c12_allow_triples.sql) and the transfers from user accounts to contracts (c12_user_events, "
                  "sql/36_c12_user_events.sql) of the W0 score window",
        "window": [w["t1_start"], w["t1"]],
        "raw": raw,
        **vals,
        "b_transfer": slope_for_median(vals["m_transfer_usd"]),
        "b_allowance": slope_for_median(vals["m_allowance_usd"]),
        "unlimited_base_units": UNLIMITED_BASE_UNITS,
        "dust_token": float(g["balance"]["dust_token"]),
        "rule": RULE,
    }, []


def step_pairs(cfg: dict, dry: bool) -> None:
    run = Run("pairs", cfg, dry)
    run.run_jobs("pairs")
    if not dry:
        run.result({"rows": run.sizes("c12_transfer_pairs", "c12_allow_pairs", "c12_allow_pairs_unc")})


def rest_identities(sizes: dict[str, int], m: dict) -> dict[str, dict[str, int]]:
    """The rows each table of the rest step must have: the t1 export pairs those of the structure pilot (its pairs
    and self-pairs per layer), one proxies row per member of the T_obs cohort, one member row per row of the
    twelve-month lists, one label row per spender and one inflow row per freeze."""
    st = (m.get("results") or {}).get("structure") or {}
    lay, loop = st.get("layers") or {}, st.get("self_pairs") or {}

    def t1(layer: str) -> int:
        return int(lay.get(layer, 0)) + int(loop.get(layer, 0))

    pairs = {"c12_x_allow_pairs_t1": t1("allow_capped"), "c12_x_allow_pairs_unc_t1": t1("allow_uncapped"),
             "c12_x_transfer_pairs_t1": t1("transfer"), "c12_proxies_tobs": sizes["c12_cohort_tobs"],
             "c12_members": sum(sizes[k] for k in U12_LISTS), "c12_x_members": sizes["c12_members"],
             "c12_x_nodes": sizes["c12_nodes"], "c12_label_parts_w0": sizes["u12_labels_w0"],
             "c12_label_parts_w1": sizes["u12_labels_w1"], "c12_x_label_split_w0": sizes["c12_label_parts_w0"],
             "c12_x_label_split_w1": sizes["c12_label_parts_w1"], "c12_inflow_untyped_tobs": 1,
             "c12_inflow_untyped_t1": 1}
    return {k: {"expected": int(v), "actual": int(sizes[k])} for k, v in pairs.items()}


def step_rest(cfg: dict, dry: bool) -> None:
    run = Run("rest", cfg, dry)
    run.run_jobs("rest")                           # cohorts, proxies, labels_w0, labels_w1, node_ids, importance
    if dry:
        return
    sizes = run.sizes(*REST_TABLES)
    ident = rest_identities(sizes, run.m)
    off = {k: v for k, v in ident.items() if v["expected"] != v["actual"]}
    run.result({"rows": sizes, "identities": ident}, passed=not off)
    print("rest:", {k: v for k, v in sizes.items() if k.startswith(PREFIX)})
    if off:
        raise SystemExit(f"stopped: {sorted(off)} do not have their expected rows ({off}); the t1 rows must be the "
                         "structure pilot's pairs (docs/discovery_protocol.md section 8); sql/42 names the cause")


def step_checks(cfg: dict, dry: bool) -> None:
    run = Run("checks", cfg, dry)
    run.run_jobs("checks")
    if dry:
        return
    got = {r["check_name"]: (None if r["violations"] is None else int(r["violations"]))
           for r in list_rows(run.client, run.ds, "c12_checks")}
    names = sorted(set(got) ^ set(EXPECTED_CHECKS))
    failed = {k: v for k, v in got.items() if v != 0}
    run.result({"checks": got, "names_missing_or_unknown": names}, passed=not names and not failed)
    print("checks:", got)
    if names or failed:
        raise SystemExit(f"stopped: an invariant of sql/42 does not hold: {failed}"
                         + (f"; names missing or unknown: {names}" if names else ""))


def step_download(cfg: dict, dry: bool) -> None:
    run = Run("download", cfg, dry)
    cmds = [download(table, GRAPH / stem) for table, stem in DOWNLOADS]
    for cmd in cmds:
        print("$", " ".join(cmd[1:]), flush=True)
    if dry:
        return
    sizes = run.sizes(*(t for t, _ in DOWNLOADS))
    files = {}
    for (table, stem), cmd in zip(DOWNLOADS, cmds):
        sh(cmd)
        side = load_json(GRAPH / f"{stem}.json")
        if side.get("rows") != sizes[table] or side.get("table_rows") != sizes[table]:
            run.result({"files": files, "failed": stem}, passed=False)
            raise SystemExit(f"stopped: {stem}: {side.get('rows')} rows downloaded, {table} has {sizes[table]:,}")
        files[stem] = {"table": table, "rows": side["rows"],
                       "sha256": {p.name: sha256(p) for p in part_paths(GRAPH / stem)}}
    try:
        verify = verify_downloads(run.fixed)
    except SystemExit as exc:
        run.result({"files": files, "verify": str(exc)}, passed=False)
        raise SystemExit(f"stopped: the downloaded tables fail the reader's checks: {exc}") from None
    cohorts = cohort_summaries(cfg)
    run.result({"files": files, "verify": verify, "cohorts": cohorts}, passed=verify["passed"])
    if not verify["passed"]:
        raise SystemExit(f"stopped: the downloaded tables differ from the pinned pilot or from each other: {verify}")


def verify_downloads(fixed: dict) -> dict:
    """The downloaded tables as the discovery runner reads them: the t1 graph has the pinned pilot's sizes, union and
    bow-tie; the t1 rows are its pairs; importance and inflow pass the runner's reader checks; members agree with
    nodes."""
    import graphs
    import run_discovery as rd
    pilot = load_json(FEASIBILITY)
    sizes = rd.graph_sizes("t1")
    match = rd.match_pilot(sizes, fixed)  # refuses unless 'Protocol fixed' carries an author_decision without decision_covers
    union = {"nodes": pilot["union"]["nodes"], "edges": pilot["union"]["edges"], **pilot["bow_tie"]}
    union_match = {k: int(sizes[k]) == int(v) for k, v in union.items()}
    lay = pilot["layers"]
    expect = {"allow_pairs_t1": lay["allow_capped"], "allow_pairs_uncapped_t1": lay["allow_uncapped"],
              "transfer_pairs_t1": lay["transfer"]}
    t1_rows = {stem: {"expected": int(v["edges"]) + int(v["self_loops"]),
                      "actual": len(read_parts(GRAPH / stem, columns=["src"]))} for stem, v in expect.items()}
    nodes = graphs.load_nodes().sort_values("id")
    ids = nodes["id"].to_numpy(dtype="int64")
    out = {"t1_sizes": sizes, "pilot_match": match, "union_match": union_match, "t1_rows": t1_rows}
    for tag in ("tobs", "t1"):
        imp = read_parts(GRAPH / f"importance_{tag}")
        p = rd.importance_positions(ids, imp)            # stops on a bad table
        out[f"importance_{tag}"] = {"rows": int(len(imp)), "outside_g": int((p < 0).sum())}
        out[f"inflow_untyped_{tag}"] = rd.read_inflow_untyped(tag)
    mem = read_parts(GRAPH / "members")
    by_addr = set(nodes["address"].astype(str))
    contract = mem[mem["class"].astype(str) == "contract"]
    missing = sorted(set(contract["address"].astype(str)) - by_addr)
    flags = {"cohort_tobs": "is_cohort", "cohort_t1": "is_cohort_t1", "spenders_w0": "is_spender_w0",
             "spenders_w1": "is_spender_w1"}
    flag_off = {lst: int((nodes[col].astype(bool).to_numpy()
                          != nodes["address"].isin(set(contract.loc[contract["list"] == lst, "address"]))
                          .to_numpy()).sum()) for lst, col in flags.items()}
    out["members"] = {"contracts_without_node": missing[:20], "n_without_node": len(missing), "flags_off": flag_off}
    out["passed"] = (all(match.values()) and all(union_match.values()) and not missing
                     and all(v["expected"] == v["actual"] for v in t1_rows.values()) and not any(flag_off.values()))
    return out


def cohort_summaries(cfg: dict) -> dict:
    """PROC/cohort/{matched_cohort,cohort_t1,spenders_w0,spenders_w1}.json from the members table (revision section
    8): the members of each list by class and, for user accounts, by source; the cohort kept (the members that are
    not user accounts for the two cohorts, the contracts for the two spender lists) and its contracts with a node."""
    mem = read_parts(GRAPH / "members")
    nodes = set(read_parts(GRAPH / "nodes", columns=["address"])["address"].astype(str))
    names = {"cohort_tobs": "matched_cohort", "cohort_t1": "cohort_t1", "spenders_w0": "spenders_w0",
             "spenders_w1": "spenders_w1"}
    recs, kept = {}, {}
    for lst, name in names.items():
        g = mem[mem["list"].astype(str) == lst]
        cls = g["class"].astype(str)
        keep = g[cls != "user_account"] if lst.startswith("cohort") else g[cls == "contract"]
        kept[lst] = set(keep["address"].astype(str))
        recs[name] = {
            "rule": ("the members of u12_" + lst + " that are not user accounts" if lst.startswith("cohort")
                     else "the spenders of u12_labels_" + lst[-2:] + " that are contracts")
                    + " (docs/revision_contract_graph.md section 8)",
            "source": "contract_rep.c12_members (sql/38_c12_cohorts.sql)",
            "listed": int(len(g)), "by_class": {k: int(v) for k, v in cls.value_counts().sort_index().items()},
            "user_accounts_by_source": {k: int(v) for k, v in g.loc[cls == "user_account", "source"].astype(str)
                                        .value_counts().sort_index().items()},
            "cohort": int(len(keep)),
            "contracts": int((cls == "contract").sum()),
            "contracts_in_nodes": int(g.loc[cls == "contract", "address"].astype(str).isin(nodes).sum())}
    recs["cohort_t1"]["in_tobs_cohort"] = len(kept["cohort_t1"] & kept["cohort_tobs"])
    for name, rec in recs.items():
        save_json(rec, PROC / "cohort" / f"{name}.json")
    return {name: {k: rec[k] for k in ("listed", "by_class", "cohort", "contracts_in_nodes", "in_tobs_cohort")
                   if k in rec} for name, rec in recs.items()}


def preflight(steps: list[str], cfg: dict, dry: bool) -> None:
    """Refuse before any step runs whatever a step of ``steps`` would refuse at its start however the steps before it
    end: a gate A step once the protocol is fixed; a gate B step without the protocol fixed on the structure pilot or
    with a file of COMMITTED or COMMITTED_B not committed; constants once constants.json is committed; and, unless it
    is a dry run, a later gate B step without the constants committed on their own. So one invocation never runs
    only part of its steps for such a reason."""
    for s in steps:
        refuse_gate_a_again(s)
        if s in GATE_B:
            gate_b_ready(cfg)
            if s == "constants":
                refuse_constants_again()
            elif not dry:
                problems = constants_problems(manifest())
                if problems:
                    raise SystemExit(f"refused: {s} needs the constants committed on their own: "
                                     + "; ".join(problems))
    if any(s in GATE_B for s in steps):
        bad = uncommitted(COMMITTED + COMMITTED_B)
        if bad:
            raise SystemExit("refused: not committed without local changes: " + ", ".join(bad))


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
    cfg = load_config()
    preflight(args.steps, cfg, args.dry_run)
    for s in args.steps:
        globals()[f"step_{s}"](cfg, args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
