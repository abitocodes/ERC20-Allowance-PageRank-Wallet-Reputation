"""Folder layout: the old names translate to the new ones, and the folders exist."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from common import load_config  # noqa: E402
from project_paths import (  # noqa: E402
    LEGACY_DIRS,
    PROCESSED,
    PUBLISHED_CONFIG,
    RAW_REPLICATION,
    REPLICATION,
    SPRING_HOLDOUT,
    current_path,
)

# New paths that only exist on a machine that made them (ignored by git).
LOCAL_ONLY = {
    "data/1-raw-blockchain-logs/observation-window-2025-12-to-2026-05/gmx_event_logs_2025-12_to_2026-05.parquet",
    "data/1-raw-blockchain-logs/expanded-pool-tier2-2025-12-to-2026-05",
    "data/1-raw-blockchain-logs/expanded-pool-tier2-2025-12-to-2026-05/erc20-approval-logs",
    "data/1-raw-blockchain-logs/expanded-pool-tier2-2025-12-to-2026-05/erc20-transfer-logs",
    "data/2-processed-tables-and-evaluations/expanded-pool-tier2-allowances-and-transfers",
    "data/2-processed-tables-and-evaluations/active-wallet-sampling-cache",
}


def test_registration_paths_translate_to_the_new_folders() -> None:
    assert current_path("data/raw/fresh_2026q3/approvals") == f"{RAW_REPLICATION}/erc20-approval-logs"
    assert current_path("data/raw/fresh_2026q3/gmx") == f"{RAW_REPLICATION}/gmx-position-close-logs"
    assert (
        current_path("data/processed/fresh_2026q3/fresh_holdout_summary.json")
        == f"{REPLICATION}/fresh_holdout_summary.json"
    )
    assert current_path("data\\processed\\holdout\\eval_summary.json") == f"{SPRING_HOLDOUT}/eval_summary.json"
    assert current_path("results/config/margin_config.yaml") == f"{PUBLISHED_CONFIG}/margin_config.yaml"
    # Paths outside the old data folders, and paths that are already new, stay as they are.
    assert current_path("docs/fresh_holdout_2026q3_plan.md") == "docs/fresh_holdout_2026q3_plan.md"
    assert current_path(f"{PROCESSED}/eval_summary.json") == f"{PROCESSED}/eval_summary.json"
    assert current_path("data/rawish/x.parquet") == "data/rawish/x.parquet"


def test_every_new_folder_exists() -> None:
    missing = [new for _, new in LEGACY_DIRS if new not in LOCAL_ONLY and not (ROOT / new).exists()]
    assert not missing


def test_config_paths_point_at_existing_files() -> None:
    cfg = load_config()
    for key in ("manifest", "eval_summary", "decoded_events", "wallet_rankings", "aave_events"):
        assert Path(cfg["paths"][key]).is_file(), key
    for key in ("raw_gmx_dir", "raw_lending_dir"):
        assert Path(cfg["paths"][key]).is_dir(), key
    rep = cfg["reputation"]["paths"]
    for key in ("raw_approvals_dir", "raw_transfers_dir"):
        assert Path(rep[key]).is_dir(), key
    for key in ("latest_allowances", "holdout_summary"):
        assert Path(rep[key]).is_file(), key
    for key in ("supplemental_path", "wallet_set_path"):
        assert Path(cfg["benchmark"][key]).is_file(), key
