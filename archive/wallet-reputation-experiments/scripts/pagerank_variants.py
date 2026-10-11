"""PageRank variants: GF-PR, LP-PR, CW-AWP, LF-PR, RiskProp, six-Aave W↔W methods."""

from __future__ import annotations

from typing import Any, Literal

import pandas as pd

from pagerank import (
    build_awp_edges,
    build_awp_paper_edges,
    build_endorserank_edges,
    build_endorserank_vt_edges,
    build_weighted_edges,
    coupled_pagerank,
    filter_subgraph_edges,
    logistic_time_decay,
    weighted_pagerank,
)

GMX_POOL_NODE = "__gmx_profit_pool__"
GMX_SINK_NODE = "__gmx_loss_sink__"

# Method ids. AWP_ID is AWP in the form published by Do, Do and Nguyen (2023):
# bounded transfer values V(z), logistic decay T(t) and restarts weighted by
# sending activity; it is the transfer-graph baseline of the thesis.
# ENDORSERANK_ID is the method the thesis proposes: the latest-allowance graph
# with AWP's edge weights T(t) V(z) and uniform restarts.
# ENDORSERANK_ACTIVITY_ID restarts it by approving activity, as AWP restarts by
# sending activity (sensitivity analysis). The two layers of C-PR and S-PR are
# weighted by raw amounts and restart uniformly. Walked alone they are C-PR at
# lambda = 1 (ALLOWANCE_LAYER_ID, no decay) and at lambda = 0
# (TRANSFER_LAYER_ID, with AWP's decay). They keep the ids "endorserank" and
# "awp" because the rule of 14 September and the registered replication
# (config/fresh_holdout_2026q3.yaml) name them so.
AWP_ID = "awp_paper"
ENDORSERANK_ID = "endorserank_vt"
ENDORSERANK_ACTIVITY_ID = "endorserank_vt_activity"
TRANSFER_LAYER_ID = "awp"
ALLOWANCE_LAYER_ID = "endorserank"


def build_endorserank_vt_layer(
    allowances: pd.DataFrame,
    config: dict[str, Any],
    observation_end: pd.Timestamp,
    seed: set[str],
) -> tuple[pd.DataFrame, dict[str, float]]:
    """EndorseRank edges kept around the seed wallets, and AWP's restart weight of every owner."""
    rep = config["reputation"]
    edges, activeness = build_endorserank_vt_edges(
        allowances,
        observation_end,
        float(rep["awp_decay_k"]),
        float(rep["awp_decay_t0_days"]),
        float((rep.get("awp_paper") or {}).get("value_b", 1.0)),
    )
    return filter_subgraph_edges(edges, seed), activeness


def build_awp_paper_layer(
    transfers: pd.DataFrame,
    config: dict[str, Any],
    observation_end: pd.Timestamp,
    seed: set[str],
) -> tuple[pd.DataFrame, dict[str, float]]:
    """AWP edges kept around the seed wallets, and the restart weight of every sender."""
    rep = config["reputation"]
    edges, activeness = build_awp_paper_edges(
        transfers,
        observation_end,
        float(rep["awp_decay_k"]),
        float(rep["awp_decay_t0_days"]),
        float((rep.get("awp_paper") or {}).get("value_b", 1.0)),
    )
    return filter_subgraph_edges(edges, seed), activeness

# Hybrid operators over the allowance and transfer layers. ``coupled_pr`` is
# the primary lambda from config; the other coupled ids carry the grid value
# in their suffix (lambda = 0.25 -> coupled_pr_l25). ``seeded_pr`` is the
# transfer walk with EndorseRank as the restart distribution.
SEEDED_PR_ID = "seeded_pr"
COUPLED_PR_ID = "coupled_pr"


def hybrid_lambda_map(config: dict[str, Any]) -> dict[str, float]:
    """method_id -> lambda for the coupled operator (primary first)."""
    hyb = (config.get("reputation") or {}).get("hybrid") or {}
    primary = float(hyb.get("coupled_lambda_primary", 0.5))
    grid = [float(x) for x in hyb.get("coupled_lambda_grid", [0.25, 0.5, 0.75])]
    out: dict[str, float] = {COUPLED_PR_ID: primary}
    for lam in grid:
        if abs(lam - primary) < 1e-12:
            continue
        out[f"{COUPLED_PR_ID}_l{int(round(lam * 100)):02d}"] = lam
    return out


