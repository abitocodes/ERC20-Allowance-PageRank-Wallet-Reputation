-- Revised analysis: edge aggregates of the two graphs at one anchor (T_obs or a freeze date)
-- from the listed-token ego events of 12_usd_ego.sql, with amounts in USD.
-- Parameters: @start_ts, @anchor_ts (inclusive), @b_transfer, @b_allowance (value-transform
-- slopes, 1/USD), @cap_allowance (USD at which an allowance is capped in the C-PR allowance
-- layer). The constants come from 13_usd_constants.sql and docs/revision_price_weighting.md.
-- __TAG__ names the anchor (tobs, t1). Decay as in 04_anchor_pairs.sql: k = 0.01, t0 = 180 days.
--
-- u_allow_triples___TAG__: latest approval of each (token, owner, spender) up to the anchor,
--   in (block number, log index) order, kept when its value is positive; usd = amount x the
--   token's price on the UTC day of the anchor.
-- u_allow_pairs___TAG__:   per (owner, spender): tokens, EndorseRank weight sum sigma*V(usd),
--   capped USD allowance sum (C-PR allowance layer), largest sigma, latest approval time,
--   and the EndorseRank weights with the slope multiplied and divided by ten (sensitivity).
-- u_transfer_pairs___TAG__: per (sender, recipient): transfers, AWP weight sum sigma*V(usd),
--   USD layer sum usd*sigma (C-PR transfer layer), largest sigma (AWP activeness), summed USD,
--   first and last transfer time, and the AWP weights with the slope multiplied and divided by ten.

CREATE TEMP FUNCTION sig(age_days FLOAT64) AS (1.0 / (1.0 + EXP(0.01 * (age_days - 180.0))));
CREATE TEMP FUNCTION vt(z FLOAT64, b FLOAT64) AS (IF(b * z >= 40.0, 1.0, 2.0 / (1.0 + EXP(-b * z)) - 1.0));

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.u_allow_triples___TAG__` AS
SELECT r.token_address, r.owner, r.spender, r.value, r.amount, r.amount * p.price_usd AS usd,
       r.block_timestamp,
       TIMESTAMP_DIFF(TIMESTAMP(@anchor_ts), r.block_timestamp, MICROSECOND) / 8.64e10 AS age_days
FROM (
  SELECT *, ROW_NUMBER() OVER (
           PARTITION BY token_address, owner, spender
           ORDER BY block_number DESC, log_index DESC) AS rn
  FROM `dissertation-bq.contract_rep.u_approvals`
  WHERE block_timestamp >= TIMESTAMP(@start_ts)
    AND block_timestamp <= TIMESTAMP(@anchor_ts)
) AS r
JOIN `dissertation-bq.contract_rep.u_prices` AS p
  ON p.token = r.token_address AND p.day = DATE(TIMESTAMP(@anchor_ts))
WHERE r.rn = 1 AND r.value > 0;

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.u_allow_pairs___TAG__` AS
SELECT owner, spender,
       COUNT(*) AS n_tokens,
       SUM(sig(age_days) * vt(usd, CAST(@b_allowance AS FLOAT64))) AS w_er,
       SUM(LEAST(usd, CAST(@cap_allowance AS FLOAT64))) AS w_raw,
       MAX(sig(age_days)) AS max_sig,
       MAX(block_timestamp) AS last_ts,
       SUM(sig(age_days) * vt(usd, 10.0 * CAST(@b_allowance AS FLOAT64))) AS w_er_b10x,
       SUM(sig(age_days) * vt(usd, 0.1 * CAST(@b_allowance AS FLOAT64))) AS w_er_b01x
FROM `dissertation-bq.contract_rep.u_allow_triples___TAG__`
GROUP BY owner, spender;

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.u_transfer_pairs___TAG__` AS
SELECT from_address, to_address,
       COUNT(*) AS n_transfers,
       SUM(sig(age_days) * vt(usd, CAST(@b_transfer AS FLOAT64))) AS w_awp,
       SUM(usd * sig(age_days)) AS w_raw,
       MAX(sig(age_days)) AS max_sig,
       SUM(usd) AS sum_usd,
       MIN(block_timestamp) AS first_ts,
       MAX(block_timestamp) AS last_ts,
       SUM(sig(age_days) * vt(usd, 10.0 * CAST(@b_transfer AS FLOAT64))) AS w_awp_b10x,
       SUM(sig(age_days) * vt(usd, 0.1 * CAST(@b_transfer AS FLOAT64))) AS w_awp_b01x
FROM (
  SELECT from_address, to_address, usd, block_timestamp,
         TIMESTAMP_DIFF(TIMESTAMP(@anchor_ts), block_timestamp, MICROSECOND) / 8.64e10 AS age_days
  FROM `dissertation-bq.contract_rep.u_transfers`
  WHERE block_timestamp >= TIMESTAMP(@start_ts)
    AND block_timestamp <= TIMESTAMP(@anchor_ts)
)
GROUP BY from_address, to_address;
