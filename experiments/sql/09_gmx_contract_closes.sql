-- GMX V2 PositionDecrease logs of the accounts that hold contract code (gmx_contract_accounts,
-- from check_account_code.py), for decoding with decode_gmx_events.py.
-- Destination: contract_rep.gmx_closes___TAG__; __SRC__ is logs_obs or logs_w1.
CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.gmx_closes___TAG__` AS
SELECT block_timestamp, block_number, log_index, raw_topics, raw_data
FROM `dissertation-bq.contract_rep.__SRC__`
WHERE kind = 'G'
  AND CONCAT('0x', SUBSTR(raw_topics[OFFSET(2)], 27))
      IN (SELECT LOWER(address) FROM `dissertation-bq.contract_rep.gmx_contract_accounts`)
