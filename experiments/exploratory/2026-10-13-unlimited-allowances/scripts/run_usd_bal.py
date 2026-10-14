"""Exploratory: EndorseRank on raw USD amounts, an unlimited allowance counted at the owner's
balance of the token at the anchor. Same cohorts, labels and bootstrap as the published runs.

Allowance weights per (owner, spender), summed over tokens, sigma = time weight:
  endorserank   sigma * V(usd)                          (published)
  er_usd_bal    sigma * x,  x = balance if unlimited else allowance usd   (requested)
  er_usd_min    sigma * min(allowance usd, balance)
  er_usd_cap    sigma * min(allowance usd, 20,000)
  er_v_bal      sigma * V(x)       (bounded transform kept, unlimited -> balance)
  er_v_min      sigma * V(min(allowance usd, balance))
*_act: the same weights with AWP's activity restarts.
Transfer side: awp (sigma * V(usd)), awp_usd (sigma * usd), both with activity restarts.
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
RAW = EXP / "data" / "1-raw-blockchain-extracts" / "exploratory-2026-10-13"  # BigQuery downloads
XPROC = EXP / "data" / "2-processed-tables-and-evaluations" / "exploratory-2026-10-13"  # score tables
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
ALLOW = {"endorserank": "w_er", "er_usd_bal": "w_usd_bal", "er_usd_min": "w_usd_min", "er_usd_cap": "w_usd_cap",
         "er_v_bal": "w_er_bal", "er_v_min": "w_er_min"}
ACT = ("endorserank", "er_usd_bal", "er_v_bal")


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def allow_table(g, tag):
    x = read_parts(RAW / f"x_usd_pairs_{tag}")
    a = g.allow.merge(x, on=["src", "dst"], how="inner", validate="one_to_one")
    assert len(a) == len(g.allow) == len(x)
    info = {
        "check_max_rel_diff_w_er": float((np.abs(a["w_er_chk"] - a["w_er"]) / a["w_er"].clip(lower=1e-300)).max()),
        "pairs": int(len(a)),
        "pairs_zero_usd_bal": int((a["w_usd_bal"] <= 0).sum()),
        "pairs_zero_usd_min": int((a["w_usd_min"] <= 0).sum()),
        "allowances": int(a["n"].sum()), "unlimited": int(a["n_unl"].sum()),
        "unlimited_zero_balance": int(a["n_unl_zero"].sum()), "allowances_zero_balance": int(a["n_zero_bal"].sum()),
    }
    return a, info


def frame(g, a, ids, p):
    S = pd.DataFrame(index=ids)
    act = activeness(a["src"], a["dst"], a["max_sig"])
    for m, w in ALLOW.items():
        s, _ = weighted_pagerank(a["src"], a["dst"], a[w], **p)
        S[m] = scores_on(ids, s).to_numpy()
        if m in ACT:
            s, _ = weighted_pagerank(a["src"], a["dst"], a[w], teleport=act, **p)
            S[m + "_act"] = scores_on(ids, s).to_numpy()
        log("scored", m)
    deg = raw_degrees(g, ids)
    S["deg"] = deg["in_approve_degree"].to_numpy()
    S["deg_bal"] = pd.Series(a.loc[a["w_usd_bal"] > 0].groupby("dst").size()).reindex(ids).fillna(0).to_numpy()
    t = g.transfer
    tact = activeness(t["src"], t["dst"], t["max_sig"])
    for m, w in (("awp", "w_awp"), ("awp_usd", "w_raw")):
        s, _ = weighted_pagerank(t["src"], t["dst"], t[w], teleport=tact, **p)
        S[m] = scores_on(ids, s).to_numpy()
    S["tdeg"] = deg["in_degree_other"].to_numpy()
    return S


def bootstrap(S, L, labels, cfg):
    b = PairedBootstrap(len(S), cfg["alignment"]["bootstrap_resamples"], cfg["alignment"]["bootstrap_seed"])
    for c in S:
        b.add(c, S[c])
    for c in labels:
        b.add(c, L[c])
    b.prefetch([(m, l) for m in S for l in labels], workers=8)
    return b


def contrasts(b, labels, cols):
    out = {}
    for m in [c for c in cols if c.startswith("er_")]:
        base = "endorserank_act" if m.endswith("_act") else "endorserank"
        for l in labels:
            out[f"{m} - {base} | {l}"] = b.contrast((m, l), (base, l))
            out[f"{m} - deg | {l}"] = b.contrast((m, l), ("deg", l))
    for l in labels:
        out[f"endorserank - deg | {l}"] = b.contrast(("endorserank", l), ("deg", l))
        out[f"er_usd_bal - deg_bal | {l}"] = b.contrast(("er_usd_bal", l), ("deg_bal", l))
        out[f"er_usd_bal - awp_usd | {l}"] = b.contrast(("er_usd_bal", l), ("awp_usd", l))
        out[f"endorserank - awp | {l}"] = b.contrast(("endorserank", l), ("awp", l))
        out[f"awp_usd - awp | {l}"] = b.contrast(("awp_usd", l), ("awp", l))
    return out


def main():
    cfg = load_config()
    p = pagerank_params(cfg)
    nodes = load_nodes()
    addr = nodes.set_index("address")["id"]
    kinds = account_types()
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
                  "zeros": {m: int((S[m] == 0).sum()) for m in S},
                  "taus": {m: {l: b.tau(m, l) for l in LABELS} for m in S},
                  "contrasts": contrasts(b, LABELS, list(S.columns))}
        pd.concat([S, lab], axis=1).to_parquet(XPROC / f"usd_bal_{w}.parquet")
        (HERE / "results_usd_bal.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
        log(w, "done")

    cohort = nodes.loc[nodes["is_cohort"], ["id", "address"]].sort_values("id")
    ids = cohort["id"].to_numpy(np.int64)
    g = load_graphs("tobs")
    a, _ = allow_table(g, "tobs")
    S = pd.DataFrame(index=ids)
    for m, w in ALLOW.items():
        s, _ = weighted_pagerank(a["src"], a["dst"], a[w], **p)
        S[m] = scores_on(ids, s).to_numpy()
    t = g.transfer
    tact = activeness(t["src"], t["dst"], t["max_sig"])
    for m, w in (("awp", "w_awp"), ("awp_usd", "w_raw")):
        s, _ = weighted_pagerank(t["src"], t["dst"], t[w], teleport=tact, **p)
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
    sw["contrasts"] = {f"{m} - endorserank | {f}": b.contrast((m, ls), ("endorserank", ls))
                       for m in ALLOW if m != "endorserank" for f, ls in fams.items()}
    sw["zeros"] = {m: int((S[m] == 0).sum()) for m in S}
    res["same_window"] = sw
    (HERE / "results_usd_bal.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    log("all done")


if __name__ == "__main__":
    main()
