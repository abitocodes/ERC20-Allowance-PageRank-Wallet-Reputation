#!/usr/bin/env python3
"""Korean-label versions of the seven data figures of the thesis.

The figures are drawn by the figure functions of the experiments scripts themselves,
from the same evaluation summaries, cohort score parts and discovery runs, so the data,
the computation, the axis ranges and the scales are those of the English figures. For
the contract-graph analysis (CONTRACT_REP_VARIANT=contract12m) these are, as in
experiments/scripts/export_latex_c12.py: fig_logistic_decay, fig_score_distributions,
fig_rank_scatter and fig_damping of export_latex.py, and fig_runtime_scaling and
fig_discovery_curves (discovery-curves.pdf, discovery-curves-out.pdf) of
export_latex_c12.py. Only two things differ: the font and the visible text (titles,
axis labels, tick labels, legends, annotations), which is replaced just before each
figure is saved. Every English text needs a Korean pattern in KO_TEXT; one without fails
the run, as does a glyph missing from the fonts.

Fonts: Latin letters, digits and punctuation are set as in the English figures, text in
the Bahnschrift SemiCondensed face of export_latex._plot_face(), formulas in Palatino
through mathtext, panel titles in Palatino. Hangul in text is set in Noto Sans KR at
weight 400, Hangul in panel titles in Noto Serif KR at weight 400. matplotlib reads only
the default instance of a variable font, so both are cut as static weight-400 instances
from the installed variable fonts with fontTools, under their own family names (KO_SANS,
KO_SERIF), and kept in experiments/data/_work/fonts/ next to the Bahnschrift face (ignored
by git); Hangul gets no added letter spacing. matplotlib takes each glyph from the first
font in the list that has it: Latin from Bahnschrift, Hangul from Noto. Where Bahnschrift
or the Noto KR fonts are missing, the text is set in one Korean body font (NanumMyeongjo,
else Batang, ...) with STIXGeneral, and a note says so.

Output: overleaf-github-ko/Figures/generated/<same file names>.pdf

The thesis figures are those of the contract-graph analysis (CONTRACT_REP_VARIANT=
contract12m), the default here; --variant usd12m, usd or registered (or the environment
variable) selects an earlier analysis, which has only the first five figures (KO_TEXT
holds the texts of the contract-graph figures; a text of an earlier analysis that is
missing fails the run and names the pattern to add).

usage: python scripts/make_ko_figures.py [--variant contract12m] [--font "Noto Sans KR Plot"]
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
DISCOVERY_FIGURES = ("discovery-curves.pdf", "discovery-curves-out.pdf")  # contract12m only

# The Hangul faces of the figures: static weight-400 cuts of the installed Noto KR variable fonts
# (sans for text and labels, serif for panel titles), under their own family names so that they
# never mix with the installed variable fonts.
KO_SANS = "Noto Sans KR Plot"
KO_SERIF = "Noto Serif KR Plot"
KO_FACES = {KO_SANS: ("NotoSansKR-VF.ttf", "noto-sans-kr-plot-w400.ttf", "NotoSansKR-Plot"),
            KO_SERIF: ("NotoSerifKR-VF.ttf", "noto-serif-kr-plot-w400.ttf", "NotoSerifKR-Plot")}

# Where Bahnschrift or the Noto KR fonts are missing: the order of the Hangul body font of the
# Korean thesis (Config/preamble.tex), NanumMyeongjo, else Batang (ships with Windows), else Malgun Gothic.
FONT_CANDIDATES = ("NanumMyeongjo", "Batang", "NanumGothic", "Malgun Gothic")
FONT_FILE_PREFIXES = ("nanummyeongjo", "batang", "nanumgothic", "malgun")

# The figure functions call fig.tight_layout() on these before saving: redone for the Korean text.
TIGHT_LAYOUT = {"score-distributions.pdf", *DISCOVERY_FIGURES}

N = r"([\d,]+)"  # a count printed with thousands separators
FAMILY_KO = {"transfer": "송금", "allowance": "허락", "stability": "안정성",  # contract-graph analysis
             "Sybil stability": "시빌 안정성"}  # earlier analyses

# (English text as export_latex.py writes it, Korean replacement). Terms follow
# TRANSLATION-GUIDE.md section 5; method names stay in English inside figures. Ranges
# use the Korean "0~913일" (an en dash between numbers reads like a minus sign).
KO_TEXT: list[tuple[str, object]] = [
    # logistic-decay.pdf
    (rf"Ages at both freezes \(0–{N} days\)", "두 동결 시점에서의 나이(0~\\1일)"),
    (r"Decay weight, (\$k=[^$]+\$), (\$t_0=[^$]+\$) days", r"시간 감쇠 무게, \1, \2일"),
    (r"(\$t_0=[^$]+\$) days", r"\1일"),
    (r"Age of the event at the anchor \(days\)", "기준 시점에서 본 이벤트의 나이(일)"),
    (r"Time-decay weight", "시간 감쇠 무게"),
    # score-distributions.pdf
    (rf"(EndorseRank|AWP): {N} positive scores\n{N} contracts score zero \(not shown\)",
     r"\1" "\n" r"0보다 큰 점수 \2개" "\n" r"0점인 계약 \3개(그리지 않음)"),
    (r"Score \((\$(?:\\log_\{10\}|\\mathregular\{log_\{10\}\})\$)\)", r"점수(\1)"),
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
    (r"(EndorseRank|AWP), (transfer|allowance|Sybil stability|stability)",
     lambda m: f"{m[1]}, {FAMILY_KO[m[2]]}"),
    (r"PageRank damping factor \$d\$", "페이지랭크 감쇠 계수 $d$"),
    (r"Family-mean Kendall \$\\tau\$", r"지표 가족 평균 켄달의 $\\tau$"),
    # runtime-scaling.pdf
    (r"(EndorseRank|AWP) \(labels: edges \$\|E\|\$ of its graph\)", r"\1(점 옆 숫자: 그 그래프의 화살표 수 $|E|$)"),
    (r"(?:Contracts in the subsample \$n\$|Subsample size \$n\$ \(contracts\)); open markers: the whole contract graph",
     "부분 표본에 든 계약 수 $n$, 속이 빈 표시: 계약 그래프 전체"),
    (r"whole\ngraph", "그래프\n전체"),
    (r"Runtime per solver call \(s, log scale\)", "풀이 한 번에 걸린 시간(초, 로그 눈금)"),
    # discovery-curves.pdf, discovery-curves-out.pdf
    (r"(\$H_q\(I_T\)\$): user-account inflow", r"\1: 사용자 계정 유입"),
    (r"(\$H_q\(I_A\)\$): user-authorized value", r"\1: 사용자 허락 금액"),
    (r"Contracts visited \(% of the universe\)", "방문한 계약(우주의 %)"),
    (r"Share of the hot contracts visited (\(\$P_\{ST\}\$\))", r"방문한 뜨거운 계약의 몫\1"),
    (r"BFS", "너비 우선(BFS)"),
    (r"Random reference", "무작위 기준"),
    (r"Random", "무작위"),
    (r"(IB\$'_U\$|IB\$\^\{\\prime\}_\{U\}\$) \(contract backlinks\)", r"\1(계약 역링크)"),
    (r"Ideal", "이상적인 순서"),
]
KO_TEXT_RE = [(re.compile(p, re.DOTALL), r) for p, r in KO_TEXT]

STATE: dict = {"font": None, "out": None, "written": [], "problems": [], "translated": 0, "used": set()}


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
                         "(Windows has Batang and Malgun Gothic), or pass --font with an installed font")
    return name


def ko_face(family: str, font_work: Path) -> str | None:
    """Family name of a static weight-400 cut of a Noto KR variable font, or None where it is not installed.

    The cut is made with fontTools.varLib.instancer from the font in the Windows font folder (or wherever
    matplotlib finds it), named `family`, kept in `font_work` (data/_work/fonts/, ignored by git) and
    registered with matplotlib. Its advances stay as they are: Hangul gets no added letter spacing.
    """
    from matplotlib import font_manager as fm

    src_name, out_name, ps_name = KO_FACES[family]
    windir = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
    src = next((p for p in [windir / src_name, *map(Path, fm.findSystemFonts(fontext="ttf"))]
                if p.name.lower() == src_name.lower() and p.exists()), None)
    if src is None:
        return None
    out = font_work / out_name
    if not out.exists() or out.stat().st_mtime < src.stat().st_mtime:
        from fontTools.ttLib import TTFont
        from fontTools.varLib import instancer

        font = instancer.instantiateVariableFont(TTFont(src), {"wght": 400})
        for tag in ("hdmx", "LTSH", "VDMX"):  # per-glyph caches of the default (thin) instance
            if tag in font:
                del font[tag]
        names = font["name"]
        names.names = [r for r in names.names if r.nameID not in (1, 2, 3, 4, 6, 16, 17, 21, 22, 25)]
        for nid, text in ((1, family), (2, "Regular"), (3, ps_name), (4, family), (6, ps_name)):
            names.setName(text, nid, 3, 1, 0x409)
        font["OS/2"].usWeightClass = 400
        font_work.mkdir(parents=True, exist_ok=True)
        font.save(out)
    fm.fontManager.addfont(str(out))
    return family


def is_hangul(ch: str) -> bool:
    o = ord(ch)
    return 0x1100 <= o <= 0x11FF or 0x3130 <= o <= 0x318F or 0xA960 <= o <= 0xA97F or 0xAC00 <= o <= 0xD7FF


def mathtext_hangul(sans: Path, serif: Path | None) -> None:
    """Let mathtext take Hangul from the Noto KR cuts.

    A text with a formula ("페이지랭크 감쇠 계수 $d$") is laid out by mathtext as a whole, and mathtext sets the
    words outside the formula in one font, the first of the text's font list (Bahnschrift), without the per-glyph
    fallback of plain text. Its Hangul is taken from the Noto Sans KR cut instead, or from the Noto Serif KR cut
    when the text is set in the serif list of a panel title.
    """
    from matplotlib import _mathtext as M
    from matplotlib.font_manager import get_font

    original = M.UnicodeFonts._get_glyph

    def _get_glyph(self, fontname, font_class, sym):
        if len(sym) == 1 and is_hangul(sym):
            families = self.default_font_prop.get_family()
            path = serif if serif is not None and KO_SERIF in families else sans
            return get_font(str(path)), ord(sym), False
        return original(self, fontname, font_class, sym)

    M.UnicodeFonts._get_glyph = _get_glyph


class MissingGlyphLog(logging.Handler):
    """Counts mathtext's "does not have a glyph" warnings as problems of the figure being saved."""

    def emit(self, record: logging.LogRecord) -> None:
        msg = record.getMessage()
        if "does not have a glyph" in msg:
            problem(f"{STATE.get('current') or '?'}: {msg}")


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
            STATE["used"].add(rx.pattern)
            return rx.sub(repl, s, count=1)
    return s


