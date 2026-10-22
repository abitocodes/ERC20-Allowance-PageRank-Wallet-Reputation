# Exploratory: where the coupled walk stands against AWP (22 October 2026)

- Post hoc, like the other folders in `exploratory/`: chosen after every registered and revised result was known, including the W0 and W1 labels. The design below was written and committed before any of its numbers was computed, so the list of comparisons is fixed, but it is not a registered test.
- Question: the thesis answers RQ5 with rules A and B, which compare C-PR with its own layers. AWP, the transfer PageRank the thesis builds on, is the comparator only in the registered sensitivity analysis of W1 and in post hoc contrasts. What do allowance edges add to AWP itself?
- Base: the revised analysis (`CONTRACT_REP_VARIANT=usd`): its graphs, cohorts, labels, PageRank settings (d = 0.85, tolerance 1e-8, at most 300 iterations) and paired bootstrap (B = 400, seed 42, the resamples of the published tables).

## Design (fixed before the run)

### Part A: the published scores

Read from the published per-contract score tables (`revised-usd/holdout-w0`, `window-w1`, `same-window`); no score is recomputed.

| Id | Comparison | Contrasts |
|---|---|---|
| A1 | Both spender labels at once: the mean of τ on new approval pairs and τ on new senders (a family mean, as in the same-window families), W0 and W1 | C-PR (λ = 0.25, 0.5, 0.75) minus AWP; EndorseRank and EndorseRank with activity restarts minus AWP, for context |
| A2 | New counterparties: new approval pairs plus new senders of each spender (an address that both approves and sends counts twice), W0 and W1 | τ of every score; C-PR (λ = 0.5) minus AWP, minus EndorseRank, minus each raw degree |
| A3 | Coverage: the spenders with no transfer edge at the freeze, which AWP scores zero (one tie block), and the rest | τ of C-PR (λ = 0.5), EndorseRank and in-approve degree on new approval pairs inside the first group; C-PR minus AWP on both labels and on new counterparties inside the second |
| A4 | Top of the ranking: share of the top k spenders (k = 100, 500, 1,000) that gained any new counterparty, any new approval pair, any new sender | AWP, C-PR (λ = 0.5), EndorseRank; point estimates only |
| A5 | Same window, both constructs: the mean of the transfer-family mean and the allowance-family mean (four proxies) on the matched cohort | C-PR (λ = 0.5) minus AWP |
| A6 | Traders: liquidation-free close rate and no-liquidation flag, W0 and W1 | C-PR (λ = 0.5) minus AWP |

### Part B: a coupled walk whose transfer end is AWP (C-AWP)

C-PR differs from AWP in three things at once: it couples the layers, it restarts uniformly where AWP restarts at active senders, and its layers carry dollar amounts where AWP's carry σ V. Its transfer layer walked alone (C-PR, λ = 0) is therefore not AWP, and a contrast of C-PR with AWP mixes the coupling with the other two. C-AWP applies the coupling of C-PR to the two published walks with activity restarts:

- transfer layer: AWP's edges, weight Σ σ(age) V(usd) (`w_awp`);
- allowance layer: EndorseRank's edges, weight Σ_tokens σ(age) V(usd) (`w_er`);
- transition row of node u: as C-PR (Equation `eq:coupled-transition`), the allowance row with weight λ and the transfer row with weight 1 − λ at a node with out-edges in both layers, the one layer at a node with out-edges in one;
- restarts: (1 − λ) π_T + λ π_A, with π_T AWP's sending activeness and π_A the owners' approving activeness of EndorseRank with activity restarts, each normalised to one.

At λ = 0 C-AWP is AWP and at λ = 1 it is EndorseRank with activity restarts, both published scores; the run checks both ends. λ = 0.5 is the primary value, 0.25 and 0.75 are reported beside it, and no other value is computed.

| Id | Comparison |
|---|---|
| B0 | Reproduction: C-AWP (λ = 0) against AWP and C-AWP (λ = 1) against EndorseRank with activity restarts on every cohort (τ and largest absolute difference) |
| B1 | Spender holdouts W0 and W1: τ of C-AWP on new approval pairs, new senders and new counterparties; C-AWP (λ = 0.5) minus AWP, minus C-PR (λ = 0.5), minus EndorseRank with activity restarts, and minus the raw degree of each label |
| B2 | The structure of rule B with AWP as the comparator, in both windows: superiority on new approval pairs (lower bound above 0), non-inferiority on new senders and on the traders' liquidation-free close rate (lower bound above −0.01) |
| B3 | Same window at T_obs on the matched cohort: family means of C-AWP and contrasts with AWP on each family |
| B4 | Traders of W0 and W1: τ of C-AWP on the liquidation-free close rate and the no-liquidation flag, and C-AWP (λ = 0.5) minus AWP |

