# Results digest

Written by `experiments/scripts/publish_results.py` on 2026-10-28 09:38 UTC from the summaries in this folder; nothing here is recomputed. Each row names the file (relative to this folder) and the key inside it. τ entries read `point [95% CI]`, contrasts `Δτ [95% CI]; τa, τb; P(Δτ>0)`, and `B` is the number of bootstrap resamples behind the interval. `SHA256SUMS.txt` lists the checksums of every file published here.

**Revised analysis, twelve-month score windows** (docs/revision_one_year_window.md on top of docs/revision_price_weighting.md): amounts in USD over the five selected tokens, scores from the twelve months before each freeze (T_obs and W1: 2025-07-01 to 2026-06-30; W0: 2025-04-01 to 2026-03-31), decided after the registered results were known. Nothing in this digest is a registered result; the registered digest is in the parent folder.

- Code revision: `0a9421563a529762662ccaef4d86ac96bfad03f6`
- Published files: `same-window/eval_summary.json`, `holdout-w0/eval_summary.json`, `window-w1/eval_summary.json`, `registered-w1/extraction_manifest.json`, `sybil-model/sybil_model.json`, `robustness/robustness.json`, `benchmark/benchmark.json`, `supplementary/supplementary.json`, `describe/describe.json`, `cohort/matched_cohort.json`, `gmx/gmx_contract_closes_obs_decoded.json`, `gmx/gmx_contract_closes_w1_decoded.json`, `config/contract_reputation.yaml`, `docs/analysis_plan.md`, `docs/registration_w1.md`, `docs/revision_price_weighting.md`, `usd/listed_tokens.csv`, `usd/usd_inputs.json`, `usd/constants.json`, `usd/chainlink_check.json`, `docs/revision_one_year_window.md`, `config/overlay_usd12m.yaml`, `usd/token_rows_12m.json`, `cohort/cohort_t1.json`, `run_manifest.json`

## 1. Cohort and graph sizes

| Quantity | Value | Source |
|---|---|---|
| Cohort rule | contracts of the registered cohort with non-zero approvals of a selected token (WETH, USDC, USDT0, ARB, WBTC) from >= 3 distinct owners, 2025-07-01 00:00:00 UTC to 2026-07-01 00:00:00 UTC (end exclusive) | `cohort/matched_cohort.json` : `rule` |
| Candidate spenders | None | `cohort/matched_cohort.json` : `candidates` |
| Matched cohort (contracts) | 6,483 | `cohort/matched_cohort.json` : `cohort` |
| Revised cohort: registered cohort | 27,844 | `cohort/matched_cohort.json` : `registered_cohort` |
| Revised cohort: left out of registered | 21,361 | `cohort/matched_cohort.json` : `left_out_of_registered` |
| W0 cohort rule | contracts of the registered cohort with non-zero approvals of a selected token (WETH, USDC, USDT0, ARB, WBTC) from >= 3 distinct owners, 2025-04-01 00:00:00 UTC to 2026-04-01 00:00:00 UTC (end exclusive) | `cohort/cohort_t1.json` : `rule` |
| W0 cohort: cohort | 6,343 | `cohort/cohort_t1.json` : `cohort` |
| W0 cohort: registered cohort | 27,844 | `cohort/cohort_t1.json` : `registered_cohort` |
| W0 cohort: left out of registered | 21,501 | `cohort/cohort_t1.json` : `left_out_of_registered` |
| W0 cohort: in tobs cohort | 5,383 | `cohort/cohort_t1.json` : `in_tobs_cohort` |
| Anchor T_obs | 2026-06-30 23:59:59 UTC | `same-window/eval_summary.json` : `anchor` |
| Cohort scored in the same window | 6,483 | `same-window/eval_summary.json` : `cohort` |
| T_obs allowance graph, nodes | 2,514,846 | `same-window/eval_summary.json` : `graph.allowance.nodes` |
| T_obs allowance graph, edges | 3,808,949 | `same-window/eval_summary.json` : `graph.allowance.edges` |
| T_obs transfer graph, nodes | 3,603,300 | `same-window/eval_summary.json` : `graph.transfer.nodes` |
| T_obs transfer graph, edges | 8,426,124 | `same-window/eval_summary.json` : `graph.transfer.edges` |
| Cohort contracts outside the allowance graph | 191 | `same-window/eval_summary.json` : `graph.cohort_outside_allowance` |
| Cohort contracts outside the transfer graph | 1,192 | `same-window/eval_summary.json` : `graph.cohort_outside_transfer` |
| Cohort contracts outside both graphs | 30 | `same-window/eval_summary.json` : `graph.cohort_outside_both` |
| Power iterations at T_obs, EndorseRank | 57 | `same-window/eval_summary.json` : `iterations.endorserank` |
| Power iterations at T_obs, EndorseRank (activity restarts) | 55 | `same-window/eval_summary.json` : `iterations.endorserank_activity` |
| Power iterations at T_obs, AWP | 94 | `same-window/eval_summary.json` : `iterations.awp` |
| Power iterations at T_obs, C-PR (λ=1) | 56 | `same-window/eval_summary.json` : `iterations.cpr_l100` |
| Power iterations at T_obs, C-PR (λ=0) | 92 | `same-window/eval_summary.json` : `iterations.cpr_l0` |
| Power iterations at T_obs, C-PR (λ=0.25) | 82 | `same-window/eval_summary.json` : `iterations.cpr_l25` |
| Power iterations at T_obs, C-PR (λ=0.5) | 82 | `same-window/eval_summary.json` : `iterations.cpr_l50` |
| Power iterations at T_obs, C-PR (λ=0.75) | 82 | `same-window/eval_summary.json` : `iterations.cpr_l75` |
| Power iterations at T_obs, S-PR | 151 | `same-window/eval_summary.json` : `iterations.spr` |
| t1 graph, allowance edges | 4,117,103 | `holdout-w0/eval_summary.json` : `graph.allowance_edges` |
| t1 graph, transfer edges | 9,198,965 | `holdout-w0/eval_summary.json` : `graph.transfer_edges` |
| Power iterations at t1, EndorseRank | 59 | `holdout-w0/eval_summary.json` : `iterations.endorserank` |
| Power iterations at t1, EndorseRank (activity restarts) | 51 | `holdout-w0/eval_summary.json` : `iterations.endorserank_activity` |
| Power iterations at t1, AWP | 92 | `holdout-w0/eval_summary.json` : `iterations.awp` |
| Power iterations at t1, C-PR (λ=1) | 59 | `holdout-w0/eval_summary.json` : `iterations.cpr_l100` |
| Power iterations at t1, C-PR (λ=0) | 92 | `holdout-w0/eval_summary.json` : `iterations.cpr_l0` |
| Power iterations at t1, C-PR (λ=0.25) | 84 | `holdout-w0/eval_summary.json` : `iterations.cpr_l25` |
| Power iterations at t1, C-PR (λ=0.5) | 85 | `holdout-w0/eval_summary.json` : `iterations.cpr_l50` |
| Power iterations at t1, C-PR (λ=0.75) | 85 | `holdout-w0/eval_summary.json` : `iterations.cpr_l75` |
| Power iterations at t1, S-PR | 153 | `holdout-w0/eval_summary.json` : `iterations.spr` |
| GMX V2 contract closes (obs), input rows | 133,685 | `gmx/gmx_contract_closes_obs_decoded.json` : `input_rows` |
| GMX V2 contract closes (obs), decoded rows | 133,685 | `gmx/gmx_contract_closes_obs_decoded.json` : `decoded_rows` |
| GMX V2 contract closes (obs), errors | 0 | `gmx/gmx_contract_closes_obs_decoded.json` : `errors` |
| GMX V2 contract closes (obs), liquidations | 6,473 | `gmx/gmx_contract_closes_obs_decoded.json` : `liquidations` |
| GMX V2 contract closes (w1), input rows | 6,805 | `gmx/gmx_contract_closes_w1_decoded.json` : `input_rows` |
| GMX V2 contract closes (w1), decoded rows | 6,805 | `gmx/gmx_contract_closes_w1_decoded.json` : `decoded_rows` |
| GMX V2 contract closes (w1), errors | 0 | `gmx/gmx_contract_closes_w1_decoded.json` : `errors` |
| GMX V2 contract closes (w1), liquidations | 182 | `gmx/gmx_contract_closes_w1_decoded.json` : `liquidations` |
| W1 extraction: started at | 2026-10-09T16:49:33+00:00 | `registered-w1/extraction_manifest.json` : `started_at` |
| W1 extraction: finished at | 2026-10-09T16:50:55+00:00 | `registered-w1/extraction_manifest.json` : `finished_at` |
| W1 extraction: head | 0d3a057e4f0c8473d36d89fbe33c24deff0c9911 | `registered-w1/extraction_manifest.json` : `head` |
| W1 extraction: registration commit | 0d3a057e4f0c8473d36d89fbe33c24deff0c9911 2026-10-10T01:49:32+09:00 | `registered-w1/extraction_manifest.json` : `registration_commit` |
| W1 extraction: override used | no | `registered-w1/extraction_manifest.json` : `override_used` |
| W1 extraction: SHA-256 of docs/registration_w1.md | 2126c8dc3fe3c0f9273aa4ecfc1e15bddc1f5a6f65e98548b9528f2b18ca2a6b | `registered-w1/extraction_manifest.json` : `sha256.docs/registration_w1.md` |
| W1 extraction: SHA-256 of config/contract_reputation.yaml | d6a30adbcabcf511d6892332da73639efdbece25891b392e13e90faf09b7a833 | `registered-w1/extraction_manifest.json` : `sha256.config/contract_reputation.yaml` |

## 2. Same-window families (matched cohort)

Family mean of Kendall τ_b with its 95% percentile interval (paired bootstrap over contracts).

| Quantity | Value | Source |
|---|---|---|
| EndorseRank, transfer family | 0.196 [0.180, 0.216]; B=400 | `same-window/eval_summary.json` : `families.endorserank.transfer` |
| EndorseRank, allowance family | 0.560 [0.548, 0.571]; B=400 | `same-window/eval_summary.json` : `families.endorserank.allowance` |
| EndorseRank, Sybil stability family | 0.026 [0.012, 0.041]; B=400 | `same-window/eval_summary.json` : `families.endorserank.sybil_stability` |
| EndorseRank (activity restarts), transfer family | 0.251 [0.233, 0.271]; B=400 | `same-window/eval_summary.json` : `families.endorserank_activity.transfer` |
| EndorseRank (activity restarts), allowance family | 0.601 [0.590, 0.613]; B=400 | `same-window/eval_summary.json` : `families.endorserank_activity.allowance` |
| EndorseRank (activity restarts), Sybil stability family | 0.056 [0.042, 0.072]; B=400 | `same-window/eval_summary.json` : `families.endorserank_activity.sybil_stability` |
| AWP, transfer family | 0.736 [0.728, 0.744]; B=400 | `same-window/eval_summary.json` : `families.awp.transfer` |
| AWP, allowance family | 0.226 [0.210, 0.245]; B=400 | `same-window/eval_summary.json` : `families.awp.allowance` |
| AWP, Sybil stability family | 0.419 [0.408, 0.434]; B=400 | `same-window/eval_summary.json` : `families.awp.sybil_stability` |
| C-PR (λ=1), transfer family | 0.196 [0.180, 0.216]; B=400 | `same-window/eval_summary.json` : `families.cpr_l100.transfer` |
| C-PR (λ=1), allowance family | 0.561 [0.550, 0.572]; B=400 | `same-window/eval_summary.json` : `families.cpr_l100.allowance` |
| C-PR (λ=1), Sybil stability family | 0.028 [0.014, 0.042]; B=400 | `same-window/eval_summary.json` : `families.cpr_l100.sybil_stability` |
| C-PR (λ=0), transfer family | 0.700 [0.691, 0.709]; B=400 | `same-window/eval_summary.json` : `families.cpr_l0.transfer` |
| C-PR (λ=0), allowance family | 0.194 [0.178, 0.213]; B=400 | `same-window/eval_summary.json` : `families.cpr_l0.allowance` |
| C-PR (λ=0), Sybil stability family | 0.402 [0.389, 0.417]; B=400 | `same-window/eval_summary.json` : `families.cpr_l0.sybil_stability` |
| C-PR (λ=0.25), transfer family | 0.422 [0.407, 0.438]; B=400 | `same-window/eval_summary.json` : `families.cpr_l25.transfer` |
| C-PR (λ=0.25), allowance family | 0.430 [0.418, 0.444]; B=400 | `same-window/eval_summary.json` : `families.cpr_l25.allowance` |
| C-PR (λ=0.25), Sybil stability family | 0.157 [0.143, 0.170]; B=400 | `same-window/eval_summary.json` : `families.cpr_l25.sybil_stability` |
| C-PR (λ=0.5), transfer family | 0.400 [0.385, 0.416]; B=400 | `same-window/eval_summary.json` : `families.cpr_l50.transfer` |
| C-PR (λ=0.5), allowance family | 0.449 [0.437, 0.463]; B=400 | `same-window/eval_summary.json` : `families.cpr_l50.allowance` |
| C-PR (λ=0.5), Sybil stability family | 0.142 [0.128, 0.156]; B=400 | `same-window/eval_summary.json` : `families.cpr_l50.sybil_stability` |
| C-PR (λ=0.75), transfer family | 0.377 [0.361, 0.393]; B=400 | `same-window/eval_summary.json` : `families.cpr_l75.transfer` |
| C-PR (λ=0.75), allowance family | 0.464 [0.452, 0.478]; B=400 | `same-window/eval_summary.json` : `families.cpr_l75.allowance` |
| C-PR (λ=0.75), Sybil stability family | 0.129 [0.115, 0.143]; B=400 | `same-window/eval_summary.json` : `families.cpr_l75.sybil_stability` |
| S-PR, transfer family | 0.671 [0.661, 0.681]; B=400 | `same-window/eval_summary.json` : `families.spr.transfer` |
| S-PR, allowance family | 0.289 [0.272, 0.308]; B=400 | `same-window/eval_summary.json` : `families.spr.allowance` |
| S-PR, Sybil stability family | 0.398 [0.386, 0.414]; B=400 | `same-window/eval_summary.json` : `families.spr.sybil_stability` |

### Per proxy (τ_b [95% CI]; Spearman ρ)

