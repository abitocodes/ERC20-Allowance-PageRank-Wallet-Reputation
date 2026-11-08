"""The gate B SQL of the contract-graph revision (sql/36 to 42, docs/revision_contract_graph.md sections 5 to 9 and the
gate B amendment of section 13) as text and as expressions.

The text checks read the files with their comments removed and their whitespace collapsed (c12_world.normal): the
parts copied from sql/13, 14, 15, 16, 17 and 35 must be those lines word for word, the export tables must have the
columns of the INTERFACE (c12_world.INTERFACE, the copy every synthetic fixture writes) and sql/42 the invariants of
the gate B decisions. The cap of the allowances (usd_eff) is also executed: c12_world.bq_eval evaluates the BigQuery
expression of sql/36 and sql/41 with BigQuery's NULL semantics, against the Python mirror usd.effective_usd and the
predicate of sql/35 that the structure pilot counted. Everything runs in this process except the few reads of the
driver's constants (run_json, under CONTRACT_REP_VARIANT=contract12m)."""

from __future__ import annotations

import ast
import json
import math
import os
import re
import subprocess
import sys
import textwrap

import numpy as np
import pytest

import c12_world as w
from c12_world import DOWNLOADS, INTERFACE, LABELS, PARTS, SPLIT, bq_eval, lines, normal, select_aliases, statement
from conftest import EXPERIMENTS, SCRIPTS

SQL = EXPERIMENTS / "sql"
GATE_B_SQL = tuple(sorted(p.name for p in SQL.glob("*.sql") if re.fullmatch(r"(3[6-9]|4[0-2])_c12_.*\.sql", p.name)))
# The files the gate B SQL copies from.
SQL13, SQL14, SQL15 = "sql/13_usd_constants.sql", "sql/14_usd_anchor_pairs.sql", "sql/15_usd_proxies.sql"
SQL16, SQL17, SQL35 = "sql/16_usd_labels.sql", "sql/17_usd_export_ids.sql", "sql/35_c12_structure.sql"
# The job of each gate B file (the first comment block names it).
FILE_JOBS = {"36_c12_allow_triples.sql": 36, "36_c12_user_events.sql": 36, "36_c12_constants.sql": 36,
             "37_c12_pairs.sql": 37, "38_c12_cohorts.sql": 38, "38_c12_proxies.sql": 38, "39_c12_label_parts.sql": 39,
             "40_c12_export_ids.sql": 40, "41_c12_importance.sql": 41, "42_c12_checks.sql": 42}
# The cap of sql/36_c12_allow_triples.sql (revision section 5): the allowance at the anchor day's price, the balance
# at the anchor in base units set to 0 below 10^(decimals - @dust_digits) base units, and their minimum.
USD_ALLOW = "value / POW(10.0, decimals) * price_usd"
USD_BAL = "IF(bal >= POW(10.0, decimals - CAST(@dust_digits AS INT64)), bal, 0.0) / POW(10.0, decimals) * price_usd"
USD_EFF = f"LEAST({USD_ALLOW}, {USD_BAL})"
PARAMS = {"dust_digits": "6"}
CONSTANT_COLUMNS = ("m_transfer", "p99_transfer", "p10_transfer", "p90_transfer", "n_transfers", "m_allowance",
                    "p99_allowance", "p10_allowance", "p90_allowance", "n_latest_allowances", "n_positive_allowances",
                    "n_capped_to_zero", "n_capped_below_allowance", "n_unlimited_positive", "m_user_transfer",
                    "p99_user_transfer", "p10_user_transfer", "p90_user_transfer", "n_user_transfers")


def run_json(code: str):
    """``code`` in a fresh interpreter under contract12m from scripts/; the JSON of its last stdout line."""
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8",
           "CONTRACT_REP_VARIANT": "contract12m"}
    env.pop("CONTRACT_REP_RPC_URL", None)
    out = subprocess.run([sys.executable, "-c", textwrap.dedent(code)], cwd=SCRIPTS, env=env, capture_output=True,
                         text=True, encoding="utf-8")
    assert out.returncode == 0, out.stdout[-2000:] + out.stderr[-4000:]
    return json.loads(out.stdout.strip().splitlines()[-1])


def body(name: str, subs: dict | None = None) -> str:
    """normal() of a SQL file (a file name of sql/ or a path relative to experiments/)."""
    return normal(w.sql_text(name, subs))


def _close(s: str, i: int) -> int:
    """The index of the parenthesis that closes the one at ``i`` (string literals and quoted names skipped)."""
    depth, quote = 0, None
    for j in range(i, len(s)):
        c = s[j]
        if quote:
            quote = None if c == quote else quote
        elif c in "'`\"":
            quote = c
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return j
    raise ValueError(f"unbalanced parenthesis at {i}")


def _depth0(s: str, sep: str) -> list[int]:
    """The positions of ``sep`` outside parentheses, string literals and quoted names."""
    out, depth, quote, j = [], 0, None, 0
    while j < len(s):
        c = s[j]
        if quote:
            quote = None if c == quote else quote
        elif c in "'`\"":
            quote = c
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        elif depth == 0 and s.startswith(sep, j):
            out.append(j)
        j += 1
    return out


def split0(s: str, sep: str) -> list[str]:
    """``s`` split at ``sep`` outside parentheses, each part stripped."""
    cuts = _depth0(s, sep)
    return [p.strip() for p in (s[a:b] for a, b in zip([0, *(c + len(sep) for c in cuts)], [*cuts, len(s)]))]


def statements(s: str) -> list[str]:
    """The statements of a normalised file, each with its closing ';'."""
    return [p + ";" for p in split0(s, ";") if p]


