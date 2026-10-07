#!/usr/bin/env python3
"""Generate synthetic GMX-like data for offline pipeline validation."""

from __future__ import annotations

import argparse
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import load_config, save_json  # noqa: E402
from compute_rankings import compute_rankings  # noqa: E402


def generate_decoded_events(n_wallets: int, seed: int, config: dict) -> pd.DataFrame:
    random.seed(seed)
    gmx = config["gmx_arbitrum"]
    liq_handler = gmx["liquidation_handler"]
    liq_type = gmx["order_type_liquidation"]
    base_ts = datetime(2026, 5, 25, 12, 0, 0, tzinfo=timezone.utc)

    wallets = [f"0x{'%040x' % i}" for i in range(1, n_wallets + 1)]
    decoded_rows: list[dict] = []

    for wi, wallet in enumerate(wallets):
        n_closes = random.randint(3, 12)
        # Skew: some high performers for GMX proxy spread
        win_rate = min(0.95, max(0.15, random.betavariate(2 + wi % 5, 2 + (wi * 3) % 7)))
        for ci in range(n_closes):
            is_liq = random.random() < 0.04
            if is_liq:
                pnl = -random.randint(100, 5000)
                order_type = liq_type
                msg_sender = liq_handler
            else:
                win = random.random() < win_rate
                pnl = random.randint(50, 8000) if win else -random.randint(50, 4000)
                order_type = 4
                msg_sender = gmx["exchange_router"]

            decoded_rows.append(
                {
                    "block_timestamp": base_ts,
                    "block_number": 300_000_000 + wi * 20 + ci,
                    "transaction_hash": f"0x{'%064x' % (wi * 1000 + ci)}",
                    "log_index": ci,
                    "account": wallet,
                    "msg_sender": msg_sender.lower(),
                    "base_pnl_usd": pnl,
                    "order_type": order_type,
                    "is_liquidation": is_liq,
                    "size_delta_usd": 500_000_000_000,
                    "is_long": bool(ci % 2),
                }
            )

    return pd.DataFrame(decoded_rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-wallets", type=int, default=571, help="Synthetic wallet count")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    config = load_config()
    decoded_df = generate_decoded_events(args.n_wallets, args.seed, config)

    raw_path = Path(config["paths"]["raw_logs"])
    decoded_path = Path(config["paths"]["decoded_events"])
    rankings_path = Path(config["paths"]["wallet_rankings"])
    manifest_path = Path(config["paths"]["manifest"])

    raw_path.parent.mkdir(parents=True, exist_ok=True)
    decoded_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"note": ["synthetic — replace via BigQuery extract_margin_week.py"]}).to_parquet(
        raw_path, index=False
    )

    decoded_df.to_parquet(decoded_path, index=False)
    rankings = compute_rankings(decoded_df, config)
    rankings.to_parquet(rankings_path, index=False)

    save_json(
        manifest_path,
        {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "synthetic": True,
            "period": config["period"],
            "protocol": config["protocol"],
            "note": "Offline synthetic data; re-run extract_margin_week.py for real BigQuery data.",
            "decoded_rows": len(decoded_df),
            "wallets_ranked": len(rankings),
            "n_wallets_requested": args.n_wallets,
        },
    )
    print(f"Synthetic: {len(decoded_df)} closes -> {len(rankings)} ranked wallets")
    print(f"  rankings: {rankings_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
