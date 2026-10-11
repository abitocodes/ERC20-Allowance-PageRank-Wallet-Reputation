#!/usr/bin/env python3
"""Check Korean particles after \\ref and \\eqref against the printed numbers.

Run after a full build, because the numbers come from the .aux files:

    python scripts/check_particles.py          # report
    python scripts/check_particles.py --fix    # also rewrite the particles

A particle such as 은/는, 이/가, 을/를, 과/와, (으)로 or 이에요/예요 depends on
how the printed number ends when read aloud (표 4.3은, 표 4.2는). The script
reads every label's number from the .aux files and reports each particle
that does not match.
"""
import re
import sys
from pathlib import Path

KO = Path(__file__).resolve().parent.parent

# last character of the printed reference -> 'C' (ends in a consonant),
# 'L' (ends in ㄹ, which takes 로 rather than 으로) or 'V' (ends in a vowel)
DIGIT = {"0": "C", "1": "L", "2": "V", "3": "C", "4": "V", "5": "V", "6": "C", "7": "L", "8": "L", "9": "V"}
LETTER = {c: "V" for c in "ABCDEFGHIJKOPQSTUVWXYZ"}
LETTER.update({"L": "L", "R": "L", "M": "C", "N": "C"})

# (form after a consonant, form after a vowel); ㄹ behaves as a consonant
# except for (으)로
PAIRS = [("은", "는"), ("을", "를"), ("과", "와"), ("이에요", "예요"), ("이고", "고"),
         ("이며", "며"), ("이나", "나"), ("이라는", "라는"), ("이라고", "라고"), ("이", "가")]


def labels():
    out = {}
    for aux in list(KO.glob("*.aux")) + list(KO.glob("Chapter-*/*.aux")):
        for m in re.finditer(r"\\newlabel\{([^}]*)\}\{\{([^}]*)\}", aux.read_text(encoding="utf-8", errors="replace")):
            out.setdefault(m.group(1), m.group(2))
    return out


def ending(text):
    t = re.sub(r"\\[A-Za-z]+\s*", "", text).strip("{} ")
    if not t:
        return None
    c = t[-1]
    if c in DIGIT:
        return DIGIT[c]
    return LETTER.get(c.upper())


def expected(kind, particle):
    """Return the right particle for a reference ending of the given kind."""
    if particle in ("으로", "로"):
        return "으로" if kind == "C" else "로"
    for cons, vow in PAIRS:
        if particle in (cons, vow):
            return cons if kind in ("C", "L") else vow
    return particle


def main():
    fix = "--fix" in sys.argv
    lab = labels()
    if not lab:
        sys.exit("no .aux labels found: build main.tex first")
    alts = sorted({p for pair in PAIRS for p in pair} | {"으로", "로"}, key=len, reverse=True)
    pat = re.compile(r"(\\(ref|eqref)\{([^}]*)\})(" + "|".join(alts) + r")(?=[\s.,;:)\]}~]|$)")
    bad = 0
    files = sorted(KO.glob("Chapter-0*/**/*.tex")) + sorted(KO.glob("01-Intro/*.tex")) \
        + sorted(KO.glob("results/tables/*.tex")) + sorted(KO.glob("Figures/*.tex"))
    for f in files:
        s = f.read_text(encoding="utf-8")
        changed = False

        def repl(m):
            nonlocal bad, changed
            cmd, key, part = m.group(2), m.group(3), m.group(4)
            num = lab.get(key)
            if num is None:
                return m.group(0)
            shown = f"({num})" if cmd == "eqref" else num
            kind = ending(num)
            if kind is None:
                return m.group(0)
            want = expected(kind, part)
            if want == part:
                return m.group(0)
            bad += 1
            line = s.count("\n", 0, m.start()) + 1
            print(f"{f.relative_to(KO)}:{line}: \\{cmd}{{{key}}} = {shown}: '{part}' -> '{want}'")
            changed = True
            return m.group(1) + want
        new = pat.sub(repl, s)
        if fix and changed:
            f.write_text(new, encoding="utf-8")
    print(f"{bad} particle(s) to change" + (" (fixed)" if fix and bad else ""))


if __name__ == "__main__":
    main()
