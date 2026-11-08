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

# Revision section 13, amendment of 9 November 2026: the extension of rule 3(b) of section 4.2. A row of the account
# types of class 'contract' is an ERC-4337 smart account (a user account) when its code hash is one of
# SMART_ACCOUNT_CODE_HASHES (proxies whose implementation the reads did not find, whose entryPoint() answers a
# canonical EntryPoint, whose own code is under 1,000 bytes and holds no paymaster selector), or when its code hash
# and implementation are one of SMART_ACCOUNT_IMPLEMENTATIONS (ERC-1967 proxies whose implementation holds
# validateUserOp and no paymaster selector and whose getter entrypoint() answers a canonical EntryPoint where
# entryPoint() fails). The amendment lists the same hashes and pairs; sql/31 (through the driver) and the structure
# pilot apply them; the typing output itself is not changed.
SMART_ACCOUNT_CODE_HASHES = (
    "0x0ed708f4e57d108c41999c5eaa34e38ce9e6bf0d0ebbf6dac60b6347bbe3a4a8",
    "0x1a374b9ed6b9c65572908c91f378dc6c4842551ac3566d6178a09f1dac5f708c",
    "0x21a481460cae2e0cbc918d3a77952717329e0cebcfd0cd8b571862bcb4d72e0f",
    "0x224cbf029efc8dbf9c2a75dcd9547f2ba7381b87ef14e29a73b766b45e4a533a",
    "0x253d2969bd835560989486cc876d337029326df5839ca36e672b924c1cb5bb5f",
    "0x2da28852498b720ab99465e8071a86db5d7b140bbfe77a1f283d1e19008ede13",
    "0x44cf1655237a86d10311b58bb7c73b84c085547fc1f2ca0458f03ce1ec556431",
    "0x4e061efb5c32cc07b9897ff9708cb26bb1e8be8cb582b15958c493455b55429e",
    "0x5104ae4e0326617faf888e41bd81276be1b37f077db2069ec8faadc0d85848af",
    "0x5b50b88c3767222ffbb152eddb5aa6ce3af2b2d3d210574a31752a2f64c0b221",
    "0x64951b55b12734bd28b1ef7d44e179920ae140a7aa15a1c7060b63164537d45a",
    "0x7d29aab09ecd524c81f133bc42f1c02c2c33f6ac9ad4eaf7de6bdb186f6d54d5",
    "0x808e958888f4bc9faad84e95e69acdb166b376874fe050277baf44f25e474e75",
    "0x967c8038107958850922eab6979865c96543a7ebda23ac10a7be3046ccffedce",
    "0xa6a4f9a88a5438ed0261f7bb650cc0c5a9dff1572ba8459d18d412d7dd8bd7c7",
    "0xaab97b91d04ecaeb9f9feeec2d5b4b1f8efb56e2644f2c082bb77f35263af9a0",
    "0xd377b91daca76fd9e6f2b2f18e9618ce2eb4dddf7b4c5f9e1da125ab5d40c67a",
    "0xe152e0d0626438840037db419d2e66fa32002f1ee719b1dbe2892314bc67b6de",
    "0xeb943ca16c0a3d8c19be2c02105552f49d4ff1d02fb80b199b613f085c8c7847",
    "0xed06f222e28bb2ee7f9691685c021e3e6b4fd92d1593839b26ab9d3d7f2965bd",
)
_PROXY_AAA52C8C = "0xaaa52c8cc8a0e3fd27ce756cc6b4e70c51423e9b597b11f32d3e49f8b1fc890d"
_PROXY_8559595D = "0x8559595d851a6b7f1c4291abb8685e947a442e2639d6e305c94e3a3e5a39336a"
SMART_ACCOUNT_IMPLEMENTATIONS = ((_PROXY_8559595D, "0xd6cedde84be40893d153be9d467cd6ad37875b28"),) + tuple(
    (_PROXY_AAA52C8C, impl) for impl in (
        "0x654f12417cb258e73d4a87aa71b24adac5490f94",
        "0x94f097e1ebeb4eca3aae54cabb08905b239a7d27",
        "0xa3b9a42afded3431193bd73012d44a26ca04a0a1",
        "0xbac849bb641841b44e965fb01a4bf5f074f84b4d",
        "0xd6cedde84be40893d153be9d467cd6ad37875b28",
        "0xd830d15d3dc0c269f3dbaa0f3e8626d33cfdabe1",
    ))
# The typed contracts that the two lists move at block 513,216,506 (checked against the typing output).
SMART_ACCOUNT_TYPED = {"code_hashes": 37_337, "implementations": 155_319}


def smart_account_extension(types: pd.DataFrame) -> pd.Series:
    """True for each row of the account types (columns account_class, code_hash, implementation) that the amendment
    of 9 November 2026 (revision section 13) counts as an ERC-4337 smart account: a row of class 'contract' whose code
    hash is listed, or whose code hash and implementation are a listed pair."""
    code_hash = types["code_hash"].fillna("").astype(str).str.lower()
    implementation = types["implementation"].fillna("").astype(str).str.lower()
    pairs = pd.MultiIndex.from_arrays([code_hash, implementation]).isin(list(SMART_ACCOUNT_IMPLEMENTATIONS))
    return ((types["account_class"].astype(str) == "contract")
            & (code_hash.isin(SMART_ACCOUNT_CODE_HASHES) | pd.Series(pairs, index=types.index)))


def with_smart_account_extension(types: pd.DataFrame) -> pd.DataFrame:
    """The account types with the rows of smart_account_extension as smart accounts of wallet kind 'erc4337'."""
    out = types.copy()
    moved = smart_account_extension(out)
    out.loc[moved, "account_class"] = "smart_account"
    if "wallet_kind" in out.columns:
        out.loc[moved, "wallet_kind"] = "erc4337"
    return out


def smart_account_sql_params() -> dict[str, str]:
    """The two lists as the STRING parameters of sql/31_c12_contracts.sql: the code hashes joined by commas, and the
    pairs as code_hash:implementation joined by commas."""
    return {"ext_code_hashes": ",".join(SMART_ACCOUNT_CODE_HASHES),
            "ext_pairs": ",".join(f"{h}:{i}" for h, i in SMART_ACCOUNT_IMPLEMENTATIONS)}

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
