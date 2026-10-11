#!/usr/bin/env python3
"""Compare an English LaTeX source with its Korean translation.

usage: check_ko.py EN.tex KO.tex

Reports every structural or numeric difference that a faithful translation
must not have, plus English sentences that look untranslated.
Exit code 0 when no problem is found.
"""
import re
import sys
from collections import Counter


def strip_comments(s: str) -> str:
    out = []
    for line in s.split("\n"):
        m = re.search(r"(?<!\\)%", line)
        out.append(line[: m.start()] if m else line)
    return "\n".join(out)


BRACE = r"\{((?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*)\}"


def grab(pattern, s, group=1):
    return [m.group(group) for m in re.finditer(pattern, s)]


def math_segments(s: str):
    segs = []
    # display/env math first
    for env in ["equation", "equation*", "align", "align*"]:
        segs += grab(r"\\begin\{" + re.escape(env) + r"\}(.*?)\\end\{" + re.escape(env) + r"\}", s, 1)
    s2 = re.sub(r"\\begin\{(equation\*?|align\*?)\}.*?\\end\{\1\}", " ", s, flags=re.S)
    segs += grab(r"\\\[(.*?)\\\]", s2, 1)
    s3 = re.sub(r"\\\[.*?\\\]", " ", s2, flags=re.S)
    segs += grab(r"(?<!\\)\$(.+?)(?<!\\)\$", s3, 1)
    return segs


def norm_math(m: str) -> str:
    m = re.sub(r"\\(text|mbox)\s*" + BRACE, r"\\\1{}", m)
    m = re.sub(r"\s+", "", m)
    return m


def remove_math(s: str) -> str:
    s = re.sub(r"\\begin\{(equation\*?|align\*?)\}.*?\\end\{\1\}", " ", s, flags=re.S)
    s = re.sub(r"\\\[.*?\\\]", " ", s, flags=re.S)
    s = re.sub(r"(?<!\\)\$(.+?)(?<!\\)\$", " ", s)
    return s


def numbers(s: str):
    s = strip_comments(s)
    s = remove_math(s)
    s = re.sub(r"\\begin\{verbatim\}.*?\\end\{verbatim\}", " ", s, flags=re.S)
    s = re.sub(r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}", " ", s, flags=re.S)
    for cmd in ["label", "ref", "eqref", "pageref", "cend", "input", "include", "texttt", "url",
                "hspace", "vspace", "setlength", "includegraphics", "TOCentry", "hyperref"]:
        s = re.sub(r"\\" + cmd + r"(\[[^\]]*\])*\s*" + BRACE, " ", s)
    s = re.sub(r"\\href" + BRACE, " ", s)
    s = re.sub(r"\[[^\]]*\\(textwidth|linewidth)[^\]]*\]", " ", s)
    s = re.sub(r"p\{[0-9.]+\\linewidth\}", " ", s)
    s = re.sub(r"\{[0-9.]+(em|pt|ex|mm|cm|in)\}", " ", s)
    s = s.replace("{,}", ",")
    toks = re.findall(r"(?<![A-Za-z\\_])-?\d+(?:[.,]\d+)*", s)
    return Counter(toks)


def english_leftovers(s: str):
    s = strip_comments(s)
    s = remove_math(s)
    s = re.sub(r"\\begin\{verbatim\}.*?\\end\{verbatim\}", " ", s, flags=re.S)
    for cmd in ["texttt", "url", "label", "ref", "eqref", "cend", "input", "include", "includegraphics", "hyperref"]:
        s = re.sub(r"\\" + cmd + r"(\[[^\]]*\])*\s*" + BRACE, " ", s)
    s = re.sub(r"\\href" + BRACE + BRACE, " ", s)
    s = re.sub(r"\\(node|draw|path|coordinate)\s*\[[^\]]*\]", " ", s)  # TikZ options are code
    s = re.sub(r"\\[A-Za-z]+\*?", " ", s)  # command names
    bad = []
    for line in s.split("\n"):
        for m in re.finditer(r"(?:\b[A-Za-z][a-z'’]+\b[\s,;:()]+){5,}[A-Za-z][a-z]+", line):
            frag = m.group(0)
            bad.append(frag[:90])
    return bad


def paragraphs(s: str) -> int:
    s = strip_comments(s)
    blocks = [b for b in re.split(r"\n\s*\n", s) if b.strip()]
    return len(blocks)


