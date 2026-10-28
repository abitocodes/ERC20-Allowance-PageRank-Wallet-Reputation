# Exploratory: when do the walks beat the raw counts out of window? (28 October 2026)

- Not yet reported in the dissertation; whether a paragraph goes into Chapter 5 is the author's decision.
- Post hoc, like the other folders in `exploratory/`: chosen after every registered and revised result was known, including the W0 and W1 labels. Before this design was written, one look was taken on 28 October 2026 in the working session: on the spenders of the twelve-month cohort, the 33-month US-dollar scores already ranked later new senders below the transfer in-degree (W0 AWP 0.412 against 0.427), while on the spenders left out of that cohort AWP led (0.159 against 0.088). Everything below was written and committed before any of its numbers was computed, so the list of comparisons is fixed, but it is not a registered test.
- Question: in the registered analysis AWP ranks later new senders above the transfer in-degree in both windows (W0 +0.038 [0.035, 0.042], W1 +0.020 [0.016, 0.023]); in the main analysis, with scores from the twelve months before each freeze, it ranks them below (−0.038, −0.041), and no PageRank of the study beats the raw degree of its edge type. Where does the registered lead sit, does it come from the walk's propagation or from its time weighting, and does propagation add anything where the closed form of EndorseRank does not hold?
- Base: the published per-contract score tables of the registered analysis (`data/2-processed-tables-and-evaluations/holdout-w0`, `registered-w1`) and of the main analysis (`revised-usd-12m/holdout-w0`, `window-w1`), and the pair tables of both (`data/1-raw-blockchain-extracts/graph-tables/`, `graph-tables-usd-12m/`). Spenders are matched across analyses by address. The spender cohort of the 33-month US-dollar analysis (`revised-usd/`) is used only as a set of addresses, to tell why a registered spender is not in the twelve-month cohort; none of its results is used.
- Statistics: Kendall τ_b and the paired bootstrap of the thesis (`scripts/stats.py`, B = 400, seed 42), recomputed inside each group, 95% percentile intervals. Every comparison below is reported whichever way it comes out.

## Design (fixed before the run)

### Q1: where the registered lead of the walks over the counts sits

Registered spender cohorts of W0 (33,101) and W1 (34,587), registered scores and labels, in four groups:

| Group | Spenders |
|---|---|
| all | the whole registered cohort |
| kept | also in the spender cohort of the main analysis in the same window (a positive latest allowance of the five tokens at the freeze, set in the twelve months before it) |
| older five-token | in the 33-month US-dollar spender cohort (a positive latest allowance of the five tokens at the freeze) but not kept: every such allowance was set more than twelve months before the freeze |
| other tokens | in neither: no positive latest allowance of the five tokens at the freeze |

Contrasts in each group: AWP minus transfer in-degree on new transfer senders; EndorseRank with activity restarts minus in-approve degree, and EndorseRank minus in-approve degree, on new approval pairs. Also the τ of each score, the group size and the share of spenders that gained each label.

### Q2: recency or propagation

Two local scores per spender, from the pair tables at the freeze of each window (t1 for W0, T_obs for W1), without any walk:

| Score | Definition |
|---|---|
| recency-weighted count | the sum over the spender's in-edges of `max_sig`, the time weight σ(age) of the latest event on that pair: transfers into the spender (senders other than itself) on the transfer side, positive latest allowances (`w_er` > 0) on the allowance side |
| weighted in-strength | the sum over the same in-edges of the walk's own edge weight: `w_awp` (σ V summed over transfers) on the transfer side, `w_er` on the allowance side |

The count of the same in-edges is checked against the published raw degrees (`t1_in_degree`, `t1_in_approve_degree`; W1 `in_degree`, `in_approve_degree`); any mismatch is reported.

Contrasts, on the registered cohorts (all, kept, older five-token, other tokens) and on the main-analysis cohorts of W0 (7,914) and W1 (7,960):
- new transfer senders: recency-weighted count minus transfer in-degree; weighted in-strength minus transfer in-degree; AWP minus recency-weighted count;
- new approval pairs: recency-weighted count minus in-approve degree; weighted in-strength minus in-approve degree; EndorseRank with activity restarts minus recency-weighted count.

Expectation written beforehand: if the registered lead of AWP comes from its time weighting, the recency-weighted count beats the transfer in-degree on the registered cohort by about as much as AWP does, AWP does not beat the recency-weighted count, and on the main-analysis cohorts, whose raw degrees count only the last twelve months, the recency-weighted count gains little over the in-degree.

### Q3: depth

For every spender with at least one positive latest allowance, depth one when none of its approving owners receives a positive latest allowance itself, deeper otherwise (the rule of `closed_form` in `scripts/run_same_window.py`), on the allowance pair table at the freeze of each window. In the main analysis (W0 and W1) and, for comparison, the registered analysis (W0 and W1), in each depth group:

