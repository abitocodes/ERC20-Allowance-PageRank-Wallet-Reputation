# 발표 자료 개정 계획: 계약 그래프 분석(contract12m)

2026-11-11 작성. 발표 자료(`index.html`, `index.en.html`, `js/sections*/`, `STORYBOARD.md`)를 영어 학위논문(원고 서브모듈 브랜치 `contract-graph`, 198쪽)의 주 분석에 맞추는 계획이에요. 1단계(데이터 다시 만들기)는 끝났고, 이 문서는 2단계(슬라이드 다시 쓰기)를 여러 작업자가 나눠 하도록 정리한 것이에요.

근거 문서(작업자가 먼저 읽을 것):

- 주장과 숫자: `ERC20-private/dissertation/notes/_claims.md`(C1–C6, 데이터 사실, 모든 글이 지킬 점), `_writing-brief.md`의 "Aim and framing", `_revision-context.md`의 "What changed in the analysis", "Status words", "Words", "Notation of the discovery-order test".
- 숫자의 원천: `experiments/data/3-published-results-for-thesis/revised-contract-12m/results_digest.md`(이하 `C§n`)와 그 JSON. 등록 분석은 `experiments/data/3-published-results-for-thesis/results_digest.md`(`G§n`).
- 한국어 용어: `dissertation/overleaf-github-ko/TRANSLATION-GUIDE.md` §5, §5b, §5c(계약 그래프와 발견 순서 검증의 말, 정해 둔 문장 넷), §5d(모든 한국어 글의 규칙).

---

## 0. 1단계에서 한 일

### 0.1 `tools/build_data.py`

- 읽는 곳을 `revised-usd-12m/`에서 `revised-contract-12m/`으로 바꿨어요(발표 `published` 요약 + `2-processed-tables-and-evaluations/revised-contract-12m/`의 계약별 parquet). 지갑이 든 분석(`revised-usd-12m/`, `revised-usd/`)은 읽지 않아요. 필요한 파일이 하나라도 없으면 다른 분석으로 넘어가지 않고 멈춰요(`Ctx`가 목록을 확인). 지금은 빠진 입력이 없어요.
- 토큰 목록·선정 입력·상수는 발표 폴더의 사본(`revised-contract-12m/usd/`)에서, 하루 가격은 `0-usd-token-list-and-prices/daily_prices_usd.csv`에서 읽어요.
- 데이터 키에서 주 분석은 여전히 `revised`라는 이름이에요(슬라이드 코드가 그 이름을 써요). 뜻은 계약 그래프 분석이에요.
- 검증: 두 digest와 parquet에서 다시 센 τ로 72개 값을 견줘요. 72/72가 맞았어요. 데이터 파일에 `trader`, `liquidat`, `gmx`, `neutral_w`라는 말과 주소(0x + 40자리)가 없는지도 확인해요.

새로 생긴 키(2단계에서 쓸 것):

| 파일 · 키 | 내용 | 출처 |
|---|---|---|
| `data/discovery.js` (새 파일) `discovery.runs.{tobs_both, tobs_out, t1_both, t1_out}` | 실행마다 `window`, `mode`, `decides`(tobs_both만 true), `sizes.graph`(SCC 265,804 · IN · OUT · other · WCC …), `sizes.universe`(|𝒰| 1,169,044, E_U 2,378,418), `seeds`(20), `hot_sets`(H_q(I_T) 13,141, H_q(I_A) 11,662, …), `protocol`(ρ 1/50, q 1/100, x, 부트스트랩) | `C§11` |
| `discovery.runs.*.auc[hot_set][ordering]['x=0.1'|'x=0.05'|'x=0.2']` | `[AUC, lo95, hi95, 가장 낮은 시드, 가장 높은 시드, 시드 SD, H의 50%까지 평균 방문 수, 90%까지]`. ordering: `bfs, random, ib_a, ib_t, ib_u, endorserank, endorserank_activity, awp, cpr_l50, cpr_l25, cpr_l75, cpr_l100, cpr_l0, spr, delta, ref_cpr, ref_ib_u, ref_ideal`; `random_curve`, `ideal_curve`는 숫자 하나 | `C§11 auc.*` |
| `discovery.runs.*.decision.{i_t, i_a}.{D1, D2}` | `{d: [점, lo, hi], p: 0보다 큰 재표본 몫, a, b, hot_set, x, n}`, `verdict`(tobs_both만 'V2'), `extra`; `decision.statements` | `C§11 decision.*` |
| `discovery.decision` | 판정 실행(tobs_both)의 `i_t`, `i_a`와 `statement`(판정 V2 문장, 다이제스트 그대로) | `decision.statements[0]` |
| `discovery.runs.*.fixed_order` | `1_walk_vs_count`(걷기′ − 그 센 수′, 14개), `2_walk_contrasts`(걷기끼리, 10개), `3_lambda`, `4_cho`(IB_U·IR 뜨거운 집합, 복제 대비), `5_sensitivities`(x, q2, 허브 없이, N_T·N_A, 시드 부트스트랩, ρ/4) | `C§11 fixed_order.*` |
| `discovery.runs.*.diagnostics` | `ties`(순서 규칙마다 동점으로 정한 몫), `wasted_visits`(첫 1%·10% 방문의 헛 방문 몫), `hubs`(개수만), `coverage`(I_T·I_A 합, 𝒰·bow-tie 부분별 몫, 상위 1%) | `C§11 diagnostics.*` |
| `discovery.runs.tobs_*.curves` | 얇게 한 곡선: `grid`, `share_of_U`, `P_ST[i_t|i_a][ordering].mean`(+ 주요 순서 규칙 `bfs, random, ib_u, cpr_l50, awp`는 `min`, `max`), `P_ST.*.random`·`ideal`(기준 곡선), `P_CS`, `captured`, `cost` | 다이제스트 그림 `discovery-curves`의 원천(`derived: true`) |
| `discovery.pilot` | t₁ 구조 파일럿: `capped_allowance_in_edge_share.U` 0.0054, `bow_tie`, `sizes`, `stop_flags`, `primary_universe`, `coverage` | `discovery/feasibility_t1.json` |
| `discovery.orderings`, `discovery.meta.importances` | 순서 규칙과 중요도의 영어·한국어 이름 | 이 스크립트 |
| `scale.revised.events` | 다섯 토큰 행 1,240,275,042 · 주소 25,537,280 · 트랜잭션 보낸 주소 17,477,779 · 양끝이 계약인 행 603,475,784 · 사용자 계정 → 계약 행 152,257,072 … | `C§1 events.*` |
| `scale.revised.account_types` | 사용자 계정 21,877,279 · 계약 1,829,719 · 읽은 주소 6,230,270 · 블록 513,216,506 · `typed`, `after_extension`, `wallet_kind_*`(Safe 46,204, ERC-4337 279,813) | `C§1 account_types.*` |
| `scale.revised.nodes`, `pairs`, `union_graph_tobs`, `union_graph_t1` | 계약 그래프의 점 1,403,959, 층마다 쌍 수(상한 씌운 허락 115,006 · 상한 없는 302,559 · 송금 2,580,709; 가장 큰 주인 98,073쌍), 합집합 그래프 | `C§1` |
| `scale.revised.amounts` (+ `amounts_t1`, `amounts_per_token`) | 잔액 상한: 계약 사이 양수 마지막 허락 339,282 · 무제한 223,892(66.0%) · 0으로 잘림 222,559(65.6%) · 상한 뒤 양수 116,723 · … | `C§12 allowances.*` |
| `scale.revised.balance_check`, `importance`, `constants`, `chainlink_check` | 잔액 점검 1,493/1,500 · I_T 166.1억 달러, I_A 3.095억 달러 · 상수 · 체인링크 점검 | `C§12` |
| `scale.revised.cohort_coverage` | 매칭 코호트·W0 코호트·W0/W1 스펜더가 계약 그래프 어디에 있는지(합집합 그래프 4,270 = 66.3% 등) | `C§3`, `C§6`, `C§7` |
| `scale.revised.members`, `by_class`, `user_accounts_by_source`, `listed` | 코호트 목록에서 사용자 계정을 뺀 수(6,483 → 6,443, 40개 스마트 계정) | `cohort/*.json` |
| `scale.revised.label_split` | 라벨을 센 계정의 종류(W0 새 허락 쌍 748,258, 사용자 계정 90.4% …) | `C§6`, `C§7` |
| `scale.revised.w0/w1.in_union_graph` | 합집합 그래프 안의 스펜더 수와 몫 | `C§6`, `C§7` |
| `results.lambda_sweep.revised.degree_baselines.{in_approve_value, in_degree_union}` | 새 기준선(받은 허락 금액, 합집합 입차수)의 W0·W1 τ | `C§6`, `C§7` |
| `results.revised.w0/w1.{baselines, baseline_contrasts, in_union_graph, label_split, cohort_coverage}`, `results.revised.robustness.uncapped_allowances` | 그대로 압축해 실음 | `C§6`, `C§7`, `C§9` |
| `results.verdicts.revised.rule_b` | `applied_criteria` ['F1','F2'], `F.{F1, F2, F6a, F6b}`, `F6`, `f1_f2_hold` false, `rule_b_not_met` true, `reading` 'not met', `decision` false(= "규칙 B 충족" 아님; 둘 다 서면 null), `note`/`note_ko`(규칙 B의 정해 둔 문장) | `C§7 rule_b.*` |
| `results.verdicts.revised.rule_b_sensitivity_awp`, `rule_b_sensitivity_isolated` | 두 등록 민감도 분석의 F1·F2와 읽기 | `C§7` |
| `sybil.revised.json.contract_farm`, `balance_threshold`, `cohort` | 농장 주소는 계약: 배포 가스, 배포 수(꼭대기까지 375), V(1달러) = 1.000; 잔액 문턱 θ = 1·10·100달러 | `C§8` |
| `params.cap.U_user_usd`(31,000), `p99_capped_allowance_usd_raw`, `p99_user_transfer_usd_raw`, `balance_cap`, `params.value.m_A_note`, `window` | 계약 그래프 위의 상수 | `C§12 constants.*` |
| `contracts.in_union`, `contracts.flag_counts.in_union_graph` | 계약마다 합집합 그래프 안(1)/밖(0) | `same-window/cohort_scores` |
| `prices.tokens[].days_main_window`, `main_window_published`, `prices.index.main_window` | 주 분석이 가격을 쓰는 548일 | `C§12 price_days` |
| `timeline.periods[contract_events]`, `anchors.contract_events`, `anchors.blocks`, `anchors.account_types_block`, `bigquery.analysis_jobs`(26), `analysis_jobs_usd`(12.63), `budget_usd`(60), `ledger`(작업 수와 합계만) | 계약 그래프 분석의 사건 기간(2025-04-01 – 2026-09-30) | `C§12 timing.*`(정의 시각은 싣지 않음) |

