-- Exploratory (2026-10-14): EndorseRank pair weights with every allowance in force at the anchor
-- counted as of the anchor, i.e. without the time weight of its approval date. sigma(0) would be
-- the same for every allowance and cancels in the row normalisation, so the weight is sum V(usd).
-- Also kept: the published weight (check), the youngest and oldest approval age of the pair.
CREATE TEMP FUNCTION sig(age_days FLOAT64) AS (1.0 / (1.0 + EXP(0.01 * (age_days - 180.0))));
CREATE TEMP FUNCTION vt(z FLOAT64, b FLOAT64) AS (IF(b * z >= 40.0, 1.0, 2.0 / (1.0 + EXP(-b * z)) - 1.0));
CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.x_nodecay_pairs___TAG__` AS
SELECT s.id AS src, d.id AS dst,
       COUNT(*) AS n_tokens,
       SUM(vt(t.usd, 0.01771955304303403)) AS w_er_nd,
       SUM(sig(t.age_days) * vt(t.usd, 0.01771955304303403)) AS w_er_chk,
       MIN(t.age_days) AS min_age_days,
       MAX(t.age_days) AS max_age_days
FROM `dissertation-bq.contract_rep.u_allow_triples___TAG__` AS t
JOIN `dissertation-bq.contract_rep.u_nodes` AS s ON s.address_bytes = t.owner
JOIN `dissertation-bq.contract_rep.u_nodes` AS d ON d.address_bytes = t.spender
GROUP BY src, dst;
