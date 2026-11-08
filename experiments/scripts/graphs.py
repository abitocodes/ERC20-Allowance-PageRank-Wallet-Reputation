"""Load the downloaded pair tables and compute every score of the study at one anchor.

Method ids (as in the result summaries and tables):
  endorserank           EndorseRank: allowance pairs, weight sigma*V, uniform restarts
  endorserank_activity  EndorseRank with AWP's activity restarts (owners' approving activity)
  awp                   AWP: transfer pairs, weight sigma*V, restarts by sending activity
  cpr_l100, cpr_l0      C-PR at lambda = 1 and 0: one raw-amount layer walked alone
  cpr_l25, cpr_l50, cpr_l75   C-PR at lambda = 0.25, 0.5 (primary), 0.75
  spr                   S-PR: raw transfer layer restarted from cpr_l100

The union graph of docs/discovery_protocol.md section 2 gives the union in-degree baseline and the
coverage of the contract-graph variant; load_graphs reads its uncapped allowance layer for the
sensitivity of docs/revision_contract_graph.md section 5.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from common import CONTRACT_GRAPH, GRAPH, load_config, read_parts
from scoring import activeness, coupled_pagerank, pagerank_params, seeded_pagerank, weighted_pagerank

EXPORT = GRAPH

METHOD_LABELS = {
    "endorserank": "EndorseRank",
    "endorserank_activity": "EndorseRank (activity restarts)",
    "awp": "AWP",
    "cpr_l100": r"C-PR ($\lambda=1$)",
    "cpr_l0": r"C-PR ($\lambda=0$)",
    "cpr_l25": r"C-PR ($\lambda=0.25$)",
    "cpr_l50": r"C-PR ($\lambda=0.5$)",
    "cpr_l75": r"C-PR ($\lambda=0.75$)",
    "spr": "S-PR",
}
COUPLED = {"cpr_l25": 0.25, "cpr_l50": 0.5, "cpr_l75": 0.75}


@dataclass
class Graphs:
    tag: str
    allow: pd.DataFrame      # src, dst, n_tokens, w_er, w_raw, max_sig, last_ts
    transfer: pd.DataFrame   # src, dst, n_transfers, w_awp, w_raw, max_sig, sum_value, first_ts, last_ts


def load_nodes() -> pd.DataFrame:
    return read_parts(EXPORT / "nodes")


ALLOW_STEMS = ("allow_pairs", "allow_pairs_uncapped")   # the capped allowance layer; the uncapped one (contract12m)


def load_graphs(tag: str, allow_stem: str = "allow_pairs") -> Graphs:
    """The allowance and transfer pairs of the freeze ``tag``; ``allow_stem`` 'allow_pairs_uncapped' takes the
    uncapped allowance layer of the contract-graph variant (docs/revision_contract_graph.md section 5) beside the
    same transfer layer."""
    if allow_stem not in ALLOW_STEMS:
        raise ValueError(f"allow_stem must be one of {ALLOW_STEMS}")
    allow = read_parts(EXPORT / f"{allow_stem}_{tag}")
    transfer = read_parts(EXPORT / f"transfer_pairs_{tag}")
    return Graphs(tag, allow, transfer)


def restrict(g: Graphs, wallet_ids: np.ndarray) -> Graphs:
    """Keep the edges with at least one end point among ``wallet_ids``."""
    keep = np.asarray(wallet_ids, dtype=np.int64)
    a = g.allow[g.allow["src"].isin(keep) | g.allow["dst"].isin(keep)]
    t = g.transfer[g.transfer["src"].isin(keep) | g.transfer["dst"].isin(keep)]
    return Graphs(g.tag, a.reset_index(drop=True), t.reset_index(drop=True))


def score_all(g: Graphs, params: dict | None = None, methods: tuple[str, ...] | None = None,
              isolated: np.ndarray | None = None) -> tuple[dict[str, pd.Series], dict[str, int]]:
    """Full score vectors (indexed by node id) and iteration counts.

    ``isolated``: wallet ids added as isolated nodes to every graph a wallet is
    missing from, the single-layer ones and the coupled one (the sensitivity rule;
    docs/revision_contract_graph.md section 11), but not S-PR's; by default a
    wallet outside a graph is simply absent. The contract-graph variant keeps the
    pairs of weight 0, which the walks drop (scoring._positive_edges), so there a
    wallet is missing from a walk's graph unless it ends a pair of positive weight
    in that walk's layers and weight columns.
    """
    p = params or pagerank_params(load_config())
    want = set(methods or METHOD_LABELS)
    a, t = g.allow, g.transfer
    out: dict[str, pd.Series] = {}
    its: dict[str, int] = {}

    def extra(src, dst):
        if isolated is None:
            return None
        if CONTRACT_GRAPH:
            # Every wallet is passed: a walk's nodes are the ends of its positive-weight pairs plus extra_nodes, each
            # once (scoring._local_index), so it adds as isolated nodes exactly the wallets that end no such pair,
            # those that end only pairs of weight 0 included.
            return np.unique(np.asarray(isolated, dtype=np.int64))
        present = np.union1d(src, dst)
        return np.setdiff1d(np.asarray(isolated, dtype=np.int64), present)

    if "endorserank" in want:
        out["endorserank"], its["endorserank"] = weighted_pagerank(
            a["src"], a["dst"], a["w_er"], extra_nodes=extra(a["src"], a["dst"]), **p)
    if "endorserank_activity" in want:
        act = activeness(a["src"], a["dst"], a["max_sig"])
        out["endorserank_activity"], its["endorserank_activity"] = weighted_pagerank(
            a["src"], a["dst"], a["w_er"], teleport=act, extra_nodes=extra(a["src"], a["dst"]), **p)
    if "awp" in want:
        act = activeness(t["src"], t["dst"], t["max_sig"])
        out["awp"], its["awp"] = weighted_pagerank(
            t["src"], t["dst"], t["w_awp"], teleport=act, extra_nodes=extra(t["src"], t["dst"]), **p)
    need_l100 = want & {"cpr_l100", "spr"}
    if need_l100:
        out["cpr_l100"], its["cpr_l100"] = weighted_pagerank(
            a["src"], a["dst"], a["w_raw"], extra_nodes=extra(a["src"], a["dst"]), **p)
    if "cpr_l0" in want:
        out["cpr_l0"], its["cpr_l0"] = weighted_pagerank(
            t["src"], t["dst"], t["w_raw"], extra_nodes=extra(t["src"], t["dst"]), **p)
    coupled_extra = None  # the isolated wallets outside both layers, computed only when there are any
    if isolated is not None and want & set(COUPLED):
        coupled_extra = extra(np.concatenate([a["src"], t["src"]]), np.concatenate([a["dst"], t["dst"]]))
    for mid, lam in COUPLED.items():
        if mid in want:
            out[mid], its[mid] = coupled_pagerank(
                [(a["src"], a["dst"], a["w_raw"], lam), (t["src"], t["dst"], t["w_raw"], 1.0 - lam)],
                extra_nodes=coupled_extra, **p)
    if "spr" in want:
        out["spr"], its["spr"] = seeded_pagerank(t["src"], t["dst"], t["w_raw"], out["cpr_l100"], **p)
        its["spr"] += its["cpr_l100"]
    if "cpr_l100" not in want:
        out.pop("cpr_l100", None)
        its.pop("cpr_l100", None)
    return out, its


def raw_degrees(g: Graphs, wallet_ids: np.ndarray) -> pd.DataFrame:
    """In-approve degree, in-approve value, and transfer in-degree without self-transfers."""
    w = pd.Index(np.asarray(wallet_ids, dtype=np.int64))
    a, t = g.allow, g.transfer
    ina = a.groupby("dst").agg(in_approve_degree=("src", "nunique"), in_approve_value=("w_raw", "sum"))
    t_other = t[t["src"] != t["dst"]]
    ind = t_other.groupby("dst")["src"].nunique().rename("in_degree_other")
    out = pd.DataFrame(index=w)
    out = out.join(ina).join(ind).fillna(0.0)
    return out


def union_pairs(g: Graphs) -> tuple[np.ndarray, np.ndarray]:
    """The union graph of docs/discovery_protocol.md section 2 on node ids: the distinct pairs (src, dst), src != dst,
    with a pair in either layer whatever its weights, in increasing (src, dst) order (crawl.CrawlGraph builds the same
    on positions, crawl.py:177-181)."""
    src = np.concatenate([g.allow["src"].to_numpy(np.int64), g.transfer["src"].to_numpy(np.int64)])
    dst = np.concatenate([g.allow["dst"].to_numpy(np.int64), g.transfer["dst"].to_numpy(np.int64)])
    keep = src != dst
    if not keep.any():
        empty = np.empty(0, np.int64)
        return empty, empty
    n = int(max(src.max(), dst.max())) + 1
    key = np.unique(src[keep] * n + dst[keep])
    return key // n, key % n


def union_sizes(union: tuple[np.ndarray, np.ndarray]) -> dict:
    """The numbers of pairs and of nodes (ends of a pair) of a union graph from union_pairs."""
    src, dst = union
    return {"pairs": int(src.size), "nodes": int(np.union1d(src, dst).size)}


def union_in_degree(g: Graphs, ids: np.ndarray, union=None) -> pd.Series:
    """IB_U of docs/discovery_protocol.md section 5 counted on G (revision section 9): for each id, the distinct
    contracts other than itself with a pair to it in either layer; 0 for an id without one."""
    _, dst = union if union is not None else union_pairs(g)
    d, c = np.unique(dst, return_counts=True)
    idx = pd.Index(np.asarray(ids, dtype=np.int64))
    return pd.Series(c, index=d, dtype=np.int64).reindex(idx, fill_value=0).rename("in_degree_union")


def in_union_graph(g: Graphs, ids: np.ndarray, union=None) -> np.ndarray:
    """Whether each id is an end of a union pair (a member with self-pairs only is outside)."""
    src, dst = union if union is not None else union_pairs(g)
    return np.isin(np.asarray(ids, dtype=np.int64), np.union1d(src, dst))


def member_coverage(g: Graphs, ids: np.ndarray, union=None) -> dict:
    """The members of a cohort by where they lie in the contract graph of the freeze: an end of an allowance pair, of a
    transfer pair (self-pairs included), of both, of a union pair, of self-pairs only, or of no pair at all
    (docs/revision_contract_graph.md section 8)."""
    ids = np.asarray(ids, dtype=np.int64)
    n = int(ids.size)
    in_a = np.isin(ids, np.union1d(g.allow["src"].to_numpy(np.int64), g.allow["dst"].to_numpy(np.int64)))
    in_t = np.isin(ids, np.union1d(g.transfer["src"].to_numpy(np.int64), g.transfer["dst"].to_numpy(np.int64)))
    in_u = in_union_graph(g, ids, union)
    any_pair = in_a | in_t

    def part(mask: np.ndarray) -> dict:
        k = int(mask.sum())
        return {"n": k, "share": (k / n) if n else None}

    return {"n": n, "allowance_layer": part(in_a), "transfer_layer": part(in_t), "both_layers": part(in_a & in_t),
            "union_graph": part(in_u), "self_pairs_only": part(any_pair & ~in_u),
            "outside_contract_graph": part(~any_pair)}