| Quantity | Value | Source |
|---|---|---|
| EndorseRank, in_degree | 0.218 [0.199, 0.238]; ρ 0.302; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank.in_degree` |
| EndorseRank, in_value | 0.175 [0.157, 0.194]; ρ 0.256; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank.in_value` |
| EndorseRank, in_approve_degree | 0.650 [0.639, 0.661]; ρ 0.804; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank.in_approve_degree` |
| EndorseRank, in_approve_value | 0.469 [0.454, 0.484]; ρ 0.628; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank.in_approve_value` |
| EndorseRank, inbound_counterparty_ratio | -0.197 [-0.213, -0.180]; ρ -0.290; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank.inbound_counterparty_ratio` |
| EndorseRank, transfer_tenure_days | 0.133 [0.114, 0.153]; ρ 0.199; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank.transfer_tenure_days` |
| EndorseRank, active_months | 0.143 [0.124, 0.164]; ρ 0.203; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank.active_months` |
| EndorseRank (activity restarts), in_degree | 0.272 [0.252, 0.292]; ρ 0.355; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank_activity.in_degree` |
| EndorseRank (activity restarts), in_value | 0.231 [0.213, 0.251]; ρ 0.319; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank_activity.in_value` |
| EndorseRank (activity restarts), in_approve_degree | 0.669 [0.659, 0.680]; ρ 0.820; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank_activity.in_approve_degree` |
| EndorseRank (activity restarts), in_approve_value | 0.534 [0.520, 0.549]; ρ 0.697; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank_activity.in_approve_value` |
| EndorseRank (activity restarts), inbound_counterparty_ratio | -0.138 [-0.154, -0.121]; ρ -0.197; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank_activity.inbound_counterparty_ratio` |
| EndorseRank (activity restarts), transfer_tenure_days | 0.145 [0.127, 0.166]; ρ 0.208; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank_activity.transfer_tenure_days` |
| EndorseRank (activity restarts), active_months | 0.161 [0.143, 0.182]; ρ 0.220; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank_activity.active_months` |
| AWP, in_degree | 0.742 [0.732, 0.752]; ρ 0.883; B=400 | `same-window/eval_summary.json` : `per_proxy.awp.in_degree` |
| AWP, in_value | 0.730 [0.720, 0.740]; ρ 0.887; B=400 | `same-window/eval_summary.json` : `per_proxy.awp.in_value` |
| AWP, in_approve_degree | 0.242 [0.223, 0.262]; ρ 0.320; B=400 | `same-window/eval_summary.json` : `per_proxy.awp.in_approve_degree` |
| AWP, in_approve_value | 0.211 [0.193, 0.229]; ρ 0.294; B=400 | `same-window/eval_summary.json` : `per_proxy.awp.in_approve_value` |
| AWP, inbound_counterparty_ratio | 0.055 [0.033, 0.079]; ρ 0.163; B=400 | `same-window/eval_summary.json` : `per_proxy.awp.inbound_counterparty_ratio` |
| AWP, transfer_tenure_days | 0.588 [0.575, 0.600]; ρ 0.763; B=400 | `same-window/eval_summary.json` : `per_proxy.awp.transfer_tenure_days` |
| AWP, active_months | 0.616 [0.603, 0.629]; ρ 0.768; B=400 | `same-window/eval_summary.json` : `per_proxy.awp.active_months` |
| C-PR (λ=1), in_degree | 0.218 [0.200, 0.237]; ρ 0.301; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l100.in_degree` |
| C-PR (λ=1), in_value | 0.174 [0.157, 0.195]; ρ 0.256; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l100.in_value` |
| C-PR (λ=1), in_approve_degree | 0.643 [0.631, 0.653]; ρ 0.796; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l100.in_approve_degree` |
| C-PR (λ=1), in_approve_value | 0.479 [0.463, 0.494]; ρ 0.638; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l100.in_approve_value` |
| C-PR (λ=1), inbound_counterparty_ratio | -0.192 [-0.208, -0.175]; ρ -0.283; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l100.inbound_counterparty_ratio` |
| C-PR (λ=1), transfer_tenure_days | 0.133 [0.115, 0.152]; ρ 0.198; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l100.transfer_tenure_days` |
| C-PR (λ=1), active_months | 0.143 [0.124, 0.162]; ρ 0.202; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l100.active_months` |
| C-PR (λ=0), in_degree | 0.713 [0.703, 0.724]; ρ 0.859; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l0.in_degree` |
| C-PR (λ=0), in_value | 0.688 [0.676, 0.698]; ρ 0.853; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l0.in_value` |
| C-PR (λ=0), in_approve_degree | 0.228 [0.209, 0.249]; ρ 0.299; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l0.in_approve_degree` |
| C-PR (λ=0), in_approve_value | 0.161 [0.143, 0.180]; ρ 0.229; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l0.in_approve_value` |
| C-PR (λ=0), inbound_counterparty_ratio | 0.110 [0.090, 0.134]; ρ 0.222; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l0.inbound_counterparty_ratio` |
| C-PR (λ=0), transfer_tenure_days | 0.536 [0.522, 0.550]; ρ 0.710; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l0.transfer_tenure_days` |
| C-PR (λ=0), active_months | 0.560 [0.546, 0.575]; ρ 0.712; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l0.active_months` |
| C-PR (λ=0.25), in_degree | 0.419 [0.401, 0.435]; ρ 0.544; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l25.in_degree` |
| C-PR (λ=0.25), in_value | 0.426 [0.410, 0.442]; ρ 0.567; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l25.in_value` |
| C-PR (λ=0.25), in_approve_degree | 0.472 [0.458, 0.487]; ρ 0.622; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l25.in_approve_degree` |
| C-PR (λ=0.25), in_approve_value | 0.389 [0.375, 0.404]; ρ 0.543; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l25.in_approve_value` |
| C-PR (λ=0.25), inbound_counterparty_ratio | -0.151 [-0.167, -0.134]; ρ -0.205; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l25.inbound_counterparty_ratio` |
| C-PR (λ=0.25), transfer_tenure_days | 0.304 [0.288, 0.320]; ρ 0.429; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l25.transfer_tenure_days` |
| C-PR (λ=0.25), active_months | 0.317 [0.300, 0.333]; ρ 0.431; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l25.active_months` |
| C-PR (λ=0.5), in_degree | 0.397 [0.380, 0.414]; ρ 0.517; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l50.in_degree` |
| C-PR (λ=0.5), in_value | 0.403 [0.387, 0.419]; ρ 0.541; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l50.in_value` |
| C-PR (λ=0.5), in_approve_degree | 0.489 [0.476, 0.505]; ρ 0.639; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l50.in_approve_degree` |
| C-PR (λ=0.5), in_approve_value | 0.409 [0.396, 0.425]; ρ 0.567; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l50.in_approve_value` |
| C-PR (λ=0.5), inbound_counterparty_ratio | -0.158 [-0.174, -0.141]; ρ -0.218; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l50.inbound_counterparty_ratio` |
| C-PR (λ=0.5), transfer_tenure_days | 0.286 [0.269, 0.302]; ρ 0.404; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l50.transfer_tenure_days` |
| C-PR (λ=0.5), active_months | 0.298 [0.282, 0.316]; ρ 0.408; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l50.active_months` |
| C-PR (λ=0.75), in_degree | 0.375 [0.358, 0.393]; ρ 0.492; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l75.in_degree` |
| C-PR (λ=0.75), in_value | 0.379 [0.362, 0.395]; ρ 0.513; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l75.in_value` |
| C-PR (λ=0.75), in_approve_degree | 0.502 [0.489, 0.518]; ρ 0.652; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l75.in_approve_degree` |
| C-PR (λ=0.75), in_approve_value | 0.426 [0.413, 0.441]; ρ 0.585; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l75.in_approve_value` |
| C-PR (λ=0.75), inbound_counterparty_ratio | -0.161 [-0.176, -0.144]; ρ -0.225; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l75.inbound_counterparty_ratio` |
| C-PR (λ=0.75), transfer_tenure_days | 0.267 [0.251, 0.284]; ρ 0.380; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l75.transfer_tenure_days` |
| C-PR (λ=0.75), active_months | 0.280 [0.263, 0.298]; ρ 0.385; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l75.active_months` |
| S-PR, in_degree | 0.665 [0.654, 0.677]; ρ 0.820; B=400 | `same-window/eval_summary.json` : `per_proxy.spr.in_degree` |
| S-PR, in_value | 0.677 [0.665, 0.689]; ρ 0.845; B=400 | `same-window/eval_summary.json` : `per_proxy.spr.in_value` |
| S-PR, in_approve_degree | 0.325 [0.307, 0.347]; ρ 0.410; B=400 | `same-window/eval_summary.json` : `per_proxy.spr.in_approve_degree` |
| S-PR, in_approve_value | 0.253 [0.234, 0.271]; ρ 0.344; B=400 | `same-window/eval_summary.json` : `per_proxy.spr.in_approve_value` |
| S-PR, inbound_counterparty_ratio | 0.085 [0.065, 0.110]; ρ 0.194; B=400 | `same-window/eval_summary.json` : `per_proxy.spr.inbound_counterparty_ratio` |
| S-PR, transfer_tenure_days | 0.539 [0.526, 0.555]; ρ 0.714; B=400 | `same-window/eval_summary.json` : `per_proxy.spr.transfer_tenure_days` |
| S-PR, active_months | 0.570 [0.556, 0.585]; ρ 0.724; B=400 | `same-window/eval_summary.json` : `per_proxy.spr.active_months` |

## 3. Same-window contrasts, score agreement and rule A (secondary part)

| Quantity | Value | Source |
|---|---|---|
| [hybrid] C-PR transfer minus C-PR (l=0) transfer | Δτ -0.300 [-0.318, -0.281]; τa 0.400, τb 0.700; P(Δτ>0) 0.000; B=400 | `same-window/eval_summary.json` : `contrasts[0]` |
| [hybrid] C-PR allowance minus C-PR (l=1) allowance | Δτ -0.112 [-0.124, -0.100]; τa 0.449, τb 0.561; P(Δτ>0) 0.000; B=400 | `same-window/eval_summary.json` : `contrasts[1]` |
| [hybrid] C-PR sybil minus C-PR (l=0) sybil | Δτ -0.260 [-0.278, -0.241]; τa 0.142, τb 0.402; P(Δτ>0) 0.000; B=400 | `same-window/eval_summary.json` : `contrasts[2]` |
| [hybrid] C-PR sybil minus C-PR (l=1) sybil | Δτ 0.115 [0.104, 0.123]; τa 0.142, τb 0.028; P(Δτ>0) 1.000; B=400 | `same-window/eval_summary.json` : `contrasts[3]` |
| [hybrid] S-PR transfer minus C-PR (l=0) transfer | Δτ -0.029 [-0.036, -0.023]; τa 0.671, τb 0.700; P(Δτ>0) 0.000; B=400 | `same-window/eval_summary.json` : `contrasts[4]` |
| [hybrid] S-PR allowance minus C-PR (l=1) allowance | Δτ -0.272 [-0.290, -0.253]; τa 0.289, τb 0.561; P(Δτ>0) 0.000; B=400 | `same-window/eval_summary.json` : `contrasts[5]` |
| [hybrid] S-PR sybil minus C-PR (l=0) sybil | Δτ -0.004 [-0.008, 0.0001815]; τa 0.398, τb 0.402; P(Δτ>0) 0.037; B=400 | `same-window/eval_summary.json` : `contrasts[6]` |
| [hybrid] S-PR sybil minus C-PR (l=1) sybil | Δτ 0.371 [0.351, 0.390]; τa 0.398, τb 0.028; P(Δτ>0) 1.000; B=400 | `same-window/eval_summary.json` : `contrasts[7]` |
| [hybrid_single] C-PR transfer minus AWP transfer | Δτ -0.336 [-0.354, -0.316]; τa 0.400, τb 0.736; P(Δτ>0) 0.000; B=400 | `same-window/eval_summary.json` : `contrasts[8]` |
| [hybrid_single] C-PR allowance minus EndorseRank allowance | Δτ -0.111 [-0.122, -0.099]; τa 0.449, τb 0.560; P(Δτ>0) 0.000; B=400 | `same-window/eval_summary.json` : `contrasts[9]` |
| [hybrid_single] C-PR sybil minus AWP sybil | Δτ -0.277 [-0.294, -0.260]; τa 0.142, τb 0.419; P(Δτ>0) 0.000; B=400 | `same-window/eval_summary.json` : `contrasts[10]` |
| [hybrid_single] C-PR sybil minus EndorseRank sybil | Δτ 0.116 [0.105, 0.125]; τa 0.142, τb 0.026; P(Δτ>0) 1.000; B=400 | `same-window/eval_summary.json` : `contrasts[11]` |
| [er_awp] EndorseRank allowance minus EndorseRank transfer | Δτ 0.363 [0.341, 0.382]; τa 0.560, τb 0.196; P(Δτ>0) 1.000; B=400 | `same-window/eval_summary.json` : `contrasts[12]` |
| [er_awp] AWP transfer minus EndorseRank transfer | Δτ 0.539 [0.518, 0.560]; τa 0.736, τb 0.196; P(Δτ>0) 1.000; B=400 | `same-window/eval_summary.json` : `contrasts[13]` |
| [er_awp] EndorseRank allowance minus AWP allowance | Δτ 0.333 [0.311, 0.354]; τa 0.560, τb 0.226; P(Δτ>0) 1.000; B=400 | `same-window/eval_summary.json` : `contrasts[14]` |
| [er_awp] AWP sybil minus EndorseRank sybil | Δτ 0.393 [0.373, 0.412]; τa 0.419, τb 0.026; P(Δτ>0) 1.000; B=400 | `same-window/eval_summary.json` : `contrasts[15]` |
| [er_awp] EndorseRank in-approve degree minus EndorseRank in-degree | Δτ 0.432 [0.410, 0.452]; τa 0.650, τb 0.218; P(Δτ>0) 1.000; B=400 | `same-window/eval_summary.json` : `contrasts[16]` |
| EndorseRank vs AWP, τ_b | 0.199 [0.181, 0.221]; B=400 | `same-window/eval_summary.json` : `inter_method.endorserank_vs_awp` |
| EndorseRank vs AWP, isolated-node rule | 0.199 [0.181, 0.221]; B=400 | `same-window/eval_summary.json` : `inter_method.isolated` |
| Concordance: pairs | 21,011,403 | `same-window/eval_summary.json` : `inter_method.concordance.pairs` |
| Concordance: ordered by both | 20,262,952 | `same-window/eval_summary.json` : `inter_method.concordance.ordered_by_both` |
| Concordance: share ordered by both | 0.964 | `same-window/eval_summary.json` : `inter_method.concordance.share_ordered_by_both` |
| Concordance: discordant share of ordered | 0.398 | `same-window/eval_summary.json` : `inter_method.concordance.discordant_share_of_ordered` |
| Concordance: tau b | 0.199 | `same-window/eval_summary.json` : `inter_method.concordance.tau_b` |
| Rule A secondary, transfer: better layer C-PR (λ=0) | C-PR 0.400 vs interval [0.691, 0.709]; pass: no | `same-window/eval_summary.json` : `rule_a_secondary.transfer` |
| Rule A secondary, allowance: better layer C-PR (λ=1) | C-PR 0.449 vs interval [0.550, 0.572]; pass: no | `same-window/eval_summary.json` : `rule_a_secondary.allowance` |
| Rule A secondary, Sybil stability: C-PR above both layers | C-PR 0.142, λ=1 0.028, λ=0 0.402; pass: no | `same-window/eval_summary.json` : `rule_a_secondary.sybil_stability` |
| Rule A secondary part met | no | `same-window/eval_summary.json` : `rule_a_secondary.pass` |

## 4. Ties and the isolated-node rule

| Quantity | Value | Source |
|---|---|---|
| EndorseRank ties (same window) | distinct 5,641 of 6,483; zeros 197; largest block 197 at 0.000; share of pairs tied 0.0020 | `same-window/eval_summary.json` : `ties.endorserank` |
| EndorseRank (activity restarts) ties (same window) | distinct 6,265 of 6,483; zeros 197; largest block 197 at 0.000; share of pairs tied 0.0009224 | `same-window/eval_summary.json` : `ties.endorserank_activity` |
| AWP ties (same window) | distinct 5,292 of 6,483; zeros 1,192; largest block 1,192 at 0.000; share of pairs tied 0.0338 | `same-window/eval_summary.json` : `ties.awp` |
| C-PR (λ=1) ties (same window) | distinct 5,238 of 6,483; zeros 191; largest block 191 at 0.000; share of pairs tied 0.0021 | `same-window/eval_summary.json` : `ties.cpr_l100` |
| C-PR (λ=0) ties (same window) | distinct 5,206 of 6,483; zeros 1,192; largest block 1,192 at 0.000; share of pairs tied 0.0338 | `same-window/eval_summary.json` : `ties.cpr_l0` |
| C-PR (λ=0.25) ties (same window) | distinct 6,274 of 6,483; zeros 30; largest block 47 at 1.762e-07; share of pairs tied 0.0001273 | `same-window/eval_summary.json` : `ties.cpr_l25` |
| C-PR (λ=0.5) ties (same window) | distinct 6,268 of 6,483; zeros 30; largest block 47 at 1.937e-07; share of pairs tied 0.0001271 | `same-window/eval_summary.json` : `ties.cpr_l50` |
| C-PR (λ=0.75) ties (same window) | distinct 6,273 of 6,483; zeros 30; largest block 46 at 2.08e-07; share of pairs tied 0.0001201 | `same-window/eval_summary.json` : `ties.cpr_l75` |
| S-PR ties (same window) | distinct 5,260 of 6,483; zeros 1,197; largest block 1,197 at 0.000; share of pairs tied 0.0341 | `same-window/eval_summary.json` : `ties.spr` |
| endorserank_iso (missing contracts as isolated nodes), transfer | 0.196 [0.180, 0.216]; B=400 | `same-window/eval_summary.json` : `isolated_rule.endorserank_iso.transfer` |
| endorserank_iso (missing contracts as isolated nodes), allowance | 0.560 [0.548, 0.571]; B=400 | `same-window/eval_summary.json` : `isolated_rule.endorserank_iso.allowance` |
| endorserank_iso (missing contracts as isolated nodes), Sybil stability | 0.026 [0.012, 0.041]; B=400 | `same-window/eval_summary.json` : `isolated_rule.endorserank_iso.sybil_stability` |
| awp_iso (missing contracts as isolated nodes), transfer | 0.736 [0.728, 0.744]; B=400 | `same-window/eval_summary.json` : `isolated_rule.awp_iso.transfer` |
| awp_iso (missing contracts as isolated nodes), allowance | 0.226 [0.210, 0.245]; B=400 | `same-window/eval_summary.json` : `isolated_rule.awp_iso.allowance` |
| awp_iso (missing contracts as isolated nodes), Sybil stability | 0.419 [0.408, 0.434]; B=400 | `same-window/eval_summary.json` : `isolated_rule.awp_iso.sybil_stability` |
| EndorseRank ties (W0 spenders) | distinct 7,368 of 7,914; zeros 9; largest block 116 at 6.414e-07; share of pairs tied 0.0005817 | `holdout-w0/eval_summary.json` : `ties.endorserank` |
| AWP ties (W0 spenders) | distinct 6,573 of 7,914; zeros 1,342; largest block 1,342 at 0.000; share of pairs tied 0.0287 | `holdout-w0/eval_summary.json` : `ties.awp` |
| C-PR (λ=1) ties (W0 spenders) | distinct 6,047 of 7,914; zeros 0; largest block 163 at 1.973e-07; share of pairs tied 0.0017 | `holdout-w0/eval_summary.json` : `ties.cpr_l100` |

## 5. Closed-form check of EndorseRank, s(v) = c (1 + d δ(v))

| Quantity | Value | Source |
|---|---|---|
| Same window: common value c | 1.928e-07 | `same-window/eval_summary.json` : `closed_form.common_value_c` |
| Same window: spread of c | 1.0000 | `same-window/eval_summary.json` : `closed_form.spread_of_c` |
| Same window: spenders | 6,224 | `same-window/eval_summary.json` : `closed_form.spenders` |
| Same window: depth one spenders | 5,232 | `same-window/eval_summary.json` : `closed_form.depth_one_spenders` |
| Same window: within 1pct all | 0.8755 | `same-window/eval_summary.json` : `closed_form.within_1pct_all` |
| Same window: within 1pct depth one | 1.0000 | `same-window/eval_summary.json` : `closed_form.within_1pct_depth_one` |
| Same window: within 1pct deeper | 0.2188 | `same-window/eval_summary.json` : `closed_form.within_1pct_deeper` |
| Same window: tau score vs delta | 0.9085 | `same-window/eval_summary.json` : `closed_form.tau_score_vs_delta` |
| W0: common value c | 1.807e-07 | `holdout-w0/eval_summary.json` : `closed_form.common_value_c` |
| W0: spread of c | 1.0000 | `holdout-w0/eval_summary.json` : `closed_form.spread_of_c` |
| W0: spenders | 7,905 | `holdout-w0/eval_summary.json` : `closed_form.spenders` |
| W0: depth one spenders | 5,092 | `holdout-w0/eval_summary.json` : `closed_form.depth_one_spenders` |
| W0: within 1pct all | 0.7075 | `holdout-w0/eval_summary.json` : `closed_form.within_1pct_all` |
| W0: within 1pct depth one | 1.0000 | `holdout-w0/eval_summary.json` : `closed_form.within_1pct_depth_one` |
| W0: within 1pct deeper | 0.1781 | `holdout-w0/eval_summary.json` : `closed_form.within_1pct_deeper` |
| W0: tau score vs delta | 0.7820 | `holdout-w0/eval_summary.json` : `closed_form.tau_score_vs_delta` |

## 6. Holdout W0 (scores at t1, labels April to June 2026)

| Quantity | Value | Source |
|---|---|---|
| Freeze t1 | 2026-03-31 23:59:59 UTC | `holdout-w0/eval_summary.json` : `freeze` |
| Label window | 2026-04-01 00:00:00 UTC to 2026-06-30 23:59:59 UTC | `holdout-w0/eval_summary.json` : `labels` |
| Spenders with a positive latest allowance at t1, account type contract | 7,914 | `holdout-w0/eval_summary.json` : `spender_account_types.contract` |
| Spenders with a positive latest allowance at t1, account type none | 39 | `holdout-w0/eval_summary.json` : `spender_account_types.none` |
| Spenders with a positive latest allowance at t1, account type eip7702 | 9 | `holdout-w0/eval_summary.json` : `spender_account_types.eip7702` |
| Spender cohort (contracts) | 7,914 | `holdout-w0/eval_summary.json` : `spenders` |
| Gained a new approval pair | 1,732 | `holdout-w0/eval_summary.json` : `gained_new_approvals` |
| Gained a new transfer sender | 1,422 | `holdout-w0/eval_summary.json` : `gained_new_senders` |

### W0 spenders: τ_b with every label

| Quantity | Value | Source |
|---|---|---|
| EndorseRank, new approval pairs | 0.303 [0.287, 0.319]; B=400 | `holdout-w0/eval_summary.json` : `taus.endorserank.future_new_approvers` |
| EndorseRank, new transfer senders | 0.272 [0.257, 0.286]; B=400 | `holdout-w0/eval_summary.json` : `taus.endorserank.future_new_transfer_senders` |
| EndorseRank, revocations | 0.343 [0.330, 0.359]; B=400 | `holdout-w0/eval_summary.json` : `taus.endorserank.future_revoke_count` |
| EndorseRank, drained owners | 0.295 [0.279, 0.312]; B=400 | `holdout-w0/eval_summary.json` : `taus.endorserank.future_drain_owners` |
| EndorseRank (activity restarts), new approval pairs | 0.332 [0.315, 0.347]; B=400 | `holdout-w0/eval_summary.json` : `taus.endorserank_activity.future_new_approvers` |
| EndorseRank (activity restarts), new transfer senders | 0.270 [0.256, 0.285]; B=400 | `holdout-w0/eval_summary.json` : `taus.endorserank_activity.future_new_transfer_senders` |
| EndorseRank (activity restarts), revocations | 0.369 [0.358, 0.384]; B=400 | `holdout-w0/eval_summary.json` : `taus.endorserank_activity.future_revoke_count` |
| EndorseRank (activity restarts), drained owners | 0.341 [0.325, 0.356]; B=400 | `holdout-w0/eval_summary.json` : `taus.endorserank_activity.future_drain_owners` |
| AWP, new approval pairs | 0.196 [0.178, 0.213]; B=400 | `holdout-w0/eval_summary.json` : `taus.awp.future_new_approvers` |
| AWP, new transfer senders | 0.409 [0.396, 0.421]; B=400 | `holdout-w0/eval_summary.json` : `taus.awp.future_new_transfer_senders` |
| AWP, revocations | 0.192 [0.172, 0.213]; B=400 | `holdout-w0/eval_summary.json` : `taus.awp.future_revoke_count` |
| AWP, drained owners | 0.193 [0.175, 0.212]; B=400 | `holdout-w0/eval_summary.json` : `taus.awp.future_drain_owners` |
| C-PR (λ=1), new approval pairs | 0.298 [0.282, 0.313]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l100.future_new_approvers` |
| C-PR (λ=1), new transfer senders | 0.267 [0.250, 0.282]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l100.future_new_transfer_senders` |
| C-PR (λ=1), revocations | 0.340 [0.327, 0.356]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l100.future_revoke_count` |
| C-PR (λ=1), drained owners | 0.280 [0.263, 0.296]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l100.future_drain_owners` |
| C-PR (λ=0), new approval pairs | 0.178 [0.160, 0.197]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l0.future_new_approvers` |
| C-PR (λ=0), new transfer senders | 0.366 [0.351, 0.378]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l0.future_new_transfer_senders` |
| C-PR (λ=0), revocations | 0.183 [0.164, 0.204]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l0.future_revoke_count` |
| C-PR (λ=0), drained owners | 0.174 [0.155, 0.195]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l0.future_drain_owners` |
| C-PR (λ=0.25), new approval pairs | 0.329 [0.312, 0.343]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l25.future_new_approvers` |
| C-PR (λ=0.25), new transfer senders | 0.345 [0.330, 0.357]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l25.future_new_transfer_senders` |
| C-PR (λ=0.25), revocations | 0.325 [0.311, 0.339]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l25.future_revoke_count` |
| C-PR (λ=0.25), drained owners | 0.335 [0.320, 0.349]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l25.future_drain_owners` |
| C-PR (λ=0.5), new approval pairs | 0.329 [0.312, 0.343]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l50.future_new_approvers` |
| C-PR (λ=0.5), new transfer senders | 0.336 [0.322, 0.348]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l50.future_new_transfer_senders` |
| C-PR (λ=0.5), revocations | 0.327 [0.314, 0.342]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l50.future_revoke_count` |
| C-PR (λ=0.5), drained owners | 0.338 [0.322, 0.353]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l50.future_drain_owners` |
| C-PR (λ=0.75), new approval pairs | 0.327 [0.311, 0.342]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l75.future_new_approvers` |
| C-PR (λ=0.75), new transfer senders | 0.327 [0.313, 0.339]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l75.future_new_transfer_senders` |
| C-PR (λ=0.75), revocations | 0.327 [0.315, 0.343]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l75.future_revoke_count` |
| C-PR (λ=0.75), drained owners | 0.337 [0.321, 0.352]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l75.future_drain_owners` |
| S-PR, new approval pairs | 0.190 [0.171, 0.209]; B=400 | `holdout-w0/eval_summary.json` : `taus.spr.future_new_approvers` |
| S-PR, new transfer senders | 0.377 [0.363, 0.389]; B=400 | `holdout-w0/eval_summary.json` : `taus.spr.future_new_transfer_senders` |
| S-PR, revocations | 0.209 [0.190, 0.230]; B=400 | `holdout-w0/eval_summary.json` : `taus.spr.future_revoke_count` |
| S-PR, drained owners | 0.196 [0.177, 0.216]; B=400 | `holdout-w0/eval_summary.json` : `taus.spr.future_drain_owners` |
| in-approve degree at t1, new approval pairs | 0.392 [0.377, 0.406]; B=400 | `holdout-w0/eval_summary.json` : `taus.t1_in_approve_degree.future_new_approvers` |
| in-approve degree at t1, new transfer senders | 0.284 [0.267, 0.299]; B=400 | `holdout-w0/eval_summary.json` : `taus.t1_in_approve_degree.future_new_transfer_senders` |
| in-approve degree at t1, revocations | 0.384 [0.366, 0.399]; B=400 | `holdout-w0/eval_summary.json` : `taus.t1_in_approve_degree.future_revoke_count` |
| in-approve degree at t1, drained owners | 0.313 [0.294, 0.330]; B=400 | `holdout-w0/eval_summary.json` : `taus.t1_in_approve_degree.future_drain_owners` |
| transfer in-degree at t1, new approval pairs | 0.203 [0.183, 0.224]; B=400 | `holdout-w0/eval_summary.json` : `taus.t1_in_degree.future_new_approvers` |
| transfer in-degree at t1, new transfer senders | 0.447 [0.435, 0.459]; B=400 | `holdout-w0/eval_summary.json` : `taus.t1_in_degree.future_new_transfer_senders` |
| transfer in-degree at t1, revocations | 0.186 [0.167, 0.209]; B=400 | `holdout-w0/eval_summary.json` : `taus.t1_in_degree.future_revoke_count` |
| transfer in-degree at t1, drained owners | 0.162 [0.143, 0.183]; B=400 | `holdout-w0/eval_summary.json` : `taus.t1_in_degree.future_drain_owners` |

### W0 contrasts

| Quantity | Value | Source |
|---|---|---|
| [contrasts_prefixed] C-PR minus C-PR (l=1), new approval pairs | Δτ 0.031 [0.021, 0.042]; τa 0.329, τb 0.298; P(Δτ>0) 1.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_prefixed[0]` |
| [contrasts_prefixed] C-PR minus C-PR (l=0), new transfer senders | Δτ -0.030 [-0.040, -0.020]; τa 0.336, τb 0.366; P(Δτ>0) 0.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_prefixed[1]` |
| [contrasts_after] C-PR (l=1) minus t1 in-approve degree, new approval pairs | Δτ -0.094 [-0.104, -0.083]; τa 0.298, τb 0.392; P(Δτ>0) 0.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_after[0]` |
| [contrasts_after] S-PR minus C-PR (l=1), new approval pairs | Δτ -0.108 [-0.128, -0.088]; τa 0.190, τb 0.298; P(Δτ>0) 0.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_after[1]` |
| [contrasts_after] S-PR minus C-PR (l=0), new transfer senders | Δτ 0.011 [0.004, 0.018]; τa 0.377, τb 0.366; P(Δτ>0) 1.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_after[2]` |
| [contrasts_after] EndorseRank minus t1 in-approve degree, new approval pairs | Δτ -0.090 [-0.100, -0.079]; τa 0.303, τb 0.392; P(Δτ>0) 0.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_after[3]` |
| [contrasts_after] AWP minus t1 in-degree, new transfer senders | Δτ -0.038 [-0.043, -0.032]; τa 0.409, τb 0.447; P(Δτ>0) 0.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_after[4]` |
| [contrasts_after] C-PR minus C-PR (l=0), new approval pairs | Δτ 0.151 [0.130, 0.170]; τa 0.329, τb 0.178; P(Δτ>0) 1.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_after[5]` |
| [contrasts_after] C-PR minus EndorseRank, new approval pairs | Δτ 0.026 [0.016, 0.037]; τa 0.329, τb 0.303; P(Δτ>0) 1.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_after[6]` |
| [contrasts_after] C-PR minus AWP, new transfer senders | Δτ -0.073 [-0.083, -0.063]; τa 0.336, τb 0.409; P(Δτ>0) 0.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_after[7]` |
| [contrasts_after] C-PR minus AWP, new approval pairs | Δτ 0.133 [0.114, 0.153]; τa 0.329, τb 0.196; P(Δτ>0) 1.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_after[8]` |
| [contrasts_after] EndorseRank minus AWP, new approval pairs | Δτ 0.107 [0.086, 0.130]; τa 0.303, τb 0.196; P(Δτ>0) 1.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_after[9]` |
| [contrasts_after] EndorseRank minus AWP, new transfer senders | Δτ -0.138 [-0.151, -0.123]; τa 0.272, τb 0.409; P(Δτ>0) 0.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_after[10]` |

