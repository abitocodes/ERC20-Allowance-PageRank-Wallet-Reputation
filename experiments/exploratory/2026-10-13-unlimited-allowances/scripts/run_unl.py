"""Exploratory: EndorseRank with unlimited allowances left out.

Variants of the allowance graph (transfer graph unchanged):
  orig  the published revised (USD) graph
  fin   unlimited allowances (>= 1.15e77 base units) dropped; a pair keeps its finite allowances
  own   every allowance of an owner that holds at least one unlimited allowance dropped

Evaluations (same cohorts, labels, bootstrap seed and B as the published runs):
  W0 holdout (scores at t1, labels Apr-Jun 2026), W1 (scores at T_obs, labels Jul-Sep 2026),
  same window at T_obs (matched cohort, proxies of the published run).
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
from graphs import Graphs, load_graphs, load_nodes, raw_degrees  # noqa: E402
from labels import account_types  # noqa: E402
from scoring import activeness, pagerank_params, scores_on, weighted_pagerank  # noqa: E402
from stats import PairedBootstrap  # noqa: E402

APPR, SEND = "future_new_approvers", "future_new_transfer_senders"
REV, DRAIN = "future_revoke_count", "future_drain_owners"
APPR_FIN, APPR_UNL = "new_appr_finite", "new_appr_unlimited"
VARIANTS = os.environ.get("UNL_VARIANTS", "orig,fin,own").split(",")
ALT = [v for v in VARIANTS if v != "orig"]
OUTNAME = os.environ.get("UNL_OUT", "results.json")


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def variants(g: Graphs, tag: str) -> tuple[dict[str, Graphs], dict]:
    x = read_parts(RAW / f"x_unl_pairs_{tag}")
    a = g.allow.merge(x, on=["src", "dst"], how="left", indicator=True)
    hit = (a["_merge"] == "both").to_numpy()
    assert hit.sum() == len(x), (hit.sum(), len(x))
    rel = np.abs(a.loc[hit, "w_er_all"] - a.loc[hit, "w_er"]) / a.loc[hit, "w_er"].clip(lower=1e-300)
    cols = ["src", "dst", "n_tokens", "w_er", "w_raw", "max_sig"]

    fin = a.copy()
    fin.loc[hit, "w_er"] = fin.loc[hit, "w_er_fin"]
    fin.loc[hit, "w_raw"] = fin.loc[hit, "w_raw_fin"]
    fin.loc[hit, "max_sig"] = fin.loc[hit, "max_sig_fin"]
    fin.loc[hit, "n_tokens"] = fin.loc[hit, "n_fin"]
    fin = fin[~hit | (fin["n_fin"] > 0).to_numpy()]

    bad_owners = np.unique(x["src"].to_numpy())
    own = g.allow[~g.allow["src"].isin(bad_owners)]

    info = {
        "pairs": int(len(g.allow)),
        "pairs_with_unlimited": int(len(x)),
        "pairs_unlimited_only": int((x["n_fin"] == 0).sum()),
        "check_max_rel_diff_w_er": float(rel.max()),
        "fin_pairs": int(len(fin)),
        "owners": int(g.allow["src"].nunique()),
        "owners_with_unlimited": int(len(bad_owners)),
        "own_pairs": int(len(own)),
        "w_er_share_kept_fin": float(fin["w_er"].sum() / g.allow["w_er"].sum()),
    }
    u = read_parts(RAW / f"x_unlonly_pairs_{tag}")
    chk = x.merge(u, on=["src", "dst"])
    assert len(chk) == len(x) == len(u)
    info["check_max_abs_diff_w_er_unl"] = float(np.abs(chk["w_er_all"] - chk["w_er_fin"] - chk["w_er_unl"]).max())
    unl = u.rename(columns={"n_unl": "n_tokens", "w_er_unl": "w_er", "w_raw_unl": "w_raw", "max_sig_unl": "max_sig"})
    uown = g.allow[g.allow["src"].isin(bad_owners)]
    info["unl_pairs"] = int(len(unl))
    info["uown_pairs"] = int(len(uown))
    out = {"orig": g,
           "fin": Graphs(tag, fin[cols].reset_index(drop=True), g.transfer),
           "own": Graphs(tag, own.reset_index(drop=True), g.transfer),
           "unl": Graphs(tag, unl[cols].reset_index(drop=True), g.transfer),
           "uown": Graphs(tag, uown.reset_index(drop=True), g.transfer)}
    return {k: v for k, v in out.items() if k in VARIANTS}, info


def allowance_scores(g: Graphs, p: dict) -> dict[str, pd.Series]:
    a = g.allow
    er, _ = weighted_pagerank(a["src"], a["dst"], a["w_er"], **p)
    act = activeness(a["src"], a["dst"], a["max_sig"])
    era, _ = weighted_pagerank(a["src"], a["dst"], a["w_er"], teleport=act, **p)
    cpr1, _ = weighted_pagerank(a["src"], a["dst"], a["w_raw"], **p)
    return {"endorserank": er, "endorserank_activity": era, "cpr_l100": cpr1}


def frame(gv: dict[str, Graphs], ids: np.ndarray, p: dict) -> pd.DataFrame:
    S = pd.DataFrame(index=ids)
    for v, g in gv.items():
        for m, s in allowance_scores(g, p).items():
            S[f"{m}:{v}"] = scores_on(ids, s).to_numpy()
        S[f"deg:{v}"] = raw_degrees(g, ids)["in_approve_degree"].to_numpy()
        log("scored", v)
    g = gv["orig"]
    t = g.transfer
    act = activeness(t["src"], t["dst"], t["max_sig"])
    awp, _ = weighted_pagerank(t["src"], t["dst"], t["w_awp"], teleport=act, **p)
    S["awp"] = scores_on(ids, awp).to_numpy()
    S["tdeg"] = raw_degrees(g, ids)["in_degree_other"].to_numpy()
    return S


def spender_labels(name: str, tag: str, kinds: pd.Series, addr: pd.Series) -> pd.DataFrame:
    lab = read_parts(GRAPH / name)
    lab["code_kind"] = lab["wallet"].map(kinds)
    lab = lab[lab["code_kind"] == "contract"].copy()
    xl = read_parts(RAW / f"x_unl_labels_{tag}").set_index("wallet")
    lab = lab.join(xl, on="wallet")
    for c in ("n_new_fin", "n_new_unl", "n_new_all"):
        lab[c] = lab[c].fillna(0).astype(np.int64)
    mism = int((lab["n_new_all"] != lab[APPR]).sum())
    lab[APPR_FIN] = lab["n_new_fin"]
    lab[APPR_UNL] = lab["n_new_unl"]
    lab["id"] = lab["wallet"].map(addr)
    lab = lab.dropna(subset=["id"]).astype({"id": np.int64}).sort_values("id").set_index("id")
    lab.attrs["label_mismatch"] = mism
    return lab


def evaluate(S: pd.DataFrame, L: pd.DataFrame, labels: list[str], cfg: dict) -> dict:
    boot = PairedBootstrap(len(S), cfg["alignment"]["bootstrap_resamples"], cfg["alignment"]["bootstrap_seed"])
    for c in S:
        boot.add(c, S[c])
    for c in labels:
        boot.add(c, L[c])
    boot.prefetch([(m, l) for m in S for l in labels], workers=8)
    taus = {m: {l: boot.tau(m, l) for l in labels} for m in S}
    con = {}
    for v in ALT:
        for l in labels:
            con[f"ER:{v} - ER:orig | {l}"] = boot.contrast((f"endorserank:{v}", l), ("endorserank:orig", l))
            con[f"ER:{v} - deg:orig | {l}"] = boot.contrast((f"endorserank:{v}", l), ("deg:orig", l))
            con[f"ER:{v} - deg:{v} | {l}"] = boot.contrast((f"endorserank:{v}", l), (f"deg:{v}", l))
            con[f"ERact:{v} - ERact:orig | {l}"] = boot.contrast((f"endorserank_activity:{v}", l), ("endorserank_activity:orig", l))
            con[f"ER:{v} - awp | {l}"] = boot.contrast((f"endorserank:{v}", l), ("awp", l))
    for l in labels:
        con[f"ER:orig - deg:orig | {l}"] = boot.contrast(("endorserank:orig", l), ("deg:orig", l))
        con[f"ER:orig - awp | {l}"] = boot.contrast(("endorserank:orig", l), ("awp", l))
    return {"taus": taus, "contrasts": con}


def holdout(name, tag, lab_name, lab_tag, cfg, p, kinds, addr):
    g = load_graphs(tag)
    gv, info = variants(g, tag)
    log(name, info)
    lab = spender_labels(lab_name, lab_tag, kinds, addr)
    ids = lab.index.to_numpy(np.int64)
    S = frame(gv, ids, p)
    zero = {v: int((S[f"deg:{v}"] == 0).sum()) for v in gv}
    labels = [APPR, SEND, REV, DRAIN, APPR_FIN, APPR_UNL]
    res = evaluate(S, lab, labels, cfg)
    unl_share = None
    extra = {
        "spenders": int(len(ids)),
        "label_mismatch_new_approvers": lab.attrs["label_mismatch"],
        "spenders_without_allowance": zero,
        "new_appr_total": int(lab[APPR].sum()),
        "new_appr_finite_total": int(lab[APPR_FIN].sum()),
        "new_appr_unlimited_total": int(lab[APPR_UNL].sum()),
        "graph": info,
    }
    return {**extra, **res}, S, lab, unl_share


def premise(S: pd.DataFrame, lab: pd.DataFrame, cfg: dict) -> dict:
    """Is a spender's share of unlimited allowances a warning sign? tau of the share with the labels."""
    sh = (1 - S["deg:fin"] / S["deg:orig"]).where(S["deg:orig"] > 0)
    keep = sh.notna().to_numpy()
    Lk = lab.loc[keep].copy()
    Lk["revoke_rate"] = Lk["future_revoke_rate"]
    Lk["drain_rate"] = Lk[DRAIN] / S.loc[keep, "deg:orig"]
    boot = PairedBootstrap(int(keep.sum()), cfg["alignment"]["bootstrap_resamples"], cfg["alignment"]["bootstrap_seed"])
    boot.add("unl_share", sh[keep])
    labs = [APPR, SEND, REV, DRAIN, "revoke_rate", "drain_rate"]
    for c in labs:
        boot.add(c, Lk[c])
    boot.prefetch([("unl_share", l) for l in labs], workers=8)
    q = pd.qcut(sh[keep], [0, 0.25, 0.5, 0.75, 1.0], duplicates="drop")
    by_q = Lk.assign(q=q.astype(str)).groupby("q").agg(
        n=(APPR, "size"), gain_appr=(APPR, lambda s: float((s > 0).mean())),
        revoke_rate=("revoke_rate", "mean"), drain_rate=("drain_rate", "mean"))
    return {"n": int(keep.sum()),
            "share_quantiles": [float(v) for v in np.nanquantile(sh, [0.1, 0.25, 0.5, 0.75, 0.9])],
            "taus": {l: boot.tau("unl_share", l) for l in labs},
            "by_quartile": by_q.reset_index().to_dict(orient="records")}