없앤 키(슬라이드가 이 키를 읽으면 지금은 코드 안의 옛 숫자가 대신 보여요):

- `data/traders.js` 전부; `results.neutral`, `results.trader_labels`, `results.neutral_pairs`, `results.verdicts.*.{R1, R2, R3, P_w0, P_w1, Q_w0, Q_w1, rule_b_sensitivity_awp(옛 불리언)}`, `rule_b.F.{F3, F4, F5}`, 등록 분석의 `rule_b.decision`, `lambda_sweep.*.w1_traders_liquidation_free_rate`, 요약 JSON 안의 `traders*`, `trader_taus`, `neutral_*`, `*_liq`, `provenance`.
- `scale.gmx`, `scale.revised.{rows, left_out_of_registered, registered_cohort, candidates, by_code_kind}`, `scale.revised.amounts.{owners, owners_with_unlimited, owners_with_both_kinds, finite_allowance_usd_percentiles_tobs, transfers_obs, transfer_usd_percentiles_obs}`, `scale.tokens.{rows_in_window_tobs, *_share_of_rows_tobs}`, 토큰의 주소.
- `timeline.monthly_counts.revised`(계약 그래프 분석은 달마다 건수를 발표하지 않아요; `registered`만 남음), `timeline.gmx_contract_traders_by_quarter`, `timeline.ledger_jobs`(작업 이름에 GMX가 있고, 시각이 정의 시점을 알려 줘요).
- `params.cap.p99_finite_allowance_usd_raw`, `params.cohort.gmx_min_closes`, `params.stats.B_neutral`.

뜻을 이어 받은 키: `scale.revised.amounts.{latest_allowances_tobs, unlimited_allowances, unlimited_share, allowances_at_or_above_cap(_share)}`(이제 계약 사이의 허락), `params.value.{m_T, m_A, b_T, b_A, m_*_raw}`, `params.cap.{U_usd, p99_transfer_usd_raw}`, `scale.revised.{cohort, graph_tobs, graph_t1, iterations_*, w0, w1}`, `results.revised.*`, `sybil.revised.*`, `benchmark.revised.*`, `contracts.*`, `holdout.*`(W0·W1 bins에 `in_approve_value`, `in_degree_union` 더함).

meta의 말(`NOTES`): `scope`는 "모든 그래프의 점은 계약, 사용자 계정은 어떤 그래프에도 없고 중요도와 라벨에만", `revised`는 정해 둔 정의 문장 전부(달러·다섯 토큰, 12개월 점수, 스마트 계정이 아닌 계약의 그래프와 체인 전체의 화살표, 잔액 상한과 잔액 재구성, 계약 그래프 위의 상수, 발견 순서 검증; 등록 결과를 안 뒤 정함; 등록된 결과라고 부르지 않음), `rule_b`(F1·F2만), `discovery`(규칙을 정하지 않음, 판정은 T_obs both만), `labels`. 트레이더 말과 P/Q/R1–R3은 없어요.

### 0.2 덱이 계속 열리게 한 최소 수정 (화면 글은 고치지 않음)

| 파일 | 고친 것 | 이유 |
|---|---|---|
| `index.html`, `index.en.html` | `<script src="data/traders.js">` → `<script src="data/discovery.js">` | traders.js가 없어짐. 이것만으로 s09-06은 오류 없이 열려요(코드가 `DD.traders`가 없을 때를 이미 견딤) |
| `js/sections/s03-data.js`, `js/sections-en/s03-data.js` | `monthly_counts.revised`가 없으면 `monA`, `monT`를 `[0, 0]`으로(주석 붙임) | 빈 SVG 길에서 `getPointAtLength`가 예외를 던짐(s03-02) |
| `js/sections/s10-sybil-speed.js`, `js/sections-en/s10-sybil-speed.js` | `lg(v)`가 0 이하에서 −9를 돌려주게(주석 붙임) | 계약 그래프에서 코호트 중앙값의 엔도스랭크가 0이라 `log(0) = −∞` → SVG 좌표와 three.js 위치가 NaN(s10-02, s10-03) |

확인: 두 판 모두 60장, 모든 클릭 단계를 돌려 페이지 오류 0, 콘솔 오류 0, 실패한 요청 0, `__deckErrors` 0. 경고 둘이 남아요: (1) s10이 스스로 하는 digest 글자 대조 "`[s10] DECK_DATA differs from the digest strings`"(s10을 다시 쓰면 사라져요), (2) s08-03의 "GSAP target not found"(빈 월별 띠). `dist/`의 한 파일 판과 인쇄판 PDF는 다시 만들지 않았어요(옛 데이터 그대로).

---

## 1. 모든 묶음이 지킬 말 (요약)

