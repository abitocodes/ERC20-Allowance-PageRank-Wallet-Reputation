-- Exploratory: net Transfer flow of the five listed tokens before the observation window
-- (2023-10-01), per (token, address), for the owners of a latest allowance at t1 or T_obs.
CREATE TEMP FUNCTION u256(v BYTES) AS (
  IFNULL((SELECT SUM(c * POW(256.0, LENGTH(v) - 1 - o))
          FROM UNNEST(TO_CODE_POINTS(v)) AS c WITH OFFSET o), 0.0)
);
CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.x_bal_pre` AS
WITH owners AS (
  SELECT DISTINCT token_address, owner FROM `dissertation-bq.contract_rep.u_allow_triples_t1`
  UNION DISTINCT
  SELECT DISTINCT token_address, owner FROM `dissertation-bq.contract_rep.u_allow_triples_tobs`
),
t AS (
  SELECT FROM_HEX(SUBSTR(LOWER(address), 3)) AS token_address,
         FROM_HEX(SUBSTR(topics[OFFSET(1)], 27)) AS a,
         FROM_HEX(SUBSTR(topics[OFFSET(2)], 27)) AS b,
         u256(SAFE.FROM_HEX(SUBSTR(data, 3))) AS v,
         block_timestamp
  FROM `bigquery-public-data.goog_blockchain_arbitrum_one_us.logs`
  WHERE block_timestamp < TIMESTAMP('2023-10-01 00:00:00 UTC')
    AND LOWER(address) IN ('0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9', '0xaf88d065e77c8cc2239327c5edb3a432268e5831',
                           '0x2f2a2543b76a4166549f7aab2e75bef0aefc5b0f', '0x82af49447d8a07e3bd95bd0d56f35241523fbab1',
                           '0x912ce59144191c1204e64559fe8253a0e49e6548')
    AND ARRAY_LENGTH(topics) = 3
    AND topics[OFFSET(0)] = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
),
flows AS (
  SELECT token_address, b AS addr, v AS d, block_timestamp FROM t
  UNION ALL
  SELECT token_address, a AS addr, -v AS d, block_timestamp FROM t
)
SELECT f.token_address, f.addr, SUM(f.d) AS net, COUNT(*) AS n, MIN(f.block_timestamp) AS first_ts
FROM flows AS f
JOIN owners AS o ON o.token_address = f.token_address AND o.owner = f.addr
GROUP BY f.token_address, f.addr;
