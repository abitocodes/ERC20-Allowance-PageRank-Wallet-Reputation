# -*- coding: utf-8 -*-
"""Annotate proposal/main.pdf with Taehong Kwon comments for each examiner correction.

Highlights the corrected passage and attaches a Text annotation (sticky note)
readable in Acrobat, Edge, Chrome, SumatraPDF, etc.
"""
from __future__ import annotations

import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parent.parent
PDF = ROOT / "proposal" / "main.pdf"
BACKUP = ROOT / "proposal" / "main.pre-annot.pdf"

AUTHOR = "Taehong Kwon"

# (anchor, occurrence, comment). occurrence: "only" | "first" | "last".
ANNOTATIONS: list[tuple[str, str, str]] = [
    (
        "3.4 Attestation-Based Reputation Tooling in Deployed DeFi Systems",
        "first",
        "Examiner comment 2: Table of contents updated for the new Section 3.4.",
    ),
    (
        "Attestation-based reputation: A wallet score obtained by aggregating weighted credentials",
        "only",
        "Examiner comments 1 and 3: Added a definition of attestation-based reputation, so that the way "
        "trust is normally established in a DeFi system (Gitcoin / Human Passport and comparable tooling) "
        "is defined before EndorseRank is introduced.",
    ),
    (
        "Sybil attack: The creation of many illegitimate identities",
        "only",
        "Examiner comment 3: Added a definition of Sybil attack, since Passport-style scoring exists "
        "primarily to address Sybil attacks.",
    ),
    (
        "In current practice, trust in a DeFi setting is established in two broad ways",
        "only",
        "Examiner comments 1 and 2: New paragraph stating how trust is normally established in a DeFi "
        "system: consistent, transparent on-chain activity that is costly to manipulate, and attestation "
        "tooling such as Human Passport (formerly Gitcoin Passport) that combines on-chain and off-chain "
        "data against a passing threshold. It also notes that both mechanisms decide admission rather "
        "than order wallets by financial reliability, and points to the new Section 3.4.",
    ),
    (
        "nor the attestation-based tooling reviewed in Section",
        "only",
        "Examiner comment 2: The novelty claim is no longer an unqualified 'no existing study'. It now "
        "states precisely what the graph-based literature and the deployed attestation tooling each do "
        "not do, so the contribution of EndorseRank is legible against both.",
    ),
    (
        "A third consideration concerns the reputation tooling already deployed",
        "only",
        "Examiner comment 2: The research problem now positions EndorseRank against Passport-style "
        "tooling, distinguishing an admission gate from a graded ordering of wallets.",
    ),
    (
        "Can EndorseRank, a Weighted PageRank computed over ERC-20 allowance",
        "only",
        "Examiner comment 4: Main research question shortened from 65 words to 28. The setting, "
        "perspective, comparison baselines and evaluation criteria were removed from the sentence itself.",
    ),
    (
        "The setting, perspective, comparison baselines, and evaluation criteria",
        "only",
        "Examiner comment 4: The side conditions removed from the research question are carried by the "
        "SPICE table immediately below, so no information is lost.",
    ),
    (
        "Because trust in operational DeFi systems is established not only",
        "only",
        "Examiner comment 2: Section 3.3 now points forward to Section 3.4, so the gap statement is read "
        "against deployed practice and not only against the scholarly literature.",
    ),
    (
        "3.4 Attestation-Based Reputation Tooling in Deployed DeFi Systems",
        "last",
        "Examiner comments 1 to 3: New Section 3.4 reviews the reputational tooling actually used in DeFi, "
        "with Gitcoin / Human Passport as the primary case: Stamps as weighted verifiable credentials, a "
        "score compared against a passing threshold, and optional on-chain attestation via the Ethereum "
        "Attestation Service. Sources: Human Passport (n.d.); Bordeianu and Popescu (2026), Applied "
        "Sciences 16(14), 6929; Siddarth et al. (2020), Frontiers in Blockchain 3, 590171; Buterin et al. "
        "(2019), Management Science 65(11).",
    ),
    (
        "Two properties of this design bear directly on the present study",
        "only",
        "Examiner comment 3: States explicitly that Passport considers both on-chain and off-chain data to "
        "calculate a trust score addressing Sybil attacks, and that the result functions as a threshold "
        "gate rather than as a ranking. Credential farming is recorded as its residual weakness.",
    ),
    (
        "EndorseRank is therefore neither a competitor to nor a replacement",
        "only",
        "Examiner comment 2: The original contribution is now stated as an explicit five-way contrast with "
        "Passport-style tooling: signal source, data scope, question answered, output form and validation "
        "target. This is the passage that answers 'how will EndorseRank make a novel contribution'.",
    ),
    (
        "In summary, the literature shows a progression",
        "only",
        "Examiner comment 2: Chapter summary rewritten so that attestation-based tooling sits alongside the "
        "graph-based and machine-learning strands, and the remaining gap is stated across all three.",
    ),
    (
        "No Personhood Layer: EndorseRank is computed entirely from on-chain state",
        "only",
        "Examiner comment 3: Limitation added. EndorseRank uses no off-chain evidence and therefore offers "
        "no personhood guarantee of its own; it is a relational ordering over an already admitted population.",
    ),
    (
        "Untested Composition: Because a personhood gate and a relational ranking",
        "only",
        "Examiner comment 3: Limitation added. Combining a Passport-style personhood gate with EndorseRank "
        "is a plausible deployment pattern but is left to future work, and credential farming would carry "
        "over to that composition.",
    ),
    (
        "A Distinct Contribution Relative to Attestation-Based Tooling",
        "only",
        "Examiner comment 2: The significance chapter now states the original contribution relative to "
        "attestation-based tooling: delegation treated as a measurable, rankable trust relation.",
    ),
    (
        "Bordeianu, A. A., & Popescu, D. E. (2026)",
        "only",
        "Examiner comments 2 and 3: Added Bordeianu and Popescu (2026), Applied Sciences 16(14), 6929, a "
        "peer-reviewed comparative analysis that covers Gitcoin's Human Passport. DOI verified against "
        "Crossref: 10.3390/app16146929.",
    ),
    (
        "Buterin, V., Hitzig, Z., & Weyl, E. G. (2019)",
        "only",
        "Examiner comment 2: Added Buterin, Hitzig and Weyl (2019), Management Science 65(11), 5171-5187, "
        "for the quadratic-funding setting that Passport was built to protect. DOI verified against "
        "Crossref: 10.1287/mnsc.2019.3337.",
    ),
    (
        "Human Passport developer documentation",
        "only",
        "Examiner comments 1 to 3: Added the Human Passport (formerly Gitcoin Passport) developer "
        "documentation as the primary source for the Stamps, weighted score and threshold mechanism.",
    ),
    (
        "Siddarth, D., Ivliev, S., Siri, S., & Berman, P. (2020)",
        "only",
        "Examiner comment 3: Added Siddarth et al. (2020), Frontiers in Blockchain 3, 590171, a "
        "peer-reviewed review of Sybil-resistant proof-of-personhood protocols. DOI verified against "
        "Crossref: 10.3389/fbloc.2020.590171.",
    ),
]


