#!/usr/bin/env python3
"""Fix the matched cohort and load it into BigQuery (analysis plan, section 3).

The cohort is every candidate spender (non-zero approvals from at least three
distinct owners in the observation window) that holds contract code. EOAs and
EIP-7702 delegated EOAs are left out. Writes data/2-.../cohort/matched_cohort
(parts) with the candidates' approval counts, and loads the addresses into
contract_rep.cohort as 20-byte BYTES (a load job, which BigQuery does not bill).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import PROC, RAW, REVISED, load_config, read_parts, save_json, write_parts  # noqa: E402

if REVISED:  # the revised cohort is built in BigQuery by sql/12_usd_ego.sql
    raise SystemExit("build_cohort.py belongs to the registered analysis; unset CONTRACT_REP_VARIANT")


def main() -> int:
    cfg = load_config()
    cand = read_parts(RAW / "cohort" / "spender_candidates")
    types = read_parts(RAW / "cohort" / "candidate_account_types")
    df = cand.merge(types, left_on="spender", right_on="address", how="left")
    missing = int(df["code_kind"].isna().sum())
    if missing:
        print(f"{missing} candidates have no account type yet; run check_account_code.py first")
        return 1
    cohort = df[df["code_kind"] == "contract"].drop(columns=["address"]).rename(columns={"spender": "wallet"})
    cohort = cohort.sort_values("wallet").reset_index(drop=True)
    out = PROC / "cohort"
    write_parts(cohort, out / "matched_cohort")
    save_json({
        "rule": f"contract spenders with non-zero approvals from >= {cfg['cohort']['min_owners']} distinct owners, "
                f"{cfg['period']['start_ts']} to {cfg['period']['observation_end']}",
        "candidates": int(len(df)),
        "by_code_kind": df["code_kind"].value_counts().to_dict(),
        "cohort": int(len(cohort)),
    }, out / "matched_cohort.json")

    csv = out / "_cohort_upload.csv"
    cohort[["wallet"]].to_csv(csv, index=False)
    project = cfg["bigquery"]["project_id"]
    ds = cfg["bigquery"]["dataset"]
    subprocess.run(["bq", "load", "--replace", "--source_format=CSV", "--skip_leading_rows=1",
                    f"{project}:{ds}.cohort_hex", str(csv), "wallet:STRING"], check=True, shell=True)
    sql = (f"CREATE OR REPLACE TABLE `{project}.{ds}.cohort` AS "
           f"SELECT FROM_HEX(SUBSTR(wallet, 3)) AS address FROM `{project}.{ds}.cohort_hex`")
    subprocess.run(["bq", "query", "--use_legacy_sql=false", sql], check=True, shell=True)
    csv.unlink()
    print(f"cohort: {len(cohort):,} contracts of {len(df):,} candidates")
    return 0


if __name__ == "__main__":
    sys.exit(main())
