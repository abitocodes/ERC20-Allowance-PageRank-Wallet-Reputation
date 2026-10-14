# Exploratory: C-PR against a role-coupled EndorseRank walk (14 October 2026)

- Post hoc, like the other folders in `exploratory/`; not reported in the dissertation. Same cohorts, labels and paired bootstrap (B = 400) as the revised analysis. The published C-PR (λ = 0.5) is reproduced exactly (W0 0.252, W1 0.250; same-window families 0.365, 0.477, 0.142).
- Question: does a walk that gives owners reputation through the transfers they received (option 1) beat C-PR? Definitions are in the docstring of `scripts/run_role_coupled.py`. In short: `cpr_plus` is C-PR with fixed λ = 0.5 but σ allowance edges with a cap of 10 spenders per owner, AWP-weighted transfer edges and restarts mixed from endorsement mass and AWP activeness; `rc_b{β}_mass` (option 1) lets wallets follow only their approvals and contracts follow their payouts with probability β, with restarts proportional to endorsement mass, and scores a contract by the mass it receives over approvals; `rc_b{β}_ctr` restarts at contracts only. `rc_b50_mass` was fixed as the primary option-1 score before the run.

## Results (Kendall τ_b [95% CI])

| Score | New approvals W0 | New approvals W1 | New senders W0 | New senders W1 |
|---|---|---|---|---|
| C-PR, published (`cpr_l50`) | 0.252 [0.241, 0.262] | 0.250 [0.240, 0.260] | 0.262 | 0.263 |
| C-PR with new ingredients (`cpr_plus`) | 0.316 [0.307, 0.325] | 0.298 [0.289, 0.307] | 0.330 | 0.312 |
| Option 1 (`rc_b50_mass`) | 0.326 [0.317, 0.335] | 0.309 [0.299, 0.319] | 0.280 | 0.254 |
| Option 1, β 0.25 / 0.75 | 0.322 / 0.331 | 0.306 / 0.313 | 0.279 / 0.280 | 0.253 / 0.256 |
| Option 1, restarts at contracts (β 0.5) | 0.169 | 0.160 | 0.105 | 0.099 |
| Allowance-only PageRank, endorsement-mass restarts | 0.319 | 0.300 | 0.280 | 0.252 |
| EndorseRank (published) | 0.231 | 0.234 | 0.200 | 0.194 |
| AWP | 0.196 | 0.169 | 0.346 | 0.330 |

- Option 1 minus published C-PR, new approvals: +0.074 [+0.066, +0.082] (W0), +0.059 [+0.053, +0.065] (W1); new senders +0.018 [+0.010, +0.026], −0.009 [−0.017, −0.002].
- Most of that comes from the ingredients: `cpr_plus` minus C-PR is +0.064 and +0.048 on new approvals and +0.069 and +0.048 on new senders. Option 1 minus `cpr_plus`: new approvals +0.010 [+0.005, +0.014] and +0.011 [+0.007, +0.015], new senders −0.051 and −0.058.
- Option 1 minus the allowance-only PageRank with the same restarts: +0.007 [+0.004, +0.010] and +0.009 [+0.006, +0.012] on new approvals, the value of letting owners gain mass from payouts.
- Given 30-day momentum (partial τ, new approvals): C-PR 0.155 and 0.132, `cpr_plus` 0.153 and 0.120, option 1 0.147 and 0.116; option 1 minus C-PR −0.008 [−0.017, +0.001] (W0) and −0.016 [−0.024, −0.008] (W1).
- Same window (matched cohort, family means transfer / allowance / Sybil stability): C-PR 0.365 / 0.477 / 0.142, `cpr_plus` 0.319 / 0.350 / 0.166, option 1 0.140 / 0.435 / 0.035.

## Files

| Path | Content |
|---|---|
| `scripts/run_role_coupled.py` | all walks and evaluations |
| `results_role_coupled.json` | every τ, contrast, partial τ and family mean, with the definitions |
| `data/2-processed-tables-and-evaluations/exploratory-2026-10-14/role_coupled_{w0,w1}.parquet` | per-spender scores (Drive) |

Needs the revised graph tables, `x_nodecay_pairs_{t1,tobs}` and `count_variants_{w0,w1}.parquet` (`../2026-10-14-endorsement-count-variants/`):

```powershell
python experiments/exploratory/2026-10-14-role-coupled-walk/scripts/run_role_coupled.py
```
