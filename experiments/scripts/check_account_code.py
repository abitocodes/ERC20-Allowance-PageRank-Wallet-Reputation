#!/usr/bin/env python3
"""Read the account type of addresses with eth_getCode on an Arbitrum RPC.

Bytecode means a contract. No bytecode, or an EIP-7702 delegation designator
(0xef0100 followed by a 20-byte address), means an externally owned account.
All reads use one block, fetched once at the start and recorded in the output,
so the classification refers to one state of the chain.

Usage:
    python scripts/check_account_code.py INPUT.csv OUTPUT_STEM [--column address]
Writes OUTPUT_STEM.parquet (split into parts below the configured size if needed)
and OUTPUT_STEM.json with the block number, the time of the read and the counts.
Addresses already classified in an existing OUTPUT_STEM.parquet are skipped.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load_config, read_parts, write_parts  # noqa: E402

BATCH = 25
WORKERS = 1


def code_kind(code: str | None, prefix: str) -> str:
    c = (code or "0x").lower()
    if c in ("0x", "0x0"):
        return "none"
    if c.startswith(prefix) and len(c) == 2 + 2 * 23:
        return "eip7702"
    return "contract"


def post(session: requests.Session, url: str, payload, retries: int = 15):
    last = ""
    for attempt in range(retries):
        try:
            resp = session.post(url, json=payload, timeout=60)
            if resp.status_code == 200:
                body = resp.json()
                if isinstance(body, list) and any("error" in item for item in body):
                    last = str([item["error"] for item in body if "error" in item][:1])
                else:
                    return body
            else:
                last = f"HTTP {resp.status_code}: {resp.text[:120]}"
        except (requests.RequestException, ValueError) as exc:
            last = repr(exc)
        time.sleep(min(2**attempt, 60))
    raise RuntimeError(f"RPC {url} kept failing: {last}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output_stem")
    ap.add_argument("--column", default="address")
    ap.add_argument("--rpc", help="RPC URL (default: accounts.rpc_url of the configuration)")
    args = ap.parse_args()

    cfg = load_config()
    url = args.rpc or cfg["accounts"]["rpc_url"]
    prefix = cfg["accounts"]["delegation_prefix"]
    stem = Path(args.output_stem)

    addrs = pd.read_csv(args.input)[args.column].astype(str).str.lower().drop_duplicates().tolist()
    done = read_parts(stem) if list(stem.parent.glob(stem.name + "*.parquet")) else pd.DataFrame()
    known = set(done["address"]) if not done.empty else set()
    todo = [a for a in addrs if a not in known]

    session = requests.Session()
    meta_path = stem.with_suffix(".json")
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    if "block_number" not in meta:
        bn = post(session, url, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []})["result"]
        meta = {"rpc": url, "block_number": int(bn, 16), "block_hex": bn,
                "read_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    block = meta["block_hex"]
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    def run(batch: list[str]) -> list[tuple[str, str]]:
        s = requests.Session()
        payload = [{"jsonrpc": "2.0", "id": i, "method": "eth_getCode", "params": [a, block]}
                   for i, a in enumerate(batch)]
        out = post(s, url, payload)
        return [(batch[item["id"]], code_kind(item.get("result"), prefix)) for item in out]

    def save(rows: list[tuple[str, str]]) -> pd.DataFrame:
        new = pd.DataFrame(rows, columns=["address", "code_kind"])
        allr = pd.concat([done[["address", "code_kind"]], new], ignore_index=True) if not done.empty else new
        allr["account_class"] = allr["code_kind"].map({"contract": "contract", "none": "eoa", "eip7702": "eoa_7702"})
        write_parts(allr.sort_values("address").reset_index(drop=True), stem)
        meta["counts"] = allr["code_kind"].value_counts().to_dict()
        meta["n"] = int(len(allr))
        meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
        return allr

    rows: list[tuple[str, str]] = []
    batches = [todo[i:i + BATCH] for i in range(0, len(todo), BATCH)]
    with ThreadPoolExecutor(WORKERS) as ex:
        for i, res in enumerate(ex.map(run, batches)):
            rows.extend(res)
            if (i + 1) % 200 == 0:
                save(rows)
                print(f"{len(rows):,}/{len(todo):,}", flush=True)
    save(rows)
    print(meta["counts"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
