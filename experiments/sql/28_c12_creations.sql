-- Contract-graph revision (docs/revision_contract_graph.md, section 12; job 28; a cross-check only): the ends
-- E created by a top-level transaction, a receipt with a contract address, before @end_ts. A contract made
-- by another contract (CREATE or CREATE2 inside a call) has no such receipt; the code read of section 4.2
-- decides the type, and this table decides nothing.
-- Inputs: bigquery-public-data.goog_blockchain_arbitrum_one_us.receipts (contract_address: 0x hex STRING,
--         NULL unless the transaction created a contract; partitioned on block_timestamp),
--         contract_rep.c12_ends (sql/25_c12_ends.sql).
-- Parameter: @end_ts (exclusive).
--
-- c12_creations: address (20-byte BYTES), created_ts (the time of the earliest such receipt).

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.c12_creations` AS
SELECT FROM_HEX(SUBSTR(r.contract_address, 3)) AS address, MIN(r.block_timestamp) AS created_ts
FROM `bigquery-public-data.goog_blockchain_arbitrum_one_us.receipts` AS r
WHERE r.block_timestamp < TIMESTAMP(@end_ts)
  AND r.contract_address IS NOT NULL
  AND FROM_HEX(SUBSTR(r.contract_address, 3)) IN (SELECT address FROM `dissertation-bq.contract_rep.c12_ends`)
GROUP BY 1;
