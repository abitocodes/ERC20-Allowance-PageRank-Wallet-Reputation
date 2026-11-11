"""Closed groups of contracts in the graphs of the contract-graph analysis (post hoc data check, decides no rule).

Question: do the graphs of the main analysis (CONTRACT_REP_VARIANT=contract12m) hold groups of contracts whose
out-edges all stay inside the group, the structure in which a PageRank walk keeps the mass that reaches it (a rank
sink; the link farms of Gyongyi and Garcia-Molina, 2005, are such groups)? If such groups held much of a walk's
mass, or many of the contracts the study ranks, the sample would be shaped by them.

For each freeze (tobs, t1) and each walk (EndorseRank, C-PR lambda=1, AWP, C-PR lambda=0, C-PR lambda=0.5), the
graph is the walk's own: the pairs of positive weight in its layers, self-pairs included (the walks keep them).
A closed group is a strongly connected component with at least one edge inside it (two or more contracts, or one
contract with a pair to itself) and no edge from it to a contract outside it. "Isolated" closed groups also receive
no edge from outside (the closed farm of the cost model). The script reports their number and size, the share of
the walk's stationary mass they hold (score vectors from graphs.score_all with the pipeline's parameters), and how
many members of the freeze's cohort and spender set lie in them.

Run from experiments/:  CONTRACT_REP_VARIANT=contract12m python -I -X utf8 exploratory/2026-11-11-closed-groups/scripts/closed_groups.py
Writes exploratory/2026-11-11-closed-groups/results.json.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components

HERE = Path(__file__).resolve().parent
EXP = HERE.parents[2]
sys.path.insert(0, str(EXP / "scripts"))

if os.environ.get("CONTRACT_REP_VARIANT") != "contract12m":
    raise SystemExit("set CONTRACT_REP_VARIANT=contract12m")

from common import ROOT, load_config  # noqa: E402
from graphs import load_graphs, load_nodes, score_all  # noqa: E402
from labels import contract_members  # noqa: E402
from scoring import pagerank_params  # noqa: E402

OUT = HERE.parent / "results.json"
MEMBERS = {"tobs": ("cohort_tobs", "spenders_w1"), "t1": ("cohort_t1", "spenders_w0")}
WALKS = ("endorserank", "cpr_l100", "awp", "cpr_l0", "cpr_l50")


def walk_edges(g, walk: str) -> tuple[np.ndarray, np.ndarray]:
    a, t = g.allow, g.transfer
    if walk == "endorserank":
        parts = [a[a["w_er"] > 0]]
    elif walk == "cpr_l100":
        parts = [a[a["w_raw"] > 0]]
    elif walk == "awp":
        parts = [t[t["w_awp"] > 0]]
    elif walk == "cpr_l0":
        parts = [t[t["w_raw"] > 0]]
    elif walk == "cpr_l50":
        parts = [a[a["w_raw"] > 0], t[t["w_raw"] > 0]]
    else:
        raise ValueError(walk)
    src = np.concatenate([p["src"].to_numpy(np.int64) for p in parts])
    dst = np.concatenate([p["dst"].to_numpy(np.int64) for p in parts])
    return src, dst


def closed_groups(src: np.ndarray, dst: np.ndarray) -> dict:
    ids, inv = np.unique(np.concatenate([src, dst]), return_inverse=True)
    s, d = inv[: src.size], inv[src.size:]
    n = ids.size
    m = csr_matrix((np.ones(s.size, dtype=np.int8), (s, d)), shape=(n, n))
    _, comp = connected_components(m, directed=True, connection="strong")
    cs, cd = comp[s], comp[d]
    size = np.bincount(comp)
    leaves = np.zeros(size.size, dtype=bool)
    leaves[cs[cs != cd]] = True                   # an edge from the component to another one
    enters = np.zeros(size.size, dtype=bool)
    enters[cd[cs != cd]] = True                   # an edge into the component from another one
    inner = np.zeros(size.size, dtype=bool)
    inner[cs[cs == cd]] = True                    # an edge inside the component (self-pairs included)
    closed = inner & ~leaves
    multi = closed & (size >= 2)
    single = closed & (size == 1)
    return {"ids": ids, "comp": comp, "size": size, "multi": multi, "single": single, "isolated": ~enters,
            "nodes": int(n), "edges": int(src.size)}


def summarize(cg: dict, score: pd.Series, members: dict[str, np.ndarray]) -> dict:
    ids, comp, size = cg["ids"], cg["comp"], cg["size"]
    s = score.reindex(ids).fillna(0.0).to_numpy()
    total = float(s.sum())
    out = {"graph": {"nodes": cg["nodes"], "edges": cg["edges"]}, "score_nodes": int(len(score)),
           "score_sum": total}

    def block(mask_comp: np.ndarray) -> dict:
        in_node = mask_comp[comp]
        k = int(in_node.sum())
        mass = float(s[in_node].sum()) / total if total > 0 else 0.0
        share = k / cg["nodes"] if cg["nodes"] else 0.0
        res = {"groups": int(mask_comp.sum()), "contracts": k, "share_of_nodes": share, "share_of_mass": mass,
               "mass_over_node_share": (mass / share) if share > 0 else None,
               "largest_group": int(size[mask_comp].max()) if mask_comp.any() else 0}
        node_set = ids[in_node]
        for name, mem in members.items():
            inside = np.isin(mem, node_set)
            res[f"{name}_inside"] = int(inside.sum())
            ms = score.reindex(mem).fillna(0.0).to_numpy()
            pos = ms > 0
            res[f"{name}_with_positive_score"] = int(pos.sum())
            if pos.any():
                top = np.argsort(-ms)[: max(1, int(np.ceil(0.01 * mem.size)))]
                res[f"{name}_top1pct"] = int(top.size)
                res[f"{name}_top1pct_inside"] = int(inside[top].sum())
        return res

    out["closed_groups_two_or_more"] = block(cg["multi"])
    out["closed_groups_two_or_more_isolated"] = block(cg["multi"] & cg["isolated"])
    out["closed_self_pair_only"] = block(cg["single"])
    return out


def main() -> int:
    params = pagerank_params(load_config())
    nodes = load_nodes()
    result = {"note": "post hoc check after every result was known; decides no rule and changes no score "
                      "(exploratory/2026-11-11-closed-groups/README.md)",
              "definition": "closed group = strongly connected component of a walk's graph (pairs of positive "
                            "weight, self-pairs included) with an edge inside it and no edge to a contract outside "
                            "it; isolated = also no edge into it from outside",
              "freezes": {}}
    for tag, names in MEMBERS.items():
        g = load_graphs(tag)
        members = {nm: contract_members(nm, nodes)[0].index.to_numpy(np.int64) for nm in names}
        scores, _ = score_all(g, params, methods=WALKS)
        per = {"members": {nm: int(v.size) for nm, v in members.items()}}
        for w in WALKS:
            src, dst = walk_edges(g, w)
            per[w] = summarize(closed_groups(src, dst), scores[w], members)
            b = per[w]["closed_groups_two_or_more"]
            print(tag, w, per[w]["graph"], {k: b[k] for k in ("groups", "contracts", "share_of_mass", "largest_group")},
                  {k: v for k, v in b.items() if k.endswith("_inside")}, flush=True)
        result["freezes"][tag] = per
    try:
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True,
                              check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        head = None
    result["provenance"] = {"head": head, "variant": "contract12m", "params": params}
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
