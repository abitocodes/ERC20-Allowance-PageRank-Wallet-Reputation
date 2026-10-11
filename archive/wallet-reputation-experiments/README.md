# wallet-reputation-experiments — 학위논문 실험 코드와 데이터

이 폴더는 학위논문 *Integrating ERC-20 Allowance Edges into PageRank for Enhanced On-Chain Wallet Reputation Scoring*의 실험을 담습니다. 4장과 부록의 숫자, 표, 그림은 모두 여기서 나옵니다.

하는 일은 네 가지입니다.

1. Arbitrum One 블록체인 기록(ERC-20 허락·송금, GMX 거래, Aave 대출)을 Google BigQuery에서 내려받습니다.
2. 지갑마다 평판 점수를 계산합니다. 이 논문이 제안한 EndorseRank, 송금 그래프 위의 AWP(원논문 그대로), 둘을 섞은 C-PR과 S-PR입니다.
3. 점수가 맞는지 시험합니다. 같은 기간의 검증 지표와 비교하고, 기준일 뒤에 실제로 일어난 일로 채점합니다(봄 홀드아웃, 6~8월 등록 재현).
4. 결과를 논문 표(LaTeX)와 그림으로 내보냅니다. 원고는 옆 폴더 `../overleaf-github/`에 있습니다.

2026년 10월 1일까지 이 폴더의 이름은 `A-Skill-Programs/margin_rank`였습니다. 그날 폴더 구성도 바꿨으니, 옛 이름은 `data/README.md` 끝의 대응표를 보세요.

## 한눈에 보기

```
wallet-reputation-experiments/
├── README.md          이 문서
├── requirements.txt   필요한 파이썬 패키지 목록
├── .gitignore         GitHub에 올리지 않는 파일(가상환경, 100 MB가 넘는 데이터 등)
├── config/            실험 설정과 등록 파일
├── data/              모든 데이터: 원본 → 가공 → 논문용 고정본 (data/README.md에 자세히)
├── docs/              설계 문서와 등록 계획서
├── scripts/           파이썬 코드
├── sql/               BigQuery에 보내는 질의문
└── tests/             자동 테스트
```

데이터는 이렇게 흐릅니다.

```
BigQuery ──extract_*.py──▶ data/1-raw-blockchain-logs/
         ──decode_*.py, preprocess_*.py──▶ data/2-processed-tables-and-evaluations/ (표)
         ──compute_*.py, run_*.py──▶ data/2-processed-tables-and-evaluations/ (점수, 평가 요약)
         ──publish_results.py──▶ data/3-published-results-for-thesis/
         ──export_latex_results.py──▶ ../overleaf-github/results/tables/*.tex
```

## config/ — 설정

| 파일 | 하는 일 |
|---|---|
| `margin_config.yaml` | 모든 실험 설정입니다. 관측 기간(2025-12-01 ~ 2026-05-31), GMX와 Aave 계약 주소, PageRank 값(감쇠 0.85, 허용 오차 1e-8, 최대 300회), AWP와 EndorseRank의 시간 감쇠와 값 가중치(`reputation.awp_paper.value_b`), C-PR의 λ와 2026-09-14에 미리 정한 성공 규칙(`reputation.hybrid`), 부트스트랩, 데이터 경로(`paths`)가 들어 있습니다. |
| `fresh_holdout_2026q3.yaml` | 6~8월 등록 재현의 등록 파일입니다. 2026-10-01 커밋 `4085ab9`에서 `status: registered`로 고정했고, 해시가 추출 기록에 남아 있으므로 **고치면 안 됩니다**. 안의 데이터 경로는 옛 폴더 이름이며, 코드가 `scripts/project_paths.py`의 대응표로 새 이름으로 바꿔 읽습니다. |

## data/ — 데이터

폴더와 파일마다의 설명은 [`data/README.md`](data/README.md)에 있습니다. 순서만 적으면 이렇습니다.

| 폴더 | 내용 |
|---|---|
| `0-gmx-abi-for-decoding-logs/` | GMX 기록을 해독하는 사전(ABI) |
| `1-raw-blockchain-logs/` | BigQuery에서 받은 원본 로그(12~5월 관측 기간, 6~8월 등록 재현) |
| `2-processed-tables-and-evaluations/` | 정리한 표, 지갑 점수, 평가 요약. 실행할 때마다 다시 써집니다. |
| `3-published-results-for-thesis/` | 논문 표의 근거가 되는 요약의 고정본과 SHA-256 목록 |
| `4-archived-extended-baselines/` | 본문에 쓰지 않은 확장 비교 실험 |

## docs/ — 문서

