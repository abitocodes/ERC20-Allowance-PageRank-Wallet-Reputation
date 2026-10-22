"""Addendum (2026-10-22): C-PR (lambda = 0) minus AWP on the spender labels of W0 and W1.

Reads the published per-contract scores of the revised analysis; the design is in ../README.md (Addendum).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

os.environ["CONTRACT_REP_VARIANT"] = "usd"
EXP = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXP / "scripts"))

from common import PROC, load_config, read_parts  # noqa: E402
from stats import PairedBootstrap  # noqa: E402

APPR, SEND = "future_new_approvers", "future_new_transfer_senders"
WINDOWS = {"W0": "holdout-w0", "W1": "window-w1"}


def main() -> int:
    cfg = load_config()["alignment"]
    out = {}
    for w, folder in WINDOWS.items():
        S = read_parts(PROC / folder / "spender_scores").sort_values("id").reset_index(drop=True)
        boot = PairedBootstrap(len(S), cfg["bootstrap_resamples"], cfg["bootstrap_seed"])
        for c in ("cpr_l0", "awp", APPR, SEND):
            boot.add(c, S[c])
        out[w] = {"n": int(len(S)),
                  "cpr_l0_minus_awp": {lab: boot.contrast(("cpr_l0", lab), ("awp", lab)) for lab in (APPR, SEND)}}
    (HERE / "results_addendum.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    for w, r in out.items():
        for lab, c in r["cpr_l0_minus_awp"].items():
            print(w, lab, f"{c['delta_tau']:+.3f} [{c['ci_low']:.3f}, {c['ci_high']:.3f}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
