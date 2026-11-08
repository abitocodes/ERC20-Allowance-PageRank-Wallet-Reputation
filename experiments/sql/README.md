# sql

BigQuery 쿼리입니다. 직접 돌리지 않고 `../scripts/run_bq.py`(수정 분석은 `../scripts/run_usd_pipeline.py`, 12개월 변형은 `../scripts/run_usd12m_pipeline.py`, 컨트랙트 그래프 수정은 `../scripts/run_contract12m_pipeline.py`)로 돌립니다. 그러면 매개변수(`@start_ts` 등)와 자리 표시자(`__TAG__` 등)를 채우고, dry run으로 비용을 먼저 본 뒤, 청구된 바이트를 `../data/bq_ledger.json`에 적습니다. 결과 테이블은 BigQuery 데이터셋 `dissertation-bq.contract_rep`에 생깁니다.

01–11은 등록 분석(원시 단위, 모든 토큰), 12–19는 수정 분석(USD, 다섯 토큰), 20–23은 12개월 변형(같은 다섯 토큰, 동결마다 직전 12개월; `../docs/revision_one_year_window.md`)입니다. 수정 분석의 쿼리는 등록 분석의 에고 테이블을 읽어 이름이 `u_`로 시작하는 새 테이블만 만들고, 등록 분석의 테이블은 바꾸지 않습니다. 12개월 변형은 이름이 `u12_`로 시작하는 테이블과 view만 만들고, 13–17을 고치지 않은 채 테이블 이름만 바꿔(`run_bq.py --rename`) 다시 씁니다. 24–35와 43(게이트 A), 36–42(게이트 B)는 컨트랙트 그래프 수정(`../docs/revision_contract_graph.md`)이고, 이름이 `c12_`로 시작하는 테이블만 만들며, 공개 view는 드라이버가 전체 이름으로 적은 것만 읽습니다(`run_bq.py --allow-public`). 01–23은 고치지 않습니다.

## 등록 분석

| 파일 | 하는 일 |
|---|---|
| `01_materialize_logs.sql` | 공개 Arbitrum One 로그에서 이 연구의 이벤트를 프로젝트 테이블 하나로 옮깁니다. scan A는 관측 기간(`logs_obs`), scan B는 7~9월(`logs_w1`)입니다. 뒤의 쿼리는 모두 이 테이블을 읽습니다. |
| `02_spender_candidates.sql` | 코호트 후보: 관측 기간에 서로 다른 주인 셋 이상에게 0이 아닌 Approval을 받은 스펜더(`spender_candidates`). 계정 종류는 뒤에 `eth_getCode`로 읽습니다. |
| `03_ego_events.sql` | 매칭 코호트의 에고 네트워크: 코호트 컨트랙트가 주인이나 스펜더인 승인, 보낸 쪽이나 받은 쪽인 송금 |
| `04_anchor_pairs.sql` | 한 기준 시점(T_obs 또는 동결일 t1)에서 두 그래프의 간선 집계 |
| `05_proxies_same_window.sql` | 관측 기간 전체의 송금 지표와 Sybil 안정성 지표 |
| `06_holdout_labels.sql` | 동결일에 양의 최신 허락을 가진 스펜더의 홀드아웃 라벨(W0, W1) |
| `07_gmx_accounts.sql` | GMX V2 `PositionDecrease` 로그의 계정 목록(`gmx_accounts`) |
| `08_export_ids.sql` | 정수 노드 번호(`nodes`)와 내려받을 간선표 |
| `09_gmx_contract_closes.sql` | 컨트랙트 계정의 GMX V2 종료 로그(해독은 `decode_gmx_events.py`) |
| `10_describe.sql` | 3·4장의 기술 통계(`describe_monthly`, `describe_values`) |
| `11_top_tokens.sql` | 강건성 점검용 상위 20개 토큰 부분 그래프(금액 순, 행 수 순) |

## 수정 분석

