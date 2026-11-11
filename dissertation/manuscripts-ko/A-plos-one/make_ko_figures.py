#!/usr/bin/env python3
"""Korean-label version of Fig 1 of manuscript A.

The figure is drawn by make_fig1.py of the English manuscript itself
(../../overleaf-github/manuscripts/A-plos-one/figures/make_fig1.py), from the same
published summaries, so the data, the computation and the axes are those of the English
figure. Two things change: the font (Hangul falls back to Malgun Gothic; Latin, digits
and the minus sign stay in the English face) and the visible text, which is replaced
just before the figure is saved. Every English text needs a Korean entry in KO_TEXT or a
pattern in KO_PATTERNS; one without fails the run, as does a missing glyph.

A text that mixes mathtext ($...$) and Hangul is set with Malgun Gothic as its first face,
because mathtext draws the plain part of such a string in the first face of its font list
only (the math part keeps the English face). Such a text must not hold the minus sign
U+2212, which Malgun Gothic lacks; the glyph check stops the run if one slips in.

Output: figures/fig1_ko.pdf next to this script.

usage: python -I -X utf8 make_ko_figures.py [--repo PATH]   (or set CONTRACT_REP_REPO;
       without either, the public repository that holds this folder is used)
"""
from __future__ import annotations

import importlib.util
import logging
import os
import re
import sys
import warnings
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]  # the public repository ERC20-Allowance-PageRank-Wallet-Reputation
EN_FIG = HERE.parents[1] / "overleaf-github" / "manuscripts" / "A-plos-one" / "figures" / "make_fig1.py"
OUT = HERE / "figures" / "fig1_ko.pdf"

KO_TEXT = {
    # legend of panels A and B
    "C-PR′ (coupled walk)": "C-PR′ (결합 걷기)",
    "IB′$_U$ (contract backlinks)": "IB′$_U$ (계약 역링크 수)",
    "AWP′ (transfer walk)": "AWP′ (송금 걷기)",
    "BFS (breadth-first)": "BFS (너비 우선)",
    "Random curve": "무작위 곡선",
    "Ideal order": "이상적인 순서",
    # axis labels
    "Contracts visited (% of the universe)": "방문한 계약 (우주의 %)",
    "Share of the hot contracts visited": "방문한 뜨거운 계약의 몫",
    "Δτ, walk minus the count it smooths (95% interval)": "Δτ, 걷기 − 그것이 다듬는 수 (95% 구간)",
    # rows of panel C (the subset rows are in KO_PATTERNS)
    "EndorseRank − in-approve degree\n(new approval pairs)": "EndorseRank − 받은 허락 수\n(새 허락 쌍)",
    "EndorseRank, activity restarts − in-approve degree\n(new approval pairs)":
        "EndorseRank, 활동 재시작 − 받은 허락 수\n(새 허락 쌍)",
    "AWP − transfer in-degree\n(new transfer senders)": "AWP − 송금 입차수\n(새 송금자)",
    # title of panel C (no minus sign: the string is set in Malgun Gothic)
    r"$\mathbf{C}$   Spender contracts: each walk minus the count it smooths, on the label of its own edge type":
        r"$\mathbf{C}$   스펜더 계약: 각 걷기에서 그것이 다듬는 수를 뺀 값, 자기 화살표 종류의 라벨에서",
    # legend of panel C
    "W1: freeze 30 Jun 2026, labels Jul–Sep 2026": "W1: 2026년 6월 30일 동결, 라벨 2026년 7–9월",
    "W0: freeze 31 Mar 2026, labels Apr–Jun 2026": "W0: 2026년 3월 31일 동결, 라벨 2026년 4–6월",
}
# texts that carry a number read from the summaries: (English pattern, Korean template)
KO_PATTERNS = [
    (re.compile(r"^\$\\mathbf\{A\}\$   Hot set of user-account inflow, \$I_T\$ \(n = ([\d,]+)\)$"),
     r"$\mathbf{{A}}$   사용자 계정 유입 $I_T$의 뜨거운 집합 (n = {0})"),
    (re.compile(r"^\$\\mathbf\{B\}\$   Hot set of user-authorized value, \$I_A\$ \(n = ([\d,]+)\)$"),
     r"$\mathbf{{B}}$   사용자 허락 금액 $I_A$의 뜨거운 집합 (n = {0})"),
    (re.compile(r"^EndorseRank − in-approve degree, among the ([\d,]+) W0\nspenders with a transfer from another contract$"),
     "EndorseRank − 받은 허락 수, 다른 계약이\n동결 전에 송금한 W0 스펜더 {0}개에서"),
    (re.compile(r"^AWP − transfer in-degree, among the ([\d,]+) W0\nspenders with a transfer from another contract$"),
     "AWP − 송금 입차수, 다른 계약이\n동결 전에 송금한 W0 스펜더 {0}개에서"),
]
NUMERIC = re.compile(r"^[\s\d.,−\-+%]*$")
HANGUL = re.compile(r"[가-힣]")
KOREAN_FACE = "Malgun Gothic"


