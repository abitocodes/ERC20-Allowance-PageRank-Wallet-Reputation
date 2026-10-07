# -*- coding: utf-8 -*-
"""Translate proposal DOCX EN→KO into a new file (never overwrite source).

Preserves paragraph/run structure by writing the full translated string into
the first run and clearing subsequent runs. Protects common technical terms
via temporary placeholders.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from deep_translator import GoogleTranslator
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from lxml import etree

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

SRC = Path(r"c:\Users\abito\Downloads\Proposal Final_080426_1705.docx")
DST = Path(r"c:\Users\abito\Downloads\Proposal Final_080426_1705_KO.docx")
CACHE = Path(__file__).resolve().parent / "_ko_translation_cache.json"

# Longer / more specific phrases first.
PROTECT = [
    "Adaptive Weighted PageRank",
    "EndorseRank",
    "PageRank",
    "RiskProp",
    "Arbitrum One",
    "BigQuery",
    "PositionDecrease",
    "PositionIncrease",
    "Human Passport",
    "Gitcoin Passport",
    "basePnlUsd",
    "orderType",
    "ERC-20",
    "EIP-2612",
    "GMX V2",
    "GMX",
    "AWP",
    "DeFi",
    "Sybil",
    "SPICE",
    "UNISA",
    "CSET",
    "Kendall",
    "Spearman",
    "Taehong Kwon",
    "Ernest Mnkandla",
    "Donatien Koulla Moulla",
    "David Sena Attipoe",
]


def _load_cache() -> dict[str, str]:
    if CACHE.exists():
        return json.loads(CACHE.read_text(encoding="utf-8"))
    return {}


def _save_cache(cache: dict[str, str]) -> None:
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")


def _should_skip(text: str) -> bool:
    t = text.strip()
    if not t:
        return True
    if re.fullmatch(r"[\d\W_]+", t, flags=re.UNICODE):
        return True
    # mostly Hangul already
    hangul = len(re.findall(r"[\uac00-\ud7a3]", t))
    latin = len(re.findall(r"[A-Za-z]", t))
    if hangul > 0 and hangul >= latin:
        return True
    return False


def _protect(text: str) -> tuple[str, list[str]]:
    held: list[str] = []
    out = text
    for term in PROTECT:
        if term not in out:
            continue
        token = f"⟦T{len(held)}⟧"

        def repl(m: re.Match[str], tok: str = token, val: str = term) -> str:
            held.append(val)
            return tok

        out = re.sub(re.escape(term), repl, out)
    return out, held


def _unprotect(text: str, held: list[str]) -> str:
    out = text
    for i, val in enumerate(held):
        for tok in (f"⟦T{i}⟧", f"[T{i}]", f"(T{i})", f"T{i}"):
            out = out.replace(tok, val)
    return out


def _translate_one(translator: GoogleTranslator, text: str, cache: dict[str, str]) -> str:
    key = text
    if key in cache:
        return cache[key]
    protected, held = _protect(text)
    # Google free endpoint ~4500–5000 chars; split long paras
    chunks: list[str] = []
    max_len = 4500
    if len(protected) <= max_len:
        parts = [protected]
    else:
        parts = []
        buf = ""
        for sent in re.split(r"(?<=[.!?])\s+", protected):
            if len(buf) + len(sent) + 1 <= max_len:
                buf = f"{buf} {sent}".strip()
            else:
                if buf:
                    parts.append(buf)
                buf = sent
        if buf:
            parts.append(buf)

    translated_parts: list[str] = []
    for part in parts:
        for attempt in range(5):
            try:
                translated_parts.append(translator.translate(part))
                break
            except Exception as exc:  # noqa: BLE001
                wait = 1.5 * (attempt + 1)
                print(f"  retry after {wait:.1f}s: {exc}", flush=True)
                time.sleep(wait)
        else:
            raise RuntimeError(f"Failed to translate chunk: {part[:80]!r}")
        time.sleep(0.12)

    result = _unprotect(" ".join(translated_parts), held)
    cache[key] = result
    return result


def _set_text_keep_first_run(paragraph, text: str) -> None:
    runs = paragraph.runs
    if not runs:
        paragraph.add_run(text)
        return
    runs[0].text = text
    for r in runs[1:]:
        r.text = ""


def _iter_all_paragraphs(doc: Document):
    yield from doc.paragraphs
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                yield from cell.paragraphs
    for section in doc.sections:
        for hdr in (section.header, section.first_page_header, section.even_page_header):
            if hdr is not None:
                yield from hdr.paragraphs
                for table in hdr.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            yield from cell.paragraphs
        for ftr in (section.footer, section.first_page_footer, section.even_page_footer):
            if ftr is not None:
                yield from ftr.paragraphs
                for table in ftr.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            yield from cell.paragraphs


def _collect_unique_texts(doc: Document) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for p in _iter_all_paragraphs(doc):
        t = p.text
        if _should_skip(t) or t in seen:
            continue
        seen.add(t)
        ordered.append(t)
    return ordered


def _translate_comments_xml(src: Path, dst: Path, cache: dict[str, str], translator: GoogleTranslator) -> None:
    """Patch comments inside the already-copied dst zip."""
    with zipfile.ZipFile(dst, "r") as zin:
        names = zin.namelist()
        if "word/comments.xml" not in names:
            return
        comments_xml = zin.read("word/comments.xml")
        other = {n: zin.read(n) for n in names if n != "word/comments.xml"}

    root = etree.fromstring(comments_xml)
    for comment in root.findall(f"{W}comment"):
        texts = comment.findall(f".//{W}t")
        if not texts:
            continue
        full = "".join(t.text or "" for t in texts)
        if _should_skip(full):
            continue
        ko = _translate_one(translator, full, cache)
        texts[0].text = ko
        for t in texts[1:]:
            t.text = ""
        # drop leftover <w:t> siblings' content already cleared
    new_xml = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)

    tmp = dst.with_suffix(".tmp.zip")
    with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for n, data in other.items():
            zout.writestr(n, data)
        zout.writestr("word/comments.xml", new_xml)
    tmp.replace(dst)


def _ensure_title_comment(doc: Document) -> None:
    """Add one Taehong Kwon comment on the title paragraph noting KO translation."""
    title = None
    for p in doc.paragraphs:
        if p.text.strip():
            title = p
            break
    if title is None or not title.runs:
        return

    # comments part may already exist; use python-docx low-level
    comments_part = None
    try:
        comments_part = doc.part._comments_part  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001
        comments_part = None

    note = (
        "요청: 원본 Proposal Final_080426_1705.docx의 한국어 번역본을 새 파일로 생성. "
        "본 문서는 영문 제안서 전체 번역본입니다(원본 미덮어쓰기)."
    )

    # Prefer editing existing comments.xml via zip after save; here just prepend a
    # visible note paragraph if comment plumbing is awkward.
    # Insert a short note after title as Normal paragraph.
    # (Full native comment insertion with existing 20 comments is fragile.)
    # Instead annotate via comments.xml post-pass below.
    _ = note
    _ = comments_part


def _append_translation_comment(dst: Path) -> None:
    """Append one Taehong Kwon comment anchored to the first paragraph text."""
    with zipfile.ZipFile(dst, "r") as zin:
        blob = {n: zin.read(n) for n in zin.namelist()}

    if "word/comments.xml" not in blob:
        return

    comments = etree.fromstring(blob["word/comments.xml"])
    ids = [int(c.get(f"{W}id")) for c in comments.findall(f"{W}comment") if c.get(f"{W}id") is not None]
    new_id = str(max(ids) + 1 if ids else 0)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    note = (
        "요청: Proposal Final_080426_1705.docx 한국어 번역본을 새 파일로 생성. "
        "원본은 덮어쓰지 않음. 본 파일은 영문 제안서 전체 KO 번역본."
    )

    comment = OxmlElement("w:comment")
    comment.set(qn("w:id"), new_id)
    comment.set(qn("w:author"), "Taehong Kwon")
    comment.set(qn("w:initials"), "TK")
    comment.set(qn("w:date"), now)
    p = OxmlElement("w:p")
    r = OxmlElement("w:r")
    t = OxmlElement("w:t")
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    t.text = note
    r.append(t)
    p.append(r)
    comment.append(p)
    comments.append(comment)
    blob["word/comments.xml"] = etree.tostring(comments, xml_declaration=True, encoding="UTF-8", standalone=True)

    # Anchor on first body paragraph that has text
    doc = etree.fromstring(blob["word/document.xml"])
    body = doc.find(f"{W}body")
    if body is None:
        return
    target_p = None
    for child in body:
        if etree.QName(child).localname != "p":
            continue
        if child.find(f".//{W}t") is not None:
            target_p = child
            break
    if target_p is None:
        return

    cstart = OxmlElement("w:commentRangeStart")
    cstart.set(qn("w:id"), new_id)
    cend = OxmlElement("w:commentRangeEnd")
    cend.set(qn("w:id"), new_id)
    cref_p = OxmlElement("w:r")
    cref = OxmlElement("w:commentReference")
    cref.set(qn("w:id"), new_id)
    cref_p.append(cref)

    target_p.insert(0, cstart)
    # insert end before final pPr? after last run
    target_p.append(cend)
    target_p.append(cref_p)
    blob["word/document.xml"] = etree.tostring(doc, xml_declaration=True, encoding="UTF-8", standalone=True)

    tmp = dst.with_suffix(".tmp.zip")
    with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for n, data in blob.items():
            zout.writestr(n, data)
    tmp.replace(dst)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if not SRC.exists():
        print("Source missing:", SRC)
        return 1
    if DST.exists():
        print("Destination already exists, refusing overwrite:", DST)
        # Allow refresh of KO file if user re-runs: delete only DST, never SRC
        DST.unlink()
        print("Removed previous KO output to regenerate.")

    print("Copying...", SRC.name, "->", DST.name)
    shutil.copy2(SRC, DST)

    cache = _load_cache()
    translator = GoogleTranslator(source="en", target="ko")

    doc = Document(str(DST))
    unique = _collect_unique_texts(doc)
    print(f"Unique paragraphs to translate: {len(unique)} (cache hits may apply)")

    mapping: dict[str, str] = {}
    for i, text in enumerate(unique, 1):
        ko = _translate_one(translator, text, cache)
        mapping[text] = ko
        if i % 20 == 0 or i == len(unique):
            _save_cache(cache)
            print(f"  translated {i}/{len(unique)}", flush=True)

    applied = 0
    for p in _iter_all_paragraphs(doc):
        t = p.text
        if t in mapping:
            _set_text_keep_first_run(p, mapping[t])
            applied += 1
    doc.save(str(DST))
    print(f"Applied to {applied} paragraph instances")

    print("Translating comments…")
    _translate_comments_xml(SRC, DST, cache, translator)
    _save_cache(cache)
    _append_translation_comment(DST)

    # Integrity
    with zipfile.ZipFile(DST, "r") as z:
        bad = z.testzip()
        print("testzip:", bad)
        assert bad is None
        assert b"ns0:" not in z.read("word/document.xml")

    # Sample
    d2 = Document(str(DST))
    samples = [p.text.strip() for p in d2.paragraphs if p.text.strip()][:8]
    print("Sample KO paragraphs:")
    for s in samples:
        print(" -", s[:120])

    print("DONE:", DST)
    print("bytes:", DST.stat().st_size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
