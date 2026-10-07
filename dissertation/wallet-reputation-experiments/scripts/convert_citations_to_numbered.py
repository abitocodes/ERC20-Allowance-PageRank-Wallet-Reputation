"""Convert APA author-year citations to numbered superscript endnotes.

Rewrites bibliography.tex with [1]..[N] labels and replaces citations in
English dissertation body/appendix/abstract with \\cend{n} / \\cend{n,m}.
"""

from __future__ import annotations

import re
from project_paths import MANUSCRIPT_DIR

ROOT = MANUSCRIPT_DIR
BIB = ROOT / "Chapter-07-References" / "index.tex"
PREAMBLE = ROOT / "Config" / "preamble.tex"

# Files to convert (English dissertation only).
TARGETS = [
    ROOT / "01-Intro" / "02-Abstract.tex",
    ROOT / "Chapter-01-Introduction-and-Research-Problem" / "index.tex",
    ROOT / "Chapter-02-Literature-Review-and-Theoretical-Framework" / "index.tex",
    ROOT / "Chapter-03-Research-Methodology" / "index.tex",
    ROOT / "Chapter-04-Implementation-and-Empirical-Results" / "index.tex",
    ROOT / "Chapter-05-Discussion" / "index.tex",
    ROOT / "Chapter-06-Conclusion-and-Future-Work" / "index.tex",
    ROOT / "Chapter-08-Appendix" / "index.tex",
    ROOT / "Chapter-08-Appendix" / "appendix-b.tex",
    ROOT / "Chapter-08-Appendix" / "appendix-c.tex",
    ROOT / "Chapter-08-Appendix" / "appendix-d.tex",
    ROOT / "Chapter-08-Appendix" / "appendix-e.tex",
]


def parse_bib_entries(bib_text: str) -> list[dict]:
    entries: list[dict] = []
    for m in re.finditer(r"\\hangindent=0\.5in \\hangafter=1 (.+?)\\par", bib_text, re.S):
        text = m.group(1).strip()
        ym = re.search(r"\((\d{4}|n\.d\.)\)", text)
        year = ym.group(1) if ym else "n.d."
        # Author block before year parenthesis
        author_block = text[: ym.start()].strip() if ym else text.split(".")[0]
        # Normalize for matching
        authors = author_block.replace(r"\&", "&").replace(r"\"{a}", "a").replace(r"\"{o}", "o")
        authors = authors.replace(r"\"{u}", "u").replace(r"\'{e}", "e")
        # First author surname (last token before comma, or first word)
        first = authors.split(",")[0].strip()
        # Handle "Ethereum Improvement Proposals", "GMX"
        if "," in authors:
            surname = first.split()[-1] if first.split() else first
            # "Angeris, G." -> Angeris; but "Ethereum Improvement Proposals" has no comma after first author style
            # Actually "Angeris, G." first part is "Angeris"
            surname = first.strip()
        else:
            surname = first.strip()
        # For "Packin, N. G., & Lev-Aretz, Y." surname is Packin
        # For corporate: "Ethereum Improvement Proposals." or "GMX."
        surname = surname.rstrip(".")
        entries.append(
            {
                "n": len(entries) + 1,
                "year": year,
                "surname": surname,
                "author_block": author_block,
                "text": text,
                "authors_norm": authors,
            }
        )
    return entries


