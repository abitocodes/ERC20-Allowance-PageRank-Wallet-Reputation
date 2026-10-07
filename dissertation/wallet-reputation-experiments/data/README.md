# data — 이 연구에 쓰인 모든 데이터

## 먼저 아주 쉽게

블록체인(이 연구에서는 Arbitrum One)은 누구나 읽을 수 있는 아주 큰 공책입니다. 누가 누구에게 돈을 보냈는지, 누가 어떤 앱에게 "내 돈을 써도 좋아"라고 허락했는지가 한 줄씩 적혀 있습니다.

이 폴더에는 그 공책에서 연구에 필요한 줄만 베껴 온 것부터 논문 표에 들어간 최종 결과까지 모두 들어 있습니다. 폴더 앞의 숫자는 데이터가 지나가는 순서입니다.

| 순서 | 폴더 | 한 줄 설명 |
|---|---|---|
| 0 | `0-gmx-abi-for-decoding-logs/` | GMX가 암호처럼 적어 둔 기록을 읽는 사전 |
| 1 | `1-raw-blockchain-logs/` | 블록체인 공책에서 그대로 베껴 온 원본. 손대지 않습니다 |
| 2 | `2-processed-tables-and-evaluations/` | 원본을 읽기 쉽게 정리한 표, 지갑 점수, 점수가 맞는지 시험한 결과 |
| 3 | `3-published-results-for-thesis/` | 2번 결과 가운데 논문 표가 쓰는 것만 따로 복사해 둔 고정본 |
| 4 | `4-archived-extended-baselines/` | 예전에 해 본 비교 실험. 논문 본문에는 쓰지 않습니다 |

1번이 "가공 전", 2번과 3번이 "가공 후"입니다. 2번은 프로그램을 다시 돌릴 때마다 새로 써지고, 3번은 논문에 실린 숫자를 지키려고 복사해 둔 것이라 함부로 바뀌지 않습니다.

```
data/
├── 0-gmx-abi-for-decoding-logs/
├── 1-raw-blockchain-logs/
│   ├── observation-window-2025-12-to-2026-05/        본 연구 6개월
│   │   ├── erc20-approval-logs/                      "써도 좋아" 허락 기록
│   │   ├── erc20-transfer-logs/                      "보냈어" 송금 기록
│   │   ├── gmx-position-close-logs/                  GMX 거래를 닫은 기록
│   │   └── aave-lending-logs/                        Aave에서 빌리고 갚은 기록
│   └── registered-replication-2026-06-to-2026-08/    미리 약속하고 나중에 꺼낸 3개월
│       ├── erc20-approval-logs/
│       ├── erc20-transfer-logs/
│       └── gmx-position-close-logs/
├── 2-processed-tables-and-evaluations/
│   ├── erc20-allowances-and-transfers/
│   ├── aave-lending-events/
│   ├── spring-holdout-2026-03-to-2026-05/
│   └── registered-replication-2026-06-to-2026-08/
├── 3-published-results-for-thesis/
│   ├── config-copies/
│   ├── spring-holdout-2026-03-to-2026-05/
│   └── registered-replication-2026-06-to-2026-08/
└── 4-archived-extended-baselines/
    └── superseded-before-2026-09-30-sign-fix/
```

## 알아 두면 좋은 낱말