Every τ comes with its 95% percentile interval over the 400 paired resamples of its cohort (traders included, as in rule B). Every comparison above is reported whichever way it comes out.

## Results (Kendall τ_b [95% CI], 400 paired resamples)

Reproduction (B0): on every cohort C-AWP (λ = 0) orders the contracts exactly as AWP and C-AWP (λ = 1) exactly as EndorseRank with activity restarts (τ = 1.000; largest relative difference of a score below 5e-15). The published contrast of C-PR with AWP on the traders' liquidation-free close rate in W1 is reproduced (+0.021 [−0.019, +0.060]).

### Spender holdouts

| Score | New approval pairs W0 | W1 | New senders W0 | W1 | New counterparties W0 | W1 |
|---|---|---|---|---|---|---|
| AWP | 0.196 [0.181, 0.210] | 0.169 [0.157, 0.183] | 0.346 [0.336, 0.356] | 0.330 [0.321, 0.340] | 0.277 [0.263, 0.290] | 0.253 [0.240, 0.266] |
| C-PR (λ = 0.5) | 0.252 [0.241, 0.262] | 0.250 [0.240, 0.260] | 0.262 [0.250, 0.273] | 0.263 [0.254, 0.273] | 0.301 [0.291, 0.313] | 0.300 [0.290, 0.310] |
| C-AWP (λ = 0.25) | 0.307 | 0.290 | 0.335 | 0.317 | 0.373 | 0.353 |
| C-AWP (λ = 0.5) | 0.314 [0.305, 0.323] | 0.296 [0.286, 0.305] | 0.331 [0.323, 0.340] | 0.312 [0.303, 0.320] | 0.376 [0.368, 0.386] | 0.355 [0.346, 0.365] |
| C-AWP (λ = 0.75) | 0.316 | 0.298 | 0.326 | 0.305 | 0.375 | 0.353 |
| EndorseRank (activity restarts) | 0.308 | 0.295 | 0.269 | 0.242 | 0.328 | 0.301 |
| In-approve degree | 0.250 | 0.268 | 0.180 | 0.205 | 0.241 | 0.261 |
| Transfer in-degree | 0.135 | 0.131 | 0.303 | 0.308 | 0.217 | 0.219 |

Contrasts with AWP (W0, W1):

| Contrast | W0 | W1 |
|---|---|---|
| A1 C-PR minus AWP, mean of both spender labels | −0.015 [−0.022, −0.006] | +0.007 [+0.001, +0.015] |
| A1 C-PR (λ = 0.25) minus AWP, same | −0.010 [−0.018, −0.002] | +0.010 [+0.004, +0.018] |
| A1 C-PR (λ = 0.75) minus AWP, same | −0.020 [−0.028, −0.011] | +0.003 [−0.004, +0.011] |
| A1 EndorseRank (activity restarts) minus AWP, same | +0.018 [+0.010, +0.027] | +0.019 [+0.010, +0.027] |
| A1 C-AWP minus AWP, same | +0.051 [+0.045, +0.058] | +0.054 [+0.048, +0.061] |
| A2 C-PR minus AWP, new counterparties | +0.024 [+0.012, +0.038] | +0.047 [+0.036, +0.060] |
| A2 C-PR minus in-approve degree, new counterparties | +0.060 [+0.051, +0.070] | +0.039 [+0.031, +0.047] |
| A2 C-PR minus transfer in-degree, new counterparties | +0.085 [+0.074, +0.098] | +0.081 [+0.069, +0.095] |
| A2 C-PR minus EndorseRank, new counterparties | +0.054 [+0.046, +0.062] | +0.059 [+0.051, +0.067] |
| B1 C-AWP minus AWP, new approval pairs (B2: superiority holds) | +0.118 [+0.106, +0.132] | +0.127 [+0.114, +0.139] |
| B1 C-AWP minus AWP, new senders (B2: non-inferiority at 0.01 fails) | −0.015 [−0.019, −0.011] | −0.018 [−0.021, −0.015] |
| B1 C-AWP minus AWP, new counterparties | +0.099 [+0.089, +0.112] | +0.102 [+0.091, +0.113] |
| B1 C-AWP (λ = 0.25) minus AWP, new approval pairs / new senders | +0.111 / −0.011 | +0.120 / −0.013 |
| B1 C-AWP (λ = 0.75) minus AWP, new approval pairs / new senders | +0.120 / −0.021 | +0.129 / −0.025 |
| B1 C-AWP minus C-PR, new approval pairs | +0.062 [+0.056, +0.068] | +0.045 [+0.041, +0.050] |
| B1 C-AWP minus C-PR, new senders | +0.070 [+0.064, +0.075] | +0.049 [+0.045, +0.053] |
| B1 C-AWP minus EndorseRank (activity restarts), new approval pairs | +0.006 [−0.000, +0.011] | +0.001 [−0.003, +0.006] |
| B1 C-AWP minus EndorseRank (activity restarts), new senders | +0.062 [+0.054, +0.068] | +0.070 [+0.062, +0.077] |
| B1 C-AWP minus in-approve degree, new approval pairs | +0.064 [+0.055, +0.073] | +0.028 [+0.021, +0.036] |
| B1 C-AWP minus transfer in-degree, new senders | +0.028 [+0.022, +0.034] | +0.004 [−0.002, +0.009] |