| 파일 | 내용 |
|---|---|
| `bigquery_data_plan.md` | BigQuery 추출 계획: 데이터 흐름, 쿼리당 비용 상한(150 GiB), 실행 순서 |
| `contract_wallet_exposure.md` | GMX에서 트레이더 지갑을 무엇으로 알아보는지(이벤트의 `account`, `tx.from`이 아님) |
| `fresh_holdout_2026q3_plan.md` | 6~8월 등록 재현 계획서(2026-09-28 작성). 등록 파일과 함께 고정되어 **고치면 안 됩니다**. |
| `research_log.md` | 연구 로그가 저장소 루트의 `.cursor/journey.md`로 옮겨졌다는 안내 |

## scripts/ — 코드

명령은 이 폴더에서 `python scripts/<이름>.py`로 실행합니다. 대부분 `--help`가 있습니다.

### 1. 데이터 가져오기 (Google Cloud 필요)

| 파일 | 하는 일 |
|---|---|
| `extract_margin_week.py` | 12~5월 GMX 포지션 마감 로그를 받습니다. `--merge-only`는 받아 둔 월별 파일을 큰 파일 하나로 합칩니다(해독 단계의 입력). |
| `extract_reputation_data.py` | 12~5월 ERC-20 허락·송금 로그를 받습니다. `--tier2`는 확장 지갑 풀용(중단된 시도). |
| `extract_aave_lending.py` | Aave V3 대출 로그를 받습니다. |
| `extract_fresh_window.py` | 6~8월 등록 재현 로그를 받습니다. 등록 파일이 커밋되어 있지 않으면 실행을 거부합니다. |
| `sample_active_wallets.py` | 확장 지갑 풀(99,080개)을 채울 활동 지갑을 뽑습니다. |
| `classify_spenders.py` | 스펜더가 로그를 남겼는지, 거래를 보냈는지로 계약과 사람 지갑을 나눕니다. |
| `check_spender_code.py` | Arbitrum 노드에 `eth_getCode`를 물어 스펜더에 코드가 있는지 확인합니다. |
| `bq_progress.py` | 도우미: BigQuery 진행 표시, 끊긴 다운로드 이어받기(`--resume`) |

### 2. 정리하기

| 파일 | 하는 일 |
|---|---|
| `decode_gmx_events.py` | GMX 로그를 해독해 `gmx_decoded_events.parquet`를 만듭니다(사전: `data/0-…`). |
| `preprocess_arbitrum_allowances.py` | (토큰, owner, spender)마다 가장 최근 허락만 남깁니다 → `latest_allowances.parquet` |
| `preprocess_arbitrum_transfers.py` | 송금 로그를 정리합니다 → `transfer_events.parquet` |
| `preprocess_aave_lending.py` | Aave 로그를 해독합니다 → `aave_events.parquet` |
| `preprocess_tier2_reputation.py` | 확장 풀 재추출분을 정리합니다. |

### 3. 점수 매기기

| 파일 | 하는 일 |
|---|---|
| `compute_rankings.py` | GMX 성적으로 매칭 코호트(거래를 3번 이상 닫은 5,521개 지갑)를 만듭니다 → `wallet_rankings.parquet` |
| `compute_reputation_ranks.py` | 방법마다 점수와 순위를 계산해 `wallet_rankings.parquet`에 붙입니다. |
| `pagerank.py` | 공통 PageRank 계산기, EndorseRank와 AWP 그래프(시간 가중치 σ와 값 가중치 V), C-PR이 쓰는 원금액 층 만들기 |
| `pagerank_variants.py` | C-PR, S-PR, 그리고 보관용 비교 방법들(GF-PR, LP-PR, CW-AWP, LF-PR, RiskProp, Aave 기반 방법) |

### 4. 시험하기

| 파일 | 하는 일 |
|---|---|
| `run_dissertation_eval.py` | 같은 기간 평가 전체: 순위 상관, 실행 시간, `--robustness` 강건성 → `eval_summary.json` |
| `evaluate_alignment.py` | 점수와 검증 지표 사이의 Kendall τ, Spearman ρ와 부트스트랩 구간 |
| `proxy_metrics.py` | 지갑마다 검증 지표(받은 송금, 받은 허락, 청산 비율, 손실 회피 등)를 계산합니다. |
| `benchmark_runtime.py` | 방법마다 실행 시간, 메모리, 반복 횟수를 잽니다. |
| `run_robustness_eval.py` | 감쇠 계수, 상위 토큰, 표본 크기를 바꿔 봅니다. |
| `refresh_alignment.py` | 실행 시간은 두고 순위 상관만 다시 계산합니다(2026-09-30 부호 수정 때 사용). |
| `holdout.py`, `run_holdout_eval.py` | 봄 홀드아웃: 2월 28일까지로 점수를 매기고 3~5월로 채점합니다. |
| `fresh_holdout.py`, `run_fresh_holdout.py` | 6~8월 등록 재현을 채점합니다. `--spring-check`는 같은 코드로 봄 결과를 재현하는지, `--fixtures`는 가짜 데이터로 코드가 도는지 확인합니다. |
| `run_supplementary_checks.py` | 결과를 본 뒤의 추가 점검: 동점 처리 규칙, 송금을 받아 본 스펜더만 남긴 봄 홀드아웃, 트레이더 수 |
| `run_fresh_posthoc.py` | 등록 재현이 끝난 뒤 6~8월 창에서 EndorseRank를 같은 코호트·라벨·재표본으로 채점합니다. 판정에는 들어가지 않습니다 → `posthoc_endorserank.json` |

