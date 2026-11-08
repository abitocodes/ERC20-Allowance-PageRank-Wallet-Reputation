-- Contract-graph revision (docs/revision_contract_graph.md sections 4 to 8, docs/discovery_protocol.md section 8 and
-- the gate B amendment of section 13; job 42, step checks): the invariants of the gate B tables before the download.
-- Every count is a number of violations and must be 0 (the driver stops otherwise). The names, in groups:
--   accounts:   contracts_user_accounts_overlap, user_accounts_zero_address, contracts_system_or_zero;
--   pairs:      pair_ends_not_contract_{tobs,t1}, pair_ends_user_account_{tobs,t1}, pairs_duplicate, tags_known;
--   nodes:      nodes_not_contract, nodes_ids (dense, in address order, unique), nodes_set (pair ends and contract
--               members exactly), node_flags, x_nodes_rows;
--   exports:    x_rows_{tobs,t1} (rows of each x table equal its tag's rows, no repeated (src, dst)), x_weights (no
--               NULL, NaN, infinite or negative weight, at least one token or transfer);
--   cap:        capped_pairs_nonpositive, cap_above_uncapped_triples, cap_above_uncapped_pairs (a capped pair is an
--               uncapped pair with no more tokens, sigma, time or weight, the weights within 1e-12 relative),
--               triples_without_balance, dust_rule (usd_eff > 0 exactly when the base-unit test and a positive
--               price hold), anchor_prices, triples_unique, triples_window_{tobs,t1};
--   pilot:      struct_allow_capped_t1, struct_allow_uncapped_t1, struct_transfer_t1 (the t1 pair sets of each layer
--               equal those of c12_struct_t1, both ways, self-pairs included);
--   sources:    transfer_pairs_window_{tobs,t1}, pairs5_{tobs,t1} (against c12_pairs5), constants_rows_t1,
--               constants_values;
--   cohorts:    members_rows, members_class, cohort_user_accounts_{tobs,t1}, cohort_not_contract_{tobs,t1},
--               cohort_rows_{tobs,t1}, spender_untyped_{w0,w1}, proxies_rows;
--   labels:     labels_recount_{w0,w1} (the recount equals u12_labels column by column: integers exactly, the two
--               rates within 1e-12, the revoked value within 1e-9 relative, since FLOAT64 sums are not
--               order-deterministic), label_parts_sum_{w0,w1}, label_split_rows_{w0,w1}, label_spender_class_{w0,w1};
--   importance: importance_not_contract_{tobs,t1}, importance_ids_{tobs,t1}, importance_rows_{tobs,t1} (one row per
--               contract, each with i_t > 0 or i_a > 0, finite, i >= n, every positive raw row), importance_raw_rows,
--               inflow_rows_{tobs,t1}, describe_rows.
-- Parameters: @start_ts, @t1, @tobs_start, @tobs, @dust_digits, @system_first, @system_last.
--
-- c12_checks: check_name (STRING), violations (INT64); 64 rows.

