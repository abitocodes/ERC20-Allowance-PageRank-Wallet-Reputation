# Results digest

Written by `experiments/scripts/publish_results.py` on 2026-10-09 23:23 UTC from the summaries in this folder; nothing here is recomputed. Each row names the file (relative to this folder) and the key inside it. τ entries read `point [95% CI]`, contrasts `Δτ [95% CI]; τa, τb; P(Δτ>0)`, and `B` is the number of bootstrap resamples behind the interval. `SHA256SUMS.txt` lists the checksums of every file published here.

- Code revision: `8d8b568ecaf882cccc6caef60b444823966f5ce8` with uncommitted changes (git status code) in: `scripts/export_latex.py (M)`, `scripts/publish_results.py (M)`, `scripts/run_benchmark.py (M)`, `scripts/describe_data.py (??)`
- Published files: `same-window/eval_summary.json`, `holdout-w0/eval_summary.json`, `registered-w1/eval_summary.json`, `registered-w1/extraction_manifest.json`, `sybil-model/sybil_model.json`, `robustness/robustness.json`, `benchmark/benchmark.json`, `supplementary/supplementary.json`, `describe/describe.json`, `cohort/matched_cohort.json`, `gmx/gmx_contract_closes_obs_decoded.json`, `gmx/gmx_contract_closes_w1_decoded.json`, `config/contract_reputation.yaml`, `docs/analysis_plan.md`, `docs/registration_w1.md`

## 1. Cohort and graph sizes

| Quantity | Value | Source |
|---|---|---|
| Cohort rule | contract spenders with non-zero approvals from >= 3 distinct owners, 2023-10-01 00:00:00 UTC to 2026-06-30 23:59:59 UTC | `cohort/matched_cohort.json` : `rule` |
| Candidate spenders | 29,022 | `cohort/matched_cohort.json` : `candidates` |
| Candidates by account type: contract | 27,844 | `cohort/matched_cohort.json` : `by_code_kind.contract` |
| Candidates by account type: none | 1,121 | `cohort/matched_cohort.json` : `by_code_kind.none` |
| Candidates by account type: eip7702 | 57 | `cohort/matched_cohort.json` : `by_code_kind.eip7702` |
| Matched cohort (contracts) | 27,844 | `cohort/matched_cohort.json` : `cohort` |
| Anchor T_obs | 2026-06-30 23:59:59 UTC | `same-window/eval_summary.json` : `anchor` |
| Cohort scored in the same window | 27,844 | `same-window/eval_summary.json` : `cohort` |
| T_obs allowance graph, nodes | 13,055,150 | `same-window/eval_summary.json` : `graph.allowance.nodes` |
| T_obs allowance graph, edges | 22,321,470 | `same-window/eval_summary.json` : `graph.allowance.edges` |
| T_obs transfer graph, nodes | 23,029,298 | `same-window/eval_summary.json` : `graph.transfer.nodes` |
| T_obs transfer graph, edges | 59,737,617 | `same-window/eval_summary.json` : `graph.transfer.edges` |
| Cohort contracts outside the allowance graph | 962 | `same-window/eval_summary.json` : `graph.cohort_outside_allowance` |
| Cohort contracts outside the transfer graph | 3,297 | `same-window/eval_summary.json` : `graph.cohort_outside_transfer` |
| Cohort contracts outside both graphs | 138 | `same-window/eval_summary.json` : `graph.cohort_outside_both` |
| Power iterations at T_obs, EndorseRank | 84 | `same-window/eval_summary.json` : `iterations.endorserank` |
| Power iterations at T_obs, EndorseRank (activity restarts) | 83 | `same-window/eval_summary.json` : `iterations.endorserank_activity` |
| Power iterations at T_obs, AWP | 93 | `same-window/eval_summary.json` : `iterations.awp` |
| Power iterations at T_obs, C-PR (λ=1) | 83 | `same-window/eval_summary.json` : `iterations.cpr_l100` |
| Power iterations at T_obs, C-PR (λ=0) | 98 | `same-window/eval_summary.json` : `iterations.cpr_l0` |
| Power iterations at T_obs, C-PR (λ=0.25) | 90 | `same-window/eval_summary.json` : `iterations.cpr_l25` |
| Power iterations at T_obs, C-PR (λ=0.5) | 92 | `same-window/eval_summary.json` : `iterations.cpr_l50` |
| Power iterations at T_obs, C-PR (λ=0.75) | 94 | `same-window/eval_summary.json` : `iterations.cpr_l75` |
| Power iterations at T_obs, S-PR | 185 | `same-window/eval_summary.json` : `iterations.spr` |
| t1 graph, allowance edges | 21,550,791 | `holdout-w0/eval_summary.json` : `graph.allowance_edges` |
| t1 graph, transfer edges | 58,065,784 | `holdout-w0/eval_summary.json` : `graph.transfer_edges` |
| Power iterations at t1, EndorseRank | 84 | `holdout-w0/eval_summary.json` : `iterations.endorserank` |
| Power iterations at t1, EndorseRank (activity restarts) | 84 | `holdout-w0/eval_summary.json` : `iterations.endorserank_activity` |
| Power iterations at t1, AWP | 93 | `holdout-w0/eval_summary.json` : `iterations.awp` |
| Power iterations at t1, C-PR (λ=1) | 84 | `holdout-w0/eval_summary.json` : `iterations.cpr_l100` |
| Power iterations at t1, C-PR (λ=0) | 98 | `holdout-w0/eval_summary.json` : `iterations.cpr_l0` |
| Power iterations at t1, C-PR (λ=0.25) | 90 | `holdout-w0/eval_summary.json` : `iterations.cpr_l25` |
| Power iterations at t1, C-PR (λ=0.5) | 92 | `holdout-w0/eval_summary.json` : `iterations.cpr_l50` |
| Power iterations at t1, C-PR (λ=0.75) | 94 | `holdout-w0/eval_summary.json` : `iterations.cpr_l75` |
| Power iterations at t1, S-PR | 187 | `holdout-w0/eval_summary.json` : `iterations.spr` |
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
| EndorseRank, transfer family | 0.122 [0.113, 0.129]; B=400 | `same-window/eval_summary.json` : `families.endorserank.transfer` |
| EndorseRank, allowance family | 0.481 [0.476, 0.487]; B=400 | `same-window/eval_summary.json` : `families.endorserank.allowance` |
| EndorseRank, Sybil stability family | 0.025 [0.019, 0.031]; B=400 | `same-window/eval_summary.json` : `families.endorserank.sybil_stability` |
| EndorseRank (activity restarts), transfer family | 0.107 [0.099, 0.114]; B=400 | `same-window/eval_summary.json` : `families.endorserank_activity.transfer` |
| EndorseRank (activity restarts), allowance family | 0.333 [0.326, 0.339]; B=400 | `same-window/eval_summary.json` : `families.endorserank_activity.allowance` |
| EndorseRank (activity restarts), Sybil stability family | 0.033 [0.027, 0.039]; B=400 | `same-window/eval_summary.json` : `families.endorserank_activity.sybil_stability` |
| AWP, transfer family | 0.447 [0.440, 0.453]; B=400 | `same-window/eval_summary.json` : `families.awp.transfer` |
| AWP, allowance family | 0.173 [0.165, 0.180]; B=400 | `same-window/eval_summary.json` : `families.awp.allowance` |
| AWP, Sybil stability family | 0.311 [0.303, 0.317]; B=400 | `same-window/eval_summary.json` : `families.awp.sybil_stability` |
| C-PR (λ=1), transfer family | 0.111 [0.103, 0.118]; B=400 | `same-window/eval_summary.json` : `families.cpr_l100.transfer` |
| C-PR (λ=1), allowance family | 0.512 [0.506, 0.517]; B=400 | `same-window/eval_summary.json` : `families.cpr_l100.allowance` |
| C-PR (λ=1), Sybil stability family | 0.020 [0.015, 0.026]; B=400 | `same-window/eval_summary.json` : `families.cpr_l100.sybil_stability` |
| C-PR (λ=0), transfer family | 0.528 [0.522, 0.534]; B=400 | `same-window/eval_summary.json` : `families.cpr_l0.transfer` |
| C-PR (λ=0), allowance family | 0.195 [0.187, 0.202]; B=400 | `same-window/eval_summary.json` : `families.cpr_l0.allowance` |
| C-PR (λ=0), Sybil stability family | 0.311 [0.304, 0.317]; B=400 | `same-window/eval_summary.json` : `families.cpr_l0.sybil_stability` |
| C-PR (λ=0.25), transfer family | 0.312 [0.304, 0.319]; B=400 | `same-window/eval_summary.json` : `families.cpr_l25.transfer` |
| C-PR (λ=0.25), allowance family | 0.396 [0.390, 0.402]; B=400 | `same-window/eval_summary.json` : `families.cpr_l25.allowance` |
| C-PR (λ=0.25), Sybil stability family | 0.138 [0.133, 0.144]; B=400 | `same-window/eval_summary.json` : `families.cpr_l25.sybil_stability` |
| C-PR (λ=0.5), transfer family | 0.296 [0.289, 0.303]; B=400 | `same-window/eval_summary.json` : `families.cpr_l50.transfer` |
| C-PR (λ=0.5), allowance family | 0.418 [0.412, 0.423]; B=400 | `same-window/eval_summary.json` : `families.cpr_l50.allowance` |
| C-PR (λ=0.5), Sybil stability family | 0.129 [0.124, 0.134]; B=400 | `same-window/eval_summary.json` : `families.cpr_l50.sybil_stability` |
| C-PR (λ=0.75), transfer family | 0.276 [0.269, 0.282]; B=400 | `same-window/eval_summary.json` : `families.cpr_l75.transfer` |
| C-PR (λ=0.75), allowance family | 0.432 [0.427, 0.438]; B=400 | `same-window/eval_summary.json` : `families.cpr_l75.allowance` |
| C-PR (λ=0.75), Sybil stability family | 0.116 [0.111, 0.122]; B=400 | `same-window/eval_summary.json` : `families.cpr_l75.sybil_stability` |
| S-PR, transfer family | 0.467 [0.460, 0.473]; B=400 | `same-window/eval_summary.json` : `families.spr.transfer` |
| S-PR, allowance family | 0.320 [0.313, 0.328]; B=400 | `same-window/eval_summary.json` : `families.spr.allowance` |
| S-PR, Sybil stability family | 0.298 [0.291, 0.304]; B=400 | `same-window/eval_summary.json` : `families.spr.sybil_stability` |

### Per proxy (τ_b [95% CI]; Spearman ρ)

