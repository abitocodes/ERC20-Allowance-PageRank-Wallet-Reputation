-- Contract-graph revision (docs/revision_contract_graph.md, sections 4.2, 5 and 12; job 31): the node set of
-- every graph of this revision, the typed user accounts, and the five-token events between contracts.
-- Inputs: contract_rep.c12_account_types (job 30: the parquet of scripts/check_account_code.py loaded as it
--         is; address is a lowercase 0x hex STRING, account_class is 'eoa', 'eoa_7702', 'contract' or
--         'smart_account', code_hash and implementation are lowercase 0x hex STRINGs or empty),
--         contract_rep.c12_tx_senders (sql/26), contract_rep.c12_logs5 (sql/24).
-- Parameters: @system_first, @system_last (0x hex; the precompiles 0x...01 to 0x...ff); @ext_code_hashes and
--   @ext_pairs, the lists of the amendment of 9 November 2026 (revision section 13: the extension of rule 3(b)
--   of section 4.2), as common.smart_account_sql_params() writes them: lowercase code hashes joined by commas,
--   and code_hash:implementation pairs joined by commas.
--
-- In both typed views below, an address of class 'contract' whose code hash is in @ext_code_hashes, or whose
-- code hash and implementation are a pair of @ext_pairs, is of class 'smart_account' (common.
-- smart_account_extension applies the same lists to the parquet).
-- c12_contracts: address (20-byte BYTES) of every RPC-typed address of class 'contract' (code that is
--   neither an EIP-7702 delegation nor a Safe or ERC-4337 smart account, section 4.2 rules 2 to 4 with the
--   extension of rule 3(b)) that is not a system address, not the zero address and not a transaction sender.
-- c12_user_accounts: address (BYTES), source: 'tx_sender' for every address of c12_tx_senders, otherwise
--   'rpc_' followed by the class of an RPC-typed address that is not a contract ('rpc_eoa', 'rpc_eoa_7702',
--   'rpc_smart_account') and not a system address (section 4.1: a system address is never a contract, and it
--   is a user account only if it sent a transaction, by rule 1, whatever its reads give).
-- c12_events_cc: the rows of c12_logs5, with all its columns, whose a and b are both in c12_contracts;
--   partitioned by month and clustered by kind like c12_logs5.

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.c12_contracts` AS
WITH typed AS (
  SELECT FROM_HEX(SUBSTR(address, 3)) AS address,
         IF(account_class = 'contract'
              AND (LOWER(code_hash) IN UNNEST(SPLIT(@ext_code_hashes, ','))
                   OR CONCAT(LOWER(code_hash), ':', LOWER(IFNULL(implementation, ''))) IN UNNEST(SPLIT(@ext_pairs, ','))),
            'smart_account', account_class) AS account_class
  FROM `dissertation-bq.contract_rep.c12_account_types`
)
SELECT t.address
FROM typed AS t
LEFT JOIN `dissertation-bq.contract_rep.c12_tx_senders` AS s ON s.address = t.address
WHERE t.account_class = 'contract'
  AND s.address IS NULL
  AND t.address != FROM_HEX(REPEAT('00', 20))
  AND t.address NOT BETWEEN FROM_HEX(SUBSTR(@system_first, 3)) AND FROM_HEX(SUBSTR(@system_last, 3));

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.c12_user_accounts` AS
WITH typed AS (
  SELECT FROM_HEX(SUBSTR(address, 3)) AS address,
         IF(account_class = 'contract'
              AND (LOWER(code_hash) IN UNNEST(SPLIT(@ext_code_hashes, ','))
                   OR CONCAT(LOWER(code_hash), ':', LOWER(IFNULL(implementation, ''))) IN UNNEST(SPLIT(@ext_pairs, ','))),
            'smart_account', account_class) AS account_class
  FROM `dissertation-bq.contract_rep.c12_account_types`
)
SELECT address, 'tx_sender' AS source
FROM `dissertation-bq.contract_rep.c12_tx_senders`
UNION ALL
SELECT t.address, CONCAT('rpc_', t.account_class) AS source
FROM typed AS t
LEFT JOIN `dissertation-bq.contract_rep.c12_tx_senders` AS s ON s.address = t.address
WHERE t.account_class != 'contract'
  AND s.address IS NULL
  AND t.address NOT BETWEEN FROM_HEX(SUBSTR(@system_first, 3)) AND FROM_HEX(SUBSTR(@system_last, 3));

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.c12_events_cc`
PARTITION BY TIMESTAMP_TRUNC(block_timestamp, MONTH)
CLUSTER BY kind
AS
SELECT l.block_timestamp, l.block_number, l.log_index, l.kind, l.token, l.a, l.b, l.value, l.amount, l.usd
FROM `dissertation-bq.contract_rep.c12_logs5` AS l
WHERE l.a IN (SELECT address FROM `dissertation-bq.contract_rep.c12_contracts`)
  AND l.b IN (SELECT address FROM `dissertation-bq.contract_rep.c12_contracts`);