1. 그래프의 점은 모두 계약이에요. 사용자 계정(EOA, EIP-7702 계정, 스마트 계정: Safe, ERC-4337 계정)은 어떤 그래프에도 없고, 점수·기준선에 들어가지 않아요. 나오는 곳은 발견 순서 검증의 중요도(I_T, I_A)와 기간 밖 라벨뿐이에요. 등록 분석을 설명하는 곳 밖에서는 사용자 계정을 점·주인·보낸 쪽으로 그리지 않아요.
2. 주 분석의 결과를 "등록된 결과"라고 부르지 않아요. 수정 분석의 정의를 말할 때는 정해 둔 문장 전부를 들고(TRANSLATION-GUIDE §5c 첫 문장), 시각을 붙이지 않고, 바꾼 이력("원래는", "줄였다", "대신", "더 이상")을 말하지 않아요.
3. 발견 순서 검증은 "등록 분석의 결과를 안 뒤에 정했고, 계획과 등록 문서의 어떤 규칙도 정하지 않아요". 미리 정했다·등록했다고 쓰지 않고 프로토콜의 시각도 쓰지 않아요. 판정 V2 문장은 TRANSLATION-GUIDE §5c(영문판은 digest `decision.statements[0]`)를 그대로 옮겨요. RQ2의 답은 "아니요"이고, "C-PR′이 너비 우선보다 빨랐다"는 말은 언제나 뒷부분(계약 역링크 수보다 빠르지 않았다)과 함께 써요.
4. 규칙 A는 계약 그래프 점수에 적용한 재분석이고 충족하지 못했어요. 규칙 B는 "등록된 기준 가운데 두 가지, F1과 F2를 적용해요. 등록 문서에 따르면 규칙 B는 자기 기준이 하나하나 모두 설 때만 충족돼요." 결과는 "규칙 B는 충족하지 못했어요"(F1 섬, F2 못 섬). 그 밖의 판정을 말하지 않아요.
5. GMX, 트레이더, 청산, F3–F5, P, Q, R1–R3, "두 화살표 어디에도 없는 결과"를 어디에도 쓰지 않고, 무엇을 지웠다·뺐다고도 쓰지 않아요.
6. C-PR이 지는 곳, 센 수가 이기는 곳을 모두 그대로 말해요(발견 순서 검증 포함).
7. 신용은 시험하지 않은, 바라는 나중의 쓰임으로만 말해요(s12 정리에서 한 번).
8. 화면 숫자는 `data/*.js`에서 읽어요. 지금 코드에 박힌 옛 digest 글자(s06-04의 λ 표, s07-04·s07-05의 구간, s10의 대조 문자열, 각 `get(…, 옛 값)`의 대체 값)는 새 값으로 바꾸거나 데이터에서 읽게 고쳐요. 대체 값이 화면에 보이면 안 돼요.
9. 상태 태그: 발견 순서 검증의 숫자에 붙일 태그가 없어요. 묶음 0이 `deck.js`의 태그 표에 하나를 더해요(제안: `발견 순서 검증 · 규칙 아님` / `Discovery-order test · decides no rule`, 아이콘은 나침반을 다시 쓰지 말고 새로). `탐색적`(옛 W0 트레이더용)은 쓰는 곳이 없어지면 표에서 빼요.
10. 주소와 개별 계약 이름을 보이지 않아요("가장 큰 주인 계약 하나가 98,073쌍"처럼 수로만).

---

## 2. 새 구성

발견 순서 검증은 논문의 첫 평가라서, 결과보다 앞에 섹션 하나로 넣어요(`s08-discovery`). 섹션 번호가 화면의 유령 숫자, 눈썹 줄, 진행 막대 칸을 정하므로(`deck.js`의 `/^s(\d+)/`), 뒤 섹션의 번호를 하나씩 미뤄요.

| # | 섹션 id (새) | 옛 id | 제목 | 장 | 시간(목표) |
|---|---|---|---|---|---|
| 01 | `s01-opening` | 같음 | 여는 질문 | 3 | 2:00 |
| 02 | `s02-world` | 같음 | 허락과 송금 | 5 | 3:00 |
| 03 | `s03-data` | 같음 | 데이터의 세계 | 6 | 3:50 |
| 04 | `s04-pagerank` | 같음 | 페이지랭크 유도 | 7 | 5:20 (s04-04 줄임) |
| 05 | `s05-weights` | 같음 | 화살표의 무게 | 6 | 4:30 (s05-04 줄임, s05-06에 잔액 상한) |
| 06 | `s06-methods` | 같음 | 네 가지 점수 | 5 | 4:15 |
| 07 | `s07-measure` | 같음 | 맞았는지 재는 법 | 5 | 3:40 (s07-03 줄임) |
| 08 | `s08-discovery` | 새 섹션 | 먼저 찾을까: 발견 순서 검증 | 6 | 4:30 |
| 09 | `s09-results` | `s08-results` | 기간 밖 예측 | 6 (8에서) | 4:35 |
| 10 | `s10-rules` | `s09-rules` | 미리 정한 규칙 | 5 (6에서) | 3:55 |
| 11 | `s11-sybil-speed` | `s10-sybil-speed` | 공격 비용과 속도 | 4 | 3:10 |
| 12 | `s12-closing` | `s11-closing` | 정리 | 5 | 2:45 |
| | | | **합계** | **63** | **약 45분 30초** |

- 지금은 60장, 44분 40초(장마다 `time`의 합)예요. 새 섹션 6장(4:30)의 시간은 옛 s09-06(R1–R3, 55초)을 지우고, 옛 s08-06(다시 출발 변형, 45초)을 옛 s08-05에 합치고, 옛 s08-07·s08-08(닫힌 식 두 장, 105초)을 한 장(55초)으로 합치고, 옛 s09-05(등록 분석과 수정 분석)를 30초로 줄이고, s04-04·s05-04·s07-03을 15초씩 줄여서 대요(합 약 4분 10초). C-PR과 합집합 입차수의 비교는 새 장을 만들지 않고 s10-04(규칙 밖에서 C-PR을 다른 점수와)에 줄로 넣어요.
- 줄일 때 건너뛸 장(STORYBOARD §1.10에 적을 것): s05-01, s06-05, s07-03의 스피어먼, s08-06의 진단 판, s10-05(등록 분석과 같은 판정).
- 번호를 미루기 싫으면 대안: 11개 섹션을 그대로 두고 발견 순서 검증을 `s08-results`의 앞 여섯 장으로 넣는 것이에요(그래도 s08 안의 장 id를 모두 다시 매겨야 하고, 한 섹션이 12장이 돼요). 권하지 않아요.

---

## 3. 장마다 판정

판정: **유지**(그대로) · **고침**(글·숫자만) · **교체**(그림이나 줄거리를 바꿈) · **새 장** · **지움/합침**. "키"는 지금 읽는 키(→ 새로 읽을 키).

### s01-opening (묶음 1)

| id | 제목 | 판정 | 키 | 할 일 |
|---|---|---|---|---|
| s01-01 | 서명하기 전의 질문 → 제목 | 고침 | `meta.*` | 지갑 창은 그대로. 둘째 문장을 목표에 맞춰("수많은 계약 가운데 사람들이 기대는 계약을 어떻게 찾을까요?"). 날짜는 원고 표지를 확인해 맞춤(`meta.date`, 지금 "2026년 10월") |
| s01-02 | 연구 질문 | 교체 | 없음 | 주 질문: "허락·송금 화살표를 한 걸음으로 걷는 C-PR이 사용자가 기대는 계약을 더 빨리 찾고, 나중 쓰임을 더 잘 맞힐까?" RQ1–RQ5를 `_claims.md` 표대로(RQ1 = 두 걷기의 순서·자기 지표·비용, RQ2 = 발견 순서 검증, RQ3 = 기간 밖 예측과 센 수, RQ4 = 규칙 A, RQ5 = 규칙 B의 F1·F2). 칩의 섹션 번호를 새 번호로(RQ2 → 08, RQ3 → 09, RQ4·RQ5 → 10, 비용 → 11). 아래 작은 글: H1–H3은 RQ1에 속하고 대체로 저절로 맞음, 시험은 RQ2–RQ5 |
| s01-03 | 오늘의 길 | 고침 | 없음 | 정거장 12개(새 섹션 이름). 진행 막대 칸도 12개(엔진이 섹션 수로 만듦) |

### s02-world (묶음 1)

| id | 제목 | 판정 | 키 | 할 일 |
|---|---|---|---|---|
| s02-01 | 디파이를 한 장으로 | 고침 | 없음 | 계약 둘레의 EOA 점선 원은 디파이 설명으로 둘 수 있지만, "이 연구의 그래프"처럼 보이지 않게. 한 줄 더: "계약은 다른 계약을 불러 써요"(조합) |
| s02-02 | 송금과 허락은 다른 일이에요 | 고침 | 없음 | 예의 주인을 계약으로도(금고 계약이 라우터에 허락). `approve`/`permit` 그대로 |
| s02-03 | 허락은 믿음처럼 보여요 — 하지만 | 고침 | `scale.revised.amounts.{unlimited_share, unlimited_allowances, latest_allowances_tobs}` → 같은 키(이제 계약 사이 허락) + `capped_to_zero_share` | "무제한 허락이 흔해요: 계약 사이 마지막 허락의 66.0%(223,892 / 339,282, T_obs)". 넷째 주의를 더함: "잔고 없는 허락도 많아요 → 65.6%는 주인 잔액이 0이라 잔액 상한에서 0으로 잘려요"(s05-06 예고) |
| s02-04 | 점수를 받는 쪽은 계약이에요 | 교체 | 없음 → `scale.revised.account_types`, `timeline.anchors.account_types_block` | 새 제목 "그래프의 점은 [[모두 계약]]이에요". 사용자 계정 = 트랜잭션을 보낸 주소·코드 없는 주소·EIP-7702 계정·스마트 계정(Safe, ERC-4337). 사용자 계정은 어떤 그래프에도 없고, 중요도와 라벨에만 나와요. 작은 글: `eth_getCode` 블록 513,216,506. 옛 "EOA는 주인·보낸 쪽·받는 쪽으로 그래프에 나와요"는 지움 |
| s02-05 | 무대: 아비트럼 원 | 고침 | `params.chain.id`, `scale.revised.rows`(없어짐) → `scale.revised.events` | "체인 전체의 다섯 토큰 기록"으로. 옛 ego 비(1 : 5.1) 대신 다섯 토큰 행과 양끝이 계약인 행. s02-05 → s03-01 공유 요소 넘기기는 유지(묶음 2와 맞출 것) |

