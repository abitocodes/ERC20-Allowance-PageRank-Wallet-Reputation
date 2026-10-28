# Revision: scores from the twelve months before each freeze

- Written on 28 October 2026, after the registered results and the results of the US-dollar revision (`docs/revision_price_weighting.md`, on the 33-month window) were known, and committed **before any score, proxy, label or constant of the twelve-month windows was computed**. The commit that adds this file is the reference point of this revision.
- This is a further deviation from the analysis plan (`docs/analysis_plan.md`, commit 43d8045) and from the W1 registration (`docs/registration_w1.md`, commit 0d3a057). For the main analysis it replaces the score window of `registration_w1.md` section 1 ("every extracted event from 2023-10-01"), the data range of the constants in `revision_price_weighting.md` section 5 ("from 1 October 2023 to t1") and the line "Windows and anchors" of section 7 of that file. It is decided after results were seen, so its results are post hoc and are never called registered.
- The registered analysis and the 33-month US-dollar analysis stay as they were committed. Their configuration, SQL (`sql/01`–`19`), code paths (`CONTRACT_REP_VARIANT` unset and `=usd`) and outputs (`data/2-processed-tables-and-evaluations/`, `.../revised-usd/`, `data/3-published-results-for-thesis/`, `.../revised-usd/`, `data/1-raw-blockchain-extracts/graph-tables-usd/`, `data/0-usd-token-list-and-prices/constants.json`) are not changed. This revision adds the variant `CONTRACT_REP_VARIANT=usd12m`, with its own BigQuery tables (`u12_*`), folders and constants.

## 1. Why the windows are shortened

The main analysis should describe the contracts by their activity in the year before each freeze, the most recent data the study holds. In the 33-month window the quantities without time decay counted events of any age at full weight: the C-PR allowance layer and the in-approve degree and value counted an approval set up to 33 months before the anchor, the latest allowances that define the spender cohorts and the new-approval label reached back as far, and the cohort rule admitted contracts whose three owners had approved them years before the freeze. A window of twelve months bounds the age of every event that enters a score, a proxy, a baseline or a label history, and it gives the two freezes windows of the same length. The time decay already weights a one-year-old event at σ(365) = 0.136 against σ(0) = 0.858, so EndorseRank and AWP are expected to change less than the undecayed quantities, the cohorts and the labels.

## 2. Status of the analyses (decision of 28 October 2026)

