# Registration of the window W1 (July–September 2026)

- Written after the W0 holdout results were known, and committed with `registered_window.status: registered` in `config/contract_reputation.yaml` **before** scan B, the only query that reads logs dated after 30 June 2026. `scripts/extract_w1.py` refuses to run unless this file and the configuration are committed with that status, and it records their SHA-256 hashes in the extraction manifest.
- Nothing below changes after the July–September logs are extracted.

## 1. Window and cohorts

- Scores are frozen at 2026-06-30 23:59:59 UTC and use every extracted event from 2023-10-01; the decay is anchored at the freeze (these are the same graphs as the same-window evaluation).
- Labels are counted from 2026-07-01 00:00:00 to 2026-09-30 23:59:59 UTC.
- Spender cohort: every contract spender with a positive latest allowance at the freeze in the extracted approval data. Labels: new approval pairs and new transfer senders, defined as in the analysis plan (section 5), with the approvals and transfers of the window extracted under the same cohort filter.
- Trader cohort: GMX V2 accounts that hold contract code, are nodes of the freeze-date graph (either layer), and close at least three positions in the label window. Label: the liquidation-free close rate, one minus the share of the account's closes in the window that were liquidations.
- Methods, solver settings, SQL and bootstrap (400 paired resamples, seed 42) are those of the analysis plan.

## 2. Decision rule B: does C-PR improve on its transfer layer walked alone?

Contrast Δτ = τ(C-PR, λ = 0.5) − τ(C-PR, λ = 0), paired over the cohort's members, 95% percentile interval.

- F1 (spenders, new approval pairs): the interval lies above zero.
- F2 (spenders, new transfer senders): the lower end lies above −δ.
- F3 (traders, liquidation-free close rate): the lower end lies above −δ.

C-PR improves on its transfer layer walked alone only if F1, F2 and F3 all hold. The margin is δ = 0.01, the half-width of the paired interval of the corresponding contrast on new transfer senders in W0 (0.0040: Δτ = -0.030, interval [-0.034, -0.026]), rounded up to two decimals; a smaller difference cannot be resolved at these sample sizes. If neither score predicts the trader label, F3 can pass with both coefficients near zero; the two coefficients are therefore reported next to the verdict.

Reported in this order, outside the decision:
- F4: C-PR against C-PR(λ = 0) on the liquidation-free close rate, as a superiority test.
- F5: C-PR against C-PR(λ = 1) on the same label.
- F6: the primary part of rule A on W1 (C-PR no worse than C-PR(λ = 1) on new approval pairs; better than C-PR(λ = 0) on new senders).
- Sensitivity 1: F1–F4 with AWP in place of C-PR(λ = 0).
- Sensitivity 2: F1–F6 with the cohort members that a graph leaves out kept as isolated nodes.

## 3. Comparison on an outcome built from neither edge type

The trader labels come from GMX closes, which enter neither graph. Two windows: W1 (primary; freeze 30 June, labels July–September) and W0 (secondary; freeze 31 March, labels April–June, trader cohort defined in the same way). The trader liquidation labels of W0 have not been computed for any score when this file is committed.

Four pairs set allowance against transfer: in-approve degree and transfer in-degree; EndorseRank with AWP's activity restarts and AWP; EndorseRank and AWP; C-PR(λ = 1) and C-PR(λ = 0). C-PR(λ = 0) minus AWP is reported to isolate AWP's weights and restarts. Six labels are reported: liquidation-free close rate (primary), no-liquidation flag, profitable closes, realized gain, profitable share, non-loss share.

Decision contrasts on the liquidation-free close rate in W1, each with a Bonferroni 97.5% interval from 2,000 paired resamples (seed 42):
- P: in-approve degree minus transfer in-degree.
- Q: EndorseRank with activity restarts minus AWP.

Because the chance of a liquidation rises with the number of closes, τ_b is also computed within strata of 3–4, 5–9, 10–24 and 25 or more closes and weighted by each stratum's pairs.

- R1 (count-level lead): the 97.5% interval of P and the 95% interval of the stratified P lie above zero in W1, and P is positive in W0.
- R2 (PageRank-level lead): the 97.5% interval of Q lies above zero in W1 and Q is positive in W0.
- R3 (specificity): if P on the profitable share or on the non-loss share in W1 is below zero with a 95% interval excluding zero, the allowance signal is read as specific to liquidation avoidance.

Recipients (traders with in-approve degree above zero at the freeze) are compared with the other traders on every label; an influence check drops the ten recipients of highest in-approve degree.

Wording of the conclusions, fixed now: if R1 holds, "the approval count at the freeze ranked contract traders above the transfer count on later liquidation avoidance"; if R1 fails, "no count-level lead of allowance over transfer on later liquidation avoidance"; if R2 holds, the same sentence for the PageRank pair, otherwise "the PageRank versions are not resolved"; if R3 applies, "the signal concerns forced-liquidation avoidance, not trading success".
