import json, sys, time
from pathlib import Path
import pandas as pd, pyarrow.parquet as pq, requests, glob
EXP = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parents[1]
RAW = EXP / "data" / "1-raw-blockchain-extracts" / "exploratory-2026-10-13"
df = pd.concat([pq.read_table(p).to_pandas() for p in sorted(RAW.glob("x_bal_check.part*.parquet"))])
URL = "https://arb1.arbitrum.io/rpc"
dec = {"0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9": 6, "0xaf88d065e77c8cc2239327c5edb3a432268e5831": 6,
       "0x2f2a2543b76a4166549f7aab2e75bef0aefc5b0f": 8, "0x82af49447d8a07e3bd95bd0d56f35241523fbab1": 18,
       "0x912ce59144191c1204e64559fe8253a0e49e6548": 18}
sym = {"0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9": "USDT0", "0xaf88d065e77c8cc2239327c5edb3a432268e5831": "USDC",
       "0x2f2a2543b76a4166549f7aab2e75bef0aefc5b0f": "WBTC", "0x82af49447d8a07e3bd95bd0d56f35241523fbab1": "WETH",
       "0x912ce59144191c1204e64559fe8253a0e49e6548": "ARB"}
s = requests.Session()
bn = s.post(URL, json={"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).json()["result"]
rows = df.to_dict("records"); out = []
for i in range(0, len(rows), 25):
    chunk = rows[i:i + 25]
    payload = [{"jsonrpc": "2.0", "id": j, "method": "eth_call",
                "params": [{"to": r["token"], "data": "0x70a08231" + r["owner"][2:].rjust(64, "0")}, bn]}
               for j, r in enumerate(chunk)]
    for attempt in range(10):
        try:
            res = s.post(URL, json=payload, timeout=60).json()
            if isinstance(res, list) and all("result" in x for x in res): break
        except Exception: pass
        time.sleep(2 + attempt)
    res = sorted(res, key=lambda x: x["id"])
    for r, x in zip(chunk, res):
        out.append(int(x["result"], 16) if x.get("result") not in (None, "0x") else None)
    time.sleep(0.2)
df["onchain"] = out
df["sym"] = df["token"].map(sym)
df["d"] = df["token"].map(dec)
tol = df["onchain"].abs().astype(float) * 1e-9 + 10.0 ** (df["d"] - 6)  # 1e-9 relative or 1e-6 token
df["match"] = (df["bal_0930"].clip(lower=0) - df["onchain"].astype(float)).abs() <= tol
df["dormant"] = df["n_w1"] == 0
print("block", int(bn, 16))
print(df.groupby(["sym", df["bal_tobs"].abs() > 1]).agg(n=("match", "size"), match=("match", "mean")).round(3).to_string())
print("overall match", round(df["match"].mean(), 4), "dormant in W1:", round(df.loc[df.dormant, "match"].mean(), 4), "n", int(df.dormant.sum()))
bad = df[~df["match"]]
print("mismatches", len(bad)); print(bad[["sym", "owner", "bal_tobs", "bal_0930", "onchain", "n_w1"]].head(15).to_string())
df.to_csv(HERE / "bal_check_result.csv", index=False)
