-- Aave V3 Pool lending events on Arbitrum One, filtered to wallet set
-- Parameters: @start_ts, @end_ts, @pool_addresses (ARRAY<STRING>),
--             @borrow_topic0, @repay_topic0, @liquidation_topic0,
--             @wallet_addresses (ARRAY<STRING>)

SELECT
  block_timestamp,
  block_number,
  transaction_hash,
  log_index,
  address AS pool_address,
  topics[SAFE_OFFSET(0)] AS topic0,
  topics[SAFE_OFFSET(1)] AS topic1,
  topics[SAFE_OFFSET(2)] AS topic2,
  topics[SAFE_OFFSET(3)] AS topic3,
  data AS event_data
FROM
  `__LOGS_FQN__`
WHERE
  block_timestamp >= TIMESTAMP(@start_ts)
  AND block_timestamp < TIMESTAMP(@end_ts)
  AND LOWER(address) IN UNNEST(@pool_addresses)
  AND topics[SAFE_OFFSET(0)] IN (
    @borrow_topic0,
    @repay_topic0,
    @liquidation_topic0
  )
  AND (
    -- Borrow: onBehalfOf in topic2
    (
      topics[SAFE_OFFSET(0)] = @borrow_topic0
      AND LOWER(CONCAT('0x', SUBSTR(topics[SAFE_OFFSET(2)], 27))) IN UNNEST(@wallet_addresses)
    )
    OR
    -- Repay: user in topic2
    (
      topics[SAFE_OFFSET(0)] = @repay_topic0
      AND LOWER(CONCAT('0x', SUBSTR(topics[SAFE_OFFSET(2)], 27))) IN UNNEST(@wallet_addresses)
    )
    OR
    -- LiquidationCall: user in topic3
    (
      topics[SAFE_OFFSET(0)] = @liquidation_topic0
      AND LOWER(CONCAT('0x', SUBSTR(topics[SAFE_OFFSET(3)], 27))) IN UNNEST(@wallet_addresses)
    )
  )
