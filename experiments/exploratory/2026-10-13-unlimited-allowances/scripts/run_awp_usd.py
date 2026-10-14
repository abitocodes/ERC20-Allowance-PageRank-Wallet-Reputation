"""Exploratory: AWP with raw USD weights (sum of sigma * usd, the C-PR transfer layer) and AWP's
activity restarts, against the published AWP (sigma * V(usd)). Same cohorts, labels and bootstrap."""
import json, os, sys
from pathlib import Path
os.environ["CONTRACT_REP_VARIANT"] = "usd"
EXP = Path(__file__).resolve().parents[3]  # experiments/
HERE = Path(__file__).resolve().parents[1]  # result summaries (JSON)
RAW = EXP / "data" / "1-raw-blockchain-extracts" / "exploratory-2026-10-13"  # BigQuery downloads
XPROC = EXP / "data" / "2-processed-tables-and-evaluations" / "exploratory-2026-10-13"  # score tables
sys.path.insert(0, str(EXP / "scripts"))
import numpy as np, pandas as pd
from common import GRAPH, load_config, read_parts
from graphs import load_graphs, load_nodes, raw_degrees
from labels import account_types
from scoring import activeness, pagerank_params, scores_on, weighted_pagerank
from stats import PairedBootstrap
APPR, SEND, REV, DRAIN = "future_new_approvers", "future_new_transfer_senders", "future_revoke_count", "future_drain_owners"

def scores(g, ids, p):
    t = g.transfer
    act = activeness(t["src"], t["dst"], t["max_sig"])
    S = pd.DataFrame(index=ids)
    for name, w in (("awp", "w_awp"), ("awp_usd", "w_raw")):
        s, _ = weighted_pagerank(t["src"], t["dst"], t[w], teleport=act, **p)
        S[name] = scores_on(ids, s).to_numpy()
    S["tdeg"] = raw_degrees(g, ids)["in_degree_other"].to_numpy()
    return S

def boot(S, L, labels, cfg):
    b = PairedBootstrap(len(S), cfg["alignment"]["bootstrap_resamples"], cfg["alignment"]["bootstrap_seed"])
    for c in S: b.add(c, S[c])
    for c in L.columns: b.add(c, L[c])
    b.prefetch([(m, l) for m in S for l in labels], workers=8)
    return b

def main():
    cfg = load_config(); p = pagerank_params(cfg)
    nodes = load_nodes(); addr = nodes.set_index("address")["id"]; kinds = account_types()
    out = {}
    for w, tag, labname in (("w0", "t1", "labels_w0"), ("w1", "tobs", "labels_w1")):
        g = load_graphs(tag)
        lab = read_parts(GRAPH / labname); lab = lab[lab["wallet"].map(kinds) == "contract"].copy()
        lab["id"] = lab["wallet"].map(addr)
        lab = lab.dropna(subset=["id"]).astype({"id": np.int64}).sort_values("id").set_index("id")
        labels = [APPR, SEND, REV, DRAIN]
        S = scores(g, lab.index.to_numpy(np.int64), p)
        b = boot(S, lab[labels], labels, cfg)
        out[w] = {"taus": {m: {l: b.tau(m, l) for l in labels} for m in S},
                  "contrasts": {f"awp_usd - awp | {l}": b.contrast(("awp_usd", l), ("awp", l)) for l in labels}
                  | {f"awp_usd - tdeg | {l}": b.contrast(("awp_usd", l), ("tdeg", l)) for l in labels}}
        print(w, "done", flush=True)
    # same window
    cohort = nodes.loc[nodes["is_cohort"], ["id", "address"]].sort_values("id"); ids = cohort["id"].to_numpy(np.int64)
    g = load_graphs("tobs"); S = scores(g, ids, p).drop(columns="tdeg")
    prox = read_parts(GRAPH / "proxies_tobs").merge(cohort, left_on="wallet", right_on="address").set_index("id").reindex(ids)
    deg = raw_degrees(g, ids)
    P = pd.DataFrame(index=ids)
    P["in_degree"] = prox["in_degree"].astype(float); P["in_value"] = prox["in_value"].astype(float)
    P["in_approve_degree"] = deg["in_approve_degree"]; P["in_approve_value"] = deg["in_approve_value"]
    for c in ("inbound_counterparty_ratio", "transfer_tenure_days", "active_months"): P[c] = prox[c].astype(float)
    fams = {"transfer": ["in_degree", "in_value"], "allowance": ["in_approve_degree", "in_approve_value"],
            "sybil_stability": ["inbound_counterparty_ratio", "transfer_tenure_days", "active_months"]}
    b = boot(S, P, list(P.columns), cfg)
    out["same_window"] = {m: {f: b.family(m, ls) for f, ls in fams.items()} for m in S}
    out["same_window"]["contrasts"] = {f"awp_usd - awp | {f}": b.contrast(("awp_usd", ls), ("awp", ls)) for f, ls in fams.items()}
    (HERE / "results_awp_usd.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print("all done", flush=True)

if __name__ == "__main__":
    main()
