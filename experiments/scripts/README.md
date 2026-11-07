# scripts

실험 스크립트입니다. 모두 `experiments/`에서 실행합니다. 경로와 설정은 `common.py`가 정하고, 환경 변수 `CONTRACT_REP_VARIANT=usd`이면 수정 분석의 경로(`graph-tables-usd/`, `revised-usd/`)를, `CONTRACT_REP_VARIANT=usd12m`이면 12개월 변형(`../docs/revision_one_year_window.md`)의 경로(`graph-tables-usd-12m/`, `revised-usd-12m/`)와 `../config/overlay_usd12m.yaml`의 두 기간 시작을, `CONTRACT_REP_VARIANT=contract12m`이면 컨트랙트 그래프 수정(`../docs/revision_contract_graph.md`, `../docs/discovery_protocol.md`)의 경로(`graph-tables-contract-12m/`, `contract-types/`, `revised-contract-12m/`)와 `../config/overlay_contract12m.yaml`의 설정(예산 USD 60 포함)을 씁니다. 실행 순서는 [`../README.md`](../README.md)의 「실행」에 있습니다.

## BigQuery와 데이터 받기

| 파일 | 하는 일 |
|---|---|
| `run_bq.py` | SQL 파일 하나를 dry run으로 비용을 본 뒤 실행하고, 청구된 바이트를 `data/bq_ledger.json`에 적습니다(실패한 작업도, 변형과 예산까지). 예산은 변형의 설정에서 읽어(USD 50, `contract12m`은 USD 60), 남은 예산을 넘는 작업은 `--force` 없이는 거부합니다. 12개월 변형용 선택 사항: 테이블 이름 바꾸기(`--rename`), 만드는 테이블의 접두사와 읽어도 되는 테이블 검사(`--require-prefix`, `--allow-read`; 이때 모든 테이블을 역따옴표 안 `project.dataset.table` 전체 이름으로 적었는지와 CREATE 말고 테이블을 바꾸는 문장(ALTER, LOAD 등)이 없는지도 검사), 읽어도 되는 공개 테이블·view를 전체 이름으로(`--allow-public`, 나머지 다른 데이터셋은 거부), 현실적인 추정 바이트(`--expect-bytes`, dry run은 여러 문장 중 첫 문장만 셈), dry run 상한(`--max-dry-bytes`), 캠페인 상한(`--campaign`, `--campaign-cap`). |
| `download_table.py` | 프로젝트 BigQuery 테이블을 Storage Read API로 받아 90 MB 아래 parquet 조각과 `.json` 기록으로 저장합니다. 쿼리를 돌리지 않아 스캔 비용이 없습니다. |
| `download_graph_tables.sh` | 등록 분석의 그래프 표를 `data/1-raw-blockchain-extracts/graph-tables/`로 받습니다(sql/04–08을 돌린 뒤). |
| `run_usd_pipeline.py` | 수정 분석(33개월)의 BigQuery 단계를 순서대로 돌립니다: load, ego, constants, pairs, rest, download. `CONTRACT_REP_VARIANT=usd`가 아니면 거부합니다(`u_*` 테이블과 `constants.json`을 덮어쓰지 않게). |
| `run_usd12m_pipeline.py` | 12개월 변형의 BigQuery 단계: check(무료 메타데이터 점검과 작업별 비용 추정), tokens, cohorts, constants, pairs, rest, checks(sql/23 불변식), download. `u12_*` 테이블만 만들고, 작업마다 추정 바이트와 캠페인 상한(USD 4.00)을 `run_bq.py`에 넘깁니다. 수정 문서·오버레이·SQL이 커밋되어 있어야 돌아가고, `revised-usd-12m/run_manifest.json`에 커밋, 해시, 작업, 단계 결과를 적습니다. |
| `run_contract12m_pipeline.py` | 컨트랙트 그래프 수정의 BigQuery·RPC 단계(수정 문서 12절). 게이트 A: check(무료 메타데이터 점검과 작업별 비용 추정; 게이트 A 파일이 커밋되기 전에는 경고만 하고 아무것도 쓰지 않음), subset(24), ends(25), activity(26–28), queue(29), typing(`check_account_code.py`로 고정 블록의 계정 종류, 로컬), load(30, 청구되지 않는 load 작업), contracts(31), balances(32, 33), anchors(34), audit(43과 `balance_audit.py`), structure(35와 구조 파일럿). 게이트 B 단계(constants, pairs, rest, checks, download)는 아직 거부합니다. `c12_*` 테이블만 만들고 이름을 적은 공개 view만 읽으며, 작업마다 추정 바이트와 캠페인 상한(USD 14)을 `run_bq.py`에 넘깁니다. check 말고는 수정 문서·프로토콜·오버레이·코드·SQL이 커밋되어 있어야 돌아가고, `revised-contract-12m/run_manifest.json`에 커밋, 해시, 작업, 단계 결과를 적습니다. 단계는 이 순서대로만 돕니다: 앞 단계마다 마지막 실행이 통과해야 하고(subset부터 모든 단계에 마지막 check가 문제없어야 함), 앞 단계를 다시 돌리면 뒤 단계도 다시 돌려야 합니다(check는 다시 돌려도 결과만 봄). 그래서 잔액 점검이 통과하지 않으면 structure는 거부되고, 저자가 그래도 진행할 때는 `--author-decision TEXT`를 주며 매니페스트에 그 글이 남습니다. 이전 실행이 남긴 `balance_audit.json`이나 `feasibility_t1.json`은 이번 실행의 결과로 적지 않고, 구조 파일럿이 로컬 변경이 있는 파일로 돌았거나 그 기록에 `run_discovery.py`가 확인하는 파일(`PILOT_COMMITTED`) 가운데 빠진 것이 있으면(본 실행이 그런 파일럿을 거부하므로) structure도 멈춥니다. |
| `extract_w1.py` | 7~9월 로그를 추출합니다(scan B). W1 등록 파일과 설정이 바뀐 것 없이 커밋되어 있어야 돌아가고, 두 파일의 SHA-256과 커밋을 `registered-w1/extraction_manifest.json`에 적습니다. |
| `drive_sync.py` | 공개 Google Drive 폴더와 로컬 데이터를 맞춥니다(status, pull, push). |

