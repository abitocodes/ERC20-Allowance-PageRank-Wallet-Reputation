#!/usr/bin/env python3
"""Build the data files of the thesis slide deck (dissertation/presentation/data/*.js).

Every number the slides show is read here from the experiment outputs of phd_works and written
into classic scripts that assign into ``window.DECK_DATA``, so the deck works when index.html is
opened by double-click (file://) as well as over http, without fetch() or ES modules.

Usage
-----
    python3 build_data.py [PHD_WORKS] [--out DIR] [--no-verify]

``PHD_WORKS`` is the root of the phd_works repository (the folder that holds
``1-Dissertation-Works/``). It is taken, in this order, from the positional argument, from the
environment variable ``PHD_WORKS``, or from the location of this script
(``<PHD_WORKS>/1-Dissertation-Works/ERC20-Allowance-PageRank-Wallet-Reputation/dissertation/
presentation/tools/build_data.py``). ``--out`` defaults to ``../data`` next to this script.

Sources (all under ``<PHD_WORKS>/1-Dissertation-Works/ERC20-Allowance-PageRank-Wallet-Reputation/``)
-------------------------------------------------------------------------------------------------
- ``experiments/data/3-published-results-for-thesis/revised-usd-12m/``: summaries of the revised
  analysis (the thesis's main analysis: USD amounts, five tokens, scores from the twelve months
  before each freeze) and its ``results_digest.md``;
- ``experiments/data/3-published-results-for-thesis/``: summaries of the registered analysis and
  its ``results_digest.md``;
- ``experiments/data/2-processed-tables-and-evaluations/revised-usd-12m/``: per-contract scores
  (``same-window/cohort_scores.part*.parquet``, ``holdout-w0`` and ``window-w1``
  ``spender_scores``/``trader_scores``) and the registered cohort scores;
- ``experiments/data/0-usd-token-list-and-prices/``: listed tokens, daily USD closes; ``usd-12m/``:
  the constants and the token rows of the twelve-month score windows;
- ``experiments/data/bq_ledger.json`` and ``experiments/config/contract_reputation.yaml``;
- ``git -C <PHD_WORKS> show`` for the commit times of 43d8045 and 0d3a057. The deck does not date the
  definitions of the revised analysis (the thesis says only that they followed the registered results).

Nothing is fitted or re-estimated. A few quantities are *derived* from the per-contract parquet
files (percentile ranks, decile bins of the holdout labels, the Sybil cost curve through the
closed form of ``experiments/scripts/sybil_model.py``, an eight-contract Kendall illustration);
each of them carries ``derived: true`` and a note in its ``meta``.

Rounding: floats keep 4 significant digits, but never fewer than needed to reproduce the 2-, 3- and
4-decimal displays of the unrounded value (so a slide that prints 3 decimals shows what the digest
shows). Percentile ranks keep 4 decimals. After writing, the script reads the written files back,
compares a set of values with the two results digests and with Kendall coefficients recomputed from
the parquet files, prints the comparison, and exits with status 1 if any check fails.

Requires Python 3.9+, numpy, pandas, pyarrow, pyyaml; scipy for the verification.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal, localcontext
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_REL = Path("1-Dissertation-Works/ERC20-Allowance-PageRank-Wallet-Reputation")
COMMITS = {
    "43d8045": "Analysis plan and configuration fixed before this study extracted any log",
    "0d3a057": "W1 registration, extraction and evaluation code committed before scan B",
}
COMMITS_KO = {
    "43d8045": "분석 계획과 설정 고정(이 연구의 로그 추출 전)",
    "0d3a057": "W1 등록 문서와 추출·평가 코드 커밋(2차 추출 전)",
}

METHODS = [
    # key, English, Korean (glossary), short, edges walked, restarts
    ("endorserank", "EndorseRank", "엔도스랭크", "ER", "allowance", "uniform"),
    ("endorserank_activity", "EndorseRank (activity restarts)", "엔도스랭크(활동 재시작)", "ER-act",
     "allowance", "activeness of approving owners"),
    ("awp", "AWP", "AWP(적응형 가중 페이지랭크)", "AWP", "transfer", "activeness of senders"),
    ("cpr_l0", "C-PR (λ=0)", "C-PR (λ=0, 송금 층만 걷기)", "λ=0", "transfer layer alone (USD amounts)", "uniform"),
    ("cpr_l25", "C-PR (λ=0.25)", "C-PR (λ=0.25)", "λ=0.25", "both layers", "uniform"),
    ("cpr_l50", "C-PR (λ=0.5)", "C-PR (λ=0.5, 주 설정)", "λ=0.5", "both layers", "uniform"),
    ("cpr_l75", "C-PR (λ=0.75)", "C-PR (λ=0.75)", "λ=0.75", "both layers", "uniform"),
    ("cpr_l100", "C-PR (λ=1)", "C-PR (λ=1, 허락 층만 걷기)", "λ=1", "allowance layer alone (capped USD)", "uniform"),
    ("spr", "S-PR", "S-PR(보증 씨앗 페이지랭크)", "S-PR", "transfer layer", "C-PR (λ=1) scores as seeds"),
    ("in_approve_degree", "In-approve degree", "받은 허락 수(허락 입차수)", "deg-A", "none (raw count)", "none"),
    ("in_degree", "Transfer in-degree", "송금 입차수", "deg-T", "none (raw count)", "none"),
]
SCORE_COLS = ["endorserank", "endorserank_activity", "awp", "cpr_l0", "cpr_l25", "cpr_l50", "cpr_l75",
              "cpr_l100", "spr"]
LAMBDA_KEYS = ["cpr_l0", "cpr_l25", "cpr_l50", "cpr_l75", "cpr_l100"]
LAMBDAS = [0, 0.25, 0.5, 0.75, 1]
PROXIES = [
    ("in_degree", "transfer", "Transfer in-degree", "송금 입차수(보내온 서로 다른 주소 수)"),
    ("in_value", "transfer", "In-value (USD)", "받은 송금액 합(달러)"),
    ("in_approve_degree", "allowance", "In-approve degree", "받은 허락 수(허락한 서로 다른 주인 수)"),
    ("in_approve_value", "allowance", "In-approve value (USD, capped at U)", "받은 허락 금액 합(달러, 상한 U)"),
    ("inbound_counterparty_ratio", "sybil_stability", "Inbound counterparty ratio", "들어온 상대 비율"),
    ("transfer_tenure_days", "sybil_stability", "Transfer tenure (days)", "송금 활동 기간(일)"),
    ("active_months", "sybil_stability", "Active months", "활동한 달 수"),
]
FAMILIES = {
    "transfer": ("Transfer family", "송금 지표 가족"),
    "allowance": ("Allowance family", "허락 지표 가족"),
    "sybil_stability": ("Sybil-stability family", "시빌 안정성 지표 가족"),
}
SPENDER_LABELS = {
    "future_new_approvers": ("New approval pairs", "새 허락 쌍"),
    "future_new_transfer_senders": ("New transfer senders", "새 송금자"),
    "future_revoke_count": ("Revocations", "허락 취소"),
    "future_drain_owners": ("Drained owners (heuristic)", "토큰이 빠져나간 주인(추정)"),
}
TRADER_LABELS = {
    "liquidation_free_rate": ("Liquidation-free close rate", "청산 없이 닫은 비율"),
    "no_liquidation": ("No liquidation", "청산 없음"),
    "profitable_closes": ("Profitable closes", "이익 낸 닫기 수"),
    "realized_gain": ("Realized gain (USD)", "실현 이익(달러)"),
    "profitable_share": ("Profitable share of closes", "이익 낸 닫기 비율"),
    "non_loss_share": ("Non-loss share of closes", "손실 없는 닫기 비율"),
}
NEUTRAL_PAIRS = {
    "P": ("in_approve_degree", "in_degree", "decision contrast P (count level)"),
    "Q": ("endorserank_activity", "awp", "decision contrast Q (PageRank level)"),
    "layers": ("cpr_l100", "cpr_l0", "amount-weighted layers"),
    "er_awp": ("endorserank", "awp", "EndorseRank minus AWP"),
    "cpr0_awp": ("cpr_l0", "awp", "isolates AWP's weights and restarts"),
    "er_degree": ("endorserank", "in_approve_degree", "EndorseRank minus its raw count"),
}
NOTES = {
    "revised": ("Revised analysis = the thesis's main analysis: USD amounts, five tokens (WETH, USDC, "
                "USDT0, ARB, WBTC), scores from the twelve months before each freeze. Decided after the "
                "registered results were known, so none of its results is a registered result; its rule "
                "verdicts are a re-analysis."),
    "revised_ko": ("수정 분석 = 논문의 주 결과예요. 금액은 달러, 토큰은 다섯 개, 점수는 동결마다 그 전 12개월로 "
                   "만들어요. 등록 결과를 본 뒤 정했기 때문에 등록된 결과가 아니에요. 규칙 판정은 재분석이에요."),
    "registered": ("Registered analysis: raw base units, every ERC-20 token, b = 1. Rule A fixed in the "
                   "plan (43d8045) before this study extracted any log; rule B, P/Q and R1-R3 fixed in the W1 "
                   "registration (0d3a057) before scan B."),
    "registered_ko": ("등록 분석: 원래 단위, 모든 ERC-20 토큰, b = 1이에요. 규칙 A는 이 연구의 로그 추출 전 계획(43d8045)에서, "
                      "규칙 B·P/Q·R1–R3는 2차 추출 전 W1 등록(0d3a057)에서 미리 정했어요."),
    "same_window": ("Same-window agreement with the families is an intended-construct check: part of it is "
                    "built in, and it is not validation or evidence of predictive power."),
    "same_window_ko": "같은 기간 일치도는 의도한 구성개념 점검이에요. 일부는 만든 방식 때문에 저절로 생기고, 검증이 아니에요.",
    "post_hoc": "Computed after the labels were known; no rule fixed it in advance (post hoc).",
    "post_hoc_ko": "라벨을 본 뒤 계산했어요(사후). 미리 정한 규칙이 아니에요.",
    "exploratory": "Exploratory run under no rule (W0 traders); intervals are wide (n = 88).",
    "exploratory_ko": "규칙 없이 살펴본 탐색적 결과예요(W0 트레이더, n = 88). 구간이 넓어요.",
    "raw_degree": ("On new approval pairs the raw in-approve degree ranks spenders better than EndorseRank "
                   "(uniform restarts) in both windows (post hoc contrasts)."),
    "raw_degree_ko": "새 허락 쌍에서는 그냥 센 허락 수가 엔도스랭크보다 잘 맞혔어요(두 기간 모두, 사후 대비).",
    "speed": ("Same solver for every score: runtime differences follow from the size of each graph and the "
              "iterations its walk needs there (the time ratio does not follow the edge ratio), not from the "
              "algorithm."),
    "speed_ko": ("모든 점수가 같은 풀이 프로그램을 써요. 시간 차이는 그래프의 크기와 그 그래프에서 걷기가 되풀이해야 하는 "
                 "반복 수에서 와요(시간 비는 화살표 수의 비를 따르지 않아요). 알고리즘의 기여가 아니에요."),
    "contracts_only": ("The study scores and evaluates smart contracts only; EOAs enter the graphs as owners, "
                       "senders and recipients and are never scored."),
    "contracts_only_ko": ("이 연구는 스마트 계약만 점수를 매기고 평가해요. EOA는 화살표의 출발점과 "
                          "도착점으로만 나오고 점수를 받지 않아요."),
}


# ----------------------------------------------------------------------------- helpers

def sig(x, n=4):
    """Round to n significant digits; ints, bools and None pass through."""
    if x is None or isinstance(x, (bool, np.bool_)):
        return None if x is None else bool(x)
    if isinstance(x, (int, np.integer)):
        return int(x)
    x = float(x)
    if not math.isfinite(x):
        return None
    if x == 0:
        return 0.0
    return float(f"{x:.{n}g}")


def js_fixed(y, d):
    """y shown with d decimals the way the deck shows it: Intl.NumberFormat in Chromium rounds the
    shortest decimal string of the double half away from zero (0.2135 -> 0.214), whereas Python's
    f"{y:.3f}" rounds the exact binary value (0.2135 -> 0.213)."""
    with localcontext() as ctx:
        ctx.prec = 400  # room for values up to 2**256 at four decimals
        s = str(Decimal(repr(float(y))).quantize(Decimal(1).scaleb(-d), rounding=ROUND_HALF_UP))
    return "0" + s[2:] if s.startswith("-0") and not any(ch in "123456789" for ch in s) else s


def safe(x, n=4):
    """sig() that keeps the 1- to 4-decimal displays of x as the deck renders them (no double-rounding drift)."""
    if x is None or isinstance(x, (bool, np.bool_, int, np.integer)):
        return sig(x)
    x = float(x)
    if not math.isfinite(x):
        return None
    for k in range(n, 17):
        y = float(f"{x:.{k}g}")
        # both ways the deck prints a number must give the digest's display: Intl.NumberFormat (js_fixed)
        # and Number.toFixed, which rounds the exact binary value as Python's format does
        if all(js_fixed(y, d) == f"{x:.{d}f}" == f"{y:.{d}f}" for d in (1, 2, 3, 4)):
            return y
    return x


def clean(o):
    """Make an object JSON-safe (numpy scalars, NaN, tuples)."""
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, np.ndarray):
        return [clean(v) for v in o.tolist()]
    if isinstance(o, (np.bool_, bool)):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, (np.floating, float)):
        f = float(o)
        return f if math.isfinite(f) else None
    return o


def compact(o):
    """Shrink the eval-summary JSON: tau entries -> [tau, lo, hi(, rho)], contrasts -> {d, ta, tb, p}."""
    if isinstance(o, dict):
        ks = set(o)
        if {"kendall_tau", "ci_low", "ci_high"} <= ks:
            out = [safe(o["kendall_tau"]), safe(o["ci_low"]), safe(o["ci_high"])]
            if "spearman_rho" in o:
                out.append(safe(o["spearman_rho"]))
            return out
        if {"mean_tau", "ci_low", "ci_high"} <= ks:
            return [safe(o["mean_tau"]), safe(o["ci_low"]), safe(o["ci_high"])]
        if {"delta_tau", "ci_low", "ci_high"} <= ks:
            c = {"d": [safe(o["delta_tau"]), safe(o["ci_low"]), safe(o["ci_high"])]}
            for src, dst in (("a_tau", "ta"), ("b_tau", "tb"), ("share_positive", "p")):
                if src in o:
                    c[dst] = safe(o[src])
            if "n_boot" in o:
                c["B"] = int(o["n_boot"])
            if "ci975_low" in o:
                c["d975"] = [safe(o["ci975_low"]), safe(o["ci975_high"])]
            for k in ("label", "group", "a", "b", "outcome", "test", "holds"):
                if k in o:
                    c[k] = o[k]
            return c
        return {k: compact(v) for k, v in o.items()}
    if isinstance(o, list):
        return [compact(v) for v in o]
    if isinstance(o, (float, np.floating)):
        return safe(o)
    return clean(o)


def n_boots(o, acc=None):
    """Collect the distinct n_boot values in a summary (for the meta notes)."""
    acc = set() if acc is None else acc
    if isinstance(o, dict):
        if "n_boot" in o:
            acc.add(int(o["n_boot"]))
        for v in o.values():
            n_boots(v, acc)
    elif isinstance(o, list):
        for v in o:
            n_boots(v, acc)
    return acc


def pct_rank(values) -> np.ndarray:
    """Mid-rank percentile in [0, 1]: (average rank - 1) / (n - 1); tied values share one position."""
    s = pd.Series(np.asarray(values, dtype=float))
    r = s.rank(method="average").to_numpy()
    return (r - 1.0) / (len(s) - 1.0)


def round_list(a, nd=4):
    return [None if (v is None or not math.isfinite(v)) else round(float(v), nd) for v in a]


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_parquet(pattern_dir: Path, stem: str) -> pd.DataFrame:
    parts = sorted(pattern_dir.glob(f"{stem}.part*.parquet"))
    if not parts:
        raise FileNotFoundError(f"no {stem}.part*.parquet in {pattern_dir}")
    return pd.concat([pd.read_parquet(p) for p in parts], ignore_index=True)


def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def method_labels():
    return {k: {"en": en, "ko": ko, "short": sh, "edges": ed, "restarts": rs}
            for k, en, ko, sh, ed, rs in METHODS}


# ----------------------------------------------------------------------------- context

class Ctx:
    def __init__(self, phd: Path, out: Path):
        self.phd = phd
        self.proj = phd / PROJECT_REL
        self.exp = self.proj / "experiments"
        self.data = self.exp / "data"
        self.pub = self.data / "3-published-results-for-thesis"
        self.pub_rev = self.pub / "revised-usd-12m"
        self.proc = self.data / "2-processed-tables-and-evaluations"
        self.proc_rev = self.proc / "revised-usd-12m"
        self.usd = self.data / "0-usd-token-list-and-prices"
        self.usd12 = self.usd / "usd-12m"
        self.out = out
        self.sources: dict[str, Path] = {}
        self.current: set[str] = set()
        for p in (self.pub_rev / "results_digest.md", self.pub / "results_digest.md", self.proc_rev):
            if not p.exists():
                raise SystemExit(f"missing source: {p}")

    def use(self, p: Path) -> Path:
        rel = str(p.relative_to(self.phd).as_posix())
        self.sources[rel] = p
        self.current.add(rel)
        return p

    def j(self, p: Path):
        return load_json(self.use(p))

    def pq(self, d: Path, stem: str) -> pd.DataFrame:
        for part in sorted(d.glob(f"{stem}.part*.parquet")):
            self.use(part)
        return read_parquet(d, stem)

    def rel(self, p: Path) -> str:
        return str(p.relative_to(self.phd).as_posix())


def git_commit(phd: Path, short: str):
    try:
        out = subprocess.run(["git", "-C", str(phd), "show", "-s", "--format=%H%x1f%cI%x1f%s", short],
                             capture_output=True, text=True, check=True, timeout=30).stdout.strip()
    except Exception:  # noqa: BLE001
        return None
    h, ci, subj = out.split("\x1f", 2)
    dt = datetime.fromisoformat(ci)
    return {"sha": h, "short": short, "committed_local": ci,
            "utc": dt.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
            "subject": subj}


def zulu(s: str | None):
    """'2026-10-09T13:41:27+00:00' or '2026-06-30 23:59:59 UTC' -> ISO with Z."""
    if s is None:
        return None
    s = s.strip()
    if s.endswith(" UTC"):
        s = s[:-4].replace(" ", "T") + "+00:00"
    dt = datetime.fromisoformat(s)
    return dt.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


# ----------------------------------------------------------------------------- builders

def build_contracts(c: Ctx):
    df = c.pq(c.proc_rev / "same-window", "cohort_scores").sort_values("id").reset_index(drop=True)
    n = len(df)
    pct = {k: round_list(pct_rank(df[k])) for k in SCORE_COLS + ["in_approve_degree", "in_degree"]}
    raw = {k: [int(v) for v in df[k].round().astype(np.int64)] for k in ("in_approve_degree", "in_degree")}
    log10 = {}
    for k in ("endorserank", "awp"):
        v = df[k].to_numpy(dtype=float)
        log10[k] = [round(math.log10(x), 3) if x > 0 else None for x in v]
    outside_allow = (df["cpr_l100"].to_numpy() == 0)
    outside_transfer = (df["cpr_l0"].to_numpy() == 0)
    flags = (outside_allow.astype(int) | (outside_transfer.astype(int) << 1)).tolist()
    zeros = {k: int((df[k] == 0).sum()) for k in SCORE_COLS}
    # rank-size view of the heavy tail (log-spaced ranks)
    ranks = sorted(set(np.unique(np.round(np.logspace(0, math.log10(n), 60)).astype(int)).tolist()))
    rank_size = {}
    for k in ("endorserank", "awp", "cpr_l50"):
        srt = np.sort(df[k].to_numpy(dtype=float))[::-1]
        rank_size[k] = [[r, sig(srt[r - 1])] for r in ranks]
    top = {k: [sig(v) for v in np.sort(df[k].to_numpy(dtype=float))[::-1][:10]] for k in ("endorserank", "awp")}
    return {
        "meta": {
            "n": n,
            "analysis": "revised",
            "source": c.rel(c.proc_rev / "same-window") + "/cohort_scores.part*.parquet",
            "order": "rows sorted by node id (the same index in every array)",
            "pct": ("mid-rank percentile in [0, 1] = (average rank - 1)/(n - 1), 4 decimals; tied values "
                    "(e.g. the zero scores of contracts outside a graph) share one position"),
            "raw": "raw integer counts at T_obs (in_approve_degree: distinct owners with a positive latest allowance; "
                   "in_degree: distinct senders)",
            "log10": "log10 of the raw score, 3 decimals; null where the score is 0",
            "flags": "bit 0 (1) = outside the allowance graph (C-PR λ=1 score 0); bit 1 (2) = outside the transfer "
                     "graph (C-PR λ=0 score 0); 3 = outside both",
            "rank_size": "[rank, score] at log-spaced ranks, scores sorted descending (heavy tail)",
            "derived": True,
            "sampling": "none: all contracts of the matched cohort",
            "note": NOTES["contracts_only"],
        },
        "columns": SCORE_COLS + ["in_approve_degree", "in_degree"],
        "pct": pct,
        "raw": raw,
        "log10": log10,
        "flags": flags,
        "zeros": zeros,
        "flag_counts": {"outside_allowance": int(outside_allow.sum()), "outside_transfer": int(outside_transfer.sum()),
                        "outside_both": int((outside_allow & outside_transfer).sum())},
        "rank_size": rank_size,
        "top10": top,
    }


def build_prices(c: Ctx):
    tok = pd.read_csv(c.use(c.usd / "listed_tokens.csv"))
    sel = tok[tok["selected"]].sort_values("rank_by_n")
    pr = pd.read_csv(c.use(c.usd / "daily_prices_usd.csv"))
    days = pd.date_range("2023-10-01", "2026-09-30", freq="D")
    day_s = [d.strftime("%Y-%m-%d") for d in days]
    close, keys, tokens = {}, {}, []
    for _, t in sel.iterrows():
        sym = t["symbol"]
        ascii_sym = "USDT0" if sym.startswith("USD") and "0" in sym and sym != "USDC" else sym
        p = pr[pr["address"] == t["address"]].set_index("day").reindex(day_s)
        close[ascii_sym] = [sig(v) if pd.notna(v) else None for v in p["price_usd"]]
        segs, prev, start = [], None, 0
        for i, k in enumerate(p["key"].fillna("none")):
            if k != prev:
                if prev is not None:
                    segs.append([start, i - 1, prev])
                prev, start = k, i
        segs.append([start, len(day_s) - 1, prev])
        keys[ascii_sym] = segs
        tokens.append({
            "symbol": ascii_sym, "symbol_display": sym, "address": t["address"], "decimals": int(t["decimals"]),
            "feed": t["feed"], "feed_category": t["feed_category"], "relation": t["relation"],
            "rows_tobs": int(t["n_rows_tobs"]), "rank_by_rows": int(t["rank_by_n"]),
            "days": int(p["price_usd"].notna().sum()), "filled_days": int(t["filled_days"]),
            "spike_days": int(t["spike_days"]), "arbitrum_key_first_day": t["arbitrum_key_first_day"],
            "second_key_days_used": int(t["second_key_days_used"]),
            "first": close[ascii_sym][0], "last_obs": close[ascii_sym][day_s.index("2026-06-30")],
            "min": sig(np.nanmin(p["price_usd"])), "max": sig(np.nanmax(p["price_usd"])),
        })
    return {
        "meta": {
            "source": c.rel(c.usd / "daily_prices_usd.csv") + ", " + c.rel(c.usd / "listed_tokens.csv"),
            "unit": "USD daily close (DefiLlama coins API, point nearest 00:00 UTC of the next day)",
            "rounding": "4 significant digits",
            "key_segments": ("[first_day_index, last_day_index, key]; key 'arbitrum' = series under the token's "
                             "Arbitrum address, 'second' = filled from the same asset's CoinGecko series"),
            "windows": {"observation": ["2023-10-01", "2026-06-30"], "W1_labels": ["2026-07-01", "2026-09-30"]},
        },
        "start": day_s[0], "end": day_s[-1], "days": len(day_s),
        "index": {"t1": day_s.index("2026-03-31"), "t_obs": day_s.index("2026-06-30"),
                  "w0_labels": [day_s.index("2026-04-01"), day_s.index("2026-06-30")],
                  "w1_labels": [day_s.index("2026-07-01"), day_s.index("2026-09-30")]},
        "tokens": tokens,
        "close": close,
        "key_segments": keys,
    }


def build_timeline(c: Ctx, digests):
    reg_desc = c.j(c.pub / "describe/describe.json")
    rev_desc = c.j(c.pub_rev / "describe/describe.json")
    manifest = c.j(c.pub / "registered-w1/extraction_manifest.json")
    ledger = c.j(c.data / "bq_ledger.json")
    cfg_path = c.exp / "config/contract_reputation.yaml"
    commits = []
    fallback = {"43d8045": reg_desc["timing"].get("plan_commit_43d8045_utc"),
                "0d3a057": reg_desc["timing"].get("registration_commit_0d3a057_utc")}
    for short, what in COMMITS.items():
        g = git_commit(c.phd, short)
        if g is None:
            g = {"short": short, "utc": zulu(fallback[short]) if fallback.get(short) else None,
                 "source": "describe.json timing (git unavailable)"}
        else:
            g["source"] = "git -C <PHD_WORKS> show"
        g["what"] = what
        g["what_ko"] = COMMITS_KO[short]
        commits.append(g)
    events = [
        {"t": zulu(reg_desc["timing"]["scan_a"]["created"]), "id": "scan_a_created",
         "en": "Scan A (observation-window logs) job created", "ko": "1차 추출(관측 기간 로그) 시작",
         "source": "describe/describe.json : timing.scan_a.created (registered)"},
        {"t": zulu(reg_desc["timing"]["scan_a"]["ended"]), "id": "scan_a_ended",
         "en": "Scan A ended", "ko": "1차 추출 끝", "source": "describe/describe.json : timing.scan_a.ended"},
        {"t": zulu(manifest["started_at"]), "id": "w1_extraction_started",
         "en": "W1 extraction script started (manifest)", "ko": "W1 추출 스크립트 시작(기록 파일)",
         "source": "registered-w1/extraction_manifest.json : started_at"},
        {"t": zulu(reg_desc["timing"]["scan_b"]["created"]), "id": "scan_b_created",
         "en": "Scan B (July-September logs) job created", "ko": "2차 추출(7~9월 로그) 시작",
         "source": "describe/describe.json : timing.scan_b.created"},
        {"t": zulu(reg_desc["timing"]["scan_b"]["ended"]), "id": "scan_b_ended",
         "en": "Scan B ended", "ko": "2차 추출 끝", "source": "describe/describe.json : timing.scan_b.ended"},
        {"t": zulu(manifest["finished_at"]), "id": "w1_extraction_finished",
         "en": "W1 extraction script finished", "ko": "W1 추출 스크립트 끝",
         "source": "registered-w1/extraction_manifest.json : finished_at"},
        {"t": digests["registered"]["written_utc"], "id": "registered_digest",
         "en": "Registered results digest written", "ko": "등록 분석 결과 요약 작성",
         "source": "results_digest.md header"},
    ]
    events.sort(key=lambda e: e["t"])

    def gap(a, b):
        return int((datetime.fromisoformat(b.replace("Z", "+00:00")) - datetime.fromisoformat(a.replace("Z", "+00:00"))).total_seconds())
    cm = {x["short"]: x["utc"] for x in commits}
    ev = {e["id"]: e["t"] for e in events}
    gaps = {"plan_commit_to_scan_a_created_s": gap(cm["43d8045"], ev["scan_a_created"]),
            "registration_commit_to_w1_extraction_start_s": gap(cm["0d3a057"], ev["w1_extraction_started"]),
            "registration_commit_to_scan_b_created_s": gap(cm["0d3a057"], ev["scan_b_created"])}
    jobs = [{"at": zulu(j["at"]), "label": j["label"], "sql": j.get("sql"),
             "tib_billed": sig((j.get("bytes_billed") or 0) / 2 ** 40), "usd": safe(j.get("usd"))}
            for j in ledger["jobs"]]
    monthly = {}
    for name, desc in (("revised", rev_desc), ("registered", reg_desc)):
        streams = {}
        for row in desc["monthly_counts"]:
            streams.setdefault(row["stream"], []).append([row["month"], int(row["n"])])
        monthly[name] = streams
    return {
        "meta": {
            "note": ("Times in UTC. Ledger times are written when a BigQuery job finished. Commit times from "
                     "git; scan times from the registered describe.json timing block; gaps in seconds below."),
            "sources": [c.rel(c.pub / "describe/describe.json"), c.rel(c.pub_rev / "describe/describe.json"),
                        c.rel(c.pub / "registered-w1/extraction_manifest.json"), c.rel(c.data / "bq_ledger.json"),
                        c.rel(cfg_path), "git log of phd_works"],
        },
        "periods": [
            {"id": "extraction", "en": "Scan A (extracted logs; the registered analysis scores all of it)",
             "ko": "1차 추출(뽑은 로그, 등록 분석은 이 기간 전부로 점수를 만듦)",
             "from": "2023-10-01T00:00:00Z", "to": "2026-06-30T23:59:59Z"},
            {"id": "observation", "en": "T_obs score window (twelve months)", "ko": "T_obs 점수 기간(12개월)",
             "from": "2025-07-01T00:00:00Z", "to": "2026-06-30T23:59:59Z",
             "use_en": "scores at T_obs, same-window checks, benchmark, robustness, W1 scores",
             "use_ko": "T_obs 점수, 같은 기간 점검, 벤치마크, 강건성, W1 점수"},
            {"id": "w0_scores", "en": "W0 score window (twelve months before t1)", "ko": "W0 점수 기간(t1 전 12개월)",
             "from": "2025-04-01T00:00:00Z", "to": "2026-03-31T23:59:59Z"},
            {"id": "w0_labels", "en": "W0 labels", "ko": "W0 라벨 기간",
             "from": "2026-04-01T00:00:00Z", "to": "2026-06-30T23:59:59Z"},
            {"id": "w1_labels", "en": "W1 labels (extracted by this study only after the registration commit)",
             "ko": "W1 라벨 기간(이 연구는 등록 커밋 뒤에만 추출)", "from": "2026-07-01T00:00:00Z", "to": "2026-09-30T23:59:59Z"},
        ],
        "anchors": {"data_start": "2023-10-01T00:00:00Z", "t1": "2026-03-31T23:59:59Z",
                    "t_obs": "2026-06-30T23:59:59Z", "data_end": "2026-09-30T23:59:59Z",
                    "score_window_tobs": ["2025-07-01T00:00:00Z", "2026-06-30T23:59:59Z"],
                    "score_window_t1": ["2025-04-01T00:00:00Z", "2026-03-31T23:59:59Z"],
                    "max_age_days_tobs": 365, "max_age_days_t1": 365},
        "commits": commits,
        "events": events,
        "gaps": gaps,
        "ledger_jobs": jobs,
        "bigquery": {"registered_usd": reg_desc["timing"]["bigquery_usd_total"],
                     "registered_tib": reg_desc["timing"]["bigquery_tib_billed"],
                     "total_usd": rev_desc["timing"]["bigquery_usd_total"],
                     "total_tib": rev_desc["timing"]["bigquery_tib_billed"],
                     "revised_jobs_usd": round(rev_desc["timing"]["usd_ego_tables_jobs_usd"]
                                               + rev_desc["timing"]["usd12m_jobs_usd"], 2),
                     "usd_ego_tables_jobs_usd": rev_desc["timing"]["usd_ego_tables_jobs_usd"],
                     "score_window_jobs_usd": rev_desc["timing"]["usd12m_jobs_usd"], "budget_usd": 50},
        "monthly_counts": monthly,
        "gmx_contract_traders_by_quarter": rev_desc["gmx_contract_traders_by_quarter"],
    }


def build_scale(c: Ctx):
    out = {"meta": {"note": "Counts exactly as in the published summaries of both analyses.",
                    "revised_note": NOTES["revised"], "registered_note": NOTES["registered"]}}
    usd_inputs = c.j(c.usd / "usd_inputs.json")
    rows12 = c.j(c.usd12 / "token_rows.json")
    per12 = {t["address"].lower(): t for t in rows12["per_listed_token"]}
    in_window = rows12["rows_in_window"]
    tok = pd.read_csv(c.use(c.usd / "listed_tokens.csv"))
    sel = tok[tok["selected"]].sort_values("rank_by_n")
    out["tokens"] = {
        "candidates": usd_inputs["candidates"], "listed": usd_inputs["listed"],
        "priced": usd_inputs["priced_tokens"], "selected": usd_inputs["top_n"],
        "listed_without_price": len(usd_inputs["listed_without_price"]),
        "rows_in_window_tobs": in_window,
        "listed_share_of_rows_tobs": safe(sum(t["rows_total"] for t in rows12["per_listed_token"]) / in_window),
        "priced_share_of_rows_tobs": safe(sum(t["rows_total"] for t in rows12["per_listed_token"] if t["priced"])
                                          / in_window),
        "selected_share_of_rows_tobs": safe(sum(t["rows_total"] for t in rows12["per_listed_token"] if t["selected"])
                                            / in_window),
        "selected_tokens": [{"symbol": ("USDT0" if r["symbol"] not in ("WETH", "USDC", "ARB", "WBTC") else r["symbol"]),
                             "address": r["address"], "rows_tobs": int(per12[r["address"].lower()]["rows_total"]),
                             "feed": r["feed"], "feed_category": r["feed_category"]} for _, r in sel.iterrows()],
        "rows_note": ("rows of the T_obs score window: ego transfers in the window plus positive latest "
                      "allowances at T_obs set inside it (usd-12m/token_rows.json)"),
        "funnel_en": ["Chainlink-mapped tokens", "low/medium market-risk feed", "with a daily price", "top five by rows"],
        "funnel_ko": ["체인링크가 대응시킨 토큰", "위험 등급 낮음·중간", "하루 가격이 있음", "행 수 상위 다섯"],
        "source": c.rel(c.usd / "usd_inputs.json"),
    }
    for name, base, w1dir in (("registered", c.pub, "registered-w1"), ("revised", c.pub_rev, "window-w1")):
        coh = c.j(base / "cohort/matched_cohort.json")
        sw = c.j(base / "same-window/eval_summary.json")
        h0 = c.j(base / "holdout-w0/eval_summary.json")
        w1 = c.j(base / w1dir / "eval_summary.json")
        desc = c.j(base / "describe/describe.json")
        blk = {
            "cohort_rule": coh["rule"], "cohort": coh["cohort"],
            "candidates": coh.get("candidates"), "by_code_kind": coh.get("by_code_kind"),
            "registered_cohort": coh.get("registered_cohort"), "left_out_of_registered": coh.get("left_out_of_registered"),
            "graph_tobs": sw["graph"], "graph_t1": h0["graph"],
            "iterations_tobs": sw["iterations"], "iterations_t1": h0["iterations"],
            "w0": {"spenders": h0["spenders"], "spender_account_types": h0["spender_account_types"],
                   "gained_new_approvals": h0["gained_new_approvals"], "gained_new_senders": h0["gained_new_senders"],
                   "traders": h0["traders"]["n"], "traders_with_any_approval_received": h0["traders"]["with_any_approval_received"],
                   "receiving_subset": h0["receiving"]["n"], "coverage": compact(h0["coverage"])},
            "w1": {"spenders": w1["spenders"], "gained_new_approvals": w1["gained_new_approvals"],
                   "gained_new_senders": w1["gained_new_senders"], "traders": w1["traders"],
                   "traders_liquidated": w1["traders_liquidated"], "traders_all_liquidated": w1["traders_all_liquidated"]},
            "amounts": compact(desc["amounts"]),
            "sources": [c.rel(base / "cohort/matched_cohort.json"), c.rel(base / "same-window/eval_summary.json"),
                        c.rel(base / "holdout-w0/eval_summary.json"), c.rel(base / w1dir / "eval_summary.json"),
                        c.rel(base / "describe/describe.json")],
        }
        if name == "revised":
            blk["rows"] = compact(desc["rows"])
            blk["per_token"] = compact(desc["per_token"])
            blk["listed_tokens"] = desc["listed_tokens"]
        out[name] = blk
    out["gmx"] = {"obs": c.j(c.pub_rev / "gmx/gmx_contract_closes_obs_decoded.json"),
                  "w1": c.j(c.pub_rev / "gmx/gmx_contract_closes_w1_decoded.json")}
    return out


def neutral_matrix(nb):
    labels = list(TRADER_LABELS)
    rows = []
    for pair in NEUTRAL_PAIRS:
        g = nb["grid"][pair]
        row = []
        for lab in labels:
            e = g[lab]
            cell = [safe(e["delta_tau"]), safe(e["ci_low"]), safe(e["ci_high"]), safe(e["a_tau"]), safe(e["b_tau"]),
                    safe(e["share_positive"])]
            if "ci975_low" in e:
                cell += [safe(e["ci975_low"]), safe(e["ci975_high"])]
            row.append(cell)
        rows.append(row)
    taus = {m: [[safe(nb["taus"][m][lab]["kendall_tau"]), safe(nb["taus"][m][lab]["ci_low"]),
                 safe(nb["taus"][m][lab]["ci_high"])] for lab in labels] for m in nb["taus"]}
    return {"n": nb["n"], "B": sorted(n_boots(nb)), "pairs": list(NEUTRAL_PAIRS), "labels": labels,
            "cell": "[Δτ, lo95, hi95, τa, τb, P(Δτ>0)(, lo97.5, hi97.5 for the liquidation-free rate of P and Q)]",
            "grid": rows, "taus": taus, "stratified": compact(nb["stratified"]),
            "recipients": compact(nb["recipients"]), "influence_without_top10": compact(nb["influence_without_top10"]),
            "max_in_approve_degree": nb["max_in_approve_degree"]}


def build_results(c: Ctx):
    res = {
        "meta": {
            "tau": "[τ_b, lo95, hi95] (per proxy: [τ_b, lo95, hi95, Spearman ρ]); family entries are family means",
            "contrast": "{d: [Δτ, lo95, hi95], ta: τ_a, tb: τ_b, p: P(Δτ>0), B} (+ d975 = Bonferroni 97.5% interval)",
            "B": "paired bootstrap over contracts, 400 resamples, seed 42; neutral-label blocks 2,000 resamples",
            "notes": NOTES,
            "rounding": "4 significant digits, kept long enough that 1-4 decimal displays match the summaries",
        },
        "methods": method_labels(),
        "proxies": {k: {"family": f, "en": en, "ko": ko} for k, f, en, ko in PROXIES},
        "families": {k: {"en": en, "ko": ko} for k, (en, ko) in FAMILIES.items()},
        "spender_labels": {k: {"en": en, "ko": ko} for k, (en, ko) in SPENDER_LABELS.items()},
        "trader_labels": {k: {"en": en, "ko": ko} for k, (en, ko) in TRADER_LABELS.items()},
        "neutral_pairs": {k: {"a": a, "b": b, "en": t} for k, (a, b, t) in NEUTRAL_PAIRS.items()},
    }
    raw = {}
    for name, base, w1dir in (("revised", c.pub_rev, "window-w1"), ("registered", c.pub, "registered-w1")):
        sw = c.j(base / "same-window/eval_summary.json")
        h0 = c.j(base / "holdout-w0/eval_summary.json")
        w1 = c.j(base / w1dir / "eval_summary.json")
        sup = c.j(base / "supplementary/supplementary.json")
        rob = c.j(base / "robustness/robustness.json")
        raw[name] = (sw, h0, w1)
        res[name] = {
            "status": NOTES[name], "status_ko": NOTES[name + "_ko"],
            "same_window": compact(sw), "w0": compact(h0), "w1": compact(w1),
            "supplementary": compact(sup), "robustness": compact(rob),
            "B_values": {"same_window": sorted(n_boots(sw)), "w0": sorted(n_boots(h0)), "w1": sorted(n_boots(w1))},
            "status_by_block": {
                "same_window.families/per_proxy": "intended-construct check (not validation)",
                "same_window.contrasts": "post hoc (reported beside rule A secondary; do not decide it)",
                "same_window.rule_a_secondary": "rule A, secondary part" + (" (re-analysis)" if name == "revised" else " (registered, plan 43d8045)"),
                "w0.contrasts_prefixed": "rule A, primary part" + (" (re-analysis)" if name == "revised" else " (registered, plan 43d8045)"),
                "w0.contrasts_after": "post hoc",
                "w0.receiving": "post hoc restriction",
                "w0.traders": "exploratory (no rule)",
                "w1.rule_b": "rule B (F1-F3 decide; F4-F6 reported beside)" + (" (re-analysis)" if name == "revised" else " (registered, 0d3a057)"),
                "w1.sensitivity_awp/isolated": "registered sensitivity analyses, do not enter the decision",
                "w1.endorserank_results": "not registered; computed after the W1 labels were known",
                "w1.neutral_rules": "R1-R3" + (" (re-analysis)" if name == "revised" else " (registered, 0d3a057)"),
                "supplementary": "post hoc, outside every rule",
                "robustness": "sensitivity checks (sample definition: not in the plan; run after the W1 labels)",
            },
            "sources": [c.rel(base / "same-window/eval_summary.json"), c.rel(base / "holdout-w0/eval_summary.json"),
                        c.rel(base / w1dir / "eval_summary.json"), c.rel(base / "supplementary/supplementary.json"),
                        c.rel(base / "robustness/robustness.json")],
        }
    # --- verdicts
    verdicts = {}
    for name, (sw, h0, w1) in raw.items():
        rb = w1["rule_b"]
        verdicts[name] = {
            "status": NOTES[name],
            "rule_a_primary": {"pass": h0["rule_a_primary"]["pass"],
                               "no_worse_on_new_approvals": h0["rule_a_primary"]["no_worse_on_new_approvals"],
                               "better_on_new_senders": h0["rule_a_primary"]["better_on_new_senders"],
                               "contrasts": compact(h0["contrasts_prefixed"])},
            "rule_a_secondary": compact(sw["rule_a_secondary"]),
            "rule_b": {"decision": rb["decision"],
                       "F": {k: compact(rb[k]) for k in ("F1", "F2", "F3", "F4", "F5", "F6a", "F6b")},
                       "F6": rb["F6"],
                       "conditions_en": {"F1": "spenders, new approval pairs: 95% interval of Δτ above 0",
                                         "F2": "spenders, new transfer senders: lower end above -δ (δ = 0.01)",
                                         "F3": "traders, liquidation-free close rate: lower end above -δ"},
                       "conditions_ko": {"F1": "스펜더, 새 허락 쌍: Δτ의 95% 구간이 0보다 위",
                                         "F2": "스펜더, 새 송금자: 구간 아래 끝이 -δ(δ = 0.01)보다 위",
                                         "F3": "트레이더, 청산 없이 닫은 비율: 구간 아래 끝이 -δ보다 위"}},
            "rule_b_sensitivity_awp": w1["sensitivity_awp"]["decision"],
            "rule_b_sensitivity_isolated": w1["sensitivity_isolated"]["decision"],
            "R1": w1["neutral_rules"]["R1"], "R2": w1["neutral_rules"]["R2"], "R3": w1["neutral_rules"]["R3"],
            "P_w1": compact(w1["neutral_w1"]["grid"]["P"]["liquidation_free_rate"]),
            "Q_w1": compact(w1["neutral_w1"]["grid"]["Q"]["liquidation_free_rate"]),
            "P_w0": compact(w1["neutral_w0"]["grid"]["P"]["liquidation_free_rate"]),
            "Q_w0": compact(w1["neutral_w0"]["grid"]["Q"]["liquidation_free_rate"]),
        }
    res["verdicts"] = verdicts
    # --- lambda sweep
    sweep = {}
    for name, (sw, h0, w1) in raw.items():
        def fam(m, f):
            e = sw["families"][m][f]
            return [safe(e["mean_tau"]), safe(e["ci_low"]), safe(e["ci_high"])]

        def tau(block, m, lab):
            e = block[m][lab]
            return [safe(e["kendall_tau"]), safe(e["ci_low"]), safe(e["ci_high"])]

        def line(keys):
            return {
                "same_window": {f: [fam(m, f) for m in keys] for f in FAMILIES},
                "w0_spenders": {lab: [tau(h0["taus"], m, lab) for m in keys]
                                for lab in ("future_new_approvers", "future_new_transfer_senders")},
                "w1_spenders": {lab: [tau(w1["spender_taus"], m, lab) for m in keys]
                                for lab in ("future_new_approvers", "future_new_transfer_senders")},
                "w1_traders_liquidation_free_rate": [[safe(w1["trader_taus"][m]["kendall_tau"]),
                                                      safe(w1["trader_taus"][m]["ci_low"]),
                                                      safe(w1["trader_taus"][m]["ci_high"])] for m in keys],
                "iterations_tobs": [sw["iterations"][m] for m in keys],
                "iterations_t1": [h0["iterations"][m] for m in keys],
            }
        sweep[name] = {"lambda": LAMBDAS, "keys": LAMBDA_KEYS, **line(LAMBDA_KEYS),
                       "references": {m: line([m]) for m in ("endorserank", "endorserank_activity", "awp", "spr")}}
        degs = {"in_approve_degree": "t1_in_approve_degree", "in_degree": "t1_in_degree"}
        sweep[name]["degree_baselines"] = {
            k: {"w0_spenders": {lab: tau(h0["taus"], v, lab) for lab in ("future_new_approvers", "future_new_transfer_senders")},
                "w1_spenders": {lab: tau(w1["spender_taus"], k, lab) for lab in ("future_new_approvers", "future_new_transfer_senders")},
                "w1_traders_liquidation_free_rate": [safe(w1["trader_taus"][k]["kendall_tau"]),
                                                     safe(w1["trader_taus"][k]["ci_low"]),
                                                     safe(w1["trader_taus"][k]["ci_high"])]}
            for k, v in degs.items()}
    res["lambda_sweep"] = {
        "meta": {"note": ("λ = 0 and λ = 1 are the layers walked alone (C-PR λ=0: transfer layer, λ=1: allowance "
                          "layer); the family is not continuous at the end points. λ = 0.5 is primary; 0.25 and 0.75 "
                          "are the fixed sensitivity values. λ was never tuned on labels."),
                 "note_ko": ("λ = 0과 λ = 1은 한 층만 걷는 점수예요(0은 송금 층, 1은 허락 층). 양 끝에서 값이 이어지지 "
                             "않아요. 주 설정은 λ = 0.5, 0.25와 0.75는 미리 정한 민감도 값이에요. 라벨을 보고 λ를 고르지 않았어요.")},
        **sweep}
    # --- closed form
    cf = {}
    for name, (sw, h0, w1) in raw.items():
        cf[name] = {}
        for win, blk in (("same_window", sw), ("w0", h0)):
            b = blk["closed_form"]
            cf[name][win] = {**compact(b), "deeper_spenders": b["spenders"] - b["depth_one_spenders"]}
    res["closed_form"] = {
        "meta": {"formula": "r_v = c (1 + d δ(v)),  δ(v) = Σ_u w(u,v)/o(u)",
                 "c": "common score of every node without in-edges, c = (1 - d + d r_D)/|V|",
                 "within_1pct": "share of spenders whose EndorseRank lies within 1% of the closed form"},
        **cf}
    # --- neutral grid
    res["neutral"] = {
        "meta": {"note": ("Comparison on GMX V2 trader labels built from neither edge type, registered with rule B "
                          "(0d3a057). W1 primary, W0 secondary. On the revised scores it is a re-analysis."),
                 "rules_en": {"R1": "count-level lead: 97.5% interval of P and 95% interval of stratified P above 0 in W1, and P > 0 in W0",
                              "R2": "PageRank-level lead: 97.5% interval of Q above 0 in W1 and Q > 0 in W0",
                              "R3": "specificity: P on the profitable or non-loss share in W1 below 0 with a 95% interval excluding 0"},
                 "rules_ko": {"R1": "개수 수준 우위: W1에서 P의 97.5% 구간과 층별 P의 95% 구간이 0보다 위, W0에서 P > 0",
                              "R2": "페이지랭크 수준 우위: W1에서 Q의 97.5% 구간이 0보다 위, W0에서 Q > 0",
                              "R3": "특정성: W1에서 이익·손실 없는 닫기 비율의 P가 0보다 아래이고 95% 구간이 0을 벗어남"}},
        **{name: {"w1": neutral_matrix(w1["neutral_w1"]), "w0": neutral_matrix(w1["neutral_w0"]),
                  "rules": w1["neutral_rules"]} for name, (sw, h0, w1) in raw.items()},
    }
    return res


def sybil_curve(er: np.ndarray, c_common: float, d: float):
    qs = sorted(set([round(q, 2) for q in np.arange(0, 90, 1.0)] + [round(q, 2) for q in np.arange(90, 99, 0.25)]
                    + [round(q, 2) for q in np.arange(99, 100.0001, 0.02)]))
    pts = []
    for q in qs:
        s = float(np.percentile(er, q))
        f = max(0.0, ((s * (1 - d ** 2) / c_common) - 1) / d)
        pts.append([q, sig(s), safe(f), int(math.ceil(f - 1e-9)) if f > 0 else 0])
    return pts


def build_sybil(c: Ctx, cfg):
    d = float(cfg["reputation"]["damping"])
    out = {"meta": {
        "curve": ("[percentile q of the cohort's EndorseRank, score s_q, farm addresses f needed, ceil(f)] with "
                  "f = max(0, (s_q (1 - d^2)/c - 1)/d), the closed form r_t = c (1 + d f)/(1 - d^2) of a star of f "
                  "farm addresses that approve target t, which approves each back (experiments/scripts/sybil_model.py); "
                  "each farm address costs two approvals per window"),
        "derived": True,
        "caveat": "before counting that a farm that large would itself enlarge |V| and lower c",
        "d": d}}
    for name, base, proc in (("revised", c.pub_rev, c.proc_rev), ("registered", c.pub, c.proc)):
        sm = c.j(base / "sybil-model/sybil_model.json")
        coh = c.pq(proc / "same-window", "cohort_scores")
        er = coh["endorserank"].to_numpy(dtype=float)
        cc = sm["b_common"]
        curve = sybil_curve(er, cc, d)
        check = {}
        for k, v in sm["farm_size_to_reach_cohort_quantile"].items():
            q = float(k[1:])
            s = float(np.percentile(er, q))
            check[k] = {"json_score": v["score"], "parquet_score": s, "match": bool(abs(s - v["score"]) <= 1e-12 * max(1, abs(s)) + 1e-18)}
        out[name] = {
            "json": compact(sm),
            "key_points": {k: {"score": sig(v["score"]), "farm_addresses": safe(v["farm_addresses"]),
                               "farm_addresses_ceil": int(math.ceil(v["farm_addresses"])) if v["farm_addresses"] > 0 else 0,
                               "approvals_per_window": 2 * (int(math.ceil(v["farm_addresses"])) if v["farm_addresses"] > 0 else 0)}
                           for k, v in sm["farm_size_to_reach_cohort_quantile"].items()},
            "pair_score": sig(cc / (1 - d)), "gain_per_farm_address": sig(d * cc / (1 - d ** 2)),
            "highest_over_c": sig(sm["star"]["highest_cohort_endorserank"] / cc),
            "curve": curve, "quantile_check": check, "cohort_n": int(len(er)),
            "source": c.rel(base / "sybil-model/sybil_model.json") + " + " + c.rel(proc / "same-window") + "/cohort_scores",
        }
    return out


def build_benchmark(c: Ctx):
    out = {"meta": {"note": NOTES["speed"], "note_ko": NOTES["speed_ko"],
                    "derived": "the two ratios are the derived rows of the digest (runtime ratio beside edge ratio)",
                    "fields": "mean_s, sd_s, runs_s, peak_mb (warm-up run, tracemalloc), iterations, nodes |V|, edges |E|"}}
    for name, base in (("revised", c.pub_rev), ("registered", c.pub)):
        b = c.j(base / "benchmark/benchmark.json")
        blk = compact(b)
        m = b["main"]
        blk["derived"] = {
            "time_ratio_awp_over_er": safe(m["awp"]["mean_s"] / m["endorserank"]["mean_s"]),
            "edge_ratio_awp_over_er": safe(m["awp"]["edges"] / m["endorserank"]["edges"]),
        }
        blk["source"] = c.rel(base / "benchmark/benchmark.json")
        out[name] = blk
    return out


def build_params(c: Ctx, cfg):
    contracts_df = c.pq(c.proc_rev / "same-window", "cohort_scores")
    c.use(c.exp / "config/contract_reputation.yaml")
    rep = cfg["reputation"]
    consts = c.j(c.usd12 / "constants.json")
    sw_rev = c.j(c.pub_rev / "same-window/eval_summary.json")
    h0_rev = c.j(c.pub_rev / "holdout-w0/eval_summary.json")
    sm = c.j(c.pub_rev / "sybil-model/sybil_model.json")
    k, t0 = float(rep["awp_decay_k"]), float(rep["awp_decay_t0_days"])
    d = float(rep["damping"])

    def sigma(dt):
        return 1.0 / (1.0 + math.exp(k * (dt - t0)))

    def V(z, b):
        return 2.0 / (1.0 + math.exp(-b * z)) - 1.0

    dts = list(range(0, 366, 5))
    zs = [float(f"{z:.4g}") for z in np.logspace(-1, 6, 141)]
    bT, bA = consts["b_transfer"], consts["b_allowance"]
    # worked example of Chapter 2 (toy graph from the thesis text)
    nodes = ["A", "B", "C", "D"]
    edges = [("A", "B", 2.0), ("A", "C", 1.0), ("B", "D", 3.0), ("C", "D", 1.0)]
    idx = {v: i for i, v in enumerate(nodes)}
    W = np.zeros((4, 4))
    for u, v, w in edges:
        W[idx[u], idx[v]] = w
    o = W.sum(1)
    P = np.divide(W, o[:, None], out=np.zeros_like(W), where=o[:, None] > 0)
    dang = (o == 0).astype(float)
    r = np.full(4, 0.25)
    hist = [r.tolist()]
    for _ in range(200):
        r2 = (1 - d) / 4 + d * P.T @ r + d * (r @ dang) / 4
        diff = float(np.abs(r2 - r).sum())
        r = r2
        hist.append(r.tolist())
        if diff < 1e-12:
            break
    worked = {
        "nodes": nodes, "edges": [[u, v, w] for u, v, w in edges], "d": d,
        "out_strength": dict(zip(nodes, o.tolist())), "teleport_per_node": (1 - d) / 4,
        "r1": [round(x, 4) for x in hist[1]], "stationary": [round(x, 4) for x in r],
        "dangling_share_to_each": round(d * r[3] / 4, 4),
        "iterations": [[round(x, 5) for x in h] for h in hist[:41]],
        "source": "toy graph of thesis Chapter 2 (worked example); vectors computed here by power iteration",
        "thesis_values": {"r1": [0.0906, 0.2323, 0.1615, 0.5156], "stationary": [0.1375, 0.2154, 0.1765, 0.4706]},
    }
    # eight real contracts for a Kendall tau illustration (EndorseRank vs in-approve degree)
    df = contracts_df.sort_values("endorserank").reset_index(drop=True)
    picks = [int(round(q * (len(df) - 1))) for q in (0.05, 0.18, 0.31, 0.44, 0.57, 0.70, 0.83, 0.96)]
    sub = df.iloc[picks]
    xs, ys = sub["endorserank"].to_numpy(), sub["in_approve_degree"].to_numpy()
    nc = nd = t1 = t2 = 0
    pairs = []
    for i in range(len(xs)):
        for j in range(i + 1, len(xs)):
            sx, sy = np.sign(xs[j] - xs[i]), np.sign(ys[j] - ys[i])
            kind = "tied_x" if sx == 0 and sy != 0 else "tied_y" if sy == 0 and sx != 0 else \
                "tied_both" if sx == 0 and sy == 0 else ("concordant" if sx == sy else "discordant")
            nc += kind == "concordant"
            nd += kind == "discordant"
            pairs.append([i, j, kind])
    n0 = len(xs) * (len(xs) - 1) // 2

    def ties(a):
        _, cnt = np.unique(a, return_counts=True)
        return int(sum(t * (t - 1) // 2 for t in cnt))
    t1, t2 = ties(xs), ties(ys)
    kendall_demo = {
        "derived": True,
        "note": ("eight contracts of the matched cohort taken at the 5th, 18th, ..., 96th percentile of EndorseRank; "
                 "an illustration of the τ_b formula, not a thesis result"),
        "endorserank": [sig(v) for v in xs], "in_approve_degree": [int(v) for v in ys],
        "pairs": pairs, "n0": n0, "nc": int(nc), "nd": int(nd), "n1": t1, "n2": t2,
        "tau_b": safe((nc - nd) / math.sqrt((n0 - t1) * (n0 - t2))) if (n0 - t1) * (n0 - t2) > 0 else None,
    }
    return {
        "meta": {"sources": [c.rel(c.exp / "config/contract_reputation.yaml"), c.rel(c.usd12 / "constants.json"),
                             c.rel(c.pub_rev / "same-window/eval_summary.json"), c.rel(c.pub_rev / "sybil-model/sybil_model.json")],
                 "note": ("Parameters fixed in the configuration of 9 October 2026; the US-dollar constants of the revised "
                          "analysis are set on the W0 score window (usd-12m/constants.json).")},
        "chain": {"name": cfg["chain_name"], "id": cfg["chain_id"]},
        "pagerank": {"d": d, "tol": float(rep["pagerank_tolerance"]), "max_iter": int(rep["max_iterations"]),
                     "start": "r(0) = 1/|V|", "stop": "||r(t+1) - r(t)||_1 < tol or max_iter",
                     "update": "r(t+1) = (1-d) π + d Pᵀ r(t) + d (r(t)ᵀ 1_dang) π",
                     "restarts": {"endorserank": "uniform", "awp": "π_u ∝ X_u (activeness)",
                                  "cpr": "uniform", "spr": "π ∝ C-PR (λ=1) scores on V_T"}},
        "decay": {"k": k, "t0_days": t0, "formula": "σ(Δt) = 1 / (1 + exp(k (Δt - t0)))",
                  "table": [[t, round(sigma(t), 4)] for t in (0, 90, 180, 273, 365)],
                  "curve": {"dt": dts, "sigma": [sig(sigma(t)) for t in dts]}},
        "value": {"formula": "V(z) = 2/(1 + e^(-b z)) - 1", "rule": consts["rule"],
                  "m_T": consts["m_transfer_usd"], "m_A": consts["m_allowance_usd"],
                  "m_T_raw": safe(consts["raw"]["m_transfer"]), "m_A_raw": safe(consts["raw"]["m_allowance"]),
                  "b_T": sig(bT, 6), "b_A": sig(bA, 6), "b_registered": float(rep["awp_value_b"]),
                  "ln3": sig(math.log(3), 6),
                  "points": {"V(m)": 0.5, "V(2m)": round(V(2, math.log(3)), 4), "V(m/2)": round(V(0.5, math.log(3)), 4)},
                  "curve": {"z_usd": zs, "V_T": [sig(V(z, bT)) for z in zs], "V_A": [sig(V(z, bA)) for z in zs]},
                  "constants_computed_at": consts["computed_at"]},
        "cap": {"U_usd": consts["cap_allowance_usd"], "p99_transfer_usd_raw": safe(consts["raw"]["p99_transfer"]),
                "p99_finite_allowance_usd_raw": sig(consts["raw"]["p99_allowance"]),
                "unlimited_threshold_base_units": consts["unlimited_base_units"],
                "uint256_max": sig(2.0 ** 256 - 1),
                "note": ("U = 99th percentile of single-transfer USD values in the W0 score window (2025-04-01 to t1), "
                         "rounded to two significant digits; the 99th percentile of the finite allowances themselves is "
                         "about 1e63 USD, so a cap taken from them would leave unlimited allowances in charge of the rows")},
        "coupled": {"lambda_primary": float(rep["hybrid"]["coupled_lambda_primary"]),
                    "lambda_grid": [float(x) for x in rep["hybrid"]["coupled_lambda_grid"]], "endpoints": [0.0, 1.0],
                    "row": "P(λ)_u = α_A(u) P_A,u + α_T(u) P_T,u; α_A = λ 1[o_A>0]/D, α_T = (1-λ) 1[o_T>0]/D"},
        "stats": {"B": int(cfg["alignment"]["bootstrap_resamples"]), "seed": int(cfg["alignment"]["bootstrap_seed"]),
                  "B_neutral": 2000, "ci": 0.95, "bonferroni_ci": 0.975,
                  "delta": float(cfg["registered_window"]["margin_delta"]),
                  "kendall": "τ_b = (n_c - n_d) / sqrt((n0 - n1)(n0 - n2))",
                  "spearman_no_ties": "ρ = 1 - 6 Σ (R_i - S_i)^2 / (n (n^2 - 1))",
                  "family_mean": "plain average of the τ of the family's proxies"},
        "cohort": {"min_owners": int(cfg["cohort"]["min_owners"]), "gmx_min_closes": int(cfg["gmx_arbitrum"]["min_closes"]),
                   "tokens": ["WETH", "USDC", "USDT0", "ARB", "WBTC"]},
        "windows": {"period_start": cfg["period"]["start_ts"], "t_obs": cfg["period"]["observation_end"],
                    "t1": cfg["holdout"]["score_end"], "w0_labels": [cfg["holdout"]["outcome_start"], cfg["holdout"]["outcome_end"]],
                    "w1_labels": [cfg["registered_window"]["outcome_start"], cfg["registered_window"]["outcome_end"]]},
        "benchmark": {"warmup_runs": int(cfg["benchmark"]["warmup_runs"]), "timed_runs": int(cfg["benchmark"]["timed_runs"]),
                      "scaling_seed": cfg["benchmark"]["scaling_seed"]},
        "robustness": {"damping_values": [float(x) for x in cfg["robustness"]["damping_values"]],
                       "value_slope_factors": [0.1, 1, 10]},
        "closed_form": {"formula": "r_v = c (1 + d δ(v))", "c_tobs": sig(sw_rev["closed_form"]["common_value_c"]),
                        "c_t1": sig(h0_rev["closed_form"]["common_value_c"])},
        "sybil": {"c": sig(sm["b_common"]), "sigma0": safe(sm["sigma0"]), "r_D": safe(sm["r_D"]),
                  "closed_cluster": "Σ_S r = (|S|/|V|) (1 - d + d r_D)/(1 - d)",
                  "bound": "Σ_S r ≤ |S| / ((1 - d)|V| + d |S|)",
                  "star": "r_t = c (1 + d f)/(1 - d^2)", "pair": "r = c/(1 - d)"},
        "worked_example": worked,
        "kendall_demo": kendall_demo,
    }


def build_traders(c: Ctx):
    out = {"meta": {"note": ("GMX V2 contract traders (contract accounts in the freeze-date graph with at least three "
                             "closes in the label window). Scores at the freeze as percentile ranks within the "
                             "trader cohort; labels from GMX closes, built from neither edge type. W0 is exploratory."),
                    "pct": "mid-rank percentile within the trader cohort, 4 decimals", "derived": True}}
    for name, d, deg in (("w0", c.proc_rev / "holdout-w0", ("t1_in_approve_degree", "t1_in_degree")),
                         ("w1", c.proc_rev / "window-w1", ("in_approve_degree", "in_degree"))):
        t = c.pq(d, "trader_scores").sort_values("id").reset_index(drop=True)
        cols = SCORE_COLS + list(deg)
        out[name] = {
            "n": len(t),
            "pct": {(k.replace("t1_", "")): round_list(pct_rank(t[k])) for k in cols},
            "raw": {"in_approve_degree": [int(v) for v in t[deg[0]]], "in_degree": [int(v) for v in t[deg[1]]],
                    "closes": [int(v) for v in t["closes"]], "liquidations": [int(v) for v in t["liquidations"]],
                    "profitable_closes": [int(v) for v in t["profitable_closes"]],
                    "losses": [int(v) for v in t["losses"]],
                    "realized_gain_usd": [sig(v) for v in t["realized_gain"]],
                    "liquidation_free_rate": [safe(v) for v in t["liquidation_free_rate"]],
                    "no_liquidation": [int(v) for v in t["no_liquidation"]],
                    "profitable_share": [safe(v) for v in t["profitable_share"]],
                    "non_loss_share": [safe(v) for v in t["non_loss_share"]]},
            "source": c.rel(d) + "/trader_scores.part*.parquet",
        }
    return out


def build_holdout(c: Ctx):
    out = {"meta": {"derived": True,
                    "note": ("Descriptive: spenders grouped into ten bins by the mid-rank percentile of each score at the "
                             "freeze; per bin the number of spenders, the share that gained at least one new approval "
                             "pair / new transfer sender, and the mean counts. Tied scores (e.g. AWP = 0 for spenders "
                             "without a transfer edge) stay in one bin, so bins differ in size. Not a thesis table; the "
                             "τ_b values are in results.*.w0.taus and results.*.w1.spender_taus."),
                    "bin": "[n, share_new_approvals, share_new_senders, mean_new_approvals, mean_new_senders]"}}
    for name, d, deg in (("w0", c.proc_rev / "holdout-w0", ("t1_in_approve_degree", "t1_in_degree")),
                         ("w1", c.proc_rev / "window-w1", ("in_approve_degree", "in_degree"))):
        s = c.pq(d, "spender_scores")
        na, ns = s["future_new_approvers"].to_numpy(), s["future_new_transfer_senders"].to_numpy()
        bins = {}
        for k in SCORE_COLS + list(deg):
            r = pd.Series(s[k].to_numpy(dtype=float)).rank(method="average").to_numpy()
            b = np.minimum(((r - 0.5) / len(r) * 10).astype(int), 9)
            rows = []
            for i in range(10):
                m = b == i
                nn = int(m.sum())
                rows.append([nn, safe((na[m] > 0).mean()) if nn else None, safe((ns[m] > 0).mean()) if nn else None,
                             safe(na[m].mean()) if nn else None, safe(ns[m].mean()) if nn else None])
            bins[k.replace("t1_", "")] = rows
        out[name] = {"n": int(len(s)), "base_rate_new_approvals": safe((na > 0).mean()),
                     "base_rate_new_senders": safe((ns > 0).mean()),
                     "gained_new_approvals": int((na > 0).sum()), "gained_new_senders": int((ns > 0).sum()),
                     "bins": bins, "source": c.rel(d) + "/spender_scores.part*.parquet"}
    return out


# ----------------------------------------------------------------------------- digests and verification

def parse_digest(p: Path):
    text = p.read_text(encoding="utf-8")
    m = re.search(r"on (\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}) UTC", text)
    written = f"{m.group(1)}T{m.group(2)}:00Z" if m else None
    rows = {}
    for line in text.splitlines():
        if not line.startswith("| ") or line.startswith("| Quantity") or line.startswith("|---"):
            continue
        cells = [x.strip() for x in line.strip().strip("|").split(" | ")]
        if len(cells) < 3:
            continue
        q, val, src = cells[0], cells[1], " | ".join(cells[2:])
        src = src.replace("`", "").strip()
        rows.setdefault(src, []).append((q, val))
    return {"written_utc": written, "rows": rows}


NUM = re.compile(r"-?\d[\d,]*\.?\d*(?:e[-+]?\d+)?", re.I)


def numbers(s: str):
    s = s.replace("P(\u0394\u03c4>0)", "P").replace("97.5%", "")
    out = []
    for tok in NUM.findall(s):
        t = tok.replace(",", "")
        dec = len(t.split("e")[0].split(".")[1]) if "." in t.split("e")[0] else 0
        out.append((float(t), dec, "e" in t.lower()))
    return out


def read_deck(out: Path):
    deck = {}
    for p in sorted(out.glob("*.js")):
        txt = p.read_text(encoding="utf-8")
        m = re.search(r"window\.DECK_DATA\.(\w+) = (.*);\s*$", txt, re.S)
        deck[m.group(1)] = json.loads(m.group(2))
    return deck


def verify(c: Ctx, digests):
    deck = read_deck(c.out)
    R, Rg = digests["revised"]["rows"], digests["registered"]["rows"]
    res, scale, sy, bm, pr = deck["results"], deck["scale"], deck["sybil"], deck["benchmark"], deck["prices"]
    checks = []

    def add(name, digest_rows, src, ours, pick=None):
        """Compare the numbers of a digest row with ours (list of numbers or bool)."""
        rows = digest_rows.get(src)
        if not rows:
            checks.append((name, "<missing in digest>", ours, False))
            return
        q, val = rows[0] if pick is None else next(r for r in rows if pick in r[0])
        if isinstance(ours, bool):
            ok = (val in ("yes", "holds")) == ours if val in ("yes", "no", "holds", "does not hold") else False
            checks.append((name, val, ours, ok))
            return
        dn = numbers(val)
        ok = len(dn) >= len(ours)
        for (dv, dec, is_e), ov in zip(dn, ours):
            if ov is None:
                ok = False
                break
            tol = (0.5 * 10 ** (-dec) + 1e-12) if not is_e else abs(dv) * 5e-4
            ok &= abs(float(ov) - dv) <= tol
        checks.append((name, val, ours, bool(ok)))

    sw, w1, h0 = res["revised"]["same_window"], res["revised"]["w1"], res["revised"]["w0"]
    add("rev: matched cohort", R, "cohort/matched_cohort.json : cohort", [scale["revised"]["cohort"]])
    add("rev: T_obs allowance edges", R, "same-window/eval_summary.json : graph.allowance.edges",
        [scale["revised"]["graph_tobs"]["allowance"]["edges"]])
    add("rev: T_obs transfer edges", R, "same-window/eval_summary.json : graph.transfer.edges",
        [scale["revised"]["graph_tobs"]["transfer"]["edges"]])
    add("rev: ER allowance family", R, "same-window/eval_summary.json : families.endorserank.allowance",
        sw["families"]["endorserank"]["allowance"])
    add("rev: C-PR(λ=0) transfer family", R, "same-window/eval_summary.json : families.cpr_l0.transfer",
        res["lambda_sweep"]["revised"]["same_window"]["transfer"][0])
    add("rev: AWP Sybil family", R, "same-window/eval_summary.json : families.awp.sybil_stability",
        sw["families"]["awp"]["sybil_stability"])
    f1 = res["verdicts"]["revised"]["rule_b"]["F"]["F1"]
    add("rev: rule B F1", R, "window-w1/eval_summary.json : rule_b.F1", f1["d"] + [f1["ta"], f1["tb"], f1["p"]])
    add("rev: rule B decision", R, "window-w1/eval_summary.json : rule_b.decision", res["verdicts"]["revised"]["rule_b"]["decision"])
    add("rev: rule A primary pass", R, "holdout-w0/eval_summary.json : rule_a_primary.pass",
        res["verdicts"]["revised"]["rule_a_primary"]["pass"])
    add("rev: R3", R, "window-w1/eval_summary.json : neutral_rules.R3", res["verdicts"]["revised"]["R3"])
    add("rev: W1 in-approve degree, new pairs", R,
        "window-w1/eval_summary.json : spender_taus.in_approve_degree.future_new_approvers",
        res["lambda_sweep"]["revised"]["degree_baselines"]["in_approve_degree"]["w1_spenders"]["future_new_approvers"])
    add("rev: W1 ER, new pairs", R, "window-w1/eval_summary.json : spender_taus.endorserank.future_new_approvers",
        res["lambda_sweep"]["revised"]["references"]["endorserank"]["w1_spenders"]["future_new_approvers"][0])
    p = res["neutral"]["revised"]["w1"]["grid"][0][0]
    add("rev: W1 P liquidation-free (95%, τa, τb, 97.5%)", R,
        "window-w1/eval_summary.json : neutral_w1.grid.P.liquidation_free_rate", p[0:3] + p[3:5] + p[6:8] + [p[5]])
    add("rev: closed form within 1% (all)", R, "same-window/eval_summary.json : closed_form.within_1pct_all",
        [res["closed_form"]["revised"]["same_window"]["within_1pct_all"]])
    e = bm["revised"]["main"]["endorserank"]
    add("rev: benchmark ER", R, "benchmark/benchmark.json : main.endorserank",
        [e["mean_s"], e["sd_s"]] + e["runs_s"] + [e["peak_mb"], e["iterations"], e["nodes"], e["edges"]])
    a = bm["revised"]["main"]["awp"]
    add("rev: benchmark AWP", R, "benchmark/benchmark.json : main.awp", [a["mean_s"], a["sd_s"]])
    add("rev: AWP/ER runtime ratio", R, "benchmark/benchmark.json : main.awp.mean_s / main.endorserank.mean_s",
        [bm["revised"]["derived"]["time_ratio_awp_over_er"]])
    kp = sy["revised"]["key_points"]["p99"]
    add("rev: Sybil farm for p99", R, "sybil-model/sybil_model.json : farm_size_to_reach_cohort_quantile.p99.farm_addresses",
        [kp["farm_addresses"]])
    curve99 = next(pt for pt in sy["revised"]["curve"] if abs(pt[0] - 99) < 1e-9)
    add("rev: Sybil curve at q=99", R, "sybil-model/sybil_model.json : farm_size_to_reach_cohort_quantile.p99.farm_addresses",
        [curve99[2]])
    add("rev: constants b_A", R, "describe/describe.json : constants.b_allowance", [deck["params"]["value"]["b_A"]])
    add("rev: cap U", R, "describe/describe.json : constants.cap_allowance_usd", [deck["params"]["cap"]["U_usd"]])
    add("rev: cohort outside allowance graph (flags)", R, "same-window/eval_summary.json : graph.cohort_outside_allowance",
        [deck["contracts"]["flag_counts"]["outside_allowance"]])
    add("rev: cohort outside both graphs (flags)", R, "same-window/eval_summary.json : graph.cohort_outside_both",
        [deck["contracts"]["flag_counts"]["outside_both"]])
    weth = next(t for t in pr["tokens"] if t["symbol"] == "WETH")
    add("rev: WETH price days", R, "describe/describe.json : prices[28]", [weth["days"]])
    add("rev: W0 spenders", R, "holdout-w0/eval_summary.json : spenders", [scale["revised"]["w0"]["spenders"]])
    # registered
    rsw = res["registered"]["same_window"]
    add("reg: matched cohort", Rg, "cohort/matched_cohort.json : cohort", [scale["registered"]["cohort"]])
    add("reg: ER allowance family", Rg, "same-window/eval_summary.json : families.endorserank.allowance",
        rsw["families"]["endorserank"]["allowance"])
    f3 = res["verdicts"]["registered"]["rule_b"]["F"]["F3"]
    add("reg: rule B F3", Rg, "registered-w1/eval_summary.json : rule_b.F3", f3["d"] + [f3["ta"], f3["tb"]])
    add("reg: R1", Rg, "registered-w1/eval_summary.json : neutral_rules.R1", res["verdicts"]["registered"]["R1"])
    add("reg: benchmark AWP", Rg, "benchmark/benchmark.json : main.awp",
        [bm["registered"]["main"]["awp"]["mean_s"], bm["registered"]["main"]["awp"]["sd_s"]])
    add("reg: Sybil farm for p100", Rg, "sybil-model/sybil_model.json : farm_size_to_reach_cohort_quantile.p100.farm_addresses",
        [sy["registered"]["key_points"]["p100"]["farm_addresses"]])

    # recomputed from parquet (shows the parquet files are the inputs of the digest values)
    try:
        from scipy.stats import kendalltau
        s0 = c.pq(c.proc_rev / "holdout-w0", "spender_scores")
        s1 = c.pq(c.proc_rev / "window-w1", "spender_scores")
        t1 = c.pq(c.proc_rev / "window-w1", "trader_scores")
        cs = c.pq(c.proc_rev / "same-window", "cohort_scores")
        rec = [
            ("parquet: W0 ER vs new pairs", "holdout-w0/eval_summary.json : taus.endorserank.future_new_approvers",
             kendalltau(s0["endorserank"], s0["future_new_approvers"], variant="b")[0]),
            ("parquet: W1 in-approve degree vs new pairs", "window-w1/eval_summary.json : spender_taus.in_approve_degree.future_new_approvers",
             kendalltau(s1["in_approve_degree"], s1["future_new_approvers"], variant="b")[0]),
            ("parquet: W1 traders C-PR(λ=0) vs liquidation-free rate", "window-w1/eval_summary.json : trader_taus.cpr_l0",
             kendalltau(t1["cpr_l0"], t1["liquidation_free_rate"], variant="b")[0]),
            ("parquet: same-window ER vs in-approve degree", "same-window/eval_summary.json : per_proxy.endorserank.in_approve_degree",
             kendalltau(cs["endorserank"], cs["in_approve_degree"], variant="b")[0]),
        ]
        for name, src, tau in rec:
            add(name, R, src, [tau])
    except ImportError:
        checks.append(("parquet recomputation", "scipy not installed", None, True))

    w = max(len(x[0]) for x in checks)
    print("\nVerification against the results digests (revised-usd-12m/results_digest.md = rev, results_digest.md = reg):")
    print(f"{'check':<{w}}  {'ok':<4} digest value  ||  deck value")
    for name, dv, ov, ok in checks:
        ovs = ov if isinstance(ov, bool) else ", ".join(
            "None" if v is None else (f"{v:.6g}" if isinstance(v, float) else str(v)) for v in (ov or []))
        print(f"{name:<{w}}  {'OK' if ok else 'FAIL':<4} {dv}  ||  {ovs}")
    n_ok = sum(1 for x in checks if x[3])
    print(f"\n{n_ok}/{len(checks)} checks passed")
    return n_ok == len(checks)


# ----------------------------------------------------------------------------- main

def write_js(out: Path, key: str, obj, sources):
    out.mkdir(parents=True, exist_ok=True)
    body = json.dumps(clean(obj), ensure_ascii=True, separators=(",", ":"), allow_nan=False)
    head = ("/* Generated by dissertation/presentation/tools/build_data.py -- do not edit by hand.\n"
            "   Sources (relative to phd_works): " + "; ".join(sorted(set(sources)))[:3000].replace("*/", "* /") + " */\n")
    p = out / f"{key}.js"
    p.write_text(head + "window.DECK_DATA = window.DECK_DATA || {};\nwindow.DECK_DATA." + key + " = " + body + ";\n",
                 encoding="utf-8")
    return p


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("phd_works", nargs="?", help="root of the phd_works repository (default: $PHD_WORKS or derived from this file)")
    ap.add_argument("--out", help="output folder (default: ../data next to this script)")
    ap.add_argument("--no-verify", action="store_true", help="skip the comparison with the digests")
    args = ap.parse_args(argv)
    here = Path(__file__).resolve()
    phd = Path(args.phd_works or os.environ.get("PHD_WORKS") or here.parents[5]).resolve()
    out = Path(args.out).resolve() if args.out else here.parent.parent / "data"
    c = Ctx(phd, out)
    import yaml
    cfg_path = c.exp / "config/contract_reputation.yaml"
    cfg = yaml.safe_load(c.use(cfg_path).read_text(encoding="utf-8"))
    digests = {"revised": parse_digest(c.use(c.pub_rev / "results_digest.md")),
               "registered": parse_digest(c.use(c.pub / "results_digest.md"))}

    built = {}

    def run(key, fn, *a):
        c.current = set()
        obj = fn(*a)
        built[key] = (obj, sorted(c.current))
        print(f"built {key}")
        return obj

    run("contracts", build_contracts, c)
    run("prices", build_prices, c)
    run("timeline", build_timeline, c, digests)
    run("scale", build_scale, c)
    run("results", build_results, c)
    run("sybil", build_sybil, c, cfg)
    run("benchmark", build_benchmark, c)
    run("params", build_params, c, cfg)
    run("traders", build_traders, c)
    run("holdout", build_holdout, c)

    files = {}
    for key, (obj, srcs) in built.items():
        p = write_js(out, key, obj, srcs)
        files[key] = p
    meta = {
        "title": {"ko": "ERC-20 허락 화살표를 페이지랭크에 넣어 온체인 지갑 평판 점수를 더 좋게 만들기",
                  "en": "Integrating ERC-20 Allowance Edges into PageRank for Enhanced On-Chain Wallet Reputation Scoring"},
        "author": {"en": "Taehong Kwon", "ko": "권태홍"},
        "supervisor": "Prof. Ernest Mnkandla",
        "co_supervisors": ["Prof. Donatien Koulla Moulla", "Dr. David Sena Attipoe"],
        "university": "University of South Africa", "date": {"en": "October 2026", "ko": "2026년 10월"},
        "scope": {"en": NOTES["contracts_only"], "ko": NOTES["contracts_only_ko"]},
        "analyses": {"revised": {"en": "Revised analysis (main)", "ko": "수정 분석(주 결과)", "note": NOTES["revised"],
                                 "note_ko": NOTES["revised_ko"]},
                     "registered": {"en": "Registered analysis", "ko": "등록 분석", "note": NOTES["registered"],
                                    "note_ko": NOTES["registered_ko"]}},
        "methods": method_labels(),
        "notes": NOTES,
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "generator": "dissertation/presentation/tools/build_data.py",
        "phd_works_layout": str(PROJECT_REL.as_posix()),
        "digests_written_utc": {k: v["written_utc"] for k, v in digests.items()},
        "files": {k: {"file": f"data/{k}.js", "bytes": p.stat().st_size} for k, p in files.items()},
        "sources": [{"path": rel, "sha256": sha256(p), "bytes": p.stat().st_size}
                    for rel, p in sorted(c.sources.items()) if p.is_file()],
    }
    p = write_js(out, "meta", meta, ["see meta.sources"])
    files["meta"] = p
    total = sum(f.stat().st_size for f in files.values())
    print("\nfiles:")
    for k, f in files.items():
        print(f"  {f.name:<16} {f.stat().st_size / 1024:9.1f} KB")
    print(f"  {'total':<16} {total / 1024:9.1f} KB")
    if args.no_verify:
        return 0
    return 0 if verify(c, digests) else 1


if __name__ == "__main__":
    sys.exit(main())
