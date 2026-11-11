#!/usr/bin/env python3
r"""Rebuild the hand-kept table of contents of the English thesis from its headings.

``01-Intro/03-TOC.tex`` lists every chapter, every section of Chapters 1 to 6 and, for the
appendix, every section and subsection, as ``\TOCentry{number}{{title}}{label}`` lines. The
numbers are typed, so they must follow the headings whenever a section is added, removed or
moved. This script reads the headings in the order LaTeX meets them and writes the entries
again; everything outside the list of entries (the title lines, the lists of figures and
tables) is kept as it is.

Rules, taken from the manuscript:

* ``\chapter{T}`` followed by ``\label{ch:...}`` opens a chapter.
* In Chapters 1 to 6 ``\dissertationSubheading[label]{T}`` is a section (N.M) and is listed;
  ``\dissertationSubsubheading`` is a subsection and is not listed.
* In the appendix ``\section{T}`` followed by ``\label{...}`` is a section (8.M, bold) and
  ``\dissertationSubheading[label]{T}`` a subsection (8.M.K); both are listed.
* The bullets under the ethics section (``\item\phantomsection\label{sub:...}`` followed by a
  lead phrase that ends at the first colon) are listed without a number.
* ``\texorpdfstring{A}{B}`` in a title is written as A.
* A heading without a label cannot be linked and stops the script.

Usage:

    python make_toc.py [--root PATH_TO_overleaf-github] [--check]

``--check`` writes nothing and exits with status 1 if the file would change.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_ROOT = HERE.parent.parent / "overleaf-github"
BR = r"\{((?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*)\}"
CHAPTER = re.compile(r"\\chapter\*?" + BR + r"\s*\\label\{([^}]+)\}")
TOKEN = re.compile(
    r"\\dissertationSubheading\[([^\]]+)\]" + BR
    + r"|\\dissertationSubsubheading\[([^\]]+)\]" + BR
    + r"|\\section\*?" + BR + r"\s*\\label\{([^}]+)\}"
    + r"|\\item\\phantomsection\\label\{(sub:[^}]+)\}\s*([^:\n]+?):"
)
INPUT = re.compile(r"^\\input\{(Chapter-[^}]+)\}", re.M)
FIXED_FRONT = [("", r"\textbf{Declaration}", "ch:declaration"), ("", r"\textbf{Abstract}", "ch:abstract"),
               ("", r"\textbf{Abbreviations and Notation}", "ch:abbreviations")]
APPENDIX = 8


def read_chapter(root: Path, folder: Path) -> str:
    """The chapter's index.tex with its \\input files spliced in at the place of the \\input."""
    text = (folder / "index.tex").read_text(encoding="utf-8")

    def splice(m: re.Match) -> str:
        p = root / m.group(1)
        if not p.suffix:
            p = p.with_suffix(".tex")
        return p.read_text(encoding="utf-8")

    return INPUT.sub(splice, strip_comments(text))


def strip_comments(text: str) -> str:
    return "\n".join(re.sub(r"(?<!\\)%.*$", "", line) for line in text.splitlines())


def clean(title: str) -> str:
    title = re.sub(r"\\texorpdfstring" + BR + BR, lambda m: m.group(1), title)
    return re.sub(r"\s+", " ", title).strip()


def entries(root: Path) -> list[tuple[int, str, str, str]]:
    """(indent level, number, title, label) for every entry, in order."""
    out = [(0, n, t, l) for n, t, l in FIXED_FRONT]
    for folder in sorted(root.glob("Chapter-0*")):
        if not folder.is_dir():
            continue
        n = int(folder.name.split("-")[1])
        text = strip_comments(read_chapter(root, folder))
        m = CHAPTER.search(text)
        if not m:
            raise SystemExit(f"{folder.name}: no \\chapter with a label")
        out.append((0, str(n), r"\textbf{" + clean(m.group(1)) + "}", m.group(2)))
        sec = sub = 0
        for t in TOKEN.finditer(text, m.end()):
            sub_label, sub_title, subsub_label, _subsub_title, sec_title, sec_label, bullet_label, bullet_title = t.groups()
            if n == APPENDIX:
                if sec_label:
                    sec, sub = sec + 1, 0
                    out.append((1, f"{n}.{sec}", r"\textbf{" + clean(sec_title) + "}", sec_label))
                elif sub_label:
                    sub += 1
                    out.append((2, f"{n}.{sec}.{sub}", clean(sub_title), sub_label))
            else:
                if sub_label:
                    sec += 1
                    out.append((1, f"{n}.{sec}", clean(sub_title), sub_label))
                elif sec_label:
                    raise SystemExit(f"{folder.name}: bare \\section {sec_title!r}; use \\dissertationSubheading")
                elif bullet_label:
                    out.append((2, "", r"\textbullet\ " + clean(bullet_title).rstrip(".:"), bullet_label))
    return out


def render(items: list[tuple[int, str, str, str]]) -> str:
    lines = []
    for level, number, title, label in items:
        indent = {0: "", 1: r"\hspace*{1.5em}", 2: r"\hspace*{3.0em}"}[level]
        lines.append(f"{indent}\\TOCentry{{{number}}}{{{{{title}}}}}{{{label}}}")
    return "\n\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    root = Path(a.root).resolve()
    toc_path = root / "01-Intro" / "03-TOC.tex"
    raw = toc_path.read_bytes().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    old = raw.replace("\r\n", "\n")
    first = re.search(r"^(?:\\hspace\*\{[^}]*\})?\\TOCentry", old, re.M)
    last = None
    for last in re.finditer(r"^(?:\\hspace\*\{[^}]*\})?\\TOCentry.*$", old, re.M):
        pass
    if not first or not last:
        raise SystemExit("no \\TOCentry lines in the table of contents")
    new = old[:first.start()] + render(entries(root)) + old[last.end():]
    n_old, n_new = old.count("\\TOCentry"), new.count("\\TOCentry")
    if new == old:
        print(f"table of contents unchanged ({n_new} entries)")
        return 0
    if a.check:
        import difflib
        for line in difflib.unified_diff(old.splitlines(), new.splitlines(), "03-TOC.tex", "rebuilt", lineterm="", n=0):
            print(line)
        return 1
    toc_path.write_bytes(new.replace("\n", nl).encode("utf-8"))
    print(f"table of contents rewritten: {n_old} -> {n_new} entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
