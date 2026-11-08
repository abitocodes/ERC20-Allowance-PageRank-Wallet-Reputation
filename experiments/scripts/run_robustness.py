#!/usr/bin/env python3
"""Robustness and sensitivity checks for EndorseRank and AWP at T_obs.

1. Top-token subgraphs: both graphs rebuilt from twenty tokens (by summed raw amount
   and by rows, sql/11_top_tokens.sql); family means on the matched cohort.
2. Sample definition: the deterministic SHA256 stages of the runtime scaling
   (subsamples of the matched cohort; each stage keeps the edges incident to its
   contracts); family means on the stage's contracts. The stages differ in size and
   composition, so their coefficients are not comparable with the main table.
3. In the contract-graph variant (CONTRACT_REP_VARIANT=contract12m), the uncapped
   sensitivity of docs/revision_contract_graph.md section 5: the comparisons of
   the scores and baselines of section 9 on the W0 and W1 spender labels, on
   graphs whose allowance layer values each allowance at usd_allow in place of
   usd_eff, beside the main comparisons; it decides no rule. In that variant the
   script refuses to run unless it, the revision, the overlay, the base
   configuration and the project modules it imports are committed without local
   changes, unless the gate B tables it reads are those the download step
   verified, and unless the evaluation outputs it reads (same-window, holdout-w0,
   window-w1) record as their inputs the gate B tables of that download; it
   records the provenance of the code, the inputs and the evaluation outputs it
   reads.
Writes data/2-.../robustness/robustness.json.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (CONTRACT_GRAPH, GRAPH, GRAPH_U12, PROC, REVISED, W1_DIR, load_config, load_json,  # noqa: E402
                    part_sha256, read_parts, require_committed, require_downloaded, save_json)
from graphs import load_graphs, load_nodes, restrict  # noqa: E402
from run_benchmark import sha_order  # noqa: E402
from run_same_window import FAMILIES  # noqa: E402
from scoring import activeness, pagerank_params, scores_on, weighted_pagerank  # noqa: E402
from stats import kendall_tau_b  # noqa: E402

OUT = PROC / "robustness"
# contract12m: the files this script needs committed besides common.EVAL_COMMITTED, the tables it reads, and the
# freeze and evaluation folder of each label window of the uncapped sensitivity.
COMMITTED_FILES = ("scripts/run_robustness.py", "scripts/run_benchmark.py", "scripts/run_same_window.py",
                   "scripts/run_holdout.py", "scripts/run_registered.py", "scripts/graphs.py", "scripts/scoring.py",
                   "scripts/stats.py", "scripts/labels.py")
GRAPH_STEMS = ("nodes", "members", "allow_pairs_tobs", "transfer_pairs_tobs", "allow_pairs_t1", "transfer_pairs_t1",
               "allow_pairs_uncapped_tobs", "allow_pairs_uncapped_t1")
U12_STEMS = ("labels_w0", "labels_w1")
UNCAPPED_WINDOWS = {"w0": ("t1", "holdout-w0"), "w1": ("tobs", W1_DIR)}
# contract12m: the folders of the earlier evaluation outputs this script reads, with the script that writes each.
EARLIER_OUTPUTS = {"same-window": "run_same_window.py", "holdout-w0": "run_holdout.py", W1_DIR: "run_registered.py"}


def require_same_download() -> None:
    """contract12m: refuse unless each earlier evaluation output this script reads was computed from the gate B tables
    of the last verified download: the eval_summary.json of its folder records provenance inputs, and
    require_downloaded of the same stems gives exactly those parts (so proxies_tobs and the label splits too)."""
    for folder, script in EARLIER_OUTPUTS.items():
        path = PROC / folder / "eval_summary.json"
        rec = (load_json(path).get("provenance") or {}).get("inputs") if path.exists() else None
        if not rec:
            raise SystemExit(f"refused: {folder}/eval_summary.json records no gate B inputs (provenance.inputs); run "
                             f"scripts/{script} before scripts/run_robustness.py")
        if require_downloaded(*rec) != rec:
            raise SystemExit(f"refused: {folder} was computed from gate B tables other than those of the last "
                             f"download; run scripts/{script} again before scripts/run_robustness.py")


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


def uncapped_sensitivity(cfg: dict, params: dict, nodes: pd.DataFrame) -> dict:
    """Revision section 5: the comparisons of the scores and baselines of section 9 on the W0 and W1 labels, on graphs
    whose allowance layer is uncapped (allow_pairs_uncapped_{tag}: usd_allow in place of usd_eff) beside the same
    transfer layer; the spenders and their order are those of the main summaries, so the resamples pair with
    theirs. Every score, the raw degrees and the union in-degree are counted on the uncapped graph. It decides no
    rule, and the discovery-order test does not use it."""
    from graphs import score_all
    from labels import UNCAPPED_NOTE, spender_cohort
    from run_holdout import AFTER, BASELINE_C12, OTHER_LABELS, PREFIXED, contrast_rows, evaluate, frame_t1_c12
    from run_registered import APPR, SEND, W1_CONTRASTS, boot_for, frame_c12, named_contrasts

    nb, seed = cfg["alignment"]["bootstrap_resamples"], cfg["alignment"]["bootstrap_seed"]
    out: dict = {"note": UNCAPPED_NOTE}
    for window, (tag, folder) in UNCAPPED_WINDOWS.items():
        lab, _ = spender_cohort(window, nodes)
        ids = lab.index.to_numpy(np.int64)
        stem = PROC / folder / "spender_scores"
        try:
            main_ids = read_parts(stem, columns=["id"])["id"].to_numpy(np.int64)
        except FileNotFoundError:
            raise SystemExit(f"refused: {folder}/spender_scores is missing; the uncapped sensitivity is reported "
                             "beside the main comparisons, so run_holdout.py and run_registered.py run first") from None
        if not np.array_equal(main_ids, ids):
            raise SystemExit(f"refused: the {window.upper()} spender cohort differs from {folder}/spender_scores; run "
                             "the main evaluation again")
        capped = int(len(read_parts(GRAPH / f"allow_pairs_{tag}", columns=["src"])))
        g = load_graphs(tag, allow_stem="allow_pairs_uncapped")
        full, its = score_all(g, params)
        block = {"freeze": tag, "spenders": int(len(ids)),
                 "allowance_pairs": {"capped": capped, "uncapped": int(len(g.allow))}, "iterations": its}
        if window == "w0":
            S = frame_t1_c12(full, ids, g)
            b, taus = evaluate(S, lab, [APPR, SEND, *OTHER_LABELS], cfg)
            block.update(taus=taus, contrasts_prefixed=contrast_rows(b, PREFIXED),
                         contrasts_after=contrast_rows(b, AFTER), baseline_contrasts=contrast_rows(b, BASELINE_C12))
        else:
            S = frame_c12(full, ids, g)
            b = boot_for(S, lab, [APPR, SEND], nb, seed)
            block.update(spender_taus={m: {l: b.tau(m, l) for l in (APPR, SEND)} for m in S},
                         contrasts=named_contrasts(b, W1_CONTRASTS))
        out[window] = block
        print("uncapped", window, {"spenders": block["spenders"], **block["allowance_pairs"]}, flush=True)
    return out


def main() -> int:
    if CONTRACT_GRAPH:
        prov = require_committed(*COMMITTED_FILES)
        inputs = require_downloaded(*GRAPH_STEMS)
        require_same_download()
    cfg = load_config()
    params = pagerank_params(cfg)
    nodes = load_nodes()
    if CONTRACT_GRAPH:
        from labels import assert_contract_only
        typed = assert_contract_only(nodes, cfg)
    cohort = nodes.loc[nodes["is_cohort"], ["id", "address"]].sort_values("id").reset_index(drop=True)
    ids = cohort["id"].to_numpy(np.int64)
    P = read_parts(PROC / "same-window" / "cohort_scores").set_index("id").loc[ids]

    g = load_graphs("tobs")
    out = {}
    if REVISED:
        # The revised graphs already keep the listed tokens only; the check of the value weight is
        # its slope b, multiplied and divided by ten (sql/14_usd_anchor_pairs.sql writes both weights).
        slope = {"1": {"endorserank": family_means(P["endorserank"].to_numpy(), P),
                       "awp": family_means(P["awp"].to_numpy(), P)}}
        for tag in ("01x", "10x"):
            er, awp = er_awp(g.allow, g.transfer, params, w_a=f"w_er_b{tag}", w_t=f"w_awp_b{tag}")
            s_er, s_awp = scores_on(ids, er).to_numpy(), scores_on(ids, awp).to_numpy()
            slope[tag] = {"endorserank": family_means(s_er, P), "awp": family_means(s_awp, P),
                          "tau_with_main": {"endorserank": kendall_tau_b(s_er, P["endorserank"].to_numpy()),
                                            "awp": kendall_tau_b(s_awp, P["awp"].to_numpy())}}
            print("slope", tag, slope[tag], flush=True)
        out["value_slope"] = slope
    else:
        tok = read_parts(GRAPH / "top_token_pairs")
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
        toklist = pd.read_csv(GRAPH / "top_tokens.csv")
        tokens["shared_tokens"] = int((toklist["by_amount"] & toklist["by_rows"]).sum())
        out["top_tokens"] = tokens

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
    out["sample_definition"] = stages
    if CONTRACT_GRAPH:
        out["uncapped_allowances"] = uncapped_sensitivity(cfg, params, nodes)
        out["contract_only"] = typed
        out["provenance"] = {**prov, "inputs": inputs,
                             "inputs_twelve_month": {s: part_sha256(GRAPH_U12 / s) for s in U12_STEMS},
                             "evaluation_outputs_read": {f"{d}/{s}": part_sha256(PROC / d / s) for d, s in (
                                 ("same-window", "cohort_scores"), ("holdout-w0", "spender_scores"),
                                 (W1_DIR, "spender_scores"))}}
    save_json(out, OUT / "robustness.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
