"""Path rules of scripts/drive_sync.py: Drive paths, local paths, exclusions and patterns."""

from __future__ import annotations

from pathlib import Path

import drive_sync as ds


def test_drive_path_maps_to_local_data_folders():
    assert ds.local_path("contract-reputation/1-raw-blockchain-extracts/graph-tables-usd/nodes.part000.parquet") == (
        ds.THESIS / "experiments/data/1-raw-blockchain-extracts/graph-tables-usd/nodes.part000.parquet")
    assert ds.local_path("wallet-reputation-archive/README.md") == (
        ds.THESIS / "archive/wallet-reputation-experiments/data/README.md")


def test_scratch_and_caches_are_not_published():
    assert ds.excluded(Path("_work/usd/llama_cache/x.json"))
    assert ds.excluded(Path("a/__pycache__/m.cpython-311.pyc"))
    assert ds.excluded(Path("a/_chunks/part.parquet"))
    assert ds.excluded(Path("run.log"))
    assert not ds.excluded(Path("1-raw-blockchain-extracts/graph-tables/nodes.part000.parquet"))
    assert not ds.excluded(Path("3-published-results-for-thesis/SHA256SUMS.txt"))


def test_patterns_match_drive_or_local_paths():
    path = "contract-reputation/1-raw-blockchain-extracts/graph-tables-usd/nodes.part000.parquet"
    assert ds.matches(path, [])
    assert ds.matches(path, ["*graph-tables-usd/*"])
    assert ds.matches(path, ["experiments/*"])
    assert ds.matches(path, ["contract-reputation/1-raw-blockchain-extracts/*"])
    assert not ds.matches(path, ["archive/*"])
    assert not ds.matches(path, ["*graph-tables/*"])
