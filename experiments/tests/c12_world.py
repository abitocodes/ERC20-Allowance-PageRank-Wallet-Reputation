"""Shared helpers of the gate B tests of the contract-graph variant (CONTRACT_REP_VARIANT=contract12m).

Not a test module (pytest collects test_*.py only). The test files import it as ``c12_world`` (tests/ is on sys.path
under pytest); a subprocess first runs ``sys.path.insert(0, str(EXPERIMENTS / "tests"))``. Nothing here reads a path
of a variant at import: numpy, pandas and pyarrow are imported inside the functions that need them, the synthetic
tables are written with pyarrow in the layout of common.write_parts (``<stem>.partNNN.parquet``, zstd), and the only
project modules imported are run_discovery and common, by pilot_from_world (the pilot's own code and the
smart-account lists it applies), and common by the account types of the change node_listed_smart_account.

- INTERFACE and DOWNLOADS: the single copy of the INTERFACE of the gate B SQL (the 16 stems the driver's download
  step writes, describe_allowances included, with their columns and arrow types). Every synthetic table is written
  with it, the SQL tests compare it with sql/36-42 and the driver tests with run_contract12m_pipeline.DOWNLOADS.
- contract_world(): a synthetic contract12m world under ``exp/data``: the 16 gate B stems, the twelve-month cohorts
  and labels, the account types and, as its last write, the driver's run manifest with the SHA-256 of every
  downloaded part (so common.require_downloaded passes), clean or with one change of CHANGES; pilot_from_world(): the
  structure pilot of its t1 tables, computed by run_discovery.feasibility on the account types with the smart-account
  lists applied, as run_discovery.run_feasibility reads them; write_stem() and rehash(): a stem rewritten after the
  fact and the manifest's record of it; download_copy(): what download_table.py writes for one table.
- earlier_world(): what the six evaluation scripts read under the variants registered, usd and usd12m.
- sandbox(), snapshot(), run_script(), RECORDER, boots(): copies of experiments/{scripts,config,docs} (the worktree or
  the gate A commit d39775c, optionally a git repository of their own with an isolated configuration) and the
  recorder subprocess that runs an evaluation script in one and logs every paired bootstrap, score_all call and
  parquet read.
- bq_eval() and the SQL text helpers: an evaluator of the BigQuery scalar expressions of the cap (NULL semantics
  included) and the normalised text of the SQL files.
- earlier_path(), ALLOWED_CHANGES, code_path_differences(), project_imports(): the statements the earlier variants
  execute (CONTRACT_GRAPH = False, TRADERS = True), compared with those of d39775c.
"""

from __future__ import annotations

import ast
import functools
import hashlib
import json
import math
import operator
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

EXPERIMENTS = Path(__file__).resolve().parents[1]
SCRIPTS = EXPERIMENTS / "scripts"
SQL = EXPERIMENTS / "sql"
GATE_A = "d39775c"                                  # the gate A commit of the contract-graph revision
# The dated amendments of gate A made before gate B, in the order of their commits:
# - 52d3aa1, the amendment of revision section 4.3 of 8 November 2026, made during the reads (Stylus program errors
#   are the call's own failures): check_account_code.py, its tests and one paragraph of section 4.3;
# - caf97c3, the amendment of 9 November 2026 (revision section 13): the smart-account lists of rule 3(b) of
#   section 4.2 in common.py (SMART_ACCOUNT_CODE_HASHES, SMART_ACCOUNT_IMPLEMENTATIONS), applied by
#   sql/31_c12_contracts.sql (through the driver) and by the structure pilot of run_discovery.py, and the entry of
#   section 13 that lists them.
GATE_A_AMENDED = ("52d3aa1", "caf97c3")
STYLUS_AMENDMENT, SMART_ACCOUNT_AMENDMENT = GATE_A_AMENDED
SANDBOX_DIRS = ("scripts", "config", "docs")

# --------------------------------------------------------------------------- the INTERFACE of the gate B tables

PAIR6 = {"src": "int64", "dst": "int64", "n_tokens": "int64", "w_er": "double", "w_raw": "double", "max_sig": "double"}
TPAIR6 = {"src": "int64", "dst": "int64", "n_transfers": "int64", "w_awp": "double", "w_raw": "double",
          "max_sig": "double"}
LABELS = ("future_new_approvers", "future_revoke_count", "future_revoke_rate", "future_keep_rate",
          "future_revoke_value", "future_new_transfer_senders", "future_drain_owners")
RATES = {"future_revoke_rate", "future_keep_rate", "future_revoke_value"}      # the double columns among LABELS
PARTS = ("user", "contract", "other")                                         # suffixes of the label split
IMP = {"id": "int64", "address": "string", "i_t": "double", "i_a": "double", "n_t": "int64", "n_a": "int64"}
SPLIT = {"wallet": "string", "spender_class": "string", "n_t1": "int64",
         **{f"n_t1_{p}": "int64" for p in PARTS},
         **{f"{lab}_{p}": ("double" if lab in RATES else "int64") for lab in LABELS for p in PARTS}}
DESCRIBE = {"tag": "string", "token": "string",
            **{c: "int64" for c in ("n_latest_positive", "n_positive_eff", "n_capped_to_zero",
                                    "n_capped_below_allowance", "n_unlimited", "n_finite", "n_eff_at_or_above_cap",
                                    "n_allow_at_or_above_cap")},
            "sum_usd_eff": "double", "sum_usd_allow_finite": "double"}
PROXIES = {"wallet": "string", "in_degree": "int64", "in_value": "double", "inbound_counterparty_ratio": "double",
           "transfer_tenure_days": "double", "active_months": "int64", "inbound_tx": "int64",
           "inbound_unique": "int64"}
INTERFACE: dict[str, dict[str, str]] = {
    "nodes": {"id": "int64", "address": "string", "is_cohort": "bool", "is_cohort_t1": "bool",
              "is_spender_w0": "bool", "is_spender_w1": "bool"},
    "allow_pairs_tobs": {**PAIR6, "w_er_b10x": "double", "w_er_b01x": "double"},
    "allow_pairs_t1": PAIR6, "allow_pairs_uncapped_tobs": PAIR6, "allow_pairs_uncapped_t1": PAIR6,
    "transfer_pairs_tobs": {**TPAIR6, "w_awp_b10x": "double", "w_awp_b01x": "double"},
    "transfer_pairs_t1": TPAIR6,
    "importance_tobs": IMP, "importance_t1": IMP,
    "inflow_untyped_tobs": {"usd": "double"}, "inflow_untyped_t1": {"usd": "double"},
    "proxies_tobs": PROXIES,
    "label_split_w0": SPLIT, "label_split_w1": SPLIT,
    "members": {"list": "string", "address": "string", "class": "string", "source": "string"},   # source nullable
    "describe_allowances": DESCRIBE,
}
NULLABLE = {("members", "source")}                  # every other INTERFACE column is NOT NULL
# The BigQuery table of each downloaded stem, in the order of run_contract12m_pipeline.DOWNLOADS.
DOWNLOADS: dict[str, str] = {
    "c12_x_nodes": "nodes",
    "c12_x_allow_pairs_tobs": "allow_pairs_tobs", "c12_x_transfer_pairs_tobs": "transfer_pairs_tobs",
    "c12_x_allow_pairs_t1": "allow_pairs_t1", "c12_x_transfer_pairs_t1": "transfer_pairs_t1",
    "c12_x_allow_pairs_unc_tobs": "allow_pairs_uncapped_tobs", "c12_x_allow_pairs_unc_t1": "allow_pairs_uncapped_t1",
    "c12_importance_tobs": "importance_tobs", "c12_importance_t1": "importance_t1",
    "c12_inflow_untyped_tobs": "inflow_untyped_tobs", "c12_inflow_untyped_t1": "inflow_untyped_t1",
    "c12_proxies_tobs": "proxies_tobs",
    "c12_x_label_split_w0": "label_split_w0", "c12_x_label_split_w1": "label_split_w1",
    "c12_x_members": "members", "c12_describe_allowances": "describe_allowances",
}
STEM_TABLE = {stem: table for table, stem in DOWNLOADS.items()}
assert len(DOWNLOADS) == 16 and set(DOWNLOADS.values()) == set(INTERFACE)

# Tables of the twelve-month variant that contract12m keeps (graph-tables-usd-12m: the arrow types of the real files).
COHORT = {"address": "binary", "owners_nonzero": "int64", "approval_logs": "int64"}
U12_LABELS = {"wallet": "string", **{lab: ("double" if lab in RATES else "int64") for lab in LABELS}}
U12_INTERFACE = {"cohort": COHORT, "cohort_t1": COHORT, "labels_w0": U12_LABELS, "labels_w1": U12_LABELS}
# contract-types/c12_account_types: check_account_code.PROBE_SCHEMA (run_discovery.TYPE_COLUMNS are among them).
TYPES_INTERFACE = {"address": "large_string", "code_kind": "large_string", "account_class": "large_string",
                   "code_size": "int64", "code_hash": "large_string", "proxy_kind": "large_string",
                   "implementation": "large_string", "has_master_copy": "bool", "threshold": "int64",
                   "n_owners": "int64", "entry_point": "large_string", "has_validate_userop": "bool",
                   "has_paymaster_selector": "bool", "wallet_kind": "large_string"}
TYPES_META = {"complete": True, "pending": 0, "block_number": 513216506}
# The earlier variants' inputs (their columns and arrow types on disk).
EARLIER_NODES = {"id": "int64", "address": "string", "is_cohort": "bool"}
EARLIER_TYPES = {"address": "large_string", "code_kind": "large_string", "account_class": "large_string"}
CLOSES = {"block_timestamp": "timestamp[us, tz=UTC]", "block_number": "int64", "log_index": "int64",
          "account": "large_string", "msg_sender": "large_string", "base_pnl_usd": "large_string",
          "order_type": "int64", "is_liquidation": "bool", "size_delta_usd": "large_string", "is_long": "bool"}
TOP_TOKEN_PAIRS = {"list": "string", "layer": "string", "src": "int64", "dst": "int64", "w": "double",
                   "max_sig": "double"}

# Relative paths under an experiments folder (common.py's layout).
RAW_REL = "data/1-raw-blockchain-extracts"
GRAPH_REL = f"{RAW_REL}/graph-tables-contract-12m"
U12_REL = f"{RAW_REL}/graph-tables-usd-12m"
TYPES_REL = f"{RAW_REL}/contract-types/c12_account_types"
PROC_SHARED_REL = "data/2-processed-tables-and-evaluations"
PROC_REL = f"{PROC_SHARED_REL}/revised-contract-12m"
MANIFEST_REL = f"{PROC_REL}/run_manifest.json"
EARLIER_VARIANTS = ("registered", "usd", "usd12m")
EARLIER_GRAPH_REL = {"registered": f"{RAW_REL}/graph-tables", "usd": f"{RAW_REL}/graph-tables-usd", "usd12m": U12_REL}
EARLIER_PROC_REL = {"registered": PROC_SHARED_REL, "usd": f"{PROC_SHARED_REL}/revised-usd",
                    "usd12m": f"{PROC_SHARED_REL}/revised-usd-12m"}
GATE_B_STEPS = ("constants", "pairs", "rest", "checks", "download")
C12_SCRIPTS = ("run_same_window", "run_holdout", "run_registered", "run_robustness")   # run_usd_local.ps1's order
EARLIER_SCRIPTS = (*C12_SCRIPTS[:3], "run_robustness", "run_supplementary", "sybil_model")
UNFINISHED_SCRIPTS = ("run_supplementary", "sybil_model", "describe_data", "export_latex", "publish_results")


def arrow_type(alias: str):
    """The pyarrow type of an INTERFACE alias (str() of the type gives the alias back)."""
    import pyarrow as pa

    types = {"int64": pa.int64(), "double": pa.float64(), "bool": pa.bool_(), "string": pa.string(),
             "large_string": pa.large_string(), "binary": pa.binary(),
             "timestamp[us, tz=UTC]": pa.timestamp("us", tz="UTC")}
    return types[alias]


