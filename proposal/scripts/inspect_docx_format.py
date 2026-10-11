"""Quick DOCX format inspection helper."""

from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path


def inspect(path: Path) -> None:
    with zipfile.ZipFile(path) as zf:
        xml = zf.read("word/document.xml").decode("utf-8")
        media = [n for n in zf.namelist() if n.startswith("word/media/")]
    fonts = re.findall(r'w:ascii="([^"]+)"', xml)[:12]
    sizes = re.findall(r'w:sz w:val="(\d+)"', xml)[:12]
    pg = re.search(r"w:pgSz[^>]*/>", xml)
    mar = re.search(r"w:pgMar[^>]*/>", xml)
    print(f"=== {path.name} ===")
    print("size_kb", round(path.stat().st_size / 1024, 1))
    print("June 2026", "June 2026" in xml)
    print("versus AWP", "versus AWP" in xml)
    print("media_count", len(media))
    print("fonts_sample", fonts)
    print("sizes_sample", sizes)
    print("pgSz", pg.group(0) if pg else "none")
    print("pgMar", mar.group(0) if mar else "none")
    print()


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        inspect(Path(arg))
