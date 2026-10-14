-- Exploratory (not part of the registered or revised plan): allowance pairs at one anchor
-- with unlimited allowances (value >= 1.15e77 base units) left out. Only pairs holding at
-- least one unlimited allowance are written; every other pair is unchanged.
CREATE TEMP FUNCTION sig(age_days FLOAT64) AS (1.0 / (1.0 + EXP(0.01 * (age_days - 180.0))));
CREATE TEMP FUNCTION vt(z FLOAT64, b FLOAT64) AS (IF(b * z >= 40.0, 1.0, 2.0 / (1.0 + EXP(-b * z)) - 1.0));

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.x_unl_pairs___TAG__` AS
SELECT s.id AS src, d.id AS dst,
       COUNTIF(t.value >= 1.15e77) AS n_unl,
       COUNTIF(t.value < 1.15e77) AS n_fin,
       SUM(sig(t.age_days) * vt(t.usd, 0.01771955304303403)) AS w_er_all,
       SUM(IF(t.value < 1.15e77, sig(t.age_days) * vt(t.usd, 0.01771955304303403), 0.0)) AS w_er_fin,
       SUM(IF(t.value < 1.15e77, LEAST(t.usd, 20000.0), 0.0)) AS w_raw_fin,
       MAX(IF(t.value < 1.15e77, sig(t.age_days), NULL)) AS max_sig_fin
FROM `dissertation-bq.contract_rep.u_allow_triples___TAG__` AS t
JOIN `dissertation-bq.contract_rep.u_nodes` AS s ON s.address_bytes = t.owner
JOIN `dissertation-bq.contract_rep.u_nodes` AS d ON d.address_bytes = t.spender
GROUP BY src, dst
HAVING n_unl > 0;
