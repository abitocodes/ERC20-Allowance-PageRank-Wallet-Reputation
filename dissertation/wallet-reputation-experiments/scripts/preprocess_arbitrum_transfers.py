#!/usr/bin/env python3
"""Normalize Arbitrum transfer logs for AWP (preserve timestamps)."""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import load_config, load_json, load_raw_parquet_dir, normalize_address, parse_token_amount, save_json  # noqa: E402


def load_transfer_frames(raw_dir: Path) -> pd.DataFrame:
    return load_raw_parquet_dir(raw_dir, "transfers_arbitrum.parquet")


def main() -> int:
    config = load_config()
    rep = config["reputation"]
    raw_dir = Path(rep["paths"]["raw_transfers_dir"])
    out_path = Path(rep["paths"]["transfer_events"])

    df = load_transfer_frames(raw_dir)
    for col in ("from_address", "to_address", "token_address"):
        if col in df.columns:
            df[col] = df[col].map(lambda x: normalize_address(str(x)) if pd.notna(x) else None)

    df["value"] = df["value"].map(parse_token_amount)
    df = df[df["value"] > 0].copy()
    df["block_timestamp"] = pd.to_datetime(df["block_timestamp"], utc=True)

    cols = [
        "block_timestamp",
        "block_number",
        "transaction_hash",
        "log_index",
        "token_address",
        "from_address",
        "to_address",
        "value",
    ]
    out = df[[c for c in cols if c in df.columns]].copy()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(out_path, index=False)

    manifest_path = Path(config["paths"]["manifest"])
    manifest = load_json(manifest_path)
    manifest["preprocess_arbitrum_transfers"] = {
        "at": datetime.now(timezone.utc).isoformat(),
        "input_rows": len(df),
        "output_rows": len(out),
        "output_path": str(out_path),
    }
    save_json(manifest_path, manifest)
    print(f"transfer_events: {len(out)} rows -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