### Rule A, primary part

| Quantity | Value | Source |
|---|---|---|
| Rule A primary: no worse on new approvals | yes | `holdout-w0/eval_summary.json` : `rule_a_primary.no_worse_on_new_approvals` |
| Rule A primary: better on new senders | no | `holdout-w0/eval_summary.json` : `rule_a_primary.better_on_new_senders` |
| Rule A primary: pass | no | `holdout-w0/eval_summary.json` : `rule_a_primary.pass` |

### Spenders that had received a transfer before t1

| Quantity | Value | Source |
|---|---|---|
| Receiving subset (contracts) | 6,489 | `holdout-w0/eval_summary.json` : `receiving.n` |
| Receiving: EndorseRank, new approval pairs | 0.299 [0.283, 0.315]; B=400 | `holdout-w0/eval_summary.json` : `receiving.taus.endorserank.future_new_approvers` |
| Receiving: EndorseRank, new transfer senders | 0.315 [0.300, 0.331]; B=400 | `holdout-w0/eval_summary.json` : `receiving.taus.endorserank.future_new_transfer_senders` |
| Receiving: AWP, new approval pairs | 0.328 [0.312, 0.343]; B=400 | `holdout-w0/eval_summary.json` : `receiving.taus.awp.future_new_approvers` |
| Receiving: AWP, new transfer senders | 0.408 [0.393, 0.422]; B=400 | `holdout-w0/eval_summary.json` : `receiving.taus.awp.future_new_transfer_senders` |
| Receiving: in-approve degree at t1, new approval pairs | 0.387 [0.370, 0.402]; B=400 | `holdout-w0/eval_summary.json` : `receiving.taus.t1_in_approve_degree.future_new_approvers` |
| Receiving: in-approve degree at t1, new transfer senders | 0.335 [0.318, 0.350]; B=400 | `holdout-w0/eval_summary.json` : `receiving.taus.t1_in_approve_degree.future_new_transfer_senders` |
| Receiving: transfer in-degree at t1, new approval pairs | 0.341 [0.325, 0.357]; B=400 | `holdout-w0/eval_summary.json` : `receiving.taus.t1_in_degree.future_new_approvers` |
| Receiving: transfer in-degree at t1, new transfer senders | 0.459 [0.445, 0.474]; B=400 | `holdout-w0/eval_summary.json` : `receiving.taus.t1_in_degree.future_new_transfer_senders` |
| Receiving: EndorseRank minus t1 in-approve degree, new approval pairs | Δτ -0.087 [-0.096, -0.078]; τa 0.299, τb 0.387; P(Δτ>0) 0.000; B=400 | `holdout-w0/eval_summary.json` : `receiving.contrasts[0]` |
| Receiving: AWP minus t1 in-degree, new transfer senders | Δτ -0.051 [-0.059, -0.043]; τa 0.408, τb 0.459; P(Δτ>0) 0.000; B=400 | `holdout-w0/eval_summary.json` : `receiving.contrasts[1]` |

### Coverage (AWP = 0 means no transfer edge)

| Quantity | Value | Source |
|---|---|---|
| spenders without transfer edge | 1,342 | `holdout-w0/eval_summary.json` : `coverage.spenders_without_transfer_edge` |
| share gaining approvals without | 0.267 | `holdout-w0/eval_summary.json` : `coverage.share_gaining_approvals_without` |
| share gaining approvals with | 0.209 | `holdout-w0/eval_summary.json` : `coverage.share_gaining_approvals_with` |
| share gaining senders without | 0.014 | `holdout-w0/eval_summary.json` : `coverage.share_gaining_senders_without` |
| share gaining senders with | 0.213 | `holdout-w0/eval_summary.json` : `coverage.share_gaining_senders_with` |

### W0 traders (exploratory)

| Quantity | Value | Source |
|---|---|---|
| Traders (GMX V2 contract accounts, ≥3 closes) | 87 | `holdout-w0/eval_summary.json` : `traders.n` |
| Traders that had received an approval by t1 | 39 | `holdout-w0/eval_summary.json` : `traders.with_any_approval_received` |
| Traders: EndorseRank, profitable closes | 0.120 [-0.032, 0.260]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.endorserank.profitable_closes` |
| Traders: EndorseRank, realized gain | 0.058 [-0.092, 0.196]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.endorserank.realized_gain` |
| Traders: EndorseRank, profitable share | -0.047 [-0.193, 0.090]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.endorserank.profitable_share` |
| Traders: EndorseRank, non-loss share | -0.167 [-0.297, -0.025]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.endorserank.non_loss_share` |
| Traders: EndorseRank (activity restarts), profitable closes | 0.139 [-0.002, 0.284]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.endorserank_activity.profitable_closes` |
| Traders: EndorseRank (activity restarts), realized gain | 0.087 [-0.064, 0.227]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.endorserank_activity.realized_gain` |
| Traders: EndorseRank (activity restarts), profitable share | -0.077 [-0.224, 0.059]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.endorserank_activity.profitable_share` |
| Traders: EndorseRank (activity restarts), non-loss share | -0.197 [-0.328, -0.066]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.endorserank_activity.non_loss_share` |
| Traders: AWP, profitable closes | 0.166 [0.015, 0.308]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.awp.profitable_closes` |
| Traders: AWP, realized gain | 0.197 [0.044, 0.332]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.awp.realized_gain` |
| Traders: AWP, profitable share | -0.121 [-0.264, 0.032]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.awp.profitable_share` |
| Traders: AWP, non-loss share | -0.275 [-0.413, -0.145]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.awp.non_loss_share` |
| Traders: C-PR (λ=1), profitable closes | 0.077 [-0.075, 0.233]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l100.profitable_closes` |
| Traders: C-PR (λ=1), realized gain | 0.039 [-0.128, 0.197]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l100.realized_gain` |
| Traders: C-PR (λ=1), profitable share | -0.076 [-0.240, 0.072]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l100.profitable_share` |
| Traders: C-PR (λ=1), non-loss share | -0.186 [-0.319, -0.045]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l100.non_loss_share` |
| Traders: C-PR (λ=0), profitable closes | 0.166 [0.020, 0.300]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l0.profitable_closes` |
| Traders: C-PR (λ=0), realized gain | 0.297 [0.133, 0.427]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l0.realized_gain` |
| Traders: C-PR (λ=0), profitable share | -0.088 [-0.247, 0.062]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l0.profitable_share` |
| Traders: C-PR (λ=0), non-loss share | -0.233 [-0.375, -0.102]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l0.non_loss_share` |
| Traders: C-PR (λ=0.25), profitable closes | 0.163 [0.012, 0.289]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l25.profitable_closes` |
| Traders: C-PR (λ=0.25), realized gain | 0.289 [0.134, 0.414]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l25.realized_gain` |
| Traders: C-PR (λ=0.25), profitable share | -0.082 [-0.234, 0.064]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l25.profitable_share` |
| Traders: C-PR (λ=0.25), non-loss share | -0.225 [-0.373, -0.089]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l25.non_loss_share` |
| Traders: C-PR (λ=0.5), profitable closes | 0.172 [0.024, 0.300]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l50.profitable_closes` |
| Traders: C-PR (λ=0.5), realized gain | 0.287 [0.131, 0.413]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l50.realized_gain` |
| Traders: C-PR (λ=0.5), profitable share | -0.080 [-0.227, 0.062]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l50.profitable_share` |
| Traders: C-PR (λ=0.5), non-loss share | -0.222 [-0.365, -0.084]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l50.non_loss_share` |
| Traders: C-PR (λ=0.75), profitable closes | 0.166 [0.021, 0.290]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l75.profitable_closes` |
| Traders: C-PR (λ=0.75), realized gain | 0.273 [0.121, 0.397]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l75.realized_gain` |
| Traders: C-PR (λ=0.75), profitable share | -0.076 [-0.228, 0.066]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l75.profitable_share` |
| Traders: C-PR (λ=0.75), non-loss share | -0.218 [-0.359, -0.081]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l75.non_loss_share` |
| Traders: S-PR, profitable closes | 0.168 [0.018, 0.301]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.spr.profitable_closes` |
| Traders: S-PR, realized gain | 0.282 [0.118, 0.407]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.spr.realized_gain` |
| Traders: S-PR, profitable share | -0.060 [-0.208, 0.092]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.spr.profitable_share` |
| Traders: S-PR, non-loss share | -0.203 [-0.354, -0.057]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.spr.non_loss_share` |
| Traders: in-approve degree at t1, profitable closes | 0.067 [-0.117, 0.225]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.t1_in_approve_degree.profitable_closes` |
| Traders: in-approve degree at t1, realized gain | 0.048 [-0.131, 0.222]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.t1_in_approve_degree.realized_gain` |
| Traders: in-approve degree at t1, profitable share | -0.160 [-0.338, 0.020]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.t1_in_approve_degree.profitable_share` |
| Traders: in-approve degree at t1, non-loss share | -0.288 [-0.450, -0.126]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.t1_in_approve_degree.non_loss_share` |
| Traders: transfer in-degree at t1, profitable closes | 0.069 [-0.076, 0.210]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.t1_in_degree.profitable_closes` |
| Traders: transfer in-degree at t1, realized gain | 0.074 [-0.090, 0.229]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.t1_in_degree.realized_gain` |
| Traders: transfer in-degree at t1, profitable share | -0.117 [-0.275, 0.036]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.t1_in_degree.profitable_share` |
| Traders: transfer in-degree at t1, non-loss share | -0.214 [-0.367, -0.062]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.t1_in_degree.non_loss_share` |

## 7. Window W1 (scores at T_obs, labels July to September 2026; the rules registered for the raw-unit analysis, applied to the revised scores)

| Quantity | Value | Source |
|---|---|---|
| Margin δ | 0.010 | `window-w1/eval_summary.json` : `delta` |
| Spender cohort (contracts) | 7,960 | `window-w1/eval_summary.json` : `spenders` |
| Gained a new approval pair | 1,495 | `window-w1/eval_summary.json` : `gained_new_approvals` |
| Gained a new transfer sender | 1,371 | `window-w1/eval_summary.json` : `gained_new_senders` |
| Traders (GMX V2 contract accounts, ≥3 closes) | 70 | `window-w1/eval_summary.json` : `traders` |
| Traders with at least one liquidation | 9 | `window-w1/eval_summary.json` : `traders_liquidated` |
| Traders whose every close was a liquidation | 1 | `window-w1/eval_summary.json` : `traders_all_liquidated` |

### Rule B (comparator C-PR λ=0)

| Quantity | Value | Source |
|---|---|---|
| Rule B (comparator C-PR λ=0): F1 | Δτ 0.170 [0.149, 0.189]; τa 0.316, τb 0.146; P(Δτ>0) 1.000; B=400; superiority: holds | `window-w1/eval_summary.json` : `rule_b.F1` |
| Rule B (comparator C-PR λ=0): F2 | Δτ -0.025 [-0.038, -0.015]; τa 0.324, τb 0.348; P(Δτ>0) 0.000; B=400; non_inferiority: fails | `window-w1/eval_summary.json` : `rule_b.F2` |
| Rule B (comparator C-PR λ=0): F3 | Δτ 0.000 [-0.010, 0.010]; τa 0.282, τb 0.282; P(Δτ>0) 0.417; B=400; non_inferiority: fails | `window-w1/eval_summary.json` : `rule_b.F3` |
| Rule B (comparator C-PR λ=0): F4 | Δτ 0.000 [-0.010, 0.010]; τa 0.282, τb 0.282; P(Δτ>0) 0.417; B=400; superiority: fails | `window-w1/eval_summary.json` : `rule_b.F4` |
| Rule B (comparator C-PR λ=0): decision | no | `window-w1/eval_summary.json` : `rule_b.decision` |
| Rule B (comparator C-PR λ=0): F5 | Δτ -0.019 [-0.123, 0.089]; τa 0.282, τb 0.302; P(Δτ>0) 0.362; B=400; superiority: fails | `window-w1/eval_summary.json` : `rule_b.F5` |
| Rule B (comparator C-PR λ=0): F6a | Δτ 0.021 [0.009, 0.032]; τa 0.316, τb 0.295; P(Δτ>0) 1.000; B=400; no_worse: holds | `window-w1/eval_summary.json` : `rule_b.F6a` |
| Rule B (comparator C-PR λ=0): F6b | Δτ -0.025 [-0.038, -0.015]; τa 0.324, τb 0.348; P(Δτ>0) 0.000; B=400; superiority: fails | `window-w1/eval_summary.json` : `rule_b.F6b` |
| Rule B (comparator C-PR λ=0): F6 | no | `window-w1/eval_summary.json` : `rule_b.F6` |

### Sensitivity 1 (comparator AWP)

| Quantity | Value | Source |
|---|---|---|
| Sensitivity 1 (comparator AWP): F1 | Δτ 0.159 [0.139, 0.178]; τa 0.316, τb 0.157; P(Δτ>0) 1.000; B=400; superiority: holds | `window-w1/eval_summary.json` : `sensitivity_awp.F1` |
| Sensitivity 1 (comparator AWP): F2 | Δτ -0.075 [-0.085, -0.065]; τa 0.324, τb 0.398; P(Δτ>0) 0.000; B=400; non_inferiority: fails | `window-w1/eval_summary.json` : `sensitivity_awp.F2` |
| Sensitivity 1 (comparator AWP): F3 | Δτ 0.019 [-0.026, 0.064]; τa 0.282, τb 0.263; P(Δτ>0) 0.802; B=400; non_inferiority: fails | `window-w1/eval_summary.json` : `sensitivity_awp.F3` |
| Sensitivity 1 (comparator AWP): F4 | Δτ 0.019 [-0.026, 0.064]; τa 0.282, τb 0.263; P(Δτ>0) 0.802; B=400; superiority: fails | `window-w1/eval_summary.json` : `sensitivity_awp.F4` |
| Sensitivity 1 (comparator AWP): decision | no | `window-w1/eval_summary.json` : `sensitivity_awp.decision` |

### Sensitivity 2 (isolated nodes)

| Quantity | Value | Source |
|---|---|---|
| Sensitivity 2 (isolated nodes): F1 | Δτ 0.168 [0.147, 0.187]; τa 0.316, τb 0.148; P(Δτ>0) 1.000; B=400; superiority: holds | `window-w1/eval_summary.json` : `sensitivity_isolated.F1` |
| Sensitivity 2 (isolated nodes): F2 | Δτ -0.025 [-0.039, -0.016]; τa 0.324, τb 0.349; P(Δτ>0) 0.000; B=400; non_inferiority: fails | `window-w1/eval_summary.json` : `sensitivity_isolated.F2` |
| Sensitivity 2 (isolated nodes): F3 | Δτ 0.000 [-0.010, 0.010]; τa 0.282, τb 0.282; P(Δτ>0) 0.417; B=400; non_inferiority: fails | `window-w1/eval_summary.json` : `sensitivity_isolated.F3` |
| Sensitivity 2 (isolated nodes): F4 | Δτ 0.000 [-0.010, 0.010]; τa 0.282, τb 0.282; P(Δτ>0) 0.417; B=400; superiority: fails | `window-w1/eval_summary.json` : `sensitivity_isolated.F4` |
| Sensitivity 2 (isolated nodes): decision | no | `window-w1/eval_summary.json` : `sensitivity_isolated.decision` |
| Sensitivity 2 (isolated nodes): F5 | Δτ -0.040 [-0.116, 0.035]; τa 0.282, τb 0.322; P(Δτ>0) 0.158; B=400; superiority: fails | `window-w1/eval_summary.json` : `sensitivity_isolated.F5` |
| Sensitivity 2 (isolated nodes): F6a | Δτ 0.021 [0.009, 0.032]; τa 0.316, τb 0.295; P(Δτ>0) 1.000; B=400; no_worse: holds | `window-w1/eval_summary.json` : `sensitivity_isolated.F6a` |
| Sensitivity 2 (isolated nodes): F6b | Δτ -0.025 [-0.039, -0.016]; τa 0.324, τb 0.349; P(Δτ>0) 0.000; B=400; superiority: fails | `window-w1/eval_summary.json` : `sensitivity_isolated.F6b` |
| Sensitivity 2 (isolated nodes): F6 | no | `window-w1/eval_summary.json` : `sensitivity_isolated.F6` |

### W1 spenders and traders: τ_b