- EndorseRank, EndorseRank with activity restarts and C-PR (λ = 0.5), each minus the in-approve degree, on new approval pairs;
- group sizes and the share of spenders that gained a new approval pair.

Expectation written beforehand: at depth one EndorseRank is close to a reweighted approval count (the closed form), so any gain from propagation over the count should show only among deeper spenders.

## Results

Computed on 28 October 2026 by `scripts/run_recency_depth.py` (`results.json`), after the design above was committed. Checks: the counts of the in-edges in the pair tables equal the published raw degrees for every spender of both analyses (0 mismatches), and the twelve-month spender cohorts lie wholly inside the registered ones (W0 7,914 of 7,914, W1 7,960 of 7,960). Entries are Δτ [95% CI] over 400 paired resamples inside each group.

### Q1: registered scores and labels, by group

| Window | Group | n | gained a new sender / approval pair | AWP − transfer in-degree (new senders) | EndorseRank (activity) − in-approve degree | EndorseRank − in-approve degree |
|---|---|---|---|---|---|---|
| W0 | all | 33,101 | 0.092 / 0.103 | +0.038 [+0.035, +0.042] | +0.043 [+0.036, +0.049] | -0.011 [-0.016, -0.006] |
| W0 | kept | 7,914 | 0.206 / 0.236 | -0.000 [-0.005, +0.007] | -0.012 [-0.021, -0.003] | -0.045 [-0.053, -0.036] |
| W0 | older five token | 9,136 | 0.031 / 0.043 | +0.066 [+0.054, +0.078] | +0.131 [+0.111, +0.151] | +0.013 [+0.001, +0.025] |
| W0 | other tokens | 16,051 | 0.070 / 0.071 | +0.017 [+0.013, +0.023] | +0.006 [-0.003, +0.017] | -0.018 [-0.026, -0.010] |
| W1 | all | 34,587 | 0.081 / 0.082 | +0.020 [+0.016, +0.023] | +0.018 [+0.012, +0.023] | -0.029 [-0.032, -0.025] |
| W1 | kept | 7,960 | 0.188 / 0.204 | -0.014 [-0.021, -0.007] | -0.028 [-0.036, -0.020] | -0.056 [-0.063, -0.048] |
| W1 | older five token | 10,192 | 0.026 / 0.025 | +0.007 [-0.001, +0.014] | +0.001 [-0.013, +0.015] | -0.037 [-0.047, -0.027] |
| W1 | other tokens | 16,435 | 0.064 / 0.059 | +0.010 [+0.004, +0.015] | +0.003 [-0.006, +0.012] | -0.029 [-0.035, -0.023] |

### Q2: recency-weighted counts and weighted in-strengths (no walk)

| Window | Cohort | recency count − in-degree | in-strength − in-degree | AWP − recency count | recency count − in-approve degree | in-strength − in-approve degree | EndorseRank (activity) − recency count |
|---|---|---|---|---|---|---|---|
| W0 | registered all | +0.056 [+0.052, +0.060] | +0.038 [+0.034, +0.042] | -0.018 [-0.019, -0.016] | +0.059 [+0.053, +0.065] | +0.059 [+0.052, +0.064] | -0.017 [-0.019, -0.014] |
| W0 | registered kept | +0.029 [+0.026, +0.034] | -0.003 [-0.009, +0.003] | -0.029 [-0.034, -0.024] | +0.016 [+0.010, +0.023] | +0.008 [+0.001, +0.015] | -0.028 [-0.035, -0.022] |
| W0 | registered older five token | +0.085 [+0.071, +0.100] | +0.066 [+0.055, +0.079] | -0.019 [-0.024, -0.014] | +0.145 [+0.124, +0.166] | +0.144 [+0.123, +0.164] | -0.015 [-0.020, -0.009] |
| W0 | registered other tokens | +0.032 [+0.027, +0.037] | +0.018 [+0.012, +0.023] | -0.014 [-0.017, -0.012] | +0.027 [+0.018, +0.037] | +0.028 [+0.018, +0.037] | -0.021 [-0.024, -0.017] |
| W0 | main analysis (twelve months) | +0.008 [+0.006, +0.011] | -0.051 [-0.060, -0.043] | -0.046 [-0.051, -0.041] | +0.004 [-0.001, +0.009] | -0.047 [-0.056, -0.038] | -0.064 [-0.073, -0.058] |
| W1 | registered all | +0.034 [+0.030, +0.037] | +0.019 [+0.015, +0.022] | -0.015 [-0.016, -0.013] | +0.035 [+0.030, +0.040] | +0.034 [+0.029, +0.039] | -0.017 [-0.019, -0.016] |
| W1 | registered kept | +0.021 [+0.017, +0.026] | -0.022 [-0.028, -0.014] | -0.035 [-0.040, -0.030] | +0.018 [+0.012, +0.024] | +0.008 [+0.002, +0.015] | -0.046 [-0.052, -0.039] |
| W1 | registered older five token | +0.014 [+0.006, +0.022] | +0.013 [+0.006, +0.019] | -0.008 [-0.011, -0.005] | +0.009 [-0.004, +0.022] | +0.012 [-0.000, +0.024] | -0.008 [-0.014, -0.001] |
| W1 | registered other tokens | +0.021 [+0.014, +0.026] | +0.010 [+0.004, +0.015] | -0.011 [-0.013, -0.008] | +0.022 [+0.013, +0.030] | +0.023 [+0.014, +0.031] | -0.019 [-0.022, -0.016] |
| W1 | main analysis (twelve months) | +0.010 [+0.007, +0.013] | -0.051 [-0.058, -0.042] | -0.051 [-0.056, -0.044] | +0.015 [+0.010, +0.020] | -0.019 [-0.029, -0.010] | -0.061 [-0.069, -0.054] |