def arrow_schema(columns: str | dict[str, str]):
    """The pyarrow schema of an INTERFACE stem (or of a {column: alias} dict), in its column order."""
    import pyarrow as pa

    cols = INTERFACE[columns] if isinstance(columns, str) else columns
    return pa.schema([pa.field(c, arrow_type(t)) for c, t in cols.items()])


def schema_of(stem: Path) -> dict[str, str]:
    """{column: arrow type alias} of the parts of ``stem`` (every part must have the same schema)."""
    import pyarrow.parquet as pq

    paths = part_paths(stem)
    if not paths:
        raise FileNotFoundError(f"no parts for {stem}")
    schemas = {str(pq.read_schema(p)) for p in paths}
    if len(schemas) != 1:
        raise ValueError(f"the parts of {stem} differ in schema")
    return {f.name: str(f.type) for f in pq.read_schema(paths[0])}


# --------------------------------------------------------------------------- addresses and the synthetic world


def contract(i: int) -> str:
    """Contract i (node id i of the contract world, i < 150; of the earlier world, i < 120)."""
    return f"0x{0x1000 + 17 * i:040x}"


def user(i: int) -> str:
    """User account i: never a node."""
    return f"0x{0xa00000 + i:040x}"


def outside(i: int) -> str:
    """A typed contract that is no node (importance rows with id -1), or with i = 9 the untyped spender."""
    return f"0x{0xb00000 + i:040x}"


def trader(i: int) -> str:
    """A GMX trader of the earlier variants' world (node id 120 + i there)."""
    return f"0x{0xc00000 + i:040x}"


def token(i: int) -> str:
    return f"0x{0xd00000 + i:040x}"


SYSTEM = "0x" + "00" * 19 + "01"
ENTRY_POINT_V07 = "0x0000000071727de22e5e9d8baf0edac6f37da032"
N_CONTRACTS = 150
# Sources of user(0..11): 0-3 tx_sender, 4-6 rpc_eoa, 7-8 rpc_eoa_7702, 9-11 rpc_smart_account (9, 10 Safe, 11 ERC-4337)
USER_SOURCES = ("tx_sender",) * 4 + ("rpc_eoa",) * 3 + ("rpc_eoa_7702",) * 2 + ("rpc_smart_account",) * 3
SMART_KIND = {9: "safe", 10: "safe", 11: "erc4337"}
# The four twelve-month lists: (contract ids, user accounts, whether the system address SYSTEM is a member).
LISTS = {
    "cohort_tobs": (tuple(range(0, 40)), (0, 4, 7, 9, 11), False),
    "cohort_t1": (tuple(range(10, 48)), (1, 5, 8, 10), False),
    "spenders_w0": (tuple(range(30, 80)), (2, 6), True),
    "spenders_w1": (tuple(range(40, 90)) + (149,), (3, 6), True),
}
NODE_FLAGS = {"cohort_tobs": "is_cohort", "cohort_t1": "is_cohort_t1", "spenders_w0": "is_spender_w0",
              "spenders_w1": "is_spender_w1"}
OUTSIDE_BOTH = (5, 25, 45, 65, 85, 149)      # no pair in any layer at either freeze (149 has the highest address)
SELF_ONLY = (7, 33, 67)                      # only an allowance self-pair (capped and uncapped) at both freezes
ALLOW_ONLY = (12, 36, 72)                    # allowance pairs to and from other contracts, no transfer pair
TRANSFER_ONLY = (14, 38, 74)                 # transfer pairs to and from other contracts, no allowance pair
UNCAPPED_GAIN = (60, 70)                     # at least 10 in-edges each that only the uncapped layer holds
CHANGES = ("member_without_node", "untyped_spender", "node_typed_eoa", "node_listed_smart_account", "split_off",
           "proxy_missing")
PAIRS = {"t1": {"allow": 5200, "transfer": 6000}, "tobs": {"allow": 3000, "transfer": 4000}}   # non-self pairs
UNCAPPED_ONLY, UNCAPPED_GAIN_MIN = 60, 10
INFLOW_UNTYPED = {"tobs": 1234.5, "t1": 987.25}
IMPORTANCE_NODES, IMPORTANCE_OUTSIDE = 105, 5

_MEMBER_CONTRACTS = tuple(sorted({i for cs, _, _ in LISTS.values() for i in cs}))
_NON_MEMBERS = tuple(i for i in range(N_CONTRACTS) if i not in set(_MEMBER_CONTRACTS))
_FREE = tuple(i for i in range(N_CONTRACTS) if i not in set(OUTSIDE_BOTH) | set(SELF_ONLY))
_A_CAND = tuple(i for i in _FREE if i not in TRANSFER_ONLY)
_T_CAND = tuple(i for i in _FREE if i not in ALLOW_ONLY)


@dataclass
class World:
    """The synthetic contract12m world that contract_world() wrote under ``exp``: its member lists, the frames of
    every table as written (tests compute their expectations from these, never from hand-typed counts) and the member
    or table a change variant concerns (``target``)."""

    exp: Path
    seed: int
    change: str | None
    lists: dict[str, list[tuple[str, str, str | None]]] = field(repr=False)   # list -> [(address, class, source)]
    frames: dict[str, Any] = field(repr=False)              # GRAPH stem -> pandas frame as written
    u12_frames: dict[str, Any] = field(repr=False)          # cohort, cohort_t1, labels_w0, labels_w1
    types_frame: Any = field(repr=False)                    # contract-types/c12_account_types
    n_t1: dict[str, dict[str, int]] = field(repr=False)     # window -> {wallet: owners at the freeze}
    target: dict | None = None                              # {"id", "address", "stem"} of a change variant
    outside_both: tuple = OUTSIDE_BOTH
    self_only: tuple = SELF_ONLY
    allow_only: tuple = ALLOW_ONLY
    transfer_only: tuple = TRANSFER_ONLY
    uncapped_gain: tuple = UNCAPPED_GAIN

    @property
    def graph(self) -> Path:
        return self.exp / GRAPH_REL

    @property
    def u12(self) -> Path:
        return self.exp / U12_REL

    @property
    def types(self) -> Path:
        return self.exp / TYPES_REL

    @property
    def proc(self) -> Path:
        return self.exp / PROC_REL

    @property
    def manifest(self) -> Path:
        return self.exp / MANIFEST_REL

    def stem(self, name: str) -> Path:
        return self.graph / name

    def contracts(self, name: str) -> list[int]:
        """The node ids of the contract members of list ``name``, increasing."""
        return sorted(_contract_id(a) for a, c, _ in self.lists[name] if c == "contract")

    def members(self, name: str, cls: str | None = None) -> list[str]:
        """The addresses of list ``name`` (of one member class) in members order."""
        return [a for a, c, _ in self.lists[name] if cls is None or c == cls]

    @property
    def cohort_tobs(self) -> list[int]:
        return self.contracts("cohort_tobs")

    @property
    def cohort_t1(self) -> list[int]:
        return self.contracts("cohort_t1")

    @property
    def spenders_w0(self) -> list[int]:
        return self.contracts("spenders_w0")

    @property
    def spenders_w1(self) -> list[int]:
        return self.contracts("spenders_w1")

    @property
    def node_ids(self) -> list[int]:
        return [int(i) for i in self.frames["nodes"]["id"]]

    @property
    def rows(self) -> dict[str, int]:
        """{stem: rows} of the 16 downloaded stems."""
        return {stem: int(len(f)) for stem, f in self.frames.items()}

    @property
    def table_rows(self) -> dict[str, int]:
        """{BigQuery table: rows} of DOWNLOADS (the rows the driver's Run.sizes reports for them)."""
        return {table: int(len(self.frames[stem])) for table, stem in DOWNLOADS.items()}


def _contract_id(address: str) -> int:
    v = int(address, 16) - 0x1000
    if v < 0 or v % 17 or v // 17 >= N_CONTRACTS:
        raise ValueError(f"{address} is not a contract of the synthetic world")
    return v // 17


def part_paths(stem: Path) -> list[Path]:
    stem = Path(stem)
    return sorted(stem.parent.glob(f"{stem.name}.part[0-9][0-9][0-9].parquet"))


def part_sha256(stem: Path) -> dict[str, str]:
    """{part file name: SHA-256} of ``stem`` (common.part_sha256, the record of the driver's download step)."""
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in part_paths(stem)}


def _rows_on_disk(stem: Path) -> int:
    import pyarrow.parquet as pq

    return int(sum(pq.read_metadata(p).num_rows for p in part_paths(stem)))


def _guard(path: Path) -> Path:
    """``path`` unless it is, or lies inside, the real experiments folder (a folder whose data holds bq_ledger.json
    counts as real too): synthetic tables are never written there."""
    path = Path(path)
    r, real = path.resolve(), EXPERIMENTS.resolve()
    if r == real or real in r.parents:
        raise ValueError(f"refusing to write synthetic files into {path}: it lies in the experiments folder "
                         f"{EXPERIMENTS}")
    if (r / "data" / "bq_ledger.json").exists():
        raise ValueError(f"refusing to write synthetic files into {path}: it holds data/bq_ledger.json, as a real "
                         "experiments folder does; write the world into a folder of its own (a driver test tree "
                         "copies from it)")
    return path


def _table(columns: dict[str, str], data: dict[str, Any]):
    """A pyarrow table with exactly ``columns`` (in order, with their types) from ``data``."""
    import numpy as np
    import pyarrow as pa

    arrays = []
    for c, t in columns.items():
        v = data[c]
        if isinstance(v, np.ndarray):
            v = v.tolist()
        arrays.append(pa.array(v, type=arrow_type(t)))
    return pa.Table.from_arrays(arrays, schema=arrow_schema(columns))


def _write(table, stem: Path) -> None:
    """``table`` as ``stem``.part000.parquet (old parts of the stem removed), the layout of common.write_parts."""
    import pyarrow.parquet as pq

    stem = Path(stem)
    stem.parent.mkdir(parents=True, exist_ok=True)
    for p in part_paths(stem):
        p.unlink()
    pq.write_table(table, stem.parent / f"{stem.name}.part000.parquet", compression="zstd")


def _save_json(obj, path: Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=str), encoding="utf-8")   # as common.save_json


def _fill(rng, pairs: dict, cand: tuple, total: int) -> None:
    """Add random distinct pairs (src != dst) of ``cand`` until ``pairs`` holds ``total``."""
    import numpy as np

    c = np.asarray(cand, dtype=np.int64)
    while len(pairs) < total:
        k = 2 * (total - len(pairs)) + 16
        for s, d in zip(rng.choice(c, k).tolist(), rng.choice(c, k).tolist()):
            if s != d:
                pairs.setdefault((s, d), None)
                if len(pairs) >= total:
                    break


def _sorted(cols: dict) -> dict:
    """The columns of a pair table in increasing (src, dst) order."""
    import numpy as np

    order = np.lexsort((cols["dst"], cols["src"]))
    return {k: np.asarray(v)[order] for k, v in cols.items()}


def _allow_weights(rng, src, dst, tobs: bool) -> dict:
    import numpy as np

    n = len(src)
    w_er = rng.lognormal(0.0, 1.0, n)
    w_er[rng.random(n) < 0.05] = 0.0
    cols = {"src": np.asarray(src, np.int64), "dst": np.asarray(dst, np.int64),
            "n_tokens": rng.integers(1, 4, n).astype(np.int64), "w_er": w_er, "w_raw": rng.lognormal(2.0, 1.0, n),
            "max_sig": rng.uniform(0.01, 1.0, n)}
    if tobs:
        cols["w_er_b10x"] = w_er * rng.uniform(1.0, 1.5, n)
        cols["w_er_b01x"] = w_er * rng.uniform(0.5, 1.0, n)
    return cols


