-- Scan A / scan B: materialise the events of the study from the public Arbitrum One logs
-- into one project table, so that every later query reads this table and not the public one.
-- Parameters: @start_ts, @end_ts (exclusive). Destination: contract_rep.logs_obs (scan A)
-- or contract_rep.logs_w1 (scan B), passed by scripts/run_bq.py.
--
-- kind: A = ERC-20 Approval, T = ERC-20 Transfer (both with exactly three topics),
--       G = GMX V2 EventLog1 PositionDecrease, V = Aave V3 Borrow / Repay / LiquidationCall.
-- For A and T: emitter = token contract, a = owner / sender, b = spender / recipient,
-- val = 32-byte amount. For G and V the topics and data are kept as they are.

CREATE TABLE `__DEST__`
PARTITION BY TIMESTAMP_TRUNC(block_timestamp, MONTH)
CLUSTER BY kind
AS
WITH src AS (
  SELECT block_timestamp, block_number, log_index, LOWER(address) AS address, topics, data
  FROM `bigquery-public-data.goog_blockchain_arbitrum_one_us.logs`
  WHERE block_timestamp >= TIMESTAMP(@start_ts)
    AND block_timestamp < TIMESTAMP(@end_ts)
),
tagged AS (
  SELECT *,
    CASE
      WHEN ARRAY_LENGTH(topics) = 3
           AND topics[OFFSET(0)] = '0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925' THEN 'A'
      WHEN ARRAY_LENGTH(topics) = 3
           AND topics[OFFSET(0)] = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef' THEN 'T'
      WHEN address = '0xc8ee91a54287db53897056e12d9819156d3822fb'
           AND ARRAY_LENGTH(topics) >= 2
           AND topics[OFFSET(0)] = '0x137a44067c8961cd7e1d876f4754a5a3a75989b4552f1843fc69c3b372def160'
           AND topics[OFFSET(1)] = '0x07d51b51b408d7c62dcc47cc558da5ce6a6e0fd129a427ebce150f52b0e5171a' THEN 'G'
      WHEN address = '0x794a61358d6845594f94dc1db02a252b5b4814ad'
           AND ARRAY_LENGTH(topics) >= 1
           AND topics[OFFSET(0)] IN (
             '0xb3d084820fb1a9decffb176436bd02558d15fac9b0ddfed8c465bc7359d7dce0',
             '0xa534c8dbe71f871f9f3530e97a74601fea17b426cae02e1c5aee42c96c784051',
             '0xe413a321e8681d831f4dbccbca790d2952b56f977908e45be37335533e005286') THEN 'V'
    END AS kind
  FROM src
)
SELECT
  block_timestamp,
  block_number,
  log_index,
  kind,
  FROM_HEX(SUBSTR(address, 3)) AS emitter,
  IF(kind IN ('A', 'T'), FROM_HEX(SUBSTR(topics[OFFSET(1)], 27)), NULL) AS a,
  IF(kind IN ('A', 'T'), FROM_HEX(SUBSTR(topics[OFFSET(2)], 27)), NULL) AS b,
  IF(kind IN ('A', 'T'), SAFE.FROM_HEX(SUBSTR(data, 3)), NULL) AS val,
  IF(kind IN ('G', 'V'), topics, NULL) AS raw_topics,
  IF(kind IN ('G', 'V'), data, NULL) AS raw_data
FROM tagged
WHERE kind IS NOT NULL
