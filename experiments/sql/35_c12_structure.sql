-- Contract-graph revision (docs/revision_contract_graph.md, sections 5 and 12, and docs/discovery_protocol.md
-- section 7; job 35): the structure of the contract graph at t1 for the structure pilot, without any weight.
-- Window: @start_ts (2025-04-01) to @t1 (2026-03-31 23:59:59 UTC, inclusive), the W0 score window.
--   allow_uncapped  the distinct (owner, spender) of the latest approval of each (token, owner, spender) of
--                   c12_events_cc in the window, in (block number, log index) order, kept when its value is
--                   positive (both ends are contracts by construction of c12_events_cc);
--   allow_capped    those pairs with at least one such token whose owner holds at t1 at least
--                   10^(decimals - @dust_digits) base units of it (c12_bal.bal_t1; 10^-6 token) and whose price
--                   on the UTC day of t1 is positive, so that the balance-capped value usd_eff is positive;
--   transfer        the distinct (sender, recipient) of the transfers of c12_events_cc in the window that have
--                   a US-dollar value (usd IS NOT NULL), as in sql/14.
-- Self-pairs are kept, as the solver keeps them.
-- Inputs: contract_rep.c12_events_cc (sql/31), c12_bal (sql/33), u_tokens, u_prices.
-- Parameters: @start_ts, @t1, @dust_digits.
--
-- c12_struct_t1: a, b (lowercase 0x hex STRING), layer ('allow_capped', 'allow_uncapped' or 'transfer'); one row
--   per distinct pair and layer.

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.c12_struct_t1` AS
WITH latest AS (
  SELECT token, owner, spender
  FROM (
    SELECT token, a AS owner, b AS spender, value,
           ROW_NUMBER() OVER (PARTITION BY token, a, b ORDER BY block_number DESC, log_index DESC) AS rn
    FROM `dissertation-bq.contract_rep.c12_events_cc`
    WHERE kind = 'A'
      AND block_timestamp >= TIMESTAMP(@start_ts)
      AND block_timestamp <= TIMESTAMP(@t1)
  )
  WHERE rn = 1 AND value > 0
),
capped AS (
  SELECT DISTINCT l.owner, l.spender
  FROM latest AS l
  JOIN `dissertation-bq.contract_rep.u_tokens` AS t ON t.token = l.token
  JOIN `dissertation-bq.contract_rep.c12_bal` AS b ON b.token = l.token AND b.address = l.owner
  JOIN `dissertation-bq.contract_rep.u_prices` AS p ON p.token = l.token AND p.day = DATE(TIMESTAMP(@t1))
  WHERE b.bal_t1 >= POW(10.0, t.decimals - CAST(@dust_digits AS INT64))
    AND p.price_usd > 0
),
transfers AS (
  SELECT DISTINCT a, b
  FROM `dissertation-bq.contract_rep.c12_events_cc`
  WHERE kind = 'T'
    AND block_timestamp >= TIMESTAMP(@start_ts)
    AND block_timestamp <= TIMESTAMP(@t1)
    AND usd IS NOT NULL
)
SELECT CONCAT('0x', TO_HEX(owner)) AS a, CONCAT('0x', TO_HEX(spender)) AS b, 'allow_uncapped' AS layer
FROM (SELECT DISTINCT owner, spender FROM latest)
UNION ALL
SELECT CONCAT('0x', TO_HEX(owner)) AS a, CONCAT('0x', TO_HEX(spender)) AS b, 'allow_capped' AS layer
FROM capped
UNION ALL
SELECT CONCAT('0x', TO_HEX(a)) AS a, CONCAT('0x', TO_HEX(b)) AS b, 'transfer' AS layer
FROM transfers;
