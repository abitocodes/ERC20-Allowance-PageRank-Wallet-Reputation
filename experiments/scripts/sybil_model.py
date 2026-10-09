#!/usr/bin/env python3
"""Quantities of the Sybil cost model (Chapter 5) on the EndorseRank graph at T_obs.

- r_D, the stationary mass of the dangling nodes, at each damping value, and the factor
  (1 - d + d r_D) / (1 - d) by which a closed farm exceeds its population share;
- a direct check: a ring of 20 new addresses, each approving the next, added to the graph;
- a star of m = 10 new addresses that each approve a new target t, which approves each of
  them back; its score against the highest EndorseRank in the matched cohort and the
  closed form r_t = b (1 + d m) / (1 - d^2) with b the common score of nodes without in-edges;
- the share of an owner's row that one fresh approval takes, sigma(0) / (o(h) + sigma(0)),
  at the median owner.
Writes data/2-.../sybil-model/sybil_model.json.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import PROC, load_config, save_json  # noqa: E402
from graphs import load_graphs, load_nodes  # noqa: E402
from scoring import logistic_decay, pagerank_params, scores_on, weighted_pagerank  # noqa: E402

OUT = PROC / "sybil-model"


def solve(src, dst, w, params):
    s, it = weighted_pagerank(src, dst, w, **params)
    out = pd.Series(w, dtype=float).groupby(np.asarray(src)).sum()
    dangling = ~s.index.isin(out[out > 0].index)
    return s, float(s[dangling].sum()), it


def main() -> int:
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
    s_ring, _, _ = weighted_pagerank(rs, rd, rw, **params)
    ring_share = float(s_ring.loc[ring].sum()) / (20 / len(s_ring))

    m = 10
    t = new_id + 100
    farm = np.arange(new_id + 101, new_id + 101 + m)
    ss = np.r_[src, farm, np.full(m, t)]
    sd = np.r_[dst, np.full(m, t), farm]
    sw = np.r_[w, np.full(2 * m, sig0)]
    s_star, _, _ = weighted_pagerank(ss, sd, sw, **params)
    top_cohort = float(scores_on(cohort, base).max())
    star = {
        "m": m, "target_score": float(s_star.loc[t]), "closed_form": b_common * (1 + d * m) / (1 - d ** 2),
        "highest_cohort_endorserank": top_cohort, "ratio_to_highest": float(s_star.loc[t]) / top_cohort,
        "approvals_per_window": 2 * m,
    }
    out_strength = pd.Series(w).groupby(src).sum()
    owners = out_strength.index
    share = sig0 / (out_strength + sig0)
    save_json({
        "graph": {"nodes": n_v, "edges": int(len(a))},
        "sigma0": sig0, "b_common": b_common, "r_D": r_d, "damping": damping,
        "ring20_collects_times_share": ring_share, "star": star,
        "fresh_approval_share_median_owner": float(np.median(share.to_numpy())),
        "owners": int(len(owners)),
    }, OUT / "sybil_model.json")
    print(damping, ring_share, star)
    return 0


if __name__ == "__main__":
    sys.exit(main())
