"""Spearman rho and Kendall tau alignment between reputation scores and proxies."""



from __future__ import annotations



from typing import Any



import numpy as np

import pandas as pd

from scipy.stats import kendalltau, spearmanr



TRANSFER_PROXIES = ("in_degree", "in_value")

ALLOWANCE_PROXIES = ("in_approve_degree", "in_approve_value")

LIQUIDATION_PROXIES = (

    "liquidation_free_rate",

    "zero_liquidation_flag",

    "liquidation_free_closes",

)

INVERSE_RISK_PROXIES = (

    "loss_avoidance",

    "non_loss_close_rate",

    "worst_close_pnl_score",

)

SYBIL_PROXIES = (

    "inbound_counterparty_ratio",

    "transfer_tenure_days",

    "active_months",

)

GMX_PROXIES = ("close_success_count", "realized_gain_proxy", "close_success_rate")



PROXY_FAMILIES: dict[str, tuple[str, ...]] = {

    "transfer": TRANSFER_PROXIES,

    "allowance": ALLOWANCE_PROXIES,

    "liquidation": LIQUIDATION_PROXIES,

    "inverse_risk": INVERSE_RISK_PROXIES,

    "sybil_stability": SYBIL_PROXIES,

    "gmx_success": GMX_PROXIES,

}



ALL_PROXIES = tuple(p for proxies in PROXY_FAMILIES.values() for p in proxies)



# "awp_paper" is AWP as published by Do, Do and Nguyen (2023), the baseline of the

# thesis, and "endorserank_vt" is EndorseRank: AWP's edge weights on the

# allowance graph with uniform restarts ("endorserank_vt_activity" restarts it

# as AWP does, a sensitivity analysis). "endorserank" and "awp" are the two

# layers of the hybrids walked alone (C-PR at lambda = 1 and 0). See pagerank_variants.

DISSERTATION_METHODS: dict[str, str] = {

    "endorserank_vt": "endorserank_vt_score",

    "awp_paper": "awp_paper_score",

    "gf_pr": "gf_pr_score",

}



METHODS: dict[str, str] = {

    "endorserank_vt": "endorserank_vt_score",

    "endorserank_vt_activity": "endorserank_vt_activity_score",

    "awp_paper": "awp_paper_score",

    "awp": "awp_score",

    "endorserank": "endorserank_score",

    "gf_pr": "gf_pr_score",

    "lp_pr": "lp_pr_score",

    "cw_awp": "cw_awp_score",

    "lf_pr": "lf_pr_score",

    "riskprop_pr": "riskprop_pr_score",

    "coupled_pr": "coupled_pr_score",

    "coupled_pr_l25": "coupled_pr_l25_score",

    "coupled_pr_l75": "coupled_pr_l75_score",

    "seeded_pr": "seeded_pr_score",

}



METHOD_LABELS: dict[str, str] = {

    "endorserank_vt": "EndorseRank",

    "endorserank_vt_activity": "EndorseRank, AWP's restarts",

    "awp_paper": "AWP",

    "awp": "C-PR ($\\lambda=0$)",

    "endorserank": "C-PR ($\\lambda=1$)",

    "gf_pr": "GF-PR",

    "lp_pr": "LP-PR",

    "cw_awp": "CW-AWP",

    "lf_pr": "LF-PR",

    "riskprop_pr": "RiskProp",

    "coupled_pr": "C-PR ($\\lambda=0.5$)",

    "coupled_pr_l25": "C-PR ($\\lambda=0.25$)",

    "coupled_pr_l75": "C-PR ($\\lambda=0.75$)",

    "seeded_pr": "S-PR",

}

# Methods that receive the paired bootstrap (CIs and contrasts).

BOOTSTRAP_METHODS: tuple[str, ...] = (

    "endorserank_vt",

    "endorserank_vt_activity",

    "awp_paper",

    "endorserank",

    "awp",

    "coupled_pr",

    "coupled_pr_l25",

    "coupled_pr_l75",

    "seeded_pr",

)

