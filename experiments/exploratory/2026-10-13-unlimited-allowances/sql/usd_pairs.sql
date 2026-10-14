-- Exploratory: allowance pair weights in raw USD with balances. bal_usd = max(balance, 0) at the
-- anchor x the token's price on the anchor day; x_bal = bal_usd for an unlimited allowance,
-- the allowance's usd otherwise. sigma as in 14_usd_anchor_pairs.sql.
CREATE TEMP FUNCTION sig(age_days FLOAT64) AS (1.0 / (1.0 + EXP(0.01 * (age_days - 180.0))));
CREATE TEMP FUNCTION vt(z FLOAT64, b FLOAT64) AS (IF(b * z >= 40.0, 1.0, 2.0 / (1.0 + EXP(-b * z)) - 1.0));
CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.x_usd_pairs___TAG__` AS
WITH r AS (
  SELECT t.owner, t.spender, t.usd, t.age_days, t.value >= 1.15e77 AS unl,
         GREATEST(IFNULL(b.__BAL__, 0.0), 0.0) / POW(10.0, k.decimals) * p.price_usd AS bal_usd
  FROM `dissertation-bq.contract_rep.u_allow_triples___TAG__` AS t
  JOIN `dissertation-bq.contract_rep.u_tokens` AS k ON k.token = t.token_address
  JOIN `dissertation-bq.contract_rep.u_prices` AS p ON p.token = t.token_address AND p.day = DATE('__DAY__')
  LEFT JOIN `dissertation-bq.contract_rep.x_bal` AS b ON b.token_address = t.token_address AND b.owner = t.owner
),
x AS (SELECT *, IF(unl, bal_usd, usd) AS xb, LEAST(usd, bal_usd) AS xm FROM r)
SELECT s.id AS src, d.id AS dst,
       SUM(sig(age_days) * xb) AS w_usd_bal,
       SUM(sig(age_days) * xm) AS w_usd_min,
       SUM(sig(age_days) * LEAST(usd, 20000.0)) AS w_usd_cap,
       SUM(sig(age_days) * vt(xb, 0.01771955304303403)) AS w_er_bal,
       SUM(sig(age_days) * vt(xm, 0.01771955304303403)) AS w_er_min,
       SUM(sig(age_days) * vt(usd, 0.01771955304303403)) AS w_er_chk,
       COUNTIF(unl) AS n_unl, COUNTIF(unl AND bal_usd <= 0) AS n_unl_zero,
       COUNTIF(bal_usd <= 0) AS n_zero_bal, COUNT(*) AS n
FROM x
JOIN `dissertation-bq.contract_rep.u_nodes` AS s ON s.address_bytes = x.owner
JOIN `dissertation-bq.contract_rep.u_nodes` AS d ON d.address_bytes = x.spender
GROUP BY src, dst;
