# Results digest

Written by `experiments/scripts/publish_results.py` on 2026-10-10 12:45 UTC from the summaries in this folder; nothing here is recomputed. Each row names the file (relative to this folder) and the key inside it. τ entries read `point [95% CI]`, contrasts `Δτ [95% CI]; τa, τb; P(Δτ>0)`, and `B` is the number of bootstrap resamples behind the interval. `SHA256SUMS.txt` lists the checksums of every file published here.

**Revised analysis** (docs/revision_price_weighting.md): amounts in USD over the listed tokens, decided after the registered results were known. Nothing in this digest is a registered result; the registered digest is in the parent folder.

- Code revision: `2705b28a4653d47a6940cca064bf923562db8f9d` with uncommitted changes (git status code) in: `scripts/chainlink_check.py (M)`, `scripts/export_latex.py (M)`, `scripts/run_holdout.py (M)`, `scripts/run_usd_pipeline.py (M)`, `scripts/run_usd_local.ps1 (??)`
- Published files: `same-window/eval_summary.json`, `holdout-w0/eval_summary.json`, `window-w1/eval_summary.json`, `registered-w1/extraction_manifest.json`, `sybil-model/sybil_model.json`, `robustness/robustness.json`, `benchmark/benchmark.json`, `supplementary/supplementary.json`, `describe/describe.json`, `cohort/matched_cohort.json`, `gmx/gmx_contract_closes_obs_decoded.json`, `gmx/gmx_contract_closes_w1_decoded.json`, `config/contract_reputation.yaml`, `docs/analysis_plan.md`, `docs/registration_w1.md`, `docs/revision_price_weighting.md`, `usd/listed_tokens.csv`, `usd/usd_inputs.json`, `usd/constants.json`, `usd/chainlink_check.json`

## 1. Cohort and graph sizes

| Quantity | Value | Source |
|---|---|---|
| Cohort rule | contracts of the registered cohort with non-zero approvals of a selected token (WETH, USDC, USDT0, ARB, WBTC) from >= 3 distinct owners, 2023-10-01 00:00:00 UTC to 2026-06-30 23:59:59 UTC | `cohort/matched_cohort.json` : `rule` |
| Candidate spenders | None | `cohort/matched_cohort.json` : `candidates` |
| Matched cohort (contracts) | 15,107 | `cohort/matched_cohort.json` : `cohort` |
| Revised cohort: registered cohort | 27,844 | `cohort/matched_cohort.json` : `registered_cohort` |
| Revised cohort: left out of registered | 12,737 | `cohort/matched_cohort.json` : `left_out_of_registered` |
| Anchor T_obs | 2026-06-30 23:59:59 UTC | `same-window/eval_summary.json` : `anchor` |
| Cohort scored in the same window | 15,107 | `same-window/eval_summary.json` : `cohort` |
| T_obs allowance graph, nodes | 6,221,665 | `same-window/eval_summary.json` : `graph.allowance.nodes` |
| T_obs allowance graph, edges | 11,210,114 | `same-window/eval_summary.json` : `graph.allowance.edges` |
| T_obs transfer graph, nodes | 7,884,602 | `same-window/eval_summary.json` : `graph.transfer.nodes` |
| T_obs transfer graph, edges | 25,001,216 | `same-window/eval_summary.json` : `graph.transfer.edges` |
| Cohort contracts outside the allowance graph | 523 | `same-window/eval_summary.json` : `graph.cohort_outside_allowance` |
| Cohort contracts outside the transfer graph | 2,670 | `same-window/eval_summary.json` : `graph.cohort_outside_transfer` |
| Cohort contracts outside both graphs | 80 | `same-window/eval_summary.json` : `graph.cohort_outside_both` |
| Power iterations at T_obs, EndorseRank | 69 | `same-window/eval_summary.json` : `iterations.endorserank` |
| Power iterations at T_obs, EndorseRank (activity restarts) | 74 | `same-window/eval_summary.json` : `iterations.endorserank_activity` |
| Power iterations at T_obs, AWP | 92 | `same-window/eval_summary.json` : `iterations.awp` |
| Power iterations at T_obs, C-PR (λ=1) | 63 | `same-window/eval_summary.json` : `iterations.cpr_l100` |
| Power iterations at T_obs, C-PR (λ=0) | 92 | `same-window/eval_summary.json` : `iterations.cpr_l0` |
| Power iterations at T_obs, C-PR (λ=0.25) | 80 | `same-window/eval_summary.json` : `iterations.cpr_l25` |
| Power iterations at T_obs, C-PR (λ=0.5) | 79 | `same-window/eval_summary.json` : `iterations.cpr_l50` |
| Power iterations at T_obs, C-PR (λ=0.75) | 79 | `same-window/eval_summary.json` : `iterations.cpr_l75` |
| Power iterations at T_obs, S-PR | 158 | `same-window/eval_summary.json` : `iterations.spr` |
| t1 graph, allowance edges | 10,650,258 | `holdout-w0/eval_summary.json` : `graph.allowance_edges` |
| t1 graph, transfer edges | 23,680,692 | `holdout-w0/eval_summary.json` : `graph.transfer_edges` |
| Power iterations at t1, EndorseRank | 70 | `holdout-w0/eval_summary.json` : `iterations.endorserank` |
| Power iterations at t1, EndorseRank (activity restarts) | 74 | `holdout-w0/eval_summary.json` : `iterations.endorserank_activity` |
| Power iterations at t1, AWP | 91 | `holdout-w0/eval_summary.json` : `iterations.awp` |
| Power iterations at t1, C-PR (λ=1) | 64 | `holdout-w0/eval_summary.json` : `iterations.cpr_l100` |
| Power iterations at t1, C-PR (λ=0) | 92 | `holdout-w0/eval_summary.json` : `iterations.cpr_l0` |
| Power iterations at t1, C-PR (λ=0.25) | 79 | `holdout-w0/eval_summary.json` : `iterations.cpr_l25` |
| Power iterations at t1, C-PR (λ=0.5) | 77 | `holdout-w0/eval_summary.json` : `iterations.cpr_l50` |
| Power iterations at t1, C-PR (λ=0.75) | 77 | `holdout-w0/eval_summary.json` : `iterations.cpr_l75` |
| Power iterations at t1, S-PR | 159 | `holdout-w0/eval_summary.json` : `iterations.spr` |
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
| EndorseRank, transfer family | 0.158 [0.147, 0.169]; B=400 | `same-window/eval_summary.json` : `families.endorserank.transfer` |
| EndorseRank, allowance family | 0.585 [0.578, 0.592]; B=400 | `same-window/eval_summary.json` : `families.endorserank.allowance` |
| EndorseRank, Sybil stability family | 0.007 [-0.001, 0.015]; B=400 | `same-window/eval_summary.json` : `families.endorserank.sybil_stability` |
| EndorseRank (activity restarts), transfer family | 0.164 [0.153, 0.173]; B=400 | `same-window/eval_summary.json` : `families.endorserank_activity.transfer` |
| EndorseRank (activity restarts), allowance family | 0.426 [0.418, 0.435]; B=400 | `same-window/eval_summary.json` : `families.endorserank_activity.allowance` |
| EndorseRank (activity restarts), Sybil stability family | 0.049 [0.039, 0.057]; B=400 | `same-window/eval_summary.json` : `families.endorserank_activity.sybil_stability` |
| AWP, transfer family | 0.572 [0.564, 0.580]; B=400 | `same-window/eval_summary.json` : `families.awp.transfer` |
| AWP, allowance family | 0.193 [0.182, 0.203]; B=400 | `same-window/eval_summary.json` : `families.awp.allowance` |
| AWP, Sybil stability family | 0.395 [0.387, 0.403]; B=400 | `same-window/eval_summary.json` : `families.awp.sybil_stability` |
| C-PR (λ=1), transfer family | 0.162 [0.151, 0.173]; B=400 | `same-window/eval_summary.json` : `families.cpr_l100.transfer` |
| C-PR (λ=1), allowance family | 0.597 [0.590, 0.604]; B=400 | `same-window/eval_summary.json` : `families.cpr_l100.allowance` |
| C-PR (λ=1), Sybil stability family | 0.011 [0.002, 0.019]; B=400 | `same-window/eval_summary.json` : `families.cpr_l100.sybil_stability` |
| C-PR (λ=0), transfer family | 0.659 [0.653, 0.666]; B=400 | `same-window/eval_summary.json` : `families.cpr_l0.transfer` |
| C-PR (λ=0), allowance family | 0.225 [0.214, 0.235]; B=400 | `same-window/eval_summary.json` : `families.cpr_l0.allowance` |
| C-PR (λ=0), Sybil stability family | 0.404 [0.396, 0.413]; B=400 | `same-window/eval_summary.json` : `families.cpr_l0.sybil_stability` |
| C-PR (λ=0.25), transfer family | 0.385 [0.374, 0.395]; B=400 | `same-window/eval_summary.json` : `families.cpr_l25.transfer` |
| C-PR (λ=0.25), allowance family | 0.457 [0.449, 0.465]; B=400 | `same-window/eval_summary.json` : `families.cpr_l25.allowance` |
| C-PR (λ=0.25), Sybil stability family | 0.155 [0.147, 0.164]; B=400 | `same-window/eval_summary.json` : `families.cpr_l25.sybil_stability` |
| C-PR (λ=0.5), transfer family | 0.365 [0.355, 0.375]; B=400 | `same-window/eval_summary.json` : `families.cpr_l50.transfer` |
| C-PR (λ=0.5), allowance family | 0.477 [0.469, 0.485]; B=400 | `same-window/eval_summary.json` : `families.cpr_l50.allowance` |
| C-PR (λ=0.5), Sybil stability family | 0.142 [0.134, 0.151]; B=400 | `same-window/eval_summary.json` : `families.cpr_l50.sybil_stability` |
| C-PR (λ=0.75), transfer family | 0.344 [0.333, 0.354]; B=400 | `same-window/eval_summary.json` : `families.cpr_l75.transfer` |
| C-PR (λ=0.75), allowance family | 0.492 [0.484, 0.500]; B=400 | `same-window/eval_summary.json` : `families.cpr_l75.allowance` |
| C-PR (λ=0.75), Sybil stability family | 0.129 [0.121, 0.138]; B=400 | `same-window/eval_summary.json` : `families.cpr_l75.sybil_stability` |
| S-PR, transfer family | 0.629 [0.621, 0.636]; B=400 | `same-window/eval_summary.json` : `families.spr.transfer` |
| S-PR, allowance family | 0.323 [0.313, 0.333]; B=400 | `same-window/eval_summary.json` : `families.spr.allowance` |
| S-PR, Sybil stability family | 0.398 [0.390, 0.406]; B=400 | `same-window/eval_summary.json` : `families.spr.sybil_stability` |

### Per proxy (τ_b [95% CI]; Spearman ρ)

