-- Revised analysis (docs/revision_price_weighting.md): the listed tokens only, amounts in
-- token units and USD, and the cohort rule applied to approvals of listed tokens.
-- Reads the ego tables of 03_ego_events.sql, which hold every event with a contract of the
-- registered cohort as owner, spender, sender or recipient. The revised cohort is a subset
-- of the registered one (a spender approved by three owners on listed tokens is approved by
-- three owners on any token), so the registered ego tables contain its ego network.
-- Inputs: contract_rep.u_tokens (token BYTES, symbol, decimals INT64),
--         contract_rep.u_prices (token BYTES, day DATE, price_usd FLOAT64; one row per token and
--         UTC day from 2023-10-01 to 2026-09-30, gaps filled with the previous day's price).
-- Parameters: @start_ts, @end_ts (observation window, end exclusive).
--
-- u_cohort:        registered cohort contracts that received a non-zero approval of a listed
--                  token from at least three distinct owners inside the observation window.
-- u_approvals:     approvals of listed tokens with a u_cohort contract as owner or spender
--                  (observation window); amount = value / 10^decimals. USD values of allowances
--                  are taken at the anchor in 14_usd_anchor_pairs.sql.
-- u_transfers:     transfers of listed tokens with a u_cohort contract as sender or recipient
--                  (observation window); usd = amount x the token's price on the UTC day of the block.
-- u_approvals_w1, u_transfers_w1: the same for the label window of W1 (scan B ego tables).

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.u_cohort` AS
SELECT spender AS address, COUNT(DISTINCT owner) AS owners_nonzero, COUNT(*) AS approval_logs
FROM `dissertation-bq.contract_rep.approvals_ego`
WHERE block_timestamp >= TIMESTAMP(@start_ts)
  AND block_timestamp < TIMESTAMP(@end_ts)
  AND value > 0
  AND token_address IN (SELECT token FROM `dissertation-bq.contract_rep.u_tokens`)
  AND spender IN (SELECT address FROM `dissertation-bq.contract_rep.cohort`)
GROUP BY spender
HAVING COUNT(DISTINCT owner) >= 3;

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.u_approvals`
PARTITION BY TIMESTAMP_TRUNC(block_timestamp, MONTH)
AS
SELECT a.block_timestamp, a.block_number, a.log_index, a.token_address, a.owner, a.spender,
       a.value, a.value / POW(10.0, t.decimals) AS amount
FROM `dissertation-bq.contract_rep.approvals_ego` AS a
JOIN `dissertation-bq.contract_rep.u_tokens` AS t ON t.token = a.token_address
WHERE a.owner IN (SELECT address FROM `dissertation-bq.contract_rep.u_cohort`)
   OR a.spender IN (SELECT address FROM `dissertation-bq.contract_rep.u_cohort`);

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.u_transfers`
PARTITION BY TIMESTAMP_TRUNC(block_timestamp, MONTH)
AS
SELECT x.block_timestamp, x.block_number, x.log_index, x.token_address, x.from_address, x.to_address,
       x.value, x.value / POW(10.0, t.decimals) * p.price_usd AS usd
FROM `dissertation-bq.contract_rep.transfers_ego` AS x
JOIN `dissertation-bq.contract_rep.u_tokens` AS t ON t.token = x.token_address
LEFT JOIN `dissertation-bq.contract_rep.u_prices` AS p
  ON p.token = x.token_address AND p.day = DATE(x.block_timestamp)
WHERE x.from_address IN (SELECT address FROM `dissertation-bq.contract_rep.u_cohort`)
   OR x.to_address IN (SELECT address FROM `dissertation-bq.contract_rep.u_cohort`);

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.u_approvals_w1`
PARTITION BY TIMESTAMP_TRUNC(block_timestamp, MONTH)
AS
SELECT a.block_timestamp, a.block_number, a.log_index, a.token_address, a.owner, a.spender,
       a.value, a.value / POW(10.0, t.decimals) AS amount
FROM `dissertation-bq.contract_rep.approvals_w1ego` AS a
JOIN `dissertation-bq.contract_rep.u_tokens` AS t ON t.token = a.token_address
WHERE a.owner IN (SELECT address FROM `dissertation-bq.contract_rep.u_cohort`)
   OR a.spender IN (SELECT address FROM `dissertation-bq.contract_rep.u_cohort`);

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.u_transfers_w1`
PARTITION BY TIMESTAMP_TRUNC(block_timestamp, MONTH)
AS
SELECT x.block_timestamp, x.block_number, x.log_index, x.token_address, x.from_address, x.to_address,
       x.value, x.value / POW(10.0, t.decimals) * p.price_usd AS usd
FROM `dissertation-bq.contract_rep.transfers_w1ego` AS x
JOIN `dissertation-bq.contract_rep.u_tokens` AS t ON t.token = x.token_address
LEFT JOIN `dissertation-bq.contract_rep.u_prices` AS p
  ON p.token = x.token_address AND p.day = DATE(x.block_timestamp)
WHERE x.from_address IN (SELECT address FROM `dissertation-bq.contract_rep.u_cohort`)
   OR x.to_address IN (SELECT address FROM `dissertation-bq.contract_rep.u_cohort`);