class MissingGlyphs(logging.Handler):
    """Collects mathtext's 'does not have a glyph' messages, which are logged, not warned."""

    def __init__(self) -> None:
        super().__init__()
        self.messages: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        if "glyph" in record.getMessage():
            self.messages.append(record.getMessage())


def translate(fig, sans: str) -> None:
    """Puts Korean into every text of the figure; stops on a text without a Korean entry."""
    from matplotlib.text import Text
    from matplotlib.ticker import FixedFormatter, FuncFormatter
    missing: list[str] = []
    korean_values = set(KO_TEXT.values())

    def korean(s: str) -> str:
        if not s or NUMERIC.match(s) or s in korean_values or HANGUL.search(s):
            return s
        if s in KO_TEXT:
            return KO_TEXT[s]
        for pat, tmpl in KO_PATTERNS:
            m = pat.match(s)
            if m:
                return tmpl.format(*m.groups())
        missing.append(s)
        return s

    # Tick labels are redrawn from their formatter, so the formatter gets the Korean.
    done = set()
    for ax in fig.axes:
        for axis in (ax.xaxis, ax.yaxis):
            fmt = axis.get_major_formatter()
            if id(fmt) in done:
                continue
            done.add(id(fmt))
            if isinstance(fmt, FixedFormatter):
                fmt.seq = [korean(s) for s in fmt.seq]
            elif isinstance(fmt, FuncFormatter):  # what set_ticklabels makes in matplotlib 3.10
                for i, loc in enumerate(axis.get_majorticklocs()):
                    korean(fmt.func(loc, i))
                fmt.func = lambda x, pos, english=fmt.func: korean(english(x, pos))
    for t in fig.findobj(Text):
        s = korean(t.get_text())
        t.set_text(s)
        if "$" in s and HANGUL.search(s):
            t.set_fontfamily([KOREAN_FACE, sans])
    if missing:
        sys.exit("no Korean text for: " + " | ".join(sorted(set(map(repr, missing)))))


def main() -> None:
    if not any(a in sys.argv for a in ("--repo", "--phd-works")) and not (
            os.environ.get("CONTRACT_REP_REPO") or os.environ.get("PHD_WORKS")):
        os.environ["CONTRACT_REP_REPO"] = str(ROOT)
    spec = importlib.util.spec_from_file_location("make_fig1", EN_FIG)
    fig1 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fig1)

    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    # Latin, digits and the minus sign in the English face; Hangul falls back to Malgun Gothic
    # (matplotlib falls back glyph by glyph only through a list of named families)
    plt.rcParams["font.family"] = [fig1.SANS, KOREAN_FACE]
    glyphs = MissingGlyphs()
    logging.getLogger("matplotlib.mathtext").addHandler(glyphs)
    logging.getLogger("matplotlib._mathtext").addHandler(glyphs)

    def save_korean(self, *_args, **kwargs):
        translate(self, fig1.SANS)
        OUT.parent.mkdir(exist_ok=True)
        with warnings.catch_warnings():
            warnings.simplefilter("error")  # a missing glyph raises
            Figure._english_savefig(self, OUT, **kwargs)
        if glyphs.messages:
            OUT.unlink()
            sys.exit("missing glyphs in mathtext: " + " | ".join(glyphs.messages))

    Figure._english_savefig = Figure.savefig
    Figure.savefig = save_korean
    sys.argv = [str(EN_FIG)] + sys.argv[1:]
    fig1.main()  # prints the English path; the Korean figure goes to OUT
    print("Korean figure:", OUT)


if __name__ == "__main__":
    main()