def creates(s: str) -> list[str]:
    """The tables a normalised text creates, in order."""
    return re.findall(r"CREATE OR REPLACE TABLE `(\w+)`", s)


def cte(stmt: str, name: str) -> str:
    """The text inside the parentheses of the CTE ``name`` of a normalised statement."""
    m = re.search(rf"(?:\bWITH|,) {name} AS \(", stmt)
    assert m, f"no CTE {name}"
    return stmt[m.end():_close(stmt, m.end() - 1)].strip()


def select_list(stmt: str) -> str:
    """The text of the select list of the last top-level SELECT of a statement (up to its FROM)."""
    s = stmt.strip().rstrip(";")
    starts = [m.end() for m in re.finditer(r"\bSELECT\b", s) if not _inside(s, m.start())]
    end = min(m.start() for m in re.finditer(r"\bFROM\b", s) if m.start() > starts[-1] and not _inside(s, m.start()))
    return s[starts[-1]:end].strip()


def _inside(s: str, i: int) -> bool:
    """Whether position ``i`` lies inside parentheses (string literals and quoted names skipped)."""
    depth, quote = 0, None
    for c in s[:i]:
        if quote:
            quote = None if c == quote else quote
        elif c in "'`\"":
            quote = c
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
    return depth > 0


def check_row(sql42: str, name: str) -> str:
    """The text of the row ``name`` of sql/42 (from SELECT 'name' to the next UNION ALL)."""
    i = sql42.index(f"SELECT '{name}'")
    ends = [j for j in _depth0(sql42, " UNION ALL ") if j > i]
    return sql42[i:ends[0] if ends else len(sql42)].strip().rstrip(";")


def check_names(text: str) -> list[str]:
    """The check names of sql/42 in order (the parse of the driver's checks test)."""
    s = re.sub(r"--[^\n]*", "", text)
    return re.findall(r"'(\w+)' AS check_name", s) + re.findall(r"UNION ALL\s+SELECT '(\w+)'", s)


# --------------------------------------------------------------------------- the evaluator itself


def test_the_expression_evaluator():
    assert bq_eval("LEAST(1, NULL)") is None
    assert bq_eval("IF(NULL >= 1, 2, 3)") == 3
    assert bq_eval("NULL AND FALSE") is False
    assert bq_eval("NULL OR TRUE") is True
    assert bq_eval("IFNULL(NULL >= 1, FALSE)") is False
    assert bq_eval("POW(10.0, x - CAST(@k AS INT64))", {"x": 18}, {"k": "6"}) == 1e12
    assert bq_eval("b.bal_t1 >= 2", {"bal_t1": 3}) is True
    # the rest of the NULL semantics the cap and the predicates use
    assert bq_eval("NULL AND TRUE") is None and bq_eval("NULL OR FALSE") is None and bq_eval("NOT NULL") is None
    assert bq_eval("NULL + 1") is None and bq_eval("NULL = NULL") is None and bq_eval("x IS NULL", {"x": None}) is True
    assert bq_eval("x IS NOT NULL", {"x": 0.0}) is True and bq_eval("GREATEST(2, 3.5)") == 3.5
    assert bq_eval("kind = 'T' AND usd IS NOT NULL", {"kind": "T", "usd": 1.0}) is True
    assert bq_eval("b.bal_t1", {"b.bal_t1": 7, "bal_t1": 9}) == 7    # the prefixed name first
    for bad in ("LEAST(1,", "1 +", "IF(1, 2)", "(1", "1 2", "FOO(1)", "", "CAST(1 AS STRING)", "x IS 3"):
        with pytest.raises(ValueError):
            bq_eval(bad)
    with pytest.raises(KeyError):
        bq_eval("y + 1", {"x": 1})
    with pytest.raises(KeyError):
        bq_eval("@k + 1")


# --------------------------------------------------------------------------- the pair tables copy sql/14


def test_pairs_copy_sql14():
    s = body("37_c12_pairs.sql")
    funcs = [st for st in statements(s) if st.startswith("CREATE TEMP FUNCTION")]
    assert " ".join(funcs) == lines(SQL14, 18, 19)
    tables = [st for st in statements(s) if st.startswith("CREATE OR REPLACE TABLE")]
    assert creates(" ".join(tables)) == ["c12_transfer_pairs", "c12_allow_pairs", "c12_allow_pairs_unc"]
    tp = statement(s, "c12_transfer_pairs")
    assert tp == tables[0]                                       # the transfer statement comes first
    head = "tag, from_address, to_address, "
    assert select_list(tp).startswith(head) and select_list(tp)[len(head):] == lines(SQL14, 51, 59)
    i = tp.index("FROM (") + len("FROM ")
    inner = tp[i + 1:_close(tp, i)]
    branches = split0(inner, " UNION ALL ")
    assert len(branches) == 2
    age = lines(SQL14, 62, 62)
    assert age == "TIMESTAMP_DIFF(TIMESTAMP(@anchor_ts), block_timestamp, MICROSECOND) / 8.64e10 AS age_days"
    for branch, (tag, start, anchor) in zip(branches, (("t1", "start_ts", "t1"), ("tobs", "tobs_start", "tobs"))):
        assert branch.startswith(f"SELECT '{tag}' AS tag, a AS from_address, b AS to_address, usd, block_timestamp, ")
        assert age.replace("@anchor_ts", f"@{anchor}") in branch, branch
        assert branch.endswith(f"FROM `c12_events_cc` WHERE kind = 'T' AND block_timestamp >= TIMESTAMP(@{start}) "
                               f"AND block_timestamp <= TIMESTAMP(@{anchor}) AND usd IS NOT NULL"), branch
    assert tp.endswith(") GROUP BY tag, from_address, to_address;")
    for table, value, where in (("c12_allow_pairs", "usd_eff", " WHERE usd_eff > 0"), ("c12_allow_pairs_unc",
                                                                                     "usd_allow", "")):
        st = statement(s, table)
        aggregates = re.sub(r"\busd\b", value, lines(SQL14, 39, 45))
        assert st == (f"CREATE OR REPLACE TABLE `{table}` CLUSTER BY tag AS SELECT tag, owner, spender, {aggregates} "
                      f"FROM `c12_allow_triples`{where} GROUP BY tag, owner, spender;"), st
    # self-pairs and zero-weight pairs are kept (revision section 5)
    for kept in ("owner != spender", "from_address != to_address", "a != b", "HAVING", "w_er > 0", "w_awp > 0",
                 "w_raw > 0"):
        assert kept not in s, kept


