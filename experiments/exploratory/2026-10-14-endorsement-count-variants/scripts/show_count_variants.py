"""Print results_count_variants.json: tau with intervals, contrasts, partial tau given 30-day momentum."""

import json
import sys
from pathlib import Path

path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "results_count_variants.json"
r = json.loads(path.read_text(encoding="utf-8"))
L = {"future_new_approvers": "newAppr", "future_new_transfer_senders": "newSend",
     "future_revoke_count": "revoke", "future_drain_owners": "drain"}


def ci(d, key="kendall_tau"):
    if not d or d.get("ci_low") is None:
        return "n/a"
    v = d.get(key, d.get("point", d.get("delta_tau")))
    return f"{v:+.3f} [{d['ci_low']:+.3f}, {d['ci_high']:+.3f}]"


for w in ("w0", "w1"):
    if w not in r:
        continue
    d = r[w]
    print(f"== {w}: spenders {d['spenders']}; graph {d['graph']}")
    print("-- tau_b [95% CI]")
    for m, t in d["taus"].items():
        print(f"  {m:16s} " + "  ".join(f"{L[l]} {ci(t[l])}" for l in L))
    print("-- contrasts (delta tau [95% CI])")
    for k, c in d["contrasts"].items():
        if any(s in k for s in ("future_new_approvers", "future_new_transfer_senders")):
            print(f"  {k:70s} {ci(c, 'delta_tau')}")
    print("-- partial tau given mom30")
    for k, c in d["partial_tau_given_mom30"].items():
        if "revoke" not in k and "drain" not in k:
            print(f"  {k:52s} {ci(c, 'point')}")
    print("-- partial contrasts")
    for k, c in d["partial_contrasts"].items():
        if "revoke" not in k and "drain" not in k:
            print(f"  {k:60s} {ci(c, 'point')}")
    print("-- ties", {m: t["zeros"] for m, t in d["ties"].items()})
if "same_window" in r:
    s = r["same_window"]
    print("== same window (family mean tau)")
    for m in [k for k in s if k != "contrasts"]:
        print(f"  {m:16s}", {f: round(x["mean_tau"], 3) for f, x in s[m].items()})
    for k, c in s["contrasts"].items():
        print(f"  {k:46s} {ci(c, 'delta_tau')}")
