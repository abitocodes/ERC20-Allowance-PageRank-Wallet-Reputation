"""The discovery-order test of docs/discovery_protocol.md: crawls of the contract graph and their measures.

A crawler that has read some contracts knows only the edges they revealed and chooses which known
contract to read next (Cho, Garcia-Molina and Page 1998). This module holds the pure parts of the
test, on node ids 0..n-1 numbered in address order:

  graph       Layer, CrawlGraph: the pairs of each layer with their weights (allowance: w_er, w_raw,
              max_sig; transfer: w_awp, w_raw, max_sig), the union pattern and the address of each
              node; CrawlGraph.restrict() renumbers a node subset
  structure   bow_tie() (giant SCC, IN, OUT, other, the WCC that holds the giant SCC), BowTie.universe(),
              pick_seeds()
  schedule    batch_size(), schedule(), recomputes() = R(rho, n), primary_mode(), projected_hours() = T(rho),
              rules() (the primary mode, rho, q and the stop flags of section 7)
  crawl       Adjacency, Crawl: one crawl for one (seed, ordering, reveal mode, rho), section 4;
              walk() and full_scores() run the scoring.py methods on revealed or complete edges
  measures    hot_set(), rank_order(), ideal_order(), hubs(), without_hubs(), curve_grid(), p_st(), p_cs(),
              captured(), visit_scores() (g_x), auc(), visits_to_reach() and the ideal and random references

Conventions the protocol leaves to the code:
  - ceil(s n) (batch sizes, hot-set ranks, AUC horizons, hub counts) is computed exactly, with s
    read as the decimal fraction it is written as (0.05 is 1/20); in floats ceil(0.07 x 100) is 8.
  - The discovery index of a contract is the visit at which it was first discovered (the seed's is
    0). BFS orders the frontier by (discovery index, SHA-256 of seed address + contract address,
    both lowercase 0x hex); every other ordering breaks ties by (discovery index, node id).
  - The random ordering makes one uniform choice among the frontier contracts at every visit (its
    batches hold one contract), so that, like BFS, its visit order does not depend on rho. It keeps
    the frontier as a list: the contracts discovered at a visit are appended in node-id order, and
    a visited one is replaced by the last contract of the list; a draw is the generator's integer
    below the length of the list.
  - Ties: the frontier, sorted by decreasing score, is cut into groups; a group starts at its
    highest score and holds every following score within tie_tolerance x the frontier maximum of
    it. A pick counts as decided by a tie when its group holds more than one contract.
  - The union pattern holds the distinct pairs (p, q), p != q, with an edge in either layer; the
    bow-tie, |E_U| and the cost axis count these pairs.
  - In the both mode an edge is revealed at the first visit of either of its ends.

scoring.py is imported only by the functions that compute walks, so the structure pilot
(run_discovery.py --feasibility) never loads weight code.
"""

from __future__ import annotations

import hashlib
import re
import time
from dataclasses import dataclass, field
from fractions import Fraction
from typing import TYPE_CHECKING, Any

import numpy as np
from scipy import sparse
from scipy.sparse.csgraph import breadth_first_order, connected_components

if TYPE_CHECKING:
    import pandas as pd

ALLOW_WEIGHTS = ("w_er", "w_raw", "max_sig")
TRANSFER_WEIGHTS = ("w_awp", "w_raw", "max_sig")
MODES = ("out", "both")
COUNTS = ("ib_a", "ib_t", "ib_u")
COUPLED_LAMBDA = {"cpr_l25": 0.25, "cpr_l50": 0.5, "cpr_l75": 0.75}
WALKS = ("endorserank", "endorserank_activity", "awp", "cpr_l50", "cpr_l25", "cpr_l75", "cpr_l100", "cpr_l0",
         "spr")
DIAGNOSTIC = "delta"
ORDERINGS = ("bfs", "random", *COUNTS, *WALKS, DIAGNOSTIC)
FREEZES = ("tobs", "t1")
_ADDRESS = re.compile(r"0x[0-9a-f]{40}")


def _scoring():
    import scoring  # weight code, loaded only where a walk is computed

    return scoring


# ---------------------------------------------------------------------------
# Exact shares


def decimal(x: Any) -> Fraction:
    """``x`` as the decimal fraction it is written as: 0.05 is 1/20, "0.0125" is 1/80."""
    if isinstance(x, Fraction):
        return x
    if isinstance(x, float):
        return Fraction(repr(x))
    return Fraction(x)


