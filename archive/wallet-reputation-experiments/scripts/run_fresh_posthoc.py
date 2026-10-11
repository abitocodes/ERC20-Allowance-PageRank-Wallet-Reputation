#!/usr/bin/env python3
"""EndorseRank on the June-August window, computed after the registered results.

The registered replication (run_fresh_holdout.py) scored the methods named in
config/fresh_holdout_2026q3.yaml. EndorseRank as the thesis defines it, AWP's
edge weights on the allowance graph with uniform restarts ("endorserank_vt"),
is not among them, so this script scores it on the same cohorts, labels and
wallet resamples, together with the variant restarted by approving activity
("endorserank_vt_activity"). Nothing here enters the registered decision; the
output is a separate file marked post hoc.

Output: data/2-processed-tables-and-evaluations/registered-replication-2026-06-to-2026-08/
posthoc_endorserank.json
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import load_config, save_json  # noqa: E402
from fresh_holdout import (  # noqa: E402
    REPORT_LABELS,
    build_cohort_frame,
    combine_events,
    load_fresh_events,
    load_registration,
    load_spring_events,
    window_config,
)
from holdout import (  # noqa: E402
    correlate_holdout,
    holdout_bounds,
    holdout_tau_diff,
    latest_positive_as_of,
    score_endorserank_vt,
)
from pagerank import assign_dense_ranks  # noqa: E402
from pagerank_variants import AWP_ID, ENDORSERANK_ACTIVITY_ID, ENDORSERANK_ID  # noqa: E402
from project_paths import REPLICATION_DIR  # noqa: E402

OUT_PATH = REPLICATION_DIR / "posthoc_endorserank.json"
METHODS = (ENDORSERANK_ID, ENDORSERANK_ACTIVITY_ID, AWP_ID, "coupled_pr", "t1_in_approve_degree", "t1_in_degree")
# (label, method_a, method_b, holdout label, role); same layout as holdout.HOLDOUT_CONTRASTS.
CONTRASTS: dict[str, tuple[tuple[str, str, str, str, str], ...]] = {
    "spenders": (
        ("EndorseRank minus t1 in-approve degree", ENDORSERANK_ID, "t1_in_approve_degree", "future_new_approvers", "increment"),
        ("AWP minus t1 in-degree", AWP_ID, "t1_in_degree", "future_new_transfer_senders", "increment"),
        ("EndorseRank minus AWP", ENDORSERANK_ID, AWP_ID, "future_new_approvers", "single_layer"),
        ("AWP minus EndorseRank", AWP_ID, ENDORSERANK_ID, "future_new_transfer_senders", "single_layer"),
        ("C-PR minus EndorseRank", "coupled_pr", ENDORSERANK_ID, "future_new_approvers", "against_single"),
    ),
    "traders": (
        ("EndorseRank minus AWP", ENDORSERANK_ID, AWP_ID, "future_liquidation_free_rate", "single_layer"),
        ("C-PR minus EndorseRank", "coupled_pr", ENDORSERANK_ID, "future_liquidation_free_rate", "against_single"),
    ),
}


def _matched_wallets(config: dict) -> list[str]:
    df = pd.read_parquet(config["paths"]["wallet_rankings"])
    return df["wallet"].astype(str).str.lower().tolist()


def _add_scores(merged: pd.DataFrame, scores: dict[str, dict[str, float]]) -> pd.DataFrame:
    out = merged.copy()
    wallets = out["wallet"].tolist()
    for method, mapping in scores.items():
        ranked = assign_dense_ranks(wallets, mapping).set_index("wallet")["score"]
        out[f"{method}_score"] = out["wallet"].map(ranked).astype(float)
    return out


def main() -> int:
    config = load_config()
    reg = load_registration()
    cfg = window_config(config, reg)
    ho = cfg["reputation"]["holdout"]
    n_boot = int(ho.get("bootstrap_resamples", 400))
    seed = int(ho.get("bootstrap_seed", 42))
    score_end, _, _ = holdout_bounds(cfg)

    spring = load_spring_events(config)
    fresh = load_fresh_events(reg)
    events = {
        "approvals": combine_events(spring["approvals"], fresh["approvals"]),
        "transfers": combine_events(spring["transfers"], fresh["transfers"]),
        "decoded": combine_events(spring["decoded"], fresh["decoded"]),
    }
    latest_t1 = latest_positive_as_of(events["approvals"], score_end)

    report: dict = {
        "note": "Computed after the registered replication was evaluated; not part of the registration.",
        "score_end": str(score_end),
        "bootstrap": {"n_boot": n_boot, "seed": seed, "ci_level": 0.95},
        "cohorts": {},
    }
    for cohort in ("spenders", "traders"):
        merged, _, meta = build_cohort_frame(cfg, events, cohort, _matched_wallets(config))
        wallets = merged["wallet"].tolist()
        merged = _add_scores(
            merged,
            {
                ENDORSERANK_ID: score_endorserank_vt(latest_t1, score_end, wallets, cfg),
                ENDORSERANK_ACTIVITY_ID: score_endorserank_vt(
                    latest_t1, score_end, wallets, cfg, activity_restarts=True
                ),
            },
        )
        labels = tuple(lab for lab in REPORT_LABELS if lab in merged.columns)
        report["cohorts"][cohort] = {
            **meta,
            "methods": list(METHODS),
            "alignment": correlate_holdout(merged, list(METHODS), labels=labels, n_resamples=n_boot, seed=seed),
            "tau_diff": holdout_tau_diff(merged, CONTRASTS[cohort], n_resamples=n_boot, seed=seed),
        }
    report["at"] = datetime.now(timezone.utc).isoformat()
    save_json(OUT_PATH, report)

    for cohort, block in report["cohorts"].items():
        print(f"== {cohort} (n={block['n_wallets']})")
        for method, stats in block["alignment"]["methods"].items():
            cells = " ".join(
                f"{lab} {stats[lab]['kendall_tau']:+.3f}" for lab in stats if stats[lab].get("kendall_tau") is not None
            )
            print(f"  {method:26s} {cells}")
        for row in block["tau_diff"]:
            print(
                f"  {row['label']:40s} {row['holdout_label']:30s} {row['delta_tau']:+.3f} "
                f"[{row['ci_low']:+.3f}, {row['ci_high']:+.3f}]"
            )
    print(f"wrote {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
