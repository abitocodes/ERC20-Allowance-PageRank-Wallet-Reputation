-- GMX V2 PositionDecrease logs: the account is the indexed topic of EventLog1 (topic 2),
-- so accounts can be listed without decoding the event data.
-- Destination: contract_rep.gmx_accounts (account, closes, first and last close).
CREATE OR REPLACE TABLE `__DEST__` AS
SELECT CONCAT('0x', SUBSTR(raw_topics[OFFSET(2)], 27)) AS account,
       COUNT(*) AS closes, MIN(block_timestamp) AS first_ts, MAX(block_timestamp) AS last_ts,
       SUM(LENGTH(raw_data)) AS data_chars
FROM `dissertation-bq.contract_rep.__SRC__`
WHERE kind = 'G'
GROUP BY 1
