# Addendum to the 14 September plan: a fresh holdout for the coupled operator

Taehong Kwon, 28 September 2026. This file and config/fresh_holdout_2026q3.yaml were committed before any log from June, July or August 2026 was extracted.

## 1. Why an addendum

The primary rule of 14 September failed, and it stays failed. At lambda = 0.5, C-PR did worse than EndorseRank on new approval pairs (difference -0.184, interval [-0.213, -0.149]) and was level with AWP on new transfer senders (+0.007, interval [-0.012, 0.028]). The thesis reports that null, as the plan said it would.

The same spring run showed something the rule did not ask about. Compared with AWP alone, C-PR ranked the spenders that later gained new approvals far better (tau 0.295 against 0.044; paired difference +0.251, interval [0.203, 0.306]), and it was level with AWP on new senders. That is the claim in the title of the thesis: allowance edges brought into the transfer walk improve on the transfer-only baseline. I saw it after the labels were in, though, so for now it is a hypothesis and nothing more. This addendum tests it on labels that nobody has extracted yet.

One more disclosure. On 29 August I ran an exploratory holdout on the traders of the matched cohort, with the spring freeze date and the GMX success labels. It scored only EndorseRank and AWP, and AWP was ahead on every success label. It had no GMX liquidation label and no C-PR; its other labels, among them inverse risk and Aave liquidations, are in the same summary file. The thesis did not report it; it will now.

## 2. What stays fixed

- The operator is C-PR at lambda = 0.5, as fixed in the configuration on 14 September. The lambda = 0.25 and 0.75 variants and S-PR are reported as before. There is no new operator and no tuning.
- Solver settings do not change: damping 0.85, tolerance 1e-8, at most 300 iterations, AWP decay k = 0.01 per day with t0 = 180 days.
- The extraction repeats the spring one: same SQL, same filter of 5,521 wallets (the GMX V2 wallets with at least three closes between December and May), same decoder for the GMX events.
- Uncertainty comes from the same paired wallet bootstrap: 400 resamples, seed 42, 95 percent percentile intervals.

## 3. The new window

Scores are frozen on 31 May 2026 at 23:59:59 UTC and use every extracted event from 1 December 2025 up to that moment. Labels are counted from 1 June to 31 August 2026. The approval and transfer logs and the GMX closes for those three months have not been extracted, so I hold no label value when this file is committed.

The spender cohort is defined as in the spring: every spender holding at least one positive latest allowance at the freeze. The trader cohort is the 5,521 matched wallets that appear in the freeze-date graph. Membership was settled by closes made before the freeze, so it does not look ahead. The trader label is defined only for wallets with at least three GMX closes in the label window.

The spenders keep their two labels from the spring: new owner-spender approval pairs, and new transfer senders. The traders get a new one, the liquidation-free close rate: one minus the share of the wallet's June to August closes that ended in liquidation. It is the closest thing to a default that this data contains. It is built from neither graph, and because it is a rate it does not reward a wallet just for trading more. Those are the reasons I picked it. Two things about it were known when I picked it. One is how common liquidations are: in the spring window, 1,434 of the 2,962 matched wallets with at least three closes had at least one; among the wallets in the 28 February graph, which is how the trader cohort is drawn here, it was 923 of 1,860. The other is its same-window counterpart. The December to May liquidation-free rate is one of the proxies behind the archived liquidation family, and on its own it gives tau 0.075 for EndorseRank and 0.083 for AWP. It has never been computed for C-PR, and never out of window for any score.

## 4. The rule, fixed before the extraction

Each hypothesis compares C-PR (lambda = 0.5) with AWP on the same wallet resamples, through the difference tau(C-PR) - tau(AWP).

- F1. Spenders, new approval pairs: C-PR is better than AWP. The interval of the difference lies entirely above zero.
- F2. Spenders, new transfer senders: C-PR is not worse than AWP by more than 0.02. The lower end of the interval lies above -0.02.
- F3. Traders, liquidation-free close rate: C-PR is not worse than AWP by more than 0.02, judged the same way as F2.

The improvement claim needs all three. Since every one of them has to hold, no correction for multiple testing is needed. I set the margin at 0.02 because that was the half-width of the paired interval for this very contrast on new senders in the spring holdout; a smaller difference could not be resolved with samples of this size.

There is a weakness in F3 that I want on record. If neither score predicts liquidation, F3 can pass with both coefficients close to zero. The thesis will print the two coefficients next to the verdict, so that a pass is not read as evidence that either score predicts liquidation.

These are reported in this order and do not enter the decision:

- F4. C-PR against AWP on the liquidation-free close rate, as a superiority test.
- F5. C-PR against EndorseRank on the same label.
- F6. The primary part of the 14 September rule, rerun on the new window.
- Every single-layer, degree and hybrid row for every label, the GMX success labels included.

## 5. What the thesis will say in each case

If F1, F2 and F3 all hold, adding allowance edges to the transfer walk improves on AWP. The coupled score carries information about future authorization that AWP does not have, and it gives up no more than the 0.02 margin on inflow or on the liquidation risk of traders. This is a claim about improving the transfer-graph method. It does not say that C-PR beats both single layers: the null of 14 September stands, and EndorseRank on its own remains the stronger score for authorization.

If F1 holds but F2 or F3 fails, the coupling buys authorization at the cost of flow or risk ranking, and the thesis makes no improvement claim.

If F1 fails, the spring pattern did not replicate, and the thesis says so.

## 6. What I will not do

Once the extraction starts, I will not change lambda, the labels, the cohorts, the margin or the window, and I will not drop wallets or months. A query that fails is rerun unchanged. Every coefficient goes into the thesis, failures included.

## 7. Mechanics and cost

This file and config/fresh_holdout_2026q3.yaml go into the public repository in one commit, and in that commit the status in the configuration changes from "draft" to "registered". The extraction script will not run until both files are committed, and it writes their hashes into its manifest; the evaluation copies them into its summary. Before anything is downloaded, a dry run records the bytes each query will scan. By the spring figures, the six approval and transfer queries and the three GMX queries should scan about 1 TB in total.

## 8. Added on 1 October 2026, before registration

I added two checks after the post hoc checks in the thesis were done and before any June to August log was extracted. Both are reported next to the decision. Neither enters it, and neither changes anything in sections 2 to 6.

The first concerns the comparator. The AWP in this pipeline is an adaptation of the method of Do, Do and Nguyen (2023), not a copy of it. It weighs each transfer by its raw token amount and restarts the walk uniformly. The published form passes each amount through V(z) = 2/(1 + e^(-bz)) - 1, so that one transfer counts at most once, and it restarts the walk in proportion to how recently and how widely each address has sent. F1 to F4 are computed a second time with that form in place of AWP. The paper gives no value for b or for the decay, so the check uses b = 1 on raw base units (reputation.awp_paper in config/margin_config.yaml) and the decay of section 2.

The second concerns wallets that a graph leaves out. The main analysis scores them zero, which puts them below every wallet in the graph. Kept as isolated nodes, each of them would score like an address without in-edges. F1 to F6 are computed a second time under that rule. Only EndorseRank and AWP change: every spender is in the allowance graph, and every trader in the cohort is in the union graph that C-PR walks.

I also corrected the liquidation count in section 3, which had given the figure for all matched wallets rather than for those in the freeze-date graph.