def hybrid_method_ids(config: dict[str, Any]) -> tuple[str, ...]:
    return tuple(hybrid_lambda_map(config)) + (SEEDED_PR_ID,)


def compute_hybrid_scores(
    wallets: list[str],
    config: dict[str, Any],
    er_edges: pd.DataFrame,
    awp_edges: pd.DataFrame,
) -> tuple[dict[str, dict[str, float]], dict[str, int]]:
    """C-PR for every configured lambda and S-PR, restricted to ``wallets``.

    ``er_edges`` and ``awp_edges`` are the already filtered allowance layer
    (ALLOWANCE_LAYER_ID) and transfer layer (TRANSFER_LAYER_ID), not the graphs
    of EndorseRank and AWP. S-PR restarts from the allowance layer walked alone.
    """
    rep = config["reputation"]
    hyb = rep.get("hybrid") or {}
    damping = float(rep["damping"])
    tol = float(rep["pagerank_tolerance"])
    max_iter = int(rep["max_iterations"])
    scores: dict[str, dict[str, float]] = {}
    edge_counts: dict[str, int] = {}

    n_er = 0 if er_edges is None else len(er_edges)
    n_awp = 0 if awp_edges is None else len(awp_edges)

    for method_id, lam in hybrid_lambda_map(config).items():
        full = coupled_pagerank(
            [(er_edges, lam), (awp_edges, 1.0 - lam)],
            damping=damping,
            tol=tol,
            max_iter=max_iter,
        )
        scores[method_id] = {w: full.get(w, 0.0) for w in wallets}
        edge_counts[method_id] = n_er + n_awp

    er_full: dict[str, float] = {}
    if n_er:
        er_full = weighted_pagerank(er_edges, damping=damping, tol=tol, max_iter=max_iter)
    if n_awp:
        seeded = weighted_pagerank(
            awp_edges,
            damping=damping,
            tol=tol,
            max_iter=max_iter,
            teleport=er_full or None,
            teleport_floor=float(hyb.get("seeded_teleport_floor", 0.0)),
        )
        scores[SEEDED_PR_ID] = {w: seeded.get(w, 0.0) for w in wallets}
    else:
        scores[SEEDED_PR_ID] = {w: 0.0 for w in wallets}
    edge_counts[SEEDED_PR_ID] = n_awp
    return scores, edge_counts

SIX_AAVE_METHOD_IDS = (
    "endorserank",
    "awp",
    "liq_pr",
    "borrow_pr",
    "repay_pr",
    "delegation_pr",
)

SIX_AAVE_DIAGNOSTIC_IDS = (
    "borrow_pr_pool",
    "repay_pr_pool",
)


def _wallet_liquidation_rates(decoded: pd.DataFrame, wallets: list[str]) -> dict[str, float]:
    work = decoded.copy()
    work["wallet"] = work["account"].astype(str).str.lower()
    wallet_set = {w.lower() for w in wallets}
    work = work[work["wallet"].isin(wallet_set)]
    if work.empty:
        return {w.lower(): 0.0 for w in wallets}

    agg = work.groupby("wallet", as_index=False).agg(
        total=("wallet", "count"),
        liq=("is_liquidation", "sum"),
    )
    agg["liq_rate"] = agg["liq"] / agg["total"].clip(lower=1)
    rates = dict(zip(agg["wallet"], agg["liq_rate"]))
    return {w.lower(): float(rates.get(w.lower(), 0.0)) for w in wallets}


