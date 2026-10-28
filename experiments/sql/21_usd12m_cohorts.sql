-- Twelve-month variant (docs/revision_one_year_window.md, section 4): one cohort per freeze, and
-- the selected-token ego events of each freeze as views over the 33-month US-dollar ego tables of
-- 12_usd_ego.sql. Those tables hold every event of a selected token touching a u_cohort contract,
-- and both twelve-month cohorts are subsets of u_cohort (three owners inside twelve months are
-- three owners inside 33), so the views hold the full ego networks of the new cohorts.
-- The window bounds are literal text (__TOBS_START__, __TOBS_END__, __T1_START__, __T1_END__,
-- __W0_END__; ends exclusive), since views take no parameters; the constant filters let BigQuery
-- prune the monthly partitions of the tables under the views.
--
-- u12_cohort_tobs: u_cohort contracts that received a non-zero approval of a selected token from
--   at least three distinct owners inside the T_obs score window [__TOBS_START__, __TOBS_END__).
-- u12_cohort_t1:   the same inside the W0 score window [__T1_START__, __T1_END__).
-- u12_approvals_tobs, u12_transfers_tobs: events of the T_obs score window with a
--   u12_cohort_tobs contract as owner or spender (sender or recipient).
-- u12_approvals_t1, u12_transfers_t1: events from __T1_START__ to the end of the W0 label window
--   (__W0_END__) with a u12_cohort_t1 contract as owner or spender (sender or recipient).
-- u12_approvals_w1, u12_transfers_w1: events of the W1 label window (scan B) with a
--   u12_cohort_tobs contract as owner or spender (sender or recipient).

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.u12_cohort_tobs` AS
SELECT spender AS address, COUNT(DISTINCT owner) AS owners_nonzero, COUNT(*) AS approval_logs
FROM `dissertation-bq.contract_rep.u_approvals`
WHERE block_timestamp >= TIMESTAMP('__TOBS_START__')
  AND block_timestamp < TIMESTAMP('__TOBS_END__')
  AND value > 0
  AND spender IN (SELECT address FROM `dissertation-bq.contract_rep.u_cohort`)
GROUP BY spender
HAVING COUNT(DISTINCT owner) >= 3;

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.u12_cohort_t1` AS
SELECT spender AS address, COUNT(DISTINCT owner) AS owners_nonzero, COUNT(*) AS approval_logs
FROM `dissertation-bq.contract_rep.u_approvals`
WHERE block_timestamp >= TIMESTAMP('__T1_START__')
  AND block_timestamp < TIMESTAMP('__T1_END__')
  AND value > 0
  AND spender IN (SELECT address FROM `dissertation-bq.contract_rep.u_cohort`)
GROUP BY spender
HAVING COUNT(DISTINCT owner) >= 3;

CREATE OR REPLACE VIEW `dissertation-bq.contract_rep.u12_approvals_tobs` AS
SELECT * FROM `dissertation-bq.contract_rep.u_approvals`
WHERE block_timestamp >= TIMESTAMP('__TOBS_START__')
  AND block_timestamp < TIMESTAMP('__TOBS_END__')
  AND (owner IN (SELECT address FROM `dissertation-bq.contract_rep.u12_cohort_tobs`)
       OR spender IN (SELECT address FROM `dissertation-bq.contract_rep.u12_cohort_tobs`));

CREATE OR REPLACE VIEW `dissertation-bq.contract_rep.u12_transfers_tobs` AS
SELECT * FROM `dissertation-bq.contract_rep.u_transfers`
WHERE block_timestamp >= TIMESTAMP('__TOBS_START__')
  AND block_timestamp < TIMESTAMP('__TOBS_END__')
  AND (from_address IN (SELECT address FROM `dissertation-bq.contract_rep.u12_cohort_tobs`)
       OR to_address IN (SELECT address FROM `dissertation-bq.contract_rep.u12_cohort_tobs`));

CREATE OR REPLACE VIEW `dissertation-bq.contract_rep.u12_approvals_t1` AS
SELECT * FROM `dissertation-bq.contract_rep.u_approvals`
WHERE block_timestamp >= TIMESTAMP('__T1_START__')
  AND block_timestamp < TIMESTAMP('__W0_END__')
  AND (owner IN (SELECT address FROM `dissertation-bq.contract_rep.u12_cohort_t1`)
       OR spender IN (SELECT address FROM `dissertation-bq.contract_rep.u12_cohort_t1`));

CREATE OR REPLACE VIEW `dissertation-bq.contract_rep.u12_transfers_t1` AS
SELECT * FROM `dissertation-bq.contract_rep.u_transfers`
WHERE block_timestamp >= TIMESTAMP('__T1_START__')
  AND block_timestamp < TIMESTAMP('__W0_END__')
  AND (from_address IN (SELECT address FROM `dissertation-bq.contract_rep.u12_cohort_t1`)
       OR to_address IN (SELECT address FROM `dissertation-bq.contract_rep.u12_cohort_t1`));

CREATE OR REPLACE VIEW `dissertation-bq.contract_rep.u12_approvals_w1` AS
SELECT * FROM `dissertation-bq.contract_rep.u_approvals_w1`
WHERE owner IN (SELECT address FROM `dissertation-bq.contract_rep.u12_cohort_tobs`)
   OR spender IN (SELECT address FROM `dissertation-bq.contract_rep.u12_cohort_tobs`);

CREATE OR REPLACE VIEW `dissertation-bq.contract_rep.u12_transfers_w1` AS
SELECT * FROM `dissertation-bq.contract_rep.u_transfers_w1`
WHERE from_address IN (SELECT address FROM `dissertation-bq.contract_rep.u12_cohort_tobs`)
   OR to_address IN (SELECT address FROM `dissertation-bq.contract_rep.u12_cohort_tobs`);
