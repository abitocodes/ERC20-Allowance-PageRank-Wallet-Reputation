# experiments

학위논문의 실험 코드와 데이터입니다. BigQuery에서 Arbitrum One 로그를 받아 허락·송금 그래프를 만들고, 점수를 계산해 평가한 뒤, 원고의 표와 그림을 만듭니다. 무엇을 왜 재는지는 학위논문 폴더의 [`README.md`](../README.md)에 있습니다.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="../../../.github/readme/code-to-manuscript-dark.png">
  <img alt="코드에서 원고까지: BigQuery 공개 로그, 원시 표(공개 Google Drive와 주고받음), 분석 계획을 따르는 점수와 평가, 평가 요약을 거쳐 export_latex.py가 원고의 표와 그림을, publish_results.py가 수치 요약을 만듦" src="../../../.github/readme/code-to-manuscript-light.png" width="880">
</picture>

도식의 `data/`, `scripts/`, `docs/`, `config/`는 이 폴더 아래에 있고, 표·그림·PDF·투고 원고는 원고 서브모듈(`../dissertation/overleaf-github/`)에 있습니다.

## 폴더

| 경로 | 내용 |
|---|---|
| [`config/contract_reputation.yaml`](config/contract_reputation.yaml) | 결과를 정하는 설정(체인, BigQuery, 기간, 코호트, 점수와 평가의 매개변수, 비용 상한). 이 연구의 첫 추출 전에 분석 계획과 함께 커밋했습니다. |
| [`config/overlay_usd12m.yaml`](config/overlay_usd12m.yaml) | 12개월 변형이 위 설정에 덮어쓰는 두 기간 시작(`period.start_ts`, `holdout.start_ts`). 다른 키가 있으면 `common.py`가 거부합니다. |
| [`docs/`](docs/) | 분석 계획, W1 등록, 수정 계획, 12개월 수정, Drive 폴더의 안내문 |
| [`sql/`](sql/) | BigQuery 쿼리 23개. 01–11은 등록 분석, 12–19는 수정 분석, 20–23은 12개월 변형 |
| [`scripts/`](scripts/) | 추출, 점수, 평가, 결과 공개, 원고 내보내기 스크립트 |
| [`tests/`](tests/) | pytest. 점수와 통계를 보관한 지갑 평판 연구의 기준 구현과 대조합니다. |
| [`data/`](data/) | 데이터. parquet은 Drive에만 있고, 작은 파일은 GitHub에도 있습니다. |
| [`exploratory/`](exploratory/) | 모든 결과를 본 뒤에 한 사후 점검 다섯 가지 |
| `drive-manifest.json` | Drive에 있는 모든 파일의 Drive id·크기·MD5와 폴더 링크(`folder_url`) |

## 실행

두 분석은 같은 코드를 씁니다. 환경 변수 `CONTRACT_REP_VARIANT`가 없으면 등록 분석(원시 단위, 모든 토큰)이고, `CONTRACT_REP_VARIANT=usd`이면 수정 분석(USD, 다섯 토큰)입니다. 수정 분석은 `data/1-raw-blockchain-extracts/graph-tables-usd/`를 읽고 결과를 `revised-usd/` 아래에 씁니다.

수정 분석(논문의 주 결과)을 처음부터 다시 만드는 순서입니다. 명령은 모두 이 폴더에서 실행합니다.

1. `python scripts/run_usd_pipeline.py load ego constants pairs rest download`: BigQuery 단계. 쿼리마다 `run_bq.py`가 먼저 dry run으로 비용을 보고, 실행한 뒤 `data/bq_ledger.json`에 적습니다. 비용이 듭니다(아래 「데이터 정책」).
2. `scripts/run_usd_local.ps1`: 로컬 평가. run_same_window, run_holdout, run_registered, run_supplementary, run_robustness, sybil_model, describe_data, run_benchmark 순서로 돌립니다.
3. `CONTRACT_REP_VARIANT=usd python scripts/publish_results.py`: 논문이 인용하는 요약을 `data/3-published-results-for-thesis/revised-usd/`에 복사하고 `results_digest.md`와 `SHA256SUMS.txt`를 씁니다.
4. `CONTRACT_REP_VARIANT=usd python scripts/export_latex.py`: 원고의 표와 그림을 씁니다(아래 「표와 그림 다시 만들기」).

### 12개월 변형

