# Revision: a graph of contracts only, allowances capped at the owner's balance, and the discovery-order test

- Written on 7 November 2026, after the registered results, the results of the two earlier revisions (`docs/revision_price_weighting.md`, `docs/revision_one_year_window.md`) and the post hoc checks of `exploratory/` were known. One of those checks had already capped allowances at the owner's balance and compared the capped weights on the W0 and W1 spender labels (section 1), and the sizes of a t1 contract graph built from the pair tables of the twelve-month revision were known (`docs/discovery_protocol.md`, header). It is committed **before any account-type read, BigQuery job, score, importance, proxy or constant of this revision is computed**; the commit that adds this file is the reference point of this revision (gate A). The labels of this revision are those of the twelve-month revision (section 8): they exist and were known, as were the earlier evaluations on them. A second commit (gate B, section 12) fixes the parameters that the structure pilot sets by rule, before any score, importance, proxy or constant of this revision exists.
- This is a further deviation from the analysis plan (`docs/analysis_plan.md`, commit d060f3a, which is 43d8045 of the working repository; see `HISTORY.md` at the repository root), from the W1 registration (`docs/registration_w1.md`, commit 1747e64, 0d3a057 of the working repository) and from the two earlier revisions. It is decided after results were seen, so its results are post hoc and are never called registered.
- The registered analysis and the two US-dollar analyses stay as they were committed. Their configuration, SQL (`sql/01`–`23`), code paths (`CONTRACT_REP_VARIANT` unset, `=usd` and `=usd12m`) and outputs are not changed. This revision adds the variant `CONTRACT_REP_VARIANT=contract12m`, with its own overlay (`config/overlay_contract12m.yaml`), BigQuery tables (`c12_*`), folders and constants.
- The discovery-order test is specified in `docs/discovery_protocol.md`, which is part of this revision.

## 1. Why the graph changes

- **User accounts.** In the earlier analyses the graphs held every owner, spender, sender and recipient of the cohort's events, so user accounts supplied most of the edges and most of the restart mass. A user account is cheap to create and much of its activity may be automated, so a score that its edges move is cheap to move. In a graph whose nodes are contracts, each node costs a deployment and each edge records a relation one contract holds toward another.
- **Allowances above the balance.** An allowance can exceed the owner's balance of the token or be unlimited. The spender can move at most the balance. Counting each allowance only up to its owner's balance at the freeze measures what the spender can actually move. The cap had been tried in the exploratory check of 13 October 2026 (`exploratory/2026-10-13-unlimited-allowances`), on the graphs of the 33-month US-dollar analysis (`CONTRACT_REP_VARIANT=usd`), which hold user accounts: with it (the variant `er_v_min` of its `results_usd_bal.json`), EndorseRank ranked the W0 and W1 spenders about as well or slightly better on new approval pairs and worse on new transfer senders. The cap is adopted for the reason above, not for those results.
- **Aim of the scores.** The scores are meant to find, among the very many contracts of the chain, those that users rely on, as PageRank was shown to find important web pages sooner than other orderings (Cho, Garcia-Molina and Page, 1998, Computer Networks and ISDN Systems 30, 161–172, doi:10.1016/S0169-7552(98)00108-1). The discovery-order test repeats their crawl-ordering experiment on the contract graph. The out-of-window prediction of the plan follows it.

## 2. Status of the analyses (decision of 7 November 2026)