| Quantity | Value | Source |
|---|---|---|
| EndorseRank, in_degree | 0.196 [0.187, 0.204]; ρ 0.283; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank.in_degree` |
| EndorseRank, in_value | 0.048 [0.039, 0.055]; ρ 0.081; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank.in_value` |
| EndorseRank, in_approve_degree | 0.626 [0.620, 0.632]; ρ 0.786; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank.in_approve_degree` |
| EndorseRank, in_approve_value | 0.336 [0.329, 0.344]; ρ 0.467; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank.in_approve_value` |
| EndorseRank, inbound_counterparty_ratio | -0.128 [-0.135, -0.121]; ρ -0.190; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank.inbound_counterparty_ratio` |
| EndorseRank, transfer_tenure_days | 0.083 [0.074, 0.090]; ρ 0.131; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank.transfer_tenure_days` |
| EndorseRank, active_months | 0.121 [0.113, 0.129]; ρ 0.180; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank.active_months` |
| EndorseRank (activity restarts), in_degree | 0.176 [0.167, 0.183]; ρ 0.250; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank_activity.in_degree` |
| EndorseRank (activity restarts), in_value | 0.037 [0.029, 0.046]; ρ 0.055; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank_activity.in_value` |
| EndorseRank (activity restarts), in_approve_degree | 0.437 [0.430, 0.443]; ρ 0.587; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank_activity.in_approve_degree` |
| EndorseRank (activity restarts), in_approve_value | 0.228 [0.221, 0.236]; ρ 0.327; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank_activity.in_approve_value` |
| EndorseRank (activity restarts), inbound_counterparty_ratio | -0.088 [-0.096, -0.080]; ρ -0.129; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank_activity.inbound_counterparty_ratio` |
| EndorseRank (activity restarts), transfer_tenure_days | 0.074 [0.066, 0.081]; ρ 0.109; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank_activity.transfer_tenure_days` |
| EndorseRank (activity restarts), active_months | 0.114 [0.106, 0.122]; ρ 0.164; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank_activity.active_months` |
| AWP, in_degree | 0.541 [0.534, 0.547]; ρ 0.706; B=400 | `same-window/eval_summary.json` : `per_proxy.awp.in_degree` |
| AWP, in_value | 0.353 [0.345, 0.361]; ρ 0.496; B=400 | `same-window/eval_summary.json` : `per_proxy.awp.in_value` |
| AWP, in_approve_degree | 0.227 [0.218, 0.235]; ρ 0.317; B=400 | `same-window/eval_summary.json` : `per_proxy.awp.in_approve_degree` |
| AWP, in_approve_value | 0.118 [0.110, 0.126]; ρ 0.176; B=400 | `same-window/eval_summary.json` : `per_proxy.awp.in_approve_value` |
| AWP, inbound_counterparty_ratio | -0.019 [-0.029, -0.010]; ρ 0.022; B=400 | `same-window/eval_summary.json` : `per_proxy.awp.inbound_counterparty_ratio` |
| AWP, transfer_tenure_days | 0.452 [0.445, 0.458]; ρ 0.620; B=400 | `same-window/eval_summary.json` : `per_proxy.awp.transfer_tenure_days` |
| AWP, active_months | 0.499 [0.492, 0.506]; ρ 0.651; B=400 | `same-window/eval_summary.json` : `per_proxy.awp.active_months` |
| C-PR (λ=1), in_degree | 0.171 [0.162, 0.179]; ρ 0.243; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l100.in_degree` |
| C-PR (λ=1), in_value | 0.051 [0.042, 0.059]; ρ 0.081; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l100.in_value` |
| C-PR (λ=1), in_approve_degree | 0.603 [0.597, 0.609]; ρ 0.760; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l100.in_approve_degree` |
| C-PR (λ=1), in_approve_value | 0.420 [0.413, 0.428]; ρ 0.564; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l100.in_approve_value` |
| C-PR (λ=1), inbound_counterparty_ratio | -0.118 [-0.126, -0.110]; ρ -0.174; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l100.inbound_counterparty_ratio` |
| C-PR (λ=1), transfer_tenure_days | 0.072 [0.064, 0.081]; ρ 0.112; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l100.transfer_tenure_days` |
| C-PR (λ=1), active_months | 0.106 [0.097, 0.114]; ρ 0.154; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l100.active_months` |
| C-PR (λ=0), in_degree | 0.599 [0.593, 0.606]; ρ 0.763; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l0.in_degree` |
| C-PR (λ=0), in_value | 0.457 [0.450, 0.465]; ρ 0.620; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l0.in_value` |
| C-PR (λ=0), in_approve_degree | 0.262 [0.253, 0.271]; ρ 0.356; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l0.in_approve_degree` |
| C-PR (λ=0), in_approve_value | 0.128 [0.120, 0.137]; ρ 0.186; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l0.in_approve_value` |
| C-PR (λ=0), inbound_counterparty_ratio | 0.080 [0.069, 0.089]; ρ 0.143; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l0.inbound_counterparty_ratio` |
| C-PR (λ=0), transfer_tenure_days | 0.406 [0.398, 0.413]; ρ 0.563; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l0.transfer_tenure_days` |
| C-PR (λ=0), active_months | 0.448 [0.440, 0.455]; ρ 0.594; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l0.active_months` |
| C-PR (λ=0.25), in_degree | 0.359 [0.351, 0.366]; ρ 0.491; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l25.in_degree` |
| C-PR (λ=0.25), in_value | 0.265 [0.256, 0.274]; ρ 0.383; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l25.in_value` |
| C-PR (λ=0.25), in_approve_degree | 0.469 [0.461, 0.475]; ρ 0.624; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l25.in_approve_degree` |
| C-PR (λ=0.25), in_approve_value | 0.324 [0.316, 0.331]; ρ 0.456; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l25.in_approve_value` |
| C-PR (λ=0.25), inbound_counterparty_ratio | -0.099 [-0.107, -0.091]; ρ -0.144; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l25.inbound_counterparty_ratio` |
| C-PR (λ=0.25), transfer_tenure_days | 0.236 [0.229, 0.243]; ρ 0.344; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l25.transfer_tenure_days` |
| C-PR (λ=0.25), active_months | 0.278 [0.271, 0.287]; ρ 0.389; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l25.active_months` |
| C-PR (λ=0.5), in_degree | 0.344 [0.336, 0.352]; ρ 0.471; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l50.in_degree` |
| C-PR (λ=0.5), in_value | 0.248 [0.240, 0.257]; ρ 0.361; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l50.in_value` |
| C-PR (λ=0.5), in_approve_degree | 0.485 [0.477, 0.491]; ρ 0.641; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l50.in_approve_degree` |
| C-PR (λ=0.5), in_approve_value | 0.351 [0.344, 0.358]; ρ 0.491; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l50.in_approve_value` |
| C-PR (λ=0.5), inbound_counterparty_ratio | -0.112 [-0.119, -0.104]; ρ -0.163; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l50.inbound_counterparty_ratio` |
| C-PR (λ=0.5), transfer_tenure_days | 0.228 [0.221, 0.236]; ρ 0.334; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l50.transfer_tenure_days` |
| C-PR (λ=0.5), active_months | 0.270 [0.262, 0.279]; ρ 0.379; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l50.active_months` |
| C-PR (λ=0.75), in_degree | 0.325 [0.317, 0.333]; ρ 0.447; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l75.in_degree` |
| C-PR (λ=0.75), in_value | 0.226 [0.218, 0.234]; ρ 0.330; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l75.in_value` |
| C-PR (λ=0.75), in_approve_degree | 0.495 [0.487, 0.501]; ρ 0.651; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l75.in_approve_degree` |
| C-PR (λ=0.75), in_approve_value | 0.370 [0.364, 0.378]; ρ 0.514; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l75.in_approve_value` |
| C-PR (λ=0.75), inbound_counterparty_ratio | -0.118 [-0.126, -0.110]; ρ -0.172; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l75.inbound_counterparty_ratio` |
| C-PR (λ=0.75), transfer_tenure_days | 0.213 [0.206, 0.221]; ρ 0.314; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l75.transfer_tenure_days` |
| C-PR (λ=0.75), active_months | 0.253 [0.246, 0.262]; ρ 0.358; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l75.active_months` |
| S-PR, in_degree | 0.518 [0.510, 0.524]; ρ 0.680; B=400 | `same-window/eval_summary.json` : `per_proxy.spr.in_degree` |
| S-PR, in_value | 0.417 [0.409, 0.425]; ρ 0.575; B=400 | `same-window/eval_summary.json` : `per_proxy.spr.in_value` |
| S-PR, in_approve_degree | 0.396 [0.388, 0.404]; ρ 0.518; B=400 | `same-window/eval_summary.json` : `per_proxy.spr.in_approve_degree` |
| S-PR, in_approve_value | 0.245 [0.237, 0.253]; ρ 0.342; B=400 | `same-window/eval_summary.json` : `per_proxy.spr.in_approve_value` |
| S-PR, inbound_counterparty_ratio | 0.086 [0.075, 0.095]; ρ 0.150; B=400 | `same-window/eval_summary.json` : `per_proxy.spr.inbound_counterparty_ratio` |
| S-PR, transfer_tenure_days | 0.377 [0.369, 0.384]; ρ 0.524; B=400 | `same-window/eval_summary.json` : `per_proxy.spr.transfer_tenure_days` |
| S-PR, active_months | 0.430 [0.423, 0.437]; ρ 0.574; B=400 | `same-window/eval_summary.json` : `per_proxy.spr.active_months` |

## 3. Same-window contrasts, score agreement and rule A (secondary part)

| Quantity | Value | Source |
|---|---|---|
| [hybrid] C-PR transfer minus C-PR (l=0) transfer | Δτ -0.232 [-0.239, -0.224]; τa 0.296, τb 0.528; P(Δτ>0) 0.000; B=400 | `same-window/eval_summary.json` : `contrasts[0]` |
| [hybrid] C-PR allowance minus C-PR (l=1) allowance | Δτ -0.094 [-0.099, -0.088]; τa 0.418, τb 0.512; P(Δτ>0) 0.000; B=400 | `same-window/eval_summary.json` : `contrasts[1]` |
| [hybrid] C-PR sybil minus C-PR (l=0) sybil | Δτ -0.182 [-0.189, -0.176]; τa 0.129, τb 0.311; P(Δτ>0) 0.000; B=400 | `same-window/eval_summary.json` : `contrasts[2]` |
| [hybrid] C-PR sybil minus C-PR (l=1) sybil | Δτ 0.109 [0.105, 0.113]; τa 0.129, τb 0.020; P(Δτ>0) 1.000; B=400 | `same-window/eval_summary.json` : `contrasts[3]` |
| [hybrid] S-PR transfer minus C-PR (l=0) transfer | Δτ -0.061 [-0.065, -0.057]; τa 0.467, τb 0.528; P(Δτ>0) 0.000; B=400 | `same-window/eval_summary.json` : `contrasts[4]` |
| [hybrid] S-PR allowance minus C-PR (l=1) allowance | Δτ -0.191 [-0.198, -0.184]; τa 0.320, τb 0.512; P(Δτ>0) 0.000; B=400 | `same-window/eval_summary.json` : `contrasts[5]` |
| [hybrid] S-PR sybil minus C-PR (l=0) sybil | Δτ -0.013 [-0.015, -0.011]; τa 0.298, τb 0.311; P(Δτ>0) 0.000; B=400 | `same-window/eval_summary.json` : `contrasts[6]` |
| [hybrid] S-PR sybil minus C-PR (l=1) sybil | Δτ 0.278 [0.269, 0.285]; τa 0.298, τb 0.020; P(Δτ>0) 1.000; B=400 | `same-window/eval_summary.json` : `contrasts[7]` |
| [hybrid_single] C-PR transfer minus AWP transfer | Δτ -0.151 [-0.159, -0.142]; τa 0.296, τb 0.447; P(Δτ>0) 0.000; B=400 | `same-window/eval_summary.json` : `contrasts[8]` |
| [hybrid_single] C-PR allowance minus EndorseRank allowance | Δτ -0.063 [-0.069, -0.058]; τa 0.418, τb 0.481; P(Δτ>0) 0.000; B=400 | `same-window/eval_summary.json` : `contrasts[9]` |
| [hybrid_single] C-PR sybil minus AWP sybil | Δτ -0.182 [-0.189, -0.175]; τa 0.129, τb 0.311; P(Δτ>0) 0.000; B=400 | `same-window/eval_summary.json` : `contrasts[10]` |
| [hybrid_single] C-PR sybil minus EndorseRank sybil | Δτ 0.103 [0.099, 0.108]; τa 0.129, τb 0.025; P(Δτ>0) 1.000; B=400 | `same-window/eval_summary.json` : `contrasts[11]` |
| [er_awp] EndorseRank allowance minus EndorseRank transfer | Δτ 0.359 [0.351, 0.367]; τa 0.481, τb 0.122; P(Δτ>0) 1.000; B=400 | `same-window/eval_summary.json` : `contrasts[12]` |
| [er_awp] AWP transfer minus EndorseRank transfer | Δτ 0.325 [0.315, 0.335]; τa 0.447, τb 0.122; P(Δτ>0) 1.000; B=400 | `same-window/eval_summary.json` : `contrasts[13]` |
| [er_awp] EndorseRank allowance minus AWP allowance | Δτ 0.309 [0.300, 0.317]; τa 0.481, τb 0.173; P(Δτ>0) 1.000; B=400 | `same-window/eval_summary.json` : `contrasts[14]` |
| [er_awp] AWP sybil minus EndorseRank sybil | Δτ 0.285 [0.277, 0.294]; τa 0.311, τb 0.025; P(Δτ>0) 1.000; B=400 | `same-window/eval_summary.json` : `contrasts[15]` |
| [er_awp] EndorseRank in-approve degree minus EndorseRank in-degree | Δτ 0.430 [0.421, 0.440]; τa 0.626, τb 0.196; P(Δτ>0) 1.000; B=400 | `same-window/eval_summary.json` : `contrasts[16]` |
| EndorseRank vs AWP, τ_b | 0.217 [0.209, 0.225]; B=400 | `same-window/eval_summary.json` : `inter_method.endorserank_vs_awp` |
| EndorseRank vs AWP, isolated-node rule | 0.217 [0.209, 0.225]; B=400 | `same-window/eval_summary.json` : `inter_method.isolated` |
| Concordance: pairs | 387,630,246 | `same-window/eval_summary.json` : `inter_method.concordance.pairs` |
| Concordance: ordered by both | 381,636,156 | `same-window/eval_summary.json` : `inter_method.concordance.ordered_by_both` |
| Concordance: share ordered by both | 0.985 | `same-window/eval_summary.json` : `inter_method.concordance.share_ordered_by_both` |
| Concordance: discordant share of ordered | 0.390 | `same-window/eval_summary.json` : `inter_method.concordance.discordant_share_of_ordered` |
| Concordance: tau b | 0.217 | `same-window/eval_summary.json` : `inter_method.concordance.tau_b` |
| Rule A secondary, transfer: better layer C-PR (λ=0) | C-PR 0.296 vs interval [0.522, 0.534]; pass: no | `same-window/eval_summary.json` : `rule_a_secondary.transfer` |
| Rule A secondary, allowance: better layer C-PR (λ=1) | C-PR 0.418 vs interval [0.506, 0.517]; pass: no | `same-window/eval_summary.json` : `rule_a_secondary.allowance` |
| Rule A secondary, Sybil stability: C-PR above both layers | C-PR 0.129, λ=1 0.020, λ=0 0.311; pass: no | `same-window/eval_summary.json` : `rule_a_secondary.sybil_stability` |
| Rule A secondary part met | no | `same-window/eval_summary.json` : `rule_a_secondary.pass` |

## 4. Ties and the isolated-node rule

| Quantity | Value | Source |
|---|---|---|
| EndorseRank ties (same window) | distinct 25,650 of 27,844; zeros 962; largest block 962 at 0.000; share of pairs tied 0.0015 | `same-window/eval_summary.json` : `ties.endorserank` |
| EndorseRank (activity restarts) ties (same window) | distinct 26,804 of 27,844; zeros 962; largest block 962 at 0.000; share of pairs tied 0.0012 | `same-window/eval_summary.json` : `ties.endorserank_activity` |
| AWP ties (same window) | distinct 24,545 of 27,844; zeros 3,297; largest block 3,297 at 0.000; share of pairs tied 0.0140 | `same-window/eval_summary.json` : `ties.awp` |
| C-PR (λ=1) ties (same window) | distinct 18,868 of 27,844; zeros 962; largest block 2,891 at 3.38e-08; share of pairs tied 0.0130 | `same-window/eval_summary.json` : `ties.cpr_l100` |
| C-PR (λ=0) ties (same window) | distinct 23,734 of 27,844; zeros 3,297; largest block 3,297 at 0.000; share of pairs tied 0.0144 | `same-window/eval_summary.json` : `ties.cpr_l0` |
| C-PR (λ=0.25) ties (same window) | distinct 26,875 of 27,844; zeros 138; largest block 247 at 1.173e-08; share of pairs tied 0.0001452 | `same-window/eval_summary.json` : `ties.cpr_l25` |
| C-PR (λ=0.5) ties (same window) | distinct 26,850 of 27,844; zeros 138; largest block 251 at 1.232e-08; share of pairs tied 0.0001463 | `same-window/eval_summary.json` : `ties.cpr_l50` |
| C-PR (λ=0.75) ties (same window) | distinct 26,855 of 27,844; zeros 138; largest block 247 at 1.284e-08; share of pairs tied 0.0001456 | `same-window/eval_summary.json` : `ties.cpr_l75` |
| S-PR ties (same window) | distinct 24,275 of 27,844; zeros 3,305; largest block 3,305 at 0.000; share of pairs tied 0.0141 | `same-window/eval_summary.json` : `ties.spr` |
| endorserank_iso (missing contracts as isolated nodes), transfer | 0.122 [0.113, 0.129]; B=400 | `same-window/eval_summary.json` : `isolated_rule.endorserank_iso.transfer` |
| endorserank_iso (missing contracts as isolated nodes), allowance | 0.481 [0.476, 0.487]; B=400 | `same-window/eval_summary.json` : `isolated_rule.endorserank_iso.allowance` |
| endorserank_iso (missing contracts as isolated nodes), Sybil stability | 0.025 [0.019, 0.031]; B=400 | `same-window/eval_summary.json` : `isolated_rule.endorserank_iso.sybil_stability` |
| awp_iso (missing contracts as isolated nodes), transfer | 0.447 [0.440, 0.453]; B=400 | `same-window/eval_summary.json` : `isolated_rule.awp_iso.transfer` |
| awp_iso (missing contracts as isolated nodes), allowance | 0.173 [0.165, 0.180]; B=400 | `same-window/eval_summary.json` : `isolated_rule.awp_iso.allowance` |
| awp_iso (missing contracts as isolated nodes), Sybil stability | 0.311 [0.303, 0.317]; B=400 | `same-window/eval_summary.json` : `isolated_rule.awp_iso.sybil_stability` |
| EndorseRank ties (W0 spenders) | distinct 31,041 of 33,101; zeros 0; largest block 212 at 6.581e-08; share of pairs tied 0.0001004 | `holdout-w0/eval_summary.json` : `ties.endorserank` |
| AWP ties (W0 spenders) | distinct 28,433 of 33,101; zeros 3,753; largest block 3,753 at 0.000; share of pairs tied 0.0129 | `holdout-w0/eval_summary.json` : `ties.awp` |
| C-PR (λ=1) ties (W0 spenders) | distinct 20,843 of 33,101; zeros 0; largest block 2,795 at 3.536e-08; share of pairs tied 0.0098 | `holdout-w0/eval_summary.json` : `ties.cpr_l100` |

## 5. Closed-form check of EndorseRank, s(v) = c (1 + d δ(v))

| Quantity | Value | Source |
|---|---|---|
| Same window: common value c | 3.403e-08 | `same-window/eval_summary.json` : `closed_form.common_value_c` |
| Same window: spread of c | 1.0000 | `same-window/eval_summary.json` : `closed_form.spread_of_c` |
| Same window: spenders | 26,512 | `same-window/eval_summary.json` : `closed_form.spenders` |
| Same window: depth one spenders | 20,942 | `same-window/eval_summary.json` : `closed_form.depth_one_spenders` |
| Same window: within 1pct all | 0.8636 | `same-window/eval_summary.json` : `closed_form.within_1pct_all` |
| Same window: within 1pct depth one | 1.0000 | `same-window/eval_summary.json` : `closed_form.within_1pct_depth_one` |
| Same window: within 1pct deeper | 0.3506 | `same-window/eval_summary.json` : `closed_form.within_1pct_deeper` |
| Same window: tau score vs delta | 0.9080 | `same-window/eval_summary.json` : `closed_form.tau_score_vs_delta` |
| W0: common value c | 3.557e-08 | `holdout-w0/eval_summary.json` : `closed_form.common_value_c` |
| W0: spread of c | 1.0000 | `holdout-w0/eval_summary.json` : `closed_form.spread_of_c` |
| W0: spenders | 33,101 | `holdout-w0/eval_summary.json` : `closed_form.spenders` |
| W0: depth one spenders | 19,955 | `holdout-w0/eval_summary.json` : `closed_form.depth_one_spenders` |
| W0: within 1pct all | 0.7355 | `holdout-w0/eval_summary.json` : `closed_form.within_1pct_all` |
| W0: within 1pct depth one | 1.0000 | `holdout-w0/eval_summary.json` : `closed_form.within_1pct_depth_one` |
| W0: within 1pct deeper | 0.3341 | `holdout-w0/eval_summary.json` : `closed_form.within_1pct_deeper` |
| W0: tau score vs delta | 0.7877 | `holdout-w0/eval_summary.json` : `closed_form.tau_score_vs_delta` |

## 6. Holdout W0 (scores at t1, labels April to June 2026)

| Quantity | Value | Source |
|---|---|---|
| Freeze t1 | 2026-03-31 23:59:59 UTC | `holdout-w0/eval_summary.json` : `freeze` |
| Label window | 2026-04-01 00:00:00 UTC to 2026-06-30 23:59:59 UTC | `holdout-w0/eval_summary.json` : `labels` |
| Spenders with a positive latest allowance at t1, account type contract | 33,101 | `holdout-w0/eval_summary.json` : `spender_account_types.contract` |
| Spenders with a positive latest allowance at t1, account type none | 431 | `holdout-w0/eval_summary.json` : `spender_account_types.none` |
| Spenders with a positive latest allowance at t1, account type eip7702 | 24 | `holdout-w0/eval_summary.json` : `spender_account_types.eip7702` |
| Spender cohort (contracts) | 33,101 | `holdout-w0/eval_summary.json` : `spenders` |
| Gained a new approval pair | 3,403 | `holdout-w0/eval_summary.json` : `gained_new_approvals` |
| Gained a new transfer sender | 3,042 | `holdout-w0/eval_summary.json` : `gained_new_senders` |

### W0 spenders: τ_b with every label

| Quantity | Value | Source |
|---|---|---|
| EndorseRank, new approval pairs | 0.241 [0.234, 0.248]; B=400 | `holdout-w0/eval_summary.json` : `taus.endorserank.future_new_approvers` |
| EndorseRank, new transfer senders | 0.226 [0.219, 0.234]; B=400 | `holdout-w0/eval_summary.json` : `taus.endorserank.future_new_transfer_senders` |
| EndorseRank, revocations | 0.320 [0.313, 0.327]; B=400 | `holdout-w0/eval_summary.json` : `taus.endorserank.future_revoke_count` |
| EndorseRank, drained owners | 0.245 [0.237, 0.252]; B=400 | `holdout-w0/eval_summary.json` : `taus.endorserank.future_drain_owners` |
| EndorseRank (activity restarts), new approval pairs | 0.295 [0.288, 0.302]; B=400 | `holdout-w0/eval_summary.json` : `taus.endorserank_activity.future_new_approvers` |
| EndorseRank (activity restarts), new transfer senders | 0.272 [0.265, 0.280]; B=400 | `holdout-w0/eval_summary.json` : `taus.endorserank_activity.future_new_transfer_senders` |
| EndorseRank (activity restarts), revocations | 0.283 [0.276, 0.291]; B=400 | `holdout-w0/eval_summary.json` : `taus.endorserank_activity.future_revoke_count` |
| EndorseRank (activity restarts), drained owners | 0.314 [0.307, 0.319]; B=400 | `holdout-w0/eval_summary.json` : `taus.endorserank_activity.future_drain_owners` |
| AWP, new approval pairs | 0.196 [0.187, 0.206]; B=400 | `holdout-w0/eval_summary.json` : `taus.awp.future_new_approvers` |
| AWP, new transfer senders | 0.340 [0.333, 0.348]; B=400 | `holdout-w0/eval_summary.json` : `taus.awp.future_new_transfer_senders` |
| AWP, revocations | 0.204 [0.193, 0.214]; B=400 | `holdout-w0/eval_summary.json` : `taus.awp.future_revoke_count` |
| AWP, drained owners | 0.201 [0.191, 0.212]; B=400 | `holdout-w0/eval_summary.json` : `taus.awp.future_drain_owners` |
| C-PR (λ=1), new approval pairs | 0.228 [0.219, 0.236]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l100.future_new_approvers` |
| C-PR (λ=1), new transfer senders | 0.122 [0.113, 0.133]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l100.future_new_transfer_senders` |
| C-PR (λ=1), revocations | 0.319 [0.312, 0.326]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l100.future_revoke_count` |
| C-PR (λ=1), drained owners | 0.216 [0.208, 0.225]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l100.future_drain_owners` |
| C-PR (λ=0), new approval pairs | 0.142 [0.133, 0.151]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l0.future_new_approvers` |
| C-PR (λ=0), new transfer senders | 0.254 [0.246, 0.262]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l0.future_new_transfer_senders` |
| C-PR (λ=0), revocations | 0.196 [0.185, 0.206]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l0.future_revoke_count` |
| C-PR (λ=0), drained owners | 0.131 [0.121, 0.141]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l0.future_drain_owners` |
| C-PR (λ=0.25), new approval pairs | 0.234 [0.227, 0.241]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l25.future_new_approvers` |
| C-PR (λ=0.25), new transfer senders | 0.230 [0.222, 0.240]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l25.future_new_transfer_senders` |
| C-PR (λ=0.25), revocations | 0.307 [0.300, 0.314]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l25.future_revoke_count` |
| C-PR (λ=0.25), drained owners | 0.223 [0.215, 0.231]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l25.future_drain_owners` |
| C-PR (λ=0.5), new approval pairs | 0.236 [0.229, 0.243]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l50.future_new_approvers` |
| C-PR (λ=0.5), new transfer senders | 0.224 [0.216, 0.234]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l50.future_new_transfer_senders` |
| C-PR (λ=0.5), revocations | 0.310 [0.304, 0.317]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l50.future_revoke_count` |
| C-PR (λ=0.5), drained owners | 0.225 [0.218, 0.233]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l50.future_drain_owners` |
| C-PR (λ=0.75), new approval pairs | 0.236 [0.229, 0.243]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l75.future_new_approvers` |
| C-PR (λ=0.75), new transfer senders | 0.217 [0.209, 0.226]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l75.future_new_transfer_senders` |
| C-PR (λ=0.75), revocations | 0.311 [0.305, 0.318]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l75.future_revoke_count` |
| C-PR (λ=0.75), drained owners | 0.225 [0.217, 0.233]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l75.future_drain_owners` |
| S-PR, new approval pairs | 0.177 [0.167, 0.186]; B=400 | `holdout-w0/eval_summary.json` : `taus.spr.future_new_approvers` |
| S-PR, new transfer senders | 0.245 [0.236, 0.253]; B=400 | `holdout-w0/eval_summary.json` : `taus.spr.future_new_transfer_senders` |
| S-PR, revocations | 0.251 [0.242, 0.260]; B=400 | `holdout-w0/eval_summary.json` : `taus.spr.future_revoke_count` |
| S-PR, drained owners | 0.165 [0.156, 0.175]; B=400 | `holdout-w0/eval_summary.json` : `taus.spr.future_drain_owners` |
| in-approve degree at t1, new approval pairs | 0.252 [0.244, 0.260]; B=400 | `holdout-w0/eval_summary.json` : `taus.t1_in_approve_degree.future_new_approvers` |
| in-approve degree at t1, new transfer senders | 0.156 [0.148, 0.166]; B=400 | `holdout-w0/eval_summary.json` : `taus.t1_in_approve_degree.future_new_transfer_senders` |
| in-approve degree at t1, revocations | 0.388 [0.381, 0.395]; B=400 | `holdout-w0/eval_summary.json` : `taus.t1_in_approve_degree.future_revoke_count` |
| in-approve degree at t1, drained owners | 0.223 [0.215, 0.231]; B=400 | `holdout-w0/eval_summary.json` : `taus.t1_in_approve_degree.future_drain_owners` |
| transfer in-degree at t1, new approval pairs | 0.148 [0.138, 0.158]; B=400 | `holdout-w0/eval_summary.json` : `taus.t1_in_degree.future_new_approvers` |
| transfer in-degree at t1, new transfer senders | 0.302 [0.294, 0.310]; B=400 | `holdout-w0/eval_summary.json` : `taus.t1_in_degree.future_new_transfer_senders` |
| transfer in-degree at t1, revocations | 0.231 [0.220, 0.242]; B=400 | `holdout-w0/eval_summary.json` : `taus.t1_in_degree.future_revoke_count` |
| transfer in-degree at t1, drained owners | 0.125 [0.115, 0.135]; B=400 | `holdout-w0/eval_summary.json` : `taus.t1_in_degree.future_drain_owners` |

### W0 contrasts

| Quantity | Value | Source |
|---|---|---|
| [contrasts_prefixed] C-PR minus C-PR (l=1), new approval pairs | Δτ 0.008 [0.003, 0.013]; τa 0.236, τb 0.228; P(Δτ>0) 1.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_prefixed[0]` |
| [contrasts_prefixed] C-PR minus C-PR (l=0), new transfer senders | Δτ -0.030 [-0.034, -0.026]; τa 0.224, τb 0.254; P(Δτ>0) 0.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_prefixed[1]` |
| [contrasts_after] C-PR (l=1) minus t1 in-approve degree, new approval pairs | Δτ -0.025 [-0.030, -0.019]; τa 0.228, τb 0.252; P(Δτ>0) 0.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_after[0]` |
| [contrasts_after] S-PR minus C-PR (l=1), new approval pairs | Δτ -0.051 [-0.060, -0.043]; τa 0.177, τb 0.228; P(Δτ>0) 0.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_after[1]` |
| [contrasts_after] S-PR minus C-PR (l=0), new transfer senders | Δτ -0.009 [-0.012, -0.006]; τa 0.245, τb 0.254; P(Δτ>0) 0.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_after[2]` |
| [contrasts_after] EndorseRank minus t1 in-approve degree, new approval pairs | Δτ -0.011 [-0.016, -0.006]; τa 0.241, τb 0.252; P(Δτ>0) 0.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_after[3]` |
| [contrasts_after] AWP minus t1 in-degree, new transfer senders | Δτ 0.038 [0.035, 0.042]; τa 0.340, τb 0.302; P(Δτ>0) 1.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_after[4]` |
| [contrasts_after] C-PR minus C-PR (l=0), new approval pairs | Δτ 0.094 [0.085, 0.103]; τa 0.236, τb 0.142; P(Δτ>0) 1.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_after[5]` |
| [contrasts_after] C-PR minus EndorseRank, new approval pairs | Δτ -0.005 [-0.010, -0.000491]; τa 0.236, τb 0.241; P(Δτ>0) 0.025; B=400 | `holdout-w0/eval_summary.json` : `contrasts_after[6]` |
| [contrasts_after] C-PR minus AWP, new transfer senders | Δτ -0.116 [-0.122, -0.109]; τa 0.224, τb 0.340; P(Δτ>0) 0.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_after[7]` |
| [contrasts_after] C-PR minus AWP, new approval pairs | Δτ 0.039 [0.029, 0.049]; τa 0.236, τb 0.196; P(Δτ>0) 1.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_after[8]` |
| [contrasts_after] EndorseRank minus AWP, new approval pairs | Δτ 0.045 [0.033, 0.055]; τa 0.241, τb 0.196; P(Δτ>0) 1.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_after[9]` |
| [contrasts_after] EndorseRank minus AWP, new transfer senders | Δτ -0.114 [-0.120, -0.108]; τa 0.226, τb 0.340; P(Δτ>0) 0.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_after[10]` |

### Rule A, primary part

| Quantity | Value | Source |
|---|---|---|
| Rule A primary: no worse on new approvals | yes | `holdout-w0/eval_summary.json` : `rule_a_primary.no_worse_on_new_approvals` |
| Rule A primary: better on new senders | no | `holdout-w0/eval_summary.json` : `rule_a_primary.better_on_new_senders` |
| Rule A primary: pass | no | `holdout-w0/eval_summary.json` : `rule_a_primary.pass` |

### Spenders that had received a transfer before t1

| Quantity | Value | Source |
|---|---|---|
| Receiving subset (contracts) | 29,228 | `holdout-w0/eval_summary.json` : `receiving.n` |
| Receiving: EndorseRank, new approval pairs | 0.249 [0.241, 0.256]; B=400 | `holdout-w0/eval_summary.json` : `receiving.taus.endorserank.future_new_approvers` |
| Receiving: EndorseRank, new transfer senders | 0.247 [0.240, 0.255]; B=400 | `holdout-w0/eval_summary.json` : `receiving.taus.endorserank.future_new_transfer_senders` |
| Receiving: AWP, new approval pairs | 0.262 [0.253, 0.270]; B=400 | `holdout-w0/eval_summary.json` : `receiving.taus.awp.future_new_approvers` |
| Receiving: AWP, new transfer senders | 0.349 [0.342, 0.356]; B=400 | `holdout-w0/eval_summary.json` : `receiving.taus.awp.future_new_transfer_senders` |
| Receiving: in-approve degree at t1, new approval pairs | 0.256 [0.248, 0.265]; B=400 | `holdout-w0/eval_summary.json` : `receiving.taus.t1_in_approve_degree.future_new_approvers` |
| Receiving: in-approve degree at t1, new transfer senders | 0.168 [0.158, 0.177]; B=400 | `holdout-w0/eval_summary.json` : `receiving.taus.t1_in_approve_degree.future_new_transfer_senders` |
| Receiving: transfer in-degree at t1, new approval pairs | 0.202 [0.192, 0.211]; B=400 | `holdout-w0/eval_summary.json` : `receiving.taus.t1_in_degree.future_new_approvers` |
| Receiving: transfer in-degree at t1, new transfer senders | 0.304 [0.295, 0.311]; B=400 | `holdout-w0/eval_summary.json` : `receiving.taus.t1_in_degree.future_new_transfer_senders` |
| Receiving: EndorseRank minus t1 in-approve degree, new approval pairs | Δτ -0.007 [-0.012, -0.002]; τa 0.249, τb 0.256; P(Δτ>0) 0.003; B=400 | `holdout-w0/eval_summary.json` : `receiving.contrasts[0]` |
| Receiving: AWP minus t1 in-degree, new transfer senders | Δτ 0.046 [0.041, 0.051]; τa 0.349, τb 0.304; P(Δτ>0) 1.000; B=400 | `holdout-w0/eval_summary.json` : `receiving.contrasts[1]` |

### Coverage (AWP = 0 means no transfer edge)

| Quantity | Value | Source |
|---|---|---|
| spenders without transfer edge | 3,753 | `holdout-w0/eval_summary.json` : `coverage.spenders_without_transfer_edge` |
| share gaining approvals without | 0.119 | `holdout-w0/eval_summary.json` : `coverage.share_gaining_approvals_without` |
| share gaining approvals with | 0.101 | `holdout-w0/eval_summary.json` : `coverage.share_gaining_approvals_with` |
| share gaining senders without | 0.003 | `holdout-w0/eval_summary.json` : `coverage.share_gaining_senders_without` |
| share gaining senders with | 0.103 | `holdout-w0/eval_summary.json` : `coverage.share_gaining_senders_with` |

### W0 traders (exploratory)

| Quantity | Value | Source |
|---|---|---|
| Traders (GMX V2 contract accounts, ≥3 closes) | 88 | `holdout-w0/eval_summary.json` : `traders.n` |
| Traders that had received an approval by t1 | 40 | `holdout-w0/eval_summary.json` : `traders.with_any_approval_received` |
| Traders: EndorseRank, profitable closes | 0.156 [-0.022, 0.302]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.endorserank.profitable_closes` |
| Traders: EndorseRank, realized gain | 0.088 [-0.079, 0.242]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.endorserank.realized_gain` |
| Traders: EndorseRank, profitable share | -0.053 [-0.186, 0.082]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.endorserank.profitable_share` |
| Traders: EndorseRank, non-loss share | -0.170 [-0.286, -0.044]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.endorserank.non_loss_share` |
| Traders: EndorseRank (activity restarts), profitable closes | 0.122 [-0.037, 0.249]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.endorserank_activity.profitable_closes` |
| Traders: EndorseRank (activity restarts), realized gain | 0.087 [-0.080, 0.243]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.endorserank_activity.realized_gain` |
| Traders: EndorseRank (activity restarts), profitable share | -0.076 [-0.209, 0.059]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.endorserank_activity.profitable_share` |
| Traders: EndorseRank (activity restarts), non-loss share | -0.186 [-0.321, -0.050]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.endorserank_activity.non_loss_share` |
| Traders: AWP, profitable closes | 0.138 [-0.020, 0.281]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.awp.profitable_closes` |
| Traders: AWP, realized gain | 0.134 [-0.018, 0.283]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.awp.realized_gain` |
| Traders: AWP, profitable share | -0.170 [-0.299, -0.032]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.awp.profitable_share` |
| Traders: AWP, non-loss share | -0.253 [-0.384, -0.112]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.awp.non_loss_share` |
| Traders: C-PR (λ=1), profitable closes | 0.077 [-0.076, 0.217]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l100.profitable_closes` |
| Traders: C-PR (λ=1), realized gain | 0.044 [-0.122, 0.211]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l100.realized_gain` |
| Traders: C-PR (λ=1), profitable share | -0.071 [-0.234, 0.074]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l100.profitable_share` |
| Traders: C-PR (λ=1), non-loss share | -0.175 [-0.309, -0.028]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l100.non_loss_share` |
| Traders: C-PR (λ=0), profitable closes | 0.042 [-0.088, 0.182]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l0.profitable_closes` |
| Traders: C-PR (λ=0), realized gain | 0.092 [-0.056, 0.240]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l0.realized_gain` |
| Traders: C-PR (λ=0), profitable share | -0.067 [-0.205, 0.074]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l0.profitable_share` |
| Traders: C-PR (λ=0), non-loss share | -0.028 [-0.170, 0.117]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l0.non_loss_share` |
| Traders: C-PR (λ=0.25), profitable closes | 0.035 [-0.095, 0.177]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l25.profitable_closes` |
| Traders: C-PR (λ=0.25), realized gain | 0.081 [-0.069, 0.236]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l25.realized_gain` |
| Traders: C-PR (λ=0.25), profitable share | -0.069 [-0.213, 0.075]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l25.profitable_share` |
| Traders: C-PR (λ=0.25), non-loss share | -0.006 [-0.149, 0.143]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l25.non_loss_share` |
| Traders: C-PR (λ=0.5), profitable closes | 0.042 [-0.092, 0.180]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l50.profitable_closes` |
| Traders: C-PR (λ=0.5), realized gain | 0.085 [-0.065, 0.231]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l50.realized_gain` |
| Traders: C-PR (λ=0.5), profitable share | -0.064 [-0.211, 0.075]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l50.profitable_share` |
| Traders: C-PR (λ=0.5), non-loss share | 0.000 [-0.144, 0.144]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l50.non_loss_share` |
| Traders: C-PR (λ=0.75), profitable closes | 0.048 [-0.088, 0.180]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l75.profitable_closes` |
| Traders: C-PR (λ=0.75), realized gain | 0.086 [-0.067, 0.236]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l75.realized_gain` |
| Traders: C-PR (λ=0.75), profitable share | -0.062 [-0.211, 0.075]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l75.profitable_share` |
| Traders: C-PR (λ=0.75), non-loss share | 0.002 [-0.146, 0.144]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.cpr_l75.non_loss_share` |
| Traders: S-PR, profitable closes | 0.055 [-0.072, 0.211]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.spr.profitable_closes` |
| Traders: S-PR, realized gain | 0.072 [-0.088, 0.225]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.spr.realized_gain` |
| Traders: S-PR, profitable share | -0.025 [-0.164, 0.110]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.spr.profitable_share` |
| Traders: S-PR, non-loss share | -0.069 [-0.215, 0.088]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.spr.non_loss_share` |
| Traders: in-approve degree at t1, profitable closes | 0.083 [-0.103, 0.238]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.t1_in_approve_degree.profitable_closes` |
| Traders: in-approve degree at t1, realized gain | 0.024 [-0.154, 0.202]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.t1_in_approve_degree.realized_gain` |
| Traders: in-approve degree at t1, profitable share | -0.146 [-0.317, 0.029]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.t1_in_approve_degree.profitable_share` |
| Traders: in-approve degree at t1, non-loss share | -0.278 [-0.431, -0.119]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.t1_in_approve_degree.non_loss_share` |
| Traders: transfer in-degree at t1, profitable closes | -0.022 [-0.166, 0.134]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.t1_in_degree.profitable_closes` |
| Traders: transfer in-degree at t1, realized gain | -0.020 [-0.168, 0.153]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.t1_in_degree.realized_gain` |
| Traders: transfer in-degree at t1, profitable share | -0.198 [-0.332, -0.053]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.t1_in_degree.profitable_share` |
| Traders: transfer in-degree at t1, non-loss share | -0.190 [-0.344, -0.036]; B=400 | `holdout-w0/eval_summary.json` : `traders.taus.t1_in_degree.non_loss_share` |

