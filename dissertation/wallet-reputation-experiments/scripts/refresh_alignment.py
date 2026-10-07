#!/usr/bin/env python3
"""Recompute the alignment entries of eval_summary.json without timing anything again.

A change to a proxy moves alignment numbers but no runtime. This script reloads
the committed parquet and the scores in wallet_rankings.parquet, recomputes
the proxies, the alignment and six-Aave reports, the Aave edge diagnostics,
the family means of the damping sweep and the two top-token checks, and writes
them into the existing summary.

Kept as measured: the benchmark and scaling entries, the runtimes and elapsed
times of the damping sweep, the sample-size sweep (its rows hold transfer and
allowance means only, and its Tier-2 pool is not in the repository) and the
GMX realized-gain variant check. The refresh is recorded under
"alignment_refresh".

Usage:
    python scripts/refresh_alignment.py --note "why the refresh was needed"
    python scripts/export_latex_results.py
    python scripts/publish_results.py
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import load_config, load_json, save_json, tier2_reputation_paths  # noqa: E402
from evaluate_alignment import build_alignment_report, build_six_aave_alignment_report  # noqa: E402
from proxy_metrics import compute_all_proxies  # noqa: E402
from run_dissertation_eval import _build_aave_diagnostics  # noqa: E402
from run_robustness_eval import damping_family_taus, run_top_token_sweep  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--summary", type=Path, help="eval_summary.json to update (default: config path)")
    parser.add_argument("--note", required=True, help="reason for the refresh, stored in the summary")
    args = parser.parse_args()

    config = load_config()
    summary_path = args.summary or Path(config["paths"]["eval_summary"])
    summary = load_json(summary_path)
    if not summary or summary.get("synthetic"):
        print(f"{summary_path} is missing or synthetic; run run_dissertation_eval.py --real first.")
        return 1

    rep_paths = tier2_reputation_paths(config)
    rankings = pd.read_parquet(config["paths"]["wallet_rankings"])
    rankings["wallet"] = rankings["wallet"].astype(str).str.lower()
    wallets = rankings["wallet"].tolist()
    decoded = pd.read_parquet(config["paths"]["decoded_events"])
    allowances = pd.read_parquet(rep_paths["latest_allowances"])
    transfers = pd.read_parquet(rep_paths["transfer_events"])
    aave_path = Path(config["paths"]["aave_events"])
    delegation_path = Path(config["paths"]["aave_delegation_events"])
    aave_events = pd.read_parquet(aave_path) if aave_path.exists() else None
    delegation_events = pd.read_parquet(delegation_path) if delegation_path.exists() else None

    min_closes = int(config["ranking"]["min_closes"])
    print(f"Recomputing proxies for {len(wallets)} wallets...")
    proxies = compute_all_proxies(transfers, allowances, decoded, wallets, min_closes=min_closes)
    merged = rankings.merge(proxies, on="wallet", how="inner")

    align_cfg = config.get("alignment") or {}
    bootstrap_cfg = {
        "n_boot": int(align_cfg.get("bootstrap_resamples", 400)),
        "seed": int(align_cfg.get("bootstrap_seed", 42)),
    }
    print(f"Alignment (n_boot={bootstrap_cfg['n_boot']}, seed={bootstrap_cfg['seed']})...")
    alignment = build_alignment_report(merged, bootstrap=bootstrap_cfg)
    six_aave = build_six_aave_alignment_report(merged)
    summary.update(
        {
            "n_wallets": len(merged),
            "alignment": alignment,
            "six_aave_alignment": six_aave,
            "method_proxy_matrix": alignment["method_proxy_matrix"],
            "six_aave_method_proxy_matrix": six_aave["method_proxy_matrix"],
            "family_winners": alignment["family_winners"],
            "six_aave_family_winners": six_aave["family_winners"],
            "aave_edge_diagnostics": _build_aave_diagnostics(
                wallets, config, allowances, transfers, aave_events, delegation_events, six_aave
            ),
        }
    )

    rob = summary.get("robustness")
    if rob:
        sweep = rob.get("damping_sweep") or {}
        for row in sweep.get("rows") or []:
            print(f"Damping sweep d={row['damping']:.2f} (family means only)...")
            row.update(damping_family_taus(wallets, allowances, transfers, proxies, config, float(row["damping"])))
        for key, rank_by in (("top_token_subgraph", "value"), ("top_token_subgraph_by_count", "count")):
            print(f"Top-token subgraph ({rank_by})...")
            rob[key] = run_top_token_sweep(wallets, allowances, transfers, decoded, config, min_closes, rank_by=rank_by)

    summary["alignment_refresh"] = {
        "at": datetime.now(timezone.utc).isoformat(),
        "note": args.note,
        "recomputed": [
            "alignment",
            "six_aave_alignment",
            "method_proxy_matrix",
            "six_aave_method_proxy_matrix",
            "family_winners",
            "six_aave_family_winners",
            "aave_edge_diagnostics",
            "robustness.damping_sweep (family means)",
            "robustness.top_token_subgraph",
            "robustness.top_token_subgraph_by_count",
        ],
        "kept_from": summary.get("generated_at"),
    }
    save_json(summary_path, summary)
    print(f"Updated {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