def build_lookup(entries: list[dict]) -> dict[tuple[str, str], int]:
    """Map (surname_lower, year) -> number. Also multi-author keys."""
    lookup: dict[tuple[str, str], int] = {}
    for e in entries:
        n = e["n"]
        year = e["year"]
        s = e["surname"].lower()
        lookup[(s, year)] = n
        # Alternate surnames for multi-author papers commonly cited
        ab = e["authors_norm"]
        # Second author surname for "X and Y (year)"
        parts = re.split(r",\s*&\s*|,\s*and\s*|&\s*", ab)
        if len(parts) >= 2:
            # "Packin, N. G." and "Lev-Aretz, Y."
            second = parts[1].strip().split(",")[0].strip()
            # second might be "Lev-Aretz" or "G." - for "Packin, N. G., & Lev-Aretz, Y."
            # parts[0]=Packin, N. G.  parts[1]=Lev-Aretz, Y.
            second_sur = second.split(",")[0].strip().lower()
            if len(second_sur) > 1:
                lookup[(f"{s} and {second_sur}", year)] = n
                lookup[(f"{s} & {second_sur}", year)] = n
                lookup[(second_sur, year)] = lookup.get((second_sur, year), n)  # careful: collisions
        # et al. form uses first surname only - already have (s, year)
        # Corporate full name
        full = e["surname"].lower()
        lookup[(full, year)] = n
    # Manual aliases for common citation forms
    aliases = {
        ("page", "1998"): None,  # Page et al. 1998 is entry Page, L. - need find
        ("brin", "1998"): None,
        ("ethereum improvement proposals", "2015"): None,
        ("ethereum improvement proposals", "2020"): None,
        ("gmx", "n.d."): None,
        ("do", "2023"): None,
        ("langville", "2006"): None,
        ("packin", "2024"): None,
        ("lev-aretz", "2024"): None,
        ("schar", "2021"): None,
        ("schä", "2021"): None,
    }
    # Fix Page et al. - entry is "Page, L., Brin, S., ..."
    for e in entries:
        s = e["surname"].lower()
        y = e["year"]
        if s == "page":
            lookup[("page", y)] = e["n"]
        if s == "brin":
            lookup[("brin", y)] = e["n"]
        if "ethereum" in s.lower() or s.startswith("ethereum"):
            lookup[("ethereum improvement proposals", y)] = e["n"]
            lookup[("eip", y)] = e["n"]
        if s == "gmx":
            lookup[("gmx", y)] = e["n"]
        if s == "do":
            lookup[("do", y)] = e["n"]
        if s == "langville":
            lookup[("langville", y)] = e["n"]
        if s == "packin":
            lookup[("packin", y)] = e["n"]
            lookup[("packin and lev-aretz", y)] = e["n"]
            lookup[("packin & lev-aretz", y)] = e["n"]
        if "gy" in s and "ngyi" in e["author_block"].lower().replace('\\', ''):
            lookup[("gyongyi", y)] = e["n"]
            lookup[("gyöngyi", y)] = e["n"]
        if s.startswith("sch"):
            # Schär
            lookup[("schar", y)] = e["n"]
            lookup[("schär", y)] = e["n"]
            lookup[('sch\\"{a}r', y)] = e["n"]
        if s == "cronbach":
            lookup[("cronbach", y)] = e["n"]
            lookup[("cronbach and meehl", y)] = e["n"]
            lookup[("cronbach & meehl", y)] = e["n"]
        if s == "resnick":
            lookup[("resnick", y)] = e["n"]
            lookup[("resnick and zeckhauser", y)] = e["n"]
        if s == "antonopoulos":
            lookup[("antonopoulos", y)] = e["n"]
            lookup[("antonopoulos and wood", y)] = e["n"]
        if s == "wood" and y == "2014":
            lookup[("wood", y)] = e["n"]
        if s == "nakamoto":
            lookup[("nakamoto", y)] = e["n"]
        if s == "buterin":
            lookup[("buterin", y)] = e["n"]
        if s == "szabo":
            lookup[("szabo", y)] = e["n"]
        if s == "spearman":
            lookup[("spearman", y)] = e["n"]
        if s == "kendall":
            lookup[("kendall", y)] = e["n"]
        if s == "douceur":
            lookup[("douceur", y)] = e["n"]
        if s == "kleinberg":
            lookup[("kleinberg", y)] = e["n"]
        if s == "kamvar":
            lookup[("kamvar", y)] = e["n"]
        if s == "lin":
            lookup[("lin", y)] = e["n"]
        if s == "kotb":
            lookup[("kotb", y)] = e["n"]
        if s == "hassija":
            lookup[("hassija", y)] = e["n"]
        if s == "werner":
            lookup[("werner", y)] = e["n"]
        if s == "harvey":
            lookup[("harvey", y)] = e["n"]
        if s == "gudgeon":
            # two Gudgeon 2020 entries - first wins unless we disambiguate
            if ("gudgeon", y) not in lookup:
                lookup[("gudgeon", y)] = e["n"]
        if s == "haveliwala":
            lookup[("haveliwala", y)] = e["n"]
        if s == "jeh":
            lookup[("jeh", y)] = e["n"]
        if s == "torres":
            lookup[("torres", y)] = e["n"]
        if s == "victor":
            lookup[("victor", y)] = e["n"]
        if s == "daian":
            lookup[("daian", y)] = e["n"]
        if s == "zhou":
            lookup[("zhou", y)] = e["n"]
        if s == "qin":
            lookup[("qin", y)] = e["n"]
        if s == "perez":
            lookup[("perez", y)] = e["n"]
        if s == "angeris":
            lookup[("angeris", y)] = e["n"]
        if s == "li" and y == "2022":
            lookup[("li", y)] = e["n"]
        if s == "bonneau":
            lookup[("bonneau", y)] = e["n"]
        if s == "gervais":
            lookup[("gervais", y)] = e["n"]
        if s == "kalodner":
            lookup[("kalodner", y)] = e["n"]
        if s == "narayanan":
            lookup[("narayanan", y)] = e["n"]
        if s == "chen" and y == "2020":
            lookup[("chen", y)] = e["n"]
        if s == "zetzsche":
            lookup[("zetzsche", y)] = e["n"]
        if s == "xu":
            lookup[("xu", y)] = e["n"]
        if s == "bartoletti":
            lookup[("bartoletti", y)] = e["n"]
    return lookup