def find_hits(doc: fitz.Document, anchor: str) -> list[tuple[int, fitz.Rect]]:
    hits: list[tuple[int, fitz.Rect]] = []
    for i in range(doc.page_count):
        for rect in doc[i].search_for(anchor):
            hits.append((i, rect))
    return hits


def resolve(
    doc: fitz.Document, anchor: str, occurrence: str
) -> tuple[int, fitz.Rect]:
    hits = find_hits(doc, anchor)
    if not hits:
        raise SystemExit(f"Anchor not found in PDF: {anchor!r}")
    if occurrence == "first":
        return hits[0]
    if occurrence == "last":
        return hits[-1]
    # "only": prefer a single page with one hit; otherwise require uniqueness.
    pages = {p for p, _ in hits}
    if len(hits) == 1:
        return hits[0]
    # Prefer body hits over TOC: take the last occurrence when TOC also matches.
    if occurrence == "only" and len(pages) > 1:
        return hits[-1]
    if len(hits) > 1 and all(p == hits[0][0] for p, _ in hits):
        # Same page, multiple rects (line wrap): use the first rect on that page.
        return hits[0]
    raise SystemExit(f"Anchor ambiguous ({hits}): {anchor!r}")


def clear_existing_annots(doc: fitz.Document) -> int:
    removed = 0
    for page in doc:
        annots = list(page.annots() or [])
        for annot in annots:
            page.delete_annot(annot)
            removed += 1
    return removed