### 5. 논문으로 내보내기

| 파일 | 하는 일 |
|---|---|
| `publish_results.py` | 논문 표의 근거 요약을 `data/3-published-results-for-thesis/`에 복사하고 SHA-256을 적습니다. `--check`로 사본이 맞는지 확인합니다. |
| `export_latex_results.py` | 요약 JSON을 `../overleaf-github/results/tables/*.tex`로 내보냅니다. |
| `export_method_matrix.py` | 보관용 비교 방법의 점수표를 `data/4-…`와 `../local-other/en-leftover/archive/`로 내보냅니다. |
| `generate_dissertation_figures.py` | 그림을 `../overleaf-github/Figures/generated/`에 그립니다. |

### 6. 원고 참고문헌 도우미 (`../overleaf-github`의 파일을 직접 고칩니다)

| 파일 | 하는 일 |
|---|---|
| `convert_citations_to_numbered.py` | 저자-연도 인용을 번호 인용으로 바꿉니다. |
| `renumber_citations.py`, `_cite_mapping.txt` | 인용 번호를 다시 매깁니다(옛 번호 → 새 번호 표). |
| `delete_bib_entries.py`, `_cite_mapping_delete.txt` | 참고문헌 항목을 지우고 번호를 다시 매깁니다. |
| `generate_bibentries.py` | `Config/bibentries.tex`를 만듭니다. |

### 7. 연습용 가짜 데이터

| 파일 | 하는 일 |
|---|---|
| `generate_synthetic_rankings.py`, `generate_synthetic_reputation.py`, `generate_synthetic_aave.py` | Google Cloud 없이 파이프라인을 시험할 가짜 GMX, 허락·송금, Aave 데이터를 만듭니다. |

### 8. 공통

| 파일 | 하는 일 |
|---|---|
| `common.py` | 설정 읽기, 주소 정리 같은 공통 함수 |
| `project_paths.py` | 폴더 이름을 한곳에 모은 파일. 옛 폴더 이름을 새 이름으로 바꾸는 표(`LEGACY_DIRS`)도 여기 있습니다. |
| `finish_folder_move.py` | 2026-10-01·2026-10-07 폴더 이동 뒤, 내 PC의 옛 폴더에 남은 파일을 새 위치로 옮기는 1회용 도구(아래 참고) |

## sql/ — BigQuery 질의문

| 파일 | 가져오는 것 |
|---|---|
| `gmx_event_logs.sql` | GMX V2 EventEmitter의 `PositionDecrease` 로그 |
| `arbitrum_approvals.sql` | 지갑 목록이 owner나 spender인 ERC-20 `Approval` 로그 |
| `arbitrum_transfers.sql` | 지갑 목록이 보내거나 받은 ERC-20 `Transfer` 로그 |
| `aave_lending_logs.sql` | 지갑 목록과 관련된 Aave V3 `Borrow`, `Repay`, `LiquidationCall` 로그 |
| `arbitrum_active_wallets.sql`, `arbitrum_active_wallets_month.sql` | 송금이 많은 활동 지갑(확장 지갑 풀용) |
| `arbitrum_account_activity.sql` | 주소가 로그를 남겼는지, 거래를 보냈는지(계약과 사람 지갑 구분) |

## tests/ — 자동 테스트

`python -m pytest -q`로 모두 돌립니다(BigQuery 없이 돕니다).

| 파일 | 확인하는 것 |
|---|---|
| `test_holdout.py` | 봄 홀드아웃의 라벨과 채점 |
| `test_fresh_holdout.py` | 등록 파일 내용, 6~8월 라벨, 판정 규칙, 추출 계획 |
| `test_supplementary.py` | 추가 점검, AWP와 EndorseRank의 가중치와 재시작 |
| `test_project_paths.py` | 옛 폴더 이름 변환, 폴더와 설정 경로가 실제로 있는지 |

## 준비

Python 3.10 이상이 필요합니다.

```powershell
# Windows PowerShell
cd 1-Dissertation-Works\ERC20-Allowance-PageRank-Wallet-Reputation\dissertation\wallet-reputation-experiments
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

```bash
# macOS, Linux
cd 1-Dissertation-Works/ERC20-Allowance-PageRank-Wallet-Reputation/dissertation/wallet-reputation-experiments
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

