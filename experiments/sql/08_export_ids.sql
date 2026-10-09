-- Integer node ids and the tables that are downloaded (one row per edge, addresses as ids).
-- nodes: every address that appears in a pair table of either anchor, or in the cohort,
--   numbered 0..N-1 in address order; is_cohort marks the matched cohort.
-- x_allow_pairs___TAG__, x_transfer_pairs___TAG__: the pair tables of 04_anchor_pairs.sql
--   with src and dst replaced by node ids.
-- Run once after both anchors exist (tags are fixed: tobs, t1). Only the columns the local
-- scoring needs are kept; first/last times and summed values stay in BigQuery.

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.nodes` AS
WITH a AS (
  SELECT owner AS address FROM `dissertation-bq.contract_rep.allow_pairs_tobs`
  UNION DISTINCT SELECT spender FROM `dissertation-bq.contract_rep.allow_pairs_tobs`
  UNION DISTINCT SELECT from_address FROM `dissertation-bq.contract_rep.transfer_pairs_tobs`
  UNION DISTINCT SELECT to_address FROM `dissertation-bq.contract_rep.transfer_pairs_tobs`
  UNION DISTINCT SELECT owner FROM `dissertation-bq.contract_rep.allow_pairs_t1`
  UNION DISTINCT SELECT spender FROM `dissertation-bq.contract_rep.allow_pairs_t1`
  UNION DISTINCT SELECT from_address FROM `dissertation-bq.contract_rep.transfer_pairs_t1`
  UNION DISTINCT SELECT to_address FROM `dissertation-bq.contract_rep.transfer_pairs_t1`
  UNION DISTINCT SELECT address FROM `dissertation-bq.contract_rep.cohort`
)
SELECT ROW_NUMBER() OVER (ORDER BY a.address) - 1 AS id,
       CONCAT('0x', TO_HEX(a.address)) AS address,
       a.address AS address_bytes,
       a.address IN (SELECT address FROM `dissertation-bq.contract_rep.cohort`) AS is_cohort
FROM a;

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.x_allow_pairs_tobs` AS
SELECT s.id AS src, d.id AS dst, p.n_tokens, p.w_er, p.w_raw, p.max_sig
FROM `dissertation-bq.contract_rep.allow_pairs_tobs` AS p
JOIN `dissertation-bq.contract_rep.nodes` AS s ON s.address_bytes = p.owner
JOIN `dissertation-bq.contract_rep.nodes` AS d ON d.address_bytes = p.spender;

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.x_allow_pairs_t1` AS
SELECT s.id AS src, d.id AS dst, p.n_tokens, p.w_er, p.w_raw, p.max_sig
FROM `dissertation-bq.contract_rep.allow_pairs_t1` AS p
JOIN `dissertation-bq.contract_rep.nodes` AS s ON s.address_bytes = p.owner
JOIN `dissertation-bq.contract_rep.nodes` AS d ON d.address_bytes = p.spender;

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.x_transfer_pairs_tobs` AS
SELECT s.id AS src, d.id AS dst, p.n_transfers, p.w_awp, p.w_raw, p.max_sig
FROM `dissertation-bq.contract_rep.transfer_pairs_tobs` AS p
JOIN `dissertation-bq.contract_rep.nodes` AS s ON s.address_bytes = p.from_address
JOIN `dissertation-bq.contract_rep.nodes` AS d ON d.address_bytes = p.to_address;

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.x_transfer_pairs_t1` AS
SELECT s.id AS src, d.id AS dst, p.n_transfers, p.w_awp, p.w_raw, p.max_sig
FROM `dissertation-bq.contract_rep.transfer_pairs_t1` AS p
JOIN `dissertation-bq.contract_rep.nodes` AS s ON s.address_bytes = p.from_address
JOIN `dissertation-bq.contract_rep.nodes` AS d ON d.address_bytes = p.to_address;
