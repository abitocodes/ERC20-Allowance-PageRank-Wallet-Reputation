-- Revised analysis: the token list and the daily prices as the revised SQL joins them.
-- scripts/run_usd_pipeline.py (step "load") first loads the two CSV files of
-- data/0-usd-token-list-and-prices/ into u_tokens_hex and u_prices_hex (load jobs);
-- this query turns the hex addresses into 20-byte BYTES, as the ego tables store them.

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.u_tokens` AS
SELECT FROM_HEX(SUBSTR(LOWER(address), 3)) AS token, symbol, name, decimals
FROM `dissertation-bq.contract_rep.u_tokens_hex`;

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.u_prices` AS
SELECT FROM_HEX(SUBSTR(LOWER(address), 3)) AS token, day, price_usd, confidence, filled, filled_from
FROM `dissertation-bq.contract_rep.u_prices_hex`;
