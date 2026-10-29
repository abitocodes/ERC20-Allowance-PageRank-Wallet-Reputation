#!/usr/bin/env python3
"""Korean-label version of Fig 1 of manuscript A.

The figure is drawn by make_fig1.py of the English manuscript itself
(../../overleaf-github/manuscripts/A-plos-one/figures/make_fig1.py), from the same
published summaries, so the data, the computation and the axes are those of the English
figure. Two things change: the font (Hangul falls back to Malgun Gothic; Latin, digits
and the panel letters stay in the English face) and the visible text, which is replaced
just before the figure is saved. Every English text needs a Korean entry in KO; one
without fails the run, as does a missing glyph.

Output: figures/fig1_ko.pdf next to this script.

usage: python -I -X utf8 make_ko_figures.py [--phd-works PATH]   (or set PHD_WORKS)
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
EN_FIG = HERE.parents[1] / "overleaf-github" / "manuscripts" / "A-plos-one" / "figures" / "make_fig1.py"
OUT = HERE / "figures" / "fig1_ko.pdf"

KO = {
    # panel A rows
    "EndorseRank\n− in-approve degree": "EndorseRank\n− 받은 허락 수",
    "EndorseRank, activity restarts\n− in-approve degree": "EndorseRank, 활동 재시작\n− 받은 허락 수",
    "AWP\n− transfer in-degree": "AWP\n− 송금 입차수",
    # panel B and C rows
    "Liquidation-free close rate": "청산 없이 닫은 비율",
    "No liquidation": "청산 없음",
    "Profitable share": "이익을 낸 비율",
    "Non-loss share": "손실이 아닌 비율",
    "Profitable closes*": "이익을 낸 닫기 수*",
    "Realized gain*": "실현 이익*",
    # legend
    "W1: freeze 30 Jun 2026, labels Jul–Sep 2026": "W1: 2026년 6월 30일 동결, 라벨 2026년 7–9월",
    "W0: freeze 31 Mar 2026, labels Apr–Jun 2026": "W0: 2026년 3월 31일 동결, 라벨 2026년 4–6월",
    # axis labels
    "Δτ, PageRank minus the raw degree it smooths (95% interval)":
        "Δτ, 페이지랭크 − 그것이 다듬는 원시 차수 (95% 구간)",
    "Δτ, allowance side minus transfer side": "Δτ, 허락 쪽 − 송금 쪽",
    # panel titles (after the bold panel letter)
    "Spender contracts: each PageRank minus its raw degree, on the label of its own edge type\n"
    "(new approval pairs for EndorseRank, new transfer senders for AWP)":
        "스펜더 계약: 각 페이지랭크 − 그 원시 차수, 자기 화살표 종류의 라벨에서\n"
        "(EndorseRank는 새 허락 쌍, AWP는 새 송금자)",
    "Contract traders, counts (P):\nin-approve degree − transfer in-degree":
        "계약 트레이더, 그냥 센 수 (P):\n받은 허락 수 − 송금 입차수",
    "Contract traders, PageRanks (Q):\nEndorseRank (activity restarts) − AWP":
        "계약 트레이더, 페이지랭크 (Q):\nEndorseRank(활동 재시작) − AWP",
}
PANEL = re.compile(r"^\$\\mathbf\{([A-Z])\}\$\s+(.*)$", re.S)
NUMERIC = re.compile(r"^[\s\d.,−\-+%]*$")
LETTER_GAP = " " * 6  # room for the bold panel letter and the gap after it


class MissingGlyphs(logging.Handler):
    """Collects mathtext's 'does not have a glyph' messages, which are logged, not warned."""

    def __init__(self) -> None:
        super().__init__()
        self.messages: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        if "glyph" in record.getMessage():
            self.messages.append(record.getMessage())


def translate(fig) -> list:
    """Puts Korean into every text; returns (title, letter) for the panel titles.

    A panel title is a mathtext string in English ("$\\mathbf{A}$   title"). Mathtext sets
    its plain part in one face without fallback, so the Korean title becomes plain text
    led by spaces, and the bold letter is drawn on top of them afterwards.
    """
    from matplotlib.text import Text
    from matplotlib.ticker import FixedFormatter, FuncFormatter
    missing, titles = [], []

    def korean(s: str) -> str:
        if not s or NUMERIC.match(s) or s in KO.values():
            return s
        if s not in KO:
            missing.append(s)
        return KO.get(s, s)

    # Tick labels are redrawn from their formatter, so the formatter gets the Korean.
    # Panels B and C share one y axis formatter, which is changed once.
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
        s = t.get_text()
        m = PANEL.match(s)
        if m and m.group(2) in KO:
            t.set_text(LETTER_GAP + KO[m.group(2)])
            titles.append((t, m.group(1)))
        else:
            t.set_text(korean(s))
    if missing:
        sys.exit("no Korean text for: " + " | ".join(sorted(set(map(repr, missing)))))
    return titles


def main() -> None:
    if "--phd-works" not in sys.argv and not os.environ.get("PHD_WORKS"):
        os.environ["PHD_WORKS"] = str(HERE.parents[4])
    spec = importlib.util.spec_from_file_location("make_fig1", EN_FIG)
    fig1 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fig1)

    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    from matplotlib.text import Text
    # Latin, digits and the minus sign in the English face; Hangul falls back to Malgun Gothic
    # (matplotlib falls back glyph by glyph only through a list of named families)
    plt.rcParams["font.family"] = [fig1.SANS, "Malgun Gothic"]
    glyphs = MissingGlyphs()
    logging.getLogger("matplotlib.mathtext").addHandler(glyphs)
    logging.getLogger("matplotlib._mathtext").addHandler(glyphs)

    def save_korean(self, *_args, **kwargs):
        titles = translate(self)
        self.draw_without_rendering()  # settles the title positions
        renderer = self._get_renderer()
        for t, letter in titles:
            box = t.get_window_extent(renderer)  # the letter goes at the top left of the title
            x, y = self.transFigure.inverted().transform((box.x0, box.y1))
            self.text(x, y, letter, ha="left", va="top", fontfamily=fig1.SANS,
                      fontweight="bold", fontsize=t.get_fontsize(), color=t.get_color())
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
