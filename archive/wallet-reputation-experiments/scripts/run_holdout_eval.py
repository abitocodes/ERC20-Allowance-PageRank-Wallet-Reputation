#!/usr/bin/env python3
"""t1 scores versus pre-registered t2 labels.

EndorseRank ("endorserank_vt") and AWP in its published form ("awp_paper") share
AWP's edge weights; "endorserank_vt_activity" restarts EndorseRank as AWP restarts
(sensitivity analysis). "endorserank" and "awp" are the allowance and transfer
layers walked alone (C-PR at lambda = 1 and 0), kept for the rule of
14 September and the S-PR ablation. Does not overwrite contemporaneous
dissertation eval_summary.json.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import load_config, save_json  # noqa: E402
from holdout import (  # noqa: E402
    BASELINE_IDS,
    EXTERNAL_LABELS,
    HOLDOUT_LABELS,
    SPRING_CONTRASTS,
    build_holdout_fixture_frames,
    classify_external_result,
    correlate_holdout,
    evaluate_primary_criterion,
    filter_transfers_as_of,
    future_aave_labels,
    future_approval_labels,
    future_drain_labels,
    future_gmx_labels,
    future_transfer_labels,
    holdout_bounds,
    holdout_tau_diff,
    label_prevalence,
    latest_positive_as_of,
    load_approval_events,
    load_transfer_events,
    resolve_score_wallets,
    score_awp,
    score_awp_paper,
    score_coupled,
    score_endorserank,
    score_endorserank_vt,
    score_seeded,
    scores_to_frame,
    t1_baselines,
    t1_connected_wallets,
)
from pagerank import build_awp_edges, build_endorserank_edges  # noqa: E402
from pagerank_variants import SEEDED_PR_ID, hybrid_lambda_map  # noqa: E402


def _load_matched_wallets(config: dict) -> list[str] | None:
    path = Path(config["paths"]["wallet_rankings"])
    if not path.exists():
        return None
    df = pd.read_parquet(path)
    return df["wallet"].astype(str).str.lower().tolist()


def _score_methods(
    latest_t1: pd.DataFrame,
    transfers_t1: pd.DataFrame,
    score_end: pd.Timestamp,
    wallets: list[str],
    config: dict,
) -> dict[str, dict[str, float]]:
    scores: dict[str, dict[str, float]] = {
        "endorserank": score_endorserank(latest_t1, wallets, config),
        "awp": score_awp(transfers_t1, score_end, wallets, config),
    }
    for method_id, lam in hybrid_lambda_map(config).items():
        scores[method_id] = score_coupled(latest_t1, transfers_t1, score_end, wallets, config, lam)
    scores[SEEDED_PR_ID] = score_seeded(latest_t1, transfers_t1, score_end, wallets, config)
    scores.update(t1_baselines(latest_t1, transfers_t1, wallets))
    return scores


def run_holdout(
    config: dict,
    approvals: pd.DataFrame,
    transfers: pd.DataFrame,
    decoded: pd.DataFrame,
    matched: list[str] | None,
    extra_scores: dict[str, dict[str, float]] | None = None,
    aave_events: pd.DataFrame | None = None,
) -> dict:
    score_end, outcome_start, outcome_end = holdout_bounds(config)
    ho = config["reputation"]["holdout"]
    min_closes = int(ho.get("min_closes", 3))
    n_boot = int(ho.get("bootstrap_resamples", 400))
    seed = int(ho.get("bootstrap_seed", 42))

    latest_t1 = latest_positive_as_of(approvals, score_end)
    transfers_t1 = filter_transfers_as_of(transfers, score_end)
    rep = config["reputation"]
    er_edges = build_endorserank_edges(latest_t1)
    awp_edges = build_awp_edges(
        transfers_t1,
        score_end,
        float(rep["awp_decay_k"]),
        float(rep["awp_decay_t0_days"]),
    )
    t1_nodes = t1_connected_wallets(er_edges, awp_edges)
    wallets = resolve_score_wallets(matched, t1_nodes)
    if not wallets:
        raise RuntimeError("No t1-connected wallets after holdout filters.")

    scores = _score_methods(latest_t1, transfers_t1, score_end, wallets, config)
    # Added here and not in _score_methods, which the registered replication reruns as it stands.
    scores["endorserank_vt"] = score_endorserank_vt(latest_t1, score_end, wallets, config)
    scores["endorserank_vt_activity"] = score_endorserank_vt(
        latest_t1, score_end, wallets, config, activity_restarts=True
    )
    scores["awp_paper"] = score_awp_paper(transfers_t1, score_end, wallets, config)
    if extra_scores:
        scores.update(extra_scores)

    frame = scores_to_frame(wallets, scores)
    labels = future_approval_labels(
        approvals, latest_t1, outcome_start, outcome_end, wallets
    )
    flow = future_transfer_labels(transfers, transfers_t1, outcome_start, outcome_end, wallets)
    gmx = future_gmx_labels(decoded, outcome_start, outcome_end, wallets, min_closes)
    drain = future_drain_labels(
        approvals, transfers, outcome_start, outcome_end, wallets
    )
    aave = future_aave_labels(aave_events, outcome_start, outcome_end, wallets)
    merged = (
        frame.merge(labels, on="wallet", how="left")
        .merge(flow, on="wallet", how="left")
        .merge(gmx, on="wallet", how="left")
        .merge(drain, on="wallet", how="left")
        .merge(aave, on="wallet", how="left")
    )

    methods = list(scores.keys())
    alignment = correlate_holdout(
        merged, methods, labels=HOLDOUT_LABELS, n_resamples=n_boot, seed=seed
    )
    prevalence = label_prevalence(merged, EXTERNAL_LABELS + ("future_drain_owners", "future_aave_liq_count"))
    verdicts: dict[str, dict[str, str]] = {}
    for method in methods:
        verdicts[method] = {}
        for lab in EXTERNAL_LABELS:
            stat = alignment["methods"].get(method, {}).get(lab, {})
            verdicts[method][lab] = classify_external_result(stat, prevalence.get(lab))
    tau_diff = holdout_tau_diff(merged, SPRING_CONTRASTS, n_resamples=n_boot, seed=seed)
    hyb = rep.get("hybrid") or {}
    return {
        "protocol": "t1_score_vs_t2_label",
        "score_end": str(score_end),
        "outcome_start": str(outcome_start),
        "outcome_end": str(outcome_end),
        "n_wallets": len(wallets),
        "n_t1_allowance_rows": int(len(latest_t1)),
        "n_t1_transfers": int(len(transfers_t1)),
        "methods": methods,
        "baselines": list(BASELINE_IDS),
        "hybrid": {
            "coupled_lambda": hybrid_lambda_map(config),
            "seeded_teleport_floor": float(hyb.get("seeded_teleport_floor", 0.0)),
        },
        "bootstrap": {"n_boot": n_boot, "seed": seed, "ci_level": 0.95},
        "alignment": alignment,
        "prevalence": prevalence,
        "verdicts": verdicts,
        "tau_diff": tau_diff,
        "primary_criterion": evaluate_primary_criterion(tau_diff),
        "at": datetime.now(timezone.utc).isoformat(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fixtures",
        action="store_true",
        help="Use synthetic events that straddle the holdout cutoff.",
    )
    parser.add_argument("--n-wallets", type=int, default=48)
    parser.add_argument("--bootstrap", type=int, default=None)
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="summary path (default: eval_summary.json, or eval_summary_spenders.json for --cohort spenders)",
    )
    parser.add_argument(
        "--cohort",
        choices=("matched", "spenders"),
        default="matched",
        help="matched = GMX rankings ∩ t1 graph; spenders = t1 inbound allowance recipients.",
    )
    args = parser.parse_args()

    config = load_config()
    if args.bootstrap is not None:
        config["reputation"]["holdout"]["bootstrap_resamples"] = args.bootstrap
    out_path = Path(config["reputation"]["paths"]["holdout_summary"])
    if not args.fixtures and args.cohort == "spenders":
        out_path = out_path.with_name("eval_summary_spenders.json")
    if args.out is not None:
        out_path = args.out

    if args.fixtures:
        frames = build_holdout_fixture_frames(n_wallets=args.n_wallets)
        matched = frames["wallets"]["wallet"].tolist()
        summary = run_holdout(
            config,
            frames["approvals"],
            frames["transfers"],
            frames["decoded"],
            matched,
        )
        summary["source"] = "fixtures"
    else:
        approvals = load_approval_events(config)
        transfers = load_transfer_events(config)
        decoded_path = Path(config["paths"]["decoded_events"])
        if not decoded_path.exists():
            print(f"Missing {decoded_path}; use --fixtures or run the GMX decode step.")
            return 1
        decoded = pd.read_parquet(decoded_path)
        aave_path = Path(config["paths"]["aave_events"])
        aave = pd.read_parquet(aave_path) if aave_path.exists() else None
        if args.cohort == "spenders":
            score_end, _, _ = holdout_bounds(config)
            latest_t1 = latest_positive_as_of(approvals, score_end)
            matched = sorted(set(latest_t1["spender"].astype(str).str.lower()))
        else:
            matched = _load_matched_wallets(config)
        summary = run_holdout(
            config,
            approvals,
            transfers,
            decoded,
            matched,
            aave_events=aave,
        )
        summary["source"] = "local_parquet"
        summary["cohort"] = args.cohort

    save_json(out_path, summary)
    print(f"holdout n={summary['n_wallets']} methods={summary['methods']} source={summary.get('source')}")
    for lab, prev in summary.get("prevalence", {}).items():
        print(
            f"  prevalence {lab}: defined={prev.get('n_defined')} nonzero={prev.get('n_nonzero')} mean={prev.get('mean')}"
        )
    for method in summary["methods"]:
        print(f"== {method}")
        for lab in EXTERNAL_LABELS:
            stat = summary["alignment"]["methods"].get(method, {}).get(lab, {})
            verdict = summary.get("verdicts", {}).get(method, {}).get(lab)
            print(
                f"  {lab:28s} tau={stat.get('kendall_tau')} "
                f"ci=({stat.get('ci_low')}, {stat.get('ci_high')}) "
                f"n={stat.get('n')} [{verdict}]"
            )
    print("== paired contrasts")
    for row in summary.get("tau_diff", []):
        print(
            f"  {row['label']:40s} on {row['holdout_label']:28s} "
            f"delta={row.get('delta_tau')} ci=({row.get('ci_low')}, {row.get('ci_high')}) "
            f"P(>0)={row.get('share_positive')}"
        )
    print(f"primary criterion: {summary.get('primary_criterion')}")
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