| Quantity | Value | Source |
|---|---|---|
| Spenders: EndorseRank, new approval pairs | 0.299 [0.284, 0.314]; B=400 | `window-w1/eval_summary.json` : `spender_taus.endorserank.future_new_approvers` |
| Spenders: EndorseRank, new transfer senders | 0.259 [0.243, 0.275]; B=400 | `window-w1/eval_summary.json` : `spender_taus.endorserank.future_new_transfer_senders` |
| Spenders: EndorseRank (activity restarts), new approval pairs | 0.335 [0.319, 0.349]; B=400 | `window-w1/eval_summary.json` : `spender_taus.endorserank_activity.future_new_approvers` |
| Spenders: EndorseRank (activity restarts), new transfer senders | 0.236 [0.219, 0.251]; B=400 | `window-w1/eval_summary.json` : `spender_taus.endorserank_activity.future_new_transfer_senders` |
| Spenders: AWP, new approval pairs | 0.157 [0.137, 0.178]; B=400 | `window-w1/eval_summary.json` : `spender_taus.awp.future_new_approvers` |
| Spenders: AWP, new transfer senders | 0.398 [0.386, 0.412]; B=400 | `window-w1/eval_summary.json` : `spender_taus.awp.future_new_transfer_senders` |
| Spenders: C-PR (λ=1), new approval pairs | 0.295 [0.280, 0.310]; B=400 | `window-w1/eval_summary.json` : `spender_taus.cpr_l100.future_new_approvers` |
| Spenders: C-PR (λ=1), new transfer senders | 0.257 [0.241, 0.274]; B=400 | `window-w1/eval_summary.json` : `spender_taus.cpr_l100.future_new_transfer_senders` |
| Spenders: C-PR (λ=0), new approval pairs | 0.146 [0.126, 0.168]; B=400 | `window-w1/eval_summary.json` : `spender_taus.cpr_l0.future_new_approvers` |
| Spenders: C-PR (λ=0), new transfer senders | 0.348 [0.335, 0.363]; B=400 | `window-w1/eval_summary.json` : `spender_taus.cpr_l0.future_new_transfer_senders` |
| Spenders: C-PR (λ=0.25), new approval pairs | 0.315 [0.299, 0.328]; B=400 | `window-w1/eval_summary.json` : `spender_taus.cpr_l25.future_new_approvers` |
| Spenders: C-PR (λ=0.25), new transfer senders | 0.332 [0.317, 0.346]; B=400 | `window-w1/eval_summary.json` : `spender_taus.cpr_l25.future_new_transfer_senders` |
| Spenders: C-PR (λ=0.5), new approval pairs | 0.316 [0.300, 0.330]; B=400 | `window-w1/eval_summary.json` : `spender_taus.cpr_l50.future_new_approvers` |
| Spenders: C-PR (λ=0.5), new transfer senders | 0.324 [0.308, 0.337]; B=400 | `window-w1/eval_summary.json` : `spender_taus.cpr_l50.future_new_transfer_senders` |
| Spenders: C-PR (λ=0.75), new approval pairs | 0.316 [0.298, 0.330]; B=400 | `window-w1/eval_summary.json` : `spender_taus.cpr_l75.future_new_approvers` |
| Spenders: C-PR (λ=0.75), new transfer senders | 0.315 [0.299, 0.329]; B=400 | `window-w1/eval_summary.json` : `spender_taus.cpr_l75.future_new_transfer_senders` |
| Spenders: S-PR, new approval pairs | 0.162 [0.140, 0.184]; B=400 | `window-w1/eval_summary.json` : `spender_taus.spr.future_new_approvers` |
| Spenders: S-PR, new transfer senders | 0.367 [0.354, 0.381]; B=400 | `window-w1/eval_summary.json` : `spender_taus.spr.future_new_transfer_senders` |
| Spenders: in-approve degree at the freeze, new approval pairs | 0.381 [0.365, 0.396]; B=400 | `window-w1/eval_summary.json` : `spender_taus.in_approve_degree.future_new_approvers` |
| Spenders: in-approve degree at the freeze, new transfer senders | 0.269 [0.250, 0.285]; B=400 | `window-w1/eval_summary.json` : `spender_taus.in_approve_degree.future_new_transfer_senders` |
| Spenders: transfer in-degree at the freeze, new approval pairs | 0.165 [0.143, 0.186]; B=400 | `window-w1/eval_summary.json` : `spender_taus.in_degree.future_new_approvers` |
| Spenders: transfer in-degree at the freeze, new transfer senders | 0.439 [0.426, 0.454]; B=400 | `window-w1/eval_summary.json` : `spender_taus.in_degree.future_new_transfer_senders` |
| Traders: EndorseRank, liquidation-free close rate | 0.297 [0.174, 0.418]; B=400 | `window-w1/eval_summary.json` : `trader_taus.endorserank` |
| Traders: EndorseRank (activity restarts), liquidation-free close rate | 0.286 [0.160, 0.404]; B=400 | `window-w1/eval_summary.json` : `trader_taus.endorserank_activity` |
| Traders: AWP, liquidation-free close rate | 0.263 [0.140, 0.379]; B=400 | `window-w1/eval_summary.json` : `trader_taus.awp` |
| Traders: C-PR (λ=1), liquidation-free close rate | 0.302 [0.177, 0.425]; B=400 | `window-w1/eval_summary.json` : `trader_taus.cpr_l100` |
| Traders: C-PR (λ=0), liquidation-free close rate | 0.282 [0.162, 0.394]; B=400 | `window-w1/eval_summary.json` : `trader_taus.cpr_l0` |
| Traders: C-PR (λ=0.25), liquidation-free close rate | 0.282 [0.162, 0.397]; B=400 | `window-w1/eval_summary.json` : `trader_taus.cpr_l25` |
| Traders: C-PR (λ=0.5), liquidation-free close rate | 0.282 [0.162, 0.397]; B=400 | `window-w1/eval_summary.json` : `trader_taus.cpr_l50` |
| Traders: C-PR (λ=0.75), liquidation-free close rate | 0.284 [0.160, 0.398]; B=400 | `window-w1/eval_summary.json` : `trader_taus.cpr_l75` |
| Traders: S-PR, liquidation-free close rate | 0.300 [0.175, 0.411]; B=400 | `window-w1/eval_summary.json` : `trader_taus.spr` |
| Traders: in-approve degree at the freeze, liquidation-free close rate | 0.394 [0.261, 0.524]; B=400 | `window-w1/eval_summary.json` : `trader_taus.in_approve_degree` |
| Traders: transfer in-degree at the freeze, liquidation-free close rate | 0.253 [0.116, 0.363]; B=400 | `window-w1/eval_summary.json` : `trader_taus.in_degree` |

### EndorseRank results (not part of rule B)

| Quantity | Value | Source |
|---|---|---|
| endorserank minus degree appr | Δτ -0.082 [-0.090, -0.073]; τa 0.299, τb 0.381; P(Δτ>0) 0.000; B=400 | `window-w1/eval_summary.json` : `endorserank_results.endorserank_minus_degree_appr` |
| awp minus degree send | Δτ -0.041 [-0.047, -0.034]; τa 0.398, τb 0.439; P(Δτ>0) 0.000; B=400 | `window-w1/eval_summary.json` : `endorserank_results.awp_minus_degree_send` |
| cpr minus endorserank appr | Δτ 0.017 [0.006, 0.029]; τa 0.316, τb 0.299; P(Δτ>0) 0.998; B=400 | `window-w1/eval_summary.json` : `endorserank_results.cpr_minus_endorserank_appr` |
| cpr minus endorserank liq | Δτ -0.015 [-0.116, 0.094]; τa 0.282, τb 0.297; P(Δτ>0) 0.390; B=400 | `window-w1/eval_summary.json` : `endorserank_results.cpr_minus_endorserank_liq` |

### Comparison on outcomes built from neither edge type: rules R1-R3

| Quantity | Value | Source |
|---|---|---|
| Rule R1 | holds | `window-w1/eval_summary.json` : `neutral_rules.R1` |
| Rule R2 | does not hold | `window-w1/eval_summary.json` : `neutral_rules.R2` |
| Rule R3 | holds | `window-w1/eval_summary.json` : `neutral_rules.R3` |

### Neutral labels, W1 (2,000 paired resamples)

