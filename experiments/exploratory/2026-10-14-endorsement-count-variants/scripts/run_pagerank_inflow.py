"""Inflow of the PageRank forms (run_pagerank_forms.py): the mass a spender receives over its in-edges,
d sum_u r(u) P[u, v] = r(v) - (1 - d + d M) t(v), i.e. its PageRank minus what its own restart mass gives it.
On a spender all of whose owners have no in-edges this is proportional to the count variant."""

import json
import os
import sys
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
from scoring import pagerank_params, weighted_pagerank  # noqa: E402
from stats import PairedBootstrap, kendall_tau_b  # noqa: E402

APPR, SEND = "future_new_approvers", "future_new_transfer_senders"
FORMS = {"in_v2_sig": ("e_v2", False), "in_v3_hl30": ("e_v3", False), "in_v2_sig_cap10": ("e_v2", True), "in_v3_hl30_cap10": ("e_v3", True)}


def main():
    cfg = load_config(); p = pagerank_params(cfg)
    res = {"definitions": __doc__}
    for w, tag in (("w0", "t1"), ("w1", "tobs")):
        g = load_graphs(tag)
        x = read_parts(RAW / f"x_nodecay_pairs_{tag}", columns=["src", "dst", "min_age_days"])
        a = g.allow.merge(x, on=["src", "dst"], how="inner", validate="one_to_one")
        age = a["min_age_days"].to_numpy()
        a = a.assign(e_v2=1.0 / (1.0 + np.exp(0.01 * (age - 180.0))), e_v3=0.5 ** (age / 30.0))
        cap = np.minimum(1.0, 10.0 / a.groupby("src").size())
        S = pd.read_parquet(XPROC / f"count_variants_{w}.parquet")
        ids = S.index.to_numpy(np.int64)
        has_in = np.zeros(int(max(a["src"].max(), a["dst"].max())) + 1, dtype=bool)
        has_in[a["dst"].to_numpy()] = True
        depth_one = ~pd.Series(has_in[a["src"].to_numpy()]).groupby(a["dst"].to_numpy()).any().reindex(ids).fillna(False).to_numpy()
        agree = {}
        for name, (col, capped) in FORMS.items():
            mass = a.groupby("src")[col].sum()
            t = mass * cap if capped else mass
            r, _ = weighted_pagerank(a["src"], a["dst"], a[col], teleport=t, **p)
            out = mass.reindex(a["src"].to_numpy()).to_numpy()
            flow = r.reindex(a["src"].to_numpy()).to_numpy() * a[col].to_numpy() / out
            S[name] = pd.Series(flow).groupby(a["dst"].to_numpy()).sum().reindex(ids).fillna(0.0).to_numpy()
            cnt = S[name[3:]].to_numpy()
            agree[name] = {"tau_depth_one": kendall_tau_b(S[name].to_numpy()[depth_one], cnt[depth_one]),
                           "tau_deeper": kendall_tau_b(S[name].to_numpy()[~depth_one], cnt[~depth_one])}
        b = PairedBootstrap(len(S), cfg["alignment"]["bootstrap_resamples"], cfg["alignment"]["bootstrap_seed"])
        cols = ["endorserank", "deg"] + [n[3:] for n in FORMS] + list(FORMS)
        for c in cols + [APPR, SEND]:
            b.add(c, S[c])
        b.prefetch([(m, l) for m in cols for l in (APPR, SEND)], workers=8)
        res[w] = {"agreement_with_count_form": agree,
                  "taus": {m: {l: b.tau(m, l) for l in (APPR, SEND)} for m in cols},
                  "contrasts": {f"{n} - {k} | {l}": b.contrast((n, l), (k, l))
                                for n in FORMS for k in (n[3:], "endorserank", "deg") for l in (APPR, SEND)}}
        S[list(FORMS)].to_parquet(XPROC / f"pagerank_inflow_{w}.parquet")
        (HERE / "results_pagerank_inflow.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
        print(w, "done", flush=True)


if __name__ == "__main__":
    main()
