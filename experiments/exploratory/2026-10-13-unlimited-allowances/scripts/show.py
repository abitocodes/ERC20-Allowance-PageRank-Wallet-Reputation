import json, sys
r = json.load(open(sys.argv[1], encoding="utf-8"))
L = ["future_new_approvers", "new_appr_finite", "new_appr_unlimited", "future_new_transfer_senders", "future_revoke_count", "future_drain_owners"]
short = {"future_new_approvers": "newAppr", "new_appr_finite": "newApprFin", "new_appr_unlimited": "newApprUnl",
         "future_new_transfer_senders": "newSend", "future_revoke_count": "revoke", "future_drain_owners": "drain"}
for w in ("w0", "w1"):
    if w not in r: continue
    d = r[w]
    print(f"== {w}: spenders {d['spenders']}, label mismatch {d['label_mismatch_new_approvers']}, no allowance {d['spenders_without_allowance']}, newAppr {d['new_appr_total']} fin {d['new_appr_finite_total']} unl {d['new_appr_unlimited_total']}")
    print(f"{'score':28s}" + "".join(f"{short[l]:>12s}" for l in L))
    for m, t in d["taus"].items():
        print(f"{m:28s}" + "".join(f"{t[l]['kendall_tau']:12.3f}" for l in L))
    print("-- contrasts (dtau [CI])")
    for k, c in d["contrasts"].items():
        if c and any(s in k for s in ("future_new_approvers", "new_appr_finite", "future_new_transfer_senders")):
            print(f"{k:60s} {c['delta_tau']:+.3f} [{c['ci_low']:+.3f}, {c['ci_high']:+.3f}]")
    p = r.get(w + "_premise")
    if p:
        print("-- premise: tau(unlimited share of a spender's owners, label)", "n", p["n"], "quantiles", [round(q, 2) for q in p["share_quantiles"]])
        for l, t in p["taus"].items():
            print(f"   {l:30s} {t['kendall_tau']:+.3f} [{t['ci_low']:+.3f}, {t['ci_high']:+.3f}]")
        for q in p["by_quartile"]:
            print("  ", q)
if "same_window" in r:
    s = r["same_window"]
    print("== same window (family mean tau)")
    for v in [k for k in s if k not in ("contrasts", "zeros")]:
        print(v, {f: round(x["mean_tau"], 3) for f, x in s[v].items()})
    for k, c in s["contrasts"].items():
        print(f"{k:40s} {c['delta_tau']:+.3f} [{c['ci_low']:+.3f}, {c['ci_high']:+.3f}]")
    print("zeros", s["zeros"])
