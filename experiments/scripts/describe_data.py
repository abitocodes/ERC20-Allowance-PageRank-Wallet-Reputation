#!/usr/bin/env python3
"""Descriptive statistics of the extracted data for Chapters 3, 4 and Appendix 8.4.

Reads the two BigQuery tables written by sql/10_describe.sql (monthly event counts and
amount shares) and the decoded GMX closes, and writes data/2-.../describe/describe.json:
monthly counts per stream, the share of transfers and latest allowances of at least
10 base units, unlimited allowances and the owners that hold them, GMX V2 closes and
accounts of contract traders per quarter, and the timing of the plan, scan A, the
registration and scan B.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import PROC, ROOT, load_config, save_json  # noqa: E402
from labels import load_closes  # noqa: E402


def bq_json(sql: str) -> list[dict]:
    out = subprocess.run(["bq", "query", "--use_legacy_sql=false", "--format=json", "--max_rows=100000", sql],
                         capture_output=True, text=True, check=True, shell=True).stdout
    return json.loads(out[out.index("["):])


def job_times(job_id: str) -> dict:
    out = subprocess.run(["bq", "show", "--format=json", "-j", f"dissertation-bq:US.{job_id}"],
                         capture_output=True, text=True, check=True, shell=True).stdout
    st = json.loads(out)["statistics"]
    conv = lambda ms: datetime.fromtimestamp(int(ms) / 1000, timezone.utc).isoformat(timespec="seconds")
    return {"created": conv(st["creationTime"]), "ended": conv(st["endTime"])}


def main() -> int:
    cfg = load_config()
    ds = f"{cfg['bigquery']['project_id']}.{cfg['bigquery']['dataset']}"
    monthly = pd.DataFrame(bq_json(f"SELECT * FROM `{ds}.describe_monthly` ORDER BY stream, month"))
    monthly["n"] = monthly["n"].astype(int)
    values = {r["what"]: {k: (int(v) if v not in (None, "") else None) for k, v in r.items() if k != "what"}
              for r in bq_json(f"SELECT * FROM `{ds}.describe_values`")}
    t = values["transfers_ego"]
    a = values["latest_allowances_tobs"]
    shares = {
        "transfers_ego": t["n"], "transfers_ge10_share": t["ge10"] / t["n"],
        "latest_allowances_tobs": a["n"], "allowances_ge10_share": a["ge10"] / a["n"],
        "unlimited_allowances": a["ge1e30"], "unlimited_share": a["ge1e30"] / a["n"],
        "owners": a["owners"], "owners_with_unlimited": a["owners_unlimited"],
        "owners_with_both_kinds": values["owners_both_kinds_tobs"]["owners_both"],
    }
    closes = load_closes(("obs", "w1"))
    q = closes.assign(quarter=closes["block_timestamp"].dt.tz_convert(None).dt.to_period("Q").astype(str))
    gmx = q.groupby("quarter").agg(closes=("account", "size"), accounts=("account", "nunique"),
                                   liquidations=("is_liquidation", "sum")).reset_index()
    ledger = json.loads((ROOT / "data" / "bq_ledger.json").read_text(encoding="utf-8"))
    scan_a = next(j for j in ledger["jobs"] if j["label"].startswith("scan A"))
    scan_b = next(j for j in ledger["jobs"] if j["label"].startswith("scan B"))
    timing = {
        "plan_commit_43d8045_utc": "2026-10-09T13:41:27+00:00",
        "scan_a": job_times(scan_a["job_id"]),
        "registration_commit_0d3a057_utc": "2026-10-09T16:49:32+00:00",
        "scan_b": job_times(scan_b["job_id"]),
        "bigquery_usd_total": round(sum(j["usd"] for j in ledger["jobs"]), 2),
        "bigquery_tib_billed": round(sum(j["bytes_billed"] for j in ledger["jobs"]) / 2**40, 3),
    }
    save_json({"monthly_counts": monthly.to_dict(orient="records"), "amounts": shares,
               "gmx_contract_traders_by_quarter": gmx.to_dict(orient="records"), "timing": timing},
              PROC / "describe" / "describe.json")
    print(shares, timing)
    return 0


if __name__ == "__main__":
    sys.exit(main())
