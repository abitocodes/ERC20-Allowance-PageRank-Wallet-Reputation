-- Contract-graph revision (docs/revision_contract_graph.md, sections 6 and 12; job 34): the last block at or
-- before each anchor, at which scripts/balance_audit.py reads balanceOf if the RPC serves historical state.
-- Each anchor reads only its own UTC day of the public blocks view (from the first second of the day to the
-- anchor), so that the scan prunes to one daily partition per anchor.
-- Input: bigquery-public-data.goog_blockchain_arbitrum_one_us.blocks (partitioned on block_timestamp).
-- Parameters: @t1, @tobs, @end_0930 (2026-03-31, 2026-06-30 and 2026-09-30 at 23:59:59 UTC, inclusive).
--
-- c12_anchor_blocks: anchor ('t1', 'tobs', 'end_0930'), ts (the anchor), block_number (the largest block
--   number whose timestamp is at or before the anchor).

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.c12_anchor_blocks` AS
SELECT 't1' AS anchor, TIMESTAMP(@t1) AS ts, MAX(block_number) AS block_number
FROM `bigquery-public-data.goog_blockchain_arbitrum_one_us.blocks`
WHERE block_timestamp >= TIMESTAMP_TRUNC(TIMESTAMP(@t1), DAY)
  AND block_timestamp <= TIMESTAMP(@t1)
UNION ALL
SELECT 'tobs' AS anchor, TIMESTAMP(@tobs) AS ts, MAX(block_number) AS block_number
FROM `bigquery-public-data.goog_blockchain_arbitrum_one_us.blocks`
WHERE block_timestamp >= TIMESTAMP_TRUNC(TIMESTAMP(@tobs), DAY)
  AND block_timestamp <= TIMESTAMP(@tobs)
UNION ALL
SELECT 'end_0930' AS anchor, TIMESTAMP(@end_0930) AS ts, MAX(block_number) AS block_number
FROM `bigquery-public-data.goog_blockchain_arbitrum_one_us.blocks`
WHERE block_timestamp >= TIMESTAMP_TRUNC(TIMESTAMP(@end_0930), DAY)
  AND block_timestamp <= TIMESTAMP(@end_0930);