def normalize_author_token(tok: str) -> str:
    t = tok.strip()
    t = t.replace(r"\&", "&")
    t = t.replace(r"\"{a}", "a").replace(r"\"{o}", "o").replace(r"\"{u}", "u")
    t = t.replace(r"\'{e}", "e").replace(r"\"{A}", "A")
    t = t.replace(r"\"{a}", "a")
    # Sch\"{a}r / Gy\"{o}ngyi style
    t = re.sub(r'\\"\{([aouAOU])\}', lambda m: {"a": "a", "o": "o", "u": "u", "A": "a", "O": "o", "U": "u"}[m.group(1)], t)
    t = re.sub(r"\\[a-zA-Z]+\{([^}]*)\}", r"\1", t)
    t = t.replace("~", " ").replace(r"\ ", " ")
    t = re.sub(r"\s+", " ", t).strip().lower()
    # strip leading non-author prefixes: "eip-20; ethereum..." handled upstream
    t = re.sub(r"\s+et\s*al\.?$", "", t)
    t = t.replace(" & ", " and ")
    return t


def resolve_cite_unit(unit: str, lookup: dict[tuple[str, str], int]) -> int | None:
    """Resolve 'Nakamoto, 2008' or 'Page et al., 1998' or 'Do et al., 2023'."""
    unit = unit.strip()
    # Drop leading non-citation labels: "EIP-20; Ethereum..." or "Sybil identities; Douceur..."
    if ";" in unit and not re.search(r"\d{4}|n\.d\.", unit.split(";")[0]):
        unit = unit.split(";", 1)[1].strip()
    # Leading token without year: "EIP-20; Ethereum Improvement Proposals, 2015"
    if ";" in unit:
        parts = [p.strip() for p in unit.split(";")]
        # Prefer the part that has author+year
        for p in reversed(parts):
            if re.search(r"\d{4}|n\.d\.", p) and re.search(r"[A-Za-z]", p):
                unit = p
                break

    ym = re.search(r",\s*(\d{4}|n\.d\.)\s*$", unit)
    if not ym:
        ym = re.search(r"(\d{4}|n\.d\.)\s*$", unit)
        if not ym:
            return None
        year = ym.group(1)
        author = unit[: ym.start()].strip().rstrip(",").strip()
    else:
        year = ym.group(1)
        author = unit[: ym.start()].strip()
    author = normalize_author_token(author)
    # strip trailing punctuation
    author = author.rstrip(".")
    key = (author, year)
    if key in lookup:
        return lookup[key]
    if " and " in author:
        if (author, year) in lookup:
            return lookup[(author, year)]
        # first surname of "packin and lev-aretz"
        first = author.split(" and ")[0].strip()
        if (first, year) in lookup:
            return lookup[(first, year)]
    first = author.split()[0] if author.split() else author
    # schar / gyongyi
    if first.startswith("schar") or "schar" in author:
        return lookup.get(("schar", year))
    if "gyongyi" in author or first.startswith("gy"):
        return lookup.get(("gyongyi", year))
    if (first, year) in lookup:
        return lookup[(first, year)]
    if "ethereum" in author:
        return lookup.get(("ethereum improvement proposals", year))
    if author.startswith("gmx"):
        return lookup.get(("gmx", year))
    return None


