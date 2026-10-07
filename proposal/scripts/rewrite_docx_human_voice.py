# -*- coding: utf-8 -*-
"""Rewrite proposal DOCX prose to reduce AI-detector hallmarks; keep structure/formatting."""
from __future__ import annotations

import re
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from lxml import etree

SRC = Path(r"c:\Users\abito\Downloads\Proposal-Draft_Taehong Kwon_28576810 (1).docx")
OUT = SRC  # same path per user request
BACKUP = SRC.with_name(SRC.stem + "_pre_humanize_backup.docx")

AUTHOR = "Taehong Kwon"
INITIALS = "TK"
COMMENT_DATE = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W14_NS = "http://schemas.microsoft.com/office/word/2010/wordml"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
REL_COMMENTS = (
    "http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments"
)

# Paragraph index -> (new_text, comment). None = leave unchanged.
# Mid-page-break fragments are rewritten so consecutive paragraphs still read as one argument.
REWRITES: dict[int, tuple[str, str]] = {
    # Title page typo + Abstract heading
    11: (
        "DOCTOR OF PHILOSOPHY",
        "요청: AI 탐지 완화 재작성 — 표지 오타 PHILIOSOPHY → PHILOSOPHY",
    ),
    29: (
        "Abstract",
        "요청: AI 탐지 완화 재작성 — 제목 Abtract → Abstract",
    ),
    # Abstract
    31: (
        "Lending remains one of the main channels through which financial systems allocate capital. "
        "DeFi is unlikely to mature unless on-chain lending can scale in a similar way. "
        "That path is blocked on two fronts. Collateralised loans are hard to enforce when the "
        "collateral itself sits in a smart contract that the lender cannot seize under conventional "
        "legal process. Unsecured credit is harder still: the usual credit-bureau inputs—income, "
        "employment, and tangible assets—are simply not available for pseudonymous wallets.",
        "요청: Turnitin AI 탐지 완화 — Abstract 도입부 문체 재작성 (의미 유지)",
    ),
    33: (
        "PageRank-style wallet scores already exist. Do et al.'s Adaptive Weighted PageRank (AWP), "
        "for example, ranks addresses by transfer volume and by how recently those transfers occurred. "
        "The method tracks economic activity, but it also forces a full historical scan of transfers. "
        "On a chain the size of Ethereum, that scan quickly becomes expensive in both time and storage.",
        "요청: Turnitin AI 탐지 완화 — Abstract AWP 문단 재작성",
    ),
    35: (
        "We propose AbitoRank. Instead of transfers, it treats ERC-20 approve and permit allowances "
        "as endorsement edges. When a holder authorises another address to spend tokens, that "
        "authorisation is an explicit trust signal, not an inferred one. AbitoRank builds a directed "
        "weighted graph Gapprove from the latest nonzero allowance for each owner–spender pair. "
        "Because a new allowance replaces the previous one for the same pair, we can drop "
        "time-decay machinery and work on a much smaller edge set.",
        "요청: Turnitin AI 탐지 완화 — Abstract AbitoRank 제안 문단 재작성",
    ),
    37: (
        "AbitoRank then runs weighted PageRank on that allowance graph. The work is organised around four aims:",
        "요청: Turnitin AI 탐지 완화 — Abstract 목표 도입 재작성",
    ),
    38: (
        "Build a pipeline that keeps only the current approve/permit allowance for each owner–spender pair.",
        "요청: Turnitin AI 탐지 완화 — Abstract 목표 1 재작성",
    ),
    39: (
        "Compute reputation scores on the resulting sparse endorsement graph.",
        "요청: Turnitin AI 탐지 완화 — Abstract 목표 2 재작성",
    ),
    43: (
        "Test whether AbitoRank predicts on-chain financial risk (for example, Aave defaults) at least as "
        "well as transfer-based PageRank baselines, using AUC, precision, and recall.",
        "요청: Turnitin AI 탐지 완화 — Abstract 목표 3 재작성",
    ),
    44: (
        "Benchmark runtime and memory against those baselines.",
        "요청: Turnitin AI 탐지 완화 — Abstract 목표 4 재작성",
    ),
    45: (
        "If those aims are met, AbitoRank should give DeFi protocols a reputation score that is cheaper "
        "to compute, easier to interpret as delegated trust, and useful for risk decisions.",
        "요청: Turnitin AI 탐지 완화 — Abstract 마무리 재작성",
    ),
    49: (
        "Keywords— DeFi, On-Chain Reputation, On-Chain Financial Risk Prediction, Blockchain Data Analytics, "
        "Predictive Modeling, Wallet Endorsement Graph",
        "요청: Turnitin AI 탐지 완화 — Keywords 서식 정리",
    ),
    # Chapter 1
    64: (
        "In credit markets, reputation scores exist mainly to separate borrowers who are likely to repay "
        "from those who are not. On-chain work has borrowed the same idea. Do et al. (2023) proposed "
        "Adaptive Weighted PageRank (AWP): wallets with larger inflows look more trusted, and recent "
        "transfers are up-weighted through a logistic time-decay. That design mixes economic size with "
        "recency, but it also requires every historical transfer to be parsed. On Ethereum-scale graphs "
        "the cost shows up quickly—both in compute and in storage.",
        "요청: Turnitin AI 탐지 완화 — Ch.1 도입 재작성",
    ),
    66: (
        "ERC-20 already encodes a more direct trust signal. Through approve and permit, a token holder "
        "tells another address how much it may spend. The authorised amount is itself a measure of how "
        "far that trust extends. If we keep only the latest allowance for each owner–spender pair, "
        "we obtain a directed weighted endorsement graph Gapprove whose edge weights are current "
        "approved amounts. Fresh approvals overwrite older ones for the same pair, so there is no need "
        "for a separate decay schedule; the graph already reflects the live permission state.",
        "요청: Turnitin AI 탐지 완화 — Ch.1 ERC-20/allowance 문단 재작성 (페이지 분할 문장 정리)",
    ),
    67: (
        "",
        "요청: Turnitin AI 탐지 완화 — 앞 문단으로 병합되어 본문 비움 (페이지 분할 잔여)",
    ),
    69: (
        "Approval graphs are also typically sparser than transfer graphs, and their edges carry clearer "
        "endorsement meaning. Even so, ERC-20 allowances have not been used as the primary PageRank "
        "edge weight in prior work. That gap is what AbitoRank targets: a standard weighted PageRank "
        "on Gapprove. We expect predictive performance on financial risk outcomes (such as defaults) "
        "to match or beat transfer- and time-decay-based scores, while cutting data-processing cost.",
        "요청: Turnitin AI 탐지 완화 — Ch.1 연구 공백/가설 재작성",
    ),
    73: (
        "",
        "요청: Turnitin AI 탐지 완화 — 앞 문단으로 병합되어 본문 비움 (페이지 분할 잔여)",
    ),
    # Chapter 2
    79: (
        "Most PageRank-based on-chain reputation scores still treat transfer amounts as the proxy for "
        "economic ties. AWP is the strongest example of that line of work, yet two problems remain:",
        "요청: Turnitin AI 탐지 완화 — Ch.2 문제제기 도입 재작성",
    ),
    80: (
        "Computational cost. AWP must walk the full transfer history of every wallet in scope. On "
        "Ethereum mainnet, where millions of token transfers occur each day, that walk drives long "
        "ingestion times, large memory footprints, and slow PageRank iterations.",
        "요청: Turnitin AI 탐지 완화 — Ch.2 비효율 항목 재작성",
    ),
    81: (
        "Weak trust semantics. A transfer shows that value moved; it does not show that one wallet "
        "chose to authorise another. Approve and permit do. They record a holder's willingness to "
        "delegate spending rights, which is closer to the notion of endorsement used in credit settings.",
        "요청: Turnitin AI 탐지 완화 — Ch.2 신뢰 표현 항목 재작성",
    ),
    82: (
        "The research problem follows directly: can an on-chain reputation score built from ERC-20 "
        "approve/permit relationships cut computation, represent endorsement more faithfully, and still "
        "predict financial risk (including defaults) at least as well as transfer-based PageRank?",
        "요청: Turnitin AI 탐지 완화 — Ch.2 중심 연구문제 재작성",
    ),
    84: (
        "To answer that question we will design, implement, and evaluate AbitoRank on an endorsement "
        "graph derived from ERC-20 approve and permit calls. Practical obstacles include:",
        "요청: Turnitin AI 탐지 완화 — Ch.2 해결 방향 재작성 (분할 문단 통합)",
    ),
    88: (
        "",
        "요청: Turnitin AI 탐지 완화 — 앞 문단으로 병합되어 본문 비움",
    ),
    89: (
        "Keeping only the latest approve/permit state per owner–spender pair so stale allowances do not "
        "distort the graph.",
        "요청: Turnitin AI 탐지 완화 — Ch.2 과제 1 재작성",
    ),
    90: (
        "Getting PageRank to converge quickly on large but sparse graphs.",
        "요청: Turnitin AI 탐지 완화 — Ch.2 과제 2 재작성",
    ),
    91: (
        "Checking how strongly AbitoRank aligns with default events in lending protocols such as Aave.",
        "요청: Turnitin AI 탐지 완화 — Ch.2 과제 3 재작성",
    ),
    95: (
        "RQ1.1: How should ERC-20 approve and permit events be preprocessed so that the resulting "
        "binary endorsement graph stays current and reliable?",
        "요청: Turnitin AI 탐지 완화 — RQ1.1 재작성",
    ),
    96: (
        "RQ1.2: Does an approve/permit graph retain enough trust signal relative to a transaction-value graph?",
        "요청: Turnitin AI 탐지 완화 — RQ1.2 재작성",
    ),
    98: (
        "RQ2.1: How does AbitoRank reorder wallets relative to AWP and to ordinary transfer-weighted PageRank?",
        "요청: Turnitin AI 탐지 완화 — RQ2.1 재작성",
    ),
    99: (
        "RQ2.2: Where do AbitoRank and AWP scores agree, and where do they diverge?",
        "요청: Turnitin AI 탐지 완화 — RQ2.2 재작성",
    ),
    101: (
        "RQ3.1: How strongly do AbitoRank scores correlate with on-chain default or liquidation events "
        "(for example on Aave V3)?",
        "요청: Turnitin AI 탐지 완화 — RQ3.1 재작성",
    ),
    102: (
        "RQ3.2: On AUC, precision, and recall for default prediction, how does AbitoRank compare with "
        "AWP and transfer-based PageRank?",
        "요청: Turnitin AI 탐지 완화 — RQ3.2 재작성",
    ),
    107: (
        "RQ4.1: For a fixed wallet set, what are the runtime and resource costs (CPU, memory) of "
        "AbitoRank versus AWP?",
        "요청: Turnitin AI 탐지 완화 — RQ4.1 재작성",
    ),
    108: (
        "RQ4.2: How does the sparsity difference between approve/permit and transfer graphs affect "
        "PageRank convergence speed and numerical stability?",
        "요청: Turnitin AI 탐지 완화 — RQ4.2 재작성",
    ),
    111: (
        "The main goal is to design, implement, and evaluate AbitoRank: a reputation score that uses "
        "ERC-20 approve/permit allowances as edge weights and does not apply time decay. In more "
        "detail, the study will:",
        "요청: Turnitin AI 탐지 완화 — Objectives 총괄 재작성",
    ),
    113: (
        "O1.1: Build an extraction pipeline that reads Ethereum ERC-20 Approve and Permit events, "
        "retains the most recent allowance for each owner–spender pair, and stores those values.",
        "요청: Turnitin AI 탐지 완화 — O1.1 재작성",
    ),
    114: (
        "Rationale: A later approve/permit for the same pair replaces earlier ones, so only the latest "
        "allowance needs to be kept.",
        "요청: Turnitin AI 탐지 완화 — O1.1 근거 재작성",
    ),
    115: (
        "O1.2: Form a directed weighted graph Gapprove. Nodes are ERC-20 wallets. An edge (u→v) carries "
        "the latest approved amount from owner u to spender v (in token units).",
        "요청: Turnitin AI 탐지 완화 — O1.2 재작성",
    ),
    116: (
        "Detail: No time-based decay and no multi-event aggregation; older approvals for a pair are "
        "superseded by the newest event.",
        "요청: Turnitin AI 탐지 완화 — O1.2 세부 재작성",
    ),
    121: (
        "O2.1: Run weighted PageRank on Gapprove so that each node spreads score to neighbours in "
        "proportion to allowance weights.",
        "요청: Turnitin AI 탐지 완화 — O2.1 재작성",
    ),
    123: (
        "Normalise each node's outgoing edges so that the transition probability from u to neighbour v is:",
        "요청: Turnitin AI 탐지 완화 — O2.1 정규화 설명 재작성",
    ),
    131: (
        "where wu→v is the latest approved amount.",
        "요청: Turnitin AI 탐지 완화 — 수식 설명 문장 정리",
    ),
    132: (
        "Keep a conventional damping factor (for example 0.85). Do not add further time-weighting or "
        "value decay on top of the raw allowance.",
        "요청: Turnitin AI 탐지 완화 — damping 명세 재작성",
    ),
    133: (
        "O2.2: Tune the implementation for large sparse graphs with sparse-matrix layouts and efficient "
        "iterative solvers, aiming for low memory use and short runtimes to convergence.",
        "요청: Turnitin AI 탐지 완화 — O2.2 재작성",
    ),
    135: (
        "O3.1: Reproduce two baselines on the same Aave V3 wallet set and the same observation window:",
        "요청: Turnitin AI 탐지 완화 — O3.1 재작성",
    ),
    136: (
        "Adaptive Weighted PageRank (AWP): transfer-value-weighted PageRank with time decay on transfers.",
        "요청: Turnitin AI 탐지 완화 — AWP baseline 설명 재작성",
    ),
    137: (
        "Transfer-based weighted PageRank: ERC-20 transfer amounts as edge weights, without time decay.",
        "요청: Turnitin AI 탐지 완화 — transfer baseline 설명 재작성",
    ),
    138: (
        "O3.2: Run AbitoRank, AWP, and transfer-based PageRank through one shared processing pipeline on "
        "the same wallets and events, so ranking differences cannot be blamed on mismatched inputs.",
        "요청: Turnitin AI 탐지 완화 — O3.2 재작성",
    ),
    142: (
        "Quantitative Performance Evaluation",
        "요청: AI 탐지 완화 재작성 — 제목 오타 Quatitative → Quantitative",
    ),
    143: (
        "O4.1: Compute Spearman's ρ and Kendall's τ between AbitoRank and each baseline to measure how "
        "similarly (or differently) wallets are ordered.",
        "요청: Turnitin AI 탐지 완화 — O4.1 재작성",
    ),
    144: (
        "O4.2: Compare score distributions (mean, median, interquartile range) across methods, and flag "
        "wallets that score high under approvals but low under transfers, or the reverse.",
        "요청: Turnitin AI 탐지 완화 — O4.2 재작성",
    ),
    146: (
        "Label wallets as defaulted or not defaulted from Aave V3 liquidation events.",
        "요청: Turnitin AI 탐지 완화 — O4.3 라벨링 재작성",
    ),
    147: (
        "Treat each ranking score as a feature in a simple classifier (logistic regression or random forest) "
        "that separates defaulted from non-defaulted wallets.",
        "요청: Turnitin AI 탐지 완화 — O4.3 분류기 재작성",
    ),
    148: (
        "Report AUC, precision, recall, F1-score, and calibration for each ranking method, and test whether "
        "AbitoRank matches or exceeds AWP and transfer-based PageRank.",
        "요청: Turnitin AI 탐지 완화 — O4.3 평가 재작성",
    ),
    150: (
        "O5.1 Runtime benchmarking: Measure end-to-end time (extraction, graph build, PageRank convergence) "
        "for AbitoRank, AWP, and transfer-based PageRank on a fixed set (for example 100,000 nodes).",
        "요청: Turnitin AI 탐지 완화 — O5.1 재작성",
    ),
    151: (
        "O5.2 Memory profiling: Record peak memory and relate AbitoRank's use of latest allowances only to "
        "a sparser graph and a smaller footprint than transfer-based graphs.",
        "요청: Turnitin AI 탐지 완화 — O5.2 재작성",
    ),
    152: (
        "O5.3 Convergence stability: Count iterations to a fixed tolerance (for example 10⁻⁶) under "
        "several damping factors and token-supply scales, and check",
        "요청: Turnitin AI 탐지 완화 — O5.3 재작성 (이어서 다음 문단)",
    ),
    156: (
        "that AbitoRank stays numerically stable even when allowance values are large.",
        "요청: Turnitin AI 탐지 완화 — O5.3 후속 문장 재작성",
    ),
    157: (
        "Taken together, these objectives test whether a latest-allowance-weighted PageRank can deliver "
        "a scalable, trust-aligned reputation score—AbitoRank—that matches or improves on "
        "transfer-value methods without paying a time-decay overhead.",
        "요청: Turnitin AI 탐지 완화 — Objectives 마무리 재작성 (분할 통합)",
    ),
    158: (
        "",
        "요청: Turnitin AI 탐지 완화 — 앞 문단으로 병합되어 본문 비움",
    ),
    # Chapter 3 Literature
    165: (
        "Graph methods entered on-chain reputation work early, mostly as adaptations of PageRank. "
        "Do et al. (2019) sketched the idea; later studies applied it more systematically to Ethereum. "
        "In Do et al. (2023), addresses are nodes, transfers are directed edges, and PageRank produces "
        "a social credit-style score. The motivation is practical: as DeFi grows, protocols need some "
        "way to rank counterparties for unsecured lending and user protection. An address scores higher "
        "when it is linked by many, or by large, incoming transfers—the same intuition that makes "
        "heavily linked web pages important. Some industrial designs, including the Colendi-style "
        "\"social connectivity strength\" metric, fold frequency and bilateral activity into edge "
        "weights before a PageRank-like iteration.",
        "요청: Turnitin AI 탐지 완화 — Ch.3 그래프 평판 도입 재작성",
    ),
    167: (
        "Edge weighting is the first design choice. Equal weights for every transfer are simple, but later "
        "work prefers value-weighted edges so that large transfers count as stronger ties.",
        "요청: Turnitin AI 탐지 완화 — Ch.3 엣지 가중 문단 재작성 (분할)",
    ),
    171: (
        "Do et al. also explore a HodgeRank reading in which ETH transferred becomes the edge weight and "
        "a global ranking is solved from those flows. High-value links are treated as stronger stakes "
        "between parties. Structure still matters: Ethereum graphs contain sinks and isolated clusters "
        "that can trap rank. Damping, as in classical PageRank, is used to limit that inflation so scores "
        "reflect participation in the wider network rather than activity inside a closed clique.",
        "요청: Turnitin AI 탐지 완화 — Ch.3 HodgeRank/구조 문단 재작성",
    ),
    173: (
        "Vanilla PageRank is not enough on its own. Imig (2023) showed that an unmodified Ethereum "
        "PageRank could not separate a known problematic address from a known trustworthy one. Later "
        "models therefore add risk signals. RiskProp, for example, attaches a de-anonymity score and "
        "propagates risk over directed bipartite graphs. In reported evaluations it flagged many "
        "known high-risk accounts that connectivity alone would have missed. That line of work treats "
        "the transaction graph less as a pure prestige ranking and more as a credit-risk network.",
        "요청: Turnitin AI 탐지 완화 — Ch.3 PageRank 한계/RiskProp 재작성",
    ),
    175: (
        "Time also enters most reputation designs. Creditworthiness drifts, so many models down-weight "
        "old interactions. Li et al. (2024), in a reputation-based consensus setting, apply exponential "
        "decay so that recent behaviour dominates. Other systems simply age out edges.",
        "요청: Turnitin AI 탐지 완화 — Ch.3 시간감쇠 문단 재작성 (분할)",
    ),
    179: (
        "Decay helps against whitewashing—letting old good behaviour mask later abuse—but the trade-off "
        "is real. Aggressive decay erases long-lived trust; weak decay leaves stale links in force.",
        "요청: Turnitin AI 탐지 완화 — Ch.3 감쇠 트레이드오프 재작성",
    ),
    183: (
        "Alongside graph scores, supervised models treat wallet histories as feature sets for default "
        "prediction. Wolf et al. (2022) build an Aave credit score in that style. Features mirror "
        "traditional credit-report categories—payment history, amounts owed, length of history, new "
        "credit, and credit mix—but are derived from on-chain behaviour. A tree-based classifier "
        "estimates the chance that a position becomes delinquent (for example, falls below collateral "
        "requirements and faces liquidation). Their results suggest borrowers can be ranked by risk "
        "well enough to support discussion of under-collateralised lending, and they released an open "
        "Aave health-factor dataset to support follow-on work.",
        "요청: Turnitin AI 탐지 완화 — Ch.3 Wolf 등 ML 신용 재작성",
    ),
    185: (
        "Other projects cast on-chain activity as features for trust or credit scores. Hassija et al. "
        "(2020) combine blockchain settlement with prospect-theory weighting so gains and losses are "
        "not treated symmetrically; the score updates as lending outcomes arrive and is intended to "
        "run as a smart-contract process.",
        "요청: Turnitin AI 탐지 완화 — Ch.3 Hassija 문단 재작성 (분할)",
    ),
    189: (
        "Under that weighting, defaults can be penalised more heavily than repayments are rewarded, "
        "which may better match observed risk attitudes. Jain et al. (2019) describe Bit-Score, an "
        "Ethereum design aimed at underbanked users: a self-sovereign identity layer aggregates "
        "financial and non-financial signals on-chain. The point for this review is methodological—"
        "alternative data can sit beside transaction history in a decentralised credit assessment.",
        "요청: Turnitin AI 탐지 완화 — Ch.3 prospect theory/Bit-Score 재작성",
    ),
    191: (
        "Industry Initiatives and Non-Scholarly Perspectives",
        "요청: Turnitin AI 탐지 완화 — 제목 소프트하이픈 제거",
    ),
    192: (
        "Industry systems show that the demand is already commercial, even when the methods are not "
        "peer-reviewed. Cred Protocol's Cred Score (roughly 300–1000, FICO-like) estimates liquidation "
        "or default risk for Ethereum addresses, including wallets with no prior borrow history. "
        "Public materials describe a large feature set drawn from many EVM chains and protocols—"
        "loan and repayment history, balances, debt ratios, yield-farming behaviour, protocol "
        "diversity, and sometimes governance participation. Partners have discussed blending "
        "off-chain data and using Cred-style scores inside Aave-related products for "
        "under-collateralised lending experiments.",
        "요청: Turnitin AI 탐지 완화 — Ch.3 Cred Protocol 문단 재작성",
    ),
    197: (
        "3Jane's Jane Score is a hybrid. It combines on-chain scores (Cred and Blockchain Bureau) with "
        "conventional bureau inputs such as TransUnion and Equifax / VantageScore-style factors, then "
        "exposes a composite 300–1000 score on-chain with privacy protections (including "
        "zero-knowledge constructions in the protocol design). The product is useful here less as a "
        "citation of academic novelty and more as evidence of which signals practitioners already "
        "treat as credit-relevant.",
        "요청: Turnitin AI 탐지 완화 — Ch.3 Jane Score 문단 재작성",
    ),
    199: (
        "Those products also mark the gap AbitoRank addresses. They lean on realised transfers, "
        "balances, and liquidations. They do not treat ERC-20 approve/permit links as first-class "
        "graph edges. An approval that lets B spend A's tokens is a standing exposure: if B is "
        "malicious or compromised, A's funds can move without a fresh transfer from A. Transfer-only "
        "graphs miss that permission structure. AbitoRank puts approve/permit edges into the "
        "reputation graph as directed weighted links that can move PageRank mass.",
        "요청: Turnitin AI 탐지 완화 — Ch.3 연구 공백 재작성 (분할 통합)",
    ),
    203: (
        "In that formulation, a large approval from A to B can raise B's score in the same way an "
        "inbound citation raises a page's rank, while A's exposure to B remains part of the "
        "relationship the score is meant to capture. Approvals often precede spending or mark "
        "delegated control; both matter for creditworthiness and are invisible to transfer-only models.",
        "요청: Turnitin AI 탐지 완화 — Ch.3 AbitoRank 그래프 해석 재작성",
    ),
    205: (
        "AbitoRank also handles time differently. Many scores decay old interactions. For approvals we "
        "argue against that default. An allowance stays live until it is changed or revoked; a "
        "year-old permission is still relevant if the allowance remains nonzero. Keeping that weight "
        "preserves long-lived financial relationships that a short memory window would erase. For "
        "transfers, ageing a payment from years ago can be reasonable. For approvals, the risk lasts "
        "as long as the authorisation does. Prior PageRank work either omitted these edges or did not "
        "treat their persistence explicitly. Combining approval networks with PageRank under that "
        "no-decay rule is intended to yield a stabler on-chain reputation reading—one that tracks "
        "both value flow and delegated spending rights.",
        "요청: Turnitin AI 탐지 완화 — Ch.3 시간감쇠 없음 논거 재작성",
    ),
    207: (
        "Overall, the literature moves from simple graph prestige scores toward richer ML credit models. "
        "PageRank-style methods stay attractive because the network story is transparent; ML methods "
        "are attractive because they predict defaults from many features. The open problem is to bring "
        "a meaningful graph feature—ERC-20 approval links—into a score that remains both explainable "
        "and predictive.",
        "요청: Turnitin AI 탐지 완화 — Ch.3 요약 재작성 (분할)",
    ),
    211: (
        "AbitoRank is our attempt at that bridge. It takes seriously who authorises whom, not only who "
        "pays whom, and it refuses to discard long-lived approvals merely because they are old. That "
        "stance answers a concrete gap in prior academic and industry designs and matches the practical "
        "need already visible in systems such as Cred Score and Jane Score: better on-chain signals for "
        "undercollateralised DeFi credit.",
        "요청: Turnitin AI 탐지 완화 — Ch.3 마무리 재작성",
    ),
    # Chapter 4
    235: (
        "The comparison between AbitoRank and Adaptive Weighted PageRank (AWP) rests on three constructs: "
        "Reputation Structure, Risk Predictive Validity, and Computational Efficiency. The framing draws "
        "on hyperlink-citation ideas from PageRank, on predictive validity as used in credit scoring, "
        "and on basic computational complexity. Each construct maps to the variables in Section 1.2.2 "
        "and supports a testable hypothesis.",
        "요청: Turnitin AI 탐지 완화 — Ch.4 이론틀 도입 재작성",
    ),
    249: (
        "H1 (Divergence): AbitoRank and AWP will produce meaningfully different wallet orderings, "
        "showing that an approve/permit endorsement graph is not just a noisier copy of a transfer graph.",
        "요청: Turnitin AI 탐지 완화 — H1 재작성",
    ),
    250: (
        "H2 (Predictive Validity): AbitoRank scores will track actual default events more closely than "
        "AWP scores.",
        "요청: Turnitin AI 탐지 완화 — H2 재작성",
    ),
    251: (
        "H3 (Computational Efficiency): AbitoRank will use less runtime and memory, and fewer iterations "
        "to converge, than AWP on the same workload.",
        "요청: Turnitin AI 탐지 완화 — H3 재작성 (괄호 닫힘 포함)",
    ),
    254: (
        "Hyperlink–citation semantics: Page et al. (1998) treat an inbound hyperlink as a citation-like "
        "vote. An ERC-20 approve/permit from wallet A to wallet B can be read the same way—as a trust "
        "citation—so PageRank on an approval graph is theoretically natural.",
        "요청: Turnitin AI 탐지 완화 — Ch.4 hyperlink 정당화 재작성",
    ),
    255: (
        "Predictive validity: In psychometrics and credit scoring, a metric is useful when it forecasts "
        "outcomes that matter.",
        "요청: Turnitin AI 탐지 완화 — Ch.4 predictive validity 도입 재작성",
    ),
    259: (
        "We therefore treat AbitoRank and AWP scores as candidate scales and compare them with AUC, "
        "precision, recall, and F1 against default labels.",
        "요청: Turnitin AI 탐지 완화 — Ch.4 예측 지표 문단 재작성",
    ),
    260: (
        "Computational complexity: Each PageRank iteration costs O(|E|) work on the edge set. "
        "Approve/permit graphs are expected to be sparser than transfer graphs, which should cut "
        "per-iteration cost, speed convergence, and reduce memory.",
        "요청: Turnitin AI 탐지 완화 — Ch.4 복잡도 문단 재작성",
    ),
    263: (
        "Measurement: Score matched Aave wallets with AbitoRank and AWP, record defaults over a fixed "
        "window, and profile runtime, peak memory, and iterations to convergence for each algorithm.",
        "요청: Turnitin AI 탐지 완화 — Ch.4 Measurement 재작성",
    ),
    268: (
        "Contribution: Linking the hypotheses to these established ideas keeps the empirical tests "
        "interpretable: we are asking whether AbitoRank is structurally different, predictively useful, "
        "and cheaper to run—not merely whether another score can be invented.",
        "요청: Turnitin AI 탐지 완화 — Ch.4 Contribution 재작성",
    ),
    # Chapter 5
    276: (
        "This chapter sets out how AbitoRank will be implemented, how AWP will be reproduced, and how "
        "the two will be compared on reputation structure, predictive validity, and computational cost.",
        "요청: Turnitin AI 탐지 완화 — Ch.5 도입 재작성",
    ),
    281: (
        "Ethereum Mainnet, 1 January 2025 – 30 June 2025, via Google BigQuery or an archive node.",
        "요청: Turnitin AI 탐지 완화 — 데이터 기간 문장 정리",
    ),
    288: (
        "All active wallets in scope for predictive analysis; a random 100,000-wallet subsample for "
        "compute benchmarks.",
        "요청: Turnitin AI 탐지 완화 — Sampling 재작성",
    ),
    305: (
        "Python with NetworkX or GraphFrames; SciPy sparse solvers; Docker for reproducible runs.",
        "요청: Turnitin AI 탐지 완화 — Tools 재작성",
    ),
    312: (
        "Validation: 5-fold cross-validation with mean ± SD.",
        "요청: Turnitin AI 탐지 완화 — Validation 문장 정리",
    ),
    314: (
        "Compute Spearman's ρ and Kendall's τ between AbitoRank and AWP.",
        "요청: Turnitin AI 탐지 완화 — Rank divergence 지표 정리",
    ),
    329: (
        "Test whether rank correlations differ significantly from 1 (one-sample t-test or Wilcoxon "
        "signed-rank, as appropriate).",
        "요청: Turnitin AI 탐지 완화 — H1 검정 재작성",
    ),
    331: (
        "Compare AUCs with DeLong's test for correlated ROC curves.",
        "요청: Turnitin AI 탐지 완화 — H2 AUC 검정 정리",
    ),
    332: (
        "Compare precision, recall, and F1 with paired bootstrap confidence intervals.",
        "요청: Turnitin AI 탐지 완화 — H2 분류지표 검정 재작성",
    ),
    334: (
        "Paired t-tests (or Wilcoxon tests if distributions are non-normal) on runtime, memory, and "
        "iteration counts.",
        "요청: Turnitin AI 탐지 완화 — H3 검정 재작성",
    ),
    343: (
        "The procedures above are meant to keep the AbitoRank–AWP comparison reproducible on structure, "
        "risk prediction, and compute cost.",
        "요청: Turnitin AI 탐지 완화 — Ch.5 마무리 재작성",
    ),
    # Chapter 6
    349: (
        "Several limits and validity threats remain even if the evaluation is careful:",
        "요청: Turnitin AI 탐지 완화 — Ch.6 도입 재작성",
    ),
    351: (
        "Event completeness: We depend on public Approve, Permit, and Transfer logs from archives or "
        "BigQuery. Missing or misindexed events (reorgs, sync gaps) can bias the graph.",
        "요청: Turnitin AI 탐지 완화 — 데이터 완전성 한계 재작성",
    ),
    352: (
        "Label noise: Defaults are inferred from Aave V3 liquidations. Wallets that become insolvent "
        "without an on-chain liquidation (for example through off-chain settlement) will be mislabelled.",
        "요청: Turnitin AI 탐지 완화 — 라벨 노이즈 한계 재작성",
    ),
    354: (
        "Fixed window: A single six-month slice may miss regime shifts. Results could change in other "
        "periods, especially around high volatility or major protocol upgrades.",
        "요청: Turnitin AI 탐지 완화 — 시간 범위 한계 재작성",
    ),
    356: (
        "Approval semantics: We treat any nonzero approve/permit as a meaningful endorsement. In practice, "
        "users often grant unlimited \"spend-all\" approvals, or route through custodial contracts, which "
        "weakens the trust reading of an edge.",
        "요청: Turnitin AI 탐지 완화 — 승인 의미 한계 재작성 (분할 통합)",
    ),
    360: (
        "",
        "요청: Turnitin AI 탐지 완화 — 앞 문단으로 병합되어 본문 비움",
    ),
    361: (
        "Edge weight aggregation: Summing transfers, or keeping only the latest allowance, ignores fund "
        "provenance and can hide multi-token or multi-chain structure.",
        "요청: Turnitin AI 탐지 완화 — 엣지 집계 한계 재작성",
    ),
    363: (
        "Fixed damping: We use d = 0.85 everywhere. The better choice may depend on token, wallet type, "
        "or network segment.",
        "요청: Turnitin AI 탐지 완화 — damping 한계 재작성",
    ),
    364: (
        "Unmodeled attributes: AbitoRank ignores off-chain factors (KYC, geolocation) and non-ERC-20 "
        "relations (NFT approvals, bridges) that may also signal trust.",
        "요청: Turnitin AI 탐지 완화 — 미모델링 속성 한계 재작성",
    ),
    366: (
        "Protocol specificity: Default labels come from Aave V3. Predictive strength may differ on "
        "Compound, MakerDAO, or non-lending settings.",
        "요청: Turnitin AI 탐지 완화 — 프로토콜 일반화 한계 재작성",
    ),
    367: (
        "Asset bias: High-volume tokens such as USDC and WETH dominate the graph; thin tokens may yield "
        "endorsement networks too sparse for stable PageRank.",
        "요청: Turnitin AI 탐지 완화 — 자산 편향 한계 재작성",
    ),
    369: (
        "Gaming and Sybil risk: Attackers can create dummy approvals or circular allowance patterns to "
        "inflate scores. Detecting and blocking those strategies is outside the present scope.",
        "요청: Turnitin AI 탐지 완화 — Sybil 한계 재작성",
    ),
    371: (
        "Scalability: Even if AbitoRank beats AWP on our sample, scoring the full Ethereum wallet set "
        "(millions of nodes) may still need distributed compute or approximation.",
        "요청: Turnitin AI 탐지 완화 — 확장성 한계 재작성 (분할 통합)",
    ),
    375: (
        "",
        "요청: Turnitin AI 탐지 완화 — 앞 문단으로 병합되어 본문 비움",
    ),
    # Chapter 7
    381: (
        "Ethics Considerations",
        "요청: Turnitin AI 탐지 완화 — Ethics 제목 공백 정리",
    ),
    383: (
        "The study uses only public blockchain data, but public data still requires restraint:",
        "요청: Turnitin AI 탐지 완화 — Ch.7 도입 재작성",
    ),
    384: (
        "Privacy and Anonymity",
        "요청: AI 탐지 완화 재작성 — 제목 오타 Annonymity → Anonymity",
    ),
    385: (
        "Pseudonymity: Ethereum addresses are not legal identities. We will not attempt to deanonymise "
        "addresses or link them to personally identifying information.",
        "요청: Turnitin AI 탐지 완화 — 가명성 항목 재작성",
    ),
    386: (
        "No sensitive off-chain collection: Analysis is limited to on-chain approve, permit, transfer, "
        "and liquidation events. IP addresses and KYC records are out of scope.",
        "요청: Turnitin AI 탐지 완화 — 민감정보 항목 재작성",
    ),
    388: (
        "Open data sources: Queries will use public datasets (for example Google BigQuery, The Graph) "
        "within their terms and rate limits.",
        "요청: Turnitin AI 탐지 완화 — 데이터 이용 항목 재작성",
    ),
    389: (
        "No disruptive interaction: We will not broadcast transactions or stress smart contracts in ways "
        "that could harm network operation.",
        "요청: Turnitin AI 탐지 완화 — 비악의적 상호작용 항목 재작성",
    ),
    394: (
        "Algorithmic fairness: We will check whether AbitoRank or AWP systematically undervalues new "
        "or low-volume wallets, and discuss any such bias in the analysis.",
        "요청: Turnitin AI 탐지 완화 — 공정성 항목 재작성",
    ),
    395: (
        "Transparency: Code, parameters, and metrics will be documented and published for audit and "
        "replication.",
        "요청: Turnitin AI 탐지 완화 — 투명성 항목 재작성",
    ),
    397: (
        "Vulnerability reporting: If the analysis surfaces exploitable approval patterns in live "
        "protocols, we will notify the relevant teams before any public write-up.",
        "요청: Turnitin AI 탐지 완화 — 책임 공개 항목 재작성",
    ),
    399: (
        "No financial advice: AbitoRank may inform risk discussion, but it is not investment or lending "
        "advice; human oversight remains necessary.",
        "요청: Turnitin AI 탐지 완화 — 금융조언 부인 재작성",
    ),
    400: (
        "Misuse awareness: We will discuss Sybil-style gaming and suggest safeguards so the method is "
        "harder to turn against particular users.",
        "요청: Turnitin AI 탐지 완화 — 오용 방지 항목 재작성",
    ),
    401: (
        "These commitments are intended to keep the work privacy-respecting and usable by DeFi "
        "practitioners without pretending that a public ledger removes ethical obligations.",
        "요청: Turnitin AI 탐지 완화 — Ch.7 마무리 재작성",
    ),
    # Chapter 8
    409: (
        "The expected contribution sits in four places.",
        "요청: Turnitin AI 탐지 완화 — Ch.8 도입 재작성",
    ),
    411: (
        "Endorsement-based graph modelling: Building a directed weighted graph from ERC-20 approve and "
        "permit events extends the PageRank citation analogy to explicit on-chain authorisations, not "
        "only to transfers.",
        "요청: Turnitin AI 탐지 완화 — 이론적 기여 1 재작성",
    ),
    412: (
        "Temporal simplification: Instead of engineering a decay function, AbitoRank relies on the "
        "override semantics of allowances. That is a simpler model of enduring trust, and it matches "
        "how approvals actually persist on-chain.",
        "요청: Turnitin AI 탐지 완화 — 이론적 기여 2 재작성",
    ),
    413: (
        "Methodological Contribution",
        "요청: AI 탐지 완화 재작성 — 제목 오타 Constribution → Contribution",
    ),
    414: (
        "Efficient computation: If a sparser approval graph matches or beats transfer-based PageRank on "
        "prediction while cutting time, memory, and iterations, large-scale reputation scoring becomes "
        "more realistic for resource-limited DeFi teams.",
        "요청: Turnitin AI 탐지 완화 — 방법론 기여 1 재작성 (분할 통합)",
    ),
    418: (
        "",
        "요청: Turnitin AI 탐지 완화 — 앞 문단으로 병합되어 본문 비움",
    ),
    419: (
        "Reproducible pipeline: The extraction, PageRank, and evaluation steps will be specified and "
        "released so others can re-run or adapt AbitoRank on other protocols.",
        "요청: Turnitin AI 탐지 완화 — 재현 파이프라인 기여 재작성",
    ),
    421: (
        "Risk management: Better separation of risky wallets could support lower collateral for "
        "stronger counterparties and more inclusive under-collateralised products—if the empirical "
        "results hold.",
        "요청: Turnitin AI 탐지 완화 — 실무 영향 1 재작성",
    ),
    422: (
        "Protocol integration: Because AbitoRank is comparatively light, it is a plausible input to "
        "risk oracles, governance dashboards, and compliance tooling.",
        "요청: Turnitin AI 탐지 완화 — 실무 영향 2 재작성",
    ),
    424: (
        "Cross-protocol reach: The same allowance-graph idea applies to other ERC-20 networks and to "
        "many L2 environments, not only Ethereum mainnet and Aave.",
        "요청: Turnitin AI 탐지 완화 — 일반화 함의 재작성",
    ),
    425: (
        "Future work: Highlighting authorisation networks invites later use of governance votes, "
        "staking approvals, and bridge permissions inside composite reputation systems.",
        "요청: Turnitin AI 탐지 완화 — 후속연구 함의 재작성",
    ),
    # Chapter 9
    431: (
        "Table 9.1 gives a 20-month plan with milestones and deliverables through February 2027.",
        "요청: Turnitin AI 탐지 완화 — Schedule 도입 재작성",
    ),
}