BigQuery에서 데이터를 받을 때만 Google Cloud 인증이 필요합니다(`gcloud auth application-default login`과 환경 변수 `GOOGLE_CLOUD_PROJECT`). 받은 데이터는 이미 `data/`에 있으니 결과를 확인하거나 다시 계산하는 데에는 필요 없습니다.

## 자주 쓰는 명령

```bash
python -m pytest -q                                   # 테스트
python scripts/publish_results.py --check             # 논문용 고정본이 맞는지 확인
python scripts/run_fresh_holdout.py --spring-check    # 봄 홀드아웃 숫자를 다시 계산해 비교
python scripts/export_latex_results.py                # 논문 표(.tex) 다시 쓰기
```

받아 둔 원본으로 처음부터 다시 계산하는 순서는 이렇습니다. 내려받기(extract) 단계는 끝났으니 정리 단계부터 적었습니다. 실행 시간은 컴퓨터마다 달라서 다시 돌리면 벤치마크 숫자가 바뀝니다. 논문 숫자를 확인만 하려면 위의 `--check`와 `--spring-check`로 충분합니다.

```bash
python scripts/extract_margin_week.py --merge-only     # 월별 GMX 파일을 큰 파일 하나로(Google Cloud 인증 필요: 합치기 전에 dry run을 돌림)
python scripts/decode_gmx_events.py
python scripts/preprocess_arbitrum_allowances.py
python scripts/preprocess_arbitrum_transfers.py        # transfer_events.parquet(216 MB, 내 PC에만)
python scripts/run_dissertation_eval.py --real --robustness --benchmark-repeats 5   # compute_rankings.py, compute_reputation_ranks.py 포함
python scripts/run_holdout_eval.py --cohort spenders
python scripts/run_supplementary_checks.py
python scripts/run_fresh_holdout.py
python scripts/publish_results.py
python scripts/export_latex_results.py
```

주의: `run_dissertation_eval.py --fixtures`와 `run_holdout_eval.py --fixtures`는 가짜 데이터를 `data/2-processed-tables-and-evaluations/`의 실제 파일 위에 덮어씁니다. 이 저장소에서 실수로 돌렸다면 `git checkout -- data`로 되돌리세요. 논문이 쓰는 값은 `data/3-published-results-for-thesis/`에도 따로 있습니다.

## 폴더 이동(2026-10-01, 2026-10-07) 뒤 내 PC 정리

`git pull`은 GitHub에 있는 파일만 새 위치로 옮깁니다. 가상환경(`.venv`), 100 MB가 넘는 데이터, 원고 서브모듈 체크아웃처럼 git이 추적하지 않는 것은 옛 폴더(10월 1일: `A-Skill-Programs/margin_rank/`, `2-Dissertation-Draft/`; 10월 7일: `2-Dissertation-Draft-Works/`, `1-Proposal/`, `4-Graduation/`, `5-Roundtable/`)에 남습니다. 저장소에서 지운 `3-Career/`에 남은 파일은 알려 주기만 하고 건드리지 않습니다. 저장소 루트에서, 옛 `.venv`가 아닌 파이썬으로 아래를 실행하면 남은 것을 새 위치로 옮깁니다.

```powershell
python 1-Dissertation-Works\ERC20-Allowance-PageRank-Wallet-Reputation\dissertation\wallet-reputation-experiments\scripts\finish_folder_move.py          # 옮길 목록만 보여 줌
python 1-Dissertation-Works\ERC20-Allowance-PageRank-Wallet-Reputation\dissertation\wallet-reputation-experiments\scripts\finish_folder_move.py --apply  # 실제로 옮김
```

이미 새 위치에 같은 이름의 파일이 있으면 덮어쓰지 않고 알려 줍니다. 옮긴 `.venv`에서 `pip`이 경로 오류를 내면 `python -m pip`을 쓰거나 가상환경을 새로 만드세요.

## In English

Experiment code and data for the dissertation (until 1 October 2026 this folder was `A-Skill-Programs/margin_rank`). `scripts/` extracts Arbitrum One logs from BigQuery, computes EndorseRank, AWP, C-PR and S-PR, evaluates them (same-window alignment, the spring holdout and the registered June–August replication) and exports the LaTeX tables to `../overleaf-github/results/tables/`. `config/` holds the settings and the frozen registration, `docs/` the data plan and the frozen replication plan, `sql/` the BigQuery queries and `tests/` the offline tests (`python -m pytest -q`). `data/README.md` describes every data folder; `data/3-published-results-for-thesis/` holds the committed summaries behind the thesis tables, checked with `python scripts/publish_results.py --check`.
