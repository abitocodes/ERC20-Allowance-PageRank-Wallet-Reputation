#!/usr/bin/env python3
"""Publish the result summaries the thesis quotes, with checksums and a digest.

Copies every evaluation summary (same window, W0, W1), the Sybil model, the
robustness, benchmark and supplementary summaries when they exist, the small manifests of the
cohort, the GMX decoding and the W1 extraction, the configuration and the plan
documents into data/3-published-results-for-thesis/, keeping their folder names.
Writes results_digest.md, every number a chapter would quote grouped by section
with the JSON file and key it comes from, and SHA256SUMS.txt over all published
files. Computes no score and no statistic.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import PROC, PUB, ROOT  # noqa: E402

# (published path, source)
FILES = [
    ("same-window/eval_summary.json", PROC / "same-window" / "eval_summary.json"),
    ("holdout-w0/eval_summary.json", PROC / "holdout-w0" / "eval_summary.json"),
    ("registered-w1/eval_summary.json", PROC / "registered-w1" / "eval_summary.json"),
    ("registered-w1/extraction_manifest.json", PROC / "registered-w1" / "extraction_manifest.json"),
    ("sybil-model/sybil_model.json", PROC / "sybil-model" / "sybil_model.json"),
    ("robustness/robustness.json", PROC / "robustness" / "robustness.json"),
    ("benchmark/benchmark.json", PROC / "benchmark" / "benchmark.json"),
    ("supplementary/supplementary.json", PROC / "supplementary" / "supplementary.json"),
    ("cohort/matched_cohort.json", PROC / "cohort" / "matched_cohort.json"),
    ("gmx/gmx_contract_closes_obs_decoded.json", PROC / "gmx" / "gmx_contract_closes_obs_decoded.json"),
    ("gmx/gmx_contract_closes_w1_decoded.json", PROC / "gmx" / "gmx_contract_closes_w1_decoded.json"),
    ("config/contract_reputation.yaml", ROOT / "config" / "contract_reputation.yaml"),
    ("docs/analysis_plan.md", ROOT / "docs" / "analysis_plan.md"),
    ("docs/registration_w1.md", ROOT / "docs" / "registration_w1.md"),
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
    src = "registered-w1/eval_summary.json"
    D.section("7. Registered window W1 (scores at T_obs, labels July to September 2026)")
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


def sec_supplementary(D: Digest, sup: dict) -> None:
    src = "supplementary/supplementary.json"
    D.sub("Supplementary spender contrasts (computed after the labels were known, outside every rule)")
    for window, d in sup.items():
        for k, v in d.items():
            if isinstance(v, dict):
                D.row(f"{window.upper()} {SUPP_NAMES.get(k, k)}", contrast(v), src, f"{window}.{k}")
            else:
                D.row(f"{window.upper()} {k}", num(v), src, f"{window}.{k}")


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


def main() -> int:
    PUB.mkdir(parents=True, exist_ok=True)
    published: list[str] = []
    missing: list[str] = []
    for dest, src in FILES:
        if not src.exists():
            missing.append(dest)
            continue
        out = PUB / dest
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, out)
        published.append(dest)
    j = {d: json.loads((PUB / d).read_text(encoding="utf-8")) for d in published if d.endswith(".json")}

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
        f"- Code revision: `{head or 'unknown'}`"
        + (" with uncommitted changes (git status code) in: " + ", ".join(f"`{p}`" for p in dirty) if dirty else ""),
        "- Published files: " + ", ".join(f"`{p}`" for p in published),
    ]
    if missing:
        D.lines.append("- Not yet available: " + ", ".join(f"`{p}`" for p in missing))
    s = j.get("same-window/eval_summary.json")
    w0 = j.get("holdout-w0/eval_summary.json")
    w1 = j.get("registered-w1/eval_summary.json")
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
    (PUB / DIGEST).write_text("\n".join(D.lines) + "\n", encoding="utf-8")
    published.append(DIGEST)

    lines = [f"{sha256(PUB / p)}  {p}" for p in sorted(published)]
    (PUB / SUMS).write_text("\n".join(lines) + "\n", encoding="utf-8")

    known = set(published) | {SUMS}
    stale = sorted(p.relative_to(PUB).as_posix() for p in PUB.rglob("*") if p.is_file()
                   and p.relative_to(PUB).as_posix() not in known)
    print(f"published {len(published)} files to {PUB}")
    if missing:
        print("not yet available:", ", ".join(missing))
    if stale:
        print("files in the folder that this run did not publish:", ", ".join(stale))
    return 0


if __name__ == "__main__":
    sys.exit(main())