### s03-data (묶음 2)

| id | 제목 | 판정 | 키 | 할 일 |
|---|---|---|---|---|
| s03-01 | 3년의 달력 | 교체 | `timeline.anchors`, `periods`, `monthly_counts.{registered, revised}` → `periods[contract_events]`, `anchors.contract_events`, `monthly_counts.registered` | 제목을 기간에 맞춰(예: "기록의 달력, 두 번의 동결"). 주 분석 사건 기간 2025-04-01 – 2026-09-30(체인 전체, 다섯 토큰), t₁·T_obs와 각 12개월 점수 기간, W0·W1 라벨, W1 자물쇠(등록 뒤 추출). 1차 추출 33개월과 월별 띠는 등록 분석으로 작게(회색, `등록 분석` 태그) 또는 지움. 나이 자는 유지 |
| s03-02 | 얼마나 많은 기록인가 | 교체 | `scale.revised.rows`(없어짐), `timeline.monthly_counts.revised`(없어짐), `timeline.bigquery` → `scale.revised.events`, `timeline.bigquery.{total_usd, budget_usd, analysis_jobs, analysis_jobs_usd}` | 다섯 토큰 행 1,240,275,042 · 주소 25,537,280 · 양끝이 계약인 행 603,475,784 · 사용자 계정 → 계약 행 152,257,072(중요도에만). 와플은 행 수로 다시. 비용 54.88 / 예산 60달러(이 분석 26작업 12.63달러). 1단계 임시 수정(`monA = [0, 0]`)을 지움 |
| s03-03 | 다섯 토큰과 달러 가격 | 고침 | `prices.*`, `params.chainlink`(없음), `scale.tokens.{priced, selected_share_of_rows_tobs}` → `prices.tokens[].days_main_window`, `scale.revised.chainlink_check`, `scale.tokens.selected_tokens` | 548일 띠는 그대로. "그 기간 기록의 79.4%"(지갑 분석의 ego 행) 문장은 지움 또는 선정 기준(행 수 상위 다섯)만. 체인링크 점검 값은 새 `chainlink_check`(중앙값 0.0001–0.0006, 최대 0.002 이하)로, 원고 부록 표와 맞춤 |
| s03-04 | 코호트 깔때기 | 교체 | `scale.registered.{candidates, by_code_kind}`, `scale.revised.{cohort, left_out_of_registered, amounts.owners}` → `scale.revised.{account_types, members, by_class, cohort, cohort_coverage}` | "계정 종류 판별 → 계약만": 읽은 6,230,270 주소 → EOA 2,909,509 · EIP-7702 1,165,025 · 스마트 계정 326,017(Safe 46,204, ERC-4337 279,813) · 계약 1,829,719; 트랜잭션 보낸 주소까지 사용자 계정 21,877,279. 그다음 코호트: 12개월 목록 6,483 → 스마트 계정 40 빼고 6,443(W0 코호트 6,292, W0 스펜더 7,864, W1 스펜더 7,915). 그래프 안: 합집합 그래프 4,270(66.3%), 허락 층 1,250(19.4%), 밖 2,173 → 모든 점수 0. 등록 분석의 29,022/27,844는 지움(s10-05에서 비교) |
| s03-05 | 두 그래프의 크기 | 교체 | `scale.revised.graph_tobs`, `benchmark.revised.main` → + `scale.revised.{pairs, union_graph_tobs, nodes}` | 계약 그래프 1,403,959개 계약. T_obs: 상한 씌운 허락 115,006쌍(주인 계약 9,459 → 스펜더 100,112, 가장 큰 주인 하나가 98,073쌍 = 85%), 송금 2,580,709쌍, 합집합 2,575,632쌍 / 1,299,438개. 화살표 비 22.4배. t₁에서는 허락 17,940쌍(가장 큰 주인 256쌍): "허락 층은 얇아요". 옛 "주인 2,508,872명의 별자리"는 지움 |
| s03-06 | 6,483개 계약을 3D로 | 고침 | `contracts.*`, `results.revised.same_window.ties`, `scale.revised.graph_tobs.*` → + `contracts.in_union` | n = 6,443(제목은 수를 데이터에서). 엔도스랭크 0점이 대부분(허락 그래프 밖 5,193)이라 바닥판이 크게 보임: 상자 글을 새 `ties`와 `graph.cohort_outside_*`로. 공유 요소 s03-06 → s06-04 → s09-02 유지 |

### s04-pagerank (묶음 3)

| id | 제목 | 판정 | 키 | 할 일 |
|---|---|---|---|---|
| s04-01 | 작은 세계 | 고침 | `params.worked_example` | A를 "토큰 주인(EOA)"에서 주인 계약으로(예: 토큰을 가진 금고 계약). 원고 2장 Worked example의 지금 문구를 확인해 같게 |
| s04-02 | 무작위로 돌아다니는 사람 | 유지 | 예시 | — |
| s04-03 | 오래 걸으면 → 균형식 | 유지 | 예시 | — |
| s04-04 | 표로 한 번에: 이동 행렬 | 고침(45 → 30초) | 예시 | 한 단계 줄임 |
| s04-05 | 두 가지 문제: 새는 물과 함정 | 고침 | 예시 | 작은 글 "서로 허락하는 두 주소" → "두 계약"; "10장에서 다시" → "11장" |
| s04-06 | 고치기: 감쇠 d와 다시 출발 | 고침 | `params.pagerank` | π 카드: "모든 계약에 똑같이" |
| s04-07 | 거듭제곱 반복 | 고침 | `scale.revised.iterations_tobs`, `params.pagerank` | 반복 수 56(엔도스랭크)·98(AWP)로 바뀜(데이터에서 읽음; 옛 57·94 대체 값 지움) |

### s05-weights (묶음 2)

| id | 제목 | 판정 | 키 | 할 일 |
|---|---|---|---|---|
| s05-01 | 왜 화살표마다 무게가 다를까 | 고침 | `timeline.anchors.max_age_days_tobs` | 예의 금액(5달러 vs 5,000달러)은 허락 쪽에서 금액 무게가 1달러 근처에서 이미 1이 되는 것과 어긋나지 않게(예: 송금 쪽 예로) |
| s05-02 | 시간 무게 σ(Δt) | 유지 | `params.decay` | σ(0) 0.858은 새 `sybil.revised.json.sigma0` 0.8581과 같음 |
| s05-03 | 금액 무게 V(z) | 고침 | `scale.registered.amounts.*`, `params.value.b_A` | 등록 분석 대조(99.52%·99.78%)는 `등록 분석` 태그 그대로. 그림의 b = ln 3/100 → 새 b(데이터) |
| s05-04 | b = ln 3 / m | 교체(55 → 40초) | `params.value.{m_T, m_A, m_*_raw}` | m_T = 160달러(164.05, 계약 사이 송금 377,876,886건), m_A = 0.071달러(0.0707, t₁의 상한 씌운 양수 허락의 중앙값, 무제한 포함). 동전 줄 예시를 다시. 허락 쪽은 1달러에서 V ≈ 1.000(s11 농장에서 다시 씀). 옛 "492,666,999건 · 2,324,723건"은 지움 |
| s05-05 | 두 그래프의 무게와 다시 출발 | 고침 | 예시, `params.value` | "활발한 송신자" → "활발하게 보내는 계약", "허락을 많이 해 준 주인" → "주인 계약" |
| s05-06 | 달러로 바꾸기와 상한 U (C-PR용) | 교체 | `params.cap.{U_usd, p99_transfer_usd_raw, p99_finite_allowance_usd_raw(없어짐)}`, `scale.revised.amounts.{unlimited_share, allowances_at_or_above_cap_share, owners_with_both_kinds(없어짐)}` → `params.cap.{U_usd, U_user_usd, p99_*_raw, balance_cap}`, `scale.revised.amounts.*` | 제목 "달러로, 잔액까지만, 상한 U까지". 새 단계: 잔액 상한 usd_eff = min(허락, 동결 시점 주인의 잔액)(339,282 → 0으로 잘림 222,559, 상한 뒤 양수 116,723; 잔액 점검 1,493/1,500). U = 16,000달러(계약 사이 송금 한 건의 99번째 백분위 16,412 → 두 자리). U_user = 31,000달러는 08의 중요도에서 씀. s05-06 → s06-03 공유 요소(상한 막대 → 허락 줄)는 묶음 3과 맞출 것 |

