#!/usr/bin/env python3
"""Korean-label versions of the five data figures of the thesis.

The figures are drawn by the figure functions of experiments/scripts/export_latex.py
itself (fig_logistic_decay, fig_score_distributions, fig_rank_scatter, fig_damping,
fig_runtime_scaling), from the same evaluation summaries and cohort score parts, so
the data, the computation, the axis ranges and the scales are those of the English
figures. Only two things change: the font (a Korean font, math stays in mathtext)
and the visible text (titles, axis labels, legends, annotations), which is replaced
just before each figure is saved. Every English text needs a Korean pattern in
KO_TEXT; one without fails the run, as does a glyph missing from the font.

Output: overleaf-github-ko/Figures/generated/<same file names>.pdf

The thesis figures are those of the revised analysis (CONTRACT_REP_VARIANT=usd), the
default here; --variant registered (or the environment variable) selects the other.

usage: python scripts/make_ko_figures.py [--variant usd] [--font NanumMyeongjo]
       [--experiments ../../experiments] [--figures-dir DIR] [--benchmark FILE]
"""

from __future__ import annotations

import argparse
import logging
import os
import re
import sys
import warnings
from pathlib import Path

HERE = Path(__file__).resolve().parent
KO_ROOT = HERE.parent  # dissertation/overleaf-github-ko
EXPERIMENTS = KO_ROOT.parents[1] / "experiments"
FIGURES = ("logistic-decay.pdf", "score-distributions.pdf", "rank-scatter.pdf",
           "damping-sensitivity.pdf", "runtime-scaling.pdf")

# NanumMyeongjo matches the Hangul body font of the Korean thesis (Config/preamble.tex);
# Malgun Gothic ships with Windows.
FONT_CANDIDATES = ("NanumMyeongjo", "NanumGothic", "Malgun Gothic")
FONT_FILE_PREFIXES = ("nanummyeongjo", "nanumgothic", "malgun")

# export_latex.py calls fig.tight_layout() on these before saving: redone for the Korean text.
TIGHT_LAYOUT = {"score-distributions.pdf"}

N = r"([\d,]+)"  # a count printed with thousands separators
FAMILY_KO = {"transfer": "송금", "allowance": "허락", "Sybil stability": "시빌 안정성"}

# (English text as export_latex.py writes it, Korean replacement). Terms follow
# TRANSLATION-GUIDE.md section 5; method names stay in English inside figures. Ranges
# use the Korean "0~913일" (an en dash in NanumMyeongjo reads like a minus sign).
KO_TEXT: list[tuple[str, object]] = [
    # logistic-decay.pdf
    (rf"Ages at the observation anchor \(0–{N} days\)", "관측 기준 시점에서의 나이(0~\\1일)"),
    (r"Decay weight, (\$k=[^$]+\$), (\$t_0=[^$]+\$) days", r"시간 감쇠 무게, \1, \2일"),
    (r"(\$t_0=[^$]+\$) days", r"\1일"),
    (rf"Ages at the W0 freeze \(0–{N} days\)", "W0 동결 시점에서의 나이(0~\\1일)"),
    (r"Age of the event at the anchor \(days\)", "기준 시점에서 본 이벤트의 나이(일)"),
    (r"Time-decay weight", "시간 감쇠 무게"),
    # score-distributions.pdf
    (rf"(EndorseRank|AWP): {N} positive scores\n{N} contracts score zero \(not shown\)",
     r"\1" "\n" r"0보다 큰 점수 \2개" "\n" r"0점인 계약 \3개(그리지 않음)"),
    (r"Score \(\$\\log_\{10\}\$\)", r"점수($\\log_{10}$)"),
    (rf"{N} contracts share the score\nof a node without in-edges",
     r"계약 \1개가" "\n" r"들어오는 화살표가 없는" "\n" r"점의 점수를 똑같이 받음"),
    (r"Contracts \(log scale\)", "계약 수(로그 눈금)"),
    # rank-scatter.pdf
    (rf"Random sample of {N} of {N} contracts \(seed (\d+)\)", r"계약 \2개 중 무작위로 뽑은 \1개(시드 \3)"),
    (r"Equal ranks", "두 순위가 같은 선"),
    (r"Kendall \$\\tau_b\$ on all contracts = (.+)", r"모든 계약에서 켄달의 $\\tau_b$ = \1"),
    (rf"{N} contracts\nscore zero under\nEndorseRank \(tied\)",
     r"EndorseRank에서" "\n" r"0점인 계약" "\n" r"\1개(동점)"),
    (rf"{N} contracts score zero under AWP \(tied\)", r"AWP에서 0점인 계약 \1개(동점)"),
    (r"(EndorseRank|AWP) rank \(1 = highest; ties share the mid-rank\)",
     r"\1 순위(1 = 가장 높음, 동점은 평균 순위)"),
    # damping-sensitivity.pdf
    (r"(EndorseRank|AWP), (transfer|allowance|Sybil stability)",
     lambda m: f"{m[1]}, {FAMILY_KO[m[2]]}"),
    (r"PageRank damping factor \$d\$", "페이지랭크 감쇠 계수 $d$"),
    (r"Family-mean Kendall \$\\tau\$", r"지표 가족 평균 켄달의 $\\tau$"),
    # runtime-scaling.pdf
    (r"(EndorseRank|AWP) \(labels: edges \$\|E\|\$ of its graph\)", r"\1(점 옆 숫자: 그 그래프의 화살표 수 $|E|$)"),
    (r"Contracts in the stage \$n\$ \(log scale\)", "단계에 든 계약 수 $n$(로그 눈금)"),
    (r"Runtime per solver call \(s, log scale\)", "풀이 한 번에 걸린 시간(초, 로그 눈금)"),
]
KO_TEXT_RE = [(re.compile(p, re.DOTALL), r) for p, r in KO_TEXT]

