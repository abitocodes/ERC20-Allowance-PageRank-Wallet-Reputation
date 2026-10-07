"""Copy the machine-readable evaluation summaries into the published-results folder.

The evaluation scripts write their summaries to
data/2-processed-tables-and-evaluations/, and every new run overwrites them.
The dissertation tables are generated from a few of those JSON files, so they
and the configuration in force are copied to data/3-published-results-for-thesis/
and committed there. A manifest records the SHA-256 of each copy so a reader can
check that the committed summary is the one the tables came from.

Usage:
    python scripts/publish_results.py            # copy + manifest
    python scripts/publish_results.py --check    # verify the copies against the manifest and their sources
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from project_paths import (
    PROCESSED,
    PUBLISHED,
    PUBLISHED_CONFIG,
    PUBLISHED_DIR,
    PUBLISHED_REPLICATION,
    PUBLISHED_SPRING_HOLDOUT,
    REPLICATION,
    ROOT,
    SPRING_HOLDOUT,
)

RESULTS = PUBLISHED_DIR


def _inside_published(folder: str) -> str:
    return folder.removeprefix(PUBLISHED + "/")


# (source relative to ROOT, destination relative to RESULTS)
ARTIFACTS: tuple[tuple[str, str], ...] = (
    (f"{PROCESSED}/eval_summary.json", "eval_summary.json"),
    (
        f"{SPRING_HOLDOUT}/eval_summary_spenders.json",
        f"{_inside_published(PUBLISHED_SPRING_HOLDOUT)}/eval_summary_spenders.json",
    ),
    # Spring freeze on the matched traders, GMX labels (scored after the labels were known).
    (
        f"{SPRING_HOLDOUT}/eval_summary_matched_traders.json",
        f"{_inside_published(PUBLISHED_SPRING_HOLDOUT)}/eval_summary_matched_traders.json",
    ),
    (f"{PROCESSED}/supplementary_checks.json", "supplementary_checks.json"),
    ("config/margin_config.yaml", f"{_inside_published(PUBLISHED_CONFIG)}/margin_config.yaml"),
    # Registered replication, June-August 2026: the registration, its extraction
    # record (bytes billed, row counts, registration hashes) and the evaluation.
    ("config/fresh_holdout_2026q3.yaml", f"{_inside_published(PUBLISHED_CONFIG)}/fresh_holdout_2026q3.yaml"),
    (
        f"{REPLICATION}/extraction_manifest.json",
        f"{_inside_published(PUBLISHED_REPLICATION)}/extraction_manifest.json",
    ),
    (
        f"{REPLICATION}/fresh_holdout_summary.json",
        f"{_inside_published(PUBLISHED_REPLICATION)}/fresh_holdout_summary.json",
    ),
    # EndorseRank on the same cohorts and labels, scored after the registered evaluation.
    (
        f"{REPLICATION}/posthoc_endorserank.json",
        f"{_inside_published(PUBLISHED_REPLICATION)}/posthoc_endorserank.json",
    ),
)

# Git stores these files with LF line endings; a Windows checkout with
# core.autocrlf writes them with CRLF. Hashing them with LF endings gives the
# same value on both, so --check works on either checkout.
TEXT_SUFFIXES = {".json", ".yaml", ".yml", ".md", ".csv", ".txt"}


def _content(path: Path) -> bytes:
    data = path.read_bytes()
    if path.suffix.lower() in TEXT_SUFFIXES:
        data = data.replace(b"\r\n", b"\n")
    return data


def _sha256(path: Path) -> str:
    return hashlib.sha256(_content(path)).hexdigest()


def publish() -> int:
    manifest: dict[str, object] = {
        "published_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "files": [],
    }
    missing = []
    for src_rel, dst_rel in ARTIFACTS:
        src = ROOT / src_rel
        if not src.exists():
            missing.append(src_rel)
            continue
        dst = RESULTS / dst_rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        manifest["files"].append(  # type: ignore[union-attr]
            {
                "path": dst_rel,
                "source": src_rel,
                "sha256": _sha256(dst),
                "bytes": len(_content(dst)),
            }
        )
        print(f"copied {src_rel} -> {PUBLISHED}/{dst_rel}")
    (RESULTS / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"manifest -> {PUBLISHED}/MANIFEST.json ({len(manifest['files'])} files)")  # type: ignore[arg-type]
    if missing:
        print("missing sources (not copied): " + ", ".join(missing), file=sys.stderr)
        return 1
    return 0


def check() -> int:
    manifest_path = RESULTS / "MANIFEST.json"
    if not manifest_path.exists():
        print(f"{PUBLISHED}/MANIFEST.json not found; run without --check first", file=sys.stderr)
        return 1
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    bad = 0
    for entry in manifest["files"]:
        dst = RESULTS / entry["path"]
        if not dst.exists():
            print(f"MISSING  {PUBLISHED}/{entry['path']}")
            bad += 1
            continue
        actual = _sha256(dst)
        state = "ok      " if actual == entry["sha256"] else "CHANGED "
        bad += actual != entry["sha256"]
        src = ROOT / entry["source"]
        if src.exists() and _sha256(src) != actual:
            state = "STALE   "
            bad += 1
        print(f"{state} {PUBLISHED}/{entry['path']}")
    return 1 if bad else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--check", action="store_true", help="verify the published copies against MANIFEST.json and their sources"
    )
    args = parser.parse_args()
    return check() if args.check else publish()


if __name__ == "__main__":
    raise SystemExit(main())