### Coverage (A3)

AWP scores zero every spender without a transfer edge at the freeze: 2,891 of 17,050 in W0 (385 of them gained a new approval pair, 16 a new sender) and 3,025 of 18,152 in W1 (326 and 7). AWP leaves them in one tie block. On new approval pairs inside that group:

| Score | W0 | W1 |
|---|---|---|
| C-PR | 0.225 [0.200, 0.253] | 0.267 [0.239, 0.290] |
| C-AWP | 0.342 [0.323, 0.364] | 0.346 [0.320, 0.366] |
| EndorseRank | 0.201 [0.177, 0.225] | 0.235 [0.205, 0.261] |
| In-approve degree | 0.246 [0.221, 0.274] | 0.285 [0.256, 0.308] |

On the other spenders (14,159 and 15,127), which AWP can order:

| Contrast | W0 | W1 |
|---|---|---|
| C-PR minus AWP, new approval pairs | −0.038 [−0.047, −0.029] | −0.018 [−0.026, −0.009] |
| C-PR minus AWP, new senders | −0.074 [−0.081, −0.068] | −0.056 [−0.062, −0.051] |
| C-PR minus AWP, new counterparties | −0.059 [−0.067, −0.050] | −0.039 [−0.046, −0.031] |
| C-AWP minus AWP, new approval pairs | +0.018 [+0.013, +0.025] | +0.025 [+0.019, +0.031] |
| C-AWP minus AWP, new senders | −0.002 [−0.005, +0.002] | −0.005 [−0.008, −0.002] |
| C-AWP minus AWP, new counterparties | +0.013 [+0.008, +0.018] | +0.015 [+0.010, +0.021] |

- C-PR's lead over AWP on new approval pairs comes from the spenders AWP cannot order; among the others AWP ranks both labels better than C-PR. C-AWP leads AWP on new approval pairs in both groups, and most of its loss on new senders comes from lifting the zero block, which almost never gains a sender.

### Top of the ranking (A4, share of the top k that gained any new counterparty / any new approval pair / any new sender)

| Score | W0 top 100 | W0 top 1,000 | W1 top 100 | W1 top 1,000 |
|---|---|---|---|---|
| AWP | 0.92 / 0.73 / 0.90 | 0.698 / 0.470 / 0.634 | 0.89 / 0.63 / 0.88 | 0.654 / 0.408 / 0.612 |
| C-PR | 0.85 / 0.80 / 0.72 | 0.564 / 0.459 / 0.436 | 0.85 / 0.76 / 0.73 | 0.499 / 0.380 / 0.398 |
| C-AWP | 0.90 / 0.85 / 0.79 | 0.677 / 0.533 / 0.533 | 0.88 / 0.78 / 0.77 | 0.624 / 0.462 / 0.501 |
| EndorseRank | 0.70 / 0.69 / 0.51 | 0.425 / 0.415 / 0.283 | 0.67 / 0.67 / 0.49 | 0.371 / 0.364 / 0.247 |

Base rates: 15.2% (W0) and 11.7% (W1) of the spenders gained any new counterparty. AWP's top lists hold the most spenders that gained any new counterparty; the coupled walks hold more that gained new approval pairs.

### Same window (A5, B3; matched cohort, n = 15,107)

