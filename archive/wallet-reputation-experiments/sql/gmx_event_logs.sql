-- GMX V2 EventEmitter PositionDecrease logs (Arbitrum)
-- Parameters: @start_ts, @end_ts, @event_emitter, @event_log1_topic0, @position_decrease_hash

SELECT
  block_timestamp,
  block_number,
  transaction_hash,
  log_index,
  address,
  topics,
  data
FROM
  `__LOGS_FQN__`
WHERE
  block_timestamp >= TIMESTAMP(@start_ts)
  AND block_timestamp < TIMESTAMP(@end_ts)
  AND LOWER(address) = LOWER(@event_emitter)
  AND ARRAY_LENGTH(topics) >= 3
  AND topics[SAFE_OFFSET(0)] = @event_log1_topic0
  AND topics[SAFE_OFFSET(1)] = @position_decrease_hash
