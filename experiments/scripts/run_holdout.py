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

In the contract-graph variant (CONTRACT_REP_VARIANT=contract12m,
docs/revision_contract_graph.md sections 8, 9 and 11) the script refuses to run
unless it, the revision, the overlay, the base configuration and the project
modules it imports are committed without local changes, and unless the gate B
tables it reads are those the download step verified. The spender cohort is the
W0 spenders of graph-tables-usd-12m/labels_w0 that the members table classes as
contracts, each kept with its node id, and the labels are those of that table
unchanged. Rule A's primary part is judged on the contract graph at t1; the
baselines also hold the in-approve value and the union in-degree, and the
summary holds C-PR minus the union in-degree on both labels, the coverage of
the W0 spenders and of the W0 cohort, the comparisons repeated on the spenders
inside the union graph (they decide no rule), the W0 label split by user
accounts, contracts and other accounts (a description outside every rule) and
the provenance of the code and inputs. This variant has no trader run.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (CONTRACT_GRAPH, GRAPH, GRAPH_U12, PROC, TRADERS, load_config, part_sha256, read_parts,  # noqa: E402
                    require_committed, require_downloaded, save_json, write_parts)
from graphs import (in_union_graph, load_graphs, load_nodes, member_coverage, raw_degrees, score_all,  # noqa: E402
                    union_in_degree, union_pairs, union_sizes)
from labels import (UNION_NOTE, account_types, assert_contract_only, contract_members, label_split,  # noqa: E402
                    load_closes, spender_cohort, trader_labels)
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
# contract12m: the files this script needs committed besides common.EVAL_COMMITTED and the tables it reads; the other
# W0 labels that main() evaluates (run_robustness reads them); the baselines of revision section 9 at t1, and C-PR
# against the union in-degree on both labels.
COMMITTED_FILES = ("scripts/run_holdout.py", "scripts/run_same_window.py", "scripts/graphs.py", "scripts/scoring.py",
                   "scripts/stats.py", "scripts/labels.py")
GRAPH_STEMS = ("nodes", "allow_pairs_t1", "transfer_pairs_t1", "members", "label_split_w0")
U12_STEMS = ("labels_w0", "cohort_t1")
OTHER_LABELS = ["future_revoke_count", "future_drain_owners"]
BASELINES_T1 = ("t1_in_approve_degree", "t1_in_approve_value", "t1_in_degree", "t1_in_degree_union")
BASELINE_C12 = [
    ("C-PR minus t1 union in-degree", "cpr_l50", "t1_in_degree_union", APPR),
    ("C-PR minus t1 union in-degree", "cpr_l50", "t1_in_degree_union", SEND),
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


def frame_t1_c12(full: dict, ids: np.ndarray, g, union=None) -> pd.DataFrame:
    """contract12m: the scores at t1 and the four baselines of revision section 9 counted on the contract graph."""
    S = pd.DataFrame({m: scores_on(ids, s).to_numpy() for m, s in full.items()}, index=ids)
    deg = raw_degrees(g, ids)
    S["t1_in_approve_degree"] = deg["in_approve_degree"].to_numpy()
    S["t1_in_degree"] = deg["in_degree_other"].to_numpy()
    S["t1_in_approve_value"] = deg["in_approve_value"].to_numpy()
    S["t1_in_degree_union"] = union_in_degree(g, ids, union).to_numpy(dtype=np.float64)
    return S


def union_sensitivity(S: pd.DataFrame, lab: pd.DataFrame, inside: np.ndarray, labels: list[str], cfg: dict) -> dict:
    """The comparisons of the W0 summary repeated on the spenders inside the union graph at t1 (revision section 8):
    the same scores, a bootstrap of the subset; no verdict of rule A, and it decides no rule."""
    n = int(inside.sum())
    b, taus = evaluate(S.loc[inside], lab.loc[inside], labels, cfg)
    return {"n": n, "share": (n / inside.size) if inside.size else None, "note": UNION_NOTE, "taus": taus,
            "contrasts_prefixed": contrast_rows(b, PREFIXED), "contrasts_after": contrast_rows(b, AFTER),
            "baseline_contrasts": contrast_rows(b, BASELINE_C12)}


def main() -> int:
    if CONTRACT_GRAPH:
        prov = require_committed(*COMMITTED_FILES)
        inputs = require_downloaded(*GRAPH_STEMS)
    cfg = load_config()
    params = pagerank_params(cfg)
    nodes = load_nodes()
    addr = nodes.set_index("address")["id"]
    g = load_graphs("t1")

    if CONTRACT_GRAPH:
        typed = assert_contract_only(nodes, cfg)
        lab, counts = spender_cohort("w0", nodes)
        split = label_split("w0", lab)
        cohort_t1, counts_t1 = contract_members("cohort_t1", nodes)
        kind_counts = counts["by_class"]
    else:
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
    if CONTRACT_GRAPH:
        union = union_pairs(g)
        S = frame_t1_c12(full, ids, g, union)
    else:
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
    # The degree contrasts of EndorseRank and AWP (the registered run used these two; select them by name).
    deg = [s for s in AFTER if (s[1], s[2]) in (("endorserank", "t1_in_approve_degree"), ("awp", "t1_in_degree"))]
    contr_r = contrast_rows(boot_r, deg)

    no_transfer = S["awp"] == 0
    coverage = {
        "spenders_without_transfer_edge": int(no_transfer.sum()),
        "share_gaining_approvals_without": float((lab.loc[no_transfer, APPR] > 0).mean()) if no_transfer.any() else None,
        "share_gaining_approvals_with": float((lab.loc[~no_transfer, APPR] > 0).mean()),
        "share_gaining_senders_without": float((lab.loc[no_transfer, SEND] > 0).mean()) if no_transfer.any() else None,
        "share_gaining_senders_with": float((lab.loc[~no_transfer, SEND] > 0).mean()),
    }

    if TRADERS:
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
    else:
        hcfg = cfg["holdout"]

    if TRADERS:
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
    else:
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
        }
    if CONTRACT_GRAPH:
        inside = in_union_graph(g, ids, union)
        summary.update({
            "members": {"spenders_w0": counts, "cohort_t1": counts_t1},
            "baselines": list(BASELINES_T1),
            "baseline_contrasts": contrast_rows(boot, BASELINE_C12),
            "cohort_coverage": {"spenders_w0": member_coverage(g, ids, union),
                                "cohort_t1": member_coverage(g, cohort_t1.index.to_numpy(np.int64), union)},
            "union_graph": union_sizes(union),
            "in_union_graph": union_sensitivity(S, lab, inside, [APPR, SEND] + other, cfg),
            "label_split": split,
            "contract_only": typed,
            "provenance": {**prov, "inputs": inputs,
                           "inputs_twelve_month": {s: part_sha256(GRAPH_U12 / s) for s in U12_STEMS}},
        })
    save_json(summary, OUT / "eval_summary.json")
    if CONTRACT_GRAPH:
        scores = pd.concat([S, lab], axis=1)
        scores["in_union_graph"] = inside
        write_parts(scores.reset_index().rename(columns={"index": "id"}), OUT / "spender_scores")
    else:
        write_parts(pd.concat([S, lab], axis=1).reset_index().rename(columns={"index": "id"}), OUT / "spender_scores")
    if TRADERS:
        write_parts(pd.concat([St, tl], axis=1).reset_index().rename(columns={"index": "id"}), OUT / "trader_scores")
    print("rule A primary:", rule_a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
