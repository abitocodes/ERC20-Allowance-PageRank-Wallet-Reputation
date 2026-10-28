#!/usr/bin/env python3
"""Audit the point estimates written with their interval (P [L, H]): which digest holds each triple.

  python triples.py --new NEW.md --old OLD.md --keep KEEP.md FILE.tex ...

Prints every triple that the new digest does not hold: those of the old digest only (not yet
replaced), those of the digest that stays only (registered sentences: check them), and those of
no digest (derived, mistyped, or half replaced).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numbers as nm  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--new", required=True)
    ap.add_argument("--old", required=True)
    ap.add_argument("--keep", required=True)
    ap.add_argument("files", nargs="+")
    a = ap.parse_args()
    new, old, keep = (nm.read_digest(Path(p)) for p in (a.new, a.old, a.keep))
    counts = {"new": 0, "old only": 0, "kept only": 0, "none": 0}
    for f in nm.tex_files(a.files):
        for ln, raw in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            line = nm.strip_comment(raw)
            nums = nm.numbers(nm.mask_dates(line))
            for idx in sorted(set(nm.groups(line, nums).values())):
                g = tuple(nums[k] for k in idx)
                where = ("new" if nm.triples(new, g) else "old only" if nm.triples(old, g) and not nm.triples(keep, g)
                         else "kept only" if nm.triples(keep, g) else "none")
                counts[where] += 1
                if where != "new":
                    txt = line[g[0].start:g[2].end + 3]
                    print(f"{where:9} {f.parent.name[:24]}:{ln}  {txt}")
    print(counts)
    return 0


if __name__ == "__main__":
    sys.exit(main())
