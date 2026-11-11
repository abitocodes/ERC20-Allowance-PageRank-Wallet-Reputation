#!/usr/bin/env python3
"""Build the data files of the thesis slide deck (dissertation/presentation/data/*.js).

Every number the slides show is read here from the experiment outputs of the study and written
into classic scripts that assign into ``window.DECK_DATA``, so the deck works when index.html is
opened by double-click (file://) as well as over http, without fetch() or ES modules.

Usage
-----
    python3 build_data.py [REPO] [--out DIR] [--no-verify]

``REPO`` is the root of a checkout of the public repository
https://github.com/abitocodes/ERC20-Allowance-PageRank-Wallet-Reputation (the folder that holds
``experiments/``), with its history. A checkout of the authors' private repository, which holds the
public one as the submodule ``1-Dissertation-Works/ERC20-Allowance-PageRank-Wallet-Reputation``,
also works. ``REPO`` is taken, in this order, from the positional argument, from the environment
variable ``CONTRACT_REP_REPO`` (or ``PHD_WORKS``), or from the location of this script
(``<REPO>/dissertation/presentation/tools/build_data.py``). ``--out`` defaults to ``../data`` next
to this script.

Sources (all under ``<REPO>/``)
-------------------------------
- ``experiments/data/3-published-results-for-thesis/revised-contract-12m/``: summaries of the
  contract-graph analysis (the thesis's main analysis; "revised" in the data keys) and its
  ``results_digest.md``: same window, W0, W1, the four runs of the discovery-order test and the
  structure pilot, Sybil model, robustness, benchmark, supplementary contrasts, data description,
  cohorts, account types, and the copies of the token list, the token-selection inputs and the
  constants (``usd/``);
- ``experiments/data/3-published-results-for-thesis/``: summaries of the registered analysis and
  its ``results_digest.md``;
- ``experiments/data/2-processed-tables-and-evaluations/revised-contract-12m/``: per-contract scores
  (``same-window/cohort_scores.part*.parquet``, ``holdout-w0`` and ``window-w1``
  ``spender_scores``) and the registered cohort scores;
- ``experiments/data/0-usd-token-list-and-prices/daily_prices_usd.csv``: daily USD closes;
- ``experiments/data/bq_ledger.json`` and ``experiments/config/contract_reputation.yaml``;
- ``git -C <REPO> show`` for the commit times of d060f3a and 1747e64, the plan and the W1
  registration in the public repository (43d8045 and 0d3a057 in the authors' repository; the
  public history keeps their times and contents, and its HISTORY.md maps the identifiers). The deck
  does not date the definitions of the contract-graph analysis or of the discovery-order test (the
  thesis says only that they were defined after the registered results were known).

The wallet-inclusive analyses (``revised-usd-12m/``, ``revised-usd/``) are not read.

Nothing is fitted or re-estimated. A few quantities are *derived* from the per-contract parquet
files (percentile ranks, decile bins of the holdout labels, the Sybil cost curve through the
closed form of ``experiments/scripts/sybil_model.py``, an eight-contract Kendall illustration) or
thinned from the published curves of the discovery-order test; each of them carries
``derived: true`` and a note in its ``meta``. No address of any contract or account is written.

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

# The public repository as a submodule of the authors' private repository.
PROJECT_REL = Path("1-Dissertation-Works/ERC20-Allowance-PageRank-Wallet-Reputation")
VARIANT = "revised-contract-12m"
# Commits of the public repository; ORIGINAL gives the identifiers of the authors' repository,
# which the extraction manifest and describe.json record.
COMMITS = {
    "d060f3a": "Analysis plan and configuration fixed before this study extracted any log",
    "1747e64": "W1 registration, extraction and evaluation code committed before scan B",
}
COMMITS_KO = {
    "d060f3a": "분석 계획과 설정 고정(이 연구의 로그 추출 전)",
    "1747e64": "W1 등록 문서와 추출·평가 코드 커밋(2차 추출 전)",
}
ORIGINAL = {"d060f3a": "43d8045", "1747e64": "0d3a057"}

METHODS = [
    # key, English, Korean (glossary), short, edges walked, restarts
    ("endorserank", "EndorseRank", "엔도스랭크", "ER", "allowance edges between contracts", "uniform over contracts"),
    ("endorserank_activity", "EndorseRank (activity restarts)", "엔도스랭크(활동 재시작)", "ER-act",
     "allowance edges between contracts", "approving activity of owner contracts"),
    ("awp", "AWP", "AWP(적응형 가중 페이지랭크)", "AWP", "transfer edges between contracts",
     "sending activity of contracts"),
    ("cpr_l0", "C-PR (λ=0)", "C-PR (λ=0, 송금 층만 걷기)", "λ=0", "transfer layer alone (USD amounts)", "uniform"),
    ("cpr_l25", "C-PR (λ=0.25)", "C-PR (λ=0.25)", "λ=0.25", "both layers", "uniform"),
    ("cpr_l50", "C-PR (λ=0.5)", "C-PR (λ=0.5, 주 설정)", "λ=0.5", "both layers", "uniform"),
    ("cpr_l75", "C-PR (λ=0.75)", "C-PR (λ=0.75)", "λ=0.75", "both layers", "uniform"),
    ("cpr_l100", "C-PR (λ=1)", "C-PR (λ=1, 허락 층만 걷기)", "λ=1",
     "allowance layer alone (balance-capped USD, capped at U)", "uniform"),
    ("spr", "S-PR", "S-PR(보증 씨앗 페이지랭크)", "S-PR", "transfer layer", "C-PR (λ=1) scores as seeds"),
    ("in_approve_degree", "In-approve degree", "받은 허락 수(허락 입차수)", "deg-A", "none (raw count of owner contracts)", "none"),
    ("in_approve_value", "In-approve value", "받은 허락 금액", "val-A", "none (capped USD from owner contracts)", "none"),
    ("in_degree", "Transfer in-degree", "송금 입차수", "deg-T", "none (raw count of sending contracts)", "none"),
    ("in_degree_union", "Union in-degree", "합집합 입차수", "deg-U",
     "none (distinct contracts with an edge in either layer)", "none"),
]
SCORE_COLS = ["endorserank", "endorserank_activity", "awp", "cpr_l0", "cpr_l25", "cpr_l50", "cpr_l75",
              "cpr_l100", "spr"]
LAMBDA_KEYS = ["cpr_l0", "cpr_l25", "cpr_l50", "cpr_l75", "cpr_l100"]
LAMBDAS = [0, 0.25, 0.5, 0.75, 1]
PROXIES = [
    ("in_degree", "transfer", "Transfer in-degree", "송금 입차수(보내온 서로 다른 계약 수)"),
    ("in_value", "transfer", "In-value (USD)", "받은 송금액 합(달러)"),
    ("in_approve_degree", "allowance", "In-approve degree", "받은 허락 수(허락한 서로 다른 주인 계약 수)"),
    ("in_approve_value", "allowance", "In-approve value (balance-capped USD, capped at U)", "받은 허락 금액 합(달러, 잔액 상한, 상한 U)"),
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
# Orderings and references of the discovery-order test (the prime marks what is computed on the
# contracts read so far).
ORDERINGS = [
    ("bfs", "BFS (breadth-first)", "너비 우선(BFS)"),
    ("random", "Random", "무작위"),
    ("ib_a", "IB′_A (allowance backlinks)", "IB′_A(허락 역링크 수)"),
    ("ib_t", "IB′_T (transfer backlinks)", "IB′_T(송금 역링크 수)"),
    ("ib_u", "IB′_U (contract backlinks)", "IB′_U(계약 역링크 수)"),
    ("endorserank", "EndorseRank′", "엔도스랭크′"),
    ("endorserank_activity", "EndorseRank-activity′", "엔도스랭크′(활동 재시작)"),
    ("awp", "AWP′", "AWP′"),
    ("cpr_l50", "C-PR′ (λ=0.5)", "C-PR′ (λ=0.5)"),
    ("cpr_l25", "C-PR′ (λ=0.25)", "C-PR′ (λ=0.25)"),
    ("cpr_l75", "C-PR′ (λ=0.75)", "C-PR′ (λ=0.75)"),
    ("cpr_l100", "C-PR′ (λ=1)", "C-PR′ (λ=1)"),
    ("cpr_l0", "C-PR′ (λ=0)", "C-PR′ (λ=0)"),
    ("spr", "S-PR′", "S-PR′"),
    ("delta", "δ′ (diagnostic)", "δ′(진단용)"),
    ("ref_cpr", "Reference: C-PR of the full graph", "기준: 전체 그래프의 C-PR"),
    ("ref_ib_u", "Reference: union in-degree of the full graph", "기준: 전체 그래프의 합집합 입차수"),
    ("ref_ideal", "Reference: ideal order", "기준: 이상적인 순서"),
    ("random_curve", "Reference: random curve K/|U|", "기준: 무작위 곡선 K/|U|"),
    ("ideal_curve", "Reference: ideal curve min(1, K/|H|)", "기준: 이상 곡선 min(1, K/|H|)"),
]
IMPORTANCES = {
    "i_t": ("I_T: user-account inflow (USD that user accounts transferred to the contract, capped per account at U_user)",
            "I_T: 사용자 계정 유입(사용자 계정이 그 계약에 보낸 달러, 계정마다 U_user까지)"),
    "i_a": ("I_A: user-authorised value (balance-capped USD that user accounts authorised the contract to spend, capped per account)",
            "I_A: 사용자 허락 금액(사용자 계정이 그 계약에 허락한 달러, 잔액 상한, 계정마다 상한)"),
    "n_t": ("N_T: user accounts that transferred at least USD 1 in total to the contract", "N_T: 그 계약에 모두 1달러 이상 보낸 사용자 계정 수"),
    "n_a": ("N_A: user accounts whose capped allowance to the contract is at least USD 1", "N_A: 그 계약에 상한 씌운 허락이 1달러 이상인 사용자 계정 수"),
    "ib_u": ("IB_U: union in-degree of the full graph (backlink importance; intended-construct check)",
             "IB_U: 전체 그래프의 합집합 입차수(역링크 중요도, 의도한 구성개념 점검)"),
    "ir": ("IR: C-PR of the full graph (PageRank importance; intended-construct check)",
           "IR: 전체 그래프의 C-PR(페이지랭크 중요도, 의도한 구성개념 점검)"),
}
CURVE_KEY_ORDERINGS = ["bfs", "random", "ib_u", "cpr_l50", "awp"]
NOTES = {
    "revised": ("Contract-graph analysis = the thesis's main analysis ('revised' in the data keys). After the "
                "registered results were known, the revised analysis was defined: amounts in US dollars on five "
                "tokens (WETH, USDC, USDT0, ARB, WBTC); scores from the twelve months before each freeze; graphs "
                "whose nodes are contracts other than smart accounts, with edges read from the whole chain; each "
                "allowance counted up to its owner's balance at the freeze, with balances reconstructed from "
                "Transfer logs; constants set on the contract graph; and the discovery-order test. None of its "
                "results is a registered result; rules A and B are applied to its scores as a re-analysis."),
    "revised_ko": ("계약 그래프 분석 = 논문의 주 분석이에요(데이터 키에서는 'revised'). 등록 분석의 결과를 안 뒤에 수정 "
                   "분석을 정했어요. 금액은 다섯 토큰(WETH, USDC, USDT0, ARB, WBTC)의 달러 금액이고, 점수는 각 동결 직전 "
                   "12개월의 사건으로 만들어요. 그래프의 점은 스마트 계정이 아닌 계약이고, 화살표는 체인 전체에서 읽어요. "
                   "허락은 동결 시점 주인의 잔액까지만 세고, 잔액은 Transfer 로그로 다시 계산해요. 상수는 계약 그래프 "
                   "위에서 정했어요. 발견 순서 검증도 이렇게 정한 것에 들어요. 주 분석의 결과는 등록된 결과가 아니에요. "
                   "규칙 A와 B는 계약 그래프의 점수에 적용한 재분석이에요."),
    "registered": ("Registered analysis: raw base units, every ERC-20 token, b = 1, scores from every event since "
                   "1 October 2023, graphs that hold every account of the cohort's events. Rule A was fixed in the "
                   "analysis plan (d060f3a) before this study extracted any log; rule B in the W1 registration "
                   "(1747e64) before scan B."),
    "registered_ko": ("등록 분석: 원래 단위, 모든 ERC-20 토큰, b = 1, 2023년 10월 1일부터의 모든 사건으로 만든 점수, 코호트 "
                      "사건의 모든 계정이 든 그래프예요. 규칙 A는 이 연구가 로그를 추출하기 전의 분석 계획(d060f3a)에서, "
                      "규칙 B는 2차 추출 전의 W1 등록(1747e64)에서 정했어요."),
    "rule_b": ("The thesis applies two of rule B's registered criteria, F1 and F2; under the registration the rule "
               "holds only if each of its criteria holds."),
    "rule_b_ko": ("이 논문은 규칙 B의 등록된 기준 가운데 두 가지, F1과 F2를 적용해요. 등록 문서에 따르면 규칙 B는 자기 "
                  "기준이 하나하나 모두 설 때만 충족돼요."),
    "discovery": ("The discovery-order test (the crawl-ordering experiment of Cho, Garcia-Molina and Page, 1998, on "
                  "the contract graph) was defined after the registered results were known and decides no rule of "
                  "the plan or the registration. Its decision is read at the T_obs freeze in the primary reveal mode "
                  "(both) only; the other three runs carry no verdict. Importance is user-account demand, which no "
                  "ordering reads."),
    "discovery_ko": ("발견 순서 검증(Cho, Garcia-Molina, Page 1998의 크롤 순서 실험을 계약 그래프에서 다시 한 것)은 등록 "
                     "분석의 결과를 안 뒤에 정했고, 계획과 등록 문서의 어떤 규칙도 정하지 않아요. 판정은 T_obs 동결의 주 "
                     "공개 방식(both)에서만 읽고, 나머지 세 실행에는 판정이 없어요. 중요도는 어떤 순서 규칙도 읽지 않는 "
                     "사용자 계정의 수요예요."),
    "same_window": ("Same-window agreement with the families is an intended-construct check: part of it is "
                    "built in, and it is not validation or evidence of predictive power."),
    "same_window_ko": "같은 기간 일치도는 의도한 구성개념 점검이에요. 일부는 만든 방식 때문에 저절로 생기고, 검증이 아니에요.",
    "post_hoc": "Computed after the labels were known; no rule fixed it in advance (post hoc).",
    "post_hoc_ko": "라벨을 본 뒤 계산했어요(사후). 미리 정한 규칙이 아니에요.",
    "raw_degree": ("On new approval pairs the in-approve degree on the contract graph ranks spenders above "
                   "EndorseRank in both windows (post hoc contrasts)."),
    "raw_degree_ko": "새 허락 쌍에서는 계약 그래프의 받은 허락 수가 엔도스랭크보다 잘 맞혔어요(두 기간 모두, 사후 대비).",
    "labels": ("The out-of-window labels count every account, user accounts included, while no score or baseline "
               "reads a user account; a member outside the contract graph scores zero under every score and baseline."),
    "labels_ko": ("기간 밖 라벨은 사용자 계정을 포함한 모든 계정을 세지만, 어떤 점수와 기준선도 사용자 계정을 읽지 않아요. "
                  "계약 그래프 밖의 구성원은 모든 점수와 기준선에서 0점이에요."),
    "speed": ("Same solver for every score: runtime differences follow from the size of each graph and the "
              "iterations its walk needs there (the time ratio does not follow the edge ratio), not from the "
              "algorithm."),
    "speed_ko": ("모든 점수가 같은 풀이 프로그램을 써요. 시간 차이는 그래프의 크기와 그 그래프에서 걷기가 되풀이해야 하는 "
                 "반복 수에서 와요(시간 비는 화살표 수의 비를 따르지 않아요). 알고리즘의 기여가 아니에요."),
    "contracts_only": ("Every node of every graph is a contract. User accounts (EOAs, EIP-7702 accounts and smart "
                       "accounts: Safes and ERC-4337 accounts) are in no graph; they enter only the importance "
                       "measures of the discovery-order test and the out-of-window labels."),
    "contracts_only_ko": ("모든 그래프의 점은 계약이에요. 사용자 계정(EOA, EIP-7702 계정, 스마트 계정: Safe와 ERC-4337 계정)은 "
                          "어떤 그래프에도 없고, 발견 순서 검증의 중요도와 기간 밖 라벨에만 들어가요."),
}
# Keys of the registered summaries that belong to outcomes the deck does not show.
DROP_KEYS = {"traders", "trader_taus", "traders_n", "traders_liquidated", "traders_all_liquidated",
             "neutral_w0", "neutral_w1", "neutral_rules", "F3", "F4", "F5", "decision",
             "provenance", "gmx_contract_traders_by_quarter"}
DROP_SUFFIX = ("_liq",)


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


def strip(o):
    """Drop the keys of DROP_KEYS (and *_liq) at every depth."""
    if isinstance(o, dict):
        return {k: strip(v) for k, v in o.items() if k not in DROP_KEYS and not k.endswith(DROP_SUFFIX)}
    if isinstance(o, list):
        return [strip(v) for v in o]
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


def ordering_labels():
    return {k: {"en": en, "ko": ko} for k, en, ko in ORDERINGS}


# ----------------------------------------------------------------------------- context

class Ctx:
    def __init__(self, phd: Path, out: Path):
        if not (phd / "experiments").is_dir() and (phd / PROJECT_REL / "experiments").is_dir():
            phd = phd / PROJECT_REL  # a checkout of the authors' repository: use its public submodule
        self.phd = phd
        self.proj = phd
        self.exp = self.proj / "experiments"
        self.data = self.exp / "data"
        self.pub = self.data / "3-published-results-for-thesis"
        self.pub_rev = self.pub / VARIANT
        self.proc = self.data / "2-processed-tables-and-evaluations"
        self.proc_rev = self.proc / VARIANT
        self.usd = self.data / "0-usd-token-list-and-prices"
        self.usd_rev = self.pub_rev / "usd"
        self.out = out
        self.sources: dict[str, Path] = {}
        self.current: set[str] = set()
        needed = [self.pub_rev / "results_digest.md", self.pub / "results_digest.md", self.proc_rev,
                  self.usd / "daily_prices_usd.csv"]
        needed += [self.pub_rev / f for f in (
            "same-window/eval_summary.json", "holdout-w0/eval_summary.json", "window-w1/eval_summary.json",
            "supplementary/supplementary.json", "robustness/robustness.json", "sybil-model/sybil_model.json",
            "benchmark/benchmark.json", "describe/describe.json", "cohort/matched_cohort.json",
            "cohort/cohort_t1.json", "cohort/spenders_w0.json", "cohort/spenders_w1.json",
            "discovery/discovery_tobs_both.json", "discovery/discovery_tobs_out.json",
            "discovery/discovery_t1_both.json", "discovery/discovery_t1_out.json", "discovery/feasibility_t1.json",
            "usd/constants.json", "usd/usd_inputs.json", "usd/listed_tokens.csv")]
        for sub, stem in (("same-window", "cohort_scores"), ("holdout-w0", "spender_scores"),
                          ("window-w1", "spender_scores")):
            if not list((self.proc_rev / sub).glob(f"{stem}.part*.parquet")):
                needed.append(self.proc_rev / sub / f"{stem}.part*.parquet")
        missing = [p for p in needed if "*" in p.name or not p.exists()]
        if missing:
            raise SystemExit("missing sources (the deck is not built from any other analysis):\n  "
                             + "\n  ".join(str(p) for p in missing))

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
                             capture_output=True, text=True, encoding="utf-8", errors="replace", check=True,
                             timeout=30).stdout.strip()
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


def ascii_symbol(sym: str) -> str:
    return "USDT0" if sym not in ("WETH", "USDC", "ARB", "WBTC") else sym


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
    in_union = [int(bool(v)) for v in df["in_union_graph"]]
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
            "analysis": "revised (contract-graph analysis)",
            "source": c.rel(c.proc_rev / "same-window") + "/cohort_scores.part*.parquet",
            "order": "rows sorted by node id (the same index in every array)",
            "pct": ("mid-rank percentile in [0, 1] = (average rank - 1)/(n - 1), 4 decimals; tied values "
                    "(e.g. the zero scores of contracts outside a graph) share one position"),
            "raw": ("raw integer counts at T_obs on the contract graph (in_approve_degree: distinct owner contracts "
                    "with a positive capped allowance; in_degree: distinct sending contracts)"),
            "log10": "log10 of the raw score, 3 decimals; null where the score is 0",
            "flags": "bit 0 (1) = outside the allowance graph (C-PR λ=1 score 0); bit 1 (2) = outside the transfer "
                     "graph (C-PR λ=0 score 0); 3 = outside both",
            "in_union": "1 = the contract lies in the union graph of the two layers; 0 = outside the contract graph",
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
        "in_union": in_union,
        "zeros": zeros,
        "flag_counts": {"outside_allowance": int(outside_allow.sum()), "outside_transfer": int(outside_transfer.sum()),
                        "outside_both": int((outside_allow & outside_transfer).sum()),
                        "in_union_graph": int(sum(in_union))},
        "rank_size": rank_size,
        "top10": top,
    }


def build_prices(c: Ctx):
    tok = pd.read_csv(c.use(c.usd_rev / "listed_tokens.csv"))
    sel = tok[tok["selected"]].sort_values("rank_by_n")
    pr = pd.read_csv(c.use(c.usd / "daily_prices_usd.csv"))
    desc = c.j(c.pub_rev / "describe/describe.json")
    pdays = {t["address"].lower(): t for t in desc["price_days"]["per_token"]}
    days = pd.date_range("2023-10-01", "2026-09-30", freq="D")
    day_s = [d.strftime("%Y-%m-%d") for d in days]
    w_from, w_to = desc["price_days"]["first_day"], desc["price_days"]["last_day"]
    close, keys, tokens = {}, {}, []
    for _, t in sel.iterrows():
        sym = t["symbol"]
        a_sym = ascii_symbol(sym)
        p = pr[pr["address"] == t["address"]].set_index("day").reindex(day_s)
        close[a_sym] = [sig(v) if pd.notna(v) else None for v in p["price_usd"]]
        segs, prev, start = [], None, 0
        for i, k in enumerate(p["key"].fillna("none")):
            if k != prev:
                if prev is not None:
                    segs.append([start, i - 1, prev])
                prev, start = k, i
        segs.append([start, len(day_s) - 1, prev])
        keys[a_sym] = segs
        in_win = p.loc[w_from:w_to, "price_usd"]
        pd_ = pdays.get(t["address"].lower(), {})
        tokens.append({
            "symbol": a_sym, "symbol_display": sym, "decimals": int(t["decimals"]),
            "feed": t["feed"], "feed_category": t["feed_category"], "relation": t["relation"],
            "rows_tobs": int(t["n_rows_tobs"]), "rank_by_rows": int(t["rank_by_n"]),
            "days": int(p["price_usd"].notna().sum()), "filled_days": int(t["filled_days"]),
            "spike_days": int(t["spike_days"]), "arbitrum_key_first_day": t["arbitrum_key_first_day"],
            "second_key_days_used": int(t["second_key_days_used"]),
            "days_main_window": int(in_win.notna().sum()),
            "main_window_published": {"days": pd_.get("days"), "second_key_days": pd_.get("second_key_days"),
                                      "filled_days": pd_.get("filled_days"), "spike_days": pd_.get("spike_days")},
            "first": close[a_sym][0], "last_obs": close[a_sym][day_s.index("2026-06-30")],
            "min": sig(np.nanmin(p["price_usd"])), "max": sig(np.nanmax(p["price_usd"])),
        })
    return {
        "meta": {
            "source": (c.rel(c.usd / "daily_prices_usd.csv") + ", " + c.rel(c.usd_rev / "listed_tokens.csv") + ", "
                       + c.rel(c.pub_rev / "describe/describe.json") + " : price_days"),
            "unit": "USD daily close (DefiLlama coins API, point nearest 00:00 UTC of the next day)",
            "rounding": "4 significant digits",
            "key_segments": ("[first_day_index, last_day_index, key]; key 'arbitrum' = series under the token's "
                             "Arbitrum address, 'second' = filled from the same asset's CoinGecko series"),
            "main_window": ("the days the main analysis prices (first day of the W0 score window to the end of W1): "
                            "days_main_window counts them in the series, main_window_published gives describe.json"),
            "windows": {"main_analysis": [w_from, w_to], "observation": ["2023-10-01", "2026-06-30"],
                        "W1_labels": ["2026-07-01", "2026-09-30"]},
        },
        "start": day_s[0], "end": day_s[-1], "days": len(day_s),
        "index": {"t1": day_s.index("2026-03-31"), "t_obs": day_s.index("2026-06-30"),
                  "main_window": [day_s.index(w_from), day_s.index(w_to)],
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
    fallback = {"d060f3a": reg_desc["timing"].get("plan_commit_43d8045_utc"),
                "1747e64": reg_desc["timing"].get("registration_commit_0d3a057_utc")}
    for short, what in COMMITS.items():
        g = git_commit(c.phd, short)
        if g is None:
            g = {"short": short, "utc": zulu(fallback[short]) if fallback.get(short) else None,
                 "source": "describe.json timing (git unavailable)"}
        else:
            g["source"] = "git -C <REPO> show (public repository)"
        g["original"] = ORIGINAL[short]
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
    gaps = {"plan_commit_to_scan_a_created_s": gap(cm["d060f3a"], ev["scan_a_created"]),
            "registration_commit_to_w1_extraction_start_s": gap(cm["1747e64"], ev["w1_extraction_started"]),
            "registration_commit_to_scan_b_created_s": gap(cm["1747e64"], ev["scan_b_created"])}
    # the ledger is summarised only: its job labels name outcomes the deck does not show
    # (and its times would date the definitions of the contract-graph analysis, which the deck does not do)
    jobs = {"jobs": len(ledger["jobs"]), "usd": round(sum(j.get("usd") or 0 for j in ledger["jobs"]), 2)}
    monthly = {}
    streams = {}
    for row in reg_desc["monthly_counts"]:
        streams.setdefault(row["stream"], []).append([row["month"], int(row["n"])])
    monthly["registered"] = streams
    t = rev_desc["timing"]
    return {
        "meta": {
            "note": ("Times in UTC. Ledger times are written when a BigQuery job finished. Commit times from "
                     "git; scan times from the registered describe.json timing block; gaps in seconds below. "
                     "No time of the definitions of the contract-graph analysis or of the discovery-order test "
                     "is given."),
            "monthly_counts": ("registered only: ego approvals and transfers per month of scan A (all tokens). The "
                               "contract-graph analysis reads the whole chain over its windows and publishes no "
                               "monthly series."),
            "sources": [c.rel(c.pub / "describe/describe.json"), c.rel(c.pub_rev / "describe/describe.json"),
                        c.rel(c.pub / "registered-w1/extraction_manifest.json"), c.rel(c.data / "bq_ledger.json"),
                        c.rel(cfg_path), "git log of the public repository"],
        },
        "periods": [
            {"id": "extraction", "en": "Scan A (extracted logs of the registered analysis, which scores all of it)",
             "ko": "1차 추출(등록 분석이 뽑은 로그, 등록 분석은 이 기간 전부로 점수를 만듦)",
             "from": "2023-10-01T00:00:00Z", "to": "2026-06-30T23:59:59Z"},
            {"id": "contract_events", "en": "Events of the contract-graph analysis (whole chain, five tokens)",
             "ko": "계약 그래프 분석의 사건(체인 전체, 다섯 토큰)",
             "from": "2025-04-01T00:00:00Z", "to": "2026-09-30T23:59:59Z"},
            {"id": "observation", "en": "T_obs score window (twelve months)", "ko": "T_obs 점수 기간(12개월)",
             "from": "2025-07-01T00:00:00Z", "to": "2026-06-30T23:59:59Z",
             "use_en": "scores at T_obs, same-window checks, discovery-order test at T_obs, benchmark, robustness, W1 scores",
             "use_ko": "T_obs 점수, 같은 기간 점검, T_obs의 발견 순서 검증, 벤치마크, 강건성, W1 점수"},
            {"id": "w0_scores", "en": "W0 score window (twelve months before t1)", "ko": "W0 점수 기간(t1 전 12개월)",
             "from": "2025-04-01T00:00:00Z", "to": "2026-03-31T23:59:59Z"},
            {"id": "w0_labels", "en": "W0 labels", "ko": "W0 라벨 기간",
             "from": "2026-04-01T00:00:00Z", "to": "2026-06-30T23:59:59Z"},
            {"id": "w1_labels", "en": "W1 labels (extracted by this study only after the registration commit)",
             "ko": "W1 라벨 기간(이 연구는 등록 커밋 뒤에만 추출)", "from": "2026-07-01T00:00:00Z", "to": "2026-09-30T23:59:59Z"},
        ],
        "anchors": {"data_start": "2023-10-01T00:00:00Z", "t1": "2026-03-31T23:59:59Z",
                    "t_obs": "2026-06-30T23:59:59Z", "data_end": "2026-09-30T23:59:59Z",
                    "contract_events": ["2025-04-01T00:00:00Z", "2026-09-30T23:59:59Z"],
                    "score_window_tobs": ["2025-07-01T00:00:00Z", "2026-06-30T23:59:59Z"],
                    "score_window_t1": ["2025-04-01T00:00:00Z", "2026-03-31T23:59:59Z"],
                    "max_age_days_tobs": 365, "max_age_days_t1": 365,
                    "blocks": rev_desc["anchor_blocks"], "account_types_block": rev_desc["account_types"]["block"]},
        "commits": commits,
        "events": events,
        "gaps": gaps,
        "ledger": jobs,
        "bigquery": {"registered_usd": reg_desc["timing"]["bigquery_usd_total"],
                     "registered_tib": reg_desc["timing"]["bigquery_tib_billed"],
                     "total_usd": t["bigquery_usd_total"], "total_tib": t["bigquery_tib_billed"],
                     "analysis_jobs": t["contract12m_jobs"], "analysis_jobs_usd": t["contract12m_jobs_usd"],
                     "budget_usd": t["budget_usd"]},
        "monthly_counts": monthly,
    }


def members(j):
    return {k: j.get(k) for k in ("rule", "listed", "cohort", "by_class", "user_accounts_by_source")}


def build_scale(c: Ctx):
    out = {"meta": {"note": "Counts exactly as in the published summaries of both analyses.",
                    "revised_note": NOTES["revised"], "registered_note": NOTES["registered"],
                    "scope": NOTES["contracts_only"], "labels": NOTES["labels"]}}
    usd_inputs = c.j(c.usd_rev / "usd_inputs.json")
    tok = pd.read_csv(c.use(c.usd_rev / "listed_tokens.csv"))
    sel = tok[tok["selected"]].sort_values("rank_by_n")
    out["tokens"] = {
        "candidates": usd_inputs["candidates"], "listed": usd_inputs["listed"],
        "priced": usd_inputs["priced_tokens"], "selected": usd_inputs["top_n"],
        "listed_without_price": len(usd_inputs["listed_without_price"]),
        "selected_tokens": [{"symbol": ascii_symbol(r["symbol"]), "rows_selection": int(r["n_rows_tobs"]),
                             "feed": r["feed"], "feed_category": r["feed_category"]} for _, r in sel.iterrows()],
        "rows_note": "rows_selection: the rows by which the five tokens were ranked (listed_tokens.csv n_rows_tobs)",
        "funnel_en": ["Chainlink-mapped tokens", "low/medium market-risk feed", "with a daily price", "top five by rows"],
        "funnel_ko": ["체인링크가 대응시킨 토큰", "위험 등급 낮음·중간", "하루 가격이 있음", "행 수 상위 다섯"],
        "source": c.rel(c.usd_rev / "usd_inputs.json"),
    }
    # registered analysis (unchanged sources; outcomes the deck does not show are dropped)
    base = c.pub
    coh = c.j(base / "cohort/matched_cohort.json")
    sw = c.j(base / "same-window/eval_summary.json")
    h0 = c.j(base / "holdout-w0/eval_summary.json")
    w1 = c.j(base / "registered-w1/eval_summary.json")
    desc = c.j(base / "describe/describe.json")
    out["registered"] = {
        "cohort_rule": coh["rule"], "cohort": coh["cohort"],
        "candidates": coh.get("candidates"), "by_code_kind": coh.get("by_code_kind"),
        "graph_tobs": sw["graph"], "graph_t1": h0["graph"],
        "iterations_tobs": sw["iterations"], "iterations_t1": h0["iterations"],
        "w0": {"spenders": h0["spenders"], "spender_account_types": h0["spender_account_types"],
               "gained_new_approvals": h0["gained_new_approvals"], "gained_new_senders": h0["gained_new_senders"],
               "receiving_subset": h0["receiving"]["n"], "coverage": compact(h0["coverage"])},
        "w1": {"spenders": w1["spenders"], "gained_new_approvals": w1["gained_new_approvals"],
               "gained_new_senders": w1["gained_new_senders"]},
        "amounts": compact(desc["amounts"]),
        "sources": [c.rel(base / "cohort/matched_cohort.json"), c.rel(base / "same-window/eval_summary.json"),
                    c.rel(base / "holdout-w0/eval_summary.json"), c.rel(base / "registered-w1/eval_summary.json"),
                    c.rel(base / "describe/describe.json")],
    }
    # contract-graph analysis
    base = c.pub_rev
    coh = c.j(base / "cohort/matched_cohort.json")
    coh_t1 = c.j(base / "cohort/cohort_t1.json")
    sp0 = c.j(base / "cohort/spenders_w0.json")
    sp1 = c.j(base / "cohort/spenders_w1.json")
    sw = c.j(base / "same-window/eval_summary.json")
    h0 = c.j(base / "holdout-w0/eval_summary.json")
    w1 = c.j(base / "window-w1/eval_summary.json")
    desc = c.j(base / "describe/describe.json")
    al = desc["allowances"]

    def amounts(tot):
        n = tot["n_latest_positive"]
        return {"latest_allowances": n, "unlimited_allowances": tot["n_unlimited"],
                "unlimited_share": safe(tot["share_unlimited"]), "finite_allowances": tot["n_finite"],
                "allowances_at_or_above_cap": tot["n_allow_at_or_above_cap"],
                "allowances_at_or_above_cap_share": safe(tot["n_allow_at_or_above_cap"] / n),
                "capped_to_zero": tot["n_capped_to_zero"], "capped_to_zero_share": safe(tot["share_capped_to_zero"]),
                "capped_below_allowance": tot["n_capped_below_allowance"],
                "positive_after_cap": tot["n_positive_eff"],
                "capped_value_at_or_above_cap": tot["n_eff_at_or_above_cap"],
                "sum_capped_usd": sig(tot["sum_usd_eff"], 6)}
    amt = amounts(al["tobs"]["total"])
    amt["latest_allowances_tobs"] = amt["latest_allowances"]
    acc = desc["account_types"]
    ev = desc["events"]
    out["revised"] = {
        "cohort_rule": coh["rule"], "cohort": coh["cohort"], "listed": coh["listed"],
        "by_class": coh["by_class"], "user_accounts_by_source": coh["user_accounts_by_source"],
        "members": {"cohort_tobs": members(coh), "cohort_t1": members(coh_t1),
                    "spenders_w0": members(sp0), "spenders_w1": members(sp1)},
        "graph_tobs": sw["graph"], "graph_t1": h0["graph"],
        "union_graph_tobs": sw["union_graph"], "union_graph_t1": h0["union_graph"],
        "iterations_tobs": sw["iterations"], "iterations_t1": h0["iterations"],
        "cohort_coverage": {**compact(sw["cohort_coverage"]), **compact(h0["cohort_coverage"]),
                            **compact(w1["cohort_coverage"])},
        "w0": {"spenders": h0["spenders"], "spender_account_types": h0["spender_account_types"],
               "gained_new_approvals": h0["gained_new_approvals"], "gained_new_senders": h0["gained_new_senders"],
               "receiving_subset": h0["receiving"]["n"], "coverage": compact(h0["coverage"]),
               "in_union_graph": {"n": h0["in_union_graph"]["n"], "share": safe(h0["in_union_graph"]["share"])}},
        "w1": {"spenders": w1["spenders"], "spender_account_types": w1["spender_account_types"],
               "gained_new_approvals": w1["gained_new_approvals"], "gained_new_senders": w1["gained_new_senders"],
               "in_union_graph": {"n": w1["in_union_graph"]["n"], "share": safe(w1["in_union_graph"]["share"])}},
        "label_split": {"w0": compact(h0["label_split"]), "w1": compact(w1["label_split"]), "note": NOTES["labels"]},
        "events": ev,
        "account_types": {
            "transaction_senders": ev["transaction_senders"], "user_accounts": ev["user_accounts"],
            "contracts": ev["contracts"], "addresses_read": acc["addresses"], "block": acc["block"],
            "aborted_addresses": acc["aborted_addresses"], "audit_senders_with_code": acc["audit_senders_with_code"],
            "code_kind": acc["code_kind"], "typed": acc["typed"], "wallet_kind_typed": acc["wallet_kind_typed"],
            "extension": acc["extension"], "after_extension": acc["after_extension"],
            "wallet_kind_after_extension": acc["wallet_kind_after_extension"], "proxy_kind": acc["proxy_kind"],
            "note": ("user accounts = transaction senders, addresses without code, EIP-7702 accounts and smart "
                     "accounts (Safes, ERC-4337 accounts); every node of every graph is one of the contracts"),
        },
        "nodes": desc["nodes"],
        "pairs": desc["pairs"],
        "amounts": amt,
        "amounts_t1": amounts(al["t1"]["total"]),
        "amounts_per_token": {"tobs": [{**{k: v for k, v in r.items() if k != "token"}, "symbol": ascii_symbol(r["symbol"])}
                                       for r in al["tobs"]["per_token"]],
                              "t1": [{**{k: v for k, v in r.items() if k != "token"}, "symbol": ascii_symbol(r["symbol"])}
                                     for r in al["t1"]["per_token"]]},
        "amounts_note": ("latest positive allowances between contracts of the five tokens at the freeze; each counts "
                         "up to its owner's balance at the freeze (balance cap); capped_to_zero: the owner holds no "
                         "balance, so the allowance is no edge; *_at_or_above_cap counts against U"),
        "balance_check": desc["balance_check"],
        "importance": compact(desc["importance"]),
        "constants": {k: desc["constants"][k] for k in ("m_transfer_usd", "m_allowance_usd", "cap_allowance_usd",
                                                        "cap_user_usd", "b_transfer", "b_allowance", "window")},
        "chainlink_check": compact(desc["chainlink_check_in_windows"]),
        "contract_only": {k: v for k, v in sw["contract_only"].items() if k != "types"},
        "sources": [c.rel(base / "cohort/matched_cohort.json"), c.rel(base / "cohort/cohort_t1.json"),
                    c.rel(base / "cohort/spenders_w0.json"), c.rel(base / "cohort/spenders_w1.json"),
                    c.rel(base / "same-window/eval_summary.json"), c.rel(base / "holdout-w0/eval_summary.json"),
                    c.rel(base / "window-w1/eval_summary.json"), c.rel(base / "describe/describe.json")],
    }
    return out


def build_results(c: Ctx):
    res = {
        "meta": {
            "tau": "[τ_b, lo95, hi95] (per proxy: [τ_b, lo95, hi95, Spearman ρ]); family entries are family means",
            "contrast": "{d: [Δτ, lo95, hi95], ta: τ_a, tb: τ_b, p: P(Δτ>0), B} (+ d975 = Bonferroni 97.5% interval)",
            "B": "paired bootstrap over contracts, 400 resamples, seed 42",
            "notes": NOTES,
            "rounding": "4 significant digits, kept long enough that 1-4 decimal displays match the summaries",
            "baselines": ("raw counts on the contract graph: in-approve degree, in-approve value, transfer in-degree, "
                          "union in-degree (keys in_approve_value / in_degree_union; t1_* in W0)"),
        },
        "methods": method_labels(),
        "proxies": {k: {"family": f, "en": en, "ko": ko} for k, f, en, ko in PROXIES},
        "families": {k: {"en": en, "ko": ko} for k, (en, ko) in FAMILIES.items()},
        "spender_labels": {k: {"en": en, "ko": ko} for k, (en, ko) in SPENDER_LABELS.items()},
    }
    raw = {}
    for name, base, w1dir in (("revised", c.pub_rev, "window-w1"), ("registered", c.pub, "registered-w1")):
        sw = strip(c.j(base / "same-window/eval_summary.json"))
        h0 = strip(c.j(base / "holdout-w0/eval_summary.json"))
        w1_full = c.j(base / w1dir / "eval_summary.json")
        w1 = strip(w1_full)
        sup = strip(c.j(base / "supplementary/supplementary.json"))
        rob = strip(c.j(base / "robustness/robustness.json"))
        raw[name] = (sw, h0, w1, w1_full)
        status = {
            "same_window.families/per_proxy": "intended-construct check (not validation)",
            "same_window.contrasts": "post hoc (reported beside rule A secondary; do not decide it)",
            "same_window.rule_a_secondary": "rule A, secondary part" + (" (re-analysis)" if name == "revised" else " (registered, plan d060f3a)"),
            "w0.contrasts_prefixed": "rule A, primary part" + (" (re-analysis)" if name == "revised" else " (registered, plan d060f3a)"),
            "w0.contrasts_after": "post hoc",
            "w0.receiving": "post hoc restriction",
            "w1.rule_b": ("two of rule B's registered criteria, F1 and F2, applied as a re-analysis (F6 reported beside)"
                          if name == "revised" else "rule B, criteria F1 and F2 (registered, 1747e64)"),
            "w1.sensitivity_awp/isolated": "registered sensitivity analyses (spender parts), do not enter the decision",
            "w1.endorserank_results": "not registered; computed after the W1 labels were known",
            "supplementary": "post hoc, outside every rule",
            "robustness": "sensitivity checks (sample definition: not in the plan; run after the W1 labels)",
        }
        if name == "revised":
            status.update({
                "*.baselines/baseline_contrasts": "post hoc: the walks against the contract-graph counts they smooth (RQ3)",
                "*.in_union_graph": "members inside the union graph only; decides no rule",
                "*.label_split": "description of the labels by the class of the counted account, outside every rule",
                "*.cohort_coverage": "where the members lie in the contract graph (description)",
                "robustness.uncapped_allowances": "sensitivity: allowance layer without the balance cap; decides no rule",
            })
        res[name] = {
            "status": NOTES[name], "status_ko": NOTES[name + "_ko"],
            "same_window": compact(sw), "w0": compact(h0), "w1": compact(w1),
            "supplementary": compact(sup), "robustness": compact(rob),
            "B_values": {"same_window": sorted(n_boots(sw)), "w0": sorted(n_boots(h0)), "w1": sorted(n_boots(w1))},
            "status_by_block": status,
            "sources": [c.rel(base / "same-window/eval_summary.json"), c.rel(base / "holdout-w0/eval_summary.json"),
                        c.rel(base / w1dir / "eval_summary.json"), c.rel(base / "supplementary/supplementary.json"),
                        c.rel(base / "robustness/robustness.json")],
        }
    # --- verdicts
    verdicts = {}
    for name, (sw, h0, w1, w1_full) in raw.items():
        rb = w1_full["rule_b"]
        v = {
            "status": NOTES[name],
            "rule_a_primary": {"pass": h0["rule_a_primary"]["pass"],
                               "no_worse_on_new_approvals": h0["rule_a_primary"]["no_worse_on_new_approvals"],
                               "better_on_new_senders": h0["rule_a_primary"]["better_on_new_senders"],
                               "contrasts": compact(h0["contrasts_prefixed"])},
            "rule_a_secondary": compact(sw["rule_a_secondary"]),
            "rule_b": {"applied_criteria": ["F1", "F2"],
                       "F": {k: compact(rb[k]) for k in ("F1", "F2", "F6a", "F6b") if k in rb},
                       "F6": rb.get("F6"),
                       "note": NOTES["rule_b"], "note_ko": NOTES["rule_b_ko"],
                       "conditions_en": {"F1": "spenders, new approval pairs: 95% interval of Δτ above 0",
                                         "F2": "spenders, new transfer senders: lower end above -δ (δ = 0.01)"},
                       "conditions_ko": {"F1": "스펜더, 새 허락 쌍: Δτ의 95% 구간이 0보다 위",
                                         "F2": "스펜더, 새 송금자: 구간 아래 끝이 -δ(δ = 0.01)보다 위"}},
        }
        if name == "revised":
            v["rule_b"].update({"f1_f2_hold": rb["f1_f2_hold"], "rule_b_not_met": rb["rule_b_not_met"],
                                "reading": rb["rule_b_reading"],
                                # 'decision' = "rule B is met": False when F1 or F2 fails, None when both hold
                                # (the thesis then gives no verdict on the rule as registered)
                                "decision": False if rb["rule_b_not_met"] else None})
            for s in ("sensitivity_awp", "sensitivity_isolated"):
                blk = w1_full[s]
                v["rule_b_" + s] = {"F1": compact(blk["F1"]), "F2": compact(blk["F2"]),
                                    "f1_f2_hold": blk["f1_f2_hold"], "rule_b_not_met": blk["rule_b_not_met"],
                                    "reading": blk["rule_b_reading"]}
        else:
            v["rule_b"]["f1_f2_hold"] = bool(rb["F1"]["holds"] and rb["F2"]["holds"])
        verdicts[name] = v
    res["verdicts"] = verdicts
    # --- lambda sweep
    sweep = {}
    for name, (sw, h0, w1, _) in raw.items():
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
                "iterations_tobs": [sw["iterations"][m] for m in keys],
                "iterations_t1": [h0["iterations"][m] for m in keys],
            }
        sweep[name] = {"lambda": LAMBDAS, "keys": LAMBDA_KEYS, **line(LAMBDA_KEYS),
                       "references": {m: line([m]) for m in ("endorserank", "endorserank_activity", "awp", "spr")}}
        degs = {"in_approve_degree": "t1_in_approve_degree", "in_degree": "t1_in_degree"}
        if name == "revised":
            degs.update({"in_approve_value": "t1_in_approve_value", "in_degree_union": "t1_in_degree_union"})
        sweep[name]["degree_baselines"] = {
            k: {"w0_spenders": {lab: tau(h0["taus"], v, lab) for lab in ("future_new_approvers", "future_new_transfer_senders")},
                "w1_spenders": {lab: tau(w1["spender_taus"], k, lab) for lab in ("future_new_approvers", "future_new_transfer_senders")}}
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
    for name, (sw, h0, w1, _) in raw.items():
        cf[name] = {}
        for win, blk in (("same_window", sw), ("w0", h0)):
            b = blk["closed_form"]
            cf[name][win] = {**compact(b), "deeper_spenders": b["spenders"] - b["depth_one_spenders"]}
    res["closed_form"] = {
        "meta": {"formula": "r_v = c (1 + d δ(v)),  δ(v) = Σ_u w(u,v)/o(u)",
                 "c": "common score of every node without in-edges, c = (1 - d + d r_D)/|V|",
                 "within_1pct": "share of spenders whose EndorseRank lies within 1% of the closed form"},
        **cf}
    return res


# ----------------------------------------------------------------------------- discovery-order test

def d_contrast(e):
    out = {"d": [safe(e["point"]), safe(e["lo"]), safe(e["hi"])], "p": safe(e.get("share_positive"))}
    for k in ("a", "b", "hot_set", "x", "n"):
        if k in e:
            out[k] = e[k]
    return out


def d_auc(e):
    """[AUC, lo95, hi95, lowest seed, highest seed, SD over seeds, mean visits to 50% of H, to 90% of H]."""
    def mean(v):
        v = [x for x in (v or []) if x is not None]
        return sig(float(np.mean(v)), 6) if v else None
    return [safe(e["auc"]), safe(e.get("lo")), safe(e.get("hi")), safe(e.get("seed_min")), safe(e.get("seed_max")),
            safe(e.get("seed_sd")), mean(e.get("visits_50")), mean(e.get("visits_90"))]


def d_compact(o):
    """Discovery summaries: contrasts -> {d, p, a, b, hot_set, x, n}; AUC entries -> list; drop seeds' addresses."""
    if isinstance(o, dict):
        ks = set(o)
        if {"point", "lo", "hi"} <= ks:
            return d_contrast(o)
        if {"auc", "per_seed"} <= ks:
            return d_auc(o)
        return {k: d_compact(v) for k, v in o.items() if k not in ("per_seed", "address", "node_id", "provenance")}
    if isinstance(o, list):
        return [d_compact(v) for v in o]
    if isinstance(o, (float, np.floating)):
        return safe(o)
    return clean(o)


