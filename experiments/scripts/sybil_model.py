#!/usr/bin/env python3
"""Quantities of the Sybil cost model (Chapter 5) on the EndorseRank graph at T_obs.

- r_D, the stationary mass of the dangling nodes, at each damping value, and the factor
  (1 - d + d r_D) / (1 - d) by which a closed farm exceeds its population share;
- a direct check: a ring of 20 new addresses, each approving the next, added to the graph;
- a star of m = 10 new addresses that each approve a new target t, which approves each of
  them back; its score against the highest EndorseRank in the matched cohort and the
  closed form r_t = b (1 + d m) / (1 - d^2) with b the common score of nodes without in-edges;
- the share of an owner's row that one fresh approval takes, sigma(0) / (o(h) + sigma(0)),
  at the median owner;
- the number of star farm addresses needed to reach the cohort's median, 90th and 99th
  percentile and highest EndorseRank.
Writes data/2-.../sybil-model/sybil_model.json.

The contract-graph variant (CONTRACT_REP_VARIANT=contract12m, docs/revision_contract_graph.md
section 13) computes the same quantities on the EndorseRank graph of contracts at T_obs (the
balance-capped allowance pairs of positive weight), where every new address of a farm is a
contract that must be deployed and whose allowance counts only up to its balance. It adds:
- the deployments each farm needs and the gas constants of a contract creation (protocol
  constants of the EVM fee schedule, in gas; no price is read);
- the value weight V of an allowance backed by a balance of USD 1, 10 and 100;
- a sensitivity to a balance threshold theta of USD 1, 10 and 100: the graph keeps only the
  allowance pairs whose capped value (w_raw, the sum over tokens of min(usd_eff, U)) is at
  least theta, so that each farm contract must hold theta at the freeze; the pairs, owners and
  spenders kept, the agreement of the scores of the cohort with the main ones, the star and the
  farm sizes are reported for each theta.
It computes no criterion and decides no rule; the output says so and records HEAD and the
SHA-256 of the tables it read.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (CONTRACT_GRAPH, GRAPH, PROC, ROOT, USD_CONSTANTS, load_config, load_json, part_sha256,  # noqa: E402
                    save_json, sha256_file)
from graphs import load_graphs, load_nodes  # noqa: E402
from scoring import logistic_decay, pagerank_params, scores_on, value_transform, weighted_pagerank  # noqa: E402
from stats import kendall_tau_b  # noqa: E402

OUT = PROC / "sybil-model"
THETAS = (1.0, 10.0, 100.0)   # balance thresholds in USD (contract-graph variant)
STAR_M = 10
# Gas of a contract creation in the EVM fee schedule (Ethereum Yellow Paper, Appendix G): the intrinsic gas of a
# transaction, the further gas of a contract-creating transaction, a CREATE operation, and each byte of code placed
# into state. Lower bounds of the execution gas of one deployment; the fee for posting the data to L1 is not in them.
EVM_GAS = {"G_transaction": 21_000, "G_txcreate": 32_000, "G_create": 32_000, "G_codedeposit_per_byte": 200}


def solve(src, dst, w, params):
    s, it = weighted_pagerank(src, dst, w, **params)
    out = pd.Series(w, dtype=float).groupby(np.asarray(src)).sum()
    dangling = ~s.index.isin(out[out > 0].index)
    return s, float(s[dangling].sum()), it


def _model(a: pd.DataFrame, cohort: np.ndarray, params: dict, sig0: float, new_id: int, damping_values) -> dict:
    """The quantities of the module docstring on the allowance pairs ``a`` (columns src, dst, w_er; positive
    weights only), with new node ids from ``new_id`` on. ``_base`` holds the score vector of the graph."""
    src, dst, w = a["src"].to_numpy(), a["dst"].to_numpy(), a["w_er"].to_numpy()
    damping = {}
    for d in damping_values:
        _, r_d, _ = solve(src, dst, w, {**params, "damping": d})
        damping[str(d)] = {"r_D": r_d, "farm_factor": (1 - d + d * r_d) / (1 - d)}
    d = params["damping"]
    base, r_d, _ = solve(src, dst, w, params)
    has_in = np.unique(dst)
    no_in = base.index[~base.index.isin(has_in)]
    b_common = float(np.median(base.loc[no_in]))

    ring = np.arange(new_id, new_id + 20)
    rs, rd, rw = np.r_[src, ring], np.r_[dst, np.roll(ring, -1)], np.r_[w, np.full(20, sig0)]
    s_ring, _ = weighted_pagerank(rs, rd, rw, **params)
    ring_share = float(s_ring.loc[ring].sum()) / (20 / len(s_ring))

    m = STAR_M
    t = new_id + 100
    farm = np.arange(new_id + 101, new_id + 101 + m)
    ss = np.r_[src, farm, np.full(m, t)]
    sd = np.r_[dst, np.full(m, t), farm]
    sw = np.r_[w, np.full(2 * m, sig0)]
    s_star, _ = weighted_pagerank(ss, sd, sw, **params)
    cohort_scores = scores_on(cohort, base).to_numpy()
    top_cohort = float(cohort_scores.max()) if cohort_scores.size else 0.0
    star = {
        "m": m, "target_score": float(s_star.loc[t]), "closed_form": b_common * (1 + d * m) / (1 - d ** 2),
        "highest_cohort_endorserank": top_cohort,
        "ratio_to_highest": (float(s_star.loc[t]) / top_cohort) if top_cohort > 0 else None,
        "approvals_per_window": 2 * m,
    }
    reach = {}
    for q in (50, 90, 99, 100):
        target = float(np.percentile(cohort_scores, q)) if cohort_scores.size else 0.0
        m_need = ((target * (1 - d ** 2) / b_common) - 1) / d
        reach[f"p{q}"] = {"score": target, "farm_addresses": max(0.0, m_need)}
    out_strength = pd.Series(w).groupby(src).sum()
    share = sig0 / (out_strength + sig0)
    return {
        "graph": {"nodes": int(len(base)), "edges": int(len(a))},
        "sigma0": sig0, "b_common": b_common, "r_D": r_d, "damping": damping,
        "ring20_collects_times_share": ring_share, "star": star,
        "fresh_approval_share_median_owner": float(np.median(share.to_numpy())),
        "owners": int(len(out_strength)),
        "farm_size_to_reach_cohort_quantile": reach,
        "_base": base,
    }


def main_contract() -> int:
    """The contract-graph variant (module docstring)."""
    cfg = load_config()
    params = pagerank_params(cfg)
    rep = cfg["reputation"]
    consts = load_json(USD_CONSTANTS)
    nodes = load_nodes()
    cohort = nodes.loc[nodes["is_cohort"], "id"].to_numpy(np.int64)
    pairs = load_graphs("tobs").allow
    a = pairs[pairs["w_er"] > 0]
    sig0 = float(logistic_decay(np.array([0.0]), rep["awp_decay_k"], rep["awp_decay_t0_days"])[0])
    new_id = int(nodes["id"].max()) + 1

    main = _model(a, cohort, params, sig0, new_id, cfg["robustness"]["damping_values"])
    base = main.pop("_base")
    main["graph"]["pairs_of_zero_weight_left_out"] = int(len(pairs) - len(a))
    main_cohort = scores_on(cohort, base).to_numpy()
    main["cohort"] = {"n": int(cohort.size), "with_positive_score": int((main_cohort > 0).sum())}

    b_a = float(consts["b_allowance"])
    m = STAR_M
    main["contract_farm"] = {
        "note": "every address of a farm is a contract: it is deployed, and its allowance counts up to its balance "
                "of the token at the freeze",
        "deployments": {"ring20": 20, "star": m + 1,
                        "reach": {q: int(np.ceil(v["farm_addresses"])) + 1
                                  for q, v in main["farm_size_to_reach_cohort_quantile"].items()}},
        "evm_gas": {**EVM_GAS,
                    "creation_by_transaction_at_least": EVM_GAS["G_transaction"] + EVM_GAS["G_txcreate"],
                    "creation_by_create_at_least": EVM_GAS["G_create"],
                    "source": "Ethereum Yellow Paper, Appendix G (fee schedule); execution gas only, without the "
                              "fee for posting data to L1"},
        "value_weight": {"m_allowance_usd": float(consts["m_allowance_usd"]), "b_allowance": b_a,
                         "V_at_usd": {f"{th:g}": float(value_transform(np.array([th]), b_a)[0]) for th in THETAS}},
    }

    thresholds = {}
    for th in THETAS:
        kept = a[a["w_raw"] >= th]
        if kept.empty:
            thresholds[f"{th:g}"] = {"theta_usd": th, "pairs_kept": 0, "share_of_pairs_kept": 0.0 if len(a) else None,
                                     "owners_kept": 0, "spenders_kept": 0, "star_balance_usd": (m + 1) * th}
            continue
        x = _model(kept, cohort, params, sig0, new_id, [params["damping"]])
        s = scores_on(cohort, x.pop("_base")).to_numpy()
        thresholds[f"{th:g}"] = {
            "theta_usd": th,
            "pairs_kept": int(len(kept)), "share_of_pairs_kept": float(len(kept) / len(a)) if len(a) else None,
            "owners_kept": int(kept["src"].nunique()), "spenders_kept": int(kept["dst"].nunique()),
            "cohort_with_positive_score": int((s > 0).sum()),
            "cohort_tau_with_main": kendall_tau_b(main_cohort, s),
            "graph": x["graph"], "b_common": x["b_common"], "r_D": x["r_D"],
            "star": x["star"], "farm_size_to_reach_cohort_quantile": x["farm_size_to_reach_cohort_quantile"],
            "star_balance_usd": (m + 1) * th,
        }
    main["balance_threshold"] = thresholds
    main["note"] = ("quantities of the Sybil cost model on the contract graph; they compute no criterion and decide "
                    "no rule (docs/revision_contract_graph.md section 13)")
    try:
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True,
                              check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        head = None
    main["provenance"] = {"head": head,
                          "inputs": {"allow_pairs_tobs": part_sha256(GRAPH / "allow_pairs_tobs"),
                                     "nodes": part_sha256(GRAPH / "nodes"),
                                     "constants": sha256_file(USD_CONSTANTS)}}
    save_json(main, OUT / "sybil_model.json")
    print(main["damping"], main["ring20_collects_times_share"], main["star"])
    for th, x in thresholds.items():
        print("theta", th, {k: x.get(k) for k in ("pairs_kept", "owners_kept", "spenders_kept", "cohort_tau_with_main")},
              (x.get("star") or {}).get("ratio_to_highest"))
    return 0


def main() -> int:
    if CONTRACT_GRAPH:
        return main_contract()
    cfg = load_config()
    params = pagerank_params(cfg)
    rep = cfg["reputation"]
    nodes = load_nodes()
    cohort = nodes.loc[nodes["is_cohort"], "id"].to_numpy(np.int64)
    a = load_graphs("tobs").allow
    a = a[a["w_er"] > 0]
    src, dst, w = a["src"].to_numpy(), a["dst"].to_numpy(), a["w_er"].to_numpy()
    sig0 = float(logistic_decay(np.array([0.0]), rep["awp_decay_k"], rep["awp_decay_t0_days"])[0])
    new_id = int(nodes["id"].max()) + 1

    damping = {}
    for d in cfg["robustness"]["damping_values"]:
        _, r_d, _ = solve(src, dst, w, {**params, "damping": d})
        damping[str(d)] = {"r_D": r_d, "farm_factor": (1 - d + d * r_d) / (1 - d)}

    d = params["damping"]
    base, r_d, _ = solve(src, dst, w, params)
    n_v = len(base)
    has_in = np.unique(dst)
    no_in = base.index[~base.index.isin(has_in)]
    b_common = float(np.median(base.loc[no_in]))

    ring = np.arange(new_id, new_id + 20)
    rs, rd, rw = np.r_[src, ring], np.r_[dst, np.roll(ring, -1)], np.r_[w, np.full(20, sig0)]
    s_ring, _ = weighted_pagerank(rs, rd, rw, **params)
    ring_share = float(s_ring.loc[ring].sum()) / (20 / len(s_ring))

    m = 10
    t = new_id + 100
    farm = np.arange(new_id + 101, new_id + 101 + m)
    ss = np.r_[src, farm, np.full(m, t)]
    sd = np.r_[dst, np.full(m, t), farm]
    sw = np.r_[w, np.full(2 * m, sig0)]
    s_star, _ = weighted_pagerank(ss, sd, sw, **params)
    top_cohort = float(scores_on(cohort, base).max())
    star = {
        "m": m, "target_score": float(s_star.loc[t]), "closed_form": b_common * (1 + d * m) / (1 - d ** 2),
        "highest_cohort_endorserank": top_cohort, "ratio_to_highest": float(s_star.loc[t]) / top_cohort,
        "approvals_per_window": 2 * m,
    }
    # Farm addresses m a star needs to reach a cohort score quantile, from r_t = b (1 + d m) / (1 - d^2);
    # 0 when a target with m = 0 (two addresses approving each other) already reaches it.
    cohort_scores = scores_on(cohort, base).to_numpy()
    reach = {}
    for q in (50, 90, 99, 100):
        target = float(np.percentile(cohort_scores, q))
        m_need = ((target * (1 - d ** 2) / b_common) - 1) / d
        reach[f"p{q}"] = {"score": target, "farm_addresses": max(0.0, m_need)}
    out_strength = pd.Series(w).groupby(src).sum()
    owners = out_strength.index
    share = sig0 / (out_strength + sig0)
    save_json({
        "graph": {"nodes": n_v, "edges": int(len(a))},
        "sigma0": sig0, "b_common": b_common, "r_D": r_d, "damping": damping,
        "ring20_collects_times_share": ring_share, "star": star,
        "fresh_approval_share_median_owner": float(np.median(share.to_numpy())),
        "owners": int(len(owners)),
        "farm_size_to_reach_cohort_quantile": reach,
    }, OUT / "sybil_model.json")
    print(damping, ring_share, star)
    return 0


if __name__ == "__main__":
    sys.exit(main())
