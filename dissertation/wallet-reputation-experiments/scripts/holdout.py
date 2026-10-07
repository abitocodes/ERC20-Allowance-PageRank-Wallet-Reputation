"""Temporal holdout: t1 scores versus t2 labels (no contemporaneous leakage)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import kendalltau, spearmanr

from common import load_raw_parquet_dir, normalize_address, parse_token_amount
from pagerank import (
    assign_dense_ranks,
    build_awp_edges,
    build_awp_paper_edges,
    build_endorserank_edges,
    build_endorserank_vt_edges,
    coupled_pagerank,
    filter_subgraph_edges,
    weighted_pagerank,
)
from proxy_metrics import compute_gmx_success_proxies, compute_inverse_risk_proxies

HOLDOUT_LABELS = (
    "future_new_approvers",
    "future_new_transfer_senders",
    "future_revoke_count",
    "future_revoke_rate",
    "future_keep_rate",
    "future_revoke_value",
    "future_drain_owners",
    "future_no_drain",
    "future_aave_liq_count",
    "future_aave_not_liquidated",
    "close_success_count",
    "realized_gain_proxy",
    "close_success_rate",
    "loss_avoidance",
    "non_loss_close_rate",
    "worst_close_pnl_score",
)

# External labels: endorsement construct (spender side), flow construct
# (inbound transfer side) and the Aave borrower liquidation check.
EXTERNAL_LABELS = (
    "future_new_approvers",
    "future_new_transfer_senders",
    "future_keep_rate",
    "future_revoke_value",
    "future_no_drain",
    "future_aave_not_liquidated",
)

# Same-window baselines at the freeze date, reported next to the scores so the
# increment of each PageRank over its own raw degree can be read directly.
BASELINE_IDS = ("t1_in_approve_degree", "t1_in_degree")

# Pre-registered paired contrasts on the holdout (label shared by a and b).
# (label, method_a, method_b, holdout_label, role)
# Here "awp" is the transfer layer walked alone (C-PR at lambda = 0), under the
# id the rule of 14 September gave it. The registered replication reruns this
# tuple as it stands (fresh_holdout.py), so it is not edited.
HOLDOUT_CONTRASTS: tuple[tuple[str, str, str, str, str], ...] = (
    ("EndorseRank minus t1 in-approve degree", "endorserank", "t1_in_approve_degree", "future_new_approvers", "increment"),
    ("AWP minus t1 in-degree", "awp", "t1_in_degree", "future_new_transfer_senders", "increment"),
    ("EndorseRank minus AWP", "endorserank", "awp", "future_new_approvers", "single_layer"),
    ("AWP minus EndorseRank", "awp", "endorserank", "future_new_transfer_senders", "single_layer"),
    ("C-PR minus EndorseRank", "coupled_pr", "endorserank", "future_new_approvers", "primary_a"),
    ("C-PR minus AWP", "coupled_pr", "awp", "future_new_transfer_senders", "primary_b"),
    ("S-PR minus EndorseRank", "seeded_pr", "endorserank", "future_new_approvers", "ablation_a"),
    ("S-PR minus AWP", "seeded_pr", "awp", "future_new_transfer_senders", "ablation_b"),
)

# Contrasts of the spring spender holdout as the thesis reports them.
# EndorseRank and AWP ("endorserank_vt", "awp_paper") share AWP's edge weights;
# their rows were computed after the spring labels were known. The rows of the rule of 14 September (primary_a,
# primary_b) and of the S-PR ablation keep their comparators, the allowance
# layer ("endorserank", C-PR at lambda = 1) and the transfer layer ("awp",
# lambda = 0) walked alone; so does the EndorseRank increment fixed with them,
# which is reported for the new EndorseRank as well. The exploratory row is the
# spring observation that the registered replication tested again.
SPRING_CONTRASTS: tuple[tuple[str, str, str, str, str], ...] = (
    ("C-PR ($\\lambda=1$) minus t1 in-approve degree", "endorserank", "t1_in_approve_degree", "future_new_approvers", "increment_fixed"),
    ("C-PR minus C-PR ($\\lambda=1$)", "coupled_pr", "endorserank", "future_new_approvers", "primary_a"),
    ("C-PR minus C-PR ($\\lambda=0$)", "coupled_pr", "awp", "future_new_transfer_senders", "primary_b"),
    ("S-PR minus C-PR ($\\lambda=1$)", "seeded_pr", "endorserank", "future_new_approvers", "ablation_a"),
    ("S-PR minus C-PR ($\\lambda=0$)", "seeded_pr", "awp", "future_new_transfer_senders", "ablation_b"),
    ("EndorseRank minus t1 in-approve degree", "endorserank_vt", "t1_in_approve_degree", "future_new_approvers", "increment"),
    ("AWP minus t1 in-degree", "awp_paper", "t1_in_degree", "future_new_transfer_senders", "increment"),
    ("EndorseRank minus AWP", "endorserank_vt", "awp_paper", "future_new_approvers", "single_layer"),
    ("AWP minus EndorseRank", "awp_paper", "endorserank_vt", "future_new_transfer_senders", "single_layer"),
    ("C-PR minus C-PR ($\\lambda=0$)", "coupled_pr", "awp", "future_new_approvers", "exploratory"),
    ("C-PR minus EndorseRank", "coupled_pr", "endorserank_vt", "future_new_approvers", "against_single"),
    ("C-PR minus AWP", "coupled_pr", "awp_paper", "future_new_transfer_senders", "against_single"),
    ("C-PR minus AWP", "coupled_pr", "awp_paper", "future_new_approvers", "against_single"),
)

UNLIMITED_ALLOWANCE = 1e30

GMX_LABELS = (
    "close_success_count",
    "realized_gain_proxy",
    "close_success_rate",
    "loss_avoidance",
    "non_loss_close_rate",
    "worst_close_pnl_score",
)


def utc_ts(value: str | pd.Timestamp) -> pd.Timestamp:
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        return ts.tz_localize("UTC")
    return ts.tz_convert("UTC")


def holdout_bounds(config: dict[str, Any]) -> tuple[pd.Timestamp, pd.Timestamp, pd.Timestamp]:
    ho = config["reputation"]["holdout"]
    return utc_ts(ho["score_end"]), utc_ts(ho["outcome_start"]), utc_ts(ho["outcome_end"])


def _ensure_ts(df: pd.DataFrame, col: str = "block_timestamp") -> pd.DataFrame:
    work = df.copy()
    work[col] = pd.to_datetime(work[col], utc=True)
    return work


def normalize_approvals(df: pd.DataFrame) -> pd.DataFrame:
    work = _ensure_ts(df)
    for col in ("owner", "spender", "token_address"):
        if col in work.columns:
            work[col] = work[col].map(lambda x: normalize_address(str(x)) if pd.notna(x) else None)
    work["value"] = work["value"].map(parse_token_amount)
    if "block_number" not in work.columns:
        work["block_number"] = 0
    if "log_index" not in work.columns:
        work["log_index"] = 0
    return work.dropna(subset=["owner", "spender"])


def normalize_transfers(df: pd.DataFrame) -> pd.DataFrame:
    work = _ensure_ts(df)
    for col in ("from_address", "to_address"):
        if col in work.columns:
            work[col] = work[col].map(lambda x: normalize_address(str(x)) if pd.notna(x) else None)
    work["value"] = work["value"].map(parse_token_amount)
    return work.dropna(subset=["from_address", "to_address"])


def load_approval_events(config: dict[str, Any]) -> pd.DataFrame:
    raw_dir = Path(config["reputation"]["paths"]["raw_approvals_dir"])
    return normalize_approvals(load_raw_parquet_dir(raw_dir, "approvals_arbitrum.parquet"))


def load_transfer_events(config: dict[str, Any]) -> pd.DataFrame:
    raw_dir = Path(config["reputation"]["paths"]["raw_transfers_dir"])
    try:
        raw = load_raw_parquet_dir(raw_dir, "transfers_arbitrum.parquet")
        if "from_address" in raw.columns:
            return normalize_transfers(raw)
    except FileNotFoundError:
        pass
    processed = Path(config["reputation"]["paths"]["transfer_events"])
    return normalize_transfers(pd.read_parquet(processed))


def latest_positive_as_of(approvals: pd.DataFrame, as_of: pd.Timestamp) -> pd.DataFrame:
    """Latest (token, owner, spender) state at as_of; keep positive allowances only."""
    work = normalize_approvals(approvals)
    work = work[work["block_timestamp"] <= as_of]
    if work.empty:
        return work
    work = work.sort_values(["block_number", "log_index", "block_timestamp"], kind="mergesort")
    latest = work.groupby(["token_address", "owner", "spender"], as_index=False).tail(1)
    return latest[latest["value"] > 0].copy()


def filter_transfers_as_of(transfers: pd.DataFrame, as_of: pd.Timestamp) -> pd.DataFrame:
    work = normalize_transfers(transfers)
    return work[work["block_timestamp"] <= as_of].copy()


def t1_positive_pairs(latest_t1: pd.DataFrame) -> set[tuple[str, str]]:
    if latest_t1.empty:
        return set()
    return set(zip(latest_t1["owner"].astype(str), latest_t1["spender"].astype(str)))


def t1_connected_wallets(er_edges: pd.DataFrame, awp_edges: pd.DataFrame) -> list[str]:
    nodes: set[str] = set()
    for edges in (er_edges, awp_edges):
        if edges is None or edges.empty:
            continue
        nodes.update(edges["from_node"].astype(str))
        nodes.update(edges["to_node"].astype(str))
    return sorted(nodes)


def resolve_score_wallets(
    matched: list[str] | None,
    t1_nodes: list[str],
) -> list[str]:
    node_set = set(t1_nodes)
    if not matched:
        return list(t1_nodes)
    return [w.lower() for w in matched if w.lower() in node_set]


def future_approval_labels(
    approvals: pd.DataFrame,
    latest_t1: pd.DataFrame,
    outcome_start: pd.Timestamp,
    outcome_end: pd.Timestamp,
    wallets: list[str],
) -> pd.DataFrame:
    pairs = t1_positive_pairs(latest_t1)
    t1_owners: dict[str, set[str]] = {}
    for owner, spender in pairs:
        t1_owners.setdefault(spender, set()).add(owner)

    work = normalize_approvals(approvals)
    window = work[
        (work["block_timestamp"] >= outcome_start) & (work["block_timestamp"] <= outcome_end)
    ]

    new_counts: dict[str, set[str]] = {w: set() for w in wallets}
    revoke_counts: dict[str, set[str]] = {w: set() for w in wallets}

    t1_pair_value: dict[tuple[str, str], float] = {}
    if not latest_t1.empty:
        grouped = latest_t1.groupby(["owner", "spender"], as_index=False)["value"].sum()
        for row in grouped.itertuples(index=False):
            t1_pair_value[(str(row.owner), str(row.spender))] = float(row.value)

    pos = window[window["value"] > 0]
    for row in pos.itertuples(index=False):
        pair = (str(row.owner), str(row.spender))
        if pair in pairs:
            continue
        if row.spender in new_counts:
            new_counts[row.spender].add(str(row.owner))

    zeros = window[window["value"] == 0]
    revoked_value: dict[str, float] = {w: 0.0 for w in wallets}
    for row in zeros.itertuples(index=False):
        pair = (str(row.owner), str(row.spender))
        if pair not in pairs:
            continue
        if row.spender in revoke_counts:
            revoke_counts[row.spender].add(str(row.owner))
            revoked_value[row.spender] = revoked_value.get(row.spender, 0.0) + t1_pair_value.get(
                pair, 0.0
            )

    rows = []
    for wallet in wallets:
        n_new = len(new_counts[wallet])
        n_rev = len(revoke_counts[wallet])
        n_t1 = len(t1_owners.get(wallet, set()))
        rate = (n_rev / n_t1) if n_t1 > 0 else np.nan
        keep = (1.0 - rate) if n_t1 > 0 else np.nan
        rows.append(
            {
                "wallet": wallet,
                "future_new_approvers": float(n_new),
                "future_revoke_count": float(n_rev),
                "future_revoke_rate": rate,
                "future_keep_rate": keep,
                "future_revoke_value": float(revoked_value.get(wallet, 0.0)),
            }
        )
    return pd.DataFrame(rows)


def future_transfer_labels(
    transfers: pd.DataFrame,
    transfers_t1: pd.DataFrame,
    outcome_start: pd.Timestamp,
    outcome_end: pd.Timestamp,
    wallets: list[str],
) -> pd.DataFrame:
    """Flow-side mirror of ``future_new_approvers``.

    ``future_new_transfer_senders`` counts distinct addresses that send a
    transfer to the wallet inside the outcome window and never did so up to
    the freeze date (self-transfers excluded).
    """
    wallet_set = set(wallets)
    t1 = normalize_transfers(transfers_t1) if not transfers_t1.empty else transfers_t1
    seen: dict[str, set[str]] = {w: set() for w in wallets}
    if not t1.empty:
        sub = t1[t1["to_address"].isin(wallet_set) & (t1["from_address"] != t1["to_address"])]
        for row in sub[["from_address", "to_address"]].drop_duplicates().itertuples(index=False):
            seen[str(row.to_address)].add(str(row.from_address))

    work = normalize_transfers(transfers)
    window = work[
        (work["block_timestamp"] >= outcome_start)
        & (work["block_timestamp"] <= outcome_end)
        & work["to_address"].isin(wallet_set)
        & (work["from_address"] != work["to_address"])
    ]
    new_senders: dict[str, set[str]] = {w: set() for w in wallets}
    for row in window[["from_address", "to_address"]].drop_duplicates().itertuples(index=False):
        to = str(row.to_address)
        frm = str(row.from_address)
        if frm not in seen[to]:
            new_senders[to].add(frm)

    return pd.DataFrame(
        {
            "wallet": wallets,
            "future_new_transfer_senders": [float(len(new_senders[w])) for w in wallets],
        }
    )


def t1_baselines(
    latest_t1: pd.DataFrame,
    transfers_t1: pd.DataFrame,
    wallets: list[str],
) -> dict[str, dict[str, float]]:
    """Raw degrees at the freeze date: distinct owners (allowance) and senders (transfer)."""
    approve: dict[str, float] = {w: 0.0 for w in wallets}
    if not latest_t1.empty:
        counts = latest_t1.groupby("spender")["owner"].nunique()
        for w in wallets:
            approve[w] = float(counts.get(w, 0))
    in_deg: dict[str, float] = {w: 0.0 for w in wallets}
    if not transfers_t1.empty:
        t1 = normalize_transfers(transfers_t1)
        t1 = t1[t1["from_address"] != t1["to_address"]]
        counts = t1.groupby("to_address")["from_address"].nunique()
        for w in wallets:
            in_deg[w] = float(counts.get(w, 0))
    return {"t1_in_approve_degree": approve, "t1_in_degree": in_deg}


def future_drain_labels(
    approvals: pd.DataFrame,
    transfers: pd.DataFrame,
    outcome_start: pd.Timestamp,
    outcome_end: pd.Timestamp,
    wallets: list[str],
    horizon_hours: float = 6.0,
    finite_frac: float = 0.5,
    unlimited_hours: float = 1.0,
) -> pd.DataFrame:
    """Approval-then-large-outbound heuristic, attributed to the spender.

    Finite allowance: same-token transfer from owner within horizon_hours
    and value >= finite_frac of the approval. Unlimited approve (value >= 1e30):
    any same-token outbound from the owner within unlimited_hours.
    Spender is not in the Transfer log; this is a noisy proxy.
    """
    empty = pd.DataFrame(
        {
            "wallet": wallets,
            "future_drain_owners": 0.0,
            "future_no_drain": 1.0,
        }
    )
    if not wallets:
        return empty
    wallet_set = set(wallets)
    apps = normalize_approvals(approvals)
    apps = apps[
        (apps["block_timestamp"] >= outcome_start)
        & (apps["block_timestamp"] <= outcome_end)
        & (apps["value"] > 0)
        & (apps["spender"].isin(wallet_set))
    ]
    if apps.empty:
        return empty

    txs = normalize_transfers(transfers)
    if "token_address" not in txs.columns or "token_address" not in apps.columns:
        return empty
    horizon = pd.Timedelta(hours=horizon_hours)
    unlim_h = pd.Timedelta(hours=unlimited_hours)
    txs = txs[
        (txs["block_timestamp"] >= outcome_start)
        & (txs["block_timestamp"] <= outcome_end + horizon)
        & (txs["from_address"].isin(set(apps["owner"])))
    ]
    if txs.empty:
        return empty

    tx_idx: dict[tuple[str, str], list[tuple[pd.Timestamp, float]]] = {}
    for row in txs.itertuples(index=False):
        key = (str(row.from_address), str(row.token_address))
        tx_idx.setdefault(key, []).append((row.block_timestamp, float(row.value)))
    for key in tx_idx:
        tx_idx[key].sort(key=lambda x: x[0])

    from bisect import bisect_right

    hit_owners: dict[str, set[str]] = {}
    for row in apps.itertuples(index=False):
        key = (str(row.owner), str(row.token_address))
        series = tx_idx.get(key)
        if not series:
            continue
        times = [t for t, _ in series]
        start_i = bisect_right(times, row.block_timestamp)
        window_end = row.block_timestamp + (unlim_h if float(row.value) >= UNLIMITED_ALLOWANCE else horizon)
        unlimited = float(row.value) >= UNLIMITED_ALLOWANCE
        for j in range(start_i, len(series)):
            ts_tx, val_tx = series[j]
            if ts_tx > window_end:
                break
            if unlimited or val_tx >= finite_frac * float(row.value):
                hit_owners.setdefault(str(row.spender), set()).add(str(row.owner))
                break
    counts = pd.Series({k: float(len(v)) for k, v in hit_owners.items()})
    rows = []
    for wallet in wallets:
        n = float(counts.get(wallet, 0))
        rows.append(
            {
                "wallet": wallet,
                "future_drain_owners": n,
                "future_no_drain": 0.0 if n > 0 else 1.0,
            }
        )
    return pd.DataFrame(rows)


def future_aave_labels(
    aave_events: pd.DataFrame | None,
    outcome_start: pd.Timestamp,
    outcome_end: pd.Timestamp,
    wallets: list[str],
) -> pd.DataFrame:
    """Borrower-side Aave liquidation in the outcome window.

    Wallets with no Aave borrow/repay/liquidation in the window are NA.
    This is not a spender-side EndorseRank construct.
    """
    base = pd.DataFrame(
        {
            "wallet": wallets,
            "future_aave_liq_count": np.nan,
            "future_aave_not_liquidated": np.nan,
        }
    )
    if aave_events is None or aave_events.empty:
        return base
    work = aave_events.copy()
    work["block_timestamp"] = pd.to_datetime(work["block_timestamp"], utc=True)
    work["user"] = work["user"].map(lambda x: normalize_address(str(x)) if pd.notna(x) else None)
    work = work.dropna(subset=["user"])
    work = work[
        (work["block_timestamp"] >= outcome_start) & (work["block_timestamp"] <= outcome_end)
    ]
    if work.empty:
        return base
    wallet_set = set(wallets)
    work = work[work["user"].isin(wallet_set)]
    if work.empty:
        return base
    active = set(work["user"])
    liq = work[work["event_type"] == "liquidation_call"]
    liq_counts = liq.groupby("user").size() if not liq.empty else pd.Series(dtype=int)
    rows = []
    for wallet in wallets:
        if wallet not in active:
            rows.append(
                {
                    "wallet": wallet,
                    "future_aave_liq_count": np.nan,
                    "future_aave_not_liquidated": np.nan,
                }
            )
            continue
        n = int(liq_counts.get(wallet, 0))
        rows.append(
            {
                "wallet": wallet,
                "future_aave_liq_count": float(n),
                "future_aave_not_liquidated": 0.0 if n > 0 else 1.0,
            }
        )
    return pd.DataFrame(rows)


def label_prevalence(df: pd.DataFrame, columns: tuple[str, ...]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for col in columns:
        if col not in df.columns:
            continue
        s = df[col]
        defined = s.notna()
        out[col] = {
            "n_defined": int(defined.sum()),
            "n_nonzero": int(((s.fillna(0) != 0) & defined).sum()),
            "mean": float(s[defined].mean()) if defined.any() else None,
            "p50": float(s[defined].median()) if defined.any() else None,
        }
    return out


def classify_external_result(stat: dict[str, Any], prevalence: dict[str, Any]) -> str:
    """noise / sparse / meaningful for EndorseRank-facing labels."""
    tau = stat.get("kendall_tau")
    lo = stat.get("ci_low")
    hi = stat.get("ci_high")
    n = int(stat.get("n") or 0)
    n_nz = int((prevalence or {}).get("n_nonzero") or 0)
    n_def = int((prevalence or {}).get("n_defined") or n)
    if n < 50 or n_def < 50:
        return "sparse"
    if n_nz < 20 and n_nz < max(20, int(0.02 * n_def)):
        return "sparse"
    if tau is None:
        return "noise"
    if lo is None or hi is None:
        return "noise" if abs(float(tau)) < 0.15 else "weak_no_ci"
    excludes_zero = (lo > 0 and hi > 0) or (lo < 0 and hi < 0)
    if abs(float(tau)) >= 0.15 and excludes_zero:
        return "meaningful"
    return "noise"


def future_gmx_labels(
    decoded: pd.DataFrame,
    outcome_start: pd.Timestamp,
    outcome_end: pd.Timestamp,
    wallets: list[str],
    min_closes: int,
) -> pd.DataFrame:
    work = decoded.copy()
    work["block_timestamp"] = pd.to_datetime(work["block_timestamp"], utc=True)
    work = work[
        (work["block_timestamp"] >= outcome_start) & (work["block_timestamp"] <= outcome_end)
    ]
    success = compute_gmx_success_proxies(work, wallets, min_closes=min_closes)
    risk = compute_inverse_risk_proxies(work, wallets, min_closes=min_closes)
    if work.empty:
        eligible: set[str] = set()
    else:
        accounts = work["account"].astype(str).str.lower()
        counts = accounts.groupby(accounts).size()
        eligible = set(counts[counts >= min_closes].index)

    out = success.merge(risk, on="wallet", how="outer")
    mask = ~out["wallet"].isin(eligible)
    for col in out.columns:
        if col != "wallet":
            out.loc[mask, col] = np.nan
    return out


def bootstrap_kendall(
    x: pd.Series,
    y: pd.Series,
    n_resamples: int = 400,
    seed: int = 42,
    ci: float = 0.95,
) -> dict[str, Any]:
    mask = x.notna() & y.notna()
    xv = x[mask].astype(float).to_numpy()
    yv = y[mask].astype(float).to_numpy()
    n = int(len(xv))
    if n < 5 or np.unique(xv).size < 2 or np.unique(yv).size < 2:
        return {
            "spearman_rho": None,
            "kendall_tau": None,
            "ci_low": None,
            "ci_high": None,
            "n": n,
            "n_boot": 0,
        }
    rho, _ = spearmanr(xv, yv)
    tau, _ = kendalltau(xv, yv)
    rng = np.random.default_rng(seed)
    samples: list[float] = []
    for _ in range(n_resamples):
        idx = rng.integers(0, n, n)
        xs, ys = xv[idx], yv[idx]
        if np.unique(xs).size < 2 or np.unique(ys).size < 2:
            continue
        t, _ = kendalltau(xs, ys)
        if t is not None and np.isfinite(t):
            samples.append(float(t))
    if len(samples) < 20:
        return {
            "spearman_rho": float(rho),
            "kendall_tau": float(tau),
            "ci_low": None,
            "ci_high": None,
            "n": n,
            "n_boot": len(samples),
        }
    alpha = (1.0 - ci) / 2.0
    arr = np.asarray(samples, dtype=float)
    return {
        "spearman_rho": float(rho),
        "kendall_tau": float(tau),
        "ci_low": float(np.quantile(arr, alpha)),
        "ci_high": float(np.quantile(arr, 1.0 - alpha)),
        "n": n,
        "n_boot": len(samples),
    }


def pagerank_params(config: dict[str, Any]) -> tuple[float, float, int]:
    rep = config["reputation"]
    return (
        float(rep.get("damping", 0.85)),
        float(rep.get("pagerank_tolerance", 1e-8)),
        int(rep.get("max_iterations", 300)),
    )


def _missing_wallets(edges: pd.DataFrame, wallets: list[str]) -> set[str]:
    """Wallets that no edge touches; kept as isolated nodes when ``isolated`` is set."""
    nodes = set(edges["from_node"]) | set(edges["to_node"]) if not edges.empty else set()
    return {w for w in wallets if w not in nodes}


def score_endorserank(
    latest_t1: pd.DataFrame,
    wallets: list[str],
    config: dict[str, Any],
    isolated: bool = False,
) -> dict[str, float]:
    """EndorseRank at t1; with ``isolated`` the wallets outside the graph join it as isolated nodes."""
    seed = set(wallets)
    edges = filter_subgraph_edges(build_endorserank_edges(latest_t1), seed)
    damping, tol, max_iter = pagerank_params(config)
    extra = _missing_wallets(edges, wallets) if isolated else None
    return weighted_pagerank(edges, damping=damping, tol=tol, max_iter=max_iter, extra_nodes=extra)


def score_awp(
    transfers_t1: pd.DataFrame,
    score_end: pd.Timestamp,
    wallets: list[str],
    config: dict[str, Any],
    isolated: bool = False,
) -> dict[str, float]:
    """AWP at t1; with ``isolated`` the wallets outside the graph join it as isolated nodes."""
    rep = config["reputation"]
    seed = set(wallets)
    edges = filter_subgraph_edges(
        build_awp_edges(
            transfers_t1,
            score_end,
            float(rep["awp_decay_k"]),
            float(rep["awp_decay_t0_days"]),
        ),
        seed,
    )
    damping, tol, max_iter = pagerank_params(config)
    extra = _missing_wallets(edges, wallets) if isolated else None
    return weighted_pagerank(edges, damping=damping, tol=tol, max_iter=max_iter, extra_nodes=extra)


def score_awp_paper(
    transfers_t1: pd.DataFrame,
    score_end: pd.Timestamp,
    wallets: list[str],
    config: dict[str, Any],
) -> dict[str, float]:
    """AWP in its published form (see pagerank.build_awp_paper_edges) at t1.

    Activeness is counted over every transfer before t1, not only those inside
    the cohort subgraph. Wallets that no edge touches score zero, as in the
    main analysis. The raw holdout transfers keep zero-value logs, which the
    same-window extract drops; on the spring spender holdout, dropping them as
    well changes this score's coefficients on both labels by less than 0.001.
    """
    rep = config["reputation"]
    paper = rep.get("awp_paper") or {}
    edges, activeness = build_awp_paper_edges(
        transfers_t1,
        score_end,
        float(rep["awp_decay_k"]),
        float(rep["awp_decay_t0_days"]),
        float(paper.get("value_b", 1.0)),
    )
    edges = filter_subgraph_edges(edges, set(wallets))
    damping, tol, max_iter = pagerank_params(config)
    return weighted_pagerank(edges, damping=damping, tol=tol, max_iter=max_iter, teleport=activeness or None)


def score_endorserank_vt(
    latest_t1: pd.DataFrame,
    score_end: pd.Timestamp,
    wallets: list[str],
    config: dict[str, Any],
    activity_restarts: bool = False,
) -> dict[str, float]:
    """EndorseRank (pagerank.build_endorserank_vt_edges) at t1.

    The latest positive allowances at t1 are aged from their approval to t1, and
    the walk restarts uniformly; with ``activity_restarts`` it restarts by
    approving activity, AWP's rule (sensitivity analysis). Wallets that no edge
    touches score zero, as in the main analysis.
    """
    rep = config["reputation"]
    paper = rep.get("awp_paper") or {}
    edges, activeness = build_endorserank_vt_edges(
        latest_t1,
        score_end,
        float(rep["awp_decay_k"]),
        float(rep["awp_decay_t0_days"]),
        float(paper.get("value_b", 1.0)),
    )
    edges = filter_subgraph_edges(edges, set(wallets))
    damping, tol, max_iter = pagerank_params(config)
    teleport = (activeness or None) if activity_restarts else None
    return weighted_pagerank(edges, damping=damping, tol=tol, max_iter=max_iter, teleport=teleport)


def _t1_layers(
    latest_t1: pd.DataFrame,
    transfers_t1: pd.DataFrame,
    score_end: pd.Timestamp,
    wallets: list[str],
    config: dict[str, Any],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rep = config["reputation"]
    seed = set(wallets)
    er_edges = filter_subgraph_edges(build_endorserank_edges(latest_t1), seed)
    awp_edges = filter_subgraph_edges(
        build_awp_edges(
            transfers_t1,
            score_end,
            float(rep["awp_decay_k"]),
            float(rep["awp_decay_t0_days"]),
        ),
        seed,
    )
    return er_edges, awp_edges


def score_coupled(
    latest_t1: pd.DataFrame,
    transfers_t1: pd.DataFrame,
    score_end: pd.Timestamp,
    wallets: list[str],
    config: dict[str, Any],
    lam: float,
) -> dict[str, float]:
    """C-PR at t1: per-node mixture of the allowance and transfer layers."""
    er_edges, awp_edges = _t1_layers(latest_t1, transfers_t1, score_end, wallets, config)
    damping, tol, max_iter = pagerank_params(config)
    return coupled_pagerank(
        [(er_edges, lam), (awp_edges, 1.0 - lam)],
        damping=damping,
        tol=tol,
        max_iter=max_iter,
    )


def score_seeded(
    latest_t1: pd.DataFrame,
    transfers_t1: pd.DataFrame,
    score_end: pd.Timestamp,
    wallets: list[str],
    config: dict[str, Any],
) -> dict[str, float]:
    """S-PR at t1: transfer walk restarted from the EndorseRank distribution."""
    er_edges, awp_edges = _t1_layers(latest_t1, transfers_t1, score_end, wallets, config)
    damping, tol, max_iter = pagerank_params(config)
    hyb = config["reputation"].get("hybrid") or {}
    er_scores = weighted_pagerank(er_edges, damping=damping, tol=tol, max_iter=max_iter)
    return weighted_pagerank(
        awp_edges,
        damping=damping,
        tol=tol,
        max_iter=max_iter,
        teleport=er_scores or None,
        teleport_floor=float(hyb.get("seeded_teleport_floor", 0.0)),
    )


def scores_to_frame(wallets: list[str], scores: dict[str, dict[str, float]]) -> pd.DataFrame:
    out = pd.DataFrame({"wallet": wallets})
    for method, mapping in scores.items():
        ranks = assign_dense_ranks(wallets, mapping)
        rank_map = ranks.set_index("wallet")
        out[f"{method}_score"] = out["wallet"].map(
            lambda w, m=rank_map: float(m.loc[w, "score"]) if w in m.index else 0.0
        )
        out[f"{method}_rank"] = out["wallet"].map(
            lambda w, m=rank_map: int(m.loc[w, "rank"]) if w in m.index else None
        )
    return out


def correlate_holdout(
    merged: pd.DataFrame,
    methods: list[str],
    labels: tuple[str, ...] = HOLDOUT_LABELS,
    n_resamples: int = 400,
    seed: int = 42,
) -> dict[str, Any]:
    report: dict[str, Any] = {"methods": {}, "protocol": "t1_score_vs_t2_label"}
    for method in methods:
        col = f"{method}_score"
        if col not in merged.columns:
            continue
        method_out: dict[str, Any] = {}
        for label in labels:
            if label not in merged.columns:
                continue
            method_out[label] = bootstrap_kendall(
                merged[col], merged[label], n_resamples=n_resamples, seed=seed
            )
        report["methods"][method] = method_out
    return report


def holdout_tau_diff(
    merged: pd.DataFrame,
    contrasts: tuple[tuple[str, str, str, str, str], ...] = HOLDOUT_CONTRASTS,
    n_resamples: int = 400,
    seed: int = 42,
    ci: float = 0.95,
) -> list[dict[str, Any]]:
    """Paired bootstrap of tau_a - tau_b on one holdout label.

    Both coefficients are recomputed on the same wallet resample, drawn with
    the same generator state as ``bootstrap_kendall`` so the per-method
    intervals and the contrast intervals share their resamples.
    """
    out: list[dict[str, Any]] = []
    alpha = (1.0 - ci) / 2.0
    for label, method_a, method_b, holdout_label, role in contrasts:
        col_a = f"{method_a}_score"
        col_b = f"{method_b}_score"
        if col_a not in merged.columns or col_b not in merged.columns or holdout_label not in merged.columns:
            continue
        mask = merged[col_a].notna() & merged[col_b].notna() & merged[holdout_label].notna()
        a = merged.loc[mask, col_a].astype(float).to_numpy()
        b = merged.loc[mask, col_b].astype(float).to_numpy()
        y = merged.loc[mask, holdout_label].astype(float).to_numpy()
        n = int(len(y))
        row: dict[str, Any] = {
            "label": label,
            "role": role,
            "a": {"method": method_a, "tau": None},
            "b": {"method": method_b, "tau": None},
            "holdout_label": holdout_label,
            "delta_tau": None,
            "ci_low": None,
            "ci_high": None,
            "share_positive": None,
            "n": n,
            "n_boot": 0,
        }
        if n < 5 or np.unique(y).size < 2 or np.unique(a).size < 2 or np.unique(b).size < 2:
            out.append(row)
            continue
        tau_a, _ = kendalltau(a, y)
        tau_b, _ = kendalltau(b, y)
        rng = np.random.default_rng(seed)
        deltas: list[float] = []
        for _ in range(n_resamples):
            idx = rng.integers(0, n, n)
            ys = y[idx]
            if np.unique(ys).size < 2:
                continue
            xa, xb = a[idx], b[idx]
            if np.unique(xa).size < 2 or np.unique(xb).size < 2:
                continue
            ta, _ = kendalltau(xa, ys)
            tb, _ = kendalltau(xb, ys)
            if ta is None or tb is None or not (np.isfinite(ta) and np.isfinite(tb)):
                continue
            deltas.append(float(ta - tb))
        row["a"]["tau"] = float(tau_a)
        row["b"]["tau"] = float(tau_b)
        row["delta_tau"] = float(tau_a - tau_b)
        row["n_boot"] = len(deltas)
        if len(deltas) >= 20:
            arr = np.asarray(deltas, dtype=float)
            row["ci_low"] = float(np.quantile(arr, alpha))
            row["ci_high"] = float(np.quantile(arr, 1.0 - alpha))
            row["share_positive"] = float(np.mean(arr > 0))
        out.append(row)
    return out


def evaluate_primary_criterion(tau_diff: list[dict[str, Any]]) -> dict[str, Any]:
    """Pre-registered primary rule for C-PR (see config ``reputation.hybrid``).

    (a) no worse than the allowance layer walked alone (method id
        "endorserank", C-PR at lambda = 1; the rule calls it EndorseRank) on
        future new approvers: the interval of tau(C-PR) - tau(endorserank)
        includes zero or lies above it;
    (b) better than the transfer layer walked alone (method id "awp", C-PR at
        lambda = 0; the rule calls it AWP) on future new transfer senders: the
        interval of tau(C-PR) - tau(awp) lies entirely above zero.
    """
    by_role = {r["role"]: r for r in tau_diff}
    a = by_role.get("primary_a") or {}
    b = by_role.get("primary_b") or {}

    def _has(r: dict[str, Any]) -> bool:
        return r.get("ci_low") is not None and r.get("ci_high") is not None

    no_worse = bool(_has(a) and float(a["ci_high"]) >= 0.0)
    better = bool(_has(b) and float(b["ci_low"]) > 0.0)
    return {
        "no_worse_than_endorserank_on_future_new_approvers": no_worse,
        "better_than_awp_on_future_new_transfer_senders": better,
        "met": bool(no_worse and better),
        "delta_a": a.get("delta_tau"),
        "delta_a_ci": [a.get("ci_low"), a.get("ci_high")],
        "delta_b": b.get("delta_tau"),
        "delta_b_ci": [b.get("ci_low"), b.get("ci_high")],
    }


def build_holdout_fixture_frames(n_wallets: int = 48, seed: int = 7) -> dict[str, pd.DataFrame]:
    """Synthetic events that straddle the March 2026 cutoff."""
    rng = np.random.default_rng(seed)
    wallets = [f"0x{i:040x}" for i in range(1, n_wallets + 1)]
    token = "0xaf88d065e77c8cc2239327c5edb3a432268e5831"
    t1 = pd.Timestamp("2026-02-01", tz="UTC")
    t2 = pd.Timestamp("2026-04-01", tz="UTC")

    approvals: list[dict] = []
    transfers: list[dict] = []
    decoded: list[dict] = []
    bn = 200_000_000

    for i, spender in enumerate(wallets):
        owner_t1 = wallets[(i + 3) % n_wallets]
        owner_new = wallets[(i + 11) % n_wallets]
        approvals.append(
            {
                "block_timestamp": t1 + pd.Timedelta(hours=i),
                "block_number": bn + i,
                "log_index": 0,
                "token_address": token,
                "owner": owner_t1,
                "spender": spender,
                "value": float(1_000_000 + i * 10_000),
            }
        )
        if i % 3 == 0:
            approvals.append(
                {
                    "block_timestamp": t2 + pd.Timedelta(hours=i),
                    "block_number": bn + 50_000 + i,
                    "log_index": 0,
                    "token_address": token,
                    "owner": owner_new,
                    "spender": spender,
                    "value": float(500_000 + i * 5_000),
                }
            )
        if i % 4 == 0:
            approvals.append(
                {
                    "block_timestamp": t2 + pd.Timedelta(days=1, hours=i),
                    "block_number": bn + 80_000 + i,
                    "log_index": 1,
                    "token_address": token,
                    "owner": owner_t1,
                    "spender": spender,
                    "value": 0.0,
                }
            )
        src = wallets[(i + 5) % n_wallets]
        transfers.append(
            {
                "block_timestamp": t1 + pd.Timedelta(hours=i + 2),
                "block_number": bn + 10_000 + i,
                "from_address": src,
                "to_address": spender,
                "token_address": token,
                "value": float(1e18 * (1 + i % 7)),
            }
        )
        transfers.append(
            {
                "block_timestamp": t2 + pd.Timedelta(hours=i + 2),
                "block_number": bn + 60_000 + i,
                "from_address": src,
                "to_address": spender,
                "token_address": token,
                "value": float(1e17),
            }
        )
        if i % 2 == 0:
            # A sender that first appears in the outcome window (future_new_transfer_senders).
            transfers.append(
                {
                    "block_timestamp": t2 + pd.Timedelta(hours=i + 3),
                    "block_number": bn + 70_000 + i,
                    "from_address": wallets[(i + 9) % n_wallets],
                    "to_address": spender,
                    "token_address": token,
                    "value": float(2e17),
                }
            )
        n_close = 3 + int(i % 5)
        for c in range(n_close):
            decoded.append(
                {
                    "account": spender,
                    "block_timestamp": t2 + pd.Timedelta(hours=c),
                    "base_pnl_usd": float((-1) ** c * (50 + i + rng.integers(0, 20))),
                    "is_liquidation": bool(c == n_close - 1 and i % 7 == 0),
                    "size_delta_usd": 1_000.0,
                }
            )

    return {
        "approvals": pd.DataFrame(approvals),
        "transfers": pd.DataFrame(transfers),
        "decoded": pd.DataFrame(decoded),
        "wallets": pd.DataFrame({"wallet": wallets}),
    }
