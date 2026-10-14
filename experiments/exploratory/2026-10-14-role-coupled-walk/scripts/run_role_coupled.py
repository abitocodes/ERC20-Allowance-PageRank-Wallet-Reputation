"""Exploratory (2026-10-14): published C-PR against a role-coupled EndorseRank walk ("option 1"),
with the published cohorts, labels and paired bootstrap (B = 400).

Every score is a PageRank (damping, tolerance and iteration cap of the configuration):
  cpr_l50          published C-PR: allowance layer min(usd, 20,000) summed, transfer layer usd * sigma,
                   lambda = 0.5 at every node, uniform restarts; score = total mass
  cpr_plus         C-PR with the ingredients of the endorsement-count work, lambda = 0.5 at every node:
                   allowance edges sigma(a_uv) min(1, 10 / n_u), transfer edges sigma V(usd) (as AWP),
                   restarts 0.5 x capped endorsement mass + 0.5 x AWP activeness (each normalised);
                   score = total mass
  rc_b{25,50,75}_mass   option 1: a wallet follows its own approvals only; a contract follows its
                   payouts (transfers it sent, AWP weights) with probability beta and its own approvals
                   with 1 - beta; restarts proportional to capped endorsement mass; score = mass
                   received over approval edges
  rc_b{25,50,75}_ctr    the same with restarts uniform over contracts
The primary option-1 score, fixed before the run, is rc_b50_mass; the other five are sensitivity checks.
Contracts: every address the account-type checks found to hold code plus the revised cohort; every other
address is treated as a wallet. Comparators from the earlier runs: endorserank, pr_v2_sig_cap10
(endorsement-mass restarts on the allowance graph alone), deg, awp, mom30.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

os.environ["CONTRACT_REP_VARIANT"] = "usd"
EXP = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parents[1]
RAW = EXP / "data" / "1-raw-blockchain-extracts" / "exploratory-2026-10-14"
XPROC = EXP / "data" / "2-processed-tables-and-evaluations" / "exploratory-2026-10-14"
sys.path.insert(0, str(EXP / "scripts"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from common import GRAPH, load_config, read_parts  # noqa: E402
from graphs import load_graphs, load_nodes, raw_degrees  # noqa: E402
from labels import account_types  # noqa: E402
from scoring import (_local_index, _out_strength, _positive_edges, _power_iterate, _teleport_vector,  # noqa: E402
                     _transposed, activeness, coupled_pagerank, pagerank_params, scores_on, weighted_pagerank)
from stats import PairedBootstrap, percentile_ci  # noqa: E402

APPR, SEND = "future_new_approvers", "future_new_transfer_senders"
LABELS = [APPR, SEND]
BETAS = (0.25, 0.5, 0.75)
OPT1 = [f"rc_b{int(b * 100)}_{r}" for r in ("mass", "ctr") for b in BETAS]
PRIMARY = "rc_b50_mass"


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def coupled_walk(layers, lam, teleport, p):
    """PageRank on a per-node mixture of layers with node-dependent layer weights and given restarts.

    layers: {name: (src, dst, w)}; lam(name, nodes) -> weight of that layer at every node. A node that
    has out-edges in some layers splits its step over them in proportion to lam; a node with none is
    dangling and its mass follows the restarts. Returns the score of every node and, per layer, the
    mass each node receives over that layer's edges.
    """
    act = {k: _positive_edges(*v) for k, v in layers.items()}
    names = list(act)
    nodes, local = _local_index([arr for k in names for arr in act[k][:2]])
    n = nodes.size
    denom = np.zeros(n)
    parts = {}
    for i, k in enumerate(names):
        s = local[2 * i]
        out, inv = _out_strength(s, act[k][2], n)
        has = (out > 0).astype(float)
        lk = lam(k, nodes)
        parts[k] = (inv, has, lk)
        denom += lk * has
    pos = denom > 0
    mats = {}
    for i, k in enumerate(names):
        inv, has, lk = parts[k]
        alpha = np.zeros(n)
        alpha[pos] = lk[pos] * has[pos] / denom[pos]
        s, d = local[2 * i], local[2 * i + 1]
        mats[k] = _transposed(s, d, act[k][2] * inv[s] * alpha[s], n)
    restart = _teleport_vector(nodes, teleport)
    rank, its = _power_iterate(list(mats.values()), ~pos, restart, p["damping"], p["tol"], p["max_iter"])
    inflow = {k: pd.Series(mats[k] @ rank, index=nodes) for k in names}
    return pd.Series(rank, index=nodes), inflow, its


def window_scores(tag, ids_sets, p, is_contract):
    g = load_graphs(tag)
    x = read_parts(RAW / f"x_nodecay_pairs_{tag}", columns=["src", "dst", "min_age_days"])
    a = g.allow.merge(x, on=["src", "dst"], how="inner", validate="one_to_one")
    age = a["min_age_days"].to_numpy()
    n_u = a.groupby("src")["dst"].transform("size").to_numpy()
    a["e"] = (1.0 / (1.0 + np.exp(0.01 * (age - 180.0)))) * np.minimum(1.0, 10.0 / n_u)
    t = g.transfer
    t_mass = a.groupby("src")["e"].sum()
    t_act = activeness(t["src"], t["dst"], t["max_sig"])
    out = {}

    def keep(name, series):
        out[name] = series
        log(tag, name, "done")

    r, _ = coupled_pagerank([(a["src"], a["dst"], a["w_raw"], 0.5), (t["src"], t["dst"], t["w_raw"], 0.5)], **p)
    keep("cpr_l50", r)
    tele = pd.concat([0.5 * t_mass / t_mass.sum(), 0.5 * t_act / t_act.sum()], axis=1).sum(axis=1)
    r, _, _ = coupled_walk({"A": (a["src"], a["dst"], a["e"]), "T": (t["src"], t["dst"], t["w_awp"])},
                           lambda k, nodes: np.full(nodes.size, 0.5), tele, p)
    keep("cpr_plus", r)
    pay = t[(t["src"] != t["dst"]).to_numpy() & is_contract[t["src"].to_numpy()]]
    for b in BETAS:
        def lam(k, nodes, b=b):
            c = is_contract[nodes]
            return np.where(c, 1.0 - b, 1.0) if k == "A" else np.full(nodes.size, b)
        layers = {"A": (a["src"], a["dst"], a["e"]), "P": (pay["src"], pay["dst"], pay["w_awp"])}
        _, inflow, _ = coupled_walk(layers, lam, t_mass, p)
        keep(f"rc_b{int(b * 100)}_mass", inflow["A"])
        nodes_all = np.union1d(np.union1d(a["src"].to_numpy(), a["dst"].to_numpy()), np.union1d(pay["src"].to_numpy(), pay["dst"].to_numpy()))
        ctr = nodes_all[is_contract[nodes_all]]
        _, inflow, _ = coupled_walk(layers, lam, pd.Series(1.0, index=ctr), p)
        keep(f"rc_b{int(b * 100)}_ctr", inflow["A"])
    r, _ = weighted_pagerank(a["src"], a["dst"], a["e"], teleport=t_mass, **p)
    keep("pr_v2_sig_cap10", r)
    r, _ = weighted_pagerank(a["src"], a["dst"], a["w_er"], **p)
    keep("endorserank", r)
    r, _ = weighted_pagerank(t["src"], t["dst"], t["w_awp"], teleport=t_act, **p)
    keep("awp", r)
    info = {"payout_edges": int(len(pay)), "allowance_edges": int(len(a)), "transfer_edges": int(len(t)),
            "contracts_known": int(is_contract.sum())}
    frames = {}
    for name, ids in ids_sets.items():
        S = pd.DataFrame({m: scores_on(ids, s).to_numpy() for m, s in out.items()}, index=ids)
        frames[name] = (S, g)
    return frames, a, info


def partial(b, x, y, z):
    pxy, pxz, pyz = b.point(x, y), b.point(x, z), b.point(y, z)
    pt = (pxy - pxz * pyz) / np.sqrt((1 - pxz ** 2) * (1 - pyz ** 2))
    sxy, sxz, syz = b.samples(x, y), b.samples(x, z), b.samples(y, z)
    s = (sxy - sxz * syz) / np.sqrt((1 - sxz ** 2) * (1 - syz ** 2)) if sxy.size == sxz.size == syz.size == b.n_boot else None
    return float(pt), s


def summ(pt, s):
    if s is None:
        return {"point": pt, "ci_low": None, "ci_high": None}
    lo, hi = percentile_ci(s)
    return {"point": pt, "ci_low": lo, "ci_high": hi, "share_positive": float(np.mean(s > 0))}


def holdout_eval(S, lab, mom, cfg):
    S = S.copy()
    S["mom30"] = mom
    b = PairedBootstrap(len(S), cfg["alignment"]["bootstrap_resamples"], cfg["alignment"]["bootstrap_seed"])
    for c in S:
        b.add(c, S[c])
    for c in LABELS:
        b.add(c, lab[c])
    b.prefetch([(m, l) for m in S for l in LABELS] + [(m, "mom30") for m in S if m != "mom30"] + [(l, "mom30") for l in LABELS], workers=8)
    taus = {m: {l: b.tau(m, l) for l in LABELS} for m in S}
    con = {}
    for m in OPT1:
        for base in ("cpr_l50", "cpr_plus", "endorserank", "pr_v2_sig_cap10", "deg"):
            for l in LABELS:
                con[f"{m} - {base} | {l}"] = b.contrast((m, l), (base, l))
    for l in LABELS:
        con[f"cpr_plus - cpr_l50 | {l}"] = b.contrast(("cpr_plus", l), ("cpr_l50", l))
        con[f"cpr_l50 - endorserank | {l}"] = b.contrast(("cpr_l50", l), ("endorserank", l))
    part, pcon = {}, {}
    for l in LABELS:
        cache = {m: partial(b, m, l, "mom30") for m in ("endorserank", "pr_v2_sig_cap10", "cpr_l50", "cpr_plus", PRIMARY, "deg")}
        for m, (pt, s) in cache.items():
            part[f"{m} | {l}"] = summ(pt, s)
        for base in ("cpr_l50", "endorserank", "pr_v2_sig_cap10"):
            (pa, sa), (pb, sb) = cache[PRIMARY], cache[base]
            pcon[f"{PRIMARY} - {base} | {l}"] = summ(pa - pb, None if sa is None or sb is None else sa - sb)
    return {"taus": taus, "contrasts": con, "partial_tau_given_mom30": part, "partial_contrasts": pcon}


def main():
    cfg = load_config()
    p = pagerank_params(cfg)
    nodes = load_nodes()
    addr = nodes.set_index("address")["id"]
    kinds = account_types()
    is_contract = np.zeros(int(nodes["id"].max()) + 1, dtype=bool)
    cids = addr.reindex(kinds[kinds == "contract"].index).dropna().astype(np.int64).to_numpy()
    is_contract[cids] = True
    is_contract[nodes.loc[nodes["is_cohort"], "id"].to_numpy()] = True
    res = {"definitions": __doc__, "primary": PRIMARY}
    for w, tag in (("w0", "t1"), ("w1", "tobs")):
        prev = pd.read_parquet(XPROC / f"count_variants_{w}.parquet")
        ids = prev.index.to_numpy(np.int64)
        sets = {"spenders": ids}
        if tag == "tobs":
            sets["cohort"] = nodes.loc[nodes["is_cohort"], "id"].sort_values().to_numpy(np.int64)
        frames, a, info = window_scores(tag, sets, p, is_contract)
        S, g = frames["spenders"]
        S["deg"] = prev["deg"].to_numpy()
        res[w] = {"graph": info, "spenders": int(len(ids)), **holdout_eval(S, prev, prev["mom30"].to_numpy(), cfg)}
        S.to_parquet(XPROC / f"role_coupled_{w}.parquet")
        (HERE / "results_role_coupled.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
        log(w, "evaluated")
        if tag == "tobs":
            Sc, g = frames["cohort"]
            cohort = nodes.loc[nodes["is_cohort"], ["id", "address"]].sort_values("id")
            cids2 = cohort["id"].to_numpy(np.int64)
            prox = read_parts(GRAPH / "proxies_tobs").merge(cohort, left_on="wallet", right_on="address").set_index("id").reindex(cids2)
            deg = raw_degrees(g, cids2)
            P = pd.DataFrame(index=cids2)
            P["in_degree"] = prox["in_degree"].astype(float)
            P["in_value"] = prox["in_value"].astype(float)
            P["in_approve_degree"] = deg["in_approve_degree"]
            P["in_approve_value"] = deg["in_approve_value"]
            for c in ("inbound_counterparty_ratio", "transfer_tenure_days", "active_months"):
                P[c] = prox[c].astype(float)
            fams = {"transfer": ["in_degree", "in_value"], "allowance": ["in_approve_degree", "in_approve_value"],
                    "sybil_stability": ["inbound_counterparty_ratio", "transfer_tenure_days", "active_months"]}
            b = PairedBootstrap(len(cids2), cfg["alignment"]["bootstrap_resamples"], cfg["alignment"]["bootstrap_seed"])
            for c in Sc:
                b.add(c, Sc[c])
            for c in P:
                b.add(c, P[c])
            b.prefetch([(m, l) for m in Sc for l in P], workers=8)
            sw = {m: {f: b.family(m, ls) for f, ls in fams.items()} for m in Sc}
            sw["contrasts"] = {f"{m} - cpr_l50 | {f}": b.contrast((m, ls), ("cpr_l50", ls))
                               for m in OPT1 + ["cpr_plus"] for f, ls in fams.items()}
            res["same_window"] = sw
            (HERE / "results_role_coupled.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
            log("same window evaluated")
    log("all done")


if __name__ == "__main__":
    main()