- The contract-graph analysis is the main analysis.
- The registered analysis is reported as it was obtained, with the verdicts of rule A and of the registered criteria of rule B that this revision applies (section 11). The criteria on GMX V2 traders (F3, F4, F5, P, Q, R1–R3) are not applied or reported in this revision or in the texts built on it (author's decision); their definitions stay in `docs/registration_w1.md` and their registered results in the registered digest (`data/3-published-results-for-thesis/results_digest.md`).
- The twelve-month US-dollar analysis (`revised-usd-12m/`), whose graphs hold user accounts, is not reported in the texts (author's decision). Its outputs stay on disk and on Drive as they are, like those of the 33-month US-dollar analysis.
- On the contract-graph scores, rule A and two of the registered criteria of rule B are applied as a re-analysis after the registered results were known.
- The supervisors have not yet confirmed this decision.

## 3. Windows

As in `docs/revision_one_year_window.md` section 3:

| | Score window (both ends inclusive) | Anchor | Label window |
|---|---|---|---|
| Same window and W1 | 2025-07-01 00:00:00 UTC to 2026-06-30 23:59:59 UTC | T_obs = 2026-06-30 23:59:59 UTC | W1: 2026-07-01 to 2026-09-30 |
| W0 | 2025-04-01 00:00:00 UTC to 2026-03-31 23:59:59 UTC | t1 = 2026-03-31 23:59:59 UTC | W0: 2026-04-01 to 2026-06-30 |

The typing window, from which the addresses to type are taken, covers both score windows and both label windows: 2025-04-01 00:00:00 UTC to 2026-10-01 00:00:00 UTC (end exclusive). The five tokens are those of the US-dollar revisions: WETH, USDC, USD₮0, ARB and WBTC.

## 4. Account types

### 4.1 Addresses

- **E** is every address other than the zero address that is an end (owner, spender, sender or recipient) of a five-token `Approval` of any value or of a non-zero `Transfer` in the typing window, read from `logs_obs` and `logs_w1`. No public log is scanned again for E.
- The system addresses 0x…0001 to 0x…00ff (the precompiles) are read like the other addresses of the queue (4.3), except that an error answer of a call to one of them, other than the node's abort at its time limit, is that call's failure at once (a precompile runs no code). Whatever the reads give, they are never contracts and never graph nodes. A system address that sent a transaction is a user account by rule 1 of 4.2, as protocol section 5 counts every transaction sender; any other system address is no user account either and adds to no importance.

### 4.2 Rules

1. **Transaction senders are user accounts.** An address that sent a transaction (public `transactions` view, any block before 2026-10-01) is an externally owned account; an EIP-7702 account is one. Apart from an EIP-7702 delegation, an account with code cannot send a transaction (EIP-3607).
2. **Code.** Every address of the RPC queue (4.3) is read with `eth_getCode` at block 513,216,506, the block of the account-type read of the cohort candidates on 9 October 2026 (`data/1-raw-blockchain-extracts/cohort/candidate_account_types.json`). For a transaction sender the read serves only as a check of rule 1: the sender stays a user account whatever it returns. The reads go only to the endpoints that serve that block; an endpoint serves a block if it returns the code of native USDC there. A failed request, a rate limit or an error answer is retried three times; an endpoint does not serve the block if it answers without that code or if every attempt fails. If no endpoint serves the block, the latest block at the first read is pinned instead and recorded, and only the endpoints that serve the pinned block are used. A read at a block after 30 September 2026 also sees code deployed after the end of the data; every address is typed by its code at the block read, which this revision accepts. No code means an externally owned account. An EIP-7702 delegation designator (`0xef0100` followed by 20 bytes) means an externally owned account. Any other code makes the address a candidate contract.
3. **Smart accounts are user accounts.** A candidate contract is a smart account if either test holds at the same block:
   - (a) **Safe.** `getThreshold()` (selector `0xe75235b8`) returns a 32-byte word with a value from 1 to 1,000, and `getOwners()` (`0xa0e67e2b`) decodes to a non-empty list of addresses. (A Safe singleton has an empty owner list and fails.)
   - (b) **ERC-4337 account.** `entryPoint()` (`0xb0d691fe`) returns a canonical EntryPoint (v0.6 `0x5ff137d4b0fdcd49dca30c7cf57e578a026d2789`, v0.7 `0x0000000071727de22e5e9d8baf0edac6f37da032`, v0.8 `0x4337084d9e255ff0702461cf8895ce9e3b5ff108`, v0.9 `0x433709009b8330fda32311df1c2afa402ed8d009`), and the account's code contains `PUSH4` of a `validateUserOp` selector (`0x3a871cdd` for v0.6, `0x19822f7c` for v0.7 and later) and no `PUSH4` of a `validatePaymasterUserOp` selector (`0xf465c77e`, `0x52b7512c`). For a proxy, the code examined is the implementation's.
4. **Contracts.** A candidate contract that is not a smart account is a contract, unless it is a system address.

### 4.3 RPC queue and reads

- **Queue K.** The addresses of E that are not transaction senders and that have at least one counterparty, in either direction and either kind of event, that is neither a transaction sender nor the zero address. To K are added every member of the twelve-month cohorts and spender sets (`u12_cohort_tobs`, `u12_cohort_t1` and the spenders of `u12_labels_w0` and `u12_labels_w1`) and two audit samples: 1,000 transaction senders and 1,000 addresses of E outside K that are not transaction senders, each the addresses with the lowest SHA-256 of a fixed salt and the address.
- An address of E outside K that is not a transaction sender has only user accounts and the zero address as counterparties, so it can never be the end of an edge between contracts. Every counterparty of a contract other than the zero address is either a transaction sender or in K, so every account that sends to or authorises a contract is typed.
- **Reads.** Each address of K gets `eth_getCode`. Proxies are recognised from the code:
  - an EIP-1167 clone is a contract whose code begins with the clone pattern, which carries its implementation;
  - an ERC-1967 proxy is a contract whose code contains the implementation slot constant `0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc` and whose slot holds a non-zero address (`eth_getStorageAt`);
  - a Safe proxy is a contract whose code contains the `masterCopy()` selector `0xa619486e`, as the operand of a `PUSH4` or as the first four bytes of a `PUSH32` operand whose other 28 bytes are zero. The Safe proxies from version 1.1.0 on return their singleton by that selector and hold it in storage slot 0, which is read for every Safe proxy.

  A clone counts as a clone whatever else its code holds. A code with the ERC-1967 constant whose slot holds no address is a Safe proxy if it contains the selector. An implementation's code is read once per implementation. For a proxy whose implementation is not found in these ways (for example a beacon proxy, a proxy that keeps its implementation in another slot, or a Safe proxy whose slot 0 holds no address), rule 3(b) examines the proxy's own code.
- **Probes.** The answers of rule 3 depend on the account's storage when the account is a proxy whose implementation sits in storage, or when it holds a Safe's threshold and owners. So the probes are run address by address on:
  - ERC-1967 proxies;
  - Safe proxies;
  - every address of a code hash whose representative answers `getThreshold()` with a 32-byte word, whatever its value.

  Every other code hash is probed on one representative (its lowest address), and the result holds for every address with that code hash. The decoded answers (threshold, number of owners, EntryPoint) are recorded for every probed address. A call that the node aborts at its time limit is sent again, up to six answered attempts: three at the endpoint that gave the first abort and three at the next one in turn (all six at one endpoint if only one serves the block); an endpoint that fails three requests in a row meanwhile is passed over for the next one. Each call keeps its first answer that is not an abort; a call aborted at all six fails its test, and its address is listed in the output.
- **Output.**
  - `data/1-raw-blockchain-extracts/contract-types/c12_account_types` (parquet parts), with one row per address of K: code kind, code size, code hash (keccak-256), proxy kind and implementation, whether the code contains the `masterCopy()` selector, probe results, wallet kind and account class.
  - `c12_account_types.json`, with the block and how it was chosen, the RPC hosts (never a URL with a key) and those that serve the block, the time of the reads, the counts, the rule settings, the addresses with a call aborted at every attempt, and the SHA-256 of the script, of the rule settings and of the queue. A read resumes an earlier output only if all three are unchanged; otherwise it stops.
- **Endpoints.** Public endpoints are used in order (`contract_graph.rpc_urls` of the overlay). A provider URL with a key is read only from the environment variable `CONTRACT_REP_RPC_URL` and is never written to disk. When the variable is set, its endpoint comes first in the reads of this revision (the typing and the balance check).
- **Code families.** The structure report (protocol section 7) lists the largest groups of contracts by code hash, and every group whose `entryPoint()` answers a canonical EntryPoint although its class is contract. These are the code families of section 13.

## 5. Edges

Every node of every graph is a contract (4.2 rule 4). An edge is kept only when both ends are contracts.

- **Allowance edge** owner → spender at a freeze: for each (token, owner, spender), the latest `Approval` between the start of the score window and the anchor, in (block number, log index) order, kept when its value is positive. Its US-dollar value is `usd_allow` = amount × the token's price on the UTC day of the anchor. **Balance cap:** `usd_eff` = min(`usd_allow`, `bal_eff` × the same price), where `bal_eff` is the owner's balance of the token at the anchor (section 6), set to 0 below 10⁻⁶ token. The edge is kept when `usd_eff` > 0. EndorseRank weight `w_er` = Σ over the pair's tokens of σ(age) · V_A(`usd_eff`); C-PR allowance-layer weight `w_raw` = Σ min(`usd_eff`, U); plus the largest σ, the latest approval time and the slope-sensitivity weights, as in `sql/14`.
- **Uncapped sensitivity.** One sensitivity analysis repeats the comparisons of the scores of section 9 on the W0 and W1 labels on graphs whose allowance layer is uncapped: every (token, owner, spender) between contracts whose latest allowance at the freeze is positive, valued at `usd_allow` in place of `usd_eff` in both weights. It is reported beside the main comparisons, decides no rule, and the discovery-order test does not use it.
- **Transfer edge** sender → recipient: the definitions of `sql/14` unchanged (US dollars at the price of the transfer's UTC day, σ, V_T, `w_awp`, `w_raw` = Σ usd · σ, largest σ, summed USD, first and last time).
- Self-loops are kept, as the solver keeps them.

## 6. Balances

- The balance of (token, address) at an anchor is the net `Transfer` flow of the token to the address up to the anchor (inclusive), in base units as FLOAT64: the public logs before 2023-10-01, `logs_obs` from 2023-10-01 to 2025-03-31 and the five-token table of this revision from 2025-04-01 to the anchor. A negative value is set to 0; a value below 10⁻⁶ token is set to 0.
- The balances are computed for every (token, owner) of a five-token approval from 2025-04-01 to T_obs, at t1, at T_obs and at 2026-09-30 23:59:59 UTC (for the check only).
- **Check.** 1,500 (token, owner) pairs: for each token, 150 with a zero and 150 with a positive balance at T_obs, the pairs with the lowest SHA-256 of a fixed salt and the pair. If an endpoint serves the last block of 30 June 2026 (it answers `balanceOf` of the first pair of the sample at that block with a result; a failed request, a rate limit or an error answer is retried three times, as in section 4.2 rule 2), their balance at T_obs is compared with `balanceOf` at that block on the endpoints that serve it; the match must reach 98%. Otherwise, as in the exploratory check of 13 October 2026, the balance carried to 30 September 2026 is compared with `balanceOf` at the latest block, and the match among owners with no transfer from 1 July to 30 September must reach 99%; if no endpoint gives the latest block either, the check gives no result and is run again. A match counts within 10⁻⁹ relative or 10⁻⁶ token. Both thresholds were set after the match rates of that check were known (98.1% of its pairs and 99.6% of its owners with no transfer from July to September; the check did not establish the cause of its 29 mismatches, 6 of them among those owners). Below the threshold the run stops until the cause is understood. The driver then refuses every later step. It goes on only with an author's decision given to it (`--author-decision`); the run manifest records the decision, and section 13 explains it.

## 7. Constants

Computed after gate B (section 12), before any score, by the rules of `revision_price_weighting.md` section 5 on the W0 score window (events from 2025-04-01 to t1) of the contract graph, rounded to two significant digits and written to `data/0-usd-token-list-and-prices/contract-12m/constants.json`:

- m_T: the median of the US-dollar values of the transfers between contracts.
- U: the 99th percentile of the same values (the cap of the C-PR allowance layer).
- m_A: the median of the positive `usd_eff` of the latest allowances between contracts at t1. Every allowance enters, unlimited ones included, since the cap makes each one finite; the earlier revisions took the median of the finite allowances only.
- U_user: the 99th percentile of the US-dollar values of the transfers from user accounts to contracts (the cap of the importance measures of `docs/discovery_protocol.md`).
- b = ln 3 / m for each slope.

## 8. Cohorts and labels

- **Matched cohort (T_obs) and W0 cohort.** The cohorts of `sql/21` (`u12_cohort_tobs`, `u12_cohort_t1`) without the members that section 4 classes as user accounts.
- **Spender cohorts of W0 and W1.** The spenders of `u12_labels_w0` and `u12_labels_w1` that section 4 classes as contracts.
- **Members outside the graph.** A member of any of these cohorts outside the contract graph stays in its cohort and scores 0 under every score and baseline (`docs/analysis_plan.md` section 4). The share of each cohort inside the union graph is reported, and one sensitivity analysis repeats the comparisons of section 9 on the members inside the union graph only; it decides no rule.
- **Labels.** The labels of `u12_labels_w0` and `u12_labels_w1` unchanged (new approval pairs, new transfer senders and the rest of `sql/16`). As a secondary description outside every rule, each label is split into the part from user accounts and the part from contracts.

## 9. Scores and baselines

- The methods of `scripts/graphs.py` with their definitions unchanged, on the contract graph of each freeze: EndorseRank (uniform restarts), EndorseRank with activity restarts, AWP (activity restarts), C-PR at λ = 0.25, 0.5 (the method) and 0.75, its layers walked alone (λ = 1 and 0) and S-PR. Uniform restarts run over the contracts of each graph. The solver is unchanged (d = 0.85, tolerance 10⁻⁸, at most 300 iterations).
- **Baselines.** The in-approve degree and value and the transfer in-degree of `raw_degrees`, counted on the contract graph, and the union in-degree (distinct contracts other than the node with an edge to it in either layer, IB_U of protocol section 5). No baseline counts user accounts.
- **Same-window proxies (rule A).** The three families of `sql/15` computed from the events between contracts.

## 10. Discovery-order test

`docs/discovery_protocol.md`. It is defined after the registered results were known and decides no rule of the plan or the registration.

## 11. Rules and their reporting

- **Rule A** as in the plan, on the contract-graph scores.
- **Rule B.** Two of its registered criteria, F1 and F2, with the registered margin δ = 0.01, and F6 and the spender parts of the two registered sensitivity analyses. Sensitivity 2 adds the cohort members a graph leaves out as isolated nodes to the graph of every walk but S-PR, the coupled one included. Under the registration rule B holds only if each of its criteria holds; this revision applies F1 and F2 only, so it reports "not met" when F1 or F2 fails and "both applied criteria hold" when both hold, and never reports rule B as met.
- F3, F4, F5, P, Q and R1–R3 are not applied (section 2).

## 12. Execution, gates and cost

- **Driver.** `scripts/run_contract12m_pipeline.py` runs the BigQuery and RPC steps in order. Gate A steps: `check`, `subset` (job 24), `ends` (25), `activity` (26, 27, 28), `queue` (29), `typing` (RPC reads, local), `load` (30, a free load job), `contracts` (31), `balances` (32, 33), `anchors` (34), `audit` (43 and the local `balanceOf` check), `structure` (35, then `scripts/run_discovery.py --window t1 --feasibility`). Gate B steps: `constants` (36), `pairs` (37), `rest` (38–41), `checks` (42), `download`.
- **Gate A.** Every step but `check` refuses to run unless the following are committed without local changes:
  - this file, `docs/discovery_protocol.md`, the overlay and the base configuration;
  - the driver, `scripts/run_bq.py`, `scripts/common.py`, `scripts/check_account_code.py`, `scripts/balance_audit.py`, `scripts/download_table.py`, `scripts/crawl.py`, `scripts/run_discovery.py`, `scripts/scoring.py`, `scripts/stats.py` and `scripts/graphs.py`;
  - the SQL files of the gate A steps.
- **Order.** A step also refuses unless the last run of every earlier step passed. The steps check the following:
  - `anchors`: a typing block after 30 September 2026 is recorded;
  - `audit`: the run itself wrote a passing balance check;
  - `structure`: the run itself wrote the pilot report, from files that were committed, and the pilot set no stop flag of protocol section 7 (at least 5,000 capped allowance edges, at least 5% of SCC ∪ OUT with a capped allowance in-edge, and a ρ within the budget).

  Running a step again makes every later step wait for it. The free `check` step is the exception: a step needs only that the last check passed. A step can go on anyway only with an author's decision given to the driver (`--author-decision`). The run manifest records the decision together with what was missing, and section 13 explains it.
- **Gate B.** The gate B steps refuse to run unless, in addition, `docs/discovery_protocol.md` carries its dated section "Protocol fixed" (with the hash of the pilot output and the values its rules set) and the SQL files of the gate B steps are committed. The gate B commit also holds the evaluation code of this variant, named file by file in a dated amendment (section 13): the scripts that compute rule A, F1, F2 and F6, the sensitivities of sections 5, 8 and 11, the baselines of section 9 and the label split of section 8. Each refuses to run in this variant unless it, this file and the overlay are committed without local changes, as `scripts/run_discovery.py` does for the crawls.
- **BigQuery.** The jobs write only tables named `c12_*` and read only the tables and public views named in the driver; `scripts/run_bq.py` checks both. The jobs are labelled `contract12m:` and capped at USD 14 in total; the budget of this variant is USD 60 (overlay; the base configuration keeps USD 50, so the earlier drivers refuse any new job once the ledger passes 50). A job is not run if the larger of its dry run and its estimate would pass a cap, or if the dry run of its first statement exceeds 1.25 times the estimate of that statement; after a job that bills more than 1.5 times its estimate the driver stops. The dry runs of 7 November 2026 bound the parts of the gate A jobs that read public views, `logs_obs` and `logs_w1` at about USD 7.7 (upper bounds, recorded in the driver). The parts that read tables of this revision, and the gate B jobs, are estimated when their step runs, from the rows of those tables. If the estimates would pass a cap, the driver refuses and the author decides. `--force` is not used.
- **Outputs.** `data/1-raw-blockchain-extracts/graph-tables-contract-12m/`, `data/1-raw-blockchain-extracts/contract-types/`, `data/2-processed-tables-and-evaluations/revised-contract-12m/`, `data/3-published-results-for-thesis/revised-contract-12m/`, `data/0-usd-token-list-and-prices/contract-12m/`.

### Tables of the gate A jobs

| Job | Table | Content |
|---|---|---|
| 24 | `c12_logs5` | five-token `Approval` (any value) and non-zero `Transfer` rows of `logs_obs` (2025-04-01 to 2026-06-30) and `logs_w1`: time, block, log index, kind, token, a, b, value (base units), amount (token units), usd (transfers, at the day's price) |
| 25 | `c12_pairs5`, `c12_ends` | distinct ordered pairs (a, b) with counts per kind and first and last time; E |
| 26 | `c12_tx_senders` | addresses of E that sent a transaction before 2026-10-01 |
| 27 | `c12_emitters` | addresses of E that emitted a decoded log in the typing window, with the count of Safe events (cross-check only) |
| 28 | `c12_creations` | addresses of E created by a top-level transaction before 2026-10-01 (cross-check only) |
| 29 | `c12_rpc_queue` | K with the reason each address is in it |
| 30 | `c12_account_types` | the RPC types, loaded from the local parquet |
| 31 | `c12_contracts`, `c12_user_accounts`, `c12_events_cc` | the node set; every typed user account with its source; the rows of `c12_logs5` whose both ends are contracts |
| 32 | `c12_bal_pre` | net flow before 2023-10-01 per (token, owner) of the balance population |
| 33 | `c12_bal` | balances at t1, T_obs and 2026-09-30 |
| 34 | `c12_anchor_blocks` | the last block at or before each anchor |
| 43 | `c12_bal_audit` | the 1,500 pairs of the balance check |
| 35 | `c12_struct_t1` | structure only: distinct contract pairs at t1 per layer (capped allowance, uncapped allowance, transfer), without weights |

## 13. Amendments

An amendment is allowed only before any score, importance, proxy, label or constant of this revision is computed; it is dated and explained in place. Gate B is the last such point. Before gate B, the author may also do the following, with the reasons recorded here:
- extend the smart-account rule of section 4.2 after seeing the code families of the structure report (section 4.3). The extension is decided from the code families alone, without reading the labels or earlier scores of the addresses it moves, and the amendment lists the code hashes it moves;
- decide to go on after a stop (sections 6 and 12, and protocol section 7).

At that point no score, importance, proxy or constant of this revision exists. The W0 and W1 labels do exist: this revision takes them unchanged from the twelve-month revision (section 8), and they and the earlier evaluations on them were known. After gate B, nothing in this file changes.
