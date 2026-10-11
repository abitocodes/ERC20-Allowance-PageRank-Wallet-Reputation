"""Rebuild 01-Intro/03-TOC.tex of the Korean edition from the translated headings.

Each \TOCentry{num}{{title}}{label} keeps its number and label; the title is
taken from the heading in the translated chapter that carries the same label.
"""
import re
from pathlib import Path

KO = Path(__file__).resolve().parent.parent
EN = KO.parent / "overleaf-github"
BR = r"\{((?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*)\}"

titles = {}
for f in sorted(KO.glob("Chapter-0*/**/*.tex")) + sorted(KO.glob("01-Intro/*.tex")):
    s = f.read_text(encoding="utf-8")
    for m in re.finditer(r"\\dissertationSub(?:sub)?heading\[([^\]]+)\]" + BR, s):
        titles[m.group(1)] = m.group(2)
    for m in re.finditer(r"\\(?:chapter|section)\*?" + BR + r"\s*(?:\\label\{([^}]+)\})?", s):
        if m.group(2):
            titles[m.group(2)] = m.group(1)
    # ethics bullets: \item\phantomsection\label{sub:x} <lead phrase>: text
    for m in re.finditer(r"\\label\{(sub:[^}]+)\}\s*\n?\s*([^:\n]+?):", s):
        titles.setdefault(m.group(1), m.group(2).strip())

toc = (EN / "01-Intro/03-TOC.tex").read_text(encoding="utf-8")
missing = []

def repl(m):
    num, inner, label = m.group(1), m.group(2), m.group(3)
    bold = inner.startswith("\\textbf{")
    bullet = "\\textbullet\\ " in inner
    if label == "ch:abstract":
        t = "초록"
    elif label == "ch:abbreviations":
        t = "줄임말과 기호"
    elif label in titles:
        t = titles[label]
    else:
        missing.append(label)
        return m.group(0)
    if bullet:
        t = "\\textbullet\\ " + t
    if bold:
        t = "\\textbf{" + t + "}"
    return "\\TOCentry{%s}{{%s}}{%s}" % (num, t, label)

out = re.sub(r"\\TOCentry\{([^}]*)\}\{\{(.*?)\}\}\{([^}]*)\}", repl, toc)
out = out.replace("{\\Large\\bfseries Table of Contents\\par}", "{\\Large\\bfseries 차례\\par}")
out = out.replace("{\\Large\\bfseries List of Figures\\par}", "{\\Large\\bfseries 그림 목록\\par}")
out = out.replace("{\\Large\\bfseries List of Tables\\par}", "{\\Large\\bfseries 표 목록\\par}")
(KO / "01-Intro/03-TOC.tex").write_text(out, encoding="utf-8")
print("entries:", len(re.findall(r"\\TOCentry", out)), "missing:", missing)
