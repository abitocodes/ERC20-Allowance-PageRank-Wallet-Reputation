-- Exploratory check: 1,500 sampled (token, owner) pairs of x_bal, 150 with a zero and 150 with a
-- positive T_obs balance per token, and their balance on 2026-09-30 (T_obs + net flow in logs_w1).
CREATE TEMP FUNCTION u256(v BYTES) AS (
  IFNULL((SELECT SUM(c * POW(256.0, LENGTH(v) - 1 - o))
          FROM UNNEST(TO_CODE_POINTS(v)) AS c WITH OFFSET o), 0.0)
);
CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.x_bal_check` AS
WITH s AS (
  SELECT * FROM (
    SELECT b.*, ROW_NUMBER() OVER (PARTITION BY token_address, ABS(bal_tobs) > 1
                                   ORDER BY FARM_FINGERPRINT(CONCAT(TO_HEX(token_address), TO_HEX(owner)))) AS r
    FROM `dissertation-bq.contract_rep.x_bal` AS b)
  WHERE r <= 150
),
t AS (
  SELECT emitter AS token_address, a, b, u256(val) AS v
  FROM `dissertation-bq.contract_rep.logs_w1`
  WHERE kind = 'T' AND emitter IN (SELECT token FROM `dissertation-bq.contract_rep.u_tokens`)
    AND block_timestamp <= TIMESTAMP('2026-09-30 23:59:59 UTC')
),
f AS (
  SELECT token_address, b AS addr, v AS d FROM t UNION ALL SELECT token_address, a, -v FROM t
),
w AS (
  SELECT f.token_address, f.addr, SUM(f.d) AS net, COUNT(*) AS n
  FROM f JOIN s ON s.token_address = f.token_address AND s.owner = f.addr
  GROUP BY 1, 2
)
SELECT CONCAT('0x', TO_HEX(s.token_address)) AS token, CONCAT('0x', TO_HEX(s.owner)) AS owner,
       s.bal_tobs, s.bal_tobs + IFNULL(w.net, 0.0) AS bal_0930, IFNULL(w.n, 0) AS n_w1
FROM s LEFT JOIN w ON w.token_address = s.token_address AND w.addr = s.owner;