`CONTRACT_REP_VARIANT=usd12m`은 같은 USD 수정 분석을 동결마다 직전 12개월(T_obs·W1 2025-07-01 ~ 2026-06-30, W0 2025-04-01 ~ 2026-03-31)로 계산합니다(`docs/revision_one_year_window.md`). 이 수정 문서 2절에 따라 학위논문의 주 분석이 되고, 원고를 12개월 수치로 다시 쓰기 전까지 원고의 표는 위 33개월 수정 분석의 것입니다. 입력은 `data/1-raw-blockchain-extracts/graph-tables-usd-12m/`, 결과는 `revised-usd-12m/` 아래와 `data/0-usd-token-list-and-prices/usd-12m/`입니다.

1. `python scripts/run_usd12m_pipeline.py check`: 무료 점검과 작업별 비용 추정(약 USD 2.7, 상한 USD 4.00).
2. `python scripts/run_usd12m_pipeline.py tokens cohorts constants`, 그다음 `pairs rest checks download`: BigQuery 단계. 수정 문서, 오버레이, SQL이 커밋되어 있어야 돌아갑니다.
3. `scripts/run_usd_local.ps1 -Variant usd12m`: 로컬 평가.
4. `CONTRACT_REP_VARIANT=usd12m python scripts/publish_results.py`: `data/3-published-results-for-thesis/revised-usd-12m/`에 요약을 냅니다.
5. `CONTRACT_REP_VARIANT=usd12m python scripts/export_latex.py`: 표와 그림을 `data/_work/latex-usd12m/`에 씁니다. 원고에는 `--into-manuscript`를 붙일 때만 씁니다.

등록 분석은 같은 스크립트를 `CONTRACT_REP_VARIANT` 없이 돌립니다. 7~9월 로그는 `scripts/extract_w1.py`만 추출하고, 이 스크립트는 W1 등록 파일과 설정이 커밋되어 있어야 돌아갑니다. 테스트는 `python -m pytest tests`로 돌립니다.

## 표와 그림 다시 만들기

논문의 결과 표(`results/tables/*.tex`)와 그래프(`Figures/generated/*.pdf`)는 손으로 고치지 않고 이 폴더에서 다시 만듭니다. `scripts/export_latex.py`는 서브모듈 `../dissertation/overleaf-github/`에 씁니다.

```bash
CONTRACT_REP_VARIANT=usd python scripts/export_latex.py
```

서브모듈이 비어 있으면 저장소 최상위에서 `git submodule update --init`을 먼저 실행합니다.

## 데이터

parquet 데이터는 GitHub에 올리지 않고 공개 Google Drive 폴더 `phd_works-blockchain-data`(링크가 있으면 누구나 읽기)에 둡니다. json·csv·md 같은 작은 파일은 GitHub와 Drive 양쪽에 있습니다. Drive에 있는 모든 파일의 Drive id·크기·MD5는 `drive-manifest.json`(커밋됨)에 있고, 폴더 링크도 거기 `folder_url`에 있습니다. 폴더마다의 내용은 [`data/README.md`](data/README.md)에 있습니다.

| 위치 | 내용 | GitHub | Drive |
|------|------|--------|-------|
| `data/1-raw-blockchain-extracts/cohort`, `gmx` | 코호트 후보, 계정 종류 판정(eth_getCode), GMX 청산 원본 | 작은 파일만 | 전부 |
| `data/1-raw-blockchain-extracts/graph-tables/` | 노드 번호표, 두 기준 시점의 허락·송금 간선표, 상위 토큰 간선표, 검증 지표, 라벨 (6.4 GB) | `.json` 기록만 | 전부 |
| `data/1-raw-blockchain-extracts/graph-tables-usd/` | 수정 분석의 같은 표(`u_x_*`, `u_proxies_tobs`, `u_labels_*`, `u_cohort`, 2.6 GB) | `.json` 기록만 | 전부 |
| `data/0-usd-token-list-and-prices` | 토큰 후보·목록, 일별 USD 가격, 상수, Chainlink 대조 | 올림 | 전부 |
| `data/2-processed-tables-and-evaluations` | 점수, 평가 요약 JSON, 해독한 GMX 청산 | 작은 파일만 | 전부 |
| `data/3-published-results-for-thesis` | 논문 표의 근거 요약과 SHA-256 목록 | 올림 | 전부 |
| `../archive/wallet-reputation-experiments/data` | 지갑 평판 연구(보관) 데이터 | 작은 파일만 | 전부 |

`data/_work/`(검증용 임시 다운로드)는 어디에도 올리지 않습니다.

### Drive에서 받기

이 폴더에서 필요한 파일만 받습니다. 패턴은 Drive 경로(`contract-reputation/...`)나 학위논문 폴더 기준 경로에 맞춘 glob입니다. 받은 파일은 MD5를 확인합니다.

