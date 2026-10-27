# Integrating ERC-20 Allowance Edges into PageRank for Enhanced On-Chain Wallet Reputation Scoring

학위논문 작업 폴더입니다. 폴더 이름 `ERC20-Allowance-PageRank-Wallet-Reputation`은 이 제목을 줄인 것입니다(전체 제목을 쓰면 Windows 경로 길이 제한 260자를 넘음). 이 연구는 2026-10-09에 `1-Dissertation-Works/ERC20-Allowance-PageRank-Contract-Reputation/`에서 시작했고, 2026-10-11에 이 폴더로 옮겼습니다.

## 연구

Arbitrum One의 스마트 컨트랙트에 온체인 평판 점수를 매깁니다. 토큰 주인이 컨트랙트에 준 ERC-20 허락(allowance)을 간선으로 PageRank를 계산하고(EndorseRank), 송금 간선의 PageRank인 AWP(Adaptive Weighted PageRank), 두 층을 함께 걷는 C-PR과 S-PR, 원시 차수와 견줍니다. 점수를 매기고 평가하는 대상은 스마트 컨트랙트이고, EOA(외부 소유 계정)는 허락·송금 간선의 출발점과 도착점으로만 그래프에 들어갑니다. 데이터는 Arbitrum One의 2023-10-01부터 2026-09-30까지 3년입니다.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="../../.github/readme/thesis-scores-dark.png">
  <img alt="학위논문의 점수: Approval 로그로 허락 그래프를, Transfer 로그로 송금 그래프를 만들고 EndorseRank, AWP, C-PR과 S-PR, 원시 차수를 계산해 같은 기간 점검과 기간 밖 라벨(W0, W1)로 평가함" src="../../.github/readme/thesis-scores-light.png" width="880">
</picture>

## 폴더

| 폴더 | 내용 |
|------|------|
| `proposal/` | 연구계획서. 고치지 않는 기준선이라 폴더 안에 README를 두지 않고, 아래 「연구계획서」에서 안내합니다. |
| [`dissertation/`](dissertation/) | 영문 원고(서브모듈), 발표 자료, 원고를 쓸 때 지키는 메모 |
| [`experiments/`](experiments/) | BigQuery 추출, 점수 계산, 평가 코드와 데이터 |
| [`references/`](references/) | 참고 문헌 69편 |
| [`archive/`](archive/) | 옛 지갑 평판 연구의 자료(읽기 전용) |

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

분석 계획 `43d8045`는 2026-10-09 13:41 UTC(이 연구의 첫 추출 10초 전)에, W1 등록 `0d3a057`은 같은 날 16:49 UTC(7~9월 로그 추출 8초 전)에 커밋했습니다. 수정 분석은 등록 이후의 이탈(deviation)이라 그 결과를 '등록된 결과'라고 부르지 않습니다. 이유와 규칙은 `experiments/docs/revision_price_weighting.md`에 있습니다. 토큰 목록과 가격은 `experiments/data/0-usd-token-list-and-prices/`에 있습니다. 지도교수가 수정 분석을 주 분석으로 할지는 아직 확인하지 않았습니다(`dissertation/notes/_todo.md`).

## 결과 (수정 분석)

모든 수치와 그 출처(JSON 파일과 키)는 [`experiments/data/3-published-results-for-thesis/revised-usd/results_digest.md`](experiments/data/3-published-results-for-thesis/revised-usd/results_digest.md)에, 등록 분석의 수치는 그 위 폴더의 `results_digest.md`에 있습니다. 공개한 파일의 SHA-256은 같은 폴더의 `SHA256SUMS.txt`에 있습니다. 괄호는 95% 부트스트랩 구간입니다.

- 각 점수는 자기 간선으로 만든 점검과 가장 잘 맞았습니다. EndorseRank와 허락 지표 묶음의 τ_b는 0.585 [0.578, 0.592], AWP와 송금 지표 묶음은 0.572 [0.564, 0.580]입니다. 두 점수의 순서는 서로 달랐습니다(τ_b 0.174 [0.163, 0.185]).
- C-PR(λ = 0.5)은 분석 계획의 규칙 A도, W1 등록의 규칙 B도 충족하지 못했습니다.
- 기간 밖에서는 다음과 같았습니다(Kendall τ_b의 차이). 사후 비교는 [`experiments/exploratory/2026-10-22-cpr-against-awp/`](experiments/exploratory/2026-10-22-cpr-against-awp/)에 있습니다.

