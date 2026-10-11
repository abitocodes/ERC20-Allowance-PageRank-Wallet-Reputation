#!/usr/bin/env python3
"""Generate synthetic Aave lending + credit delegation events for offline six-Aave eval."""

from __future__ import annotations

import argparse
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import load_config, load_json, save_json  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--aave-fraction", type=float, default=0.15)
    args = parser.parse_args()

    config = load_config()
    random.seed(args.seed)
    pool = config["aave_arbitrum"]["pool_addresses"][0].lower()

    rankings_path = Path(config["paths"]["wallet_rankings"])
    if not rankings_path.exists():
        print(f"Missing {rankings_path}; run generate_synthetic_rankings.py first.")
        return 1

    rankings = pd.read_parquet(rankings_path)
    wallets = rankings["wallet"].astype(str).str.lower().tolist()
    n = len(wallets)
    n_aave = max(20, int(n * args.aave_fraction))
    aave_wallets = set(random.sample(wallets, min(n_aave, n)))

    base_ts = datetime(2026, 1, 15, tzinfo=timezone.utc)
    lending_rows: list[dict] = []
    delegation_rows: list[dict] = []

    for i, w in enumerate(sorted(aave_wallets)):
        ts = base_ts + timedelta(days=i % 120, hours=i % 24)

        # Self borrow (pool-leg only; skipped by W↔W borrow_pr)
        lending_rows.append(
            {
                "event_type": "borrow",
                "user": w,
                "on_behalf_of": w,
                "initiator": w,
                "repayer": None,
                "liquidator": None,
                "pool": pool,
                "amount": float(random.randint(1_000, 50_000) * 10**6),
                "block_timestamp": ts,
                "block_number": 300_000_000 + i,
                "transaction_hash": f"0x{'f1' * 30}{i:04x}",
                "log_index": 0,
            }
        )

        # Cross-wallet borrow: initiator -> onBehalfOf
        peer = wallets[(i * 17 + 3) % n]
        if peer != w and peer in aave_wallets:
            lending_rows.append(
                {
                    "event_type": "borrow",
                    "user": peer,
                    "on_behalf_of": peer,
                    "initiator": w,
                    "repayer": None,
                    "liquidator": None,
                    "pool": pool,
                    "amount": float(random.randint(2_000, 80_000) * 10**6),
                    "block_timestamp": ts + timedelta(days=2),
                    "block_number": 300_100_000 + i,
                    "transaction_hash": f"0x{'f2' * 30}{i:04x}",
                    "log_index": 1,
                }
            )

        # Cross-wallet repay
        victim = wallets[(i * 23 + 5) % n]
        if victim != w:
            lending_rows.append(
                {
                    "event_type": "repay",
                    "user": victim,
                    "on_behalf_of": victim,
                    "initiator": None,
                    "repayer": w,
                    "liquidator": None,
                    "pool": pool,
                    "amount": float(random.randint(1_000, 40_000) * 10**6),
                    "block_timestamp": ts + timedelta(days=5),
                    "block_number": 300_200_000 + i,
                    "transaction_hash": f"0x{'f3' * 30}{i:04x}",
                    "log_index": 0,
                }
            )

        # LiquidationCall: liquidator -> user
        if i % 4 == 0:
            liquidated = wallets[(i * 31 + 7) % n]
            liquidator = w
            if liquidated != liquidator:
                lending_rows.append(
                    {
                        "event_type": "liquidation_call",
                        "user": liquidated,
                        "on_behalf_of": liquidated,
                        "initiator": None,
                        "repayer": None,
                        "liquidator": liquidator,
                        "pool": pool,
                        "amount": float(random.randint(500, 20_000) * 10**6),
                        "block_timestamp": ts + timedelta(days=8),
                        "block_number": 300_300_000 + i,
                        "transaction_hash": f"0x{'f4' * 30}{i:04x}",
                        "log_index": 0,
                    }
                )

        # Credit delegation
        delegatee = wallets[(i * 11 + 9) % n]
        if delegatee != w:
            delegation_rows.append(
                {
                    "from_user": w,
                    "to_user": delegatee,
                    "amount": float(random.randint(5_000, 100_000) * 10**6),
                    "block_timestamp": ts + timedelta(days=3),
                    "block_number": 300_400_000 + i,
                    "transaction_hash": f"0x{'f5' * 30}{i:04x}",
                    "log_index": 0,
                }
            )

    aave_path = Path(config["paths"]["aave_events"])
    delegation_path = Path(config["paths"]["aave_delegation_events"])
    aave_path.parent.mkdir(parents=True, exist_ok=True)

    pd.DataFrame(lending_rows).to_parquet(aave_path, index=False)
    pd.DataFrame(delegation_rows).to_parquet(delegation_path, index=False)

    manifest_path = Path(config["paths"]["manifest"])
    manifest = load_json(manifest_path)
    manifest["aave_synthetic"] = {
        "at": datetime.now(timezone.utc).isoformat(),
        "lending_rows": len(lending_rows),
        "delegation_rows": len(delegation_rows),
        "aave_wallets": len(aave_wallets),
    }
    save_json(manifest_path, manifest)
    print(f"Synthetic aave_events: {len(lending_rows)} -> {aave_path}")
    print(f"Synthetic delegation: {len(delegation_rows)} -> {delegation_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