# Table cell rewrites: (table_idx, row, col) -> (text, comment)
TABLE_REWRITES: dict[tuple[int, int, int], tuple[str, str]] = {
    (0, 1, 1): (
        "How a ranking orders wallets relative to one another.",
        "요청: Turnitin AI 탐지 완화 — Table 4.1 Reputation Structure 정의 재작성",
    ),
    (0, 3, 1): (
        "How well a reputation score forecasts observed default events on a DeFi platform.",
        "요청: Turnitin AI 탐지 완화 — Table 4.1 Predictive Validity 정의 재작성",
    ),
    (0, 4, 1): (
        "Time, memory, and iterations needed to compute scores.",
        "요청: Turnitin AI 탐지 완화 — Table 4.1 Efficiency 정의 재작성",
    ),
}


def set_paragraph_text(paragraph, text: str) -> None:
    """Replace paragraph text while keeping pPr / first-run formatting."""
    if not paragraph.runs:
        paragraph.add_run(text)
        return
    first = paragraph.runs[0]
    # Clear all run texts
    for i, run in enumerate(paragraph.runs):
        run.text = text if i == 0 else ""
    # If somehow empty after, ensure first has text
    if paragraph.runs[0].text != text:
        paragraph.runs[0].text = text
    # Remove leftover empty runs beyond the first to reduce XML noise (keep first)
    # Safer: leave empty runs; Word handles them.