| 파일 | 하는 일 |
|---|---|
| `12_usd_ego.sql` | 다섯 토큰만, 금액을 토큰 단위와 USD로 바꾸고, 그 토큰의 승인으로 코호트 규칙을 다시 적용합니다(수정 코호트는 등록 코호트의 부분집합). |
| `13_usd_constants.sql` | USD 척도 상수. 가장 이른 동결일 t1(2026-03-31)까지의 사건만 써서 라벨 기간의 사건이 들어가지 않게 합니다(`u_constants`). |
| `14_usd_anchor_pairs.sql` | 한 기준 시점의 두 그래프 간선 집계(USD) |
| `15_usd_proxies.sql` | 같은 기간 지표(`u_proxies_tobs`). 송금마다 그날의 가격을 씁니다. |
| `16_usd_labels.sql` | 홀드아웃 라벨(다섯 토큰만) |
| `17_usd_export_ids.sql` | 정수 노드 번호(`u_nodes`)와 내려받을 간선표 |
| `18_usd_describe.sql` | 기술 통계와, 토큰 목록과 수정 코호트가 빼는 행의 집계 |
| `19_usd_load.sql` | 올린 토큰 목록과 일별 가격의 16진 주소를 에고 테이블과 같은 20바이트 BYTES로 바꿉니다. |

## 12개월 변형

| 파일 | 하는 일 |
|---|---|
| `20_usd12m_token_rows.sql` | T_obs 점수 기간(2025-07-01 ~ 2026-06-30)에 등록 에고 데이터의 토큰별 행 수(`u12_token_rows`). 기록만 하고 다섯 토큰은 바꾸지 않습니다. |
| `21_usd12m_cohorts.sql` | 동결마다의 코호트(`u12_cohort_tobs`, `u12_cohort_t1`: 그 12개월 안에 서로 다른 주인 셋 이상)와, 33개월 USD 에고 테이블 위에 그 코호트의 기간별 사건만 남긴 view(`u12_approvals_*`, `u12_transfers_*`) |
| `22_usd12m_describe.sql` | 18과 같은 기술 통계를 점수 기간 안에서 셉니다(`u12_describe_*`). |
| `23_usd12m_checks.sql` | 33개월 테이블과의 불변식(`u12_checks`, 모두 0이어야 함): 기간 안의 최신 허락이 양쪽에서 같음, 코호트가 `u_cohort`의 부분집합, 송금 쌍이 33개월 쌍 안에 있음 |

13(상수, W0 view), 14(T_obs·t1의 간선 집계), 15(지표), 16(W0·W1 라벨; 하드코딩된 "seen" 송금 테이블도 그 동결의 view로), 17(노드 번호)은 `run_usd12m_pipeline.py`가 이름을 바꿔 돌립니다.

## 컨트랙트 그래프 수정(게이트 A)

계정 종류를 정하고 컨트랙트끼리의 구조만 보는 단계입니다(점수, 중요도, 라벨, 상수는 아직 없음). 30은 로컬 parquet을 올리는 load 작업이라 SQL 파일이 없습니다. 36–42는 게이트 B의 작업입니다(아래).

