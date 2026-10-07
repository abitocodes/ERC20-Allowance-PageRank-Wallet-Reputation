# -*- coding: utf-8 -*-
"""Re-anchor Word comments in Downloads/main.docx to match main.pdf highlights.

Reads highlight text from the annotated PDF, removes existing Word comments,
then wraps each comment around the matching phrase (not the whole paragraph).
"""
from __future__ import annotations

import re
import shutil
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import fitz
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from lxml import etree

PDF = Path(r"D:\Github\phd_works\1-Dissertation-Works\ERC20-Allowance-PageRank-Wallet-Reputation\proposal\proposal\main.pdf")
DOCX = Path(r"c:\Users\abito\Downloads\main.docx")
DOCX_OUT = Path(r"c:\Users\abito\Downloads\main.reanchored.docx")
BACKUP_IMG = Path(r"c:\Users\abito\Downloads\main.before-word-comments.docx")

AUTHOR = "Taehong Kwon"
INITIALS = "TK"
COMMENT_DATE = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
REL_COMMENTS = (
    "http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments"
)

# Fallback when PDF highlight text is too short / missing from DOCX (e.g. TOC "3.4").
# The converted DOCX omits TOC body lines, so the TOC comment is anchored to the
# "Table of Contents" heading (not the Section 3.4 body heading) to keep it distinct.
FALLBACK_PHRASE = {
    "Examiner comment 2: Table of contents updated for the new Section 3.4.": (
        "Table of Contents"
    ),
    "Examiner comments 1 to 3: Added the Human Passport (formerly Gitcoin Passport) developer "
    "documentation as the primary source for the Stamps, weighted score and threshold mechanism.": (
        "Human Passport developer documentation"
    ),
}


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def pdf_comment_targets() -> list[tuple[str, str]]:
    """Return [(highlight_phrase, comment_text), ...] from PDF Text+Highlight pairs."""
    doc = fitz.open(PDF)
    out: list[tuple[str, str]] = []
    for page in doc:
        highlights = [h for h in (page.annots() or []) if h.type[1] == "Highlight"]
        for a in page.annots() or []:
            if a.type[1] != "Text":
                continue
            content = (a.info.get("content") or "").strip()
            phrase = ""
            hl_rect = None
            for h in highlights:
                hc = (h.info.get("content") or "").strip()
                if hc[:60] == content[:60]:
                    phrase = page.get_textbox(h.rect).replace("\n", " ").strip()
                    phrase = re.sub(r"\s+", " ", phrase)
                    hl_rect = h.rect
                    break

            # Expand only short / page-number-glued highlights; leave long ones alone.
            words0 = (phrase or "").split()
            already_good = bool(
                re.search(r"\(\d{4}\)|\(n\.d\.\)|documentation\.?$|et al\.", phrase or "", re.I)
            ) or (
                len(words0) >= 4 and not re.match(r"^\d+\s", phrase or "")
                and not phrase.rstrip().endswith((" in", " the", " a", " to", " for", " and", " of"))
            )
            if hl_rect is not None and not already_good and (
                len(norm(phrase)) < 45
                or re.match(r"^\d+\s", phrase or "")
                or phrase.rstrip().endswith((" in", " the", " a", " to", " for", " and", " of"))
            ):
                clip = fitz.Rect(
                    50,
                    max(0, hl_rect.y0 - 2),
                    page.rect.width - 40,
                    min(page.rect.height, hl_rect.y1 + 16),
                )
                line = page.get_text("text", clip=clip).replace("\n", " ").strip()
                line = re.sub(r"\s+", " ", line)
                line = re.sub(r"^\d{1,2}\s+(?=[A-Za-z])", "", line)
                key = re.sub(r"^\d{1,2}\s+", "", phrase or "").strip()
                if key and key.lower() in line.lower():
                    idx = line.lower().find(key.lower())
                    phrase = line[idx:]
                elif line:
                    phrase = line
                words = phrase.split()
                phrase = " ".join(words[:12])

            if not phrase:
                phrase = FALLBACK_PHRASE.get(content, "")
            if len(norm(phrase)) < 8 and content in FALLBACK_PHRASE:
                phrase = FALLBACK_PHRASE[content]

            out.append((phrase, content))
    return out


