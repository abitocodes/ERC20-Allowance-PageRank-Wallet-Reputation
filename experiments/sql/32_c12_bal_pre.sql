-- Contract-graph revision (docs/revision_contract_graph.md, sections 6 and 12; job 32): the net Transfer flow
-- of the five tokens before @obs_start (2023-10-01, where logs_obs begins), read from the public Arbitrum One
-- logs (from the first block of the chain), for every (token, owner) of the balance population: the distinct
-- (token, a) of the approvals of c12_logs5 with @start_ts <= block_timestamp < @tobs_end (2025-04-01 to T_obs
-- inclusive). The five token addresses are literals, as in the exploratory check of 13 October 2026
-- (exploratory/2026-10-13-unlimited-allowances/sql/bal_pre.sql); scripts/run_contract12m_pipeline.py check
-- compares them with u_tokens.
-- Inputs: bigquery-public-data.goog_blockchain_arbitrum_one_us.logs (address: 0x hex STRING; topics; data;
--         partitioned on block_timestamp), contract_rep.c12_logs5 (sql/24).
-- Parameters: @obs_start, @start_ts, @tobs_end (exclusive).
--
-- c12_bal_pre: token, address (20-byte BYTES), net (received minus sent before @obs_start, in base units as
--   FLOAT64; a self-transfer adds nothing), n (non-zero transfers in which the address is the sender or the
--   recipient, a self-transfer counted twice), first_ts (the first of them). Pairs of the population without
--   such a transfer have no row.

CREATE TEMP FUNCTION u256(v BYTES) AS (
  IFNULL((SELECT SUM(c * POW(256.0, LENGTH(v) - 1 - o))
          FROM UNNEST(TO_CODE_POINTS(v)) AS c WITH OFFSET o), 0.0)
);

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.c12_bal_pre` AS
WITH pop AS (
  SELECT DISTINCT token, a AS address
  FROM `dissertation-bq.contract_rep.c12_logs5`
  WHERE kind = 'A'
    AND block_timestamp >= TIMESTAMP(@start_ts)
    AND block_timestamp < TIMESTAMP(@tobs_end)
),
t AS (
  SELECT FROM_HEX(SUBSTR(LOWER(address), 3)) AS token,
         FROM_HEX(SUBSTR(topics[OFFSET(1)], 27)) AS a,
         FROM_HEX(SUBSTR(topics[OFFSET(2)], 27)) AS b,
         u256(SAFE.FROM_HEX(SUBSTR(data, 3))) AS v,
         block_timestamp
  FROM `bigquery-public-data.goog_blockchain_arbitrum_one_us.logs`
  WHERE block_timestamp < TIMESTAMP(@obs_start)
    AND LOWER(address) IN ('0x82af49447d8a07e3bd95bd0d56f35241523fbab1', '0xaf88d065e77c8cc2239327c5edb3a432268e5831',
                           '0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9', '0x912ce59144191c1204e64559fe8253a0e49e6548',
                           '0x2f2a2543b76a4166549f7aab2e75bef0aefc5b0f')
    AND ARRAY_LENGTH(topics) = 3
    AND topics[OFFSET(0)] = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
    AND LTRIM(SUBSTR(data, 3), '0') != ''
),
flows AS (
  SELECT token, b AS address, v AS d, block_timestamp FROM t
  UNION ALL
  SELECT token, a AS address, -v AS d, block_timestamp FROM t
)
SELECT f.token, f.address, SUM(f.d) AS net, COUNT(*) AS n, MIN(f.block_timestamp) AS first_ts
FROM flows AS f
JOIN pop AS p ON p.token = f.token AND p.address = f.address
GROUP BY f.token, f.address;
