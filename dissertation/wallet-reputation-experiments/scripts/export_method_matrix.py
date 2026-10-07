#!/usr/bin/env python3
"""Export method-proxy matrix to CSV and LaTeX (three-method or archived presets)."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import load_config, load_json  # noqa: E402
from evaluate_alignment import (  # noqa: E402
    DISSERTATION_METHODS,
    METHOD_LABELS,
    PROXY_FAMILIES,
    SEVEN_METHODS,
    SIX_AAVE_LABELS,
    SIX_AAVE_METHODS,
)  # noqa: E402
from project_paths import ARCHIVE_DIR, EN_LEFTOVER_DIR  # noqa: E402

METHODS = SEVEN_METHODS

FAMILY_HEADERS = {
    "transfer": "Transfer",
    "allowance": "Allowance",
    "liquidation": "Liq.",
    "inverse_risk": "Inv.risk",
    "sybil_stability": "Sybil",
    "gmx_success": "GMX",
}

PRESETS = {
    "three": {
        "methods": DISSERTATION_METHODS,
        "labels": METHOD_LABELS,
        "matrix_key": "method_proxy_matrix",
        "benchmark_prefix": None,
        "csv_name": "three_method_proxy_matrix.csv",
        "tex_name": "alignment-three-methods.tex",
        "label": "tab:alignment-three-methods",
        "caption_extra": (
            " EndorseRank and AWP are social reputation graphs; GF-PR is an "
            "outcome-native GMX PnL star baseline (construct overlap on GMX proxies)."
        ),
    },
    "seven": {
        "methods": METHODS,
        "labels": METHOD_LABELS,
        "matrix_key": "method_proxy_matrix",
        "benchmark_prefix": None,
        "csv_name": "method_proxy_matrix.csv",
        "tex_name": "alignment-seven-methods.tex",
        "label": "tab:alignment-seven-methods",
        "caption_extra": "",
    },
    "six-aave": {
        "methods": SIX_AAVE_METHODS,
        "labels": SIX_AAVE_LABELS,
        "matrix_key": "six_aave_method_proxy_matrix",
        "benchmark_prefix": "six_aave",
        "csv_name": "six_aave_method_proxy_matrix.csv",
        "tex_name": "alignment-six-aave-methods.tex",
        "label": "tab:alignment-six-aave-methods",
        "caption_extra": (
            " Aave W\\textrightarrow W edges: LiqCall (liquidator$\\rightarrow$user), "
            "Borrow (initiator$\\rightarrow$onBehalfOf), Repay (repayer$\\rightarrow$user), "
            "Delegation (delegator$\\rightarrow$delegatee). "
            "Credit Delegation BQ extract deferred when parquet absent---$\\tau$ may be degenerate."
        ),
    },
}


def _fmt(v: float | None, digits: int = 3) -> str:
    if v is None:
        return "---"
    return f"{v:.{digits}f}"


def _method_runtime_sec(summary: dict, method_id: str, benchmark_prefix: str | None) -> float | None:
    bench = summary.get("benchmark", {})
    if benchmark_prefix and isinstance(bench.get(benchmark_prefix), dict):
        entry = bench[benchmark_prefix].get(method_id)
    else:
        entry = bench.get(method_id)
    if not isinstance(entry, dict):
        return None
    val = entry.get("runtime_sec_mean")
    return float(val) if val is not None else None


def write_csv(matrix: dict, out: Path, summary: dict, preset_cfg: dict) -> None:
    families = list(PROXY_FAMILIES.keys())
    methods = preset_cfg["methods"]
    headers = ["method"] + families + ["runtime_sec"]
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for method_id in methods:
            row = matrix.get(method_id, {})
            rt = _method_runtime_sec(summary, method_id, preset_cfg["benchmark_prefix"])
            writer.writerow(
                [method_id]
                + [row.get(fam) if row.get(fam) is not None else "" for fam in families]
                + [rt if rt is not None else ""]
            )


def write_latex(summary: dict, out: Path, preset_cfg: dict) -> None:
    matrix = summary.get(preset_cfg["matrix_key"]) or summary.get("alignment", {}).get(
        preset_cfg["matrix_key"]
    )
    if not matrix:
        matrix = summary.get("alignment", {}).get("method_proxy_matrix", {})
    n = summary.get("n_wallets", "---")
    synthetic = summary.get("synthetic", False)
    diagnostics = summary.get("aave_edge_diagnostics", {})
    edge_note = ""
    if preset_cfg.get("tex_name") == "alignment-seven-methods.tex" and diagnostics:
        parts = []
        for key in ("liq_pr", "borrow_pr", "repay_pr", "borrow_pr_pool", "repay_pr_pool", "delegation_pr"):
            if key in diagnostics:
                parts.append(f"{key}={diagnostics[key].get('edge_count', 0)}")
        if parts:
            edge_note = " Edge counts: " + ", ".join(parts) + "."
    elif preset_cfg.get("tex_name") == "alignment-six-aave-methods.tex" and diagnostics:
        parts = []
        for key in ("liq_pr", "borrow_pr", "repay_pr", "borrow_pr_pool", "repay_pr_pool", "delegation_pr"):
            if key in diagnostics:
                parts.append(f"\\texttt{{{key}={diagnostics[key].get('edge_count', 0)}}}")
        if parts:
            edge_note = " Edge counts: " + ", ".join(parts) + "."

    if synthetic:
        hdr = r"""% Synthetic fixtures -- regenerate with:
