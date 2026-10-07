-- ERC-20 Approval events on Arbitrum One, filtered to wallet set
-- Parameters: @start_ts, @end_ts, @approval_topic0, @wallet_addresses (ARRAY<STRING>)

SELECT
  block_timestamp,
  block_number,
  transaction_hash,
  log_index,
  address AS token_address,
  topics[SAFE_OFFSET(1)] AS owner_topic,
  topics[SAFE_OFFSET(2)] AS spender_topic,
  data AS value_data
FROM
  `__LOGS_FQN__`
WHERE
  block_timestamp >= TIMESTAMP(@start_ts)
  AND block_timestamp < TIMESTAMP(@end_ts)
  AND ARRAY_LENGTH(topics) >= 3
  AND topics[SAFE_OFFSET(0)] = @approval_topic0
  AND (
    LOWER(CONCAT('0x', SUBSTR(topics[SAFE_OFFSET(1)], 27))) IN UNNEST(@wallet_addresses)
    OR LOWER(CONCAT('0x', SUBSTR(topics[SAFE_OFFSET(2)], 27))) IN UNNEST(@wallet_addresses)
  )