def ensure_comments_part(docx_path: Path) -> None:
    """Ensure comments.xml exists and is related from document.xml."""
    tmp = docx_path.with_suffix(".comments_fix.docx")
    with zipfile.ZipFile(docx_path, "r") as zin, zipfile.ZipFile(
        tmp, "w", compression=zipfile.ZIP_DEFLATED
    ) as zout:
        names = set(zin.namelist())
        ct = etree.fromstring(zin.read("[Content_Types].xml"))
        rels = etree.fromstring(zin.read("word/_rels/document.xml.rels"))

        if "word/comments.xml" not in names:
            comments = etree.Element(
                qn("w:comments"),
                nsmap={"w": W_NS, "w14": W14_NS},
            )
            # written below
        else:
            comments = etree.fromstring(zin.read("word/comments.xml"))

        # Content types
        if not any(
            el.get("PartName") == "/word/comments.xml" for el in ct
        ):
            etree.SubElement(
                ct,
                "{%s}Override" % CT_NS,
                PartName="/word/comments.xml",
                ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml",
            )

        # Relationship
        if not any(el.get("Type") == REL_COMMENTS for el in rels):
            used = {el.get("Id") for el in rels}
            rid = "rIdComments"
            n = 90
            while rid in used:
                rid = f"rId{n}"
                n += 1
            etree.SubElement(
                rels,
                "{%s}Relationship" % REL_NS,
                Id=rid,
                Type=REL_COMMENTS,
                Target="comments.xml",
            )

        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "[Content_Types].xml":
                data = etree.tostring(
                    ct, xml_declaration=True, encoding="UTF-8", standalone=True
                )
            elif item.filename == "word/_rels/document.xml.rels":
                data = etree.tostring(
                    rels, xml_declaration=True, encoding="UTF-8", standalone=True
                )
            elif item.filename == "word/comments.xml":
                continue  # rewrite below
            zout.writestr(item, data)

        if "word/comments.xml" not in names:
            comments = etree.Element(
                "{%s}comments" % W_NS,
                nsmap={"w": W_NS},
            )
        zout.writestr(
            "word/comments.xml",
            etree.tostring(
                comments, xml_declaration=True, encoding="UTF-8", standalone=True
            ),
        )

    shutil.move(str(tmp), str(docx_path))


