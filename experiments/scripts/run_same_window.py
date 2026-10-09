#!/usr/bin/env python3
"""Same-window evaluation on the matched cohort at T_obs (analysis plan, sections 4-6).

Computes every score, the transfer, allowance and Sybil-stability proxies, the
paired-bootstrap Kendall tau of every score on every proxy and family, the
same-window contrasts of the coupled operator, the secondary part of rule A,
the agreement of EndorseRank and AWP, the tie structure, the isolated-node
sensitivity analysis, the damping sweep and the closed-form check of
EndorseRank. Writes data/2-.../same-window/eval_summary.json and the cohort
score table (parts).
"""

from __future__ import annotations

import sys
from math import comb
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import PROC, RAW, load_config, read_parts, save_json, write_parts  # noqa: E402
from graphs import METHOD_LABELS, load_graphs, load_nodes, raw_degrees, score_all  # noqa: E402
from scoring import pagerank_params, scores_on  # noqa: E402
from stats import PairedBootstrap, kendall_tau_b, spearman  # noqa: E402

OUT = PROC / "same-window"
FAMILIES = {
    "transfer": ["in_degree", "in_value"],
    "allowance": ["in_approve_degree", "in_approve_value"],
    "sybil_stability": ["inbound_counterparty_ratio", "transfer_tenure_days", "active_months"],
}
CONTRASTS = [
    # (label, (a, family), (b, family), group)
    ("C-PR transfer minus C-PR (l=0) transfer", ("cpr_l50", "transfer"), ("cpr_l0", "transfer"), "hybrid"),
    ("C-PR allowance minus C-PR (l=1) allowance", ("cpr_l50", "allowance"), ("cpr_l100", "allowance"), "hybrid"),
    ("C-PR sybil minus C-PR (l=0) sybil", ("cpr_l50", "sybil_stability"), ("cpr_l0", "sybil_stability"), "hybrid"),
    ("C-PR sybil minus C-PR (l=1) sybil", ("cpr_l50", "sybil_stability"), ("cpr_l100", "sybil_stability"), "hybrid"),
    ("S-PR transfer minus C-PR (l=0) transfer", ("spr", "transfer"), ("cpr_l0", "transfer"), "hybrid"),
    ("S-PR allowance minus C-PR (l=1) allowance", ("spr", "allowance"), ("cpr_l100", "allowance"), "hybrid"),
    ("S-PR sybil minus C-PR (l=0) sybil", ("spr", "sybil_stability"), ("cpr_l0", "sybil_stability"), "hybrid"),
    ("S-PR sybil minus C-PR (l=1) sybil", ("spr", "sybil_stability"), ("cpr_l100", "sybil_stability"), "hybrid"),
    ("C-PR transfer minus AWP transfer", ("cpr_l50", "transfer"), ("awp", "transfer"), "hybrid_single"),
    ("C-PR allowance minus EndorseRank allowance", ("cpr_l50", "allowance"), ("endorserank", "allowance"), "hybrid_single"),
    ("C-PR sybil minus AWP sybil", ("cpr_l50", "sybil_stability"), ("awp", "sybil_stability"), "hybrid_single"),
    ("C-PR sybil minus EndorseRank sybil", ("cpr_l50", "sybil_stability"), ("endorserank", "sybil_stability"), "hybrid_single"),
    ("EndorseRank allowance minus EndorseRank transfer", ("endorserank", "allowance"), ("endorserank", "transfer"), "er_awp"),
    ("AWP transfer minus EndorseRank transfer", ("awp", "transfer"), ("endorserank", "transfer"), "er_awp"),
    ("EndorseRank allowance minus AWP allowance", ("endorserank", "allowance"), ("awp", "allowance"), "er_awp"),
    ("AWP sybil minus EndorseRank sybil", ("awp", "sybil_stability"), ("endorserank", "sybil_stability"), "er_awp"),
    ("EndorseRank in-approve degree minus EndorseRank in-degree", ("endorserank", "in_approve_degree"), ("endorserank", "in_degree"), "er_awp"),
]


def tie_profile(x: np.ndarray) -> dict:
    vals, counts = np.unique(x, return_counts=True)
    n = len(x)
    tied_pairs = int(sum(comb(int(c), 2) for c in counts if c > 1))
    top = int(np.argmax(counts))
    return {
        "n": n, "distinct": int(len(vals)), "share_pairs_tied": tied_pairs / comb(n, 2),
        "largest_block": int(counts[top]), "largest_block_value": float(vals[top]),
        "zeros": int((x == 0).sum()),
    }


