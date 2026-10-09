#!/usr/bin/env python3
"""Decode GMX V2 EventLog1 PositionDecrease logs into one row per close.

Reads the parts written by download_table.py (columns block_timestamp, block_number,
log_index, raw_topics, raw_data) and writes the decoded closes as parts too:
account, base PnL in USD (30-decimal integer as text), order type, liquidation
flag, size delta and side. A close is a liquidation when its order type is the
liquidation enum value or the liquidation handler emitted it.

Usage:
    python scripts/decode_gmx_events.py RAW_STEM DECODED_STEM
"""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import pandas as pd
from eth_abi.exceptions import DecodingError
from web3 import Web3
from web3._utils.events import get_event_data

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import DATA, load_config, read_parts, save_json, write_parts  # noqa: E402

ABI_PATH = DATA / "0-gmx-abi-for-decoding-logs" / "EventEmitter.json"
_EVENT_ABI = None


def _event_abi() -> dict:
    global _EVENT_ABI
    if _EVENT_ABI is None:
        abi = json.loads(ABI_PATH.read_text(encoding="utf-8"))["abi"]
        _EVENT_ABI = next(e for e in abi if e.get("name") == "EventLog1" and e.get("type") == "event")
    return _EVENT_ABI


def _hex(val) -> bytes:
    s = str(val or "").strip()
    s = s[2:] if s.startswith("0x") else s
    return bytes.fromhex(s) if s else b""


def _item(items: list[dict], key: str):
    for it in items:
        if it.get("key") == key:
            return it.get("value")
    return None


def _norm(addr) -> str | None:
    return str(addr).lower() if addr else None


def decode_chunk(rows: list[dict], liq_handler: str, liq_type: int) -> tuple[list[dict], int]:
    codec = Web3().codec
    out, errors = [], 0
    for r in rows:
        topics = list(r["raw_topics"])
        entry = {
            "address": "0xc8ee91a54287db53897056e12d9819156d3822fb",
            "data": _hex(r["raw_data"]),
            "topics": [_hex(t) for t in topics],
            "logIndex": int(r["log_index"]),
            "transactionIndex": 0,
            "transactionHash": b"\x00" * 32,
            "blockHash": b"\x00" * 32,
            "blockNumber": int(r["block_number"]),
        }
        try:
            ev = get_event_data(codec, _event_abi(), entry)
        except (DecodingError, ValueError, TypeError):
            errors += 1
            continue
        args = ev["args"]
        if args.get("eventName") != "PositionDecrease":
            errors += 1
            continue
        data = args["eventData"]
        account = _item(data["addressItems"]["items"], "account")
        pnl = _item(data["intItems"]["items"], "basePnlUsd")
        if pnl is None:
            errors += 1
            continue
        otype = _item(data["uintItems"]["items"], "orderType")
        size = _item(data["uintItems"]["items"], "sizeDeltaUsd")
        is_long = _item(data["boolItems"]["items"], "isLong")
        sender = _norm(args.get("msgSender"))
        otype = int(otype) if otype is not None else None
        out.append({
            "block_timestamp": r["block_timestamp"],
            "block_number": int(r["block_number"]),
            "log_index": int(r["log_index"]),
            "account": _norm(account) or "0x" + topics[2][-40:].lower(),
            "msg_sender": sender,
            "base_pnl_usd": str(int(pnl)),
            "order_type": otype,
            "is_liquidation": otype == liq_type or sender == liq_handler.lower(),
            "size_delta_usd": str(int(size)) if size is not None else None,
            "is_long": bool(is_long) if is_long is not None else None,
        })
    return out, errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("raw_stem")
    ap.add_argument("decoded_stem")
    args = ap.parse_args()
    gmx = load_config()["gmx_arbitrum"]
    rows = read_parts(Path(args.raw_stem)).to_dict(orient="records")
    chunks = [rows[i:i + 20000] for i in range(0, len(rows), 20000)]
    decoded, errors = [], 0
    with ProcessPoolExecutor(max_workers=12) as ex:
        futs = [ex.submit(decode_chunk, c, gmx["liquidation_handler"], int(gmx["order_type_liquidation"]))
                for c in chunks]
        for f in futs:
            part, err = f.result()
            decoded.extend(part)
            errors += err
    df = pd.DataFrame(decoded).sort_values(["block_number", "log_index"]).reset_index(drop=True)
    stem = Path(args.decoded_stem)
    write_parts(df, stem)
    save_json({"input_rows": len(rows), "decoded_rows": len(df), "errors": errors,
               "liquidations": int(df["is_liquidation"].sum()) if len(df) else 0},
              stem.parent / f"{stem.name}.json")
    print(f"decoded {len(df):,} of {len(rows):,} (errors {errors})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
