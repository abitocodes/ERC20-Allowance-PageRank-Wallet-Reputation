"""Build proposal/main.docx from main.pdf preserving PDF layout (pdf2docx)."""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

from pdf2docx import Converter

ROOT = Path(__file__).resolve().parent.parent
PDF = ROOT / "proposal" / "main.pdf"
DOCX = ROOT / "proposal" / "main.docx"

REQUIRED_SNIPPETS = (
    "August 2026",
    "versus AWP",
    "EndorseRank",
    "Lin et al",
    "Figure 1",
    "Human Passport",
    "Bordeianu",
    "Siddarth",
)


def verify_docx(docx_path: Path) -> None:
    with zipfile.ZipFile(docx_path) as zf:
        if zf.testzip() is not None:
            raise RuntimeError("DOCX zip integrity check failed")
        xml = zf.read("word/document.xml").decode("utf-8")

    missing = [snippet for snippet in REQUIRED_SNIPPETS if snippet not in xml]
    if missing:
        raise RuntimeError(f"DOCX missing expected content: {missing}")
    if "Yang et al" in xml:
        raise RuntimeError("DOCX still contains stale 'Yang et al' citation")


def build(pdf_path: Path, docx_path: Path) -> None:
    if not pdf_path.is_file():
        raise FileNotFoundError(
            f"PDF not found: {pdf_path}. Run proposal/build.ps1 first."
        )

    docx_path.parent.mkdir(parents=True, exist_ok=True)
    if docx_path.exists():
        docx_path.unlink()

    converter = Converter(str(pdf_path))
    try:
        converter.convert(str(docx_path), start=0, end=None)
    finally:
        converter.close()

    verify_docx(docx_path)


def main() -> None:
    pdf = Path(sys.argv[1]) if len(sys.argv) > 1 else PDF
    docx = Path(sys.argv[2]) if len(sys.argv) > 2 else DOCX
    build(pdf, docx)
    print(f"Built {docx}")


if __name__ == "__main__":
    main()