HYBRID_METHODS: tuple[str, ...] = ("coupled_pr", "coupled_pr_l25", "coupled_pr_l75", "seeded_pr")

# Original seven-method preset (archived extended baselines), without hybrids.

SEVEN_METHODS: dict[str, str] = {

    k: v
    for k, v in METHODS.items()
    if k not in HYBRID_METHODS and k not in ("endorserank_vt", "endorserank_vt_activity", "awp_paper")

}


SIX_AAVE_METHODS: dict[str, str] = {

    "awp": "awp_score",

    "endorserank": "endorserank_score",

    "liq_pr": "liq_pr_score",

    "borrow_pr": "borrow_pr_score",

    "repay_pr": "repay_pr_score",

    "delegation_pr": "delegation_pr_score",

}


SIX_AAVE_DIAGNOSTIC_METHODS: dict[str, str] = {

    "borrow_pr_pool": "borrow_pr_pool_score",

    "repay_pr_pool": "repay_pr_pool_score",

}


SIX_AAVE_LABELS: dict[str, str] = {

    "awp": "C-PR ($\\lambda=0$)",

    "endorserank": "C-PR ($\\lambda=1$)",

    "liq_pr": "LiqCall-PR",

    "borrow_pr": "Borrow-PR",

    "repay_pr": "Repay-PR",

    "delegation_pr": "Delegation-PR",

}





def _correlate(scores: pd.Series, proxy: pd.Series) -> dict[str, float | None]:

    mask = scores.notna() & proxy.notna()

    if mask.sum() < 5:

        return {"spearman_rho": None, "kendall_tau": None, "n": int(mask.sum())}

    x = scores[mask].astype(float)

    y = proxy[mask].astype(float)

    if x.nunique() < 2 or y.nunique() < 2:

        return {"spearman_rho": None, "kendall_tau": None, "n": int(mask.sum())}

    rho, _ = spearmanr(x, y)

    tau, _ = kendalltau(x, y)

    return {"spearman_rho": float(rho), "kendall_tau": float(tau), "n": int(mask.sum())}





def evaluate_method(

    df: pd.DataFrame,

    score_col: str,

    proxy_cols: tuple[str, ...],

) -> dict[str, dict[str, Any]]:

    out: dict[str, dict[str, Any]] = {}

    if score_col not in df.columns:

        return out

    scores = df[score_col]

    for proxy in proxy_cols:

        if proxy not in df.columns:

            continue

        out[proxy] = _correlate(scores, df[proxy])

    return out





def mean_tau(results: dict[str, dict[str, Any]], proxies: tuple[str, ...]) -> float | None:

    vals = [

        results[p]["kendall_tau"]

        for p in proxies

        if p in results and results[p]["kendall_tau"] is not None

    ]

    return float(sum(vals) / len(vals)) if vals else None





def _cross_proxy_means(method_results: dict[str, dict[str, Any]]) -> dict[str, float | None]:

    return {

        f"{family}_mean_tau": mean_tau(method_results, proxies)

        for family, proxies in PROXY_FAMILIES.items()

    }





def _method_comparison(

    er_cross: dict[str, float | None],

    other_cross: dict[str, float | None],

    other_id: str,

    other_label: str,

) -> dict[str, dict[str, Any]]:

    """EndorseRank against one transfer walk, family by family (keys carry the walk's id)."""

    out: dict[str, dict[str, Any]] = {}

    for family in PROXY_FAMILIES:

        key = f"{family}_mean_tau"

        er_tau = er_cross.get(key)

        other_tau = other_cross.get(key)

        diff = None

        winner = None

        if er_tau is not None and other_tau is not None:

            diff = float(er_tau - other_tau)

            if abs(diff) < 1e-9:

                winner = "tie"

            elif diff > 0:

                winner = "EndorseRank"

            else:

                winner = other_label

        out[family] = {

            "endorserank_mean_tau": er_tau,

            f"{other_id}_mean_tau": other_tau,

            f"delta_er_minus_{other_id}": diff,

            "higher_alignment": winner,

        }

    return out





