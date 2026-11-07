-- Contract-graph revision (docs/revision_contract_graph.md, section 4.2 rule 1 and section 12; job 26): the
-- transaction senders among the ends E. An address that sent a transaction is an externally owned account
-- (an EIP-7702 account is one); an account with code cannot send a transaction (EIP-3607). Every block before
-- @end_ts (the end of the typing window) counts, from the first block of the chain.
-- Inputs: bigquery-public-data.goog_blockchain_arbitrum_one_us.transactions (from_address: 0x hex STRING;
--         partitioned on block_timestamp), contract_rep.c12_ends (sql/25_c12_ends.sql).
-- Parameter: @end_ts (exclusive).
--
-- c12_tx_senders: address (20-byte BYTES), one row per address of c12_ends that sent a transaction.

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.c12_tx_senders` AS
SELECT DISTINCT FROM_HEX(SUBSTR(t.from_address, 3)) AS address
FROM `bigquery-public-data.goog_blockchain_arbitrum_one_us.transactions` AS t
WHERE t.block_timestamp < TIMESTAMP(@end_ts)
  AND FROM_HEX(SUBSTR(t.from_address, 3)) IN (SELECT address FROM `dissertation-bq.contract_rep.c12_ends`);
