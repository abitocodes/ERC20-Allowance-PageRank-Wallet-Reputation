#!/usr/bin/env python3
"""Window W1: rule B, the reported results and the comparison on outcomes built from neither
edge type (docs/registration_w1.md); in the contract-graph variant, two of rule B's registered
criteria (F1, F2), F6 and the spender parts of the two registered sensitivity analyses
(docs/revision_contract_graph.md section 11).

Needs scan B (scripts/extract_w1.py), the W1 labels (sql/06_holdout_labels.sql with
TAG=w1), the decoded GMX closes of July-September and the account types of the new
GMX accounts. Writes data/2-.../registered-w1/eval_summary.json.

In the contract-graph variant (CONTRACT_REP_VARIANT=contract12m) main() runs
main_contract_graph() and nothing else. On the W1 spenders that are contracts (the members
table of graph-tables-contract-12m, with the labels of graph-tables-usd-12m/labels_w1
unchanged) it computes F1 and F2 with the registered margin δ = 0.01 and F6, read only as
"not met" or "both applied criteria hold"; the same criteria under Sensitivity 1 (AWP in place
of C-PR(λ=0)) and Sensitivity 2 (the spenders added as isolated nodes to the graph of every
walk but S-PR); the baselines of revision section 9 with C-PR minus the union in-degree on both
labels; the coverage of the spenders; the comparisons inside the union graph, which decide no
rule; and the W1 label split. It refuses unless it, the project modules it imports, the
revision, the overlay, the base configuration and docs/registration_w1.md are committed without
local changes and the gate B tables it reads are those the driver's download step verified; it
records HEAD and their SHA-256 and writes revised-contract-12m/window-w1/eval_summary.json and
spender_scores.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (GRAPH, GRAPH_U12, PROC, ROOT, TRADERS, W1_DIR, load_config, part_sha256, read_parts,  # noqa: E402
                    require_committed, require_downloaded, save_json, write_parts)
from graphs import (METHOD_LABELS, in_union_graph, load_graphs, load_nodes, member_coverage, raw_degrees,  # noqa: E402
                    score_all, union_in_degree, union_pairs, union_sizes)
from labels import (TRADER_LABELS, UNION_NOTE, account_types, assert_contract_only, label_split,  # noqa: E402
                    load_closes, spender_cohort, strata_tau, trader_labels)
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


# --------------------------------------------------------------------------- the contract-graph variant
# (docs/revision_contract_graph.md section 11; reached only under CONTRACT_REP_VARIANT=contract12m)

# The files main_contract_graph needs committed besides common.EVAL_COMMITTED (δ is read from the registration), the
# gate B tables it reads and the twelve-month table whose labels it keeps.
COMMITTED_FILES = ("scripts/run_registered.py", "scripts/graphs.py", "scripts/scoring.py", "scripts/stats.py",
                   "scripts/labels.py", "docs/registration_w1.md")
GRAPH_STEMS = ("nodes", "allow_pairs_tobs", "transfer_pairs_tobs", "members", "label_split_w1")
U12_STEMS = ("labels_w1",)
APPLIED_CRITERIA = ("F1", "F2")
RULE_B_READING = {True: "both applied criteria hold", False: "not met"}    # revision section 11
ISOLATED_WALKS = tuple(m for m in METHOD_LABELS if m != "spr")             # Sensitivity 2: every walk but S-PR
BASELINES_W1 = ("in_approve_degree", "in_approve_value", "in_degree", "in_degree_union")   # revision section 9
W1_CONTRASTS = (   # (key, a, b, label): the contrasts of F1, F2, F6a, F6b, Sensitivity 1 and the union baseline
    ("cpr_minus_cpr_l0_appr", "cpr_l50", "cpr_l0", APPR),
    ("cpr_minus_cpr_l0_send", "cpr_l50", "cpr_l0", SEND),
    ("cpr_minus_cpr_l100_appr", "cpr_l50", "cpr_l100", APPR),
    ("cpr_minus_awp_appr", "cpr_l50", "awp", APPR),
    ("cpr_minus_awp_send", "cpr_l50", "awp", SEND),
    ("cpr_minus_union_in_degree_appr", "cpr_l50", "in_degree_union", APPR),
    ("cpr_minus_union_in_degree_send", "cpr_l50", "in_degree_union", SEND),
)
BASELINE_W1 = W1_CONTRASTS[5:]


def judged(r: dict | None, what: str) -> dict:
    """The contrast ``r`` of a criterion; a contrast without a value stops the run, since the criterion cannot be
    judged."""
    if r is None:
        raise SystemExit(f"stopped: {what} has no value on every resample (stats.PairedBootstrap.contrast), so its "
                         "criterion cannot be judged; the author decides")
    return r


def applied_rule_b(bs: PairedBootstrap, comp: str, delta: float, with_f6: bool) -> dict:
    """The two criteria of rule B that docs/revision_contract_graph.md section 11 applies (F1: C-PR above ``comp`` on
    new approval pairs; F2: not below it by δ on new transfer senders), whether both hold, and the reading "not met"
    or "both applied criteria hold"; with ``with_f6`` also F6 (rule A's primary part on W1). Rule B is never reported
    as met: the registration needs criteria this revision does not apply."""

    def judge(other: str, label: str, test: str) -> dict:
        r = judged(bs.contrast(("cpr_l50", label), (other, label)), f"C-PR minus {other} on {label}")
        return verdict(r, test, delta)

    out = {"F1": judge(comp, APPR, "superiority"), "F2": judge(comp, SEND, "non_inferiority")}
    hold = bool(out["F1"]["holds"] and out["F2"]["holds"])
    out.update(f1_f2_hold=hold, rule_b_not_met=not hold, rule_b_reading=RULE_B_READING[hold])
    if with_f6:
        out["F6a"] = judge("cpr_l100", APPR, "no_worse")
        out["F6b"] = judge("cpr_l0", SEND, "superiority")
        out["F6"] = bool(out["F6a"]["holds"] and out["F6b"]["holds"])
    return out


def named_contrasts(b: PairedBootstrap, specs) -> dict:
    """{key: contrast or None} for (key, a, b, label) specs, without a verdict."""
    return {key: b.contrast((a, lab), (c, lab)) for key, a, c, lab in specs}


def frame_c12(full: dict, ids: np.ndarray, g, union=None) -> pd.DataFrame:
    """The W1 scores and the four baselines of revision section 9 counted on the contract graph (frame() plus the
    in-approve value and the union in-degree)."""
    S = pd.DataFrame({m: scores_on(ids, s).to_numpy() for m, s in full.items()}, index=ids)
    deg = raw_degrees(g, ids)
    S["in_approve_degree"] = deg["in_approve_degree"].to_numpy()
    S["in_degree"] = deg["in_degree_other"].to_numpy()
    S["in_approve_value"] = deg["in_approve_value"].to_numpy()
    S["in_degree_union"] = union_in_degree(g, ids, union).to_numpy(dtype=np.float64)
    return S


def isolated_frame(g, S: pd.DataFrame, params: dict) -> tuple[pd.DataFrame, dict]:
    """Sensitivity 2 (revision section 11): the members a graph leaves out added as isolated nodes to the graph of
    every walk but S-PR, the coupled ones included (graphs.score_all passes them to coupled_pagerank as extra_nodes).
    S-PR is left out of the call because its restarts would come from the isolated C-PR(λ=1); it and the baselines
    keep their values from S."""
    ids = S.index.to_numpy(np.int64)
    iso, its = score_all(g, params, methods=ISOLATED_WALKS, isolated=ids)
    S2 = S.copy()
    for m in ISOLATED_WALKS:
        S2[m] = scores_on(ids, iso[m]).to_numpy()
    return S2, its


def main_contract_graph() -> int:
    """W1 of the contract-graph variant: F1 and F2 with δ = 0.01, F6, sensitivities 1 and 2, the baselines, the
    coverage, the comparisons inside the union graph and the label split. Writes window-w1/eval_summary.json and
    spender_scores."""
    prov = require_committed(*COMMITTED_FILES)
    inputs = require_downloaded(*GRAPH_STEMS)
    cfg = load_config()
    if cfg["registered_window"].get("status") != "registered":
        raise SystemExit("W1 is not registered")
    delta = registered_delta()
    if delta != 0.01:
        raise SystemExit(f"refused: docs/registration_w1.md gives δ = {delta}; revision section 11 applies the "
                         "registered margin δ = 0.01")
    params = pagerank_params(cfg)
    nb, seed = cfg["alignment"]["bootstrap_resamples"], cfg["alignment"]["bootstrap_seed"]
    nodes = load_nodes()
    typed = assert_contract_only(nodes, cfg)
    lab, counts = spender_cohort("w1", nodes)
    split = label_split("w1", lab)                                       # every refusal before any score
    ids = lab.index.to_numpy(np.int64)
    g = load_graphs("tobs")
    union = union_pairs(g)
    full, iters = score_all(g, params)
    S = frame_c12(full, ids, g, union)
    bs = boot_for(S, lab, [APPR, SEND], nb, seed)
    rule = applied_rule_b(bs, "cpr_l0", delta, with_f6=True)
    sens_awp = applied_rule_b(bs, "awp", delta, with_f6=False)          # Sensitivity 1
    S2, iso_iters = isolated_frame(g, S, params)                         # Sensitivity 2
    b2 = boot_for(S2, lab, [APPR, SEND], nb, seed)
    sens_iso = {**applied_rule_b(b2, "cpr_l0", delta, with_f6=True), "isolated_walks": list(ISOLATED_WALKS),
                "iterations": iso_iters,
                "spender_taus": {m: {l: b2.tau(m, l) for l in (APPR, SEND)} for m in S2}}
    inside = in_union_graph(g, ids, union)
    bi = boot_for(S.loc[inside], lab.loc[inside], [APPR, SEND], nb, seed)
    n_in = int(inside.sum())
    summary = {
        "delta": delta,
        "applied_criteria": list(APPLIED_CRITERIA),
        "spenders": int(len(S)),
        "gained_new_approvals": int((lab[APPR] > 0).sum()),
        "gained_new_senders": int((lab[SEND] > 0).sum()),
        "spender_account_types": counts["by_class"],
        "members": {"spenders_w1": counts},
        "rule_b": rule,
        "sensitivity_awp": sens_awp,
        "sensitivity_isolated": sens_iso,
        "spender_taus": {m: {l: bs.tau(m, l) for l in (APPR, SEND)} for m in S},
        "endorserank_results": {
            "endorserank_minus_degree_appr": bs.contrast(("endorserank", APPR), ("in_approve_degree", APPR)),
            "awp_minus_degree_send": bs.contrast(("awp", SEND), ("in_degree", SEND)),
            "cpr_minus_endorserank_appr": bs.contrast(("cpr_l50", APPR), ("endorserank", APPR)),
        },
        "baselines": list(BASELINES_W1),
        "baseline_contrasts": named_contrasts(bs, BASELINE_W1),
        "graph": {"allowance_pairs": int(len(g.allow)), "transfer_pairs": int(len(g.transfer))},
        "union_graph": union_sizes(union),
        "iterations": iters,
        "cohort_coverage": {"spenders_w1": member_coverage(g, ids, union)},
        "in_union_graph": {"n": n_in, "share": (n_in / inside.size) if inside.size else None, "note": UNION_NOTE,
                           "spender_taus": {m: {l: bi.tau(m, l) for l in (APPR, SEND)} for m in S},
                           "contrasts": named_contrasts(bi, W1_CONTRASTS)},
        "label_split": split,
        "contract_only": typed,
        "provenance": {**prov, "inputs": inputs,
                       "inputs_twelve_month": {s: part_sha256(GRAPH_U12 / s) for s in U12_STEMS}},
    }
    save_json(summary, OUT / "eval_summary.json")
    write_parts(pd.concat([S, lab, pd.DataFrame({"in_union_graph": inside}, index=S.index)], axis=1)
                .reset_index(names="id"), OUT / "spender_scores")
    print("F1 and F2, two of rule B's registered criteria:", rule["rule_b_reading"],
          {k: rule[k]["holds"] for k in APPLIED_CRITERIA})
    return 0


def main() -> int:
    if not TRADERS:
        # docs/revision_contract_graph.md section 11: two of rule B's registered criteria (F1, F2), F6 and the spender
        # parts of the two registered sensitivity analyses, on the contract graph; nothing below runs in that variant.
        return main_contract_graph()
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
