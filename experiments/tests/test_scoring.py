"""scoring.py against the wallet-reputation reference (pagerank.py, pagerank_variants.py, holdout.py)."""

from __future__ import annotations

import time
from dataclasses import dataclass

import numpy as np
import pandas as pd
import pytest
from conftest import load_reference

import scoring
from stats import PairedBootstrap, spearman

ATOL = 1e-12
OBS_END = pd.Timestamp("2026-06-30 23:59:59", tz="UTC")


@pytest.fixture(scope="module")
def ref():
    return load_reference("pagerank")


@pytest.fixture(scope="module")
def ref_variants():
    return load_reference("pagerank_variants")


@pytest.fixture(scope="module")
def decay(config):
    rep = config["reputation"]
    return {"k": float(rep["awp_decay_k"]), "t0": float(rep["awp_decay_t0_days"]), "b": float(rep["awp_value_b"])}


@dataclass
class World:
    """Random events on string addresses and the integer ids that stand for them."""

    to_id: dict[str, int]
    transfers: pd.DataFrame
    allowances: pd.DataFrame
    cohort: list[str]

    def ids(self, col: pd.Series) -> np.ndarray:
        return col.map(self.to_id).to_numpy(dtype=np.int64)

    def cohort_ids(self) -> np.ndarray:
        return np.asarray([self.to_id[w] for w in self.cohort], dtype=np.int64)


def make_world(seed: int, sparse_ids: bool = False, n_nodes: int = 70) -> World:
    rng = np.random.default_rng(seed)
    names = [f"0x{int(v):040x}" for v in rng.choice(10**12, size=n_nodes + 3, replace=False)]
    if sparse_ids:
        ids = np.unique(rng.integers(-(2**62), 2**62, size=4 * n_nodes))[: n_nodes + 3]
        ids = rng.permutation(ids)
    else:
        ids = rng.permutation(5 * n_nodes)[: n_nodes + 3]
    to_id = {name: int(i) for name, i in zip(names, ids)}
    graph_names = names[:n_nodes]  # the last three never appear in an event

    # Transfers: senders are a subset, so nodes that only receive are dangling.
    n_t = 900
    src = rng.integers(0, int(0.7 * n_nodes), n_t)
    dst = rng.integers(0, n_nodes, n_t)
    loops = rng.random(n_t) < 0.05
    dst[loops] = src[loops]
    kind = rng.random(n_t)
    value = np.where(kind < 0.1, 0.0, np.where(kind < 0.5, rng.uniform(0, 3, n_t), 10 ** rng.uniform(15, 21, n_t)))
    seconds = rng.integers(0, 900 * 86400, n_t)
    transfers = pd.DataFrame(
        {
            "block_timestamp": OBS_END - pd.to_timedelta(seconds, unit="s"),
            "from_address": [graph_names[i] for i in src],
            "to_address": [graph_names[i] for i in dst],
            "value": value,
        }
    )

    # Latest positive allowances of (token, owner, spender); spenders are the first 25 nodes.
    n_a = 400
    owner = rng.integers(0, n_nodes, n_a)
    spender = rng.integers(0, 25, n_a)
    self_appr = rng.random(n_a) < 0.03
    owner[self_appr] = spender[self_appr]
    token = rng.integers(0, 5, n_a)
    a_value = np.where(rng.random(n_a) < 0.3, 1e30, 10 ** rng.uniform(0, 24, n_a))
    a_seconds = rng.integers(0, 900 * 86400, n_a)
    allowances = pd.DataFrame(
        {
            "token_address": [f"0xt{t}" for t in token],
            "owner": [graph_names[i] for i in owner],
            "spender": [graph_names[i] for i in spender],
            "value": a_value,
            "block_timestamp": OBS_END - pd.to_timedelta(a_seconds, unit="s"),
        }
    ).drop_duplicates(["token_address", "owner", "spender"], ignore_index=True)

    cohort = graph_names[:30] + names[n_nodes:]
    return World(to_id, transfers, allowances, cohort)


