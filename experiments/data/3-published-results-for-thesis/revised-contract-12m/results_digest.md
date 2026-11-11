# Results digest

Written by `experiments/scripts/publish_results.py` on 2026-11-11 03:27 UTC from the summaries in this folder; nothing here is recomputed. Each row names the file (relative to this folder) and the key inside it. τ entries read `point [95% CI]`, contrasts `Δτ [95% CI]; τa, τb; P(Δτ>0)`, and `B` is the number of bootstrap resamples behind the interval. `SHA256SUMS.txt` lists the checksums of every file published here.

**Contract-graph analysis** (docs/revision_contract_graph.md and docs/discovery_protocol.md, on top of docs/revision_one_year_window.md and docs/revision_price_weighting.md): graphs whose nodes are contracts other than smart accounts, with edges read from the whole chain; amounts in USD over the five selected tokens; scores from the twelve months before each freeze (T_obs and W1: 2025-07-01 to 2026-06-30; W0: 2025-04-01 to 2026-03-31); each allowance counted up to its owner's balance at the freeze; constants set on the contract graph; and the discovery-order test. All of it was defined after the registered results were known, so every result here is post hoc. Nothing in this digest is a registered result; the registered digest is in the parent folder.

- Code revision: `bb78da330d39a430c54922ba41c6da9e98e02e5d`
- Published files: `same-window/eval_summary.json`, `holdout-w0/eval_summary.json`, `window-w1/eval_summary.json`, `discovery/discovery_tobs_both.json`, `discovery/discovery_tobs_out.json`, `discovery/discovery_t1_both.json`, `discovery/discovery_t1_out.json`, `discovery/feasibility_t1.json`, `sybil-model/sybil_model.json`, `robustness/robustness.json`, `benchmark/benchmark.json`, `supplementary/supplementary.json`, `describe/describe.json`, `cohort/matched_cohort.json`, `cohort/cohort_t1.json`, `cohort/spenders_w0.json`, `cohort/spenders_w1.json`, `typing/balance_audit.json`, `typing/c12_account_types.json`, `typing/c12_smart_account_reads.json`, `run_manifest.json`, `config/contract_reputation.yaml`, `config/overlay_contract12m.yaml`, `docs/analysis_plan.md`, `docs/registration_w1.md`, `docs/revision_price_weighting.md`, `docs/revision_one_year_window.md`, `docs/revision_contract_graph.md`, `docs/discovery_protocol.md`, `usd/listed_tokens.csv`, `usd/usd_inputs.json`, `usd/constants.json`, `usd/chainlink_check.json`

## 1. Data, account types, cohorts and graph sizes

| Quantity | Value | Source |
|---|---|---|
| Events: five token rows | 1,240,275,042 | `describe/describe.json` : `events.five_token_rows` |
| Events: distinct pairs | 73,058,133 | `describe/describe.json` : `events.distinct_pairs` |
| Events: addresses | 25,537,280 | `describe/describe.json` : `events.addresses` |
| Events: transaction senders | 17,477,779 | `describe/describe.json` : `events.transaction_senders` |
| Events: rpc queue | 6,230,270 | `describe/describe.json` : `events.rpc_queue` |
| Events: contracts | 1,829,719 | `describe/describe.json` : `events.contracts` |
| Events: user accounts | 21,877,279 | `describe/describe.json` : `events.user_accounts` |
| Events: rows between contracts | 603,475,784 | `describe/describe.json` : `events.rows_between_contracts` |
| Events: latest allowances between contracts both freezes | 648,204 | `describe/describe.json` : `events.latest_allowances_between_contracts_both_freezes` |
| Events: user account rows toward contracts | 152,257,072 | `describe/describe.json` : `events.user_account_rows_toward_contracts` |
| Account types: block | 513216506 | `describe/describe.json` : `account_types.block` |
| Account types: addresses | 6,230,270 | `describe/describe.json` : `account_types.addresses` |
| Account types: aborted addresses | 0 | `describe/describe.json` : `account_types.aborted_addresses` |
| Account types: audit senders with code | 0 | `describe/describe.json` : `account_types.audit_senders_with_code` |
| Account types: read from | 2026-11-07T09:47:01+00:00 | `describe/describe.json` : `account_types.read_from` |
| Account types: read until | 2026-11-08T12:49:57+00:00 | `describe/describe.json` : `account_types.read_until` |
| Account types, code kind: none | 2,909,509 | `describe/describe.json` : `account_types.code_kind.none` |
| Account types, code kind: contract | 2,155,736 | `describe/describe.json` : `account_types.code_kind.contract` |
| Account types, code kind: eip7702 | 1,165,025 | `describe/describe.json` : `account_types.code_kind.eip7702` |
| Account types, typed: eoa | 2,909,509 | `describe/describe.json` : `account_types.typed.eoa` |
| Account types, typed: contract | 2,022,375 | `describe/describe.json` : `account_types.typed.contract` |
| Account types, typed: eoa_7702 | 1,165,025 | `describe/describe.json` : `account_types.typed.eoa_7702` |
| Account types, typed: smart_account | 133,361 | `describe/describe.json` : `account_types.typed.smart_account` |
| Account types, wallet kind typed: erc4337 | 87,157 | `describe/describe.json` : `account_types.wallet_kind_typed.erc4337` |
| Account types, wallet kind typed: safe | 46,204 | `describe/describe.json` : `account_types.wallet_kind_typed.safe` |
| Account types, proxy kind: none | 5,156,938 | `describe/describe.json` : `account_types.proxy_kind.none` |
| Account types, proxy kind: erc1967 | 524,454 | `describe/describe.json` : `account_types.proxy_kind.erc1967` |
| Account types, proxy kind: eip1167 | 503,516 | `describe/describe.json` : `account_types.proxy_kind.eip1167` |
| Account types, proxy kind: safe | 45,362 | `describe/describe.json` : `account_types.proxy_kind.safe` |
| Account types, extension: moved | 192,656 | `describe/describe.json` : `account_types.extension.moved` |
| Account types, extension: by_code_hash | 37,337 | `describe/describe.json` : `account_types.extension.by_code_hash` |
| Account types, extension: by_implementation | 155,319 | `describe/describe.json` : `account_types.extension.by_implementation` |
| Account types, after extension: eoa | 2,909,509 | `describe/describe.json` : `account_types.after_extension.eoa` |
| Account types, after extension: contract | 1,829,719 | `describe/describe.json` : `account_types.after_extension.contract` |
| Account types, after extension: eoa_7702 | 1,165,025 | `describe/describe.json` : `account_types.after_extension.eoa_7702` |
| Account types, after extension: smart_account | 326,017 | `describe/describe.json` : `account_types.after_extension.smart_account` |
| Account types, wallet kind after extension: erc4337 | 279,813 | `describe/describe.json` : `account_types.wallet_kind_after_extension.erc4337` |
| Account types, wallet kind after extension: safe | 46,204 | `describe/describe.json` : `account_types.wallet_kind_after_extension.safe` |
| Nodes of the contract graph: contracts | 1,403,959 | `describe/describe.json` : `nodes.contracts` |
| Nodes of the contract graph: is cohort | 6,443 | `describe/describe.json` : `nodes.is_cohort` |
| Nodes of the contract graph: is cohort t1 | 6,292 | `describe/describe.json` : `nodes.is_cohort_t1` |
| Nodes of the contract graph: is spender w0 | 7,864 | `describe/describe.json` : `nodes.is_spender_w0` |
| Nodes of the contract graph: is spender w1 | 7,915 | `describe/describe.json` : `nodes.is_spender_w1` |
| Pairs at tobs, allowance capped: pairs | 115,006 | `describe/describe.json` : `pairs.tobs.allowance_capped.pairs` |
| Pairs at tobs, allowance capped: self pairs | 25 | `describe/describe.json` : `pairs.tobs.allowance_capped.self_pairs` |
| Pairs at tobs, allowance capped: sources | 9,459 | `describe/describe.json` : `pairs.tobs.allowance_capped.sources` |
| Pairs at tobs, allowance capped: destinations | 100,112 | `describe/describe.json` : `pairs.tobs.allowance_capped.destinations` |
| Pairs at tobs, allowance capped: positive w er | 114,997 | `describe/describe.json` : `pairs.tobs.allowance_capped.positive_w_er` |
| Pairs at tobs, allowance capped: positive w raw | 115,006 | `describe/describe.json` : `pairs.tobs.allowance_capped.positive_w_raw` |
| Pairs at tobs, allowance capped: largest source pairs | 98,073 | `describe/describe.json` : `pairs.tobs.allowance_capped.largest_source_pairs` |
| Pairs at tobs, allowance capped: largest destination pairs | 2,097 | `describe/describe.json` : `pairs.tobs.allowance_capped.largest_destination_pairs` |
| Pairs at tobs, allowance capped: pairs of ten largest sources | 99,039 | `describe/describe.json` : `pairs.tobs.allowance_capped.pairs_of_ten_largest_sources` |
| Pairs at tobs, allowance uncapped: pairs | 302,559 | `describe/describe.json` : `pairs.tobs.allowance_uncapped.pairs` |
| Pairs at tobs, allowance uncapped: self pairs | 121 | `describe/describe.json` : `pairs.tobs.allowance_uncapped.self_pairs` |
| Pairs at tobs, allowance uncapped: sources | 141,974 | `describe/describe.json` : `pairs.tobs.allowance_uncapped.sources` |
| Pairs at tobs, allowance uncapped: destinations | 108,825 | `describe/describe.json` : `pairs.tobs.allowance_uncapped.destinations` |
| Pairs at tobs, allowance uncapped: positive w er | 302,543 | `describe/describe.json` : `pairs.tobs.allowance_uncapped.positive_w_er` |
| Pairs at tobs, allowance uncapped: positive w raw | 302,559 | `describe/describe.json` : `pairs.tobs.allowance_uncapped.positive_w_raw` |
| Pairs at tobs, allowance uncapped: largest source pairs | 98,073 | `describe/describe.json` : `pairs.tobs.allowance_uncapped.largest_source_pairs` |
| Pairs at tobs, allowance uncapped: largest destination pairs | 28,082 | `describe/describe.json` : `pairs.tobs.allowance_uncapped.largest_destination_pairs` |
| Pairs at tobs, allowance uncapped: pairs of ten largest sources | 102,409 | `describe/describe.json` : `pairs.tobs.allowance_uncapped.pairs_of_ten_largest_sources` |
| Pairs at tobs, transfer: pairs | 2,580,709 | `describe/describe.json` : `pairs.tobs.transfer.pairs` |
| Pairs at tobs, transfer: self pairs | 15,596 | `describe/describe.json` : `pairs.tobs.transfer.self_pairs` |
| Pairs at tobs, transfer: sources | 1,007,310 | `describe/describe.json` : `pairs.tobs.transfer.sources` |
| Pairs at tobs, transfer: destinations | 801,813 | `describe/describe.json` : `pairs.tobs.transfer.destinations` |
| Pairs at tobs, transfer: positive w awp | 2,580,381 | `describe/describe.json` : `pairs.tobs.transfer.positive_w_awp` |
| Pairs at tobs, transfer: positive w raw | 2,580,709 | `describe/describe.json` : `pairs.tobs.transfer.positive_w_raw` |
| Pairs at tobs, transfer: largest source pairs | 130,667 | `describe/describe.json` : `pairs.tobs.transfer.largest_source_pairs` |
| Pairs at tobs, transfer: largest destination pairs | 441,612 | `describe/describe.json` : `pairs.tobs.transfer.largest_destination_pairs` |
| Pairs at tobs, transfer: pairs of ten largest sources | 644,889 | `describe/describe.json` : `pairs.tobs.transfer.pairs_of_ten_largest_sources` |
| Pairs at t1, allowance capped: pairs | 17,940 | `describe/describe.json` : `pairs.t1.allowance_capped.pairs` |
| Pairs at t1, allowance capped: self pairs | 35 | `describe/describe.json` : `pairs.t1.allowance_capped.self_pairs` |
| Pairs at t1, allowance capped: sources | 10,153 | `describe/describe.json` : `pairs.t1.allowance_capped.sources` |
| Pairs at t1, allowance capped: destinations | 2,050 | `describe/describe.json` : `pairs.t1.allowance_capped.destinations` |
| Pairs at t1, allowance capped: positive w er | 17,933 | `describe/describe.json` : `pairs.t1.allowance_capped.positive_w_er` |
| Pairs at t1, allowance capped: positive w raw | 17,940 | `describe/describe.json` : `pairs.t1.allowance_capped.positive_w_raw` |
| Pairs at t1, allowance capped: largest source pairs | 256 | `describe/describe.json` : `pairs.t1.allowance_capped.largest_source_pairs` |
| Pairs at t1, allowance capped: largest destination pairs | 2,008 | `describe/describe.json` : `pairs.t1.allowance_capped.largest_destination_pairs` |
| Pairs at t1, allowance capped: pairs of ten largest sources | 948 | `describe/describe.json` : `pairs.t1.allowance_capped.pairs_of_ten_largest_sources` |
| Pairs at t1, allowance uncapped: pairs | 275,917 | `describe/describe.json` : `pairs.t1.allowance_uncapped.pairs` |
| Pairs at t1, allowance uncapped: self pairs | 155 | `describe/describe.json` : `pairs.t1.allowance_uncapped.self_pairs` |
| Pairs at t1, allowance uncapped: sources | 140,327 | `describe/describe.json` : `pairs.t1.allowance_uncapped.sources` |
| Pairs at t1, allowance uncapped: destinations | 89,727 | `describe/describe.json` : `pairs.t1.allowance_uncapped.destinations` |
| Pairs at t1, allowance uncapped: positive w er | 275,903 | `describe/describe.json` : `pairs.t1.allowance_uncapped.positive_w_er` |
| Pairs at t1, allowance uncapped: positive w raw | 275,917 | `describe/describe.json` : `pairs.t1.allowance_uncapped.positive_w_raw` |
| Pairs at t1, allowance uncapped: largest source pairs | 78,382 | `describe/describe.json` : `pairs.t1.allowance_uncapped.largest_source_pairs` |
| Pairs at t1, allowance uncapped: largest destination pairs | 25,810 | `describe/describe.json` : `pairs.t1.allowance_uncapped.largest_destination_pairs` |
| Pairs at t1, allowance uncapped: pairs of ten largest sources | 82,707 | `describe/describe.json` : `pairs.t1.allowance_uncapped.pairs_of_ten_largest_sources` |
| Pairs at t1, transfer: pairs | 2,269,073 | `describe/describe.json` : `pairs.t1.transfer.pairs` |
| Pairs at t1, transfer: self pairs | 11,430 | `describe/describe.json` : `pairs.t1.transfer.self_pairs` |
| Pairs at t1, transfer: sources | 873,388 | `describe/describe.json` : `pairs.t1.transfer.sources` |
| Pairs at t1, transfer: destinations | 626,356 | `describe/describe.json` : `pairs.t1.transfer.destinations` |
| Pairs at t1, transfer: positive w awp | 2,268,818 | `describe/describe.json` : `pairs.t1.transfer.positive_w_awp` |
| Pairs at t1, transfer: positive w raw | 2,269,073 | `describe/describe.json` : `pairs.t1.transfer.positive_w_raw` |
| Pairs at t1, transfer: largest source pairs | 121,708 | `describe/describe.json` : `pairs.t1.transfer.largest_source_pairs` |
| Pairs at t1, transfer: largest destination pairs | 439,299 | `describe/describe.json` : `pairs.t1.transfer.largest_destination_pairs` |
| Pairs at t1, transfer: pairs of ten largest sources | 536,380 | `describe/describe.json` : `pairs.t1.transfer.pairs_of_ten_largest_sources` |
| matched_cohort: rule | the members of u12_cohort_tobs that are not user accounts (docs/revision_contract_graph.md section 8) | `cohort/matched_cohort.json` : `rule` |
| matched_cohort: listed | 6,483 | `cohort/matched_cohort.json` : `listed` |
| matched_cohort: cohort | 6,443 | `cohort/matched_cohort.json` : `cohort` |
| matched_cohort: contracts in nodes | 6,443 | `cohort/matched_cohort.json` : `contracts_in_nodes` |
| matched_cohort, by class: contract | 6,443 | `cohort/matched_cohort.json` : `by_class.contract` |
| matched_cohort, by class: user_account | 40 | `cohort/matched_cohort.json` : `by_class.user_account` |
| matched_cohort, user accounts by source: rpc_smart_account | 40 | `cohort/matched_cohort.json` : `user_accounts_by_source.rpc_smart_account` |
| cohort_t1: rule | the members of u12_cohort_t1 that are not user accounts (docs/revision_contract_graph.md section 8) | `cohort/cohort_t1.json` : `rule` |
| cohort_t1: listed | 6,343 | `cohort/cohort_t1.json` : `listed` |
| cohort_t1: cohort | 6,292 | `cohort/cohort_t1.json` : `cohort` |
| cohort_t1: contracts in nodes | 6,292 | `cohort/cohort_t1.json` : `contracts_in_nodes` |
| cohort_t1, by class: contract | 6,292 | `cohort/cohort_t1.json` : `by_class.contract` |
| cohort_t1, by class: user_account | 51 | `cohort/cohort_t1.json` : `by_class.user_account` |
| cohort_t1, user accounts by source: rpc_smart_account | 51 | `cohort/cohort_t1.json` : `user_accounts_by_source.rpc_smart_account` |
| spenders_w0: rule | the spenders of u12_labels_w0 that are contracts (docs/revision_contract_graph.md section 8) | `cohort/spenders_w0.json` : `rule` |
| spenders_w0: listed | 7,962 | `cohort/spenders_w0.json` : `listed` |
| spenders_w0: cohort | 7,864 | `cohort/spenders_w0.json` : `cohort` |
| spenders_w0: contracts in nodes | 7,864 | `cohort/spenders_w0.json` : `contracts_in_nodes` |
| spenders_w0, by class: contract | 7,864 | `cohort/spenders_w0.json` : `by_class.contract` |
| spenders_w0, by class: system | 1 | `cohort/spenders_w0.json` : `by_class.system` |
| spenders_w0, by class: user_account | 97 | `cohort/spenders_w0.json` : `by_class.user_account` |
| spenders_w0, user accounts by source: rpc_eoa | 5 | `cohort/spenders_w0.json` : `user_accounts_by_source.rpc_eoa` |
| spenders_w0, user accounts by source: rpc_eoa_7702 | 1 | `cohort/spenders_w0.json` : `user_accounts_by_source.rpc_eoa_7702` |
| spenders_w0, user accounts by source: rpc_smart_account | 50 | `cohort/spenders_w0.json` : `user_accounts_by_source.rpc_smart_account` |
| spenders_w0, user accounts by source: tx_sender | 41 | `cohort/spenders_w0.json` : `user_accounts_by_source.tx_sender` |
| spenders_w1: rule | the spenders of u12_labels_w1 that are contracts (docs/revision_contract_graph.md section 8) | `cohort/spenders_w1.json` : `rule` |
| spenders_w1: listed | 7,995 | `cohort/spenders_w1.json` : `listed` |
| spenders_w1: cohort | 7,915 | `cohort/spenders_w1.json` : `cohort` |
| spenders_w1: contracts in nodes | 7,915 | `cohort/spenders_w1.json` : `contracts_in_nodes` |
| spenders_w1, by class: contract | 7,915 | `cohort/spenders_w1.json` : `by_class.contract` |
| spenders_w1, by class: system | 1 | `cohort/spenders_w1.json` : `by_class.system` |
| spenders_w1, by class: user_account | 79 | `cohort/spenders_w1.json` : `by_class.user_account` |
| spenders_w1, user accounts by source: rpc_eoa | 3 | `cohort/spenders_w1.json` : `user_accounts_by_source.rpc_eoa` |
| spenders_w1, user accounts by source: rpc_eoa_7702 | 1 | `cohort/spenders_w1.json` : `user_accounts_by_source.rpc_eoa_7702` |
| spenders_w1, user accounts by source: rpc_smart_account | 45 | `cohort/spenders_w1.json` : `user_accounts_by_source.rpc_smart_account` |
| spenders_w1, user accounts by source: tx_sender | 30 | `cohort/spenders_w1.json` : `user_accounts_by_source.tx_sender` |
| Anchor T_obs | 2026-06-30 23:59:59 UTC | `same-window/eval_summary.json` : `anchor` |
| Cohort scored in the same window | 6,443 | `same-window/eval_summary.json` : `cohort` |
| T_obs allowance graph (pairs of positive weight), nodes | 109,389 | `same-window/eval_summary.json` : `graph.allowance.nodes` |
| T_obs allowance graph (pairs of positive weight), edges | 114,997 | `same-window/eval_summary.json` : `graph.allowance.edges` |
| T_obs transfer graph (pairs of positive weight), nodes | 1,298,724 | `same-window/eval_summary.json` : `graph.transfer.nodes` |
| T_obs transfer graph (pairs of positive weight), edges | 2,580,381 | `same-window/eval_summary.json` : `graph.transfer.edges` |
| Cohort contracts outside the allowance graph | 5,193 | `same-window/eval_summary.json` : `graph.cohort_outside_allowance` |
| Cohort contracts outside the transfer graph | 2,384 | `same-window/eval_summary.json` : `graph.cohort_outside_transfer` |
| Cohort contracts outside both graphs | 2,173 | `same-window/eval_summary.json` : `graph.cohort_outside_both` |
| T_obs union graph, pairs | 2,575,632 | `same-window/eval_summary.json` : `union_graph.pairs` |
| T_obs union graph, nodes | 1,299,438 | `same-window/eval_summary.json` : `union_graph.nodes` |
| Power iterations at T_obs, EndorseRank | 56 | `same-window/eval_summary.json` : `iterations.endorserank` |
| Power iterations at T_obs, EndorseRank (activity restarts) | 110 | `same-window/eval_summary.json` : `iterations.endorserank_activity` |
| Power iterations at T_obs, AWP | 98 | `same-window/eval_summary.json` : `iterations.awp` |
| Power iterations at T_obs, C-PR (λ=1) | 56 | `same-window/eval_summary.json` : `iterations.cpr_l100` |
| Power iterations at T_obs, C-PR (λ=0) | 91 | `same-window/eval_summary.json` : `iterations.cpr_l0` |
| Power iterations at T_obs, C-PR (λ=0.25) | 92 | `same-window/eval_summary.json` : `iterations.cpr_l25` |
| Power iterations at T_obs, C-PR (λ=0.5) | 92 | `same-window/eval_summary.json` : `iterations.cpr_l50` |
| Power iterations at T_obs, C-PR (λ=0.75) | 92 | `same-window/eval_summary.json` : `iterations.cpr_l75` |
| Power iterations at T_obs, S-PR | 153 | `same-window/eval_summary.json` : `iterations.spr` |
| t1 graph, allowance edges | 17,940 | `holdout-w0/eval_summary.json` : `graph.allowance_edges` |
| t1 graph, transfer edges | 2,269,073 | `holdout-w0/eval_summary.json` : `graph.transfer_edges` |
| t1 union graph, pairs | 2,269,421 | `holdout-w0/eval_summary.json` : `union_graph.pairs` |
| t1 union graph, nodes | 1,111,554 | `holdout-w0/eval_summary.json` : `union_graph.nodes` |
| Power iterations at t1, EndorseRank | 70 | `holdout-w0/eval_summary.json` : `iterations.endorserank` |
| Power iterations at t1, EndorseRank (activity restarts) | 68 | `holdout-w0/eval_summary.json` : `iterations.endorserank_activity` |
| Power iterations at t1, AWP | 94 | `holdout-w0/eval_summary.json` : `iterations.awp` |
| Power iterations at t1, C-PR (λ=1) | 70 | `holdout-w0/eval_summary.json` : `iterations.cpr_l100` |
| Power iterations at t1, C-PR (λ=0) | 84 | `holdout-w0/eval_summary.json` : `iterations.cpr_l0` |
| Power iterations at t1, C-PR (λ=0.25) | 85 | `holdout-w0/eval_summary.json` : `iterations.cpr_l25` |
| Power iterations at t1, C-PR (λ=0.5) | 86 | `holdout-w0/eval_summary.json` : `iterations.cpr_l50` |
| Power iterations at t1, C-PR (λ=0.75) | 85 | `holdout-w0/eval_summary.json` : `iterations.cpr_l75` |
| Power iterations at t1, S-PR | 163 | `holdout-w0/eval_summary.json` : `iterations.spr` |

## 2. Same-window families (matched cohort)

Family mean of Kendall τ_b with its 95% percentile interval (paired bootstrap over contracts).

| Quantity | Value | Source |
|---|---|---|
| EndorseRank, transfer family | 0.297 [0.280, 0.317]; B=400 | `same-window/eval_summary.json` : `families.endorserank.transfer` |
| EndorseRank, allowance family | 0.839 [0.828, 0.849]; B=400 | `same-window/eval_summary.json` : `families.endorserank.allowance` |
| EndorseRank, Sybil stability family | 0.220 [0.206, 0.237]; B=400 | `same-window/eval_summary.json` : `families.endorserank.sybil_stability` |
| EndorseRank (activity restarts), transfer family | 0.299 [0.281, 0.318]; B=400 | `same-window/eval_summary.json` : `families.endorserank_activity.transfer` |
| EndorseRank (activity restarts), allowance family | 0.799 [0.782, 0.813]; B=400 | `same-window/eval_summary.json` : `families.endorserank_activity.allowance` |
| EndorseRank (activity restarts), Sybil stability family | 0.225 [0.210, 0.242]; B=400 | `same-window/eval_summary.json` : `families.endorserank_activity.sybil_stability` |
| AWP, transfer family | 0.755 [0.748, 0.762]; B=400 | `same-window/eval_summary.json` : `families.awp.transfer` |
| AWP, allowance family | 0.227 [0.206, 0.245]; B=400 | `same-window/eval_summary.json` : `families.awp.allowance` |
| AWP, Sybil stability family | 0.643 [0.635, 0.651]; B=400 | `same-window/eval_summary.json` : `families.awp.sybil_stability` |
| C-PR (λ=1), transfer family | 0.298 [0.281, 0.318]; B=400 | `same-window/eval_summary.json` : `families.cpr_l100.transfer` |
| C-PR (λ=1), allowance family | 0.838 [0.827, 0.850]; B=400 | `same-window/eval_summary.json` : `families.cpr_l100.allowance` |
| C-PR (λ=1), Sybil stability family | 0.222 [0.207, 0.238]; B=400 | `same-window/eval_summary.json` : `families.cpr_l100.sybil_stability` |
| C-PR (λ=0), transfer family | 0.804 [0.799, 0.809]; B=400 | `same-window/eval_summary.json` : `families.cpr_l0.transfer` |
| C-PR (λ=0), allowance family | 0.238 [0.218, 0.258]; B=400 | `same-window/eval_summary.json` : `families.cpr_l0.allowance` |
| C-PR (λ=0), Sybil stability family | 0.637 [0.628, 0.646]; B=400 | `same-window/eval_summary.json` : `families.cpr_l0.sybil_stability` |
| C-PR (λ=0.25), transfer family | 0.742 [0.734, 0.751]; B=400 | `same-window/eval_summary.json` : `families.cpr_l25.transfer` |
| C-PR (λ=0.25), allowance family | 0.424 [0.411, 0.437]; B=400 | `same-window/eval_summary.json` : `families.cpr_l25.allowance` |
| C-PR (λ=0.25), Sybil stability family | 0.577 [0.567, 0.588]; B=400 | `same-window/eval_summary.json` : `families.cpr_l25.sybil_stability` |
| C-PR (λ=0.5), transfer family | 0.738 [0.729, 0.747]; B=400 | `same-window/eval_summary.json` : `families.cpr_l50.transfer` |
| C-PR (λ=0.5), allowance family | 0.433 [0.419, 0.445]; B=400 | `same-window/eval_summary.json` : `families.cpr_l50.allowance` |
| C-PR (λ=0.5), Sybil stability family | 0.574 [0.564, 0.585]; B=400 | `same-window/eval_summary.json` : `families.cpr_l50.sybil_stability` |
| C-PR (λ=0.75), transfer family | 0.734 [0.725, 0.743]; B=400 | `same-window/eval_summary.json` : `families.cpr_l75.transfer` |
| C-PR (λ=0.75), allowance family | 0.438 [0.424, 0.450]; B=400 | `same-window/eval_summary.json` : `families.cpr_l75.allowance` |
| C-PR (λ=0.75), Sybil stability family | 0.572 [0.561, 0.583]; B=400 | `same-window/eval_summary.json` : `families.cpr_l75.sybil_stability` |
| S-PR, transfer family | 0.782 [0.773, 0.791]; B=400 | `same-window/eval_summary.json` : `families.spr.transfer` |
| S-PR, allowance family | 0.371 [0.350, 0.391]; B=400 | `same-window/eval_summary.json` : `families.spr.allowance` |
| S-PR, Sybil stability family | 0.584 [0.575, 0.593]; B=400 | `same-window/eval_summary.json` : `families.spr.sybil_stability` |

### Per proxy (τ_b [95% CI]; Spearman ρ)

| Quantity | Value | Source |
|---|---|---|
| EndorseRank, in_degree | 0.305 [0.287, 0.326]; ρ 0.345; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank.in_degree` |
| EndorseRank, in_value | 0.289 [0.269, 0.309]; ρ 0.338; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank.in_value` |
| EndorseRank, in_approve_degree | 0.847 [0.835, 0.857]; ρ 0.883; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank.in_approve_degree` |
| EndorseRank, in_approve_value | 0.831 [0.820, 0.841]; ρ 0.882; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank.in_approve_value` |
| EndorseRank, inbound_counterparty_ratio | 0.148 [0.130, 0.166]; ρ 0.177; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank.inbound_counterparty_ratio` |
| EndorseRank, transfer_tenure_days | 0.271 [0.253, 0.289]; ρ 0.317; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank.transfer_tenure_days` |
| EndorseRank, active_months | 0.243 [0.224, 0.262]; ρ 0.281; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank.active_months` |
| EndorseRank (activity restarts), in_degree | 0.306 [0.288, 0.327]; ρ 0.348; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank_activity.in_degree` |
| EndorseRank (activity restarts), in_value | 0.291 [0.271, 0.310]; ρ 0.342; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank_activity.in_value` |
| EndorseRank (activity restarts), in_approve_degree | 0.814 [0.798, 0.828]; ρ 0.842; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank_activity.in_approve_degree` |
| EndorseRank (activity restarts), in_approve_value | 0.783 [0.767, 0.797]; ρ 0.837; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank_activity.in_approve_value` |
| EndorseRank (activity restarts), inbound_counterparty_ratio | 0.149 [0.131, 0.168]; ρ 0.179; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank_activity.inbound_counterparty_ratio` |
| EndorseRank (activity restarts), transfer_tenure_days | 0.278 [0.260, 0.296]; ρ 0.325; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank_activity.transfer_tenure_days` |
| EndorseRank (activity restarts), active_months | 0.249 [0.231, 0.268]; ρ 0.289; B=400 | `same-window/eval_summary.json` : `per_proxy.endorserank_activity.active_months` |
| AWP, in_degree | 0.764 [0.757, 0.772]; ρ 0.873; B=400 | `same-window/eval_summary.json` : `per_proxy.awp.in_degree` |
| AWP, in_value | 0.746 [0.738, 0.754]; ρ 0.872; B=400 | `same-window/eval_summary.json` : `per_proxy.awp.in_value` |
| AWP, in_approve_degree | 0.229 [0.207, 0.248]; ρ 0.271; B=400 | `same-window/eval_summary.json` : `per_proxy.awp.in_approve_degree` |
| AWP, in_approve_value | 0.225 [0.204, 0.243]; ρ 0.269; B=400 | `same-window/eval_summary.json` : `per_proxy.awp.in_approve_value` |
| AWP, inbound_counterparty_ratio | 0.428 [0.414, 0.443]; ρ 0.648; B=400 | `same-window/eval_summary.json` : `per_proxy.awp.inbound_counterparty_ratio` |
| AWP, transfer_tenure_days | 0.711 [0.702, 0.719]; ρ 0.862; B=400 | `same-window/eval_summary.json` : `per_proxy.awp.transfer_tenure_days` |
| AWP, active_months | 0.789 [0.781, 0.797]; ρ 0.917; B=400 | `same-window/eval_summary.json` : `per_proxy.awp.active_months` |
| C-PR (λ=1), in_degree | 0.306 [0.287, 0.327]; ρ 0.346; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l100.in_degree` |
| C-PR (λ=1), in_value | 0.291 [0.272, 0.311]; ρ 0.341; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l100.in_value` |
| C-PR (λ=1), in_approve_degree | 0.846 [0.835, 0.857]; ρ 0.882; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l100.in_approve_degree` |
| C-PR (λ=1), in_approve_value | 0.831 [0.820, 0.841]; ρ 0.881; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l100.in_approve_value` |
| C-PR (λ=1), inbound_counterparty_ratio | 0.148 [0.130, 0.166]; ρ 0.177; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l100.inbound_counterparty_ratio` |
| C-PR (λ=1), transfer_tenure_days | 0.273 [0.255, 0.291]; ρ 0.319; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l100.transfer_tenure_days` |
| C-PR (λ=1), active_months | 0.244 [0.225, 0.264]; ρ 0.283; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l100.active_months` |
| C-PR (λ=0), in_degree | 0.792 [0.786, 0.798]; ρ 0.914; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l0.in_degree` |
| C-PR (λ=0), in_value | 0.816 [0.810, 0.821]; ρ 0.928; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l0.in_value` |
| C-PR (λ=0), in_approve_degree | 0.238 [0.218, 0.258]; ρ 0.280; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l0.in_approve_degree` |
| C-PR (λ=0), in_approve_value | 0.238 [0.218, 0.257]; ρ 0.281; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l0.in_approve_value` |
| C-PR (λ=0), inbound_counterparty_ratio | 0.501 [0.487, 0.515]; ρ 0.746; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l0.inbound_counterparty_ratio` |
| C-PR (λ=0), transfer_tenure_days | 0.660 [0.651, 0.669]; ρ 0.815; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l0.transfer_tenure_days` |
| C-PR (λ=0), active_months | 0.749 [0.739, 0.758]; ρ 0.884; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l0.active_months` |
| C-PR (λ=0.25), in_degree | 0.736 [0.727, 0.746]; ρ 0.852; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l25.in_degree` |
| C-PR (λ=0.25), in_value | 0.749 [0.740, 0.758]; ρ 0.863; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l25.in_value` |
| C-PR (λ=0.25), in_approve_degree | 0.430 [0.416, 0.442]; ρ 0.503; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l25.in_approve_degree` |
| C-PR (λ=0.25), in_approve_value | 0.419 [0.406, 0.431]; ρ 0.499; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l25.in_approve_value` |
| C-PR (λ=0.25), inbound_counterparty_ratio | 0.447 [0.433, 0.463]; ρ 0.672; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l25.inbound_counterparty_ratio` |
| C-PR (λ=0.25), transfer_tenure_days | 0.607 [0.597, 0.619]; ρ 0.755; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l25.transfer_tenure_days` |
| C-PR (λ=0.25), active_months | 0.676 [0.663, 0.690]; ρ 0.804; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l25.active_months` |
| C-PR (λ=0.5), in_degree | 0.732 [0.723, 0.742]; ρ 0.848; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l50.in_degree` |
| C-PR (λ=0.5), in_value | 0.743 [0.734, 0.752]; ρ 0.857; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l50.in_value` |
| C-PR (λ=0.5), in_approve_degree | 0.439 [0.425, 0.451]; ρ 0.513; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l50.in_approve_degree` |
| C-PR (λ=0.5), in_approve_value | 0.427 [0.414, 0.439]; ρ 0.509; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l50.in_approve_value` |
| C-PR (λ=0.5), inbound_counterparty_ratio | 0.446 [0.432, 0.461]; ρ 0.669; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l50.inbound_counterparty_ratio` |
| C-PR (λ=0.5), transfer_tenure_days | 0.604 [0.592, 0.615]; ρ 0.750; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l50.transfer_tenure_days` |
| C-PR (λ=0.5), active_months | 0.672 [0.659, 0.687]; ρ 0.799; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l50.active_months` |
| C-PR (λ=0.75), in_degree | 0.730 [0.721, 0.740]; ρ 0.845; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l75.in_degree` |
| C-PR (λ=0.75), in_value | 0.738 [0.729, 0.747]; ρ 0.853; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l75.in_value` |
| C-PR (λ=0.75), in_approve_degree | 0.444 [0.430, 0.457]; ρ 0.518; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l75.in_approve_degree` |
| C-PR (λ=0.75), in_approve_value | 0.432 [0.419, 0.444]; ρ 0.515; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l75.in_approve_value` |
| C-PR (λ=0.75), inbound_counterparty_ratio | 0.445 [0.431, 0.461]; ρ 0.667; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l75.inbound_counterparty_ratio` |
| C-PR (λ=0.75), transfer_tenure_days | 0.601 [0.589, 0.612]; ρ 0.747; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l75.transfer_tenure_days` |
| C-PR (λ=0.75), active_months | 0.670 [0.656, 0.684]; ρ 0.795; B=400 | `same-window/eval_summary.json` : `per_proxy.cpr_l75.active_months` |
| S-PR, in_degree | 0.767 [0.758, 0.776]; ρ 0.884; B=400 | `same-window/eval_summary.json` : `per_proxy.spr.in_degree` |
| S-PR, in_value | 0.797 [0.788, 0.807]; ρ 0.896; B=400 | `same-window/eval_summary.json` : `per_proxy.spr.in_value` |
| S-PR, in_approve_degree | 0.372 [0.350, 0.391]; ρ 0.422; B=400 | `same-window/eval_summary.json` : `per_proxy.spr.in_approve_degree` |
| S-PR, in_approve_value | 0.371 [0.350, 0.391]; ρ 0.423; B=400 | `same-window/eval_summary.json` : `per_proxy.spr.in_approve_value` |
| S-PR, inbound_counterparty_ratio | 0.472 [0.457, 0.490]; ρ 0.671; B=400 | `same-window/eval_summary.json` : `per_proxy.spr.inbound_counterparty_ratio` |
| S-PR, transfer_tenure_days | 0.633 [0.621, 0.645]; ρ 0.768; B=400 | `same-window/eval_summary.json` : `per_proxy.spr.transfer_tenure_days` |
| S-PR, active_months | 0.646 [0.636, 0.657]; ρ 0.770; B=400 | `same-window/eval_summary.json` : `per_proxy.spr.active_months` |

## 3. Same-window contrasts, score agreement and rule A (secondary part)

| Quantity | Value | Source |
|---|---|---|
| [hybrid] C-PR transfer minus C-PR (l=0) transfer | Δτ -0.066 [-0.074, -0.058]; τa 0.738, τb 0.804; P(Δτ>0) 0.000; B=400 | `same-window/eval_summary.json` : `contrasts[0]` |
| [hybrid] C-PR allowance minus C-PR (l=1) allowance | Δτ -0.406 [-0.418, -0.393]; τa 0.433, τb 0.838; P(Δτ>0) 0.000; B=400 | `same-window/eval_summary.json` : `contrasts[1]` |
| [hybrid] C-PR sybil minus C-PR (l=0) sybil | Δτ -0.063 [-0.071, -0.053]; τa 0.574, τb 0.637; P(Δτ>0) 0.000; B=400 | `same-window/eval_summary.json` : `contrasts[2]` |
| [hybrid] C-PR sybil minus C-PR (l=1) sybil | Δτ 0.352 [0.340, 0.365]; τa 0.574, τb 0.222; P(Δτ>0) 1.000; B=400 | `same-window/eval_summary.json` : `contrasts[3]` |
| [hybrid] S-PR transfer minus C-PR (l=0) transfer | Δτ -0.022 [-0.030, -0.013]; τa 0.782, τb 0.804; P(Δτ>0) 0.000; B=400 | `same-window/eval_summary.json` : `contrasts[4]` |
| [hybrid] S-PR allowance minus C-PR (l=1) allowance | Δτ -0.467 [-0.488, -0.446]; τa 0.371, τb 0.838; P(Δτ>0) 0.000; B=400 | `same-window/eval_summary.json` : `contrasts[5]` |
| [hybrid] S-PR sybil minus C-PR (l=0) sybil | Δτ -0.053 [-0.058, -0.048]; τa 0.584, τb 0.637; P(Δτ>0) 0.000; B=400 | `same-window/eval_summary.json` : `contrasts[6]` |
| [hybrid] S-PR sybil minus C-PR (l=1) sybil | Δτ 0.362 [0.346, 0.379]; τa 0.584, τb 0.222; P(Δτ>0) 1.000; B=400 | `same-window/eval_summary.json` : `contrasts[7]` |
| [hybrid_single] C-PR transfer minus AWP transfer | Δτ -0.017 [-0.028, -0.006]; τa 0.738, τb 0.755; P(Δτ>0) 0.000; B=400 | `same-window/eval_summary.json` : `contrasts[8]` |
| [hybrid_single] C-PR allowance minus EndorseRank allowance | Δτ -0.406 [-0.419, -0.393]; τa 0.433, τb 0.839; P(Δτ>0) 0.000; B=400 | `same-window/eval_summary.json` : `contrasts[9]` |
| [hybrid_single] C-PR sybil minus AWP sybil | Δτ -0.069 [-0.077, -0.059]; τa 0.574, τb 0.643; P(Δτ>0) 0.000; B=400 | `same-window/eval_summary.json` : `contrasts[10]` |
| [hybrid_single] C-PR sybil minus EndorseRank sybil | Δτ 0.353 [0.341, 0.367]; τa 0.574, τb 0.220; P(Δτ>0) 1.000; B=400 | `same-window/eval_summary.json` : `contrasts[11]` |
| [er_awp] EndorseRank allowance minus EndorseRank transfer | Δτ 0.542 [0.520, 0.563]; τa 0.839, τb 0.297; P(Δτ>0) 1.000; B=400 | `same-window/eval_summary.json` : `contrasts[12]` |
| [er_awp] AWP transfer minus EndorseRank transfer | Δτ 0.458 [0.438, 0.476]; τa 0.755, τb 0.297; P(Δτ>0) 1.000; B=400 | `same-window/eval_summary.json` : `contrasts[13]` |
| [er_awp] EndorseRank allowance minus AWP allowance | Δτ 0.613 [0.591, 0.632]; τa 0.839, τb 0.227; P(Δτ>0) 1.000; B=400 | `same-window/eval_summary.json` : `contrasts[14]` |
| [er_awp] AWP sybil minus EndorseRank sybil | Δτ 0.422 [0.404, 0.438]; τa 0.643, τb 0.220; P(Δτ>0) 1.000; B=400 | `same-window/eval_summary.json` : `contrasts[15]` |
| [er_awp] EndorseRank in-approve degree minus EndorseRank in-degree | Δτ 0.542 [0.521, 0.564]; τa 0.847, τb 0.305; P(Δτ>0) 1.000; B=400 | `same-window/eval_summary.json` : `contrasts[16]` |
| EndorseRank vs AWP, τ_b | 0.275 [0.258, 0.294]; B=400 | `same-window/eval_summary.json` : `inter_method.endorserank_vs_awp` |
| EndorseRank vs AWP, isolated-node rule | 0.227 [0.207, 0.245]; B=400 | `same-window/eval_summary.json` : `inter_method.isolated` |
| Concordance: pairs | 20,752,903 | `same-window/eval_summary.json` : `inter_method.concordance.pairs` |
| Concordance: ordered by both | 6,704,900 | `same-window/eval_summary.json` : `inter_method.concordance.ordered_by_both` |
| Concordance: share ordered by both | 0.323 | `same-window/eval_summary.json` : `inter_method.concordance.share_ordered_by_both` |
| Concordance: discordant share of ordered | 0.267 | `same-window/eval_summary.json` : `inter_method.concordance.discordant_share_of_ordered` |
| Concordance: tau b | 0.275 | `same-window/eval_summary.json` : `inter_method.concordance.tau_b` |
| Rule A secondary, transfer: better layer C-PR (λ=0) | C-PR 0.738 vs interval [0.799, 0.809]; pass: no | `same-window/eval_summary.json` : `rule_a_secondary.transfer` |
| Rule A secondary, allowance: better layer C-PR (λ=1) | C-PR 0.433 vs interval [0.827, 0.850]; pass: no | `same-window/eval_summary.json` : `rule_a_secondary.allowance` |
| Rule A secondary, Sybil stability: C-PR above both layers | C-PR 0.574, λ=1 0.222, λ=0 0.637; pass: no | `same-window/eval_summary.json` : `rule_a_secondary.sybil_stability` |
| Rule A secondary part met | no | `same-window/eval_summary.json` : `rule_a_secondary.pass` |

### Same window: where the members of cohort_tobs lie in the contract graph

| Quantity | Value | Source |
|---|---|---|
| cohort_tobs: members | 6,443 | `same-window/eval_summary.json` : `cohort_coverage.cohort_tobs.n` |
| cohort_tobs: allowance layer | 1,250 (0.194) | `same-window/eval_summary.json` : `cohort_coverage.cohort_tobs.allowance_layer` |
| cohort_tobs: transfer layer | 4,059 (0.630) | `same-window/eval_summary.json` : `cohort_coverage.cohort_tobs.transfer_layer` |
| cohort_tobs: both layers | 1,039 (0.161) | `same-window/eval_summary.json` : `cohort_coverage.cohort_tobs.both_layers` |
| cohort_tobs: union graph | 4,270 (0.663) | `same-window/eval_summary.json` : `cohort_coverage.cohort_tobs.union_graph` |
| cohort_tobs: self pairs only | 0 (0.000) | `same-window/eval_summary.json` : `cohort_coverage.cohort_tobs.self_pairs_only` |
| cohort_tobs: outside contract graph | 2,173 (0.337) | `same-window/eval_summary.json` : `cohort_coverage.cohort_tobs.outside_contract_graph` |

### Same window: comparisons on the members inside the union graph only (decides no rule)

| Quantity | Value | Source |
|---|---|---|
| Same window members inside the union graph | 4,270 (0.663) | `same-window/eval_summary.json` : `in_union_graph.n` |
| Inside the union graph: EndorseRank, in_degree | 0.174 [0.146, 0.200]; ρ 0.206; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.endorserank.in_degree` |
| Inside the union graph: EndorseRank, in_value | 0.153 [0.127, 0.177]; ρ 0.191; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.endorserank.in_value` |
| Inside the union graph: EndorseRank, in_approve_degree | 0.838 [0.828, 0.847]; ρ 0.892; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.endorserank.in_approve_degree` |
| Inside the union graph: EndorseRank, in_approve_value | 0.813 [0.803, 0.822]; ρ 0.889; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.endorserank.in_approve_value` |
| Inside the union graph: EndorseRank, inbound_counterparty_ratio | -0.091 [-0.112, -0.068]; ρ -0.112; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.endorserank.inbound_counterparty_ratio` |
| Inside the union graph: EndorseRank, transfer_tenure_days | 0.108 [0.082, 0.132]; ρ 0.135; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.endorserank.transfer_tenure_days` |
| Inside the union graph: EndorseRank, active_months | 0.067 [0.038, 0.096]; ρ 0.077; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.endorserank.active_months` |
| Inside the union graph: EndorseRank (activity restarts), in_degree | 0.178 [0.151, 0.204]; ρ 0.212; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.endorserank_activity.in_degree` |
| Inside the union graph: EndorseRank (activity restarts), in_value | 0.156 [0.131, 0.180]; ρ 0.199; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.endorserank_activity.in_value` |
| Inside the union graph: EndorseRank (activity restarts), in_approve_degree | 0.786 [0.769, 0.801]; ρ 0.827; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.endorserank_activity.in_approve_degree` |
| Inside the union graph: EndorseRank (activity restarts), in_approve_value | 0.737 [0.721, 0.753]; ρ 0.816; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.endorserank_activity.in_approve_value` |
| Inside the union graph: EndorseRank (activity restarts), inbound_counterparty_ratio | -0.087 [-0.108, -0.064]; ρ -0.110; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.endorserank_activity.inbound_counterparty_ratio` |
| Inside the union graph: EndorseRank (activity restarts), transfer_tenure_days | 0.120 [0.094, 0.142]; ρ 0.150; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.endorserank_activity.transfer_tenure_days` |
| Inside the union graph: EndorseRank (activity restarts), active_months | 0.081 [0.052, 0.107]; ρ 0.096; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.endorserank_activity.active_months` |
| Inside the union graph: AWP, in_degree | 0.650 [0.636, 0.662]; ρ 0.804; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.awp.in_degree` |
| Inside the union graph: AWP, in_value | 0.623 [0.611, 0.634]; ρ 0.802; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.awp.in_value` |
| Inside the union graph: AWP, in_approve_degree | 0.122 [0.091, 0.151]; ρ 0.152; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.awp.in_approve_degree` |
| Inside the union graph: AWP, in_approve_value | 0.116 [0.087, 0.145]; ρ 0.147; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.awp.in_approve_value` |
| Inside the union graph: AWP, inbound_counterparty_ratio | 0.018 [-0.007, 0.042]; ρ 0.096; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.awp.inbound_counterparty_ratio` |
| Inside the union graph: AWP, transfer_tenure_days | 0.555 [0.540, 0.568]; ρ 0.739; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.awp.transfer_tenure_days` |
| Inside the union graph: AWP, active_months | 0.566 [0.548, 0.581]; ρ 0.724; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.awp.active_months` |
| Inside the union graph: C-PR (λ=1), in_degree | 0.175 [0.145, 0.201]; ρ 0.206; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.cpr_l100.in_degree` |
| Inside the union graph: C-PR (λ=1), in_value | 0.155 [0.128, 0.178]; ρ 0.194; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.cpr_l100.in_value` |
| Inside the union graph: C-PR (λ=1), in_approve_degree | 0.838 [0.827, 0.847]; ρ 0.891; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.cpr_l100.in_approve_degree` |
| Inside the union graph: C-PR (λ=1), in_approve_value | 0.813 [0.803, 0.822]; ρ 0.888; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.cpr_l100.in_approve_value` |
| Inside the union graph: C-PR (λ=1), inbound_counterparty_ratio | -0.092 [-0.113, -0.070]; ρ -0.114; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.cpr_l100.inbound_counterparty_ratio` |
| Inside the union graph: C-PR (λ=1), transfer_tenure_days | 0.109 [0.084, 0.133]; ρ 0.136; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.cpr_l100.transfer_tenure_days` |
| Inside the union graph: C-PR (λ=1), active_months | 0.069 [0.039, 0.098]; ρ 0.080; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.cpr_l100.active_months` |
| Inside the union graph: C-PR (λ=0), in_degree | 0.702 [0.690, 0.715]; ρ 0.852; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.cpr_l0.in_degree` |
| Inside the union graph: C-PR (λ=0), in_value | 0.754 [0.744, 0.765]; ρ 0.898; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.cpr_l0.in_value` |
| Inside the union graph: C-PR (λ=0), in_approve_degree | 0.137 [0.105, 0.166]; ρ 0.168; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.cpr_l0.in_approve_degree` |
| Inside the union graph: C-PR (λ=0), in_approve_value | 0.138 [0.107, 0.166]; ρ 0.171; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.cpr_l0.in_approve_value` |
| Inside the union graph: C-PR (λ=0), inbound_counterparty_ratio | 0.149 [0.122, 0.174]; ρ 0.322; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.cpr_l0.inbound_counterparty_ratio` |
| Inside the union graph: C-PR (λ=0), transfer_tenure_days | 0.455 [0.439, 0.472]; ρ 0.619; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.cpr_l0.transfer_tenure_days` |
| Inside the union graph: C-PR (λ=0), active_months | 0.477 [0.458, 0.495]; ρ 0.616; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.cpr_l0.active_months` |
| Inside the union graph: C-PR (λ=0.25), in_degree | 0.612 [0.594, 0.628]; ρ 0.744; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.cpr_l25.in_degree` |
| Inside the union graph: C-PR (λ=0.25), in_value | 0.645 [0.627, 0.660]; ρ 0.778; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.cpr_l25.in_value` |
| Inside the union graph: C-PR (λ=0.25), in_approve_degree | 0.409 [0.393, 0.427]; ρ 0.498; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.cpr_l25.in_approve_degree` |
| Inside the union graph: C-PR (λ=0.25), in_approve_value | 0.392 [0.376, 0.408]; ρ 0.488; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.cpr_l25.in_approve_value` |
| Inside the union graph: C-PR (λ=0.25), inbound_counterparty_ratio | 0.058 [0.030, 0.082]; ρ 0.171; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.cpr_l25.inbound_counterparty_ratio` |
| Inside the union graph: C-PR (λ=0.25), transfer_tenure_days | 0.370 [0.353, 0.387]; ρ 0.509; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.cpr_l25.transfer_tenure_days` |
| Inside the union graph: C-PR (λ=0.25), active_months | 0.345 [0.324, 0.364]; ρ 0.460; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.cpr_l25.active_months` |
| Inside the union graph: C-PR (λ=0.5), in_degree | 0.606 [0.587, 0.622]; ρ 0.735; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.cpr_l50.in_degree` |
| Inside the union graph: C-PR (λ=0.5), in_value | 0.633 [0.616, 0.649]; ρ 0.764; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.cpr_l50.in_value` |
| Inside the union graph: C-PR (λ=0.5), in_approve_degree | 0.426 [0.409, 0.442]; ρ 0.517; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.cpr_l50.in_approve_degree` |
| Inside the union graph: C-PR (λ=0.5), in_approve_value | 0.406 [0.390, 0.422]; ρ 0.507; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.cpr_l50.in_approve_value` |
| Inside the union graph: C-PR (λ=0.5), inbound_counterparty_ratio | 0.055 [0.026, 0.079]; ρ 0.166; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.cpr_l50.inbound_counterparty_ratio` |
| Inside the union graph: C-PR (λ=0.5), transfer_tenure_days | 0.363 [0.345, 0.380]; ρ 0.498; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.cpr_l50.transfer_tenure_days` |
| Inside the union graph: C-PR (λ=0.5), active_months | 0.337 [0.315, 0.356]; ρ 0.447; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.cpr_l50.active_months` |
| Inside the union graph: C-PR (λ=0.75), in_degree | 0.601 [0.583, 0.618]; ρ 0.729; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.cpr_l75.in_degree` |
| Inside the union graph: C-PR (λ=0.75), in_value | 0.624 [0.606, 0.640]; ρ 0.755; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.cpr_l75.in_value` |
| Inside the union graph: C-PR (λ=0.75), in_approve_degree | 0.435 [0.419, 0.451]; ρ 0.528; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.cpr_l75.in_approve_degree` |
| Inside the union graph: C-PR (λ=0.75), in_approve_value | 0.415 [0.399, 0.431]; ρ 0.517; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.cpr_l75.in_approve_value` |
| Inside the union graph: C-PR (λ=0.75), inbound_counterparty_ratio | 0.054 [0.026, 0.078]; ρ 0.163; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.cpr_l75.inbound_counterparty_ratio` |
| Inside the union graph: C-PR (λ=0.75), transfer_tenure_days | 0.357 [0.339, 0.374]; ρ 0.491; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.cpr_l75.transfer_tenure_days` |
| Inside the union graph: C-PR (λ=0.75), active_months | 0.331 [0.309, 0.351]; ρ 0.438; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.cpr_l75.active_months` |
| Inside the union graph: S-PR, in_degree | 0.622 [0.606, 0.634]; ρ 0.770; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.spr.in_degree` |
| Inside the union graph: S-PR, in_value | 0.682 [0.667, 0.696]; ρ 0.811; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.spr.in_value` |
| Inside the union graph: S-PR, in_approve_degree | 0.329 [0.299, 0.357]; ρ 0.394; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.spr.in_approve_degree` |
| Inside the union graph: S-PR, in_approve_value | 0.328 [0.299, 0.353]; ρ 0.395; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.spr.in_approve_value` |
| Inside the union graph: S-PR, inbound_counterparty_ratio | 0.095 [0.066, 0.122]; ρ 0.217; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.spr.inbound_counterparty_ratio` |
| Inside the union graph: S-PR, transfer_tenure_days | 0.452 [0.435, 0.470]; ρ 0.608; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.spr.transfer_tenure_days` |
| Inside the union graph: S-PR, active_months | 0.455 [0.438, 0.473]; ρ 0.591; B=400 | `same-window/eval_summary.json` : `in_union_graph.per_proxy.spr.active_months` |
| Inside the union graph: EndorseRank, transfer family | 0.163 [0.138, 0.187]; B=400 | `same-window/eval_summary.json` : `in_union_graph.families.endorserank.transfer` |
| Inside the union graph: EndorseRank, allowance family | 0.825 [0.815, 0.833]; B=400 | `same-window/eval_summary.json` : `in_union_graph.families.endorserank.allowance` |
| Inside the union graph: EndorseRank, Sybil stability family | 0.028 [0.009, 0.046]; B=400 | `same-window/eval_summary.json` : `in_union_graph.families.endorserank.sybil_stability` |
| Inside the union graph: EndorseRank (activity restarts), transfer family | 0.167 [0.142, 0.192]; B=400 | `same-window/eval_summary.json` : `in_union_graph.families.endorserank_activity.transfer` |
| Inside the union graph: EndorseRank (activity restarts), allowance family | 0.761 [0.745, 0.777]; B=400 | `same-window/eval_summary.json` : `in_union_graph.families.endorserank_activity.allowance` |
| Inside the union graph: EndorseRank (activity restarts), Sybil stability family | 0.038 [0.018, 0.056]; B=400 | `same-window/eval_summary.json` : `in_union_graph.families.endorserank_activity.sybil_stability` |
| Inside the union graph: AWP, transfer family | 0.636 [0.626, 0.647]; B=400 | `same-window/eval_summary.json` : `in_union_graph.families.awp.transfer` |
| Inside the union graph: AWP, allowance family | 0.119 [0.089, 0.147]; B=400 | `same-window/eval_summary.json` : `in_union_graph.families.awp.allowance` |
| Inside the union graph: AWP, Sybil stability family | 0.380 [0.367, 0.393]; B=400 | `same-window/eval_summary.json` : `in_union_graph.families.awp.sybil_stability` |
| Inside the union graph: C-PR (λ=1), transfer family | 0.165 [0.139, 0.188]; B=400 | `same-window/eval_summary.json` : `in_union_graph.families.cpr_l100.transfer` |
| Inside the union graph: C-PR (λ=1), allowance family | 0.825 [0.815, 0.834]; B=400 | `same-window/eval_summary.json` : `in_union_graph.families.cpr_l100.allowance` |
| Inside the union graph: C-PR (λ=1), Sybil stability family | 0.029 [0.009, 0.047]; B=400 | `same-window/eval_summary.json` : `in_union_graph.families.cpr_l100.sybil_stability` |
| Inside the union graph: C-PR (λ=0), transfer family | 0.728 [0.718, 0.738]; B=400 | `same-window/eval_summary.json` : `in_union_graph.families.cpr_l0.transfer` |
| Inside the union graph: C-PR (λ=0), allowance family | 0.138 [0.106, 0.166]; B=400 | `same-window/eval_summary.json` : `in_union_graph.families.cpr_l0.allowance` |
| Inside the union graph: C-PR (λ=0), Sybil stability family | 0.361 [0.347, 0.376]; B=400 | `same-window/eval_summary.json` : `in_union_graph.families.cpr_l0.sybil_stability` |
| Inside the union graph: C-PR (λ=0.25), transfer family | 0.629 [0.613, 0.643]; B=400 | `same-window/eval_summary.json` : `in_union_graph.families.cpr_l25.transfer` |
| Inside the union graph: C-PR (λ=0.25), allowance family | 0.400 [0.385, 0.417]; B=400 | `same-window/eval_summary.json` : `in_union_graph.families.cpr_l25.allowance` |
| Inside the union graph: C-PR (λ=0.25), Sybil stability family | 0.258 [0.243, 0.272]; B=400 | `same-window/eval_summary.json` : `in_union_graph.families.cpr_l25.sybil_stability` |
| Inside the union graph: C-PR (λ=0.5), transfer family | 0.619 [0.603, 0.634]; B=400 | `same-window/eval_summary.json` : `in_union_graph.families.cpr_l50.transfer` |
| Inside the union graph: C-PR (λ=0.5), allowance family | 0.416 [0.400, 0.432]; B=400 | `same-window/eval_summary.json` : `in_union_graph.families.cpr_l50.allowance` |
| Inside the union graph: C-PR (λ=0.5), Sybil stability family | 0.251 [0.236, 0.265]; B=400 | `same-window/eval_summary.json` : `in_union_graph.families.cpr_l50.sybil_stability` |
| Inside the union graph: C-PR (λ=0.75), transfer family | 0.612 [0.596, 0.628]; B=400 | `same-window/eval_summary.json` : `in_union_graph.families.cpr_l75.transfer` |
| Inside the union graph: C-PR (λ=0.75), allowance family | 0.425 [0.409, 0.441]; B=400 | `same-window/eval_summary.json` : `in_union_graph.families.cpr_l75.allowance` |
| Inside the union graph: C-PR (λ=0.75), Sybil stability family | 0.247 [0.232, 0.261]; B=400 | `same-window/eval_summary.json` : `in_union_graph.families.cpr_l75.sybil_stability` |
| Inside the union graph: S-PR, transfer family | 0.652 [0.638, 0.665]; B=400 | `same-window/eval_summary.json` : `in_union_graph.families.spr.transfer` |
| Inside the union graph: S-PR, allowance family | 0.328 [0.299, 0.355]; B=400 | `same-window/eval_summary.json` : `in_union_graph.families.spr.allowance` |
| Inside the union graph: S-PR, Sybil stability family | 0.334 [0.321, 0.348]; B=400 | `same-window/eval_summary.json` : `in_union_graph.families.spr.sybil_stability` |
| Inside the union graph: [hybrid] C-PR transfer minus C-PR (l=0) transfer | Δτ -0.109 [-0.124, -0.096]; τa 0.619, τb 0.728; P(Δτ>0) 0.000; B=400 | `same-window/eval_summary.json` : `in_union_graph.contrasts[0]` |
| Inside the union graph: [hybrid] C-PR allowance minus C-PR (l=1) allowance | Δτ -0.409 [-0.424, -0.391]; τa 0.416, τb 0.825; P(Δτ>0) 0.000; B=400 | `same-window/eval_summary.json` : `in_union_graph.contrasts[1]` |
| Inside the union graph: [hybrid] C-PR sybil minus C-PR (l=0) sybil | Δτ -0.109 [-0.126, -0.094]; τa 0.251, τb 0.361; P(Δτ>0) 0.000; B=400 | `same-window/eval_summary.json` : `in_union_graph.contrasts[2]` |
| Inside the union graph: [hybrid] C-PR sybil minus C-PR (l=1) sybil | Δτ 0.223 [0.206, 0.239]; τa 0.251, τb 0.029; P(Δτ>0) 1.000; B=400 | `same-window/eval_summary.json` : `in_union_graph.contrasts[3]` |
| Inside the union graph: [hybrid] S-PR transfer minus C-PR (l=0) transfer | Δτ -0.076 [-0.088, -0.064]; τa 0.652, τb 0.728; P(Δτ>0) 0.000; B=400 | `same-window/eval_summary.json` : `in_union_graph.contrasts[4]` |
| Inside the union graph: [hybrid] S-PR allowance minus C-PR (l=1) allowance | Δτ -0.497 [-0.526, -0.469]; τa 0.328, τb 0.825; P(Δτ>0) 0.000; B=400 | `same-window/eval_summary.json` : `in_union_graph.contrasts[5]` |
| Inside the union graph: [hybrid] S-PR sybil minus C-PR (l=0) sybil | Δτ -0.027 [-0.035, -0.019]; τa 0.334, τb 0.361; P(Δτ>0) 0.000; B=400 | `same-window/eval_summary.json` : `in_union_graph.contrasts[6]` |
| Inside the union graph: [hybrid] S-PR sybil minus C-PR (l=1) sybil | Δτ 0.305 [0.281, 0.333]; τa 0.334, τb 0.029; P(Δτ>0) 1.000; B=400 | `same-window/eval_summary.json` : `in_union_graph.contrasts[7]` |
| Inside the union graph: [hybrid_single] C-PR transfer minus AWP transfer | Δτ -0.017 [-0.038, 0.003]; τa 0.619, τb 0.636; P(Δτ>0) 0.043; B=400 | `same-window/eval_summary.json` : `in_union_graph.contrasts[8]` |
| Inside the union graph: [hybrid_single] C-PR allowance minus EndorseRank allowance | Δτ -0.409 [-0.425, -0.391]; τa 0.416, τb 0.825; P(Δτ>0) 0.000; B=400 | `same-window/eval_summary.json` : `in_union_graph.contrasts[9]` |
| Inside the union graph: [hybrid_single] C-PR sybil minus AWP sybil | Δτ -0.128 [-0.147, -0.113]; τa 0.251, τb 0.380; P(Δτ>0) 0.000; B=400 | `same-window/eval_summary.json` : `in_union_graph.contrasts[10]` |
| Inside the union graph: [hybrid_single] C-PR sybil minus EndorseRank sybil | Δτ 0.223 [0.207, 0.239]; τa 0.251, τb 0.028; P(Δτ>0) 1.000; B=400 | `same-window/eval_summary.json` : `in_union_graph.contrasts[11]` |
| Inside the union graph: [er_awp] EndorseRank allowance minus EndorseRank transfer | Δτ 0.662 [0.635, 0.687]; τa 0.825, τb 0.163; P(Δτ>0) 1.000; B=400 | `same-window/eval_summary.json` : `in_union_graph.contrasts[12]` |
| Inside the union graph: [er_awp] AWP transfer minus EndorseRank transfer | Δτ 0.473 [0.446, 0.500]; τa 0.636, τb 0.163; P(Δτ>0) 1.000; B=400 | `same-window/eval_summary.json` : `in_union_graph.contrasts[13]` |
| Inside the union graph: [er_awp] EndorseRank allowance minus AWP allowance | Δτ 0.706 [0.673, 0.734]; τa 0.825, τb 0.119; P(Δτ>0) 1.000; B=400 | `same-window/eval_summary.json` : `in_union_graph.contrasts[14]` |
| Inside the union graph: [er_awp] AWP sybil minus EndorseRank sybil | Δτ 0.352 [0.326, 0.380]; τa 0.380, τb 0.028; P(Δτ>0) 1.000; B=400 | `same-window/eval_summary.json` : `in_union_graph.contrasts[15]` |
| Inside the union graph: [er_awp] EndorseRank in-approve degree minus EndorseRank in-degree | Δτ 0.663 [0.635, 0.691]; τa 0.838, τb 0.174; P(Δτ>0) 1.000; B=400 | `same-window/eval_summary.json` : `in_union_graph.contrasts[16]` |

## 4. Ties and the isolated-node rule

| Quantity | Value | Source |
|---|---|---|
| EndorseRank ties (same window) | distinct 801 of 6,443; zeros 5,200; largest block 5,200 at 0.000; share of pairs tied 0.6539 | `same-window/eval_summary.json` : `ties.endorserank` |
| EndorseRank (activity restarts) ties (same window) | distinct 1,226 of 6,443; zeros 5,200; largest block 5,200 at 0.000; share of pairs tied 0.6514 | `same-window/eval_summary.json` : `ties.endorserank_activity` |
| AWP ties (same window) | distinct 3,982 of 6,443; zeros 2,384; largest block 2,384 at 0.000; share of pairs tied 0.1369 | `same-window/eval_summary.json` : `ties.awp` |
| C-PR (λ=1) ties (same window) | distinct 631 of 6,443; zeros 5,193; largest block 5,193 at 0.000; share of pairs tied 0.6523 | `same-window/eval_summary.json` : `ties.cpr_l100` |
| C-PR (λ=0) ties (same window) | distinct 3,035 of 6,443; zeros 2,384; largest block 2,384 at 0.000; share of pairs tied 0.1552 | `same-window/eval_summary.json` : `ties.cpr_l0` |
| C-PR (λ=0.25) ties (same window) | distinct 3,233 of 6,443; zeros 2,173; largest block 2,173 at 0.000; share of pairs tied 0.1317 | `same-window/eval_summary.json` : `ties.cpr_l25` |
| C-PR (λ=0.5) ties (same window) | distinct 3,233 of 6,443; zeros 2,173; largest block 2,173 at 0.000; share of pairs tied 0.1316 | `same-window/eval_summary.json` : `ties.cpr_l50` |
| C-PR (λ=0.75) ties (same window) | distinct 3,238 of 6,443; zeros 2,173; largest block 2,173 at 0.000; share of pairs tied 0.1316 | `same-window/eval_summary.json` : `ties.cpr_l75` |
| S-PR ties (same window) | distinct 2,883 of 6,443; zeros 3,486; largest block 3,486 at 0.000; share of pairs tied 0.2928 | `same-window/eval_summary.json` : `ties.spr` |
| endorserank_iso (missing contracts as isolated nodes), transfer | 0.259 [0.239, 0.278]; B=400 | `same-window/eval_summary.json` : `isolated_rule.endorserank_iso.transfer` |
| endorserank_iso (missing contracts as isolated nodes), allowance | 0.956 [0.952, 0.960]; B=400 | `same-window/eval_summary.json` : `isolated_rule.endorserank_iso.allowance` |
| endorserank_iso (missing contracts as isolated nodes), Sybil stability | 0.171 [0.155, 0.187]; B=400 | `same-window/eval_summary.json` : `isolated_rule.endorserank_iso.sybil_stability` |
| awp_iso (missing contracts as isolated nodes), transfer | 0.755 [0.748, 0.762]; B=400 | `same-window/eval_summary.json` : `isolated_rule.awp_iso.transfer` |
| awp_iso (missing contracts as isolated nodes), allowance | 0.227 [0.206, 0.245]; B=400 | `same-window/eval_summary.json` : `isolated_rule.awp_iso.allowance` |
| awp_iso (missing contracts as isolated nodes), Sybil stability | 0.643 [0.635, 0.651]; B=400 | `same-window/eval_summary.json` : `isolated_rule.awp_iso.sybil_stability` |
| EndorseRank ties (W0 spenders) | distinct 1,190 of 7,864; zeros 5,966; largest block 5,966 at 0.000; share of pairs tied 0.5803 | `holdout-w0/eval_summary.json` : `ties.endorserank` |
| AWP ties (W0 spenders) | distinct 5,366 of 7,864; zeros 2,421; largest block 2,421 at 0.000; share of pairs tied 0.0948 | `holdout-w0/eval_summary.json` : `ties.awp` |
| C-PR (λ=1) ties (W0 spenders) | distinct 684 of 7,864; zeros 5,963; largest block 5,963 at 0.000; share of pairs tied 0.5805 | `holdout-w0/eval_summary.json` : `ties.cpr_l100` |

## 5. Closed-form check of EndorseRank, s(v) = c (1 + d δ(v))

| Quantity | Value | Source |
|---|---|---|
| Same window: common value c | 8.451e-06 | `same-window/eval_summary.json` : `closed_form.common_value_c` |
| Same window: spread of c | 1.0000 | `same-window/eval_summary.json` : `closed_form.spread_of_c` |
| Same window: spenders | 926 | `same-window/eval_summary.json` : `closed_form.spenders` |
| Same window: depth one spenders | 651 | `same-window/eval_summary.json` : `closed_form.depth_one_spenders` |
| Same window: within 1pct all | 0.8035 | `same-window/eval_summary.json` : `closed_form.within_1pct_all` |
| Same window: within 1pct depth one | 1.0000 | `same-window/eval_summary.json` : `closed_form.within_1pct_depth_one` |
| Same window: within 1pct deeper | 0.3382 | `same-window/eval_summary.json` : `closed_form.within_1pct_deeper` |
| Same window: tau score vs delta | 0.9227 | `same-window/eval_summary.json` : `closed_form.tau_score_vs_delta` |
| W0: common value c | 4.589e-05 | `holdout-w0/eval_summary.json` : `closed_form.common_value_c` |
| W0: spread of c | 1.0000 | `holdout-w0/eval_summary.json` : `closed_form.spread_of_c` |
| W0: spenders | 1,362 | `holdout-w0/eval_summary.json` : `closed_form.spenders` |
| W0: depth one spenders | 810 | `holdout-w0/eval_summary.json` : `closed_form.depth_one_spenders` |
| W0: within 1pct all | 0.6843 | `holdout-w0/eval_summary.json` : `closed_form.within_1pct_all` |
| W0: within 1pct depth one | 1.0000 | `holdout-w0/eval_summary.json` : `closed_form.within_1pct_depth_one` |
| W0: within 1pct deeper | 0.2210 | `holdout-w0/eval_summary.json` : `closed_form.within_1pct_deeper` |
| W0: tau score vs delta | 0.8611 | `holdout-w0/eval_summary.json` : `closed_form.tau_score_vs_delta` |

## 6. Holdout W0 (scores at t1 on the contract graph, labels April to June 2026)

| Quantity | Value | Source |
|---|---|---|
| Freeze t1 | 2026-03-31 23:59:59 UTC | `holdout-w0/eval_summary.json` : `freeze` |
| Label window | 2026-04-01 00:00:00 UTC to 2026-06-30 23:59:59 UTC | `holdout-w0/eval_summary.json` : `labels` |
| Listed spenders of the twelve-month labels, class contract | 7,864 | `holdout-w0/eval_summary.json` : `spender_account_types.contract` |
| Listed spenders of the twelve-month labels, class user_account | 97 | `holdout-w0/eval_summary.json` : `spender_account_types.user_account` |
| Listed spenders of the twelve-month labels, class system | 1 | `holdout-w0/eval_summary.json` : `spender_account_types.system` |
| Listed spenders of the twelve-month labels, class untyped | 0 | `holdout-w0/eval_summary.json` : `spender_account_types.untyped` |
| Spender cohort (contracts) | 7,864 | `holdout-w0/eval_summary.json` : `spenders` |
| Gained a new approval pair | 1,725 | `holdout-w0/eval_summary.json` : `gained_new_approvals` |
| Gained a new transfer sender | 1,416 | `holdout-w0/eval_summary.json` : `gained_new_senders` |

### W0 spenders: τ_b with every label (scores and the baselines counted on the contract graph)

| Quantity | Value | Source |
|---|---|---|
| EndorseRank, new approval pairs | 0.168 [0.145, 0.193]; B=400 | `holdout-w0/eval_summary.json` : `taus.endorserank.future_new_approvers` |
| EndorseRank, new transfer senders | 0.084 [0.062, 0.105]; B=400 | `holdout-w0/eval_summary.json` : `taus.endorserank.future_new_transfer_senders` |
| EndorseRank, revocations | 0.174 [0.147, 0.202]; B=400 | `holdout-w0/eval_summary.json` : `taus.endorserank.future_revoke_count` |
| EndorseRank, drained owners | 0.202 [0.180, 0.226]; B=400 | `holdout-w0/eval_summary.json` : `taus.endorserank.future_drain_owners` |
| EndorseRank (activity restarts), new approval pairs | 0.163 [0.142, 0.188]; B=400 | `holdout-w0/eval_summary.json` : `taus.endorserank_activity.future_new_approvers` |
| EndorseRank (activity restarts), new transfer senders | 0.089 [0.069, 0.111]; B=400 | `holdout-w0/eval_summary.json` : `taus.endorserank_activity.future_new_transfer_senders` |
| EndorseRank (activity restarts), revocations | 0.173 [0.147, 0.199]; B=400 | `holdout-w0/eval_summary.json` : `taus.endorserank_activity.future_revoke_count` |
| EndorseRank (activity restarts), drained owners | 0.209 [0.186, 0.233]; B=400 | `holdout-w0/eval_summary.json` : `taus.endorserank_activity.future_drain_owners` |
| AWP, new approval pairs | 0.098 [0.079, 0.119]; B=400 | `holdout-w0/eval_summary.json` : `taus.awp.future_new_approvers` |
| AWP, new transfer senders | 0.330 [0.313, 0.347]; B=400 | `holdout-w0/eval_summary.json` : `taus.awp.future_new_transfer_senders` |
| AWP, revocations | 0.099 [0.079, 0.121]; B=400 | `holdout-w0/eval_summary.json` : `taus.awp.future_revoke_count` |
| AWP, drained owners | 0.131 [0.112, 0.152]; B=400 | `holdout-w0/eval_summary.json` : `taus.awp.future_drain_owners` |
| C-PR (λ=1), new approval pairs | 0.167 [0.145, 0.192]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l100.future_new_approvers` |
| C-PR (λ=1), new transfer senders | 0.084 [0.062, 0.105]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l100.future_new_transfer_senders` |
| C-PR (λ=1), revocations | 0.173 [0.147, 0.201]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l100.future_revoke_count` |
| C-PR (λ=1), drained owners | 0.201 [0.179, 0.225]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l100.future_drain_owners` |
| C-PR (λ=0), new approval pairs | 0.070 [0.052, 0.091]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l0.future_new_approvers` |
| C-PR (λ=0), new transfer senders | 0.268 [0.250, 0.285]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l0.future_new_transfer_senders` |
| C-PR (λ=0), revocations | 0.071 [0.052, 0.094]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l0.future_revoke_count` |
| C-PR (λ=0), drained owners | 0.094 [0.076, 0.114]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l0.future_drain_owners` |
| C-PR (λ=0.25), new approval pairs | 0.141 [0.123, 0.161]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l25.future_new_approvers` |
| C-PR (λ=0.25), new transfer senders | 0.256 [0.238, 0.273]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l25.future_new_transfer_senders` |
| C-PR (λ=0.25), revocations | 0.130 [0.111, 0.153]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l25.future_revoke_count` |
| C-PR (λ=0.25), drained owners | 0.167 [0.150, 0.188]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l25.future_drain_owners` |
| C-PR (λ=0.5), new approval pairs | 0.142 [0.124, 0.162]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l50.future_new_approvers` |
| C-PR (λ=0.5), new transfer senders | 0.254 [0.235, 0.270]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l50.future_new_transfer_senders` |
| C-PR (λ=0.5), revocations | 0.132 [0.112, 0.155]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l50.future_revoke_count` |
| C-PR (λ=0.5), drained owners | 0.169 [0.151, 0.190]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l50.future_drain_owners` |
| C-PR (λ=0.75), new approval pairs | 0.142 [0.124, 0.162]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l75.future_new_approvers` |
| C-PR (λ=0.75), new transfer senders | 0.251 [0.232, 0.267]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l75.future_new_transfer_senders` |
| C-PR (λ=0.75), revocations | 0.132 [0.112, 0.155]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l75.future_revoke_count` |
| C-PR (λ=0.75), drained owners | 0.168 [0.151, 0.190]; B=400 | `holdout-w0/eval_summary.json` : `taus.cpr_l75.future_drain_owners` |
| S-PR, new approval pairs | 0.091 [0.074, 0.113]; B=400 | `holdout-w0/eval_summary.json` : `taus.spr.future_new_approvers` |
| S-PR, new transfer senders | 0.264 [0.246, 0.283]; B=400 | `holdout-w0/eval_summary.json` : `taus.spr.future_new_transfer_senders` |
| S-PR, revocations | 0.097 [0.077, 0.122]; B=400 | `holdout-w0/eval_summary.json` : `taus.spr.future_revoke_count` |
| S-PR, drained owners | 0.131 [0.113, 0.151]; B=400 | `holdout-w0/eval_summary.json` : `taus.spr.future_drain_owners` |
| in-approve degree at t1, new approval pairs | 0.204 [0.181, 0.228]; B=400 | `holdout-w0/eval_summary.json` : `taus.t1_in_approve_degree.future_new_approvers` |
| in-approve degree at t1, new transfer senders | 0.091 [0.066, 0.113]; B=400 | `holdout-w0/eval_summary.json` : `taus.t1_in_approve_degree.future_new_transfer_senders` |
| in-approve degree at t1, revocations | 0.190 [0.161, 0.220]; B=400 | `holdout-w0/eval_summary.json` : `taus.t1_in_approve_degree.future_revoke_count` |
| in-approve degree at t1, drained owners | 0.213 [0.188, 0.238]; B=400 | `holdout-w0/eval_summary.json` : `taus.t1_in_approve_degree.future_drain_owners` |
| transfer in-degree at t1, new approval pairs | 0.070 [0.050, 0.091]; B=400 | `holdout-w0/eval_summary.json` : `taus.t1_in_degree.future_new_approvers` |
| transfer in-degree at t1, new transfer senders | 0.318 [0.298, 0.336]; B=400 | `holdout-w0/eval_summary.json` : `taus.t1_in_degree.future_new_transfer_senders` |
| transfer in-degree at t1, revocations | 0.061 [0.040, 0.083]; B=400 | `holdout-w0/eval_summary.json` : `taus.t1_in_degree.future_revoke_count` |
| transfer in-degree at t1, drained owners | 0.092 [0.072, 0.113]; B=400 | `holdout-w0/eval_summary.json` : `taus.t1_in_degree.future_drain_owners` |
| in-approve value at t1, new approval pairs | 0.189 [0.166, 0.213]; B=400 | `holdout-w0/eval_summary.json` : `taus.t1_in_approve_value.future_new_approvers` |
| in-approve value at t1, new transfer senders | 0.081 [0.057, 0.103]; B=400 | `holdout-w0/eval_summary.json` : `taus.t1_in_approve_value.future_new_transfer_senders` |
| in-approve value at t1, revocations | 0.178 [0.150, 0.207]; B=400 | `holdout-w0/eval_summary.json` : `taus.t1_in_approve_value.future_revoke_count` |
| in-approve value at t1, drained owners | 0.198 [0.175, 0.223]; B=400 | `holdout-w0/eval_summary.json` : `taus.t1_in_approve_value.future_drain_owners` |
| union in-degree at t1, new approval pairs | 0.126 [0.108, 0.146]; B=400 | `holdout-w0/eval_summary.json` : `taus.t1_in_degree_union.future_new_approvers` |
| union in-degree at t1, new transfer senders | 0.306 [0.287, 0.324]; B=400 | `holdout-w0/eval_summary.json` : `taus.t1_in_degree_union.future_new_transfer_senders` |
| union in-degree at t1, revocations | 0.114 [0.094, 0.138]; B=400 | `holdout-w0/eval_summary.json` : `taus.t1_in_degree_union.future_revoke_count` |
| union in-degree at t1, drained owners | 0.149 [0.131, 0.171]; B=400 | `holdout-w0/eval_summary.json` : `taus.t1_in_degree_union.future_drain_owners` |

### W0 contrasts

| Quantity | Value | Source |
|---|---|---|
| [contrasts_prefixed] C-PR minus C-PR (l=1), new approval pairs | Δτ -0.025 [-0.045, -0.004]; τa 0.142, τb 0.167; P(Δτ>0) 0.015; B=400 | `holdout-w0/eval_summary.json` : `contrasts_prefixed[0]` |
| [contrasts_prefixed] C-PR minus C-PR (l=0), new transfer senders | Δτ -0.014 [-0.019, -0.008]; τa 0.254, τb 0.268; P(Δτ>0) 0.003; B=400 | `holdout-w0/eval_summary.json` : `contrasts_prefixed[1]` |
| [contrasts_after] C-PR (l=1) minus t1 in-approve degree, new approval pairs | Δτ -0.037 [-0.046, -0.028]; τa 0.167, τb 0.204; P(Δτ>0) 0.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_after[0]` |
| [contrasts_after] S-PR minus C-PR (l=1), new approval pairs | Δτ -0.077 [-0.098, -0.055]; τa 0.091, τb 0.167; P(Δτ>0) 0.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_after[1]` |
| [contrasts_after] S-PR minus C-PR (l=0), new transfer senders | Δτ -0.003 [-0.013, 0.008]; τa 0.264, τb 0.268; P(Δτ>0) 0.285; B=400 | `holdout-w0/eval_summary.json` : `contrasts_after[2]` |
| [contrasts_after] EndorseRank minus t1 in-approve degree, new approval pairs | Δτ -0.036 [-0.046, -0.027]; τa 0.168, τb 0.204; P(Δτ>0) 0.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_after[3]` |
| [contrasts_after] AWP minus t1 in-degree, new transfer senders | Δτ 0.012 [0.003, 0.023]; τa 0.330, τb 0.318; P(Δτ>0) 0.998; B=400 | `holdout-w0/eval_summary.json` : `contrasts_after[4]` |
| [contrasts_after] C-PR minus C-PR (l=0), new approval pairs | Δτ 0.071 [0.059, 0.084]; τa 0.142, τb 0.070; P(Δτ>0) 1.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_after[5]` |
| [contrasts_after] C-PR minus EndorseRank, new approval pairs | Δτ -0.026 [-0.046, -0.004]; τa 0.142, τb 0.168; P(Δτ>0) 0.013; B=400 | `holdout-w0/eval_summary.json` : `contrasts_after[6]` |
| [contrasts_after] C-PR minus AWP, new transfer senders | Δτ -0.077 [-0.087, -0.068]; τa 0.254, τb 0.330; P(Δτ>0) 0.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_after[7]` |
| [contrasts_after] C-PR minus AWP, new approval pairs | Δτ 0.044 [0.029, 0.058]; τa 0.142, τb 0.098; P(Δτ>0) 1.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_after[8]` |
| [contrasts_after] EndorseRank minus AWP, new approval pairs | Δτ 0.070 [0.042, 0.096]; τa 0.168, τb 0.098; P(Δτ>0) 1.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_after[9]` |
| [contrasts_after] EndorseRank minus AWP, new transfer senders | Δτ -0.246 [-0.271, -0.220]; τa 0.084, τb 0.330; P(Δτ>0) 0.000; B=400 | `holdout-w0/eval_summary.json` : `contrasts_after[10]` |
| [baseline_contrasts] C-PR minus t1 union in-degree, new approval pairs | Δτ 0.016 [0.007, 0.024]; τa 0.142, τb 0.126; P(Δτ>0) 1.000; B=400 | `holdout-w0/eval_summary.json` : `baseline_contrasts[0]` |
| [baseline_contrasts] C-PR minus t1 union in-degree, new transfer senders | Δτ -0.053 [-0.061, -0.043]; τa 0.254, τb 0.306; P(Δτ>0) 0.000; B=400 | `holdout-w0/eval_summary.json` : `baseline_contrasts[1]` |

### Rule A, primary part

| Quantity | Value | Source |
|---|---|---|
| Rule A primary: no worse on new approvals | no | `holdout-w0/eval_summary.json` : `rule_a_primary.no_worse_on_new_approvals` |
| Rule A primary: better on new senders | no | `holdout-w0/eval_summary.json` : `rule_a_primary.better_on_new_senders` |
| Rule A primary: pass | no | `holdout-w0/eval_summary.json` : `rule_a_primary.pass` |

### Spenders that another contract had paid before t1

| Quantity | Value | Source |
|---|---|---|
| Receiving subset (contracts) | 4,569 | `holdout-w0/eval_summary.json` : `receiving.n` |
| Receiving: EndorseRank, new approval pairs | 0.167 [0.139, 0.197]; B=400 | `holdout-w0/eval_summary.json` : `receiving.taus.endorserank.future_new_approvers` |
| Receiving: EndorseRank, new transfer senders | 0.068 [0.040, 0.094]; B=400 | `holdout-w0/eval_summary.json` : `receiving.taus.endorserank.future_new_transfer_senders` |
| Receiving: AWP, new approval pairs | 0.238 [0.219, 0.260]; B=400 | `holdout-w0/eval_summary.json` : `receiving.taus.awp.future_new_approvers` |
| Receiving: AWP, new transfer senders | 0.411 [0.389, 0.429]; B=400 | `holdout-w0/eval_summary.json` : `receiving.taus.awp.future_new_transfer_senders` |
| Receiving: in-approve degree at t1, new approval pairs | 0.212 [0.183, 0.242]; B=400 | `holdout-w0/eval_summary.json` : `receiving.taus.t1_in_approve_degree.future_new_approvers` |
| Receiving: in-approve degree at t1, new transfer senders | 0.104 [0.076, 0.133]; B=400 | `holdout-w0/eval_summary.json` : `receiving.taus.t1_in_approve_degree.future_new_transfer_senders` |
| Receiving: transfer in-degree at t1, new approval pairs | 0.220 [0.196, 0.243]; B=400 | `holdout-w0/eval_summary.json` : `receiving.taus.t1_in_degree.future_new_approvers` |
| Receiving: transfer in-degree at t1, new transfer senders | 0.446 [0.423, 0.467]; B=400 | `holdout-w0/eval_summary.json` : `receiving.taus.t1_in_degree.future_new_transfer_senders` |
| Receiving: EndorseRank minus t1 in-approve degree, new approval pairs | Δτ -0.045 [-0.058, -0.033]; τa 0.167, τb 0.212; P(Δτ>0) 0.000; B=400 | `holdout-w0/eval_summary.json` : `receiving.contrasts[0]` |
| Receiving: AWP minus t1 in-degree, new transfer senders | Δτ -0.035 [-0.049, -0.022]; τa 0.411, τb 0.446; P(Δτ>0) 0.000; B=400 | `holdout-w0/eval_summary.json` : `receiving.contrasts[1]` |

### Coverage (AWP = 0 means no transfer edge)

| Quantity | Value | Source |
|---|---|---|
| spenders without transfer edge | 2,421 | `holdout-w0/eval_summary.json` : `coverage.spenders_without_transfer_edge` |
| share gaining approvals without | 0.234 | `holdout-w0/eval_summary.json` : `coverage.share_gaining_approvals_without` |
| share gaining approvals with | 0.213 | `holdout-w0/eval_summary.json` : `coverage.share_gaining_approvals_with` |
| share gaining senders without | 0.079 | `holdout-w0/eval_summary.json` : `coverage.share_gaining_senders_without` |
| share gaining senders with | 0.225 | `holdout-w0/eval_summary.json` : `coverage.share_gaining_senders_with` |

### W0: where the members of spenders_w0 lie in the contract graph

| Quantity | Value | Source |
|---|---|---|
| spenders_w0: members | 7,864 | `holdout-w0/eval_summary.json` : `cohort_coverage.spenders_w0.n` |
| spenders_w0: allowance layer | 1,901 (0.242) | `holdout-w0/eval_summary.json` : `cohort_coverage.spenders_w0.allowance_layer` |
| spenders_w0: transfer layer | 5,443 (0.692) | `holdout-w0/eval_summary.json` : `cohort_coverage.spenders_w0.transfer_layer` |
| spenders_w0: both layers | 1,644 (0.209) | `holdout-w0/eval_summary.json` : `cohort_coverage.spenders_w0.both_layers` |
| spenders_w0: union graph | 5,700 (0.725) | `holdout-w0/eval_summary.json` : `cohort_coverage.spenders_w0.union_graph` |
| spenders_w0: self pairs only | 0 (0.000) | `holdout-w0/eval_summary.json` : `cohort_coverage.spenders_w0.self_pairs_only` |
| spenders_w0: outside contract graph | 2,164 (0.275) | `holdout-w0/eval_summary.json` : `cohort_coverage.spenders_w0.outside_contract_graph` |

### W0: where the members of cohort_t1 lie in the contract graph

| Quantity | Value | Source |
|---|---|---|
| cohort_t1: members | 6,292 | `holdout-w0/eval_summary.json` : `cohort_coverage.cohort_t1.n` |
| cohort_t1: allowance layer | 1,248 (0.198) | `holdout-w0/eval_summary.json` : `cohort_coverage.cohort_t1.allowance_layer` |
| cohort_t1: transfer layer | 3,893 (0.619) | `holdout-w0/eval_summary.json` : `cohort_coverage.cohort_t1.transfer_layer` |
| cohort_t1: both layers | 1,033 (0.164) | `holdout-w0/eval_summary.json` : `cohort_coverage.cohort_t1.both_layers` |
| cohort_t1: union graph | 4,108 (0.653) | `holdout-w0/eval_summary.json` : `cohort_coverage.cohort_t1.union_graph` |
| cohort_t1: self pairs only | 0 (0.000) | `holdout-w0/eval_summary.json` : `cohort_coverage.cohort_t1.self_pairs_only` |
| cohort_t1: outside contract graph | 2,184 (0.347) | `holdout-w0/eval_summary.json` : `cohort_coverage.cohort_t1.outside_contract_graph` |

### W0: comparisons on the members inside the union graph only (decides no rule)

| Quantity | Value | Source |
|---|---|---|
| W0 members inside the union graph | 5,700 (0.725) | `holdout-w0/eval_summary.json` : `in_union_graph.n` |
| Inside the union graph: EndorseRank, new approval pairs | 0.202 [0.177, 0.227]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.endorserank.future_new_approvers` |
| Inside the union graph: EndorseRank, new transfer senders | 0.045 [0.019, 0.071]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.endorserank.future_new_transfer_senders` |
| Inside the union graph: EndorseRank, revocations | 0.195 [0.167, 0.221]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.endorserank.future_revoke_count` |
| Inside the union graph: EndorseRank, drained owners | 0.230 [0.207, 0.255]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.endorserank.future_drain_owners` |
| Inside the union graph: EndorseRank (activity restarts), new approval pairs | 0.195 [0.170, 0.220]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.endorserank_activity.future_new_approvers` |
| Inside the union graph: EndorseRank (activity restarts), new transfer senders | 0.053 [0.027, 0.079]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.endorserank_activity.future_new_transfer_senders` |
| Inside the union graph: EndorseRank (activity restarts), revocations | 0.194 [0.167, 0.218]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.endorserank_activity.future_revoke_count` |
| Inside the union graph: EndorseRank (activity restarts), drained owners | 0.241 [0.218, 0.266]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.endorserank_activity.future_drain_owners` |
| Inside the union graph: AWP, new approval pairs | 0.159 [0.137, 0.181]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.awp.future_new_approvers` |
| Inside the union graph: AWP, new transfer senders | 0.380 [0.362, 0.396]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.awp.future_new_transfer_senders` |
| Inside the union graph: AWP, revocations | 0.131 [0.106, 0.155]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.awp.future_revoke_count` |
| Inside the union graph: AWP, drained owners | 0.190 [0.167, 0.210]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.awp.future_drain_owners` |
| Inside the union graph: C-PR (λ=1), new approval pairs | 0.201 [0.176, 0.226]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.cpr_l100.future_new_approvers` |
| Inside the union graph: C-PR (λ=1), new transfer senders | 0.045 [0.019, 0.070]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.cpr_l100.future_new_transfer_senders` |
| Inside the union graph: C-PR (λ=1), revocations | 0.194 [0.166, 0.219]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.cpr_l100.future_revoke_count` |
| Inside the union graph: C-PR (λ=1), drained owners | 0.229 [0.205, 0.253]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.cpr_l100.future_drain_owners` |
| Inside the union graph: C-PR (λ=0), new approval pairs | 0.110 [0.086, 0.133]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.cpr_l0.future_new_approvers` |
| Inside the union graph: C-PR (λ=0), new transfer senders | 0.275 [0.254, 0.295]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.cpr_l0.future_new_transfer_senders` |
| Inside the union graph: C-PR (λ=0), revocations | 0.082 [0.057, 0.110]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.cpr_l0.future_revoke_count` |
| Inside the union graph: C-PR (λ=0), drained owners | 0.125 [0.099, 0.149]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.cpr_l0.future_drain_owners` |
| Inside the union graph: C-PR (λ=0.25), new approval pairs | 0.219 [0.199, 0.240]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.cpr_l25.future_new_approvers` |
| Inside the union graph: C-PR (λ=0.25), new transfer senders | 0.264 [0.242, 0.286]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.cpr_l25.future_new_transfer_senders` |
| Inside the union graph: C-PR (λ=0.25), revocations | 0.170 [0.148, 0.194]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.cpr_l25.future_revoke_count` |
| Inside the union graph: C-PR (λ=0.25), drained owners | 0.237 [0.215, 0.258]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.cpr_l25.future_drain_owners` |
| Inside the union graph: C-PR (λ=0.5), new approval pairs | 0.221 [0.200, 0.241]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.cpr_l50.future_new_approvers` |
| Inside the union graph: C-PR (λ=0.5), new transfer senders | 0.259 [0.238, 0.281]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.cpr_l50.future_new_transfer_senders` |
| Inside the union graph: C-PR (λ=0.5), revocations | 0.173 [0.151, 0.196]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.cpr_l50.future_revoke_count` |
| Inside the union graph: C-PR (λ=0.5), drained owners | 0.239 [0.217, 0.260]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.cpr_l50.future_drain_owners` |
| Inside the union graph: C-PR (λ=0.75), new approval pairs | 0.221 [0.199, 0.241]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.cpr_l75.future_new_approvers` |
| Inside the union graph: C-PR (λ=0.75), new transfer senders | 0.255 [0.234, 0.277]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.cpr_l75.future_new_transfer_senders` |
| Inside the union graph: C-PR (λ=0.75), revocations | 0.173 [0.151, 0.196]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.cpr_l75.future_revoke_count` |
| Inside the union graph: C-PR (λ=0.75), drained owners | 0.239 [0.216, 0.260]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.cpr_l75.future_drain_owners` |
| Inside the union graph: S-PR, new approval pairs | 0.120 [0.095, 0.142]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.spr.future_new_approvers` |
| Inside the union graph: S-PR, new transfer senders | 0.249 [0.229, 0.270]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.spr.future_new_transfer_senders` |
| Inside the union graph: S-PR, revocations | 0.108 [0.086, 0.133]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.spr.future_revoke_count` |
| Inside the union graph: S-PR, drained owners | 0.155 [0.132, 0.178]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.spr.future_drain_owners` |
| Inside the union graph: in-approve degree at t1, new approval pairs | 0.244 [0.214, 0.271]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.t1_in_approve_degree.future_new_approvers` |
| Inside the union graph: in-approve degree at t1, new transfer senders | 0.062 [0.033, 0.087]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.t1_in_approve_degree.future_new_transfer_senders` |
| Inside the union graph: in-approve degree at t1, revocations | 0.214 [0.185, 0.244]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.t1_in_approve_degree.future_revoke_count` |
| Inside the union graph: in-approve degree at t1, drained owners | 0.245 [0.219, 0.272]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.t1_in_approve_degree.future_drain_owners` |
| Inside the union graph: transfer in-degree at t1, new approval pairs | 0.106 [0.079, 0.131]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.t1_in_degree.future_new_approvers` |
| Inside the union graph: transfer in-degree at t1, new transfer senders | 0.358 [0.336, 0.383]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.t1_in_degree.future_new_transfer_senders` |
| Inside the union graph: transfer in-degree at t1, revocations | 0.069 [0.044, 0.096]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.t1_in_degree.future_revoke_count` |
| Inside the union graph: transfer in-degree at t1, drained owners | 0.114 [0.085, 0.138]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.t1_in_degree.future_drain_owners` |
| Inside the union graph: in-approve value at t1, new approval pairs | 0.219 [0.193, 0.244]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.t1_in_approve_value.future_new_approvers` |
| Inside the union graph: in-approve value at t1, new transfer senders | 0.048 [0.021, 0.073]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.t1_in_approve_value.future_new_transfer_senders` |
| Inside the union graph: in-approve value at t1, revocations | 0.195 [0.167, 0.224]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.t1_in_approve_value.future_revoke_count` |
| Inside the union graph: in-approve value at t1, drained owners | 0.221 [0.196, 0.248]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.t1_in_approve_value.future_drain_owners` |
| Inside the union graph: union in-degree at t1, new approval pairs | 0.186 [0.164, 0.209]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.t1_in_degree_union.future_new_approvers` |
| Inside the union graph: union in-degree at t1, new transfer senders | 0.349 [0.325, 0.374]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.t1_in_degree_union.future_new_transfer_senders` |
| Inside the union graph: union in-degree at t1, revocations | 0.141 [0.118, 0.167]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.t1_in_degree_union.future_revoke_count` |
| Inside the union graph: union in-degree at t1, drained owners | 0.195 [0.169, 0.216]; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.taus.t1_in_degree_union.future_drain_owners` |
| Inside the union graph [contrasts_prefixed]: C-PR minus C-PR (l=1), new approval pairs | Δτ 0.020 [-0.002, 0.043]; τa 0.221, τb 0.201; P(Δτ>0) 0.960; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.contrasts_prefixed[0]` |
| Inside the union graph [contrasts_prefixed]: C-PR minus C-PR (l=0), new transfer senders | Δτ -0.016 [-0.025, -0.007]; τa 0.259, τb 0.275; P(Δτ>0) 0.000; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.contrasts_prefixed[1]` |
| Inside the union graph [contrasts_after]: C-PR (l=1) minus t1 in-approve degree, new approval pairs | Δτ -0.043 [-0.053, -0.031]; τa 0.201, τb 0.244; P(Δτ>0) 0.000; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.contrasts_after[0]` |
| Inside the union graph [contrasts_after]: S-PR minus C-PR (l=1), new approval pairs | Δτ -0.081 [-0.106, -0.057]; τa 0.120, τb 0.201; P(Δτ>0) 0.000; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.contrasts_after[1]` |
| Inside the union graph [contrasts_after]: S-PR minus C-PR (l=0), new transfer senders | Δτ -0.026 [-0.039, -0.012]; τa 0.249, τb 0.275; P(Δτ>0) 0.000; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.contrasts_after[2]` |
| Inside the union graph [contrasts_after]: EndorseRank minus t1 in-approve degree, new approval pairs | Δτ -0.041 [-0.051, -0.031]; τa 0.202, τb 0.244; P(Δτ>0) 0.000; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.contrasts_after[3]` |
| Inside the union graph [contrasts_after]: AWP minus t1 in-degree, new transfer senders | Δτ 0.021 [0.005, 0.038]; τa 0.380, τb 0.358; P(Δτ>0) 1.000; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.contrasts_after[4]` |
| Inside the union graph [contrasts_after]: C-PR minus C-PR (l=0), new approval pairs | Δτ 0.111 [0.095, 0.130]; τa 0.221, τb 0.110; P(Δτ>0) 1.000; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.contrasts_after[5]` |
| Inside the union graph [contrasts_after]: C-PR minus EndorseRank, new approval pairs | Δτ 0.019 [-0.005, 0.042]; τa 0.221, τb 0.202; P(Δτ>0) 0.955; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.contrasts_after[6]` |
| Inside the union graph [contrasts_after]: C-PR minus AWP, new transfer senders | Δτ -0.120 [-0.136, -0.107]; τa 0.259, τb 0.380; P(Δτ>0) 0.000; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.contrasts_after[7]` |
| Inside the union graph [contrasts_after]: C-PR minus AWP, new approval pairs | Δτ 0.062 [0.042, 0.083]; τa 0.221, τb 0.159; P(Δτ>0) 1.000; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.contrasts_after[8]` |
| Inside the union graph [contrasts_after]: EndorseRank minus AWP, new approval pairs | Δτ 0.043 [0.013, 0.075]; τa 0.202, τb 0.159; P(Δτ>0) 0.998; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.contrasts_after[9]` |
| Inside the union graph [contrasts_after]: EndorseRank minus AWP, new transfer senders | Δτ -0.335 [-0.362, -0.306]; τa 0.045, τb 0.380; P(Δτ>0) 0.000; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.contrasts_after[10]` |
| Inside the union graph [baseline_contrasts]: C-PR minus t1 union in-degree, new approval pairs | Δτ 0.035 [0.022, 0.049]; τa 0.221, τb 0.186; P(Δτ>0) 1.000; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.baseline_contrasts[0]` |
| Inside the union graph [baseline_contrasts]: C-PR minus t1 union in-degree, new transfer senders | Δτ -0.089 [-0.103, -0.075]; τa 0.259, τb 0.349; P(Δτ>0) 0.000; B=400 | `holdout-w0/eval_summary.json` : `in_union_graph.baseline_contrasts[1]` |

### W0 labels by the class of the counted account (a description outside every rule)

| Quantity | Value | Source |
|---|---|---|
| W0 owners at the freeze: total | 4,116,471 | `holdout-w0/eval_summary.json` : `label_split.owners_at_freeze.total` |
| W0 owners at the freeze: user accounts | 3,926,375 | `holdout-w0/eval_summary.json` : `label_split.owners_at_freeze.user_accounts` |
| W0 owners at the freeze: contracts | 190,096 | `holdout-w0/eval_summary.json` : `label_split.owners_at_freeze.contracts` |
| W0 owners at the freeze: other | 0 | `holdout-w0/eval_summary.json` : `label_split.owners_at_freeze.other` |
| W0 new approval pairs: total | 748,258 | `holdout-w0/eval_summary.json` : `label_split.labels.future_new_approvers.total` |
| W0 new approval pairs: user accounts | 676,525 | `holdout-w0/eval_summary.json` : `label_split.labels.future_new_approvers.user_accounts` |
| W0 new approval pairs: contracts | 71,733 | `holdout-w0/eval_summary.json` : `label_split.labels.future_new_approvers.contracts` |
| W0 new approval pairs: other | 0 | `holdout-w0/eval_summary.json` : `label_split.labels.future_new_approvers.other` |
| W0 new approval pairs: share user accounts | 0.904 | `holdout-w0/eval_summary.json` : `label_split.labels.future_new_approvers.share_user_accounts` |
| W0 new approval pairs: share contracts | 0.096 | `holdout-w0/eval_summary.json` : `label_split.labels.future_new_approvers.share_contracts` |
| W0 new approval pairs: share other | 0.000 | `holdout-w0/eval_summary.json` : `label_split.labels.future_new_approvers.share_other` |
| W0 new approval pairs: spenders with label | 1,725 | `holdout-w0/eval_summary.json` : `label_split.labels.future_new_approvers.spenders_with_label` |
| W0 new approval pairs: spenders with user accounts | 1,322 | `holdout-w0/eval_summary.json` : `label_split.labels.future_new_approvers.spenders_with_user_accounts` |
| W0 new approval pairs: spenders with contracts | 876 | `holdout-w0/eval_summary.json` : `label_split.labels.future_new_approvers.spenders_with_contracts` |
| W0 new approval pairs: spenders with other | 0 | `holdout-w0/eval_summary.json` : `label_split.labels.future_new_approvers.spenders_with_other` |
| W0 revocations: total | 61,869 | `holdout-w0/eval_summary.json` : `label_split.labels.future_revoke_count.total` |
| W0 revocations: user accounts | 60,111 | `holdout-w0/eval_summary.json` : `label_split.labels.future_revoke_count.user_accounts` |
| W0 revocations: contracts | 1,758 | `holdout-w0/eval_summary.json` : `label_split.labels.future_revoke_count.contracts` |
| W0 revocations: other | 0 | `holdout-w0/eval_summary.json` : `label_split.labels.future_revoke_count.other` |
| W0 revocations: share user accounts | 0.972 | `holdout-w0/eval_summary.json` : `label_split.labels.future_revoke_count.share_user_accounts` |
| W0 revocations: share contracts | 0.028 | `holdout-w0/eval_summary.json` : `label_split.labels.future_revoke_count.share_contracts` |
| W0 revocations: share other | 0.000 | `holdout-w0/eval_summary.json` : `label_split.labels.future_revoke_count.share_other` |
| W0 revocations: spenders with label | 1,113 | `holdout-w0/eval_summary.json` : `label_split.labels.future_revoke_count.spenders_with_label` |
| W0 revocations: spenders with user accounts | 947 | `holdout-w0/eval_summary.json` : `label_split.labels.future_revoke_count.spenders_with_user_accounts` |
| W0 revocations: spenders with contracts | 287 | `holdout-w0/eval_summary.json` : `label_split.labels.future_revoke_count.spenders_with_contracts` |
| W0 revocations: spenders with other | 0 | `holdout-w0/eval_summary.json` : `label_split.labels.future_revoke_count.spenders_with_other` |
| W0 revoke rate: mean | 0.020 | `holdout-w0/eval_summary.json` : `label_split.labels.future_revoke_rate.mean` |
| W0 revoke rate: mean user accounts | 0.008 | `holdout-w0/eval_summary.json` : `label_split.labels.future_revoke_rate.mean_user_accounts` |
| W0 revoke rate: mean contracts | 0.012 | `holdout-w0/eval_summary.json` : `label_split.labels.future_revoke_rate.mean_contracts` |
| W0 revoke rate: mean other | 0.000 | `holdout-w0/eval_summary.json` : `label_split.labels.future_revoke_rate.mean_other` |
| W0 keep rate: mean | 0.980 | `holdout-w0/eval_summary.json` : `label_split.labels.future_keep_rate.mean` |
| W0 keep rate: mean user accounts | 0.597 | `holdout-w0/eval_summary.json` : `label_split.labels.future_keep_rate.mean_user_accounts` |
| W0 keep rate: mean contracts | 0.383 | `holdout-w0/eval_summary.json` : `label_split.labels.future_keep_rate.mean_contracts` |
| W0 keep rate: mean other | 0.000 | `holdout-w0/eval_summary.json` : `label_split.labels.future_keep_rate.mean_other` |
| W0 revoke value: total | 1.882e+77 | `holdout-w0/eval_summary.json` : `label_split.labels.future_revoke_value.total` |
| W0 revoke value: user accounts | 1.826e+77 | `holdout-w0/eval_summary.json` : `label_split.labels.future_revoke_value.user_accounts` |
| W0 revoke value: contracts | 5.626e+75 | `holdout-w0/eval_summary.json` : `label_split.labels.future_revoke_value.contracts` |
| W0 revoke value: other | 0.000 | `holdout-w0/eval_summary.json` : `label_split.labels.future_revoke_value.other` |
| W0 revoke value: share user accounts | 0.970 | `holdout-w0/eval_summary.json` : `label_split.labels.future_revoke_value.share_user_accounts` |
| W0 revoke value: share contracts | 0.030 | `holdout-w0/eval_summary.json` : `label_split.labels.future_revoke_value.share_contracts` |
| W0 revoke value: share other | 0.000 | `holdout-w0/eval_summary.json` : `label_split.labels.future_revoke_value.share_other` |
| W0 revoke value: spenders with label | 1,113 | `holdout-w0/eval_summary.json` : `label_split.labels.future_revoke_value.spenders_with_label` |
| W0 revoke value: spenders with user accounts | 947 | `holdout-w0/eval_summary.json` : `label_split.labels.future_revoke_value.spenders_with_user_accounts` |
| W0 revoke value: spenders with contracts | 287 | `holdout-w0/eval_summary.json` : `label_split.labels.future_revoke_value.spenders_with_contracts` |
| W0 revoke value: spenders with other | 0 | `holdout-w0/eval_summary.json` : `label_split.labels.future_revoke_value.spenders_with_other` |
| W0 new transfer senders: total | 651,474 | `holdout-w0/eval_summary.json` : `label_split.labels.future_new_transfer_senders.total` |
| W0 new transfer senders: user accounts | 562,007 | `holdout-w0/eval_summary.json` : `label_split.labels.future_new_transfer_senders.user_accounts` |
| W0 new transfer senders: contracts | 89,458 | `holdout-w0/eval_summary.json` : `label_split.labels.future_new_transfer_senders.contracts` |
| W0 new transfer senders: other | 9 | `holdout-w0/eval_summary.json` : `label_split.labels.future_new_transfer_senders.other` |
| W0 new transfer senders: share user accounts | 0.863 | `holdout-w0/eval_summary.json` : `label_split.labels.future_new_transfer_senders.share_user_accounts` |
| W0 new transfer senders: share contracts | 0.137 | `holdout-w0/eval_summary.json` : `label_split.labels.future_new_transfer_senders.share_contracts` |
| W0 new transfer senders: share other | 1.381e-05 | `holdout-w0/eval_summary.json` : `label_split.labels.future_new_transfer_senders.share_other` |
| W0 new transfer senders: spenders with label | 1,416 | `holdout-w0/eval_summary.json` : `label_split.labels.future_new_transfer_senders.spenders_with_label` |
| W0 new transfer senders: spenders with user accounts | 1,044 | `holdout-w0/eval_summary.json` : `label_split.labels.future_new_transfer_senders.spenders_with_user_accounts` |
| W0 new transfer senders: spenders with contracts | 883 | `holdout-w0/eval_summary.json` : `label_split.labels.future_new_transfer_senders.spenders_with_contracts` |
| W0 new transfer senders: spenders with other | 9 | `holdout-w0/eval_summary.json` : `label_split.labels.future_new_transfer_senders.spenders_with_other` |
| W0 drained owners: total | 570,724 | `holdout-w0/eval_summary.json` : `label_split.labels.future_drain_owners.total` |
| W0 drained owners: user accounts | 547,427 | `holdout-w0/eval_summary.json` : `label_split.labels.future_drain_owners.user_accounts` |
| W0 drained owners: contracts | 23,297 | `holdout-w0/eval_summary.json` : `label_split.labels.future_drain_owners.contracts` |
| W0 drained owners: other | 0 | `holdout-w0/eval_summary.json` : `label_split.labels.future_drain_owners.other` |
| W0 drained owners: share user accounts | 0.959 | `holdout-w0/eval_summary.json` : `label_split.labels.future_drain_owners.share_user_accounts` |
| W0 drained owners: share contracts | 0.041 | `holdout-w0/eval_summary.json` : `label_split.labels.future_drain_owners.share_contracts` |
| W0 drained owners: share other | 0.000 | `holdout-w0/eval_summary.json` : `label_split.labels.future_drain_owners.share_other` |
| W0 drained owners: spenders with label | 1,807 | `holdout-w0/eval_summary.json` : `label_split.labels.future_drain_owners.spenders_with_label` |
| W0 drained owners: spenders with user accounts | 1,271 | `holdout-w0/eval_summary.json` : `label_split.labels.future_drain_owners.spenders_with_user_accounts` |
| W0 drained owners: spenders with contracts | 926 | `holdout-w0/eval_summary.json` : `label_split.labels.future_drain_owners.spenders_with_contracts` |
| W0 drained owners: spenders with other | 0 | `holdout-w0/eval_summary.json` : `label_split.labels.future_drain_owners.spenders_with_other` |

## 7. Window W1 (scores at T_obs on the contract graph, labels July to September 2026; two of the registered criteria of rule B, F1 and F2, applied as a re-analysis)

Under the registration rule B holds only if each of its criteria holds. This analysis applies F1 and F2 only, so it reports "not met" when one of them fails and "both applied criteria hold" when both hold (docs/revision_contract_graph.md section 11).

| Quantity | Value | Source |
|---|---|---|
| Margin δ | 0.010 | `window-w1/eval_summary.json` : `delta` |
| Applied criteria | F1, F2 | `window-w1/eval_summary.json` : `applied_criteria` |
| Listed spenders of the twelve-month labels, class contract | 7,915 | `window-w1/eval_summary.json` : `spender_account_types.contract` |
| Listed spenders of the twelve-month labels, class user_account | 79 | `window-w1/eval_summary.json` : `spender_account_types.user_account` |
| Listed spenders of the twelve-month labels, class system | 1 | `window-w1/eval_summary.json` : `spender_account_types.system` |
| Listed spenders of the twelve-month labels, class untyped | 0 | `window-w1/eval_summary.json` : `spender_account_types.untyped` |
| Spender cohort (contracts) | 7,915 | `window-w1/eval_summary.json` : `spenders` |
| Gained a new approval pair | 1,491 | `window-w1/eval_summary.json` : `gained_new_approvals` |
| Gained a new transfer sender | 1,369 | `window-w1/eval_summary.json` : `gained_new_senders` |

### F1 and F2, two of rule B's registered criteria (comparator C-PR λ=0)

| Quantity | Value | Source |
|---|---|---|
| F1 | Δτ 0.074 [0.060, 0.087]; τa 0.104, τb 0.030; P(Δτ>0) 1.000; B=400; superiority: holds | `window-w1/eval_summary.json` : `rule_b.F1` |
| F2 | Δτ -0.016 [-0.022, -0.012]; τa 0.236, τb 0.253; P(Δτ>0) 0.000; B=400; non_inferiority: fails | `window-w1/eval_summary.json` : `rule_b.F2` |
| F6a | Δτ -0.043 [-0.061, -0.024]; τa 0.104, τb 0.147; P(Δτ>0) 0.000; B=400; no_worse: fails | `window-w1/eval_summary.json` : `rule_b.F6a` |
| F6b | Δτ -0.016 [-0.022, -0.012]; τa 0.236, τb 0.253; P(Δτ>0) 0.000; B=400; superiority: fails | `window-w1/eval_summary.json` : `rule_b.F6b` |
| Both applied criteria (F1 and F2) hold | no | `window-w1/eval_summary.json` : `rule_b.f1_f2_hold` |
| Reading | not met | `window-w1/eval_summary.json` : `rule_b.rule_b_reading` |
| F6 (both parts hold) | no | `window-w1/eval_summary.json` : `rule_b.F6` |

### Sensitivity 1 (comparator AWP)

| Quantity | Value | Source |
|---|---|---|
| F1 | Δτ 0.040 [0.026, 0.055]; τa 0.104, τb 0.064; P(Δτ>0) 1.000; B=400; superiority: holds | `window-w1/eval_summary.json` : `sensitivity_awp.F1` |
| F2 | Δτ -0.077 [-0.086, -0.069]; τa 0.236, τb 0.314; P(Δτ>0) 0.000; B=400; non_inferiority: fails | `window-w1/eval_summary.json` : `sensitivity_awp.F2` |
| Both applied criteria (F1 and F2) hold | no | `window-w1/eval_summary.json` : `sensitivity_awp.f1_f2_hold` |
| Reading | not met | `window-w1/eval_summary.json` : `sensitivity_awp.rule_b_reading` |

### Sensitivity 2 (members a graph leaves out as isolated nodes)

| Quantity | Value | Source |
|---|---|---|
| F1 | Δτ 0.073 [0.059, 0.086]; τa 0.111, τb 0.038; P(Δτ>0) 1.000; B=400; superiority: holds | `window-w1/eval_summary.json` : `sensitivity_isolated.F1` |
| F2 | Δτ -0.016 [-0.022, -0.011]; τa 0.238, τb 0.253; P(Δτ>0) 0.000; B=400; non_inferiority: fails | `window-w1/eval_summary.json` : `sensitivity_isolated.F2` |
| F6a | Δτ -0.062 [-0.081, -0.041]; τa 0.111, τb 0.173; P(Δτ>0) 0.000; B=400; no_worse: fails | `window-w1/eval_summary.json` : `sensitivity_isolated.F6a` |
| F6b | Δτ -0.016 [-0.022, -0.011]; τa 0.238, τb 0.253; P(Δτ>0) 0.000; B=400; superiority: fails | `window-w1/eval_summary.json` : `sensitivity_isolated.F6b` |
| Both applied criteria (F1 and F2) hold | no | `window-w1/eval_summary.json` : `sensitivity_isolated.f1_f2_hold` |
| Reading | not met | `window-w1/eval_summary.json` : `sensitivity_isolated.rule_b_reading` |
| F6 (both parts hold) | no | `window-w1/eval_summary.json` : `sensitivity_isolated.F6` |

### W1 spenders: τ_b (scores and the baselines counted on the contract graph)

| Quantity | Value | Source |
|---|---|---|
| Spenders: EndorseRank, new approval pairs | 0.147 [0.125, 0.170]; B=400 | `window-w1/eval_summary.json` : `spender_taus.endorserank.future_new_approvers` |
| Spenders: EndorseRank, new transfer senders | 0.064 [0.041, 0.085]; B=400 | `window-w1/eval_summary.json` : `spender_taus.endorserank.future_new_transfer_senders` |
| Spenders: EndorseRank (activity restarts), new approval pairs | 0.148 [0.126, 0.171]; B=400 | `window-w1/eval_summary.json` : `spender_taus.endorserank_activity.future_new_approvers` |
| Spenders: EndorseRank (activity restarts), new transfer senders | 0.072 [0.049, 0.093]; B=400 | `window-w1/eval_summary.json` : `spender_taus.endorserank_activity.future_new_transfer_senders` |
| Spenders: AWP, new approval pairs | 0.064 [0.042, 0.084]; B=400 | `window-w1/eval_summary.json` : `spender_taus.awp.future_new_approvers` |
| Spenders: AWP, new transfer senders | 0.314 [0.295, 0.332]; B=400 | `window-w1/eval_summary.json` : `spender_taus.awp.future_new_transfer_senders` |
| Spenders: C-PR (λ=1), new approval pairs | 0.147 [0.124, 0.170]; B=400 | `window-w1/eval_summary.json` : `spender_taus.cpr_l100.future_new_approvers` |
| Spenders: C-PR (λ=1), new transfer senders | 0.064 [0.041, 0.084]; B=400 | `window-w1/eval_summary.json` : `spender_taus.cpr_l100.future_new_transfer_senders` |
| Spenders: C-PR (λ=0), new approval pairs | 0.030 [0.008, 0.050]; B=400 | `window-w1/eval_summary.json` : `spender_taus.cpr_l0.future_new_approvers` |
| Spenders: C-PR (λ=0), new transfer senders | 0.253 [0.232, 0.272]; B=400 | `window-w1/eval_summary.json` : `spender_taus.cpr_l0.future_new_transfer_senders` |
| Spenders: C-PR (λ=0.25), new approval pairs | 0.103 [0.081, 0.124]; B=400 | `window-w1/eval_summary.json` : `spender_taus.cpr_l25.future_new_approvers` |
| Spenders: C-PR (λ=0.25), new transfer senders | 0.239 [0.219, 0.258]; B=400 | `window-w1/eval_summary.json` : `spender_taus.cpr_l25.future_new_transfer_senders` |
| Spenders: C-PR (λ=0.5), new approval pairs | 0.104 [0.083, 0.126]; B=400 | `window-w1/eval_summary.json` : `spender_taus.cpr_l50.future_new_approvers` |
| Spenders: C-PR (λ=0.5), new transfer senders | 0.236 [0.217, 0.255]; B=400 | `window-w1/eval_summary.json` : `spender_taus.cpr_l50.future_new_transfer_senders` |
| Spenders: C-PR (λ=0.75), new approval pairs | 0.104 [0.082, 0.126]; B=400 | `window-w1/eval_summary.json` : `spender_taus.cpr_l75.future_new_approvers` |
| Spenders: C-PR (λ=0.75), new transfer senders | 0.234 [0.215, 0.252]; B=400 | `window-w1/eval_summary.json` : `spender_taus.cpr_l75.future_new_transfer_senders` |
| Spenders: S-PR, new approval pairs | 0.055 [0.034, 0.073]; B=400 | `window-w1/eval_summary.json` : `spender_taus.spr.future_new_approvers` |
| Spenders: S-PR, new transfer senders | 0.242 [0.222, 0.261]; B=400 | `window-w1/eval_summary.json` : `spender_taus.spr.future_new_transfer_senders` |
| Spenders: in-approve degree at the freeze, new approval pairs | 0.181 [0.158, 0.208]; B=400 | `window-w1/eval_summary.json` : `spender_taus.in_approve_degree.future_new_approvers` |
| Spenders: in-approve degree at the freeze, new transfer senders | 0.072 [0.046, 0.096]; B=400 | `window-w1/eval_summary.json` : `spender_taus.in_approve_degree.future_new_transfer_senders` |
| Spenders: transfer in-degree at the freeze, new approval pairs | 0.031 [0.008, 0.052]; B=400 | `window-w1/eval_summary.json` : `spender_taus.in_degree.future_new_approvers` |
| Spenders: transfer in-degree at the freeze, new transfer senders | 0.302 [0.278, 0.323]; B=400 | `window-w1/eval_summary.json` : `spender_taus.in_degree.future_new_transfer_senders` |
| Spenders: in-approve value at the freeze, new approval pairs | 0.163 [0.141, 0.188]; B=400 | `window-w1/eval_summary.json` : `spender_taus.in_approve_value.future_new_approvers` |
| Spenders: in-approve value at the freeze, new transfer senders | 0.062 [0.037, 0.084]; B=400 | `window-w1/eval_summary.json` : `spender_taus.in_approve_value.future_new_transfer_senders` |
| Spenders: union in-degree at the freeze, new approval pairs | 0.093 [0.071, 0.114]; B=400 | `window-w1/eval_summary.json` : `spender_taus.in_degree_union.future_new_approvers` |
| Spenders: union in-degree at the freeze, new transfer senders | 0.292 [0.270, 0.312]; B=400 | `window-w1/eval_summary.json` : `spender_taus.in_degree_union.future_new_transfer_senders` |

### Sensitivity 2: τ_b with the members left out added as isolated nodes

| Quantity | Value | Source |
|---|---|---|
| Isolated nodes: EndorseRank, new approval pairs | 0.173 [0.150, 0.199]; B=400 | `window-w1/eval_summary.json` : `sensitivity_isolated.spender_taus.endorserank.future_new_approvers` |
| Isolated nodes: EndorseRank, new transfer senders | 0.070 [0.044, 0.093]; B=400 | `window-w1/eval_summary.json` : `sensitivity_isolated.spender_taus.endorserank.future_new_transfer_senders` |
| Isolated nodes: EndorseRank (activity restarts), new approval pairs | 0.148 [0.125, 0.170]; B=400 | `window-w1/eval_summary.json` : `sensitivity_isolated.spender_taus.endorserank_activity.future_new_approvers` |
| Isolated nodes: EndorseRank (activity restarts), new transfer senders | 0.072 [0.049, 0.093]; B=400 | `window-w1/eval_summary.json` : `sensitivity_isolated.spender_taus.endorserank_activity.future_new_transfer_senders` |
| Isolated nodes: AWP, new approval pairs | 0.064 [0.042, 0.084]; B=400 | `window-w1/eval_summary.json` : `sensitivity_isolated.spender_taus.awp.future_new_approvers` |
| Isolated nodes: AWP, new transfer senders | 0.314 [0.295, 0.332]; B=400 | `window-w1/eval_summary.json` : `sensitivity_isolated.spender_taus.awp.future_new_transfer_senders` |
| Isolated nodes: C-PR (λ=1), new approval pairs | 0.173 [0.150, 0.199]; B=400 | `window-w1/eval_summary.json` : `sensitivity_isolated.spender_taus.cpr_l100.future_new_approvers` |
| Isolated nodes: C-PR (λ=1), new transfer senders | 0.070 [0.044, 0.093]; B=400 | `window-w1/eval_summary.json` : `sensitivity_isolated.spender_taus.cpr_l100.future_new_transfer_senders` |
| Isolated nodes: C-PR (λ=0), new approval pairs | 0.038 [0.017, 0.058]; B=400 | `window-w1/eval_summary.json` : `sensitivity_isolated.spender_taus.cpr_l0.future_new_approvers` |
| Isolated nodes: C-PR (λ=0), new transfer senders | 0.253 [0.231, 0.274]; B=400 | `window-w1/eval_summary.json` : `sensitivity_isolated.spender_taus.cpr_l0.future_new_transfer_senders` |
| Isolated nodes: C-PR (λ=0.25), new approval pairs | 0.110 [0.089, 0.131]; B=400 | `window-w1/eval_summary.json` : `sensitivity_isolated.spender_taus.cpr_l25.future_new_approvers` |
| Isolated nodes: C-PR (λ=0.25), new transfer senders | 0.240 [0.221, 0.260]; B=400 | `window-w1/eval_summary.json` : `sensitivity_isolated.spender_taus.cpr_l25.future_new_transfer_senders` |
| Isolated nodes: C-PR (λ=0.5), new approval pairs | 0.111 [0.090, 0.132]; B=400 | `window-w1/eval_summary.json` : `sensitivity_isolated.spender_taus.cpr_l50.future_new_approvers` |
| Isolated nodes: C-PR (λ=0.5), new transfer senders | 0.238 [0.218, 0.256]; B=400 | `window-w1/eval_summary.json` : `sensitivity_isolated.spender_taus.cpr_l50.future_new_transfer_senders` |
| Isolated nodes: C-PR (λ=0.75), new approval pairs | 0.111 [0.090, 0.132]; B=400 | `window-w1/eval_summary.json` : `sensitivity_isolated.spender_taus.cpr_l75.future_new_approvers` |
| Isolated nodes: C-PR (λ=0.75), new transfer senders | 0.235 [0.215, 0.254]; B=400 | `window-w1/eval_summary.json` : `sensitivity_isolated.spender_taus.cpr_l75.future_new_transfer_senders` |
| Isolated nodes: S-PR, new approval pairs | 0.055 [0.034, 0.073]; B=400 | `window-w1/eval_summary.json` : `sensitivity_isolated.spender_taus.spr.future_new_approvers` |
| Isolated nodes: S-PR, new transfer senders | 0.242 [0.222, 0.261]; B=400 | `window-w1/eval_summary.json` : `sensitivity_isolated.spender_taus.spr.future_new_transfer_senders` |
| Isolated nodes: in-approve degree at the freeze, new approval pairs | 0.181 [0.158, 0.208]; B=400 | `window-w1/eval_summary.json` : `sensitivity_isolated.spender_taus.in_approve_degree.future_new_approvers` |
| Isolated nodes: in-approve degree at the freeze, new transfer senders | 0.072 [0.046, 0.096]; B=400 | `window-w1/eval_summary.json` : `sensitivity_isolated.spender_taus.in_approve_degree.future_new_transfer_senders` |
| Isolated nodes: transfer in-degree at the freeze, new approval pairs | 0.031 [0.008, 0.052]; B=400 | `window-w1/eval_summary.json` : `sensitivity_isolated.spender_taus.in_degree.future_new_approvers` |
| Isolated nodes: transfer in-degree at the freeze, new transfer senders | 0.302 [0.278, 0.323]; B=400 | `window-w1/eval_summary.json` : `sensitivity_isolated.spender_taus.in_degree.future_new_transfer_senders` |
| Isolated nodes: in-approve value at the freeze, new approval pairs | 0.163 [0.141, 0.188]; B=400 | `window-w1/eval_summary.json` : `sensitivity_isolated.spender_taus.in_approve_value.future_new_approvers` |
| Isolated nodes: in-approve value at the freeze, new transfer senders | 0.062 [0.037, 0.084]; B=400 | `window-w1/eval_summary.json` : `sensitivity_isolated.spender_taus.in_approve_value.future_new_transfer_senders` |
| Isolated nodes: union in-degree at the freeze, new approval pairs | 0.093 [0.071, 0.114]; B=400 | `window-w1/eval_summary.json` : `sensitivity_isolated.spender_taus.in_degree_union.future_new_approvers` |
| Isolated nodes: union in-degree at the freeze, new transfer senders | 0.292 [0.270, 0.312]; B=400 | `window-w1/eval_summary.json` : `sensitivity_isolated.spender_taus.in_degree_union.future_new_transfer_senders` |

### EndorseRank results and the union in-degree baseline (outside F1 and F2)

| Quantity | Value | Source |
|---|---|---|
| endorserank minus degree appr | Δτ -0.034 [-0.043, -0.025]; τa 0.147, τb 0.181; P(Δτ>0) 0.000; B=400 | `window-w1/eval_summary.json` : `endorserank_results.endorserank_minus_degree_appr` |
| awp minus degree send | Δτ 0.011 [0.001, 0.022]; τa 0.314, τb 0.302; P(Δτ>0) 0.995; B=400 | `window-w1/eval_summary.json` : `endorserank_results.awp_minus_degree_send` |
| cpr minus endorserank appr | Δτ -0.043 [-0.062, -0.025]; τa 0.104, τb 0.147; P(Δτ>0) 0.000; B=400 | `window-w1/eval_summary.json` : `endorserank_results.cpr_minus_endorserank_appr` |
| cpr minus union in degree appr | Δτ 0.011 [0.003, 0.019]; τa 0.104, τb 0.093; P(Δτ>0) 1.000; B=400 | `window-w1/eval_summary.json` : `baseline_contrasts.cpr_minus_union_in_degree_appr` |
| cpr minus union in degree send | Δτ -0.056 [-0.065, -0.047]; τa 0.236, τb 0.292; P(Δτ>0) 0.000; B=400 | `window-w1/eval_summary.json` : `baseline_contrasts.cpr_minus_union_in_degree_send` |

### W1: where the members of spenders_w1 lie in the contract graph

| Quantity | Value | Source |
|---|---|---|
| spenders_w1: members | 7,915 | `window-w1/eval_summary.json` : `cohort_coverage.spenders_w1.n` |
| spenders_w1: allowance layer | 1,975 (0.250) | `window-w1/eval_summary.json` : `cohort_coverage.spenders_w1.allowance_layer` |
| spenders_w1: transfer layer | 5,504 (0.695) | `window-w1/eval_summary.json` : `cohort_coverage.spenders_w1.transfer_layer` |
| spenders_w1: both layers | 1,720 (0.217) | `window-w1/eval_summary.json` : `cohort_coverage.spenders_w1.both_layers` |
| spenders_w1: union graph | 5,759 (0.728) | `window-w1/eval_summary.json` : `cohort_coverage.spenders_w1.union_graph` |
| spenders_w1: self pairs only | 0 (0.000) | `window-w1/eval_summary.json` : `cohort_coverage.spenders_w1.self_pairs_only` |
| spenders_w1: outside contract graph | 2,156 (0.272) | `window-w1/eval_summary.json` : `cohort_coverage.spenders_w1.outside_contract_graph` |

### W1: comparisons on the members inside the union graph only (decides no rule)

| Quantity | Value | Source |
|---|---|---|
| W1 members inside the union graph | 5,759 (0.728) | `window-w1/eval_summary.json` : `in_union_graph.n` |
| Inside the union graph: EndorseRank, new approval pairs | 0.197 [0.172, 0.222]; B=400 | `window-w1/eval_summary.json` : `in_union_graph.spender_taus.endorserank.future_new_approvers` |
| Inside the union graph: EndorseRank, new transfer senders | 0.030 [0.003, 0.054]; B=400 | `window-w1/eval_summary.json` : `in_union_graph.spender_taus.endorserank.future_new_transfer_senders` |
| Inside the union graph: EndorseRank (activity restarts), new approval pairs | 0.199 [0.175, 0.225]; B=400 | `window-w1/eval_summary.json` : `in_union_graph.spender_taus.endorserank_activity.future_new_approvers` |
| Inside the union graph: EndorseRank (activity restarts), new transfer senders | 0.043 [0.017, 0.068]; B=400 | `window-w1/eval_summary.json` : `in_union_graph.spender_taus.endorserank_activity.future_new_transfer_senders` |
| Inside the union graph: AWP, new approval pairs | 0.147 [0.123, 0.169]; B=400 | `window-w1/eval_summary.json` : `in_union_graph.spender_taus.awp.future_new_approvers` |
| Inside the union graph: AWP, new transfer senders | 0.372 [0.353, 0.388]; B=400 | `window-w1/eval_summary.json` : `in_union_graph.spender_taus.awp.future_new_transfer_senders` |
| Inside the union graph: C-PR (λ=1), new approval pairs | 0.196 [0.172, 0.222]; B=400 | `window-w1/eval_summary.json` : `in_union_graph.spender_taus.cpr_l100.future_new_approvers` |
| Inside the union graph: C-PR (λ=1), new transfer senders | 0.030 [0.002, 0.053]; B=400 | `window-w1/eval_summary.json` : `in_union_graph.spender_taus.cpr_l100.future_new_transfer_senders` |
| Inside the union graph: C-PR (λ=0), new approval pairs | 0.086 [0.056, 0.108]; B=400 | `window-w1/eval_summary.json` : `in_union_graph.spender_taus.cpr_l0.future_new_approvers` |
| Inside the union graph: C-PR (λ=0), new transfer senders | 0.270 [0.250, 0.292]; B=400 | `window-w1/eval_summary.json` : `in_union_graph.spender_taus.cpr_l0.future_new_transfer_senders` |
| Inside the union graph: C-PR (λ=0.25), new approval pairs | 0.201 [0.178, 0.223]; B=400 | `window-w1/eval_summary.json` : `in_union_graph.spender_taus.cpr_l25.future_new_approvers` |
| Inside the union graph: C-PR (λ=0.25), new transfer senders | 0.255 [0.234, 0.276]; B=400 | `window-w1/eval_summary.json` : `in_union_graph.spender_taus.cpr_l25.future_new_transfer_senders` |
| Inside the union graph: C-PR (λ=0.5), new approval pairs | 0.204 [0.180, 0.225]; B=400 | `window-w1/eval_summary.json` : `in_union_graph.spender_taus.cpr_l50.future_new_approvers` |
| Inside the union graph: C-PR (λ=0.5), new transfer senders | 0.251 [0.229, 0.272]; B=400 | `window-w1/eval_summary.json` : `in_union_graph.spender_taus.cpr_l50.future_new_transfer_senders` |
| Inside the union graph: C-PR (λ=0.75), new approval pairs | 0.204 [0.180, 0.226]; B=400 | `window-w1/eval_summary.json` : `in_union_graph.spender_taus.cpr_l75.future_new_approvers` |
| Inside the union graph: C-PR (λ=0.75), new transfer senders | 0.246 [0.225, 0.267]; B=400 | `window-w1/eval_summary.json` : `in_union_graph.spender_taus.cpr_l75.future_new_transfer_senders` |
| Inside the union graph: S-PR, new approval pairs | 0.101 [0.075, 0.122]; B=400 | `window-w1/eval_summary.json` : `in_union_graph.spender_taus.spr.future_new_approvers` |
| Inside the union graph: S-PR, new transfer senders | 0.234 [0.213, 0.253]; B=400 | `window-w1/eval_summary.json` : `in_union_graph.spender_taus.spr.future_new_transfer_senders` |
| Inside the union graph: in-approve degree at the freeze, new approval pairs | 0.235 [0.210, 0.261]; B=400 | `window-w1/eval_summary.json` : `in_union_graph.spender_taus.in_approve_degree.future_new_approvers` |
| Inside the union graph: in-approve degree at the freeze, new transfer senders | 0.047 [0.019, 0.071]; B=400 | `window-w1/eval_summary.json` : `in_union_graph.spender_taus.in_approve_degree.future_new_transfer_senders` |
| Inside the union graph: transfer in-degree at the freeze, new approval pairs | 0.087 [0.056, 0.109]; B=400 | `window-w1/eval_summary.json` : `in_union_graph.spender_taus.in_degree.future_new_approvers` |
| Inside the union graph: transfer in-degree at the freeze, new transfer senders | 0.352 [0.328, 0.372]; B=400 | `window-w1/eval_summary.json` : `in_union_graph.spender_taus.in_degree.future_new_transfer_senders` |
| Inside the union graph: in-approve value at the freeze, new approval pairs | 0.204 [0.179, 0.228]; B=400 | `window-w1/eval_summary.json` : `in_union_graph.spender_taus.in_approve_value.future_new_approvers` |
| Inside the union graph: in-approve value at the freeze, new transfer senders | 0.032 [0.007, 0.057]; B=400 | `window-w1/eval_summary.json` : `in_union_graph.spender_taus.in_approve_value.future_new_transfer_senders` |
| Inside the union graph: union in-degree at the freeze, new approval pairs | 0.177 [0.153, 0.199]; B=400 | `window-w1/eval_summary.json` : `in_union_graph.spender_taus.in_degree_union.future_new_approvers` |
| Inside the union graph: union in-degree at the freeze, new transfer senders | 0.344 [0.321, 0.364]; B=400 | `window-w1/eval_summary.json` : `in_union_graph.spender_taus.in_degree_union.future_new_transfer_senders` |
| Inside the union graph: cpr minus cpr l0 appr | Δτ 0.118 [0.101, 0.138]; τa 0.204, τb 0.086; P(Δτ>0) 1.000; B=400 | `window-w1/eval_summary.json` : `in_union_graph.contrasts.cpr_minus_cpr_l0_appr` |
| Inside the union graph: cpr minus cpr l0 send | Δτ -0.020 [-0.027, -0.011]; τa 0.251, τb 0.270; P(Δτ>0) 0.000; B=400 | `window-w1/eval_summary.json` : `in_union_graph.contrasts.cpr_minus_cpr_l0_send` |
| Inside the union graph: cpr minus cpr l100 appr | Δτ 0.007 [-0.017, 0.029]; τa 0.204, τb 0.196; P(Δτ>0) 0.700; B=400 | `window-w1/eval_summary.json` : `in_union_graph.contrasts.cpr_minus_cpr_l100_appr` |
| Inside the union graph: cpr minus awp appr | Δτ 0.057 [0.036, 0.080]; τa 0.204, τb 0.147; P(Δτ>0) 1.000; B=400 | `window-w1/eval_summary.json` : `in_union_graph.contrasts.cpr_minus_awp_appr` |
| Inside the union graph: cpr minus awp send | Δτ -0.121 [-0.135, -0.107]; τa 0.251, τb 0.372; P(Δτ>0) 0.000; B=400 | `window-w1/eval_summary.json` : `in_union_graph.contrasts.cpr_minus_awp_send` |
| Inside the union graph: cpr minus union in degree appr | Δτ 0.027 [0.014, 0.041]; τa 0.204, τb 0.177; P(Δτ>0) 1.000; B=400 | `window-w1/eval_summary.json` : `in_union_graph.contrasts.cpr_minus_union_in_degree_appr` |
| Inside the union graph: cpr minus union in degree send | Δτ -0.093 [-0.107, -0.077]; τa 0.251, τb 0.344; P(Δτ>0) 0.000; B=400 | `window-w1/eval_summary.json` : `in_union_graph.contrasts.cpr_minus_union_in_degree_send` |

### W1 labels by the class of the counted account (a description outside every rule)

| Quantity | Value | Source |
|---|---|---|
| W1 owners at the freeze: total | 3,809,524 | `window-w1/eval_summary.json` : `label_split.owners_at_freeze.total` |
| W1 owners at the freeze: user accounts | 3,611,886 | `window-w1/eval_summary.json` : `label_split.owners_at_freeze.user_accounts` |
| W1 owners at the freeze: contracts | 197,638 | `window-w1/eval_summary.json` : `label_split.owners_at_freeze.contracts` |
| W1 owners at the freeze: other | 0 | `window-w1/eval_summary.json` : `label_split.owners_at_freeze.other` |
| W1 new approval pairs: total | 702,275 | `window-w1/eval_summary.json` : `label_split.labels.future_new_approvers.total` |
| W1 new approval pairs: user accounts | 617,088 | `window-w1/eval_summary.json` : `label_split.labels.future_new_approvers.user_accounts` |
| W1 new approval pairs: contracts | 85,187 | `window-w1/eval_summary.json` : `label_split.labels.future_new_approvers.contracts` |
| W1 new approval pairs: other | 0 | `window-w1/eval_summary.json` : `label_split.labels.future_new_approvers.other` |
| W1 new approval pairs: share user accounts | 0.879 | `window-w1/eval_summary.json` : `label_split.labels.future_new_approvers.share_user_accounts` |
| W1 new approval pairs: share contracts | 0.121 | `window-w1/eval_summary.json` : `label_split.labels.future_new_approvers.share_contracts` |
| W1 new approval pairs: share other | 0.000 | `window-w1/eval_summary.json` : `label_split.labels.future_new_approvers.share_other` |
| W1 new approval pairs: spenders with label | 1,491 | `window-w1/eval_summary.json` : `label_split.labels.future_new_approvers.spenders_with_label` |
| W1 new approval pairs: spenders with user accounts | 1,220 | `window-w1/eval_summary.json` : `label_split.labels.future_new_approvers.spenders_with_user_accounts` |
| W1 new approval pairs: spenders with contracts | 641 | `window-w1/eval_summary.json` : `label_split.labels.future_new_approvers.spenders_with_contracts` |
| W1 new approval pairs: spenders with other | 0 | `window-w1/eval_summary.json` : `label_split.labels.future_new_approvers.spenders_with_other` |
| W1 revocations: total | 43,625 | `window-w1/eval_summary.json` : `label_split.labels.future_revoke_count.total` |
| W1 revocations: user accounts | 42,270 | `window-w1/eval_summary.json` : `label_split.labels.future_revoke_count.user_accounts` |
| W1 revocations: contracts | 1,355 | `window-w1/eval_summary.json` : `label_split.labels.future_revoke_count.contracts` |
| W1 revocations: other | 0 | `window-w1/eval_summary.json` : `label_split.labels.future_revoke_count.other` |
| W1 revocations: share user accounts | 0.969 | `window-w1/eval_summary.json` : `label_split.labels.future_revoke_count.share_user_accounts` |
| W1 revocations: share contracts | 0.031 | `window-w1/eval_summary.json` : `label_split.labels.future_revoke_count.share_contracts` |
| W1 revocations: share other | 0.000 | `window-w1/eval_summary.json` : `label_split.labels.future_revoke_count.share_other` |
| W1 revocations: spenders with label | 935 | `window-w1/eval_summary.json` : `label_split.labels.future_revoke_count.spenders_with_label` |
| W1 revocations: spenders with user accounts | 761 | `window-w1/eval_summary.json` : `label_split.labels.future_revoke_count.spenders_with_user_accounts` |
| W1 revocations: spenders with contracts | 279 | `window-w1/eval_summary.json` : `label_split.labels.future_revoke_count.spenders_with_contracts` |
| W1 revocations: spenders with other | 0 | `window-w1/eval_summary.json` : `label_split.labels.future_revoke_count.spenders_with_other` |
| W1 revoke rate: mean | 0.017 | `window-w1/eval_summary.json` : `label_split.labels.future_revoke_rate.mean` |
| W1 revoke rate: mean user accounts | 0.006 | `window-w1/eval_summary.json` : `label_split.labels.future_revoke_rate.mean_user_accounts` |
| W1 revoke rate: mean contracts | 0.012 | `window-w1/eval_summary.json` : `label_split.labels.future_revoke_rate.mean_contracts` |
| W1 revoke rate: mean other | 0.000 | `window-w1/eval_summary.json` : `label_split.labels.future_revoke_rate.mean_other` |
| W1 keep rate: mean | 0.983 | `window-w1/eval_summary.json` : `label_split.labels.future_keep_rate.mean` |
| W1 keep rate: mean user accounts | 0.604 | `window-w1/eval_summary.json` : `label_split.labels.future_keep_rate.mean_user_accounts` |
| W1 keep rate: mean contracts | 0.379 | `window-w1/eval_summary.json` : `label_split.labels.future_keep_rate.mean_contracts` |
| W1 keep rate: mean other | 0.000 | `window-w1/eval_summary.json` : `label_split.labels.future_keep_rate.mean_other` |
| W1 revoke value: total | 8.925e+76 | `window-w1/eval_summary.json` : `label_split.labels.future_revoke_value.total` |
| W1 revoke value: user accounts | 8.748e+76 | `window-w1/eval_summary.json` : `label_split.labels.future_revoke_value.user_accounts` |
| W1 revoke value: contracts | 1.772e+75 | `window-w1/eval_summary.json` : `label_split.labels.future_revoke_value.contracts` |
| W1 revoke value: other | 0.000 | `window-w1/eval_summary.json` : `label_split.labels.future_revoke_value.other` |
| W1 revoke value: share user accounts | 0.980 | `window-w1/eval_summary.json` : `label_split.labels.future_revoke_value.share_user_accounts` |
| W1 revoke value: share contracts | 0.020 | `window-w1/eval_summary.json` : `label_split.labels.future_revoke_value.share_contracts` |
| W1 revoke value: share other | 0.000 | `window-w1/eval_summary.json` : `label_split.labels.future_revoke_value.share_other` |
| W1 revoke value: spenders with label | 935 | `window-w1/eval_summary.json` : `label_split.labels.future_revoke_value.spenders_with_label` |
| W1 revoke value: spenders with user accounts | 761 | `window-w1/eval_summary.json` : `label_split.labels.future_revoke_value.spenders_with_user_accounts` |
| W1 revoke value: spenders with contracts | 279 | `window-w1/eval_summary.json` : `label_split.labels.future_revoke_value.spenders_with_contracts` |
| W1 revoke value: spenders with other | 0 | `window-w1/eval_summary.json` : `label_split.labels.future_revoke_value.spenders_with_other` |
| W1 new transfer senders: total | 618,461 | `window-w1/eval_summary.json` : `label_split.labels.future_new_transfer_senders.total` |
| W1 new transfer senders: user accounts | 509,194 | `window-w1/eval_summary.json` : `label_split.labels.future_new_transfer_senders.user_accounts` |
| W1 new transfer senders: contracts | 109,258 | `window-w1/eval_summary.json` : `label_split.labels.future_new_transfer_senders.contracts` |
| W1 new transfer senders: other | 9 | `window-w1/eval_summary.json` : `label_split.labels.future_new_transfer_senders.other` |
| W1 new transfer senders: share user accounts | 0.823 | `window-w1/eval_summary.json` : `label_split.labels.future_new_transfer_senders.share_user_accounts` |
| W1 new transfer senders: share contracts | 0.177 | `window-w1/eval_summary.json` : `label_split.labels.future_new_transfer_senders.share_contracts` |
| W1 new transfer senders: share other | 1.455e-05 | `window-w1/eval_summary.json` : `label_split.labels.future_new_transfer_senders.share_other` |
| W1 new transfer senders: spenders with label | 1,369 | `window-w1/eval_summary.json` : `label_split.labels.future_new_transfer_senders.spenders_with_label` |
| W1 new transfer senders: spenders with user accounts | 970 | `window-w1/eval_summary.json` : `label_split.labels.future_new_transfer_senders.spenders_with_user_accounts` |
| W1 new transfer senders: spenders with contracts | 855 | `window-w1/eval_summary.json` : `label_split.labels.future_new_transfer_senders.spenders_with_contracts` |
| W1 new transfer senders: spenders with other | 9 | `window-w1/eval_summary.json` : `label_split.labels.future_new_transfer_senders.spenders_with_other` |
| W1 drained owners: total | 528,557 | `window-w1/eval_summary.json` : `label_split.labels.future_drain_owners.total` |
| W1 drained owners: user accounts | 503,788 | `window-w1/eval_summary.json` : `label_split.labels.future_drain_owners.user_accounts` |
| W1 drained owners: contracts | 24,769 | `window-w1/eval_summary.json` : `label_split.labels.future_drain_owners.contracts` |
| W1 drained owners: other | 0 | `window-w1/eval_summary.json` : `label_split.labels.future_drain_owners.other` |
| W1 drained owners: share user accounts | 0.953 | `window-w1/eval_summary.json` : `label_split.labels.future_drain_owners.share_user_accounts` |
| W1 drained owners: share contracts | 0.047 | `window-w1/eval_summary.json` : `label_split.labels.future_drain_owners.share_contracts` |
| W1 drained owners: share other | 0.000 | `window-w1/eval_summary.json` : `label_split.labels.future_drain_owners.share_other` |
| W1 drained owners: spenders with label | 1,611 | `window-w1/eval_summary.json` : `label_split.labels.future_drain_owners.spenders_with_label` |
| W1 drained owners: spenders with user accounts | 1,139 | `window-w1/eval_summary.json` : `label_split.labels.future_drain_owners.spenders_with_user_accounts` |
| W1 drained owners: spenders with contracts | 847 | `window-w1/eval_summary.json` : `label_split.labels.future_drain_owners.spenders_with_contracts` |
| W1 drained owners: spenders with other | 0 | `window-w1/eval_summary.json` : `label_split.labels.future_drain_owners.spenders_with_other` |

### Supplementary spender contrasts (computed after the labels were known, outside every rule)

post hoc descriptions outside every rule, computed after the labels and the evaluation of the contract-graph variant were known (docs/revision_contract_graph.md section 13)

| Quantity | Value | Source |
|---|---|---|
| W0 EndorseRank (activity restarts) minus in-approve degree, new approval pairs | Δτ -0.041 [-0.053, -0.029]; τa 0.163, τb 0.204; P(Δτ>0) 0.000; B=400 | `supplementary/supplementary.json` : `w0.er_activity_minus_degree_appr` |
| W0 EndorseRank (activity restarts) minus EndorseRank, new approval pairs | Δτ -0.004 [-0.008, -0.0007761]; τa 0.163, τb 0.168; P(Δτ>0) 0.015; B=400 | `supplementary/supplementary.json` : `w0.er_activity_minus_er_appr` |
| W0 EndorseRank (activity restarts) minus EndorseRank, new transfer senders | Δτ 0.005 [0.002, 0.009]; τa 0.089, τb 0.084; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w0.er_activity_minus_er_send` |
| W0 EndorseRank minus AWP, new approval pairs | Δτ 0.070 [0.042, 0.096]; τa 0.168, τb 0.098; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w0.er_minus_awp_appr` |
| W0 EndorseRank minus AWP, new transfer senders | Δτ -0.246 [-0.271, -0.220]; τa 0.084, τb 0.330; P(Δτ>0) 0.000; B=400 | `supplementary/supplementary.json` : `w0.er_minus_awp_send` |
| W0 n | 7,864 | `supplementary/supplementary.json` : `w0.n` |
| W0 C-PR minus C-PR (λ=1), new transfer senders | Δτ 0.170 [0.148, 0.191]; τa 0.254, τb 0.084; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w0.cpr_minus_l100_send` |
| W0 C-PR minus EndorseRank, new transfer senders | Δτ 0.170 [0.148, 0.191]; τa 0.254, τb 0.084; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w0.cpr_minus_er_send` |
| W0 C-PR minus EndorseRank (activity restarts), new approval pairs | Δτ -0.022 [-0.042, -0.0003759]; τa 0.142, τb 0.163; P(Δτ>0) 0.025; B=400 | `supplementary/supplementary.json` : `w0.cpr_minus_er_activity_appr` |
| W0 C-PR minus EndorseRank (activity restarts), new transfer senders | Δτ 0.164 [0.142, 0.187]; τa 0.254, τb 0.089; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w0.cpr_minus_er_activity_send` |
| W0 C-PR minus S-PR, new approval pairs | Δτ 0.051 [0.038, 0.064]; τa 0.142, τb 0.091; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w0.cpr_minus_spr_appr` |
| W0 C-PR minus S-PR, new transfer senders | Δτ -0.011 [-0.021, -0.0004375]; τa 0.254, τb 0.264; P(Δτ>0) 0.020; B=400 | `supplementary/supplementary.json` : `w0.cpr_minus_spr_send` |
| W0 C-PR minus in-approve degree, new approval pairs | Δτ -0.062 [-0.082, -0.037]; τa 0.142, τb 0.204; P(Δτ>0) 0.000; B=400 | `supplementary/supplementary.json` : `w0.cpr_minus_degree_appr` |
| W0 C-PR minus in-approve degree, new transfer senders | Δτ 0.163 [0.142, 0.187]; τa 0.254, τb 0.091; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w0.cpr_minus_degree_send` |
| W0 C-PR minus transfer in-degree, new approval pairs | Δτ 0.072 [0.059, 0.086]; τa 0.142, τb 0.070; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w0.cpr_minus_in_degree_appr` |
| W0 C-PR minus transfer in-degree, new transfer senders | Δτ -0.064 [-0.075, -0.054]; τa 0.254, τb 0.318; P(Δτ>0) 0.000; B=400 | `supplementary/supplementary.json` : `w0.cpr_minus_in_degree_send` |
| W0 Spenders that had received a transfer before the freeze | 4,569 | `supplementary/supplementary.json` : `w0.recv_n` |
| W0 Received a transfer: C-PR, new approval pairs | 0.264 [0.244, 0.286]; B=400 | `supplementary/supplementary.json` : `w0.recv_cpr_tau_appr` |
| W0 Received a transfer: C-PR minus AWP, new approval pairs | Δτ 0.026 [0.013, 0.041]; τa 0.264, τb 0.238; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w0.recv_cpr_minus_awp_appr` |
| W0 Received a transfer: C-PR, new transfer senders | 0.327 [0.306, 0.347]; B=400 | `supplementary/supplementary.json` : `w0.recv_cpr_tau_send` |
| W0 Received a transfer: C-PR minus AWP, new transfer senders | Δτ -0.084 [-0.097, -0.069]; τa 0.327, τb 0.411; P(Δτ>0) 0.000; B=400 | `supplementary/supplementary.json` : `w0.recv_cpr_minus_awp_send` |
| W0 Received a transfer: C-PR minus in-approve degree, new approval pairs | Δτ 0.051 [0.025, 0.076]; τa 0.264, τb 0.212; P(Δτ>0) 0.998; B=400 | `supplementary/supplementary.json` : `w0.recv_cpr_minus_degree_appr` |
| W0 C-PR minus in-approve value, new approval pairs | Δτ -0.048 [-0.068, -0.024]; τa 0.142, τb 0.189; P(Δτ>0) 0.000; B=400 | `supplementary/supplementary.json` : `w0.cpr_minus_approve_value_appr` |
| W0 C-PR minus in-approve value, new transfer senders | Δτ 0.173 [0.152, 0.195]; τa 0.254, τb 0.081; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w0.cpr_minus_approve_value_send` |
| W1 EndorseRank (activity restarts) minus in-approve degree, new approval pairs | Δτ -0.033 [-0.044, -0.022]; τa 0.148, τb 0.181; P(Δτ>0) 0.000; B=400 | `supplementary/supplementary.json` : `w1.er_activity_minus_degree_appr` |
| W1 EndorseRank (activity restarts) minus EndorseRank, new approval pairs | Δτ 0.001 [-0.002, 0.005]; τa 0.148, τb 0.147; P(Δτ>0) 0.710; B=400 | `supplementary/supplementary.json` : `w1.er_activity_minus_er_appr` |
| W1 EndorseRank (activity restarts) minus EndorseRank, new transfer senders | Δτ 0.008 [0.004, 0.012]; τa 0.072, τb 0.064; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w1.er_activity_minus_er_send` |
| W1 EndorseRank minus AWP, new approval pairs | Δτ 0.083 [0.059, 0.110]; τa 0.147, τb 0.064; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w1.er_minus_awp_appr` |
| W1 EndorseRank minus AWP, new transfer senders | Δτ -0.250 [-0.273, -0.225]; τa 0.064, τb 0.314; P(Δτ>0) 0.000; B=400 | `supplementary/supplementary.json` : `w1.er_minus_awp_send` |
| W1 n | 7,915 | `supplementary/supplementary.json` : `w1.n` |
| W1 C-PR minus C-PR (λ=1), new transfer senders | Δτ 0.173 [0.152, 0.194]; τa 0.236, τb 0.064; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w1.cpr_minus_l100_send` |
| W1 C-PR minus EndorseRank, new transfer senders | Δτ 0.172 [0.152, 0.193]; τa 0.236, τb 0.064; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w1.cpr_minus_er_send` |
| W1 C-PR minus EndorseRank (activity restarts), new approval pairs | Δτ -0.044 [-0.063, -0.025]; τa 0.104, τb 0.148; P(Δτ>0) 0.000; B=400 | `supplementary/supplementary.json` : `w1.cpr_minus_er_activity_appr` |
| W1 C-PR minus EndorseRank (activity restarts), new transfer senders | Δτ 0.164 [0.144, 0.186]; τa 0.236, τb 0.072; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w1.cpr_minus_er_activity_send` |
| W1 C-PR minus S-PR, new approval pairs | Δτ 0.049 [0.036, 0.063]; τa 0.104, τb 0.055; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w1.cpr_minus_spr_appr` |
| W1 C-PR minus S-PR, new transfer senders | Δτ -0.006 [-0.015, 0.002]; τa 0.236, τb 0.242; P(Δτ>0) 0.080; B=400 | `supplementary/supplementary.json` : `w1.cpr_minus_spr_send` |
| W1 C-PR minus in-approve degree, new approval pairs | Δτ -0.077 [-0.097, -0.057]; τa 0.104, τb 0.181; P(Δτ>0) 0.000; B=400 | `supplementary/supplementary.json` : `w1.cpr_minus_degree_appr` |
| W1 C-PR minus in-approve degree, new transfer senders | Δτ 0.164 [0.141, 0.188]; τa 0.236, τb 0.072; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w1.cpr_minus_degree_send` |
| W1 C-PR minus transfer in-degree, new approval pairs | Δτ 0.072 [0.058, 0.087]; τa 0.104, τb 0.031; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w1.cpr_minus_in_degree_appr` |
| W1 C-PR minus transfer in-degree, new transfer senders | Δτ -0.066 [-0.075, -0.057]; τa 0.236, τb 0.302; P(Δτ>0) 0.000; B=400 | `supplementary/supplementary.json` : `w1.cpr_minus_in_degree_send` |
| W1 Spenders that had received a transfer before the freeze | 4,642 | `supplementary/supplementary.json` : `w1.recv_n` |
| W1 Received a transfer: C-PR, new approval pairs | 0.250 [0.229, 0.270]; B=400 | `supplementary/supplementary.json` : `w1.recv_cpr_tau_appr` |
| W1 Received a transfer: C-PR minus AWP, new approval pairs | Δτ 0.007 [-0.008, 0.021]; τa 0.250, τb 0.243; P(Δτ>0) 0.795; B=400 | `supplementary/supplementary.json` : `w1.recv_cpr_minus_awp_appr` |
| W1 Received a transfer: C-PR, new transfer senders | 0.313 [0.293, 0.334]; B=400 | `supplementary/supplementary.json` : `w1.recv_cpr_tau_send` |
| W1 Received a transfer: C-PR minus AWP, new transfer senders | Δτ -0.094 [-0.108, -0.079]; τa 0.313, τb 0.407; P(Δτ>0) 0.000; B=400 | `supplementary/supplementary.json` : `w1.recv_cpr_minus_awp_send` |
| W1 Received a transfer: C-PR minus in-approve degree, new approval pairs | Δτ 0.053 [0.025, 0.080]; τa 0.250, τb 0.197; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w1.recv_cpr_minus_degree_appr` |
| W1 C-PR minus in-approve value, new approval pairs | Δτ -0.059 [-0.079, -0.039]; τa 0.104, τb 0.163; P(Δτ>0) 0.000; B=400 | `supplementary/supplementary.json` : `w1.cpr_minus_approve_value_appr` |
| W1 C-PR minus in-approve value, new transfer senders | Δτ 0.174 [0.151, 0.197]; τa 0.236, τb 0.062; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `w1.cpr_minus_approve_value_send` |
| SAME Same window: C-PR minus EndorseRank, transfer family | Δτ 0.441 [0.423, 0.457]; τa 0.738, τb 0.297; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `same.cpr_minus_er_transfer` |
| SAME Same window: C-PR minus AWP, allowance family | Δτ 0.206 [0.188, 0.224]; τa 0.433, τb 0.227; P(Δτ>0) 1.000; B=400 | `supplementary/supplementary.json` : `same.cpr_minus_awp_allowance` |
| SAME n | 6,443 | `supplementary/supplementary.json` : `same.n` |

## 8. Sybil cost model (EndorseRank graph of contracts at T_obs)

quantities of the Sybil cost model on the contract graph; they compute no criterion and decide no rule (docs/revision_contract_graph.md section 13)

| Quantity | Value | Source |
|---|---|---|
| graph.nodes | 109,381 | `sybil-model/sybil_model.json` : `graph.nodes` |
| graph.edges | 114,997 | `sybil-model/sybil_model.json` : `graph.edges` |
| graph.pairs of zero weight left out | 9 | `sybil-model/sybil_model.json` : `graph.pairs_of_zero_weight_left_out` |
| sigma0 | 0.8581 | `sybil-model/sybil_model.json` : `sigma0` |
| b common | 8.451e-06 | `sybil-model/sybil_model.json` : `b_common` |
| r D | 0.9111 | `sybil-model/sybil_model.json` : `r_D` |
| damping.0.75.r D | 0.9114 | `sybil-model/sybil_model.json` : `damping.0.75.r_D` |
| damping.0.75.farm factor | 3.7342 | `sybil-model/sybil_model.json` : `damping.0.75.farm_factor` |
| damping.0.85.r D | 0.9111 | `sybil-model/sybil_model.json` : `damping.0.85.r_D` |
| damping.0.85.farm factor | 6.1627 | `sybil-model/sybil_model.json` : `damping.0.85.farm_factor` |
| damping.0.95.r D | 0.9103 | `sybil-model/sybil_model.json` : `damping.0.95.r_D` |
| damping.0.95.farm factor | 18.2965 | `sybil-model/sybil_model.json` : `damping.0.95.farm_factor` |
| ring20 collects times share | 6.1568 | `sybil-model/sybil_model.json` : `ring20_collects_times_share` |
| star.m | 10 | `sybil-model/sybil_model.json` : `star.m` |
| star.target score | 0.0002891 | `sybil-model/sybil_model.json` : `star.target_score` |
| star.closed form | 0.0002893 | `sybil-model/sybil_model.json` : `star.closed_form` |
| star.highest cohort endorserank | 0.0097 | `sybil-model/sybil_model.json` : `star.highest_cohort_endorserank` |
| star.ratio to highest | 0.0298 | `sybil-model/sybil_model.json` : `star.ratio_to_highest` |
| star.approvals per window | 20 | `sybil-model/sybil_model.json` : `star.approvals_per_window` |
| fresh approval share median owner | 0.6869 | `sybil-model/sybil_model.json` : `fresh_approval_share_median_owner` |
| owners | 9,452 | `sybil-model/sybil_model.json` : `owners` |
| farm size to reach cohort quantile.p50.score | 0.0000 | `sybil-model/sybil_model.json` : `farm_size_to_reach_cohort_quantile.p50.score` |
| farm size to reach cohort quantile.p50.farm addresses | 0.0000 | `sybil-model/sybil_model.json` : `farm_size_to_reach_cohort_quantile.p50.farm_addresses` |
| farm size to reach cohort quantile.p90.score | 9.871e-06 | `sybil-model/sybil_model.json` : `farm_size_to_reach_cohort_quantile.p90.score` |
| farm size to reach cohort quantile.p90.farm addresses | 0.0000 | `sybil-model/sybil_model.json` : `farm_size_to_reach_cohort_quantile.p90.farm_addresses` |
| farm size to reach cohort quantile.p99.score | 9.31e-05 | `sybil-model/sybil_model.json` : `farm_size_to_reach_cohort_quantile.p99.score` |
| farm size to reach cohort quantile.p99.farm addresses | 2.4198 | `sybil-model/sybil_model.json` : `farm_size_to_reach_cohort_quantile.p99.farm_addresses` |
| farm size to reach cohort quantile.p100.score | 0.0097 | `sybil-model/sybil_model.json` : `farm_size_to_reach_cohort_quantile.p100.score` |
| farm size to reach cohort quantile.p100.farm addresses | 373.2281 | `sybil-model/sybil_model.json` : `farm_size_to_reach_cohort_quantile.p100.farm_addresses` |
| cohort.n | 6,443 | `sybil-model/sybil_model.json` : `cohort.n` |
| cohort.with positive score | 1,243 | `sybil-model/sybil_model.json` : `cohort.with_positive_score` |
| contract farm.note | every address of a farm is a contract: it is deployed, and its allowance counts up to its balance of the token at the freeze | `sybil-model/sybil_model.json` : `contract_farm.note` |
| contract farm.deployments.ring20 | 20 | `sybil-model/sybil_model.json` : `contract_farm.deployments.ring20` |
| contract farm.deployments.star | 11 | `sybil-model/sybil_model.json` : `contract_farm.deployments.star` |
| contract farm.deployments.reach.p50 | 1 | `sybil-model/sybil_model.json` : `contract_farm.deployments.reach.p50` |
| contract farm.deployments.reach.p90 | 1 | `sybil-model/sybil_model.json` : `contract_farm.deployments.reach.p90` |
| contract farm.deployments.reach.p99 | 4 | `sybil-model/sybil_model.json` : `contract_farm.deployments.reach.p99` |
| contract farm.deployments.reach.p100 | 375 | `sybil-model/sybil_model.json` : `contract_farm.deployments.reach.p100` |
| contract farm.evm gas.G transaction | 21,000 | `sybil-model/sybil_model.json` : `contract_farm.evm_gas.G_transaction` |
| contract farm.evm gas.G txcreate | 32,000 | `sybil-model/sybil_model.json` : `contract_farm.evm_gas.G_txcreate` |
| contract farm.evm gas.G create | 32,000 | `sybil-model/sybil_model.json` : `contract_farm.evm_gas.G_create` |
| contract farm.evm gas.G codedeposit per byte | 200 | `sybil-model/sybil_model.json` : `contract_farm.evm_gas.G_codedeposit_per_byte` |
| contract farm.evm gas.creation by transaction at least | 53,000 | `sybil-model/sybil_model.json` : `contract_farm.evm_gas.creation_by_transaction_at_least` |
| contract farm.evm gas.creation by create at least | 32,000 | `sybil-model/sybil_model.json` : `contract_farm.evm_gas.creation_by_create_at_least` |
| contract farm.evm gas.source | Ethereum Yellow Paper, Appendix G (fee schedule); execution gas only, without the fee for posting data to L1 | `sybil-model/sybil_model.json` : `contract_farm.evm_gas.source` |
| contract farm.value weight.m allowance usd | 0.0710 | `sybil-model/sybil_model.json` : `contract_farm.value_weight.m_allowance_usd` |
| contract farm.value weight.b allowance | 15.4734 | `sybil-model/sybil_model.json` : `contract_farm.value_weight.b_allowance` |
| contract farm.value weight.V at usd.1 | 1.0000 | `sybil-model/sybil_model.json` : `contract_farm.value_weight.V_at_usd.1` |
| contract farm.value weight.V at usd.10 | 1.0000 | `sybil-model/sybil_model.json` : `contract_farm.value_weight.V_at_usd.10` |
| contract farm.value weight.V at usd.100 | 1.0000 | `sybil-model/sybil_model.json` : `contract_farm.value_weight.V_at_usd.100` |

### Sensitivity to a balance threshold θ (pairs whose capped value is at least θ)

| Quantity | Value | Source |
|---|---|---|
| θ = USD 1: theta usd | 1.0000 | `sybil-model/sybil_model.json` : `balance_threshold.1.theta_usd` |
| θ = USD 1: pairs kept | 4,247 | `sybil-model/sybil_model.json` : `balance_threshold.1.pairs_kept` |
| θ = USD 1: share of pairs kept | 0.0369 | `sybil-model/sybil_model.json` : `balance_threshold.1.share_of_pairs_kept` |
| θ = USD 1: owners kept | 2,390 | `sybil-model/sybil_model.json` : `balance_threshold.1.owners_kept` |
| θ = USD 1: spenders kept | 1,074 | `sybil-model/sybil_model.json` : `balance_threshold.1.spenders_kept` |
| θ = USD 1: cohort with positive score | 699 | `sybil-model/sybil_model.json` : `balance_threshold.1.cohort_with_positive_score` |
| θ = USD 1: cohort tau with main | 0.7092 | `sybil-model/sybil_model.json` : `balance_threshold.1.cohort_tau_with_main` |
| θ = USD 1: graph.nodes | 3,394 | `sybil-model/sybil_model.json` : `balance_threshold.1.graph.nodes` |
| θ = USD 1: graph.edges | 4,247 | `sybil-model/sybil_model.json` : `balance_threshold.1.graph.edges` |
| θ = USD 1: b common | 0.0001737 | `sybil-model/sybil_model.json` : `balance_threshold.1.b_common` |
| θ = USD 1: r D | 0.5172 | `sybil-model/sybil_model.json` : `balance_threshold.1.r_D` |
| θ = USD 1: star.m | 10 | `sybil-model/sybil_model.json` : `balance_threshold.1.star.m` |
| θ = USD 1: star.target score | 0.0059 | `sybil-model/sybil_model.json` : `balance_threshold.1.star.target_score` |
| θ = USD 1: star.closed form | 0.0059 | `sybil-model/sybil_model.json` : `balance_threshold.1.star.closed_form` |
| θ = USD 1: star.highest cohort endorserank | 0.0636 | `sybil-model/sybil_model.json` : `balance_threshold.1.star.highest_cohort_endorserank` |
| θ = USD 1: star.ratio to highest | 0.0923 | `sybil-model/sybil_model.json` : `balance_threshold.1.star.ratio_to_highest` |
| θ = USD 1: star.approvals per window | 20 | `sybil-model/sybil_model.json` : `balance_threshold.1.star.approvals_per_window` |
| θ = USD 1: farm size to reach cohort quantile.p50.score | 0.0000 | `sybil-model/sybil_model.json` : `balance_threshold.1.farm_size_to_reach_cohort_quantile.p50.score` |
| θ = USD 1: farm size to reach cohort quantile.p50.farm addresses | 0.0000 | `sybil-model/sybil_model.json` : `balance_threshold.1.farm_size_to_reach_cohort_quantile.p50.farm_addresses` |
| θ = USD 1: farm size to reach cohort quantile.p90.score | 0.0001737 | `sybil-model/sybil_model.json` : `balance_threshold.1.farm_size_to_reach_cohort_quantile.p90.score` |
| θ = USD 1: farm size to reach cohort quantile.p90.farm addresses | 0.0000 | `sybil-model/sybil_model.json` : `balance_threshold.1.farm_size_to_reach_cohort_quantile.p90.farm_addresses` |
| θ = USD 1: farm size to reach cohort quantile.p99.score | 0.0007209 | `sybil-model/sybil_model.json` : `balance_threshold.1.farm_size_to_reach_cohort_quantile.p99.score` |
| θ = USD 1: farm size to reach cohort quantile.p99.farm addresses | 0.1783 | `sybil-model/sybil_model.json` : `balance_threshold.1.farm_size_to_reach_cohort_quantile.p99.farm_addresses` |
| θ = USD 1: farm size to reach cohort quantile.p100.score | 0.0636 | `sybil-model/sybil_model.json` : `balance_threshold.1.farm_size_to_reach_cohort_quantile.p100.score` |
| θ = USD 1: farm size to reach cohort quantile.p100.farm addresses | 118.3362 | `sybil-model/sybil_model.json` : `balance_threshold.1.farm_size_to_reach_cohort_quantile.p100.farm_addresses` |
| θ = USD 1: star balance usd | 11.0000 | `sybil-model/sybil_model.json` : `balance_threshold.1.star_balance_usd` |
| θ = USD 10: theta usd | 10.0000 | `sybil-model/sybil_model.json` : `balance_threshold.10.theta_usd` |
| θ = USD 10: pairs kept | 2,167 | `sybil-model/sybil_model.json` : `balance_threshold.10.pairs_kept` |
| θ = USD 10: share of pairs kept | 0.0188 | `sybil-model/sybil_model.json` : `balance_threshold.10.share_of_pairs_kept` |
| θ = USD 10: owners kept | 1,000 | `sybil-model/sybil_model.json` : `balance_threshold.10.owners_kept` |
| θ = USD 10: spenders kept | 817 | `sybil-model/sybil_model.json` : `balance_threshold.10.spenders_kept` |
| θ = USD 10: cohort with positive score | 491 | `sybil-model/sybil_model.json` : `balance_threshold.10.cohort_with_positive_score` |
| θ = USD 10: cohort tau with main | 0.5890 | `sybil-model/sybil_model.json` : `balance_threshold.10.cohort_tau_with_main` |
| θ = USD 10: graph.nodes | 1,769 | `sybil-model/sybil_model.json` : `balance_threshold.10.graph.nodes` |
| θ = USD 10: graph.edges | 2,167 | `sybil-model/sybil_model.json` : `balance_threshold.10.graph.edges` |
| θ = USD 10: b common | 0.0003645 | `sybil-model/sybil_model.json` : `balance_threshold.10.b_common` |
| θ = USD 10: r D | 0.5822 | `sybil-model/sybil_model.json` : `balance_threshold.10.r_D` |
| θ = USD 10: star.m | 10 | `sybil-model/sybil_model.json` : `balance_threshold.10.star.m` |
| θ = USD 10: star.target score | 0.0122 | `sybil-model/sybil_model.json` : `balance_threshold.10.star.target_score` |
| θ = USD 10: star.closed form | 0.0125 | `sybil-model/sybil_model.json` : `balance_threshold.10.star.closed_form` |
| θ = USD 10: star.highest cohort endorserank | 0.0374 | `sybil-model/sybil_model.json` : `balance_threshold.10.star.highest_cohort_endorserank` |
| θ = USD 10: star.ratio to highest | 0.3254 | `sybil-model/sybil_model.json` : `balance_threshold.10.star.ratio_to_highest` |
| θ = USD 10: star.approvals per window | 20 | `sybil-model/sybil_model.json` : `balance_threshold.10.star.approvals_per_window` |
| θ = USD 10: farm size to reach cohort quantile.p50.score | 0.0000 | `sybil-model/sybil_model.json` : `balance_threshold.10.farm_size_to_reach_cohort_quantile.p50.score` |
| θ = USD 10: farm size to reach cohort quantile.p50.farm addresses | 0.0000 | `sybil-model/sybil_model.json` : `balance_threshold.10.farm_size_to_reach_cohort_quantile.p50.farm_addresses` |
| θ = USD 10: farm size to reach cohort quantile.p90.score | 0.0000 | `sybil-model/sybil_model.json` : `balance_threshold.10.farm_size_to_reach_cohort_quantile.p90.score` |
| θ = USD 10: farm size to reach cohort quantile.p90.farm addresses | 0.0000 | `sybil-model/sybil_model.json` : `balance_threshold.10.farm_size_to_reach_cohort_quantile.p90.farm_addresses` |
| θ = USD 10: farm size to reach cohort quantile.p99.score | 0.0010 | `sybil-model/sybil_model.json` : `balance_threshold.10.farm_size_to_reach_cohort_quantile.p99.score` |
| θ = USD 10: farm size to reach cohort quantile.p99.farm addresses | 0.0000 | `sybil-model/sybil_model.json` : `balance_threshold.10.farm_size_to_reach_cohort_quantile.p99.farm_addresses` |
| θ = USD 10: farm size to reach cohort quantile.p100.score | 0.0374 | `sybil-model/sybil_model.json` : `balance_threshold.10.farm_size_to_reach_cohort_quantile.p100.score` |
| θ = USD 10: farm size to reach cohort quantile.p100.farm addresses | 32.2806 | `sybil-model/sybil_model.json` : `balance_threshold.10.farm_size_to_reach_cohort_quantile.p100.farm_addresses` |
| θ = USD 10: star balance usd | 110.0000 | `sybil-model/sybil_model.json` : `balance_threshold.10.star_balance_usd` |
| θ = USD 100: theta usd | 100.0000 | `sybil-model/sybil_model.json` : `balance_threshold.100.theta_usd` |
| θ = USD 100: pairs kept | 992 | `sybil-model/sybil_model.json` : `balance_threshold.100.pairs_kept` |
| θ = USD 100: share of pairs kept | 0.0086 | `sybil-model/sybil_model.json` : `balance_threshold.100.share_of_pairs_kept` |
| θ = USD 100: owners kept | 500 | `sybil-model/sybil_model.json` : `balance_threshold.100.owners_kept` |
| θ = USD 100: spenders kept | 352 | `sybil-model/sybil_model.json` : `balance_threshold.100.spenders_kept` |
| θ = USD 100: cohort with positive score | 308 | `sybil-model/sybil_model.json` : `balance_threshold.100.cohort_with_positive_score` |
| θ = USD 100: cohort tau with main | 0.4643 | `sybil-model/sybil_model.json` : `balance_threshold.100.cohort_tau_with_main` |
| θ = USD 100: graph.nodes | 837 | `sybil-model/sybil_model.json` : `balance_threshold.100.graph.nodes` |
| θ = USD 100: graph.edges | 992 | `sybil-model/sybil_model.json` : `balance_threshold.100.graph.edges` |
| θ = USD 100: b common | 0.0007739 | `sybil-model/sybil_model.json` : `balance_threshold.100.b_common` |
| θ = USD 100: r D | 0.5856 | `sybil-model/sybil_model.json` : `balance_threshold.100.r_D` |
| θ = USD 100: star.m | 10 | `sybil-model/sybil_model.json` : `balance_threshold.100.star.m` |
| θ = USD 100: star.target score | 0.0251 | `sybil-model/sybil_model.json` : `balance_threshold.100.star.target_score` |
| θ = USD 100: star.closed form | 0.0265 | `sybil-model/sybil_model.json` : `balance_threshold.100.star.closed_form` |
| θ = USD 100: star.highest cohort endorserank | 0.0238 | `sybil-model/sybil_model.json` : `balance_threshold.100.star.highest_cohort_endorserank` |
| θ = USD 100: star.ratio to highest | 1.0535 | `sybil-model/sybil_model.json` : `balance_threshold.100.star.ratio_to_highest` |
| θ = USD 100: star.approvals per window | 20 | `sybil-model/sybil_model.json` : `balance_threshold.100.star.approvals_per_window` |
| θ = USD 100: farm size to reach cohort quantile.p50.score | 0.0000 | `sybil-model/sybil_model.json` : `balance_threshold.100.farm_size_to_reach_cohort_quantile.p50.score` |
| θ = USD 100: farm size to reach cohort quantile.p50.farm addresses | 0.0000 | `sybil-model/sybil_model.json` : `balance_threshold.100.farm_size_to_reach_cohort_quantile.p50.farm_addresses` |
| θ = USD 100: farm size to reach cohort quantile.p90.score | 0.0000 | `sybil-model/sybil_model.json` : `balance_threshold.100.farm_size_to_reach_cohort_quantile.p90.score` |
| θ = USD 100: farm size to reach cohort quantile.p90.farm addresses | 0.0000 | `sybil-model/sybil_model.json` : `balance_threshold.100.farm_size_to_reach_cohort_quantile.p90.farm_addresses` |
| θ = USD 100: farm size to reach cohort quantile.p99.score | 0.0016 | `sybil-model/sybil_model.json` : `balance_threshold.100.farm_size_to_reach_cohort_quantile.p99.score` |
| θ = USD 100: farm size to reach cohort quantile.p99.farm addresses | 0.0000 | `sybil-model/sybil_model.json` : `balance_threshold.100.farm_size_to_reach_cohort_quantile.p99.farm_addresses` |
| θ = USD 100: farm size to reach cohort quantile.p100.score | 0.0238 | `sybil-model/sybil_model.json` : `balance_threshold.100.farm_size_to_reach_cohort_quantile.p100.score` |
| θ = USD 100: farm size to reach cohort quantile.p100.farm addresses | 8.8625 | `sybil-model/sybil_model.json` : `balance_threshold.100.farm_size_to_reach_cohort_quantile.p100.farm_addresses` |
| θ = USD 100: star balance usd | 1,100 | `sybil-model/sybil_model.json` : `balance_threshold.100.star_balance_usd` |

## 9. Robustness

| Quantity | Value | Source |
|---|---|---|
| Damping endorserank_d75: iterations | 32 | `same-window/eval_summary.json` : `damping.endorserank_d75.iterations` |
| Damping endorserank_d75: transfer family | 0.297 [0.280, 0.317]; B=400 | `same-window/eval_summary.json` : `damping.endorserank_d75.transfer` |
| Damping endorserank_d75: allowance family | 0.839 [0.828, 0.849]; B=400 | `same-window/eval_summary.json` : `damping.endorserank_d75.allowance` |
| Damping endorserank_d75: Sybil stability family | 0.220 [0.206, 0.237]; B=400 | `same-window/eval_summary.json` : `damping.endorserank_d75.sybil_stability` |
| Damping awp_d75: iterations | 57 | `same-window/eval_summary.json` : `damping.awp_d75.iterations` |
| Damping awp_d75: transfer family | 0.750 [0.742, 0.757]; B=400 | `same-window/eval_summary.json` : `damping.awp_d75.transfer` |
| Damping awp_d75: allowance family | 0.224 [0.204, 0.244]; B=400 | `same-window/eval_summary.json` : `damping.awp_d75.allowance` |
| Damping awp_d75: Sybil stability family | 0.643 [0.634, 0.651]; B=400 | `same-window/eval_summary.json` : `damping.awp_d75.sybil_stability` |
| Damping endorserank_d85: iterations | 56 | `same-window/eval_summary.json` : `damping.endorserank_d85.iterations` |
| Damping endorserank_d85: transfer family | 0.297 [0.280, 0.317]; B=400 | `same-window/eval_summary.json` : `damping.endorserank_d85.transfer` |
| Damping endorserank_d85: allowance family | 0.839 [0.828, 0.849]; B=400 | `same-window/eval_summary.json` : `damping.endorserank_d85.allowance` |
| Damping endorserank_d85: Sybil stability family | 0.220 [0.206, 0.237]; B=400 | `same-window/eval_summary.json` : `damping.endorserank_d85.sybil_stability` |
| Damping awp_d85: iterations | 98 | `same-window/eval_summary.json` : `damping.awp_d85.iterations` |
| Damping awp_d85: transfer family | 0.755 [0.748, 0.762]; B=400 | `same-window/eval_summary.json` : `damping.awp_d85.transfer` |
| Damping awp_d85: allowance family | 0.227 [0.206, 0.245]; B=400 | `same-window/eval_summary.json` : `damping.awp_d85.allowance` |
| Damping awp_d85: Sybil stability family | 0.643 [0.635, 0.651]; B=400 | `same-window/eval_summary.json` : `damping.awp_d85.sybil_stability` |
| Damping endorserank_d95: iterations | 176 | `same-window/eval_summary.json` : `damping.endorserank_d95.iterations` |
| Damping endorserank_d95: transfer family | 0.297 [0.280, 0.317]; B=400 | `same-window/eval_summary.json` : `damping.endorserank_d95.transfer` |
| Damping endorserank_d95: allowance family | 0.839 [0.828, 0.849]; B=400 | `same-window/eval_summary.json` : `damping.endorserank_d95.allowance` |
| Damping endorserank_d95: Sybil stability family | 0.220 [0.206, 0.237]; B=400 | `same-window/eval_summary.json` : `damping.endorserank_d95.sybil_stability` |
| Damping awp_d95: iterations | 294 | `same-window/eval_summary.json` : `damping.awp_d95.iterations` |
| Damping awp_d95: transfer family | 0.761 [0.754, 0.768]; B=400 | `same-window/eval_summary.json` : `damping.awp_d95.transfer` |
| Damping awp_d95: allowance family | 0.228 [0.207, 0.246]; B=400 | `same-window/eval_summary.json` : `damping.awp_d95.allowance` |
| Damping awp_d95: Sybil stability family | 0.641 [0.633, 0.650]; B=400 | `same-window/eval_summary.json` : `damping.awp_d95.sybil_stability` |
| Slope 1: EndorseRank, transfer | 0.297 | `robustness/robustness.json` : `value_slope.1.endorserank.transfer` |
| Slope 1: EndorseRank, allowance | 0.839 | `robustness/robustness.json` : `value_slope.1.endorserank.allowance` |
| Slope 1: EndorseRank, Sybil stability | 0.220 | `robustness/robustness.json` : `value_slope.1.endorserank.sybil_stability` |
| Slope 1: AWP, transfer | 0.755 | `robustness/robustness.json` : `value_slope.1.awp.transfer` |
| Slope 1: AWP, allowance | 0.227 | `robustness/robustness.json` : `value_slope.1.awp.allowance` |
| Slope 1: AWP, Sybil stability | 0.643 | `robustness/robustness.json` : `value_slope.1.awp.sybil_stability` |
| Slope 01x: EndorseRank, transfer | 0.297 | `robustness/robustness.json` : `value_slope.01x.endorserank.transfer` |
| Slope 01x: EndorseRank, allowance | 0.839 | `robustness/robustness.json` : `value_slope.01x.endorserank.allowance` |
| Slope 01x: EndorseRank, Sybil stability | 0.220 | `robustness/robustness.json` : `value_slope.01x.endorserank.sybil_stability` |
| Slope 01x: AWP, transfer | 0.754 | `robustness/robustness.json` : `value_slope.01x.awp.transfer` |
| Slope 01x: AWP, allowance | 0.227 | `robustness/robustness.json` : `value_slope.01x.awp.allowance` |
| Slope 01x: AWP, Sybil stability | 0.642 | `robustness/robustness.json` : `value_slope.01x.awp.sybil_stability` |
| Slope 01x: EndorseRank rank agreement with the main score | 0.999 | `robustness/robustness.json` : `value_slope.01x.tau_with_main.endorserank` |
| Slope 01x: AWP rank agreement with the main score | 0.986 | `robustness/robustness.json` : `value_slope.01x.tau_with_main.awp` |
| Slope 10x: EndorseRank, transfer | 0.297 | `robustness/robustness.json` : `value_slope.10x.endorserank.transfer` |
| Slope 10x: EndorseRank, allowance | 0.838 | `robustness/robustness.json` : `value_slope.10x.endorserank.allowance` |
| Slope 10x: EndorseRank, Sybil stability | 0.221 | `robustness/robustness.json` : `value_slope.10x.endorserank.sybil_stability` |
| Slope 10x: AWP, transfer | 0.756 | `robustness/robustness.json` : `value_slope.10x.awp.transfer` |
| Slope 10x: AWP, allowance | 0.225 | `robustness/robustness.json` : `value_slope.10x.awp.allowance` |
| Slope 10x: AWP, Sybil stability | 0.643 | `robustness/robustness.json` : `value_slope.10x.awp.sybil_stability` |
| Slope 10x: EndorseRank rank agreement with the main score | 0.998 | `robustness/robustness.json` : `value_slope.10x.tau_with_main.endorserank` |
| Slope 10x: AWP rank agreement with the main score | 0.984 | `robustness/robustness.json` : `value_slope.10x.tau_with_main.awp` |
| Stage n=1,000: EndorseRank, transfer | 0.322 | `robustness/robustness.json` : `sample_definition[0].endorserank.transfer` |
| Stage n=1,000: EndorseRank, allowance | 0.860 | `robustness/robustness.json` : `sample_definition[0].endorserank.allowance` |
| Stage n=1,000: EndorseRank, Sybil stability | 0.230 | `robustness/robustness.json` : `sample_definition[0].endorserank.sybil_stability` |
| Stage n=1,000: AWP, transfer | 0.771 | `robustness/robustness.json` : `sample_definition[0].awp.transfer` |
| Stage n=1,000: AWP, allowance | 0.246 | `robustness/robustness.json` : `sample_definition[0].awp.allowance` |
| Stage n=1,000: AWP, Sybil stability | 0.666 | `robustness/robustness.json` : `sample_definition[0].awp.sybil_stability` |
| Stage n=1,000: allowance edges | 1,611 | `robustness/robustness.json` : `sample_definition[0].allowance_edges` |
| Stage n=1,000: transfer edges | 120,296 | `robustness/robustness.json` : `sample_definition[0].transfer_edges` |
| Stage n=2,000: EndorseRank, transfer | 0.324 | `robustness/robustness.json` : `sample_definition[1].endorserank.transfer` |
| Stage n=2,000: EndorseRank, allowance | 0.853 | `robustness/robustness.json` : `sample_definition[1].endorserank.allowance` |
| Stage n=2,000: EndorseRank, Sybil stability | 0.237 | `robustness/robustness.json` : `sample_definition[1].endorserank.sybil_stability` |
| Stage n=2,000: AWP, transfer | 0.762 | `robustness/robustness.json` : `sample_definition[1].awp.transfer` |
| Stage n=2,000: AWP, allowance | 0.248 | `robustness/robustness.json` : `sample_definition[1].awp.allowance` |
| Stage n=2,000: AWP, Sybil stability | 0.657 | `robustness/robustness.json` : `sample_definition[1].awp.sybil_stability` |
| Stage n=2,000: allowance edges | 4,788 | `robustness/robustness.json` : `sample_definition[1].allowance_edges` |
| Stage n=2,000: transfer edges | 235,934 | `robustness/robustness.json` : `sample_definition[1].transfer_edges` |
| Stage n=5,000: EndorseRank, transfer | 0.303 | `robustness/robustness.json` : `sample_definition[2].endorserank.transfer` |
| Stage n=5,000: EndorseRank, allowance | 0.839 | `robustness/robustness.json` : `sample_definition[2].endorserank.allowance` |
| Stage n=5,000: EndorseRank, Sybil stability | 0.226 | `robustness/robustness.json` : `sample_definition[2].endorserank.sybil_stability` |
| Stage n=5,000: AWP, transfer | 0.760 | `robustness/robustness.json` : `sample_definition[2].awp.transfer` |
| Stage n=5,000: AWP, allowance | 0.235 | `robustness/robustness.json` : `sample_definition[2].awp.allowance` |
| Stage n=5,000: AWP, Sybil stability | 0.648 | `robustness/robustness.json` : `sample_definition[2].awp.sybil_stability` |
| Stage n=5,000: allowance edges | 11,249 | `robustness/robustness.json` : `sample_definition[2].allowance_edges` |
| Stage n=5,000: transfer edges | 889,794 | `robustness/robustness.json` : `sample_definition[2].transfer_edges` |
| Stage n=6,443: EndorseRank, transfer | 0.297 | `robustness/robustness.json` : `sample_definition[3].endorserank.transfer` |
| Stage n=6,443: EndorseRank, allowance | 0.839 | `robustness/robustness.json` : `sample_definition[3].endorserank.allowance` |
| Stage n=6,443: EndorseRank, Sybil stability | 0.220 | `robustness/robustness.json` : `sample_definition[3].endorserank.sybil_stability` |
| Stage n=6,443: AWP, transfer | 0.753 | `robustness/robustness.json` : `sample_definition[3].awp.transfer` |
| Stage n=6,443: AWP, allowance | 0.226 | `robustness/robustness.json` : `sample_definition[3].awp.allowance` |
| Stage n=6,443: AWP, Sybil stability | 0.643 | `robustness/robustness.json` : `sample_definition[3].awp.sybil_stability` |
| Stage n=6,443: allowance edges | 16,324 | `robustness/robustness.json` : `sample_definition[3].allowance_edges` |
| Stage n=6,443: transfer edges | 1,063,593 | `robustness/robustness.json` : `sample_definition[3].transfer_edges` |

### Uncapped allowance layer (sensitivity; decides no rule)

| Quantity | Value | Source |
|---|---|---|
| W0: allowance pairs, capped | 17,940 | `robustness/robustness.json` : `uncapped_allowances.w0.allowance_pairs.capped` |
| W0: allowance pairs, uncapped | 275,917 | `robustness/robustness.json` : `uncapped_allowances.w0.allowance_pairs.uncapped` |
| W0 uncapped: EndorseRank, new approval pairs | 0.088 [0.067, 0.107]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.endorserank.future_new_approvers` |
| W0 uncapped: EndorseRank, new transfer senders | 0.185 [0.166, 0.202]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.endorserank.future_new_transfer_senders` |
| W0 uncapped: EndorseRank, revocations | 0.084 [0.064, 0.107]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.endorserank.future_revoke_count` |
| W0 uncapped: EndorseRank, drained owners | 0.123 [0.106, 0.142]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.endorserank.future_drain_owners` |
| W0 uncapped: EndorseRank (activity restarts), new approval pairs | 0.134 [0.113, 0.154]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.endorserank_activity.future_new_approvers` |
| W0 uncapped: EndorseRank (activity restarts), new transfer senders | 0.222 [0.203, 0.239]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.endorserank_activity.future_new_transfer_senders` |
| W0 uncapped: EndorseRank (activity restarts), revocations | 0.127 [0.106, 0.147]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.endorserank_activity.future_revoke_count` |
| W0 uncapped: EndorseRank (activity restarts), drained owners | 0.183 [0.164, 0.203]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.endorserank_activity.future_drain_owners` |
| W0 uncapped: AWP, new approval pairs | 0.098 [0.079, 0.119]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.awp.future_new_approvers` |
| W0 uncapped: AWP, new transfer senders | 0.330 [0.313, 0.347]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.awp.future_new_transfer_senders` |
| W0 uncapped: AWP, revocations | 0.099 [0.079, 0.121]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.awp.future_revoke_count` |
| W0 uncapped: AWP, drained owners | 0.131 [0.112, 0.152]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.awp.future_drain_owners` |
| W0 uncapped: C-PR (λ=1), new approval pairs | 0.086 [0.066, 0.106]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.cpr_l100.future_new_approvers` |
| W0 uncapped: C-PR (λ=1), new transfer senders | 0.183 [0.164, 0.200]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.cpr_l100.future_new_transfer_senders` |
| W0 uncapped: C-PR (λ=1), revocations | 0.080 [0.059, 0.102]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.cpr_l100.future_revoke_count` |
| W0 uncapped: C-PR (λ=1), drained owners | 0.119 [0.101, 0.138]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.cpr_l100.future_drain_owners` |
| W0 uncapped: C-PR (λ=0), new approval pairs | 0.070 [0.052, 0.091]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.cpr_l0.future_new_approvers` |
| W0 uncapped: C-PR (λ=0), new transfer senders | 0.268 [0.250, 0.285]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.cpr_l0.future_new_transfer_senders` |
| W0 uncapped: C-PR (λ=0), revocations | 0.071 [0.052, 0.094]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.cpr_l0.future_revoke_count` |
| W0 uncapped: C-PR (λ=0), drained owners | 0.094 [0.076, 0.114]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.cpr_l0.future_drain_owners` |
| W0 uncapped: C-PR (λ=0.25), new approval pairs | 0.150 [0.131, 0.171]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.cpr_l25.future_new_approvers` |
| W0 uncapped: C-PR (λ=0.25), new transfer senders | 0.253 [0.235, 0.270]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.cpr_l25.future_new_transfer_senders` |
| W0 uncapped: C-PR (λ=0.25), revocations | 0.121 [0.103, 0.142]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.cpr_l25.future_revoke_count` |
| W0 uncapped: C-PR (λ=0.25), drained owners | 0.175 [0.157, 0.196]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.cpr_l25.future_drain_owners` |
| W0 uncapped: C-PR (λ=0.5), new approval pairs | 0.150 [0.131, 0.171]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.cpr_l50.future_new_approvers` |
| W0 uncapped: C-PR (λ=0.5), new transfer senders | 0.248 [0.230, 0.265]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.cpr_l50.future_new_transfer_senders` |
| W0 uncapped: C-PR (λ=0.5), revocations | 0.120 [0.102, 0.142]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.cpr_l50.future_revoke_count` |
| W0 uncapped: C-PR (λ=0.5), drained owners | 0.178 [0.159, 0.198]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.cpr_l50.future_drain_owners` |
| W0 uncapped: C-PR (λ=0.75), new approval pairs | 0.148 [0.129, 0.169]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.cpr_l75.future_new_approvers` |
| W0 uncapped: C-PR (λ=0.75), new transfer senders | 0.242 [0.224, 0.259]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.cpr_l75.future_new_transfer_senders` |
| W0 uncapped: C-PR (λ=0.75), revocations | 0.118 [0.100, 0.140]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.cpr_l75.future_revoke_count` |
| W0 uncapped: C-PR (λ=0.75), drained owners | 0.177 [0.157, 0.197]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.cpr_l75.future_drain_owners` |
| W0 uncapped: S-PR, new approval pairs | 0.069 [0.051, 0.090]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.spr.future_new_approvers` |
| W0 uncapped: S-PR, new transfer senders | 0.273 [0.255, 0.291]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.spr.future_new_transfer_senders` |
| W0 uncapped: S-PR, revocations | 0.073 [0.054, 0.095]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.spr.future_revoke_count` |
| W0 uncapped: S-PR, drained owners | 0.101 [0.082, 0.121]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.spr.future_drain_owners` |
| W0 uncapped: in-approve degree at t1, new approval pairs | 0.105 [0.084, 0.129]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.t1_in_approve_degree.future_new_approvers` |
| W0 uncapped: in-approve degree at t1, new transfer senders | 0.196 [0.172, 0.215]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.t1_in_approve_degree.future_new_transfer_senders` |
| W0 uncapped: in-approve degree at t1, revocations | 0.078 [0.055, 0.104]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.t1_in_approve_degree.future_revoke_count` |
| W0 uncapped: in-approve degree at t1, drained owners | 0.138 [0.117, 0.161]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.t1_in_approve_degree.future_drain_owners` |
| W0 uncapped: transfer in-degree at t1, new approval pairs | 0.070 [0.050, 0.091]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.t1_in_degree.future_new_approvers` |
| W0 uncapped: transfer in-degree at t1, new transfer senders | 0.318 [0.298, 0.336]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.t1_in_degree.future_new_transfer_senders` |
| W0 uncapped: transfer in-degree at t1, revocations | 0.061 [0.040, 0.083]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.t1_in_degree.future_revoke_count` |
| W0 uncapped: transfer in-degree at t1, drained owners | 0.092 [0.072, 0.113]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.t1_in_degree.future_drain_owners` |
| W0 uncapped: in-approve value at t1, new approval pairs | 0.094 [0.073, 0.116]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.t1_in_approve_value.future_new_approvers` |
| W0 uncapped: in-approve value at t1, new transfer senders | 0.183 [0.161, 0.203]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.t1_in_approve_value.future_new_transfer_senders` |
| W0 uncapped: in-approve value at t1, revocations | 0.062 [0.040, 0.086]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.t1_in_approve_value.future_revoke_count` |
| W0 uncapped: in-approve value at t1, drained owners | 0.133 [0.113, 0.155]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.t1_in_approve_value.future_drain_owners` |
| W0 uncapped: union in-degree at t1, new approval pairs | 0.146 [0.127, 0.165]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.t1_in_degree_union.future_new_approvers` |
| W0 uncapped: union in-degree at t1, new transfer senders | 0.286 [0.265, 0.304]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.t1_in_degree_union.future_new_transfer_senders` |
| W0 uncapped: union in-degree at t1, revocations | 0.118 [0.100, 0.141]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.t1_in_degree_union.future_revoke_count` |
| W0 uncapped: union in-degree at t1, drained owners | 0.169 [0.151, 0.188]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.taus.t1_in_degree_union.future_drain_owners` |
| W0 uncapped [contrasts_prefixed]: C-PR minus C-PR (l=1), new approval pairs | Δτ 0.064 [0.051, 0.076]; τa 0.150, τb 0.086; P(Δτ>0) 1.000; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.contrasts_prefixed[0]` |
| W0 uncapped [contrasts_prefixed]: C-PR minus C-PR (l=0), new transfer senders | Δτ -0.019 [-0.027, -0.012]; τa 0.248, τb 0.268; P(Δτ>0) 0.000; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.contrasts_prefixed[1]` |
| W0 uncapped [contrasts_after]: C-PR (l=1) minus t1 in-approve degree, new approval pairs | Δτ -0.019 [-0.026, -0.011]; τa 0.086, τb 0.105; P(Δτ>0) 0.000; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.contrasts_after[0]` |
| W0 uncapped [contrasts_after]: S-PR minus C-PR (l=1), new approval pairs | Δτ -0.018 [-0.035, -0.001]; τa 0.069, τb 0.086; P(Δτ>0) 0.015; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.contrasts_after[1]` |
| W0 uncapped [contrasts_after]: S-PR minus C-PR (l=0), new transfer senders | Δτ 0.006 [-0.003, 0.012]; τa 0.273, τb 0.268; P(Δτ>0) 0.910; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.contrasts_after[2]` |
| W0 uncapped [contrasts_after]: EndorseRank minus t1 in-approve degree, new approval pairs | Δτ -0.018 [-0.025, -0.011]; τa 0.088, τb 0.105; P(Δτ>0) 0.000; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.contrasts_after[3]` |
| W0 uncapped [contrasts_after]: AWP minus t1 in-degree, new transfer senders | Δτ 0.012 [0.003, 0.023]; τa 0.330, τb 0.318; P(Δτ>0) 0.998; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.contrasts_after[4]` |
| W0 uncapped [contrasts_after]: C-PR minus C-PR (l=0), new approval pairs | Δτ 0.079 [0.065, 0.094]; τa 0.150, τb 0.070; P(Δτ>0) 1.000; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.contrasts_after[5]` |
| W0 uncapped [contrasts_after]: C-PR minus EndorseRank, new approval pairs | Δτ 0.062 [0.050, 0.075]; τa 0.150, τb 0.088; P(Δτ>0) 1.000; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.contrasts_after[6]` |
| W0 uncapped [contrasts_after]: C-PR minus AWP, new transfer senders | Δτ -0.082 [-0.093, -0.071]; τa 0.248, τb 0.330; P(Δτ>0) 0.000; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.contrasts_after[7]` |
| W0 uncapped [contrasts_after]: C-PR minus AWP, new approval pairs | Δτ 0.052 [0.033, 0.069]; τa 0.150, τb 0.098; P(Δτ>0) 1.000; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.contrasts_after[8]` |
| W0 uncapped [contrasts_after]: EndorseRank minus AWP, new approval pairs | Δτ -0.011 [-0.031, 0.012]; τa 0.088, τb 0.098; P(Δτ>0) 0.163; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.contrasts_after[9]` |
| W0 uncapped [contrasts_after]: EndorseRank minus AWP, new transfer senders | Δτ -0.145 [-0.163, -0.129]; τa 0.185, τb 0.330; P(Δτ>0) 0.000; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.contrasts_after[10]` |
| W0 uncapped [baseline_contrasts]: C-PR minus t1 union in-degree, new approval pairs | Δτ 0.004 [-0.004, 0.012]; τa 0.150, τb 0.146; P(Δτ>0) 0.838; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.baseline_contrasts[0]` |
| W0 uncapped [baseline_contrasts]: C-PR minus t1 union in-degree, new transfer senders | Δτ -0.037 [-0.045, -0.029]; τa 0.248, τb 0.286; P(Δτ>0) 0.000; B=400 | `robustness/robustness.json` : `uncapped_allowances.w0.baseline_contrasts[1]` |
| W1: allowance pairs, capped | 115,006 | `robustness/robustness.json` : `uncapped_allowances.w1.allowance_pairs.capped` |
| W1: allowance pairs, uncapped | 302,559 | `robustness/robustness.json` : `uncapped_allowances.w1.allowance_pairs.uncapped` |
| W1 uncapped: EndorseRank, new approval pairs | 0.078 [0.058, 0.099]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w1.spender_taus.endorserank.future_new_approvers` |
| W1 uncapped: EndorseRank, new transfer senders | 0.177 [0.156, 0.197]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w1.spender_taus.endorserank.future_new_transfer_senders` |
| W1 uncapped: EndorseRank (activity restarts), new approval pairs | 0.128 [0.107, 0.150]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w1.spender_taus.endorserank_activity.future_new_approvers` |
| W1 uncapped: EndorseRank (activity restarts), new transfer senders | 0.197 [0.175, 0.218]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w1.spender_taus.endorserank_activity.future_new_transfer_senders` |
| W1 uncapped: AWP, new approval pairs | 0.064 [0.042, 0.084]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w1.spender_taus.awp.future_new_approvers` |
| W1 uncapped: AWP, new transfer senders | 0.314 [0.295, 0.332]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w1.spender_taus.awp.future_new_transfer_senders` |
| W1 uncapped: C-PR (λ=1), new approval pairs | 0.077 [0.057, 0.097]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w1.spender_taus.cpr_l100.future_new_approvers` |
| W1 uncapped: C-PR (λ=1), new transfer senders | 0.181 [0.159, 0.200]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w1.spender_taus.cpr_l100.future_new_transfer_senders` |
| W1 uncapped: C-PR (λ=0), new approval pairs | 0.030 [0.008, 0.050]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w1.spender_taus.cpr_l0.future_new_approvers` |
| W1 uncapped: C-PR (λ=0), new transfer senders | 0.253 [0.232, 0.272]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w1.spender_taus.cpr_l0.future_new_transfer_senders` |
| W1 uncapped: C-PR (λ=0.25), new approval pairs | 0.117 [0.093, 0.138]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w1.spender_taus.cpr_l25.future_new_approvers` |
| W1 uncapped: C-PR (λ=0.25), new transfer senders | 0.239 [0.218, 0.258]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w1.spender_taus.cpr_l25.future_new_transfer_senders` |
| W1 uncapped: C-PR (λ=0.5), new approval pairs | 0.118 [0.094, 0.139]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w1.spender_taus.cpr_l50.future_new_approvers` |
| W1 uncapped: C-PR (λ=0.5), new transfer senders | 0.234 [0.214, 0.253]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w1.spender_taus.cpr_l50.future_new_transfer_senders` |
| W1 uncapped: C-PR (λ=0.75), new approval pairs | 0.117 [0.094, 0.139]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w1.spender_taus.cpr_l75.future_new_approvers` |
| W1 uncapped: C-PR (λ=0.75), new transfer senders | 0.230 [0.210, 0.249]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w1.spender_taus.cpr_l75.future_new_transfer_senders` |
| W1 uncapped: S-PR, new approval pairs | 0.037 [0.017, 0.058]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w1.spender_taus.spr.future_new_approvers` |
| W1 uncapped: S-PR, new transfer senders | 0.264 [0.244, 0.283]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w1.spender_taus.spr.future_new_transfer_senders` |
| W1 uncapped: in-approve degree at the freeze, new approval pairs | 0.102 [0.080, 0.125]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w1.spender_taus.in_approve_degree.future_new_approvers` |
| W1 uncapped: in-approve degree at the freeze, new transfer senders | 0.189 [0.166, 0.209]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w1.spender_taus.in_approve_degree.future_new_transfer_senders` |
| W1 uncapped: transfer in-degree at the freeze, new approval pairs | 0.031 [0.008, 0.052]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w1.spender_taus.in_degree.future_new_approvers` |
| W1 uncapped: transfer in-degree at the freeze, new transfer senders | 0.302 [0.278, 0.323]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w1.spender_taus.in_degree.future_new_transfer_senders` |
| W1 uncapped: in-approve value at the freeze, new approval pairs | 0.092 [0.072, 0.113]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w1.spender_taus.in_approve_value.future_new_approvers` |
| W1 uncapped: in-approve value at the freeze, new transfer senders | 0.181 [0.159, 0.201]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w1.spender_taus.in_approve_value.future_new_transfer_senders` |
| W1 uncapped: union in-degree at the freeze, new approval pairs | 0.118 [0.095, 0.140]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w1.spender_taus.in_degree_union.future_new_approvers` |
| W1 uncapped: union in-degree at the freeze, new transfer senders | 0.274 [0.249, 0.294]; B=400 | `robustness/robustness.json` : `uncapped_allowances.w1.spender_taus.in_degree_union.future_new_transfer_senders` |
| W1 uncapped: cpr minus cpr l0 appr | Δτ 0.088 [0.074, 0.103]; τa 0.118, τb 0.030; P(Δτ>0) 1.000; B=400 | `robustness/robustness.json` : `uncapped_allowances.w1.contrasts.cpr_minus_cpr_l0_appr` |
| W1 uncapped: cpr minus cpr l0 send | Δτ -0.018 [-0.028, -0.011]; τa 0.234, τb 0.253; P(Δτ>0) 0.000; B=400 | `robustness/robustness.json` : `uncapped_allowances.w1.contrasts.cpr_minus_cpr_l0_send` |
| W1 uncapped: cpr minus cpr l100 appr | Δτ 0.041 [0.031, 0.053]; τa 0.118, τb 0.077; P(Δτ>0) 1.000; B=400 | `robustness/robustness.json` : `uncapped_allowances.w1.contrasts.cpr_minus_cpr_l100_appr` |
| W1 uncapped: cpr minus awp appr | Δτ 0.054 [0.038, 0.071]; τa 0.118, τb 0.064; P(Δτ>0) 1.000; B=400 | `robustness/robustness.json` : `uncapped_allowances.w1.contrasts.cpr_minus_awp_appr` |
| W1 uncapped: cpr minus awp send | Δτ -0.079 [-0.090, -0.071]; τa 0.234, τb 0.314; P(Δτ>0) 0.000; B=400 | `robustness/robustness.json` : `uncapped_allowances.w1.contrasts.cpr_minus_awp_send` |
| W1 uncapped: cpr minus union in degree appr | Δτ 8.467e-05 [-0.007, 0.008]; τa 0.118, τb 0.118; P(Δτ>0) 0.497; B=400 | `robustness/robustness.json` : `uncapped_allowances.w1.contrasts.cpr_minus_union_in_degree_appr` |
| W1 uncapped: cpr minus union in degree send | Δτ -0.040 [-0.047, -0.031]; τa 0.234, τb 0.274; P(Δτ>0) 0.000; B=400 | `robustness/robustness.json` : `uncapped_allowances.w1.contrasts.cpr_minus_union_in_degree_send` |

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
| Full graphs: EndorseRank | mean 0.101 s, SD 0.009 s; runs 0.101, 0.112, 0.096, 0.107, 0.089; peak 13.7 MB; iterations 56; \|V\| 109,381; \|E\| 114,997 | `benchmark/benchmark.json` : `main.endorserank` |
| Full graphs: AWP | mean 2.821 s, SD 0.189 s; runs 2.964, 2.792, 2.852, 2.514, 2.984; peak 228.2 MB; iterations 98; \|V\| 1,298,649; \|E\| 2,580,381 | `benchmark/benchmark.json` : `main.awp` |
| Full graphs: C-PR (λ=0.5) | mean 3.080 s, SD 0.184 s; runs 2.954, 2.963, 3.394, 3.095, 2.993; peak 204.8 MB; iterations 92; \|V\| 1,299,479; \|E\| 2,591,253 | `benchmark/benchmark.json` : `main.cpr_l50` |
| Full graphs: S-PR | mean 2.657 s, SD 0.202 s; runs 2.997, 2.682, 2.512, 2.527, 2.565; peak 142.6 MB; iterations 153; \|V\| 1,298,724; \|E\| 2,580,709 | `benchmark/benchmark.json` : `main.spr` |
| AWP/EndorseRank runtime ratio (derived) | 27.90 | `benchmark/benchmark.json` : `main.awp.mean_s / main.endorserank.mean_s` |
| AWP/EndorseRank edge ratio (derived) | 22.44 | `benchmark/benchmark.json` : `main.awp.edges / main.endorserank.edges` |
| Damping 0.75: EndorseRank | mean 0.086 s, SD 0.005 s; runs 0.082, 0.088, 0.093, 0.085, 0.081; peak 13.7 MB; iterations 32; \|V\| 109,381; \|E\| 114,997 | `benchmark/benchmark.json` : `damping.0.75.endorserank` |
| Damping 0.75: AWP | mean 1.755 s, SD 0.232 s; runs 2.146, 1.687, 1.613, 1.562, 1.769; peak 228.2 MB; iterations 57; \|V\| 1,298,649; \|E\| 2,580,381 | `benchmark/benchmark.json` : `damping.0.75.awp` |
| Damping 0.85: EndorseRank | mean 0.101 s, SD 0.009 s; runs 0.101, 0.112, 0.096, 0.107, 0.089; peak 13.7 MB; iterations 56; \|V\| 109,381; \|E\| 114,997 | `benchmark/benchmark.json` : `damping.0.85.endorserank` |
| Damping 0.85: AWP | mean 2.821 s, SD 0.189 s; runs 2.964, 2.792, 2.852, 2.514, 2.984; peak 228.2 MB; iterations 98; \|V\| 1,298,649; \|E\| 2,580,381 | `benchmark/benchmark.json` : `damping.0.85.awp` |
| Damping 0.95: EndorseRank | mean 0.208 s, SD 0.028 s; runs 0.179, 0.233, 0.241, 0.204, 0.185; peak 13.7 MB; iterations 176; \|V\| 109,381; \|E\| 114,997 | `benchmark/benchmark.json` : `damping.0.95.endorserank` |
| Damping 0.95: AWP | mean 7.182 s, SD 0.348 s; runs 6.870, 6.961, 7.566, 7.555, 6.957; peak 228.2 MB; iterations 294; \|V\| 1,298,649; \|E\| 2,580,381 | `benchmark/benchmark.json` : `damping.0.95.awp` |
| Stage n=1,000: EndorseRank | mean 0.001 s, SD 3.488e-05 s; runs 0.001, 0.001, 0.001, 0.001, 0.001; peak 0.2 MB; iterations 48; \|V\| 1,293; \|E\| 1,608 | `benchmark/benchmark.json` : `scaling[0].endorserank` |
| Stage n=1,000: AWP | mean 0.095 s, SD 0.0004788 s; runs 0.096, 0.096, 0.095, 0.095, 0.095; peak 12.1 MB; iterations 94; \|V\| 78,869; \|E\| 120,252 | `benchmark/benchmark.json` : `scaling[0].awp` |
| Stage n=2,000: EndorseRank | mean 0.002 s, SD 8.498e-05 s; runs 0.002, 0.002, 0.002, 0.002, 0.002; peak 0.5 MB; iterations 26; \|V\| 3,972; \|E\| 4,784 | `benchmark/benchmark.json` : `scaling[1].endorserank` |
| Stage n=2,000: AWP | mean 0.134 s, SD 0.003 s; runs 0.135, 0.131, 0.132, 0.138, 0.132; peak 21.0 MB; iterations 90; \|V\| 129,533; \|E\| 235,864 | `benchmark/benchmark.json` : `scaling[1].awp` |
| Stage n=5,000: EndorseRank | mean 0.006 s, SD 0.0001205 s; runs 0.007, 0.006, 0.006, 0.006, 0.006; peak 1.1 MB; iterations 62; \|V\| 8,720; \|E\| 11,240 | `benchmark/benchmark.json` : `scaling[2].endorserank` |
| Stage n=5,000: AWP | mean 0.689 s, SD 0.031 s; runs 0.693, 0.735, 0.698, 0.657, 0.663; peak 75.0 MB; iterations 104; \|V\| 426,557; \|E\| 889,662 | `benchmark/benchmark.json` : `scaling[2].awp` |
| Stage n=6,443 (reused main measurement): EndorseRank | mean 0.101 s, SD 0.009 s; runs 0.101, 0.112, 0.096, 0.107, 0.089; peak 13.7 MB; iterations 56; \|V\| 109,381; \|E\| 114,997 | `benchmark/benchmark.json` : `scaling[3].endorserank` |
| Stage n=6,443 (reused main measurement): AWP | mean 2.821 s, SD 0.189 s; runs 2.964, 2.792, 2.852, 2.514, 2.984; peak 228.2 MB; iterations 98; \|V\| 1,298,649; \|E\| 2,580,381 | `benchmark/benchmark.json` : `scaling[3].awp` |

## 11. Discovery-order test (docs/discovery_protocol.md)

Defined after the registered results were known; it decides no rule of the plan or the registration. The decision is read at the T_obs freeze in the primary mode only (`decides` true); the other three runs carry no verdict. AUC is AUC_x of protocol section 6 with x = 10% unless a row says otherwise; contrasts read `point [95% interval]; share of resamples above 0`.


### Run tobs, mode both (the decision)

| Quantity | Value | Source |
|---|---|---|
| tobs, mode both (the decision): decides | yes | `discovery/discovery_tobs_both.json` : `decides` |
| tobs, mode both (the decision): is primary | yes | `discovery/discovery_tobs_both.json` : `is_primary` |
| tobs, mode both (the decision): primary mode | both | `discovery/discovery_tobs_both.json` : `primary_mode` |
| tobs, mode both (the decision): created at | 2026-11-10T15:46:54+00:00 | `discovery/discovery_tobs_both.json` : `created_at` |
| tobs, mode both (the decision): seconds | 29,948.3 | `discovery/discovery_tobs_both.json` : `seconds` |
| tobs, mode both (the decision): workers | 16 | `discovery/discovery_tobs_both.json` : `workers` |
| tobs, mode both (the decision): protocol rho | 1/50 | `discovery/discovery_tobs_both.json` : `protocol.rho` |
| tobs, mode both (the decision): protocol q | 1/100 | `discovery/discovery_tobs_both.json` : `protocol.q` |
| tobs, mode both (the decision): protocol q_secondary | 0.05 | `discovery/discovery_tobs_both.json` : `protocol.q_secondary` |
| tobs, mode both (the decision): protocol decision_covers | ['few_capped_allowance_in_edges'] | `discovery/discovery_tobs_both.json` : `protocol.decision_covers` |
| tobs, mode both (the decision): code revision | b840210f82c7ed6d0bbd60bd32a6406350084d7a | `discovery/discovery_tobs_both.json` : `provenance.head` |
| tobs, mode both (the decision): sizes of the graph, g_nodes | 1,403,959 | `discovery/discovery_tobs_both.json` : `sizes.graph.g_nodes` |
| tobs, mode both (the decision): sizes of the graph, allow_pairs | 115,006 | `discovery/discovery_tobs_both.json` : `sizes.graph.allow_pairs` |
| tobs, mode both (the decision): sizes of the graph, transfer_pairs | 2,580,709 | `discovery/discovery_tobs_both.json` : `sizes.graph.transfer_pairs` |
| tobs, mode both (the decision): sizes of the graph, nodes | 1,299,438 | `discovery/discovery_tobs_both.json` : `sizes.graph.nodes` |
| tobs, mode both (the decision): sizes of the graph, edges | 2,575,632 | `discovery/discovery_tobs_both.json` : `sizes.graph.edges` |
| tobs, mode both (the decision): sizes of the graph, scc | 265,804 | `discovery/discovery_tobs_both.json` : `sizes.graph.scc` |
| tobs, mode both (the decision): sizes of the graph, in | 174,239 | `discovery/discovery_tobs_both.json` : `sizes.graph.in` |
| tobs, mode both (the decision): sizes of the graph, out | 242,833 | `discovery/discovery_tobs_both.json` : `sizes.graph.out` |
| tobs, mode both (the decision): sizes of the graph, other | 616,562 | `discovery/discovery_tobs_both.json` : `sizes.graph.other` |
| tobs, mode both (the decision): sizes of the graph, U | 508,637 | `discovery/discovery_tobs_both.json` : `sizes.graph.U` |
| tobs, mode both (the decision): sizes of the graph, E_U | 1,546,906 | `discovery/discovery_tobs_both.json` : `sizes.graph.E_U` |
| tobs, mode both (the decision): sizes of the graph, WCC | 1,169,044 | `discovery/discovery_tobs_both.json` : `sizes.graph.WCC` |
| tobs, mode both (the decision): sizes of the graph, E_WCC | 2,378,418 | `discovery/discovery_tobs_both.json` : `sizes.graph.E_WCC` |
| tobs, mode both (the decision): sizes of the universe, U | 1,169,044 | `discovery/discovery_tobs_both.json` : `sizes.universe.U` |
| tobs, mode both (the decision): sizes of the universe, E_U | 2,378,418 | `discovery/discovery_tobs_both.json` : `sizes.universe.E_U` |
| tobs, mode both (the decision): sizes of the universe, allow_pairs | 16,776 | `discovery/discovery_tobs_both.json` : `sizes.universe.allow_pairs` |
| tobs, mode both (the decision): sizes of the universe, transfer_pairs | 2,383,503 | `discovery/discovery_tobs_both.json` : `sizes.universe.transfer_pairs` |
| tobs, mode both (the decision): contracts in H_q(I_T) | 13,141 | `discovery/discovery_tobs_both.json` : `hot_sets.i_t@q` |
| tobs, mode both (the decision): contracts in H_q(I_A) | 11,662 | `discovery/discovery_tobs_both.json` : `hot_sets.i_a@q` |
| tobs, mode both (the decision): contracts in H_q(N_T) | 25,729 | `discovery/discovery_tobs_both.json` : `hot_sets.n_t@q` |
| tobs, mode both (the decision): contracts in H_q(N_A) | 6,848 | `discovery/discovery_tobs_both.json` : `hot_sets.n_a@q` |
| tobs, mode both (the decision): contracts in H_q(IB_U) | 13,683 | `discovery/discovery_tobs_both.json` : `hot_sets.ib_u@q` |
| tobs, mode both (the decision): contracts in H_q(IR) | 11,691 | `discovery/discovery_tobs_both.json` : `hot_sets.ir@q` |
| tobs, mode both (the decision): contracts in H_q2(I_T) | 58,529 | `discovery/discovery_tobs_both.json` : `hot_sets.i_t@q2` |
| tobs, mode both (the decision): contracts in H_q(I_T) without hubs | 12,564 | `discovery/discovery_tobs_both.json` : `hot_sets.i_t@q-nohubs` |
| tobs, mode both (the decision): contracts in H_q2(I_A) | 11,662 | `discovery/discovery_tobs_both.json` : `hot_sets.i_a@q2` |
| tobs, mode both (the decision): contracts in H_q(I_A) without hubs | 11,498 | `discovery/discovery_tobs_both.json` : `hot_sets.i_a@q-nohubs` |
| tobs, mode both (the decision): D1 = C-PR′ − BFS on H_q(I_T) | +0.0520 [+0.0485, +0.0558]; share of resamples above 0 1.000 | `discovery/discovery_tobs_both.json` : `decision.i_t.D1` |
| tobs, mode both (the decision): D2 = C-PR′ − IB′_U on H_q(I_T) | -0.0051 [-0.0087, -0.0010]; share of resamples above 0 0.005 | `discovery/discovery_tobs_both.json` : `decision.i_t.D2` |
| tobs, mode both (the decision): verdict on I_T | V2 | `discovery/discovery_tobs_both.json` : `decision.i_t.verdict` |
| tobs, mode both (the decision): D1 = C-PR′ − BFS on H_q(I_A) | +0.0061 [+0.0014, +0.0111]; share of resamples above 0 0.998 | `discovery/discovery_tobs_both.json` : `decision.i_a.D1` |
| tobs, mode both (the decision): D2 = C-PR′ − IB′_U on H_q(I_A) | -0.0571 [-0.0621, -0.0519]; share of resamples above 0 0.000 | `discovery/discovery_tobs_both.json` : `decision.i_a.D2` |
| tobs, mode both (the decision): verdict on I_A | V2 | `discovery/discovery_tobs_both.json` : `decision.i_a.verdict` |
| tobs, mode both (the decision): statement 1 | Ordered by C-PR on the contracts read so far, a crawl from a random contract of the giant strongly connected component reached the contracts of the universe with the most user-account inflow and those with the most user-authorised value sooner than a breadth-first crawl, but not sooner than a crawl ordered by the number of contract backlinks. A crawl ordered by the number of contract backlinks reached them sooner. | `discovery/discovery_tobs_both.json` : `decision.statements[0]` |
| tobs, mode both (the decision): AUC of breadth-first on H_q(I_T) | 0.0565 [0.0543, 0.0586]; seeds 0.0004 to 0.1263 | `discovery/discovery_tobs_both.json` : `auc.i_t@q.bfs.x=0.1` |
| tobs, mode both (the decision): AUC of random on H_q(I_T) | 0.0609 [0.0593, 0.0627]; seeds 0.0090 to 0.0996 | `discovery/discovery_tobs_both.json` : `auc.i_t@q.random.x=0.1` |
| tobs, mode both (the decision): AUC of IB′_A (allowance backlinks) on H_q(I_T) | 0.0626 [0.0601, 0.0654]; seeds 0.0006 to 0.1161 | `discovery/discovery_tobs_both.json` : `auc.i_t@q.ib_a.x=0.1` |
| tobs, mode both (the decision): AUC of IB′_T (transfer backlinks) on H_q(I_T) | 0.1135 [0.1090, 0.1184]; seeds 0.0259 to 0.1500 | `discovery/discovery_tobs_both.json` : `auc.i_t@q.ib_t.x=0.1` |
| tobs, mode both (the decision): AUC of IB′_U (contract backlinks) on H_q(I_T) | 0.1136 [0.1091, 0.1184]; seeds 0.0260 to 0.1501 | `discovery/discovery_tobs_both.json` : `auc.i_t@q.ib_u.x=0.1` |
| tobs, mode both (the decision): AUC of EndorseRank′ on H_q(I_T) | 0.0621 [0.0595, 0.0648]; seeds 0.0006 to 0.1194 | `discovery/discovery_tobs_both.json` : `auc.i_t@q.endorserank.x=0.1` |
| tobs, mode both (the decision): AUC of EndorseRank-activity′ on H_q(I_T) | 0.0612 [0.0583, 0.0643]; seeds 0.0064 to 0.0989 | `discovery/discovery_tobs_both.json` : `auc.i_t@q.endorserank_activity.x=0.1` |
| tobs, mode both (the decision): AUC of AWP′ on H_q(I_T) | 0.1465 [0.1411, 0.1524]; seeds 0.1464 to 0.1465 | `discovery/discovery_tobs_both.json` : `auc.i_t@q.awp.x=0.1` |
| tobs, mode both (the decision): AUC of C-PR′ (λ=0.5) on H_q(I_T) | 0.1085 [0.1036, 0.1136]; seeds 0.1026 to 0.1125 | `discovery/discovery_tobs_both.json` : `auc.i_t@q.cpr_l50.x=0.1` |
| tobs, mode both (the decision): AUC of C-PR′ (λ=0.25) on H_q(I_T) | 0.1081 [0.1032, 0.1132]; seeds 0.1025 to 0.1118 | `discovery/discovery_tobs_both.json` : `auc.i_t@q.cpr_l25.x=0.1` |
| tobs, mode both (the decision): AUC of C-PR′ (λ=0.75) on H_q(I_T) | 0.1091 [0.1039, 0.1141]; seeds 0.1028 to 0.1133 | `discovery/discovery_tobs_both.json` : `auc.i_t@q.cpr_l75.x=0.1` |
| tobs, mode both (the decision): AUC of C-PR′ (λ=1) on H_q(I_T) | 0.0617 [0.0593, 0.0645]; seeds 0.0006 to 0.1167 | `discovery/discovery_tobs_both.json` : `auc.i_t@q.cpr_l100.x=0.1` |
| tobs, mode both (the decision): AUC of C-PR′ (λ=0) on H_q(I_T) | 0.1061 [0.1012, 0.1114]; seeds 0.1009 to 0.1096 | `discovery/discovery_tobs_both.json` : `auc.i_t@q.cpr_l0.x=0.1` |
| tobs, mode both (the decision): AUC of S-PR′ on H_q(I_T) | 0.1069 [0.1019, 0.1121]; seeds 0.1017 to 0.1103 | `discovery/discovery_tobs_both.json` : `auc.i_t@q.spr.x=0.1` |
| tobs, mode both (the decision): AUC of δ′ (diagnostic) on H_q(I_T) | 0.1643 [0.1587, 0.1708]; seeds 0.1642 to 0.1643 | `discovery/discovery_tobs_both.json` : `auc.i_t@q.delta.x=0.1` |
| tobs, mode both (the decision): AUC of reference: C-PR of the full graph on H_q(I_T) | 0.1061 [0.1015, 0.1115]; seeds 0.1061 to 0.1061 | `discovery/discovery_tobs_both.json` : `auc.i_t@q.ref_cpr.x=0.1` |
| tobs, mode both (the decision): AUC of reference: union in-degree of the full graph on H_q(I_T) | 0.1593 [0.1534, 0.1663]; seeds 0.1593 to 0.1593 | `discovery/discovery_tobs_both.json` : `auc.i_t@q.ref_ib_u.x=0.1` |
| tobs, mode both (the decision): AUC of reference: ideal order on H_q(I_T) | 0.9438 [0.9432, 0.9444]; seeds 0.9438 to 0.9438 | `discovery/discovery_tobs_both.json` : `auc.i_t@q.ref_ideal.x=0.1` |
| tobs, mode both (the decision): AUC of reference: random curve on H_q(I_T) | 0.0500 | `discovery/discovery_tobs_both.json` : `auc.i_t@q.random_curve.x=0.1` |
| tobs, mode both (the decision): AUC of reference: ideal curve on H_q(I_T) | 0.9438 | `discovery/discovery_tobs_both.json` : `auc.i_t@q.ideal_curve.x=0.1` |
| tobs, mode both (the decision): AUC of breadth-first on H_q(I_A) | 0.0882 [0.0859, 0.0900]; seeds 0.0005 to 0.2267 | `discovery/discovery_tobs_both.json` : `auc.i_a@q.bfs.x=0.1` |
| tobs, mode both (the decision): AUC of random on H_q(I_A) | 0.0725 [0.0710, 0.0742]; seeds 0.0111 to 0.1386 | `discovery/discovery_tobs_both.json` : `auc.i_a@q.random.x=0.1` |
| tobs, mode both (the decision): AUC of IB′_A (allowance backlinks) on H_q(I_A) | 0.0881 [0.0853, 0.0905]; seeds 0.0008 to 0.1626 | `discovery/discovery_tobs_both.json` : `auc.i_a@q.ib_a.x=0.1` |
| tobs, mode both (the decision): AUC of IB′_T (transfer backlinks) on H_q(I_A) | 0.1466 [0.1416, 0.1513]; seeds 0.0241 to 0.2109 | `discovery/discovery_tobs_both.json` : `auc.i_a@q.ib_t.x=0.1` |
| tobs, mode both (the decision): AUC of IB′_U (contract backlinks) on H_q(I_A) | 0.1514 [0.1462, 0.1562]; seeds 0.0251 to 0.2169 | `discovery/discovery_tobs_both.json` : `auc.i_a@q.ib_u.x=0.1` |
| tobs, mode both (the decision): AUC of EndorseRank′ on H_q(I_A) | 0.0869 [0.0841, 0.0893]; seeds 0.0008 to 0.1595 | `discovery/discovery_tobs_both.json` : `auc.i_a@q.endorserank.x=0.1` |
| tobs, mode both (the decision): AUC of EndorseRank-activity′ on H_q(I_A) | 0.1042 [0.1002, 0.1079]; seeds 0.0142 to 0.1584 | `discovery/discovery_tobs_both.json` : `auc.i_a@q.endorserank_activity.x=0.1` |
| tobs, mode both (the decision): AUC of AWP′ on H_q(I_A) | 0.1582 [0.1521, 0.1644]; seeds 0.1582 to 0.1582 | `discovery/discovery_tobs_both.json` : `auc.i_a@q.awp.x=0.1` |
| tobs, mode both (the decision): AUC of C-PR′ (λ=0.5) on H_q(I_A) | 0.0943 [0.0895, 0.0996]; seeds 0.0877 to 0.0987 | `discovery/discovery_tobs_both.json` : `auc.i_a@q.cpr_l50.x=0.1` |
| tobs, mode both (the decision): AUC of C-PR′ (λ=0.25) on H_q(I_A) | 0.0930 [0.0883, 0.0982]; seeds 0.0864 to 0.0974 | `discovery/discovery_tobs_both.json` : `auc.i_a@q.cpr_l25.x=0.1` |
| tobs, mode both (the decision): AUC of C-PR′ (λ=0.75) on H_q(I_A) | 0.0952 [0.0905, 0.1004]; seeds 0.0880 to 0.1000 | `discovery/discovery_tobs_both.json` : `auc.i_a@q.cpr_l75.x=0.1` |
| tobs, mode both (the decision): AUC of C-PR′ (λ=1) on H_q(I_A) | 0.0864 [0.0836, 0.0888]; seeds 0.0008 to 0.1584 | `discovery/discovery_tobs_both.json` : `auc.i_a@q.cpr_l100.x=0.1` |
| tobs, mode both (the decision): AUC of C-PR′ (λ=0) on H_q(I_A) | 0.0806 [0.0760, 0.0850]; seeds 0.0747 to 0.0846 | `discovery/discovery_tobs_both.json` : `auc.i_a@q.cpr_l0.x=0.1` |
| tobs, mode both (the decision): AUC of S-PR′ on H_q(I_A) | 0.0861 [0.0817, 0.0908]; seeds 0.0797 to 0.0903 | `discovery/discovery_tobs_both.json` : `auc.i_a@q.spr.x=0.1` |
| tobs, mode both (the decision): AUC of δ′ (diagnostic) on H_q(I_A) | 0.1942 [0.1874, 0.2012]; seeds 0.1942 to 0.1942 | `discovery/discovery_tobs_both.json` : `auc.i_a@q.delta.x=0.1` |
| tobs, mode both (the decision): AUC of reference: C-PR of the full graph on H_q(I_A) | 0.1157 [0.1105, 0.1210]; seeds 0.1157 to 0.1157 | `discovery/discovery_tobs_both.json` : `auc.i_a@q.ref_cpr.x=0.1` |
| tobs, mode both (the decision): AUC of reference: union in-degree of the full graph on H_q(I_A) | 0.1994 [0.1933, 0.2055]; seeds 0.1994 to 0.1994 | `discovery/discovery_tobs_both.json` : `auc.i_a@q.ref_ib_u.x=0.1` |
| tobs, mode both (the decision): AUC of reference: ideal order on H_q(I_A) | 0.9501 [0.9496, 0.9507]; seeds 0.9501 to 0.9501 | `discovery/discovery_tobs_both.json` : `auc.i_a@q.ref_ideal.x=0.1` |
| tobs, mode both (the decision): AUC of reference: random curve on H_q(I_A) | 0.0500 | `discovery/discovery_tobs_both.json` : `auc.i_a@q.random_curve.x=0.1` |
| tobs, mode both (the decision): AUC of reference: ideal curve on H_q(I_A) | 0.9501 | `discovery/discovery_tobs_both.json` : `auc.i_a@q.ideal_curve.x=0.1` |
| tobs, mode both (the decision): [1 walk′ against its count] EndorseRank′ − IB′_A (allowance backlinks) on H_q(I_T) | -0.0006 [-0.0007, -0.0004]; share of resamples above 0 0.000 | `discovery/discovery_tobs_both.json` : `fixed_order.1_walk_vs_count[0]` |
| tobs, mode both (the decision): [1 walk′ against its count] EndorseRank′ − IB′_A (allowance backlinks) on H_q(I_A) | -0.0012 [-0.0014, -0.0010]; share of resamples above 0 0.000 | `discovery/discovery_tobs_both.json` : `fixed_order.1_walk_vs_count[1]` |
| tobs, mode both (the decision): [1 walk′ against its count] EndorseRank-activity′ − IB′_A (allowance backlinks) on H_q(I_T) | -0.0014 [-0.0030, +0.0001]; share of resamples above 0 0.035 | `discovery/discovery_tobs_both.json` : `fixed_order.1_walk_vs_count[2]` |
| tobs, mode both (the decision): [1 walk′ against its count] EndorseRank-activity′ − IB′_A (allowance backlinks) on H_q(I_A) | +0.0161 [+0.0136, +0.0185]; share of resamples above 0 1.000 | `discovery/discovery_tobs_both.json` : `fixed_order.1_walk_vs_count[3]` |
| tobs, mode both (the decision): [1 walk′ against its count] C-PR′ (λ=1) − IB′_A (allowance backlinks) on H_q(I_T) | -0.0009 [-0.0010, -0.0007]; share of resamples above 0 0.000 | `discovery/discovery_tobs_both.json` : `fixed_order.1_walk_vs_count[4]` |
| tobs, mode both (the decision): [1 walk′ against its count] C-PR′ (λ=1) − IB′_A (allowance backlinks) on H_q(I_A) | -0.0017 [-0.0019, -0.0015]; share of resamples above 0 0.000 | `discovery/discovery_tobs_both.json` : `fixed_order.1_walk_vs_count[5]` |
| tobs, mode both (the decision): [1 walk′ against its count] AWP′ − IB′_T (transfer backlinks) on H_q(I_T) | +0.0329 [+0.0298, +0.0368]; share of resamples above 0 1.000 | `discovery/discovery_tobs_both.json` : `fixed_order.1_walk_vs_count[6]` |
| tobs, mode both (the decision): [1 walk′ against its count] AWP′ − IB′_T (transfer backlinks) on H_q(I_A) | +0.0116 [+0.0071, +0.0162]; share of resamples above 0 1.000 | `discovery/discovery_tobs_both.json` : `fixed_order.1_walk_vs_count[7]` |
| tobs, mode both (the decision): [1 walk′ against its count] C-PR′ (λ=0) − IB′_T (transfer backlinks) on H_q(I_T) | -0.0074 [-0.0109, -0.0031]; share of resamples above 0 0.000 | `discovery/discovery_tobs_both.json` : `fixed_order.1_walk_vs_count[8]` |
| tobs, mode both (the decision): [1 walk′ against its count] C-PR′ (λ=0) − IB′_T (transfer backlinks) on H_q(I_A) | -0.0660 [-0.0709, -0.0609]; share of resamples above 0 0.000 | `discovery/discovery_tobs_both.json` : `fixed_order.1_walk_vs_count[9]` |
| tobs, mode both (the decision): [1 walk′ against its count] C-PR′ (λ=0.5) − IB′_A (allowance backlinks) on H_q(I_T) | +0.0459 [+0.0427, +0.0492]; share of resamples above 0 1.000 | `discovery/discovery_tobs_both.json` : `fixed_order.1_walk_vs_count[10]` |
| tobs, mode both (the decision): [1 walk′ against its count] C-PR′ (λ=0.5) − IB′_A (allowance backlinks) on H_q(I_A) | +0.0062 [+0.0023, +0.0106]; share of resamples above 0 0.998 | `discovery/discovery_tobs_both.json` : `fixed_order.1_walk_vs_count[11]` |
| tobs, mode both (the decision): [1 walk′ against its count] C-PR′ (λ=0.5) − IB′_T (transfer backlinks) on H_q(I_T) | -0.0050 [-0.0086, -0.0008]; share of resamples above 0 0.005 | `discovery/discovery_tobs_both.json` : `fixed_order.1_walk_vs_count[12]` |
| tobs, mode both (the decision): [1 walk′ against its count] C-PR′ (λ=0.5) − IB′_T (transfer backlinks) on H_q(I_A) | -0.0523 [-0.0575, -0.0468]; share of resamples above 0 0.000 | `discovery/discovery_tobs_both.json` : `fixed_order.1_walk_vs_count[13]` |
| tobs, mode both (the decision): [2 among walks] C-PR′ (λ=0.5) − C-PR′ (λ=0) on H_q(I_T) | +0.0024 [+0.0016, +0.0033]; share of resamples above 0 1.000 | `discovery/discovery_tobs_both.json` : `fixed_order.2_walk_contrasts[0]` |
| tobs, mode both (the decision): [2 among walks] C-PR′ (λ=0.5) − C-PR′ (λ=0) on H_q(I_A) | +0.0137 [+0.0117, +0.0156]; share of resamples above 0 1.000 | `discovery/discovery_tobs_both.json` : `fixed_order.2_walk_contrasts[1]` |
| tobs, mode both (the decision): [2 among walks] C-PR′ (λ=0.5) − AWP′ on H_q(I_T) | -0.0379 [-0.0412, -0.0347]; share of resamples above 0 0.000 | `discovery/discovery_tobs_both.json` : `fixed_order.2_walk_contrasts[2]` |
| tobs, mode both (the decision): [2 among walks] C-PR′ (λ=0.5) − AWP′ on H_q(I_A) | -0.0639 [-0.0683, -0.0591]; share of resamples above 0 0.000 | `discovery/discovery_tobs_both.json` : `fixed_order.2_walk_contrasts[3]` |
| tobs, mode both (the decision): [2 among walks] C-PR′ (λ=0.5) − C-PR′ (λ=1) on H_q(I_T) | +0.0468 [+0.0436, +0.0501]; share of resamples above 0 1.000 | `discovery/discovery_tobs_both.json` : `fixed_order.2_walk_contrasts[4]` |
| tobs, mode both (the decision): [2 among walks] C-PR′ (λ=0.5) − C-PR′ (λ=1) on H_q(I_A) | +0.0078 [+0.0040, +0.0123]; share of resamples above 0 1.000 | `discovery/discovery_tobs_both.json` : `fixed_order.2_walk_contrasts[5]` |
| tobs, mode both (the decision): [2 among walks] C-PR′ (λ=0.5) − EndorseRank′ on H_q(I_T) | +0.0465 [+0.0433, +0.0498]; share of resamples above 0 1.000 | `discovery/discovery_tobs_both.json` : `fixed_order.2_walk_contrasts[6]` |
| tobs, mode both (the decision): [2 among walks] C-PR′ (λ=0.5) − EndorseRank′ on H_q(I_A) | +0.0074 [+0.0035, +0.0117]; share of resamples above 0 1.000 | `discovery/discovery_tobs_both.json` : `fixed_order.2_walk_contrasts[7]` |
| tobs, mode both (the decision): [2 among walks] S-PR′ − C-PR′ (λ=0) on H_q(I_T) | +0.0008 [+0.0006, +0.0011]; share of resamples above 0 1.000 | `discovery/discovery_tobs_both.json` : `fixed_order.2_walk_contrasts[8]` |
| tobs, mode both (the decision): [2 among walks] S-PR′ − C-PR′ (λ=0) on H_q(I_A) | +0.0054 [+0.0044, +0.0066]; share of resamples above 0 1.000 | `discovery/discovery_tobs_both.json` : `fixed_order.2_walk_contrasts[9]` |
| tobs, mode both (the decision): [3 λ] C-PR′ (λ=0.25) D1 on H_q(I_T) | +0.0515 [+0.0480, +0.0555]; share of resamples above 0 1.000 | `discovery/discovery_tobs_both.json` : `fixed_order.3_lambda.cpr_l25.i_t@q.D1` |
| tobs, mode both (the decision): [3 λ] C-PR′ (λ=0.25) D2 on H_q(I_T) | -0.0055 [-0.0091, -0.0016]; share of resamples above 0 0.003 | `discovery/discovery_tobs_both.json` : `fixed_order.3_lambda.cpr_l25.i_t@q.D2` |
| tobs, mode both (the decision): [3 λ] C-PR′ (λ=0.25) minus C-PR′ (λ=0.5) on H_q(I_T) | -0.0005 [-0.0008, -0.0001]; share of resamples above 0 0.010 | `discovery/discovery_tobs_both.json` : `fixed_order.3_lambda.cpr_l25.i_t@q.vs_cpr_l50` |
| tobs, mode both (the decision): [3 λ] C-PR′ (λ=0.25) D1 on H_q(I_A) | +0.0049 [+0.0002, +0.0100]; share of resamples above 0 0.988 | `discovery/discovery_tobs_both.json` : `fixed_order.3_lambda.cpr_l25.i_a@q.D1` |
| tobs, mode both (the decision): [3 λ] C-PR′ (λ=0.25) D2 on H_q(I_A) | -0.0584 [-0.0633, -0.0531]; share of resamples above 0 0.000 | `discovery/discovery_tobs_both.json` : `fixed_order.3_lambda.cpr_l25.i_a@q.D2` |
| tobs, mode both (the decision): [3 λ] C-PR′ (λ=0.25) minus C-PR′ (λ=0.5) on H_q(I_A) | -0.0012 [-0.0017, -0.0008]; share of resamples above 0 0.000 | `discovery/discovery_tobs_both.json` : `fixed_order.3_lambda.cpr_l25.i_a@q.vs_cpr_l50` |
| tobs, mode both (the decision): [3 λ] C-PR′ (λ=0.75) D1 on H_q(I_T) | +0.0526 [+0.0491, +0.0563]; share of resamples above 0 1.000 | `discovery/discovery_tobs_both.json` : `fixed_order.3_lambda.cpr_l75.i_t@q.D1` |
| tobs, mode both (the decision): [3 λ] C-PR′ (λ=0.75) D2 on H_q(I_T) | -0.0045 [-0.0080, -0.0005]; share of resamples above 0 0.013 | `discovery/discovery_tobs_both.json` : `fixed_order.3_lambda.cpr_l75.i_t@q.D2` |
| tobs, mode both (the decision): [3 λ] C-PR′ (λ=0.75) minus C-PR′ (λ=0.5) on H_q(I_T) | +0.0006 [+0.0002, +0.0010]; share of resamples above 0 1.000 | `discovery/discovery_tobs_both.json` : `fixed_order.3_lambda.cpr_l75.i_t@q.vs_cpr_l50` |
| tobs, mode both (the decision): [3 λ] C-PR′ (λ=0.75) D1 on H_q(I_A) | +0.0070 [+0.0024, +0.0121]; share of resamples above 0 1.000 | `discovery/discovery_tobs_both.json` : `fixed_order.3_lambda.cpr_l75.i_a@q.D1` |
| tobs, mode both (the decision): [3 λ] C-PR′ (λ=0.75) D2 on H_q(I_A) | -0.0562 [-0.0610, -0.0508]; share of resamples above 0 0.000 | `discovery/discovery_tobs_both.json` : `fixed_order.3_lambda.cpr_l75.i_a@q.D2` |
| tobs, mode both (the decision): [3 λ] C-PR′ (λ=0.75) minus C-PR′ (λ=0.5) on H_q(I_A) | +0.0009 [+0.0005, +0.0014]; share of resamples above 0 1.000 | `discovery/discovery_tobs_both.json` : `fixed_order.3_lambda.cpr_l75.i_a@q.vs_cpr_l50` |
| tobs, mode both (the decision): [4 Cho] D1 on H_q(IB_U) | +0.0176 [+0.0119, +0.0238]; share of resamples above 0 1.000 | `discovery/discovery_tobs_both.json` : `fixed_order.4_cho.hot_sets.ib_u@q.D1` |
| tobs, mode both (the decision): [4 Cho] D2 on H_q(IB_U) | -0.3031 [-0.3106, -0.2958]; share of resamples above 0 0.000 | `discovery/discovery_tobs_both.json` : `fixed_order.4_cho.hot_sets.ib_u@q.D2` |
| tobs, mode both (the decision): [4 Cho] D1 on H_q(IR) | +0.3084 [+0.3024, +0.3143]; share of resamples above 0 1.000 | `discovery/discovery_tobs_both.json` : `fixed_order.4_cho.hot_sets.ir@q.D1` |
| tobs, mode both (the decision): [4 Cho] D2 on H_q(IR) | +0.2606 [+0.2544, +0.2663]; share of resamples above 0 1.000 | `discovery/discovery_tobs_both.json` : `fixed_order.4_cho.hot_sets.ir@q.D2` |
| tobs, mode both (the decision): [4 Cho] replication contrast C-PR′ − IB′_U on H_q(IB_U) | -0.3031 [-0.3106, -0.2958]; share of resamples above 0 0.000 | `discovery/discovery_tobs_both.json` : `fixed_order.4_cho.replication_contrast` |
| tobs, mode both (the decision): [5 sensitivity x=0.05] D1 on H_q(I_T) | +0.0673 [+0.0635, +0.0714]; share of resamples above 0 1.000 | `discovery/discovery_tobs_both.json` : `fixed_order.5_sensitivities.x.x=0.05.i_t@q.D1` |
| tobs, mode both (the decision): [5 sensitivity x=0.05] D2 on H_q(I_T) | +0.0026 [-0.0010, +0.0064]; share of resamples above 0 0.922 | `discovery/discovery_tobs_both.json` : `fixed_order.5_sensitivities.x.x=0.05.i_t@q.D2` |
| tobs, mode both (the decision): [5 sensitivity x=0.05] D1 on H_q(I_A) | +0.0472 [+0.0429, +0.0521]; share of resamples above 0 1.000 | `discovery/discovery_tobs_both.json` : `fixed_order.5_sensitivities.x.x=0.05.i_a@q.D1` |
| tobs, mode both (the decision): [5 sensitivity x=0.05] D2 on H_q(I_A) | -0.0132 [-0.0178, -0.0084]; share of resamples above 0 0.000 | `discovery/discovery_tobs_both.json` : `fixed_order.5_sensitivities.x.x=0.05.i_a@q.D2` |
| tobs, mode both (the decision): [5 sensitivity x=0.2] D1 on H_q(I_T) | +0.0199 [+0.0169, +0.0230]; share of resamples above 0 1.000 | `discovery/discovery_tobs_both.json` : `fixed_order.5_sensitivities.x.x=0.2.i_t@q.D1` |
| tobs, mode both (the decision): [5 sensitivity x=0.2] D2 on H_q(I_T) | -0.0063 [-0.0091, -0.0034]; share of resamples above 0 0.000 | `discovery/discovery_tobs_both.json` : `fixed_order.5_sensitivities.x.x=0.2.i_t@q.D2` |
| tobs, mode both (the decision): [5 sensitivity x=0.2] D1 on H_q(I_A) | -0.0518 [-0.0575, -0.0460]; share of resamples above 0 0.000 | `discovery/discovery_tobs_both.json` : `fixed_order.5_sensitivities.x.x=0.2.i_a@q.D1` |
| tobs, mode both (the decision): [5 sensitivity x=0.2] D2 on H_q(I_A) | -0.0966 [-0.1023, -0.0905]; share of resamples above 0 0.000 | `discovery/discovery_tobs_both.json` : `fixed_order.5_sensitivities.x.x=0.2.i_a@q.D2` |
| tobs, mode both (the decision): [5 sensitivity secondary q] q | 0.050 | `discovery/discovery_tobs_both.json` : `fixed_order.5_sensitivities.q_secondary.q` |
| tobs, mode both (the decision): [5 sensitivity secondary q] D1 on H_q2(I_T) | +0.0132 [+0.0121, +0.0144]; share of resamples above 0 1.000 | `discovery/discovery_tobs_both.json` : `fixed_order.5_sensitivities.q_secondary.i_t@q2.D1` |
| tobs, mode both (the decision): [5 sensitivity secondary q] D2 on H_q2(I_T) | -0.0067 [-0.0078, -0.0057]; share of resamples above 0 0.000 | `discovery/discovery_tobs_both.json` : `fixed_order.5_sensitivities.q_secondary.i_t@q2.D2` |
| tobs, mode both (the decision): [5 sensitivity secondary q] D1 on H_q2(I_A) | +0.0061 [+0.0014, +0.0111]; share of resamples above 0 0.998 | `discovery/discovery_tobs_both.json` : `fixed_order.5_sensitivities.q_secondary.i_a@q2.D1` |
| tobs, mode both (the decision): [5 sensitivity secondary q] D2 on H_q2(I_A) | -0.0571 [-0.0621, -0.0519]; share of resamples above 0 0.000 | `discovery/discovery_tobs_both.json` : `fixed_order.5_sensitivities.q_secondary.i_a@q2.D2` |
| tobs, mode both (the decision): [5 sensitivity no hubs] hubs | 1,170 | `discovery/discovery_tobs_both.json` : `fixed_order.5_sensitivities.no_hubs.hubs` |
| tobs, mode both (the decision): [5 sensitivity no hubs] D1 on H_q(I_T) without hubs | +0.0306 [+0.0274, +0.0341]; share of resamples above 0 1.000 | `discovery/discovery_tobs_both.json` : `fixed_order.5_sensitivities.no_hubs.i_t@q-nohubs.D1` |
| tobs, mode both (the decision): [5 sensitivity no hubs] D2 on H_q(I_T) without hubs | -0.0126 [-0.0159, -0.0088]; share of resamples above 0 0.000 | `discovery/discovery_tobs_both.json` : `fixed_order.5_sensitivities.no_hubs.i_t@q-nohubs.D2` |
| tobs, mode both (the decision): [5 sensitivity no hubs] D1 on H_q(I_A) without hubs | -0.0019 [-0.0065, +0.0026]; share of resamples above 0 0.180 | `discovery/discovery_tobs_both.json` : `fixed_order.5_sensitivities.no_hubs.i_a@q-nohubs.D1` |
| tobs, mode both (the decision): [5 sensitivity no hubs] D2 on H_q(I_A) without hubs | -0.0607 [-0.0654, -0.0553]; share of resamples above 0 0.000 | `discovery/discovery_tobs_both.json` : `fixed_order.5_sensitivities.no_hubs.i_a@q-nohubs.D2` |
| tobs, mode both (the decision): [5 sensitivity importance by counts] D1 on H_q(N_T) | +0.0188 [+0.0163, +0.0211]; share of resamples above 0 1.000 | `discovery/discovery_tobs_both.json` : `fixed_order.5_sensitivities.importance_counts.n_t@q.D1` |
| tobs, mode both (the decision): [5 sensitivity importance by counts] D2 on H_q(N_T) | -0.0282 [-0.0308, -0.0254]; share of resamples above 0 0.000 | `discovery/discovery_tobs_both.json` : `fixed_order.5_sensitivities.importance_counts.n_t@q.D2` |
| tobs, mode both (the decision): [5 sensitivity importance by counts] D1 on H_q(N_A) | +0.0191 [+0.0129, +0.0262]; share of resamples above 0 1.000 | `discovery/discovery_tobs_both.json` : `fixed_order.5_sensitivities.importance_counts.n_a@q.D1` |
| tobs, mode both (the decision): [5 sensitivity importance by counts] D2 on H_q(N_A) | -0.0473 [-0.0537, -0.0408]; share of resamples above 0 0.000 | `discovery/discovery_tobs_both.json` : `fixed_order.5_sensitivities.importance_counts.n_a@q.D2` |
| tobs, mode both (the decision): [5 sensitivity seed bootstrap] D1 on H_q(I_T) | +0.0520 [+0.0320, +0.0717]; share of resamples above 0 1.000 | `discovery/discovery_tobs_both.json` : `fixed_order.5_sensitivities.seed_bootstrap.i_t@q.D1` |
| tobs, mode both (the decision): [5 sensitivity seed bootstrap] D2 on H_q(I_T) | -0.0051 [-0.0249, +0.0179]; share of resamples above 0 0.343 | `discovery/discovery_tobs_both.json` : `fixed_order.5_sensitivities.seed_bootstrap.i_t@q.D2` |
| tobs, mode both (the decision): [5 sensitivity seed bootstrap] D1 on H_q(I_A) | +0.0061 [-0.0315, +0.0398]; share of resamples above 0 0.620 | `discovery/discovery_tobs_both.json` : `fixed_order.5_sensitivities.seed_bootstrap.i_a@q.D1` |
| tobs, mode both (the decision): [5 sensitivity seed bootstrap] D2 on H_q(I_A) | -0.0571 [-0.0873, -0.0221]; share of resamples above 0 0.000 | `discovery/discovery_tobs_both.json` : `fixed_order.5_sensitivities.seed_bootstrap.i_a@q.D2` |
| tobs, mode both (the decision): [5 sensitivity ρ/4] ρ and seeds | 1/200, 5 seeds | `discovery/discovery_tobs_both.json` : `fixed_order.5_sensitivities.rho_quarter` |
| tobs, mode both (the decision): [5 sensitivity ρ/4] D1 on H_q(I_T) | +0.0381 [+0.0347, +0.0418]; share of resamples above 0 1.000 | `discovery/discovery_tobs_both.json` : `fixed_order.5_sensitivities.rho_quarter.contrasts.i_t@q.D1` |
| tobs, mode both (the decision): [5 sensitivity ρ/4] D2 on H_q(I_T) | -0.0129 [-0.0167, -0.0087]; share of resamples above 0 0.000 | `discovery/discovery_tobs_both.json` : `fixed_order.5_sensitivities.rho_quarter.contrasts.i_t@q.D2` |
| tobs, mode both (the decision): [5 sensitivity ρ/4] D1 on H_q(I_A) | -0.0134 [-0.0181, -0.0082]; share of resamples above 0 0.000 | `discovery/discovery_tobs_both.json` : `fixed_order.5_sensitivities.rho_quarter.contrasts.i_a@q.D1` |
| tobs, mode both (the decision): [5 sensitivity ρ/4] D2 on H_q(I_A) | -0.0713 [-0.0765, -0.0658]; share of resamples above 0 0.000 | `discovery/discovery_tobs_both.json` : `fixed_order.5_sensitivities.rho_quarter.contrasts.i_a@q.D2` |
| tobs, mode both (the decision): share of picks decided by a tie, breadth-first | 0.0000 | `discovery/discovery_tobs_both.json` : `diagnostics.ties.bfs` |
| tobs, mode both (the decision): share of picks decided by a tie, random | 0.0000 | `discovery/discovery_tobs_both.json` : `diagnostics.ties.random` |
| tobs, mode both (the decision): share of picks decided by a tie, IB′_A (allowance backlinks) | 0.9999 | `discovery/discovery_tobs_both.json` : `diagnostics.ties.ib_a` |
| tobs, mode both (the decision): share of picks decided by a tie, IB′_T (transfer backlinks) | 0.9998 | `discovery/discovery_tobs_both.json` : `diagnostics.ties.ib_t` |
| tobs, mode both (the decision): share of picks decided by a tie, IB′_U (contract backlinks) | 0.9998 | `discovery/discovery_tobs_both.json` : `diagnostics.ties.ib_u` |
| tobs, mode both (the decision): share of picks decided by a tie, EndorseRank′ | 0.9989 | `discovery/discovery_tobs_both.json` : `diagnostics.ties.endorserank` |
| tobs, mode both (the decision): share of picks decided by a tie, EndorseRank-activity′ | 0.9909 | `discovery/discovery_tobs_both.json` : `diagnostics.ties.endorserank_activity` |
| tobs, mode both (the decision): share of picks decided by a tie, AWP′ | 0.2518 | `discovery/discovery_tobs_both.json` : `diagnostics.ties.awp` |
| tobs, mode both (the decision): share of picks decided by a tie, C-PR′ (λ=0.5) | 0.5351 | `discovery/discovery_tobs_both.json` : `diagnostics.ties.cpr_l50` |
| tobs, mode both (the decision): share of picks decided by a tie, C-PR′ (λ=0.25) | 0.5336 | `discovery/discovery_tobs_both.json` : `diagnostics.ties.cpr_l25` |
| tobs, mode both (the decision): share of picks decided by a tie, C-PR′ (λ=0.75) | 0.5373 | `discovery/discovery_tobs_both.json` : `diagnostics.ties.cpr_l75` |
| tobs, mode both (the decision): share of picks decided by a tie, C-PR′ (λ=1) | 0.9996 | `discovery/discovery_tobs_both.json` : `diagnostics.ties.cpr_l100` |
| tobs, mode both (the decision): share of picks decided by a tie, C-PR′ (λ=0) | 0.5314 | `discovery/discovery_tobs_both.json` : `diagnostics.ties.cpr_l0` |
| tobs, mode both (the decision): share of picks decided by a tie, S-PR′ | 0.5306 | `discovery/discovery_tobs_both.json` : `diagnostics.ties.spr` |
| tobs, mode both (the decision): share of picks decided by a tie, δ′ (diagnostic) | 0.6344 | `discovery/discovery_tobs_both.json` : `diagnostics.ties.delta` |
| tobs, mode both (the decision): wasted visits of breadth-first (first 1%, first 10%) | 0.8907, 0.8446 | `discovery/discovery_tobs_both.json` : `diagnostics.wasted_visits.bfs` |
| tobs, mode both (the decision): wasted visits of random (first 1%, first 10%) | 0.8409, 0.6820 | `discovery/discovery_tobs_both.json` : `diagnostics.wasted_visits.random` |
| tobs, mode both (the decision): wasted visits of IB′_A (allowance backlinks) (first 1%, first 10%) | 0.8740, 0.8622 | `discovery/discovery_tobs_both.json` : `diagnostics.wasted_visits.ib_a` |
| tobs, mode both (the decision): wasted visits of IB′_T (transfer backlinks) (first 1%, first 10%) | 0.6780, 0.8877 | `discovery/discovery_tobs_both.json` : `diagnostics.wasted_visits.ib_t` |
| tobs, mode both (the decision): wasted visits of IB′_U (contract backlinks) (first 1%, first 10%) | 0.6745, 0.8881 | `discovery/discovery_tobs_both.json` : `diagnostics.wasted_visits.ib_u` |
| tobs, mode both (the decision): wasted visits of EndorseRank′ (first 1%, first 10%) | 0.8740, 0.8627 | `discovery/discovery_tobs_both.json` : `diagnostics.wasted_visits.endorserank` |
| tobs, mode both (the decision): wasted visits of EndorseRank-activity′ (first 1%, first 10%) | 0.6918, 0.8573 | `discovery/discovery_tobs_both.json` : `diagnostics.wasted_visits.endorserank_activity` |
| tobs, mode both (the decision): wasted visits of AWP′ (first 1%, first 10%) | 0.5224, 0.8348 | `discovery/discovery_tobs_both.json` : `diagnostics.wasted_visits.awp` |
| tobs, mode both (the decision): wasted visits of C-PR′ (λ=0.5) (first 1%, first 10%) | 0.7191, 0.9001 | `discovery/discovery_tobs_both.json` : `diagnostics.wasted_visits.cpr_l50` |
| tobs, mode both (the decision): wasted visits of C-PR′ (λ=0.25) (first 1%, first 10%) | 0.7268, 0.9079 | `discovery/discovery_tobs_both.json` : `diagnostics.wasted_visits.cpr_l25` |
| tobs, mode both (the decision): wasted visits of C-PR′ (λ=0.75) (first 1%, first 10%) | 0.7189, 0.8888 | `discovery/discovery_tobs_both.json` : `diagnostics.wasted_visits.cpr_l75` |
| tobs, mode both (the decision): wasted visits of C-PR′ (λ=1) (first 1%, first 10%) | 0.8740, 0.8627 | `discovery/discovery_tobs_both.json` : `diagnostics.wasted_visits.cpr_l100` |
| tobs, mode both (the decision): wasted visits of C-PR′ (λ=0) (first 1%, first 10%) | 0.7472, 0.9112 | `discovery/discovery_tobs_both.json` : `diagnostics.wasted_visits.cpr_l0` |
| tobs, mode both (the decision): wasted visits of S-PR′ (first 1%, first 10%) | 0.7429, 0.9104 | `discovery/discovery_tobs_both.json` : `diagnostics.wasted_visits.spr` |
| tobs, mode both (the decision): wasted visits of δ′ (diagnostic) (first 1%, first 10%) | 0.4965, 0.6495 | `discovery/discovery_tobs_both.json` : `diagnostics.wasted_visits.delta` |
| tobs, mode both (the decision): hubs | 1,170 | `discovery/discovery_tobs_both.json` : `diagnostics.hubs` |
| tobs, mode both (the decision): largest hub | 0x085b48ca6908dceafb4fae56c90709e1537ec9a7 with IB_U 441,612 | `discovery/discovery_tobs_both.json` : `diagnostics.hubs[0]` |
| tobs, mode both (the decision): median over hubs of the mean visit index, breadth-first | 73,218.6 | `discovery/discovery_tobs_both.json` : `diagnostics.hub_visits.bfs.mean` |
| tobs, mode both (the decision): median over hubs of the mean visit index, random | 272,806.2 | `discovery/discovery_tobs_both.json` : `diagnostics.hub_visits.random.mean` |
| tobs, mode both (the decision): median over hubs of the mean visit index, IB′_A (allowance backlinks) | 59,089.3 | `discovery/discovery_tobs_both.json` : `diagnostics.hub_visits.ib_a.mean` |
| tobs, mode both (the decision): median over hubs of the mean visit index, IB′_T (transfer backlinks) | 25,566.4 | `discovery/discovery_tobs_both.json` : `diagnostics.hub_visits.ib_t.mean` |
| tobs, mode both (the decision): median over hubs of the mean visit index, IB′_U (contract backlinks) | 25,565.1 | `discovery/discovery_tobs_both.json` : `diagnostics.hub_visits.ib_u.mean` |
| tobs, mode both (the decision): median over hubs of the mean visit index, EndorseRank′ | 60,493.8 | `discovery/discovery_tobs_both.json` : `diagnostics.hub_visits.endorserank.mean` |
| tobs, mode both (the decision): median over hubs of the mean visit index, EndorseRank-activity′ | 66,698.6 | `discovery/discovery_tobs_both.json` : `diagnostics.hub_visits.endorserank_activity.mean` |
| tobs, mode both (the decision): median over hubs of the mean visit index, AWP′ | 949.500 | `discovery/discovery_tobs_both.json` : `diagnostics.hub_visits.awp.mean` |
| tobs, mode both (the decision): median over hubs of the mean visit index, C-PR′ (λ=0.5) | 4,087.5 | `discovery/discovery_tobs_both.json` : `diagnostics.hub_visits.cpr_l50.mean` |
| tobs, mode both (the decision): median over hubs of the mean visit index, C-PR′ (λ=0.25) | 4,185.3 | `discovery/discovery_tobs_both.json` : `diagnostics.hub_visits.cpr_l25.mean` |
| tobs, mode both (the decision): median over hubs of the mean visit index, C-PR′ (λ=0.75) | 4,203.1 | `discovery/discovery_tobs_both.json` : `diagnostics.hub_visits.cpr_l75.mean` |
| tobs, mode both (the decision): median over hubs of the mean visit index, C-PR′ (λ=1) | 60,840.4 | `discovery/discovery_tobs_both.json` : `diagnostics.hub_visits.cpr_l100.mean` |
| tobs, mode both (the decision): median over hubs of the mean visit index, C-PR′ (λ=0) | 5,155.9 | `discovery/discovery_tobs_both.json` : `diagnostics.hub_visits.cpr_l0.mean` |
| tobs, mode both (the decision): median over hubs of the mean visit index, S-PR′ | 4,885.1 | `discovery/discovery_tobs_both.json` : `diagnostics.hub_visits.spr.mean` |
| tobs, mode both (the decision): median over hubs of the mean visit index, δ′ (diagnostic) | 1,403.7 | `discovery/discovery_tobs_both.json` : `diagnostics.hub_visits.delta.mean` |
| tobs, mode both (the decision): coverage, contracts | 809,296 | `discovery/discovery_tobs_both.json` : `diagnostics.coverage.contracts` |
| tobs, mode both (the decision): coverage, outside g | 112,210 | `discovery/discovery_tobs_both.json` : `diagnostics.coverage.outside_g` |
| tobs, mode both (the decision): coverage, inflow untyped usd | 1,681,953,612.2 | `discovery/discovery_tobs_both.json` : `diagnostics.coverage.inflow_untyped_usd` |
| tobs, mode both (the decision): coverage of I_T, total (USD) | 16,611,212,142.1 | `discovery/discovery_tobs_both.json` : `diagnostics.coverage.i_t.total` |
| tobs, mode both (the decision): coverage of I_T, share held by the universe | 0.9648 | `discovery/discovery_tobs_both.json` : `diagnostics.coverage.i_t.share_U` |
| tobs, mode both (the decision): coverage of I_T, share in scc | 0.7124 | `discovery/discovery_tobs_both.json` : `diagnostics.coverage.i_t.share_by_part.scc` |
| tobs, mode both (the decision): coverage of I_T, share in in | 0.0970 | `discovery/discovery_tobs_both.json` : `diagnostics.coverage.i_t.share_by_part.in` |
| tobs, mode both (the decision): coverage of I_T, share in out | 0.1007 | `discovery/discovery_tobs_both.json` : `diagnostics.coverage.i_t.share_by_part.out` |
| tobs, mode both (the decision): coverage of I_T, share in other | 0.0813 | `discovery/discovery_tobs_both.json` : `diagnostics.coverage.i_t.share_by_part.other` |
| tobs, mode both (the decision): coverage of I_T, share in isolated | 0.0042 | `discovery/discovery_tobs_both.json` : `diagnostics.coverage.i_t.share_by_part.isolated` |
| tobs, mode both (the decision): coverage of I_T, share in outside g | 0.0045 | `discovery/discovery_tobs_both.json` : `diagnostics.coverage.i_t.share_by_part.outside_g` |
| tobs, mode both (the decision): coverage of I_T, top 1% of rows: rows | 8,093 | `discovery/discovery_tobs_both.json` : `diagnostics.coverage.i_t.top_1pct.rows` |
| tobs, mode both (the decision): coverage of I_T, top 1% of rows: share in U | 0.6420 | `discovery/discovery_tobs_both.json` : `diagnostics.coverage.i_t.top_1pct.share_in_U` |
| tobs, mode both (the decision): coverage of I_T, top 1% of rows: tied at cut | 12,701 | `discovery/discovery_tobs_both.json` : `diagnostics.coverage.i_t.top_1pct.tied_at_cut` |
| tobs, mode both (the decision): coverage of I_T, top 1% of rows: slots at cut | 1,937 | `discovery/discovery_tobs_both.json` : `diagnostics.coverage.i_t.top_1pct.slots_at_cut` |
| tobs, mode both (the decision): coverage of I_A, total (USD) | 309,472,584.1 | `discovery/discovery_tobs_both.json` : `diagnostics.coverage.i_a.total` |
| tobs, mode both (the decision): coverage of I_A, share held by the universe | 0.9305 | `discovery/discovery_tobs_both.json` : `diagnostics.coverage.i_a.share_U` |
| tobs, mode both (the decision): coverage of I_A, share in scc | 0.5022 | `discovery/discovery_tobs_both.json` : `diagnostics.coverage.i_a.share_by_part.scc` |
| tobs, mode both (the decision): coverage of I_A, share in in | 0.0174 | `discovery/discovery_tobs_both.json` : `diagnostics.coverage.i_a.share_by_part.in` |
| tobs, mode both (the decision): coverage of I_A, share in out | 0.4036 | `discovery/discovery_tobs_both.json` : `diagnostics.coverage.i_a.share_by_part.out` |
| tobs, mode both (the decision): coverage of I_A, share in other | 0.0342 | `discovery/discovery_tobs_both.json` : `diagnostics.coverage.i_a.share_by_part.other` |
| tobs, mode both (the decision): coverage of I_A, share in isolated | 0.0361 | `discovery/discovery_tobs_both.json` : `diagnostics.coverage.i_a.share_by_part.isolated` |
| tobs, mode both (the decision): coverage of I_A, share in outside g | 0.0066 | `discovery/discovery_tobs_both.json` : `diagnostics.coverage.i_a.share_by_part.outside_g` |
| tobs, mode both (the decision): coverage of I_A, top 1% of rows: rows | 8,093 | `discovery/discovery_tobs_both.json` : `diagnostics.coverage.i_a.top_1pct.rows` |
| tobs, mode both (the decision): coverage of I_A, top 1% of rows: share in U | 0.3806 | `discovery/discovery_tobs_both.json` : `diagnostics.coverage.i_a.top_1pct.share_in_U` |
| tobs, mode both (the decision): coverage of I_A, top 1% of rows: tied at cut | 1 | `discovery/discovery_tobs_both.json` : `diagnostics.coverage.i_a.top_1pct.tied_at_cut` |
| tobs, mode both (the decision): coverage of I_A, top 1% of rows: slots at cut | 1 | `discovery/discovery_tobs_both.json` : `diagnostics.coverage.i_a.top_1pct.slots_at_cut` |
| tobs, mode both (the decision): crawls of bfs@1/200 | 5 crawls, 282.164 s, 1,856.8 recomputes, 0.000 solves, 0.000 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_both.json` : `runs.bfs@1/200` |
| tobs, mode both (the decision): crawls of bfs@1/50 | 20 crawls, 259.021 s, 539.450 recomputes, 0.000 solves, 0.000 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_both.json` : `runs.bfs@1/50` |
| tobs, mode both (the decision): crawls of random@1/200 | 5 crawls, 1,752.3 s, 1,169,043 recomputes, 0.000 solves, 0.000 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_both.json` : `runs.random@1/200` |
| tobs, mode both (the decision): crawls of random@1/50 | 20 crawls, 10,980.8 s, 1,169,043 recomputes, 0.000 solves, 0.000 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_both.json` : `runs.random@1/50` |
| tobs, mode both (the decision): crawls of ib_a@1/200 | 5 crawls, 1,487.8 s, 1,857 recomputes, 0.000 solves, 0.000 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_both.json` : `runs.ib_a@1/200` |
| tobs, mode both (the decision): crawls of ib_a@1/50 | 20 crawls, 1,356.7 s, 540.000 recomputes, 0.000 solves, 0.000 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_both.json` : `runs.ib_a@1/50` |
| tobs, mode both (the decision): crawls of ib_t@1/200 | 5 crawls, 662.766 s, 1,856.8 recomputes, 0.000 solves, 0.000 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_both.json` : `runs.ib_t@1/200` |
| tobs, mode both (the decision): crawls of ib_t@1/50 | 20 crawls, 728.758 s, 540.000 recomputes, 0.000 solves, 0.000 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_both.json` : `runs.ib_t@1/50` |
| tobs, mode both (the decision): crawls of ib_u@1/200 | 5 crawls, 529.878 s, 1,857 recomputes, 0.000 solves, 0.000 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_both.json` : `runs.ib_u@1/200` |
| tobs, mode both (the decision): crawls of ib_u@1/50 | 20 crawls, 830.363 s, 540.000 recomputes, 0.000 solves, 0.000 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_both.json` : `runs.ib_u@1/50` |
| tobs, mode both (the decision): crawls of endorserank@1/200 | 5 crawls, 4,813.3 s, 1,857 recomputes, 1,857 solves, 3,473.4 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_both.json` : `runs.endorserank@1/200` |
| tobs, mode both (the decision): crawls of endorserank@1/50 | 20 crawls, 4,969.3 s, 540.000 recomputes, 540.000 solves, 1,322.2 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_both.json` : `runs.endorserank@1/50` |
| tobs, mode both (the decision): crawls of endorserank_activity@1/200 | 5 crawls, 10,525.8 s, 1,857 recomputes, 1,857 solves, 36,315.6 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_both.json` : `runs.endorserank_activity@1/200` |
| tobs, mode both (the decision): crawls of endorserank_activity@1/50 | 20 crawls, 12,360.5 s, 540.000 recomputes, 540.000 solves, 13,805.2 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_both.json` : `runs.endorserank_activity@1/50` |
| tobs, mode both (the decision): crawls of awp@1/200 | 5 crawls, 64,002.5 s, 1,859 recomputes, 1,859 solves, 80,073 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_both.json` : `runs.awp@1/200` |
| tobs, mode both (the decision): crawls of awp@1/50 | 20 crawls, 65,884.7 s, 542.000 recomputes, 542.000 solves, 29,042.0 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_both.json` : `runs.awp@1/50` |
| tobs, mode both (the decision): crawls of cpr_l50@1/200 | 5 crawls, 22,461.0 s, 1,856.8 recomputes, 1,856.8 solves, 54,615.4 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_both.json` : `runs.cpr_l50@1/200` |
| tobs, mode both (the decision): crawls of cpr_l50@1/50 | 20 crawls, 31,258.3 s, 540.000 recomputes, 540.000 solves, 22,594.3 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_both.json` : `runs.cpr_l50@1/50` |
| tobs, mode both (the decision): crawls of cpr_l25@1/200 | 5 crawls, 24,329.7 s, 1,856.8 recomputes, 1,856.8 solves, 56,432.6 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_both.json` : `runs.cpr_l25@1/200` |
| tobs, mode both (the decision): crawls of cpr_l25@1/50 | 20 crawls, 32,515.9 s, 540.000 recomputes, 540.000 solves, 23,327.5 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_both.json` : `runs.cpr_l25@1/50` |
| tobs, mode both (the decision): crawls of cpr_l75@1/200 | 5 crawls, 26,690.2 s, 1,856.8 recomputes, 1,856.8 solves, 53,477.8 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_both.json` : `runs.cpr_l75@1/200` |
| tobs, mode both (the decision): crawls of cpr_l75@1/50 | 20 crawls, 34,389.6 s, 540.000 recomputes, 540.000 solves, 22,273.0 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_both.json` : `runs.cpr_l75@1/50` |
| tobs, mode both (the decision): crawls of cpr_l100@1/200 | 5 crawls, 3,868.3 s, 1,857 recomputes, 1,857 solves, 3,470.4 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_both.json` : `runs.cpr_l100@1/200` |
| tobs, mode both (the decision): crawls of cpr_l100@1/50 | 20 crawls, 3,843.8 s, 540.000 recomputes, 540.000 solves, 1,316.8 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_both.json` : `runs.cpr_l100@1/50` |
| tobs, mode both (the decision): crawls of cpr_l0@1/200 | 5 crawls, 19,403.2 s, 1,857 recomputes, 1,857 solves, 59,120.6 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_both.json` : `runs.cpr_l0@1/200` |
| tobs, mode both (the decision): crawls of cpr_l0@1/50 | 20 crawls, 27,002.1 s, 540.000 recomputes, 540.000 solves, 24,303.0 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_both.json` : `runs.cpr_l0@1/50` |
| tobs, mode both (the decision): crawls of spr@1/200 | 5 crawls, 23,553.2 s, 1,856.8 recomputes, 3,713.6 solves, 63,760.6 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_both.json` : `runs.spr@1/200` |
| tobs, mode both (the decision): crawls of spr@1/50 | 20 crawls, 29,965.9 s, 540.000 recomputes, 1,080 solves, 26,023.5 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_both.json` : `runs.spr@1/50` |
| tobs, mode both (the decision): crawls of delta@1/200 | 5 crawls, 612.185 s, 1,856.8 recomputes, 0.000 solves, 0.000 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_both.json` : `runs.delta@1/200` |
| tobs, mode both (the decision): crawls of delta@1/50 | 20 crawls, 697.562 s, 540.000 recomputes, 0.000 solves, 0.000 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_both.json` : `runs.delta@1/50` |
| tobs, mode both (the decision): invariant all visited | yes | `discovery/discovery_tobs_both.json` : `invariants.all_visited` |
| tobs, mode both (the decision): invariant final walks within | 1e-09 | `discovery/discovery_tobs_both.json` : `invariants.final_walks_within` |
| tobs, mode both (the decision): invariant max final diff | 2.43e-16 | `discovery/discovery_tobs_both.json` : `invariants.max_final_diff` |

### Run tobs, mode out

| Quantity | Value | Source |
|---|---|---|
| tobs, mode out: decides | no | `discovery/discovery_tobs_out.json` : `decides` |
| tobs, mode out: is primary | no | `discovery/discovery_tobs_out.json` : `is_primary` |
| tobs, mode out: primary mode | both | `discovery/discovery_tobs_out.json` : `primary_mode` |
| tobs, mode out: created at | 2026-11-10T17:54:54+00:00 | `discovery/discovery_tobs_out.json` : `created_at` |
| tobs, mode out: seconds | 7,646.1 | `discovery/discovery_tobs_out.json` : `seconds` |
| tobs, mode out: workers | 16 | `discovery/discovery_tobs_out.json` : `workers` |
| tobs, mode out: protocol rho | 1/50 | `discovery/discovery_tobs_out.json` : `protocol.rho` |
| tobs, mode out: protocol q | 1/100 | `discovery/discovery_tobs_out.json` : `protocol.q` |
| tobs, mode out: protocol q_secondary | 0.05 | `discovery/discovery_tobs_out.json` : `protocol.q_secondary` |
| tobs, mode out: protocol decision_covers | ['few_capped_allowance_in_edges'] | `discovery/discovery_tobs_out.json` : `protocol.decision_covers` |
| tobs, mode out: code revision | b840210f82c7ed6d0bbd60bd32a6406350084d7a | `discovery/discovery_tobs_out.json` : `provenance.head` |
| tobs, mode out: sizes of the graph, g_nodes | 1,403,959 | `discovery/discovery_tobs_out.json` : `sizes.graph.g_nodes` |
| tobs, mode out: sizes of the graph, allow_pairs | 115,006 | `discovery/discovery_tobs_out.json` : `sizes.graph.allow_pairs` |
| tobs, mode out: sizes of the graph, transfer_pairs | 2,580,709 | `discovery/discovery_tobs_out.json` : `sizes.graph.transfer_pairs` |
| tobs, mode out: sizes of the graph, nodes | 1,299,438 | `discovery/discovery_tobs_out.json` : `sizes.graph.nodes` |
| tobs, mode out: sizes of the graph, edges | 2,575,632 | `discovery/discovery_tobs_out.json` : `sizes.graph.edges` |
| tobs, mode out: sizes of the graph, scc | 265,804 | `discovery/discovery_tobs_out.json` : `sizes.graph.scc` |
| tobs, mode out: sizes of the graph, in | 174,239 | `discovery/discovery_tobs_out.json` : `sizes.graph.in` |
| tobs, mode out: sizes of the graph, out | 242,833 | `discovery/discovery_tobs_out.json` : `sizes.graph.out` |
| tobs, mode out: sizes of the graph, other | 616,562 | `discovery/discovery_tobs_out.json` : `sizes.graph.other` |
| tobs, mode out: sizes of the graph, U | 508,637 | `discovery/discovery_tobs_out.json` : `sizes.graph.U` |
| tobs, mode out: sizes of the graph, E_U | 1,546,906 | `discovery/discovery_tobs_out.json` : `sizes.graph.E_U` |
| tobs, mode out: sizes of the graph, WCC | 1,169,044 | `discovery/discovery_tobs_out.json` : `sizes.graph.WCC` |
| tobs, mode out: sizes of the graph, E_WCC | 2,378,418 | `discovery/discovery_tobs_out.json` : `sizes.graph.E_WCC` |
| tobs, mode out: sizes of the universe, U | 508,637 | `discovery/discovery_tobs_out.json` : `sizes.universe.U` |
| tobs, mode out: sizes of the universe, E_U | 1,546,906 | `discovery/discovery_tobs_out.json` : `sizes.universe.E_U` |
| tobs, mode out: sizes of the universe, allow_pairs | 13,540 | `discovery/discovery_tobs_out.json` : `sizes.universe.allow_pairs` |
| tobs, mode out: sizes of the universe, transfer_pairs | 1,553,499 | `discovery/discovery_tobs_out.json` : `sizes.universe.transfer_pairs` |
| tobs, mode out: contracts in H_q(I_T) | 5,087 | `discovery/discovery_tobs_out.json` : `hot_sets.i_t@q` |
| tobs, mode out: contracts in H_q(I_A) | 5,088 | `discovery/discovery_tobs_out.json` : `hot_sets.i_a@q` |
| tobs, mode out: contracts in H_q(N_T) | 7,928 | `discovery/discovery_tobs_out.json` : `hot_sets.n_t@q` |
| tobs, mode out: contracts in H_q(N_A) | 4,471 | `discovery/discovery_tobs_out.json` : `hot_sets.n_a@q` |
| tobs, mode out: contracts in H_q(IB_U) | 5,402 | `discovery/discovery_tobs_out.json` : `hot_sets.ib_u@q` |
| tobs, mode out: contracts in H_q(IR) | 5,087 | `discovery/discovery_tobs_out.json` : `hot_sets.ir@q` |
| tobs, mode out: contracts in H_q2(I_T) | 25,432 | `discovery/discovery_tobs_out.json` : `hot_sets.i_t@q2` |
| tobs, mode out: contracts in H_q(I_T) without hubs | 4,733 | `discovery/discovery_tobs_out.json` : `hot_sets.i_t@q-nohubs` |
| tobs, mode out: contracts in H_q2(I_A) | 7,192 | `discovery/discovery_tobs_out.json` : `hot_sets.i_a@q2` |
| tobs, mode out: contracts in H_q(I_A) without hubs | 5,009 | `discovery/discovery_tobs_out.json` : `hot_sets.i_a@q-nohubs` |
| tobs, mode out: D1 = C-PR′ − BFS on H_q(I_T) | +0.2650 [+0.2540, +0.2743]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `decision.i_t.D1` |
| tobs, mode out: D2 = C-PR′ − IB′_U on H_q(I_T) | +0.0803 [+0.0690, +0.0920]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `decision.i_t.D2` |
| tobs, mode out: contrasts on I_T with the interval above 0 | D1, D2 | `discovery/discovery_tobs_out.json` : `decision.i_t.above_zero` |
| tobs, mode out: contrasts on I_T with the interval below 0 | none | `discovery/discovery_tobs_out.json` : `decision.i_t.below_zero` |
| tobs, mode out: D1 = C-PR′ − BFS on H_q(I_A) | +0.1143 [+0.1053, +0.1237]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `decision.i_a.D1` |
| tobs, mode out: D2 = C-PR′ − IB′_U on H_q(I_A) | +0.0436 [+0.0347, +0.0522]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `decision.i_a.D2` |
| tobs, mode out: contrasts on I_A with the interval above 0 | D1, D2 | `discovery/discovery_tobs_out.json` : `decision.i_a.above_zero` |
| tobs, mode out: contrasts on I_A with the interval below 0 | none | `discovery/discovery_tobs_out.json` : `decision.i_a.below_zero` |
| tobs, mode out: AUC of breadth-first on H_q(I_T) | 0.1179 [0.1139, 0.1219]; seeds 0.0004 to 0.3937 | `discovery/discovery_tobs_out.json` : `auc.i_t@q.bfs.x=0.1` |
| tobs, mode out: AUC of random on H_q(I_T) | 0.1085 [0.1054, 0.1114]; seeds 0.0010 to 0.2006 | `discovery/discovery_tobs_out.json` : `auc.i_t@q.random.x=0.1` |
| tobs, mode out: AUC of IB′_A (allowance backlinks) on H_q(I_T) | 0.1438 [0.1384, 0.1490]; seeds 0.0009 to 0.3846 | `discovery/discovery_tobs_out.json` : `auc.i_t@q.ib_a.x=0.1` |
| tobs, mode out: AUC of IB′_T (transfer backlinks) on H_q(I_T) | 0.3023 [0.2931, 0.3120]; seeds 0.0031 to 0.4310 | `discovery/discovery_tobs_out.json` : `auc.i_t@q.ib_t.x=0.1` |
| tobs, mode out: AUC of IB′_U (contract backlinks) on H_q(I_T) | 0.3026 [0.2938, 0.3124]; seeds 0.0031 to 0.4313 | `discovery/discovery_tobs_out.json` : `auc.i_t@q.ib_u.x=0.1` |
| tobs, mode out: AUC of EndorseRank′ on H_q(I_T) | 0.1404 [0.1351, 0.1456]; seeds 0.0009 to 0.3880 | `discovery/discovery_tobs_out.json` : `auc.i_t@q.endorserank.x=0.1` |
| tobs, mode out: AUC of EndorseRank-activity′ on H_q(I_T) | 0.1404 [0.1351, 0.1457]; seeds 0.0009 to 0.3880 | `discovery/discovery_tobs_out.json` : `auc.i_t@q.endorserank_activity.x=0.1` |
| tobs, mode out: AUC of AWP′ on H_q(I_T) | 0.4446 [0.4320, 0.4562]; seeds 0.4445 to 0.4447 | `discovery/discovery_tobs_out.json` : `auc.i_t@q.awp.x=0.1` |
| tobs, mode out: AUC of C-PR′ (λ=0.5) on H_q(I_T) | 0.3829 [0.3705, 0.3938]; seeds 0.3124 to 0.4241 | `discovery/discovery_tobs_out.json` : `auc.i_t@q.cpr_l50.x=0.1` |
| tobs, mode out: AUC of C-PR′ (λ=0.25) on H_q(I_T) | 0.4129 [0.4012, 0.4243]; seeds 0.3717 to 0.4267 | `discovery/discovery_tobs_out.json` : `auc.i_t@q.cpr_l25.x=0.1` |
| tobs, mode out: AUC of C-PR′ (λ=0.75) on H_q(I_T) | 0.3744 [0.3612, 0.3854]; seeds 0.3030 to 0.4186 | `discovery/discovery_tobs_out.json` : `auc.i_t@q.cpr_l75.x=0.1` |
| tobs, mode out: AUC of C-PR′ (λ=1) on H_q(I_T) | 0.1398 [0.1347, 0.1449]; seeds 0.0009 to 0.3848 | `discovery/discovery_tobs_out.json` : `auc.i_t@q.cpr_l100.x=0.1` |
| tobs, mode out: AUC of C-PR′ (λ=0) on H_q(I_T) | 0.4133 [0.4021, 0.4246]; seeds 0.3978 to 0.4186 | `discovery/discovery_tobs_out.json` : `auc.i_t@q.cpr_l0.x=0.1` |
| tobs, mode out: AUC of S-PR′ on H_q(I_T) | 0.4190 [0.4075, 0.4302]; seeds 0.4078 to 0.4230 | `discovery/discovery_tobs_out.json` : `auc.i_t@q.spr.x=0.1` |
| tobs, mode out: AUC of δ′ (diagnostic) on H_q(I_T) | 0.5357 [0.5251, 0.5469]; seeds 0.5353 to 0.5361 | `discovery/discovery_tobs_out.json` : `auc.i_t@q.delta.x=0.1` |
| tobs, mode out: AUC of reference: C-PR of the full graph on H_q(I_T) | 0.2449 [0.2338, 0.2555]; seeds 0.2449 to 0.2449 | `discovery/discovery_tobs_out.json` : `auc.i_t@q.ref_cpr.x=0.1` |
| tobs, mode out: AUC of reference: union in-degree of the full graph on H_q(I_T) | 0.4600 [0.4467, 0.4727]; seeds 0.4600 to 0.4600 | `discovery/discovery_tobs_out.json` : `auc.i_t@q.ref_ib_u.x=0.1` |
| tobs, mode out: AUC of reference: ideal order on H_q(I_T) | 0.9500 [0.9492, 0.9508]; seeds 0.9500 to 0.9500 | `discovery/discovery_tobs_out.json` : `auc.i_t@q.ref_ideal.x=0.1` |
| tobs, mode out: AUC of reference: random curve on H_q(I_T) | 0.0500 | `discovery/discovery_tobs_out.json` : `auc.i_t@q.random_curve.x=0.1` |
| tobs, mode out: AUC of reference: ideal curve on H_q(I_T) | 0.9500 | `discovery/discovery_tobs_out.json` : `auc.i_t@q.ideal_curve.x=0.1` |
| tobs, mode out: AUC of breadth-first on H_q(I_A) | 0.0595 [0.0573, 0.0616]; seeds 0.0002 to 0.2957 | `discovery/discovery_tobs_out.json` : `auc.i_a@q.bfs.x=0.1` |
| tobs, mode out: AUC of random on H_q(I_A) | 0.0621 [0.0599, 0.0640]; seeds 0.0002 to 0.1324 | `discovery/discovery_tobs_out.json` : `auc.i_a@q.random.x=0.1` |
| tobs, mode out: AUC of IB′_A (allowance backlinks) on H_q(I_A) | 0.0818 [0.0778, 0.0852]; seeds 0.0005 to 0.2588 | `discovery/discovery_tobs_out.json` : `auc.i_a@q.ib_a.x=0.1` |
| tobs, mode out: AUC of IB′_T (transfer backlinks) on H_q(I_A) | 0.1233 [0.1156, 0.1293]; seeds 0.0003 to 0.1790 | `discovery/discovery_tobs_out.json` : `auc.i_a@q.ib_t.x=0.1` |
| tobs, mode out: AUC of IB′_U (contract backlinks) on H_q(I_A) | 0.1302 [0.1224, 0.1363]; seeds 0.0007 to 0.1884 | `discovery/discovery_tobs_out.json` : `auc.i_a@q.ib_u.x=0.1` |
| tobs, mode out: AUC of EndorseRank′ on H_q(I_A) | 0.0802 [0.0762, 0.0836]; seeds 0.0005 to 0.2603 | `discovery/discovery_tobs_out.json` : `auc.i_a@q.endorserank.x=0.1` |
| tobs, mode out: AUC of EndorseRank-activity′ on H_q(I_A) | 0.0802 [0.0763, 0.0836]; seeds 0.0005 to 0.2603 | `discovery/discovery_tobs_out.json` : `auc.i_a@q.endorserank_activity.x=0.1` |
| tobs, mode out: AUC of AWP′ on H_q(I_A) | 0.1753 [0.1654, 0.1845]; seeds 0.1753 to 0.1754 | `discovery/discovery_tobs_out.json` : `auc.i_a@q.awp.x=0.1` |
| tobs, mode out: AUC of C-PR′ (λ=0.5) on H_q(I_A) | 0.1738 [0.1633, 0.1830]; seeds 0.1456 to 0.1902 | `discovery/discovery_tobs_out.json` : `auc.i_a@q.cpr_l50.x=0.1` |
| tobs, mode out: AUC of C-PR′ (λ=0.25) on H_q(I_A) | 0.1835 [0.1735, 0.1928]; seeds 0.1607 to 0.1915 | `discovery/discovery_tobs_out.json` : `auc.i_a@q.cpr_l25.x=0.1` |
| tobs, mode out: AUC of C-PR′ (λ=0.75) on H_q(I_A) | 0.1608 [0.1507, 0.1703]; seeds 0.1437 to 0.1703 | `discovery/discovery_tobs_out.json` : `auc.i_a@q.cpr_l75.x=0.1` |
| tobs, mode out: AUC of C-PR′ (λ=1) on H_q(I_A) | 0.0789 [0.0750, 0.0823]; seeds 0.0005 to 0.2586 | `discovery/discovery_tobs_out.json` : `auc.i_a@q.cpr_l100.x=0.1` |
| tobs, mode out: AUC of C-PR′ (λ=0) on H_q(I_A) | 0.1584 [0.1494, 0.1674]; seeds 0.1419 to 0.1641 | `discovery/discovery_tobs_out.json` : `auc.i_a@q.cpr_l0.x=0.1` |
| tobs, mode out: AUC of S-PR′ on H_q(I_A) | 0.1805 [0.1704, 0.1898]; seeds 0.1650 to 0.1858 | `discovery/discovery_tobs_out.json` : `auc.i_a@q.spr.x=0.1` |
| tobs, mode out: AUC of δ′ (diagnostic) on H_q(I_A) | 0.2317 [0.2204, 0.2416]; seeds 0.2316 to 0.2318 | `discovery/discovery_tobs_out.json` : `auc.i_a@q.delta.x=0.1` |
| tobs, mode out: AUC of reference: C-PR of the full graph on H_q(I_A) | 0.1279 [0.1190, 0.1354]; seeds 0.1279 to 0.1279 | `discovery/discovery_tobs_out.json` : `auc.i_a@q.ref_cpr.x=0.1` |
| tobs, mode out: AUC of reference: union in-degree of the full graph on H_q(I_A) | 0.2142 [0.2040, 0.2241]; seeds 0.2142 to 0.2142 | `discovery/discovery_tobs_out.json` : `auc.i_a@q.ref_ib_u.x=0.1` |
| tobs, mode out: AUC of reference: ideal order on H_q(I_A) | 0.9500 [0.9492, 0.9507]; seeds 0.9500 to 0.9500 | `discovery/discovery_tobs_out.json` : `auc.i_a@q.ref_ideal.x=0.1` |
| tobs, mode out: AUC of reference: random curve on H_q(I_A) | 0.0500 | `discovery/discovery_tobs_out.json` : `auc.i_a@q.random_curve.x=0.1` |
| tobs, mode out: AUC of reference: ideal curve on H_q(I_A) | 0.9500 | `discovery/discovery_tobs_out.json` : `auc.i_a@q.ideal_curve.x=0.1` |
| tobs, mode out: [1 walk′ against its count] EndorseRank′ − IB′_A (allowance backlinks) on H_q(I_T) | -0.0033 [-0.0038, -0.0029]; share of resamples above 0 0.000 | `discovery/discovery_tobs_out.json` : `fixed_order.1_walk_vs_count[0]` |
| tobs, mode out: [1 walk′ against its count] EndorseRank′ − IB′_A (allowance backlinks) on H_q(I_A) | -0.0016 [-0.0019, -0.0013]; share of resamples above 0 0.000 | `discovery/discovery_tobs_out.json` : `fixed_order.1_walk_vs_count[1]` |
| tobs, mode out: [1 walk′ against its count] EndorseRank-activity′ − IB′_A (allowance backlinks) on H_q(I_T) | -0.0033 [-0.0038, -0.0029]; share of resamples above 0 0.000 | `discovery/discovery_tobs_out.json` : `fixed_order.1_walk_vs_count[2]` |
| tobs, mode out: [1 walk′ against its count] EndorseRank-activity′ − IB′_A (allowance backlinks) on H_q(I_A) | -0.0016 [-0.0019, -0.0012]; share of resamples above 0 0.000 | `discovery/discovery_tobs_out.json` : `fixed_order.1_walk_vs_count[3]` |
| tobs, mode out: [1 walk′ against its count] C-PR′ (λ=1) − IB′_A (allowance backlinks) on H_q(I_T) | -0.0040 [-0.0044, -0.0036]; share of resamples above 0 0.000 | `discovery/discovery_tobs_out.json` : `fixed_order.1_walk_vs_count[4]` |
| tobs, mode out: [1 walk′ against its count] C-PR′ (λ=1) − IB′_A (allowance backlinks) on H_q(I_A) | -0.0029 [-0.0032, -0.0026]; share of resamples above 0 0.000 | `discovery/discovery_tobs_out.json` : `fixed_order.1_walk_vs_count[5]` |
| tobs, mode out: [1 walk′ against its count] AWP′ − IB′_T (transfer backlinks) on H_q(I_T) | +0.1423 [+0.1289, +0.1543]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.1_walk_vs_count[6]` |
| tobs, mode out: [1 walk′ against its count] AWP′ − IB′_T (transfer backlinks) on H_q(I_A) | +0.0520 [+0.0424, +0.0611]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.1_walk_vs_count[7]` |
| tobs, mode out: [1 walk′ against its count] C-PR′ (λ=0) − IB′_T (transfer backlinks) on H_q(I_T) | +0.1110 [+0.0992, +0.1229]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.1_walk_vs_count[8]` |
| tobs, mode out: [1 walk′ against its count] C-PR′ (λ=0) − IB′_T (transfer backlinks) on H_q(I_A) | +0.0351 [+0.0258, +0.0431]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.1_walk_vs_count[9]` |
| tobs, mode out: [1 walk′ against its count] C-PR′ (λ=0.5) − IB′_A (allowance backlinks) on H_q(I_T) | +0.2391 [+0.2283, +0.2486]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.1_walk_vs_count[10]` |
| tobs, mode out: [1 walk′ against its count] C-PR′ (λ=0.5) − IB′_A (allowance backlinks) on H_q(I_A) | +0.0920 [+0.0837, +0.1003]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.1_walk_vs_count[11]` |
| tobs, mode out: [1 walk′ against its count] C-PR′ (λ=0.5) − IB′_T (transfer backlinks) on H_q(I_T) | +0.0806 [+0.0692, +0.0922]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.1_walk_vs_count[12]` |
| tobs, mode out: [1 walk′ against its count] C-PR′ (λ=0.5) − IB′_T (transfer backlinks) on H_q(I_A) | +0.0504 [+0.0408, +0.0596]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.1_walk_vs_count[13]` |
| tobs, mode out: [2 among walks] C-PR′ (λ=0.5) − C-PR′ (λ=0) on H_q(I_T) | -0.0305 [-0.0343, -0.0264]; share of resamples above 0 0.000 | `discovery/discovery_tobs_out.json` : `fixed_order.2_walk_contrasts[0]` |
| tobs, mode out: [2 among walks] C-PR′ (λ=0.5) − C-PR′ (λ=0) on H_q(I_A) | +0.0153 [+0.0108, +0.0206]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.2_walk_contrasts[1]` |
| tobs, mode out: [2 among walks] C-PR′ (λ=0.5) − AWP′ on H_q(I_T) | -0.0617 [-0.0709, -0.0526]; share of resamples above 0 0.000 | `discovery/discovery_tobs_out.json` : `fixed_order.2_walk_contrasts[2]` |
| tobs, mode out: [2 among walks] C-PR′ (λ=0.5) − AWP′ on H_q(I_A) | -0.0016 [-0.0091, +0.0063]; share of resamples above 0 0.345 | `discovery/discovery_tobs_out.json` : `fixed_order.2_walk_contrasts[3]` |
| tobs, mode out: [2 among walks] C-PR′ (λ=0.5) − C-PR′ (λ=1) on H_q(I_T) | +0.2431 [+0.2316, +0.2525]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.2_walk_contrasts[4]` |
| tobs, mode out: [2 among walks] C-PR′ (λ=0.5) − C-PR′ (λ=1) on H_q(I_A) | +0.0949 [+0.0865, +0.1033]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.2_walk_contrasts[5]` |
| tobs, mode out: [2 among walks] C-PR′ (λ=0.5) − EndorseRank′ on H_q(I_T) | +0.2424 [+0.2312, +0.2518]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.2_walk_contrasts[6]` |
| tobs, mode out: [2 among walks] C-PR′ (λ=0.5) − EndorseRank′ on H_q(I_A) | +0.0936 [+0.0852, +0.1020]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.2_walk_contrasts[7]` |
| tobs, mode out: [2 among walks] S-PR′ − C-PR′ (λ=0) on H_q(I_T) | +0.0057 [+0.0041, +0.0078]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.2_walk_contrasts[8]` |
| tobs, mode out: [2 among walks] S-PR′ − C-PR′ (λ=0) on H_q(I_A) | +0.0221 [+0.0185, +0.0256]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.2_walk_contrasts[9]` |
| tobs, mode out: [3 λ] C-PR′ (λ=0.25) D1 on H_q(I_T) | +0.2951 [+0.2841, +0.3045]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.3_lambda.cpr_l25.i_t@q.D1` |
| tobs, mode out: [3 λ] C-PR′ (λ=0.25) D2 on H_q(I_T) | +0.1103 [+0.0982, +0.1225]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.3_lambda.cpr_l25.i_t@q.D2` |
| tobs, mode out: [3 λ] C-PR′ (λ=0.25) minus C-PR′ (λ=0.5) on H_q(I_T) | +0.0301 [+0.0277, +0.0326]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.3_lambda.cpr_l25.i_t@q.vs_cpr_l50` |
| tobs, mode out: [3 λ] C-PR′ (λ=0.25) D1 on H_q(I_A) | +0.1240 [+0.1146, +0.1332]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.3_lambda.cpr_l25.i_a@q.D1` |
| tobs, mode out: [3 λ] C-PR′ (λ=0.25) D2 on H_q(I_A) | +0.0533 [+0.0442, +0.0617]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.3_lambda.cpr_l25.i_a@q.D2` |
| tobs, mode out: [3 λ] C-PR′ (λ=0.25) minus C-PR′ (λ=0.5) on H_q(I_A) | +0.0098 [+0.0080, +0.0114]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.3_lambda.cpr_l25.i_a@q.vs_cpr_l50` |
| tobs, mode out: [3 λ] C-PR′ (λ=0.75) D1 on H_q(I_T) | +0.2565 [+0.2448, +0.2664]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.3_lambda.cpr_l75.i_t@q.D1` |
| tobs, mode out: [3 λ] C-PR′ (λ=0.75) D2 on H_q(I_T) | +0.0718 [+0.0603, +0.0832]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.3_lambda.cpr_l75.i_t@q.D2` |
| tobs, mode out: [3 λ] C-PR′ (λ=0.75) minus C-PR′ (λ=0.5) on H_q(I_T) | -0.0085 [-0.0108, -0.0064]; share of resamples above 0 0.000 | `discovery/discovery_tobs_out.json` : `fixed_order.3_lambda.cpr_l75.i_t@q.vs_cpr_l50` |
| tobs, mode out: [3 λ] C-PR′ (λ=0.75) D1 on H_q(I_A) | +0.1013 [+0.0919, +0.1104]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.3_lambda.cpr_l75.i_a@q.D1` |
| tobs, mode out: [3 λ] C-PR′ (λ=0.75) D2 on H_q(I_A) | +0.0306 [+0.0214, +0.0396]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.3_lambda.cpr_l75.i_a@q.D2` |
| tobs, mode out: [3 λ] C-PR′ (λ=0.75) minus C-PR′ (λ=0.5) on H_q(I_A) | -0.0129 [-0.0148, -0.0110]; share of resamples above 0 0.000 | `discovery/discovery_tobs_out.json` : `fixed_order.3_lambda.cpr_l75.i_a@q.vs_cpr_l50` |
| tobs, mode out: [4 Cho] D1 on H_q(IB_U) | +0.1769 [+0.1659, +0.1893]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.4_cho.hot_sets.ib_u@q.D1` |
| tobs, mode out: [4 Cho] D2 on H_q(IB_U) | -0.1955 [-0.2086, -0.1819]; share of resamples above 0 0.000 | `discovery/discovery_tobs_out.json` : `fixed_order.4_cho.hot_sets.ib_u@q.D2` |
| tobs, mode out: [4 Cho] D1 on H_q(IR) | +0.3736 [+0.3634, +0.3835]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.4_cho.hot_sets.ir@q.D1` |
| tobs, mode out: [4 Cho] D2 on H_q(IR) | +0.3033 [+0.2945, +0.3129]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.4_cho.hot_sets.ir@q.D2` |
| tobs, mode out: [4 Cho] replication contrast C-PR′ − IB′_U on H_q(IB_U) | -0.1955 [-0.2086, -0.1819]; share of resamples above 0 0.000 | `discovery/discovery_tobs_out.json` : `fixed_order.4_cho.replication_contrast` |
| tobs, mode out: [5 sensitivity x=0.05] D1 on H_q(I_T) | +0.2762 [+0.2652, +0.2857]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.5_sensitivities.x.x=0.05.i_t@q.D1` |
| tobs, mode out: [5 sensitivity x=0.05] D2 on H_q(I_T) | +0.0881 [+0.0772, +0.0978]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.5_sensitivities.x.x=0.05.i_t@q.D2` |
| tobs, mode out: [5 sensitivity x=0.05] D1 on H_q(I_A) | +0.1211 [+0.1119, +0.1298]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.5_sensitivities.x.x=0.05.i_a@q.D1` |
| tobs, mode out: [5 sensitivity x=0.05] D2 on H_q(I_A) | +0.0493 [+0.0403, +0.0570]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.5_sensitivities.x.x=0.05.i_a@q.D2` |
| tobs, mode out: [5 sensitivity x=0.2] D1 on H_q(I_T) | +0.1804 [+0.1692, +0.1903]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.5_sensitivities.x.x=0.2.i_t@q.D1` |
| tobs, mode out: [5 sensitivity x=0.2] D2 on H_q(I_T) | +0.0296 [+0.0186, +0.0407]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.5_sensitivities.x.x=0.2.i_t@q.D2` |
| tobs, mode out: [5 sensitivity x=0.2] D1 on H_q(I_A) | +0.0422 [+0.0326, +0.0526]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.5_sensitivities.x.x=0.2.i_a@q.D1` |
| tobs, mode out: [5 sensitivity x=0.2] D2 on H_q(I_A) | -0.0251 [-0.0341, -0.0167]; share of resamples above 0 0.000 | `discovery/discovery_tobs_out.json` : `fixed_order.5_sensitivities.x.x=0.2.i_a@q.D2` |
| tobs, mode out: [5 sensitivity secondary q] q | 0.050 | `discovery/discovery_tobs_out.json` : `fixed_order.5_sensitivities.q_secondary.q` |
| tobs, mode out: [5 sensitivity secondary q] D1 on H_q2(I_T) | +0.0942 [+0.0910, +0.0972]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.5_sensitivities.q_secondary.i_t@q2.D1` |
| tobs, mode out: [5 sensitivity secondary q] D2 on H_q2(I_T) | +0.0267 [+0.0231, +0.0304]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.5_sensitivities.q_secondary.i_t@q2.D2` |
| tobs, mode out: [5 sensitivity secondary q] D1 on H_q2(I_A) | +0.1014 [+0.0938, +0.1076]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.5_sensitivities.q_secondary.i_a@q2.D1` |
| tobs, mode out: [5 sensitivity secondary q] D2 on H_q2(I_A) | +0.0231 [+0.0147, +0.0303]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.5_sensitivities.q_secondary.i_a@q2.D2` |
| tobs, mode out: [5 sensitivity no hubs] hubs | 509 | `discovery/discovery_tobs_out.json` : `fixed_order.5_sensitivities.no_hubs.hubs` |
| tobs, mode out: [5 sensitivity no hubs] D1 on H_q(I_T) without hubs | +0.2430 [+0.2316, +0.2545]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.5_sensitivities.no_hubs.i_t@q-nohubs.D1` |
| tobs, mode out: [5 sensitivity no hubs] D2 on H_q(I_T) without hubs | +0.0652 [+0.0524, +0.0786]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.5_sensitivities.no_hubs.i_t@q-nohubs.D2` |
| tobs, mode out: [5 sensitivity no hubs] D1 on H_q(I_A) without hubs | +0.1062 [+0.0969, +0.1156]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.5_sensitivities.no_hubs.i_a@q-nohubs.D1` |
| tobs, mode out: [5 sensitivity no hubs] D2 on H_q(I_A) without hubs | +0.0393 [+0.0294, +0.0479]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.5_sensitivities.no_hubs.i_a@q-nohubs.D2` |
| tobs, mode out: [5 sensitivity importance by counts] D1 on H_q(N_T) | +0.1309 [+0.1236, +0.1386]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.5_sensitivities.importance_counts.n_t@q.D1` |
| tobs, mode out: [5 sensitivity importance by counts] D2 on H_q(N_T) | -0.0117 [-0.0196, -0.0032]; share of resamples above 0 0.003 | `discovery/discovery_tobs_out.json` : `fixed_order.5_sensitivities.importance_counts.n_t@q.D2` |
| tobs, mode out: [5 sensitivity importance by counts] D1 on H_q(N_A) | +0.1184 [+0.1091, +0.1285]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.5_sensitivities.importance_counts.n_a@q.D1` |
| tobs, mode out: [5 sensitivity importance by counts] D2 on H_q(N_A) | +0.0417 [+0.0322, +0.0511]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.5_sensitivities.importance_counts.n_a@q.D2` |
| tobs, mode out: [5 sensitivity seed bootstrap] D1 on H_q(I_T) | +0.2650 [+0.2147, +0.3053]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.5_sensitivities.seed_bootstrap.i_t@q.D1` |
| tobs, mode out: [5 sensitivity seed bootstrap] D2 on H_q(I_T) | +0.0803 [+0.0259, +0.1448]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.5_sensitivities.seed_bootstrap.i_t@q.D2` |
| tobs, mode out: [5 sensitivity seed bootstrap] D1 on H_q(I_A) | +0.1143 [+0.0759, +0.1424]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.5_sensitivities.seed_bootstrap.i_a@q.D1` |
| tobs, mode out: [5 sensitivity seed bootstrap] D2 on H_q(I_A) | +0.0436 [+0.0193, +0.0724]; share of resamples above 0 1.000 | `discovery/discovery_tobs_out.json` : `fixed_order.5_sensitivities.seed_bootstrap.i_a@q.D2` |
| tobs, mode out: share of picks decided by a tie, breadth-first | 0.0000 | `discovery/discovery_tobs_out.json` : `diagnostics.ties.bfs` |
| tobs, mode out: share of picks decided by a tie, random | 0.0000 | `discovery/discovery_tobs_out.json` : `diagnostics.ties.random` |
| tobs, mode out: share of picks decided by a tie, IB′_A (allowance backlinks) | 0.9999 | `discovery/discovery_tobs_out.json` : `diagnostics.ties.ib_a` |
| tobs, mode out: share of picks decided by a tie, IB′_T (transfer backlinks) | 0.9995 | `discovery/discovery_tobs_out.json` : `diagnostics.ties.ib_t` |
| tobs, mode out: share of picks decided by a tie, IB′_U (contract backlinks) | 0.9995 | `discovery/discovery_tobs_out.json` : `diagnostics.ties.ib_u` |
| tobs, mode out: share of picks decided by a tie, EndorseRank′ | 0.9975 | `discovery/discovery_tobs_out.json` : `diagnostics.ties.endorserank` |
| tobs, mode out: share of picks decided by a tie, EndorseRank-activity′ | 0.9974 | `discovery/discovery_tobs_out.json` : `diagnostics.ties.endorserank_activity` |
| tobs, mode out: share of picks decided by a tie, AWP′ | 0.0051 | `discovery/discovery_tobs_out.json` : `diagnostics.ties.awp` |
| tobs, mode out: share of picks decided by a tie, C-PR′ (λ=0.5) | 0.0231 | `discovery/discovery_tobs_out.json` : `diagnostics.ties.cpr_l50` |
| tobs, mode out: share of picks decided by a tie, C-PR′ (λ=0.25) | 0.0195 | `discovery/discovery_tobs_out.json` : `diagnostics.ties.cpr_l25` |
| tobs, mode out: share of picks decided by a tie, C-PR′ (λ=0.75) | 0.0247 | `discovery/discovery_tobs_out.json` : `diagnostics.ties.cpr_l75` |
| tobs, mode out: share of picks decided by a tie, C-PR′ (λ=1) | 0.9991 | `discovery/discovery_tobs_out.json` : `diagnostics.ties.cpr_l100` |
| tobs, mode out: share of picks decided by a tie, C-PR′ (λ=0) | 0.0188 | `discovery/discovery_tobs_out.json` : `diagnostics.ties.cpr_l0` |
| tobs, mode out: share of picks decided by a tie, S-PR′ | 0.0189 | `discovery/discovery_tobs_out.json` : `diagnostics.ties.spr` |
| tobs, mode out: share of picks decided by a tie, δ′ (diagnostic) | 0.2826 | `discovery/discovery_tobs_out.json` : `diagnostics.ties.delta` |
| tobs, mode out: wasted visits of breadth-first (first 1%, first 10%) | 0.8643, 0.9029 | `discovery/discovery_tobs_out.json` : `diagnostics.wasted_visits.bfs` |
| tobs, mode out: wasted visits of random (first 1%, first 10%) | 0.8919, 0.8713 | `discovery/discovery_tobs_out.json` : `diagnostics.wasted_visits.random` |
| tobs, mode out: wasted visits of IB′_A (allowance backlinks) (first 1%, first 10%) | 0.8423, 0.9000 | `discovery/discovery_tobs_out.json` : `diagnostics.wasted_visits.ib_a` |
| tobs, mode out: wasted visits of IB′_T (transfer backlinks) (first 1%, first 10%) | 0.5849, 0.8893 | `discovery/discovery_tobs_out.json` : `diagnostics.wasted_visits.ib_t` |
| tobs, mode out: wasted visits of IB′_U (contract backlinks) (first 1%, first 10%) | 0.5840, 0.8884 | `discovery/discovery_tobs_out.json` : `diagnostics.wasted_visits.ib_u` |
| tobs, mode out: wasted visits of EndorseRank′ (first 1%, first 10%) | 0.8424, 0.8981 | `discovery/discovery_tobs_out.json` : `diagnostics.wasted_visits.endorserank` |
| tobs, mode out: wasted visits of EndorseRank-activity′ (first 1%, first 10%) | 0.8424, 0.8981 | `discovery/discovery_tobs_out.json` : `diagnostics.wasted_visits.endorserank_activity` |
| tobs, mode out: wasted visits of AWP′ (first 1%, first 10%) | 0.4759, 0.7272 | `discovery/discovery_tobs_out.json` : `diagnostics.wasted_visits.awp` |
| tobs, mode out: wasted visits of C-PR′ (λ=0.5) (first 1%, first 10%) | 0.4904, 0.8413 | `discovery/discovery_tobs_out.json` : `diagnostics.wasted_visits.cpr_l50` |
| tobs, mode out: wasted visits of C-PR′ (λ=0.25) (first 1%, first 10%) | 0.4912, 0.8110 | `discovery/discovery_tobs_out.json` : `diagnostics.wasted_visits.cpr_l25` |
| tobs, mode out: wasted visits of C-PR′ (λ=0.75) (first 1%, first 10%) | 0.4942, 0.8332 | `discovery/discovery_tobs_out.json` : `diagnostics.wasted_visits.cpr_l75` |
| tobs, mode out: wasted visits of C-PR′ (λ=1) (first 1%, first 10%) | 0.8424, 0.9009 | `discovery/discovery_tobs_out.json` : `diagnostics.wasted_visits.cpr_l100` |
| tobs, mode out: wasted visits of C-PR′ (λ=0) (first 1%, first 10%) | 0.5562, 0.7825 | `discovery/discovery_tobs_out.json` : `diagnostics.wasted_visits.cpr_l0` |
| tobs, mode out: wasted visits of S-PR′ (first 1%, first 10%) | 0.5130, 0.8120 | `discovery/discovery_tobs_out.json` : `diagnostics.wasted_visits.spr` |
| tobs, mode out: wasted visits of δ′ (diagnostic) (first 1%, first 10%) | 0.4283, 0.4634 | `discovery/discovery_tobs_out.json` : `diagnostics.wasted_visits.delta` |
| tobs, mode out: hubs | 509 | `discovery/discovery_tobs_out.json` : `diagnostics.hubs` |
| tobs, mode out: largest hub | 0xfb64e79a562f7250131cf528242ceb10fdc82395 with IB_U 90,127 | `discovery/discovery_tobs_out.json` : `diagnostics.hubs[0]` |
| tobs, mode out: median over hubs of the mean visit index, breadth-first | 44,547.7 | `discovery/discovery_tobs_out.json` : `diagnostics.hub_visits.bfs.mean` |
| tobs, mode out: median over hubs of the mean visit index, random | 127,441.6 | `discovery/discovery_tobs_out.json` : `diagnostics.hub_visits.random.mean` |
| tobs, mode out: median over hubs of the mean visit index, IB′_A (allowance backlinks) | 44,794.2 | `discovery/discovery_tobs_out.json` : `diagnostics.hub_visits.ib_a.mean` |
| tobs, mode out: median over hubs of the mean visit index, IB′_T (transfer backlinks) | 25,222.9 | `discovery/discovery_tobs_out.json` : `diagnostics.hub_visits.ib_t.mean` |
| tobs, mode out: median over hubs of the mean visit index, IB′_U (contract backlinks) | 25,219.8 | `discovery/discovery_tobs_out.json` : `diagnostics.hub_visits.ib_u.mean` |
| tobs, mode out: median over hubs of the mean visit index, EndorseRank′ | 45,444.7 | `discovery/discovery_tobs_out.json` : `diagnostics.hub_visits.endorserank.mean` |
| tobs, mode out: median over hubs of the mean visit index, EndorseRank-activity′ | 45,444.8 | `discovery/discovery_tobs_out.json` : `diagnostics.hub_visits.endorserank_activity.mean` |
| tobs, mode out: median over hubs of the mean visit index, AWP′ | 531.900 | `discovery/discovery_tobs_out.json` : `diagnostics.hub_visits.awp.mean` |
| tobs, mode out: median over hubs of the mean visit index, C-PR′ (λ=0.5) | 1,102.5 | `discovery/discovery_tobs_out.json` : `diagnostics.hub_visits.cpr_l50.mean` |
| tobs, mode out: median over hubs of the mean visit index, C-PR′ (λ=0.25) | 1,094 | `discovery/discovery_tobs_out.json` : `diagnostics.hub_visits.cpr_l25.mean` |
| tobs, mode out: median over hubs of the mean visit index, C-PR′ (λ=0.75) | 1,027.5 | `discovery/discovery_tobs_out.json` : `diagnostics.hub_visits.cpr_l75.mean` |
| tobs, mode out: median over hubs of the mean visit index, C-PR′ (λ=1) | 45,416.8 | `discovery/discovery_tobs_out.json` : `diagnostics.hub_visits.cpr_l100.mean` |
| tobs, mode out: median over hubs of the mean visit index, C-PR′ (λ=0) | 998.800 | `discovery/discovery_tobs_out.json` : `diagnostics.hub_visits.cpr_l0.mean` |
| tobs, mode out: median over hubs of the mean visit index, S-PR′ | 918.300 | `discovery/discovery_tobs_out.json` : `diagnostics.hub_visits.spr.mean` |
| tobs, mode out: median over hubs of the mean visit index, δ′ (diagnostic) | 702.000 | `discovery/discovery_tobs_out.json` : `diagnostics.hub_visits.delta.mean` |
| tobs, mode out: coverage, contracts | 809,296 | `discovery/discovery_tobs_out.json` : `diagnostics.coverage.contracts` |
| tobs, mode out: coverage, outside g | 112,210 | `discovery/discovery_tobs_out.json` : `diagnostics.coverage.outside_g` |
| tobs, mode out: coverage, inflow untyped usd | 1,681,953,612.2 | `discovery/discovery_tobs_out.json` : `diagnostics.coverage.inflow_untyped_usd` |
| tobs, mode out: coverage of I_T, total (USD) | 16,611,212,142.1 | `discovery/discovery_tobs_out.json` : `diagnostics.coverage.i_t.total` |
| tobs, mode out: coverage of I_T, share held by the universe | 0.8130 | `discovery/discovery_tobs_out.json` : `diagnostics.coverage.i_t.share_U` |
| tobs, mode out: coverage of I_T, share in scc | 0.7124 | `discovery/discovery_tobs_out.json` : `diagnostics.coverage.i_t.share_by_part.scc` |
| tobs, mode out: coverage of I_T, share in in | 0.0970 | `discovery/discovery_tobs_out.json` : `diagnostics.coverage.i_t.share_by_part.in` |
| tobs, mode out: coverage of I_T, share in out | 0.1007 | `discovery/discovery_tobs_out.json` : `diagnostics.coverage.i_t.share_by_part.out` |
| tobs, mode out: coverage of I_T, share in other | 0.0813 | `discovery/discovery_tobs_out.json` : `diagnostics.coverage.i_t.share_by_part.other` |
| tobs, mode out: coverage of I_T, share in isolated | 0.0042 | `discovery/discovery_tobs_out.json` : `diagnostics.coverage.i_t.share_by_part.isolated` |
| tobs, mode out: coverage of I_T, share in outside g | 0.0045 | `discovery/discovery_tobs_out.json` : `diagnostics.coverage.i_t.share_by_part.outside_g` |
| tobs, mode out: coverage of I_T, top 1% of rows: rows | 8,093 | `discovery/discovery_tobs_out.json` : `diagnostics.coverage.i_t.top_1pct.rows` |
| tobs, mode out: coverage of I_T, top 1% of rows: share in U | 0.2963 | `discovery/discovery_tobs_out.json` : `diagnostics.coverage.i_t.top_1pct.share_in_U` |
| tobs, mode out: coverage of I_T, top 1% of rows: tied at cut | 12,701 | `discovery/discovery_tobs_out.json` : `diagnostics.coverage.i_t.top_1pct.tied_at_cut` |
| tobs, mode out: coverage of I_T, top 1% of rows: slots at cut | 1,937 | `discovery/discovery_tobs_out.json` : `diagnostics.coverage.i_t.top_1pct.slots_at_cut` |
| tobs, mode out: coverage of I_A, total (USD) | 309,472,584.1 | `discovery/discovery_tobs_out.json` : `diagnostics.coverage.i_a.total` |
| tobs, mode out: coverage of I_A, share held by the universe | 0.9058 | `discovery/discovery_tobs_out.json` : `diagnostics.coverage.i_a.share_U` |
| tobs, mode out: coverage of I_A, share in scc | 0.5022 | `discovery/discovery_tobs_out.json` : `diagnostics.coverage.i_a.share_by_part.scc` |
| tobs, mode out: coverage of I_A, share in in | 0.0174 | `discovery/discovery_tobs_out.json` : `diagnostics.coverage.i_a.share_by_part.in` |
| tobs, mode out: coverage of I_A, share in out | 0.4036 | `discovery/discovery_tobs_out.json` : `diagnostics.coverage.i_a.share_by_part.out` |
| tobs, mode out: coverage of I_A, share in other | 0.0342 | `discovery/discovery_tobs_out.json` : `diagnostics.coverage.i_a.share_by_part.other` |
| tobs, mode out: coverage of I_A, share in isolated | 0.0361 | `discovery/discovery_tobs_out.json` : `diagnostics.coverage.i_a.share_by_part.isolated` |
| tobs, mode out: coverage of I_A, share in outside g | 0.0066 | `discovery/discovery_tobs_out.json` : `diagnostics.coverage.i_a.share_by_part.outside_g` |
| tobs, mode out: coverage of I_A, top 1% of rows: rows | 8,093 | `discovery/discovery_tobs_out.json` : `diagnostics.coverage.i_a.top_1pct.rows` |
| tobs, mode out: coverage of I_A, top 1% of rows: share in U | 0.2623 | `discovery/discovery_tobs_out.json` : `diagnostics.coverage.i_a.top_1pct.share_in_U` |
| tobs, mode out: coverage of I_A, top 1% of rows: tied at cut | 1 | `discovery/discovery_tobs_out.json` : `diagnostics.coverage.i_a.top_1pct.tied_at_cut` |
| tobs, mode out: coverage of I_A, top 1% of rows: slots at cut | 1 | `discovery/discovery_tobs_out.json` : `diagnostics.coverage.i_a.top_1pct.slots_at_cut` |
| tobs, mode out: crawls of bfs@1/50 | 20 crawls, 107.500 s, 501.000 recomputes, 0.000 solves, 0.000 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_out.json` : `runs.bfs@1/50` |
| tobs, mode out: crawls of random@1/50 | 20 crawls, 1,964.6 s, 508,636 recomputes, 0.000 solves, 0.000 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_out.json` : `runs.random@1/50` |
| tobs, mode out: crawls of ib_a@1/50 | 20 crawls, 457.072 s, 501.450 recomputes, 0.000 solves, 0.000 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_out.json` : `runs.ib_a@1/50` |
| tobs, mode out: crawls of ib_t@1/50 | 20 crawls, 325.368 s, 502.200 recomputes, 0.000 solves, 0.000 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_out.json` : `runs.ib_t@1/50` |
| tobs, mode out: crawls of ib_u@1/50 | 20 crawls, 338.506 s, 502.250 recomputes, 0.000 solves, 0.000 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_out.json` : `runs.ib_u@1/50` |
| tobs, mode out: crawls of endorserank@1/50 | 20 crawls, 1,266.2 s, 501.450 recomputes, 501.450 solves, 956.950 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_out.json` : `runs.endorserank@1/50` |
| tobs, mode out: crawls of endorserank_activity@1/50 | 20 crawls, 3,473.4 s, 501.450 recomputes, 501.450 solves, 13,662.1 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_out.json` : `runs.endorserank_activity@1/50` |
| tobs, mode out: crawls of awp@1/50 | 20 crawls, 28,626.5 s, 497.000 recomputes, 497.000 solves, 23,844.8 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_out.json` : `runs.awp@1/50` |
| tobs, mode out: crawls of cpr_l50@1/50 | 20 crawls, 14,718.0 s, 498.000 recomputes, 498.000 solves, 21,894.6 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_out.json` : `runs.cpr_l50@1/50` |
| tobs, mode out: crawls of cpr_l25@1/50 | 20 crawls, 16,465.6 s, 498.000 recomputes, 498.000 solves, 23,186.2 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_out.json` : `runs.cpr_l25@1/50` |
| tobs, mode out: crawls of cpr_l75@1/50 | 20 crawls, 13,909.1 s, 498.000 recomputes, 498.000 solves, 20,961.0 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_out.json` : `runs.cpr_l75@1/50` |
| tobs, mode out: crawls of cpr_l100@1/50 | 20 crawls, 1,288.7 s, 501.450 recomputes, 501.450 solves, 943.650 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_out.json` : `runs.cpr_l100@1/50` |
| tobs, mode out: crawls of cpr_l0@1/50 | 20 crawls, 18,056.4 s, 498.000 recomputes, 498.000 solves, 24,879 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_out.json` : `runs.cpr_l0@1/50` |
| tobs, mode out: crawls of spr@1/50 | 20 crawls, 17,675.1 s, 498.000 recomputes, 996.000 solves, 26,262.2 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_out.json` : `runs.spr@1/50` |
| tobs, mode out: crawls of delta@1/50 | 20 crawls, 272.319 s, 498.000 recomputes, 0.000 solves, 0.000 iterations (means per crawl but the seconds) | `discovery/discovery_tobs_out.json` : `runs.delta@1/50` |
| tobs, mode out: invariant all visited | yes | `discovery/discovery_tobs_out.json` : `invariants.all_visited` |
| tobs, mode out: invariant final walks within | 1e-09 | `discovery/discovery_tobs_out.json` : `invariants.final_walks_within` |
| tobs, mode out: invariant max final diff | 0 | `discovery/discovery_tobs_out.json` : `invariants.max_final_diff` |

### Run t1, mode both

| Quantity | Value | Source |
|---|---|---|
| t1, mode both: decides | no | `discovery/discovery_t1_both.json` : `decides` |
| t1, mode both: is primary | yes | `discovery/discovery_t1_both.json` : `is_primary` |
| t1, mode both: primary mode | both | `discovery/discovery_t1_both.json` : `primary_mode` |
| t1, mode both: created at | 2026-11-11T00:24:05+00:00 | `discovery/discovery_t1_both.json` : `created_at` |
| t1, mode both: seconds | 23,333.9 | `discovery/discovery_t1_both.json` : `seconds` |
| t1, mode both: workers | 16 | `discovery/discovery_t1_both.json` : `workers` |
| t1, mode both: protocol rho | 1/50 | `discovery/discovery_t1_both.json` : `protocol.rho` |
| t1, mode both: protocol q | 1/100 | `discovery/discovery_t1_both.json` : `protocol.q` |
| t1, mode both: protocol q_secondary | 0.05 | `discovery/discovery_t1_both.json` : `protocol.q_secondary` |
| t1, mode both: protocol decision_covers | ['few_capped_allowance_in_edges'] | `discovery/discovery_t1_both.json` : `protocol.decision_covers` |
| t1, mode both: code revision | f1079690751b7a9c8669c72a7699ca4f771af8fa | `discovery/discovery_t1_both.json` : `provenance.head` |
| t1, mode both: sizes of the graph, g_nodes | 1,403,959 | `discovery/discovery_t1_both.json` : `sizes.graph.g_nodes` |
| t1, mode both: sizes of the graph, allow_pairs | 17,940 | `discovery/discovery_t1_both.json` : `sizes.graph.allow_pairs` |
| t1, mode both: sizes of the graph, transfer_pairs | 2,269,073 | `discovery/discovery_t1_both.json` : `sizes.graph.transfer_pairs` |
| t1, mode both: sizes of the graph, nodes | 1,111,554 | `discovery/discovery_t1_both.json` : `sizes.graph.nodes` |
| t1, mode both: sizes of the graph, edges | 2,269,421 | `discovery/discovery_t1_both.json` : `sizes.graph.edges` |
| t1, mode both: sizes of the graph, scc | 222,592 | `discovery/discovery_t1_both.json` : `sizes.graph.scc` |
| t1, mode both: sizes of the graph, in | 169,237 | `discovery/discovery_t1_both.json` : `sizes.graph.in` |
| t1, mode both: sizes of the graph, out | 109,804 | `discovery/discovery_t1_both.json` : `sizes.graph.out` |
| t1, mode both: sizes of the graph, other | 609,921 | `discovery/discovery_t1_both.json` : `sizes.graph.other` |
| t1, mode both: sizes of the graph, U | 332,396 | `discovery/discovery_t1_both.json` : `sizes.graph.U` |
| t1, mode both: sizes of the graph, E_U | 1,283,946 | `discovery/discovery_t1_both.json` : `sizes.graph.E_U` |
| t1, mode both: sizes of the graph, WCC | 1,015,867 | `discovery/discovery_t1_both.json` : `sizes.graph.WCC` |
| t1, mode both: sizes of the graph, E_WCC | 2,121,895 | `discovery/discovery_t1_both.json` : `sizes.graph.E_WCC` |
| t1, mode both: sizes of the universe, U | 1,015,867 | `discovery/discovery_t1_both.json` : `sizes.universe.U` |
| t1, mode both: sizes of the universe, E_U | 2,121,895 | `discovery/discovery_t1_both.json` : `sizes.universe.E_U` |
| t1, mode both: sizes of the universe, allow_pairs | 17,741 | `discovery/discovery_t1_both.json` : `sizes.universe.allow_pairs` |
| t1, mode both: sizes of the universe, transfer_pairs | 2,121,600 | `discovery/discovery_t1_both.json` : `sizes.universe.transfer_pairs` |
| t1, mode both: contracts in H_q(I_T) | 12,697 | `discovery/discovery_t1_both.json` : `hot_sets.i_t@q` |
| t1, mode both: contracts in H_q(I_A) | 8,136 | `discovery/discovery_t1_both.json` : `hot_sets.i_a@q` |
| t1, mode both: contracts in H_q(N_T) | 22,201 | `discovery/discovery_t1_both.json` : `hot_sets.n_t@q` |
| t1, mode both: contracts in H_q(N_A) | 5,223 | `discovery/discovery_t1_both.json` : `hot_sets.n_a@q` |
| t1, mode both: contracts in H_q(IB_U) | 10,456 | `discovery/discovery_t1_both.json` : `hot_sets.ib_u@q` |
| t1, mode both: contracts in H_q(IR) | 10,159 | `discovery/discovery_t1_both.json` : `hot_sets.ir@q` |
| t1, mode both: contracts in H_q2(I_T) | 50,794 | `discovery/discovery_t1_both.json` : `hot_sets.i_t@q2` |
| t1, mode both: contracts in H_q(I_T) without hubs | 12,151 | `discovery/discovery_t1_both.json` : `hot_sets.i_t@q-nohubs` |
| t1, mode both: contracts in H_q2(I_A) | 8,136 | `discovery/discovery_t1_both.json` : `hot_sets.i_a@q2` |
| t1, mode both: contracts in H_q(I_A) without hubs | 7,976 | `discovery/discovery_t1_both.json` : `hot_sets.i_a@q-nohubs` |
| t1, mode both: D1 = C-PR′ − BFS on H_q(I_T) | +0.0574 [+0.0530, +0.0611]; share of resamples above 0 1.000 | `discovery/discovery_t1_both.json` : `decision.i_t.D1` |
| t1, mode both: D2 = C-PR′ − IB′_U on H_q(I_T) | -0.0158 [-0.0196, -0.0121]; share of resamples above 0 0.000 | `discovery/discovery_t1_both.json` : `decision.i_t.D2` |
| t1, mode both: contrasts on I_T with the interval above 0 | D1 | `discovery/discovery_t1_both.json` : `decision.i_t.above_zero` |
| t1, mode both: contrasts on I_T with the interval below 0 | D2 | `discovery/discovery_t1_both.json` : `decision.i_t.below_zero` |
| t1, mode both: D1 = C-PR′ − BFS on H_q(I_A) | +0.0230 [+0.0164, +0.0291]; share of resamples above 0 1.000 | `discovery/discovery_t1_both.json` : `decision.i_a.D1` |
| t1, mode both: D2 = C-PR′ − IB′_U on H_q(I_A) | -0.1010 [-0.1083, -0.0933]; share of resamples above 0 0.000 | `discovery/discovery_t1_both.json` : `decision.i_a.D2` |
| t1, mode both: contrasts on I_A with the interval above 0 | D1 | `discovery/discovery_t1_both.json` : `decision.i_a.above_zero` |
| t1, mode both: contrasts on I_A with the interval below 0 | D2 | `discovery/discovery_t1_both.json` : `decision.i_a.below_zero` |
| t1, mode both: AUC of breadth-first on H_q(I_T) | 0.0543 [0.0524, 0.0564]; seeds 0.0013 to 0.1299 | `discovery/discovery_t1_both.json` : `auc.i_t@q.bfs.x=0.1` |
| t1, mode both: AUC of random on H_q(I_T) | 0.0543 [0.0528, 0.0558]; seeds 0.0032 to 0.0877 | `discovery/discovery_t1_both.json` : `auc.i_t@q.random.x=0.1` |
| t1, mode both: AUC of IB′_A (allowance backlinks) on H_q(I_T) | 0.0539 [0.0516, 0.0563]; seeds 0.0021 to 0.1242 | `discovery/discovery_t1_both.json` : `auc.i_t@q.ib_a.x=0.1` |
| t1, mode both: AUC of IB′_T (transfer backlinks) on H_q(I_T) | 0.1107 [0.1067, 0.1154]; seeds 0.0248 to 0.1602 | `discovery/discovery_t1_both.json` : `auc.i_t@q.ib_t.x=0.1` |
| t1, mode both: AUC of IB′_U (contract backlinks) on H_q(I_T) | 0.1276 [0.1228, 0.1331]; seeds 0.0728 to 0.1601 | `discovery/discovery_t1_both.json` : `auc.i_t@q.ib_u.x=0.1` |
| t1, mode both: AUC of EndorseRank′ on H_q(I_T) | 0.0526 [0.0503, 0.0550]; seeds 0.0021 to 0.1207 | `discovery/discovery_t1_both.json` : `auc.i_t@q.endorserank.x=0.1` |
| t1, mode both: AUC of EndorseRank-activity′ on H_q(I_T) | 0.0587 [0.0559, 0.0612]; seeds 0.0055 to 0.1142 | `discovery/discovery_t1_both.json` : `auc.i_t@q.endorserank_activity.x=0.1` |
| t1, mode both: AUC of AWP′ on H_q(I_T) | 0.1524 [0.1466, 0.1588]; seeds 0.1524 to 0.1524 | `discovery/discovery_t1_both.json` : `auc.i_t@q.awp.x=0.1` |
| t1, mode both: AUC of C-PR′ (λ=0.5) on H_q(I_T) | 0.1118 [0.1059, 0.1169]; seeds 0.1044 to 0.1167 | `discovery/discovery_t1_both.json` : `auc.i_t@q.cpr_l50.x=0.1` |
| t1, mode both: AUC of C-PR′ (λ=0.25) on H_q(I_T) | 0.1110 [0.1052, 0.1161]; seeds 0.1045 to 0.1153 | `discovery/discovery_t1_both.json` : `auc.i_t@q.cpr_l25.x=0.1` |
| t1, mode both: AUC of C-PR′ (λ=0.75) on H_q(I_T) | 0.1121 [0.1061, 0.1173]; seeds 0.1040 to 0.1175 | `discovery/discovery_t1_both.json` : `auc.i_t@q.cpr_l75.x=0.1` |
| t1, mode both: AUC of C-PR′ (λ=1) on H_q(I_T) | 0.0526 [0.0503, 0.0549]; seeds 0.0021 to 0.1209 | `discovery/discovery_t1_both.json` : `auc.i_t@q.cpr_l100.x=0.1` |
| t1, mode both: AUC of C-PR′ (λ=0) on H_q(I_T) | 0.1088 [0.1031, 0.1139]; seeds 0.1028 to 0.1129 | `discovery/discovery_t1_both.json` : `auc.i_t@q.cpr_l0.x=0.1` |
| t1, mode both: AUC of S-PR′ on H_q(I_T) | 0.1095 [0.1036, 0.1145]; seeds 0.1036 to 0.1134 | `discovery/discovery_t1_both.json` : `auc.i_t@q.spr.x=0.1` |
| t1, mode both: AUC of δ′ (diagnostic) on H_q(I_T) | 0.1775 [0.1709, 0.1845]; seeds 0.1774 to 0.1775 | `discovery/discovery_t1_both.json` : `auc.i_t@q.delta.x=0.1` |
| t1, mode both: AUC of reference: C-PR of the full graph on H_q(I_T) | 0.1165 [0.1109, 0.1218]; seeds 0.1165 to 0.1165 | `discovery/discovery_t1_both.json` : `auc.i_t@q.ref_cpr.x=0.1` |
| t1, mode both: AUC of reference: union in-degree of the full graph on H_q(I_T) | 0.1757 [0.1694, 0.1826]; seeds 0.1757 to 0.1757 | `discovery/discovery_t1_both.json` : `auc.i_t@q.ref_ib_u.x=0.1` |
| t1, mode both: AUC of reference: ideal order on H_q(I_T) | 0.9375 [0.9369, 0.9381]; seeds 0.9375 to 0.9375 | `discovery/discovery_t1_both.json` : `auc.i_t@q.ref_ideal.x=0.1` |
| t1, mode both: AUC of reference: random curve on H_q(I_T) | 0.0500 | `discovery/discovery_t1_both.json` : `auc.i_t@q.random_curve.x=0.1` |
| t1, mode both: AUC of reference: ideal curve on H_q(I_T) | 0.9375 | `discovery/discovery_t1_both.json` : `auc.i_t@q.ideal_curve.x=0.1` |
| t1, mode both: AUC of breadth-first on H_q(I_A) | 0.1088 [0.1066, 0.1110]; seeds 0.0014 to 0.3046 | `discovery/discovery_t1_both.json` : `auc.i_a@q.bfs.x=0.1` |
| t1, mode both: AUC of random on H_q(I_A) | 0.0930 [0.0913, 0.0948]; seeds 0.0053 to 0.1974 | `discovery/discovery_t1_both.json` : `auc.i_a@q.random.x=0.1` |
| t1, mode both: AUC of IB′_A (allowance backlinks) on H_q(I_A) | 0.1094 [0.1064, 0.1124]; seeds 0.0032 to 0.2657 | `discovery/discovery_t1_both.json` : `auc.i_a@q.ib_a.x=0.1` |
| t1, mode both: AUC of IB′_T (transfer backlinks) on H_q(I_A) | 0.2001 [0.1945, 0.2055]; seeds 0.0312 to 0.3046 | `discovery/discovery_t1_both.json` : `auc.i_a@q.ib_t.x=0.1` |
| t1, mode both: AUC of IB′_U (contract backlinks) on H_q(I_A) | 0.2328 [0.2268, 0.2394]; seeds 0.1089 to 0.3137 | `discovery/discovery_t1_both.json` : `auc.i_a@q.ib_u.x=0.1` |
| t1, mode both: AUC of EndorseRank′ on H_q(I_A) | 0.1062 [0.1032, 0.1091]; seeds 0.0032 to 0.2570 | `discovery/discovery_t1_both.json` : `auc.i_a@q.endorserank.x=0.1` |
| t1, mode both: AUC of EndorseRank-activity′ on H_q(I_A) | 0.1426 [0.1377, 0.1469]; seeds 0.0189 to 0.2654 | `discovery/discovery_t1_both.json` : `auc.i_a@q.endorserank_activity.x=0.1` |
| t1, mode both: AUC of AWP′ on H_q(I_A) | 0.2220 [0.2142, 0.2302]; seeds 0.2220 to 0.2220 | `discovery/discovery_t1_both.json` : `auc.i_a@q.awp.x=0.1` |
| t1, mode both: AUC of C-PR′ (λ=0.5) on H_q(I_A) | 0.1319 [0.1248, 0.1384]; seeds 0.1209 to 0.1392 | `discovery/discovery_t1_both.json` : `auc.i_a@q.cpr_l50.x=0.1` |
| t1, mode both: AUC of C-PR′ (λ=0.25) on H_q(I_A) | 0.1297 [0.1229, 0.1362]; seeds 0.1197 to 0.1364 | `discovery/discovery_t1_both.json` : `auc.i_a@q.cpr_l25.x=0.1` |
| t1, mode both: AUC of C-PR′ (λ=0.75) on H_q(I_A) | 0.1323 [0.1252, 0.1388]; seeds 0.1206 to 0.1401 | `discovery/discovery_t1_both.json` : `auc.i_a@q.cpr_l75.x=0.1` |
| t1, mode both: AUC of C-PR′ (λ=1) on H_q(I_A) | 0.1057 [0.1027, 0.1086]; seeds 0.0032 to 0.2556 | `discovery/discovery_t1_both.json` : `auc.i_a@q.cpr_l100.x=0.1` |
| t1, mode both: AUC of C-PR′ (λ=0) on H_q(I_A) | 0.1097 [0.1035, 0.1156]; seeds 0.1007 to 0.1157 | `discovery/discovery_t1_both.json` : `auc.i_a@q.cpr_l0.x=0.1` |
| t1, mode both: AUC of S-PR′ on H_q(I_A) | 0.1170 [0.1107, 0.1231]; seeds 0.1076 to 0.1233 | `discovery/discovery_t1_both.json` : `auc.i_a@q.spr.x=0.1` |
| t1, mode both: AUC of δ′ (diagnostic) on H_q(I_A) | 0.2778 [0.2695, 0.2860]; seeds 0.2778 to 0.2779 | `discovery/discovery_t1_both.json` : `auc.i_a@q.delta.x=0.1` |
| t1, mode both: AUC of reference: C-PR of the full graph on H_q(I_A) | 0.1646 [0.1573, 0.1717]; seeds 0.1646 to 0.1646 | `discovery/discovery_t1_both.json` : `auc.i_a@q.ref_cpr.x=0.1` |
| t1, mode both: AUC of reference: union in-degree of the full graph on H_q(I_A) | 0.3151 [0.3065, 0.3240]; seeds 0.3151 to 0.3151 | `discovery/discovery_t1_both.json` : `auc.i_a@q.ref_ib_u.x=0.1` |
| t1, mode both: AUC of reference: ideal order on H_q(I_A) | 0.9600 [0.9594, 0.9605]; seeds 0.9600 to 0.9600 | `discovery/discovery_t1_both.json` : `auc.i_a@q.ref_ideal.x=0.1` |
| t1, mode both: AUC of reference: random curve on H_q(I_A) | 0.0500 | `discovery/discovery_t1_both.json` : `auc.i_a@q.random_curve.x=0.1` |
| t1, mode both: AUC of reference: ideal curve on H_q(I_A) | 0.9600 | `discovery/discovery_t1_both.json` : `auc.i_a@q.ideal_curve.x=0.1` |
| t1, mode both: [1 walk′ against its count] EndorseRank′ − IB′_A (allowance backlinks) on H_q(I_T) | -0.0012 [-0.0014, -0.0011]; share of resamples above 0 0.000 | `discovery/discovery_t1_both.json` : `fixed_order.1_walk_vs_count[0]` |
| t1, mode both: [1 walk′ against its count] EndorseRank′ − IB′_A (allowance backlinks) on H_q(I_A) | -0.0032 [-0.0034, -0.0030]; share of resamples above 0 0.000 | `discovery/discovery_t1_both.json` : `fixed_order.1_walk_vs_count[1]` |
| t1, mode both: [1 walk′ against its count] EndorseRank-activity′ − IB′_A (allowance backlinks) on H_q(I_T) | +0.0049 [+0.0035, +0.0061]; share of resamples above 0 1.000 | `discovery/discovery_t1_both.json` : `fixed_order.1_walk_vs_count[2]` |
| t1, mode both: [1 walk′ against its count] EndorseRank-activity′ − IB′_A (allowance backlinks) on H_q(I_A) | +0.0332 [+0.0300, +0.0362]; share of resamples above 0 1.000 | `discovery/discovery_t1_both.json` : `fixed_order.1_walk_vs_count[3]` |
| t1, mode both: [1 walk′ against its count] C-PR′ (λ=1) − IB′_A (allowance backlinks) on H_q(I_T) | -0.0013 [-0.0014, -0.0012]; share of resamples above 0 0.000 | `discovery/discovery_t1_both.json` : `fixed_order.1_walk_vs_count[4]` |
| t1, mode both: [1 walk′ against its count] C-PR′ (λ=1) − IB′_A (allowance backlinks) on H_q(I_A) | -0.0037 [-0.0039, -0.0035]; share of resamples above 0 0.000 | `discovery/discovery_t1_both.json` : `fixed_order.1_walk_vs_count[5]` |
| t1, mode both: [1 walk′ against its count] AWP′ − IB′_T (transfer backlinks) on H_q(I_T) | +0.0417 [+0.0381, +0.0452]; share of resamples above 0 1.000 | `discovery/discovery_t1_both.json` : `fixed_order.1_walk_vs_count[6]` |
| t1, mode both: [1 walk′ against its count] AWP′ − IB′_T (transfer backlinks) on H_q(I_A) | +0.0219 [+0.0157, +0.0284]; share of resamples above 0 1.000 | `discovery/discovery_t1_both.json` : `fixed_order.1_walk_vs_count[7]` |
| t1, mode both: [1 walk′ against its count] C-PR′ (λ=0) − IB′_T (transfer backlinks) on H_q(I_T) | -0.0019 [-0.0056, +0.0017]; share of resamples above 0 0.145 | `discovery/discovery_t1_both.json` : `fixed_order.1_walk_vs_count[8]` |
| t1, mode both: [1 walk′ against its count] C-PR′ (λ=0) − IB′_T (transfer backlinks) on H_q(I_A) | -0.0904 [-0.0971, -0.0838]; share of resamples above 0 0.000 | `discovery/discovery_t1_both.json` : `fixed_order.1_walk_vs_count[9]` |
| t1, mode both: [1 walk′ against its count] C-PR′ (λ=0.5) − IB′_A (allowance backlinks) on H_q(I_T) | +0.0579 [+0.0538, +0.0616]; share of resamples above 0 1.000 | `discovery/discovery_t1_both.json` : `fixed_order.1_walk_vs_count[10]` |
| t1, mode both: [1 walk′ against its count] C-PR′ (λ=0.5) − IB′_A (allowance backlinks) on H_q(I_A) | +0.0224 [+0.0165, +0.0281]; share of resamples above 0 1.000 | `discovery/discovery_t1_both.json` : `fixed_order.1_walk_vs_count[11]` |
| t1, mode both: [1 walk′ against its count] C-PR′ (λ=0.5) − IB′_T (transfer backlinks) on H_q(I_T) | +0.0010 [-0.0025, +0.0046]; share of resamples above 0 0.703 | `discovery/discovery_t1_both.json` : `fixed_order.1_walk_vs_count[12]` |
| t1, mode both: [1 walk′ against its count] C-PR′ (λ=0.5) − IB′_T (transfer backlinks) on H_q(I_A) | -0.0683 [-0.0756, -0.0609]; share of resamples above 0 0.000 | `discovery/discovery_t1_both.json` : `fixed_order.1_walk_vs_count[13]` |
| t1, mode both: [2 among walks] C-PR′ (λ=0.5) − C-PR′ (λ=0) on H_q(I_T) | +0.0030 [+0.0021, +0.0038]; share of resamples above 0 1.000 | `discovery/discovery_t1_both.json` : `fixed_order.2_walk_contrasts[0]` |
| t1, mode both: [2 among walks] C-PR′ (λ=0.5) − C-PR′ (λ=0) on H_q(I_A) | +0.0222 [+0.0195, +0.0254]; share of resamples above 0 1.000 | `discovery/discovery_t1_both.json` : `fixed_order.2_walk_contrasts[1]` |
| t1, mode both: [2 among walks] C-PR′ (λ=0.5) − AWP′ on H_q(I_T) | -0.0406 [-0.0442, -0.0371]; share of resamples above 0 0.000 | `discovery/discovery_t1_both.json` : `fixed_order.2_walk_contrasts[2]` |
| t1, mode both: [2 among walks] C-PR′ (λ=0.5) − AWP′ on H_q(I_A) | -0.0901 [-0.0967, -0.0832]; share of resamples above 0 0.000 | `discovery/discovery_t1_both.json` : `fixed_order.2_walk_contrasts[3]` |
| t1, mode both: [2 among walks] C-PR′ (λ=0.5) − C-PR′ (λ=1) on H_q(I_T) | +0.0592 [+0.0551, +0.0629]; share of resamples above 0 1.000 | `discovery/discovery_t1_both.json` : `fixed_order.2_walk_contrasts[4]` |
| t1, mode both: [2 among walks] C-PR′ (λ=0.5) − C-PR′ (λ=1) on H_q(I_A) | +0.0262 [+0.0202, +0.0317]; share of resamples above 0 1.000 | `discovery/discovery_t1_both.json` : `fixed_order.2_walk_contrasts[5]` |
| t1, mode both: [2 among walks] C-PR′ (λ=0.5) − EndorseRank′ on H_q(I_T) | +0.0592 [+0.0551, +0.0628]; share of resamples above 0 1.000 | `discovery/discovery_t1_both.json` : `fixed_order.2_walk_contrasts[6]` |
| t1, mode both: [2 among walks] C-PR′ (λ=0.5) − EndorseRank′ on H_q(I_A) | +0.0256 [+0.0197, +0.0312]; share of resamples above 0 1.000 | `discovery/discovery_t1_both.json` : `fixed_order.2_walk_contrasts[7]` |
| t1, mode both: [2 among walks] S-PR′ − C-PR′ (λ=0) on H_q(I_T) | +0.0006 [+0.0005, +0.0009]; share of resamples above 0 1.000 | `discovery/discovery_t1_both.json` : `fixed_order.2_walk_contrasts[8]` |
| t1, mode both: [2 among walks] S-PR′ − C-PR′ (λ=0) on H_q(I_A) | +0.0073 [+0.0059, +0.0090]; share of resamples above 0 1.000 | `discovery/discovery_t1_both.json` : `fixed_order.2_walk_contrasts[9]` |
| t1, mode both: [3 λ] C-PR′ (λ=0.25) D1 on H_q(I_T) | +0.0566 [+0.0523, +0.0606]; share of resamples above 0 1.000 | `discovery/discovery_t1_both.json` : `fixed_order.3_lambda.cpr_l25.i_t@q.D1` |
| t1, mode both: [3 λ] C-PR′ (λ=0.25) D2 on H_q(I_T) | -0.0166 [-0.0204, -0.0129]; share of resamples above 0 0.000 | `discovery/discovery_t1_both.json` : `fixed_order.3_lambda.cpr_l25.i_t@q.D2` |
| t1, mode both: [3 λ] C-PR′ (λ=0.25) minus C-PR′ (λ=0.5) on H_q(I_T) | -0.0008 [-0.0011, -0.0005]; share of resamples above 0 0.000 | `discovery/discovery_t1_both.json` : `fixed_order.3_lambda.cpr_l25.i_t@q.vs_cpr_l50` |
| t1, mode both: [3 λ] C-PR′ (λ=0.25) D1 on H_q(I_A) | +0.0209 [+0.0142, +0.0268]; share of resamples above 0 1.000 | `discovery/discovery_t1_both.json` : `fixed_order.3_lambda.cpr_l25.i_a@q.D1` |
| t1, mode both: [3 λ] C-PR′ (λ=0.25) D2 on H_q(I_A) | -0.1031 [-0.1102, -0.0953]; share of resamples above 0 0.000 | `discovery/discovery_t1_both.json` : `fixed_order.3_lambda.cpr_l25.i_a@q.D2` |
| t1, mode both: [3 λ] C-PR′ (λ=0.25) minus C-PR′ (λ=0.5) on H_q(I_A) | -0.0021 [-0.0027, -0.0016]; share of resamples above 0 0.000 | `discovery/discovery_t1_both.json` : `fixed_order.3_lambda.cpr_l25.i_a@q.vs_cpr_l50` |
| t1, mode both: [3 λ] C-PR′ (λ=0.75) D1 on H_q(I_T) | +0.0578 [+0.0535, +0.0612]; share of resamples above 0 1.000 | `discovery/discovery_t1_both.json` : `fixed_order.3_lambda.cpr_l75.i_t@q.D1` |
| t1, mode both: [3 λ] C-PR′ (λ=0.75) D2 on H_q(I_T) | -0.0155 [-0.0194, -0.0119]; share of resamples above 0 0.000 | `discovery/discovery_t1_both.json` : `fixed_order.3_lambda.cpr_l75.i_t@q.D2` |
| t1, mode both: [3 λ] C-PR′ (λ=0.75) minus C-PR′ (λ=0.5) on H_q(I_T) | +0.0003 [-0.0001, +0.0007]; share of resamples above 0 0.917 | `discovery/discovery_t1_both.json` : `fixed_order.3_lambda.cpr_l75.i_t@q.vs_cpr_l50` |
| t1, mode both: [3 λ] C-PR′ (λ=0.75) D1 on H_q(I_A) | +0.0234 [+0.0169, +0.0295]; share of resamples above 0 1.000 | `discovery/discovery_t1_both.json` : `fixed_order.3_lambda.cpr_l75.i_a@q.D1` |
| t1, mode both: [3 λ] C-PR′ (λ=0.75) D2 on H_q(I_A) | -0.1006 [-0.1079, -0.0928]; share of resamples above 0 0.000 | `discovery/discovery_t1_both.json` : `fixed_order.3_lambda.cpr_l75.i_a@q.D2` |
| t1, mode both: [3 λ] C-PR′ (λ=0.75) minus C-PR′ (λ=0.5) on H_q(I_A) | +0.0004 [-0.0002, +0.0010]; share of resamples above 0 0.917 | `discovery/discovery_t1_both.json` : `fixed_order.3_lambda.cpr_l75.i_a@q.vs_cpr_l50` |
| t1, mode both: [4 Cho] D1 on H_q(IB_U) | +0.0309 [+0.0239, +0.0372]; share of resamples above 0 1.000 | `discovery/discovery_t1_both.json` : `fixed_order.4_cho.hot_sets.ib_u@q.D1` |
| t1, mode both: [4 Cho] D2 on H_q(IB_U) | -0.4689 [-0.4762, -0.4617]; share of resamples above 0 0.000 | `discovery/discovery_t1_both.json` : `fixed_order.4_cho.hot_sets.ib_u@q.D2` |
| t1, mode both: [4 Cho] D1 on H_q(IR) | +0.5536 [+0.5482, +0.5593]; share of resamples above 0 1.000 | `discovery/discovery_t1_both.json` : `fixed_order.4_cho.hot_sets.ir@q.D1` |
| t1, mode both: [4 Cho] D2 on H_q(IR) | +0.4931 [+0.4856, +0.4998]; share of resamples above 0 1.000 | `discovery/discovery_t1_both.json` : `fixed_order.4_cho.hot_sets.ir@q.D2` |
| t1, mode both: [4 Cho] replication contrast C-PR′ − IB′_U on H_q(IB_U) | -0.4689 [-0.4762, -0.4617]; share of resamples above 0 0.000 | `discovery/discovery_t1_both.json` : `fixed_order.4_cho.replication_contrast` |
| t1, mode both: [5 sensitivity x=0.05] D1 on H_q(I_T) | +0.0734 [+0.0687, +0.0776]; share of resamples above 0 1.000 | `discovery/discovery_t1_both.json` : `fixed_order.5_sensitivities.x.x=0.05.i_t@q.D1` |
| t1, mode both: [5 sensitivity x=0.05] D2 on H_q(I_T) | +0.0082 [+0.0046, +0.0118]; share of resamples above 0 1.000 | `discovery/discovery_t1_both.json` : `fixed_order.5_sensitivities.x.x=0.05.i_t@q.D2` |
| t1, mode both: [5 sensitivity x=0.05] D1 on H_q(I_A) | +0.0762 [+0.0701, +0.0820]; share of resamples above 0 1.000 | `discovery/discovery_t1_both.json` : `fixed_order.5_sensitivities.x.x=0.05.i_a@q.D1` |
| t1, mode both: [5 sensitivity x=0.05] D2 on H_q(I_A) | -0.0140 [-0.0198, -0.0072]; share of resamples above 0 0.000 | `discovery/discovery_t1_both.json` : `fixed_order.5_sensitivities.x.x=0.05.i_a@q.D2` |
| t1, mode both: [5 sensitivity x=0.2] D1 on H_q(I_T) | +0.0280 [+0.0245, +0.0311]; share of resamples above 0 1.000 | `discovery/discovery_t1_both.json` : `fixed_order.5_sensitivities.x.x=0.2.i_t@q.D1` |
| t1, mode both: [5 sensitivity x=0.2] D2 on H_q(I_T) | -0.0135 [-0.0167, -0.0107]; share of resamples above 0 0.000 | `discovery/discovery_t1_both.json` : `fixed_order.5_sensitivities.x.x=0.2.i_t@q.D2` |
| t1, mode both: [5 sensitivity x=0.2] D1 on H_q(I_A) | -0.0417 [-0.0492, -0.0350]; share of resamples above 0 0.000 | `discovery/discovery_t1_both.json` : `fixed_order.5_sensitivities.x.x=0.2.i_a@q.D1` |
| t1, mode both: [5 sensitivity x=0.2] D2 on H_q(I_A) | -0.1623 [-0.1702, -0.1551]; share of resamples above 0 0.000 | `discovery/discovery_t1_both.json` : `fixed_order.5_sensitivities.x.x=0.2.i_a@q.D2` |
| t1, mode both: [5 sensitivity secondary q] q | 0.050 | `discovery/discovery_t1_both.json` : `fixed_order.5_sensitivities.q_secondary.q` |
| t1, mode both: [5 sensitivity secondary q] D1 on H_q2(I_T) | +0.0161 [+0.0150, +0.0173]; share of resamples above 0 1.000 | `discovery/discovery_t1_both.json` : `fixed_order.5_sensitivities.q_secondary.i_t@q2.D1` |
| t1, mode both: [5 sensitivity secondary q] D2 on H_q2(I_T) | -0.0116 [-0.0130, -0.0104]; share of resamples above 0 0.000 | `discovery/discovery_t1_both.json` : `fixed_order.5_sensitivities.q_secondary.i_t@q2.D2` |
| t1, mode both: [5 sensitivity secondary q] D1 on H_q2(I_A) | +0.0230 [+0.0164, +0.0291]; share of resamples above 0 1.000 | `discovery/discovery_t1_both.json` : `fixed_order.5_sensitivities.q_secondary.i_a@q2.D1` |
| t1, mode both: [5 sensitivity secondary q] D2 on H_q2(I_A) | -0.1010 [-0.1083, -0.0933]; share of resamples above 0 0.000 | `discovery/discovery_t1_both.json` : `fixed_order.5_sensitivities.q_secondary.i_a@q2.D2` |
| t1, mode both: [5 sensitivity no hubs] hubs | 1,016 | `discovery/discovery_t1_both.json` : `fixed_order.5_sensitivities.no_hubs.hubs` |
| t1, mode both: [5 sensitivity no hubs] D1 on H_q(I_T) without hubs | +0.0360 [+0.0328, +0.0398]; share of resamples above 0 1.000 | `discovery/discovery_t1_both.json` : `fixed_order.5_sensitivities.no_hubs.i_t@q-nohubs.D1` |
| t1, mode both: [5 sensitivity no hubs] D2 on H_q(I_T) without hubs | -0.0219 [-0.0256, -0.0180]; share of resamples above 0 0.000 | `discovery/discovery_t1_both.json` : `fixed_order.5_sensitivities.no_hubs.i_t@q-nohubs.D2` |
| t1, mode both: [5 sensitivity no hubs] D1 on H_q(I_A) without hubs | +0.0116 [+0.0053, +0.0179]; share of resamples above 0 1.000 | `discovery/discovery_t1_both.json` : `fixed_order.5_sensitivities.no_hubs.i_a@q-nohubs.D1` |
| t1, mode both: [5 sensitivity no hubs] D2 on H_q(I_A) without hubs | -0.1064 [-0.1137, -0.0994]; share of resamples above 0 0.000 | `discovery/discovery_t1_both.json` : `fixed_order.5_sensitivities.no_hubs.i_a@q-nohubs.D2` |
| t1, mode both: [5 sensitivity importance by counts] D1 on H_q(N_T) | +0.0229 [+0.0205, +0.0255]; share of resamples above 0 1.000 | `discovery/discovery_t1_both.json` : `fixed_order.5_sensitivities.importance_counts.n_t@q.D1` |
| t1, mode both: [5 sensitivity importance by counts] D2 on H_q(N_T) | -0.0445 [-0.0476, -0.0410]; share of resamples above 0 0.000 | `discovery/discovery_t1_both.json` : `fixed_order.5_sensitivities.importance_counts.n_t@q.D2` |
| t1, mode both: [5 sensitivity importance by counts] D1 on H_q(N_A) | +0.0491 [+0.0406, +0.0575]; share of resamples above 0 1.000 | `discovery/discovery_t1_both.json` : `fixed_order.5_sensitivities.importance_counts.n_a@q.D1` |
| t1, mode both: [5 sensitivity importance by counts] D2 on H_q(N_A) | -0.0731 [-0.0830, -0.0651]; share of resamples above 0 0.000 | `discovery/discovery_t1_both.json` : `fixed_order.5_sensitivities.importance_counts.n_a@q.D2` |
| t1, mode both: [5 sensitivity seed bootstrap] D1 on H_q(I_T) | +0.0574 [+0.0347, +0.0757]; share of resamples above 0 1.000 | `discovery/discovery_t1_both.json` : `fixed_order.5_sensitivities.seed_bootstrap.i_t@q.D1` |
| t1, mode both: [5 sensitivity seed bootstrap] D2 on H_q(I_T) | -0.0158 [-0.0299, -0.0012]; share of resamples above 0 0.018 | `discovery/discovery_t1_both.json` : `fixed_order.5_sensitivities.seed_bootstrap.i_t@q.D2` |
| t1, mode both: [5 sensitivity seed bootstrap] D1 on H_q(I_A) | +0.0230 [-0.0325, +0.0681]; share of resamples above 0 0.797 | `discovery/discovery_t1_both.json` : `fixed_order.5_sensitivities.seed_bootstrap.i_a@q.D1` |
| t1, mode both: [5 sensitivity seed bootstrap] D2 on H_q(I_A) | -0.1010 [-0.1343, -0.0667]; share of resamples above 0 0.000 | `discovery/discovery_t1_both.json` : `fixed_order.5_sensitivities.seed_bootstrap.i_a@q.D2` |
| t1, mode both: [5 sensitivity ρ/4] ρ and seeds | 1/200, 5 seeds | `discovery/discovery_t1_both.json` : `fixed_order.5_sensitivities.rho_quarter` |
| t1, mode both: [5 sensitivity ρ/4] D1 on H_q(I_T) | +0.0585 [+0.0542, +0.0621]; share of resamples above 0 1.000 | `discovery/discovery_t1_both.json` : `fixed_order.5_sensitivities.rho_quarter.contrasts.i_t@q.D1` |
| t1, mode both: [5 sensitivity ρ/4] D2 on H_q(I_T) | -0.0282 [-0.0322, -0.0245]; share of resamples above 0 0.000 | `discovery/discovery_t1_both.json` : `fixed_order.5_sensitivities.rho_quarter.contrasts.i_t@q.D2` |
| t1, mode both: [5 sensitivity ρ/4] D1 on H_q(I_A) | +0.0256 [+0.0190, +0.0317]; share of resamples above 0 1.000 | `discovery/discovery_t1_both.json` : `fixed_order.5_sensitivities.rho_quarter.contrasts.i_a@q.D1` |
| t1, mode both: [5 sensitivity ρ/4] D2 on H_q(I_A) | -0.1292 [-0.1370, -0.1213]; share of resamples above 0 0.000 | `discovery/discovery_t1_both.json` : `fixed_order.5_sensitivities.rho_quarter.contrasts.i_a@q.D2` |
| t1, mode both: share of picks decided by a tie, breadth-first | 0.0000 | `discovery/discovery_t1_both.json` : `diagnostics.ties.bfs` |
| t1, mode both: share of picks decided by a tie, random | 0.0000 | `discovery/discovery_t1_both.json` : `diagnostics.ties.random` |
| t1, mode both: share of picks decided by a tie, IB′_A (allowance backlinks) | 0.9999 | `discovery/discovery_t1_both.json` : `diagnostics.ties.ib_a` |
| t1, mode both: share of picks decided by a tie, IB′_T (transfer backlinks) | 0.9998 | `discovery/discovery_t1_both.json` : `diagnostics.ties.ib_t` |
| t1, mode both: share of picks decided by a tie, IB′_U (contract backlinks) | 0.9997 | `discovery/discovery_t1_both.json` : `diagnostics.ties.ib_u` |
| t1, mode both: share of picks decided by a tie, EndorseRank′ | 0.9988 | `discovery/discovery_t1_both.json` : `diagnostics.ties.endorserank` |
| t1, mode both: share of picks decided by a tie, EndorseRank-activity′ | 0.9890 | `discovery/discovery_t1_both.json` : `diagnostics.ties.endorserank_activity` |
| t1, mode both: share of picks decided by a tie, AWP′ | 0.2835 | `discovery/discovery_t1_both.json` : `diagnostics.ties.awp` |
| t1, mode both: share of picks decided by a tie, C-PR′ (λ=0.5) | 0.5645 | `discovery/discovery_t1_both.json` : `diagnostics.ties.cpr_l50` |
| t1, mode both: share of picks decided by a tie, C-PR′ (λ=0.25) | 0.5637 | `discovery/discovery_t1_both.json` : `diagnostics.ties.cpr_l25` |
| t1, mode both: share of picks decided by a tie, C-PR′ (λ=0.75) | 0.5646 | `discovery/discovery_t1_both.json` : `diagnostics.ties.cpr_l75` |
| t1, mode both: share of picks decided by a tie, C-PR′ (λ=1) | 0.9995 | `discovery/discovery_t1_both.json` : `diagnostics.ties.cpr_l100` |
| t1, mode both: share of picks decided by a tie, C-PR′ (λ=0) | 0.5630 | `discovery/discovery_t1_both.json` : `diagnostics.ties.cpr_l0` |
| t1, mode both: share of picks decided by a tie, S-PR′ | 0.5628 | `discovery/discovery_t1_both.json` : `diagnostics.ties.spr` |
| t1, mode both: share of picks decided by a tie, δ′ (diagnostic) | 0.6464 | `discovery/discovery_t1_both.json` : `diagnostics.ties.delta` |
| t1, mode both: wasted visits of breadth-first (first 1%, first 10%) | 0.8439, 0.7709 | `discovery/discovery_t1_both.json` : `diagnostics.wasted_visits.bfs` |
| t1, mode both: wasted visits of random (first 1%, first 10%) | 0.7819, 0.6887 | `discovery/discovery_t1_both.json` : `diagnostics.wasted_visits.random` |
| t1, mode both: wasted visits of IB′_A (allowance backlinks) (first 1%, first 10%) | 0.8326, 0.8074 | `discovery/discovery_t1_both.json` : `diagnostics.wasted_visits.ib_a` |
| t1, mode both: wasted visits of IB′_T (transfer backlinks) (first 1%, first 10%) | 0.6349, 0.8426 | `discovery/discovery_t1_both.json` : `diagnostics.wasted_visits.ib_t` |
| t1, mode both: wasted visits of IB′_U (contract backlinks) (first 1%, first 10%) | 0.6316, 0.8331 | `discovery/discovery_t1_both.json` : `diagnostics.wasted_visits.ib_u` |
| t1, mode both: wasted visits of EndorseRank′ (first 1%, first 10%) | 0.8327, 0.8077 | `discovery/discovery_t1_both.json` : `diagnostics.wasted_visits.endorserank` |
| t1, mode both: wasted visits of EndorseRank-activity′ (first 1%, first 10%) | 0.6737, 0.8062 | `discovery/discovery_t1_both.json` : `diagnostics.wasted_visits.endorserank_activity` |
| t1, mode both: wasted visits of AWP′ (first 1%, first 10%) | 0.4508, 0.8241 | `discovery/discovery_t1_both.json` : `diagnostics.wasted_visits.awp` |
| t1, mode both: wasted visits of C-PR′ (λ=0.5) (first 1%, first 10%) | 0.6942, 0.9206 | `discovery/discovery_t1_both.json` : `diagnostics.wasted_visits.cpr_l50` |
| t1, mode both: wasted visits of C-PR′ (λ=0.25) (first 1%, first 10%) | 0.7004, 0.9211 | `discovery/discovery_t1_both.json` : `diagnostics.wasted_visits.cpr_l25` |
| t1, mode both: wasted visits of C-PR′ (λ=0.75) (first 1%, first 10%) | 0.6895, 0.9196 | `discovery/discovery_t1_both.json` : `diagnostics.wasted_visits.cpr_l75` |
| t1, mode both: wasted visits of C-PR′ (λ=1) (first 1%, first 10%) | 0.8327, 0.8077 | `discovery/discovery_t1_both.json` : `diagnostics.wasted_visits.cpr_l100` |
| t1, mode both: wasted visits of C-PR′ (λ=0) (first 1%, first 10%) | 0.7256, 0.9228 | `discovery/discovery_t1_both.json` : `diagnostics.wasted_visits.cpr_l0` |
| t1, mode both: wasted visits of S-PR′ (first 1%, first 10%) | 0.7206, 0.9212 | `discovery/discovery_t1_both.json` : `diagnostics.wasted_visits.spr` |
| t1, mode both: wasted visits of δ′ (diagnostic) (first 1%, first 10%) | 0.5283, 0.8034 | `discovery/discovery_t1_both.json` : `diagnostics.wasted_visits.delta` |
| t1, mode both: hubs | 1,016 | `discovery/discovery_t1_both.json` : `diagnostics.hubs` |
| t1, mode both: largest hub | 0x085b48ca6908dceafb4fae56c90709e1537ec9a7 with IB_U 439,299 | `discovery/discovery_t1_both.json` : `diagnostics.hubs[0]` |
| t1, mode both: median over hubs of the mean visit index, breadth-first | 63,790.8 | `discovery/discovery_t1_both.json` : `diagnostics.hub_visits.bfs.mean` |
| t1, mode both: median over hubs of the mean visit index, random | 267,450.5 | `discovery/discovery_t1_both.json` : `diagnostics.hub_visits.random.mean` |
| t1, mode both: median over hubs of the mean visit index, IB′_A (allowance backlinks) | 61,678.8 | `discovery/discovery_t1_both.json` : `diagnostics.hub_visits.ib_a.mean` |
| t1, mode both: median over hubs of the mean visit index, IB′_T (transfer backlinks) | 29,633.7 | `discovery/discovery_t1_both.json` : `diagnostics.hub_visits.ib_t.mean` |
| t1, mode both: median over hubs of the mean visit index, IB′_U (contract backlinks) | 18,495.2 | `discovery/discovery_t1_both.json` : `diagnostics.hub_visits.ib_u.mean` |
| t1, mode both: median over hubs of the mean visit index, EndorseRank′ | 62,223.7 | `discovery/discovery_t1_both.json` : `diagnostics.hub_visits.endorserank.mean` |
| t1, mode both: median over hubs of the mean visit index, EndorseRank-activity′ | 72,853.1 | `discovery/discovery_t1_both.json` : `diagnostics.hub_visits.endorserank_activity.mean` |
| t1, mode both: median over hubs of the mean visit index, AWP′ | 851.400 | `discovery/discovery_t1_both.json` : `diagnostics.hub_visits.awp.mean` |
| t1, mode both: median over hubs of the mean visit index, C-PR′ (λ=0.5) | 3,605.3 | `discovery/discovery_t1_both.json` : `diagnostics.hub_visits.cpr_l50.mean` |
| t1, mode both: median over hubs of the mean visit index, C-PR′ (λ=0.25) | 3,692.8 | `discovery/discovery_t1_both.json` : `diagnostics.hub_visits.cpr_l25.mean` |
| t1, mode both: median over hubs of the mean visit index, C-PR′ (λ=0.75) | 3,736.4 | `discovery/discovery_t1_both.json` : `diagnostics.hub_visits.cpr_l75.mean` |
| t1, mode both: median over hubs of the mean visit index, C-PR′ (λ=1) | 62,205.9 | `discovery/discovery_t1_both.json` : `diagnostics.hub_visits.cpr_l100.mean` |
| t1, mode both: median over hubs of the mean visit index, C-PR′ (λ=0) | 4,395.1 | `discovery/discovery_t1_both.json` : `diagnostics.hub_visits.cpr_l0.mean` |
| t1, mode both: median over hubs of the mean visit index, S-PR′ | 4,073.9 | `discovery/discovery_t1_both.json` : `diagnostics.hub_visits.spr.mean` |
| t1, mode both: median over hubs of the mean visit index, δ′ (diagnostic) | 1,360.8 | `discovery/discovery_t1_both.json` : `diagnostics.hub_visits.delta.mean` |
| t1, mode both: coverage, contracts | 715,480 | `discovery/discovery_t1_both.json` : `diagnostics.coverage.contracts` |
| t1, mode both: coverage, outside g | 109,094 | `discovery/discovery_t1_both.json` : `diagnostics.coverage.outside_g` |
| t1, mode both: coverage, inflow untyped usd | 1,373,560,052.4 | `discovery/discovery_t1_both.json` : `diagnostics.coverage.inflow_untyped_usd` |
| t1, mode both: coverage of I_T, total (USD) | 16,622,706,250.4 | `discovery/discovery_t1_both.json` : `diagnostics.coverage.i_t.total` |
| t1, mode both: coverage of I_T, share held by the universe | 0.9695 | `discovery/discovery_t1_both.json` : `diagnostics.coverage.i_t.share_U` |
| t1, mode both: coverage of I_T, share in scc | 0.7409 | `discovery/discovery_t1_both.json` : `diagnostics.coverage.i_t.share_by_part.scc` |
| t1, mode both: coverage of I_T, share in in | 0.0905 | `discovery/discovery_t1_both.json` : `diagnostics.coverage.i_t.share_by_part.in` |
| t1, mode both: coverage of I_T, share in out | 0.0660 | `discovery/discovery_t1_both.json` : `diagnostics.coverage.i_t.share_by_part.out` |
| t1, mode both: coverage of I_T, share in other | 0.0949 | `discovery/discovery_t1_both.json` : `diagnostics.coverage.i_t.share_by_part.other` |
| t1, mode both: coverage of I_T, share in isolated | 0.0050 | `discovery/discovery_t1_both.json` : `diagnostics.coverage.i_t.share_by_part.isolated` |
| t1, mode both: coverage of I_T, share in outside g | 0.0028 | `discovery/discovery_t1_both.json` : `diagnostics.coverage.i_t.share_by_part.outside_g` |
| t1, mode both: coverage of I_T, top 1% of rows: rows | 7,155 | `discovery/discovery_t1_both.json` : `diagnostics.coverage.i_t.top_1pct.rows` |
| t1, mode both: coverage of I_T, top 1% of rows: share in U | 0.6483 | `discovery/discovery_t1_both.json` : `diagnostics.coverage.i_t.top_1pct.share_in_U` |
| t1, mode both: coverage of I_T, top 1% of rows: tied at cut | 11,490 | `discovery/discovery_t1_both.json` : `diagnostics.coverage.i_t.top_1pct.tied_at_cut` |
| t1, mode both: coverage of I_T, top 1% of rows: slots at cut | 1,386 | `discovery/discovery_t1_both.json` : `diagnostics.coverage.i_t.top_1pct.slots_at_cut` |
| t1, mode both: coverage of I_A, total (USD) | 343,843,976.1 | `discovery/discovery_t1_both.json` : `diagnostics.coverage.i_a.total` |
| t1, mode both: coverage of I_A, share held by the universe | 0.9376 | `discovery/discovery_t1_both.json` : `diagnostics.coverage.i_a.share_U` |
| t1, mode both: coverage of I_A, share in scc | 0.4913 | `discovery/discovery_t1_both.json` : `diagnostics.coverage.i_a.share_by_part.scc` |
| t1, mode both: coverage of I_A, share in in | 0.0261 | `discovery/discovery_t1_both.json` : `diagnostics.coverage.i_a.share_by_part.in` |
| t1, mode both: coverage of I_A, share in out | 0.3819 | `discovery/discovery_t1_both.json` : `diagnostics.coverage.i_a.share_by_part.out` |
| t1, mode both: coverage of I_A, share in other | 0.0628 | `discovery/discovery_t1_both.json` : `diagnostics.coverage.i_a.share_by_part.other` |
| t1, mode both: coverage of I_A, share in isolated | 0.0332 | `discovery/discovery_t1_both.json` : `diagnostics.coverage.i_a.share_by_part.isolated` |
| t1, mode both: coverage of I_A, share in outside g | 0.0048 | `discovery/discovery_t1_both.json` : `diagnostics.coverage.i_a.share_by_part.outside_g` |
| t1, mode both: coverage of I_A, top 1% of rows: rows | 7,155 | `discovery/discovery_t1_both.json` : `diagnostics.coverage.i_a.top_1pct.rows` |
| t1, mode both: coverage of I_A, top 1% of rows: share in U | 0.3464 | `discovery/discovery_t1_both.json` : `diagnostics.coverage.i_a.top_1pct.share_in_U` |
| t1, mode both: coverage of I_A, top 1% of rows: tied at cut | 241 | `discovery/discovery_t1_both.json` : `diagnostics.coverage.i_a.top_1pct.tied_at_cut` |
| t1, mode both: coverage of I_A, top 1% of rows: slots at cut | 7 | `discovery/discovery_t1_both.json` : `diagnostics.coverage.i_a.top_1pct.slots_at_cut` |
| t1, mode both: crawls of bfs@1/200 | 5 crawls, 184.289 s, 1,829.4 recomputes, 0.000 solves, 0.000 iterations (means per crawl but the seconds) | `discovery/discovery_t1_both.json` : `runs.bfs@1/200` |
| t1, mode both: crawls of bfs@1/50 | 20 crawls, 168.071 s, 532.950 recomputes, 0.000 solves, 0.000 iterations (means per crawl but the seconds) | `discovery/discovery_t1_both.json` : `runs.bfs@1/50` |
| t1, mode both: crawls of random@1/200 | 5 crawls, 1,404.5 s, 1,015,866 recomputes, 0.000 solves, 0.000 iterations (means per crawl but the seconds) | `discovery/discovery_t1_both.json` : `runs.random@1/200` |
| t1, mode both: crawls of random@1/50 | 20 crawls, 5,926.2 s, 1,015,866 recomputes, 0.000 solves, 0.000 iterations (means per crawl but the seconds) | `discovery/discovery_t1_both.json` : `runs.random@1/50` |
| t1, mode both: crawls of ib_a@1/200 | 5 crawls, 922.096 s, 1,829.6 recomputes, 0.000 solves, 0.000 iterations (means per crawl but the seconds) | `discovery/discovery_t1_both.json` : `runs.ib_a@1/200` |
| t1, mode both: crawls of ib_a@1/50 | 20 crawls, 787.200 s, 532.600 recomputes, 0.000 solves, 0.000 iterations (means per crawl but the seconds) | `discovery/discovery_t1_both.json` : `runs.ib_a@1/50` |
| t1, mode both: crawls of ib_t@1/200 | 5 crawls, 531.846 s, 1,829 recomputes, 0.000 solves, 0.000 iterations (means per crawl but the seconds) | `discovery/discovery_t1_both.json` : `runs.ib_t@1/200` |
| t1, mode both: crawls of ib_t@1/50 | 20 crawls, 448.957 s, 532.000 recomputes, 0.000 solves, 0.000 iterations (means per crawl but the seconds) | `discovery/discovery_t1_both.json` : `runs.ib_t@1/50` |
| t1, mode both: crawls of ib_u@1/200 | 5 crawls, 420.123 s, 1,828 recomputes, 0.000 solves, 0.000 iterations (means per crawl but the seconds) | `discovery/discovery_t1_both.json` : `runs.ib_u@1/200` |
| t1, mode both: crawls of ib_u@1/50 | 20 crawls, 442.825 s, 532.000 recomputes, 0.000 solves, 0.000 iterations (means per crawl but the seconds) | `discovery/discovery_t1_both.json` : `runs.ib_u@1/50` |
| t1, mode both: crawls of endorserank@1/200 | 5 crawls, 2,141.6 s, 1,829.6 recomputes, 1,829.6 solves, 3,350.4 iterations (means per crawl but the seconds) | `discovery/discovery_t1_both.json` : `runs.endorserank@1/200` |
| t1, mode both: crawls of endorserank@1/50 | 20 crawls, 3,211.8 s, 532.600 recomputes, 532.600 solves, 1,236.9 iterations (means per crawl but the seconds) | `discovery/discovery_t1_both.json` : `runs.endorserank@1/50` |
| t1, mode both: crawls of endorserank_activity@1/200 | 5 crawls, 6,186.3 s, 1,829.6 recomputes, 1,829.6 solves, 30,353 iterations (means per crawl but the seconds) | `discovery/discovery_t1_both.json` : `runs.endorserank_activity@1/200` |
| t1, mode both: crawls of endorserank_activity@1/50 | 20 crawls, 9,703.2 s, 532.600 recomputes, 532.600 solves, 12,620.4 iterations (means per crawl but the seconds) | `discovery/discovery_t1_both.json` : `runs.endorserank_activity@1/50` |
| t1, mode both: crawls of awp@1/200 | 5 crawls, 41,580.6 s, 1,830 recomputes, 1,830 solves, 68,010.4 iterations (means per crawl but the seconds) | `discovery/discovery_t1_both.json` : `runs.awp@1/200` |
| t1, mode both: crawls of awp@1/50 | 20 crawls, 51,465.8 s, 534.000 recomputes, 534.000 solves, 25,454.8 iterations (means per crawl but the seconds) | `discovery/discovery_t1_both.json` : `runs.awp@1/50` |
| t1, mode both: crawls of cpr_l50@1/200 | 5 crawls, 19,164.5 s, 1,828 recomputes, 1,828 solves, 52,926.8 iterations (means per crawl but the seconds) | `discovery/discovery_t1_both.json` : `runs.cpr_l50@1/200` |
| t1, mode both: crawls of cpr_l50@1/50 | 20 crawls, 26,745.2 s, 532.000 recomputes, 532.000 solves, 21,724.5 iterations (means per crawl but the seconds) | `discovery/discovery_t1_both.json` : `runs.cpr_l50@1/50` |
| t1, mode both: crawls of cpr_l25@1/200 | 5 crawls, 19,852.0 s, 1,828 recomputes, 1,828 solves, 54,181.8 iterations (means per crawl but the seconds) | `discovery/discovery_t1_both.json` : `runs.cpr_l25@1/200` |
| t1, mode both: crawls of cpr_l25@1/50 | 20 crawls, 27,149.4 s, 532.000 recomputes, 532.000 solves, 22,198.3 iterations (means per crawl but the seconds) | `discovery/discovery_t1_both.json` : `runs.cpr_l25@1/50` |
| t1, mode both: crawls of cpr_l75@1/200 | 5 crawls, 21,247.5 s, 1,828 recomputes, 1,828 solves, 52,334 iterations (means per crawl but the seconds) | `discovery/discovery_t1_both.json` : `runs.cpr_l75@1/200` |
| t1, mode both: crawls of cpr_l75@1/50 | 20 crawls, 25,782.7 s, 532.000 recomputes, 532.000 solves, 21,471.2 iterations (means per crawl but the seconds) | `discovery/discovery_t1_both.json` : `runs.cpr_l75@1/50` |
| t1, mode both: crawls of cpr_l100@1/200 | 5 crawls, 2,470.5 s, 1,829.6 recomputes, 1,829.6 solves, 3,346.8 iterations (means per crawl but the seconds) | `discovery/discovery_t1_both.json` : `runs.cpr_l100@1/200` |
| t1, mode both: crawls of cpr_l100@1/50 | 20 crawls, 2,081.2 s, 532.600 recomputes, 532.600 solves, 1,236.2 iterations (means per crawl but the seconds) | `discovery/discovery_t1_both.json` : `runs.cpr_l100@1/50` |
| t1, mode both: crawls of cpr_l0@1/200 | 5 crawls, 19,885.1 s, 1,829 recomputes, 1,829 solves, 55,782.4 iterations (means per crawl but the seconds) | `discovery/discovery_t1_both.json` : `runs.cpr_l0@1/200` |
| t1, mode both: crawls of cpr_l0@1/50 | 20 crawls, 20,619.2 s, 532.000 recomputes, 532.000 solves, 23,096.0 iterations (means per crawl but the seconds) | `discovery/discovery_t1_both.json` : `runs.cpr_l0@1/50` |
| t1, mode both: crawls of spr@1/200 | 5 crawls, 23,497.6 s, 1,828 recomputes, 3,656 solves, 60,897.6 iterations (means per crawl but the seconds) | `discovery/discovery_t1_both.json` : `runs.spr@1/200` |
| t1, mode both: crawls of spr@1/50 | 20 crawls, 26,554.6 s, 532.000 recomputes, 1,064 solves, 24,991.5 iterations (means per crawl but the seconds) | `discovery/discovery_t1_both.json` : `runs.spr@1/50` |
| t1, mode both: crawls of delta@1/200 | 5 crawls, 546.390 s, 1,828 recomputes, 0.000 solves, 0.000 iterations (means per crawl but the seconds) | `discovery/discovery_t1_both.json` : `runs.delta@1/200` |
| t1, mode both: crawls of delta@1/50 | 20 crawls, 477.716 s, 532.000 recomputes, 0.000 solves, 0.000 iterations (means per crawl but the seconds) | `discovery/discovery_t1_both.json` : `runs.delta@1/50` |
| t1, mode both: invariant all visited | yes | `discovery/discovery_t1_both.json` : `invariants.all_visited` |
| t1, mode both: invariant final walks within | 1e-09 | `discovery/discovery_t1_both.json` : `invariants.final_walks_within` |
| t1, mode both: invariant max final diff | 8.33e-17 | `discovery/discovery_t1_both.json` : `invariants.max_final_diff` |

### Run t1, mode out

| Quantity | Value | Source |
|---|---|---|
| t1, mode out: decides | no | `discovery/discovery_t1_out.json` : `decides` |
| t1, mode out: is primary | no | `discovery/discovery_t1_out.json` : `is_primary` |
| t1, mode out: primary mode | both | `discovery/discovery_t1_out.json` : `primary_mode` |
| t1, mode out: created at | 2026-11-11T01:46:58+00:00 | `discovery/discovery_t1_out.json` : `created_at` |
| t1, mode out: seconds | 4,944.1 | `discovery/discovery_t1_out.json` : `seconds` |
| t1, mode out: workers | 16 | `discovery/discovery_t1_out.json` : `workers` |
| t1, mode out: protocol rho | 1/50 | `discovery/discovery_t1_out.json` : `protocol.rho` |
| t1, mode out: protocol q | 1/100 | `discovery/discovery_t1_out.json` : `protocol.q` |
| t1, mode out: protocol q_secondary | 0.05 | `discovery/discovery_t1_out.json` : `protocol.q_secondary` |
| t1, mode out: protocol decision_covers | ['few_capped_allowance_in_edges'] | `discovery/discovery_t1_out.json` : `protocol.decision_covers` |
| t1, mode out: code revision | b005f903a7c30be627b923609f35ff290a8cd56d | `discovery/discovery_t1_out.json` : `provenance.head` |
| t1, mode out: sizes of the graph, g_nodes | 1,403,959 | `discovery/discovery_t1_out.json` : `sizes.graph.g_nodes` |
| t1, mode out: sizes of the graph, allow_pairs | 17,940 | `discovery/discovery_t1_out.json` : `sizes.graph.allow_pairs` |
| t1, mode out: sizes of the graph, transfer_pairs | 2,269,073 | `discovery/discovery_t1_out.json` : `sizes.graph.transfer_pairs` |
| t1, mode out: sizes of the graph, nodes | 1,111,554 | `discovery/discovery_t1_out.json` : `sizes.graph.nodes` |
| t1, mode out: sizes of the graph, edges | 2,269,421 | `discovery/discovery_t1_out.json` : `sizes.graph.edges` |
| t1, mode out: sizes of the graph, scc | 222,592 | `discovery/discovery_t1_out.json` : `sizes.graph.scc` |
| t1, mode out: sizes of the graph, in | 169,237 | `discovery/discovery_t1_out.json` : `sizes.graph.in` |
| t1, mode out: sizes of the graph, out | 109,804 | `discovery/discovery_t1_out.json` : `sizes.graph.out` |
| t1, mode out: sizes of the graph, other | 609,921 | `discovery/discovery_t1_out.json` : `sizes.graph.other` |
| t1, mode out: sizes of the graph, U | 332,396 | `discovery/discovery_t1_out.json` : `sizes.graph.U` |
| t1, mode out: sizes of the graph, E_U | 1,283,946 | `discovery/discovery_t1_out.json` : `sizes.graph.E_U` |
| t1, mode out: sizes of the graph, WCC | 1,015,867 | `discovery/discovery_t1_out.json` : `sizes.graph.WCC` |
| t1, mode out: sizes of the graph, E_WCC | 2,121,895 | `discovery/discovery_t1_out.json` : `sizes.graph.E_WCC` |
| t1, mode out: sizes of the universe, U | 332,396 | `discovery/discovery_t1_out.json` : `sizes.universe.U` |
| t1, mode out: sizes of the universe, E_U | 1,283,946 | `discovery/discovery_t1_out.json` : `sizes.universe.E_U` |
| t1, mode out: sizes of the universe, allow_pairs | 14,618 | `discovery/discovery_t1_out.json` : `sizes.universe.allow_pairs` |
| t1, mode out: sizes of the universe, transfer_pairs | 1,285,637 | `discovery/discovery_t1_out.json` : `sizes.universe.transfer_pairs` |
| t1, mode out: contracts in H_q(I_T) | 3,324 | `discovery/discovery_t1_out.json` : `hot_sets.i_t@q` |
| t1, mode out: contracts in H_q(I_A) | 3,324 | `discovery/discovery_t1_out.json` : `hot_sets.i_a@q` |
| t1, mode out: contracts in H_q(N_T) | 3,664 | `discovery/discovery_t1_out.json` : `hot_sets.n_t@q` |
| t1, mode out: contracts in H_q(N_A) | 3,653 | `discovery/discovery_t1_out.json` : `hot_sets.n_a@q` |
| t1, mode out: contracts in H_q(IB_U) | 3,362 | `discovery/discovery_t1_out.json` : `hot_sets.ib_u@q` |
| t1, mode out: contracts in H_q(IR) | 3,324 | `discovery/discovery_t1_out.json` : `hot_sets.ir@q` |
| t1, mode out: contracts in H_q2(I_T) | 16,620 | `discovery/discovery_t1_out.json` : `hot_sets.i_t@q2` |
| t1, mode out: contracts in H_q(I_T) without hubs | 3,085 | `discovery/discovery_t1_out.json` : `hot_sets.i_t@q-nohubs` |
| t1, mode out: contracts in H_q2(I_A) | 5,751 | `discovery/discovery_t1_out.json` : `hot_sets.i_a@q2` |
| t1, mode out: contracts in H_q(I_A) without hubs | 3,265 | `discovery/discovery_t1_out.json` : `hot_sets.i_a@q-nohubs` |
| t1, mode out: D1 = C-PR′ − BFS on H_q(I_T) | +0.3414 [+0.3282, +0.3547]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `decision.i_t.D1` |
| t1, mode out: D2 = C-PR′ − IB′_U on H_q(I_T) | +0.1222 [+0.1079, +0.1361]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `decision.i_t.D2` |
| t1, mode out: contrasts on I_T with the interval above 0 | D1, D2 | `discovery/discovery_t1_out.json` : `decision.i_t.above_zero` |
| t1, mode out: contrasts on I_T with the interval below 0 | none | `discovery/discovery_t1_out.json` : `decision.i_t.below_zero` |
| t1, mode out: D1 = C-PR′ − BFS on H_q(I_A) | +0.1705 [+0.1564, +0.1822]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `decision.i_a.D1` |
| t1, mode out: D2 = C-PR′ − IB′_U on H_q(I_A) | +0.0739 [+0.0607, +0.0848]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `decision.i_a.D2` |
| t1, mode out: contrasts on I_A with the interval above 0 | D1, D2 | `discovery/discovery_t1_out.json` : `decision.i_a.above_zero` |
| t1, mode out: contrasts on I_A with the interval below 0 | none | `discovery/discovery_t1_out.json` : `decision.i_a.below_zero` |
| t1, mode out: AUC of breadth-first on H_q(I_T) | 0.1269 [0.1228, 0.1313]; seeds 0.0003 to 0.4025 | `discovery/discovery_t1_out.json` : `auc.i_t@q.bfs.x=0.1` |
| t1, mode out: AUC of random on H_q(I_T) | 0.1169 [0.1141, 0.1198]; seeds 0.0007 to 0.2674 | `discovery/discovery_t1_out.json` : `auc.i_t@q.random.x=0.1` |
| t1, mode out: AUC of IB′_A (allowance backlinks) on H_q(I_T) | 0.1750 [0.1696, 0.1806]; seeds 0.0007 to 0.4767 | `discovery/discovery_t1_out.json` : `auc.i_t@q.ib_a.x=0.1` |
| t1, mode out: AUC of IB′_T (transfer backlinks) on H_q(I_T) | 0.3460 [0.3370, 0.3560]; seeds 0.0024 to 0.5484 | `discovery/discovery_t1_out.json` : `auc.i_t@q.ib_t.x=0.1` |
| t1, mode out: AUC of IB′_U (contract backlinks) on H_q(I_T) | 0.3461 [0.3371, 0.3559]; seeds 0.0024 to 0.5486 | `discovery/discovery_t1_out.json` : `auc.i_t@q.ib_u.x=0.1` |
| t1, mode out: AUC of EndorseRank′ on H_q(I_T) | 0.1733 [0.1679, 0.1790]; seeds 0.0007 to 0.4767 | `discovery/discovery_t1_out.json` : `auc.i_t@q.endorserank.x=0.1` |
| t1, mode out: AUC of EndorseRank-activity′ on H_q(I_T) | 0.1734 [0.1680, 0.1790]; seeds 0.0007 to 0.4771 | `discovery/discovery_t1_out.json` : `auc.i_t@q.endorserank_activity.x=0.1` |
| t1, mode out: AUC of AWP′ on H_q(I_T) | 0.4766 [0.4608, 0.4919]; seeds 0.4763 to 0.4769 | `discovery/discovery_t1_out.json` : `auc.i_t@q.awp.x=0.1` |
| t1, mode out: AUC of C-PR′ (λ=0.5) on H_q(I_T) | 0.4683 [0.4538, 0.4824]; seeds 0.4256 to 0.4918 | `discovery/discovery_t1_out.json` : `auc.i_t@q.cpr_l50.x=0.1` |
| t1, mode out: AUC of C-PR′ (λ=0.25) on H_q(I_T) | 0.4817 [0.4665, 0.4962]; seeds 0.4548 to 0.4962 | `discovery/discovery_t1_out.json` : `auc.i_t@q.cpr_l25.x=0.1` |
| t1, mode out: AUC of C-PR′ (λ=0.75) on H_q(I_T) | 0.4562 [0.4413, 0.4711]; seeds 0.4116 to 0.4812 | `discovery/discovery_t1_out.json` : `auc.i_t@q.cpr_l75.x=0.1` |
| t1, mode out: AUC of C-PR′ (λ=1) on H_q(I_T) | 0.1728 [0.1674, 0.1785]; seeds 0.0007 to 0.4767 | `discovery/discovery_t1_out.json` : `auc.i_t@q.cpr_l100.x=0.1` |
| t1, mode out: AUC of C-PR′ (λ=0) on H_q(I_T) | 0.4818 [0.4666, 0.4970]; seeds 0.4579 to 0.4950 | `discovery/discovery_t1_out.json` : `auc.i_t@q.cpr_l0.x=0.1` |
| t1, mode out: AUC of S-PR′ on H_q(I_T) | 0.4874 [0.4721, 0.5015]; seeds 0.4696 to 0.4973 | `discovery/discovery_t1_out.json` : `auc.i_t@q.spr.x=0.1` |
| t1, mode out: AUC of δ′ (diagnostic) on H_q(I_T) | 0.5795 [0.5654, 0.5933]; seeds 0.5793 to 0.5799 | `discovery/discovery_t1_out.json` : `auc.i_t@q.delta.x=0.1` |
| t1, mode out: AUC of reference: C-PR of the full graph on H_q(I_T) | 0.3239 [0.3092, 0.3393]; seeds 0.3239 to 0.3239 | `discovery/discovery_t1_out.json` : `auc.i_t@q.ref_cpr.x=0.1` |
| t1, mode out: AUC of reference: union in-degree of the full graph on H_q(I_T) | 0.5826 [0.5680, 0.5978]; seeds 0.5826 to 0.5826 | `discovery/discovery_t1_out.json` : `auc.i_t@q.ref_ib_u.x=0.1` |
| t1, mode out: AUC of reference: ideal order on H_q(I_T) | 0.9500 [0.9491, 0.9510]; seeds 0.9500 to 0.9500 | `discovery/discovery_t1_out.json` : `auc.i_t@q.ref_ideal.x=0.1` |
| t1, mode out: AUC of reference: random curve on H_q(I_T) | 0.0500 | `discovery/discovery_t1_out.json` : `auc.i_t@q.random_curve.x=0.1` |
| t1, mode out: AUC of reference: ideal curve on H_q(I_T) | 0.9500 | `discovery/discovery_t1_out.json` : `auc.i_t@q.ideal_curve.x=0.1` |
| t1, mode out: AUC of breadth-first on H_q(I_A) | 0.0595 [0.0572, 0.0626]; seeds 0.0003 to 0.2290 | `discovery/discovery_t1_out.json` : `auc.i_a@q.bfs.x=0.1` |
| t1, mode out: AUC of random on H_q(I_A) | 0.0703 [0.0678, 0.0727]; seeds 0.0003 to 0.1827 | `discovery/discovery_t1_out.json` : `auc.i_a@q.random.x=0.1` |
| t1, mode out: AUC of IB′_A (allowance backlinks) on H_q(I_A) | 0.1076 [0.1031, 0.1134]; seeds 0.0006 to 0.2913 | `discovery/discovery_t1_out.json` : `auc.i_a@q.ib_a.x=0.1` |
| t1, mode out: AUC of IB′_T (transfer backlinks) on H_q(I_A) | 0.1478 [0.1406, 0.1554]; seeds 0.0006 to 0.2376 | `discovery/discovery_t1_out.json` : `auc.i_a@q.ib_t.x=0.1` |
| t1, mode out: AUC of IB′_U (contract backlinks) on H_q(I_A) | 0.1561 [0.1481, 0.1638]; seeds 0.0006 to 0.2506 | `discovery/discovery_t1_out.json` : `auc.i_a@q.ib_u.x=0.1` |
| t1, mode out: AUC of EndorseRank′ on H_q(I_A) | 0.1068 [0.1024, 0.1122]; seeds 0.0006 to 0.2913 | `discovery/discovery_t1_out.json` : `auc.i_a@q.endorserank.x=0.1` |
| t1, mode out: AUC of EndorseRank-activity′ on H_q(I_A) | 0.1066 [0.1022, 0.1121]; seeds 0.0006 to 0.2904 | `discovery/discovery_t1_out.json` : `auc.i_a@q.endorserank_activity.x=0.1` |
| t1, mode out: AUC of AWP′ on H_q(I_A) | 0.2231 [0.2096, 0.2363]; seeds 0.2229 to 0.2232 | `discovery/discovery_t1_out.json` : `auc.i_a@q.awp.x=0.1` |
| t1, mode out: AUC of C-PR′ (λ=0.5) on H_q(I_A) | 0.2300 [0.2160, 0.2417]; seeds 0.2040 to 0.2443 | `discovery/discovery_t1_out.json` : `auc.i_a@q.cpr_l50.x=0.1` |
| t1, mode out: AUC of C-PR′ (λ=0.25) on H_q(I_A) | 0.2349 [0.2216, 0.2469]; seeds 0.2155 to 0.2455 | `discovery/discovery_t1_out.json` : `auc.i_a@q.cpr_l25.x=0.1` |
| t1, mode out: AUC of C-PR′ (λ=0.75) on H_q(I_A) | 0.2197 [0.2058, 0.2316]; seeds 0.1995 to 0.2309 | `discovery/discovery_t1_out.json` : `auc.i_a@q.cpr_l75.x=0.1` |
| t1, mode out: AUC of C-PR′ (λ=1) on H_q(I_A) | 0.1063 [0.1018, 0.1120]; seeds 0.0006 to 0.2914 | `discovery/discovery_t1_out.json` : `auc.i_a@q.cpr_l100.x=0.1` |
| t1, mode out: AUC of C-PR′ (λ=0) on H_q(I_A) | 0.2020 [0.1895, 0.2133]; seeds 0.1842 to 0.2118 | `discovery/discovery_t1_out.json` : `auc.i_a@q.cpr_l0.x=0.1` |
| t1, mode out: AUC of S-PR′ on H_q(I_A) | 0.2360 [0.2227, 0.2481]; seeds 0.2266 to 0.2414 | `discovery/discovery_t1_out.json` : `auc.i_a@q.spr.x=0.1` |
| t1, mode out: AUC of δ′ (diagnostic) on H_q(I_A) | 0.2937 [0.2801, 0.3054]; seeds 0.2936 to 0.2939 | `discovery/discovery_t1_out.json` : `auc.i_a@q.delta.x=0.1` |
| t1, mode out: AUC of reference: C-PR of the full graph on H_q(I_A) | 0.1773 [0.1636, 0.1886]; seeds 0.1773 to 0.1773 | `discovery/discovery_t1_out.json` : `auc.i_a@q.ref_cpr.x=0.1` |
| t1, mode out: AUC of reference: union in-degree of the full graph on H_q(I_A) | 0.2846 [0.2718, 0.2964]; seeds 0.2846 to 0.2846 | `discovery/discovery_t1_out.json` : `auc.i_a@q.ref_ib_u.x=0.1` |
| t1, mode out: AUC of reference: ideal order on H_q(I_A) | 0.9500 [0.9491, 0.9509]; seeds 0.9500 to 0.9500 | `discovery/discovery_t1_out.json` : `auc.i_a@q.ref_ideal.x=0.1` |
| t1, mode out: AUC of reference: random curve on H_q(I_A) | 0.0500 | `discovery/discovery_t1_out.json` : `auc.i_a@q.random_curve.x=0.1` |
| t1, mode out: AUC of reference: ideal curve on H_q(I_A) | 0.9500 | `discovery/discovery_t1_out.json` : `auc.i_a@q.ideal_curve.x=0.1` |
| t1, mode out: [1 walk′ against its count] EndorseRank′ − IB′_A (allowance backlinks) on H_q(I_T) | -0.0017 [-0.0020, -0.0014]; share of resamples above 0 0.000 | `discovery/discovery_t1_out.json` : `fixed_order.1_walk_vs_count[0]` |
| t1, mode out: [1 walk′ against its count] EndorseRank′ − IB′_A (allowance backlinks) on H_q(I_A) | -0.0008 [-0.0011, -0.0006]; share of resamples above 0 0.000 | `discovery/discovery_t1_out.json` : `fixed_order.1_walk_vs_count[1]` |
| t1, mode out: [1 walk′ against its count] EndorseRank-activity′ − IB′_A (allowance backlinks) on H_q(I_T) | -0.0016 [-0.0020, -0.0013]; share of resamples above 0 0.000 | `discovery/discovery_t1_out.json` : `fixed_order.1_walk_vs_count[2]` |
| t1, mode out: [1 walk′ against its count] EndorseRank-activity′ − IB′_A (allowance backlinks) on H_q(I_A) | -0.0010 [-0.0012, -0.0008]; share of resamples above 0 0.000 | `discovery/discovery_t1_out.json` : `fixed_order.1_walk_vs_count[3]` |
| t1, mode out: [1 walk′ against its count] C-PR′ (λ=1) − IB′_A (allowance backlinks) on H_q(I_T) | -0.0022 [-0.0025, -0.0019]; share of resamples above 0 0.000 | `discovery/discovery_t1_out.json` : `fixed_order.1_walk_vs_count[4]` |
| t1, mode out: [1 walk′ against its count] C-PR′ (λ=1) − IB′_A (allowance backlinks) on H_q(I_A) | -0.0013 [-0.0015, -0.0010]; share of resamples above 0 0.000 | `discovery/discovery_t1_out.json` : `fixed_order.1_walk_vs_count[5]` |
| t1, mode out: [1 walk′ against its count] AWP′ − IB′_T (transfer backlinks) on H_q(I_T) | +0.1307 [+0.1167, +0.1456]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.1_walk_vs_count[6]` |
| t1, mode out: [1 walk′ against its count] AWP′ − IB′_T (transfer backlinks) on H_q(I_A) | +0.0752 [+0.0624, +0.0870]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.1_walk_vs_count[7]` |
| t1, mode out: [1 walk′ against its count] C-PR′ (λ=0) − IB′_T (transfer backlinks) on H_q(I_T) | +0.1358 [+0.1216, +0.1504]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.1_walk_vs_count[8]` |
| t1, mode out: [1 walk′ against its count] C-PR′ (λ=0) − IB′_T (transfer backlinks) on H_q(I_A) | +0.0542 [+0.0418, +0.0657]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.1_walk_vs_count[9]` |
| t1, mode out: [1 walk′ against its count] C-PR′ (λ=0.5) − IB′_A (allowance backlinks) on H_q(I_T) | +0.2933 [+0.2799, +0.3052]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.1_walk_vs_count[10]` |
| t1, mode out: [1 walk′ against its count] C-PR′ (λ=0.5) − IB′_A (allowance backlinks) on H_q(I_A) | +0.1224 [+0.1103, +0.1331]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.1_walk_vs_count[11]` |
| t1, mode out: [1 walk′ against its count] C-PR′ (λ=0.5) − IB′_T (transfer backlinks) on H_q(I_T) | +0.1223 [+0.1078, +0.1363]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.1_walk_vs_count[12]` |
| t1, mode out: [1 walk′ against its count] C-PR′ (λ=0.5) − IB′_T (transfer backlinks) on H_q(I_A) | +0.0822 [+0.0682, +0.0937]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.1_walk_vs_count[13]` |
| t1, mode out: [2 among walks] C-PR′ (λ=0.5) − C-PR′ (λ=0) on H_q(I_T) | -0.0135 [-0.0182, -0.0090]; share of resamples above 0 0.000 | `discovery/discovery_t1_out.json` : `fixed_order.2_walk_contrasts[0]` |
| t1, mode out: [2 among walks] C-PR′ (λ=0.5) − C-PR′ (λ=0) on H_q(I_A) | +0.0280 [+0.0213, +0.0350]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.2_walk_contrasts[1]` |
| t1, mode out: [2 among walks] C-PR′ (λ=0.5) − AWP′ on H_q(I_T) | -0.0084 [-0.0182, +0.0028]; share of resamples above 0 0.068 | `discovery/discovery_t1_out.json` : `fixed_order.2_walk_contrasts[2]` |
| t1, mode out: [2 among walks] C-PR′ (λ=0.5) − AWP′ on H_q(I_A) | +0.0070 [-0.0029, +0.0167]; share of resamples above 0 0.910 | `discovery/discovery_t1_out.json` : `fixed_order.2_walk_contrasts[3]` |
| t1, mode out: [2 among walks] C-PR′ (λ=0.5) − C-PR′ (λ=1) on H_q(I_T) | +0.2955 [+0.2820, +0.3074]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.2_walk_contrasts[4]` |
| t1, mode out: [2 among walks] C-PR′ (λ=0.5) − C-PR′ (λ=1) on H_q(I_A) | +0.1237 [+0.1116, +0.1343]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.2_walk_contrasts[5]` |
| t1, mode out: [2 among walks] C-PR′ (λ=0.5) − EndorseRank′ on H_q(I_T) | +0.2950 [+0.2816, +0.3070]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.2_walk_contrasts[6]` |
| t1, mode out: [2 among walks] C-PR′ (λ=0.5) − EndorseRank′ on H_q(I_A) | +0.1233 [+0.1112, +0.1340]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.2_walk_contrasts[7]` |
| t1, mode out: [2 among walks] S-PR′ − C-PR′ (λ=0) on H_q(I_T) | +0.0056 [+0.0034, +0.0078]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.2_walk_contrasts[8]` |
| t1, mode out: [2 among walks] S-PR′ − C-PR′ (λ=0) on H_q(I_A) | +0.0341 [+0.0283, +0.0398]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.2_walk_contrasts[9]` |
| t1, mode out: [3 λ] C-PR′ (λ=0.25) D1 on H_q(I_T) | +0.3547 [+0.3420, +0.3683]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.3_lambda.cpr_l25.i_t@q.D1` |
| t1, mode out: [3 λ] C-PR′ (λ=0.25) D2 on H_q(I_T) | +0.1356 [+0.1211, +0.1499]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.3_lambda.cpr_l25.i_t@q.D2` |
| t1, mode out: [3 λ] C-PR′ (λ=0.25) minus C-PR′ (λ=0.5) on H_q(I_T) | +0.0134 [+0.0112, +0.0159]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.3_lambda.cpr_l25.i_t@q.vs_cpr_l50` |
| t1, mode out: [3 λ] C-PR′ (λ=0.25) D1 on H_q(I_A) | +0.1754 [+0.1622, +0.1873]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.3_lambda.cpr_l25.i_a@q.D1` |
| t1, mode out: [3 λ] C-PR′ (λ=0.25) D2 on H_q(I_A) | +0.0788 [+0.0652, +0.0897]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.3_lambda.cpr_l25.i_a@q.D2` |
| t1, mode out: [3 λ] C-PR′ (λ=0.25) minus C-PR′ (λ=0.5) on H_q(I_A) | +0.0049 [+0.0032, +0.0067]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.3_lambda.cpr_l25.i_a@q.vs_cpr_l50` |
| t1, mode out: [3 λ] C-PR′ (λ=0.75) D1 on H_q(I_T) | +0.3293 [+0.3152, +0.3427]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.3_lambda.cpr_l75.i_t@q.D1` |
| t1, mode out: [3 λ] C-PR′ (λ=0.75) D2 on H_q(I_T) | +0.1101 [+0.0960, +0.1245]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.3_lambda.cpr_l75.i_t@q.D2` |
| t1, mode out: [3 λ] C-PR′ (λ=0.75) minus C-PR′ (λ=0.5) on H_q(I_T) | -0.0120 [-0.0142, -0.0101]; share of resamples above 0 0.000 | `discovery/discovery_t1_out.json` : `fixed_order.3_lambda.cpr_l75.i_t@q.vs_cpr_l50` |
| t1, mode out: [3 λ] C-PR′ (λ=0.75) D1 on H_q(I_A) | +0.1602 [+0.1462, +0.1716]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.3_lambda.cpr_l75.i_a@q.D1` |
| t1, mode out: [3 λ] C-PR′ (λ=0.75) D2 on H_q(I_A) | +0.0636 [+0.0507, +0.0739]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.3_lambda.cpr_l75.i_a@q.D2` |
| t1, mode out: [3 λ] C-PR′ (λ=0.75) minus C-PR′ (λ=0.5) on H_q(I_A) | -0.0103 [-0.0125, -0.0086]; share of resamples above 0 0.000 | `discovery/discovery_t1_out.json` : `fixed_order.3_lambda.cpr_l75.i_a@q.vs_cpr_l50` |
| t1, mode out: [4 Cho] D1 on H_q(IB_U) | +0.2612 [+0.2480, +0.2761]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.4_cho.hot_sets.ib_u@q.D1` |
| t1, mode out: [4 Cho] D2 on H_q(IB_U) | -0.0877 [-0.1017, -0.0724]; share of resamples above 0 0.000 | `discovery/discovery_t1_out.json` : `fixed_order.4_cho.hot_sets.ib_u@q.D2` |
| t1, mode out: [4 Cho] D1 on H_q(IR) | +0.5467 [+0.5364, +0.5558]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.4_cho.hot_sets.ir@q.D1` |
| t1, mode out: [4 Cho] D2 on H_q(IR) | +0.4356 [+0.4263, +0.4442]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.4_cho.hot_sets.ir@q.D2` |
| t1, mode out: [4 Cho] replication contrast C-PR′ − IB′_U on H_q(IB_U) | -0.0877 [-0.1017, -0.0724]; share of resamples above 0 0.000 | `discovery/discovery_t1_out.json` : `fixed_order.4_cho.replication_contrast` |
| t1, mode out: [5 sensitivity x=0.05] D1 on H_q(I_T) | +0.3348 [+0.3211, +0.3481]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.5_sensitivities.x.x=0.05.i_t@q.D1` |
| t1, mode out: [5 sensitivity x=0.05] D2 on H_q(I_T) | +0.1181 [+0.1050, +0.1313]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.5_sensitivities.x.x=0.05.i_t@q.D2` |
| t1, mode out: [5 sensitivity x=0.05] D1 on H_q(I_A) | +0.1699 [+0.1575, +0.1808]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.5_sensitivities.x.x=0.05.i_a@q.D1` |
| t1, mode out: [5 sensitivity x=0.05] D2 on H_q(I_A) | +0.0808 [+0.0687, +0.0906]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.5_sensitivities.x.x=0.05.i_a@q.D2` |
| t1, mode out: [5 sensitivity x=0.2] D1 on H_q(I_T) | +0.2664 [+0.2525, +0.2805]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.5_sensitivities.x.x=0.2.i_t@q.D1` |
| t1, mode out: [5 sensitivity x=0.2] D2 on H_q(I_T) | +0.0588 [+0.0440, +0.0743]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.5_sensitivities.x.x=0.2.i_t@q.D2` |
| t1, mode out: [5 sensitivity x=0.2] D1 on H_q(I_A) | +0.1129 [+0.0978, +0.1258]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.5_sensitivities.x.x=0.2.i_a@q.D1` |
| t1, mode out: [5 sensitivity x=0.2] D2 on H_q(I_A) | +0.0134 [-0.0012, +0.0260]; share of resamples above 0 0.968 | `discovery/discovery_t1_out.json` : `fixed_order.5_sensitivities.x.x=0.2.i_a@q.D2` |
| t1, mode out: [5 sensitivity secondary q] q | 0.050 | `discovery/discovery_t1_out.json` : `fixed_order.5_sensitivities.q_secondary.q` |
| t1, mode out: [5 sensitivity secondary q] D1 on H_q2(I_T) | +0.0937 [+0.0893, +0.0982]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.5_sensitivities.q_secondary.i_t@q2.D1` |
| t1, mode out: [5 sensitivity secondary q] D2 on H_q2(I_T) | -0.0002 [-0.0057, +0.0043]; share of resamples above 0 0.458 | `discovery/discovery_t1_out.json` : `fixed_order.5_sensitivities.q_secondary.i_t@q2.D2` |
| t1, mode out: [5 sensitivity secondary q] D1 on H_q2(I_A) | +0.1371 [+0.1276, +0.1453]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.5_sensitivities.q_secondary.i_a@q2.D1` |
| t1, mode out: [5 sensitivity secondary q] D2 on H_q2(I_A) | +0.0397 [+0.0306, +0.0481]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.5_sensitivities.q_secondary.i_a@q2.D2` |
| t1, mode out: [5 sensitivity no hubs] hubs | 333 | `discovery/discovery_t1_out.json` : `fixed_order.5_sensitivities.no_hubs.hubs` |
| t1, mode out: [5 sensitivity no hubs] D1 on H_q(I_T) without hubs | +0.3193 [+0.3051, +0.3355]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.5_sensitivities.no_hubs.i_t@q-nohubs.D1` |
| t1, mode out: [5 sensitivity no hubs] D2 on H_q(I_T) without hubs | +0.1044 [+0.0886, +0.1229]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.5_sensitivities.no_hubs.i_t@q-nohubs.D2` |
| t1, mode out: [5 sensitivity no hubs] D1 on H_q(I_A) without hubs | +0.1614 [+0.1472, +0.1742]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.5_sensitivities.no_hubs.i_a@q-nohubs.D1` |
| t1, mode out: [5 sensitivity no hubs] D2 on H_q(I_A) without hubs | +0.0683 [+0.0547, +0.0816]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.5_sensitivities.no_hubs.i_a@q-nohubs.D2` |
| t1, mode out: [5 sensitivity importance by counts] D1 on H_q(N_T) | +0.2507 [+0.2371, +0.2632]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.5_sensitivities.importance_counts.n_t@q.D1` |
| t1, mode out: [5 sensitivity importance by counts] D2 on H_q(N_T) | +0.0296 [+0.0152, +0.0434]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.5_sensitivities.importance_counts.n_t@q.D2` |
| t1, mode out: [5 sensitivity importance by counts] D1 on H_q(N_A) | +0.1646 [+0.1538, +0.1762]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.5_sensitivities.importance_counts.n_a@q.D1` |
| t1, mode out: [5 sensitivity importance by counts] D2 on H_q(N_A) | +0.0682 [+0.0579, +0.0800]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.5_sensitivities.importance_counts.n_a@q.D2` |
| t1, mode out: [5 sensitivity seed bootstrap] D1 on H_q(I_T) | +0.3414 [+0.2850, +0.3953]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.5_sensitivities.seed_bootstrap.i_t@q.D1` |
| t1, mode out: [5 sensitivity seed bootstrap] D2 on H_q(I_T) | +0.1222 [+0.0362, +0.2177]; share of resamples above 0 0.995 | `discovery/discovery_t1_out.json` : `fixed_order.5_sensitivities.seed_bootstrap.i_t@q.D2` |
| t1, mode out: [5 sensitivity seed bootstrap] D1 on H_q(I_A) | +0.1705 [+0.1408, +0.2000]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.5_sensitivities.seed_bootstrap.i_a@q.D1` |
| t1, mode out: [5 sensitivity seed bootstrap] D2 on H_q(I_A) | +0.0739 [+0.0374, +0.1153]; share of resamples above 0 1.000 | `discovery/discovery_t1_out.json` : `fixed_order.5_sensitivities.seed_bootstrap.i_a@q.D2` |
| t1, mode out: share of picks decided by a tie, breadth-first | 0.0000 | `discovery/discovery_t1_out.json` : `diagnostics.ties.bfs` |
| t1, mode out: share of picks decided by a tie, random | 0.0000 | `discovery/discovery_t1_out.json` : `diagnostics.ties.random` |
| t1, mode out: share of picks decided by a tie, IB′_A (allowance backlinks) | 0.9998 | `discovery/discovery_t1_out.json` : `diagnostics.ties.ib_a` |
| t1, mode out: share of picks decided by a tie, IB′_T (transfer backlinks) | 0.9992 | `discovery/discovery_t1_out.json` : `diagnostics.ties.ib_t` |
| t1, mode out: share of picks decided by a tie, IB′_U (contract backlinks) | 0.9992 | `discovery/discovery_t1_out.json` : `diagnostics.ties.ib_u` |
| t1, mode out: share of picks decided by a tie, EndorseRank′ | 0.9963 | `discovery/discovery_t1_out.json` : `diagnostics.ties.endorserank` |
| t1, mode out: share of picks decided by a tie, EndorseRank-activity′ | 0.9960 | `discovery/discovery_t1_out.json` : `diagnostics.ties.endorserank_activity` |
| t1, mode out: share of picks decided by a tie, AWP′ | 0.0051 | `discovery/discovery_t1_out.json` : `diagnostics.ties.awp` |
| t1, mode out: share of picks decided by a tie, C-PR′ (λ=0.5) | 0.0223 | `discovery/discovery_t1_out.json` : `diagnostics.ties.cpr_l50` |
| t1, mode out: share of picks decided by a tie, C-PR′ (λ=0.25) | 0.0218 | `discovery/discovery_t1_out.json` : `diagnostics.ties.cpr_l25` |
| t1, mode out: share of picks decided by a tie, C-PR′ (λ=0.75) | 0.0242 | `discovery/discovery_t1_out.json` : `diagnostics.ties.cpr_l75` |
| t1, mode out: share of picks decided by a tie, C-PR′ (λ=1) | 0.9987 | `discovery/discovery_t1_out.json` : `diagnostics.ties.cpr_l100` |
| t1, mode out: share of picks decided by a tie, C-PR′ (λ=0) | 0.0217 | `discovery/discovery_t1_out.json` : `diagnostics.ties.cpr_l0` |
| t1, mode out: share of picks decided by a tie, S-PR′ | 0.0210 | `discovery/discovery_t1_out.json` : `diagnostics.ties.spr` |
| t1, mode out: share of picks decided by a tie, δ′ (diagnostic) | 0.2896 | `discovery/discovery_t1_out.json` : `diagnostics.ties.delta` |
| t1, mode out: wasted visits of breadth-first (first 1%, first 10%) | 0.8744, 0.8593 | `discovery/discovery_t1_out.json` : `diagnostics.wasted_visits.bfs` |
| t1, mode out: wasted visits of random (first 1%, first 10%) | 0.8119, 0.8195 | `discovery/discovery_t1_out.json` : `diagnostics.wasted_visits.random` |
| t1, mode out: wasted visits of IB′_A (allowance backlinks) (first 1%, first 10%) | 0.8387, 0.8405 | `discovery/discovery_t1_out.json` : `diagnostics.wasted_visits.ib_a` |
| t1, mode out: wasted visits of IB′_T (transfer backlinks) (first 1%, first 10%) | 0.5594, 0.8595 | `discovery/discovery_t1_out.json` : `diagnostics.wasted_visits.ib_t` |
| t1, mode out: wasted visits of IB′_U (contract backlinks) (first 1%, first 10%) | 0.5586, 0.8582 | `discovery/discovery_t1_out.json` : `diagnostics.wasted_visits.ib_u` |
| t1, mode out: wasted visits of EndorseRank′ (first 1%, first 10%) | 0.8387, 0.8526 | `discovery/discovery_t1_out.json` : `diagnostics.wasted_visits.endorserank` |
| t1, mode out: wasted visits of EndorseRank-activity′ (first 1%, first 10%) | 0.8387, 0.8526 | `discovery/discovery_t1_out.json` : `diagnostics.wasted_visits.endorserank_activity` |
| t1, mode out: wasted visits of AWP′ (first 1%, first 10%) | 0.4053, 0.6736 | `discovery/discovery_t1_out.json` : `diagnostics.wasted_visits.awp` |
| t1, mode out: wasted visits of C-PR′ (λ=0.5) (first 1%, first 10%) | 0.3995, 0.8703 | `discovery/discovery_t1_out.json` : `diagnostics.wasted_visits.cpr_l50` |
| t1, mode out: wasted visits of C-PR′ (λ=0.25) (first 1%, first 10%) | 0.4010, 0.8619 | `discovery/discovery_t1_out.json` : `diagnostics.wasted_visits.cpr_l25` |
| t1, mode out: wasted visits of C-PR′ (λ=0.75) (first 1%, first 10%) | 0.4002, 0.8899 | `discovery/discovery_t1_out.json` : `diagnostics.wasted_visits.cpr_l75` |
| t1, mode out: wasted visits of C-PR′ (λ=1) (first 1%, first 10%) | 0.8387, 0.8533 | `discovery/discovery_t1_out.json` : `diagnostics.wasted_visits.cpr_l100` |
| t1, mode out: wasted visits of C-PR′ (λ=0) (first 1%, first 10%) | 0.4304, 0.8662 | `discovery/discovery_t1_out.json` : `diagnostics.wasted_visits.cpr_l0` |
| t1, mode out: wasted visits of S-PR′ (first 1%, first 10%) | 0.4356, 0.8553 | `discovery/discovery_t1_out.json` : `diagnostics.wasted_visits.spr` |
| t1, mode out: wasted visits of δ′ (diagnostic) (first 1%, first 10%) | 0.3705, 0.6610 | `discovery/discovery_t1_out.json` : `diagnostics.wasted_visits.delta` |
| t1, mode out: hubs | 333 | `discovery/discovery_t1_out.json` : `diagnostics.hubs` |
| t1, mode out: largest hub | 0xfb64e79a562f7250131cf528242ceb10fdc82395 with IB_U 79,653 | `discovery/discovery_t1_out.json` : `diagnostics.hubs[0]` |
| t1, mode out: median over hubs of the mean visit index, breadth-first | 41,614.6 | `discovery/discovery_t1_out.json` : `diagnostics.hub_visits.bfs.mean` |
| t1, mode out: median over hubs of the mean visit index, random | 87,163.8 | `discovery/discovery_t1_out.json` : `diagnostics.hub_visits.random.mean` |
| t1, mode out: median over hubs of the mean visit index, IB′_A (allowance backlinks) | 43,654.5 | `discovery/discovery_t1_out.json` : `diagnostics.hub_visits.ib_a.mean` |
| t1, mode out: median over hubs of the mean visit index, IB′_T (transfer backlinks) | 28,961.6 | `discovery/discovery_t1_out.json` : `diagnostics.hub_visits.ib_t.mean` |
| t1, mode out: median over hubs of the mean visit index, IB′_U (contract backlinks) | 17,963 | `discovery/discovery_t1_out.json` : `diagnostics.hub_visits.ib_u.mean` |
| t1, mode out: median over hubs of the mean visit index, EndorseRank′ | 43,696.9 | `discovery/discovery_t1_out.json` : `diagnostics.hub_visits.endorserank.mean` |
| t1, mode out: median over hubs of the mean visit index, EndorseRank-activity′ | 43,696.9 | `discovery/discovery_t1_out.json` : `diagnostics.hub_visits.endorserank_activity.mean` |
| t1, mode out: median over hubs of the mean visit index, AWP′ | 345.800 | `discovery/discovery_t1_out.json` : `diagnostics.hub_visits.awp.mean` |
| t1, mode out: median over hubs of the mean visit index, C-PR′ (λ=0.5) | 781.500 | `discovery/discovery_t1_out.json` : `diagnostics.hub_visits.cpr_l50.mean` |
| t1, mode out: median over hubs of the mean visit index, C-PR′ (λ=0.25) | 785.600 | `discovery/discovery_t1_out.json` : `diagnostics.hub_visits.cpr_l25.mean` |
| t1, mode out: median over hubs of the mean visit index, C-PR′ (λ=0.75) | 753.100 | `discovery/discovery_t1_out.json` : `diagnostics.hub_visits.cpr_l75.mean` |
| t1, mode out: median over hubs of the mean visit index, C-PR′ (λ=1) | 43,699.2 | `discovery/discovery_t1_out.json` : `diagnostics.hub_visits.cpr_l100.mean` |
| t1, mode out: median over hubs of the mean visit index, C-PR′ (λ=0) | 698.000 | `discovery/discovery_t1_out.json` : `diagnostics.hub_visits.cpr_l0.mean` |
| t1, mode out: median over hubs of the mean visit index, S-PR′ | 688.700 | `discovery/discovery_t1_out.json` : `diagnostics.hub_visits.spr.mean` |
| t1, mode out: median over hubs of the mean visit index, δ′ (diagnostic) | 512.800 | `discovery/discovery_t1_out.json` : `diagnostics.hub_visits.delta.mean` |
| t1, mode out: coverage, contracts | 715,480 | `discovery/discovery_t1_out.json` : `diagnostics.coverage.contracts` |
| t1, mode out: coverage, outside g | 109,094 | `discovery/discovery_t1_out.json` : `diagnostics.coverage.outside_g` |
| t1, mode out: coverage, inflow untyped usd | 1,373,560,052.4 | `discovery/discovery_t1_out.json` : `diagnostics.coverage.inflow_untyped_usd` |
| t1, mode out: coverage of I_T, total (USD) | 16,622,706,250.4 | `discovery/discovery_t1_out.json` : `diagnostics.coverage.i_t.total` |
| t1, mode out: coverage of I_T, share held by the universe | 0.8069 | `discovery/discovery_t1_out.json` : `diagnostics.coverage.i_t.share_U` |
| t1, mode out: coverage of I_T, share in scc | 0.7409 | `discovery/discovery_t1_out.json` : `diagnostics.coverage.i_t.share_by_part.scc` |
| t1, mode out: coverage of I_T, share in in | 0.0905 | `discovery/discovery_t1_out.json` : `diagnostics.coverage.i_t.share_by_part.in` |
| t1, mode out: coverage of I_T, share in out | 0.0660 | `discovery/discovery_t1_out.json` : `diagnostics.coverage.i_t.share_by_part.out` |
| t1, mode out: coverage of I_T, share in other | 0.0949 | `discovery/discovery_t1_out.json` : `diagnostics.coverage.i_t.share_by_part.other` |
| t1, mode out: coverage of I_T, share in isolated | 0.0050 | `discovery/discovery_t1_out.json` : `diagnostics.coverage.i_t.share_by_part.isolated` |
| t1, mode out: coverage of I_T, share in outside g | 0.0028 | `discovery/discovery_t1_out.json` : `diagnostics.coverage.i_t.share_by_part.outside_g` |
| t1, mode out: coverage of I_T, top 1% of rows: rows | 7,155 | `discovery/discovery_t1_out.json` : `diagnostics.coverage.i_t.top_1pct.rows` |
| t1, mode out: coverage of I_T, top 1% of rows: share in U | 0.3250 | `discovery/discovery_t1_out.json` : `diagnostics.coverage.i_t.top_1pct.share_in_U` |
| t1, mode out: coverage of I_T, top 1% of rows: tied at cut | 11,490 | `discovery/discovery_t1_out.json` : `diagnostics.coverage.i_t.top_1pct.tied_at_cut` |
| t1, mode out: coverage of I_T, top 1% of rows: slots at cut | 1,386 | `discovery/discovery_t1_out.json` : `diagnostics.coverage.i_t.top_1pct.slots_at_cut` |
| t1, mode out: coverage of I_A, total (USD) | 343,843,976.1 | `discovery/discovery_t1_out.json` : `diagnostics.coverage.i_a.total` |
| t1, mode out: coverage of I_A, share held by the universe | 0.8732 | `discovery/discovery_t1_out.json` : `diagnostics.coverage.i_a.share_U` |
| t1, mode out: coverage of I_A, share in scc | 0.4913 | `discovery/discovery_t1_out.json` : `diagnostics.coverage.i_a.share_by_part.scc` |
| t1, mode out: coverage of I_A, share in in | 0.0261 | `discovery/discovery_t1_out.json` : `diagnostics.coverage.i_a.share_by_part.in` |
| t1, mode out: coverage of I_A, share in out | 0.3819 | `discovery/discovery_t1_out.json` : `diagnostics.coverage.i_a.share_by_part.out` |
| t1, mode out: coverage of I_A, share in other | 0.0628 | `discovery/discovery_t1_out.json` : `diagnostics.coverage.i_a.share_by_part.other` |
| t1, mode out: coverage of I_A, share in isolated | 0.0332 | `discovery/discovery_t1_out.json` : `diagnostics.coverage.i_a.share_by_part.isolated` |
| t1, mode out: coverage of I_A, share in outside g | 0.0048 | `discovery/discovery_t1_out.json` : `diagnostics.coverage.i_a.share_by_part.outside_g` |
| t1, mode out: coverage of I_A, top 1% of rows: rows | 7,155 | `discovery/discovery_t1_out.json` : `diagnostics.coverage.i_a.top_1pct.rows` |
| t1, mode out: coverage of I_A, top 1% of rows: share in U | 0.2367 | `discovery/discovery_t1_out.json` : `diagnostics.coverage.i_a.top_1pct.share_in_U` |
| t1, mode out: coverage of I_A, top 1% of rows: tied at cut | 241 | `discovery/discovery_t1_out.json` : `diagnostics.coverage.i_a.top_1pct.tied_at_cut` |
| t1, mode out: coverage of I_A, top 1% of rows: slots at cut | 7 | `discovery/discovery_t1_out.json` : `diagnostics.coverage.i_a.top_1pct.slots_at_cut` |
| t1, mode out: crawls of bfs@1/50 | 20 crawls, 78.337 s, 481.850 recomputes, 0.000 solves, 0.000 iterations (means per crawl but the seconds) | `discovery/discovery_t1_out.json` : `runs.bfs@1/50` |
| t1, mode out: crawls of random@1/50 | 20 crawls, 1,621.7 s, 332,395 recomputes, 0.000 solves, 0.000 iterations (means per crawl but the seconds) | `discovery/discovery_t1_out.json` : `runs.random@1/50` |
| t1, mode out: crawls of ib_a@1/50 | 20 crawls, 344.150 s, 482.500 recomputes, 0.000 solves, 0.000 iterations (means per crawl but the seconds) | `discovery/discovery_t1_out.json` : `runs.ib_a@1/50` |
| t1, mode out: crawls of ib_t@1/50 | 20 crawls, 222.636 s, 483.300 recomputes, 0.000 solves, 0.000 iterations (means per crawl but the seconds) | `discovery/discovery_t1_out.json` : `runs.ib_t@1/50` |
| t1, mode out: crawls of ib_u@1/50 | 20 crawls, 218.595 s, 483.650 recomputes, 0.000 solves, 0.000 iterations (means per crawl but the seconds) | `discovery/discovery_t1_out.json` : `runs.ib_u@1/50` |
| t1, mode out: crawls of endorserank@1/50 | 20 crawls, 1,011.5 s, 482.500 recomputes, 482.500 solves, 955.600 iterations (means per crawl but the seconds) | `discovery/discovery_t1_out.json` : `runs.endorserank@1/50` |
| t1, mode out: crawls of endorserank_activity@1/50 | 20 crawls, 2,506.7 s, 482.500 recomputes, 482.500 solves, 12,393.4 iterations (means per crawl but the seconds) | `discovery/discovery_t1_out.json` : `runs.endorserank_activity@1/50` |
| t1, mode out: crawls of awp@1/50 | 20 crawls, 16,131.1 s, 476.000 recomputes, 476.000 solves, 21,777 iterations (means per crawl but the seconds) | `discovery/discovery_t1_out.json` : `runs.awp@1/50` |
| t1, mode out: crawls of cpr_l50@1/50 | 20 crawls, 10,891.9 s, 476.000 recomputes, 476.000 solves, 21,197.9 iterations (means per crawl but the seconds) | `discovery/discovery_t1_out.json` : `runs.cpr_l50@1/50` |
| t1, mode out: crawls of cpr_l25@1/50 | 20 crawls, 11,194.0 s, 476.000 recomputes, 476.000 solves, 22,332.8 iterations (means per crawl but the seconds) | `discovery/discovery_t1_out.json` : `runs.cpr_l25@1/50` |
| t1, mode out: crawls of cpr_l75@1/50 | 20 crawls, 10,795.7 s, 476.000 recomputes, 476.000 solves, 20,460.7 iterations (means per crawl but the seconds) | `discovery/discovery_t1_out.json` : `runs.cpr_l75@1/50` |
| t1, mode out: crawls of cpr_l100@1/50 | 20 crawls, 998.807 s, 482.500 recomputes, 482.500 solves, 950.550 iterations (means per crawl but the seconds) | `discovery/discovery_t1_out.json` : `runs.cpr_l100@1/50` |
| t1, mode out: crawls of cpr_l0@1/50 | 20 crawls, 9,855.8 s, 476.000 recomputes, 476.000 solves, 24,027.9 iterations (means per crawl but the seconds) | `discovery/discovery_t1_out.json` : `runs.cpr_l0@1/50` |
| t1, mode out: crawls of spr@1/50 | 20 crawls, 10,588.8 s, 476.000 recomputes, 952.000 solves, 25,391.2 iterations (means per crawl but the seconds) | `discovery/discovery_t1_out.json` : `runs.spr@1/50` |
| t1, mode out: crawls of delta@1/50 | 20 crawls, 203.886 s, 477.000 recomputes, 0.000 solves, 0.000 iterations (means per crawl but the seconds) | `discovery/discovery_t1_out.json` : `runs.delta@1/50` |
| t1, mode out: invariant all visited | yes | `discovery/discovery_t1_out.json` : `invariants.all_visited` |
| t1, mode out: invariant final walks within | 1e-09 | `discovery/discovery_t1_out.json` : `invariants.final_walks_within` |
| t1, mode out: invariant max final diff | 0 | `discovery/discovery_t1_out.json` : `invariants.max_final_diff` |

### Structure pilot at t1 (before any score; protocol section 7)

| Quantity | Value | Source |
|---|---|---|
| Pilot: U | 332,396 | `discovery/feasibility_t1.json` : `U` |
| Pilot: E_U | 1,283,946 | `discovery/feasibility_t1.json` : `E_U` |
| Pilot: WCC | 1,015,867 | `discovery/feasibility_t1.json` : `WCC` |
| Pilot: E_WCC | 2,121,895 | `discovery/feasibility_t1.json` : `E_WCC` |
| Pilot: rho | 0.020 | `discovery/feasibility_t1.json` : `rho` |
| Pilot: q | 0.010 | `discovery/feasibility_t1.json` : `q` |
| Pilot: primary_mode | both | `discovery/feasibility_t1.json` : `primary_mode` |
| Pilot: stopped | yes | `discovery/feasibility_t1.json` : `stopped` |
| Pilot: allow capped edges | 17,905 | `discovery/feasibility_t1.json` : `layers.allow_capped.edges` |
| Pilot: allow capped nodes | 12,007 | `discovery/feasibility_t1.json` : `layers.allow_capped.nodes` |
| Pilot: allow capped self loops | 35 | `discovery/feasibility_t1.json` : `layers.allow_capped.self_loops` |
| Pilot: allow uncapped edges | 275,762 | `discovery/feasibility_t1.json` : `layers.allow_uncapped.edges` |
| Pilot: allow uncapped nodes | 224,785 | `discovery/feasibility_t1.json` : `layers.allow_uncapped.nodes` |
| Pilot: allow uncapped self loops | 155 | `discovery/feasibility_t1.json` : `layers.allow_uncapped.self_loops` |
| Pilot: transfer edges | 2,257,643 | `discovery/feasibility_t1.json` : `layers.transfer.edges` |
| Pilot: transfer nodes | 1,110,768 | `discovery/feasibility_t1.json` : `layers.transfer.nodes` |
| Pilot: transfer self loops | 11,430 | `discovery/feasibility_t1.json` : `layers.transfer.self_loops` |
| Pilot: bow-tie scc | 222,592 | `discovery/feasibility_t1.json` : `bow_tie.scc` |
| Pilot: bow-tie in | 169,237 | `discovery/feasibility_t1.json` : `bow_tie.in` |
| Pilot: bow-tie out | 109,804 | `discovery/feasibility_t1.json` : `bow_tie.out` |
| Pilot: bow-tie other | 609,921 | `discovery/feasibility_t1.json` : `bow_tie.other` |
| Pilot: share with a capped allowance in-edge, U | 0.0054 | `discovery/feasibility_t1.json` : `capped_allowance_in_edge_share.U` |
| Pilot: share with a capped allowance in-edge, U_from_U | 0.0053 | `discovery/feasibility_t1.json` : `capped_allowance_in_edge_share.U_from_U` |
| Pilot: projected hours at ρ = 0.01 | 12.49 | `discovery/feasibility_t1.json` : `rules.projected_hours.0.01` |
| Pilot: projected hours at ρ = 0.02 | 6.75 | `discovery/feasibility_t1.json` : `rules.projected_hours.0.02` |
| Pilot: projected hours at ρ = 0.05 | 2.98 | `discovery/feasibility_t1.json` : `rules.projected_hours.0.05` |
| Pilot: stop flag no rho within budget | no | `discovery/feasibility_t1.json` : `rules.stop.no_rho_within_budget` |
| Pilot: stop flag few capped allowance edges | no | `discovery/feasibility_t1.json` : `rules.stop.few_capped_allowance_edges` |
| Pilot: stop flag few capped allowance in edges | yes | `discovery/feasibility_t1.json` : `rules.stop.few_capped_allowance_in_edges` |

## 12. Allowances and the balance cap, importance, balance check, constants, prices, cost

| Quantity | Value | Source |
|---|---|---|
| Latest allowances between contracts at tobs, all five tokens: n latest positive | 339,282 | `describe/describe.json` : `allowances.tobs.total.n_latest_positive` |
| Latest allowances between contracts at tobs, all five tokens: n positive eff | 116,723 | `describe/describe.json` : `allowances.tobs.total.n_positive_eff` |
| Latest allowances between contracts at tobs, all five tokens: n capped to zero | 222,559 | `describe/describe.json` : `allowances.tobs.total.n_capped_to_zero` |
| Latest allowances between contracts at tobs, all five tokens: n capped below allowance | 114,454 | `describe/describe.json` : `allowances.tobs.total.n_capped_below_allowance` |
| Latest allowances between contracts at tobs, all five tokens: n unlimited | 223,892 | `describe/describe.json` : `allowances.tobs.total.n_unlimited` |
| Latest allowances between contracts at tobs, all five tokens: n finite | 115,390 | `describe/describe.json` : `allowances.tobs.total.n_finite` |
| Latest allowances between contracts at tobs, all five tokens: n eff at or above cap | 150 | `describe/describe.json` : `allowances.tobs.total.n_eff_at_or_above_cap` |
| Latest allowances between contracts at tobs, all five tokens: n allow at or above cap | 230,313 | `describe/describe.json` : `allowances.tobs.total.n_allow_at_or_above_cap` |
| Latest allowances between contracts at tobs, all five tokens: sum usd eff | 68,149,271.2 | `describe/describe.json` : `allowances.tobs.total.sum_usd_eff` |
| Latest allowances between contracts at tobs, all five tokens: sum usd allow finite | 6.262e+74 | `describe/describe.json` : `allowances.tobs.total.sum_usd_allow_finite` |
| Latest allowances between contracts at tobs, all five tokens: share capped to zero | 0.6560 | `describe/describe.json` : `allowances.tobs.total.share_capped_to_zero` |
| Latest allowances between contracts at tobs, all five tokens: share unlimited | 0.6599 | `describe/describe.json` : `allowances.tobs.total.share_unlimited` |
| Latest allowances between contracts at tobs, USDC | positive 255,339; positive after the cap 108,916; capped to zero 146,423; capped below the allowance 106,988; unlimited 167,068; capped value at or above U 64; sum of the capped values USD 32,697,898.4 | `describe/describe.json` : `allowances.tobs.per_token[0]` |
| Latest allowances between contracts at tobs, USD₮0 | positive 36,468; positive after the cap 5,648; capped to zero 30,820; capped below the allowance 5,522; unlimited 29,609; capped value at or above U 18; sum of the capped values USD 6,467,762.3 | `describe/describe.json` : `allowances.tobs.per_token[1]` |
| Latest allowances between contracts at tobs, WETH | positive 30,826; positive after the cap 1,395; capped to zero 29,431; capped below the allowance 1,270; unlimited 17,608; capped value at or above U 29; sum of the capped values USD 20,322,898.5 | `describe/describe.json` : `allowances.tobs.per_token[2]` |
| Latest allowances between contracts at tobs, WBTC | positive 11,841; positive after the cap 386; capped to zero 11,455; capped below the allowance 341; unlimited 5,592; capped value at or above U 33; sum of the capped values USD 7,819,502.7 | `describe/describe.json` : `allowances.tobs.per_token[3]` |
| Latest allowances between contracts at tobs, ARB | positive 4,808; positive after the cap 378; capped to zero 4,430; capped below the allowance 333; unlimited 4,015; capped value at or above U 6; sum of the capped values USD 841,209.3 | `describe/describe.json` : `allowances.tobs.per_token[4]` |
| Importance at tobs: contracts | 809,296 | `describe/describe.json` : `importance.tobs.contracts` |
| Importance at tobs: outside nodes | 112,210 | `describe/describe.json` : `importance.tobs.outside_nodes` |
| Importance at tobs: with i t | 807,452 | `describe/describe.json` : `importance.tobs.with_i_t` |
| Importance at tobs: with i a | 52,446 | `describe/describe.json` : `importance.tobs.with_i_a` |
| Importance at tobs: with both | 50,602 | `describe/describe.json` : `importance.tobs.with_both` |
| Importance at tobs: i t usd | 16,611,212,142.1 | `describe/describe.json` : `importance.tobs.i_t_usd` |
| Importance at tobs: i a usd | 309,472,584.1 | `describe/describe.json` : `importance.tobs.i_a_usd` |
| Importance at tobs: inflow untyped usd | 1,681,953,612.2 | `describe/describe.json` : `importance.tobs.inflow_untyped_usd` |
| Latest allowances between contracts at t1, all five tokens: n latest positive | 308,922 | `describe/describe.json` : `allowances.t1.total.n_latest_positive` |
| Latest allowances between contracts at t1, all five tokens: n positive eff | 19,623 | `describe/describe.json` : `allowances.t1.total.n_positive_eff` |
| Latest allowances between contracts at t1, all five tokens: n capped to zero | 289,299 | `describe/describe.json` : `allowances.t1.total.n_capped_to_zero` |
| Latest allowances between contracts at t1, all five tokens: n capped below allowance | 17,480 | `describe/describe.json` : `allowances.t1.total.n_capped_below_allowance` |
| Latest allowances between contracts at t1, all five tokens: n unlimited | 208,245 | `describe/describe.json` : `allowances.t1.total.n_unlimited` |
| Latest allowances between contracts at t1, all five tokens: n finite | 100,677 | `describe/describe.json` : `allowances.t1.total.n_finite` |
| Latest allowances between contracts at t1, all five tokens: n eff at or above cap | 204 | `describe/describe.json` : `allowances.t1.total.n_eff_at_or_above_cap` |
| Latest allowances between contracts at t1, all five tokens: n allow at or above cap | 214,808 | `describe/describe.json` : `allowances.t1.total.n_allow_at_or_above_cap` |
| Latest allowances between contracts at t1, all five tokens: sum usd eff | 83,952,622.3 | `describe/describe.json` : `allowances.t1.total.sum_usd_eff` |
| Latest allowances between contracts at t1, all five tokens: sum usd allow finite | 5.99e+74 | `describe/describe.json` : `allowances.t1.total.sum_usd_allow_finite` |
| Latest allowances between contracts at t1, all five tokens: share capped to zero | 0.9365 | `describe/describe.json` : `allowances.t1.total.share_capped_to_zero` |
| Latest allowances between contracts at t1, all five tokens: share unlimited | 0.6741 | `describe/describe.json` : `allowances.t1.total.share_unlimited` |
| Latest allowances between contracts at t1, USDC | positive 223,685; positive after the cap 11,381; capped to zero 212,304; capped below the allowance 9,640; unlimited 146,928; capped value at or above U 87; sum of the capped values USD 33,068,341.4 | `describe/describe.json` : `allowances.t1.per_token[0]` |
| Latest allowances between contracts at t1, WETH | positive 36,916; positive after the cap 1,442; capped to zero 35,474; capped below the allowance 1,294; unlimited 24,198; capped value at or above U 43; sum of the capped values USD 31,897,955.5 | `describe/describe.json` : `allowances.t1.per_token[1]` |
| Latest allowances between contracts at t1, USD₮0 | positive 33,673; positive after the cap 6,007; capped to zero 27,666; capped below the allowance 5,851; unlimited 27,950; capped value at or above U 23; sum of the capped values USD 7,617,881.6 | `describe/describe.json` : `allowances.t1.per_token[2]` |
| Latest allowances between contracts at t1, WBTC | positive 9,853; positive after the cap 440; capped to zero 9,413; capped below the allowance 390; unlimited 5,409; capped value at or above U 43; sum of the capped values USD 10,755,175.2 | `describe/describe.json` : `allowances.t1.per_token[3]` |
| Latest allowances between contracts at t1, ARB | positive 4,795; positive after the cap 353; capped to zero 4,442; capped below the allowance 305; unlimited 3,760; capped value at or above U 8; sum of the capped values USD 613,268.6 | `describe/describe.json` : `allowances.t1.per_token[4]` |
| Importance at t1: contracts | 715,480 | `describe/describe.json` : `importance.t1.contracts` |
| Importance at t1: outside nodes | 109,094 | `describe/describe.json` : `importance.t1.outside_nodes` |
| Importance at t1: with i t | 713,738 | `describe/describe.json` : `importance.t1.with_i_t` |
| Importance at t1: with i a | 40,395 | `describe/describe.json` : `importance.t1.with_i_a` |
| Importance at t1: with both | 38,653 | `describe/describe.json` : `importance.t1.with_both` |
| Importance at t1: i t usd | 16,622,706,250.4 | `describe/describe.json` : `importance.t1.i_t_usd` |
| Importance at t1: i a usd | 343,843,976.1 | `describe/describe.json` : `importance.t1.i_a_usd` |
| Importance at t1: inflow untyped usd | 1,373,560,052.4 | `describe/describe.json` : `importance.t1.inflow_untyped_usd` |
| Last block at or before the anchor t1 | 447736930 | `describe/describe.json` : `anchor_blocks.t1` |
| Last block at or before the anchor tobs | 479089705 | `describe/describe.json` : `anchor_blocks.tobs` |
| Last block at or before the anchor end_0930 | 510496863 | `describe/describe.json` : `anchor_blocks.end_0930` |
| Balance check: mode | archive | `describe/describe.json` : `balance_check.mode` |
| Balance check: block | 479089705 | `describe/describe.json` : `balance_check.block` |
| Balance check: rows | 1,500 | `describe/describe.json` : `balance_check.rows` |
| Balance check: judged | 1,500 | `describe/describe.json` : `balance_check.judged` |
| Balance check: matched | 1,493 | `describe/describe.json` : `balance_check.matched` |
| Balance check: share | 0.9953 | `describe/describe.json` : `balance_check.share` |
| Balance check: threshold | 0.9800 | `describe/describe.json` : `balance_check.threshold` |
| Balance check: passed | yes | `describe/describe.json` : `balance_check.passed` |
| Balance check: balances | 6,033,263 | `describe/describe.json` : `balance_check.balances` |
| Balance check cell 0x2f2a2543b76a4166549f7aab2e75bef0aefc5b0f positive | 150 pairs, 150 judged, match 1.0000 | `typing/balance_audit.json` : `per_cell[0]` |
| Balance check cell 0x2f2a2543b76a4166549f7aab2e75bef0aefc5b0f zero | 150 pairs, 150 judged, match 1.0000 | `typing/balance_audit.json` : `per_cell[1]` |
| Balance check cell 0x82af49447d8a07e3bd95bd0d56f35241523fbab1 positive | 150 pairs, 150 judged, match 1.0000 | `typing/balance_audit.json` : `per_cell[2]` |
| Balance check cell 0x82af49447d8a07e3bd95bd0d56f35241523fbab1 zero | 150 pairs, 150 judged, match 0.9733 | `typing/balance_audit.json` : `per_cell[3]` |
| Balance check cell 0x912ce59144191c1204e64559fe8253a0e49e6548 positive | 150 pairs, 150 judged, match 1.0000 | `typing/balance_audit.json` : `per_cell[4]` |
| Balance check cell 0x912ce59144191c1204e64559fe8253a0e49e6548 zero | 150 pairs, 150 judged, match 1.0000 | `typing/balance_audit.json` : `per_cell[5]` |
| Balance check cell 0xaf88d065e77c8cc2239327c5edb3a432268e5831 positive | 150 pairs, 150 judged, match 1.0000 | `typing/balance_audit.json` : `per_cell[6]` |
| Balance check cell 0xaf88d065e77c8cc2239327c5edb3a432268e5831 zero | 150 pairs, 150 judged, match 1.0000 | `typing/balance_audit.json` : `per_cell[7]` |
| Balance check cell 0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9 positive | 150 pairs, 150 judged, match 1.0000 | `typing/balance_audit.json` : `per_cell[8]` |
| Balance check cell 0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9 zero | 150 pairs, 150 judged, match 0.9800 | `typing/balance_audit.json` : `per_cell[9]` |
| constants.computed at | 2026-11-08T19:58:00+00:00 | `describe/describe.json` : `constants.computed_at` |
| constants.source | sql/36_c12_constants.sql (contract_rep.c12_constants): the transfers between contracts (c12_events_cc), the latest allowances between contracts at t1 (c12_allow_triples, sql/36_c12_allow_triples.sql) and the transfers from user accounts to contracts (c12_user_events, sql/36_c12_user_events.sql) of the W0 score window | `describe/describe.json` : `constants.source` |
| constants.raw.m transfer | 164.0542 | `describe/describe.json` : `constants.raw.m_transfer` |
| constants.raw.p99 transfer | 16,412.3 | `describe/describe.json` : `constants.raw.p99_transfer` |
| constants.raw.p10 transfer | 1.5255 | `describe/describe.json` : `constants.raw.p10_transfer` |
| constants.raw.p90 transfer | 2,110.0 | `describe/describe.json` : `constants.raw.p90_transfer` |
| constants.raw.n transfers | 377,876,886 | `describe/describe.json` : `constants.raw.n_transfers` |
| constants.raw.m allowance | 0.0707 | `describe/describe.json` : `constants.raw.m_allowance` |
| constants.raw.p99 allowance | 17,993.9 | `describe/describe.json` : `constants.raw.p99_allowance` |
| constants.raw.p10 allowance | 2.999e-06 | `describe/describe.json` : `constants.raw.p10_allowance` |
| constants.raw.p90 allowance | 26.3787 | `describe/describe.json` : `constants.raw.p90_allowance` |
| constants.raw.n latest allowances | 308,922 | `describe/describe.json` : `constants.raw.n_latest_allowances` |
| constants.raw.n positive allowances | 19,623 | `describe/describe.json` : `constants.raw.n_positive_allowances` |
| constants.raw.n capped to zero | 289,299 | `describe/describe.json` : `constants.raw.n_capped_to_zero` |
| constants.raw.n capped below allowance | 17,480 | `describe/describe.json` : `constants.raw.n_capped_below_allowance` |
| constants.raw.n unlimited positive | 8,531 | `describe/describe.json` : `constants.raw.n_unlimited_positive` |
| constants.raw.m user transfer | 250.8180 | `describe/describe.json` : `constants.raw.m_user_transfer` |
| constants.raw.p99 user transfer | 31,306.6 | `describe/describe.json` : `constants.raw.p99_user_transfer` |
| constants.raw.p10 user transfer | 4.4576 | `describe/describe.json` : `constants.raw.p10_user_transfer` |
| constants.raw.p90 user transfer | 3,981.7 | `describe/describe.json` : `constants.raw.p90_user_transfer` |
| constants.raw.n user transfers | 82,749,550 | `describe/describe.json` : `constants.raw.n_user_transfers` |
| constants.m transfer usd | 160.0000 | `describe/describe.json` : `constants.m_transfer_usd` |
| constants.m allowance usd | 0.0710 | `describe/describe.json` : `constants.m_allowance_usd` |
| constants.cap allowance usd | 16,000 | `describe/describe.json` : `constants.cap_allowance_usd` |
| constants.cap user usd | 31,000 | `describe/describe.json` : `constants.cap_user_usd` |
| constants.b transfer | 0.0069 | `describe/describe.json` : `constants.b_transfer` |
| constants.b allowance | 15.4734 | `describe/describe.json` : `constants.b_allowance` |
| constants.unlimited base units | 114,999,999,999,999,997,377,225,245,734,177,625,043,124,954,484,653,241,178,190,190,737,365,693,104,128 | `describe/describe.json` : `constants.unlimited_base_units` |
| constants.dust token | 1e-06 | `describe/describe.json` : `constants.dust_token` |
| constants.rule | b = ln 3 / m with m the median rounded to two significant digits (usd.round_sig); U is the 99th percentile of the US-dollar values of the transfers between contracts and U_user that of the transfers from user accounts to contracts, both of the W0 score window and rounded to two significant digits; m_A is the median of the positive usd_eff of the latest allowances between contracts at t1, unlimited ones included (docs/revision_contract_graph.md section 7) | `describe/describe.json` : `constants.rule` |
| timing.revision commit utc | d39775c 2026-11-07T09:33:38+00:00 | `describe/describe.json` : `timing.revision_commit_utc` |
| timing.protocol commit utc | d39775c 2026-11-07T09:33:38+00:00 | `describe/describe.json` : `timing.protocol_commit_utc` |
| timing.protocol fixed commit utc | 8645bca 2026-11-08T19:51:41+00:00 | `describe/describe.json` : `timing.protocol_fixed_commit_utc` |
| timing.contract12m jobs | 26 | `describe/describe.json` : `timing.contract12m_jobs` |
| timing.contract12m jobs usd | 12.6300 | `describe/describe.json` : `timing.contract12m_jobs_usd` |
| timing.bigquery usd total | 54.8800 | `describe/describe.json` : `timing.bigquery_usd_total` |
| timing.bigquery tib billed | 8.7800 | `describe/describe.json` : `timing.bigquery_tib_billed` |
| timing.budget usd | 60.0000 | `describe/describe.json` : `timing.budget_usd` |

### Daily prices of the five tokens from 2025-04-01 to 2026-09-30

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

## 13. Decisions recorded in the run manifest

| Quantity | Value | Source |
|---|---|---|
| Decision before gate B, step structure started 2026-11-08T17:16:55+00:00 | Revision section 13, amendment of 9 November 2026: jobs 32 and 33 (balances), 34 (anchors) and 43 with the balance check (audit) read no table that job 31 writes, so their runs of 8 November 2026 stand after job 31 was run again with the smart-account lists; they are not run again. | `run_manifest.json` : `steps[14].author_decision` |
| What the step structure would have waited for | a run of balances after the last run of contracts; a run of anchors after the last run of contracts; a run of audit after the last run of contracts | `run_manifest.json` : `steps[14].waited_for` |

No step of gate B ran with an author's decision taken after gate B.

| Quantity | Value | Source |
|---|---|---|
| Decision in "Protocol fixed" (taken before gate B) | The discovery-order test goes on after the stop flag few_capped_allowance_in_edges of section 7, the only flag the pilot set. No change that this protocol or the revision allows lifts the stop; the test is the only direct test of the question of section 1; the decision was taken before any weight, constant, importance, score or crawl of the revision existed (revision section 13, amendment of 9 November 2026). It covers that flag only (decision_covers), so every other refusal of section 8 stays. | `run_manifest.json` : `steps[].gate_b.protocol_fixed.author_decision` |
| Invariants of sql/42 (each a count of violations) | 64 invariants, sum 0 | `run_manifest.json` : `results.checks.checks` |