def parenthetical_to_cend(match: re.Match, lookup: dict) -> str:
    inner = match.group(1)
    # Skip non-citation parentheses (equations, n=5521, etc.)
    if not re.search(r"\d{4}|n\.d\.", inner):
        return match.group(0)
    # Skip math-like parentheses (not LaTeX accents like \"{a} or \&)
    if any(x in inner for x in ("=", "<", ">", "approx", "leq", "geq", "cdot", "times")):
        return match.group(0)
    if re.search(r"\\\\(?:frac|sum|prod|int|mathbb|mathcal|text|texttt)", inner):
        return match.group(0)
    # Split on semicolons
    units = [u.strip() for u in inner.split(";")]
    nums: list[int] = []
    for u in units:
        # Skip non-citation fragments (e.g. "Sybil identities", "EIP-20")
        if not re.search(r"\d{4}|n\.d\.", u):
            continue
        # Handle "Ethereum Improvement Proposals, 2015, 2020" as two years
        multi_years = re.match(
            r"^(.+?),\s*((?:\d{4}|n\.d\.)(?:\s*,\s*(?:\d{4}|n\.d\.))+)$", u
        )
        if multi_years:
            author = multi_years.group(1).strip()
            # Drop leading labels like "EIP-20; " already split away
            years = re.findall(r"\d{4}|n\.d\.", multi_years.group(2))
            for y in years:
                n = resolve_cite_unit(f"{author}, {y}", lookup)
                if n is None:
                    return match.group(0)
                if n not in nums:
                    nums.append(n)
            continue
        n = resolve_cite_unit(u, lookup)
        if n is None:
            return match.group(0)
        if n not in nums:
            nums.append(n)
    if not nums:
        return match.group(0)
    return "\\cend{" + ",".join(str(n) for n in nums) + "}"


def narrative_to_cend(match: re.Match, lookup: dict) -> str:
    """Author (year) or Author et al. (year) -> Author\\cend{n} or Author et al.\\cend{n}"""
    author = match.group(1)
    year = match.group(2)
    unit = f"{author}, {year}"
    n = resolve_cite_unit(unit, lookup)
    if n is None:
        return match.group(0)
    # Preserve author text, drop (year)
    return f"{author}\\cend{{{n}}}"


