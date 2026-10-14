# Exploratory: endorsement-count variants of EndorseRank (14 October 2026)

- Post hoc, like the other folders in `exploratory/`: the variants were chosen after quick point estimates on the same W0 and W1 labels, so these results are not evidence that would survive a registered test. They are not reported in the dissertation.
- On the depth-one allowance graph EndorseRank is close to c (1 + d Σ_u w(u,v) / out(u)) (closed-form check of the revised analysis): every owner casts one vote and splits it over the spenders it approved. The variants keep the sum over owners and change the vote. Each owner counts once per spender.
- Base: the revised analysis (`CONTRACT_REP_VARIANT=usd`), its W0 and W1 spender cohorts (17,050 and 18,152 contracts), labels, matched cohort and paired bootstrap (B = 400, seed from the configuration). Pair ages come from `x_nodecay_pairs_{t1,tobs}` (`../2026-10-14-freeze-date-time-weight/`), so no new BigQuery job was run; σ recomputed from them matches the published `max_sig` to 2e-16.

| Score | Vote of owner u for spender v |
|---|---|
| `endorserank` | published EndorseRank (σ(age) V(usd), split over u's spenders, PageRank) |
| `endorserank_act` | published EndorseRank with AWP's activity restarts |
| `v1_sigV` | Σ_tokens σ(age) V(usd), not split |
| `v2_sig` | σ(a_uv), a_uv = age of u's youngest latest approval to v, k = 0.01, t0 = 180 days as published |
| `v3_hl30` | 0.5^(a_uv / 30), half-life 30 days |
| `v2_sig_cap10`, `v3_hl30_cap10` | the same × min(1, 10 / n_u), n_u = number of spenders u approved, so no owner adds more than 10 in all |
| `deg` | 1 (in-approve degree) |
| `mom30` | 1 if a_uv ≤ 30 days (owners with a standing approval made in the last 30 days) |

## Holdout results (Kendall τ_b [95% CI])

New approval pairs:

| Score | W0 | W1 | minus EndorseRank, W0 | minus EndorseRank, W1 |
|---|---|---|---|---|
| `endorserank` | 0.231 [0.220, 0.242] | 0.234 [0.222, 0.244] | | |
| `endorserank_act` | 0.308 [0.299, 0.319] | 0.295 [0.285, 0.304] | | |
| `deg` | 0.250 [0.237, 0.262] | 0.268 [0.257, 0.279] | | |
| `v1_sigV` | 0.307 [0.297, 0.318] | 0.305 [0.295, 0.315] | +0.077 [+0.069, +0.085] | +0.071 [+0.063, +0.078] |
| `v2_sig` | 0.335 [0.325, 0.344] | 0.318 [0.308, 0.327] | +0.104 [+0.096, +0.113] | +0.084 [+0.076, +0.090] |
| `v3_hl30` | 0.366 [0.358, 0.376] | 0.338 [0.329, 0.348] | +0.136 [+0.126, +0.146] | +0.105 [+0.096, +0.113] |
| `v2_sig_cap10` | 0.334 [0.325, 0.344] | 0.316 [0.306, 0.325] | +0.103 [+0.096, +0.112] | +0.082 [+0.076, +0.088] |
| `v3_hl30_cap10` | 0.368 [0.358, 0.377] | 0.338 [0.328, 0.347] | +0.137 [+0.128, +0.148] | +0.105 [+0.096, +0.112] |
| `mom30` | 0.579 [0.564, 0.596] | 0.606 [0.587, 0.623] | | |

- Every variant also beats in-approve degree (W0 +0.058 to +0.118, W1 +0.038 to +0.071) and `endorserank_act` (`v2_sig` +0.027 and +0.023, `v3_hl30` +0.058 and +0.044), except that `v1_sigV` ties it in W0 (−0.001 [−0.007, +0.005]; W1 +0.011).
- One change at a time (W0, W1): not splitting the vote +0.077, +0.071; dropping V +0.027, +0.012; a 30-day half-life +0.032, +0.021; the cap of 10 −0.001, −0.002 on `v2_sig` and +0.002, −0.000 on `v3_hl30`.
- New transfer senders: `v2_sig` 0.271 and 0.248, `v3_hl30` 0.294 and 0.255, against EndorseRank 0.200 and 0.194 and AWP 0.346 and 0.330. The cap costs `v2_sig` 0.017 (W0) and 0.007 (W1) here.
- Revocations: the 30-day half-life lowers τ (`v3_hl30` 0.250 and 0.230 against EndorseRank 0.337 and 0.312); in-approve degree is highest (0.388, 0.347). Drained owners rise with recency (`v3_hl30` 0.397 and 0.364).

## Beyond 30-day momentum

`mom30` alone outranks every score, and 86% (W0) and 89% (W1) of the spenders have no approval in the last 30 days. Partial τ of score and new approval pairs given `mom30`:

| Score | W0 | W1 | minus EndorseRank, W0 | minus EndorseRank, W1 |
|---|---|---|---|---|
| `endorserank` | 0.124 [0.113, 0.135] | 0.114 [0.104, 0.125] | | |
| `endorserank_act` | 0.125 [0.115, 0.135] | 0.105 [0.095, 0.114] | +0.001 [−0.006, +0.008] | −0.010 [−0.017, −0.003] |
| `v1_sigV` | 0.143 [0.132, 0.154] | 0.133 [0.122, 0.143] | +0.019 [+0.008, +0.028] | +0.018 [+0.009, +0.026] |
| `v2_sig` | 0.152 [0.143, 0.161] | 0.127 [0.118, 0.136] | +0.028 [+0.018, +0.037] | +0.013 [+0.005, +0.021] |
| `v3_hl30` | 0.123 [0.114, 0.131] | 0.096 [0.087, 0.105] | −0.002 [−0.013, +0.009] | −0.019 [−0.029, −0.009] |
| `v2_sig_cap10` | 0.165 [0.156, 0.174] | 0.136 [0.128, 0.145] | +0.041 [+0.032, +0.050] | +0.022 [+0.013, +0.029] |
| `v3_hl30_cap10` | 0.134 [0.126, 0.144] | 0.103 [0.094, 0.112] | +0.010 [−0.001, +0.021] | −0.012 [−0.022, −0.003] |
| `deg` | 0.177 [0.165, 0.189] | 0.189 [0.178, 0.199] | | |

- The 30-day half-life gains raw τ mostly by overlapping with momentum: given `mom30` it adds nothing (W0) or less (W1) than EndorseRank.
- `v2_sig_cap10` is the only variant above EndorseRank in both windows given momentum. In-approve degree stays above every variant given momentum (`v2_sig_cap10` −0.012 [−0.021, −0.003] in W0, −0.053 [−0.061, −0.045] in W1).

## The same variants as PageRank

The count variants drop the three parts that make EndorseRank a PageRank: the split of each owner's vote (row-stochastic transitions), the restarts and the propagation. They can be written as PageRank again by moving the owner's weight into the restarts: edges weighted by the variant's e(u,v) and every node restarting in proportion to its own endorsement mass, t_u = c_u Σ_w e(u,w) (c_u = min(1, 10/n_u) with the cap). An owner without in-edges then has r(u) ∝ t_u, and the mass a spender receives over its in-edges, d Σ_u r(u) P(u,v), equals the count variant up to a constant whenever none of its owners is itself approved (`scripts/run_pagerank_forms.py`, `scripts/run_pagerank_inflow.py`).

- On these depth-one spenders (11,324 of 17,050 in W0, 12,063 of 18,152 in W1) the received mass ranks the spenders exactly as the count variant (τ = 1.000 for every variant in both windows). On the other third PageRank propagates through owners that are themselves approved, and the two rankings differ (τ 0.69–0.88).
- New approval pairs, PageRank form of `v2_sig_cap10` (full score): 0.319 [0.310, 0.328] in W0 and 0.300 [0.290, 0.309] in W1, +0.088 [+0.081, +0.095] and +0.066 [+0.059, +0.072] over EndorseRank and +0.069 and +0.032 over in-approve degree; new senders 0.280 and 0.252. Of `v3_hl30`: 0.358 and 0.331.
- Every PageRank form is 0.008–0.016 below its count form, the same whether the full score or only the received mass is used, so the gap comes from the propagation on the deeper spenders, not from the spenders' own restart mass.
- Given 30-day momentum the PageRank form of `v2_sig_cap10` has partial τ 0.140 [0.131, 0.149] (W0) and 0.110 [0.100, 0.119] (W1), against EndorseRank 0.124 and 0.114 and the count form 0.165 and 0.136.
- The published activity-restart variant is of the same kind (restarts ∝ owner activeness, edges σ V): 0.308 and 0.295, so within PageRank most of the gain over the published EndorseRank comes from weighting the restarts by the owners' endorsements, and making edges and restarts consistent (σ on both, no V, cap 10) adds about 0.01.

## Same window (matched cohort, family means)

| Score | Transfer | Allowance | Sybil stability |
|---|---|---|---|
| `endorserank` | 0.158 | 0.585 | 0.007 |
| `v1_sigV` | 0.148 | 0.518 | 0.025 |
| `v2_sig` | 0.127 | 0.435 | 0.030 |
| `v3_hl30` | 0.082 | 0.309 | 0.021 |
| `v2_sig_cap10` | 0.111 | 0.437 | 0.013 |
| `v3_hl30_cap10` | 0.075 | 0.317 | 0.012 |

The proxies are counts and sums over the whole observation window, so recency-weighted scores agree with them less (allowance family −0.067 to −0.276); the Sybil-stability family moves by at most +0.023.

## Files

| Path | Content |
|---|---|
| `scripts/run_count_variants.py` | W0, W1 and same-window evaluation, contrasts and partial τ |
| `scripts/show_count_variants.py` | prints `results_count_variants.json` |
| `results_count_variants.json` | every τ, contrast, partial τ and family mean, with the definitions |
| `scripts/run_pagerank_forms.py`, `results_pagerank_forms.json` | PageRank forms with endorsement-mass restarts: τ, contrasts, partial τ, agreement with the count forms |
| `scripts/run_pagerank_inflow.py`, `results_pagerank_inflow.json` | the mass each spender receives in those walks, and its agreement with the count forms |
| `data/2-processed-tables-and-evaluations/exploratory-2026-10-14/count_variants_{w0,w1}.parquet` | per-spender scores and labels (Drive) |
| `data/2-processed-tables-and-evaluations/exploratory-2026-10-14/pagerank_forms_{w0,w1}.parquet`, `pagerank_inflow_{w0,w1}.parquet` | per-spender scores of the PageRank forms (Drive) |

## Rerun

Needs the revised graph tables (`python scripts/drive_sync.py pull "*graph-tables-usd/*"`) and `x_nodecay_pairs_{t1,tobs}` (`pull "*exploratory-2026-10-14/*"`):

```powershell
python experiments/exploratory/2026-10-14-endorsement-count-variants/scripts/run_count_variants.py
```

The PageRank forms read `count_variants_{w0,w1}.parquet`, so they run after it:

```powershell
python experiments/exploratory/2026-10-14-endorsement-count-variants/scripts/run_pagerank_forms.py
```

```powershell
python experiments/exploratory/2026-10-14-endorsement-count-variants/scripts/run_pagerank_inflow.py
```
