# Revision: amounts in USD over a list of price-verified tokens

- Written on 10 October 2026, after the registered results of the same window, W0 and W1 were known, and committed **before any revised score, proxy or label was computed**. The commit that adds this file is the reference point of the revision.
- This is a deviation from the analysis plan (`docs/analysis_plan.md`, commit 43d8045) and from the W1 registration (`docs/registration_w1.md`, commit 0d3a057). It is decided after results were seen, so the revised results are post hoc and are never called registered.
- The registered analysis stays as it was committed. Its configuration, SQL (`sql/01`–`11`), code path and outputs (`data/2-processed-tables-and-evaluations/*`, `data/3-published-results-for-thesis/*`) are not changed and can be rerun with `CONTRACT_REP_VARIANT` unset.

## 1. Why the amounts are revised

1. **The amount played no part in EndorseRank and AWP.** The plan applied V(z) = 2/(1+exp(−bz)) − 1 with b = 1 to raw base units. V(z) is within 10⁻⁴ of 1 for z ≥ 10 base units, and 99.52% of the ego transfers and 99.78% of the latest allowances at T_obs are at least 10 base units (`describe/describe.json`). An AWP edge therefore counts transfers and an EndorseRank edge counts approved tokens, each weighted by age. Do, Do and Nguyen (2023) introduce V so that larger transactions weigh more; the registered setting did not do that.
2. **The C-PR layers added incommensurable numbers.** The C-PR allowance layer summed raw allowances over tokens and the transfer layer summed raw transfer amounts over tokens. One USDC is 10⁶ base units and one WETH 10¹⁸, so a layer weight mixed scales that differ by twelve orders of magnitude, and unlimited allowances (2²⁵⁶ − 1, 45.3% of the latest allowances at T_obs) took almost the whole row of every owner that held one.
3. **Every ERC-20 contract counted.** A token contract can emit `Approval` and `Transfer` logs that name any address as owner or sender, without that address taking part; spam and address-poisoning tokens do this. A log of such a token is not evidence that the named owner endorsed the spender or paid the recipient. For widely used tokens with standard implementations, an `Approval` records an allowance that the owner set by calling `approve` or by signing a `permit` (or what is left of it after a `transferFrom`), and a `Transfer` moves a balance the sender held.

The three points are defects of the registered measurement, found after the registered results were known. They are corrected here by valuing every amount in USD and keeping only tokens whose USD price is reliable.

## 2. Status of the two analyses (decision of 10 October 2026)

- The revised analysis is the main analysis of the thesis. Chapter 4 reports it.
- The registered analysis is reported as registered, with the verdicts of rule A, rule B (F1–F6 and its two sensitivity analyses) and R1–R3 exactly as they were obtained, in an appendix and in one table that sets the registered and revised decision contrasts side by side.
- On the revised scores, rules A and B and R1–R3 are applied with the thresholds that were registered (including δ = 0.01). Those results are a re-analysis after the registered results were known, and the thesis says so wherever it reports them.
- Chapter 3 states the deviation, its reasons (section 1) and its date.
- The supervisors have not yet confirmed this decision.

## 3. Token list

A token is listed when all three conditions hold.

1. **A Chainlink market-price feed of low or medium risk.** Chainlink's directory of data feeds on Arbitrum One, read on 10 October 2026 (snapshot in `data/0-usd-token-list-and-prices/sources/`), has a standard market-price feed (product type `RefPrice`) quoted in USD or in ETH whose market-risk category is `low` or `medium`. Chainlink assigns the category from the depth, spread and concentration of the asset's markets; feeds rated `high`, `new` or not rated, exchange-rate and other custom feeds, hidden feeds and feeds scheduled for shutdown do not qualify. An exchange-rate feed reads a conversion rate from a contract and does not follow the market (on 10 October 2026 the USR exchange-rate feed read 1.000 while DefiLlama priced USR at 0.083).
2. **The feed prices this token.** The feed's base asset is the token itself; or the asset that the token wraps one-to-one through its issuer (WETH for ETH); or the Ethereum token of which the token is the copy minted by Arbitrum's canonical token bridge, when that Ethereum token is the asset's own issue (USDC.e for USDC). Tokens issued by other bridges (Axelar, Wormhole, Hyperlane and the like), copies of assets native to another chain, tokens for which the feed prices only an underlying asset (tokenised shares, cbBTC through BTC / USD) and tokens that copy a listed symbol at another address are not listed. Each identification was checked against the issuer's documentation, the Aave address book, the Arbitrum bridge token lists or CoinGecko's platform addresses, and against `symbol()`, `name()` and `decimals()` on the chain.
3. **The token occurs in the observation-window data** (ego transfers or latest allowances at T_obs).

