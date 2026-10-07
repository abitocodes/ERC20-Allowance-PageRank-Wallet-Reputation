#!/usr/bin/env python3
"""Aggregate decoded PositionDecrease events into wallet success-rate rankings."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import load_config, load_json, normalize_address, save_json  # noqa: E402


def compute_rankings(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    period = config["period"]
    ranking_cfg = config["ranking"]
    min_closes = int(ranking_cfg["min_closes"])

    if df.empty:
        return pd.DataFrame(
            columns=[
                "rank",
                "wallet",
                "success_rate",
                "total_closes",
                "wins",
                "losses",
                "period_start",
                "period_end",
                "protocol",
            ]
        )

    work = df.copy()
    work["wallet"] = work["account"].map(normalize_address)
    work = work.dropna(subset=["wallet"])

    def is_win(row: pd.Series) -> bool:
        if row.get("is_liquidation"):
            return False
        return int(str(row["base_pnl_usd"])) > 0

    work["win"] = work.apply(is_win, axis=1)

    agg = (
        work.groupby("wallet", as_index=False)
        .agg(
            total_closes=("win", "count"),
            wins=("win", "sum"),
        )
    )
    agg["losses"] = agg["total_closes"] - agg["wins"]
    agg = agg[agg["total_closes"] >= min_closes].copy()
    agg["success_rate"] = agg["wins"] / agg["total_closes"]
    agg = agg.sort_values(
        ["success_rate", "total_closes"],
        ascending=[False, False],
    ).reset_index(drop=True)
    agg["rank"] = range(1, len(agg) + 1)
    agg["period_start"] = period["start_date"]
    agg["period_end"] = "2026-05-31"
    agg["protocol"] = config["protocol"]

    return agg[
        [
            "rank",
            "wallet",
            "success_rate",
            "total_closes",
            "wins",
            "losses",
            "period_start",
            "period_end",
            "protocol",
        ]
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="Decoded events parquet")
    parser.add_argument("--output", type=Path, help="Wallet rankings parquet")
    args = parser.parse_args()

    config = load_config()
    in_path = args.input or Path(config["paths"]["decoded_events"])
    out_path = args.output or Path(config["paths"]["wallet_rankings"])

    if not in_path.exists():
        print(f"Missing input: {in_path}")
        return 1

    df = pd.read_parquet(in_path)
    rankings = compute_rankings(df, config)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    rankings.to_parquet(out_path, index=False)

    manifest_path = Path(config["paths"]["manifest"])
    manifest = load_json(manifest_path)
    manifest["rankings"] = {
        "at": datetime.now(timezone.utc).isoformat(),
        "wallets_ranked": len(rankings),
        "min_closes": config["ranking"]["min_closes"],
        "output": str(out_path),
    }
    save_json(manifest_path, manifest)
    print(f"Ranked {len(rankings)} wallets -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
