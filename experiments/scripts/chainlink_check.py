#!/usr/bin/env python3
"""Compare the DefiLlama daily prices of the revised analysis with Chainlink feeds read on Arbitrum One.

For the selected tokens and dates (the 15th of every month from October 2023 to
September 2026, and the two freezes), the price of day D in daily_prices_usd.csv (DefiLlama's close of D) is
set against the answer of the token's Chainlink proxy in force at 00:00 UTC of D+1. Proxy rounds are read with
getRoundData (round id = phaseId << 64 | aggregator round), found by k-ary search over the rounds of each phase,
so no archive node is needed. ETH-quoted feeds are skipped.

Writes data/0-usd-token-list-and-prices/chainlink_check.csv and chainlink_check.json.
Usage: python scripts/chainlink_check.py [--tokens N] [--rpc URL]
"""

from __future__ import annotations

import argparse
import sys
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import USD_INPUTS, load_config, save_json  # noqa: E402

SEL_LATEST, SEL_ROUND, SEL_PHASE, SEL_DEC = "0xfeaf968c", "0x9a6fc8f5", "0x58303b10", "0x313ce567"


class Proxy:
    def __init__(self, session: requests.Session, url: str, address: str):
        self.s, self.url, self.to = session, url, address
        self.cache: dict[int, dict | None] = {}

    def _calls(self, datas: list[str]) -> list[str | None]:
        payload = [{"jsonrpc": "2.0", "id": i, "method": "eth_call", "params": [{"to": self.to, "data": d}, "latest"]}
                   for i, d in enumerate(datas)]
        for attempt in range(12):
            try:
                resp = self.s.post(self.url, json=payload, timeout=60).json()
                if isinstance(resp, list):
                    by = {r["id"]: r for r in resp}
                    if all(i in by and ("result" in by[i] or "revert" in str(by[i].get("error", "")).lower())
                           for i in range(len(datas))):
                        return [by[i].get("result") for i in range(len(datas))]
            except (requests.RequestException, ValueError):
                pass
            time.sleep(min(2 ** attempt, 30))
        raise RuntimeError(f"RPC {self.url} kept failing for proxy {self.to}")

    @staticmethod
    def _decode(h: str | None) -> dict | None:
        if not h or len(h) < 2 + 64 * 5:
            return None
        w = [int(h[2 + 64 * i:2 + 64 * (i + 1)], 16) for i in range(5)]
        ans = w[1] - 2 ** 256 if w[1] >= 2 ** 255 else w[1]
        return {"round": w[0], "answer": ans, "updated": w[3]}

    def rounds(self, ids: list[int]) -> list[dict | None]:
        need = [i for i in ids if i not in self.cache]
        for k in range(0, len(need), 10):
            part = need[k:k + 10]
            for i, h in zip(part, self._calls([SEL_ROUND + format(i, "064x") for i in part])):
                r = self._decode(h)
                self.cache[i] = r if r and r["updated"] > 0 else None
        return [self.cache[i] for i in ids]

    def setup(self) -> None:
        latest, phase, dec = self._calls([SEL_LATEST, SEL_PHASE, SEL_DEC])
        self.decimals = int(dec, 16)
        cur = int(phase, 16)
        last = self._decode(latest)["round"] - (cur << 64)
        self.phases = []
        for ph in range(1, cur + 1):
            self.phases.append((ph, last if ph == cur else self._max_round(ph)))

    def _max_round(self, ph: int) -> int:
        base, lo, hi = ph << 64, 0, 1
        while self.rounds([base + hi])[0]:
            lo, hi = hi, hi * 2
        while hi - lo > 1:
            mid = (lo + hi) // 2
            lo, hi = (mid, hi) if self.rounds([base + mid])[0] else (lo, mid)
        return lo

    def at(self, t: int) -> dict | None:
        """The round in force at time t (largest updatedAt <= t), searching the latest phase that started by t."""
        for ph, mx in reversed(self.phases):
            if mx < 1:
                continue
            base = ph << 64
            first, last = self.rounds([base + 1, base + mx])
            if not first or first["updated"] > t:
                continue
            if last and last["updated"] <= t:
                return last
            lo, hi = 1, mx
            while hi - lo > 1:
                before = (lo, hi)
                pts = sorted({lo + (hi - lo) * (i + 1) // 10 for i in range(9)} - {lo, hi})
                for p, r in zip(pts, self.rounds([base + p for p in pts])):
                    if r is None:
                        continue
                    if r["updated"] <= t:
                        lo = max(lo, p)
                    else:
                        hi = min(hi, p)
                        break
                if (lo, hi) == before:  # every probe was empty: stop at the last round known to precede t
                    break
            return self.rounds([base + lo])[0]
        return None


def dates(cfg: dict) -> list[date]:
    out, d = [], date(2023, 10, 15)
    while d <= date(2026, 9, 15):
        out.append(d)
        d = (d.replace(day=1) + timedelta(days=32)).replace(day=15)
    out += [date.fromisoformat(cfg["holdout"]["score_end"][:10]), date.fromisoformat(cfg["period"]["observation_end"][:10])]
    return sorted(set(out))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tokens", type=int, default=5, help="the N largest selected USD-quoted tokens by rows")
    ap.add_argument("--rpc", help="RPC URL (default: accounts.rpc_url of the configuration)")
    args = ap.parse_args()
    cfg = load_config()
    url = args.rpc or cfg["accounts"]["rpc_url"]
    lst = pd.read_csv(USD_INPUTS / "listed_tokens.csv")
    lst = lst[(lst["selected"].astype(str).str.lower() == "true") & (lst["quote"] == "USD")]
    lst = lst.sort_values("n_rows_tobs", ascending=False).drop_duplicates("feed_proxy").head(args.tokens)
    prices = pd.read_csv(USD_INPUTS / "daily_prices_usd.csv").set_index(["address", "day"])
    session = requests.Session()
    rows = []
    for _, r in lst.iterrows():
        px = Proxy(session, url, r["feed_proxy"].lower())
        px.setup()
        for d in dates(cfg):
            t = int(datetime(d.year, d.month, d.day, tzinfo=timezone.utc).timestamp()) + 86400
            rd = px.at(t)
            key = (r["address"], d.isoformat())
            llama = prices.loc[key] if key in prices.index else None
            cl = rd["answer"] / 10 ** px.decimals if rd else None
            rows.append({"symbol": r["symbol"], "address": r["address"], "feed": r["feed"], "proxy": px.to,
                         "day": d.isoformat(), "chainlink_time": t,
                         "chainlink_updated": rd["updated"] if rd else None, "chainlink_price": cl,
                         "llama_price": float(llama["price_usd"]) if llama is not None else None,
                         "llama_key": llama["key"] if llama is not None else None,
                         "rel_diff": (float(llama["price_usd"]) / cl - 1.0) if (llama is not None and cl) else None})
        last = rows[-1]
        print(r["symbol"], px.phases, last["day"], last["chainlink_price"], last["llama_price"], flush=True)
    out = pd.DataFrame(rows)
    out.to_csv(USD_INPUTS / "chainlink_check.csv", index=False)
    a = out.dropna(subset=["rel_diff"]).assign(abs_diff=lambda x: x["rel_diff"].abs())
    per = a.groupby("symbol")["abs_diff"].agg(["count", "median", "max"])
    save_json({
        "written_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "rpc": url,
        "method": "DefiLlama close of day D against the Chainlink answer in force at 00:00 UTC of D+1",
        "pairs": int(len(a)), "median_abs_rel_diff": float(a["abs_diff"].median()),
        "max_abs_rel_diff": float(a["abs_diff"].max()),
        "share_within_1pct": float((a["abs_diff"] <= 0.01).mean()),
        "per_token": {s: {"n": int(v["count"]), "median": float(v["median"]), "max": float(v["max"])}
                      for s, v in per.iterrows()},
        "missing": int(out["rel_diff"].isna().sum()),
    }, USD_INPUTS / "chainlink_check.json")
    print(per)
    return 0


if __name__ == "__main__":
    sys.exit(main())