def build_gf_pr_edges(decoded: pd.DataFrame, wallets: list[str]) -> pd.DataFrame:
    """ProfitFlow star graph: POOL -> wallet (gains), wallet -> SINK (losses/liquidations)."""
    work = decoded.copy()
    work["wallet"] = work["account"].astype(str).str.lower()
    work["base_pnl_usd"] = pd.to_numeric(work["base_pnl_usd"], errors="coerce").fillna(0)
    work["is_liquidation"] = work["is_liquidation"].fillna(False).astype(bool)
    wallet_set = {w.lower() for w in wallets}
    work = work[work["wallet"].isin(wallet_set)]

    pool_to: dict[str, float] = {}
    to_sink: dict[str, float] = {}

    for _, row in work.iterrows():
        w = row["wallet"]
        pnl = float(row["base_pnl_usd"])
        if row["is_liquidation"]:
            to_sink[w] = to_sink.get(w, 0.0) + abs(pnl) + 1.0
        elif pnl > 0:
            pool_to[w] = pool_to.get(w, 0.0) + pnl
        elif pnl < 0:
            to_sink[w] = to_sink.get(w, 0.0) + abs(pnl) + 0.1

    rows: list[dict[str, Any]] = []
    for w, wt in pool_to.items():
        if wt > 0:
            rows.append({"from_node": GMX_POOL_NODE, "to_node": w, "weight": wt})
    for w, wt in to_sink.items():
        if wt > 0:
            rows.append({"from_node": w, "to_node": GMX_SINK_NODE, "weight": wt})

    if not rows:
        return pd.DataFrame(columns=["from_node", "to_node", "weight"])
    return pd.DataFrame(rows)


def build_lp_pr_edges(
    transfers: pd.DataFrame,
    decoded: pd.DataFrame,
    wallets: list[str],
    observation_end: pd.Timestamp,
    k: float,
    t0_days: float,
) -> pd.DataFrame:
    """AWP transfer edges penalized by endpoint liquidation rates."""
    base = build_awp_edges(transfers, observation_end, k, t0_days)
    if base.empty:
        return base

    liq_rate = _wallet_liquidation_rates(decoded, wallets)
    work = base.copy()
    work["weight"] = work.apply(
        lambda r: float(r["weight"])
        * (1.0 - liq_rate.get(str(r["from_node"]).lower(), 0.0))
        * (1.0 - liq_rate.get(str(r["to_node"]).lower(), 0.0)),
        axis=1,
    )
    return work[work["weight"] > 0]


def build_cw_awp_edges(
    transfers: pd.DataFrame,
    token_allowlist: list[str],
    observation_end: pd.Timestamp,
    k: float,
    t0_days: float,
) -> pd.DataFrame:
    """AWP on collateral-token transfers only."""
    allow = {t.lower() for t in token_allowlist}
    work = transfers.copy()
    work["token_address"] = work["token_address"].astype(str).str.lower()
    filtered = work[work["token_address"].isin(allow)]
    return build_awp_edges(filtered, observation_end, k, t0_days)


def build_riskprop_edges(
    transfers: pd.DataFrame,
    decoded: pd.DataFrame,
    wallets: list[str],
    observation_end: pd.Timestamp,
    k: float,
    t0_days: float,
) -> pd.DataFrame:
    """AWP edges scaled by (1 - risk(from)) where risk = liquidation rate."""
    base = build_awp_edges(transfers, observation_end, k, t0_days)
    if base.empty:
        return base

    risk = _wallet_liquidation_rates(decoded, wallets)
    work = base.copy()
    work["weight"] = work.apply(
        lambda r: float(r["weight"]) * (1.0 - risk.get(str(r["from_node"]).lower(), 0.0)),
        axis=1,
    )
    return work[work["weight"] > 0]


