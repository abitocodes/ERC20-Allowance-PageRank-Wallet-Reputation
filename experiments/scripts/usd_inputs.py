#!/usr/bin/env python3
"""Token list and daily USD prices of the revised analysis (docs/revision_price_weighting.md, sections 3 and 4).

Reads data/0-usd-token-list-and-prices/sources/token_candidates.csv, the reviewed table of every token that
Chainlink's Arbitrum One directory (snapshot in the same folder) maps to an Arbitrum One address, with the
feed's category and product type and the token's relation to the feed's base asset. The rule is applied
mechanically:

  listed = category in {low, medium} and product RefPrice and not hidden and no shutdown date
           and quote in {USD, ETH} and relation in {token_itself, issuer_wrapper, canonical_bridge}
           and the token occurs in the observation-window data and its identity was not refuted

Then:
  1. symbol(), name() and decimals() of the listed tokens at one block (eth_call);
  2. DefiLlama daily charts of each listed token, Arbitrum key and second key, 2023-10-01 to 2026-10-01;
  3. day alignment: the point nearest 00:00 UTC of day D+1 is the price (close) of day D;
  4. the second key fills days without an Arbitrum point when the two keys' median absolute relative
     difference on shared days is below 1%;
  5. a point more than twice (or less than half) both neighbouring days, which lie within a factor of two of
     each other, is a data error: replaced by the previous day's price and flagged;
  6. remaining gaps take the previous day's price (filled); nothing is carried backwards;
  7. of the listed tokens with a price, the TOP_N with the most rows (transfers plus latest allowances at
     T_obs) are selected; only they enter the revised SQL (column `selected`).

Writes listed_tokens.csv, token_candidates.csv (with the listing decision), daily_prices_usd.csv,
daily_points_raw.csv and usd_inputs.json to data/0-usd-token-list-and-prices/. DefiLlama responses are
cached under data/_work/usd/llama_cache/ so that a rerun reads the same points.

Usage: python scripts/usd_inputs.py [--rpc URL] [--refresh]
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import DATA, USD_INPUTS, load_config, save_json  # noqa: E402
from token_metadata import read_metadata  # noqa: E402
from usd import fill_daily  # noqa: E402

SOURCES = USD_INPUTS / "sources"
CACHE = DATA / "_work" / "usd" / "llama_cache"
LLAMA = "https://coins.llama.fi"
FIRST_DAY, LAST_DAY = "2023-10-01", "2026-09-30"
MAX_POINTS = 500                     # DefiLlama /chart: span x coins <= 500 per request
SECOND_KEY_MAD = 0.01
SPIKE = 2.0
LISTED_CATEGORIES = ("low", "medium")
LISTED_RELATIONS = ("token_itself", "issuer_wrapper", "canonical_bridge")
# Of the listed tokens that have a price, the analysis keeps the TOP_N with the most rows in the
# observation-window data (decision of 10 October 2026, docs/revision_price_weighting.md section 3).
TOP_N = 5


def listing(c: pd.DataFrame) -> pd.DataFrame:
    """The listing decision and, for every token left out, the first condition it fails."""
    c = c.copy()
    reasons = []
    for _, r in c.iterrows():
        if r["feed_category"] not in LISTED_CATEGORIES:
            reasons.append(f"feed category {r['feed_category']}")
        elif r["feed_product"] != "RefPrice":
            reasons.append(f"feed product {r['feed_product'] or 'none'} (not a market-price feed)")
        elif bool(r["feed_hidden"]):
            reasons.append("hidden feed")
        elif isinstance(r["feed_shutdown_date"], str) and r["feed_shutdown_date"]:
            reasons.append(f"feed shuts down {r['feed_shutdown_date']}")
        elif r["quote"] not in ("USD", "ETH"):
            reasons.append(f"feed quoted in {r['quote']}")
        elif r["relation"] not in LISTED_RELATIONS:
            reasons.append(f"relation {r['relation']}")
        elif not r["n_rows_tobs"] > 0:
            reasons.append("not in the observation-window data")
        elif r.get("verification") == "wrong":
            reasons.append("identity refuted")
        else:
            reasons.append("")
    c["listed"] = [not x for x in reasons]
    c["reason_not_listed"] = reasons
    return c


def chart(key: str, refresh: bool) -> list[dict]:
    """Daily chart points of one DefiLlama key from 2023-10-01 00:00 to 2026-10-01 00:00 UTC (cached)."""
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / (key.replace(":", "_").replace("/", "_") + ".json")
    if path.exists() and not refresh:
        return json.loads(path.read_text(encoding="utf-8"))["points"]
    start = int(datetime(2023, 10, 1, tzinfo=timezone.utc).timestamp())
    end = int(datetime(2026, 10, 1, tzinfo=timezone.utc).timestamp())
    points, t = [], start
    while t <= end:
        span = min(MAX_POINTS, (end - t) // 86400 + 1)
        url = f"{LLAMA}/chart/{key}?start={t}&span={span}&period=1d"
        for attempt in range(8):
            try:
                resp = requests.get(url, timeout=60)
                if resp.status_code == 200:
                    coin = resp.json().get("coins", {}).get(key) or {}
                    for p in coin.get("prices", []):
                        points.append({"timestamp": int(p["timestamp"]), "price": float(p["price"]),
                                       "confidence": coin.get("confidence"), "symbol": coin.get("symbol")})
                    break
            except (requests.RequestException, ValueError):
                pass
            time.sleep(min(2 ** attempt, 30))
        else:
            raise RuntimeError(f"DefiLlama kept failing for {url}")
        t += span * 86400
        time.sleep(0.3)
    path.write_text(json.dumps({"key": key, "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                                "points": points}), encoding="utf-8")
    return points


def to_days(points: list[dict]) -> pd.DataFrame:
    """One price per day D: the point nearest 00:00 UTC of D+1 (DefiLlama's close of D)."""
    if not points:
        return pd.DataFrame(columns=["day", "price", "confidence", "timestamp"])
    p = pd.DataFrame(points)
    ts = pd.to_datetime(p["timestamp"], unit="s", utc=True)
    midnight = ts.dt.round("D")
    p["offset"] = (ts - midnight).dt.total_seconds().abs()
    p["day"] = (midnight - pd.Timedelta(days=1)).dt.tz_localize(None)
    p = p[p["price"] > 0].sort_values(["day", "offset"]).drop_duplicates("day")
    p = p[(p["day"] >= FIRST_DAY) & (p["day"] <= LAST_DAY)]
    return p[["day", "price", "confidence", "timestamp"]].reset_index(drop=True)


def combine(arb: pd.DataFrame, second: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """The Arbitrum key's days, then the second key's days where the Arbitrum key has none (if the keys agree)."""
    a, s = arb.set_index("day"), second.set_index("day")
    shared = a.index.intersection(s.index)
    mad = float(np.median(np.abs(a.loc[shared, "price"] / s.loc[shared, "price"] - 1.0))) if len(shared) else None
    use = mad is not None and mad < SECOND_KEY_MAD
    out = a.assign(key="arbitrum")
    if use:
        extra = s.loc[s.index.difference(a.index)].assign(key="second")
        out = pd.concat([out, extra])
    out = out.sort_index()
    return out.reset_index(), {"shared_days": int(len(shared)), "median_abs_rel_diff": mad, "second_key_used": use,
                               "second_key_days": int((out["key"] == "second").sum())}


def spikes(df: pd.DataFrame) -> pd.DataFrame:
    """Flag a one-day error (rule 5) and replace its price by the previous day's price."""
    df = df.sort_values("day").reset_index(drop=True)
    p = df["price"].to_numpy()
    d = df["day"].to_numpy()
    flag = np.zeros(len(df), dtype=bool)
    one = np.timedelta64(1, "D")
    for i in range(1, len(df) - 1):
        if d[i] - d[i - 1] != one or d[i + 1] - d[i] != one:
            continue
        up = p[i] > SPIKE * p[i - 1] and p[i] > SPIKE * p[i + 1]
        down = p[i] < p[i - 1] / SPIKE and p[i] < p[i + 1] / SPIKE
        calm = 1.0 / SPIKE <= p[i - 1] / p[i + 1] <= SPIKE
        if (up or down) and calm:
            flag[i] = True
    prices = p.copy()
    prices[flag] = p[np.flatnonzero(flag) - 1]
    return df.assign(price=prices, spike=flag)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rpc", help="RPC URL (default: accounts.rpc_url of the configuration)")
    ap.add_argument("--refresh", action="store_true", help="fetch DefiLlama again instead of using the cache")
    args = ap.parse_args()
    cfg = load_config()

    cand = listing(pd.read_csv(SOURCES / "token_candidates.csv", keep_default_na=False,
                               dtype={"feed_shutdown_date": str}))
    lst = cand[cand["listed"]].copy()
    print(f"{len(lst)} of {len(cand)} candidates listed", flush=True)

    meta_df, rpc_meta = read_metadata(lst["address"].tolist(), args.rpc or cfg["accounts"]["rpc_url"])
    meta_df = meta_df.set_index("address")
    bad = [a for a in lst["address"] if meta_df.loc[a, "decimals"] != int(lst.set_index("address").loc[a, "decimals"])]
    if bad:
        raise SystemExit(f"decimals read on chain differ from the candidate table for {bad}")

    raw_rows, price_frames, summary = [], [], []
    for _, r in lst.iterrows():
        a = r["address"]
        arb_key = f"arbitrum:{a}"
        arb_pts = chart(arb_key, args.refresh)
        sec_key = r["second_key"] or ""
        sec_pts = chart(sec_key, args.refresh) if sec_key else []
        for key, pts in ((arb_key, arb_pts), (sec_key, sec_pts)):
            for p in pts:
                raw_rows.append({"address": a, "key": key, **{k: p[k] for k in ("timestamp", "price", "confidence")}})
        arb, sec = to_days(arb_pts), to_days(sec_pts)
        comb, info = combine(arb, sec)
        comb = spikes(comb) if len(comb) else comb.assign(spike=False)
        filled = fill_daily(comb.rename(columns={"price": "price_usd"}).assign(token=a)[
            ["token", "day", "price_usd", "confidence"]], FIRST_DAY, LAST_DAY)
        filled = filled.merge(comb[["day", "key", "spike"]], on="day", how="left")
        filled["key"] = filled["key"].fillna("filled")
        filled["spike"] = filled["spike"].fillna(False).astype(bool)
        if len(filled):
            price_frames.append(filled.rename(columns={"token": "address"}))
        summary.append({
            "address": a, "arbitrum_key_days": int(len(arb)),
            "arbitrum_key_first_day": arb["day"].min().date().isoformat() if len(arb) else "",
            "second_key": sec_key, "second_key_days_available": int(len(sec)),
            "second_key_shared_days": info["shared_days"],
            "second_key_median_abs_rel_diff": info["median_abs_rel_diff"],
            "second_key_used": info["second_key_used"], "second_key_days_used": info["second_key_days"],
            "spike_days": int(comb["spike"].sum()) if len(comb) else 0,
            "first_price_day": filled["day"].min().date().isoformat() if len(filled) else "",
            "priced": bool(len(filled)), "priced_days": int(len(filled)), "filled_days": int(filled["filled"].sum()),
            "min_confidence": float(pd.to_numeric(filled["confidence"], errors="coerce").min()) if len(filled) else None,
        })
        print(f"{r['symbol']:>8} arbitrum {len(arb):4d} days, second {info['second_key_days']:4d} used "
              f"(MAD {info['median_abs_rel_diff']}), spikes {summary[-1]['spike_days']}, "
              f"filled {summary[-1]['filled_days']}, first {summary[-1]['first_price_day']}", flush=True)

    prices = pd.concat(price_frames, ignore_index=True)
    prices["day"] = pd.to_datetime(prices["day"]).dt.date.astype(str)
    prices["filled_from"] = pd.to_datetime(prices["filled_from"]).dt.date.astype(str)
    prices.loc[~prices["filled"], "filled_from"] = ""
    prices = prices[["address", "day", "price_usd", "confidence", "filled", "filled_from", "key", "spike"]]

    s = pd.DataFrame(summary).set_index("address")
    out = lst.set_index("address")[["symbol", "name", "decimals", "feed", "feed_path", "feed_proxy", "quote",
                                    "feed_category", "relation", "relation_note", "n_rows_tobs", "rank_by_n",
                                    "verification"]].join(s)
    out["symbol"] = meta_df["symbol"].reindex(out.index).fillna(out["symbol"])
    out["name"] = meta_df["name"].reindex(out.index).fillna(out["name"])
    out = out.reset_index()[["address", "symbol", "name", "decimals", *[c for c in out.columns if c not in
                                                                        ("address", "symbol", "name", "decimals")]]]
    out = out.sort_values("n_rows_tobs", ascending=False)
    rank = out["n_rows_tobs"].where(out["priced"]).rank(ascending=False, method="first")
    out["selected"] = rank <= TOP_N

    USD_INPUTS.mkdir(parents=True, exist_ok=True)
    out.to_csv(USD_INPUTS / "listed_tokens.csv", index=False)
    cand.to_csv(USD_INPUTS / "token_candidates.csv", index=False)
    prices.to_csv(USD_INPUTS / "daily_prices_usd.csv", index=False)
    pd.DataFrame(raw_rows).to_csv(USD_INPUTS / "daily_points_raw.csv", index=False)
    anchors = (cfg["holdout"]["score_end"][:10], cfg["period"]["observation_end"][:10])
    have = set(zip(prices["address"], prices["day"]))
    no_anchor = [(a, d) for a in out.loc[out["priced"], "address"] for d in anchors if (a, d) not in have]
    total_rows = 1_566_473_485  # transfers + latest allowances at T_obs over all 131,609 tokens (top_tokens)
    save_json({
        "written_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "rule": "docs/revision_price_weighting.md, sections 3 and 4",
        "candidates": int(len(cand)), "listed": int(len(lst)),
        "listed_rows_tobs": int(out["n_rows_tobs"].sum()),
        "listed_share_of_rows_tobs": float(out["n_rows_tobs"].sum() / total_rows),
        # A listed token without any DefiLlama point has no price on any day: every one of its events would be
        # unpriced, so it is left out of contract_rep.u_tokens altogether and reported here.
        "listed_without_price": out.loc[~out["priced"], ["address", "symbol", "n_rows_tobs"]].to_dict(orient="records"),
        "priced_tokens": int(out["priced"].sum()),
        "priced_rows_tobs": int(out.loc[out["priced"], "n_rows_tobs"].sum()),
        "priced_share_of_rows_tobs": float(out.loc[out["priced"], "n_rows_tobs"].sum() / total_rows),
        "top_n": TOP_N,
        "selected": out.loc[out["selected"], ["address", "symbol", "n_rows_tobs"]].to_dict(orient="records"),
        "selected_rows_tobs": int(out.loc[out["selected"], "n_rows_tobs"].sum()),
        "selected_share_of_rows_tobs": float(out.loc[out["selected"], "n_rows_tobs"].sum() / total_rows),
        "not_listed_by_reason": cand.loc[~cand["listed"], "reason_not_listed"].str.split(" ").str[:2].str.join(" ")
                                    .value_counts().to_dict(),
        "priced_tokens_without_anchor_price": no_anchor,
        "metadata": rpc_meta,
        "prices": {"source": f"{LLAMA}/chart, period=1d", "days": [FIRST_DAY, LAST_DAY],
                   "second_key_threshold": SECOND_KEY_MAD, "spike_factor": SPIKE,
                   "price_rows": int(len(prices)), "filled_days": int(prices["filled"].sum()),
                   "spike_days": int(prices["spike"].sum()),
                   "second_key_days": int((prices["key"] == "second").sum())},
    }, USD_INPUTS / "usd_inputs.json")
    print(json.dumps(json.loads((USD_INPUTS / "usd_inputs.json").read_text(encoding="utf-8")), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
