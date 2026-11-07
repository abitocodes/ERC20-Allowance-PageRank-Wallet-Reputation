-- Contract-graph revision (docs/revision_contract_graph.md, section 12; job 27; a cross-check only): the ends
-- E that emitted a decoded log in the typing window, with the number of Safe events among those logs. The
-- account types come from the code (scripts/check_account_code.py, section 4.2); this table decides nothing.
-- Inputs: bigquery-public-data.goog_blockchain_arbitrum_one_us.decoded_events (address: 0x hex STRING;
--         event_signature: the human-readable signature; partitioned on block_timestamp),
--         contract_rep.c12_ends (sql/25_c12_ends.sql).
-- Parameters: @start_ts, @end_ts (the typing window, end exclusive).
--
-- c12_emitters: address (20-byte BYTES), n_logs (the logs it emitted in the window), n_safe_events (those
--   whose event name is one of the Safe events ExecutionSuccess, ExecutionFailure, SafeSetup, SafeReceived,
--   ChangedThreshold, AddedOwner, RemovedOwner, EnabledModule, ExecutionFromModuleSuccess). The name is the
--   identifier before the first '(' of event_signature, with a leading 'event' keyword dropped, so that
--   'Name(type,...)' and 'event Name(type indexed name, ...)' give the same name.

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.c12_emitters` AS
WITH ev AS (
  SELECT FROM_HEX(SUBSTR(d.address, 3)) AS address,
         REGEXP_EXTRACT(d.event_signature, r'^\s*(?:event\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*\(') AS name
  FROM `bigquery-public-data.goog_blockchain_arbitrum_one_us.decoded_events` AS d
  WHERE d.block_timestamp >= TIMESTAMP(@start_ts)
    AND d.block_timestamp < TIMESTAMP(@end_ts)
)
SELECT address,
       COUNT(*) AS n_logs,
       COUNTIF(name IN ('ExecutionSuccess', 'ExecutionFailure', 'SafeSetup', 'SafeReceived', 'ChangedThreshold',
                        'AddedOwner', 'RemovedOwner', 'EnabledModule', 'ExecutionFromModuleSuccess')) AS n_safe_events
FROM ev
WHERE address IN (SELECT address FROM `dissertation-bq.contract_rep.c12_ends`)
GROUP BY address;
