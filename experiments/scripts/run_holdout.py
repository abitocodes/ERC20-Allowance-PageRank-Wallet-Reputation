#!/usr/bin/env python3
"""Temporal holdout W0: scores frozen at t1, labels counted from April to June 2026.

Spender cohort: every contract spender with a positive latest allowance at t1 in the
extracted approval data. Every score and the two raw degrees at t1 are set against
new approval pairs and new transfer senders with paired-bootstrap intervals, the
primary part of rule A is judged, the contrasts fixed in advance are separated
from those computed afterwards, and the restriction to spenders that had received
a transfer before t1 is reported. The exploratory trader run scores the GMX
contract accounts on profit labels (liquidation labels are left for the
registered analysis). Writes data/2-.../holdout-w0/eval_summary.json.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import GRAPH, PROC, load_config, read_parts, save_json, write_parts  # noqa: E402
from graphs import load_graphs, load_nodes, raw_degrees, score_all  # noqa: E402
from labels import account_types, load_closes, trader_labels  # noqa: E402
from run_same_window import closed_form, tie_profile  # noqa: E402
from scoring import pagerank_params, scores_on  # noqa: E402
from stats import PairedBootstrap  # noqa: E402

OUT = PROC / "holdout-w0"
APPR, SEND = "future_new_approvers", "future_new_transfer_senders"

PREFIXED = [  # rule A, fixed in docs/analysis_plan.md (commit 43d8045) before any data
    ("C-PR minus C-PR (l=1)", "cpr_l50", "cpr_l100", APPR),
    ("C-PR minus C-PR (l=0)", "cpr_l50", "cpr_l0", SEND),
]
AFTER = [  # computed after the labels were known
    ("C-PR (l=1) minus t1 in-approve degree", "cpr_l100", "t1_in_approve_degree", APPR),
    ("S-PR minus C-PR (l=1)", "spr", "cpr_l100", APPR),
    ("S-PR minus C-PR (l=0)", "spr", "cpr_l0", SEND),
    ("EndorseRank minus t1 in-approve degree", "endorserank", "t1_in_approve_degree", APPR),
    ("AWP minus t1 in-degree", "awp", "t1_in_degree", SEND),
    ("C-PR minus C-PR (l=0)", "cpr_l50", "cpr_l0", APPR),
    ("C-PR minus EndorseRank", "cpr_l50", "endorserank", APPR),
    ("C-PR minus AWP", "cpr_l50", "awp", SEND),
    ("C-PR minus AWP", "cpr_l50", "awp", APPR),
    ("EndorseRank minus AWP", "endorserank", "awp", APPR),
    ("EndorseRank minus AWP", "endorserank", "awp", SEND),
]


def contrast_rows(boot: PairedBootstrap, specs) -> list[dict]:
    rows = []
    for label, a, b, lab in specs:
        r = boot.contrast((a, lab), (b, lab)) or {}
        rows.append({"label": label, "a": a, "b": b, "outcome": lab, **r})
    return rows


def evaluate(S: pd.DataFrame, L: pd.DataFrame, labels: list[str], cfg: dict) -> tuple[PairedBootstrap, dict]:
    boot = PairedBootstrap(len(S), cfg["alignment"]["bootstrap_resamples"], cfg["alignment"]["bootstrap_seed"])
    for c in S:
        boot.add(c, S[c])
    for c in labels:
        boot.add(c, L[c])
    boot.prefetch([(m, l) for m in S for l in labels], workers=8)
    return boot, {m: {l: boot.tau(m, l) for l in labels} for m in S}


def main() -> int:
    cfg = load_config()
    params = pagerank_params(cfg)
    nodes = load_nodes()
    addr = nodes.set_index("address")["id"]
    g = load_graphs("t1")

    lab = read_parts(GRAPH / "labels_w0")
    kinds = account_types()
    lab["code_kind"] = lab["wallet"].map(kinds)
    unknown = int(lab["code_kind"].isna().sum())
    if unknown:
        print(f"{unknown} spenders without an account type; run check_account_code.py on them first")
        return 1
    kind_counts = lab["code_kind"].value_counts().to_dict()
    lab = lab[lab["code_kind"] == "contract"].copy()
    lab["id"] = lab["wallet"].map(addr)
    lab = lab.dropna(subset=["id"]).astype({"id": np.int64}).sort_values("id").set_index("id")
    ids = lab.index.to_numpy(np.int64)

    full, iters = score_all(g, params)
    S = pd.DataFrame({m: scores_on(ids, s).to_numpy() for m, s in full.items()}, index=ids)
    deg = raw_degrees(g, ids)
    S["t1_in_approve_degree"] = deg["in_approve_degree"].to_numpy()
    S["t1_in_degree"] = deg["in_degree_other"].to_numpy()

    other = ["future_revoke_count", "future_drain_owners"]
    boot, taus = evaluate(S, lab, [APPR, SEND] + other, cfg)
    pre = contrast_rows(boot, PREFIXED)
    post = contrast_rows(boot, AFTER)
    d_appr = next(r for r in pre if r["a"] == "cpr_l50" and r["b"] == "cpr_l100")
    d_send = next(r for r in pre if r["a"] == "cpr_l50" and r["b"] == "cpr_l0")
    rule_a = {
        "no_worse_on_new_approvals": d_appr["ci_high"] >= 0,
        "better_on_new_senders": d_send["ci_low"] > 0,
    }
    rule_a["pass"] = rule_a["no_worse_on_new_approvals"] and rule_a["better_on_new_senders"]

    # Spenders that had received a transfer from another address before t1.
    recv = S["t1_in_degree"] > 0
    Sr, Lr = S.loc[recv, ["endorserank", "awp", "t1_in_approve_degree", "t1_in_degree"]], lab.loc[recv]
    boot_r, taus_r = evaluate(Sr, Lr, [APPR, SEND], cfg)
    contr_r = contrast_rows(boot_r, [AFTER[0], AFTER[1]])

    no_transfer = S["awp"] == 0
    coverage = {
        "spenders_without_transfer_edge": int(no_transfer.sum()),
        "share_gaining_approvals_without": float((lab.loc[no_transfer, APPR] > 0).mean()) if no_transfer.any() else None,
        "share_gaining_approvals_with": float((lab.loc[~no_transfer, APPR] > 0).mean()),
        "share_gaining_senders_without": float((lab.loc[no_transfer, SEND] > 0).mean()) if no_transfer.any() else None,
        "share_gaining_senders_with": float((lab.loc[~no_transfer, SEND] > 0).mean()),
    }

    # Exploratory trader run: GMX contract accounts in the t1 graph with >= 3 closes in the window.
    closes = load_closes(("obs",))
    hcfg = cfg["holdout"]
    tl = trader_labels(closes, hcfg["outcome_start"], hcfg["outcome_end"], cfg["gmx_arbitrum"]["min_closes"])
    tl["id"] = tl.index.map(addr)
    in_graph = set(np.union1d(np.union1d(g.allow["src"], g.allow["dst"]), np.union1d(g.transfer["src"], g.transfer["dst"])))
    tl = tl.dropna(subset=["id"]).astype({"id": np.int64})
    tl = tl[tl["id"].isin(in_graph)].sort_values("id").set_index("id")
    tids = tl.index.to_numpy(np.int64)
    St = pd.DataFrame({m: scores_on(tids, s).to_numpy() for m, s in full.items()}, index=tids)
    tdeg = raw_degrees(g, tids)
    St["t1_in_approve_degree"] = tdeg["in_approve_degree"].to_numpy()
    St["t1_in_degree"] = tdeg["in_degree_other"].to_numpy()
    profit = ["profitable_closes", "realized_gain", "profitable_share", "non_loss_share"]
    _, taus_t = evaluate(St, tl, profit, cfg)

    summary = {
        "freeze": hcfg["score_end"], "labels": [hcfg["outcome_start"], hcfg["outcome_end"]],
        "spender_account_types": kind_counts,
        "spenders": int(len(ids)),
        "gained_new_approvals": int((lab[APPR] > 0).sum()),
        "gained_new_senders": int((lab[SEND] > 0).sum()),
        "graph": {"allowance_edges": int(len(g.allow)), "transfer_edges": int(len(g.transfer))},
        "iterations": iters,
        "taus": taus,
        "contrasts_prefixed": pre,
        "contrasts_after": post,
        "rule_a_primary": rule_a,
        "receiving": {"n": int(recv.sum()), "taus": taus_r, "contrasts": contr_r},
        "coverage": coverage,
        "ties": {m: tie_profile(S[m].to_numpy()) for m in ("endorserank", "awp", "cpr_l100")},
        "closed_form": closed_form(g.allow, full["endorserank"], ids, params["damping"]),
        "traders": {"n": int(len(tids)), "with_any_approval_received": int((St["t1_in_approve_degree"] > 0).sum()),
                    "taus": taus_t},
    }
    save_json(summary, OUT / "eval_summary.json")
    write_parts(pd.concat([S, lab], axis=1).reset_index().rename(columns={"index": "id"}), OUT / "spender_scores")
    write_parts(pd.concat([St, tl], axis=1).reset_index().rename(columns={"index": "id"}), OUT / "trader_scores")
    print("rule A primary:", rule_a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
