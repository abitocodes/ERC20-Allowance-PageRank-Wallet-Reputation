-- Contract-graph revision (docs/discovery_protocol.md sections 5, 6 and 8, revision section 7 and the gate B
-- amendment of section 13; job 41, step rest): the importance measures of the discovery-order test at both freezes,
-- the US dollars that user accounts sent to untyped addresses, and the description of the allowances between
-- contracts.
--   c12_importance_raw: from the user-account events of c12_user_events (job 36), per tag and contract c:
--     i_t = the sum over user accounts w of LEAST(S_T(w, c), @cap_user), S_T the US dollars w transferred to c in the
--       score window (each transfer at the price of its UTC day);
--     i_a = the sum over w of LEAST(S_A(w, c), @cap_user), S_A the sum over tokens of usd_eff(w, c): the latest
--       approval of w to c in the score window up to the anchor, in (block number, log index) order, counted when
--       its value is positive, capped at w's balance at the anchor (c12_bal, the base-unit test of sql/35 line 38)
--       and valued at the anchor day's price, with the expression of usd_eff of sql/36_c12_allow_triples.sql;
--     n_t, n_a = the user accounts with S_T, S_A of at least @min_usd.
--     One row per tag and contract (part 'contract'), and one row per tag (part 'untyped') whose usd is the plain sum,
--     without a cap, of the transfers from user accounts to the untyped addresses (to_contract false).
--   c12_importance_{tobs,t1}: every contract with i_t > 0 or i_a > 0, with its node id (c12_nodes), -1 outside it.
--   c12_inflow_untyped_{tobs,t1}: one row, usd (0 without such a transfer).
--   c12_describe_allowances: per tag and token, the counts and sums of the latest allowances between contracts
--     (c12_allow_triples): every one, positive usd_eff, capped to zero, capped below the allowance, unlimited, finite,
--     usd_eff and usd_allow at or above U; the sum of usd_eff and the sum of the finite usd_allow.
-- @cap_user is U_user and @cap_allowance U of data/0-usd-token-list-and-prices/contract-12m/constants.json; @min_usd
-- is discovery.min_usd_account of the overlay; @unlimited the base units at or above which an allowance is unlimited.
-- Inputs: contract_rep.c12_user_events, c12_allow_triples (job 36), c12_bal (sql/33), u_tokens, u_prices, c12_nodes
--   (sql/40).

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.c12_importance_raw` AS
WITH ev AS (
  SELECT kind, token, a, b, value, usd, block_number, log_index, block_timestamp, to_contract
  FROM `dissertation-bq.contract_rep.c12_user_events`
),
flows AS (
  SELECT 't1' AS tag, a AS w, b AS c, SUM(usd) AS s
  FROM ev
  WHERE kind = 'T' AND to_contract
    AND block_timestamp >= TIMESTAMP(@start_ts) AND block_timestamp <= TIMESTAMP(@t1)
  GROUP BY a, b
  UNION ALL
  SELECT 'tobs' AS tag, a AS w, b AS c, SUM(usd) AS s
  FROM ev
  WHERE kind = 'T' AND to_contract
    AND block_timestamp >= TIMESTAMP(@tobs_start) AND block_timestamp <= TIMESTAMP(@tobs)
  GROUP BY a, b
),
latest AS (
  SELECT 't1' AS tag, token, owner, spender, value
  FROM (
    SELECT token, a AS owner, b AS spender, value,
           ROW_NUMBER() OVER (PARTITION BY token, a, b ORDER BY block_number DESC, log_index DESC) AS rn
    FROM ev
    WHERE kind = 'A'
      AND block_timestamp >= TIMESTAMP(@start_ts)
      AND block_timestamp <= TIMESTAMP(@t1)
  )
  WHERE rn = 1 AND value > 0
  UNION ALL
  SELECT 'tobs' AS tag, token, owner, spender, value
  FROM (
    SELECT token, a AS owner, b AS spender, value,
           ROW_NUMBER() OVER (PARTITION BY token, a, b ORDER BY block_number DESC, log_index DESC) AS rn
    FROM ev
    WHERE kind = 'A'
      AND block_timestamp >= TIMESTAMP(@tobs_start)
      AND block_timestamp <= TIMESTAMP(@tobs)
  )
  WHERE rn = 1 AND value > 0
),
priced AS (
  SELECT l.tag, l.owner, l.spender, l.value, t.decimals, p.price_usd,
         IF(l.tag = 't1', b.bal_t1, b.bal_tobs) AS bal
  FROM latest AS l
  JOIN `dissertation-bq.contract_rep.u_tokens` AS t ON t.token = l.token
  JOIN `dissertation-bq.contract_rep.u_prices` AS p
    ON p.token = l.token AND p.day = IF(l.tag = 't1', DATE(TIMESTAMP(@t1)), DATE(TIMESTAMP(@tobs)))
  LEFT JOIN `dissertation-bq.contract_rep.c12_bal` AS b ON b.token = l.token AND b.address = l.owner
),
auth AS (
  SELECT tag, owner AS w, spender AS c,
         SUM(LEAST(value / POW(10.0, decimals) * price_usd,
                   IF(bal >= POW(10.0, decimals - CAST(@dust_digits AS INT64)), bal, 0.0) / POW(10.0, decimals) * price_usd))
           AS s
  FROM priced
  GROUP BY tag, owner, spender
),
it AS (
  SELECT tag, c, SUM(LEAST(s, CAST(@cap_user AS FLOAT64))) AS i_t, COUNTIF(s >= CAST(@min_usd AS FLOAT64)) AS n_t
  FROM flows
  GROUP BY tag, c
),
ia AS (
  SELECT tag, c, SUM(LEAST(s, CAST(@cap_user AS FLOAT64))) AS i_a, COUNTIF(s >= CAST(@min_usd AS FLOAT64)) AS n_a
  FROM auth
  GROUP BY tag, c
),
untyped AS (
  SELECT 't1' AS tag, SUM(usd) AS usd
  FROM ev
  WHERE kind = 'T' AND NOT to_contract
    AND block_timestamp >= TIMESTAMP(@start_ts) AND block_timestamp <= TIMESTAMP(@t1)
  UNION ALL
  SELECT 'tobs' AS tag, SUM(usd) AS usd
  FROM ev
  WHERE kind = 'T' AND NOT to_contract
    AND block_timestamp >= TIMESTAMP(@tobs_start) AND block_timestamp <= TIMESTAMP(@tobs)
)
SELECT tag, 'contract' AS part, c AS address,
       IFNULL(it.i_t, 0.0) AS i_t, IFNULL(ia.i_a, 0.0) AS i_a,
       IFNULL(it.n_t, 0) AS n_t, IFNULL(ia.n_a, 0) AS n_a,
       CAST(NULL AS FLOAT64) AS usd
FROM it FULL OUTER JOIN ia USING (tag, c)
UNION ALL
SELECT tag, 'untyped' AS part, CAST(NULL AS BYTES) AS address, 0.0 AS i_t, 0.0 AS i_a, 0 AS n_t, 0 AS n_a,
       IFNULL(usd, 0.0) AS usd
FROM untyped;

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.c12_importance_tobs` AS
SELECT IFNULL(n.id, -1) AS id, CONCAT('0x', TO_HEX(r.address)) AS address, r.i_t, r.i_a, r.n_t, r.n_a
FROM `dissertation-bq.contract_rep.c12_importance_raw` AS r
LEFT JOIN `dissertation-bq.contract_rep.c12_nodes` AS n ON n.address_bytes = r.address
WHERE r.tag = 'tobs' AND r.part = 'contract' AND (r.i_t > 0 OR r.i_a > 0);

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.c12_importance_t1` AS
SELECT IFNULL(n.id, -1) AS id, CONCAT('0x', TO_HEX(r.address)) AS address, r.i_t, r.i_a, r.n_t, r.n_a
FROM `dissertation-bq.contract_rep.c12_importance_raw` AS r
LEFT JOIN `dissertation-bq.contract_rep.c12_nodes` AS n ON n.address_bytes = r.address
WHERE r.tag = 't1' AND r.part = 'contract' AND (r.i_t > 0 OR r.i_a > 0);

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.c12_inflow_untyped_tobs` AS
SELECT IFNULL(SUM(usd), 0.0) AS usd
FROM `dissertation-bq.contract_rep.c12_importance_raw`
WHERE tag = 'tobs' AND part = 'untyped';

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.c12_inflow_untyped_t1` AS
SELECT IFNULL(SUM(usd), 0.0) AS usd
FROM `dissertation-bq.contract_rep.c12_importance_raw`
WHERE tag = 't1' AND part = 'untyped';

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.c12_describe_allowances` AS
SELECT tag, CONCAT('0x', TO_HEX(token)) AS token,
       COUNT(*) AS n_latest_positive,
       COUNTIF(usd_eff > 0) AS n_positive_eff,
       COUNTIF(usd_eff = 0) AS n_capped_to_zero,
       COUNTIF(usd_eff > 0 AND usd_eff < usd_allow) AS n_capped_below_allowance,
       COUNTIF(value >= CAST(@unlimited AS FLOAT64)) AS n_unlimited,
       COUNTIF(value < CAST(@unlimited AS FLOAT64)) AS n_finite,
       COUNTIF(usd_eff >= CAST(@cap_allowance AS FLOAT64)) AS n_eff_at_or_above_cap,
       COUNTIF(usd_allow >= CAST(@cap_allowance AS FLOAT64)) AS n_allow_at_or_above_cap,
       SUM(usd_eff) AS sum_usd_eff,
       SUM(IF(value < CAST(@unlimited AS FLOAT64), usd_allow, 0.0)) AS sum_usd_allow_finite
FROM `dissertation-bq.contract_rep.c12_allow_triples`
GROUP BY 1, 2;
