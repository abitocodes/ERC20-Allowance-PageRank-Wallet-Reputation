#!/usr/bin/env python3
"""Rows of two results digests side by side, by section, file and key.

  python digest_diff.py OLD.md NEW.md [--grep TEXT] [--changed]

Prints one line per row: the quantity, the old value and the new one; rows only in one digest
are listed at the end. With --changed, rows whose value is the same are left out.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROW = re.compile(r"^\| (?P<q>.*?) \| (?P<v>.*?) \| `(?P<f>[^`]*)` : `(?P<k>[^`]*)` \|\s*$")


def rows(path: Path) -> dict:
    out, section, seen = {}, "", {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## ") or line.startswith("### "):
            section = line.lstrip("# ").strip()
            continue
        m = ROW.match(line)
        if not m or m.group("q") == "Quantity":
            continue
        ident = (m.group("f"), m.group("k"), m.group("q"))
        seen[ident] = seen.get(ident, 0) + 1
        out[(*ident, seen[ident])] = (section, m.group("v"))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("old")
    ap.add_argument("new")
    ap.add_argument("--grep", default="")
    ap.add_argument("--changed", action="store_true")
    args = ap.parse_args()
    old, new = rows(Path(args.old)), rows(Path(args.new))
    pat = re.compile(args.grep, re.I) if args.grep else None
    last = None
    for ident, (section, nv) in new.items():
        ov = old.get(ident, (None, None))[1]
        if args.changed and ov == nv:
            continue
        line = f"{ident[2]} | {ov} | {nv}"
        if pat and not pat.search(line + " " + ident[1]):
            continue
        if section != last:
            print(f"\n## {section}")
            last = section
        print(line)
    only_old = [i for i in old if i not in new]
    only_new = [i for i in new if i not in old]
    if not pat:
        print(f"\n{len(only_old)} rows only in the old digest, {len(only_new)} only in the new one")
        for i in only_old[:40]:
            print("  old only:", i[2], "|", old[i][1])
        for i in only_new[:40]:
            print("  new only:", i[2], "|", new[i][1])
    return 0


if __name__ == "__main__":
    sys.exit(main())
