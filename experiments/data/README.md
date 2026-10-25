# data

실험 데이터입니다. 폴더 번호는 흐름의 순서입니다: 0 입력, 1 BigQuery에서 받은 원시 표, 2 점수와 평가, 3 논문이 인용하는 결과.

parquet은 GitHub에 없고 공개 Google Drive 폴더에만 있습니다. 받는 법은 [`../README.md`](../README.md)의 「데이터」에 있습니다. 큰 표는 90 MB 아래 조각(`<표>.part000.parquet`, ...)으로 나누고, 옆의 `<표>.json`에 원래 BigQuery 테이블, 행 수, 조각 목록을 적습니다. json·csv·md 같은 작은 파일은 GitHub와 Drive 양쪽에 있습니다.

| 경로 | 내용 | 만드는 곳 |
|---|---|---|
| `0-gmx-abi-for-decoding-logs/EventEmitter.json` | GMX V2 EventEmitter의 ABI. 종료 로그를 해독할 때 씀 | 받은 파일 |
| [`0-usd-token-list-and-prices/`](0-usd-token-list-and-prices/) | 수정 분석의 토큰 목록, 일별 USD 가격, 상수, Chainlink 대조 | `usd_inputs.py`, `run_usd_pipeline.py`, `chainlink_check.py` |
| [`1-raw-blockchain-extracts/`](1-raw-blockchain-extracts/) | BigQuery에서 받은 원시 표: 코호트, GMX, 그래프 표 | `download_table.py` 등 |
| [`2-processed-tables-and-evaluations/`](2-processed-tables-and-evaluations/) | 점수, 평가 요약, 해독한 GMX 종료 | `run_*.py` 등 |
| `3-published-results-for-thesis/` | 논문이 인용하는 결과(아래) | `publish_results.py` |
| `bq_ledger.json` | BigQuery 작업마다 시각, SQL, 대상, 청구 바이트, 비용(USD) | `run_bq.py` |

`_work/`(검증용 임시 다운로드)는 어디에도 올리지 않습니다.

## 3-published-results-for-thesis

논문이 인용하는 요약을 고정해 둔 곳입니다. `publish_results.py`만 이 폴더에 쓰고, 자기가 내보내지 않은 파일이 있으면 실행할 때마다 알립니다. 그래서 이 폴더 안에는 README를 두지 않고 여기서 설명합니다.

| 경로 | 내용 |
|---|---|
| `results_digest.md` | 등록 분석의 모든 수치와, 그 수치가 나온 JSON 파일과 키 |
| `SHA256SUMS.txt` | 이 폴더에 공개한 모든 파일의 SHA-256 |
| `same-window/`, `holdout-w0/`, `registered-w1/` | 같은 기간, 홀드아웃 W0, 등록 창 W1의 평가 요약(`eval_summary.json`)과 W1 추출 기록(`extraction_manifest.json`) |
| `sybil-model/`, `robustness/`, `benchmark/`, `supplementary/`, `describe/` | Sybil 비용 모형, 강건성, 벤치마크, 사후 대비, 기술 통계 |
| `cohort/`, `gmx/` | 매칭 코호트의 기록, 해독한 GMX 종료의 기록 |
| `config/`, `docs/` | 그때의 설정과 계획 문서 사본 |
| `revised-usd/` | 수정 분석(논문의 주 결과)의 같은 구성. 자체 `results_digest.md`와 `SHA256SUMS.txt`가 있고, W1 평가는 `window-w1/`, 토큰 목록·상수·가격 입력·Chainlink 대조는 `usd/`에 있습니다. `registered-w1/`에는 추출 기록만 있습니다. |