def ensure_comments_part(docx_path: Path) -> None:
    tmp = docx_path.with_suffix(".comments_tmp.docx")
    with zipfile.ZipFile(docx_path, "r") as zin, zipfile.ZipFile(
        tmp, "w", compression=zipfile.ZIP_DEFLATED
    ) as zout:
        names = set(zin.namelist())
        ct = etree.fromstring(zin.read("[Content_Types].xml"))
        rels = etree.fromstring(zin.read("word/_rels/document.xml.rels"))

        if not any(el.get("PartName") == "/word/comments.xml" for el in ct):
            etree.SubElement(
                ct,
                f"{{{CT_NS}}}Override",
                PartName="/word/comments.xml",
                ContentType=(
                    "application/vnd.openxmlformats-officedocument"
                    ".wordprocessingml.comments+xml"
                ),
            )
        if not any(el.get("Type") == REL_COMMENTS for el in rels):
            used = {el.get("Id") for el in rels}
            rid = "rIdComments"
            n = 90
            while rid in used:
                rid = f"rId{n}"
                n += 1
            etree.SubElement(
                rels,
                f"{{{REL_NS}}}Relationship",
                Id=rid,
                Type=REL_COMMENTS,
                Target="comments.xml",
            )

        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "[Content_Types].xml":
                data = etree.tostring(
                    ct, xml_declaration=True, encoding="UTF-8", standalone=True
                )
            elif item.filename == "word/_rels/document.xml.rels":
                data = etree.tostring(
                    rels, xml_declaration=True, encoding="UTF-8", standalone=True
                )
            elif item.filename == "word/comments.xml":
                continue
            zout.writestr(item, data)

        if "word/comments.xml" not in names:
            comments = etree.Element(f"{{{W_NS}}}comments", nsmap={"w": W_NS})
            zout.writestr(
                "word/comments.xml",
                etree.tostring(
                    comments, xml_declaration=True, encoding="UTF-8", standalone=True
                ),
            )
    shutil.move(str(tmp), str(docx_path))


def clear_existing_word_comments(docx_path: Path) -> None:
    """Remove comment markers from document.xml and empty comments.xml."""
    tmp = docx_path.with_suffix(".clear_tmp.docx")
    with zipfile.ZipFile(docx_path, "r") as zin, zipfile.ZipFile(
        tmp, "w", compression=zipfile.ZIP_DEFLATED
    ) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "word/document.xml":
                root = etree.fromstring(data)
                for tag in (
                    "commentRangeStart",
                    "commentRangeEnd",
                    "commentReference",
                ):
                    for el in list(root.findall(f".//{{{W_NS}}}{tag}")):
                        parent = el.getparent()
                        if parent is None:
                            continue
                        # commentReference lives inside a w:r — remove the whole run if it only holds the ref
                        if tag == "commentReference" and etree.QName(parent).localname == "r":
                            grand = parent.getparent()
                            if grand is not None:
                                grand.remove(parent)
                            continue
                        parent.remove(el)
                data = etree.tostring(
                    root, xml_declaration=True, encoding="UTF-8", standalone=True
                )
            elif item.filename == "word/comments.xml":
                comments = etree.Element(f"{{{W_NS}}}comments", nsmap={"w": W_NS})
                data = etree.tostring(
                    comments, xml_declaration=True, encoding="UTF-8", standalone=True
                )
            zout.writestr(item, data)
    shutil.move(str(tmp), str(docx_path))


def add_comment_element(comments_root, cid: int, text: str) -> None:
    c = OxmlElement("w:comment")
    c.set(qn("w:id"), str(cid))
    c.set(qn("w:author"), AUTHOR)
    c.set(qn("w:date"), COMMENT_DATE)
    c.set(qn("w:initials"), INITIALS)
    p = OxmlElement("w:p")
    ref_run = OxmlElement("w:r")
    ref_run.append(OxmlElement("w:annotationRef"))
    p.append(ref_run)
    run = OxmlElement("w:r")
    t = OxmlElement("w:t")
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    t.text = text
    run.append(t)
    p.append(run)
    c.append(p)
    comments_root.append(c)