def build_method_proxy_matrix(

    method_cross: dict[str, dict[str, float | None]],

    methods: dict[str, str] | None = None,

) -> dict[str, dict[str, float | None]]:

    """method_id -> family -> mean_tau."""

    method_ids = methods if methods is not None else METHODS

    matrix: dict[str, dict[str, float | None]] = {}

    for method_id in method_ids:

        cross = method_cross.get(method_id, {})

        matrix[method_id] = {

            family: cross.get(f"{family}_mean_tau") for family in PROXY_FAMILIES

        }

    return matrix





def build_family_winners(

    matrix: dict[str, dict[str, float | None]],

    methods: dict[str, str] | None = None,

) -> dict[str, str | None]:

    method_ids = methods if methods is not None else METHODS

    winners: dict[str, str | None] = {}

    for family in PROXY_FAMILIES:

        best_method: str | None = None

        best_tau: float | None = None

        for method_id in method_ids:

            row = matrix.get(method_id, {})

            tau = row.get(family)

            if tau is None:

                continue

            if best_tau is None or tau > best_tau:

                best_tau = tau

                best_method = method_id

        winners[family] = best_method

    return winners





def _build_method_cross(

    merged: pd.DataFrame,

    methods: dict[str, str],

) -> tuple[dict[str, dict[str, dict[str, Any]]], dict[str, dict[str, float | None]]]:

    method_results: dict[str, dict[str, dict[str, Any]]] = {}

    method_cross: dict[str, dict[str, float | None]] = {}

    for method_id, score_col in methods.items():

        if score_col not in merged.columns:

            continue

        res = evaluate_method(merged, score_col, ALL_PROXIES)

        method_results[method_id] = res

        method_cross[method_id] = _cross_proxy_means(res)

    return method_results, method_cross





def _tau_safe(x: np.ndarray, y: np.ndarray) -> float | None:

    if x.size < 5 or np.unique(x).size < 2 or np.unique(y).size < 2:

        return None

    t, _ = kendalltau(x, y)

    if t is None or not np.isfinite(t):

        return None

    return float(t)





def _percentile_ci(samples: list[float], ci: float) -> tuple[float | None, float | None]:

    if not samples:

        return None, None

    arr = np.asarray(samples, dtype=float)

    lo = float(np.percentile(arr, (1.0 - ci) / 2.0 * 100.0))

    hi = float(np.percentile(arr, (1.0 + ci) / 2.0 * 100.0))

    return lo, hi





# Paired contrasts reported with bootstrap intervals on the difference. Each

# entry is (label, (method_a, family_or_proxy_a), (method_b, family_or_proxy_b), group).

# Family names resolve to family mean tau; proxy names resolve to a single proxy.

# Group "primary" = EndorseRank vs AWP ("endorserank_vt", "awp_paper");

# "hybrid" = coupled/seeded operators against the layer that leads each family,

# the allowance layer ("endorserank", C-PR at lambda = 1) or the transfer layer

# ("awp", lambda = 0) walked alone, as in the secondary rule of 14 September;

# "hybrid_single" = the coupled operator against EndorseRank and AWP.

