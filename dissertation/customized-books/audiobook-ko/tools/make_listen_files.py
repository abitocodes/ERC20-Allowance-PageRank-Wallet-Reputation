#!/usr/bin/env python3
"""Bundle the scripts into files a read-aloud app can import.

usage: make_listen_files.py

Writes listen/audiobook-ko.epub (one chapter per script, with a table of
contents) and listen/audiobook-ko.txt. Numbers are already spelled out in
Korean (tools/normalize.py), so any phone voice reads them the same way.
"""
import html
import re
import uuid
import zipfile
from pathlib import Path

from normalize import segments

ROOT = Path(__file__).resolve().parent.parent
TITLE = "ERC-20 허락 화살표를 페이지랭크에 넣어 온체인 지갑 평판 점수를 더 좋게 만들기: 오디오북 대본(듣기용)"
AUTHOR = "권태홍"


def chapters():
    for f in sorted((ROOT / "script").glob("0*.md")):
        raw = f.read_text(encoding="utf-8")
        heads = [(len(m.group(1)), m.group(2).strip()) for m in re.finditer(r"^(#{1,4})\s*(.+)$", raw, flags=re.M)]
        yield f.stem, heads, list(segments(raw))


def xhtml(title, body):
    return ('<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE html>\n'
            '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="ko" xml:lang="ko">\n'
            f"<head><meta charset=\"utf-8\"/><title>{html.escape(title)}</title></head>\n<body>\n{body}\n</body>\n</html>\n")


def main():
    out = ROOT / "listen"
    out.mkdir(exist_ok=True)
    chs = list(chapters())

    # plain text
    lines = [TITLE, f"지은이 {AUTHOR}", ""]
    for _, _, segs in chs:
        for kind, text in segs:
            lines += [text, ""]
        lines.append("")
    (out / "audiobook-ko.txt").write_text("\n".join(lines), encoding="utf-8")

    # EPUB 3
    book_id = "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_URL, "phd_works/audiobook-ko"))
    epub = out / "audiobook-ko.epub"
    with zipfile.ZipFile(epub, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml",
                   '<?xml version="1.0" encoding="utf-8"?>\n<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
                   '<rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>\n',
                   compress_type=zipfile.ZIP_DEFLATED)
        manifest, spine, nav = [], [], []
        for i, (stem, heads, segs) in enumerate(chs, 1):
            name = f"ch{i:02d}.xhtml"
            body, n = [], 0
            sub = []
            for kind, text in segs:
                if kind.startswith("h"):
                    n += 1
                    level = int(kind[1])
                    body.append(f'<h{level} id="s{n}">{html.escape(text)}</h{level}>')
                    if level == 2 and n - 1 < len(heads):
                        sub.append(f'<li><a href="{name}#s{n}">{html.escape(heads[n - 1][1])}</a></li>')
                else:
                    body.append(f"<p>{html.escape(text)}</p>")
            title = heads[0][1] if heads else stem
            z.writestr(f"OEBPS/{name}", xhtml(title, "\n".join(body)), compress_type=zipfile.ZIP_DEFLATED)
            manifest.append(f'<item id="c{i}" href="{name}" media-type="application/xhtml+xml"/>')
            spine.append(f'<itemref idref="c{i}"/>')
            inner = f"<ol>{''.join(sub)}</ol>" if sub else ""
            nav.append(f'<li><a href="{name}">{html.escape(title)}</a>{inner}</li>')
        z.writestr("OEBPS/nav.xhtml", xhtml("차례", '<nav epub:type="toc" id="toc"><h1>차례</h1><ol>' + "".join(nav) + "</ol></nav>"),
                   compress_type=zipfile.ZIP_DEFLATED)
        opf = ('<?xml version="1.0" encoding="utf-8"?>\n'
               '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" xml:lang="ko">\n'
               '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">'
               f'<dc:identifier id="bookid">{book_id}</dc:identifier><dc:title>{html.escape(TITLE)}</dc:title>'
               f'<dc:creator>{AUTHOR}</dc:creator><dc:language>ko</dc:language>'
               '<meta property="dcterms:modified">2026-10-04T00:00:00Z</meta></metadata>\n'
               '<manifest><item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>'
               + "".join(manifest) + "</manifest>\n<spine>" + "".join(spine) + "</spine>\n</package>\n")
        z.writestr("OEBPS/content.opf", opf, compress_type=zipfile.ZIP_DEFLATED)
    print(epub, epub.stat().st_size, "bytes;", out / "audiobook-ko.txt")


if __name__ == "__main__":
    main()
