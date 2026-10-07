"""Compute validation proxy metrics per wallet across six proxy families."""

from __future__ import annotations

import pandas as pd


def compute_transfer_proxies(transfers: pd.DataFrame, wallets: list[str]) -> pd.DataFrame:
    """Do et al. (2023) style in-degree and in-value from inbound transfers."""
    work = transfers.copy()
    work["to_address"] = work["to_address"].astype(str).str.lower()
    work["from_address"] = work["from_address"].astype(str).str.lower()
    work["value"] = work["value"].astype(float)

    inbound = work[work["to_address"].isin(wallets)]
    agg = (
        inbound.groupby("to_address", as_index=False)
        .agg(
            in_degree=("from_address", "nunique"),
            in_value=("value", "sum"),
        )
        .rename(columns={"to_address": "wallet"})
    )

    base = pd.DataFrame({"wallet": [w.lower() for w in wallets]})
    return base.merge(agg, on="wallet", how="left").fillna({"in_degree": 0, "in_value": 0.0})


def compute_allowance_proxies(allowances: pd.DataFrame, wallets: list[str]) -> pd.DataFrame:
    """Inbound allowance proxies: wallet as spender (owner -> spender endorsement)."""
    work = allowances.copy()
    work["owner"] = work["owner"].astype(str).str.lower()
    work["spender"] = work["spender"].astype(str).str.lower()
    work["value"] = work["value"].astype(float)

    wallet_set = {w.lower() for w in wallets}
    inbound = work[work["spender"].isin(wallet_set)]
    agg = (
        inbound.groupby("spender", as_index=False)
        .agg(
            in_approve_degree=("owner", "nunique"),
            in_approve_value=("value", "sum"),
        )
        .rename(columns={"spender": "wallet"})
    )

    base = pd.DataFrame({"wallet": [w.lower() for w in wallets]})
    return base.merge(agg, on="wallet", how="left").fillna(
        {"in_approve_degree": 0, "in_approve_value": 0.0}
    )


def _gmx_wallet_frame(decoded: pd.DataFrame, wallets: list[str], min_closes: int) -> pd.DataFrame:
    work = decoded.copy()
    work["wallet"] = work["account"].astype(str).str.lower()
    work["base_pnl_usd"] = pd.to_numeric(work["base_pnl_usd"], errors="coerce").fillna(0)
    work["is_liquidation"] = work["is_liquidation"].fillna(False).astype(bool)

    counts = work.groupby("wallet").size()
    eligible = set(counts[counts >= min_closes].index) & {w.lower() for w in wallets}
    return work[work["wallet"].isin(eligible)].copy()


def compute_liquidation_proxies(
    decoded: pd.DataFrame,
    wallets: list[str],
    min_closes: int = 3,
) -> pd.DataFrame:
    """Default/liquidation family — higher values imply better reputation."""
    work = _gmx_wallet_frame(decoded, wallets, min_closes)
    if work.empty:
        base = pd.DataFrame({"wallet": [w.lower() for w in wallets]})
        for col in (
            "liquidation_free_rate",
            "zero_liquidation_flag",
            "liquidation_free_closes",
        ):
            base[col] = 0.0
        return base

    work["non_liq"] = ~work["is_liquidation"]
    agg = work.groupby("wallet", as_index=False).agg(
        total_closes=("wallet", "count"),
        liquidation_count=("is_liquidation", "sum"),
        liquidation_free_closes=("non_liq", "sum"),
    )
    agg["liquidation_free_rate"] = 1.0 - (
        agg["liquidation_count"] / agg["total_closes"].clip(lower=1)
    )
    agg["zero_liquidation_flag"] = (agg["liquidation_count"] == 0).astype(float)

    base = pd.DataFrame({"wallet": [w.lower() for w in wallets]})
    return base.merge(
        agg[
            [
                "wallet",
                "liquidation_free_rate",
                "zero_liquidation_flag",
                "liquidation_free_closes",
            ]
        ],
        on="wallet",
        how="left",
    ).fillna(
        {
            "liquidation_free_rate": 0.0,
            "zero_liquidation_flag": 0.0,
            "liquidation_free_closes": 0.0,
        }
    )


