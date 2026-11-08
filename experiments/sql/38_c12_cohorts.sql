-- Contract-graph revision (docs/revision_contract_graph.md section 8; job 38, step rest): the cohorts and the members
-- of the four lists of the twelve-month analysis.
--   c12_cohort_tobs, c12_cohort_t1: the cohorts of sql/21_usd12m_cohorts.sql (u12_cohort_tobs, u12_cohort_t1)
--     without the members that are user accounts (c12_user_accounts); sql/42 stops the run on a member left that is
--     not in c12_contracts.
--   c12_members: every member of u12_cohort_tobs, u12_cohort_t1 and the spenders (wallet) of u12_labels_w0 and
--     u12_labels_w1, with its class: 'contract' (c12_contracts), 'user_account' (c12_user_accounts, with its source),
--     'system' (0x...01 to 0x...ff and not a user account) or 'untyped'. The spender cohorts of section 8 are the
--     spenders of class contract; the others are reported by class, and sql/42 stops the run only on an untyped one.
-- Inputs: contract_rep.u12_cohort_tobs, u12_cohort_t1 (sql/21), u12_labels_w0, u12_labels_w1 (sql/16 of the
--   twelve-month variant), c12_user_accounts, c12_contracts (sql/31).
-- Parameters: @system_first, @system_last (0x hex).

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.c12_cohort_tobs` AS
SELECT c.address, c.owners_nonzero, c.approval_logs
FROM `dissertation-bq.contract_rep.u12_cohort_tobs` AS c
LEFT JOIN `dissertation-bq.contract_rep.c12_user_accounts` AS u ON u.address = c.address
WHERE u.address IS NULL;

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.c12_cohort_t1` AS
SELECT c.address, c.owners_nonzero, c.approval_logs
FROM `dissertation-bq.contract_rep.u12_cohort_t1` AS c
LEFT JOIN `dissertation-bq.contract_rep.c12_user_accounts` AS u ON u.address = c.address
WHERE u.address IS NULL;

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.c12_members` AS
WITH lists AS (
  SELECT 'cohort_tobs' AS list, address FROM `dissertation-bq.contract_rep.u12_cohort_tobs`
  UNION ALL
  SELECT 'cohort_t1' AS list, address FROM `dissertation-bq.contract_rep.u12_cohort_t1`
  UNION ALL
  SELECT 'spenders_w0' AS list, FROM_HEX(SUBSTR(wallet, 3)) AS address
  FROM `dissertation-bq.contract_rep.u12_labels_w0`
  UNION ALL
  SELECT 'spenders_w1' AS list, FROM_HEX(SUBSTR(wallet, 3)) AS address
  FROM `dissertation-bq.contract_rep.u12_labels_w1`
)
SELECT l.list, CONCAT('0x', TO_HEX(l.address)) AS address, l.address AS address_bytes,
       CASE WHEN c.address IS NOT NULL THEN 'contract'
            WHEN u.address IS NOT NULL THEN 'user_account'
            WHEN l.address BETWEEN FROM_HEX(SUBSTR(@system_first, 3)) AND FROM_HEX(SUBSTR(@system_last, 3))
              THEN 'system'
            ELSE 'untyped' END AS class,
       u.source
FROM lists AS l
LEFT JOIN `dissertation-bq.contract_rep.c12_contracts` AS c ON c.address = l.address
LEFT JOIN `dissertation-bq.contract_rep.c12_user_accounts` AS u ON u.address = l.address;
