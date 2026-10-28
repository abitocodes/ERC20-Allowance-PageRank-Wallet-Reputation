#!/usr/bin/env python3
"""Find the numbers of a results digest in the manuscript and map them to another digest.

The manuscript quotes the published digests (experiments/data/3-published-results-for-thesis/).
When an analysis is rerun, every quoted number of the old digest has to become the number of
the new digest under the same key. This tool does the bookkeeping; it never decides a sentence.

  scan   every number in the given .tex files (generated tables excluded), with the digest rows
         whose value holds it: the old digest of the analysis being replaced, the new one, and the
         digest that stays (the registered analysis). Writes a CSV report:
           unique      the old value under keys that all map to one new value; safe to replace
           ambiguous   the old value under keys that map to different new values
           both        a value of the old digest and of the digest that stays; decided by its sentence
           small       an integer below 1,000 that matches the old digest; decided by its sentence
           kept        only a value of the digest that stays
           none        in no digest (constants, dates, derived numbers)
         A point estimate written with its interval (P [L, H]) is matched as a triple, which a
         coincidence almost never matches: group-unique, group-kept, group-both, group-ambiguous,
         group-none. Dates and clock times are not read as numbers.
  apply  replace the occurrences marked unique (and those a reviewer set to replace) in place
  audit  the old values that are still in the files and are not values of the digest that stays

Numbers are compared at the precision written: "0.41" matches a digest value 0.412 only if the
digest value rounds to it and has at least as many decimals. Thousands separators ({,} and ,),
the minus signs (-, −, $-$) and an explicit + are read; percentages are matched as written.

Usage:
  python numbers.py scan  --old OLD.md --new NEW.md --keep KEEP.md --out report.csv FILE.tex ...
  python numbers.py apply --report report.csv
  python numbers.py audit --old OLD.md --keep KEEP.md [--new NEW.md] FILE.tex ...
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

ROW = re.compile(r"^\| (?P<q>.*?) \| (?P<v>.*?) \| `(?P<f>[^`]*)` : `(?P<k>[^`]*)` \|\s*$")
# A number as LaTeX prose writes it: optional sign, digits with {,} or , thousands, decimals, optional \%.
NUM = re.compile(
    r"(?<![\w.{}\\])"
    r"(?P<sign>\$-\$|[+\-−]|\$-|)"
    r"(?P<int>\d{1,3}(?:(?:\{,\}|,)\d{3})+|\d+)"
    r"(?P<dec>\.\d+)?"
    r"(?P<pct>\\%|%)?"
    r"(?![\w{])")


@dataclass
class Num:
    text: str      # as written
    value: float
    decimals: int
    pct: bool
    start: int
    end: int

    @property
    def key(self) -> tuple[str, bool]:
        return (f"{self.value:.{self.decimals}f}", self.pct)


def parse_number(m: re.Match) -> Num:
    sign = m.group("sign")
    neg = sign in ("-", "−", "$-$", "$-")
    digits = re.sub(r"\{,\}|,", "", m.group("int"))
    dec = m.group("dec") or ""
    v = float(digits + dec) * (-1 if neg else 1)
    return Num(m.group(0), v, len(dec) - 1 if dec else 0, bool(m.group("pct")), m.start(), m.end())


def numbers(text: str) -> list[Num]:
    """The numbers of a text; a digit string with a leading zero (01, 08) is a name, not a number."""
    return [parse_number(m) for m in NUM.finditer(text) if not re.fullmatch(r"0\d+", m.group("int"))]


def read_digest(path: Path) -> list[dict]:
    rows, count = [], defaultdict(int)
    for line in path.read_text(encoding="utf-8").splitlines():
        m = ROW.match(line)
        if not m or m.group("q") == "Quantity":
            continue
        ident = (m.group("f"), m.group("k"), m.group("q"))
        count[ident] += 1
        rows.append({"id": (*ident, count[ident]), "value": m.group("v"), "nums": numbers(m.group("v"))})
    return rows


def matches(prose: Num, digest: Num) -> int | None:
    """The scale (1, or 100 for a percentage of a share) at which the digest number, written at the
    precision of the prose number, equals it; None if it does not."""
    for scale in ((1, 100) if prose.pct and not digest.pct else (1,)):
        places = prose.decimals + (2 if scale == 100 else 0)
        if digest.decimals >= places and f"{digest.value * scale:.{prose.decimals}f}" == f"{prose.value:.{prose.decimals}f}":
            return scale
    return None


def fmt_like(prose: Num, new: Num, scale: int) -> str:
    """The new digest number written the way the prose number is written: decimals, thousands
    separators, the minus sign used, an explicit + where the prose or the digest shows one, percent."""
    t, value = prose.text, new.value * scale
    body = f"{abs(value):,.{prose.decimals}f}"
    if "{,}" in t:
        body = body.replace(",", "{,}")
    elif not re.search(r"\d,\d{3}", t):
        body = body.replace(",", "")
    dollar = "$" if t.startswith("$") else ""
    # an explicit + where the prose or the digest writes one (a contrast), not merely because the old value was negative
    signed = t.lstrip("$")[:1] == "+" or new.text[:1] == "+"
    if value < 0:
        sign = "−" if t.lstrip("$")[:1] == "−" else "-"
    else:
        sign = "+" if signed else ""
    pct = "\%" if t.endswith("\%") else ("%" if t.endswith("%") else "")
    return dollar + sign + body + pct


def index(rows: list[dict]) -> dict:
    by_id = {r["id"]: r for r in rows}
    return by_id


def tex_files(paths: list[str]) -> list[Path]:
    out = []
    for p in map(Path, paths):
        files = sorted(p.rglob("*.tex")) if p.is_dir() else [p]
        out += [f for f in files if f.suffix == ".tex" and "results/tables" not in f.as_posix()
                and "_chapter_aux_backup" not in f.as_posix()]
    return out


def strip_comment(line: str) -> str:
    """The line without its LaTeX comment; a TikZ drawing command is dropped whole (its numbers are
    coordinates)."""
    line = re.sub(r"(?<!\\)%.*$", "", line)
    if re.match(r"\s*\\(draw|node|fill|filldraw|path|coordinate|foreach|def|shade|clip|matrix|tikzset)\b", line) \
            or re.search(r"\(\s*-?\d+(\.\d+)?\s*,\s*-?\d+(\.\d+)?\s*\)", line):
        return ""
    return line


DATE = re.compile(r"\d{4}-\d{2}-\d{2}|\d{1,2}:\d{2}(?::\d{2})?")


def mask_dates(line: str) -> str:
    """Dates (2026-06-30) and clock times (23:59:59) blanked out, so that columns stay the same."""
    return DATE.sub(lambda m: "#" * len(m.group(0)), line)


def groups(line: str, nums: list[Num]) -> dict[int, tuple[int, int, int]]:
    """Point estimates written with their interval, P [L, H] or $P$ ($[L,H]$): the index of each
    member to the indices of its group."""
    out = {}
    for i in range(len(nums) - 2):
        p, lo, hi = nums[i], nums[i + 1], nums[i + 2]
        # between the point and the interval: no digit, at most a short phrase ("$, with interval $[")
        between = line[p.end:lo.start]
        if (re.fullmatch(r"[^\d\[\]]{0,40}\[\s*", between) and ";" not in between
                and re.fullmatch(r"\s*,\s*", line[lo.end:hi.start])
                and re.match(r"\s*\]", line[hi.end:])):
            for k in (i, i + 1, i + 2):
                out[k] = (i, i + 1, i + 2)
    return out


def triples(rows: list[dict], g: tuple) -> list[tuple[dict, int]]:
    """Rows that hold the three numbers of a group in this order, with the index of the first."""
    out = []
    for r in rows:
        ns = r["nums"]
        for j in range(len(ns) - 2):
            if all(matches(x, ns[j + k]) == 1 for k, x in enumerate(g)):
                out.append((r, j))
    return out


def scan(args) -> int:
    old, new, keep = read_digest(Path(args.old)), index(read_digest(Path(args.new))), read_digest(Path(args.keep))
    out = []
    for f in tex_files(args.files):
        for ln, raw in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            line = strip_comment(raw)
            nums = numbers(mask_dates(line))
            grp = groups(line, nums)
            # a group is decided as a whole: replaced only if every member has one new value
            gdec = {}
            for idx in set(grp.values()):
                g = tuple(nums[k] for k in idx)
                oc, kc = triples(old, g), triples(keep, g)
                props = [set() for _ in idx]
                for r, j in oc:
                    nr = new.get(r["id"])
                    for pos, k in enumerate(idx):
                        props[pos].add(None if nr is None or len(nr["nums"]) != len(r["nums"])
                                       else fmt_like(nums[k], nr["nums"][j + pos], 1))
                one = all(len(p) == 1 and None not in p for p in props)
                status = ("group-kept" if kc and not oc else "group-both" if kc else
                          "group-unique" if one else "group-ambiguous" if oc else "group-none")
                gdec[idx] = (status, [next(iter(p)) if one else "" for p in props], oc, kc)
            for gi, n in enumerate(nums):
                if gi in grp:
                    idx = grp[gi]
                    status, news, oc, kc = gdec[idx]
                    new_text = news[idx.index(gi)]
                    out.append({
                        "file": f.as_posix(), "line": ln, "col": n.start, "text": n.text, "status": status,
                        "new": new_text,
                        "action": "replace" if status == "group-unique" and new_text != n.text else "",
                        "keys": " | ".join(sorted({" : ".join(map(str, r["id"][:3])) for r, _ in oc})[:3]),
                        "kept_keys": " | ".join(sorted({" : ".join(map(str, r["id"][:3])) for r, _ in kc})[:2]),
                        "context": line[max(0, n.start - 70):n.end + 50].strip(),
                    })
                    continue
                cands = [(r, i, sc) for r in old for i, d in enumerate(r["nums"])
                         if (sc := matches(n, d)) is not None]
                kept = [r for r in keep for d in r["nums"] if matches(n, d) is not None]
                proposals = set()
                for r, i, sc in cands:
                    nr = new.get(r["id"])
                    if nr is None or len(nr["nums"]) != len(r["nums"]):
                        proposals.add(None)
                    else:
                        proposals.add(fmt_like(n, nr["nums"][i], sc))
                one = len(proposals) == 1 and None not in proposals
                if not cands:
                    status = "kept" if kept else "none"
                elif n.decimals == 0 and abs(n.value) < 1000 and not n.pct:
                    status = "small"  # small integers match many rows; decided by hand
                elif kept:
                    status = "both"   # a value of both digests; its sentence decides
                else:
                    status = "unique" if one else "ambiguous"
                new_text = next(iter(proposals)) if one and status in ("unique", "both", "small") else ""
                ids = sorted({" : ".join(map(str, r["id"][:3])) for r, _, _ in cands})
                out.append({
                    "file": f.as_posix(), "line": ln, "col": n.start, "text": n.text, "status": status,
                    "new": new_text, "action": "replace" if status == "unique" and new_text != n.text else "",
                    "keys": " | ".join(ids[:4]) + (f" (+{len(ids) - 4})" if len(ids) > 4 else ""),
                    "kept_keys": " | ".join(sorted({" : ".join(map(str, r["id"][:3])) for r in kept})[:2]),
                    "context": line[max(0, n.start - 70):n.end + 50].strip(),
                })
    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]) if out else ["file"])
        w.writeheader()
        w.writerows(out)
    counts = defaultdict(int)
    for r in out:
        counts[r["status"]] += 1
    print(f"{len(out)} numbers: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())),
          f"; {sum(1 for r in out if r['action'] == 'replace')} to replace")
    return 0


def apply(args) -> int:
    rows = [r for r in csv.DictReader(open(args.report, encoding="utf-8")) if r["action"] == "replace"]
    by_file = defaultdict(list)
    for r in rows:
        by_file[r["file"]].append(r)
    changed = 0
    for f, rs in by_file.items():
        p = Path(f)
        raw = p.read_bytes().decode("utf-8")
        nl = "\r\n" if "\r\n" in raw else "\n"
        lines = raw.replace("\r\n", "\n").split("\n")
        for r in sorted(rs, key=lambda r: (int(r["line"]), -int(r["col"]))):
            i, c = int(r["line"]) - 1, int(r["col"])
            line = lines[i]
            if line[c:c + len(r["text"])] != r["text"]:
                raise SystemExit(f"{f}:{r['line']}: expected {r['text']!r} at column {c}")
            lines[i] = line[:c] + r["new"] + line[c + len(r["text"]):]
            changed += 1
        p.write_bytes("\n".join(lines).replace("\n", nl).encode("utf-8"))
    print(f"replaced {changed} numbers in {len(by_file)} files")
    return 0


def audit(args) -> int:
    old, keep = read_digest(Path(args.old)), read_digest(Path(args.keep))
    keep = keep + (read_digest(Path(args.new)) if args.new else [])  # a value of the new digest is not left over
    left = 0
    for f in tex_files(args.files):
        for ln, raw in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            line = strip_comment(raw)
            for n in numbers(mask_dates(line)):
                if n.decimals == 0 and abs(n.value) < 1000:
                    continue  # small integers are everywhere; the scan report lists them
                if any(matches(n, d) is not None for r in old for d in r["nums"]) and not any(
                        matches(n, d) is not None for r in keep for d in r["nums"]):
                    left += 1
                    print(f"{f.as_posix()}:{ln}: {n.text}  ...{line[max(0, n.start - 60):n.end + 40].strip()}...")
    print(f"{left} old values left")
    return 1 if left else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scan")
    s.add_argument("--old", required=True)
    s.add_argument("--new", required=True)
    s.add_argument("--keep", required=True)
    s.add_argument("--out", required=True)
    s.add_argument("files", nargs="+")
    a = sub.add_parser("apply")
    a.add_argument("--report", required=True)
    u = sub.add_parser("audit")
    u.add_argument("--old", required=True)
    u.add_argument("--keep", required=True)
    u.add_argument("--new", help="the digest that replaces --old; its values are not reported")
    u.add_argument("files", nargs="+")
    args = ap.parse_args()
    return {"scan": scan, "apply": apply, "audit": audit}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
