"""Load the downloaded pair tables and compute every score of the study at one anchor.

Method ids (as in the result summaries and tables):
  endorserank           EndorseRank: allowance pairs, weight sigma*V, uniform restarts
  endorserank_activity  EndorseRank with AWP's activity restarts (owners' approving activity)
  awp                   AWP: transfer pairs, weight sigma*V, restarts by sending activity
  cpr_l100, cpr_l0      C-PR at lambda = 1 and 0: one raw-amount layer walked alone
  cpr_l25, cpr_l50, cpr_l75   C-PR at lambda = 0.25, 0.5 (primary), 0.75
  spr                   S-PR: raw transfer layer restarted from cpr_l100
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from common import GRAPH, load_config, read_parts
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


def load_graphs(tag: str) -> Graphs:
    allow = read_parts(EXPORT / f"allow_pairs_{tag}")
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

    ``isolated``: wallet ids added to every single-layer graph as isolated nodes
    (the sensitivity rule); by default a wallet outside a graph is simply absent.
    """
    p = params or pagerank_params(load_config())
    want = set(methods or METHOD_LABELS)
    a, t = g.allow, g.transfer
    out: dict[str, pd.Series] = {}
    its: dict[str, int] = {}

    def extra(src, dst):
        if isolated is None:
            return None
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
    for mid, lam in COUPLED.items():
        if mid in want:
            out[mid], its[mid] = coupled_pagerank(
                [(a["src"], a["dst"], a["w_raw"], lam), (t["src"], t["dst"], t["w_raw"], 1.0 - lam)], **p)
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