def build_lf_pr_edges(
    aave_events: pd.DataFrame,
    observation_end: pd.Timestamp,
    k: float,
    t0_days: float,
) -> pd.DataFrame:
    """Time-decayed user <-> pool edges from Aave lending events."""
    if aave_events.empty:
        return pd.DataFrame(columns=["from_node", "to_node", "weight"])

    from pagerank import logistic_time_decay

    work = aave_events.copy()
    work["user"] = work["user"].astype(str).str.lower()
    work["pool"] = work["pool"].astype(str).str.lower()
    work["amount"] = work["amount"].astype(float)
    work["block_timestamp"] = pd.to_datetime(work["block_timestamp"], utc=True)
    work = work[work["amount"] > 0]

    delta = (observation_end - work["block_timestamp"]).dt.total_seconds() / 86400.0
    work["decay"] = logistic_time_decay(delta, k, t0_days)
    work["weighted"] = work["amount"] * work["decay"]

    rows: list[dict[str, Any]] = []
    for _, row in work.iterrows():
        user, pool = row["user"], row["pool"]
        w = float(row["weighted"])
        et = str(row.get("event_type", "")).lower()
        if et == "borrow":
            rows.append({"from_node": pool, "to_node": user, "weight": w})
        elif et in ("repay", "liquidation_call", "liquidation"):
            rows.append({"from_node": user, "to_node": pool, "weight": w})
        else:
            rows.append({"from_node": user, "to_node": pool, "weight": w * 0.5})
            rows.append({"from_node": pool, "to_node": user, "weight": w * 0.5})

    if not rows:
        return pd.DataFrame(columns=["from_node", "to_node", "weight"])
    df = pd.DataFrame(rows)
    return build_weighted_edges(df, "from_node", "to_node", "weight")


def _pool_address_set(config: dict[str, Any]) -> set[str]:
    pools = config.get("aave_arbitrum", {}).get("pool_addresses", [])
    return {str(p).lower() for p in pools}


def _decayed_aave_rows(
    aave_events: pd.DataFrame,
    observation_end: pd.Timestamp,
    k: float,
    t0_days: float,
    event_types: set[str] | None = None,
) -> pd.DataFrame:
    if aave_events.empty:
        return pd.DataFrame()

    work = aave_events.copy()
    work["block_timestamp"] = pd.to_datetime(work["block_timestamp"], utc=True)
    work["amount"] = pd.to_numeric(work["amount"], errors="coerce").fillna(0)
    work = work[work["amount"] > 0]
    if event_types is not None:
        work = work[work["event_type"].astype(str).str.lower().isin(event_types)]
    if work.empty:
        return work

    delta = (observation_end - work["block_timestamp"]).dt.total_seconds() / 86400.0
    work["weight"] = work["amount"] * logistic_time_decay(delta, k, t0_days)
    return work[work["weight"] > 0]


def _is_wallet(addr: str | None, pool_addrs: set[str]) -> bool:
    if not addr or pd.isna(addr):
        return False
    a = str(addr).lower()
    if a in pool_addrs or a == "0x0000000000000000000000000000000000000000":
        return False
    return True


def build_liq_pr_edges(
    aave_events: pd.DataFrame,
    config: dict[str, Any],
    observation_end: pd.Timestamp,
    k: float,
    t0_days: float,
) -> pd.DataFrame:
    """liquidator -> user from Aave LiquidationCall events."""
    pool_addrs = _pool_address_set(config)
    work = _decayed_aave_rows(
        aave_events, observation_end, k, t0_days, {"liquidation_call"}
    )
    if work.empty:
        return pd.DataFrame(columns=["from_node", "to_node", "weight"])

    rows: list[dict[str, Any]] = []
    for _, row in work.iterrows():
        liquidator = row.get("liquidator")
        user = row.get("user")
        if not _is_wallet(liquidator, pool_addrs) or not _is_wallet(user, pool_addrs):
            continue
        if str(liquidator).lower() == str(user).lower():
            continue
        rows.append(
            {
                "from_node": str(liquidator).lower(),
                "to_node": str(user).lower(),
                "weight": float(row["weight"]),
            }
        )
    if not rows:
        return pd.DataFrame(columns=["from_node", "to_node", "weight"])
    return build_weighted_edges(pd.DataFrame(rows), "from_node", "to_node", "weight")