### s06-methods (묶음 3)

| id | 제목 | 판정 | 키 | 할 일 |
|---|---|---|---|---|
| s06-01 | 엔도스랭크 | 고침 | `results.revised.same_window.graph`, `params` | 화살표 "주인 계약 → 스펜더 계약". "평가 대상 … 주인(EOA)도 몫을 갖지만" 줄을 "모든 점이 계약 · 평가는 허락을 받은 계약"으로. 그래프 109,389점 · 114,997화살표(데이터) |
| s06-02 | AWP와 원시 차수 기준선 | 고침 | 없음 → `results.methods` | 기준선 넷: 받은 허락 수(서로 다른 주인 계약), 받은 허락 금액, 송금 입차수(서로 다른 보낸 계약), 합집합 입차수(어느 층이든 화살표가 있는 서로 다른 계약). "사용자 계정을 세는 기준선은 없어요" |
| s06-03 | C-PR | 고침 | `params.cap.U_usd`, `params.coupled` | U = 16,000달러로(대체 값 19,000 지움). "분석 계획이 정함"은 λ에만 맞음 — 그대로 |
| s06-04 | λ를 돌리면 (대표 장면) | 고침 | `contracts.*`, `results.revised.same_window.*` | 박힌 λ 표(τ와 0점 수)를 `results.revised.same_window.per_proxy`와 `contracts.zeros`에서 읽게. 6,443개 |
| s06-05 | S-PR | 고침 | `results.revised.w0.contrasts_after` | 미리 보기 두 줄의 방향을 새 값으로 확인(`C§6 contrasts_after`) |

### s07-measure (묶음 3)

| id | 제목 | 판정 | 키 | 할 일 |
|---|---|---|---|---|
| s07-01 | 무엇과 견줄까: 점검과 시험 | 교체 | 없음 | 사다리: ① 같은 기간 점검(의도한 구성개념 점검) ② 발견 순서 검증(크롤이 사용자 수요가 큰 계약에 얼마나 빨리 닿는지, 08) ③ 기간 밖 예측(새 허락 쌍, 새 송금자, 09). GMX 칸을 지움. 지표 가족의 "보낸 주소" → "보낸 계약" |
| s07-02 | 켄달의 타우 | 고침 | `results.revised.same_window.inter_method.concordance.pairs` | 쌍 수는 데이터(6,443개의 쌍) |
| s07-03 | 동점이 있으면: τ_b | 고침(45 → 30초) | 예시 | 스피어먼 곁 판 줄임. "0인 계약이 많아요"는 이제 더 맞음(5,193) |
| s07-04 | 부트스트랩 | 고침 | `results.revised.same_window.{cohort, families}`, `params.stats.B_neutral`(없어짐) | 주머니 6,443개, 예 0.839 [0.828, 0.849](엔도스랭크 × 허락 가족, 데이터에서). "트레이더 비교는 B = 2,000" 지움. 발견 순서 검증의 부트스트랩(뜨거운 계약 위, 400번)을 한 줄 예고 |
| s07-05 | 짝지어 빼기 Δτ, 허용 폭 | 고침 | `results.revised.w0.*` | 예를 새 값으로: W0 새 허락 쌍 C-PR 0.142 vs 엔도스랭크 0.168, 짝지은 차이 −0.026 [−0.046, −0.004] → "이 예에서는 엔도스랭크가 조금 더 잘 맞혔어요". 본페로니 97.5%는 트레이더용이었으니 지움(δ = 0.01은 F2용으로 둠) |

### s08-discovery (새 섹션, 묶음 4) — 4절에 설계

### s09-results (옛 s08-results, 묶음 5)

| 새 id | 옛 id | 제목 | 판정 | 키 | 할 일 |
|---|---|---|---|---|---|
| s09-01 | s08-01 | 같은 기간: 각 점수는 자기 화살표의 지표와 | 고침 | `results.revised.same_window.families` | 엔도스랭크 × 허락 0.839, AWP × 송금 0.755, C-PR 값(데이터). 박힌 대체 값 지움 |
| s09-02 | s08-02 | 두 점수는 순서가 달라요 | 고침 | `contracts.*`, `results.revised.same_window.inter_method` | τ = 0.275 [0.258, 0.294]. 두 점수가 모두 순서를 정한 쌍은 32.3%(엔도스랭크 0점 5,200개 때문), 그중 반대 26.7%. 외톨이 점으로 두면 허락 가족 0.956(`tie-sensitivity`). 등록 분석 유령 0.217 그대로 |
| s09-03 | s08-03 | 기간 밖 예측: 점수를 얼리고 기다려요 | 고침 | `scale.revised.{w0, w1}`, `holdout.*`, `timeline.monthly_counts.revised`(없어짐) → + `scale.revised.{label_split, cohort_coverage}`, `w0/w1.in_union_graph` | 스펜더 7,864 / 7,915, 새 허락 쌍 1,725 / 1,491, 새 송금자 1,416 / 1,369. 두 사실을 화면에: 라벨은 모든 계정을 세요(W0 새 허락 쌍의 90.4%가 사용자 계정)인데 어떤 점수도 사용자 계정을 읽지 않아요; 스펜더의 약 27%는 합집합 그래프 밖이라 0점. 월별 띠(없어짐)는 지우고 점수 기간 띠만. "W1 등록 기간"은 "W1(등록한 기간)" 그대로 |
| s09-04 | s08-04 | 송금 쪽: 그냥 센 수가 AWP를 이겨요 | 교체 | `results.revised.{w0.taus, w1.spender_taus, w0.contrasts_after, w0.receiving}` | 방향이 바뀜: 코호트 전체에서는 AWP가 송금 입차수보다 조금 위(W0 +0.012 [0.003, 0.023], W1 +0.011 [0.001, 0.022]), 다른 계약이 동결 전에 송금한 W0 스펜더 4,569개에서는 아래(−0.035 [−0.049, −0.022]). 둘 다 말함. 제목을 새 결과로 |
| s09-05 | s08-05 (+ s08-06 합침) | 허락 쪽: 그냥 센 수가 이겨요 | 고침 | `results.revised.*`, `results.revised.supplementary.*` | 엔도스랭크 − 받은 허락 수: W0 −0.036 [−0.046, −0.027], W1 −0.034 [−0.043, −0.025]; 활동 재시작도 −0.041 / −0.033(옛 s08-06의 내용을 단계 하나로). 부익부 그림 유지 |
| — | s08-06 | 다시 출발 규칙만 바꾸면? (사후) | 합침 | — | s09-05의 한 단계로 |
| s09-06 | s08-07 + s08-08 | 닫힌 식과 결과 한 장 | 합침(105 → 55초) | `results.closed_form.revised`, `params.closed_form` | 한 단계 스펜더 651/926 모두 1% 안, 더 깊은 쪽 33.8%. 아래 판 "넷 모두 센 수가 이겨요"는 틀려짐 → 결과 한 장을 새로(허락 쪽은 센 수가 위, 송금 쪽은 AWP가 조금 위·송금 받은 스펜더에서는 아래, C-PR은 합집합 입차수보다 허락 쌍에서 위·송금자에서 아래) |

### s10-rules (옛 s09-rules, 묶음 5)

