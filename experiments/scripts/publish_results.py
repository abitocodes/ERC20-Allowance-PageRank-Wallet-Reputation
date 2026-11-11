#!/usr/bin/env python3
"""Publish the result summaries the thesis quotes, with checksums and a digest.

Copies every evaluation summary (same window, W0, W1), the Sybil model, the
robustness, benchmark and supplementary summaries when they exist, the small manifests of the
cohort, the GMX decoding and the W1 extraction, the configuration and the plan
documents into data/3-published-results-for-thesis/, keeping their folder names.
Writes results_digest.md, every number a chapter would quote grouped by section
with the JSON file and key it comes from, and SHA256SUMS.txt over all published
files. Computes no score and no statistic.

The contract-graph variant (CONTRACT_REP_VARIANT=contract12m) publishes its own set of files (the
four discovery runs and the structure pilot, the account-type and balance-check records, the
cohort lists, the two revision documents and the protocol) and a digest with its own sections;
it has no trader file. The digest is refused if it holds a word that the texts built on this
variant do not use (docs/revision_contract_graph.md sections 2 and 11).
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (CONTRACT_GRAPH, ONE_YEAR, PROC, PROC_SHARED, PUB, REVISED, ROOT, TYPES_DIR,  # noqa: E402
                    USD_CONSTANTS, USD_INPUTS, W1_DIR)

W1_SRC = f"{W1_DIR}/eval_summary.json"
# (published path, source)
FILES = [
    ("same-window/eval_summary.json", PROC / "same-window" / "eval_summary.json"),
    ("holdout-w0/eval_summary.json", PROC / "holdout-w0" / "eval_summary.json"),
    (W1_SRC, PROC / W1_DIR / "eval_summary.json"),
    ("registered-w1/extraction_manifest.json", PROC_SHARED / "registered-w1" / "extraction_manifest.json"),
    ("sybil-model/sybil_model.json", PROC / "sybil-model" / "sybil_model.json"),
    ("robustness/robustness.json", PROC / "robustness" / "robustness.json"),
    ("benchmark/benchmark.json", PROC / "benchmark" / "benchmark.json"),
    ("supplementary/supplementary.json", PROC / "supplementary" / "supplementary.json"),
    ("describe/describe.json", PROC / "describe" / "describe.json"),
    ("cohort/matched_cohort.json", PROC / "cohort" / "matched_cohort.json"),
    ("gmx/gmx_contract_closes_obs_decoded.json", PROC_SHARED / "gmx" / "gmx_contract_closes_obs_decoded.json"),
    ("gmx/gmx_contract_closes_w1_decoded.json", PROC_SHARED / "gmx" / "gmx_contract_closes_w1_decoded.json"),
    ("config/contract_reputation.yaml", ROOT / "config" / "contract_reputation.yaml"),
    ("docs/analysis_plan.md", ROOT / "docs" / "analysis_plan.md"),
    ("docs/registration_w1.md", ROOT / "docs" / "registration_w1.md"),
]
if REVISED:
    FILES += [
        ("docs/revision_price_weighting.md", ROOT / "docs" / "revision_price_weighting.md"),
        ("usd/listed_tokens.csv", USD_INPUTS / "listed_tokens.csv"),
        ("usd/usd_inputs.json", USD_INPUTS / "usd_inputs.json"),
        ("usd/constants.json", USD_CONSTANTS),
        ("usd/chainlink_check.json", USD_INPUTS / "chainlink_check.json"),
    ]
if ONE_YEAR:
    FILES += [
        ("docs/revision_one_year_window.md", ROOT / "docs" / "revision_one_year_window.md"),
        ("config/overlay_usd12m.yaml", ROOT / "config" / "overlay_usd12m.yaml"),
        ("usd/token_rows_12m.json", USD_INPUTS / "usd-12m" / "token_rows.json"),
        ("cohort/cohort_t1.json", PROC / "cohort" / "cohort_t1.json"),
        ("run_manifest.json", PROC / "run_manifest.json"),
    ]
DIGEST, SUMS = "results_digest.md", "SHA256SUMS.txt"

METHODS = {
    "endorserank": "EndorseRank",
    "endorserank_activity": "EndorseRank (activity restarts)",
    "awp": "AWP",
    "cpr_l100": "C-PR (λ=1)",
    "cpr_l0": "C-PR (λ=0)",
    "cpr_l25": "C-PR (λ=0.25)",
    "cpr_l50": "C-PR (λ=0.5)",
    "cpr_l75": "C-PR (λ=0.75)",
    "spr": "S-PR",
    "t1_in_approve_degree": "in-approve degree at t1",
    "t1_in_degree": "transfer in-degree at t1",
    "in_approve_degree": "in-approve degree at the freeze",
    "in_degree": "transfer in-degree at the freeze",
}
LABELS = {
    "future_new_approvers": "new approval pairs",
    "future_new_transfer_senders": "new transfer senders",
    "future_revoke_count": "revocations",
    "future_drain_owners": "drained owners",
    "liquidation_free_rate": "liquidation-free close rate",
    "no_liquidation": "no liquidation",
    "profitable_closes": "profitable closes",
    "realized_gain": "realized gain",
    "profitable_share": "profitable share",
    "non_loss_share": "non-loss share",
}
FAMILIES = {"transfer": "transfer", "allowance": "allowance", "sybil_stability": "Sybil stability"}
PAIRS = {
    "P": "P: in-approve degree minus transfer in-degree",
    "Q": "Q: EndorseRank (activity restarts) minus AWP",
    "layers": "C-PR (λ=1) minus C-PR (λ=0)",
    "er_awp": "EndorseRank minus AWP",
    "cpr0_awp": "C-PR (λ=0) minus AWP",
    "er_degree": "EndorseRank minus in-approve degree",
}


# --------------------------------------------------------------------------- formatting


def num(v, digits: int = 3) -> str:
    if v is None:
        return "None"
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, int):
        return f"{v:,}"
    v = float(v)
    if v != 0 and abs(v) < 1e-3:
        return f"{v:.4g}"
    if abs(v) >= 1e3:
        return f"{int(v):,}" if v.is_integer() else f"{v:,.1f}"
    return f"{v:.{digits}f}"


def tau(d: dict | None) -> str:
    if not d:
        return "None"
    point = d.get("kendall_tau", d.get("mean_tau"))
    out = f"{num(point)} [{num(d.get('ci_low'))}, {num(d.get('ci_high'))}]"
    if "spearman_rho" in d:
        out += f"; ρ {num(d['spearman_rho'])}"
    if d.get("n_boot") is not None:
        out += f"; B={d['n_boot']}"
    return out


def contrast(d: dict | None) -> str:
    if not d:
        return "None"
    out = (f"Δτ {num(d.get('delta_tau'))} [{num(d.get('ci_low'))}, {num(d.get('ci_high'))}]; "
           f"τa {num(d.get('a_tau'))}, τb {num(d.get('b_tau'))}")
    if d.get("ci975_low") is not None:
        out += f"; 97.5% [{num(d['ci975_low'])}, {num(d['ci975_high'])}]"
    if d.get("share_positive") is not None:
        out += f"; P(Δτ>0) {num(d['share_positive'])}"
    if d.get("n_boot") is not None:
        out += f"; B={d['n_boot']}"
    if "holds" in d:
        out += f"; {d.get('test')}: {'holds' if d['holds'] else 'fails'}"
    return out


def cell(text: str) -> str:
    return str(text).replace("|", "\\|")


class Digest:
    def __init__(self) -> None:
        self.lines: list[str] = []
        self.in_table = False

    def section(self, title: str) -> None:
        self.lines += ["", f"## {title}", ""]
        self.in_table = False

    def sub(self, title: str) -> None:
        self.lines += ["", f"### {title}", ""]
        self.in_table = False

    def note(self, text: str) -> None:
        if self.in_table:
            self.lines.append("")
        self.lines += [text, ""]
        self.in_table = False

    def row(self, quantity: str, value: str, src: str, key: str) -> None:
        if not self.in_table:
            self.lines += ["| Quantity | Value | Source |", "|---|---|---|"]
            self.in_table = True
        self.lines.append(f"| {cell(quantity)} | {cell(value)} | `{src}` : `{key}` |")


def get(d: dict, key: str):
    for part in key.split("."):
        if not isinstance(d, dict) or part not in d:
            return None
        d = d[part]
    return d


# --------------------------------------------------------------------------- sections


def sec_sizes(D: Digest, j: dict) -> None:
    D.section("1. Cohort and graph sizes")
    c, src = j.get("cohort/matched_cohort.json"), "cohort/matched_cohort.json"
    if c:
        D.row("Cohort rule", c.get("rule"), src, "rule")
        D.row("Candidate spenders", num(c.get("candidates")), src, "candidates")
        for k, v in (c.get("by_code_kind") or {}).items():
            D.row(f"Candidates by account type: {k}", num(v), src, f"by_code_kind.{k}")
        D.row("Matched cohort (contracts)", num(c.get("cohort")), src, "cohort")
        for k in ("registered_cohort", "left_out_of_registered"):
            if k in c:
                D.row(f"Revised cohort: {k.replace('_', ' ')}", num(c.get(k)), src, k)
    c, src = j.get("cohort/cohort_t1.json"), "cohort/cohort_t1.json"
    if c:
        D.row("W0 cohort rule", c.get("rule"), src, "rule")
        for k in ("cohort", "registered_cohort", "left_out_of_registered", "in_tobs_cohort"):
            D.row(f"W0 cohort: {k.replace('_', ' ')}", num(c.get(k)), src, k)
    s, src = j.get("same-window/eval_summary.json"), "same-window/eval_summary.json"
    if s:
        D.row("Anchor T_obs", s.get("anchor"), src, "anchor")
        D.row("Cohort scored in the same window", num(s.get("cohort")), src, "cohort")
        for layer in ("allowance", "transfer"):
            for k in ("nodes", "edges"):
                D.row(f"T_obs {layer} graph, {k}", num(get(s, f"graph.{layer}.{k}")), src, f"graph.{layer}.{k}")
        for k, name in (("cohort_outside_allowance", "Cohort contracts outside the allowance graph"),
                        ("cohort_outside_transfer", "Cohort contracts outside the transfer graph"),
                        ("cohort_outside_both", "Cohort contracts outside both graphs")):
            D.row(name, num(get(s, f"graph.{k}")), src, f"graph.{k}")
        for m, it in (s.get("iterations") or {}).items():
            D.row(f"Power iterations at T_obs, {METHODS.get(m, m)}", num(it), src, f"iterations.{m}")
    w0, src = j.get("holdout-w0/eval_summary.json"), "holdout-w0/eval_summary.json"
    if w0:
        for k in ("allowance_edges", "transfer_edges"):
            D.row(f"t1 graph, {k.replace('_', ' ')}", num(get(w0, f"graph.{k}")), src, f"graph.{k}")
        for m, it in (w0.get("iterations") or {}).items():
            D.row(f"Power iterations at t1, {METHODS.get(m, m)}", num(it), src, f"iterations.{m}")
    for tag in ("obs", "w1"):
        src = f"gmx/gmx_contract_closes_{tag}_decoded.json"
        g = j.get(src)
        if g:
            for k, v in g.items():
                D.row(f"GMX V2 contract closes ({tag}), {k.replace('_', ' ')}", num(v), src, k)
    m, src = j.get("registered-w1/extraction_manifest.json"), "registered-w1/extraction_manifest.json"
    if m:
        for k in ("started_at", "finished_at", "head", "registration_commit", "override_used"):
            D.row(f"W1 extraction: {k.replace('_', ' ')}", num(m.get(k)) if isinstance(m.get(k), bool) else m.get(k),
                  src, k)
        for f, h in (m.get("sha256") or {}).items():
            D.row(f"W1 extraction: SHA-256 of {f}", h, src, f"sha256.{f}")


def sec_same_window(D: Digest, s: dict) -> None:
    src = "same-window/eval_summary.json"
    D.section("2. Same-window families (matched cohort)")
    D.note("Family mean of Kendall τ_b with its 95% percentile interval (paired bootstrap over contracts).")
    for m, fams in (s.get("families") or {}).items():
        for f, d in fams.items():
            D.row(f"{METHODS.get(m, m)}, {FAMILIES.get(f, f)} family", tau(d), src, f"families.{m}.{f}")
    D.sub("Per proxy (τ_b [95% CI]; Spearman ρ)")
    for m, proxies in (s.get("per_proxy") or {}).items():
        for p, d in proxies.items():
            D.row(f"{METHODS.get(m, m)}, {p}", tau(d), src, f"per_proxy.{m}.{p}")


def sec_contrasts(D: Digest, s: dict) -> None:
    src = "same-window/eval_summary.json"
    D.section("3. Same-window contrasts, score agreement and rule A (secondary part)")
    for i, c in enumerate(s.get("contrasts") or []):
        D.row(f"[{c.get('group')}] {c.get('label')}", contrast(c), src, f"contrasts[{i}]")
    inter = s.get("inter_method") or {}
    D.row("EndorseRank vs AWP, τ_b", tau(inter.get("endorserank_vs_awp")), src, "inter_method.endorserank_vs_awp")
    D.row("EndorseRank vs AWP, isolated-node rule", tau(inter.get("isolated")), src, "inter_method.isolated")
    for k, v in (inter.get("concordance") or {}).items():
        D.row(f"Concordance: {k.replace('_', ' ')}", num(v), src, f"inter_method.concordance.{k}")
    rule = s.get("rule_a_secondary") or {}
    for fam in ("transfer", "allowance"):
        r = rule.get(fam) or {}
        D.row(f"Rule A secondary, {fam}: better layer {METHODS.get(r.get('best_layer'), r.get('best_layer'))}",
              f"C-PR {num(r.get('cpr'))} vs interval [{num((r.get('best_ci') or [None, None])[0])}, "
              f"{num((r.get('best_ci') or [None, None])[1])}]; pass: {num(r.get('pass'))}", src,
              f"rule_a_secondary.{fam}")
    r = rule.get("sybil_stability") or {}
    D.row("Rule A secondary, Sybil stability: C-PR above both layers",
          f"C-PR {num(r.get('cpr_l50'))}, λ=1 {num(r.get('cpr_l100'))}, λ=0 {num(r.get('cpr_l0'))}; "
          f"pass: {num(r.get('pass'))}", src, "rule_a_secondary.sybil_stability")
    D.row("Rule A secondary part met", num(rule.get("pass")), src, "rule_a_secondary.pass")


def sec_ties(D: Digest, s: dict, w0: dict | None) -> None:
    D.section("4. Ties and the isolated-node rule")
    src = "same-window/eval_summary.json"
    for m, t in (s.get("ties") or {}).items():
        D.row(f"{METHODS.get(m, m)} ties (same window)",
              f"distinct {num(t.get('distinct'))} of {num(t.get('n'))}; zeros {num(t.get('zeros'))}; largest block "
              f"{num(t.get('largest_block'))} at {num(t.get('largest_block_value'))}; share of pairs tied "
              f"{num(t.get('share_pairs_tied'), 4)}", src, f"ties.{m}")
    for m, fams in (s.get("isolated_rule") or {}).items():
        for f, d in fams.items():
            D.row(f"{m} (missing contracts as isolated nodes), {FAMILIES.get(f, f)}", tau(d), src,
                  f"isolated_rule.{m}.{f}")
    if w0:
        src = "holdout-w0/eval_summary.json"
        for m, t in (w0.get("ties") or {}).items():
            D.row(f"{METHODS.get(m, m)} ties (W0 spenders)",
                  f"distinct {num(t.get('distinct'))} of {num(t.get('n'))}; zeros {num(t.get('zeros'))}; largest "
                  f"block {num(t.get('largest_block'))} at {num(t.get('largest_block_value'))}; share of pairs tied "
                  f"{num(t.get('share_pairs_tied'), 4)}", src, f"ties.{m}")


def sec_closed_form(D: Digest, s: dict, w0: dict | None) -> None:
    D.section("5. Closed-form check of EndorseRank, s(v) = c (1 + d δ(v))")
    for src, d in (("same-window/eval_summary.json", s), ("holdout-w0/eval_summary.json", w0)):
        cf = (d or {}).get("closed_form") or {}
        for k, v in cf.items():
            D.row(f"{'Same window' if 'same' in src else 'W0'}: {k.replace('_', ' ')}", num(v, 4), src,
                  f"closed_form.{k}")


def sec_w0(D: Digest, w0: dict) -> None:
    src = "holdout-w0/eval_summary.json"
    D.section("6. Holdout W0 (scores at t1, labels April to June 2026)")
    D.row("Freeze t1", w0.get("freeze"), src, "freeze")
    D.row("Label window", " to ".join(w0.get("labels") or []), src, "labels")
    for k, v in (w0.get("spender_account_types") or {}).items():
        D.row(f"Spenders with a positive latest allowance at t1, account type {k}", num(v), src,
              f"spender_account_types.{k}")
    for k, name in (("spenders", "Spender cohort (contracts)"), ("gained_new_approvals", "Gained a new approval pair"),
                    ("gained_new_senders", "Gained a new transfer sender")):
        D.row(name, num(w0.get(k)), src, k)
    D.sub("W0 spenders: τ_b with every label")
    for m, labs in (w0.get("taus") or {}).items():
        for lab, d in labs.items():
            D.row(f"{METHODS.get(m, m)}, {LABELS.get(lab, lab)}", tau(d), src, f"taus.{m}.{lab}")
    D.sub("W0 contrasts")
    for block in ("contrasts_prefixed", "contrasts_after"):
        for i, c in enumerate(w0.get(block) or []):
            D.row(f"[{block}] {c.get('label')}, {LABELS.get(c.get('outcome'), c.get('outcome'))}", contrast(c), src,
                  f"{block}[{i}]")
    D.sub("Rule A, primary part")
    for k, v in (w0.get("rule_a_primary") or {}).items():
        D.row(f"Rule A primary: {k.replace('_', ' ')}", num(v), src, f"rule_a_primary.{k}")
    D.sub("Spenders that had received a transfer before t1")
    rec = w0.get("receiving") or {}
    D.row("Receiving subset (contracts)", num(rec.get("n")), src, "receiving.n")
    for m, labs in (rec.get("taus") or {}).items():
        for lab, d in labs.items():
            D.row(f"Receiving: {METHODS.get(m, m)}, {LABELS.get(lab, lab)}", tau(d), src, f"receiving.taus.{m}.{lab}")
    for i, c in enumerate(rec.get("contrasts") or []):
        D.row(f"Receiving: {c.get('label')}, {LABELS.get(c.get('outcome'), c.get('outcome'))}", contrast(c), src,
              f"receiving.contrasts[{i}]")
    D.sub("Coverage (AWP = 0 means no transfer edge)")
    for k, v in (w0.get("coverage") or {}).items():
        D.row(k.replace("_", " "), num(v), src, f"coverage.{k}")
    D.sub("W0 traders (exploratory)")
    tr = w0.get("traders") or {}
    D.row("Traders (GMX V2 contract accounts, ≥3 closes)", num(tr.get("n")), src, "traders.n")
    D.row("Traders that had received an approval by t1", num(tr.get("with_any_approval_received")), src,
          "traders.with_any_approval_received")
    for m, labs in (tr.get("taus") or {}).items():
        for lab, d in labs.items():
            D.row(f"Traders: {METHODS.get(m, m)}, {LABELS.get(lab, lab)}", tau(d), src, f"traders.taus.{m}.{lab}")


def sec_w1(D: Digest, w1: dict) -> None:
    src = W1_SRC
    D.section("7. Window W1 (scores at T_obs, labels July to September 2026; the rules registered for the "
              "raw-unit analysis, applied to the revised scores)" if REVISED else
              "7. Registered window W1 (scores at T_obs, labels July to September 2026)")
    for k, name in (("delta", "Margin δ"), ("spenders", "Spender cohort (contracts)"),
                    ("gained_new_approvals", "Gained a new approval pair"),
                    ("gained_new_senders", "Gained a new transfer sender"),
                    ("traders", "Traders (GMX V2 contract accounts, ≥3 closes)"),
                    ("traders_liquidated", "Traders with at least one liquidation"),
                    ("traders_all_liquidated", "Traders whose every close was a liquidation")):
        D.row(name, num(w1.get(k)), src, k)
    for block, title in (("rule_b", "Rule B (comparator C-PR λ=0)"),
                         ("sensitivity_awp", "Sensitivity 1 (comparator AWP)"),
                         ("sensitivity_isolated", "Sensitivity 2 (isolated nodes)")):
        D.sub(title)
        b = w1.get(block) or {}
        for k, v in b.items():
            D.row(f"{title}: {k}", contrast(v) if isinstance(v, dict) else num(v), src, f"{block}.{k}")
    D.sub("W1 spenders and traders: τ_b")
    for m, labs in (w1.get("spender_taus") or {}).items():
        for lab, d in labs.items():
            D.row(f"Spenders: {METHODS.get(m, m)}, {LABELS.get(lab, lab)}", tau(d), src, f"spender_taus.{m}.{lab}")
    for m, d in (w1.get("trader_taus") or {}).items():
        D.row(f"Traders: {METHODS.get(m, m)}, liquidation-free close rate", tau(d), src, f"trader_taus.{m}")
    D.sub("EndorseRank results (not part of rule B)")
    for k, v in (w1.get("endorserank_results") or {}).items():
        D.row(k.replace("_", " "), contrast(v), src, f"endorserank_results.{k}")
    D.sub("Comparison on outcomes built from neither edge type: rules R1-R3")
    for k, v in (w1.get("neutral_rules") or {}).items():
        D.row(f"Rule {k}", "holds" if v else "does not hold", src, f"neutral_rules.{k}")
    for key, window in (("neutral_w1", "W1"), ("neutral_w0", "W0")):
        nw = w1.get(key) or {}
        D.sub(f"Neutral labels, {window} (2,000 paired resamples)")
        D.row(f"{window} traders", num(nw.get("n")), src, f"{key}.n")
        D.row(f"{window} highest in-approve degree among traders", num(nw.get("max_in_approve_degree")), src,
              f"{key}.max_in_approve_degree")
        for pair, labs in (nw.get("grid") or {}).items():
            for lab, d in labs.items():
                D.row(f"{window} {PAIRS.get(pair, pair)}, {LABELS.get(lab, lab)}", contrast(d), src,
                      f"{key}.grid.{pair}.{lab}")
        for pair, d in (nw.get("stratified") or {}).items():
            D.row(f"{window} {PAIRS.get(pair, pair)}, stratified by closes", contrast(d), src,
                  f"{key}.stratified.{pair}")
        for grp, d in (nw.get("recipients") or {}).items():
            for k, v in d.items():
                D.row(f"{window} {grp}: {k.replace('_', ' ')}", num(v), src, f"{key}.recipients.{grp}.{k}")
        D.row(f"{window} P without the ten recipients of highest in-approve degree",
              contrast(nw.get("influence_without_top10")), src, f"{key}.influence_without_top10")
        for m, labs in (nw.get("taus") or {}).items():
            for lab, d in labs.items():
                D.row(f"{window} {METHODS.get(m, m)}, {LABELS.get(lab, lab)}", tau(d), src, f"{key}.taus.{m}.{lab}")


SUPP_NAMES = {
    "er_activity_minus_degree_appr": "EndorseRank (activity restarts) minus in-approve degree, new approval pairs",
    "er_activity_minus_er_appr": "EndorseRank (activity restarts) minus EndorseRank, new approval pairs",
    "er_activity_minus_er_send": "EndorseRank (activity restarts) minus EndorseRank, new transfer senders",
    "er_minus_awp_appr": "EndorseRank minus AWP, new approval pairs",
    "er_minus_awp_send": "EndorseRank minus AWP, new transfer senders",
}
SUPP_SCORES = {
    "l100": "C-PR (λ=1)", "l0": "C-PR (λ=0)", "er": "EndorseRank", "er_activity": "EndorseRank (activity restarts)",
    "awp": "AWP", "spr": "S-PR", "degree": "in-approve degree", "in_degree": "transfer in-degree",
}
SUPP_LABELS = {"appr": "new approval pairs", "send": "new transfer senders", "liq": "liquidation-free close rate"}
SUPP_NAMES.update({f"cpr_minus_{k}_{s}": f"C-PR minus {v}, {lab}" for k, v in SUPP_SCORES.items()
                   for s, lab in SUPP_LABELS.items()})
SUPP_NAMES.update({
    "recv_n": "Spenders that had received a transfer before the freeze",
    "recv_cpr_tau_appr": "Received a transfer: C-PR, new approval pairs",
    "recv_cpr_tau_send": "Received a transfer: C-PR, new transfer senders",
    "recv_cpr_minus_awp_appr": "Received a transfer: C-PR minus AWP, new approval pairs",
    "recv_cpr_minus_awp_send": "Received a transfer: C-PR minus AWP, new transfer senders",
    "recv_cpr_minus_degree_appr": "Received a transfer: C-PR minus in-approve degree, new approval pairs",
    "traders_n": "Traders",
    "cpr_minus_er_transfer": "Same window: C-PR minus EndorseRank, transfer family",
    "cpr_minus_awp_allowance": "Same window: C-PR minus AWP, allowance family",
})


def _walk(D: Digest, d, src: str, prefix: str) -> None:
    for k, v in d.items():
        key = f"{prefix}{k}"
        if isinstance(v, dict):
            _walk(D, v, src, key + ".")
        elif isinstance(v, list):
            continue
        else:
            D.row(key.replace("_", " "), num(v, 4) if isinstance(v, float) else (f"{v:,}" if isinstance(v, int) and
                  not isinstance(v, bool) else str(v)), src, key)


def sec_describe(D: Digest, z: dict) -> None:
    src = "describe/describe.json"
    D.section("Data description (token list, rows left out, amounts in USD, constants, prices, GMX contract "
              "traders, timing)" if REVISED else
              "Data description (amount shares, monthly counts, GMX contract traders, timing)")
    if REVISED:
        for part in ("rows", "amounts", "constants", "timing"):
            _walk(D, z.get(part) or {}, src, f"{part}.")
        D.row("listed tokens", num(z.get("listed_tokens")), src, "listed_tokens")
        D.sub("Listed tokens: rows of the registered and revised ego tables, USD volume")
        for i, t in enumerate(z.get("per_token") or []):
            D.row(f"{t.get('symbol')} {t.get('token')}",
                  f"registered approvals {num(t.get('reg_approvals'))}, transfers {num(t.get('reg_transfers'))}; "
                  f"revised approvals {num(t.get('rev_approvals'))}, transfers {num(t.get('rev_transfers'))}; "
                  f"transfer USD {num(t.get('rev_transfer_usd'))}; without price "
                  f"{num(t.get('rev_transfers_without_price'))}", src, f"per_token[{i}]")
        D.sub("Daily prices per listed token")
        for i, t in enumerate(z.get("prices") or []):
            D.row(f"{t.get('symbol')} {t.get('address')}",
                  f"days {num(t.get('days'))}, filled {num(t.get('filled_days'))}, first {t.get('first_day')}, "
                  f"min confidence {num(t.get('min_confidence'))}", src, f"prices[{i}]")
        pdays = z.get("price_days")  # twelve-month variant: the days its windows cover
        if pdays:
            D.sub(f"Daily prices of the selected tokens from {pdays.get('first_day')} to {pdays.get('last_day')}")
            for i, t in enumerate(pdays.get("per_token") or []):
                D.row(f"{t.get('symbol')} {t.get('address')}",
                      f"days {num(t.get('days'))}, second key {num(t.get('second_key_days'))}, filled "
                      f"{num(t.get('filled_days'))}, one-day errors {num(t.get('spike_days'))}", src,
                      f"price_days.per_token[{i}]")
            cl = z.get("chainlink_check_in_windows") or {}
            for sym, v in (cl.get("per_token") or {}).items():
                D.row(f"Chainlink check on those days, {sym}", f"{num(v.get('n'))} dates, median "
                      f"{num(v.get('median'))}, largest {num(v.get('max'))} (absolute relative difference)",
                      src, f"chainlink_check_in_windows.per_token.{sym}")
        for r in z["gmx_contract_traders_by_quarter"]:
            D.row(f"GMX contract traders {r['quarter']}", f"{r['closes']:,} closes, {r['accounts']:,} accounts, "
                  f"{int(r['liquidations']):,} liquidations", src, "gmx_contract_traders_by_quarter")
        for r in z["monthly_counts"]:
            D.row(f"{r['stream']} {r['month']}", f"{int(r['n']):,}", src, "monthly_counts")
        return
    for k, v in z["amounts"].items():
        D.row(k.replace("_", " "), num(v, 4) if isinstance(v, float) else f"{v:,}", src, f"amounts.{k}")
    for k, v in z["timing"].items():
        val = v if not isinstance(v, dict) else ", ".join(f"{a} {b}" for a, b in v.items())
        D.row(k.replace("_", " "), str(val), src, f"timing.{k}")
    for r in z["gmx_contract_traders_by_quarter"]:
        D.row(f"GMX contract traders {r['quarter']}", f"{r['closes']:,} closes, {r['accounts']:,} accounts, "
              f"{int(r['liquidations']):,} liquidations", src, "gmx_contract_traders_by_quarter")
    for r in z["monthly_counts"]:
        D.row(f"{r['stream']} {r['month']}", f"{int(r['n']):,}", src, "monthly_counts")


def sec_token_rows(D: Digest, z: dict) -> None:
    """Twelve-month variant: rows of the listed tokens in the T_obs score window (sql/20), reported only."""
    src = "usd/token_rows_12m.json"
    D.section("Token rows of the T_obs score window (reported; the five selected tokens are kept)")
    for k in ("selected", "top_priced_by_rows", "same_as_selected", "tokens_in_window", "rows_in_window"):
        v = z.get(k)
        D.row(k.replace("_", " "), ", ".join(v) if isinstance(v, list) else num(v), src, k)
    for i, t in enumerate(z.get("per_listed_token") or []):
        if t.get("priced") and (t.get("rank_by_rows") or 99) <= 10:
            D.row(f"{t.get('rank_by_rows')}. {t.get('symbol')}", f"{num(t.get('rows_total'))} rows "
                  f"({num(t.get('transfers'))} transfers, {num(t.get('latest_allowances'))} latest allowances)"
                  + ("; selected" if t.get("selected") else ""), src, f"per_listed_token[{i}]")


def sec_supplementary(D: Digest, sup: dict) -> None:
    src = "supplementary/supplementary.json"
    D.sub("Supplementary spender contrasts (computed after the labels were known, outside every rule)")
    for window, d in sup.items():
        for k, v in d.items():
            if isinstance(v, dict):
                val = contrast(v) if "delta_tau" in v else tau(v)
                D.row(f"{window.upper()} {SUPP_NAMES.get(k, k)}", val, src, f"{window}.{k}")
            else:
                D.row(f"{window.upper()} {SUPP_NAMES.get(k, k)}", num(v), src, f"{window}.{k}")


def sec_sybil(D: Digest, y: dict) -> None:
    src = "sybil-model/sybil_model.json"
    D.section("8. Sybil cost model (EndorseRank graph at T_obs)")

    def walk(d, prefix=""):
        for k, v in d.items():
            key = f"{prefix}{k}"
            if isinstance(v, dict):
                walk(v, key + ".")
            else:
                D.row(key.replace("_", " "), num(v, 4), src, key)

    walk(y)
    farm = y.get("farm_size_to_reach_cohort_quantile") or {}
    negative = [q for q, d in farm.items() if (d.get("farm_addresses") or 0) < 0]
    if negative:
        D.note(f"Note: farm_addresses is negative at {', '.join(negative)}: the closed form gives a negative farm "
               "size when the quantile score is already reached with no farm, so read it as zero addresses. This key "
               "is not written by the current scripts/sybil_model.py.")


def sec_robustness(D: Digest, s: dict | None, rob: dict | None) -> None:
    D.section("9. Robustness")
    if s:
        src = "same-window/eval_summary.json"
        for name, d in (s.get("damping") or {}).items():
            D.row(f"Damping {name}: iterations", num(d.get("iterations")), src, f"damping.{name}.iterations")
            for f in FAMILIES:
                D.row(f"Damping {name}: {FAMILIES[f]} family", tau(d.get(f)), src, f"damping.{name}.{f}")
    if rob:
        src = "robustness/robustness.json"
        for v, d in (rob.get("value_slope") or {}).items():
            for m, fam in d.items():
                if m == "tau_with_main":
                    for mm, t in fam.items():
                        D.row(f"Slope {v}: {METHODS.get(mm, mm)} rank agreement with the main score", num(t), src,
                              f"value_slope.{v}.tau_with_main.{mm}")
                    continue
                for f, t in fam.items():
                    D.row(f"Slope {v}: {METHODS.get(m, m)}, {FAMILIES.get(f, f)}", num(t), src,
                          f"value_slope.{v}.{m}.{f}")
        tok = rob.get("top_tokens") or {}
        for lst, d in tok.items():
            if not isinstance(d, dict):
                D.row(f"Top tokens: {lst.replace('_', ' ')}", num(d), src, f"top_tokens.{lst}")
                continue
            for m, v in d.items():
                if isinstance(v, dict):
                    for f, t in v.items():
                        D.row(f"Top tokens {lst}: {METHODS.get(m, m)}, {FAMILIES.get(f, f)}", num(t), src,
                              f"top_tokens.{lst}.{m}.{f}")
                else:
                    D.row(f"Top tokens {lst}: {m.replace('_', ' ')}", num(v), src, f"top_tokens.{lst}.{m}")
        for i, st in enumerate(rob.get("sample_definition") or []):
            for m in ("endorserank", "awp"):
                for f, t in (st.get(m) or {}).items():
                    D.row(f"Stage n={num(st.get('n'))}: {METHODS[m]}, {FAMILIES.get(f, f)}", num(t), src,
                          f"sample_definition[{i}].{m}.{f}")
            for k in ("allowance_edges", "transfer_edges"):
                D.row(f"Stage n={num(st.get('n'))}: {k.replace('_', ' ')}", num(st.get(k)), src,
                      f"sample_definition[{i}].{k}")
    else:
        D.note("robustness/robustness.json does not exist yet.")


def _bench_row(D: Digest, title: str, d: dict, src: str, key: str) -> None:
    runs = ", ".join(num(r) for r in d.get("runs_s") or [])
    D.row(title, f"mean {num(d.get('mean_s'))} s, SD {num(d.get('sd_s'))} s; runs {runs}; peak {num(d.get('peak_mb'), 1)} "
                 f"MB; iterations {num(d.get('iterations'))}; |V| {num(d.get('nodes'))}; |E| {num(d.get('edges'))}",
          src, key)


def sec_benchmark(D: Digest, b: dict | None) -> None:
    D.section("10. Benchmark")
    if not b:
        D.note("benchmark/benchmark.json does not exist yet.")
        return
    src = "benchmark/benchmark.json"
    for k, v in (b.get("protocol") or {}).items():
        D.row(f"Protocol: {k.replace('_', ' ')}", f"{v:g}" if isinstance(v, float) else num(v), src, f"protocol.{k}")
    for k, v in (b.get("machine") or {}).items():
        D.row(f"Machine: {k}", v, src, f"machine.{k}")
    D.row("Scaling seed", b.get("scaling_seed"), src, "scaling_seed")
    main = b.get("main") or {}
    for m, d in main.items():
        _bench_row(D, f"Full graphs: {METHODS.get(m, m)}", d, src, f"main.{m}")
    er, awp = main.get("endorserank") or {}, main.get("awp") or {}
    if er.get("mean_s") and er.get("edges"):
        D.row("AWP/EndorseRank runtime ratio (derived)", num(awp["mean_s"] / er["mean_s"], 2), src,
              "main.awp.mean_s / main.endorserank.mean_s")
        D.row("AWP/EndorseRank edge ratio (derived)", num(awp["edges"] / er["edges"], 2), src,
              "main.awp.edges / main.endorserank.edges")
    for d, rows in (b.get("damping") or {}).items():
        for m, r in rows.items():
            _bench_row(D, f"Damping {d}: {METHODS.get(m, m)}", r, src, f"damping.{d}.{m}")
    for i, st in enumerate(b.get("scaling") or []):
        reused = " (reused main measurement)" if st.get("reused_main") else ""
        for m in ("endorserank", "awp"):
            if st.get(m):
                _bench_row(D, f"Stage n={num(st.get('n'))}{reused}: {METHODS[m]}", st[m], src, f"scaling[{i}].{m}")


# --------------------------------------------------------------------------- main


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args: str) -> str:
    try:
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return ""


def uncommitted_code() -> list[str]:
    """Paths under scripts/, config/, docs/ and sql/ that differ from the commit, relative to experiments/."""
    prefix = git("rev-parse", "--show-prefix").strip()
    out = []
    for line in git("status", "--porcelain", "--", "scripts", "config", "docs", "sql").splitlines():
        path = line[3:].strip().strip('"')
        out.append(f"{path[len(prefix):] if prefix and path.startswith(prefix) else path} ({line[:2].strip()})")
    return out


# --------------------------------------------------------------------------- the contract-graph variant


C12_DISCOVERY = ("tobs_both", "tobs_out", "t1_both", "t1_out")
C12_ORDERINGS = {
    "bfs": "breadth-first", "random": "random", "ib_a": "IB′_A (allowance backlinks)",
    "ib_t": "IB′_T (transfer backlinks)", "ib_u": "IB′_U (contract backlinks)", "endorserank": "EndorseRank′",
    "endorserank_activity": "EndorseRank-activity′", "awp": "AWP′", "cpr_l50": "C-PR′ (λ=0.5)",
    "cpr_l25": "C-PR′ (λ=0.25)", "cpr_l75": "C-PR′ (λ=0.75)", "cpr_l100": "C-PR′ (λ=1)", "cpr_l0": "C-PR′ (λ=0)",
    "spr": "S-PR′", "delta": "δ′ (diagnostic)", "ref_cpr": "reference: C-PR of the full graph",
    "ref_ib_u": "reference: union in-degree of the full graph", "ref_ideal": "reference: ideal order",
    "random_curve": "reference: random curve", "ideal_curve": "reference: ideal curve",
}
C12_HOT = {
    "i_t@q": "H_q(I_T)", "i_a@q": "H_q(I_A)", "n_t@q": "H_q(N_T)", "n_a@q": "H_q(N_A)", "ib_u@q": "H_q(IB_U)",
    "ir@q": "H_q(IR)", "i_t@q2": "H_q2(I_T)", "i_a@q2": "H_q2(I_A)", "i_t@q-nohubs": "H_q(I_T) without hubs",
    "i_a@q-nohubs": "H_q(I_A) without hubs",
}
C12_METHODS = {**METHODS, "t1_in_approve_value": "in-approve value at t1", "t1_in_degree_union": "union in-degree at t1",
               "in_approve_value": "in-approve value at the freeze", "in_degree_union": "union in-degree at the freeze"}
C12_SUPP_NAMES = {
    **SUPP_NAMES,
    "cpr_minus_approve_value_appr": "C-PR minus in-approve value, new approval pairs",
    "cpr_minus_approve_value_send": "C-PR minus in-approve value, new transfer senders",
}
# Words that the texts built on this variant do not use (docs/revision_contract_graph.md sections 2 and 11); the
# digest of this variant is checked for them before it is written.
C12_FORBIDDEN = re.compile(r"GMX|\btraders?\b|liquidat|rule B (?:is )?met\b|\bregistered results?\b", re.I)


def c12_files() -> list[tuple[str, Path]]:
    """(published path, source) of the contract-graph variant."""
    usd, c12 = USD_INPUTS, USD_INPUTS / "contract-12m"
    files = [
        ("same-window/eval_summary.json", PROC / "same-window" / "eval_summary.json"),
        ("holdout-w0/eval_summary.json", PROC / "holdout-w0" / "eval_summary.json"),
        (W1_SRC, PROC / W1_DIR / "eval_summary.json"),
        *((f"discovery/discovery_{k}.json", PROC / "discovery" / f"discovery_{k}.json") for k in C12_DISCOVERY),
        ("discovery/feasibility_t1.json", PROC / "discovery" / "feasibility_t1.json"),
        ("sybil-model/sybil_model.json", PROC / "sybil-model" / "sybil_model.json"),
        ("robustness/robustness.json", PROC / "robustness" / "robustness.json"),
        ("benchmark/benchmark.json", PROC / "benchmark" / "benchmark.json"),
        ("supplementary/supplementary.json", PROC / "supplementary" / "supplementary.json"),
        ("describe/describe.json", PROC / "describe" / "describe.json"),
        *((f"cohort/{n}.json", PROC / "cohort" / f"{n}.json")
          for n in ("matched_cohort", "cohort_t1", "spenders_w0", "spenders_w1")),
        ("typing/balance_audit.json", PROC / "typing" / "balance_audit.json"),
        ("typing/c12_account_types.json", TYPES_DIR / "c12_account_types.json"),
        ("typing/c12_smart_account_reads.json", TYPES_DIR / "c12_smart_account_reads.json"),
        ("run_manifest.json", PROC / "run_manifest.json"),
        ("config/contract_reputation.yaml", ROOT / "config" / "contract_reputation.yaml"),
        ("config/overlay_contract12m.yaml", ROOT / "config" / "overlay_contract12m.yaml"),
        *((f"docs/{n}.md", ROOT / "docs" / f"{n}.md")
          for n in ("analysis_plan", "registration_w1", "revision_price_weighting", "revision_one_year_window",
                    "revision_contract_graph", "discovery_protocol")),
        ("usd/listed_tokens.csv", usd / "listed_tokens.csv"),
        ("usd/usd_inputs.json", usd / "usd_inputs.json"),
        ("usd/constants.json", c12 / "constants.json"),
        ("usd/chainlink_check.json", usd / "chainlink_check.json"),
    ]
    return files


def c12_stat(d: dict | None) -> str:
    """A discovery contrast: point [95% interval]; share of resamples above 0."""
    if not d or d.get("point") is None:
        return "None"
    return (f"{d['point']:+.4f} [{d['lo']:+.4f}, {d['hi']:+.4f}]; share of resamples above 0 "
            f"{num(d.get('share_positive'))}")


def sec_c12_sizes(D: Digest, j: dict) -> None:
    D.section("1. Data, account types, cohorts and graph sizes")
    z, src = j.get("describe/describe.json") or {}, "describe/describe.json"
    for k, v in (z.get("events") or {}).items():
        D.row(f"Events: {k.replace('_', ' ')}", num(v), src, f"events.{k}")
    at = z.get("account_types") or {}
    for k in ("block", "addresses", "aborted_addresses", "audit_senders_with_code"):
        D.row(f"Account types: {k.replace('_', ' ')}", str(at.get(k)) if k == "block" else num(at.get(k)), src,
              f"account_types.{k}")
    for k in ("read_from", "read_until"):
        D.row(f"Account types: {k.replace('_', ' ')}", str(at.get(k)), src, f"account_types.{k}")
    for part in ("code_kind", "typed", "wallet_kind_typed", "proxy_kind", "extension", "after_extension",
                 "wallet_kind_after_extension"):
        for k, v in (at.get(part) or {}).items():
            D.row(f"Account types, {part.replace('_', ' ')}: {k}", num(v), src, f"account_types.{part}.{k}")
    for k, v in (z.get("nodes") or {}).items():
        D.row(f"Nodes of the contract graph: {k.replace('_', ' ')}", num(v), src, f"nodes.{k}")
    for tag in ("tobs", "t1"):
        for layer, d in ((z.get("pairs") or {}).get(tag) or {}).items():
            for k, v in d.items():
                D.row(f"Pairs at {tag}, {layer.replace('_', ' ')}: {k.replace('_', ' ')}", num(v), src,
                      f"pairs.{tag}.{layer}.{k}")
    for name in ("matched_cohort", "cohort_t1", "spenders_w0", "spenders_w1"):
        c, src = j.get(f"cohort/{name}.json"), f"cohort/{name}.json"
        if not c:
            continue
        D.row(f"{name}: rule", c.get("rule"), src, "rule")
        for k in ("listed", "cohort", "contracts_in_nodes"):
            D.row(f"{name}: {k.replace('_', ' ')}", num(c.get(k)), src, k)
        for part in ("by_class", "user_accounts_by_source"):
            for k, v in (c.get(part) or {}).items():
                D.row(f"{name}, {part.replace('_', ' ')}: {k}", num(v), src, f"{part}.{k}")
    s, src = j.get("same-window/eval_summary.json"), "same-window/eval_summary.json"
    if s:
        D.row("Anchor T_obs", s.get("anchor"), src, "anchor")
        D.row("Cohort scored in the same window", num(s.get("cohort")), src, "cohort")
        for layer in ("allowance", "transfer"):
            for k in ("nodes", "edges"):
                D.row(f"T_obs {layer} graph (pairs of positive weight), {k}", num(get(s, f"graph.{layer}.{k}")), src,
                      f"graph.{layer}.{k}")
        for k, name in (("cohort_outside_allowance", "Cohort contracts outside the allowance graph"),
                        ("cohort_outside_transfer", "Cohort contracts outside the transfer graph"),
                        ("cohort_outside_both", "Cohort contracts outside both graphs")):
            D.row(name, num(get(s, f"graph.{k}")), src, f"graph.{k}")
        for k, v in (s.get("union_graph") or {}).items():
            D.row(f"T_obs union graph, {k}", num(v), src, f"union_graph.{k}")
        for m, it in (s.get("iterations") or {}).items():
            D.row(f"Power iterations at T_obs, {METHODS.get(m, m)}", num(it), src, f"iterations.{m}")
    w0, src = j.get("holdout-w0/eval_summary.json"), "holdout-w0/eval_summary.json"
    if w0:
        for k in ("allowance_edges", "transfer_edges"):
            D.row(f"t1 graph, {k.replace('_', ' ')}", num(get(w0, f"graph.{k}")), src, f"graph.{k}")
        for k, v in (w0.get("union_graph") or {}).items():
            D.row(f"t1 union graph, {k}", num(v), src, f"union_graph.{k}")
        for m, it in (w0.get("iterations") or {}).items():
            D.row(f"Power iterations at t1, {METHODS.get(m, m)}", num(it), src, f"iterations.{m}")


def sec_c12_coverage(D: Digest, summary: dict | None, src: str, title: str) -> None:
    """Cohort coverage of one summary (revision section 8)."""
    for name, cov in ((summary or {}).get("cohort_coverage") or {}).items():
        D.sub(f"{title}: where the members of {name} lie in the contract graph")
        D.row(f"{name}: members", num(cov.get("n")), src, f"cohort_coverage.{name}.n")
        for k, v in cov.items():
            if isinstance(v, dict):
                D.row(f"{name}: {k.replace('_', ' ')}", f"{num(v.get('n'))} ({num(v.get('share'))})", src,
                      f"cohort_coverage.{name}.{k}")


def sec_c12_label_split(D: Digest, summary: dict | None, src: str, window: str) -> None:
    ls = (summary or {}).get("label_split") or {}
    if not ls:
        return
    D.sub(f"{window} labels by the class of the counted account (a description outside every rule)")
    for k, v in (ls.get("owners_at_freeze") or {}).items():
        D.row(f"{window} owners at the freeze: {k.replace('_', ' ')}", num(v), src, f"label_split.owners_at_freeze.{k}")
    for lab, d in (ls.get("labels") or {}).items():
        for k, v in d.items():
            D.row(f"{window} {LABELS.get(lab, lab.replace('future_', '').replace('_', ' '))}: {k.replace('_', ' ')}",
                  f"{v:.4g}" if isinstance(v, float) and abs(v) >= 1e15 else num(v), src,
                  f"label_split.labels.{lab}.{k}")


def sec_c12_in_union(D: Digest, summary: dict | None, src: str, window: str) -> None:
    iu = (summary or {}).get("in_union_graph") or {}
    if not iu:
        return
    D.sub(f"{window}: comparisons on the members inside the union graph only (decides no rule)")
    D.row(f"{window} members inside the union graph", f"{num(iu.get('n'))} ({num(iu.get('share'))})", src,
          "in_union_graph.n")
    for key in ("taus", "spender_taus"):
        for m, labs in (iu.get(key) or {}).items():
            for lab, d in labs.items():
                D.row(f"Inside the union graph: {C12_METHODS.get(m, m)}, {LABELS.get(lab, lab)}", tau(d), src,
                      f"in_union_graph.{key}.{m}.{lab}")
    for m, proxies in (iu.get("per_proxy") or {}).items():
        for p, d in proxies.items():
            D.row(f"Inside the union graph: {C12_METHODS.get(m, m)}, {p}", tau(d), src,
                  f"in_union_graph.per_proxy.{m}.{p}")
    for m, fams in (iu.get("families") or {}).items():
        for f, d in fams.items():
            D.row(f"Inside the union graph: {C12_METHODS.get(m, m)}, {FAMILIES.get(f, f)} family", tau(d), src,
                  f"in_union_graph.families.{m}.{f}")
    for block in ("contrasts_prefixed", "contrasts_after", "baseline_contrasts"):
        for i, c in enumerate(iu.get(block) or []) if isinstance(iu.get(block), list) else []:
            D.row(f"Inside the union graph [{block}]: {c.get('label')}, "
                  f"{LABELS.get(c.get('outcome'), c.get('outcome'))}", contrast(c), src, f"in_union_graph.{block}[{i}]")
    c = iu.get("contrasts")
    if isinstance(c, dict):
        for k, v in c.items():
            D.row(f"Inside the union graph: {k.replace('_', ' ')}", contrast(v), src, f"in_union_graph.contrasts.{k}")
    elif isinstance(c, list):
        for i, v in enumerate(c):
            D.row(f"Inside the union graph: [{v.get('group')}] {v.get('label')}", contrast(v), src,
                  f"in_union_graph.contrasts[{i}]")
    rule = iu.get("rule_a_secondary")
    if isinstance(rule, dict):
        D.row("Inside the union graph: rule A secondary part would be met (decides no rule)", num(rule.get("pass")),
              src, "in_union_graph.rule_a_secondary.pass")


def sec_c12_w0(D: Digest, w0: dict) -> None:
    src = "holdout-w0/eval_summary.json"
    D.section("6. Holdout W0 (scores at t1 on the contract graph, labels April to June 2026)")
    D.row("Freeze t1", w0.get("freeze"), src, "freeze")
    D.row("Label window", " to ".join(w0.get("labels") or []), src, "labels")
    for k, v in (w0.get("spender_account_types") or {}).items():
        D.row(f"Listed spenders of the twelve-month labels, class {k}", num(v), src, f"spender_account_types.{k}")
    for k, name in (("spenders", "Spender cohort (contracts)"), ("gained_new_approvals", "Gained a new approval pair"),
                    ("gained_new_senders", "Gained a new transfer sender")):
        D.row(name, num(w0.get(k)), src, k)
    D.sub("W0 spenders: τ_b with every label (scores and the baselines counted on the contract graph)")
    for m, labs in (w0.get("taus") or {}).items():
        for lab, d in labs.items():
            D.row(f"{C12_METHODS.get(m, m)}, {LABELS.get(lab, lab)}", tau(d), src, f"taus.{m}.{lab}")
    D.sub("W0 contrasts")
    for block in ("contrasts_prefixed", "contrasts_after", "baseline_contrasts"):
        for i, c in enumerate(w0.get(block) or []):
            D.row(f"[{block}] {c.get('label')}, {LABELS.get(c.get('outcome'), c.get('outcome'))}", contrast(c), src,
                  f"{block}[{i}]")
    D.sub("Rule A, primary part")
    for k, v in (w0.get("rule_a_primary") or {}).items():
        D.row(f"Rule A primary: {k.replace('_', ' ')}", num(v), src, f"rule_a_primary.{k}")
    D.sub("Spenders that another contract had paid before t1")
    rec = w0.get("receiving") or {}
    D.row("Receiving subset (contracts)", num(rec.get("n")), src, "receiving.n")
    for m, labs in (rec.get("taus") or {}).items():
        for lab, d in labs.items():
            D.row(f"Receiving: {C12_METHODS.get(m, m)}, {LABELS.get(lab, lab)}", tau(d), src,
                  f"receiving.taus.{m}.{lab}")
    for i, c in enumerate(rec.get("contrasts") or []):
        D.row(f"Receiving: {c.get('label')}, {LABELS.get(c.get('outcome'), c.get('outcome'))}", contrast(c), src,
              f"receiving.contrasts[{i}]")
    D.sub("Coverage (AWP = 0 means no transfer edge)")
    for k, v in (w0.get("coverage") or {}).items():
        D.row(k.replace("_", " "), num(v), src, f"coverage.{k}")
    sec_c12_coverage(D, w0, src, "W0")
    sec_c12_in_union(D, w0, src, "W0")
    sec_c12_label_split(D, w0, src, "W0")


def sec_c12_w1(D: Digest, w1: dict) -> None:
    src = W1_SRC
    D.section("7. Window W1 (scores at T_obs on the contract graph, labels July to September 2026; two of the "
              "registered criteria of rule B, F1 and F2, applied as a re-analysis)")
    D.note("Under the registration rule B holds only if each of its criteria holds. This analysis applies F1 and F2 "
           "only, so it reports \"not met\" when one of them fails and \"both applied criteria hold\" when both hold "
           "(docs/revision_contract_graph.md section 11).")
    D.row("Margin δ", num(w1.get("delta")), src, "delta")
    D.row("Applied criteria", ", ".join(w1.get("applied_criteria") or []), src, "applied_criteria")
    for k, v in (w1.get("spender_account_types") or {}).items():
        D.row(f"Listed spenders of the twelve-month labels, class {k}", num(v), src, f"spender_account_types.{k}")
    for k, name in (("spenders", "Spender cohort (contracts)"), ("gained_new_approvals", "Gained a new approval pair"),
                    ("gained_new_senders", "Gained a new transfer sender")):
        D.row(name, num(w1.get(k)), src, k)
    for block, title in (("rule_b", "F1 and F2, two of rule B's registered criteria (comparator C-PR λ=0)"),
                         ("sensitivity_awp", "Sensitivity 1 (comparator AWP)"),
                         ("sensitivity_isolated", "Sensitivity 2 (members a graph leaves out as isolated nodes)")):
        D.sub(title)
        b = w1.get(block) or {}
        for k in ("F1", "F2", "F6a", "F6b"):
            if k in b:
                D.row(f"{k}", contrast(b[k]), src, f"{block}.{k}")
        if "f1_f2_hold" in b:
            D.row("Both applied criteria (F1 and F2) hold", num(b.get("f1_f2_hold")), src, f"{block}.f1_f2_hold")
        if "rule_b_reading" in b:
            D.row("Reading", str(b.get("rule_b_reading")), src, f"{block}.rule_b_reading")
        if "F6" in b:
            D.row("F6 (both parts hold)", num(b.get("F6")), src, f"{block}.F6")
    D.sub("W1 spenders: τ_b (scores and the baselines counted on the contract graph)")
    for m, labs in (w1.get("spender_taus") or {}).items():
        for lab, d in labs.items():
            D.row(f"Spenders: {C12_METHODS.get(m, m)}, {LABELS.get(lab, lab)}", tau(d), src,
                  f"spender_taus.{m}.{lab}")
    D.sub("Sensitivity 2: τ_b with the members left out added as isolated nodes")
    for m, labs in (get(w1, "sensitivity_isolated.spender_taus") or {}).items():
        for lab, d in labs.items():
            D.row(f"Isolated nodes: {C12_METHODS.get(m, m)}, {LABELS.get(lab, lab)}", tau(d), src,
                  f"sensitivity_isolated.spender_taus.{m}.{lab}")
    D.sub("EndorseRank results and the union in-degree baseline (outside F1 and F2)")
    for block in ("endorserank_results", "baseline_contrasts"):
        for k, v in (w1.get(block) or {}).items():
            D.row(k.replace("_", " "), contrast(v), src, f"{block}.{k}")
    sec_c12_coverage(D, w1, src, "W1")
    sec_c12_in_union(D, w1, src, "W1")
    sec_c12_label_split(D, w1, src, "W1")


def sec_c12_supplementary(D: Digest, sup: dict) -> None:
    src = "supplementary/supplementary.json"
    D.sub("Supplementary spender contrasts (computed after the labels were known, outside every rule)")
    if sup.get("note"):
        D.note(str(sup["note"]))
    for window in ("w0", "w1", "same"):
        for k, v in (sup.get(window) or {}).items():
            name = f"{window.upper()} {C12_SUPP_NAMES.get(k, k)}"
            if isinstance(v, dict):
                D.row(name, contrast(v) if "delta_tau" in v else tau(v), src, f"{window}.{k}")
            else:
                D.row(name, num(v), src, f"{window}.{k}")


def sec_c12_discovery(D: Digest, j: dict) -> None:
    D.section("11. Discovery-order test (docs/discovery_protocol.md)")
    D.note("Defined after the registered results were known; it decides no rule of the plan or the registration. "
           "The decision is read at the T_obs freeze in the primary mode only (`decides` true); the other three runs "
           "carry no verdict. AUC is AUC_x of protocol section 6 with x = 10% unless a row says otherwise; contrasts "
           "read `point [95% interval]; share of resamples above 0`.")
    for name in C12_DISCOVERY:
        src = f"discovery/discovery_{name}.json"
        d = j.get(src)
        if not d:
            continue
        title = f"{d.get('window')}, mode {d.get('mode')}" + (" (the decision)" if d.get("decides") else "")
        D.sub(f"Run {title}")
        for k in ("decides", "is_primary", "primary_mode", "created_at", "seconds", "workers"):
            D.row(f"{title}: {k.replace('_', ' ')}", num(d.get(k)) if not isinstance(d.get(k), str) else d.get(k), src, k)
        for k in ("rho", "q", "q_secondary", "decision_covers"):
            D.row(f"{title}: protocol {k}", str(get(d, f"protocol.{k}")), src, f"protocol.{k}")
        D.row(f"{title}: code revision", str(get(d, "provenance.head")), src, "provenance.head")
        for part in ("graph", "universe"):
            for k, v in (get(d, f"sizes.{part}") or {}).items():
                if not isinstance(v, (dict, list)):
                    D.row(f"{title}: sizes of the {part}, {k}", num(v), src, f"sizes.{part}.{k}")
        for k, v in (d.get("hot_sets") or {}).items():
            D.row(f"{title}: contracts in {C12_HOT.get(k, k)}", num(v), src, f"hot_sets.{k}")
        dec = d.get("decision") or {}
        for imp in ("i_t", "i_a"):
            v = dec.get(imp) or {}
            name_imp = "I_T" if imp == "i_t" else "I_A"
            D.row(f"{title}: D1 = C-PR′ − BFS on H_q({name_imp})", c12_stat(v.get("D1")), src, f"decision.{imp}.D1")
            D.row(f"{title}: D2 = C-PR′ − IB′_U on H_q({name_imp})", c12_stat(v.get("D2")), src, f"decision.{imp}.D2")
            if d.get("decides"):
                D.row(f"{title}: verdict on {name_imp}", str(v.get("verdict")), src, f"decision.{imp}.verdict")
            else:
                D.row(f"{title}: contrasts on {name_imp} with the interval above 0",
                      ", ".join(v.get("above_zero") or []) or "none", src, f"decision.{imp}.above_zero")
                D.row(f"{title}: contrasts on {name_imp} with the interval below 0",
                      ", ".join(v.get("below_zero") or []) or "none", src, f"decision.{imp}.below_zero")
        for i, st in enumerate(dec.get("statements") or []):
            D.row(f"{title}: statement {i + 1}", st, src, f"decision.statements[{i}]")
        for hot in ("i_t@q", "i_a@q"):
            for o, v in (get(d, f"auc.{hot}") or {}).items():
                a = v.get("x=0.1") if isinstance(v, dict) else None
                if isinstance(a, dict) and a.get("auc") is not None:
                    val = f"{a['auc']:.4f}"
                    if a.get("lo") is not None:
                        val += f" [{a['lo']:.4f}, {a['hi']:.4f}]"
                    if a.get("seed_min") is not None:
                        val += f"; seeds {a['seed_min']:.4f} to {a['seed_max']:.4f}"
                    D.row(f"{title}: AUC of {C12_ORDERINGS.get(o, o)} on {C12_HOT[hot]}", val, src,
                          f"auc.{hot}.{o}.x=0.1")
                elif isinstance(a, (int, float)):
                    D.row(f"{title}: AUC of {C12_ORDERINGS.get(o, o)} on {C12_HOT[hot]}", f"{a:.4f}", src,
                          f"auc.{hot}.{o}.x=0.1")
        fo = d.get("fixed_order") or {}
        for key, label in (("1_walk_vs_count", "1 walk′ against its count"), ("2_walk_contrasts", "2 among walks")):
            for i, x in enumerate(fo.get(key) or []):
                D.row(f"{title}: [{label}] {C12_ORDERINGS.get(x.get('a'), x.get('a'))} − "
                      f"{C12_ORDERINGS.get(x.get('b'), x.get('b'))} on {C12_HOT.get(x.get('hot_set'), x.get('hot_set'))}",
                      c12_stat(x), src, f"fixed_order.{key}[{i}]")
        for m, hs in (fo.get("3_lambda") or {}).items():
            for h, v in hs.items():
                for k, lab in (("D1", "D1"), ("D2", "D2"), ("vs_cpr_l50", "minus C-PR′ (λ=0.5)")):
                    D.row(f"{title}: [3 λ] {C12_ORDERINGS.get(m, m)} {lab} on {C12_HOT.get(h, h)}", c12_stat(v.get(k)),
                          src, f"fixed_order.3_lambda.{m}.{h}.{k}")
        cho = fo.get("4_cho") or {}
        for h, v in (cho.get("hot_sets") or {}).items():
            for k in ("D1", "D2"):
                D.row(f"{title}: [4 Cho] {k} on {C12_HOT.get(h, h)}", c12_stat(v.get(k)), src,
                      f"fixed_order.4_cho.hot_sets.{h}.{k}")
        D.row(f"{title}: [4 Cho] replication contrast C-PR′ − IB′_U on H_q(IB_U)",
              c12_stat(cho.get("replication_contrast")), src, "fixed_order.4_cho.replication_contrast")
        sens = fo.get("5_sensitivities") or {}
        for xk, hs in (sens.get("x") or {}).items():
            for h, v in hs.items():
                for k in ("D1", "D2"):
                    D.row(f"{title}: [5 sensitivity {xk}] {k} on {C12_HOT.get(h, h)}", c12_stat(v.get(k)), src,
                          f"fixed_order.5_sensitivities.x.{xk}.{h}.{k}")
        for block, label in (("q_secondary", "secondary q"), ("no_hubs", "no hubs"),
                             ("importance_counts", "importance by counts"), ("seed_bootstrap", "seed bootstrap")):
            b = sens.get(block) or {}
            for h, v in b.items():
                if not isinstance(v, dict) or "D1" not in v:
                    D.row(f"{title}: [5 sensitivity {label}] {h}", num(v) if not isinstance(v, list) else num(len(v)),
                          src, f"fixed_order.5_sensitivities.{block}.{h}")
                    continue
                for k in ("D1", "D2"):
                    D.row(f"{title}: [5 sensitivity {label}] {k} on {C12_HOT.get(h, h)}", c12_stat(v.get(k)), src,
                          f"fixed_order.5_sensitivities.{block}.{h}.{k}")
        rq = sens.get("rho_quarter") or {}
        if rq:
            D.row(f"{title}: [5 sensitivity ρ/4] ρ and seeds", f"{rq.get('rho')}, {num(rq.get('seeds'))} seeds", src,
                  "fixed_order.5_sensitivities.rho_quarter")
            for h, v in (rq.get("contrasts") or {}).items():
                for k in ("D1", "D2"):
                    D.row(f"{title}: [5 sensitivity ρ/4] {k} on {C12_HOT.get(h, h)}", c12_stat(v.get(k)), src,
                          f"fixed_order.5_sensitivities.rho_quarter.contrasts.{h}.{k}")
        dg = d.get("diagnostics") or {}
        for o, v in (dg.get("ties") or {}).items():
            D.row(f"{title}: share of picks decided by a tie, {C12_ORDERINGS.get(o, o)}", num(v, 4), src,
                  f"diagnostics.ties.{o}")
        for o, v in (dg.get("wasted_visits") or {}).items():
            D.row(f"{title}: wasted visits of {C12_ORDERINGS.get(o, o)} (first 1%, first 10%)",
                  f"{num(v.get('first_1pct'), 4)}, {num(v.get('first_10pct'), 4)}", src,
                  f"diagnostics.wasted_visits.{o}")
        hubs = dg.get("hubs") or []
        D.row(f"{title}: hubs", num(len(hubs)), src, "diagnostics.hubs")
        if hubs:
            D.row(f"{title}: largest hub", f"{hubs[0].get('address')} with IB_U {num(hubs[0].get('ib_u'))}", src,
                  "diagnostics.hubs[0]")
        for o, v in (dg.get("hub_visits") or {}).items():
            means = sorted(v.get("mean") or [])
            if means:
                D.row(f"{title}: median over hubs of the mean visit index, {C12_ORDERINGS.get(o, o)}",
                      num(float(means[len(means) // 2])), src, f"diagnostics.hub_visits.{o}.mean")
        cov = dg.get("coverage") or {}
        for k in ("contracts", "outside_g", "inflow_untyped_usd"):
            D.row(f"{title}: coverage, {k.replace('_', ' ')}", num(cov.get(k)), src, f"diagnostics.coverage.{k}")
        for imp in ("i_t", "i_a"):
            c = cov.get(imp) or {}
            D.row(f"{title}: coverage of {imp.upper()}, total (USD)", num(c.get("total")), src,
                  f"diagnostics.coverage.{imp}.total")
            D.row(f"{title}: coverage of {imp.upper()}, share held by the universe", num(c.get("share_U"), 4), src,
                  f"diagnostics.coverage.{imp}.share_U")
            for part, v in (c.get("share_by_part") or {}).items():
                D.row(f"{title}: coverage of {imp.upper()}, share in {part.replace('_', ' ')}", num(v, 4), src,
                      f"diagnostics.coverage.{imp}.share_by_part.{part}")
            for k, v in (c.get("top_1pct") or {}).items():
                D.row(f"{title}: coverage of {imp.upper()}, top 1% of rows: {k.replace('_', ' ')}", num(v, 4), src,
                      f"diagnostics.coverage.{imp}.top_1pct.{k}")
        for k, v in (d.get("runs") or {}).items():
            D.row(f"{title}: crawls of {k}", f"{num(v.get('crawls'))} crawls, {num(v.get('seconds'))} s, "
                  f"{num(v.get('recomputes'))} recomputes, {num(v.get('solves'))} solves, {num(v.get('iterations'))} "
                  "iterations (means per crawl but the seconds)", src, f"runs.{k}")
        for k, v in (d.get("invariants") or {}).items():
            D.row(f"{title}: invariant {k.replace('_', ' ')}", f"{v:.3g}" if isinstance(v, float) else num(v), src,
                  f"invariants.{k}")
    f, src = j.get("discovery/feasibility_t1.json"), "discovery/feasibility_t1.json"
    if f:
        D.sub("Structure pilot at t1 (before any score; protocol section 7)")
        for k in ("U", "E_U", "WCC", "E_WCC", "rho", "q", "primary_mode", "stopped"):
            D.row(f"Pilot: {k}", num(f.get(k)) if not isinstance(f.get(k), str) else f.get(k), src, k)
        for layer, v in (f.get("layers") or {}).items():
            for k, x in v.items():
                D.row(f"Pilot: {layer.replace('_', ' ')} {k.replace('_', ' ')}", num(x), src, f"layers.{layer}.{k}")
        for k, v in (f.get("bow_tie") or {}).items():
            D.row(f"Pilot: bow-tie {k}", num(v), src, f"bow_tie.{k}")
        for k, v in (f.get("capped_allowance_in_edge_share") or {}).items():
            D.row(f"Pilot: share with a capped allowance in-edge, {k}", num(v, 4), src,
                  f"capped_allowance_in_edge_share.{k}")
        for k, v in (get(f, "rules.projected_hours") or {}).items():
            D.row(f"Pilot: projected hours at ρ = {k}", num(v, 2), src, f"rules.projected_hours.{k}")
        for k, v in (get(f, "rules.stop") or {}).items():
            D.row(f"Pilot: stop flag {k.replace('_', ' ')}", num(v), src, f"rules.stop.{k}")


def sec_c12_sybil(D: Digest, y: dict) -> None:
    src = "sybil-model/sybil_model.json"
    D.section("8. Sybil cost model (EndorseRank graph of contracts at T_obs)")
    if y.get("note"):
        D.note(str(y["note"]))

    def walk(d, prefix=""):
        for k, v in d.items():
            key = f"{prefix}{k}"
            if key in ("provenance", "note", "balance_threshold"):
                continue
            if isinstance(v, dict):
                walk(v, key + ".")
            elif isinstance(v, str):
                D.row(key.replace("_", " "), v, src, key)
            else:
                D.row(key.replace("_", " "), num(v, 4), src, key)

    walk(y)
    D.sub("Sensitivity to a balance threshold θ (pairs whose capped value is at least θ)")
    for th, x in (y.get("balance_threshold") or {}).items():
        def rows(d, prefix):
            for k, v in d.items():
                key = f"{prefix}{k}"
                if isinstance(v, dict):
                    rows(v, key + ".")
                else:
                    D.row(f"θ = USD {th}: {key.split('.', 2)[-1].replace('_', ' ')}", num(v, 4), src, key)
        rows(x, f"balance_threshold.{th}.")


def sec_c12_uncapped(D: Digest, rob: dict | None) -> None:
    unc = (rob or {}).get("uncapped_allowances") or {}
    if not unc:
        return
    src = "robustness/robustness.json"
    D.sub("Uncapped allowance layer (sensitivity; decides no rule)")
    for w, d in unc.items():
        if not isinstance(d, dict):
            continue
        W = w.upper()
        for k, v in (d.get("allowance_pairs") or {}).items():
            D.row(f"{W}: allowance pairs, {k}", num(v), src, f"uncapped_allowances.{w}.allowance_pairs.{k}")
        for key in ("taus", "spender_taus"):
            for m, labs in (d.get(key) or {}).items():
                for lab, t in labs.items():
                    D.row(f"{W} uncapped: {C12_METHODS.get(m, m)}, {LABELS.get(lab, lab)}", tau(t), src,
                          f"uncapped_allowances.{w}.{key}.{m}.{lab}")
        for block in ("contrasts_prefixed", "contrasts_after", "baseline_contrasts"):
            for i, c in enumerate(d.get(block) or []):
                D.row(f"{W} uncapped [{block}]: {c.get('label')}, {LABELS.get(c.get('outcome'), c.get('outcome'))}",
                      contrast(c), src, f"uncapped_allowances.{w}.{block}[{i}]")
        for k, c in (d.get("contrasts") or {}).items() if isinstance(d.get("contrasts"), dict) else []:
            D.row(f"{W} uncapped: {k.replace('_', ' ')}", contrast(c), src, f"uncapped_allowances.{w}.contrasts.{k}")


def sec_c12_describe(D: Digest, z: dict, j: dict) -> None:
    src = "describe/describe.json"
    D.section("12. Allowances and the balance cap, importance, balance check, constants, prices, cost")
    for tag in ("tobs", "t1"):
        a = (z.get("allowances") or {}).get(tag) or {}
        for k, v in (a.get("total") or {}).items():
            D.row(f"Latest allowances between contracts at {tag}, all five tokens: {k.replace('_', ' ')}",
                  f"{v:.4g}" if isinstance(v, float) and abs(v) >= 1e15 else num(v, 4), src,
                  f"allowances.{tag}.total.{k}")
        for i, t in enumerate(a.get("per_token") or []):
            D.row(f"Latest allowances between contracts at {tag}, {t.get('symbol')}",
                  f"positive {num(t.get('n_latest_positive'))}; positive after the cap {num(t.get('n_positive_eff'))}; "
                  f"capped to zero {num(t.get('n_capped_to_zero'))}; capped below the allowance "
                  f"{num(t.get('n_capped_below_allowance'))}; unlimited {num(t.get('n_unlimited'))}; capped value at "
                  f"or above U {num(t.get('n_eff_at_or_above_cap'))}; sum of the capped values USD "
                  f"{num(t.get('sum_usd_eff'))}", src, f"allowances.{tag}.per_token[{i}]")
        for k, v in ((z.get("importance") or {}).get(tag) or {}).items():
            D.row(f"Importance at {tag}: {k.replace('_', ' ')}", num(v), src, f"importance.{tag}.{k}")
    for k, v in (z.get("anchor_blocks") or {}).items():
        D.row(f"Last block at or before the anchor {k}", str(v), src, f"anchor_blocks.{k}")
    for k, v in (z.get("balance_check") or {}).items():
        D.row(f"Balance check: {k.replace('_', ' ')}", str(v) if k in ("block", "mode") else num(v, 4), src,
              f"balance_check.{k}")
    a, asrc = j.get("typing/balance_audit.json") or {}, "typing/balance_audit.json"
    for i, c in enumerate(a.get("per_cell") or []):
        D.row(f"Balance check cell {c.get('token')} {c.get('cell')}",
              f"{num(c.get('n'))} pairs, {num(c.get('judged'))} judged, match {num(c.get('match'), 4)}", asrc,
              f"per_cell[{i}]")
    _walk(D, z.get("constants") or {}, src, "constants.")
    _walk(D, z.get("timing") or {}, src, "timing.")
    pdays = z.get("price_days")
    if pdays:
        D.sub(f"Daily prices of the five tokens from {pdays.get('first_day')} to {pdays.get('last_day')}")
        for i, t in enumerate(pdays.get("per_token") or []):
            D.row(f"{t.get('symbol')} {t.get('address')}",
                  f"days {num(t.get('days'))}, second key {num(t.get('second_key_days'))}, filled "
                  f"{num(t.get('filled_days'))}, one-day errors {num(t.get('spike_days'))}", src,
                  f"price_days.per_token[{i}]")
        cl = z.get("chainlink_check_in_windows") or {}
        for sym, v in (cl.get("per_token") or {}).items():
            D.row(f"Chainlink check on those days, {sym}", f"{num(v.get('n'))} dates, median "
                  f"{num(v.get('median'))}, largest {num(v.get('max'))} (absolute relative difference)",
                  src, f"chainlink_check_in_windows.per_token.{sym}")


def sec_c12_decisions(D: Digest, m: dict | None) -> None:
    """Author's decisions recorded in the run manifest (revision section 13, last paragraph of the gate B entry)."""
    src = "run_manifest.json"
    D.section("13. Decisions recorded in the run manifest")
    steps = (m or {}).get("steps") or []
    before = [(i, e) for i, e in enumerate(steps) if e.get("author_decision") and not e.get("gate_b")]
    after = [(i, e) for i, e in enumerate(steps) if e.get("author_decision") and e.get("gate_b")]
    for i, e in before:
        D.row(f"Decision before gate B, step {e.get('step')} started {e.get('started_at')}",
              str(e.get("author_decision")), src, f"steps[{i}].author_decision")
        if e.get("waited_for"):
            D.row(f"What the step {e.get('step')} would have waited for", "; ".join(e["waited_for"]), src,
                  f"steps[{i}].waited_for")
    if after:
        for i, e in after:
            D.row(f"Decision after gate B, step {e.get('step')} started {e.get('started_at')}",
                  str(e.get("author_decision")), src, f"steps[{i}].author_decision")
    else:
        D.note("No step of gate B ran with an author's decision taken after gate B.")
    gate_b = next((e for e in steps if e.get("gate_b")), None)
    pf = (gate_b or {}).get("gate_b", {}).get("protocol_fixed") or {}
    if pf:
        D.row("Decision in \"Protocol fixed\" (taken before gate B)", str(pf.get("author_decision")), src,
              "steps[].gate_b.protocol_fixed.author_decision")
    chk = ((m or {}).get("results") or {}).get("checks") or {}
    checks = chk.get("checks") or {}
    D.row("Invariants of sql/42 (each a count of violations)", f"{num(len(checks))} invariants, sum "
          f"{num(sum(int(v) for v in checks.values()))}", src, "results.checks.checks")


