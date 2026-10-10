"""Trader labels from decoded GMX V2 closes, and helpers shared by the holdout runs."""

from __future__ import annotations

import numpy as np
import pandas as pd

from common import PROC_SHARED, RAW, read_parts

TRADER_LABELS = {
    "liquidation_free_rate": "Liquidation-free close rate",
    "no_liquidation": "No liquidation",
    "profitable_closes": "Profitable closes",
    "realized_gain": "Realized gain",
    "profitable_share": "Profitable share",
    "non_loss_share": "Non-loss share",
}


def load_closes(tags: tuple[str, ...] = ("obs",)) -> pd.DataFrame:
    frames = [read_parts(PROC_SHARED / "gmx" / f"gmx_contract_closes_{t}_decoded") for t in tags]
    df = pd.concat(frames, ignore_index=True)
    df["block_timestamp"] = pd.to_datetime(df["block_timestamp"], utc=True)
    df["pnl"] = df["base_pnl_usd"].astype(float) / 1e30
    df["account"] = df["account"].str.lower()
    return df


def trader_labels(closes: pd.DataFrame, start: str, end: str, min_closes: int) -> pd.DataFrame:
    """One row per account with at least ``min_closes`` closes in [start, end].

    A close counts as profitable when it is not a liquidation and its base PnL is
    positive, and as a loss when it is not a liquidation and its base PnL is negative,
    so a liquidated close is neither (the non-loss share counts it as not a loss).
    """
    w = closes[(closes["block_timestamp"] >= pd.Timestamp(start)) & (closes["block_timestamp"] <= pd.Timestamp(end))]
    w = w.assign(win=(~w["is_liquidation"]) & (w["pnl"] > 0),
                 loss=(~w["is_liquidation"]) & (w["pnl"] < 0),
                 gain=w["pnl"].clip(lower=0))
    g = w.groupby("account").agg(closes=("win", "size"), liquidations=("is_liquidation", "sum"),
                                 profitable_closes=("win", "sum"), losses=("loss", "sum"),
                                 realized_gain=("gain", "sum"))
    g = g[g["closes"] >= min_closes].copy()
    g["liquidation_free_rate"] = 1.0 - g["liquidations"] / g["closes"]
    g["no_liquidation"] = (g["liquidations"] == 0).astype(float)
    g["profitable_share"] = g["profitable_closes"] / g["closes"]
    g["non_loss_share"] = 1.0 - g["losses"] / g["closes"]
    return g.astype(float)


def account_types() -> pd.DataFrame:
    """Account type of every address read so far (cohort candidates, holdout spenders, GMX accounts)."""
    frames = []
    for stem in (RAW / "cohort" / "candidate_account_types", RAW / "cohort" / "holdout_spender_types",
                 RAW / "gmx" / "gmx_account_types", RAW / "gmx" / "gmx_account_types_w1"):
        try:
            frames.append(read_parts(stem)[["address", "code_kind"]])
        except FileNotFoundError:
            pass
    return pd.concat(frames, ignore_index=True).drop_duplicates("address").set_index("address")["code_kind"]


def strata_tau(score: np.ndarray, label: np.ndarray, closes: np.ndarray, edges=(3, 5, 10, 25)) -> float | None:
    """Kendall tau_b within strata of closes (3-4, 5-9, 10-24, 25+), weighted by wallet pairs."""
    from stats import kendall_tau_b
    bins = np.digitize(closes, edges[1:])
    num = den = 0.0
    for b in np.unique(bins):
        m = bins == b
        n = int(m.sum())
        t = kendall_tau_b(score[m], label[m]) if n >= 5 else None
        if t is None:
            continue
        pairs = n * (n - 1) / 2
        num += t * pairs
        den += pairs
    return num / den if den else None