def next_comment_id(comments_root) -> int:
    ids = [
        int(c.get(qn("w:id")))
        for c in comments_root.findall(qn("w:comment"))
        if c.get(qn("w:id")) is not None
    ]
    return (max(ids) + 1) if ids else 0


def add_comment_element(comments_root, cid: int, text: str) -> None:
    c = OxmlElement("w:comment")
    c.set(qn("w:id"), str(cid))
    c.set(qn("w:author"), AUTHOR)
    c.set(qn("w:date"), COMMENT_DATE)
    c.set(qn("w:initials"), INITIALS)
    p = OxmlElement("w:p")
    r0 = OxmlElement("w:r")
    r0.append(OxmlElement("w:annotationRef"))
    p.append(r0)
    r = OxmlElement("w:r")
    t = OxmlElement("w:t")
    if text.startswith(" ") or text.endswith(" ") or "  " in text:
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    t.text = text
    r.append(t)
    p.append(r)
    c.append(p)
    comments_root.append(c)


def wrap_paragraph_comment(paragraph, cid: int) -> None:
    p = paragraph._p
    # skip if already commented
    if p.find(qn("w:commentRangeStart")) is not None:
        return
    start = OxmlElement("w:commentRangeStart")
    start.set(qn("w:id"), str(cid))
    end = OxmlElement("w:commentRangeEnd")
    end.set(qn("w:id"), str(cid))
    ref_r = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    style = OxmlElement("w:rStyle")
    style.set(qn("w:val"), "CommentReference")
    rpr.append(style)
    ref_r.append(rpr)
    ref = OxmlElement("w:commentReference")
    ref.set(qn("w:id"), str(cid))
    ref_r.append(ref)
    p.insert(0, start)
    p.append(end)
    p.append(ref_r)


