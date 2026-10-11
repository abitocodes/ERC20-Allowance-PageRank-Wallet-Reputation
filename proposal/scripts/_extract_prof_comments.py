"""Extract professor comments with anchor text from commented DOCX."""

from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W_NS = f"{{{W}}}"


def para_text(p: ET.Element) -> str:
    parts: list[str] = []
    for t in p.iter(f"{W_NS}t"):
        if t.text:
            parts.append(t.text)
        if t.tail:
            parts.append(t.tail)
    return re.sub(r"\s+", " ", "".join(parts)).strip()


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    path = Path(r"D:\Github\phd_works\sources\professor-feedback\dissertation-proposal-commented.docx")
    with zipfile.ZipFile(path) as zf:
        doc = ET.fromstring(zf.read("word/document.xml"))
        comments_root = ET.fromstring(zf.read("word/comments.xml"))

    comments: dict[str, dict] = {}
    for c in comments_root.findall(f".//{W_NS}comment"):
        cid = c.get(f"{W_NS}id")
        parts: list[str] = []
        for t in c.iter(f"{W_NS}t"):
            if t.text:
                parts.append(t.text)
            if t.tail:
                parts.append(t.tail)
        comments[cid] = {
            "author": c.get(f"{W_NS}author"),
            "text": re.sub(r"\s+", " ", "".join(parts)).strip(),
            "anchor": "",
        }

    for p in doc.iter(f"{W_NS}p"):
        in_comment: dict[str, list[str]] = {}
        for child in p:
            tag = child.tag.split("}")[-1]
            if tag == "commentRangeStart":
                cid = child.get(f"{W_NS}id")
                in_comment[cid] = []
            elif tag == "commentRangeEnd":
                cid = child.get(f"{W_NS}id")
                if cid in comments and in_comment.get(cid):
                    comments[cid]["anchor"] = " ".join(in_comment[cid]).strip()[:260]
                in_comment.pop(cid, None)
            elif tag == "r":
                run_parts: list[str] = []
                for t in child.iter(f"{W_NS}t"):
                    if t.text:
                        run_parts.append(t.text)
                    if t.tail:
                        run_parts.append(t.tail)
                run_text = "".join(run_parts)
                for cid in in_comment:
                    in_comment[cid].append(run_text)

    prof_authors = {"Mnkandla, Ernest", "Moulla, Donatien Koulla", "Attipoe, David Sena"}
    ordered = sorted(comments.items(), key=lambda x: int(x[0]))
    prof = [(cid, c) for cid, c in ordered if c["author"] in prof_authors]
    print(f"PROF_TOTAL={len(prof)}")
    for i, (cid, c) in enumerate(prof, 1):
        print(f"### {i} [{c['author']}] ###")
        print(f"ANCHOR: {c['anchor']}")
        print(f"COMMENT: {c['text']}")
        print()


if __name__ == "__main__":
    main()