def compute_inverse_risk_proxies(
    decoded: pd.DataFrame,
    wallets: list[str],
    min_closes: int = 3,
) -> pd.DataFrame:
    """Inverse-risk family — loss avoidance and non-loss close metrics (higher = smaller losses)."""
    work = _gmx_wallet_frame(decoded, wallets, min_closes)
    if work.empty:
        base = pd.DataFrame({"wallet": [w.lower() for w in wallets]})
        for col in ("loss_avoidance", "non_loss_close_rate", "worst_close_pnl_score"):
            base[col] = 0.0
        return base

    work["loss_close"] = (~work["is_liquidation"]) & (work["base_pnl_usd"] < 0)
    work["loss_amount"] = work["base_pnl_usd"].clip(upper=0)

    agg = work.groupby("wallet", as_index=False).agg(
        total_closes=("wallet", "count"),
        loss_close_count=("loss_close", "sum"),
        loss_avoidance=("loss_amount", "sum"),
        worst_close_pnl=("base_pnl_usd", "min"),
    )
    # Summed losses and the worst close are <= 0 for a wallet that lost money, so a
    # value nearer zero means smaller losses and ranks higher, like every other proxy.
    # (Until 2026-09-30 both were negated, which ranked the largest losses highest.)
    agg["non_loss_close_rate"] = 1.0 - (
        agg["loss_close_count"] / agg["total_closes"].clip(lower=1)
    )
    agg["worst_close_pnl_score"] = agg["worst_close_pnl"]

    base = pd.DataFrame({"wallet": [w.lower() for w in wallets]})
    return base.merge(
        agg[
            [
                "wallet",
                "loss_avoidance",
                "non_loss_close_rate",
                "worst_close_pnl_score",
            ]
        ],
        on="wallet",
        how="left",
    ).fillna(
        {
            "loss_avoidance": 0.0,
            "non_loss_close_rate": 0.0,
            "worst_close_pnl_score": 0.0,
        }
    )


def compute_sybil_stability_proxies(transfers: pd.DataFrame, wallets: list[str]) -> pd.DataFrame:
    """Sybil-adjusted stability from transfer activity (self-transfers excluded)."""
    work = transfers.copy()
    work["to_address"] = work["to_address"].astype(str).str.lower()
    work["from_address"] = work["from_address"].astype(str).str.lower()
    work["block_timestamp"] = pd.to_datetime(work["block_timestamp"], utc=True)

    wallet_set = {w.lower() for w in wallets}
    inbound = work[
        work["to_address"].isin(wallet_set) & (work["from_address"] != work["to_address"])
    ].copy()

    if inbound.empty:
        base = pd.DataFrame({"wallet": [w.lower() for w in wallets]})
        base["inbound_counterparty_ratio"] = 0.0
        base["transfer_tenure_days"] = 0.0
        base["active_months"] = 0.0
        return base

    inbound["month"] = inbound["block_timestamp"].dt.strftime("%Y-%m")
    in_agg = inbound.groupby("to_address", as_index=False).agg(
        inbound_tx=("from_address", "count"),
        inbound_unique=("from_address", "nunique"),
        first_ts=("block_timestamp", "min"),
        last_ts=("block_timestamp", "max"),
        active_months=("month", "nunique"),
    )
    in_agg["inbound_counterparty_ratio"] = in_agg["inbound_unique"] / in_agg[
        "inbound_tx"
    ].clip(lower=1)
    in_agg["transfer_tenure_days"] = (
        in_agg["last_ts"] - in_agg["first_ts"]
    ).dt.total_seconds() / 86400.0

    involved = work[
        work["from_address"].isin(wallet_set) | work["to_address"].isin(wallet_set)
    ].copy()
    involved["wallet"] = involved.apply(
        lambda r: r["from_address"]
        if r["from_address"] in wallet_set
        else r["to_address"],
        axis=1,
    )
    involved["month"] = involved["block_timestamp"].dt.strftime("%Y-%m")
    span = involved.groupby("wallet", as_index=False).agg(
        span_first=("block_timestamp", "min"),
        span_last=("block_timestamp", "max"),
        span_months=("month", "nunique"),
    )
    span["transfer_tenure_days"] = (
        span["span_last"] - span["span_first"]
    ).dt.total_seconds() / 86400.0

    in_agg = in_agg.rename(columns={"to_address": "wallet"})
    merged = in_agg[
        ["wallet", "inbound_counterparty_ratio", "active_months"]
    ].merge(span[["wallet", "transfer_tenure_days", "span_months"]], on="wallet", how="outer")
    merged["active_months"] = merged[["active_months", "span_months"]].max(axis=1)
    merged = merged.drop(columns=["span_months"])

    base = pd.DataFrame({"wallet": [w.lower() for w in wallets]})
    out = base.merge(merged, on="wallet", how="left").fillna(
        {
            "inbound_counterparty_ratio": 0.0,
            "transfer_tenure_days": 0.0,
            "active_months": 0.0,
        }
    )
    return out


