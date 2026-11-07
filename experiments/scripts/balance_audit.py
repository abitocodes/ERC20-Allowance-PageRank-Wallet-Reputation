#!/usr/bin/env python3
"""Balance check of the contract-graph revision (docs/revision_contract_graph.md, section 6).

Reads the sample of sql/43_c12_bal_audit.sql (graph-tables-contract-12m/bal_audit: for each of the five tokens,
150 (token, owner) pairs with a zero and 150 with a positive reconstructed balance at T_obs) and the anchor
blocks of sql/34_c12_anchor_blocks.sql (graph-tables-contract-12m/anchor_blocks), and compares the reconstructed
balances with balanceOf on an Arbitrum RPC. An endpoint serves the T_obs anchor block if it answers balanceOf of
the first pair of the sample at that block with a result; a failed request, a rate limit or an error answer is
retried three times, and an endpoint that answers without a result, or fails every attempt, does not serve it
(revision sections 4.2 rule 2 and 6). The check runs in one of two modes:

  archive  (an endpoint serves the block) balanceOf at the T_obs block against bal_tobs, over every pair of
           the sample, on the endpoints that serve it; the match must reach balance.min_match (98%);
  latest   balanceOf at the latest block (read once and then pinned) against bal_0930, the balance carried to
           30 September 2026, judged on the owners with no transfer from 1 July to 30 September (n_w1 = 0); the
           match must reach balance.min_match_dormant (99%), as in the exploratory check of 13 October 2026.

A pair matches when the reconstructed balance, a negative value clipped to 0, is within 1e-9 of the on-chain
balance relative to it, or within balance.dust_token (1e-6) token. Endpoints: a provider URL with a key only
from the environment variable CONTRACT_REP_RPC_URL (tried first and never written anywhere), then the public
contract_graph.rpc_urls of the configuration in order. The outputs name host names only.

Writes data/2-processed-tables-and-evaluations/revised-contract-12m/typing/balance_audit.json and
balance_audit.csv (one row per pair). Exits 1 below the threshold, and 2 without a check when no endpoint
serves the T_obs block and none gives the latest block either.

Usage: python scripts/balance_audit.py [--sample STEM] [--anchors STEM] [--batch 25]
"""

from __future__ import annotations

import argparse
import math
import os
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

import pandas as pd

os.environ.setdefault("CONTRACT_REP_VARIANT", "contract12m")
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import GRAPH, PROC, ROOT, VARIANT, load_config, read_parts, save_json  # noqa: E402

BALANCE_OF = "0x70a08231"  # balanceOf(address)
REL_TOL = 1e-9
PROBE_RETRIES = 3   # retries of the block probe after a failed request, a rate limit or an error answer (rule 2)
OUT = PROC / "typing"


class NoAnswer(RuntimeError):
    """An endpoint did not answer (transport errors or HTTP failures after the retries)."""


def host(url: str) -> str:
    """The host (and port) of an endpoint, without credentials, path or query string."""
    return urlsplit(url).netloc.rsplit("@", 1)[-1]


def endpoints(cfg: dict) -> list[str]:
    key = os.environ.get("CONTRACT_REP_RPC_URL", "").strip()
    return ([key] if key else []) + [str(u) for u in cfg["contract_graph"]["rpc_urls"]]


def matches(reconstructed: float, onchain: float | None, decimals: int, dust_token: float,
            rel: float = REL_TOL) -> bool:
    """Whether a reconstructed balance (base units, clipped at 0) agrees with the on-chain one: within ``rel``
    of it, or within ``dust_token`` tokens. A missing on-chain value never matches."""
    if onchain is None or (isinstance(onchain, float) and math.isnan(onchain)):
        return False
    diff = abs(max(float(reconstructed), 0.0) - float(onchain))
    return diff <= rel * abs(float(onchain)) or diff <= float(dust_token) * 10.0 ** int(decimals)