def _transfer_weights(rng, src, dst, tobs: bool) -> dict:
    import numpy as np

    n = len(src)
    w_awp = rng.lognormal(0.0, 1.0, n)
    w_awp[rng.random(n) < 0.05] = 0.0
    cols = {"src": np.asarray(src, np.int64), "dst": np.asarray(dst, np.int64),
            "n_transfers": rng.integers(1, 21, n).astype(np.int64), "w_awp": w_awp,
            "w_raw": rng.lognormal(3.0, 1.0, n), "max_sig": rng.uniform(0.01, 1.0, n)}
    if tobs:
        cols["w_awp_b10x"] = w_awp * rng.uniform(1.0, 1.5, n)
        cols["w_awp_b01x"] = w_awp * rng.uniform(0.5, 1.0, n)
    return cols


def _freeze_pairs(seed: int, tag: str) -> dict[str, dict]:
    """The capped, uncapped and transfer pairs of one freeze. Every list member that may have a pair of a layer gets
    one in and one out with a non-member contract; then random distinct pairs among the candidates of the layer, the
    allowance self-pairs of SELF_ONLY and two random allowance and three random transfer self-pairs."""
    import numpy as np

    rng = np.random.default_rng(seed + {"t1": 1, "tobs": 2}[tag])
    allow: dict = {}
    transfer: dict = {}
    a_set, t_set = set(_A_CAND), set(_T_CAND)
    for m in _MEMBER_CONTRACTS:
        if m in a_set:
            x, y = (int(v) for v in rng.choice(_NON_MEMBERS, 2, replace=False))
            allow.setdefault((x, m), None)
            allow.setdefault((m, y), None)
        if m in t_set:
            x, y = (int(v) for v in rng.choice(_NON_MEMBERS, 2, replace=False))
            transfer.setdefault((x, m), None)
            transfer.setdefault((m, y), None)
    _fill(rng, allow, _A_CAND, PAIRS[tag]["allow"])
    _fill(rng, transfer, _T_CAND, PAIRS[tag]["transfer"])
    a_self = [*SELF_ONLY, *(int(v) for v in rng.choice(_A_CAND, 2, replace=False))]
    t_self = [int(v) for v in rng.choice(_T_CAND, 3, replace=False)]
    a_pairs = sorted([*allow, *((s, s) for s in a_self)])
    t_pairs = sorted([*transfer, *((s, s) for s in t_self)])
    tobs = tag == "tobs"
    capped = _allow_weights(rng, [p[0] for p in a_pairs], [p[1] for p in a_pairs], tobs)
    moved = _transfer_weights(rng, [p[0] for p in t_pairs], [p[1] for p in t_pairs], tobs)
    # Uncapped: every capped pair with larger weights (usd_allow >= usd_eff), plus pairs only the uncapped layer holds:
    # at least UNCAPPED_GAIN_MIN into each UNCAPPED_GAIN member, none touching OUTSIDE_BOTH, SELF_ONLY or TRANSFER_ONLY.
    n = len(a_pairs)
    unc = {"src": capped["src"].copy(), "dst": capped["dst"].copy(),
           "n_tokens": capped["n_tokens"] + rng.integers(0, 2, n), "w_er": capped["w_er"] * rng.uniform(1.0, 2.0, n),
           "w_raw": capped["w_raw"] * rng.uniform(1.0, 4.0, n), "max_sig": capped["max_sig"].copy()}
    have = set(a_pairs)
    extra: dict = {}
    for g in UNCAPPED_GAIN:
        srcs = [s for s in _A_CAND if s != g and (s, g) not in have]
        for s in rng.choice(srcs, UNCAPPED_GAIN_MIN, replace=False):
            extra.setdefault((int(s), g), None)
    while len(extra) < UNCAPPED_ONLY:
        s, d = (int(v) for v in rng.choice(_A_CAND, 2, replace=False))
        if (s, d) not in have:
            extra.setdefault((s, d), None)
    e = sorted(extra)
    k = len(e)
    unc = {"src": np.concatenate([unc["src"], [p[0] for p in e]]).astype(np.int64),
           "dst": np.concatenate([unc["dst"], [p[1] for p in e]]).astype(np.int64),
           "n_tokens": np.concatenate([unc["n_tokens"], rng.integers(1, 4, k)]).astype(np.int64),
           "w_er": np.concatenate([unc["w_er"], rng.lognormal(0.0, 1.0, k)]),
           "w_raw": np.concatenate([unc["w_raw"], rng.lognormal(2.0, 1.0, k)]),
           "max_sig": np.concatenate([unc["max_sig"], rng.uniform(0.01, 1.0, k)])}
    return {"allow": capped, "uncapped": _sorted(unc), "transfer": moved}


def _member_rows(change: str | None) -> dict[str, list[tuple[str, str, str | None]]]:
    rows = {}
    for name, (cs, us, system) in LISTS.items():
        r = [(contract(i), "contract", None) for i in cs]
        r += [(user(u), "user_account", USER_SOURCES[u]) for u in us]
        if system:
            r.append((SYSTEM, "system", None))
        if change == "untyped_spender" and name == "spenders_w1":
            r.append((outside(9), "untyped", None))
        rows[name] = r
    return rows


def _proxies(seed: int, cohort: list[int], transfer: dict) -> dict:
    """proxies_tobs as job 38 computes it from the T_obs transfers between contracts (check H2): in_degree = the
    distinct senders over the member's in-pairs, self included; inbound_tx, inbound_unique = the transfers and pairs
    from other senders; a member without an in-pair has 0 everywhere."""
    import numpy as np

    rng = np.random.default_rng(seed + 3)
    src, dst = np.asarray(transfer["src"]), np.asarray(transfer["dst"])
    ntr, wraw = np.asarray(transfer["n_transfers"]), np.asarray(transfer["w_raw"])
    out = {c: [] for c in PROXIES}
    for i in cohort:
        months = int(rng.integers(1, 13))
        m = dst == i
        s = src[m]
        other = s != i
        tx, uniq = int(ntr[m][other].sum()), int(other.sum())
        months = months if m.any() else 0
        out["wallet"].append(contract(i))
        out["in_degree"].append(int(np.unique(s).size))
        out["in_value"].append(float(10.0 * wraw[m].sum()))
        out["inbound_counterparty_ratio"].append(uniq / max(tx, 1))
        out["transfer_tenure_days"].append(30.0 * months)
        out["active_months"].append(months)
        out["inbound_tx"].append(tx)
        out["inbound_unique"].append(uniq)
    return out


def _labels(seed: int, window: str, rows: list[tuple[str, str, str | None]]) -> tuple[dict, dict, dict]:
    """The u12 labels of every spender list row, its label split and its n_t1. Each spender's n_t1 pairs get a class
    (user, contract, other) and the revoked pairs are drawn among them; every count label is split by drawing a class
    per counted account; the rate parts are part / n_t1, the keep parts (n_t1 part - revoked part) / n_t1, the value
    parts value x part / count with the third as the remainder."""
    import numpy as np

    rng = np.random.default_rng(seed + {"w0": 6, "w1": 7}[window])
    lab = {c: [] for c in U12_LABELS}
    split = {c: [] for c in SPLIT}
    n_t1s = {}
    for address, cls, _ in rows:
        n_t1 = int(rng.integers(1, 12))
        pair_cls = rng.integers(0, 3, n_t1)
        revoked = rng.random(n_t1) < 0.4
        count = int(revoked.sum())
        counted = {"future_new_approvers": int(rng.integers(0, 6)),
                   "future_new_transfer_senders": int(rng.integers(0, 8)),
                   "future_drain_owners": int(rng.integers(0, 2))}
        value = count * float(rng.uniform(10.0, 1000.0))
        classes = {c: rng.integers(0, 3, k) for c, k in counted.items()}
        n_t1s[address] = n_t1
        lab["wallet"].append(address)
        lab["future_new_approvers"].append(counted["future_new_approvers"])
        lab["future_revoke_count"].append(count)
        lab["future_revoke_rate"].append(count / n_t1)
        lab["future_keep_rate"].append(1.0 - count / n_t1)
        lab["future_revoke_value"].append(value)
        lab["future_new_transfer_senders"].append(counted["future_new_transfer_senders"])
        lab["future_drain_owners"].append(counted["future_drain_owners"])
        split["wallet"].append(address)
        split["spender_class"].append(cls)
        split["n_t1"].append(n_t1)
        rev = {}
        for k, p in enumerate(PARTS):
            n_p = int((pair_cls == k).sum())
            r_p = int((revoked & (pair_cls == k)).sum())
            rev[p] = r_p
            split[f"n_t1_{p}"].append(n_p)
            split[f"future_revoke_count_{p}"].append(r_p)
            split[f"future_revoke_rate_{p}"].append(r_p / n_t1)
            split[f"future_keep_rate_{p}"].append((n_p - r_p) / n_t1)
            for c in counted:
                split[f"{c}_{p}"].append(int((classes[c] == k).sum()))
        v_user = value * rev["user"] / count if count else 0.0
        v_contract = value * rev["contract"] / count if count else 0.0
        split["future_revoke_value_user"].append(v_user)
        split["future_revoke_value_contract"].append(v_contract)
        split["future_revoke_value_other"].append(value - v_user - v_contract if count else 0.0)
    return lab, split, n_t1s


def _importance(seed: int, tag: str) -> dict:
    """IMPORTANCE_NODES distinct node ids drawn from 0..148 (so that member_without_node leaves no row without its
    node) and IMPORTANCE_OUTSIDE rows id -1 at outside(0..); every row has i_t > 0 or i_a > 0, n_t = floor(i_t) and
    n_a = floor(i_a) (int64, n <= i)."""
    import numpy as np

    rng = np.random.default_rng(seed + {"tobs": 4, "t1": 5}[tag])
    ids = np.sort(rng.choice(N_CONTRACTS - 1, IMPORTANCE_NODES, replace=False)).astype(np.int64)
    k = IMPORTANCE_NODES + IMPORTANCE_OUTSIDE
    i_t = np.where(rng.random(k) < 0.6, rng.lognormal(1.0, 1.5, k), 0.0)
    i_a = np.where(rng.random(k) < 0.6, rng.lognormal(1.0, 1.5, k), 0.0)
    none = (i_t == 0) & (i_a == 0)
    i_t[none] = rng.lognormal(1.0, 1.5, int(none.sum()))
    return {"id": np.concatenate([ids, np.full(IMPORTANCE_OUTSIDE, -1, np.int64)]),
            "address": [contract(int(i)) for i in ids] + [outside(j) for j in range(IMPORTANCE_OUTSIDE)],
            "i_t": i_t, "i_a": i_a, "n_t": np.floor(i_t).astype(np.int64), "n_a": np.floor(i_a).astype(np.int64)}


