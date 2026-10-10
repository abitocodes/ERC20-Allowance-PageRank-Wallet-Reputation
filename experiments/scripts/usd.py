"""USD amounts of the revised analysis (docs/revision_price_weighting.md).

The SQL of the revised pipeline (sql/12-18) computes these quantities in BigQuery; the
functions here state the same arithmetic in Python, build the daily price table that
BigQuery joins, and are what the tests check.
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
