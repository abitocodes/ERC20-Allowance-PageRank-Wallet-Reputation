"""PageRank forms of the count variants (run_count_variants.py), with the same cohorts, labels and bootstrap.

Weighted PageRank r = (1 - d) t + d P^T r + d (dangling mass) t, P[u, v] = e(u,v) / sum_w e(u,w). When the
restart mass of every owner is its own endorsement mass, t_u = c_u sum_w e(u,w), an owner with no in-edges
gets r(u) proportional to t_u and a spender all of whose owners have no in-edges gets
r(v) = d (1 - d + d M) sum_u c_u e(u,v), the count variant, while spenders deeper in the graph still
receive propagated mass. Edge weights e and owner factors c:

  pr_v1_sigV        e = sigma(age) V(usd) per token (w_er)     c = 1
  pr_v2_sig         e = sigma(a_uv)                              c = 1
  pr_v3_hl30        e = 0.5 ** (a_uv / 30)                       c = 1
  pr_v2_sig_cap10   e = sigma(a_uv)                              c = min(1, 10 / n_u)
  pr_v3_hl30_cap10  e = 0.5 ** (a_uv / 30)                       c = min(1, 10 / n_u)
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
RAW = EXP / "data" / "1-raw-blockchain-extracts" / "exploratory-2026-10-14"
XPROC = EXP / "data" / "2-processed-tables-and-evaluations" / "exploratory-2026-10-14"
sys.path.insert(0, str(EXP / "scripts"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from common import load_config, read_parts  # noqa: E402
from graphs import load_graphs  # noqa: E402
from scoring import pagerank_params, scores_on, weighted_pagerank  # noqa: E402
from stats import PairedBootstrap, kendall_tau_b, percentile_ci  # noqa: E402

APPR, SEND = "future_new_approvers", "future_new_transfer_senders"
LABELS = [APPR, SEND]
FORMS = {"pr_v1_sigV": ("e_v1", False), "pr_v2_sig": ("e_v2", False), "pr_v3_hl30": ("e_v3", False),
         "pr_v2_sig_cap10": ("e_v2", True), "pr_v3_hl30_cap10": ("e_v3", True)}


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def main():
    cfg = load_config()
    p = pagerank_params(cfg)
    res = {"definitions": __doc__}
    for w, tag in (("w0", "t1"), ("w1", "tobs")):
        g = load_graphs(tag)
        x = read_parts(RAW / f"x_nodecay_pairs_{tag}", columns=["src", "dst", "min_age_days"])
        a = g.allow.merge(x, on=["src", "dst"], how="inner", validate="one_to_one")
        age = a["min_age_days"].to_numpy()
        a = a.assign(e_v1=a["w_er"].to_numpy(), e_v2=1.0 / (1.0 + np.exp(0.01 * (age - 180.0))), e_v3=0.5 ** (age / 30.0))
        n_u = a.groupby("src").size()
        cap = np.minimum(1.0, 10.0 / n_u)
        S = pd.read_parquet(XPROC / f"count_variants_{w}.parquet")
        ids = S.index.to_numpy(np.int64)
        for name, (col, capped) in FORMS.items():
            mass = a.groupby("src")[col].sum()
            t = mass * cap if capped else mass
            r, its = weighted_pagerank(a["src"], a["dst"], a[col], teleport=t, **p)
            S[name] = scores_on(ids, r).to_numpy()
            log(w, name, "iterations", its)
        # depth-one spenders: none of their owners receives an approval itself
        has_in = np.zeros(int(max(a["src"].max(), a["dst"].max())) + 1, dtype=bool)
        has_in[a["dst"].to_numpy()] = True
        deeper = pd.Series(has_in[a["src"].to_numpy()]).groupby(a["dst"].to_numpy()).any()
        depth_one = ~deeper.reindex(ids).fillna(False).to_numpy()
        agree = {}
        for name in FORMS:
            cnt = name[3:]
            agree[name] = {"tau_all": kendall_tau_b(S[name].to_numpy(), S[cnt].to_numpy()),
                           "tau_depth_one": kendall_tau_b(S[name].to_numpy()[depth_one], S[cnt].to_numpy()[depth_one]),
                           "tau_deeper": kendall_tau_b(S[name].to_numpy()[~depth_one], S[cnt].to_numpy()[~depth_one])}
        b = PairedBootstrap(len(S), cfg["alignment"]["bootstrap_resamples"], cfg["alignment"]["bootstrap_seed"])
        cols = ["endorserank", "deg", "mom30"] + [n[3:] for n in FORMS] + list(FORMS)
        for c in cols + LABELS:
            b.add(c, S[c])
        b.prefetch([(m, l) for m in cols for l in LABELS] + [(m, "mom30") for m in cols if m != "mom30"]
                   + [(l, "mom30") for l in LABELS], workers=8)
        taus = {m: {l: b.tau(m, l) for l in LABELS} for m in cols}
        con = {}
        for name in FORMS:
            for l in LABELS:
                con[f"{name} - {name[3:]} | {l}"] = b.contrast((name, l), (name[3:], l))
                con[f"{name} - endorserank | {l}"] = b.contrast((name, l), ("endorserank", l))
                con[f"{name} - deg | {l}"] = b.contrast((name, l), ("deg", l))
        part = {}
        for l in LABELS:
            for m in ("endorserank", "deg", "v2_sig_cap10", "pr_v2_sig_cap10"):
                pxy, pxz, pyz = b.point(m, l), b.point(m, "mom30"), b.point(l, "mom30")
                sxy, sxz, syz = b.samples(m, l), b.samples(m, "mom30"), b.samples(l, "mom30")
                pt = (pxy - pxz * pyz) / np.sqrt((1 - pxz ** 2) * (1 - pyz ** 2))
                s = (sxy - sxz * syz) / np.sqrt((1 - sxz ** 2) * (1 - syz ** 2)) if sxy.size == sxz.size == syz.size == b.n_boot else None
                lo, hi = percentile_ci(s) if s is not None else (None, None)
                part[f"{m} | {l}"] = {"point": float(pt), "ci_low": lo, "ci_high": hi}
        res[w] = {"spenders": int(len(ids)), "depth_one_spenders": int(depth_one.sum()),
                  "agreement_with_count_form": agree, "taus": taus, "contrasts": con, "partial_tau_given_mom30": part}
        S[list(FORMS)].to_parquet(XPROC / f"pagerank_forms_{w}.parquet")
        (HERE / "results_pagerank_forms.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
        log(w, "done")


if __name__ == "__main__":
    main()