def build_borrow_pr_edges(
    aave_events: pd.DataFrame,
    config: dict[str, Any],
    observation_end: pd.Timestamp,
    k: float,
    t0_days: float,
    mode: Literal["ww", "pool"] = "ww",
) -> pd.DataFrame:
    """W↔W: initiator -> onBehalfOf; pool-leg: pool -> onBehalfOf."""
    pool_addrs = _pool_address_set(config)
    work = _decayed_aave_rows(aave_events, observation_end, k, t0_days, {"borrow"})
    if work.empty:
        return pd.DataFrame(columns=["from_node", "to_node", "weight"])

    rows: list[dict[str, Any]] = []
    for _, row in work.iterrows():
        on_behalf = row.get("on_behalf_of") or row.get("user")
        if not _is_wallet(on_behalf, pool_addrs):
            continue
        if mode == "pool":
            pool = row.get("pool")
            if not pool:
                continue
            rows.append(
                {
                    "from_node": str(pool).lower(),
                    "to_node": str(on_behalf).lower(),
                    "weight": float(row["weight"]),
                }
            )
        else:
            initiator = row.get("initiator")
            if not _is_wallet(initiator, pool_addrs):
                continue
            if str(initiator).lower() == str(on_behalf).lower():
                continue
            rows.append(
                {
                    "from_node": str(initiator).lower(),
                    "to_node": str(on_behalf).lower(),
                    "weight": float(row["weight"]),
                }
            )
    if not rows:
        return pd.DataFrame(columns=["from_node", "to_node", "weight"])
    return build_weighted_edges(pd.DataFrame(rows), "from_node", "to_node", "weight")


def build_repay_pr_edges(
    aave_events: pd.DataFrame,
    config: dict[str, Any],
    observation_end: pd.Timestamp,
    k: float,
    t0_days: float,
    mode: Literal["ww", "pool"] = "ww",
) -> pd.DataFrame:
    """W↔W: repayer -> user; pool-leg: repayer -> pool."""
    pool_addrs = _pool_address_set(config)
    work = _decayed_aave_rows(aave_events, observation_end, k, t0_days, {"repay"})
    if work.empty:
        return pd.DataFrame(columns=["from_node", "to_node", "weight"])

    rows: list[dict[str, Any]] = []
    for _, row in work.iterrows():
        user = row.get("user")
        repayer = row.get("repayer")
        if mode == "pool":
            pool = row.get("pool")
            if not _is_wallet(repayer, pool_addrs) or not pool:
                continue
            rows.append(
                {
                    "from_node": str(repayer).lower(),
                    "to_node": str(pool).lower(),
                    "weight": float(row["weight"]),
                }
            )
        else:
            if not _is_wallet(repayer, pool_addrs) or not _is_wallet(user, pool_addrs):
                continue
            if str(repayer).lower() == str(user).lower():
                continue
            rows.append(
                {
                    "from_node": str(repayer).lower(),
                    "to_node": str(user).lower(),
                    "weight": float(row["weight"]),
                }
            )
    if not rows:
        return pd.DataFrame(columns=["from_node", "to_node", "weight"])
    return build_weighted_edges(pd.DataFrame(rows), "from_node", "to_node", "weight")


def build_delegation_pr_edges(
    delegation_events: pd.DataFrame,
    observation_end: pd.Timestamp,
    k: float,
    t0_days: float,
) -> pd.DataFrame:
    """delegator (from_user) -> delegatee (to_user) from BorrowAllowanceDelegated."""
    if delegation_events.empty:
        return pd.DataFrame(columns=["from_node", "to_node", "weight"])

    work = delegation_events.copy()
    work["block_timestamp"] = pd.to_datetime(work["block_timestamp"], utc=True)
    work["amount"] = pd.to_numeric(work["amount"], errors="coerce").fillna(0)
    work = work[work["amount"] > 0]
    if work.empty:
        return pd.DataFrame(columns=["from_node", "to_node", "weight"])

    delta = (observation_end - work["block_timestamp"]).dt.total_seconds() / 86400.0
    work["weight"] = work["amount"] * logistic_time_decay(delta, k, t0_days)
    work = work[work["weight"] > 0]

    rows: list[dict[str, Any]] = []
    for _, row in work.iterrows():
        delegator = row.get("from_user") or row.get("delegator")
        delegatee = row.get("to_user") or row.get("delegatee")
        if not delegator or not delegatee:
            continue
        if str(delegator).lower() == str(delegatee).lower():
            continue
        rows.append(
            {
                "from_node": str(delegator).lower(),
                "to_node": str(delegatee).lower(),
                "weight": float(row["weight"]),
            }
        )
    if not rows:
        return pd.DataFrame(columns=["from_node", "to_node", "weight"])
    return build_weighted_edges(pd.DataFrame(rows), "from_node", "to_node", "weight")


