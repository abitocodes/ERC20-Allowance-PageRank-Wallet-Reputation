-- Exploratory: allowance pairs at one anchor keeping only unlimited allowances
-- (value >= 1.15e77 base units); pairs without an unlimited allowance are not written.
CREATE TEMP FUNCTION sig(age_days FLOAT64) AS (1.0 / (1.0 + EXP(0.01 * (age_days - 180.0))));
CREATE TEMP FUNCTION vt(z FLOAT64, b FLOAT64) AS (IF(b * z >= 40.0, 1.0, 2.0 / (1.0 + EXP(-b * z)) - 1.0));

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.x_unlonly_pairs___TAG__` AS
SELECT s.id AS src, d.id AS dst,
       COUNT(*) AS n_unl,
       SUM(sig(t.age_days) * vt(t.usd, 0.01771955304303403)) AS w_er_unl,
       SUM(LEAST(t.usd, 20000.0)) AS w_raw_unl,
       MAX(sig(t.age_days)) AS max_sig_unl
FROM `dissertation-bq.contract_rep.u_allow_triples___TAG__` AS t
JOIN `dissertation-bq.contract_rep.u_nodes` AS s ON s.address_bytes = t.owner
JOIN `dissertation-bq.contract_rep.u_nodes` AS d ON d.address_bytes = t.spender
WHERE t.value >= 1.15e77
GROUP BY src, dst;
