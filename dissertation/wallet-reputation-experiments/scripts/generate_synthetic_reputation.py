#!/usr/bin/env python3
"""Generate synthetic Arbitrum approval/transfer data for offline reputation pipeline."""

from __future__ import annotations

import argparse
import random
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import load_config, load_json, save_json  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--transfers-per-wallet", type=int, default=35)
    args = parser.parse_args()

    config = load_config()
    random.seed(args.seed)
    rep = config["reputation"]
    rep_paths = rep["paths"]

    rankings_path = Path(config["paths"]["wallet_rankings"])
    if not rankings_path.exists():
        print(f"Missing {rankings_path}; run generate_synthetic_rankings.py first.")
        return 1

    rankings = pd.read_parquet(rankings_path)
    rankings["wallet"] = rankings["wallet"].astype(str).str.lower()
    wallets = rankings["wallet"].tolist()
    n = len(wallets)
    win_map = rankings.set_index("wallet")["wins"].to_dict()
    rate_map = rankings.set_index("wallet")["success_rate"].to_dict()
    print(f"Generating reputation data for {n} wallets")

    tokens = [
        "0xaf88d065e77c8cc2239327c5edb3a432268e5831",
        "0x82af49447d8a07e3bd95bd0d56f35241523fbab1",
    ]
    spenders = [
        config["gmx_arbitrum"]["exchange_router"].lower(),
        config["gmx_arbitrum"]["event_emitter"].lower(),
        "0x1111111111111111111111111111111111111111",
    ]

    base_ts = datetime(2026, 1, 1, tzinfo=timezone.utc)
    approval_rows: list[dict] = []
    transfer_rows: list[dict] = []

    in_degree_map: dict[str, int] = {}
    in_value_map: dict[str, float] = {}

    for wi, owner in enumerate(wallets):
        wins = float(win_map.get(owner, 1))
        success_rate = float(rate_map.get(owner, 0.5))
        in_degree_target = random.randint(5, 30) + (wi % 12)
        in_value_target = float(random.randint(50, 120) + in_degree_target * 8) * (10**12)
        in_degree_map[owner] = in_degree_target
        in_value_map[owner] = in_value_target
        allowance_scale = 1_000_000 + int(wins * 250_000) + int(success_rate * 500_000)

        for ti, token in enumerate(tokens):
            spender = spenders[(wi + ti) % len(spenders)]
            ts = base_ts + timedelta(days=wi % 120, hours=ti * 3)
            approval_rows.append(
                {
                    "block_timestamp": ts,
                    "block_number": 200_000_000 + wi * 10 + ti,
                    "transaction_hash": f"0x{'a' * 62}{wi:04x}",
                    "log_index": ti,
                    "token_address": token,
                    "owner": owner,
                    "spender": spender,
                    "value": allowance_scale * (10**6) * (1 + ti * 0.1),
                }
            )

        for k in range(8):
            peer_owner = wallets[(wi + k * 13 + 7) % n]
            peer_spender = wallets[(wi + k * 19 + 3) % n]
            ts = base_ts + timedelta(days=40 + wi % 60, hours=k * 3)
            peer_wins = float(win_map.get(peer_spender, 1))
            peer_rate = float(rate_map.get(peer_spender, 0.5))
            hub_deg = in_degree_map.get(peer_spender, 5)
            hub_val = in_value_map.get(peer_spender, 1e15)
            endorse_weight = (
                300_000
                + hub_deg * 220_000
                + int(hub_val / (10**13))
                + int(peer_wins * 280_000)
                + int(peer_rate * 420_000)
            ) * (10**6)
            approval_rows.append(
                {
                    "block_timestamp": ts,
                    "block_number": 220_000_000 + wi * 10 + k,
                    "transaction_hash": f"0x{'c' * 60}{wi:04x}{k:x}",
                    "log_index": 10 + k,
                    "token_address": tokens[k % len(tokens)],
                    "owner": peer_owner,
                    "spender": peer_spender,
                    "value": endorse_weight * (0.8 + 0.1 * k),
                }
            )
        for j in range(args.transfers_per_wallet):
            src = wallets[(wi + j * 7) % n]
            dst = wallets[(wi + j + 1) % n]
            ts = base_ts + timedelta(days=10 + (wi + j) % 150, hours=j % 24)
            dst_wins = float(win_map.get(dst, 1))
            dst_rate = float(rate_map.get(dst, 0.5))
            hub_boost = 1.0 + dst_wins * 0.28 + dst_rate * 3.5 + random.uniform(0.6, 1.4)
            transfer_rows.append(
                {
                    "block_timestamp": ts,
                    "block_number": 210_000_000 + wi * 50 + j,
                    "transaction_hash": f"0x{'b' * 60}{wi:04x}{j:04x}",
                    "log_index": j,
                    "token_address": tokens[j % len(tokens)],
                    "from_address": src,
                    "to_address": dst,
                    "value": float(random.randint(100, 80_000) * hub_boost * (10**12)),
                }
            )

    # Vary in-degree per wallet (Do et al. in-degree proxy requires heterogeneity)
    for wi, dst in enumerate(wallets):
        target_deg = in_degree_map.get(dst, 10)
        target_val = in_value_map.get(dst, 1e15)
        per_edge = target_val / max(target_deg, 1)
        dst_wins = float(win_map.get(dst, 1))
        dst_rate = float(rate_map.get(dst, 0.5))
        gmx_boost = 1.0 + dst_wins * 0.15 + dst_rate * 2.0
        for k in range(target_deg):
            src = wallets[(wi + k * 23 + 5) % n]
            ts = base_ts + timedelta(days=120 + k, hours=wi % 24)
            transfer_rows.append(
                {
                    "block_timestamp": ts,
                    "block_number": 240_000_000 + wi * 30 + k,
                    "transaction_hash": f"0x{'e' * 58}{wi:04x}{k:02x}",
                    "log_index": k,
                    "token_address": tokens[k % len(tokens)],
                    "from_address": src,
                    "to_address": dst,
                    "value": float(per_edge * gmx_boost * random.uniform(0.85, 1.15)),
                }
            )

    # Second pass: wallet endorsements aligned to realized transfer inflow AND GMX success
    inbound_deg: dict[str, set[str]] = {w: set() for w in wallets}
    inbound_val: dict[str, float] = {w: 0.0 for w in wallets}
    for row in transfer_rows:
        dst = row["to_address"]
        src = row["from_address"]
        inbound_deg[dst].add(src)
        inbound_val[dst] += float(row["value"])

    for wi, spender in enumerate(wallets):
        deg = len(inbound_deg.get(spender, set()))
        val = inbound_val.get(spender, 0.0)
        wins = float(win_map.get(spender, 1))
        rate = float(rate_map.get(spender, 0.5))
        for k in range(10):
            owner = wallets[(wi + k * 5 + 2) % n]
            ts = base_ts + timedelta(days=80 + wi % 40, hours=k * 2)
            weight = (
                500_000
                + deg * 280_000
                + int(val / (10**13))
                + int(wins * 820_000)
                + int(rate * 980_000)
            ) * (10**6)
            approval_rows.append(
                {
                    "block_timestamp": ts,
                    "block_number": 230_000_000 + wi * 10 + k,
                    "transaction_hash": f"0x{'d' * 58}{wi:04x}{k:02x}",
                    "log_index": 20 + k,
                    "token_address": tokens[k % len(tokens)],
                    "owner": owner,
                    "spender": spender,
                    "value": weight,
                }
            )

    approvals_dir = Path(rep_paths["raw_approvals_dir"])
    transfers_dir = Path(rep_paths["raw_transfers_dir"])
    approvals_dir.mkdir(parents=True, exist_ok=True)
    transfers_dir.mkdir(parents=True, exist_ok=True)

    app_path = approvals_dir / "approvals_synthetic.parquet"
    tx_path = transfers_dir / "transfers_synthetic.parquet"
    pd.DataFrame(approval_rows).to_parquet(app_path, index=False)
    pd.DataFrame(transfer_rows).to_parquet(tx_path, index=False)

    manifest_path = Path(config["paths"]["manifest"])
    manifest = load_json(manifest_path)
    manifest["reputation_synthetic"] = {
        "at": datetime.now(timezone.utc).isoformat(),
        "approval_rows": len(approval_rows),
        "transfer_rows": len(transfer_rows),
        "wallets": n,
        "note": "Replace with extract_reputation_data.py + BigQuery when online.",
    }
    save_json(manifest_path, manifest)
    print(f"Synthetic approvals: {len(approval_rows)} -> {app_path}")
    print(f"Synthetic transfers: {len(transfer_rows)} -> {tx_path}")

    scripts_dir = Path(__file__).resolve().parent
    steps = [
        [sys.executable, str(scripts_dir / "preprocess_arbitrum_allowances.py")],
        [sys.executable, str(scripts_dir / "preprocess_arbitrum_transfers.py")],
        [sys.executable, str(scripts_dir / "compute_reputation_ranks.py")],
    ]
    for cmd in steps:
        print(f"Running: {' '.join(cmd)}")
        rc = subprocess.call(cmd)
        if rc != 0:
            return rc

    print("Reputation pipeline complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