@pytest.fixture(scope="module", params=[False, True], ids=["dense_ids", "sparse_ids"])
def world(request) -> World:
    return make_world(11, sparse_ids=request.param)


def to_arrays(world: World, edges: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """A reference edge table (from_node, to_node, weight) on integer ids."""
    return world.ids(edges["from_node"]), world.ids(edges["to_node"]), edges["weight"].to_numpy(dtype=float)


def assert_same_scores(world: World, ref_scores: dict[str, float], mine: pd.Series) -> None:
    expected = pd.Series({world.to_id[k]: v for k, v in ref_scores.items()}, dtype=float).sort_index()
    assert mine.index.is_monotonic_increasing
    np.testing.assert_array_equal(mine.index.to_numpy(), expected.index.to_numpy())
    assert np.max(np.abs(mine.to_numpy() - expected.to_numpy()), initial=0.0) < ATOL


def assert_same_edges(world: World, ref_edges: pd.DataFrame, mine: pd.DataFrame, rtol: float = 1e-12) -> None:
    s, d, w = to_arrays(world, ref_edges)
    expected = pd.DataFrame({"src": s, "dst": d, "w": w}).sort_values(["src", "dst"], ignore_index=True)
    got = mine.sort_values(["src", "dst"], ignore_index=True)
    np.testing.assert_array_equal(got["src"].to_numpy(), expected["src"].to_numpy())
    np.testing.assert_array_equal(got["dst"].to_numpy(), expected["dst"].to_numpy())
    np.testing.assert_allclose(got["w"].to_numpy(), expected["w"].to_numpy(), rtol=rtol, atol=0)


def assert_same_activeness(world: World, ref_act: dict[str, float], mine: pd.Series) -> None:
    expected = pd.Series({world.to_id[k]: v for k, v in ref_act.items()}, dtype=float).sort_index()
    got = mine.sort_index()
    np.testing.assert_array_equal(got.index.to_numpy(), expected.index.to_numpy())
    np.testing.assert_allclose(got.to_numpy(), expected.to_numpy(), rtol=1e-12, atol=0)


# ---------------------------------------------------------------------------
# Decay, value transform and edge builders


def test_decay_and_value_transform_match_reference(ref, decay):
    rng = np.random.default_rng(3)
    ages = np.concatenate([rng.uniform(0, 1200, 500), [0.0, 180.0, 1e4]])
    x = np.concatenate([rng.uniform(-5, 5, 300), 10 ** rng.uniform(-3, 30, 200), [0.0, np.nan, 1e77]])
    np.testing.assert_array_equal(
        scoring.logistic_decay(ages, decay["k"], decay["t0"]),
        ref.logistic_time_decay(pd.Series(ages), decay["k"], decay["t0"]).to_numpy(),
    )
    np.testing.assert_array_equal(
        scoring.value_transform(x, decay["b"]), ref.value_transform(pd.Series(x), decay["b"]).to_numpy()
    )


def test_awp_edges_match_reference(ref, world, decay):
    t = world.transfers
    ref_edges, ref_act = ref.build_awp_paper_edges(t, OBS_END, decay["k"], decay["t0"], decay["b"])
    edges, act = scoring.awp_edges(
        world.ids(t["from_address"]),
        world.ids(t["to_address"]),
        t["value"],
        scoring.age_days(t["block_timestamp"], OBS_END),
        **decay,
    )
    assert_same_edges(world, ref_edges, edges)
    assert_same_activeness(world, ref_act, act)


def test_endorserank_edges_match_reference(ref, world, decay):
    a = world.allowances
    # Zero amounts add nothing to the edges and are left out of the activeness.
    zeros = a.sample(15, random_state=1).assign(value=0.0, token_address="0xt9")
    a = pd.concat([a, zeros], ignore_index=True)
    ref_edges, ref_act = ref.build_endorserank_vt_edges(a, OBS_END, decay["k"], decay["t0"], decay["b"])
    edges, act = scoring.endorserank_edges(
        world.ids(a["owner"]),
        world.ids(a["spender"]),
        a["value"],
        scoring.age_days(a["block_timestamp"], OBS_END),
        **decay,
    )
    assert_same_edges(world, ref_edges, edges)
    assert_same_activeness(world, ref_act, act)


def test_raw_layers_match_reference(ref, world, decay):
    a, t = world.allowances, world.transfers
    assert_same_edges(
        world,
        ref.build_endorserank_edges(a),
        scoring.allowance_layer_edges(world.ids(a["owner"]), world.ids(a["spender"]), a["value"]),
    )
    assert_same_edges(
        world,
        ref.build_awp_edges(t, OBS_END, decay["k"], decay["t0"]),
        scoring.transfer_layer_edges(
            world.ids(t["from_address"]),
            world.ids(t["to_address"]),
            t["value"],
            scoring.age_days(t["block_timestamp"], OBS_END),
            k=decay["k"],
            t0=decay["t0"],
        ),
    )


# ---------------------------------------------------------------------------
# Single-layer walks


@pytest.mark.parametrize("damping", [0.85, 0.95])
def test_weighted_pagerank_matches_reference(ref, world, decay, params, damping):
    p = {**params, "damping": damping}
    edges = ref.build_awp_edges(world.transfers, OBS_END, decay["k"], decay["t0"])
    ref_scores, ref_iter = ref.weighted_pagerank(edges, return_iterations=True, **p)
    mine, iterations = scoring.weighted_pagerank(*to_arrays(world, edges), **p)
    assert iterations == ref_iter
    assert_same_scores(world, ref_scores, mine)
    assert abs(mine.sum() - 1.0) < 1e-12


def test_duplicates_and_non_positive_weights(ref, world, params):
    edges = ref.build_endorserank_edges(world.allowances)
    s, d, w = to_arrays(world, edges)
    # Split every weight over two rows and add rows that must be ignored.
    junk = np.arange(5)
    s2 = np.concatenate([s, s, s[junk], s[junk]])
    d2 = np.concatenate([d, d, d[junk], d[junk]])
    w2 = np.concatenate([w * 0.25, w * 0.75, np.zeros(5), -np.ones(5)])
    expected, it1 = scoring.weighted_pagerank(s, d, w, **params)
    got, it2 = scoring.weighted_pagerank(s2, d2, w2, **params)
    assert it1 == it2
    np.testing.assert_array_equal(got.index, expected.index)
    assert np.max(np.abs(got.to_numpy() - expected.to_numpy())) < ATOL


def test_awp_pipeline_matches_reference(ref, world, decay, params):
    """AWP as published: edges kept around the cohort, restarts by sending activity over all transfers."""
    t = world.transfers
    ref_edges, ref_act = ref.build_awp_paper_edges(t, OBS_END, decay["k"], decay["t0"], decay["b"])
    ref_edges = ref.filter_subgraph_edges(ref_edges, set(world.cohort))
    ref_scores = ref.weighted_pagerank(ref_edges, teleport=ref_act or None, **params)

    edges, act = scoring.awp_edges(
        world.ids(t["from_address"]),
        world.ids(t["to_address"]),
        t["value"],
        scoring.age_days(t["block_timestamp"], OBS_END),
        **decay,
    )
    keep = scoring.touching(edges["src"], edges["dst"], world.cohort_ids())
    edges = edges[keep]
    mine, _ = scoring.weighted_pagerank(edges["src"], edges["dst"], edges["w"], teleport=act, **params)
    assert_same_scores(world, ref_scores, mine)
    # A plain dict works as the restart mapping too.
    mine_dict, _ = scoring.weighted_pagerank(
        edges["src"], edges["dst"], edges["w"], teleport=act.to_dict(), **params
    )
    assert_same_scores(world, ref_scores, mine_dict)


@pytest.mark.parametrize("activity_restarts", [False, True])
def test_endorserank_pipeline_matches_reference(ref, world, decay, params, activity_restarts):
    a = world.allowances
    ref_edges, ref_act = ref.build_endorserank_vt_edges(a, OBS_END, decay["k"], decay["t0"], decay["b"])
    ref_edges = ref.filter_subgraph_edges(ref_edges, set(world.cohort))
    ref_scores = ref.weighted_pagerank(
        ref_edges, teleport=(ref_act or None) if activity_restarts else None, **params
    )
    edges, act = scoring.endorserank_edges(
        world.ids(a["owner"]),
        world.ids(a["spender"]),
        a["value"],
        scoring.age_days(a["block_timestamp"], OBS_END),
        **decay,
    )
    edges = edges[scoring.touching(edges["src"], edges["dst"], world.cohort_ids())]
    mine, _ = scoring.weighted_pagerank(
        edges["src"], edges["dst"], edges["w"], teleport=act if activity_restarts else None, **params
    )
    assert_same_scores(world, ref_scores, mine)


def test_pair_table_input_matches_reference(ref, world, decay, params):
    """Pairs aggregated as 04_anchor_pairs.sql does give the AWP scores of the per-transfer path."""
    t = world.transfers
    sig = scoring.logistic_decay(scoring.age_days(t["block_timestamp"], OBS_END), decay["k"], decay["t0"])
    rows = pd.DataFrame(
        {
            "src": world.ids(t["from_address"]),
            "dst": world.ids(t["to_address"]),
            "awp": sig * scoring.value_transform(t["value"], decay["b"]),
            "sig": sig,
        }
    )
    pairs = rows.groupby(["src", "dst"], as_index=False).agg(w_awp=("awp", "sum"), max_sig=("sig", "max"))
    assert (pairs["w_awp"] == 0).any()  # pairs of zero-value transfers only: in the activeness, not the graph

    ref_edges, ref_act = ref.build_awp_paper_edges(t, OBS_END, decay["k"], decay["t0"], decay["b"])
    act = scoring.activeness(pairs["src"], pairs["dst"], pairs["max_sig"])
    assert_same_activeness(world, ref_act, act)
    ref_scores = ref.weighted_pagerank(ref_edges, teleport=ref_act, **params)
    mine, _ = scoring.weighted_pagerank(*scoring.layer_arrays(pairs, "w_awp"), teleport=act, **params)
    assert_same_scores(world, ref_scores, mine)


def test_teleport_without_mass_is_uniform(ref, world, decay, params):
    edges = ref.build_awp_edges(world.transfers, OBS_END, decay["k"], decay["t0"])
    outside = {world.cohort[-1]: 1.0}  # a wallet that no event touches
    ref_scores = ref.weighted_pagerank(edges, teleport=outside, **params)
    arrays = to_arrays(world, edges)
    mine, _ = scoring.weighted_pagerank(*arrays, teleport={world.to_id[k]: v for k, v in outside.items()}, **params)
    uniform, _ = scoring.weighted_pagerank(*arrays, **params)
    assert_same_scores(world, ref_scores, mine)
    np.testing.assert_array_equal(mine.to_numpy(), uniform.to_numpy())


def test_isolated_nodes_match_reference(ref, world, params):
    edges = ref.filter_subgraph_edges(ref.build_endorserank_edges(world.allowances), set(world.cohort))
    nodes = set(edges["from_node"]) | set(edges["to_node"])
    missing = {w for w in world.cohort if w not in nodes}
    assert missing
    ref_scores = ref.weighted_pagerank(edges, extra_nodes=missing, **params)
    mine, _ = scoring.weighted_pagerank(*to_arrays(world, edges), extra_nodes=world.cohort_ids(), **params)
    assert_same_scores(world, ref_scores, mine)
    cohort = scoring.scores_on(world.cohort_ids(), mine)
    assert (cohort > 0).all()


def test_scores_on_gives_zero_outside_the_graph(ref, world, params):
    edges = ref.filter_subgraph_edges(ref.build_endorserank_edges(world.allowances), set(world.cohort))
    ref_scores = ref.weighted_pagerank(edges, **params)
    mine, _ = scoring.weighted_pagerank(*to_arrays(world, edges), **params)
    got = scoring.scores_on(world.cohort_ids(), mine)
    expected = np.asarray([ref_scores.get(w, 0.0) for w in world.cohort])
    assert list(got.index) == list(world.cohort_ids())
    assert np.max(np.abs(got.to_numpy() - expected)) < ATOL
    assert (got.iloc[-3:] == 0).all()
    empty, iterations = scoring.weighted_pagerank([], [], [], extra_nodes=world.cohort_ids(), **params)
    assert empty.empty and iterations == 0
    assert (scoring.scores_on(world.cohort_ids(), empty) == 0).all()


# ---------------------------------------------------------------------------
# Coupled and seeded walks


def _layers(ref, world, decay):
    """The two C-PR layers kept around the cohort, as pagerank_variants builds them."""
    seed = set(world.cohort)
    er = ref.filter_subgraph_edges(ref.build_endorserank_edges(world.allowances), seed)
    awp = ref.filter_subgraph_edges(ref.build_awp_edges(world.transfers, OBS_END, decay["k"], decay["t0"]), seed)
    return er, awp


@pytest.mark.parametrize("lam", [0.25, 0.5, 0.75, 1.0, 0.0])
def test_coupled_matches_reference(ref, world, decay, params, lam):
    er, awp = _layers(ref, world, decay)
    ref_scores, ref_iter = ref.coupled_pagerank([(er, lam), (awp, 1.0 - lam)], return_iterations=True, **params)
    mine, iterations = scoring.coupled_pagerank(
        [(*to_arrays(world, er), lam), (*to_arrays(world, awp), 1.0 - lam)], **params
    )
    assert iterations == ref_iter
    assert_same_scores(world, ref_scores, mine)


@pytest.mark.parametrize("lam, layer", [(1.0, 0), (0.0, 1)])
def test_coupled_end_points_are_single_layer_walks(ref, world, decay, params, lam, layer):
    er, awp = _layers(ref, world, decay)
    alone = (er, awp)[layer]
    mine, _ = scoring.coupled_pagerank(
        [(*to_arrays(world, er), lam), (*to_arrays(world, awp), 1.0 - lam)], **params
    )
    single, _ = scoring.weighted_pagerank(*to_arrays(world, alone), **params)
    np.testing.assert_array_equal(mine.index, single.index)
    assert np.max(np.abs(mine.to_numpy() - single.to_numpy())) < ATOL
    assert_same_scores(world, ref.weighted_pagerank(alone, **params), mine)


def test_coupled_lambda_one_on_a_shared_node_set(params):
    """Both layers span the same nodes: lambda = 1 is the allowance walk, lambda = 0 the transfer walk."""
    rng = np.random.default_rng(5)
    nodes = rng.permutation(1000)[:40]
    layers = []
    for _ in range(2):
        src = np.concatenate([nodes, rng.choice(nodes, 300)])
        dst = np.concatenate([rng.choice(nodes, 40), rng.choice(nodes, 300)])
        layers.append((src, dst, 10 ** rng.uniform(0, 6, src.size)))
    allowance, transfer = layers
    for a in layers:
        assert set(a[0]) | set(a[1]) == set(nodes)

    def coupled(lam):
        return scoring.coupled_pagerank([(*allowance, lam), (*transfer, 1.0 - lam)], **params)[0]

    for lam, alone in ((1.0, allowance), (0.0, transfer)):
        single, _ = scoring.weighted_pagerank(*alone, **params)
        np.testing.assert_array_equal(coupled(lam).index, single.index)
        assert np.max(np.abs(coupled(lam).to_numpy() - single.to_numpy())) < ATOL
    mixed = coupled(0.5).to_numpy()
    assert np.max(np.abs(mixed - scoring.weighted_pagerank(*allowance, **params)[0].to_numpy())) > 1e-6


def test_hybrids_match_compute_hybrid_scores(ref, ref_variants, world, decay, config, params):
    er, awp = _layers(ref, world, decay)
    ref_scores, _ = ref_variants.compute_hybrid_scores(world.cohort, config, er, awp)
    er_arrays, awp_arrays = to_arrays(world, er), to_arrays(world, awp)
    cohort = world.cohort_ids()

    for method_id, lam in ref_variants.hybrid_lambda_map(config).items():
        full, _ = scoring.coupled_pagerank([(*er_arrays, lam), (*awp_arrays, 1.0 - lam)], **params)
        got = scoring.scores_on(cohort, full).to_numpy()
        expected = np.asarray([ref_scores[method_id][w] for w in world.cohort])
        assert np.max(np.abs(got - expected)) < ATOL, method_id

    allowance_alone, _ = scoring.weighted_pagerank(*er_arrays, **params)
    seeded, _ = scoring.seeded_pagerank(*awp_arrays, allowance_alone, **params)
    got = scoring.scores_on(cohort, seeded).to_numpy()
    expected = np.asarray([ref_scores[ref_variants.SEEDED_PR_ID][w] for w in world.cohort])
    assert np.max(np.abs(got - expected)) < ATOL
    # The full seeded walk, every transfer-layer node included.
    er_full = ref.weighted_pagerank(er, **params)
    assert_same_scores(world, ref.weighted_pagerank(awp, teleport=er_full, **params), seeded)


def test_seeded_without_allowance_mass_is_uniform(ref, world, decay, params):
    _, awp = _layers(ref, world, decay)
    awp_arrays = to_arrays(world, awp)
    nodes = set(awp["from_node"]) | set(awp["to_node"])
    outside = [w for w in world.to_id if w not in nodes]
    allowance = pd.Series(1.0 / len(outside), index=[world.to_id[w] for w in outside])
    seeded, _ = scoring.seeded_pagerank(*awp_arrays, allowance, **params)
    uniform, _ = scoring.weighted_pagerank(*awp_arrays, **params)
    np.testing.assert_array_equal(seeded.to_numpy(), uniform.to_numpy())
    assert_same_scores(
        world, ref.weighted_pagerank(awp, teleport={w: 1.0 / len(outside) for w in outside}, **params), seeded
    )
    empty, _ = scoring.seeded_pagerank(*awp_arrays, pd.Series(dtype=float), **params)
    np.testing.assert_array_equal(empty.to_numpy(), uniform.to_numpy())


# ---------------------------------------------------------------------------
# Bootstrap point estimate and intervals against holdout.bootstrap_kendall


def test_bootstrap_reproduces_bootstrap_kendall():
    holdout = load_reference("holdout")
    rng = np.random.default_rng(8)
    n = 300
    score = np.round(rng.lognormal(size=n), 2)
    score[:40] = 0.0  # wallets outside the graph tie at zero
    label = rng.poisson(1.0 + 3 * (score > 1), n).astype(float)
    expected = holdout.bootstrap_kendall(pd.Series(score), pd.Series(label), n_resamples=400, seed=42)

    bs = PairedBootstrap(n, n_boot=400, seed=42)
    bs.add("score", score)
    bs.add("label", label)
    got = bs.tau("score", "label")
    assert got["kendall_tau"] == expected["kendall_tau"]
    assert spearman(score, label) == expected["spearman_rho"]
    # Same generator stream, so the resamples and the intervals agree as well.
    assert got["n_boot"] == expected["n_boot"] == 400
    assert abs(got["ci_low"] - expected["ci_low"]) < 1e-15
    assert abs(got["ci_high"] - expected["ci_high"]) < 1e-15


# ---------------------------------------------------------------------------
# Performance smoke test


def test_pagerank_5m_edges_smoke(capsys, params):
    rng = np.random.default_rng(0)
    m, n = 5_000_000, 1_000_000
    src = rng.integers(0, n, m)
    dst = rng.integers(0, n, m)
    w = rng.lognormal(size=m)
    start = time.perf_counter()
    scores, iterations = scoring.weighted_pagerank(src, dst, w, **params)
    elapsed = time.perf_counter() - start
    with capsys.disabled():
        print(
            f"\nweighted_pagerank: {m:,} edges, {scores.size:,} nodes, "
            f"{iterations} iterations, {elapsed:.2f} s"
        )
    assert abs(scores.sum() - 1.0) < 1e-9
