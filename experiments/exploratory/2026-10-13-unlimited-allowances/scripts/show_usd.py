import json, sys
r = json.load(open(sys.argv[1], encoding="utf-8"))
L = ["future_new_approvers", "future_new_transfer_senders", "future_revoke_count", "future_drain_owners"]
for w in ("w0", "w1"):
    if w not in r: continue
    d = r[w]
    print(f"== {w}: spenders {d['spenders']}; graph {d['graph']}")
    print(f"{'score':20s}{'newAppr':>10s}{'newSend':>10s}{'revoke':>10s}{'drain':>10s}{'zeros':>8s}")
    for m, t in d["taus"].items():
        print(f"{m:20s}" + "".join(f"{t[l]['kendall_tau']:10.3f}" for l in L) + f"{d['zeros'][m]:8d}")
    for k, c in d["contrasts"].items():
        if c and ("future_new_approvers" in k or "future_new_transfer_senders" in k):
            print(f"  {k:62s} {c['delta_tau']:+.3f} [{c['ci_low']:+.3f}, {c['ci_high']:+.3f}]")
if "same_window" in r:
    s = r["same_window"]
    print("== same window")
    for m in [k for k in s if k not in ("contrasts", "zeros")]:
        print(f"{m:14s}", {f: round(x["mean_tau"], 3) for f, x in s[m].items()}, "zeros", s["zeros"][m])
    for k, c in s["contrasts"].items():
        print(f"  {k:44s} {c['delta_tau']:+.3f} [{c['ci_low']:+.3f}, {c['ci_high']:+.3f}]")
