#!/usr/bin/env python3
"""Robustness and sensitivity checks for EndorseRank and AWP at T_obs.

1. Top-token subgraphs: both graphs rebuilt from twenty tokens (by summed raw amount
   and by rows, sql/11_top_tokens.sql); family means on the matched cohort.
2. Sample definition: the deterministic SHA256 stages of the runtime scaling
   (subsamples of the matched cohort; each stage keeps the edges incident to its
   contracts); family means on the stage's contracts. The stages differ in size and
   composition, so their coefficients are not comparable with the main table.
Writes data/2-.../robustness/robustness.json.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import PROC, RAW, load_config, read_parts, save_json  # noqa: E402
from graphs import load_graphs, load_nodes, restrict  # noqa: E402
from run_benchmark import sha_order  # noqa: E402
from run_same_window import FAMILIES  # noqa: E402
from scoring import activeness, pagerank_params, scores_on, weighted_pagerank  # noqa: E402
from stats import kendall_tau_b  # noqa: E402

OUT = PROC / "robustness"


def er_awp(allow: pd.DataFrame, transfer: pd.DataFrame, params: dict, w_a="w_er", w_t="w_awp"):
    er, _ = weighted_pagerank(allow["src"], allow["dst"], allow[w_a], **params)
    act = activeness(transfer["src"], transfer["dst"], transfer["max_sig"])
    awp, _ = weighted_pagerank(transfer["src"], transfer["dst"], transfer[w_t], teleport=act, **params)
    return er, awp


def family_means(score: np.ndarray, P: pd.DataFrame) -> dict:
    out = {}
    for f, cols in FAMILIES.items():
        taus = [kendall_tau_b(score, P[c].to_numpy()) for c in cols]
        taus = [t for t in taus if t is not None]
        out[f] = float(np.mean(taus)) if taus else None
    return out


def main() -> int:
    cfg = load_config()
    params = pagerank_params(cfg)
    nodes = load_nodes()
    cohort = nodes.loc[nodes["is_cohort"], ["id", "address"]].sort_values("id").reset_index(drop=True)
    ids = cohort["id"].to_numpy(np.int64)
    P = read_parts(PROC / "same-window" / "cohort_scores").set_index("id").loc[ids]

    tok = read_parts(RAW / "graph-tables" / "top_token_pairs")
    tokens = {}
    for lst in ("by_amount", "by_rows"):
        a = tok[(tok["list"] == lst) & (tok["layer"] == "allowance")].rename(columns={"w": "w_er"})
        t = tok[(tok["list"] == lst) & (tok["layer"] == "transfer")].rename(columns={"w": "w_awp"})
        er, awp = er_awp(a, t, params)
        tokens[lst] = {"endorserank": family_means(scores_on(ids, er).to_numpy(), P),
                       "awp": family_means(scores_on(ids, awp).to_numpy(), P),
                       "allowance_edges": int(len(a)), "transfer_edges": int(len(t))}
        print(lst, tokens[lst], flush=True)
    tokens["all"] = {"endorserank": family_means(P["endorserank"].to_numpy(), P),
                     "awp": family_means(P["awp"].to_numpy(), P)}
    toklist = pd.read_csv(RAW / "graph-tables" / "top_tokens.csv")
    tokens["shared_tokens"] = int((toklist["by_amount"] & toklist["by_rows"]).sum())

    g = load_graphs("tobs")
    order = sha_order(cohort["address"], cfg["benchmark"]["scaling_seed"])
    stages = []
    for n in [s for s in (1000, 2000, 5000, 10000, 20000) if s < len(ids)] + [len(ids)]:
        sid = np.sort(ids[order[:n]])
        sub = restrict(g, sid)
        er, awp = er_awp(sub.allow, sub.transfer, params)
        Ps = P.loc[sid]
        stages.append({"n": n, "endorserank": family_means(scores_on(sid, er).to_numpy(), Ps),
                       "awp": family_means(scores_on(sid, awp).to_numpy(), Ps),
                       "allowance_edges": int(len(sub.allow)), "transfer_edges": int(len(sub.transfer))})
        print("stage", n, stages[-1], flush=True)
    save_json({"top_tokens": tokens, "sample_definition": stages}, OUT / "robustness.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