STATE: dict = {"font": None, "out": None, "written": [], "problems": [], "translated": 0}


def problem(msg: str) -> None:
    if msg not in STATE["problems"]:
        STATE["problems"].append(msg)


def korean_font(requested: str | None) -> str:
    """Name of the first Korean font matplotlib can use, registering font files it has not cached."""
    from matplotlib import font_manager as fm

    wanted = (requested,) if requested else FONT_CANDIDATES

    def known() -> str | None:
        names = {f.name for f in fm.fontManager.ttflist}
        return next((w for w in wanted if w in names), None)

    name = known()
    if name is None:  # installed after matplotlib built its font cache
        for path in fm.findSystemFonts(fontext="ttf"):
            if Path(path).stem.lower().startswith(FONT_FILE_PREFIXES):
                try:
                    fm.fontManager.addfont(path)
                except (OSError, RuntimeError, ValueError):
                    pass
        name = known()
    if name is None:
        raise SystemExit(f"no Korean font found among {', '.join(wanted)}: install NanumMyeongjo "
                         "(or NanumGothic; Windows has Malgun Gothic), or pass --font with an installed font")
    return name


def needs_translation(s: str) -> bool:
    """True when English words remain outside math, method names and counts such as 1.3M or 423k."""
    s = re.sub(r"\$[^$]*\$", "", s)
    s = re.sub(r"\b(EndorseRank|AWP|C-PR|S-PR|W0|W1)\b", "", s)
    s = re.sub(r"\b\d[\d,.]*[kM]\b", "", s)
    return bool(re.search(r"[A-Za-z]", s))


def to_korean(s: str) -> str:
    for rx, repl in KO_TEXT_RE:
        if rx.fullmatch(s):
            STATE["translated"] += 1
            return rx.sub(repl, s, count=1)
    return s


def translate_figure(fig, name: str) -> None:
    from matplotlib.text import Text

    for t in fig.findobj(Text):
        s = t.get_text()
        if not s:
            continue
        ko = to_korean(s)
        if ko != s:
            t.set_text(ko)
        elif needs_translation(s):
            problem(f"{name}: no Korean text for {s!r} (add a pattern to KO_TEXT)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--variant", choices=("usd", "registered"),
                    default=os.environ.get("CONTRACT_REP_VARIANT", "usd"),
                    help="analysis to draw (default: CONTRACT_REP_VARIANT, else usd as in the thesis)")
    ap.add_argument("--font", help=f"Korean font family (default: first of {', '.join(FONT_CANDIDATES)})")
    ap.add_argument("--experiments", type=Path, default=EXPERIMENTS, help="experiments folder with scripts/export_latex.py")
    ap.add_argument("--figures-dir", type=Path, default=KO_ROOT / "Figures" / "generated", help="output folder")
    ap.add_argument("--benchmark", type=Path, help="benchmark.json to use instead of the default (as export_latex.py)")
    args = ap.parse_args()

    scripts = args.experiments.resolve() / "scripts"
    if not (scripts / "export_latex.py").exists():
        raise SystemExit(f"export_latex.py not found in {scripts}; pass --experiments")
    os.environ["CONTRACT_REP_VARIANT"] = args.variant  # read by common.py when it is imported
    sys.path.insert(0, str(scripts))
    import export_latex as E  # noqa: E402  (also puts scripts/ on sys.path for common.py)
    from common import load_config, read_parts  # noqa: E402

    STATE["font"] = korean_font(args.font)
    logging.getLogger("fontTools.subset").setLevel(logging.ERROR)  # "TSI0 NOT subset" notes of hinted fonts
    STATE["out"] = args.figures_dir
    STATE["out"].mkdir(parents=True, exist_ok=True)
    english_style = E._style

    def ko_style():
        plt = english_style()
        plt.rcParams.update({"font.family": [STATE["font"]], "axes.unicode_minus": False})
        return plt

    def ko_save(fig, name: str) -> None:
        import matplotlib.pyplot as plt

        translate_figure(fig, name)
        if name in TIGHT_LAYOUT:
            fig.tight_layout()
        path = STATE["out"] / name
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            fig.savefig(path)
        for w in caught:
            text = str(w.message)
            if "missing from" in text or "Glyph" in text:
                problem(f"{name}: {text}")
            else:
                warnings.warn_explicit(w.message, w.category, w.filename, w.lineno)
        plt.close(fig)
        STATE["written"].append(path)

    E._style, E._save = ko_style, ko_save  # the figure functions look both up in their module

    cfg = load_config()
    same = E._load("same")
    bench = E._load("bench", args.benchmark)
    E.fig_logistic_decay(cfg)
    if same:
        scores = read_parts(E.COHORT_SCORES, columns=["endorserank", "awp"])
        if len(scores) != int(same["cohort"]):
            problem(f"cohort score parts have {len(scores)} rows, the summary {same['cohort']}")
        E.fig_score_distributions(scores, same)
        E.fig_rank_scatter(scores, same)
        E.fig_damping(same)
    if bench:
        E.fig_runtime_scaling(bench)

    written = {p.name for p in STATE["written"]}
    for name in FIGURES:
        if name not in written:
            problem(f"{name} not written (missing input; export_latex.py skipped: {'; '.join(E.SKIPPED) or '-'})")
    print(f"variant {args.variant}, font {STATE['font']}, {STATE['translated']} texts translated")
    for p in STATE["written"]:
        print("wrote", p)
    if STATE["problems"]:
        print(f"{len(STATE['problems'])} problem(s):")
        for msg in STATE["problems"]:
            print("  -", msg)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
