# Discovery-order test: protocol

- Part of the contract-graph revision (`docs/revision_contract_graph.md`, variant `contract12m`). Written on 7 November 2026, after the registered results, the results of the two earlier revisions and the post hoc checks of `exploratory/` were known, and committed at gate A, before any account-type read, BigQuery job, score, importance or crawl of this revision. The test decides no rule of the analysis plan or the W1 registration, and its results are never called registered.
- When this file was written, the sizes of a t1 contract graph built from the pair tables of the twelve-month revision were known. That graph used the earlier account types, uncapped allowances and only the events around the cohort; it had about 11,300 contracts, 109,000 union pairs and 10,300 allowance pairs, a giant SCC of about 6,300 contracts and an OUT part of about 1,300. The rules and stop thresholds of section 7 were written with these sizes known. No crawl had been run on a graph of the study's data.
- At gate B the section "Protocol fixed" is added with the values that the rules of section 7 set from the structure pilot. Nothing else in this file changes after gate A.
- Model: the crawl-ordering experiment of Cho, Garcia-Molina and Page (1998), "Efficient crawling through URL ordering", Computer Networks and ISDN Systems 30(1–7), 161–172, doi:10.1016/S0169-7552(98)00108-1. A crawler that has read some pages knows only their links and must choose which known page to read next; the experiment compares the orders in which different choices reach the important pages.

## 1. Question

Ordered by C-PR computed on the contracts read so far, does a crawl of the contract graph from a random contract of its giant strongly connected component reach the contracts of the universe (section 2) with the most user-account demand sooner than a breadth-first crawl and sooner than a crawl ordered by the number of contract backlinks?

## 2. Graph, universe and what a visit reveals

| Web crawl | Contract graph at one freeze |
|---|---|
| page | contract (revision section 4) |
| link p → q | allowance edge from owner contract p to spender contract q (balance-capped, revision section 5), or transfer edge from sender contract p to recipient contract q |
| reading a page | reading every approval the contract granted and every transfer it sent in the score window: its out-edges in both layers, with their weights |
| frontier | contracts that a visited contract approved or paid and that are not yet visited |

- **Freezes.** T_obs (primary; the T_obs score window) and t1 (secondary; the W0 score window, which overlaps the other by nine months, so the two are not independent).
- **Graph.** G is the contract graph of the freeze with both layers and their weights (`w_er`, `w_raw` and the largest σ of the allowance pairs; `w_awp`, `w_raw` and the largest σ of the transfer pairs). The union graph holds the distinct pairs (p, q), p ≠ q, that have an edge in either layer. The bow-tie, the edge counts of the universes and the cost axis count these pairs. Self-loops are ignored for the structure, and the walks keep them, as the solver does.
- **Universe.** U is the giant strongly connected component of the union graph (of two equally large, the one that holds the lowest address) together with every contract reachable from it (the giant SCC ∪ OUT). E_U is the set of union pairs with both ends in U. The full graph is G restricted to U: the edges that a crawl has read once it has visited all of U.
- **Reveal mode, primary (`out`).** Visiting a contract reveals its out-edges in both layers with their weights. Every crawl from a seed in the giant SCC visits exactly U.
- **Reveal mode, sensitivity (`both`).**
  - Visiting a contract reveals its in-edges and out-edges, so an edge is revealed at the first visit of either of its ends.
  - The universe is the weakly connected component of the union graph that holds the giant SCC (WCC below), and E_WCC is the set of its union pairs.
  - A frontier contract's row in a walk is normalised by its revealed, partial out-strength.
  - If the rule of section 7 applies, `both` becomes the primary mode and `out` the sensitivity.
- In sections 3 to 6, U and E_U stand for the universe of the mode in use and its union pairs: SCC ∪ OUT in the `out` mode and WCC in the `both` mode. Sections 7 and 8 name the two universes explicitly.

## 3. Seeds

The 20 contracts of the giant SCC with the lowest SHA-256 of `"crawl-seed-v1:"` followed by the lowercase hexadecimal address (with `0x`). No contract is named as a seed: the chain has no counterpart of a home page, a hub seed would help every ordering alike, and a seed chosen by importance would leak the target. The seed is visit 1. Every crawl must end with its universe visited; the runner checks this.

## 4. Orderings

