# 가격 확인 토큰 목록과 일별 USD 가격 (수정 분석)

`docs/revision_price_weighting.md` 3·4절의 규칙으로 만든 입력입니다. 등록 분석(원시 base unit, 모든 토큰)은 이 폴더를 읽지 않습니다.

| 파일 | 내용 | 만드는 곳 |
|------|------|-----------|
| `sources/chainlink_feeds_arbitrum_2026-10-10.json` | Chainlink의 Arbitrum One 데이터 피드 목록(docs.chain.link가 읽는 JSON), 2026-10-10에 받은 사본 | 내려받음 |
| `sources/token_candidates.csv` | Chainlink 목록이 Arbitrum One 토큰 주소에 대응하는 133개 후보. 피드, 위험 등급, 제품 유형, 토큰과 피드 기초자산의 관계(`relation`), 근거, 신원 검증 판정, DefiLlama 두 번째 키 | 검토한 입력 |
| `token_candidates.csv` | 위 표에 규칙을 적용한 결과(`listed`, 빠진 첫 이유 `reason_not_listed`) | `scripts/usd_inputs.py` |
| `listed_tokens.csv` | 목록 토큰. 주소, 심볼, 이름, decimals(고정 블록의 `eth_call`), 피드, 관계, 행 수, 가격 키별 일수, 채운 날, 오류 값 날 | `scripts/usd_inputs.py` |
| `daily_prices_usd.csv` | 토큰별 UTC 일별 가격(그날 종가). `key`는 arbitrum / second / filled, `spike`는 오류 값 규칙으로 바꾼 날 | `scripts/usd_inputs.py` |
| `daily_points_raw.csv` | DefiLlama에서 받은 원래 점(키, 시각, 가격, confidence) | `scripts/usd_inputs.py` |
| `usd_inputs.json` | 실행 기록: 후보·목록 수, 빠진 이유별 수, 메타데이터를 읽은 블록, 가격 규칙의 상수와 집계 | `scripts/usd_inputs.py` |
| `constants.json` | b와 C-PR 승인 층 상한 U (t1까지의 데이터로 구함) | `scripts/run_usd_pipeline.py constants` |
| `chainlink_check.csv`, `.json` | DefiLlama 가격과 Chainlink 온체인 값의 비교 | `scripts/chainlink_check.py` |

BigQuery에는 `contract_rep.u_tokens`, `contract_rep.u_prices`로 올라갑니다(`scripts/run_usd_pipeline.py load`).