| Quantity | Value | Source |
|---|---|---|
| W1 traders | 70 | `window-w1/eval_summary.json` : `neutral_w1.n` |
| W1 highest in-approve degree among traders | 1.000 | `window-w1/eval_summary.json` : `neutral_w1.max_in_approve_degree` |
| W1 P: in-approve degree minus transfer in-degree, liquidation-free close rate | Δτ 0.141 [0.037, 0.240]; τa 0.394, τb 0.253; 97.5% [0.026, 0.256]; P(Δτ>0) 0.998; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.P.liquidation_free_rate` |
| W1 P: in-approve degree minus transfer in-degree, no liquidation | Δτ 0.141 [0.044, 0.232]; τa 0.407, τb 0.266; P(Δτ>0) 0.998; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.P.no_liquidation` |
| W1 P: in-approve degree minus transfer in-degree, profitable closes | Δτ -0.115 [-0.257, 0.025]; τa 0.042, τb 0.156; P(Δτ>0) 0.061; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.P.profitable_closes` |
| W1 P: in-approve degree minus transfer in-degree, realized gain | Δτ -0.109 [-0.247, 0.032]; τa 0.033, τb 0.142; P(Δτ>0) 0.069; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.P.realized_gain` |
| W1 P: in-approve degree minus transfer in-degree, profitable share | Δτ -0.162 [-0.295, -0.025]; τa -0.221, τb -0.059; P(Δτ>0) 0.009; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.P.profitable_share` |
| W1 P: in-approve degree minus transfer in-degree, non-loss share | Δτ -0.222 [-0.328, -0.106]; τa -0.294, τb -0.071; P(Δτ>0) 0.000; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.P.non_loss_share` |
| W1 Q: EndorseRank (activity restarts) minus AWP, liquidation-free close rate | Δτ 0.023 [-0.062, 0.113]; τa 0.286, τb 0.263; 97.5% [-0.071, 0.127]; P(Δτ>0) 0.700; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.Q.liquidation_free_rate` |
| W1 Q: EndorseRank (activity restarts) minus AWP, no liquidation | Δτ 0.027 [-0.066, 0.129]; τa 0.292, τb 0.265; P(Δτ>0) 0.709; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.Q.no_liquidation` |
| W1 Q: EndorseRank (activity restarts) minus AWP, profitable closes | Δτ -0.215 [-0.399, -0.042]; τa 0.049, τb 0.264; P(Δτ>0) 0.008; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.Q.profitable_closes` |
| W1 Q: EndorseRank (activity restarts) minus AWP, realized gain | Δτ -0.299 [-0.457, -0.146]; τa -0.019, τb 0.280; P(Δτ>0) 0.0005; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.Q.realized_gain` |
| W1 Q: EndorseRank (activity restarts) minus AWP, profitable share | Δτ -0.262 [-0.436, -0.100]; τa -0.200, τb 0.062; P(Δτ>0) 0.002; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.Q.profitable_share` |
| W1 Q: EndorseRank (activity restarts) minus AWP, non-loss share | Δτ -0.324 [-0.471, -0.188]; τa -0.275, τb 0.049; P(Δτ>0) 0.000; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.Q.non_loss_share` |
| W1 C-PR (λ=1) minus C-PR (λ=0), liquidation-free close rate | Δτ 0.019 [-0.093, 0.128]; τa 0.302, τb 0.282; P(Δτ>0) 0.635; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.layers.liquidation_free_rate` |
| W1 C-PR (λ=1) minus C-PR (λ=0), no liquidation | Δτ 0.021 [-0.087, 0.132]; τa 0.308, τb 0.286; P(Δτ>0) 0.652; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.layers.no_liquidation` |
| W1 C-PR (λ=1) minus C-PR (λ=0), profitable closes | Δτ -0.213 [-0.402, -0.028]; τa 0.009, τb 0.222; P(Δτ>0) 0.011; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.layers.profitable_closes` |
| W1 C-PR (λ=1) minus C-PR (λ=0), realized gain | Δτ -0.294 [-0.476, -0.116]; τa -0.066, τb 0.228; P(Δτ>0) 0.001; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.layers.realized_gain` |
| W1 C-PR (λ=1) minus C-PR (λ=0), profitable share | Δτ -0.266 [-0.461, -0.070]; τa -0.208, τb 0.058; P(Δτ>0) 0.002; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.layers.profitable_share` |
| W1 C-PR (λ=1) minus C-PR (λ=0), non-loss share | Δτ -0.316 [-0.481, -0.152]; τa -0.287, τb 0.029; P(Δτ>0) 0.000; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.layers.non_loss_share` |
| W1 EndorseRank minus AWP, liquidation-free close rate | Δτ 0.034 [-0.067, 0.134]; τa 0.297, τb 0.263; P(Δτ>0) 0.750; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.er_awp.liquidation_free_rate` |
| W1 EndorseRank minus AWP, no liquidation | Δτ 0.038 [-0.069, 0.149]; τa 0.303, τb 0.265; P(Δτ>0) 0.761; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.er_awp.no_liquidation` |
| W1 EndorseRank minus AWP, profitable closes | Δτ -0.200 [-0.390, -0.023]; τa 0.063, τb 0.264; P(Δτ>0) 0.011; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.er_awp.profitable_closes` |
| W1 EndorseRank minus AWP, realized gain | Δτ -0.292 [-0.460, -0.134]; τa -0.011, τb 0.280; P(Δτ>0) 0.0005; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.er_awp.realized_gain` |
| W1 EndorseRank minus AWP, profitable share | Δτ -0.246 [-0.427, -0.073]; τa -0.184, τb 0.062; P(Δτ>0) 0.002; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.er_awp.profitable_share` |
| W1 EndorseRank minus AWP, non-loss share | Δτ -0.315 [-0.468, -0.176]; τa -0.265, τb 0.049; P(Δτ>0) 0.000; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.er_awp.non_loss_share` |
| W1 C-PR (λ=0) minus AWP, liquidation-free close rate | Δτ 0.019 [-0.031, 0.066]; τa 0.282, τb 0.263; P(Δτ>0) 0.790; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.cpr0_awp.liquidation_free_rate` |
| W1 C-PR (λ=0) minus AWP, no liquidation | Δτ 0.021 [-0.031, 0.072]; τa 0.286, τb 0.265; P(Δτ>0) 0.797; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.cpr0_awp.no_liquidation` |
| W1 C-PR (λ=0) minus AWP, profitable closes | Δτ -0.042 [-0.087, 0.005]; τa 0.222, τb 0.264; P(Δτ>0) 0.036; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.cpr0_awp.profitable_closes` |
| W1 C-PR (λ=0) minus AWP, realized gain | Δτ -0.052 [-0.108, 0.002]; τa 0.228, τb 0.280; P(Δτ>0) 0.032; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.cpr0_awp.realized_gain` |
| W1 C-PR (λ=0) minus AWP, profitable share | Δτ -0.004 [-0.054, 0.043]; τa 0.058, τb 0.062; P(Δτ>0) 0.422; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.cpr0_awp.profitable_share` |
| W1 C-PR (λ=0) minus AWP, non-loss share | Δτ -0.021 [-0.065, 0.026]; τa 0.029, τb 0.049; P(Δτ>0) 0.187; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.cpr0_awp.non_loss_share` |
| W1 EndorseRank minus in-approve degree, liquidation-free close rate | Δτ -0.097 [-0.174, -0.009]; τa 0.297, τb 0.394; P(Δτ>0) 0.016; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.er_degree.liquidation_free_rate` |
| W1 EndorseRank minus in-approve degree, no liquidation | Δτ -0.103 [-0.180, -0.012]; τa 0.303, τb 0.407; P(Δτ>0) 0.011; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.er_degree.no_liquidation` |
| W1 EndorseRank minus in-approve degree, profitable closes | Δτ 0.022 [-0.080, 0.119]; τa 0.063, τb 0.042; P(Δτ>0) 0.663; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.er_degree.profitable_closes` |
| W1 EndorseRank minus in-approve degree, realized gain | Δτ -0.044 [-0.141, 0.058]; τa -0.011, τb 0.033; P(Δτ>0) 0.199; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.er_degree.realized_gain` |
| W1 EndorseRank minus in-approve degree, profitable share | Δτ 0.037 [-0.067, 0.134]; τa -0.184, τb -0.221; P(Δτ>0) 0.767; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.er_degree.profitable_share` |
| W1 EndorseRank minus in-approve degree, non-loss share | Δτ 0.028 [-0.068, 0.129]; τa -0.265, τb -0.294; P(Δτ>0) 0.724; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.er_degree.non_loss_share` |
| W1 P: in-approve degree minus transfer in-degree, stratified by closes | Δτ 0.145 [0.040, 0.328]; τa 0.381, τb 0.236 | `window-w1/eval_summary.json` : `neutral_w1.stratified.P` |
| W1 Q: EndorseRank (activity restarts) minus AWP, stratified by closes | Δτ 0.034 [-0.096, 0.171]; τa 0.273, τb 0.238 | `window-w1/eval_summary.json` : `neutral_w1.stratified.Q` |
| W1 recipients: n | 37 | `window-w1/eval_summary.json` : `neutral_w1.recipients.recipients.n` |
| W1 recipients: share no liquidation | 1.000 | `window-w1/eval_summary.json` : `neutral_w1.recipients.recipients.share_no_liquidation` |
| W1 recipients: mean liquidation free rate | 1.000 | `window-w1/eval_summary.json` : `neutral_w1.recipients.recipients.mean_liquidation_free_rate` |
| W1 recipients: mean profitable share | 0.325 | `window-w1/eval_summary.json` : `neutral_w1.recipients.recipients.mean_profitable_share` |
| W1 recipients: mean non loss share | 0.433 | `window-w1/eval_summary.json` : `neutral_w1.recipients.recipients.mean_non_loss_share` |
| W1 recipients: median closes | 24.000 | `window-w1/eval_summary.json` : `neutral_w1.recipients.recipients.median_closes` |
| W1 others: n | 33 | `window-w1/eval_summary.json` : `neutral_w1.recipients.others.n` |
| W1 others: share no liquidation | 0.727 | `window-w1/eval_summary.json` : `neutral_w1.recipients.others.share_no_liquidation` |
| W1 others: mean liquidation free rate | 0.878 | `window-w1/eval_summary.json` : `neutral_w1.recipients.others.mean_liquidation_free_rate` |
| W1 others: mean profitable share | 0.479 | `window-w1/eval_summary.json` : `neutral_w1.recipients.others.mean_profitable_share` |
| W1 others: mean non loss share | 0.644 | `window-w1/eval_summary.json` : `neutral_w1.recipients.others.mean_non_loss_share` |
| W1 others: median closes | 11.000 | `window-w1/eval_summary.json` : `neutral_w1.recipients.others.median_closes` |
| W1 P without the ten recipients of highest in-approve degree | Δτ 0.155 [0.032, 0.276]; τa 0.366, τb 0.211; P(Δτ>0) 0.996; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.influence_without_top10` |
| W1 EndorseRank, liquidation-free close rate | 0.297 [0.171, 0.410]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.endorserank.liquidation_free_rate` |
| W1 EndorseRank, no liquidation | 0.303 [0.172, 0.422]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.endorserank.no_liquidation` |
| W1 EndorseRank, profitable closes | 0.063 [-0.124, 0.253]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.endorserank.profitable_closes` |
| W1 EndorseRank, realized gain | -0.011 [-0.211, 0.187]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.endorserank.realized_gain` |
| W1 EndorseRank, profitable share | -0.184 [-0.341, -0.014]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.endorserank.profitable_share` |
| W1 EndorseRank, non-loss share | -0.265 [-0.411, -0.107]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.endorserank.non_loss_share` |
| W1 EndorseRank (activity restarts), liquidation-free close rate | 0.286 [0.156, 0.404]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.endorserank_activity.liquidation_free_rate` |
| W1 EndorseRank (activity restarts), no liquidation | 0.292 [0.155, 0.415]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.endorserank_activity.no_liquidation` |
| W1 EndorseRank (activity restarts), profitable closes | 0.049 [-0.129, 0.237]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.endorserank_activity.profitable_closes` |
| W1 EndorseRank (activity restarts), realized gain | -0.019 [-0.195, 0.166]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.endorserank_activity.realized_gain` |
| W1 EndorseRank (activity restarts), profitable share | -0.200 [-0.345, -0.037]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.endorserank_activity.profitable_share` |
| W1 EndorseRank (activity restarts), non-loss share | -0.275 [-0.418, -0.123]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.endorserank_activity.non_loss_share` |
| W1 AWP, liquidation-free close rate | 0.263 [0.141, 0.376]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.awp.liquidation_free_rate` |
| W1 AWP, no liquidation | 0.265 [0.139, 0.383]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.awp.no_liquidation` |
| W1 AWP, profitable closes | 0.264 [0.103, 0.408]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.awp.profitable_closes` |
| W1 AWP, realized gain | 0.280 [0.111, 0.435]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.awp.realized_gain` |
| W1 AWP, profitable share | 0.062 [-0.101, 0.213]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.awp.profitable_share` |
| W1 AWP, non-loss share | 0.049 [-0.090, 0.185]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.awp.non_loss_share` |
| W1 C-PR (λ=1), liquidation-free close rate | 0.302 [0.174, 0.419]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l100.liquidation_free_rate` |
| W1 C-PR (λ=1), no liquidation | 0.308 [0.175, 0.428]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l100.no_liquidation` |
| W1 C-PR (λ=1), profitable closes | 0.009 [-0.167, 0.192]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l100.profitable_closes` |
| W1 C-PR (λ=1), realized gain | -0.066 [-0.249, 0.120]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l100.realized_gain` |
| W1 C-PR (λ=1), profitable share | -0.208 [-0.370, -0.030]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l100.profitable_share` |
| W1 C-PR (λ=1), non-loss share | -0.287 [-0.443, -0.121]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l100.non_loss_share` |
| W1 C-PR (λ=0), liquidation-free close rate | 0.282 [0.162, 0.397]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l0.liquidation_free_rate` |
| W1 C-PR (λ=0), no liquidation | 0.286 [0.166, 0.400]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l0.no_liquidation` |
| W1 C-PR (λ=0), profitable closes | 0.222 [0.072, 0.366]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l0.profitable_closes` |
| W1 C-PR (λ=0), realized gain | 0.228 [0.063, 0.388]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l0.realized_gain` |
| W1 C-PR (λ=0), profitable share | 0.058 [-0.108, 0.210]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l0.profitable_share` |
| W1 C-PR (λ=0), non-loss share | 0.029 [-0.117, 0.170]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l0.non_loss_share` |
| W1 C-PR (λ=0.25), liquidation-free close rate | 0.282 [0.160, 0.399]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l25.liquidation_free_rate` |
| W1 C-PR (λ=0.25), no liquidation | 0.284 [0.163, 0.399]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l25.no_liquidation` |
| W1 C-PR (λ=0.25), profitable closes | 0.166 [0.011, 0.309]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l25.profitable_closes` |
| W1 C-PR (λ=0.25), realized gain | 0.168 [-0.002, 0.331]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l25.realized_gain` |
| W1 C-PR (λ=0.25), profitable share | 0.008 [-0.157, 0.162]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l25.profitable_share` |
| W1 C-PR (λ=0.25), non-loss share | -0.023 [-0.171, 0.117]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l25.non_loss_share` |
| W1 C-PR (λ=0.5), liquidation-free close rate | 0.282 [0.160, 0.399]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l50.liquidation_free_rate` |
| W1 C-PR (λ=0.5), no liquidation | 0.283 [0.162, 0.398]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l50.no_liquidation` |
| W1 C-PR (λ=0.5), profitable closes | 0.129 [-0.018, 0.271]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l50.profitable_closes` |
| W1 C-PR (λ=0.5), realized gain | 0.131 [-0.041, 0.297]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l50.realized_gain` |
| W1 C-PR (λ=0.5), profitable share | -0.025 [-0.185, 0.129]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l50.profitable_share` |
| W1 C-PR (λ=0.5), non-loss share | -0.062 [-0.210, 0.080]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l50.non_loss_share` |
| W1 C-PR (λ=0.75), liquidation-free close rate | 0.284 [0.161, 0.399]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l75.liquidation_free_rate` |
| W1 C-PR (λ=0.75), no liquidation | 0.284 [0.163, 0.398]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l75.no_liquidation` |
| W1 C-PR (λ=0.75), profitable closes | 0.103 [-0.049, 0.254]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l75.profitable_closes` |
| W1 C-PR (λ=0.75), realized gain | 0.099 [-0.076, 0.267]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l75.realized_gain` |
| W1 C-PR (λ=0.75), profitable share | -0.051 [-0.212, 0.107]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l75.profitable_share` |
| W1 C-PR (λ=0.75), non-loss share | -0.102 [-0.253, 0.047]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l75.non_loss_share` |
| W1 S-PR, liquidation-free close rate | 0.300 [0.174, 0.413]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.spr.liquidation_free_rate` |
| W1 S-PR, no liquidation | 0.304 [0.177, 0.418]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.spr.no_liquidation` |
| W1 S-PR, profitable closes | 0.177 [0.033, 0.310]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.spr.profitable_closes` |
| W1 S-PR, realized gain | 0.146 [-0.031, 0.321]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.spr.realized_gain` |
| W1 S-PR, profitable share | 0.009 [-0.143, 0.153]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.spr.profitable_share` |
| W1 S-PR, non-loss share | -0.027 [-0.169, 0.111]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.spr.non_loss_share` |
| W1 in-approve degree at the freeze, liquidation-free close rate | 0.394 [0.265, 0.518]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.in_approve_degree.liquidation_free_rate` |
| W1 in-approve degree at the freeze, no liquidation | 0.407 [0.268, 0.541]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.in_approve_degree.no_liquidation` |
| W1 in-approve degree at the freeze, profitable closes | 0.042 [-0.158, 0.243]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.in_approve_degree.profitable_closes` |
| W1 in-approve degree at the freeze, realized gain | 0.033 [-0.164, 0.230]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.in_approve_degree.realized_gain` |
| W1 in-approve degree at the freeze, profitable share | -0.221 [-0.406, -0.034]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.in_approve_degree.profitable_share` |
| W1 in-approve degree at the freeze, non-loss share | -0.294 [-0.468, -0.106]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.in_approve_degree.non_loss_share` |
| W1 transfer in-degree at the freeze, liquidation-free close rate | 0.253 [0.117, 0.379]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.in_degree.liquidation_free_rate` |
| W1 transfer in-degree at the freeze, no liquidation | 0.266 [0.125, 0.395]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.in_degree.no_liquidation` |
| W1 transfer in-degree at the freeze, profitable closes | 0.156 [-0.012, 0.306]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.in_degree.profitable_closes` |
| W1 transfer in-degree at the freeze, realized gain | 0.142 [-0.018, 0.278]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.in_degree.realized_gain` |
| W1 transfer in-degree at the freeze, profitable share | -0.059 [-0.225, 0.099]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.in_degree.profitable_share` |
| W1 transfer in-degree at the freeze, non-loss share | -0.071 [-0.225, 0.082]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.in_degree.non_loss_share` |

### Neutral labels, W0 (2,000 paired resamples)

| Quantity | Value | Source |
|---|---|---|
| W0 traders | 87 | `window-w1/eval_summary.json` : `neutral_w0.n` |
| W0 highest in-approve degree among traders | 3.000 | `window-w1/eval_summary.json` : `neutral_w0.max_in_approve_degree` |
| W0 P: in-approve degree minus transfer in-degree, liquidation-free close rate | Δτ 0.095 [-0.027, 0.234]; τa 0.345, τb 0.249; 97.5% [-0.041, 0.263]; P(Δτ>0) 0.925; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.P.liquidation_free_rate` |
| W0 P: in-approve degree minus transfer in-degree, no liquidation | Δτ 0.109 [-0.022, 0.257]; τa 0.357, τb 0.248; P(Δτ>0) 0.940; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.P.no_liquidation` |
| W0 P: in-approve degree minus transfer in-degree, profitable closes | Δτ -0.002 [-0.141, 0.129]; τa 0.067, τb 0.069; P(Δτ>0) 0.483; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.P.profitable_closes` |
| W0 P: in-approve degree minus transfer in-degree, realized gain | Δτ -0.026 [-0.176, 0.112]; τa 0.048, τb 0.074; P(Δτ>0) 0.347; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.P.realized_gain` |
| W0 P: in-approve degree minus transfer in-degree, profitable share | Δτ -0.043 [-0.182, 0.081]; τa -0.160, τb -0.117; P(Δτ>0) 0.285; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.P.profitable_share` |
| W0 P: in-approve degree minus transfer in-degree, non-loss share | Δτ -0.074 [-0.208, 0.052]; τa -0.288, τb -0.214; P(Δτ>0) 0.142; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.P.non_loss_share` |
| W0 Q: EndorseRank (activity restarts) minus AWP, liquidation-free close rate | Δτ -0.012 [-0.153, 0.149]; τa 0.242, τb 0.254; 97.5% [-0.177, 0.168]; P(Δτ>0) 0.425; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.Q.liquidation_free_rate` |
| W0 Q: EndorseRank (activity restarts) minus AWP, no liquidation | Δτ -0.005 [-0.162, 0.165]; τa 0.236, τb 0.241; P(Δτ>0) 0.466; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.Q.no_liquidation` |
| W0 Q: EndorseRank (activity restarts) minus AWP, profitable closes | Δτ -0.027 [-0.170, 0.113]; τa 0.139, τb 0.166; P(Δτ>0) 0.364; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.Q.profitable_closes` |
| W0 Q: EndorseRank (activity restarts) minus AWP, realized gain | Δτ -0.110 [-0.270, 0.040]; τa 0.087, τb 0.197; P(Δτ>0) 0.073; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.Q.realized_gain` |
| W0 Q: EndorseRank (activity restarts) minus AWP, profitable share | Δτ 0.044 [-0.084, 0.183]; τa -0.077, τb -0.121; P(Δτ>0) 0.766; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.Q.profitable_share` |
| W0 Q: EndorseRank (activity restarts) minus AWP, non-loss share | Δτ 0.078 [-0.055, 0.217]; τa -0.197, τb -0.275; P(Δτ>0) 0.896; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.Q.non_loss_share` |
| W0 C-PR (λ=1) minus C-PR (λ=0), liquidation-free close rate | Δτ -0.057 [-0.209, 0.092]; τa 0.237, τb 0.294; P(Δτ>0) 0.218; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.layers.liquidation_free_rate` |
| W0 C-PR (λ=1) minus C-PR (λ=0), no liquidation | Δτ -0.056 [-0.211, 0.098]; τa 0.235, τb 0.291; P(Δτ>0) 0.243; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.layers.no_liquidation` |
| W0 C-PR (λ=1) minus C-PR (λ=0), profitable closes | Δτ -0.089 [-0.244, 0.070]; τa 0.077, τb 0.166; P(Δτ>0) 0.130; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.layers.profitable_closes` |
| W0 C-PR (λ=1) minus C-PR (λ=0), realized gain | Δτ -0.257 [-0.447, -0.071]; τa 0.039, τb 0.297; P(Δτ>0) 0.003; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.layers.realized_gain` |
| W0 C-PR (λ=1) minus C-PR (λ=0), profitable share | Δτ 0.012 [-0.125, 0.150]; τa -0.076, τb -0.088; P(Δτ>0) 0.590; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.layers.profitable_share` |
| W0 C-PR (λ=1) minus C-PR (λ=0), non-loss share | Δτ 0.047 [-0.090, 0.191]; τa -0.186, τb -0.233; P(Δτ>0) 0.760; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.layers.non_loss_share` |
| W0 EndorseRank minus AWP, liquidation-free close rate | Δτ -0.019 [-0.173, 0.144]; τa 0.236, τb 0.254; P(Δτ>0) 0.401; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.er_awp.liquidation_free_rate` |
| W0 EndorseRank minus AWP, no liquidation | Δτ -0.007 [-0.170, 0.165]; τa 0.234, τb 0.241; P(Δτ>0) 0.456; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.er_awp.no_liquidation` |
| W0 EndorseRank minus AWP, profitable closes | Δτ -0.046 [-0.205, 0.113]; τa 0.120, τb 0.166; P(Δτ>0) 0.302; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.er_awp.profitable_closes` |
| W0 EndorseRank minus AWP, realized gain | Δτ -0.139 [-0.311, 0.022]; τa 0.058, τb 0.197; P(Δτ>0) 0.050; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.er_awp.realized_gain` |
| W0 EndorseRank minus AWP, profitable share | Δτ 0.074 [-0.066, 0.223]; τa -0.047, τb -0.121; P(Δτ>0) 0.851; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.er_awp.profitable_share` |
| W0 EndorseRank minus AWP, non-loss share | Δτ 0.108 [-0.034, 0.256]; τa -0.167, τb -0.275; P(Δτ>0) 0.939; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.er_awp.non_loss_share` |
| W0 C-PR (λ=0) minus AWP, liquidation-free close rate | Δτ 0.040 [-0.023, 0.098]; τa 0.294, τb 0.254; P(Δτ>0) 0.897; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.cpr0_awp.liquidation_free_rate` |
| W0 C-PR (λ=0) minus AWP, no liquidation | Δτ 0.050 [-0.015, 0.111]; τa 0.291, τb 0.241; P(Δτ>0) 0.935; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.cpr0_awp.no_liquidation` |
| W0 C-PR (λ=0) minus AWP, profitable closes | Δτ -0.0004717 [-0.064, 0.070]; τa 0.166, τb 0.166; P(Δτ>0) 0.470; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.cpr0_awp.profitable_closes` |
| W0 C-PR (λ=0) minus AWP, realized gain | Δτ 0.100 [0.018, 0.188]; τa 0.297, τb 0.197; P(Δτ>0) 0.993; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.cpr0_awp.realized_gain` |
| W0 C-PR (λ=0) minus AWP, profitable share | Δτ 0.032 [-0.041, 0.109]; τa -0.088, τb -0.121; P(Δτ>0) 0.798; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.cpr0_awp.profitable_share` |
| W0 C-PR (λ=0) minus AWP, non-loss share | Δτ 0.042 [-0.026, 0.117]; τa -0.233, τb -0.275; P(Δτ>0) 0.884; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.cpr0_awp.non_loss_share` |
| W0 EndorseRank minus in-approve degree, liquidation-free close rate | Δτ -0.109 [-0.196, -0.018]; τa 0.236, τb 0.345; P(Δτ>0) 0.010; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.er_degree.liquidation_free_rate` |
| W0 EndorseRank minus in-approve degree, no liquidation | Δτ -0.123 [-0.209, -0.024]; τa 0.234, τb 0.357; P(Δτ>0) 0.005; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.er_degree.no_liquidation` |
| W0 EndorseRank minus in-approve degree, profitable closes | Δτ 0.053 [-0.034, 0.137]; τa 0.120, τb 0.067; P(Δτ>0) 0.886; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.er_degree.profitable_closes` |
| W0 EndorseRank minus in-approve degree, realized gain | Δτ 0.010 [-0.080, 0.101]; τa 0.058, τb 0.048; P(Δτ>0) 0.593; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.er_degree.realized_gain` |
| W0 EndorseRank minus in-approve degree, profitable share | Δτ 0.113 [0.022, 0.210]; τa -0.047, τb -0.160; P(Δτ>0) 0.995; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.er_degree.profitable_share` |
| W0 EndorseRank minus in-approve degree, non-loss share | Δτ 0.121 [0.034, 0.211]; τa -0.167, τb -0.288; P(Δτ>0) 0.997; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.er_degree.non_loss_share` |
| W0 P: in-approve degree minus transfer in-degree, stratified by closes | Δτ 0.089 [-0.025, 0.252]; τa 0.342, τb 0.253 | `window-w1/eval_summary.json` : `neutral_w0.stratified.P` |
| W0 Q: EndorseRank (activity restarts) minus AWP, stratified by closes | Δτ -0.036 [-0.186, 0.145]; τa 0.229, τb 0.265 | `window-w1/eval_summary.json` : `neutral_w0.stratified.Q` |
| W0 recipients: n | 39 | `window-w1/eval_summary.json` : `neutral_w0.recipients.recipients.n` |
| W0 recipients: share no liquidation | 1.000 | `window-w1/eval_summary.json` : `neutral_w0.recipients.recipients.share_no_liquidation` |
| W0 recipients: mean liquidation free rate | 1.000 | `window-w1/eval_summary.json` : `neutral_w0.recipients.recipients.mean_liquidation_free_rate` |
| W0 recipients: mean profitable share | 0.359 | `window-w1/eval_summary.json` : `neutral_w0.recipients.recipients.mean_profitable_share` |
| W0 recipients: mean non loss share | 0.401 | `window-w1/eval_summary.json` : `neutral_w0.recipients.recipients.mean_non_loss_share` |
| W0 recipients: median closes | 30.000 | `window-w1/eval_summary.json` : `neutral_w0.recipients.recipients.median_closes` |
| W0 others: n | 48 | `window-w1/eval_summary.json` : `neutral_w0.recipients.others.n` |
| W0 others: share no liquidation | 0.750 | `window-w1/eval_summary.json` : `neutral_w0.recipients.others.share_no_liquidation` |
| W0 others: mean liquidation free rate | 0.919 | `window-w1/eval_summary.json` : `neutral_w0.recipients.others.mean_liquidation_free_rate` |
| W0 others: mean profitable share | 0.474 | `window-w1/eval_summary.json` : `neutral_w0.recipients.others.mean_profitable_share` |
| W0 others: mean non loss share | 0.607 | `window-w1/eval_summary.json` : `neutral_w0.recipients.others.mean_non_loss_share` |
| W0 others: median closes | 10.000 | `window-w1/eval_summary.json` : `neutral_w0.recipients.others.median_closes` |
| W0 P without the ten recipients of highest in-approve degree | Δτ 0.088 [-0.048, 0.240]; τa 0.321, τb 0.233; P(Δτ>0) 0.893; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.influence_without_top10` |
| W0 EndorseRank, liquidation-free close rate | 0.236 [0.108, 0.352]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.endorserank.liquidation_free_rate` |
| W0 EndorseRank, no liquidation | 0.234 [0.106, 0.353]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.endorserank.no_liquidation` |
| W0 EndorseRank, profitable closes | 0.120 [-0.036, 0.275]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.endorserank.profitable_closes` |
| W0 EndorseRank, realized gain | 0.058 [-0.097, 0.213]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.endorserank.realized_gain` |
| W0 EndorseRank, profitable share | -0.047 [-0.179, 0.092]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.endorserank.profitable_share` |
| W0 EndorseRank, non-loss share | -0.167 [-0.305, -0.033]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.endorserank.non_loss_share` |
| W0 EndorseRank (activity restarts), liquidation-free close rate | 0.242 [0.116, 0.357]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.endorserank_activity.liquidation_free_rate` |
| W0 EndorseRank (activity restarts), no liquidation | 0.236 [0.108, 0.353]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.endorserank_activity.no_liquidation` |
| W0 EndorseRank (activity restarts), profitable closes | 0.139 [-0.012, 0.293]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.endorserank_activity.profitable_closes` |
| W0 EndorseRank (activity restarts), realized gain | 0.087 [-0.068, 0.243]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.endorserank_activity.realized_gain` |
| W0 EndorseRank (activity restarts), profitable share | -0.077 [-0.208, 0.061]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.endorserank_activity.profitable_share` |
| W0 EndorseRank (activity restarts), non-loss share | -0.197 [-0.332, -0.060]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.endorserank_activity.non_loss_share` |
| W0 AWP, liquidation-free close rate | 0.254 [0.074, 0.405]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.awp.liquidation_free_rate` |
| W0 AWP, no liquidation | 0.241 [0.058, 0.395]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.awp.no_liquidation` |
| W0 AWP, profitable closes | 0.166 [0.004, 0.313]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.awp.profitable_closes` |
| W0 AWP, realized gain | 0.197 [0.037, 0.348]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.awp.realized_gain` |
| W0 AWP, profitable share | -0.121 [-0.270, 0.040]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.awp.profitable_share` |
| W0 AWP, non-loss share | -0.275 [-0.416, -0.136]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.awp.non_loss_share` |
| W0 C-PR (λ=1), liquidation-free close rate | 0.237 [0.108, 0.352]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l100.liquidation_free_rate` |
| W0 C-PR (λ=1), no liquidation | 0.235 [0.106, 0.354]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l100.no_liquidation` |
| W0 C-PR (λ=1), profitable closes | 0.077 [-0.080, 0.238]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l100.profitable_closes` |
| W0 C-PR (λ=1), realized gain | 0.039 [-0.126, 0.202]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l100.realized_gain` |
| W0 C-PR (λ=1), profitable share | -0.076 [-0.222, 0.072]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l100.profitable_share` |
| W0 C-PR (λ=1), non-loss share | -0.186 [-0.328, -0.048]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l100.non_loss_share` |
| W0 C-PR (λ=0), liquidation-free close rate | 0.294 [0.136, 0.428]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l0.liquidation_free_rate` |
| W0 C-PR (λ=0), no liquidation | 0.291 [0.128, 0.431]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l0.no_liquidation` |
| W0 C-PR (λ=0), profitable closes | 0.166 [0.012, 0.301]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l0.profitable_closes` |
| W0 C-PR (λ=0), realized gain | 0.297 [0.137, 0.440]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l0.realized_gain` |
| W0 C-PR (λ=0), profitable share | -0.088 [-0.241, 0.065]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l0.profitable_share` |
| W0 C-PR (λ=0), non-loss share | -0.233 [-0.378, -0.090]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l0.non_loss_share` |
| W0 C-PR (λ=0.25), liquidation-free close rate | 0.301 [0.144, 0.432]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l25.liquidation_free_rate` |
| W0 C-PR (λ=0.25), no liquidation | 0.299 [0.136, 0.436]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l25.no_liquidation` |
| W0 C-PR (λ=0.25), profitable closes | 0.163 [0.012, 0.297]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l25.profitable_closes` |
| W0 C-PR (λ=0.25), realized gain | 0.289 [0.132, 0.427]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l25.realized_gain` |
| W0 C-PR (λ=0.25), profitable share | -0.082 [-0.230, 0.069]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l25.profitable_share` |
| W0 C-PR (λ=0.25), non-loss share | -0.225 [-0.364, -0.082]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l25.non_loss_share` |
| W0 C-PR (λ=0.5), liquidation-free close rate | 0.297 [0.140, 0.430]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l50.liquidation_free_rate` |
| W0 C-PR (λ=0.5), no liquidation | 0.294 [0.131, 0.434]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l50.no_liquidation` |
| W0 C-PR (λ=0.5), profitable closes | 0.172 [0.024, 0.306]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l50.profitable_closes` |
| W0 C-PR (λ=0.5), realized gain | 0.287 [0.134, 0.423]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l50.realized_gain` |
| W0 C-PR (λ=0.5), profitable share | -0.080 [-0.225, 0.065]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l50.profitable_share` |
| W0 C-PR (λ=0.5), non-loss share | -0.222 [-0.365, -0.081]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l50.non_loss_share` |
| W0 C-PR (λ=0.75), liquidation-free close rate | 0.294 [0.135, 0.428]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l75.liquidation_free_rate` |
| W0 C-PR (λ=0.75), no liquidation | 0.292 [0.128, 0.431]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l75.no_liquidation` |
| W0 C-PR (λ=0.75), profitable closes | 0.166 [0.020, 0.296]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l75.profitable_closes` |
| W0 C-PR (λ=0.75), realized gain | 0.273 [0.122, 0.406]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l75.realized_gain` |
| W0 C-PR (λ=0.75), profitable share | -0.076 [-0.226, 0.066]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l75.profitable_share` |
| W0 C-PR (λ=0.75), non-loss share | -0.218 [-0.358, -0.077]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l75.non_loss_share` |
| W0 S-PR, liquidation-free close rate | 0.281 [0.120, 0.414]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.spr.liquidation_free_rate` |
| W0 S-PR, no liquidation | 0.274 [0.115, 0.407]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.spr.no_liquidation` |
| W0 S-PR, profitable closes | 0.168 [0.012, 0.307]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.spr.profitable_closes` |
| W0 S-PR, realized gain | 0.282 [0.121, 0.424]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.spr.realized_gain` |
| W0 S-PR, profitable share | -0.060 [-0.214, 0.096]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.spr.profitable_share` |
| W0 S-PR, non-loss share | -0.203 [-0.354, -0.061]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.spr.non_loss_share` |
| W0 in-approve degree at the freeze, liquidation-free close rate | 0.345 [0.240, 0.442]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.in_approve_degree.liquidation_free_rate` |
| W0 in-approve degree at the freeze, no liquidation | 0.357 [0.244, 0.465]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.in_approve_degree.no_liquidation` |
| W0 in-approve degree at the freeze, profitable closes | 0.067 [-0.113, 0.243]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.in_approve_degree.profitable_closes` |
| W0 in-approve degree at the freeze, realized gain | 0.048 [-0.132, 0.224]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.in_approve_degree.realized_gain` |
| W0 in-approve degree at the freeze, profitable share | -0.160 [-0.327, 0.023]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.in_approve_degree.profitable_share` |
| W0 in-approve degree at the freeze, non-loss share | -0.288 [-0.441, -0.122]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.in_approve_degree.non_loss_share` |
| W0 transfer in-degree at the freeze, liquidation-free close rate | 0.249 [0.090, 0.392]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.in_degree.liquidation_free_rate` |
| W0 transfer in-degree at the freeze, no liquidation | 0.248 [0.080, 0.398]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.in_degree.no_liquidation` |
| W0 transfer in-degree at the freeze, profitable closes | 0.069 [-0.085, 0.215]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.in_degree.profitable_closes` |
| W0 transfer in-degree at the freeze, realized gain | 0.074 [-0.090, 0.240]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.in_degree.realized_gain` |
| W0 transfer in-degree at the freeze, profitable share | -0.117 [-0.275, 0.041]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.in_degree.profitable_share` |
| W0 transfer in-degree at the freeze, non-loss share | -0.214 [-0.375, -0.058]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.in_degree.non_loss_share` |

