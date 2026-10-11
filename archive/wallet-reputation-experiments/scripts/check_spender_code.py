#!/usr/bin/env python3
"""Check which spring spenders hold contract code, with eth_getCode on an Arbitrum RPC.

classify_spenders.py reads BigQuery activity in the scoring window: an address
that emitted a log is a contract and one that sent a transaction is an EOA.
Many routers do neither themselves (their events come from other contracts and
they never originate transactions), so that check leaves part of the cohort
undetermined. eth_getCode settles it: bytecode means a contract, no bytecode an
EOA, and code that starts with 0xef0100 an EOA delegating to contract code
(EIP-7702).

The state read is that of the latest block, not the freeze date. The script
needs no credentials; the public Arbitrum RPC is the default.

Usage:
    python scripts/check_spender_code.py
    python scripts/check_spender_code.py --rpc <url>     # or set ARBITRUM_RPC_URL
Reads spender_account_types.csv (from classify_spenders.py) in
data/2-processed-tables-and-evaluations/spring-holdout-2026-03-to-2026-05/,
adds the columns code_kind and account_class, and adds a code_check block to
spender_account_types.json.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import load_json, save_json  # noqa: E402
from project_paths import SPRING_HOLDOUT_DIR  # noqa: E402

OUT_DIR = SPRING_HOLDOUT_DIR
DEFAULT_RPC = "https://arb1.arbitrum.io/rpc"
BATCH = 25
TOP_N = 100
# EIP-7702 delegation designator: 0xef0100 followed by a 20-byte address.
DELEGATION_PREFIX = "0xef0100"
DELEGATION_LENGTH = 2 + 2 * 23

CLASS_OF_KIND = {"contract": "contract", "none": "eoa", "eip7702": "eoa_7702"}


def code_kind(code: str | None) -> str:
    c = (code or "0x").lower()
    if c in ("0x", "0x0"):
        return "none"
    if c.startswith(DELEGATION_PREFIX) and len(c) == DELEGATION_LENGTH:
        return "eip7702"
    return "contract"


def _post(session: requests.Session, url: str, payload, retries: int = 6):
    for attempt in range(retries):
        try:
            resp = session.post(url, json=payload, timeout=30)
        except requests.RequestException:
            time.sleep(2**attempt)
            continue
        if resp.status_code == 429 or resp.status_code >= 500:
            time.sleep(2**attempt)
            continue
        resp.raise_for_status()
        return resp.json()
    raise RuntimeError(f"RPC {url} kept failing after {retries} attempts")


def _single(session: requests.Session, url: str, method: str, params: list):
    data = _post(session, url, {"jsonrpc": "2.0", "id": 1, "method": method, "params": params})
    if "error" in data:
        raise RuntimeError(f"{method} failed: {data['error']}")
    return data["result"]


def fetch_codes(session: requests.Session, url: str, addresses: list[str], block: str) -> dict[str, str]:
    """eth_getCode for every address, in JSON-RPC batches, one call at a time if a batch fails."""
    codes: dict[str, str] = {}
    for start in range(0, len(addresses), BATCH):
        chunk = addresses[start : start + BATCH]
        payload = [
            {"jsonrpc": "2.0", "id": i, "method": "eth_getCode", "params": [addr, block]}
            for i, addr in enumerate(chunk)
        ]
        data = _post(session, url, payload)
        results = {}
        if isinstance(data, list):
            results = {d.get("id"): d.get("result") for d in data if "error" not in d}
        for i, addr in enumerate(chunk):
            code = results.get(i)
            if code is None:
                code = _single(session, url, "eth_getCode", [addr, block])
            codes[addr] = code
        done = min(start + BATCH, len(addresses))
        if done % 250 < BATCH or done == len(addresses):
            print(f"  {done}/{len(addresses)}", flush=True)
    return codes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--rpc", default=os.environ.get("ARBITRUM_RPC_URL", DEFAULT_RPC))
    args = parser.parse_args()

    csv_path = OUT_DIR / "spender_account_types.csv"
    json_path = OUT_DIR / "spender_account_types.json"
    if not csv_path.exists():
        print(f"Missing {csv_path}; run classify_spenders.py --run first.")
        return 1
    types = pd.read_csv(csv_path)
    types["wallet"] = types["wallet"].astype(str).str.lower()

    session = requests.Session()
    block = int(_single(session, args.rpc, "eth_blockNumber", []), 16)
    block_tag = hex(block)
    print(f"eth_getCode for {len(types)} spenders at block {block}...")
    codes = fetch_codes(session, args.rpc, types["wallet"].tolist(), block_tag)
    types["code_kind"] = types["wallet"].map(lambda w: code_kind(codes.get(w)))
    types["account_class"] = types["code_kind"].map(CLASS_OF_KIND)
    types.to_csv(csv_path, index=False)

    def counts(frame: pd.DataFrame) -> dict[str, int]:
        return {k: int(v) for k, v in frame["account_class"].value_counts().items()}

    summary = load_json(json_path)
    top = types.sort_values("endorserank_t1", ascending=False).head(TOP_N)
    summary["code_check"] = {
        "at": datetime.now(timezone.utc).isoformat(),
        "rpc_host": urlparse(args.rpc).netloc,
        "block": block,
        "counts": counts(types),
        f"counts_top{TOP_N}_endorserank": counts(top),
        "counts_with_new_approver": counts(types[types["future_new_approvers"] > 0]),
        "by_bigquery_activity": {
            activity: counts(group) for activity, group in types.groupby("account_type")
        },
    }
    save_json(json_path, summary)
    print(json.dumps(summary["code_check"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
