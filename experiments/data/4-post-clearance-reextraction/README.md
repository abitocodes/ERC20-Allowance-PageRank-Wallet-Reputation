# 4-post-clearance-reextraction

윤리 승인 뒤에 BigQuery 데이터를 처음부터 다시 추출하고 모든 평가를 다시 계산한 데이터와, 그것을 공개된 결과와 맞춰 본 기록입니다(심사 전 검토 항목 C-01, 2026-11-22 저자 결정). 공개된 결과 폴더(`../2-processed-tables-and-evaluations/`, `../3-published-results-for-thesis/`)와 원래 원장 `../bq_ledger.json`은 바꾸지 않았습니다.

## 어떻게 했나

- **복제본:** 커밋 `5b26585`의 `experiments/{scripts,sql,config,docs,tests}`를 저장소 밖(`D:\Github\phd_reextract\experiments`)에 복사해 따로 git 저장소로 만들었습니다(`replica_build.json`). 바꾼 것은 BigQuery 데이터셋 이름 하나입니다(`contract_rep` → `contract_rep_r1`, 설정 파일과 SQL). 그래서 새 추출은 옛 표를 읽을 수 없습니다. 옛 데이터셋 `contract_rep`는 그대로 둡니다.
- **BigQuery:** 원래 원장에서 두 분석이 쓰는 작업 48개를 골라(`plan.json`) 같은 SQL과 매개변수로 다시 돌렸습니다. 재추출 원장 `r1_bq_ledger.json`에는 53건이 있습니다. 작업 49건(그중 1건은 빠뜨린 로컬 단계를 마친 뒤 다시 돌린 것), 로컬 단계의 쿼리 3건, 비교용 메타데이터 쿼리 1건입니다. 청구 합계는 USD 44.30(7.088 TiB)이고 상한은 USD 50이었습니다.
- **RPC:** 계정 종류와 잔액 점검은 공개 엔드포인트에서 원래와 같은 블록으로 읽었습니다. 최신 블록으로 넘어가지 않았습니다.
- **로컬 단계(`local_steps/`):** 내려받기, 계정 종류, 코호트, 잔액 점검, 발견 순서 검증의 네 실행입니다. 파일마다 끝난 시각과, 무엇을 맞춰 보았는지가 적혀 있습니다.
- **평가:** 주 분석(`CONTRACT_REP_VARIANT=contract12m`)과 등록 분석을 복제본에서 모두 다시 돌렸습니다. 그다음 `publish_results.py`로 요약본을, `export_latex.py`로 표를 복제본 안에 다시 만들어 공개된 것과 비교했습니다.

## 결과

**추출한 데이터는 같습니다.**

- 뿌리 추출(스캔 A·B)은 달마다의 행 수가 같습니다(관측 기간 33개월, W1 3개월; `comparisons/r1_compare_meta_scans.json`).
- BigQuery 표 99개는 행 수가 모두 같습니다(`r1_compare_meta.json`).
- 내려받은 표와 로컬 단계의 비교 45건 가운데 38건은 정확히 같습니다. 정렬한 뒤 키 열은 정확히, 실수 열은 상대 1e-12로 비교했습니다(`comparisons/r1_local_compare.json`). 나머지 7건은 다음과 같습니다.
  - 잔액 점검(`balance_audit.json`): 원래 실행은 RPC 오류 7건 때문에 1,500개 가운데 1,493개만 맞았습니다. 다시 읽으니 1,500개가 모두 맞았습니다.
  - `c12_bal_audit`과 계약 그래프의 내려받기 5개(`c12_x_allow_pairs_tobs`, `c12_x_allow_pairs_t1`, `c12_importance_tobs`, `c12_importance_t1`, `c12_describe_allowances`): 행과 키는 같습니다. BigQuery가 FLOAT64 잔액을 더하는 순서가 달라 실수 값의 끝자리가 다릅니다. 그 때문에 잔액 상한에 걸리는 허락이 몇 개 바뀌었고, `c12_x_allow_pairs_t1`에서는 8쌍의 토큰 수가 3에서 2로 줄었습니다. 2026-11-24 저자 결정에 따라 이 차이를 기록하고, 다시 추출한 표로 계속했습니다.

**판정은 같습니다.** 두 분석의 요약본 모두에서, 판정을 나타내는 말(통과·실패, 충족 여부, 판정 문장)이 바뀐 행은 하나도 없습니다.