TAU_DIFF_CONTRASTS: tuple[tuple[str, tuple[str, str], tuple[str, str], str], ...] = (

    ("EndorseRank allowance minus EndorseRank transfer", ("endorserank_vt", "allowance"), ("endorserank_vt", "transfer"), "primary"),

    ("AWP transfer minus EndorseRank transfer", ("awp_paper", "transfer"), ("endorserank_vt", "transfer"), "primary"),

    ("EndorseRank allowance minus AWP allowance", ("endorserank_vt", "allowance"), ("awp_paper", "allowance"), "primary"),

    ("AWP sybil-stability minus EndorseRank sybil-stability", ("awp_paper", "sybil_stability"), ("endorserank_vt", "sybil_stability"), "primary"),

    ("EndorseRank in-approve degree minus EndorseRank in-degree", ("endorserank_vt", "in_approve_degree"), ("endorserank_vt", "in_degree"), "primary"),

    ("C-PR transfer minus C-PR ($\\lambda=0$) transfer", ("coupled_pr", "transfer"), ("awp", "transfer"), "hybrid"),

    ("C-PR allowance minus C-PR ($\\lambda=1$) allowance", ("coupled_pr", "allowance"), ("endorserank", "allowance"), "hybrid"),

    ("C-PR sybil-stability minus C-PR ($\\lambda=0$) sybil-stability", ("coupled_pr", "sybil_stability"), ("awp", "sybil_stability"), "hybrid"),

    ("C-PR sybil-stability minus C-PR ($\\lambda=1$) sybil-stability", ("coupled_pr", "sybil_stability"), ("endorserank", "sybil_stability"), "hybrid"),

    ("S-PR transfer minus C-PR ($\\lambda=0$) transfer", ("seeded_pr", "transfer"), ("awp", "transfer"), "hybrid"),

    ("S-PR allowance minus C-PR ($\\lambda=1$) allowance", ("seeded_pr", "allowance"), ("endorserank", "allowance"), "hybrid"),

    ("S-PR sybil-stability minus C-PR ($\\lambda=0$) sybil-stability", ("seeded_pr", "sybil_stability"), ("awp", "sybil_stability"), "hybrid"),

    ("S-PR sybil-stability minus C-PR ($\\lambda=1$) sybil-stability", ("seeded_pr", "sybil_stability"), ("endorserank", "sybil_stability"), "hybrid"),

    ("C-PR transfer minus AWP transfer", ("coupled_pr", "transfer"), ("awp_paper", "transfer"), "hybrid_single"),

    ("C-PR allowance minus EndorseRank allowance", ("coupled_pr", "allowance"), ("endorserank_vt", "allowance"), "hybrid_single"),

    ("C-PR sybil-stability minus AWP sybil-stability", ("coupled_pr", "sybil_stability"), ("awp_paper", "sybil_stability"), "hybrid_single"),

    ("C-PR sybil-stability minus EndorseRank sybil-stability", ("coupled_pr", "sybil_stability"), ("endorserank_vt", "sybil_stability"), "hybrid_single"),

)