Every ordering but the random one gives a score to every frontier contract and follows one schedule:
- After V visits the ordering is recomputed.
- Then the min(b(V), F) highest-scored contracts of the frontier at the recompute are visited in order, where b(V) = max(1, ⌈ρV⌉) and F is the number of frontier contracts.
- When the frontier holds fewer than b(V) contracts, the whole frontier is visited and the ordering is recomputed after it.
- ⌈·⌉ of a share is computed exactly, with the share read as the decimal fraction it is written as.

The breadth-first order does not depend on ρ, and the random order does not use the schedule. The **discovery index** of a contract is the visit at which it was first discovered; the seed's is 0.

- **BFS.** The frontier is visited in increasing discovery index. Contracts with the same index go in increasing SHA-256 of the seed address followed by the contract address (both lowercase hexadecimal with `0x`), so the order uses no weight.
- **Random.** At every visit, one uniform choice among the contracts on the frontier at that moment, from NumPy's `default_rng` (PCG64), seeded with the SHA-256 digest of `"random-v1:"` followed by the seed address, read as a big-endian integer.
  - The frontier is kept as a list. At a visit, the visited contract is first replaced by the last one of the list, and the contracts the visit discovers are then appended in address order.
  - A draw is `Generator.integers(n)` for a list of n contracts: the position of the contract chosen.
- **Counts on the visited part** (the raw degrees that the walks smooth):
  - IB′_A(f): distinct visited contracts with an allowance edge to f;
  - IB′_T(f): distinct visited contracts other than f with a transfer edge to f;
  - IB′_U(f): distinct visited contracts other than f with an edge to f in either layer.