def convert_text(text: str, lookup: dict) -> str:
    # 1) Parenthetical citations: (A, 2008; B, 2014)
    # Avoid matching already-converted or labels
    def paren_repl(m: re.Match) -> str:
        return parenthetical_to_cend(m, lookup)

    # Only match parens that contain a year
    text = re.sub(
        r"\(([^()]*(?:\d{4}|n\.d\.)[^()]*)\)",
        paren_repl,
        text,
    )

    # 2) Narrative: Author (year) / Author et al. (year) / Author \& Author (year)
    # Patterns like: Page et al.\ (1998), Do et al.\ (2023), Packin \& Lev-Aretz (2024)
    narr_pat = re.compile(
        r"(?<!\\cend\{)"
        r"((?:[A-Z][\w\\\'\"{}\.-]+(?:\s+(?:and|&|\\&)\s+[A-Z][\w\\\'\"{}\.-]+)?|"
        r"[A-Z][\w\\\'\"{}\.-]+(?:\s+et\s+al\.?)?|"
        r"Ethereum Improvement Proposals|GMX|"
        r"Packin\s*(?:and|\\&|&)\s*Lev-Aretz|"
        r"Cronbach\s*(?:and|\\&|&)\s*Meehl|"
        r"Antonopoulos\s*(?:and|\\&|&)\s*Wood|"
        r"Resnick\s*(?:and|\\&|&)\s*Zeckhauser|"
        r"Langville\s*(?:and|\\&|&)\s*Meyer|"
        r"Brin\s*(?:and|\\&|&)\s*Page|"
        r"Gy\\\"\{o\}ngyi|Sch\\\"\{a\}r)"
        r"(?:\s+et\s+al\.?)?)"
        r"\s*\((\d{4}|n\.d\.)\)"
    )

    def narr_repl(m: re.Match) -> str:
        return narrative_to_cend(m, lookup)

    # Multiple passes for remaining narrative cites - simpler pattern
    narr_pat2 = re.compile(
        r"([A-Za-z\\\'\"{}\.-]+(?:\s+(?:et\s+al\.|and|&|\\&)\s+[A-Za-z\\\'\"{}\.-]+)*(?:\s+et\s+al\.)?)"
        r"\s*\((\d{4}|n\.d\.)\)"
    )

    def narr_repl2(m: re.Match) -> str:
        author = m.group(1)
        # skip if author looks like a number or command
        if author.strip().startswith("\\") and "cend" in author:
            return m.group(0)
        if re.match(r"^[\d\.]+$", author.strip()):
            return m.group(0)
        # skip common non-author words
        skip = {
            "section",
            "chapter",
            "table",
            "figure",
            "equation",
            "claim",
            "hypothesis",
            "algorithm",
            "appendix",
            "row",
            "rows",
            "stage",
            "stages",
            "window",
            "cohort",
            "pool",
            "method",
            "methods",
            "family",
            "families",
            "proxy",
            "proxies",
            "score",
            "scores",
            "rank",
            "ranks",
            "edge",
            "edges",
            "node",
            "nodes",
            "wallet",
            "wallets",
            "runtime",
            "speedup",
            "iteration",
            "iterations",
            "tolerance",
            "damping",
            "default",
            "primary",
            "secondary",
            "supplementary",
            "matched",
            "expanded",
            "observation",
            "minimum",
            "maximum",
            "approximately",
            "about",
            "see",
            "cf",
            "e.g",
            "i.e",
            "vs",
            "versus",
            "through",
            "from",
            "between",
            "within",
            "under",
            "over",
            "after",
            "before",
            "since",
            "until",
            "during",
            "including",
            "excluding",
            "using",
            "via",
            "per",
            "at",
            "in",
            "on",
            "of",
            "to",
            "for",
            "with",
            "by",
            "as",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",  # careful: Do et al. is author
            "n",
            "N",
            "d",
            "k",
            "t",
            "m",
            "w",
            "u",
            "v",
            "G",
            "P",
            "E",
            "V",
            "W",
            "T",
            "C",
            "H",
            "RQ",
            "SRQ",
            "SC",
            "H1",
            "H2",
            "H3",
            "C1",
            "C2",
            "C3",
            "C4",
            "AWP",
            "GF-PR",
            "EndorseRank",
            "PageRank",
            "ERC-20",
            "GMX",
            "DeFi",
            "L2",
            "EOA",
            "PnL",
            "SQL",
            "ABI",
            "UTC",
            "USD",
            "BigQuery",
            "Arbitrum",
            "Ethereum",
            "Bitcoin",
            "Tier",
        }
        # "Do et al." is author - allow "Do" only with et al
        a_norm = normalize_author_token(author)
        if a_norm in skip and "et al" not in author.lower():
            # Special case: Do et al. - author is "Do"
            if a_norm == "do" and "et al" not in author.lower():
                return m.group(0)
            if a_norm != "do":
                return m.group(0)
        # Capitalized author names typically
        if not re.search(r"[A-Z]", author):
            return m.group(0)
        return narrative_to_cend(m, lookup)

    # Apply narrative conversion carefully - only when author starts with capital
    text = re.sub(
        r"(?<!\[)"
        r"((?:[A-Z][A-Za-z\\\'\"{}\.-]+|"
        r"Sch\\\"\{a\}r|Gy\\\"\{o\}ngyi|"
        r"Ethereum Improvement Proposals)"
        r"(?:\s+(?:et\s+al\.|and|&|\\&)\s+[A-Z][A-Za-z\\\'\"{}\.-]+)*"
        r"(?:\s+et\s+al\.)?)"
        r"\s*\((\d{4}|n\.d\.)\)",
        narr_repl2,
        text,
    )
    return text


def write_bibliography(entries: list[dict]) -> None:
    lines = [
        "% !TEX root = ../main.tex",
        "\\clearpage",
        "\\chapter*{References}",
        "\\label{ch:references}",
        "",
        "\\begin{enumerate}[label={[{{\\arabic*}}]}, leftmargin=*, itemsep=0.35em, parsep=0pt]",
    ]
    for e in entries:
        # strip leading author formatting - entry text is full APA entry
        lines.append(f"  \\item\\phantomsection\\label{{ref:{e['n']}}} {e['text']}")
    lines.append("\\end{enumerate}")
    lines.append("")
    BIB.write_text("\n".join(lines) + "\n", encoding="utf-8")