| 낱말 | 쉽게 말하면 |
|---|---|
| 지갑 (wallet) | 블록체인 위의 계좌입니다. `0x`로 시작하는 긴 주소로 부릅니다. 사람이 쓰는 지갑(EOA)도 있고, 앱이 쓰는 지갑(계약, contract)도 있습니다. |
| 토큰 (ERC-20) | 블록체인 위의 돈이나 포인트입니다. USDC 같은 것입니다. |
| 허락 (approval, allowance) | "이 앱이 내 토큰을 N개까지 꺼내 써도 좋아"라는 기록입니다. 허락한 쪽이 owner, 허락받은 쪽이 spender입니다. |
| 송금 (transfer) | "토큰 N개를 보냈어"라는 기록입니다. 보낸 쪽이 from, 받은 쪽이 to입니다. |
| GMX | 빚을 내서 크게 거는 거래(레버리지 거래)를 하는 앱입니다. 거래를 닫으면 기록이 남고, 담보가 모자라 강제로 닫히면 청산(liquidation)이라고 합니다. |
| Aave | 돈을 빌리고(borrow) 갚는(repay) 앱입니다. |
| 로그 (log) | 블록체인 공책의 한 줄입니다. |
| EndorseRank | 이 논문이 제안한 점수입니다. 허락을 "이 지갑을 믿는다"는 추천으로 보고, 믿을 만한 지갑에게서 추천을 많이 받을수록 점수를 높게 줍니다(PageRank 계산). 허락 하나하나에는 AWP와 똑같은 무게(오래될수록 작게, 금액은 거의 한 번으로)를 주고, 다시 출발하는 곳은 모든 지갑에 고르게 둡니다. |
| AWP | 비교 대상인 기존 점수입니다(Do, Do, Nguyen 2023 논문 그대로). 허락 대신 송금을 보고 점수를 주고, 최근에 여러 곳으로 보낸 지갑에서 더 자주 다시 출발합니다. |
| C-PR, S-PR | 허락과 송금을 함께 쓰는 점수입니다. C-PR은 금액을 그대로 쓰는 두 층을 반반(λ=0.5) 섞고, S-PR은 허락 층 점수에서 출발해 송금을 따라갑니다. λ=1과 λ=0은 한 층만 걷는 경우이고, 9월 14일 규칙과 등록 문서는 이 둘을 EndorseRank와 AWP라고 불렀습니다(코드 id `endorserank`, `awp`). |
| 매칭 코호트 | 2025년 12월부터 2026년 5월까지 GMX에서 거래를 3번 이상 닫은 지갑 5,521개입니다. 허락·송금 기록은 이 지갑들이 관련된 것만 가져왔습니다. |
| 스펜더 코호트 | 기준일에 누군가에게서 유효한 허락을 받아 둔 지갑들입니다(대부분 앱). 2월 28일에는 1,335개, 5월 31일에는 1,964개입니다. |
| 동결일과 라벨 | 시험지를 미리 보지 않게 하는 장치입니다. 점수는 동결일까지의 기록만 보고 매기고, 그 뒤에 실제로 일어난 일(라벨)로 채점합니다. |
| parquet, json, csv, yaml | 파일 종류입니다. parquet은 큰 표(파이썬 pandas로 엽니다), json은 결과를 적은 글자 파일, csv는 엑셀로 열리는 작은 표, yaml은 설정 파일입니다. |

## 0-gmx-abi-for-decoding-logs/ — 사전

| 파일 | 쉽게 말하면 | 자세히 |
|---|---|---|
| `EventEmitter.json` | GMX가 암호처럼 적어 둔 거래 기록을 풀어 읽는 사전 | GMX V2 EventEmitter 계약의 ABI(Hardhat 산출물)입니다. `scripts/decode_gmx_events.py`가 `EventLog1` 기록의 구조를 풀 때 읽습니다. 예전 이름은 `abis/`였습니다. |

## 1-raw-blockchain-logs/ — 블록체인에서 베껴 온 원본

Google BigQuery의 공개 테이블 `bigquery-public-data.goog_blockchain_arbitrum_one_us.logs`에서 내려받은 그대로입니다. 한 달치가 파일 하나입니다. 허락·송금·Aave 기록은 매칭 코호트 지갑이 관련된 줄만, GMX 기록은 모든 지갑의 줄을 가져왔습니다.

### observation-window-2025-12-to-2026-05/ — 본 연구 6개월 (2025-12-01 ~ 2026-05-31)

논문 4장의 거의 모든 결과가 이 6개월에서 나옵니다. 봄 홀드아웃(아래 2번 폴더)도 이 6개월 안에서 2월 28일을 동결일로 삼아 채점합니다.

