-- Twelve-month variant (docs/revision_one_year_window.md, section 4, Tokens): the rows of every
-- token in the registered ego data inside the T_obs score window, counted as the token rule of
-- docs/revision_price_weighting.md section 3 counts them (ego transfers plus positive latest
-- allowances at T_obs). Reported only: the five selected tokens are kept whatever this ranking
-- says. scripts/run_usd12m_pipeline.py ranks the listed and priced tokens locally.
-- Parameters: @start_ts, @end_ts (exclusive), @anchor_ts (inclusive).
-- Destination: contract_rep.u12_token_rows, one row per token address.

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.u12_token_rows` AS
WITH tr AS (
  SELECT token_address AS token, COUNT(*) AS n
  FROM `dissertation-bq.contract_rep.transfers_ego`
  WHERE block_timestamp >= TIMESTAMP(@start_ts) AND block_timestamp < TIMESTAMP(@end_ts)
  GROUP BY 1
),
latest AS (
  SELECT token_address AS token, value,
         ROW_NUMBER() OVER (PARTITION BY token_address, owner, spender
                            ORDER BY block_number DESC, log_index DESC) AS rn
  FROM `dissertation-bq.contract_rep.approvals_ego`
  WHERE block_timestamp >= TIMESTAMP(@start_ts) AND block_timestamp <= TIMESTAMP(@anchor_ts)
),
al AS (SELECT token, COUNT(*) AS n FROM latest WHERE rn = 1 AND value > 0 GROUP BY 1)
SELECT CONCAT('0x', TO_HEX(COALESCE(tr.token, al.token))) AS token,
       IFNULL(tr.n, 0) AS transfers,
       IFNULL(al.n, 0) AS latest_allowances,
       IFNULL(tr.n, 0) + IFNULL(al.n, 0) AS rows_total
FROM tr FULL OUTER JOIN al ON tr.token = al.token;