### Q3: depth one against deeper spenders, new approval pairs

| Window | Analysis | Depth | n | gained a new approval pair | EndorseRank − in-approve degree | EndorseRank (activity) − in-approve degree | C-PR − in-approve degree |
|---|---|---|---|---|---|---|---|
| W0 | main | one | 5,092 | 0.233 | -0.033 [-0.042, -0.022] | +0.008 [-0.002, +0.019] | -0.015 [-0.032, +0.003] |
| W0 | main | deeper | 2,813 | 0.194 | -0.258 [-0.274, -0.241] | -0.236 [-0.252, -0.220] | -0.222 [-0.238, -0.203] |
| W0 | registered | one | 19,955 | 0.107 | +0.033 [+0.026, +0.039] | +0.125 [+0.115, +0.135] | +0.017 [+0.009, +0.027] |
| W0 | registered | deeper | 13,146 | 0.097 | -0.106 [-0.113, -0.098] | -0.088 [-0.096, -0.080] | -0.102 [-0.110, -0.094] |
| W1 | main | one | 5,244 | 0.200 | -0.022 [-0.033, -0.012] | +0.025 [+0.014, +0.036] | -0.007 [-0.024, +0.010] |
| W1 | main | deeper | 2,712 | 0.164 | -0.241 [-0.258, -0.222] | -0.213 [-0.229, -0.198] | -0.208 [-0.224, -0.192] |
| W1 | registered | one | 20,976 | 0.082 | +0.013 [+0.008, +0.019] | +0.088 [+0.081, +0.096] | +0.008 [+0.001, +0.016] |
| W1 | registered | deeper | 13,611 | 0.083 | -0.125 [-0.132, -0.117] | -0.113 [-0.122, -0.104] | -0.112 [-0.118, -0.105] |

### Reading (post hoc)

- Q1. In the registered analysis the leads of AWP and of EndorseRank with activity restarts over the raw counts sit outside the twelve-month cohort, above all among the spenders whose five-token allowances were all older than twelve months (W0: AWP +0.066, the activity variant +0.131), of which only 3.1% gained a new sender and 4.3% a new approval pair. On the spenders that the twelve-month cohort keeps, the registered scores themselves do not beat the counts (AWP level in W0 and below in W1; the activity variant below in both).
- Q2. The lead is recency, not propagation. A count that weighs each sender or owner by σ of the age of its latest event, with the thesis's own k and t0 and no walk, beats the raw count by more than AWP and the activity variant do, in every group of the registered cohort and in both windows, and neither walk beats this recency-weighted count anywhere (every AWP − recency count and activity variant − recency count interval lies below zero). AWP ranks new senders as its own weighted in-strength does (W0 0.340 against 0.340, W1 0.322 against 0.321): its propagation adds nothing to its edge weights. In the main analysis, whose raw degrees already count only the last twelve months, the recency weighting gains little but still resolves on new senders (+0.008 W0, +0.010 W1) and on new approval pairs in W1 (+0.015), while the value-weighted in-strengths fall below the counts.
- Q3. The expectation written beforehand did not hold. Among deeper spenders, where the walk is more than a reweighted count, every walk falls far below the in-approve degree (main analysis −0.21 to −0.26), and the count ranks that group unusually well (τ 0.657 in W0, 0.615 in W1). Among depth-one spenders the walks are near the count, and EndorseRank with activity restarts, which at depth one weighs each owner by its approving activity, is level with it in W0 (+0.008 [−0.002, 0.019]) and above it in W1 (+0.025 [0.014, 0.036]).
- Together: on these data what improves on the raw count out of window is weighing the counterparties by recency or activity; propagation over the graph adds nothing, and where it does change the ranking, among deeper spenders, it makes it worse. All of this was computed after the labels were known; the recency-weighted counts would need a registered test on a later window before any claim.
