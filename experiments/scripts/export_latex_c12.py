#!/usr/bin/env python3
"""The LaTeX tables and figures of the contract-graph variant (CONTRACT_REP_VARIANT=contract12m).

scripts/export_latex.py hands its run to this module under that variant (docs/revision_contract_graph.md
section 13). The tables of the earlier variants that fit this one are written by the functions of
export_latex.py; the tables that held trader columns, or whose captions spoke of the earlier analyses, are written
here without them; the discovery-order test (docs/discovery_protocol.md), the account types, the balance cap, the
coverage of the cohorts, the label split, the uncapped sensitivity and the balance threshold of the Sybil model
have their own tables and figures here. Nothing is computed: every cell is read from a summary of the evaluation.

Tables go to data/_work/latex-contract12m/ unless --into-manuscript is given. Besides the checks of
export_latex.py (missing numbers, reversed intervals, verdicts that do not follow from their intervals), this
module checks that a discovery verdict follows from its two intervals, that every AUC lies between the random and
the ideal reference, that every curve is monotone and ends at 1, that no text says rule B is met, and that no
caption uses a word this variant's texts do not use (revision sections 2 and 11; the discovery captions also none
that would present the test as fixed before the registered results).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import export_latex as E  # noqa: E402
from common import (CONTRACT_GRAPH, PROC, PROC_SHARED, ROOT, USD_CONSTANTS, USD_INPUTS, W1_DIR, load_config,  # noqa: E402
                    load_json, read_parts)
from graphs import METHOD_LABELS  # noqa: E402

APPR, SEND = E.APPR, E.SEND
DISC = PROC / "discovery"
RUNS = (("tobs", "both"), ("tobs", "out"), ("t1", "both"), ("t1", "out"))
SRC = {
    "describe": PROC / "describe" / "describe.json",
    **{f"disc_{t}_{m}": DISC / f"discovery_{t}_{m}.json" for t, m in RUNS},
}
FREEZE = {"tobs": "$T_{\\mathrm{obs}}$", "t1": "$t_1$"}
ORDER_ROWS = (
    ("bfs", "Breadth-first (BFS)"), ("random", "Random"), None,
    ("ib_a", "$\\mathrm{IB}'_A$ (allowance backlinks)"), ("ib_t", "$\\mathrm{IB}'_T$ (transfer backlinks)"),
    ("ib_u", "$\\mathrm{IB}'_U$ (contract backlinks)"), None,
    ("endorserank", "EndorseRank$'$"), ("endorserank_activity", "EndorseRank-activity$'$"), ("awp", "AWP$'$"), None,
    ("cpr_l100", "C-PR$'$ ($\\lambda=1$)"), ("cpr_l0", "C-PR$'$ ($\\lambda=0$)"),
    ("cpr_l25", "C-PR$'$ ($\\lambda=0.25$)"), ("cpr_l50", "C-PR$'$ ($\\lambda=0.5$)"),
    ("cpr_l75", "C-PR$'$ ($\\lambda=0.75$)"), ("spr", "S-PR$'$"),
)
ORDER_NAMES = {k: v for k, v in (r for r in ORDER_ROWS if r)}
ORDER_NAMES.update({"delta": "$\\delta'$ (normalised in-strength)"})
ORDER_SHORT = {**ORDER_NAMES, "ib_a": "$\\mathrm{IB}'_A$", "ib_t": "$\\mathrm{IB}'_T$", "ib_u": "$\\mathrm{IB}'_U$",
               "bfs": "BFS", "cpr_l50": "C-PR$'$"}
REF_ROWS = (("delta", "$\\delta'$ (diagnostic, outside the comparisons)"), None,
            ("ref_cpr", "Reference: C-PR of the full graph"), ("ref_ib_u", "Reference: union in-degree of the full graph"),
            ("ref_ideal", "Reference: ideal order"), ("random_curve", "Reference: random curve"))
HOT_NAMES = {"i_t@q": "$H_q(I_T)$", "i_a@q": "$H_q(I_A)$", "ib_u@q": "$H_q(\\mathrm{IB}_U)$", "ir@q": "$H_q(\\mathrm{IR})$",
             "n_t@q": "$H_q(N_T)$", "n_a@q": "$H_q(N_A)$"}
W0_ROWS = (
    ("t1_in_approve_degree", "In-approve degree at $t_1$ (baseline)"),
    ("t1_in_approve_value", "In-approve value at $t_1$ (baseline)"),
    ("t1_in_degree", "Transfer in-degree at $t_1$ (baseline)"),
    ("t1_in_degree_union", "Union in-degree at $t_1$ (baseline)"),
    None, ("endorserank", "EndorseRank"), ("awp", "AWP"), None,
    *((m, METHOD_LABELS[m]) for m in E.LAYER_ROWS),
)
W1_BASELINES = (
    ("in_approve_degree", "In-approve degree at the freeze (baseline)"),
    ("in_approve_value", "In-approve value at the freeze (baseline)"),
    ("in_degree", "Transfer in-degree at the freeze (baseline)"),
    ("in_degree_union", "Union in-degree at the freeze (baseline)"),
)
W1_ROWS = (*W1_BASELINES, None, ("awp", "AWP"), None, *((m, METHOD_LABELS[m]) for m in E.LAYER_ROWS))
SHORT = {**E.SHORT, "t1_in_approve_value": "$t_1$ in-approve value", "t1_in_degree_union": "$t_1$ union in-degree",
         "in_approve_value": "in-approve value", "in_degree_union": "union in-degree"}
STATUS = ("defined after the registered results were known; it decides no rule of the analysis plan or the "
          "registration")
# Words that the texts of this variant do not use; the phrase of STATUS is taken out before a caption is checked.
FORBIDDEN = re.compile(r"GMX|\btraders?\b|liquidat|rule~?\s?B (?:is )?met\b|\bregistered results?\b", re.I)
FORBIDDEN_DISCOVERY = re.compile(r"\bplanned\b|pre-?specified|\bregistered\b|in advance|committed before", re.I)
CAPTIONS: list[tuple[str, str]] = []


# --------------------------------------------------------------------------- helpers


# Entries of the List of Tables for the tables this module writes under a name of export_latex.py; the other tables
# of this module use the first sentence of their caption.
SHORT_CAPTIONS = {
    "benchmark-runtime": "Computational benchmark on the contract graph.",
    "benchmark-scaling": "Runtime on subsamples of the matched cohort and on the whole contract graph.",
    "benchmark-runs": "Every timed solver call of the benchmark.",
    "robustness-sample-size": "Sensitivity of the family means to the evaluation set.",
    "holdout-spenders": "Temporal holdout W0 on the spender cohort.",
    "holdout-diff": "Paired bootstrap differences on the spender holdout W0.",
    "holdout-receiving": "Spender holdout W0 restricted to spenders that had received a transfer before the freeze.",
    "endorserank-awp-holdout": "Paired bootstrap differences between EndorseRank and AWP out of window.",
    "fresh-holdout": "Window W1: Kendall $\\tau$ on the two spender labels.",
    "fresh-contrasts": "Window W1: F1 and F2, two of rule B's registered criteria, with their verdicts and the "
                       "sensitivity analyses.",
    "fresh-posthoc": "EndorseRank and its variant with activity restarts in window W1.",
    "cpr-contrasts": "C-PR against every other score and the raw counts out of window.",
    "registered-vs-revised": "Decision contrasts of the registered analysis and of the contract-graph analysis.",
    "usd-tokens": "The five tokens, their allowances between contracts and their prices.",
    "discovery-sizes": "Sizes of the contract graph and of the universes of the discovery-order test.",
    "discovery-auc": "Discovery-order test: $\\mathrm{AUC}_{10\\%}$ of every ordering in the four runs.",
    "discovery-decision": "Discovery-order test: the decision contrasts and their reading.",
    "discovery-contrasts": "Discovery-order test: the contrasts reported outside the decision.",
    "discovery-sensitivity": "Discovery-order test: sensitivity of the decision contrasts.",
    "discovery-diagnostics": "Discovery-order test: ties, wasted visits and hub visits.",
    "discovery-coverage": "Coverage of the two importances by the contract graph and the universes.",
    "contract-types": "Account types of the contract graph.",
    "allowance-cap": "Latest allowances between contracts and the balance cap.",
    "graph-layers": "The two layers of the contract graph at both freezes.",
    "cohort-coverage": "Where the members of each cohort lie in the contract graph.",
    "label-split": "The labels by the class of the account they count.",
    "union-members": "The main out-of-window contrasts inside the union graph.",
    "uncapped-sensitivity": "Sensitivity to the balance cap.",
    "sybil-threshold": "The Sybil cost model on the contract graph and its sensitivity to a balance threshold.",
}


def emit(name: str, caption: str, tab: str, sources: list[Path], discovery: bool = False) -> None:
    """Write a table as E.emit does, with the List-of-Tables entry and the wording checks of this variant."""
    text = caption.replace("after the registered results were known", "")
    bad = sorted({m.group(0) for m in FORBIDDEN.finditer(text + " " + tab)})
    if discovery:
        bad += sorted({m.group(0) for m in FORBIDDEN_DISCOVERY.finditer(text)})
    if bad:
        E.problem(f"wording {bad}")
    CAPTIONS.append((name, caption))
    short = SHORT_CAPTIONS.get(name) or E._short_caption(caption)
    cap = f"\\caption[{short}]{{{caption}}}" if short != caption else f"\\caption{{{caption}}}"
    head = "".join(f"% Source: {E.rel(p)}\n" for p in sources)
    path = E.OUT["tables"] / f"{name}.tex"
    path.write_text(
        "% Generated by experiments/scripts/export_latex.py (export_latex_c12.py) -- do not edit by hand.\n"
        f"{head}"
        "\\begin{table}[htbp]\n\\centering\n"
        f"{cap}\n\\label{{tab:{name}}}\n\\fitwidth{{%\n{tab}\n}}\n\\end{{table}}\n", encoding="utf-8")
    E.WRITTEN.append(path)


def f4(v, what: str = "value") -> str:
    x = E._num(v)
    if x is None:
        E.problem(f"missing {what}")
        return "---"
    return f"{x:.4f}"


def s4(v, what: str = "difference") -> str:
    x = E._num(v)
    if x is None:
        E.problem(f"missing {what}")
        return "---"
    return f"{x:+.4f}"


def ci4(d: dict | None, what: str) -> str:
    lo, hi = E._num((d or {}).get("lo")), E._num((d or {}).get("hi"))
    if lo is None or hi is None:
        E.problem(f"missing interval of {what}")
        return "---"
    if lo > hi:
        E.problem(f"reversed interval of {what} [{lo}, {hi}]")
    return f"[{lo:+.4f}, {hi:+.4f}]"


def dstat(d: dict | None, what: str) -> str:
    """A discovery contrast: point [interval]."""
    if not d:
        E.problem(f"no contrast for {what}")
        return "---"
    return f"{s4(d.get('point'), what)} {ci4(d, what)}"


def dstack(d: dict | None, what: str) -> str:
    """A discovery contrast, the point over its interval."""
    if not d:
        E.problem(f"no contrast for {what}")
        return "---"
    return (f"\\begin{{tabular}}[c]{{@{{}}c@{{}}}}{s4(d.get('point'), what)}\\\\[-1pt]{{\\footnotesize "
            f"{ci4(d, what)}}}\\end{{tabular}}")


def pct(v, digits: int = 1, what: str = "share") -> str:
    x = E._num(v)
    if x is None:
        E.problem(f"missing {what}")
        return "---"
    return f"{100 * x:.{digits}f}\\%"


def usd(v, what: str = "amount") -> str:
    """A US-dollar amount in millions or billions."""
    x = E._num(v)
    if x is None:
        E.problem(f"missing {what}")
        return "---"
    if abs(x) >= 1e9:
        return f"\\${x / 1e9:.2f} billion"
    if abs(x) >= 1e6:
        return f"\\${x / 1e6:.1f} million"
    return f"\\${E.fint(x)}"


def small_usd(v, what: str = "amount") -> str:
    """A US-dollar amount that may be below one dollar (two significant digits there)."""
    x = E._num(v)
    if x is None:
        E.problem(f"missing {what}")
        return "---"
    return f"\\${x:.2g}" if abs(x) < 1 else f"\\${E.fint(x)}"


def auc_of(d: dict, hot: str, ordering: str, x: str = "x=0.1"):
    v = ((d.get("auc") or {}).get(hot) or {}).get(ordering)
    if isinstance(v, dict):
        v = v.get(x)
    return v.get("auc") if isinstance(v, dict) else v


def header(text: str, cols: int) -> str:
    return f"\\multicolumn{{{cols}}}{{l}}{{\\emph{{{text}}}}} \\\\"


def boot_words(d: dict) -> str:
    b = (d.get("protocol") or {}).get("bootstrap") or {}
    return (f"95\\% percentile intervals of a paired bootstrap over the hot contracts ({E.fint(b.get('resamples'))} "
            f"resamples, seed {b.get('seed')})")


# --------------------------------------------------------------------------- discovery-order test


def check_discovery(runs: dict) -> None:
    """Verdicts follow from their intervals; AUCs lie between the random and the ideal reference; the curves are
    monotone and end at 1 (plan section 8)."""
    E.begin("discovery-checks")
    for (tag, mode), d in runs.items():
        name = f"{tag} {mode}"
        for imp in ("i_t", "i_a"):
            v = (d.get("decision") or {}).get(imp) or {}
            lo1, lo2 = (v.get("D1") or {}).get("lo"), (v.get("D2") or {}).get("lo")
            hi1, hi2 = (v.get("D1") or {}).get("hi"), (v.get("D2") or {}).get("hi")
            if None in (lo1, lo2, hi1, hi2):
                E.problem(f"{name} {imp}: decision contrasts missing")
                continue
            if d.get("decides"):
                want = "V3" if not lo1 > 0 else ("V1" if lo2 > 0 else "V2")
                if v.get("verdict") != want:
                    E.problem(f"{name} {imp}: verdict {v.get('verdict')} does not follow from its intervals ({want})")
            else:
                if v.get("verdict"):
                    E.problem(f"{name} {imp}: a run outside the decision carries a verdict")
                above = [k for k, lo in (("D1", lo1), ("D2", lo2)) if lo > 0]
                below = [k for k, hi in (("D1", hi1), ("D2", hi2)) if hi < 0]
                if sorted(v.get("above_zero") or []) != above or sorted(v.get("below_zero") or []) != below:
                    E.problem(f"{name} {imp}: the lists above and below 0 do not follow from the intervals")
        for hot in ("i_t@q", "i_a@q"):
            row = (d.get("auc") or {}).get(hot) or {}
            ideal, rand = auc_of(d, hot, "ideal_curve"), auc_of(d, hot, "random_curve")
            for o, _ in (r for r in ORDER_ROWS if r):
                a = auc_of(d, hot, o)
                if a is None or ideal is None or not (0 <= a <= ideal + 1e-12):
                    E.problem(f"{name} {hot} {o}: AUC {a} outside [0, ideal {ideal}]")
            if rand is None or ideal is None or not rand < ideal:
                E.problem(f"{name} {hot}: the random reference {rand} is not below the ideal one {ideal}")
            if not row:
                E.problem(f"{name}: no AUC for {hot}")
        curves = (d.get("curves") or {}).get("P_ST") or {}
        for imp, by in curves.items():
            for o, c in by.items():
                m = np.asarray(c.get("mean") if isinstance(c, dict) else c, dtype=float)
                if m.size == 0 or np.any(np.diff(m) < -1e-12) or abs(m[-1] - 1.0) > 1e-9:
                    E.problem(f"{name} P_ST {imp} {o}: the curve is not monotone or does not end at 1")
        inv = d.get("invariants") or {}
        if not inv.get("all_visited"):
            E.problem(f"{name}: a crawl did not visit its universe")


def t_discovery_sizes(runs: dict) -> None:
    E.begin("discovery-sizes")
    both = {t: runs[(t, "both")] for t in ("tobs", "t1")}
    out = {t: runs[(t, "out")] for t in ("tobs", "t1")}
    g = {t: (d.get("sizes") or {}).get("graph") or {} for t, d in both.items()}

    def row(label: str, get) -> str:
        return f"{label} & " + " & ".join(E.fint(get(t), f"{label} {t}") for t in ("tobs", "t1")) + " \\\\"

    lines = [
        row("Contracts of $G$ (one numbering for both freezes)", lambda t: g[t].get("g_nodes")),
        row("Capped allowance pairs", lambda t: g[t].get("allow_pairs")),
        row("Transfer pairs", lambda t: g[t].get("transfer_pairs")),
        row("Union graph: contracts with a pair", lambda t: g[t].get("nodes")),
        row("Union graph: pairs", lambda t: g[t].get("edges")),
        "\\midrule",
        row("Giant strongly connected component (SCC)", lambda t: g[t].get("scc")),
        row("IN (reaches the SCC)", lambda t: g[t].get("in")),
        row("OUT (reached from the SCC)", lambda t: g[t].get("out")),
        row("Other contracts with a pair", lambda t: g[t].get("other")),
        "\\midrule",
        row("$|\\mathrm{SCC}\\cup\\mathrm{OUT}|$, universe of the \\texttt{out} mode", lambda t: g[t].get("U")),
        row("Union pairs inside it", lambda t: g[t].get("E_U")),
        row("$|\\mathrm{WCC}|$, universe of the \\texttt{both} mode (primary)", lambda t: g[t].get("WCC")),
        row("Union pairs inside it", lambda t: g[t].get("E_WCC")),
        row("Capped allowance pairs inside the WCC", lambda t: ((both[t].get("sizes") or {}).get("universe") or {}).get("allow_pairs")),
        "\\midrule",
        row("$|H_q(I_T)|$, \\texttt{both} mode", lambda t: (both[t].get("hot_sets") or {}).get("i_t@q")),
        row("$|H_q(I_A)|$, \\texttt{both} mode", lambda t: (both[t].get("hot_sets") or {}).get("i_a@q")),
        row("$|H_q(I_T)|$, \\texttt{out} mode", lambda t: (out[t].get("hot_sets") or {}).get("i_t@q")),
        row("$|H_q(I_A)|$, \\texttt{out} mode", lambda t: (out[t].get("hot_sets") or {}).get("i_a@q")),
    ]
    for t in ("tobs", "t1"):
        if g[t].get("U") is not None and g[t].get("WCC") and not g[t]["U"] < 0.5 * g[t]["WCC"]:
            E.problem(f"{t}: SCC and OUT are not below half the WCC, yet the both mode is primary")
    p = both["tobs"].get("protocol") or {}
    caption = (
        "Sizes of the contract graph and of the two universes of the discovery-order test at both freezes. The union "
        "graph holds the distinct ordered pairs of different contracts with an edge in either layer; the bow-tie is "
        "that of the union graph. $\\mathrm{SCC}\\cup\\mathrm{OUT}$ holds fewer than half the contracts of the weakly "
        "connected component of the giant SCC (WCC) at $t_1$, so by the rule of the protocol the \\texttt{both} mode, "
        "whose universe is the WCC, is the primary mode at both freezes and the \\texttt{out} mode the sensitivity. A "
        f"hot set $H_q(I)$ holds the contracts of the universe with the largest positive importance $I$, $q={p.get('q')}$ "
        "of the universe with ties included, so it is smaller when fewer contracts have a positive importance."
    )
    emit("discovery-sizes", caption,
         E.tabular("lrr", f"Quantity & {FREEZE['tobs']} (primary) & {FREEZE['t1']}", lines),
         [SRC[f"disc_{t}_{m}"] for t, m in RUNS], discovery=True)


def t_discovery_auc(runs: dict) -> None:
    E.begin("discovery-auc")
    cols = [(t, m, h) for t, m in RUNS for h in ("i_t@q", "i_a@q")]

    def cell(o: str) -> str:
        return " & ".join(f4(auc_of(runs[(t, m)], h, o), f"AUC {o} {t} {m} {h}") for t, m, h in cols)

    lines = E.method_rows(ORDER_ROWS, cell) + ["\\midrule"] + E.method_rows(REF_ROWS, cell)
    d = runs[("tobs", "both")]
    p = d.get("protocol") or {}
    groups = " & ".join(f"\\multicolumn{{2}}{{c}}{{{FREEZE[t]}, \\texttt{{{m}}}}}" for t, m in RUNS)
    head = (f" & {groups} \\\\\n\\cmidrule(lr){{2-3}} \\cmidrule(lr){{4-5}} \\cmidrule(lr){{6-7}} "
            "\\cmidrule(lr){8-9}\nOrdering & " + " & ".join(["$I_T$", "$I_A$"] * 4))
    caption = (
        "Discovery-order test: $\\mathrm{AUC}_{10\\%}$ of every ordering on the hot sets of the two importances, "
        "user-account inflow $I_T$ and user-authorised value $I_A$, in the four runs. $\\mathrm{AUC}_{10\\%}$ is the "
        "mean over the hot contracts of $\\max(0, 1-t_h/\\lceil 0.1|\\mathcal{U}|\\rceil)$, where $\\mathcal{U}$ is the "
        "universe of the run and $t_h$ the visit at which the "
        f"crawl reaches hot contract $h$, averaged over {E.fint(len(d.get('seeds') or []))} seeds from the giant "
        "strongly connected component; a crawl recomputes its ordering each time its visits have grown by the share "
        f"$\\rho={p.get('rho')}$. The "
        f"first two columns ({FREEZE['tobs']}, \\texttt{{both}} mode) are the run that the decision reads "
        "(Table~\\ref{tab:discovery-decision}). A primed name is the count or walk computed on the contracts read so "
        "far. $\\delta'$ is a diagnostic outside every comparison. The references are not crawls: the orders by "
        "C-PR and by union in-degree of the full graph, the ideal order (hot contracts first) and the random curve. "
        f"The test was {STATUS}."
    )
    emit("discovery-auc", caption, E.tabular("l" + "c" * 8, head, lines),
         [SRC[f"disc_{t}_{m}"] for t, m in RUNS], discovery=True)


VERDICT_WORDS = {
    "V1": "V1: sooner than BFS and than $\\mathrm{IB}'_U$",
    "V2": "V2: sooner than BFS, not sooner than $\\mathrm{IB}'_U$",
    "V3": "V3: not sooner than BFS",
}


def t_discovery_decision(runs: dict) -> None:
    E.begin("discovery-decision")
    lines = []
    for tag, mode in RUNS:
        d = runs[(tag, mode)]
        dec = d.get("decision") or {}
        if lines:
            lines.append("\\midrule")
        title = f"{FREEZE[tag]}, \\texttt{{{mode}}} mode" + (": the decision" if d.get("decides") else ": no verdict")
        lines.append(header(title, 8))
        for imp, name in (("i_t", "$I_T$"), ("i_a", "$I_A$")):
            v = dec.get(imp) or {}
            if d.get("decides"):
                reading = VERDICT_WORDS.get(v.get("verdict"), "---")
                if v.get("verdict") not in VERDICT_WORDS:
                    E.problem(f"{tag} {mode} {imp}: no verdict")
                extra = v.get("extra") or []
                if extra and (v.get("D2") or {}).get("hi", 0) < 0:
                    reading += "; $\\mathrm{IB}'_U$ sooner"
            else:
                math = {"D1": "$D_1$", "D2": "$D_2$"}
                up = ", ".join(math[k] for k in v.get("above_zero") or []) or "none"
                down = ", ".join(math[k] for k in v.get("below_zero") or []) or "none"
                reading = f"above 0: {up}; below 0: {down}"
            lines.append(
                f"{name} & {E.fint(v.get('n_hot'), 'hot set size')} & {s4((v.get('D1') or {}).get('point'), 'D1')} & "
                f"{ci4(v.get('D1'), 'D1')} & {s4((v.get('D2') or {}).get('point'), 'D2')} & {ci4(v.get('D2'), 'D2')} & "
                f"{E.f3((v.get('D1') or {}).get('share_positive'), 'share D1')} / "
                f"{E.f3((v.get('D2') or {}).get('share_positive'), 'share D2')} & {reading} \\\\")
    d = runs[("tobs", "both")]
    caption = (
        "Discovery-order test: the two decision contrasts on each importance, $D_1 = "
        "\\mathrm{AUC}_{10\\%}(\\text{C-PR}') - \\mathrm{AUC}_{10\\%}(\\text{BFS})$ and $D_2 = "
        "\\mathrm{AUC}_{10\\%}(\\text{C-PR}') - \\mathrm{AUC}_{10\\%}(\\mathrm{IB}'_U)$, with "
        f"{boot_words(d)} and the shares of resamples above 0 for $D_1$ and $D_2$. The decision is read at "
        f"{FREEZE['tobs']} in the primary mode only. Its verdict on an importance is V1 when both intervals lie above "
        "0, V2 when the interval of $D_1$ lies above 0 and that of $D_2$ does not, and V3 when the interval of $D_1$ "
        "does not lie above 0; an interval of $D_2$ below 0 adds that the crawl ordered by contract backlinks was "
        "sooner. The answer to the question of the test is the weaker of the two verdicts, so it is yes only when "
        "both are V1. The other three runs carry no verdict: for each importance the contrasts whose interval lies "
        f"above 0 and those whose interval lies below 0 are listed. The two freezes share nine months of their score "
        f"windows and are not independent. The test was {STATUS}."
    )
    head = ("Importance & $|H_q|$ & $D_1$ & 95\\% interval & $D_2$ & 95\\% interval & Share above 0 ($D_1$ / $D_2$) & "
            "Reading")
    emit("discovery-decision", caption, E.tabular("lrcccccl", head, lines),
         [SRC[f"disc_{t}_{m}"] for t, m in RUNS], discovery=True)


def t_discovery_contrasts(d: dict) -> None:
    """The contrasts reported in the fixed order of protocol section 6 (items 1 to 4), at T_obs in the primary mode."""
    E.begin("discovery-contrasts")
    fo = d.get("fixed_order") or {}

    def pair_rows(items) -> list[str]:
        by: dict[tuple[str, str], dict[str, dict]] = {}
        for x in items or []:
            by.setdefault((x.get("a"), x.get("b")), {})[x.get("hot_set")] = x
        out = []
        for (a, b), hs in by.items():
            label = f"{ORDER_SHORT.get(a, a)} $-$ {ORDER_SHORT.get(b, b)}"
            out.append(f"{label} & {dstat(hs.get('i_t@q'), f'{a}-{b} I_T')} & {dstat(hs.get('i_a@q'), f'{a}-{b} I_A')} \\\\")
        return out

    lines = [header("1. Each walk$'$ against the count it smooths", 3), *pair_rows(fo.get("1_walk_vs_count")),
             "\\midrule", header("2. Among the walks", 3), *pair_rows(fo.get("2_walk_contrasts")),
             "\\midrule", header("3. Other values of $\\lambda$", 3)]
    for m, lam in (("cpr_l25", "0.25"), ("cpr_l75", "0.75")):
        hs = (fo.get("3_lambda") or {}).get(m) or {}
        for key, label in (("D1", f"C-PR$'$ ($\\lambda={lam}$) $-$ BFS"),
                           ("D2", f"C-PR$'$ ($\\lambda={lam}$) $-$ $\\mathrm{{IB}}'_U$"),
                           ("vs_cpr_l50", f"C-PR$'$ ($\\lambda={lam}$) $-$ C-PR$'$ ($\\lambda=0.5$)")):
            lines.append(f"{label} & {dstat((hs.get('i_t@q') or {}).get(key), f'{m} {key} I_T')} & "
                         f"{dstat((hs.get('i_a@q') or {}).get(key), f'{m} {key} I_A')} \\\\")
    cho = fo.get("4_cho") or {}
    lines += ["\\midrule", header("4. Hot sets in the manner of Cho et al.\\ (an intended-construct check)", 3)]
    for h in ("ib_u@q", "ir@q"):
        v = (cho.get("hot_sets") or {}).get(h) or {}
        for key, label in (("D1", "C-PR$'$ $-$ BFS"), ("D2", "C-PR$'$ $-$ $\\mathrm{IB}'_U$")):
            lines.append(f"{label} on {HOT_NAMES[h]} & \\multicolumn{{2}}{{c}}{{{dstat(v.get(key), f'{h} {key}')}}} \\\\")
    rep, d2 = cho.get("replication_contrast") or {}, ((cho.get("hot_sets") or {}).get("ib_u@q") or {}).get("D2") or {}
    if rep.get("point") != d2.get("point"):
        E.problem("the replication contrast is not C-PR' minus IB'_U on H(IB_U)")
    caption = (
        f"Discovery-order test at {FREEZE['tobs']} in the primary mode: the contrasts reported outside the decision, "
        "in the order fixed in the protocol. Each cell is the difference of $\\mathrm{AUC}_{10\\%}$ between two "
        f"orderings with its {boot_words(d)}; an interval above 0 means the first ordering reached the hot contracts "
        "sooner. Block 1 sets each walk beside the count it smooths; block 2 compares the walks, first C-PR$'$ with "
        "its transfer layer walked alone, C-PR$'$ ($\\lambda=0$), and with AWP$'$, which shows what the allowance "
        "layer adds. In block 4 the hot sets are defined on the edges that the orderings read, the union in-degree "
        "$\\mathrm{IB}_U$ and C-PR of the full graph ($\\mathrm{IR}$), so agreement there is an intended-construct "
        "check; C-PR$'$ minus $\\mathrm{IB}'_U$ on $H_q(\\mathrm{IB}_U)$ is the contrast that repeats the comparison "
        f"of Cho et al. The test was {STATUS}."
    )
    emit("discovery-contrasts", caption,
         E.tabular("lcc", "Contrast & On $H_q(I_T)$ & On $H_q(I_A)$", lines), [SRC["disc_tobs_both"]], discovery=True)


def t_discovery_sensitivity(d: dict) -> None:
    E.begin("discovery-sensitivity")
    sens = (d.get("fixed_order") or {}).get("5_sensitivities") or {}
    dec = d.get("decision") or {}

    def line(label: str, it: dict | None, ia: dict | None, what: str) -> str:
        cells = [dstack((x or {}).get(k), f"{what} {k} {imp}") for imp, x in (("I_T", it), ("I_A", ia))
                 for k in ("D1", "D2")]
        return f"{label} & " + " & ".join(cells) + " \\\\"

    q2 = sens.get("q_secondary") or {}
    nh = sens.get("no_hubs") or {}
    cnt = sens.get("importance_counts") or {}
    sb = sens.get("seed_bootstrap") or {}
    rq = sens.get("rho_quarter") or {}
    xs = sens.get("x") or {}
    lines = [
        line("Decision ($x=10\\%$, $q=1\\%$)", dec.get("i_t"), dec.get("i_a"), "decision"),
        "\\midrule",
        line("$x=5\\%$", (xs.get("x=0.05") or {}).get("i_t@q"), (xs.get("x=0.05") or {}).get("i_a@q"), "x=0.05"),
        line("$x=20\\%$", (xs.get("x=0.2") or {}).get("i_t@q"), (xs.get("x=0.2") or {}).get("i_a@q"), "x=0.2"),
        line(f"$q={100 * float(q2.get('q', 0)):.0f}\\%$", q2.get("i_t@q2"), q2.get("i_a@q2"), "q2"),
        line(f"Without the {E.fint(len(nh.get('hubs') or []) if isinstance(nh.get('hubs'), list) else nh.get('hubs'))} hubs",
             nh.get("i_t@q-nohubs"), nh.get("i_a@q-nohubs"), "no hubs"),
        line("Importance by counts ($N_T$, $N_A$)", cnt.get("n_t@q"), cnt.get("n_a@q"), "counts"),
        line("Bootstrap over seeds", sb.get("i_t@q"), sb.get("i_a@q"), "seed bootstrap"),
    ]
    if rq:
        c = rq.get("contrasts") or {}
        lines.append(line(f"$\\rho/4$ (recomputed at each growth of {rq.get('rho')}; {E.fint(rq.get('seeds'))} seeds)",
                          c.get("i_t@q"), c.get("i_a@q"), "rho/4"))
    hot = d.get("hot_sets") or {}
    same_q = hot.get("i_a@q") == hot.get("i_a@q2")
    caption = (
        f"Discovery-order test at {FREEZE['tobs']} in the primary mode: sensitivity of the two decision contrasts, "
        f"$D_1$ (C-PR$'$ minus BFS) and $D_2$ (C-PR$'$ minus $\\mathrm{{IB}}'_U$), each over its {boot_words(d)}. "
        "The rows change one setting at a time: the share $x$ of the universe over which the area is taken, the share "
        "$q$ of the hot set, the hot set without the hubs (the contracts with the highest union in-degree, removed "
        "from the hot set but kept in the graph), the importance measured by the number of user accounts with at "
        "least one dollar, a bootstrap over the seeds in place of the hot contracts, and a schedule that recomputes "
        "the ordering four times as often, on the first seeds. "
        + (f"Only {E.fint(hot.get('i_a@q'))} contracts of the universe have a positive $I_A$, so the hot set of $I_A$ "
           "is the same at both shares $q$. " if same_q else "")
        + "The other mode and the other freeze are in Table~\\ref{tab:discovery-decision}. None of these rows carries "
        f"a verdict. The test was {STATUS}."
    )
    head = (" & \\multicolumn{2}{c}{On $H_q(I_T)$} & \\multicolumn{2}{c}{On $H_q(I_A)$} \\\\\n"
            "\\cmidrule(lr){2-3} \\cmidrule(lr){4-5}\nSetting & $D_1$ & $D_2$ & $D_1$ & $D_2$")
    emit("discovery-sensitivity", caption, E.tabular("lcccc", head, lines), [SRC["disc_tobs_both"]], discovery=True)


def t_discovery_diagnostics(runs: dict) -> None:
    E.begin("discovery-diagnostics")
    d, o = runs[("tobs", "both")], runs[("tobs", "out")]
    dg, og = d.get("diagnostics") or {}, o.get("diagnostics") or {}

    def cell(m: str) -> str:
        w = (dg.get("wasted_visits") or {}).get(m) or {}
        means = sorted(((dg.get("hub_visits") or {}).get(m) or {}).get("mean") or [])
        hub = E.fint(means[len(means) // 2], f"hub visits {m}") if means else "---"
        return (f"{E.f3((dg.get('ties') or {}).get(m), f'ties {m}')} & {E.f3((og.get('ties') or {}).get(m), f'ties out {m}')} & "
                f"{E.f3(w.get('first_1pct'), f'wasted 1% {m}')} & {E.f3(w.get('first_10pct'), f'wasted 10% {m}')} & {hub}")

    lines = E.method_rows((*ORDER_ROWS, None, ("delta", ORDER_NAMES["delta"])), cell)
    hubs = dg.get("hubs") or []
    top = hubs[0] if hubs else {}
    caption = (
        f"Discovery-order test at {FREEZE['tobs']}: diagnostics of the crawls. Ties: the share of picks whose group of "
        "tied scores held more than one contract, in the primary mode (\\texttt{both}) and in the \\texttt{out} mode; "
        "a tie is broken by the earlier discovery and then by the lower address. Wasted visits: the share of the "
        "first 1\\% and of the first 10\\% of visits that went to contracts with $I_T = I_A = 0$ (primary mode). Hub "
        f"visit: over the {E.fint(len(hubs))} hubs of the primary universe, the median of each hub's mean visit index "
        f"across seeds; the largest hub has a union in-degree of {E.fint(top.get('ib_u'))}. The count orderings and "
        "the walks on the allowance layer alone decide nearly every pick by a tie."
    )
    head = (" & \\multicolumn{2}{c}{Picks decided by a tie} & \\multicolumn{2}{c}{Wasted visits} & Median hub \\\\\n"
            "\\cmidrule(lr){2-3} \\cmidrule(lr){4-5}\nOrdering & \\texttt{both} & \\texttt{out} & first 1\\% & "
            "first 10\\% & visit index")
    emit("discovery-diagnostics", caption, E.tabular("lccccr", head, lines),
         [SRC["disc_tobs_both"], SRC["disc_tobs_out"]], discovery=True)


def t_discovery_coverage(runs: dict) -> None:
    E.begin("discovery-coverage")
    cov = {(t, m): ((runs[(t, m)].get("diagnostics") or {}).get("coverage") or {}) for t, m in RUNS}
    cols = [(t, imp) for t in ("tobs", "t1") for imp in ("i_t", "i_a")]

    def row(label: str, get, fmt=pct) -> str:
        return f"{label} & " + " & ".join(fmt(get(t, imp), what=f"{label} {t} {imp}") for t, imp in cols) + " \\\\"

    parts = (("scc", "Giant SCC"), ("in", "IN"), ("out", "OUT"), ("other", "Other contracts with a pair"),
             ("isolated", "Contracts of $G$ without a union pair"), ("outside_g", "Contracts outside $G$"))
    lines = [f"Sum over all typed contracts & " + " & ".join(
        usd((cov[(t, "both")].get(imp) or {}).get("total"), f"total {t} {imp}") for t, imp in cols) + " \\\\", "\\midrule"]
    for key, name in parts:
        lines.append(row(name, lambda t, imp, key=key: ((cov[(t, "both")].get(imp) or {}).get("share_by_part") or {}).get(key)))
    for t in ("tobs", "t1"):
        for imp in ("i_t", "i_a"):
            s = sum(((cov[(t, "both")].get(imp) or {}).get("share_by_part") or {}).values())
            if abs(s - 1) > 1e-9:
                E.problem(f"coverage parts of {imp} at {t} sum to {s}")
    lines += ["\\midrule",
              row("Held by the WCC (\\texttt{both} mode)", lambda t, imp: (cov[(t, "both")].get(imp) or {}).get("share_U")),
              row("Held by $\\mathrm{SCC}\\cup\\mathrm{OUT}$ (\\texttt{out} mode)",
                  lambda t, imp: (cov[(t, "out")].get(imp) or {}).get("share_U")),
              row("Top 1\\% of the contracts by the importance: share in the WCC",
                  lambda t, imp: ((cov[(t, "both")].get(imp) or {}).get("top_1pct") or {}).get("share_in_U")),
              row("Top 1\\%: share in $\\mathrm{SCC}\\cup\\mathrm{OUT}$",
                  lambda t, imp: ((cov[(t, "out")].get(imp) or {}).get("top_1pct") or {}).get("share_in_U"))]
    c = cov[("tobs", "both")]
    c1 = cov[("t1", "both")]
    caption = (
        "Coverage of the two importances by the contract graph and by the universes of the discovery-order test. "
        "$I_T$ is the US-dollar value that user accounts transferred to a contract in the score window and $I_A$ the "
        "value they had authorised it to spend at the freeze, each counted up to $U_{\\mathrm{user}}$ per account "
        f"and, for $I_A$, up to the account's balance. At {FREEZE['tobs']} {E.fint(c.get('contracts'))} typed contracts "
        f"have a positive importance, {E.fint(c.get('outside_g'))} of them outside $G$ (at {FREEZE['t1']}: "
        f"{E.fint(c1.get('contracts'))} and {E.fint(c1.get('outside_g'))}). The parts of the bow-tie are those of the "
        "union graph and sum to 100\\%. User accounts also transferred "
        f"{usd(c.get('inflow_untyped_usd'), 'untyped inflow')} at {FREEZE['tobs']} and "
        f"{usd(c1.get('inflow_untyped_usd'), 'untyped inflow t1')} at {FREEZE['t1']} to addresses that were not typed "
        "because every counterparty of theirs is a user account; these addresses are never graph nodes, and the sum "
        "bounds the inflow that the coverage cannot place."
    )
    head = (f" & \\multicolumn{{2}}{{c}}{{{FREEZE['tobs']}}} & \\multicolumn{{2}}{{c}}{{{FREEZE['t1']}}} \\\\\n"
            "\\cmidrule(lr){2-3} \\cmidrule(lr){4-5}\nShare of the importance & $I_T$ & $I_A$ & $I_T$ & $I_A$")
    emit("discovery-coverage", caption, E.tabular("lrrrr", head, lines),
         [SRC[f"disc_{t}_{m}"] for t, m in RUNS], discovery=True)


CURVE_LINES = (("bfs", "BFS", "#7f7f7f", "-"), ("random", "Random", "#bdbdbd", "-"),
               ("ib_u", "IB$'_U$ (contract backlinks)", E.RED, "-"), ("awp", "AWP$'$", "#3a7d44", "-"),
               ("cpr_l50", "C-PR$'$", E.BLUE, "-"))


def fig_discovery_curves(d: dict, name: str) -> None:
    """P_ST over the first 20% of the visits for the main orderings, one panel per importance."""
    plt = E._style()
    grid = np.asarray((d.get("curves") or {}).get("grid") or [], dtype=float)
    n = float(((d.get("sizes") or {}).get("universe") or {}).get("U") or 0)
    pst = (d.get("curves") or {}).get("P_ST") or {}
    if grid.size == 0 or not n or not pst:
        E.SKIPPED.append(f"{name} (no curves)")
        return
    x = grid / n
    keep = x <= 0.2
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.1), sharey=False)
    for ax, (imp, title) in zip(axes, (("i_t", "$H_q(I_T)$: user-account inflow"),
                                       ("i_a", "$H_q(I_A)$: user-authorised value"))):
        by = pst.get(imp) or {}
        for key, label, color, style in CURVE_LINES:
            c = by.get(key)
            if not c:
                E.problem(f"{name}: no curve for {key} on {imp}")
                continue
            m = np.asarray(c["mean"] if isinstance(c, dict) else c, dtype=float)
            ax.plot(100 * x[keep], m[keep], style, color=color, lw=1.6 if key == "cpr_l50" else 1.2, label=label)
            if key in ("cpr_l50", "ib_u") and isinstance(c, dict):
                ax.fill_between(100 * x[keep], np.asarray(c["min"], dtype=float)[keep],
                                np.asarray(c["max"], dtype=float)[keep], color=color, alpha=0.12, lw=0)
        ideal = by.get("ideal") or {}
        if ideal:
            ax.plot(100 * x[keep], np.asarray(ideal["mean"] if isinstance(ideal, dict) else ideal, dtype=float)[keep],
                    ":", color="black", lw=1.0, label="Ideal")
        ax.axvline(10, color="black", lw=0.6, alpha=0.5)
        ax.set_title(title, fontsize=10)
        ax.set_xlabel("Contracts visited (% of the universe)")
        ax.set_xlim(0, 20)
        top = max(float(np.asarray(by[k]["mean"] if isinstance(by[k], dict) else by[k], dtype=float)[keep].max())
                  for k, *_ in CURVE_LINES if by.get(k))
        ax.set_ylim(0, min(1.0, 1.25 * top))
    axes[0].set_ylabel("Share of the hot contracts visited ($P_{ST}$)")
    axes[1].legend(loc="upper left", frameon=False)
    fig.tight_layout()
    E._save(fig, name)


# --------------------------------------------------------------------------- data: account types, cap, coverage


def t_contract_types(desc: dict) -> None:
    E.begin("contract-types")
    at, ev = desc.get("account_types") or {}, desc.get("events") or {}
    typed, after, ext = at.get("typed") or {}, at.get("after_extension") or {}, at.get("extension") or {}
    wk, pk = at.get("wallet_kind_typed") or {}, at.get("proxy_kind") or {}
    k = at.get("addresses")
    if sum(after.values()) != k:
        E.problem("the classes after the extension do not sum to the queue")
    lines = [
        f"Externally owned account without code & user account & {E.fint(after.get('eoa'))} \\\\",
        f"Externally owned account with an EIP-7702 delegation & user account & {E.fint(after.get('eoa_7702'))} \\\\",
        f"Safe (threshold and owners answered) & user account & {E.fint(wk.get('safe'))} \\\\",
        f"ERC-4337 account, by the rule of the reads & user account & {E.fint(wk.get('erc4337'))} \\\\",
        f"ERC-4337 account, by the listed code families & user account & {E.fint(ext.get('moved'))} \\\\",
        f"Any other code & contract (graph node) & {E.fint(after.get('contract'))} \\\\",
        "\\midrule",
        f"Addresses read & & {E.fint(k)} \\\\",
    ]
    if (wk.get("safe", 0) + wk.get("erc4337", 0) + ext.get("moved", 0)) != after.get("smart_account"):
        E.problem("the smart accounts do not sum")
    caption = (
        "Account types of the contract graph. The five-token events of the typing window have "
        f"{E.fint(ev.get('addresses'))} distinct addresses other than the zero address; "
        f"{E.fint(ev.get('transaction_senders'))} of them sent a transaction and are user accounts by that fact. The "
        f"table types the {E.fint(k)} addresses that were read with \\texttt{{eth\\_getCode}} at block "
        f"{E.fint(at.get('block'))}: every address that sent no transaction and has a counterparty that is neither a "
        "transaction sender nor the zero address, the members of the cohorts and two audit samples. An address "
        "outside this set that sent no transaction has only user accounts as counterparties and cannot end an edge "
        "between contracts. Smart accounts are user accounts: a Safe answers its threshold and owners, and an "
        "ERC-4337 account answers a canonical EntryPoint and carries a \\texttt{validateUserOp} selector and no "
        f"paymaster selector; {E.fint(ext.get('moved'))} further accounts whose proxy hides that selector were moved "
        f"by listed code families ({E.fint(ext.get('by_code_hash'))} by code hash and "
        f"{E.fint(ext.get('by_implementation'))} by code hash and implementation). Of the addresses read, "
        f"{E.fint(pk.get('erc1967'))} are ERC-1967 proxies, {E.fint(pk.get('eip1167'))} ERC-1167 clones and "
        f"{E.fint(pk.get('safe'))} Safe proxies. With the transaction senders, {E.fint(ev.get('user_accounts'))} "
        f"addresses are typed user accounts and {E.fint(ev.get('contracts'))} contracts."
    )
    emit("contract-types", caption, E.tabular("llr", "Code read at the block & Class & Addresses", lines),
         [SRC["describe"]])


def t_allowance_cap(desc: dict) -> None:
    E.begin("allowance-cap")
    al = desc.get("allowances") or {}
    cons = desc.get("constants") or {}
    lines = []
    for tag in ("tobs", "t1"):
        a = al.get(tag) or {}
        if lines:
            lines.append("\\midrule")
        lines.append(header(f"At {FREEZE[tag]}", 7))
        rows = [*(a.get("per_token") or []), {"symbol": "All five tokens", **(a.get("total") or {})}]
        for t in rows:
            sym = "USDT0" if t.get("symbol") == "USD₮0" else t.get("symbol")
            n = t.get("n_latest_positive")
            if (t.get("n_positive_eff", 0) + t.get("n_capped_to_zero", 0)) != n:
                E.problem(f"{tag} {sym}: positive after the cap and capped to zero do not sum to the allowances")
            lines.append(
                f"{sym} & {E.fint(n)} & {E.fint(t.get('n_unlimited'))} & {E.fint(t.get('n_capped_to_zero'))} & "
                f"{E.fint(t.get('n_capped_below_allowance'))} & {E.fint(t.get('n_positive_eff'))} & "
                f"{E._sci(t.get('sum_usd_eff'))} \\\\")
    tot = (al.get("tobs") or {}).get("total") or {}
    tot1 = (al.get("t1") or {}).get("total") or {}
    caption = (
        "Latest allowances between contracts and the balance cap, per token and freeze. An allowance is the latest "
        "\\texttt{Approval} of a (token, owner, spender) triple in the score window, kept when its value is positive. "
        "It is counted up to the owner's balance of the token at the freeze: unlimited allowances are those of at "
        f"least {E._sci(cons.get('unlimited_base_units'))} base units, an allowance is capped to zero when the owner holds no "
        "balance of the token at the freeze, and capped below the allowance when the balance is positive and "
        "smaller than the allowance. Only the allowances that stay positive enter the allowance layer. The last "
        "column is the sum of the capped values in US dollars. At "
        f"{FREEZE['tobs']} {pct(tot.get('share_capped_to_zero'))} of the allowances are capped to zero and "
        f"{pct(tot.get('share_unlimited'))} are unlimited (at {FREEZE['t1']}: {pct(tot1.get('share_capped_to_zero'))} "
        f"and {pct(tot1.get('share_unlimited'))}). The median positive capped value at {FREEZE['t1']} is "
        f"{small_usd(cons.get('m_allowance_usd'))}, the constant $m_A$."
    )
    head = ("Token & Positive allowances & Unlimited & Capped to zero & Capped below & Positive after the cap & "
            "Capped value (USD)")
    emit("allowance-cap", caption, E.tabular("lrrrrrr", head, lines), [SRC["describe"]])


def t_graph_layers(desc: dict) -> None:
    E.begin("graph-layers")
    pairs = desc.get("pairs") or {}
    layers = (("allowance_capped", "Allowance layer (capped)"), ("allowance_uncapped", "Allowance pairs before the cap"),
              ("transfer", "Transfer layer"))
    lines = []
    for tag in ("tobs", "t1"):
        if lines:
            lines.append("\\midrule")
        lines.append(header(f"At {FREEZE[tag]}", 6))
        for key, name in layers:
            p = (pairs.get(tag) or {}).get(key) or {}
            lines.append(f"{name} & {E.fint(p.get('pairs'))} & {E.fint(p.get('sources'))} & "
                         f"{E.fint(p.get('destinations'))} & {E.fint(p.get('largest_source_pairs'))} & "
                         f"{E.fint(p.get('largest_destination_pairs'))} \\\\")
    a = (pairs.get("tobs") or {}).get("allowance_capped") or {}
    a1 = (pairs.get("t1") or {}).get("allowance_capped") or {}
    nodes = desc.get("nodes") or {}
    caption = (
        "The two layers of the contract graph at both freezes: ordered pairs of contracts, the distinct contracts at "
        "their source (owners or senders) and destination (spenders or recipients), and the largest number of pairs "
        "that one source and one destination hold. Every end of every pair is a contract; the graph numbers "
        f"{E.fint(nodes.get('contracts'))} contracts over both freezes. At {FREEZE['tobs']} one owner contract holds "
        f"{E.fint(a.get('largest_source_pairs'))} of the {E.fint(a.get('pairs'))} capped allowance pairs; at "
        f"{FREEZE['t1']} the largest owner holds {E.fint(a1.get('largest_source_pairs'))} of "
        f"{E.fint(a1.get('pairs'))}."
    )
    head = "Layer & Pairs & Sources & Destinations & Largest source & Largest destination"
    emit("graph-layers", caption, E.tabular("lrrrrr", head, lines), [SRC["describe"]])


def t_cohort_coverage(same: dict, w0: dict, w1: dict) -> None:
    E.begin("cohort-coverage")
    rows = (("Matched cohort at $T_{\\mathrm{obs}}$", (same.get("cohort_coverage") or {}).get("cohort_tobs")),
            ("W0 cohort at $t_1$", (w0.get("cohort_coverage") or {}).get("cohort_t1")),
            ("W0 spenders at $t_1$", (w0.get("cohort_coverage") or {}).get("spenders_w0")),
            ("W1 spenders at $T_{\\mathrm{obs}}$", (w1.get("cohort_coverage") or {}).get("spenders_w1")))
    lines = []
    for name, c in rows:
        if not c:
            E.problem(f"no coverage for {name}")
            continue

        def cell(k: str) -> str:
            v = c.get(k) or {}
            return f"{E.fint(v.get('n'))} ({pct(v.get('share'))})"

        lines.append(f"{name} & {E.fint(c.get('n'))} & {cell('allowance_layer')} & {cell('transfer_layer')} & "
                     f"{cell('union_graph')} & {cell('outside_contract_graph')} \\\\")
        if (c.get("union_graph") or {}).get("n", 0) + (c.get("outside_contract_graph") or {}).get("n", 0) \
                + (c.get("self_pairs_only") or {}).get("n", 0) != c.get("n"):
            E.problem(f"{name}: union, self-pairs only and outside do not sum to the cohort")
    caption = (
        "Where the members of each cohort lie in the contract graph of their freeze: members that end a capped "
        "allowance pair, a transfer pair, a pair of the union graph, and members that end no pair between contracts. "
        "A member outside a graph stays in its cohort and scores zero under every score and baseline, so the scores "
        "tie on these members; Table~\\ref{tab:union-members} repeats the main comparisons on the members inside "
        "the union graph."
    )
    head = "Cohort & Members & In the allowance layer & In the transfer layer & In the union graph & Outside the graph"
    emit("cohort-coverage", caption, E.tabular("lrrrrr", head, lines), [E.SOURCES["same"], E.SOURCES["w0"], E.SOURCES["w1"]])


def t_label_split(w0: dict, w1: dict) -> None:
    E.begin("label-split")
    names = (("future_new_approvers", "New approval pairs"), ("future_new_transfer_senders", "New transfer senders"),
             ("future_revoke_count", "Revocations"), ("future_drain_owners", "Drained owners"))
    lines = []
    for w, d in (("W0", w0), ("W1", w1)):
        ls = (d.get("label_split") or {}).get("labels") or {}
        if not ls:
            E.problem(f"no label split for {w}")
            continue
        if lines:
            lines.append("\\midrule")
        lines.append(header(f"{w} ($n={E.fint(d.get('spenders'))}$ spender contracts)", 7))
        for key, name in names:
            v = ls.get(key) or {}
            if v.get("user_accounts", 0) + v.get("contracts", 0) + v.get("other", 0) != v.get("total"):
                E.problem(f"{w} {key}: the parts do not sum to the label")
            lines.append(f"{name} & {E.fint(v.get('total'))} & {E.fint(v.get('user_accounts'))} & "
                         f"{E.fint(v.get('contracts'))} & {pct(v.get('share_contracts'))} & "
                         f"{E.fint(v.get('spenders_with_user_accounts'))} & {E.fint(v.get('spenders_with_contracts'))} \\\\")
    caption = (
        "The labels of the two label windows by the class of the account they count: for each label, its total over "
        "the spender cohort, the parts counted on user accounts and on contracts, the share of the contracts, and "
        "the spenders that have a positive part of each kind. An approval pair is counted by the class of its owner "
        "and a sender by its own class; a handful of senders are neither (the zero address of mints), so the two "
        "parts can fall short of the total by them. The split is a description outside every rule: the labels are "
        "those of the twelve-month analysis, unchanged, and most of what they count are user accounts, which no "
        "score of the contract graph reads."
    )
    head = ("Label & Total & From user accounts & From contracts & Contracts' share & Spenders with user accounts & "
            "Spenders with contracts")
    emit("label-split", caption, E.tabular("lrrrrrr", head, lines), [E.SOURCES["w0"], E.SOURCES["w1"]])


# --------------------------------------------------------------------------- out-of-window tables of this variant


def t_holdout_spenders(w0: dict, seed: int, cfg: dict) -> None:
    E.begin("holdout-spenders")
    taus = w0.get("taus") or {}
    lines = E.method_rows(W0_ROWS, lambda m: " & ".join(E.tc((taus.get(m) or {}).get(lab), f"{m} {lab}")
                                                        for lab in (APPR, SEND)))
    h = cfg["holdout"]
    kinds = w0.get("spender_account_types") or {}
    cov = ((w0.get("cohort_coverage") or {}).get("spenders_w0") or {}).get("union_graph") or {}
    caption = (
        f"Temporal holdout W0 on the spender cohort ($n={E.fint(w0.get('spenders'))}$ contracts): Kendall $\\tau$ "
        f"between scores frozen at {E.tex_date(h['score_end'])} on the contract graph and two labels counted on the "
        f"contract between {E.tex_date(h['outcome_start'])} and {E.tex_date(h['outcome_end'])}: the number of new "
        "owner--spender approval pairs and the number of accounts that sent a transfer to the contract for the first "
        f"time. The cohort keeps the {E.fint(kinds.get('contract'))} contracts among the "
        f"{E.fint(sum(kinds.values()))} spenders of the labels; {E.fint(kinds.get('user_account', 0))} user accounts "
        f"and {E.fint(kinds.get('system', 0))} system address are left out. {E.fint(w0.get('gained_new_approvals'))} "
        f"contracts received at least one new pair and {E.fint(w0.get('gained_new_senders'))} at least one new "
        f"sender. {E.fint(cov.get('n'))} of the cohort ({pct(cov.get('share'))}) lie in the union graph; a contract "
        "outside a graph scores zero. Baseline rows are raw counts on the contract graph at $t_1$: the in-approve "
        "degree and value and the transfer in-degree that the single-layer walks smooth, and the union in-degree, "
        "the number of distinct contracts with an edge to the contract in either layer. C-PR ($\\lambda=1$) and C-PR "
        f"($\\lambda=0$) are the allowance and transfer layers of the coupled operator walked alone. {E.boot_note(seed)}"
    )
    head = "Score at $t_1$ & New approval pairs ($\\tau$ [95\\% CI]) & New transfer senders ($\\tau$ [95\\% CI])"
    emit("holdout-spenders", caption, E.tabular("lcc", head, lines), [E.SOURCES["w0"]])


def _label(r: dict) -> str:
    return f"{SHORT[r['a']]} minus {SHORT[r['b']]}"


def t_holdout_diff(w0: dict, seed: int, supp: dict | None) -> None:
    E.begin("holdout-diff")
    pre = w0.get("contrasts_prefixed") or []
    moved = bool(E.cpr_supp(supp))
    post = [r for r in w0.get("contrasts_after") or []
            if not E.is_er_awp(r) and not (moved and r.get("a") == "cpr_l50")]
    base = w0.get("baseline_contrasts") or []
    lines = [header("Rule A, primary part, fixed in the plan", 7)]
    lines += [E.contrast_line(_label(r), r, E.LABEL_WORDS[r["outcome"]]) for r in pre]
    if post:
        lines += ["\\midrule", header("Computed after the labels were known", 7)]
        lines += [E.contrast_line(_label(r), r, E.LABEL_WORDS[r["outcome"]]) for r in post]
    if base:
        lines += ["\\midrule", header("C-PR against the union in-degree, the baseline of the contract graph", 7)]
        lines += [E.contrast_line(_label(r), r, E.LABEL_WORDS[r["outcome"]]) for r in base]
    rule = w0.get("rule_a_primary") or {}
    appr = next((r for r in pre if r["a"] == "cpr_l50" and r["b"] == "cpr_l100" and r["outcome"] == APPR), {})
    send = next((r for r in pre if r["a"] == "cpr_l50" and r["b"] == "cpr_l0" and r["outcome"] == SEND), {})
    if not (appr and send):
        E.problem("the two contrasts of rule A are missing")
    else:
        if bool(appr["ci_high"] >= 0) != bool(rule.get("no_worse_on_new_approvals")):
            E.problem("rule A no-worse verdict does not follow from its interval")
        if bool(send["ci_low"] > 0) != bool(rule.get("better_on_new_senders")):
            E.problem("rule A better verdict does not follow from its interval")
    yes = {True: "holds", False: "fails"}
    caption = (
        f"Paired bootstrap differences on the spender holdout W0 ($n={E.fint(w0.get('spenders'))}$ contracts; "
        f"{E.fint(max(E.STATE['nboot']) if E.STATE['nboot'] else None)} resamples shared by $a$ and $b$, seed {seed}). "
        "The first block holds the two contrasts of the primary part of rule A, fixed in the analysis plan committed "
        "on 9~October~2026 before the study extracted any data and applied here to the scores of the contract graph "
        "(C-PR against C-PR ($\\lambda=1$) on new approval pairs and against C-PR ($\\lambda=0$) on new transfer "
        "senders). The second block was computed after the labels were known: the increment of C-PR ($\\lambda=1$), "
        "the allowance layer walked alone, over its raw degree at $t_1$, the same comparisons for S-PR, and the "
        "increments of EndorseRank and AWP over their raw degrees; C-PR's other contrasts are in "
        "Table~\\ref{tab:cpr-contrasts}. The third block sets C-PR beside the union in-degree. Primary part of rule A "
        "(C-PR no worse than C-PR ($\\lambda=1$) on new approval pairs and better than C-PR ($\\lambda=0$) on new "
        f"transfer senders): no worse {yes[bool(rule.get('no_worse_on_new_approvals'))]}, better "
        f"{yes[bool(rule.get('better_on_new_senders'))]}, so the rule is {'met' if rule.get('pass') else 'not met'}. "
        "The differences between EndorseRank and AWP are in Table~\\ref{tab:endorserank-awp-holdout}."
    )
    emit("holdout-diff", caption, E.tabular("llccccc", E.CONTRAST_HEAD_LABEL, lines), [E.SOURCES["w0"]])


def t_holdout_receiving(w0: dict, seed: int, supp: dict | None) -> None:
    E.begin("holdout-receiving")
    rec = w0.get("receiving") or {}
    taus = rec.get("taus") or {}
    if not taus:
        E.SKIPPED.append("holdout-receiving (no receiving subset)")
        return
    s0 = E.cpr_supp(supp).get("w0") or {}
    cpr_row = bool(s0.get("recv_cpr_tau_appr"))
    if cpr_row:
        if s0.get("recv_n") != rec.get("n"):
            E.problem(f"supplementary receiving n={s0.get('recv_n')} differs from {rec.get('n')}")
        taus = {**taus, "cpr_l50": {APPR: s0.get("recv_cpr_tau_appr"), SEND: s0.get("recv_cpr_tau_send")}}
    order = (("endorserank", "EndorseRank"), ("awp", "AWP"),
             *((("cpr_l50", f"{METHOD_LABELS['cpr_l50']}$^{{a}}$"),) if cpr_row else ()), None,
             ("t1_in_approve_degree", "In-approve degree at $t_1$"), ("t1_in_degree", "Transfer in-degree at $t_1$"))
    lines = E.method_rows(order, lambda m: " & ".join(E.tc((taus.get(m) or {}).get(lab), f"{m} {lab}")
                                                      for lab in (APPR, SEND)))
    diffs = rec.get("contrasts") or []
    if diffs:
        lines.append("\\midrule")
        for r in diffs:
            lines.append(f"{_label(r)} ({E.LABEL_WORDS[r['outcome']]}) & \\multicolumn{{2}}{{c}}{{$\\Delta\\tau="
                         f"{E.fsigned(r.get('delta_tau'))}$ {E.fci(r.get('ci_low'), r.get('ci_high'))}}} \\\\")
            if r.get("n_boot") is not None:
                E.STATE["nboot"].add(int(r["n_boot"]))
    n_sp, n_rec = w0.get("spenders"), rec.get("n")
    cov = w0.get("coverage") or {}
    caption = (
        f"Spender holdout W0 restricted to the {E.fint(n_rec)} of the {E.fint(n_sp)} spender contracts that had "
        f"received a transfer from another contract before the freeze ($n={E.fint(n_rec)}$). The other "
        f"{E.fint(n_sp - n_rec if n_sp is not None and n_rec is not None else None)} have no inbound transfer edge "
        f"from another contract, and {E.fint(cov.get('spenders_without_transfer_edge'))} spenders score zero under "
        f"AWP. The restriction was chosen after the results were known. {E.boot_note(seed)}"
        + (" $^{a}$Computed afterwards from the saved scores, with the same resamples; its contrasts with AWP and "
           "the in-approve degree on this subset are in Table~\\ref{tab:cpr-contrasts}." if cpr_row else "")
    )
    head = "Score at $t_1$ & New approval pairs ($\\tau$ [95\\% CI]) & New transfer senders ($\\tau$ [95\\% CI])"
    emit("holdout-receiving", caption, E.tabular("lcc", head, lines),
         [E.SOURCES["w0"]] + ([E.SOURCES["supp"]] if cpr_row else []))


def t_endorserank_awp_holdout(w0: dict, w1: dict, supp: dict | None, seed: int) -> None:
    E.begin("endorserank-awp-holdout")
    blocks, counts = [], []
    sp0 = [r for r in w0.get("contrasts_after") or [] if E.is_er_awp(r)]
    if sp0:
        counts += [int(r.get("n_boot") or 0) for r in sp0]
        n = E.fint(w0.get("spenders"))
        blocks.append((f"W0, spenders ($n={n}$)", f"W0 spenders $n={n}$",
                       [(_label(r), E.LABEL_WORDS[r["outcome"]], r) for r in sp0]))
    s1 = (supp or {}).get("w1") or {}
    sp1 = [(s1.get(k), lab) for k, lab in (("er_minus_awp_appr", APPR), ("er_minus_awp_send", SEND)) if s1.get(k)]
    if sp1:
        if s1.get("n") != w1.get("spenders"):
            E.problem(f"supplementary W1 n={s1.get('n')} differs from the W1 spender cohort {w1.get('spenders')}")
        counts += [int(r.get("n_boot") or 0) for r, _ in sp1]
        n = E.fint(s1.get("n"))
        blocks.append((f"W1, spenders ($n={n}$)", f"W1 spenders $n={n}$",
                       [("EndorseRank minus AWP", E.LABEL_WORDS[lab], r) for r, lab in sp1]))
    if not blocks:
        E.SKIPPED.append("endorserank-awp-holdout (no EndorseRank-AWP contrasts)")
        return
    lines = []
    for title, _, rows in blocks:
        if lines:
            lines.append("\\midrule")
        lines.append(header(title, 7))
        lines += [E.contrast_line(name, r, lab) for name, lab, r in rows]
    sizes = "; ".join(size for _, size, _ in blocks)
    caption = (
        f"Paired bootstrap differences between EndorseRank and AWP out of window ({sizes}). None of them enters rule "
        "A or the two applied criteria of rule B: the rows were computed after the labels were known"
        + (", the W1 rows from the saved W1 scores with the resamples of Table~\\ref{tab:fresh-holdout}" if sp1 else "")
        + f". Within each block $a$ and $b$ share the contract resamples ({E.fint(max(counts))}; seed {seed})."
    )
    srcs = [E.SOURCES["w0"]] + ([E.SOURCES["supp"]] if sp1 else []) + [E.SOURCES["w1"]]
    emit("endorserank-awp-holdout", caption, E.tabular("llccccc", E.CONTRAST_HEAD_LABEL, lines), srcs)


def t_fresh_holdout(w1: dict, seed: int, cfg: dict) -> None:
    E.begin("fresh-holdout")
    sp = w1.get("spender_taus") or {}
    lines = E.method_rows(W1_ROWS, lambda m: " & ".join(E.tc((sp.get(m) or {}).get(lab), f"{m} {lab}")
                                                        for lab in (APPR, SEND)))
    rw = cfg["registered_window"]
    kinds = w1.get("spender_account_types") or {}
    cov = ((w1.get("cohort_coverage") or {}).get("spenders_w1") or {}).get("union_graph") or {}
    caption = (
        f"Window W1: Kendall $\\tau$ between scores frozen at {E.tex_date(rw['score_end'])} on the contract graph and "
        f"the two spender labels, counted from {E.tex_date(rw['outcome_start'])} to {E.tex_date(rw['outcome_end'])}. "
        f"The spenders are the $n={E.fint(w1.get('spenders'))}$ contracts among the {E.fint(sum(kinds.values()))} "
        f"spenders of the labels ({E.fint(kinds.get('user_account', 0))} user accounts and "
        f"{E.fint(kinds.get('system', 0))} system address are left out); {E.fint(w1.get('gained_new_approvals'))} of "
        f"them gained a new approval pair and {E.fint(w1.get('gained_new_senders'))} a new sender, and "
        f"{E.fint(cov.get('n'))} ({pct(cov.get('share'))}) lie in the union graph. C-PR ($\\lambda=0$) is the "
        "comparator of the two applied criteria of rule B and AWP that of the first sensitivity analysis "
        "(Table~\\ref{tab:fresh-contrasts}); EndorseRank is in Table~\\ref{tab:fresh-posthoc}. The baselines are raw "
        f"counts on the contract graph at the freeze. {E.boot_note(seed)}"
    )
    head = (f"Score at {E.tex_date(rw['score_end']).replace('~', ' ')} & New approval pairs ($\\tau$ [95\\% CI]) & "
            "New transfer senders ($\\tau$ [95\\% CI])")
    emit("fresh-holdout", caption, E.tabular("lcc", head, lines), [E.SOURCES["w1"]])


READING = {True: "both applied criteria hold", False: "not met"}


def _reading_line(block: dict, name: str) -> str:
    f1, f2 = bool((block.get("F1") or {}).get("holds")), bool((block.get("F2") or {}).get("holds"))
    if bool(block.get("f1_f2_hold")) != (f1 and f2):
        E.problem(f"{name}: f1_f2_hold does not follow from F1 and F2")
    if block.get("rule_b_reading") != READING[f1 and f2]:
        E.problem(f"{name}: the reading {block.get('rule_b_reading')!r} does not follow from F1 and F2")
    if bool(block.get("rule_b_not_met")) != (not (f1 and f2)):
        E.problem(f"{name}: rule_b_not_met does not follow from F1 and F2")
    return f"\\multicolumn{{7}}{{l}}{{Reading of F1 and F2}} & {READING[f1 and f2]} \\\\"


def t_fresh_contrasts(w1: dict, seed: int) -> None:
    E.begin("fresh-contrasts")
    rule = w1.get("rule_b") or {}
    if not rule:
        E.SKIPPED.append("fresh-contrasts (no rule_b)")
        return
    if sorted(w1.get("applied_criteria") or []) != ["F1", "F2"]:
        E.problem(f"applied criteria are {w1.get('applied_criteria')}")
    delta = float(w1.get("delta"))
    comp = E.F_COMPARATOR
    lines = [header("F1 and F2, two of rule B's registered criteria: C-PR ($\\lambda=0.5$) against its transfer layer "
                    "walked alone, C-PR ($\\lambda=0$)", 8)]
    lines += [E._f_line(k, rule.get(k), comp.get(k, "cpr_l0"), delta, "F1 and F2") for k in ("F1", "F2")]
    lines.append(_reading_line(rule, "F1 and F2"))
    lines += ["\\midrule", header("Reported beside them", 8)]
    lines += [E._f_line(k, rule.get(k), comp.get(k, "cpr_l0"), delta, "F6") for k in ("F6a", "F6b") if k in rule]
    for key, title, c in (("sensitivity_awp", "Sensitivity analysis 1: AWP as the comparator", "awp"),
                          ("sensitivity_isolated",
                           "Sensitivity analysis 2: contracts outside a graph kept as isolated nodes", "cpr_l0")):
        s = w1.get(key) or {}
        if not s:
            E.problem(f"no {key}")
            continue
        lines += ["\\midrule", header(title, 8)]
        lines += [E._f_line(k, s.get(k), comp.get(k, c), delta, key) for k in ("F1", "F2", "F6a", "F6b") if k in s]
        lines.append(_reading_line(s, key))
    caption = (
        "Window W1: the paired contrasts F1 and F2, two of the registered criteria of rule B, with their verdicts on "
        "the scores of the contract graph, and the spender parts of the two registered sensitivity analyses. Under "
        "the registration the rule holds only if each of its criteria holds; this analysis applies F1 and F2 only, "
        "so its reading is ``not met'' when one of them fails and ``both applied criteria hold'' when both hold. "
        "The criteria and the margin are those of the registration of W1; they are applied here as a re-analysis "
        "after the registered results were known. $\\Delta\\tau=\\tau(a)-\\tau(b)$, with C-PR ($\\lambda=0.5$) as "
        "$a$. Superiority holds when the interval lies above zero; non-inferiority holds when its lower end lies "
        f"above $-\\delta=-{delta:.2f}$; F6a, the first part of rule A, holds when the interval contains zero or "
        f"lies above it. Every contrast is on the spenders ($n={E.fint(w1.get('spenders'))}$ contracts) of "
        f"Table~\\ref{{tab:fresh-holdout}}. {E.boot_note(seed)}"
    )
    head = " & Contrast & Label & Test & $\\tau(a)$ & $\\tau(b)$ & $\\Delta\\tau$ [95\\% CI] & Verdict"
    emit("fresh-contrasts", caption, E.tabular("lllcccll", head, lines), [E.SOURCES["w1"]])


def t_fresh_posthoc(w1: dict, supp: dict | None, seed: int, cfg: dict) -> None:
    E.begin("fresh-posthoc")
    sp, res = w1.get("spender_taus") or {}, w1.get("endorserank_results") or {}
    if "endorserank" not in sp:
        E.SKIPPED.append("fresh-posthoc (no EndorseRank in W1)")
        return
    order = (*W1_BASELINES[:1], W1_BASELINES[2], None, ("endorserank", "EndorseRank"),
             ("endorserank_activity", "EndorseRank, restarts by approving activity"), ("awp", "AWP"),
             ("cpr_l50", METHOD_LABELS["cpr_l50"]))
    lines = E.method_rows(order, lambda m: " & ".join(E.tc((sp.get(m) or {}).get(lab), f"{m} {lab}")
                                                      for lab in (APPR, SEND)))
    names = (("endorserank_minus_degree_appr", "EndorseRank minus in-approve degree, new approval pairs"),
             ("awp_minus_degree_send", "AWP minus transfer in-degree, new transfer senders"))
    if res:
        lines.append("\\midrule")
        for key, name in names:
            lines.append(f"{name} & \\multicolumn{{2}}{{l}}{{{E.delta_math(res.get(key), key)}}} \\\\")
    s1 = (supp or {}).get("w1") or {}
    act = (("er_activity_minus_degree_appr", "EndorseRank (activity restarts) minus in-approve degree, new approval pairs"),
           ("er_activity_minus_er_appr", "EndorseRank (activity restarts) minus EndorseRank, new approval pairs"),
           ("er_activity_minus_er_send", "EndorseRank (activity restarts) minus EndorseRank, new transfer senders"))
    act = [(k, name) for k, name in act if s1.get(k)]
    if act:
        if s1.get("n") != w1.get("spenders"):
            E.problem(f"supplementary W1 n={s1.get('n')} differs from the W1 spender cohort {w1.get('spenders')}")
        lines.append("\\midrule")
        for key, name in act:
            lines.append(f"{name} & \\multicolumn{{2}}{{l}}{{{E.delta_math(s1.get(key), key)}}} \\\\")
    rw = cfg["registered_window"]
    caption = (
        "EndorseRank and its variant with activity restarts on the spender cohort and labels of window W1 "
        f"($n={E.fint(w1.get('spenders'))}$ contracts). Neither these rows nor the contrasts below them belong to "
        "the two applied criteria of rule B, and the contrasts were not named in the registration."
        + (" The contrasts of EndorseRank with activity restarts were computed afterwards from the saved W1 scores."
           if act else "")
        + " The AWP, C-PR and degree rows repeat Table~\\ref{tab:fresh-holdout}, and every contrast uses the same "
        "contract resamples; the differences between EndorseRank and AWP are in "
        "Table~\\ref{tab:endorserank-awp-holdout}, and those of C-PR in Table~\\ref{tab:cpr-contrasts}. "
        f"{E.boot_note(seed)}"
    )
    head = (f"Score at {E.tex_date(rw['score_end']).replace('~', ' ')} & New approval pairs ($\\tau$ [95\\% CI]) & "
            "New transfer senders ($\\tau$ [95\\% CI])")
    emit("fresh-posthoc", caption, E.tabular("lcc", head, lines), [E.SOURCES["w1"]] + ([E.SOURCES["supp"]] if act else []))


def t_cpr_contrasts(w0: dict, w1: dict, supp: dict | None, seed: int) -> None:
    """C-PR (lambda = 0.5) against every other score and the four raw counts, both windows (spender labels)."""
    E.begin("cpr-contrasts")
    cs = E.cpr_supp(supp)
    if not cs:
        E.SKIPPED.append("cpr-contrasts (no C-PR contrasts in supplementary.json)")
        return
    s0, s1 = cs["w0"], cs["w1"]
    if s0.get("n") != w0.get("spenders") or s1.get("n") != w1.get("spenders"):
        E.problem("supplementary spender cohorts differ from the holdout summaries")
    rb, sa, er = w1.get("rule_b") or {}, w1.get("sensitivity_awp") or {}, w1.get("endorserank_results") or {}
    b0 = {r["outcome"]: r for r in w0.get("baseline_contrasts") or []}
    b1 = w1.get("baseline_contrasts") or {}
    A, B, S, U = "$^{\\mathrm{A}}$", "$^{\\mathrm{B}}$", "$^{\\mathrm{S}}$", "$^{\\mathrm{U}}$"

    def w0c(key, b, outcome):
        return E._w0_contrast(w0, key, "cpr_l50", b, outcome)

    def supp_row(key: str):
        return [(s0.get(f"cpr_minus_{key}_{k}"), "") for k in ("appr", "send")] \
            + [(s1.get(f"cpr_minus_{key}_{k}"), "") for k in ("appr", "send")]

    rows = [
        (E.SHORT["cpr_l100"], [(w0c("contrasts_prefixed", "cpr_l100", APPR), A), (s0.get("cpr_minus_l100_send"), ""),
                               (rb.get("F6a"), B), (s1.get("cpr_minus_l100_send"), "")]),
        (E.SHORT["cpr_l0"], [(w0c("contrasts_after", "cpr_l0", APPR), ""), (w0c("contrasts_prefixed", "cpr_l0", SEND), A),
                             (rb.get("F1"), B), (rb.get("F2"), B)]),
        ("EndorseRank", [(w0c("contrasts_after", "endorserank", APPR), ""), (s0.get("cpr_minus_er_send"), ""),
                         (er.get("cpr_minus_endorserank_appr"), ""), (s1.get("cpr_minus_er_send"), "")]),
        ("EndorseRank (activity restarts)", supp_row("er_activity")),
        ("AWP", [(w0c("contrasts_after", "awp", APPR), ""), (w0c("contrasts_after", "awp", SEND), ""),
                 (sa.get("F1"), S), (sa.get("F2"), S)]),
        ("S-PR", supp_row("spr")),
        ("In-approve degree at the freeze", supp_row("degree")),
        ("In-approve value at the freeze", supp_row("approve_value")),
        ("Transfer in-degree at the freeze", supp_row("in_degree")),
        ("Union in-degree at the freeze", [(b0.get(APPR), U), (b0.get(SEND), U),
                                           (b1.get("cpr_minus_union_in_degree_appr"), U),
                                           (b1.get("cpr_minus_union_in_degree_send"), U)]),
    ]
    cols = ("W0 approvals", "W0 senders", "W1 approvals", "W1 senders")
    lines = [f"{label} & " + " & ".join(E._stack_delta(r, f"C-PR minus {label}, {c}", m)
                                        for (r, m), c in zip(cells, cols)) + " \\\\" for label, cells in rows]
    n0, n1 = s0.get("recv_n"), s1.get("recv_n")
    lines += ["\\midrule",
              header(f"Spenders that had received a transfer from another contract before the freeze "
                     f"(W0 $n={E.fint(n0)}$, W1 $n={E.fint(n1)}$)", 5)]
    lines.append("AWP & " + " & ".join(
        [E._stack_delta(s0.get(f"recv_cpr_minus_awp_{k}"), f"received W0 AWP {k}") for k in ("appr", "send")]
        + [E._stack_delta(s1.get(f"recv_cpr_minus_awp_{k}"), f"received W1 AWP {k}") for k in ("appr", "send")])
        + " \\\\")
    lines.append("In-approve degree at the freeze & "
                 f"{E._stack_delta(s0.get('recv_cpr_minus_degree_appr'), 'received W0 degree')} & --- & "
                 f"{E._stack_delta(s1.get('recv_cpr_minus_degree_appr'), 'received W1 degree')} & --- \\\\")
    caption = (
        "Paired contrasts of C-PR ($\\lambda=0.5$) with every other score of this study and with the four raw counts "
        f"of the contract graph, on the spender labels of W0 ($n={E.fint(w0.get('spenders'))}$ contracts) and W1 "
        f"($n={E.fint(w1.get('spenders'))}$). Each cell is $\\Delta\\tau=\\tau_{{\\text{{C-PR}}}}-\\tau_b$ over its "
        "95\\% interval; within a cohort every cell uses the same resamples. Cells marked $^{\\mathrm{A}}$ are the "
        "contrasts of rule A, fixed in the analysis plan; $^{\\mathrm{B}}$ marks F1, F2 and F6a of the registration "
        "of W1 and $^{\\mathrm{S}}$ the contrasts of its first sensitivity analysis, with AWP as the comparator. These "
        "rules were fixed for the raw-unit analysis and are applied here to the scores of the contract graph. Cells "
        "marked $^{\\mathrm{U}}$, against the union in-degree, were named when the contract-graph analysis was "
        "defined and belong to no rule. Every other cell was computed after the labels were known and belongs to no "
        "rule. The lower block repeats the contrasts with AWP and the in-approve degree on the spenders that had "
        "received a transfer from another contract before the freeze, the spenders AWP can order; that restriction "
        f"was also chosen after the results were known. {E.boot_note(seed)}"
    )
    head = (" & \\multicolumn{2}{c}{W0 spenders} & \\multicolumn{2}{c}{W1 spenders} \\\\\n"
            "\\cmidrule(lr){2-3} \\cmidrule(lr){4-5}\n"
            "C-PR minus & New approval pairs & New transfer senders & New approval pairs & New transfer senders")
    emit("cpr-contrasts", caption, E.tabular("lcccc", head, lines),
         [E.SOURCES["w0"], E.SOURCES["w1"], E.SOURCES["supp"]])


def t_union_members(w0: dict, w1: dict, seed: int) -> None:
    """The main comparisons on the cohort members inside the union graph only (revision section 8)."""
    E.begin("union-members")
    u0, u1 = w0.get("in_union_graph") or {}, w1.get("in_union_graph") or {}
    if not (u0 and u1):
        E.SKIPPED.append("union-members (no in_union_graph)")
        return

    def find(rows, a, b, outcome):
        return next((r for r in rows or [] if r.get("a") == a and r.get("b") == b and r.get("outcome") == outcome), None)

    def full0(a, b, outcome):
        for key in ("contrasts_prefixed", "contrasts_after", "baseline_contrasts"):
            r = find(w0.get(key), a, b, outcome)
            if r:
                return r
        return None

    def in0(a, b, outcome):
        for key in ("contrasts_prefixed", "contrasts_after", "baseline_contrasts"):
            r = find(u0.get(key), a, b, outcome)
            if r:
                return r
        return None

    rb, bc, c1 = w1.get("rule_b") or {}, w1.get("baseline_contrasts") or {}, u1.get("contrasts") or {}
    rows = [
        ("W0", "C-PR minus C-PR ($\\lambda=1$)", APPR, full0("cpr_l50", "cpr_l100", APPR), in0("cpr_l50", "cpr_l100", APPR)),
        ("W0", "C-PR minus C-PR ($\\lambda=0$)", SEND, full0("cpr_l50", "cpr_l0", SEND), in0("cpr_l50", "cpr_l0", SEND)),
        ("W0", "C-PR minus union in-degree", APPR, full0("cpr_l50", "t1_in_degree_union", APPR),
         in0("cpr_l50", "t1_in_degree_union", APPR)),
        ("W0", "C-PR minus union in-degree", SEND, full0("cpr_l50", "t1_in_degree_union", SEND),
         in0("cpr_l50", "t1_in_degree_union", SEND)),
        None,
        ("W1", "C-PR minus C-PR ($\\lambda=0$)", APPR, rb.get("F1"), c1.get("cpr_minus_cpr_l0_appr")),
        ("W1", "C-PR minus C-PR ($\\lambda=0$)", SEND, rb.get("F2"), c1.get("cpr_minus_cpr_l0_send")),
        ("W1", "C-PR minus C-PR ($\\lambda=1$)", APPR, rb.get("F6a"), c1.get("cpr_minus_cpr_l100_appr")),
        ("W1", "C-PR minus union in-degree", APPR, bc.get("cpr_minus_union_in_degree_appr"),
         c1.get("cpr_minus_union_in_degree_appr")),
        ("W1", "C-PR minus union in-degree", SEND, bc.get("cpr_minus_union_in_degree_send"),
         c1.get("cpr_minus_union_in_degree_send")),
    ]
    lines = []
    for r in rows:
        if r is None:
            lines.append("\\midrule")
            continue
        w, name, lab, full, inside = r
        lines.append(f"{w} & {name} & {E.LABEL_WORDS[lab]} & {E._dci(full, f'{w} {name} cohort')} & "
                     f"{E._dci(inside, f'{w} {name} inside')} \\\\")
    caption = (
        "The main out-of-window contrasts on the whole spender cohorts and on their members inside the union graph "
        f"only (W0: {E.fint(u0.get('n'))} of {E.fint(w0.get('spenders'))} contracts; W1: {E.fint(u1.get('n'))} of "
        f"{E.fint(w1.get('spenders'))}). A spender outside the union graph ends no pair between contracts and scores "
        "zero under every score and baseline, so on the whole cohort a contrast also reflects how the two scores "
        "order the members with a pair against those without one. The right column decides no rule. "
        f"$\\Delta\\tau$ with 95\\% paired bootstrap interval ({E.fint(max(E.STATE['nboot']) if E.STATE['nboot'] else None)} "
        f"resamples, seed {seed})."
    )
    head = "Window & Contrast ($a$ minus $b$) & Label & Whole cohort & Inside the union graph"
    emit("union-members", caption, E.tabular("lllcc", head, lines), [E.SOURCES["w0"], E.SOURCES["w1"]])


def t_uncapped(rob: dict, w0: dict, w1: dict, seed: int) -> None:
    """The uncapped allowance layer beside the capped one (revision section 5); decides no rule."""
    E.begin("uncapped-sensitivity")
    unc = rob.get("uncapped_allowances") or {}
    u0, u1 = unc.get("w0") or {}, unc.get("w1") or {}
    if not (u0 and u1):
        E.SKIPPED.append("uncapped-sensitivity (no uncapped_allowances)")
        return
    t0c, t0u, t1c, t1u = w0.get("taus") or {}, u0.get("taus") or {}, w1.get("spender_taus") or {}, u1.get("spender_taus") or {}
    order = (("endorserank", "t1_in_approve_degree", "t1_in_degree_union"), ("in_approve_degree", "in_degree_union"))
    names = (("endorserank", "EndorseRank"), ("cpr_l100", METHOD_LABELS["cpr_l100"]), ("cpr_l50", METHOD_LABELS["cpr_l50"]),
             ("awp", "AWP"), None, ("@degree", "In-approve degree at the freeze"), ("@union", "Union in-degree at the freeze"))
    del order

    def key0(m): return {"@degree": "t1_in_approve_degree", "@union": "t1_in_degree_union"}.get(m, m)
    def key1(m): return {"@degree": "in_approve_degree", "@union": "in_degree_union"}.get(m, m)

    def cell(m: str) -> str:
        cells = []
        for capped, uncapped, key in ((t0c, t0u, key0(m)), (t1c, t1u, key1(m))):
            for lab in (APPR, SEND):
                cells.append(f"{E.f3(((capped.get(key) or {}).get(lab) or {}).get('kendall_tau'), f'{key} capped')} / "
                             f"{E.f3(((uncapped.get(key) or {}).get(lab) or {}).get('kendall_tau'), f'{key} uncapped')}")
        return " & ".join(cells)

    lines = E.method_rows(names, cell)

    def find(rows, a, b, outcome):
        return next((r for r in rows or [] if r.get("a") == a and r.get("b") == b and r.get("outcome") == outcome), None)

    c1 = u1.get("contrasts") or {}
    rb = w1.get("rule_b") or {}
    lines += ["\\midrule", header("Contrasts ($\\Delta\\tau$ [95\\% CI]), capped / uncapped", 5)]
    pairs = (
        ("W0: C-PR minus C-PR ($\\lambda=1$), new approval pairs",
         find(w0.get("contrasts_prefixed"), "cpr_l50", "cpr_l100", APPR), find(u0.get("contrasts_prefixed"), "cpr_l50", "cpr_l100", APPR)),
        ("W0: C-PR minus C-PR ($\\lambda=0$), new transfer senders",
         find(w0.get("contrasts_prefixed"), "cpr_l50", "cpr_l0", SEND), find(u0.get("contrasts_prefixed"), "cpr_l50", "cpr_l0", SEND)),
        ("W1: C-PR minus C-PR ($\\lambda=0$), new approval pairs", rb.get("F1"), c1.get("cpr_minus_cpr_l0_appr")),
        ("W1: C-PR minus C-PR ($\\lambda=0$), new transfer senders", rb.get("F2"), c1.get("cpr_minus_cpr_l0_send")),
    )
    for name, capped, uncapped in pairs:
        lines.append(f"{name} & \\multicolumn{{2}}{{c}}{{{E._dci(capped, name + ' capped')}}} & "
                     f"\\multicolumn{{2}}{{c}}{{{E._dci(uncapped, name + ' uncapped')}}} \\\\")
    p0, p1 = u0.get("allowance_pairs") or {}, u1.get("allowance_pairs") or {}
    caption = (
        "Sensitivity to the balance cap: Kendall $\\tau$ on the two spender labels with the allowance layer capped "
        "at the owner's balance (the main analysis) and uncapped, where every positive latest allowance between "
        "contracts counts at its own value. Each cell reads capped / uncapped. Without the cap the allowance layer "
        f"has {E.fint(p0.get('uncapped'))} pairs at $t_1$ against {E.fint(p0.get('capped'))} with it, and "
        f"{E.fint(p1.get('uncapped'))} against {E.fint(p1.get('capped'))} at $T_{{\\mathrm{{obs}}}}$. AWP reads no "
        "allowance, so its two values are equal. In the lower block the left cell is the contrast of the main "
        "analysis and the right cell the same contrast on the uncapped layer. The uncapped layer decides no rule. "
        f"Intervals: 95\\% paired bootstrap ({E.fint(max(E.STATE['nboot']) if E.STATE['nboot'] else None)} resamples, "
        f"seed {seed})."
    )
    head = (" & \\multicolumn{2}{c}{W0 spenders} & \\multicolumn{2}{c}{W1 spenders} \\\\\n"
            "\\cmidrule(lr){2-3} \\cmidrule(lr){4-5}\n"
            "Score & New approval pairs & New transfer senders & New approval pairs & New transfer senders")
    emit("uncapped-sensitivity", caption, E.tabular("lcccc", head, lines),
         [E.SOURCES["rob"], E.SOURCES["w0"], E.SOURCES["w1"]])


def t_sybil_threshold(sybil: dict) -> None:
    E.begin("sybil-threshold")
    th = sybil.get("balance_threshold") or {}
    if not th:
        E.SKIPPED.append("sybil-threshold (no balance_threshold)")
        return

    def row(label: str, x: dict, pairs, share) -> str:
        star = x.get("star") or {}
        reach = ((x.get("farm_size_to_reach_cohort_quantile") or {}).get("p100") or {}).get("farm_addresses")
        return (f"{label} & {E.fint(pairs)} & {share} & {E.fint(x.get('owners_kept', x.get('owners')))} & "
                f"{E.fint((x.get('graph') or {}).get('nodes'))} & {E.f3(x.get('cohort_tau_with_main'), 'tau') if 'cohort_tau_with_main' in x else '1.000'} & "
                f"{E.f3(star.get('ratio_to_highest'), 'star ratio')} & {E.fint(np.ceil(reach) if reach is not None else None)} \\\\")

    g = sybil.get("graph") or {}
    lines = [row("None (main analysis)", sybil, g.get("edges"), "100\\%"), "\\midrule"]
    for key, x in th.items():
        lines.append(row(f"$\\theta=\\${key}$", x, x.get("pairs_kept"), pct(x.get("share_of_pairs_kept"))))
    farm = sybil.get("contract_farm") or {}
    gas = farm.get("evm_gas") or {}
    v = (farm.get("value_weight") or {}).get("V_at_usd") or {}
    star = sybil.get("star") or {}
    caption = (
        "The Sybil cost model on the EndorseRank graph of contracts at $T_{\\mathrm{obs}}$, and its sensitivity to a "
        "balance threshold $\\theta$: the graph keeps only the allowance pairs whose capped value is at least "
        "$\\theta$, so that every farm contract must hold $\\theta$ of the token at the freeze. Columns: the pairs "
        "kept and their share, the owners and the nodes of the graph, the rank agreement $\\tau$ of the matched "
        "cohort's scores with those of the main analysis, the score of the target of a star farm of "
        f"{E.fint(star.get('m'))} contracts as a share of the highest EndorseRank in the cohort, and the farm "
        "contracts that the closed form needs to reach that highest score. Every farm address is a contract: a "
        f"creation costs at least {E.fint(gas.get('creation_by_create_at_least'))} gas from a factory and "
        f"{E.fint(gas.get('creation_by_transaction_at_least'))} gas by its own transaction, plus "
        f"{E.fint(gas.get('G_codedeposit_per_byte'))} gas per byte of code (execution gas of the EVM fee schedule, "
        "without the fee for posting data to L1). The value weight of an allowance backed by one dollar is "
        f"$V={E.f3(v.get('1'), 'V at 1')}$, so a larger balance buys no further weight. The quantities decide no "
        "rule."
    )
    head = ("Threshold & Pairs kept & Share & Owners & Nodes & $\\tau$ with main & Star target / highest & "
            "Farm contracts to the top")
    emit("sybil-threshold", caption, E.tabular("lrrrrccr", head, lines), [E.SOURCES["sybil"]])


def t_tokens(desc: dict, cfg: dict) -> None:
    """The five tokens: feed, price days and the Chainlink check inside the windows."""
    E.begin("usd-tokens")
    import pandas as pd
    lst = pd.read_csv(USD_INPUTS / "listed_tokens.csv")
    sel = lst[lst["selected"].astype(str).str.lower() == "true"]
    win, cl = desc.get("price_days") or {}, desc.get("chainlink_check_in_windows") or {}
    if not win or not cl:
        E.problem("no price_days or chainlink_check_in_windows in describe.json")
    days = {t["address"]: t for t in win.get("per_token") or []}
    chk = cl.get("per_token") or {}
    al = {t["token"]: t for t in ((desc.get("allowances") or {}).get("tobs") or {}).get("per_token") or []}
    sel = sel.assign(_n=sel["address"].map(lambda a: (al.get(a) or {}).get("n_latest_positive", 0))).sort_values(
        "_n", ascending=False)
    lines = []
    for _, r in sel.iterrows():
        d, c, a = days.get(r["address"]) or {}, chk.get(r["symbol"]) or {}, al.get(r["address"]) or {}
        if not d or not a:
            E.problem(f"no describe row for {r['symbol']}")
        sym = "USDT0" if r["symbol"] == "USD₮0" else r["symbol"]
        lines.append(
            f"{sym} & \\texttt{{{r['address'][:6]}\\ldots{{}}{r['address'][-4:]}}} & {E.fint(r['decimals'])} & "
            f"{r['feed']} ({r['feed_category']}) & {E.fint(a.get('n_latest_positive'))} & {E.fint(a.get('n_positive_eff'))} & "
            f"{E.fint(d.get('second_key_days'))} & {E.fint(d.get('filled_days'))} & {E.fint(d.get('spike_days'))} & "
            f"{100 * (E._num(c.get('median')) or float('nan')):.2f} / {100 * (E._num(c.get('max')) or float('nan')):.2f} \\\\")
    first, last = cfg["holdout"]["start_ts"], cfg["registered_window"]["outcome_end"]
    import datetime as dt
    n_days = (dt.date.fromisoformat(last[:10]) - dt.date.fromisoformat(first[:10])).days + 1
    if win.get("days") != n_days:
        E.problem(f"price_days.days is not the {n_days} days from {first[:10]} to {last[:10]}")
    ev = desc.get("events") or {}
    caption = (
        "The five tokens of the analysis, with their Chainlink feed (market-risk category), the positive latest "
        "allowances between contracts at $T_{\\mathrm{obs}}$ and those that stay positive after the balance cap, the "
        "days of the price series filled from the second DefiLlama key, filled from the previous day and replaced as "
        f"one-day errors (of the {E.fint(n_days)} days from {E.tex_date(first)} to {E.tex_date(last)} that the windows "
        "cover), and the median and largest absolute difference, in percent, between the DefiLlama price and the "
        f"Chainlink feed read on the chain on the {E.fint(cl.get('dates'))} check dates among those days. The "
        f"five-token events of the typing window number {E.fint(ev.get('five_token_rows'))}; "
        f"{E.fint(ev.get('rows_between_contracts'))} of them have a contract at both ends."
    )
    head = ("Token & Address & Dec. & Chainlink feed & Allowances & After the cap & 2nd key & Filled & Errors & "
            "CL diff.\\ (\\%)")
    emit("usd-tokens", caption, E.tabular("llrlrrrrrr", head, lines),
         [USD_INPUTS / "listed_tokens.csv", SRC["describe"], USD_INPUTS / "chainlink_check.json"])


def t_registered_vs_contract(reg: dict, rev: dict, seed: int, cfg: dict) -> None:
    """The decision contrasts of the registered analysis, as registered, beside the same contrasts on the scores of
    the contract graph; rule B by the two criteria this analysis applies (revision section 11)."""
    E.begin("registered-vs-revised")
    rows: list[tuple[str, str, str]] = []

    def both(label: str, get, kind: str = "contrast") -> None:
        cells = []
        for name, d in (("registered", reg), ("contract graph", rev)):
            try:
                v = get(d)
            except (KeyError, TypeError, StopIteration):
                v = None
            if kind == "contrast":
                cells.append(E._dci(v, f"{name} {label}"))
            elif kind == "count":
                cells.append(E.fint(v, f"{name} {label}"))
            elif kind == "tau":
                cells.append(E.tc(v, f"{name} {label}"))
            elif kind == "reading":
                cells.append(v if v else "---")
                if not v:
                    E.problem(f"no reading for {name} {label}")
            else:
                cells.append(E._yes(v, *kind.split("/")) if "/" in kind else E._yes(v))
        rows.append((label, cells[0], cells[1]))

    def pre(d, a, b):
        return next(r for r in d["w0"]["contrasts_prefixed"] if r["a"] == a and r["b"] == b)

    def after(d, a, b, out):
        return next(r for r in d["w0"]["contrasts_after"] if r["a"] == a and r["b"] == b and r["outcome"] == out)

    def reading(block: dict) -> str:
        """'not met (F2 fails)' or 'both applied criteria hold', from the verdicts of F1 and F2 alone."""
        failed = [k for k in ("F1", "F2") if not block[k]["holds"]]
        if not failed:
            return READING[True]
        return f"{READING[False]} ({' and '.join(failed)} fail{'s' if len(failed) == 1 else ''})"

    both("Matched cohort (contracts)", lambda d: d["same"]["cohort"], "count")
    both("W0 spender cohort", lambda d: d["w0"]["spenders"], "count")
    both("W1 spender cohort", lambda d: d["w1"]["spenders"], "count")
    both("EndorseRank vs.\\ AWP, same window ($\\tau$)", lambda d: d["same"]["inter_method"]["endorserank_vs_awp"], "tau")
    rows.append(("\\midrule", "", ""))
    both("A, W0: C-PR minus C-PR ($\\lambda=1$), new approval pairs", lambda d: pre(d, "cpr_l50", "cpr_l100"))
    both("A, W0: C-PR minus C-PR ($\\lambda=0$), new transfer senders", lambda d: pre(d, "cpr_l50", "cpr_l0"))
    both("Rule A, primary part", lambda d: d["w0"]["rule_a_primary"]["pass"], "verdict")
    both("Rule A, secondary part", lambda d: d["same"]["rule_a_secondary"]["pass"], "verdict")
    rows.append(("\\midrule", "", ""))
    for k, lab in (("F1", "new approval pairs"), ("F2", "new transfer senders")):
        both(f"B, {k}: C-PR minus C-PR ($\\lambda=0$), {lab}", lambda d, k=k: d["w1"]["rule_b"][k])
    both("F1 and F2, two of rule B's registered criteria", lambda d: reading(d["w1"]["rule_b"]), "reading")
    both("F1 and F2, sensitivity 1 (AWP as comparator)", lambda d: reading(d["w1"]["sensitivity_awp"]), "reading")
    both("F1 and F2, sensitivity 2 (isolated nodes)", lambda d: reading(d["w1"]["sensitivity_isolated"]), "reading")
    both("F6 (rule A, primary part, on W1)", lambda d: d["w1"]["rule_b"]["F6"], "holds/fails")
    rows.append(("\\midrule", "", ""))
    both("W0: EndorseRank minus in-approve degree, new pairs", lambda d: after(d, "endorserank", "t1_in_approve_degree", APPR))
    both("W0: AWP minus transfer in-degree, new senders", lambda d: after(d, "awp", "t1_in_degree", SEND))
    both("W1: EndorseRank minus in-approve degree, new pairs",
         lambda d: d["w1"]["endorserank_results"]["endorserank_minus_degree_appr"])
    both("W1: AWP minus transfer in-degree, new senders", lambda d: d["w1"]["endorserank_results"]["awp_minus_degree_send"])
    lines = [r[0] if r[0] == "\\midrule" else f"{r[0]} & {r[1]} & {r[2]} \\\\" for r in rows]
    nb = sorted(E.STATE["nboot"])
    caption = (
        "Decision contrasts and verdicts of the registered analysis (amounts in raw base units, every ERC-20 token, "
        f"$b=1$, scores from every event since {E.tex_date(cfg['bigquery']['scan_a']['start_ts'])}, graphs that hold "
        "every account of the cohort's events), exactly as obtained under the analysis plan and the W1 registration, "
        "beside the same contrasts on the scores of the contract graph (amounts in USD, the five tokens, scores from "
        "the twelve months before each freeze, nodes that are contracts other than smart accounts, each allowance "
        "counted up to its owner's balance). The contract-graph analysis was defined after the registered results "
        "were known; its column applies the registered rules and thresholds to its scores and is not a registered "
        "test. Under the registration rule B holds only if each of its criteria holds; the table applies two of "
        "them, F1 and F2, in both columns. The last block holds degree contrasts that no rule of either analysis "
        "decides; they are reported in both. $\\Delta\\tau$ with 95\\% paired bootstrap interval "
        f"({' and '.join(E.fint(x) for x in nb)} resamples, seed {seed}); the rules and their thresholds are in "
        "Sections~\\ref{sec:holdout-protocol} and~\\ref{sub:fresh-holdout}."
    )
    head = "Quantity & Registered analysis & Contract-graph analysis"
    emit("registered-vs-revised", caption, E.tabular("lcc", head, lines),
         [PROC_SHARED / "same-window" / "eval_summary.json", PROC_SHARED / "holdout-w0" / "eval_summary.json",
          PROC_SHARED / "registered-w1" / "eval_summary.json", E.SOURCES["same"], E.SOURCES["w0"], E.SOURCES["w1"]])


# --------------------------------------------------------------------------- main


# --------------------------------------------------------------------------- benchmark on the whole contract graph
#
# The benchmark of this variant times the whole contract graph at T_obs (every pair between contracts), and its
# scaling stages keep the pairs incident to a subsample of the matched cohort. The stage of the full cohort is not
# timed: scripts/run_benchmark.py reuses the main measurement for it (``reused_main``), which here is another graph
# than the pairs incident to the cohort. The tables below say so; export_latex.py's own tables describe graphs made
# of the cohort's events, where the two coincide.


def _cohort_stage_edges(rob: dict | None, n: int) -> tuple[int, int] | None:
    """Allowance and transfer pairs incident to the full cohort (the last sample-definition stage of the robustness run)."""
    for st in (rob or {}).get("sample_definition") or []:
        if int(st.get("n", -1)) == int(n) and st.get("allowance_edges") is not None:
            return int(st["allowance_edges"]), int(st["transfer_edges"])
    return None


def t_benchmark_runtime(bench: dict, n: int) -> None:
    E.begin("benchmark-runtime")
    main_ = bench.get("main") or {}

    def cell(m: str) -> str:
        x = main_.get(m)
        if not x:
            E.problem(f"no benchmark row for {m}")
            x = {}
        return (f"{E.f3(x.get('mean_s'), 'runtime')} & {E.f3(x.get('sd_s'), 'SD')} & {E.f1(x.get('peak_mb'), 'peak memory')} & "
                f"{E.fint(x.get('iterations'), 'iterations')} & {E.fint(x.get('nodes'), '|V|')} & {E.fint(x.get('edges'), '|E|')}")

    order = (("endorserank", "EndorseRank"), ("awp", "AWP"), None, ("cpr_l50", E.METHOD_LABELS["cpr_l50"]), ("spr", "S-PR"))
    lines = E.method_rows(order, cell)
    er, awp = main_.get("endorserank") or {}, main_.get("awp") or {}
    proto = bench.get("protocol") or {}
    runs, warm = int(proto.get("timed_runs", 5)), int(proto.get("warmup_runs", 1))
    caption = (
        "Computational benchmark on the contract graph at $T_{\\mathrm{obs}}$, which holds every pair between contracts "
        f"and not only the pairs of the matched cohort (AWP/EndorseRank runtime ratio {E.ratio(awp.get('mean_s'), er.get('mean_s'))} "
        f"at an edge ratio of {E.ratio(awp.get('edges'), er.get('edges'))}). Runtime = mean wall-clock seconds over {runs} "
        f"timed solver calls after {E.NUMBER_WORDS.get(warm, warm)} untimed warm-up, on which alone peak memory is traced; "
        f"SD over the same {runs} runs. A timed call turns an edge list into scores: node indexing, sparse-matrix assembly, "
        "row normalisation, restart vector and power iteration. $|V|$ and $|E|$ are the nodes and distinct edges of each "
        "method's solver graph. C-PR walks on the union of the allowance layer and the transfer layer, so its $|E|$ "
        "counts the distinct pairs of both; S-PR runs on the transfer layer, and its runtime and iterations include the "
        "solve of the allowance layer that supplies its restart vector. Table~\\ref{tab:benchmark-runs} lists every run."
    )
    head = "Method & Runtime (s) & SD (s) & Peak mem.\\ (MB) & Iters & $|V|$ & $|E|$"
    emit("benchmark-runtime", caption, E.tabular("lrrrrrr", head, lines), [E.SOURCES["bench"]])


def t_benchmark_scaling(bench: dict, rob: dict | None, n: int, cfg: dict) -> None:
    E.begin("benchmark-scaling")
    lines, whole = [], False
    for st in bench.get("scaling") or []:
        er, awp = st.get("endorserank") or {}, st.get("awp") or {}
        if st.get("reused_main"):
            whole = True
            lines.append("\\midrule")
            first = "Whole graph$^{a}$"
        else:
            first = E.fint(st.get("n"), "stage n")
        lines.append(
            f"{first} & {E.f3(er.get('mean_s'), 'ER runtime')} & {E.f3(awp.get('mean_s'), 'AWP runtime')} & "
            f"{E.ratio(awp.get('mean_s'), er.get('mean_s'))} & {E.ratio(awp.get('edges'), er.get('edges'))} & "
            f"{E.fint(er.get('nodes'), 'ER |V|')} & {E.fint(er.get('edges'), 'ER |E|')} & "
            f"{E.fint(awp.get('nodes'), 'AWP |V|')} & {E.fint(awp.get('edges'), 'AWP |E|')} \\\\")
    if not lines:
        E.SKIPPED.append("benchmark-scaling (no stages)")
        return
    runs = int((bench.get("protocol") or {}).get("timed_runs", 5))
    seed = bench.get("scaling_seed") or cfg["benchmark"]["scaling_seed"]
    note = ""
    if whole:
        inc = _cohort_stage_edges(rob, n)
        note = (" $^{a}$The measurement of Table~\\ref{tab:benchmark-runtime} on the whole contract graph, which holds "
                "every pair between contracts"
                + (f"; ${E.fint(inc[0])}$ allowance pairs and ${E.fint(inc[1])}$ transfer pairs are incident to the full "
                   f"cohort of $n={E.fint(n)}$ contracts, and the graph of those pairs has no timing of its own" if inc else "")
                + ".")
    caption = (
        "Runtime of EndorseRank (ER) and AWP on subsamples of the matched cohort and on the whole contract graph. The "
        f"numbered rows are deterministic SHA256 subsamples of the cohort (seed \\texttt{{{seed}}}); each keeps the pairs "
        "incident to its $n$ sampled contracts, so $|V|$ and $|E|$ of both solver graphs are reported per row. AWP/ER time "
        "and AWP/ER $|E|$ are the ratios of the two runtimes and of the two edge counts in the same row. Runtime = mean "
        f"wall-clock seconds over {runs} timed solver calls after one untimed warm-up.{note}"
    )
    head = "$n$ & ER (s) & AWP (s) & AWP/ER time & AWP/ER $|E|$ & ER $|V|$ & ER $|E|$ & AWP $|V|$ & AWP $|E|$"
    emit("benchmark-scaling", caption, E.tabular("rrrrrrrrr", head, lines), [E.SOURCES["bench"]])


def t_benchmark_runs(bench: dict, cfg: dict) -> None:
    E.begin("benchmark-runs")
    main_ = bench.get("main") or {}
    d0 = float((bench.get("protocol") or {}).get("damping", cfg["reputation"]["damping"]))
    blocks: list[tuple[str, list[tuple[str, dict]]]] = [(
        f"Whole contract graph, $d={d0:g}$",
        [(name, main_.get(m) or {}) for m, name in (("endorserank", "EndorseRank"), ("awp", "AWP"),
                                                      ("cpr_l50", E.METHOD_LABELS["cpr_l50"]), ("spr", "S-PR"))],
    )]
    for d, rows in sorted((bench.get("damping") or {}).items(), key=lambda kv: float(kv[0])):
        if abs(float(d) - d0) < 1e-12:
            continue  # the main measurement, reused
        blocks.append((f"Whole contract graph, $d={float(d):g}$",
                       [("EndorseRank", rows.get("endorserank") or {}), ("AWP", rows.get("awp") or {})]))
    for st in bench.get("scaling") or []:
        if st.get("reused_main"):
            continue
        blocks.append((f"Subsample of the cohort, $n={E.fint(st.get('n'))}$",
                       [("EndorseRank", st.get("endorserank") or {}), ("AWP", st.get("awp") or {})]))
    k = max((len(x.get("runs_s") or []) for _, rows in blocks for _, x in rows), default=0)
    if k == 0:
        E.SKIPPED.append("benchmark-runs (no timed runs)")
        return
    lines = []
    for title, rows in blocks:
        if lines:
            lines.append("\\midrule")
        lines.append(f"\\multicolumn{{{k + 3}}}{{l}}{{\\emph{{{title}}}}} \\\\")
        for name, x in rows:
            E._check_runs(x, f"{title} {name}")
            runs = list(x.get("runs_s") or [])
            cells = [E.f3(r, "run") for r in runs] + ["---"] * (k - len(runs))
            if len(runs) < k:
                E.problem(f"{title} {name} has {len(runs)} runs, not {k}")
            lines.append(f"{name} & {' & '.join(cells)} & {E.f3(x.get('mean_s'), 'mean')} & {E.f3(x.get('sd_s'), 'SD')} \\\\")
    head = "Method & " + " & ".join(f"Run {i + 1}" for i in range(k)) + " & Mean & SD"
    caption = (
        "Wall-clock seconds of every timed solver call of the benchmark, in the order the runs were made, with their "
        "mean and standard deviation. Each configuration had one untimed warm-up before its timed runs, and each graph "
        f"and setting was timed once: the $d={d0:g}$ rows of Table~\\ref{{tab:robustness-damping}} and the whole-graph row "
        "of Table~\\ref{tab:benchmark-scaling} are the first block, reused. The subsamples are those of "
        "Table~\\ref{tab:benchmark-scaling}."
    )
    emit("benchmark-runs", caption, E.tabular("l" + "r" * (k + 2), head, lines), [E.SOURCES["bench"]])


def t_robustness_sample_size(rob: dict, bench: dict | None, n: int, cfg: dict) -> None:
    E.begin("robustness-sample-size")
    stages = rob.get("sample_definition") or []
    if not stages:
        E.SKIPPED.append("robustness-sample-size (no stages)")
        return
    timed = {int(s["n"]): s for s in ((bench or {}).get("scaling") or []) if not s.get("reused_main")}
    lines, untimed = [], False
    for st in stages:
        er, awp = st.get("endorserank") or {}, st.get("awp") or {}
        cells = []
        for f in ("allowance", "transfer", "sybil_stability"):
            cells += [E.f3(er.get(f), f"ER {f} n={st.get('n')}"), E.f3(awp.get(f), f"AWP {f} n={st.get('n')}")]
        cells += [E.fint(st.get("allowance_edges"), "allowance pairs"), E.fint(st.get("transfer_edges"), "transfer pairs")]
        if bench is not None:
            b = timed.get(int(st["n"]))
            if b:
                be, ba = b.get("endorserank") or {}, b.get("awp") or {}
                cells += [E.f3(be.get("mean_s"), "ER runtime"), E.f3(ba.get("mean_s"), "AWP runtime")]
            else:
                untimed = True
                cells += ["--", "--"]
        lines.append(f"{E.fint(st.get('n'))} & {' & '.join(cells)} \\\\")
    seed = cfg["benchmark"]["scaling_seed"]
    runtime = ""
    if bench is not None:
        runtime = " Runtimes are the measurements of Table~\\ref{tab:benchmark-scaling}"
        runtime += ("; the graph of the pairs incident to the full cohort has no timing of its own (--)." if untimed else ".")
    caption = (
        "Sensitivity of the family means to the evaluation set: family-mean Kendall $\\tau$ of EndorseRank (ER) and AWP "
        f"on deterministic SHA256 subsamples of the matched cohort (seed \\texttt{{{seed}}}, full cohort $n={E.fint(n)}$ "
        "contracts), each row scored on the pairs incident to its contracts, whose numbers the columns $|E_A|$ (allowance) "
        "and $|E_T|$ (transfer) give; all.\\ = allowance, tr.\\ = transfer, Syb.\\ = Sybil stability. Rows are evaluated "
        "on different contract sets and on other graphs than the whole contract graph, so their $\\tau$ values are not "
        "comparable with Table~\\ref{tab:alignment-hybrid}; they show how much the statistic moves with the evaluation "
        f"population. No intervals were computed for the rows.{runtime}"
    )
    head = "$n$ & ER all. & AWP all. & ER tr. & AWP tr. & ER Syb. & AWP Syb. & $|E_A|$ & $|E_T|$"
    spec = "r" + "c" * 6 + "rr"
    if bench is not None:
        head += " & ER (s) & AWP (s)"
        spec += "rr"
    srcs = [E.SOURCES["rob"]] + ([E.SOURCES["bench"]] if bench is not None else [])
    emit("robustness-sample-size", caption, E.tabular(spec, head, lines), srcs)


def fig_runtime_scaling(bench: dict) -> None:
    """Runtime on the subsamples of the cohort, with the whole contract graph as a separate last position."""
    import numpy as np
    plt = E._style()
    stages = bench.get("scaling") or []
    if not stages:
        E.SKIPPED.append("runtime-scaling.pdf (no stages)")
        return
    sub = [s for s in stages if not s.get("reused_main")]
    whole = [s for s in stages if s.get("reused_main")]
    x_sub = np.arange(len(sub), dtype=float)
    x_whole = float(len(sub)) + 0.35
    fig, ax = plt.subplots(figsize=(5.8, 3.8))
    for m, name, color, marker, dy in (("endorserank", "EndorseRank", E.BLUE, "o", -11), ("awp", "AWP", E.RED, "s", 7)):
        if sub:
            t = np.array([s[m]["mean_s"] for s in sub])
            sd = np.array([s[m]["sd_s"] for s in sub])
            ax.errorbar(x_sub, t, yerr=sd, marker=marker, color=color, capsize=2.5, linewidth=1.2, markersize=4.5,
                        label=f"{name} (labels: edges $|E|$ of its graph)")
            for xi, ti, s in zip(x_sub, t, sub):
                ax.annotate(E._short_count(float(s[m]["edges"])), (xi, ti), textcoords="offset points", xytext=(0, dy),
                            ha="center", fontsize=7.5, color=color)
        for s in whole:
            ax.errorbar([x_whole], [s[m]["mean_s"]], yerr=[s[m]["sd_s"]], marker=marker, color=color, capsize=2.5,
                        linewidth=0, elinewidth=1.2, markersize=5.5, markerfacecolor="white",
                        label=None if sub else f"{name} (labels: edges $|E|$ of its graph)")
            ax.annotate(E._short_count(float(s[m]["edges"])), (x_whole, s[m]["mean_s"]), textcoords="offset points",
                        xytext=(0, dy), ha="center", fontsize=7.5, color=color)
    ax.set_yscale("log")
    ax.margins(x=0.08, y=0.15)
    ticks = list(x_sub) + ([x_whole] if whole else [])
    labels = [f"{int(s['n']):,}" for s in sub] + (["whole\ngraph"] if whole else [])
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels)
    if whole and sub:
        ax.axvline((x_sub[-1] + x_whole) / 2, color="#bdbdbd", linewidth=0.8, linestyle=":")
    ax.minorticks_off()
    ax.set_xlabel("Contracts in the subsample $n$; open markers: the whole contract graph")
    ax.set_ylabel("Runtime per solver call (s, log scale)")
    ax.legend(frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.01), ncol=1)
    E._save(fig, "runtime-scaling.pdf")


def main() -> int:
    if not CONTRACT_GRAPH:
        raise SystemExit("refused: export_latex_c12.py writes the tables of the contract-graph variant only "
                         "(CONTRACT_REP_VARIANT=contract12m)")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tables-dir", type=Path, help="output folder for the .tex tables")
    ap.add_argument("--figures-dir", type=Path, help="output folder for the .pdf figures")
    ap.add_argument("--no-figures", action="store_true")
    ap.add_argument("-v", "--verbose", action="store_true", help="also list the outputs skipped for missing inputs")
    ap.add_argument("--into-manuscript", action="store_true",
                    help="write into the manuscript instead of data/_work/latex-contract12m/")
    args = ap.parse_args()
    if not args.into_manuscript:
        stage = ROOT / "data" / "_work" / "latex-contract12m"
        E.OUT["tables"], E.OUT["figures"] = stage / "tables", stage / "figures"
    if args.tables_dir:
        E.OUT["tables"] = args.tables_dir
    if args.figures_dir:
        E.OUT["figures"] = args.figures_dir
    E.OUT["tables"].mkdir(parents=True, exist_ok=True)
    E.OUT["figures"].mkdir(parents=True, exist_ok=True)

    cfg = load_config()
    seed = int(cfg["alignment"]["bootstrap_seed"])
    same, w0, w1 = E._load("same"), E._load("w0"), E._load("w1")
    rob, bench, supp, sybil = E._load("rob"), E._load("bench"), E._load("supp"), E._load("sybil")
    desc = load_json(SRC["describe"]) if SRC["describe"].exists() else None
    runs = {(t, m): load_json(SRC[f"disc_{t}_{m}"]) for t, m in RUNS if SRC[f"disc_{t}_{m}"].exists()}
    n = int(same["cohort"]) if same else None

    if bench and n:
        t_benchmark_runtime(bench, n)
        t_benchmark_scaling(bench, rob, n, cfg)
        t_benchmark_runs(bench, cfg)
    else:
        E.SKIPPED.append("benchmark tables (no benchmark.json)")
    if same:
        E.t_alignment_hybrid(same, seed)
        E.t_tau_diff_hybrid(same, seed, supp)
        E.t_tau_diff(same, seed)
        E.t_tie_sensitivity(same, seed)
        for fam in E.FAMILY_TABLES:
            E.t_alignment_family(same, seed, fam)
        E.t_alignment_family_ci(same, seed)
        E.t_robustness_damping(same, bench, seed, cfg)
    else:
        E.SKIPPED.append("same-window tables (no same-window summary)")
    if rob and n:
        E.t_robustness_slope(rob, n, load_json(USD_CONSTANTS))
        t_robustness_sample_size(rob, bench, n, cfg)
    else:
        E.SKIPPED.append("robustness tables (no robustness.json)")
    if same and w0 and w1:
        E.t_endorserank_restarts(same, w0, w1, seed, cfg)
        t_cohort_coverage(same, w0, w1)
        t_label_split(w0, w1)
        t_union_members(w0, w1, seed)
        t_endorserank_awp_holdout(w0, w1, supp, seed)
        t_cpr_contrasts(w0, w1, supp, seed)
        reg = {k: load_json(PROC_SHARED / d / "eval_summary.json")
               for k, d in (("same", "same-window"), ("w0", "holdout-w0"), ("w1", "registered-w1"))}
        t_registered_vs_contract(reg, {"same": same, "w0": w0, "w1": w1}, seed, cfg)
        if rob:
            t_uncapped(rob, w0, w1, seed)
    else:
        E.SKIPPED.append("tables that need the same-window, W0 and W1 summaries")
    if w0:
        t_holdout_spenders(w0, seed, cfg)
        t_holdout_diff(w0, seed, supp)
        t_holdout_receiving(w0, seed, supp)
    if w1:
        t_fresh_holdout(w1, seed, cfg)
        t_fresh_contrasts(w1, seed)
        t_fresh_posthoc(w1, supp, seed, cfg)
    if desc:
        t_contract_types(desc)
        t_allowance_cap(desc)
        t_graph_layers(desc)
        t_tokens(desc, cfg)
    else:
        E.SKIPPED.append("data tables (no describe.json)")
    if sybil:
        t_sybil_threshold(sybil)
    if len(runs) == len(RUNS):
        check_discovery(runs)
        t_discovery_sizes(runs)
        t_discovery_auc(runs)
        t_discovery_decision(runs)
        t_discovery_contrasts(runs[("tobs", "both")])
        t_discovery_sensitivity(runs[("tobs", "both")])
        t_discovery_diagnostics(runs)
        t_discovery_coverage(runs)
    else:
        E.SKIPPED.append("discovery tables (the four runs are not all on disk)")

    if not args.no_figures:
        E.STATE["name"] = "figures"
        E.fig_logistic_decay(cfg)
        if same:
            try:
                scores = read_parts(E.COHORT_SCORES, columns=["endorserank", "awp"])
            except FileNotFoundError:
                scores = None
                E.SKIPPED.append("score-distributions.pdf, rank-scatter.pdf (no cohort score parts)")
            if scores is not None:
                if len(scores) != n:
                    E.problem(f"cohort score parts have {len(scores)} rows, the summary {n}")
                E.fig_score_distributions(scores, same)
                E.fig_rank_scatter(scores, same)
            E.fig_damping(same)
        if bench:
            fig_runtime_scaling(bench)
        if len(runs) == len(RUNS):
            fig_discovery_curves(runs[("tobs", "both")], "discovery-curves.pdf")
            fig_discovery_curves(runs[("tobs", "out")], "discovery-curves-out.pdf")

    # No written table says that rule B is met, and none holds a word this variant's texts do not use.
    E.STATE["name"] = "wording"
    for path in E.WRITTEN:
        if path.suffix != ".tex":
            continue
        text = path.read_text(encoding="utf-8").replace("after the registered results were known", "")
        bad = sorted({m.group(0) for m in FORBIDDEN.finditer(text)})
        if bad:
            E.problem(f"{path.name}: {bad}")
        if re.search(r"rule~?\s?B[^.]{0,40}\bmet\b", text, re.I) and "not met" not in text:
            E.problem(f"{path.name}: says that rule B is met")

    for p in E.WRITTEN:
        print("wrote", p)
    if args.verbose and E.SKIPPED:
        print("skipped:", "; ".join(E.SKIPPED))
    if E.PROBLEMS:
        print(f"{len(E.PROBLEMS)} problem(s):")
        for msg in E.PROBLEMS:
            print("  -", msg)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
