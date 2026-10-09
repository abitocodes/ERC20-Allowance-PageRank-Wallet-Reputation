# Analysis plan: contract reputation from ERC-20 allowance edges

- Written and committed on 9 October 2026, before any log of this study was extracted.
- Settings live in `config/contract_reputation.yaml`; this plan states what they mean and which results decide which question.
- Sections 1–6 are fixed by this commit. Section 7 (the registered window) is completed and registered in a later commit, before scan B runs.

## 1. Data

- Chain: Arbitrum One (chain ID 42161). Source: `bigquery-public-data.goog_blockchain_arbitrum_one_us.logs`.
- Observation window: 2023-10-01 00:00:00 UTC to 2026-06-30 23:59:59 UTC (33 months). The time decay is anchored at T_obs = 2026-06-30 23:59:59 UTC.
- Events: ERC-20 `Approval` and `Transfer` logs with exactly three topics (ERC-721 logs carry a fourth topic and are excluded), GMX V2 `EventLog1` logs named `PositionDecrease` from the EventEmitter, and Aave V3 pool `Borrow`, `Repay` and `LiquidationCall` logs.
- Scan A materialises these events for the observation window into the project table `contract_rep.logs_obs`; scan B does the same for 2026-07-01 to 2026-09-30 and runs only after section 7 is registered.
- Amounts stay in raw token base units. Addresses are lower-cased.
- Every file written under `data/` is split into parts below 90 MB so that it can be committed to GitHub.

## 2. Account type

An address is a contract when `eth_getCode` at one pinned block returns bytecode that is not an EIP-7702 delegation designator (`0xef0100` followed by 20 bytes). No bytecode, or a designator, makes it an externally owned account (EOA). The pinned block number and the date of the read are recorded with the result.

## 3. Cohorts

- Matched cohort W: every contract that, inside the observation window, received a non-zero `Approval` from at least three distinct owners. It is fixed from the approval logs and the code check alone, before any transfer is aggregated. Only cohort members are scored and evaluated; externally owned accounts enter the graphs as owners, senders and receivers but are never evaluated.
- Extraction filter: an approval is kept when a cohort contract is its owner or its spender; a transfer is kept when a cohort contract is its sender or its recipient. Each graph is therefore the ego network of the cohort.
- Holdout spender cohort (W0): every contract spender that holds at least one positive latest allowance at t1 in the extracted approval data.
- Trader cohort: GMX V2 accounts that are contracts, appear in the freeze-date graph, and close at least three positions in the label window.
- Expanded pool for runtime scaling: deterministic SHA256 subsamples of the cohort (seed `contract-benchmark-v1`); each stage keeps the extracted edges incident to its sampled contracts, so the edge count grows with the stage.

## 4. Scores

All PageRanks use one power-iteration solver: d = 0.85, tolerance 1e-8 (L1), at most 300 iterations, dangling mass returned through the restart distribution.

- AWP (Do, Do and Nguyen, IEEE RIVF 2023): transfer graph; each transfer weighs sigma(Δt)·V(x), sigma(Δt) = 1/(1+exp(k(Δt−t0))) with k = 0.01 and t0 = 180 days, V(z) = 2/(1+exp(−bz))−1 with b = 1 on raw base units; restarts proportional to activeness X_u = Σ_{v≠u} max_e sigma(Δt_e).
- EndorseRank: the latest in-window allowance of each (token, owner, spender), ordered by (block number, log index); a zero allowance deletes the edge; weight sigma(Δt*)·V(a*) summed over tokens; uniform restarts. The variant with AWP's activity restarts is reported beside it.
- C-PR: one walk over a raw-amount allowance layer (Σ_token a*) and a raw-amount transfer layer (Σ_e x_e·sigma(Δt_e)), rows mixed per node with weights λ and 1−λ over the layers in which the node has out-edges; uniform restarts. λ = 0.5 primary, 0.25 and 0.75 sensitivity; λ = 1 and λ = 0 walk one layer alone (C-PR(λ=1), C-PR(λ=0)).
- S-PR: the transfer layer walked with restarts from C-PR(λ=1), restricted to the transfer-layer nodes and renormalised (uniform if that mass is zero).
- Raw degrees: in-approve degree (distinct owners with a positive latest allowance) and transfer in-degree (distinct senders other than the address itself).
- A cohort contract absent from a graph scores 0 under that graph's method; the isolated-node alternative is reported as a sensitivity analysis.

## 5. Checks, labels and statistics

- Same-window families on W: transfer (in-degree including self-transfers, in-value), allowance (in-approve degree, in-approve value), Sybil-adjusted stability (inbound counterparty ratio, transfer tenure in days, active months). Family mean = plain average of the proxies' Kendall tau_b.
- Holdout labels on the spender cohort, counted from 2026-04-01 to 2026-06-30: new owner–spender approval pairs absent from the positive snapshot at t1, and new transfer senders not seen between 2023-10-01 and t1 (self-transfers excluded). Scores and degrees use events up to t1 only, with the decay anchored at t1.
- Statistics: Kendall tau_b and Spearman rho on raw scores; 95% percentile intervals from a paired bootstrap over cohort members, B = 400, seed 42, one index matrix shared by all methods; every comparison is a paired difference on the same resamples; no interpretation thresholds; no p-values.
- Benchmark: one untimed warm-up run (peak memory tracked there), five timed runs; times reported with |V| and |E| of the solver graph.
- Robustness: damping {0.75, 0.85, 0.95}; top-20 token subgraph (largest summed raw amounts, and most rows); isolated-node rule.

## 6. Rule A for the coupled operator (fixed now, before any score exists)

- Primary part, spender holdout W0: C-PR at λ = 0.5 does no worse than C-PR(λ=1) on new approval pairs (95% interval of Δtau contains zero or lies above it) and does better than C-PR(λ=0) on new transfer senders (interval above zero).
- Secondary part, matched cohort, same window: C-PR's point estimate lies inside the 95% interval of the better single layer on the transfer family and on the allowance family, and C-PR exceeds both layers on the Sybil-stability family.
- If the primary part fails, the question whether C-PR beats a walk over either layer alone is answered in the negative. λ is not tuned after any label is seen.

## 7. Registered window W1 (to be completed and registered before scan B)

Scores frozen at 2026-06-30 23:59:59 UTC, labels from 2026-07-01 to 2026-09-30. The decision rule for whether C-PR improves on its transfer layer walked alone, its margin, the trader label and any comparison on outcomes built from neither edge type are written here after the W0 results are known and committed with `registered_window.status: registered` before scan B is run.