## 코호트, 계정, 토큰, 가격

| 파일 | 하는 일 |
|---|---|
| `check_account_code.py` | Arbitrum RPC의 `eth_getCode`로 계정 종류를 판정합니다. 바이트코드가 있으면 컨트랙트, 없거나 EIP-7702 위임 표시이면 EOA입니다. 한 블록에서 읽고 그 블록을 기록합니다. 컨트랙트 그래프 수정용 선택 사항(수정 문서 4.2–4.3절): 정한 블록에서 읽기(`--block`, 블록 확인은 실패·속도 제한·오류 응답이면 세 번 더 시도하고, 그 블록을 주는 RPC가 없으면 `--fallback-latest`로 첫 읽기의 최신 블록), RPC 주소 순서(`--rpc`; `--block`이나 `--probe-wallets`로 읽을 때만 환경 변수 `CONTRACT_REP_RPC_URL`이 있으면 맨 앞, 등록 분석의 사용법은 이 변수를 읽지 않음), parquet 입력(`--input-parquet`), 프록시(EIP-1167 복제, ERC-1967, `masterCopy()` 선택자가 있는 Safe 프록시와 그 저장 슬롯 0의 싱글턴)와 스마트 계정(Safe, ERC-4337) 판정(`--probe-wallets`; 프록시는 찾은 구현체의 코드를 봄). 노드가 시간 한도에서 멈춘 호출은 처음 멈춘 RPC에서 세 번(첫 시도 포함), 다음 RPC에서 세 번 보내고(그사이 요청이 세 번 잇달아 실패한 RPC는 건너뜀), 호출마다 멈추지 않은 첫 답을 지키며, 여섯 번 모두 멈출 때만 실패한 호출로 보아 JSON에 개수와 주소를 적습니다. 오류 응답은 코드 3이거나 EVM 오류 문구로 시작할 때만(시스템 주소는 시간 한도의 멈춤 말고는 어떤 오류든) 호출의 실패로 봅니다. 정한 블록을 주는 RPC의 호스트 이름을 JSON에 적습니다(`served_by`). `getThreshold()`·`getOwners()`·`entryPoint()` 호출은 ERC-1967 프록시와 Safe 프록시에는 주소마다 하고, 나머지는 코드 해시마다 대표(가장 낮은 주소) 하나에 해서 같은 해시의 주소에 복사하되, 대표가 32바이트 `getThreshold()` 값을 돌려준 해시는 남은 주소도 하나씩 호출합니다. 호출한 주소마다 threshold, 소유자 수, EntryPoint를 적습니다. JSON에는 호스트 이름만 적고 URL은 적지 않으며, 끊긴 실행은 같은 블록에서만, 수정 분석의 읽기는 스크립트·규칙·입력 주소의 SHA-256(`resume_key`)도 같을 때만 이어 갑니다(다르면 거부하므로 출력을 옮기고 새로 읽음). |
| `balance_audit.py` | 잔액 점검(수정 문서 6절): sql/43의 표본 1,500쌍에서 다시 만든 잔액을 RPC의 `balanceOf`와 대조합니다. T_obs 블록을 주는 RPC가 있으면 그 블록에서 98%, 없으면 최신 블록에서 7~9월에 송금이 없는 주인으로 99%가 맞아야 하고, 미달이면 끝 상태 1로 멈춥니다. 블록을 주는지는 첫 쌍의 `balanceOf`로 보며, 요청 실패·속도 제한·오류 응답이면 세 번 더 시도합니다(수정 문서 4.2절 규칙 2). 어느 RPC도 최신 블록조차 주지 않으면 끝 상태 2입니다. 결과는 `revised-contract-12m/typing/balance_audit.json`에 호스트 이름만 적습니다. |
| `build_cohort.py` | 매칭 코호트(분석 계획 3절)를 정해 `data/2-.../cohort/`에 쓰고 BigQuery에 올립니다. |
| `decode_gmx_events.py` | GMX V2 `EventLog1` `PositionDecrease` 로그를 종료 한 건씩 해독합니다(계정, PnL, 주문 유형, 청산 여부, 크기, 방향). |
| `token_metadata.py` | ERC-20 토큰의 `symbol()`, `name()`, `decimals()`를 한 블록에서 읽습니다. |
| `usd_inputs.py` | 수정 분석의 토큰 목록과 일별 USD 가격을 만듭니다(`data/0-usd-token-list-and-prices/`). |
| `usd.py` | 수정 분석의 USD 금액 계산. SQL(sql/12–18)과 같은 산술을 파이썬으로 적은 것이고, 테스트가 확인합니다. |
| `chainlink_check.py` | DefiLlama 일별 가격을 Arbitrum One의 Chainlink 피드 값과 대조합니다. |

