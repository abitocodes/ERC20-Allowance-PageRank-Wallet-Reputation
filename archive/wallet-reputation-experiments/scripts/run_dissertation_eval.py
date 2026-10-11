#!/usr/bin/env python3
"""Master dissertation evaluation pipeline.

Offline (--fixtures): synthetic GMX + reputation + Aave data, no BigQuery.
Real (--real): assumes extract/preprocess scripts already ran.

Output: data/2-processed-tables-and-evaluations/eval_summary.json
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from benchmark_runtime import (  # noqa: E402
    TIMING_PROTOCOL,
    benchmark_reputation,
    benchmark_scaling,
    benchmark_tier2_scaling,
    reset_timing_cache,
)
from common import build_tier2_wallet_pool, load_config, save_json, tier2_reputation_paths  # noqa: E402
from evaluate_alignment import (  # noqa: E402
    METHOD_LABELS,
    METHODS,
    PROXY_FAMILIES,
    SIX_AAVE_LABELS,
    SIX_AAVE_METHODS,
    build_alignment_report,
    build_six_aave_alignment_report,
)
from pagerank_variants import AWP_ID, ENDORSERANK_ID, collect_six_aave_edges  # noqa: E402
from project_paths import ARCHIVE_DIR, EN_LEFTOVER_DIR  # noqa: E402
from proxy_metrics import compute_all_proxies  # noqa: E402
from run_robustness_eval import run_robustness_eval  # noqa: E402


def _run_script(name: str, extra: list[str] | None = None) -> int:
    scripts_dir = Path(__file__).resolve().parent
    cmd = [sys.executable, str(scripts_dir / name)] + (extra or [])
    print(f"\n>> {' '.join(cmd)}")
    return subprocess.call(cmd)


def _build_aave_diagnostics(
    wallets: list[str],
    config: dict,
    allowances: pd.DataFrame,
    transfers: pd.DataFrame,
    aave_events: pd.DataFrame | None,
    delegation_events: pd.DataFrame | None,
    six_aave_alignment: dict,
) -> dict:
    edge_map = collect_six_aave_edges(
        wallets, config, allowances, transfers, aave_events, delegation_events
    )
    n = len(wallets)
    diagnostics: dict = {"n_wallets": n, "aave_missing": aave_events is None or aave_events.empty}
    for key in (
        "liq_pr",
        "borrow_pr",
        "repay_pr",
        "borrow_pr_pool",
        "repay_pr_pool",
        "delegation_pr",
    ):
        edges = edge_map.get(key, pd.DataFrame())
        ec = len(edges)
        wallets_touched = set()
        if not edges.empty:
            wallets_touched = set(edges["from_node"]) | set(edges["to_node"])
        cross = six_aave_alignment.get("diagnostic_matrix", {}).get(key)
        if cross is None and key in ("borrow_pr_pool", "repay_pr_pool"):
            cross_proxy = six_aave_alignment.get("diagnostic_methods", {}).get(key, {})
            cross = {
                fam: cross_proxy.get(f"{fam}_mean_tau") for fam in PROXY_FAMILIES
            }
        mean_tau_vals = []
        if key in SIX_AAVE_METHODS:
            row = six_aave_alignment.get("method_proxy_matrix", {}).get(key, {})
            mean_tau_vals = [v for v in row.values() if v is not None]
        elif isinstance(cross, dict):
            mean_tau_vals = [v for v in cross.values() if v is not None]
        diagnostics[key] = {
            "edge_count": ec,
            "wallets_in_graph": len(wallets_touched),
            "coverage_pct": round(100.0 * len(wallets_touched) / n, 2) if n else 0.0,
            "mean_tau_avg": float(sum(mean_tau_vals) / len(mean_tau_vals)) if mean_tau_vals else None,
        }
    diagnostics["delegation_deferred"] = delegation_events is None or delegation_events.empty
    return diagnostics


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixtures", action="store_true", help="Generate synthetic data (no GCP)")
    parser.add_argument("--real", action="store_true", help="Use existing BigQuery-derived parquet")
    parser.add_argument("--n-wallets", type=int, default=571)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--benchmark-repeats", type=int, default=5)
    parser.add_argument("--export-latex", action="store_true", help="Run export_latex_results.py after eval")
    parser.add_argument(
        "--skip-aave",
        action="store_true",
        help="Do not require Aave lending parquet (Aave PR scores may be zero)",
    )
    parser.add_argument(
        "--robustness",
        action="store_true",
        help="Run Tier-3 robustness sweeps (damping, top-token, sample-size)",
    )
    args = parser.parse_args()

    if not args.fixtures and not args.real:
        parser.error("Specify --fixtures (offline) or --real (post-BigQuery)")

    config = load_config()

    if args.fixtures:
        rc = _run_script(
            "generate_synthetic_rankings.py",
            ["--n-wallets", str(args.n_wallets), "--seed", str(args.seed)],
        )
        if rc != 0:
            return rc
        rc = _run_script("generate_synthetic_reputation.py", ["--seed", str(args.seed)])
        if rc != 0:
            return rc
        rc = _run_script("generate_synthetic_aave.py", ["--seed", str(args.seed)])
        if rc != 0:
            return rc
        rc = _run_script("compute_reputation_ranks.py")
        if rc != 0:
            return rc
    else:
        rc = _run_script("compute_rankings.py")
        if rc != 0:
            return rc
        rc = _run_script("compute_reputation_ranks.py")
        if rc != 0:
            return rc

    rankings_path = Path(config["paths"]["wallet_rankings"])
    decoded_path = Path(config["paths"]["decoded_events"])
    rep = config["reputation"]
    rep_paths = tier2_reputation_paths(config)
    allowances_path = Path(rep_paths["latest_allowances"])
    transfers_path = Path(rep_paths["transfer_events"])
    aave_path = Path(config["paths"]["aave_events"])
    delegation_path = Path(config["paths"]["aave_delegation_events"])

    for p in (rankings_path, decoded_path, allowances_path, transfers_path):
        if not p.exists():
            print(f"Missing required file: {p}")
            return 1

    if not aave_path.exists() and not args.skip_aave:
        print(f"Note: {aave_path} missing ??Aave PR methods will be zero.")
        print("  Run: extract_aave_lending.py --gmx-only --extract --yes && preprocess_aave_lending.py")
        print("  Or pass --skip-aave to suppress this notice.")

    rankings = pd.read_parquet(rankings_path)
    rankings["wallet"] = rankings["wallet"].astype(str).str.lower()
    wallets = rankings["wallet"].tolist()

    decoded = pd.read_parquet(decoded_path)
    allowances = pd.read_parquet(allowances_path)
    transfers = pd.read_parquet(transfers_path)

    aave_events = pd.read_parquet(aave_path) if aave_path.exists() else None
    delegation_events = pd.read_parquet(delegation_path) if delegation_path.exists() else None

    min_closes = int(config["ranking"]["min_closes"])
    print(f"Loading cohort data ({len(wallets)} wallets)...")
    proxies = compute_all_proxies(transfers, allowances, decoded, wallets, min_closes=min_closes)
    merged = rankings.merge(proxies, on="wallet", how="inner")

    missing_methods = [col for col in METHODS.values() if col not in merged.columns]
    if missing_methods:
        print(f"Missing score columns: {missing_methods}; run compute_reputation_ranks.py")
        return 1

    missing_six = [col for col in SIX_AAVE_METHODS.values() if col not in merged.columns]
    if missing_six:
        print(f"Missing six-aave score columns: {missing_six}; run compute_reputation_ranks.py")
        return 1

    align_cfg = config.get("alignment") or {}
    bootstrap_cfg = {
        "n_boot": int(align_cfg.get("bootstrap_resamples", 400)),
        "seed": int(align_cfg.get("bootstrap_seed", 42)),
    }
    print(
        f"Alignment with paired wallet bootstrap "
        f"(n_boot={bootstrap_cfg['n_boot']}, seed={bootstrap_cfg['seed']})..."
    )
    alignment = build_alignment_report(merged, bootstrap=bootstrap_cfg)
    six_aave_alignment = build_six_aave_alignment_report(merged)

    print("Benchmarking EndorseRank vs AWP (full cohort)...")
    reset_timing_cache()
    benchmark = benchmark_reputation(
        wallets,
        allowances,
        transfers,
        config,
        repeats=args.benchmark_repeats,
        decoded=decoded,
        aave_events=aave_events,
        delegation_events=delegation_events,
    )

    print("Tier-1 in-cohort scaling benchmark...")
    benchmark_scaling_result = benchmark_scaling(
        wallets,
        allowances,
        transfers,
        config,
        repeats=args.benchmark_repeats,
        decoded=decoded,
        aave_events=aave_events,
        authoritative_full_cohort=benchmark,
    )

    wallet_pool, pool_meta = build_tier2_wallet_pool(wallets, allowances, transfers, config)
    tier2_paths = config.get("benchmark", {}).get("tier2_paths") or {}
    tier2_allowances = allowances
    tier2_transfers = transfers
    tier2_processed = Path(tier2_paths.get("transfer_events", ""))
    if tier2_processed.exists():
        tier2_allowances = pd.read_parquet(tier2_paths["latest_allowances"])
        tier2_transfers = pd.read_parquet(tier2_paths["transfer_events"])
        pool_from_t2 = build_tier2_wallet_pool(
            wallets, tier2_allowances, tier2_transfers, config
        )
        wallet_pool, pool_meta = pool_from_t2

    print(f"Tier-2 scaling benchmark (pool N={len(wallet_pool)})...")
    benchmark_tier2_result = benchmark_tier2_scaling(
        wallet_pool,
        tier2_allowances,
        tier2_transfers,
        config,
        repeats=args.benchmark_repeats,
    )

    robustness_result = None
    if args.robustness:
        print("Tier-3 robustness sweeps (damping, top-token, sample-size)...")
        robustness_result = run_robustness_eval(
            wallets,
            wallet_pool,
            allowances,
            transfers,
            decoded,
            merged,
            config,
            min_closes,
            repeats=args.benchmark_repeats,
        )

    aave_diagnostics = _build_aave_diagnostics(
        wallets,
        config,
        allowances,
        transfers,
        aave_events,
        delegation_events,
        six_aave_alignment,
    )

    note = (
        "Synthetic fixture evaluation; replace with --real after BigQuery extraction."
        if args.fixtures
        else "BigQuery-derived parquet evaluation (goog_blockchain_arbitrum_one_us + GMX EventEmitter)."
    )

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "synthetic": args.fixtures,
        "n_wallets": len(merged),
        "note": note,
        "timing_protocol": {
            **TIMING_PROTOCOL,
            "timed_repeats": args.benchmark_repeats,
            "applies_to": [
                "benchmark",
                "benchmark_scaling",
                "benchmark_tier2",
                "robustness.damping_sweep",
                "robustness.sample_size_sweep",
            ],
        },
        "bootstrap_protocol": {
            **bootstrap_cfg,
            "ci_level": 0.95,
            "design": "paired wallet resampling shared across methods and proxies",
        },
        "benchmark": benchmark,
        "benchmark_scaling": benchmark_scaling_result,
        "benchmark_tier2": benchmark_tier2_result,
        "wallet_pool_meta": pool_meta,
        "alignment": alignment,
        "six_aave_alignment": six_aave_alignment,
        "method_proxy_matrix": alignment["method_proxy_matrix"],
        "six_aave_method_proxy_matrix": six_aave_alignment["method_proxy_matrix"],
        "family_winners": alignment["family_winners"],
        "six_aave_family_winners": six_aave_alignment["family_winners"],
        "aave_edge_diagnostics": aave_diagnostics,
        "robustness": robustness_result,
        "dataset": {
            "rankings_path": str(rankings_path),
            "decoded_events_path": str(decoded_path),
            "allowances_path": str(allowances_path),
            "transfers_path": str(transfers_path),
            "aave_events_path": str(aave_path) if aave_path.exists() else None,
            "delegation_events_path": str(delegation_path) if delegation_path.exists() else None,
        },
    }

    out_path = Path(config["paths"]["eval_summary"])
    save_json(out_path, summary)
    print(f"\nEval summary -> {out_path}")

    er_rt = benchmark[ENDORSERANK_ID]["runtime_sec_mean"]
    awp_rt = benchmark[AWP_ID]["runtime_sec_mean"]
    print(f"  EndorseRank runtime: {er_rt:.3f}s | AWP: {awp_rt:.3f}s")

    print("\n  6-Aave method mean tau matrix:")
    matrix = six_aave_alignment["method_proxy_matrix"]
    header = f"    {'Method':14s} " + " ".join(f"{f[:6]:>7s}" for f in PROXY_FAMILIES)
    print(header)
    for method_id in SIX_AAVE_METHODS:
        label = SIX_AAVE_LABELS.get(method_id, method_id)
        row = matrix.get(method_id, {})
        vals = " ".join(
            f"{row.get(f, float('nan')):7.3f}" if row.get(f) is not None else "    ---"
            for f in PROXY_FAMILIES
        )
        print(f"    {label:14s} {vals}")

    print("\n  Aave edge diagnostics:")
    for key, diag in aave_diagnostics.items():
        if isinstance(diag, dict) and "edge_count" in diag:
            print(
                f"    {key:16s} edges={diag['edge_count']:5d}  "
                f"coverage={diag['coverage_pct']:.1f}%"
            )

    if args.export_latex:
        rc = _run_script("export_latex_results.py")
        if rc != 0:
            return rc
        rc = _run_script("export_method_matrix.py", ["--preset", "three"])
        if rc != 0:
            return rc
        archive_tex = EN_LEFTOVER_DIR / "archive" / "extended-baselines" / "tables"
        archive_csv = ARCHIVE_DIR
        for preset in ("seven", "six-aave"):
            rc = _run_script(
                "export_method_matrix.py",
                [
                    "--preset",
                    preset,
                    "--out-dir",
                    str(archive_tex),
                    "--csv-out-dir",
                    str(archive_csv),
                ],
            )
            if rc != 0:
                return rc

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
