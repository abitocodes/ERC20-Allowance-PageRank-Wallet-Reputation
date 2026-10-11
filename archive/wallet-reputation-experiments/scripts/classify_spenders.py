#!/usr/bin/env python3
"""Classify the spring spender cohort as contracts or externally owned accounts (EOAs).

The dissertation describes the spenders that EndorseRank ranks as routers and
vaults. This script checks the claim on BigQuery for the spenders that held a
positive allowance at the spring freeze:

  contract   emitted at least one log in the window (only code emits logs)
  eoa        sent at least one transaction in the window (only EOAs sign)
  both       did both; an EOA running delegated code (EIP-7702)
  inactive   did neither in the window, so the query cannot tell; routers whose
             events come from other contracts and that never send transactions
             land here, so run check_spender_code.py (eth_getCode) afterwards

Only logs.address, transactions.from_address and their block_timestamp
partitions are read. Run --dry-run first to see the bytes that would be billed.

Credentials: application default credentials, or a service-account key given
as JSON text in GCP_SA_KEY_JSON. The billing project comes from
GOOGLE_CLOUD_PROJECT, the config (bigquery.project_id) or the key.

Usage:
    python scripts/classify_spenders.py --dry-run
    python scripts/classify_spenders.py --run
Output: spender_account_types.csv and spender_account_types.json in
data/2-processed-tables-and-evaluations/spring-holdout-2026-03-to-2026-05/
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import format_bytes, load_config, read_sql, save_json  # noqa: E402
from project_paths import SPRING_HOLDOUT_DIR  # noqa: E402
from holdout import (  # noqa: E402
    future_approval_labels,
    holdout_bounds,
    latest_positive_as_of,
    load_approval_events,
    score_endorserank,
)

OUT_DIR = SPRING_HOLDOUT_DIR
TOP_N = 100


def _client(config: dict[str, Any]):
    from google.cloud import bigquery

    project = os.environ.get("GOOGLE_CLOUD_PROJECT") or config.get("bigquery", {}).get("project_id")
    key_json = os.environ.get("GCP_SA_KEY_JSON")
    if key_json:
        from google.oauth2 import service_account

        info = json.loads(key_json)
        creds = service_account.Credentials.from_service_account_info(
            info, scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        return bigquery.Client(project=project or info.get("project_id"), credentials=creds)
    return bigquery.Client(project=project)


def _address_variants(addresses: list[str]) -> list[str]:
    """Lower-case and EIP-55 forms, so the SQL filter matches either storage style."""
    from eth_utils import to_checksum_address

    out: set[str] = set()
    for addr in addresses:
        out.add(addr.lower())
        out.add(to_checksum_address(addr))
    return sorted(out)


def classify(activity: pd.DataFrame, spenders: list[str]) -> pd.DataFrame:
    emitted = set(activity.loc[activity["activity"] == "emitted_log", "address"])
    sent = set(activity.loc[activity["activity"] == "sent_transaction", "address"])
    kinds = []
    for addr in spenders:
        if addr in emitted and addr in sent:
            kinds.append("both")
        elif addr in emitted:
            kinds.append("contract")
        elif addr in sent:
            kinds.append("eoa")
        else:
            kinds.append("inactive")
    return pd.DataFrame({"wallet": spenders, "account_type": kinds})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", help="estimate bytes only")
    parser.add_argument("--run", action="store_true", help="run the query")
    parser.add_argument("--start", default=None, help="window start (default: observation start)")
    parser.add_argument("--end", default=None, help="window end, exclusive (default: day after the freeze)")
    args = parser.parse_args()
    if not (args.dry_run or args.run):
        parser.error("Specify --dry-run or --run")

    config = load_config()
    score_end, outcome_start, outcome_end = holdout_bounds(config)
    start = args.start or config["reputation"]["observation_start_ts"]
    end = args.end or str(outcome_start)

    approvals = load_approval_events(config)
    latest_t1 = latest_positive_as_of(approvals, score_end)
    spenders = sorted(set(latest_t1["spender"].astype(str).str.lower()))
    print(f"{len(spenders)} spenders with a positive allowance at {score_end}")

    from google.cloud.bigquery import ArrayQueryParameter, QueryJobConfig, ScalarQueryParameter

    sql = (
        read_sql("arbitrum_account_activity.sql")
        .replace("__LOGS_FQN__", config["bigquery"]["logs_fqn"])
        .replace("__TX_FQN__", config["bigquery"]["transactions_fqn"])
    )
    params = [
        ScalarQueryParameter("start_ts", "STRING", str(start)),
        ScalarQueryParameter("end_ts", "STRING", str(end)),
        ArrayQueryParameter("addresses", "STRING", _address_variants(spenders)),
    ]
    client = _client(config)
    dry = client.query(sql, job_config=QueryJobConfig(dry_run=True, use_query_cache=False, query_parameters=params))
    billed = int(dry.total_bytes_processed or 0)
    budget = int(config.get("budget", {}).get("max_bytes_per_query", 0))
    print(f"Dry run: {format_bytes(billed)} for {start} to {end}")
    if args.dry_run and not args.run:
        return 0
    if budget and billed > budget:
        print(f"Above the per-query budget ({format_bytes(budget)}); narrow the window with --start/--end.")
        return 1

    activity = client.query(sql, job_config=QueryJobConfig(query_parameters=params)).to_dataframe()
    activity["address"] = activity["address"].astype(str).str.lower()
    types = classify(activity, spenders)

    er = score_endorserank(latest_t1, spenders, config)
    types["endorserank_t1"] = types["wallet"].map(lambda w: er.get(w, 0.0))
    types["endorserank_t1_top"] = types["endorserank_t1"].rank(method="first", ascending=False) <= TOP_N
    labels = future_approval_labels(approvals, latest_t1, outcome_start, outcome_end, spenders)
    types = types.merge(labels[["wallet", "future_new_approvers"]], on="wallet", how="left")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    types.to_csv(OUT_DIR / "spender_account_types.csv", index=False)
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "window": [str(start), str(end)],
        "bytes_processed": billed,
        "n_spenders": len(types),
        "counts": types["account_type"].value_counts().to_dict(),
        f"counts_top{TOP_N}_endorserank": types.loc[types["endorserank_t1_top"], "account_type"].value_counts().to_dict(),
        "counts_with_new_approver": types.loc[types["future_new_approvers"] > 0, "account_type"].value_counts().to_dict(),
    }
    save_json(OUT_DIR / "spender_account_types.json", summary)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