def _describe(seed: int) -> dict:
    """describe_allowances: one row per (tag, token) of five tokens, with consistent counts."""
    import numpy as np

    rng = np.random.default_rng(seed + 8)
    out = {c: [] for c in DESCRIBE}
    for tag in ("t1", "tobs"):
        for k in range(5):
            latest = int(rng.integers(100, 1000))
            positive = int(rng.integers(1, latest + 1))
            unlimited = int(rng.integers(0, latest // 10 + 1))
            eff_cap = int(rng.integers(0, 5))
            s_eff = float(rng.uniform(1e3, 1e6))
            row = {"tag": tag, "token": token(k), "n_latest_positive": latest, "n_positive_eff": positive,
                   "n_capped_to_zero": latest - positive,
                   "n_capped_below_allowance": int(rng.integers(0, positive + 1)),
                   "n_unlimited": unlimited, "n_finite": latest - unlimited, "n_eff_at_or_above_cap": eff_cap,
                   "n_allow_at_or_above_cap": eff_cap + int(rng.integers(0, 5)), "sum_usd_eff": s_eff,
                   "sum_usd_allow_finite": s_eff * float(rng.uniform(1.0, 3.0))}
            for c in DESCRIBE:
                out[c].append(row[c])
    return out


def _type_row(address: str, kind: str, i: int = 0) -> dict:
    """A row of check_account_code's output: kind contract, eoa, eoa_7702, safe or erc4337."""
    row = {"address": address, "code_kind": "contract", "account_class": "contract", "code_size": 100 + i,
           "code_hash": "0x" + f"{i % 7:064x}", "proxy_kind": "none", "implementation": "", "has_master_copy": False,
           "threshold": -1, "n_owners": -1, "entry_point": "", "has_validate_userop": False,
           "has_paymaster_selector": False, "wallet_kind": ""}
    if kind == "eoa":
        row.update(code_kind="none", account_class="eoa", code_size=0, code_hash="")
    elif kind == "eoa_7702":
        row.update(code_kind="eip7702", account_class="eoa_7702", code_size=23, code_hash="0x" + "77" * 32)
    elif kind == "safe":
        row.update(account_class="smart_account", code_size=171, code_hash="0x" + "5a" * 32, proxy_kind="safe",
                   implementation="0x" + "41" * 20, has_master_copy=True, threshold=1, n_owners=2, wallet_kind="safe")
    elif kind == "erc4337":
        row.update(account_class="smart_account", code_size=402, code_hash="0x" + "43" * 32,
                   entry_point=ENTRY_POINT_V07, has_validate_userop=True, wallet_kind="erc4337")
    return row


def _types(change: str | None) -> dict:
    """Every contract and outside(0..4) typed contract, the user accounts by source, SYSTEM an eoa; sorted by address
    as check_account_code writes them. node_typed_eoa types contract 120 as an eoa. node_listed_smart_account types it
    a contract whose code hash is the first of common.SMART_ACCOUNT_CODE_HASHES (proxy kind none, own code under 1,000
    bytes, entryPoint() answering the canonical v0.7 EntryPoint): the typing output says contract, and the smart-account
    lists of the amendment of 9 November 2026 (revision section 13) make it a smart account, a user account."""
    rows = [_type_row(contract(i), "eoa" if (change == "node_typed_eoa" and i == 120) else "contract", i)
            for i in range(N_CONTRACTS)]
    if change == "node_listed_smart_account":
        import common

        rows[120].update(code_hash=common.SMART_ACCOUNT_CODE_HASHES[0], entry_point=ENTRY_POINT_V07)
    rows += [_type_row(outside(j), "contract", j) for j in range(IMPORTANCE_OUTSIDE)]
    kinds = {"tx_sender": "eoa", "rpc_eoa": "eoa", "rpc_eoa_7702": "eoa_7702"}
    rows += [_type_row(user(u), kinds.get(src) or SMART_KIND[u]) for u, src in enumerate(USER_SOURCES)]
    rows.append(_type_row(SYSTEM, "eoa"))
    rows.sort(key=lambda r: r["address"])
    return {c: [r[c] for r in rows] for c in TYPES_INTERFACE}


def contract_world(exp: Path, *, seed: int = 11, change: str | None = None) -> World:
    """Write the synthetic contract12m world under ``exp/data`` (exp = the experiments folder of a sandbox or of a
    driver test tree) and return it.

    Contracts 0..149 = contract(i) are the rows of nodes (ids dense, in address order); user(0..11) are never nodes.
    The lists: cohort_tobs = contracts 0..39 and users 0, 4, 7, 9, 11; cohort_t1 = 10..47 and users 1, 5, 8, 10;
    spenders_w0 = 30..79, users 2, 6 and SYSTEM; spenders_w1 = 40..89 and 149, users 3, 6 and SYSTEM. Placement at both
    freezes: OUTSIDE_BOTH, SELF_ONLY, ALLOW_ONLY, TRANSFER_ONLY and UNCAPPED_GAIN; 5,200 capped allowance pairs at t1
    keep the pilot above the stop threshold of 5,000 edges. Written, with exactly the INTERFACE columns and types:
    the 16 stems of graph-tables-contract-12m, graph-tables-usd-12m/{cohort, cohort_t1, labels_w0, labels_w1},
    contract-types/c12_account_types (+ .json) and, last, revised-contract-12m/run_manifest.json with the steps
    constants to download passed and results.download.files[stem] = {table, rows, sha256 of every part} (check H1).

    ``change`` writes one variant instead (the manifest is written after the change, so its hashes are those of the
    changed tables): member_without_node (node 149 left out of nodes), untyped_spender (outside(9) a spenders_w1
    member of class untyped, with its labels and split row), node_typed_eoa (the types row of contract 120 says eoa),
    node_listed_smart_account (the types row of contract 120 says contract, on a code hash of the smart-account lists
    of revision section 13), split_off (future_new_approvers_user of the first contract spender of label_split_w0 + 1),
    proxy_missing (the proxies row of contract 3 left out). ``World.target`` names the member or stem concerned."""
    import numpy as np

    if change is not None and change not in CHANGES:
        raise ValueError(f"change must be None or one of {CHANGES}, not {change!r}")
    exp = _guard(exp)
    graph, u12 = exp / GRAPH_REL, exp / U12_REL
    tables = {}
    target = None
    node_ids = [i for i in range(N_CONTRACTS) if not (change == "member_without_node" and i == 149)]
    lists = _member_rows(change)
    tables["nodes"] = _table(INTERFACE["nodes"], {
        "id": node_ids, "address": [contract(i) for i in node_ids],
        **{flag: [i in set(LISTS[name][0]) for i in node_ids] for name, flag in NODE_FLAGS.items()}})
    tables["members"] = _table(INTERFACE["members"], {
        "list": [name for name, rows in lists.items() for _ in rows],
        "address": [a for rows in lists.values() for a, _, _ in rows],
        "class": [c for rows in lists.values() for _, c, _ in rows],
        "source": [s for rows in lists.values() for _, _, s in rows]})
    pairs = {tag: _freeze_pairs(seed, tag) for tag in ("t1", "tobs")}
    for tag in ("t1", "tobs"):
        tables[f"allow_pairs_{tag}"] = _table(INTERFACE[f"allow_pairs_{tag}"], pairs[tag]["allow"])
        tables[f"allow_pairs_uncapped_{tag}"] = _table(INTERFACE[f"allow_pairs_uncapped_{tag}"], pairs[tag]["uncapped"])
        tables[f"transfer_pairs_{tag}"] = _table(INTERFACE[f"transfer_pairs_{tag}"], pairs[tag]["transfer"])
        tables[f"importance_{tag}"] = _table(IMP, _importance(seed, tag))
        tables[f"inflow_untyped_{tag}"] = _table({"usd": "double"}, {"usd": [INFLOW_UNTYPED[tag]]})
    prox = _proxies(seed, list(LISTS["cohort_tobs"][0]), pairs["tobs"]["transfer"])
    if change == "proxy_missing":
        keep = [w != contract(3) for w in prox["wallet"]]
        prox = {c: [v for v, k in zip(vals, keep) if k] for c, vals in prox.items()}
        target = {"id": 3, "address": contract(3), "stem": "proxies_tobs"}
    tables["proxies_tobs"] = _table(PROXIES, prox)
    u12_tables, n_t1 = {}, {}
    for window in ("w0", "w1"):
        lab, split, n_t1[window] = _labels(seed, window, lists[f"spenders_{window}"])
        if change == "split_off" and window == "w0":
            first = split["spender_class"].index("contract")
            split["future_new_approvers_user"][first] += 1
            target = {"id": _contract_id(split["wallet"][first]), "address": split["wallet"][first],
                      "stem": "label_split_w0"}
        u12_tables[f"labels_{window}"] = _table(U12_LABELS, lab)
        tables[f"label_split_{window}"] = _table(SPLIT, split)
    for name, stem in (("cohort_tobs", "cohort"), ("cohort_t1", "cohort_t1")):
        rows = lists[name]
        u12_tables[stem] = _table(COHORT, {"address": [bytes.fromhex(a[2:]) for a, _, _ in rows],
                                           "owners_nonzero": [3 + i % 7 for i in range(len(rows))],
                                           "approval_logs": [5 + i % 11 for i in range(len(rows))]})
    tables["describe_allowances"] = _table(DESCRIBE, _describe(seed))
    types = _table(TYPES_INTERFACE, _types(change))
    if change == "member_without_node":
        target = {"id": 149, "address": contract(149), "stem": "nodes"}
    elif change == "untyped_spender":
        target = {"id": None, "address": outside(9), "stem": "members"}
    elif change in ("node_typed_eoa", "node_listed_smart_account"):
        target = {"id": 120, "address": contract(120), "stem": None}
    assert set(tables) == set(INTERFACE), sorted(set(INTERFACE) ^ set(tables))
    for stem, t in tables.items():
        _write(t, graph / stem)
    for stem, t in u12_tables.items():
        _write(t, u12 / stem)
    _write(types, exp / TYPES_REL)
    _save_json(TYPES_META, (exp / TYPES_REL).with_suffix(".json"))
    write_manifest(exp)                                                       # the last write (check H1)
    return World(exp=exp, seed=seed, change=change, lists=lists,
                 frames={stem: t.to_pandas() for stem, t in tables.items()},
                 u12_frames={stem: t.to_pandas() for stem, t in u12_tables.items()},
                 types_frame=types.to_pandas(), n_t1=n_t1, target=target)


def manifest_for(exp: Path) -> dict:
    """The driver's run manifest for the gate B stems on disk under ``exp``: the gate B steps passed in their order
    and results.download.files[stem] = {table, rows, sha256: {part: SHA-256}} for every stem of DOWNLOADS."""
    graph = Path(exp) / GRAPH_REL
    files = {stem: {"table": table, "rows": _rows_on_disk(graph / stem), "sha256": part_sha256(graph / stem)}
             for table, stem in DOWNLOADS.items()}
    return {"variant": "contract12m", "steps": [{"step": s, "passed": True} for s in GATE_B_STEPS], "jobs": [],
            "results": {"download": {"files": files}}}


def write_manifest(exp: Path) -> Path:
    """Write manifest_for(exp) to ``exp``/MANIFEST_REL; return its path."""
    path = _guard(exp) / MANIFEST_REL
    _save_json(manifest_for(exp), path)
    return path


def rehash(world_or_exp: World | Path, *stems: str) -> dict:
    """Rewrite results.download.files[stem].sha256 and rows of the run manifest to the parts on disk (every stem of
    DOWNLOADS when none is given), as the download step would record them; return the manifest."""
    exp = _guard(world_or_exp.exp if isinstance(world_or_exp, World) else Path(world_or_exp))
    path = exp / MANIFEST_REL
    m = json.loads(path.read_text(encoding="utf-8"))
    files = m.setdefault("results", {}).setdefault("download", {}).setdefault("files", {})
    for stem in stems or tuple(DOWNLOADS.values()):
        rec = files.setdefault(stem, {"table": STEM_TABLE.get(stem, stem)})
        rec["rows"] = _rows_on_disk(exp / GRAPH_REL / stem)
        rec["sha256"] = part_sha256(exp / GRAPH_REL / stem)
    _save_json(m, path)
    return m


def write_stem(world: World, stem: str, frame, *, rehashed: bool = True):
    """Write ``frame`` (pandas) as the gate B stem ``stem`` of ``world`` with its INTERFACE columns and types, update
    world.frames and, unless ``rehashed`` is False, the manifest's record of the stem; return the frame as written."""
    t = _table(INTERFACE[stem], {c: frame[c].tolist() for c in INTERFACE[stem]})
    _write(t, _guard(world.exp) / GRAPH_REL / stem)
    world.frames[stem] = t.to_pandas()
    if rehashed:
        rehash(world, stem)
    return world.frames[stem]


def download_copy(world: World, table: str, dest: Path, *, rows: int | None = None) -> dict:
    """What scripts/download_table.py writes for ``table`` (of DOWNLOADS, with or without "contract_rep.") into the
    stem ``dest``: the parts of the world's stem copied there (old parts of dest removed) and the sidecar dest.json
    {table, rows, table_rows, downloaded_at, parts, bytes}; ``rows`` replaces the sidecar's rows (not table_rows), as
    in a download that lost rows. Returns the sidecar (a fake of the driver's sh for the download step)."""
    table = table.split(".")[-1]
    stem, dest = DOWNLOADS[table], Path(dest)
    _guard(dest.parent).mkdir(parents=True, exist_ok=True)
    for p in part_paths(dest):
        p.unlink()
    names = []
    for p in part_paths(world.graph / stem):
        names.append(dest.name + p.name[len(stem):])
        shutil.copyfile(p, dest.parent / names[-1])
    n = _rows_on_disk(dest)
    side = {"table": f"dissertation-bq.contract_rep.{table}", "rows": n if rows is None else int(rows),
            "table_rows": n, "downloaded_at": "2026-11-10T00:00:00+00:00", "parts": names,
            "bytes": int(sum((dest.parent / x).stat().st_size for x in names))}
    _save_json(side, dest.parent / f"{dest.name}.json")
    return side


def pilot_from_world(world: World, cfg: dict) -> dict:
    """The structure pilot of the world's t1 tables: a struct frame (a, b, layer) of its capped, uncapped and transfer
    pairs as hex addresses (self-pairs included), then run_discovery.feasibility(cfg, struct, types, the u12 cohort_t1,
    the wallets of labels_w0), the pilot's own code, plus code = {head abc123, every file of run_discovery.COMMITTED
    committed}, cleaned as JSON. The types are the world's account types with the smart-account lists of the
    amendment of 9 November 2026 (revision section 13) applied by common.with_smart_account_extension, as
    run_discovery.run_feasibility reads them. ``cfg`` is the contract12m configuration (its discovery and
    contract_graph sections); its rules set no stop flag (5,200 capped edges), so check_fixed passes without an
    author's decision."""
    import common
    import pandas as pd
    import run_discovery as rd

    parts = []
    for stem, layer in (("allow_pairs_t1", "allow_capped"), ("allow_pairs_uncapped_t1", "allow_uncapped"),
                        ("transfer_pairs_t1", "transfer")):
        f = world.frames[stem]
        parts.append(pd.DataFrame({"a": [contract(int(i)) for i in f["src"]], "b": [contract(int(i)) for i in f["dst"]],
                                   "layer": layer}))
    struct = pd.concat(parts, ignore_index=True)
    cohort = ["0x" + bytes(a).hex() for a in world.u12_frames["cohort_t1"]["address"]]
    spenders = [str(w) for w in world.u12_frames["labels_w0"]["wallet"]]
    report = rd.feasibility(cfg, struct, common.with_smart_account_extension(world.types_frame), cohort, spenders)
    report["code"] = {"head": "abc123", "committed": {rel: True for rel in rd.COMMITTED}}
    return json.loads(json.dumps(rd._clean(report)))


# --------------------------------------------------------------------------- the earlier variants' world

N_EARLY, N_TRADERS = 120, 24
EARLY_COHORT = tuple(range(0, 40))
EARLY_SPENDERS = {"w0": tuple(range(30, 80)), "w1": tuple(range(40, 90))}
EARLY_USERS = {user(0): ("none", "eoa"), user(1): ("eip7702", "eoa_7702")}   # typed spenders that are no contracts
EARLY_OWNERS_ONLY = tuple(range(100, N_EARLY))   # never the spender of an allowance pair (EndorseRank's common c)
EARLY_PAIRS = {"allow": 1500, "allow_self": 3, "transfer": 2000, "transfer_self": 10}
WINDOWS = {"obs": "2026-04-01T00:00:00+00:00", "w1": "2026-07-01T00:00:00+00:00"}   # the W0 and W1 label windows


@dataclass
class EarlierWorld:
    """What earlier_world() wrote: node ids (contracts 0..119, traders 120..143), the cohort, the spender contracts and
    the traders, and the frames of the variant's GRAPH folder as written."""

    exp: Path
    variant: str
    seed: int
    frames: dict[str, Any] = field(repr=False)              # GRAPH stem -> pandas frame as written
    closes: dict[str, Any] = field(repr=False)              # obs, w1 -> the decoded closes as written
    cohort: tuple = EARLY_COHORT
    spenders: dict = field(default_factory=lambda: dict(EARLY_SPENDERS))
    traders: tuple = tuple(range(N_EARLY, N_EARLY + N_TRADERS))

    @property
    def graph(self) -> Path:
        return self.exp / EARLIER_GRAPH_REL[self.variant]

    @property
    def proc(self) -> Path:
        return self.exp / EARLIER_PROC_REL[self.variant]

    @property
    def trader_addresses(self) -> list[str]:
        return [trader(k) for k in range(N_TRADERS)]


def _early_freeze(seed: int, tag: str, slopes: bool) -> tuple[dict, dict]:
    import numpy as np

    rng = np.random.default_rng(seed + {"t1": 1, "tobs": 2}[tag])
    allow: dict = {}
    transfer: dict = {}
    owners = np.arange(N_EARLY)
    spenders = np.asarray([i for i in range(N_EARLY) if i not in EARLY_OWNERS_ONLY])
    while len(allow) < EARLY_PAIRS["allow"]:
        s, d = int(rng.choice(owners)), int(rng.choice(spenders))
        if s != d:
            allow.setdefault((s, d), None)
    _fill(rng, transfer, tuple(range(N_EARLY)), EARLY_PAIRS["transfer"])
    for s in rng.choice(spenders, EARLY_PAIRS["allow_self"], replace=False):
        allow.setdefault((int(s), int(s)), None)
    for s in rng.choice(owners, EARLY_PAIRS["transfer_self"], replace=False):
        transfer.setdefault((int(s), int(s)), None)
    # Every trader is the spender of 1 + k % 6 allowance pairs and the recipient of 1 + 5k % 7 transfer pairs.
    for k in range(N_TRADERS):
        t = N_EARLY + k
        for s in rng.choice(owners, 1 + k % 6, replace=False):
            allow.setdefault((int(s), t), None)
        for s in rng.choice(owners, 1 + (5 * k) % 7, replace=False):
            transfer.setdefault((int(s), t), None)
    a, t = sorted(allow), sorted(transfer)
    tobs = tag == "tobs" and slopes
    return (_allow_weights(rng, [p[0] for p in a], [p[1] for p in a], tobs),
            _transfer_weights(rng, [p[0] for p in t], [p[1] for p in t], tobs))


def _closes(seed: int, window: str) -> dict:
    """Decoded GMX closes inside the W0 (obs) or W1 (w1) label window: trader k closes 3 + k % 8 times; for an even
    k every third close is a liquidation (order type 7), so that LIQ takes several values on every resample; the other
    closes win unless (k + j) % 3 == 0."""
    import numpy as np
    import pandas as pd

    rng = np.random.default_rng(seed + {"obs": 9, "w1": 10}[window])
    start = pd.Timestamp(WINDOWS[window])
    out = {c: [] for c in CLOSES}
    for k in range(N_TRADERS):
        for j in range(3 + k % 8):
            liq = k % 2 == 0 and j % 3 == 2
            size = 1 + int(abs(rng.normal(0.0, 1000.0)))
            pnl = -size if (liq or (k + j) % 3 == 0) else size
            ts = start + pd.Timedelta(days=(7 * k + 13 * j) % 85, hours=(k + 3 * j) % 24, minutes=j)
            out["block_timestamp"].append(ts.to_pydatetime())
            out["block_number"].append(400_000_000 + 1000 * k + j)
            out["log_index"].append(j)
            out["account"].append(trader(k))
            out["msg_sender"].append(trader(k))
            out["base_pnl_usd"].append(str(pnl * 10**30))
            out["order_type"].append(7 if liq else 4)
            out["is_liquidation"].append(liq)
            out["size_delta_usd"].append(str((100 + int(rng.integers(0, 10000))) * 10**30))
            out["is_long"].append((k + j) % 2 == 0)
    return out


def earlier_world(exp: Path, variant: str, *, seed: int = 13) -> EarlierWorld:
    """Write what the six evaluation scripts of O1 read under ``variant`` (registered, usd or usd12m) and return it.

    In the variant's GRAPH folder: nodes (id, address, is_cohort; contracts 0..119, then N_TRADERS traders, ids in
    address order; the cohort is contracts 0..39), allow_pairs_{tobs,t1} and transfer_pairs_{tobs,t1} (the six
    registered columns; the slope columns at T_obs for usd and usd12m only, as on disk; contracts 100..119 own
    allowances but receive none), proxies_tobs (the cohort), labels_w0 (contracts 30..79, user(0), user(1)), labels_w1
    (40..89 and the same two); for registered also top_token_pairs (by_amount and by_rows x allowance and transfer,
    300 rows each) and top_tokens.csv (5 tokens, 3 in both lists). Shared: RAW/cohort/candidate_account_types and
    holdout_spender_types (contracts contract, user(0) none, user(1) eip7702), RAW/gmx/gmx_account_types and _w1 (the
    traders, contract), PROC_SHARED/gmx/gmx_contract_closes_{obs,w1}_decoded (_closes). Every trader is the end of a
    pair at both freezes. Requirement: every script of EARLIER_SCRIPTS runs to completion on it under all three
    variants; with 24 traders (the design's 16 would leave a resample of the 2,000 of run_registered's neutral-label
    grid without a liquidated trader) every trader contrast has a value on every resample."""
    import numpy as np

    if variant not in EARLIER_VARIANTS:
        raise ValueError(f"variant must be one of {EARLIER_VARIANTS}, not {variant!r}")
    exp = _guard(exp)
    graph = exp / EARLIER_GRAPH_REL[variant]
    raw, shared = exp / RAW_REL, exp / PROC_SHARED_REL
    slopes = variant != "registered"
    frames = {}
    ids = list(range(N_EARLY + N_TRADERS))
    addresses = [contract(i) for i in range(N_EARLY)] + [trader(k) for k in range(N_TRADERS)]
    frames["nodes"] = _table(EARLIER_NODES, {"id": ids, "address": addresses,
                                             "is_cohort": [i in set(EARLY_COHORT) for i in ids]})
    pairs = {tag: _early_freeze(seed, tag, slopes) for tag in ("t1", "tobs")}
    for tag, (allow, transfer) in pairs.items():
        a_cols = {**PAIR6, **({"w_er_b10x": "double", "w_er_b01x": "double"} if tag == "tobs" and slopes else {})}
        t_cols = {**TPAIR6, **({"w_awp_b10x": "double", "w_awp_b01x": "double"} if tag == "tobs" and slopes else {})}
        frames[f"allow_pairs_{tag}"] = _table(a_cols, allow)
        frames[f"transfer_pairs_{tag}"] = _table(t_cols, transfer)
    prox = _proxies(seed, list(EARLY_COHORT), pairs["tobs"][1])
    frames["proxies_tobs"] = _table(PROXIES, prox)
    for window in ("w0", "w1"):
        rows = [(contract(i), "contract", None) for i in EARLY_SPENDERS[window]]
        rows += [(u, "user_account", None) for u in EARLY_USERS]
        lab, _, _ = _labels(seed, window, rows)
        frames[f"labels_{window}"] = _table(U12_LABELS, lab)
    if variant == "registered":
        rng = np.random.default_rng(seed + 8)
        tok = {c: [] for c in TOP_TOKEN_PAIRS}
        dsts = [i for i in range(N_EARLY) if i not in EARLY_OWNERS_ONLY]
        for lst in ("by_amount", "by_rows"):
            for layer in ("allowance", "transfer"):
                chosen: dict = {}
                while len(chosen) < 300:
                    s, d = int(rng.integers(0, N_EARLY)), int(rng.choice(dsts))
                    if s != d:
                        chosen.setdefault((s, d), None)
                for s, d in sorted(chosen):
                    tok["list"].append(lst)
                    tok["layer"].append(layer)
                    tok["src"].append(s)
                    tok["dst"].append(d)
                    tok["w"].append(float(rng.lognormal(0.0, 1.0)))
                    tok["max_sig"].append(float(rng.uniform(0.01, 1.0)))
        frames["top_token_pairs"] = _table(TOP_TOKEN_PAIRS, tok)
    for stem, t in frames.items():
        _write(t, graph / stem)
    if variant == "registered":
        both = [(True, True), (True, True), (True, True), (True, False), (False, True)]
        lines = ["token,amount,n,by_amount,by_rows"] + [
            f"{token(k)},{(k + 1) * 1.5e20!r},{1000 * (5 - k)},{str(a).lower()},{str(b).lower()}"
            for k, (a, b) in enumerate(both)]
        (graph / "top_tokens.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")
    typed = {contract(i): ("contract", "contract") for i in range(N_EARLY)}
    spenders = sorted({i for s in EARLY_SPENDERS.values() for i in s})
    _write(_table(EARLIER_TYPES, _early_types([*typed.items(), *EARLY_USERS.items()])),
           raw / "cohort" / "candidate_account_types")
    _write(_table(EARLIER_TYPES, _early_types([*((contract(i), typed[contract(i)]) for i in spenders),
                                               *EARLY_USERS.items()])),
           raw / "cohort" / "holdout_spender_types")
    gmx = [(trader(k), ("contract", "contract")) for k in range(N_TRADERS)]
    _write(_table(EARLIER_TYPES, _early_types(gmx)), raw / "gmx" / "gmx_account_types")
    _write(_table(EARLIER_TYPES, _early_types(gmx)), raw / "gmx" / "gmx_account_types_w1")
    closes = {}
    for window in ("obs", "w1"):
        t = _table(CLOSES, _closes(seed, window))
        _write(t, shared / "gmx" / f"gmx_contract_closes_{window}_decoded")
        closes[window] = t.to_pandas()
    return EarlierWorld(exp=exp, variant=variant, seed=seed, frames={k: t.to_pandas() for k, t in frames.items()},
                        closes=closes)


def _early_types(rows: Iterable[tuple[str, tuple[str, str]]]) -> dict:
    rows = sorted(rows)
    return {"address": [a for a, _ in rows], "code_kind": [k[0] for _, k in rows],
            "account_class": [k[1] for _, k in rows]}


# --------------------------------------------------------------------------- sandboxes, git and the recorder


def _git_read(*args: str) -> str:
    """A read-only git command in the experiments folder of this checkout."""
    return subprocess.run(["git", *args], cwd=EXPERIMENTS, capture_output=True, text=True, encoding="utf-8",
                          check=True).stdout


def commit_exists(rev: str = GATE_A) -> bool:
    out = subprocess.run(["git", "cat-file", "-e", f"{rev}^{{commit}}"], cwd=EXPERIMENTS, capture_output=True)
    return out.returncode == 0


def commit_time(rev: str) -> datetime:
    """The committer date of the commit ``rev`` with its UTC offset (git log, read only)."""
    return datetime.fromisoformat(_git_read("log", "-1", "--format=%cI", rev).strip())


def git_blob(rev: str, rel: str) -> bytes | None:
    """The bytes of experiments/``rel`` at ``rev`` (git show, read only), or None."""
    out = subprocess.run(["git", "show", f"{rev}:./{rel}"], cwd=EXPERIMENTS, capture_output=True)
    return out.stdout if out.returncode == 0 else None


@functools.lru_cache(maxsize=8)
def commit_files(rev: str = GATE_A, dirs: tuple[str, ...] = SANDBOX_DIRS) -> tuple[tuple[str, bytes], ...] | None:
    """Every file of ``dirs`` (relative to experiments/) at ``rev`` with its bytes, from git ls-tree and one git
    cat-file --batch (read only); None when the commit is missing."""
    if not commit_exists(rev):
        return None
    prefix = _git_read("rev-parse", "--show-prefix").strip()
    names = [n for n in _git_read("ls-tree", "-r", "--name-only", "--full-name", rev, "--", *dirs).splitlines() if n]
    spec = "".join(f"{rev}:{n}\n" for n in names).encode("utf-8")
    out = subprocess.run(["git", "cat-file", "--batch"], cwd=EXPERIMENTS, input=spec, capture_output=True,
                         check=True).stdout
    files, pos = [], 0
    for n in names:
        nl = out.index(b"\n", pos)
        head = out[pos:nl].decode("utf-8").split()
        if len(head) != 3 or head[1] != "blob":
            raise RuntimeError(f"git cat-file gave {head} for {rev}:{n}")
        size = int(head[2])
        files.append((n[len(prefix):] if prefix and n.startswith(prefix) else n, out[nl + 1:nl + 1 + size]))
        pos = nl + 1 + size + 1
    return tuple(files)


def git_env(root: Path, base: dict | None = None) -> dict:
    """The environment of a git command (or of a script that runs git) in the sandbox ``root``: no system or global
    configuration (GIT_CONFIG_GLOBAL is an empty file inside root/.git), no GIT_* variable of the caller, and a
    ceiling at root's parent, so git never finds a repository above the sandbox."""
    env = {k: v for k, v in (base if base is not None else os.environ).items() if not k.startswith("GIT_")}
    root = Path(root).resolve()
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=str(root / ".git" / "c12-empty-global-config"),
               GIT_CEILING_DIRECTORIES=str(root.parent), GIT_TERMINAL_PROMPT="0")
    return env


_GIT_FLAGS = ("-c", "core.autocrlf=false", "-c", "commit.gpgsign=false", "-c", "init.defaultBranch=main",
              "-c", "user.name=c12 sandbox", "-c", "user.email=c12-sandbox@example.invalid")


def _git_in(root: Path, cwd: Path, args: tuple[str, ...], check: bool = True) -> str:
    out = subprocess.run(["git", *_GIT_FLAGS, *args], cwd=cwd, env=git_env(root), capture_output=True, text=True,
                         encoding="utf-8")
    if check and out.returncode:
        raise RuntimeError(f"git {' '.join(args)} failed in {cwd}: {out.stderr.strip()}")
    return out.stdout


def sandbox_git(exp_or_root: Path, *args: str, check: bool = True) -> str:
    """Run git with the isolated configuration in a sandbox repository (cwd its experiments folder or its root);
    return stdout, or raise RuntimeError on failure when ``check``."""
    path = Path(exp_or_root)
    root = path if (path / ".git").exists() else path.parent
    return _git_in(root, path, args, check)


def init_repo(root: Path) -> str:
    """Make ``root`` a git repository holding exactly experiments/{scripts,config,docs} in one commit (isolated
    configuration, core.autocrlf false); data written later stays untracked. Returns HEAD."""
    root = _guard(Path(root))
    _git_in(root, root, ("init", "-q"))
    (root / ".git" / "c12-empty-global-config").write_text("", encoding="utf-8")
    for key, value in (("core.autocrlf", "false"), ("commit.gpgsign", "false"), ("user.name", "c12 sandbox"),
                       ("user.email", "c12-sandbox@example.invalid")):
        _git_in(root, root, ("config", key, value))
    _git_in(root, root, ("add", "-A", "--", *(f"experiments/{d}" for d in SANDBOX_DIRS)))
    _git_in(root, root, ("commit", "-q", "-m", "sandbox"))
    return _git_in(root, root, ("rev-parse", "HEAD")).strip()


def sandbox(tmp: Path, code: str = "worktree", git: bool = False) -> Path:
    """Create ``tmp``/experiments/{scripts,config,docs}: with code "worktree" copied from this checkout's experiments
    folder (no __pycache__), otherwise the files of the commit ``code`` (e.g. GATE_A) from git (the test is skipped
    when the commit is missing). With ``git``, tmp becomes a repository holding exactly those files in one commit
    (init_repo). Returns tmp/experiments, which is common.ROOT of a script run from it."""
    root = _guard(Path(tmp))
    exp = root / "experiments"
    if code == "worktree":
        for d in SANDBOX_DIRS:
            shutil.copytree(EXPERIMENTS / d, exp / d, dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"))
    else:
        files = commit_files(code)
        if files is None:
            import pytest

            pytest.skip(f"commit {code} is not in this repository")
        for rel, data in files:
            path = exp / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    if git:
        init_repo(root)
    return exp


def snapshot(root: Path) -> dict[str, str]:
    """{path relative to root: SHA-256} of every file under ``root`` outside .git."""
    root = Path(root)
    out = {}
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root)
        if ".git" not in rel.parts and p.is_file():
            out[rel.as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def variant_env(variant: str | None, base: dict | None = None) -> dict:
    """The environment of a script run under ``variant`` (None or 'registered': unset): no bytecode, UTF-8 output, no
    RPC URL (the run_py pattern of the gate A tests)."""
    env = dict(base if base is not None else os.environ)
    env.update(PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
    env.pop("CONTRACT_REP_VARIANT", None)
    env.pop("CONTRACT_REP_RPC_URL", None)
    if variant and variant != "registered":
        env["CONTRACT_REP_VARIANT"] = variant
    return env


# The recorder: ``python -c RECORDER <exp> <script> <record path or ""> <flags json>`` imports the script from
# exp/scripts and runs its main(). Before that it installs wrappers that log every stats.PairedBootstrap (its n and
# every vector added), every graphs.score_all call (tag, methods, isolated ids) and every common.read_parts stem
# (relative to exp), and forces PairedBootstrap.prefetch to one process (the results do not depend on the workers).
# Flags: traps (contract12m: labels.load_closes, trader_labels, strata_tau and account_types raise), git_trap (git or
# bq run by subprocess.run raises), argv, paths (common attributes set before graphs and labels bind them; O9) and
# fake_bigquery (a google.cloud.bigquery whose Client raises). The record is written even when main() fails.
RECORDER = r'''
import json, subprocess, sys, types
from pathlib import Path
EXP, SCRIPT, REC, FLAGS = Path(sys.argv[1]), sys.argv[2], sys.argv[3], json.loads(sys.argv[4])
sys.path.insert(0, str(EXP / "scripts"))
sys.argv = [SCRIPT + ".py", *FLAGS.get("argv", [])]
import numpy as np
if FLAGS.get("fake_bigquery"):
    import google.cloud
    bq = types.ModuleType("google.cloud.bigquery")
    def _no_client(*a, **k):
        raise AssertionError("BigQuery client")
    bq.Client = _no_client
    sys.modules["google.cloud.bigquery"] = bq
    google.cloud.bigquery = bq
import common
for name, path in FLAGS.get("paths", {}).items():
    setattr(common, name, Path(path))
log = {"boot": [], "score_all": [], "read_parts": []}
_read = common.read_parts
def read_parts(stem, columns=None):
    try:
        rel = Path(stem).resolve().relative_to(EXP.resolve()).as_posix()
    except ValueError:
        rel = str(stem)
    log["read_parts"].append(rel)
    return _read(stem, columns)
common.read_parts = read_parts
import stats, graphs, labels
_init, _add, _pre = stats.PairedBootstrap.__init__, stats.PairedBootstrap.add, stats.PairedBootstrap.prefetch
def init(self, n, n_boot=400, seed=42, ci=0.95):
    _init(self, n, n_boot, seed, ci)
    log["boot"].append({"n": int(n), "n_boot": int(n_boot), "seed": int(seed), "vectors": {}})
    self._rec = log["boot"][-1]
def add(self, name, values):
    _add(self, name, values)
    self._rec["vectors"][name] = [float(x) for x in np.asarray(values, dtype=np.float64)]
stats.PairedBootstrap.__init__, stats.PairedBootstrap.add = init, add
stats.PairedBootstrap.prefetch = lambda self, pairs, workers=1: _pre(self, pairs, 1)
_score_all = graphs.score_all
def score_all(g, params=None, methods=None, isolated=None):
    log["score_all"].append({"tag": g.tag, "methods": None if methods is None else sorted(methods),
                             "isolated": None if isolated is None else sorted(int(x) for x in isolated)})
    return _score_all(g, params, methods, isolated)
graphs.score_all = score_all
def _trap(name):
    def f(*a, **k):
        raise AssertionError(f"labels.{name} was called")
    return f
if FLAGS.get("traps"):
    for name in ("load_closes", "trader_labels", "strata_tau", "account_types"):
        setattr(labels, name, _trap(name))
if FLAGS.get("git_trap"):
    _run = subprocess.run
    def run(cmd, *a, **k):
        head = cmd[0] if isinstance(cmd, (list, tuple)) else str(cmd).split()[0]
        if Path(str(head)).stem.lower() in ("git", "bq"):
            raise AssertionError(f"{head} was called")
        return _run(cmd, *a, **k)
    subprocess.run = run
import importlib
mod = importlib.import_module(SCRIPT)
try:
    rc = mod.main()
finally:
    if REC:
        Path(REC).write_text(json.dumps(log), encoding="utf-8")
sys.exit(rc)
'''


def run_script(exp: Path, script: str, variant: str | None, *, rec: Path | None = None, traps: bool = True,
               git_trap: bool = False, argv: Iterable[str] = (), paths: dict | None = None,
               fake_bigquery: bool = False, timeout: float = 900) -> subprocess.CompletedProcess:
    """Run scripts/``script``.py of the sandbox ``exp`` under ``variant`` through RECORDER (cwd exp, no bytecode); the
    record goes to ``rec`` when given. Git always gets the sandbox's isolated configuration and a ceiling at the
    sandbox root's parent, so a script never reaches a repository outside the sandbox."""
    exp = Path(exp)
    flags = {"traps": bool(traps), "git_trap": bool(git_trap), "argv": [str(a) for a in argv],
             "paths": {k: str(v) for k, v in (paths or {}).items()}, "fake_bigquery": bool(fake_bigquery)}
    env = git_env(exp.parent, variant_env(variant))
    return subprocess.run([sys.executable, "-c", RECORDER, str(exp), script, str(rec) if rec else "",
                           json.dumps(flags)], cwd=exp, env=env, capture_output=True, text=True, encoding="utf-8",
                          timeout=timeout)


def load_record(rec: Path | dict) -> dict:
    return rec if isinstance(rec, dict) else json.loads(Path(rec).read_text(encoding="utf-8"))


def boots(rec: Path | dict, *, n: int | None = None, has: Iterable[str] = ()) -> list[dict]:
    """The recorded PairedBootstrap instances with ``n`` members (any n when None) that hold every vector name in
    ``has``, in creation order; each is {"n", "n_boot", "seed", "vectors": {name: [values in member order]}}. The
    member order is the cohort's node ids in increasing order (the scripts sort by id)."""
    want = tuple(has)
    return [b for b in load_record(rec)["boot"]
            if (n is None or b["n"] == n) and all(h in b["vectors"] for h in want)]


# --------------------------------------------------------------------------- SQL text and BigQuery expressions

_FULL_NAME = re.compile(r"`dissertation-bq\.contract_rep\.([A-Za-z0-9_]+)`")


def sql_text(name: str, subs: dict[str, str] | None = None) -> str:
    """The text of a SQL file: ``name`` relative to experiments/ ("sql/16_usd_labels.sql") or a file name of sql/;
    ``subs`` replaces each __KEY__ (run_bq's --sub) by its value."""
    path = EXPERIMENTS / name if "/" in name.replace("\\", "/") else SQL / name
    out = path.read_text(encoding="utf-8")
    for key, value in (subs or {}).items():
        out = out.replace(f"__{key}__", value)
    return out


text = sql_text


def normal(s: str) -> str:
    """SQL text without comments (--...), with `dissertation-bq.contract_rep.X` written `X` and whitespace collapsed to
    one space."""
    s = re.sub(r"--[^\n]*", "", s)
    s = _FULL_NAME.sub(r"`\1`", s)
    return re.sub(r"\s+", " ", s).strip()


def lines(name: str, a: int, b: int, subs: dict[str, str] | None = None) -> str:
    """normal() of lines a..b (1-based, inclusive) of a SQL file."""
    return normal("\n".join(sql_text(name, subs).splitlines()[a - 1:b]))


def _mask(s: str) -> str:
    """``s`` with the contents of string literals and quoted names replaced by '_' (same length)."""
    out, q, i = list(s), None, 0
    while i < len(s):
        c = s[i]
        if q:
            if c == "\\" and q == "'" and i + 1 < len(s):
                out[i] = out[i + 1] = "_"
                i += 2
                continue
            if c == q:
                q = None
            else:
                out[i] = "_"
        elif c in ("'", "`", '"'):
            q = c
        i += 1
    return "".join(out)


def _depths(masked: str) -> list[int]:
    """The parenthesis depth of each character (a parenthesis has the depth outside it)."""
    out, d = [], 0
    for c in masked:
        if c == ")":
            d -= 1
        out.append(d)
        if c == "(":
            d += 1
    return out


def statement(sql: str, table: str) -> str:
    """The normalised text from ``CREATE OR REPLACE TABLE `table``` to the ';' that ends it (depth 0), inclusive."""
    s = normal(sql)
    head = f"CREATE OR REPLACE TABLE `{table}`"
    i = s.find(head)
    if i < 0:
        raise ValueError(f"no statement creates {table}")
    m = _mask(s)
    depth = 0
    for j in range(i, len(s)):
        if m[j] == "(":
            depth += 1
        elif m[j] == ")":
            depth -= 1
        elif m[j] == ";" and depth == 0:
            return s[i:j + 1]
    return s[i:]


def select_aliases(stmt: str) -> list[str]:
    """The output names of the last top-level SELECT ... FROM of a statement (depth 0, after the WITH list), split at
    depth-0 commas; a name is the word after the last depth-0 AS, or the part after the last '.' (p.n_tokens ->
    n_tokens)."""
    s = stmt.strip().rstrip(";")
    m = _mask(s)
    d = _depths(m)
    selects = [x.end() for x in re.finditer(r"\bSELECT\b", m, re.I) if d[x.start()] == 0]
    if not selects:
        raise ValueError("no top-level SELECT")
    start = selects[-1]
    ends = [x.start() for x in re.finditer(r"\bFROM\b", m, re.I) if x.start() > start and d[x.start()] == 0]
    end = ends[0] if ends else len(s)
    lead = re.match(r"\s*DISTINCT\b", m[start:end], re.I)
    a = start + (lead.end() if lead else 0)
    cuts = [j for j in range(a, end) if m[j] == "," and d[j] == 0]
    names = []
    for lo, hi in zip([a, *(c + 1 for c in cuts)], [*cuts, end]):
        item, mi = s[lo:hi], m[lo:hi]
        ases = [x.end() for x in re.finditer(r"\sAS\s", mi, re.I) if d[lo + x.start()] == 0]
        name = item[ases[-1]:] if ases else item.rsplit(".", 1)[-1]
        names.append(name.strip().strip("`"))
    return names


_TOKEN = re.compile(r"(?P<num>(?:\d+\.\d*|\.\d+|\d+)(?:[eE][+-]?\d+)?)|(?P<str>'(?:[^'\\]|\\.)*')"
                    r"|(?P<param>@[A-Za-z_]\w*)|(?P<quoted>`[^`]+`)|(?P<name>[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)"
                    r"|(?P<op><=|>=|!=|<>|[=<>+\-*/(),])")
_KEYWORDS = {"OR", "AND", "NOT", "IS", "NULL", "TRUE", "FALSE", "CAST", "AS"}
_FUNCS = {"LEAST": (1, None), "GREATEST": (1, None), "IF": (3, 3), "POW": (2, 2), "POWER": (2, 2), "IFNULL": (2, 2)}
_CMP = {"=": operator.eq, "!=": operator.ne, "<>": operator.ne, "<": operator.lt, "<=": operator.le,
        ">": operator.gt, ">=": operator.ge}
_ARITH = {"+": operator.add, "-": operator.sub, "*": operator.mul, "/": operator.truediv}


def _tokens(expr: str) -> list[tuple[str, str]]:
    out, pos = [], 0
    while True:
        while pos < len(expr) and expr[pos].isspace():
            pos += 1
        if pos >= len(expr):
            return out
        m = _TOKEN.match(expr, pos)
        if not m:
            raise ValueError(f"cannot read {expr[pos:pos + 20]!r} in {expr!r}")
        out.append((m.lastgroup, m.group(m.lastgroup)))
        pos = m.end()


class _Parser:
    """Recursive descent over the grammar of bq_eval; builds a tuple tree."""

    def __init__(self, expr: str):
        self.expr, self.t, self.i = expr, _tokens(expr), 0

    def _peek(self):
        return self.t[self.i] if self.i < len(self.t) else (None, None)

    def _fail(self, what: str):
        raise ValueError(f"{what} at token {self.i} of {self.expr!r}")

    def _kw(self, word: str) -> bool:
        kind, val = self._peek()
        return kind == "name" and val.upper() == word

    def _op(self, *ops: str) -> str | None:
        kind, val = self._peek()
        return val if kind == "op" and val in ops else None

    def _expect_op(self, op: str) -> None:
        if not self._op(op):
            self._fail(f"expected {op!r}")
        self.i += 1

    def parse(self):
        if not self.t:
            self._fail("empty expression")
        node = self._or()
        if self.i != len(self.t):
            self._fail("unexpected token")
        return node

    def _or(self):
        node = self._and()
        while self._kw("OR"):
            self.i += 1
            node = ("or", node, self._and())
        return node

    def _and(self):
        node = self._not()
        while self._kw("AND"):
            self.i += 1
            node = ("and", node, self._not())
        return node

    def _not(self):
        if self._kw("NOT"):
            self.i += 1
            return ("not", self._not())
        return self._cmp()

    def _cmp(self):
        left = self._add()
        op = self._op(*_CMP)
        if op:
            self.i += 1
            return ("cmp", op, left, self._add())
        if self._kw("IS"):
            self.i += 1
            negate = self._kw("NOT")
            if negate:
                self.i += 1
            if not self._kw("NULL"):
                self._fail("expected NULL after IS")
            self.i += 1
            return ("isnull", left, negate)
        return left

    def _add(self):
        node = self._mul()
        while (op := self._op("+", "-")):
            self.i += 1
            node = ("arith", op, node, self._mul())
        return node

    def _mul(self):
        node = self._unary()
        while (op := self._op("*", "/")):
            self.i += 1
            node = ("arith", op, node, self._unary())
        return node

    def _unary(self):
        if self._op("-"):
            self.i += 1
            return ("neg", self._unary())
        return self._atom()

    def _atom(self):
        kind, val = self._peek()
        if kind is None:
            self._fail("unexpected end")
        self.i += 1
        if kind == "num":
            return ("const", float(val) if any(c in val for c in ".eE") else int(val))
        if kind == "str":
            return ("const", re.sub(r"\\(.)", r"\1", val[1:-1]))
        if kind == "param":
            return ("param", val[1:])
        if kind == "quoted":
            return ("col", val[1:-1])
        if kind == "op":
            if val == "(":
                node = self._or()
                self._expect_op(")")
                return node
            self._fail(f"unexpected {val!r}")
        word = val.upper()
        if word in ("TRUE", "FALSE"):
            return ("const", word == "TRUE")
        if word == "NULL":
            return ("const", None)
        if word == "CAST":
            self._expect_op("(")
            node = self._or()
            if not self._kw("AS"):
                self._fail("expected AS in CAST")
            self.i += 1
            k, typ = self._peek()
            if k != "name" or typ.upper() not in ("INT64", "FLOAT64"):
                self._fail("expected INT64 or FLOAT64")
            self.i += 1
            self._expect_op(")")
            return ("cast", node, typ.upper())
        if self._op("("):
            if word not in _FUNCS:
                self._fail(f"unknown function {val}")
            self.i += 1
            args = []
            if not self._op(")"):
                args.append(self._or())
                while self._op(","):
                    self.i += 1
                    args.append(self._or())
            self._expect_op(")")
            lo, hi = _FUNCS[word]
            if len(args) < lo or (hi is not None and len(args) > hi):
                self._fail(f"{word} takes {lo if hi == lo else f'{lo} or more'} arguments")
            return ("call", "POW" if word == "POWER" else word, args)
        if word in _KEYWORDS:
            self._fail(f"unexpected keyword {val}")
        return ("col", val)


def _plain(v):
    """A numpy scalar as its Python value."""
    return v.item() if type(v).__module__ == "numpy" and hasattr(v, "item") else v


def _round_half_away(x: float) -> int:
    if not math.isfinite(x):
        raise ValueError(f"CAST of {x} AS INT64")
    return int(math.floor(abs(x) + 0.5)) * (1 if x >= 0 else -1)


def _eval(node, row: dict, params: dict):
    kind = node[0]
    if kind == "const":
        return node[1]
    if kind == "param":
        if node[1] not in params:
            raise KeyError(f"no parameter @{node[1]}")
        return _plain(params[node[1]])
    if kind == "col":
        name = node[1]
        if name in row:
            return _plain(row[name])
        if "." in name and name.rsplit(".", 1)[1] in row:
            return _plain(row[name.rsplit(".", 1)[1]])
        raise KeyError(f"no column {name}")
    if kind == "neg":
        v = _eval(node[1], row, params)
        return None if v is None else -v
    if kind == "not":
        v = _eval(node[1], row, params)
        return None if v is None else (not v)
    if kind == "and":
        a = _eval(node[1], row, params)
        if a is False:
            return False
        b = _eval(node[2], row, params)
        if b is False:
            return False
        return None if (a is None or b is None) else True
    if kind == "or":
        a = _eval(node[1], row, params)
        if a is True:
            return True
        b = _eval(node[2], row, params)
        if b is True:
            return True
        return None if (a is None or b is None) else False
    if kind == "isnull":
        v = _eval(node[1], row, params) is None
        return (not v) if node[2] else v
    if kind in ("cmp", "arith"):
        a, b = _eval(node[2], row, params), _eval(node[3], row, params)
        if a is None or b is None:
            return None
        return bool(_CMP[node[1]](a, b)) if kind == "cmp" else _ARITH[node[1]](a, b)
    if kind == "cast":
        v = _eval(node[1], row, params)
        if v is None:
            return None
        if node[2] == "FLOAT64":
            return float(v.strip()) if isinstance(v, str) else float(v)
        if isinstance(v, str):
            return int(v.strip())
        return int(v) if isinstance(v, (bool, int)) else _round_half_away(float(v))
    if kind == "call":
        fn, args = node[1], node[2]
        if fn == "IF":
            return _eval(args[1] if _eval(args[0], row, params) is True else args[2], row, params)
        if fn == "IFNULL":
            v = _eval(args[0], row, params)
            return v if v is not None else _eval(args[1], row, params)
        vals = [_eval(a, row, params) for a in args]
        if any(v is None for v in vals):
            return None
        if fn == "POW":
            return math.pow(float(vals[0]), float(vals[1]))
        if any(isinstance(v, float) and math.isnan(v) for v in vals):
            return math.nan
        out = (min if fn == "LEAST" else max)(vals)
        return float(out) if any(isinstance(v, float) for v in vals) else out
    raise ValueError(f"unknown node {kind}")


def bq_eval(expr: str, row: dict | None = None, params: dict | None = None):
    """Evaluate a BigQuery scalar expression of the subset the cap expressions use, with BigQuery's semantics.

    Grammar: or := and (OR and)*; and := not (AND not)*; not := NOT not | cmp; cmp := add ((= | != | <> | < | <= | >
    | >=) add | IS [NOT] NULL)?; add := mul ((+|-) mul)*; mul := unary ((*|/) unary)*; unary := - unary | atom; atom :=
    number | 'string' | TRUE | FALSE | NULL | @name | name[.name] | f(args) | CAST(expr AS INT64|FLOAT64) | (expr),
    f in LEAST, GREATEST, IF, POW (POWER), IFNULL. NULL is None; arithmetic and comparison with a NULL give NULL; AND
    is FALSE if a side is FALSE, else NULL if a side is NULL; OR mirrors it; NOT NULL is NULL; IF(c, a, b) is a only
    when c is TRUE; LEAST and GREATEST are NULL with a NULL argument (NaN with a NaN one); POW(a, b) = math.pow of the
    floats; CAST AS INT64 rounds half away from zero (the string parameter "6" gives 6); a column name with an alias
    prefix (b.bal_t1) reads row["b.bal_t1"], else row["bal_t1"]. A malformed expression raises ValueError, an unknown
    column or parameter KeyError."""
    return _eval(_Parser(expr).parse(), row or {}, params or {})


# --------------------------------------------------------------------------- the earlier variants' code path

PATH_FLAGS = {"CONTRACT_GRAPH": False, "TRADERS": True}      # the values under registered, usd and usd12m
# Top-level functions whose code may change while the earlier variants' behaviour is kept; each has a behavioural
# test (O2: graphs.load_graphs gained allow_stem, and its old call form gives the old result).
ALLOWED_CHANGES = {"graphs.load_graphs"}
CODE_PATH_FILES = ("scripts/common.py", "scripts/labels.py", "scripts/graphs.py", "scripts/usd.py",
                   "scripts/run_same_window.py", "scripts/run_holdout.py", "scripts/run_registered.py",
                   "scripts/run_robustness.py", "scripts/run_supplementary.py", "scripts/sybil_model.py",
                   "scripts/describe_data.py", "scripts/export_latex.py", "scripts/publish_results.py")


def _flag_value(test: ast.expr) -> bool | None:
    if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
        v = _flag_value(test.operand)
        return None if v is None else not v
    if isinstance(test, ast.Name) and test.id in PATH_FLAGS:
        return PATH_FLAGS[test.id]
    if (isinstance(test, ast.Attribute) and isinstance(test.value, ast.Name) and test.value.id == "common"
            and test.attr in PATH_FLAGS):
        return PATH_FLAGS[test.attr]
    return None


class _FoldFlags(ast.NodeTransformer):
    """Replace an if statement or conditional expression on a flag (or its not) by the branch the earlier variants
    take; a removed branch leaves nothing, a kept one is spliced in place."""

    def visit_If(self, node: ast.If):
        v = _flag_value(node.test)
        if v is None:
            return self.generic_visit(node)
        out = []
        for stmt in node.body if v else node.orelse:
            r = self.visit(stmt)
            out.extend(r if isinstance(r, list) else ([] if r is None else [r]))
        return out

    def visit_IfExp(self, node: ast.IfExp):
        v = _flag_value(node.test)
        if v is None:
            return self.generic_visit(node)
        return self.visit(node.body if v else node.orelse)


def _strip_docstrings(tree: ast.AST) -> None:
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            b = node.body
            if b and isinstance(b[0], ast.Expr) and isinstance(b[0].value, ast.Constant) \
                    and isinstance(b[0].value.value, str):
                node.body = b[1:]


def _imports(tree: ast.AST) -> tuple[set[str], dict[str, set[str]]]:
    """The modules of plain imports and {module: names} of from-imports anywhere in ``tree``."""
    plain, froms = set(), {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            plain |= {a.name for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            froms.setdefault(("." * node.level) + (node.module or ""), set()).update(a.name for a in node.names)
    return plain, froms


class _PruneImports(ast.NodeTransformer):
    """Remove every import of a module the base lacks and, from a from-import, the names the base lacks (check H3)."""

    def __init__(self, plain: set[str], froms: dict[str, set[str]]):
        self.plain, self.froms = plain, froms

    def visit_Import(self, node: ast.Import):
        node.names = [a for a in node.names if a.name in self.plain]
        return node if node.names else None

    def visit_ImportFrom(self, node: ast.ImportFrom):
        have = self.froms.get(("." * node.level) + (node.module or ""))
        if have is None:
            return None
        node.names = [a for a in node.names if a.name in have]
        return node if node.names else None


def _defined(node: ast.stmt) -> set[str] | None:
    """The names a top-level def, class or assignment to plain names defines; None for any other statement."""
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return {node.name}
    targets = (node.targets if isinstance(node, ast.Assign) else
               [node.target] if isinstance(node, (ast.AnnAssign, ast.AugAssign)) else None)
    if targets is None:
        return None
    names: set[str] = set()
    for t in targets:
        for e in (t.elts if isinstance(t, (ast.Tuple, ast.List)) else [t]):
            e = e.value if isinstance(e, ast.Starred) else e
            if not isinstance(e, ast.Name):
                return None
            names.add(e.id)
    return names


def earlier_path(src: str, base: str | None = None) -> ast.Module:
    """The AST that the variants registered, usd and usd12m execute (partial evaluation of CONTRACT_GRAPH = False and
    TRADERS = True, docstrings removed). With ``base`` (the d39775c source of the same file) also: every import of a
    module the base does not import is removed, and from a from-import the names the base does not import from it
    (check H3); a top-level def, class or assignment whose names are all absent from the base's top-level names is
    removed (the new functions and constants of contract12m). The comparison is ast.dump(earlier_path(old)) ==
    ast.dump(earlier_path(new, base=old)); see code_path_differences."""
    tree = _FoldFlags().visit(ast.parse(src))
    _strip_docstrings(tree)
    if base is not None:
        plain, froms = _imports(ast.parse(base))
        tree = _PruneImports(plain, froms).visit(tree)
        known: set[str] = set()
        for node in earlier_path(base).body:
            known |= _defined(node) or set()
        tree.body = [n for n in tree.body if not (d := _defined(n)) or d & known]
    return tree


def _keyed(tree: ast.Module) -> list[tuple[str, str]]:
    out = []
    for node in tree.body:
        d = _defined(node)
        key = ",".join(sorted(d)) if d else f"<{type(node).__name__}: {ast.unparse(node).splitlines()[0][:80]}>"
        out.append((key, ast.dump(node)))
    return out


def code_path_differences(module: str, old: str, new: str) -> list[str]:
    """The top-level names (or statements) whose earlier-variant code differs between ``old`` (the d39775c source) and
    ``new``; empty when the earlier variants execute the statements of d39775c. ``module`` ("graphs" or
    "scripts/graphs.py") selects the entries of ALLOWED_CHANGES that are left out of the comparison."""
    name = Path(module).stem
    allowed = {n.split(".", 1)[1] for n in ALLOWED_CHANGES if n.split(".", 1)[0] == name}
    a = [kd for kd in _keyed(earlier_path(old)) if kd[0] not in allowed]
    b = [kd for kd in _keyed(earlier_path(new, base=old)) if kd[0] not in allowed]
    if a == b:
        return []
    keys = list(dict.fromkeys(k for k, _ in (*a, *b)))
    diff = [k for k in keys if [d for kk, d in a if kk == k] != [d for kk, d in b if kk == k]]
    return diff or ["<the order of the top-level statements>"]


def project_imports(script: str, scripts: Path | None = None) -> set[str]:
    """{"scripts/<name>.py"} of ``script`` and of every module of scripts/ that it imports, through import and from
    statements anywhere (inside functions too), transitively (the script itself included)."""
    folder = Path(scripts) if scripts is not None else SCRIPTS
    todo, seen = [Path(script).stem], set()
    while todo:
        name = todo.pop()
        if name in seen:
            continue
        seen.add(name)
        tree = ast.parse((folder / f"{name}.py").read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                mods = [a.name.split(".")[0] for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
                mods = [node.module.split(".")[0]]
            else:
                continue
            todo += [m for m in mods if m not in seen and (folder / f"{m}.py").is_file()]
    return {f"scripts/{n}.py" for n in seen}
