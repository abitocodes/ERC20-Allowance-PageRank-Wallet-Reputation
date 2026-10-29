#!/usr/bin/env python3
"""Check Korean particles after \\ref and \\eqref against the printed numbers.

Run after a build, because the numbers come from <folder>/main.aux:

    python -I -X utf8 check_particles.py A-plos-one          # report
    python -I -X utf8 check_particles.py A-plos-one --fix    # also rewrite them

A particle such as 은/는, 이/가, 을/를, 과/와, (으)로 or 이에요/예요 depends on how
the printed number ends when read aloud (표 3은, 표 2는, 식 (7)이, 부록 A가). The
rules are those of ../overleaf-github-ko/scripts/check_particles.py, applied to the
.tex files of one reading edition.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# last character of the printed reference -> 'C' (ends in a consonant),
# 'L' (ends in ㄹ, which takes 로 rather than 으로) or 'V' (ends in a vowel)
DIGIT = {"0": "C", "1": "L", "2": "V", "3": "C", "4": "V", "5": "V", "6": "C", "7": "L", "8": "L", "9": "V"}
LETTER = {c: "V" for c in "ABCDEFGHIJKOPQSTUVWXYZ"}
LETTER.update({"L": "L", "R": "L", "M": "C", "N": "C"})

# (form after a consonant, form after a vowel); ㄹ behaves as a consonant
# except for (으)로
PAIRS = [("은", "는"), ("을", "를"), ("과", "와"), ("이에요", "예요"), ("이고", "고"),
         ("이며", "며"), ("이나", "나"), ("이라는", "라는"), ("이라고", "라고"), ("이", "가")]


def labels(folder: Path) -> dict:
    aux = folder / "main.aux"
    if not aux.exists():
        return {}
    text = aux.read_text(encoding="utf-8", errors="replace")
    return {m.group(1): m.group(2) for m in re.finditer(r"\\newlabel\{([^}]*)\}\{\{([^}]*)\}", text)}


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
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        sys.exit(__doc__)
    folder = HERE / args[0].strip("/\\")
    fix = "--fix" in sys.argv
    lab = labels(folder)
    if not lab:
        sys.exit(f"no labels in {folder / 'main.aux'}: build main.tex first")
    alts = sorted({p for pair in PAIRS for p in pair} | {"으로", "로"}, key=len, reverse=True)
    pat = re.compile(r"(\\(ref|eqref)\{([^}]*)\})(" + "|".join(alts) + r")(?=[\s.,;:)\]}~]|$)")
    bad = 0
    for f in sorted(folder.glob("*.tex")):
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
            print(f"{f.relative_to(HERE)}:{line}: \\{cmd}{{{key}}} = {shown}: '{part}' -> '{want}'")
            changed = True
            return m.group(1) + want
        new = pat.sub(repl, s)
        if fix and changed:
            f.write_text(new, encoding="utf-8")
    print(f"{folder.name}: {bad} particle(s) to change" + (" (fixed)" if fix and bad else ""))


if __name__ == "__main__":
    main()
