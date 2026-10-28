#!/usr/bin/env python3
"""Exploratory check of 28 October 2026 (../README.md, design fixed before the run).

Q1  where the registered lead of the walks over the raw counts sits (four groups of registered spenders);
Q2  whether it comes from time weighting or from propagation (local scores without a walk);
Q3  whether propagation adds anything among deeper spenders, where EndorseRank's closed form fails.

Reads the published per-contract score tables and the pair tables; writes ../results.json.
usage: python scripts/run_recency_depth.py   (from this folder; the experiments scripts are imported)
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

FOLDER = Path(__file__).resolve().parents[1]
EXP = FOLDER.parents[1]
sys.path.insert(0, str(EXP / "scripts"))
from stats import PairedBootstrap  # noqa: E402

DATA = EXP / "data"
PROC = DATA / "2-processed-tables-and-evaluations"
RAW = DATA / "1-raw-blockchain-extracts"
N_BOOT, SEED = 400, 42
APPR, SEND = "future_new_approvers", "future_new_transfer_senders"
SCORES = {
    ("registered", "w0"): PROC / "holdout-w0",
    ("registered", "w1"): PROC / "registered-w1",
    ("usd", "w0"): PROC / "revised-usd" / "holdout-w0",
    ("usd", "w1"): PROC / "revised-usd" / "window-w1",
    ("usd12m", "w0"): PROC / "revised-usd-12m" / "holdout-w0",
    ("usd12m", "w1"): PROC / "revised-usd-12m" / "window-w1",
}
GRAPHS = {"registered": RAW / "graph-tables", "usd12m": RAW / "graph-tables-usd-12m"}
ANCHOR = {"w0": "t1", "w1": "tobs"}
DEGREE_NAMES = {"t1_in_approve_degree": "deg_appr", "in_approve_degree": "deg_appr",
                "t1_in_degree": "deg_send", "in_degree": "deg_send"}


def read_parts(folder: Path, stem: str, columns=None) -> pd.DataFrame:
    parts = sorted(folder.glob(f"{stem}.part*.parquet"))
    if not parts:
        raise SystemExit(f"no {stem}.part*.parquet in {folder}")
    return pd.concat([pd.read_parquet(p, columns=columns) for p in parts], ignore_index=True)


def spenders(analysis: str, win: str) -> pd.DataFrame:
    df = read_parts(SCORES[(analysis, win)], "spender_scores")
    return df.rename(columns={k: v for k, v in DEGREE_NAMES.items() if k in df.columns})


def local_scores(analysis: str, win: str, ids: np.ndarray) -> pd.DataFrame:
    """Recency-weighted counts, weighted in-strengths and depth of each spender, from the pair tables."""
    g, tag = GRAPHS[analysis], ANCHOR[win]
    idx = pd.Index(np.asarray(ids, dtype=np.int64))
    t = read_parts(g, f"transfer_pairs_{tag}", ["src", "dst", "w_awp", "max_sig"])
    t = t[(t["src"] != t["dst"]) & t["dst"].isin(idx)]          # senders other than the spender (raw_degrees)
    a = read_parts(g, f"allow_pairs_{tag}", ["src", "dst", "w_er", "max_sig"])
    pos = a[a["w_er"] > 0]                                       # EndorseRank's edges (closed_form)
    has_in = pd.Index(pos["dst"].unique())
    a = a[a["dst"].isin(idx)]
    pos = pos[pos["dst"].isin(idx)]
    gt, ga = t.groupby("dst"), a.groupby("dst")
    out = pd.DataFrame(index=idx)
    out["n_send_pairs"] = gt["src"].nunique()
    out["rec_send"] = gt["max_sig"].sum()
    out["str_send"] = gt["w_awp"].sum()
    out["n_appr_pairs"] = ga["src"].nunique()
    out["rec_appr"] = ga["max_sig"].sum()
    out["str_appr"] = ga["w_er"].sum()
    out = out.fillna(0.0)
    deeper = pos.assign(src_has_in=pos["src"].isin(has_in)).groupby("dst")["src_has_in"].any()
    out["depth"] = "none"
    out.loc[deeper.index[~deeper.to_numpy()], "depth"] = "one"
    out.loc[deeper.index[deeper.to_numpy()], "depth"] = "deeper"
    return out


def contrasts(frame: pd.DataFrame, specs) -> dict:
    """Paired-bootstrap contrasts tau(a, label) - tau(b, label) inside ``frame``; specs are (key, a, b, label)."""
    b = PairedBootstrap(len(frame), N_BOOT, SEED)
    cols = {c for _, x, y, lab in specs for c in (x, y, lab)}
    for c in cols:
        b.add(c, frame[c])
    out = {"n": int(len(frame)),
           "share_new_approval_pair": float((frame[APPR] > 0).mean()),
           "share_new_sender": float((frame[SEND] > 0).mean())}
    for key, x, y, lab in specs:
        out[key] = b.contrast((x, lab), (y, lab))
    return out


Q1_SPECS = [("awp_minus_degree_send", "awp", "deg_send", SEND),
            ("er_activity_minus_degree_appr", "endorserank_activity", "deg_appr", APPR),
            ("er_minus_degree_appr", "endorserank", "deg_appr", APPR)]
Q2_SPECS = [("recency_minus_degree_send", "rec_send", "deg_send", SEND),
            ("strength_minus_degree_send", "str_send", "deg_send", SEND),
            ("awp_minus_recency_send", "awp", "rec_send", SEND),
            ("recency_minus_degree_appr", "rec_appr", "deg_appr", APPR),
            ("strength_minus_degree_appr", "str_appr", "deg_appr", APPR),
            ("er_activity_minus_recency_appr", "endorserank_activity", "rec_appr", APPR)]
Q3_SPECS = [("er_minus_degree_appr", "endorserank", "deg_appr", APPR),
            ("er_activity_minus_degree_appr", "endorserank_activity", "deg_appr", APPR),
            ("cpr_minus_degree_appr", "cpr_l50", "deg_appr", APPR)]


def degree_check(frame: pd.DataFrame) -> dict:
    return {"send_mismatch": int((frame["n_send_pairs"] != frame["deg_send"]).sum()),
            "appr_mismatch": int((frame["n_appr_pairs"] != frame["deg_appr"]).sum())}


def main() -> int:
    res = {"computed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "design": "README.md (committed before the run)", "n_boot": N_BOOT, "seed": SEED,
           "q1": {}, "q2": {}, "q3": {}, "checks": {}}
    for win in ("w0", "w1"):
        reg, usd, m12 = spenders("registered", win), spenders("usd", win), spenders("usd12m", win)
        kept_w, usd_w = set(m12["wallet"]), set(usd["wallet"])
        reg["group"] = np.where(reg["wallet"].isin(kept_w), "kept",
                                np.where(reg["wallet"].isin(usd_w), "older_five_token", "other_tokens"))
        res["checks"][f"{win}_twelve_month_inside_registered"] = int(m12["wallet"].isin(set(reg["wallet"])).sum())
        res["checks"][f"{win}_twelve_month_n"] = int(len(m12))

        # Q1: the registered scores and labels in four groups
        groups = {"all": reg, **{g: reg[reg["group"] == g] for g in ("kept", "older_five_token", "other_tokens")}}
        res["q1"][win] = {g: contrasts(fr, Q1_SPECS) for g, fr in groups.items()}

        # Q2 and Q3 need the local scores of both analyses
        loc_reg = local_scores("registered", win, reg["id"].to_numpy())
        loc_m12 = local_scores("usd12m", win, m12["id"].to_numpy())
        reg2 = reg.join(loc_reg, on="id")
        m122 = m12.join(loc_m12, on="id")
        res["checks"][f"{win}_registered_degrees"] = degree_check(reg2)
        res["checks"][f"{win}_twelve_month_degrees"] = degree_check(m122)
        groups2 = {"all": reg2, **{g: reg2[reg2["group"] == g] for g in ("kept", "older_five_token", "other_tokens")}}
        res["q2"][win] = {"registered": {g: contrasts(fr, Q2_SPECS) for g, fr in groups2.items()},
                          "twelve_month": contrasts(m122, Q2_SPECS)}

        res["q3"][win] = {}
        for name, fr in (("twelve_month", m122), ("registered", reg2)):
            res["q3"][win][name] = {d: contrasts(fr[fr["depth"] == d], Q3_SPECS) for d in ("one", "deeper")}
            res["q3"][win][name]["none_n"] = int((fr["depth"] == "none").sum())
        print(f"{win}: done")
    (FOLDER / "results.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    print("wrote", FOLDER / "results.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