| 비교 | W0 | W1 |
|---|---|---|
| AWP − 송금 입차수, 새 송금자 | +0.043 [0.038, 0.048] | +0.022 [0.017, 0.027] |
| EndorseRank − 승인 입차수, 새 승인 쌍 | −0.019 [−0.026, −0.011] | −0.034 [−0.038, −0.029] |
| C-AWP − AWP, 새 승인 쌍 (사후) | +0.118 [+0.106, +0.132] | +0.127 [+0.114, +0.139] |
| C-AWP − AWP, 새 송금자 (사후) | −0.015 [−0.019, −0.011] | −0.018 [−0.021, −0.015] |

C-AWP는 AWP의 가중치와 활동 재시작을 두 층에 쓴 결합 점수입니다. 원고 4장(sub:cpr-awp-posthoc)은 이 결과를 사후 비교로 보고하고, 다음 창에 등록해 시험할 가설로 남깁니다. C-AWP를 실제 금융 성과로 검증하려는 다음 단계 연구는 [`papers/survey-2024-2026-onchain-reputation/`](../../papers/survey-2024-2026-onchain-reputation/)에 있습니다.

## 연구계획서

`proposal/`은 고치지 않는 기준선입니다(`HANDOFF.md`). 폴더 안을 바꾸지 않으려고 안내를 여기에 둡니다.

| 경로 | 내용 |
|---|---|
| `proposal/proposal/` | LaTeX 정본: `01-Intro/`(제목, 초록, 목차), `02-Content/`(10개 장), `03-End/`(참고문헌, 부록), `Config/`, `Figures/`. 빌드한 `main.pdf`, 빌드 스크립트 `build.ps1`과 `build-docx.ps1`, 심사위원 지적 수정표 |
| `proposal/sources/` | 교수 코멘트 docx(`professor-feedback/`, README 있음), 심사위원 지적 메일과 답장 초안(`examiner-feedback/`), myModules 제출본과 2026-08-04 수정본의 비교(`submission-records/`) |
| `proposal/presentation/` | 연구계획서 발표 HTML 덱과 15분 발표 대본 |
| `proposal/translations/` | 영문 수정본 스냅샷과 영한 대역본(README 있음) |
| `proposal/scripts/` | DOCX 변환·병합·번역·주석 도구 |
| `proposal/archive/` | 옛 DOCX, DOCX 변환과 절 수정의 작업본, 스냅샷 |

상태: 2026-08-02의 심사위원 지적(DeFi 평판 도구에 대한 논의, 장황한 연구 질문)을 반영한 수정본을 2026-08-04에 지도교수께 보냈고, 2026-10-10에 승인 절차를 마무리해 달라고 요청했습니다. myModules의 최종 제출 칸에는 2026-06-20 판이 남아 있습니다. 남은 일은 [`proposal/sources/submission-records/`](proposal/sources/submission-records/2026-10-13_myModules-Proposal-FINAL-vs-2026-08-04-revision.md)의 「할 일」에 있습니다.

교수 피드백과 연구계획서 편집은 요청을 받았을 때만 `proposal/proposal/`에서 하고, `dissertation/`에 섞지 않습니다. 빌드는 그 폴더에서 `.\build.ps1`(→ `main.pdf`), Word 판은 `.\build-docx.ps1`(→ `main.docx`)입니다.

## 지킬 것

- 분석 계획(`experiments/docs/analysis_plan.md`)과 설정(`experiments/config/contract_reputation.yaml`)은 이 연구의 첫 추출 전에 커밋했습니다. 1~6절을 고치지 않습니다. W1 등록 파일도 고치지 않습니다.
- `proposal/`과 `archive/`는 고치지 않습니다. 테스트 `experiments/tests/`는 보관 스크립트(`archive/wallet-reputation-experiments/scripts/`)를 읽기 전용 기준으로 불러오므로, 그 폴더를 옮기거나 지우지 않습니다.
- 원고 문장 규칙은 `dissertation/notes/_writing-brief.md`를 따릅니다.
- 데이터, Drive, BigQuery 비용의 규칙은 [`experiments/README.md`](experiments/README.md)의 「데이터 정책」에 있습니다.