- **주 분석:**
  - 발견 순서 검증의 결정값 D1·D2와 판정 문장이 같습니다.
  - 요약본은 2,433행 가운데 174행이 다릅니다(`comparisons/r1_digest_diff_c12_full.json`). 대부분은 실행 시간과 기록 행입니다. 결과 행의 차이는 세 가지입니다.
    - 잔액 상한 표의 개수 몇 개(예: 1,270 → 1,273).
    - 잔액 점검(1,493 → 1,500).
    - 점수에서 나온 값의 소수 셋째 자리 안팎(예: 동점 비율 0.019 → 0.020, C-PR 기준선 구간 상한 0.1210 → 0.1209).
  - 학위논문 표는 39개 가운데 31개가 숫자까지 같습니다(`comparisons/r1_table_numdiff_c12_full.json`). 다른 8개는 실행 시간 표 5개와 `allowance-cap`, `tie-sensitivity`(0.187 → 0.188), `discovery-diagnostics`(0.019 → 0.020)입니다.
  - 발견 순서 검증 네 실행의 값별 비교는 `comparisons/r1_json_diff_discovery_*.json`에 있습니다.
- **등록 분석:**
  - 점수는 상대 1e-12 안에서 같습니다.
  - 요약본은 공통 960행 가운데 62행이 다릅니다(`comparisons/r1_digest_diff_registered.json`).
    - 결과 행 35행은 소수 셋째 자리에서 다릅니다. 동점의 수가 몇 개 바뀐 것이 원인입니다. 2026-11-22 저자 결정에 따라, BigQuery 실수 합 순서에서 온 동점 변화로 기록했습니다.
    - 나머지는 실행 시간 23행과 추출 기록 4행입니다.
  - 데이터 설명(`describe.json`)은 값이 모두 같고, 추출 시각과 비용 합계만 다릅니다(`comparisons/r1_reg_describe_diff.json`).

**실행 시간**은 다시 쟀습니다. 두 분석 모두 반복 수와 그래프 크기는 같고, 메모리 최댓값도 0.001 MB 안에서 같습니다.

- **주 분석:** EndorseRank 0.101 → 0.086초, AWP 2.821 → 2.366초, C-PR 3.080 → 2.652초, S-PR 2.657 → 2.223초입니다(`comparisons/r1_c12_benchmark_diff.json`).
- **등록 분석:** EndorseRank 29.60 → 25.62초, AWP 69.82 → 72.05초, C-PR 105.51 → 95.19초, S-PR 100.86 → 100.72초입니다(`comparisons/r1_reg_benchmark_diff.json`).

## 다시 추출한 데이터

`replica/experiments/data/`에 복제본의 데이터가 있습니다.

- `1-raw-blockchain-extracts/`: BigQuery에서 다시 받은 원시 표입니다.
- `2-processed-tables-and-evaluations/`: 점수와 평가입니다.
- `3-published-results-for-thesis/`: 두 분석의 요약본, 요약 JSON, `SHA256SUMS.txt`입니다.

학위논문과 투고 논문 A·B의 수치는 이 요약본에서 나왔습니다. 파일의 줄 끝은 공개된 결과 폴더처럼 CRLF입니다. parquet은 GitHub에 없고 Google Drive에만 있습니다(`../README.md`).

## 파일

| 파일 | 내용 |
|---|---|
| `plan.json` | 다시 돌린 작업 48개(원래 원장의 위치, SQL, 원래 청구, 만드는 표와 읽는 표)와 로컬 단계 5개 |
| `r1_bq_ledger.json` | 재추출 원장. 라벨은 `r1: `로 시작합니다 |
| `replica_build.json` | 복제본을 만든 커밋, 복사한 폴더, 데이터셋 이름을 바꾼 곳 |
| `r1_compare_meta.json` | BigQuery 표 99개의 행 수와 크기, 옛 것과 새 것 |
| `local_steps/` | 로컬 단계마다 끝난 시각과 비교 결과 |
| `comparisons/r1_compare_meta_scans.json` | 스캔 A·B의 달별 행 수 |
| `comparisons/r1_local_compare.json` | 내려받은 표와 로컬 단계의 비교 45건 |
| `comparisons/r1_compare_results_*.json` | 결과 파일(점수, 평가 요약)의 파일별 비교 |
| `comparisons/r1_json_diff_discovery_*.json` | 발견 순서 검증 네 실행의 값별 비교 |
| `comparisons/r1_digest_diff_*.json` | 요약본의 행별 비교(주 분석, 등록 분석) |
| `comparisons/r1_table_numdiff_c12_full.json` | 학위논문 표 39개의 숫자 비교 |
| `comparisons/r1_*_benchmark_diff.json` | 실행 시간 측정의 비교 |
| `comparisons/r1_reg_describe_diff.json` | 등록 분석 데이터 설명의 비교 |

비교에 쓴 스크립트와 기록은 복제본(`D:\Github\phd_reextract\experiments`)의 git에 있습니다.