def judge(df: pd.DataFrame, mode: str, balance_cfg: dict) -> dict:
    """Mark each row (columns bal_tobs, bal_0930, n_w1, decimals, onchain) and decide the check of ``mode``
    ('archive' or 'latest'). Adds the columns reference, reconstructed, match and judged to ``df``."""
    ref = "bal_tobs" if mode == "archive" else "bal_0930"
    dust = float(balance_cfg["dust_token"])
    df["reference"] = ref
    df["reconstructed"] = df[ref].astype(float).clip(lower=0.0)
    df["match"] = [matches(r, o, d, dust) for r, o, d in zip(df[ref], df["onchain"], df["decimals"])]
    df["judged"] = True if mode == "archive" else df["n_w1"].astype(int) == 0
    judged = df[df["judged"]]
    threshold = float(balance_cfg["min_match"] if mode == "archive" else balance_cfg["min_match_dormant"])
    share = float(judged["match"].mean()) if len(judged) else 0.0
    return {"mode": mode, "reference": ref, "rows": int(len(df)), "judged": int(len(judged)),
            "matched": int(judged["match"].sum()), "share": round(share, 6), "threshold": threshold,
            "passed": bool(len(judged) > 0 and share >= threshold),
            "overall_share": round(float(df["match"].mean()), 6) if len(df) else 0.0}


class Rpc:
    """JSON-RPC over a list of endpoints in order; counts the calls per host."""

    def __init__(self, urls: list[str], retries: int = 6):
        import requests
        self.requests = requests
        self.session = requests.Session()
        self.urls, self.retries = list(urls), retries
        self.calls: Counter = Counter()

    def send(self, url: str, payload) -> tuple[object, str]:
        """One request to one endpoint: the decoded answer and '', or None and why (never the URL)."""
        self.calls[host(url)] += len(payload) if isinstance(payload, list) else 1
        try:
            resp = self.session.post(url, json=payload, timeout=60)
            if resp.status_code == 200:
                return resp.json(), ""
            return None, f"HTTP {resp.status_code}"
        except (self.requests.RequestException, ValueError) as exc:
            return None, type(exc).__name__

    def post(self, url: str, payload):
        """The decoded answer of one endpoint, retrying transport errors; messages never show the URL."""
        last = ""
        for attempt in range(self.retries):
            body, last = self.send(url, payload)
            if body is not None:
                return body
            time.sleep(min(2 ** attempt, 30))
        raise NoAnswer(f"{host(url)}: {last}")

    def batch(self, payload: list[dict], tries: int = 4) -> dict[int, str | None]:
        """The result of every call of a batch by id. Calls that fail (an error or an empty result) are sent
        again, then to the next endpoint; a call that fails everywhere gives None."""
        ids = [c["id"] for c in payload]
        good: dict[int, str] = {}
        for url in self.urls:
            for attempt in range(tries):
                todo = [c for c in payload if c["id"] not in good]
                if not todo:
                    break
                try:
                    body = self.post(url, todo)
                except NoAnswer:
                    break
                for x in body if isinstance(body, list) else [body]:
                    if isinstance(x, dict) and x.get("id") in ids and x.get("result") not in (None, "0x"):
                        good[x["id"]] = x["result"]
                if len(good) < len(ids):
                    time.sleep(1 + attempt)
            if len(good) == len(ids):
                break
        return {i: good.get(i) for i in ids}


def balance_call(i: int, token: str, owner: str, block: str) -> dict:
    data = BALANCE_OF + owner.lower().removeprefix("0x").rjust(64, "0")
    return {"jsonrpc": "2.0", "id": i, "method": "eth_call", "params": [{"to": token, "data": data}, block]}


def archive_endpoints(rpc: Rpc, row: dict, block_hex: str) -> tuple[list[str], dict[str, str], dict[str, int]]:
    """The endpoints that serve the T_obs block (revision sections 4.2 rule 2 and 6), the outcome per host and the
    attempts per host. An endpoint serves it if it answers balanceOf of the first pair at that block with a result.
    A failed request, a rate limit or an error answer is retried PROBE_RETRIES times; an answer without a result
    ('0x') means no at once, and so does an endpoint whose every attempt fails. The outcome is 'served',
    'no result', the last error answer or failure, or 'no answer' when no attempt was answered."""
    ok, outcome, attempts = [], {}, {}
    call = [balance_call(0, row["token"], row["owner"], block_hex)]
    for url in rpc.urls:
        last, answered = "no answer", False
        for attempt in range(1 + PROBE_RETRIES):
            attempts[host(url)] = attempt + 1
            body, err = rpc.send(url, call)
            if body is not None:
                answered = True
                item = body[0] if isinstance(body, list) and body else body
                result = item.get("result") if isinstance(item, dict) and "error" not in item else None
                if isinstance(result, str) and result.lower() not in ("", "0x"):
                    ok.append(url)
                    last = "served"
                    break
                if isinstance(result, str):
                    last = "no result"
                    break
                error = item.get("error") if isinstance(item, dict) else None
                message = error.get("message", error) if isinstance(error, dict) else (error or str(item)[:120])
                last = "error: " + str(message)[:120]
            elif answered:
                last = "failed: " + err
            if attempt < PROBE_RETRIES:
                time.sleep(min(2 ** attempt, 30))
        outcome[host(url)] = last
    return ok, outcome, attempts


