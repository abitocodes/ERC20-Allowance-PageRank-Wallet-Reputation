"""Weighted PageRank on sparse directed graphs."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import sparse


def build_weighted_edges(
    df: pd.DataFrame,
    from_col: str,
    to_col: str,
    weight_col: str,
) -> pd.DataFrame:
    """Aggregate duplicate edges by summing weights."""
    work = df[[from_col, to_col, weight_col]].copy()
    work = work[work[weight_col] > 0]
    return (
        work.groupby([from_col, to_col], as_index=False)[weight_col]
        .sum()
        .rename(columns={from_col: "from_node", to_col: "to_node", weight_col: "weight"})
    )


def filter_subgraph_edges(
    edges: pd.DataFrame,
    seed_wallets: set[str],
) -> pd.DataFrame:
    """Keep edges touching at least one seed wallet (includes 1-hop neighbors)."""
    mask = edges["from_node"].isin(seed_wallets) | edges["to_node"].isin(seed_wallets)
    return edges[mask].copy()


def _adjacency_on_index(
    edges: pd.DataFrame,
    idx: dict[str, int],
    n: int,
) -> tuple[sparse.csr_matrix, np.ndarray]:
    """Weighted adjacency and out-strength on a fixed node index.

    Edges whose end points are not in ``idx`` are ignored; non-positive weights
    are dropped. The per-edge loop is the same construction path that the
    runtime benchmark has always timed, so single-layer timings stay comparable.
    """
    row: list[int] = []
    col: list[int] = []
    data: list[float] = []
    out_strength = np.zeros(n, dtype=np.float64)
    for _, r in edges.iterrows():
        u = idx.get(r["from_node"])
        v = idx.get(r["to_node"])
        if u is None or v is None:
            continue
        w = float(r["weight"])
        if w <= 0:
            continue
        row.append(u)
        col.append(v)
        data.append(w)
        out_strength[u] += w
    adj = sparse.csr_matrix((data, (row, col)), shape=(n, n))
    return adj, out_strength


def _row_normalise(adj: sparse.csr_matrix, out_strength: np.ndarray) -> sparse.csr_matrix:
    """P[u, v] = w[u, v] / sum_out(u) for rows with positive out-strength."""
    n = adj.shape[0]
    inv_out = np.zeros(n, dtype=np.float64)
    nonzero = out_strength > 0
    inv_out[nonzero] = 1.0 / out_strength[nonzero]
    return sparse.diags(inv_out, format="csr") @ adj


def _teleport_vector(
    nodes: list[str],
    teleport: dict[str, float] | None,
    floor: float = 0.0,
) -> np.ndarray:
    """Normalised restart distribution; uniform when ``teleport`` is None or empty."""
    n = len(nodes)
    if not teleport:
        return np.full(n, 1.0 / n, dtype=np.float64)
    v = np.asarray([max(float(teleport.get(node, 0.0)), 0.0) for node in nodes], dtype=np.float64)
    if floor > 0:
        v = v + float(floor)
    total = v.sum()
    if total <= 0:
        return np.full(n, 1.0 / n, dtype=np.float64)
    return v / total


def _power_iterate(
    transition: sparse.csr_matrix,
    dangling: np.ndarray,
    teleport: np.ndarray,
    damping: float,
    tol: float,
    max_iter: int,
) -> tuple[np.ndarray, int]:
    """Damped power iteration; dangling mass is redistributed by ``teleport``."""
    n = transition.shape[0]
    rank = np.full(n, 1.0 / n, dtype=np.float64)
    iterations = 0
    for i in range(max_iter):
        iterations = i + 1
        dangling_contrib = rank[dangling].sum() * teleport
        new_rank = (1.0 - damping) * teleport + damping * (transition.T @ rank)
        new_rank = new_rank + damping * dangling_contrib
        if np.abs(new_rank - rank).sum() < tol:
            rank = new_rank
            break
        rank = new_rank
    total = rank.sum()
    if total > 0:
        rank = rank / total
    return rank, iterations


def weighted_pagerank(
    edges: pd.DataFrame,
    damping: float = 0.85,
    tol: float = 1e-8,
    max_iter: int = 100,
    return_iterations: bool = False,
    teleport: dict[str, float] | None = None,
    teleport_floor: float = 0.0,
    extra_nodes: set[str] | None = None,
) -> dict[str, float] | tuple[dict[str, float], int]:
    """
    Run weighted PageRank on edge list with columns: from_node, to_node, weight.

    ``teleport`` (node -> non-negative mass) personalises the restart
    distribution and the dangling redistribution; None means uniform.
    ``extra_nodes`` are added as isolated nodes (no edges), so under uniform
    teleportation they score like any node without in-edges instead of being
    left out.
    Returns mapping node -> score (sums to 1 over reachable nodes).
    """
    if edges.empty:
        if return_iterations:
            return {}, 0
        return {}

    nodes = sorted(set(edges["from_node"]) | set(edges["to_node"]) | set(extra_nodes or ()))
    idx = {n: i for i, n in enumerate(nodes)}
    n = len(nodes)

    adj, out_strength = _adjacency_on_index(edges, idx, n)
    transition = _row_normalise(adj, out_strength)
    dangling = ~(out_strength > 0)
    restart = _teleport_vector(nodes, teleport, floor=teleport_floor)

    rank, iterations = _power_iterate(transition, dangling, restart, damping, tol, max_iter)

    scores = {nodes[i]: float(rank[i]) for i in range(n)}
    if return_iterations:
        return scores, iterations
    return scores


def coupled_pagerank(
    layers: list[tuple[pd.DataFrame, float]],
    damping: float = 0.85,
    tol: float = 1e-8,
    max_iter: int = 100,
    return_iterations: bool = False,
) -> dict[str, float] | tuple[dict[str, float], int]:
    """PageRank on a per-node mixture of several edge layers.

    ``layers`` is a list of ``(edges, weight)`` pairs sharing one node set
    (the union of all end points). For node ``u`` the transition row is

        P[u, .] = sum_l a_l(u) * P_l[u, .],
        a_l(u) = weight_l * 1[u has out-edges in l] / sum_k weight_k * 1[u has out-edges in k],

    so a node present in only one layer follows that layer alone and a node
    with no out-edges in any layer is dangling (uniform redistribution).
    With two layers and weights (lambda, 1 - lambda), lambda = 1 reproduces the
    first layer's PageRank and lambda = 0 the second's whenever both layers
    span the same node set. Teleportation is uniform.
    """
    active = [(e, float(w)) for e, w in layers if e is not None and not e.empty and float(w) > 0]
    if not active:
        if return_iterations:
            return {}, 0
        return {}

    node_set: set[str] = set()
    for edges, _ in active:
        node_set.update(edges["from_node"])
        node_set.update(edges["to_node"])
    nodes = sorted(node_set)
    idx = {n: i for i, n in enumerate(nodes)}
    n = len(nodes)

    transitions: list[sparse.csr_matrix] = []
    presence: list[np.ndarray] = []
    weights: list[float] = []
    for edges, weight in active:
        adj, out_strength = _adjacency_on_index(edges, idx, n)
        transitions.append(_row_normalise(adj, out_strength))
        presence.append((out_strength > 0).astype(np.float64))
        weights.append(weight)

    denom = np.zeros(n, dtype=np.float64)
    for w, has in zip(weights, presence):
        denom += w * has
    mixed = sparse.csr_matrix((n, n), dtype=np.float64)
    for w, has, trans in zip(weights, presence, transitions):
        alpha = np.zeros(n, dtype=np.float64)
        pos = denom > 0
        alpha[pos] = w * has[pos] / denom[pos]
        mixed = mixed + sparse.diags(alpha, format="csr") @ trans

    dangling = denom <= 0
    restart = np.full(n, 1.0 / n, dtype=np.float64)
    rank, iterations = _power_iterate(mixed, dangling, restart, damping, tol, max_iter)

    scores = {nodes[i]: float(rank[i]) for i in range(n)}
    if return_iterations:
        return scores, iterations
    return scores


def assign_dense_ranks(
    wallets: list[str],
    scores: dict[str, float],
) -> pd.DataFrame:
    """Rank wallets by score descending (1 = highest)."""
    rows = [{"wallet": w, "score": scores.get(w, 0.0)} for w in wallets]
    df = pd.DataFrame(rows)
    df = df.sort_values(["score", "wallet"], ascending=[False, True]).reset_index(drop=True)
    df["rank"] = range(1, len(df) + 1)
    return df


def logistic_time_decay(
    delta_days: pd.Series,
    k: float,
    t0: float,
) -> pd.Series:
    """sigma(dt) = 1 / (1 + exp(k * (dt - t0)))."""
    return 1.0 / (1.0 + np.exp(k * (delta_days - t0)))


def build_awp_edges(
    transfers: pd.DataFrame,
    observation_end: pd.Timestamp,
    k: float,
    t0_days: float,
) -> pd.DataFrame:
    """Aggregate time-decayed transfer weights into directed edges."""
    work = transfers.copy()
    work["block_timestamp"] = pd.to_datetime(work["block_timestamp"], utc=True)
    delta = (observation_end - work["block_timestamp"]).dt.total_seconds() / 86400.0
    work["decay"] = logistic_time_decay(delta, k, t0_days)
    work["weighted_value"] = work["value"].astype(float) * work["decay"]
    return build_weighted_edges(work, "from_address", "to_address", "weighted_value")


def value_transform(values: pd.Series, b: float) -> pd.Series:
    """V(z) = 2 / (1 + exp(-b z)) - 1, the value transform of Do, Do and Nguyen (2023, Eq. 3).

    Each transfer gets a weight in [0, 1), so one large transfer counts at most once.
    """
    z = values.astype(float).clip(lower=0.0)
    return 2.0 / (1.0 + np.exp(-b * z)) - 1.0


def build_awp_paper_edges(
    transfers: pd.DataFrame,
    observation_end: pd.Timestamp,
    k: float,
    t0_days: float,
    b: float,
) -> tuple[pd.DataFrame, dict[str, float]]:
    """Edges and restart weights of AWP in the form published by Do, Do and Nguyen (2023).

    The edge i -> j weighs the sum of T(t) V(z) over the transfers from i to j
    (their Eq. 3), with T the logistic decay of build_awp_edges. The restart
    weight of node i is its activeness X_i, the sum over j != i of the largest
    T(t) on i -> j (their Eq. 2), so restarts favour addresses that sent recently.
    As in Eq. 2, X_i counts transfers of zero value too; they add nothing to Y.
    The paper gives no values for the decay or for b; this pipeline supplies its own.
    """
    work = transfers.copy()
    work["block_timestamp"] = pd.to_datetime(work["block_timestamp"], utc=True)
    delta = (observation_end - work["block_timestamp"]).dt.total_seconds() / 86400.0
    work["decay"] = logistic_time_decay(delta, k, t0_days)
    work["paper_weight"] = work["decay"] * value_transform(work["value"], b)
    edges = build_weighted_edges(work, "from_address", "to_address", "paper_weight")
    others = work[work["from_address"] != work["to_address"]]
    latest = others.groupby(["from_address", "to_address"])["decay"].max()
    activeness = latest.groupby(level=0).sum()
    return edges, {str(node): float(x) for node, x in activeness.items()}


def build_endorserank_vt_edges(
    allowances: pd.DataFrame,
    observation_end: pd.Timestamp,
    k: float,
    t0_days: float,
    b: float,
) -> tuple[pd.DataFrame, dict[str, float]]:
    """Edges of EndorseRank: AWP's edge weights (build_awp_paper_edges) on the allowance graph.

    ``allowances`` holds the latest positive allowance of each (token, owner,
    spender), as build_endorserank_edges takes it; each one is an endorsement
    made at the time of its approval. The edge owner -> spender weighs the sum
    over tokens of T(t) V(z), with z the approved amount and t the time of the
    approval. EndorseRank restarts uniformly. The second return value is the
    restart weight AWP's rule would give each owner (the sum over the spenders
    it endorses of the largest T(t) among its allowances to each); it is used
    only for the sensitivity analysis with AWP's restarts.
    """
    work = allowances.copy()
    work["block_timestamp"] = pd.to_datetime(work["block_timestamp"], utc=True)
    delta = (observation_end - work["block_timestamp"]).dt.total_seconds() / 86400.0
    work["decay"] = logistic_time_decay(delta, k, t0_days)
    work["paper_weight"] = work["decay"] * value_transform(work["value"], b)
    edges = build_weighted_edges(work, "owner", "spender", "paper_weight")
    others = work[(work["owner"] != work["spender"]) & (work["value"].astype(float) > 0)]
    latest = others.groupby(["owner", "spender"])["decay"].max()
    activeness = latest.groupby(level=0).sum()
    return edges, {str(node): float(x) for node, x in activeness.items()}


def build_endorserank_edges(allowances: pd.DataFrame) -> pd.DataFrame:
    """Sum latest allowance amounts per owner -> spender across tokens.

    This is the allowance layer of C-PR (raw amounts, no decay); walked alone with
    uniform restarts it is C-PR at lambda = 1.
    """
    agg = (
        allowances.groupby(["owner", "spender"], as_index=False)["value"]
        .sum()
        .rename(columns={"owner": "from_node", "spender": "to_node", "value": "weight"})
    )
    return agg