def compute_gmx_success_proxies_size_weighted(
    decoded: pd.DataFrame,
    wallets: list[str],
    min_closes: int = 3,
) -> pd.DataFrame:
    """GMX success proxies with size-weighted realized gain (positive PnL × |sizeDeltaUsd|)."""
    work = _gmx_wallet_frame(decoded, wallets, min_closes)
    if work.empty:
        base = pd.DataFrame({"wallet": [w.lower() for w in wallets]})
        base["close_success_count"] = 0.0
        base["realized_gain_proxy"] = 0.0
        base["close_success_rate"] = 0.0
        return base

    work["win"] = (~work["is_liquidation"]) & (work["base_pnl_usd"] > 0)
    work["realized_gain"] = work["base_pnl_usd"].clip(lower=0)
    if "size_delta_usd" in work.columns:
        size = pd.to_numeric(work["size_delta_usd"], errors="coerce").fillna(0.0).abs()
        size = size.replace(0.0, 1.0)
        work["realized_gain"] = work["realized_gain"] * size

    agg = work.groupby("wallet", as_index=False).agg(
        close_success_count=("win", "sum"),
        realized_gain_proxy=("realized_gain", "sum"),
        total_closes=("win", "count"),
    )
    agg["close_success_rate"] = agg["close_success_count"] / agg["total_closes"].clip(lower=1)

    base = pd.DataFrame({"wallet": [w.lower() for w in wallets]})
    return base.merge(
        agg[
            [
                "wallet",
                "close_success_count",
                "realized_gain_proxy",
                "close_success_rate",
            ]
        ],
        on="wallet",
        how="left",
    ).fillna(
        {
            "close_success_count": 0.0,
            "realized_gain_proxy": 0.0,
            "close_success_rate": 0.0,
        }
    )


def compute_gmx_success_proxies(
    decoded: pd.DataFrame,
    wallets: list[str],
    min_closes: int = 3,
) -> pd.DataFrame:
    """GMX margin-trading success proxies for matched wallets."""
    work = _gmx_wallet_frame(decoded, wallets, min_closes)
    if work.empty:
        base = pd.DataFrame({"wallet": [w.lower() for w in wallets]})
        base["close_success_count"] = 0.0
        base["realized_gain_proxy"] = 0.0
        base["close_success_rate"] = 0.0
        return base

    work["win"] = (~work["is_liquidation"]) & (work["base_pnl_usd"] > 0)
    work["realized_gain"] = work["base_pnl_usd"].clip(lower=0)

    agg = work.groupby("wallet", as_index=False).agg(
        close_success_count=("win", "sum"),
        realized_gain_proxy=("realized_gain", "sum"),
        total_closes=("win", "count"),
    )
    agg["close_success_rate"] = agg["close_success_count"] / agg["total_closes"].clip(
        lower=1
    )

    base = pd.DataFrame({"wallet": [w.lower() for w in wallets]})
    return base.merge(
        agg[
            [
                "wallet",
                "close_success_count",
                "realized_gain_proxy",
                "close_success_rate",
            ]
        ],
        on="wallet",
        how="left",
    ).fillna(
        {
            "close_success_count": 0.0,
            "realized_gain_proxy": 0.0,
            "close_success_rate": 0.0,
        }
    )


def compute_gmx_proxies(
    decoded: pd.DataFrame,
    rankings: pd.DataFrame,
    min_closes: int = 3,
) -> pd.DataFrame:
    """Backward-compatible wrapper for GMX success proxies joined to rankings."""
    wallets = rankings["wallet"].astype(str).str.lower().tolist()
    gmx = compute_gmx_success_proxies(decoded, wallets, min_closes=min_closes)
    ranked = rankings[["wallet", "success_rate", "wins", "total_closes"]].copy()
    ranked["wallet"] = ranked["wallet"].astype(str).str.lower()
    work = decoded.copy()
    work["wallet"] = work["account"].astype(str).str.lower()
    eligible = set(work.groupby("wallet").size().pipe(lambda s: s[s >= min_closes].index))
    gmx_eligible = gmx[gmx["wallet"].isin(eligible)]
    return ranked.merge(gmx_eligible, on="wallet", how="inner", suffixes=("_rank", ""))


def compute_all_proxies(
    transfers: pd.DataFrame,
    allowances: pd.DataFrame,
    decoded: pd.DataFrame,
    wallets: list[str],
    min_closes: int = 3,
) -> pd.DataFrame:
    """Merge all six proxy families on wallet (one row per cohort wallet)."""
    base = pd.DataFrame({"wallet": [w.lower() for w in wallets]})
    frames = [
        compute_transfer_proxies(transfers, wallets),
        compute_allowance_proxies(allowances, wallets),
        compute_liquidation_proxies(decoded, wallets, min_closes),
        compute_inverse_risk_proxies(decoded, wallets, min_closes),
        compute_sybil_stability_proxies(transfers, wallets),
        compute_gmx_success_proxies(decoded, wallets, min_closes),
    ]
    out = base
    for frame in frames:
        cols = [c for c in frame.columns if c != "wallet"]
        out = out.merge(frame, on="wallet", how="left")
        for c in cols:
            if out[c].dtype == object:
                continue
            out[c] = out[c].fillna(0.0)
    return out