def ensure_cend_command() -> None:
    text = PREAMBLE.read_text(encoding="utf-8")
    if "\\newcommand{\\cend}" in text or "\\newcommand{\\cend}[" in text:
        return
    snippet = r"""
% Numbered endnote-style citations (list in Section 7 References).
% Footnotes (\footnote{...}) remain available for page-bottom notes.
\newcommand{\cend}[1]{%
  \textsuperscript{%
    \def\cendsep{}%
    \@for\cendn:=#1\do{%
      \cendsep\hyperref[ref:\cendn]{[\cendn]}%
      \def\cendsep{,}%
    }%
  }%
}
\makeatletter
\renewcommand{\cend}[1]{%
  \textsuperscript{%
    \def\cend@sep{}%
    \@for\cend@n:=#1\do{%
      \cend@sep\hyperref[ref:\cend@n]{[\cend@n]}%
      \def\cend@sep{,}%
    }%
  }%
}
\makeatother
"""
    # Simpler version without makeatletter mess
    snippet = r"""
% Numbered endnote-style citations (list in Section 7 References).
% Use \footnote{...} for page-bottom notes (각주); references are endnotes (미주).
\newcommand{\cend}[1]{\textsuperscript{\cendlist{#1}}}
\newcommand{\cendlist}[1]{\cendlistparse#1,\relax}
\def\cendlistparse#1,#2\relax{%
  \hyperref[ref:#1]{[#1]}%
  \ifx\relax#2\relax\else,\cendlistparse#2\relax\fi
}
"""
    # Even simpler - only support single or pre-joined
    snippet = r"""
% Numbered endnote-style citations pointing to Section 7 References (미주).
% Page-bottom notes use \footnote{...} (각주).
\newcommand{\cend}[1]{\textsuperscript{\cendrefs{#1}}}
\makeatletter
\newcommand{\cendrefs}[1]{%
  \@for\@cendnum:=#1\do{%
    \hyperref[ref:\@cendnum]{[\@cendnum]}%
    \unless\ifx\@cendnum\@cendlast
      \@cend@comma
    \fi
  }%
}
% Helper: print commas between items
\def\@cend@comma{,}
\makeatother
"""
    # The \@for approach with trailing comma is tricky. Use a clean implementation:
    snippet = r"""
% Numbered endnote-style citations pointing to Section 7 References (미주).
% Page-bottom notes use \footnote{...} (각주).
\makeatletter
\newcommand{\cend}[1]{%
  \textsuperscript{%
    \def\cend@sep{}%
    \@for\cend@tmp:=#1\do{%
      \cend@sep\hyperref[ref:\cend@tmp]{[\cend@tmp]}%
      \def\cend@sep{,}%
    }%
  }%
}
\makeatother
"""
    text = text.rstrip() + "\n" + snippet + "\n"
    PREAMBLE.write_text(text, encoding="utf-8")


def main() -> None:
    bib_text = BIB.read_text(encoding="utf-8")
    entries = parse_bib_entries(bib_text)
    print(f"parsed {len(entries)} bibliography entries")
    for e in entries:
        print(f"  [{e['n']}] {e['surname']} ({e['year']})")
    lookup = build_lookup(entries)
    write_bibliography(entries)
    ensure_cend_command()

    unresolved: list[str] = []
    for path in TARGETS:
        if not path.exists():
            continue
        original = path.read_text(encoding="utf-8")
        converted = convert_text(original, lookup)
        # Find remaining author-year patterns
        leftovers = re.findall(
            r"\([^)]*(?:19|20)\d{2}[^)]*\)|[A-Z][a-z]+(?:\s+et\s+al\.)?\s*\((?:19|20)\d{2}\)",
            converted,
        )
        # filter false positives
        real = []
        for L in leftovers:
            if re.search(
                r"Nakamoto|Page|Do |Wood|Sch|Packin|Langville|Kendall|Spearman|Douceur|GMX|Ethereum|Werner|Harvey|Cronbach|Brin|Buterin|Szabo|Kleinberg|Kamvar|Lin |Kotb|Hassija|Qin|Perez|Daian|Zhou|Victor|Torres|Angeris|Bonneau|Gervais|Kalodner|Narayanan|Gudgeon|Haveliwala|Jeh |Resnick|Antonopoulos|Gy",
                L,
            ):
                real.append(L)
        if real:
            unresolved.append(f"{path.name}: {real[:8]}")
        path.write_text(converted, encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")

    if unresolved:
        print("POSSIBLE UNRESOLVED:")
        for u in unresolved:
            print(" ", u)
    else:
        print("no obvious unresolved citation patterns")


if __name__ == "__main__":
    main()