def thin_curves(cv, n_u):
    """Keep every grid point up to 10% of |U| visits and every tenth one after it."""
    grid = cv["grid"]
    cut = 0.1 * n_u
    idx = [i for i, k in enumerate(grid) if k <= cut or i % 10 == 0 or i == len(grid) - 1]
    pick = lambda arr: [round(float(arr[i]), 4) if arr[i] is not None else None for i in idx]  # noqa: E731
    out = {"grid": [int(grid[i]) for i in idx], "share_of_U": [round(grid[i] / n_u, 5) for i in idx]}
    for name in ("P_ST", "P_CS", "captured"):
        blk = {}
        for imp, by in cv[name].items():
            row = {}
            for o, v in by.items():
                if isinstance(v, list):
                    row[o] = pick(v)
                elif o in CURVE_KEY_ORDERINGS or name == "P_ST":
                    row[o] = {"mean": pick(v["mean"])}
                    if o in CURVE_KEY_ORDERINGS:
                        row[o]["min"] = pick(v["min"])
                        row[o]["max"] = pick(v["max"])
            blk[imp] = row
        out[name] = blk
    out["cost"] = {o: {"mean": pick(v["mean"])} for o, v in cv["cost"].items() if o in CURVE_KEY_ORDERINGS}
    return out