def set_cell_text(cell, text: str) -> None:
    # Put all text in first paragraph; clear others' text
    if not cell.paragraphs:
        return
    set_paragraph_text(cell.paragraphs[0], text)
    for p in cell.paragraphs[1:]:
        for run in p.runs:
            run.text = ""


def main() -> None:
    if not SRC.exists():
        raise FileNotFoundError(SRC)

    shutil.copy2(SRC, BACKUP)
    print(f"Backup: {BACKUP}")

    ensure_comments_part(SRC)

    doc = Document(str(SRC))

    # Load comments part via package
    comments_part = None
    for rel in doc.part.rels.values():
        if rel.reltype == REL_COMMENTS:
            comments_part = rel.target_part
            break
    if comments_part is None:
        raise RuntimeError("comments part missing after ensure_comments_part")

    comments_root = comments_part.element
    cid = next_comment_id(comments_root)
    changed = 0

    for idx, (text, comment) in REWRITES.items():
        if idx >= len(doc.paragraphs):
            print(f"SKIP missing para {idx}")
            continue
        p = doc.paragraphs[idx]
        old = p.text
        if old == text:
            # still add comment if not present? skip
            continue
        set_paragraph_text(p, text)
        add_comment_element(comments_root, cid, comment)
        wrap_paragraph_comment(p, cid)
        cid += 1
        changed += 1

    for (ti, ri, ci), (text, comment) in TABLE_REWRITES.items():
        cell = doc.tables[ti].rows[ri].cells[ci]
        if cell.text.strip() == text.strip():
            continue
        set_cell_text(cell, text)
        # comment on first paragraph of cell
        add_comment_element(comments_root, cid, comment)
        wrap_paragraph_comment(cell.paragraphs[0], cid)
        cid += 1
        changed += 1

    try:
        doc.save(str(OUT))
    except PermissionError:
        alt = OUT.with_name(OUT.stem + "_humanized.docx")
        doc.save(str(alt))
        print(f"PermissionError on {OUT}; saved to {alt}")
        OUT_USED = alt
    else:
        OUT_USED = OUT
        print(f"Saved: {OUT_USED}")

    # Validate
    with zipfile.ZipFile(OUT_USED) as z:
        bad = z.testzip()
        assert bad is None, bad
        assert "word/comments.xml" in z.namelist()
        root = etree.fromstring(z.read("word/comments.xml"))
        authors = {
            c.get(qn("w:author"))
            for c in root.findall(qn("w:comment"))
        }
        n_comments = len(root.findall(qn("w:comment")))
        print(f"comments={n_comments}, authors={authors}, changed={changed}")
        assert authors == {AUTHOR} or (AUTHOR in authors and len(authors) == 1)

    # Spot-check a few rewritten paragraphs
    doc2 = Document(str(OUT_USED))
    assert "PHILOSOPHY" in doc2.paragraphs[11].text
    assert doc2.paragraphs[29].text.strip() == "Abstract"
    assert "We propose AbitoRank" in doc2.paragraphs[35].text
    assert "Quatitative" not in doc2.paragraphs[142].text
    assert "Anonymity" in doc2.paragraphs[384].text
    print("Spot checks OK")
    print(f"OUT={OUT_USED}")


if __name__ == "__main__":
    main()