| Quantity | Value | Source |
|---|---|---|
| EndorseRank, in_degree | 0.182 [0.169, 0.194]; ρ 0.261; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank.in_degree` |
| EndorseRank, in_value | 0.134 [0.123, 0.145]; ρ 0.205; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank.in_value` |
| EndorseRank, in_approve_degree | 0.655 [0.648, 0.662]; ρ 0.811; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank.in_approve_degree` |
| EndorseRank, in_approve_value | 0.515 [0.506, 0.524]; ρ 0.681; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank.in_approve_value` |
| EndorseRank, inbound_counterparty_ratio | -0.156 [-0.166, -0.147]; ρ -0.231; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank.inbound_counterparty_ratio` |
| EndorseRank, transfer_tenure_days | 0.080 [0.069, 0.091]; ρ 0.124; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank.transfer_tenure_days` |
| EndorseRank, active_months | 0.098 [0.087, 0.109]; ρ 0.146; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank.active_months` |
| EndorseRank (activity restarts), in_degree | 0.179 [0.167, 0.190]; ρ 0.254; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank_activity.in_degree` |
| EndorseRank (activity restarts), in_value | 0.149 [0.137, 0.158]; ρ 0.217; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank_activity.in_value` |
| EndorseRank (activity restarts), in_approve_degree | 0.447 [0.438, 0.457]; ρ 0.598; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank_activity.in_approve_degree` |
| EndorseRank (activity restarts), in_approve_value | 0.406 [0.396, 0.415]; ρ 0.562; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank_activity.in_approve_value` |
| EndorseRank (activity restarts), inbound_counterparty_ratio | -0.090 [-0.102, -0.080]; ρ -0.133; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank_activity.inbound_counterparty_ratio` |
| EndorseRank (activity restarts), transfer_tenure_days | 0.107 [0.096, 0.117]; ρ 0.157; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank_activity.transfer_tenure_days` |
| EndorseRank (activity restarts), active_months | 0.130 [0.118, 0.140]; ρ 0.185; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank_activity.active_months` |
| AWP, in_degree | 0.578 [0.569, 0.587]; ρ 0.744; B=400 | `same-window/eval_summary.json` : `per_proxy.awp.in_degree` |
| AWP, in_value | 0.566 [0.558, 0.575]; ρ 0.741; B=400 | `same-window/eval_summary.json` : `per_proxy.awp.in_value` |
| AWP, in_approve_degree | 0.206 [0.193, 0.217]; ρ 0.286; B=400 | `same-window/eval_summary.json` : `per_proxy.awp.in_approve_degree` |
| AWP, in_approve_value | 0.180 [0.169, 0.191]; ρ 0.260; B=400 | `same-window/eval_summary.json` : `per_proxy.awp.in_approve_value` |
| AWP, inbound_counterparty_ratio | 0.127 [0.114, 0.141]; ρ 0.234; B=400 | `same-window/eval_summary.json` : `per_proxy.awp.inbound_counterparty_ratio` |
| AWP, transfer_tenure_days | 0.508 [0.499, 0.517]; ρ 0.683; B=400 | `same-window/eval_summary.json` : `per_proxy.awp.transfer_tenure_days` |
| AWP, active_months | 0.549 [0.540, 0.558]; ρ 0.704; B=400 | `same-window/eval_summary.json` : `per_proxy.awp.active_months` |
| C-PR (λ=1), in_degree | 0.183 [0.171, 0.195]; ρ 0.262; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l100.in_degree` |
| C-PR (λ=1), in_value | 0.141 [0.130, 0.152]; ρ 0.214; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l100.in_value` |
| C-PR (λ=1), in_approve_degree | 0.654 [0.647, 0.660]; ρ 0.809; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l100.in_approve_degree` |
| C-PR (λ=1), in_approve_value | 0.540 [0.531, 0.549]; ρ 0.705; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l100.in_approve_value` |
| C-PR (λ=1), inbound_counterparty_ratio | -0.157 [-0.167, -0.147]; ρ -0.232; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l100.inbound_counterparty_ratio` |
| C-PR (λ=1), transfer_tenure_days | 0.086 [0.076, 0.096]; ρ 0.133; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l100.transfer_tenure_days` |
| C-PR (λ=1), active_months | 0.103 [0.092, 0.113]; ρ 0.153; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l100.active_months` |
| C-PR (λ=0), in_degree | 0.689 [0.682, 0.697]; ρ 0.843; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l0.in_degree` |
| C-PR (λ=0), in_value | 0.629 [0.621, 0.637]; ρ 0.804; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l0.in_value` |
| C-PR (λ=0), in_approve_degree | 0.262 [0.250, 0.273]; ρ 0.350; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l0.in_approve_degree` |
| C-PR (λ=0), in_approve_value | 0.188 [0.176, 0.199]; ρ 0.267; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l0.in_approve_value` |
| C-PR (λ=0), inbound_counterparty_ratio | 0.160 [0.147, 0.174]; ρ 0.272; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l0.inbound_counterparty_ratio` |
| C-PR (λ=0), transfer_tenure_days | 0.507 [0.498, 0.517]; ρ 0.681; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l0.transfer_tenure_days` |
| C-PR (λ=0), active_months | 0.546 [0.537, 0.555]; ρ 0.703; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l0.active_months` |
| C-PR (λ=0.25), in_degree | 0.390 [0.379, 0.402]; ρ 0.517; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l25.in_degree` |
| C-PR (λ=0.25), in_value | 0.379 [0.368, 0.389]; ρ 0.521; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l25.in_value` |
| C-PR (λ=0.25), in_approve_degree | 0.495 [0.486, 0.504]; ρ 0.650; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l25.in_approve_degree` |
| C-PR (λ=0.25), in_approve_value | 0.419 [0.410, 0.429]; ρ 0.581; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l25.in_approve_value` |
| C-PR (λ=0.25), inbound_counterparty_ratio | -0.096 [-0.106, -0.084]; ρ -0.135; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l25.inbound_counterparty_ratio` |
| C-PR (λ=0.25), transfer_tenure_days | 0.268 [0.258, 0.278]; ρ 0.384; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l25.transfer_tenure_days` |
| C-PR (λ=0.25), active_months | 0.294 [0.284, 0.305]; ρ 0.407; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l25.active_months` |
| C-PR (λ=0.5), in_degree | 0.369 [0.358, 0.381]; ρ 0.490; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l50.in_degree` |
| C-PR (λ=0.5), in_value | 0.361 [0.350, 0.372]; ρ 0.500; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l50.in_value` |
| C-PR (λ=0.5), in_approve_degree | 0.511 [0.503, 0.520]; ρ 0.667; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l50.in_approve_degree` |
| C-PR (λ=0.5), in_approve_value | 0.442 [0.433, 0.451]; ρ 0.608; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l50.in_approve_value` |
| C-PR (λ=0.5), inbound_counterparty_ratio | -0.106 [-0.116, -0.094]; ρ -0.151; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l50.inbound_counterparty_ratio` |
| C-PR (λ=0.5), transfer_tenure_days | 0.253 [0.243, 0.264]; ρ 0.365; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l50.transfer_tenure_days` |
| C-PR (λ=0.5), active_months | 0.278 [0.269, 0.290]; ρ 0.387; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l50.active_months` |
| C-PR (λ=0.75), in_degree | 0.347 [0.336, 0.359]; ρ 0.464; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l75.in_degree` |
| C-PR (λ=0.75), in_value | 0.341 [0.330, 0.351]; ρ 0.475; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l75.in_value` |
| C-PR (λ=0.75), in_approve_degree | 0.523 [0.515, 0.532]; ρ 0.679; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l75.in_approve_degree` |
| C-PR (λ=0.75), in_approve_value | 0.461 [0.452, 0.470]; ρ 0.629; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l75.in_approve_value` |
| C-PR (λ=0.75), inbound_counterparty_ratio | -0.111 [-0.121, -0.100]; ρ -0.161; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l75.inbound_counterparty_ratio` |
| C-PR (λ=0.75), transfer_tenure_days | 0.236 [0.226, 0.247]; ρ 0.342; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l75.transfer_tenure_days` |
| C-PR (λ=0.75), active_months | 0.261 [0.251, 0.272]; ρ 0.365; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l75.active_months` |
| S-PR, in_degree | 0.635 [0.626, 0.643]; ρ 0.794; B=400 | `same-window/eval_summary.json` : `per_proxy.spr.in_degree` |
| S-PR, in_value | 0.623 [0.614, 0.631]; ρ 0.798; B=400 | `same-window/eval_summary.json` : `per_proxy.spr.in_value` |
| S-PR, in_approve_degree | 0.362 [0.351, 0.373]; ρ 0.462; B=400 | `same-window/eval_summary.json` : `per_proxy.spr.in_approve_degree` |
| S-PR, in_approve_value | 0.284 [0.272, 0.294]; ρ 0.385; B=400 | `same-window/eval_summary.json` : `per_proxy.spr.in_approve_value` |
| S-PR, inbound_counterparty_ratio | 0.138 [0.125, 0.153]; ρ 0.247; B=400 | `same-window/eval_summary.json` : `per_proxy.spr.inbound_counterparty_ratio` |
| S-PR, transfer_tenure_days | 0.506 [0.497, 0.516]; ρ 0.679; B=400 | `same-window/eval_summary.json` : `per_proxy.spr.transfer_tenure_days` |
| S-PR, active_months | 0.548 [0.539, 0.557]; ρ 0.705; B=400 | `same-window/eval_summary.json` : `per_proxy.spr.active_months` |

## 3. Same-window contrasts, score agreement and rule A (secondary part)

| Quantity | Value | Source |
|---|---|---|
| [hybrid] C-PR transfer minus C-PR (l=0) transfer | Δτ -0.294 [-0.305, -0.284]; τa 0.365, τb 0.659; P(Δτ>0) 0.000; B=400 | `same-window/eval_summary.json` : `contrasts[0]` |
| [hybrid] C-PR allowance minus C-PR (l=1) allowance | Δτ -0.120 [-0.127, -0.113]; τa 0.477, τb 0.597; P(Δτ>0) 0.000; B=400 | `same-window/eval_summary.json` : `contrasts[1]` |
| [hybrid] C-PR sybil minus C-PR (l=0) sybil | Δτ -0.262 [-0.273, -0.253]; τa 0.142, τb 0.404; P(Δτ>0) 0.000; B=400 | `same-window/eval_summary.json` : `contrasts[2]` |
| [hybrid] C-PR sybil minus C-PR (l=1) sybil | Δτ 0.131 [0.126, 0.137]; τa 0.142, τb 0.011; P(Δτ>0) 1.000; B=400 | `same-window/eval_summary.json` : `contrasts[3]` |
| [hybrid] S-PR transfer minus C-PR (l=0) transfer | Δτ -0.031 [-0.035, -0.028]; τa 0.629, τb 0.659; P(Δτ>0) 0.000; B=400 | `same-window/eval_summary.json` : `contrasts[4]` |
| [hybrid] S-PR allowance minus C-PR (l=1) allowance | Δτ -0.274 [-0.285, -0.263]; τa 0.323, τb 0.597; P(Δτ>0) 0.000; B=400 | `same-window/eval_summary.json` : `contrasts[5]` |
| [hybrid] S-PR sybil minus C-PR (l=0) sybil | Δτ -0.007 [-0.009, -0.004]; τa 0.398, τb 0.404; P(Δτ>0) 0.000; B=400 | `same-window/eval_summary.json` : `contrasts[6]` |
| [hybrid] S-PR sybil minus C-PR (l=1) sybil | Δτ 0.387 [0.376, 0.399]; τa 0.398, τb 0.011; P(Δτ>0) 1.000; B=400 | `same-window/eval_summary.json` : `contrasts[7]` |
| [hybrid_single] C-PR transfer minus AWP transfer | Δτ -0.207 [-0.220, -0.194]; τa 0.365, τb 0.572; P(Δτ>0) 0.000; B=400 | `same-window/eval_summary.json` : `contrasts[8]` |
| [hybrid_single] C-PR allowance minus EndorseRank allowance | Δτ -0.108 [-0.115, -0.101]; τa 0.477, τb 0.585; P(Δτ>0) 0.000; B=400 | `same-window/eval_summary.json` : `contrasts[9]` |
| [hybrid_single] C-PR sybil minus AWP sybil | Δτ -0.253 [-0.263, -0.242]; τa 0.142, τb 0.395; P(Δτ>0) 0.000; B=400 | `same-window/eval_summary.json` : `contrasts[10]` |
| [hybrid_single] C-PR sybil minus EndorseRank sybil | Δτ 0.135 [0.129, 0.141]; τa 0.142, τb 0.007; P(Δτ>0) 1.000; B=400 | `same-window/eval_summary.json` : `contrasts[11]` |
| [er_awp] EndorseRank allowance minus EndorseRank transfer | Δτ 0.427 [0.416, 0.440]; τa 0.585, τb 0.158; P(Δτ>0) 1.000; B=400 | `same-window/eval_summary.json` : `contrasts[12]` |
| [er_awp] AWP transfer minus EndorseRank transfer | Δτ 0.414 [0.401, 0.427]; τa 0.572, τb 0.158; P(Δτ>0) 1.000; B=400 | `same-window/eval_summary.json` : `contrasts[13]` |
| [er_awp] EndorseRank allowance minus AWP allowance | Δτ 0.392 [0.380, 0.405]; τa 0.585, τb 0.193; P(Δτ>0) 1.000; B=400 | `same-window/eval_summary.json` : `contrasts[14]` |
| [er_awp] AWP sybil minus EndorseRank sybil | Δτ 0.388 [0.376, 0.401]; τa 0.395, τb 0.007; P(Δτ>0) 1.000; B=400 | `same-window/eval_summary.json` : `contrasts[15]` |
| [er_awp] EndorseRank in-approve degree minus EndorseRank in-degree | Δτ 0.473 [0.461, 0.486]; τa 0.655, τb 0.182; P(Δτ>0) 1.000; B=400 | `same-window/eval_summary.json` : `contrasts[16]` |
| EndorseRank vs AWP, τ_b | 0.174 [0.163, 0.185]; B=400 | `same-window/eval_summary.json` : `inter_method.endorserank_vs_awp` |
| EndorseRank vs AWP, isolated-node rule | 0.174 [0.163, 0.185]; B=400 | `same-window/eval_summary.json` : `inter_method.isolated` |
| Concordance: pairs | 114,103,171 | `same-window/eval_summary.json` : `inter_method.concordance.pairs` |
| Concordance: ordered by both | 110,354,162 | `same-window/eval_summary.json` : `inter_method.concordance.ordered_by_both` |
| Concordance: share ordered by both | 0.967 | `same-window/eval_summary.json` : `inter_method.concordance.share_ordered_by_both` |
| Concordance: discordant share of ordered | 0.412 | `same-window/eval_summary.json` : `inter_method.concordance.discordant_share_of_ordered` |
| Concordance: tau b | 0.174 | `same-window/eval_summary.json` : `inter_method.concordance.tau_b` |
| Rule A secondary, transfer: better layer C-PR (λ=0) | C-PR 0.365 vs interval [0.653, 0.666]; pass: no | `same-window/eval_summary.json` : `rule_a_secondary.transfer` |
| Rule A secondary, allowance: better layer C-PR (λ=1) | C-PR 0.477 vs interval [0.590, 0.604]; pass: no | `same-window/eval_summary.json` : `rule_a_secondary.allowance` |
| Rule A secondary, Sybil stability: C-PR above both layers | C-PR 0.142, λ=1 0.011, λ=0 0.404; pass: no | `same-window/eval_summary.json` : `rule_a_secondary.sybil_stability` |
| Rule A secondary part met | no | `same-window/eval_summary.json` : `rule_a_secondary.pass` |

## 4. Ties and the isolated-node rule

| Quantity | Value | Source |
|---|---|---|
| EndorseRank ties (same window) | distinct 13,625 of 15,107; zeros 535; largest block 535 at 0.000; share of pairs tied 0.0017 | `same-window/eval_summary.json` : `ties.endorserank` |
| EndorseRank (activity restarts) ties (same window) | distinct 14,532 of 15,107; zeros 535; largest block 535 at 0.000; share of pairs tied 0.0013 | `same-window/eval_summary.json` : `ties.endorserank_activity` |
| AWP ties (same window) | distinct 12,435 of 15,107; zeros 2,672; largest block 2,672 at 0.000; share of pairs tied 0.0313 | `same-window/eval_summary.json` : `ties.awp` |
| C-PR (λ=1) ties (same window) | distinct 12,817 of 15,107; zeros 523; largest block 523 at 0.000; share of pairs tied 0.0017 | `same-window/eval_summary.json` : `ties.cpr_l100` |
| C-PR (λ=0) ties (same window) | distinct 12,299 of 15,107; zeros 2,670; largest block 2,670 at 0.000; share of pairs tied 0.0312 | `same-window/eval_summary.json` : `ties.cpr_l0` |
| C-PR (λ=0.25) ties (same window) | distinct 14,703 of 15,107; zeros 80; largest block 80 at 0.000; share of pairs tied 7.724e-05 | `same-window/eval_summary.json` : `ties.cpr_l25` |
| C-PR (λ=0.5) ties (same window) | distinct 14,694 of 15,107; zeros 80; largest block 80 at 0.000; share of pairs tied 7.819e-05 | `same-window/eval_summary.json` : `ties.cpr_l50` |
| C-PR (λ=0.75) ties (same window) | distinct 14,687 of 15,107; zeros 80; largest block 80 at 0.000; share of pairs tied 7.572e-05 | `same-window/eval_summary.json` : `ties.cpr_l75` |
| S-PR ties (same window) | distinct 12,370 of 15,107; zeros 2,684; largest block 2,684 at 0.000; share of pairs tied 0.0316 | `same-window/eval_summary.json` : `ties.spr` |
| endorserank_iso (missing contracts as isolated nodes), transfer | 0.158 [0.146, 0.169]; B=400 | `same-window/eval_summary.json` : `isolated_rule.endorserank_iso.transfer` |
| endorserank_iso (missing contracts as isolated nodes), allowance | 0.585 [0.579, 0.592]; B=400 | `same-window/eval_summary.json` : `isolated_rule.endorserank_iso.allowance` |
| endorserank_iso (missing contracts as isolated nodes), Sybil stability | 0.007 [-0.002, 0.015]; B=400 | `same-window/eval_summary.json` : `isolated_rule.endorserank_iso.sybil_stability` |
| awp_iso (missing contracts as isolated nodes), transfer | 0.572 [0.564, 0.580]; B=400 | `same-window/eval_summary.json` : `isolated_rule.awp_iso.transfer` |
| awp_iso (missing contracts as isolated nodes), allowance | 0.193 [0.182, 0.203]; B=400 | `same-window/eval_summary.json` : `isolated_rule.awp_iso.allowance` |
| awp_iso (missing contracts as isolated nodes), Sybil stability | 0.395 [0.387, 0.403]; B=400 | `same-window/eval_summary.json` : `isolated_rule.awp_iso.sybil_stability` |
| EndorseRank ties (W0 spenders) | distinct 16,208 of 17,050; zeros 16; largest block 156 at 2.89e-07; share of pairs tied 0.0002668 | `holdout-w0/eval_summary.json` : `ties.endorserank` |
| AWP ties (W0 spenders) | distinct 14,158 of 17,050; zeros 2,891; largest block 2,891 at 0.000; share of pairs tied 0.0287 | `holdout-w0/eval_summary.json` : `ties.awp` |
| C-PR (λ=1) ties (W0 spenders) | distinct 13,712 of 17,050; zeros 0; largest block 305 at 8.648e-08; share of pairs tied 0.000829 | `holdout-w0/eval_summary.json` : `ties.cpr_l100` |

## 5. Closed-form check of EndorseRank, s(v) = c (1 + d δ(v))

| Quantity | Value | Source |
|---|---|---|
| Same window: common value c | 7.639e-08 | `same-window/eval_summary.json` : `closed_form.common_value_c` |
| Same window: spread of c | 1.0000 | `same-window/eval_summary.json` : `closed_form.spread_of_c` |
| Same window: spenders | 14,406 | `same-window/eval_summary.json` : `closed_form.spenders` |
| Same window: depth one spenders | 12,039 | `same-window/eval_summary.json` : `closed_form.depth_one_spenders` |
| Same window: within 1pct all | 0.8791 | `same-window/eval_summary.json` : `closed_form.within_1pct_all` |
| Same window: within 1pct depth one | 1.0000 | `same-window/eval_summary.json` : `closed_form.within_1pct_depth_one` |
| Same window: within 1pct deeper | 0.2645 | `same-window/eval_summary.json` : `closed_form.within_1pct_deeper` |
| Same window: tau score vs delta | 0.9245 | `same-window/eval_summary.json` : `closed_form.tau_score_vs_delta` |
| W0: common value c | 8.14e-08 | `holdout-w0/eval_summary.json` : `closed_form.common_value_c` |
| W0: spread of c | 1.0000 | `holdout-w0/eval_summary.json` : `closed_form.spread_of_c` |
| W0: spenders | 17,032 | `holdout-w0/eval_summary.json` : `closed_form.spenders` |
| W0: depth one spenders | 11,326 | `holdout-w0/eval_summary.json` : `closed_form.depth_one_spenders` |
| W0: within 1pct all | 0.7367 | `holdout-w0/eval_summary.json` : `closed_form.within_1pct_all` |
| W0: within 1pct depth one | 1.0000 | `holdout-w0/eval_summary.json` : `closed_form.within_1pct_depth_one` |
| W0: within 1pct deeper | 0.2140 | `holdout-w0/eval_summary.json` : `closed_form.within_1pct_deeper` |
| W0: tau score vs delta | 0.8126 | `holdout-w0/eval_summary.json` : `closed_form.tau_score_vs_delta` |

## 6. Holdout W0 (scores at t1, labels April to June 2026)

| Quantity | Value | Source |
|---|---|---|
| Freeze t1 | 2026-03-31 23:59:59 UTC | `holdout-w0/eval_summary.json` : `freeze` |
| Label window | 2026-04-01 00:00:00 UTC to 2026-06-30 23:59:59 UTC | `holdout-w0/eval_summary.json` : `labels` |
| Spenders with a positive latest allowance at t1, account type contract | 17,050 | `holdout-w0/eval_summary.json` : `spender_account_types.contract` |
| Spenders with a positive latest allowance at t1, account type none | 104 | `holdout-w0/eval_summary.json` : `spender_account_types.none` |
| Spenders with a positive latest allowance at t1, account type eip7702 | 13 | `holdout-w0/eval_summary.json` : `spender_account_types.eip7702` |
| Spender cohort (contracts) | 17,050 | `holdout-w0/eval_summary.json` : `spenders` |
| Gained a new approval pair | 2,070 | `holdout-w0/eval_summary.json` : `gained_new_approvals` |
| Gained a new transfer sender | 1,695 | `holdout-w0/eval_summary.json` : `gained_new_senders` |

### W0 spenders: τ_b with every label

| Quantity | Value | Source |
|---|---|---|
| EndorseRank, new approval pairs | 0.231 [0.220, 0.242]; B=400 | `holdout-w0/eval_summary.json` : `taus.endorserank.future_new_approvers` |
| EndorseRank, new transfer senders | 0.200 [0.189, 0.210]; B=400 | `holdout-w0/eval_summary.json` : `taus.endorserank.future_new_transfer_senders` |
| EndorseRank, revocations | 0.337 [0.327, 0.347]; B=400 | `holdout-w0/eval_summary.json` : `taus.endorserank.future_revoke_count` |
| EndorseRank, drained owners | 0.234 [0.224, 0.245]; B=400 | `holdout-w0/eval_summary.json` : `taus.endorserank.future_drain_owners` |
| EndorseRank (activity restarts), new approval pairs | 0.308 [0.299, 0.319]; B=400 | `holdout-w0/eval_summary.json` : `taus.endorserank_activity.future_new_approvers` |
| EndorseRank (activity restarts), new transfer senders | 0.269 [0.260, 0.278]; B=400 | `holdout-w0/eval_summary.json` : `taus.endorserank_activity.future_new_transfer_senders` |
| EndorseRank (activity restarts), revocations | 0.311 [0.300, 0.321]; B=400 | `holdout-w0/eval_summary.json` : `taus.endorserank_activity.future_revoke_count` |
| EndorseRank (activity restarts), drained owners | 0.328 [0.318, 0.338]; B=400 | `holdout-w0/eval_summary.json` : `taus.endorserank_activity.future_drain_owners` |
| AWP, new approval pairs | 0.196 [0.181, 0.210]; B=400 | `holdout-w0/eval_summary.json` : `taus.awp.future_new_approvers` |
| AWP, new transfer senders | 0.346 [0.336, 0.356]; B=400 | `holdout-w0/eval_summary.json` : `taus.awp.future_new_transfer_senders` |
| AWP, revocations | 0.191 [0.175, 0.205]; B=400 | `holdout-w0/eval_summary.json` : `taus.awp.future_revoke_count` |
| AWP, drained owners | 0.202 [0.186, 0.216]; B=400 | `holdout-w0/eval_summary.json` : `taus.awp.future_drain_owners` |
| C-PR (λ=1), new approval pairs | 0.223 [0.213, 0.233]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l100.future_new_approvers` |
| C-PR (λ=1), new transfer senders | 0.188 [0.177, 0.199]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l100.future_new_transfer_senders` |
| C-PR (λ=1), revocations | 0.335 [0.325, 0.345]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l100.future_revoke_count` |
| C-PR (λ=1), drained owners | 0.218 [0.207, 0.228]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l100.future_drain_owners` |
| C-PR (λ=0), new approval pairs | 0.160 [0.144, 0.174]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l0.future_new_approvers` |
| C-PR (λ=0), new transfer senders | 0.296 [0.285, 0.307]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l0.future_new_transfer_senders` |
| C-PR (λ=0), revocations | 0.200 [0.185, 0.214]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l0.future_revoke_count` |
| C-PR (λ=0), drained owners | 0.155 [0.140, 0.169]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l0.future_drain_owners` |
| C-PR (λ=0.25), new approval pairs | 0.253 [0.243, 0.264]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l25.future_new_approvers` |
| C-PR (λ=0.25), new transfer senders | 0.269 [0.257, 0.280]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l25.future_new_transfer_senders` |
| C-PR (λ=0.25), revocations | 0.323 [0.312, 0.332]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l25.future_revoke_count` |
| C-PR (λ=0.25), drained owners | 0.254 [0.242, 0.264]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l25.future_drain_owners` |
| C-PR (λ=0.5), new approval pairs | 0.252 [0.241, 0.262]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l50.future_new_approvers` |
| C-PR (λ=0.5), new transfer senders | 0.262 [0.250, 0.273]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l50.future_new_transfer_senders` |
| C-PR (λ=0.5), revocations | 0.325 [0.315, 0.334]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l50.future_revoke_count` |
| C-PR (λ=0.5), drained owners | 0.254 [0.243, 0.265]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l50.future_drain_owners` |
| C-PR (λ=0.75), new approval pairs | 0.249 [0.238, 0.260]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l75.future_new_approvers` |
| C-PR (λ=0.75), new transfer senders | 0.253 [0.242, 0.265]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l75.future_new_transfer_senders` |
| C-PR (λ=0.75), revocations | 0.326 [0.315, 0.335]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l75.future_revoke_count` |
| C-PR (λ=0.75), drained owners | 0.252 [0.241, 0.263]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l75.future_drain_owners` |
| S-PR, new approval pairs | 0.172 [0.157, 0.185]; B=400 | `holdout-w0/eval_summary.json` : `taus.spr.future_new_approvers` |
| S-PR, new transfer senders | 0.295 [0.284, 0.305]; B=400 | `holdout-w0/eval_summary.json` : `taus.spr.future_new_transfer_senders` |
| S-PR, revocations | 0.225 [0.210, 0.239]; B=400 | `holdout-w0/eval_summary.json` : `taus.spr.future_revoke_count` |
| S-PR, drained owners | 0.171 [0.156, 0.185]; B=400 | `holdout-w0/eval_summary.json` : `taus.spr.future_drain_owners` |
| in-approve degree at t1, new approval pairs | 0.250 [0.237, 0.262]; B=400 | `holdout-w0/eval_summary.json` : `taus.t1_in_approve_degree.future_new_approvers` |
| in-approve degree at t1, new transfer senders | 0.180 [0.169, 0.192]; B=400 | `holdout-w0/eval_summary.json` : `taus.t1_in_approve_degree.future_new_transfer_senders` |
| in-approve degree at t1, revocations | 0.388 [0.376, 0.398]; B=400 | `holdout-w0/eval_summary.json` : `taus.t1_in_approve_degree.future_revoke_count` |
| in-approve degree at t1, drained owners | 0.214 [0.200, 0.227]; B=400 | `holdout-w0/eval_summary.json` : `taus.t1_in_approve_degree.future_drain_owners` |
| transfer in-degree at t1, new approval pairs | 0.135 [0.121, 0.150]; B=400 | `holdout-w0/eval_summary.json` : `taus.t1_in_degree.future_new_approvers` |
| transfer in-degree at t1, new transfer senders | 0.303 [0.292, 0.315]; B=400 | `holdout-w0/eval_summary.json` : `taus.t1_in_degree.future_new_transfer_senders` |
| transfer in-degree at t1, revocations | 0.205 [0.189, 0.218]; B=400 | `holdout-w0/eval_summary.json` : `taus.t1_in_degree.future_revoke_count` |
| transfer in-degree at t1, drained owners | 0.112 [0.096, 0.126]; B=400 | `holdout-w0/eval_summary.json` : `taus.t1_in_degree.future_drain_owners` |

### W0 contrasts

| Quantity | Value | Source |
|---|---|---|
| [contrasts_prefixed] C-PR minus C-PR (l=1), new approval pairs | Δτ 0.029 [0.022, 0.036]; τa 0.252, τb 0.223; P(Δτ>0) 1.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_prefixed[0]` |
| [contrasts_prefixed] C-PR minus C-PR (l=0), new transfer senders | Δτ -0.034 [-0.040, -0.029]; τa 0.262, τb 0.296; P(Δτ>0) 0.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_prefixed[1]` |
| [contrasts_after] C-PR (l=1) minus t1 in-approve degree, new approval pairs | Δτ -0.027 [-0.034, -0.019]; τa 0.223, τb 0.250; P(Δτ>0) 0.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_after[0]` |
| [contrasts_after] S-PR minus C-PR (l=1), new approval pairs | Δτ -0.051 [-0.066, -0.038]; τa 0.172, τb 0.223; P(Δτ>0) 0.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_after[1]` |
| [contrasts_after] S-PR minus C-PR (l=0), new transfer senders | Δτ -0.001 [-0.004, 0.002]; τa 0.295, τb 0.296; P(Δτ>0) 0.265; B=400 | `holdout-w0/eval_summary.json` : `contrasts_after[2]` |
| [contrasts_after] EndorseRank minus t1 in-approve degree, new approval pairs | Δτ -0.019 [-0.026, -0.011]; τa 0.231, τb 0.250; P(Δτ>0) 0.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_after[3]` |
| [contrasts_after] AWP minus t1 in-degree, new transfer senders | Δτ 0.043 [0.038, 0.048]; τa 0.346, τb 0.303; P(Δτ>0) 1.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_after[4]` |
| [contrasts_after] C-PR minus C-PR (l=0), new approval pairs | Δτ 0.092 [0.080, 0.105]; τa 0.252, τb 0.160; P(Δτ>0) 1.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_after[5]` |
| [contrasts_after] C-PR minus EndorseRank, new approval pairs | Δτ 0.021 [0.013, 0.028]; τa 0.252, τb 0.231; P(Δτ>0) 1.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_after[6]` |
| [contrasts_after] C-PR minus AWP, new transfer senders | Δτ -0.085 [-0.092, -0.078]; τa 0.262, τb 0.346; P(Δτ>0) 0.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_after[7]` |
| [contrasts_after] C-PR minus AWP, new approval pairs | Δτ 0.056 [0.042, 0.070]; τa 0.252, τb 0.196; P(Δτ>0) 1.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_after[8]` |
| [contrasts_after] EndorseRank minus AWP, new approval pairs | Δτ 0.035 [0.019, 0.051]; τa 0.231, τb 0.196; P(Δτ>0) 1.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_after[9]` |
| [contrasts_after] EndorseRank minus AWP, new transfer senders | Δτ -0.146 [-0.156, -0.136]; τa 0.200, τb 0.346; P(Δτ>0) 0.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_after[10]` |

### Rule A, primary part

| Quantity | Value | Source |
|---|---|---|
| Rule A primary: no worse on new approvals | yes | `holdout-w0/eval_summary.json` : `rule_a_primary.no_worse_on_new_approvals` |
| Rule A primary: better on new senders | no | `holdout-w0/eval_summary.json` : `rule_a_primary.better_on_new_senders` |
| Rule A primary: pass | no | `holdout-w0/eval_summary.json` : `rule_a_primary.pass` |

### Spenders that had received a transfer before t1

| Quantity | Value | Source |
|---|---|---|
| Receiving subset (contracts) | 14,094 | `holdout-w0/eval_summary.json` : `receiving.n` |
| Receiving: EndorseRank, new approval pairs | 0.236 [0.224, 0.249]; B=400 | `holdout-w0/eval_summary.json` : `receiving.taus.endorserank.future_new_approvers` |
| Receiving: EndorseRank, new transfer senders | 0.231 [0.219, 0.244]; B=400 | `holdout-w0/eval_summary.json` : `receiving.taus.endorserank.future_new_transfer_senders` |
| Receiving: AWP, new approval pairs | 0.298 [0.287, 0.308]; B=400 | `holdout-w0/eval_summary.json` : `receiving.taus.awp.future_new_approvers` |
| Receiving: AWP, new transfer senders | 0.357 [0.347, 0.367]; B=400 | `holdout-w0/eval_summary.json` : `receiving.taus.awp.future_new_transfer_senders` |
| Receiving: in-approve degree at t1, new approval pairs | 0.249 [0.237, 0.264]; B=400 | `holdout-w0/eval_summary.json` : `receiving.taus.t1_in_approve_degree.future_new_approvers` |
| Receiving: in-approve degree at t1, new transfer senders | 0.205 [0.193, 0.218]; B=400 | `holdout-w0/eval_summary.json` : `receiving.taus.t1_in_approve_degree.future_new_transfer_senders` |
| Receiving: transfer in-degree at t1, new approval pairs | 0.211 [0.196, 0.224]; B=400 | `holdout-w0/eval_summary.json` : `receiving.taus.t1_in_degree.future_new_approvers` |
| Receiving: transfer in-degree at t1, new transfer senders | 0.301 [0.289, 0.313]; B=400 | `holdout-w0/eval_summary.json` : `receiving.taus.t1_in_degree.future_new_transfer_senders` |
| Receiving: EndorseRank minus t1 in-approve degree, new approval pairs | Δτ -0.013 [-0.020, -0.006]; τa 0.236, τb 0.249; P(Δτ>0) 0.000; B=400 | `holdout-w0/eval_summary.json` : `receiving.contrasts[0]` |
| Receiving: AWP minus t1 in-degree, new transfer senders | Δτ 0.056 [0.049, 0.064]; τa 0.357, τb 0.301; P(Δτ>0) 1.000; B=400 | `holdout-w0/eval_summary.json` : `receiving.contrasts[1]` |

### Coverage (AWP = 0 means no transfer edge)

| Quantity | Value | Source |
|---|---|---|
| spenders without transfer edge | 2,891 | `holdout-w0/eval_summary.json` : `coverage.spenders_without_transfer_edge` |
| share gaining approvals without | 0.133 | `holdout-w0/eval_summary.json` : `coverage.share_gaining_approvals_without` |
| share gaining approvals with | 0.119 | `holdout-w0/eval_summary.json` : `coverage.share_gaining_approvals_with` |
| share gaining senders without | 0.006 | `holdout-w0/eval_summary.json` : `coverage.share_gaining_senders_without` |
| share gaining senders with | 0.119 | `holdout-w0/eval_summary.json` : `coverage.share_gaining_senders_with` |

### W0 traders (exploratory)

| Quantity | Value | Source |
|---|---|---|
| Traders (GMX V2 contract accounts, ≥3 closes) | 88 | `holdout-w0/eval_summary.json` : `traders.n` |
| Traders that had received an approval by t1 | 40 | `holdout-w0/eval_summary.json` : `traders.with_any_approval_received` |
| Traders: EndorseRank, profitable closes | 0.150 [-0.019, 0.295]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.endorserank.profitable_closes` |
| Traders: EndorseRank, realized gain | 0.078 [-0.094, 0.226]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.endorserank.realized_gain` |
| Traders: EndorseRank, profitable share | -0.055 [-0.196, 0.084]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.endorserank.profitable_share` |
| Traders: EndorseRank, non-loss share | -0.178 [-0.298, -0.042]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.endorserank.non_loss_share` |
| Traders: EndorseRank (activity restarts), profitable closes | 0.139 [-0.022, 0.278]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.endorserank_activity.profitable_closes` |
| Traders: EndorseRank (activity restarts), realized gain | 0.088 [-0.074, 0.234]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.endorserank_activity.realized_gain` |
| Traders: EndorseRank (activity restarts), profitable share | -0.078 [-0.220, 0.056]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.endorserank_activity.profitable_share` |
| Traders: EndorseRank (activity restarts), non-loss share | -0.199 [-0.319, -0.062]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.endorserank_activity.non_loss_share` |
| Traders: AWP, profitable closes | 0.155 [0.005, 0.297]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.awp.profitable_closes` |
| Traders: AWP, realized gain | 0.196 [0.048, 0.351]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.awp.realized_gain` |
| Traders: AWP, profitable share | -0.124 [-0.265, 0.015]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.awp.profitable_share` |
| Traders: AWP, non-loss share | -0.254 [-0.404, -0.104]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.awp.non_loss_share` |
| Traders: C-PR (λ=1), profitable closes | 0.083 [-0.072, 0.223]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l100.profitable_closes` |
| Traders: C-PR (λ=1), realized gain | 0.040 [-0.133, 0.190]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l100.realized_gain` |
| Traders: C-PR (λ=1), profitable share | -0.074 [-0.231, 0.068]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l100.profitable_share` |
| Traders: C-PR (λ=1), non-loss share | -0.188 [-0.322, -0.047]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l100.non_loss_share` |
| Traders: C-PR (λ=0), profitable closes | 0.150 [0.011, 0.272]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l0.profitable_closes` |
| Traders: C-PR (λ=0), realized gain | 0.288 [0.128, 0.438]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l0.realized_gain` |
| Traders: C-PR (λ=0), profitable share | -0.101 [-0.243, 0.045]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l0.profitable_share` |
| Traders: C-PR (λ=0), non-loss share | -0.225 [-0.359, -0.083]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l0.non_loss_share` |
| Traders: C-PR (λ=0.25), profitable closes | 0.152 [0.015, 0.274]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l25.profitable_closes` |
| Traders: C-PR (λ=0.25), realized gain | 0.294 [0.143, 0.424]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l25.realized_gain` |
| Traders: C-PR (λ=0.25), profitable share | -0.084 [-0.233, 0.069]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l25.profitable_share` |
| Traders: C-PR (λ=0.25), non-loss share | -0.210 [-0.352, -0.061]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l25.non_loss_share` |
| Traders: C-PR (λ=0.5), profitable closes | 0.160 [0.030, 0.284]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l50.profitable_closes` |
| Traders: C-PR (λ=0.5), realized gain | 0.283 [0.142, 0.410]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l50.realized_gain` |
| Traders: C-PR (λ=0.5), profitable share | -0.084 [-0.227, 0.058]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l50.profitable_share` |
| Traders: C-PR (λ=0.5), non-loss share | -0.208 [-0.346, -0.061]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l50.non_loss_share` |
| Traders: C-PR (λ=0.75), profitable closes | 0.155 [0.025, 0.279]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l75.profitable_closes` |
| Traders: C-PR (λ=0.75), realized gain | 0.270 [0.127, 0.398]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l75.realized_gain` |
| Traders: C-PR (λ=0.75), profitable share | -0.082 [-0.221, 0.063]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l75.profitable_share` |
| Traders: C-PR (λ=0.75), non-loss share | -0.203 [-0.341, -0.059]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l75.non_loss_share` |
| Traders: S-PR, profitable closes | 0.166 [0.023, 0.290]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.spr.profitable_closes` |
| Traders: S-PR, realized gain | 0.301 [0.147, 0.436]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.spr.realized_gain` |
| Traders: S-PR, profitable share | -0.075 [-0.221, 0.072]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.spr.profitable_share` |
| Traders: S-PR, non-loss share | -0.221 [-0.365, -0.078]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.spr.non_loss_share` |
| Traders: in-approve degree at t1, profitable closes | 0.083 [-0.103, 0.238]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.t1_in_approve_degree.profitable_closes` |
| Traders: in-approve degree at t1, realized gain | 0.024 [-0.154, 0.202]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.t1_in_approve_degree.realized_gain` |
| Traders: in-approve degree at t1, profitable share | -0.146 [-0.317, 0.029]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.t1_in_approve_degree.profitable_share` |
| Traders: in-approve degree at t1, non-loss share | -0.278 [-0.431, -0.119]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.t1_in_approve_degree.non_loss_share` |
| Traders: transfer in-degree at t1, profitable closes | 0.008 [-0.135, 0.169]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.t1_in_degree.profitable_closes` |
| Traders: transfer in-degree at t1, realized gain | 0.008 [-0.149, 0.175]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.t1_in_degree.realized_gain` |
| Traders: transfer in-degree at t1, profitable share | -0.191 [-0.329, -0.041]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.t1_in_degree.profitable_share` |
| Traders: transfer in-degree at t1, non-loss share | -0.197 [-0.350, -0.035]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.t1_in_degree.non_loss_share` |

## 7. Window W1 (scores at T_obs, labels July to September 2026; the rules registered for the raw-unit analysis, applied to the revised scores)

| Quantity | Value | Source |
|---|---|---|
| Margin δ | 0.010 | `window-w1/eval_summary.json` : `delta` |
| Spender cohort (contracts) | 18,152 | `window-w1/eval_summary.json` : `spenders` |
| Gained a new approval pair | 1,616 | `window-w1/eval_summary.json` : `gained_new_approvals` |
| Gained a new transfer sender | 1,533 | `window-w1/eval_summary.json` : `gained_new_senders` |
| Traders (GMX V2 contract accounts, ≥3 closes) | 70 | `window-w1/eval_summary.json` : `traders` |
| Traders with at least one liquidation | 9 | `window-w1/eval_summary.json` : `traders_liquidated` |
| Traders whose every close was a liquidation | 1 | `window-w1/eval_summary.json` : `traders_all_liquidated` |

### Rule B (comparator C-PR λ=0)

| Quantity | Value | Source |
|---|---|---|
| Rule B (comparator C-PR λ=0): F1 | Δτ 0.110 [0.098, 0.122]; τa 0.250, τb 0.141; P(Δτ>0) 1.000; B=400; superiority: holds | `window-w1/eval_summary.json` : `rule_b.F1` |
| Rule B (comparator C-PR λ=0): F2 | Δτ -0.028 [-0.033, -0.023]; τa 0.263, τb 0.291; P(Δτ>0) 0.000; B=400; non_inferiority: fails | `window-w1/eval_summary.json` : `rule_b.F2` |
| Rule B (comparator C-PR λ=0): F3 | Δτ 0.000 [-0.014, 0.010]; τa 0.350, τb 0.350; P(Δτ>0) 0.422; B=400; non_inferiority: fails | `window-w1/eval_summary.json` : `rule_b.F3` |
| Rule B (comparator C-PR λ=0): F4 | Δτ 0.000 [-0.014, 0.010]; τa 0.350, τb 0.350; P(Δτ>0) 0.422; B=400; superiority: fails | `window-w1/eval_summary.json` : `rule_b.F4` |
| Rule B (comparator C-PR λ=0): decision | no | `window-w1/eval_summary.json` : `rule_b.decision` |
| Rule B (comparator C-PR λ=0): F5 | Δτ 0.049 [-0.055, 0.168]; τa 0.350, τb 0.301; P(Δτ>0) 0.830; B=400; superiority: fails | `window-w1/eval_summary.json` : `rule_b.F5` |
| Rule B (comparator C-PR λ=0): F6a | Δτ 0.022 [0.015, 0.029]; τa 0.250, τb 0.228; P(Δτ>0) 1.000; B=400; no_worse: holds | `window-w1/eval_summary.json` : `rule_b.F6a` |
| Rule B (comparator C-PR λ=0): F6b | Δτ -0.028 [-0.033, -0.023]; τa 0.263, τb 0.291; P(Δτ>0) 0.000; B=400; superiority: fails | `window-w1/eval_summary.json` : `rule_b.F6b` |
| Rule B (comparator C-PR λ=0): F6 | no | `window-w1/eval_summary.json` : `rule_b.F6` |

### Sensitivity 1 (comparator AWP)

| Quantity | Value | Source |
|---|---|---|
| Sensitivity 1 (comparator AWP): F1 | Δτ 0.081 [0.069, 0.095]; τa 0.250, τb 0.169; P(Δτ>0) 1.000; B=400; superiority: holds | `window-w1/eval_summary.json` : `sensitivity_awp.F1` |
| Sensitivity 1 (comparator AWP): F2 | Δτ -0.067 [-0.072, -0.061]; τa 0.263, τb 0.330; P(Δτ>0) 0.000; B=400; non_inferiority: fails | `window-w1/eval_summary.json` : `sensitivity_awp.F2` |
| Sensitivity 1 (comparator AWP): F3 | Δτ 0.021 [-0.019, 0.060]; τa 0.350, τb 0.329; P(Δτ>0) 0.860; B=400; non_inferiority: fails | `window-w1/eval_summary.json` : `sensitivity_awp.F3` |
| Sensitivity 1 (comparator AWP): F4 | Δτ 0.021 [-0.019, 0.060]; τa 0.350, τb 0.329; P(Δτ>0) 0.860; B=400; superiority: fails | `window-w1/eval_summary.json` : `sensitivity_awp.F4` |
| Sensitivity 1 (comparator AWP): decision | no | `window-w1/eval_summary.json` : `sensitivity_awp.decision` |

### Sensitivity 2 (isolated nodes)

| Quantity | Value | Source |
|---|---|---|
| Sensitivity 2 (isolated nodes): F1 | Δτ 0.109 [0.098, 0.121]; τa 0.250, τb 0.141; P(Δτ>0) 1.000; B=400; superiority: holds | `window-w1/eval_summary.json` : `sensitivity_isolated.F1` |
| Sensitivity 2 (isolated nodes): F2 | Δτ -0.028 [-0.033, -0.023]; τa 0.263, τb 0.291; P(Δτ>0) 0.000; B=400; non_inferiority: fails | `window-w1/eval_summary.json` : `sensitivity_isolated.F2` |
| Sensitivity 2 (isolated nodes): F3 | Δτ 0.000 [-0.014, 0.010]; τa 0.350, τb 0.350; P(Δτ>0) 0.422; B=400; non_inferiority: fails | `window-w1/eval_summary.json` : `sensitivity_isolated.F3` |
| Sensitivity 2 (isolated nodes): F4 | Δτ 0.000 [-0.014, 0.010]; τa 0.350, τb 0.350; P(Δτ>0) 0.422; B=400; superiority: fails | `window-w1/eval_summary.json` : `sensitivity_isolated.F4` |
| Sensitivity 2 (isolated nodes): decision | no | `window-w1/eval_summary.json` : `sensitivity_isolated.decision` |
| Sensitivity 2 (isolated nodes): F5 | Δτ 0.028 [-0.047, 0.094]; τa 0.350, τb 0.322; P(Δτ>0) 0.790; B=400; superiority: fails | `window-w1/eval_summary.json` : `sensitivity_isolated.F5` |
| Sensitivity 2 (isolated nodes): F6a | Δτ 0.022 [0.015, 0.029]; τa 0.250, τb 0.228; P(Δτ>0) 1.000; B=400; no_worse: holds | `window-w1/eval_summary.json` : `sensitivity_isolated.F6a` |
| Sensitivity 2 (isolated nodes): F6b | Δτ -0.028 [-0.033, -0.023]; τa 0.263, τb 0.291; P(Δτ>0) 0.000; B=400; superiority: fails | `window-w1/eval_summary.json` : `sensitivity_isolated.F6b` |
| Sensitivity 2 (isolated nodes): F6 | no | `window-w1/eval_summary.json` : `sensitivity_isolated.F6` |

### W1 spenders and traders: τ_b

| Quantity | Value | Source |
|---|---|---|
| Spenders: EndorseRank, new approval pairs | 0.234 [0.222, 0.244]; B=400 | `window-w1/eval_summary.json` : `spender_taus.endorserank.future_new_approvers` |
| Spenders: EndorseRank, new transfer senders | 0.194 [0.184, 0.205]; B=400 | `window-w1/eval_summary.json` : `spender_taus.endorserank.future_new_transfer_senders` |
| Spenders: EndorseRank (activity restarts), new approval pairs | 0.295 [0.285, 0.304]; B=400 | `window-w1/eval_summary.json` : `spender_taus.endorserank_activity.future_new_approvers` |
| Spenders: EndorseRank (activity restarts), new transfer senders | 0.242 [0.232, 0.253]; B=400 | `window-w1/eval_summary.json` : `spender_taus.endorserank_activity.future_new_transfer_senders` |
| Spenders: AWP, new approval pairs | 0.169 [0.157, 0.183]; B=400 | `window-w1/eval_summary.json` : `spender_taus.awp.future_new_approvers` |
| Spenders: AWP, new transfer senders | 0.330 [0.321, 0.340]; B=400 | `window-w1/eval_summary.json` : `spender_taus.awp.future_new_transfer_senders` |
| Spenders: C-PR (λ=1), new approval pairs | 0.228 [0.217, 0.238]; B=400 | `window-w1/eval_summary.json` : `spender_taus.cpr_l100.future_new_approvers` |
| Spenders: C-PR (λ=1), new transfer senders | 0.188 [0.178, 0.198]; B=400 | `window-w1/eval_summary.json` : `spender_taus.cpr_l100.future_new_transfer_senders` |
| Spenders: C-PR (λ=0), new approval pairs | 0.141 [0.129, 0.154]; B=400 | `window-w1/eval_summary.json` : `spender_taus.cpr_l0.future_new_approvers` |
| Spenders: C-PR (λ=0), new transfer senders | 0.291 [0.282, 0.301]; B=400 | `window-w1/eval_summary.json` : `spender_taus.cpr_l0.future_new_transfer_senders` |
| Spenders: C-PR (λ=0.25), new approval pairs | 0.251 [0.241, 0.260]; B=400 | `window-w1/eval_summary.json` : `spender_taus.cpr_l25.future_new_approvers` |
| Spenders: C-PR (λ=0.25), new transfer senders | 0.270 [0.260, 0.279]; B=400 | `window-w1/eval_summary.json` : `spender_taus.cpr_l25.future_new_transfer_senders` |
| Spenders: C-PR (λ=0.5), new approval pairs | 0.250 [0.240, 0.260]; B=400 | `window-w1/eval_summary.json` : `spender_taus.cpr_l50.future_new_approvers` |
| Spenders: C-PR (λ=0.5), new transfer senders | 0.263 [0.254, 0.273]; B=400 | `window-w1/eval_summary.json` : `spender_taus.cpr_l50.future_new_transfer_senders` |
| Spenders: C-PR (λ=0.75), new approval pairs | 0.249 [0.238, 0.259]; B=400 | `window-w1/eval_summary.json` : `spender_taus.cpr_l75.future_new_approvers` |
| Spenders: C-PR (λ=0.75), new transfer senders | 0.256 [0.246, 0.266]; B=400 | `window-w1/eval_summary.json` : `spender_taus.cpr_l75.future_new_transfer_senders` |
| Spenders: S-PR, new approval pairs | 0.155 [0.142, 0.168]; B=400 | `window-w1/eval_summary.json` : `spender_taus.spr.future_new_approvers` |
| Spenders: S-PR, new transfer senders | 0.291 [0.281, 0.301]; B=400 | `window-w1/eval_summary.json` : `spender_taus.spr.future_new_transfer_senders` |
| Spenders: in-approve degree at the freeze, new approval pairs | 0.268 [0.257, 0.279]; B=400 | `window-w1/eval_summary.json` : `spender_taus.in_approve_degree.future_new_approvers` |
| Spenders: in-approve degree at the freeze, new transfer senders | 0.205 [0.193, 0.215]; B=400 | `window-w1/eval_summary.json` : `spender_taus.in_approve_degree.future_new_transfer_senders` |
| Spenders: transfer in-degree at the freeze, new approval pairs | 0.131 [0.119, 0.143]; B=400 | `window-w1/eval_summary.json` : `spender_taus.in_degree.future_new_approvers` |
| Spenders: transfer in-degree at the freeze, new transfer senders | 0.308 [0.299, 0.319]; B=400 | `window-w1/eval_summary.json` : `spender_taus.in_degree.future_new_transfer_senders` |
| Traders: EndorseRank, liquidation-free close rate | 0.297 [0.174, 0.418]; B=400 | `window-w1/eval_summary.json` : `trader_taus.endorserank` |
| Traders: EndorseRank (activity restarts), liquidation-free close rate | 0.288 [0.161, 0.405]; B=400 | `window-w1/eval_summary.json` : `trader_taus.endorserank_activity` |
| Traders: AWP, liquidation-free close rate | 0.329 [0.215, 0.439]; B=400 | `window-w1/eval_summary.json` : `trader_taus.awp` |
| Traders: C-PR (λ=1), liquidation-free close rate | 0.301 [0.177, 0.425]; B=400 | `window-w1/eval_summary.json` : `trader_taus.cpr_l100` |
| Traders: C-PR (λ=0), liquidation-free close rate | 0.350 [0.236, 0.461]; B=400 | `window-w1/eval_summary.json` : `trader_taus.cpr_l0` |
| Traders: C-PR (λ=0.25), liquidation-free close rate | 0.349 [0.234, 0.459]; B=400 | `window-w1/eval_summary.json` : `trader_taus.cpr_l25` |
| Traders: C-PR (λ=0.5), liquidation-free close rate | 0.350 [0.236, 0.461]; B=400 | `window-w1/eval_summary.json` : `trader_taus.cpr_l50` |
| Traders: C-PR (λ=0.75), liquidation-free close rate | 0.347 [0.231, 0.462]; B=400 | `window-w1/eval_summary.json` : `trader_taus.cpr_l75` |
| Traders: S-PR, liquidation-free close rate | 0.374 [0.255, 0.498]; B=400 | `window-w1/eval_summary.json` : `trader_taus.spr` |
| Traders: in-approve degree at the freeze, liquidation-free close rate | 0.394 [0.261, 0.524]; B=400 | `window-w1/eval_summary.json` : `trader_taus.in_approve_degree` |
| Traders: transfer in-degree at the freeze, liquidation-free close rate | 0.310 [0.185, 0.416]; B=400 | `window-w1/eval_summary.json` : `trader_taus.in_degree` |

### EndorseRank results (not part of rule B)

| Quantity | Value | Source |
|---|---|---|
| endorserank minus degree appr | Δτ -0.034 [-0.038, -0.029]; τa 0.234, τb 0.268; P(Δτ>0) 0.000; B=400 | `window-w1/eval_summary.json` : `endorserank_results.endorserank_minus_degree_appr` |
| awp minus degree send | Δτ 0.022 [0.017, 0.027]; τa 0.330, τb 0.308; P(Δτ>0) 1.000; B=400 | `window-w1/eval_summary.json` : `endorserank_results.awp_minus_degree_send` |
| cpr minus endorserank appr | Δτ 0.016 [0.010, 0.024]; τa 0.250, τb 0.234; P(Δτ>0) 1.000; B=400 | `window-w1/eval_summary.json` : `endorserank_results.cpr_minus_endorserank_appr` |
| cpr minus endorserank liq | Δτ 0.053 [-0.051, 0.171]; τa 0.350, τb 0.297; P(Δτ>0) 0.845; B=400 | `window-w1/eval_summary.json` : `endorserank_results.cpr_minus_endorserank_liq` |

### Comparison on outcomes built from neither edge type: rules R1-R3

| Quantity | Value | Source |
|---|---|---|
| Rule R1 | does not hold | `window-w1/eval_summary.json` : `neutral_rules.R1` |
| Rule R2 | does not hold | `window-w1/eval_summary.json` : `neutral_rules.R2` |
| Rule R3 | holds | `window-w1/eval_summary.json` : `neutral_rules.R3` |

### Neutral labels, W1 (2,000 paired resamples)

| Quantity | Value | Source |
|---|---|---|
| W1 traders | 70 | `window-w1/eval_summary.json` : `neutral_w1.n` |
| W1 highest in-approve degree among traders | 1.000 | `window-w1/eval_summary.json` : `neutral_w1.max_in_approve_degree` |
| W1 P: in-approve degree minus transfer in-degree, liquidation-free close rate | Δτ 0.084 [-0.013, 0.176]; τa 0.394, τb 0.310; 97.5% [-0.026, 0.188]; P(Δτ>0) 0.958; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.P.liquidation_free_rate` |
| W1 P: in-approve degree minus transfer in-degree, no liquidation | Δτ 0.078 [-0.012, 0.166]; τa 0.407, τb 0.329; P(Δτ>0) 0.960; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.P.no_liquidation` |
| W1 P: in-approve degree minus transfer in-degree, profitable closes | Δτ -0.143 [-0.318, 0.013]; τa 0.042, τb 0.185; P(Δτ>0) 0.040; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.P.profitable_closes` |
| W1 P: in-approve degree minus transfer in-degree, realized gain | Δτ -0.135 [-0.308, 0.025]; τa 0.033, τb 0.168; P(Δτ>0) 0.054; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.P.realized_gain` |
| W1 P: in-approve degree minus transfer in-degree, profitable share | Δτ -0.196 [-0.364, -0.046]; τa -0.221, τb -0.025; P(Δτ>0) 0.005; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.P.profitable_share` |
| W1 P: in-approve degree minus transfer in-degree, non-loss share | Δτ -0.252 [-0.391, -0.120]; τa -0.294, τb -0.042; P(Δτ>0) 0.000; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.P.non_loss_share` |
| W1 Q: EndorseRank (activity restarts) minus AWP, liquidation-free close rate | Δτ -0.041 [-0.135, 0.050]; τa 0.288, τb 0.329; 97.5% [-0.148, 0.064]; P(Δτ>0) 0.203; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.Q.liquidation_free_rate` |
| W1 Q: EndorseRank (activity restarts) minus AWP, no liquidation | Δτ -0.039 [-0.138, 0.062]; τa 0.294, τb 0.333; P(Δτ>0) 0.224; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.Q.no_liquidation` |
| W1 Q: EndorseRank (activity restarts) minus AWP, profitable closes | Δτ -0.231 [-0.429, -0.027]; τa 0.057, τb 0.288; P(Δτ>0) 0.013; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.Q.profitable_closes` |
| W1 Q: EndorseRank (activity restarts) minus AWP, realized gain | Δτ -0.350 [-0.536, -0.157]; τa -0.004, τb 0.346; P(Δτ>0) 0.002; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.Q.realized_gain` |
| W1 Q: EndorseRank (activity restarts) minus AWP, profitable share | Δτ -0.336 [-0.523, -0.141]; τa -0.199, τb 0.136; P(Δτ>0) 0.001; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.Q.profitable_share` |
| W1 Q: EndorseRank (activity restarts) minus AWP, non-loss share | Δτ -0.350 [-0.526, -0.175]; τa -0.269, τb 0.082; P(Δτ>0) 0.000; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.Q.non_loss_share` |
| W1 C-PR (λ=1) minus C-PR (λ=0), liquidation-free close rate | Δτ -0.049 [-0.169, 0.060]; τa 0.301, τb 0.350; P(Δτ>0) 0.205; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.layers.liquidation_free_rate` |
| W1 C-PR (λ=1) minus C-PR (λ=0), no liquidation | Δτ -0.051 [-0.170, 0.064]; τa 0.307, τb 0.358; P(Δτ>0) 0.202; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.layers.no_liquidation` |
| W1 C-PR (λ=1) minus C-PR (λ=0), profitable closes | Δτ -0.190 [-0.411, 0.037]; τa 0.010, τb 0.199; P(Δτ>0) 0.046; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.layers.profitable_closes` |
| W1 C-PR (λ=1) minus C-PR (λ=0), realized gain | Δτ -0.404 [-0.624, -0.182]; τa -0.066, τb 0.338; P(Δτ>0) 0.0005; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.layers.realized_gain` |
| W1 C-PR (λ=1) minus C-PR (λ=0), profitable share | Δτ -0.344 [-0.551, -0.120]; τa -0.208, τb 0.136; P(Δτ>0) 0.0005; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.layers.profitable_share` |
| W1 C-PR (λ=1) minus C-PR (λ=0), non-loss share | Δτ -0.324 [-0.531, -0.109]; τa -0.287, τb 0.038; P(Δτ>0) 0.002; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.layers.non_loss_share` |
| W1 EndorseRank minus AWP, liquidation-free close rate | Δτ -0.032 [-0.133, 0.066]; τa 0.297, τb 0.329; P(Δτ>0) 0.279; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.er_awp.liquidation_free_rate` |
| W1 EndorseRank minus AWP, no liquidation | Δτ -0.029 [-0.136, 0.080]; τa 0.303, τb 0.333; P(Δτ>0) 0.294; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.er_awp.no_liquidation` |
| W1 EndorseRank minus AWP, profitable closes | Δτ -0.214 [-0.423, -0.012]; τa 0.073, τb 0.288; P(Δτ>0) 0.019; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.er_awp.profitable_closes` |
| W1 EndorseRank minus AWP, realized gain | Δτ -0.346 [-0.547, -0.144]; τa 0.000, τb 0.346; P(Δτ>0) 0.001; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.er_awp.realized_gain` |
| W1 EndorseRank minus AWP, profitable share | Δτ -0.316 [-0.517, -0.112]; τa -0.180, τb 0.136; P(Δτ>0) 0.0005; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.er_awp.profitable_share` |
| W1 EndorseRank minus AWP, non-loss share | Δτ -0.346 [-0.526, -0.161]; τa -0.264, τb 0.082; P(Δτ>0) 0.000; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.er_awp.non_loss_share` |
| W1 C-PR (λ=0) minus AWP, liquidation-free close rate | Δτ 0.021 [-0.016, 0.065]; τa 0.350, τb 0.329; P(Δτ>0) 0.875; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.cpr0_awp.liquidation_free_rate` |
| W1 C-PR (λ=0) minus AWP, no liquidation | Δτ 0.026 [-0.012, 0.073]; τa 0.358, τb 0.333; P(Δτ>0) 0.903; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.cpr0_awp.no_liquidation` |
| W1 C-PR (λ=0) minus AWP, profitable closes | Δτ -0.088 [-0.148, -0.030]; τa 0.199, τb 0.288; P(Δτ>0) 0.002; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.cpr0_awp.profitable_closes` |
| W1 C-PR (λ=0) minus AWP, realized gain | Δτ -0.008 [-0.072, 0.061]; τa 0.338, τb 0.346; P(Δτ>0) 0.395; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.cpr0_awp.realized_gain` |
| W1 C-PR (λ=0) minus AWP, profitable share | Δτ -0.000668 [-0.058, 0.060]; τa 0.136, τb 0.136; P(Δτ>0) 0.495; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.cpr0_awp.profitable_share` |
| W1 C-PR (λ=0) minus AWP, non-loss share | Δτ -0.044 [-0.102, 0.012]; τa 0.038, τb 0.082; P(Δτ>0) 0.067; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.cpr0_awp.non_loss_share` |
| W1 EndorseRank minus in-approve degree, liquidation-free close rate | Δτ -0.097 [-0.174, -0.009]; τa 0.297, τb 0.394; P(Δτ>0) 0.016; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.er_degree.liquidation_free_rate` |
| W1 EndorseRank minus in-approve degree, no liquidation | Δτ -0.103 [-0.180, -0.012]; τa 0.303, τb 0.407; P(Δτ>0) 0.011; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.er_degree.no_liquidation` |
| W1 EndorseRank minus in-approve degree, profitable closes | Δτ 0.031 [-0.066, 0.127]; τa 0.073, τb 0.042; P(Δτ>0) 0.743; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.er_degree.profitable_closes` |
| W1 EndorseRank minus in-approve degree, realized gain | Δτ -0.033 [-0.128, 0.069]; τa 0.000, τb 0.033; P(Δτ>0) 0.258; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.er_degree.realized_gain` |
| W1 EndorseRank minus in-approve degree, profitable share | Δτ 0.042 [-0.062, 0.142]; τa -0.180, τb -0.221; P(Δτ>0) 0.790; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.er_degree.profitable_share` |
| W1 EndorseRank minus in-approve degree, non-loss share | Δτ 0.029 [-0.072, 0.130]; τa -0.264, τb -0.294; P(Δτ>0) 0.733; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.grid.er_degree.non_loss_share` |
| W1 P: in-approve degree minus transfer in-degree, stratified by closes | Δτ 0.101 [-0.024, 0.231]; τa 0.381, τb 0.280 | `window-w1/eval_summary.json` : `neutral_w1.stratified.P` |
| W1 Q: EndorseRank (activity restarts) minus AWP, stratified by closes | Δτ -0.028 [-0.207, 0.098]; τa 0.273, τb 0.301 | `window-w1/eval_summary.json` : `neutral_w1.stratified.Q` |
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
| W1 P without the ten recipients of highest in-approve degree | Δτ 0.073 [-0.039, 0.186]; τa 0.366, τb 0.292; P(Δτ>0) 0.895; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.influence_without_top10` |
| W1 EndorseRank, liquidation-free close rate | 0.297 [0.171, 0.410]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.endorserank.liquidation_free_rate` |
| W1 EndorseRank, no liquidation | 0.303 [0.172, 0.422]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.endorserank.no_liquidation` |
| W1 EndorseRank, profitable closes | 0.073 [-0.115, 0.260]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.endorserank.profitable_closes` |
| W1 EndorseRank, realized gain | 0.000 [-0.198, 0.200]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.endorserank.realized_gain` |
| W1 EndorseRank, profitable share | -0.180 [-0.340, -0.012]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.endorserank.profitable_share` |
| W1 EndorseRank, non-loss share | -0.264 [-0.408, -0.106]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.endorserank.non_loss_share` |
| W1 EndorseRank (activity restarts), liquidation-free close rate | 0.288 [0.157, 0.404]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.endorserank_activity.liquidation_free_rate` |
| W1 EndorseRank (activity restarts), no liquidation | 0.294 [0.158, 0.417]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.endorserank_activity.no_liquidation` |
| W1 EndorseRank (activity restarts), profitable closes | 0.057 [-0.123, 0.239]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.endorserank_activity.profitable_closes` |
| W1 EndorseRank (activity restarts), realized gain | -0.004 [-0.179, 0.181]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.endorserank_activity.realized_gain` |
| W1 EndorseRank (activity restarts), profitable share | -0.199 [-0.346, -0.039]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.endorserank_activity.profitable_share` |
| W1 EndorseRank (activity restarts), non-loss share | -0.269 [-0.412, -0.118]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.endorserank_activity.non_loss_share` |
| W1 AWP, liquidation-free close rate | 0.329 [0.207, 0.440]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.awp.liquidation_free_rate` |
| W1 AWP, no liquidation | 0.333 [0.207, 0.447]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.awp.no_liquidation` |
| W1 AWP, profitable closes | 0.288 [0.125, 0.442]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.awp.profitable_closes` |
| W1 AWP, realized gain | 0.346 [0.189, 0.490]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.awp.realized_gain` |
| W1 AWP, profitable share | 0.136 [-0.039, 0.300]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.awp.profitable_share` |
| W1 AWP, non-loss share | 0.082 [-0.077, 0.247]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.awp.non_loss_share` |
| W1 C-PR (λ=1), liquidation-free close rate | 0.301 [0.174, 0.419]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l100.liquidation_free_rate` |
| W1 C-PR (λ=1), no liquidation | 0.307 [0.174, 0.428]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l100.no_liquidation` |
| W1 C-PR (λ=1), profitable closes | 0.010 [-0.167, 0.192]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l100.profitable_closes` |
| W1 C-PR (λ=1), realized gain | -0.066 [-0.249, 0.121]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l100.realized_gain` |
| W1 C-PR (λ=1), profitable share | -0.208 [-0.370, -0.030]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l100.profitable_share` |
| W1 C-PR (λ=1), non-loss share | -0.287 [-0.443, -0.121]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l100.non_loss_share` |
| W1 C-PR (λ=0), liquidation-free close rate | 0.350 [0.226, 0.461]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l0.liquidation_free_rate` |
| W1 C-PR (λ=0), no liquidation | 0.358 [0.228, 0.475]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l0.no_liquidation` |
| W1 C-PR (λ=0), profitable closes | 0.199 [0.043, 0.355]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l0.profitable_closes` |
| W1 C-PR (λ=0), realized gain | 0.338 [0.178, 0.485]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l0.realized_gain` |
| W1 C-PR (λ=0), profitable share | 0.136 [-0.034, 0.290]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l0.profitable_share` |
| W1 C-PR (λ=0), non-loss share | 0.038 [-0.127, 0.201]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l0.non_loss_share` |
| W1 C-PR (λ=0.25), liquidation-free close rate | 0.349 [0.225, 0.461]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l25.liquidation_free_rate` |
| W1 C-PR (λ=0.25), no liquidation | 0.357 [0.227, 0.474]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l25.no_liquidation` |
| W1 C-PR (λ=0.25), profitable closes | 0.155 [0.002, 0.305]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l25.profitable_closes` |
| W1 C-PR (λ=0.25), realized gain | 0.284 [0.122, 0.435]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l25.realized_gain` |
| W1 C-PR (λ=0.25), profitable share | 0.090 [-0.075, 0.242]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l25.profitable_share` |
| W1 C-PR (λ=0.25), non-loss share | -0.011 [-0.173, 0.148]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l25.non_loss_share` |
| W1 C-PR (λ=0.5), liquidation-free close rate | 0.350 [0.225, 0.466]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l50.liquidation_free_rate` |
| W1 C-PR (λ=0.5), no liquidation | 0.358 [0.229, 0.475]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l50.no_liquidation` |
| W1 C-PR (λ=0.5), profitable closes | 0.114 [-0.044, 0.267]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l50.profitable_closes` |
| W1 C-PR (λ=0.5), realized gain | 0.240 [0.075, 0.397]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l50.realized_gain` |
| W1 C-PR (λ=0.5), profitable share | 0.053 [-0.115, 0.212]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l50.profitable_share` |
| W1 C-PR (λ=0.5), non-loss share | -0.053 [-0.217, 0.103]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l50.non_loss_share` |
| W1 C-PR (λ=0.75), liquidation-free close rate | 0.347 [0.224, 0.465]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l75.liquidation_free_rate` |
| W1 C-PR (λ=0.75), no liquidation | 0.353 [0.226, 0.472]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l75.no_liquidation` |
| W1 C-PR (λ=0.75), profitable closes | 0.081 [-0.078, 0.244]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l75.profitable_closes` |
| W1 C-PR (λ=0.75), realized gain | 0.201 [0.023, 0.368]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l75.realized_gain` |
| W1 C-PR (λ=0.75), profitable share | 0.016 [-0.153, 0.182]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l75.profitable_share` |
| W1 C-PR (λ=0.75), non-loss share | -0.090 [-0.256, 0.072]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.cpr_l75.non_loss_share` |
| W1 S-PR, liquidation-free close rate | 0.374 [0.247, 0.482]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.spr.liquidation_free_rate` |
| W1 S-PR, no liquidation | 0.381 [0.248, 0.495]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.spr.no_liquidation` |
| W1 S-PR, profitable closes | 0.167 [0.018, 0.312]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.spr.profitable_closes` |
| W1 S-PR, realized gain | 0.286 [0.122, 0.441]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.spr.realized_gain` |
| W1 S-PR, profitable share | 0.100 [-0.048, 0.244]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.spr.profitable_share` |
| W1 S-PR, non-loss share | -0.011 [-0.164, 0.151]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.spr.non_loss_share` |
| W1 in-approve degree at the freeze, liquidation-free close rate | 0.394 [0.265, 0.518]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.in_approve_degree.liquidation_free_rate` |
| W1 in-approve degree at the freeze, no liquidation | 0.407 [0.268, 0.541]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.in_approve_degree.no_liquidation` |
| W1 in-approve degree at the freeze, profitable closes | 0.042 [-0.158, 0.243]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.in_approve_degree.profitable_closes` |
| W1 in-approve degree at the freeze, realized gain | 0.033 [-0.164, 0.230]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.in_approve_degree.realized_gain` |
| W1 in-approve degree at the freeze, profitable share | -0.221 [-0.406, -0.034]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.in_approve_degree.profitable_share` |
| W1 in-approve degree at the freeze, non-loss share | -0.294 [-0.468, -0.106]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.in_approve_degree.non_loss_share` |
| W1 transfer in-degree at the freeze, liquidation-free close rate | 0.310 [0.184, 0.425]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.in_degree.liquidation_free_rate` |
| W1 transfer in-degree at the freeze, no liquidation | 0.329 [0.189, 0.451]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.in_degree.no_liquidation` |
| W1 transfer in-degree at the freeze, profitable closes | 0.185 [0.014, 0.341]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.in_degree.profitable_closes` |
| W1 transfer in-degree at the freeze, realized gain | 0.168 [0.028, 0.291]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.in_degree.realized_gain` |
| W1 transfer in-degree at the freeze, profitable share | -0.025 [-0.194, 0.131]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.in_degree.profitable_share` |
| W1 transfer in-degree at the freeze, non-loss share | -0.042 [-0.203, 0.114]; B=2000 | `window-w1/eval_summary.json` : `neutral_w1.taus.in_degree.non_loss_share` |

### Neutral labels, W0 (2,000 paired resamples)

| Quantity | Value | Source |
|---|---|---|
| W0 traders | 88 | `window-w1/eval_summary.json` : `neutral_w0.n` |
| W0 highest in-approve degree among traders | 3.000 | `window-w1/eval_summary.json` : `neutral_w0.max_in_approve_degree` |
| W0 P: in-approve degree minus transfer in-degree, liquidation-free close rate | Δτ 0.182 [0.052, 0.314]; τa 0.344, τb 0.161; 97.5% [0.032, 0.338]; P(Δτ>0) 0.997; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.P.liquidation_free_rate` |
| W0 P: in-approve degree minus transfer in-degree, no liquidation | Δτ 0.197 [0.059, 0.333]; τa 0.356, τb 0.159; P(Δτ>0) 0.997; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.P.no_liquidation` |
| W0 P: in-approve degree minus transfer in-degree, profitable closes | Δτ 0.075 [-0.080, 0.222]; τa 0.083, τb 0.008; P(Δτ>0) 0.827; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.P.profitable_closes` |
| W0 P: in-approve degree minus transfer in-degree, realized gain | Δτ 0.017 [-0.150, 0.176]; τa 0.024, τb 0.008; P(Δτ>0) 0.559; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.P.realized_gain` |
| W0 P: in-approve degree minus transfer in-degree, profitable share | Δτ 0.045 [-0.113, 0.184]; τa -0.146, τb -0.191; P(Δτ>0) 0.735; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.P.profitable_share` |
| W0 P: in-approve degree minus transfer in-degree, non-loss share | Δτ -0.080 [-0.228, 0.058]; τa -0.278, τb -0.197; P(Δτ>0) 0.137; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.P.non_loss_share` |
| W0 Q: EndorseRank (activity restarts) minus AWP, liquidation-free close rate | Δτ -0.014 [-0.147, 0.130]; τa 0.227, τb 0.240; 97.5% [-0.161, 0.151]; P(Δτ>0) 0.407; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.Q.liquidation_free_rate` |
| W0 Q: EndorseRank (activity restarts) minus AWP, no liquidation | Δτ -0.010 [-0.152, 0.146]; τa 0.217, τb 0.227; P(Δτ>0) 0.432; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.Q.no_liquidation` |
| W0 Q: EndorseRank (activity restarts) minus AWP, profitable closes | Δτ -0.016 [-0.150, 0.118]; τa 0.139, τb 0.155; P(Δτ>0) 0.426; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.Q.profitable_closes` |
| W0 Q: EndorseRank (activity restarts) minus AWP, realized gain | Δτ -0.107 [-0.252, 0.044]; τa 0.088, τb 0.196; P(Δτ>0) 0.081; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.Q.realized_gain` |
| W0 Q: EndorseRank (activity restarts) minus AWP, profitable share | Δτ 0.046 [-0.071, 0.172]; τa -0.078, τb -0.124; P(Δτ>0) 0.778; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.Q.profitable_share` |
| W0 Q: EndorseRank (activity restarts) minus AWP, non-loss share | Δτ 0.055 [-0.070, 0.192]; τa -0.199, τb -0.254; P(Δτ>0) 0.799; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.Q.non_loss_share` |
| W0 C-PR (λ=1) minus C-PR (λ=0), liquidation-free close rate | Δτ -0.041 [-0.187, 0.105]; τa 0.225, τb 0.265; P(Δτ>0) 0.278; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.layers.liquidation_free_rate` |
| W0 C-PR (λ=1) minus C-PR (λ=0), no liquidation | Δτ -0.051 [-0.198, 0.102]; τa 0.216, τb 0.267; P(Δτ>0) 0.249; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.layers.no_liquidation` |
| W0 C-PR (λ=1) minus C-PR (λ=0), profitable closes | Δτ -0.067 [-0.222, 0.087]; τa 0.083, τb 0.150; P(Δτ>0) 0.204; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.layers.profitable_closes` |
| W0 C-PR (λ=1) minus C-PR (λ=0), realized gain | Δτ -0.248 [-0.433, -0.067]; τa 0.040, τb 0.288; P(Δτ>0) 0.002; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.layers.realized_gain` |
| W0 C-PR (λ=1) minus C-PR (λ=0), profitable share | Δτ 0.027 [-0.112, 0.181]; τa -0.074, τb -0.101; P(Δτ>0) 0.647; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.layers.profitable_share` |
| W0 C-PR (λ=1) minus C-PR (λ=0), non-loss share | Δτ 0.037 [-0.111, 0.189]; τa -0.188, τb -0.225; P(Δτ>0) 0.702; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.layers.non_loss_share` |
| W0 EndorseRank minus AWP, liquidation-free close rate | Δτ -0.017 [-0.156, 0.128]; τa 0.224, τb 0.240; P(Δτ>0) 0.394; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.er_awp.liquidation_free_rate` |
| W0 EndorseRank minus AWP, no liquidation | Δτ -0.012 [-0.154, 0.137]; τa 0.215, τb 0.227; P(Δτ>0) 0.424; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.er_awp.no_liquidation` |
| W0 EndorseRank minus AWP, profitable closes | Δτ -0.005 [-0.163, 0.155]; τa 0.150, τb 0.155; P(Δτ>0) 0.493; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.er_awp.profitable_closes` |
| W0 EndorseRank minus AWP, realized gain | Δτ -0.118 [-0.286, 0.046]; τa 0.078, τb 0.196; P(Δτ>0) 0.080; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.er_awp.realized_gain` |
| W0 EndorseRank minus AWP, profitable share | Δτ 0.069 [-0.060, 0.208]; τa -0.055, τb -0.124; P(Δτ>0) 0.857; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.er_awp.profitable_share` |
| W0 EndorseRank minus AWP, non-loss share | Δτ 0.076 [-0.063, 0.223]; τa -0.178, τb -0.254; P(Δτ>0) 0.869; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.er_awp.non_loss_share` |
| W0 C-PR (λ=0) minus AWP, liquidation-free close rate | Δτ 0.025 [-0.022, 0.077]; τa 0.265, τb 0.240; P(Δτ>0) 0.845; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.cpr0_awp.liquidation_free_rate` |
| W0 C-PR (λ=0) minus AWP, no liquidation | Δτ 0.040 [-0.005, 0.089]; τa 0.267, τb 0.227; P(Δτ>0) 0.957; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.cpr0_awp.no_liquidation` |
| W0 C-PR (λ=0) minus AWP, profitable closes | Δτ -0.005 [-0.068, 0.069]; τa 0.150, τb 0.155; P(Δτ>0) 0.400; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.cpr0_awp.profitable_closes` |
| W0 C-PR (λ=0) minus AWP, realized gain | Δτ 0.092 [0.013, 0.179]; τa 0.288, τb 0.196; P(Δτ>0) 0.989; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.cpr0_awp.realized_gain` |
| W0 C-PR (λ=0) minus AWP, profitable share | Δτ 0.022 [-0.048, 0.098]; τa -0.101, τb -0.124; P(Δτ>0) 0.735; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.cpr0_awp.profitable_share` |
| W0 C-PR (λ=0) minus AWP, non-loss share | Δτ 0.029 [-0.035, 0.098]; τa -0.225, τb -0.254; P(Δτ>0) 0.817; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.cpr0_awp.non_loss_share` |
| W0 EndorseRank minus in-approve degree, liquidation-free close rate | Δτ -0.120 [-0.203, -0.033]; τa 0.224, τb 0.344; P(Δτ>0) 0.004; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.er_degree.liquidation_free_rate` |
| W0 EndorseRank minus in-approve degree, no liquidation | Δτ -0.140 [-0.225, -0.051]; τa 0.215, τb 0.356; P(Δτ>0) 0.004; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.er_degree.no_liquidation` |
| W0 EndorseRank minus in-approve degree, profitable closes | Δτ 0.068 [-0.023, 0.150]; τa 0.150, τb 0.083; P(Δτ>0) 0.939; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.er_degree.profitable_closes` |
| W0 EndorseRank minus in-approve degree, realized gain | Δτ 0.053 [-0.034, 0.147]; τa 0.078, τb 0.024; P(Δτ>0) 0.881; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.er_degree.realized_gain` |
| W0 EndorseRank minus in-approve degree, profitable share | Δτ 0.091 [-0.003, 0.190]; τa -0.055, τb -0.146; P(Δτ>0) 0.971; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.er_degree.profitable_share` |
| W0 EndorseRank minus in-approve degree, non-loss share | Δτ 0.100 [0.009, 0.194]; τa -0.178, τb -0.278; P(Δτ>0) 0.985; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.grid.er_degree.non_loss_share` |
| W0 P: in-approve degree minus transfer in-degree, stratified by closes | Δτ 0.129 [0.020, 0.293]; τa 0.338, τb 0.209 | `window-w1/eval_summary.json` : `neutral_w0.stratified.P` |
| W0 Q: EndorseRank (activity restarts) minus AWP, stratified by closes | Δτ -0.037 [-0.173, 0.125]; τa 0.215, τb 0.252 | `window-w1/eval_summary.json` : `neutral_w0.stratified.Q` |
| W0 recipients: n | 40 | `window-w1/eval_summary.json` : `neutral_w0.recipients.recipients.n` |
| W0 recipients: share no liquidation | 1.000 | `window-w1/eval_summary.json` : `neutral_w0.recipients.recipients.share_no_liquidation` |
| W0 recipients: mean liquidation free rate | 1.000 | `window-w1/eval_summary.json` : `neutral_w0.recipients.recipients.mean_liquidation_free_rate` |
| W0 recipients: mean profitable share | 0.362 | `window-w1/eval_summary.json` : `neutral_w0.recipients.recipients.mean_profitable_share` |
| W0 recipients: mean non loss share | 0.402 | `window-w1/eval_summary.json` : `neutral_w0.recipients.recipients.mean_non_loss_share` |
| W0 recipients: median closes | 31.000 | `window-w1/eval_summary.json` : `neutral_w0.recipients.recipients.median_closes` |
| W0 others: n | 48 | `window-w1/eval_summary.json` : `neutral_w0.recipients.others.n` |
| W0 others: share no liquidation | 0.750 | `window-w1/eval_summary.json` : `neutral_w0.recipients.others.share_no_liquidation` |
| W0 others: mean liquidation free rate | 0.919 | `window-w1/eval_summary.json` : `neutral_w0.recipients.others.mean_liquidation_free_rate` |
| W0 others: mean profitable share | 0.474 | `window-w1/eval_summary.json` : `neutral_w0.recipients.others.mean_profitable_share` |
| W0 others: mean non loss share | 0.607 | `window-w1/eval_summary.json` : `neutral_w0.recipients.others.mean_non_loss_share` |
| W0 others: median closes | 10.000 | `window-w1/eval_summary.json` : `neutral_w0.recipients.others.median_closes` |
| W0 P without the ten recipients of highest in-approve degree | Δτ 0.188 [0.046, 0.331]; τa 0.324, τb 0.136; P(Δτ>0) 0.994; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.influence_without_top10` |
| W0 EndorseRank, liquidation-free close rate | 0.224 [0.105, 0.339]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.endorserank.liquidation_free_rate` |
| W0 EndorseRank, no liquidation | 0.215 [0.102, 0.329]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.endorserank.no_liquidation` |
| W0 EndorseRank, profitable closes | 0.150 [-0.017, 0.310]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.endorserank.profitable_closes` |
| W0 EndorseRank, realized gain | 0.078 [-0.084, 0.231]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.endorserank.realized_gain` |
| W0 EndorseRank, profitable share | -0.055 [-0.189, 0.084]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.endorserank.profitable_share` |
| W0 EndorseRank, non-loss share | -0.178 [-0.303, -0.045]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.endorserank.non_loss_share` |
| W0 EndorseRank (activity restarts), liquidation-free close rate | 0.227 [0.107, 0.344]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.endorserank_activity.liquidation_free_rate` |
| W0 EndorseRank (activity restarts), no liquidation | 0.217 [0.101, 0.333]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.endorserank_activity.no_liquidation` |
| W0 EndorseRank (activity restarts), profitable closes | 0.139 [-0.021, 0.288]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.endorserank_activity.profitable_closes` |
| W0 EndorseRank (activity restarts), realized gain | 0.088 [-0.069, 0.239]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.endorserank_activity.realized_gain` |
| W0 EndorseRank (activity restarts), profitable share | -0.078 [-0.216, 0.066]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.endorserank_activity.profitable_share` |
| W0 EndorseRank (activity restarts), non-loss share | -0.199 [-0.328, -0.060]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.endorserank_activity.non_loss_share` |
| W0 AWP, liquidation-free close rate | 0.240 [0.073, 0.380]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.awp.liquidation_free_rate` |
| W0 AWP, no liquidation | 0.227 [0.057, 0.370]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.awp.no_liquidation` |
| W0 AWP, profitable closes | 0.155 [0.005, 0.301]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.awp.profitable_closes` |
| W0 AWP, realized gain | 0.196 [0.040, 0.348]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.awp.realized_gain` |
| W0 AWP, profitable share | -0.124 [-0.271, 0.021]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.awp.profitable_share` |
| W0 AWP, non-loss share | -0.254 [-0.401, -0.109]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.awp.non_loss_share` |
| W0 C-PR (λ=1), liquidation-free close rate | 0.225 [0.106, 0.340]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l100.liquidation_free_rate` |
| W0 C-PR (λ=1), no liquidation | 0.216 [0.102, 0.331]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l100.no_liquidation` |
| W0 C-PR (λ=1), profitable closes | 0.083 [-0.075, 0.240]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l100.profitable_closes` |
| W0 C-PR (λ=1), realized gain | 0.040 [-0.124, 0.195]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l100.realized_gain` |
| W0 C-PR (λ=1), profitable share | -0.074 [-0.222, 0.075]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l100.profitable_share` |
| W0 C-PR (λ=1), non-loss share | -0.188 [-0.324, -0.048]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l100.non_loss_share` |
| W0 C-PR (λ=0), liquidation-free close rate | 0.265 [0.109, 0.391]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l0.liquidation_free_rate` |
| W0 C-PR (λ=0), no liquidation | 0.267 [0.101, 0.403]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l0.no_liquidation` |
| W0 C-PR (λ=0), profitable closes | 0.150 [0.008, 0.280]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l0.profitable_closes` |
| W0 C-PR (λ=0), realized gain | 0.288 [0.140, 0.426]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l0.realized_gain` |
| W0 C-PR (λ=0), profitable share | -0.101 [-0.247, 0.043]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l0.profitable_share` |
| W0 C-PR (λ=0), non-loss share | -0.225 [-0.370, -0.087]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l0.non_loss_share` |
| W0 C-PR (λ=0.25), liquidation-free close rate | 0.275 [0.112, 0.401]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l25.liquidation_free_rate` |
| W0 C-PR (λ=0.25), no liquidation | 0.277 [0.106, 0.414]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l25.no_liquidation` |
| W0 C-PR (λ=0.25), profitable closes | 0.152 [0.013, 0.280]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l25.profitable_closes` |
| W0 C-PR (λ=0.25), realized gain | 0.294 [0.151, 0.426]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l25.realized_gain` |
| W0 C-PR (λ=0.25), profitable share | -0.084 [-0.228, 0.061]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l25.profitable_share` |
| W0 C-PR (λ=0.25), non-loss share | -0.210 [-0.354, -0.070]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l25.non_loss_share` |
| W0 C-PR (λ=0.5), liquidation-free close rate | 0.274 [0.110, 0.401]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l50.liquidation_free_rate` |
| W0 C-PR (λ=0.5), no liquidation | 0.276 [0.105, 0.410]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l50.no_liquidation` |
| W0 C-PR (λ=0.5), profitable closes | 0.160 [0.021, 0.287]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l50.profitable_closes` |
| W0 C-PR (λ=0.5), realized gain | 0.283 [0.142, 0.412]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l50.realized_gain` |
| W0 C-PR (λ=0.5), profitable share | -0.084 [-0.227, 0.058]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l50.profitable_share` |
| W0 C-PR (λ=0.5), non-loss share | -0.208 [-0.351, -0.066]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l50.non_loss_share` |
| W0 C-PR (λ=0.75), liquidation-free close rate | 0.265 [0.098, 0.394]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l75.liquidation_free_rate` |
| W0 C-PR (λ=0.75), no liquidation | 0.267 [0.091, 0.403]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l75.no_liquidation` |
| W0 C-PR (λ=0.75), profitable closes | 0.155 [0.019, 0.280]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l75.profitable_closes` |
| W0 C-PR (λ=0.75), realized gain | 0.270 [0.130, 0.400]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l75.realized_gain` |
| W0 C-PR (λ=0.75), profitable share | -0.082 [-0.225, 0.060]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l75.profitable_share` |
| W0 C-PR (λ=0.75), non-loss share | -0.203 [-0.343, -0.059]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.cpr_l75.non_loss_share` |
| W0 S-PR, liquidation-free close rate | 0.292 [0.131, 0.427]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.spr.liquidation_free_rate` |
| W0 S-PR, no liquidation | 0.279 [0.118, 0.414]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.spr.no_liquidation` |
| W0 S-PR, profitable closes | 0.166 [0.019, 0.296]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.spr.profitable_closes` |
| W0 S-PR, realized gain | 0.301 [0.150, 0.436]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.spr.realized_gain` |
| W0 S-PR, profitable share | -0.075 [-0.221, 0.072]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.spr.profitable_share` |
| W0 S-PR, non-loss share | -0.221 [-0.367, -0.081]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.spr.non_loss_share` |
| W0 in-approve degree at the freeze, liquidation-free close rate | 0.344 [0.244, 0.440]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.in_approve_degree.liquidation_free_rate` |
| W0 in-approve degree at the freeze, no liquidation | 0.356 [0.248, 0.462]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.in_approve_degree.no_liquidation` |
| W0 in-approve degree at the freeze, profitable closes | 0.083 [-0.094, 0.259]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.in_approve_degree.profitable_closes` |
| W0 in-approve degree at the freeze, realized gain | 0.024 [-0.158, 0.207]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.in_approve_degree.realized_gain` |
| W0 in-approve degree at the freeze, profitable share | -0.146 [-0.317, 0.028]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.in_approve_degree.profitable_share` |
| W0 in-approve degree at the freeze, non-loss share | -0.278 [-0.425, -0.123]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.in_approve_degree.non_loss_share` |
| W0 transfer in-degree at the freeze, liquidation-free close rate | 0.161 [0.015, 0.299]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.in_degree.liquidation_free_rate` |
| W0 transfer in-degree at the freeze, no liquidation | 0.159 [0.013, 0.301]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.in_degree.no_liquidation` |
| W0 transfer in-degree at the freeze, profitable closes | 0.008 [-0.141, 0.167]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.in_degree.profitable_closes` |
| W0 transfer in-degree at the freeze, realized gain | 0.008 [-0.150, 0.170]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.in_degree.realized_gain` |
| W0 transfer in-degree at the freeze, profitable share | -0.191 [-0.334, -0.037]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.in_degree.profitable_share` |
| W0 transfer in-degree at the freeze, non-loss share | -0.197 [-0.358, -0.033]; B=2000 | `window-w1/eval_summary.json` : `neutral_w0.taus.in_degree.non_loss_share` |

### Supplementary spender contrasts (computed after the labels were known, outside every rule)

| Quantity | Value | Source |
|---|---|---|
| W0 EndorseRank (activity restarts) minus in-approve degree, new approval pairs | Δτ 0.059 [0.050, 0.067]; τa 0.308, τb 0.250; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w0.er_activity_minus_degree_appr` |
| W0 EndorseRank (activity restarts) minus EndorseRank, new approval pairs | Δτ 0.077 [0.071, 0.084]; τa 0.308, τb 0.231; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w0.er_activity_minus_er_appr` |
| W0 EndorseRank (activity restarts) minus EndorseRank, new transfer senders | Δτ 0.070 [0.064, 0.076]; τa 0.269, τb 0.200; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w0.er_activity_minus_er_send` |
| W0 EndorseRank minus AWP, new approval pairs | Δτ 0.035 [0.019, 0.051]; τa 0.231, τb 0.196; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w0.er_minus_awp_appr` |
| W0 EndorseRank minus AWP, new transfer senders | Δτ -0.146 [-0.156, -0.136]; τa 0.200, τb 0.346; P(Δτ>0) 0.000; B=400 | `supplementary/supplementary.json` : `w0.er_minus_awp_send` |
| W0 n | 17,050 | `supplementary/supplementary.json` : `w0.n` |
| W1 EndorseRank (activity restarts) minus in-approve degree, new approval pairs | Δτ 0.027 [0.021, 0.034]; τa 0.295, τb 0.268; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w1.er_activity_minus_degree_appr` |
| W1 EndorseRank (activity restarts) minus EndorseRank, new approval pairs | Δτ 0.061 [0.054, 0.067]; τa 0.295, τb 0.234; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w1.er_activity_minus_er_appr` |
| W1 EndorseRank (activity restarts) minus EndorseRank, new transfer senders | Δτ 0.048 [0.042, 0.053]; τa 0.242, τb 0.194; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w1.er_activity_minus_er_send` |
| W1 EndorseRank minus AWP, new approval pairs | Δτ 0.065 [0.051, 0.081]; τa 0.234, τb 0.169; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w1.er_minus_awp_appr` |
| W1 EndorseRank minus AWP, new transfer senders | Δτ -0.136 [-0.146, -0.127]; τa 0.194, τb 0.330; P(Δτ>0) 0.000; B=400 | `supplementary/supplementary.json` : `w1.er_minus_awp_send` |
| W1 n | 18,152 | `supplementary/supplementary.json` : `w1.n` |

## 8. Sybil cost model (EndorseRank graph at T_obs)

| Quantity | Value | Source |
|---|---|---|
| graph.nodes | 6,219,063 | `sybil-model/sybil_model.json` : `graph.nodes` |
| graph.edges | 11,210,114 | `sybil-model/sybil_model.json` : `graph.edges` |
| sigma0 | 0.8581 | `sybil-model/sybil_model.json` : `sigma0` |
| b common | 7.639e-08 | `sybil-model/sybil_model.json` : `b_common` |
| r D | 0.3824 | `sybil-model/sybil_model.json` : `r_D` |
| damping.0.75.r D | 0.3549 | `sybil-model/sybil_model.json` : `damping.0.75.r_D` |
| damping.0.75.farm factor | 2.0648 | `sybil-model/sybil_model.json` : `damping.0.75.farm_factor` |
| damping.0.85.r D | 0.3824 | `sybil-model/sybil_model.json` : `damping.0.85.r_D` |
| damping.0.85.farm factor | 3.1671 | `sybil-model/sybil_model.json` : `damping.0.85.farm_factor` |
| damping.0.95.r D | 0.4043 | `sybil-model/sybil_model.json` : `damping.0.95.r_D` |
| damping.0.95.farm factor | 8.6819 | `sybil-model/sybil_model.json` : `damping.0.95.farm_factor` |
| ring20 collects times share | 3.1671 | `sybil-model/sybil_model.json` : `ring20_collects_times_share` |
| star.m | 10 | `sybil-model/sybil_model.json` : `star.m` |
| star.target score | 2.615e-06 | `sybil-model/sybil_model.json` : `star.target_score` |
| star.closed form | 2.615e-06 | `sybil-model/sybil_model.json` : `star.closed_form` |
| star.highest cohort endorserank | 0.0318 | `sybil-model/sybil_model.json` : `star.highest_cohort_endorserank` |
| star.ratio to highest | 8.224e-05 | `sybil-model/sybil_model.json` : `star.ratio_to_highest` |
| star.approvals per window | 20 | `sybil-model/sybil_model.json` : `star.approvals_per_window` |
| fresh approval share median owner | 0.9573 | `sybil-model/sybil_model.json` : `fresh_approval_share_median_owner` |
| owners | 6,206,162 | `sybil-model/sybil_model.json` : `owners` |
| farm size to reach cohort quantile.p50.score | 1.881e-07 | `sybil-model/sybil_model.json` : `farm_size_to_reach_cohort_quantile.p50.score` |
| farm size to reach cohort quantile.p50.farm addresses | 0.0000 | `sybil-model/sybil_model.json` : `farm_size_to_reach_cohort_quantile.p50.farm_addresses` |
| farm size to reach cohort quantile.p90.score | 5.278e-06 | `sybil-model/sybil_model.json` : `farm_size_to_reach_cohort_quantile.p90.score` |
| farm size to reach cohort quantile.p90.farm addresses | 21.3797 | `sybil-model/sybil_model.json` : `farm_size_to_reach_cohort_quantile.p90.farm_addresses` |
| farm size to reach cohort quantile.p99.score | 0.0004855 | `sybil-model/sybil_model.json` : `farm_size_to_reach_cohort_quantile.p99.score` |
| farm size to reach cohort quantile.p99.farm addresses | 2,073.9 | `sybil-model/sybil_model.json` : `farm_size_to_reach_cohort_quantile.p99.farm_addresses` |
| farm size to reach cohort quantile.p100.score | 0.0318 | `sybil-model/sybil_model.json` : `farm_size_to_reach_cohort_quantile.p100.score` |
| farm size to reach cohort quantile.p100.farm addresses | 135,894.8 | `sybil-model/sybil_model.json` : `farm_size_to_reach_cohort_quantile.p100.farm_addresses` |

## 9. Robustness

| Quantity | Value | Source |
|---|---|---|
| Damping endorserank_d75: iterations | 41 | `same-window/eval_summary.json` : `damping.endorserank_d75.iterations` |
| Damping endorserank_d75: transfer family | 0.158 [0.146, 0.168]; B=400 | `same-window/eval_summary.json` : `damping.endorserank_d75.transfer` |
| Damping endorserank_d75: allowance family | 0.586 [0.580, 0.594]; B=400 | `same-window/eval_summary.json` : `damping.endorserank_d75.allowance` |
| Damping endorserank_d75: Sybil stability family | 0.007 [-0.002, 0.015]; B=400 | `same-window/eval_summary.json` : `damping.endorserank_d75.sybil_stability` |
| Damping awp_d75: iterations | 55 | `same-window/eval_summary.json` : `damping.awp_d75.iterations` |
| Damping awp_d75: transfer family | 0.570 [0.562, 0.578]; B=400 | `same-window/eval_summary.json` : `damping.awp_d75.transfer` |
| Damping awp_d75: allowance family | 0.193 [0.182, 0.203]; B=400 | `same-window/eval_summary.json` : `damping.awp_d75.allowance` |
| Damping awp_d75: Sybil stability family | 0.397 [0.389, 0.406]; B=400 | `same-window/eval_summary.json` : `damping.awp_d75.sybil_stability` |
| Damping endorserank_d85: iterations | 69 | `same-window/eval_summary.json` : `damping.endorserank_d85.iterations` |
| Damping endorserank_d85: transfer family | 0.158 [0.147, 0.169]; B=400 | `same-window/eval_summary.json` : `damping.endorserank_d85.transfer` |
| Damping endorserank_d85: allowance family | 0.585 [0.578, 0.592]; B=400 | `same-window/eval_summary.json` : `damping.endorserank_d85.allowance` |
| Damping endorserank_d85: Sybil stability family | 0.007 [-0.001, 0.015]; B=400 | `same-window/eval_summary.json` : `damping.endorserank_d85.sybil_stability` |
| Damping awp_d85: iterations | 92 | `same-window/eval_summary.json` : `damping.awp_d85.iterations` |
| Damping awp_d85: transfer family | 0.572 [0.564, 0.580]; B=400 | `same-window/eval_summary.json` : `damping.awp_d85.transfer` |
| Damping awp_d85: allowance family | 0.193 [0.182, 0.203]; B=400 | `same-window/eval_summary.json` : `damping.awp_d85.allowance` |
| Damping awp_d85: Sybil stability family | 0.395 [0.387, 0.403]; B=400 | `same-window/eval_summary.json` : `damping.awp_d85.sybil_stability` |
| Damping endorserank_d95: iterations | 217 | `same-window/eval_summary.json` : `damping.endorserank_d95.iterations` |
| Damping endorserank_d95: transfer family | 0.158 [0.147, 0.169]; B=400 | `same-window/eval_summary.json` : `damping.endorserank_d95.transfer` |
| Damping endorserank_d95: allowance family | 0.583 [0.577, 0.591]; B=400 | `same-window/eval_summary.json` : `damping.endorserank_d95.allowance` |
| Damping endorserank_d95: Sybil stability family | 0.008 [-0.0008255, 0.016]; B=400 | `same-window/eval_summary.json` : `damping.endorserank_d95.sybil_stability` |
| Damping awp_d95: iterations | 261 | `same-window/eval_summary.json` : `damping.awp_d95.iterations` |
| Damping awp_d95: transfer family | 0.577 [0.569, 0.585]; B=400 | `same-window/eval_summary.json` : `damping.awp_d95.transfer` |
| Damping awp_d95: allowance family | 0.192 [0.181, 0.202]; B=400 | `same-window/eval_summary.json` : `damping.awp_d95.allowance` |
| Damping awp_d95: Sybil stability family | 0.391 [0.384, 0.400]; B=400 | `same-window/eval_summary.json` : `damping.awp_d95.sybil_stability` |
| Slope 1: EndorseRank, transfer | 0.158 | `robustness/robustness.json` : `value_slope.1.endorserank.transfer` |
| Slope 1: EndorseRank, allowance | 0.585 | `robustness/robustness.json` : `value_slope.1.endorserank.allowance` |
| Slope 1: EndorseRank, Sybil stability | 0.007 | `robustness/robustness.json` : `value_slope.1.endorserank.sybil_stability` |
| Slope 1: AWP, transfer | 0.572 | `robustness/robustness.json` : `value_slope.1.awp.transfer` |
| Slope 1: AWP, allowance | 0.193 | `robustness/robustness.json` : `value_slope.1.awp.allowance` |
| Slope 1: AWP, Sybil stability | 0.395 | `robustness/robustness.json` : `value_slope.1.awp.sybil_stability` |
| Slope 01x: EndorseRank, transfer | 0.157 | `robustness/robustness.json` : `value_slope.01x.endorserank.transfer` |
| Slope 01x: EndorseRank, allowance | 0.588 | `robustness/robustness.json` : `value_slope.01x.endorserank.allowance` |
| Slope 01x: EndorseRank, Sybil stability | 0.006 | `robustness/robustness.json` : `value_slope.01x.endorserank.sybil_stability` |
| Slope 01x: AWP, transfer | 0.577 | `robustness/robustness.json` : `value_slope.01x.awp.transfer` |
| Slope 01x: AWP, allowance | 0.193 | `robustness/robustness.json` : `value_slope.01x.awp.allowance` |
| Slope 01x: AWP, Sybil stability | 0.397 | `robustness/robustness.json` : `value_slope.01x.awp.sybil_stability` |
| Slope 01x: EndorseRank rank agreement with the main score | 0.973 | `robustness/robustness.json` : `value_slope.01x.tau_with_main.endorserank` |
| Slope 01x: AWP rank agreement with the main score | 0.973 | `robustness/robustness.json` : `value_slope.01x.tau_with_main.awp` |
| Slope 10x: EndorseRank, transfer | 0.159 | `robustness/robustness.json` : `value_slope.10x.endorserank.transfer` |
| Slope 10x: EndorseRank, allowance | 0.580 | `robustness/robustness.json` : `value_slope.10x.endorserank.allowance` |
| Slope 10x: EndorseRank, Sybil stability | 0.009 | `robustness/robustness.json` : `value_slope.10x.endorserank.sybil_stability` |
| Slope 10x: AWP, transfer | 0.567 | `robustness/robustness.json` : `value_slope.10x.awp.transfer` |
| Slope 10x: AWP, allowance | 0.191 | `robustness/robustness.json` : `value_slope.10x.awp.allowance` |
| Slope 10x: AWP, Sybil stability | 0.393 | `robustness/robustness.json` : `value_slope.10x.awp.sybil_stability` |
| Slope 10x: EndorseRank rank agreement with the main score | 0.968 | `robustness/robustness.json` : `value_slope.10x.tau_with_main.endorserank` |
| Slope 10x: AWP rank agreement with the main score | 0.971 | `robustness/robustness.json` : `value_slope.10x.tau_with_main.awp` |
| Stage n=1,000: EndorseRank, transfer | 0.205 | `robustness/robustness.json` : `sample_definition[0].endorserank.transfer` |
| Stage n=1,000: EndorseRank, allowance | 0.715 | `robustness/robustness.json` : `sample_definition[0].endorserank.allowance` |
| Stage n=1,000: EndorseRank, Sybil stability | 0.038 | `robustness/robustness.json` : `sample_definition[0].endorserank.sybil_stability` |
| Stage n=1,000: AWP, transfer | 0.586 | `robustness/robustness.json` : `sample_definition[0].awp.transfer` |
| Stage n=1,000: AWP, allowance | 0.196 | `robustness/robustness.json` : `sample_definition[0].awp.allowance` |
| Stage n=1,000: AWP, Sybil stability | 0.408 | `robustness/robustness.json` : `sample_definition[0].awp.sybil_stability` |
| Stage n=1,000: allowance edges | 425,088 | `robustness/robustness.json` : `sample_definition[0].allowance_edges` |
| Stage n=1,000: transfer edges | 1,695,695 | `robustness/robustness.json` : `sample_definition[0].transfer_edges` |
| Stage n=2,000: EndorseRank, transfer | 0.196 | `robustness/robustness.json` : `sample_definition[1].endorserank.transfer` |
| Stage n=2,000: EndorseRank, allowance | 0.686 | `robustness/robustness.json` : `sample_definition[1].endorserank.allowance` |
| Stage n=2,000: EndorseRank, Sybil stability | 0.033 | `robustness/robustness.json` : `sample_definition[1].endorserank.sybil_stability` |
| Stage n=2,000: AWP, transfer | 0.588 | `robustness/robustness.json` : `sample_definition[1].awp.transfer` |
| Stage n=2,000: AWP, allowance | 0.199 | `robustness/robustness.json` : `sample_definition[1].awp.allowance` |
| Stage n=2,000: AWP, Sybil stability | 0.411 | `robustness/robustness.json` : `sample_definition[1].awp.sybil_stability` |
| Stage n=2,000: allowance edges | 1,263,854 | `robustness/robustness.json` : `sample_definition[1].allowance_edges` |
| Stage n=2,000: transfer edges | 3,152,531 | `robustness/robustness.json` : `sample_definition[1].transfer_edges` |
| Stage n=5,000: EndorseRank, transfer | 0.195 | `robustness/robustness.json` : `sample_definition[2].endorserank.transfer` |
| Stage n=5,000: EndorseRank, allowance | 0.634 | `robustness/robustness.json` : `sample_definition[2].endorserank.allowance` |
| Stage n=5,000: EndorseRank, Sybil stability | 0.034 | `robustness/robustness.json` : `sample_definition[2].endorserank.sybil_stability` |
| Stage n=5,000: AWP, transfer | 0.571 | `robustness/robustness.json` : `sample_definition[2].awp.transfer` |
| Stage n=5,000: AWP, allowance | 0.211 | `robustness/robustness.json` : `sample_definition[2].awp.allowance` |
| Stage n=5,000: AWP, Sybil stability | 0.391 | `robustness/robustness.json` : `sample_definition[2].awp.sybil_stability` |
| Stage n=5,000: allowance edges | 2,989,819 | `robustness/robustness.json` : `sample_definition[2].allowance_edges` |
| Stage n=5,000: transfer edges | 7,778,320 | `robustness/robustness.json` : `sample_definition[2].transfer_edges` |
| Stage n=10,000: EndorseRank, transfer | 0.167 | `robustness/robustness.json` : `sample_definition[3].endorserank.transfer` |
| Stage n=10,000: EndorseRank, allowance | 0.607 | `robustness/robustness.json` : `sample_definition[3].endorserank.allowance` |
| Stage n=10,000: EndorseRank, Sybil stability | 0.013 | `robustness/robustness.json` : `sample_definition[3].endorserank.sybil_stability` |
| Stage n=10,000: AWP, transfer | 0.571 | `robustness/robustness.json` : `sample_definition[3].awp.transfer` |
| Stage n=10,000: AWP, allowance | 0.196 | `robustness/robustness.json` : `sample_definition[3].awp.allowance` |
| Stage n=10,000: AWP, Sybil stability | 0.394 | `robustness/robustness.json` : `sample_definition[3].awp.sybil_stability` |
| Stage n=10,000: allowance edges | 6,678,752 | `robustness/robustness.json` : `sample_definition[3].allowance_edges` |
| Stage n=10,000: transfer edges | 17,190,775 | `robustness/robustness.json` : `sample_definition[3].transfer_edges` |
| Stage n=15,107: EndorseRank, transfer | 0.158 | `robustness/robustness.json` : `sample_definition[4].endorserank.transfer` |
| Stage n=15,107: EndorseRank, allowance | 0.585 | `robustness/robustness.json` : `sample_definition[4].endorserank.allowance` |
| Stage n=15,107: EndorseRank, Sybil stability | 0.007 | `robustness/robustness.json` : `sample_definition[4].endorserank.sybil_stability` |
| Stage n=15,107: AWP, transfer | 0.572 | `robustness/robustness.json` : `sample_definition[4].awp.transfer` |
| Stage n=15,107: AWP, allowance | 0.193 | `robustness/robustness.json` : `sample_definition[4].awp.allowance` |
| Stage n=15,107: AWP, Sybil stability | 0.395 | `robustness/robustness.json` : `sample_definition[4].awp.sybil_stability` |
| Stage n=15,107: allowance edges | 11,219,116 | `robustness/robustness.json` : `sample_definition[4].allowance_edges` |
| Stage n=15,107: transfer edges | 25,018,892 | `robustness/robustness.json` : `sample_definition[4].transfer_edges` |

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
| Full graphs: EndorseRank | mean 10.294 s, SD 0.601 s; runs 9.570, 11.063, 10.497, 9.811, 10.530; peak 879.7 MB; iterations 69; \|V\| 6,219,063; \|E\| 11,210,114 | `benchmark/benchmark.json` : `main.endorserank` |
| Full graphs: AWP | mean 22.367 s, SD 1.825 s; runs 21.139, 20.446, 24.122, 24.492, 21.637; peak 1,712.6 MB; iterations 92; \|V\| 7,882,356; \|E\| 25,001,216 | `benchmark/benchmark.json` : `main.awp` |
| Full graphs: C-PR (λ=0.5) | mean 36.162 s, SD 2.112 s; runs 33.813, 39.576, 35.439, 35.793, 36.187; peak 1,768.1 MB; iterations 79; \|V\| 9,151,010; \|E\| 31,552,359 | `benchmark/benchmark.json` : `main.cpr_l50` |
| Full graphs: S-PR | mean 34.422 s, SD 3.833 s; runs 38.769, 36.970, 29.310, 35.214, 31.848; peak 1,235.8 MB; iterations 158; \|V\| 7,884,602; \|E\| 25,018,892 | `benchmark/benchmark.json` : `main.spr` |
| AWP/EndorseRank runtime ratio (derived) | 2.17 | `benchmark/benchmark.json` : `main.awp.mean_s / main.endorserank.mean_s` |
| AWP/EndorseRank edge ratio (derived) | 2.23 | `benchmark/benchmark.json` : `main.awp.edges / main.endorserank.edges` |
| Damping 0.75: EndorseRank | mean 5.984 s, SD 0.044 s; runs 6.045, 5.963, 6.003, 5.984, 5.927; peak 879.7 MB; iterations 41; \|V\| 6,219,063; \|E\| 11,210,114 | `benchmark/benchmark.json` : `damping.0.75.endorserank` |
| Damping 0.75: AWP | mean 15.236 s, SD 1.781 s; runs 13.208, 16.968, 16.667, 15.870, 13.469; peak 1,712.6 MB; iterations 55; \|V\| 7,882,356; \|E\| 25,001,216 | `benchmark/benchmark.json` : `damping.0.75.awp` |
| Damping 0.85: EndorseRank | mean 10.294 s, SD 0.601 s; runs 9.570, 11.063, 10.497, 9.811, 10.530; peak 879.7 MB; iterations 69; \|V\| 6,219,063; \|E\| 11,210,114 | `benchmark/benchmark.json` : `damping.0.85.endorserank` |
| Damping 0.85: AWP | mean 22.367 s, SD 1.825 s; runs 21.139, 20.446, 24.122, 24.492, 21.637; peak 1,712.6 MB; iterations 92; \|V\| 7,882,356; \|E\| 25,001,216 | `benchmark/benchmark.json` : `damping.0.85.awp` |
| Damping 0.95: EndorseRank | mean 31.233 s, SD 0.673 s; runs 31.701, 32.171, 30.886, 30.574, 30.836; peak 879.7 MB; iterations 217; \|V\| 6,219,063; \|E\| 11,210,114 | `benchmark/benchmark.json` : `damping.0.95.endorserank` |
| Damping 0.95: AWP | mean 60.962 s, SD 3.697 s; runs 58.498, 56.896, 59.713, 64.490, 65.212; peak 1,712.6 MB; iterations 261; \|V\| 7,882,356; \|E\| 25,001,216 | `benchmark/benchmark.json` : `damping.0.95.awp` |
| Stage n=1,000: EndorseRank | mean 0.580 s, SD 0.125 s; runs 0.425, 0.489, 0.585, 0.683, 0.719; peak 47.7 MB; iterations 56; \|V\| 404,563; \|E\| 424,888 | `benchmark/benchmark.json` : `scaling[0].endorserank` |
| Stage n=1,000: AWP | mean 1.677 s, SD 0.229 s; runs 1.892, 1.408, 1.870, 1.758, 1.458; peak 166.1 MB; iterations 96; \|V\| 1,124,621; \|E\| 1,692,513 | `benchmark/benchmark.json` : `scaling[0].awp` |
| Stage n=2,000: EndorseRank | mean 0.939 s, SD 0.012 s; runs 0.944, 0.956, 0.925, 0.932, 0.937; peak 126.2 MB; iterations 45; \|V\| 1,112,404; \|E\| 1,263,471 | `benchmark/benchmark.json` : `scaling[1].endorserank` |
| Stage n=2,000: AWP | mean 4.272 s, SD 0.543 s; runs 3.748, 4.876, 4.133, 4.811, 3.792; peak 297.9 MB; iterations 98; \|V\| 1,917,597; \|E\| 3,148,826 | `benchmark/benchmark.json` : `scaling[1].awp` |
| Stage n=5,000: EndorseRank | mean 2.496 s, SD 0.159 s; runs 2.293, 2.420, 2.489, 2.555, 2.723; peak 263.9 MB; iterations 65; \|V\| 2,104,606; \|E\| 2,988,450 | `benchmark/benchmark.json` : `scaling[2].endorserank` |
| Stage n=5,000: AWP | mean 8.995 s, SD 0.840 s; runs 8.713, 9.861, 9.895, 8.051, 8.453; peak 634.5 MB; iterations 94; \|V\| 3,539,528; \|E\| 7,769,268 | `benchmark/benchmark.json` : `scaling[2].awp` |
| Stage n=10,000: EndorseRank | mean 6.220 s, SD 0.126 s; runs 6.253, 6.375, 6.065, 6.285, 6.119; peak 562.5 MB; iterations 72; \|V\| 4,291,078; \|E\| 6,673,167 | `benchmark/benchmark.json` : `scaling[3].endorserank` |
| Stage n=10,000: AWP | mean 16.821 s, SD 0.802 s; runs 17.640, 17.362, 17.160, 16.124, 15.816; peak 1,275.5 MB; iterations 94; \|V\| 6,247,634; \|E\| 17,180,184 | `benchmark/benchmark.json` : `scaling[3].awp` |
| Stage n=15,107 (reused main measurement): EndorseRank | mean 10.294 s, SD 0.601 s; runs 9.570, 11.063, 10.497, 9.811, 10.530; peak 879.7 MB; iterations 69; \|V\| 6,219,063; \|E\| 11,210,114 | `benchmark/benchmark.json` : `scaling[4].endorserank` |
| Stage n=15,107 (reused main measurement): AWP | mean 22.367 s, SD 1.825 s; runs 21.139, 20.446, 24.122, 24.492, 21.637; peak 1,712.6 MB; iterations 92; \|V\| 7,882,356; \|E\| 25,001,216 | `benchmark/benchmark.json` : `scaling[4].awp` |

## Data description (token list, rows left out, amounts in USD, constants, prices, GMX contract traders, timing)

| Quantity | Value | Source |
|---|---|---|
| rows.registered ego.approvals | 389,866,882 | `describe/describe.json` : `rows.registered_ego.approvals` |
| rows.registered ego.transfers | 1,538,404,067 | `describe/describe.json` : `rows.registered_ego.transfers` |
| rows.registered ego.approvals w1 | 18,199,269 | `describe/describe.json` : `rows.registered_ego.approvals_w1` |
| rows.registered ego.transfers w1 | 74,441,935 | `describe/describe.json` : `rows.registered_ego.transfers_w1` |
| rows.unlisted tokens.tokens | 142,958 | `describe/describe.json` : `rows.unlisted_tokens.tokens` |
| rows.unlisted tokens.approvals | 164,202,859 | `describe/describe.json` : `rows.unlisted_tokens.approvals` |
| rows.unlisted tokens.transfers | 364,468,917 | `describe/describe.json` : `rows.unlisted_tokens.transfers` |
| rows.unlisted tokens.approvals w1 | 5,985,398 | `describe/describe.json` : `rows.unlisted_tokens.approvals_w1` |
| rows.unlisted tokens.transfers w1 | 13,539,539 | `describe/describe.json` : `rows.unlisted_tokens.transfers_w1` |
| rows.listed tokens outside revised ego.approvals | 709,821 | `describe/describe.json` : `rows.listed_tokens_outside_revised_ego.approvals` |
| rows.listed tokens outside revised ego.transfers | 24,766,612 | `describe/describe.json` : `rows.listed_tokens_outside_revised_ego.transfers` |
| rows.listed tokens outside revised ego.approvals w1 | 3,977 | `describe/describe.json` : `rows.listed_tokens_outside_revised_ego.approvals_w1` |
| rows.listed tokens outside revised ego.transfers w1 | 720,204 | `describe/describe.json` : `rows.listed_tokens_outside_revised_ego.transfers_w1` |
| rows.revised ego.approvals | 224,954,202 | `describe/describe.json` : `rows.revised_ego.approvals` |
| rows.revised ego.transfers | 1,149,168,538 | `describe/describe.json` : `rows.revised_ego.transfers` |
| rows.revised ego.approvals w1 | 12,209,894 | `describe/describe.json` : `rows.revised_ego.approvals_w1` |
| rows.revised ego.transfers w1 | 60,182,192 | `describe/describe.json` : `rows.revised_ego.transfers_w1` |
| rows.revised share of registered.approvals | 0.5770 | `describe/describe.json` : `rows.revised_share_of_registered.approvals` |
| rows.revised share of registered.transfers | 0.7470 | `describe/describe.json` : `rows.revised_share_of_registered.transfers` |
| rows.revised share of registered.approvals w1 | 0.6709 | `describe/describe.json` : `rows.revised_share_of_registered.approvals_w1` |
| rows.revised share of registered.transfers w1 | 0.8084 | `describe/describe.json` : `rows.revised_share_of_registered.transfers_w1` |
| rows.revised transfers without price | 0 | `describe/describe.json` : `rows.revised_transfers_without_price` |
| amounts.latest allowances tobs | 12,590,613 | `describe/describe.json` : `amounts.latest_allowances_tobs` |
| amounts.unlimited allowances | 5,763,757 | `describe/describe.json` : `amounts.unlimited_allowances` |
| amounts.unlimited share | 0.4578 | `describe/describe.json` : `amounts.unlimited_share` |
| amounts.allowances at or above cap | 6,776,289 | `describe/describe.json` : `amounts.allowances_at_or_above_cap` |
| amounts.allowances at or above cap share | 0.5382 | `describe/describe.json` : `amounts.allowances_at_or_above_cap_share` |
| amounts.owners | 6,208,769 | `describe/describe.json` : `amounts.owners` |
| amounts.owners with unlimited | 3,294,370 | `describe/describe.json` : `amounts.owners_with_unlimited` |
| amounts.owners with both kinds | 797,852 | `describe/describe.json` : `amounts.owners_with_both_kinds` |
| amounts.finite allowance usd percentiles tobs.p10 | 0.3299 | `describe/describe.json` : `amounts.finite_allowance_usd_percentiles_tobs.p10` |
| amounts.finite allowance usd percentiles tobs.p25 | 5.4414 | `describe/describe.json` : `amounts.finite_allowance_usd_percentiles_tobs.p25` |
| amounts.finite allowance usd percentiles tobs.p50 | 60.5836 | `describe/describe.json` : `amounts.finite_allowance_usd_percentiles_tobs.p50` |
| amounts.finite allowance usd percentiles tobs.p75 | 1,198.4 | `describe/describe.json` : `amounts.finite_allowance_usd_percentiles_tobs.p75` |
| amounts.finite allowance usd percentiles tobs.p90 | 2,144,554,702.5 | `describe/describe.json` : `amounts.finite_allowance_usd_percentiles_tobs.p90` |
| amounts.finite allowance usd percentiles tobs.p99 | 5,852,974,286,215,904,673,302,322,648,306,172,706,982,723,584 | `describe/describe.json` : `amounts.finite_allowance_usd_percentiles_tobs.p99` |
| amounts.transfers obs | 1,149,168,538 | `describe/describe.json` : `amounts.transfers_obs` |
| amounts.transfer usd percentiles obs.p10 | 0.1415 | `describe/describe.json` : `amounts.transfer_usd_percentiles_obs.p10` |
| amounts.transfer usd percentiles obs.p25 | 12.1944 | `describe/describe.json` : `amounts.transfer_usd_percentiles_obs.p25` |
| amounts.transfer usd percentiles obs.p50 | 193.5688 | `describe/describe.json` : `amounts.transfer_usd_percentiles_obs.p50` |
| amounts.transfer usd percentiles obs.p75 | 891.9413 | `describe/describe.json` : `amounts.transfer_usd_percentiles_obs.p75` |
| amounts.transfer usd percentiles obs.p90 | 2,967.6 | `describe/describe.json` : `amounts.transfer_usd_percentiles_obs.p90` |
| amounts.transfer usd percentiles obs.p99 | 19,999.9 | `describe/describe.json` : `amounts.transfer_usd_percentiles_obs.p99` |
| constants.computed at | 2026-10-10T11:23:50+00:00 | `describe/describe.json` : `constants.computed_at` |
| constants.source | sql/13_usd_constants.sql (contract_rep.u_constants), events up to t1 | `describe/describe.json` : `constants.source` |
| constants.raw.m allowance | 61.5102 | `describe/describe.json` : `constants.raw.m_allowance` |
| constants.raw.m transfer | 203.7129 | `describe/describe.json` : `constants.raw.m_transfer` |
| constants.raw.n finite allowances | 6,491,970 | `describe/describe.json` : `constants.raw.n_finite_allowances` |
| constants.raw.n transfers | 1,073,838,657 | `describe/describe.json` : `constants.raw.n_transfers` |
| constants.raw.n unlimited allowances | 5,490,386 | `describe/describe.json` : `constants.raw.n_unlimited_allowances` |
| constants.raw.p10 allowance | 0.3246 | `describe/describe.json` : `constants.raw.p10_allowance` |
| constants.raw.p10 transfer | 0.1402 | `describe/describe.json` : `constants.raw.p10_transfer` |
| constants.raw.p90 allowance | 2,146,753,785.3 | `describe/describe.json` : `constants.raw.p90_allowance` |
| constants.raw.p90 transfer | 3,051.5 | `describe/describe.json` : `constants.raw.p90_transfer` |
| constants.raw.p99 allowance | 99,966,013,166,071,363,303,716,946,220,738,462,691,769,712,640 | `describe/describe.json` : `constants.raw.p99_allowance` |
| constants.raw.p99 transfer | 20,266.4 | `describe/describe.json` : `constants.raw.p99_transfer` |
| constants.m transfer usd | 200.0000 | `describe/describe.json` : `constants.m_transfer_usd` |
| constants.m allowance usd | 62.0000 | `describe/describe.json` : `constants.m_allowance_usd` |
| constants.cap allowance usd | 20,000 | `describe/describe.json` : `constants.cap_allowance_usd` |
| constants.b transfer | 0.0055 | `describe/describe.json` : `constants.b_transfer` |
| constants.b allowance | 0.0177 | `describe/describe.json` : `constants.b_allowance` |
| constants.unlimited base units | 114,999,999,999,999,997,377,225,245,734,177,625,043,124,954,484,653,241,178,190,190,737,365,693,104,128 | `describe/describe.json` : `constants.unlimited_base_units` |
| constants.rule | b = ln 3 / m with m the median rounded to two significant digits; the allowance cap U is the 99th percentile of the USD values of the transfers up to t1, rounded to two significant digits | `describe/describe.json` : `constants.rule` |
| timing.revision commit utc | a897475 2026-10-10T07:54:35+00:00 | `describe/describe.json` : `timing.revision_commit_utc` |
| timing.revised jobs usd | 5.0900 | `describe/describe.json` : `timing.revised_jobs_usd` |
| timing.bigquery usd total | 34.8000 | `describe/describe.json` : `timing.bigquery_usd_total` |
| timing.bigquery tib billed | 5.5690 | `describe/describe.json` : `timing.bigquery_tib_billed` |
| listed tokens | 64 | `describe/describe.json` : `listed_tokens` |

### Listed tokens: rows of the registered and revised ego tables, USD volume

| Quantity | Value | Source |
|---|---|---|
| WETH 0x82af49447d8a07e3bd95bd0d56f35241523fbab1 | registered approvals 77,975,750, transfers 508,611,616; revised approvals 77,750,158, transfers 491,260,915; transfer USD 835,852,965,864.8; without price 0.000 | `describe/describe.json` : `per_token[0]` |
| USDC 0xaf88d065e77c8cc2239327c5edb3a432268e5831 | registered approvals 41,395,787, transfers 359,321,018; revised approvals 41,384,428, transfers 354,895,908; transfer USD 991,356,457,001.6; without price 0.000 | `describe/describe.json` : `per_token[1]` |
| USD₮0 0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9 | registered approvals 72,936,517, transfers 160,137,487; revised approvals 72,873,996, transfers 158,554,279; transfer USD 273,071,295,763.1; without price 0.000 | `describe/describe.json` : `per_token[2]` |
| ARB 0x912ce59144191c1204e64559fe8253a0e49e6548 | registered approvals 16,330,925, transfers 74,421,140; revised approvals 15,924,247, transfers 73,305,553; transfer USD 85,022,223,181.1; without price 0.000 | `describe/describe.json` : `per_token[3]` |
| WBTC 0x2f2a2543b76a4166549f7aab2e75bef0aefc5b0f | registered approvals 17,025,044, transfers 71,443,889; revised approvals 17,021,373, transfers 71,151,883; transfer USD 223,190,802,368.9; without price 0.000 | `describe/describe.json` : `per_token[4]` |

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
| approval_ego 2023-10 | 2,657,369 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2023-11 | 3,763,237 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2023-12 | 3,378,029 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2024-01 | 4,668,526 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2024-02 | 3,871,550 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2024-03 | 6,783,784 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2024-04 | 14,387,562 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2024-05 | 9,923,795 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2024-06 | 7,874,383 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2024-07 | 9,020,360 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2024-08 | 7,954,426 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2024-09 | 6,098,610 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2024-10 | 6,220,715 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2024-11 | 7,397,325 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2024-12 | 8,728,129 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2025-01 | 6,782,148 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2025-02 | 5,637,389 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2025-03 | 6,386,946 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2025-04 | 4,971,297 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2025-05 | 6,644,732 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2025-06 | 5,394,561 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2025-07 | 6,069,259 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2025-08 | 9,174,372 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2025-09 | 8,351,629 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2025-10 | 9,940,050 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2025-11 | 7,559,344 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2025-12 | 11,007,845 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2026-01 | 7,814,615 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2026-02 | 7,201,005 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2026-03 | 5,967,171 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2026-04 | 4,353,160 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2026-05 | 3,295,991 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2026-06 | 5,674,888 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2023-10 | 8,131,746 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2023-11 | 11,304,117 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2023-12 | 11,861,292 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2024-01 | 15,582,879 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2024-02 | 12,195,340 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2024-03 | 23,565,922 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2024-04 | 41,446,470 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2024-05 | 30,594,305 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2024-06 | 25,356,843 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2024-07 | 36,917,305 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2024-08 | 42,543,803 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2024-09 | 29,397,283 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2024-10 | 31,463,575 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2024-11 | 50,183,746 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2024-12 | 49,030,590 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2025-01 | 43,973,194 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2025-02 | 45,503,945 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2025-03 | 47,759,742 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2025-04 | 41,841,325 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2025-05 | 51,787,297 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2025-06 | 43,134,889 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2025-07 | 49,486,331 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2025-08 | 52,533,142 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2025-09 | 38,244,778 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2025-10 | 49,611,973 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2025-11 | 44,650,159 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2025-12 | 42,182,264 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2026-01 | 39,119,508 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2026-02 | 35,385,506 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2026-03 | 29,049,388 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2026-04 | 24,033,195 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2026-05 | 22,049,046 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2026-06 | 29,247,640 | `describe/describe.json` : `monthly_counts` |
