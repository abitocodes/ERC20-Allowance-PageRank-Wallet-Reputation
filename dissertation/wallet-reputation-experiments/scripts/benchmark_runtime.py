"""Benchmark PageRank runtime, memory, and iterations for all seven methods.

Timing protocol (one session per ``run_dissertation_eval.py`` invocation):

* one untimed warm-up solve per configuration; peak memory is taken from that
  warm-up under ``tracemalloc`` so the timed runs carry no tracing overhead;
* ``repeats`` timed solves (wall clock, ``time.perf_counter``) reported as
  mean, standard deviation, median, and minimum;
* each unique (edge multiset, damping, tolerance, max_iter) configuration is
  timed once per session and memoised, so any table that re-uses the same
  graph prints the same measurement.
"""

from __future__ import annotations

import hashlib
import time
import tracemalloc
from statistics import mean, median
from typing import Any

import numpy as np
import pandas as pd

from pagerank_variants import (
    ALLOWANCE_LAYER_ID,
    AWP_ID,
    ENDORSERANK_ID,
    SIX_AAVE_METHOD_IDS,
    TRANSFER_LAYER_ID,
    build_awp_paper_layer,
    build_endorserank_vt_layer,
    collect_method_edges,
    collect_six_aave_edges,
)

TIMING_PROTOCOL: dict[str, Any] = {
    "warmup_runs": 1,
    "memory_measure": "tracemalloc peak during the warm-up solve",
    "timing_measure": "time.perf_counter wall clock per timed solve, no tracing",
    "cache": "each unique (graph, damping, tol, max_iter) is timed once per session",
}

_TIMING_CACHE: dict[tuple, dict[str, Any]] = {}


def reset_timing_cache() -> None:
    _TIMING_CACHE.clear()


def _edge_signature(edges: pd.DataFrame) -> tuple:
    """Order-invariant fingerprint of an edge multiset."""
    if edges.empty:
        return ("empty", 0)
    cols = edges[["from_node", "to_node", "weight"]].reset_index(drop=True)
    h = pd.util.hash_pandas_object(cols, index=False).to_numpy(dtype=np.uint64)
    total = int(h.sum(dtype=np.uint64))
    xored = int(np.bitwise_xor.reduce(h))
    return (int(len(h)), total, xored)


def _teleport_signature(teleport: dict[str, float] | None) -> tuple:
    """Order-invariant fingerprint of a restart distribution (None = uniform)."""
    if not teleport:
        return ("uniform",)
    frame = pd.DataFrame({"node": list(teleport), "mass": list(teleport.values())})
    return ("weighted",) + _edge_signature(
        frame.rename(columns={"node": "from_node", "mass": "weight"}).assign(to_node="")
    )


def subsample_wallets_deterministic(
    wallets: list[str],
    n: int,
    seed: str = "benchmark-scale-v1",
) -> list[str]:
    """Return n wallets via SHA256(seed:address) ordering for reproducible scaling runs."""
    unique = sorted({w.lower() for w in wallets})
    if n >= len(unique):
        return unique
    keyed = sorted(
        unique,
        key=lambda w: hashlib.sha256(f"{seed}:{w}".encode()).hexdigest(),
    )
    return keyed[:n]


def scaling_stages_for_cohort(wallets: list[str], config: dict) -> list[int]:
    """Configured in-cohort stages plus full cohort size, capped at len(wallets)."""
    bench = config.get("benchmark") or {}
    configured = [int(s) for s in bench.get("scaling_stages", [1000, 2000, 4000])]
    full = len(wallets)
    stages = sorted({s for s in configured if 0 < s <= full})
    if full not in stages:
        stages.append(full)
    return stages