def latest_block(rpc: Rpc) -> int:
    for url in rpc.urls:
        try:
            body = rpc.post(url, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []})
        except NoAnswer:
            continue
        if isinstance(body, dict) and body.get("result"):
            return int(body["result"], 16)
    raise NoAnswer("no endpoint gave the latest block")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sample", default=str(GRAPH / "bal_audit"), help="parquet parts of c12_bal_audit")
    ap.add_argument("--anchors", default=str(GRAPH / "anchor_blocks"), help="parquet parts of c12_anchor_blocks")
    ap.add_argument("--batch", type=int, default=25)
    args = ap.parse_args()
    if VARIANT != "contract12m":
        raise SystemExit("balance_audit.py belongs to the contract-graph variant (CONTRACT_REP_VARIANT=contract12m)")
    cfg = load_config()
    bal = cfg["contract_graph"]["balance"]
    df = read_parts(Path(args.sample)).sort_values(["token", "cell", "owner"]).reset_index(drop=True)
    anchors = {r["anchor"]: int(r["block_number"]) for r in read_parts(Path(args.anchors)).to_dict("records")}
    rpc = Rpc(endpoints(cfg))
    first = df.iloc[0].to_dict()
    ok, probe, probe_attempts = archive_endpoints(rpc, first, hex(anchors["tobs"]))
    # No endpoint serves the T_obs block, including an endpoint whose every attempt failed (rule 2): the latest
    # block. If no endpoint gives that either, nothing can be checked (exit 2).
    if ok:
        mode, block = "archive", anchors["tobs"]
        rpc.urls = ok
    else:
        try:
            mode, block = "latest", latest_block(rpc)
        except NoAnswer as exc:
            print(exc)
            return 2
    print(f"mode {mode} at block {block:,} ({', '.join(host(u) for u in rpc.urls)})", flush=True)
    rows = df.to_dict("records")
    raw: list[str | None] = []
    for i in range(0, len(rows), args.batch):
        chunk = rows[i:i + args.batch]
        got = rpc.batch([balance_call(j, r["token"], r["owner"], hex(block)) for j, r in enumerate(chunk)])
        raw += [got.get(j) for j in range(len(chunk))]
        time.sleep(0.2)
    df["onchain_hex"] = raw
    df["onchain"] = [float(int(x, 16)) if x else float("nan") for x in raw]
    verdict = judge(df, mode, bal)
    cells = (df.groupby(["token", "cell"])
               .agg(n=("match", "size"), match=("match", "mean"), judged=("judged", "sum"))
               .reset_index())
    sample = Path(args.sample).resolve()
    out = {
        "computed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sample": sample.relative_to(ROOT).as_posix() if sample.is_relative_to(ROOT) else sample.name,
        "anchor_blocks": anchors,
        "archive_probe": probe,
        "archive_probe_attempts": probe_attempts,
        "block": block,
        "hosts": [host(u) for u in rpc.urls],
        "calls_per_host": dict(rpc.calls),
        "errors": int(df["onchain"].isna().sum()),
        "rule": "balance at T_obs against balanceOf at the T_obs block if the RPC serves it (min_match), otherwise "
                "the balance carried to 2026-09-30 against balanceOf at the latest block, judged on the owners with "
                "no transfer from 1 July to 30 September (min_match_dormant); a match is within 1e-9 relative or "
                "1e-6 token, a negative reconstructed balance clipped to 0 (docs/revision_contract_graph.md "
                "section 6)",
        **verdict,
        "per_cell": [{"token": r["token"], "cell": r["cell"], "n": int(r["n"]), "match": round(float(r["match"]), 4),
                      "judged": int(r["judged"])} for r in cells.to_dict("records")],
    }
    OUT.mkdir(parents=True, exist_ok=True)
    save_json(out, OUT / "balance_audit.json")
    df.to_csv(OUT / "balance_audit.csv", index=False)
    print(f"{verdict['matched']:,} of {verdict['judged']:,} judged pairs match ({verdict['share']:.2%}; threshold "
          f"{verdict['threshold']:.0%}); all pairs {verdict['overall_share']:.2%}; "
          f"{'passed' if verdict['passed'] else 'NOT passed'}")
    return 0 if verdict["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