```bash
python scripts/drive_sync.py pull "*graph-tables-usd/*"   # 수정 분석(주 결과)의 그래프 표
python scripts/drive_sync.py pull "experiments/*"         # 이 논문의 데이터 전부
python scripts/drive_sync.py pull --all                   # 보관 데이터까지 전부(약 10 GB)
python scripts/drive_sync.py status                       # 로컬과 Drive의 차이
```

rclone 리모트가 있으면 rclone으로, 없으면 HTTPS로 받습니다(파이썬 표준 라이브러리만 씀). HTTPS는 환경 변수 `GDRIVE_API_KEY`가 있으면 `www.googleapis.com`을, 없으면 `drive.usercontent.google.com`을 씁니다. Claude Code 클라우드 환경 `Default`는 네트워크를 '사용자 지정'(기본 목록 포함)으로 두고 `drive.usercontent.google.com`을 더해 두었으므로(2026-10-12), 클라우드 세션에서도 키 없이 받습니다. 새 환경을 만들면 같은 도메인을 더합니다.

### Drive에 올리기

BigQuery에서 새로 받은 데이터는 `download_table.py`로 `data/` 아래에 받은 뒤 올립니다. 그래프 표를 BigQuery에서 다시 받는 방법은 `scripts/download_graph_tables.sh`와 `python scripts/download_table.py contract_rep.x_top_token_pairs data/1-raw-blockchain-extracts/graph-tables/top_token_pairs`입니다(쿼리 비용 없음, Storage Read API).

```bash
python scripts/drive_sync.py push --dry-run   # 올릴 파일 확인
python scripts/drive_sync.py push             # 올리고 drive-manifest.json 갱신
```

그다음 `drive-manifest.json`을 커밋합니다. push는 rclone 리모트 `phd-gdrive`(개인 Google 계정, 다른 이름은 `DRIVE_SYNC_REMOTE`)를 씁니다. rclone은 GCP 프로젝트 `dissertation-bq`의 데스크톱 OAuth 클라이언트 `rclone phd-gdrive`로 로그인합니다. 이 OAuth 앱(`ds-daq`)은 '테스트 중' 상태라 로그인이 7일마다 만료되므로, 오랜만에 push할 때는 먼저 `rclone config reconnect phd-gdrive:`로 브라우저에서 다시 허용합니다. 새 PC에서는 `winget install Rclone.Rclone` 뒤 `rclone config create phd-gdrive drive scope=drive client_id=... client_secret=...`(콘솔의 그 클라이언트 값)로 한 번 로그인합니다. push는 Drive의 파일을 지우지 않고, 이미 있는 파일은 `--allow-overwrite` 없이는 바꾸지 않습니다(논문이 인용하는 데이터라서).

`data/` 아래의 README도 작은 md 파일이라 Drive에 함께 올라갑니다. 새로 만든 README는 다음 push 전까지 `status`에 로컬에만 있는 파일로 나옵니다.

## 데이터 정책

| 항목 | 정책 |
|---|---|
| parquet | 공개 Google Drive 폴더에만 둡니다. json·csv·md 같은 작은 파일은 GitHub에도 올립니다. `data/` 아래 파일은 모두 90 MB 아래로 나눠 저장합니다. |
| 보관한 지갑 평판 데이터 | `../archive/wallet-reputation-experiments/data/`도 같은 규칙입니다. parquet은 Drive에만 둡니다. |
| Drive 폴더 | UNISA 학위논문에 쓴 데이터는 심사가 끝난 뒤에도 몇 달 동안 누구나 볼 수 있어야 합니다. Drive 폴더 `phd_works-blockchain-data`와 그 공유 설정(링크가 있는 모든 사용자 읽기)을 지우거나 바꾸지 않습니다. |
| 결과 표와 그림 | `scripts/export_latex.py`로 만듭니다. 손으로 고치지 않습니다. |
| BigQuery 비용 | `data/bq_ledger.json`에 쌓이며 전체 상한은 USD 50입니다. 2026-10-14까지 USD 39.76을 썼습니다(등록 분석 29.71, 수정 분석까지 34.80, 나머지는 사후 점검). |
| 고정한 파일 | `docs/analysis_plan.md`의 1~6절, `config/contract_reputation.yaml`, W1 등록 파일은 고치지 않습니다. |
| 커밋 | 스크립트, export한 표, 작은 데이터 파일을 커밋합니다. `.venv/`, parquet, 100 MB가 넘는 파일은 커밋하지 않습니다. |