def _time_solver(
    key: tuple,
    solve: Any,
    edge_count: int,
    node_count: int,
    repeats: int,
) -> dict[str, Any]:
    """Warm-up (tracemalloc peak) plus ``repeats`` timed calls of ``solve()``.

    ``solve`` must return ``(scores, iterations)``. Results are memoised on
    ``key`` so identical configurations report identical measurements.
    """
    cached = _TIMING_CACHE.get(key)
    if cached is not None:
        out = dict(cached)
        out["reused_measurement"] = True
        return out

    tracemalloc.start()
    _, warm_iters = solve()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    peak_mb = peak / (1024 * 1024)

    runtimes: list[float] = []
    iterations: list[int] = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        _, iters = solve()
        runtimes.append(time.perf_counter() - t0)
        iterations.append(iters)

    result = {
        "runtime_sec_mean": round(mean(runtimes), 3),
        "runtime_sec_std": round(float(pd.Series(runtimes).std(ddof=0) or 0), 3),
        "runtime_sec_median": round(median(runtimes), 3),
        "runtime_sec_min": round(min(runtimes), 3),
        "runtime_sec_runs": [round(r, 4) for r in runtimes],
        "iterations_mean": round(mean(iterations), 1),
        "warmup_iterations": int(warm_iters),
        "peak_memory_mb": round(peak_mb, 2),
        "edge_count": int(edge_count),
        "node_count": int(node_count),
        "repeats": repeats,
        "warmup_runs": 1,
        "reused_measurement": False,
    }
    _TIMING_CACHE[key] = result
    return dict(result)


def _node_count(edges: pd.DataFrame) -> int:
    return len(set(edges["from_node"]) | set(edges["to_node"])) if not edges.empty else 0


