#!/usr/bin/env python3
"""Turn an audiobook script into text a Korean TTS voice reads correctly.

Numbers become Korean words: Sino-Korean by default (5,521개 -> 오천오백이십일 개,
0.36 -> 영 점 삼육, 2026년 -> 이천이십육 년, 95% -> 구십오 퍼센트), native
Korean before counting words for 1-99 (37번 -> 서른일곱 번), and the month
names 유월 and 시월. Headings and paragraphs are split into segments so the
synthesizer can put pauses between them.

usage: normalize.py SCRIPT.md        prints the segments, one per line
"""
import re
import sys

DIG = "영일이삼사오육칠팔구"
NATIVE_ONES = ["", "한", "두", "세", "네", "다섯", "여섯", "일곱", "여덟", "아홉"]
NATIVE_TENS = ["", "열", "스물", "서른", "마흔", "쉰", "예순", "일흔", "여든", "아흔"]
# words counted with native Korean numbers
NATIVE_COUNTERS = ("번", "개", "가지", "명", "시간", "살", "달", "쌍", "줄", "마리", "사람", "곳", "군데", "차례", "바퀴", "권", "시")


def sino(n: int) -> str:
    """Sino-Korean reading of a non-negative integer."""
    if n == 0:
        return "영"
    units = [(10 ** 12, "조"), (10 ** 8, "억"), (10 ** 4, "만")]
    out = []
    for value, name in units:
        if n >= value:
            head = n // value
            n %= value
            words = _under_10000(head)
            if name == "만" and head == 1:
                words = ""
            out.append(words + name)
    if n:
        out.append(_under_10000(n))
    return " ".join(out)


def _under_10000(n: int) -> str:
    s = ""
    for value, name in [(1000, "천"), (100, "백"), (10, "십")]:
        d = n // value
        n %= value
        if d:
            s += ("" if d == 1 else DIG[d]) + name
    if n:
        s += DIG[n]
    return s


def native(n: int, before_counter: bool = True) -> str:
    """Native Korean reading for 1-99 (counting form before a counter)."""
    tens, ones = divmod(n, 10)
    if ones == 0 and tens == 2 and before_counter:
        return "스무"
    word = NATIVE_TENS[tens] + NATIVE_ONES[ones]
    return word


def decimal(text: str) -> str:
    """'0.36' -> '영 점 삼육', '12.5' -> '십이 점 오'."""
    whole, frac = text.split(".")
    return sino(int(whole)) + " 점 " + "".join(DIG[int(c)] for c in frac)


def number_words(raw: str) -> str:
    raw = raw.replace(",", "")
    if "." in raw:
        return decimal(raw)
    return sino(int(raw))


NUM = r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?"


def normalize_text(t: str) -> str:
    # minus before a number
    t = re.sub(r"(?<![\d가-힣])-(?=\d)", "마이너스 ", t)
    # months with irregular readings, then dates and other numbers
    t = re.sub(r"(?<!\d)6월", "유월", t)
    t = re.sub(r"(?<!\d)10월", "시월", t)
    # percent
    t = re.sub(r"(" + NUM + r")\s?%", lambda m: number_words(m.group(1)) + " 퍼센트", t)
    # native counters for 1-99 (integers only)
    counters = "|".join(NATIVE_COUNTERS)
    t = re.sub(r"(?<![\d.,])(\d{1,2})\s?(" + counters + r")(?![가-힣])",
               lambda m: (native(int(m.group(1))) if 0 < int(m.group(1)) < 100 else number_words(m.group(1))) + m.group(2), t)
    # everything else Sino-Korean; a following particle or unit stays attached (1과 -> 일과)
    t = re.sub(r"(" + NUM + r")", lambda m: number_words(m.group(1)), t)
    t = re.sub(r"[ \t]+", " ", t)
    return t.strip()


def segments(script: str):
    """Yield (kind, text) with kind in {'h1','h2','h3','h4','p'}."""
    para = []
    for line in script.split("\n"):
        m = re.match(r"^(#{1,4})\s*(.+)$", line)
        if m:
            if para:
                yield "p", normalize_text(" ".join(para))
                para = []
            title = m.group(2).strip()
            if not re.search(r"[.?!]$", title):
                title += "."
            yield "h%d" % len(m.group(1)), normalize_text(title)
        elif line.strip():
            para.append(line.strip())
        elif para:
            yield "p", normalize_text(" ".join(para))
            para = []
    if para:
        yield "p", normalize_text(" ".join(para))


if __name__ == "__main__":
    text = open(sys.argv[1], encoding="utf-8").read()
    for kind, seg in segments(text):
        print(f"[{kind}] {seg}")
