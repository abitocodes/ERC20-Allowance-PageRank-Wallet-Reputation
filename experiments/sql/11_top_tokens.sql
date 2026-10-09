-- Top-token subgraphs at T_obs (robustness check). Two token lists of 20:
--   by_amount: largest summed raw amounts, transfers plus latest allowances (an unlimited
--              allowance counts as 2^256 - 1, so this favours tokens with many of them);
--   by_rows:   most rows, transfers plus latest allowances.
-- For each list the allowance and transfer pair tables are rebuilt from that list's tokens
-- only, with node ids from contract_rep.nodes. Parameters: @start_ts, @anchor_ts.

CREATE TEMP FUNCTION sig(age_days FLOAT64) AS (1.0 / (1.0 + EXP(0.01 * (age_days - 180.0))));
CREATE TEMP FUNCTION vt(x FLOAT64) AS (IF(x >= 40.0, 1.0, 2.0 / (1.0 + EXP(-x)) - 1.0));

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.top_tokens` AS
WITH t AS (
  SELECT token_address, SUM(value) AS amount, COUNT(*) AS n
  FROM `dissertation-bq.contract_rep.transfers_ego`
  WHERE block_timestamp >= TIMESTAMP(@start_ts) AND block_timestamp <= TIMESTAMP(@anchor_ts)
  GROUP BY token_address
),
a AS (
  SELECT token_address, SUM(value) AS amount, COUNT(*) AS n
  FROM `dissertation-bq.contract_rep.allow_triples_tobs` GROUP BY token_address
),
j AS (
  SELECT COALESCE(t.token_address, a.token_address) AS token_address,
         IFNULL(t.amount, 0) + IFNULL(a.amount, 0) AS amount,
         IFNULL(t.n, 0) + IFNULL(a.n, 0) AS n
  FROM t FULL OUTER JOIN a ON t.token_address = a.token_address
)
SELECT token_address, amount, n,
       RANK() OVER (ORDER BY amount DESC) <= 20 AS by_amount,
       RANK() OVER (ORDER BY n DESC) <= 20 AS by_rows
FROM j;

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.top_token_transfer_triples` AS
SELECT from_address, to_address, token_address,
       SUM(sig(age_days) * vt(value)) AS w_awp, MAX(sig(age_days)) AS max_sig
FROM (
  SELECT from_address, to_address, token_address, value,
         TIMESTAMP_DIFF(TIMESTAMP(@anchor_ts), block_timestamp, MICROSECOND) / 8.64e10 AS age_days
  FROM `dissertation-bq.contract_rep.transfers_ego`
  WHERE block_timestamp >= TIMESTAMP(@start_ts) AND block_timestamp <= TIMESTAMP(@anchor_ts)
    AND token_address IN (SELECT token_address FROM `dissertation-bq.contract_rep.top_tokens` WHERE by_amount OR by_rows)
)
GROUP BY 1, 2, 3;

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.x_top_token_pairs` AS
WITH tt AS (SELECT * FROM `dissertation-bq.contract_rep.top_tokens`),
tr AS (
  SELECT 'by_amount' AS list, 'transfer' AS layer, from_address AS u, to_address AS v,
         SUM(w_awp) AS w, MAX(max_sig) AS max_sig
  FROM `dissertation-bq.contract_rep.top_token_transfer_triples`
  WHERE token_address IN (SELECT token_address FROM tt WHERE by_amount) GROUP BY 3, 4
  UNION ALL
  SELECT 'by_rows', 'transfer', from_address, to_address, SUM(w_awp), MAX(max_sig)
  FROM `dissertation-bq.contract_rep.top_token_transfer_triples`
  WHERE token_address IN (SELECT token_address FROM tt WHERE by_rows) GROUP BY 3, 4
),
al AS (
  SELECT 'by_amount' AS list, 'allowance' AS layer, owner AS u, spender AS v,
         SUM(sig(age_days) * vt(value)) AS w, MAX(sig(age_days)) AS max_sig
  FROM `dissertation-bq.contract_rep.allow_triples_tobs`
  WHERE token_address IN (SELECT token_address FROM tt WHERE by_amount) GROUP BY 3, 4
  UNION ALL
  SELECT 'by_rows', 'allowance', owner, spender, SUM(sig(age_days) * vt(value)), MAX(sig(age_days))
  FROM `dissertation-bq.contract_rep.allow_triples_tobs`
  WHERE token_address IN (SELECT token_address FROM tt WHERE by_rows) GROUP BY 3, 4
)
SELECT x.list, x.layer, s.id AS src, d.id AS dst, x.w, x.max_sig
FROM (SELECT * FROM tr UNION ALL SELECT * FROM al) AS x
JOIN `dissertation-bq.contract_rep.nodes` AS s ON s.address_bytes = x.u
JOIN `dissertation-bq.contract_rep.nodes` AS d ON d.address_bytes = x.v;
