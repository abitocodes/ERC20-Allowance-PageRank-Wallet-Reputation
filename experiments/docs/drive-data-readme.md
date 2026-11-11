# Data: Integrating ERC-20 Allowance Edges into PageRank for Enhanced On-Chain Wallet Reputation Scoring

This folder holds the blockchain data of the doctoral dissertation above (UNISA). The code that
extracted and analysed it, and the dissertation itself, are in the public repository
https://github.com/abitocodes/ERC20-Allowance-PageRank-Wallet-Reputation (the repository paths
below are relative to it; the dissertation's source is its submodule `dissertation/overleaf-github`,
https://github.com/abitocodes/phd-dissertation-draft-en).

All data come from Arbitrum One, 2023-10-01 to 2026-09-30, extracted from the public BigQuery
table `bigquery-public-data.goog_blockchain_arbitrum_one_us.logs`. Token prices are DefiLlama
daily closes. Account types of the main analysis were read with `eth_getCode` from public RPC
endpoints at block 513,216,506.

The dissertation's main analysis is the contract-graph analysis: graphs whose nodes are contracts
only, amounts in US dollars on five tokens, scores from the twelve months before each freeze, and
each allowance counted up to its owner's balance at the freeze. It was defined after the registered
results were known; none of its results is a registered result.

## Folders

| Folder | Contents | Repository path |
|--------|----------|-----------------|
| `contract-reputation/` | Data of the dissertation | `experiments/data/` |
| `contract-reputation/0-usd-token-list-and-prices/` | Token candidates, the listed tokens, daily USD prices, Chainlink cross-check | same |
| `contract-reputation/1-raw-blockchain-extracts/` | Cohort and GMX extracts; graph tables of each analysis (node ids, allowance and transfer edge tables at two cut-off dates, proxy metrics, labels): `graph-tables/` (registered analysis, raw base units, 6.4 GB), `graph-tables-usd/` and `graph-tables-usd-12m/` (US-dollar analyses whose graphs hold user accounts; kept as a record), `graph-tables-contract-12m/` (main analysis: contract graph, capped and uncapped allowance pairs, transfer pairs, cohort members, label split, importance); `contract-types/` (account types of the main analysis) | same |
| `contract-reputation/2-processed-tables-and-evaluations/` | Scores, evaluation summaries, decoded GMX closes; the main analysis is in `revised-contract-12m/` (with the curves of the discovery-order test) | same |
| `contract-reputation/3-published-results-for-thesis/` | Summaries behind every table of the dissertation, with `SHA256SUMS.txt`: the registered analysis at the top, the main analysis in `revised-contract-12m/` (each with its `results_digest.md`) | same |
| `wallet-reputation-archive/` | Data of the earlier wallet-reputation study that preceded the dissertation (archived, not used in its results) | `archive/wallet-reputation-experiments/data/` |

Large tables are split into parquet parts below 90 MB (`<table>.part000.parquet`, ...); the
`<table>.json` next to them records the source BigQuery table, row count and parts.

## Fetching the files with the repository

`experiments/drive-manifest.json` in the repository lists every file here with its Drive id,
size and MD5. From `experiments/`:

```bash
python scripts/drive_sync.py pull "*graph-tables-contract-12m/*"   # graph tables of the main analysis
python scripts/drive_sync.py pull "*revised-contract-12m/*"        # its scores and evaluation outputs
python scripts/drive_sync.py pull --all                   # everything
```

The script needs only Python 3.10+ and checks the MD5 of every file it downloads.