def main_contract() -> int:
    """Publish the contract-graph variant: its files, the digest and the checksums (see the module docstring)."""
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, help="publish into this folder instead (verification runs)")
    pub = ap.parse_args().out or PUB
    pub.mkdir(parents=True, exist_ok=True)
    published: list[str] = []
    missing: list[str] = []
    for dest, src in c12_files():
        if not src.exists():
            missing.append(dest)
            continue
        out = pub / dest
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, out)
        published.append(dest)
    j = {d: json.loads((pub / d).read_text(encoding="utf-8")) for d in published if d.endswith(".json")}

    head = git("rev-parse", "HEAD").strip()
    dirty = uncommitted_code()
    D = Digest()
    D.lines += [
        "# Results digest",
        "",
        f"Written by `experiments/scripts/publish_results.py` on {dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M} UTC "
        "from the summaries in this folder; nothing here is recomputed. Each row names the file (relative to this "
        "folder) and the key inside it. τ entries read `point [95% CI]`, contrasts `Δτ [95% CI]; τa, τb; P(Δτ>0)`, "
        "and `B` is the number of bootstrap resamples behind the interval. `SHA256SUMS.txt` lists the checksums of "
        "every file published here.",
        "",
        "**Contract-graph analysis** (docs/revision_contract_graph.md and docs/discovery_protocol.md, on top of "
        "docs/revision_one_year_window.md and docs/revision_price_weighting.md): graphs whose nodes are contracts "
        "other than smart accounts, with edges read from the whole chain; amounts in USD over the five selected "
        "tokens; scores from the twelve months before each freeze (T_obs and W1: 2025-07-01 to 2026-06-30; W0: "
        "2025-04-01 to 2026-03-31); each allowance counted up to its owner's balance at the freeze; constants set on "
        "the contract graph; and the discovery-order test. All of it was defined after the registered results were "
        "known, so every result here is post hoc. Nothing in this digest is a registered result; the registered "
        "digest is in the parent folder.",
        "",
        f"- Code revision: `{head or 'unknown'}`"
        + (" with uncommitted changes (git status code) in: " + ", ".join(f"`{p}`" for p in dirty) if dirty else ""),
        "- Published files: " + ", ".join(f"`{p}`" for p in published),
    ]
    if missing:
        D.lines.append("- Not yet available: " + ", ".join(f"`{p}`" for p in missing))
    s = j.get("same-window/eval_summary.json")
    w0 = j.get("holdout-w0/eval_summary.json")
    w1 = j.get(W1_SRC)
    sec_c12_sizes(D, j)
    if s:
        sec_same_window(D, s)
        sec_contrasts(D, s)
        sec_c12_coverage(D, s, "same-window/eval_summary.json", "Same window")
        sec_c12_in_union(D, s, "same-window/eval_summary.json", "Same window")
        sec_ties(D, s, w0)
        sec_closed_form(D, s, w0)
    if w0:
        sec_c12_w0(D, w0)
    if w1:
        sec_c12_w1(D, w1)
    if j.get("supplementary/supplementary.json"):
        sec_c12_supplementary(D, j["supplementary/supplementary.json"])
    if j.get("sybil-model/sybil_model.json"):
        sec_c12_sybil(D, j["sybil-model/sybil_model.json"])
    sec_robustness(D, s, j.get("robustness/robustness.json"))
    sec_c12_uncapped(D, j.get("robustness/robustness.json"))
    sec_benchmark(D, j.get("benchmark/benchmark.json"))
    sec_c12_discovery(D, j)
    if j.get("describe/describe.json"):
        sec_c12_describe(D, j["describe/describe.json"], j)
    sec_c12_decisions(D, j.get("run_manifest.json"))
    text = "\n".join(D.lines) + "\n"
    bad = sorted({m.group(0) for m in C12_FORBIDDEN.finditer(
        text.replace("Nothing in this digest is a registered result", "")
            .replace("defined after the registered results were known", "")
            .replace("Defined after the registered results were known", ""))})
    if bad:
        raise SystemExit(f"refused: the digest of the contract-graph variant holds {bad}")
    (pub / DIGEST).write_text(text, encoding="utf-8")
    published.append(DIGEST)

    lines = [f"{sha256(pub / p)}  {p}" for p in sorted(published)]
    (pub / SUMS).write_text("\n".join(lines) + "\n", encoding="utf-8")

    known = set(published) | {SUMS}
    stale = sorted(p.relative_to(pub).as_posix() for p in pub.rglob("*") if p.is_file()
                   and p.relative_to(pub).as_posix() not in known)
    print(f"published {len(published)} files to {pub}")
    if missing:
        print("not yet available:", ", ".join(missing))
    if stale:
        print("files in the folder that this run did not publish:", ", ".join(stale))
    return 0


