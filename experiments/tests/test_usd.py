"""USD conversion, the value transform with b = ln 3 / m, the price table and the revised SQL."""

from __future__ import annotations

import os
import re
import subprocess
import sys

import numpy as np
import pandas as pd
import pytest

from conftest import EXPERIMENTS, SCRIPTS
import scoring
import usd

SQL = EXPERIMENTS / "sql"
REVISED_SQL = sorted(p for p in SQL.glob("*.sql") if re.match(r"1[2-9]_usd_", p.name))


def test_slope_puts_the_median_at_one_half():
    for m in (0.37, 12.0, 840.0, 2.5e6):
        b = usd.slope_for_median(m)
        assert usd.value_transform_sql([m], b)[0] == pytest.approx(0.5, abs=1e-12)
        assert scoring.value_transform([m], b)[0] == pytest.approx(0.5, abs=1e-12)
    with pytest.raises(ValueError):
        usd.slope_for_median(0.0)


def test_sql_value_transform_matches_scoring():
    b = usd.slope_for_median(50.0)
    z = np.array([0.0, 1e-9, 0.5, 49.9, 50.0, 400.0, 2000.0, 1e9, 1e62])
    a = usd.value_transform_sql(z, b)
    ref = scoring.value_transform(z, b)
    assert np.allclose(a, ref, rtol=0, atol=1e-15)
    assert a[0] == 0.0 and a[-1] == 1.0
    assert np.all(np.diff(a) >= 0)


def test_round_sig():
    assert usd.round_sig(123.456) == 120.0
    assert usd.round_sig(0.0012345) == 0.0012
    assert usd.round_sig(98765.0, 3) == 98800.0
    assert usd.round_sig(0.0) == 0.0


@pytest.mark.parametrize("decimals,value,price,expected", [
    (6, 2_500_000.0, 1.0, 2.5),               # 2.5 USDC
    (8, 150_000_000.0, 60_000.0, 90_000.0),   # 1.5 WBTC
    (18, 3e17, 2_500.0, 750.0),               # 0.3 WETH
    (2, 1_000.0, 1.08, 10.8),                 # 10 EURS
])
def test_usd_value_scales_by_decimals(decimals, value, price, expected):
    assert usd.usd_value([value], [decimals], [price])[0] == pytest.approx(expected, rel=1e-12)


def test_raw_units_of_tokens_with_different_decimals_are_not_comparable():
    # The registered layers add base units; one USDC (6 decimals) is then a millionth of a
    # micro-WETH. In USD the order is the economic one.
    usdc_raw, weth_raw = 1e6 * 1000.0, 1e18 * 0.001   # 1,000 USDC and 0.001 WETH
    assert usdc_raw < weth_raw
    usdc_usd, weth_usd = usd.usd_value([usdc_raw, weth_raw], [6, 18], [1.0, 2_500.0])
    assert usdc_usd > weth_usd


def test_unlimited_allowance_is_finite_and_capped():
    unlimited = float(2**256 - 1)
    assert usd.is_unlimited([unlimited, 1e30])[0] and not usd.is_unlimited([1e30])[0]
    v = usd.usd_value([unlimited], [18], [2_500.0])[0]
    assert np.isfinite(v) and v > 1e62
    assert usd.capped([v, 10.0], 5e5).tolist() == [5e5, 10.0]


def test_fill_daily_forward_fills_and_never_back_fills():
    prices = pd.DataFrame({
        "token": ["a", "a", "a", "b"],
        "day": ["2024-01-02", "2024-01-03", "2024-01-06", "2024-01-04"],
        "price_usd": [1.0, 1.1, 1.3, 50.0],
        "confidence": [0.99, 0.99, 0.98, 0.9],
    })
    out = usd.fill_daily(prices, "2024-01-01", "2024-01-07")
    a = out[out["token"] == "a"].set_index("day")
    assert a.index.min() == pd.Timestamp("2024-01-02")       # no price before the first one
    assert len(a) == 6
    assert a.loc["2024-01-05", "price_usd"] == 1.1 and a.loc["2024-01-05", "filled"]
    assert a.loc["2024-01-05", "filled_from"] == pd.Timestamp("2024-01-03")
    assert a.loc["2024-01-07", "price_usd"] == 1.3 and a.loc["2024-01-07", "filled"]
    assert not a.loc["2024-01-06", "filled"]
    b = out[out["token"] == "b"]
    assert b["day"].min() == pd.Timestamp("2024-01-04") and len(b) == 4
    with pytest.raises(ValueError):
        usd.fill_daily(pd.concat([prices, prices.iloc[:1]]), "2024-01-01", "2024-01-07")


def test_revised_sql_never_writes_a_registered_table():
    assert REVISED_SQL, "no revised SQL files found"
    created = []
    for path in REVISED_SQL:
        text = path.read_text(encoding="utf-8")
        for name in re.findall(r"CREATE\s+OR\s+REPLACE\s+TABLE\s+`([^`]+)`", text, flags=re.I):
            created.append((path.name, name))
    assert created
    for fname, name in created:
        table = name.split(".")[-1]
        assert table.startswith("u_"), f"{fname} writes {name}"


def test_revised_sql_reads_only_listed_tokens():
    ego = (SQL / "12_usd_ego.sql").read_text(encoding="utf-8")
    # Every revised ego table joins the token list; the cohort counts listed-token approvals only.
    assert ego.count("JOIN `dissertation-bq.contract_rep.u_tokens`") == 4
    assert "token_address IN (SELECT token FROM `dissertation-bq.contract_rep.u_tokens`)" in ego
    labels = (SQL / "16_usd_labels.sql").read_text(encoding="utf-8")
    assert "emitter IN (SELECT token FROM `dissertation-bq.contract_rep.u_tokens`)" in labels


@pytest.mark.parametrize("variant,graph,proc", [
    ("registered", "graph-tables", "2-processed-tables-and-evaluations"),
    ("usd", "graph-tables-usd", "revised-usd"),
])
def test_variant_paths(variant, graph, proc):
    env = {**os.environ, "CONTRACT_REP_VARIANT": variant, "PYTHONDONTWRITEBYTECODE": "1"}
    code = "import common; print(common.GRAPH.name, common.PROC.name, common.PUB.name, common.PROC_SHARED.name)"
    out = subprocess.run([sys.executable, "-c", code], cwd=SCRIPTS, env=env, capture_output=True, text=True, check=True)
    g, p, pub, shared = out.stdout.split()
    assert (g, p) == (graph, proc)
    assert shared == "2-processed-tables-and-evaluations"
    assert pub == ("revised-usd" if variant == "usd" else "3-published-results-for-thesis")


def test_unknown_variant_is_refused():
    env = {**os.environ, "CONTRACT_REP_VARIANT": "eth", "PYTHONDONTWRITEBYTECODE": "1"}
    out = subprocess.run([sys.executable, "-c", "import common"], cwd=SCRIPTS, env=env, capture_output=True, text=True)
    assert out.returncode != 0
