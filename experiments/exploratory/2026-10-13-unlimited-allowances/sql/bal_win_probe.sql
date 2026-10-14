CREATE TEMP FUNCTION u256(v BYTES) AS (
  IFNULL((SELECT SUM(c * POW(256.0, LENGTH(v) - 1 - o))
          FROM UNNEST(TO_CODE_POINTS(v)) AS c WITH OFFSET o), 0.0)
);
SELECT emitter, a, b, u256(val) AS v, block_timestamp
FROM `dissertation-bq.contract_rep.logs_obs`
WHERE kind = 'T' AND emitter IN (SELECT token FROM `dissertation-bq.contract_rep.u_tokens`)
  AND block_timestamp <= TIMESTAMP('2026-06-30 23:59:59 UTC')
