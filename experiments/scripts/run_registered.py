#!/usr/bin/env python3
"""Registered window W1 (docs/registration_w1.md): rule B, the reported results and the
comparison on outcomes built from neither edge type, in the order the registration fixes.

Needs scan B (scripts/extract_w1.py), the W1 labels (sql/06_holdout_labels.sql with
TAG=w1), the decoded GMX closes of July-September and the account types of the new
GMX accounts. Writes data/2-.../registered-w1/eval_summary.json.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import GRAPH, PROC, ROOT, W1_DIR, load_config, read_parts, save_json, write_parts  # noqa: E402
from graphs import load_graphs, load_nodes, raw_degrees, score_all  # noqa: E402
from labels import TRADER_LABELS, account_types, load_closes, strata_tau, trader_labels  # noqa: E402
from scoring import pagerank_params, scores_on  # noqa: E402
from stats import PairedBootstrap, percentile_ci  # noqa: E402

OUT = PROC / W1_DIR
APPR, SEND, LIQ = "future_new_approvers", "future_new_transfer_senders", "liquidation_free_rate"


def registered_delta() -> float:
    text = (ROOT / "docs" / "registration_w1.md").read_text(encoding="utf-8")
    m = re.search(r"margin is δ = ([0-9.]+)", text)
    if not m:
        raise SystemExit("registration has no margin")
    return float(m.group(1))


def frame(full, ids, g) -> pd.DataFrame:
    S = pd.DataFrame({m: scores_on(ids, s).to_numpy() for m, s in full.items()}, index=ids)
    deg = raw_degrees(g, ids)
    S["in_approve_degree"] = deg["in_approve_degree"].to_numpy()
    S["in_degree"] = deg["in_degree_other"].to_numpy()
    return S


def boot_for(S: pd.DataFrame, L: pd.DataFrame, labels: list[str], n_boot: int, seed: int) -> PairedBootstrap:
    b = PairedBootstrap(len(S), n_boot, seed)
    for c in S:
        b.add(c, S[c])
    for c in labels:
        b.add(c, L[c])
    b.prefetch([(m, l) for m in S for l in labels], workers=8)
    return b


def verdict(r: dict, test: str, delta: float) -> dict:
    if test == "superiority":
        ok = r["ci_low"] > 0
    elif test == "non_inferiority":
        ok = r["ci_low"] > -delta
    else:  # no worse
        ok = r["ci_high"] >= 0
    return {**r, "test": test, "holds": bool(ok)}


def rule_b(bs: PairedBootstrap, bt: PairedBootstrap, comp: str, delta: float, with_f56: bool) -> dict:
    out = {
        "F1": verdict(bs.contrast(("cpr_l50", APPR), (comp, APPR)), "superiority", delta),
        "F2": verdict(bs.contrast(("cpr_l50", SEND), (comp, SEND)), "non_inferiority", delta),
        "F3": verdict(bt.contrast(("cpr_l50", LIQ), (comp, LIQ)), "non_inferiority", delta),
        "F4": verdict(bt.contrast(("cpr_l50", LIQ), (comp, LIQ)), "superiority", delta),
    }
    out["decision"] = all(out[k]["holds"] for k in ("F1", "F2", "F3"))
    if with_f56:
        out["F5"] = verdict(bt.contrast(("cpr_l50", LIQ), ("cpr_l100", LIQ)), "superiority", delta)
        out["F6a"] = verdict(bs.contrast(("cpr_l50", APPR), ("cpr_l100", APPR)), "no_worse", delta)
        out["F6b"] = verdict(bs.contrast(("cpr_l50", SEND), ("cpr_l0", SEND)), "superiority", delta)
        out["F6"] = out["F6a"]["holds"] and out["F6b"]["holds"]
    return out


NEUTRAL_PAIRS = [
    ("P", "in_approve_degree", "in_degree"),
    ("Q", "endorserank_activity", "awp"),
    ("layers", "cpr_l100", "cpr_l0"),
    ("er_awp", "endorserank", "awp"),
    ("cpr0_awp", "cpr_l0", "awp"),
    ("er_degree", "endorserank", "in_approve_degree"),
]


def neutral(St: pd.DataFrame, tl: pd.DataFrame, n_boot: int, seed: int) -> dict:
    labels = list(TRADER_LABELS)
    b = boot_for(St, tl, labels, n_boot, seed)
    grid = {}
    for name, a, c in NEUTRAL_PAIRS:
        grid[name] = {}
        for lab in labels:
            r = b.contrast((a, lab), (c, lab)) or {}
            if r and name in ("P", "Q") and lab == LIQ:
                lo, hi = percentile_ci(b.samples(a, lab) - b.samples(c, lab), 0.975)
                r["ci975_low"], r["ci975_high"] = lo, hi
            grid[name][lab] = r
    closes = tl["closes"].to_numpy()
    strat = {}
    for name, a, c in NEUTRAL_PAIRS[:2]:
        y = tl[LIQ].to_numpy()
        pa, pc = St[a].to_numpy(), St[c].to_numpy()
        point = strata_tau(pa, y, closes) - strata_tau(pc, y, closes)
        sam = []
        for row in b.idx:
            ta, tc = strata_tau(pa[row], y[row], closes[row]), strata_tau(pc[row], y[row], closes[row])
            if ta is not None and tc is not None:
                sam.append(ta - tc)
        lo, hi = percentile_ci(np.asarray(sam), 0.95)
        strat[name] = {"a_tau": strata_tau(pa, y, closes), "b_tau": strata_tau(pc, y, closes),
                       "delta_tau": point, "ci_low": lo, "ci_high": hi}
    taus = {m: {l: b.tau(m, l) for l in labels} for m in St}
    rec = St["in_approve_degree"] > 0
    recipients = {}
    for grp, mask in (("recipients", rec), ("others", ~rec)):
        sub = tl.loc[mask]
        recipients[grp] = {"n": int(mask.sum()), "share_no_liquidation": float(sub["no_liquidation"].mean()) if len(sub) else None,
                           **{f"mean_{l}": float(sub[l].mean()) if len(sub) else None for l in (LIQ, "profitable_share", "non_loss_share")},
                           "median_closes": float(sub["closes"].median()) if len(sub) else None}
    top = St["in_approve_degree"].nlargest(10).index
    keep = ~St.index.isin(top)
    b2 = boot_for(St.loc[keep, ["in_approve_degree", "in_degree"]], tl.loc[keep], [LIQ], n_boot, seed)
    influence = b2.contrast(("in_approve_degree", LIQ), ("in_degree", LIQ))
    return {"n": int(len(St)), "taus": taus, "grid": grid, "stratified": strat,
            "recipients": recipients, "influence_without_top10": influence,
            "max_in_approve_degree": float(St["in_approve_degree"].max())}


def traders(closes, start, end, g, full, addr, kinds, min_closes) -> tuple[pd.DataFrame, pd.DataFrame]:
    tl = trader_labels(closes, start, end, min_closes)
    tl = tl[tl.index.map(lambda a: kinds.get(a) == "contract")]
    tl["id"] = tl.index.map(addr)
    nodes_in = set(np.union1d(np.union1d(g.allow["src"], g.allow["dst"]), np.union1d(g.transfer["src"], g.transfer["dst"])))
    tl = tl.dropna(subset=["id"]).astype({"id": np.int64})
    tl = tl[tl["id"].isin(nodes_in)].sort_values("id").set_index("id")
    St = frame(full, tl.index.to_numpy(np.int64), g)
    return St, tl


def main() -> int:
    cfg = load_config()
    if cfg["registered_window"].get("status") != "registered":
        raise SystemExit("W1 is not registered")
    delta = registered_delta()
    params = pagerank_params(cfg)
    nb, seed = cfg["alignment"]["bootstrap_resamples"], cfg["alignment"]["bootstrap_seed"]
    nodes = load_nodes()
    addr = nodes.set_index("address")["id"]
    kinds = account_types()
    g = load_graphs("tobs")
    full, iters = score_all(g, params)

    lab = read_parts(GRAPH / "labels_w1")
    lab["code_kind"] = lab["wallet"].map(kinds)
    if lab["code_kind"].isna().any():
        raise SystemExit(f"{int(lab['code_kind'].isna().sum())} W1 spenders lack an account type")
    lab = lab[lab["code_kind"] == "contract"].copy()
    lab["id"] = lab["wallet"].map(addr)
    lab = lab.dropna(subset=["id"]).astype({"id": np.int64}).sort_values("id").set_index("id")
    S = frame(full, lab.index.to_numpy(np.int64), g)
    bs = boot_for(S, lab, [APPR, SEND], nb, seed)

    closes = load_closes(("obs", "w1"))
    rw = cfg["registered_window"]
    St, tl = traders(closes, rw["outcome_start"], rw["outcome_end"], g, full, addr, kinds, cfg["gmx_arbitrum"]["min_closes"])
    bt = boot_for(St, tl, [LIQ], nb, seed)

    rule = rule_b(bs, bt, "cpr_l0", delta, with_f56=True)
    sens_awp = rule_b(bs, bt, "awp", delta, with_f56=False)

    # Sensitivity 2: wallets outside a graph kept as isolated nodes (changes the single-layer walks).
    iso_s, _ = score_all(g, params, methods=("cpr_l100", "cpr_l0"), isolated=lab.index.to_numpy(np.int64))
    iso_t, _ = score_all(g, params, methods=("cpr_l100", "cpr_l0"), isolated=St.index.to_numpy(np.int64))
    S2, St2 = S.copy(), St.copy()
    for m in ("cpr_l100", "cpr_l0"):
        S2[m] = scores_on(S.index.to_numpy(), iso_s[m]).to_numpy()
        St2[m] = scores_on(St.index.to_numpy(), iso_t[m]).to_numpy()
    sens_iso = rule_b(boot_for(S2, lab, [APPR, SEND], nb, seed), boot_for(St2, tl, [LIQ], nb, seed), "cpr_l0", delta, with_f56=True)

    spender_taus = {m: {l: bs.tau(m, l) for l in (APPR, SEND)} for m in S}
    trader_taus = {m: bt.tau(m, LIQ) for m in St}
    posthoc = {
        "endorserank_minus_degree_appr": bs.contrast(("endorserank", APPR), ("in_approve_degree", APPR)),
        "awp_minus_degree_send": bs.contrast(("awp", SEND), ("in_degree", SEND)),
        "cpr_minus_endorserank_appr": bs.contrast(("cpr_l50", APPR), ("endorserank", APPR)),
        "cpr_minus_endorserank_liq": bt.contrast(("cpr_l50", LIQ), ("endorserank", LIQ)),
    }
    other_trader = neutral(St, tl, 2000, seed)

    # W0 (secondary window of the neutral-label comparison).
    g0 = load_graphs("t1")
    full0, _ = score_all(g0, params)
    hw = cfg["holdout"]
    St0, tl0 = traders(closes, hw["outcome_start"], hw["outcome_end"], g0, full0, addr, kinds, cfg["gmx_arbitrum"]["min_closes"])
    other_trader_w0 = neutral(St0, tl0, 2000, seed)

    p = other_trader["grid"]["P"][LIQ]
    q = other_trader["grid"]["Q"][LIQ]
    r = {
        "R1": bool(p["ci975_low"] > 0 and other_trader["stratified"]["P"]["ci_low"] > 0
                   and other_trader_w0["grid"]["P"][LIQ]["delta_tau"] > 0),
        "R2": bool(q["ci975_low"] > 0 and other_trader_w0["grid"]["Q"][LIQ]["delta_tau"] > 0),
        "R3": bool(any(other_trader["grid"]["P"][l]["ci_high"] < 0 for l in ("profitable_share", "non_loss_share"))),
    }
    summary = {
        "delta": delta,
        "spenders": int(len(S)), "gained_new_approvals": int((lab[APPR] > 0).sum()),
        "gained_new_senders": int((lab[SEND] > 0).sum()),
        "traders": int(len(St)), "traders_liquidated": int((tl["liquidations"] > 0).sum()),
        "traders_all_liquidated": int((tl[LIQ] == 0).sum()),
        "rule_b": rule, "sensitivity_awp": sens_awp, "sensitivity_isolated": sens_iso,
        "spender_taus": spender_taus, "trader_taus": trader_taus, "endorserank_results": posthoc,
        "neutral_w1": other_trader, "neutral_w0": other_trader_w0, "neutral_rules": r,
        "iterations": iters,
    }
    save_json(summary, OUT / "eval_summary.json")
    write_parts(pd.concat([S, lab], axis=1).reset_index(names="id"), OUT / "spender_scores")
    write_parts(pd.concat([St, tl], axis=1).reset_index(names="id"), OUT / "trader_scores")
    print("rule B decision:", rule["decision"], {k: rule[k]["holds"] for k in ("F1", "F2", "F3")}, r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