| 새 id | 옛 id | 제목 | 판정 | 키 | 할 일 |
|---|---|---|---|---|---|
| s10-01 | s09-01 | 언제, 무엇을 정했나 | 고침 | `timeline.{commits, events, gaps, periods}` | 등록 줄의 "R1–R3" 지움(규칙 B · 허용 폭 · 판정 문장). 선 아래 "그 뒤 · 수정 분석을 정함" 꼬리표를 정의 전부로: 달러 · 다섯 토큰 · 12개월 점수 · 계약만의 그래프(체인 전체) · 잔액 상한 · 계약 그래프 위의 상수 · 발견 순서 검증. 시각 없음 |
| s10-02 | s09-02 | 규칙 A | 고침 | `results.verdicts.revised.{rule_a_primary, rule_a_secondary}` | ① −0.025 [−0.045, −0.004] 미충족(옛 화면은 충족), ② −0.014 [−0.019, −0.008] 미충족, ③ 0.738 vs [0.799, 0.809] · 0.433 vs [0.827, 0.850] · 시빌 0.574(0.222와 0.637) 미충족. "규칙 A 미충족" `재분석`. 규칙 밖 한 줄(합집합 그래프 안에서는 허락 층과의 차이가 0을 품음; 상한 없는 허락 층이면 +0.064)은 노트로 |
| s10-03 | s09-03 | 규칙 B | 교체 | `results.verdicts.revised.rule_b`(+ `rule_b_sensitivity_*`), `results.revised.w1.rule_b` | 두 줄만: F1 +0.074 [0.060, 0.087] ✓, F2 −0.016 [−0.022, −0.012] ✕(허용 폭 −0.01). 머리에 정해 둔 문장("등록된 기준 가운데 두 가지 … 모두 설 때만 충족"). 도장 "규칙 B는 충족하지 못했어요" `재분석`. F3 줄과 ×200 확대 창은 지움. 두 민감도 분석도 같은 읽기(작은 글). F6a −0.043은 노트 |
| s10-04 | s09-04 | 규칙 밖에서: C-PR을 다른 점수와 견주면 | 고침 | `results.revised.{w0.contrasts_after, w1.endorserank_results, supplementary, w0/w1.baseline_contrasts, in_union_graph}`, `results.lambda_sweep.revised.degree_baselines.in_degree_union` | 새 값(C4): 엔도스랭크 대비 허락 쌍 아래·송금자 위, AWP 대비 허락 쌍 위·송금자 아래, 송금 받은 스펜더만, 활동 재시작, S-PR, 센 수 넷. 합집합 입차수 줄을 더함(C2): 새 허락 쌍에서 위(W0 +0.016 [0.007, 0.024], W1 +0.011 [0.003, 0.019]), 새 송금자에서 아래(−0.053, −0.056); 합집합 그래프 안에서도 같은 방향. 정리 글을 새 방향으로. 태그 `사후(라벨 본 뒤)` |
| s10-05 | s09-05 | 등록 분석과 수정 분석 | 교체(50 → 30초) | `scale.registered`, `scale.revised`, `results.registered`, `results.revised` | 제목 "두 분석, 같은 판정"(규칙 A 미충족, F1 섬·F2 못 섬). "고친 이유 셋"(①②③)은 바꾼 이력이라 지움. 표: 코호트 27,844 / 6,443 · W0 스펜더 33,101 / 7,864 · W1 34,587 / 7,915 · τ(엔도스랭크, AWP) 0.217 / 0.275. 등록 분석의 설명은 그 자체로(원래 단위, 모든 토큰, b = 1, 2023년 10월부터, 코호트 사건의 모든 계정이 든 그래프) |
| — | s09-06 | 두 화살표 어디에도 없는 결과: R1–R3 | 지움 | `traders`, `results.verdicts.revised.{R1–R3, P_*, Q_*}` | 장 전체를 지움. 그 55초는 08에 씀. 다른 장에서 이 장을 가리키는 말도 지움(지웠다고 쓰지 않음) |

### s11-sybil-speed (옛 s10-sybil-speed, 묶음 3)

| 새 id | 옛 id | 제목 | 판정 | 키 | 할 일 |
|---|---|---|---|---|---|
| s11-01 | s10-01 | 가짜 주소 농장 | 교체 | `sybil.revised.json.{r_D, damping, ring20_collects_times_share, graph}` → + `contract_farm` | 닫힌 농장은 인구 비율의 6.16배(d 0.75 → 3.73, 0.95 → 18.30), 고리 20개 6.157, r_D 0.911, 풀이 그래프 109,381점 · 114,997화살표. "허락은 잔고가 없어도 할 수 있어요 → 드는 돈은 가스뿐"은 이제 틀림: 농장의 주소는 모두 계약이라 하나마다 배포(팩토리로 32,000가스 이상, 자기 트랜잭션으로 53,000가스 이상 + 코드 1바이트에 200가스), 허락은 그 계약의 잔액까지만 셈. 제목 수는 데이터에서 |
| s11-02 | s10-02 | 별 모양 농장 | 교체 | `sybil.revised.{json.star, key_points, pair_score, gain_per_farm_address}` | 별 10개: 2.891 × 10⁻⁴ = 꼭대기(0.0097)의 3.0%. 중앙값 점수가 0(코호트의 81%가 허락 그래프 밖)이라 "중앙값보다 높지만"의 비교 줄이 달라짐: 10개짜리 별이 이미 99번째 백분위(9.31 × 10⁻⁵) 위. 1단계 임시 수정(`lg`의 바닥 −9)을 지우고 0점을 그리는 방법을 정함 |
| s11-03 | s10-03 | 꼭대기까지 몇 개 | 교체 | `sybil.revised.{curve, key_points}`, `contracts.log10.endorserank` → + `json.balance_threshold`, `json.contract_farm.deployments`, `json.fresh_approval_share_median_owner` | 꼭대기까지 농장 계약 약 374개(배포 375), 99번째 백분위 약 3개. 새 허락 하나가 중앙 주인의 줄에서 68.7%. V(1달러) = 1.000(m_A 0.071달러). 잔액 문턱 θ: 1달러면 쌍의 3.7%만 남고 꼭대기까지 119개, 100달러면 0.9%만 남고 10개짜리 별이 꼭대기를 넘음 → "문턱은 농장의 자본을 늘리지만 정직한 그래프를 더 빨리 줄여요". 탑 점구름은 6,443개, 0점 바닥 처리 |
| s11-04 | s10-04 | 속도는 그래프 크기와 반복 횟수에서 (RQ1) | 고침 | `benchmark.revised.*`, `results.revised.same_window.{graph, iterations}` | 엔도스랭크 0.101초(114,997화살표, 56번), AWP 2.82초(2,580,381, 98번): 시간 27.9배, 화살표 22.4배(d 0.75·0.95에서 20.5·34.5). C-PR 3.08초(AWP의 1.09배), S-PR 2.66초(153번). 제목의 RQ 번호를 RQ1로(비용은 RQ1). s11의 digest 대조 문자열을 새 값으로(경고가 사라짐) |

### s12-closing (옛 s11-closing, 묶음 1)

| 새 id | 옛 id | 제목 | 판정 | 키 | 할 일 |
|---|---|---|---|---|---|
| s12-01 | s11-01 | 연구 질문에 대한 답 | 교체 | `results.revised.*`, `benchmark.revised.*`, `results.revised.w1.neutral_*`(없어짐) → + `discovery.decision` | RQ1: τ 0.275, 0.839·0.755, 비용 27.9배 / 22.4배. RQ2: "아니요 — 너비 우선보다는 빨랐지만 계약 역링크 수보다 빠르지 않았어요"(D1 > 0, D2 < 0, V2). RQ3: 허락 쪽은 센 수가 이김, 송금 쪽은 AWP가 조금 위(송금 받은 스펜더에서는 아래), C-PR은 합집합 입차수보다 허락 쌍에서 위·송금자에서 아래. RQ4: 규칙 A 미충족. RQ5: 규칙 B 미충족(F1 섬, F2 못 섬). 등록 분석도 같은 판정. 옛 "청산 피하기" 줄과 트레이더 와플을 지움 |
| s12-02 | s11-02 | 이 연구가 새로 보탠 것 | 고침 | 없음 | ⑤(GMX)를 지우고 "계약 그래프에서 다시 한 크롤 순서 실험(중요도 = 사용자 계정의 수요)"을 넣음. ①의 "규칙 밖에서는 두 스펜더 라벨 모두 엔도스랭크보다 위"는 틀려짐 → 새 결과로. 작은 글 "빌려 온 것 / 새것" 유지 |
| s12-03 | s11-03 | 한계 | 고침 | `results.revised.w1.neutral_*`(없어짐) | 지울 줄: 트레이더 표본, "에고 네트워크". 더할 줄: 스마트 계정 판별이 놓치는 종류(계약으로 남은 `validateUserOp` 셀렉터 115,084개), T_obs 허락 층은 주인 계약 하나가 85%, 허락 층이 얇음(t₁ 파일럿 0.5%, 멈춤 표시가 섰고 검증은 계속함), 라벨은 사용자 계정을 세지만 점수는 읽지 않음, 스펜더의 약 27%가 그래프 밖, 한 블록의 계정 종류. "EOA에 대해 말하지 않아요" → "사용자 계정에 점수를 주지 않아요" |
| s12-04 | s11-04 | 지갑 프로그램이 보여 줄 수 있는 것, 다음 일 | 고침 | 없음 | 지갑 창의 새 줄은 시험한 것만(예: "이 계약을 허락한 다른 계약 수" 또는 C-PR 순위, `가설`/자리 표시 표시 유지). 다음 일을 원고 6.3절대로: 계약에 대한 신용 판단(시험하지 않음, 바라는 쓰임으로 한 번), 체인 밖 중요도 라벨, 더 나은 스마트 계정 판별, 데이터가 생기기 전에 정한 나중 동결에서 발견 순서 검증, C-AWP(이름만) |
| s12-05 | s11-05 | 감사합니다 | 고침 | `meta.*` | digest 경로 `…/revised-contract-12m/` |

