"""The discovery-order test (docs/discovery_protocol.md): crawl.py, run_discovery.py and the additions to
scoring.py and stats.py, on toy graphs."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import math
import os
import subprocess
import sys
import textwrap
from fractions import Fraction
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pytest
import yaml
from conftest import CONFIG_PATH, EXPERIMENTS, SCRIPTS

import c12_world

import common
import crawl
import run_discovery as rd
import scoring
import stats

OVERLAY = EXPERIMENTS / "config" / "overlay_contract12m.yaml"
SCORING_BASE = "1747e64"  # the last commit of scripts/scoring.py before the warm start was added


@pytest.fixture(scope="module")
def contract_cfg() -> dict:
    """The configuration of the contract12m variant (the overlay merged as common.load_config does)."""
    cfg = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    for section, values in yaml.safe_load(OVERLAY.read_text(encoding="utf-8")).items():
        cfg.setdefault(section, {}).update(values)
    return cfg


@pytest.fixture(scope="module")
def dcfg(contract_cfg) -> dict:
    return contract_cfg["discovery"]


def addresses(n: int) -> np.ndarray:
    return np.array([f"0x{0x1000 + 17 * i:040x}" for i in range(n)], dtype=object)


def layer(pairs: list[tuple], names: tuple[str, ...]) -> crawl.Layer:
    """A layer from (src, dst) or (src, dst, w) tuples; every weight is w (default 1) and max_sig 0.5."""
    if not pairs:
        return crawl.Layer(np.empty(0, np.int64), np.empty(0, np.int64), {k: np.empty(0) for k in names})
    src = np.array([p[0] for p in pairs], dtype=np.int64)
    dst = np.array([p[1] for p in pairs], dtype=np.int64)
    w = np.array([p[2] if len(p) > 2 else 1.0 for p in pairs], dtype=np.float64)
    return crawl.Layer(src, dst, {k: (np.full(src.size, 0.5) if k == "max_sig" else w) for k in names})


def toy(n: int, allow: list[tuple], transfer: list[tuple]) -> crawl.CrawlGraph:
    return crawl.CrawlGraph(addresses(n), layer(allow, crawl.ALLOW_WEIGHTS), layer(transfer, crawl.TRANSFER_WEIGHTS))


def random_layer(rng: np.random.Generator, n: int, m: int, names: tuple[str, ...],
                 sources: np.ndarray | None = None) -> crawl.Layer:
    src = rng.integers(0, n, m) if sources is None else rng.choice(sources, m)
    key = np.unique(src * n + rng.integers(0, n, m))
    src, dst = key // n, key % n
    w = {k: rng.lognormal(size=src.size) for k in names}
    w["w_raw"][rng.random(src.size) < 0.05] = 0.0  # pairs a walk drops
    w["max_sig"] = rng.uniform(0.01, 1.0, src.size)
    return crawl.Layer(src, dst, w)


def random_graph(n: int, m: int, seed: int) -> crawl.CrawlGraph:
    rng = np.random.default_rng(seed)
    return crawl.CrawlGraph(addresses(n), random_layer(rng, n, int(0.4 * m), crawl.ALLOW_WEIGHTS),
                            random_layer(rng, n, m - int(0.4 * m), crawl.TRANSFER_WEIGHTS))


def universe_graph(n: int, m: int, seed: int, mode: str = "out") -> tuple[crawl.CrawlGraph, np.ndarray]:
    """A random graph restricted to its universe, and the giant-SCC nodes in it."""
    g = random_graph(n, m, seed)
    bt = crawl.bow_tie(g.n, g.union_src, g.union_dst)
    gu, ids = g.restrict(bt.universe(mode))
    return gu, np.flatnonzero(bt.scc[ids])


def visit_order(result: crawl.CrawlResult) -> list[int]:
    v = result.visit_index
    done = np.flatnonzero(v > 0)
    return done[np.argsort(v[done])].tolist()


# --------------------------------------------------------------------------- (1) BFS


def bfs_expected(children: dict[int, list[int]], seed: int, address: np.ndarray) -> list[int]:
    """FIFO by discovery visit; contracts first discovered in the same visit by SHA-256(seed + contract)."""
    seed_hex = address[seed]

    def sha(i):
        return hashlib.sha256((seed_hex + address[i]).encode()).hexdigest()

    order, seen = [seed], {seed}
    i = 0
    while i < len(order):
        new = sorted((c for c in children.get(order[i], []) if c not in seen), key=sha)
        seen.update(new)
        order.extend(new)
        i += 1
    return order


@pytest.mark.parametrize("rho", ["0.05", "0.5"])
def test_bfs_order_on_a_path_and_a_tree(dcfg, rho):
    path = toy(6, [(0, 1), (1, 2), (2, 3)], [(3, 4), (4, 5)])
    assert visit_order(crawl.Crawl(path, 0, "bfs", rho=rho, cfg=dcfg).run()) == [0, 1, 2, 3, 4, 5]

    children = {0: [1, 2, 3], 1: [4, 5, 6], 2: [7], 3: [8, 9], 5: [10, 11], 7: [12]}
    edges = [(p, c) for p, cs in children.items() for c in cs]
    tree = toy(13, edges[::2], edges[1::2])
    got = visit_order(crawl.Crawl(tree, 0, "bfs", rho=rho, cfg=dcfg).run())
    assert got == bfs_expected(children, 0, tree.address)
    assert got[:4] != [0, 1, 2, 3] or got[4:7] != [4, 5, 6]  # the hash order is not the id order here


@pytest.mark.parametrize("mode", crawl.MODES)
def test_bfs_and_random_orders_do_not_depend_on_rho(dcfg, mode):
    g, scc = universe_graph(400, 2400, 3, mode)
    seed = int(crawl.pick_seeds(g.address, scc, 1, dcfg["seed_salt"])[0])
    for ordering in ("bfs", "random"):
        runs = [crawl.Crawl(g, seed, ordering, mode=mode, rho=rho, cfg=dcfg).run() for rho in ("1/100", "1/400",
                                                                                                "1/20", "1/2")]
        assert (runs[0].visit_index > 0).all()
        for r in runs[1:]:
            np.testing.assert_array_equal(r.visit_index, runs[0].visit_index, err_msg=f"{ordering} rho {r.rho}")
    # The random ordering draws one contract per visit from the whole frontier as it is at that visit.
    c = crawl.Crawl(g, seed, "random", mode=mode, rho="1/2", cfg=dcfg)
    while True:
        assert sorted(c._pool) == c.frontier().tolist()
        picks = c.pick()
        if picks.size == 0:
            break
        assert picks.size == 1
        c.visit(picks)
    assert c.recomputes == g.n - 1
    other = crawl.Crawl(g, seed, "random", mode=mode, rho="1/2", cfg={**dcfg, "random_salt": "random-v2:"}).run()
    assert not np.array_equal(other.visit_index, runs[0].visit_index)  # the generator follows the salt and seed


# --------------------------------------------------------------------------- (2), (3) counts and walks


@pytest.mark.parametrize("ordering", crawl.COUNTS)
def test_count_picks_the_most_visited_backlinks(dcfg, ordering):
    edges = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 3)]
    g = toy(5, edges, edges)
    c = crawl.Crawl(g, 0, ordering, rho=0.01, cfg=dcfg)
    c.visit([1, 2])
    assert c.counts[ordering][3] == 2 and c.counts[ordering][4] == 1
    assert c.pick().tolist() == [3]
    # From the seed: a tie between 1 and 2 (same discovery) goes to the lower id, then 2 (earlier
    # discovery than 3 and 4), then 3 with two visited backlinks.
    assert visit_order(crawl.Crawl(g, 0, ordering, rho=0.01, cfg=dcfg).run()) == [0, 1, 2, 3, 4]


def normalisation_graph() -> crawl.CrawlGraph:
    """Seed 0 -> 1, 2, 3; 1 -> 4 alone; 2 and 3 each -> 5 and 99 contracts of their own."""
    edges = [(0, 1), (0, 2), (0, 3), (1, 4), (2, 5), (3, 5)]
    edges += [(2, 6 + i) for i in range(99)] + [(3, 105 + i) for i in range(99)]
    return toy(204, edges, edges)


@pytest.mark.parametrize("ordering, pick", [("ib_a", 5), ("ib_t", 5), ("ib_u", 5), ("cpr_l50", 4), ("cpr_l25", 4),
                                            ("cpr_l75", 4), ("cpr_l100", 4), ("cpr_l0", 4), ("endorserank", 4),
                                            ("spr", 4), ("delta", 4)])
def test_normalisation_counts_and_walks_disagree(dcfg, params, ordering, pick):
    # The walks with uniform restarts (and S-PR, restarted from one of them); the activity walks
    # restart mostly at the two busy contracts and are left out.
    c = crawl.Crawl(normalisation_graph(), 0, ordering, rho=0.01, cfg=dcfg, params=params)
    c.visit([1, 2, 3])
    assert c.pick().tolist() == [pick]


# --------------------------------------------------------------------------- (4), (5) walks on the seen graph


def expected_seen(g: crawl.CrawlGraph, visited: np.ndarray, mode: str):
    """The seen graph built independently: the pairs a visit reveals and the node set S."""
    vis = np.zeros(g.n, dtype=bool)
    vis[visited] = True

    def part(lay: crawl.Layer) -> crawl.Layer:
        keep = vis[lay.src] | (vis[lay.dst] if mode == "both" else False)
        return lay.take(np.flatnonzero(keep))

    a, t = part(g.allow), part(g.transfer)
    nodes = np.unique(np.concatenate([visited, a.src, a.dst, t.src, t.dst]))
    return a, t, nodes


def pairs(lay: crawl.Layer) -> set:
    return set(zip(lay.src.tolist(), lay.dst.tolist(), lay.weights["w_raw"].tolist()))


@pytest.mark.parametrize("mode", crawl.MODES)
def test_walks_on_the_seen_graph_are_the_scoring_functions(dcfg, params, mode):
    g, scc = universe_graph(70, 350, 4, mode)
    c = crawl.Crawl(g, scc[0], "cpr_l50", mode=mode, rho=0.1, cfg=dcfg, params=params)
    c.run(max_visits=25)
    visited = np.flatnonzero(c.visit_index > 0)
    assert visited.size == 25
    a, t, nodes = expected_seen(g, visited, mode)
    sa, st = c.seen()
    assert pairs(sa) == pairs(a) and pairs(st) == pairs(t)
    assert sa.size == a.size and st.size == t.size  # each pair revealed once
    np.testing.assert_array_equal(np.flatnonzero(c.known), nodes)

    act_a = scoring.activeness(a.src, a.dst, a.weights["max_sig"])
    act_t = scoring.activeness(t.src, t.dst, t.weights["max_sig"])
    l100, _ = scoring.weighted_pagerank(a.src, a.dst, a.weights["w_raw"], extra_nodes=nodes, **params)
    direct = {
        "endorserank": scoring.weighted_pagerank(a.src, a.dst, a.weights["w_er"], extra_nodes=nodes, **params)[0],
        "endorserank_activity": scoring.weighted_pagerank(a.src, a.dst, a.weights["w_er"], teleport=act_a,
                                                          extra_nodes=nodes, **params)[0],
        "awp": scoring.weighted_pagerank(t.src, t.dst, t.weights["w_awp"], teleport=act_t, extra_nodes=nodes,
                                         **params)[0],
        "cpr_l100": l100,
        "cpr_l0": scoring.weighted_pagerank(t.src, t.dst, t.weights["w_raw"], extra_nodes=nodes, **params)[0],
        "spr": scoring.weighted_pagerank(t.src, t.dst, t.weights["w_raw"], teleport=l100, extra_nodes=nodes,
                                         **params)[0],
    }
    for method, lam in crawl.COUPLED_LAMBDA.items():
        direct[method] = scoring.coupled_pagerank(
            [(a.src, a.dst, a.weights["w_raw"], lam), (t.src, t.dst, t.weights["w_raw"], 1 - lam)],
            extra_nodes=nodes, **params)[0]
    assert set(direct) == set(crawl.WALKS)
    for method, expected in direct.items():
        got = c.walk_scores(method, warm=False)
        np.testing.assert_array_equal(got.index.to_numpy(), nodes, err_msg=method)
        assert np.max(np.abs(got.to_numpy() - expected.to_numpy())) < 1e-12, method
    # A frontier contract has no revealed out-edge in the out mode: its activeness is 0.
    if mode == "out":
        frontier = c.frontier()
        assert not np.isin(frontier, act_a.index[act_a > 0]).any()


def test_s_pr_without_a_revealed_transfer_edge_is_its_restart_vector(dcfg, params):
    # The seed approves 1, 2 and 3 and pays no contract, so its visit reveals no transfer edge: every contract of S
    # dangles in S-PR', which is then its restart vector C-PR'(1) (protocol section 4), not 0 everywhere.
    g = toy(4, [(0, 1, 1.0), (0, 2, 5.0), (0, 3, 50.0)], [(1, 0), (2, 0), (3, 0)])
    c = crawl.Crawl(g, 0, "spr", rho=0.01, cfg=dcfg, params=params)
    spr, l100 = c.walk_scores("spr", warm=False), c.walk_scores("cpr_l100", warm=False)
    np.testing.assert_array_equal(spr.index.to_numpy(), np.arange(4))
    np.testing.assert_array_equal(spr.to_numpy(), l100.to_numpy())
    assert c.pick().tolist() == [3]
    # After 3 is visited its payment to 0 is revealed; the restarts still put 2 (approved for more) before 1.
    assert visit_order(crawl.Crawl(g, 0, "spr", rho=0.01, cfg=dcfg, params=params).run()) == [0, 3, 2, 1]


@pytest.mark.parametrize("method", ["endorserank", "endorserank_activity", "cpr_l100", "cpr_l25"])
def test_a_walk_without_a_revealed_edge_scores_and_warm_starts_from_its_restarts(dcfg, params, method):
    # The seed pays 1 and 2 and approves no contract, so these walks have no revealed edge in their layers (the
    # coupled walk has its transfer layer, and is the control): every contract of S dangles and the walk scores its
    # restart vector, 1/|S| here, which the next recompute warm-starts from (protocol section 4).
    g = toy(5, [(1, 3), (2, 4)], [(0, 1), (0, 2)])
    c = crawl.Crawl(g, 0, method, rho=0.01, cfg=dcfg, params=params)
    s = c.walk_scores(method, warm=False)
    np.testing.assert_array_equal(s.index.to_numpy(), np.arange(3))
    if method == "cpr_l25":
        assert s.iloc[1] == s.iloc[2] > s.iloc[0]
        return
    np.testing.assert_allclose(s.to_numpy(), np.full(3, 1 / 3), rtol=0, atol=1e-15)
    assert c.pick().tolist() == [1]                     # one tie group: the lower address
    np.testing.assert_allclose(c.prev[method].to_numpy(), np.full(3, 1 / 3), rtol=0, atol=1e-15)
    assert crawl.restart_vector([4, 2, 2]).to_dict() == {2: 0.5, 4: 0.5}


def test_warm_start_reaches_the_cold_fixed_point(params):
    rng = np.random.default_rng(9)
    bound = 2 * params["damping"] / (1 - params["damping"]) * params["tol"]
    for trial in range(5):
        n, m = 200, 1500
        src, dst, w = rng.integers(0, n, m), rng.integers(0, n, m), rng.lognormal(size=m)
        cold, it_cold = scoring.weighted_pagerank(src, dst, w, **params)
        part = rng.random(m) < 0.5
        prev, _ = scoring.weighted_pagerank(src[part], dst[part], w[part], **params)  # an earlier, smaller graph
        warm, it_warm = scoring.weighted_pagerank(src, dst, w, init=prev, **params)
        np.testing.assert_array_equal(warm.index, cold.index)
        assert np.abs(warm.to_numpy() - cold.to_numpy()).sum() < bound
        again, it_again = scoring.weighted_pagerank(src, dst, w, init=cold, **params)
        assert it_again <= 2 and np.abs(again.to_numpy() - cold.to_numpy()).sum() < bound

        layers = [(src[part], dst[part], w[part], 0.5), (src[~part], dst[~part], w[~part], 0.5)]
        c_cold, _ = scoring.coupled_pagerank(layers, extra_nodes=np.arange(n + 5), **params)
        c_warm, _ = scoring.coupled_pagerank(layers, extra_nodes=np.arange(n + 5), init=prev, **params)
        assert np.abs(c_warm.to_numpy() - c_cold.to_numpy()).sum() < bound
        s_cold, _ = scoring.seeded_pagerank(src, dst, w, prev, **params)
        s_warm, _ = scoring.seeded_pagerank(src, dst, w, prev, init=cold, **params)
        assert np.abs(s_warm.to_numpy() - s_cold.to_numpy()).sum() < bound
    # The start vector: previous values on known nodes, 1/n on new ones, renormalised.
    start = scoring._start_vector(np.array([1, 2, 3, 4]), pd.Series([0.5, 0.5], index=[2, 3]))
    np.testing.assert_allclose(start, np.array([0.25, 0.5, 0.5, 0.25]) / 1.5)


# --------------------------------------------------------------------------- (6), (7) no leak, universe


def rewired(g: crawl.CrawlGraph, keep: np.ndarray, seed: int) -> crawl.CrawlGraph:
    """``g`` with every out-edge of the contracts outside ``keep`` replaced by random ones."""
    rng = np.random.default_rng(seed)
    others = np.setdiff1d(np.arange(g.n), keep)

    def swap(lay: crawl.Layer, names: tuple[str, ...]) -> crawl.Layer:
        kept = lay.take(np.flatnonzero(np.isin(lay.src, keep)))
        new = random_layer(rng, g.n, 3 * others.size, names, sources=others)
        return crawl.Layer(np.concatenate([kept.src, new.src]), np.concatenate([kept.dst, new.dst]),
                           {k: np.concatenate([kept.weights[k], new.weights[k]]) for k in names})

    return crawl.CrawlGraph(g.address, swap(g.allow, crawl.ALLOW_WEIGHTS), swap(g.transfer, crawl.TRANSFER_WEIGHTS))


@pytest.mark.parametrize("ordering", ["bfs", "random", "ib_a", "ib_t", "ib_u", "endorserank_activity", "awp",
                                      "cpr_l50", "spr", "delta"])
def test_no_leak_from_unvisited_out_edges(dcfg, params, ordering):
    g = random_graph(90, 450, 6)
    bt = crawl.bow_tie(g.n, g.union_src, g.union_dst)
    seed = int(crawl.pick_seeds(g.address, np.flatnonzero(bt.scc), 1, dcfg["seed_salt"])[0])
    full = visit_order(crawl.Crawl(g, seed, ordering, rho=0.1, cfg=dcfg, params=params).run())
    assert len(full) > 60
    for k in (3, 12, 40):
        g2 = rewired(g, np.array(full[:k]), seed=k)
        part = visit_order(crawl.Crawl(g2, seed, ordering, rho=0.1, cfg=dcfg, params=params).run(max_visits=k + 1))
        assert part == full[: k + 1], (ordering, k)


def test_out_mode_visits_exactly_scc_and_out(dcfg, params):
    # IN = {0, 1}, SCC = {2, 3, 4}, OUT = {5, 6}, a tendril 7 and a separate piece 8 -> 9.
    edges = [(0, 2), (1, 0), (2, 3), (3, 4), (4, 2), (4, 5), (5, 6), (0, 7), (8, 9)]
    g = toy(10, edges[:5], edges[5:] + [(3, 3)])
    bt = crawl.bow_tie(g.n, g.union_src, g.union_dst)
    assert [np.flatnonzero(m).tolist() for m in (bt.scc, bt.in_, bt.out, bt.other, bt.wcc)] == [
        [2, 3, 4], [0, 1], [5, 6], [7, 8, 9], [0, 1, 2, 3, 4, 5, 6, 7]]
    assert bt.sizes() == {"nodes": 10, "edges": 9, "scc": 3, "in": 2, "out": 2, "other": 3, "U": 5,
                          "E_U": 5, "WCC": 8, "E_WCC": 8}
    for seed in (2, 3, 4):
        r = crawl.Crawl(g, seed, "ib_u", rho=0.05, cfg=dcfg).run()
        assert np.flatnonzero(r.visit_index).tolist() == bt.universe("out").tolist()
        r = crawl.Crawl(g, seed, "bfs", mode="both", rho=0.05, cfg=dcfg).run()
        assert np.flatnonzero(r.visit_index).tolist() == bt.universe("both").tolist()
    g = random_graph(150, 330, 2)
    bt = crawl.bow_tie(g.n, g.union_src, g.union_dst)
    assert bt.in_.any() and bt.out.any()
    for seed in crawl.pick_seeds(g.address, np.flatnonzero(bt.scc), 3, dcfg["seed_salt"]):
        r = crawl.Crawl(g, seed, "cpr_l50" if seed % 2 else "random", rho=0.05, cfg=dcfg, params=params).run()
        np.testing.assert_array_equal(np.flatnonzero(r.visit_index), bt.universe("out"))
        assert r.edges_read.sum() == bt.e_u


def test_both_universe_is_the_wcc_of_the_giant_scc(dcfg, params):
    # A: SCC {0, 1, 2}, IN {9}, OUT {10}, five nodes. B: a 2-cycle {3, 4} and a path 4 -> 5 -> ... -> 11, seven
    # nodes. The largest WCC is B, but the both universe is the WCC that holds the giant SCC: A.
    a_edges = [(0, 1), (1, 2), (2, 0), (9, 0), (2, 10)]
    b_edges = [(3, 4), (4, 3), (4, 5), (5, 6), (6, 7), (7, 8), (8, 11)]
    g = toy(12, a_edges[:3] + b_edges[:3], a_edges[3:] + b_edges[3:])
    bt = crawl.bow_tie(g.n, g.union_src, g.union_dst)
    assert np.flatnonzero(bt.scc).tolist() == [0, 1, 2]
    assert np.flatnonzero(bt.wcc).tolist() == [0, 1, 2, 9, 10]
    assert bt.universe("both").tolist() == [0, 1, 2, 9, 10] and bt.universe("out").tolist() == [0, 1, 2, 10]
    assert np.flatnonzero(bt.other).tolist() == [3, 4, 5, 6, 7, 8, 11]
    assert bt.sizes() == {"nodes": 12, "edges": 12, "scc": 3, "in": 1, "out": 1, "other": 7, "U": 4, "E_U": 4,
                          "WCC": 5, "E_WCC": 5}
    # A crawl from a seed of the giant SCC visits exactly the universe of its mode.
    for seed in (0, 1, 2):
        for ordering in ("bfs", "random", "ib_u", "cpr_l50"):
            r = crawl.Crawl(g, seed, ordering, mode="both", rho=0.05, cfg=dcfg, params=params).run()
            assert np.flatnonzero(r.visit_index).tolist() == [0, 1, 2, 9, 10], (seed, ordering)
            assert r.edges_read.sum() == bt.e_wcc
            r = crawl.Crawl(g, seed, ordering, mode="out", rho=0.05, cfg=dcfg, params=params).run()
            assert np.flatnonzero(r.visit_index).tolist() == [0, 1, 2, 10], (seed, ordering)
    # On the universe graph of the both mode the crawl visits every node.
    gu, ids = g.restrict(bt.universe("both"))
    seed = int(np.flatnonzero(bt.scc[ids])[0])
    assert (crawl.Crawl(gu, seed, "bfs", mode="both", rho=0.05, cfg=dcfg).run().visit_index > 0).all()


def test_seeds_are_the_lowest_hashes(dcfg):
    g = toy(30, [(i, (i + 1) % 30) for i in range(30)], [])
    seeds = crawl.pick_seeds(g.address, np.arange(30), 5, dcfg["seed_salt"])
    digests = [hashlib.sha256(("crawl-seed-v1:" + a).encode()).hexdigest() for a in g.address]
    assert seeds.tolist() == sorted(range(30), key=lambda i: digests[i])[:5]
    assert dcfg["seed_salt"] == "crawl-seed-v1:" and dcfg["random_salt"] == "random-v1:"


# --------------------------------------------------------------------------- (8) curves and AUC


def test_curves_and_auc_against_hand_computed_values():
    n = 10
    t = np.array([[2, 5, 9], [1, 3, 10]])  # visit index of three hot contracts, two seeds
    # x = 0.5: X = 5; g = [0.6, 0, 0] and [0.8, 0.4, 0]; g-bar = [0.7, 0.2, 0]
    np.testing.assert_allclose(crawl.visit_scores(t, n, 0.5), [[0.6, 0.0, 0.0], [0.8, 0.4, 0.0]])
    assert crawl.auc(t, n, 0.5) == pytest.approx(0.3)
    grid = crawl.curve_grid(n, 1000)
    assert grid.tolist() == list(range(1, 11))
    pst = crawl.p_st(t, grid)
    np.testing.assert_allclose(pst[0], [0, 1, 1, 1, 2, 2, 2, 2, 3, 3] / np.float64(3))
    np.testing.assert_allclose(pst[1], [1, 1, 2, 2, 2, 2, 2, 2, 2, 3] / np.float64(3))
    # AUC_x is the area under P_ST (a step function) up to X visits, divided by X.
    for row, g in zip(pst, crawl.visit_scores(t, n, 0.5)):
        assert np.r_[0.0, row][:5].sum() / 5 == pytest.approx(g.mean())
    assert crawl.visits_to_reach(t, 0.5).tolist() == [5, 3]
    assert crawl.visits_to_reach(t, 0.9).tolist() == [9, 10]

    # References: the ideal order puts the hot contracts at visits 1..|H|; the random curve is K/|U|.
    assert crawl.ideal_auc(3, n, 0.5) == pytest.approx((0.8 + 0.6 + 0.4) / 3)
    assert crawl.random_auc(n, 0.5) == pytest.approx((5 - 1) / (2 * n))
    np.testing.assert_allclose(crawl.ideal_curve(grid, 3), np.minimum(1, grid / 3))
    np.testing.assert_allclose(crawl.random_curve(grid, n), grid / 10)
    importance = np.array([0, 9, 0, 0, 7, 0, 0, 8, 0, 0], dtype=float)
    hot = crawl.hot_set(importance, 0.3)
    ideal = crawl.ideal_order(importance, hot)
    assert sorted(ideal[hot].tolist()) == [1, 2, 3]
    assert crawl.auc(ideal[hot][None, :], n, 0.5) == pytest.approx(crawl.ideal_auc(3, n, 0.5))
    # The mean over all orders of g_x equals the random reference.
    perms = np.array([np.random.default_rng(i).permutation(n) + 1 for i in range(4000)])
    assert crawl.visit_scores(perms[:, :1], n, 0.5).mean() == pytest.approx(crawl.random_auc(n, 0.5), abs=0.01)

    # P_CS: R_K by rank (decreasing importance, ties to the lower id).
    rank = crawl.rank_order(importance)
    assert rank[[1, 7, 4]].tolist() == [1, 2, 3] and rank[0] == 4
    visit = np.array([3, 1, 4, 5, 2, 6, 7, 8, 9, 10])  # visits 1, 4, 0, 2, ...
    pcs = crawl.p_cs(visit, rank, grid)[0]
    # K = 1: V = {1}, R = {1} -> 1; K = 2: V = {1, 4}, R = {1, 7} -> 1/2; K = 3: V adds 0, R adds 4 -> 2/3
    np.testing.assert_allclose(pcs[:3], [1.0, 0.5, 2 / 3])
    assert pcs[-1] == 1.0
    cap = crawl.captured(visit, importance, grid)[0]
    np.testing.assert_allclose(cap[:3], [9 / 24, 16 / 24, 16 / 24])


def test_exact_shares_hot_sets_and_hubs(dcfg):
    assert crawl.ceil_share(0.07, 100) == 7 and math.ceil(0.07 * 100) == 8  # floats would give 8
    assert crawl.batch_size(0.05, 60) == 3 and crawl.batch_size("0.0125", 81) == 2
    assert crawl.horizon(0.05, 20) == 1 and crawl.ceil_share(0.01, 0) == 0
    v = np.array([5, 3, 3, 1, 0, 0, 0, 0, 0, 0], dtype=float)
    assert np.flatnonzero(crawl.hot_set(v, 0.2)).tolist() == [0, 1, 2]  # ties at the 2nd largest
    assert np.flatnonzero(crawl.hot_set(v, 0.6)).tolist() == [0, 1, 2, 3]  # never a zero
    assert not crawl.hot_set(np.zeros(5), 0.5).any()
    ib = np.array([4, 9, 9, 1] + [0] * 20000, dtype=float)
    assert crawl.hubs(ib, dcfg)[:4].tolist() == [1, 2, 0, 3] and crawl.hubs(ib, dcfg).size == 21  # 0.1 % of 20,004


# --------------------------------------------------------------------------- (9) schedule


@pytest.mark.parametrize("rho", [0.01, 0.05, 0.1, "0.0025"])
def test_batches_follow_the_schedule(dcfg, rho):
    n = 50
    complete = toy(n, [], [(i, j) for i in range(n) for j in range(n) if i != j])
    r = crawl.Crawl(complete, 0, "ib_u", rho=rho, cfg=dcfg).run()
    assert r.batch_sizes.tolist() == crawl.schedule(rho, n)
    assert r.recomputes == crawl.recomputes(rho, n) == len(crawl.schedule(rho, n))
    v = 1
    for b in r.batch_sizes:
        assert b == min(max(1, math.ceil(Fraction(str(rho)) * v)), n - v)
        v += b
    # A frontier shorter than b(V) forces an early recompute: on a path every batch holds one visit.
    path = toy(n, [(i, i + 1) for i in range(n - 1)], [])
    r = crawl.Crawl(path, 0, "ib_u", rho=rho, cfg=dcfg).run()
    assert r.batch_sizes.tolist() == [1] * (n - 1)


def test_recomputes_by_hand():
    assert crawl.schedule(0.5, 10) == [1, 1, 2, 3, 2]
    assert crawl.recomputes(0.5, 10) == 5
    assert crawl.recomputes(0.01, 1) == 0
    assert crawl.recomputes(0.01, 101) == 100  # b(V) = 1 up to V = 100
    assert crawl.recomputes(0.01, 102) == 101


# --------------------------------------------------------------------------- (10) workers


def test_results_do_not_depend_on_the_workers(dcfg, params):
    g, scc = universe_graph(80, 400, 8)
    seeds = crawl.pick_seeds(g.address, scc, 2, dcfg["seed_salt"])
    refs = {m: crawl.full_scores(g, m, params) for m in crawl.WALKS}
    grid = crawl.curve_grid(g.n, 1000)
    tasks = [rd.Task(i, int(s), o, "1/20") for i, s in enumerate(seeds)
             for o in ("bfs", "random", "ib_u", "cpr_l50", "spr", "endorserank_activity", "delta")]
    one = rd.run_crawls(g, tasks, mode="out", cfg=dcfg, params=params, refs=refs, grid=grid, workers=1)
    two = rd.run_crawls(g, tasks, mode="out", cfg=dcfg, params=params, refs=refs, grid=grid, workers=2)
    assert list(one) == list(two) == tasks
    for t in tasks:
        a, b = one[t], two[t]
        assert set(a) == set(b)
        for k in a:
            if k != "seconds":
                np.testing.assert_array_equal(np.asarray(a[k]), np.asarray(b[k]), err_msg=f"{t} {k}")
        assert a["visits"] == g.n and a["batches_ok"]
        if t.ordering in crawl.WALKS:
            assert a["final_diff"] < rd.FINAL_TOLERANCE


# --------------------------------------------------------------------------- (11) paired_mean_contrast


def test_paired_mean_contrast_against_a_direct_computation():
    rng = np.random.default_rng(12)
    a, b = rng.uniform(size=60), rng.uniform(size=60) * 0.9
    idx = stats.resample_matrix(60, 400, 42)
    got = stats.paired_mean_contrast(a, b, idx)
    delta = np.array([a[row].mean() - b[row].mean() for row in idx])
    assert got["point"] == pytest.approx(a.mean() - b.mean(), abs=1e-15)
    assert got["lo"] == pytest.approx(np.percentile(delta, 2.5), abs=1e-14)
    assert got["hi"] == pytest.approx(np.percentile(delta, 97.5), abs=1e-14)
    assert got["share_positive"] == np.mean(delta > 0) and got["n"] == 60
    assert stats.paired_mean_contrast([], [], np.empty((400, 0)))["point"] is None
    with pytest.raises(ValueError):
        stats.paired_mean_contrast(a, b[:-1], idx)


# --------------------------------------------------------------------------- (12) unchanged scores


@pytest.fixture(scope="module")
def scoring_base(tmp_path_factory):
    out = subprocess.run(["git", "show", f"{SCORING_BASE}:./scripts/scoring.py"], cwd=EXPERIMENTS,
                         capture_output=True)
    if out.returncode != 0:
        pytest.skip(f"commit {SCORING_BASE} is not available")
    path = tmp_path_factory.mktemp("base") / "scoring_base.py"
    path.write_bytes(out.stdout)
    spec = importlib.util.spec_from_file_location("scoring_base", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def same(x, y) -> None:
    (sx, ix), (sy, iy) = x, y
    assert ix == iy
    np.testing.assert_array_equal(sx.index.to_numpy(), sy.index.to_numpy())
    np.testing.assert_array_equal(sx.to_numpy(), sy.to_numpy())


@pytest.mark.parametrize("seed", [0, 1, 2, 3])
def test_init_none_leaves_the_scores_unchanged(scoring_base, params, seed):
    rng = np.random.default_rng(seed)
    n = 300 if seed % 2 else 40
    ids = rng.permutation(10 * n)[:n] if seed < 2 else np.unique(rng.integers(-(2**60), 2**60, 2 * n))[:n]
    layers = []
    for _ in range(2):
        m = 6 * n
        src, dst = ids[rng.integers(0, n // 2 + 1, m)], ids[rng.integers(0, n, m)]
        w = np.where(rng.random(m) < 0.1, 0.0, rng.lognormal(size=m))
        layers.append((src, dst, w))
    (sa, da, wa), (st, dt, wt) = layers
    act = scoring.activeness(sa, da, rng.uniform(size=sa.size))
    extra = ids[rng.integers(0, n, 20)]
    new, old = scoring, scoring_base
    same(new.weighted_pagerank(sa, da, wa, **params), old.weighted_pagerank(sa, da, wa, **params))
    same(new.weighted_pagerank(sa, da, wa, teleport=act, init=None, **params),
         old.weighted_pagerank(sa, da, wa, teleport=act, **params))
    same(new.weighted_pagerank(st, dt, wt, extra_nodes=extra, **params),
         old.weighted_pagerank(st, dt, wt, extra_nodes=extra, **params))
    for lam in (0.25, 0.5, 0.75, 1.0, 0.0):
        lay = [(sa, da, wa, lam), (st, dt, wt, 1.0 - lam)]
        same(new.coupled_pagerank(lay, **params), old.coupled_pagerank(lay, **params))
        same(new.coupled_pagerank(lay, extra_nodes=None, init=None, **params), old.coupled_pagerank(lay, **params))
    allowance, _ = old.weighted_pagerank(sa, da, wa, **params)
    same(new.seeded_pagerank(st, dt, wt, allowance, **params), old.seeded_pagerank(st, dt, wt, allowance, **params))
    # extra_nodes of the coupled walk adds isolated nodes as in weighted_pagerank.
    lay = [(sa, da, wa, 1.0), (st, dt, wt, 0.0)]
    coupled, _ = scoring.coupled_pagerank(lay, extra_nodes=extra, **params)
    single, _ = scoring.weighted_pagerank(sa, da, wa, extra_nodes=extra, **params)
    np.testing.assert_array_equal(coupled.index, single.index)
    assert np.max(np.abs(coupled.to_numpy() - single.to_numpy())) < 1e-12


def test_isolated_wallets_join_the_coupled_graph_too(params):
    # Revision section 11, Sensitivity 2: the cohort members a graph leaves out are added to every graph as
    # isolated nodes, the coupled one included (graphs.score_all). Without them every score is as before.
    import graphs

    allow = pd.DataFrame({"src": [1, 2], "dst": [2, 3], "w_er": [1.0, 2.0], "w_raw": [1.0, 2.0],
                          "max_sig": [0.5, 0.5]})
    transfer = pd.DataFrame({"src": [3, 4], "dst": [4, 1], "w_awp": [1.0, 1.0], "w_raw": [3.0, 1.0],
                             "max_sig": [0.5, 0.5]})
    g = graphs.Graphs("t1", allow, transfer)
    plain, _ = graphs.score_all(g, params)
    iso, _ = graphs.score_all(g, params, isolated=np.array([2, 9]))
    for m, lam in graphs.COUPLED.items():
        lay = [(allow["src"], allow["dst"], allow["w_raw"], lam),
               (transfer["src"], transfer["dst"], transfer["w_raw"], 1.0 - lam)]
        pd.testing.assert_series_equal(plain[m], scoring.coupled_pagerank(lay, **params)[0])
        pd.testing.assert_series_equal(iso[m], scoring.coupled_pagerank(lay, extra_nodes=[9], **params)[0])
        assert 9 not in plain[m].index and iso[m].loc[9] > 0 and iso[m].sum() == pytest.approx(1.0)
    # Each single-layer walk takes the wallets it lacks (2 is a node of the allowance layer); S-PR takes none.
    assert set(iso["cpr_l100"].index) == {1, 2, 3, 9} and set(iso["cpr_l0"].index) == {1, 2, 3, 4, 9}
    assert set(iso["spr"].index) == set(plain["spr"].index) == {1, 3, 4}


# --------------------------------------------------------------------------- (13) the structure pilot


def pilot_inputs(root: Path) -> dict[str, Path]:
    """Toy inputs of the pilot: SCC {0, 1, 2}, IN {4}, OUT {3, 5}, other {6, 7}; 8 only uncapped."""
    a = addresses(12)
    rows = [("allow_capped", 0, 1), ("allow_capped", 1, 2), ("allow_capped", 2, 0), ("allow_capped", 2, 3),
            ("allow_capped", 4, 0), ("allow_capped", 4, 0),  # a duplicate row
            ("transfer", 3, 5), ("transfer", 1, 1), ("transfer", 6, 7),
            ("allow_uncapped", 0, 1), ("allow_uncapped", 1, 2), ("allow_uncapped", 2, 0), ("allow_uncapped", 2, 3),
            ("allow_uncapped", 4, 0), ("allow_uncapped", 8, 0)]
    paths = {k: root / k for k in ("struct_t1", "types", "cohort_t1", "labels_w0")}
    common.write_parts(pd.DataFrame({"a": [a[i].upper().replace("0X", "0x") for _, i, _ in rows],
                                     "b": [a[j] for _, _, j in rows], "layer": [r[0] for r in rows]}),
                       paths["struct_t1"])
    common.write_parts(pilot_types(a), paths["types"])
    untyped = "0x" + "ab" * 20
    cohort = [bytes.fromhex(x[2:]) for x in (a[0], a[3], a[6], a[9], untyped)]
    common.write_parts(pd.DataFrame({"address": cohort, "owners_nonzero": 3, "approval_logs": 3}), paths["cohort_t1"])
    common.write_parts(pd.DataFrame({"wallet": [a[1], a[5], a[8], a[9]], "future_new_approvers": 1}),
                       paths["labels_w0"])
    return paths


HASH = {k: "0x" + k * 32 for k in ("aa", "bb", "cc", "dd", "ee")}
IMPL = {k: "0x" + k * 20 for k in ("f1", "f2")}
EP_V06, EP_V07 = "0x5ff137d4b0fdcd49dca30c7cf57e578a026d2789", "0x0000000071727de22e5e9d8baf0edac6f37da032"
OTHER_EP = "0x" + "12" * 20


def pilot_types(a: np.ndarray) -> pd.DataFrame:
    """Account types of the pilot's toy addresses 0..9 (9 is an externally owned account; 8 is no node of the
    union graph). Code families among the union nodes 0..7: aa {0, 1, 2}, bb {3, 4}, cc {5}, dd {6, 7}, where 6
    answers the canonical EntryPoint v0.7 (in upper case); 8, of family ee, answers v0.6."""
    return pd.DataFrame({
        "address": list(a[:10]), "account_class": ["contract"] * 9 + ["eoa"],
        "code_kind": ["contract"] * 9 + ["none"],
        "code_size": [100, 100, 200, 300, 50, 10, 400, 400, 500, None],
        "code_hash": [HASH["aa"]] * 3 + [HASH["bb"]] * 2 + [HASH["cc"]] + [HASH["dd"].upper().replace("0X", "0x")] * 2
                     + [HASH["ee"], None],
        "proxy_kind": ["none", "eip1167", "eip1167", "none", "erc1967", None, "none", "none", "none", None],
        "implementation": [None, IMPL["f1"], IMPL["f1"], None, IMPL["f2"], None, None, "", None, None],
        "entry_point": [None, "", "", None, None, OTHER_EP, EP_V07.upper().replace("0X", "0x"), "", EP_V06, None],
        "wallet_kind": ["none"] * 9 + [None],
        "has_master_copy": [False] * 10})


def protocol_copy(path: Path, block: dict | None = None) -> Path:
    text = "# Protocol\n\n## 7. Rules\n\nText.\n\n## Protocol fixed\n\n(Added at gate B.)\n"
    if block is not None:
        text += "\nFixed by rule.\n\n```json\n" + json.dumps(block, indent=2) + "\n```\n\n## After\n\nMore.\n"
    path.write_text(text, encoding="utf-8")
    return path


def check_pilot(rep: dict, dcfg: dict) -> None:
    assert rep["struct_rows"] == 15 and rep["duplicate_rows"] == 1
    assert rep["layers"] == {"allow_capped": {"edges": 5, "nodes": 5, "self_loops": 0},
                             "allow_uncapped": {"edges": 6, "nodes": 6, "self_loops": 0},
                             "transfer": {"edges": 2, "nodes": 4, "self_loops": 1}}
    assert rep["union"] == {"layers": ["allow_capped", "transfer"], "nodes": 8, "edges": 7}
    assert rep["bow_tie"] == {"scc": 3, "in": 1, "out": 2, "other": 2}
    assert rep["sizes"] == {"U": 5, "E_U": 5, "WCC": 6, "E_WCC": 6}
    assert rep["capped_allowance_in_edge_share"] == {"U": 0.8, "U_from_U": 0.8}
    cohort, spenders = rep["coverage"]["w0_cohort"], rep["coverage"]["w0_spenders"]
    assert (cohort["members"], cohort["contracts"], cohort["user_accounts"], cohort["untyped"]) == (5, 3, 1, 1)
    assert {k: v["n"] for k, v in cohort["covered"].items()} == {
        "allow_capped": 2, "allow_uncapped": 2, "transfer": 2, "union": 3, "U": 2, "WCC": 2}
    assert {k: v["n"] for k, v in spenders["covered"].items()} == {
        "allow_capped": 1, "allow_uncapped": 2, "transfer": 1, "union": 2, "U": 2, "WCC": 2}
    assert rep["account_types"] == {
        "queue": {"rows": 10, "account_class": {"contract": 9, "eoa": 1}, "wallet_kind": {"": 1, "none": 9},
                  "proxy_kind": {"": 2, "eip1167": 2, "erc1967": 1, "none": 5}},
        "union_nodes": {"nodes": 8, "untyped": 0, "account_class": {"contract": 8}, "wallet_kind": {"none": 8},
                        "proxy_kind": {"": 1, "eip1167": 2, "erc1967": 1, "none": 4}}}
    fam = rep["code_families"]
    assert (fam["contracts"], fam["groups"]) == (8, 4)
    assert fam["largest"] == [
        {"code_hash": HASH["aa"], "n": 3, "code_size": 100, "proxy_kind": "eip1167", "implementation": IMPL["f1"],
         "entry_points": {"": 3}},
        {"code_hash": HASH["bb"], "n": 2, "code_size": 50, "proxy_kind": "erc1967", "implementation": IMPL["f2"],
         "entry_points": {"": 2}},  # ties: the lower code size and proxy kind
        {"code_hash": HASH["dd"], "n": 2, "code_size": 400, "proxy_kind": "none", "implementation": "",
         "entry_points": {"": 1, EP_V07: 1}},
        {"code_hash": HASH["cc"], "n": 1, "code_size": 10, "proxy_kind": "", "implementation": "",
         "entry_points": {OTHER_EP: 1}}]
    # Only the union nodes count: 8 answers v0.6 but is no node of the union graph.
    assert fam["canonical_entry_point"] == [{**fam["largest"][2], "n_canonical": 1}]
    rules = rep["rules"]
    assert (rules["rho"], rules["q"], rules["primary_mode"]) == (0.01, 0.05, "out")
    assert rules["primary_universe"] == {"name": "U", "P": 5, "E_P": 5}
    assert rules["stop"] == {"no_rho_within_budget": False, "few_capped_allowance_edges": True,
                             "few_capped_allowance_in_edges": False} and rules["stopped"]
    assert rules["projected_hours"]["0.01"] == crawl.projected_hours(0.01, rep["rule_inputs"], dcfg)
    assert {k: rep[k] for k in ("U", "E_U", "WCC", "E_WCC", "rho", "q", "primary_mode", "stopped")} == {
        "U": 5, "E_U": 5, "WCC": 6, "E_WCC": 6, "rho": 0.01, "q": 0.05, "primary_mode": "out", "stopped": True}


FORBIDDEN = {
    crawl: ("Crawl", "walk", "full_scores", "dense", "select_top", "hot_set", "rank_order", "ideal_order", "hubs",
            "without_hubs", "curve_grid", "p_st", "p_cs", "captured", "visit_scores", "auc", "visits_to_reach",
            "ideal_auc", "random_auc", "pick_seeds", "random_generator"),
    scoring: ("weighted_pagerank", "coupled_pagerank", "seeded_pagerank", "activeness", "awp_edges",
              "endorserank_edges", "value_transform", "logistic_decay", "_power_iterate"),
    stats: ("paired_mean_contrast", "resample_matrix", "percentile_ci", "kendall_tau_b", "PairedBootstrap"),
    rd: ("run_window", "run_crawls", "Measures", "full_graph", "coverage", "check_fixed", "committed", "graph_sizes",
         "match_pilot", "importance_positions", "read_inflow_untyped", "top_share", "verdict", "statements"),
}


def test_the_pilot_reads_the_classes_with_the_smart_account_lists(tmp_path, monkeypatch, contract_cfg):
    # Revision section 13, amendment of 9 November 2026: the pilot reads the account types as sql/31 does, with the
    # listed contracts as smart accounts of wallet kind erc4337.
    a = addresses(12)
    paths = pilot_inputs(tmp_path)
    # Address 10, a contract of code hash 99 that is no node of the structure, joins the W0 cohort.
    types = pilot_types(a)
    extra = {**{c: None for c in types.columns}, "address": a[10], "account_class": "contract", "code_kind": "contract",
             "code_size": 90, "code_hash": "0x" + "99" * 32, "proxy_kind": "none", "implementation": "",
             "entry_point": EP_V06, "wallet_kind": "none", "has_master_copy": False}
    common.write_parts(pd.concat([types, pd.DataFrame([extra])], ignore_index=True), paths["types"])
    cohort = common.read_parts(paths["cohort_t1"])
    common.write_parts(pd.concat([cohort, pd.DataFrame({"address": [bytes.fromhex(a[10][2:])], "owners_nonzero": [3],
                                                        "approval_logs": [3]})], ignore_index=True), paths["cohort_t1"])

    def pilot(out: str) -> dict:
        return rd.run_feasibility(contract_cfg, struct=paths["struct_t1"], types=paths["types"],
                                  cohort=paths["cohort_t1"], labels=paths["labels_w0"], out=tmp_path / out,
                                  protocol=protocol_copy(tmp_path / "protocol.md"))

    plain = pilot("plain.json")["coverage"]["w0_cohort"]
    assert (plain["members"], plain["contracts"], plain["user_accounts"]) == (6, 4, 1)
    monkeypatch.setattr(common, "SMART_ACCOUNT_CODE_HASHES", ("0x" + "99" * 32,))
    rep = pilot("listed.json")
    cohort_cov = rep["coverage"]["w0_cohort"]
    assert (cohort_cov["members"], cohort_cov["contracts"], cohort_cov["user_accounts"]) == (6, 3, 2)
    assert rep["account_types"]["queue"]["account_class"] == {"contract": 9, "eoa": 1, "smart_account": 1}
    assert rep["account_types"]["queue"]["wallet_kind"]["erc4337"] == 1
    assert rep["sizes"] == {"U": 5, "E_U": 5, "WCC": 6, "E_WCC": 6}  # address 10 is no node
    # A listed contract among the nodes means a structure table built without the lists: no pilot output.
    monkeypatch.setattr(common, "SMART_ACCOUNT_IMPLEMENTATIONS", ((HASH["bb"], IMPL["f2"]),))  # address 4, a node
    with pytest.raises(SystemExit, match="not contracts"):
        pilot("refused.json")
    assert not (tmp_path / "refused.json").exists()
    # the typing output on disk is not changed
    assert common.read_parts(paths["types"], ["account_class"])["account_class"].tolist() == \
        ["contract"] * 9 + ["eoa", "contract"]


def test_feasibility_touches_no_weight_importance_or_crawl_code(tmp_path, monkeypatch, contract_cfg, dcfg):
    paths = pilot_inputs(tmp_path)

    def forbidden(*args, **kwargs):
        raise AssertionError("the structure pilot called weight, importance, crawl, curve or AUC code")

    for module, names in FORBIDDEN.items():
        for name in names:
            monkeypatch.setattr(module, name, forbidden)
    real_read = common.read_parts

    def read(stem, columns=None):
        assert Path(stem).name in ("struct_t1", "types", "cohort_t1", "labels_w0"), stem
        assert Path(stem).name != "labels_w0" or list(columns) == ["wallet"]  # no label value is read
        return real_read(stem, columns)

    monkeypatch.setattr(common, "read_parts", read)
    out = tmp_path / "feasibility_t1.json"
    rep = rd.run_feasibility(contract_cfg, struct=paths["struct_t1"], types=paths["types"],
                             cohort=paths["cohort_t1"], labels=paths["labels_w0"], out=out,
                             protocol=protocol_copy(tmp_path / "protocol.md"))
    check_pilot(rep, dcfg)
    assert json.loads(out.read_text(encoding="utf-8"))["sizes"]["U"] == 5
    # From the command line a stop flag (here: fewer than 5,000 capped allowance edges) exits with 2.
    real = rd.run_feasibility
    monkeypatch.setattr(common, "CONTRACT_GRAPH", True)
    monkeypatch.setattr(rd, "run_feasibility", lambda cfg: real(
        contract_cfg, struct=paths["struct_t1"], types=paths["types"], cohort=paths["cohort_t1"],
        labels=paths["labels_w0"], out=out, protocol=protocol_copy(tmp_path / "protocol.md")))
    assert rd.main(["--window", "t1", "--feasibility"]) == 2
    # Once the protocol is fixed the pilot output is pinned.
    with pytest.raises(SystemExit, match="pinned"):
        real(contract_cfg, struct=paths["struct_t1"], types=paths["types"],
                           cohort=paths["cohort_t1"], labels=paths["labels_w0"], out=out,
                           protocol=protocol_copy(tmp_path / "fixed.md", {"date": "2026-11-09"}))


def run_py(code: str, variant: str | None = "contract12m", args: list[str] | None = None):
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"}
    env.pop("CONTRACT_REP_VARIANT", None)
    if variant:
        env["CONTRACT_REP_VARIANT"] = variant
    cmd = [sys.executable, *(args or ["-c", textwrap.dedent(code)])]
    return subprocess.run(cmd, cwd=SCRIPTS if args is None else EXPERIMENTS, env=env, capture_output=True,
                          text=True, encoding="utf-8")


def test_account_types_and_code_families_on_synthetic_types():
    a = addresses(12)
    types = pilot_types(a)
    # A node without a type row counts as untyped; the types of addresses outside the nodes are left out.
    nodes = [a[0], a[4], a[9], a[11]]
    got = rd.account_types(types, nodes)
    assert got["queue"]["rows"] == 10
    assert got["union_nodes"] == {"nodes": 4, "untyped": 1, "account_class": {"contract": 2, "eoa": 1, "untyped": 1},
                                  "wallet_kind": {"": 1, "none": 2, "untyped": 1},
                                  "proxy_kind": {"": 1, "erc1967": 1, "none": 1, "untyped": 1}}
    # Every canonical group is listed, also beyond the largest ones; the comparison ignores case; a user account
    # never forms a family.
    canonical = [EP_V06.upper().replace("0X", "0x"), EP_V07]
    fam = rd.code_families(types, list(a[:10]), canonical, top=2)
    assert [f["code_hash"] for f in fam["largest"]] == [HASH["aa"], HASH["bb"]]
    assert [(f["code_hash"], f["n"], f["n_canonical"]) for f in fam["canonical_entry_point"]] == [
        (HASH["dd"], 2, 1), (HASH["ee"], 1, 1)]
    assert fam["contracts"] == 9 and fam["groups"] == 5
    assert rd.code_families(types, [a[9]], canonical) == {"contracts": 0, "groups": 0, "largest": [],
                                                         "canonical_entry_point": []}


def test_feasibility_imports_no_weight_code(tmp_path):
    paths = pilot_inputs(tmp_path)
    out = run_py(f"""
        import json, sys
        from pathlib import Path
        import common, run_discovery as rd
        rep = rd.run_feasibility(common.load_config(), struct=Path(r"{paths['struct_t1']}"),
                                 types=Path(r"{paths['types']}"), cohort=Path(r"{paths['cohort_t1']}"),
                                 labels=Path(r"{paths['labels_w0']}"), out=Path(r"{tmp_path / 'f.json'}"),
                                 protocol=Path(r"{protocol_copy(tmp_path / 'p.md')}"))
        print(json.dumps({{"loaded": [m for m in ("scoring", "graphs", "stats") if m in sys.modules],
                          "U": rep["sizes"]["U"]}}))
    """)
    assert out.returncode == 0, out.stderr
    assert json.loads(out.stdout) == {"loaded": [], "U": 5}


# --------------------------------------------------------------------------- (14) rules


def test_rules_on_hand_made_structure_counts(dcfg):
    big = {"U": 100_000, "E_U": 1_000_000, "WCC": 150_000, "E_WCC": 1_500_000, "allow_capped_edges": 80_000,
           "allow_in_share": 0.3}
    r = crawl.rules(big, dcfg)
    # The out mode is primary (100,000 >= 0.5 x 150,000), so P = SCC u OUT:
    # T(rho) = 12 ns x 30 x [400 R(rho, U) E_U + 400 R(rho, WCC) E_WCC + 100 R(rho/4, U) E_U] / 16
    for rho, quarter in ((0.01, "0.0025"), (0.02, "0.005"), (0.05, "0.0125")):
        work = (400 * crawl.recomputes(rho, 100_000) * 1_000_000 + 400 * crawl.recomputes(rho, 150_000) * 1_500_000
                + 100 * crawl.recomputes(quarter, 100_000) * 1_000_000)
        assert r["projected_hours"][str(rho)] == pytest.approx(12e-9 * 30 * work / 16 / 3600)
        assert r["recomputes"][str(rho)] == {"U": crawl.recomputes(rho, 100_000), "WCC": crawl.recomputes(rho, 150_000),
                                             "P_quarter": crawl.recomputes(quarter, 100_000)}
    assert r["projected_hours"]["0.01"] < 12 and r["rho"] == 0.01
    assert (r["q"], r["primary_mode"], r["stopped"]) == (0.01, "out", False)
    assert r["primary_universe"] == {"name": "U", "P": 100_000, "E_P": 1_000_000}

    # The both mode is primary (40,000 < 75,000): the rho/4 term runs on the WCC, and q is set by |WCC|.
    wide = {**big, "U": 4_000, "E_U": 30_000, "WCC": 150_000, "E_WCC": 1_500_000}
    r = crawl.rules(wide, dcfg)
    assert r["primary_mode"] == "both" and r["primary_universe"] == {"name": "WCC", "P": 150_000, "E_P": 1_500_000}
    for rho, quarter in ((0.01, "0.0025"), (0.02, "0.005"), (0.05, "0.0125")):
        work = (400 * crawl.recomputes(rho, 4_000) * 30_000 + 400 * crawl.recomputes(rho, 150_000) * 1_500_000
                + 100 * crawl.recomputes(quarter, 150_000) * 1_500_000)
        assert r["projected_hours"][str(rho)] == pytest.approx(12e-9 * 30 * work / 16 / 3600)
        assert crawl.projected_hours(rho, wide, dcfg) == r["projected_hours"][str(rho)]
        assert r["recomputes"][str(rho)]["P_quarter"] == crawl.recomputes(quarter, 150_000)
    assert r["q"] == 0.01  # |SCC u OUT| = 4,000 alone would give 5%
    r = crawl.rules({**wide, "WCC": 9_000, "E_WCC": 90_000}, dcfg)  # 4,000 < 4,500: both, and |WCC| < 10,000
    assert (r["primary_mode"], r["q"]) == ("both", 0.05)
    r = crawl.rules({**wide, "U": 12_000, "WCC": 20_000}, dcfg)  # 12,000 >= 10,000: out, q by |SCC u OUT|
    assert (r["primary_mode"], r["q"]) == ("out", 0.01)
    r = crawl.rules({**wide, "U": 9_000, "WCC": 12_000}, dcfg)  # out although |WCC| >= 10,000
    assert (r["primary_mode"], r["q"]) == ("out", 0.05)
    # The stop share stays the share of SCC u OUT, whatever the mode.
    assert crawl.rules({**wide, "allow_in_share": 0.049}, dcfg)["stop"]["few_capped_allowance_in_edges"]

    slow = {**big, "E_U": 3_000_000, "E_WCC": 4_000_000}  # rho = 0.01 too slow, 0.02 within 12 hours
    r = crawl.rules(slow, dcfg)
    assert r["projected_hours"]["0.01"] > 12 >= r["projected_hours"]["0.02"] and r["rho"] == 0.02
    r = crawl.rules({**big, "E_U": 10**9, "E_WCC": 10**9}, dcfg)
    assert r["rho"] is None and r["stop"]["no_rho_within_budget"] and r["stopped"]

    assert crawl.rules({**big, "U": 9_999, "WCC": 15_000}, dcfg)["q"] == 0.05
    assert crawl.rules({**big, "U": 10_000, "WCC": 15_000}, dcfg)["q"] == 0.01
    assert crawl.rules({**big, "U": 74_999}, dcfg)["primary_mode"] == "both"  # below 0.5 x 150,000
    assert crawl.rules({**big, "U": 75_000}, dcfg)["primary_mode"] == "out"
    r = crawl.rules({**big, "allow_capped_edges": 4_999}, dcfg)
    assert r["stop"]["few_capped_allowance_edges"] and r["stopped"]
    assert not crawl.rules({**big, "allow_capped_edges": 5_000}, dcfg)["stopped"]
    r = crawl.rules({**big, "allow_in_share": 0.049}, dcfg)
    assert r["stop"]["few_capped_allowance_in_edges"] and r["stopped"]
    assert not crawl.rules({**big, "allow_in_share": 0.05}, dcfg)["stopped"]


# --------------------------------------------------------------------------- (15) refusals, decision wording


def fixed_setup(tmp_path: Path, dcfg: dict, pilot_change: dict | None = None, inputs: dict | None = None,
                **change) -> tuple[dict, Path]:
    """A pilot output (run on committed files with the overlay's discovery settings, its rules those of crawl.rules
    on its rule inputs) and a block that fixes it. ``stopped`` gives the pilot too few capped allowance edges."""
    feas = tmp_path / "data" / "discovery" / "feasibility_t1.json"
    feas.parent.mkdir(parents=True, exist_ok=True)
    sizes = {"U": 5, "E_U": 5, "WCC": 6, "E_WCC": 6}
    stopped = change.pop("stopped", False)
    inputs = inputs or {**sizes, "allow_capped_edges": 100 if stopped else 6000, "allow_in_share": 0.5}
    rules = json.loads(json.dumps(rd._clean(crawl.rules(inputs, dcfg))))
    pilot = {"sizes": {k: inputs[k] for k in sizes}, "rules": rules, "rule_inputs": inputs,
             "layers": {"allow_capped": {"edges": inputs["allow_capped_edges"]}},
             "capped_allowance_in_edge_share": {"U": inputs["allow_in_share"]},
             "code": {"head": "abc123", "committed": {rel: True for rel in rd.COMMITTED}}, "discovery_config": dcfg,
             **(pilot_change or {})}
    feas.write_text(json.dumps(pilot), encoding="utf-8")
    recorded = pilot["rules"]
    block = {"date": "2026-11-09", "feasibility": "data/discovery/feasibility_t1.json",
             "sha256": hashlib.sha256(feas.read_bytes()).hexdigest(), **pilot["sizes"],
             "rho": recorded["rho"], "q": recorded["q"], "primary_mode": recorded["primary_mode"], **change}
    return block, feas


BIG = {"U": 100_000, "E_U": 200_000, "WCC": 150_000, "E_WCC": 300_000, "allow_capped_edges": 6000,
       "allow_in_share": 0.5}


def test_the_pilot_must_be_that_of_this_code_and_its_values_those_of_the_rules(tmp_path, dcfg, capsys):
    rules = crawl.rules(BIG, dcfg)
    assert (rules["rho"], rules["q"], rules["primary_mode"], rules["stopped"]) == (0.01, 0.01, "out", False)
    block, feas = fixed_setup(tmp_path, dcfg, inputs=BIG)
    assert rd.check_fixed(block, feas, tmp_path, dcfg)["q"] == Fraction(1, 100)
    # A pilot written by other code records rules that this code does not give from the same inputs (here q =
    # 5% for |P| = 100,000). Its values never become the protocol's (protocol section 8): "Protocol fixed" must
    # carry the values that the rules of this code set from the pilot's sizes, with or without an author decision,
    # and the pilot itself goes on only with an author decision.
    other = {"rules": {**json.loads(json.dumps(rd._clean(rules))), "q": 0.05}}
    block, feas = fixed_setup(tmp_path, dcfg, other, inputs=BIG)
    assert block["q"] == 0.05
    for decided in ({}, {"author_decision": "the pilot of commit abc"}):
        with pytest.raises(SystemExit, match="differ from the values that the rules"):
            rd.check_fixed({**block, **decided}, feas, tmp_path, dcfg)
    with pytest.raises(SystemExit, match="refused: the rules of this code give other values"):
        rd.check_fixed({**block, "q": 0.01}, feas, tmp_path, dcfg)
    assert rd.check_fixed({**block, "q": 0.01, "author_decision": "the pilot of commit abc"}, feas, tmp_path,
                          dcfg)["q"] == Fraction(1, 100)
    # A pilot whose rule inputs are not its own counts (its sizes, capped allowance edges and in-edge share).
    for change in ({"rule_inputs": None}, {"rule_inputs": {**BIG, "U": 99_999}},
                   {"layers": {"allow_capped": {"edges": 7000}}},
                   {"capped_allowance_in_edge_share": {"U": 0.4}}):
        block, feas = fixed_setup(tmp_path, dcfg, change, inputs=BIG)
        with pytest.raises(SystemExit, match="refused: the structure pilot records no rule inputs"):
            rd.check_fixed(block, feas, tmp_path, dcfg)
    # Its own counts set a stop flag that its rule inputs hide: the run stops unless the author decides.
    block, feas = fixed_setup(tmp_path, dcfg, {"layers": {"allow_capped": {"edges": 4000}}}, inputs=BIG)
    with pytest.raises(SystemExit, match="stopped"):
        rd.check_fixed(block, feas, tmp_path, dcfg)
    assert rd.check_fixed({**block, "author_decision": "few edges, run anyway"}, feas, tmp_path,
                          dcfg)["q"] == Fraction(1, 100)
    # The rules of this code with the settings of this run, even when the pilot ran with others.
    block, feas = fixed_setup(tmp_path, dcfg, {"discovery_config": {**dcfg, "runtime_budget_hours": 0.0001}},
                              inputs=BIG)
    with pytest.raises(SystemExit, match="refused: the discovery settings differ"):
        rd.check_fixed(block, feas, tmp_path, dcfg)
    with pytest.raises(SystemExit, match="refused: the discovery settings differ"):
        rd.check_fixed({**block, "author_decision": "settings checked"}, feas, tmp_path, None)
    # Protocol section 8: an author's decision also lets a pilot output go on whose hash is not the pinned one.
    block, feas = fixed_setup(tmp_path, dcfg, inputs=BIG)
    changed = {**block, "sha256": "0" * 64}
    with pytest.raises(SystemExit, match="refused: the SHA-256"):
        rd.check_fixed(changed, feas, tmp_path, dcfg)
    ok = rd.check_fixed({**changed, "author_decision": "re-serialised by hand"}, feas, tmp_path, dcfg)
    assert ok["pinned_sha256"] == "0" * 64 and ok["feasibility_sha256"] == hashlib.sha256(feas.read_bytes()).hexdigest()
    assert "does not match" in capsys.readouterr().out
    # No rho within the budget: the run stops, and an author's decision chooses rho; q and the mode stay the rules'.
    slow = {**BIG, "E_U": 10**9, "E_WCC": 10**9}
    assert crawl.rules(slow, dcfg)["rho"] is None
    block, feas = fixed_setup(tmp_path, dcfg, inputs=slow, rho=0.05)
    with pytest.raises(SystemExit, match="stopped"):
        rd.check_fixed(block, feas, tmp_path, dcfg)
    decided = {**block, "author_decision": "no rho within 12 hours; 0.05 on 32 workers"}
    assert rd.check_fixed(decided, feas, tmp_path, dcfg)["rho"] == Fraction(1, 20)
    with pytest.raises(SystemExit, match="differ from the values that the rules"):
        rd.check_fixed({**decided, "q": 0.05}, feas, tmp_path, dcfg)


# The stop-only decision of the gate B amendment (revision section 13, decided on 9 November 2026): an author's
# decision that passes the stop by few_capped_allowance_in_edges and nothing else.
STOP_ONLY = {"author_decision": "too few capped allowance in-edges; the test goes on (revision section 13)",
             "decision_covers": ["few_capped_allowance_in_edges"]}
FEW_IN = {**BIG, "allow_in_share": 0.0054}  # sets the stop flag few_capped_allowance_in_edges and no other
COVERS_IN = "; the author_decision covers only the stop flags few_capped_allowance_in_edges"


def test_a_stop_only_decision_passes_the_stop_it_lists_and_nothing_else(tmp_path, dcfg, capsys):
    # With decision_covers an author_decision passes the stop of protocol section 7 by the flags it lists. Every
    # other refusal of protocol section 8 stays as without a decision.
    assert list(crawl.rules(BIG, dcfg)["stop"]) == list(rd.STOP_FLAGS)  # the flags of section 7, as crawl names them
    rules = json.loads(json.dumps(rd._clean(crawl.rules(FEW_IN, dcfg))))
    assert [k for k, v in rules["stop"].items() if v] == ["few_capped_allowance_in_edges"]
    block, feas = fixed_setup(tmp_path, dcfg, inputs=FEW_IN)
    with pytest.raises(SystemExit, match="refused: the structure pilot stopped the run"):
        rd.check_fixed(block, feas, tmp_path, dcfg)
    ok = rd.check_fixed({**block, **STOP_ONLY}, feas, tmp_path, dcfg)
    assert (ok["rho"], ok["q"], ok["primary_mode"]) == (Fraction(1, 100), Fraction(1, 100), "out")
    assert (ok["author_decision"], ok["decision_covers"]) == (STOP_ONLY["author_decision"],
                                                              ["few_capped_allowance_in_edges"])
    assert ok["pinned_sha256"] == ok["feasibility_sha256"] == block["sha256"]
    # The object as 'Protocol fixed' holds it (a JSON list) reads back the same.
    assert rd.protocol_fixed(protocol_copy(tmp_path / "f.md", {**block, **STOP_ONLY})) == {**block, **STOP_ONLY}
    # rho, q and the mode are still those of the rules.
    for bad in ({"rho": 0.02}, {"q": 0.05}, {"primary_mode": "both"}):
        with pytest.raises(SystemExit, match="differ from the values that the rules"):
            rd.check_fixed({**block, **STOP_ONLY, **bad}, feas, tmp_path, dcfg)
    # Without decision_covers the decision keeps its meaning, and the result lists no flags.
    assert rd.check_fixed({**block, "author_decision": "go on"}, feas, tmp_path, dcfg)["decision_covers"] is None

    # A stop flag that decision_covers does not list refuses: as the pilot recorded it ...
    both = {**STOP_ONLY, "decision_covers": ["few_capped_allowance_in_edges", "few_capped_allowance_edges"]}
    block, feas = fixed_setup(tmp_path, dcfg, inputs={**FEW_IN, "allow_capped_edges": 100})
    with pytest.raises(SystemExit, match=r"^refused: the structure pilot stopped the run by stop flags that "
                                         r"decision_covers does not list \(few_capped_allowance_edges\)" + COVERS_IN
                                         + "$"):
        rd.check_fixed({**block, **STOP_ONLY}, feas, tmp_path, dcfg)
    assert rd.check_fixed({**block, **both}, feas, tmp_path, dcfg)["decision_covers"] == both["decision_covers"]
    stray = {"rules": {**rules, "stop": {**rules["stop"], "few_capped_allowance_edges": True}}}
    block, feas = fixed_setup(tmp_path, dcfg, stray, inputs=FEW_IN)
    with pytest.raises(SystemExit, match=r"does not list \(few_capped_allowance_edges\)"):
        rd.check_fixed({**block, **STOP_ONLY}, feas, tmp_path, dcfg)
    with pytest.raises(SystemExit, match="refused: the rules of this code give other values"):
        rd.check_fixed({**block, **both}, feas, tmp_path, dcfg)
    # ... and as the rules set it from the pilot's own counts, which its rule inputs hide.
    block, feas = fixed_setup(tmp_path, dcfg, {"layers": {"allow_capped": {"edges": 4000}}}, inputs=FEW_IN)
    with pytest.raises(SystemExit, match=r"does not list \(few_capped_allowance_edges\)"):
        rd.check_fixed({**block, **STOP_ONLY}, feas, tmp_path, dcfg)
    with pytest.raises(SystemExit, match="refused: the structure pilot records no rule inputs, or rule inputs"):
        rd.check_fixed({**block, **both}, feas, tmp_path, dcfg)
    assert rd.check_fixed({**block, "author_decision": "go on"}, feas, tmp_path, dcfg)["q"] == Fraction(1, 100)
    # A pilot that records no stop flags, or no counts for them, cannot be compared with the list.
    no_flags = {k: v for k, v in rules.items() if k != "stop"}
    for change in ({"rules": no_flags}, {"capped_allowance_in_edge_share": None}):
        block, feas = fixed_setup(tmp_path, dcfg, change, inputs=FEW_IN)
        with pytest.raises(SystemExit, match="refused: the structure pilot records no stop flags or no counts"):
            rd.check_fixed({**block, **STOP_ONLY}, feas, tmp_path, dcfg)
        assert rd.check_fixed({**block, "author_decision": "go on"}, feas, tmp_path, dcfg)["q"] == Fraction(1, 100)
    # No rho within the budget: the author chooses rho only when decision_covers lists no_rho_within_budget.
    block, feas = fixed_setup(tmp_path, dcfg, inputs={**BIG, "E_U": 10**9, "E_WCC": 10**9}, rho=0.05)
    rho_only = {**STOP_ONLY, "decision_covers": ["no_rho_within_budget"]}
    assert rd.check_fixed({**block, **rho_only}, feas, tmp_path, dcfg)["rho"] == Fraction(1, 20)
    with pytest.raises(SystemExit, match=r"does not list \(no_rho_within_budget\)"):
        rd.check_fixed({**block, **STOP_ONLY}, feas, tmp_path, dcfg)

    # The pinned hash, the committed files, the discovery settings, the rule inputs and the code of the pilot are
    # checked as without a decision; a decision without decision_covers passes each of them.
    block, feas = fixed_setup(tmp_path, dcfg, inputs=FEW_IN)
    with pytest.raises(SystemExit, match="^refused: the SHA-256 in 'Protocol fixed' does not match "
                                         f"data/discovery/feasibility_t1.json{COVERS_IN}$"):
        rd.check_fixed({**block, **STOP_ONLY, "sha256": "0" * 64}, feas, tmp_path, dcfg)
    assert rd.check_fixed({**block, "author_decision": "go on", "sha256": "0" * 64}, feas, tmp_path,
                          dcfg)["pinned_sha256"] == "0" * 64
    assert "does not match" in capsys.readouterr().out
    dirty = {"code": {"head": "abc123",
                      "committed": {**{rel: True for rel in rd.COMMITTED}, "scripts/crawl.py": False}}}
    for change, start in (({"code": None}, "the structure pilot did not run on committed files (no record)"),
                          (dirty, "the structure pilot did not run on committed files (scripts/crawl.py)"),
                          ({"discovery_config": {**dcfg, "runtime_budget_hours": 24}}, "the discovery settings differ"),
                          ({"rule_inputs": {**FEW_IN, "U": 99_999}}, "the structure pilot records no rule inputs"),
                          ({"rules": {**rules, "projected_hours": {}}}, "the rules of this code give other values")):
        block, feas = fixed_setup(tmp_path, dcfg, change, inputs=FEW_IN)
        with pytest.raises(SystemExit) as refused:
            rd.check_fixed({**block, **STOP_ONLY}, feas, tmp_path, dcfg)
        text = str(refused.value)
        assert text.startswith(f"refused: {start}") and text.endswith(COVERS_IN), text
        assert rd.check_fixed({**block, "author_decision": "go on"}, feas, tmp_path, dcfg)["decision_covers"] is None

    # decision_covers goes only with an author_decision, as a non-empty list of distinct stop flags of section 7;
    # any other key still refuses.
    block, feas = fixed_setup(tmp_path, dcfg, inputs=FEW_IN)
    for alone in ({}, {"author_decision": None}):
        with pytest.raises(SystemExit, match="refused: decision_covers goes only with an author_decision"):
            rd.check_fixed({**block, **alone, "decision_covers": ["few_capped_allowance_in_edges"]}, feas, tmp_path,
                           dcfg)
    for bad in (["few_capped_allowance_share"], ["few_capped_allowance_in_edges", "stopped"], [], None,
                "few_capped_allowance_in_edges", ["few_capped_allowance_in_edges"] * 2, [7]):
        with pytest.raises(SystemExit, match="refused: decision_covers must be a non-empty list of distinct stop "
                                             "flags of protocol section 7"):
            rd.check_fixed({**block, **STOP_ONLY, "decision_covers": bad}, feas, tmp_path, dcfg)
    with pytest.raises(SystemExit, match=r"refused: 'Protocol fixed' lacks \[\] or has unknown keys \['covers'\]"):
        rd.check_fixed({**block, **STOP_ONLY, "covers": ["few_capped_allowance_edges"]}, feas, tmp_path, dcfg)


def test_main_run_refuses_without_a_fixed_protocol(tmp_path, monkeypatch, dcfg):
    with pytest.raises(SystemExit, match="Protocol fixed"):
        rd.check_fixed(rd.protocol_fixed(protocol_copy(tmp_path / "p.md")))
    # The block documented in run_discovery.py is the format the parser reads.
    documented = textwrap.dedent("    ```json" + rd.__doc__.split("```json", 1)[1].split("```", 1)[0] + "```")
    doc = tmp_path / "documented.md"
    doc.write_text("## Protocol fixed\n\n" + documented + "\n", encoding="utf-8")
    assert set(rd.protocol_fixed(doc)) == set(rd.FIXED_KEYS)
    block, feas = fixed_setup(tmp_path, dcfg)
    parsed = rd.protocol_fixed(protocol_copy(tmp_path / "f.md", block))
    assert parsed == block
    ok = rd.check_fixed(parsed, feas, tmp_path, dcfg)
    assert (ok["rho"], ok["q"], ok["primary_mode"]) == (Fraction(1, 100), Fraction(1, 20), "out")
    for bad in ({"sha256": "0" * 64}, {"U": 6}, {"rho": 0.02}, {"q": 0.01}, {"primary_mode": "both"},
                {"feasibility": "elsewhere.json"}, {"date": "9 November"}, {"extra": 1}):
        with pytest.raises(SystemExit, match="refused"):
            rd.check_fixed({**block, **bad}, feas, tmp_path, dcfg)
    del block["date"]
    with pytest.raises(SystemExit, match="refused"):
        rd.check_fixed(block, feas, tmp_path, dcfg)
    # The pilot must have run on committed files, with the discovery settings of the main run.
    # A record that lacks a file of COMMITTED counts that file as not committed.
    partial = {rel: True for rel in rd.COMMITTED if rel != "scripts/stats.py"}
    for change in ({"code": {"head": "abc123", "committed": {"scripts/crawl.py": False, "scripts/common.py": True}}},
                   {"code": {"head": "abc123", "committed": partial}}, {"code": None}):
        block, feas = fixed_setup(tmp_path, dcfg, change)
        with pytest.raises(SystemExit, match="refused: the structure pilot did not run on committed files"):
            rd.check_fixed(block, feas, tmp_path, dcfg)
    block, feas = fixed_setup(tmp_path, dcfg)
    for other in ({**dcfg, "runtime_budget_hours": 24}, None):
        with pytest.raises(SystemExit, match="refused: the discovery settings differ"):
            rd.check_fixed(block, feas, tmp_path, other)
    # A stopped pilot or a pilot on other files goes on only with an author decision, and then with the values
    # of the rules all the same.
    block, feas = fixed_setup(tmp_path, dcfg, stopped=True)
    with pytest.raises(SystemExit, match="stopped"):
        rd.check_fixed(block, feas, tmp_path, dcfg)
    block, feas = fixed_setup(tmp_path, dcfg, {"code": None}, stopped=True, author_decision="few edges, run anyway")
    ok = rd.check_fixed(block, feas, tmp_path, dcfg)
    assert (ok["rho"], ok["q"], ok["primary_mode"], ok["author_decision"]) == (
        Fraction(1, 100), Fraction(1, 20), "out", "few edges, run anyway")
    for bad in ({"rho": 0.1}, {"q": 0.01}, {"primary_mode": "both"}):
        with pytest.raises(SystemExit, match="differ from the values that the rules"):
            rd.check_fixed({**block, **bad}, feas, tmp_path, dcfg)

    # The commit check: any file with local changes, or never committed, refuses the run.
    calls = []

    def git(*args, root=None):
        calls.append(args)
        if args[0] == "status":
            return " M docs/discovery_protocol.md" if args[-1] == "docs/discovery_protocol.md" else ""
        return "abc123"

    monkeypatch.setattr(rd, "_git", git)
    with pytest.raises(SystemExit, match="refused: not committed.*discovery_protocol.md"):
        rd.committed()
    monkeypatch.setattr(rd, "_git", lambda *args, root=None: "" if args[0] == "status" else "abc123")
    state = rd.committed()
    assert state["head"] == "abc123" and set(state["sha256"]) == set(rd.COMMITTED)
    assert {"scripts/crawl.py", "scripts/run_discovery.py", "scripts/scoring.py", "docs/discovery_protocol.md",
            "docs/revision_contract_graph.md", "config/overlay_contract12m.yaml",
            "config/contract_reputation.yaml"} <= set(rd.COMMITTED)  # the base file holds the solver and bootstrap


def test_the_script_refuses_a_main_run_and_other_variants(tmp_path, monkeypatch):
    with pytest.raises(SystemExit, match="contract-graph variant"):
        rd.main(["--window", "t1", "--feasibility"])  # this process runs the registered variant
    monkeypatch.setattr(common, "CONTRACT_GRAPH", True)
    monkeypatch.setattr(rd, "PROTOCOL", protocol_copy(tmp_path / "p.md"))
    with pytest.raises(SystemExit, match="refused: .*Protocol fixed"):
        rd.main(["--window", "tobs", "--workers", "2"])
    with pytest.raises(SystemExit, match="t1 only"):
        rd.main(["--window", "tobs", "--feasibility"])
    # Run as a script it selects the contract-graph variant itself.
    out = run_py("", variant=None, args=["scripts/run_discovery.py", "--window", "tobs", "--feasibility"])
    assert out.returncode != 0 and "t1 only" in out.stderr


INFLOW_UNTYPED = 1234.5


def write_interface(frame: pd.DataFrame, stem: Path, columns: dict[str, str]) -> None:
    """``frame`` written as the gate B stem ``stem`` with exactly ``columns`` (the arrow types of the INTERFACE of
    tests/c12_world.py, which the download step writes)."""
    common.write_parts(pa.Table.from_pandas(frame[list(columns)], schema=c12_world.arrow_schema(columns),
                                            preserve_index=False), stem)


def gate_b_tables(folder: Path, tag: str, n: int = 100, seed: int = 5, isolated: int = 0) -> np.ndarray:
    """Synthetic gate B tables (interface 4) with the columns and arrow types of the INTERFACE (c12_world.INTERFACE)
    and node ids 100, 103, ... in address order: nodes with the four flags; the capped allowance pairs and the
    transfer pairs (with the slope-sensitivity weights at T_obs) and the uncapped allowance pairs, a superset of the
    capped ones; importance with the address of each row, three typed contracts outside G (id -1), every row with a
    positive I_T or I_A and N_T <= I_T, N_A <= I_A; the one-row inflow table. ``isolated`` nodes without a pair follow
    the others (their ids and addresses continue the sequence); they are in G but in no union pair. Returns the ids."""
    g = random_graph(n, 5 * n, seed)
    rng = np.random.default_rng(seed)
    more = np.random.default_rng(seed + 1000)  # the columns and isolated nodes beyond the first version's draws
    m = n + isolated
    ids = 100 + 3 * np.arange(m)
    nodes = pd.DataFrame({"id": ids, "address": list(addresses(m)),
                          "is_cohort": np.concatenate([rng.random(n) < 0.2, more.random(isolated) < 0.2])})
    for flag in ("is_cohort_t1", "is_spender_w0", "is_spender_w1"):
        nodes[flag] = more.random(m) < 0.2
    write_interface(nodes, folder / "nodes", c12_world.INTERFACE["nodes"])
    tobs = tag == "tobs"
    for name, lay, count, weight in (("allow", g.allow, "n_tokens", "w_er"),
                                     ("transfer", g.transfer, "n_transfers", "w_awp")):
        f = pd.DataFrame({"src": ids[lay.src], "dst": ids[lay.dst], count: 1, **lay.weights})
        if tobs:
            f[f"{weight}_b10x"] = f[weight] * more.uniform(1.0, 1.5, len(f))
            f[f"{weight}_b01x"] = f[weight] * more.uniform(0.5, 1.0, len(f))
        write_interface(f, folder / f"{name}_pairs_{tag}", c12_world.INTERFACE[f"{name}_pairs_{tag}"])
        if name == "allow":
            # every capped pair at no lower weights (usd_allow >= usd_eff), and pairs only the uncapped layer holds
            have = set(zip(lay.src.tolist(), lay.dst.tolist()))
            extra = sorted({(int(a), int(b)) for a, b in more.integers(0, n, (40, 2)) if (a, b) not in have})[:10]
            k = len(f)
            unc = pd.DataFrame({"src": f["src"], "dst": f["dst"], "n_tokens": 1 + more.integers(0, 2, k),
                                "w_er": f["w_er"] * more.uniform(1.0, 2.0, k),
                                "w_raw": f["w_raw"] * more.uniform(1.0, 4.0, k), "max_sig": f["max_sig"]})
            unc = pd.concat([unc, pd.DataFrame({"src": ids[[a for a, _ in extra]], "dst": ids[[b for _, b in extra]],
                                                "n_tokens": 1, "w_er": more.lognormal(size=len(extra)),
                                                "w_raw": more.lognormal(size=len(extra)),
                                                "max_sig": more.uniform(0.01, 1.0, len(extra))})], ignore_index=True)
            write_interface(unc.sort_values(["src", "dst"], ignore_index=True), folder / f"allow_pairs_uncapped_{tag}",
                            c12_world.INTERFACE[f"allow_pairs_uncapped_{tag}"])
    rows = np.concatenate([rng.choice(ids[:n], int(0.9 * n), replace=False), [-1, -1, -1]])  # three outside G
    vals = {k: np.where(rng.random(rows.size) < 0.6, rng.lognormal(size=rows.size), 0.0) for k in ("i_t", "i_a")}
    none = (vals["i_t"] == 0) & (vals["i_a"] == 0)
    vals["i_t"][none] = rng.lognormal(size=int(none.sum()))
    vals["i_t"][-1] = 50.0  # a contract outside G among the largest
    vals.update(n_t=np.floor(vals["i_t"]).astype(np.int64), n_a=np.floor(vals["i_a"]).astype(np.int64))
    by_id = dict(zip(ids.tolist(), nodes["address"]))
    outside = iter(c12_world.outside(j) for j in range(3))
    address = [by_id[i] if i >= 0 else next(outside) for i in rows.tolist()]
    write_interface(pd.DataFrame({"id": rows, "address": address, **vals}), folder / f"importance_{tag}",
                    c12_world.INTERFACE[f"importance_{tag}"])
    write_interface(pd.DataFrame({"usd": [INFLOW_UNTYPED]}), folder / f"inflow_untyped_{tag}",
                    c12_world.INTERFACE[f"inflow_untyped_{tag}"])
    return ids


def strings(obj) -> list[str]:
    """Every string value and key of a JSON object."""
    if isinstance(obj, dict):
        return [*obj.keys(), *(x for v in obj.values() for x in strings(v))]
    if isinstance(obj, list):
        return [x for v in obj for x in strings(v)]
    return [obj] if isinstance(obj, str) else []


MAIN_FIXED = {"date": "2026-11-09", "rho": Fraction(1, 10), "q": Fraction(1, 20), "primary_mode": "out",
              "author_decision": None, "feasibility_sha256": "0" * 64}
ISOLATED = 3  # nodes of G without a pair (contract members outside the graph, protocol section 8)


def main_cfg(contract_cfg: dict) -> dict:
    cfg = json.loads(json.dumps(contract_cfg))
    cfg["discovery"].update(n_seeds=4, rho_sensitivity={"divisor": 4, "seeds": 2}, min_hot=3)
    return cfg


@pytest.mark.parametrize("tag, mode", [("t1", "out"), ("t1", "both"), ("tobs", "out"), ("tobs", "both")])
def test_a_main_run_on_synthetic_tables(tmp_path, monkeypatch, contract_cfg, tag, mode):
    import graphs

    gate_b_tables(tmp_path / "in", tag, isolated=ISOLATED)
    monkeypatch.setattr(graphs, "EXPORT", tmp_path / "in")
    monkeypatch.setattr(common, "GRAPH", tmp_path / "in")
    monkeypatch.setattr(rd, "DISC", tmp_path / "out")
    fixed = {**MAIN_FIXED, **STOP_ONLY} if mode == "both" else MAIN_FIXED
    path = rd.run_window(tag, mode, fixed, {"head": "abc"}, main_cfg(contract_cfg), workers=1)

    def no_nan(token):
        raise AssertionError(f"{token} in the output")

    out = json.loads(path.read_text(encoding="utf-8"), parse_constant=no_nan)
    # The protocol record names the author's decision and the stop flags it covers (null without decision_covers).
    assert (out["protocol"]["author_decision"], out["protocol"]["decision_covers"]) == (
        fixed["author_decision"], fixed.get("decision_covers"))
    # D23: |G| (every row of nodes, the isolated nodes included) under its own key; sizes.graph.nodes stays the
    # bow-tie's count of the contracts with a union pair, and no size of the bow-tie depends on the isolated nodes.
    graph = out["sizes"]["graph"]
    g = graphs.load_graphs(tag)
    full, _ = rd.full_graph(graphs.load_nodes(), g.allow, g.transfer)
    bt = crawl.bow_tie(full.n, full.union_src, full.union_dst).sizes()
    assert graph["g_nodes"] == full.n == len(graphs.load_nodes()) == 100 + ISOLATED
    assert graph["nodes"] == bt["nodes"] < 100 + ISOLATED and {k: graph[k] for k in bt} == bt
    gate_b_tables(tmp_path / "plain", tag)
    monkeypatch.setattr(graphs, "EXPORT", tmp_path / "plain")
    monkeypatch.setattr(common, "GRAPH", tmp_path / "plain")
    assert rd.graph_sizes(tag) == bt
    monkeypatch.setattr(graphs, "EXPORT", tmp_path / "in")
    monkeypatch.setattr(common, "GRAPH", tmp_path / "in")
    assert out["invariants"]["max_final_diff"] < rd.FINAL_TOLERANCE
    assert len(out["seeds"]) == 4 and out["is_primary"] == (mode == "out")
    assert out["protocol"]["bootstrap"] == {"resamples": 400, "seed": 42}  # protocol section 6
    assert out["protocol"]["solver"] == {"damping": 0.85, "tol": 1e-8, "max_iter": 300}
    assert ("rho_quarter" in out["fixed_order"]["5_sensitivities"]) == (mode == "out")
    n = out["sizes"]["universe"]["U"]
    for h, by_ordering in out["auc"].items():
        best = by_ordering["ref_ideal"]["x=0.1"]["auc"]
        for o in crawl.ORDERINGS:
            rec = by_ordering[o]["x=0.1"]
            if rec["auc"] is not None:
                assert rec["auc"] <= best + 1e-12 and len(rec["per_seed"]) == 4, (h, o)
        assert by_ordering["random_curve"]["x=0.1"] == pytest.approx(crawl.random_auc(n, 0.1))
    # Only T_obs in the primary mode decides; the other files carry the same contrasts without a verdict: no V-code,
    # no sentence, only which intervals lie above and below 0 (protocol section 6).
    decides = tag == "tobs" and mode == "out"
    assert out["decides"] is decides
    for col in ("i_t", "i_a"):
        dec = out["decision"][col]
        assert dec["hot_set"] == f"{col}@q" and dec["D1"]["a"] == "cpr_l50" and dec["D1"]["b"] == "bfs"
        assert dec["D2"]["b"] == "ib_u"
        if decides:
            assert dec["verdict"] in ("V1", "V2", "V3") and "above_zero" not in dec
        else:
            assert not {"verdict", "pattern", "extra", "descriptive"} & set(dec)
            assert dec["above_zero"] == [k for k in ("D1", "D2") if dec[k]["lo"] is not None and dec[k]["lo"] > 0]
            assert dec["below_zero"] == [k for k in ("D1", "D2") if dec[k]["hi"] is not None and dec[k]["hi"] < 0]
            assert not any(v in ("V1", "V2", "V3") for v in strings(dec))
    text = strings(out)
    if decides:
        assert out["decision"]["statements"] and "note" not in out["decision"]
        assert any(rd.LEAD in t for t in text)
    else:
        assert out["decision"]["statements"] == [] and out["decision"]["note"] == rd.NOT_DECIDING
        assert not any(rd.LEAD in t or "reached them sooner" in t or "descriptive only" in t for t in text)

    # Coverage over every row of importance, those outside G (id -1) included.
    cov = out["diagnostics"]["coverage"]
    imp = common.read_parts(tmp_path / "in" / f"importance_{tag}")
    assert (cov["contracts"], cov["outside_g"], cov["inflow_untyped_usd"]) == (len(imp), 3, INFLOW_UNTYPED)
    for col in ("i_t", "i_a"):
        c = cov[col]
        assert sum(c["share_by_part"].values()) == pytest.approx(1.0)
        assert c["share_by_part"]["outside_g"] == pytest.approx(imp.loc[imp["id"] == -1, col].sum() / imp[col].sum())
        u = (c["share_by_part"]["scc"] + c["share_by_part"]["out"]) if mode == "out" else None
        if u is not None:
            assert c["share_U"] == pytest.approx(u)
        assert c["share_U"] <= 1 - c["share_by_part"]["outside_g"] + 1e-12
        assert c["top_1pct"]["rows"] == math.ceil(len(imp) / 100)
    # The largest I_T is outside G: the top 1% (one row) lies outside U.
    assert cov["i_t"]["top_1pct"]["share_in_U"] == 0.0
    parts = sorted((tmp_path / "out").glob(f"discovery_{tag}_{mode}_hot_visits*"))
    visits = pd.concat([pd.read_parquet(p) for p in parts])
    crawls = visits[visits["seed"] >= 0].groupby(["ordering", "rho"]).size()
    assert set(crawls.index.get_level_values(0)) == set(crawl.ORDERINGS)
    assert (visits["visit_index"] >= 1).all() and (visits["visit_index"] <= n).all()


# The commit whose run_discovery.py wrote the structure pilot that 'Protocol fixed' pins: the amendment of
# 9 November 2026 (revision section 13), after which job 31, job 35 and the pilot ran again. The pilot records it as
# its HEAD. Its run_window is still that of the gate A commit d39775c.
PILOT_CODE = "caf97c3"
# The definitions of run_discovery.py that gate B changes against PILOT_CODE: run_window (D23, sizes.graph.g_nodes)
# and, for the stop-only decision of the gate B amendment (decision_covers in 'Protocol fixed'), check_fixed,
# match_pilot and the new constant STOP_FLAGS. The pilot calls none of them.
GATE_B_CHANGED = ("run_window", "check_fixed", "match_pilot")
GATE_B_ADDED = ("STOP_FLAGS",)


@pytest.fixture(scope="module")
def rd_base(tmp_path_factory):
    """run_discovery.py of PILOT_CODE (caf97c3) as a module of its own, and its source (the scoring_base pattern;
    put in sys.modules as rd_base, since its dataclasses look their module up); its import puts its own folder first
    on sys.path, which is undone."""
    out = subprocess.run(["git", "show", f"{PILOT_CODE}:./scripts/run_discovery.py"], cwd=EXPERIMENTS,
                         capture_output=True)
    if out.returncode != 0:
        pytest.skip(f"commit {PILOT_CODE} is not available")
    path = tmp_path_factory.mktemp("rd_base") / "rd_base.py"
    path.write_bytes(out.stdout)
    saved = list(sys.path)
    spec = importlib.util.spec_from_file_location("rd_base", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["rd_base"] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path[:] = saved
    yield module, out.stdout.decode("utf-8")
    sys.modules.pop("rd_base", None)


def definitions(src: str) -> list[tuple[str, str]]:
    """(name, AST dump) of every top-level statement of a module, docstrings removed (design_tests.md 2.5 without
    the flags); a statement that defines no name is named by its first line."""
    tree = ast.parse(src)
    out = []
    for node in tree.body:
        for sub in ast.walk(node):
            if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and sub.body and isinstance(
                    sub.body[0], ast.Expr) and isinstance(sub.body[0].value, ast.Constant) and isinstance(
                    sub.body[0].value.value, str):
                sub.body = sub.body[1:] or [ast.Pass()]
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            continue  # the module docstring
        out.append((getattr(node, "name", None) or ast.unparse(node).splitlines()[0][:80], ast.dump(node)))
    return out


def without_times(obj: dict, disc: Path) -> dict:
    """A main-run output without its clock (created_at, seconds, runs[*].seconds) and with its output folder (named
    in the paths it reports) written <DISC>."""

    def paths(v):
        if isinstance(v, dict):
            return {k: paths(x) for k, x in v.items()}
        if isinstance(v, list):
            return [paths(x) for x in v]
        return v.replace(str(disc), "<DISC>") if isinstance(v, str) else v

    obj = paths(json.loads(json.dumps(obj)))
    obj.pop("created_at", None)
    obj.pop("seconds", None)
    for run in (obj.get("runs") or {}).values():
        run.pop("seconds", None)
    return obj


def test_run_discovery_changes_only_the_graph_node_count(tmp_path, monkeypatch, contract_cfg, rd_base):
    # X2 (D23): on the same gate B tables (with isolated nodes) the main run of PILOT_CODE (whose run_window is that
    # of d39775c) and of this tree write the same parquet parts and the same output but for two more keys,
    # sizes.graph.g_nodes and protocol.decision_covers (null here). Every top-level definition of run_discovery.py
    # outside GATE_B_CHANGED and GATE_B_ADDED, and its COMMITTED, are those of PILOT_CODE, the code of the pilot
    # that 'Protocol fixed' pins, so that pilot stays valid. check_fixed, match_pilot and STOP_FLAGS differ for the
    # stop-only decision of the gate B amendment: an author_decision with decision_covers passes only the stop flags
    # it lists, and every other refusal of protocol section 8 stays.
    import graphs

    base, src = rd_base
    gate_b_tables(tmp_path / "in", "tobs", isolated=ISOLATED)
    monkeypatch.setattr(graphs, "EXPORT", tmp_path / "in")
    monkeypatch.setattr(common, "GRAPH", tmp_path / "in")
    monkeypatch.setattr(rd, "DISC", tmp_path / "new")
    monkeypatch.setattr(base, "DISC", tmp_path / "old")
    cfg = main_cfg(contract_cfg)
    new = without_times(json.loads(rd.run_window("tobs", "out", MAIN_FIXED, {"head": "abc"}, cfg, workers=1)
                                   .read_text(encoding="utf-8")), tmp_path / "new")
    old = without_times(json.loads(base.run_window("tobs", "out", MAIN_FIXED, {"head": "abc"}, cfg, workers=1)
                                   .read_text(encoding="utf-8")), tmp_path / "old")
    assert set(new["sizes"]["graph"]) - set(old["sizes"]["graph"]) == {"g_nodes"}
    assert new["sizes"]["graph"].pop("g_nodes") == 100 + ISOLATED
    assert set(new["protocol"]) - set(old["protocol"]) == {"decision_covers"}
    assert new["protocol"].pop("decision_covers") is None
    assert new == old
    for part in ("hot_visits", "hot_sets"):
        stems = [tmp_path / d / f"discovery_tobs_out_{part}" for d in ("new", "old")]
        tables = [pa.concat_tables([pq.read_table(p) for p in common.part_paths(stem)]) for stem in stems]
        assert tables[0].equals(tables[1]), part
    current = (SCRIPTS / "run_discovery.py").read_text(encoding="utf-8")

    def name(d: tuple[str, str]) -> str:
        """The name of a definition; an assignment is named by its first line, 'NAME = ...'."""
        return d[0].split(" = ", 1)[0]

    def kept(text: str) -> list[tuple[str, str]]:
        return [d for d in definitions(text) if name(d) not in GATE_B_CHANGED + GATE_B_ADDED]

    assert kept(current) == kept(src)
    names = [name(d) for d in definitions(current)]
    assert [n for n in names if n not in GATE_B_ADDED] == [name(d) for d in definitions(src)]
    assert [n for n in names if n in GATE_B_ADDED] == list(GATE_B_ADDED)
    assert not {name(d) for d in definitions(src)} & set(GATE_B_ADDED)
    assert rd.COMMITTED == base.COMMITTED


def test_a_t1_graph_other_than_the_pilot_stops_the_run_before_any_crawl(tmp_path, monkeypatch, contract_cfg):
    import graphs

    gate_b_tables(tmp_path / "in", "t1")
    monkeypatch.setattr(graphs, "EXPORT", tmp_path / "in")
    monkeypatch.setattr(common, "GRAPH", tmp_path / "in")
    sizes = rd.graph_sizes("t1")
    fixed = {"date": "2026-11-09", "rho": Fraction(1, 10), "q": Fraction(1, 20), "primary_mode": "out",
             "author_decision": None, "feasibility_sha256": "0" * 64,
             "sizes": {k: sizes[k] for k in ("U", "E_U", "WCC", "E_WCC")}}
    assert rd.match_pilot(sizes, fixed) == {"U": True, "E_U": True, "WCC": True, "E_WCC": True}
    wrong = {**fixed, "sizes": {**fixed["sizes"], "E_U": sizes["E_U"] + 1}}
    with pytest.raises(SystemExit, match="refused: the t1 graph differs from the structure pilot"):
        rd.match_pilot(sizes, wrong)
    assert rd.match_pilot(sizes, {**wrong, "author_decision": "checked by hand"})["E_U"] is False
    # A stop-only decision (decision_covers) does not pass another t1 graph.
    assert rd.match_pilot(sizes, {**fixed, **STOP_ONLY}) == {"U": True, "E_U": True, "WCC": True, "E_WCC": True}
    with pytest.raises(SystemExit, match="refused: the t1 graph differs from the structure pilot: .*; the "
                                         "author_decision in 'Protocol fixed' covers only the stop flags "
                                         "few_capped_allowance_in_edges$"):
        rd.match_pilot(sizes, {**wrong, **STOP_ONLY})
    with pytest.raises(SystemExit, match="t1 graph differs"):  # a main run of t1 stops before its crawls
        rd.run_window("t1", "out", wrong, {"head": "abc"}, contract_cfg, workers=1)
    # main() compares the t1 graph first, also for a run of T_obs alone.
    ran = []
    monkeypatch.setattr(common, "CONTRACT_GRAPH", True)
    monkeypatch.setattr(common, "load_config", lambda: contract_cfg)
    monkeypatch.setattr(rd, "committed", lambda *args, **kwargs: {"head": "abc", "sha256": {}})
    monkeypatch.setattr(rd, "run_window", lambda tag, mode, *args: ran.append((tag, mode)))
    monkeypatch.setattr(rd, "check_fixed", lambda *args: wrong)
    with pytest.raises(SystemExit, match="t1 graph differs"):
        rd.main(["--window", "tobs"])
    monkeypatch.setattr(rd, "check_fixed", lambda *args: {**wrong, **STOP_ONLY})
    with pytest.raises(SystemExit, match="t1 graph differs.*covers only the stop flags"):
        rd.main(["--window", "tobs"])
    assert ran == []
    monkeypatch.setattr(rd, "check_fixed", lambda *args: fixed)
    assert rd.main(["--window", "tobs"]) == 0 and ran == [("tobs", "out"), ("tobs", "both")]


def test_importance_rows_and_the_inflow_table(tmp_path, monkeypatch):
    ids = np.array([100, 103, 106])
    good = pd.DataFrame({"id": [103, -1, -1, 100], "i_t": [1.0, 2.0, 0.0, 3.0], "i_a": [0.0, 1.0, 4.0, 0.0],
                         "n_t": 1, "n_a": 1})
    assert rd.importance_positions(ids, good).tolist() == [1, -1, -1, 0]
    for bad, match in (({"id": [103, 7, -1, 100]}, "lacks"), ({"id": [103, 103, -1, 100]}, "twice"),
                       ({"i_a": [0.0, -1.0, 4.0, 0.0]}, "non-negative")):
        with pytest.raises(SystemExit, match=match):
            rd.importance_positions(ids, good.assign(**bad))
    with pytest.raises(SystemExit, match="reserves"):
        rd.importance_positions(np.array([-1, 100, 103]), good)
    with pytest.raises(SystemExit, match="columns"):
        rd.importance_positions(ids, good.drop(columns="n_a"))
    # The top 1% holds exactly ceil(rows / 100) rows; rows tied at the cut share the slots left.
    member = np.array([True, False, True, False])
    assert rd.top_share(np.array([5.0, 9.0, 1.0, 0.5]), member, "0.25") == {
        "rows": 1, "share_in_U": 0.0, "tied_at_cut": 1, "slots_at_cut": 1}
    got = rd.top_share(np.array([9.0, 4.0, 4.0, 4.0]), member, "0.5")
    assert got["rows"] == 2 and got["share_in_U"] == pytest.approx((1 + 1 / 3) / 2) and got["tied_at_cut"] == 3
    flat = rd.top_share(np.array([3.0] * 150), np.arange(150) < 30, Fraction(1, 100))
    assert flat["rows"] == 2 and flat["share_in_U"] == pytest.approx(0.2)
    # inflow_untyped is one row with a column usd.
    monkeypatch.setattr(common, "GRAPH", tmp_path)
    common.write_parts(pd.DataFrame({"usd": [12.5]}), tmp_path / "inflow_untyped_t1")
    assert rd.read_inflow_untyped("t1") == 12.5
    common.write_parts(pd.DataFrame({"usd": pd.Series([None], dtype="float64")}), tmp_path / "inflow_untyped_t1")
    assert rd.read_inflow_untyped("t1") == 0.0
    common.write_parts(pd.DataFrame({"usd": [1.0, 2.0]}), tmp_path / "inflow_untyped_t1")
    with pytest.raises(SystemExit, match="one row"):
        rd.read_inflow_untyped("t1")


def test_verdict_wording():
    up = {"lo": 0.01, "hi": 0.05}
    flat = {"lo": -0.01, "hi": 0.02}
    down = {"lo": -0.05, "hi": -0.01}
    assert rd.verdict(up, up, 40, 30)["verdict"] == "V1"
    assert rd.verdict(up, flat, 40, 30)["verdict"] == "V2"
    v = rd.verdict(up, down, 40, 30)
    assert v["verdict"] == "V2" and v["extra"] == ["A crawl ordered by the number of contract backlinks reached "
                                                   "them sooner."]
    v = rd.verdict(down, up, 40, 30)
    assert v["verdict"] == "V3" and v["extra"] == ["A breadth-first crawl reached them sooner."]
    assert rd.verdict(up, up, 29, 30)["descriptive"]
    lead = ("Ordered by C-PR on the contracts read so far, a crawl from a random contract of the giant strongly "
            "connected component")
    one = rd.statements({"i_t": rd.verdict(up, up, 40, 30), "i_a": rd.verdict(up, up, 50, 30)})
    assert one == [
        f"{lead} reached the contracts of the universe with the most user-account inflow and those with the most "
        "user-authorised value sooner than a breadth-first crawl and than a crawl ordered by the number of contract "
        "backlinks."]
    # Different verdicts are stated separately, and the weaker one answers the question of section 1.
    two = rd.statements({"i_t": rd.verdict(up, flat, 40, 30), "i_a": rd.verdict(flat, up, 50, 30)})
    assert two == [
        f"{lead} reached the contracts of the universe with the most user-account inflow sooner than a breadth-first "
        "crawl, but not sooner than a crawl ordered by the number of contract backlinks.",
        f"{lead} did not reach the contracts of the universe with the most user-authorised value sooner than a "
        "breadth-first crawl.",
        f"Over both importances, the weaker verdict: {lead} did not reach the contracts of the universe with the "
        "most user-account demand sooner than a breadth-first crawl."]
    # The same verdict with different added sentences is stated separately too, each with its own sentence.
    same = rd.statements({"i_t": rd.verdict(up, down, 40, 30), "i_a": rd.verdict(up, flat, 50, 30)})
    assert len(same) == 3 and same[0].endswith("A crawl ordered by the number of contract backlinks reached them "
                                                "sooner.")
    assert "user-account inflow" in same[0] and "user-authorised value" in same[1] and "reached them" not in same[1]
    assert same[2].startswith("Over both importances, the weaker verdict: ") and "but not sooner" in same[2]
    # An importance with too few hot contracts carries no verdict, and the question has no answer.
    part = rd.statements({"i_t": rd.verdict(up, up, 40, 30), "i_a": rd.verdict(up, up, 12, 30)})
    assert part == [f"{lead} reached the contracts of the universe with the most user-account inflow sooner than a "
                    "breadth-first crawl and than a crawl ordered by the number of contract backlinks.",
                    "Fewer than the minimum number of hot contracts for user-authorised value: descriptive only.",
                    rd.NO_ANSWER]


def test_the_secondary_share_is_the_other_share(dcfg):
    for q, other in ((Fraction(1, 100), Fraction(1, 20)), (Fraction(1, 20), Fraction(1, 100)),
                     (0.01, Fraction(1, 20)), (0.05, Fraction(1, 100)), ("0.05", Fraction(1, 100))):
        assert rd.secondary_share(q, dcfg) == other, q
