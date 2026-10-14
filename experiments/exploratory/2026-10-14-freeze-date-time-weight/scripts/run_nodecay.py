"""Exploratory (2026-10-14): EndorseRank with every allowance in force at the anchor counted as of
the anchor, i.e. without the time weight of its approval date. Same cohorts, labels and bootstrap
as the published runs.

  endorserank       sigma(age) * V(usd)                     (published)
  er_nd             V(usd); sigma(0) is common to all allowances and cancels in the row normalisation
  endorserank_act   published weights, AWP's activity restarts (sum of the largest sigma per spender)
  er_nd_act         V(usd), activity restarts without decay (an owner's number of spenders)
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

os.environ["CONTRACT_REP_VARIANT"] = "usd"
EXP = Path(__file__).resolve().parents[3]  # experiments/
HERE = Path(__file__).resolve().parents[1]  # result summaries (JSON)
RAW = EXP / "data" / "1-raw-blockchain-extracts" / "exploratory-2026-10-14"  # BigQuery downloads
XPROC = EXP / "data" / "2-processed-tables-and-evaluations" / "exploratory-2026-10-14"  # score tables
sys.path.insert(0, str(EXP / "scripts"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from common import GRAPH, load_config, read_parts  # noqa: E402
from graphs import load_graphs, load_nodes, raw_degrees  # noqa: E402
from labels import account_types  # noqa: E402
from scoring import activeness, pagerank_params, scores_on, weighted_pagerank  # noqa: E402
from stats import PairedBootstrap  # noqa: E402

APPR, SEND, REV, DRAIN = "future_new_approvers", "future_new_transfer_senders", "future_revoke_count", "future_drain_owners"
LABELS = [APPR, SEND, REV, DRAIN]


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def allow_table(g, tag):
    x = read_parts(RAW / f"x_nodecay_pairs_{tag}")
    a = g.allow.merge(x[["src", "dst", "w_er_nd", "w_er_chk", "min_age_days", "max_age_days"]],
                      on=["src", "dst"], how="inner", validate="one_to_one")
    assert len(a) == len(g.allow) == len(x)
    age = a["min_age_days"]
    info = {
        "check_max_rel_diff_w_er": float((np.abs(a["w_er_chk"] - a["w_er"]) / a["w_er"].clip(lower=1e-300)).max()),
        "pairs": int(len(a)),
        "pair_age_days_quantiles": [float(q) for q in np.quantile(age, [0.1, 0.25, 0.5, 0.75, 0.9])],
        "share_pairs_older_180d": float((age > 180).mean()),
        "share_pairs_older_365d": float((age > 365).mean()),
        "share_pairs_older_730d": float((age > 730).mean()),
        # sigma(0) * V summed over all pairs against the published weights: the share the decay keeps
        "share_weight_kept_by_decay": float(a["w_er"].sum() / (a["w_er_nd"].sum() / (1.0 + np.exp(-1.8)))),
    }
    return a, info


def frame(g, a, ids, p):
    S = pd.DataFrame(index=ids)
    act = activeness(a["src"], a["dst"], a["max_sig"])
    act_nd = activeness(a["src"], a["dst"], np.ones(len(a)))
    for m, w, tel in (("endorserank", "w_er", None), ("er_nd", "w_er_nd", None),
                      ("endorserank_act", "w_er", act), ("er_nd_act", "w_er_nd", act_nd)):
        s, _ = weighted_pagerank(a["src"], a["dst"], a[w], teleport=tel, **p)
        S[m] = scores_on(ids, s).to_numpy()
        log("scored", m)
    deg = raw_degrees(g, ids)
    S["deg"] = deg["in_approve_degree"].to_numpy()
    t = g.transfer
    s, _ = weighted_pagerank(t["src"], t["dst"], t["w_awp"], teleport=activeness(t["src"], t["dst"], t["max_sig"]), **p)
    S["awp"] = scores_on(ids, s).to_numpy()
    return S


def bootstrap(S, L, labels, cfg):
    b = PairedBootstrap(len(S), cfg["alignment"]["bootstrap_resamples"], cfg["alignment"]["bootstrap_seed"])
    for c in S:
        b.add(c, S[c])
    for c in labels:
        b.add(c, L[c])
    b.prefetch([(m, l) for m in S for l in labels], workers=8)
    return b


def contrasts(b, labels):
    out = {}
    for l in labels:
        out[f"er_nd - endorserank | {l}"] = b.contrast(("er_nd", l), ("endorserank", l))
        out[f"er_nd_act - endorserank_act | {l}"] = b.contrast(("er_nd_act", l), ("endorserank_act", l))
        out[f"er_nd - deg | {l}"] = b.contrast(("er_nd", l), ("deg", l))
        out[f"er_nd_act - deg | {l}"] = b.contrast(("er_nd_act", l), ("deg", l))
        out[f"endorserank - deg | {l}"] = b.contrast(("endorserank", l), ("deg", l))
        out[f"endorserank_act - deg | {l}"] = b.contrast(("endorserank_act", l), ("deg", l))
    return out


def main():
    cfg = load_config()
    p = pagerank_params(cfg)
    nodes = load_nodes()
    addr = nodes.set_index("address")["id"]
    kinds = account_types()
    XPROC.mkdir(parents=True, exist_ok=True)
    res = {}
    for w, tag, labname in (("w0", "t1", "labels_w0"), ("w1", "tobs", "labels_w1")):
        g = load_graphs(tag)
        a, info = allow_table(g, tag)
        log(w, info)
        lab = read_parts(GRAPH / labname)
        lab = lab[lab["wallet"].map(kinds) == "contract"].copy()
        lab["id"] = lab["wallet"].map(addr)
        lab = lab.dropna(subset=["id"]).astype({"id": np.int64}).sort_values("id").set_index("id")
        ids = lab.index.to_numpy(np.int64)
        S = frame(g, a, ids, p)
        b = bootstrap(S, lab, LABELS, cfg)
        res[w] = {"graph": info, "spenders": int(len(ids)),
                  "taus": {m: {l: b.tau(m, l) for l in LABELS} for m in S},
                  "contrasts": contrasts(b, LABELS)}
        pd.concat([S, lab], axis=1).to_parquet(XPROC / f"nodecay_{w}.parquet")
        (HERE / "results_nodecay.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
        log(w, "done")

    cohort = nodes.loc[nodes["is_cohort"], ["id", "address"]].sort_values("id")
    ids = cohort["id"].to_numpy(np.int64)
    g = load_graphs("tobs")
    a, _ = allow_table(g, "tobs")
    S = pd.DataFrame(index=ids)
    for m, w in (("endorserank", "w_er"), ("er_nd", "w_er_nd")):
        s, _ = weighted_pagerank(a["src"], a["dst"], a[w], **p)
        S[m] = scores_on(ids, s).to_numpy()
    prox = read_parts(GRAPH / "proxies_tobs").merge(cohort, left_on="wallet", right_on="address").set_index("id").reindex(ids)
    deg = raw_degrees(g, ids)
    P = pd.DataFrame(index=ids)
    P["in_degree"] = prox["in_degree"].astype(float)
    P["in_value"] = prox["in_value"].astype(float)
    P["in_approve_degree"] = deg["in_approve_degree"]
    P["in_approve_value"] = deg["in_approve_value"]
    for c in ("inbound_counterparty_ratio", "transfer_tenure_days", "active_months"):
        P[c] = prox[c].astype(float)
    fams = {"transfer": ["in_degree", "in_value"], "allowance": ["in_approve_degree", "in_approve_value"],
            "sybil_stability": ["inbound_counterparty_ratio", "transfer_tenure_days", "active_months"]}
    b = bootstrap(S, P, list(P.columns), cfg)
    sw = {m: {f: b.family(m, ls) for f, ls in fams.items()} for m in S}
    sw["contrasts"] = {f"er_nd - endorserank | {f}": b.contrast(("er_nd", ls), ("endorserank", ls)) for f, ls in fams.items()}
    res["same_window"] = sw
    (HERE / "results_nodecay.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    log("all done")


if __name__ == "__main__":
    main()
