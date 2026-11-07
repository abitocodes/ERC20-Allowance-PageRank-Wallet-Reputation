-- Contract-graph revision (docs/revision_contract_graph.md, sections 6 and 12; job 43): the sample of the
-- balance check. For each of the five tokens, the @per_cell (token, owner) pairs of c12_bal with the lowest
-- SHA-256 of @audit_salt followed by the lowercase 0x hex token and the lowercase 0x hex owner, among the pairs
-- whose balance at T_obs is below 10^(decimals - @dust_digits) base units (cell 'zero': below 10^-6 token,
-- negative values included), and as many among the rest (cell 'positive'). A cell with fewer pairs gives all
-- of them. scripts/balance_audit.py compares their balances with balanceOf.
-- Inputs: contract_rep.c12_bal (sql/33), contract_rep.u_tokens.
-- Parameters: @audit_salt, @per_cell, @dust_digits (6 for the dust rule of 10^-6 token).
--
-- c12_bal_audit: token, owner (lowercase 0x hex STRING), bal_tobs, bal_0930 (base units, FLOAT64, not
--   clipped), n_w1 (transfers from 2026-07-01 to 2026-09-30), decimals, cell ('zero' or 'positive').

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.c12_bal_audit` AS
WITH cells AS (
  SELECT b.token, b.address, b.bal_tobs, b.bal_0930, b.n_w1, t.decimals,
         IF(b.bal_tobs < POW(10.0, t.decimals - CAST(@dust_digits AS INT64)), 'zero', 'positive') AS cell,
         SHA256(CONCAT(@audit_salt, '0x', TO_HEX(b.token), '0x', TO_HEX(b.address))) AS h
  FROM `dissertation-bq.contract_rep.c12_bal` AS b
  JOIN `dissertation-bq.contract_rep.u_tokens` AS t ON t.token = b.token
),
ranked AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY token, cell ORDER BY h) AS r
  FROM cells
)
SELECT CONCAT('0x', TO_HEX(token)) AS token, CONCAT('0x', TO_HEX(address)) AS owner,
       bal_tobs, bal_0930, n_w1, decimals, cell
FROM ranked
WHERE r <= CAST(@per_cell AS INT64);