# --------------------------------------------------------------------------- the cap and its Python mirror


def grid() -> list[dict]:
    """The rows of the cap test: decimals x value x balance (None = no c12_bal row) x price, 162 rows."""
    rows = []
    for dec in (6, 8, 18):
        for value in (1.0, 10.0 ** dec, float(2 ** 256 - 1)):
            for bal in (None, -3.0, 0.0, float(np.nextafter(10.0 ** (dec - 6), 0)), 10.0 ** (dec - 6),
                        5 * 10.0 ** dec):
                for price in (0.0, 1.0, 2500.0):
                    rows.append({"value": value, "decimals": dec, "bal": bal, "price_usd": price})
    return rows


def eff(row: dict) -> float:
    return bq_eval(USD_EFF, row, PARAMS)


def test_cap_expression_is_shared_and_mirrored():
    import usd

    triples = statement(w.sql_text("36_c12_allow_triples.sql"), "c12_allow_triples")
    for expr, alias in ((USD_ALLOW, "usd_allow"), (USD_BAL, "usd_bal"), (USD_EFF, "usd_eff")):
        assert f"{expr} AS {alias}" in triples, alias
    assert f"SUM({USD_EFF}) AS s" in cte(statement(w.sql_text("41_c12_importance.sql"), "c12_importance_raw"), "auth")
    # the balance test is the predicate of sql/35 line 38 on the triple's own columns
    test = lines(SQL35, 38, 38)
    assert test.startswith("WHERE ")
    test = test[len("WHERE "):].replace("b.bal_t1", "bal").replace("t.decimals", "decimals")
    assert f"IF({test}, bal, 0.0)" in USD_BAL
    rows = grid()
    assert len(rows) == 162
    got = np.array([eff(r) for r in rows], dtype=np.float64)
    mirror = np.array([usd.effective_usd([r["value"]], [r["decimals"]], [r["price_usd"]],
                                         [math.nan if r["bal"] is None else r["bal"]], dust_digits=6)[0]
                       for r in rows], dtype=np.float64)
    np.testing.assert_array_equal(got, mirror)
    spot = [
        ({"value": 1e8, "decimals": 6, "bal": 5e7, "price_usd": 1.0}, 50.0),            # 100 USDC allowed, 50 held
        ({"value": float(2 ** 256 - 1), "decimals": 18, "bal": 5e18, "price_usd": 2500.0}, 12500.0),   # unlimited
        ({"value": 1e18, "decimals": 18, "bal": 1e12, "price_usd": 2500.0}, 1e12 / 10.0 ** 18 * 2500.0),
        ({"value": 1e18, "decimals": 18, "bal": float(np.nextafter(1e12, 0)), "price_usd": 2500.0}, 0.0),
        ({"value": 1e18, "decimals": 18, "bal": -3.0, "price_usd": 2500.0}, 0.0),
        ({"value": 1e18, "decimals": 18, "bal": None, "price_usd": 2500.0}, 0.0),
        ({"value": 1e18, "decimals": 18, "bal": 5e18, "price_usd": 0.0}, 0.0),
    ]
    for row, want in spot:
        assert eff(row) == want, row
    for name in GATE_B_SQL:
        assert "bal_0930" not in w.sql_text(name), name


# --------------------------------------------------------------------------- the t1 branches are the pilot's


