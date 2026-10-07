# BigQuery Data Acquisition Plan

Technical reference for EndorseRank dissertation evaluation on Arbitrum One.
LaTeX mirrors: `1-Dissertation-Works/ERC20-Allowance-PageRank-Wallet-Reputation/proposal/proposal/02-Content/Chapter-05.tex`, `1-Dissertation-Works/ERC20-Allowance-PageRank-Wallet-Reputation/dissertation/overleaf-github/Chapter-03-Research-Methodology/index.tex`.

## Source

| Item | Value |
|------|-------|
| Dataset | `bigquery-public-data.goog_blockchain_arbitrum_one_us.logs` |
| Chain | Arbitrum One (42161) |
| Observation window | 2025-12-01 00:00 UTC — 2026-05-31 23:59:59 UTC |
| SQL templates | `sql/gmx_event_logs.sql`, `sql/arbitrum_approvals.sql`, `sql/arbitrum_transfers.sql` |

## Data streams

### Stream A — GMX validation labels (Phase 1)

| Field | Detail |
|-------|--------|
| Event | GMX V2 `EventEmitter` `PositionDecrease` |
| Contract | `0xC8ee91A54287DB53897056e12D9819156D3822Fb` |
| Fields | `block_timestamp`, `account`, `basePnlUsd`, `orderType`, `sizeDeltaUsd`, `transaction_hash` |
| Trader ID | Event `account` (not `transaction.from`) |
| Proxies | Close-success count, realized gain proxy, close success rate (wallets with ≥3 closes) |
| Script | `scripts/extract_margin_week.py` |

### Stream B — EndorseRank graph (Phase 2)

| Field | Detail |
|-------|--------|
| Event | ERC-20 `Approval` (topic0 `0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925`) |
| Fields | `token_address`, `owner`, `spender`, `value`, `block_timestamp` |
| Preprocessing | Latest nonzero allowance per (token, owner, spender) |
| Filter | `@wallet_addresses` from Phase 1 qualified wallets (+ benchmark seed wallets) |
| Batches | 6 monthly queries (Dec 2025 — May 2026) |
| Script | `scripts/extract_reputation_data.py` |

### Stream C — AWP baseline graph (Phase 2)

| Field | Detail |
|-------|--------|
| Event | ERC-20 `Transfer` (topic0 `0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef`) |
| Fields | `from_address`, `to_address`, `value`, `block_timestamp` |
| Weights | Logistic time-decay (k=0.01, t₀=180 days) |
| Filter / batches | Same as Stream B |

## Excluded (cost / design)

- Unfiltered 6-month full-chain Approval/Transfer scans (hundreds of TiB)
- `transactions` table (unused)
- Multi-chain data
- Standalone `PositionIncrease` extraction (Decrease suffices for proxies)

## Collection tiers

### Tier 1 — Alignment cohort (required, target $0)

| Item | Scale |
|------|-------|
| GMX `PositionDecrease` | Full 6-month window |
| Alignment wallets n | All wallets with ≥3 GMX closes in window (expected 500–3,000; TBD after extraction) |
| Approval/Transfer | Tier 1 wallet set only, 6 monthly batches × 2 event types |
| Estimated BQ scan | ~80–350 GiB (confirm via `--dry-run`) |
| Cost | Within 1 TiB/month free tier → **$0** |
| Hypotheses | H1 (rank divergence), H2 (GMX alignment) |

### Tier 2 — Benchmark scaling (H3, staged)

| Stage | Wallets | Condition |
|-------|---------|-----------|
| Pilot | 10,000 | Tier 1 dry-run cumulative < 700 GiB |
| Mid | 50,000 | Cumulative < 900 GiB |
| Full | 100,000 | Cumulative < 1 TiB; overage ~$6.25/TiB |

- **Seed:** Tier 1 GMX wallets supplemented by fixed-seed addresses up to `benchmark.target_wallets` (100,000).
- **Implementation:** `extract_reputation_data.py` merges GMX wallets with `benchmark.supplemental_path` (optional parquet of BQ-sampled active addresses) or deterministic `SHA256(seed:i)` padding. Output: `data/2-processed-tables-and-evaluations/extraction_wallet_set.parquet`. Use `--gmx-only` for Tier 1 alignment extraction without benchmark padding.
- **No extra BQ cost for scaling:** Wallet filter reduces returned rows, not partition scan bytes. After Tier 1 extraction, benchmark sizes (10k/50k/100k) are subsampled from local parquet via `benchmark_runtime.py`.

### Tier 3 — Robustness (local only)

- Damping {0.75, 0.85, 0.95}, top-20 token subgraph, raw/log/USD weights: recomputed from Tier 1 parquet without re-querying BigQuery.

## Cost guardrails

| Guard | Value |
|-------|-------|
| Per-query limit | 150 GiB (`config/margin_config.yaml` → `budget.max_bytes_per_query`) |
| Monthly free tier | 1 TiB processed per billing account |
| Overage | ~$6.25/TiB ([BigQuery pricing](https://cloud.google.com/bigquery/pricing)) |
| Mandatory | `--dry-run` before every `--extract` |
| Audit trail | `data/2-processed-tables-and-evaluations/extraction_manifest.json` |
| Fallback | If dry-run exceeds budget, restrict to top-20 ERC-20 tokens by Arbitrum volume (robustness check in proposal §5.2.2) |

## Execution order

```bash
export GOOGLE_CLOUD_PROJECT=your-project-id

# Phase 1
python scripts/extract_margin_week.py --dry-run
python scripts/extract_margin_week.py --extract --yes
python scripts/decode_gmx_events.py
python scripts/compute_rankings.py

# Phase 2
python scripts/extract_reputation_data.py --dry-run
python scripts/extract_reputation_data.py --extract --yes
python scripts/preprocess_arbitrum_allowances.py
python scripts/preprocess_arbitrum_transfers.py
python scripts/compute_reputation_ranks.py

# Phase 3 (local)
python scripts/run_dissertation_eval.py --real --export-latex
python scripts/benchmark_runtime.py
```

## Hypothesis mapping

| Claim | Data required | Tier |
|-------|---------------|------|
| H2: EndorseRank > AWP vs GMX proxies | Streams A + B + C on GMX-qualified wallets | 1 |
| H1: EndorseRank ≠ AWP ordering | Same wallet cohort | 1 |
| H3: EndorseRank faster than AWP | Subgraph benchmark 10k → 50k → 100k | 2 |
| Robustness | Tier 1 parquet, local recompute | 3 |
