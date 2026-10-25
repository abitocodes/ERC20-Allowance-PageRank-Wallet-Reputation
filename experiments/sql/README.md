# sql

BigQuery 쿼리입니다. 직접 돌리지 않고 `../scripts/run_bq.py`(수정 분석은 `../scripts/run_usd_pipeline.py`)로 돌립니다. 그러면 매개변수(`@start_ts` 등)와 자리 표시자(`__TAG__` 등)를 채우고, dry run으로 비용을 먼저 본 뒤, 청구된 바이트를 `../data/bq_ledger.json`에 적습니다. 결과 테이블은 BigQuery 데이터셋 `dissertation-bq.contract_rep`에 생깁니다.

01–11은 등록 분석(원시 단위, 모든 토큰), 12–19는 수정 분석(USD, 다섯 토큰)입니다. 수정 분석의 쿼리는 등록 분석의 에고 테이블을 읽어 이름이 `u_`로 시작하는 새 테이블만 만들고, 등록 분석의 테이블은 바꾸지 않습니다.

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