def bootstrap_alignment(

    merged: pd.DataFrame,

    methods: dict[str, str],

    n_boot: int = 400,

    seed: int = 42,

    ci: float = 0.95,

    contrasts: tuple[tuple[str, tuple[str, str], tuple[str, str], str], ...] = TAU_DIFF_CONTRASTS,

) -> dict[str, Any]:

    """Paired bootstrap over wallets for every (method, proxy) Kendall tau.



    One resample index matrix (n_boot x n) is shared by all methods and proxies,

    so differences between any two tau statistics are paired by construction.

    Returns per-proxy CIs, family-mean CIs, the inter-method CI, and the

    contrast table (delta tau with percentile CI and bootstrap share > 0).

    """

    n = len(merged)

    rng = np.random.default_rng(seed)

    idx_matrix = rng.integers(0, n, size=(n_boot, n))



    score_arrays: dict[str, np.ndarray] = {}

    for method_id, col in methods.items():

        if col in merged.columns:

            score_arrays[method_id] = merged[col].astype(float).to_numpy()

    proxy_arrays: dict[str, np.ndarray] = {

        p: merged[p].astype(float).to_numpy() for p in ALL_PROXIES if p in merged.columns

    }



    # per (method, proxy): list of resampled tau

    resampled: dict[str, dict[str, list[float]]] = {m: {} for m in score_arrays}

    point: dict[str, dict[str, float | None]] = {m: {} for m in score_arrays}

    for m, s in score_arrays.items():

        for p, y in proxy_arrays.items():

            mask = np.isfinite(s) & np.isfinite(y)

            point[m][p] = _tau_safe(s[mask], y[mask])

            vals: list[float] = []

            for b in range(n_boot):

                idx = idx_matrix[b]

                mb = mask[idx]

                t = _tau_safe(s[idx][mb], y[idx][mb])

                if t is not None:

                    vals.append(t)

            resampled[m][p] = vals



    proxy_ci: dict[str, dict[str, dict[str, Any]]] = {}

    for m in resampled:

        proxy_ci[m] = {}

        for p, vals in resampled[m].items():

            lo, hi = _percentile_ci(vals, ci)

            proxy_ci[m][p] = {

                "kendall_tau": point[m][p],

                "ci_low": lo,

                "ci_high": hi,

                "n_boot": len(vals),

            }



    # family means per resample (mean over proxies present in that resample)

    family_samples: dict[str, dict[str, np.ndarray]] = {m: {} for m in resampled}

    family_ci: dict[str, dict[str, dict[str, Any]]] = {m: {} for m in resampled}

    for m in resampled:

        for family, proxies in PROXY_FAMILIES.items():

            cols = [np.asarray(resampled[m][p], dtype=float) for p in proxies if p in resampled[m]]

            cols = [c for c in cols if c.size == n_boot]

            if not cols:

                continue

            fam = np.mean(np.vstack(cols), axis=0)

            family_samples[m][family] = fam

            lo, hi = _percentile_ci(fam.tolist(), ci)

            pts = [point[m][p] for p in proxies if point[m].get(p) is not None]

            family_ci[m][family] = {

                "mean_tau": float(np.mean(pts)) if pts else None,

                "ci_low": lo,

                "ci_high": hi,

                "n_boot": int(fam.size),

            }



    inter_method_ci: dict[str, Any] = {}

    if "endorserank_vt" in score_arrays and "awp_paper" in score_arrays:

        a = score_arrays["endorserank_vt"]

        b_arr = score_arrays["awp_paper"]

        mask = np.isfinite(a) & np.isfinite(b_arr)

        vals = []

        for b in range(n_boot):

            idx = idx_matrix[b]

            mb = mask[idx]

            t = _tau_safe(a[idx][mb], b_arr[idx][mb])

            if t is not None:

                vals.append(t)

        lo, hi = _percentile_ci(vals, ci)

        inter_method_ci = {

            "kendall_tau": _tau_safe(a[mask], b_arr[mask]),

            "ci_low": lo,

            "ci_high": hi,

            "n_boot": len(vals),

        }



    def _resolve(spec: tuple[str, str]) -> tuple[np.ndarray | None, float | None]:

        m, key = spec

        if key in PROXY_FAMILIES:

            fam = family_samples.get(m, {}).get(key)

            pt = family_ci.get(m, {}).get(key, {}).get("mean_tau")

            return fam, pt

        vals = resampled.get(m, {}).get(key)

        arr = np.asarray(vals, dtype=float) if vals is not None and len(vals) == n_boot else None

        return arr, point.get(m, {}).get(key)



    tau_diff: list[dict[str, Any]] = []

    for label, spec_a, spec_b, group in contrasts:

        arr_a, pt_a = _resolve(spec_a)

        arr_b, pt_b = _resolve(spec_b)

        if arr_a is None or arr_b is None or pt_a is None or pt_b is None:

            continue

        delta = arr_a - arr_b

        lo, hi = _percentile_ci(delta.tolist(), ci)

        tau_diff.append(

            {

                "label": label,

                "group": group,

                "a": {"method": spec_a[0], "key": spec_a[1], "tau": pt_a},

                "b": {"method": spec_b[0], "key": spec_b[1], "tau": pt_b},

                "delta_tau": float(pt_a - pt_b),

                "ci_low": lo,

                "ci_high": hi,

                "share_positive": float(np.mean(delta > 0)),

                "n_boot": int(delta.size),

            }

        )



    return {

        "n_boot": n_boot,

        "seed": seed,

        "ci_level": ci,

        "n_wallets": n,

        "methods": sorted(score_arrays),

        "proxy_ci": proxy_ci,

        "family_ci": family_ci,

        "inter_method_ci": inter_method_ci,

        "tau_diff": tau_diff,

    }