def plain_paragraph_text(paragraph) -> str:
    parts = []
    for node in paragraph._p.iter():
        if etree.QName(node).localname != "t":
            continue
        ancestors = {etree.QName(a).localname for a in node.iterancestors()}
        if ancestors & {"drawing", "txbxContent", "pict", "wsp", "shape"}:
            continue
        if node.text:
            parts.append(node.text)
    return "".join(parts)


def clean_phrase(phrase: str) -> str:
    """Drop PDF artifacts (page numbers glued to highlight text, leading section nos)."""
    phrase = re.sub(r"\s+", " ", phrase).strip()
    # e.g. "3 nor the attestation-based" from a page-number digit beside the line
    phrase = re.sub(r"^\d{1,2}\s+(?=[A-Za-z])", "", phrase)
    # PDF sometimes splits "3.4" as "3 4"
    phrase = re.sub(r"\bSection\s+(\d)\s+(\d)\b", r"Section \1.\2", phrase)
    phrase = re.sub(r"\b(\d)\s+(\d)\b(?=\s+[A-Z])", r"\1.\2", phrase)
    return phrase.strip(" .;:")


def phrase_candidates(phrase: str, content: str) -> list[str]:
    """Ordered list of phrases to try when locating the anchor in the DOCX."""
    out: list[str] = []
    for key, fb in FALLBACK_PHRASE.items():
        if content.startswith(key[:40]) or key.startswith(content[:40]):
            out.append(fb)
    cleaned = clean_phrase(phrase)
    if cleaned:
        out.append(cleaned)
    # Without leading "N.N " section number
    stripped = re.sub(r"^\d+\.\d+\s+", "", cleaned)
    if stripped and stripped not in out:
        out.append(stripped)
    # Without trailing dotted leaders / URL tails from TOC/bibliography lines
    no_leaders = re.sub(r"\s*\.{2,}.*$", "", stripped or cleaned).strip()
    if no_leaders and no_leaders not in out:
        out.append(no_leaders)
    no_url = re.sub(
        r"\s+(https?://\S+|docs\.\S+).*$",
        "",
        stripped or cleaned,
        flags=re.I,
    ).strip()
    if no_url and no_url not in out:
        out.append(no_url)
    # First sentence only (bibliography lines often continue into the next entry)
    first_sent = re.split(r"(?<=\.)\s+(?=[A-Z])", no_url or cleaned, maxsplit=1)[0].strip()
    if first_sent and first_sent not in out:
        out.append(first_sent)
    # First N words for long bibliography lines
    words = (first_sent or no_url or stripped or cleaned).split()
    if len(words) > 8:
        out.append(" ".join(words[:8]))
    if phrase and phrase not in out:
        out.append(phrase)
    seen = set()
    uniq = []
    for p in out:
        key = norm(p)
        if not key or key in seen:
            continue
        seen.add(key)
        uniq.append(p)
    return uniq


def find_paragraph(paragraphs, phrase: str) -> int:
    needle = norm(phrase)
    if not needle:
        raise ValueError("Empty phrase")
    hits = [
        i
        for i, p in enumerate(paragraphs)
        if needle in norm(plain_paragraph_text(p))
    ]
    if not hits:
        words = phrase.split()
        for k in range(len(words), 2, -1):
            sub = norm(" ".join(words[:k]))
            if len(sub) < 12:
                break
            hits = [
                i
                for i, p in enumerate(paragraphs)
                if sub in norm(plain_paragraph_text(p))
            ]
            if len(hits) == 1:
                return hits[0]
            if hits:
                break
        raise ValueError(f"Phrase not found in DOCX: {phrase!r}")
    if len(hits) == 1:
        return hits[0]
    # Prefer the earliest occurrence (PDF reading order), not the shortest para.
    return hits[0]


