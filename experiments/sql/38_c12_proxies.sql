-- Contract-graph revision (docs/revision_contract_graph.md section 9; job 38, step rest): the same-window proxies of
-- rule A for the T_obs contract cohort (c12_cohort_tobs), the transfer and Sybil-stability families of
-- sql/15_usd_proxies.sql (lines 7-41 copied; u_cohort is c12_cohort_tobs and u_transfers the transfers between
-- contracts of the T_obs score window: c12_events_cc, kind 'T', usd IS NOT NULL). A member without such a transfer
-- has 0 in every column. The allowance family is computed locally from the capped contract graph
-- (graphs.raw_degrees), as in every earlier variant (D10).
-- Inputs: contract_rep.c12_events_cc (sql/31), c12_cohort_tobs (sql/38_c12_cohorts.sql).
-- Parameters: @start_ts, @anchor_ts (the T_obs score window, inclusive).

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.c12_proxies_tobs` AS
WITH t AS (
  SELECT x.*, FORMAT_TIMESTAMP('%Y-%m', block_timestamp) AS month,
         x.from_address IN (SELECT address FROM `dissertation-bq.contract_rep.c12_cohort_tobs`) AS from_cohort,
         x.to_address IN (SELECT address FROM `dissertation-bq.contract_rep.c12_cohort_tobs`) AS to_cohort
  FROM (
    SELECT block_timestamp, a AS from_address, b AS to_address, usd
    FROM `dissertation-bq.contract_rep.c12_events_cc`
    WHERE kind = 'T'
      AND block_timestamp >= TIMESTAMP(@start_ts) AND block_timestamp <= TIMESTAMP(@anchor_ts)
  ) AS x
  WHERE block_timestamp >= TIMESTAMP(@start_ts) AND block_timestamp <= TIMESTAMP(@anchor_ts)
    AND usd IS NOT NULL
),
inbound_all AS (
  SELECT to_address AS wallet, COUNT(DISTINCT from_address) AS in_degree, SUM(usd) AS in_value
  FROM t WHERE to_cohort GROUP BY to_address
),
inbound_other AS (
  SELECT to_address AS wallet, COUNT(*) AS inbound_tx, COUNT(DISTINCT from_address) AS inbound_unique,
         COUNT(DISTINCT month) AS in_months
  FROM t WHERE to_cohort AND from_address != to_address GROUP BY to_address
),
attributed AS (
  SELECT IF(from_cohort, from_address, to_address) AS wallet,
         MIN(block_timestamp) AS span_first, MAX(block_timestamp) AS span_last,
         COUNT(DISTINCT month) AS span_months
  FROM t GROUP BY 1
)
SELECT CONCAT('0x', TO_HEX(c.address)) AS wallet,
       IFNULL(a.in_degree, 0) AS in_degree,
       IFNULL(a.in_value, 0.0) AS in_value,
       IFNULL(o.inbound_unique / GREATEST(o.inbound_tx, 1), 0.0) AS inbound_counterparty_ratio,
       IFNULL(TIMESTAMP_DIFF(s.span_last, s.span_first, MICROSECOND) / 8.64e10, 0.0) AS transfer_tenure_days,
       GREATEST(IFNULL(o.in_months, 0), IFNULL(s.span_months, 0)) AS active_months,
       IFNULL(o.inbound_tx, 0) AS inbound_tx,
       IFNULL(o.inbound_unique, 0) AS inbound_unique
FROM `dissertation-bq.contract_rep.c12_cohort_tobs` AS c
LEFT JOIN inbound_all AS a ON a.wallet = c.address
LEFT JOIN inbound_other AS o ON o.wallet = c.address
LEFT JOIN attributed AS s ON s.wallet = c.address;
