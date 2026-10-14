-- Exploratory: new approval pairs of the label window split by kind, for the spenders of
-- u_labels___TAG__ (same "new" rule as sql/16_usd_labels.sql: owner had no positive latest
-- allowance to the spender at the freeze). n_new_fin: new owners with a finite positive
-- approval in the window; n_new_unl: new owners with an unlimited one.
CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.x_unl_labels___TAG__` AS
WITH t1_pairs AS (
  SELECT DISTINCT owner, spender FROM `dissertation-bq.contract_rep.u_allow_triples___FREEZE__`
),
spenders AS (SELECT DISTINCT spender FROM t1_pairs),
win AS (
  SELECT owner, spender, value FROM `dissertation-bq.contract_rep.__APPROVALS__`
  WHERE block_timestamp >= TIMESTAMP(@out_start) AND block_timestamp <= TIMESTAMP(@out_end)
    AND spender IN (SELECT spender FROM spenders) AND value > 0
)
SELECT CONCAT('0x', TO_HEX(w.spender)) AS wallet,
       COUNT(DISTINCT IF(w.value < 1.15e77, w.owner, NULL)) AS n_new_fin,
       COUNT(DISTINCT IF(w.value >= 1.15e77, w.owner, NULL)) AS n_new_unl,
       COUNT(DISTINCT w.owner) AS n_new_all
FROM win AS w
LEFT JOIN t1_pairs AS p ON p.owner = w.owner AND p.spender = w.spender
WHERE p.owner IS NULL
GROUP BY w.spender;
