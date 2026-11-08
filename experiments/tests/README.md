# tests

`experiments/`에서 `python -m pytest tests`로 돌립니다.

점수와 통계는 보관한 지갑 평판 연구의 스크립트를 기준 구현으로 삼아 대조합니다. `conftest.py`가 그 스크립트(`../../archive/wallet-reputation-experiments/scripts/`)를 읽기 전용으로 불러오므로, 그 폴더를 옮기거나 지우면 테스트가 깨집니다.

| 파일 | 확인하는 것 |
|---|---|
| `conftest.py` | 테스트의 경로, 기준 스크립트를 읽기 전용으로 불러오기(바이트코드를 남기지 않음), 게이트 B 개정의 파일 목록 파서(`gate_b_amendment_files`), 느린 테스트 표시(`slow`, `CONTRACT_REP_SLOW_TESTS=1`일 때만 돎) |
| `c12_world.py` | 컨트랙트 그래프 수정의 게이트 B 테스트가 함께 쓰는 도우미: 내려받는 표 16개의 열과 형식(INTERFACE), 합성 contract12m 세계(실행 기록 포함)와 앞 변형들의 세계, d39775c 코드의 모래 상자, 기록기, BigQuery 상한 식의 계산기, 코드 경로 비교 |
| `pytest.ini` | pytest 설정 |
| `test_scoring.py` | `scoring.py`를 기준 구현(`pagerank.py`, `pagerank_variants.py`, `holdout.py`)과 대조 |
| `test_stats.py` | `stats.py`를 기준 구현(`evaluate_alignment.bootstrap_alignment`)과 대조 |
| `test_usd.py` | USD 환산, b = ln 3 / m인 값 변환, 가격 표, 수정 분석의 SQL |
| `test_usd12m.py` | 12개월 변형: 경로, 오버레이가 `usd12m`에만 적용되는지, 고정 파일과 sql/01–19가 `fab8d63`과 같은지, 작업마다 만드는 테이블의 접두사·읽는 테이블·매개변수, 거부 동작, 비용 추정 |
| `test_account_code.py` | `check_account_code.py`: 등록 분석의 사용법이 예전 스크립트와 같은 parquet을 쓰는지(환경 변수 `CONTRACT_REP_RPC_URL`이 있어도 `accounts.rpc_url`만 읽는지), 코드·프록시·Safe·ERC-4337 판정(`masterCopy()` 선택자의 PUSH4·PUSH32 형태, Safe 프록시는 슬롯 0의 싱글턴 코드를 봄), 호출 범위(ERC-1967 프록시와 Safe 프록시는 주소마다, 대표가 `getThreshold()`에 답한 코드 해시는 남은 주소도, 나머지는 대표의 결과를 복사), 노드의 시간 한도 중단은 다시 보내기, 시스템 주소의 오류, 블록 고정과 대체(블록 확인의 세 번 재시도), RPC 순서와 호스트 이름만 기록, 이어 가기(어느 단계에서 끊겨도 끊기지 않은 실행과 같은 parquet, 스크립트·규칙·입력 주소가 바뀌면 거부; RPC는 가짜) |
| `test_contract12m_pipeline.py` | `run_contract12m_pipeline.py`와 sql/24–35·43: 단계 순서와 앞 단계를 기다리는 규칙(모든 단계가 문제없는 마지막 check를 기다림, 잔액 점검이 통과하지 않으면 structure 거부, 이전 실행의 결과 파일은 적지 않음), 게이트 B 거부, 작업마다 만드는 `c12_` 테이블·읽는 테이블·공개 view·매개변수(대기열 K는 시스템 주소를 빼지 않고 노드 집합만 뺌), 비용 추정과 상한, 커밋 검사(수정 문서 12절의 파일 목록, 구조 파일럿이 확인하는 파일이 그 안에 있는지, 파일럿 기록에 빠진 파일), `balance_audit.py`의 일치 규칙(네트워크는 가짜), 게이트 B 단계(constants, pairs, rest, checks, download)의 거부 조건(「Protocol fixed」와 파일럿 해시, 게이트 B 파일의 커밋, 게이트 B 뒤 게이트 A 단계의 거부, 상수의 따로 커밋(상수·실행 매니페스트·원장 세 파일만 담은 커밋)과 다시 돌리기 거부, job 39의 측정 항이 보정한 입력이 처음 보정한 청구 뒤에 바뀌면 rest와 checks가 거부하는지(게이트 A의 원천 표 확인은 d39775c와 같음)), 게이트 B 작업의 등록·추정·상한·비용 예상(투영에 필요한 상한과 예산을 센트 단위로 올려 적는 `cap needed`·`budget needed` 줄), `constants.json`의 반올림, 내려받기와 그 검증 |
| `test_contract12m_sql.py` | sql/36–42: 앞의 SQL(13–17, 35)에서 옮긴 줄이 그대로인지(상수의 열 이름과 분위수, T_obs 갈래의 잔액과 가격, 중요도의 최신 승인·가격·유입 창까지), 잔액 상한 식을 sql/35와 `usd.py`의 Python 거울에 맞춰 계산, 내려받는 표의 열과 형식이 INTERFACE와 같은지, sql/42의 검사 이름 |
| `test_contract12m_eval.py` | contract12m의 평가 코드: 규칙 B의 키(블록마다 정확한 키 집합)와 문구(「Rule B met」 없음, 규칙 B를 이름에 단 다른 키나 'met'·'holds'만 적은 값도 없음), 트레이더·GMX 출력 없음, 민감도 2의 고립 노드(결합 보행 포함, 가중치 0인 쌍만 가진 구성원 포함), 그래프 밖 구성원은 0점, 포함 범위, 기준선, 상한 없는 민감도(기준선도 상한 없는 그래프에서 셈), 라벨 분할, 커밋과 내려받기 검사(단계 순서 포함, 스크립트마다 내려받기가 확인하지 않은 stem의 거부와 입력 기록, `run_robustness`가 다른 내려받기에서 나온 앞선 평가 출력을 거부하는지), 아직 이 변형의 갈래가 없는 다섯 스크립트의 거부 |
| `test_crawl.py` | `crawl.py`와 `run_discovery.py`: 일정과 정확한 비율, bow-tie(가장 큰 WCC가 거대 SCC를 담지 않는 그래프 포함)와 시드, 순서마다의 크롤(BFS와 무작위 순서는 ρ와 무관), 보는 그래프 위의 보행이 `scoring.py`와 같은지, 곡선과 AUC, 구조 파일럿의 규칙(out과 both가 주 모드일 때)과 계정 종류·코드 계열 집계, 파일럿이 가중치 코드를 쓰지 않는지, 「Protocol fixed」 검사(파일럿의 코드 상태와 설정, 이 코드로 다시 계산한 규칙, 저자 결정이 있어도 규칙이 정한 ρ·q·주 모드 포함), t1 그래프와 파일럿 크기의 비교, 중요도 표(G 밖은 id −1)와 coverage, 합성 게이트 B 표의 본 실행(두 동결 × 두 모드, 판정은 T_obs의 주 모드에서만, 나머지 파일에는 V 코드 없음)과 그 표의 열·형식, 출력의 |G|(`g_nodes`), 그리고 `scoring.py`의 warm start, 결합 그래프에도 더하는 고립 노드(`graphs.score_all`)와 `stats.py`의 `paired_mean_contrast` |
| `test_contract12m.py` | 컨트랙트 그래프 변형 전체: 변형마다의 경로·설정·`run_bq.py` 예산(앞의 세 변형은 이 수정 전 커밋의 `common.py`와 같음), 오버레이 키 검사, `check_tables`의 공개 view 허용, `run_registered.py`가 이 변형에서는 자기 W1 평가 갈래로 가는지, 고정 파일과 게이트 A 파일의 해시, 앞 변형들의 출력과 코드 경로가 d39775c와 같은지, 이 변형의 두 폴더(`revised-contract-12m/`, `contract-12m/`)만 바이트 그대로 커밋하게 하는 저장소 루트의 `.gitattributes`, 게이트 B 상태(「Protocol fixed」와 수정 문서의 날짜 붙은 개정: 자리표시가 다 채워졌는지, 파일럿의 수·규칙과 상한 문장이 맞는지, 커밋된 파일럿이 고정한 해시인지; `-k "not gate_b_state"`로 빼고 돌릴 수 있음), 드라이버의 typing 명령 → `check_account_code.py` → 대기열 검사 → 구조 파일럿(그 출력의 계정 종류와 코드 계열까지), 공유 경로, 가짜 메타데이터 위의 check 단계(게이트 B 작업은 투영으로만 판단하고, 투영에 필요한 상한과 예산을 적음) |
| `test_drive_sync.py` | `drive_sync.py`의 경로 규칙: Drive 경로, 로컬 경로, 제외할 파일, 패턴 |
