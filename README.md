# Integrating ERC-20 Allowance Edges into PageRank for Enhanced On-Chain Wallet Reputation Scoring

학위논문 작업 폴더입니다. 폴더 이름 `ERC20-Allowance-PageRank-Wallet-Reputation`은 이 제목을 줄인 것입니다(전체 제목을 쓰면 Windows 경로 길이 제한 260자를 넘음).

2026-10-11부터 이 폴더의 논문은 **컨트랙트 평판 연구**입니다. 점수를 매기고 평가하는 대상은 스마트 컨트랙트뿐이고, 일반 지갑(EOA)은 허락·송금 간선의 출발점과 도착점으로만 그래프에 들어갑니다. 데이터는 Arbitrum One의 2023-10-01부터 2026-09-30까지 3년입니다. 이 연구는 2026-10-09에 `1-Dissertation-Works/ERC20-Allowance-PageRank-Contract-Reputation/`에서 시작했고, 2026-10-11에 이 폴더로 옮겼습니다. 논문 제목은 승인된 연구계획서의 제목을 그대로 씁니다.

| 폴더 | 내용 |
|------|------|
| `proposal/` | 연구계획서(승인·고정): LaTeX 정본, 교수·심사위원 피드백, 발표 자료, DOCX 도구. 명시적인 요청 없이는 고치지 않습니다 |
| `dissertation/overleaf-github/` | 논문 원고(영문, UNISA 양식 LaTeX). 서브모듈 `phd-dissertation-draft-en`(Overleaf가 `main`을 읽음). 투고 원고 `manuscripts/`와 보조 분석 `analysis/`도 이 저장소에 있습니다 |
| `dissertation/overleaf-github-ko/` | 원고를 쉬운 한국어로 옮긴 번역본(LaTeX, `main.pdf`) |
| `dissertation/presentation/` | 학위논문 발표 자료(한국어 HTML 슬라이드 59장: 3D 데이터 시각화, 중학생 눈높이의 수식 유도, 모션 그래픽). `index.html`을 브라우저로 열면 오프라인에서도 돌아갑니다. [`README.md`](dissertation/presentation/README.md) 참고 |
| `dissertation/notes/` | 원고를 쓸 때 지키는 규칙과 메모(`_writing-brief.md`, `_claims.md`, `_revision-context.md`, `_todo.md`). 빌드에 들어가지 않습니다 |
| `experiments/` | BigQuery 추출, 점수 계산, 평가 코드와 데이터 |
| `archive/` | 2026-10-11 이전의 지갑 평판 연구 자료(실험 코드와 데이터, 한국어판, 로컬 원고 자료, 어린이 책·오디오북, 피드백 정리). [`archive/README.md`](archive/README.md) 참고 |

## 기간

| 구간 | 날짜 | 쓰임 |
|------|------|------|
| 관측 기간 | 2023-10-01 ~ 2026-06-30 | 같은 기간 정렬, 벤치마크, 강건성 |
| 홀드아웃 W0 | 2026-03-31 동결, 4~6월 라벨 | 스펜더 홀드아웃, 규칙 A |
| 등록 재현 W1 | 2026-06-30 동결, 7~9월 라벨 | 등록 파일을 커밋한 뒤에 7~9월 로그를 추출 |

## 두 분석: 등록 분석과 수정 분석

| | 등록 분석 | 수정 분석 (논문의 주 결과) |
|---|---|---|
| 금액 | 원시 base unit, b = 1 | USD (DefiLlama 일별 종가), b = ln3/m (m_T = $200, m_A = $62) |
| 토큰 | 모든 ERC-20 | WETH, USDC, USDT0, ARB, WBTC (Chainlink low·medium 규칙을 통과하고 가격이 있는 46개 중 행 수 상위 5개) |
| 코호트 | 27,844 | 15,107 (등록 코호트의 부분집합) |
| C-PR 승인 층 | 원시 합 | min(USD, $20,000) 합 |
| 고정 시점 | 계획 43d8045, W1 등록 0d3a057 (모두 결과 전) | 수정 계획 a897475·09dfc32·2705b28 (2026-10-10, 등록 결과를 본 뒤, 수정 점수 계산 전) |
| 결과 | `experiments/data/3-published-results-for-thesis/` | `.../3-published-results-for-thesis/revised-usd/` |
| 실행 | `CONTRACT_REP_VARIANT` 없이 | `CONTRACT_REP_VARIANT=usd` (`scripts/run_usd_pipeline.py`, `scripts/run_usd_local.ps1`) |

