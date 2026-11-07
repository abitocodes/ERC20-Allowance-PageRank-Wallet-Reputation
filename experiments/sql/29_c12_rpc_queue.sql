-- Contract-graph revision (docs/revision_contract_graph.md, sections 4.1 to 4.3 and 12; job 29): the RPC queue
-- K, the addresses whose code scripts/check_account_code.py reads, with the reason each one is in it.
--   counterparty   an end of E (c12_ends) that sent no transaction (c12_tx_senders), with at least one
--                  counterparty in c12_pairs5, in either direction and of either kind of event, that is
--                  neither the zero address nor a transaction sender. An end of E outside K that sent no
--                  transaction has only transaction senders and the zero address as counterparties, so it is
--                  never the end of an edge between contracts (section 4.3). The system addresses (0x...01 to
--                  0x...ff, the precompiles) are in K like any other end: they are typed, and sql/31 keeps them
--                  out of the node set (section 4.2 rule 4).
--   cohort         every member of u12_cohort_tobs or u12_cohort_t1;
--   spender        every spender of u12_labels_w0 or u12_labels_w1 (column wallet, 0x hex);
--                  transaction senders among these two are read as well (section 4.3 adds every member to K),
--                  so that every cohort member and spender has an account type;
--   audit_sender   the __AUDIT_SENDERS__ transaction senders with the lowest SHA-256 of @sender_salt followed
--                  by the lowercase 0x hex address;
--   audit_untyped  the __AUDIT_UNTYPED__ ends of E outside K (cohort, spender and counterparty) that sent no
--                  transaction, with the lowest SHA-256 of @untyped_salt followed by the lowercase 0x hex
--                  address.
-- One row per address; an address with several reasons takes the first of cohort, spender, counterparty,
-- audit_sender, audit_untyped. The sample sizes are text substitutions because LIMIT takes no STRING
-- parameter.
-- Inputs: contract_rep.c12_ends, c12_pairs5 (sql/25), c12_tx_senders (sql/26), c12_emitters (sql/27),
--         c12_creations (sql/28), u12_cohort_tobs, u12_cohort_t1 (sql/21), u12_labels_w0, u12_labels_w1
--         (sql/16 of the twelve-month variant).
-- Parameters: @sender_salt, @untyped_salt.
--
-- c12_rpc_queue: address (lowercase 0x hex STRING), reason (STRING), is_emitter (in c12_emitters), is_created
--   (in c12_creations); the two flags are cross-checks only.

CREATE OR REPLACE TABLE `dissertation-bq.contract_rep.c12_rpc_queue` AS
WITH
cand AS (
  SELECT e.address
  FROM `dissertation-bq.contract_rep.c12_ends` AS e
  LEFT JOIN `dissertation-bq.contract_rep.c12_tx_senders` AS s ON s.address = e.address
  WHERE s.address IS NULL
),
links AS (
  SELECT a AS x, b AS y FROM `dissertation-bq.contract_rep.c12_pairs5`
  UNION ALL
  SELECT b AS x, a AS y FROM `dissertation-bq.contract_rep.c12_pairs5`
),
open_links AS (
  SELECT l.x
  FROM links AS l
  LEFT JOIN `dissertation-bq.contract_rep.c12_tx_senders` AS s ON s.address = l.y
  WHERE s.address IS NULL
    AND l.y != FROM_HEX(REPEAT('00', 20))
),
counterparty AS (
  SELECT c.address
  FROM cand AS c
  WHERE c.address IN (SELECT x FROM open_links)
),
listed AS (
  SELECT address, 1 AS pri FROM `dissertation-bq.contract_rep.u12_cohort_tobs`
  UNION ALL
  SELECT address, 1 AS pri FROM `dissertation-bq.contract_rep.u12_cohort_t1`
  UNION ALL
  SELECT FROM_HEX(SUBSTR(wallet, 3)) AS address, 2 AS pri FROM `dissertation-bq.contract_rep.u12_labels_w0`
  UNION ALL
  SELECT FROM_HEX(SUBSTR(wallet, 3)) AS address, 2 AS pri FROM `dissertation-bq.contract_rep.u12_labels_w1`
),
k AS (
  SELECT u.address, MIN(u.pri) AS pri
  FROM (
    SELECT address, pri FROM listed
    UNION ALL
    SELECT address, 3 AS pri FROM counterparty
  ) AS u
  GROUP BY u.address
),
audit_sender AS (
  SELECT address, 4 AS pri
  FROM `dissertation-bq.contract_rep.c12_tx_senders`
  ORDER BY SHA256(CONCAT(@sender_salt, '0x', TO_HEX(address)))
  LIMIT __AUDIT_SENDERS__
),
audit_untyped AS (
  SELECT e.address, 5 AS pri
  FROM `dissertation-bq.contract_rep.c12_ends` AS e
  LEFT JOIN k ON k.address = e.address
  LEFT JOIN `dissertation-bq.contract_rep.c12_tx_senders` AS s ON s.address = e.address
  WHERE k.address IS NULL AND s.address IS NULL
  ORDER BY SHA256(CONCAT(@untyped_salt, '0x', TO_HEX(e.address)))
  LIMIT __AUDIT_UNTYPED__
),
queue AS (
  SELECT address, MIN(pri) AS pri
  FROM (
    SELECT address, pri FROM k
    UNION ALL
    SELECT address, pri FROM audit_sender
    UNION ALL
    SELECT address, pri FROM audit_untyped
  )
  GROUP BY address
)
SELECT CONCAT('0x', TO_HEX(q.address)) AS address,
       CASE q.pri WHEN 1 THEN 'cohort' WHEN 2 THEN 'spender' WHEN 3 THEN 'counterparty'
                  WHEN 4 THEN 'audit_sender' ELSE 'audit_untyped' END AS reason,
       m.address IS NOT NULL AS is_emitter,
       c.address IS NOT NULL AS is_created
FROM queue AS q
LEFT JOIN `dissertation-bq.contract_rep.c12_emitters` AS m ON m.address = q.address
LEFT JOIN `dissertation-bq.contract_rep.c12_creations` AS c ON c.address = q.address;
