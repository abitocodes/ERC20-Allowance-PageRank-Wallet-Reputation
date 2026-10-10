#!/usr/bin/env python3
"""Scan B: extract July-September 2026 only after the W1 registration is committed.

Refuses to run unless docs/registration_w1.md and config/contract_reputation.yaml
are committed without local changes and the configuration says
registered_window.status: registered. Records both files' SHA-256 hashes and the
commit in data/2-.../registered-w1/extraction_manifest.json, then runs:
  1. sql/01_materialize_logs.sql into contract_rep.logs_w1 (scan B),
  2. sql/03_ego_events.sql into approvals_w1ego / transfers_w1ego,
  3. sql/07_gmx_accounts.sql into gmx_accounts_w1.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import PROC, REVISED, ROOT, load_config, save_json  # noqa: E402

if REVISED:  # scan B ran once, for the registered analysis; the revised analysis reads its ego tables
    raise SystemExit("extract_w1.py belongs to the registered analysis; unset CONTRACT_REP_VARIANT")

FILES = [ROOT / "docs" / "registration_w1.md", ROOT / "config" / "contract_reputation.yaml"]


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()


def run(*args: str) -> None:
    subprocess.run([sys.executable, *args], cwd=ROOT, check=True)


def main() -> int:
    cfg = load_config()
    if cfg["registered_window"].get("status") != "registered":
        print("refused: registered_window.status is not 'registered'")
        return 2
    for f in FILES:
        rel = f.relative_to(ROOT)
        if git("status", "--porcelain", "--", str(rel)):
            print(f"refused: {rel} has uncommitted changes")
            return 2
        if not git("log", "-1", "--format=%H", "--", str(rel)):
            print(f"refused: {rel} is not committed")
            return 2
    manifest = {
        "started_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "head": git("rev-parse", "HEAD"),
        "registration_commit": git("log", "-1", "--format=%H %cI", "--", str(FILES[0].relative_to(ROOT))),
        "sha256": {str(f.relative_to(ROOT).as_posix()): hashlib.sha256(f.read_bytes()).hexdigest() for f in FILES},
        "override_used": False,
    }
    out = PROC / "registered-w1"
    save_json(manifest, out / "extraction_manifest.json")
    b = cfg["bigquery"]["scan_b"]
    run("scripts/run_bq.py", "sql/01_materialize_logs.sql", "--dest", "contract_rep.logs_w1",
        "--param", f"start_ts={b['start_ts']}", "--param", f"end_ts={b['end_ts']}", "--label", "scan B: W1 window")
    run("scripts/run_bq.py", "sql/03_ego_events.sql", "--sub", "SUFFIX=w1ego", "--sub", "SRC=logs_w1",
        "--param", f"start_ts={b['start_ts']}", "--param", f"end_ts={b['end_ts']}", "--label", "ego events, W1")
    run("scripts/run_bq.py", "sql/07_gmx_accounts.sql", "--dest", "contract_rep.gmx_accounts_w1",
        "--sub", "SRC=logs_w1", "--label", "gmx accounts, W1")
    manifest["finished_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    save_json(manifest, out / "extraction_manifest.json")
    print("scan B done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
