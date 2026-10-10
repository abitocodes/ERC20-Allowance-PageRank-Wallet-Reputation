"""Shared helpers: configuration, paths, and parquet files split below GitHub's size limit.

Two analyses share this code. The registered analysis (raw base units, every token) is the
default. Setting the environment variable CONTRACT_REP_VARIANT=usd selects the revised
analysis of docs/revision_price_weighting.md (listed tokens, amounts in USD): the graph tables
are then read from graph-tables-usd and every result is written under revised-usd, so the
registered inputs and outputs are never overwritten.
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
# Inputs both analyses read: account types, decoded GMX closes, the registered cohort.
PROC_SHARED = DATA / "2-processed-tables-and-evaluations"
USD_INPUTS = DATA / "0-usd-token-list-and-prices"

VARIANTS = ("registered", "usd")
VARIANT = os.environ.get("CONTRACT_REP_VARIANT", "registered")
if VARIANT not in VARIANTS:
    raise SystemExit(f"CONTRACT_REP_VARIANT must be one of {VARIANTS}, not {VARIANT!r}")
REVISED = VARIANT == "usd"

GRAPH = RAW / ("graph-tables-usd" if REVISED else "graph-tables")
PROC = PROC_SHARED / "revised-usd" if REVISED else PROC_SHARED
PUB = DATA / "3-published-results-for-thesis" / "revised-usd" if REVISED else DATA / "3-published-results-for-thesis"
# Folder of the W1 evaluation; the revised one is not registered and is not named so.
W1_DIR = "window-w1" if REVISED else "registered-w1"


def load_config() -> dict:
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))


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
