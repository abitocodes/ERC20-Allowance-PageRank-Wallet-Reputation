-- Contract-graph revision (docs/revision_contract_graph.md section 7; job 36, step constants): the constants of the
-- contract graph, one value of each for both freezes, on the W0 score window (@start_ts to @t1, both inclusive), by
-- the rules of docs/revision_price_weighting.md section 5: BigQuery APPROX_QUANTILES over 10,000 buckets with the
-- offsets of sql/13_usd_constants.sql lines 37-41. The driver rounds them to two significant digits (usd.round_sig)
-- and writes data/0-usd-token-list-and-prices/contract-12m/constants.json.
--   m_transfer, p99_transfer: the median and the 99th percentile (U, the cap of the C-PR allowance layer) of the
--     US-dollar values of the transfers between contracts (c12_events_cc, kind 'T', usd IS NOT NULL; sql/13 lines
--     15-20 on c12_events_cc);
--   m_allowance: the median of the positive usd_eff of the latest allowances between contracts at t1
--     (c12_allow_triples, tag 't1'); every allowance enters, unlimited ones included, since the cap makes each one
--     finite;
--   p99_user_transfer: U_user, the 99th percentile of the US-dollar values of the transfers from user accounts to
--     contracts (c12_user_events, kind 'T', to_contract), the cap of the importance measures.
-- Inputs: contract_rep.c12_events_cc (sql/31), c12_allow_triples, c12_user_events (job 36).
-- Parameters: @start_ts, @t1 (inclusive), @unlimited (base units at or above which an allowance is unlimited).
--
-- c12_constants: one row (see the column list of the final SELECT).

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.c12_constants` AS
WITH tr AS (
  SELECT APPROX_QUANTILES(usd, 10000) AS q, COUNT(*) AS n
  FROM `dissertation-bq.contract_rep.c12_events_cc`
  WHERE kind = 'T'
    AND block_timestamp >= TIMESTAMP(@start_ts) AND block_timestamp <= TIMESTAMP(@t1)
    AND usd IS NOT NULL
),
al AS (
  SELECT APPROX_QUANTILES(IF(usd_eff > 0, usd_eff, NULL), 10000) AS q,
         COUNT(*) AS n_latest,
         COUNTIF(usd_eff > 0) AS n,
         COUNTIF(usd_eff = 0) AS n_zero,
         COUNTIF(usd_eff > 0 AND usd_eff < usd_allow) AS n_below,
         COUNTIF(usd_eff > 0 AND value >= CAST(@unlimited AS FLOAT64)) AS n_unlimited
  FROM `dissertation-bq.contract_rep.c12_allow_triples`
  WHERE tag = 't1'
),
ut AS (
  SELECT APPROX_QUANTILES(usd, 10000) AS q, COUNT(*) AS n
  FROM `dissertation-bq.contract_rep.c12_user_events`
  WHERE kind = 'T' AND to_contract
    AND block_timestamp >= TIMESTAMP(@start_ts) AND block_timestamp <= TIMESTAMP(@t1)
)
SELECT tr.q[OFFSET(5000)] AS m_transfer, tr.q[OFFSET(9900)] AS p99_transfer,
       tr.q[OFFSET(1000)] AS p10_transfer, tr.q[OFFSET(9000)] AS p90_transfer, tr.n AS n_transfers,
       al.q[OFFSET(5000)] AS m_allowance, al.q[OFFSET(9900)] AS p99_allowance,
       al.q[OFFSET(1000)] AS p10_allowance, al.q[OFFSET(9000)] AS p90_allowance,
       al.n_latest AS n_latest_allowances, al.n AS n_positive_allowances, al.n_zero AS n_capped_to_zero,
       al.n_below AS n_capped_below_allowance, al.n_unlimited AS n_unlimited_positive,
       ut.q[OFFSET(5000)] AS m_user_transfer, ut.q[OFFSET(9900)] AS p99_user_transfer,
       ut.q[OFFSET(1000)] AS p10_user_transfer, ut.q[OFFSET(9000)] AS p90_user_transfer,
       ut.n AS n_user_transfers
FROM tr CROSS JOIN al CROSS JOIN ut;
