-- Which of the given addresses emitted a log or sent a transaction in a window.
-- Only contract code emits logs, and only externally owned accounts sign transactions.
-- Parameters: @start_ts, @end_ts, @addresses (ARRAY<STRING>; pass each address both
-- lower-case and checksummed so the filter needs no function on the column)

WITH emitters AS (
  SELECT DISTINCT LOWER(address) AS addr
  FROM `__LOGS_FQN__`
  WHERE block_timestamp >= TIMESTAMP(@start_ts)
    AND block_timestamp < TIMESTAMP(@end_ts)
    AND address IN UNNEST(@addresses)
),
senders AS (
  SELECT DISTINCT LOWER(from_address) AS addr
  FROM `__TX_FQN__`
  WHERE block_timestamp >= TIMESTAMP(@start_ts)
    AND block_timestamp < TIMESTAMP(@end_ts)
    AND from_address IN UNNEST(@addresses)
)
SELECT addr AS address, 'emitted_log' AS activity FROM emitters
UNION ALL
SELECT addr AS address, 'sent_transaction' AS activity FROM senders
