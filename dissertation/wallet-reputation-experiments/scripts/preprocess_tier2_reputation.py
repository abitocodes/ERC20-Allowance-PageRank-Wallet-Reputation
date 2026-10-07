#!/usr/bin/env python3
"""Preprocess Tier-2 reputation raw parquet into tier2_paths processed files."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402
    load_config,
    load_json,
    load_raw_parquet_dir,
    normalize_address,
    parse_token_amount,
    save_json,
)


def _preprocess_allowances(raw_dir: Path, out_path: Path) -> dict:
    df = load_raw_parquet_dir(raw_dir, "approvals_arbitrum.parquet")
    for col in ("owner", "spender", "token_address"):
        if col in df.columns:
            df[col] = df[col].map(lambda x: normalize_address(str(x)) if pd.notna(x) else None)
    df["value"] = df["value"].map(parse_token_amount)
    df = df.sort_values(["block_number", "log_index"], ascending=True)
    latest = df.groupby(["token_address", "owner", "spender"], as_index=False).tail(1)
    latest = latest[latest["value"] > 0].copy()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    latest.to_parquet(out_path, index=False)
    return {"input_rows": len(df), "output_rows": len(latest), "output_path": str(out_path)}


def _preprocess_transfers(raw_dir: Path, out_path: Path) -> dict:
    df = load_raw_parquet_dir(raw_dir, "transfers_arbitrum.parquet")
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
    return {"input_rows": len(df), "output_rows": len(out), "output_path": str(out_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    config = load_config()
    tier2 = config.get("benchmark", {}).get("tier2_paths") or {}
    if not tier2:
        print("benchmark.tier2_paths missing in margin_config.yaml")
        return 1

    allowances_meta = _preprocess_allowances(
        Path(tier2["raw_approvals_dir"]),
        Path(tier2["latest_allowances"]),
    )
    transfers_meta = _preprocess_transfers(
        Path(tier2["raw_transfers_dir"]),
        Path(tier2["transfer_events"]),
    )

    manifest_path = Path(config["paths"]["manifest"])
    manifest = load_json(manifest_path)
    manifest["preprocess_tier2_reputation"] = {
        "at": datetime.now(timezone.utc).isoformat(),
        "allowances": allowances_meta,
        "transfers": transfers_meta,
    }
    save_json(manifest_path, manifest)
    print(f"Tier-2 allowances: {allowances_meta['output_rows']} rows")
    print(f"Tier-2 transfers: {transfers_meta['output_rows']} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