| 폴더 / 파일 | 쉽게 말하면 | 자세히 |
|---|---|---|
| `erc20-approval-logs/approvals_2025-12.parquet` … `approvals_2026-05.parquet` | 한 달 동안의 "써도 좋아" 기록 | 달마다 65,576~79,204줄. 열: 시각(`block_timestamp`), 토큰 주소, `owner`, `spender`, 허락한 양(`value`), 원래 형태(`owner_topic` 등) |
| `erc20-approval-logs/approvals_arbitrum.parquet` | 위 여섯 달을 한 파일로 합친 것 | 453,545줄. 이 파일이 있으면 스크립트는 월별 파일 대신 이것을 읽습니다. |
| `erc20-approval-logs/approvals_synthetic.parquet` | 연습용으로 컴퓨터가 지어낸 가짜 기록 | 11,420줄. 진짜 파일이 있으면 읽지 않습니다(`generate_synthetic_reputation.py`). |
| `erc20-transfer-logs/transfers_2025-12.parquet` … `transfers_2026-05.parquet` | 한 달 동안의 "보냈어" 기록 | 달마다 397,523~510,326줄. 열: 시각, 토큰 주소, `from_address`, `to_address`, 보낸 양(`value`) |
| `erc20-transfer-logs/transfers_synthetic.parquet` | 연습용 가짜 송금 기록 | 33,323줄 |
| `erc20-transfer-logs/transfers_arbitrum.parquet` (내 PC에만) | 여섯 달 송금을 합친 큰 파일 | 100 MB가 넘어 GitHub에 올리지 않습니다. 없으면 스크립트가 월별 파일을 읽습니다. |
| `gmx-position-close-logs/gmx_event_logs_2025-12.parquet` … `2026-05.parquet` | GMX에서 거래를 닫은 기록, 아직 암호 상태 | 달마다 53,554~68,537줄. GMX V2 `PositionDecrease` 이벤트(일부만 닫은 것과 청산 포함) |
| `gmx_event_logs_2025-12_to_2026-05.parquet` (내 PC에만, 이 폴더 바로 아래) | 여섯 달 GMX 기록을 합친 큰 파일 | `decode_gmx_events.py`의 입력입니다. 100 MB가 넘어 GitHub에는 없고, `python scripts/extract_margin_week.py --merge-only`로 월별 파일에서 다시 만듭니다(Google Cloud 인증 필요). |
| `aave-lending-logs/aave_events_2025-12.parquet` … `2026-05.parquet` | Aave에서 빌리고, 갚고, 청산된 기록 | 달마다 602~2,365줄. Aave V3 Pool의 Borrow, Repay, LiquidationCall |
| `aave-lending-logs/aave_events_arbitrum.parquet` | 위 여섯 달을 합친 것 | 8,801줄 |

### registered-replication-2026-06-to-2026-08/ — 미리 약속하고 나중에 꺼낸 3개월 (2026-06-01 ~ 2026-08-31)

"무엇을 어떻게 채점할지"를 먼저 적어 공개(등록)한 다음에 꺼내 온 채점용 기록입니다. 등록은 2026년 10월 1일 커밋 `4085ab9`에서 했고, 기록은 같은 날 그 뒤에 내려받았습니다. 점수는 5월 31일까지의 기록으로 매기고, 이 3개월로 채점합니다. 같은 SQL, 같은 5,521개 지갑 조건을 썼습니다.

| 폴더 / 파일 | 쉽게 말하면 | 자세히 |
|---|---|---|
| `erc20-approval-logs/approvals_2026-06.parquet` … `2026-08.parquet` | 6~8월의 "써도 좋아" 기록 | 72,790 / 45,904 / 44,859줄, 합계 163,553줄 |
| `erc20-transfer-logs/transfers_2026-06.parquet` … `2026-08.parquet` | 6~8월의 "보냈어" 기록 | 448,328 / 278,548 / 286,147줄, 합계 1,013,023줄 |
| `gmx-position-close-logs/gmx_event_logs_2026-06.parquet` … `2026-08.parquet` | 6~8월에 GMX 거래를 닫은 기록 | 59,969 / 38,176 / 46,007줄, 합계 144,152줄 |