def main() -> int:
    if CONTRACT_GRAPH:
        return main_contract()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, help="publish into this folder instead (verification runs)")
    pub = ap.parse_args().out or PUB
    pub.mkdir(parents=True, exist_ok=True)
    published: list[str] = []
    missing: list[str] = []
    for dest, src in FILES:
        if not src.exists():
            missing.append(dest)
            continue
        out = pub / dest
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, out)
        published.append(dest)
    j = {d: json.loads((pub / d).read_text(encoding="utf-8")) for d in published if d.endswith(".json")}

    head = git("rev-parse", "HEAD").strip()
    dirty = uncommitted_code()
    D = Digest()
    D.lines += [
        "# Results digest",
        "",
        f"Written by `experiments/scripts/publish_results.py` on {dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M} UTC "
        "from the summaries in this folder; nothing here is recomputed. Each row names the file (relative to this "
        "folder) and the key inside it. τ entries read `point [95% CI]`, contrasts `Δτ [95% CI]; τa, τb; P(Δτ>0)`, "
        "and `B` is the number of bootstrap resamples behind the interval. `SHA256SUMS.txt` lists the checksums of "
        "every file published here.",
        "",
        *(["**Revised analysis, twelve-month score windows** (docs/revision_one_year_window.md on top of "
           "docs/revision_price_weighting.md): amounts in USD over the five selected tokens, scores from the twelve "
           "months before each freeze (T_obs and W1: 2025-07-01 to 2026-06-30; W0: 2025-04-01 to 2026-03-31), "
           "decided after the registered results were known. Nothing in this digest is a registered result; the "
           "registered digest is in the parent folder.", ""] if ONE_YEAR else
          ["**Revised analysis** (docs/revision_price_weighting.md): amounts in USD over the listed tokens, decided "
           "after the registered results were known. Nothing in this digest is a registered result; the registered "
           "digest is in the parent folder.", ""] if REVISED else []),
        f"- Code revision: `{head or 'unknown'}`"
        + (" with uncommitted changes (git status code) in: " + ", ".join(f"`{p}`" for p in dirty) if dirty else ""),
        "- Published files: " + ", ".join(f"`{p}`" for p in published),
    ]
    if missing:
        D.lines.append("- Not yet available: " + ", ".join(f"`{p}`" for p in missing))
    s = j.get("same-window/eval_summary.json")
    w0 = j.get("holdout-w0/eval_summary.json")
    w1 = j.get(W1_SRC)
    sec_sizes(D, j)
    if s:
        sec_same_window(D, s)
        sec_contrasts(D, s)
        sec_ties(D, s, w0)
        sec_closed_form(D, s, w0)
    if w0:
        sec_w0(D, w0)
    if w1:
        sec_w1(D, w1)
    if j.get("supplementary/supplementary.json"):
        sec_supplementary(D, j["supplementary/supplementary.json"])
    if j.get("sybil-model/sybil_model.json"):
        sec_sybil(D, j["sybil-model/sybil_model.json"])
    sec_robustness(D, s, j.get("robustness/robustness.json"))
    sec_benchmark(D, j.get("benchmark/benchmark.json"))
    if j.get("describe/describe.json"):
        sec_describe(D, j["describe/describe.json"])
    if j.get("usd/token_rows_12m.json"):
        sec_token_rows(D, j["usd/token_rows_12m.json"])
    (pub / DIGEST).write_text("\n".join(D.lines) + "\n", encoding="utf-8")
    published.append(DIGEST)

    lines = [f"{sha256(pub / p)}  {p}" for p in sorted(published)]
    (pub / SUMS).write_text("\n".join(lines) + "\n", encoding="utf-8")

    known = set(published) | {SUMS}
    stale = sorted(p.relative_to(pub).as_posix() for p in pub.rglob("*") if p.is_file()
                   and p.relative_to(pub).as_posix() not in known
                   and not p.relative_to(pub).as_posix().startswith(("revised-usd/", "revised-usd-12m/")))
    print(f"published {len(published)} files to {pub}")
    if missing:
        print("not yet available:", ", ".join(missing))
    if stale:
        print("files in the folder that this run did not publish:", ", ".join(stale))
    return 0


if __name__ == "__main__":
    sys.exit(main())
