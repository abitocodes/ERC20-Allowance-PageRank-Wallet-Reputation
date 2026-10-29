#!/usr/bin/env python3
"""Korean-label versions of Figs. 2 and 3 of manuscript B.

The figures are drawn by the figure functions of the English manuscript's own script
(../../overleaf-github/manuscripts/B-ieee-access/figures/make_figures_b.py: sweep and
forest), from the same published summaries, so the data, the computation, the axes and
the layout are those of the English figures. Two things change: the font (Malgun Gothic,
with Arial for the minus sign; mathematics stays in STIX mathtext) and the visible text,
which is replaced just before each figure is saved. Every English text needs a Korean entry in KO_TEXT; a text without
one fails the run, and so does a glyph missing from the font.

Output: figures/fig_contrasts.pdf and figures/fig_lambda_sweep.pdf next to this script.
Nothing is written into the English folder.

usage: python -I -X utf8 make_ko_figures.py --phd-works D:/Github/phd_works   (or set PHD_WORKS)
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import re
import sys
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("pdf")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402
from matplotlib.text import Text  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "figures"
EN_SCRIPT = (HERE.parents[1] / "overleaf-github" / "manuscripts" / "B-ieee-access"
             / "figures" / "make_figures_b.py")

# English text as make_figures_b.py writes it -> Korean text. Terms follow
# ../../overleaf-github-ko/TRANSLATION-GUIDE.md; method names stay in English.
KO_TEXT: dict[str, str] = {
    # Fig. 3 (sweep)
    "W0 spenders (labels Apr–Jun)": "W0 스펜더(라벨 4~6월)",
    "W1 spenders (labels Jul–Sep)": "W1 스펜더(라벨 7~9월)",
    "W1 traders (labels Jul–Sep)": "W1 트레이더(라벨 7~9월)",
    "Revised analysis (main analysis, a re-analysis; US dollars, five tokens, twelve-month score windows)":
        "수정 분석(주 분석, 재분석; 달러 금액, 다섯 토큰, 동결 직전 12개월 점수 기간)",
    "Registered analysis (the pre-specified test; raw base units, every ERC-20)":
        "등록 분석(미리 정한 시험; 원래 단위, 모든 ERC-20 토큰)",
    r"Kendall $\tau_b$": r"켄달의 $\tau_b$",
    r"weight $\lambda$ on the authorization layer": r"허락 층의 무게 $\lambda$",
    "New approval pairs": "새 허락 쌍",
    "New transfer senders": "새 송금자",
    "Liquidation-free close rate": "청산 없이 닫은 비율",
    r"$\lambda=0$ or $1$: one layer walked alone": r"$\lambda=0$ 또는 $1$: 한 층만 걷기",
    # Fig. 2 (forest): group headers
    "Rule A, primary part (plan, 13:41:27 UTC); W0": "규칙 A의 주 부분(계획, 13:41:27 UTC); W0",
    "Rule B (registration, 16:49:32 UTC); W1; all three required": "규칙 B(등록, 16:49:32 UTC); W1; 셋 모두 충족해야 함",
    "Reported beside rule B (nominal)": "규칙 B 옆에 보고(명목상)",
    "Sensitivity 1: AWP as comparator (nominal)": "민감도 분석 S1: AWP와 견줌(명목상)",
    "Sensitivity 2: contracts outside a graph as isolated nodes (nominal)":
        "민감도 분석 S2: 그래프 밖 계약을 외톨이 점으로 둠(명목상)",
    # Fig. 2: rows
    "A1  C-PR − C-PR(1) · new approval pairs": "A1  C-PR − C-PR(1) · 새 허락 쌍",
    "A2  C-PR − C-PR(0) · new transfer senders": "A2  C-PR − C-PR(0) · 새 송금자",
    "F1  C-PR − C-PR(0) · new approval pairs": "F1  C-PR − C-PR(0) · 새 허락 쌍",
    "F2  C-PR − C-PR(0) · new transfer senders": "F2  C-PR − C-PR(0) · 새 송금자",
    "F3  C-PR − C-PR(0) · liquidation-free rate": "F3  C-PR − C-PR(0) · 청산 없이 닫은 비율",
    "F4  as F3, superiority": "F4  F3과 같은 대비, 우월성",
    "F5  C-PR − C-PR(1) · liquidation-free rate": "F5  C-PR − C-PR(1) · 청산 없이 닫은 비율",
    "F6a C-PR − C-PR(1) · new approval pairs": "F6a C-PR − C-PR(1) · 새 허락 쌍",
    "F6b C-PR − C-PR(0) · new transfer senders": "F6b C-PR − C-PR(0) · 새 송금자",
    "F1  C-PR − AWP · new approval pairs": "F1  C-PR − AWP · 새 허락 쌍",
    "F2  C-PR − AWP · new transfer senders": "F2  C-PR − AWP · 새 송금자",
    "F3  C-PR − AWP · liquidation-free rate": "F3  C-PR − AWP · 청산 없이 닫은 비율",
    # Fig. 2: tests, axis and legend
    "no worse": "더 나쁘지 않음",
    "superiority": "우월성",
    "non-inferiority": "비열등성",
    r"$\Delta\tau_b$ with 95% paired-bootstrap interval; dashed line: margin $-\delta=-0.01$":
        r"$\Delta\tau_b$와 95% 짝지은 부트스트랩 구간; 점선: 허용 폭 $-\delta=-0.01$",
    "revised analysis (main; re-analysis)": "수정 분석(주 분석, 재분석)",
    "registered analysis (pre-specified test)": "등록 분석(미리 정한 시험)",
    "filled: criterion met": "채운 표시: 기준 충족",
    "open: not met": "빈 표시: 충족 못 함",
}


def translate(text: str) -> str:
    """The Korean text for a visible text; texts without Latin letters stay as they are."""
    if not re.search(r"[A-Za-z]", text):
        return text
    if text in KO_TEXT:
        return KO_TEXT[text]
    if text in KO_TEXT.values():
        return text
    raise SystemExit(f"no Korean text for {text!r}; add it to KO_TEXT")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--phd-works", default=os.environ.get("PHD_WORKS"))
    args = ap.parse_args()
    if not args.phd_works:
        sys.exit("pass --phd-works PATH or set PHD_WORKS")

    spec = importlib.util.spec_from_file_location("make_figures_b", EN_SCRIPT)
    en = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(en)  # sets the English rcParams; the font is replaced below

    # Malgun Gothic first: text inside a mathtext string ("켄달의 $\tau_b$") is set in the
    # first family only. Malgun Gothic has no minus sign (U+2212); that glyph comes from Arial.
    plt.rcParams.update({"font.family": ["Malgun Gothic", "Arial"], "axes.unicode_minus": True})
    warnings.filterwarnings("error", message=r".*[Gg]lyph.*missing")
    warnings.filterwarnings("error", message=r".*does not have a glyph")

    OUT.mkdir(exist_ok=True)
    written: list[Path] = []
    save = Figure.savefig

    def save_korean(fig: Figure, fname, *a, **kw) -> None:
        for t in fig.findobj(Text):
            if t.get_text():
                t.set_text(translate(t.get_text()))
        target = (OUT / Path(fname).name).resolve()
        if target.parent != OUT.resolve():
            sys.exit(f"refusing to write {target}")
        save(fig, target, *a, **kw)
        written.append(target)

    Figure.savefig = save_korean
    data = en.load(en.published_dirs(Path(args.phd_works).resolve()))
    en.sweep(data)
    en.forest(data)
    for p in written:
        print("wrote", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