When this file was written the rule gave about 64 tokens holding about 86% of the rows (transfers plus latest allowances at T_obs) of the registered ego data; the exact list, its counts and the rows of every other token are produced by `scripts/usd_inputs.py` and `sql/18_usd_describe.sql` and reported. An ETH-quoted feed qualifies a token as a USD-quoted one does (wstETH, weETH, rETH, cbETH); the feeds decide only which tokens are listed, and every listed token's USD price comes from DefiLlama (section 4).

Wrapped XRP is not listed. Hex Trust's wXRP is not deployed on Arbitrum One (no code at its address; the issuer lists Ethereum, Optimism, HyperEVM and Solana). The XRP-backed tokens that do exist there are tiny and have no Chainlink feed of their own: uXRP of Universal Protocol (about 25,000 tokens, 11,729 rows of the data) and a canonical-bridge copy of Wrapped.com's Ethereum WXRP (2.13 tokens, 38 rows), whose Ethereum token is itself a custodial wrapper, not XRP.

- Each listed token is recorded in `data/0-usd-token-list-and-prices/listed_tokens.csv` with address, symbol, name, decimals (read with `eth_call` at one pinned block), the feed, its category and the evidence that puts it on the list; `token_candidates.csv` in the same folder lists every token the Chainlink directory mapped to an Arbitrum One address, with the reason it is or is not listed.
- Every other token is left out. The number of tokens and the rows left out are counted per stream and window in `u_describe_tokens` (section 9) and reported; nothing is dropped without being counted.
- Native ETH is not an ERC-20 token and moves without `Transfer` logs (top-level value transfers and internal calls), so the logs used here never contained it. ETH enters the graphs through WETH only, and the thesis states this limitation.

## 4. Prices