def collect_six_aave_edges(
    wallets: list[str],
    config: dict[str, Any],
    allowances: pd.DataFrame,
    transfers: pd.DataFrame,
    aave_events: pd.DataFrame | None,
    delegation_events: pd.DataFrame | None,
) -> dict[str, pd.DataFrame]:
    """Edge lists for six-Aave PageRank preset (+ pool-leg diagnostics)."""
    rep = config["reputation"]
    seed = set(w.lower() for w in wallets)
    observation_end = pd.Timestamp(rep["observation_end"], tz="UTC")
    k = float(rep["awp_decay_k"])
    t0 = float(rep["awp_decay_t0_days"])

    edges: dict[str, pd.DataFrame] = {}
    edges["endorserank"] = filter_subgraph_edges(build_endorserank_edges(allowances), seed)
    edges["awp"] = filter_subgraph_edges(
        build_awp_edges(transfers, observation_end, k, t0), seed
    )

    empty = pd.DataFrame(columns=["from_node", "to_node", "weight"])
    aave = aave_events if aave_events is not None else pd.DataFrame()

    if not aave.empty:
        edges["liq_pr"] = filter_subgraph_edges(
            build_liq_pr_edges(aave, config, observation_end, k, t0), seed
        )
        edges["borrow_pr"] = filter_subgraph_edges(
            build_borrow_pr_edges(aave, config, observation_end, k, t0, mode="ww"), seed
        )
        edges["repay_pr"] = filter_subgraph_edges(
            build_repay_pr_edges(aave, config, observation_end, k, t0, mode="ww"), seed
        )
        edges["borrow_pr_pool"] = filter_subgraph_edges(
            build_borrow_pr_edges(aave, config, observation_end, k, t0, mode="pool"), seed
        )
        edges["repay_pr_pool"] = filter_subgraph_edges(
            build_repay_pr_edges(aave, config, observation_end, k, t0, mode="pool"), seed
        )
    else:
        for mid in ("liq_pr", "borrow_pr", "repay_pr", "borrow_pr_pool", "repay_pr_pool"):
            edges[mid] = empty.copy()

    delegation = delegation_events if delegation_events is not None else pd.DataFrame()
    if not delegation.empty:
        edges["delegation_pr"] = filter_subgraph_edges(
            build_delegation_pr_edges(delegation, observation_end, k, t0), seed
        )
    else:
        edges["delegation_pr"] = empty.copy()

    return edges


def compute_six_aave_scores(
    wallets: list[str],
    config: dict[str, Any],
    allowances: pd.DataFrame,
    transfers: pd.DataFrame,
    aave_events: pd.DataFrame | None,
    delegation_events: pd.DataFrame | None = None,
) -> tuple[dict[str, dict[str, float]], dict[str, int]]:
    """Compute six-Aave preset scores and edge counts."""
    rep = config["reputation"]
    seed = set(w.lower() for w in wallets)

    edge_map = collect_six_aave_edges(
        wallets, config, allowances, transfers, aave_events, delegation_events
    )

    scores: dict[str, dict[str, float]] = {}
    edge_counts: dict[str, int] = {}

    for method_id in SIX_AAVE_METHOD_IDS:
        edges = edge_map.get(method_id, pd.DataFrame())
        scores[method_id], edge_counts[method_id] = _run_pagerank_on_edges(
            edges, wallets, seed, rep
        )

    for diag_id in SIX_AAVE_DIAGNOSTIC_IDS:
        edges = edge_map.get(diag_id, pd.DataFrame())
        scores[diag_id], edge_counts[diag_id] = _run_pagerank_on_edges(
            edges, wallets, seed, rep
        )

    return scores, edge_counts


