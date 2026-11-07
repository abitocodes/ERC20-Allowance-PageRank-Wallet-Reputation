"""Shared helpers: configuration, paths, and parquet files split below GitHub's size limit.

Four analyses share this code. The registered analysis (raw base units, every token) is the
default. Setting the environment variable CONTRACT_REP_VARIANT=usd selects the revised
analysis of docs/revision_price_weighting.md (listed tokens, amounts in USD): the graph tables
are then read from graph-tables-usd and every result is written under revised-usd, so the
registered inputs and outputs are never overwritten. CONTRACT_REP_VARIANT=usd12m selects the
same US-dollar analysis on the twelve-month score windows of docs/revision_one_year_window.md:
config/overlay_usd12m.yaml is merged over the configuration, the graph tables are read from
graph-tables-usd-12m and every result is written under revised-usd-12m.
CONTRACT_REP_VARIANT=contract12m selects the analysis of docs/revision_contract_graph.md on the
same windows: graphs whose nodes are contracts only, allowances capped at the owner's balance and
the discovery-order test of docs/discovery_protocol.md. config/overlay_contract12m.yaml is merged
over the configuration, the graph tables are read from graph-tables-contract-12m and every result
is written under revised-contract-12m.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Iterable

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "contract_reputation.yaml"
DATA = ROOT / "data"
RAW = DATA / "1-raw-blockchain-extracts"
# Inputs every analysis reads: account types, decoded GMX closes, the registered cohort.
PROC_SHARED = DATA / "2-processed-tables-and-evaluations"
USD_INPUTS = DATA / "0-usd-token-list-and-prices"

VARIANTS = ("registered", "usd", "usd12m", "contract12m")
VARIANT = os.environ.get("CONTRACT_REP_VARIANT", "registered")
if VARIANT not in VARIANTS:
    raise SystemExit(f"CONTRACT_REP_VARIANT must be one of {VARIANTS}, not {VARIANT!r}")
# Every variant but the registered one takes the revised code path; the twelve-month ones also
# their own windows; the contract-graph one also its own graphs (contracts only), types and test.
REVISED = VARIANT != "registered"
ONE_YEAR = VARIANT in ("usd12m", "contract12m")
CONTRACT_GRAPH = VARIANT == "contract12m"
# The GMX V2 trader cohorts and criteria belong to every variant but the contract-graph one
# (docs/revision_contract_graph.md section 2).
TRADERS = not CONTRACT_GRAPH

_FOLDER = {"registered": None, "usd": "revised-usd", "usd12m": "revised-usd-12m",
           "contract12m": "revised-contract-12m"}[VARIANT]
GRAPH = RAW / {"registered": "graph-tables", "usd": "graph-tables-usd", "usd12m": "graph-tables-usd-12m",
               "contract12m": "graph-tables-contract-12m"}[VARIANT]
PROC = PROC_SHARED / _FOLDER if REVISED else PROC_SHARED
PUB = DATA / "3-published-results-for-thesis" / _FOLDER if REVISED else DATA / "3-published-results-for-thesis"
# Rounded amount constants of the US-dollar variants (run_usd_pipeline.py, run_usd12m_pipeline.py,
# run_contract12m_pipeline.py).
USD_CONSTANTS = {"registered": USD_INPUTS / "constants.json", "usd": USD_INPUTS / "constants.json",
                 "usd12m": USD_INPUTS / "usd-12m" / "constants.json",
                 "contract12m": USD_INPUTS / "contract-12m" / "constants.json"}[VARIANT]
# Prefix of the BigQuery tables a revised variant writes.
BQ_PREFIX = {"registered": "u_", "usd": "u_", "usd12m": "u12_", "contract12m": "c12_"}[VARIANT]
# Folder of the W1 evaluation; the revised one is not registered and is not named so.
W1_DIR = "window-w1" if REVISED else "registered-w1"
# Account types of the contract-graph variant (scripts/check_account_code.py, revision section 4) and
# the twelve-month graph tables whose cohorts, spender sets and labels it keeps.
TYPES_DIR = RAW / "contract-types"
TYPES = TYPES_DIR / "c12_account_types"
GRAPH_U12 = RAW / "graph-tables-usd-12m"

# The overlay of a variant and the only keys it may set (it must set exactly these).
_OVERLAY_KEYS_USD12M = {("period", "start_ts"), ("holdout", "start_ts")}
_OVERLAY_KEYS_CONTRACT12M = _OVERLAY_KEYS_USD12M | {("bigquery", "budget_usd")} | {
    ("contract_graph", k) for k in (
        "typing_start", "typing_end", "pinned_block", "rpc_urls", "campaign_cap_usd", "system_address_max",
        "safe_threshold_max", "entry_points", "selectors", "erc1967_slot", "audit", "balance")
} | {
    ("discovery", k) for k in (
        "seed_salt", "random_salt", "n_seeds", "rho_grid", "runtime_budget_hours", "ns_per_edge_iteration",
        "warm_iterations", "projection_workers", "walk_solves", "q_primary", "q_small", "small_universe",
        "q_secondary", "x_primary", "x_secondary", "tie_tolerance", "lambda_primary", "lambda_grid",
        "both_mode_ratio", "stop_min_allow_edges", "stop_min_allow_share", "min_hot", "hub_drop",
        "rho_sensitivity", "curve_points", "min_usd_account")
}
OVERLAY_PATH = {"usd12m": ROOT / "config" / "overlay_usd12m.yaml",
                "contract12m": ROOT / "config" / "overlay_contract12m.yaml"}.get(VARIANT)
OVERLAY_KEYS = {"usd12m": _OVERLAY_KEYS_USD12M, "contract12m": _OVERLAY_KEYS_CONTRACT12M}.get(VARIANT, set())


def load_config() -> dict:
    cfg = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    if OVERLAY_PATH is not None:
        overlay = yaml.safe_load(OVERLAY_PATH.read_text(encoding="utf-8"))
        keys = {(section, key) for section, values in overlay.items() for key in values}
        if keys != OVERLAY_KEYS:
            raise SystemExit(f"{OVERLAY_PATH.name} must set exactly {sorted(OVERLAY_KEYS)}, not {sorted(keys)}")
        for section, values in overlay.items():
            cfg.setdefault(section, {}).update(values)
    return cfg


def max_part_bytes() -> int:
    return int(load_config()["storage"]["max_part_bytes"])


def _part_path(stem: Path, i: int) -> Path:
    return stem.parent / f"{stem.name}.part{i:03d}.parquet"


def part_paths(stem: Path) -> list[Path]:
    stem = Path(stem)
    return sorted(stem.parent.glob(f"{stem.name}.part[0-9][0-9][0-9].parquet"))


def clear_parts(stem: Path) -> None:
    for p in part_paths(stem):
        p.unlink()


def write_parts(df: pd.DataFrame | pa.Table, stem: Path, limit: int | None = None) -> list[Path]:
    """Write a table as stem.part000.parquet, stem.part001.parquet, ... each below ``limit`` bytes."""
    stem = Path(stem)
    stem.parent.mkdir(parents=True, exist_ok=True)
    limit = limit or max_part_bytes()
    table = pa.Table.from_pandas(df, preserve_index=False) if isinstance(df, pd.DataFrame) else df
    clear_parts(stem)
    n = table.num_rows
    if n == 0:
        pq.write_table(table, _part_path(stem, 0), compression="zstd")
        return [_part_path(stem, 0)]
    # First guess from the in-memory size; compressed files are smaller, so this is safe.
    rows_per_part = max(1, int(n * limit * 0.8 / max(table.nbytes, 1)))
    rows_per_part = min(rows_per_part, n)
    paths: list[Path] = []
    start, i = 0, 0
    while start < n:
        size = min(rows_per_part, n - start)
        while True:
            path = _part_path(stem, i)
            pq.write_table(table.slice(start, size), path, compression="zstd")
            if path.stat().st_size <= limit or size == 1:
                break
            size = max(1, size // 2)
        paths.append(path)
        start += size
        i += 1
    return paths


class PartWriter:
    """Stream record batches into parts below ``limit`` bytes (for large downloads)."""

    def __init__(self, stem: Path, schema: pa.Schema, limit: int | None = None):
        self.stem = Path(stem)
        self.stem.parent.mkdir(parents=True, exist_ok=True)
        clear_parts(self.stem)
        self.schema = schema
        self.limit = limit or max_part_bytes()
        self.i = 0
        self.rows = 0
        self.pending: list[pa.RecordBatch] = []
        self.pending_bytes = 0
        self.ratio = 0.35  # compressed bytes per in-memory byte; updated after each part

    def write(self, batch: pa.RecordBatch) -> None:
        self.pending.append(batch)
        self.pending_bytes += batch.nbytes
        if self.pending_bytes * self.ratio >= self.limit * 0.85:
            self._flush()

    def _flush(self) -> None:
        if not self.pending:
            return
        table = pa.Table.from_batches(self.pending, schema=self.schema)
        self.pending, self.pending_bytes = [], 0
        start = 0
        while start < table.num_rows:
            size = table.num_rows - start
            while True:
                path = _part_path(self.stem, self.i)
                chunk = table.slice(start, size)
                pq.write_table(chunk, path, compression="zstd")
                if path.stat().st_size <= self.limit or size == 1:
                    break
                size = max(1, size // 2)
            self.ratio = max(0.05, path.stat().st_size / max(chunk.nbytes, 1))
            self.rows += size
            start += size
            self.i += 1

    def close(self) -> int:
        self._flush()
        if self.i == 0:
            pq.write_table(self.schema.empty_table(), _part_path(self.stem, 0), compression="zstd")
        return self.rows


def read_parts(stem: Path, columns: Iterable[str] | None = None) -> pd.DataFrame:
    paths = part_paths(Path(stem))
    if not paths:
        raise FileNotFoundError(f"no parts for {stem}")
    tables = [pq.read_table(p, columns=list(columns) if columns else None) for p in paths]
    return pa.concat_tables(tables).to_pandas()


def save_json(obj, path: Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=str), encoding="utf-8")


def load_json(path: Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))