def test_t1_branches_have_the_predicates_of_sql35():
    triples = statement(w.sql_text("36_c12_allow_triples.sql"), "c12_allow_triples")
    latest = {tag: cte(triples, f"latest_{tag}") for tag in ("t1", "tobs")}
    m = re.search(r"SELECT token, a AS owner.*WHERE rn = 1 AND value > 0", latest["t1"])
    assert m, latest["t1"]
    inner = m.group(0)
    assert ", block_timestamp, ROW_NUMBER()" in inner
    assert inner.replace(", block_timestamp, ROW_NUMBER()", ", ROW_NUMBER()", 1) == lines(SQL35, 23, 30)
    assert latest["tobs"] == latest["t1"].replace("@start_ts", "@tobs_start").replace("@t1)", "@tobs)")
    assert lines(SQL35, 37, 37) == "JOIN `u_prices` AS p ON p.token = l.token AND p.day = DATE(TIMESTAMP(@t1))"
    assert lines(SQL35, 37, 37) in cte(triples, "valued")
    # Each freeze takes its own latest allowances, the owner's balance at its own anchor and the price of its own
    # anchor day: the T_obs branch of valued is the t1 branch with every t1 name replaced (sql/42 compares only the
    # t1 rows with the pilot, so nothing else would notice a T_obs triple capped at the t1 balance or priced on t1).
    branches = split0(cte(triples, "valued"), " UNION ALL ")
    assert len(branches) == 2, branches
    t1 = ("SELECT 't1' AS tag, l.token, l.owner, l.spender, l.value, t.decimals, p.price_usd, b.bal_t1 AS bal, "
          "l.block_timestamp, TIMESTAMP_DIFF(TIMESTAMP(@t1), l.block_timestamp, MICROSECOND) / 8.64e10 AS age_days "
          "FROM latest_t1 AS l JOIN `u_tokens` AS t ON t.token = l.token " + lines(SQL35, 37, 37)
          + " LEFT JOIN `c12_bal` AS b ON b.token = l.token AND b.address = l.owner")
    assert branches[0] == t1, branches[0]
    tobs = (t1.replace("'t1'", "'tobs'").replace("latest_t1", "latest_tobs").replace("b.bal_t1", "b.bal_tobs")
            .replace("@t1)", "@tobs)"))
    assert tobs.count("@tobs)") == 2 and "bal_t1" not in tobs and "@t1" not in tobs
    assert branches[1] == tobs, branches[1]
    tp = statement(w.sql_text("37_c12_pairs.sql"), "c12_transfer_pairs")
    where = lines(SQL35, 44, 47)
    assert where.startswith("WHERE kind = 'T'") and f"FROM `c12_events_cc` {where} UNION ALL" in tp
    # Executed: usd_eff > 0 exactly when the structure pilot's capped predicate holds (a NULL predicate is false:
    # the inner join of sql/35 drops a triple without a c12_bal row, the LEFT JOIN of sql/36 gives it usd_eff 0).
    pred = lines(SQL35, 38, 39)[len("WHERE "):]
    rule = check_row(body("42_c12_checks.sql"), "dust_rule")
    m = re.fullmatch(r"SELECT 'dust_rule', \(SELECT COUNTIF\(IFNULL\((.*), TRUE\)\) FROM triples\)", rule)
    assert m, rule
    dust = m.group(1)
    assert dust.startswith("(usd_eff > 0) != (IFNULL(bal >= POW(10.0, decimals - CAST(@dust_digits AS INT64)), FALSE)")
    for r in grid():
        pilot = bq_eval(pred, {"b.bal_t1": r["bal"], "t.decimals": r["decimals"], "p.price_usd": r["price_usd"]},
                        PARAMS)
        assert (eff(r) > 0) == (pilot is True), r
        assert bq_eval(dust, {**r, "usd_eff": eff(r)}, PARAMS) is False, r
    passing = {"value": 1e18, "decimals": 18, "bal": 5e18, "price_usd": 2500.0}
    assert eff(passing) > 0 and bq_eval(dust, {**passing, "usd_eff": 0.0}, PARAMS) is True
    p = run_json("""
        import json
        import run_contract12m_pipeline as d
        from common import load_config
        jobs = {j.key: j for j in d.all_jobs(load_config())}
        print(json.dumps({k: [jobs[k].params.get("start_ts"), jobs[k].params.get("t1")]
                          for k in ("structure", "triples", "pairs", "checks")}))
    """)
    assert p["triples"] == p["pairs"] == p["checks"] == p["structure"] == ["2025-04-01 00:00:00 UTC",
                                                                           "2026-03-31 23:59:59 UTC"]


# --------------------------------------------------------------------------- the proxies copy sql/15


def test_proxies_copy_sql15():
    st = statement(w.sql_text("38_c12_proxies.sql"), "c12_proxies_tobs")
    rename = lambda s: s.replace("`u_cohort`", "`c12_cohort_tobs`")  # noqa: E731
    assert st[st.index("inbound_all AS ("):] == rename(lines(SQL15, 15, 41))
    t = cte(st, "t")
    first = rename(lines(SQL15, 8, 10))
    assert first.startswith("SELECT x.*, FORMAT_TIMESTAMP('%Y-%m', block_timestamp) AS month,")
    assert t.startswith(first + " FROM (")
    i = t.index("FROM (") + len("FROM ")
    sub = t[i + 1:_close(t, i)].strip()
    assert sub == ("SELECT block_timestamp, a AS from_address, b AS to_address, usd FROM `c12_events_cc` WHERE "
                   "kind = 'T' AND block_timestamp >= TIMESTAMP(@start_ts) AND block_timestamp <= "
                   "TIMESTAMP(@anchor_ts)")
    assert t.endswith(") AS x " + lines(SQL15, 12, 13)), t
    assert select_aliases(st) == list(INTERFACE["proxies_tobs"])


# --------------------------------------------------------------------------- the constants follow sql/13