| 파일 | 하는 일 |
|---|---|
| `24_c12_logs5.sql` | 판정 기간(2025-04-01 ~ 2026-09-30)의 다섯 토큰 `Approval`(값과 무관)과 0이 아닌 `Transfer`를 `logs_obs`·`logs_w1`에서 한 테이블로(`c12_logs5`, 송금은 그날 가격의 USD). 뒤의 작업은 모두 이 테이블을 읽습니다. |
| `25_c12_ends.sql` | 그 사건의 순서쌍(`c12_pairs5`)과 끝점 E(`c12_ends`, 영 주소 제외) |
| `26_c12_tx_senders.sql` | E 가운데 2026-10-01 전에 트랜잭션을 보낸 주소(`c12_tx_senders`, 사용자 계정) |
| `27_c12_emitters.sql` | E 가운데 판정 기간에 해독된 로그를 낸 주소와 Safe 이벤트 수(`c12_emitters`, 교차 점검만) |
| `28_c12_creations.sql` | E 가운데 최상위 트랜잭션으로 만들어진 컨트랙트(`c12_creations`, 교차 점검만) |
| `29_c12_rpc_queue.sql` | RPC로 코드를 읽을 대기열 K와 들어간 이유(`c12_rpc_queue`): 트랜잭션을 보내지 않았고, 트랜잭션 송신자도 영 주소도 아닌 상대가 있는 E(시스템 주소도 빼지 않음; 노드 집합에서는 31이 뺌), 12개월 코호트와 스펜더 전원, 감사 표본 두 개 |
| `31_c12_contracts.sql` | 노드 집합(`c12_contracts`), 사용자 계정과 그 출처(`c12_user_accounts`), 양 끝이 컨트랙트인 사건(`c12_events_cc`). 시스템 주소(0x…01–0x…ff)는 노드 집합에 넣지 않고, 트랜잭션을 보낸 적이 없으면 사용자 계정에도 넣지 않음. 2026-11-09 개정(수정 문서 13절): 판별에서 컨트랙트로 나왔지만 목록(`common.SMART_ACCOUNT_CODE_HASHES`, `SMART_ACCOUNT_IMPLEMENTATIONS`; 드라이버가 `@ext_code_hashes`, `@ext_pairs`로 넘김)에 든 주소는 스마트 계정으로 봄 |
| `32_c12_bal_pre.sql` | 잔액 모집단(2025-04-01 ~ T_obs의 승인 주인과 토큰)의 2023-10-01 전 순유입, 공개 로그에서(`c12_bal_pre`) |
| `33_c12_bal.sql` | t1, T_obs, 2026-09-30의 잔액과 기간별 송금 수(`c12_bal`, 기초 단위, 자르지 않음) |
| `34_c12_anchor_blocks.sql` | 기준 시점마다 그 시각 이전의 마지막 블록(`c12_anchor_blocks`, 하루 파티션만 읽음) |
| `43_c12_bal_audit.sql` | 잔액 점검 표본: 토큰마다 T_obs 잔액이 0인 쌍과 양인 쌍 150개씩(`c12_bal_audit`, `../scripts/balance_audit.py`가 `balanceOf`와 대조) |
| `35_c12_structure.sql` | t1의 구조 파일럿 입력: 층마다(잔액으로 자른 허락, 자르지 않은 허락, 송금) 컨트랙트 쌍, 가중치 없이(`c12_struct_t1`) |

## 컨트랙트 그래프 수정(게이트 B)

발견 순서 프로토콜(`../docs/discovery_protocol.md`)에 'Protocol fixed'가 적히고 이 파일들이 커밋된 뒤에 돌리는 단계입니다. 단계는 `constants`(36), `pairs`(37), `rest`(38–41), `checks`(42), `download` 순서이고, 36에는 작업이 셋, 38에는 둘 있습니다. 허락, 간선, 중요도는 두 동결(t1, T_obs)을 한 문장에서 함께 만들어 `tag` 열('t1', 'tobs')로 나누고, 40과 41이 동결마다 내려받을 표로 나눕니다. `c12_logs5`는 36의 사용자 계정 사건에서만, `c12_events_cc`는 36(허락, 상수), 37, 38(지표)에서만 읽습니다. 라벨은 12개월 변형의 `u12_labels_w0`, `u12_labels_w1`을 바꾸지 않고 씁니다(39는 나누려고 다시 셀 뿐입니다).

