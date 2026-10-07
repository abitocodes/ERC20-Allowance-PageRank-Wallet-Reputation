"""Renumber all \\cend citations and the References list.

Usage:
  python renumber_citations.py                      # alphabetical (APA order)
  python renumber_citations.py --mode first-appearance [--drop-uncited]

Modes
  alpha            Insert NEW_ENTRIES, sort APA-style by first-author surname,
                   rewrite ref:N labels and every \\cend{...}.
  first-appearance Number references in the order they are first cited when the
                   document is read front to back (main.tex include order,
                   following nested \\input/\\include). Entries that are never
                   cited are reported and, with --drop-uncited, removed.
                   Requested by the 2026-09-09 supervisory meeting (Moulla).

Reads 1-Dissertation-Works/ERC20-Allowance-PageRank-Wallet-Reputation/dissertation/overleaf-github/Chapter-07-References/index.tex and updates the
\\cend{...} calls in every chapter/appendix .tex file. Prints the old->new
mapping for QA and regenerates Config/bibentries.tex.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from project_paths import MANUSCRIPT_DIR

ROOT = MANUSCRIPT_DIR
BIB = ROOT / "Chapter-07-References" / "index.tex"
MAIN = ROOT / "main.tex"
CONTENT_DIRS = [ROOT / "01-Intro"] + sorted(ROOT.glob("Chapter-*"))

# Verified APA entries (Crossref / standard book citation). No leading label.
# Entries added by earlier runs are already in the References file; keep this
# list empty unless a new alphabetical insertion is required.
NEW_ENTRIES: list[str] = []

ITEM_RE = re.compile(
    r"\\item\\phantomsection\\label\{ref:(\d+)\} (.+?)(?=\n  \\item|\n\\end\{enumerate\})",
    re.S,
)
CEND_RE = re.compile(r"\\cend\{([^}]+)\}")


def normalize_sort_key(text: str) -> tuple[str, str, str]:
    """Return (surname_lower, year, title_lower) for APA-ish sort."""
    text = text.strip()
    # Strip LaTeX accents for sorting: Sch\"{a}r ??Schar
    plain = re.sub(r'\\[a-zA-Z]+\{([^{}]*)\}', r"\1", text)
    plain = plain.replace(r"\&", "&")
    # First author surname: text before first comma, or first token before period for orgs.
    if "," in plain.split("(")[0]:
        surname = plain.split(",", 1)[0].strip()
    else:
        surname = plain.split(".", 1)[0].strip()
    m_year = re.search(r"\((\d{4}|n\.d\.)\)", plain)
    year = m_year.group(1) if m_year else "0000"
    # Title fragment after year for tie-break
    title = plain
    if m_year:
        title = plain[m_year.end() :].lstrip(". ").lower()
    return (surname.lower(), year, title[:80])


def parse_bibliography(bib_text: str) -> list[tuple[int | None, str]]:
    """Return list of (old_number_or_None, entry_text)."""
    entries: list[tuple[int | None, str]] = []
    for m in ITEM_RE.finditer(bib_text):
        entries.append((int(m.group(1)), m.group(2).strip()))
    return entries


def rewrite_bibliography(header: str, footer: str, entries: list[str]) -> str:
    lines = [header.rstrip()]
    for i, text in enumerate(entries, start=1):
        lines.append(f"  \\item\\phantomsection\\label{{ref:{i}}} {text}")
    lines.append(footer)
    return "\n".join(lines) + "\n"


def update_cend(text: str, mapping: dict[int, int]) -> str:
    def repl(m: re.Match[str]) -> str:
        nums = [n.strip() for n in m.group(1).split(",")]
        new_nums = []
        for n in nums:
            if not n.isdigit():
                raise ValueError(f"non-numeric cite in \\cend{{{m.group(1)}}}")
            old = int(n)
            if old not in mapping:
                raise KeyError(f"old cite {old} missing from mapping")
            new_nums.append(str(mapping[old]))
        return "\\cend{" + ",".join(new_nums) + "}"

    return CEND_RE.sub(repl, text)


INPUT_RE = re.compile(r"\\(?:input|include)\{([^}]+)\}")


def strip_tex_comments(text: str) -> str:
    """Remove % comments (not \\%) so commented-out \\input lines are ignored."""
    return re.sub(r"(?<!\\)%.*", "", text)


def document_order_files(main: Path = MAIN) -> list[Path]:
    """Return .tex files in reading order by following \\input/\\include from main.tex."""
    order: list[Path] = []

    def walk(path: Path) -> None:
        if path in order or not path.exists():
            return
        order.append(path)
        text = strip_tex_comments(path.read_text(encoding="utf-8"))
        for m in INPUT_RE.finditer(text):
            rel = m.group(1).strip()
            if rel.startswith("\\"):
                continue  # macro-driven include (e.g. \ChapterOnlyPath/index)
            if not rel.endswith(".tex"):
                rel += ".tex"
            candidate = (path.parent / rel) if not (ROOT / rel).exists() else (ROOT / rel)
            walk(candidate.resolve())

    walk(main.resolve())
    return order


def cited_in_order(files: list[Path]) -> list[int]:
    """Old citation numbers in first-appearance order across `files`."""
    seen: list[int] = []
    for path in files:
        if path.resolve() == BIB.resolve() or path.name == "bibentries.tex":
            continue
        text = strip_tex_comments(path.read_text(encoding="utf-8"))
        for m in CEND_RE.finditer(text):
            for n in m.group(1).split(","):
                n = n.strip()
                if not n.isdigit():
                    raise ValueError(f"non-numeric cite in {path.name}: \\cend{{{m.group(1)}}}")
                num = int(n)
                if num not in seen:
                    seen.append(num)
    return seen


def rewrite_content(mapping: dict[int, int]) -> int:
    updated_files = 0
    for d in CONTENT_DIRS:
        for path in sorted(d.rglob("*.tex")):
            if path.name == "bibliography.tex" or path.resolve() == BIB.resolve():
                continue
            if "archive" in path.parts:
                continue
            original = path.read_text(encoding="utf-8")
            if "\\cend{" not in original:
                continue
            updated = update_cend(original, mapping)
            if updated != original:
                path.write_text(updated, encoding="utf-8")
                updated_files += 1
                print(f"updated cites in {path.relative_to(ROOT)}")
    print(f"updated {updated_files} content files")
    return updated_files


def save_mapping(mapping: dict[int, int], new_texts: list[str], extra: list[str]) -> None:
    map_path = Path(__file__).resolve().parent / "_cite_mapping.txt"
    lines = [f"{o}\t{mapping[o]}" for o in sorted(mapping)]
    lines.extend(extra)
    map_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"mapping saved to {map_path}")


def regenerate_bibentries() -> None:
    try:
        from generate_bibentries import main as gen_main  # type: ignore
    except ImportError:  # pragma: no cover
        import sys

        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from generate_bibentries import main as gen_main  # type: ignore
    gen_main()


def split_bib(bib_text: str) -> tuple[str, str]:
    begin_idx = bib_text.index("\\begin{enumerate}")
    end_line = bib_text.index("\n", begin_idx)
    return bib_text[: end_line + 1], "\\end{enumerate}\n"


def run_alpha() -> None:
    bib_text = BIB.read_text(encoding="utf-8")
    header, footer = split_bib(bib_text)

    old_entries = parse_bibliography(bib_text)
    if not old_entries:
        raise RuntimeError("no bibliography entries parsed")

    combined: list[tuple[int | None, str]] = list(old_entries)
    for text in NEW_ENTRIES:
        combined.append((None, text))
    combined.sort(key=lambda pair: normalize_sort_key(pair[1]))

    mapping: dict[int, int] = {}
    new_texts: list[str] = []
    for new_num, (old_num, text) in enumerate(combined, start=1):
        new_texts.append(text)
        if old_num is not None:
            mapping[old_num] = new_num

    BIB.write_text(rewrite_bibliography(header, footer, new_texts), encoding="utf-8")
    print(f"wrote {BIB} ({len(new_texts)} entries)")
    print("old -> new mapping:")
    for old in sorted(mapping):
        print(f"  {old:3d} -> {mapping[old]:3d}")
    new_only = set(range(1, len(new_texts) + 1)) - set(mapping.values())
    for n in sorted(new_only):
        print(f"  NEW [{n}] {new_texts[n - 1][:90]}...")

    rewrite_content(mapping)
    save_mapping(mapping, new_texts, [f"NEW\t{n}\t{new_texts[n - 1][:120]}" for n in sorted(new_only)])
    regenerate_bibentries()


def run_first_appearance(drop_uncited: bool) -> None:
    bib_text = BIB.read_text(encoding="utf-8")
    header, footer = split_bib(bib_text)
    old_entries = parse_bibliography(bib_text)
    if not old_entries:
        raise RuntimeError("no bibliography entries parsed")
    by_old = {num: text for num, text in old_entries}
    if len(by_old) != len(old_entries):
        raise RuntimeError("duplicate ref:N labels in References")

    files = document_order_files()
    print("reading order:")
    for p in files:
        print(f"  {p.relative_to(ROOT)}")
    order = cited_in_order(files)
    missing = [n for n in order if n not in by_old]
    if missing:
        raise KeyError(f"cited numbers without a References entry: {missing}")
    uncited = sorted(set(by_old) - set(order))

    mapping: dict[int, int] = {old: new for new, old in enumerate(order, start=1)}
    new_texts: list[str] = [by_old[old] for old in order]
    extra: list[str] = []
    if uncited:
        print(f"uncited entries ({len(uncited)}):")
        for n in uncited:
            print(f"  [{n}] {by_old[n][:100]}...")
        if drop_uncited:
            print("  -> dropped (--drop-uncited)")
            extra = [f"DROPPED\t{n}\t{by_old[n][:120]}" for n in uncited]
        else:
            # Keep them at the tail so nothing is lost silently.
            for n in uncited:
                mapping[n] = len(new_texts) + 1
                new_texts.append(by_old[n])
            extra = [f"UNCITED-TAIL\t{n}\t{mapping[n]}" for n in uncited]

    BIB.write_text(rewrite_bibliography(header, footer, new_texts), encoding="utf-8")
    print(f"wrote {BIB} ({len(new_texts)} entries, first-appearance order)")
    changed = sum(1 for o, n in mapping.items() if o != n)
    print(f"old -> new mapping ({changed} renumbered):")
    for old in sorted(mapping):
        marker = "" if mapping[old] == old else "  *"
        print(f"  {old:3d} -> {mapping[old]:3d}{marker}")

    rewrite_content(mapping)
    save_mapping(mapping, new_texts, extra)
    regenerate_bibentries()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--mode", choices=("alpha", "first-appearance"), default="alpha")
    parser.add_argument(
        "--drop-uncited",
        action="store_true",
        help="first-appearance mode: remove References entries that are never cited",
    )
    args = parser.parse_args()
    if args.mode == "alpha":
        run_alpha()
    else:
        run_first_appearance(drop_uncited=args.drop_uncited)


if __name__ == "__main__":
    main()