- **Walks on the seen graph.** The seen graph S holds the visited and frontier contracts and the revealed edges, with the full-graph weights. Each walk is the method of `scripts/graphs.py` run by `scripts/scoring.py` on S, and the frontier score is the walk's value at the frontier contract. Every walk′ has all contracts of S as its nodes, so a contract with no revealed edge in the walk's layers scores what the restarts give it (the S-PR of `scripts/graphs.py` has only the contracts of the transfer layer as nodes):
  - EndorseRank′ (`w_er`, uniform restarts over S);
  - EndorseRank-activity′ (`w_er`, restarts by the activeness of `scoring.activeness` computed on the revealed allowance edges);
  - AWP′ (`w_awp`, restarts by the activeness computed on the revealed transfer edges);
  - C-PR′ at λ = 0.5 (primary), 0.25 and 0.75, and its layers C-PR′(1) and C-PR′(0) (`w_raw`, uniform restarts, rows mixed as in `scoring.coupled_pagerank`);
  - S-PR′ (the revealed transfer layer restarted from C-PR′(1)).
  - A frontier contract has no revealed out-edge in the `out` mode, so its mass returns through the restarts (the solver's dangling rule), and its activeness is 0.
  - A walk′ whose layers hold no revealed edge of positive weight has every contract of S dangling, so it scores its restart vector over S: C-PR′(1) for S-PR′, and 1/|S| on every contract for the walks with uniform restarts, so that the tie rule orders the frontier. That vector is the previous vector of the next recompute.
- **References that are not crawls**, computed on G restricted to U: the ideal order (hot contracts first, by decreasing importance, ties to the lower address); the order by decreasing C-PR (λ = 0.5) of the full graph and the order by decreasing union in-degree of the full graph, each with ties to the lower address. They separate the quality of a score from the loss caused by the partial view.
- **Diagnostic** (outside every comparison of section 6): the normalised in-strength δ′(f) = Σ over visited v with an edge v → f of w(v → f) / out-strength(v), with the C-PR weights mixed by λ = 0.5, the depth-one closed form.
- **Solver.** As in the plan: d = 0.85, tolerance 10⁻⁸, at most 300 iterations. Warm start: each recompute starts from the previous vector on the old nodes and 1/|S| on the new ones, renormalised. The warm start is part of the method: a warm and a cold solve of the same seen graph each stop within the tolerance of their fixed point but not at the same vector (S-PR′ also restarts from a warm-started C-PR′(1)), so contracts whose scores differ by less than the solver's error may be visited in another order than with cold starts.
- **Ties.**
  - The frontier, sorted by decreasing score, is cut into groups. A group starts at the highest score not yet in a group and holds every following score within 10⁻¹² times the frontier maximum of that score.
  - Inside a group, the earlier discovery index goes first, then the lower address.
  - A pick counts as decided by a tie when its group holds more than one contract.

## 5. Importance (the ground truth)

- **User accounts** are transaction senders, externally owned accounts, EIP-7702 accounts and smart accounts (revision section 4). No ordering sees any edge of a user account.
- **Primary, two measures** for each contract c of U, over the score window of the freeze:
  - I_T(c) = Σ over user accounts w of min(US dollars that w transferred to c, U_user), each transfer at the price of its UTC day;
  - I_A(c) = Σ over user accounts w of min(Σ over tokens of `usd_eff`(w, c), U_user), where, for each token, `usd_eff`(w, c) is the latest allowance of w to c in the score window up to the anchor, in (block number, log index) order, counted only when it is positive, capped at w's balance of the token at the anchor and valued at the anchor day's price (revision sections 5 and 6).
  - U_user is the constant of revision section 7. The cap per account bounds a single large account, and an account with no balance adds nothing to I_A.
  - The two measures see different roles: a contract that users authorise (a router, a permit contract) scores high on I_A, a contract that users pay into (a pool, a vault) on I_T. Each has its own verdict, and the answer to the question of section 1 needs both (section 6); this is an all-must-hold rule, not a combined label.
- **Secondary.** N_T(c): the number of user accounts that transferred at least USD 1 in total to c; N_A(c): the number of user accounts whose capped allowance to c is at least USD 1. Cumulative captured importance: the share of Σ_U I held by the contracts visited so far.
- **Importance in the manner of Cho et al.** IB_U (the union in-degree of the full graph) and IR (C-PR at λ = 0.5 on the full graph). They are measured on the edges the orderings read, so agreement with them is an intended-construct check, never a validation. The replication contrast is C-PR′ − IB′_U on the hot set defined by IB_U.
- Future labels are not used as importance: they are the outcome of the out-of-window evaluation, and they exist only for spenders.

## 6. Hot sets, curves, statistic and decision

- **Hot set.** H_q(I) = {c ∈ U : I(c) ≥ θ and I(c) > 0}, where θ is the ⌈q|U|⌉-th largest value of I on U; ties at θ are included. q is the primary share of section 7 (1%, or 5% if |P| < 10,000; the same q in both modes). The secondary share is the other of 1% and 5%: 5% when q is 1%, and 1% when q is 5%.
- **Visit index.** t_h is the visit at which the hot contract h is visited in the crawl from one seed with one ordering (the seed is visit 1).
- **Statistic.** g_x(h) = max(0, 1 − t_h / ⌈x|U|⌉), averaged over the 20 seeds: ḡ_x(h). AUC_x = the mean of ḡ_x(h) over h ∈ H. It equals the normalised area under the curve P_ST up to x|U| visits. x = 10% is primary; 5% and 20% are secondary. Descriptive extras: the visits needed to reach 50% and 90% of H.
- **Curves.** P_ST(K) = |H ∩ V_K| / |H| (Crawl & Stop with Threshold) and P_CS(K) = |V_K ∩ R_K| / K, where V_K is the set of the first K contracts visited and R_K the K most important contracts of U (Crawl & Stop; ties go to the lower address), on a grid of at most 1,000 values of K, as the mean and the minimum and maximum over seeds. References: the ideal curve min(1, K/|H|) and the random curve K/|U|.
- **Uncertainty.** A paired bootstrap over hot contracts: B = 400 resamples with seed 42, one index matrix of `stats.resample_matrix` shared by every ordering and contrast. A contrast D = AUC(o₁) − AUC(o₂) reports its point value, the 95% percentile interval of its resampled values and the share of resamples above 0. Sensitivities: the spread across seeds and a bootstrap over seeds.
- **Decision**, fixed here before any number of this revision exists. It is read at the T_obs freeze in the primary mode. On H_q(I_T) and on H_q(I_A), with AUC_10%: D1 = C-PR′ − BFS and D2 = C-PR′ − IB′_U. For each importance:
  - V1, both intervals above 0: "Ordered by C-PR on the contracts read so far, a crawl from a random contract of the giant strongly connected component reached the contracts of the universe with the most [user-account inflow | user-authorised value] sooner than a breadth-first crawl and than a crawl ordered by the number of contract backlinks."
  - V2, the D1 interval above 0 and the D2 interval not above 0: "… sooner than a breadth-first crawl, but not sooner than a crawl ordered by the number of contract backlinks."
  - V3, the D1 interval not above 0: "… did not reach the contracts of the universe with the most [user-account inflow | user-authorised value] sooner than a breadth-first crawl."
  - An interval below 0 adds a sentence naming the ordering that was faster.
  - The verdicts of the two importances are stated once when they and their added sentences agree, and separately otherwise.
  - The answer to the question of section 1 is the weaker of the two verdicts (V2 is weaker than V1, and V3 than V2), so it is yes only when both are V1. When the two are stated separately, the answer follows them: "Over both importances, the weaker verdict: " followed by that verdict's sentence for "user-account demand".
  - With |H| < 30 for an importance, its results are descriptive and carry no verdict, and the question of section 1 has no answer; the verdict of the other importance is stated for that importance only.
  - At t1 and in the other mode, the same contrasts are reported in the fixed order below without a verdict: for each importance, the contrasts whose interval lies above 0 and those whose interval lies below 0 are listed.
- **Reported in this fixed order, outside the decision:**
  1. each walk′ against the count it smooths: EndorseRank′, EndorseRank-activity′ and C-PR′(1) against IB′_A; AWP′ and C-PR′(0) against IB′_T; C-PR′ against IB′_A and against IB′_T;
  2. contrasts among the walks: C-PR′ − C-PR′(0) and C-PR′ − AWP′ (does the allowance layer help discovery?), C-PR′ − C-PR′(1), C-PR′ − EndorseRank′, S-PR′ − C-PR′(0);
  3. λ = 0.25 and 0.75;
  4. the hot sets of Cho et al. (IB_U, IR) and the replication contrast;
  5. sensitivities: x = 5% and 20%, the secondary share of q, P_CS, no hubs (the max(10, ⌈0.001|U|⌉) contracts with the highest IB_U, ties to the lower address, removed from H but kept in the graph), the importances N_T and N_A, cumulative captured importance, the other reveal mode, ρ/4 on the first 5 seeds, the seed bootstrap and a cost axis (the share of E_U read); P_CS and the cumulative captured importance are reported as curves only;
  6. the t1 freeze.
- **Diagnostics.** The share of picks decided by a tie; wasted visits (the share of the first 1% and 10% of visits that went to contracts with I_T = I_A = 0); the visit index of each hub; coverage, over the rows of `importance_{tag}` (section 8):
  - the share of each of I_T and I_A held by U, and by each part: the giant SCC, IN, OUT and the other parts of the bow-tie, the contracts of G with no union pair, and the contracts outside G. The parts sum to 1; in the `both` mode U also holds parts other than the giant SCC and OUT;
  - the share of the top 1% of those rows by each importance that lies in U. The top 1% are the ⌈n/100⌉ largest of the n rows; rows tied at the cut share the places left equally;
  - `inflow_untyped` (section 8), 0 when there is no such transfer.

## 7. Structure pilot and the rules it applies (t1 only, before any score)

- `scripts/run_discovery.py --window t1 --feasibility` reads the structure table of job 35 (distinct contract pairs per layer at t1, without weights), the account types and the twelve-month cohort lists. It reports:
  - nodes and edges per layer (capped allowances, uncapped allowances, transfers) and of the union;
  - the bow-tie (giant SCC, IN, OUT, other) of the union graph;
  - |SCC ∪ OUT|, its union pairs, |WCC| and its union pairs;
  - the share of SCC ∪ OUT with a capped allowance in-edge;
  - the coverage of the W0 cohort and the W0 spender cohort in each layer and in the union;
  - the account types: counts by class, wallet kind and proxy kind, over the queue and over the nodes of the union graph;
  - among the contracts that are nodes of the union graph, the 50 largest groups by code hash, and every group whose `entryPoint()` answers a canonical EntryPoint although its class is contract. Each group is reported with its size, code size, proxy kind, most frequent implementation and EntryPoint answers. These are the code families of revision section 13;
  - the projected run time below.
- It computes no weight, importance, crawl, curve, label, constant or ranking by degree, and it calls no crawl, curve or AUC function.
- **Rules**, applied to the t1 pilot and used at both freezes, in this order:
  - **Mode:** if |SCC ∪ OUT| < 0.5 × |WCC|, the `both` mode is primary and the `out` mode the sensitivity; otherwise `out` is primary. P denotes the primary universe and E_P its union pairs.
  - **ρ** is the smallest of {0.01, 0.02, 0.05} whose projected time T(ρ) is at most 12 hours, with
    T(ρ) = 12 ns × 30 × [N_out · R(ρ, |SCC ∪ OUT|) · |E_U| + N_both · R(ρ, |WCC|) · |E_WCC| + N_4 · R(ρ/4, |P|) · |E_P|] / W.
    - R(ρ, n) is the number of recomputes of the schedule of section 4 for a universe of n contracts whose frontier never runs short, counted exactly.
    - W = 16 workers.
    - N_out = N_both = 10 × 20 × 2 = 400 walk crawls: ten walk solves per recompute set (the nine walks, with S-PR′ counted twice), twenty seeds and two freezes.
    - N_4 = 10 × 5 × 2 = 100, the ρ/4 sensitivity in the primary mode.
    - The t1 sizes stand for both freezes.
    - T(ρ) is a projection used only for this choice; the run times are reported.
    - If no value qualifies, the run stops and the author decides.
  - **q:** the primary share is 1% if P holds at least 10,000 contracts and 5% otherwise. The same q is used in both modes.
- **Stop thresholds.** The run stops before gate B, and the author decides whether to go on, if the capped allowance edges between contracts at t1 are fewer than 5,000 or if fewer than 5% of the contracts of SCC ∪ OUT have a capped allowance in-edge. A decision to go on is recorded in "Protocol fixed" with its reasons.
- Nothing else is set from the pilot.

## 8. Runs and outputs

- After gate B: `python scripts/run_discovery.py --window tobs`, then `--window t1`, each in the primary mode and the sensitivity mode (`--mode out|both`), with `--workers N`; the results do not depend on N.
- **Committed files.** The runner refuses any run other than `--feasibility` unless the following are committed without local changes, and it records their SHA-256 and HEAD in its output:
  - this file with its section "Protocol fixed", `docs/revision_contract_graph.md` and the overlay;
  - the base configuration, whose solver and bootstrap settings the runs use;
  - `scripts/crawl.py`, `scripts/run_discovery.py`, `scripts/scoring.py`, `scripts/stats.py`, `scripts/graphs.py` and `scripts/common.py`.
- **Further refusals.** Unless "Protocol fixed" records an author's decision with its reasons, the runner also refuses:
  - a pilot output whose hash differs from the pinned one;
  - a pilot that ran on files that were not committed, or with discovery settings other than those of the overlay;
  - a pilot whose recorded rule inputs are not its own counts (its sizes, its capped allowance edges and its share of SCC ∪ OUT with a capped allowance in-edge), or whose recorded rule values differ from those that the rules of section 7, applied by the committed code to those counts, give;
  - a t1 graph whose |SCC ∪ OUT|, |E_U|, |WCC| or |E_WCC| differ from those of the pilot. The pilot and the gate B pairs share their definitions, so the sizes must agree. The runner checks the t1 sizes before any crawl, at either freeze.
- The values of ρ, q and the mode in "Protocol fixed" must be those that the rules of section 7, applied by the committed code with the overlay's settings, set from the pilot's sizes, even with an author's decision; only a ρ that the author chose because no value qualified differs.
- **Inputs** (gate B outputs, in `data/1-raw-blockchain-extracts/graph-tables-contract-12m/`):
  - `nodes`, one table for both freezes, which numbers in increasing address order every contract with a pair at either freeze and any further contract the gate B tables carry, and `allow_pairs_{tag}` and `transfer_pairs_{tag}` with those node ids. At each freeze G has every contract of `nodes` as a node, so a contract without a pair at that freeze is among "the contracts of G with no union pair" of section 6;
  - `importance_{tag}`: every typed contract with a positive I_T or I_A, with its node id when it is in `nodes` and −1 otherwise (I_T, I_A, N_T, N_A);
  - `inflow_untyped_{tag}`: the US dollars that user accounts transferred in the score window to the addresses of E that were not typed (outside the RPC queue of revision section 4.3 and not transaction senders). These addresses are never graph nodes, so this sum bounds the user-account inflow that the coverage cannot place.
- Outputs: `data/2-processed-tables-and-evaluations/revised-contract-12m/discovery/feasibility_t1.json` (pilot), `discovery_{tobs,t1}_{mode}.json` (sizes, coverage, hot-set sizes, AUC for every ordering, importance, q and x with per-seed values and intervals, curves, the decision contrasts and the verdict, the fixed-order contrasts and sensitivities, diagnostics, run times with the recomputes, solves and iterations, and the numbers of nodes and union pairs of G and of U), and parquet parts with the visit index of every hot contract for every seed and ordering (`discovery_{tag}_{mode}_hot_visits`) and with the membership of the hot sets (`discovery_{tag}_{mode}_hot_sets`).

## Protocol fixed

(Added at gate B: the date, the path and SHA-256 of `feasibility_t1.json`, |U|, |E_U|, |WCC|, |E_WCC|, the values of ρ, q and the primary mode set by section 7, and an author's decision with its reasons when the run goes on after a stop of section 7 or a refusal of section 8.)