| 파일 | 하는 일 |
|---|---|
| `36_c12_allow_triples.sql` | 두 동결마다 점수 기간에서 기준 시점까지 컨트랙트끼리의 (토큰, 주인, 스펜더)별 양의 최신 허락(`c12_allow_triples`): 기준일 가격의 USD(`usd_allow`)와, 주인의 기준 시점 잔액까지로 자른 값(`usd_eff`; 10⁻⁶ 토큰 미만의 잔액은 0). 상수가 필요 없어 상수보다 먼저 만듭니다. t1 쪽은 35와 같은 조건이라 구조 파일럿의 쌍을 그대로 냅니다. |
| `36_c12_user_events.sql` | 두 점수 기간(2025-04-01 ~ T_obs)에 사용자 계정이 컨트랙트에 보낸 승인과 USD 송금, 그리고 타입을 읽지 않은 E의 주소(대기열 K 밖이고 트랜잭션을 보낸 적 없음)에 보낸 USD 송금(`c12_user_events`). U_user와 중요도(41)가 이 테이블을 읽으므로, 게이트 B에서 `c12_logs5`를 읽는 작업은 이것 하나입니다. |
| `36_c12_constants.sql` | W0 점수 기간의 상수(`c12_constants`): 컨트랙트끼리의 송금 USD의 중앙값과 99분위수(U), t1의 양의 `usd_eff` 중앙값(무제한 허락 포함), 사용자 계정이 컨트랙트에 보낸 송금의 99분위수(U_user). 드라이버가 유효숫자 두 자리로 반올림해 `../data/0-usd-token-list-and-prices/contract-12m/constants.json`에 씁니다. |
| `37_c12_pairs.sql` | 두 동결의 간선 집계, 14의 정의 그대로: 송금 쌍(`c12_transfer_pairs`), 잔액으로 자른 허락 쌍(`c12_allow_pairs`, `usd_eff`가 양인 토큰만), 자르지 않은 허락 쌍(`c12_allow_pairs_unc`, 민감도 분석용). 자기 쌍과 가중치가 0인 쌍도 남깁니다. |
| `38_c12_cohorts.sql` | 12개월 코호트에서 사용자 계정을 뺀 코호트(`c12_cohort_tobs`, `c12_cohort_t1`)와, 네 목록(두 코호트, W0·W1 스펜더)의 구성원과 그 종류(`c12_members`: 컨트랙트, 사용자 계정, 시스템 주소, 타입 없음) |
| `38_c12_proxies.sql` | T_obs 컨트랙트 코호트의 같은 기간 지표(`c12_proxies_tobs`): 15의 송금 지표와 Sybil 안정성 지표를 컨트랙트끼리의 송금으로 셉니다. 허락 지표는 잔액으로 자른 그래프에서 로컬로 셉니다. |
| `39_c12_label_parts.sql` | W0·W1 라벨(`u12_labels_*`)을 같은 입력과 16의 정의로 다시 세고, 라벨마다 센 계정을 사용자 계정, 컨트랙트, 그 밖(민트의 영 주소, 시스템 주소, 타입 없음)으로 나눕니다(`c12_label_parts_*`, 내려받는 `c12_x_label_split_*`). 규칙 밖의 보조 기술이고, `__TAG__`를 w0과 w1로 바꿔 두 번 돌립니다. |
| `40_c12_export_ids.sql` | 두 동결에 하나인 노드 번호(`c12_nodes`: 어느 동결에서든 쌍의 끝이거나 네 목록의 컨트랙트 구성원인 컨트랙트, 주소 순)와 내려받을 간선표, 구성원 표(`c12_x_*`) |
| `41_c12_importance.sql` | 발견 순서 시험의 중요도(`c12_importance_raw`, 내려받는 `c12_importance_tobs`, `c12_importance_t1`): 컨트랙트마다 사용자 계정의 송금(I_T)과 잔액으로 자른 허락(I_A)을 계정마다 U_user까지로 잘라 더한 값과, USD 1 이상인 계정 수(N_T, N_A). `c12_nodes`에 없는 컨트랙트의 번호는 −1입니다. 타입을 읽지 않은 주소로 간 USD의 합(`c12_inflow_untyped_*`, 자르지 않음)과 허락의 토큰별 기술 통계(`c12_describe_allowances`)도 만듭니다. |
| `42_c12_checks.sql` | 게이트 B 테이블의 불변식 64개(`c12_checks`, 모두 0이어야 함): 노드와 쌍의 끝이 모두 컨트랙트이고 사용자 계정이 없음, 자른 가중치가 자르지 않은 가중치 이하, t1 쌍이 구조 파일럿(`c12_struct_t1`)과 같음, 다시 센 라벨이 `u12_labels_*`와 같고 나눈 부분의 합이 라벨, 중요도가 컨트랙트와 동결마다 한 행 |