- The twelve-month analysis is the main analysis of the thesis. Chapter 4 reports it.
- The registered analysis is reported as before: registered, with the verdicts of rule A, rule B (F1–F6 and its two sensitivity analyses) and R1–R3 exactly as they were obtained, in an appendix and in one table that sets the registered and main decision contrasts side by side.
- The 33-month US-dollar analysis is not reported in the thesis (author's decision). Its outputs stay in `data/.../revised-usd/` and on Drive as they are.
- On the twelve-month scores, rules A and B and R1–R3 are applied with the thresholds that were registered (including δ = 0.01). Those results are a re-analysis after the registered results were known, and the thesis says so wherever it reports them.
- The thesis describes the main analysis as a design and does not narrate how it was reached (author's decision). It states that the main analysis was defined after the registered results were known, lists the windows among the choices so defined, and describes the registered analysis with its own window. This file and the change record in `dissertation/notes/` record the change.
- The supervisors have not yet confirmed this decision.

## 3. Windows

| | Score window (both ends inclusive) | Anchor | Label window |
|---|---|---|---|
| Same window and W1 | 2025-07-01 00:00:00 UTC to 2026-06-30 23:59:59 UTC | T_obs = 2026-06-30 23:59:59 UTC | W1: 2026-07-01 to 2026-09-30 |
| W0 | 2025-04-01 00:00:00 UTC to 2026-03-31 23:59:59 UTC | t1 = 2026-03-31 23:59:59 UTC | W0: 2026-04-01 to 2026-06-30 |

`config/overlay_usd12m.yaml` holds the two window starts (`period.start_ts` and the new key `holdout.start_ts`); `scripts/common.py` merges it over `config/contract_reputation.yaml` for this variant only and refuses an overlay with any other key. The anchors, the label windows and every other setting come from the configuration file unchanged.

## 4. Window-dependent definitions

- **Cohorts, one per freeze.** The T_obs cohort: contracts that received a non-zero `Approval` of a selected token from at least three distinct owners inside the T_obs score window. The W0 cohort: the same rule inside the W0 score window, so that only data up to t1 choose it. A contract with three owners inside a twelve-month window also has them inside the 33-month window, so both cohorts are subsets of the 33-month US-dollar cohort (`u_cohort`) and of the registered cohort; their account types are known and no new `eth_getCode` read is needed. The T_obs cohort is the matched cohort of the same-window evaluation and the extraction filter of T_obs and W1; the W0 cohort is the extraction filter of t1 and W0.
- **Ego networks.** Approvals and transfers of the selected tokens with a contract of the freeze's cohort as owner, spender, sender or recipient: inside the score window for the graphs and the proxies, inside the label window for the labels (W0 from scan A, W1 from scan B).
- **Latest-allowance edges.** The latest approval of each (token, owner, spender) between the start of the score window and the anchor, in (block number, log index) order, kept when its value is positive. An allowance last set before the window start is not an edge even if it is still in force; the thesis states this limitation.
- **Spender cohorts of W0 and W1.** Contract spenders with a positive latest allowance of a selected token at the freeze in the freeze's ego network.
- **New approval pairs.** Label-window approvals of an owner–spender pair that has no positive latest allowance at the freeze. **New transfer senders.** Label-window senders of a spender not seen between the start of the score window and the freeze.
- **Revocations and the drain heuristic.** As in the USD revision, over the label window, with events taken from the freeze's ego network.
- **Proxies.** Computed inside the T_obs score window: transfer tenure is at most 365 days and active months at most 12.
- **Constants.** m_T, m_A and the cap U follow the rules of `revision_price_weighting.md` section 5 (as amended there), computed on the W0 score window and the W0 ego network (events from 2025-04-01 to t1), and are used at both freezes; no label window enters them. They are rounded to two significant digits and written to `data/0-usd-token-list-and-prices/usd-12m/constants.json`.
- **Tokens.** The five selected tokens of the USD revision are kept: WETH, USDC, USD₮0, ARB and WBTC. This is decided here, before any count of the twelve-month windows. The twelve-month row counts of all listed tokens in the registered ego data are computed (`sql/20`) and reported, and they do not change the list.
- **Prices.** As in the USD revision: a transfer at the price of its UTC day, a latest allowance at the price of the anchor's day.
- **Trader cohorts.** As registered (GMX V2 contract accounts with at least three closes in the label window), with membership in the freeze's twelve-month graph.
- **Sybil model, benchmark, robustness, supplementary contrasts.** The same code on the twelve-month graphs. A sample-definition or benchmark stage at or above the size of the cohort is left out.
- **Descriptive statistics.** `sql/22` counts events and quantities inside the score windows.

## 5. Unchanged

The extraction (scans A and B, the account-type reads, the GMX decoding; no public log is scanned again), the time decay (k = 0.01, t0 = 180 days, age from the anchor), the amount weights (V(z) with b = ln 3 / m, the cap rule for U) apart from the data range of the constants, the solver (d = 0.85, tolerance 10⁻⁸, at most 300 iterations, dangling mass through the restarts), the restarts of each method, the λ values, the raw degree baselines, the statistics (Kendall τ_b, Spearman ρ, 400 paired bootstrap resamples with seed 42, 2,000 for the outcome comparison), the decision thresholds of rules A and B and R1–R3, the benchmark protocol, the Sybil model and the robustness checks of the USD revision (slope ×10 and ÷10, damping, isolated-node rule, sample-definition stages).

## 6. Execution and cost

- Variant `CONTRACT_REP_VARIANT=usd12m`. `scripts/run_usd12m_pipeline.py` runs the BigQuery steps in order (`check`, `tokens`, `cohorts`, `constants`, `pairs`, `rest`, `checks`, `download`) and refuses to run unless this file, the overlay and the SQL it uses are committed without local changes. `scripts/run_usd_pipeline.py` refuses every variant but `usd`, so the 33-month tables cannot be overwritten.
- The twelve-month jobs write only tables named `u12_*` and read only the `u_*` and ego tables listed in the driver; `scripts/run_bq.py` checks both before a job runs. `sql/13`–`17` are reused unchanged through table renames; `sql/20`–`23` are new.
- Cost: about USD 2.7 (477 GB), estimated by `run_usd12m_pipeline.py check` from the monthly row counts of the two `describe/describe.json` files and the table metadata, times the bytes of the columns each query reads; the two label jobs add the log scan of the 33-month label jobs, which read the same partitions, and the node-id job is bounded by its 33-month bill. The jobs are labelled `usd12m:` and capped at USD 4.00 in total; a job is not run if the larger of its dry run and its estimate would pass the cap, or the study budget of USD 50, or if the dry run of its first statement exceeds 1.25 times the estimate of that statement (a partition filter that did not prune). If a job bills more than 1.5 times its estimate, the next job waits until the cause is understood. `--force` is not used.
- Outputs: `data/1-raw-blockchain-extracts/graph-tables-usd-12m/`, `data/2-processed-tables-and-evaluations/revised-usd-12m/`, `data/3-published-results-for-thesis/revised-usd-12m/`, `data/0-usd-token-list-and-prices/usd-12m/`.

## 7. Amendments

An amendment is allowed only before any twelve-month score is computed; it is dated and explained in place, as in the USD revision. After the first twelve-month score exists, nothing in this file changes.
