-- Descriptive statistics quoted in Chapters 3 and 4 (one row per statistic group).
-- Destination tables: describe_monthly (events per month), describe_values (amount shares).
CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.describe_monthly` AS
SELECT FORMAT_TIMESTAMP('%Y-%m', block_timestamp) AS month, 'approval_ego' AS stream, COUNT(*) AS n
FROM `dissertation-bq.contract_rep.approvals_ego` GROUP BY 1
UNION ALL
SELECT FORMAT_TIMESTAMP('%Y-%m', block_timestamp), 'transfer_ego', COUNT(*)
FROM `dissertation-bq.contract_rep.transfers_ego` GROUP BY 1
UNION ALL
SELECT FORMAT_TIMESTAMP('%Y-%m', block_timestamp), CONCAT('logs_', kind), COUNT(*)
FROM `dissertation-bq.contract_rep.logs_obs` WHERE kind IN ('G', 'V') GROUP BY 1, kind;

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.describe_values` AS
SELECT 'transfers_ego' AS what, COUNT(*) AS n,
       COUNTIF(value >= 10) AS ge10, COUNTIF(value >= 1e30) AS ge1e30, NULL AS owners, NULL AS owners_unlimited, NULL AS owners_both
FROM `dissertation-bq.contract_rep.transfers_ego`
UNION ALL
SELECT 'latest_allowances_tobs', COUNT(*), COUNTIF(value >= 10), COUNTIF(value >= 1.15e77),
       COUNT(DISTINCT owner),
       COUNT(DISTINCT IF(value >= 1.15e77, owner, NULL)),
       NULL
FROM `dissertation-bq.contract_rep.allow_triples_tobs`
UNION ALL
SELECT 'owners_both_kinds_tobs', COUNT(*), NULL, NULL, NULL, NULL, COUNT(*)
FROM (
  SELECT owner FROM `dissertation-bq.contract_rep.allow_triples_tobs`
  GROUP BY owner HAVING COUNTIF(value >= 1.15e77) > 0 AND COUNTIF(value < 1.15e77) > 0
);