- Source: the DefiLlama coins API, daily chart of each listed token by its Arbitrum One address (`coins.llama.fi/chart/arbitrum:<address>`, `period=1d`), fetched once and stored in `data/0-usd-token-list-and-prices/daily_prices_usd.csv` with DefiLlama's confidence value, the key used and the fetch time.
- Day alignment: DefiLlama's daily point is the price record nearest a 00:00 UTC grid time (within about ±2.4 hours). The point nearest 00:00 UTC of day D+1 is the closing price of day D, and it is the price of day D.
- Second key: for several canonical tokens DefiLlama's Arbitrum series starts long after the token's first use (WETH on 16 August 2024, USD₮0 on 24 January 2025). A day without a point under the Arbitrum key takes the point of a second DefiLlama key for the same asset (`coingecko:<id>` or the asset's Ethereum address), provided that on the days both keys have a point their median absolute relative difference is below 1%. The key of every day is recorded.
- Errors: a daily point that is more than twice, or less than half, both the previous and the next day's point, while those two lie within a factor of two of each other, is treated as a data error, replaced by the previous day's price and flagged.
- Gaps: a day still without a price takes the previous day's price (`filled`); filled days are counted per token. No price is carried backwards before a token's first point; an event on such a day has no price and is counted.
- Check: for a sample of tokens and dates the DefiLlama price is compared with the Chainlink feed on Arbitrum One read on-chain (`scripts/chainlink_check.py`); the differences are reported in the appendix. A scouting run before this file was written found median absolute differences of 0.01–0.04% and at most 0.56% for ETH and USDC on 37 dates.
- A transfer is valued at the price of its UTC day. A latest allowance is valued at the price of the anchor's UTC day (30 June 2026 at T_obs, 31 March 2026 at t1), since it is the permission in force at the anchor that the edge represents.
- USD value = raw value / 10^decimals × price, in double precision (`scripts/usd.py`, mirrored in SQL).

## 5. Amount weights

- EndorseRank and AWP keep V(z) = 2/(1+exp(−bz)) − 1, now with z in USD. The slope is set so that V of the median amount is one half: b = ln 3 / m. m_T is the median USD value of the ego transfers of listed tokens from 1 October 2023 to t1, and m_A the median USD value at t1 prices of the finite latest allowances at t1 (below 1.15 × 10⁷⁷ base units). Both use only events up to t1 = 31 March 2026, the earlier freeze, so no label window enters them. The medians are computed by `sql/13_usd_constants.sql` (BigQuery `APPROX_QUANTILES`, 10,000 buckets) and rounded to two significant digits; b is computed from the rounded value.
- An unlimited allowance has V = 1, the most an approval can weigh.
- C-PR transfer layer: Σ_e usd_e · σ(Δt_e), the registered form with USD in place of base units.
- C-PR allowance layer: Σ_token min(usd, U). U is the 99th percentile of the USD values, at t1 prices, of the finite positive latest allowances at t1, rounded to two significant digits (`sql/13_usd_constants.sql`). Every allowance at or above U counts U, so an unlimited allowance (and any allowance too large to be spent, such as 2¹²⁸) weighs as much as the largest finite ones instead of taking the owner's whole row. The number of allowances at or above U is reported.
- S-PR walks the USD transfer layer with restarts from C-PR (λ = 1) on the USD allowance layer.
- Proxies: in-value is the USD sum of inbound transfers; in-approve value is the spender's sum of the C-PR allowance layer weights.

## 6. Scope

Every quantity is restricted to the listed tokens:

- Matched cohort: contracts that, inside the observation window, received a non-zero `Approval` of a listed token from at least three distinct owners. Such a contract received non-zero approvals from three owners on some token, so it is a member of the registered cohort; its account type is already known, and no new `eth_getCode` read is needed.
- Graphs: approvals and transfers of listed tokens with a contract of the revised cohort as owner, spender, sender or recipient. These events are a subset of the registered ego tables, which hold every event touching a registered cohort contract; no public log is scanned again.
- Spender cohorts of W0 and W1: contract spenders with a positive latest allowance of a listed token at the freeze in the revised approval data (a subset of the registered spender cohorts, whose account types are known).
- Trader cohort: as registered (GMX V2 contract accounts with at least three closes in the window), with membership in the revised freeze-date graph.
- Labels: new approval pairs, new transfer senders, revocations and the drain heuristic count events of listed tokens only. The GMX trader labels do not depend on tokens and are unchanged.

## 7. Unchanged

Windows and anchors, the logistic decay (k = 0.01, t0 = 180 days), the solver (d = 0.85, tolerance 10⁻⁸, at most 300 iterations, dangling mass through the restarts), restarts of each method, λ values, the raw degree baselines (now counted on listed tokens), the statistics (Kendall τ_b, Spearman ρ, 400 paired bootstrap resamples with seed 42, 2,000 for the outcome comparison), the decision thresholds of rules A and B and R1–R3, the benchmark protocol and the Sybil model.

## 8. Robustness

The top-20-token subgraph check of the plan (section 5) loses its point once every graph keeps only listed tokens. It is replaced by a check of the new free parameter: EndorseRank and AWP are recomputed at T_obs with the slope b multiplied and divided by ten (the edge weights come from the same query as the main weights), and their family means on the matched cohort and their rank agreement with the main scores are reported without intervals, as the token check was. The damping sweep, the isolated-node rule and the sample-definition stages are unchanged.

The registered analysis keeps its top-20-token check as registered.

## 9. Execution

Inputs: `scripts/usd_inputs.py` applies the rule of section 3 to the Chainlink directory snapshot and the reviewed candidate table, reads symbol, name and decimals at one pinned block, fetches and builds the daily prices of section 4 and writes `data/0-usd-token-list-and-prices/`; `scripts/chainlink_check.py` writes the Chainlink comparison.

BigQuery (each query dry-run first by `scripts/run_bq.py`, all within the study's USD 50 budget; `scripts/run_usd_pipeline.py` runs the steps in order):

1. Load `u_tokens` and `u_prices` from the CSV files (load jobs are not billed).
2. `sql/12_usd_ego.sql`: revised cohort and listed-token ego tables (`u_cohort`, `u_approvals`, `u_transfers`, `u_approvals_w1`, `u_transfers_w1`).
3. `sql/13_usd_constants.sql`: medians and quantiles up to t1 (`u_constants`).
4. `sql/14_usd_anchor_pairs.sql` at T_obs and t1.
5. `sql/15_usd_proxies.sql`; `sql/16_usd_labels.sql` for W0 and W1; `sql/17_usd_export_ids.sql`; `sql/18_usd_describe.sql`.
6. Download the `u_x_*`, `u_proxies_tobs` and `u_labels_*` tables into `data/1-raw-blockchain-extracts/graph-tables-usd/`.

Locally, with `CONTRACT_REP_VARIANT=usd` (outputs under `data/2-processed-tables-and-evaluations/revised-usd/` and `data/3-published-results-for-thesis/revised-usd/`): `run_same_window.py`, `run_holdout.py`, `run_registered.py`, `run_robustness.py`, `run_benchmark.py`, `run_supplementary.py`, `sybil_model.py`, the descriptive summary, `publish_results.py`, `export_latex.py`.