def main():
    en_raw = open(sys.argv[1], encoding="utf-8").read()
    ko_raw = open(sys.argv[2], encoding="utf-8").read()
    en, ko = strip_comments(en_raw), strip_comments(ko_raw)
    problems = []

    def cmp(name, a, b):
        ca, cb = Counter(a), Counter(b)
        if ca != cb:
            miss = ca - cb
            extra = cb - ca
            problems.append(f"[{name}] missing in KO: {dict(miss)} | extra in KO: {dict(extra)}")

    cmp("label", grab(r"\\label\{([^}]*)\}", en), grab(r"\\label\{([^}]*)\}", ko))
    cmp("ref", grab(r"\\(?:ref|eqref|pageref)\{([^}]*)\}", en), grab(r"\\(?:ref|eqref|pageref)\{([^}]*)\}", ko))
    cmp("hyperref", grab(r"\\hyperref\[([^\]]*)\]", en), grab(r"\\hyperref\[([^\]]*)\]", ko))
    norm_c = lambda xs: [",".join(sorted(x.replace(" ", "").split(","))) for x in xs]
    cmp("cite \\cend", norm_c(grab(r"\\cend\{([^}]*)\}", en)), norm_c(grab(r"\\cend\{([^}]*)\}", ko)))
    cmp("input", grab(r"\\(?:input|include)\{([^}]*)\}", en), grab(r"\\(?:input|include)\{([^}]*)\}", ko))
    cmp("includegraphics", grab(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]*)\}", en), grab(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]*)\}", ko))
    cmp("environment", grab(r"\\begin\{([^}]*)\}", en), grab(r"\\begin\{([^}]*)\}", ko))
    cmp("\\item", ["item"] * len(re.findall(r"\\item\b", en)), ["item"] * len(re.findall(r"\\item\b", ko)))
    for cmd in ["caption", "footnote", "dissertationSubheading", "dissertationSubsubheading", "chapter", "section", "subsection"]:
        n_en = len(re.findall(r"\\" + cmd + r"\b", en))
        n_ko = len(re.findall(r"\\" + cmd + r"\b", ko))
        if n_en != n_ko:
            problems.append(f"[\\{cmd}] EN {n_en} vs KO {n_ko}")
    cmp("heading key", grab(r"\\dissertationSub(?:sub)?heading\[([^\]]*)\]", en), grab(r"\\dissertationSub(?:sub)?heading\[([^\]]*)\]", ko))
    cmp("texttt", grab(r"\\texttt" + BRACE, en), grab(r"\\texttt" + BRACE, ko))
    cmp("url", grab(r"\\url\{([^}]*)\}", en), grab(r"\\url\{([^}]*)\}", ko))
    cmp("math", [norm_math(m) for m in math_segments(en)], [norm_math(m) for m in math_segments(ko)])
    amp_en = len(re.findall(r"(?<!\\)&", remove_math(en)))
    amp_ko = len(re.findall(r"(?<!\\)&", remove_math(ko)))
    if amp_en != amp_ko:
        problems.append(f"[& column separators] EN {amp_en} vs KO {amp_ko}")
    nl_en = len(re.findall(r"\\\\", remove_math(en)))
    nl_ko = len(re.findall(r"\\\\", remove_math(ko)))
    if nl_en != nl_ko:
        problems.append(f"[\\\\ row ends] EN {nl_en} vs KO {nl_ko}")
    ne, nk = numbers(en_raw), numbers(ko_raw)
    miss = ne - nk
    if miss:
        problems.append(f"[numbers] missing in KO: {dict(miss)}")
    extra = nk - ne
    pe, pk = paragraphs(en_raw), paragraphs(ko_raw)
    if pe != pk:
        problems.append(f"[paragraphs] EN {pe} vs KO {pk}")
    left = english_leftovers(ko_raw)
    if left:
        problems.append(f"[English left] {len(left)} fragments, e.g. " + " || ".join(left[:6]))

    if problems:
        print(f"{len(problems)} problem(s):")
        for p in problems:
            print(" -", p)
        if extra:
            print(" (info) numbers only in KO:", dict(extra))
        sys.exit(1)
    print("OK: no problems")
    if extra:
        print(" (info) numbers only in KO:", dict(extra))


if __name__ == "__main__":
    main()
