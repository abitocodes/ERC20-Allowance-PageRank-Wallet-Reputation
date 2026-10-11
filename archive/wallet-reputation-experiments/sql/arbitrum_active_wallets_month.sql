-- Per-month wallet transfer activity (for batched active-wallet sampling).
-- Parameters: @start_ts, @end_ts, @transfer_topic0

WITH transfers AS (
  SELECT
    LOWER(CONCAT('0x', SUBSTR(topics[SAFE_OFFSET(1)], 27))) AS from_address,
    LOWER(CONCAT('0x', SUBSTR(topics[SAFE_OFFSET(2)], 27))) AS to_address
  FROM
    `__LOGS_FQN__`
  WHERE
    block_timestamp >= TIMESTAMP(@start_ts)
    AND block_timestamp < TIMESTAMP(@end_ts)
    AND ARRAY_LENGTH(topics) >= 3
    AND topics[SAFE_OFFSET(0)] = @transfer_topic0
),
wallet_activity AS (
  SELECT wallet, SUM(evt_count) AS activity
  FROM (
    SELECT from_address AS wallet, COUNT(*) AS evt_count
    FROM transfers
    WHERE from_address IS NOT NULL AND from_address != '0x'
    GROUP BY from_address
    UNION ALL
    SELECT to_address AS wallet, COUNT(*) AS evt_count
    FROM transfers
    WHERE to_address IS NOT NULL AND to_address != '0x'
    GROUP BY to_address
  )
  GROUP BY wallet
)
SELECT wallet, activity
FROM wallet_activity
WHERE wallet LIKE '0x%'
