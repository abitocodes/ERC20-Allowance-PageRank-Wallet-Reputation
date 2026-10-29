#!/usr/bin/env python3
"""Flag text that runs out of the text block of a Korean reading edition.

usage: python -I -X utf8 check_layout.py main.pdf

The text block is that of common/preamble.tex (A4, 25 mm left and right margins). A word
is flagged when it starts left of the block or ends right of it by more than 2 pt, or
when it lies below the page number. The header line and the page number are ignored.
"""
from __future__ import annotations

import re
import sys

import fitz  # PyMuPDF

MM = 72 / 25.4
LEFT, RIGHT, TOL = 25 * MM, 25 * MM, 2.0


def main() -> int:
    doc = fitz.open(sys.argv[1])
    bad = 0
    for page in doc:
        w, h = page.rect.width, page.rect.height
        words = page.get_text("words", flags=fitz.TEXT_PRESERVE_WHITESPACE)
        body = [x for x in words if 24 * MM < x[1] < h - 22 * MM]
        numbers = [x for x in words if x[1] >= h - 22 * MM and re.fullmatch(r"\d+", x[4])]
        floor = min((x[1] for x in numbers), default=h)
        out = [x for x in body if x[0] < LEFT - TOL or x[2] > w - RIGHT + TOL]
        low = [x for x in words if x[3] > floor + 1 and x not in numbers]
        if out or low:
            bad += 1
            text = " ".join(x[4] for x in (out + low)[:10])
            print(f"  page {page.number + 1}: {len(out)} words outside the block, "
                  f"{len(low)} below the page number: {text}")
    print(f"{sys.argv[1]}: {len(doc)} pages, {bad} with text outside the text block")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
