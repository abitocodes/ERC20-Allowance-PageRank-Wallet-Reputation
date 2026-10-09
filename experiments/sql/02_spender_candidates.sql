-- Cohort candidates: spenders that received a non-zero Approval from at least three
-- distinct owners inside the observation window (analysis plan, section 3).
-- The account type of each candidate is read afterwards with eth_getCode.
-- Destination: contract_rep.spender_candidates.

CREATE OR REPLACE TABLE `__DEST__` AS
SELECT
  CONCAT('0x', TO_HEX(b)) AS spender,
  COUNT(DISTINCT a) AS owners_nonzero,
  COUNT(*) AS approval_logs,
  MIN(block_timestamp) AS first_ts,
  MAX(block_timestamp) AS last_ts
FROM `dissertation-bq.contract_rep.logs_obs`
WHERE kind = 'A'
  AND block_timestamp >= TIMESTAMP(@start_ts)
  AND block_timestamp < TIMESTAMP(@end_ts)
  AND LTRIM(TO_HEX(val), '0') != ''
GROUP BY b
HAVING COUNT(DISTINCT a) >= 3
