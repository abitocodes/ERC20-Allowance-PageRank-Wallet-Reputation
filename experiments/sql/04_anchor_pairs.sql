-- Edge aggregates of the two graphs at one anchor (T_obs or a freeze date), from the
-- ego events of 03_ego_events.sql. Parameters: @start_ts, @anchor_ts (inclusive).
-- __TAG__ names the anchor (tobs, t1). The decay and value transform use the values of
-- config/contract_reputation.yaml: k = 0.01, t0 = 180 days, b = 1.
--
-- allow_triples___TAG__: latest approval of each (token, owner, spender) up to the anchor,
--   in (block number, log index) order, kept when its value is positive.
-- allow_pairs___TAG__:   per (owner, spender): tokens, EndorseRank weight sum sigma*V,
--   raw allowance sum (C-PR allowance layer), largest sigma, latest approval time.
-- transfer_pairs___TAG__: per (sender, recipient): transfers, AWP weight sum sigma*V,
--   raw layer sum x*sigma (C-PR transfer layer), largest sigma (AWP activeness),
--   summed raw value, first and last transfer time.

CREATE TEMP FUNCTION sig(age_days FLOAT64) AS (1.0 / (1.0 + EXP(0.01 * (age_days - 180.0))));
CREATE TEMP FUNCTION vt(x FLOAT64) AS (IF(x >= 40.0, 1.0, 2.0 / (1.0 + EXP(-x)) - 1.0));

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.allow_triples___TAG__` AS
SELECT token_address, owner, spender, value, block_timestamp,
       TIMESTAMP_DIFF(TIMESTAMP(@anchor_ts), block_timestamp, MICROSECOND) / 8.64e10 AS age_days
FROM (
  SELECT *, ROW_NUMBER() OVER (
           PARTITION BY token_address, owner, spender
           ORDER BY block_number DESC, log_index DESC) AS rn
  FROM `dissertation-bq.contract_rep.approvals_ego`
  WHERE block_timestamp >= TIMESTAMP(@start_ts)
    AND block_timestamp <= TIMESTAMP(@anchor_ts)
)
WHERE rn = 1 AND value > 0;

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.allow_pairs___TAG__` AS
SELECT owner, spender,
       COUNT(*) AS n_tokens,
       SUM(sig(age_days) * vt(value)) AS w_er,
       SUM(value) AS w_raw,
       MAX(sig(age_days)) AS max_sig,
       MAX(block_timestamp) AS last_ts
FROM `dissertation-bq.contract_rep.allow_triples___TAG__`
GROUP BY owner, spender;

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.transfer_pairs___TAG__` AS
SELECT from_address, to_address,
       COUNT(*) AS n_transfers,
       SUM(sig(age_days) * vt(value)) AS w_awp,
       SUM(value * sig(age_days)) AS w_raw,
       MAX(sig(age_days)) AS max_sig,
       SUM(value) AS sum_value,
       MIN(block_timestamp) AS first_ts,
       MAX(block_timestamp) AS last_ts
FROM (
  SELECT from_address, to_address, value, block_timestamp,
         TIMESTAMP_DIFF(TIMESTAMP(@anchor_ts), block_timestamp, MICROSECOND) / 8.64e10 AS age_days
  FROM `dissertation-bq.contract_rep.transfers_ego`
  WHERE block_timestamp >= TIMESTAMP(@start_ts)
    AND block_timestamp <= TIMESTAMP(@anchor_ts)
)
GROUP BY from_address, to_address;
