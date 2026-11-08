-- Contract-graph revision (docs/revision_contract_graph.md section 5; job 37, step pairs): the pair tables of both
-- freezes, with the definitions of sql/14_usd_anchor_pairs.sql (lines 18-19 and the aggregates of lines 38-46 and
-- 50-59 copied; decay k = 0.01, t0 = 180 days).
--   c12_transfer_pairs: per (tag, sender, recipient), sql/14 lines 49-68 on the transfers between contracts
--     (c12_events_cc, kind 'T', usd IS NOT NULL) of the tag's score window up to its anchor. The t1 rows use the
--     predicates of sql/35_c12_structure.sql lines 44-47 word for word. One read of c12_events_cc serves both freezes.
--   c12_allow_pairs: the capped allowance layer, per (tag, owner, spender): sql/14 lines 37-47 over the triples with
--     usd_eff > 0 (c12_allow_triples), usd_eff in place of usd: w_er = sum of sigma(age) V_A(usd_eff), w_raw = sum of
--     min(usd_eff, U).
--   c12_allow_pairs_unc: the uncapped sensitivity (section 5), the same aggregates over every triple, usd_allow in
--     place of usd_eff.
-- Self-pairs are kept and no pair is dropped for a zero weight (V of a few base units is 0 in FLOAT64).
-- Inputs: contract_rep.c12_events_cc (sql/31), c12_allow_triples (job 36).
-- Parameters: @start_ts, @t1, @tobs_start, @tobs, @b_transfer, @b_allowance (1/USD), @cap_allowance (U, USD): the
--   constants of data/0-usd-token-list-and-prices/contract-12m/constants.json.

CREATE TEMP FUNCTION sig(age_days FLOAT64) AS (1.0 / (1.0 + EXP(0.01 * (age_days - 180.0))));
CREATE TEMP FUNCTION vt(z FLOAT64, b FLOAT64) AS (IF(b * z >= 40.0, 1.0, 2.0 / (1.0 + EXP(-b * z)) - 1.0));

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.c12_transfer_pairs`
CLUSTER BY tag
AS
SELECT tag, from_address, to_address,
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
  SELECT 't1' AS tag, a AS from_address, b AS to_address, usd, block_timestamp,
         TIMESTAMP_DIFF(TIMESTAMP(@t1), block_timestamp, MICROSECOND) / 8.64e10 AS age_days
  FROM `dissertation-bq.contract_rep.c12_events_cc`
  WHERE kind = 'T'
    AND block_timestamp >= TIMESTAMP(@start_ts)
    AND block_timestamp <= TIMESTAMP(@t1)
    AND usd IS NOT NULL
  UNION ALL
  SELECT 'tobs' AS tag, a AS from_address, b AS to_address, usd, block_timestamp,
         TIMESTAMP_DIFF(TIMESTAMP(@tobs), block_timestamp, MICROSECOND) / 8.64e10 AS age_days
  FROM `dissertation-bq.contract_rep.c12_events_cc`
  WHERE kind = 'T'
    AND block_timestamp >= TIMESTAMP(@tobs_start)
    AND block_timestamp <= TIMESTAMP(@tobs)
    AND usd IS NOT NULL
)
GROUP BY tag, from_address, to_address;

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.c12_allow_pairs`
CLUSTER BY tag
AS
SELECT tag, owner, spender,
       COUNT(*) AS n_tokens,
       SUM(sig(age_days) * vt(usd_eff, CAST(@b_allowance AS FLOAT64))) AS w_er,
       SUM(LEAST(usd_eff, CAST(@cap_allowance AS FLOAT64))) AS w_raw,
       MAX(sig(age_days)) AS max_sig,
       MAX(block_timestamp) AS last_ts,
       SUM(sig(age_days) * vt(usd_eff, 10.0 * CAST(@b_allowance AS FLOAT64))) AS w_er_b10x,
       SUM(sig(age_days) * vt(usd_eff, 0.1 * CAST(@b_allowance AS FLOAT64))) AS w_er_b01x
FROM `dissertation-bq.contract_rep.c12_allow_triples`
WHERE usd_eff > 0
GROUP BY tag, owner, spender;

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.c12_allow_pairs_unc`
CLUSTER BY tag
AS
SELECT tag, owner, spender,
       COUNT(*) AS n_tokens,
       SUM(sig(age_days) * vt(usd_allow, CAST(@b_allowance AS FLOAT64))) AS w_er,
       SUM(LEAST(usd_allow, CAST(@cap_allowance AS FLOAT64))) AS w_raw,
       MAX(sig(age_days)) AS max_sig,
       MAX(block_timestamp) AS last_ts,
       SUM(sig(age_days) * vt(usd_allow, 10.0 * CAST(@b_allowance AS FLOAT64))) AS w_er_b10x,
       SUM(sig(age_days) * vt(usd_allow, 0.1 * CAST(@b_allowance AS FLOAT64))) AS w_er_b01x
FROM `dissertation-bq.contract_rep.c12_allow_triples`
GROUP BY tag, owner, spender;