def concordance(x: np.ndarray, y: np.ndarray) -> dict:
    """Pairs ordered by both scores and the discordant share among them (from tau_b and tie counts)."""
    n = len(x)
    n0 = comb(n, 2)
    _, cx = np.unique(x, return_counts=True)
    _, cy = np.unique(y, return_counts=True)
    _, cxy = np.unique(np.stack([x, y], axis=1), axis=0, return_counts=True)
    n1 = sum(comb(int(c), 2) for c in cx)
    n2 = sum(comb(int(c), 2) for c in cy)
    n3 = sum(comb(int(c), 2) for c in cxy)
    tau = kendall_tau_b(x, y)
    both = n0 - n1 - n2 + n3
    diff = tau * np.sqrt((n0 - n1) * (n0 - n2))
    nd = (both - diff) / 2
    return {"pairs": n0, "ordered_by_both": both, "share_ordered_by_both": both / n0,
            "discordant_share_of_ordered": nd / both if both else None, "tau_b": tau}


def closed_form(allow: pd.DataFrame, scores: pd.Series, spender_ids: np.ndarray, damping: float) -> dict:
    """Check s(v) = c (1 + d delta(v)) for spenders whose in-neighbours have no in-edges.

    delta(v) = sum over owners u -> v of w(u, v) / out-strength(u), the owner-normalised
    in-strength; c is the common score of nodes without in-edges.
    """
    a = allow[allow["w_er"] > 0]
    out_strength = a.groupby("src")["w_er"].sum()
    has_in = set(a["dst"].unique())
    no_in_nodes = np.setdiff1d(scores.index.to_numpy(), np.fromiter(has_in, dtype=np.int64))
    c_vals = scores.loc[no_in_nodes]
    c = float(np.median(c_vals)) if len(c_vals) else float("nan")
    a = a.assign(share=a["w_er"].to_numpy() / out_strength.loc[a["src"]].to_numpy())
    delta = a.groupby("dst")["share"].sum()
    depth_one = a.assign(src_has_in=a["src"].isin(has_in)).groupby("dst")["src_has_in"].any()
    sp = pd.Index(np.intersect1d(spender_ids, delta.index.to_numpy()))
    pred = c * (1.0 + damping * delta.loc[sp])
    rel = (scores.loc[sp] - pred).abs() / scores.loc[sp]
    d1 = ~depth_one.loc[sp]
    return {
        "common_value_c": c,
        "spread_of_c": float(c_vals.max() / c_vals.min()) if len(c_vals) else None,
        "spenders": int(len(sp)),
        "depth_one_spenders": int(d1.sum()),
        "within_1pct_all": float((rel <= 0.01).mean()),
        "within_1pct_depth_one": float((rel[d1] <= 0.01).mean()) if d1.any() else None,
        "within_1pct_deeper": float((rel[~d1] <= 0.01).mean()) if (~d1).any() else None,
        "tau_score_vs_delta": kendall_tau_b(scores.loc[sp].to_numpy(), delta.loc[sp].to_numpy()),
    }


