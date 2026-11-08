-- Contract-graph revision (docs/discovery_protocol.md section 8, revision section 8; job 40, step rest): the node
-- ids of both freezes and the tables that the evaluation and the discovery runner download, as
-- sql/17_usd_export_ids.sql does (lines 21-24 and the select lists of lines 31, 37, 43 and 49 copied).
--   c12_nodes: every contract of c12_contracts that is an end of a capped, uncapped or transfer pair at either freeze
--     (sql/37) or a contract member of one of the four lists of c12_members, numbered 0..N-1 in address order (BYTES
--     order is the order of the lowercase hex); is_cohort (the T_obs cohort), is_cohort_t1, is_spender_w0 and
--     is_spender_w1 mark the contract members. The importance rows add no node (protocol section 8).
--   c12_x_nodes: id, address and the four flags.  c12_x_members: c12_members without the BYTES address.
--   c12_x_allow_pairs_{tobs,t1}, c12_x_allow_pairs_unc_{tobs,t1}, c12_x_transfer_pairs_{tobs,t1}: the pair tables of
--     each freeze with node ids; the slope-sensitivity weights at T_obs only, the uncapped pairs without them.
-- Inputs: contract_rep.c12_allow_pairs, c12_allow_pairs_unc, c12_transfer_pairs (sql/37), c12_members (sql/38),
--   c12_contracts (sql/31).

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.c12_nodes` AS
WITH ends AS (
  SELECT owner AS address FROM `dissertation-bq.contract_rep.c12_allow_pairs`
  UNION DISTINCT SELECT spender FROM `dissertation-bq.contract_rep.c12_allow_pairs`
  UNION DISTINCT SELECT owner FROM `dissertation-bq.contract_rep.c12_allow_pairs_unc`
  UNION DISTINCT SELECT spender FROM `dissertation-bq.contract_rep.c12_allow_pairs_unc`
  UNION DISTINCT SELECT from_address FROM `dissertation-bq.contract_rep.c12_transfer_pairs`
  UNION DISTINCT SELECT to_address FROM `dissertation-bq.contract_rep.c12_transfer_pairs`
  UNION DISTINCT SELECT address_bytes FROM `dissertation-bq.contract_rep.c12_members` WHERE class = 'contract'
),
a AS (
  SELECT address FROM ends
  WHERE address IN (SELECT address FROM `dissertation-bq.contract_rep.c12_contracts`)
)
SELECT ROW_NUMBER() OVER (ORDER BY a.address) - 1 AS id,
       CONCAT('0x', TO_HEX(a.address)) AS address,
       a.address AS address_bytes,
       a.address IN (SELECT address_bytes FROM `dissertation-bq.contract_rep.c12_members`
                     WHERE list = 'cohort_tobs' AND class = 'contract') AS is_cohort,
       a.address IN (SELECT address_bytes FROM `dissertation-bq.contract_rep.c12_members`
                     WHERE list = 'cohort_t1' AND class = 'contract') AS is_cohort_t1,
       a.address IN (SELECT address_bytes FROM `dissertation-bq.contract_rep.c12_members`
                     WHERE list = 'spenders_w0' AND class = 'contract') AS is_spender_w0,
       a.address IN (SELECT address_bytes FROM `dissertation-bq.contract_rep.c12_members`
                     WHERE list = 'spenders_w1' AND class = 'contract') AS is_spender_w1
FROM a;

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.c12_x_nodes` AS
SELECT id, address, is_cohort, is_cohort_t1, is_spender_w0, is_spender_w1
FROM `dissertation-bq.contract_rep.c12_nodes`;

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.c12_x_members` AS
SELECT list, address, class, source
FROM `dissertation-bq.contract_rep.c12_members`;

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.c12_x_allow_pairs_tobs` AS
SELECT s.id AS src, d.id AS dst, p.n_tokens, p.w_er, p.w_raw, p.max_sig, p.w_er_b10x, p.w_er_b01x
FROM `dissertation-bq.contract_rep.c12_allow_pairs` AS p
JOIN `dissertation-bq.contract_rep.c12_nodes` AS s ON s.address_bytes = p.owner
JOIN `dissertation-bq.contract_rep.c12_nodes` AS d ON d.address_bytes = p.spender
WHERE p.tag = 'tobs';

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.c12_x_allow_pairs_t1` AS
SELECT s.id AS src, d.id AS dst, p.n_tokens, p.w_er, p.w_raw, p.max_sig
FROM `dissertation-bq.contract_rep.c12_allow_pairs` AS p
JOIN `dissertation-bq.contract_rep.c12_nodes` AS s ON s.address_bytes = p.owner
JOIN `dissertation-bq.contract_rep.c12_nodes` AS d ON d.address_bytes = p.spender
WHERE p.tag = 't1';

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.c12_x_allow_pairs_unc_tobs` AS
SELECT s.id AS src, d.id AS dst, p.n_tokens, p.w_er, p.w_raw, p.max_sig
FROM `dissertation-bq.contract_rep.c12_allow_pairs_unc` AS p
JOIN `dissertation-bq.contract_rep.c12_nodes` AS s ON s.address_bytes = p.owner
JOIN `dissertation-bq.contract_rep.c12_nodes` AS d ON d.address_bytes = p.spender
WHERE p.tag = 'tobs';

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.c12_x_allow_pairs_unc_t1` AS
SELECT s.id AS src, d.id AS dst, p.n_tokens, p.w_er, p.w_raw, p.max_sig
FROM `dissertation-bq.contract_rep.c12_allow_pairs_unc` AS p
JOIN `dissertation-bq.contract_rep.c12_nodes` AS s ON s.address_bytes = p.owner
JOIN `dissertation-bq.contract_rep.c12_nodes` AS d ON d.address_bytes = p.spender
WHERE p.tag = 't1';

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.c12_x_transfer_pairs_tobs` AS
SELECT s.id AS src, d.id AS dst, p.n_transfers, p.w_awp, p.w_raw, p.max_sig, p.w_awp_b10x, p.w_awp_b01x
FROM `dissertation-bq.contract_rep.c12_transfer_pairs` AS p
JOIN `dissertation-bq.contract_rep.c12_nodes` AS s ON s.address_bytes = p.from_address
JOIN `dissertation-bq.contract_rep.c12_nodes` AS d ON d.address_bytes = p.to_address
WHERE p.tag = 'tobs';

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.c12_x_transfer_pairs_t1` AS
SELECT s.id AS src, d.id AS dst, p.n_transfers, p.w_awp, p.w_raw, p.max_sig
FROM `dissertation-bq.contract_rep.c12_transfer_pairs` AS p
JOIN `dissertation-bq.contract_rep.c12_nodes` AS s ON s.address_bytes = p.from_address
JOIN `dissertation-bq.contract_rep.c12_nodes` AS d ON d.address_bytes = p.to_address
WHERE p.tag = 't1';
