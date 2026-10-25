# docs

분석의 규칙을 정한 문서입니다. 결과를 보기 전에 커밋한 문서는 그 뒤로 고치지 않습니다.

| 파일 | 내용 | 고정 |
|---|---|---|
| `analysis_plan.md` | 분석 계획: 데이터, 계정 종류, 코호트, 점수, 점검·라벨·통계, 규칙 A, 등록 창(7절) | 커밋 `43d8045`(2026-10-09 13:41 UTC, 이 연구의 첫 추출 10초 전). 1~6절은 고치지 않습니다. |
| `registration_w1.md` | W1(7~9월) 등록: 창과 코호트, 규칙 B, 보고할 결과 | 커밋 `0d3a057`(같은 날 16:49 UTC, 7~9월 로그 추출 8초 전). 고치지 않습니다. |
| `revision_price_weighting.md` | 수정 분석: USD 금액, 가격을 확인한 다섯 토큰. 등록 결과를 본 뒤의 이탈이라 그 결과를 '등록된 결과'라고 부르지 않습니다. | 수정 점수를 계산하기 전에 커밋(`a897475`, `09dfc32`, `2705b28`) |
| `drive-data-readme.md` | 공개 Google Drive 폴더의 안내문(영문). `../scripts/drive_sync.py push`가 Drive 폴더 맨 위에 `README.md`로 올립니다. | |

`../scripts/publish_results.py`는 앞의 계획 문서를 `../data/3-published-results-for-thesis/`의 `docs/`에 복사합니다. 등록 분석 결과에는 분석 계획과 W1 등록을, 수정 분석 결과(`revised-usd/docs/`)에는 수정 계획까지 세 문서를 둡니다.