def test_constants_follow_sql13():
    st = statement(w.sql_text("36_c12_constants.sql"), "c12_constants")
    assert len(re.findall(r"APPROX_QUANTILES\((?:[^()]|\([^()]*\))*, 10000\)", st)) == 3
    # Each column name is tied to its quantile and source: the offset of each quantile is the one sql/13 lines 37-41
    # give it (for its transfers and its allowances alike), and the counts are those of their CTEs. A swap of m_T
    # and U, or of U_user and another percentile, fails here; nothing at run time checks the quantiles' order.
    def items(select: str) -> dict[str, str]:
        return {i.rsplit(" AS ", 1)[1]: i.rsplit(" AS ", 1)[0] for i in split0(select, ",")}

    sql13 = lines(SQL13, 37, 41)
    assert sql13.startswith("SELECT ")
    offsets = {}
    for alias, expr in items(sql13[len("SELECT "):]).items():
        m = re.fullmatch(r"(tr|al)\.q\[OFFSET\((\d+)\)\]", expr)
        if m:
            prefix, suffix = alias.split("_", 1)
            assert suffix == {"tr": "transfer", "al": "allowance"}[m.group(1)], alias
            assert offsets.setdefault(prefix, int(m.group(2))) == int(m.group(2)), alias
    assert offsets == {"m": 5000, "p99": 9900, "p10": 1000, "p90": 9000}
    want = {f"{p}_{s}": f"{x}.q[OFFSET({o})]" for x, s in (("tr", "transfer"), ("al", "allowance"),
                                                            ("ut", "user_transfer")) for p, o in offsets.items()}
    want.update(n_transfers="tr.n", n_latest_allowances="al.n_latest", n_positive_allowances="al.n",
                n_capped_to_zero="al.n_zero", n_capped_below_allowance="al.n_below",
                n_unlimited_positive="al.n_unlimited", n_user_transfers="ut.n")
    got = items(select_list(st))
    assert got == want, {k: (got.get(k), want.get(k)) for k in set(got) | set(want) if got.get(k) != want.get(k)}
    al_counts = items(cte(st, "al")[len("SELECT "):cte(st, "al").index(" FROM ")])
    assert {k: v for k, v in al_counts.items() if k != "q"} == {
        "n_latest": "COUNT(*)", "n": "COUNTIF(usd_eff > 0)", "n_zero": "COUNTIF(usd_eff = 0)",
        "n_below": "COUNTIF(usd_eff > 0 AND usd_eff < usd_allow)",
        "n_unlimited": "COUNTIF(usd_eff > 0 AND value >= CAST(@unlimited AS FLOAT64))"}
    tr = lines(SQL13, 15, 20).replace("`u_transfers`", "`c12_events_cc`").replace("WHERE ", "WHERE kind = 'T' AND ", 1)
    assert tr.startswith("WITH tr AS (") and tr in st
    al = cte(st, "al")
    assert al.startswith("SELECT APPROX_QUANTILES(IF(usd_eff > 0, usd_eff, NULL), 10000) AS q,")
    assert al.endswith("FROM `c12_allow_triples` WHERE tag = 't1'")
    quantile = re.search(r"APPROX_QUANTILES\(((?:[^()]|\([^()]*\))*), 10000\)", al).group(1)
    assert "@unlimited" not in quantile          # unlimited allowances enter, capped at the balance
    ut = cte(st, "ut")
    assert ut == ("SELECT APPROX_QUANTILES(usd, 10000) AS q, COUNT(*) AS n FROM `c12_user_events` WHERE kind = 'T' "
                  "AND to_contract AND block_timestamp >= TIMESTAMP(@start_ts) AND block_timestamp <= TIMESTAMP(@t1)")
    assert select_aliases(st) == list(CONSTANT_COLUMNS)
    assert {"m_transfer", "m_allowance", "p99_transfer", "p99_user_transfer"} <= set(CONSTANT_COLUMNS)
    r = run_json("""
        import json
        import run_contract12m_pipeline as d
        print(json.dumps(list(getattr(d, "CONSTANT_COLUMNS", ()))))
    """)
    assert r == list(CONSTANT_COLUMNS)


# --------------------------------------------------------------------------- the label parts copy sql/16


def test_label_parts_copy_sql16():
    s = body("39_c12_label_parts.sql")
    assert lines(SQL16, 12, 15) in s
    copied = lines(SQL16, 18, 98).replace("`u_allow_triples___FREEZE__`", "`u12_allow_triples___FREEZE__`")
    copied = copied.replace("`u_transfers`", "`__SEEN__`")
    assert copied.startswith("WITH t1_pairs AS (") and copied in s
    labels = cte(statement(s, "c12_label_parts___TAG__"), "labels")
    expressions = split0(lines(SQL16, 100, 106), ",")
    assert len(expressions) == 7 and [e.rsplit(" AS ", 1)[1] for e in expressions] == list(LABELS)
    for e in expressions:
        assert e in labels, e
    joins = lines(SQL16, 107, 112)
    assert joins.endswith(";")
    assert joins[:-1] in labels                  # line 112 ends the statement of sql/16; the CTE has no ';'
    st = statement(s, "c12_label_parts___TAG__")
    counted = split0(cte(st, "counted"), " UNION ALL ")
    assert [re.match(r"SELECT (?:DISTINCT )?'(\w+)' AS what", b).group(1) for b in counted] == [
        "t1", "new_appr", "revoked", "new_senders", "drain"]
    t1, new_appr, revoked, new_senders, drain = counted
    assert t1 == "SELECT 't1' AS what, spender, owner AS account, 0.0 AS v FROM t1_pairs"
    assert new_appr.startswith("SELECT DISTINCT 'new_appr'") and lines(SQL16, 33, 33) == (
        "WHERE w.value > 0 AND p.owner IS NULL") and new_appr.endswith(lines(SQL16, 31, 33))
    assert lines(SQL16, 39, 42) in revoked
    assert lines(SQL16, 64, 65) in new_senders and new_senders.endswith("WHERE s.from_address IS NULL")
    assert drain.startswith("SELECT DISTINCT 'drain'") and drain.endswith(lines(SQL16, 94, 96))
    assert cte(st, "cls") == ("SELECT address, 'contract' AS cls FROM `c12_contracts` UNION ALL SELECT address, 'user' "
                              "AS cls FROM `c12_user_accounts`")
    parts = cte(st, "parts")
    assert parts.endswith("FROM counted AS c LEFT JOIN cls AS k ON k.address = c.account GROUP BY c.spender")
    items = split0(select_list(parts), ",")
    assert items[0] == "c.spender" and len(items) == 1 + 18
    predicate = {"user": "k.cls = 'user'", "contract": "k.cls = 'contract'", "other": "k.cls IS NULL"}
    for item in items[1:]:
        part = item.rsplit("_", 1)[1]
        assert predicate[part] in item and sum(p in item for p in predicate.values()) == 1, item
    for tag in ("w0", "w1"):
        t = body("39_c12_label_parts.sql", {"TAG": tag})
        assert select_aliases(statement(t, f"c12_label_parts_{tag}")) == [
            "wallet", "spender_class", *LABELS, "n_t1", "n_t1_user", "n_t1_contract", "n_t1_other",
            *(f"{lab}_{p}" for lab in LABELS for p in PARTS)]
        assert set(select_aliases(statement(t, f"c12_x_label_split_{tag}"))) == set(INTERFACE[f"label_split_{tag}"])
        assert (f"LEFT JOIN `c12_members` AS m ON m.address_bytes = l.spender AND m.list = 'spenders_{tag}';"
                in statement(t, f"c12_label_parts_{tag}"))
        assert "m.class AS spender_class" in select_list(statement(t, f"c12_label_parts_{tag}"))


