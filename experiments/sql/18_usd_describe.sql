-- Revised analysis: descriptive statistics and the account of every row the token list and the
-- revised cohort leave out (docs/revision_price_weighting.md).
-- Parameters: @unlimited (base units at or above which an allowance is unlimited), @cap_allowance (USD).
--
-- u_describe_tokens: per listed token, and one row for all other tokens together, the rows of
--   the registered ego tables (observation window and W1) and of the revised ego tables, the USD
--   volume of the revised transfers and the revised transfers without a price (expected zero).
-- u_describe_monthly: revised events per month and stream.
-- u_describe_values: latest allowances at T_obs (count, unlimited, capped in the C-PR layer,
--   owners, owners with an unlimited allowance, owners with both kinds) and USD quantiles of
--   the revised transfers and finite latest allowances at T_obs.

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.u_describe_tokens` AS
WITH listed AS (SELECT token FROM `dissertation-bq.contract_rep.u_tokens`),
old_a AS (SELECT token_address AS token, COUNT(*) AS n FROM `dissertation-bq.contract_rep.approvals_ego` GROUP BY 1),
old_t AS (SELECT token_address AS token, COUNT(*) AS n FROM `dissertation-bq.contract_rep.transfers_ego` GROUP BY 1),
old_a1 AS (SELECT token_address AS token, COUNT(*) AS n FROM `dissertation-bq.contract_rep.approvals_w1ego` GROUP BY 1),
old_t1 AS (SELECT token_address AS token, COUNT(*) AS n FROM `dissertation-bq.contract_rep.transfers_w1ego` GROUP BY 1),
new_a AS (SELECT token_address AS token, COUNT(*) AS n FROM `dissertation-bq.contract_rep.u_approvals` GROUP BY 1),
new_t AS (SELECT token_address AS token, COUNT(*) AS n, SUM(usd) AS usd, COUNTIF(usd IS NULL) AS n_noprice
          FROM `dissertation-bq.contract_rep.u_transfers` GROUP BY 1),
new_a1 AS (SELECT token_address AS token, COUNT(*) AS n FROM `dissertation-bq.contract_rep.u_approvals_w1` GROUP BY 1),
new_t1 AS (SELECT token_address AS token, COUNT(*) AS n, SUM(usd) AS usd, COUNTIF(usd IS NULL) AS n_noprice
           FROM `dissertation-bq.contract_rep.u_transfers_w1` GROUP BY 1),
toks AS (
  SELECT token FROM old_a UNION DISTINCT SELECT token FROM old_t
  UNION DISTINCT SELECT token FROM old_a1 UNION DISTINCT SELECT token FROM old_t1
),
per AS (
  SELECT k.token, k.token IN (SELECT token FROM listed) AS listed,
         IFNULL(oa.n, 0) AS reg_approvals, IFNULL(ot.n, 0) AS reg_transfers,
         IFNULL(oa1.n, 0) AS reg_approvals_w1, IFNULL(ot1.n, 0) AS reg_transfers_w1,
         IFNULL(na.n, 0) AS rev_approvals, IFNULL(nt.n, 0) AS rev_transfers,
         IFNULL(na1.n, 0) AS rev_approvals_w1, IFNULL(nt1.n, 0) AS rev_transfers_w1,
         IFNULL(nt.usd, 0) AS rev_transfer_usd, IFNULL(nt1.usd, 0) AS rev_transfer_usd_w1,
         IFNULL(nt.n_noprice, 0) + IFNULL(nt1.n_noprice, 0) AS rev_transfers_without_price
  FROM toks AS k
  LEFT JOIN old_a AS oa ON oa.token = k.token LEFT JOIN old_t AS ot ON ot.token = k.token
  LEFT JOIN old_a1 AS oa1 ON oa1.token = k.token LEFT JOIN old_t1 AS ot1 ON ot1.token = k.token
  LEFT JOIN new_a AS na ON na.token = k.token LEFT JOIN new_t AS nt ON nt.token = k.token
  LEFT JOIN new_a1 AS na1 ON na1.token = k.token LEFT JOIN new_t1 AS nt1 ON nt1.token = k.token
)
SELECT IF(listed, CONCAT('0x', TO_HEX(token)), 'unlisted') AS token, listed,
       COUNT(*) AS tokens,
       SUM(reg_approvals) AS reg_approvals, SUM(reg_transfers) AS reg_transfers,
       SUM(reg_approvals_w1) AS reg_approvals_w1, SUM(reg_transfers_w1) AS reg_transfers_w1,
       SUM(rev_approvals) AS rev_approvals, SUM(rev_transfers) AS rev_transfers,
       SUM(rev_approvals_w1) AS rev_approvals_w1, SUM(rev_transfers_w1) AS rev_transfers_w1,
       SUM(rev_transfer_usd) AS rev_transfer_usd, SUM(rev_transfer_usd_w1) AS rev_transfer_usd_w1,
       SUM(rev_transfers_without_price) AS rev_transfers_without_price
FROM per
GROUP BY 1, 2;

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.u_describe_monthly` AS
SELECT FORMAT_TIMESTAMP('%Y-%m', block_timestamp) AS month, 'approval_ego' AS stream, COUNT(*) AS n
FROM `dissertation-bq.contract_rep.u_approvals` GROUP BY 1
UNION ALL
SELECT FORMAT_TIMESTAMP('%Y-%m', block_timestamp), 'transfer_ego', COUNT(*)
FROM `dissertation-bq.contract_rep.u_transfers` GROUP BY 1;

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.u_describe_values` AS
SELECT 'latest_allowances_tobs' AS what, COUNT(*) AS n,
       COUNTIF(value >= CAST(@unlimited AS FLOAT64)) AS unlimited,
       COUNTIF(usd >= CAST(@cap_allowance AS FLOAT64)) AS at_or_above_cap,
       COUNT(DISTINCT owner) AS owners,
       COUNT(DISTINCT IF(value >= CAST(@unlimited AS FLOAT64), owner, NULL)) AS owners_unlimited,
       NULL AS owners_both,
       APPROX_QUANTILES(IF(value < CAST(@unlimited AS FLOAT64), usd, NULL), 100) AS usd_percentiles
FROM `dissertation-bq.contract_rep.u_allow_triples_tobs`
UNION ALL
SELECT 'owners_both_kinds_tobs', COUNT(*), NULL, NULL, NULL, NULL, COUNT(*), NULL
FROM (
  SELECT owner FROM `dissertation-bq.contract_rep.u_allow_triples_tobs`
  GROUP BY owner
  HAVING COUNTIF(value >= CAST(@unlimited AS FLOAT64)) > 0 AND COUNTIF(value < CAST(@unlimited AS FLOAT64)) > 0
)
UNION ALL
SELECT 'transfers_obs', COUNT(*), NULL, NULL, NULL, NULL, NULL, APPROX_QUANTILES(usd, 100)
FROM `dissertation-bq.contract_rep.u_transfers`;