def build_discovery(c: Ctx):
    out = {"meta": {
        "status": NOTES["discovery"], "status_ko": NOTES["discovery_ko"],
        "decision_rule": ("On H_q(I_T) and on H_q(I_A), with AUC_10%: D1 = C-PR′ − BFS and D2 = C-PR′ − IB′_U "
                          "(docs/discovery_protocol.md, section 6). Verdicts V1, V2, V3 as the protocol states them."),
        "statistic": ("AUC_x = mean over the hot contracts h of ḡ_x(h), g_x(h) = max(0, 1 − t_h/⌈x|U|⌉) averaged "
                      "over the 20 seeds; the normalised area under P_ST up to x|U| visits. x = 10% primary, 5% and "
                      "20% secondary."),
        "auc": "[AUC, lo95, hi95, lowest seed, highest seed, SD over seeds, mean visits to 50% of H, to 90% of H]",
        "contrast": "{d: [point, lo95, hi95], p: share of resamples above 0, a, b, hot_set, x, n}",
        "B": "paired bootstrap over hot contracts, 400 resamples, seed 42",
        "modes": {"both": "a visit reveals the contract's in-edges and out-edges; universe = the WCC of the giant SCC",
                  "out": "a visit reveals out-edges only; universe = SCC ∪ OUT (a sensitivity that carries no verdict)"},
        "hot_sets": "H_q(I): the contracts of the universe with the largest importance I, q = 1/100 (q2 = 5/100); "
                    "'-nohubs' without the hubs (the contracts with the highest IB_U)",
        "curves": ("thinned from the published grid (every point up to 10% of |U| visits, then every tenth): P_ST(K) = "
                   "|H ∩ V_K|/|H|; P_CS(K) = |V_K ∩ R_K|/K; captured = share of Σ_U I held by the visited contracts; "
                   "cost = share of E_U read; mean over seeds (min/max for the key orderings)"),
        "derived": True,
        "note": "No address of a seed, hub or contract is written.",
        "importances": {k: {"en": en, "ko": ko} for k, (en, ko) in IMPORTANCES.items()},
    }, "orderings": ordering_labels()}
    runs = {}
    for tag in ("tobs_both", "tobs_out", "t1_both", "t1_out"):
        d = c.j(c.pub_rev / f"discovery/discovery_{tag}.json")
        proto = d["protocol"]
        n_u = d["sizes"]["universe"]["U"]
        r = {
            "window": d["window"], "mode": d["mode"], "is_primary": d["is_primary"], "decides": d["decides"],
            "protocol": {k: proto.get(k) for k in ("rho", "rho_float", "rho_quarter", "q", "q_secondary", "x",
                                                   "solver", "bootstrap", "decision_covers")},
            "sizes": {"graph": d["sizes"]["graph"], "universe": d["sizes"]["universe"]},
            "seeds": len(d["seeds"]),
            "hot_sets": d["hot_sets"],
            "auc": d_compact(d["auc"]),
            "decision": d_compact(d["decision"]),
            "fixed_order": d_compact(d["fixed_order"]),
            "diagnostics": {"ties": d_compact(d["diagnostics"]["ties"]),
                            "wasted_visits": d_compact(d["diagnostics"]["wasted_visits"]),
                            "hubs": len(d["diagnostics"].get("hubs", [])),
                            "coverage": d_compact(d["diagnostics"]["coverage"])},
            "invariants": d.get("invariants"),
            "source": c.rel(c.pub_rev / f"discovery/discovery_{tag}.json"),
        }
        if d["window"] == "tobs":
            r["curves"] = thin_curves(d["curves"], n_u)
        runs[tag] = r
    out["runs"] = runs
    dec = runs["tobs_both"]["decision"]
    out["decision"] = {"run": "tobs_both", "i_t": dec["i_t"], "i_a": dec["i_a"],
                       "statement": dec["statements"][0] if dec.get("statements") else None}
    # structure pilot at t1, before any score
    f = c.j(c.pub_rev / "discovery/feasibility_t1.json")
    out["pilot"] = {
        "note": ("Structure pilot at t1 (graph shape only, before any score). It raised the stop flag "
                 "few_capped_allowance_in_edges; the test went on (recorded in the protocol). Outside every rule."),
        "window": f["window"], "primary_mode": f["primary_mode"], "stopped": f["stopped"],
        "sizes": f["sizes"], "layers": f["layers"], "union": f["union"], "bow_tie": f["bow_tie"],
        "capped_allowance_in_edge_share": d_compact(f["capped_allowance_in_edge_share"]),
        "stop_flags": f["rules"]["stop"], "primary_universe": f["rules"]["primary_universe"],
        "both_mode_ratio": f["discovery_config"].get("both_mode_ratio"),
        "coverage": d_compact(f["coverage"]),
        "source": c.rel(c.pub_rev / "discovery/feasibility_t1.json"),
    }
    return out