def collect_method_edges(
    wallets: list[str],
    config: dict[str, Any],
    allowances: pd.DataFrame,
    transfers: pd.DataFrame,
    decoded: pd.DataFrame,
    aave_events: pd.DataFrame | None,
    with_restarts: bool = False,
) -> dict[str, pd.DataFrame] | tuple[dict[str, pd.DataFrame], dict[str, dict[str, float]]]:
    """Filtered edge lists per method (for PageRank runtime benchmarking).

    With ``with_restarts`` it also returns the restart weights of the methods
    that do not restart uniformly (only AWP_ID).
    """
    rep = config["reputation"]
    seed = set(w.lower() for w in wallets)
    observation_end = pd.Timestamp(rep["observation_end"], tz="UTC")
    k = float(rep["awp_decay_k"])
    t0 = float(rep["awp_decay_t0_days"])
    methods_cfg = config.get("methods", {})
    collateral = config.get("collateral_tokens", [])

    edges: dict[str, pd.DataFrame] = {}
    restarts: dict[str, dict[str, float]] = {}

    edges[ENDORSERANK_ID], _ = build_endorserank_vt_layer(allowances, config, observation_end, seed)
    edges[ALLOWANCE_LAYER_ID] = filter_subgraph_edges(build_endorserank_edges(allowances), seed)

    edges[AWP_ID], restarts[AWP_ID] = build_awp_paper_layer(transfers, config, observation_end, seed)

    awp_edge_df = build_awp_edges(transfers, observation_end, k, t0)
    edges[TRANSFER_LAYER_ID] = filter_subgraph_edges(awp_edge_df, seed)

    if methods_cfg.get("gf_pr", {}).get("enabled", True):
        gf_edges = build_gf_pr_edges(decoded, wallets)
        edges["gf_pr"] = filter_subgraph_edges(
            gf_edges, seed | {GMX_POOL_NODE, GMX_SINK_NODE}
        )

    if methods_cfg.get("lp_pr", {}).get("enabled", True):
        lp_edges = build_lp_pr_edges(transfers, decoded, wallets, observation_end, k, t0)
        edges["lp_pr"] = filter_subgraph_edges(lp_edges, seed)

    if methods_cfg.get("cw_awp", {}).get("enabled", True) and collateral:
        cw_edges = build_cw_awp_edges(transfers, collateral, observation_end, k, t0)
        edges["cw_awp"] = filter_subgraph_edges(cw_edges, seed)

    if methods_cfg.get("riskprop_pr", {}).get("enabled", True):
        rp_edges = build_riskprop_edges(transfers, decoded, wallets, observation_end, k, t0)
        edges["riskprop_pr"] = filter_subgraph_edges(rp_edges, seed)

    if methods_cfg.get("lf_pr", {}).get("enabled", True):
        if aave_events is not None and not aave_events.empty:
            lf_edges = build_lf_pr_edges(aave_events, observation_end, k, t0)
            edges["lf_pr"] = filter_subgraph_edges(lf_edges, seed)
        else:
            edges["lf_pr"] = pd.DataFrame(columns=["from_node", "to_node", "weight"])

    if with_restarts:
        return edges, restarts
    return edges


def _run_pagerank_on_edges(
    edges: pd.DataFrame,
    wallets: list[str],
    seed: set[str],
    rep: dict[str, Any],
    teleport: dict[str, float] | None = None,
) -> tuple[dict[str, float], int]:
    if edges.empty:
        return {w: 0.0 for w in wallets}, 0

    filtered = filter_subgraph_edges(edges, seed)
    scores = weighted_pagerank(
        filtered,
        damping=float(rep["damping"]),
        tol=float(rep["pagerank_tolerance"]),
        max_iter=int(rep["max_iterations"]),
        teleport=teleport or None,
    )
    return {w: scores.get(w, 0.0) for w in wallets}, len(filtered)


