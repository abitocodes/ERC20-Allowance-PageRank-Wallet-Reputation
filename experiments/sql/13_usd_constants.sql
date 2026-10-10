-- Revised analysis: the USD scale constants, from events up to the earliest freeze t1
-- (31 March 2026) only, so that no event of a label window enters them.
-- Parameters: @start_ts, @t1 (inclusive), @unlimited (base units at or above which an allowance
-- is unlimited, as in 10_describe.sql). Destination: contract_rep.u_constants (one row).
--
-- m_transfer:  median USD value of the ego transfers of listed tokens up to t1.
-- m_allowance: median USD value, at t1 prices, of the finite positive latest allowances at t1.
-- p99_allowance: 99th percentile of the same finite allowances.
-- Quantiles are BigQuery APPROX_QUANTILES over 10,000 buckets; the constants of the analysis
-- are these values rounded to two significant digits (docs/revision_price_weighting.md).

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.u_constants` AS
WITH tr AS (
  SELECT APPROX_QUANTILES(usd, 10000) AS q, COUNT(*) AS n
  FROM `dissertation-bq.contract_rep.u_transfers`
  WHERE block_timestamp >= TIMESTAMP(@start_ts) AND block_timestamp <= TIMESTAMP(@t1)
),
latest AS (
  SELECT token_address, value, amount,
         ROW_NUMBER() OVER (PARTITION BY token_address, owner, spender
                            ORDER BY block_number DESC, log_index DESC) AS rn
  FROM `dissertation-bq.contract_rep.u_approvals`
  WHERE block_timestamp >= TIMESTAMP(@start_ts) AND block_timestamp <= TIMESTAMP(@t1)
),
al AS (
  SELECT APPROX_QUANTILES(IF(l.value < CAST(@unlimited AS FLOAT64), l.amount * p.price_usd, NULL), 10000) AS q,
         COUNTIF(l.value < CAST(@unlimited AS FLOAT64)) AS n,
         COUNTIF(l.value >= CAST(@unlimited AS FLOAT64)) AS n_unlimited
  FROM latest AS l
  JOIN `dissertation-bq.contract_rep.u_prices` AS p
    ON p.token = l.token_address AND p.day = DATE(TIMESTAMP(@t1))
  WHERE l.rn = 1 AND l.value > 0
)
SELECT tr.q[OFFSET(5000)] AS m_transfer, tr.n AS n_transfers,
       al.q[OFFSET(5000)] AS m_allowance, al.q[OFFSET(9900)] AS p99_allowance, al.n AS n_finite_allowances,
       al.n_unlimited AS n_unlimited_allowances,
       tr.q[OFFSET(1000)] AS p10_transfer, tr.q[OFFSET(9000)] AS p90_transfer,
       al.q[OFFSET(1000)] AS p10_allowance, al.q[OFFSET(9000)] AS p90_allowance
FROM tr CROSS JOIN al;