---

## 4. 발견 순서 검증 섹션(`s08-discovery`, 묶음 4)

모든 숫자는 `data/discovery.js`(`DD.discovery`)에서 읽어요. 판정은 `runs.tobs_both`만. 태그는 1절 9번의 새 태그. 기호는 `_revision-context.md`의 표기(𝒰, H_q(I), AUC_10%, D1, D2, 프라임). 섹션 첫 장 의식(유령 숫자 `08`).

| 새 id | 제목(안) | 시간 | 내용 | 키 |
|---|---|---|---|---|
| s08-01 | 웹 크롤러처럼 계약을 찾아가요 | 50초 | Cho, Garcia-Molina, Page(1998)의 크롤 순서 실험을 계약 그래프에서. 거대 강연결 성분의 무작위 계약 하나에서 출발(출발 계약 20개), 방문하면 그 계약의 들어오고 나가는 화살표가 드러나고(`both`), 프런티어에서 다음 계약을 순서 규칙으로 골라요. 우주 = 거대 SCC의 약연결 성분 1,169,044개(나비넥타이: SCC 265,804 · IN 174,239 · OUT 242,833). s04의 작은 세계 그림을 다시 써도 좋음 | `runs.tobs_both.{sizes, seeds}`, `meta.modes` |
| s08-02 | 무엇으로 다음 계약을 고를까: 순서 규칙 | 45초 | 너비 우선(BFS), 무작위, 계약 역링크 수 IB′_U(허락 IB′_A, 송금 IB′_T), 걷기 EndorseRank′·AWP′·C-PR′·S-PR′, 진단 δ′. 프라임 = 지금까지 읽은 계약들로 계산. 걷기는 방문의 1/50마다 다시 계산(ρ). | `orderings`, `runs.tobs_both.protocol` |
| s08-03 | 무엇이 중요한 계약일까: 사용자 계정의 수요 | 45초 | 중요도는 어떤 순서 규칙도 읽지 않는 사용자 계정의 수요: I_T(사용자 계정이 보낸 달러, 계정마다 U_user = 31,000달러까지; 합 166.1억 달러), I_A(잔액 상한을 씌운 허락 달러; 3.095억 달러). 우주가 I_T의 96.5%, I_A의 93.0%를 담아요. 뜨거운 집합 = 상위 1%(13,141 / 11,662개). 사용자 계정은 그래프의 점이 아님을 다시 | `scale.revised.importance`, `runs.tobs_both.{hot_sets, diagnostics.coverage}`, `params.cap.U_user_usd` |
| s08-04 | 얼마나 빨리 닿았나: AUC_10% | 50초 | P_ST 곡선(방문한 몫 → 찾은 뜨거운 계약의 몫), 첫 10% 방문까지의 넓이를 이상적인 순서로 나눔(식 g_x(h)). 수준: BFS 0.0565 · IB′_U 0.1136 · C-PR′ 0.1085 · AWP′ 0.1465(가장 높음) · 이상적인 순서 0.9438 · 무작위 곡선 0.0500 → "모든 크롤이 이상에서 멀어요". I_A 쪽 값도 | `runs.tobs_both.{curves.P_ST, auc['i_t@q'], auc['i_a@q']}` |
| s08-05 | 판정: D1과 D2 (RQ2) | 50초 | D1 = C-PR′ − BFS: +0.0520 [+0.0485, +0.0558](I_T), +0.0061 [+0.0014, +0.0111](I_A). D2 = C-PR′ − IB′_U: −0.0051 [−0.0087, −0.0010], −0.0571 [−0.0621, −0.0519]. 두 중요도 모두 판정 V2. 판정 문장을 그대로(§5c). "RQ2의 답: 아니요" | `discovery.decision`, `runs.tobs_both.decision` |
| s08-06 | 판정 밖에서 본 것 | 50초 | (1) `out` 방식(나가는 화살표만, 우주 SCC ∪ OUT)에서는 네 대비가 모두 0보다 위(T_obs D1 +0.2650·+0.1143, D2 +0.0803·+0.0436; t₁도) — 판정이 아닌 민감도. (2) 고정 순서 비교: AWP′만 자기가 다듬는 센 수 위, 허락 층은 조금 보탬(C-PR′ − C-PR′(λ=0) +0.0024·+0.0137), C-PR′는 AWP′ 아래. (3) t₁ both도 D1 > 0, D2 < 0. (4) 진단: 센 수 순서 규칙은 거의 모든 선택을 동점으로(0.9998–0.9999), C-PR′는 0.535; 첫 10% 방문의 0.83–0.91이 헛 방문. 파일럿의 멈춤 표시(t₁ SCC ∪ OUT의 0.5%만 상한 씌운 허락 화살표를 받음)와 계속한 이유 한 줄 | `runs.tobs_out.decision`, `runs.t1_*.decision`, `runs.tobs_both.{fixed_order, diagnostics}`, `pilot` |

- 시간 4:50. 길면 s08-06의 진단을 노트로 내려 4:30.
- 주의: "C-PR′이 더 빨리 찾았다"를 뒷부분 없이 쓰지 않음; `out` 결과를 답처럼 내세우지 않음; 프로토콜 시각을 쓰지 않음; IB_U·IR 뜨거운 집합 결과(4_cho)는 의도한 구성개념 점검으로만.

---

## 5. GMX·트레이더가 있던 곳과 그 시간

| 곳 | 무엇 | 처리 |
|---|---|---|
| s02-04 노트, 섹션 머리 | 계정 종류를 읽은 블록 설명의 "GMX 계정" | 지움(묶음 1) |
| s07-01 | 사다리 셋째 칸 "GMX V2 계약 트레이더의 청산" | 발견 순서 검증 칸으로(묶음 3) |
| s07-04 | "트레이더 비교는 B = 2,000" | 지움(묶음 3) |
| s07-05 | 본페로니 97.5% 설명(R1·R2용) | 지움(묶음 3) |
| s09-02(새 s10-02) 머리 상수 | `F3LO`, `F3TAU` 등 | 지움(묶음 5) |
| s09-03(새 s10-03) | F3 줄, 확대 창 | 지움(묶음 5) |
| s09-04(새 s10-04) | "R1 충족 / R2 / R3" 표 줄 | 지움(묶음 5) |
| s09-05(새 s10-05) | "R1만 빼고 같은 판정" | 제목과 표를 새로(묶음 5) |
| s09-06 | 장 전체(55초) | 지움 → 08에 씀 |
| s11-01(새 s12-01) | RQ5 칸의 청산 피하기, W1 트레이더 와플 | 지움(묶음 1) |
| s11-02(새 s12-02) | ⑤ 등록한 비교(GMX) | 발견 순서 검증으로 바꿈(묶음 1) |
| s11-03(새 s12-03) | 트레이더 표본 70·87 | 지움(묶음 1) |
| `STORYBOARD.md` §0.3 | `등록함(W1)`의 "F4–F6, R1–R3", `탐색적`(W0 트레이더) | 고침(묶음 0) |
| `README.md` | 데이터 표의 `traders.js`, 섹션 표의 "R1–R3", digest 경로 | 고침(묶음 0) |

시간: s09-06(55초)과 줄인 장들(약 3분 25초)로 새 섹션(4분 30초–4분 50초)을 대요.

---

## 6. 사용자 계정을 점·주인·보낸 쪽으로 그린 곳