수정 분석은 등록 이후의 이탈(deviation)이라 그 결과를 '등록된 결과'라고 부르지 않습니다. 이유와 규칙은 `experiments/docs/revision_price_weighting.md`에 있습니다. 토큰 목록과 가격은 `experiments/data/0-usd-token-list-and-prices/`에 있습니다.

## 결과 한눈에

- 원고: `dissertation/overleaf-github/main.pdf` (수정 분석이 주 결과). 빌드는 `dissertation/overleaf-github/`에서 xelatex → biber → xelatex 두 번(`build.ps1`)이며, MiKTeX에서는 PATH를 `/c/Program Files/MiKTeX/miktex/bin/x64:/c/Windows/System32:/c/Windows:/usr/bin`으로 줄여야 biber와 xelatex가 돕니다.
- 한국어판: `dissertation/overleaf-github-ko/main.pdf`.
- 수치: `experiments/data/3-published-results-for-thesis/results_digest.md` (모든 수치와 그 JSON 경로), `SHA256SUMS.txt`.
- 사전 고정: 분석 계획 `43d8045`(2026-10-09 13:41 UTC, 1차 추출 10초 전), W1 등록 `0d3a057`(같은 날 16:49 UTC, 2차 추출 8초 전).
- BigQuery 비용: 등록 분석 USD 29.71, 수정 분석을 더해 USD 34.80 (`experiments/data/bq_ledger.json`).

## 표와 그림 다시 만들기

논문의 결과 표(`results/tables/*.tex`)와 그래프(`Figures/generated/*.pdf`)는 손으로 고치지 않고 `experiments/`에서 다시 만듭니다. `scripts/export_latex.py`는 서브모듈 `dissertation/overleaf-github/`에 씁니다.

```bash
cd experiments
CONTRACT_REP_VARIANT=usd python scripts/export_latex.py
```

서브모듈이 비어 있으면 저장소 최상위에서 `git submodule update --init`을 먼저 실행합니다.

## 데이터

| 위치 | 내용 | GitHub |
|------|------|--------|
| `experiments/data/1-raw-blockchain-extracts/cohort`, `gmx` | 코호트 후보, 계정 종류 판정(eth_getCode), GMX 청산 원본 | 올림 |
| `experiments/data/1-raw-blockchain-extracts/graph-tables/*.parquet` | 노드 번호표, 두 기준 시점의 허락·송금 간선표, 상위 토큰 간선표, 검증 지표, 라벨 (6.4 GB) | **올리지 않음** (`.json` 기록만 올림) |
| `experiments/data/1-raw-blockchain-extracts/graph-tables-usd/*.parquet` | 수정 분석의 같은 표(`u_x_*`, `u_proxies_tobs`, `u_labels_*`, `u_cohort`) | **올리지 않음** (`.json` 기록만 올림) |
| `experiments/data/0-usd-token-list-and-prices` | 토큰 후보·목록, 일별 USD 가격, 상수, Chainlink 대조 | 올림 |
| `experiments/data/2-processed-tables-and-evaluations` | 점수, 평가 요약 JSON, 해독한 GMX 청산 | 올림 |
| `experiments/data/3-published-results-for-thesis` | 논문 표의 근거 요약과 SHA-256 목록 | 올림 |

그래프 표는 BigQuery 프로젝트 `dissertation-bq`의 `contract_rep` 데이터셋에 남아 있습니다. 다시 받으려면 `experiments/`에서 다음을 실행합니다(쿼리 비용 없음, Storage Read API).

```bash
bash scripts/download_graph_tables.sh
```

상위 토큰 간선표(`top_token_pairs`)와 W1 라벨(`labels_w1`)은 `python scripts/download_table.py contract_rep.x_top_token_pairs data/1-raw-blockchain-extracts/graph-tables/top_token_pairs`처럼 따로 받습니다. 모든 파일은 90 MB 아래로 나뉩니다.

## 지킬 것

- 분석 계획(`experiments/docs/analysis_plan.md`)과 설정(`experiments/config/contract_reputation.yaml`)은 추출 전에 커밋했습니다. 1~6절을 고치지 않습니다.
- `data/` 아래 파일은 모두 90 MB 아래로 나눠 저장합니다(GitHub 100 MB 한도).
- BigQuery 비용은 `experiments/data/bq_ledger.json`에 쌓이며 전체 상한은 USD 50입니다.
- 테스트 `experiments/tests/`는 옛 실험 코드(`archive/wallet-reputation-experiments/scripts/`)를 읽기 전용 기준으로 불러옵니다. 그 폴더를 옮기거나 지우지 않습니다.
- 원고 문장 규칙은 `dissertation/notes/_writing-brief.md`를 따릅니다.
