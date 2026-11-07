-- Contract-graph revision (docs/revision_contract_graph.md, sections 6 and 12; job 33): the balance of every
-- (token, owner) of the balance population at t1, at T_obs and at 2026-09-30 23:59:59 UTC (the last only for
-- the check of section 6). The population is that of sql/32: the distinct (token, a) of the approvals of
-- c12_logs5 with @start_ts <= block_timestamp < @tobs_end. The balance at an anchor is the net Transfer flow
-- to the owner up to the anchor (inclusive): c12_bal_pre (the public logs before @obs_start), plus the
-- non-zero transfers of the five tokens in logs_obs from @obs_start to before @start_ts, plus the transfers
-- of c12_logs5 from @start_ts up to the anchor (@t1, @tobs, @end_0930).
-- Values are in base units as FLOAT64 and are not clipped here: a negative value of a few base units is
-- floating-point error, and the clipping to 0 and the dust rule (below 10^-6 token counts as 0) apply where a
-- balance is used (sql/35, sql/43, scripts/balance_audit.py and the gate B jobs).
-- Inputs: contract_rep.c12_bal_pre (sql/32), contract_rep.c12_logs5 (sql/24), contract_rep.logs_obs
--         (sql/01), contract_rep.u_tokens.
-- Parameters: @obs_start, @start_ts, @tobs_end (exclusive), @t1, @tobs, @end_0930 (inclusive), @mid_ts, @end_ts
--         (the W1 label window, end exclusive).
--
-- c12_bal: token, address (20-byte BYTES), bal_t1, bal_tobs, bal_0930 (base units, FLOAT64), n_pre (transfers
--   before @obs_start), n_mid (transfers from @obs_start to before @start_ts), n_win (transfers from @start_ts
--   up to @tobs), n_w1 (transfers from @mid_ts to before @end_ts); every count is of the non-zero transfers in
--   which the address is the sender or the recipient (a self-transfer counted twice).

CREATE TEMP FUNCTION u256(v BYTES) AS (
  IFNULL((SELECT SUM(c * POW(256.0, LENGTH(v) - 1 - o))
          FROM UNNEST(TO_CODE_POINTS(v)) AS c WITH OFFSET o), 0.0)
);

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.c12_bal` AS
WITH pop AS (
  SELECT DISTINCT token, a AS address
  FROM `dissertation-bq.contract_rep.c12_logs5`
  WHERE kind = 'A'
    AND block_timestamp >= TIMESTAMP(@start_ts)
    AND block_timestamp < TIMESTAMP(@tobs_end)
),
mid AS (
  SELECT emitter AS token, a, b, u256(val) AS v
  FROM `dissertation-bq.contract_rep.logs_obs`
  WHERE kind = 'T'
    AND block_timestamp >= TIMESTAMP(@obs_start)
    AND block_timestamp < TIMESTAMP(@start_ts)
    AND emitter IN (SELECT token FROM `dissertation-bq.contract_rep.u_tokens`)
    AND LTRIM(TO_HEX(val), '0') != ''
),
mid_flows AS (
  SELECT token, b AS address, v AS d FROM mid
  UNION ALL
  SELECT token, a AS address, -v AS d FROM mid
),
mid_net AS (
  SELECT f.token, f.address, SUM(f.d) AS net, COUNT(*) AS n
  FROM mid_flows AS f
  JOIN pop AS p ON p.token = f.token AND p.address = f.address
  GROUP BY f.token, f.address
),
win AS (
  SELECT token, a, b, value AS v, block_timestamp
  FROM `dissertation-bq.contract_rep.c12_logs5`
  WHERE kind = 'T'
    AND block_timestamp >= TIMESTAMP(@start_ts)
    AND block_timestamp < TIMESTAMP(@end_ts)
),
win_flows AS (
  SELECT token, b AS address, v AS d, block_timestamp FROM win
  UNION ALL
  SELECT token, a AS address, -v AS d, block_timestamp FROM win
),
win_net AS (
  SELECT f.token, f.address,
         SUM(IF(f.block_timestamp <= TIMESTAMP(@t1), f.d, 0.0)) AS net_t1,
         SUM(IF(f.block_timestamp <= TIMESTAMP(@tobs), f.d, 0.0)) AS net_tobs,
         SUM(IF(f.block_timestamp <= TIMESTAMP(@end_0930), f.d, 0.0)) AS net_0930,
         COUNTIF(f.block_timestamp <= TIMESTAMP(@tobs)) AS n_win,
         COUNTIF(f.block_timestamp >= TIMESTAMP(@mid_ts)) AS n_w1
  FROM win_flows AS f
  JOIN pop AS p ON p.token = f.token AND p.address = f.address
  GROUP BY f.token, f.address
)
SELECT p.token, p.address,
       IFNULL(b.net, 0.0) + IFNULL(m.net, 0.0) + IFNULL(w.net_t1, 0.0) AS bal_t1,
       IFNULL(b.net, 0.0) + IFNULL(m.net, 0.0) + IFNULL(w.net_tobs, 0.0) AS bal_tobs,
       IFNULL(b.net, 0.0) + IFNULL(m.net, 0.0) + IFNULL(w.net_0930, 0.0) AS bal_0930,
       IFNULL(b.n, 0) AS n_pre, IFNULL(m.n, 0) AS n_mid, IFNULL(w.n_win, 0) AS n_win, IFNULL(w.n_w1, 0) AS n_w1
FROM pop AS p
LEFT JOIN `dissertation-bq.contract_rep.c12_bal_pre` AS b ON b.token = p.token AND b.address = p.address
LEFT JOIN mid_net AS m ON m.token = p.token AND m.address = p.address
LEFT JOIN win_net AS w ON w.token = p.token AND w.address = p.address;