def ceil_share(share: Any, n: int) -> int:
    """ceil(share x n), exactly."""
    f = decimal(share) * int(n)
    return -(-f.numerator // f.denominator)


def batch_size(rho: Any, visits: int) -> int:
    """b(V) = max(1, ceil(rho V)) (protocol section 4)."""
    return max(1, ceil_share(rho, visits))


def schedule(rho: Any, n: int) -> list[int]:
    """Batch sizes of a crawl of n contracts whose frontier never runs short: from V = 1 (the seed)
    each recompute adds min(b(V), n - V) visits."""
    r = decimal(rho)
    num, den = r.numerator, r.denominator
    out, v = [], 1
    while v < n:
        b = min(max(1, -(-num * v // den)), n - v)
        out.append(b)
        v += b
    return out


def recomputes(rho: Any, n: int) -> int:
    """R(rho, n): the number of recomputes of the schedule for a universe of n contracts."""
    return len(schedule(rho, n))


# ---------------------------------------------------------------------------
# Graph


@dataclass
class Layer:
    """Distinct (src, dst) pairs of one layer and their weights, by name."""

    src: np.ndarray
    dst: np.ndarray
    weights: dict[str, np.ndarray]

    def __post_init__(self) -> None:
        self.src = np.asarray(self.src, dtype=np.int64).ravel()
        self.dst = np.asarray(self.dst, dtype=np.int64).ravel()
        self.weights = {k: np.asarray(v, dtype=np.float64).ravel() for k, v in self.weights.items()}
        if self.src.size != self.dst.size or any(v.size != self.src.size for v in self.weights.values()):
            raise ValueError("src, dst and the weights differ in length")

    @property
    def size(self) -> int:
        return int(self.src.size)

    def take(self, idx: np.ndarray) -> Layer:
        return Layer(self.src[idx], self.dst[idx], {k: v[idx] for k, v in self.weights.items()})


@dataclass
class CrawlGraph:
    """Contracts 0..n-1 in address order, the allowance and transfer layers and their union pattern."""

    address: np.ndarray
    allow: Layer
    transfer: Layer
    union_src: np.ndarray = field(init=False, repr=False)
    union_dst: np.ndarray = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.address = np.asarray(self.address, dtype=object).ravel()
        n = self.n
        if any(not isinstance(a, str) or not _ADDRESS.fullmatch(a) for a in self.address):
            raise ValueError("addresses must be lowercase 0x hex of 20 bytes")
        if n > 1 and not bool(np.all(self.address[1:] > self.address[:-1])):
            raise ValueError("node ids must be numbered in increasing address order")
        for name, layer, keys in (("allow", self.allow, ALLOW_WEIGHTS), ("transfer", self.transfer, TRANSFER_WEIGHTS)):
            missing = sorted(set(keys) - set(layer.weights))
            if missing:
                raise ValueError(f"{name} lacks the weights {missing}")
            if layer.size:
                lo = min(int(layer.src.min()), int(layer.dst.min()))
                hi = max(int(layer.src.max()), int(layer.dst.max()))
                if lo < 0 or hi >= n:
                    raise ValueError(f"{name} has a node id outside 0..{n - 1}")
                if np.unique(layer.src * n + layer.dst).size != layer.size:
                    raise ValueError(f"{name} holds a pair twice")
            for k in keys:
                w = layer.weights[k]
                if not np.isfinite(w).all() or (w < 0).any():
                    raise ValueError(f"{name}.{k} must be finite and non-negative")
        src = np.concatenate([self.allow.src, self.transfer.src])
        dst = np.concatenate([self.allow.dst, self.transfer.dst])
        keep = src != dst
        key = np.unique(src[keep] * n + dst[keep])
        self.union_src, self.union_dst = key // max(n, 1), key % max(n, 1)

    @property
    def n(self) -> int:
        return int(self.address.size)

    def restrict(self, nodes: Any) -> tuple[CrawlGraph, np.ndarray]:
        """The subgraph induced on ``nodes``, renumbered 0..k-1 in the same order, and the old ids."""
        nodes = np.unique(np.asarray(nodes, dtype=np.int64))
        lookup = np.full(self.n, -1, dtype=np.int64)
        lookup[nodes] = np.arange(nodes.size)

        def part(layer: Layer) -> Layer:
            keep = (lookup[layer.src] >= 0) & (lookup[layer.dst] >= 0)
            sub = layer.take(np.flatnonzero(keep))
            return Layer(lookup[sub.src], lookup[sub.dst], sub.weights)

        return CrawlGraph(self.address[nodes], part(self.allow), part(self.transfer)), nodes

    def union_in_degree(self) -> np.ndarray:
        """IB_U: distinct other contracts with an edge to each node in either layer."""
        return np.bincount(self.union_dst, minlength=self.n).astype(np.int64)


# ---------------------------------------------------------------------------
# Structure


@dataclass
class BowTie:
    """Parts of the union graph (masks over node ids) and the edges of the two universes."""

    scc: np.ndarray        # the giant strongly connected component
    in_: np.ndarray        # reaches the SCC
    out: np.ndarray        # reached from the SCC
    other: np.ndarray      # in the union graph, none of the above
    isolated: np.ndarray   # without an edge of the union graph (self-loops ignored)
    wcc: np.ndarray        # the weakly connected component that holds the giant SCC
    n_edges: int           # edges of the union graph
    e_u: int               # edges with both ends in SCC u OUT
    e_wcc: int             # edges with both ends in that WCC

    def universe(self, mode: str) -> np.ndarray:
        """U: SCC u OUT for the out mode, the WCC that holds the giant SCC for the both mode (protocol section 2).

        Both universes hold the giant SCC, so a crawl from a seed in it can visit the whole universe."""
        if mode == "out":
            return np.flatnonzero(self.scc | self.out)
        if mode == "both":
            return np.flatnonzero(self.wcc)
        raise ValueError(f"mode must be one of {MODES}")

    def universe_edges(self, mode: str) -> int:
        return self.e_u if mode == "out" else self.e_wcc

    def sizes(self) -> dict[str, Any]:
        return {
            "nodes": int((~self.isolated).sum()), "edges": self.n_edges,
            "scc": int(self.scc.sum()), "in": int(self.in_.sum()), "out": int(self.out.sum()),
            "other": int(self.other.sum()),
            "U": int((self.scc | self.out).sum()), "E_U": self.e_u,
            "WCC": int(self.wcc.sum()), "E_WCC": self.e_wcc,
        }


def _largest(labels: np.ndarray, present: np.ndarray) -> np.ndarray:
    """Mask of the largest component among present nodes; a tie goes to the one with the lowest id."""
    lab = labels[present]
    sizes = np.bincount(lab)
    best = np.flatnonzero(sizes == sizes.max())
    label = lab[np.isin(lab, best)][0]
    return (labels == label) & present


def bow_tie(n: int, src: Any, dst: Any) -> BowTie:
    """Bow-tie of the union graph on nodes 0..n-1 (duplicate pairs and self-loops ignored).

    The giant SCC is the largest strongly connected component (a tie goes to the one with the lowest node id);
    the WCC is the weakly connected component that holds it, which need not be the largest WCC.
    """
    src = np.asarray(src, dtype=np.int64).ravel()
    dst = np.asarray(dst, dtype=np.int64).ravel()
    keep = src != dst
    key = np.unique(src[keep] * n + dst[keep])
    s, d = key // max(n, 1), key % max(n, 1)
    present = np.zeros(n, dtype=bool)
    present[s] = True
    present[d] = True
    if s.size == 0:
        none = np.zeros(n, dtype=bool)
        return BowTie(none, none.copy(), none.copy(), none.copy(), ~present, none.copy(), 0, 0, 0)
    a = sparse.csr_matrix((np.ones(s.size, dtype=np.int8), (s, d)), shape=(n, n))
    _, strong = connected_components(a, directed=True, connection="strong")
    scc = _largest(strong, present)
    root = int(np.flatnonzero(scc)[0])
    reach = np.zeros(n, dtype=bool)
    reach[breadth_first_order(a, root, directed=True, return_predecessors=False)] = True
    back = np.zeros(n, dtype=bool)
    back[breadth_first_order(a.T.tocsr(), root, directed=True, return_predecessors=False)] = True
    out = reach & ~scc
    in_ = back & ~scc
    other = present & ~(scc | out | in_)
    _, weak = connected_components(a, directed=True, connection="weak")
    wcc = (weak == weak[root]) & present
    inu = scc | out
    return BowTie(scc, in_, out, other, ~present, wcc, int(s.size), int((inu[s] & inu[d]).sum()),
                  int((wcc[s] & wcc[d]).sum()))


def sha_order(values: Any, prefix: str) -> np.ndarray:
    """Positions of ``values`` sorted by SHA-256 of prefix + value (lowest digest first)."""
    digests = np.array([hashlib.sha256((prefix + str(v)).encode("ascii")).hexdigest() for v in values])
    return np.argsort(digests, kind="stable")


def sha_ranks(address: np.ndarray, prefix: str) -> np.ndarray:
    """Rank of every node (0 = lowest) by SHA-256 of prefix + its address."""
    order = sha_order(address, prefix)
    rank = np.empty(order.size, dtype=np.int64)
    rank[order] = np.arange(order.size)
    return rank


def pick_seeds(address: np.ndarray, candidates: Any, n: int, salt: str) -> np.ndarray:
    """The n candidate node ids with the lowest SHA-256 of salt + address, lowest first (section 3)."""
    candidates = np.asarray(candidates, dtype=np.int64)
    order = sha_order(np.asarray(address, dtype=object)[candidates], salt)
    return candidates[order[:n]]


def random_generator(salt: str, seed_address: str) -> np.random.Generator:
    """The generator of the random ordering, seeded by SHA-256 of salt + seed address."""
    digest = hashlib.sha256((salt + seed_address).encode("ascii")).digest()
    return np.random.default_rng(int.from_bytes(digest, "big"))


# ---------------------------------------------------------------------------
# Rules of the structure pilot (protocol section 7)


def primary_mode(sizes: dict[str, Any], cfg: dict[str, Any]) -> str:
    """The mode rule of section 7: both is primary if |SCC u OUT| < both_mode_ratio x |WCC|, else out."""
    return "both" if sizes["U"] < decimal(cfg["both_mode_ratio"]) * sizes["WCC"] else "out"


def primary_sizes(sizes: dict[str, Any], cfg: dict[str, Any]) -> tuple[int, int]:
    """|P| and |E_P|: the size and the union pairs of the primary universe (SCC u OUT, or the WCC)."""
    if primary_mode(sizes, cfg) == "both":
        return int(sizes["WCC"]), int(sizes["E_WCC"])
    return int(sizes["U"]), int(sizes["E_U"])


def projected_hours(rho: Any, sizes: dict[str, int], cfg: dict[str, Any]) -> float:
    """T(rho) of section 7 in hours, for the sizes U, E_U, WCC and E_WCC of the t1 pilot:

        12 ns x 30 x [N_out R(rho, |SCC u OUT|) |E_U| + N_both R(rho, |WCC|) |E_WCC| + N_4 R(rho/4, |P|) |E_P|] / W

    where P is the primary universe of the mode rule and N_4 the crawls of the rho/4 sensitivity, which runs in
    the primary mode only.
    """
    r = decimal(rho)
    walk_crawls = int(cfg["walk_solves"]) * int(cfg["n_seeds"]) * len(FREEZES)
    quarter = int(cfg["walk_solves"]) * int(cfg["rho_sensitivity"]["seeds"]) * len(FREEZES)
    r4 = r / int(cfg["rho_sensitivity"]["divisor"])
    n_p, e_p = primary_sizes(sizes, cfg)
    work = (walk_crawls * recomputes(r, sizes["U"]) * sizes["E_U"]
            + walk_crawls * recomputes(r, sizes["WCC"]) * sizes["E_WCC"]
            + quarter * recomputes(r4, n_p) * e_p)
    seconds = float(cfg["ns_per_edge_iteration"]) * 1e-9 * int(cfg["warm_iterations"]) * work
    return seconds / int(cfg["projection_workers"]) / 3600.0


def rules(sizes: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any]:
    """The primary mode, rho, q and the stop flags of section 7 from the counts of the t1 pilot, in that order.

    ``sizes`` holds U (|SCC u OUT|), E_U, WCC, E_WCC, allow_capped_edges (capped allowance edges between
    contracts) and allow_in_share (the share of SCC u OUT with a capped allowance in-edge); ``cfg`` is
    cfg["discovery"]. The mode rule names the primary universe P; rho is the smallest value of the grid whose
    T(rho) is within the budget; q is q_primary if |P| >= small_universe and q_small otherwise, for both modes.
    """
    mode = primary_mode(sizes, cfg)
    n_p, e_p = primary_sizes(sizes, cfg)
    divisor = int(cfg["rho_sensitivity"]["divisor"])
    grid = sorted(decimal(r) for r in cfg["rho_grid"])
    hours = {str(float(r)): projected_hours(r, sizes, cfg) for r in grid}
    recs = {str(float(r)): {"U": recomputes(r, sizes["U"]), "WCC": recomputes(r, sizes["WCC"]),
                            "P_quarter": recomputes(r / divisor, n_p)}
            for r in grid}
    fit = [r for r in grid if hours[str(float(r))] <= float(cfg["runtime_budget_hours"])]
    rho = float(fit[0]) if fit else None
    q = float(cfg["q_primary"]) if n_p >= int(cfg["small_universe"]) else float(cfg["q_small"])
    stop = {
        "no_rho_within_budget": rho is None,
        "few_capped_allowance_edges": sizes["allow_capped_edges"] < int(cfg["stop_min_allow_edges"]),
        "few_capped_allowance_in_edges": sizes["allow_in_share"] < float(cfg["stop_min_allow_share"]),
    }
    return {
        "primary_mode": mode, "primary_universe": {"name": "WCC" if mode == "both" else "U", "P": n_p, "E_P": e_p},
        "rho": rho, "q": q,
        "projected_hours": hours, "recomputes": recs, "stop": stop, "stopped": any(stop.values()),
    }


# ---------------------------------------------------------------------------
# Walks


def walk(method: str, allow: Layer, transfer: Layer, nodes: np.ndarray, params: dict[str, Any],
         prev: dict[str, pd.Series] | None = None) -> tuple[pd.Series, int, int, dict[str, pd.Series]]:
    """One walk of scripts/graphs.py on the given edges with the node set ``nodes``.

    The edges are the pairs with their full-graph weights; every walk adds ``nodes`` as extra
    nodes, so its restarts run over them, and starts from ``prev`` (the warm start of section 4)
    when given. S-PR is weighted_pagerank with the C-PR(1) restarts, the walk seeded_pagerank
    runs, so that it takes the node set as well. A walk whose layers hold no edge of positive weight
    has every node dangling: its scores are its restart vector over ``nodes`` (C-PR(1) for S-PR,
    1/|nodes| for the walks with uniform restarts), which the next call warm-starts from (protocol
    section 4), where the solver itself returns nothing. Returns the scores, the iterations, the
    number of solves and the vectors to warm-start the next call with.
    """
    sc = _scoring()
    prev = prev or {}
    a, t = allow, transfer
    kw = {"extra_nodes": nodes, **params}
    restart = None
    if method == "endorserank":
        s, it = sc.weighted_pagerank(a.src, a.dst, a.weights["w_er"], init=prev.get(method), **kw)
    elif method == "endorserank_activity":
        restart = sc.activeness(a.src, a.dst, a.weights["max_sig"])
        s, it = sc.weighted_pagerank(a.src, a.dst, a.weights["w_er"], teleport=restart, init=prev.get(method), **kw)
    elif method == "awp":
        restart = sc.activeness(t.src, t.dst, t.weights["max_sig"])
        s, it = sc.weighted_pagerank(t.src, t.dst, t.weights["w_awp"], teleport=restart, init=prev.get(method), **kw)
    elif method == "cpr_l100":
        s, it = sc.weighted_pagerank(a.src, a.dst, a.weights["w_raw"], init=prev.get(method), **kw)
    elif method == "cpr_l0":
        s, it = sc.weighted_pagerank(t.src, t.dst, t.weights["w_raw"], init=prev.get(method), **kw)
    elif method in COUPLED_LAMBDA:
        lam = COUPLED_LAMBDA[method]
        s, it = sc.coupled_pagerank([(a.src, a.dst, a.weights["w_raw"], lam),
                                     (t.src, t.dst, t.weights["w_raw"], 1.0 - lam)], init=prev.get(method), **kw)
    elif method == "spr":
        l100, it1 = sc.weighted_pagerank(a.src, a.dst, a.weights["w_raw"], init=prev.get("cpr_l100"), **kw)
        if l100.empty:
            l100 = restart_vector(nodes)
        s, it2 = sc.weighted_pagerank(t.src, t.dst, t.weights["w_raw"], teleport=l100, init=prev.get("spr"), **kw)
        if s.empty:   # no positive transfer edge: every node dangles, so S-PR is its restart vector
            s = restart_vector(nodes, l100)
        return s, it1 + it2, 2, {"cpr_l100": l100, "spr": s}
    else:
        raise ValueError(f"not a walk: {method}")
    if s.empty:
        s = restart_vector(nodes, restart)
    return s, it, 1, {method: s}


def restart_vector(nodes: Any, teleport: pd.Series | None = None) -> pd.Series:
    """The restart distribution of a walk over ``nodes``, as scoring.py builds it (``teleport`` normalised there,
    uniform when it is None, empty or of zero mass): the scores of a walk whose every node dangles."""
    sc = _scoring()
    ids = np.unique(np.asarray(nodes, dtype=np.int64))
    return sc._scores(ids, sc._teleport_vector(ids, teleport))


def full_scores(graph: CrawlGraph, method: str, params: dict[str, Any]) -> np.ndarray:
    """A walk on the whole of ``graph`` with every node in its node set, as a vector over node ids."""
    s, _, _, _ = walk(method, graph.allow, graph.transfer, np.arange(graph.n), params)
    return dense(s, graph.n)


def dense(scores: pd.Series, n: int) -> np.ndarray:
    """A score Series indexed by node id as a vector over 0..n-1 (0 where it has no value)."""
    out = np.zeros(n, dtype=np.float64)
    if len(scores):
        out[scores.index.to_numpy(dtype=np.int64)] = scores.to_numpy(dtype=np.float64)
    return out


# ---------------------------------------------------------------------------
# Crawl


def _csr(keys: np.ndarray, n: int) -> tuple[np.ndarray, np.ndarray]:
    """(row pointer, positions sorted by key) of a CSR on ``keys``."""
    order = np.argsort(keys, kind="stable")
    ptr = np.zeros(n + 1, dtype=np.int64)
    np.cumsum(np.bincount(keys, minlength=n), out=ptr[1:])
    return ptr, order


def _gather(ptr: np.ndarray, rows: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """CSR positions of the entries of ``rows`` in row order, and the index in ``rows`` of each."""
    starts = ptr[rows]
    lens = ptr[rows + 1] - starts
    total = int(lens.sum())
    if total == 0:
        return np.empty(0, dtype=np.int64), np.empty(0, dtype=np.int64)
    owner = np.repeat(np.arange(rows.size, dtype=np.int64), lens)
    offsets = np.cumsum(lens) - lens
    return np.arange(total, dtype=np.int64) - offsets[owner] + starts[owner], owner


@dataclass
class Adjacency:
    """CSR views of a CrawlGraph: out-edges of every node per layer and in the union pattern, and the
    in-edges for the both mode."""

    mode: str
    out: dict[str, tuple[np.ndarray, np.ndarray]]          # layer -> (ptr, edge index by src)
    inn: dict[str, tuple[np.ndarray, np.ndarray]] | None   # layer -> (ptr, edge index by dst)
    u_out: tuple[np.ndarray, np.ndarray]                   # (ptr, dst) of the union pattern
    u_in: tuple[np.ndarray, np.ndarray] | None             # (ptr, src) of the union pattern

    @classmethod
    def build(cls, graph: CrawlGraph, mode: str) -> Adjacency:
        if mode not in MODES:
            raise ValueError(f"mode must be one of {MODES}")
        n = graph.n
        layers = {"allow": graph.allow, "transfer": graph.transfer}
        out = {k: _csr(v.src, n) for k, v in layers.items()}
        u_ptr, _ = _csr(graph.union_src, n)  # the union pairs are sorted by (src, dst)
        inn = u_in = None
        if mode == "both":
            inn = {k: _csr(v.dst, n) for k, v in layers.items()}
            ptr, order = _csr(graph.union_dst, n)
            u_in = (ptr, graph.union_src[order])
        return cls(mode, out, inn, (u_ptr, graph.union_dst), u_in)


@dataclass
class CrawlResult:
    ordering: str
    seed: int
    mode: str
    rho: str
    visit_index: np.ndarray   # visit number of every node, 0 if never visited
    visits: int
    recomputes: int
    batch_sizes: np.ndarray   # visits made after each recompute
    iterations: int           # solver iterations over all recomputes
    solves: int
    tied: int                 # picks decided by a tie
    edges_read: np.ndarray    # union edges first read at each visit (index V - 1)
    seconds: float


class Crawl:
    """One crawl of ``graph`` from ``seed`` with one ordering, reveal mode and rho (protocol section 4).

    The seed is visit 1. pick() recomputes the ordering after V visits and returns the b(V) highest-
    scored frontier contracts (fewer if the frontier is shorter; one uniform choice for the random
    ordering); visit() reads a batch in order. The seen graph S is the visited and frontier contracts
    with the revealed pairs; a walk ordering runs its scoring.py method on S, warm-started from its
    previous vector. run() repeats pick and visit until the frontier is empty.
    """

    def __init__(self, graph: CrawlGraph, seed: int, ordering: str, *, mode: str = "out", rho: Any,
                 cfg: dict[str, Any], params: dict[str, Any] | None = None,
                 adjacency: Adjacency | None = None):
        if ordering not in ORDERINGS:
            raise ValueError(f"ordering must be one of {ORDERINGS}")
        if ordering in WALKS and params is None:
            raise ValueError("a walk ordering needs the solver parameters")
        self.graph, self.n, self.seed, self.ordering, self.mode = graph, graph.n, int(seed), ordering, mode
        self.rho = decimal(rho)
        self.params = params
        self.tol = float(cfg["tie_tolerance"])
        self.adj = adjacency if adjacency is not None else Adjacency.build(graph, mode)
        if self.adj.mode != mode and not (mode == "out" and self.adj.mode == "both"):
            raise ValueError(f"the adjacency was built for the {self.adj.mode} mode")
        n = self.n
        self.visit_index = np.zeros(n, dtype=np.int64)
        self.disc = np.full(n, -1, dtype=np.int64)
        self.known = np.zeros(n, dtype=bool)
        self._tb = np.zeros(n, dtype=np.int64)  # visit number of each contract of the batch being read
        self.counts = {k: np.zeros(n, dtype=np.int64) for k in COUNTS}
        self.delta = np.zeros(n, dtype=np.float64)
        self._rows = self._delta_rows(float(cfg["lambda_primary"]))
        self.edges_read = np.zeros(max(n, 1), dtype=np.int64)
        layers = {"allow": graph.allow, "transfer": graph.transfer}
        self._buf = {k: {"src": np.empty(v.size, np.int64), "dst": np.empty(v.size, np.int64),
                         **{w: np.empty(v.size, np.float64) for w in v.weights}} for k, v in layers.items()}
        self._len = {k: 0 for k in layers}
        self.V = 0
        self.recomputes = 0
        self.batch_sizes: list[int] = []
        self.iterations = 0
        self.solves = 0
        self.tied = 0
        self.prev: dict[str, pd.Series] = {}
        seed_hex = str(graph.address[self.seed])
        self._sha_rank = sha_ranks(graph.address, seed_hex) if ordering == "bfs" else None
        self._rng = random_generator(cfg["random_salt"], seed_hex) if ordering == "random" else None
        # The frontier of the random ordering as a list, and the position of each contract in it (-1: not in it).
        self._pool: list[int] = []
        self._slot = np.full(n, -1, dtype=np.int64) if ordering == "random" else None
        self.known[self.seed] = True
        self.disc[self.seed] = 0
        self.visit(np.array([self.seed]))

    # -- revealing

    def _delta_rows(self, lam: float) -> dict[str, np.ndarray]:
        """delta' terms of every out-edge, in CSR order: the C-PR(lambda) transition probability."""
        n = self.n
        layers = {"allow": self.graph.allow, "transfer": self.graph.transfer}
        strength = {}
        for k, layer in layers.items():
            w = layer.weights["w_raw"]
            pos = w > 0
            strength[k] = np.bincount(layer.src[pos], weights=w[pos], minlength=n)
        has_a = (strength["allow"] > 0).astype(np.float64)
        has_t = (strength["transfer"] > 0).astype(np.float64)
        denom = lam * has_a + (1.0 - lam) * has_t
        mix = {"allow": lam * has_a, "transfer": (1.0 - lam) * has_t}
        rows = {}
        for k, layer in layers.items():
            w = layer.weights["w_raw"]
            s = layer.src
            with np.errstate(divide="ignore", invalid="ignore"):
                val = np.where((w > 0) & (denom[s] > 0), mix[k][s] / denom[s] * w / strength[k][s], 0.0)
            rows[k] = val[self.adj.out[k][1]]
        return rows

    def _append(self, name: str, layer: Layer, e: np.ndarray) -> None:
        start = self._len[name]
        end = start + e.size
        buf = self._buf[name]
        buf["src"][start:end] = layer.src[e]
        buf["dst"][start:end] = layer.dst[e]
        for w, v in layer.weights.items():
            buf[w][start:end] = v[e]
        self._len[name] = end

    def visit(self, batch: Any) -> None:
        """Read ``batch`` in order: reveal its pairs, discover new contracts, update the counts."""
        batch = np.asarray(batch, dtype=np.int64).ravel()
        k = batch.size
        if k == 0:
            return
        if (np.unique(batch).size != k or not self.known[batch].all() or (self.visit_index[batch] > 0).any()):
            raise ValueError("a batch holds known contracts not yet visited, each once")
        times = self.V + 1 + np.arange(k, dtype=np.int64)
        tb = self._tb
        tb[batch] = times
        both = self.mode == "both"
        g = self.graph
        for name, layer in (("allow", g.allow), ("transfer", g.transfer)):
            ptr, order = self.adj.out[name]
            pos, owner = _gather(ptr, batch)
            e = order[pos]
            dst = layer.dst[e]
            # The counts and delta' use every out-edge of a visited contract.
            if name == "allow":
                np.add.at(self.counts["ib_a"], dst, 1)
            else:
                other = dst != batch[owner]
                np.add.at(self.counts["ib_t"], dst[other], 1)
            np.add.at(self.delta, dst, self._rows[name][pos])
            if both:
                # An edge to a contract visited earlier was revealed at that visit.
                e = e[self.visit_index[dst] == 0]
                iptr, iorder = self.adj.inn[name]
                ipos, _ = _gather(iptr, batch)
                ie = iorder[ipos]
                s = layer.src[ie]
                e = np.concatenate([e, ie[(self.visit_index[s] == 0) & (tb[s] == 0)]])
            self._append(name, layer, e)

        uptr, udst = self.adj.u_out
        pos, owner = _gather(uptr, batch)
        nbr, t_nbr = udst[pos], times[owner]
        np.add.at(self.counts["ib_u"], nbr, 1)
        if both:
            keep = self.visit_index[nbr] == 0
            nbr, t_nbr = nbr[keep], t_nbr[keep]
            # An edge between two contracts of the batch is read at the earlier of the two visits.
            t_read = np.where(tb[nbr] > 0, np.minimum(t_nbr, tb[nbr]), t_nbr)
            iptr, isrc = self.adj.u_in
            ipos, iowner = _gather(iptr, batch)
            src = isrc[ipos]
            ikeep = (self.visit_index[src] == 0) & (tb[src] == 0)
            src, t_src = src[ikeep], times[iowner[ikeep]]
            found = np.concatenate([nbr, src])
            t_found = np.concatenate([t_nbr, t_src])
            t_read = np.concatenate([t_read, t_src])
        else:
            found, t_found, t_read = nbr, t_nbr, t_nbr
        np.add.at(self.edges_read, t_read - 1, 1)
        if self._slot is not None:
            self._leave_pool(batch)
        new = ~self.known[found]
        if new.any():
            f, t = found[new], t_found[new]
            order = np.lexsort((t, f))
            f, t = f[order], t[order]
            first = np.ones(f.size, dtype=bool)
            first[1:] = f[1:] != f[:-1]
            self.known[f[first]] = True
            self.disc[f[first]] = t[first]
            if self._slot is not None:
                f, t = f[first], t[first]
                self._join_pool(f[np.lexsort((f, t))])  # by discovery index, then node id
        self.visit_index[batch] = times
        tb[batch] = 0
        self.V += k

    def _join_pool(self, contracts: np.ndarray) -> None:
        """Append newly discovered contracts to the frontier list of the random ordering."""
        start = len(self._pool)
        self._pool.extend(contracts.tolist())
        self._slot[contracts] = np.arange(start, len(self._pool))

    def _leave_pool(self, batch: np.ndarray) -> None:
        """Take visited contracts out of the frontier list: each is replaced by the last contract of the list."""
        for c in batch.tolist():
            j = int(self._slot[c])
            if j < 0:  # the seed, never in the list
                continue
            last = self._pool.pop()
            if last != c:
                self._pool[j] = last
                self._slot[last] = j
            self._slot[c] = -1

    # -- the seen graph

    def frontier(self) -> np.ndarray:
        return np.flatnonzero(self.known & (self.visit_index == 0))

    def seen(self) -> tuple[Layer, Layer]:
        """The revealed pairs of each layer with their full-graph weights."""
        out = []
        for name in ("allow", "transfer"):
            m = self._len[name]
            buf = self._buf[name]
            out.append(Layer(buf["src"][:m], buf["dst"][:m], {w: v[:m] for w, v in buf.items()
                                                              if w not in ("src", "dst")}))
        return out[0], out[1]

    def walk_scores(self, method: str | None = None, warm: bool = True) -> pd.Series:
        """A walk on the seen graph, with the visited and frontier contracts as its node set."""
        method = method or self.ordering
        allow, transfer = self.seen()
        s, it, solves, prev = walk(method, allow, transfer, np.flatnonzero(self.known), self.params,
                                   self.prev if warm else None)
        if warm and method == self.ordering:
            self.prev = prev
            self.iterations += it
            self.solves += solves
        return s

    def final_scores(self) -> pd.Series | None:
        """The walk on the complete seen graph from a cold start (for the invariant check)."""
        if self.ordering not in WALKS:
            return None
        return self.walk_scores(warm=False)

    def frontier_scores(self, frontier: np.ndarray) -> np.ndarray:
        o = self.ordering
        if o in COUNTS:
            return self.counts[o][frontier].astype(np.float64)
        if o == DIAGNOSTIC:
            return self.delta[frontier]
        if o in WALKS:
            return dense(self.walk_scores(), self.n)[frontier]
        raise ValueError(f"{o} has no frontier scores")

    # -- choosing

    def pick(self) -> np.ndarray:
        """Recompute the ordering and return the next batch (empty when the frontier is)."""
        if self.ordering == "random":
            # One uniform choice among the frontier contracts per visit: the visit order depends on the seed
            # only, not on rho (protocol section 4).
            if not self._pool:
                return np.empty(0, dtype=np.int64)
            self.recomputes += 1
            self.batch_sizes.append(1)
            return np.array([self._pool[int(self._rng.integers(len(self._pool)))]], dtype=np.int64)
        frontier = self.frontier()
        if frontier.size == 0:
            return frontier
        k = min(batch_size(self.rho, self.V), frontier.size)
        self.recomputes += 1
        self.batch_sizes.append(k)
        if self.ordering == "bfs":
            key = self.disc[frontier] * self.n + self._sha_rank[frontier]
            part = np.argpartition(key, k - 1)[:k] if k < frontier.size else np.arange(frontier.size)
            return frontier[part[np.argsort(key[part])]]
        picks, tied = select_top(frontier, self.frontier_scores(frontier), self.disc[frontier], k, self.tol)
        self.tied += tied
        return picks

    def run(self, max_visits: int | None = None) -> CrawlResult:
        start = time.perf_counter()
        while max_visits is None or self.V < max_visits:
            picks = self.pick()
            if picks.size == 0:
                break
            if max_visits is not None and picks.size > max_visits - self.V:
                picks = picks[: max_visits - self.V]
                self.batch_sizes[-1] = picks.size
            self.visit(picks)
        return CrawlResult(
            self.ordering, self.seed, self.mode, str(self.rho), self.visit_index.copy(), self.V,
            self.recomputes, np.asarray(self.batch_sizes, dtype=np.int64), self.iterations, self.solves,
            self.tied, self.edges_read[: self.V].copy(), time.perf_counter() - start)


def select_top(frontier: np.ndarray, scores: np.ndarray, disc: np.ndarray, k: int,
               tie_tolerance: float) -> tuple[np.ndarray, int]:
    """The k frontier contracts ranked first, in order, and how many of them a tie decided.

    Groups are cut in decreasing score: each starts at its highest score and holds the scores within
    tie_tolerance x the frontier maximum of it; inside a group the earlier discovery index and then
    the lower node id go first. ``scores`` and ``disc`` are aligned with ``frontier``.
    """
    m = frontier.size
    k = min(int(k), m)
    if k <= 0:
        return np.empty(0, dtype=np.int64), 0
    s = np.asarray(scores, dtype=np.float64)
    top = float(s.max())
    tol = tie_tolerance * top if top > 0 else 0.0
    if k < m:
        kth = np.partition(s, m - k)[m - k]
        cand = np.flatnonzero(s >= kth - tol)
    else:
        cand = np.arange(m)
    f, sc, dd = frontier[cand], s[cand], disc[cand]
    order = np.lexsort((f, dd, -sc))
    f, sc, dd = f[order], sc[order], dd[order]
    neg = -sc
    picks, tied, taken, i = [], 0, 0, 0
    while taken < k:
        j = int(np.searchsorted(neg, tol - sc[i], side="right"))
        members = f[i:j]
        if members.size > 1:
            members = members[np.lexsort((members, dd[i:j]))]
        take = min(k - taken, members.size)
        picks.append(members[:take])
        if members.size > 1:
            tied += take
        taken += take
        i = j
    return np.concatenate(picks), tied


# ---------------------------------------------------------------------------
# Measures (protocol section 6)


def hot_set(values: Any, q: Any) -> np.ndarray:
    """H_q(I) as a mask: I >= the ceil(q n)-th largest value and I > 0 (ties at it included)."""
    v = np.asarray(values, dtype=np.float64).ravel()
    n = v.size
    k = ceil_share(q, n)
    if n == 0 or k == 0:
        return np.zeros(n, dtype=bool)
    g = np.partition(v, n - k)[n - k]
    return (v >= g) & (v > 0)


def rank_order(values: Any, first: np.ndarray | None = None) -> np.ndarray:
    """Position 1..n of each node by decreasing value, ties to the lower node id; nodes in the
    mask ``first`` come before the others."""
    v = np.asarray(values, dtype=np.float64).ravel()
    keys = [np.arange(v.size), -v]
    if first is not None:
        keys.append(~np.asarray(first, dtype=bool))
    order = np.lexsort(keys)
    pos = np.empty(v.size, dtype=np.int64)
    pos[order] = np.arange(1, v.size + 1)
    return pos


def ideal_order(values: Any, hot: np.ndarray) -> np.ndarray:
    """Visit index of the ideal reference: the hot contracts first, by decreasing importance."""
    return rank_order(values, first=hot)


def hubs(ib_u: Any, cfg: dict[str, Any]) -> np.ndarray:
    """The max(min, ceil(share |U|)) contracts with the highest IB_U, ties to the lower id, in rank order."""
    v = np.asarray(ib_u, dtype=np.float64).ravel()
    k = max(int(cfg["hub_drop"]["min"]), ceil_share(cfg["hub_drop"]["share"], v.size))
    return np.lexsort((np.arange(v.size), -v))[:k]


def without_hubs(hot_ids: Any, hub_ids: Any) -> np.ndarray:
    """The no-hubs variant of a hot set: its contracts other than the hubs (which stay in the graph)."""
    return np.setdiff1d(np.asarray(hot_ids, dtype=np.int64), np.asarray(hub_ids, dtype=np.int64))


def curve_grid(n: int, points: int) -> np.ndarray:
    """At most ``points`` values of K from 1 to n (all of them when n <= points)."""
    if n <= points:
        return np.arange(1, n + 1, dtype=np.int64)
    return np.unique(np.rint(np.linspace(1, n, points)).astype(np.int64))


def _visits(visit_index: np.ndarray) -> np.ndarray:
    v = np.atleast_2d(np.asarray(visit_index, dtype=np.int64))
    return np.where(v > 0, v, np.iinfo(np.int64).max)  # never visited: after every K


def p_st(t_hot: Any, grid: np.ndarray) -> np.ndarray:
    """P_ST(K) = |H n V_K| / |H| for each row (seed) of the visit indices of the hot contracts."""
    t = _visits(t_hot)
    if t.shape[1] == 0:
        return np.full((t.shape[0], grid.size), np.nan)
    t = np.sort(t, axis=1)
    return np.vstack([np.searchsorted(row, grid, side="right") for row in t]) / t.shape[1]


def p_cs(visit_index: Any, rank: np.ndarray, grid: np.ndarray) -> np.ndarray:
    """P_CS(K) = |V_K n R_K| / K, R_K the K contracts ranked first (``rank`` from rank_order)."""
    v = _visits(visit_index)
    rows = [np.searchsorted(np.sort(np.maximum(row, rank)), grid, side="right") for row in v]
    return np.vstack(rows) / grid


def captured(visit_index: Any, values: Any, grid: np.ndarray) -> np.ndarray:
    """Cumulative captured importance: the share of the total held by the contracts visited by K."""
    v = _visits(visit_index)
    x = np.asarray(values, dtype=np.float64).ravel()
    total = x.sum()
    if not total > 0:
        return np.full((v.shape[0], grid.size), np.nan)
    rows = [np.cumsum(x[np.argsort(row, kind="stable")])[grid - 1] / total for row in v]
    return np.vstack(rows)


def horizon(x: Any, n: int) -> int:
    """ceil(x |U|), the number of visits up to which AUC_x is taken."""
    return ceil_share(x, n)


def visit_scores(t_hot: Any, n: int, x: Any) -> np.ndarray:
    """g_x(h) = max(0, 1 - t_h / ceil(x |U|)) for each seed (row) and hot contract (column)."""
    t = np.atleast_2d(np.asarray(t_hot, dtype=np.float64))
    t = np.where(t > 0, t, np.inf)
    return np.maximum(0.0, 1.0 - t / horizon(x, n))


def auc(t_hot: Any, n: int, x: Any) -> float:
    """AUC_x: the mean over hot contracts of g_x averaged over seeds."""
    g = visit_scores(t_hot, n, x)
    return float(g.mean()) if g.size else float("nan")


def visits_to_reach(t_hot: Any, share: Any) -> np.ndarray:
    """Per seed, the visits needed to reach ``share`` of the hot contracts."""
    t = np.sort(_visits(t_hot), axis=1)
    if t.shape[1] == 0:
        return np.zeros(t.shape[0], dtype=np.int64)
    return t[:, max(ceil_share(share, t.shape[1]), 1) - 1]


def ideal_curve(grid: np.ndarray, n_hot: int) -> np.ndarray:
    return np.minimum(1.0, grid / max(n_hot, 1))


def random_curve(grid: np.ndarray, n: int) -> np.ndarray:
    return grid / n


def ideal_auc(n_hot: int, n: int, x: Any) -> float:
    """AUC_x of the ideal order: the hot contracts at visits 1..|H|."""
    return auc(np.arange(1, n_hot + 1), n, x) if n_hot else float("nan")


def random_auc(n: int, x: Any) -> float:
    """AUC_x of the random curve K / |U|: the mean of g_x over a visit index uniform on 1..|U|,
    (X - 1) / (2 |U|) with X = ceil(x |U|) <= |U|."""
    big_x = horizon(x, n)
    t = np.arange(1, min(big_x, n) + 1, dtype=np.float64)
    return float((1.0 - t / big_x).sum() / n)