## 7. Registered window W1 (scores at T_obs, labels July to September 2026)

| Quantity | Value | Source |
|---|---|---|
| Margin δ | 0.010 | `registered-w1/eval_summary.json` : `delta` |
| Spender cohort (contracts) | 34,587 | `registered-w1/eval_summary.json` : `spenders` |
| Gained a new approval pair | 2,850 | `registered-w1/eval_summary.json` : `gained_new_approvals` |
| Gained a new transfer sender | 2,812 | `registered-w1/eval_summary.json` : `gained_new_senders` |
| Traders (GMX V2 contract accounts, ≥3 closes) | 70 | `registered-w1/eval_summary.json` : `traders` |
| Traders with at least one liquidation | 9 | `registered-w1/eval_summary.json` : `traders_liquidated` |
| Traders whose every close was a liquidation | 1 | `registered-w1/eval_summary.json` : `traders_all_liquidated` |

### Rule B (comparator C-PR λ=0)

| Quantity | Value | Source |
|---|---|---|
| Rule B (comparator C-PR λ=0): F1 | Δτ 0.101 [0.092, 0.111]; τa 0.237, τb 0.136; P(Δτ>0) 1.000; B=400; superiority: holds | `registered-w1/eval_summary.json` : `rule_b.F1` |
| Rule B (comparator C-PR λ=0): F2 | Δτ -0.025 [-0.029, -0.021]; τa 0.235, τb 0.260; P(Δτ>0) 0.000; B=400; non_inferiority: fails | `registered-w1/eval_summary.json` : `rule_b.F2` |
| Rule B (comparator C-PR λ=0): F3 | Δτ -0.044 [-0.100, -0.002]; τa 0.095, τb 0.138; P(Δτ>0) 0.010; B=400; non_inferiority: fails | `registered-w1/eval_summary.json` : `rule_b.F3` |
| Rule B (comparator C-PR λ=0): F4 | Δτ -0.044 [-0.100, -0.002]; τa 0.095, τb 0.138; P(Δτ>0) 0.010; B=400; superiority: fails | `registered-w1/eval_summary.json` : `rule_b.F4` |
| Rule B (comparator C-PR λ=0): decision | no | `registered-w1/eval_summary.json` : `rule_b.decision` |
| Rule B (comparator C-PR λ=0): F5 | Δτ -0.215 [-0.472, 0.062]; τa 0.095, τb 0.310; P(Δτ>0) 0.065; B=400; superiority: fails | `registered-w1/eval_summary.json` : `rule_b.F5` |
| Rule B (comparator C-PR λ=0): F6a | Δτ 0.010 [0.005, 0.014]; τa 0.237, τb 0.227; P(Δτ>0) 1.000; B=400; no_worse: holds | `registered-w1/eval_summary.json` : `rule_b.F6a` |
| Rule B (comparator C-PR λ=0): F6b | Δτ -0.025 [-0.029, -0.021]; τa 0.235, τb 0.260; P(Δτ>0) 0.000; B=400; superiority: fails | `registered-w1/eval_summary.json` : `rule_b.F6b` |
| Rule B (comparator C-PR λ=0): F6 | no | `registered-w1/eval_summary.json` : `rule_b.F6` |

