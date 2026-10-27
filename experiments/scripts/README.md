# scripts

실험 스크립트입니다. 모두 `experiments/`에서 실행합니다. 경로와 설정은 `common.py`가 정하고, 환경 변수 `CONTRACT_REP_VARIANT=usd`이면 수정 분석의 경로(`graph-tables-usd/`, `revised-usd/`)를 씁니다. 실행 순서는 [`../README.md`](../README.md)의 「실행」에 있습니다.

## BigQuery와 데이터 받기

| 파일 | 하는 일 |
|---|---|
| `run_bq.py` | SQL 파일 하나를 dry run으로 비용을 본 뒤 실행하고, 청구된 바이트를 `data/bq_ledger.json`에 적습니다. 남은 예산을 넘는 작업은 `--force` 없이는 거부합니다. |
| `download_table.py` | 프로젝트 BigQuery 테이블을 Storage Read API로 받아 90 MB 아래 parquet 조각과 `.json` 기록으로 저장합니다. 쿼리를 돌리지 않아 스캔 비용이 없습니다. |
| `download_graph_tables.sh` | 등록 분석의 그래프 표를 `data/1-raw-blockchain-extracts/graph-tables/`로 받습니다(sql/04–08을 돌린 뒤). |
| `run_usd_pipeline.py` | 수정 분석의 BigQuery 단계를 순서대로 돌립니다: load, ego, constants, pairs, rest, download. |
| `extract_w1.py` | 7~9월 로그를 추출합니다(scan B). W1 등록 파일과 설정이 바뀐 것 없이 커밋되어 있어야 돌아가고, 두 파일의 SHA-256과 커밋을 `registered-w1/extraction_manifest.json`에 적습니다. |
| `drive_sync.py` | 공개 Google Drive 폴더와 로컬 데이터를 맞춥니다(status, pull, push). |

## 코호트, 계정, 토큰, 가격

| 파일 | 하는 일 |
|---|---|
| `check_account_code.py` | Arbitrum RPC의 `eth_getCode`로 계정 종류를 판정합니다. 바이트코드가 있으면 컨트랙트, 없거나 EIP-7702 위임 표시이면 EOA입니다. 한 블록에서 읽고 그 블록을 기록합니다. |
| `build_cohort.py` | 매칭 코호트(분석 계획 3절)를 정해 `data/2-.../cohort/`에 쓰고 BigQuery에 올립니다. |
| `decode_gmx_events.py` | GMX V2 `EventLog1` `PositionDecrease` 로그를 종료 한 건씩 해독합니다(계정, PnL, 주문 유형, 청산 여부, 크기, 방향). |
| `token_metadata.py` | ERC-20 토큰의 `symbol()`, `name()`, `decimals()`를 한 블록에서 읽습니다. |
| `usd_inputs.py` | 수정 분석의 토큰 목록과 일별 USD 가격을 만듭니다(`data/0-usd-token-list-and-prices/`). |
| `usd.py` | 수정 분석의 USD 금액 계산. SQL(sql/12–18)과 같은 산술을 파이썬으로 적은 것이고, 테스트가 확인합니다. |
| `chainlink_check.py` | DefiLlama 일별 가격을 Arbitrum One의 Chainlink 피드 값과 대조합니다. |

## 점수와 평가

| 파일 | 하는 일 |
|---|---|
| `common.py` | 설정, 경로, GitHub 크기 제한 아래로 나눈 parquet 조각 |
| `scoring.py` | 가중 PageRank, 결합 보행과 시드 보행, AWP와 EndorseRank의 간선 가중치 |
| `graphs.py` | 간선표를 읽어 한 기준 시점의 모든 점수를 계산합니다. 결과 요약과 표에 쓰는 방법 id(endorserank, awp, cpr_l50 등)가 여기서 정해집니다. |
| `labels.py` | GMX V2 종료로 만든 트레이더 라벨과 홀드아웃 실행의 공통 도우미 |
| `stats.py` | Kendall τ_b, Spearman ρ, 코호트 단위 짝지은 부트스트랩 |
| `run_same_window.py` | 관측 기간 안의 평가(분석 계획 4–6절)와 규칙 A의 2차 부분 |
| `run_holdout.py` | 홀드아웃 W0(t1 동결, 4~6월 라벨)과 규칙 A의 1차 부분 |
| `run_registered.py` | 등록 창 W1: 규칙 B, 보고할 결과, 어느 간선으로도 만들지 않은 결과와의 비교(등록 순서대로) |
| `run_supplementary.py` | 라벨을 본 뒤 계산한 대비. 어느 규칙에도 속하지 않습니다. |
| `run_robustness.py` | 강건성과 민감도: 상위 토큰 부분 그래프, 표본 정의 |
| `sybil_model.py` | Sybil 비용 모형(5장)의 양 |
| `run_benchmark.py` | 계산 벤치마크(주장 C1)와 규모 확장 |
| `describe_data.py` | 추출한 데이터의 기술 통계(3·4장, 부록 8.4) |
| `run_usd_local.ps1` | 수정 분석의 로컬 평가를 등록 분석과 같은 순서로 돌립니다. |

## 결과 공개와 원고

| 파일 | 하는 일 |
|---|---|
| `publish_results.py` | 논문이 인용하는 요약, 설정, 계획 문서를 `data/3-published-results-for-thesis/`에 복사하고 `results_digest.md`(모든 수치와 그 JSON 키)와 `SHA256SUMS.txt`를 씁니다. |
| `export_latex.py` | 평가 요약 JSON으로 원고의 LaTeX 표와 그림을 서브모듈 `../dissertation/overleaf-github/`에 씁니다. 점수나 통계를 새로 계산하지 않습니다. |
