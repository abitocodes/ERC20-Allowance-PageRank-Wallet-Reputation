-- Contract-graph revision (docs/revision_contract_graph.md section 8 and the gate B amendment of section 13; job 39,
-- step rest): the label split of __TAG__, a secondary description outside every rule. The labels stay those of
-- u12_labels___TAG__; this job recounts them on the same inputs with the definitions of sql/16_usd_labels.sql (lines
-- 12-15 and 18-98 copied, lines 99-112 copied into the CTE labels), so that the counted accounts are exactly those of
-- the twelve-month labels (sql/42 compares the recount with u12_labels___TAG__ column by column), and splits every
-- label by the class of the account it counts: user accounts (c12_user_accounts), contracts (c12_contracts) and
-- other (the zero address of mints, the system addresses, untyped addresses). The parts of a count sum to the count;
-- a rate is split as part count over the same denominator n_t1; the revoked value by the owner's class.
-- __FREEZE__ is the anchor tag of the snapshot (t1, tobs); __APPROVALS__, __TRANSFERS__ the twelve-month ego views
-- that hold the label window; __SEEN__ the view of the score window (the table sql/16 reads as u_transfers);
-- __LOGS__ the materialised logs of the drain heuristic (logs_obs, logs_w1): the substitutions and renames of
-- scripts/run_usd12m_pipeline.py lines 294-309. spender_class is the class of c12_members (list spenders___TAG__).
-- Inputs: contract_rep.u12_allow_triples___FREEZE__, __APPROVALS__, __TRANSFERS__, __SEEN__, __LOGS__, u_tokens,
--   c12_contracts, c12_user_accounts (sql/31), c12_members (sql/38_c12_cohorts.sql).
-- Parameters: @start_ts (score window start), @t1 (freeze, inclusive), @out_start, @out_end (label window, inclusive).

