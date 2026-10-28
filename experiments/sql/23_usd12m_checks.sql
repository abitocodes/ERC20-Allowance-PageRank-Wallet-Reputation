-- Twelve-month variant (docs/revision_one_year_window.md): invariants that must hold exactly once
-- the pair tables exist. Every count is the number of violations and must be 0.
-- Parameters: @tobs_start, @t1_start.
--
-- allowances_tobs, allowances_t1: the twelve-month latest allowances equal the 33-month ones
--   (u_allow_triples_*) whose latest approval falls inside the score window and that touch the
--   freeze's cohort, in both directions (a triple whose latest approval up to the anchor is inside
--   the window has the same latest approval in both tables; one whose latest approval is older has
--   no approval in the window).
-- cohort_tobs_outside, cohort_t1_outside: twelve-month cohort contracts outside u_cohort.
-- transfer_pairs_tobs, transfer_pairs_t1: twelve-month transfer pairs missing from the 33-month
--   pair table, with more transfers than it, or with a first transfer before the window start.

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.u12_checks` AS
WITH
a12_tobs AS (SELECT token_address, owner, spender, value, block_timestamp
             FROM `dissertation-bq.contract_rep.u12_allow_triples_tobs`),
a33_tobs AS (SELECT token_address, owner, spender, value, block_timestamp
             FROM `dissertation-bq.contract_rep.u_allow_triples_tobs`
             WHERE block_timestamp >= TIMESTAMP(@tobs_start)
               AND (owner IN (SELECT address FROM `dissertation-bq.contract_rep.u12_cohort_tobs`)
                    OR spender IN (SELECT address FROM `dissertation-bq.contract_rep.u12_cohort_tobs`))),
a12_t1 AS (SELECT token_address, owner, spender, value, block_timestamp
           FROM `dissertation-bq.contract_rep.u12_allow_triples_t1`),
a33_t1 AS (SELECT token_address, owner, spender, value, block_timestamp
           FROM `dissertation-bq.contract_rep.u_allow_triples_t1`
           WHERE block_timestamp >= TIMESTAMP(@t1_start)
             AND (owner IN (SELECT address FROM `dissertation-bq.contract_rep.u12_cohort_t1`)
                  OR spender IN (SELECT address FROM `dissertation-bq.contract_rep.u12_cohort_t1`))),
p_tobs AS (
  SELECT COUNTIF(o.from_address IS NULL OR n.n_transfers > o.n_transfers
                 OR n.first_ts < TIMESTAMP(@tobs_start)) AS bad
  FROM `dissertation-bq.contract_rep.u12_transfer_pairs_tobs` AS n
  LEFT JOIN `dissertation-bq.contract_rep.u_transfer_pairs_tobs` AS o
    ON o.from_address = n.from_address AND o.to_address = n.to_address
),
p_t1 AS (
  SELECT COUNTIF(o.from_address IS NULL OR n.n_transfers > o.n_transfers
                 OR n.first_ts < TIMESTAMP(@t1_start)) AS bad
  FROM `dissertation-bq.contract_rep.u12_transfer_pairs_t1` AS n
  LEFT JOIN `dissertation-bq.contract_rep.u_transfer_pairs_t1` AS o
    ON o.from_address = n.from_address AND o.to_address = n.to_address
)
SELECT 'allowances_tobs' AS check_name,
       (SELECT COUNT(*) FROM (SELECT * FROM a12_tobs EXCEPT DISTINCT SELECT * FROM a33_tobs))
     + (SELECT COUNT(*) FROM (SELECT * FROM a33_tobs EXCEPT DISTINCT SELECT * FROM a12_tobs)) AS violations
UNION ALL
SELECT 'allowances_t1',
       (SELECT COUNT(*) FROM (SELECT * FROM a12_t1 EXCEPT DISTINCT SELECT * FROM a33_t1))
     + (SELECT COUNT(*) FROM (SELECT * FROM a33_t1 EXCEPT DISTINCT SELECT * FROM a12_t1))
UNION ALL
SELECT 'cohort_tobs_outside',
       (SELECT COUNT(*) FROM `dissertation-bq.contract_rep.u12_cohort_tobs`
        WHERE address NOT IN (SELECT address FROM `dissertation-bq.contract_rep.u_cohort`))
UNION ALL
SELECT 'cohort_t1_outside',
       (SELECT COUNT(*) FROM `dissertation-bq.contract_rep.u12_cohort_t1`
        WHERE address NOT IN (SELECT address FROM `dissertation-bq.contract_rep.u_cohort`))
UNION ALL
SELECT 'transfer_pairs_tobs', (SELECT bad FROM p_tobs)
UNION ALL
SELECT 'transfer_pairs_t1', (SELECT bad FROM p_t1);
