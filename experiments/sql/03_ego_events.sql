-- Ego network of the matched cohort (analysis plan, section 3).
-- An approval is kept when a cohort contract is its owner or its spender, a transfer
-- when a cohort contract is its sender or its recipient. Amounts are decoded to
-- FLOAT64 in raw base units (the uint256 read as a double); addresses stay 20-byte BYTES. Zero-value transfers
-- are dropped; approvals keep zero values, which delete an allowance.
-- Destinations: contract_rep.approvals_ego, contract_rep.transfers_ego.
-- Parameters: @start_ts, @end_ts (exclusive); __SRC__ is logs_obs or logs_w1.

CREATE TEMP FUNCTION u256(v BYTES) AS (
  IFNULL((SELECT SUM(c * POW(256.0, LENGTH(v) - 1 - o))
          FROM UNNEST(TO_CODE_POINTS(v)) AS c WITH OFFSET o), 0.0)
);

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.approvals___SUFFIX__`
PARTITION BY TIMESTAMP_TRUNC(block_timestamp, MONTH)
AS
SELECT
  l.block_timestamp, l.block_number, l.log_index,
  l.emitter AS token_address,
  l.a AS owner,
  l.b AS spender,
  u256(l.val) AS value
FROM `dissertation-bq.contract_rep.__SRC__` AS l
WHERE l.kind = 'A'
  AND l.block_timestamp >= TIMESTAMP(@start_ts)
  AND l.block_timestamp < TIMESTAMP(@end_ts)
  AND (l.a IN (SELECT address FROM `dissertation-bq.contract_rep.cohort`)
       OR l.b IN (SELECT address FROM `dissertation-bq.contract_rep.cohort`));

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.transfers___SUFFIX__`
PARTITION BY TIMESTAMP_TRUNC(block_timestamp, MONTH)
AS
SELECT
  l.block_timestamp, l.block_number, l.log_index,
  l.emitter AS token_address,
  l.a AS from_address,
  l.b AS to_address,
  u256(l.val) AS value
FROM `dissertation-bq.contract_rep.__SRC__` AS l
WHERE l.kind = 'T'
  AND l.block_timestamp >= TIMESTAMP(@start_ts)
  AND l.block_timestamp < TIMESTAMP(@end_ts)
  AND LTRIM(TO_HEX(l.val), '0') != ''
  AND (l.a IN (SELECT address FROM `dissertation-bq.contract_rep.cohort`)
       OR l.b IN (SELECT address FROM `dissertation-bq.contract_rep.cohort`));
