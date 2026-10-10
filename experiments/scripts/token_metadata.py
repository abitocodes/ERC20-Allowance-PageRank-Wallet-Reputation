#!/usr/bin/env python3
"""Read symbol(), name() and decimals() of ERC-20 token contracts on an Arbitrum RPC.

All reads use one block, fetched once at the start and recorded in the output JSON,
so the metadata refer to one state of the chain. A string return is ABI-decoded; a
bytes32 return (older tokens) is read up to its first zero byte. A call that reverts
or returns nothing leaves the field empty.

Usage:
    python scripts/token_metadata.py INPUT.csv OUTPUT.csv [--column token_address] [--top N]
Writes OUTPUT.csv (address, symbol, name, decimals) and OUTPUT.json (block, time, counts).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_account_code import post  # noqa: E402
from common import load_config  # noqa: E402

SELECTORS = {"symbol": "0x95d89b41", "name": "0x06fdde03", "decimals": "0x313ce567"}
BATCH = 10  # tokens per JSON-RPC batch (three calls each)


def decode_string(hexdata: str | None) -> str | None:
    if not hexdata or hexdata in ("0x", "0x0"):
        return None
    raw = bytes.fromhex(hexdata[2:])
    try:
        if len(raw) >= 64:
            off = int.from_bytes(raw[:32], "big")
            if off + 32 <= len(raw):
                n = int.from_bytes(raw[off:off + 32], "big")
                if off + 32 + n <= len(raw) and n < 512:
                    return raw[off + 32:off + 32 + n].decode("utf-8", errors="replace").strip("\x00").strip()
        if len(raw) == 32:
            return raw.split(b"\x00", 1)[0].decode("utf-8", errors="replace").strip()
    except Exception:
        return None
    return None


def decode_uint(hexdata: str | None) -> int | None:
    if not hexdata or hexdata in ("0x", "0x0") or len(hexdata) < 3:
        return None
    try:
        v = int(hexdata[2:66], 16)
    except ValueError:
        return None
    return v if v < 256 else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--column", default="token_address")
    ap.add_argument("--top", type=int, default=0, help="first N rows of the input only")
    ap.add_argument("--rpc", help="RPC URL (default: accounts.rpc_url of the configuration)")
    args = ap.parse_args()

    cfg = load_config()
    url = args.rpc or cfg["accounts"]["rpc_url"]
    df = pd.read_csv(args.input)
    if args.top:
        df = df.head(args.top)
    addrs = df[args.column].astype(str).str.lower().drop_duplicates().tolist()
    session = requests.Session()
    bn = post(session, url, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []})["result"]
    meta = {"rpc": url, "block_number": int(bn, 16), "block_hex": bn,
            "read_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}

    rows = []
    reverted = 0
    for i in range(0, len(addrs), BATCH):
        batch = addrs[i:i + BATCH]
        todo = {}
        for j, a in enumerate(batch):
            for k, (field, sel) in enumerate(SELECTORS.items()):
                todo[j * 10 + k] = {"jsonrpc": "2.0", "id": j * 10 + k, "method": "eth_call",
                                    "params": [{"to": a, "data": sel}, bn]}
        # A reverted call is final and leaves the field empty; any other per-item error
        # (rate limits, timeouts) is retried with a growing pause.
        got: dict[int, str | None] = {}
        for attempt in range(12):
            if not todo:
                break
            try:
                resp = session.post(url, json=list(todo.values()), timeout=60).json()
            except (requests.RequestException, ValueError):
                resp = None
            if isinstance(resp, list):
                for item in resp:
                    err = item.get("error")
                    if err is None:
                        got[item["id"]] = item.get("result")
                        todo.pop(item["id"], None)
                    elif "revert" in str(err.get("message", "")).lower() or err.get("code") == 3:
                        got[item["id"]] = None
                        reverted += 1
                        todo.pop(item["id"], None)
            if todo:
                time.sleep(min(2 ** attempt, 30))
        if todo:
            raise RuntimeError(f"RPC {url} kept failing for {len(todo)} calls of batch {i // BATCH}")
        for j, a in enumerate(batch):
            rows.append({"address": a,
                         "symbol": decode_string(got.get(j * 10 + 0)),
                         "name": decode_string(got.get(j * 10 + 1)),
                         "decimals": decode_uint(got.get(j * 10 + 2))})
        if (i // BATCH) % 20 == 0:
            print(f"{len(rows):,}/{len(addrs):,}", flush=True)
    out = pd.DataFrame(rows)
    out.to_csv(args.output, index=False)
    meta["n"] = int(len(out))
    meta["with_decimals"] = int(out["decimals"].notna().sum())
    meta["reverted_calls"] = reverted
    Path(args.output).with_suffix(".json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(meta)
    return 0


if __name__ == "__main__":
    sys.exit(main())