def build_alignment_report(

    merged: pd.DataFrame,

    methods: dict[str, str] | None = None,

    bootstrap: dict[str, Any] | None = None,

) -> dict[str, Any]:

    """Full alignment report for methods across six proxy families.



    ``bootstrap`` = {"n_boot": int, "seed": int, "methods": {id: col}} enables the

    paired wallet bootstrap for the listed methods (default: BOOTSTRAP_METHODS).

    """

    methods_dict = methods if methods is not None else METHODS

    method_results, method_cross = _build_method_cross(merged, methods_dict)



    matrix = build_method_proxy_matrix(method_cross, methods_dict)

    family_winners = build_family_winners(matrix, methods_dict)



    er = method_results.get("endorserank_vt", {})

    awp_res = method_results.get("awp_paper", {})

    er_cross = method_cross.get("endorserank_vt", _cross_proxy_means(er))

    awp_cross = method_cross.get("awp_paper", _cross_proxy_means(awp_res))



    inter_method: dict[str, Any] = {}

    if "endorserank_vt_score" in merged.columns and "awp_paper_score" in merged.columns:

        inter_method = _correlate(merged["endorserank_vt_score"], merged["awp_paper_score"])



    boot: dict[str, Any] = {}

    if bootstrap:

        boot_methods = bootstrap.get("methods") or {

            k: v

            for k, v in methods_dict.items()

            if k in BOOTSTRAP_METHODS and v in merged.columns

        }

        boot = bootstrap_alignment(

            merged,

            boot_methods,

            n_boot=int(bootstrap.get("n_boot", 400)),

            seed=int(bootstrap.get("seed", 42)),

        )

        for m, per_proxy in boot["proxy_ci"].items():

            for p, ci_row in per_proxy.items():

                if m in method_results and p in method_results[m]:

                    method_results[m][p]["ci_low"] = ci_row["ci_low"]

                    method_results[m][p]["ci_high"] = ci_row["ci_high"]

                    method_results[m][p]["n_boot"] = ci_row["n_boot"]

        if boot.get("inter_method_ci"):

            inter_method = {**inter_method, **{k: v for k, v in boot["inter_method_ci"].items() if k != "kendall_tau"}}



    return {

        "methods": method_results,

        "method_cross_proxy": method_cross,

        "method_proxy_matrix": matrix,

        "family_winners": family_winners,

        "endorserank_vt": er,

        "awp_paper": awp_res,

        "endorserank_vt_cross_proxy": er_cross,

        "awp_paper_cross_proxy": awp_cross,

        "method_comparison": _method_comparison(er_cross, awp_cross, "awp_paper", "AWP"),

        "inter_method": inter_method,

        "bootstrap": boot,

        "n_wallets": len(merged),

    }





def build_six_aave_alignment_report(merged: pd.DataFrame) -> dict[str, Any]:

    """Six-Aave preset alignment (EndorseRank, AWP, four Aave W↔W methods)."""

    all_methods = {**SIX_AAVE_METHODS, **SIX_AAVE_DIAGNOSTIC_METHODS}

    method_results, method_cross = _build_method_cross(merged, all_methods)

    matrix = build_method_proxy_matrix(method_cross, SIX_AAVE_METHODS)

    family_winners = build_family_winners(matrix, SIX_AAVE_METHODS)

    er_cross = method_cross.get("endorserank", {})

    awp_cross = method_cross.get("awp", {})

    return {

        "methods": {k: method_results[k] for k in SIX_AAVE_METHODS if k in method_results},

        "method_cross_proxy": {k: method_cross[k] for k in SIX_AAVE_METHODS if k in method_cross},

        "method_proxy_matrix": matrix,

        "family_winners": family_winners,

        "method_comparison": _method_comparison(er_cross, awp_cross, "awp", METHOD_LABELS["awp"]),

        "diagnostic_methods": {

            k: method_cross.get(k, {}) for k in SIX_AAVE_DIAGNOSTIC_METHODS

        },

        "diagnostic_matrix": build_method_proxy_matrix(method_cross, SIX_AAVE_DIAGNOSTIC_METHODS),

        "n_wallets": len(merged),

    }