### Supplementary spender contrasts (computed after the labels were known, outside every rule)

| Quantity | Value | Source |
|---|---|---|
| W0 EndorseRank (activity restarts) minus in-approve degree, new approval pairs | Δτ -0.060 [-0.070, -0.052]; τa 0.332, τb 0.392; P(Δτ>0) 0.000; B=400 | `supplementary/supplementary.json` : `w0.er_activity_minus_degree_appr` |
| W0 EndorseRank (activity restarts) minus EndorseRank, new approval pairs | Δτ 0.029 [0.023, 0.037]; τa 0.332, τb 0.303; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w0.er_activity_minus_er_appr` |
| W0 EndorseRank (activity restarts) minus EndorseRank, new transfer senders | Δτ -0.002 [-0.009, 0.005]; τa 0.270, τb 0.272; P(Δτ>0) 0.333; B=400 | `supplementary/supplementary.json` : `w0.er_activity_minus_er_send` |
| W0 EndorseRank minus AWP, new approval pairs | Δτ 0.107 [0.086, 0.130]; τa 0.303, τb 0.196; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w0.er_minus_awp_appr` |
| W0 EndorseRank minus AWP, new transfer senders | Δτ -0.138 [-0.151, -0.123]; τa 0.272, τb 0.409; P(Δτ>0) 0.000; B=400 | `supplementary/supplementary.json` : `w0.er_minus_awp_send` |
| W0 n | 7,914 | `supplementary/supplementary.json` : `w0.n` |
| W0 C-PR minus C-PR (λ=1), new transfer senders | Δτ 0.069 [0.057, 0.080]; τa 0.336, τb 0.267; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w0.cpr_minus_l100_send` |
| W0 C-PR minus EndorseRank, new transfer senders | Δτ 0.064 [0.052, 0.075]; τa 0.336, τb 0.272; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w0.cpr_minus_er_send` |
| W0 C-PR minus EndorseRank (activity restarts), new approval pairs | Δτ -0.003 [-0.014, 0.008]; τa 0.329, τb 0.332; P(Δτ>0) 0.290; B=400 | `supplementary/supplementary.json` : `w0.cpr_minus_er_activity_appr` |
| W0 C-PR minus EndorseRank (activity restarts), new transfer senders | Δτ 0.066 [0.055, 0.078]; τa 0.336, τb 0.270; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w0.cpr_minus_er_activity_send` |
| W0 C-PR minus S-PR, new approval pairs | Δτ 0.139 [0.121, 0.156]; τa 0.329, τb 0.190; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w0.cpr_minus_spr_appr` |
| W0 C-PR minus S-PR, new transfer senders | Δτ -0.041 [-0.049, -0.032]; τa 0.336, τb 0.377; P(Δτ>0) 0.000; B=400 | `supplementary/supplementary.json` : `w0.cpr_minus_spr_send` |
| W0 C-PR minus in-approve degree, new approval pairs | Δτ -0.063 [-0.076, -0.052]; τa 0.329, τb 0.392; P(Δτ>0) 0.000; B=400 | `supplementary/supplementary.json` : `w0.cpr_minus_degree_appr` |
| W0 C-PR minus in-approve degree, new transfer senders | Δτ 0.052 [0.038, 0.065]; τa 0.336, τb 0.284; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w0.cpr_minus_degree_send` |
| W0 C-PR minus transfer in-degree, new approval pairs | Δτ 0.126 [0.104, 0.145]; τa 0.329, τb 0.203; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w0.cpr_minus_in_degree_appr` |
| W0 C-PR minus transfer in-degree, new transfer senders | Δτ -0.111 [-0.121, -0.100]; τa 0.336, τb 0.447; P(Δτ>0) 0.000; B=400 | `supplementary/supplementary.json` : `w0.cpr_minus_in_degree_send` |
| W0 Spenders that had received a transfer before the freeze | 6,489 | `supplementary/supplementary.json` : `w0.recv_n` |
| W0 Received a transfer: C-PR, new approval pairs | 0.336 [0.321, 0.351]; B=400 | `supplementary/supplementary.json` : `w0.recv_cpr_tau_appr` |
| W0 Received a transfer: C-PR minus AWP, new approval pairs | Δτ 0.008 [-0.002, 0.020]; τa 0.336, τb 0.328; P(Δτ>0) 0.917; B=400 | `supplementary/supplementary.json` : `w0.recv_cpr_minus_awp_appr` |
| W0 Received a transfer: C-PR, new transfer senders | 0.372 [0.359, 0.386]; B=400 | `supplementary/supplementary.json` : `w0.recv_cpr_tau_send` |
| W0 Received a transfer: C-PR minus AWP, new transfer senders | Δτ -0.036 [-0.044, -0.026]; τa 0.372, τb 0.408; P(Δτ>0) 0.000; B=400 | `supplementary/supplementary.json` : `w0.recv_cpr_minus_awp_send` |
| W0 Received a transfer: C-PR minus in-approve degree, new approval pairs | Δτ -0.051 [-0.064, -0.037]; τa 0.336, τb 0.387; P(Δτ>0) 0.000; B=400 | `supplementary/supplementary.json` : `w0.recv_cpr_minus_degree_appr` |
| W1 EndorseRank (activity restarts) minus in-approve degree, new approval pairs | Δτ -0.046 [-0.055, -0.038]; τa 0.335, τb 0.381; P(Δτ>0) 0.000; B=400 | `supplementary/supplementary.json` : `w1.er_activity_minus_degree_appr` |
| W1 EndorseRank (activity restarts) minus EndorseRank, new approval pairs | Δτ 0.035 [0.029, 0.042]; τa 0.335, τb 0.299; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w1.er_activity_minus_er_appr` |
| W1 EndorseRank (activity restarts) minus EndorseRank, new transfer senders | Δτ -0.023 [-0.032, -0.013]; τa 0.236, τb 0.259; P(Δτ>0) 0.000; B=400 | `supplementary/supplementary.json` : `w1.er_activity_minus_er_send` |
| W1 EndorseRank minus AWP, new approval pairs | Δτ 0.142 [0.119, 0.164]; τa 0.299, τb 0.157; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w1.er_minus_awp_appr` |
| W1 EndorseRank minus AWP, new transfer senders | Δτ -0.139 [-0.154, -0.125]; τa 0.259, τb 0.398; P(Δτ>0) 0.000; B=400 | `supplementary/supplementary.json` : `w1.er_minus_awp_send` |
| W1 n | 7,960 | `supplementary/supplementary.json` : `w1.n` |
| W1 C-PR minus C-PR (λ=1), new transfer senders | Δτ 0.066 [0.054, 0.078]; τa 0.324, τb 0.257; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w1.cpr_minus_l100_send` |
| W1 C-PR minus EndorseRank, new transfer senders | Δτ 0.064 [0.051, 0.076]; τa 0.324, τb 0.259; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w1.cpr_minus_er_send` |
| W1 C-PR minus EndorseRank (activity restarts), new approval pairs | Δτ -0.019 [-0.029, -0.008]; τa 0.316, τb 0.335; P(Δτ>0) 0.000; B=400 | `supplementary/supplementary.json` : `w1.cpr_minus_er_activity_appr` |
| W1 C-PR minus EndorseRank (activity restarts), new transfer senders | Δτ 0.087 [0.075, 0.102]; τa 0.324, τb 0.236; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w1.cpr_minus_er_activity_send` |
| W1 C-PR minus S-PR, new approval pairs | Δτ 0.154 [0.134, 0.174]; τa 0.316, τb 0.162; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w1.cpr_minus_spr_appr` |
| W1 C-PR minus S-PR, new transfer senders | Δτ -0.044 [-0.052, -0.037]; τa 0.324, τb 0.367; P(Δτ>0) 0.000; B=400 | `supplementary/supplementary.json` : `w1.cpr_minus_spr_send` |
| W1 C-PR minus in-approve degree, new approval pairs | Δτ -0.065 [-0.077, -0.054]; τa 0.316, τb 0.381; P(Δτ>0) 0.000; B=400 | `supplementary/supplementary.json` : `w1.cpr_minus_degree_appr` |
| W1 C-PR minus in-approve degree, new transfer senders | Δτ 0.055 [0.040, 0.071]; τa 0.324, τb 0.269; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w1.cpr_minus_degree_send` |
| W1 C-PR minus transfer in-degree, new approval pairs | Δτ 0.151 [0.130, 0.173]; τa 0.316, τb 0.165; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w1.cpr_minus_in_degree_appr` |
| W1 C-PR minus transfer in-degree, new transfer senders | Δτ -0.115 [-0.128, -0.105]; τa 0.324, τb 0.439; P(Δτ>0) 0.000; B=400 | `supplementary/supplementary.json` : `w1.cpr_minus_in_degree_send` |
| W1 Spenders that had received a transfer before the freeze | 6,567 | `supplementary/supplementary.json` : `w1.recv_n` |
| W1 Received a transfer: C-PR, new approval pairs | 0.316 [0.300, 0.330]; B=400 | `supplementary/supplementary.json` : `w1.recv_cpr_tau_appr` |
| W1 Received a transfer: C-PR minus AWP, new approval pairs | Δτ 0.022 [0.011, 0.033]; τa 0.316, τb 0.294; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w1.recv_cpr_minus_awp_appr` |
| W1 Received a transfer: C-PR, new transfer senders | 0.353 [0.338, 0.368]; B=400 | `supplementary/supplementary.json` : `w1.recv_cpr_tau_send` |
| W1 Received a transfer: C-PR minus AWP, new transfer senders | Δτ -0.037 [-0.046, -0.028]; τa 0.353, τb 0.390; P(Δτ>0) 0.000; B=400 | `supplementary/supplementary.json` : `w1.recv_cpr_minus_awp_send` |
| W1 Received a transfer: C-PR minus in-approve degree, new approval pairs | Δτ -0.053 [-0.066, -0.041]; τa 0.316, τb 0.368; P(Δτ>0) 0.000; B=400 | `supplementary/supplementary.json` : `w1.recv_cpr_minus_degree_appr` |
| W1 C-PR minus EndorseRank (activity restarts), liquidation-free close rate | Δτ -0.004 [-0.102, 0.105]; τa 0.282, τb 0.286; P(Δτ>0) 0.485; B=400 | `supplementary/supplementary.json` : `w1.cpr_minus_er_activity_liq` |
| W1 C-PR minus S-PR, liquidation-free close rate | Δτ -0.017 [-0.094, 0.048]; τa 0.282, τb 0.300; P(Δτ>0) 0.307; B=400 | `supplementary/supplementary.json` : `w1.cpr_minus_spr_liq` |
| W1 C-PR minus in-approve degree, liquidation-free close rate | Δτ -0.112 [-0.194, -0.026]; τa 0.282, τb 0.394; P(Δτ>0) 0.010; B=400 | `supplementary/supplementary.json` : `w1.cpr_minus_degree_liq` |
| W1 C-PR minus transfer in-degree, liquidation-free close rate | Δτ 0.030 [-0.021, 0.099]; τa 0.282, τb 0.253; P(Δτ>0) 0.805; B=400 | `supplementary/supplementary.json` : `w1.cpr_minus_in_degree_liq` |
| W1 Traders | 70 | `supplementary/supplementary.json` : `w1.traders_n` |
| SAME Same window: C-PR minus EndorseRank, transfer family | Δτ 0.204 [0.191, 0.214]; τa 0.400, τb 0.196; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `same.cpr_minus_er_transfer` |
| SAME Same window: C-PR minus AWP, allowance family | Δτ 0.223 [0.206, 0.240]; τa 0.449, τb 0.226; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `same.cpr_minus_awp_allowance` |
| SAME n | 6,483 | `supplementary/supplementary.json` : `same.n` |

## 8. Sybil cost model (EndorseRank graph at T_obs)

| Quantity | Value | Source |
|---|---|---|
| graph.nodes | 2,513,982 | `sybil-model/sybil_model.json` : `graph.nodes` |
| graph.edges | 3,808,949 | `sybil-model/sybil_model.json` : `graph.edges` |
| sigma0 | 0.8581 | `sybil-model/sybil_model.json` : `sigma0` |
| b common | 1.928e-07 | `sybil-model/sybil_model.json` : `b_common` |
| r D | 0.3939 | `sybil-model/sybil_model.json` : `r_D` |
| damping.0.75.r D | 0.3652 | `sybil-model/sybil_model.json` : `damping.0.75.r_D` |
| damping.0.75.farm factor | 2.0956 | `sybil-model/sybil_model.json` : `damping.0.75.farm_factor` |
| damping.0.85.r D | 0.3939 | `sybil-model/sybil_model.json` : `damping.0.85.r_D` |
| damping.0.85.farm factor | 3.2320 | `sybil-model/sybil_model.json` : `damping.0.85.farm_factor` |
| damping.0.95.r D | 0.4191 | `sybil-model/sybil_model.json` : `damping.0.95.r_D` |
| damping.0.95.farm factor | 8.9626 | `sybil-model/sybil_model.json` : `damping.0.95.farm_factor` |
| ring20 collects times share | 3.2317 | `sybil-model/sybil_model.json` : `ring20_collects_times_share` |
| star.m | 10 | `sybil-model/sybil_model.json` : `star.m` |
| star.target score | 6.601e-06 | `sybil-model/sybil_model.json` : `star.target_score` |
| star.closed form | 6.602e-06 | `sybil-model/sybil_model.json` : `star.closed_form` |
| star.highest cohort endorserank | 0.0278 | `sybil-model/sybil_model.json` : `star.highest_cohort_endorserank` |
| star.ratio to highest | 0.0002374 | `sybil-model/sybil_model.json` : `star.ratio_to_highest` |
| star.approvals per window | 20 | `sybil-model/sybil_model.json` : `star.approvals_per_window` |
| fresh approval share median owner | 0.6830 | `sybil-model/sybil_model.json` : `fresh_approval_share_median_owner` |
| owners | 2,508,006 | `sybil-model/sybil_model.json` : `owners` |
| farm size to reach cohort quantile.p50.score | 5.817e-07 | `sybil-model/sybil_model.json` : `farm_size_to_reach_cohort_quantile.p50.score` |
| farm size to reach cohort quantile.p50.farm addresses | 0.0000 | `sybil-model/sybil_model.json` : `farm_size_to_reach_cohort_quantile.p50.farm_addresses` |
| farm size to reach cohort quantile.p90.score | 1.557e-05 | `sybil-model/sybil_model.json` : `farm_size_to_reach_cohort_quantile.p90.score` |
| farm size to reach cohort quantile.p90.farm addresses | 25.1891 | `sybil-model/sybil_model.json` : `farm_size_to_reach_cohort_quantile.p90.farm_addresses` |
| farm size to reach cohort quantile.p99.score | 0.0014 | `sybil-model/sybil_model.json` : `farm_size_to_reach_cohort_quantile.p99.score` |
| farm size to reach cohort quantile.p99.farm addresses | 2,291.7 | `sybil-model/sybil_model.json` : `farm_size_to_reach_cohort_quantile.p99.farm_addresses` |
| farm size to reach cohort quantile.p100.score | 0.0278 | `sybil-model/sybil_model.json` : `farm_size_to_reach_cohort_quantile.p100.score` |
| farm size to reach cohort quantile.p100.farm addresses | 47,072.6 | `sybil-model/sybil_model.json` : `farm_size_to_reach_cohort_quantile.p100.farm_addresses` |

## 9. Robustness

| Quantity | Value | Source |
|---|---|---|
| Damping endorserank_d75: iterations | 38 | `same-window/eval_summary.json` : `damping.endorserank_d75.iterations` |
| Damping endorserank_d75: transfer family | 0.196 [0.180, 0.215]; B=400 | `same-window/eval_summary.json` : `damping.endorserank_d75.transfer` |
| Damping endorserank_d75: allowance family | 0.561 [0.549, 0.573]; B=400 | `same-window/eval_summary.json` : `damping.endorserank_d75.allowance` |
| Damping endorserank_d75: Sybil stability family | 0.026 [0.012, 0.041]; B=400 | `same-window/eval_summary.json` : `damping.endorserank_d75.sybil_stability` |
| Damping awp_d75: iterations | 56 | `same-window/eval_summary.json` : `damping.awp_d75.iterations` |
| Damping awp_d75: transfer family | 0.740 [0.732, 0.748]; B=400 | `same-window/eval_summary.json` : `damping.awp_d75.transfer` |
| Damping awp_d75: allowance family | 0.229 [0.212, 0.248]; B=400 | `same-window/eval_summary.json` : `damping.awp_d75.allowance` |
| Damping awp_d75: Sybil stability family | 0.427 [0.416, 0.441]; B=400 | `same-window/eval_summary.json` : `damping.awp_d75.sybil_stability` |
| Damping endorserank_d85: iterations | 57 | `same-window/eval_summary.json` : `damping.endorserank_d85.iterations` |
| Damping endorserank_d85: transfer family | 0.196 [0.180, 0.216]; B=400 | `same-window/eval_summary.json` : `damping.endorserank_d85.transfer` |
| Damping endorserank_d85: allowance family | 0.560 [0.548, 0.571]; B=400 | `same-window/eval_summary.json` : `damping.endorserank_d85.allowance` |
| Damping endorserank_d85: Sybil stability family | 0.026 [0.012, 0.041]; B=400 | `same-window/eval_summary.json` : `damping.endorserank_d85.sybil_stability` |
| Damping awp_d85: iterations | 94 | `same-window/eval_summary.json` : `damping.awp_d85.iterations` |
| Damping awp_d85: transfer family | 0.736 [0.728, 0.744]; B=400 | `same-window/eval_summary.json` : `damping.awp_d85.transfer` |
| Damping awp_d85: allowance family | 0.226 [0.210, 0.245]; B=400 | `same-window/eval_summary.json` : `damping.awp_d85.allowance` |
| Damping awp_d85: Sybil stability family | 0.419 [0.408, 0.434]; B=400 | `same-window/eval_summary.json` : `damping.awp_d85.sybil_stability` |
| Damping endorserank_d95: iterations | 174 | `same-window/eval_summary.json` : `damping.endorserank_d95.iterations` |
| Damping endorserank_d95: transfer family | 0.197 [0.181, 0.216]; B=400 | `same-window/eval_summary.json` : `damping.endorserank_d95.transfer` |
| Damping endorserank_d95: allowance family | 0.558 [0.547, 0.570]; B=400 | `same-window/eval_summary.json` : `damping.endorserank_d95.allowance` |
| Damping endorserank_d95: Sybil stability family | 0.027 [0.013, 0.041]; B=400 | `same-window/eval_summary.json` : `damping.endorserank_d95.sybil_stability` |
| Damping awp_d95: iterations | 269 | `same-window/eval_summary.json` : `damping.awp_d95.iterations` |
| Damping awp_d95: transfer family | 0.723 [0.715, 0.731]; B=400 | `same-window/eval_summary.json` : `damping.awp_d95.transfer` |
| Damping awp_d95: allowance family | 0.217 [0.200, 0.235]; B=400 | `same-window/eval_summary.json` : `damping.awp_d95.allowance` |
| Damping awp_d95: Sybil stability family | 0.406 [0.394, 0.420]; B=400 | `same-window/eval_summary.json` : `damping.awp_d95.sybil_stability` |
| Slope 1: EndorseRank, transfer | 0.196 | `robustness/robustness.json` : `value_slope.1.endorserank.transfer` |
| Slope 1: EndorseRank, allowance | 0.560 | `robustness/robustness.json` : `value_slope.1.endorserank.allowance` |
| Slope 1: EndorseRank, Sybil stability | 0.026 | `robustness/robustness.json` : `value_slope.1.endorserank.sybil_stability` |
| Slope 1: AWP, transfer | 0.736 | `robustness/robustness.json` : `value_slope.1.awp.transfer` |
| Slope 1: AWP, allowance | 0.226 | `robustness/robustness.json` : `value_slope.1.awp.allowance` |
| Slope 1: AWP, Sybil stability | 0.419 | `robustness/robustness.json` : `value_slope.1.awp.sybil_stability` |
| Slope 01x: EndorseRank, transfer | 0.196 | `robustness/robustness.json` : `value_slope.01x.endorserank.transfer` |
| Slope 01x: EndorseRank, allowance | 0.561 | `robustness/robustness.json` : `value_slope.01x.endorserank.allowance` |
| Slope 01x: EndorseRank, Sybil stability | 0.026 | `robustness/robustness.json` : `value_slope.01x.endorserank.sybil_stability` |
| Slope 01x: AWP, transfer | 0.736 | `robustness/robustness.json` : `value_slope.01x.awp.transfer` |
| Slope 01x: AWP, allowance | 0.224 | `robustness/robustness.json` : `value_slope.01x.awp.allowance` |
| Slope 01x: AWP, Sybil stability | 0.421 | `robustness/robustness.json` : `value_slope.01x.awp.sybil_stability` |
| Slope 01x: EndorseRank rank agreement with the main score | 0.979 | `robustness/robustness.json` : `value_slope.01x.tau_with_main.endorserank` |
| Slope 01x: AWP rank agreement with the main score | 0.969 | `robustness/robustness.json` : `value_slope.01x.tau_with_main.awp` |
| Slope 10x: EndorseRank, transfer | 0.196 | `robustness/robustness.json` : `value_slope.10x.endorserank.transfer` |
| Slope 10x: EndorseRank, allowance | 0.555 | `robustness/robustness.json` : `value_slope.10x.endorserank.allowance` |
| Slope 10x: EndorseRank, Sybil stability | 0.027 | `robustness/robustness.json` : `value_slope.10x.endorserank.sybil_stability` |
| Slope 10x: AWP, transfer | 0.734 | `robustness/robustness.json` : `value_slope.10x.awp.transfer` |
| Slope 10x: AWP, allowance | 0.226 | `robustness/robustness.json` : `value_slope.10x.awp.allowance` |
| Slope 10x: AWP, Sybil stability | 0.419 | `robustness/robustness.json` : `value_slope.10x.awp.sybil_stability` |
| Slope 10x: EndorseRank rank agreement with the main score | 0.971 | `robustness/robustness.json` : `value_slope.10x.tau_with_main.endorserank` |
| Slope 10x: AWP rank agreement with the main score | 0.964 | `robustness/robustness.json` : `value_slope.10x.tau_with_main.awp` |
| Stage n=1,000: EndorseRank, transfer | 0.225 | `robustness/robustness.json` : `sample_definition[0].endorserank.transfer` |
| Stage n=1,000: EndorseRank, allowance | 0.665 | `robustness/robustness.json` : `sample_definition[0].endorserank.allowance` |
| Stage n=1,000: EndorseRank, Sybil stability | 0.049 | `robustness/robustness.json` : `sample_definition[0].endorserank.sybil_stability` |
| Stage n=1,000: AWP, transfer | 0.752 | `robustness/robustness.json` : `sample_definition[0].awp.transfer` |
| Stage n=1,000: AWP, allowance | 0.228 | `robustness/robustness.json` : `sample_definition[0].awp.allowance` |
| Stage n=1,000: AWP, Sybil stability | 0.441 | `robustness/robustness.json` : `sample_definition[0].awp.sybil_stability` |
| Stage n=1,000: allowance edges | 485,181 | `robustness/robustness.json` : `sample_definition[0].allowance_edges` |
| Stage n=1,000: transfer edges | 1,385,217 | `robustness/robustness.json` : `sample_definition[0].transfer_edges` |
| Stage n=2,000: EndorseRank, transfer | 0.200 | `robustness/robustness.json` : `sample_definition[1].endorserank.transfer` |
| Stage n=2,000: EndorseRank, allowance | 0.611 | `robustness/robustness.json` : `sample_definition[1].endorserank.allowance` |
| Stage n=2,000: EndorseRank, Sybil stability | 0.036 | `robustness/robustness.json` : `sample_definition[1].endorserank.sybil_stability` |
| Stage n=2,000: AWP, transfer | 0.731 | `robustness/robustness.json` : `sample_definition[1].awp.transfer` |
| Stage n=2,000: AWP, allowance | 0.223 | `robustness/robustness.json` : `sample_definition[1].awp.allowance` |
| Stage n=2,000: AWP, Sybil stability | 0.421 | `robustness/robustness.json` : `sample_definition[1].awp.sybil_stability` |
| Stage n=2,000: allowance edges | 897,933 | `robustness/robustness.json` : `sample_definition[1].allowance_edges` |
| Stage n=2,000: transfer edges | 2,651,178 | `robustness/robustness.json` : `sample_definition[1].transfer_edges` |
| Stage n=5,000: EndorseRank, transfer | 0.201 | `robustness/robustness.json` : `sample_definition[2].endorserank.transfer` |
| Stage n=5,000: EndorseRank, allowance | 0.577 | `robustness/robustness.json` : `sample_definition[2].endorserank.allowance` |
| Stage n=5,000: EndorseRank, Sybil stability | 0.033 | `robustness/robustness.json` : `sample_definition[2].endorserank.sybil_stability` |
| Stage n=5,000: AWP, transfer | 0.735 | `robustness/robustness.json` : `sample_definition[2].awp.transfer` |
| Stage n=5,000: AWP, allowance | 0.229 | `robustness/robustness.json` : `sample_definition[2].awp.allowance` |
| Stage n=5,000: AWP, Sybil stability | 0.420 | `robustness/robustness.json` : `sample_definition[2].awp.sybil_stability` |
| Stage n=5,000: allowance edges | 2,578,378 | `robustness/robustness.json` : `sample_definition[2].allowance_edges` |
| Stage n=5,000: transfer edges | 7,042,072 | `robustness/robustness.json` : `sample_definition[2].transfer_edges` |
| Stage n=6,483: EndorseRank, transfer | 0.196 | `robustness/robustness.json` : `sample_definition[3].endorserank.transfer` |
| Stage n=6,483: EndorseRank, allowance | 0.560 | `robustness/robustness.json` : `sample_definition[3].endorserank.allowance` |
| Stage n=6,483: EndorseRank, Sybil stability | 0.026 | `robustness/robustness.json` : `sample_definition[3].endorserank.sybil_stability` |
| Stage n=6,483: AWP, transfer | 0.736 | `robustness/robustness.json` : `sample_definition[3].awp.transfer` |
| Stage n=6,483: AWP, allowance | 0.226 | `robustness/robustness.json` : `sample_definition[3].awp.allowance` |
| Stage n=6,483: AWP, Sybil stability | 0.419 | `robustness/robustness.json` : `sample_definition[3].awp.sybil_stability` |
| Stage n=6,483: allowance edges | 3,810,253 | `robustness/robustness.json` : `sample_definition[3].allowance_edges` |
| Stage n=6,483: transfer edges | 8,432,635 | `robustness/robustness.json` : `sample_definition[3].transfer_edges` |

## 10. Benchmark

| Quantity | Value | Source |
|---|---|---|
| Protocol: warmup runs | 1 | `benchmark/benchmark.json` : `protocol.warmup_runs` |
| Protocol: timed runs | 5 | `benchmark/benchmark.json` : `protocol.timed_runs` |
| Protocol: damping | 0.85 | `benchmark/benchmark.json` : `protocol.damping` |
| Protocol: tol | 1e-08 | `benchmark/benchmark.json` : `protocol.tol` |
| Protocol: max iter | 300 | `benchmark/benchmark.json` : `protocol.max_iter` |
| Machine: platform | Windows-10-10.0.26200-SP0 | `benchmark/benchmark.json` : `machine.platform` |
| Machine: processor | Intel64 Family 6 Model 170 Stepping 4, GenuineIntel | `benchmark/benchmark.json` : `machine.processor` |
| Machine: python | 3.11.9 | `benchmark/benchmark.json` : `machine.python` |
| Machine: numpy | 2.3.2 | `benchmark/benchmark.json` : `machine.numpy` |
| Machine: scipy | 1.16.1 | `benchmark/benchmark.json` : `machine.scipy` |
| Scaling seed | contract-benchmark-v1 | `benchmark/benchmark.json` : `scaling_seed` |
| Full graphs: EndorseRank | mean 2.657 s, SD 0.109 s; runs 2.799, 2.591, 2.562, 2.751, 2.582; peak 325.3 MB; iterations 57; \|V\| 2,513,982; \|E\| 3,808,949 | `benchmark/benchmark.json` : `main.endorserank` |
| Full graphs: AWP | mean 8.530 s, SD 0.618 s; runs 7.870, 7.925, 8.795, 9.308, 8.750; peak 663.7 MB; iterations 94; \|V\| 3,601,727; \|E\| 8,426,124 | `benchmark/benchmark.json` : `main.awp` |
| Full graphs: C-PR (λ=0.5) | mean 11.563 s, SD 0.214 s; runs 11.737, 11.304, 11.429, 11.527, 11.821; peak 719.1 MB; iterations 82; \|V\| 4,111,490; \|E\| 10,562,390 | `benchmark/benchmark.json` : `main.cpr_l50` |
| Full graphs: S-PR | mean 10.883 s, SD 0.330 s; runs 11.145, 10.580, 11.319, 10.743, 10.628; peak 509.4 MB; iterations 151; \|V\| 3,603,300; \|E\| 8,432,635 | `benchmark/benchmark.json` : `main.spr` |
| AWP/EndorseRank runtime ratio (derived) | 3.21 | `benchmark/benchmark.json` : `main.awp.mean_s / main.endorserank.mean_s` |
| AWP/EndorseRank edge ratio (derived) | 2.21 | `benchmark/benchmark.json` : `main.awp.edges / main.endorserank.edges` |
| Damping 0.75: EndorseRank | mean 1.986 s, SD 0.132 s; runs 2.179, 1.881, 1.859, 1.959, 2.054; peak 325.3 MB; iterations 38; \|V\| 2,513,982; \|E\| 3,808,949 | `benchmark/benchmark.json` : `damping.0.75.endorserank` |
| Damping 0.75: AWP | mean 5.956 s, SD 0.483 s; runs 6.566, 5.925, 6.196, 5.832, 5.260; peak 663.7 MB; iterations 56; \|V\| 3,601,727; \|E\| 8,426,124 | `benchmark/benchmark.json` : `damping.0.75.awp` |
| Damping 0.85: EndorseRank | mean 2.657 s, SD 0.109 s; runs 2.799, 2.591, 2.562, 2.751, 2.582; peak 325.3 MB; iterations 57; \|V\| 2,513,982; \|E\| 3,808,949 | `benchmark/benchmark.json` : `damping.0.85.endorserank` |
| Damping 0.85: AWP | mean 8.530 s, SD 0.618 s; runs 7.870, 7.925, 8.795, 9.308, 8.750; peak 663.7 MB; iterations 94; \|V\| 3,601,727; \|E\| 8,426,124 | `benchmark/benchmark.json` : `damping.0.85.awp` |
| Damping 0.95: EndorseRank | mean 8.113 s, SD 0.679 s; runs 7.560, 7.353, 8.068, 8.929, 8.654; peak 325.3 MB; iterations 174; \|V\| 2,513,982; \|E\| 3,808,949 | `benchmark/benchmark.json` : `damping.0.95.endorserank` |
| Damping 0.95: AWP | mean 20.805 s, SD 0.757 s; runs 21.964, 21.172, 20.230, 20.452, 20.206; peak 663.7 MB; iterations 269; \|V\| 3,601,727; \|E\| 8,426,124 | `benchmark/benchmark.json` : `damping.0.95.awp` |
| Stage n=1,000: EndorseRank | mean 0.498 s, SD 0.050 s; runs 0.530, 0.563, 0.496, 0.466, 0.435; peak 53.8 MB; iterations 43; \|V\| 451,248; \|E\| 485,077 | `benchmark/benchmark.json` : `scaling[0].endorserank` |
| Stage n=1,000: AWP | mean 1.307 s, SD 0.016 s; runs 1.305, 1.305, 1.298, 1.294, 1.334; peak 140.5 MB; iterations 96; \|V\| 953,795; \|E\| 1,382,177 | `benchmark/benchmark.json` : `scaling[0].awp` |
| Stage n=2,000: EndorseRank | mean 0.318 s, SD 0.008 s; runs 0.308, 0.321, 0.330, 0.319, 0.314; peak 87.7 MB; iterations 30; \|V\| 760,410; \|E\| 897,812 | `benchmark/benchmark.json` : `scaling[1].endorserank` |
| Stage n=2,000: AWP | mean 2.383 s, SD 0.062 s; runs 2.493, 2.353, 2.349, 2.358, 2.361; peak 243.7 MB; iterations 94; \|V\| 1,459,514; \|E\| 2,647,854 | `benchmark/benchmark.json` : `scaling[1].awp` |
| Stage n=5,000: EndorseRank | mean 1.672 s, SD 0.062 s; runs 1.740, 1.619, 1.596, 1.715, 1.689; peak 229.0 MB; iterations 57; \|V\| 1,834,957; \|E\| 2,577,926 | `benchmark/benchmark.json` : `scaling[2].endorserank` |
| Stage n=5,000: AWP | mean 6.620 s, SD 0.119 s; runs 6.711, 6.760, 6.461, 6.558, 6.610; peak 577.3 MB; iterations 95; \|V\| 3,183,096; \|E\| 7,035,600 | `benchmark/benchmark.json` : `scaling[2].awp` |
| Stage n=6,483 (reused main measurement): EndorseRank | mean 2.657 s, SD 0.109 s; runs 2.799, 2.591, 2.562, 2.751, 2.582; peak 325.3 MB; iterations 57; \|V\| 2,513,982; \|E\| 3,808,949 | `benchmark/benchmark.json` : `scaling[3].endorserank` |
| Stage n=6,483 (reused main measurement): AWP | mean 8.530 s, SD 0.618 s; runs 7.870, 7.925, 8.795, 9.308, 8.750; peak 663.7 MB; iterations 94; \|V\| 3,601,727; \|E\| 8,426,124 | `benchmark/benchmark.json` : `scaling[3].awp` |

## Data description (token list, rows left out, amounts in USD, constants, prices, GMX contract traders, timing)

| Quantity | Value | Source |
|---|---|---|
| rows.registered ego.approvals | 135,799,669 | `describe/describe.json` : `rows.registered_ego.approvals` |
| rows.registered ego.transfers | 580,802,372 | `describe/describe.json` : `rows.registered_ego.transfers` |
| rows.registered ego.approvals w1 | 18,199,269 | `describe/describe.json` : `rows.registered_ego.approvals_w1` |
| rows.registered ego.transfers w1 | 74,441,935 | `describe/describe.json` : `rows.registered_ego.transfers_w1` |
| rows.unlisted tokens.tokens | 44,119 | `describe/describe.json` : `rows.unlisted_tokens.tokens` |
| rows.unlisted tokens.approvals | 49,138,325 | `describe/describe.json` : `rows.unlisted_tokens.approvals` |
| rows.unlisted tokens.transfers | 117,646,035 | `describe/describe.json` : `rows.unlisted_tokens.transfers` |
| rows.unlisted tokens.approvals w1 | 5,985,398 | `describe/describe.json` : `rows.unlisted_tokens.approvals_w1` |
| rows.unlisted tokens.transfers w1 | 13,539,539 | `describe/describe.json` : `rows.unlisted_tokens.transfers_w1` |
| rows.listed tokens outside revised ego.approvals | 674,782 | `describe/describe.json` : `rows.listed_tokens_outside_revised_ego.approvals` |
| rows.listed tokens outside revised ego.transfers | 20,434,298 | `describe/describe.json` : `rows.listed_tokens_outside_revised_ego.transfers` |
| rows.listed tokens outside revised ego.approvals w1 | 13,189 | `describe/describe.json` : `rows.listed_tokens_outside_revised_ego.approvals_w1` |
| rows.listed tokens outside revised ego.transfers w1 | 2,276,971 | `describe/describe.json` : `rows.listed_tokens_outside_revised_ego.transfers_w1` |
| rows.revised ego.approvals | 85,986,562 | `describe/describe.json` : `rows.revised_ego.approvals` |
| rows.revised ego.transfers | 442,722,039 | `describe/describe.json` : `rows.revised_ego.transfers` |
| rows.revised ego.approvals w1 | 12,200,682 | `describe/describe.json` : `rows.revised_ego.approvals_w1` |
| rows.revised ego.transfers w1 | 58,625,425 | `describe/describe.json` : `rows.revised_ego.transfers_w1` |
| rows.revised share of registered.approvals | 0.6332 | `describe/describe.json` : `rows.revised_share_of_registered.approvals` |
| rows.revised share of registered.transfers | 0.7623 | `describe/describe.json` : `rows.revised_share_of_registered.transfers` |
| rows.revised share of registered.approvals w1 | 0.6704 | `describe/describe.json` : `rows.revised_share_of_registered.approvals_w1` |
| rows.revised share of registered.transfers w1 | 0.7875 | `describe/describe.json` : `rows.revised_share_of_registered.transfers_w1` |
| rows.revised transfers without price | 0 | `describe/describe.json` : `rows.revised_transfers_without_price` |
| amounts.latest allowances tobs | 4,185,287 | `describe/describe.json` : `amounts.latest_allowances_tobs` |
| amounts.unlimited allowances | 2,084,669 | `describe/describe.json` : `amounts.unlimited_allowances` |
| amounts.unlimited share | 0.4981 | `describe/describe.json` : `amounts.unlimited_share` |
| amounts.allowances at or above cap | 2,331,420 | `describe/describe.json` : `amounts.allowances_at_or_above_cap` |
| amounts.allowances at or above cap share | 0.5571 | `describe/describe.json` : `amounts.allowances_at_or_above_cap_share` |
| amounts.owners | 2,508,872 | `describe/describe.json` : `amounts.owners` |
| amounts.owners with unlimited | 1,389,569 | `describe/describe.json` : `amounts.owners_with_unlimited` |
| amounts.owners with both kinds | 256,803 | `describe/describe.json` : `amounts.owners_with_both_kinds` |
| amounts.finite allowance usd percentiles tobs.p10 | 1.1148 | `describe/describe.json` : `amounts.finite_allowance_usd_percentiles_tobs.p10` |
| amounts.finite allowance usd percentiles tobs.p25 | 10.6876 | `describe/describe.json` : `amounts.finite_allowance_usd_percentiles_tobs.p25` |
| amounts.finite allowance usd percentiles tobs.p50 | 100.7627 | `describe/describe.json` : `amounts.finite_allowance_usd_percentiles_tobs.p50` |
| amounts.finite allowance usd percentiles tobs.p75 | 1,370.6 | `describe/describe.json` : `amounts.finite_allowance_usd_percentiles_tobs.p75` |
| amounts.finite allowance usd percentiles tobs.p90 | 79,970.4 | `describe/describe.json` : `amounts.finite_allowance_usd_percentiles_tobs.p90` |
| amounts.finite allowance usd percentiles tobs.p99 | 2,048,622,604,561,610,761,337,653,976,079,983,536,590,324,800,421,888 | `describe/describe.json` : `amounts.finite_allowance_usd_percentiles_tobs.p99` |
| amounts.transfers obs | 442,722,039 | `describe/describe.json` : `amounts.transfers_obs` |
| amounts.transfer usd percentiles obs.p10 | 0.1829 | `describe/describe.json` : `amounts.transfer_usd_percentiles_obs.p10` |
| amounts.transfer usd percentiles obs.p25 | 12.2090 | `describe/describe.json` : `amounts.transfer_usd_percentiles_obs.p25` |
| amounts.transfer usd percentiles obs.p50 | 142.5157 | `describe/describe.json` : `amounts.transfer_usd_percentiles_obs.p50` |
| amounts.transfer usd percentiles obs.p75 | 694.9995 | `describe/describe.json` : `amounts.transfer_usd_percentiles_obs.p75` |
| amounts.transfer usd percentiles obs.p90 | 2,362.3 | `describe/describe.json` : `amounts.transfer_usd_percentiles_obs.p90` |
| amounts.transfer usd percentiles obs.p99 | 19,627.2 | `describe/describe.json` : `amounts.transfer_usd_percentiles_obs.p99` |
| constants.computed at | 2026-10-28T09:05:26+00:00 | `describe/describe.json` : `constants.computed_at` |
| constants.source | sql/13_usd_constants.sql on the W0 views of sql/21_usd12m_cohorts.sql (contract_rep.u12_constants): events of the W0 cohort from 2025-04-01 00:00:00 UTC to t1 | `describe/describe.json` : `constants.source` |
| constants.raw.m transfer | 169.3310 | `describe/describe.json` : `constants.raw.m_transfer` |
| constants.raw.n transfers | 492,666,999 | `describe/describe.json` : `constants.raw.n_transfers` |
| constants.raw.p99 transfer | 18,575.3 | `describe/describe.json` : `constants.raw.p99_transfer` |
| constants.raw.m allowance | 99.9700 | `describe/describe.json` : `constants.raw.m_allowance` |
| constants.raw.p99 allowance | 923,170,557,712,169,318,042,517,531,931,405,645,977,962,313,358,648,377,304,154,112 | `describe/describe.json` : `constants.raw.p99_allowance` |
| constants.raw.n finite allowances | 2,324,723 | `describe/describe.json` : `constants.raw.n_finite_allowances` |
| constants.raw.n unlimited allowances | 2,230,356 | `describe/describe.json` : `constants.raw.n_unlimited_allowances` |
| constants.raw.p10 transfer | 0.1992 | `describe/describe.json` : `constants.raw.p10_transfer` |
| constants.raw.p90 transfer | 2,421.4 | `describe/describe.json` : `constants.raw.p90_transfer` |
| constants.raw.p10 allowance | 1.1127 | `describe/describe.json` : `constants.raw.p10_allowance` |
| constants.raw.p90 allowance | 999,660.1 | `describe/describe.json` : `constants.raw.p90_allowance` |
| constants.m transfer usd | 170.0000 | `describe/describe.json` : `constants.m_transfer_usd` |
| constants.m allowance usd | 100.0000 | `describe/describe.json` : `constants.m_allowance_usd` |
| constants.cap allowance usd | 19,000 | `describe/describe.json` : `constants.cap_allowance_usd` |
| constants.b transfer | 0.0065 | `describe/describe.json` : `constants.b_transfer` |
| constants.b allowance | 0.0110 | `describe/describe.json` : `constants.b_allowance` |
| constants.unlimited base units | 114,999,999,999,999,997,377,225,245,734,177,625,043,124,954,484,653,241,178,190,190,737,365,693,104,128 | `describe/describe.json` : `constants.unlimited_base_units` |
| constants.rule | b = ln 3 / m with m the median rounded to two significant digits; the allowance cap U is the 99th percentile of the USD values of the transfers of the W0 score window, rounded to two significant digits | `describe/describe.json` : `constants.rule` |
| timing.revision commit utc | 951923a 2026-10-11T18:08:21+00:00 | `describe/describe.json` : `timing.revision_commit_utc` |
| timing.window revision commit utc | e6c352d 2026-10-28T09:02:41+00:00 | `describe/describe.json` : `timing.window_revision_commit_utc` |
| timing.usd ego tables jobs usd | 1.3100 | `describe/describe.json` : `timing.usd_ego_tables_jobs_usd` |
| timing.usd12m jobs usd | 2.4900 | `describe/describe.json` : `timing.usd12m_jobs_usd` |
| timing.bigquery usd total | 42.2400 | `describe/describe.json` : `timing.bigquery_usd_total` |
| timing.bigquery tib billed | 6.7590 | `describe/describe.json` : `timing.bigquery_tib_billed` |
| listed tokens | 64 | `describe/describe.json` : `listed_tokens` |

### Listed tokens: rows of the registered and revised ego tables, USD volume

| Quantity | Value | Source |
|---|---|---|
| WETH 0x82af49447d8a07e3bd95bd0d56f35241523fbab1 | registered approvals 25,657,527, transfers 175,468,585; revised approvals 25,436,560, transfers 166,231,108; transfer USD 187,624,576,798.2; without price 0.000 | `describe/describe.json` : `per_token[0]` |
| USDC 0xaf88d065e77c8cc2239327c5edb3a432268e5831 | registered approvals 19,788,193, transfers 166,973,568; revised approvals 19,749,004, transfers 160,525,234; transfer USD 490,331,748,584.1; without price 0.000 | `describe/describe.json` : `per_token[1]` |
| USD₮0 0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9 | registered approvals 30,443,521, transfers 64,623,759; revised approvals 30,340,339, transfers 62,360,589; transfer USD 104,330,610,345.5; without price 0.000 | `describe/describe.json` : `per_token[2]` |
| WBTC 0x2f2a2543b76a4166549f7aab2e75bef0aefc5b0f | registered approvals 8,305,711, transfers 33,424,788; revised approvals 8,201,066, transfers 32,409,742; transfer USD 77,321,918,867.5; without price 0.000 | `describe/describe.json` : `per_token[3]` |
| ARB 0x912ce59144191c1204e64559fe8253a0e49e6548 | registered approvals 2,466,392, transfers 22,665,637; revised approvals 2,259,593, transfers 21,195,366; transfer USD 10,185,070,991.3; without price 0.000 | `describe/describe.json` : `per_token[4]` |

### Daily prices per listed token

| Quantity | Value | Source |
|---|---|---|
| USDG 0x004b506865409877c9fa29bfb1eba929984b9bbc | days 695, filled 2, first 2024-11-05, min confidence 0.990 | `describe/describe.json` : `prices[0]` |
| PENDLE 0x0c880f6761f1af8d9aa9c466984b80dab9a8c9e8 | days 1,096, filled 0, first 2023-10-01, min confidence 0.990 | `describe/describe.json` : `prices[1]` |
| CRV 0x11cdb42b0eb46d95f990bedd4695a6e3fa034978 | days 1,096, filled 0, first 2023-10-01, min confidence 0.990 | `describe/describe.json` : `prices[2]` |
| LDO 0x13ad51ed4f1b7e9dc168d8a00cb3f4ddd85efa60 | days 1,096, filled 0, first 2023-10-01, min confidence 0.990 | `describe/describe.json` : `prices[3]` |
| FRAX 0x17fc002b466eec40dae837fc4be5c67993ddbd6f | days 1,096, filled 0, first 2023-10-01, min confidence 0.990 | `describe/describe.json` : `prices[4]` |
| Cake 0x1b896893dfc86bb67cf57767298b9073d2c1ba2c | days 1,096, filled 0, first 2023-10-01, min confidence 0.990 | `describe/describe.json` : `prices[5]` |
| cbETH 0x1debd73e752beaf79865fd6446b0c970eae7732f | days 1,096, filled 0, first 2023-10-01, min confidence 0.990 | `describe/describe.json` : `prices[6]` |
| sUSDe 0x211cc4dd073734da055fbf44a2b4667d5e5fe5d2 | days 925, filled 0, first 2024-03-20, min confidence 0.990 | `describe/describe.json` : `prices[7]` |
| AXL 0x23ee2343b892b1bb63503a4fabc840e0e2c6810f | days 1,096, filled 1, first 2023-10-01, min confidence 0.990 | `describe/describe.json` : `prices[8]` |
| PEPE 0x25d887ce7a35172c62febfd67a1856f20faebb00 | days 1,096, filled 0, first 2023-10-01, min confidence 0.990 | `describe/describe.json` : `prices[9]` |
| WBTC 0x2f2a2543b76a4166549f7aab2e75bef0aefc5b0f | days 1,096, filled 0, first 2023-10-01, min confidence 0.990 | `describe/describe.json` : `prices[10]` |
| RDNT 0x3082cc23568ea640225c2467653db90e9250aaa0 | days 1,096, filled 0, first 2023-10-01, min confidence 0.990 | `describe/describe.json` : `prices[11]` |
| COMP 0x354a6da3fcde098f8389cad84b0182725c6c91de | days 1,096, filled 0, first 2023-10-01, min confidence 0.990 | `describe/describe.json` : `prices[12]` |
| weETH 0x35751007a407ca6feffe80b3cb397736d2cf4dbe | days 1,000, filled 1, first 2024-01-05, min confidence 0.990 | `describe/describe.json` : `prices[13]` |
| SPELL 0x3e6648c5a70a150a88bce65f4ad4d506fe15d2af | days 1,096, filled 1, first 2023-10-01, min confidence 0.990 | `describe/describe.json` : `prices[14]` |
| MORPHO 0x40bd670a58238e6e230c430bbb5ce6ec0d40df48 | days 679, filled 0, first 2024-11-21, min confidence 0.990 | `describe/describe.json` : `prices[15]` |
| PYUSD 0x46850ad61c2b7d64d08c9c754f45254596696984 | days 1,096, filled 0, first 2023-10-01, min confidence 0.990 | `describe/describe.json` : `prices[16]` |
| crvUSD 0x498bf2b1e120fed3ad3d42ea2165e9b73f99c1e5 | days 1,096, filled 0, first 2023-10-01, min confidence 0.990 | `describe/describe.json` : `prices[17]` |
| MAGIC 0x539bde0d7dbd336b79148aa742883198bbf60342 | days 1,096, filled 1, first 2023-10-01, min confidence 0.990 | `describe/describe.json` : `prices[18]` |
| ENA 0x58538e6a46e07434d7e7375bc268d3cb839c0133 | days 912, filled 0, first 2024-04-02, min confidence 0.990 | `describe/describe.json` : `prices[19]` |
| wstETH 0x5979d7b546e38e414f7e9822514be443a4800529 | days 1,096, filled 0, first 2023-10-01, min confidence 0.990 | `describe/describe.json` : `prices[20]` |
| USDe 0x5d3a1ff2b6bab83b63cd9ad0787074081a52ef34 | days 1,023, filled 9, first 2023-12-13, min confidence 0.990 | `describe/describe.json` : `prices[21]` |
| 1INCH 0x6314c31a7a1652ce482cffe247e9cb7c3f4bb9af | days 1,096, filled 0, first 2023-10-01, min confidence 0.990 | `describe/describe.json` : `prices[22]` |
| USDS 0x6491c05a82219b8d1479057361ff1654749b876b | days 737, filled 2, first 2024-09-24, min confidence 0.990 | `describe/describe.json` : `prices[23]` |
| ZRO 0x6985884c4392d348587b19cb9eaaf157f13271cd | days 833, filled 0, first 2024-06-20, min confidence 0.990 | `describe/describe.json` : `prices[24]` |
| tBTC 0x6c84a8f1c29108f47a79964b5fe888d4f4d0de40 | days 1,096, filled 1, first 2023-10-01, min confidence 0.990 | `describe/describe.json` : `prices[25]` |
| GHO 0x7dff72693f6a4149b17e7c6314655f6a9f7c8b33 | days 1,096, filled 2, first 2023-10-01, min confidence 0.990 | `describe/describe.json` : `prices[26]` |
| APE 0x7f9fbf9bdd3f4105c478b996b648fe6e828a1e98 | days 1,096, filled 0, first 2023-10-01, min confidence 0.990 | `describe/describe.json` : `prices[27]` |
| WETH 0x82af49447d8a07e3bd95bd0d56f35241523fbab1 | days 1,096, filled 0, first 2023-10-01, min confidence 0.990 | `describe/describe.json` : `prices[28]` |
| YFI 0x82e3a8f066a6989666b031d916c43672085b1582 | days 1,096, filled 2, first 2023-10-01, min confidence 0.990 | `describe/describe.json` : `prices[29]` |
| ARB 0x912ce59144191c1204e64559fe8253a0e49e6548 | days 1,096, filled 0, first 2023-10-01, min confidence 0.990 | `describe/describe.json` : `prices[30]` |
| GRT 0x9623063377ad1b27544c965ccd7342f7ea7e88c7 | days 1,096, filled 0, first 2023-10-01, min confidence 0.990 | `describe/describe.json` : `prices[31]` |
| USDC 0xaf88d065e77c8cc2239327c5edb3a432268e5831 | days 1,096, filled 0, first 2023-10-01, min confidence 0.990 | `describe/describe.json` : `prices[32]` |
| AAVE 0xba5ddd1f9d7f570dc94a51479a000e3bce967196 | days 1,096, filled 0, first 2023-10-01, min confidence 0.990 | `describe/describe.json` : `prices[33]` |
| ATH 0xc87b37a581ec3257b734886d9d3a581f5a9d056c | days 841, filled 0, first 2024-06-12, min confidence 0.990 | `describe/describe.json` : `prices[34]` |
| RSR 0xca5ca9083702c56b481d1eec86f1776fdbd2e594 | days 1,096, filled 0, first 2023-10-01, min confidence 0.990 | `describe/describe.json` : `prices[35]` |
| WOO 0xcafcd85d8ca7ad1e1c6f82f651fa15e33aefd07b | days 1,096, filled 1, first 2023-10-01, min confidence 0.990 | `describe/describe.json` : `prices[36]` |
| SUSHI 0xd4d42f0b6def4ce0383636770ef773390d85c61a | days 1,096, filled 1, first 2023-10-01, min confidence 0.990 | `describe/describe.json` : `prices[37]` |
| DAI 0xda10009cbd5d07dd0cecc66161fc93d7c9000da1 | days 1,096, filled 0, first 2023-10-01, min confidence 0.990 | `describe/describe.json` : `prices[38]` |
| rETH 0xec70dcb4a1efa46b8f2d97c310c9c4790ba5ffa8 | days 1,096, filled 1, first 2023-10-01, min confidence 0.990 | `describe/describe.json` : `prices[39]` |
| LINK 0xf97f4df75117a78c1a5a0dbb814af92458539fb4 | days 1,096, filled 0, first 2023-10-01, min confidence 0.990 | `describe/describe.json` : `prices[40]` |
| UNI 0xfa7f8980b0f1e64a2062791cc3b0871572f1f7f0 | days 1,096, filled 0, first 2023-10-01, min confidence 0.990 | `describe/describe.json` : `prices[41]` |
| GMX 0xfc5a1a6eb076a2c7ad06ed22c90d7e710e35ad0a | days 1,096, filled 0, first 2023-10-01, min confidence 0.990 | `describe/describe.json` : `prices[42]` |
| USD₮0 0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9 | days 1,096, filled 0, first 2023-10-01, min confidence 0.990 | `describe/describe.json` : `prices[43]` |
| PAXG 0xfeb4dfc8c4cf7ed305bb08065d08ec6ee6728429 | days 1,096, filled 1, first 2023-10-01, min confidence 0.990 | `describe/describe.json` : `prices[44]` |
| USDC 0xff970a61a04b1ca14834a43f5de4533ebddb5cc8 | days 1,096, filled 0, first 2023-10-01, min confidence 0.990 | `describe/describe.json` : `prices[45]` |

### Daily prices of the selected tokens from 2025-04-01 to 2026-09-30

| Quantity | Value | Source |
|---|---|---|
| WBTC 0x2f2a2543b76a4166549f7aab2e75bef0aefc5b0f | days 548, second key 0, filled 0, one-day errors 0 | `describe/describe.json` : `price_days.per_token[0]` |
| WETH 0x82af49447d8a07e3bd95bd0d56f35241523fbab1 | days 548, second key 0, filled 0, one-day errors 0 | `describe/describe.json` : `price_days.per_token[1]` |
| ARB 0x912ce59144191c1204e64559fe8253a0e49e6548 | days 548, second key 0, filled 0, one-day errors 0 | `describe/describe.json` : `price_days.per_token[2]` |
| USDC 0xaf88d065e77c8cc2239327c5edb3a432268e5831 | days 548, second key 0, filled 0, one-day errors 0 | `describe/describe.json` : `price_days.per_token[3]` |
| USD₮0 0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9 | days 548, second key 0, filled 0, one-day errors 0 | `describe/describe.json` : `price_days.per_token[4]` |
| Chainlink check on those days, ARB | 20 dates, median 0.0005645, largest 0.002 (absolute relative difference) | `describe/describe.json` : `chainlink_check_in_windows.per_token.ARB` |
| Chainlink check on those days, USDC | 20 dates, median 9.873e-05, largest 0.0002229 (absolute relative difference) | `describe/describe.json` : `chainlink_check_in_windows.per_token.USDC` |
| Chainlink check on those days, USD₮0 | 20 dates, median 0.0001448, largest 0.001 (absolute relative difference) | `describe/describe.json` : `chainlink_check_in_windows.per_token.USD₮0` |
| Chainlink check on those days, WBTC | 20 dates, median 0.0004861, largest 0.002 (absolute relative difference) | `describe/describe.json` : `chainlink_check_in_windows.per_token.WBTC` |
| Chainlink check on those days, WETH | 20 dates, median 0.0004138, largest 0.001 (absolute relative difference) | `describe/describe.json` : `chainlink_check_in_windows.per_token.WETH` |
| GMX contract traders 2023Q4 | 1,119 closes, 180 accounts, 104 liquidations | `describe/describe.json` : `gmx_contract_traders_by_quarter` |
| GMX contract traders 2024Q1 | 7,956 closes, 1,247 accounts, 692 liquidations | `describe/describe.json` : `gmx_contract_traders_by_quarter` |
| GMX contract traders 2024Q2 | 11,509 closes, 2,120 accounts, 589 liquidations | `describe/describe.json` : `gmx_contract_traders_by_quarter` |
| GMX contract traders 2024Q3 | 7,947 closes, 1,807 accounts, 456 liquidations | `describe/describe.json` : `gmx_contract_traders_by_quarter` |
| GMX contract traders 2024Q4 | 7,343 closes, 1,321 accounts, 904 liquidations | `describe/describe.json` : `gmx_contract_traders_by_quarter` |
| GMX contract traders 2025Q1 | 6,929 closes, 497 accounts, 498 liquidations | `describe/describe.json` : `gmx_contract_traders_by_quarter` |
| GMX contract traders 2025Q2 | 12,080 closes, 368 accounts, 379 liquidations | `describe/describe.json` : `gmx_contract_traders_by_quarter` |
| GMX contract traders 2025Q3 | 28,753 closes, 1,750 accounts, 897 liquidations | `describe/describe.json` : `gmx_contract_traders_by_quarter` |
| GMX contract traders 2025Q4 | 40,240 closes, 1,915 accounts, 1,596 liquidations | `describe/describe.json` : `gmx_contract_traders_by_quarter` |
| GMX contract traders 2026Q1 | 6,026 closes, 269 accounts, 233 liquidations | `describe/describe.json` : `gmx_contract_traders_by_quarter` |
| GMX contract traders 2026Q2 | 3,783 closes, 169 accounts, 125 liquidations | `describe/describe.json` : `gmx_contract_traders_by_quarter` |
| GMX contract traders 2026Q3 | 6,805 closes, 165 accounts, 182 liquidations | `describe/describe.json` : `gmx_contract_traders_by_quarter` |
| approval_ego 2025-07 | 5,991,902 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2025-08 | 9,091,262 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2025-09 | 8,305,761 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2025-10 | 9,876,486 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2025-11 | 7,487,811 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2025-12 | 10,988,779 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2026-01 | 7,794,190 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2026-02 | 7,178,372 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2026-03 | 5,961,711 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2026-04 | 4,349,080 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2026-05 | 3,292,667 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2026-06 | 5,668,541 | `describe/describe.json` : `monthly_counts` |
| approval_ego_t1 2025-04 | 4,882,727 | `describe/describe.json` : `monthly_counts` |
| approval_ego_t1 2025-05 | 6,540,459 | `describe/describe.json` : `monthly_counts` |
| approval_ego_t1 2025-06 | 5,340,697 | `describe/describe.json` : `monthly_counts` |
| approval_ego_t1 2025-07 | 6,015,579 | `describe/describe.json` : `monthly_counts` |
| approval_ego_t1 2025-08 | 6,264,088 | `describe/describe.json` : `monthly_counts` |
| approval_ego_t1 2025-09 | 6,332,435 | `describe/describe.json` : `monthly_counts` |
| approval_ego_t1 2025-10 | 7,489,198 | `describe/describe.json` : `monthly_counts` |
| approval_ego_t1 2025-11 | 5,480,130 | `describe/describe.json` : `monthly_counts` |
| approval_ego_t1 2025-12 | 9,533,185 | `describe/describe.json` : `monthly_counts` |
| approval_ego_t1 2026-01 | 6,399,817 | `describe/describe.json` : `monthly_counts` |
| approval_ego_t1 2026-02 | 4,943,990 | `describe/describe.json` : `monthly_counts` |
| approval_ego_t1 2026-03 | 3,880,163 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2025-07 | 47,153,179 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2025-08 | 50,295,595 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2025-09 | 36,323,733 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2025-10 | 47,646,273 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2025-11 | 43,571,904 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2025-12 | 41,599,240 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2026-01 | 38,479,282 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2026-02 | 34,802,116 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2026-03 | 28,616,605 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2026-04 | 23,678,774 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2026-05 | 21,706,641 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2026-06 | 28,848,697 | `describe/describe.json` : `monthly_counts` |
| transfer_ego_t1 2025-04 | 39,627,790 | `describe/describe.json` : `monthly_counts` |
| transfer_ego_t1 2025-05 | 49,275,323 | `describe/describe.json` : `monthly_counts` |
| transfer_ego_t1 2025-06 | 41,171,254 | `describe/describe.json` : `monthly_counts` |
| transfer_ego_t1 2025-07 | 47,544,022 | `describe/describe.json` : `monthly_counts` |
| transfer_ego_t1 2025-08 | 49,902,905 | `describe/describe.json` : `monthly_counts` |
| transfer_ego_t1 2025-09 | 36,143,515 | `describe/describe.json` : `monthly_counts` |
| transfer_ego_t1 2025-10 | 47,363,411 | `describe/describe.json` : `monthly_counts` |
| transfer_ego_t1 2025-11 | 42,832,532 | `describe/describe.json` : `monthly_counts` |
| transfer_ego_t1 2025-12 | 40,800,596 | `describe/describe.json` : `monthly_counts` |
| transfer_ego_t1 2026-01 | 37,581,493 | `describe/describe.json` : `monthly_counts` |
| transfer_ego_t1 2026-02 | 33,237,094 | `describe/describe.json` : `monthly_counts` |
| transfer_ego_t1 2026-03 | 27,187,064 | `describe/describe.json` : `monthly_counts` |

## Token rows of the T_obs score window (reported; the five selected tokens are kept)

| Quantity | Value | Source |
|---|---|---|
| selected | WETH, USDC, USD₮0, ARB, WBTC | `usd/token_rows_12m.json` : `selected` |
| top priced by rows | WETH, USDC, USD₮0, WBTC, ARB | `usd/token_rows_12m.json` : `top_priced_by_rows` |
| same as selected | yes | `usd/token_rows_12m.json` : `same_as_selected` |
| tokens in window | 33,517 | `usd/token_rows_12m.json` : `tokens_in_window` |
| rows in window | 588,568,431 | `usd/token_rows_12m.json` : `rows_in_window` |
| 1. WETH | 175,675,769 rows (175,468,585 transfers, 207,184 latest allowances); selected | `usd/token_rows_12m.json` : `per_listed_token[0]` |
| 2. USDC | 169,599,362 rows (166,973,568 transfers, 2,625,794 latest allowances); selected | `usd/token_rows_12m.json` : `per_listed_token[1]` |
| 3. USD₮0 | 65,737,487 rows (64,623,759 transfers, 1,113,728 latest allowances); selected | `usd/token_rows_12m.json` : `per_listed_token[2]` |
| 4. WBTC | 33,542,142 rows (33,424,788 transfers, 117,354 latest allowances); selected | `usd/token_rows_12m.json` : `per_listed_token[3]` |
| 5. ARB | 22,790,294 rows (22,665,637 transfers, 124,657 latest allowances); selected | `usd/token_rows_12m.json` : `per_listed_token[4]` |
| 6. USDC | 14,471,516 rows (14,367,921 transfers, 103,595 latest allowances) | `usd/token_rows_12m.json` : `per_listed_token[5]` |
| 7. PENDLE | 5,729,768 rows (5,703,165 transfers, 26,603 latest allowances) | `usd/token_rows_12m.json` : `per_listed_token[6]` |
| 8. LINK | 2,399,040 rows (2,371,593 transfers, 27,447 latest allowances) | `usd/token_rows_12m.json` : `per_listed_token[7]` |
| 9. DAI | 2,087,101 rows (2,032,848 transfers, 54,253 latest allowances) | `usd/token_rows_12m.json` : `per_listed_token[8]` |
| 10. AAVE | 1,655,105 rows (1,637,233 transfers, 17,872 latest allowances) | `usd/token_rows_12m.json` : `per_listed_token[9]` |
