-- Contract-graph revision (docs/revision_contract_graph.md, sections 3, 4.1 and 12; job 24): the five-token
-- events of the typing window in one table, so that every later job of this revision reads it and not the
-- materialised logs. Rows of logs_obs with @start_ts <= block_timestamp < @mid_ts and of logs_w1 with
-- @mid_ts <= block_timestamp < @end_ts (together the typing window, 2025-04-01 to 2026-10-01, end exclusive)
-- whose emitter is one of the tokens of u_tokens (WETH, USDC, USDT0, ARB, WBTC): every Approval (kind 'A', of
-- any value, since a zero approval removes an allowance) and every Transfer (kind 'T') with a non-zero value.
-- Inputs: contract_rep.logs_obs and contract_rep.logs_w1 (sql/01_materialize_logs.sql),
--         contract_rep.u_tokens (token BYTES, decimals INT64),
--         contract_rep.u_prices (token BYTES, day DATE, price_usd FLOAT64; one row per token and UTC day
--         from 2023-10-01 to 2026-09-30).
-- Parameters: @start_ts, @mid_ts (the end of logs_obs and the start of logs_w1), @end_ts (exclusive).
--
-- c12_logs5: block_timestamp, block_number, log_index, kind ('A' or 'T'), token (the emitter), a (owner or
--   sender), b (spender or recipient), value (the uint256 amount in base units read as FLOAT64, as in
--   sql/03_ego_events.sql), amount (value / 10^decimals, token units), usd (for 'T': amount x the token's
--   price on the UTC day of the block, NULL without a price; NULL for 'A', whose US-dollar value is taken
--   at an anchor). Addresses are 20-byte BYTES. Partitioned by month and clustered by kind (BigQuery does
--   not cluster on BYTES, so the token cannot be a clustering column).

CREATE TEMP FUNCTION u256(v BYTES) AS (
  IFNULL((SELECT SUM(c * POW(256.0, LENGTH(v) - 1 - o))
          FROM UNNEST(TO_CODE_POINTS(v)) AS c WITH OFFSET o), 0.0)
);

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.c12_logs5`
PARTITION BY TIMESTAMP_TRUNC(block_timestamp, MONTH)
CLUSTER BY kind
AS
WITH src AS (
  SELECT block_timestamp, block_number, log_index, kind, emitter, a, b, val
  FROM `dissertation-bq.contract_rep.logs_obs`
  WHERE block_timestamp >= TIMESTAMP(@start_ts)
    AND block_timestamp < TIMESTAMP(@mid_ts)
    AND kind IN ('A', 'T')
  UNION ALL
  SELECT block_timestamp, block_number, log_index, kind, emitter, a, b, val
  FROM `dissertation-bq.contract_rep.logs_w1`
  WHERE block_timestamp >= TIMESTAMP(@mid_ts)
    AND block_timestamp < TIMESTAMP(@end_ts)
    AND kind IN ('A', 'T')
),
five AS (
  SELECT s.block_timestamp, s.block_number, s.log_index, s.kind, s.emitter AS token, s.a, s.b,
         u256(s.val) AS value
  FROM src AS s
  WHERE s.emitter IN (SELECT token FROM `dissertation-bq.contract_rep.u_tokens`)
    AND (s.kind = 'A' OR LTRIM(TO_HEX(s.val), '0') != '')
)
SELECT f.block_timestamp, f.block_number, f.log_index, f.kind, f.token, f.a, f.b, f.value,
       f.value / POW(10.0, t.decimals) AS amount,
       IF(f.kind = 'T', f.value / POW(10.0, t.decimals) * p.price_usd, NULL) AS usd
FROM five AS f
JOIN `dissertation-bq.contract_rep.u_tokens` AS t ON t.token = f.token
LEFT JOIN `dissertation-bq.contract_rep.u_prices` AS p
  ON p.token = f.token AND p.day = DATE(f.block_timestamp);