CREATE TEMP FUNCTION bad(x FLOAT64) AS (x IS NULL OR IS_NAN(x) OR IS_INF(x) OR x < 0);

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.c12_checks` AS
WITH
contracts AS (SELECT address FROM `dissertation-bq.contract_rep.c12_contracts`),
users AS (SELECT address FROM `dissertation-bq.contract_rep.c12_user_accounts`),
nodes AS (
  SELECT id, address, address_bytes, is_cohort, is_cohort_t1, is_spender_w0, is_spender_w1
  FROM `dissertation-bq.contract_rep.c12_nodes`
),
members AS (SELECT list, address, address_bytes, class FROM `dissertation-bq.contract_rep.c12_members`),
triples AS (
  SELECT tag, token, owner, spender, value, decimals, price_usd, bal, usd_allow, usd_bal, usd_eff, block_timestamp,
         age_days
  FROM `dissertation-bq.contract_rep.c12_allow_triples`
),
cap AS (
  SELECT tag, owner, spender, n_tokens, w_er, w_raw, max_sig, last_ts
  FROM `dissertation-bq.contract_rep.c12_allow_pairs`
),
unc AS (
  SELECT tag, owner, spender, n_tokens, w_er, w_raw, max_sig, last_ts
  FROM `dissertation-bq.contract_rep.c12_allow_pairs_unc`
),
tp AS (
  SELECT tag, from_address, to_address, n_transfers, first_ts, last_ts
  FROM `dissertation-bq.contract_rep.c12_transfer_pairs`
),
ends AS (
  SELECT tag, owner AS x FROM cap
  UNION ALL SELECT tag, spender FROM cap
  UNION ALL SELECT tag, owner FROM unc
  UNION ALL SELECT tag, spender FROM unc
  UNION ALL SELECT tag, from_address FROM tp
  UNION ALL SELECT tag, to_address FROM tp
),
expected_nodes AS (
  SELECT x AS address FROM ends
  UNION DISTINCT
  SELECT address_bytes FROM members WHERE class = 'contract'
),
flags AS (
  SELECT n.id, n.is_cohort, n.is_cohort_t1, n.is_spender_w0, n.is_spender_w1,
         IFNULL(LOGICAL_OR(m.list = 'cohort_tobs'), FALSE) AS e_cohort,
         IFNULL(LOGICAL_OR(m.list = 'cohort_t1'), FALSE) AS e_cohort_t1,
         IFNULL(LOGICAL_OR(m.list = 'spenders_w0'), FALSE) AS e_spender_w0,
         IFNULL(LOGICAL_OR(m.list = 'spenders_w1'), FALSE) AS e_spender_w1
  FROM nodes AS n
  LEFT JOIN members AS m ON m.address_bytes = n.address_bytes AND m.class = 'contract'
  GROUP BY n.id, n.is_cohort, n.is_cohort_t1, n.is_spender_w0, n.is_spender_w1
),
st1 AS (SELECT a, b, layer FROM `dissertation-bq.contract_rep.c12_struct_t1`),
cap_t1 AS (
  SELECT CONCAT('0x', TO_HEX(owner)) AS a, CONCAT('0x', TO_HEX(spender)) AS b FROM cap WHERE tag = 't1'
),
unc_t1 AS (
  SELECT CONCAT('0x', TO_HEX(owner)) AS a, CONCAT('0x', TO_HEX(spender)) AS b FROM unc WHERE tag = 't1'
),
tp_t1 AS (
  SELECT CONCAT('0x', TO_HEX(from_address)) AS a, CONCAT('0x', TO_HEX(to_address)) AS b FROM tp WHERE tag = 't1'
),
p5 AS (SELECT a, b, n_approvals, n_transfers, first_ts FROM `dissertation-bq.contract_rep.c12_pairs5`),
member_class AS (
  SELECT m.class,
         CASE WHEN c.address IS NOT NULL THEN 'contract'
              WHEN u.address IS NOT NULL THEN 'user_account'
              WHEN m.address_bytes BETWEEN FROM_HEX(SUBSTR(@system_first, 3)) AND FROM_HEX(SUBSTR(@system_last, 3))
                THEN 'system'
              ELSE 'untyped' END AS expected
  FROM members AS m
  LEFT JOIN contracts AS c ON c.address = m.address_bytes
  LEFT JOIN users AS u ON u.address = m.address_bytes
),
recount_w0 AS (
  SELECT COUNTIF(IFNULL(
           p.wallet IS NULL OR u.wallet IS NULL
           OR p.future_new_approvers != u.future_new_approvers
           OR p.future_revoke_count != u.future_revoke_count
           OR ABS(p.future_revoke_rate - u.future_revoke_rate) > 1e-12
           OR ABS(p.future_keep_rate - u.future_keep_rate) > 1e-12
           OR ABS(p.future_revoke_value - u.future_revoke_value)
                > 1e-9 * GREATEST(1.0, ABS(p.future_revoke_value), ABS(u.future_revoke_value))
           OR p.future_new_transfer_senders != u.future_new_transfer_senders
           OR p.future_drain_owners != u.future_drain_owners, TRUE)) AS n
  FROM `dissertation-bq.contract_rep.c12_label_parts_w0` AS p
  FULL OUTER JOIN `dissertation-bq.contract_rep.u12_labels_w0` AS u ON u.wallet = p.wallet
),
recount_w1 AS (
  SELECT COUNTIF(IFNULL(
           p.wallet IS NULL OR u.wallet IS NULL
           OR p.future_new_approvers != u.future_new_approvers
           OR p.future_revoke_count != u.future_revoke_count
           OR ABS(p.future_revoke_rate - u.future_revoke_rate) > 1e-12
           OR ABS(p.future_keep_rate - u.future_keep_rate) > 1e-12
           OR ABS(p.future_revoke_value - u.future_revoke_value)
                > 1e-9 * GREATEST(1.0, ABS(p.future_revoke_value), ABS(u.future_revoke_value))
           OR p.future_new_transfer_senders != u.future_new_transfer_senders
           OR p.future_drain_owners != u.future_drain_owners, TRUE)) AS n
  FROM `dissertation-bq.contract_rep.c12_label_parts_w1` AS p
  FULL OUTER JOIN `dissertation-bq.contract_rep.u12_labels_w1` AS u ON u.wallet = p.wallet
),
parts_w0 AS (
  SELECT COUNTIF(IFNULL(
           n_t1_user + n_t1_contract + n_t1_other != n_t1
           OR future_new_approvers_user + future_new_approvers_contract + future_new_approvers_other
                != future_new_approvers
           OR future_revoke_count_user + future_revoke_count_contract + future_revoke_count_other
                != future_revoke_count
           OR future_new_transfer_senders_user + future_new_transfer_senders_contract
                + future_new_transfer_senders_other != future_new_transfer_senders
           OR future_drain_owners_user + future_drain_owners_contract + future_drain_owners_other
                != future_drain_owners
           OR ABS(future_revoke_rate_user + future_revoke_rate_contract + future_revoke_rate_other
                  - future_revoke_rate) > 1e-12
           OR ABS(future_keep_rate_user + future_keep_rate_contract + future_keep_rate_other
                  - future_keep_rate) > 1e-12
           OR ABS(future_revoke_value_user + future_revoke_value_contract + future_revoke_value_other
                  - future_revoke_value) > 1e-9 * GREATEST(1.0, ABS(future_revoke_value))
           OR LEAST(n_t1_user, n_t1_contract, n_t1_other,
                    future_new_approvers_user, future_new_approvers_contract, future_new_approvers_other,
                    future_revoke_count_user, future_revoke_count_contract, future_revoke_count_other,
                    future_new_transfer_senders_user, future_new_transfer_senders_contract,
                    future_new_transfer_senders_other,
                    future_drain_owners_user, future_drain_owners_contract, future_drain_owners_other) < 0
           OR LEAST(future_revoke_rate_user, future_revoke_rate_contract, future_revoke_rate_other,
                    future_keep_rate_user, future_keep_rate_contract, future_keep_rate_other,
                    future_revoke_value_user, future_revoke_value_contract, future_revoke_value_other) < 0,
           TRUE)) AS n
  FROM `dissertation-bq.contract_rep.c12_label_parts_w0`
),
parts_w1 AS (
  -- the predicate of parts_w0, word for word, on c12_label_parts_w1
  SELECT COUNTIF(IFNULL(
           n_t1_user + n_t1_contract + n_t1_other != n_t1
           OR future_new_approvers_user + future_new_approvers_contract + future_new_approvers_other
                != future_new_approvers
           OR future_revoke_count_user + future_revoke_count_contract + future_revoke_count_other
                != future_revoke_count
           OR future_new_transfer_senders_user + future_new_transfer_senders_contract
                + future_new_transfer_senders_other != future_new_transfer_senders
           OR future_drain_owners_user + future_drain_owners_contract + future_drain_owners_other
                != future_drain_owners
           OR ABS(future_revoke_rate_user + future_revoke_rate_contract + future_revoke_rate_other
                  - future_revoke_rate) > 1e-12
           OR ABS(future_keep_rate_user + future_keep_rate_contract + future_keep_rate_other
                  - future_keep_rate) > 1e-12
           OR ABS(future_revoke_value_user + future_revoke_value_contract + future_revoke_value_other
                  - future_revoke_value) > 1e-9 * GREATEST(1.0, ABS(future_revoke_value))
           OR LEAST(n_t1_user, n_t1_contract, n_t1_other,
                    future_new_approvers_user, future_new_approvers_contract, future_new_approvers_other,
                    future_revoke_count_user, future_revoke_count_contract, future_revoke_count_other,
                    future_new_transfer_senders_user, future_new_transfer_senders_contract,
                    future_new_transfer_senders_other,
                    future_drain_owners_user, future_drain_owners_contract, future_drain_owners_other) < 0
           OR LEAST(future_revoke_rate_user, future_revoke_rate_contract, future_revoke_rate_other,
                    future_keep_rate_user, future_keep_rate_contract, future_keep_rate_other,
                    future_revoke_value_user, future_revoke_value_contract, future_revoke_value_other) < 0,
           TRUE)) AS n
  FROM `dissertation-bq.contract_rep.c12_label_parts_w1`
),
split_w0 AS (
  SELECT wallet, spender_class, n_t1, n_t1_user, n_t1_contract, n_t1_other,
         future_new_approvers_user, future_new_approvers_contract, future_new_approvers_other,
         future_revoke_count_user, future_revoke_count_contract, future_revoke_count_other,
         future_revoke_rate_user, future_revoke_rate_contract, future_revoke_rate_other,
         future_keep_rate_user, future_keep_rate_contract, future_keep_rate_other,
         future_revoke_value_user, future_revoke_value_contract, future_revoke_value_other,
         future_new_transfer_senders_user, future_new_transfer_senders_contract, future_new_transfer_senders_other,
         future_drain_owners_user, future_drain_owners_contract, future_drain_owners_other
  FROM `dissertation-bq.contract_rep.c12_label_parts_w0`
),
x_split_w0 AS (
  SELECT wallet, spender_class, n_t1, n_t1_user, n_t1_contract, n_t1_other,
         future_new_approvers_user, future_new_approvers_contract, future_new_approvers_other,
         future_revoke_count_user, future_revoke_count_contract, future_revoke_count_other,
         future_revoke_rate_user, future_revoke_rate_contract, future_revoke_rate_other,
         future_keep_rate_user, future_keep_rate_contract, future_keep_rate_other,
         future_revoke_value_user, future_revoke_value_contract, future_revoke_value_other,
         future_new_transfer_senders_user, future_new_transfer_senders_contract, future_new_transfer_senders_other,
         future_drain_owners_user, future_drain_owners_contract, future_drain_owners_other
  FROM `dissertation-bq.contract_rep.c12_x_label_split_w0`
),
split_w1 AS (
  -- the column list of split_w0 on c12_label_parts_w1
  SELECT wallet, spender_class, n_t1, n_t1_user, n_t1_contract, n_t1_other,
         future_new_approvers_user, future_new_approvers_contract, future_new_approvers_other,
         future_revoke_count_user, future_revoke_count_contract, future_revoke_count_other,
         future_revoke_rate_user, future_revoke_rate_contract, future_revoke_rate_other,
         future_keep_rate_user, future_keep_rate_contract, future_keep_rate_other,
         future_revoke_value_user, future_revoke_value_contract, future_revoke_value_other,
         future_new_transfer_senders_user, future_new_transfer_senders_contract, future_new_transfer_senders_other,
         future_drain_owners_user, future_drain_owners_contract, future_drain_owners_other
  FROM `dissertation-bq.contract_rep.c12_label_parts_w1`
),
x_split_w1 AS (
  -- the column list of split_w0 on c12_x_label_split_w1
  SELECT wallet, spender_class, n_t1, n_t1_user, n_t1_contract, n_t1_other,
         future_new_approvers_user, future_new_approvers_contract, future_new_approvers_other,
         future_revoke_count_user, future_revoke_count_contract, future_revoke_count_other,
         future_revoke_rate_user, future_revoke_rate_contract, future_revoke_rate_other,
         future_keep_rate_user, future_keep_rate_contract, future_keep_rate_other,
         future_revoke_value_user, future_revoke_value_contract, future_revoke_value_other,
         future_new_transfer_senders_user, future_new_transfer_senders_contract, future_new_transfer_senders_other,
         future_drain_owners_user, future_drain_owners_contract, future_drain_owners_other
  FROM `dissertation-bq.contract_rep.c12_x_label_split_w1`
)
SELECT 'contracts_user_accounts_overlap' AS check_name,
       (SELECT COUNT(*) FROM contracts AS c JOIN users AS u ON u.address = c.address) AS violations
UNION ALL
SELECT 'user_accounts_zero_address', (SELECT COUNTIF(address = FROM_HEX(REPEAT('00', 20))) FROM users)
UNION ALL
SELECT 'contracts_system_or_zero',
       (SELECT COUNTIF(address = FROM_HEX(REPEAT('00', 20))
                       OR address BETWEEN FROM_HEX(SUBSTR(@system_first, 3)) AND FROM_HEX(SUBSTR(@system_last, 3)))
        FROM contracts)
UNION ALL
SELECT 'pair_ends_not_contract_tobs',
       (SELECT COUNT(*) FROM ends AS e LEFT JOIN contracts AS c ON c.address = e.x
        WHERE e.tag = 'tobs' AND c.address IS NULL)
UNION ALL
SELECT 'pair_ends_not_contract_t1',
       (SELECT COUNT(*) FROM ends AS e LEFT JOIN contracts AS c ON c.address = e.x
        WHERE e.tag = 't1' AND c.address IS NULL)
UNION ALL
SELECT 'pair_ends_user_account_tobs',
       (SELECT COUNT(*) FROM ends AS e JOIN users AS u ON u.address = e.x WHERE e.tag = 'tobs')
UNION ALL
SELECT 'pair_ends_user_account_t1',
       (SELECT COUNT(*) FROM ends AS e JOIN users AS u ON u.address = e.x WHERE e.tag = 't1')
UNION ALL
SELECT 'pairs_duplicate',
       (SELECT COUNT(*) FROM (SELECT tag, owner, spender FROM cap GROUP BY tag, owner, spender HAVING COUNT(*) > 1))
     + (SELECT COUNT(*) FROM (SELECT tag, owner, spender FROM unc GROUP BY tag, owner, spender HAVING COUNT(*) > 1))
     + (SELECT COUNT(*) FROM (SELECT tag, from_address, to_address FROM tp
                              GROUP BY tag, from_address, to_address HAVING COUNT(*) > 1))
UNION ALL
SELECT 'tags_known',
       (SELECT COUNTIF(IFNULL(tag NOT IN ('t1', 'tobs'), TRUE)) FROM triples)
     + (SELECT COUNTIF(IFNULL(tag NOT IN ('t1', 'tobs'), TRUE)) FROM cap)
     + (SELECT COUNTIF(IFNULL(tag NOT IN ('t1', 'tobs'), TRUE)) FROM unc)
     + (SELECT COUNTIF(IFNULL(tag NOT IN ('t1', 'tobs'), TRUE)) FROM tp)
UNION ALL
SELECT 'nodes_not_contract',
       (SELECT COUNT(*) FROM nodes AS n LEFT JOIN contracts AS c ON c.address = n.address_bytes
        WHERE c.address IS NULL)
UNION ALL
SELECT 'nodes_ids',
       (SELECT COUNTIF(IFNULL(id != r - 1 OR address != CONCAT('0x', TO_HEX(address_bytes)), TRUE))
        FROM (SELECT id, address, address_bytes, ROW_NUMBER() OVER (ORDER BY address_bytes) AS r FROM nodes))
     + (SELECT COUNT(*) - COUNT(DISTINCT address_bytes) FROM nodes)
UNION ALL
SELECT 'nodes_set',
       (SELECT COUNT(*) FROM (SELECT address FROM expected_nodes EXCEPT DISTINCT SELECT address_bytes FROM nodes))
     + (SELECT COUNT(*) FROM (SELECT address_bytes FROM nodes EXCEPT DISTINCT SELECT address FROM expected_nodes))
UNION ALL
SELECT 'node_flags',
       (SELECT COUNTIF(IFNULL(is_cohort != e_cohort OR is_cohort_t1 != e_cohort_t1 OR is_spender_w0 != e_spender_w0
                              OR is_spender_w1 != e_spender_w1, TRUE))
        FROM flags)
UNION ALL
SELECT 'x_nodes_rows',
       (SELECT COUNT(*) FROM (
          SELECT id, address, is_cohort, is_cohort_t1, is_spender_w0, is_spender_w1 FROM nodes
          EXCEPT DISTINCT
          SELECT id, address, is_cohort, is_cohort_t1, is_spender_w0, is_spender_w1
          FROM `dissertation-bq.contract_rep.c12_x_nodes`))
     + (SELECT COUNT(*) FROM (
          SELECT id, address, is_cohort, is_cohort_t1, is_spender_w0, is_spender_w1
          FROM `dissertation-bq.contract_rep.c12_x_nodes`
          EXCEPT DISTINCT
          SELECT id, address, is_cohort, is_cohort_t1, is_spender_w0, is_spender_w1 FROM nodes))
     + ABS((SELECT COUNT(*) FROM nodes) - (SELECT COUNT(*) FROM `dissertation-bq.contract_rep.c12_x_nodes`))
UNION ALL
SELECT 'x_rows_tobs',
       ABS((SELECT COUNT(*) FROM `dissertation-bq.contract_rep.c12_x_allow_pairs_tobs`)
           - (SELECT COUNTIF(tag = 'tobs') FROM cap))
     + ABS((SELECT COUNT(*) FROM `dissertation-bq.contract_rep.c12_x_allow_pairs_unc_tobs`)
           - (SELECT COUNTIF(tag = 'tobs') FROM unc))
     + ABS((SELECT COUNT(*) FROM `dissertation-bq.contract_rep.c12_x_transfer_pairs_tobs`)
           - (SELECT COUNTIF(tag = 'tobs') FROM tp))
     + (SELECT COUNT(*) FROM (SELECT src, dst FROM `dissertation-bq.contract_rep.c12_x_allow_pairs_tobs`
                              GROUP BY src, dst HAVING COUNT(*) > 1))
     + (SELECT COUNT(*) FROM (SELECT src, dst FROM `dissertation-bq.contract_rep.c12_x_allow_pairs_unc_tobs`
                              GROUP BY src, dst HAVING COUNT(*) > 1))
     + (SELECT COUNT(*) FROM (SELECT src, dst FROM `dissertation-bq.contract_rep.c12_x_transfer_pairs_tobs`
                              GROUP BY src, dst HAVING COUNT(*) > 1))
UNION ALL
SELECT 'x_rows_t1',
       ABS((SELECT COUNT(*) FROM `dissertation-bq.contract_rep.c12_x_allow_pairs_t1`)
           - (SELECT COUNTIF(tag = 't1') FROM cap))
     + ABS((SELECT COUNT(*) FROM `dissertation-bq.contract_rep.c12_x_allow_pairs_unc_t1`)
           - (SELECT COUNTIF(tag = 't1') FROM unc))
     + ABS((SELECT COUNT(*) FROM `dissertation-bq.contract_rep.c12_x_transfer_pairs_t1`)
           - (SELECT COUNTIF(tag = 't1') FROM tp))
     + (SELECT COUNT(*) FROM (SELECT src, dst FROM `dissertation-bq.contract_rep.c12_x_allow_pairs_t1`
                              GROUP BY src, dst HAVING COUNT(*) > 1))
     + (SELECT COUNT(*) FROM (SELECT src, dst FROM `dissertation-bq.contract_rep.c12_x_allow_pairs_unc_t1`
                              GROUP BY src, dst HAVING COUNT(*) > 1))
     + (SELECT COUNT(*) FROM (SELECT src, dst FROM `dissertation-bq.contract_rep.c12_x_transfer_pairs_t1`
                              GROUP BY src, dst HAVING COUNT(*) > 1))
UNION ALL
SELECT 'x_weights',
       (SELECT COUNTIF(IFNULL(src IS NULL OR dst IS NULL OR n_tokens < 1 OR bad(w_er) OR bad(w_raw) OR bad(max_sig)
                              OR bad(w_er_b10x) OR bad(w_er_b01x), TRUE))
        FROM `dissertation-bq.contract_rep.c12_x_allow_pairs_tobs`)
     + (SELECT COUNTIF(IFNULL(src IS NULL OR dst IS NULL OR n_tokens < 1 OR bad(w_er) OR bad(w_raw) OR bad(max_sig),
                              TRUE))
        FROM `dissertation-bq.contract_rep.c12_x_allow_pairs_t1`)
     + (SELECT COUNTIF(IFNULL(src IS NULL OR dst IS NULL OR n_tokens < 1 OR bad(w_er) OR bad(w_raw) OR bad(max_sig),
                              TRUE))
        FROM `dissertation-bq.contract_rep.c12_x_allow_pairs_unc_tobs`)
     + (SELECT COUNTIF(IFNULL(src IS NULL OR dst IS NULL OR n_tokens < 1 OR bad(w_er) OR bad(w_raw) OR bad(max_sig),
                              TRUE))
        FROM `dissertation-bq.contract_rep.c12_x_allow_pairs_unc_t1`)
     + (SELECT COUNTIF(IFNULL(src IS NULL OR dst IS NULL OR n_transfers < 1 OR bad(w_awp) OR bad(w_raw)
                              OR bad(max_sig) OR bad(w_awp_b10x) OR bad(w_awp_b01x), TRUE))
        FROM `dissertation-bq.contract_rep.c12_x_transfer_pairs_tobs`)
     + (SELECT COUNTIF(IFNULL(src IS NULL OR dst IS NULL OR n_transfers < 1 OR bad(w_awp) OR bad(w_raw)
                              OR bad(max_sig), TRUE))
        FROM `dissertation-bq.contract_rep.c12_x_transfer_pairs_t1`)
UNION ALL
SELECT 'capped_pairs_nonpositive', (SELECT COUNTIF(IFNULL(w_raw <= 0 OR n_tokens < 1, TRUE)) FROM cap)
UNION ALL
SELECT 'cap_above_uncapped_triples',
       (SELECT COUNTIF(IFNULL(usd_eff < 0 OR usd_bal < 0 OR usd_eff > usd_allow, TRUE)) FROM triples)
UNION ALL
SELECT 'cap_above_uncapped_pairs',
       (SELECT COUNTIF(IFNULL(u.owner IS NULL OR c.n_tokens > u.n_tokens OR c.max_sig > u.max_sig
                              OR c.last_ts > u.last_ts OR c.w_raw > u.w_raw * (1.0 + 1e-12)
                              OR c.w_er > u.w_er * (1.0 + 1e-12), TRUE))
        FROM cap AS c
        LEFT JOIN unc AS u ON u.tag = c.tag AND u.owner = c.owner AND u.spender = c.spender)
UNION ALL
SELECT 'triples_without_balance', (SELECT COUNTIF(bal IS NULL) FROM triples)
UNION ALL
SELECT 'dust_rule',
       (SELECT COUNTIF(IFNULL((usd_eff > 0)
                              != (IFNULL(bal >= POW(10.0, decimals - CAST(@dust_digits AS INT64)), FALSE)
                                  AND price_usd > 0), TRUE))
        FROM triples)
UNION ALL
SELECT 'anchor_prices',
       ABS(2 * (SELECT COUNT(*) FROM `dissertation-bq.contract_rep.u_tokens`)
           - (SELECT COUNTIF(price_usd > 0) FROM `dissertation-bq.contract_rep.u_prices`
              WHERE token IN (SELECT token FROM `dissertation-bq.contract_rep.u_tokens`)
                AND day IN (DATE(TIMESTAMP(@t1)), DATE(TIMESTAMP(@tobs)))))
UNION ALL
SELECT 'triples_unique',
       (SELECT COUNT(*) FROM (SELECT tag, token, owner, spender FROM triples
                              GROUP BY tag, token, owner, spender HAVING COUNT(*) > 1))
UNION ALL
SELECT 'triples_window_tobs',
       (SELECT COUNTIF(IFNULL(block_timestamp < TIMESTAMP(@tobs_start) OR block_timestamp > TIMESTAMP(@tobs)
                              OR age_days < 0 OR value <= 0, TRUE))
        FROM triples WHERE tag = 'tobs')
UNION ALL
SELECT 'triples_window_t1',
       (SELECT COUNTIF(IFNULL(block_timestamp < TIMESTAMP(@start_ts) OR block_timestamp > TIMESTAMP(@t1)
                              OR age_days < 0 OR value <= 0, TRUE))
        FROM triples WHERE tag = 't1')
UNION ALL
SELECT 'struct_allow_capped_t1',
       (SELECT COUNT(*) FROM (SELECT a, b FROM cap_t1
                              EXCEPT DISTINCT SELECT a, b FROM st1 WHERE layer = 'allow_capped'))
     + (SELECT COUNT(*) FROM (SELECT a, b FROM st1 WHERE layer = 'allow_capped'
                              EXCEPT DISTINCT SELECT a, b FROM cap_t1))
UNION ALL
SELECT 'struct_allow_uncapped_t1',
       (SELECT COUNT(*) FROM (SELECT a, b FROM unc_t1
                              EXCEPT DISTINCT SELECT a, b FROM st1 WHERE layer = 'allow_uncapped'))
     + (SELECT COUNT(*) FROM (SELECT a, b FROM st1 WHERE layer = 'allow_uncapped'
                              EXCEPT DISTINCT SELECT a, b FROM unc_t1))
UNION ALL
SELECT 'struct_transfer_t1',
       (SELECT COUNT(*) FROM (SELECT a, b FROM tp_t1 EXCEPT DISTINCT SELECT a, b FROM st1 WHERE layer = 'transfer'))
     + (SELECT COUNT(*) FROM (SELECT a, b FROM st1 WHERE layer = 'transfer' EXCEPT DISTINCT SELECT a, b FROM tp_t1))
UNION ALL
SELECT 'transfer_pairs_window_tobs',
       (SELECT COUNTIF(IFNULL(first_ts < TIMESTAMP(@tobs_start) OR last_ts > TIMESTAMP(@tobs) OR first_ts > last_ts
                              OR n_transfers < 1, TRUE))
        FROM tp WHERE tag = 'tobs')
UNION ALL
SELECT 'transfer_pairs_window_t1',
       (SELECT COUNTIF(IFNULL(first_ts < TIMESTAMP(@start_ts) OR last_ts > TIMESTAMP(@t1) OR first_ts > last_ts
                              OR n_transfers < 1, TRUE))
        FROM tp WHERE tag = 't1')
UNION ALL
SELECT 'pairs5_tobs',
       (SELECT COUNTIF(IFNULL(p.a IS NULL OR t.n_transfers > p.n_transfers OR t.first_ts < p.first_ts, TRUE))
        FROM tp AS t LEFT JOIN p5 AS p ON p.a = t.from_address AND p.b = t.to_address WHERE t.tag = 'tobs')
     + (SELECT COUNTIF(IFNULL(p.a IS NULL OR p.n_approvals = 0, TRUE))
        FROM unc AS u LEFT JOIN p5 AS p ON p.a = u.owner AND p.b = u.spender WHERE u.tag = 'tobs')
UNION ALL
SELECT 'pairs5_t1',
       (SELECT COUNTIF(IFNULL(p.a IS NULL OR t.n_transfers > p.n_transfers OR t.first_ts < p.first_ts, TRUE))
        FROM tp AS t LEFT JOIN p5 AS p ON p.a = t.from_address AND p.b = t.to_address WHERE t.tag = 't1')
     + (SELECT COUNTIF(IFNULL(p.a IS NULL OR p.n_approvals = 0, TRUE))
        FROM unc AS u LEFT JOIN p5 AS p ON p.a = u.owner AND p.b = u.spender WHERE u.tag = 't1')
UNION ALL
SELECT 'constants_rows_t1',
       IFNULL((SELECT ABS(c.n_transfers - (SELECT IFNULL(SUM(n_transfers), 0) FROM tp WHERE tag = 't1'))
                    + ABS(c.n_positive_allowances - (SELECT COUNTIF(tag = 't1' AND usd_eff > 0) FROM triples))
                    + ABS(c.n_latest_allowances - (SELECT COUNTIF(tag = 't1') FROM triples))
               FROM `dissertation-bq.contract_rep.c12_constants` AS c), 1)
     + ABS((SELECT COUNT(*) FROM `dissertation-bq.contract_rep.c12_constants`) - 1)
UNION ALL
SELECT 'constants_values',
       (SELECT COUNTIF(IFNULL(bad(m_transfer) OR m_transfer = 0 OR bad(p99_transfer) OR p99_transfer = 0
                              OR bad(m_allowance) OR m_allowance = 0 OR bad(p99_user_transfer)
                              OR p99_user_transfer = 0, TRUE))
        FROM `dissertation-bq.contract_rep.c12_constants`)
UNION ALL
SELECT 'members_rows',
       ABS((SELECT COUNT(*) FROM members)
           - (SELECT COUNT(*) FROM `dissertation-bq.contract_rep.u12_cohort_tobs`)
           - (SELECT COUNT(*) FROM `dissertation-bq.contract_rep.u12_cohort_t1`)
           - (SELECT COUNT(*) FROM `dissertation-bq.contract_rep.u12_labels_w0`)
           - (SELECT COUNT(*) FROM `dissertation-bq.contract_rep.u12_labels_w1`))
     + (SELECT COUNT(*) FROM (SELECT list, address_bytes FROM members GROUP BY list, address_bytes HAVING COUNT(*) > 1))
     + (SELECT COUNTIF(IFNULL(address != CONCAT('0x', TO_HEX(address_bytes))
                              OR list NOT IN ('cohort_tobs', 'cohort_t1', 'spenders_w0', 'spenders_w1'), TRUE))
        FROM members)
UNION ALL
SELECT 'members_class', (SELECT COUNTIF(class IS DISTINCT FROM expected) FROM member_class)
UNION ALL
SELECT 'cohort_user_accounts_tobs',
       (SELECT COUNT(*) FROM `dissertation-bq.contract_rep.c12_cohort_tobs` AS k JOIN users AS u ON u.address = k.address)
UNION ALL
SELECT 'cohort_user_accounts_t1',
       (SELECT COUNT(*) FROM `dissertation-bq.contract_rep.c12_cohort_t1` AS k JOIN users AS u ON u.address = k.address)
UNION ALL
SELECT 'cohort_not_contract_tobs',
       (SELECT COUNT(*) FROM `dissertation-bq.contract_rep.c12_cohort_tobs` AS k
        LEFT JOIN contracts AS c ON c.address = k.address WHERE c.address IS NULL)
UNION ALL
SELECT 'cohort_not_contract_t1',
       (SELECT COUNT(*) FROM `dissertation-bq.contract_rep.c12_cohort_t1` AS k
        LEFT JOIN contracts AS c ON c.address = k.address WHERE c.address IS NULL)
UNION ALL
SELECT 'cohort_rows_tobs',
       ABS((SELECT COUNT(*) FROM `dissertation-bq.contract_rep.u12_cohort_tobs`)
           - (SELECT COUNT(*) FROM `dissertation-bq.contract_rep.u12_cohort_tobs` AS k
              JOIN users AS u ON u.address = k.address)
           - (SELECT COUNT(*) FROM `dissertation-bq.contract_rep.c12_cohort_tobs`))
     + (SELECT COUNT(*) FROM (SELECT address FROM `dissertation-bq.contract_rep.c12_cohort_tobs`
                              GROUP BY address HAVING COUNT(*) > 1))
UNION ALL
SELECT 'cohort_rows_t1',
       ABS((SELECT COUNT(*) FROM `dissertation-bq.contract_rep.u12_cohort_t1`)
           - (SELECT COUNT(*) FROM `dissertation-bq.contract_rep.u12_cohort_t1` AS k
              JOIN users AS u ON u.address = k.address)
           - (SELECT COUNT(*) FROM `dissertation-bq.contract_rep.c12_cohort_t1`))
     + (SELECT COUNT(*) FROM (SELECT address FROM `dissertation-bq.contract_rep.c12_cohort_t1`
                              GROUP BY address HAVING COUNT(*) > 1))
UNION ALL
SELECT 'spender_untyped_w0', (SELECT COUNTIF(class = 'untyped') FROM members WHERE list = 'spenders_w0')
UNION ALL
SELECT 'spender_untyped_w1', (SELECT COUNTIF(class = 'untyped') FROM members WHERE list = 'spenders_w1')
UNION ALL
SELECT 'proxies_rows',
       ABS((SELECT COUNT(*) FROM `dissertation-bq.contract_rep.c12_proxies_tobs`)
           - (SELECT COUNT(*) FROM `dissertation-bq.contract_rep.c12_cohort_tobs`))
     + (SELECT COUNT(*) FROM (SELECT wallet FROM `dissertation-bq.contract_rep.c12_proxies_tobs`
                              EXCEPT DISTINCT
                              SELECT CONCAT('0x', TO_HEX(address)) FROM `dissertation-bq.contract_rep.c12_cohort_tobs`))
     + (SELECT COUNT(*) FROM (SELECT wallet FROM `dissertation-bq.contract_rep.c12_proxies_tobs`
                              GROUP BY wallet HAVING COUNT(*) > 1))
     + (SELECT COUNTIF(IFNULL(in_degree IS NULL OR bad(in_value) OR bad(inbound_counterparty_ratio)
                              OR bad(transfer_tenure_days) OR active_months IS NULL OR inbound_tx IS NULL
                              OR inbound_unique IS NULL, TRUE))
        FROM `dissertation-bq.contract_rep.c12_proxies_tobs`)
UNION ALL
SELECT 'labels_recount_w0', (SELECT n FROM recount_w0)
UNION ALL
SELECT 'labels_recount_w1', (SELECT n FROM recount_w1)
UNION ALL
SELECT 'label_parts_sum_w0', (SELECT n FROM parts_w0)
UNION ALL
SELECT 'label_parts_sum_w1', (SELECT n FROM parts_w1)
UNION ALL
SELECT 'label_split_rows_w0',
       (SELECT COUNT(*) FROM (SELECT * FROM split_w0 EXCEPT DISTINCT SELECT * FROM x_split_w0))
     + (SELECT COUNT(*) FROM (SELECT * FROM x_split_w0 EXCEPT DISTINCT SELECT * FROM split_w0))
     + ABS((SELECT COUNT(*) FROM split_w0) - (SELECT COUNT(*) FROM x_split_w0))
UNION ALL
SELECT 'label_split_rows_w1',
       (SELECT COUNT(*) FROM (SELECT * FROM split_w1 EXCEPT DISTINCT SELECT * FROM x_split_w1))
     + (SELECT COUNT(*) FROM (SELECT * FROM x_split_w1 EXCEPT DISTINCT SELECT * FROM split_w1))
     + ABS((SELECT COUNT(*) FROM split_w1) - (SELECT COUNT(*) FROM x_split_w1))
UNION ALL
SELECT 'label_spender_class_w0',
       (SELECT COUNTIF(spender_class IS NULL) FROM `dissertation-bq.contract_rep.c12_label_parts_w0`)
UNION ALL
SELECT 'label_spender_class_w1',
       (SELECT COUNTIF(spender_class IS NULL) FROM `dissertation-bq.contract_rep.c12_label_parts_w1`)
UNION ALL
SELECT 'importance_not_contract_tobs',
       (SELECT COUNT(*) FROM `dissertation-bq.contract_rep.c12_importance_tobs` AS i
        LEFT JOIN contracts AS c ON c.address = FROM_HEX(SUBSTR(i.address, 3)) WHERE c.address IS NULL)
UNION ALL
SELECT 'importance_not_contract_t1',
       (SELECT COUNT(*) FROM `dissertation-bq.contract_rep.c12_importance_t1` AS i
        LEFT JOIN contracts AS c ON c.address = FROM_HEX(SUBSTR(i.address, 3)) WHERE c.address IS NULL)
UNION ALL
SELECT 'importance_ids_tobs',
       (SELECT COUNTIF(IFNULL(i.id < -1 OR (i.id = -1 AND n.id IS NOT NULL) OR (i.id >= 0 AND n.id IS NULL)
                              OR (i.id >= 0 AND n.id != i.id), TRUE))
        FROM `dissertation-bq.contract_rep.c12_importance_tobs` AS i LEFT JOIN nodes AS n ON n.address = i.address)
UNION ALL
SELECT 'importance_ids_t1',
       (SELECT COUNTIF(IFNULL(i.id < -1 OR (i.id = -1 AND n.id IS NOT NULL) OR (i.id >= 0 AND n.id IS NULL)
                              OR (i.id >= 0 AND n.id != i.id), TRUE))
        FROM `dissertation-bq.contract_rep.c12_importance_t1` AS i LEFT JOIN nodes AS n ON n.address = i.address)
UNION ALL
SELECT 'importance_rows_tobs',
       (SELECT COUNT(*) FROM (SELECT address FROM `dissertation-bq.contract_rep.c12_importance_tobs`
                              GROUP BY address HAVING COUNT(*) > 1))
     + (SELECT COUNTIF(IFNULL(NOT (i_t > 0 OR i_a > 0) OR bad(i_t) OR bad(i_a) OR n_t < 0 OR n_a < 0
                              OR i_t < n_t OR i_a < n_a, TRUE))
        FROM `dissertation-bq.contract_rep.c12_importance_tobs`)
     + ABS((SELECT COUNT(*) FROM `dissertation-bq.contract_rep.c12_importance_tobs`)
           - (SELECT COUNTIF(tag = 'tobs' AND part = 'contract' AND (i_t > 0 OR i_a > 0))
              FROM `dissertation-bq.contract_rep.c12_importance_raw`))
UNION ALL
SELECT 'importance_rows_t1',
       (SELECT COUNT(*) FROM (SELECT address FROM `dissertation-bq.contract_rep.c12_importance_t1`
                              GROUP BY address HAVING COUNT(*) > 1))
     + (SELECT COUNTIF(IFNULL(NOT (i_t > 0 OR i_a > 0) OR bad(i_t) OR bad(i_a) OR n_t < 0 OR n_a < 0
                              OR i_t < n_t OR i_a < n_a, TRUE))
        FROM `dissertation-bq.contract_rep.c12_importance_t1`)
     + ABS((SELECT COUNT(*) FROM `dissertation-bq.contract_rep.c12_importance_t1`)
           - (SELECT COUNTIF(tag = 't1' AND part = 'contract' AND (i_t > 0 OR i_a > 0))
              FROM `dissertation-bq.contract_rep.c12_importance_raw`))
UNION ALL
SELECT 'importance_raw_rows',
       (SELECT COUNT(*) FROM (SELECT tag, address FROM `dissertation-bq.contract_rep.c12_importance_raw`
                              WHERE part = 'contract' GROUP BY tag, address HAVING COUNT(*) > 1))
     + ABS((SELECT COUNTIF(part = 'untyped') FROM `dissertation-bq.contract_rep.c12_importance_raw`) - 2)
     + (SELECT COUNTIF(IFNULL(part NOT IN ('contract', 'untyped') OR tag NOT IN ('t1', 'tobs')
                              OR (part = 'contract') != (address IS NOT NULL), TRUE))
        FROM `dissertation-bq.contract_rep.c12_importance_raw`)
UNION ALL
SELECT 'inflow_rows_tobs',
       ABS((SELECT COUNT(*) FROM `dissertation-bq.contract_rep.c12_inflow_untyped_tobs`) - 1)
     + (SELECT COUNTIF(bad(usd)) FROM `dissertation-bq.contract_rep.c12_inflow_untyped_tobs`)
UNION ALL
SELECT 'inflow_rows_t1',
       ABS((SELECT COUNT(*) FROM `dissertation-bq.contract_rep.c12_inflow_untyped_t1`) - 1)
     + (SELECT COUNTIF(bad(usd)) FROM `dissertation-bq.contract_rep.c12_inflow_untyped_t1`)
UNION ALL
SELECT 'describe_rows',
       ABS(IFNULL((SELECT SUM(n_latest_positive) FROM `dissertation-bq.contract_rep.c12_describe_allowances`), 0)
           - (SELECT COUNT(*) FROM triples));
