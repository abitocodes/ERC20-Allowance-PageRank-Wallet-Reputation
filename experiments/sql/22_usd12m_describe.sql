-- Twelve-month variant (docs/revision_one_year_window.md): descriptive statistics as in
-- 18_usd_describe.sql, with the same tables and columns but counted inside the score windows.
-- Parameters: @tobs_start, @tobs_end (exclusive), @t1_start, @t1_end (exclusive), @unlimited,
-- @cap_allowance (USD).
--
-- u12_describe_tokens: per selected token, and one row for all other tokens together, the rows of
--   the registered ego tables inside the T_obs score window (approvals, transfers) and in the W1
--   label window, the rows of the twelve-month ego views (T_obs and W1), the USD volume of their
--   transfers and their transfers without a price (expected zero).
-- u12_describe_monthly: events per month of the T_obs ego views (streams approval_ego,
--   transfer_ego) and of the W0 score window of the t1 views (approval_ego_t1, transfer_ego_t1).
-- u12_describe_values: as u_describe_values, on u12_allow_triples_tobs and u12_transfers_tobs.

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.u12_describe_tokens` AS
WITH listed AS (SELECT token FROM `dissertation-bq.contract_rep.u_tokens`),
old_a AS (SELECT token_address AS token, COUNT(*) AS n FROM `dissertation-bq.contract_rep.approvals_ego`
          WHERE block_timestamp >= TIMESTAMP(@tobs_start) AND block_timestamp < TIMESTAMP(@tobs_end) GROUP BY 1),
old_t AS (SELECT token_address AS token, COUNT(*) AS n FROM `dissertation-bq.contract_rep.transfers_ego`
          WHERE block_timestamp >= TIMESTAMP(@tobs_start) AND block_timestamp < TIMESTAMP(@tobs_end) GROUP BY 1),
old_a1 AS (SELECT token_address AS token, COUNT(*) AS n FROM `dissertation-bq.contract_rep.approvals_w1ego` GROUP BY 1),
old_t1 AS (SELECT token_address AS token, COUNT(*) AS n FROM `dissertation-bq.contract_rep.transfers_w1ego` GROUP BY 1),
new_a AS (SELECT token_address AS token, COUNT(*) AS n FROM `dissertation-bq.contract_rep.u12_approvals_tobs` GROUP BY 1),
new_t AS (SELECT token_address AS token, COUNT(*) AS n, SUM(usd) AS usd, COUNTIF(usd IS NULL) AS n_noprice
          FROM `dissertation-bq.contract_rep.u12_transfers_tobs` GROUP BY 1),
new_a1 AS (SELECT token_address AS token, COUNT(*) AS n FROM `dissertation-bq.contract_rep.u12_approvals_w1` GROUP BY 1),
new_t1 AS (SELECT token_address AS token, COUNT(*) AS n, SUM(usd) AS usd, COUNTIF(usd IS NULL) AS n_noprice
           FROM `dissertation-bq.contract_rep.u12_transfers_w1` GROUP BY 1),
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

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.u12_describe_monthly` AS
SELECT FORMAT_TIMESTAMP('%Y-%m', block_timestamp) AS month, 'approval_ego' AS stream, COUNT(*) AS n
FROM `dissertation-bq.contract_rep.u12_approvals_tobs` GROUP BY 1
UNION ALL
SELECT FORMAT_TIMESTAMP('%Y-%m', block_timestamp), 'transfer_ego', COUNT(*)
FROM `dissertation-bq.contract_rep.u12_transfers_tobs` GROUP BY 1
UNION ALL
SELECT FORMAT_TIMESTAMP('%Y-%m', block_timestamp), 'approval_ego_t1', COUNT(*)
FROM `dissertation-bq.contract_rep.u12_approvals_t1`
WHERE block_timestamp >= TIMESTAMP(@t1_start) AND block_timestamp < TIMESTAMP(@t1_end) GROUP BY 1
UNION ALL
SELECT FORMAT_TIMESTAMP('%Y-%m', block_timestamp), 'transfer_ego_t1', COUNT(*)
FROM `dissertation-bq.contract_rep.u12_transfers_t1`
WHERE block_timestamp >= TIMESTAMP(@t1_start) AND block_timestamp < TIMESTAMP(@t1_end) GROUP BY 1;

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.u12_describe_values` AS
SELECT 'latest_allowances_tobs' AS what, COUNT(*) AS n,
       COUNTIF(value >= CAST(@unlimited AS FLOAT64)) AS unlimited,
       COUNTIF(usd >= CAST(@cap_allowance AS FLOAT64)) AS at_or_above_cap,
       COUNT(DISTINCT owner) AS owners,
       COUNT(DISTINCT IF(value >= CAST(@unlimited AS FLOAT64), owner, NULL)) AS owners_unlimited,
       NULL AS owners_both,
       APPROX_QUANTILES(IF(value < CAST(@unlimited AS FLOAT64), usd, NULL), 100) AS usd_percentiles
FROM `dissertation-bq.contract_rep.u12_allow_triples_tobs`
UNION ALL
SELECT 'owners_both_kinds_tobs', COUNT(*), NULL, NULL, NULL, NULL, COUNT(*), NULL
FROM (
  SELECT owner FROM `dissertation-bq.contract_rep.u12_allow_triples_tobs`
  GROUP BY owner
  HAVING COUNTIF(value >= CAST(@unlimited AS FLOAT64)) > 0 AND COUNTIF(value < CAST(@unlimited AS FLOAT64)) > 0
)
UNION ALL
SELECT 'transfers_obs', COUNT(*), NULL, NULL, NULL, NULL, NULL, APPROX_QUANTILES(usd, 100)
FROM `dissertation-bq.contract_rep.u12_transfers_tobs`;
