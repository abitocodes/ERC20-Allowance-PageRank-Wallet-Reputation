# Exploratory: unlimited allowances and USD balance weights (13 October 2026)

- Post hoc. These checks were chosen and run on 13 October 2026, after every registered and revised result was known. They are not part of the analysis plan, the W1 registration or the revision (`docs/`), and the dissertation does not report them.
- Base: the revised analysis (`CONTRACT_REP_VARIANT=usd`), with its cohorts, labels and paired bootstrap (B = 400, seed from `config/contract_reputation.yaml`). Rerunning the published allowance graph through these scripts reproduces the published values (W0 EndorseRank 0.231, W1 0.234; EndorseRank minus in-approve degree −0.019 and −0.034).
- An allowance is unlimited when its value is at least 1.15e77 base units, as in `scripts/usd.py`.

## Questions and variants

| Variant | Allowance graph | Script |
|---|---|---|
| orig | the published revised graph | all |
| A `fin` | unlimited allowances dropped; a pair keeps its finite allowances | `run_unl.py` |
| B `own` | every allowance of an owner holding at least one unlimited allowance dropped | `run_unl.py` |
| C `unl` | only unlimited allowances kept | `run_unl.py` |
| D `uown` | only owners holding at least one unlimited allowance, with all their allowances | `run_unl.py` |
| `er_usd_bal` | weight σ × USD; an unlimited allowance counts at the owner's balance of the token at the anchor | `run_usd_bal.py` |
| `er_usd_min` | weight σ × min(allowance USD, balance USD) | `run_usd_bal.py` |
| `er_usd_cap` | weight σ × min(allowance USD, 20,000) | `run_usd_bal.py` |
| `er_v_bal`, `er_v_min` | V(z) kept, z = the balance-based amounts above | `run_usd_bal.py` |
| `awp_usd` | AWP with σ × USD (the C-PR transfer layer) and AWP's activity restarts | `run_awp_usd.py` |

## Results (Kendall τ_b, spender holdouts)

New approval pairs, the difference from in-approve degree, and new transfer senders. For orig and A–D the degree is counted on the same graph; for the USD rows it is the published in-approve degree (against the degree of pairs with a positive `er_usd_bal` weight the differences are −0.016 and −0.028):

| Variant | W0 | W1 | W0 − degree | W1 − degree | W0 new senders | W1 new senders |
|---|---|---|---|---|---|---|
| orig | 0.231 | 0.234 | −0.019 | −0.034 | 0.200 | 0.194 |
| A | 0.208 | 0.202 | −0.006 | −0.013 | 0.112 | 0.113 |
| B | 0.191 | 0.192 | −0.012 | −0.015 | 0.110 | 0.111 |
| C | 0.193 | 0.196 | −0.009 | −0.018 | 0.194 | 0.188 |
| D | 0.217 | 0.219 | −0.013 | −0.019 | 0.172 | 0.180 |
| `er_usd_bal` | 0.233 | 0.233 | −0.017 | −0.035 | 0.103 | 0.106 |
| `er_usd_min` | 0.237 | 0.249 | −0.012 | −0.019 | 0.106 | 0.122 |

- No variant ranks spenders better than in-approve degree on the same graph.
- `er_usd_bal` minus orig on new approval pairs: +0.002 [−0.004, +0.009] in W0 and −0.001 [−0.006, +0.004] in W1. `er_usd_min`: +0.007 [−0.001, +0.016] and +0.015 [+0.007, +0.021].
- Raw USD instead of V(z) changes little: on new approval pairs and new senders `er_usd_cap` is within 0.004 of orig, and `awp_usd` within 0.006 of AWP (W0 new senders 0.343 against 0.346).
- At t1, 3,769,894 of the 5,490,386 unlimited allowances (69%) belong to owners with no balance of the token, so they weigh nothing in `er_usd_bal`.
- Unlimited allowances concentrate on widely used spenders (at T_obs the canonical Permit2 address `0x000000000022d473030f116ddee9f6b43ac78ba3` holds 539,403 owner pairs with an unlimited allowance, and the top 100 spenders hold 85% of all such pairs), and a spender's unlimited share correlates positively with its later new approvals (τ ≈ +0.09) and new senders (τ ≈ +0.13).
- Full numbers: `results.json` (A, B and the unlimited-share check), `results_unl.json` (C, D), `results_usd_bal.json`, `results_awp_usd.json`.

