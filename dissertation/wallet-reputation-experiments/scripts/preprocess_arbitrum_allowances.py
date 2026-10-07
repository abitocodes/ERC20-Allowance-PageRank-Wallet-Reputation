#!/usr/bin/env python3
"""Build latest allowance state per (token, owner, spender) from Arbitrum approvals."""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import load_config, load_json, load_raw_parquet_dir, normalize_address, parse_token_amount, save_json  # noqa: E402


def load_approval_frames(raw_dir: Path) -> pd.DataFrame:
    return load_raw_parquet_dir(raw_dir, "approvals_arbitrum.parquet")


def main() -> int:
    config = load_config()
    rep = config["reputation"]
    raw_dir = Path(rep["paths"]["raw_approvals_dir"])
    out_path = Path(rep["paths"]["latest_allowances"])

    df = load_approval_frames(raw_dir)
    for col in ("owner", "spender", "token_address"):
        if col in df.columns:
            df[col] = df[col].map(lambda x: normalize_address(str(x)) if pd.notna(x) else None)

    df["value"] = df["value"].map(parse_token_amount)
    df = df.sort_values(["block_number", "log_index"], ascending=True)

    latest = df.groupby(["token_address", "owner", "spender"], as_index=False).tail(1)
    latest = latest[latest["value"] > 0].copy()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    latest.to_parquet(out_path, index=False)

    manifest_path = Path(config["paths"]["manifest"])
    manifest = load_json(manifest_path)
    manifest["preprocess_arbitrum_allowances"] = {
        "at": datetime.now(timezone.utc).isoformat(),
        "input_rows": len(df),
        "output_rows": len(latest),
        "output_path": str(out_path),
    }
    save_json(manifest_path, manifest)
    print(f"latest_allowances: {len(latest)} rows -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
