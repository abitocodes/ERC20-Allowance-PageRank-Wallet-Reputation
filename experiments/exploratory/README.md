# exploratory

등록 분석과 수정 분석의 결과를 모두 본 뒤에 한 사후 점검입니다. 분석 계획, W1 등록, 수정 계획에 들어 있지 않으므로, 여기 결과는 등록된 시험을 대신하지 않습니다. 기준은 모두 수정 분석(`CONTRACT_REP_VARIANT=usd`)의 코호트, 라벨, 짝지은 부트스트랩입니다. 폴더마다 README에 질문, 설계, 결과가 있습니다.

| 폴더 | 질문 | 원고에서 |
|---|---|---|
| [`2026-10-13-unlimited-allowances/`](2026-10-13-unlimited-allowances/) | 무제한 허락을 빼거나 USD 잔액으로 가중하면 결과가 어떻게 바뀌나 | 보고하지 않음 |
| [`2026-10-14-endorsement-count-variants/`](2026-10-14-endorsement-count-variants/) | EndorseRank에서 주인의 표를 세는 방식을 바꾸면 | 30일 모멘텀 기준선(`mom30`)만 5장(sub:threat-construct)에서 구성 타당도 위협으로 인용 |
| [`2026-10-14-freeze-date-time-weight/`](2026-10-14-freeze-date-time-weight/) | 동결일에 유효한 허락을 그날 기준으로 세면(시간 가중을 빼면) | 보고하지 않음 |
| [`2026-10-14-role-coupled-walk/`](2026-10-14-role-coupled-walk/) | 주인이 받은 송금으로 주인에게 평판을 주는 역할 결합 보행이 C-PR보다 나은가 | 보고하지 않음 |
| [`2026-10-22-cpr-against-awp/`](2026-10-22-cpr-against-awp/) | 허락 간선이 AWP 자체에 무엇을 더하나(C-PR, C-AWP 대 AWP) | 보고하지 않음. C-AWP는 6장 향후 연구에 이름만 나오고(2026-10-22 결정, 10-27 재확인), C-PR 대 AWP의 커버리지 결과는 논문이 `scripts/run_supplementary.py`로 다시 계산해 4장(sub:cpr-contrasts, 표 cpr-contrasts)에 씀. 비교 목록은 계산 전에 커밋 |
| [`2026-10-28-recency-and-depth/`](2026-10-28-recency-and-depth/) | 기간 밖에서 페이지랭크가 원시 차수를 이긴 것(등록 분석의 AWP)은 어디서, 왜 생겼나(대상 계약, 최신성과 전파, 깊이) | 아직 보고하지 않음(5장에 넣을지는 저자 판단). 비교 목록은 계산 전에 커밋. 기준은 등록 분석과 12개월 주 분석 |

폴더마다 `scripts/`(와 `sql/`)에 그 점검의 코드가, 맨 위에 결과 파일(JSON, CSV)이 있습니다. 새로 받은 BigQuery 표는 `../data/1-raw-blockchain-extracts/exploratory-2026-10-13/`, `exploratory-2026-10-14/`에 있습니다.
