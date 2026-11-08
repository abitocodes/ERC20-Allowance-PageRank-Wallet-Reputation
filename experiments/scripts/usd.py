"""USD amounts of the revised analysis (docs/revision_price_weighting.md).

The SQL of the revised pipeline (sql/12-18) computes these quantities in BigQuery; the
functions here state the same arithmetic in Python, build the daily price table that
BigQuery joins, and are what the tests check. balance_usd, effective_usd and
allowance_pair_weights state the balance cap and the allowance pair weights of the
contract-graph SQL (sql/36_c12_allow_triples.sql, sql/37_c12_pairs.sql) for the tests.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd

LN3 = math.log(3.0)
# Base units at or above which an allowance counts as unlimited (sql/10_describe.sql):
# type(uint256).max = 2^256 - 1 ~ 1.158e77 read as a double.
UNLIMITED_BASE_UNITS = 1.15e77


def round_sig(x: float, digits: int = 2) -> float:
    """``x`` rounded to ``digits`` significant digits (0 stays 0)."""
    if x == 0 or not math.isfinite(x):
        return float(x)
    return float(round(x, digits - 1 - int(math.floor(math.log10(abs(x))))))


def slope_for_median(m: float) -> float:
    """b with V(m) = 1/2 for V(z) = 2 / (1 + exp(-b z)) - 1, i.e. b = ln 3 / m."""
    if not m > 0:
        raise ValueError("the median must be positive")
    return LN3 / m


def value_transform_sql(z: Any, b: float) -> np.ndarray:
    """vt(z, b) of sql/14_usd_anchor_pairs.sql: V(z) with V = 1 once b z >= 40."""
    z = np.clip(np.asarray(z, dtype=np.float64), 0.0, None)
    bz = b * z
    out = np.ones_like(bz)
    small = bz < 40.0
    out[small] = 2.0 / (1.0 + np.exp(-bz[small])) - 1.0
    return out


def token_amount(value: Any, decimals: Any) -> np.ndarray:
    """Token units of a raw uint256 amount read as a double: value / 10^decimals."""
    return np.asarray(value, dtype=np.float64) / np.power(10.0, np.asarray(decimals, dtype=np.float64))


def usd_value(value: Any, decimals: Any, price: Any) -> np.ndarray:
    """USD value of a raw amount: value / 10^decimals x price."""
    return token_amount(value, decimals) * np.asarray(price, dtype=np.float64)


def capped(usd: Any, cap: float) -> np.ndarray:
    """min(usd, cap): the C-PR allowance layer counts an allowance at most ``cap`` USD."""
    return np.minimum(np.asarray(usd, dtype=np.float64), cap)


def is_unlimited(value: Any) -> np.ndarray:
    return np.asarray(value, dtype=np.float64) >= UNLIMITED_BASE_UNITS


def fill_daily(prices: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    """One row per token and UTC day from ``start`` to ``end`` inclusive.

    ``prices`` has columns token, day (date or string), price_usd and optionally confidence.
    A day without a price takes the last earlier price of the same token (``filled`` = True,
    ``filled_from`` = the day the price comes from). Days before a token's first price stay
    out of the table, so an event on such a day finds no price and is counted as unpriced.
    """
    days = pd.date_range(pd.Timestamp(start).normalize(), pd.Timestamp(end).normalize(), freq="D")
    p = prices.copy()
    p["day"] = pd.to_datetime(p["day"]).dt.normalize()
    p = p[(p["day"] >= days[0]) & (p["day"] <= days[-1])]
    if p.duplicated(["token", "day"]).any():
        raise ValueError("more than one price for a token and day")
    out = []
    for token, g in p.groupby("token", sort=True):
        g = g.set_index("day").sort_index()
        grid = pd.DataFrame(index=days[days >= g.index.min()])
        grid.index.name = "day"
        grid = grid.join(g.drop(columns=["token"]))
        grid["filled"] = grid["price_usd"].isna()
        grid["filled_from"] = pd.Series(grid.index, index=grid.index).where(~grid["filled"])
        grid = grid.ffill()
        grid["token"] = token
        out.append(grid.reset_index())
    cols = ["token", "day", "price_usd", "filled", "filled_from"]
    if "confidence" in p.columns:
        cols.insert(3, "confidence")
    if not out:
        return pd.DataFrame(columns=cols)
    res = pd.concat(out, ignore_index=True)[cols]
    res["filled"] = res["filled"].astype(bool)
    return res


def balance_usd(balance: Any, decimals: Any, price: Any, dust_digits: int = 6) -> np.ndarray:
    """usd_bal of sql/36_c12_allow_triples.sql: the owner's balance in base units, 0 unless at least
    10^(decimals - dust_digits) base units (a negative or missing balance, NaN, gives 0; sql/35 line 38), in token
    units, times the anchor day's price."""
    bal = np.asarray(balance, dtype=np.float64)
    dec = np.asarray(decimals, dtype=np.float64)
    kept = np.where(bal >= np.power(10.0, dec - dust_digits), bal, 0.0)   # NaN >= x is False
    return kept / np.power(10.0, dec) * np.asarray(price, dtype=np.float64)


def effective_usd(value: Any, decimals: Any, price: Any, balance: Any, dust_digits: int = 6) -> np.ndarray:
    """usd_eff = min(usd_allow, usd_bal) (docs/revision_contract_graph.md section 5): the allowance ``value`` (base
    units) at the anchor day's price, capped at the owner's balance (base units, NaN when missing)."""
    return np.minimum(usd_value(value, decimals, price), balance_usd(balance, decimals, price, dust_digits))


def allowance_pair_weights(triples: pd.DataFrame, b_allowance: float, cap_allowance: float,
                           value: str = "usd_eff") -> pd.DataFrame:
    """The allowance pairs of sql/37_c12_pairs.sql from (owner, spender, age_days, usd_eff, usd_allow) triples:
    with value 'usd_eff' the triples with usd_eff > 0 (the capped layer), with 'usd_allow' every triple (the uncapped
    sensitivity); per (owner, spender) n_tokens, w_er = sum sigma(age) V(value), w_raw = sum min(value, U), max_sig and
    the slope weights w_er_b10x, w_er_b01x; sigma(age) = 1 / (1 + exp(0.01 (age - 180)))."""
    t = triples[triples[value] > 0] if value == "usd_eff" else triples
    v = t[value].to_numpy(np.float64)
    sig = 1.0 / (1.0 + np.exp(0.01 * (t["age_days"].to_numpy(np.float64) - 180.0)))
    work = pd.DataFrame({"owner": t["owner"].to_numpy(), "spender": t["spender"].to_numpy(), "sig": sig,
                         "w_er": sig * value_transform_sql(v, b_allowance), "w_raw": capped(v, cap_allowance),
                         "w_er_b10x": sig * value_transform_sql(v, 10.0 * b_allowance),
                         "w_er_b01x": sig * value_transform_sql(v, 0.1 * b_allowance)})
    g = work.groupby(["owner", "spender"], sort=True)
    return g.agg(n_tokens=("sig", "size"), w_er=("w_er", "sum"), w_raw=("w_raw", "sum"), max_sig=("sig", "max"),
                 w_er_b10x=("w_er_b10x", "sum"), w_er_b01x=("w_er_b01x", "sum")).reset_index()