def main() -> int:
    cfg = load_config()
    params = pagerank_params(cfg)
    nodes = load_nodes()
    cohort = nodes.loc[nodes["is_cohort"], ["id", "address"]].sort_values("id")
    ids = cohort["id"].to_numpy(np.int64)
    g = load_graphs("tobs")
    print(f"cohort {len(ids):,}; allowance edges {len(g.allow):,}; transfer edges {len(g.transfer):,}", flush=True)

    full, iters = score_all(g, params)
    S = pd.DataFrame({m: scores_on(ids, s).to_numpy() for m, s in full.items()}, index=ids)

    prox = read_parts(RAW / "graph-tables" / "proxies_tobs").merge(
        cohort, left_on="wallet", right_on="address").set_index("id").reindex(ids)
    deg = raw_degrees(g, ids)
    P = pd.DataFrame(index=ids)
    P["in_degree"] = prox["in_degree"].astype(float)
    P["in_value"] = prox["in_value"].astype(float)
    P["in_approve_degree"] = deg["in_approve_degree"]
    P["in_approve_value"] = deg["in_approve_value"]
    for c in FAMILIES["sybil_stability"]:
        P[c] = prox[c].astype(float)

    boot = PairedBootstrap(len(ids), cfg["alignment"]["bootstrap_resamples"], cfg["alignment"]["bootstrap_seed"])
    for m in S:
        boot.add(m, S[m])
    for p in P:
        boot.add(p, P[p])
    proxies = [p for f in FAMILIES.values() for p in f]
    pairs = [(m, p) for m in S for p in proxies] + [("endorserank", "awp")]
    boot.prefetch(pairs, workers=8)

    per_proxy = {m: {p: {**boot.tau(m, p), "spearman_rho": spearman(S[m], P[p])} for p in proxies} for m in S}
    families = {m: {f: boot.family(m, labels) for f, labels in FAMILIES.items()} for m in S}
    contrasts = []
    for label, a, b, group in CONTRASTS:
        fa = FAMILIES.get(a[1], a[1])
        fb = FAMILIES.get(b[1], b[1])
        r = boot.contrast((a[0], fa), (b[0], fb))
        contrasts.append({"label": label, "a": a, "b": b, "group": group, **(r or {})})

    # Secondary part of rule A: C-PR(0.5) point estimate inside the CI of the better layer on
    # transfer and allowance, and above both layers on Sybil stability.
    rule = {}
    for fam in ("transfer", "allowance"):
        best = max(("cpr_l100", "cpr_l0"), key=lambda m: families[m][fam]["mean_tau"])
        ci = families[best][fam]
        rule[fam] = {"best_layer": best, "best_ci": [ci["ci_low"], ci["ci_high"]],
                     "cpr": families["cpr_l50"][fam]["mean_tau"],
                     "pass": ci["ci_low"] <= families["cpr_l50"][fam]["mean_tau"] <= ci["ci_high"]}
    syb = {m: families[m]["sybil_stability"]["mean_tau"] for m in ("cpr_l50", "cpr_l100", "cpr_l0")}
    rule["sybil_stability"] = {**syb, "pass": syb["cpr_l50"] > max(syb["cpr_l100"], syb["cpr_l0"])}
    rule["pass"] = all(rule[k]["pass"] for k in ("transfer", "allowance", "sybil_stability"))

    # Isolated-node rule for EndorseRank and AWP.
    iso, _ = score_all(g, params, methods=("endorserank", "awp"), isolated=ids)
    Si = pd.DataFrame({m: scores_on(ids, s).to_numpy() for m, s in iso.items()}, index=ids)
    boot.add("endorserank_iso", Si["endorserank"])
    boot.add("awp_iso", Si["awp"])
    boot.prefetch([(m, p) for m in ("endorserank_iso", "awp_iso") for p in proxies] + [("endorserank_iso", "awp_iso")], workers=8)
    isolated = {m: {f: boot.family(m, labels) for f, labels in FAMILIES.items()} for m in ("endorserank_iso", "awp_iso")}

    # Damping sweep for EndorseRank and AWP.
    damping = {}
    for d in cfg["robustness"]["damping_values"]:
        sc, it = score_all(g, {**params, "damping": d}, methods=("endorserank", "awp"))
        for m, s in sc.items():
            name = f"{m}_d{int(round(d * 100))}"
            boot.add(name, scores_on(ids, s).to_numpy())
            boot.prefetch([(name, p) for p in proxies], workers=8)
            damping[name] = {"damping": d, "iterations": it[m],
                             **{f: boot.family(name, labels) for f, labels in FAMILIES.items()}}

    in_graph_allow = np.isin(ids, np.union1d(g.allow["src"], g.allow["dst"]))
    in_graph_transfer = np.isin(ids, np.union1d(g.transfer["src"], g.transfer["dst"]))
    summary = {
        "anchor": cfg["period"]["observation_end"],
        "cohort": int(len(ids)),
        "graph": {
            "allowance": {"edges": int((g.allow["w_er"] > 0).sum()),
                          "nodes": int(len(np.union1d(g.allow["src"], g.allow["dst"])))},
            "transfer": {"edges": int((g.transfer["w_awp"] > 0).sum()),
                         "nodes": int(len(np.union1d(g.transfer["src"], g.transfer["dst"])))},
            "cohort_outside_allowance": int((~in_graph_allow).sum()),
            "cohort_outside_transfer": int((~in_graph_transfer).sum()),
            "cohort_outside_both": int((~in_graph_allow & ~in_graph_transfer).sum()),
        },
        "iterations": iters,
        "per_proxy": per_proxy,
        "families": families,
        "contrasts": contrasts,
        "rule_a_secondary": rule,
        "inter_method": {"endorserank_vs_awp": boot.tau("endorserank", "awp"),
                         "isolated": boot.tau("endorserank_iso", "awp_iso"),
                         "concordance": concordance(S["endorserank"].to_numpy(), S["awp"].to_numpy())},
        "ties": {m: tie_profile(S[m].to_numpy()) for m in S},
        "isolated_rule": isolated,
        "damping": damping,
        "closed_form": closed_form(g.allow, full["endorserank"], ids, params["damping"]),
        "methods": METHOD_LABELS,
    }
    save_json(summary, OUT / "eval_summary.json")
    write_parts(pd.concat([S, P], axis=1).reset_index().rename(columns={"index": "id"}), OUT / "cohort_scores")
    print("written", OUT / "eval_summary.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