def same_window(cfg, p):
    nodes = load_nodes()
    cohort = nodes.loc[nodes["is_cohort"], ["id", "address"]].sort_values("id")
    ids = cohort["id"].to_numpy(np.int64)
    g = load_graphs("tobs")
    gv, _ = variants(g, "tobs")
    S = pd.DataFrame(index=ids)
    for v, gg in gv.items():
        a = gg.allow
        er, _ = weighted_pagerank(a["src"], a["dst"], a["w_er"], **p)
        S[f"endorserank:{v}"] = scores_on(ids, er).to_numpy()
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
    boot = PairedBootstrap(len(ids), cfg["alignment"]["bootstrap_resamples"], cfg["alignment"]["bootstrap_seed"])
    for c in S:
        boot.add(c, S[c])
    for c in P:
        boot.add(c, P[c])
    boot.prefetch([(m, l) for m in S for l in P], workers=8)
    out = {v: {f: boot.family(f"endorserank:{v}", ls) for f, ls in fams.items()} for v in gv}
    out["contrasts"] = {f"{v} - orig | {f}": boot.contrast((f"endorserank:{v}", ls), ("endorserank:orig", ls))
                        for v in ALT for f, ls in fams.items()}
    out["zeros"] = {v: int((S[f"endorserank:{v}"] == 0).sum()) for v in gv}
    return out


def main() -> int:
    cfg = load_config()
    p = pagerank_params(cfg)
    nodes = load_nodes()
    addr = nodes.set_index("address")["id"]
    kinds = account_types()
    res = {}
    res["w0"], S0, L0, _ = holdout("W0", "t1", "labels_w0", "w0", cfg, p, kinds, addr)
    if "fin" in VARIANTS: res["w0_premise"] = premise(S0, L0, cfg)
    pd.concat([S0, L0], axis=1).to_parquet(XPROC / OUTNAME.replace(".json", "_w0.parquet"))
    (HERE / OUTNAME).write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    log("W0 done")
    res["w1"], S1, L1, _ = holdout("W1", "tobs", "labels_w1", "w1", cfg, p, kinds, addr)
    if "fin" in VARIANTS: res["w1_premise"] = premise(S1, L1, cfg)
    pd.concat([S1, L1], axis=1).to_parquet(XPROC / OUTNAME.replace(".json", "_w1.parquet"))
    (HERE / OUTNAME).write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    log("W1 done")
    res["same_window"] = same_window(cfg, p)
    (HERE / OUTNAME).write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    log("all done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
