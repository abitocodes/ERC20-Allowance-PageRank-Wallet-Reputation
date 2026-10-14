"""Print results_nodecay.json: taus per score and label, contrasts, same-window families."""
import json, sys
from pathlib import Path
r = json.load(open(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "results_nodecay.json", encoding="utf-8"))
L = ["future_new_approvers", "future_new_transfer_senders", "future_revoke_count", "future_drain_owners"]
for w in ("w0", "w1"):
    if w not in r: continue
    d = r[w]
    print(f"== {w}: spenders {d['spenders']}")
    print(f"{'score':18s}{'newAppr':>10s}{'newSend':>10s}{'revoke':>10s}{'drain':>10s}")
    for m, t in d["taus"].items():
        print(f"{m:18s}" + "".join(f"{t[l]['kendall_tau']:10.3f}" for l in L))
    for k, c in d["contrasts"].items():
        print(f"  {k:58s} {c['delta_tau']:+.3f} [{c['ci_low']:+.3f}, {c['ci_high']:+.3f}]")
if "same_window" in r:
    s = r["same_window"]
    print("== same window")
    for m in ("endorserank", "er_nd"):
        print(f"{m:12s}", {f: round(x["mean_tau"], 3) for f, x in s[m].items()})
    for k, c in s["contrasts"].items():
        print(f"  {k:40s} {c['delta_tau']:+.3f} [{c['ci_low']:+.3f}, {c['ci_high']:+.3f}]")
