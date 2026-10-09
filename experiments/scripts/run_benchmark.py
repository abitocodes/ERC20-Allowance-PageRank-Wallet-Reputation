#!/usr/bin/env python3
"""Computational benchmark (Claim C1) and runtime scaling.

The timed call turns an edge list into scores: node indexing, sparse matrix
assembly, row normalisation, restart vector and power iteration. Edge lists and
AWP's restart weights are built before the timer starts. Every configuration
gets one untimed warm-up run, on which alone peak memory is traced, and five
timed runs; the mean and standard deviation of the timed runs, the iterations
and |V| and |E| of the solver graph are reported.

Scaling stages are deterministic SHA256 subsamples of the matched cohort (seed of
the configuration); a stage keeps the edges incident to its sampled contracts,
so |E| grows with the stage.
"""

from __future__ import annotations

import hashlib
import platform
import sys
import time
import tracemalloc
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import PROC, load_config, save_json  # noqa: E402
from graphs import Graphs, load_graphs, load_nodes, restrict  # noqa: E402
from scoring import activeness, coupled_pagerank, pagerank_params, seeded_pagerank, weighted_pagerank  # noqa: E402

OUT = PROC / "benchmark"


def solver_calls(g: Graphs, params: dict) -> dict:
    a, t = g.allow, g.transfer
    act = activeness(t["src"], t["dst"], t["max_sig"])
    a_arr = (a["src"].to_numpy(), a["dst"].to_numpy(), a["w_er"].to_numpy())
    t_arr = (t["src"].to_numpy(), t["dst"].to_numpy(), t["w_awp"].to_numpy())
    ar = (a["src"].to_numpy(), a["dst"].to_numpy(), a["w_raw"].to_numpy())
    tr = (t["src"].to_numpy(), t["dst"].to_numpy(), t["w_raw"].to_numpy())

    def spr():
        l100, it1 = weighted_pagerank(*ar, **params)
        s, it2 = seeded_pagerank(*tr, l100, **params)
        return s, it1 + it2

    return {
        "endorserank": (lambda: weighted_pagerank(*a_arr, **params), a_arr),
        "awp": (lambda: weighted_pagerank(*t_arr, teleport=act, **params), t_arr),
        "cpr_l50": (lambda: coupled_pagerank([(*ar, 0.5), (*tr, 0.5)], **params), None),
        "spr": (spr, tr),
    }


def graph_size(arrs) -> tuple[int, int]:
    src, dst, w = arrs
    keep = w > 0
    pairs = pd.DataFrame({"s": src[keep], "d": dst[keep]}).drop_duplicates()
    return int(len(np.union1d(pairs["s"], pairs["d"]))), int(len(pairs))


def time_call(fn, runs: int) -> dict:
    tracemalloc.start()
    _, it = fn()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    times = []
    for _ in range(runs):
        t0 = time.perf_counter()
        _, it = fn()
        times.append(time.perf_counter() - t0)
    return {"mean_s": float(np.mean(times)), "sd_s": float(np.std(times, ddof=1)), "runs_s": times,
            "peak_mb": peak / 2**20, "iterations": int(it)}


def sha_order(addresses: pd.Series, seed: str) -> np.ndarray:
    keys = [hashlib.sha256(f"{seed}:{a}".encode()).hexdigest() for a in addresses]
    return np.argsort(np.asarray(keys))


def main() -> int:
    cfg = load_config()
    params = pagerank_params(cfg)
    runs = int(cfg["benchmark"]["timed_runs"])
    nodes = load_nodes()
    cohort = nodes.loc[nodes["is_cohort"], ["id", "address"]].reset_index(drop=True)
    g = load_graphs("tobs")

    main_rows = {}
    calls = solver_calls(g, params)
    for m, (fn, arrs) in calls.items():
        r = time_call(fn, runs)
        if arrs is None:
            a, t = g.allow, g.transfer
            both = pd.concat([a.loc[a["w_raw"] > 0, ["src", "dst"]], t.loc[t["w_raw"] > 0, ["src", "dst"]]]).drop_duplicates()
            r["nodes"], r["edges"] = int(len(np.union1d(both["src"], both["dst"]))), int(len(both))
        else:
            r["nodes"], r["edges"] = graph_size(arrs)
        main_rows[m] = r
        print(m, f"{r['mean_s']:.3f}s", r["iterations"], r["edges"], flush=True)

    # Damping sweep: the d = 0.85 rows are the main measurements above, reused, not re-timed.
    damping = {}
    for d in cfg["robustness"]["damping_values"]:
        if abs(d - params["damping"]) < 1e-12:
            damping[str(d)] = {m: main_rows[m] for m in ("endorserank", "awp")}
            continue
        sc = solver_calls(g, {**params, "damping": d})
        damping[str(d)] = {}
        for m in ("endorserank", "awp"):
            fn, arrs = sc[m]
            r = time_call(fn, runs)
            r["nodes"], r["edges"] = graph_size(arrs)
            damping[str(d)][m] = r
        print("damping", d, {m: round(v["mean_s"], 3) for m, v in damping[str(d)].items()}, flush=True)

    order = sha_order(cohort["address"], cfg["benchmark"]["scaling_seed"])
    n_all = len(cohort)
    stages = [s for s in (1000, 2000, 5000, 10000, 20000) if s < n_all] + [n_all]
    scaling = []
    for n in stages:
        if n == n_all:  # the full cohort graph is the main measurement, reused
            scaling.append({"n": n, "endorserank": main_rows["endorserank"], "awp": main_rows["awp"], "reused_main": True})
            continue
        ids = cohort["id"].to_numpy()[order[:n]]
        sub = restrict(g, ids)
        sc = solver_calls(sub, params)
        row = {"n": n}
        for m in ("endorserank", "awp"):
            fn, arrs = sc[m]
            r = time_call(fn, runs)
            r["nodes"], r["edges"] = graph_size(arrs)
            row[m] = r
        scaling.append(row)
        print("stage", n, f"ER {row['endorserank']['mean_s']:.3f}s |E|={row['endorserank']['edges']}",
              f"AWP {row['awp']['mean_s']:.3f}s |E|={row['awp']['edges']}", flush=True)

    save_json({
        "protocol": {"warmup_runs": 1, "timed_runs": runs, "damping": params["damping"],
                     "tol": params["tol"], "max_iter": params["max_iter"]},
        "machine": {"platform": platform.platform(), "processor": platform.processor(),
                    "python": platform.python_version()},
        "main": main_rows,
        "damping": damping,
        "scaling": scaling,
        "scaling_seed": cfg["benchmark"]["scaling_seed"],
    }, OUT / "benchmark.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
