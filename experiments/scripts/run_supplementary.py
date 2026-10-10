#!/usr/bin/env python3
"""Contrasts computed after the labels were known, outside every rule, from the saved scores.

- EndorseRank with activity restarts against the in-approve degree on new approval pairs
  (W0 and W1), and against EndorseRank;
- EndorseRank against AWP on both spender labels in W1 (W0 is in the holdout summary).
Same paired bootstrap as the drivers (400 resamples, seed 42). Writes
data/2-.../supplementary/supplementary.json.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import PROC, W1_DIR, load_config, read_parts, save_json  # noqa: E402
from stats import PairedBootstrap  # noqa: E402

APPR, SEND = "future_new_approvers", "future_new_transfer_senders"


def run(frame, deg_col, cfg):
    b = PairedBootstrap(len(frame), cfg["alignment"]["bootstrap_resamples"], cfg["alignment"]["bootstrap_seed"])
    for c in ("endorserank", "endorserank_activity", "awp", deg_col, APPR, SEND):
        b.add(c, frame[c])
    return {
        "er_activity_minus_degree_appr": b.contrast(("endorserank_activity", APPR), (deg_col, APPR)),
        "er_activity_minus_er_appr": b.contrast(("endorserank_activity", APPR), ("endorserank", APPR)),
        "er_activity_minus_er_send": b.contrast(("endorserank_activity", SEND), ("endorserank", SEND)),
        "er_minus_awp_appr": b.contrast(("endorserank", APPR), ("awp", APPR)),
        "er_minus_awp_send": b.contrast(("endorserank", SEND), ("awp", SEND)),
        "n": len(frame),
    }


def main() -> int:
    cfg = load_config()
    w0 = read_parts(PROC / "holdout-w0" / "spender_scores")
    w1 = read_parts(PROC / W1_DIR / "spender_scores")
    out = {"w0": run(w0, "t1_in_approve_degree", cfg), "w1": run(w1, "in_approve_degree", cfg)}
    save_json(out, PROC / "supplementary" / "supplementary.json")
    for w, d in out.items():
        for k, v in d.items():
            if isinstance(v, dict):
                print(w, k, round(v["delta_tau"], 3), [round(v["ci_low"], 3), round(v["ci_high"], 3)])
    return 0


if __name__ == "__main__":
    sys.exit(main())
