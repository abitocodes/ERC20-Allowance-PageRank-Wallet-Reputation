"""Folder layout of the project, kept in one place.

Scripts take their folders from here or from config/margin_config.yaml, whose
relative paths are resolved against ROOT. data/README.md explains every folder.
This module uses the standard library only, so the citation and migration
helpers can import it without the data packages.

The folders were renamed on 1 October 2026. LEGACY_DIRS maps each old name to
its new one. The registration config/fresh_holdout_2026q3.yaml is frozen and
still uses the old names, so fresh_holdout.load_registration translates its
paths with current_path().
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # wallet-reputation-experiments/
WORKS_DIR = ROOT.parent  # 1-Dissertation-Works/<title>/dissertation/
REPO_ROOT = WORKS_DIR.parents[2]  # phd_works/
MANUSCRIPT_DIR = WORKS_DIR / "overleaf-github"  # dissertation LaTeX (git submodule)
EN_LEFTOVER_DIR = WORKS_DIR / "local-other" / "en-leftover"
# How the scripts folder is named from the repository root, for generated headers.
SCRIPTS_IN_REPO = (ROOT.relative_to(REPO_ROOT) / "scripts").as_posix()

CONFIG_DIR = ROOT / "config"
SQL_DIR = ROOT / "sql"
DATA_DIR = ROOT / "data"

# Folder names relative to ROOT, in the order the data flow through them.
ABI = "data/0-gmx-abi-for-decoding-logs"
RAW = "data/1-raw-blockchain-logs"
RAW_OBSERVATION = f"{RAW}/observation-window-2025-12-to-2026-05"
RAW_REPLICATION = f"{RAW}/registered-replication-2026-06-to-2026-08"
RAW_TIER2 = f"{RAW}/expanded-pool-tier2-2025-12-to-2026-05"
PROCESSED = "data/2-processed-tables-and-evaluations"
SPRING_HOLDOUT = f"{PROCESSED}/spring-holdout-2026-03-to-2026-05"
REPLICATION = f"{PROCESSED}/registered-replication-2026-06-to-2026-08"
PUBLISHED = "data/3-published-results-for-thesis"
PUBLISHED_CONFIG = f"{PUBLISHED}/config-copies"
PUBLISHED_SPRING_HOLDOUT = f"{PUBLISHED}/spring-holdout-2026-03-to-2026-05"
PUBLISHED_REPLICATION = f"{PUBLISHED}/registered-replication-2026-06-to-2026-08"
ARCHIVE = "data/4-archived-extended-baselines"

ABI_DIR = ROOT / ABI
RAW_DIR = ROOT / RAW
RAW_OBSERVATION_DIR = ROOT / RAW_OBSERVATION
RAW_REPLICATION_DIR = ROOT / RAW_REPLICATION
PROCESSED_DIR = ROOT / PROCESSED
SPRING_HOLDOUT_DIR = ROOT / SPRING_HOLDOUT
REPLICATION_DIR = ROOT / REPLICATION
PUBLISHED_DIR = ROOT / PUBLISHED
PUBLISHED_SPRING_HOLDOUT_DIR = ROOT / PUBLISHED_SPRING_HOLDOUT
PUBLISHED_REPLICATION_DIR = ROOT / PUBLISHED_REPLICATION
ARCHIVE_DIR = ROOT / ARCHIVE

# (old path, new path), both relative to ROOT. A longer old path wins over a
# shorter one, so the entries for single files and subfolders come first.
LEGACY_DIRS: tuple[tuple[str, str], ...] = (
    ("abis", ABI),
    ("data/raw/reputation/approvals", f"{RAW_OBSERVATION}/erc20-approval-logs"),
    ("data/raw/reputation/transfers", f"{RAW_OBSERVATION}/erc20-transfer-logs"),
    ("data/raw/gmx", f"{RAW_OBSERVATION}/gmx-position-close-logs"),
    ("data/raw/lending", f"{RAW_OBSERVATION}/aave-lending-logs"),
    (
        "data/raw/gmx_event_logs_2025-12_to_2026-05.parquet",
        f"{RAW_OBSERVATION}/gmx_event_logs_2025-12_to_2026-05.parquet",
    ),
    ("data/raw/fresh_2026q3/approvals", f"{RAW_REPLICATION}/erc20-approval-logs"),
    ("data/raw/fresh_2026q3/transfers", f"{RAW_REPLICATION}/erc20-transfer-logs"),
    ("data/raw/fresh_2026q3/gmx", f"{RAW_REPLICATION}/gmx-position-close-logs"),
    ("data/raw/fresh_2026q3", RAW_REPLICATION),
    ("data/raw/reputation_tier2/approvals", f"{RAW_TIER2}/erc20-approval-logs"),
    ("data/raw/reputation_tier2/transfers", f"{RAW_TIER2}/erc20-transfer-logs"),
    ("data/raw/reputation_tier2", RAW_TIER2),
    ("data/raw", RAW),
    ("data/processed/reputation_tier2", f"{PROCESSED}/expanded-pool-tier2-allowances-and-transfers"),
    ("data/processed/reputation", f"{PROCESSED}/erc20-allowances-and-transfers"),
    ("data/processed/lending", f"{PROCESSED}/aave-lending-events"),
    ("data/processed/holdout", SPRING_HOLDOUT),
    ("data/processed/fresh_2026q3", REPLICATION),
    ("data/processed/active_wallet_cache", f"{PROCESSED}/active-wallet-sampling-cache"),
    (
        "data/processed/method_proxy_matrix.csv",
        f"{ARCHIVE}/superseded-before-2026-09-30-sign-fix/method_proxy_matrix.csv",
    ),
    (
        "data/processed/six_aave_method_proxy_matrix.csv",
        f"{ARCHIVE}/superseded-before-2026-09-30-sign-fix/six_aave_method_proxy_matrix.csv",
    ),
    ("data/processed", PROCESSED),
    ("data/archive/extended-baselines", ARCHIVE),
    ("results/config", PUBLISHED_CONFIG),
    ("results/holdout", PUBLISHED_SPRING_HOLDOUT),
    ("results/fresh_2026q3", PUBLISHED_REPLICATION),
    ("results", PUBLISHED),
)

_BY_LENGTH = sorted(LEGACY_DIRS, key=lambda pair: len(pair[0]), reverse=True)


def current_path(rel: str) -> str:
    """Translate a path relative to ROOT from the old folder names to the new ones.

    Paths that do not start with an old name are returned unchanged (with
    forward slashes), so the function is safe on paths that are already new.
    """
    posix = rel.replace("\\", "/")
    while posix.startswith("./"):
        posix = posix[2:]
    for old, new in _BY_LENGTH:
        if posix == old or posix.startswith(old + "/"):
            return new + posix[len(old) :]
    return posix