def _run_timed(
    edges: pd.DataFrame,
    damping: float,
    tol: float,
    max_iter: int,
    repeats: int = 5,
    teleport: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Time one weighted PageRank; ``teleport`` is the restart distribution (None = uniform)."""
    from pagerank import weighted_pagerank

    key = (
        _edge_signature(edges),
        _teleport_signature(teleport),
        float(damping),
        float(tol),
        int(max_iter),
        int(repeats),
    )
    return _time_solver(
        key,
        lambda: weighted_pagerank(
            edges,
            damping=damping,
            tol=tol,
            max_iter=max_iter,
            return_iterations=True,
            teleport=teleport or None,
        ),
        edge_count=len(edges),
        node_count=_node_count(edges),
        repeats=repeats,
    )


def _run_timed_hybrids(
    er_edges: pd.DataFrame,
    awp_edges: pd.DataFrame,
    config: dict,
    repeats: int = 5,
) -> dict[str, dict[str, Any]]:
    """Time C-PR (configured lambdas) and S-PR on the two filtered layers.

    S-PR timing includes the EndorseRank solve that supplies its restart
    vector, since that solve is part of producing the score.
    """
    from pagerank import coupled_pagerank, weighted_pagerank
    from pagerank_variants import SEEDED_PR_ID, hybrid_lambda_map

    rep = config["reputation"]
    hyb = rep.get("hybrid") or {}
    damping = float(rep["damping"])
    tol = float(rep["pagerank_tolerance"])
    max_iter = int(rep["max_iterations"])
    sig_er = _edge_signature(er_edges)
    sig_awp = _edge_signature(awp_edges)
    union_nodes = len(
        (set(er_edges["from_node"]) | set(er_edges["to_node"]) if not er_edges.empty else set())
        | (set(awp_edges["from_node"]) | set(awp_edges["to_node"]) if not awp_edges.empty else set())
    )
    out: dict[str, dict[str, Any]] = {}
    for method_id, lam in hybrid_lambda_map(config).items():
        key = ("coupled", sig_er, sig_awp, float(lam), damping, tol, max_iter, int(repeats))
        out[method_id] = _time_solver(
            key,
            lambda lam=lam: coupled_pagerank(
                [(er_edges, lam), (awp_edges, 1.0 - lam)],
                damping=damping,
                tol=tol,
                max_iter=max_iter,
                return_iterations=True,
            ),
            edge_count=len(er_edges) + len(awp_edges),
            node_count=union_nodes,
            repeats=repeats,
        )
        out[method_id]["lambda"] = float(lam)

    floor = float(hyb.get("seeded_teleport_floor", 0.0))

    def _seeded() -> tuple[dict[str, float], int]:
        er_scores, er_iters = weighted_pagerank(
            er_edges, damping=damping, tol=tol, max_iter=max_iter, return_iterations=True
        )
        scores, iters = weighted_pagerank(
            awp_edges,
            damping=damping,
            tol=tol,
            max_iter=max_iter,
            return_iterations=True,
            teleport=er_scores or None,
            teleport_floor=floor,
        )
        return scores, int(er_iters) + int(iters)

    key = ("seeded", sig_er, sig_awp, floor, damping, tol, max_iter, int(repeats))
    out[SEEDED_PR_ID] = _time_solver(
        key,
        _seeded,
        edge_count=len(awp_edges),
        node_count=_node_count(awp_edges),
        repeats=repeats,
    )
    out[SEEDED_PR_ID]["iterations_note"] = "EndorseRank solve plus seeded transfer solve"
    return out


def benchmark_er_awp_pair(
    wallets: list[str],
    allowances: pd.DataFrame,
    transfers: pd.DataFrame,
    config: dict,
    repeats: int = 5,
    decoded: pd.DataFrame | None = None,
    aave_events: pd.DataFrame | None = None,
) -> dict[str, Any]:
    """Time EndorseRank and AWP (ENDORSERANK_ID, AWP_ID) on pre-built edge lists.

    Same path as the full benchmark; AWP's solve includes its activity-weighted restarts.
    """
    rep = config["reputation"]
    damping = float(rep["damping"])
    tol = float(rep["pagerank_tolerance"])
    max_iter = int(rep["max_iterations"])

    if decoded is not None:
        edge_map, restarts = collect_method_edges(
            wallets, config, allowances, transfers, decoded, aave_events, with_restarts=True
        )
        er_edges = edge_map[ENDORSERANK_ID]
        awp_edges = edge_map[AWP_ID]
        activeness = restarts[AWP_ID]
    else:
        seed = set(w.lower() for w in wallets)
        observation_end = pd.Timestamp(rep["observation_end"], tz="UTC")
        er_edges, _ = build_endorserank_vt_layer(allowances, config, observation_end, seed)
        awp_edges, activeness = build_awp_paper_layer(transfers, config, observation_end, seed)

    return {
        ENDORSERANK_ID: _run_timed(er_edges, damping, tol, max_iter, repeats),
        AWP_ID: _run_timed(awp_edges, damping, tol, max_iter, repeats, teleport=activeness),
        "n_wallets": len(wallets),
    }


def benchmark_all_methods(
    wallets: list[str],
    allowances: pd.DataFrame,
    transfers: pd.DataFrame,
    decoded: pd.DataFrame,
    aave_events: pd.DataFrame | None,
    config: dict,
    repeats: int = 5,
) -> dict[str, Any]:
    """Time weighted PageRank on each method's filtered edge list."""
    rep = config["reputation"]
    damping = float(rep["damping"])
    tol = float(rep["pagerank_tolerance"])
    max_iter = int(rep["max_iterations"])

    edge_map, restarts = collect_method_edges(
        wallets, config, allowances, transfers, decoded, aave_events, with_restarts=True
    )

    results: dict[str, Any] = {"n_wallets": len(wallets)}
    for method_id, edges in edge_map.items():
        results[method_id] = _run_timed(
            edges, damping, tol, max_iter, repeats, teleport=restarts.get(method_id)
        )

    results.update(
        _run_timed_hybrids(
            edge_map[ALLOWANCE_LAYER_ID], edge_map[TRANSFER_LAYER_ID], config, repeats=repeats
        )
    )
    return results


def benchmark_six_aave_methods(
    wallets: list[str],
    allowances: pd.DataFrame,
    transfers: pd.DataFrame,
    aave_events: pd.DataFrame | None,
    delegation_events: pd.DataFrame | None,
    config: dict,
    repeats: int = 5,
) -> dict[str, Any]:
    """Time PageRank for six-Aave preset methods."""
    rep = config["reputation"]
    damping = float(rep["damping"])
    tol = float(rep["pagerank_tolerance"])
    max_iter = int(rep["max_iterations"])

    edge_map = collect_six_aave_edges(
        wallets, config, allowances, transfers, aave_events, delegation_events
    )

    results: dict[str, Any] = {"n_wallets": len(wallets)}
    for method_id in SIX_AAVE_METHOD_IDS:
        edges = edge_map.get(method_id, pd.DataFrame())
        results[method_id] = _run_timed(edges, damping, tol, max_iter, repeats)
    return results


def benchmark_reputation(
    wallets: list[str],
    allowances: pd.DataFrame,
    transfers: pd.DataFrame,
    config: dict,
    repeats: int = 5,
    decoded: pd.DataFrame | None = None,
    aave_events: pd.DataFrame | None = None,
    delegation_events: pd.DataFrame | None = None,
) -> dict[str, Any]:
    """Backward-compatible wrapper; benchmarks all methods when decoded is provided."""
    if decoded is not None:
        results = benchmark_all_methods(
            wallets, allowances, transfers, decoded, aave_events, config, repeats
        )
        six_bench = benchmark_six_aave_methods(
            wallets, allowances, transfers, aave_events, delegation_events, config, repeats
        )
        results["six_aave"] = six_bench
        for method_id in SIX_AAVE_METHOD_IDS:
            if method_id in six_bench:
                results[method_id] = six_bench[method_id]
        return results

    return benchmark_er_awp_pair(
        wallets, allowances, transfers, config, repeats=repeats, decoded=None
    )


def benchmark_scaling(
    wallets: list[str],
    allowances: pd.DataFrame,
    transfers: pd.DataFrame,
    config: dict,
    repeats: int = 5,
    decoded: pd.DataFrame | None = None,
    aave_events: pd.DataFrame | None = None,
    authoritative_full_cohort: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Benchmark EndorseRank vs AWP at deterministic in-cohort subsample sizes."""
    bench = config.get("benchmark") or {}
    scaling_seed = str(bench.get("scaling_seed", "benchmark-scale-v1"))
    stages = scaling_stages_for_cohort(wallets, config)
    full_n = len(wallets)

    rows: list[dict[str, Any]] = []
    for n in stages:
        subset = subsample_wallets_deterministic(wallets, n, seed=scaling_seed)
        if (
            authoritative_full_cohort is not None
            and len(subset) == full_n
            and n == full_n
        ):
            er = authoritative_full_cohort[ENDORSERANK_ID]
            awp = authoritative_full_cohort[AWP_ID]
        else:
            pair = benchmark_er_awp_pair(
                subset,
                allowances,
                transfers,
                config,
                repeats=repeats,
                decoded=decoded,
                aave_events=aave_events,
            )
            er = pair[ENDORSERANK_ID]
            awp = pair[AWP_ID]

        er_speedup_ratio = (
            round(awp["runtime_sec_mean"] / er["runtime_sec_mean"], 2)
            if er["runtime_sec_mean"] > 0
            else None
        )
        rows.append(
            {
                "n_wallets": len(subset),
                "scaling_seed": scaling_seed,
                ENDORSERANK_ID: er,
                AWP_ID: awp,
                "er_speedup_ratio": er_speedup_ratio,
                "speedup_awp_over_er": er_speedup_ratio,
            }
        )

    return {
        "scaling_seed": scaling_seed,
        "stages": stages,
        "rows": rows,
        "repeats": repeats,
    }


def tier2_stages_for_pool(pool_size: int, config: dict) -> list[int]:
    """Configured Tier-2 benchmark stages capped at wallet pool size."""
    bench = config.get("benchmark") or {}
    configured = [int(s) for s in bench.get("stages", [10000, 50000, 100000])]
    stages = sorted({s for s in configured if 0 < s <= pool_size})
    if pool_size not in stages and pool_size > 0:
        stages.append(pool_size)
    return stages


def benchmark_tier2_scaling(
    wallet_pool: list[str],
    allowances: pd.DataFrame,
    transfers: pd.DataFrame,
    config: dict,
    repeats: int = 5,
) -> dict[str, Any]:
    """Benchmark EndorseRank vs AWP at Tier-2 stages (10k/50k/100k) from wallet pool."""
    bench = config.get("benchmark") or {}
    scaling_seed = str(bench.get("tier2_scaling_seed", "benchmark-tier2-v1"))
    stages = tier2_stages_for_pool(len(wallet_pool), config)

    rows: list[dict[str, Any]] = []
    for n in stages:
        subset = subsample_wallets_deterministic(wallet_pool, n, seed=scaling_seed)
        pair = benchmark_er_awp_pair(
            subset,
            allowances,
            transfers,
            config,
            repeats=repeats,
        )
        er = pair[ENDORSERANK_ID]
        awp = pair[AWP_ID]
        er_speedup_ratio = (
            round(awp["runtime_sec_mean"] / er["runtime_sec_mean"], 2)
            if er["runtime_sec_mean"] > 0
            else None
        )
        rows.append(
            {
                "n_wallets": len(subset),
                "scaling_seed": scaling_seed,
                ENDORSERANK_ID: er,
                AWP_ID: awp,
                "er_speedup_ratio": er_speedup_ratio,
                "speedup_awp_over_er": er_speedup_ratio,
            }
        )

    return {
        "scaling_seed": scaling_seed,
        "wallet_pool_size": len(wallet_pool),
        "stages": stages,
        "rows": rows,
        "repeats": repeats,
        "tier": 2,
    }
