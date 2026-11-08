-- Contract-graph revision (docs/revision_contract_graph.md, sections 5 to 7 and the gate B amendment of section 13;
-- job 36, step constants): the latest allowances between contracts at both freezes, valued at the anchor day's
-- price and capped at the owner's balance at the anchor. They need no constant, so they are built once, before the
-- constants: m_A is the median of their positive usd_eff at t1 (sql/36_c12_constants.sql).
-- For each freeze, the latest Approval of each (token, owner, spender) of c12_events_cc in the score window up to the
-- anchor, in (block number, log index) order, kept when its value is positive. The t1 branch has the predicates of
-- sql/35_c12_structure.sql lines 24-30 word for word (block_timestamp is added to its select list), so its pairs are
-- the structure pilot's allow_uncapped pairs, and those with usd_eff > 0 its allow_capped pairs: usd_eff > 0 holds
-- exactly when the balance test of sql/35 line 38 holds and the price is positive (docs/discovery_protocol.md
-- section 8).
--   usd_allow = amount x the token's price on the UTC day of the anchor, amount = value / 10^decimals (the expression
--     of sql/24_c12_logs5.sql line 50, so the column amount of c12_events_cc is not read);
--   usd_bal   = the owner's balance at the anchor (c12_bal, base units) set to 0 unless it is at least
--     10^(decimals - @dust_digits) base units (sql/35 line 38: a negative or missing balance gives 0), in token
--     units, x the same price;
--   usd_eff   = LEAST(usd_allow, usd_bal).
-- Rows with usd_eff = 0 stay (the uncapped sensitivity and sql/42 read them); the capped pairs of sql/37 leave them
-- out, as sql/14_usd_anchor_pairs.sql aggregates only the triples it keeps.
-- Inputs: contract_rep.c12_events_cc (sql/31), c12_bal (sql/33), u_tokens, u_prices.
-- Parameters: @start_ts, @t1 (the W0 score window, both inclusive), @tobs_start, @tobs (the T_obs score window),
--   @dust_digits.
--
-- c12_allow_triples: tag ('t1' or 'tobs'), token, owner, spender (20-byte BYTES), value (base units), amount (token
--   units), decimals, price_usd (anchor day), bal (c12_bal at the anchor, base units, not clipped; NULL without a
--   row), usd_allow, usd_bal, usd_eff (USD), block_timestamp (of the latest approval), age_days (to the anchor).
--   One row per (tag, token, owner, spender); clustered by tag.

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.c12_allow_triples`
CLUSTER BY tag
AS
WITH latest_t1 AS (
  SELECT token, owner, spender, value, block_timestamp
  FROM (
    SELECT token, a AS owner, b AS spender, value, block_timestamp,
           ROW_NUMBER() OVER (PARTITION BY token, a, b ORDER BY block_number DESC, log_index DESC) AS rn
    FROM `dissertation-bq.contract_rep.c12_events_cc`
    WHERE kind = 'A'
      AND block_timestamp >= TIMESTAMP(@start_ts)
      AND block_timestamp <= TIMESTAMP(@t1)
  )
  WHERE rn = 1 AND value > 0
),
latest_tobs AS (
  SELECT token, owner, spender, value, block_timestamp
  FROM (
    SELECT token, a AS owner, b AS spender, value, block_timestamp,
           ROW_NUMBER() OVER (PARTITION BY token, a, b ORDER BY block_number DESC, log_index DESC) AS rn
    FROM `dissertation-bq.contract_rep.c12_events_cc`
    WHERE kind = 'A'
      AND block_timestamp >= TIMESTAMP(@tobs_start)
      AND block_timestamp <= TIMESTAMP(@tobs)
  )
  WHERE rn = 1 AND value > 0
),
valued AS (
  SELECT 't1' AS tag, l.token, l.owner, l.spender, l.value, t.decimals, p.price_usd, b.bal_t1 AS bal,
         l.block_timestamp,
         TIMESTAMP_DIFF(TIMESTAMP(@t1), l.block_timestamp, MICROSECOND) / 8.64e10 AS age_days
  FROM latest_t1 AS l
  JOIN `dissertation-bq.contract_rep.u_tokens` AS t ON t.token = l.token
  JOIN `dissertation-bq.contract_rep.u_prices` AS p ON p.token = l.token AND p.day = DATE(TIMESTAMP(@t1))
  LEFT JOIN `dissertation-bq.contract_rep.c12_bal` AS b ON b.token = l.token AND b.address = l.owner
  UNION ALL
  SELECT 'tobs' AS tag, l.token, l.owner, l.spender, l.value, t.decimals, p.price_usd, b.bal_tobs AS bal,
         l.block_timestamp,
         TIMESTAMP_DIFF(TIMESTAMP(@tobs), l.block_timestamp, MICROSECOND) / 8.64e10 AS age_days
  FROM latest_tobs AS l
  JOIN `dissertation-bq.contract_rep.u_tokens` AS t ON t.token = l.token
  JOIN `dissertation-bq.contract_rep.u_prices` AS p ON p.token = l.token AND p.day = DATE(TIMESTAMP(@tobs))
  LEFT JOIN `dissertation-bq.contract_rep.c12_bal` AS b ON b.token = l.token AND b.address = l.owner
)
SELECT tag, token, owner, spender, value,
       value / POW(10.0, decimals) AS amount,
       decimals, price_usd, bal,
       value / POW(10.0, decimals) * price_usd AS usd_allow,
       IF(bal >= POW(10.0, decimals - CAST(@dust_digits AS INT64)), bal, 0.0) / POW(10.0, decimals) * price_usd
         AS usd_bal,
       LEAST(value / POW(10.0, decimals) * price_usd,
             IF(bal >= POW(10.0, decimals - CAST(@dust_digits AS INT64)), bal, 0.0) / POW(10.0, decimals) * price_usd)
         AS usd_eff,
       block_timestamp, age_days
FROM valued;
