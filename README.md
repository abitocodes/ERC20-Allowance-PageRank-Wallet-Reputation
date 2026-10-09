# Integrating ERC-20 Allowance Edges into PageRank for On-Chain Smart Contract Reputation Scoring

2026-10-09에 시작한 새 학위논문 작업 폴더입니다. 점수를 매기고 평가하는 대상은 스마트 컨트랙트뿐이고, 일반 지갑(EOA)은 허락·송금 간선의 출발점과 도착점으로만 그래프에 들어갑니다. 데이터는 Arbitrum One의 2023-10-01부터 2026-09-30까지 3년입니다.

| 폴더 | 내용 |
|------|------|
| `experiments/` | BigQuery 추출, 점수 계산, 평가 코드와 데이터 |
| `dissertation/` | UNISA 양식의 논문 원고(LaTeX) |

## 기간

| 구간 | 날짜 | 쓰임 |
|------|------|------|
| 관측 기간 | 2023-10-01 ~ 2026-06-30 | 같은 기간 정렬, 벤치마크, 강건성 |
| 홀드아웃 W0 | 2026-03-31 동결, 4~6월 라벨 | 스펜더 홀드아웃, 규칙 A |
| 등록 재현 W1 | 2026-06-30 동결, 7~9월 라벨 | 등록 파일을 커밋한 뒤에 7~9월 로그를 추출 |

## 지킬 것

- 분석 계획(`experiments/docs/analysis_plan.md`)과 설정(`experiments/config/contract_reputation.yaml`)은 추출 전에 커밋했습니다. 1~6절을 고치지 않습니다.
- `data/` 아래 파일은 모두 90 MB 아래로 나눠 저장합니다(GitHub 100 MB 한도).
- BigQuery 비용은 `experiments/data/bq_ledger.json`에 쌓이며 전체 상한은 USD 50입니다.
