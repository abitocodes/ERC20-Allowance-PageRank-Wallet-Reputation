-- Contract-graph revision (docs/revision_contract_graph.md, sections 4.1, 4.3 and 12; job 25): the pairs and
-- the ends of the five-token events of the typing window.
-- Input: contract_rep.c12_logs5 (sql/24_c12_logs5.sql).
--
-- c12_pairs5: one row per distinct ordered pair (a, b) of c12_logs5, owner -> spender for an approval and
--   sender -> recipient for a transfer, across the five tokens; pairs with the zero address (mints and burns)
--   and self-pairs included. n_approvals and n_transfers count the events of the pair, first_ts and
--   last_ts are the times of its first and last event.
-- c12_ends: E of section 4.1, every address other than the zero address that is the a or the b of an event
--   of c12_logs5; n_as_a and n_as_b count the events in which it is the a and the b (a self-pair counts
--   on both sides).

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.c12_pairs5` AS
SELECT a, b,
       COUNTIF(kind = 'A') AS n_approvals,
       COUNTIF(kind = 'T') AS n_transfers,
       MIN(block_timestamp) AS first_ts,
       MAX(block_timestamp) AS last_ts
FROM `dissertation-bq.contract_rep.c12_logs5`
GROUP BY a, b;

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.c12_ends` AS
WITH sides AS (
  SELECT a AS address, n_approvals + n_transfers AS n_a, 0 AS n_b
  FROM `dissertation-bq.contract_rep.c12_pairs5`
  UNION ALL
  SELECT b AS address, 0 AS n_a, n_approvals + n_transfers AS n_b
  FROM `dissertation-bq.contract_rep.c12_pairs5`
)
SELECT address, SUM(n_a) AS n_as_a, SUM(n_b) AS n_as_b
FROM sides
WHERE address != FROM_HEX(REPEAT('00', 20))
GROUP BY address;
