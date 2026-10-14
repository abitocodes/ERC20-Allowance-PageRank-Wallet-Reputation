# Exploratory: allowances counted as of the freeze date (14 October 2026)

- Post hoc, like `../2026-10-13-unlimited-allowances/`: chosen and run after every registered and revised result was known, and not reported in the dissertation.
- Question: an allowance stays in force until it is revoked or replaced, so should an allowance in force at the freeze date count as of that date, whatever its approval date? EndorseRank weighs each latest allowance by σ(age) with age = anchor − approval time. Counting every allowance as of the anchor gives all of them age 0, and σ(0) ≈ 0.858 is a common factor that cancels in the row normalisation, so the variant is EndorseRank without the time weight: w(u, v) = Σ_tokens V(usd).
- Base: the revised analysis (`CONTRACT_REP_VARIANT=usd`), its cohorts, labels and paired bootstrap (B = 400). The published weights are reproduced to 4e-16 by the same query.

| Score | Weight | Restarts |
|---|---|---|
| `endorserank` | σ(age) V(usd) (published) | uniform |
| `er_nd` | V(usd) | uniform |
| `endorserank_act` | σ(age) V(usd) (published) | owner activeness Σ max σ |
| `er_nd_act` | V(usd) | owner activeness without decay (number of spenders) |

## Results (Kendall τ_b)

| Score | W0 new approvals | W1 new approvals | W0 new senders | W1 new senders |
|---|---|---|---|---|
| `endorserank` | 0.231 | 0.234 | 0.200 | 0.194 |
| `er_nd` | 0.220 | 0.227 | 0.189 | 0.187 |
| `endorserank_act` | 0.308 | 0.295 | 0.269 | 0.242 |
| `er_nd_act` | 0.210 | 0.221 | 0.182 | 0.183 |
| in-approve degree | 0.250 | 0.268 | 0.180 | 0.205 |

- `er_nd` minus `endorserank`, new approval pairs: −0.011 [−0.013, −0.009] in W0, −0.007 [−0.008, −0.005] in W1; new senders −0.011 and −0.008; drained owners −0.013 (W0); revocations unchanged.
- With activity restarts the loss is large: −0.098 [−0.105, −0.091] (W0) and −0.074 [−0.080, −0.067] (W1) on new approvals. `endorserank_act` beats in-approve degree (+0.059, +0.027) only with the time weight; `er_nd_act` falls below it (−0.040, −0.047).
- Same window (matched cohort, proxies over the whole observation window): `er_nd` is slightly higher in every family (transfer +0.011, allowance +0.009, Sybil stability +0.006).
- Allowance ages: at t1 the median pair's youngest approval is 460 days old, 80% are older than 180 days (σ < 0.5) and 61% older than a year; at T_obs 535 days, 84% and 66%. The decay keeps 26% (t1) and 21% (T_obs) of the weight that σ(0) would give.
- In uniform-restart EndorseRank σ only shifts an owner's share between its spenders (an owner with one spender gives it the whole row either way), so dropping it changes little. In the activity restarts σ sets how much restart mass each owner gets, so recent approvers lose their weight and the scores move far more.

## Files

| Path | Content |
|---|---|
| `sql/nodecay_pairs.sql` | `x_nodecay_pairs_{t1,tobs}`: per pair, Σ V(usd), the published weight as a check, youngest and oldest approval age |
| `scripts/run_nodecay.py` | W0, W1 and same-window evaluation |
| `scripts/show_nodecay.py` | prints `results_nodecay.json` |
| `results_nodecay.json` | every τ, contrast and family mean |
| `data/1-raw-blockchain-extracts/exploratory-2026-10-14/` | the two downloads (parquet on Drive) |
| `data/2-processed-tables-and-evaluations/exploratory-2026-10-14/` | per-spender scores and labels, `nodecay_w0`, `nodecay_w1` |

## Rerun

The two BigQuery jobs (`--sub TAG=t1` and `--sub TAG=tobs` through `scripts/run_bq.py`, labels `exploratory: allowance pairs without time weight (…)`) billed about USD 0.01 (ledger USD 39.75 → 39.76). Download each with `scripts/download_table.py contract_rep.x_nodecay_pairs_<tag> data/1-raw-blockchain-extracts/exploratory-2026-10-14/x_nodecay_pairs_<tag>`; the scoring also needs the revised graph tables (`python scripts/drive_sync.py pull "*graph-tables-usd/*"`).

```powershell
python experiments/exploratory/2026-10-14-freeze-date-time-weight/scripts/run_nodecay.py
```
