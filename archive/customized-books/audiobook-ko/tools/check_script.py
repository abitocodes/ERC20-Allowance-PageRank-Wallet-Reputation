#!/usr/bin/env python3
"""Check an audiobook script against SCRIPT-GUIDE.md and its translated source.

usage: check_script.py SCRIPT.md SOURCE.tex [SOURCE.tex ...]

Reports what a text-to-speech voice cannot read well (LaTeX, Latin letters,
symbols, numbered cross-references, small native counts written as digits),
sentences that do not end in 해요체, and source headings that have no
matching heading in the script. Exit code 0 when no problem is found.
"""
import re
import sys
from pathlib import Path

BR = r"\{((?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*)\}"


def source_headings(paths):
    out = []
    for p in paths:
        s = Path(p).read_text(encoding="utf-8")
        s = "\n".join(re.sub(r"(?<!\\)%.*", "", l) for l in s.split("\n"))
        pat = r"\\(chapter\*?|section\*?|dissertationSubheading|dissertationSubsubheading)(?:\[[^\]]*\])?\s*" + BR
        for m in re.finditer(pat, s):
            out.append((m.group(1), m.group(2)))
    return out


def hangul_set(t):
    t = re.sub(r"\\texorpdfstring\{[^}]*\}\{([^}]*)\}", r"\1", t)
    t = re.sub(r"\$[^$]*\$", " ", t)
    return set(re.findall(r"[가-힣0-9]", t))


def main():
    script_path, sources = sys.argv[1], sys.argv[2:]
    text = Path(script_path).read_text(encoding="utf-8")
    lines = text.split("\n")
    body = [l for l in lines if not l.startswith("#")]
    body_text = "\n".join(body)
    problems = []

    def report(name, items):
        if items:
            ex = " || ".join(items[:6])
            problems.append(f"[{name}] {len(items)}: {ex}")

    report("LaTeX", [m.group(0) for m in re.finditer(r".{0,15}[\\$\{\}_^&].{0,15}", text)])
    report("Latin letters", [m.group(0) for m in re.finditer(r".{0,12}[A-Za-z]+.{0,12}", text)])
    report("symbols", [m.group(0) for m in re.finditer(r".{0,12}[≤≥×±→←~/\[\]()<>|·–—…＊*].{0,12}", body_text)])
    report("percent", [m.group(0) for m in re.finditer(r".{0,10}(?<!\d)%.{0,10}", body_text)])
    report("hash in body", [l[:30] for l in body if "#" in l])
    report("numbered cross-reference", [m.group(0) for m in re.finditer(
        r"(?<![가-힣])(표|그림|식|알고리즘|부록)\s?\(?\d+(\.\d+)*\)?|\d+\.\d+(\.\d+)*\s?절", text)])
    report("native count as digits", [m.group(0) for m in re.finditer(
        r"(?<![\d,.])(1[0-9]|[1-9])\s?(번|개|가지|명|층|살|달|쌍|줄|마리|시간)(?![가-힣])", body_text)])
    report("삭제", [m.group(0) for m in re.finditer(r".{0,10}삭제.{0,10}", text)])

    # 해요체: a sentence ending in 다. / 다? that is not 니다 is a slip; 니다 is also not 해요체
    endings = []
    for para in body:
        for m in re.finditer(r"[가-힣]+다[.?!](?=\s|$)", para):
            endings.append(m.group(0))
    report("not 해요체", endings)

    # headings: every source heading needs a script heading with most of its letters, in order
    heads = [(len(m.group(1)), m.group(2)) for m in re.finditer(r"^(#+)\s*(.+)$", text, flags=re.M)]
    missing = []
    pos = 0
    for kind, title in source_headings(sources):
        want = hangul_set(title)
        if not want:
            continue
        found = None
        for i in range(pos, len(heads)):
            have = hangul_set(heads[i][1])
            if len(want & have) >= 0.6 * len(want):
                found = i
                break
        if found is None:
            missing.append(f"{kind}: {title[:40]}")
        else:
            pos = found + 1
    report("source heading missing or out of order", missing)

    hangul = len(re.findall(r"[가-힣]", body_text))
    digits = len(re.findall(r"\d", body_text))
    minutes = (hangul + 1.5 * digits) / 6.0 / 60
    stats = f"script: {len(heads)} headings, {hangul:,} Hangul syllables, about {minutes:.0f} min at 6 syllables/s"

    if problems:
        print(f"{len(problems)} problem(s):")
        for p in problems:
            print(" -", p)
        print(stats)
        sys.exit(1)
    print("OK: no problems")
    print(stats)


if __name__ == "__main__":
    main()
