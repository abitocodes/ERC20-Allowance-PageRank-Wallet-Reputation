"""Exploratory (2026-10-14): endorsement-count variants of EndorseRank with the published cohorts,
labels and paired bootstrap (B = 400, seed from the configuration).

On the depth-one allowance graph EndorseRank is close to c (1 + d sum_u w(u,v) / out(u)): every owner
casts one vote and splits it over its spenders. The variants keep the per-owner sum and change the
vote. Every variant counts each owner once per spender, summed over owners:

  v1_sigV        sum_u w_er(u,v)                         sigma(age) V(usd) summed over tokens, no split
  v2_sig         sum_u sigma(a_uv)                       a_uv = age of u's youngest latest approval to v,
                                                         sigma with k = 0.01, t0 = 180 days (as published)
  v3_hl30        sum_u 0.5 ** (a_uv / 30)                half-life of 30 days
  v2_sig_cap10   sum_u sigma(a_uv) min(1, 10 / n_u)      n_u = number of spenders u approved, so no owner
  v3_hl30_cap10  sum_u 0.5 ** (a_uv / 30) min(1, 10/n_u)   adds more than 10 in all

Comparators: endorserank and endorserank_act (published PageRank scores), deg (in-approve degree),
awp, tdeg (transfer in-degree without self-transfers) and mom30, the number of owners whose latest
approval to the spender is at most 30 days old at the anchor. Partial tau given mom30 measures what a
score adds beyond that momentum.
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
RAW = EXP / "data" / "1-raw-blockchain-extracts" / "exploratory-2026-10-14"  # x_nodecay_pairs (pair ages)
XPROC = EXP / "data" / "2-processed-tables-and-evaluations" / "exploratory-2026-10-14"  # score tables
sys.path.insert(0, str(EXP / "scripts"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from common import GRAPH, load_config, read_parts  # noqa: E402
from graphs import load_graphs, load_nodes, raw_degrees  # noqa: E402
from labels import account_types  # noqa: E402
from scoring import activeness, pagerank_params, scores_on, weighted_pagerank  # noqa: E402
from stats import PairedBootstrap, percentile_ci  # noqa: E402

APPR, SEND, REV, DRAIN = "future_new_approvers", "future_new_transfer_senders", "future_revoke_count", "future_drain_owners"
LABELS = [APPR, SEND, REV, DRAIN]
VARIANTS = ["v1_sigV", "v2_sig", "v3_hl30", "v2_sig_cap10", "v3_hl30_cap10"]
BASES = ["endorserank", "endorserank_act", "deg", "mom30"]
DECOMP = [  # one change at a time
    ("no split (v1_sigV) minus EndorseRank", "v1_sigV", "endorserank"),
    ("drop V (v2_sig) minus v1_sigV", "v2_sig", "v1_sigV"),
    ("30-day half-life (v3_hl30) minus v2_sig", "v3_hl30", "v2_sig"),
    ("cap 10 (v2_sig_cap10) minus v2_sig", "v2_sig_cap10", "v2_sig"),
    ("cap 10 (v3_hl30_cap10) minus v3_hl30", "v3_hl30_cap10", "v3_hl30"),
]


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def allow_table(g, tag):
    x = read_parts(RAW / f"x_nodecay_pairs_{tag}", columns=["src", "dst", "min_age_days"])
    a = g.allow.merge(x, on=["src", "dst"], how="inner", validate="one_to_one")
    assert len(a) == len(g.allow) == len(x)
    age = a["min_age_days"].to_numpy()
    sig = 1.0 / (1.0 + np.exp(0.01 * (age - 180.0)))
    # max_sig of the published pair table is sigma of the youngest approval age
    check = float(np.max(np.abs(sig - a["max_sig"].to_numpy())))
    n_u = a.groupby("src")["dst"].transform("size").to_numpy()
    cap = np.minimum(1.0, 10.0 / n_u)
    hl = 0.5 ** (age / 30.0)
    a = a.assign(e_v1=a["w_er"].to_numpy(), e_v2=sig, e_v3=hl, e_v2c=sig * cap, e_v3c=hl * cap,
                 e_mom=(age <= 30.0).astype(float))
    info = {"pairs": int(len(a)), "check_max_abs_diff_sigma_vs_max_sig": check,
            "owners": int(a["src"].nunique()), "owners_over_10_spenders": int((a.groupby("src").size() > 10).sum()),
            "pairs_capped": int((n_u > 10).sum()), "pairs_at_most_30_days": int((age <= 30).sum())}
    return a, info


def counts(a, ids):
    cols = {"v1_sigV": "e_v1", "v2_sig": "e_v2", "v3_hl30": "e_v3", "v2_sig_cap10": "e_v2c",
            "v3_hl30_cap10": "e_v3c", "mom30": "e_mom"}
    sums = a.groupby("dst")[list(cols.values())].sum()
    return {name: sums[c].reindex(ids).fillna(0.0).to_numpy() for name, c in cols.items()}


def frame(g, a, ids, p):
    S = pd.DataFrame(index=ids)
    er, _ = weighted_pagerank(a["src"], a["dst"], a["w_er"], **p)
    S["endorserank"] = scores_on(ids, er).to_numpy()
    era, _ = weighted_pagerank(a["src"], a["dst"], a["w_er"], teleport=activeness(a["src"], a["dst"], a["max_sig"]), **p)
    S["endorserank_act"] = scores_on(ids, era).to_numpy()
    for k, v in counts(a, ids).items():
        S[k] = v
    deg = raw_degrees(g, ids)
    S["deg"] = deg["in_approve_degree"].to_numpy()
    S["tdeg"] = deg["in_degree_other"].to_numpy()
    t = g.transfer
    awp, _ = weighted_pagerank(t["src"], t["dst"], t["w_awp"], teleport=activeness(t["src"], t["dst"], t["max_sig"]), **p)
    S["awp"] = scores_on(ids, awp).to_numpy()
    return S


def partial_tau(b, x, y, z):
    """Partial Kendall tau of x and y given z: point, bootstrap samples (None if any resample was skipped)."""
    px, pz, pyz = b.point(x, y), b.point(x, z), b.point(y, z)
    point = (px - pz * pyz) / np.sqrt((1 - pz ** 2) * (1 - pyz ** 2))
    sxy, sxz, syz = b.samples(x, y), b.samples(x, z), b.samples(y, z)
    if not (sxy.size == sxz.size == syz.size == b.n_boot):
        return float(point), None
    return float(point), (sxy - sxz * syz) / np.sqrt((1 - sxz ** 2) * (1 - syz ** 2))


def summarize(point, s, ci=0.95):
    if s is None:
        return {"point": point, "ci_low": None, "ci_high": None}
    lo, hi = percentile_ci(s, ci)
    return {"point": point, "ci_low": lo, "ci_high": hi, "share_positive": float(np.mean(s > 0)), "n_boot": int(s.size)}


def evaluate(S, L, cfg):
    b = PairedBootstrap(len(S), cfg["alignment"]["bootstrap_resamples"], cfg["alignment"]["bootstrap_seed"])
    for c in S:
        b.add(c, S[c])
    for c in LABELS:
        b.add(c, L[c])
    pairs = [(m, l) for m in S for l in LABELS] + [(m, "mom30") for m in S if m != "mom30"] + [(l, "mom30") for l in LABELS]
    b.prefetch(pairs, workers=8)
    taus = {m: {l: b.tau(m, l) for l in LABELS} for m in S}
    con = {}
    for v in VARIANTS:
        for base in BASES:
            for l in LABELS:
                con[f"{v} - {base} | {l}"] = b.contrast((v, l), (base, l))
    for label, x, y in DECOMP:
        for l in LABELS:
            con[f"[{label}] | {l}"] = b.contrast((x, l), (y, l))
    part, pcon = {}, {}
    for l in (APPR, SEND, REV, DRAIN):
        cache = {}
        for m in S:
            if m == "mom30":
                continue
            pt, s = partial_tau(b, m, l, "mom30")
            cache[m] = (pt, s)
            part[f"{m} | {l}"] = summarize(pt, s)
        for v in VARIANTS + ["endorserank_act"]:
            for base in ("endorserank", "deg"):
                (pa, sa), (pb, sb) = cache[v], cache[base]
                d = None if sa is None or sb is None else sa - sb
                pcon[f"{v} - {base} | {l}"] = summarize(pa - pb, d)
    return taus, con, part, pcon


def ties(x):
    vals, cnt = np.unique(x, return_counts=True)
    return {"distinct": int(len(vals)), "zeros": int((x == 0).sum()), "largest_block": int(cnt.max())}


def main():
    cfg = load_config()
    p = pagerank_params(cfg)
    nodes = load_nodes()
    addr = nodes.set_index("address")["id"]
    kinds = account_types()
    XPROC.mkdir(parents=True, exist_ok=True)
    res = {"definitions": __doc__}
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
        log(w, "scored")
        taus, con, part, pcon = evaluate(S, lab, cfg)
        res[w] = {"graph": info, "spenders": int(len(ids)), "ties": {m: ties(S[m].to_numpy()) for m in S},
                  "taus": taus, "contrasts": con, "partial_tau_given_mom30": part, "partial_contrasts": pcon}
        pd.concat([S, lab], axis=1).to_parquet(XPROC / f"count_variants_{w}.parquet")
        (HERE / "results_count_variants.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
        log(w, "done")

    cohort = nodes.loc[nodes["is_cohort"], ["id", "address"]].sort_values("id")
    ids = cohort["id"].to_numpy(np.int64)
    g = load_graphs("tobs")
    a, _ = allow_table(g, "tobs")
    S = pd.DataFrame(index=ids)
    er, _ = weighted_pagerank(a["src"], a["dst"], a["w_er"], **p)
    S["endorserank"] = scores_on(ids, er).to_numpy()
    for k, v in counts(a, ids).items():
        if k != "mom30":
            S[k] = v
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
    b = PairedBootstrap(len(ids), cfg["alignment"]["bootstrap_resamples"], cfg["alignment"]["bootstrap_seed"])
    for c in S:
        b.add(c, S[c])
    for c in P:
        b.add(c, P[c])
    b.prefetch([(m, l) for m in S for l in P], workers=8)
    sw = {m: {f: b.family(m, ls) for f, ls in fams.items()} for m in S}
    sw["contrasts"] = {f"{m} - endorserank | {f}": b.contrast((m, ls), ("endorserank", ls))
                       for m in VARIANTS for f, ls in fams.items()}
    res["same_window"] = sw
    (HERE / "results_count_variants.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    log("all done")


if __name__ == "__main__":
    main()