## Balances

- Balance of each (token, owner) of a latest allowance at t1 or T_obs = net `Transfer` flow of the five tokens before 2023-10-01 (public Arbitrum logs, from July 2021) + net flow in `logs_obs` up to the anchor. Negative values of a few base units (floating-point error) are set to zero.
- Check (`sql/bal_check.sql`, `scripts/rpc_check.py`): 1,500 sampled pairs carried to 2026-09-30 with `logs_w1` and compared with `balanceOf` at block 514,451,509. 98.1% match, 99.6% of the owners with no transfer in July to September; the rest moved tokens after 30 September. Per-pair result: `bal_check_result.csv`.

## Files

| Path | Content |
|---|---|
| `sql/fin_pairs.sql` | `x_unl_pairs_{t1,tobs}`: per pair, counts and weights of the finite allowances (pairs with an unlimited allowance only) |
| `sql/fin_labels.sql` | `x_unl_labels_{w0,w1}`: new approval pairs of the label window split into finite and unlimited |
| `sql/unl_pairs.sql` | `x_unlonly_pairs_{t1,tobs}`: per pair, weights of the unlimited allowances |
| `sql/bal_pre.sql`, `sql/bal_win.sql` | `x_bal_pre`, `x_bal`: balances at t1 and T_obs |
| `sql/bal_check.sql` | `x_bal_check`: the 1,500-pair sample of the balance check |
| `sql/usd_pairs.sql` | `x_usd_pairs_{t1,tobs}`: USD and balance-based pair weights |
| `sql/bal_win_probe.sql` | cost probe, run as a dry run only |
| `scripts/run_unl.py` | variants A–D; `UNL_VARIANTS` and `UNL_OUT` select the variants and the output name |
| `scripts/run_usd_bal.py`, `scripts/run_awp_usd.py` | the USD variants |
| `scripts/rpc_check.py` | `balanceOf` check of the balance sample |
| `scripts/show.py`, `scripts/show_usd.py` | print a results file |

Data (parquet on Drive only; the `.json` download records are also in git):

- `data/1-raw-blockchain-extracts/exploratory-2026-10-13/`: the BigQuery downloads named above.
- `data/2-processed-tables-and-evaluations/exploratory-2026-10-13/`: per-spender scores and labels. `w0_scores`, `w1_scores` come from the A/B run (the current `run_unl.py` names them `results_w0`, `results_w1`); `results_unl_w0`, `results_unl_w1` from the C/D run; `usd_bal_w0`, `usd_bal_w1` from `run_usd_bal.py`.

## Rerun

BigQuery jobs go through `scripts/run_bq.py` (dry run, budget check, ledger). Their ledger entries are labelled `exploratory: …`; together they billed about USD 4.95 (ledger USD 34.80 → 39.75 of 50). Substitutions: `fin_pairs`, `unl_pairs`: `--sub TAG=t1` or `tobs`. `fin_labels`: `--sub TAG=w0 --sub FREEZE=t1 --sub APPROVALS=u_approvals` with `--param "out_start=2026-04-01 00:00:00 UTC" --param "out_end=2026-06-30 23:59:59 UTC"`, or `TAG=w1`, `FREEZE=tobs`, `APPROVALS=u_approvals_w1` with July to September. `usd_pairs`: `--sub TAG=t1 --sub BAL=bal_t1 --sub DAY=2026-03-31` or `TAG=tobs`, `BAL=bal_tobs`, `DAY=2026-06-30`. Each table is downloaded with `scripts/download_table.py contract_rep.<table> data/1-raw-blockchain-extracts/exploratory-2026-10-13/<table>`.

The scoring scripts need the revised graph tables (`python scripts/drive_sync.py pull "*graph-tables-usd/*"`) and the downloads above (`pull "*exploratory-2026-10-13/*"`):

```powershell
python experiments/exploratory/2026-10-13-unlimited-allowances/scripts/run_unl.py
```

```powershell
$env:UNL_VARIANTS = "orig,unl,uown"; $env:UNL_OUT = "results_unl.json"; python experiments/exploratory/2026-10-13-unlimited-allowances/scripts/run_unl.py
```

```powershell
python experiments/exploratory/2026-10-13-unlimited-allowances/scripts/run_usd_bal.py
```

```powershell
python experiments/exploratory/2026-10-13-unlimited-allowances/scripts/run_awp_usd.py
```