def iter_text_runs(paragraph):
    """Yield (run_element, text) for body text runs only."""
    for child in list(paragraph._p):
        if etree.QName(child).localname != "r":
            continue
        # skip runs that only contain drawings
        has_drawing = any(
            etree.QName(c).localname in ("drawing", "pict", "AlternateContent", "object")
            for c in child
        )
        t_el = child.find(qn("w:t"))
        if t_el is None:
            continue
        if has_drawing:
            continue
        yield child, t_el.text or ""


def split_run(run_el, at: int):
    """Split run_el so left keeps text[:at], right gets text[at:]. Returns right run."""
    t_el = run_el.find(qn("w:t"))
    text = t_el.text or ""
    if at <= 0 or at >= len(text):
        return None
    left, right = text[:at], text[at:]
    t_el.text = left
    if left.startswith(" ") or left.endswith(" ") or "  " in left:
        t_el.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")

    new_run = OxmlElement("w:r")
    rPr = run_el.find(qn("w:rPr"))
    if rPr is not None:
        new_run.append(etree.fromstring(etree.tostring(rPr)))
    new_t = OxmlElement("w:t")
    if right.startswith(" ") or right.endswith(" ") or "  " in right:
        new_t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    new_t.text = right
    new_run.append(new_t)
    run_el.addnext(new_run)
    return new_run


def wrap_phrase_comment(paragraph, phrase: str, cid: int) -> str:
    """Wrap comment markers around the first occurrence of phrase in paragraph.

    Matching ignores spaces/punct differences by locating the phrase in the
    concatenated run texts via a space-flexible regex built from the phrase.
    Returns the actual matched substring.
    """
    runs = list(iter_text_runs(paragraph))
    if not runs:
        raise ValueError(f"No text runs in paragraph for phrase {phrase!r}")

    full = "".join(text for _, text in runs)

    # Build a regex that allows flexible whitespace between words of phrase
    words = [re.escape(w) for w in phrase.split() if w]
    if not words:
        raise ValueError(f"Empty phrase words: {phrase!r}")
    pattern = r"\s*".join(words)
    m = re.search(pattern, full, flags=re.IGNORECASE)
    if not m:
        raise ValueError(
            f"Phrase not found inside chosen paragraph: {phrase!r} / para={full[:120]!r}"
        )

    start, end = m.start(), m.end()
    matched = full[start:end]

    # Build absolute offsets for each run
    offsets = []
    pos = 0
    for run_el, text in runs:
        offsets.append((run_el, pos, pos + len(text), text))
        pos += len(text)

    # Split runs at start and end boundaries so markers sit cleanly between runs
    # Work from end to start so earlier offsets stay valid within each run after later splits...
    # Actually splitting changes the run list. Do start first, then recompute for end.

    def locate(abs_pos: int):
        for run_el, a, b, text in offsets:
            if a <= abs_pos < b or (abs_pos == b == offsets[-1][2] and abs_pos == b):
                return run_el, abs_pos - a
            if abs_pos == b and abs_pos < offsets[-1][2]:
                # boundary: belongs to next run start
                continue
        # end-of-text
        run_el, a, b, text = offsets[-1]
        return run_el, len(text)

    # Split at end first (higher index), then start
    run_end, off_end = locate(end)
    if 0 < off_end < len(run_end.find(qn("w:t")).text or ""):
        split_run(run_end, off_end)

    # rebuild offsets after end split
    runs = list(iter_text_runs(paragraph))
    offsets = []
    pos = 0
    for run_el, text in runs:
        offsets.append((run_el, pos, pos + len(text), text))
        pos += len(text)

    run_start, off_start = locate(start)
    if 0 < off_start < len(run_start.find(qn("w:t")).text or ""):
        right = split_run(run_start, off_start)
        # the phrase now starts at `right` (or next)
        start_run = right if right is not None else run_start
    else:
        start_run = run_start if off_start == 0 else run_start

    # rebuild again
    runs = list(iter_text_runs(paragraph))
    offsets = []
    pos = 0
    for run_el, text in runs:
        offsets.append((run_el, pos, pos + len(text), text))
        pos += len(text)

    # find runs covering [start, end)
    cover = []
    for run_el, a, b, text in offsets:
        if b <= start:
            continue
        if a >= end:
            break
        cover.append(run_el)
    if not cover:
        raise ValueError(f"No covered runs for {phrase!r}")

    first, last = cover[0], cover[-1]

    start_mark = OxmlElement("w:commentRangeStart")
    start_mark.set(qn("w:id"), str(cid))
    end_mark = OxmlElement("w:commentRangeEnd")
    end_mark.set(qn("w:id"), str(cid))
    ref_run = OxmlElement("w:r")
    ref = OxmlElement("w:commentReference")
    ref.set(qn("w:id"), str(cid))
    ref_run.append(ref)

    first.addprevious(start_mark)
    last.addnext(end_mark)
    end_mark.addnext(ref_run)
    return matched


