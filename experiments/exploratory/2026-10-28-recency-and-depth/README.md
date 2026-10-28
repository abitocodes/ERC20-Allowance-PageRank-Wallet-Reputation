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

(Added after the run.)
