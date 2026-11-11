#!/usr/bin/env python3
r"""Rewrite results/README.md of the thesis from the manuscript itself.

For every generated table in ``results/tables/`` the README gives the entry of the List of
Tables (the optional argument of ``\caption``, or the caption's first sentence) and the place
where the thesis inputs it (chapter and section heading). Tables that no chapter inputs are
listed apart. The text above the first ``## `` heading of the README is kept as it is.

Usage:

    python make_results_readme.py [--root PATH_TO_overleaf-github] [--check]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_ROOT = HERE.parent.parent / "overleaf-github"
BR = r"\{((?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*)\}"
HEADING = re.compile(r"\\(?:chapter|section|dissertationSubheading|dissertationSubsubheading)\*?(?:\[[^\]]*\])?" + BR)
INPUT = re.compile(r"\\input\{results/tables/([^}]+?)(?:\.tex)?\}")
CHAPTER_INPUT = re.compile(r"^\\input\{(Chapter-[^}]+)\}", re.M)


def strip_comments(text: str) -> str:
    return "\n".join(re.sub(r"(?<!\\)%.*$", "", line) for line in text.splitlines())


def plain(tex: str) -> str:
    tex = re.sub(r"\\texorpdfstring" + BR + BR, lambda m: m.group(1), tex)
    tex = tex.replace("~", " ").replace("\\%", "%").replace("\\&", "&").replace("$", "")
    tex = re.sub(r"\\(?:mathrm|texttt|emph|textbf|text|mathcal)\{([^{}]*)\}", r"\1", tex)
    tex = tex.replace("\\tau", "τ").replace("\\lambda", "λ").replace("\\rho", "ρ").replace("\\delta", "δ")
    tex = re.sub(r"\\[a-zA-Z]+\*?", "", tex)
    tex = re.sub(r"[{}]", "", tex)
    return re.sub(r"\s+", " ", tex).strip()


def short_caption(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    m = re.search(r"\\caption\[((?:[^\[\]]|\{[^{}]*\})*)\]", text)
    if m:
        return plain(m.group(1))
    m = re.search(r"\\caption" + BR, text)
    if not m:
        return ""
    first = re.split(r"(?<=\.)\s+(?=[A-Z$\\])", m.group(1), maxsplit=1)[0]
    return plain(first)


def places(root: Path) -> dict[str, tuple[str, str]]:
    """table name -> (chapter title, section heading) of its \\input."""
    out: dict[str, tuple[str, str]] = {}
    for folder in sorted(root.glob("Chapter-0*")):
        if not folder.is_dir():
            continue
        text = strip_comments((folder / "index.tex").read_text(encoding="utf-8"))

        def splice(m: re.Match) -> str:
            p = root / m.group(1)
            return strip_comments((p if p.suffix else p.with_suffix(".tex")).read_text(encoding="utf-8"))

        text = CHAPTER_INPUT.sub(splice, text)
        n = int(folder.name.split("-")[1])
        chapter = "Appendix" if n == 8 else f"Chapter {n}"
        heads = [(m.start(), plain(m.group(1))) for m in HEADING.finditer(text)]
        for m in INPUT.finditer(text):
            sec = next((t for pos, t in reversed(heads) if pos < m.start()), "")
            if m.group(1) in out:
                raise SystemExit(f"table {m.group(1)} is input twice")
            out[m.group(1)] = (chapter, sec)
    return out


def build(root: Path) -> str:
    readme = root / "results" / "README.md"
    old = readme.read_text(encoding="utf-8").replace("\r\n", "\n")
    head = old.split("\n## ", 1)[0].rstrip("\n")
    where = places(root)
    tables = sorted(p.stem for p in (root / "results" / "tables").glob("*.tex"))
    missing = sorted(set(where) - set(tables))
    if missing:
        raise SystemExit("input of a table that does not exist: " + ", ".join(missing))
    lines = [head, ""]
    order = [f"Chapter {i}" for i in range(1, 7)] + ["Appendix"]
    for chapter in order:
        rows = [(t, where[t][1]) for t in tables if t in where and where[t][0] == chapter]
        if not rows:
            continue
        lines += [f"## {chapter}", "", "| File | Section | Entry in the List of Tables |", "|------|---------|-----------------------------|"]
        # in the order of appearance: keep the order of `where` (insertion order follows the text)
        seq = [t for t in where if where[t][0] == chapter]
        for t in seq:
            lines.append(f"| `{t}.tex` | {where[t][1]} | {short_caption(root / 'results' / 'tables' / (t + '.tex'))} |")
        lines.append("")
    unused = [t for t in tables if t not in where]
    if unused:
        lines += ["## Generated but not input", "", "| File | Entry in the List of Tables |", "|------|-----------------------------|"]
        lines += [f"| `{t}.tex` | {short_caption(root / 'results' / 'tables' / (t + '.tex'))} |" for t in unused]
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    root = Path(a.root).resolve()
    readme = root / "results" / "README.md"
    raw = readme.read_bytes().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    new = build(root)
    if new == raw.replace("\r\n", "\n"):
        print("results/README.md unchanged")
        return 0
    if a.check:
        print("results/README.md would change")
        return 1
    readme.write_bytes(new.replace("\n", nl).encode("utf-8"))
    print("results/README.md rewritten")
    return 0


if __name__ == "__main__":
    sys.exit(main())