# --------------------------------------------------------------------------- the export ids follow sql/17


def test_export_ids_follow_sql17():
    s = body("40_c12_export_ids.sql")
    nodes = statement(s, "c12_nodes")
    assert lines(SQL17, 21, 23).startswith("SELECT ROW_NUMBER() OVER (ORDER BY a.address) - 1 AS id,")
    assert lines(SQL17, 21, 23) in nodes
    for table, line, tag in (("c12_x_allow_pairs_tobs", 31, "tobs"), ("c12_x_allow_pairs_t1", 37, "t1"),
                             ("c12_x_allow_pairs_unc_tobs", 37, "tobs"), ("c12_x_allow_pairs_unc_t1", 37, "t1"),
                             ("c12_x_transfer_pairs_tobs", 43, "tobs"), ("c12_x_transfer_pairs_t1", 49, "t1")):
        st = statement(s, table)
        assert st.startswith(f"CREATE OR REPLACE TABLE `{table}` AS {lines(SQL17, line, line)} FROM "), table
        assert st.endswith(f" WHERE p.tag = '{tag}';"), table
        source = "c12_allow_pairs_unc" if "_unc_" in table else table.replace("_x_", "_").rsplit("_", 1)[0]
        assert f"FROM `{source}` AS p JOIN `c12_nodes` AS s" in st, table
    assert "WHERE address IN (SELECT address FROM `c12_contracts`)" in cte(nodes, "a")
    ends = cte(nodes, "ends")
    for src in ("c12_allow_pairs", "c12_allow_pairs_unc", "c12_transfer_pairs"):
        assert f"FROM `{src}`" in ends, src
    assert "SELECT address_bytes FROM `c12_members` WHERE class = 'contract'" in ends
    for lst, flag in w.NODE_FLAGS.items():
        assert (f"a.address IN (SELECT address_bytes FROM `c12_members` WHERE list = '{lst}' AND class = 'contract') "
                f"AS {flag}") in nodes, flag


# --------------------------------------------------------------------------- the checks of sql/42


