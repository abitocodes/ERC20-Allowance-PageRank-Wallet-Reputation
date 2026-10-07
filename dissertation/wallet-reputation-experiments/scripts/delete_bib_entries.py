"""Delete bibliography entries by old number and renumber all \\cend citations."""

from __future__ import annotations

import re
from pathlib import Path

from project_paths import MANUSCRIPT_DIR

ROOT = MANUSCRIPT_DIR
BIB = ROOT / "Chapter-07-References" / "index.tex"
CONTENT_DIRS = [ROOT / "01-Intro"] + sorted(ROOT.glob("Chapter-*"))

# Old numbers to remove (Saleh PoS, Yaish time manipulation).
DELETE_OLD: set[int] = {53, 63}

ITEM_RE = re.compile(
    r"\\item\\phantomsection\\label\{ref:(\d+)\} (.+?)(?=\n  \\item|\n\\end\{enumerate\})",
    re.S,
)
CEND_RE = re.compile(r"\\cend\{([^}]+)\}")


def main() -> None:
    bib_text = BIB.read_text(encoding="utf-8")
    begin_idx = bib_text.index("\\begin{enumerate}")
    end_line = bib_text.index("\n", begin_idx)
    header = bib_text[: end_line + 1]
    footer = "\\end{enumerate}\n"

    entries = [(int(m.group(1)), m.group(2).strip()) for m in ITEM_RE.finditer(bib_text)]
    kept = [(old, text) for old, text in entries if old not in DELETE_OLD]
    removed = [(old, text) for old, text in entries if old in DELETE_OLD]
    print("removed:")
    for old, text in removed:
        print(f"  [{old}] {text[:90]}...")

    mapping: dict[int, int] = {}
    new_texts: list[str] = []
    for new_num, (old_num, text) in enumerate(kept, start=1):
        mapping[old_num] = new_num
        new_texts.append(text)

    lines = [header.rstrip()]
    for i, text in enumerate(new_texts, start=1):
        lines.append(f"  \\item\\phantomsection\\label{{ref:{i}}} {text}")
    lines.append(footer)
    BIB.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {BIB} ({len(new_texts)} entries)")

    def update_cend(text: str) -> str:
        def repl(m: re.Match[str]) -> str:
            nums = [n.strip() for n in m.group(1).split(",")]
            new_nums = []
            for n in nums:
                old = int(n)
                if old in DELETE_OLD:
                    raise ValueError(f"cite to deleted entry {old} in \\cend{{{m.group(1)}}}")
                new_nums.append(str(mapping[old]))
            return "\\cend{" + ",".join(new_nums) + "}"

        return CEND_RE.sub(repl, text)

    for d in CONTENT_DIRS:
        for path in sorted(d.rglob("*.tex")):
            if path.name == "bibliography.tex":
                continue
            original = path.read_text(encoding="utf-8")
            if "\\cend{" not in original:
                continue
            updated = update_cend(original)
            if updated != original:
                path.write_text(updated, encoding="utf-8")
                print(f"updated {path.relative_to(ROOT)}")

    map_path = Path(__file__).resolve().parent / "_cite_mapping_delete.txt"
    map_path.write_text(
        "\n".join(f"{o}\t{mapping[o]}" for o in sorted(mapping)) + "\n",
        encoding="utf-8",
    )
    print(f"mapping saved to {map_path}")


if __name__ == "__main__":
    main()
