-- Holdout labels for every spender that holds a positive latest allowance at the freeze
-- (analysis plan, section 5); the contract filter is applied locally from the code check.
-- Parameters: @start_ts (data start), @t1 (freeze, inclusive), @out_start, @out_end (inclusive).
-- __TAG__ names the window (w0, w1); __APPROVALS__, __TRANSFERS__ name the ego tables that
-- hold the label window, __LOGS__ the materialised logs used by the drain heuristic.
-- Reads allow_triples___FREEZE__ for the snapshot at the freeze.
--
-- future_new_approvers: owners with a positive approval to the spender inside the window
--   whose (owner, spender) pair held no positive allowance at the freeze.
-- future_revoke_count / rate / value: owners of a positive pair at the freeze that set an
--   allowance of that pair to zero inside the window; the rate divides by the owners at the freeze.
-- future_new_transfer_senders: other addresses that send to the spender inside the window
--   and sent it nothing between the data start and the freeze.
-- future_drain_owners: owners whose positive approval inside the window is followed by a
--   transfer of the same token from the owner, within 6 hours and of at least half the
--   approved amount, or within 1 hour of any amount when the approval is >= 1e30.

CREATE TEMP FUNCTION u256(v BYTES) AS (
  IFNULL((SELECT SUM(c * POW(256.0, LENGTH(v) - 1 - o))
          FROM UNNEST(TO_CODE_POINTS(v)) AS c WITH OFFSET o), 0.0)
);

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.labels___TAG__` AS
WITH t1_pairs AS (
  SELECT owner, spender, SUM(value) AS pair_value
  FROM `dissertation-bq.contract_rep.allow_triples___FREEZE__`
  GROUP BY owner, spender
),
spenders AS (SELECT DISTINCT spender FROM t1_pairs),
win_appr AS (
  SELECT * FROM `dissertation-bq.contract_rep.__APPROVALS__`
  WHERE block_timestamp >= TIMESTAMP(@out_start) AND block_timestamp <= TIMESTAMP(@out_end)
    AND spender IN (SELECT spender FROM spenders)
),
new_appr AS (
  SELECT w.spender, COUNT(DISTINCT w.owner) AS n_new
  FROM win_appr AS w
  LEFT JOIN t1_pairs AS p ON p.owner = w.owner AND p.spender = w.spender
  WHERE w.value > 0 AND p.owner IS NULL
  GROUP BY w.spender
),
revoked AS (
  SELECT spender, COUNT(*) AS n_rev, SUM(pair_value) AS rev_value
  FROM (
    SELECT DISTINCT w.spender, w.owner, p.pair_value
    FROM win_appr AS w
    JOIN t1_pairs AS p ON p.owner = w.owner AND p.spender = w.spender
    WHERE w.value = 0
  )
  GROUP BY spender
),
t1_owners AS (SELECT spender, COUNT(*) AS n_t1 FROM t1_pairs GROUP BY spender),
seen AS (
  SELECT DISTINCT to_address, from_address
  FROM `dissertation-bq.contract_rep.transfers_ego`
  WHERE block_timestamp >= TIMESTAMP(@start_ts) AND block_timestamp <= TIMESTAMP(@t1)
    AND to_address IN (SELECT spender FROM spenders) AND from_address != to_address
),
win_senders AS (
  SELECT DISTINCT to_address, from_address
  FROM `dissertation-bq.contract_rep.__TRANSFERS__`
  WHERE block_timestamp >= TIMESTAMP(@out_start) AND block_timestamp <= TIMESTAMP(@out_end)
    AND to_address IN (SELECT spender FROM spenders) AND from_address != to_address
),
new_senders AS (
  SELECT w.to_address AS spender, COUNT(*) AS n_new_senders
  FROM win_senders AS w
  LEFT JOIN seen AS s ON s.to_address = w.to_address AND s.from_address = w.from_address
  WHERE s.from_address IS NULL
  GROUP BY w.to_address
),
drain_stream AS (
  -- One stream per (owner, token): the owner's approvals to cohort-window spenders and the
  -- owner's non-zero outgoing transfers of that token. Window frames give, for each
  -- approval, the largest transfer in the next 6 hours and the transfers in the next hour.
  SELECT owner, token_address, spender, block_timestamp, value AS approved, NULL AS sent
  FROM win_appr WHERE value > 0
  UNION ALL
  SELECT a AS owner, emitter AS token_address, NULL, block_timestamp, NULL, u256(val)
  FROM `dissertation-bq.contract_rep.__LOGS__`
  WHERE kind = 'T'
    AND LTRIM(TO_HEX(val), '0') != ''
    AND block_timestamp >= TIMESTAMP(@out_start)
    AND block_timestamp <= TIMESTAMP_ADD(TIMESTAMP(@out_end), INTERVAL 6 HOUR)
    AND a IN (SELECT owner FROM win_appr WHERE value > 0)
),
drain_marked AS (
  SELECT spender, owner, approved,
    MAX(sent) OVER w6 AS max_sent_6h,
    COUNT(sent) OVER w1 AS n_sent_1h
  FROM drain_stream
  WINDOW
    w6 AS (PARTITION BY owner, token_address ORDER BY UNIX_MICROS(block_timestamp)
           RANGE BETWEEN 1 FOLLOWING AND 21600000000 FOLLOWING),
    w1 AS (PARTITION BY owner, token_address ORDER BY UNIX_MICROS(block_timestamp)
           RANGE BETWEEN 1 FOLLOWING AND 3600000000 FOLLOWING)
),
drain AS (
  SELECT spender, COUNT(DISTINCT owner) AS n_drain
  FROM drain_marked
  WHERE approved IS NOT NULL
    AND ((approved >= 1e30 AND n_sent_1h > 0) OR (approved < 1e30 AND max_sent_6h >= 0.5 * approved))
  GROUP BY spender
)
SELECT CONCAT('0x', TO_HEX(s.spender)) AS wallet,
       IFNULL(n.n_new, 0) AS future_new_approvers,
       IFNULL(r.n_rev, 0) AS future_revoke_count,
       IFNULL(r.n_rev, 0) / o.n_t1 AS future_revoke_rate,
       1.0 - IFNULL(r.n_rev, 0) / o.n_t1 AS future_keep_rate,
       IFNULL(r.rev_value, 0.0) AS future_revoke_value,
       IFNULL(ns.n_new_senders, 0) AS future_new_transfer_senders,
       IFNULL(d.n_drain, 0) AS future_drain_owners
FROM spenders AS s
JOIN t1_owners AS o ON o.spender = s.spender
LEFT JOIN new_appr AS n ON n.spender = s.spender
LEFT JOIN revoked AS r ON r.spender = s.spender
LEFT JOIN new_senders AS ns ON ns.spender = s.spender
LEFT JOIN drain AS d ON d.spender = s.spender;
