# 1-raw-blockchain-extracts

BigQuery에서 받은 원시 표입니다. 표 하나는 90 MB 아래 parquet 조각과 `.json` 기록(원래 BigQuery 테이블, 행 수, 조각 목록, 받은 시각)으로 저장합니다. GitHub에는 `.json` 기록과 작은 파일만 있고, parquet은 공개 Google Drive에 있습니다.

| 폴더 | 내용 | 만드는 곳 |
|---|---|---|
| `cohort/` | 코호트 후보(`spender_candidates`), 후보의 계정 종류(`candidate_account_types`), 홀드아웃 스펜더의 계정 종류(`holdout_spender_types`) | `sql/02`, `check_account_code.py` |
| `gmx/` | GMX V2 계정(`gmx_accounts_obs`), 계정 종류(`gmx_account_types`, `_w1`), 컨트랙트 계정의 종료 로그(`gmx_contract_closes_obs`, `_w1`) | `sql/07`, `sql/09`, `check_account_code.py` |
| `graph-tables/` | 등록 분석(원시 단위)의 표, 6.4 GB: 노드 번호표(`nodes`), 두 기준 시점(`tobs`, `t1`)의 허락·송금 간선표(`allow_pairs_*`, `transfer_pairs_*`), 같은 기간 지표(`proxies_tobs`), 홀드아웃 라벨(`labels_w0`, `labels_w1`), 상위 토큰 간선표(`top_token_pairs`, `top_tokens.csv`) | `sql/04`–`08`, `sql/11`, `download_graph_tables.sh` |
| `graph-tables-usd/` | 수정 분석(USD, 다섯 토큰)의 같은 표, 2.6 GB, 그리고 수정 코호트(`cohort`) | `sql/12`–`17`, `run_usd_pipeline.py download` |
| `exploratory-2026-10-13/` | 사후 점검의 표: 무제한 허락을 뺀 간선표(`x_unl_pairs_*`)와 무제한 허락만의 간선표(`x_unlonly_pairs_*`), 허락 종류별 새 승인 라벨(`x_unl_labels_*`), 잔액을 붙인 USD 간선표(`x_usd_pairs_*`), 잔액 대조 표본(`x_bal_check`) | `../../exploratory/2026-10-13-unlimited-allowances/` |
| `exploratory-2026-10-14/` | 사후 점검의 표: 시간 가중 없는 허락 쌍(`x_nodecay_pairs_*`) | `../../exploratory/2026-10-14-freeze-date-time-weight/` |

`graph-tables-usd/`의 BigQuery 테이블 이름은 `u_x_*`, `u_proxies_tobs`, `u_labels_*`, `u_cohort`처럼 `u_`로 시작합니다.
