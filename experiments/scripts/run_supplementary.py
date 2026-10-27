#!/usr/bin/env python3
"""Contrasts computed after the labels were known, outside every rule, from the saved scores.

- EndorseRank with activity restarts against the in-approve degree on new approval pairs
  (W0 and W1), and against EndorseRank;
- EndorseRank against AWP on both spender labels in W1 (W0 is in the holdout summary);
- revised analysis only: C-PR (lambda = 0.5) against every other score of the plan and the
  two raw degrees, on both spender labels in W0 and W1 and on the W1 traders' liquidation-free
  close rate (only the contrasts that no rule and no earlier summary already reports); C-PR
  against AWP among the spenders that had received a transfer before the freeze; C-PR against
  the single-layer walk of the other edge type on the same-window families.
Same paired bootstrap as the drivers (400 resamples, seed 42; the resamples of a cohort depend
only on its size, so every contrast here is paired with the published ones). Writes
data/2-.../supplementary/supplementary.json.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import PROC, REVISED, W1_DIR, load_config, read_parts, save_json  # noqa: E402
from stats import PairedBootstrap  # noqa: E402

APPR, SEND, LIQ = "future_new_approvers", "future_new_transfer_senders", "liquidation_free_rate"
SUFFIX = {APPR: "appr", SEND: "send", LIQ: "liq"}
# The same-window families of run_same_window.py.
FAMILIES = {"transfer": ["in_degree", "in_value"], "allowance": ["in_approve_degree", "in_approve_value"]}


def boot(cfg, n: int) -> PairedBootstrap:
    return PairedBootstrap(n, cfg["alignment"]["bootstrap_resamples"], cfg["alignment"]["bootstrap_seed"])


def run(frame, deg_col, cfg):
    b = boot(cfg, len(frame))
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


def cpr_contrasts(b: PairedBootstrap, pairs) -> dict:
    """C-PR (lambda = 0.5) minus each (key, column, label) of ``pairs``."""
    return {f"cpr_minus_{key}_{SUFFIX[lab]}": b.contrast(("cpr_l50", lab), (col, lab)) for key, col, lab in pairs}


def run_cpr(frame, deg_col, indeg_col, done, cfg):
    """C-PR against the other scores and the raw degrees on both spender labels, without the
    contrasts in ``done`` (reported by a rule or by the holdout summary), and among the
    spenders that had received a transfer from another address before the freeze."""
    others = {"l100": "cpr_l100", "l0": "cpr_l0", "er": "endorserank", "er_activity": "endorserank_activity",
              "awp": "awp", "spr": "spr", "degree": deg_col, "in_degree": indeg_col}
    b = boot(cfg, len(frame))
    for c in ("cpr_l50", *others.values(), APPR, SEND):
        b.add(c, frame[c])
    pairs = [(k, c, lab) for k, c in others.items() for lab in (APPR, SEND) if (k, SUFFIX[lab]) not in done]
    out = cpr_contrasts(b, pairs)

    recv = frame[indeg_col] > 0
    fr = frame.loc[recv]
    br = boot(cfg, len(fr))
    for c in ("cpr_l50", "awp", deg_col, APPR, SEND):
        br.add(c, fr[c])
    out["recv_n"] = int(len(fr))
    for lab in (APPR, SEND):
        out[f"recv_cpr_tau_{SUFFIX[lab]}"] = br.tau("cpr_l50", lab)
        out[f"recv_cpr_minus_awp_{SUFFIX[lab]}"] = br.contrast(("cpr_l50", lab), ("awp", lab))
    out["recv_cpr_minus_degree_appr"] = br.contrast(("cpr_l50", APPR), (deg_col, APPR))
    return out


def run_cpr_traders(frame, cfg):
    """W1 traders: C-PR minus the scores that rule B (F3, F5 against lambda = 0 and 1), its AWP
    sensitivity analysis and the EndorseRank results of the W1 summary leave out."""
    cols = {"er_activity": "endorserank_activity", "spr": "spr",
            "degree": "in_approve_degree", "in_degree": "in_degree"}
    b = boot(cfg, len(frame))
    for c in ("cpr_l50", *cols.values(), LIQ):
        b.add(c, frame[c])
    out = cpr_contrasts(b, [(k, c, LIQ) for k, c in cols.items()])
    out["traders_n"] = int(len(frame))
    return out


def run_same(frame, cfg):
    """C-PR against the single-layer walk of the other edge type on the same-window families."""
    b = boot(cfg, len(frame))
    for c in ("cpr_l50", "endorserank", "awp", *FAMILIES["transfer"], *FAMILIES["allowance"]):
        b.add(c, frame[c])
    return {
        "cpr_minus_er_transfer": b.contrast(("cpr_l50", FAMILIES["transfer"]), ("endorserank", FAMILIES["transfer"])),
        "cpr_minus_awp_allowance": b.contrast(("cpr_l50", FAMILIES["allowance"]), ("awp", FAMILIES["allowance"])),
        "n": len(frame),
    }


def main() -> int:
    cfg = load_config()
    w0 = read_parts(PROC / "holdout-w0" / "spender_scores")
    w1 = read_parts(PROC / W1_DIR / "spender_scores")
    out = {"w0": run(w0, "t1_in_approve_degree", cfg), "w1": run(w1, "in_approve_degree", cfg)}
    if REVISED:
        # W0: contrasts_prefixed holds C-PR minus lambda=1 on approvals and minus lambda=0 on senders,
        # contrasts_after C-PR minus lambda=0, EndorseRank and AWP on approvals and minus AWP on senders.
        done_w0 = {("l100", "appr"), ("l0", "send"), ("l0", "appr"), ("er", "appr"), ("awp", "appr"), ("awp", "send")}
        # W1: rule B (F1, F2 against lambda=0; F6a against lambda=1 on approvals) and its AWP sensitivity
        # analysis on both labels; EndorseRank on approvals in the W1 summary.
        done_w1 = {("l0", "appr"), ("l0", "send"), ("l100", "appr"), ("awp", "appr"), ("awp", "send"), ("er", "appr")}
        out["w0"].update(run_cpr(w0, "t1_in_approve_degree", "t1_in_degree", done_w0, cfg))
        out["w1"].update(run_cpr(w1, "in_approve_degree", "in_degree", done_w1, cfg))
        out["w1"].update(run_cpr_traders(read_parts(PROC / W1_DIR / "trader_scores"), cfg))
        out["same"] = run_same(read_parts(PROC / "same-window" / "cohort_scores"), cfg)
    save_json(out, PROC / "supplementary" / "supplementary.json")
    for w, d in out.items():
        for k, v in d.items():
            if isinstance(v, dict) and "delta_tau" in v:
                print(w, k, round(v["delta_tau"], 3), [round(v["ci_low"], 3), round(v["ci_high"], 3)])
            elif isinstance(v, dict):
                print(w, k, round(v["kendall_tau"], 3), [round(v["ci_low"], 3), round(v["ci_high"], 3)])
    return 0


if __name__ == "__main__":
    sys.exit(main())