CREATE TEMP FUNCTION u256(v BYTES) AS (
  IFNULL((SELECT SUM(c * POW(256.0, LENGTH(v) - 1 - o))
          FROM UNNEST(TO_CODE_POINTS(v)) AS c WITH OFFSET o), 0.0)
);

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.c12_label_parts___TAG__` AS
WITH t1_pairs AS (
  SELECT owner, spender, SUM(usd) AS pair_value
  FROM `dissertation-bq.contract_rep.u12_allow_triples___FREEZE__`
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
  FROM `dissertation-bq.contract_rep.__SEEN__`
  WHERE block_timestamp >= TIMESTAMP(@start_ts) AND block_timestamp <= TIMESTAMP(@t1)
    AND to_address IN (SELECT spender FROM spenders) AND from_address != to_address
    AND usd IS NOT NULL
),
win_senders AS (
  SELECT DISTINCT to_address, from_address
  FROM `dissertation-bq.contract_rep.__TRANSFERS__`
  WHERE block_timestamp >= TIMESTAMP(@out_start) AND block_timestamp <= TIMESTAMP(@out_end)
    AND to_address IN (SELECT spender FROM spenders) AND from_address != to_address
    AND usd IS NOT NULL
),
new_senders AS (
  SELECT w.to_address AS spender, COUNT(*) AS n_new_senders
  FROM win_senders AS w
  LEFT JOIN seen AS s ON s.to_address = w.to_address AND s.from_address = w.from_address
  WHERE s.from_address IS NULL
  GROUP BY w.to_address
),
drain_stream AS (
  SELECT owner, token_address, spender, block_timestamp, value AS approved, NULL AS sent
  FROM win_appr WHERE value > 0
  UNION ALL
  SELECT a AS owner, emitter AS token_address, NULL, block_timestamp, NULL, u256(val)
  FROM `dissertation-bq.contract_rep.__LOGS__`
  WHERE kind = 'T'
    AND LTRIM(TO_HEX(val), '0') != ''
    AND block_timestamp >= TIMESTAMP(@out_start)
    AND block_timestamp <= TIMESTAMP_ADD(TIMESTAMP(@out_end), INTERVAL 6 HOUR)
    AND emitter IN (SELECT token FROM `dissertation-bq.contract_rep.u_tokens`)
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
),
labels AS (
  SELECT s.spender,
         IFNULL(n.n_new, 0) AS future_new_approvers,
         IFNULL(r.n_rev, 0) AS future_revoke_count,
         IFNULL(r.n_rev, 0) / o.n_t1 AS future_revoke_rate,
         1.0 - IFNULL(r.n_rev, 0) / o.n_t1 AS future_keep_rate,
         IFNULL(r.rev_value, 0.0) AS future_revoke_value,
         IFNULL(ns.n_new_senders, 0) AS future_new_transfer_senders,
         IFNULL(d.n_drain, 0) AS future_drain_owners,
         o.n_t1
  FROM spenders AS s
  JOIN t1_owners AS o ON o.spender = s.spender
  LEFT JOIN new_appr AS n ON n.spender = s.spender
  LEFT JOIN revoked AS r ON r.spender = s.spender
  LEFT JOIN new_senders AS ns ON ns.spender = s.spender
  LEFT JOIN drain AS d ON d.spender = s.spender
),
cls AS (
  SELECT address, 'contract' AS cls FROM `dissertation-bq.contract_rep.c12_contracts`
  UNION ALL
  SELECT address, 'user' AS cls FROM `dissertation-bq.contract_rep.c12_user_accounts`
),
counted AS (
  SELECT 't1' AS what, spender, owner AS account, 0.0 AS v FROM t1_pairs
  UNION ALL
  SELECT DISTINCT 'new_appr' AS what, w.spender, w.owner AS account, 0.0 AS v
  FROM win_appr AS w
  LEFT JOIN t1_pairs AS p ON p.owner = w.owner AND p.spender = w.spender
  WHERE w.value > 0 AND p.owner IS NULL
  UNION ALL
  SELECT 'revoked' AS what, spender, owner AS account, pair_value AS v
  FROM (
    SELECT DISTINCT w.spender, w.owner, p.pair_value
    FROM win_appr AS w
    JOIN t1_pairs AS p ON p.owner = w.owner AND p.spender = w.spender
    WHERE w.value = 0
  )
  UNION ALL
  SELECT 'new_senders' AS what, w.to_address AS spender, w.from_address AS account, 0.0 AS v
  FROM win_senders AS w
  LEFT JOIN seen AS s ON s.to_address = w.to_address AND s.from_address = w.from_address
  WHERE s.from_address IS NULL
  UNION ALL
  SELECT DISTINCT 'drain' AS what, spender, owner AS account, 0.0 AS v
  FROM drain_marked
  WHERE approved IS NOT NULL
    AND ((approved >= 1e30 AND n_sent_1h > 0) OR (approved < 1e30 AND max_sent_6h >= 0.5 * approved))
),
parts AS (
  SELECT c.spender,
         COUNTIF(c.what = 't1' AND k.cls = 'user') AS n_t1_user,
         COUNTIF(c.what = 't1' AND k.cls = 'contract') AS n_t1_contract,
         COUNTIF(c.what = 't1' AND k.cls IS NULL) AS n_t1_other,
         COUNTIF(c.what = 'new_appr' AND k.cls = 'user') AS new_appr_user,
         COUNTIF(c.what = 'new_appr' AND k.cls = 'contract') AS new_appr_contract,
         COUNTIF(c.what = 'new_appr' AND k.cls IS NULL) AS new_appr_other,
         COUNTIF(c.what = 'revoked' AND k.cls = 'user') AS rev_user,
         COUNTIF(c.what = 'revoked' AND k.cls = 'contract') AS rev_contract,
         COUNTIF(c.what = 'revoked' AND k.cls IS NULL) AS rev_other,
         SUM(IF(c.what = 'revoked' AND k.cls = 'user', c.v, 0.0)) AS rev_value_user,
         SUM(IF(c.what = 'revoked' AND k.cls = 'contract', c.v, 0.0)) AS rev_value_contract,
         SUM(IF(c.what = 'revoked' AND k.cls IS NULL, c.v, 0.0)) AS rev_value_other,
         COUNTIF(c.what = 'new_senders' AND k.cls = 'user') AS new_senders_user,
         COUNTIF(c.what = 'new_senders' AND k.cls = 'contract') AS new_senders_contract,
         COUNTIF(c.what = 'new_senders' AND k.cls IS NULL) AS new_senders_other,
         COUNTIF(c.what = 'drain' AND k.cls = 'user') AS drain_user,
         COUNTIF(c.what = 'drain' AND k.cls = 'contract') AS drain_contract,
         COUNTIF(c.what = 'drain' AND k.cls IS NULL) AS drain_other
  FROM counted AS c
  LEFT JOIN cls AS k ON k.address = c.account
  GROUP BY c.spender
)
SELECT CONCAT('0x', TO_HEX(l.spender)) AS wallet,
       m.class AS spender_class,
       l.future_new_approvers, l.future_revoke_count, l.future_revoke_rate, l.future_keep_rate,
       l.future_revoke_value, l.future_new_transfer_senders, l.future_drain_owners,
       l.n_t1, p.n_t1_user, p.n_t1_contract, p.n_t1_other,
       p.new_appr_user AS future_new_approvers_user,
       p.new_appr_contract AS future_new_approvers_contract,
       p.new_appr_other AS future_new_approvers_other,
       p.rev_user AS future_revoke_count_user,
       p.rev_contract AS future_revoke_count_contract,
       p.rev_other AS future_revoke_count_other,
       p.rev_user / l.n_t1 AS future_revoke_rate_user,
       p.rev_contract / l.n_t1 AS future_revoke_rate_contract,
       p.rev_other / l.n_t1 AS future_revoke_rate_other,
       (p.n_t1_user - p.rev_user) / l.n_t1 AS future_keep_rate_user,
       (p.n_t1_contract - p.rev_contract) / l.n_t1 AS future_keep_rate_contract,
       (p.n_t1_other - p.rev_other) / l.n_t1 AS future_keep_rate_other,
       p.rev_value_user AS future_revoke_value_user,
       p.rev_value_contract AS future_revoke_value_contract,
       p.rev_value_other AS future_revoke_value_other,
       p.new_senders_user AS future_new_transfer_senders_user,
       p.new_senders_contract AS future_new_transfer_senders_contract,
       p.new_senders_other AS future_new_transfer_senders_other,
       p.drain_user AS future_drain_owners_user,
       p.drain_contract AS future_drain_owners_contract,
       p.drain_other AS future_drain_owners_other
FROM labels AS l
JOIN parts AS p ON p.spender = l.spender
LEFT JOIN `dissertation-bq.contract_rep.c12_members` AS m
  ON m.address_bytes = l.spender AND m.list = 'spenders___TAG__';

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.c12_x_label_split___TAG__` AS
SELECT wallet, spender_class, n_t1, n_t1_user, n_t1_contract, n_t1_other,
       future_new_approvers_user, future_new_approvers_contract, future_new_approvers_other,
       future_revoke_count_user, future_revoke_count_contract, future_revoke_count_other,
       future_revoke_rate_user, future_revoke_rate_contract, future_revoke_rate_other,
       future_keep_rate_user, future_keep_rate_contract, future_keep_rate_other,
       future_revoke_value_user, future_revoke_value_contract, future_revoke_value_other,
       future_new_transfer_senders_user, future_new_transfer_senders_contract, future_new_transfer_senders_other,
       future_drain_owners_user, future_drain_owners_contract, future_drain_owners_other
FROM `dissertation-bq.contract_rep.c12_label_parts___TAG__`;
