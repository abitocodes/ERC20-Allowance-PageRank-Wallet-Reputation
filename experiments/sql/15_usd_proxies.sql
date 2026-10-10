-- Revised analysis: same-window transfer and Sybil-stability proxies of the revised cohort,
-- as in 05_proxies_same_window.sql but over the listed-token transfers of 12_usd_ego.sql,
-- with in_value in USD (each transfer at the price of its UTC day).
-- Parameters: @start_ts, @anchor_ts (inclusive). Destination: contract_rep.u_proxies_tobs.

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.u_proxies_tobs` AS
WITH t AS (
  SELECT x.*, FORMAT_TIMESTAMP('%Y-%m', block_timestamp) AS month,
         x.from_address IN (SELECT address FROM `dissertation-bq.contract_rep.u_cohort`) AS from_cohort,
         x.to_address IN (SELECT address FROM `dissertation-bq.contract_rep.u_cohort`) AS to_cohort
  FROM `dissertation-bq.contract_rep.u_transfers` AS x
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
FROM `dissertation-bq.contract_rep.u_cohort` AS c
LEFT JOIN inbound_all AS a ON a.wallet = c.address
LEFT JOIN inbound_other AS o ON o.wallet = c.address
LEFT JOIN attributed AS s ON s.wallet = c.address;
