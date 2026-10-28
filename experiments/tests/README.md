# tests

`experiments/`에서 `python -m pytest tests`로 돌립니다.

점수와 통계는 보관한 지갑 평판 연구의 스크립트를 기준 구현으로 삼아 대조합니다. `conftest.py`가 그 스크립트(`../../archive/wallet-reputation-experiments/scripts/`)를 읽기 전용으로 불러오므로, 그 폴더를 옮기거나 지우면 테스트가 깨집니다.

| 파일 | 확인하는 것 |
|---|---|
| `conftest.py` | 테스트의 경로, 기준 스크립트를 읽기 전용으로 불러오기(바이트코드를 남기지 않음) |
| `pytest.ini` | pytest 설정 |
| `test_scoring.py` | `scoring.py`를 기준 구현(`pagerank.py`, `pagerank_variants.py`, `holdout.py`)과 대조 |
| `test_stats.py` | `stats.py`를 기준 구현(`evaluate_alignment.bootstrap_alignment`)과 대조 |
| `test_usd.py` | USD 환산, b = ln 3 / m인 값 변환, 가격 표, 수정 분석의 SQL |
| `test_usd12m.py` | 12개월 변형: 경로, 오버레이가 `usd12m`에만 적용되는지, 고정 파일과 sql/01–19가 `fab8d63`과 같은지, 작업마다 만드는 테이블의 접두사·읽는 테이블·매개변수, 거부 동작, 비용 추정 |
| `test_drive_sync.py` | `drive_sync.py`의 경로 규칙: Drive 경로, 로컬 경로, 제외할 파일, 패턴 |
