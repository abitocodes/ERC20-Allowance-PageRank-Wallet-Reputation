# Data: Integrating ERC-20 Allowance Edges into PageRank for Enhanced On-Chain Wallet Reputation Scoring

This folder holds the blockchain data of the doctoral dissertation above (UNISA). The code that
extracted and analysed it, and the dissertation itself, are in the public repository
https://github.com/abitocodes/phd_works, folder
`1-Dissertation-Works/ERC20-Allowance-PageRank-Wallet-Reputation/`.

All data come from Arbitrum One, 2023-10-01 to 2026-09-30, extracted from the public BigQuery
table `bigquery-public-data.goog_blockchain_arbitrum_one_us.logs`. Token prices are DefiLlama
daily closes.

## Folders

| Folder | Contents | Repository path |
|--------|----------|-----------------|
| `contract-reputation/` | Data of the dissertation | `experiments/data/` |
| `contract-reputation/0-usd-token-list-and-prices/` | Token candidates, the listed tokens, daily USD prices, Chainlink cross-check | same |
| `contract-reputation/1-raw-blockchain-extracts/` | Cohort and GMX extracts; `graph-tables/` (registered analysis, raw base units, 6.4 GB) and `graph-tables-usd/` (revised analysis, USD, 2.6 GB): node ids, allowance and transfer edge tables at two cut-off dates, proxy metrics, labels | same |
| `contract-reputation/2-processed-tables-and-evaluations/` | Scores, evaluation summaries, decoded GMX closes | same |
| `contract-reputation/3-published-results-for-thesis/` | Summaries behind every table of the dissertation, with `SHA256SUMS.txt` | same |
| `wallet-reputation-archive/` | Data of the earlier wallet-reputation study that preceded the dissertation (archived, not used in its results) | `archive/wallet-reputation-experiments/data/` |

Large tables are split into parquet parts below 90 MB (`<table>.part000.parquet`, ...); the
`<table>.json` next to them records the source BigQuery table, row count and parts.

## Fetching the files with the repository

`experiments/drive-manifest.json` in the repository lists every file here with its Drive id,
size and MD5. From `experiments/`:

```bash
python scripts/drive_sync.py pull "*graph-tables-usd/*"   # the revised (main) analysis
python scripts/drive_sync.py pull --all                   # everything
```

The script needs only Python 3.10+ and checks the MD5 of every file it downloads.
