# Extended baselines (archived)

These tables were removed from the main dissertation draft when the narrative
focused on **three methods**: EndorseRank, AWP, and GF-PR.

## Contents

| File | Description |
|------|-------------|
| `tables/alignment-seven-methods.tex` | 7-method proxy-family matrix (LP-PR, CW-AWP, LF-PR, RiskProp, …) |
| `tables/alignment-six-aave-methods.tex` | 6-method Aave W↔W PageRank baselines |

CSV exports live under
`1-Dissertation-Works/ERC20-Allowance-PageRank-Wallet-Reputation/dissertation/wallet-reputation-experiments/data/4-archived-extended-baselines/`.

## Regenerate (after `run_dissertation_eval.py --real`)

```powershell
cd 1-Dissertation-Works/ERC20-Allowance-PageRank-Wallet-Reputation/dissertation/wallet-reputation-experiments
python scripts/export_method_matrix.py --preset seven
python scripts/export_method_matrix.py --preset six-aave
```

By default the tables go to this folder (`tables/`) and the CSV files to
`data/4-archived-extended-baselines/`.

Or run `python scripts/run_dissertation_eval.py --real --export-latex` — archive
presets are exported automatically alongside the dissertation tables.
