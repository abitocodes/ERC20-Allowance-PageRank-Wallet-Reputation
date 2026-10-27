"""Exploratory (2026-10-22): C-PR against AWP, and a coupled walk whose transfer end is AWP (C-AWP).

Part A reads the published per-contract scores of the revised analysis and compares C-PR with AWP on
both spender labels at once, on new counterparties, by coverage, at the top of the ranking, on both
same-window constructs and on the traders. Part B computes C-AWP:

  transfer layer   AWP's edges (w_awp = sum sigma V(usd))
  allowance layer  EndorseRank's edges (w_er = sum over tokens sigma V(usd))
  transitions      per-node mixture as in C-PR: weight lam on the allowance row and 1 - lam on the
                   transfer row at a node with out-edges in both layers, the one layer otherwise
  restarts         (1 - lam) pi_T + lam pi_A, pi_T = AWP's sending activeness, pi_A = the owners'
                   approving activeness of EndorseRank with activity restarts, each normalised

so lam = 0 is AWP and lam = 1 is EndorseRank with activity restarts. The design is fixed in ../README.md.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

os.environ["CONTRACT_REP_VARIANT"] = "usd"
EXP = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXP / "scripts"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from common import GRAPH, PROC, load_config, read_parts  # noqa: E402
from scoring import (_local_index, _out_strength, _positive_edges, _power_iterate,  # noqa: E402
                     _scores, _teleport_vector, _transposed, activeness, pagerank_params, scores_on)
from stats import PairedBootstrap, percentile_ci  # noqa: E402

APPR, SEND, NEWCP = "future_new_approvers", "future_new_transfer_senders", "future_new_counterparties"
LIQ, NOLIQ = "liquidation_free_rate", "no_liquidation"
LAMS = {"cawp_l25": 0.25, "cawp_l50": 0.5, "cawp_l75": 0.75}
CHECKS = {"cawp_l0": 0.0, "cawp_l100": 1.0}
PUBLISHED = ["endorserank", "endorserank_activity", "awp", "cpr_l0", "cpr_l25", "cpr_l50", "cpr_l75", "cpr_l100", "spr"]
FAMILIES = {
    "transfer": ["in_degree", "in_value"],
    "allowance": ["in_approve_degree", "in_approve_value"],
    "sybil_stability": ["inbound_counterparty_ratio", "transfer_tenure_days", "active_months"],
}
DELTA = 0.01
REV = PROC  # data/2-.../revised-usd under CONTRACT_REP_VARIANT=usd
CACHE = EXP / "data" / "_work" / "cawp"
WINDOWS = {"W0": ("t1", "holdout-w0", "t1_in_approve_degree", "t1_in_degree"),
           "W1": ("tobs", "window-w1", "in_approve_degree", "in_degree")}
WORKERS = int(os.environ.get("CAWP_WORKERS", "4"))


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def coupled_with_restarts(layers, teleport, p):
    """C-PR's per-node mixture of layers (scoring.coupled_pagerank) with a given restart vector.

    layers: [(src, dst, w, weight)]; a layer with weight 0 is left out, as in coupled_pagerank.
    """
    active = []
    for src, dst, w, weight in layers:
        if float(weight) <= 0:
            continue
        s, d, ww = _positive_edges(src, dst, w)
        if s.size:
            active.append((s, d, ww, float(weight)))
    nodes, local = _local_index([a for s, d, _, _ in active for a in (s, d)])
    n = nodes.size
    strengths, denom = [], np.zeros(n)
    for i, (_, _, w, weight) in enumerate(active):
        out, inv = _out_strength(local[2 * i], w, n)
        has = (out > 0).astype(np.float64)
        denom += weight * has
        strengths.append((inv, has))
    pos = denom > 0
    mats = []
    for i, (_, _, w, weight) in enumerate(active):
        inv, has = strengths[i]
        alpha = np.zeros(n)
        alpha[pos] = weight * has[pos] / denom[pos]
        s, d = local[2 * i], local[2 * i + 1]
        mats.append(_transposed(s, d, w * inv[s] * alpha[s], n))
    restart = _teleport_vector(nodes, teleport)
    rank, iterations = _power_iterate(mats, ~pos, restart, p["damping"], p["tol"], p["max_iter"])
    return _scores(nodes, rank), iterations


def cawp_scores(tag: str, p: dict) -> tuple[dict[str, pd.Series], dict[str, int]]:
    cached = CACHE / f"cawp_{tag}.parquet"
    if cached.exists():
        frame = pd.read_parquet(cached)
        its = json.loads((CACHE / f"cawp_{tag}_iterations.json").read_text())
        return {m: frame[m].dropna() for m in frame}, its
    a = read_parts(GRAPH / f"allow_pairs_{tag}", ["src", "dst", "w_er", "max_sig"])
    t = read_parts(GRAPH / f"transfer_pairs_{tag}", ["src", "dst", "w_awp", "max_sig"])
    pi_t = activeness(t["src"], t["dst"], t["max_sig"])
    pi_a = activeness(a["src"], a["dst"], a["max_sig"])
    pi_t, pi_a = pi_t / pi_t.sum(), pi_a / pi_a.sum()
    out, its = {}, {}
    for name, lam in {**CHECKS, **LAMS}.items():
        tele = pi_t.mul(1.0 - lam).add(pi_a.mul(lam), fill_value=0.0)
        t0 = time.time()
        out[name], its[name] = coupled_with_restarts(
            [(a["src"], a["dst"], a["w_er"], lam), (t["src"], t["dst"], t["w_awp"], 1.0 - lam)], tele, p)
        log(tag, name, "iterations", its[name], f"{time.time() - t0:.1f}s")
    CACHE.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(out).to_parquet(cached)
    (CACHE / f"cawp_{tag}_iterations.json").write_text(json.dumps(its))
    return out, its


def tau_rows(boot: PairedBootstrap, scores, labels):
    return {s: {lab: boot.tau(s, lab) for lab in labels} for s in scores}


def contrasts(boot: PairedBootstrap, specs):
    rows = []
    for a, b, lab in specs:
        r = boot.contrast((a, lab), (b, lab)) or {}
        rows.append({"a": a, "b": b, "outcome": lab if isinstance(lab, str) else list(lab), **r})
    return rows


def boot_on(frame: pd.DataFrame, cols, n_boot: int, seed: int) -> PairedBootstrap:
    boot = PairedBootstrap(len(frame), n_boot, seed)
    for c in cols:
        boot.add(c, frame[c].to_numpy(dtype=np.float64))
    return boot


def reproduction(frame: pd.DataFrame) -> dict:
    from stats import kendall_tau_b
    out = {}
    for new, old in (("cawp_l0", "awp"), ("cawp_l100", "endorserank_activity")):
        x, y = frame[new].to_numpy(), frame[old].to_numpy()
        out[f"{new}_vs_{old}"] = {"kendall_tau": kendall_tau_b(x, y), "max_abs_diff": float(np.max(np.abs(x - y))),
                                  "max_rel_diff": float(np.max(np.abs(x - y) / np.maximum(np.abs(y), 1e-300)))}
    return out


def top_k(frame: pd.DataFrame, scores, ks=(100, 500, 1000)) -> dict:
    any_new = (frame[APPR] > 0) | (frame[SEND] > 0)
    out = {}
    for s in scores:
        order = frame.sort_values([s, "id"], ascending=[False, True], kind="mergesort").index
        out[s] = {}
        for k in ks:
            top = order[:k]
            out[s][str(k)] = {"any_new_counterparty": float(any_new.loc[top].mean()),
                              "any_new_approval_pair": float((frame.loc[top, APPR] > 0).mean()),
                              "any_new_sender": float((frame.loc[top, SEND] > 0).mean()),
                              "ties_at_cutoff": int((frame[s] == frame.loc[order[k - 1], s]).sum())}
    out["base_rate"] = {"any_new_counterparty": float(any_new.mean()), "any_new_approval_pair": float((frame[APPR] > 0).mean()),
                        "any_new_sender": float((frame[SEND] > 0).mean())}
    return out


def spender_window(name: str, cfg: dict, full: dict[str, pd.Series], its: dict[str, int]) -> dict:
    tag, folder, adeg, tdeg = WINDOWS[name]
    nb, seed = cfg["alignment"]["bootstrap_resamples"], cfg["alignment"]["bootstrap_seed"]
    S = read_parts(REV / folder / "spender_scores").sort_values("id").reset_index(drop=True)
    S = S.rename(columns={adeg: "in_approve_degree", tdeg: "in_degree"})
    S[NEWCP] = S[APPR] + S[SEND]
    ids = S["id"].to_numpy(np.int64)
    for m, s in full.items():
        S[m] = scores_on(ids, s).to_numpy()
    scores = PUBLISHED + ["in_approve_degree", "in_degree"] + list(LAMS)
    labels = [APPR, SEND, NEWCP]
    boot = boot_on(S, scores + labels, nb, seed)
    boot.prefetch([(s, lab) for s in scores for lab in labels], workers=WORKERS)
    out = {"n": int(len(S)), "iterations": its, "reproduction": reproduction(S), "taus": tau_rows(boot, scores, labels)}
    fam = [APPR, SEND]
    out["A1_both_labels"] = {
        "family_means": {s: boot.family(s, fam) for s in scores},
        "contrasts": contrasts(boot, [(s, "awp", fam) for s in ("cpr_l25", "cpr_l50", "cpr_l75", "endorserank",
                                                                 "endorserank_activity", "cawp_l50")]),
    }
    out["A2_new_counterparties"] = contrasts(boot, [("cpr_l50", b, NEWCP) for b in ("awp", "endorserank", "in_approve_degree", "in_degree")])
    zero = S["awp"] == 0
    Z, R = S.loc[zero].reset_index(drop=True), S.loc[~zero].reset_index(drop=True)
    bz = boot_on(Z, ["cpr_l50", "endorserank", "in_approve_degree", "cawp_l50", APPR], nb, seed)
    br = boot_on(R, ["cpr_l50", "awp", "cawp_l50"] + labels, nb, seed)
    out["A3_coverage"] = {
        "awp_zero": {"n": int(zero.sum()), "gained_approval_pair": int((Z[APPR] > 0).sum()), "gained_sender": int((Z[SEND] > 0).sum()),
                     "taus_new_approval_pairs": {s: bz.tau(s, APPR) for s in ("cpr_l50", "endorserank", "in_approve_degree", "cawp_l50")}},
        "awp_positive": {"n": int((~zero).sum()), "contrasts": contrasts(br, [(a, "awp", lab) for a in ("cpr_l50", "cawp_l50") for lab in labels])},
    }
    out["A4_top_k"] = top_k(S, ["awp", "cpr_l50", "endorserank", "cawp_l50"])
    b1 = []
    for lab in labels:
        b1 += [("cawp_l50", "awp", lab), ("cawp_l50", "cpr_l50", lab), ("cawp_l50", "endorserank_activity", lab)]
    b1 += [("cawp_l50", "in_approve_degree", APPR), ("cawp_l50", "in_degree", SEND),
           ("cawp_l25", "awp", APPR), ("cawp_l25", "awp", SEND), ("cawp_l75", "awp", APPR), ("cawp_l75", "awp", SEND)]
    out["B1_contrasts"] = contrasts(boot, b1)
    f1 = boot.contrast(("cawp_l50", APPR), ("awp", APPR))
    f2 = boot.contrast(("cawp_l50", SEND), ("awp", SEND))
    out["B2_spender_part"] = {"F1_superiority_new_approval_pairs": {**f1, "holds": bool(f1["ci_low"] > 0)},
                              "F2_noninferiority_new_senders": {**f2, "holds": bool(f2["ci_low"] > -DELTA)}}
    keep = ["id"] + [c for c in S.columns if c.startswith("cawp_")]
    out["_scores"] = S[keep]
    return out


def traders(name: str, cfg: dict, cache: dict) -> dict:
    tag, folder, adeg, tdeg = WINDOWS[name]
    nb, seed = cfg["alignment"]["bootstrap_resamples"], cfg["alignment"]["bootstrap_seed"]
    T = read_parts(REV / folder / "trader_scores").sort_values("id").reset_index(drop=True)
    T = T.rename(columns={adeg: "in_approve_degree", tdeg: "in_degree"})
    ids = T["id"].to_numpy(np.int64)
    for m, s in cache[tag].items():
        T[m] = scores_on(ids, s).to_numpy()
    scores = ["awp", "cpr_l0", "cpr_l50", "cpr_l100", "endorserank", "endorserank_activity", "in_approve_degree", "in_degree"] + list(LAMS)
    labels = [LIQ, NOLIQ]
    boot = boot_on(T, scores + labels, nb, seed)
    out = {"n": int(len(T)), "reproduction": reproduction(T), "taus": tau_rows(boot, scores, labels),
           "contrasts": contrasts(boot, [(a, "awp", lab) for a in ("cpr_l50", "cawp_l50", "cawp_l25", "cawp_l75") for lab in labels])}
    f3 = boot.contrast(("cawp_l50", LIQ), ("awp", LIQ))
    out["B2_F3_noninferiority_liquidation_free_rate"] = {**f3, "holds": bool(f3["ci_low"] > -DELTA)}
    f3c = boot.contrast(("cpr_l50", LIQ), ("awp", LIQ))
    out["published_F3_against_awp_check"] = f3c
    return out


def same_window(cfg: dict, cache: dict) -> dict:
    nb, seed = cfg["alignment"]["bootstrap_resamples"], cfg["alignment"]["bootstrap_seed"]
    C = read_parts(REV / "same-window" / "cohort_scores").sort_values("id").reset_index(drop=True)
    ids = C["id"].to_numpy(np.int64)
    for m, s in cache["tobs"].items():
        C[m] = scores_on(ids, s).to_numpy()
    proxies = [x for f in FAMILIES.values() for x in f]
    scores = ["awp", "cpr_l50", "endorserank", "endorserank_activity"] + list(LAMS)
    boot = boot_on(C, scores + proxies, nb, seed)
    boot.prefetch([(s, x) for s in scores for x in proxies], workers=WORKERS)
    both = FAMILIES["transfer"] + FAMILIES["allowance"]
    out = {"n": int(len(C)), "reproduction": reproduction(C),
           "families": {s: {f: boot.family(s, labs) for f, labs in FAMILIES.items()} for s in scores},
           "A5_both_constructs": {"family_means": {s: boot.family(s, both) for s in scores},
                                  "contrasts": contrasts(boot, [(a, "awp", both) for a in ("cpr_l50", "cawp_l50", "endorserank")])},
           "B3_contrasts": contrasts(boot, [("cawp_l50", "awp", labs) for labs in FAMILIES.values()]
                                     + [("cawp_l50", "cpr_l50", labs) for labs in FAMILIES.values()])}
    return out


def _plain(x):
    if isinstance(x, (np.bool_,)):
        return bool(x)
    if isinstance(x, np.integer):
        return int(x)
    if isinstance(x, np.floating):
        return float(x)
    raise TypeError(type(x))


def main() -> int:
    cfg = load_config()
    p = pagerank_params(cfg)
    res, scores = {"design": "../README.md", "params": p, "bootstrap": cfg["alignment"]}, {}
    cache = {}
    for w in WINDOWS:
        tag = WINDOWS[w][0]
        log("C-AWP at", tag)
        cache[tag], its = cawp_scores(tag, p)
        log("spender window", w)
        r = spender_window(w, cfg, cache[tag], its)
        scores[w] = r.pop("_scores")
        res[w] = r
    for w in WINDOWS:
        log("traders", w)
        res[f"traders_{w}"] = traders(w, cfg, cache)
    log("same window")
    res["same_window"] = same_window(cfg, cache)
    out = HERE / "results_cpr_awp.json"
    out.write_text(json.dumps(res, indent=2, default=_plain), encoding="utf-8")
    xproc = EXP / "data" / "2-processed-tables-and-evaluations" / "exploratory-2026-10-22"
    xproc.mkdir(parents=True, exist_ok=True)
    for w, frame in scores.items():
        frame.to_parquet(xproc / f"cawp_{w.lower()}.parquet", index=False)
    log("wrote", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