# ----------------------------------------------------------------------------- Sybil, benchmark, params

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
        "contract_farm": ("on the contract graph every farm address is a contract: each costs a deployment, and its "
                          "allowance counts only up to its balance of the token at the freeze (contract_farm, "
                          "balance_threshold in the JSON)"),
        "derived": True,
        "caveat": "before counting that a farm that large would itself enlarge |V| and lower c",
        "d": d}}
    for name, base, proc in (("revised", c.pub_rev, c.proc_rev), ("registered", c.pub, c.proc)):
        sm = strip(c.j(base / "sybil-model/sybil_model.json"))
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
    consts = c.j(c.usd_rev / "constants.json")
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
    zs = [float(f"{z:.4g}") for z in np.logspace(-3, 6, 181)]
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
    raw = consts["raw"]
    return {
        "meta": {"sources": [c.rel(c.exp / "config/contract_reputation.yaml"), c.rel(c.usd_rev / "constants.json"),
                             c.rel(c.pub_rev / "same-window/eval_summary.json"), c.rel(c.pub_rev / "sybil-model/sybil_model.json")],
                 "note": ("Parameters fixed in the configuration of 9 October 2026; the US-dollar constants of the "
                          "contract-graph analysis are set on the W0 score window of the contract graph "
                          "(usd/constants.json).")},
        "chain": {"name": cfg["chain_name"], "id": cfg["chain_id"]},
        "pagerank": {"d": d, "tol": float(rep["pagerank_tolerance"]), "max_iter": int(rep["max_iterations"]),
                     "start": "r(0) = 1/|V|", "stop": "||r(t+1) - r(t)||_1 < tol or max_iter",
                     "update": "r(t+1) = (1-d) π + d Pᵀ r(t) + d (r(t)ᵀ 1_dang) π",
                     "restarts": {"endorserank": "uniform over contracts",
                                  "endorserank_activity": "π_u ∝ approving activity of owner contract u",
                                  "awp": "π_u ∝ X_u (sending activity of contract u)",
                                  "cpr": "uniform over contracts", "spr": "π ∝ C-PR (λ=1) scores on V_T"}},
        "decay": {"k": k, "t0_days": t0, "formula": "σ(Δt) = 1 / (1 + exp(k (Δt - t0)))",
                  "table": [[t, round(sigma(t), 4)] for t in (0, 90, 180, 273, 365)],
                  "curve": {"dt": dts, "sigma": [sig(sigma(t)) for t in dts]}},
        "value": {"formula": "V(z) = 2/(1 + e^(-b z)) - 1", "rule": consts["rule"],
                  "m_T": consts["m_transfer_usd"], "m_A": consts["m_allowance_usd"],
                  "m_T_raw": safe(raw["m_transfer"]), "m_A_raw": safe(raw["m_allowance"]),
                  "m_A_note": "median positive capped allowance between contracts at t1 (unlimited ones included)",
                  "b_T": sig(bT, 6), "b_A": sig(bA, 6), "b_registered": float(rep["awp_value_b"]),
                  "ln3": sig(math.log(3), 6),
                  "points": {"V(m)": 0.5, "V(2m)": round(V(2, math.log(3)), 4), "V(m/2)": round(V(0.5, math.log(3)), 4)},
                  "curve": {"z_usd": zs, "V_T": [sig(V(z, bT)) for z in zs], "V_A": [sig(V(z, bA)) for z in zs]},
                  "constants_computed_at": consts["computed_at"], "window": consts.get("window")},
        "cap": {"U_usd": consts["cap_allowance_usd"], "U_user_usd": consts["cap_user_usd"],
                "p99_transfer_usd_raw": safe(raw["p99_transfer"]),
                "p99_capped_allowance_usd_raw": safe(raw["p99_allowance"]),
                "p99_user_transfer_usd_raw": safe(raw["p99_user_transfer"]),
                "unlimited_threshold_base_units": consts["unlimited_base_units"],
                "dust_token": consts.get("dust_token"),
                "uint256_max": sig(2.0 ** 256 - 1),
                "balance_cap": "usd_eff = min(allowance, balance of the owner at the freeze), in USD at the freeze day's price",
                "note": ("U = 99th percentile of the US-dollar values of single transfers between contracts in the W0 "
                         "score window (2025-04-01 to t1), two significant digits; U_user = the same percentile of the "
                         "transfers from user accounts to contracts, the cap per user account in the importance "
                         "measures of the discovery-order test")},
        "coupled": {"lambda_primary": float(rep["hybrid"]["coupled_lambda_primary"]),
                    "lambda_grid": [float(x) for x in rep["hybrid"]["coupled_lambda_grid"]], "endpoints": [0.0, 1.0],
                    "row": "P(λ)_u = α_A(u) P_A,u + α_T(u) P_T,u; α_A = λ 1[o_A>0]/D, α_T = (1-λ) 1[o_T>0]/D"},
        "stats": {"B": int(cfg["alignment"]["bootstrap_resamples"]), "seed": int(cfg["alignment"]["bootstrap_seed"]),
                  "ci": 0.95, "bonferroni_ci": 0.975,
                  "delta": float(cfg["registered_window"]["margin_delta"]),
                  "kendall": "τ_b = (n_c - n_d) / sqrt((n0 - n1)(n0 - n2))",
                  "spearman_no_ties": "ρ = 1 - 6 Σ (R_i - S_i)^2 / (n (n^2 - 1))",
                  "family_mean": "plain average of the τ of the family's proxies"},
        "cohort": {"min_owners": int(cfg["cohort"]["min_owners"]),
                   "tokens": ["WETH", "USDC", "USDT0", "ARB", "WBTC"],
                   "rule": ("a non-zero Approval of one of the five tokens from at least three distinct owners in the "
                            "score window (counts every approving account); members typed as user accounts are left "
                            "out of the contract-graph cohorts")},
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


def build_holdout(c: Ctx):
    out = {"meta": {"derived": True,
                    "note": ("Descriptive: spenders grouped into ten bins by the mid-rank percentile of each score at the "
                             "freeze; per bin the number of spenders, the share that gained at least one new approval "
                             "pair / new transfer sender, and the mean counts. Tied scores (e.g. AWP = 0 for spenders "
                             "without a transfer edge) stay in one bin, so bins differ in size. Not a thesis table; the "
                             "τ_b values are in results.*.w0.taus and results.*.w1.spender_taus. " + NOTES["labels"]),
                    "bin": "[n, share_new_approvals, share_new_senders, mean_new_approvals, mean_new_senders]"}}
    for name, d, deg in (("w0", c.proc_rev / "holdout-w0",
                          ("t1_in_approve_degree", "t1_in_degree", "t1_in_approve_value", "t1_in_degree_union")),
                         ("w1", c.proc_rev / "window-w1",
                          ("in_approve_degree", "in_degree", "in_approve_value", "in_degree_union"))):
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
                     "in_union_graph": int(s["in_union_graph"].astype(bool).sum()),
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
    s = s.replace("P(Δτ>0)", "P").replace("97.5%", "")
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
    disc = deck["discovery"]
    checks = []

    def add(name, digest_rows, src, ours, pick=None):
        """Compare the numbers of a digest row with ours (list of numbers, bool or string)."""
        rows = digest_rows.get(src)
        if not rows:
            checks.append((name, "<missing in digest>", ours, False))
            return
        q, val = rows[0] if pick is None else next(r for r in rows if pick in r[0])
        if isinstance(ours, bool):
            ok = (val in ("yes", "holds")) == ours if val in ("yes", "no", "holds", "does not hold") else False
            checks.append((name, val, ours, ok))
            return
        if isinstance(ours, str):
            checks.append((name, val, [ours], val.strip() == ours.strip()))
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

    sw, h0, w1 = res["revised"]["same_window"], res["revised"]["w0"], res["revised"]["w1"]
    rv = scale["revised"]
    add("rev: matched cohort", R, "cohort/matched_cohort.json : cohort", [rv["cohort"]])
    add("rev: T_obs allowance edges", R, "same-window/eval_summary.json : graph.allowance.edges",
        [rv["graph_tobs"]["allowance"]["edges"]])
    add("rev: T_obs transfer edges", R, "same-window/eval_summary.json : graph.transfer.edges",
        [rv["graph_tobs"]["transfer"]["edges"]])
    add("rev: T_obs union graph nodes", R, "same-window/eval_summary.json : union_graph.nodes",
        [rv["union_graph_tobs"]["nodes"]])
    add("rev: five-token rows", R, "describe/describe.json : events.five_token_rows", [rv["events"]["five_token_rows"]])
    add("rev: user accounts", R, "describe/describe.json : events.user_accounts", [rv["account_types"]["user_accounts"]])
    add("rev: contracts after extension", R, "describe/describe.json : account_types.after_extension.contract",
        [rv["account_types"]["after_extension"]["contract"]])
    add("rev: nodes of the contract graph", R, "describe/describe.json : nodes.contracts", [rv["nodes"]["contracts"]])
    add("rev: latest allowances at T_obs", R, "describe/describe.json : allowances.tobs.total.n_latest_positive",
        [rv["amounts"]["latest_allowances_tobs"]])
    add("rev: capped to zero share at T_obs", R, "describe/describe.json : allowances.tobs.total.share_capped_to_zero",
        [rv["amounts"]["capped_to_zero_share"]])
    add("rev: balance check matched", R, "describe/describe.json : balance_check.matched", [rv["balance_check"]["matched"]])
    add("rev: union coverage of the cohort", R, "same-window/eval_summary.json : cohort_coverage.cohort_tobs.union_graph",
        [rv["cohort_coverage"]["cohort_tobs"]["union_graph"]["n"], rv["cohort_coverage"]["cohort_tobs"]["union_graph"]["share"]])
    add("rev: ER allowance family", R, "same-window/eval_summary.json : families.endorserank.allowance",
        sw["families"]["endorserank"]["allowance"])
    add("rev: C-PR(λ=0) transfer family", R, "same-window/eval_summary.json : families.cpr_l0.transfer",
        res["lambda_sweep"]["revised"]["same_window"]["transfer"][0])
    add("rev: AWP Sybil family", R, "same-window/eval_summary.json : families.awp.sybil_stability",
        sw["families"]["awp"]["sybil_stability"])
    f1 = res["verdicts"]["revised"]["rule_b"]["F"]["F1"]
    add("rev: rule B F1", R, "window-w1/eval_summary.json : rule_b.F1", f1["d"] + [f1["ta"], f1["tb"], f1["p"]])
    f2 = res["verdicts"]["revised"]["rule_b"]["F"]["F2"]
    add("rev: rule B F2", R, "window-w1/eval_summary.json : rule_b.F2", f2["d"] + [f2["ta"], f2["tb"], f2["p"]])
    add("rev: F1 and F2 hold", R, "window-w1/eval_summary.json : rule_b.f1_f2_hold",
        res["verdicts"]["revised"]["rule_b"]["f1_f2_hold"])
    add("rev: rule B reading", R, "window-w1/eval_summary.json : rule_b.rule_b_reading",
        res["verdicts"]["revised"]["rule_b"]["reading"])
    add("rev: rule A primary pass", R, "holdout-w0/eval_summary.json : rule_a_primary.pass",
        res["verdicts"]["revised"]["rule_a_primary"]["pass"])
    add("rev: W1 in-approve degree, new pairs", R,
        "window-w1/eval_summary.json : spender_taus.in_approve_degree.future_new_approvers",
        res["lambda_sweep"]["revised"]["degree_baselines"]["in_approve_degree"]["w1_spenders"]["future_new_approvers"])
    add("rev: W1 union in-degree, new pairs", R,
        "window-w1/eval_summary.json : spender_taus.in_degree_union.future_new_approvers",
        res["lambda_sweep"]["revised"]["degree_baselines"]["in_degree_union"]["w1_spenders"]["future_new_approvers"])
    add("rev: W1 ER, new pairs", R, "window-w1/eval_summary.json : spender_taus.endorserank.future_new_approvers",
        res["lambda_sweep"]["revised"]["references"]["endorserank"]["w1_spenders"]["future_new_approvers"][0])
    add("rev: closed form within 1% (all)", R, "same-window/eval_summary.json : closed_form.within_1pct_all",
        [res["closed_form"]["revised"]["same_window"]["within_1pct_all"]])
    e = bm["revised"]["main"]["endorserank"]
    add("rev: benchmark ER", R, "benchmark/benchmark.json : main.endorserank",
        [e["mean_s"], e["sd_s"]] + e["runs_s"] + [e["peak_mb"], e["iterations"], e["nodes"], e["edges"]])
    a = bm["revised"]["main"]["awp"]
    add("rev: benchmark AWP", R, "benchmark/benchmark.json : main.awp", [a["mean_s"], a["sd_s"]])
    add("rev: AWP/ER runtime ratio", R, "benchmark/benchmark.json : main.awp.mean_s / main.endorserank.mean_s",
        [bm["revised"]["derived"]["time_ratio_awp_over_er"]])
    kp = sy["revised"]["key_points"]["p100"]
    add("rev: Sybil farm for p100", R, "sybil-model/sybil_model.json : farm_size_to_reach_cohort_quantile.p100.farm_addresses",
        [kp["farm_addresses"]])
    curve99 = next(pt for pt in sy["revised"]["curve"] if abs(pt[0] - 99) < 1e-9)
    add("rev: Sybil curve at q=99", R, "sybil-model/sybil_model.json : farm_size_to_reach_cohort_quantile.p99.farm_addresses",
        [curve99[2]])
    add("rev: Sybil farm deployments to the top", R, "sybil-model/sybil_model.json : contract_farm.deployments.reach.p100",
        [sy["revised"]["json"]["contract_farm"]["deployments"]["reach"]["p100"]])
    add("rev: Sybil θ = 1 share of pairs kept", R, "sybil-model/sybil_model.json : balance_threshold.1.share_of_pairs_kept",
        [sy["revised"]["json"]["balance_threshold"]["1"]["share_of_pairs_kept"]])
    add("rev: constants b_A", R, "describe/describe.json : constants.b_allowance", [deck["params"]["value"]["b_A"]])
    add("rev: cap U", R, "describe/describe.json : constants.cap_allowance_usd", [deck["params"]["cap"]["U_usd"]])
    add("rev: cap U_user", R, "describe/describe.json : constants.cap_user_usd", [deck["params"]["cap"]["U_user_usd"]])
    add("rev: cohort outside allowance graph (flags)", R, "same-window/eval_summary.json : graph.cohort_outside_allowance",
        [deck["contracts"]["flag_counts"]["outside_allowance"]])
    add("rev: cohort outside both graphs (flags)", R, "same-window/eval_summary.json : graph.cohort_outside_both",
        [deck["contracts"]["flag_counts"]["outside_both"]])
    add("rev: cohort in the union graph (parquet flag)", R, "same-window/eval_summary.json : cohort_coverage.cohort_tobs.union_graph",
        [deck["contracts"]["flag_counts"]["in_union_graph"]])
    weth = next(t for t in pr["tokens"] if t["symbol"] == "WETH")
    add("rev: WETH price days (series)", R, "describe/describe.json : price_days.per_token[1]", [weth["days_main_window"]])
    add("rev: W0 spenders", R, "holdout-w0/eval_summary.json : spenders", [rv["w0"]["spenders"]])
    add("rev: W1 spenders", R, "window-w1/eval_summary.json : spenders", [rv["w1"]["spenders"]])
    # discovery-order test
    dec = disc["runs"]["tobs_both"]["decision"]
    for imp in ("i_t", "i_a"):
        for k in ("D1", "D2"):
            x = dec[imp][k]
            add(f"disc: tobs both {k} on {imp}", R, f"discovery/discovery_tobs_both.json : decision.{imp}.{k}",
                x["d"] + [0, x["p"]])
        add(f"disc: verdict on {imp}", R, f"discovery/discovery_tobs_both.json : decision.{imp}.verdict", dec[imp]["verdict"])
    add("disc: statement", R, "discovery/discovery_tobs_both.json : decision.statements[0]", disc["decision"]["statement"])
    au = disc["runs"]["tobs_both"]["auc"]
    for o in ("bfs", "ib_u", "cpr_l50", "awp", "ref_ideal"):
        add(f"disc: AUC {o} on H_q(I_T)", R, f"discovery/discovery_tobs_both.json : auc.i_t@q.{o}.x=0.1", au["i_t@q"][o]["x=0.1"][:5])
    add("disc: AUC C-PR′ on H_q(I_A)", R, "discovery/discovery_tobs_both.json : auc.i_a@q.cpr_l50.x=0.1",
        au["i_a@q"]["cpr_l50"]["x=0.1"][:5])
    add("disc: universe", R, "discovery/discovery_tobs_both.json : sizes.universe.U",
        [disc["runs"]["tobs_both"]["sizes"]["universe"]["U"]])
    add("disc: hot set I_T", R, "discovery/discovery_tobs_both.json : hot_sets.i_t@q", [disc["runs"]["tobs_both"]["hot_sets"]["i_t@q"]])
    for tag in ("tobs_out", "t1_both", "t1_out"):
        x = disc["runs"][tag]["decision"]["i_t"]["D1"]
        add(f"disc: {tag} D1 on i_t", R, f"discovery/discovery_{tag}.json : decision.i_t.D1", x["d"] + [0, x["p"]])
    # registered
    rsw = res["registered"]["same_window"]
    add("reg: matched cohort", Rg, "cohort/matched_cohort.json : cohort", [scale["registered"]["cohort"]])
    add("reg: ER allowance family", Rg, "same-window/eval_summary.json : families.endorserank.allowance",
        rsw["families"]["endorserank"]["allowance"])
    f1g = res["verdicts"]["registered"]["rule_b"]["F"]["F1"]
    add("reg: rule B F1", Rg, "registered-w1/eval_summary.json : rule_b.F1", f1g["d"] + [f1g["ta"], f1g["tb"]])
    add("reg: benchmark AWP", Rg, "benchmark/benchmark.json : main.awp",
        [bm["registered"]["main"]["awp"]["mean_s"], bm["registered"]["main"]["awp"]["sd_s"]])
    add("reg: Sybil farm for p100", Rg, "sybil-model/sybil_model.json : farm_size_to_reach_cohort_quantile.p100.farm_addresses",
        [sy["registered"]["key_points"]["p100"]["farm_addresses"]])

    # recomputed from parquet (shows the parquet files are the inputs of the digest values)
    try:
        from scipy.stats import kendalltau
        s0 = c.pq(c.proc_rev / "holdout-w0", "spender_scores")
        s1 = c.pq(c.proc_rev / "window-w1", "spender_scores")
        cs = c.pq(c.proc_rev / "same-window", "cohort_scores")
        rec = [
            ("parquet: W0 ER vs new pairs", "holdout-w0/eval_summary.json : taus.endorserank.future_new_approvers",
             kendalltau(s0["endorserank"], s0["future_new_approvers"], variant="b")[0]),
            ("parquet: W1 in-approve degree vs new pairs", "window-w1/eval_summary.json : spender_taus.in_approve_degree.future_new_approvers",
             kendalltau(s1["in_approve_degree"], s1["future_new_approvers"], variant="b")[0]),
            ("parquet: W1 union in-degree vs new pairs", "window-w1/eval_summary.json : spender_taus.in_degree_union.future_new_approvers",
             kendalltau(s1["in_degree_union"], s1["future_new_approvers"], variant="b")[0]),
            ("parquet: same-window ER vs in-approve degree", "same-window/eval_summary.json : per_proxy.endorserank.in_approve_degree",
             kendalltau(cs["endorserank"], cs["in_approve_degree"], variant="b")[0]),
        ]
        for name, src, tau in rec:
            add(name, R, src, [tau])
    except ImportError:
        checks.append(("parquet recomputation", "scipy not installed", None, True))

    # nothing of the outcomes the deck does not show, and no address, is written
    blob = " ".join((c.out / f"{k}.js").read_text(encoding="utf-8") for k in deck)
    for word in ("trader", "liquidat", "gmx", "neutral_w"):
        checks.append((f"absent: '{word}'", "-", None, word not in blob.lower()))
    checks.append(("absent: addresses (0x + 40 hex)", "-", None, re.search(r"0x[0-9a-fA-F]{40}", blob) is None))

    w = max(len(x[0]) for x in checks)
    print(f"\nVerification against the results digests ({VARIANT}/results_digest.md = rev, results_digest.md = reg):")
    print(f"{'check':<{w}}  {'ok':<4} digest value  ||  deck value")
    for name, dv, ov, ok in checks:
        ovs = ov if isinstance(ov, bool) else ", ".join(
            "None" if v is None else (f"{v:.6g}" if isinstance(v, float) else str(v)) for v in (ov or []))
        print(f"{name:<{w}}  {'OK' if ok else 'FAIL':<4} {str(dv)[:90]}  ||  {str(ovs)[:90]}")
    n_ok = sum(1 for x in checks if x[3])
    print(f"\n{n_ok}/{len(checks)} checks passed")
    return n_ok == len(checks)


# ----------------------------------------------------------------------------- main

def write_js(out: Path, key: str, obj, sources):
    out.mkdir(parents=True, exist_ok=True)
    body = json.dumps(clean(obj), ensure_ascii=True, separators=(",", ":"), allow_nan=False)
    head = ("/* Generated by dissertation/presentation/tools/build_data.py -- do not edit by hand.\n"
            "   Sources (relative to the repository root): " + "; ".join(sorted(set(sources)))[:3000].replace("*/", "* /") + " */\n")
    p = out / f"{key}.js"
    p.write_text(head + "window.DECK_DATA = window.DECK_DATA || {};\nwindow.DECK_DATA." + key + " = " + body + ";\n",
                 encoding="utf-8")
    return p


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("phd_works", nargs="?", metavar="REPO",
                    help="root of the public repository (default: $CONTRACT_REP_REPO, $PHD_WORKS or derived from this file)")
    ap.add_argument("--out", help="output folder (default: ../data next to this script)")
    ap.add_argument("--no-verify", action="store_true", help="skip the comparison with the digests")
    args = ap.parse_args(argv)
    here = Path(__file__).resolve()
    phd = Path(args.phd_works or os.environ.get("CONTRACT_REP_REPO") or os.environ.get("PHD_WORKS")
               or here.parents[3]).resolve()
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
    run("discovery", build_discovery, c)
    run("sybil", build_sybil, c, cfg)
    run("benchmark", build_benchmark, c)
    run("params", build_params, c, cfg)
    run("holdout", build_holdout, c)

    stale = out / "traders.js"
    if stale.exists():
        stale.unlink()
        print("removed data/traders.js (no trader data in the deck)")

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
        "analyses": {"revised": {"en": "Contract-graph analysis (main)", "ko": "계약 그래프 분석(주 분석)",
                                 "variant": "contract12m", "note": NOTES["revised"], "note_ko": NOTES["revised_ko"]},
                     "registered": {"en": "Registered analysis", "ko": "등록 분석", "note": NOTES["registered"],
                                    "note_ko": NOTES["registered_ko"]}},
        "methods": method_labels(),
        "orderings": ordering_labels(),
        "notes": NOTES,
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "generator": "dissertation/presentation/tools/build_data.py",
        "repository": "https://github.com/abitocodes/ERC20-Allowance-PageRank-Wallet-Reputation",
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
