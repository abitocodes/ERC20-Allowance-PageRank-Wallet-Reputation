-- Revised analysis: integer node ids and the downloaded tables, as in 08_export_ids.sql, for the
-- pair tables of 14_usd_anchor_pairs.sql (tags tobs and t1) and the revised cohort.
-- u_nodes: every address in a revised pair table of either anchor or in u_cohort, numbered
--   0..N-1 in address order; is_cohort marks the revised cohort.
-- u_x_allow_pairs___, u_x_transfer_pairs___: the pair tables with node ids, keeping the columns
--   the local scoring reads (the registered column names, so the scoring code is unchanged) and
--   the slope-sensitivity weights.

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.u_nodes` AS
WITH a AS (
  SELECT owner AS address FROM `dissertation-bq.contract_rep.u_allow_pairs_tobs`
  UNION DISTINCT SELECT spender FROM `dissertation-bq.contract_rep.u_allow_pairs_tobs`
  UNION DISTINCT SELECT from_address FROM `dissertation-bq.contract_rep.u_transfer_pairs_tobs`
  UNION DISTINCT SELECT to_address FROM `dissertation-bq.contract_rep.u_transfer_pairs_tobs`
  UNION DISTINCT SELECT owner FROM `dissertation-bq.contract_rep.u_allow_pairs_t1`
  UNION DISTINCT SELECT spender FROM `dissertation-bq.contract_rep.u_allow_pairs_t1`
  UNION DISTINCT SELECT from_address FROM `dissertation-bq.contract_rep.u_transfer_pairs_t1`
  UNION DISTINCT SELECT to_address FROM `dissertation-bq.contract_rep.u_transfer_pairs_t1`
  UNION DISTINCT SELECT address FROM `dissertation-bq.contract_rep.u_cohort`
)
SELECT ROW_NUMBER() OVER (ORDER BY a.address) - 1 AS id,
       CONCAT('0x', TO_HEX(a.address)) AS address,
       a.address AS address_bytes,
       a.address IN (SELECT address FROM `dissertation-bq.contract_rep.u_cohort`) AS is_cohort
FROM a;

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.u_x_nodes` AS
SELECT id, address, is_cohort FROM `dissertation-bq.contract_rep.u_nodes`;

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.u_x_allow_pairs_tobs` AS
SELECT s.id AS src, d.id AS dst, p.n_tokens, p.w_er, p.w_raw, p.max_sig, p.w_er_b10x, p.w_er_b01x
FROM `dissertation-bq.contract_rep.u_allow_pairs_tobs` AS p
JOIN `dissertation-bq.contract_rep.u_nodes` AS s ON s.address_bytes = p.owner
JOIN `dissertation-bq.contract_rep.u_nodes` AS d ON d.address_bytes = p.spender;

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.u_x_allow_pairs_t1` AS
SELECT s.id AS src, d.id AS dst, p.n_tokens, p.w_er, p.w_raw, p.max_sig
FROM `dissertation-bq.contract_rep.u_allow_pairs_t1` AS p
JOIN `dissertation-bq.contract_rep.u_nodes` AS s ON s.address_bytes = p.owner
JOIN `dissertation-bq.contract_rep.u_nodes` AS d ON d.address_bytes = p.spender;

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.u_x_transfer_pairs_tobs` AS
SELECT s.id AS src, d.id AS dst, p.n_transfers, p.w_awp, p.w_raw, p.max_sig, p.w_awp_b10x, p.w_awp_b01x
FROM `dissertation-bq.contract_rep.u_transfer_pairs_tobs` AS p
JOIN `dissertation-bq.contract_rep.u_nodes` AS s ON s.address_bytes = p.from_address
JOIN `dissertation-bq.contract_rep.u_nodes` AS d ON d.address_bytes = p.to_address;

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.u_x_transfer_pairs_t1` AS
SELECT s.id AS src, d.id AS dst, p.n_transfers, p.w_awp, p.w_raw, p.max_sig
FROM `dissertation-bq.contract_rep.u_transfer_pairs_t1` AS p
JOIN `dissertation-bq.contract_rep.u_nodes` AS s ON s.address_bytes = p.from_address
JOIN `dissertation-bq.contract_rep.u_nodes` AS d ON d.address_bytes = p.to_address;