### expanded-pool-tier2-2025-12-to-2026-05/ (내 PC에만, 없을 수도 있음)

확장 지갑 풀(99,080개)의 허락·송금 기록을 따로 다시 받으려던 시도가 남긴 폴더입니다(`extract_reputation_data.py --tier2`). 예상 비용이 1.3 TiB를 넘었고 내려받기가 계속 실패해서 그만두었습니다(논문 부록 A). 결과에는 쓰이지 않았습니다.

## 2-processed-tables-and-evaluations/ — 정리한 표, 점수, 시험 결과

원본을 읽기 쉽게 정리하고(암호 풀기, 가장 최근 허락만 남기기), 지갑마다 점수를 매기고, 그 점수가 맞는지 시험한 결과입니다. 스크립트를 다시 돌리면 여기 파일이 덮어써집니다. 논문 표가 기대는 고정본은 3번 폴더에 있습니다.

### 바로 아래에 있는 파일

| 파일 | 쉽게 말하면 | 자세히 |
|---|---|---|
| `gmx_decoded_events.parquet` | 암호를 푼 GMX 거래 마감 기록(12~5월) | 365,488건, 지갑 9,388개, 그중 청산 29,848건. 열: `account`(거래한 지갑), `base_pnl_usd`(벌거나 잃은 달러), `is_liquidation`(청산 여부), `size_delta_usd`(닫은 크기), `order_type`, `is_long`. `decode_gmx_events.py`가 만듭니다. |
| `wallet_rankings.parquet` | 매칭 코호트 5,521개 지갑의 성적표와 방법별 점수 | 지갑마다 닫은 횟수(`total_closes`), 이긴 횟수(`wins`), 진 횟수(`losses`), 성공률과 각 방법의 점수·순위: `endorserank_vt`(EndorseRank), `endorserank_vt_activity`(재시작만 AWP 방식으로 바꾼 민감도 분석), `awp_paper`(AWP), `endorserank`(C-PR λ=1), `awp`(C-PR λ=0), `coupled_pr`(C-PR, λ=0.5), `coupled_pr_l25`, `coupled_pr_l75`, `seeded_pr`(S-PR), 그리고 4번 창고용 비교 방법들. `compute_rankings.py`, `compute_reputation_ranks.py` |
| `extraction_wallet_set.parquet` | 확장 지갑 풀 99,080개의 주소 목록 | 매칭 코호트 5,521개에 보충 지갑 93,559개를 더한 것입니다. 실행 시간 측정(표 benchmark-scaling)에 씁니다. |
| `supplemental_wallets.parquet` | 보충용으로 뽑아 둔 활동 지갑 94,479개 | `sample_active_wallets.py`가 BigQuery에서 송금이 많은 지갑을 뽑았습니다. 확장 풀을 채울 때 앞에서부터 씁니다. |
| `extraction_manifest.json` | 12~5월 기록을 어떻게 가져오고 정리했는지 적은 일지 | 쿼리마다 읽은 바이트, 줄 수, 출력 파일, 해독 결과. 안에 적힌 경로는 그때의 위치(옛 폴더 이름, 사용자 PC의 `D:\`)입니다. |
| `eval_summary.json` | 같은 6개월 안에서 점수를 시험한 결과 | 점수와 검증 지표 사이의 순위 상관(Kendall τ, Spearman ρ)과 95% 부트스트랩 구간, Δτ 대비, 실행 시간, 강건성 점검. 2026-10-02에 클라우드 컨테이너(4코어 Xeon 2.8 GHz)에서 다시 만들었습니다. 4장 표 대부분의 근거입니다. |
| `supplementary_checks.json` | 결과를 본 뒤에 해 본 추가 점검 | 동점 처리 규칙, 송금을 받아 본 스펜더 977개만 남긴 봄 홀드아웃, 트레이더 수. `run_supplementary_checks.py`. 표 tie-sensitivity, holdout-receiving과 부록 표 endorserank-awp-holdout(둘째 묶음)의 근거입니다. |

### erc20-allowances-and-transfers/

| 파일 | 쉽게 말하면 | 자세히 |
|---|---|---|
| `latest_allowances.parquet` | 지금도 살아 있는 "써도 좋아" 허락 목록 | (토큰, owner, spender)마다 가장 최근 허락 하나만 남긴 표입니다. 21,585줄, owner 4,590개, spender 1,964개, 토큰 466개. EndorseRank 그래프의 선이 됩니다. `preprocess_arbitrum_allowances.py` |
| `transfer_events.parquet` (내 PC에만) | 정리한 송금 목록 | 2,639,388건. 216 MB라 GitHub에는 없고 `python scripts/preprocess_arbitrum_transfers.py`로 다시 만듭니다. AWP 그래프의 선이 됩니다. |

### aave-lending-events/

| 파일 | 쉽게 말하면 | 자세히 |
|---|---|---|
| `aave_events.parquet` | 암호를 푼 Aave 기록 | 8,801건(빌림 4,409, 갚음 4,344, 청산 48). `preprocess_aave_lending.py`. 논문 본문 결과에는 쓰이지 않았고, 4번 창고의 비교 실험과 8월 29일 탐색용 채점(Aave 청산 라벨)에 쓰였습니다. |

### spring-holdout-2026-03-to-2026-05/ — 봄 홀드아웃

2월 28일까지의 기록으로 점수를 매기고, 3~5월에 실제로 일어난 일로 채점한 결과입니다.

| 파일 | 쉽게 말하면 | 자세히 |
|---|---|---|
| `eval_summary_spenders.json` | 스펜더 1,335개의 채점표 | 라벨 두 가지(새로 생긴 허락 쌍, 새로 생긴 송금자)에 대한 모든 점수와 원시 차수의 τ, 9월 14일에 미리 정한 대비와 라벨을 본 뒤 계산한 대비, 9월 14일 규칙 판정. `run_holdout_eval.py --cohort spenders`. 3번 폴더에 고정본이 있습니다. |
| `eval_summary_matched_traders.json` | 트레이더 4,227명의 탐색용 채점 | 3~5월 GMX 성적(이익 난 마감 수, 실현 이익, 이익 비율)에 대한 모든 점수의 τ. 라벨은 8월 29일에 정했고, 점수는 라벨을 본 뒤인 10월 2일에 매겼습니다. `run_holdout_eval.py --cohort matched --out …` |
| `eval_summary.json` | 8월 29일에 해 본 탐색용 채점(보관) | 트레이더 4,227명, 허락 층과 송금 층을 각각 혼자 걸은 점수만 채점했습니다(부트스트랩 200회). inverse-risk 라벨은 9월 30일 부호 수정 전 그대로 보관합니다. |
| `spender_account_types.csv` | 스펜더 하나하나가 앱(계약)인지 사람 지갑인지 | 1,335줄. 계약 1,174개, 사람 지갑 161개(EIP-7702 지갑 1개 포함). `classify_spenders.py`, `check_spender_code.py` |
| `spender_account_types.json` | 위 표의 개수 요약 | 기간, 읽은 바이트, 종류별 개수 |

### registered-replication-2026-06-to-2026-08/ — 등록 재현

| 파일 | 쉽게 말하면 | 자세히 |
|---|---|---|
| `gmx_decoded_events.parquet` | 암호를 푼 6~8월 GMX 거래 마감 기록 | 144,152건. 열은 12~5월 파일과 같습니다. |
| `extraction_manifest.json` | 6~8월 기록을 가져온 일지 | 쿼리 9개, 과금 약 1.04 TB, 줄 수, 등록 파일과 계획서의 해시(사용자 Windows 체크아웃, 즉 줄바꿈 CRLF 기준) |
| `fresh_holdout_summary.json` | 등록 재현 채점표 | F1~F6, 판정, 민감도 분석 두 가지. 판정은 미충족입니다(F1·F3 통과, F2 실패). `run_fresh_holdout.py` |
| `spring_check.json` | 같은 코드로 봄 결과를 다시 계산해 본 확인서 | 봄 홀드아웃의 모든 계수가 발표된 값과 같았습니다(불일치 0). `run_fresh_holdout.py --spring-check`. 10월 2일에 다시 돌려도 같았습니다. |
| `posthoc_endorserank.json` | 등록 재현 뒤에 EndorseRank를 따로 채점한 결과 | 같은 코호트, 라벨, 재표본으로 EndorseRank(와 재시작을 AWP 방식으로 바꾼 것)를 채점했습니다. 판정에는 들어가지 않습니다. `run_fresh_posthoc.py` |
| `fixtures_summary.json` | 가짜 데이터로 돌려 본 연습 결과 | 코드가 도는지만 확인한 것이라 숫자에 뜻이 없습니다. `run_fresh_holdout.py --fixtures` |

### 내 PC에만 생기는 폴더

- `active-wallet-sampling-cache/`: `sample_active_wallets.py`가 달마다 받은 활동 지갑 목록을 저장해 두는 곳입니다. 몇 달 치는 100 MB를 넘습니다.
- `expanded-pool-tier2-allowances-and-transfers/`: 위 tier2 재추출을 정리한 결과가 들어갈 곳입니다.

## 3-published-results-for-thesis/ — 논문 표의 고정본

2번 폴더의 결과는 다시 돌리면 바뀝니다. 그래서 논문 표를 만든 바로 그 결과를 여기에 복사해 두고, 파일마다 지문(SHA-256)을 `MANIFEST.json`에 적었습니다. 논문의 숫자는 여기 파일과 맞춰 볼 수 있습니다.

| 파일 | 쉽게 말하면 | 논문에서 |
|---|---|---|
| `eval_summary.json` | 2번 폴더 같은 이름 파일의 사본 | 정렬, 대비, 실행 시간, 강건성 표 |
| `supplementary_checks.json` | 2번 폴더 같은 이름 파일의 사본 | 표 tie-sensitivity, holdout-receiving, 부록 표 endorserank-awp-holdout |
| `spring-holdout-2026-03-to-2026-05/eval_summary_spenders.json` | 봄 홀드아웃 채점표 사본 | 표 holdout-spenders, holdout-diff, endorserank-restarts, 부록 표 endorserank-awp-holdout |
| `spring-holdout-2026-03-to-2026-05/eval_summary_matched_traders.json` | 트레이더 탐색용 채점표 사본 | 표 holdout-traders |
| `registered-replication-2026-06-to-2026-08/extraction_manifest.json` | 6~8월 추출 일지 사본 | 등록 파일 해시 확인용 |
| `registered-replication-2026-06-to-2026-08/fresh_holdout_summary.json` | 등록 재현 채점표 사본 | 표 fresh-holdout, fresh-contrasts, fresh-traders |
| `registered-replication-2026-06-to-2026-08/posthoc_endorserank.json` | 등록 재현 뒤 EndorseRank 채점 사본 | 표 fresh-posthoc, 부록 표 endorserank-awp-holdout |
| `config-copies/margin_config.yaml` | 설정 파일 사본 | 2026-09-14에 고정한 C-PR 규칙(`reputation.hybrid`) 포함 |
| `config-copies/fresh_holdout_2026q3.yaml` | 등록 파일 사본 | `status: registered`, 커밋 `4085ab9` |
| `MANIFEST.json` | 위 파일들의 지문 목록 | 파일마다 원본 위치, 크기, SHA-256 |

- 복사와 확인: `python scripts/publish_results.py`가 복사하고 지문을 적습니다. `python scripts/publish_results.py --check`는 사본이 지문, 그리고 2번 폴더의 원본과 같은지 확인합니다.
- `MANIFEST.json`의 지문은 줄바꿈을 LF로 맞춰서 계산하므로 Windows(CRLF)와 Linux에서 같은 값이 나옵니다. 반면 `extraction_manifest.json` 안의 등록 파일 해시는 Windows 파일을 그대로 계산한 값입니다. 그래서 같은 등록 파일이라도 두 곳의 해시가 다릅니다(LF `6291f42…`, CRLF `9777f30…`).
- 2026-09-30에 inverse-risk 검증 지표 두 개(`loss_avoidance`, `worst_close_pnl_score`)의 부호가 거꾸로였던 것을 찾아 고쳤습니다. `scripts/refresh_alignment.py`가 같은 parquet으로 `eval_summary.json`의 정렬 부분만 다시 계산했고, 실행 시간은 다시 재지 않았습니다.
- 6~8월 등록 재현은 2026-10-01에 등록(커밋 `4085ab9`)하고 같은 날 추출해서 `run_fresh_holdout.py`의 `registered` 모드로 채점했습니다.
- 2026-10-02에 같은 기간 평가, 봄 홀드아웃, 트레이더 탐색 채점, 추가 점검을 다시 돌렸습니다. EndorseRank와 AWP의 점수, 그리고 실행 시간이 이때 나온 값입니다(클라우드 컨테이너, 4코어 Xeon 2.8 GHz, 메모리 15 GB). 등록 재현의 숫자는 바뀌지 않았습니다.

## 4-archived-extended-baselines/ — 창고

다른 PageRank 방법들과 넓게 비교해 본 결과입니다. 논문에서는 EndorseRank, AWP, 그리고 두 층으로 만든 C-PR과 S-PR만 다루기로 해서 창고에 두었습니다. 이 표들의 허락 기준과 송금 기준은 금액을 그대로 쓰는 두 층을 각각 혼자 걸은 점수(지금의 C-PR λ=1, λ=0)입니다. 표의 줄은 방법, 칸은 검증 지표 여섯 가족의 평균 τ와 실행 시간(초)입니다. `python scripts/export_method_matrix.py --preset three|seven|six-aave`로 다시 만듭니다.

| 파일 | 쉽게 말하면 |
|---|---|
| `three_method_proxy_matrix.csv` | EndorseRank, AWP, GF-PR 세 방법. GF-PR은 GMX 성적으로 만든 점수를 GMX 성적으로 채점하는 꼴이라 본문에서 뺐습니다. |
| `method_proxy_matrix.csv` | 일곱 방법(위 셋에 LP-PR, CW-AWP, LF-PR, RiskProp-PR) |
| `six_aave_method_proxy_matrix.csv` | Aave 기록을 쓰는 방법을 더한 여섯 방법 |
| `superseded-before-2026-09-30-sign-fix/` | 9월 30일 부호 수정 전에 만든 옛 사본 두 개(예전 위치는 `data/processed/`). 어떤 스크립트도 읽지 않습니다. |

## GitHub에 없는 파일 (내 PC에만)

100 MB가 넘거나 다시 만들 수 있는 파일은 올리지 않습니다(`../.gitignore`).

| 파일 / 폴더 | 다시 만드는 방법 |
|---|---|
| `1-raw-blockchain-logs/observation-window-2025-12-to-2026-05/gmx_event_logs_2025-12_to_2026-05.parquet` | `python scripts/extract_margin_week.py --merge-only` (Google Cloud 인증 필요) |
| `1-raw-blockchain-logs/observation-window-2025-12-to-2026-05/erc20-transfer-logs/transfers_arbitrum.parquet` | 없어도 됩니다. 스크립트가 월별 파일을 읽습니다. |
| `2-processed-tables-and-evaluations/erc20-allowances-and-transfers/transfer_events.parquet` | `python scripts/preprocess_arbitrum_transfers.py` |
| `1-raw-blockchain-logs/expanded-pool-tier2-2025-12-to-2026-05/`, `2-processed-tables-and-evaluations/active-wallet-sampling-cache/` | 결과에 필요 없습니다. |
| 어느 폴더든 `_chunks/`, `*.log` | 내려받다 멈춘 조각과 실행 기록입니다. 다시 받을 때 `--resume`이 씁니다. |

## 옛 폴더 이름 (2026-10-01 전)

2026년 10월 1일에 폴더 이름을 바꿨습니다. 그 전에 만든 JSON 일지 안의 경로와 등록 파일 `config/fresh_holdout_2026q3.yaml`(고정되어 고칠 수 없음)은 옛 이름을 그대로 씁니다. 코드는 `scripts/project_paths.py`의 대응표로 옛 이름을 새 이름으로 바꿔 읽습니다.

| 옛 이름 (`A-Skill-Programs/margin_rank/` 아래) | 새 이름 (`data/` 아래) |
|---|---|
| `abis/` | `0-gmx-abi-for-decoding-logs/` |
| `data/raw/reputation/approvals/` | `1-raw-blockchain-logs/observation-window-2025-12-to-2026-05/erc20-approval-logs/` |
| `data/raw/reputation/transfers/` | `1-raw-blockchain-logs/observation-window-2025-12-to-2026-05/erc20-transfer-logs/` |
| `data/raw/gmx/` | `1-raw-blockchain-logs/observation-window-2025-12-to-2026-05/gmx-position-close-logs/` |
| `data/raw/lending/` | `1-raw-blockchain-logs/observation-window-2025-12-to-2026-05/aave-lending-logs/` |
| `data/raw/fresh_2026q3/{approvals,transfers,gmx}/` | `1-raw-blockchain-logs/registered-replication-2026-06-to-2026-08/{erc20-approval-logs,erc20-transfer-logs,gmx-position-close-logs}/` |
| `data/raw/reputation_tier2/` | `1-raw-blockchain-logs/expanded-pool-tier2-2025-12-to-2026-05/` |
| `data/processed/` | `2-processed-tables-and-evaluations/` |
| `data/processed/reputation/` | `2-processed-tables-and-evaluations/erc20-allowances-and-transfers/` |
| `data/processed/lending/` | `2-processed-tables-and-evaluations/aave-lending-events/` |
| `data/processed/holdout/` | `2-processed-tables-and-evaluations/spring-holdout-2026-03-to-2026-05/` |
| `data/processed/fresh_2026q3/` | `2-processed-tables-and-evaluations/registered-replication-2026-06-to-2026-08/` |
| `results/` | `3-published-results-for-thesis/` |
| `results/config/`, `results/holdout/`, `results/fresh_2026q3/` | `3-published-results-for-thesis/config-copies/`, `…/spring-holdout-2026-03-to-2026-05/`, `…/registered-replication-2026-06-to-2026-08/` |
| `data/archive/extended-baselines/` | `4-archived-extended-baselines/` |
| `data/fixtures/` (설명 파일만 있던 폴더) | 없앰. 내용은 이 문서에 옮겼습니다. |

## In English

This folder holds every dataset behind the dissertation, in the order the data flow: `0-gmx-abi-for-decoding-logs/` (the GMX V2 EventEmitter ABI used to decode GMX logs), `1-raw-blockchain-logs/` (Arbitrum One logs as downloaded from BigQuery: the observation window December 2025 to May 2026, and the registered replication window June to August 2026), `2-processed-tables-and-evaluations/` (decoded and cleaned tables, wallet scores and evaluation summaries, rewritten on each run), `3-published-results-for-thesis/` (the committed copies of the summaries behind the thesis tables, with SHA-256 hashes in `MANIFEST.json`) and `4-archived-extended-baselines/` (extended-baseline matrices not used in the main text). The table above maps the folder names used before 1 October 2026 to the present ones.
