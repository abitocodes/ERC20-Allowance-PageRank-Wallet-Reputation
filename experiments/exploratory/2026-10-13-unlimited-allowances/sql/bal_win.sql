-- Exploratory: balance of the five listed tokens at t1 and at T_obs for every (token, owner) of
-- a latest allowance at t1 or T_obs: net Transfer flow before 2023-10-01 (x_bal_pre) plus the
-- net flow in logs_obs up to each anchor (inclusive). Base units, FLOAT64.
CREATE TEMP FUNCTION u256(v BYTES) AS (
  IFNULL((SELECT SUM(c * POW(256.0, LENGTH(v) - 1 - o))
          FROM UNNEST(TO_CODE_POINTS(v)) AS c WITH OFFSET o), 0.0)
);
CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.x_bal` AS
WITH owners AS (
  SELECT DISTINCT token_address, owner FROM `dissertation-bq.contract_rep.u_allow_triples_t1`
  UNION DISTINCT
  SELECT DISTINCT token_address, owner FROM `dissertation-bq.contract_rep.u_allow_triples_tobs`
),
t AS (
  SELECT emitter AS token_address, a, b, u256(val) AS v, block_timestamp
  FROM `dissertation-bq.contract_rep.logs_obs`
  WHERE kind = 'T' AND emitter IN (SELECT token FROM `dissertation-bq.contract_rep.u_tokens`)
    AND block_timestamp <= TIMESTAMP('2026-06-30 23:59:59 UTC')
),
flows AS (
  SELECT token_address, b AS addr, v AS d, block_timestamp FROM t
  UNION ALL
  SELECT token_address, a AS addr, -v AS d, block_timestamp FROM t
),
win AS (
  SELECT f.token_address, f.addr,
         SUM(IF(f.block_timestamp <= TIMESTAMP('2026-03-31 23:59:59 UTC'), f.d, 0.0)) AS net_t1,
         SUM(f.d) AS net_tobs,
         COUNT(*) AS n_win
  FROM flows AS f
  JOIN owners AS o ON o.token_address = f.token_address AND o.owner = f.addr
  GROUP BY f.token_address, f.addr
)
SELECT o.token_address, o.owner,
       IFNULL(p.net, 0.0) + IFNULL(w.net_t1, 0.0) AS bal_t1,
       IFNULL(p.net, 0.0) + IFNULL(w.net_tobs, 0.0) AS bal_tobs,
       IFNULL(p.n, 0) AS n_pre, IFNULL(w.n_win, 0) AS n_win, p.first_ts AS first_pre_ts
FROM owners AS o
LEFT JOIN `dissertation-bq.contract_rep.x_bal_pre` AS p ON p.token_address = o.token_address AND p.addr = o.owner
LEFT JOIN win AS w ON w.token_address = o.token_address AND w.addr = o.owner;