def add_comment(
    page: fitz.Page, rect: fitz.Rect, comment: str, stamp: str
) -> None:
    # Yellow highlight over the matched passage.
    highlight = page.add_highlight_annot(rect)
    highlight.set_colors(stroke=(1, 0.85, 0.2))
    highlight.set_opacity(0.35)
    highlight.set_info(
        title=AUTHOR,
        content=comment,
        subject="Examiner correction",
        creationDate=stamp,
        modDate=stamp,
    )
    highlight.update()

    # Sticky-note icon at the right margin, aligned with the highlighted line.
    point = fitz.Point(min(page.rect.width - 28, rect.x1 + 6), rect.y0)
    note = page.add_text_annot(point, comment, icon="Comment")
    note.set_info(
        title=AUTHOR,
        content=comment,
        subject="Examiner correction",
        creationDate=stamp,
        modDate=stamp,
    )
    note.set_colors(stroke=(1, 0.85, 0.2))
    note.update()


def main() -> None:
    if not PDF.is_file():
        raise SystemExit(f"Missing {PDF}. Run proposal/build.ps1 first.")

    # Prefer a freshly built PDF. Refresh the clean backup only when the current
    # PDF has no annotations (i.e. just came from XeLaTeX), otherwise restore
    # from backup so re-runs are idempotent.
    if BACKUP.is_file():
        probe = fitz.open(PDF)
        has_annots = any(list(p.annots() or []) for p in probe)
        probe.close()
        if has_annots:
            shutil.copy2(BACKUP, PDF)
        else:
            shutil.copy2(PDF, BACKUP)
    else:
        shutil.copy2(PDF, BACKUP)

    try:
        doc = fitz.open(PDF)
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(f"Cannot open {PDF}: {exc}") from exc

    # Drop any leftover annotations before re-applying.
    cleared = clear_existing_annots(doc)
    if cleared:
        print(f"Cleared {cleared} existing annotation(s)")

    stamp = datetime.now(timezone.utc).strftime("D:%Y%m%d%H%M%SZ")
    placed: list[tuple[int, str]] = []

    for anchor, occurrence, comment in ANNOTATIONS:
        page_i, rect = resolve(doc, anchor, occurrence)
        add_comment(doc[page_i], rect, comment, stamp)
        placed.append((page_i + 1, anchor[:60]))
        print(f"  [pdf p{page_i + 1}] {anchor[:60]}")

    tmp = PDF.with_suffix(".annotating.pdf")
    try:
        doc.save(tmp, garbage=4, deflate=True)
        doc.close()
        shutil.move(str(tmp), str(PDF))
    except PermissionError:
        doc.close()
        if tmp.exists():
            tmp.unlink(missing_ok=True)
        raise SystemExit(
            f"{PDF} is open in a PDF viewer. Close it and re-run; nothing was written."
        )

    # Verify
    check = fitz.open(PDF)
    annots = []
    authors = set()
    for page in check:
        for annot in page.annots() or []:
            info = annot.info
            authors.add(info.get("title") or "")
            annots.append((page.number + 1, annot.type[1], info.get("content", "")[:80]))
    check.close()

    expected = len(ANNOTATIONS) * 2  # highlight + sticky note each
    if len(annots) != expected:
        raise SystemExit(f"Expected {expected} annotations, found {len(annots)}")
    if authors != {AUTHOR}:
        raise SystemExit(f"Unexpected annotation authors: {authors}")

    print(f"Annotated {PDF} with {len(ANNOTATIONS)} comments ({expected} annotations) by {AUTHOR}")
    for page, label in placed:
        print(f"  page {page}: {label}")


if __name__ == "__main__":
    sys.exit(main())