| 곳 | 지금 | 고칠 것 |
|---|---|---|
| s02-01 | 계약 둘레의 EOA 점선 원(디파이 그림) | 디파이 설명이면 둘 수 있음. 이 연구의 그래프 그림이 아님을 분명히 |
| s02-04 | "EOA는 화살표의 끝점으로만 나와요 — 주인, 보낸 쪽, 받는 쪽"(화면·노트) | 교체(3절) |
| s03-03/s03-04 | 깔때기에서 EOA가 속 빈 회색 원으로 빠짐, "EOA라서 뺌" | 계정 종류 판별 깔때기로 교체(3절) |
| s03-05 | "허락 그래프 = 주인 2,508,872명이 … 가리키는 별자리" | 주인 계약 9,459 → 스펜더 100,112 |
| s03-06, s06-04 | 깊이축 "송금을 보낸 주소 수", 가로축 "허락한 주인 수" | "보낸 계약 수", "허락한 주인 계약 수" |
| s04-01 | "A 토큰 주인(EOA), 사람의 지갑 주소" | 주인 계약 |
| s05-05 | "활발한 송신자", "허락을 많이 해 준 주인" | 계약으로 |
| s06-01 | "평가 대상 … 주인(EOA)도 걷기에서 몫을 갖지만 평가하지 않아요"; 노트의 EOA 몫 | 모든 점이 계약 |
| s06-02 | 송금 입차수 = "보낸 서로 다른 주소 수" | 서로 다른 보낸 계약 수; 합집합 입차수 더함 |
| s07-01 | 지표 가족 "보낸 주소" | 보낸 계약 |
| s09-03, s09-04(새 번호) | 라벨 "처음으로 송금을 보내온 주소" | 라벨은 모든 계정을 세므로 "주소(사용자 계정 포함)"가 맞음. 단, 점수와 기준선은 사용자 계정을 읽지 않는다는 말을 함께 |
| s11-01–s11-03(새 번호) | "가짜 주소", "서로만 허락하는 주소" | "가짜 계약(농장 계약)": 배포가 필요한 계약 |
| s12-02, s12-03(새 번호) | "EOA에 대해서는 말하지 않아요" | "사용자 계정에는 점수를 주지 않아요" |
| `components.js` | 지갑 창, EOA 원 글리프(G-묶음) | 글리프는 그대로 둘 수 있음. 그래프 그림에서는 쓰지 않음 |

---

## 7. 시빌 장(새 s11-01–s11-03)

- 농장의 모든 주소는 계약이에요(`sybil.revised.json.contract_farm.note`). 그래서 비용 이야기가 "허락 두 번의 가스"에서 셋으로 바뀌어요: (1) 배포 — 하나마다 팩토리로 32,000가스 이상, 자기 트랜잭션으로 53,000가스 이상, 코드 1바이트에 200가스(실행 가스만, L1 데이터 비용 빼고; 출처 Yellow Paper 부록 G), (2) 잔액 — 허락은 그 계약의 잔액까지만 세요, (3) 잔액 1달러로 이미 금액 무게가 다 차요(m_A = 0.071달러, V(1달러) = 1.000).
- 숫자: r_D 0.911, 닫힌 농장 6.16배(3.73, 18.30), 별 10개 꼭대기의 3.0%, 꼭대기까지 약 374개(배포 375), 새 허락 하나가 중앙 주인 줄의 68.7%.
- 잔액 문턱 θ(`balance_threshold`): θ = 1달러에서 쌍의 3.7%만 남고 꼭대기까지 119개, θ = 100달러에서 0.9%만 남고 10개짜리 별이 꼭대기를 넘음. 메시지: 문턱은 농장이 들고 있어야 할 자본을 늘리지만 정직한 그래프를 더 빨리 줄여요.
- 그림: 코호트 중앙값과 90번째 백분위의 점수가 0과 아주 작은 값이라 로그 막대·탑의 바닥 처리가 필요해요(1단계의 `lg` 임시 바닥을 지우고, 0점은 바닥판에 따로).
- 이 장들은 어떤 규칙도 정하지 않아요(`sybil_model.json`의 note).

---

## 8. 묶음

묶음 0을 먼저 끝내고, 묶음 1–5는 동시에 해요. 각 묶음은 맡은 섹션을 `js/sections/`와 `js/sections-en/`에서 함께 고치고, `STORYBOARD.md` §2의 맡은 장 항목(그리고 섹션 머리)을 고쳐요. 영문판은 같은 장 id와 단계를 지켜요.

| 묶음 | 맡는 것 | 파일 | 장 수 | 메모 |
|---|---|---|---|---|
| 0 · 뼈대(먼저, 짧게) | 섹션 번호 미루기와 새 섹션 자리 | 파일 이름 바꾸기(커밋은 저자가 정함): `s08-results.js` → `s09-results.js`, `s09-rules` → `s10-rules`, `s10-sybil-speed` → `s11-sybil-speed`, `s11-closing` → `s12-closing`(두 언어), 각 파일의 섹션 id와 장 id(`s08-0N` → `s09-0N` …), 장 사이를 가리키는 말(`#s08-03`, "10장에서" 등)의 번호; 빈 `s08-discovery.js`(두 언어, 장 껍데기 6개); `index.html`·`index.en.html`의 스크립트 목록; `deck.js` 태그 표에 발견 순서 검증 태그 더하고 `탐색적` 정리; `STORYBOARD.md` §0(근거 경로 `revised-contract-12m`, §0.2 `R§` → `C§`, §0.3 태그, §0.4 정직성 규칙을 1절대로), §1.8 데이터 키 표, §1.10 시간표, §3 목록; `README.md`의 섹션 표·데이터 표·출처 표; `tools/build_print.mjs`와 `shoot.mjs` 도움말의 예시 id | — | 번호만 바꾸고 화면 글은 고치지 않음. 끝나면 probe로 60장 그대로 열리는지 확인 |
| 1 · 틀과 맺음 | s01, s02, s12(옛 s11) | `s01-opening.js`, `s02-world.js`, `s12-closing.js` | 13 | 목표와 RQ 번호(RQ2 = 발견 순서 검증, 비용은 RQ1)를 처음과 끝에서 똑같이. 지갑 창 공유 요소 s01-01 → s12-04. s02-05 → s03-01 넘기기는 묶음 2와 맞춤 |
| 2 · 데이터와 무게 | s03, s05 | `s03-data.js`, `s05-weights.js` | 12 | 계정 종류, 체인 전체 사건, 계약 그래프 층과 얇은 허락 층, 잔액 상한, 상수(m_T 160, m_A 0.071, U 16,000, U_user 31,000). 1단계 임시 수정(s03 `monA`) 지움. s05-06 → s06-03 넘기기는 묶음 3과 맞춤 |
| 3 · 방법, 재는 법, 시빌과 속도 | s04, s06, s07, s11(옛 s10) | `s04-pagerank.js`, `s06-methods.js`, `s07-measure.js`, `s11-sybil-speed.js` | 21 | 대부분 글·숫자 고침. s04-05 → s11-01(함정 → 농장) 넘기기가 같은 묶음 안. s11의 1단계 임시 수정(`lg`)과 digest 대조 문자열 정리 |
| 4 · 발견 순서 검증 | 새 s08 | `s08-discovery.js` | 6 | `data/discovery.js`만으로 그림. 곡선 그림은 dataviz 원칙(색은 기존 토큰: C-PR 보라, 센 수 초록 …). 새 태그 사용 |
| 5 · 기간 밖 예측과 규칙 | s09(옛 s08), s10(옛 s09) | `s09-results.js`, `s10-rules.js` | 11 | 방향이 바뀐 결과(송금 쪽 AWP, C-PR과 합집합 입차수), 규칙 B를 F1·F2만, s10-06 지움, 등록 분석 비교 줄임. 공유 요소 s03-06 → s06-04 → s09-02(점구름)의 끝을 맡음 |

마지막(누구든 하나, 모든 묶음 뒤):

1. `python tools/build_data.py`(72/72)와 두 판 probe(모든 장·단계에서 콘솔 오류 0, 경고 0이 목표).
2. 바뀐 화면 글에서 금지어 찾기: `GMX|트레이더|청산|R1|R2|R3|F3|등록된 결과|registered result|EOA는 .*그래프|에고|ego|6,483|revised-usd`(등록 분석 설명 안은 예외).
3. `tools/build_single.py`로 `dist/` 다시 묶고, 인쇄판(`node build_print.mjs`)을 다시 만들기. 스크린샷 일부(`node shoot.mjs --only s08-discovery`).
4. `video/`의 대본은 고치지 않아요(이번 개정에서 그대로 둠). README에 "영상 대본은 계약 그래프 분석을 따르지 않는다"는 줄만 맞춤.