### Sensitivity 1 (comparator AWP)

| Quantity | Value | Source |
|---|---|---|
| Sensitivity 1 (comparator AWP): F1 | Δτ 0.060 [0.050, 0.070]; τa 0.237, τb 0.177; P(Δτ>0) 1.000; B=400; superiority: holds | `registered-w1/eval_summary.json` : `sensitivity_awp.F1` |
| Sensitivity 1 (comparator AWP): F2 | Δτ -0.087 [-0.093, -0.082]; τa 0.235, τb 0.322; P(Δτ>0) 0.000; B=400; non_inferiority: fails | `registered-w1/eval_summary.json` : `sensitivity_awp.F2` |
| Sensitivity 1 (comparator AWP): F3 | Δτ -0.145 [-0.348, 0.043]; τa 0.095, τb 0.240; P(Δτ>0) 0.075; B=400; non_inferiority: fails | `registered-w1/eval_summary.json` : `sensitivity_awp.F3` |
| Sensitivity 1 (comparator AWP): F4 | Δτ -0.145 [-0.348, 0.043]; τa 0.095, τb 0.240; P(Δτ>0) 0.075; B=400; superiority: fails | `registered-w1/eval_summary.json` : `sensitivity_awp.F4` |
| Sensitivity 1 (comparator AWP): decision | no | `registered-w1/eval_summary.json` : `sensitivity_awp.decision` |

### Sensitivity 2 (isolated nodes)

| Quantity | Value | Source |
|---|---|---|
| Sensitivity 2 (isolated nodes): F1 | Δτ 0.101 [0.091, 0.111]; τa 0.237, τb 0.136; P(Δτ>0) 1.000; B=400; superiority: holds | `registered-w1/eval_summary.json` : `sensitivity_isolated.F1` |
| Sensitivity 2 (isolated nodes): F2 | Δτ -0.025 [-0.029, -0.022]; τa 0.235, τb 0.260; P(Δτ>0) 0.000; B=400; non_inferiority: fails | `registered-w1/eval_summary.json` : `sensitivity_isolated.F2` |
| Sensitivity 2 (isolated nodes): F3 | Δτ -0.044 [-0.100, -0.002]; τa 0.095, τb 0.138; P(Δτ>0) 0.010; B=400; non_inferiority: fails | `registered-w1/eval_summary.json` : `sensitivity_isolated.F3` |
| Sensitivity 2 (isolated nodes): F4 | Δτ -0.044 [-0.100, -0.002]; τa 0.095, τb 0.138; P(Δτ>0) 0.010; B=400; superiority: fails | `registered-w1/eval_summary.json` : `sensitivity_isolated.F4` |
| Sensitivity 2 (isolated nodes): decision | no | `registered-w1/eval_summary.json` : `sensitivity_isolated.decision` |
| Sensitivity 2 (isolated nodes): F5 | Δτ -0.227 [-0.426, -0.016]; τa 0.095, τb 0.322; P(Δτ>0) 0.018; B=400; superiority: fails | `registered-w1/eval_summary.json` : `sensitivity_isolated.F5` |
| Sensitivity 2 (isolated nodes): F6a | Δτ 0.010 [0.005, 0.014]; τa 0.237, τb 0.227; P(Δτ>0) 1.000; B=400; no_worse: holds | `registered-w1/eval_summary.json` : `sensitivity_isolated.F6a` |
| Sensitivity 2 (isolated nodes): F6b | Δτ -0.025 [-0.029, -0.022]; τa 0.235, τb 0.260; P(Δτ>0) 0.000; B=400; superiority: fails | `registered-w1/eval_summary.json` : `sensitivity_isolated.F6b` |
| Sensitivity 2 (isolated nodes): F6 | no | `registered-w1/eval_summary.json` : `sensitivity_isolated.F6` |

### W1 spenders and traders: τ_b

| Quantity | Value | Source |
|---|---|---|
| Spenders: EndorseRank, new approval pairs | 0.233 [0.226, 0.240]; B=400 | `registered-w1/eval_summary.json` : `spender_taus.endorserank.future_new_approvers` |
| Spenders: EndorseRank, new transfer senders | 0.210 [0.203, 0.217]; B=400 | `registered-w1/eval_summary.json` : `spender_taus.endorserank.future_new_transfer_senders` |
| Spenders: EndorseRank (activity restarts), new approval pairs | 0.280 [0.272, 0.287]; B=400 | `registered-w1/eval_summary.json` : `spender_taus.endorserank_activity.future_new_approvers` |
| Spenders: EndorseRank (activity restarts), new transfer senders | 0.245 [0.237, 0.252]; B=400 | `registered-w1/eval_summary.json` : `spender_taus.endorserank_activity.future_new_transfer_senders` |
| Spenders: AWP, new approval pairs | 0.177 [0.166, 0.187]; B=400 | `registered-w1/eval_summary.json` : `spender_taus.awp.future_new_approvers` |
| Spenders: AWP, new transfer senders | 0.322 [0.316, 0.329]; B=400 | `registered-w1/eval_summary.json` : `spender_taus.awp.future_new_transfer_senders` |
| Spenders: C-PR (λ=1), new approval pairs | 0.227 [0.219, 0.234]; B=400 | `registered-w1/eval_summary.json` : `spender_taus.cpr_l100.future_new_approvers` |
| Spenders: C-PR (λ=1), new transfer senders | 0.133 [0.125, 0.142]; B=400 | `registered-w1/eval_summary.json` : `spender_taus.cpr_l100.future_new_transfer_senders` |
| Spenders: C-PR (λ=0), new approval pairs | 0.136 [0.125, 0.145]; B=400 | `registered-w1/eval_summary.json` : `spender_taus.cpr_l0.future_new_approvers` |
| Spenders: C-PR (λ=0), new transfer senders | 0.260 [0.252, 0.266]; B=400 | `registered-w1/eval_summary.json` : `spender_taus.cpr_l0.future_new_transfer_senders` |
| Spenders: C-PR (λ=0.25), new approval pairs | 0.235 [0.228, 0.242]; B=400 | `registered-w1/eval_summary.json` : `spender_taus.cpr_l25.future_new_approvers` |
| Spenders: C-PR (λ=0.25), new transfer senders | 0.240 [0.232, 0.247]; B=400 | `registered-w1/eval_summary.json` : `spender_taus.cpr_l25.future_new_transfer_senders` |
| Spenders: C-PR (λ=0.5), new approval pairs | 0.237 [0.230, 0.244]; B=400 | `registered-w1/eval_summary.json` : `spender_taus.cpr_l50.future_new_approvers` |
| Spenders: C-PR (λ=0.5), new transfer senders | 0.235 [0.227, 0.243]; B=400 | `registered-w1/eval_summary.json` : `spender_taus.cpr_l50.future_new_transfer_senders` |
| Spenders: C-PR (λ=0.75), new approval pairs | 0.237 [0.230, 0.244]; B=400 | `registered-w1/eval_summary.json` : `spender_taus.cpr_l75.future_new_approvers` |
| Spenders: C-PR (λ=0.75), new transfer senders | 0.228 [0.220, 0.236]; B=400 | `registered-w1/eval_summary.json` : `spender_taus.cpr_l75.future_new_transfer_senders` |
| Spenders: S-PR, new approval pairs | 0.169 [0.159, 0.178]; B=400 | `registered-w1/eval_summary.json` : `spender_taus.spr.future_new_approvers` |
| Spenders: S-PR, new transfer senders | 0.251 [0.244, 0.258]; B=400 | `registered-w1/eval_summary.json` : `spender_taus.spr.future_new_transfer_senders` |
| Spenders: in-approve degree at the freeze, new approval pairs | 0.262 [0.255, 0.269]; B=400 | `registered-w1/eval_summary.json` : `spender_taus.in_approve_degree.future_new_approvers` |
| Spenders: in-approve degree at the freeze, new transfer senders | 0.179 [0.171, 0.186]; B=400 | `registered-w1/eval_summary.json` : `spender_taus.in_approve_degree.future_new_transfer_senders` |
| Spenders: transfer in-degree at the freeze, new approval pairs | 0.145 [0.135, 0.155]; B=400 | `registered-w1/eval_summary.json` : `spender_taus.in_degree.future_new_approvers` |
| Spenders: transfer in-degree at the freeze, new transfer senders | 0.303 [0.296, 0.309]; B=400 | `registered-w1/eval_summary.json` : `spender_taus.in_degree.future_new_transfer_senders` |
| Traders: EndorseRank, liquidation-free close rate | 0.306 [0.176, 0.421]; B=400 | `registered-w1/eval_summary.json` : `trader_taus.endorserank` |
| Traders: EndorseRank (activity restarts), liquidation-free close rate | 0.291 [0.162, 0.410]; B=400 | `registered-w1/eval_summary.json` : `trader_taus.endorserank_activity` |
| Traders: AWP, liquidation-free close rate | 0.240 [0.090, 0.362]; B=400 | `registered-w1/eval_summary.json` : `trader_taus.awp` |
| Traders: C-PR (λ=1), liquidation-free close rate | 0.310 [0.181, 0.432]; B=400 | `registered-w1/eval_summary.json` : `trader_taus.cpr_l100` |
| Traders: C-PR (λ=0), liquidation-free close rate | 0.138 [-0.048, 0.310]; B=400 | `registered-w1/eval_summary.json` : `trader_taus.cpr_l0` |
| Traders: C-PR (λ=0.25), liquidation-free close rate | 0.101 [-0.096, 0.280]; B=400 | `registered-w1/eval_summary.json` : `trader_taus.cpr_l25` |
| Traders: C-PR (λ=0.5), liquidation-free close rate | 0.095 [-0.102, 0.274]; B=400 | `registered-w1/eval_summary.json` : `trader_taus.cpr_l50` |
| Traders: C-PR (λ=0.75), liquidation-free close rate | 0.088 [-0.110, 0.269]; B=400 | `registered-w1/eval_summary.json` : `trader_taus.cpr_l75` |
| Traders: S-PR, liquidation-free close rate | 0.312 [0.183, 0.422]; B=400 | `registered-w1/eval_summary.json` : `trader_taus.spr` |
| Traders: in-approve degree at the freeze, liquidation-free close rate | 0.394 [0.261, 0.524]; B=400 | `registered-w1/eval_summary.json` : `trader_taus.in_approve_degree` |
| Traders: transfer in-degree at the freeze, liquidation-free close rate | 0.331 [0.209, 0.441]; B=400 | `registered-w1/eval_summary.json` : `trader_taus.in_degree` |

### EndorseRank results (not part of rule B)

| Quantity | Value | Source |
|---|---|---|
| endorserank minus degree appr | Δτ -0.029 [-0.032, -0.025]; τa 0.233, τb 0.262; P(Δτ>0) 0.000; B=400 | `registered-w1/eval_summary.json` : `endorserank_results.endorserank_minus_degree_appr` |
| awp minus degree send | Δτ 0.020 [0.016, 0.023]; τa 0.322, τb 0.303; P(Δτ>0) 1.000; B=400 | `registered-w1/eval_summary.json` : `endorserank_results.awp_minus_degree_send` |
| cpr minus endorserank appr | Δτ 0.004 [-0.0008016, 0.008]; τa 0.237, τb 0.233; P(Δτ>0) 0.925; B=400 | `registered-w1/eval_summary.json` : `endorserank_results.cpr_minus_endorserank_appr` |
| cpr minus endorserank liq | Δτ -0.211 [-0.466, 0.067]; τa 0.095, τb 0.306; P(Δτ>0) 0.068; B=400 | `registered-w1/eval_summary.json` : `endorserank_results.cpr_minus_endorserank_liq` |

### Comparison on outcomes built from neither edge type: rules R1-R3

| Quantity | Value | Source |
|---|---|---|
| Rule R1 | does not hold | `registered-w1/eval_summary.json` : `neutral_rules.R1` |
| Rule R2 | does not hold | `registered-w1/eval_summary.json` : `neutral_rules.R2` |
| Rule R3 | holds | `registered-w1/eval_summary.json` : `neutral_rules.R3` |

### Neutral labels, W1 (2,000 paired resamples)

