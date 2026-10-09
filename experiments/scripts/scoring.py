"""Weighted PageRank, the coupled and seeded walks, and the edge weights of AWP and EndorseRank.

Node ids are int64 global ids into the node table. The semantics are those of
the wallet-reputation pagerank.py and pagerank_variants.py; the matrix assembly
is vectorised so that graphs with a few hundred million edges fit the solver.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Union

import numpy as np
import pandas as pd
from scipy import sparse

SECONDS_PER_DAY = 86400.0

Teleport = Union[Mapping[int, float], pd.Series, None]


def pagerank_params(config: dict[str, Any]) -> dict[str, Any]:
    """damping, tol and max_iter from config/contract_reputation.yaml, ready to pass as keywords."""
    rep = config["reputation"]
    return {
        "damping": float(rep["damping"]),
        "tol": float(rep["pagerank_tolerance"]),
        "max_iter": int(rep["max_iterations"]),
    }


# ---------------------------------------------------------------------------
# Decay and value transform


def age_days(timestamps: Any, anchor: str | pd.Timestamp) -> np.ndarray:
    """Age of each timestamp at ``anchor`` in days, computed as the reference computes it."""
    anchor = pd.Timestamp(anchor)
    anchor = anchor.tz_localize("UTC") if anchor.tzinfo is None else anchor.tz_convert("UTC")
    ts = pd.to_datetime(pd.Series(timestamps), utc=True)
    return ((anchor - ts).dt.total_seconds() / SECONDS_PER_DAY).to_numpy(dtype=np.float64)


def logistic_decay(age_days: Any, k: float, t0: float) -> np.ndarray:
    """sigma(dt) = 1 / (1 + exp(k (dt - t0)))."""
    return 1.0 / (1.0 + np.exp(k * (np.asarray(age_days, dtype=np.float64) - t0)))


def value_transform(x: Any, b: float) -> np.ndarray:
    """V(z) = 2 / (1 + exp(-b z)) - 1 with z = max(x, 0), in [0, 1) (Do, Do and Nguyen 2023, Eq. 3)."""
    z = np.clip(np.asarray(x, dtype=np.float64), 0.0, None)
    return 2.0 / (1.0 + np.exp(-b * z)) - 1.0


# ---------------------------------------------------------------------------
# Edge tables


def _ids(x: Any) -> np.ndarray:
    if x is None:
        return np.empty(0, dtype=np.int64)
    if isinstance(x, (set, frozenset)):
        x = list(x)
    return np.asarray(x, dtype=np.int64).ravel()


def _floats(x: Any) -> np.ndarray:
    return np.asarray(x, dtype=np.float64).ravel()


def sum_edges(src: Any, dst: Any, w: Any) -> pd.DataFrame:
    """Rows with w > 0 summed per (src, dst); build_weighted_edges on integer ids."""
    src, dst, w = _ids(src), _ids(dst), _floats(w)
    keep = w > 0
    work = pd.DataFrame({"src": src[keep], "dst": dst[keep], "w": w[keep]})
    return work.groupby(["src", "dst"], as_index=False, sort=True)["w"].sum()


def activeness(src: Any, dst: Any, sig: Any) -> pd.Series:
    """X_u = sum over v != u of the largest sig on u -> v (AWP's Eq. 2).

    Works on event rows (one decay per transfer or allowance) and on pair rows
    that already hold the largest decay of each pair (``max_sig``).
    """
    src, dst, sig = _ids(src), _ids(dst), _floats(sig)
    keep = src != dst
    work = pd.DataFrame({"src": src[keep], "dst": dst[keep], "sig": sig[keep]})
    latest = work.groupby(["src", "dst"], sort=True)["sig"].max()
    out = latest.groupby(level=0).sum()
    out.index.name = "node_id"
    return out.rename("activeness")


def awp_edges(
    src: Any, dst: Any, value: Any, age: Any, *, k: float, t0: float, b: float
) -> tuple[pd.DataFrame, pd.Series]:
    """AWP as published, on transfer rows (pagerank.build_awp_paper_edges).

    Edge u -> v weighs the sum of sigma(age) V(x) over its transfers; the restart
    weight of u is its activeness over every transfer, zero-valued ones included.
    """
    sig = logistic_decay(age, k, t0)
    edges = sum_edges(src, dst, sig * value_transform(value, b))
    return edges, activeness(src, dst, sig)


def endorserank_edges(
    owner: Any, spender: Any, value: Any, age: Any, *, k: float, t0: float, b: float
) -> tuple[pd.DataFrame, pd.Series]:
    """EndorseRank on latest allowances (pagerank.build_endorserank_vt_edges).

    Rows are the latest allowance of each (token, owner, spender). Edge owner ->
    spender weighs the sum over tokens of sigma(age of the approval) V(amount).
    The second value is the owner activeness used only by the AWP-restart variant.
    """
    owner, spender, value = _ids(owner), _ids(spender), _floats(value)
    sig = logistic_decay(age, k, t0)
    edges = sum_edges(owner, spender, sig * value_transform(value, b))
    pos = value > 0
    return edges, activeness(owner[pos], spender[pos], sig[pos])


def allowance_layer_edges(owner: Any, spender: Any, value: Any) -> pd.DataFrame:
    """C-PR allowance layer: latest amounts summed per owner -> spender, no decay (build_endorserank_edges)."""
    work = pd.DataFrame({"src": _ids(owner), "dst": _ids(spender), "w": _floats(value)})
    return work.groupby(["src", "dst"], as_index=False, sort=True)["w"].sum()


def transfer_layer_edges(src: Any, dst: Any, value: Any, age: Any, *, k: float, t0: float) -> pd.DataFrame:
    """C-PR transfer layer: sum of x sigma(age) per sender -> recipient (build_awp_edges)."""
    return sum_edges(src, dst, _floats(value) * logistic_decay(age, k, t0))


def layer_arrays(
    pairs: pd.DataFrame, weight: str, src: str = "src", dst: str = "dst"
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(src, dst, w) arrays of a pair table, e.g. allow_pairs with weight 'w_er' or 'w_raw'."""
    return _ids(pairs[src]), _ids(pairs[dst]), _floats(pairs[weight])


def touching(src: Any, dst: Any, node_ids: Any) -> np.ndarray:
    """Mask of edges with at least one end point in ``node_ids`` (filter_subgraph_edges)."""
    ids = np.unique(_ids(node_ids))
    return np.isin(_ids(src), ids) | np.isin(_ids(dst), ids)


# ---------------------------------------------------------------------------
# Solver


def _positive_edges(src: Any, dst: Any, w: Any) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    src, dst, w = _ids(src), _ids(dst), _floats(w)
    if not (src.size == dst.size == w.size):
        raise ValueError("src, dst and w differ in length")
    keep = w > 0
    if keep.all():
        return src, dst, w
    return src[keep], dst[keep], w[keep]


def _local_index(id_arrays: Sequence[np.ndarray]) -> tuple[np.ndarray, list[np.ndarray]]:
    """Sorted distinct ids over ``id_arrays`` and the position of every id in that list."""
    parts = [a for a in id_arrays if a.size]
    if not parts:
        return np.empty(0, dtype=np.int64), [np.empty(0, dtype=np.int32) for _ in id_arrays]
    lo = min(int(a.min()) for a in parts)
    hi = max(int(a.max()) for a in parts)
    total = sum(a.size for a in parts)
    if lo >= 0 and hi < max(4 * total, 1 << 20):
        # Dense global ids: a lookup table is linear where np.unique would sort.
        seen = np.zeros(hi + 1, dtype=bool)
        for a in parts:
            seen[a] = True
        nodes = np.flatnonzero(seen).astype(np.int64)
        dtype = np.int32 if nodes.size < 2**31 else np.int64
        lookup = np.empty(hi + 1, dtype=dtype)
        lookup[nodes] = np.arange(nodes.size, dtype=dtype)
        return nodes, [lookup[a] for a in id_arrays]
    nodes = np.unique(np.concatenate(parts))
    return nodes, [np.searchsorted(nodes, a) for a in id_arrays]


def _out_strength(src_local: np.ndarray, w: np.ndarray, n: int) -> tuple[np.ndarray, np.ndarray]:
    out = np.bincount(src_local, weights=w, minlength=n)
    inv = np.zeros(n, dtype=np.float64)
    pos = out > 0
    inv[pos] = 1.0 / out[pos]
    return out, inv


def _transposed(src_local: np.ndarray, dst_local: np.ndarray, vals: np.ndarray, n: int) -> sparse.csr_matrix:
    """CSR of P^T (row = target); duplicate pairs are summed by the COO -> CSR conversion."""
    return sparse.csr_matrix((vals, (dst_local, src_local)), shape=(n, n))


def _teleport_vector(nodes: np.ndarray, teleport: Teleport) -> np.ndarray:
    """Restart distribution over ``nodes``; uniform when ``teleport`` is empty or puts no mass there."""
    n = nodes.size
    if teleport is None or len(teleport) == 0:
        return np.full(n, 1.0 / n, dtype=np.float64)
    t = teleport if isinstance(teleport, pd.Series) else pd.Series(dict(teleport), dtype=np.float64)
    v = t.reindex(nodes).to_numpy(dtype=np.float64, na_value=0.0)
    v = np.where(v > 0, v, 0.0)
    total = v.sum()
    if not total > 0:
        return np.full(n, 1.0 / n, dtype=np.float64)
    return v / total


def _power_iterate(
    mats: list[sparse.csr_matrix],
    dangling: np.ndarray,
    teleport: np.ndarray,
    damping: float,
    tol: float,
    max_iter: int,
) -> tuple[np.ndarray, int]:
    """r <- (1-d) pi + d P^T r + d (dangling mass) pi, from uniform, until the L1 change is below tol.

    ``mats`` holds P^T, or the per-layer parts of P^T whose sum is the mixed walk.
    """
    n = teleport.size
    dangling_idx = np.flatnonzero(dangling)
    base = (1.0 - damping) * teleport
    rank = np.full(n, 1.0 / n, dtype=np.float64)
    tmp = np.empty(n, dtype=np.float64)
    iterations = 0
    for i in range(max_iter):
        iterations = i + 1
        mass = rank[dangling_idx].sum() if dangling_idx.size else 0.0
        new_rank = mats[0] @ rank
        for m in mats[1:]:
            new_rank += m @ rank
        new_rank *= damping
        new_rank += base
        np.multiply(teleport, mass, out=tmp)
        tmp *= damping
        new_rank += tmp
        np.subtract(new_rank, rank, out=tmp)
        np.abs(tmp, out=tmp)
        rank = new_rank
        if tmp.sum() < tol:
            break
    total = rank.sum()
    if total > 0:
        rank = rank / total
    return rank, iterations


def _scores(nodes: np.ndarray, rank: np.ndarray) -> pd.Series:
    return pd.Series(rank, index=pd.Index(nodes, name="node_id"), name="score")


def _empty_scores() -> pd.Series:
    return _scores(np.empty(0, dtype=np.int64), np.empty(0, dtype=np.float64))


def weighted_pagerank(
    src: Any,
    dst: Any,
    w: Any,
    *,
    teleport: Teleport = None,
    damping: float,
    tol: float,
    max_iter: int,
    extra_nodes: Any = None,
) -> tuple[pd.Series, int]:
    """Weighted PageRank (pagerank.weighted_pagerank on integer ids).

    The node set is the end points of the edges with w > 0 plus ``extra_nodes``
    (isolated nodes, for the isolated-node sensitivity analysis). Duplicate
    (src, dst) edges are summed and self-loops kept. P[u, v] = w / out-strength;
    nodes without out-edges are dangling and their mass follows the restarts.
    ``teleport`` (id -> non-negative mass) is normalised over the node set and
    uniform when None, empty or of zero mass there. Without a positive edge the
    result is empty, whatever ``extra_nodes`` holds, as in the reference.
    Returns the score of every node (sums to 1) and the iterations run.
    """
    src, dst, w = _positive_edges(src, dst, w)
    if src.size == 0:
        return _empty_scores(), 0
    nodes, (s, d, _) = _local_index([src, dst, _ids(extra_nodes)])
    n = nodes.size
    out, inv = _out_strength(s, w, n)
    pt = _transposed(s, d, w * inv[s], n)
    restart = _teleport_vector(nodes, teleport)
    rank, iterations = _power_iterate([pt], ~(out > 0), restart, damping, tol, max_iter)
    return _scores(nodes, rank), iterations


def coupled_pagerank(
    layers: Sequence[tuple[Any, Any, Any, float]],
    *,
    damping: float,
    tol: float,
    max_iter: int,
) -> tuple[pd.Series, int]:
    """PageRank on a per-node mixture of edge layers (pagerank.coupled_pagerank).

    ``layers`` holds (src, dst, w, layer_weight). A layer is active when its
    weight is positive and it has a positive edge; the node set is the union of
    the end points of the active layers. The transition row of u is

        P[u, .] = sum_l a_l(u) P_l[u, .],
        a_l(u) = weight_l 1[u has out-edges in l] / sum_k weight_k 1[u has out-edges in k],

    so a node with out-edges in one layer follows that layer alone, and a node
    without out-edges in any active layer is dangling. Restarts are uniform.
    """
    active = []
    for src, dst, w, weight in layers:
        if float(weight) <= 0:
            continue
        s, d, ww = _positive_edges(src, dst, w)
        if s.size:
            active.append((s, d, ww, float(weight)))
    if not active:
        return _empty_scores(), 0

    nodes, local = _local_index([a for s, d, _, _ in active for a in (s, d)])
    n = nodes.size
    strengths = []
    denom = np.zeros(n, dtype=np.float64)
    for i, (_, _, w, weight) in enumerate(active):
        out, inv = _out_strength(local[2 * i], w, n)
        has = (out > 0).astype(np.float64)
        denom += weight * has
        strengths.append((inv, has))

    pos = denom > 0
    mats = []
    for i, (_, _, w, weight) in enumerate(active):
        inv, has = strengths[i]
        alpha = np.zeros(n, dtype=np.float64)
        alpha[pos] = weight * has[pos] / denom[pos]
        s, d = local[2 * i], local[2 * i + 1]
        mats.append(_transposed(s, d, w * inv[s] * alpha[s], n))

    restart = np.full(n, 1.0 / n, dtype=np.float64)
    rank, iterations = _power_iterate(mats, ~pos, restart, damping, tol, max_iter)
    return _scores(nodes, rank), iterations


def seeded_pagerank(
    src: Any,
    dst: Any,
    w: Any,
    allowance_scores: pd.Series | None,
    *,
    damping: float,
    tol: float,
    max_iter: int,
) -> tuple[pd.Series, int]:
    """S-PR: the transfer layer walked with restarts from C-PR(lambda = 1) (compute_hybrid_scores).

    ``allowance_scores`` are restricted to the transfer-layer nodes and
    renormalised; the restarts are uniform when they put no mass there.
    """
    return weighted_pagerank(
        src, dst, w, teleport=allowance_scores, damping=damping, tol=tol, max_iter=max_iter
    )


def scores_on(wallet_ids: Any, scores: pd.Series, missing: float = 0.0) -> pd.Series:
    """Scores aligned to a cohort; wallets outside the solver graph get ``missing`` (0, as the reference)."""
    ids = pd.Index(_ids(wallet_ids), name="node_id")
    values = scores.reindex(ids).to_numpy(dtype=np.float64, na_value=missing)
    return pd.Series(values, index=ids, name=scores.name)
