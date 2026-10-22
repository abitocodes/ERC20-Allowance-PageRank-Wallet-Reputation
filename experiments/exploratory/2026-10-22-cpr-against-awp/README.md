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

## Rerun

Needs the revised graph tables and the published score tables:

```powershell
python scripts/drive_sync.py pull "*graph-tables-usd/*"
python scripts/drive_sync.py pull "*2-processed-tables-and-evaluations/revised-usd/*"
python experiments/exploratory/2026-10-22-cpr-against-awp/scripts/run_cpr_awp.py
```