def compute_variant_scores(
    wallets: list[str],
    config: dict[str, Any],
    allowances: pd.DataFrame,
    transfers: pd.DataFrame,
    decoded: pd.DataFrame,
    aave_events: pd.DataFrame | None,
) -> tuple[dict[str, dict[str, float]], dict[str, int]]:
    """Compute all seven method scores and edge counts."""
    rep = config["reputation"]
    seed = set(w.lower() for w in wallets)
    observation_end = pd.Timestamp(rep["observation_end"], tz="UTC")
    k = float(rep["awp_decay_k"])
    t0 = float(rep["awp_decay_t0_days"])

    methods_cfg = config.get("methods", {})
    collateral = config.get("collateral_tokens", [])

    scores: dict[str, dict[str, float]] = {}
    edge_counts: dict[str, int] = {}

    # EndorseRank: AWP's edge weights on the latest-allowance graph, uniform restarts.
    er_vt_edges, er_activeness = build_endorserank_vt_layer(allowances, config, observation_end, seed)
    scores[ENDORSERANK_ID], edge_counts[ENDORSERANK_ID] = _run_pagerank_on_edges(
        er_vt_edges, wallets, seed, rep
    )
    # Sensitivity analysis: the same graph restarted by approving activity, AWP's rule.
    scores[ENDORSERANK_ACTIVITY_ID], edge_counts[ENDORSERANK_ACTIVITY_ID] = _run_pagerank_on_edges(
        er_vt_edges, wallets, seed, rep, teleport=er_activeness
    )

    # Allowance layer walked alone (raw amounts, uniform restarts; C-PR at lambda = 1).
    er_edges = filter_subgraph_edges(build_endorserank_edges(allowances), seed)
    scores[ALLOWANCE_LAYER_ID], edge_counts[ALLOWANCE_LAYER_ID] = _run_pagerank_on_edges(
        er_edges, wallets, seed, rep
    )

    # AWP as published: bounded transfer values, restarts weighted by sending activity.
    paper_edges, activeness = build_awp_paper_layer(transfers, config, observation_end, seed)
    scores[AWP_ID], edge_counts[AWP_ID] = _run_pagerank_on_edges(
        paper_edges, wallets, seed, rep, teleport=activeness
    )

    # Transfer layer walked alone (raw amounts, uniform restarts; C-PR at lambda = 0).
    awp_edges = filter_subgraph_edges(build_awp_edges(transfers, observation_end, k, t0), seed)
    scores[TRANSFER_LAYER_ID], edge_counts[TRANSFER_LAYER_ID] = _run_pagerank_on_edges(
        awp_edges, wallets, seed, rep
    )

    # Hybrids (C-PR grid and S-PR) on the allowance layer and the transfer layer.
    hybrid_scores, hybrid_counts = compute_hybrid_scores(wallets, config, er_edges, awp_edges)
    scores.update(hybrid_scores)
    edge_counts.update(hybrid_counts)

    if methods_cfg.get("gf_pr", {}).get("enabled", True):
        gf_edges = build_gf_pr_edges(decoded, wallets)
        scores["gf_pr"], edge_counts["gf_pr"] = _run_pagerank_on_edges(
            gf_edges, wallets, seed | {GMX_POOL_NODE, GMX_SINK_NODE}, rep
        )

    if methods_cfg.get("lp_pr", {}).get("enabled", True):
        lp_edges = build_lp_pr_edges(transfers, decoded, wallets, observation_end, k, t0)
        scores["lp_pr"], edge_counts["lp_pr"] = _run_pagerank_on_edges(
            lp_edges, wallets, seed, rep
        )

    if methods_cfg.get("cw_awp", {}).get("enabled", True) and collateral:
        cw_edges = build_cw_awp_edges(transfers, collateral, observation_end, k, t0)
        scores["cw_awp"], edge_counts["cw_awp"] = _run_pagerank_on_edges(
            cw_edges, wallets, seed, rep
        )

    if methods_cfg.get("riskprop_pr", {}).get("enabled", True):
        rp_edges = build_riskprop_edges(transfers, decoded, wallets, observation_end, k, t0)
        scores["riskprop_pr"], edge_counts["riskprop_pr"] = _run_pagerank_on_edges(
            rp_edges, wallets, seed, rep
        )

    if methods_cfg.get("lf_pr", {}).get("enabled", True):
        if aave_events is not None and not aave_events.empty:
            lf_edges = build_lf_pr_edges(aave_events, observation_end, k, t0)
            scores["lf_pr"], edge_counts["lf_pr"] = _run_pagerank_on_edges(
                lf_edges, wallets, seed, rep
            )
        else:
            scores["lf_pr"] = {w: 0.0 for w in wallets}
            edge_counts["lf_pr"] = 0

    return scores, edge_counts
