-- Contract-graph revision (docs/discovery_protocol.md sections 5 and 8, revision section 7 and the gate B amendment
-- of section 13; job 36, step constants): the five-token events of user accounts toward contracts and toward the
-- untyped addresses of E in the two score windows (@start_ts = 2025-04-01 to T_obs), materialised once, so that
-- c12_logs5 is read once in gate B: U_user of sql/36_c12_constants.sql and the importance measures and the untyped
-- inflow of sql/41_c12_importance.sql read this table.
--   toward contracts (to_contract true): every Approval (of any value: the latest one decides) and every Transfer
--     with a US-dollar value whose a is a user account (c12_user_accounts, without the zero address) and whose b is
--     in c12_contracts;
--   toward untyped addresses (to_contract false): every Transfer with a US-dollar value whose a is a user account and
--     whose b is an address of E (c12_ends) outside the RPC queue (c12_rpc_queue) that sent no transaction
--     (c12_tx_senders); the system addresses outside the queue are among them.
-- Inputs: contract_rep.c12_logs5 (sql/24), c12_user_accounts, c12_contracts (sql/31), c12_ends (sql/25),
--   c12_rpc_queue (sql/29), c12_tx_senders (sql/26).
-- Parameters: @start_ts, @tobs (both inclusive).
--
-- c12_user_events: block_timestamp, block_number, log_index, kind ('A' or 'T'), token, a, b, value, usd (as in
--   c12_logs5; amount is left out, it is value / 10^decimals), to_contract. Partitioned by month and clustered by
--   kind like c12_logs5.

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.c12_user_events`
PARTITION BY TIMESTAMP_TRUNC(block_timestamp, MONTH)
CLUSTER BY kind
AS
WITH untyped AS (
  SELECT e.address
  FROM `dissertation-bq.contract_rep.c12_ends` AS e
  LEFT JOIN (SELECT FROM_HEX(SUBSTR(address, 3)) AS address
             FROM `dissertation-bq.contract_rep.c12_rpc_queue`) AS q ON q.address = e.address
  LEFT JOIN `dissertation-bq.contract_rep.c12_tx_senders` AS s ON s.address = e.address
  WHERE q.address IS NULL AND s.address IS NULL
),
ev AS (
  SELECT l.block_timestamp, l.block_number, l.log_index, l.kind, l.token, l.a, l.b, l.value, l.usd,
         l.b IN (SELECT address FROM `dissertation-bq.contract_rep.c12_contracts`) AS to_contract,
         l.b IN (SELECT address FROM untyped) AS to_untyped
  FROM `dissertation-bq.contract_rep.c12_logs5` AS l
  WHERE l.block_timestamp >= TIMESTAMP(@start_ts)
    AND l.block_timestamp <= TIMESTAMP(@tobs)
    AND l.a IN (SELECT address FROM `dissertation-bq.contract_rep.c12_user_accounts`)
    AND l.a != FROM_HEX(REPEAT('00', 20))
)
SELECT block_timestamp, block_number, log_index, kind, token, a, b, value, usd, to_contract
FROM ev
WHERE (to_contract AND (kind = 'A' OR usd IS NOT NULL))
   OR (to_untyped AND kind = 'T' AND usd IS NOT NULL);