def main() -> None:
    target = DOCX
    if not target.is_file():
        raise SystemExit(f"Missing {target}")
    if not PDF.is_file():
        raise SystemExit(f"Missing {PDF}")

    # If main.docx is locked (open in Word), work on a copy.
    work = DOCX
    try:
        with open(DOCX, "a"):
            pass
    except PermissionError:
        shutil.copy2(DOCX, DOCX_OUT)
        work = DOCX_OUT
        print(f"{DOCX} is locked; writing to {DOCX_OUT}")

    targets = pdf_comment_targets()
    print(f"Loaded {len(targets)} PDF comment targets")
    for i, (phrase, content) in enumerate(targets):
        print(f"  [{i}] phrase={phrase[:70]!r}")
        print(f"       comment={content[:70]}")

    ensure_comments_part(work)
    clear_existing_word_comments(work)
    ensure_comments_part(work)

    doc = Document(str(work))
    comments_part = None
    for rel in doc.part.rels.values():
        if rel.reltype == REL_COMMENTS:
            comments_part = rel.target_part
            break
    if comments_part is None:
        raise SystemExit("comments part missing")

    comments_root = comments_part.element
    for old in list(comments_root.findall(qn("w:comment"))):
        comments_root.remove(old)

    for cid, (phrase, content) in enumerate(targets):
        candidates = phrase_candidates(phrase, content)
        last_err: Exception | None = None
        matched = None
        idx = None
        used = None
        for cand in candidates:
            try:
                idx = find_paragraph(doc.paragraphs, cand)
                matched = wrap_phrase_comment(doc.paragraphs[idx], cand, cid)
                used = cand
                break
            except ValueError as exc:
                last_err = exc
                continue
        if matched is None or idx is None:
            raise SystemExit(
                f"[{cid}] could not place comment. tried={candidates!r} last={last_err}"
            )
        add_comment_element(comments_root, cid, content)
        print(f"  [{cid}] p{idx} used={used[:70]!r} matched={matched[:70]!r}")

    try:
        doc.save(str(work))
    except PermissionError:
        alt = work.with_name(work.stem + ".new.docx")
        doc.save(str(alt))
        work = alt
        print(f"PermissionError; saved to {alt}")

    with zipfile.ZipFile(work) as z:
        assert z.testzip() is None
        root = etree.fromstring(z.read("word/document.xml"))
        comments = etree.fromstring(z.read("word/comments.xml"))
        found = comments.findall(qn("w:comment"))
        starts = root.findall(".//" + qn("w:commentRangeStart"))
        refs = root.findall(".//" + qn("w:commentReference"))
        authors = {c.get(qn("w:author")) for c in found}

    if len(found) != len(targets):
        raise SystemExit(f"comment count {len(found)} != {len(targets)}")
    if len(starts) != len(refs) or len(starts) != len(targets):
        raise SystemExit(f"anchor mismatch start={len(starts)} ref={len(refs)}")
    if authors != {AUTHOR}:
        raise SystemExit(f"authors={authors}")

    print(f"Done: {len(found)} phrase-anchored Word comments in {work}")


if __name__ == "__main__":
    sys.exit(main())