| Score | Transfer | Allowance | Sybil stability | Mean of transfer and allowance families |
|---|---|---|---|---|
| AWP | 0.572 [0.564, 0.580] | 0.193 [0.182, 0.203] | 0.395 [0.387, 0.403] | 0.383 [0.376, 0.390] |
| C-PR | 0.365 [0.355, 0.375] | 0.477 [0.469, 0.485] | 0.142 [0.134, 0.151] | 0.421 [0.415, 0.428] |
| C-AWP | 0.327 [0.317, 0.337] | 0.359 [0.350, 0.368] | 0.170 [0.162, 0.178] | 0.343 [0.336, 0.350] |
| EndorseRank | 0.158 | 0.585 | 0.007 | 0.371 [0.364, 0.378] |

C-PR minus AWP on the mean of the two families +0.038 [+0.033, +0.043]; C-AWP minus AWP −0.040 [−0.042, −0.037]. C-AWP minus AWP by family: transfer −0.245, allowance +0.166, Sybil stability −0.225.

### Traders (A6, B4; liquidation-free close rate / no-liquidation flag)

| Contrast with AWP | W0 (n = 88) | W1 (n = 70) |
|---|---|---|
| C-PR | +0.033 [−0.013, +0.100] / +0.049 [−0.000, +0.115] | +0.021 [−0.019, +0.060] / +0.026 [−0.014, +0.070] |
| C-AWP | +0.021 [−0.016, +0.074] / +0.012 [−0.026, +0.066] | +0.025 [−0.023, +0.082] / +0.023 [−0.030, +0.079] |

No trader contrast is resolved; the B2 non-inferiority condition on the liquidation-free close rate fails in both windows (lower bounds −0.016 and −0.023).

### Reading

- Against AWP, the published C-PR gains on new approval pairs only through the spenders AWP cannot order, loses on new senders, and is ahead on new counterparties of either kind in both windows and on the same-window mean of the two constructs. Across both spender labels it is behind AWP in W0 and slightly ahead in W1.
- Most of C-PR's loss to AWP on new senders comes from its weights and uniform restarts, not from the coupling: with AWP's weights and restarts the loss shrinks from −0.085 and −0.067 to −0.015 and −0.018, while the gain on new approval pairs grows from +0.056 and +0.081 to +0.118 and +0.127.
- C-AWP still fails the structure of rule B against AWP in both windows: superiority on new approval pairs holds, but non-inferiority at 0.01 fails on new senders and on the traders. It is a hypothesis for a registered test on a later window, not a finding.
- Run time: C-AWP walks the union graph of C-PR; its solves took 79 to 81 iterations at d = 0.85 (not timed under the benchmark protocol).

## Addendum (fixed after the results above were known, before it was computed)

A review of the thesis asked how much of C-PR's gap to AWP belongs to C-PR's transfer layer walked alone, which differs from AWP in its weights and restarts but not in coupling. The registration of W1 named C-PR (λ = 0) minus AWP for the traders "to isolate AWP's weights and restarts"; this addendum computes the same contrast on the spender cohorts, and nothing else.

| Id | Comparison |
|---|---|
| D1 | C-PR (λ = 0) minus AWP on new approval pairs and on new senders, W0 and W1, the 400 paired resamples of each cohort |

Script: `scripts/run_addendum.py`; output: `results_addendum.json`.

Result (Δτ [95% CI]):

| Contrast | W0 | W1 |
|---|---|---|
| C-PR (λ = 0) minus AWP, new approval pairs | −0.036 [−0.040, −0.032] | −0.028 [−0.032, −0.024] |
| C-PR (λ = 0) minus AWP, new senders | −0.050 [−0.054, −0.046] | −0.039 [−0.043, −0.035] |

On new senders C-PR minus AWP (−0.085 and −0.067) is the sum of this layer gap and the cost of coupling, C-PR minus C-PR (λ = 0) (−0.034 and −0.028): the layer gap is about three fifths of the whole in both windows.

## Files

| Path | Content |
|---|---|
| `scripts/run_cpr_awp.py` | every comparison of the design |
| `results_cpr_awp.json` | every τ, family mean, contrast and share above, with the reproduction checks |
| `data/2-processed-tables-and-evaluations/exploratory-2026-10-22/cawp_{w0,w1}.parquet` | C-AWP scores of the spender cohorts (written by the script; not yet on Drive, and recomputed by a rerun in about 15 minutes) |

## Rerun

Needs the revised graph tables and the published score tables:

```powershell
python scripts/drive_sync.py pull "*graph-tables-usd/*"
python scripts/drive_sync.py pull "*2-processed-tables-and-evaluations/revised-usd/*"
python experiments/exploratory/2026-10-22-cpr-against-awp/scripts/run_cpr_awp.py
```
