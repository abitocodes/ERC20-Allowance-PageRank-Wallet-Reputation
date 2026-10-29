#!/usr/bin/env python3
"""Compare the numbers of a Korean reading edition with its English manuscript.

usage: python -I -X utf8 check_numbers.py A-plos-one
       python -I -X utf8 check_numbers.py B-ieee-access

The English sources are ../overleaf-github/manuscripts/<folder>/main.tex and every file
it \\input's; the Korean text is <folder>/main.tex and every file it \\input's (the
shared preamble excepted). Only the document bodies are read, without comments.

Three lists are printed:
  1. numbers of the Korean text that the English sources do not contain (must be empty);
  2. numbers written with an explicit sign in Korean whose signed form the English
     sources do not contain (must be empty);
  3. numbers of the English sources that the Korean text leaves out (check each one).
Numbers wrapped in \\ill{...} (illustrations) are skipped, and so are whole numbers up
to 12, which Korean writes as digits where English spells them out ("twelve months").
The exit status is 1 when list 1 or 2 is not empty.
"""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
EN_ROOT = HERE.parent / "overleaf-github" / "manuscripts"

# A number may touch Hangul ("6,483개", "2.21배") but not Latin letters, digits or a dot
# ("0a94215", "W0", "S1", "3.11.9" yields 3.11 only once).
NUM = re.compile(r"(?<![A-Za-z0-9_.])([+-]?)(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)(?![A-Za-z0-9_])")


def strip_comments(text: str) -> str:
    return "\n".join(re.sub(r"(?<!\\)%.*", "", line) for line in text.splitlines())


def with_inputs(path: Path, skip: tuple[str, ...] = ()) -> str:
    """The file's text with every \\input{...} replaced by that file's text."""
    text = strip_comments(path.read_text(encoding="utf-8"))

    def sub(m: re.Match) -> str:
        name = m.group(1)
        if any(s in name for s in skip):
            return ""
        p = (path.parent / name)
        if p.suffix != ".tex":
            p = p.with_suffix(".tex")
        return with_inputs(p, skip) if p.exists() else ""

    return re.sub(r"\\input\{([^}]+)\}", sub, text)


def body(text: str) -> str:
    m = re.search(r"\\begin\{document\}(.*)\\end\{document\}", text, re.S)
    return m.group(1) if m else text


def drop_braced(text: str, command: str) -> str:
    """Remove \\command{...} (with nested braces) from the text."""
    out, i, key = [], 0, "\\" + command + "{"
    while True:
        j = text.find(key, i)
        if j < 0:
            out.append(text[i:])
            return "".join(out)
        out.append(text[i:j])
        k, depth = j + len(key), 1
        while k < len(text) and depth:
            depth += {"{": 1, "}": -1}.get(text[k], 0)
            k += 1
        i = k


def normalize(text: str) -> str:
    text = drop_braced(text, "ill")
    text = re.sub(r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}", " ", text, flags=re.S)
    text = re.sub(r"\\fontsize\{[^}]*\}\{[^}]*\}", " ", text)
    text = re.sub(r"\\renewcommand\{?\\arraystretch\}?\{[^}]*\}", " ", text)
    for cmd in ("label", "ref", "eqref", "pageref", "cite", "url", "nolinkurl", "href",
                "bibliography", "bibliographystyle", "includegraphics", "input",
                "hypersetup", "setlength", "vspace", "hspace", "rule", "linespread",
                "resizebox", "scalebox", "addlinespace"):
        text = re.sub(r"\\" + cmd + r"\*?(\[[^\]]*\])?\{[^{}]*\}", " ", text)
    text = re.sub(r"\\addlinespace\[[^\]]*\]", " ", text)
    text = re.sub(r"\\(begin|end)\{[^}]*\}(\{[^}]*\})*(\[[^\]]*\])?", " ", text)
    text = re.sub(r"\[[\d.]+(pt|em|ex|in|mm|cm)\]", " ", text)
    text = re.sub(r"[\d.]+\\(linewidth|textwidth|columnwidth|hsize)", " ", text)
    text = re.sub(r"(?<![\d.])[\d.]+(pt|em|ex|in|mm|cm)\b", " ", text)
    text = re.sub(r"(\d)(st|nd|rd|th)\b", r"\1", text)  # "99th" is the number 99
    text = text.replace("{,}", ",").replace("\\,", " ").replace("~", " ")
    text = text.replace("$-$", "-").replace("$+$", "+").replace("\u2212", "-").replace("\u2013", " ")
    text = text.replace("\\%", "%").replace("--", " ")
    text = re.sub(r"\$\s*-\s*", "-", text)
    text = re.sub(r"\\(times|cdot)", " ", text)
    text = re.sub(r"\\[A-Za-z]+", " ", text)
    return text


def numbers(text: str) -> tuple[Counter, Counter]:
    """(unsigned numbers, numbers written with a sign), each as a Counter of strings."""
    plain, signed = Counter(), Counter()
    for sign, num in NUM.findall(normalize(text)):
        value = num.replace(",", "")
        if re.fullmatch(r"\d+", value) and int(value) <= 12:
            continue
        plain[num] += 1
        if sign:
            signed[sign + num] += 1
    return plain, signed


def main() -> int:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    folder = sys.argv[1].strip("/\\")
    en_text = body(with_inputs(EN_ROOT / folder / "main.tex"))
    ko_text = body(with_inputs(HERE / folder / "main.tex", skip=("common/preamble",)))
    en_plain, en_signed = numbers(en_text)
    ko_plain, ko_signed = numbers(ko_text)
    en_signed_all = set(en_signed) | {"+" + n for n in en_plain}  # an unsigned English number may be read as positive

    only_ko = sorted(n for n in ko_plain if n not in en_plain)
    bad_sign = sorted(n for n in ko_signed if n not in en_signed_all)
    only_en = sorted(n for n in en_plain if n not in ko_plain)

    print(f"{folder}: English {sum(en_plain.values())} numbers ({len(en_plain)} distinct), "
          f"Korean {sum(ko_plain.values())} ({len(ko_plain)} distinct)")
    print(f"1. only in the Korean text ({len(only_ko)}):", " ".join(only_ko) or "none")
    print(f"2. sign not in the English sources ({len(bad_sign)}):", " ".join(bad_sign) or "none")
    print(f"3. left out of the Korean text ({len(only_en)}):", " ".join(only_en) or "none")
    return 1 if only_ko or bad_sign else 0


if __name__ == "__main__":
    sys.exit(main())