def translate_figure(fig, name: str) -> None:
    from matplotlib.text import Text
    from matplotlib.ticker import FixedFormatter, FuncFormatter

    # Tick labels set with set_xticklabels are redrawn from their formatter when the figure is saved.
    for ax in fig.axes:
        for axis in (ax.xaxis, ax.yaxis):
            fmt = axis.get_major_formatter()
            if isinstance(fmt, (FixedFormatter, FuncFormatter)):
                axis.set_major_formatter(FuncFormatter(lambda v, pos, f=fmt: to_korean(f(v, pos))))
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
    ap.add_argument("--variant", choices=("contract12m", "usd12m", "usd", "registered"),
                    default=os.environ.get("CONTRACT_REP_VARIANT", "contract12m"),
                    help="analysis to draw (default: CONTRACT_REP_VARIANT, else contract12m as in the thesis)")
    ap.add_argument("--font", help=f"font family of the Hangul in text (default: {KO_SANS}, cut from the installed "
                                   f"Noto Sans KR; where it is missing, the first of {', '.join(FONT_CANDIDATES)})")
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

    # "TSI0 NOT subset" notes of hinted fonts, "Table version value is a float" of Batang
    logging.getLogger("fontTools").setLevel(logging.ERROR)
    contract_graph = args.variant == "contract12m"
    # The faces of the English figures (Bahnschrift SemiCondensed for text) and the Noto KR cuts for Hangul;
    # the earlier analyses keep the single Korean body font they were drawn with.
    latin = E._plot_face() if contract_graph else None
    if args.font in (None, KO_SANS):
        hangul = ko_face(KO_SANS, E.FONT_WORK)
    else:
        hangul = korean_font(args.font)
    serif = ko_face(KO_SERIF, E.FONT_WORK) if latin and hangul else None
    STATE["mixed"] = bool(latin and hangul)
    logging.getLogger("matplotlib.mathtext").addHandler(MissingGlyphLog())
    if STATE["mixed"]:
        STATE["font"] = hangul
        from matplotlib import font_manager as fm

        def path_of(family: str) -> Path:
            return Path(fm.findfont(fm.FontProperties(family=family), fallback_to_default=False))

        mathtext_hangul(path_of(hangul), path_of(serif) if serif else None)
    else:
        if contract_graph:
            print("note: Bahnschrift or Noto Sans KR is not installed, so the text is set in one Korean body font "
                  "with STIXGeneral", file=sys.stderr)
        STATE["font"] = korean_font(None if args.font in (None, KO_SANS) else args.font)
    STATE["out"] = args.figures_dir
    STATE["out"].mkdir(parents=True, exist_ok=True)
    english_style = E._style
    english_title_kw = E.title_kw

    def ko_style():
        plt = english_style()
        if STATE["mixed"]:
            # Latin, digits and punctuation from Bahnschrift (which has the minus sign U+2212), Hangul from
            # Noto Sans KR, a glyph both lack from STIXGeneral; mathtext as in the English figures.
            plt.rcParams.update({"font.family": [latin, STATE["font"], "STIXGeneral"], "axes.unicode_minus": True})
        else:
            # STIXGeneral after the Korean font: glyphs the Korean font lacks (Malgun Gothic has no U+2212,
            # which the log-axis tick labels write in mathtext) come from the font of the English figures.
            plt.rcParams.update({"font.family": [STATE["font"], "STIXGeneral"], "axes.unicode_minus": False})
        return plt

    def ko_title_kw() -> dict:
        # Panel titles in Palatino as in the English figures; their Hangul from Noto Serif KR (else the Korean
        # text font), which comes after Palatino in the list.
        kw = english_title_kw()
        if kw:
            kw = {"fontfamily": [kw["fontfamily"], serif or STATE["font"]]}
        return kw

    def ko_save(fig, name: str) -> None:
        import matplotlib.pyplot as plt

        STATE["current"] = name
        translate_figure(fig, name)
        if name in DISCOVERY_FIGURES:
            # the legend row above the panels sits outside the axes: keep the top strip free, as the English figure
            fig.tight_layout(rect=(0, 0, 1, 0.92))
        elif name in TIGHT_LAYOUT:
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

    E._style, E._save, E.title_kw = ko_style, ko_save, ko_title_kw  # the figure functions look them up in E

    if contract_graph:
        import export_latex_c12 as C  # noqa: E402  (its figure functions call E._style and E._save)
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
        (C.fig_runtime_scaling if contract_graph else E.fig_runtime_scaling)(bench)
    expected = FIGURES
    if contract_graph:
        expected = FIGURES + DISCOVERY_FIGURES
        for (t, m), name in ((("tobs", "both"), DISCOVERY_FIGURES[0]), (("tobs", "out"), DISCOVERY_FIGURES[1])):
            src = C.SRC[f"disc_{t}_{m}"]
            if src.exists():
                C.fig_discovery_curves(C.load_json(src), name)
            else:
                problem(f"{name}: discovery run {src} not on disk")
    for msg in E.PROBLEMS:
        problem(f"export_latex: {msg}")

    written = {p.name for p in STATE["written"]}
    for name in expected:
        if name not in written:
            problem(f"{name} not written (missing input; export_latex.py skipped: {'; '.join(E.SKIPPED) or '-'})")
    fonts = f"{latin} + {STATE['font']}, titles + {serif or STATE['font']}" if STATE["mixed"] else STATE["font"]
    print(f"variant {args.variant}, fonts {fonts}, {STATE['translated']} texts translated")
    for p in STATE["written"]:
        print("wrote", p)
    unused = [p for p, _ in KO_TEXT if p not in STATE["used"]]
    if unused:  # patterns of texts this variant's figures do not write (e.g. another variant's band label)
        print("KO_TEXT patterns not used:", "; ".join(unused))
    if STATE["problems"]:
        print(f"{len(STATE['problems'])} problem(s):")
        for msg in STATE["problems"]:
            print("  -", msg)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