## 점수와 평가

| 파일 | 하는 일 |
|---|---|
| `common.py` | 설정, 경로, GitHub 크기 제한 아래로 나눈 parquet 조각. 변형(`registered`, `usd`, `usd12m`, `contract12m`)마다 경로와 오버레이를 정하고, 오버레이가 정해진 키만 정확히 담는지 검사합니다. |
| `scoring.py` | 가중 PageRank, 결합 보행과 시드 보행, AWP와 EndorseRank의 간선 가중치. 보행은 이전 점수에서 시작(warm start, `init`)할 수 있습니다. |
| `graphs.py` | 간선표를 읽어 한 기준 시점의 모든 점수를 계산합니다. 결과 요약과 표에 쓰는 방법 id(endorserank, awp, cpr_l50 등)가 여기서 정해집니다. 민감도 분석의 고립 노드(`isolated`)는 단층 그래프와 결합 그래프에 모두 더합니다(S-PR 제외). |
| `labels.py` | GMX V2 종료로 만든 트레이더 라벨과 홀드아웃 실행의 공통 도우미 |
| `stats.py` | Kendall τ_b, Spearman ρ, 코호트 단위 짝지은 부트스트랩, 두 순서의 평균 차이와 짝지은 백분위 구간(`paired_mean_contrast`) |
| `crawl.py` | 발견 순서 검정(`../docs/discovery_protocol.md`)의 순수 함수: 컨트랙트 그래프, bow-tie(거대 SCC가 든 약연결 성분 WCC 포함)와 두 우주(out 모드는 SCC ∪ OUT, both 모드는 그 WCC), 시드, 재계산 일정과 구조 파일럿의 규칙(이 순서로 주 모드, 주 우주 P, ρ, |P|로 정하는 q, 멈춤 조건), 한 시드·한 순서의 크롤, 핫셋·곡선·AUC. 보행 점수는 `scoring.py`로 계산하고, 구조 함수는 가중치 코드를 불러오지 않습니다. |
| `run_discovery.py` | 발견 순서 검정의 실행. `--window t1 --feasibility`는 구조 파일럿(가중치·중요도·크롤 없이 구조, 계정 종류 집계, 코드 해시별 코드 계열, 규칙만, `discovery/feasibility_t1.json`)이고, 인자 없이는 T_obs와 t1의 본 실행을 주 모드와 다른 모드로 돌립니다(`--workers N`, 결과는 N과 무관). 판정은 T_obs의 주 모드 실행만 내리고(`decides`), 나머지 파일은 같은 대비를 판정(V1–V3)과 문장 없이 구간이 0 위·아래인지만 적습니다. 본 실행은 중요도가 G 안팎과 bow-tie 부분마다 어디에 있는지(coverage)와 계정 종류를 읽지 않은 주소로 사용자 계정이 보낸 금액도 적습니다. 본 실행은 프로토콜의 「Protocol fixed」 절이 채워지고 코드와 기본 설정 파일이 커밋되어 있어야 돌아갑니다. 파일럿이 커밋된 파일과 지금의 discovery 설정으로 돌았는지, 파일럿이 적은 규칙을 이 코드가 같은 입력에서 다시 내는지, 파일럿 해시가 고정한 값과 같은지, t1 그래프의 크기가 파일럿과 같은지도 크롤 전에 확인하고, 다르면 `author_decision` 없이는 멈춥니다. ρ, q, 주 모드는 `author_decision`이 있어도 규칙이 정한 값이어야 하고, 예산 안의 ρ가 없을 때만 저자가 ρ를 정합니다. |
| `run_same_window.py` | 관측 기간 안의 평가(분석 계획 4–6절)와 규칙 A의 2차 부분 |
| `run_holdout.py` | 홀드아웃 W0(t1 동결, 4~6월 라벨)과 규칙 A의 1차 부분 |
| `run_registered.py` | 등록 창 W1: 규칙 B, 보고할 결과, 어느 간선으로도 만들지 않은 결과와의 비교(등록 순서대로). 트레이더 기준을 계산하므로 `contract12m` 변형에서는 아무것도 읽지 않고 거부합니다(수정 문서 2·11절; 그 변형의 F1·F2·F6 평가는 아직 없음). |
| `run_supplementary.py` | 라벨을 본 뒤 계산한 대비. 어느 규칙에도 속하지 않습니다. |
| `run_robustness.py` | 강건성과 민감도: 상위 토큰 부분 그래프, 표본 정의 |
| `sybil_model.py` | Sybil 비용 모형(5장)의 양 |
| `run_benchmark.py` | 계산 벤치마크(주장 C1)와 규모 확장 |
| `describe_data.py` | 추출한 데이터의 기술 통계(3·4장, 부록 8.4) |
| `run_usd_local.ps1` | 수정 분석의 로컬 평가를 등록 분석과 같은 순서로 돌립니다. `-Variant usd12m`이면 12개월 변형을, `-Variant contract12m`이면 컨트랙트 그래프 수정을 돌리고, 이때는 같은 기간 평가 바로 뒤에 `run_discovery.py`의 본 실행을 `-Workers`개(기본 16, 프로토콜의 실행 시간 추정과 같음) 프로세스로 돌립니다. |

## 결과 공개와 원고

| 파일 | 하는 일 |
|---|---|
| `publish_results.py` | 논문이 인용하는 요약, 설정, 계획 문서를 `data/3-published-results-for-thesis/`에 복사하고 `results_digest.md`(모든 수치와 그 JSON 키)와 `SHA256SUMS.txt`를 씁니다. `--out`은 검증용으로 다른 폴더에 씁니다. |
| `export_latex.py` | 평가 요약 JSON으로 원고의 LaTeX 표와 그림을 서브모듈 `../dissertation/overleaf-github/`에 씁니다. 점수나 통계를 새로 계산하지 않습니다. 12개월 변형은 `--into-manuscript`가 없으면 `data/_work/latex-usd12m/`에 씁니다. |