def _writes() -> tuple[str, ...]:
    """run_bq.WRITES, read from its source (importing run_bq would bind this process to a variant)."""
    tree = ast.parse((SCRIPTS / "run_bq.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "WRITES" for t in node.targets):
            return tuple(ast.literal_eval(node.value))
    raise AssertionError("run_bq.py defines no WRITES")


def documented_checks(text: str) -> list[str]:
    """The check names that the header comment of sql/42 lists in groups ('{tobs,t1}' expanded)."""
    head = " ".join(line.lstrip("-").strip() for line in text.splitlines() if line.startswith("--"))
    head = head[head.index("The names, in groups:") + len("The names, in groups:"):head.index("Parameters:")]
    while re.search(r"\([^()]*\)", head):                 # the explanations in parentheses, nested ones too
        head = re.sub(r"\([^()]*\)", " ", head)
    head = re.sub(r"([a-z0-9_]*)\{([a-z0-9_,]+)\}([a-z0-9_]*)",
                  lambda m: ", ".join(m.group(1) + x + m.group(3) for x in m.group(2).split(",")), head)
    return [item.strip() for item in re.split(r"[,;.]|\b[a-z]+:", head) if item.strip()]


def test_checks_sql():
    text = w.sql_text("42_c12_checks.sql")
    s = normal(text)
    assert creates(s) == ["c12_checks"] and len(re.findall(r"CREATE (?:OR REPLACE )?(?:TABLE|VIEW)", s)) == 1
    names = check_names(text)
    assert len(names) == 64 and len(set(names)) == 64
    writes = re.compile(rf"\b({'|'.join(_writes())})\b", re.I)
    for n in names:
        assert re.fullmatch(r"[a-z0-9_]+", n) and not writes.search(n), n
    documented = documented_checks(text)
    assert all(re.fullmatch(r"[a-z0-9_]+", n) for n in documented), documented
    assert sorted(documented) == sorted(names)       # every name has the form of the comment groups
    assert {"nodes_not_contract", "pair_ends_user_account_tobs", "pair_ends_user_account_t1",
            "cap_above_uncapped_triples", "cap_above_uncapped_pairs", "struct_allow_capped_t1",
            "struct_allow_uncapped_t1", "struct_transfer_t1", "labels_recount_w0", "labels_recount_w1",
            "label_parts_sum_w0", "label_parts_sum_w1", "importance_ids_tobs", "importance_ids_t1",
            "importance_rows_tobs", "importance_rows_t1", "spender_untyped_w0", "spender_untyped_w1",
            "user_accounts_zero_address"} <= set(names)
    assert re.search(r"c12_checks: check_name \(STRING\), violations \(INT64\); 64 rows", text)


# --------------------------------------------------------------------------- user events and importance


def test_user_events_and_importance_shapes():
    ue = statement(w.sql_text("36_c12_user_events.sql"), "c12_user_events")
    assert body("36_c12_user_events.sql").count("`c12_logs5`") == 1
    ev = cte(ue, "ev")
    assert "FROM `c12_logs5` AS l WHERE l.block_timestamp >= TIMESTAMP(@start_ts) AND l.block_timestamp <= " \
           "TIMESTAMP(@tobs)" in ev
    assert "l.a IN (SELECT address FROM `c12_user_accounts`)" in ev and "l.a != FROM_HEX(REPEAT('00', 20))" in ev
    assert "l.b IN (SELECT address FROM `c12_contracts`) AS to_contract" in ev
    assert "l.b IN (SELECT address FROM untyped) AS to_untyped" in ev
    untyped = cte(ue, "untyped")
    for part in ("SELECT e.address FROM `c12_ends` AS e",
                 "LEFT JOIN (SELECT FROM_HEX(SUBSTR(address, 3)) AS address FROM `c12_rpc_queue`) AS q ON q.address "
                 "= e.address", "LEFT JOIN `c12_tx_senders` AS s ON s.address = e.address",
                 "WHERE q.address IS NULL AND s.address IS NULL"):
        assert part in untyped, part
    where = ue[[m.start() for m in re.finditer(r"\bWHERE\b", ue) if not _inside(ue, m.start())][-1]:]
    keep = where[len("WHERE "):].rstrip(";")
    for kind in ("A", "T"):
        for usd in (None, 5.0):
            for to_contract, to_untyped in ((True, False), (False, True), (False, False)):
                row = {"kind": kind, "usd": usd, "to_contract": to_contract, "to_untyped": to_untyped}
                # every Approval toward a contract (the latest one decides), the priced transfers toward contracts
                # and toward the untyped addresses of E; nothing else (protocol section 5)
                want = (to_contract and (kind == "A" or usd is not None)) or (to_untyped and kind == "T"
                                                                               and usd is not None)
                assert (bq_eval(keep, row) is True) == want, row
    imp = statement(w.sql_text("41_c12_importance.sql"), "c12_importance_raw")
    flows = split0(cte(imp, "flows"), " UNION ALL ")
    assert len(flows) == 2
    for branch, (tag, start, end) in zip(flows, (("t1", "start_ts", "t1"), ("tobs", "tobs_start", "tobs"))):
        assert branch == (f"SELECT '{tag}' AS tag, a AS w, b AS c, SUM(usd) AS s FROM ev WHERE kind = 'T' AND "
                          f"to_contract AND block_timestamp >= TIMESTAMP(@{start}) AND block_timestamp <= "
                          f"TIMESTAMP(@{end}) GROUP BY a, b"), branch
    for name, src, i, n in (("it", "flows", "i_t", "n_t"), ("ia", "auth", "i_a", "n_a")):
        assert cte(imp, name) == (f"SELECT tag, c, SUM(LEAST(s, CAST(@cap_user AS FLOAT64))) AS {i}, "
                                  f"COUNTIF(s >= CAST(@min_usd AS FLOAT64)) AS {n} FROM {src} GROUP BY tag, c"), name
    # Which allowances count toward I_A at each freeze: the latest approval of each (token, owner, spender) in the
    # freeze's own score window, by the predicates of sql/35 lines 23-30 on the user-account events; each priced at
    # its own anchor day and capped at the balance at its own anchor (protocol section 5).
    latest = split0(cte(imp, "latest"), " UNION ALL ")
    t1 = "SELECT 't1' AS tag, token, owner, spender, value FROM ( " + lines(SQL35, 23, 30).replace("`c12_events_cc`",
                                                                                                    "ev")
    tobs = t1.replace("'t1'", "'tobs'").replace("@start_ts", "@tobs_start").replace("@t1)", "@tobs)")
    assert "@tobs_start" in tobs and "@tobs)" in tobs and "@t1" not in tobs
    assert latest == [t1, tobs], latest
    assert cte(imp, "priced") == (
        "SELECT l.tag, l.owner, l.spender, l.value, t.decimals, p.price_usd, IF(l.tag = 't1', b.bal_t1, b.bal_tobs) "
        "AS bal FROM latest AS l JOIN `u_tokens` AS t ON t.token = l.token JOIN `u_prices` AS p ON p.token = l.token "
        "AND p.day = IF(l.tag = 't1', DATE(TIMESTAMP(@t1)), DATE(TIMESTAMP(@tobs))) LEFT JOIN `c12_bal` AS b ON "
        "b.token = l.token AND b.address = l.owner"), cte(imp, "priced")
    for tag, bal in (("t1", 1.0), ("tobs", 2.0)):
        assert bq_eval("IF(l.tag = 't1', b.bal_t1, b.bal_tobs)", {"l.tag": tag, "b.bal_t1": 1.0, "b.bal_tobs": 2.0}) \
            == bal, tag
    # The untyped inflow: a plain sum of each freeze's own score window, without the cap U_user.
    untyped = split0(cte(imp, "untyped"), " UNION ALL ")
    assert untyped == [f"SELECT '{tag}' AS tag, SUM(usd) AS usd FROM ev WHERE kind = 'T' AND NOT to_contract AND "
                       f"block_timestamp >= TIMESTAMP(@{start}) AND block_timestamp <= TIMESTAMP(@{end})"
                       for tag, start, end in (("t1", "start_ts", "t1"), ("tobs", "tobs_start", "tobs"))], untyped
    s = body("41_c12_importance.sql")
    for tag in ("tobs", "t1"):
        st = statement(s, f"c12_importance_{tag}")
        assert "SELECT IFNULL(n.id, -1) AS id," in st and st.endswith(
            f"WHERE r.tag = '{tag}' AND r.part = 'contract' AND (r.i_t > 0 OR r.i_a > 0);"), st
        st = statement(s, f"c12_inflow_untyped_{tag}")
        assert "GROUP BY" not in st and st.endswith(f"WHERE tag = '{tag}' AND part = 'untyped';"), st
        assert select_list(st) == "IFNULL(SUM(usd), 0.0) AS usd"


# --------------------------------------------------------------------------- the exports and the INTERFACE


def test_exports_match_the_interface():
    texts = {}
    for name in GATE_B_SQL:
        if "__TAG__" in w.sql_text(name):
            for tag in ("w0", "w1"):
                texts[f"{name}:{tag}"] = body(name, {"TAG": tag})
        else:
            texts[name] = body(name)
    assert set(DOWNLOADS.values()) == set(INTERFACE) and len(DOWNLOADS) == 16
    for table, stem in DOWNLOADS.items():
        owners = [k for k, t in texts.items() if table in creates(t)]
        assert len(owners) == 1, (table, owners)
        assert set(select_aliases(statement(texts[owners[0]], table))) == set(INTERFACE[stem]), table


def test_the_reader_fixture_writes_the_interface(tmp_path):
    """test_crawl.gate_b_tables, the fixture of the discovery runner's tests, writes the columns and arrow types
    of the INTERFACE: the reader-side fixture and the writer (the SQL) agree."""
    import test_crawl

    for tag in ("t1", "tobs"):
        folder = tmp_path / tag
        test_crawl.gate_b_tables(folder, tag)
        stems = ["nodes", f"allow_pairs_{tag}", f"transfer_pairs_{tag}", f"importance_{tag}", f"inflow_untyped_{tag}"]
        if w.part_paths(folder / f"allow_pairs_uncapped_{tag}"):
            stems.append(f"allow_pairs_uncapped_{tag}")
        for stem in stems:
            assert w.schema_of(folder / stem) == INTERFACE[stem], (
                f"test_crawl.gate_b_tables writes {stem} as {w.schema_of(folder / stem)}, not the INTERFACE "
                f"{INTERFACE[stem]} (the fixture must write the INTERFACE)")


# --------------------------------------------------------------------------- the checks cover the INTERFACE


def test_checks_cover_the_interface():
    st = statement(w.sql_text("42_c12_checks.sql"), "c12_checks")
    split_columns = [c for c in INTERFACE["label_split_w0"] if c not in ("wallet", "spender_class")]
    parts_w0 = cte(st, "parts_w0")
    for c in split_columns:
        assert re.search(rf"\b{c}\b", parts_w0), c
    assert "n_t1" in split_columns
    assert cte(st, "parts_w1") == parts_w0.replace("_w0", "_w1")
    recount_w0 = cte(st, "recount_w0")
    assert cte(st, "recount_w1") == recount_w0.replace("_w0", "_w1")
    for lab in LABELS:
        assert f"p.{lab}" in recount_w0 and f"u.{lab}" in recount_w0, lab
    assert recount_w0.endswith("FROM `c12_label_parts_w0` AS p FULL OUTER JOIN `u12_labels_w0` AS u ON u.wallet = "
                               "p.wallet")
    row = check_row(normal(w.sql_text("42_c12_checks.sql")), "x_weights")
    tables = re.findall(r"FROM `(c12_x_\w+)`\)", row)
    assert sorted(tables) == sorted(t for t in DOWNLOADS if "_pairs_" in t)
    for sub in re.findall(r"\(SELECT COUNTIF\(IFNULL\(.*?, TRUE\)\) FROM `c12_x_\w+`\)", row):
        table = re.search(r"FROM `(c12_x_\w+)`\)$", sub).group(1)
        for c in INTERFACE[DOWNLOADS[table]]:
            assert re.search(rf"\b{c}\b", sub), (table, c)
    for name, source in (("split_w0", "c12_label_parts_w0"), ("x_split_w0", "c12_x_label_split_w0"),
                         ("split_w1", "c12_label_parts_w1"), ("x_split_w1", "c12_x_label_split_w1")):
        q = cte(st, name)
        assert select_aliases(q) == list(SPLIT) and q.endswith(f"FROM `{source}`"), name


# --------------------------------------------------------------------------- what the gate B SQL reads


def test_gate_b_sql_reads_only_what_it_should():
    assert GATE_B_SQL == tuple(sorted(FILE_JOBS))
    for name in GATE_B_SQL:
        raw = w.sql_text(name)
        s = normal(raw)
        assert "bal_0930" not in raw, name
        if name != "36_c12_user_events.sql":
            assert "c12_logs5" not in s, name                # the header of sql/36_c12_allow_triples cites sql/24
        assert not re.search(r"\blogs_(obs|w1)\b", s), name   # only through __LOGS__ of sql/39
        head = []
        for line in raw.splitlines():
            if not line.startswith("--"):
                break
            head.append(line)
        block = " ".join(h.lstrip("-").strip() for h in head)
        assert head and head[0].startswith("-- Contract-graph revision ("), name
        assert re.search(r"(docs/revision_contract_graph\.md,?|revision) sections? \d+", block), name
        assert re.search(rf"\bjob {FILE_JOBS[name]}\b", block), name
    assert "c12_logs5" in body("36_c12_user_events.sql")
    assert "`__LOGS__`" in body("39_c12_label_parts.sql")