| Quantity | Value | Source |
|---|---|---|
| W1 traders | 70 | `registered-w1/eval_summary.json` : `neutral_w1.n` |
| W1 highest in-approve degree among traders | 1.000 | `registered-w1/eval_summary.json` : `neutral_w1.max_in_approve_degree` |
| W1 P: in-approve degree minus transfer in-degree, liquidation-free close rate | Δτ 0.063 [-0.026, 0.148]; τa 0.394, τb 0.331; 97.5% [-0.040, 0.158]; P(Δτ>0) 0.907; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.grid.P.liquidation_free_rate` |
| W1 P: in-approve degree minus transfer in-degree, no liquidation | Δτ 0.057 [-0.031, 0.144]; τa 0.407, τb 0.350; P(Δτ>0) 0.889; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.grid.P.no_liquidation` |
| W1 P: in-approve degree minus transfer in-degree, profitable closes | Δτ -0.138 [-0.329, 0.043]; τa 0.042, τb 0.180; P(Δτ>0) 0.065; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.grid.P.profitable_closes` |
| W1 P: in-approve degree minus transfer in-degree, realized gain | Δτ -0.139 [-0.326, 0.056]; τa 0.033, τb 0.171; P(Δτ>0) 0.073; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.grid.P.realized_gain` |
| W1 P: in-approve degree minus transfer in-degree, profitable share | Δτ -0.226 [-0.421, -0.038]; τa -0.221, τb 0.004; P(Δτ>0) 0.009; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.grid.P.profitable_share` |
| W1 P: in-approve degree minus transfer in-degree, non-loss share | Δτ -0.272 [-0.444, -0.108]; τa -0.294, τb -0.022; P(Δτ>0) 0.000; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.grid.P.non_loss_share` |
| W1 Q: EndorseRank (activity restarts) minus AWP, liquidation-free close rate | Δτ 0.051 [-0.085, 0.213]; τa 0.291, τb 0.240; 97.5% [-0.104, 0.232]; P(Δτ>0) 0.732; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.grid.Q.liquidation_free_rate` |
| W1 Q: EndorseRank (activity restarts) minus AWP, no liquidation | Δτ 0.049 [-0.090, 0.222]; τa 0.297, τb 0.248; P(Δτ>0) 0.714; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.grid.Q.no_liquidation` |
| W1 Q: EndorseRank (activity restarts) minus AWP, profitable closes | Δτ -0.193 [-0.384, -0.0005762]; τa 0.087, τb 0.280; P(Δτ>0) 0.025; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.grid.Q.profitable_closes` |
| W1 Q: EndorseRank (activity restarts) minus AWP, realized gain | Δτ -0.294 [-0.454, -0.133]; τa 0.000, τb 0.294; P(Δτ>0) 0.0005; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.grid.Q.realized_gain` |
| W1 Q: EndorseRank (activity restarts) minus AWP, profitable share | Δτ -0.212 [-0.394, -0.030]; τa -0.146, τb 0.065; P(Δτ>0) 0.013; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.grid.Q.profitable_share` |
| W1 Q: EndorseRank (activity restarts) minus AWP, non-loss share | Δτ -0.301 [-0.465, -0.139]; τa -0.231, τb 0.071; P(Δτ>0) 0.000; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.grid.Q.non_loss_share` |
| W1 C-PR (λ=1) minus C-PR (λ=0), liquidation-free close rate | Δτ 0.171 [-0.083, 0.438]; τa 0.310, τb 0.138; P(Δτ>0) 0.904; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.grid.layers.liquidation_free_rate` |
| W1 C-PR (λ=1) minus C-PR (λ=0), no liquidation | Δτ 0.171 [-0.088, 0.450]; τa 0.316, τb 0.146; P(Δτ>0) 0.896; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.grid.layers.no_liquidation` |
| W1 C-PR (λ=1) minus C-PR (λ=0), profitable closes | Δτ -0.225 [-0.464, 0.021]; τa 0.004, τb 0.228; P(Δτ>0) 0.038; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.grid.layers.profitable_closes` |
| W1 C-PR (λ=1) minus C-PR (λ=0), realized gain | Δτ -0.414 [-0.640, -0.177]; τa -0.077, τb 0.336; P(Δτ>0) 0.002; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.grid.layers.realized_gain` |
| W1 C-PR (λ=1) minus C-PR (λ=0), profitable share | Δτ -0.375 [-0.620, -0.118]; τa -0.206, τb 0.168; P(Δτ>0) 0.002; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.grid.layers.profitable_share` |
| W1 C-PR (λ=1) minus C-PR (λ=0), non-loss share | Δτ -0.436 [-0.666, -0.180]; τa -0.287, τb 0.149; P(Δτ>0) 0.000; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.grid.layers.non_loss_share` |
| W1 EndorseRank minus AWP, liquidation-free close rate | Δτ 0.066 [-0.069, 0.227]; τa 0.306, τb 0.240; P(Δτ>0) 0.783; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.grid.er_awp.liquidation_free_rate` |
| W1 EndorseRank minus AWP, no liquidation | Δτ 0.064 [-0.078, 0.240]; τa 0.312, τb 0.248; P(Δτ>0) 0.765; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.grid.er_awp.no_liquidation` |
| W1 EndorseRank minus AWP, profitable closes | Δτ -0.186 [-0.370, -0.007]; τa 0.094, τb 0.280; P(Δτ>0) 0.021; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.grid.er_awp.profitable_closes` |
| W1 EndorseRank minus AWP, realized gain | Δτ -0.260 [-0.422, -0.096]; τa 0.034, τb 0.294; P(Δτ>0) 0.002; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.grid.er_awp.realized_gain` |
| W1 EndorseRank minus AWP, profitable share | Δτ -0.195 [-0.371, -0.020]; τa -0.129, τb 0.065; P(Δτ>0) 0.013; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.grid.er_awp.profitable_share` |
| W1 EndorseRank minus AWP, non-loss share | Δτ -0.308 [-0.461, -0.160]; τa -0.237, τb 0.071; P(Δτ>0) 0.000; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.grid.er_awp.non_loss_share` |
| W1 C-PR (λ=0) minus AWP, liquidation-free close rate | Δτ -0.101 [-0.273, 0.058]; τa 0.138, τb 0.240; P(Δτ>0) 0.115; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.grid.cpr0_awp.liquidation_free_rate` |
| W1 C-PR (λ=0) minus AWP, no liquidation | Δτ -0.102 [-0.283, 0.064]; τa 0.146, τb 0.248; P(Δτ>0) 0.120; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.grid.cpr0_awp.no_liquidation` |
| W1 C-PR (λ=0) minus AWP, profitable closes | Δτ -0.051 [-0.184, 0.062]; τa 0.228, τb 0.280; P(Δτ>0) 0.203; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.grid.cpr0_awp.profitable_closes` |
| W1 C-PR (λ=0) minus AWP, realized gain | Δτ 0.042 [-0.110, 0.198]; τa 0.336, τb 0.294; P(Δτ>0) 0.716; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.grid.cpr0_awp.realized_gain` |
| W1 C-PR (λ=0) minus AWP, profitable share | Δτ 0.103 [-0.044, 0.256]; τa 0.168, τb 0.065; P(Δτ>0) 0.920; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.grid.cpr0_awp.profitable_share` |
| W1 C-PR (λ=0) minus AWP, non-loss share | Δτ 0.078 [-0.065, 0.224]; τa 0.149, τb 0.071; P(Δτ>0) 0.857; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.grid.cpr0_awp.non_loss_share` |
| W1 EndorseRank minus in-approve degree, liquidation-free close rate | Δτ -0.088 [-0.166, 0.0009232]; τa 0.306, τb 0.394; P(Δτ>0) 0.026; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.grid.er_degree.liquidation_free_rate` |
| W1 EndorseRank minus in-approve degree, no liquidation | Δτ -0.095 [-0.173, -0.002]; τa 0.312, τb 0.407; P(Δτ>0) 0.021; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.grid.er_degree.no_liquidation` |
| W1 EndorseRank minus in-approve degree, profitable closes | Δτ 0.052 [-0.041, 0.145]; τa 0.094, τb 0.042; P(Δτ>0) 0.863; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.grid.er_degree.profitable_closes` |
| W1 EndorseRank minus in-approve degree, realized gain | Δτ 0.002 [-0.100, 0.101]; τa 0.034, τb 0.033; P(Δτ>0) 0.497; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.grid.er_degree.realized_gain` |
| W1 EndorseRank minus in-approve degree, profitable share | Δτ 0.092 [-0.016, 0.194]; τa -0.129, τb -0.221; P(Δτ>0) 0.959; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.grid.er_degree.profitable_share` |
| W1 EndorseRank minus in-approve degree, non-loss share | Δτ 0.057 [-0.041, 0.157]; τa -0.237, τb -0.294; P(Δτ>0) 0.879; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.grid.er_degree.non_loss_share` |
| W1 P: in-approve degree minus transfer in-degree, stratified by closes | Δτ 0.113 [-0.021, 0.238]; τa 0.381, τb 0.268 | `registered-w1/eval_summary.json` : `neutral_w1.stratified.P` |
| W1 Q: EndorseRank (activity restarts) minus AWP, stratified by closes | Δτ 0.110 [-0.114, 0.359]; τa 0.274, τb 0.165 | `registered-w1/eval_summary.json` : `neutral_w1.stratified.Q` |
| W1 recipients: n | 37 | `registered-w1/eval_summary.json` : `neutral_w1.recipients.recipients.n` |
| W1 recipients: share no liquidation | 1.000 | `registered-w1/eval_summary.json` : `neutral_w1.recipients.recipients.share_no_liquidation` |
| W1 recipients: mean liquidation free rate | 1.000 | `registered-w1/eval_summary.json` : `neutral_w1.recipients.recipients.mean_liquidation_free_rate` |
| W1 recipients: mean profitable share | 0.325 | `registered-w1/eval_summary.json` : `neutral_w1.recipients.recipients.mean_profitable_share` |
| W1 recipients: mean non loss share | 0.433 | `registered-w1/eval_summary.json` : `neutral_w1.recipients.recipients.mean_non_loss_share` |
| W1 recipients: median closes | 24.000 | `registered-w1/eval_summary.json` : `neutral_w1.recipients.recipients.median_closes` |
| W1 others: n | 33 | `registered-w1/eval_summary.json` : `neutral_w1.recipients.others.n` |
| W1 others: share no liquidation | 0.727 | `registered-w1/eval_summary.json` : `neutral_w1.recipients.others.share_no_liquidation` |
| W1 others: mean liquidation free rate | 0.878 | `registered-w1/eval_summary.json` : `neutral_w1.recipients.others.mean_liquidation_free_rate` |
| W1 others: mean profitable share | 0.479 | `registered-w1/eval_summary.json` : `neutral_w1.recipients.others.mean_profitable_share` |
| W1 others: mean non loss share | 0.644 | `registered-w1/eval_summary.json` : `neutral_w1.recipients.others.mean_non_loss_share` |
| W1 others: median closes | 11.000 | `registered-w1/eval_summary.json` : `neutral_w1.recipients.others.median_closes` |
| W1 P without the ten recipients of highest in-approve degree | Δτ 0.047 [-0.056, 0.152]; τa 0.366, τb 0.319; P(Δτ>0) 0.782; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.influence_without_top10` |
| W1 EndorseRank, liquidation-free close rate | 0.306 [0.177, 0.421]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.endorserank.liquidation_free_rate` |
| W1 EndorseRank, no liquidation | 0.312 [0.178, 0.432]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.endorserank.no_liquidation` |
| W1 EndorseRank, profitable closes | 0.094 [-0.086, 0.277]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.endorserank.profitable_closes` |
| W1 EndorseRank, realized gain | 0.034 [-0.158, 0.225]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.endorserank.realized_gain` |
| W1 EndorseRank, profitable share | -0.129 [-0.294, 0.029]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.endorserank.profitable_share` |
| W1 EndorseRank, non-loss share | -0.237 [-0.380, -0.090]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.endorserank.non_loss_share` |
| W1 EndorseRank (activity restarts), liquidation-free close rate | 0.291 [0.157, 0.407]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.endorserank_activity.liquidation_free_rate` |
| W1 EndorseRank (activity restarts), no liquidation | 0.297 [0.160, 0.422]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.endorserank_activity.no_liquidation` |
| W1 EndorseRank (activity restarts), profitable closes | 0.087 [-0.087, 0.258]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.endorserank_activity.profitable_closes` |
| W1 EndorseRank (activity restarts), realized gain | 0.000 [-0.162, 0.167]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.endorserank_activity.realized_gain` |
| W1 EndorseRank (activity restarts), profitable share | -0.146 [-0.304, 0.015]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.endorserank_activity.profitable_share` |
| W1 EndorseRank (activity restarts), non-loss share | -0.231 [-0.378, -0.065]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.endorserank_activity.non_loss_share` |
| W1 AWP, liquidation-free close rate | 0.240 [0.094, 0.365]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.awp.liquidation_free_rate` |
| W1 AWP, no liquidation | 0.248 [0.095, 0.382]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.awp.no_liquidation` |
| W1 AWP, profitable closes | 0.280 [0.114, 0.428]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.awp.profitable_closes` |
| W1 AWP, realized gain | 0.294 [0.148, 0.434]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.awp.realized_gain` |
| W1 AWP, profitable share | 0.065 [-0.106, 0.224]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.awp.profitable_share` |
| W1 AWP, non-loss share | 0.071 [-0.083, 0.215]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.awp.non_loss_share` |
| W1 C-PR (λ=1), liquidation-free close rate | 0.310 [0.181, 0.429]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.cpr_l100.liquidation_free_rate` |
| W1 C-PR (λ=1), no liquidation | 0.316 [0.180, 0.437]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.cpr_l100.no_liquidation` |
| W1 C-PR (λ=1), profitable closes | 0.004 [-0.173, 0.187]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.cpr_l100.profitable_closes` |
| W1 C-PR (λ=1), realized gain | -0.077 [-0.258, 0.112]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.cpr_l100.realized_gain` |
| W1 C-PR (λ=1), profitable share | -0.206 [-0.370, -0.029]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.cpr_l100.profitable_share` |
| W1 C-PR (λ=1), non-loss share | -0.287 [-0.445, -0.118]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.cpr_l100.non_loss_share` |
| W1 C-PR (λ=0), liquidation-free close rate | 0.138 [-0.065, 0.313]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.cpr_l0.liquidation_free_rate` |
| W1 C-PR (λ=0), no liquidation | 0.146 [-0.072, 0.329]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.cpr_l0.no_liquidation` |
| W1 C-PR (λ=0), profitable closes | 0.228 [0.068, 0.384]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.cpr_l0.profitable_closes` |
| W1 C-PR (λ=0), realized gain | 0.336 [0.203, 0.460]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.cpr_l0.realized_gain` |
| W1 C-PR (λ=0), profitable share | 0.168 [-0.009, 0.335]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.cpr_l0.profitable_share` |
| W1 C-PR (λ=0), non-loss share | 0.149 [-0.022, 0.311]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.cpr_l0.non_loss_share` |
| W1 C-PR (λ=0.25), liquidation-free close rate | 0.101 [-0.118, 0.296]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.cpr_l25.liquidation_free_rate` |
| W1 C-PR (λ=0.25), no liquidation | 0.107 [-0.122, 0.305]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.cpr_l25.no_liquidation` |
| W1 C-PR (λ=0.25), profitable closes | 0.224 [0.063, 0.382]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.cpr_l25.profitable_closes` |
| W1 C-PR (λ=0.25), realized gain | 0.332 [0.201, 0.456]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.cpr_l25.realized_gain` |
| W1 C-PR (λ=0.25), profitable share | 0.165 [-0.015, 0.333]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.cpr_l25.profitable_share` |
| W1 C-PR (λ=0.25), non-loss share | 0.165 [-0.006, 0.330]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.cpr_l25.non_loss_share` |
| W1 C-PR (λ=0.5), liquidation-free close rate | 0.095 [-0.124, 0.291]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.cpr_l50.liquidation_free_rate` |
| W1 C-PR (λ=0.5), no liquidation | 0.100 [-0.132, 0.301]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.cpr_l50.no_liquidation` |
| W1 C-PR (λ=0.5), profitable closes | 0.226 [0.064, 0.378]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.cpr_l50.profitable_closes` |
| W1 C-PR (λ=0.5), realized gain | 0.335 [0.201, 0.457]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.cpr_l50.realized_gain` |
| W1 C-PR (λ=0.5), profitable share | 0.160 [-0.019, 0.328]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.cpr_l50.profitable_share` |
| W1 C-PR (λ=0.5), non-loss share | 0.164 [-0.009, 0.328]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.cpr_l50.non_loss_share` |
| W1 C-PR (λ=0.75), liquidation-free close rate | 0.088 [-0.134, 0.289]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.cpr_l75.liquidation_free_rate` |
| W1 C-PR (λ=0.75), no liquidation | 0.093 [-0.141, 0.299]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.cpr_l75.no_liquidation` |
| W1 C-PR (λ=0.75), profitable closes | 0.223 [0.061, 0.375]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.cpr_l75.profitable_closes` |
| W1 C-PR (λ=0.75), realized gain | 0.331 [0.196, 0.453]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.cpr_l75.realized_gain` |
| W1 C-PR (λ=0.75), profitable share | 0.153 [-0.024, 0.320]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.cpr_l75.profitable_share` |
| W1 C-PR (λ=0.75), non-loss share | 0.160 [-0.011, 0.324]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.cpr_l75.non_loss_share` |
| W1 S-PR, liquidation-free close rate | 0.312 [0.184, 0.423]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.spr.liquidation_free_rate` |
| W1 S-PR, no liquidation | 0.318 [0.190, 0.434]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.spr.no_liquidation` |
| W1 S-PR, profitable closes | 0.240 [0.088, 0.384]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.spr.profitable_closes` |
| W1 S-PR, realized gain | 0.139 [-0.035, 0.296]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.spr.realized_gain` |
| W1 S-PR, profitable share | 0.057 [-0.103, 0.211]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.spr.profitable_share` |
| W1 S-PR, non-loss share | 0.012 [-0.145, 0.161]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.spr.non_loss_share` |
| W1 in-approve degree at the freeze, liquidation-free close rate | 0.394 [0.265, 0.518]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.in_approve_degree.liquidation_free_rate` |
| W1 in-approve degree at the freeze, no liquidation | 0.407 [0.268, 0.541]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.in_approve_degree.no_liquidation` |
| W1 in-approve degree at the freeze, profitable closes | 0.042 [-0.158, 0.243]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.in_approve_degree.profitable_closes` |
| W1 in-approve degree at the freeze, realized gain | 0.033 [-0.164, 0.230]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.in_approve_degree.realized_gain` |
| W1 in-approve degree at the freeze, profitable share | -0.221 [-0.406, -0.034]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.in_approve_degree.profitable_share` |
| W1 in-approve degree at the freeze, non-loss share | -0.294 [-0.468, -0.106]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.in_approve_degree.non_loss_share` |
| W1 transfer in-degree at the freeze, liquidation-free close rate | 0.331 [0.208, 0.441]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.in_degree.liquidation_free_rate` |
| W1 transfer in-degree at the freeze, no liquidation | 0.350 [0.214, 0.468]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.in_degree.no_liquidation` |
| W1 transfer in-degree at the freeze, profitable closes | 0.180 [0.005, 0.344]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.in_degree.profitable_closes` |
| W1 transfer in-degree at the freeze, realized gain | 0.171 [0.035, 0.296]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.in_degree.realized_gain` |
| W1 transfer in-degree at the freeze, profitable share | 0.004 [-0.174, 0.179]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.in_degree.profitable_share` |
| W1 transfer in-degree at the freeze, non-loss share | -0.022 [-0.196, 0.145]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w1.taus.in_degree.non_loss_share` |

### Neutral labels, W0 (2,000 paired resamples)

| Quantity | Value | Source |
|---|---|---|
| W0 traders | 88 | `registered-w1/eval_summary.json` : `neutral_w0.n` |
| W0 highest in-approve degree among traders | 3.000 | `registered-w1/eval_summary.json` : `neutral_w0.max_in_approve_degree` |
| W0 P: in-approve degree minus transfer in-degree, liquidation-free close rate | Δτ 0.252 [0.093, 0.413]; τa 0.344, τb 0.092; 97.5% [0.067, 0.438]; P(Δτ>0) 0.999; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.grid.P.liquidation_free_rate` |
| W0 P: in-approve degree minus transfer in-degree, no liquidation | Δτ 0.270 [0.098, 0.441]; τa 0.356, τb 0.086; P(Δτ>0) 0.999; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.grid.P.no_liquidation` |
| W0 P: in-approve degree minus transfer in-degree, profitable closes | Δτ 0.105 [-0.057, 0.258]; τa 0.083, τb -0.022; P(Δτ>0) 0.905; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.grid.P.profitable_closes` |
| W0 P: in-approve degree minus transfer in-degree, realized gain | Δτ 0.044 [-0.134, 0.212]; τa 0.024, τb -0.020; P(Δτ>0) 0.679; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.grid.P.realized_gain` |
| W0 P: in-approve degree minus transfer in-degree, profitable share | Δτ 0.052 [-0.115, 0.204]; τa -0.146, τb -0.198; P(Δτ>0) 0.740; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.grid.P.profitable_share` |
| W0 P: in-approve degree minus transfer in-degree, non-loss share | Δτ -0.088 [-0.239, 0.057]; τa -0.278, τb -0.190; P(Δτ>0) 0.128; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.grid.P.non_loss_share` |
| W0 Q: EndorseRank (activity restarts) minus AWP, liquidation-free close rate | Δτ 0.062 [-0.078, 0.219]; τa 0.230, τb 0.168; 97.5% [-0.096, 0.234]; P(Δτ>0) 0.779; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.grid.Q.liquidation_free_rate` |
| W0 Q: EndorseRank (activity restarts) minus AWP, no liquidation | Δτ 0.063 [-0.086, 0.222]; τa 0.221, τb 0.158; P(Δτ>0) 0.774; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.grid.Q.no_liquidation` |
| W0 Q: EndorseRank (activity restarts) minus AWP, profitable closes | Δτ -0.016 [-0.134, 0.094]; τa 0.122, τb 0.138; P(Δτ>0) 0.394; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.grid.Q.profitable_closes` |
| W0 Q: EndorseRank (activity restarts) minus AWP, realized gain | Δτ -0.047 [-0.163, 0.061]; τa 0.087, τb 0.134; P(Δτ>0) 0.204; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.grid.Q.realized_gain` |
| W0 Q: EndorseRank (activity restarts) minus AWP, profitable share | Δτ 0.093 [0.0009477, 0.187]; τa -0.076, τb -0.170; P(Δτ>0) 0.977; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.grid.Q.profitable_share` |
| W0 Q: EndorseRank (activity restarts) minus AWP, non-loss share | Δτ 0.067 [-0.034, 0.162]; τa -0.186, τb -0.253; P(Δτ>0) 0.899; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.grid.Q.non_loss_share` |
| W0 C-PR (λ=1) minus C-PR (λ=0), liquidation-free close rate | Δτ 0.205 [-0.041, 0.437]; τa 0.220, τb 0.016; P(Δτ>0) 0.948; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.grid.layers.liquidation_free_rate` |
| W0 C-PR (λ=1) minus C-PR (λ=0), no liquidation | Δτ 0.189 [-0.049, 0.431]; τa 0.212, τb 0.023; P(Δτ>0) 0.941; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.grid.layers.no_liquidation` |
| W0 C-PR (λ=1) minus C-PR (λ=0), profitable closes | Δτ 0.035 [-0.184, 0.249]; τa 0.077, τb 0.042; P(Δτ>0) 0.645; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.grid.layers.profitable_closes` |
| W0 C-PR (λ=1) minus C-PR (λ=0), realized gain | Δτ -0.048 [-0.282, 0.169]; τa 0.044, τb 0.092; P(Δτ>0) 0.339; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.grid.layers.realized_gain` |
| W0 C-PR (λ=1) minus C-PR (λ=0), profitable share | Δτ -0.004 [-0.211, 0.209]; τa -0.071, τb -0.067; P(Δτ>0) 0.489; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.grid.layers.profitable_share` |
| W0 C-PR (λ=1) minus C-PR (λ=0), non-loss share | Δτ -0.147 [-0.352, 0.055]; τa -0.175, τb -0.028; P(Δτ>0) 0.077; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.grid.layers.non_loss_share` |
| W0 EndorseRank minus AWP, liquidation-free close rate | Δτ 0.062 [-0.079, 0.217]; τa 0.230, τb 0.168; P(Δτ>0) 0.780; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.grid.er_awp.liquidation_free_rate` |
| W0 EndorseRank minus AWP, no liquidation | Δτ 0.064 [-0.082, 0.218]; τa 0.222, τb 0.158; P(Δτ>0) 0.783; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.grid.er_awp.no_liquidation` |
| W0 EndorseRank minus AWP, profitable closes | Δτ 0.018 [-0.133, 0.151]; τa 0.156, τb 0.138; P(Δτ>0) 0.600; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.grid.er_awp.profitable_closes` |
| W0 EndorseRank minus AWP, realized gain | Δτ -0.046 [-0.185, 0.082]; τa 0.088, τb 0.134; P(Δτ>0) 0.239; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.grid.er_awp.realized_gain` |
| W0 EndorseRank minus AWP, profitable share | Δτ 0.117 [0.004, 0.227]; τa -0.053, τb -0.170; P(Δτ>0) 0.980; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.grid.er_awp.profitable_share` |
| W0 EndorseRank minus AWP, non-loss share | Δτ 0.083 [-0.031, 0.188]; τa -0.170, τb -0.253; P(Δτ>0) 0.938; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.grid.er_awp.non_loss_share` |
| W0 C-PR (λ=0) minus AWP, liquidation-free close rate | Δτ -0.152 [-0.359, 0.035]; τa 0.016, τb 0.168; P(Δτ>0) 0.061; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.grid.cpr0_awp.liquidation_free_rate` |
| W0 C-PR (λ=0) minus AWP, no liquidation | Δτ -0.136 [-0.343, 0.054]; τa 0.023, τb 0.158; P(Δτ>0) 0.085; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.grid.cpr0_awp.no_liquidation` |
| W0 C-PR (λ=0) minus AWP, profitable closes | Δτ -0.097 [-0.265, 0.066]; τa 0.042, τb 0.138; P(Δτ>0) 0.129; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.grid.cpr0_awp.profitable_closes` |
| W0 C-PR (λ=0) minus AWP, realized gain | Δτ -0.043 [-0.208, 0.133]; τa 0.092, τb 0.134; P(Δτ>0) 0.316; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.grid.cpr0_awp.realized_gain` |
| W0 C-PR (λ=0) minus AWP, profitable share | Δτ 0.102 [-0.067, 0.259]; τa -0.067, τb -0.170; P(Δτ>0) 0.880; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.grid.cpr0_awp.profitable_share` |
| W0 C-PR (λ=0) minus AWP, non-loss share | Δτ 0.225 [0.083, 0.374]; τa -0.028, τb -0.253; P(Δτ>0) 0.997; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.grid.cpr0_awp.non_loss_share` |
| W0 EndorseRank minus in-approve degree, liquidation-free close rate | Δτ -0.113 [-0.198, -0.026]; τa 0.230, τb 0.344; P(Δτ>0) 0.006; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.grid.er_degree.liquidation_free_rate` |
| W0 EndorseRank minus in-approve degree, no liquidation | Δτ -0.134 [-0.218, -0.044]; τa 0.222, τb 0.356; P(Δτ>0) 0.004; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.grid.er_degree.no_liquidation` |
| W0 EndorseRank minus in-approve degree, profitable closes | Δτ 0.074 [-0.017, 0.164]; τa 0.156, τb 0.083; P(Δτ>0) 0.949; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.grid.er_degree.profitable_closes` |
| W0 EndorseRank minus in-approve degree, realized gain | Δτ 0.064 [-0.028, 0.158]; τa 0.088, τb 0.024; P(Δτ>0) 0.913; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.grid.er_degree.realized_gain` |
| W0 EndorseRank minus in-approve degree, profitable share | Δτ 0.093 [-0.003, 0.189]; τa -0.053, τb -0.146; P(Δτ>0) 0.970; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.grid.er_degree.profitable_share` |
| W0 EndorseRank minus in-approve degree, non-loss share | Δτ 0.108 [0.019, 0.202]; τa -0.170, τb -0.278; P(Δτ>0) 0.990; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.grid.er_degree.non_loss_share` |
| W0 P: in-approve degree minus transfer in-degree, stratified by closes | Δτ 0.179 [0.055, 0.392]; τa 0.338, τb 0.158 | `registered-w1/eval_summary.json` : `neutral_w0.stratified.P` |
| W0 Q: EndorseRank (activity restarts) minus AWP, stratified by closes | Δτ 0.066 [-0.116, 0.274]; τa 0.220, τb 0.154 | `registered-w1/eval_summary.json` : `neutral_w0.stratified.Q` |
| W0 recipients: n | 40 | `registered-w1/eval_summary.json` : `neutral_w0.recipients.recipients.n` |
| W0 recipients: share no liquidation | 1.000 | `registered-w1/eval_summary.json` : `neutral_w0.recipients.recipients.share_no_liquidation` |
| W0 recipients: mean liquidation free rate | 1.000 | `registered-w1/eval_summary.json` : `neutral_w0.recipients.recipients.mean_liquidation_free_rate` |
| W0 recipients: mean profitable share | 0.362 | `registered-w1/eval_summary.json` : `neutral_w0.recipients.recipients.mean_profitable_share` |
| W0 recipients: mean non loss share | 0.402 | `registered-w1/eval_summary.json` : `neutral_w0.recipients.recipients.mean_non_loss_share` |
| W0 recipients: median closes | 31.000 | `registered-w1/eval_summary.json` : `neutral_w0.recipients.recipients.median_closes` |
| W0 others: n | 48 | `registered-w1/eval_summary.json` : `neutral_w0.recipients.others.n` |
| W0 others: share no liquidation | 0.750 | `registered-w1/eval_summary.json` : `neutral_w0.recipients.others.share_no_liquidation` |
| W0 others: mean liquidation free rate | 0.919 | `registered-w1/eval_summary.json` : `neutral_w0.recipients.others.mean_liquidation_free_rate` |
| W0 others: mean profitable share | 0.474 | `registered-w1/eval_summary.json` : `neutral_w0.recipients.others.mean_profitable_share` |
| W0 others: mean non loss share | 0.607 | `registered-w1/eval_summary.json` : `neutral_w0.recipients.others.mean_non_loss_share` |
| W0 others: median closes | 10.000 | `registered-w1/eval_summary.json` : `neutral_w0.recipients.others.median_closes` |
| W0 P without the ten recipients of highest in-approve degree | Δτ 0.249 [0.083, 0.421]; τa 0.324, τb 0.075; P(Δτ>0) 0.998; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.influence_without_top10` |
| W0 EndorseRank, liquidation-free close rate | 0.230 [0.115, 0.341]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.endorserank.liquidation_free_rate` |
| W0 EndorseRank, no liquidation | 0.222 [0.110, 0.332]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.endorserank.no_liquidation` |
| W0 EndorseRank, profitable closes | 0.156 [-0.010, 0.317]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.endorserank.profitable_closes` |
| W0 EndorseRank, realized gain | 0.088 [-0.070, 0.245]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.endorserank.realized_gain` |
| W0 EndorseRank, profitable share | -0.053 [-0.184, 0.085]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.endorserank.profitable_share` |
| W0 EndorseRank, non-loss share | -0.170 [-0.298, -0.040]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.endorserank.non_loss_share` |
| W0 EndorseRank (activity restarts), liquidation-free close rate | 0.230 [0.111, 0.346]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.endorserank_activity.liquidation_free_rate` |
| W0 EndorseRank (activity restarts), no liquidation | 0.221 [0.104, 0.337]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.endorserank_activity.no_liquidation` |
| W0 EndorseRank (activity restarts), profitable closes | 0.122 [-0.039, 0.276]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.endorserank_activity.profitable_closes` |
| W0 EndorseRank (activity restarts), realized gain | 0.087 [-0.075, 0.240]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.endorserank_activity.realized_gain` |
| W0 EndorseRank (activity restarts), profitable share | -0.076 [-0.210, 0.068]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.endorserank_activity.profitable_share` |
| W0 EndorseRank (activity restarts), non-loss share | -0.186 [-0.322, -0.044]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.endorserank_activity.non_loss_share` |
| W0 AWP, liquidation-free close rate | 0.168 [0.022, 0.315]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.awp.liquidation_free_rate` |
| W0 AWP, no liquidation | 0.158 [0.011, 0.305]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.awp.no_liquidation` |
| W0 AWP, profitable closes | 0.138 [-0.018, 0.291]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.awp.profitable_closes` |
| W0 AWP, realized gain | 0.134 [-0.026, 0.295]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.awp.realized_gain` |
| W0 AWP, profitable share | -0.170 [-0.309, -0.025]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.awp.profitable_share` |
| W0 AWP, non-loss share | -0.253 [-0.387, -0.117]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.awp.non_loss_share` |
| W0 C-PR (λ=1), liquidation-free close rate | 0.220 [0.100, 0.335]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.cpr_l100.liquidation_free_rate` |
| W0 C-PR (λ=1), no liquidation | 0.212 [0.095, 0.326]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.cpr_l100.no_liquidation` |
| W0 C-PR (λ=1), profitable closes | 0.077 [-0.085, 0.234]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.cpr_l100.profitable_closes` |
| W0 C-PR (λ=1), realized gain | 0.044 [-0.117, 0.203]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.cpr_l100.realized_gain` |
| W0 C-PR (λ=1), profitable share | -0.071 [-0.222, 0.080]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.cpr_l100.profitable_share` |
| W0 C-PR (λ=1), non-loss share | -0.175 [-0.313, -0.029]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.cpr_l100.non_loss_share` |
| W0 C-PR (λ=0), liquidation-free close rate | 0.016 [-0.156, 0.199]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.cpr_l0.liquidation_free_rate` |
| W0 C-PR (λ=0), no liquidation | 0.023 [-0.157, 0.205]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.cpr_l0.no_liquidation` |
| W0 C-PR (λ=0), profitable closes | 0.042 [-0.097, 0.179]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.cpr_l0.profitable_closes` |
| W0 C-PR (λ=0), realized gain | 0.092 [-0.050, 0.243]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.cpr_l0.realized_gain` |
| W0 C-PR (λ=0), profitable share | -0.067 [-0.213, 0.081]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.cpr_l0.profitable_share` |
| W0 C-PR (λ=0), non-loss share | -0.028 [-0.176, 0.117]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.cpr_l0.non_loss_share` |
| W0 C-PR (λ=0.25), liquidation-free close rate | -0.005 [-0.184, 0.186]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.cpr_l25.liquidation_free_rate` |
| W0 C-PR (λ=0.25), no liquidation | 0.001 [-0.187, 0.195]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.cpr_l25.no_liquidation` |
| W0 C-PR (λ=0.25), profitable closes | 0.035 [-0.107, 0.175]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.cpr_l25.profitable_closes` |
| W0 C-PR (λ=0.25), realized gain | 0.081 [-0.060, 0.233]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.cpr_l25.realized_gain` |
| W0 C-PR (λ=0.25), profitable share | -0.069 [-0.217, 0.078]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.cpr_l25.profitable_share` |
| W0 C-PR (λ=0.25), non-loss share | -0.006 [-0.152, 0.140]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.cpr_l25.non_loss_share` |
| W0 C-PR (λ=0.5), liquidation-free close rate | -0.003 [-0.187, 0.190]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.cpr_l50.liquidation_free_rate` |
| W0 C-PR (λ=0.5), no liquidation | 0.003 [-0.191, 0.201]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.cpr_l50.no_liquidation` |
| W0 C-PR (λ=0.5), profitable closes | 0.042 [-0.101, 0.182]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.cpr_l50.profitable_closes` |
| W0 C-PR (λ=0.5), realized gain | 0.085 [-0.061, 0.239]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.cpr_l50.realized_gain` |
| W0 C-PR (λ=0.5), profitable share | -0.064 [-0.211, 0.085]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.cpr_l50.profitable_share` |
| W0 C-PR (λ=0.5), non-loss share | 0.000 [-0.146, 0.145]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.cpr_l50.non_loss_share` |
| W0 C-PR (λ=0.75), liquidation-free close rate | 0.000 [-0.183, 0.193]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.cpr_l75.liquidation_free_rate` |
| W0 C-PR (λ=0.75), no liquidation | 0.006 [-0.187, 0.203]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.cpr_l75.no_liquidation` |
| W0 C-PR (λ=0.75), profitable closes | 0.048 [-0.094, 0.184]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.cpr_l75.profitable_closes` |
| W0 C-PR (λ=0.75), realized gain | 0.086 [-0.061, 0.241]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.cpr_l75.realized_gain` |
| W0 C-PR (λ=0.75), profitable share | -0.062 [-0.210, 0.087]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.cpr_l75.profitable_share` |
| W0 C-PR (λ=0.75), non-loss share | 0.002 [-0.148, 0.147]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.cpr_l75.non_loss_share` |
| W0 S-PR, liquidation-free close rate | 0.113 [-0.056, 0.266]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.spr.liquidation_free_rate` |
| W0 S-PR, no liquidation | 0.100 [-0.072, 0.255]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.spr.no_liquidation` |
| W0 S-PR, profitable closes | 0.055 [-0.083, 0.202]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.spr.profitable_closes` |
| W0 S-PR, realized gain | 0.072 [-0.087, 0.239]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.spr.realized_gain` |
| W0 S-PR, profitable share | -0.025 [-0.164, 0.121]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.spr.profitable_share` |
| W0 S-PR, non-loss share | -0.069 [-0.215, 0.080]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.spr.non_loss_share` |
| W0 in-approve degree at the freeze, liquidation-free close rate | 0.344 [0.244, 0.440]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.in_approve_degree.liquidation_free_rate` |
| W0 in-approve degree at the freeze, no liquidation | 0.356 [0.248, 0.462]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.in_approve_degree.no_liquidation` |
| W0 in-approve degree at the freeze, profitable closes | 0.083 [-0.094, 0.259]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.in_approve_degree.profitable_closes` |
| W0 in-approve degree at the freeze, realized gain | 0.024 [-0.158, 0.207]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.in_approve_degree.realized_gain` |
| W0 in-approve degree at the freeze, profitable share | -0.146 [-0.317, 0.028]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.in_approve_degree.profitable_share` |
| W0 in-approve degree at the freeze, non-loss share | -0.278 [-0.425, -0.123]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.in_approve_degree.non_loss_share` |
| W0 transfer in-degree at the freeze, liquidation-free close rate | 0.092 [-0.071, 0.238]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.in_degree.liquidation_free_rate` |
| W0 transfer in-degree at the freeze, no liquidation | 0.086 [-0.081, 0.239]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.in_degree.no_liquidation` |
| W0 transfer in-degree at the freeze, profitable closes | -0.022 [-0.169, 0.136]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.in_degree.profitable_closes` |
| W0 transfer in-degree at the freeze, realized gain | -0.020 [-0.174, 0.144]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.in_degree.realized_gain` |
| W0 transfer in-degree at the freeze, profitable share | -0.198 [-0.342, -0.048]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.in_degree.profitable_share` |
| W0 transfer in-degree at the freeze, non-loss share | -0.190 [-0.345, -0.036]; B=2000 | `registered-w1/eval_summary.json` : `neutral_w0.taus.in_degree.non_loss_share` |

### Supplementary spender contrasts (computed after the labels were known, outside every rule)

| Quantity | Value | Source |
|---|---|---|
| W0 EndorseRank (activity restarts) minus in-approve degree, new approval pairs | Δτ 0.043 [0.036, 0.049]; τa 0.295, τb 0.252; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w0.er_activity_minus_degree_appr` |
| W0 EndorseRank (activity restarts) minus EndorseRank, new approval pairs | Δτ 0.054 [0.049, 0.058]; τa 0.295, τb 0.241; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w0.er_activity_minus_er_appr` |
| W0 EndorseRank (activity restarts) minus EndorseRank, new transfer senders | Δτ 0.046 [0.041, 0.050]; τa 0.272, τb 0.226; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w0.er_activity_minus_er_send` |
| W0 EndorseRank minus AWP, new approval pairs | Δτ 0.045 [0.033, 0.055]; τa 0.241, τb 0.196; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w0.er_minus_awp_appr` |
| W0 EndorseRank minus AWP, new transfer senders | Δτ -0.114 [-0.120, -0.108]; τa 0.226, τb 0.340; P(Δτ>0) 0.000; B=400 | `supplementary/supplementary.json` : `w0.er_minus_awp_send` |
| W0 n | 33,101 | `supplementary/supplementary.json` : `w0.n` |
| W1 EndorseRank (activity restarts) minus in-approve degree, new approval pairs | Δτ 0.018 [0.012, 0.023]; τa 0.280, τb 0.262; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w1.er_activity_minus_degree_appr` |
| W1 EndorseRank (activity restarts) minus EndorseRank, new approval pairs | Δτ 0.046 [0.042, 0.051]; τa 0.280, τb 0.233; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w1.er_activity_minus_er_appr` |
| W1 EndorseRank (activity restarts) minus EndorseRank, new transfer senders | Δτ 0.035 [0.030, 0.039]; τa 0.245, τb 0.210; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w1.er_activity_minus_er_send` |
| W1 EndorseRank minus AWP, new approval pairs | Δτ 0.056 [0.046, 0.068]; τa 0.233, τb 0.177; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w1.er_minus_awp_appr` |
| W1 EndorseRank minus AWP, new transfer senders | Δτ -0.112 [-0.119, -0.106]; τa 0.210, τb 0.322; P(Δτ>0) 0.000; B=400 | `supplementary/supplementary.json` : `w1.er_minus_awp_send` |
| W1 n | 34,587 | `supplementary/supplementary.json` : `w1.n` |

## 8. Sybil cost model (EndorseRank graph at T_obs)

| Quantity | Value | Source |
|---|---|---|
| graph.nodes | 13,055,150 | `sybil-model/sybil_model.json` : `graph.nodes` |
| graph.edges | 22,321,470 | `sybil-model/sybil_model.json` : `graph.edges` |
| sigma0 | 0.8581 | `sybil-model/sybil_model.json` : `sigma0` |
| b common | 3.403e-08 | `sybil-model/sybil_model.json` : `b_common` |
| r D | 0.3461 | `sybil-model/sybil_model.json` : `r_D` |
| damping.0.75.r D | 0.3379 | `sybil-model/sybil_model.json` : `damping.0.75.r_D` |
| damping.0.75.farm factor | 2.0137 | `sybil-model/sybil_model.json` : `damping.0.75.farm_factor` |
| damping.0.85.r D | 0.3461 | `sybil-model/sybil_model.json` : `damping.0.85.r_D` |
| damping.0.85.farm factor | 2.9614 | `sybil-model/sybil_model.json` : `damping.0.85.farm_factor` |
| damping.0.95.r D | 0.2960 | `sybil-model/sybil_model.json` : `damping.0.95.r_D` |
| damping.0.95.farm factor | 6.6239 | `sybil-model/sybil_model.json` : `damping.0.95.farm_factor` |
| ring20 collects times share | 2.9614 | `sybil-model/sybil_model.json` : `ring20_collects_times_share` |
| star.m | 10 | `sybil-model/sybil_model.json` : `star.m` |
| star.target score | 1.165e-06 | `sybil-model/sybil_model.json` : `star.target_score` |
| star.closed form | 1.165e-06 | `sybil-model/sybil_model.json` : `star.closed_form` |
| star.highest cohort endorserank | 0.1126 | `sybil-model/sybil_model.json` : `star.highest_cohort_endorserank` |
| star.ratio to highest | 1.035e-05 | `sybil-model/sybil_model.json` : `star.ratio_to_highest` |
| star.approvals per window | 20 | `sybil-model/sybil_model.json` : `star.approvals_per_window` |
| fresh approval share median owner | 0.9441 | `sybil-model/sybil_model.json` : `fresh_approval_share_median_owner` |
| owners | 13,029,306 | `sybil-model/sybil_model.json` : `owners` |
| farm size to reach cohort quantile.p50.score | 7.103e-08 | `sybil-model/sybil_model.json` : `farm_size_to_reach_cohort_quantile.p50.score` |
| farm size to reach cohort quantile.p50.farm addresses | 0.0000 | `sybil-model/sybil_model.json` : `farm_size_to_reach_cohort_quantile.p50.farm_addresses` |
| farm size to reach cohort quantile.p90.score | 1.472e-06 | `sybil-model/sybil_model.json` : `farm_size_to_reach_cohort_quantile.p90.score` |
| farm size to reach cohort quantile.p90.farm addresses | 12.9433 | `sybil-model/sybil_model.json` : `farm_size_to_reach_cohort_quantile.p90.farm_addresses` |
| farm size to reach cohort quantile.p99.score | 0.0001307 | `sybil-model/sybil_model.json` : `farm_size_to_reach_cohort_quantile.p99.score` |
| farm size to reach cohort quantile.p99.farm addresses | 1,252.9 | `sybil-model/sybil_model.json` : `farm_size_to_reach_cohort_quantile.p99.farm_addresses` |
| farm size to reach cohort quantile.p100.score | 0.1126 | `sybil-model/sybil_model.json` : `farm_size_to_reach_cohort_quantile.p100.score` |
| farm size to reach cohort quantile.p100.farm addresses | 1,080,270.5 | `sybil-model/sybil_model.json` : `farm_size_to_reach_cohort_quantile.p100.farm_addresses` |

## 9. Robustness

| Quantity | Value | Source |
|---|---|---|
| Damping endorserank_d75: iterations | 50 | `same-window/eval_summary.json` : `damping.endorserank_d75.iterations` |
| Damping endorserank_d75: transfer family | 0.121 [0.112, 0.128]; B=400 | `same-window/eval_summary.json` : `damping.endorserank_d75.transfer` |
| Damping endorserank_d75: allowance family | 0.483 [0.478, 0.488]; B=400 | `same-window/eval_summary.json` : `damping.endorserank_d75.allowance` |
| Damping endorserank_d75: Sybil stability family | 0.025 [0.018, 0.030]; B=400 | `same-window/eval_summary.json` : `damping.endorserank_d75.sybil_stability` |
| Damping awp_d75: iterations | 54 | `same-window/eval_summary.json` : `damping.awp_d75.iterations` |
| Damping awp_d75: transfer family | 0.448 [0.441, 0.455]; B=400 | `same-window/eval_summary.json` : `damping.awp_d75.transfer` |
| Damping awp_d75: allowance family | 0.174 [0.166, 0.181]; B=400 | `same-window/eval_summary.json` : `damping.awp_d75.allowance` |
| Damping awp_d75: Sybil stability family | 0.315 [0.308, 0.321]; B=400 | `same-window/eval_summary.json` : `damping.awp_d75.sybil_stability` |
| Damping endorserank_d85: iterations | 84 | `same-window/eval_summary.json` : `damping.endorserank_d85.iterations` |
| Damping endorserank_d85: transfer family | 0.122 [0.113, 0.129]; B=400 | `same-window/eval_summary.json` : `damping.endorserank_d85.transfer` |
| Damping endorserank_d85: allowance family | 0.481 [0.476, 0.487]; B=400 | `same-window/eval_summary.json` : `damping.endorserank_d85.allowance` |
| Damping endorserank_d85: Sybil stability family | 0.025 [0.019, 0.031]; B=400 | `same-window/eval_summary.json` : `damping.endorserank_d85.sybil_stability` |
| Damping awp_d85: iterations | 93 | `same-window/eval_summary.json` : `damping.awp_d85.iterations` |
| Damping awp_d85: transfer family | 0.447 [0.440, 0.453]; B=400 | `same-window/eval_summary.json` : `damping.awp_d85.transfer` |
| Damping awp_d85: allowance family | 0.173 [0.165, 0.180]; B=400 | `same-window/eval_summary.json` : `damping.awp_d85.allowance` |
| Damping awp_d85: Sybil stability family | 0.311 [0.303, 0.317]; B=400 | `same-window/eval_summary.json` : `damping.awp_d85.sybil_stability` |
| Damping endorserank_d95: iterations | 224 | `same-window/eval_summary.json` : `damping.endorserank_d95.iterations` |
| Damping endorserank_d95: transfer family | 0.122 [0.114, 0.130]; B=400 | `same-window/eval_summary.json` : `damping.endorserank_d95.transfer` |
| Damping endorserank_d95: allowance family | 0.480 [0.474, 0.485]; B=400 | `same-window/eval_summary.json` : `damping.endorserank_d95.allowance` |
| Damping endorserank_d95: Sybil stability family | 0.026 [0.020, 0.031]; B=400 | `same-window/eval_summary.json` : `damping.endorserank_d95.sybil_stability` |
| Damping awp_d95: iterations | 276 | `same-window/eval_summary.json` : `damping.awp_d95.iterations` |
| Damping awp_d95: transfer family | 0.444 [0.437, 0.451]; B=400 | `same-window/eval_summary.json` : `damping.awp_d95.transfer` |
| Damping awp_d95: allowance family | 0.170 [0.162, 0.177]; B=400 | `same-window/eval_summary.json` : `damping.awp_d95.allowance` |
| Damping awp_d95: Sybil stability family | 0.303 [0.296, 0.310]; B=400 | `same-window/eval_summary.json` : `damping.awp_d95.sybil_stability` |
| Top tokens by_amount: EndorseRank, transfer | 0.020 | `robustness/robustness.json` : `top_tokens.by_amount.endorserank.transfer` |
| Top tokens by_amount: EndorseRank, allowance | 0.237 | `robustness/robustness.json` : `top_tokens.by_amount.endorserank.allowance` |
| Top tokens by_amount: EndorseRank, Sybil stability | -0.017 | `robustness/robustness.json` : `top_tokens.by_amount.endorserank.sybil_stability` |
| Top tokens by_amount: AWP, transfer | 0.290 | `robustness/robustness.json` : `top_tokens.by_amount.awp.transfer` |
| Top tokens by_amount: AWP, allowance | 0.073 | `robustness/robustness.json` : `top_tokens.by_amount.awp.allowance` |
| Top tokens by_amount: AWP, Sybil stability | 0.207 | `robustness/robustness.json` : `top_tokens.by_amount.awp.sybil_stability` |
| Top tokens by_amount: allowance edges | 16,708,034 | `robustness/robustness.json` : `top_tokens.by_amount.allowance_edges` |
| Top tokens by_amount: transfer edges | 34,385,548 | `robustness/robustness.json` : `top_tokens.by_amount.transfer_edges` |
| Top tokens by_rows: EndorseRank, transfer | 0.022 | `robustness/robustness.json` : `top_tokens.by_rows.endorserank.transfer` |
| Top tokens by_rows: EndorseRank, allowance | 0.239 | `robustness/robustness.json` : `top_tokens.by_rows.endorserank.allowance` |
| Top tokens by_rows: EndorseRank, Sybil stability | -0.014 | `robustness/robustness.json` : `top_tokens.by_rows.endorserank.sybil_stability` |
| Top tokens by_rows: AWP, transfer | 0.294 | `robustness/robustness.json` : `top_tokens.by_rows.awp.transfer` |
| Top tokens by_rows: AWP, allowance | 0.074 | `robustness/robustness.json` : `top_tokens.by_rows.awp.allowance` |
| Top tokens by_rows: AWP, Sybil stability | 0.210 | `robustness/robustness.json` : `top_tokens.by_rows.awp.sybil_stability` |
| Top tokens by_rows: allowance edges | 17,536,468 | `robustness/robustness.json` : `top_tokens.by_rows.allowance_edges` |
| Top tokens by_rows: transfer edges | 35,700,301 | `robustness/robustness.json` : `top_tokens.by_rows.transfer_edges` |
| Top tokens all: EndorseRank, transfer | 0.122 | `robustness/robustness.json` : `top_tokens.all.endorserank.transfer` |
| Top tokens all: EndorseRank, allowance | 0.481 | `robustness/robustness.json` : `top_tokens.all.endorserank.allowance` |
| Top tokens all: EndorseRank, Sybil stability | 0.025 | `robustness/robustness.json` : `top_tokens.all.endorserank.sybil_stability` |
| Top tokens all: AWP, transfer | 0.447 | `robustness/robustness.json` : `top_tokens.all.awp.transfer` |
| Top tokens all: AWP, allowance | 0.173 | `robustness/robustness.json` : `top_tokens.all.awp.allowance` |
| Top tokens all: AWP, Sybil stability | 0.311 | `robustness/robustness.json` : `top_tokens.all.awp.sybil_stability` |
| Top tokens: shared tokens | 13 | `robustness/robustness.json` : `top_tokens.shared_tokens` |
| Stage n=1,000: EndorseRank, transfer | 0.228 | `robustness/robustness.json` : `sample_definition[0].endorserank.transfer` |
| Stage n=1,000: EndorseRank, allowance | 0.636 | `robustness/robustness.json` : `sample_definition[0].endorserank.allowance` |
| Stage n=1,000: EndorseRank, Sybil stability | 0.085 | `robustness/robustness.json` : `sample_definition[0].endorserank.sybil_stability` |
| Stage n=1,000: AWP, transfer | 0.480 | `robustness/robustness.json` : `sample_definition[0].awp.transfer` |
| Stage n=1,000: AWP, allowance | 0.196 | `robustness/robustness.json` : `sample_definition[0].awp.allowance` |
| Stage n=1,000: AWP, Sybil stability | 0.324 | `robustness/robustness.json` : `sample_definition[0].awp.sybil_stability` |
| Stage n=1,000: allowance edges | 194,084 | `robustness/robustness.json` : `sample_definition[0].allowance_edges` |
| Stage n=1,000: transfer edges | 1,385,509 | `robustness/robustness.json` : `sample_definition[0].transfer_edges` |
| Stage n=2,000: EndorseRank, transfer | 0.201 | `robustness/robustness.json` : `sample_definition[1].endorserank.transfer` |
| Stage n=2,000: EndorseRank, allowance | 0.622 | `robustness/robustness.json` : `sample_definition[1].endorserank.allowance` |
| Stage n=2,000: EndorseRank, Sybil stability | 0.075 | `robustness/robustness.json` : `sample_definition[1].endorserank.sybil_stability` |
| Stage n=2,000: AWP, transfer | 0.464 | `robustness/robustness.json` : `sample_definition[1].awp.transfer` |
| Stage n=2,000: AWP, allowance | 0.197 | `robustness/robustness.json` : `sample_definition[1].awp.allowance` |
| Stage n=2,000: AWP, Sybil stability | 0.317 | `robustness/robustness.json` : `sample_definition[1].awp.sybil_stability` |
| Stage n=2,000: allowance edges | 761,242 | `robustness/robustness.json` : `sample_definition[1].allowance_edges` |
| Stage n=2,000: transfer edges | 3,145,438 | `robustness/robustness.json` : `sample_definition[1].transfer_edges` |
| Stage n=5,000: EndorseRank, transfer | 0.167 | `robustness/robustness.json` : `sample_definition[2].endorserank.transfer` |
| Stage n=5,000: EndorseRank, allowance | 0.561 | `robustness/robustness.json` : `sample_definition[2].endorserank.allowance` |
| Stage n=5,000: EndorseRank, Sybil stability | 0.059 | `robustness/robustness.json` : `sample_definition[2].endorserank.sybil_stability` |
| Stage n=5,000: AWP, transfer | 0.456 | `robustness/robustness.json` : `sample_definition[2].awp.transfer` |
| Stage n=5,000: AWP, allowance | 0.199 | `robustness/robustness.json` : `sample_definition[2].awp.allowance` |
| Stage n=5,000: AWP, Sybil stability | 0.320 | `robustness/robustness.json` : `sample_definition[2].awp.sybil_stability` |
| Stage n=5,000: allowance edges | 4,606,533 | `robustness/robustness.json` : `sample_definition[2].allowance_edges` |
| Stage n=5,000: transfer edges | 12,043,690 | `robustness/robustness.json` : `sample_definition[2].transfer_edges` |
| Stage n=10,000: EndorseRank, transfer | 0.151 | `robustness/robustness.json` : `sample_definition[3].endorserank.transfer` |
| Stage n=10,000: EndorseRank, allowance | 0.527 | `robustness/robustness.json` : `sample_definition[3].endorserank.allowance` |
| Stage n=10,000: EndorseRank, Sybil stability | 0.044 | `robustness/robustness.json` : `sample_definition[3].endorserank.sybil_stability` |
| Stage n=10,000: AWP, transfer | 0.448 | `robustness/robustness.json` : `sample_definition[3].awp.transfer` |
| Stage n=10,000: AWP, allowance | 0.183 | `robustness/robustness.json` : `sample_definition[3].awp.allowance` |
| Stage n=10,000: AWP, Sybil stability | 0.313 | `robustness/robustness.json` : `sample_definition[3].awp.sybil_stability` |
| Stage n=10,000: allowance edges | 7,030,772 | `robustness/robustness.json` : `sample_definition[3].allowance_edges` |
| Stage n=10,000: transfer edges | 20,054,589 | `robustness/robustness.json` : `sample_definition[3].transfer_edges` |
| Stage n=20,000: EndorseRank, transfer | 0.131 | `robustness/robustness.json` : `sample_definition[4].endorserank.transfer` |
| Stage n=20,000: EndorseRank, allowance | 0.501 | `robustness/robustness.json` : `sample_definition[4].endorserank.allowance` |
| Stage n=20,000: EndorseRank, Sybil stability | 0.030 | `robustness/robustness.json` : `sample_definition[4].endorserank.sybil_stability` |
| Stage n=20,000: AWP, transfer | 0.450 | `robustness/robustness.json` : `sample_definition[4].awp.transfer` |
| Stage n=20,000: AWP, allowance | 0.178 | `robustness/robustness.json` : `sample_definition[4].awp.allowance` |
| Stage n=20,000: AWP, Sybil stability | 0.312 | `robustness/robustness.json` : `sample_definition[4].awp.sybil_stability` |
| Stage n=20,000: allowance edges | 15,690,094 | `robustness/robustness.json` : `sample_definition[4].allowance_edges` |
| Stage n=20,000: transfer edges | 48,796,598 | `robustness/robustness.json` : `sample_definition[4].transfer_edges` |
| Stage n=27,844: EndorseRank, transfer | 0.122 | `robustness/robustness.json` : `sample_definition[5].endorserank.transfer` |
| Stage n=27,844: EndorseRank, allowance | 0.481 | `robustness/robustness.json` : `sample_definition[5].endorserank.allowance` |
| Stage n=27,844: EndorseRank, Sybil stability | 0.025 | `robustness/robustness.json` : `sample_definition[5].endorserank.sybil_stability` |
| Stage n=27,844: AWP, transfer | 0.447 | `robustness/robustness.json` : `sample_definition[5].awp.transfer` |
| Stage n=27,844: AWP, allowance | 0.173 | `robustness/robustness.json` : `sample_definition[5].awp.allowance` |
| Stage n=27,844: AWP, Sybil stability | 0.311 | `robustness/robustness.json` : `sample_definition[5].awp.sybil_stability` |
| Stage n=27,844: allowance edges | 22,321,470 | `robustness/robustness.json` : `sample_definition[5].allowance_edges` |
| Stage n=27,844: transfer edges | 59,737,617 | `robustness/robustness.json` : `sample_definition[5].transfer_edges` |

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
| Scaling seed | contract-benchmark-v1 | `benchmark/benchmark.json` : `scaling_seed` |
| Full graphs: EndorseRank | mean 29.596 s, SD 0.606 s; runs 29.644, 30.210, 29.762, 29.784, 28.582; peak 1,285.0 MB; iterations 84; \|V\| 13,055,150; \|E\| 22,321,470 | `benchmark/benchmark.json` : `main.endorserank` |
| Full graphs: AWP | mean 69.819 s, SD 2.302 s; runs 70.808, 69.357, 73.212, 68.491, 67.226; peak 2,995.9 MB; iterations 93; \|V\| 23,029,298; \|E\| 59,737,617 | `benchmark/benchmark.json` : `main.awp` |
| Full graphs: C-PR (λ=0.5) | mean 105.507 s, SD 2.478 s; runs 102.667, 103.853, 107.489, 104.934, 108.592; peak 4,582.2 MB; iterations 92; \|V\| 25,304,106; \|E\| 71,375,442 | `benchmark/benchmark.json` : `main.cpr_l50` |
| Full graphs: S-PR | mean 100.861 s, SD 4.820 s; runs 107.139, 102.530, 94.957, 97.215, 102.465; peak 3,453.1 MB; iterations 185; \|V\| 23,029,298; \|E\| 59,737,617 | `benchmark/benchmark.json` : `main.spr` |
| AWP/EndorseRank runtime ratio (derived) | 2.36 | `benchmark/benchmark.json` : `main.awp.mean_s / main.endorserank.mean_s` |
| AWP/EndorseRank edge ratio (derived) | 2.68 | `benchmark/benchmark.json` : `main.awp.edges / main.endorserank.edges` |
| Damping 0.75: EndorseRank | mean 18.998 s, SD 0.468 s; runs 18.986, 18.938, 19.770, 18.776, 18.522; peak 1,285.0 MB; iterations 50; \|V\| 13,055,150; \|E\| 22,321,470 | `benchmark/benchmark.json` : `damping.0.75.endorserank` |
| Damping 0.75: AWP | mean 38.619 s, SD 1.297 s; runs 40.597, 39.114, 37.220, 38.200, 37.962; peak 2,995.9 MB; iterations 54; \|V\| 23,029,298; \|E\| 59,737,617 | `benchmark/benchmark.json` : `damping.0.75.awp` |
| Damping 0.85: EndorseRank | mean 29.596 s, SD 0.606 s; runs 29.644, 30.210, 29.762, 29.784, 28.582; peak 1,285.0 MB; iterations 84; \|V\| 13,055,150; \|E\| 22,321,470 | `benchmark/benchmark.json` : `damping.0.85.endorserank` |
| Damping 0.85: AWP | mean 69.819 s, SD 2.302 s; runs 70.808, 69.357, 73.212, 68.491, 67.226; peak 2,995.9 MB; iterations 93; \|V\| 23,029,298; \|E\| 59,737,617 | `benchmark/benchmark.json` : `damping.0.85.awp` |
| Damping 0.95: EndorseRank | mean 63.623 s, SD 1.093 s; runs 62.116, 64.104, 64.708, 64.337, 62.852; peak 1,285.0 MB; iterations 224; \|V\| 13,055,150; \|E\| 22,321,470 | `benchmark/benchmark.json` : `damping.0.95.endorserank` |
| Damping 0.95: AWP | mean 162.587 s, SD 8.359 s; runs 165.730, 175.831, 155.496, 158.528, 157.348; peak 2,995.9 MB; iterations 276; \|V\| 23,029,298; \|E\| 59,737,617 | `benchmark/benchmark.json` : `damping.0.95.awp` |
| Stage n=1,000: EndorseRank | mean 0.166 s, SD 0.002 s; runs 0.168, 0.166, 0.166, 0.168, 0.162; peak 17.4 MB; iterations 82; \|V\| 185,281; \|E\| 194,084 | `benchmark/benchmark.json` : `scaling[0].endorserank` |
| Stage n=1,000: AWP | mean 2.698 s, SD 0.121 s; runs 2.606, 2.688, 2.904, 2.616, 2.675; peak 126.8 MB; iterations 94; \|V\| 1,138,289; \|E\| 1,385,509 | `benchmark/benchmark.json` : `scaling[0].awp` |
| Stage n=2,000: EndorseRank | mean 0.957 s, SD 0.016 s; runs 0.942, 0.953, 0.966, 0.981, 0.944; peak 65.6 MB; iterations 76; \|V\| 687,884; \|E\| 761,242 | `benchmark/benchmark.json` : `scaling[1].endorserank` |
| Stage n=2,000: AWP | mean 6.922 s, SD 0.259 s; runs 7.070, 6.688, 6.782, 7.306, 6.767; peak 237.3 MB; iterations 89; \|V\| 1,946,268; \|E\| 3,145,438 | `benchmark/benchmark.json` : `scaling[1].awp` |
| Stage n=5,000: EndorseRank | mean 4.460 s, SD 0.199 s; runs 4.718, 4.521, 4.263, 4.254, 4.542; peak 348.4 MB; iterations 74; \|V\| 3,958,686; \|E\| 4,606,533 | `benchmark/benchmark.json` : `scaling[2].endorserank` |
| Stage n=5,000: AWP | mean 14.514 s, SD 0.264 s; runs 14.640, 14.841, 14.184, 14.594, 14.312; peak 902.6 MB; iterations 91; \|V\| 7,814,870; \|E\| 12,043,690 | `benchmark/benchmark.json` : `scaling[2].awp` |
| Stage n=10,000: EndorseRank | mean 7.096 s, SD 0.142 s; runs 7.064, 7.000, 6.931, 7.265, 7.218; peak 476.3 MB; iterations 76; \|V\| 5,198,375; \|E\| 7,030,772 | `benchmark/benchmark.json` : `scaling[3].endorserank` |
| Stage n=10,000: AWP | mean 21.589 s, SD 0.613 s; runs 20.986, 22.037, 21.046, 22.385, 21.492; peak 1,181.6 MB; iterations 92; \|V\| 9,727,925; \|E\| 20,054,589 | `benchmark/benchmark.json` : `scaling[3].awp` |
| Stage n=20,000: EndorseRank | mean 16.285 s, SD 0.245 s; runs 16.297, 16.098, 16.453, 16.586, 15.990; peak 984.4 MB; iterations 75; \|V\| 10,409,908; \|E\| 15,690,094 | `benchmark/benchmark.json` : `scaling[4].endorserank` |
| Stage n=20,000: AWP | mean 52.004 s, SD 0.790 s; runs 51.618, 52.408, 53.029, 52.024, 50.939; peak 2,643.0 MB; iterations 96; \|V\| 20,865,342; \|E\| 48,796,598 | `benchmark/benchmark.json` : `scaling[4].awp` |
| Stage n=27,844 (reused main measurement): EndorseRank | mean 29.596 s, SD 0.606 s; runs 29.644, 30.210, 29.762, 29.784, 28.582; peak 1,285.0 MB; iterations 84; \|V\| 13,055,150; \|E\| 22,321,470 | `benchmark/benchmark.json` : `scaling[5].endorserank` |
| Stage n=27,844 (reused main measurement): AWP | mean 69.819 s, SD 2.302 s; runs 70.808, 69.357, 73.212, 68.491, 67.226; peak 2,995.9 MB; iterations 93; \|V\| 23,029,298; \|E\| 59,737,617 | `benchmark/benchmark.json` : `scaling[5].awp` |

## Data description (amount shares, monthly counts, GMX contract traders, timing)

| Quantity | Value | Source |
|---|---|---|
| transfers ego | 1,538,404,067 | `describe/describe.json` : `amounts.transfers_ego` |
| transfers ge10 share | 0.9952 | `describe/describe.json` : `amounts.transfers_ge10_share` |
| latest allowances tobs | 28,069,418 | `describe/describe.json` : `amounts.latest_allowances_tobs` |
| allowances ge10 share | 0.9978 | `describe/describe.json` : `amounts.allowances_ge10_share` |
| unlimited allowances | 12,701,544 | `describe/describe.json` : `amounts.unlimited_allowances` |
| unlimited share | 0.4525 | `describe/describe.json` : `amounts.unlimited_share` |
| owners | 13,029,306 | `describe/describe.json` : `amounts.owners` |
| owners with unlimited | 5,798,712 | `describe/describe.json` : `amounts.owners_with_unlimited` |
| owners with both kinds | 1,532,301 | `describe/describe.json` : `amounts.owners_with_both_kinds` |
| plan commit 43d8045 utc | 2026-10-09T13:41:27+00:00 | `describe/describe.json` : `timing.plan_commit_43d8045_utc` |
| scan a | created 2026-10-09T13:41:37+00:00, ended 2026-10-09T13:43:54+00:00 | `describe/describe.json` : `timing.scan_a` |
| registration commit 0d3a057 utc | 2026-10-09T16:49:32+00:00 | `describe/describe.json` : `timing.registration_commit_0d3a057_utc` |
| scan b | created 2026-10-09T16:49:40+00:00, ended 2026-10-09T16:50:11+00:00 | `describe/describe.json` : `timing.scan_b` |
| bigquery usd total | 29.71 | `describe/describe.json` : `timing.bigquery_usd_total` |
| bigquery tib billed | 4.754 | `describe/describe.json` : `timing.bigquery_tib_billed` |
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
| approval_ego 2023-10 | 6,550,552 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2023-11 | 8,249,843 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2023-12 | 8,295,650 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2024-01 | 10,121,473 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2024-02 | 7,735,239 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2024-03 | 12,757,917 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2024-04 | 23,625,463 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2024-05 | 20,926,464 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2024-06 | 14,438,650 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2024-07 | 15,293,846 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2024-08 | 13,937,402 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2024-09 | 10,047,990 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2024-10 | 10,616,817 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2024-11 | 12,370,652 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2024-12 | 14,754,155 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2025-01 | 11,283,677 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2025-02 | 9,026,269 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2025-03 | 12,696,548 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2025-04 | 10,617,469 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2025-05 | 10,655,513 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2025-06 | 10,065,624 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2025-07 | 12,522,333 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2025-08 | 16,674,579 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2025-09 | 12,814,948 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2025-10 | 13,897,714 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2025-11 | 11,139,720 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2025-12 | 17,247,237 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2026-01 | 11,262,167 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2026-02 | 9,912,123 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2026-03 | 9,034,662 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2026-04 | 6,869,236 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2026-05 | 5,677,394 | `describe/describe.json` : `monthly_counts` |
| approval_ego 2026-06 | 8,747,556 | `describe/describe.json` : `monthly_counts` |
| logs_G 2023-10 | 49,527 | `describe/describe.json` : `monthly_counts` |
| logs_G 2023-11 | 32,832 | `describe/describe.json` : `monthly_counts` |
| logs_G 2023-12 | 38,266 | `describe/describe.json` : `monthly_counts` |
| logs_G 2024-01 | 45,244 | `describe/describe.json` : `monthly_counts` |
| logs_G 2024-02 | 36,572 | `describe/describe.json` : `monthly_counts` |
| logs_G 2024-03 | 58,183 | `describe/describe.json` : `monthly_counts` |
| logs_G 2024-04 | 62,113 | `describe/describe.json` : `monthly_counts` |
| logs_G 2024-05 | 41,584 | `describe/describe.json` : `monthly_counts` |
| logs_G 2024-06 | 37,592 | `describe/describe.json` : `monthly_counts` |
| logs_G 2024-07 | 60,369 | `describe/describe.json` : `monthly_counts` |
| logs_G 2024-08 | 59,675 | `describe/describe.json` : `monthly_counts` |
| logs_G 2024-09 | 56,010 | `describe/describe.json` : `monthly_counts` |
| logs_G 2024-10 | 60,616 | `describe/describe.json` : `monthly_counts` |
| logs_G 2024-11 | 100,758 | `describe/describe.json` : `monthly_counts` |
| logs_G 2024-12 | 89,671 | `describe/describe.json` : `monthly_counts` |
| logs_G 2025-01 | 74,619 | `describe/describe.json` : `monthly_counts` |
| logs_G 2025-02 | 74,068 | `describe/describe.json` : `monthly_counts` |
| logs_G 2025-03 | 78,398 | `describe/describe.json` : `monthly_counts` |
| logs_G 2025-04 | 81,774 | `describe/describe.json` : `monthly_counts` |
| logs_G 2025-05 | 85,790 | `describe/describe.json` : `monthly_counts` |
| logs_G 2025-06 | 71,209 | `describe/describe.json` : `monthly_counts` |
| logs_G 2025-07 | 107,619 | `describe/describe.json` : `monthly_counts` |
| logs_G 2025-08 | 110,509 | `describe/describe.json` : `monthly_counts` |
| logs_G 2025-09 | 86,605 | `describe/describe.json` : `monthly_counts` |
| logs_G 2025-10 | 107,090 | `describe/describe.json` : `monthly_counts` |
| logs_G 2025-11 | 86,534 | `describe/describe.json` : `monthly_counts` |
| logs_G 2025-12 | 57,240 | `describe/describe.json` : `monthly_counts` |
| logs_G 2026-01 | 68,537 | `describe/describe.json` : `monthly_counts` |
| logs_G 2026-02 | 66,692 | `describe/describe.json` : `monthly_counts` |
| logs_G 2026-03 | 59,968 | `describe/describe.json` : `monthly_counts` |
| logs_G 2026-04 | 53,554 | `describe/describe.json` : `monthly_counts` |
| logs_G 2026-05 | 59,497 | `describe/describe.json` : `monthly_counts` |
| logs_G 2026-06 | 59,969 | `describe/describe.json` : `monthly_counts` |
| logs_V 2023-10 | 32,453 | `describe/describe.json` : `monthly_counts` |
| logs_V 2023-11 | 33,083 | `describe/describe.json` : `monthly_counts` |
| logs_V 2023-12 | 36,634 | `describe/describe.json` : `monthly_counts` |
| logs_V 2024-01 | 40,702 | `describe/describe.json` : `monthly_counts` |
| logs_V 2024-02 | 47,914 | `describe/describe.json` : `monthly_counts` |
| logs_V 2024-03 | 71,972 | `describe/describe.json` : `monthly_counts` |
| logs_V 2024-04 | 67,540 | `describe/describe.json` : `monthly_counts` |
| logs_V 2024-05 | 67,471 | `describe/describe.json` : `monthly_counts` |
| logs_V 2024-06 | 72,879 | `describe/describe.json` : `monthly_counts` |
| logs_V 2024-07 | 100,779 | `describe/describe.json` : `monthly_counts` |
| logs_V 2024-08 | 106,157 | `describe/describe.json` : `monthly_counts` |
| logs_V 2024-09 | 64,090 | `describe/describe.json` : `monthly_counts` |
| logs_V 2024-10 | 71,934 | `describe/describe.json` : `monthly_counts` |
| logs_V 2024-11 | 126,733 | `describe/describe.json` : `monthly_counts` |
| logs_V 2024-12 | 123,755 | `describe/describe.json` : `monthly_counts` |
| logs_V 2025-01 | 93,449 | `describe/describe.json` : `monthly_counts` |
| logs_V 2025-02 | 108,761 | `describe/describe.json` : `monthly_counts` |
| logs_V 2025-03 | 107,565 | `describe/describe.json` : `monthly_counts` |
| logs_V 2025-04 | 89,350 | `describe/describe.json` : `monthly_counts` |
| logs_V 2025-05 | 95,917 | `describe/describe.json` : `monthly_counts` |
| logs_V 2025-06 | 84,103 | `describe/describe.json` : `monthly_counts` |
| logs_V 2025-07 | 134,233 | `describe/describe.json` : `monthly_counts` |
| logs_V 2025-08 | 142,520 | `describe/describe.json` : `monthly_counts` |
| logs_V 2025-09 | 95,443 | `describe/describe.json` : `monthly_counts` |
| logs_V 2025-10 | 120,416 | `describe/describe.json` : `monthly_counts` |
| logs_V 2025-11 | 106,996 | `describe/describe.json` : `monthly_counts` |
| logs_V 2025-12 | 56,628 | `describe/describe.json` : `monthly_counts` |
| logs_V 2026-01 | 64,924 | `describe/describe.json` : `monthly_counts` |
| logs_V 2026-02 | 75,968 | `describe/describe.json` : `monthly_counts` |
| logs_V 2026-03 | 55,451 | `describe/describe.json` : `monthly_counts` |
| logs_V 2026-04 | 41,395 | `describe/describe.json` : `monthly_counts` |
| logs_V 2026-05 | 37,703 | `describe/describe.json` : `monthly_counts` |
| logs_V 2026-06 | 58,228 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2023-10 | 14,300,580 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2023-11 | 19,268,431 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2023-12 | 20,124,810 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2024-01 | 25,891,066 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2024-02 | 20,149,012 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2024-03 | 36,580,294 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2024-04 | 61,441,344 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2024-05 | 47,956,506 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2024-06 | 39,909,928 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2024-07 | 51,109,579 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2024-08 | 56,517,663 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2024-09 | 40,576,538 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2024-10 | 45,102,719 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2024-11 | 63,978,880 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2024-12 | 63,416,248 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2025-01 | 55,093,057 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2025-02 | 55,205,950 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2025-03 | 60,153,290 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2025-04 | 55,610,632 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2025-05 | 68,388,497 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2025-06 | 56,826,671 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2025-07 | 64,444,756 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2025-08 | 67,702,627 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2025-09 | 49,695,846 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2025-10 | 59,438,422 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2025-11 | 53,361,692 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2025-12 | 57,949,683 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2026-01 | 62,732,053 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2026-02 | 41,069,636 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2026-03 | 33,959,783 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2026-04 | 28,192,517 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2026-05 | 26,591,803 | `describe/describe.json` : `monthly_counts` |
| transfer_ego 2026-06 | 35,663,554 | `describe/describe.json` : `monthly_counts` |
