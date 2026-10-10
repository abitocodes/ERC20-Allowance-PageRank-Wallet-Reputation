#!/usr/bin/env python3
"""Write the LaTeX tables and figures of the thesis from the evaluation summaries.

Reads the JSON summaries of the evaluation drivers (run_same_window.py,
run_holdout.py, run_registered.py, sybil_model.py, run_robustness.py,
run_benchmark.py; run_supplementary.py when it exists) and the same-window cohort
score parts; it computes no score and no statistic. A table or figure is written
only when its inputs exist.

Tables:  dissertation/results/tables/<name>.tex, \\label{tab:<name>}
Figures: dissertation/Figures/generated/<name>.pdf

Every cell is checked while it is written: a missing number is printed as ---
and listed at the end, as is an interval whose ends are reversed, a verdict that
does not follow from its interval, or a mean runtime that does not match its runs.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import PROC, PROC_SHARED, REVISED, ROOT, USD_INPUTS, W1_DIR, load_config, load_json, read_parts  # noqa: E402
from graphs import METHOD_LABELS  # noqa: E402
from labels import TRADER_LABELS  # noqa: E402
from run_same_window import FAMILIES as FAMILY_PROXIES  # noqa: E402

THESIS = ROOT.parent / "dissertation"
SOURCES = {
    "same": PROC / "same-window" / "eval_summary.json",
    "w0": PROC / "holdout-w0" / "eval_summary.json",
    "w1": PROC / W1_DIR / "eval_summary.json",
    "sybil": PROC / "sybil-model" / "sybil_model.json",
    "rob": PROC / "robustness" / "robustness.json",
    "bench": PROC / "benchmark" / "benchmark.json",
    "supp": PROC / "supplementary" / "supplementary.json",  # run_supplementary.py, optional
}
COHORT_SCORES = PROC / "same-window" / "cohort_scores"

APPR, SEND, LIQ = "future_new_approvers", "future_new_transfer_senders", "liquidation_free_rate"
LABEL_WORDS = {APPR: "new approval pairs", SEND: "new transfer senders", LIQ: "liquidation-free close rate"}
FAMILIES = (("transfer", "Transfer"), ("allowance", "Allowance"), ("sybil_stability", "Sybil"))
FAMILY_WORDS = {
    "transfer": "transfer",
    "allowance": "allowance",
    "sybil_stability": "sybil-stability",
    "in_approve_degree": "in-approve degree",
    "in_degree": "in-degree",
}
PROXY_LABELS = {
    "in_degree": "In-degree",
    "in_value": "In-value (sum inbound)",
    "in_approve_degree": "In-approve degree",
    "in_approve_value": "In-approve value (sum)",
    "inbound_counterparty_ratio": "Inbound counterparty ratio",
    "transfer_tenure_days": "Transfer tenure (days)",
    "active_months": "Active months",
}
# Names inside contrast labels: C-PR alone is the primary lambda = 0.5.
SHORT = {
    "endorserank": "EndorseRank",
    "endorserank_activity": "EndorseRank (activity restarts)",
    "awp": "AWP",
    "cpr_l100": r"C-PR ($\lambda=1$)",
    "cpr_l0": r"C-PR ($\lambda=0$)",
    "cpr_l25": r"C-PR ($\lambda=0.25$)",
    "cpr_l50": "C-PR",
    "cpr_l75": r"C-PR ($\lambda=0.75$)",
    "spr": "S-PR",
    "t1_in_approve_degree": r"$t_1$ in-approve degree",
    "t1_in_degree": r"$t_1$ in-degree",
    "in_approve_degree": "in-approve degree",
    "in_degree": "transfer in-degree",
}
LAYER_ROWS = ("cpr_l100", "cpr_l0", "cpr_l25", "cpr_l50", "cpr_l75", "spr")
HYBRID_ROWS = ("endorserank", "awp", None, *LAYER_ROWS)  # None draws a \midrule
W0_ROWS = (
    ("t1_in_approve_degree", "In-approve degree at $t_1$ (baseline)"),
    ("t1_in_degree", "Transfer in-degree at $t_1$ (baseline)"),
    None,
    ("endorserank", "EndorseRank"),
    ("awp", "AWP"),
    None,
    *((m, METHOD_LABELS[m]) for m in LAYER_ROWS),
)
W1_BASELINES = (
    ("in_approve_degree", "In-approve degree at the freeze (baseline)"),
    ("in_degree", "Transfer in-degree at the freeze (baseline)"),
)
W1_ROWS = (*W1_BASELINES, None, ("awp", "AWP"), None, *((m, METHOD_LABELS[m]) for m in LAYER_ROWS))
W1_TRADER_ROWS = (
    *W1_BASELINES,
    None,
    ("endorserank", "EndorseRank"),
    ("endorserank_activity", "EndorseRank, restarts by approving activity"),
    ("awp", "AWP"),
    None,
    *((m, METHOD_LABELS[m]) for m in LAYER_ROWS),
)
NEUTRAL_ROWS = (
    ("P", "In-approve degree minus transfer in-degree"),
    ("Q", "EndorseRank (activity restarts) minus AWP"),
    ("layers", r"C-PR ($\lambda=1$) minus C-PR ($\lambda=0$)"),
    ("er_awp", "EndorseRank minus AWP"),
    ("cpr0_awp", r"C-PR ($\lambda=0$) minus AWP"),
    ("er_degree", "EndorseRank minus in-approve degree"),
)
NUMBER_WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 10: "ten"}

# Wording that differs between the registered analysis and the revised one
# (docs/revision_price_weighting.md): the revised results are never called registered.
W1_NAME = "Window W1" if REVISED else "Registered window W1"
LAYER_A = "latest allowances in USD, each capped" if REVISED else "latest allowances in raw amounts"
LAYER_T = ("USD amounts discounted by the decay of AWP" if REVISED
           else "raw amounts discounted by the decay of AWP")
W1_NAME_LC = "window W1" if REVISED else "registered window W1"
REG = "" if REVISED else "registered "
APPLIED = " and applied here to the revised scores" if REVISED else ""

PROBLEMS: list[str] = []
WRITTEN: list[Path] = []
SKIPPED: list[str] = []
STATE: dict = {"name": "", "nboot": set()}
OUT = {"tables": THESIS / "results" / "tables", "figures": THESIS / "Figures" / "generated"}


# --------------------------------------------------------------------------- formatting and checks


def problem(msg: str) -> None:
    PROBLEMS.append(f"{STATE['name']}: {msg}")


def begin(name: str) -> None:
    STATE["name"] = name
    STATE["nboot"] = set()


def _num(v) -> float | None:
    if v is None:
        return None
    v = float(v)
    return v if np.isfinite(v) else None


def f3(v, what: str = "value") -> str:
    x = _num(v)
    if x is None:
        problem(f"missing {what}")
        return "---"
    return f"{x:.3f}"


def fsigned(v, what: str = "difference") -> str:
    x = _num(v)
    if x is None:
        problem(f"missing {what}")
        return "---"
    return f"{x:+.3f}"


def f1(v, what: str = "value") -> str:
    x = _num(v)
    if x is None:
        problem(f"missing {what}")
        return "---"
    return f"{x:,.1f}".replace(",", "{,}")


def fint(v, what: str = "count") -> str:
    x = _num(v)
    if x is None:
        problem(f"missing {what}")
        return "---"
    return f"{int(round(x)):,}".replace(",", "{,}")


def fci(lo, hi, what: str = "interval") -> str:
    a, b = _num(lo), _num(hi)
    if a is None or b is None:
        problem(f"missing {what}")
        return "---"
    if a > b:
        problem(f"reversed {what} [{a}, {b}]")
    return f"[{a:.3f}, {b:.3f}]"


def ratio(a, b) -> str:
    x, y = _num(a), _num(b)
    if x is None or y is None or y == 0:
        problem("ratio without both values")
        return "---"
    return f"{x / y:.1f}$\\times$"


def _point(d: dict):
    for key in ("kendall_tau", "mean_tau", "delta_tau"):
        if key in d:
            return d[key]
    return None


def parts(d: dict | None, what: str) -> tuple[str, str]:
    """(coefficient, interval) of a tau, family-mean or contrast entry."""
    if not d:
        problem(f"no entry for {what}")
        return "---", "---"
    if d.get("n_boot") is not None:
        STATE["nboot"].add(int(d["n_boot"]))
    return f3(_point(d), what), fci(d.get("ci_low"), d.get("ci_high"), f"interval of {what}")


def tc(d: dict | None, what: str) -> str:
    t, ci = parts(d, what)
    return f"{t} {ci}"


def stack(d: dict | None, what: str) -> str:
    """Coefficient over its interval, for tables with many columns."""
    t, ci = parts(d, what)
    return f"\\begin{{tabular}}[c]{{@{{}}c@{{}}}}{t}\\\\[-1pt]{{\\footnotesize {ci}}}\\end{{tabular}}"


def boot_note(seed: int, unit: str = "contracts") -> str:
    nb = sorted(STATE["nboot"])
    if not nb:
        problem("no bootstrap count found")
        count = "---"
    else:
        if len(nb) > 1:
            problem(f"cells with different bootstrap counts {nb}")
        count = fint(max(nb))
    return f"CI = 95\\% percentile bootstrap over {unit} ({count} paired resamples, seed {seed})."


def tex_date(ts: str) -> str:
    d = dt.date.fromisoformat(str(ts)[:10])
    return f"{d.day}~{d.strftime('%B')}~{d.year}"


def month_range(start: str, end: str) -> str:
    a, b = dt.date.fromisoformat(str(start)[:10]), dt.date.fromisoformat(str(end)[:10])
    return f"{a.strftime('%B')}--{b.strftime('%B')} {b.year}"


def rel(path: Path) -> str:
    try:
        return "experiments/" + path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _short_caption(caption: str) -> str:
    """First sentence of the caption, for the List of Tables."""
    first = re.split(r"(?<=\.)\s+(?=[A-Z$\\])", caption, maxsplit=1)[0].strip()
    first = re.sub(r"\s*\((?:[^()]|\([^()]*\))*\)\.?$", "", first).rstrip()
    return first if first.endswith(".") else first + "."


# Entries of the List of Tables; a table without one uses the first sentence of its caption.
SHORT_CAPTIONS = {
    "benchmark-runtime": "Computational benchmark on the full graphs of the matched cohort.",
    "benchmark-scaling": "Runtime against the size of the evaluation set.",
    "benchmark-runs": "Every timed solver call of the benchmark.",
    "alignment-hybrid": "Same-window family-mean Kendall $\\tau$ for every score of this study.",
    "tau-diff-hybrid": "Same-window paired contrasts of C-PR and S-PR against their two layers and of C-PR against "
                       "EndorseRank and AWP.",
    "tau-diff": "Same-window paired contrasts between EndorseRank and AWP.",
    "tie-sensitivity": "Same-window family means with missing contracts scored zero or kept as isolated nodes.",
    "alignment-transfer": "Domain alignment of EndorseRank and AWP with the transfer proxies.",
    "alignment-allowance": "Domain alignment of EndorseRank and AWP with the allowance proxies.",
    "alignment-sybil-stability": "Domain alignment of EndorseRank and AWP with the Sybil-adjusted stability proxies.",
    "alignment-family-ci": "Family-mean Kendall $\\tau$ of EndorseRank and AWP with bootstrap intervals.",
    "robustness-damping": "Robustness: family-mean Kendall $\\tau$ under PageRank damping $d$.",
    "robustness-tokens": "Robustness: family-mean Kendall $\\tau$ on top-token subgraphs.",
    "robustness-sample-size": "Sensitivity of the family means to the evaluation set.",
    "endorserank-restarts": "EndorseRank with uniform and with activity-weighted restarts, next to AWP.",
    "holdout-spenders": "Temporal holdout W0 on the spender cohort.",
    "holdout-diff": "Paired bootstrap differences on the spender holdout W0.",
    "holdout-receiving": "Spender holdout W0 restricted to spenders that had received a transfer before the freeze.",
    "holdout-traders": "W0 trader run on the GMX~V2 profit labels.",
    "endorserank-awp-holdout": "Paired bootstrap differences between EndorseRank and AWP out of window.",
    "fresh-holdout": f"{W1_NAME}: Kendall $\\tau$ on the three {REG}labels{' of rule B' if REVISED else ''}.",
    "fresh-contrasts": f"{W1_NAME}: the contrasts of rule B with their verdicts and the {REG}"
                       "sensitivity analyses.",
    "fresh-posthoc": f"EndorseRank and its variant with activity restarts in the {W1_NAME_LC}.",
    "fresh-traders": f"{W1_NAME}: Kendall $\\tau$ on the other trader labels.",
    "robustness-slope": "Robustness: family-mean Kendall $\\tau$ under ten times smaller and larger value slopes.",
    "registered-vs-revised": "Decision contrasts of the registered analysis and of the revised analysis.",
    "usd-tokens": "The five tokens of the revised analysis, the rows they keep and their prices.",
    "neutral-label-contrasts": "Allowance-side against transfer-side scores on the liquidation-free close rate.",
    "neutral-label-recipients": "Traders that receive approvals against all other labelled traders.",
    "neutral-label-grid": "Allowance-side minus transfer-side scores on every trader label in both windows.",
}


def emit(name: str, caption: str, tabular: str, sources: list[Path], label: str | None = None) -> None:
    label = label or f"tab:{name}"
    short = SHORT_CAPTIONS.get(name) or _short_caption(caption)
    cap = f"\\caption[{short}]{{{caption}}}" if short != caption else f"\\caption{{{caption}}}"
    header = "".join(f"% Source: {rel(p)}\n" for p in sources)
    text = (
        "% Generated by experiments/scripts/export_latex.py -- do not edit by hand.\n"
        f"{header}"
        "\\begin{table}[htbp]\n\\centering\n"
        f"{cap}\n\\label{{{label}}}\n\\fitwidth{{%\n{tabular}\n}}\n\\end{{table}}\n"
    )
    path = OUT["tables"] / f"{name}.tex"
    path.write_text(text, encoding="utf-8")
    WRITTEN.append(path)


def tabular(colspec: str, head: str, lines: list[str]) -> str:
    body = "\n".join(lines)
    return f"\\begin{{tabular}}{{{colspec}}}\n\\toprule\n{head} \\\\\n\\midrule\n{body}\n\\bottomrule\n\\end{{tabular}}"


def method_rows(order, cell) -> list[str]:
    """One row per (method, label) of ``order``; None draws a rule. ``cell(method)`` returns the cells."""
    lines: list[str] = []
    for item in order:
        if item is None:
            if lines and lines[-1] != "\\midrule":
                lines.append("\\midrule")
            continue
        method, name = item
        lines.append(f"{name} & {cell(method)} \\\\")
    while lines and lines[-1] == "\\midrule":
        lines.pop()
    return lines


def contrast_line(label: str, r: dict | None, extra: str = "", share: bool = True) -> str:
    """label [& extra] & tau_a & tau_b & delta & CI [& P(delta>0)]."""
    if not r:
        problem(f"no contrast for {label}")
        r = {}
    if r.get("n_boot") is not None:
        STATE["nboot"].add(int(r["n_boot"]))
    cells = [label] + ([extra] if extra else [])
    cells += [
        f3(r.get("a_tau"), f"tau_a of {label}"),
        f3(r.get("b_tau"), f"tau_b of {label}"),
        fsigned(r.get("delta_tau"), f"delta of {label}"),
        fci(r.get("ci_low"), r.get("ci_high"), f"interval of {label}"),
    ]
    if share:
        cells.append(f3(r.get("share_positive"), f"P(delta>0) of {label}"))
    return " & ".join(cells) + " \\\\"


def delta_ci(r: dict | None, what: str, signed: bool = True) -> str:
    if not r:
        problem(f"no contrast for {what}")
        return "--- ---"
    if r.get("n_boot") is not None:
        STATE["nboot"].add(int(r["n_boot"]))
    d = fsigned(r.get("delta_tau"), what) if signed else f3(r.get("delta_tau"), what)
    return f"{d} {fci(r.get('ci_low'), r.get('ci_high'), f'interval of {what}')}"


def delta_math(r: dict | None, what: str, signed: bool = True) -> str:
    """$\\Delta\\tau=d$ [lo, hi] for a cell that spans several columns."""
    d, ci = delta_ci(r, what, signed).split(" ", 1)
    return f"$\\Delta\\tau={d}$ {ci}"


def is_er_awp(r: dict) -> bool:
    return {r.get("a"), r.get("b")} == {"endorserank", "awp"}


CONTRAST_HEAD = (
    "Contrast ($a$ minus $b$) & $\\tau_a$ & $\\tau_b$ & $\\Delta\\tau$ & 95\\% CI of $\\Delta\\tau$ & $P(\\Delta\\tau>0)$"
)
CONTRAST_HEAD_LABEL = (
    "Contrast ($a$ minus $b$) & Label & $\\tau_a$ & $\\tau_b$ & $\\Delta\\tau$ & 95\\% CI of $\\Delta\\tau$ & $P(\\Delta\\tau>0)$"
)


# --------------------------------------------------------------------------- benchmark


def t_benchmark_runtime(bench: dict, n: int) -> None:
    begin("benchmark-runtime")
    main = bench.get("main") or {}

    def cell(m: str) -> str:
        x = main.get(m)
        if not x:
            problem(f"no benchmark row for {m}")
            x = {}
        return (
            f"{f3(x.get('mean_s'), 'runtime')} & {f3(x.get('sd_s'), 'SD')} & {f1(x.get('peak_mb'), 'peak memory')} & "
            f"{fint(x.get('iterations'), 'iterations')} & {fint(x.get('nodes'), '|V|')} & {fint(x.get('edges'), '|E|')}"
        )

    order = (("endorserank", "EndorseRank"), ("awp", "AWP"), None,
             ("cpr_l50", METHOD_LABELS["cpr_l50"]), ("spr", "S-PR"))
    lines = method_rows(order, cell)
    er, awp = main.get("endorserank") or {}, main.get("awp") or {}
    proto = bench.get("protocol") or {}
    runs = int(proto.get("timed_runs", 5))
    warm = int(proto.get("warmup_runs", 1))
    caption = (
        f"Computational benchmark on the full graphs of the matched cohort ($n={fint(n)}$ contracts; AWP/EndorseRank "
        f"runtime ratio {ratio(awp.get('mean_s'), er.get('mean_s'))} at an edge ratio of "
        f"{ratio(awp.get('edges'), er.get('edges'))}). Runtime = mean wall-clock seconds over {runs} timed solver calls "
        f"after {NUMBER_WORDS.get(warm, warm)} untimed warm-up, on which alone peak memory is traced; SD over the same "
        f"{runs} runs. A timed call turns an edge list into scores: node indexing, sparse-matrix assembly, row "
        "normalisation, restart vector and power iteration. $|V|$ and $|E|$ are the nodes and distinct edges of each "
        "method's solver graph. C-PR walks on the union of the allowance layer and the transfer layer, so its $|E|$ "
        "counts the distinct pairs of both; S-PR runs on the transfer layer, and its runtime and iterations include the "
        "solve of the allowance layer that supplies its restart vector. Table~\\ref{tab:benchmark-runs} lists every run."
    )
    head = "Method & Runtime (s) & SD (s) & Peak mem.\\ (MB) & Iters & $|V|$ & $|E|$"
    emit("benchmark-runtime", caption, tabular("lrrrrrr", head, lines), [SOURCES["bench"]])


def t_benchmark_scaling(bench: dict, n: int, cfg: dict) -> None:
    begin("benchmark-scaling")
    lines = []
    for st in bench.get("scaling") or []:
        er, awp = st.get("endorserank") or {}, st.get("awp") or {}
        mark = "$^{a}$" if st.get("reused_main") else ""
        lines.append(
            f"{fint(st.get('n'), 'stage n')}{mark} & {f3(er.get('mean_s'), 'ER runtime')} & {f3(awp.get('mean_s'), 'AWP runtime')} & "
            f"{ratio(awp.get('mean_s'), er.get('mean_s'))} & {ratio(awp.get('edges'), er.get('edges'))} & "
            f"{fint(er.get('nodes'), 'ER |V|')} & {fint(er.get('edges'), 'ER |E|')} & "
            f"{fint(awp.get('nodes'), 'AWP |V|')} & {fint(awp.get('edges'), 'AWP |E|')} \\\\"
        )
    if not lines:
        SKIPPED.append("benchmark-scaling (no stages)")
        return
    runs = int((bench.get("protocol") or {}).get("timed_runs", 5))
    seed = bench.get("scaling_seed") or cfg["benchmark"]["scaling_seed"]
    reused = any(st.get("reused_main") for st in bench.get("scaling") or [])
    caption = (
        f"Runtime of EndorseRank (ER) and AWP against the size of the evaluation set: deterministic SHA256 subsamples "
        f"of the matched cohort (seed \\texttt{{{seed}}}) up to the full cohort of $n={fint(n)}$ contracts. Each stage "
        "keeps the extracted edges incident to its sampled contracts, so $|V|$ and $|E|$ of both solver graphs are "
        "reported per stage. AWP/ER time and AWP/ER $|E|$ are the ratios of the two runtimes and of the two edge counts "
        f"in the same row. Runtime = mean wall-clock seconds over {runs} timed solver calls after one untimed warm-up."
        + (" $^{a}$The full-cohort row is the measurement of Table~\\ref{tab:benchmark-runtime}, reused, not timed again."
           if reused else "")
    )
    head = ("$n$ & ER (s) & AWP (s) & AWP/ER time & AWP/ER $|E|$ & ER $|V|$ & ER $|E|$ & AWP $|V|$ & AWP $|E|$")
    emit("benchmark-scaling", caption, tabular("rrrrrrrrr", head, lines), [SOURCES["bench"]])


def _check_runs(x: dict, what: str) -> None:
    runs = x.get("runs_s") or []
    if not runs:
        problem(f"no timed runs for {what}")
        return
    if x.get("mean_s") is not None and abs(float(np.mean(runs)) - float(x["mean_s"])) > 1e-9:
        problem(f"mean of the runs of {what} differs from mean_s")
    if len(runs) > 1 and x.get("sd_s") is not None and abs(float(np.std(runs, ddof=1)) - float(x["sd_s"])) > 1e-9:
        problem(f"SD of the runs of {what} differs from sd_s")


def t_benchmark_runs(bench: dict, n: int, cfg: dict) -> None:
    begin("benchmark-runs")
    main = bench.get("main") or {}
    d0 = float((bench.get("protocol") or {}).get("damping", cfg["reputation"]["damping"]))
    blocks: list[tuple[str, list[tuple[str, dict]]]] = [(
        f"Full graphs, $d={d0:g}$",
        [(name, main.get(m) or {}) for m, name in (("endorserank", "EndorseRank"), ("awp", "AWP"),
                                                     ("cpr_l50", METHOD_LABELS["cpr_l50"]), ("spr", "S-PR"))],
    )]
    for d, rows in sorted((bench.get("damping") or {}).items(), key=lambda kv: float(kv[0])):
        if abs(float(d) - d0) < 1e-12:
            continue  # the main measurement, reused
        blocks.append((f"Full graphs, $d={float(d):g}$",
                       [("EndorseRank", rows.get("endorserank") or {}), ("AWP", rows.get("awp") or {})]))
    for st in bench.get("scaling") or []:
        if st.get("reused_main"):
            continue
        blocks.append((f"Stage $n={fint(st.get('n'))}$",
                       [("EndorseRank", st.get("endorserank") or {}), ("AWP", st.get("awp") or {})]))
    k = max((len(x.get("runs_s") or []) for _, rows in blocks for _, x in rows), default=0)
    if k == 0:
        SKIPPED.append("benchmark-runs (no timed runs)")
        return
    lines = []
    for title, rows in blocks:
        if lines:
            lines.append("\\midrule")
        lines.append(f"\\multicolumn{{{k + 3}}}{{l}}{{\\emph{{{title}}}}} \\\\")
        for name, x in rows:
            _check_runs(x, f"{title} {name}")
            runs = list(x.get("runs_s") or [])
            cells = [f3(r, "run") for r in runs] + ["---"] * (k - len(runs))
            if len(runs) < k:
                problem(f"{title} {name} has {len(runs)} runs, not {k}")
            lines.append(f"{name} & {' & '.join(cells)} & {f3(x.get('mean_s'), 'mean')} & {f3(x.get('sd_s'), 'SD')} \\\\")
    head = "Method & " + " & ".join(f"Run {i + 1}" for i in range(k)) + " & Mean & SD"
    caption = (
        f"Wall-clock seconds of every timed solver call of the benchmark (matched cohort, $n={fint(n)}$ contracts), "
        "in the order the runs were made, with their mean and standard deviation. Each configuration had one untimed "
        "warm-up before its timed runs, and each graph and setting was timed once: the $d="
        f"{d0:g}$ rows of Table~\\ref{{tab:robustness-damping}} and the full-cohort row of "
        "Table~\\ref{tab:benchmark-scaling} are the first block, reused. The stages are the subsamples of "
        "Table~\\ref{tab:benchmark-scaling}."
    )
    emit("benchmark-runs", caption, tabular("l" + "r" * (k + 2), head, lines), [SOURCES["bench"]])


# --------------------------------------------------------------------------- same window


def t_alignment_hybrid(same: dict, seed: int) -> None:
    begin("alignment-hybrid")
    fams = same.get("families") or {}

    def cell(m: str) -> str:
        return " & ".join(tc((fams.get(m) or {}).get(f), f"{m} {f}") for f, _ in FAMILIES)

    lines = method_rows([None if m is None else (m, METHOD_LABELS[m]) for m in HYBRID_ROWS], cell)
    caption = (
        "Same-window family-mean Kendall $\\tau$ with bootstrap intervals for every score of this study (matched "
        f"cohort, $n={fint(same.get('cohort'))}$ contracts). The scores are EndorseRank and AWP, the coupled operator "
        "C-PR at five values of $\\lambda$ and the endorsement-seeded walk S-PR; $\\lambda=1$ is the allowance layer "
        f"walked alone ({LAYER_A}) and $\\lambda=0$ the transfer layer walked alone ({LAYER_T}); both restart uniformly. The raw degrees have no row because they are proxies "
        "of the transfer and allowance families; EndorseRank with activity restarts is in "
        f"Table~\\ref{{tab:endorserank-restarts}}. {boot_note(seed)}"
    )
    head = "Method & " + " & ".join(h for _, h in FAMILIES)
    emit("alignment-hybrid", caption, tabular("lccc", head, lines), [SOURCES["same"]])


def _sw_label(c: dict) -> str:
    (a, fa), (b, fb) = c["a"], c["b"]
    return f"{SHORT[a]} {FAMILY_WORDS[fa]} minus {SHORT[b]} {FAMILY_WORDS[fb]}"


def _rule_a_secondary_text(rule: dict) -> str:
    if not rule:
        problem("no secondary part of rule A")
        return ""
    t, a, s = rule.get("transfer") or {}, rule.get("allowance") or {}, rule.get("sybil_stability") or {}

    def inside(r: dict, fam: str) -> str:
        best = SHORT.get(r.get("best_layer"), r.get("best_layer"))
        where = "inside" if r.get("pass") else "outside"
        return f"{where} the interval of {best} on the {fam} family"

    syb = "exceeds" if s.get("pass") else "does not exceed"
    verdict = "met" if rule.get("pass") else "not met"
    return (
        f"The secondary part of rule A, fixed in the analysis plan{APPLIED}, is {verdict}: C-PR's point estimate lies "
        f"{inside(t, 'transfer')} and {inside(a, 'allowance')}, and C-PR {syb} both layers on the Sybil-stability family."
    )


def t_tau_diff_hybrid(same: dict, seed: int) -> None:
    begin("tau-diff-hybrid")
    rows = same.get("contrasts") or []
    layer = [r for r in rows if r.get("group") == "hybrid"]
    single = [r for r in rows if r.get("group") == "hybrid_single"]
    if not layer:
        SKIPPED.append("tau-diff-hybrid (no hybrid contrasts)")
        return
    lines = ["\\multicolumn{6}{l}{\\emph{Against the two layers walked alone}} \\\\"]
    lines += [contrast_line(_sw_label(r), r) for r in layer]
    if single:
        lines += ["\\midrule", "\\multicolumn{6}{l}{\\emph{Against EndorseRank and AWP}} \\\\"]
        lines += [contrast_line(_sw_label(r), r) for r in single]
    caption = (
        "Same-window paired contrasts for the coupled operator (C-PR, $\\lambda=0.5$) and the endorsement-seeded walk "
        "(S-PR) against the two layers they are built from, the allowance layer (C-PR ($\\lambda=1$)) and the transfer "
        "layer (C-PR ($\\lambda=0$)), and of C-PR against EndorseRank and AWP (matched cohort, "
        f"$n={fint(same.get('cohort'))}$ contracts). Family-mean $\\tau$; the same contract resamples are used for $a$ "
        "and $b$. The contrasts with the layers are a stricter check beside the secondary part of rule A, which "
        "compares C-PR's point estimate with the better layer's interval in Table~\\ref{tab:alignment-hybrid}. "
        f"{_rule_a_secondary_text(same.get('rule_a_secondary') or {})} An interval below 0 means $a$ is below $b$ "
        f"beyond sampling variation; one above 0 means it exceeds it. {boot_note(seed)}"
    )
    emit("tau-diff-hybrid", caption, tabular("lccccc", CONTRAST_HEAD, lines), [SOURCES["same"]])


def t_tau_diff(same: dict, seed: int) -> None:
    begin("tau-diff")
    rows = [r for r in same.get("contrasts") or [] if r.get("group") == "er_awp"]
    if not rows:
        SKIPPED.append("tau-diff (no er_awp contrasts)")
        return
    lines = [contrast_line(_sw_label(r), r) for r in rows]
    caption = (
        "Paired bootstrap tests of differences between Kendall $\\tau$ coefficients of EndorseRank and AWP in the same "
        f"window (matched cohort, $n={fint(same.get('cohort'))}$ contracts). Family entries use the family-mean "
        "$\\tau$; the same contract resamples are used for $a$ and $b$, so the interval is on the paired difference. "
        "An interval excluding 0 indicates a difference not attributable to sampling variation at the 5\\% level. "
        f"{boot_note(seed)}"
    )
    emit("tau-diff", caption, tabular("lccccc", CONTRAST_HEAD, lines), [SOURCES["same"]])


def t_tie_sensitivity(same: dict, seed: int) -> None:
    begin("tie-sensitivity")
    fams = same.get("families") or {}
    iso = same.get("isolated_rule") or {}
    if not iso:
        SKIPPED.append("tie-sensitivity (no isolated_rule)")
        return
    names = {"transfer": "Transfer", "allowance": "Allowance", "sybil_stability": "Sybil stability"}
    lines = []
    for f, name in names.items():
        cells = [tc((fams.get("endorserank") or {}).get(f), f"ER {f}"), tc((fams.get("awp") or {}).get(f), f"AWP {f}"),
                 tc((iso.get("endorserank_iso") or {}).get(f), f"ER iso {f}"),
                 tc((iso.get("awp_iso") or {}).get(f), f"AWP iso {f}")]
        lines.append(f"{name} & {' & '.join(cells)} \\\\")
    inter = same.get("inter_method") or {}
    lines += ["\\midrule",
              f"EndorseRank vs.\\ AWP & \\multicolumn{{2}}{{c}}{{{tc(inter.get('endorserank_vs_awp'), 'inter-method')}}} & "
              f"\\multicolumn{{2}}{{c}}{{{tc(inter.get('isolated'), 'inter-method, isolated')}}} \\\\"]
    g = same.get("graph") or {}
    awp_same = all((fams.get("awp") or {}).get(f) == (iso.get("awp_iso") or {}).get(f) for f in names)
    awp_text = (
        "AWP restarts only at addresses that sent a transfer, so an isolated contract keeps the score zero and AWP's "
        "coefficients are the same under both rules. " if awp_same else
        "AWP's coefficients differ between the two rules. "
    )
    caption = (
        "Same-window family-mean Kendall $\\tau$ with contracts missing from a graph scored zero or kept as isolated "
        f"nodes (matched cohort, $n={fint(same.get('cohort'))}$ contracts). The main analysis scores a contract that is "
        "missing from a method's graph zero; keeping it as an isolated node is the sensitivity analysis fixed in the "
        f"analysis plan. The rule concerns {fint(g.get('cohort_outside_allowance'))} contracts for EndorseRank and "
        f"{fint(g.get('cohort_outside_transfer'))} for AWP ({fint(g.get('cohort_outside_both'))} are missing from both "
        "graphs). Under EndorseRank's uniform restarts an isolated node gets the score of a node without in-edges. "
        f"{awp_text}The last row is the agreement between the two scores. {boot_note(seed)}"
    )
    head = (" & \\multicolumn{2}{c}{Missing contracts scored zero} & \\multicolumn{2}{c}{Missing contracts as isolated "
            "nodes} \\\\\n\\cmidrule(lr){2-3} \\cmidrule(lr){4-5}\nFamily & EndorseRank & AWP & EndorseRank & AWP")
    emit("tie-sensitivity", caption, tabular("lcccc", head, lines), [SOURCES["same"]])


FAMILY_TABLES = {
    "transfer": ("alignment-transfer",
                 "Domain alignment of EndorseRank and AWP with the transfer proxies (in-degree and in-value of each "
                 "contract)"),
    "allowance": ("alignment-allowance",
                  "Domain alignment of EndorseRank and AWP with the allowance proxies (in-approve degree and value of "
                  "each spender contract)"),
    "sybil_stability": ("alignment-sybil-stability",
                        "Domain alignment of EndorseRank and AWP with the Sybil-adjusted stability proxies from transfer "
                        "activity"),
}


def t_alignment_family(same: dict, seed: int, family: str) -> None:
    name, head_text = FAMILY_TABLES[family]
    begin(name)
    pp = same.get("per_proxy") or {}
    blocks = []
    for m in ("endorserank", "awp"):
        rows = []
        for p in FAMILY_PROXIES[family]:
            r = (pp.get(m) or {}).get(p)
            t, ci = parts(r, f"{m} {p}")
            rho = f3((r or {}).get("spearman_rho"), f"rho of {m} {p}")
            rows.append(f"{PROXY_LABELS[p]} & {rho} & {t} & {ci} \\\\")
        blocks.append(f"\\multicolumn{{4}}{{l}}{{\\textit{{{METHOD_LABELS[m]}}}}} \\\\\n" + "\n".join(rows))
    caption = (
        f"{head_text}, same window (matched cohort, $n={fint(same.get('cohort'))}$ contracts). Kendall $\\tau$ and "
        f"Spearman $\\rho$ between scores and proxy rankings. {boot_note(seed)}"
    )
    head = "Proxy & Spearman $\\rho$ & Kendall $\\tau$ & 95\\% CI of $\\tau$"
    emit(name, caption, tabular("lccc", head, ["\n\\addlinespace\n".join(blocks)]), [SOURCES["same"]])


def t_alignment_family_ci(same: dict, seed: int) -> None:
    begin("alignment-family-ci")
    fams = same.get("families") or {}
    lines = []
    for f, name in FAMILIES:
        et, eci = parts((fams.get("endorserank") or {}).get(f), f"ER {f}")
        at, aci = parts((fams.get("awp") or {}).get(f), f"AWP {f}")
        lines.append(f"{name} & {et} & {eci} & {at} & {aci} \\\\")
    inter = (same.get("inter_method") or {}).get("endorserank_vs_awp")
    t, ci = parts(inter, "inter-method")
    lines += ["\\midrule",
              f"\\multicolumn{{5}}{{l}}{{EndorseRank vs.\\ AWP score agreement: $\\tau={t}$, CI {ci}}} \\\\"]
    caption = (
        "Family-mean Kendall $\\tau$ of EndorseRank (ER) and AWP with bootstrap confidence intervals on the matched "
        f"cohort ($n={fint(same.get('cohort'))}$ contracts). {boot_note(seed)}"
    )
    head = "Family & ER mean $\\tau$ & ER 95\\% CI & AWP mean $\\tau$ & AWP 95\\% CI"
    emit("alignment-family-ci", caption, tabular("lcccc", head, lines), [SOURCES["same"]])


def t_robustness_damping(same: dict, bench: dict | None, seed: int, cfg: dict) -> None:
    begin("robustness-damping")
    dmp = same.get("damping") or {}
    ds = sorted({float(v["damping"]) for v in dmp.values()})
    if not ds:
        SKIPPED.append("robustness-damping (no damping sweep)")
        return
    bdmp = {float(k): v for k, v in ((bench or {}).get("damping") or {}).items()}
    lines = []
    for d in ds:
        er, awp = dmp.get(f"endorserank_d{int(round(d * 100))}") or {}, dmp.get(f"awp_d{int(round(d * 100))}") or {}
        cells = []
        for f in ("allowance", "transfer", "sybil_stability"):
            cells += [stack(er.get(f), f"ER {f} d={d}"), stack(awp.get(f), f"AWP {f} d={d}")]
        if bench is not None:
            b = bdmp.get(d) or {}
            if not b:
                problem(f"no benchmark timing at d={d}")
            cells += [f3((b.get("endorserank") or {}).get("mean_s"), f"ER runtime d={d}"),
                      f3((b.get("awp") or {}).get("mean_s"), f"AWP runtime d={d}")]
        lines.append(f"{d:.2f} & {' & '.join(cells)} \\\\")
    vals = ", ".join(f"{d:g}" for d in ds)
    d0 = float(cfg["reputation"]["damping"])
    runs = int(((bench or {}).get("protocol") or {}).get("timed_runs", 5))
    runtime = (
        f" Runtimes are means of {NUMBER_WORDS.get(runs, runs)} timed solver calls on the full graphs; the "
        f"$d={d0:g}$ runtimes are the measurements of Table~\\ref{{tab:benchmark-runtime}}, reused, not timed again "
        "(Table~\\ref{tab:benchmark-runs} lists every run)." if bench is not None else ""
    )
    caption = (
        f"Robustness: family-mean Kendall $\\tau$ of EndorseRank (ER) and AWP under PageRank damping $d \\in \\{{{vals}\\}}$ "
        f"on the matched cohort ($n={fint(same.get('cohort'))}$ contracts); all.\\ = allowance, tr.\\ = transfer, "
        f"Syb.\\ = Sybil stability.{runtime} {boot_note(seed)}"
    )
    head = "$d$ & ER all. & AWP all. & ER tr. & AWP tr. & ER Syb. & AWP Syb."
    spec = "r" + "c" * 6
    if bench is not None:
        head += " & ER (s) & AWP (s)"
        spec += "rr"
    srcs = [SOURCES["same"]] + ([SOURCES["bench"]] if bench is not None else [])
    emit("robustness-damping", caption, tabular(spec, head, lines), srcs)


# --------------------------------------------------------------------------- robustness.json


def t_robustness_tokens(rob: dict, n: int, cfg: dict) -> None:
    begin("robustness-tokens")
    tok = rob.get("top_tokens") or {}
    subsets = ("by_amount", "by_rows", "all")
    if not all(s in tok for s in subsets):
        SKIPPED.append("robustness-tokens (incomplete top_tokens)")
        return
    lines = []
    for m, name in (("endorserank", "EndorseRank"), ("awp", "AWP")):
        cells = [f3((tok[s].get(m) or {}).get(f), f"{m} {f} {s}") for f, _ in FAMILIES for s in subsets]
        lines.append(f"{name} & {' & '.join(cells)} \\\\")
    top_n = cfg["robustness"]["top_n_tokens"]
    a, r = tok["by_amount"], tok["by_rows"]
    caption = (
        f"Robustness: family-mean Kendall $\\tau$ on the matched cohort ($n={fint(n)}$ contracts) when both graphs keep "
        f"only {top_n} ERC-20 tokens, chosen by summed raw amount or by number of rows (transfer events and latest "
        "allowances), next to the value on all tokens from Table~\\ref{tab:alignment-hybrid}. The two lists share "
        f"{fint(tok.get('shared_tokens'), 'shared tokens')} tokens. The subgraphs have "
        f"{fint(a.get('allowance_edges'))} allowance and {fint(a.get('transfer_edges'))} transfer edges by amount, and "
        f"{fint(r.get('allowance_edges'))} and {fint(r.get('transfer_edges'))} by count. No intervals were computed for "
        "the token subgraphs."
    )
    group = " & ".join(f"\\multicolumn{{3}}{{c}}{{{h}}}" for _, h in FAMILIES)
    head = (f"Method & {group} \\\\\n\\cmidrule(lr){{2-4}} \\cmidrule(lr){{5-7}} \\cmidrule(lr){{8-10}}\n"
            " & " + " & ".join(["by amount & by count & all"] * 3))
    emit("robustness-tokens", caption, tabular("l" + "c" * 9, head, lines), [SOURCES["rob"]])


def t_robustness_slope(rob: dict, n: int, consts: dict) -> None:
    """Revised analysis: EndorseRank and AWP with the value slope b divided and multiplied by ten."""
    begin("robustness-slope")
    sl = rob.get("value_slope") or {}
    variants = (("01x", "$b/10$"), ("1", "$b$"), ("10x", "$10b$"))
    if not all(v in sl for v, _ in variants):
        SKIPPED.append("robustness-slope (incomplete value_slope)")
        return
    lines = []
    for m, name in (("endorserank", "EndorseRank"), ("awp", "AWP")):
        cells = [f3((sl[v].get(m) or {}).get(f), f"{m} {f} slope {v}") for f, _ in FAMILIES for v, _ in variants]
        lines.append(f"{name} & {' & '.join(cells)} \\\\")
    agree = []
    for v, h in (("01x", "$b/10$"), ("10x", "$10b$")):
        t = sl[v].get("tau_with_main") or {}
        agree.append(f"${f3(t.get('endorserank'), f'ER agreement {v}')}$ and ${f3(t.get('awp'), f'AWP agreement {v}')}$ "
                     f"at {h}")
    caption = (
        f"Robustness: family-mean Kendall $\\tau$ on the matched cohort ($n={fint(n)}$ contracts) when the slope $b$ "
        "of the value weight $V$ is divided or multiplied by ten, next to the main analysis. The main slopes put "
        f"$V=1/2$ at the median amount, \\${fint(consts.get('m_transfer_usd'))} for transfers and "
        f"\\${fint(consts.get('m_allowance_usd'))} for allowances; $b/10$ moves that point to ten times the median and "
        "$10b$ to a tenth of it. The rank agreement $\\tau$ of each variant with the main score of the same method "
        f"(EndorseRank and AWP) is {agree[0]}, and {agree[1]}. No intervals were computed for the variants."
    )
    group = " & ".join(f"\\multicolumn{{3}}{{c}}{{{h}}}" for _, h in FAMILIES)
    head = (f"Method & {group} \\\\\n\\cmidrule(lr){{2-4}} \\cmidrule(lr){{5-7}} \\cmidrule(lr){{8-10}}\n"
            " & " + " & ".join([" & ".join(h for _, h in variants)] * 3))
    emit("robustness-slope", caption, tabular("l" + "c" * 9, head, lines), [SOURCES["rob"], USD_INPUTS / "constants.json"])


def _sci(x, digits: int = 2) -> str:
    """A large number as m \\times 10^{k} in math mode."""
    v = _num(x)
    if v is None:
        problem("missing number")
        return "---"
    if v == 0:
        return "$0$"
    k = int(np.floor(np.log10(abs(v))))
    return f"${v / 10 ** k:.{digits - 1}f}\\times10^{{{k}}}$"


def t_usd_tokens(desc: dict, cfg: dict) -> None:
    """Revised analysis: the five tokens, the rows they keep and leave out, and their prices."""
    begin("usd-tokens")
    import pandas as pd
    lst = pd.read_csv(USD_INPUTS / "listed_tokens.csv")
    sel = lst[lst["selected"].astype(str).str.lower() == "true"].sort_values("n_rows_tobs", ascending=False)
    per = {t["token"]: t for t in desc.get("per_token") or []}
    chk = load_json(USD_INPUTS / "chainlink_check.json").get("per_token", {}) if (USD_INPUTS / "chainlink_check.json").exists() else {}
    lines = []
    for _, r in sel.iterrows():
        p = per.get(r["address"]) or {}
        if not p:
            problem(f"no describe row for {r['symbol']}")
        reg = (_num(p.get("reg_approvals")) or 0) + (_num(p.get("reg_transfers")) or 0)
        rev = (_num(p.get("rev_approvals")) or 0) + (_num(p.get("rev_transfers")) or 0)
        c = chk.get(r["symbol"]) or {}
        sym = "USDT0" if r["symbol"] == "USD₮0" else r["symbol"]
        lines.append(
            f"{sym} & \\texttt{{{r['address'][:6]}\\ldots{{}}{r['address'][-4:]}}} & {fint(r['decimals'])} & "
            f"{r['feed']} ({r['feed_category']}) & {fint(reg)} & {fint(rev)} & {_sci(p.get('rev_transfer_usd'))} & "
            f"{fint(r['second_key_days_used'])} & {fint(r['filled_days'])} & {fint(r['spike_days'])} & "
            f"{100 * (_num(c.get('median')) or float('nan')):.2f} / {100 * (_num(c.get('max')) or float('nan')):.2f} \\\\")
    rows = desc.get("rows") or {}
    reg, unl, out_ego, rev = (rows.get(k) or {} for k in ("registered_ego", "unlisted_tokens",
                                                          "listed_tokens_outside_revised_ego", "revised_ego"))
    am = desc.get("amounts") or {}
    cons = desc.get("constants") or {}
    caption = (
        "The five tokens of the revised analysis, with their Chainlink feed (market-risk category), the rows of the "
        "observation window that the ego tables of the plan's cohort hold for them (approvals and transfers) and the "
        "rows that the revised analysis keeps, the US-dollar volume of the kept transfers, the days of the price "
        "series filled from the second DefiLlama key, filled from the previous day and replaced as one-day errors "
        "(of 1{,}096 days), and the median and largest absolute difference, in percent, between the DefiLlama price "
        "and the Chainlink feed read on the chain on 38 dates. "
        f"The ego tables of the plan's cohort hold {fint(reg.get('approvals'))} approvals and "
        f"{fint(reg.get('transfers'))} transfers in the observation window. Of these, {fint(unl.get('approvals'))} "
        f"approvals and {fint(unl.get('transfers'))} transfers belong to other tokens (of the "
        f"{fint(unl.get('tokens'))} other tokens in the ego tables of the observation window and W1) and are left out; {fint(out_ego.get('approvals'))} approvals and {fint(out_ego.get('transfers'))} transfers "
        "of the five tokens are left out because neither end point is a contract of the revised cohort; and "
        f"{fint(rows.get('revised_transfers_without_price'))} kept transfers precede their token's first price. "
        f"At $T_{{\\mathrm{{obs}}}}$, {fint(am.get('unlimited_allowances'))} of the {fint(am.get('latest_allowances_tobs'))} "
        f"positive latest allowances are unlimited and {fint(am.get('allowances_at_or_above_cap'))} reach the cap "
        f"$U={fint(cons.get('cap_allowance_usd'))}$ dollars of the allowance layer of C-PR."
    )
    head = ("Token & Address & Dec. & Chainlink feed & Rows, plan & Rows, kept & Transfer USD & 2nd key & Filled & "
            "Errors & CL diff.\\ (\\%)")
    emit("usd-tokens", caption, tabular("llrlrrrrrrr", head, lines),
         [USD_INPUTS / "listed_tokens.csv", PROC / "describe" / "describe.json", USD_INPUTS / "chainlink_check.json"])


def _dci(r: dict | None, what: str) -> str:
    if not r:
        problem(f"no {what}")
        return "---"
    if r.get("n_boot") is not None:
        STATE["nboot"].add(int(r["n_boot"]))
    return f"${fsigned(r.get('delta_tau'), what)}$ {fci(r.get('ci_low'), r.get('ci_high'), what)}"


def _yes(v, yes: str = "met", no: str = "not met") -> str:
    if v is None:
        problem("missing verdict")
        return "---"
    return yes if v else no


def t_registered_vs_revised(reg: dict, rev: dict, seed: int) -> None:
    """Revised analysis: the decision contrasts and verdicts of the registered analysis, as registered, beside the
    same contrasts on the revised scores."""
    begin("registered-vs-revised")
    rows: list[tuple[str, str, str]] = []

    def both(label: str, get, kind: str = "contrast") -> None:
        cells = []
        for name, d in (("registered", reg), ("revised", rev)):
            try:
                v = get(d)
            except (KeyError, TypeError, StopIteration):
                v = None
            if kind == "contrast":
                cells.append(_dci(v, f"{name} {label}"))
            elif kind == "count":
                cells.append(fint(v, f"{name} {label}"))
            elif kind == "tau":
                cells.append(tc(v, f"{name} {label}"))
            else:
                cells.append(_yes(v, *kind.split("/")) if "/" in kind else _yes(v))
        rows.append((label, cells[0], cells[1]))

    def pre(d, a, b):
        return next(r for r in d["w0"]["contrasts_prefixed"] if r["a"] == a and r["b"] == b)

    def after(d, a, b, out):
        return next(r for r in d["w0"]["contrasts_after"] if r["a"] == a and r["b"] == b and r["outcome"] == out)

    both("Matched cohort (contracts)", lambda d: d["same"]["cohort"], "count")
    both("W0 spender cohort", lambda d: d["w0"]["spenders"], "count")
    both("W1 spender cohort", lambda d: d["w1"]["spenders"], "count")
    both("W1 traders", lambda d: d["w1"]["traders"], "count")
    both("EndorseRank vs.\\ AWP, same window ($\\tau$)", lambda d: d["same"]["inter_method"]["endorserank_vs_awp"], "tau")
    rows.append(("\\midrule", "", ""))
    both("A, W0: C-PR minus C-PR ($\\lambda=1$), new approval pairs", lambda d: pre(d, "cpr_l50", "cpr_l100"))
    both("A, W0: C-PR minus C-PR ($\\lambda=0$), new transfer senders", lambda d: pre(d, "cpr_l50", "cpr_l0"))
    both("Rule A, primary part", lambda d: d["w0"]["rule_a_primary"]["pass"], "verdict")
    both("Rule A, secondary part", lambda d: d["same"]["rule_a_secondary"]["pass"], "verdict")
    rows.append(("\\midrule", "", ""))
    for k, lab in (("F1", "new approval pairs"), ("F2", "new transfer senders"), ("F3", "liquidation-free close rate")):
        both(f"B, {k}: C-PR minus C-PR ($\\lambda=0$), {lab}", lambda d, k=k: d["w1"]["rule_b"][k])
    both("Rule B (F1, F2 and F3)", lambda d: d["w1"]["rule_b"]["decision"], "verdict")
    both("Rule B, sensitivity 1 (AWP as comparator)", lambda d: d["w1"]["sensitivity_awp"]["decision"], "verdict")
    both("Rule B, sensitivity 2 (isolated nodes)", lambda d: d["w1"]["sensitivity_isolated"]["decision"], "verdict")
    both("F6 (rule A, primary part, on W1)", lambda d: d["w1"]["rule_b"]["F6"], "holds/fails")
    rows.append(("\\midrule", "", ""))
    both("P, W1: in-approve degree minus transfer in-degree", lambda d: d["w1"]["neutral_w1"]["grid"]["P"][LIQ])
    both("Q, W1: EndorseRank (activity restarts) minus AWP", lambda d: d["w1"]["neutral_w1"]["grid"]["Q"][LIQ])
    both("R1 (count-level lead)", lambda d: d["w1"]["neutral_rules"]["R1"], "verdict")
    both("R2 (PageRank-level lead)", lambda d: d["w1"]["neutral_rules"]["R2"], "verdict")
    both("R3 (specificity)", lambda d: d["w1"]["neutral_rules"]["R3"], "applies/does not apply")
    rows.append(("\\midrule", "", ""))
    both("W0: EndorseRank minus in-approve degree, new pairs", lambda d: after(d, "endorserank", "t1_in_approve_degree", APPR))
    both("W0: AWP minus transfer in-degree, new senders", lambda d: after(d, "awp", "t1_in_degree", SEND))
    both("W1: EndorseRank minus in-approve degree, new pairs",
         lambda d: d["w1"]["endorserank_results"]["endorserank_minus_degree_appr"])
    both("W1: AWP minus transfer in-degree, new senders", lambda d: d["w1"]["endorserank_results"]["awp_minus_degree_send"])
    lines = [r[0] if r[0] == "\\midrule" else f"{r[0]} & {r[1]} & {r[2]} \\\\" for r in rows]
    nb = sorted(STATE["nboot"])
    caption = (
        "Decision contrasts and verdicts of the registered analysis (amounts in raw base units, every ERC-20 token, "
        "$b=1$), exactly as obtained under the analysis plan and the W1 registration, beside the same contrasts on "
        "the revised scores (amounts in USD, listed tokens only). The revision was decided after the registered "
        "results were known; the revised column applies the registered rules and thresholds to the revised scores "
        "and is not a registered test. The last block holds degree contrasts that no rule of either analysis "
        "decides; they are reported in both. $\\Delta\\tau$ with 95\\% paired bootstrap interval "
        f"({' and '.join(fint(x) for x in nb)} resamples, seed {seed}); the rules and their thresholds are in "
        "Sections~\\ref{sec:holdout-protocol} and~\\ref{sub:fresh-holdout}."
    )
    head = "Quantity & Registered analysis & Revised analysis"
    emit("registered-vs-revised", caption, tabular("lcc", head, lines),
         [PROC_SHARED / "same-window" / "eval_summary.json", PROC_SHARED / "holdout-w0" / "eval_summary.json",
          PROC_SHARED / "registered-w1" / "eval_summary.json", SOURCES["same"], SOURCES["w0"], SOURCES["w1"]])


def t_robustness_sample_size(rob: dict, bench: dict | None, n: int, cfg: dict) -> None:
    begin("robustness-sample-size")
    stages = rob.get("sample_definition") or []
    if not stages:
        SKIPPED.append("robustness-sample-size (no stages)")
        return
    bst = {int(s["n"]): s for s in ((bench or {}).get("scaling") or [])}
    lines = []
    for st in stages:
        er, awp = st.get("endorserank") or {}, st.get("awp") or {}
        cells = []
        for f in ("allowance", "transfer", "sybil_stability"):
            cells += [f3(er.get(f), f"ER {f} n={st.get('n')}"), f3(awp.get(f), f"AWP {f} n={st.get('n')}")]
        if bench is not None:
            b = bst.get(int(st["n"])) or {}
            if not b:
                problem(f"no benchmark stage n={st['n']}")
            be, ba = b.get("endorserank") or {}, b.get("awp") or {}
            cells += [f3(be.get("mean_s"), "ER runtime"), f3(ba.get("mean_s"), "AWP runtime"),
                      ratio(ba.get("mean_s"), be.get("mean_s"))]
        lines.append(f"{fint(st.get('n'))} & {' & '.join(cells)} \\\\")
    seed = cfg["benchmark"]["scaling_seed"]
    runtime = " Runtimes are the measurements of Table~\\ref{tab:benchmark-scaling}." if bench is not None else ""
    caption = (
        "Sensitivity of the family means to the evaluation set: family-mean Kendall $\\tau$ of EndorseRank (ER) and AWP "
        f"on deterministic SHA256 subsamples of the matched cohort (seed \\texttt{{{seed}}}, full cohort $n={fint(n)}$ "
        "contracts), each stage scored on the edges incident to its contracts; all.\\ = allowance, tr.\\ = transfer, "
        "Syb.\\ = Sybil stability. Rows are evaluated on different contract sets, so their $\\tau$ values are not "
        "comparable with Table~\\ref{tab:alignment-hybrid}; they show how much the statistic moves with the evaluation "
        f"population. No intervals were computed for the stages.{runtime}"
    )
    head = "$n$ & ER all. & AWP all. & ER tr. & AWP tr. & ER Syb. & AWP Syb."
    spec = "r" + "c" * 6
    if bench is not None:
        head += " & ER (s) & AWP (s) & AWP/ER time"
        spec += "rrr"
    srcs = [SOURCES["rob"]] + ([SOURCES["bench"]] if bench is not None else [])
    emit("robustness-sample-size", caption, tabular(spec, head, lines), srcs)


# --------------------------------------------------------------------------- holdout W0


def t_endorserank_restarts(same: dict, w0: dict, w1: dict, seed: int, cfg: dict) -> None:
    begin("endorserank-restarts")
    fams = same.get("families") or {}
    rows = (("endorserank", "EndorseRank", "uniform"), ("endorserank_activity", "EndorseRank", "by approving activity"),
            ("awp", "AWP", "by sending activity"))
    lines = []
    for m, name, restart in rows:
        cells = [stack((fams.get(m) or {}).get(f), f"{m} {f}") for f, _ in FAMILIES]
        cells += [stack(((w0.get("taus") or {}).get(m) or {}).get(lab), f"W0 {m} {lab}") for lab in (APPR, SEND)]
        cells += [stack(((w1.get("spender_taus") or {}).get(m) or {}).get(lab), f"W1 {m} {lab}") for lab in (APPR, SEND)]
        lines.append(f"{name} & {restart} & {' & '.join(cells)} \\\\")
    caption = (
        "EndorseRank with uniform restarts and with restarts weighted by approving activity, AWP's rule applied to the "
        "allowance graph, next to AWP: family-mean Kendall $\\tau$ on the matched cohort "
        f"($n={fint(same.get('cohort'))}$ contracts) and $\\tau$ with the two spender labels in W0 "
        f"($n={fint(w0.get('spenders'))}$ spender contracts, scores frozen at {tex_date(cfg['holdout']['score_end'])}) "
        f"and W1 ($n={fint(w1.get('spenders'))}$, frozen at {tex_date(cfg['registered_window']['score_end'])}). Both "
        f"EndorseRank rows weight each latest allowance by $\\sigma(\\Delta t)V(z)$. {boot_note(seed)}"
    )
    head = (" & & \\multicolumn{3}{c}{Same window, matched cohort} & \\multicolumn{2}{c}{W0, spenders} & "
            "\\multicolumn{2}{c}{W1, spenders} \\\\\n\\cmidrule(lr){3-5} \\cmidrule(lr){6-7} \\cmidrule(lr){8-9}\n"
            "Method & Restarts & Transfer & Allowance & Sybil & New approval pairs & New senders & New approval pairs & "
            "New senders")
    emit("endorserank-restarts", caption, tabular("llccccccc", head, lines),
         [SOURCES["same"], SOURCES["w0"], SOURCES["w1"]])


def t_holdout_spenders(w0: dict, seed: int, cfg: dict) -> None:
    begin("holdout-spenders")
    taus = w0.get("taus") or {}

    def cell(m: str) -> str:
        return " & ".join(tc((taus.get(m) or {}).get(lab), f"{m} {lab}") for lab in (APPR, SEND))

    lines = method_rows(W0_ROWS, cell)
    h = cfg["holdout"]
    kinds = w0.get("spender_account_types") or {}
    caption = (
        f"Temporal holdout W0 on the spender cohort ($n={fint(w0.get('spenders'))}$ contracts): Kendall $\\tau$ between "
        f"scores frozen at {tex_date(h['score_end'])} and two labels counted on the contract between "
        f"{tex_date(h['outcome_start'])} and {tex_date(h['outcome_end'])}: the number of new owner--spender approval "
        "pairs and the number of addresses that sent a transfer to the contract for the first time. The cohort keeps "
        f"the {fint(kinds.get('contract'))} contracts among the {fint(sum(kinds.values()))} spenders with a positive "
        f"latest allowance at the freeze; {fint(kinds.get('none', 0))} EOAs without code and "
        f"{fint(kinds.get('eip7702', 0))} EOAs with an EIP-7702 delegation are left out. "
        f"{fint(w0.get('gained_new_approvals'))} contracts received at least one new pair "
        f"and {fint(w0.get('gained_new_senders'))} at least one new sender. Baseline rows are the raw degrees at $t_1$ "
        "that each single-layer PageRank smooths. C-PR ($\\lambda=1$) and C-PR ($\\lambda=0$) are the allowance and "
        f"transfer layers of the coupled operator walked alone. {boot_note(seed)}"
    )
    head = "Score at $t_1$ & New approval pairs ($\\tau$ [95\\% CI]) & New transfer senders ($\\tau$ [95\\% CI])"
    emit("holdout-spenders", caption, tabular("lcc", head, lines), [SOURCES["w0"]])


def _w0_label(r: dict) -> str:
    return f"{SHORT[r['a']]} minus {SHORT[r['b']]}"


def t_holdout_diff(w0: dict, seed: int) -> None:
    begin("holdout-diff")
    pre = w0.get("contrasts_prefixed") or []
    post = [r for r in w0.get("contrasts_after") or [] if not is_er_awp(r)]
    if not pre:
        SKIPPED.append("holdout-diff (no contrasts)")
        return
    first = "Rule A, primary part, fixed in the plan" if REVISED else "Fixed before the data"
    lines = [f"\\multicolumn{{7}}{{l}}{{\\emph{{{first}}}}} \\\\"]
    lines += [contrast_line(_w0_label(r), r, LABEL_WORDS[r["outcome"]]) for r in pre]
    if post:
        lines += ["\\midrule", "\\multicolumn{7}{l}{\\emph{Computed after the labels were known}} \\\\"]
        lines += [contrast_line(_w0_label(r), r, LABEL_WORDS[r["outcome"]]) for r in post]
    rule = w0.get("rule_a_primary") or {}
    # Rule A, primary part: no worse = interval of C-PR minus C-PR(l=1) not below zero; better = interval above zero.
    appr = next((r for r in pre if r["a"] == "cpr_l50" and r["b"] == "cpr_l100" and r["outcome"] == APPR), {})
    send = next((r for r in pre if r["a"] == "cpr_l50" and r["b"] == "cpr_l0" and r["outcome"] == SEND), {})
    if appr and send:
        if bool(appr["ci_high"] >= 0) != bool(rule.get("no_worse_on_new_approvals")):
            problem("rule A no-worse verdict does not follow from its interval")
        if bool(send["ci_low"] > 0) != bool(rule.get("better_on_new_senders")):
            problem("rule A better verdict does not follow from its interval")
    yes = {True: "holds", False: "fails"}
    caption = (
        f"Paired bootstrap differences on the spender holdout W0 ($n={fint(w0.get('spenders'))}$ contracts; "
        f"{fint(max(STATE['nboot']) if STATE['nboot'] else None)} resamples shared by $a$ and $b$, seed {seed}). The "
        + ("first block holds the two contrasts of the primary part of rule A, fixed in the analysis plan committed on "
           "9~October~2026 before any data and applied here to the revised scores (C-PR against C-PR ($\\lambda=1$) on "
           "new approval pairs and against C-PR " if REVISED else
           "first block holds the two contrasts fixed before the data, the primary part of rule A in the analysis "
           "plan committed on 9~October~2026 (C-PR against C-PR ($\\lambda=1$) on new approval pairs and against C-PR ")
        + "($\\lambda=0$) on new transfer senders). The second block was computed after the labels were known: the "
        "increment of C-PR ($\\lambda=1$), the allowance layer walked alone, over its raw degree at $t_1$, the same "
        "comparisons for S-PR, the increments of EndorseRank and AWP over their raw degrees, C-PR against C-PR "
        "($\\lambda=0$) on new approval pairs, and C-PR against EndorseRank and AWP. Primary part of rule A (C-PR no "
        "worse than C-PR ($\\lambda=1$) on new approval pairs and better than C-PR ($\\lambda=0$) on new transfer "
        f"senders): no worse {yes[bool(rule.get('no_worse_on_new_approvals'))]}, better "
        f"{yes[bool(rule.get('better_on_new_senders'))]}, so the rule is {'met' if rule.get('pass') else 'not met'}. "
        "The differences between EndorseRank and AWP are in Table~\\ref{tab:endorserank-awp-holdout}."
    )
    emit("holdout-diff", caption, tabular("llccccc", CONTRAST_HEAD_LABEL, lines), [SOURCES["w0"]])


def t_holdout_receiving(w0: dict, seed: int) -> None:
    begin("holdout-receiving")
    rec = w0.get("receiving") or {}
    taus = rec.get("taus") or {}
    if not taus:
        SKIPPED.append("holdout-receiving (no receiving subset)")
        return
    order = (("endorserank", "EndorseRank"), ("awp", "AWP"), None,
             ("t1_in_approve_degree", "In-approve degree at $t_1$"), ("t1_in_degree", "Transfer in-degree at $t_1$"))
    lines = method_rows(order, lambda m: " & ".join(tc((taus.get(m) or {}).get(lab), f"{m} {lab}")
                                                   for lab in (APPR, SEND)))
    diffs = rec.get("contrasts") or []
    if diffs:
        lines.append("\\midrule")
        for r in diffs:
            lines.append(f"{_w0_label(r)} ({LABEL_WORDS[r['outcome']]}) & \\multicolumn{{2}}{{c}}{{$\\Delta\\tau="
                         f"{fsigned(r.get('delta_tau'))}$ {fci(r.get('ci_low'), r.get('ci_high'))}}} \\\\")
            if r.get("n_boot") is not None:
                STATE["nboot"].add(int(r["n_boot"]))
    n_sp, n_rec = w0.get("spenders"), rec.get("n")
    cov = w0.get("coverage") or {}
    caption = (
        f"Spender holdout W0 restricted to the {fint(n_rec)} of the {fint(n_sp)} spender contracts that had received a "
        f"transfer from another address before the freeze ($n={fint(n_rec)}$). The other "
        f"{fint(n_sp - n_rec if n_sp is not None and n_rec is not None else None)} have no inbound transfer edge from "
        f"another address, and {fint(cov.get('spenders_without_transfer_edge'))} spenders score zero under AWP. The "
        f"restriction was chosen after the results were known. {boot_note(seed)}"
    )
    head = "Score at $t_1$ & New approval pairs ($\\tau$ [95\\% CI]) & New transfer senders ($\\tau$ [95\\% CI])"
    emit("holdout-receiving", caption, tabular("lcc", head, lines), [SOURCES["w0"]])


PROFIT_LABELS = ("profitable_closes", "realized_gain", "profitable_share", "non_loss_share")


def t_holdout_traders(w0: dict, seed: int, cfg: dict) -> None:
    begin("holdout-traders")
    tr = w0.get("traders") or {}
    taus = tr.get("taus") or {}
    if not taus:
        SKIPPED.append("holdout-traders (no trader run)")
        return
    lines = method_rows(W0_ROWS, lambda m: " & ".join(stack((taus.get(m) or {}).get(lab), f"{m} {lab}")
                                                      for lab in PROFIT_LABELS))
    h = cfg["holdout"]
    caption = (
        f"W0 trader run: Kendall $\\tau$ between scores frozen at {tex_date(h['score_end'])} and GMX~V2 labels counted "
        f"from {tex_date(h['outcome_start'])} to {tex_date(h['outcome_end'])}, on the $n={fint(tr.get('n'))}$ GMX~V2 "
        f"contract accounts in the freeze-date graph with at least {NUMBER_WORDS[cfg['gmx_arbitrum']['min_closes']]} "
        f"closes in that window, {fint(tr.get('with_any_approval_received'))} of which had received an approval by the "
        f"freeze. The run is exploratory; the liquidation labels of W0 were left for the {REG}comparison "
        "(Table~\\ref{tab:neutral-label-contrasts}). Profitable closes and realized gain grow with the number of "
        f"closes; the two shares do not. {boot_note(seed)}"
    )
    head = "Score at $t_1$ & " + " & ".join(TRADER_LABELS[lab] for lab in PROFIT_LABELS)
    emit("holdout-traders", caption, tabular("lcccc", head, lines), [SOURCES["w0"]])


def t_endorserank_awp_holdout(w0: dict, w1: dict | None, supp: dict | None, seed: int, cfg: dict) -> None:
    begin("endorserank-awp-holdout")
    min_closes = NUMBER_WORDS[cfg["gmx_arbitrum"]["min_closes"]]
    sp_counts, tr_counts = [], []

    def traders(key: str, title: str):
        nw = (w1 or {}).get(key) or {}
        r = ((nw.get("grid") or {}).get("er_awp") or {}).get(LIQ)
        if not r:
            return None
        tr_counts.append(int(r.get("n_boot") or 0))
        n = fint(nw.get("n"))
        return (f"{title}, traders with at least {min_closes} closes ($n={n}$)", f"{title} traders $n={n}$",
                [("EndorseRank minus AWP", LABEL_WORDS[LIQ], r)])

    blocks = []
    sp0 = [r for r in w0.get("contrasts_after") or [] if is_er_awp(r)]
    if sp0:
        sp_counts += [int(r.get("n_boot") or 0) for r in sp0]
        n = fint(w0.get("spenders"))
        blocks.append((f"W0, spenders ($n={n}$)", f"W0 spenders $n={n}$",
                       [(_w0_label(r), LABEL_WORDS[r["outcome"]], r) for r in sp0]))
    blocks.append(traders("neutral_w0", "W0"))
    s1 = (supp or {}).get("w1") or {}
    sp1 = [(s1.get(k), lab) for k, lab in (("er_minus_awp_appr", APPR), ("er_minus_awp_send", SEND)) if s1.get(k)]
    if sp1:
        if w1 and s1.get("n") != w1.get("spenders"):
            problem(f"supplementary W1 n={s1.get('n')} differs from the W1 spender cohort {w1.get('spenders')}")
        sp_counts += [int(r.get("n_boot") or 0) for r, _ in sp1]
        n = fint(s1.get("n"))
        blocks.append((f"W1, spenders ($n={n}$)", f"W1 spenders $n={n}$",
                       [("EndorseRank minus AWP", LABEL_WORDS[lab], r) for r, lab in sp1]))
    blocks.append(traders("neutral_w1", "W1"))
    blocks = [b for b in blocks if b]
    if not blocks:
        SKIPPED.append("endorserank-awp-holdout (no EndorseRank-AWP contrasts)")
        return
    lines = []
    for title, _, rows in blocks:
        if lines:
            lines.append("\\midrule")
        lines.append(f"\\multicolumn{{7}}{{l}}{{\\emph{{{title}}}}} \\\\")
        lines += [contrast_line(name, r, lab) for name, lab, r in rows]
    parts_ = []
    if sp_counts:
        parts_.append(f"{fint(max(sp_counts))} for the spenders")
    if tr_counts:
        parts_.append(f"{fint(max(tr_counts))} for the traders")
    w1_sp = (f" The W1 spender rows were computed from the saved W1 scores after the {'W1' if REVISED else 'registered'} evaluation, with the "
             "resamples of Table~\\ref{tab:fresh-holdout}." if sp1 else "")
    sizes = "; ".join(size for _, size, _ in blocks)
    caption = (
        f"Paired bootstrap differences between EndorseRank and AWP out of window ({sizes}). "
        "None of them enters rule A or rule B: "
        "the spender rows were computed after the labels were known, and the trader rows are the EndorseRank-minus-AWP "
        f"pair of the {REG}comparison on an outcome built from neither edge type "
        f"(Tables~\\ref{{tab:neutral-label-contrasts}} and~\\ref{{tab:neutral-label-grid}}).{w1_sp} Within each block "
        f"$a$ and $b$ share the contract resamples ({' and '.join(parts_)}; seed {seed})."
    )
    srcs = [SOURCES["w0"]] + ([SOURCES["supp"]] if sp1 else []) + ([SOURCES["w1"]] if w1 else [])
    emit("endorserank-awp-holdout", caption, tabular("llccccc", CONTRAST_HEAD_LABEL, lines), srcs)


# --------------------------------------------------------------------------- registered window W1


def t_fresh_holdout(w1: dict, seed: int, cfg: dict) -> None:
    begin("fresh-holdout")
    sp, tr = w1.get("spender_taus") or {}, w1.get("trader_taus") or {}

    def cell(m: str) -> str:
        cells = [tc((sp.get(m) or {}).get(lab), f"{m} {lab}") for lab in (APPR, SEND)]
        return " & ".join(cells + [tc(tr.get(m), f"{m} liquidation-free rate")])

    lines = method_rows(W1_ROWS, cell)
    rw = cfg["registered_window"]
    caption = (
        f"{W1_NAME}: Kendall $\\tau$ between scores frozen at {tex_date(rw['score_end'])} and the three "
        f"{REG}labels{' of rule B' if REVISED else ''}, counted from {tex_date(rw['outcome_start'])} to {tex_date(rw['outcome_end'])}. The "
        f"spenders are the $n={fint(w1.get('spenders'))}$ contract spenders holding a positive latest allowance at the "
        f"freeze; {fint(w1.get('gained_new_approvals'))} of them gained a new approval pair and "
        f"{fint(w1.get('gained_new_senders'))} a new sender. The traders are the $n={fint(w1.get('traders'))}$ GMX~V2 "
        f"contract accounts in the freeze-date graph with at least {NUMBER_WORDS[cfg['gmx_arbitrum']['min_closes']]} "
        f"closes in the label window; {fint(w1.get('traders_liquidated'))} of them had at least one liquidation and "
        f"{fint(w1.get('traders_all_liquidated'))} had only liquidations. C-PR ($\\lambda=0$) is the comparator of "
        "rule B and AWP that of its first sensitivity analysis (Table~\\ref{tab:fresh-contrasts}); EndorseRank is in "
        f"Table~\\ref{{tab:fresh-posthoc}}. {boot_note(seed)}"
    )
    head = (f" & \\multicolumn{{2}}{{c}}{{Spenders ($n={fint(w1.get('spenders'))}$)}} & "
            f"Traders ($n={fint(w1.get('traders'))}$) \\\\\n\\cmidrule(lr){{2-3}} \\cmidrule(lr){{4-4}}\n"
            f"Score at {tex_date(rw['score_end']).replace('~', ' ')} & New approval pairs & New transfer senders & "
            "Liquidation-free close rate")
    emit("fresh-holdout", caption, tabular("lccc", head, lines), [SOURCES["w1"]])


F_LABEL = {"F1": APPR, "F2": SEND, "F3": LIQ, "F4": LIQ, "F5": LIQ, "F6a": APPR, "F6b": SEND}
F_COMPARATOR = {"F5": "cpr_l100", "F6a": "cpr_l100", "F6b": "cpr_l0"}


def _verdict_ok(r: dict, delta: float) -> bool | None:
    lo, hi = _num(r.get("ci_low")), _num(r.get("ci_high"))
    if lo is None or hi is None:
        return None
    return {"superiority": lo > 0, "non_inferiority": lo > -delta, "no_worse": hi >= 0}.get(r.get("test"))


def _f_line(key: str, r: dict, comparator: str, delta: float, block: str) -> str:
    if not r:
        problem(f"no {key} in {block}")
        r = {}
    if r.get("n_boot") is not None:
        STATE["nboot"].add(int(r["n_boot"]))
    test = {"superiority": "superiority", "non_inferiority": f"non-inferiority, $-{delta:.2f}$",
            "no_worse": "no worse"}.get(r.get("test"), "---")
    ok = _verdict_ok(r, delta)
    if ok is None or ok != bool(r.get("holds")):
        problem(f"{block} {key}: verdict {r.get('holds')} does not follow from its interval")
    return (
        f"{key} & C-PR vs.\\ {SHORT[comparator]} & {LABEL_WORDS[F_LABEL[key]]} & {test} & "
        f"{f3(r.get('a_tau'), f'tau_a {key}')} & {f3(r.get('b_tau'), f'tau_b {key}')} & {delta_ci(r, key)} & "
        f"{'holds' if r.get('holds') else 'fails'} \\\\"
    )


def t_fresh_contrasts(w1: dict, seed: int) -> None:
    begin("fresh-contrasts")
    rule = w1.get("rule_b") or {}
    if not rule:
        SKIPPED.append("fresh-contrasts (no rule_b)")
        return
    delta = float(w1.get("delta"))
    lines = ["\\multicolumn{8}{l}{\\emph{Rule B: C-PR ($\\lambda=0.5$) against its transfer layer walked alone, "
             "C-PR ($\\lambda=0$)}} \\\\"]
    lines += [_f_line(k, rule.get(k), F_COMPARATOR.get(k, "cpr_l0"), delta, "rule B") for k in ("F1", "F2", "F3")]
    decision = all(bool((rule.get(k) or {}).get("holds")) for k in ("F1", "F2", "F3"))
    if decision != bool(rule.get("decision")):
        problem("rule B decision does not follow from F1-F3")
    lines.append(f"\\multicolumn{{7}}{{l}}{{Decision: F1, F2 and F3 must all hold}} & "
                 f"{'met' if rule.get('decision') else 'not met'} \\\\")
    lines += ["\\midrule", "\\multicolumn{8}{l}{\\emph{Reported, not part of the decision}} \\\\"]
    lines += [_f_line(k, rule.get(k), F_COMPARATOR.get(k, "cpr_l0"), delta, "rule B")
              for k in ("F4", "F5", "F6a", "F6b") if k in rule]
    for key, title, comp in (("sensitivity_awp", "Sensitivity analysis 1: AWP as the comparator", "awp"),
                             ("sensitivity_isolated",
                              "Sensitivity analysis 2: contracts outside a graph kept as isolated nodes", "cpr_l0")):
        s = w1.get(key) or {}
        if not s:
            problem(f"no {key}")
            continue
        lines += ["\\midrule", f"\\multicolumn{{8}}{{l}}{{\\emph{{{title}}}}} \\\\"]
        lines += [_f_line(k, s.get(k), F_COMPARATOR.get(k, comp), delta, key)
                  for k in ("F1", "F2", "F3", "F4", "F5", "F6a", "F6b") if k in s]
    n_tr = w1.get("traders")
    caption = (
        f"{W1_NAME}: the paired contrasts F1--F6 of rule B with their verdicts, and the two {REG}"
        "sensitivity analyses"
        + (" (rule B and its sensitivity analyses were registered for the raw-unit analysis; here they are applied to "
           "the revised scores)" if REVISED else "")
        + ". $\\Delta\\tau=\\tau_a-\\tau_b$, with C-PR ($\\lambda=0.5$) as $a$. Superiority holds "
        f"when the interval lies above zero; non-inferiority holds when its lower end lies above $-\\delta=-{delta:.2f}$; "
        "F6a, the first part of rule A, holds when the interval contains zero or lies above it. F1, F2, F6a and F6b "
        f"are on the spenders ($n={fint(w1.get('spenders'))}$ contracts), F3--F5 on the traders ($n={fint(n_tr)}$), as "
        f"in Table~\\ref{{tab:fresh-holdout}}. {boot_note(seed)}"
    )
    head = " & Contrast & Label & Test & $\\tau_a$ & $\\tau_b$ & $\\Delta\\tau$ [95\\% CI] & Verdict"
    emit("fresh-contrasts", caption, tabular("lllcccll", head, lines), [SOURCES["w1"]])


def t_fresh_posthoc(w1: dict, supp: dict | None, seed: int, cfg: dict) -> None:
    begin("fresh-posthoc")
    sp, tr = w1.get("spender_taus") or {}, w1.get("trader_taus") or {}
    res = w1.get("endorserank_results") or {}
    if "endorserank" not in sp:
        SKIPPED.append("fresh-posthoc (no EndorseRank in W1)")
        return

    def cell(m: str) -> str:
        cells = [tc((sp.get(m) or {}).get(lab), f"{m} {lab}") for lab in (APPR, SEND)]
        return " & ".join(cells + [tc(tr.get(m), f"{m} liquidation-free rate")])

    order = (*W1_BASELINES, None, ("endorserank", "EndorseRank"),
             ("endorserank_activity", "EndorseRank, restarts by approving activity"), ("awp", "AWP"),
             ("cpr_l50", METHOD_LABELS["cpr_l50"]))
    lines = method_rows(order, cell)
    names = (
        ("endorserank_minus_degree_appr", "EndorseRank minus in-approve degree, new approval pairs"),
        ("awp_minus_degree_send", "AWP minus transfer in-degree, new transfer senders"),
        ("cpr_minus_endorserank_appr", "C-PR minus EndorseRank, new approval pairs"),
        ("cpr_minus_endorserank_liq", "C-PR minus EndorseRank, liquidation-free close rate"),
    )
    if res:
        lines.append("\\midrule")
        for key, name in names:
            lines.append(f"{name} & \\multicolumn{{3}}{{l}}{{{delta_math(res.get(key), key)}}} \\\\")
    s1 = (supp or {}).get("w1") or {}
    act = (
        ("er_activity_minus_degree_appr", "EndorseRank (activity restarts) minus in-approve degree, new approval pairs"),
        ("er_activity_minus_er_appr", "EndorseRank (activity restarts) minus EndorseRank, new approval pairs"),
        ("er_activity_minus_er_send", "EndorseRank (activity restarts) minus EndorseRank, new transfer senders"),
    )
    act = [(k, name) for k, name in act if s1.get(k)]
    if act:
        if s1.get("n") != w1.get("spenders"):
            problem(f"supplementary W1 n={s1.get('n')} differs from the W1 spender cohort {w1.get('spenders')}")
        lines.append("\\midrule")
        for key, name in act:
            lines.append(f"{name} & \\multicolumn{{3}}{{l}}{{{delta_math(s1.get(key), key)}}} \\\\")
    rw = cfg["registered_window"]
    act_text = (" The contrasts of EndorseRank with activity restarts were computed afterwards from the saved W1 "
                "scores." if act else "")
    caption = (
        f"EndorseRank and its variant with activity restarts on the cohorts and labels of the {W1_NAME_LC} "
        f"(spenders $n={fint(w1.get('spenders'))}$ contracts, traders $n={fint(w1.get('traders'))}$). Neither these "
        "rows nor the contrasts below them are part of rule B, and the contrasts were not named in the registration."
        f"{act_text} The AWP, C-PR and degree rows repeat Table~\\ref{{tab:fresh-holdout}}, and every contrast uses "
        "the same contract resamples; the differences between EndorseRank and AWP are in "
        f"Table~\\ref{{tab:endorserank-awp-holdout}}. {boot_note(seed)}"
    )
    head = (f" & \\multicolumn{{2}}{{c}}{{Spenders ($n={fint(w1.get('spenders'))}$)}} & "
            f"Traders ($n={fint(w1.get('traders'))}$) \\\\\n\\cmidrule(lr){{2-3}} \\cmidrule(lr){{4-4}}\n"
            f"Score at {tex_date(rw['score_end']).replace('~', ' ')} & New approval pairs & New transfer senders & "
            "Liquidation-free close rate")
    emit("fresh-posthoc", caption, tabular("lccc", head, lines), [SOURCES["w1"]] + ([SOURCES["supp"]] if act else []))


W1_OTHER_LABELS = ("no_liquidation", "profitable_closes", "realized_gain", "profitable_share", "non_loss_share")


def t_fresh_traders(w1: dict, seed: int, cfg: dict) -> None:
    begin("fresh-traders")
    nw = w1.get("neutral_w1") or {}
    taus = nw.get("taus") or {}
    if not taus:
        SKIPPED.append("fresh-traders (no neutral_w1 taus)")
        return
    lines = method_rows(W1_TRADER_ROWS, lambda m: " & ".join(stack((taus.get(m) or {}).get(lab), f"{m} {lab}")
                                                             for lab in W1_OTHER_LABELS))
    rw = cfg["registered_window"]
    caption = (
        f"{W1_NAME}, traders: Kendall $\\tau$ between scores frozen at {tex_date(rw['score_end'])} and the "
        f"other GMX~V2 labels counted from {tex_date(rw['outcome_start'])} to {tex_date(rw['outcome_end'])}, on the "
        f"$n={fint(nw.get('n'))}$ contract accounts with at least {NUMBER_WORDS[cfg['gmx_arbitrum']['min_closes']]} "
        "closes in that window. No liquidation is 1 when none of the account's closes was a liquidation. Profitable "
        "closes and realized gain grow with the number of closes; the two shares do not. These labels are reported "
        "and do not enter rule B. The intervals use the resamples of Table~\\ref{tab:neutral-label-contrasts}. "
        f"{boot_note(seed)}"
    )
    head = (f"Score at {tex_date(rw['score_end']).replace('~', ' ')} & "
            + " & ".join(TRADER_LABELS[lab] for lab in W1_OTHER_LABELS))
    emit("fresh-traders", caption, tabular("lccccc", head, lines), [SOURCES["w1"]])


def _rules_text(rules: dict) -> str:
    if not rules:
        problem("no neutral-label rules")
        return ""
    r1 = "met" if rules.get("R1") else "not met"
    r2 = "met" if rules.get("R2") else "not met"
    r3 = "applies" if rules.get("R3") else "does not apply"
    head = "Registered rules applied to the revised scores" if REVISED else "Registered rules"
    return f"{head}: R1 (count-level lead) {r1}; R2 (PageRank-level lead) {r2}; R3 (specificity) {r3}."


def _window_title(cfg_window: dict, n, label: str) -> str:
    return (f"{label}, {month_range(cfg_window['outcome_start'], cfg_window['outcome_end'])} "
            f"($n={fint(n)}$ traders)")


def t_neutral_contrasts(w1: dict, seed: int, cfg: dict) -> None:
    begin("neutral-label-contrasts")
    lines = []
    for key, title, win in (("neutral_w1", W1_NAME, cfg["registered_window"]),
                            ("neutral_w0", "Window W0", cfg["holdout"])):
        nw = w1.get(key) or {}
        if not nw:
            problem(f"no {key}")
            continue
        if lines:
            lines.append("\\midrule")
        lines.append(f"\\multicolumn{{6}}{{l}}{{\\emph{{{_window_title(win, nw.get('n'), title)}}}}} \\\\")
        grid = nw.get("grid") or {}
        for pair, name in NEUTRAL_ROWS:
            r = (grid.get(pair) or {}).get(LIQ) or {}
            if not r:
                problem(f"no {pair} on {key}")
            if r.get("n_boot") is not None:
                STATE["nboot"].add(int(r["n_boot"]))
            c975 = fci(r.get("ci975_low"), r.get("ci975_high"), f"97.5% interval of {pair}") if pair in ("P", "Q") else "--"
            lines.append(f"{name} & {f3(r.get('a_tau'))} & {f3(r.get('b_tau'))} & {f3(r.get('delta_tau'))} & "
                         f"{fci(r.get('ci_low'), r.get('ci_high'))} & {c975} \\\\")
            if pair in ("P", "Q") and r:
                lo, hi = _num(r.get("ci975_low")), _num(r.get("ci975_high"))
                if lo is not None and hi is not None and not (lo <= r["ci_low"] and r["ci_high"] <= hi):
                    problem(f"{key} {pair}: 97.5% interval does not contain the 95% interval")
        for pair, name in NEUTRAL_ROWS[:2]:
            s = (nw.get("stratified") or {}).get(pair) or {}
            if not s:
                problem(f"no stratified {pair} on {key}")
            lines.append(f"\\quad {name}, stratified by closes & {f3(s.get('a_tau'))} & {f3(s.get('b_tau'))} & "
                         f"{f3(s.get('delta_tau'))} & {fci(s.get('ci_low'), s.get('ci_high'))} & -- \\\\")
    if not lines:
        SKIPPED.append("neutral-label-contrasts (no neutral blocks)")
        return
    caption = (
        "Allowance-side against transfer-side scores on the liquidation-free close rate of the GMX~V2 contract traders "
        f"with at least {NUMBER_WORDS[cfg['gmx_arbitrum']['min_closes']]} closes in the label window, a label built "
        "from neither edge type ($n="
        f"{fint((w1.get('neutral_w1') or {}).get('n'))}$ traders in W1, $n={fint((w1.get('neutral_w0') or {}).get('n'))}$ "
        "in W0). The pairs, the decision contrasts P and Q with their Bonferroni 97.5\\% intervals and the stratified "
        + ("rows were registered before the July--September logs were extracted, for the raw-unit analysis, and are "
           "applied here to the revised scores; W1 is the primary window and W0 the " if REVISED else
           "rows were registered before the July--September logs were extracted; W1 is the primary window and W0 the ")
        + f"secondary one. Paired contract bootstrap with {fint(max(STATE['nboot']) if STATE['nboot'] else None)} "
        f"resamples (seed {seed}). The stratified rows combine Kendall's $\\tau_b$ within strata of the number of "
        "label-window closes (3--4, 5--9, 10--24, 25 or more), weighted by the number of contract pairs. "
        f"{_rules_text(w1.get('neutral_rules') or {})}"
    )
    head = "Contrast ($a$ minus $b$) & $\\tau_a$ & $\\tau_b$ & $\\Delta\\tau$ & 95\\% CI & 97.5\\% CI"
    emit("neutral-label-contrasts", caption, tabular("lccccc", head, lines), [SOURCES["w1"]])


def t_neutral_recipients(w1: dict, seed: int, cfg: dict) -> None:
    begin("neutral-label-recipients")
    lines = []
    maxdeg = []
    for key, title, win in (("neutral_w1", W1_NAME, cfg["registered_window"]),
                            ("neutral_w0", "Window W0", cfg["holdout"])):
        nw = w1.get(key) or {}
        rec = nw.get("recipients") or {}
        if not rec:
            problem(f"no recipients in {key}")
            continue
        a, b = rec.get("recipients") or {}, rec.get("others") or {}
        if lines:
            lines.append("\\midrule")
        lines.append(f"\\multicolumn{{3}}{{l}}{{\\emph{{{_window_title(win, nw.get('n'), title)}}}}} \\\\")
        lines.append(f"Traders & {fint(a.get('n'))} & {fint(b.get('n'))} \\\\")
        for k, name in (("share_no_liquidation", "Share with no liquidation"),
                        (f"mean_{LIQ}", "Mean liquidation-free close rate"),
                        ("mean_profitable_share", "Mean profitable share"),
                        ("mean_non_loss_share", "Mean non-loss share")):
            lines.append(f"{name} & {f3(a.get(k), f'recipients {k}')} & {f3(b.get(k), f'others {k}')} \\\\")
        lines.append(f"Median closes in the label window & {f1(a.get('median_closes'))} & {f1(b.get('median_closes'))} \\\\")
        if (_num(a.get("n")) or 0) + (_num(b.get("n")) or 0) != (_num(nw.get("n")) or -1):
            problem(f"{key}: recipients and others do not add up to n")
        infl = nw.get("influence_without_top10")
        lines.append(f"\\multicolumn{{3}}{{l}}{{P without the ten recipients of highest in-approve degree: "
                     f"{delta_math(infl, 'influence', signed=False)}}} \\\\")
        maxdeg.append((title.split()[-1], nw.get("max_in_approve_degree")))
    if not lines:
        SKIPPED.append("neutral-label-recipients (no recipients)")
        return
    deg = " and ".join(f"{fint(v)} in {w}" for w, v in maxdeg)
    caption = (
        "GMX~V2 contract traders with a positive in-approve degree at the freeze (recipients) against all other "
        f"labelled traders, in both windows ($n={fint((w1.get('neutral_w1') or {}).get('n'))}$ traders in W1, "
        f"$n={fint((w1.get('neutral_w0') or {}).get('n'))}$ in W0). The comparison of recipients with the other traders "
        "and the influence check were registered with the contrasts of Table~\\ref{tab:neutral-label-contrasts}"
        + (" and are applied here to the revised scores" if REVISED else "") + ". The "
        f"highest in-approve degree among the traders is {deg}, so the ten recipients left out by the influence check "
        "are taken from tied values in node order. The influence check is a paired contract bootstrap on the remaining "
        f"traders ({fint(max(STATE['nboot']) if STATE['nboot'] else None)} resamples, seed {seed})."
    )
    head = " & Recipients & Other traders"
    emit("neutral-label-recipients", caption, tabular("lcc", head, lines), [SOURCES["w1"]])


def t_neutral_grid(w1: dict, seed: int, cfg: dict) -> None:
    begin("neutral-label-grid")
    pairs = ("P", "Q", "layers", "er_awp")
    lines = []
    for key, title, win in (("neutral_w1", W1_NAME, cfg["registered_window"]),
                            ("neutral_w0", "Window W0", cfg["holdout"])):
        nw = w1.get(key) or {}
        grid = nw.get("grid") or {}
        if not grid:
            problem(f"no grid in {key}")
            continue
        if lines:
            lines.append("\\midrule")
        lines.append(f"\\multicolumn{{5}}{{l}}{{\\emph{{{_window_title(win, nw.get('n'), title)}}}}} \\\\")
        for lab, name in TRADER_LABELS.items():
            cells = []
            for p in pairs:
                r = (grid.get(p) or {}).get(lab) or {}
                if r.get("n_boot") is not None:
                    STATE["nboot"].add(int(r["n_boot"]))
                d, ci = f3(r.get("delta_tau"), f"{p} {lab}"), fci(r.get("ci_low"), r.get("ci_high"), f"{p} {lab}")
                cells.append(f"\\begin{{tabular}}[c]{{@{{}}c@{{}}}}{d}\\\\[-1pt]{{\\footnotesize {ci}}}\\end{{tabular}}")
            lines.append(f"{name} & {' & '.join(cells)} \\\\")
    if not lines:
        SKIPPED.append("neutral-label-grid (no grid)")
        return
    caption = (
        "Allowance-side minus transfer-side scores, $\\Delta\\tau$ with 95\\% paired bootstrap interval, on all six "
        f"trader labels of the {W1_NAME_LC} ($n={fint((w1.get('neutral_w1') or {}).get('n'))}$ GMX~V2 contract "
        f"traders) and of W0 ($n={fint((w1.get('neutral_w0') or {}).get('n'))}$). P: in-approve degree minus transfer "
        "in-degree. Q: EndorseRank with activity restarts minus AWP (same edge weights and restart rule). C-PR: "
        f"$\\lambda=1$ minus $\\lambda=0$ (same {'USD' if REVISED else 'raw-amount'} build). ER: EndorseRank minus AWP. Profitable closes and "
        f"realized gain grow with the number of closes; the other four labels do not. {boot_note(seed)}"
    )
    head = "Label & P (counts) & Q (PageRanks) & C-PR layers & ER minus AWP"
    emit("neutral-label-grid", caption, tabular("lcccc", head, lines), [SOURCES["w1"]])


# --------------------------------------------------------------------------- figures


def _style():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Times New Roman", "TeX Gyre Termes", "STIXGeneral", "DejaVu Serif"],
        "mathtext.fontset": "stix",
        "font.size": 10,
        "axes.labelsize": 10.5,
        "legend.fontsize": 8.5,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "savefig.bbox": "tight",
        "savefig.dpi": 300,
        "axes.grid": True,
        "grid.alpha": 0.3,
        "pdf.fonttype": 42,
    })
    return plt


BLUE, RED, GREY = "#2c5f8a", "#a03c3c", "#c8d4e0"


def _save(fig, name: str) -> None:
    import matplotlib.pyplot as plt

    path = OUT["figures"] / name
    fig.savefig(path)
    plt.close(fig)
    WRITTEN.append(path)


def _days(a: str, b: str) -> int:
    ta = dt.datetime.fromisoformat(str(a).replace(" UTC", ""))
    tb = dt.datetime.fromisoformat(str(b).replace(" UTC", ""))
    return int(round((tb - ta).total_seconds() / 86400))


def fig_logistic_decay(cfg: dict) -> None:
    plt = _style()
    k, t0 = float(cfg["reputation"]["awp_decay_k"]), float(cfg["reputation"]["awp_decay_t0_days"])
    obs = _days(cfg["period"]["start_ts"], cfg["period"]["observation_end"])
    w0 = _days(cfg["period"]["start_ts"], cfg["holdout"]["score_end"])
    x = np.linspace(0, obs, obs + 1)
    y = 1.0 / (1.0 + np.exp(k * (x - t0)))
    fig, ax = plt.subplots(figsize=(5.4, 3.3))
    ax.axvspan(0, obs, color=GREY, alpha=0.45, linewidth=0,
               label=f"Ages at the observation anchor (0\u2013{obs:,} days)")
    ax.plot(x, y, color=BLUE, linewidth=2, label=rf"Decay weight, $k={k:g}$, $t_0={t0:g}$ days")
    ax.axvline(t0, color="grey", linestyle="--", linewidth=0.8)
    ax.text(t0 + 12, 0.30, rf"$t_0={t0:g}$ days", fontsize=9)
    ax.annotate("", xy=(w0, 0.97), xytext=(0, 0.97),
                arrowprops={"arrowstyle": "<->", "color": RED, "linewidth": 1.0, "shrinkA": 0, "shrinkB": 0})
    ax.axvline(w0, color=RED, linestyle=":", linewidth=1.0)
    ax.text(w0 / 2, 1.0, f"Ages at the W0 freeze (0\u2013{w0:,} days)", ha="center", va="bottom",
            fontsize=8.5, color=RED)
    ax.set_xlim(-10, obs + 90)
    ax.set_ylim(-0.02, 1.12)
    ticks = sorted({0, int(t0), 365, 730, w0, obs})
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{t:,}" for t in ticks])
    ax.set_xlabel("Age of the event at the anchor (days)")
    ax.set_ylabel("Time-decay weight")
    ax.legend(loc="upper right", bbox_to_anchor=(0.97, 0.86), frameon=True, framealpha=0.9, edgecolor="none")
    _save(fig, "logistic-decay.pdf")


def fig_score_distributions(scores, same: dict) -> None:
    plt = _style()
    fig, axes = plt.subplots(1, 2, figsize=(5.8, 3.0), sharey=True)
    c = (same.get("closed_form") or {}).get("common_value_c")
    tallest = 1.0
    for ax, col, name, color in ((axes[0], "endorserank", "EndorseRank", BLUE), (axes[1], "awp", "AWP", RED)):
        s = scores[col].to_numpy(dtype=float)
        pos = s[s > 0]
        zeros = int((s == 0).sum())
        counts_, _, _ = ax.hist(np.log10(pos), bins=40, color=color, edgecolor="white", linewidth=0.3, log=True,
                                label=f"{name}: {len(pos):,} positive scores\n{zeros:,} contracts score zero (not shown)")
        tallest = max(tallest, float(np.max(counts_)))
        ax.set_ylim(0.6, tallest * 60)  # headroom above the bars for the legend (shared y axis)
        ax.set_xlabel(r"Score ($\log_{10}$)")
        ax.legend(loc="upper right", frameon=False)
        if col == "endorserank" and c:
            vals, counts = np.unique(pos, return_counts=True)
            i = int(np.argmax(counts))
            if np.isclose(vals[i], c, rtol=1e-9, atol=0):
                ax.annotate(f"{counts[i]:,} contracts share the score\nof a node without in-edges",
                            xy=(np.log10(vals[i]), counts[i]), xytext=(0.40, 0.55), textcoords="axes fraction",
                            fontsize=8, arrowprops={"arrowstyle": "->", "linewidth": 0.7})
    axes[0].set_ylabel("Contracts (log scale)")
    fig.tight_layout()
    _save(fig, "score-distributions.pdf")


def fig_rank_scatter(scores, same: dict) -> None:
    plt = _style()
    import matplotlib.ticker as mticker

    er, awp = scores["endorserank"].astype(float), scores["awp"].astype(float)
    n = len(scores)
    x = (n + 1 - er.rank(method="average")).to_numpy()  # 1 = highest; ties share the mid-rank
    y = (n + 1 - awp.rank(method="average")).to_numpy()
    k = min(3000, n)
    idx = np.random.default_rng(42).choice(n, size=k, replace=False)
    fig, ax = plt.subplots(figsize=(5.0, 4.9))
    ax.scatter(x[idx], y[idx], s=5, alpha=0.4, color=BLUE, edgecolors="none",
               label=f"Random sample of {k:,} of {n:,} contracts (seed 42)")
    ax.plot([1, n], [1, n], "k--", linewidth=0.8, label="Equal ranks")
    inter = (same.get("inter_method") or {}).get("endorserank_vs_awp") or {}
    title = (rf"Kendall $\tau_b$ on all contracts = {inter['kendall_tau']:.3f} "
             f"[{inter['ci_low']:.3f}, {inter['ci_high']:.3f}]") if inter else None
    z_er, z_awp = int((er == 0).sum()), int((awp == 0).sum())
    if z_er:
        xz = float(x[(er == 0).to_numpy()][0])
        ax.text(xz - 300, n * 0.32, f"{z_er:,} contracts\nscore zero under\nEndorseRank (tied)", fontsize=8,
                ha="right", va="center", bbox={"facecolor": "white", "alpha": 0.8, "edgecolor": "none", "pad": 1})
    if z_awp:
        yz = float(y[(awp == 0).to_numpy()][0])
        ax.text(n * 0.03, yz - 500, f"{z_awp:,} contracts score zero under AWP (tied)", fontsize=8, va="top",
                bbox={"facecolor": "white", "alpha": 0.8, "edgecolor": "none", "pad": 1})
    ax.set_xlabel("EndorseRank rank (1 = highest; ties share the mid-rank)")
    ax.set_ylabel("AWP rank (1 = highest; ties share the mid-rank)")
    ax.set_xlim(-300, n + 300)
    ax.set_ylim(-300, n + 300)
    thousands = mticker.FuncFormatter(lambda v, _: f"{int(v):,}")
    ax.xaxis.set_major_formatter(thousands)
    ax.yaxis.set_major_formatter(thousands)
    ax.set_aspect("equal", adjustable="box")
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.01), frameon=False, title=title, title_fontsize=8.5)
    _save(fig, "rank-scatter.pdf")


def fig_damping(same: dict) -> None:
    plt = _style()
    dmp = same.get("damping") or {}
    ds = sorted({float(v["damping"]) for v in dmp.values()})
    if not ds:
        SKIPPED.append("damping-sensitivity.pdf (no damping sweep)")
        return
    fig, ax = plt.subplots(figsize=(5.6, 3.6))
    styles = {"transfer": ("o", "-"), "allowance": ("s", "--"), "sybil_stability": ("^", ":")}
    words = {"transfer": "transfer", "allowance": "allowance", "sybil_stability": "Sybil stability"}
    for m, name, color, off in (("endorserank", "EndorseRank", BLUE, -0.003), ("awp", "AWP", RED, 0.003)):
        for f, (marker, ls) in styles.items():
            rows = [dmp[f"{m}_d{int(round(d * 100))}"][f] for d in ds]
            mu = np.array([r["mean_tau"] for r in rows])
            err = np.array([[r["mean_tau"] - r["ci_low"] for r in rows], [r["ci_high"] - r["mean_tau"] for r in rows]])
            ax.errorbar(np.array(ds) + off, mu, yerr=err, marker=marker, linestyle=ls, color=color, capsize=2.5,
                        markersize=4.5, linewidth=1.2, label=f"{name}, {words[f]}")
    ax.set_xticks(ds)
    ax.set_xticklabels([f"{d:.2f}" for d in ds])
    ax.set_xlabel("PageRank damping factor $d$")
    ax.set_ylabel(r"Family-mean Kendall $\tau$")
    ax.legend(frameon=False, ncol=2, loc="lower center", bbox_to_anchor=(0.5, 1.01))
    _save(fig, "damping-sensitivity.pdf")


def _short_count(e: float) -> str:
    if e >= 1e6:
        return f"{e / 1e6:.1f}M"
    if e >= 1e3:
        return f"{e / 1e3:.0f}k"
    return f"{e:.0f}"


def fig_runtime_scaling(bench: dict) -> None:
    plt = _style()
    stages = bench.get("scaling") or []
    if not stages:
        SKIPPED.append("runtime-scaling.pdf (no stages)")
        return
    n = np.array([s["n"] for s in stages], dtype=float)
    fig, ax = plt.subplots(figsize=(5.8, 3.8))
    for m, name, color, marker, dy in (("endorserank", "EndorseRank", BLUE, "o", -11), ("awp", "AWP", RED, "s", 7)):
        t = np.array([s[m]["mean_s"] for s in stages])
        sd = np.array([s[m]["sd_s"] for s in stages])
        ax.errorbar(n, t, yerr=sd, marker=marker, color=color, capsize=2.5, linewidth=1.2, markersize=4.5,
                    label=f"{name} (labels: edges $|E|$ of its graph)")
        for xi, ti, s in zip(n, t, stages):
            ax.annotate(_short_count(float(s[m]["edges"])), (xi, ti), textcoords="offset points", xytext=(0, dy),
                        ha="center", fontsize=7.5, color=color)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.margins(x=0.06, y=0.15)
    ax.set_xticks(n)
    ax.set_xticklabels([f"{int(v):,}" for v in n], rotation=30, ha="right")
    ax.minorticks_off()
    ax.set_xlabel("Contracts in the stage $n$ (log scale)")
    ax.set_ylabel("Runtime per solver call (s, log scale)")
    ax.legend(frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.01), ncol=1)
    _save(fig, "runtime-scaling.pdf")


# --------------------------------------------------------------------------- main


def _load(key: str, override: Path | None = None) -> dict | None:
    p = override or SOURCES[key]
    if override:
        SOURCES[key] = override
    return load_json(p) if p.exists() else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tables-dir", type=Path, help="output folder for the .tex tables")
    ap.add_argument("--figures-dir", type=Path, help="output folder for the .pdf figures")
    ap.add_argument("--benchmark", type=Path, help="benchmark.json to use instead of the default")
    ap.add_argument("--robustness", type=Path, help="robustness.json to use instead of the default")
    ap.add_argument("--no-figures", action="store_true")
    ap.add_argument("-v", "--verbose", action="store_true", help="also list the outputs skipped for missing inputs")
    args = ap.parse_args()
    if args.tables_dir:
        OUT["tables"] = args.tables_dir
    if args.figures_dir:
        OUT["figures"] = args.figures_dir
    OUT["tables"].mkdir(parents=True, exist_ok=True)
    OUT["figures"].mkdir(parents=True, exist_ok=True)

    cfg = load_config()
    seed = int(cfg["alignment"]["bootstrap_seed"])
    same, w0, w1 = _load("same"), _load("w0"), _load("w1")
    rob, bench = _load("rob", args.robustness), _load("bench", args.benchmark)
    supp = _load("supp")
    n = int(same["cohort"]) if same else None

    if bench and n:
        t_benchmark_runtime(bench, n)
        t_benchmark_scaling(bench, n, cfg)
        t_benchmark_runs(bench, n, cfg)
    else:
        SKIPPED.append("benchmark-runtime, benchmark-scaling, benchmark-runs (no benchmark.json)")
    if same:
        t_alignment_hybrid(same, seed)
        t_tau_diff_hybrid(same, seed)
        t_tau_diff(same, seed)
        t_tie_sensitivity(same, seed)
        for fam in FAMILY_TABLES:
            t_alignment_family(same, seed, fam)
        t_alignment_family_ci(same, seed)
        t_robustness_damping(same, bench, seed, cfg)
    else:
        SKIPPED.append("same-window tables (no same-window summary)")
    if rob and n:
        if REVISED:
            t_robustness_slope(rob, n, load_json(USD_INPUTS / "constants.json"))
        else:
            t_robustness_tokens(rob, n, cfg)
        t_robustness_sample_size(rob, bench, n, cfg)
    else:
        SKIPPED.append("robustness-tokens, robustness-sample-size (no robustness.json)")
    if same and w0 and w1:
        t_endorserank_restarts(same, w0, w1, seed, cfg)
    else:
        SKIPPED.append("endorserank-restarts (needs the same-window, W0 and W1 summaries)")
    if w0:
        t_holdout_spenders(w0, seed, cfg)
        t_holdout_diff(w0, seed)
        t_holdout_receiving(w0, seed)
        t_holdout_traders(w0, seed, cfg)
        t_endorserank_awp_holdout(w0, w1, supp, seed, cfg)
    else:
        SKIPPED.append("W0 tables (no holdout summary)")
    if w1:
        t_fresh_holdout(w1, seed, cfg)
        t_fresh_contrasts(w1, seed)
        t_fresh_posthoc(w1, supp, seed, cfg)
        t_fresh_traders(w1, seed, cfg)
        t_neutral_contrasts(w1, seed, cfg)
        t_neutral_recipients(w1, seed, cfg)
        t_neutral_grid(w1, seed, cfg)
    else:
        SKIPPED.append("W1 tables (no registered summary)")
    if REVISED and (PROC / "describe" / "describe.json").exists():
        t_usd_tokens(load_json(PROC / "describe" / "describe.json"), cfg)
    if REVISED and same and w0 and w1:
        reg = {k: load_json(PROC_SHARED / d / "eval_summary.json")
               for k, d in (("same", "same-window"), ("w0", "holdout-w0"), ("w1", "registered-w1"))}
        t_registered_vs_revised(reg, {"same": same, "w0": w0, "w1": w1}, seed)

    if not args.no_figures:
        STATE["name"] = "figures"
        fig_logistic_decay(cfg)
        if same:
            try:
                scores = read_parts(COHORT_SCORES, columns=["endorserank", "awp"])
            except FileNotFoundError:
                scores = None
                SKIPPED.append("score-distributions.pdf, rank-scatter.pdf (no cohort score parts)")
            if scores is not None:
                if len(scores) != n:
                    problem(f"cohort score parts have {len(scores)} rows, the summary {n}")
                fig_score_distributions(scores, same)
                fig_rank_scatter(scores, same)
            fig_damping(same)
        if bench:
            fig_runtime_scaling(bench)
        else:
            SKIPPED.append("runtime-scaling.pdf (no benchmark.json)")

    for p in WRITTEN:
        print("wrote", p)
    if args.verbose and SKIPPED:
        print("skipped:", "; ".join(SKIPPED))
    if PROBLEMS:
        print(f"{len(PROBLEMS)} problem(s):")
        for msg in PROBLEMS:
            print("  -", msg)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