%   run_dissertation_eval.py --fixtures --export-latex
"""
    else:
        hdr = r"""% Real BigQuery data -- regenerate with:
%   run_dissertation_eval.py --real --export-latex
"""

    families = list(PROXY_FAMILIES.keys())
    col_headers = " & ".join(FAMILY_HEADERS[f] for f in families)
    methods = preset_cfg["methods"]
    labels = preset_cfg["labels"]

    col_max: dict[str, float | None] = {}
    for fam in families:
        vals = [
            matrix.get(m, {}).get(fam)
            for m in methods
            if matrix.get(m, {}).get(fam) is not None
        ]
        col_max[fam] = max(vals) if vals else None

    rows = []
    for method_id in methods:
        label = labels.get(method_id, method_id)
        cells = []
        row = matrix.get(method_id, {})
        for fam in families:
            tau = row.get(fam)
            cell = _fmt(tau)
            if tau is not None and col_max.get(fam) is not None and abs(tau - col_max[fam]) < 1e-9:
                cell = f"\\textbf{{{cell}}}"
            cells.append(cell)
        rt = _method_runtime_sec(summary, method_id, preset_cfg["benchmark_prefix"])
        rt_cell = _fmt(rt, 3) if rt is not None else "---"
        rows.append(f"{label} & {' & '.join(cells)} & {rt_cell} \\\\")

    method_count = len(methods)
    repeats = (
        summary.get("timing_protocol", {}).get("timed_repeats")
        or summary.get("benchmark", {}).get("endorserank", {}).get("repeats")
        or 5
    )
    tabular = f"""\\begin{{tabular}}{{l{'c' * len(families)}r}}
\\toprule
Method & {col_headers} & Runtime (s) \\\\
\\midrule
{chr(10).join(rows)}
\\bottomrule
\\end{{tabular}}"""
    body = f"""{hdr}
\\begin{{table}}[htbp]
\\centering
\\caption{{Mean Kendall $\\tau$ by proxy family across {method_count} PageRank methods ($n={n}$). Bold = column maximum. Runtime = mean PageRank wall time (s, {repeats} timed repeats after one warm-up).{preset_cfg['caption_extra']}{edge_note}}}
\\label{{{preset_cfg['label']}}}
\\fitwidth{{%
{tabular}
}}
\\end{{table}}
"""
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(body, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path, help="eval_summary.json path")
    parser.add_argument(
        "--preset",
        choices=list(PRESETS.keys()),
        default="three",
        help="Matrix preset (default: three)",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        help="LaTeX tables output directory (default: dissertation results/tables for three)",
    )
    parser.add_argument(
        "--csv-out-dir",
        type=Path,
        help="CSV output directory (default: data/4-archived-extended-baselines)",
    )
    args = parser.parse_args()

    preset_cfg = PRESETS[args.preset]
    config = load_config()
    summary_path = args.summary or Path(config["paths"]["eval_summary"])
    if not summary_path.exists():
        print(f"Missing {summary_path}; run run_dissertation_eval.py first.")
        return 1

    summary = load_json(summary_path)
    matrix = summary.get(preset_cfg["matrix_key"])
    if not matrix:
        alignment = summary.get("alignment", {})
        matrix = alignment.get(preset_cfg["matrix_key"]) or alignment.get("method_proxy_matrix")
    if not matrix:
        print(f"Missing {preset_cfg['matrix_key']} in eval summary.")
        return 1

    # All matrix presets (including the former three-method table with GF-PR) are
    # archived: the main text reports EndorseRank vs AWP only, via
    # export_latex_results.py (alignment-family-ci.tex). GF-PR was withdrawn from
    # the narrative as circular with the GMX proxies (supervisor comment id 14).
    if args.csv_out_dir:
        csv_dir = args.csv_out_dir
    else:
        csv_dir = ARCHIVE_DIR
    csv_path = csv_dir / preset_cfg["csv_name"]
    write_csv(matrix, csv_path, summary, preset_cfg)

    if args.out_dir:
        tex_path = args.out_dir / preset_cfg["tex_name"]
    else:
        tex_path = EN_LEFTOVER_DIR / "archive" / "extended-baselines" / "tables" / preset_cfg["tex_name"]
    write_latex(summary, tex_path, preset_cfg)

    print(f"CSV  -> {csv_path}")
    print(f"LaTeX -> {tex_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
