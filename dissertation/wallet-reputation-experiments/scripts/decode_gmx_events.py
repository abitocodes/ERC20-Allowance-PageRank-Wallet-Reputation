#!/usr/bin/env python3
"""Decode GMX EventLog1 PositionDecrease logs into structured events."""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from eth_abi.exceptions import DecodingError
from web3 import Web3
from web3._utils.events import get_event_data

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402
    load_config,
    load_json,
    normalize_address,
    parse_topic_address,
    save_json,
)
from project_paths import ABI_DIR  # noqa: E402

ABI_PATH = ABI_DIR / "EventEmitter.json"
_EVENT_ABI = None


def _get_event_abi() -> dict:
    global _EVENT_ABI
    if _EVENT_ABI is None:
        with ABI_PATH.open(encoding="utf-8") as f:
            abi = json.load(f)["abi"]
        _EVENT_ABI = next(e for e in abi if e.get("name") == "EventLog1" and e.get("type") == "event")
    return _EVENT_ABI


def _hex_to_bytes(val: str | bytes | None) -> bytes:
    if val is None:
        return b""
    if isinstance(val, bytes):
        return val
    s = str(val).strip()
    if s.startswith("0x"):
        s = s[2:]
    if not s:
        return b""
    return bytes.fromhex(s)


def _get_item(items: list[dict], key: str):
    for item in items:
        if item.get("key") == key:
            return item.get("value")
    return None


def _extract_fields(event_data: dict) -> dict[str, object]:
    return {
        "account": _get_item(event_data.get("addressItems", {}).get("items", []), "account"),
        "basePnlUsd": _get_item(event_data.get("intItems", {}).get("items", []), "basePnlUsd"),
        "orderType": _get_item(event_data.get("uintItems", {}).get("items", []), "orderType"),
        "sizeDeltaUsd": _get_item(event_data.get("uintItems", {}).get("items", []), "sizeDeltaUsd"),
        "isLong": _get_item(event_data.get("boolItems", {}).get("items", []), "isLong"),
    }


def decode_log_row(
    row: pd.Series,
    liquidation_handler: str,
    liq_order_type: int,
    codec,
) -> dict | None:
    raw_topics = row.get("topics")
    if raw_topics is None:
        return None
    topics = list(raw_topics) if hasattr(raw_topics, "__iter__") and not isinstance(raw_topics, str) else []
    if len(topics) < 3:
        return None

    account_topic = parse_topic_address(topics[2])
    data = _hex_to_bytes(row.get("data"))
    if not data:
        return None

    log_entry = {
        "address": row.get("address", ""),
        "data": data,
        "topics": [_hex_to_bytes(t) for t in topics],
        "logIndex": int(row.get("log_index", 0)),
        "transactionIndex": 0,
        "transactionHash": _hex_to_bytes(row.get("transaction_hash")),
        "blockHash": b"\x00" * 32,
        "blockNumber": int(row.get("block_number", 0)),
    }

    try:
        decoded = get_event_data(codec, _get_event_abi(), log_entry)
    except (DecodingError, ValueError, TypeError):
        return None

    args = decoded.get("args", {})
    if args.get("eventName") != "PositionDecrease":
        return None

    fields = _extract_fields(args["eventData"])
    account = normalize_address(fields.get("account")) or account_topic
    base_pnl = fields.get("basePnlUsd")
    if base_pnl is None:
        return None

    order_type = fields.get("orderType")
    order_type_int = int(order_type) if order_type is not None else None
    msg_sender_norm = normalize_address(args.get("msgSender"))
    is_liquidation = (
        order_type_int == liq_order_type
        or msg_sender_norm == normalize_address(liquidation_handler)
    )

    return {
        "block_timestamp": row.get("block_timestamp"),
        "block_number": int(row.get("block_number", 0)),
        "transaction_hash": row.get("transaction_hash"),
        "log_index": int(row.get("log_index", 0)),
        "account": account,
        "msg_sender": msg_sender_norm,
        "base_pnl_usd": str(int(base_pnl)),
        "order_type": order_type_int,
        "is_liquidation": is_liquidation,
        "size_delta_usd": (
            str(int(fields["sizeDeltaUsd"])) if fields.get("sizeDeltaUsd") is not None else None
        ),
        "is_long": bool(fields["isLong"]) if fields.get("isLong") is not None else None,
    }


def _decode_records(rows: list[dict], liquidation_handler: str, liq_order_type: int) -> tuple[list[dict], int]:
    codec = Web3().codec
    decoded: list[dict] = []
    errors = 0
    for row_dict in rows:
        rec = decode_log_row(
            pd.Series(row_dict),
            liquidation_handler,
            liq_order_type,
            codec,
        )
        if rec:
            decoded.append(rec)
        else:
            errors += 1
    return decoded, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="Raw logs parquet")
    parser.add_argument("--output", type=Path, help="Decoded events parquet")
    args = parser.parse_args()

    config = load_config()
    in_path = args.input or Path(config["paths"]["raw_logs"])
    out_path = args.output or Path(config["paths"]["decoded_events"])
    gmx = config["gmx_arbitrum"]

    if not in_path.exists():
        print(f"Missing input: {in_path}")
        print("Run extract_margin_week.py or generate_synthetic_rankings.py first.")
        return 1

    df = pd.read_parquet(in_path)
    row_dicts = df.to_dict(orient="records")
    total = len(row_dicts)
    chunk_size = 10000
    chunks = [row_dicts[i : i + chunk_size] for i in range(0, total, chunk_size)]
    decoded: list[dict] = []
    errors = 0
    workers = min(8, max(1, len(chunks)))
    print(f"Decoding {total} logs in {len(chunks)} chunks ({workers} workers)...")
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(
                _decode_records,
                chunk,
                gmx["liquidation_handler"],
                gmx["order_type_liquidation"],
            ): idx
            for idx, chunk in enumerate(chunks)
        }
        done = 0
        for fut in as_completed(futures):
            part, err = fut.result()
            decoded.extend(part)
            errors += err
            done += 1
            if done % 5 == 0 or done == len(chunks):
                print(f"  chunks {done}/{len(chunks)} ({len(decoded)} decoded)")

    out_df = pd.DataFrame(decoded)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_parquet(out_path, index=False)

    manifest_path = Path(config["paths"]["manifest"])
    manifest = load_json(manifest_path)
    manifest["decode"] = {
        "at": datetime.now(timezone.utc).isoformat(),
        "input_rows": len(df),
        "decoded_rows": len(out_df),
        "decode_errors": errors,
        "output": str(out_path),
    }
    manifest["synthetic"] = False
    save_json(manifest_path, manifest)
    print(f"Decoded {len(out_df)} events ({errors} skipped) -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
