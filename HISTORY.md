# History of this repository

This repository holds the folder `1-Dissertation-Works/ERC20-Allowance-PageRank-Wallet-Reputation` of the authors' private working repository, together with its commit history.

## How the history was copied

- Every commit that changed the folder was copied with its author, committer, dates and message, and the folder became the root of this repository.
- The study began in a sibling folder, `1-Dissertation-Works/ERC20-Allowance-PageRank-Contract-Reputation`. Its commits were copied the same way. Commit `f7a63de` moved the study into the present folder; it has two parents. The first parent is the line of the contract-reputation study, which holds the analysis plan and the W1 registration. The second is the earlier wallet-reputation line, whose material is now in `archive/`.
- Because the copied commits contain only the folder, their identifiers differ from those of the original commits. Documents written in the working repository, such as the extraction manifests, the results digests and these READMEs before this commit, record the original identifiers. The tables below translate them.
- Files that the authors keep private were removed from every commit:
  - correspondence with the supervisors and examiners, their comments, and ethics and submission forms (`proposal/sources/`, `archive/local-other/sources/supervisor-feedback/`, `archive/professor-feedback-summary.md`, `proposal/scripts/_prof_comments_out.txt`, `proposal/scripts/build_correction_table.py`, `proposal/proposal/Correction-Table_Taehong-Kwon_080426_1700.docx`);
  - working copies of the proposal documents (`proposal/archive/`);
  - the authors' internal notes (`dissertation/notes/`);
  - the PDF copies of published articles (`references/*.pdf`).
- Commits that changed only these files were left out. Nothing else was changed: the tree of every copied commit was compared with the original folder and differs only in the paths above.
- Earlier commits contain per-contract parquet files. Later commits leave them out; the files are in a public Google Drive folder, listed with checksums in `experiments/drive-manifest.json`.

## Commits cited in the thesis and the manuscripts

| What | Original commit | Commit in this repository |
|---|---|---|
| Analysis plan and versioned configuration (rule A), committed at 13:41:27 UTC on 9 October 2026 | `43d8045` | `d060f3a` |
| W1 registration (rule B, contrasts P and Q, rules R1–R3), committed at 16:49:32 UTC on 9 October 2026 | `0d3a057` | `1747e64` |
| Results of the registered analysis | `8d8b568` | `344017e` |
| Documents that define the revised analysis (amounts in US dollars, five tokens, twelve-month score windows) | `a897475`, `09dfc32`, `2705b28`, `e6c352d` | `1d4b9d6`, `d4796eb`, `52aa40b`, `69c7d12` |
| Code revision of the revised results | `0a94215` | `77a1e49` |
| Revised results | `950a7a4` | `dbe9ad6` |
| Drive manifest of the per-contract files | `ac7d32a` | `ce4e9d8` |
| Move of the study into this folder (merge of the two lines) | `951923a` | `f7a63de` |

## All 93 copied commits, newest first

| Original | Here | Folder | Message |
|---|---|---|---|
| `55dbfbc` | `ac27135` | Wallet-Reputation | docs: 투고 원고 A·B를 저자가 읽을 쉬운 한국어 해설판으로 풀어 쓴다(원고 07391e9) |
| `b67542e` | `63184f9` | Wallet-Reputation | docs: 원고 서브모듈을 투고 원고 두 편을 12개월 결과로 다시 쓴 판(07391e9)으로 올리고 변경 기록에 적는다 |
| `c5ef6f5` | `438e3ba` | Wallet-Reputation | docs: 원고 서브모듈을 표 1.2와 표 5.1을 고친 판(392937a)으로 올리고 변경 기록에 원고 push를 적는다 |
| `bb1cc0b` | `af165a0` | Wallet-Reputation | docs: 한국어 번역본의 표 1.2와 표 5.1을 원고에 맞춰 한 쪽에 들어가게 줄인다 |
| `5a61003` | `cfcbcfa` | Wallet-Reputation | data: 걷기가 원시 차수를 이긴 까닭의 사후 점검 결과를 낸다(이득은 최신성에서 오고 전파는 더하지 않음) |
| `6a59e64` | `a7abf02` | Wallet-Reputation | docs: 기간 밖에서 걷기가 원시 차수를 이긴 까닭을 나눠 보는 사후 점검의 설계와 코드를 계산 전에 커밋한다 |
| `ea989b4` | `1cc0f3c` | Wallet-Reputation | docs: 원고 서브모듈을 번역 중에 찾은 원문 오류를 고친 판(6a5dfb6)으로 올리고 변경 기록에 번역본과 발표 자료를 적는다 |
| `dd93270` | `9136ba3` | Wallet-Reputation | docs: 발표 자료를 12개월 점수 기간으로 다시 쓴 원고와 결과에 맞춘다 |
| `0598d46` | `dfaf7de` | Wallet-Reputation | docs: 한국어 번역본을 되살리고 12개월 점수 기간으로 다시 쓴 원고(6a5dfb6)에 맞춰 다시 옮긴다 |
| `b17a3a3` | `0a61762` | Wallet-Reputation | docs: 안내 문서가 12개월 주 분석의 변형, 결과 경로, 표 내보내기 명령을 가리키게 한다 |
| `35a1299` | `d10dc63` | Wallet-Reputation | feat: 결과 요약이 바뀌었을 때 원고 수치를 옛 요약과 새 요약에 대조하는 도구를 더한다 |
| `4b0f3a7` | `898a163` | Wallet-Reputation | docs: 원고 서브모듈을 12개월 점수 기간으로 다시 쓴 원고(7c820a2)로 올리고 원고 메모와 변경 기록을 맞춘다 |
| `ac7d32a` | `ce4e9d8` | Wallet-Reputation | data: 12개월 변형의 새 파일 79개를 Drive에 올리고 원장과 토큰 목록 README를 교체한 목록으로 manifest를 갱신한다 |
| `950a7a4` | `dbe9ad6` | Wallet-Reputation | data: 12개월 변형의 BigQuery 나머지 단계, 로컬 평가, 결과 요약을 낸다 |
| `0a94215` | `77a1e49` | Wallet-Reputation | data: 12개월 변형의 토큰 행 수, 동결마다의 코호트, W0 기간의 USD 상수(m_T 170, m_A 100, U 19,000)를 12개월 점수 계산 전에 커밋한다 |
| `e6c352d` | `69c7d12` | Wallet-Reputation | feat: 동결마다 직전 12개월로 점수를 만드는 12개월 변형(usd12m)을 12개월 숫자를 하나라도 계산하기 전에 더한다 |
| `e2d548e` | `eaa36b6` | Wallet-Reputation | chore: republish the revised results digest from e9feac2 and sync it to Drive |
| `efea428` | `17c71c6` | Wallet-Reputation | docs: keep C-AWP to future work in the notes, READMEs and table export |
| `696db74` | `a6909d2` | Wallet-Reputation | Merge origin/master into claude/cpr-main-method |
| `346acda` | `5fb3783` | Wallet-Reputation | feat: make C-PR the thesis method and sync its contrasts to Drive |
| `16b30bd` | `44c952a` | Wallet-Reputation | docs: README를 폴더마다 나누고, 루트 README에는 저장소 전체 안내만 남긴다 |
| `901cc59` | `da69e51` | Wallet-Reputation | refactor: 학위논문 참고 문헌을 papers/에서 학위논문 폴더의 references/로 옮긴다 |
| `458d774` | `1c353b9` | Wallet-Reputation | docs: 원고 서브모듈을 검토 반영본(4391b64)으로 옮긴다 |
| `b00c6f5` | `1d00446` | Wallet-Reputation | fix: 사후 비교 표가 한 쪽에 들어가도록 설명을 줄이고 상위 1,000 블록을 본문으로 옮긴다 |
| `d17ddb7` | `156f366` | Wallet-Reputation | docs: 사후 점검 폴더의 안내를 논문이 실제로 인용하는 것과 맞춘다 |
| `aa99330` | `d6a22b9` | Wallet-Reputation | fix: 대비 표의 머리글을 τ(a), τ(b)로 바꿔 Kendall τ_a, τ_b와 헷갈리지 않게 한다 |
| `3f31cd4` | `70eee25` | Wallet-Reputation | feat: C-PR 송금 층과 AWP의 차이를 남기고 사후 비교 표에 넣는다 |
| `4f097f2` | `1d3cac1` | Wallet-Reputation | feat: C-PR 송금 층과 AWP의 차이를 보는 덧붙임 점검을 계산 전에 적어 둔다 |
| `4eea281` | `df1ada2` | Wallet-Reputation | feat: C-PR과 C-AWP를 AWP와 견준 사후 점검 표를 만든다 |
| `2b91fda` | `cfcd741` | Wallet-Reputation | feat: C-PR과 C-AWP를 AWP와 견준 사후 점검 결과를 남긴다 |
| `500b66f` | `4ac0f7f` | Wallet-Reputation | fix: 사후 점검 스크립트가 공개 점수 표를 맞는 폴더에서 읽게 한다 |
| `21e6de6` | `e4a2c07` | Wallet-Reputation | feat: C-PR을 AWP와 견주는 사후 점검의 설계를 계산 전에 적어 둔다 |
| `42c37bd` | `2bf61c3` | Wallet-Reputation | Merge pull request #15 from abitocodes/claude/brave-keller-pqexh6 |
| `327dbb3` | `5125dbf` | Wallet-Reputation | feat: keep the endorsement-count and coupled-walk checks of EndorseRank |
| `7486bff` | `acb129a` | Wallet-Reputation | feat: keep the post hoc check of EndorseRank without the time weight |
| `d14e771` | `72abd04` | Wallet-Reputation | feat: keep the post hoc unlimited-allowance checks and their Drive data |
| `144972a` | `f4c572a` | Wallet-Reputation | docs: 해설 영상 길이를 다시 그린 최종본 값으로 고친다 |
| `1786f86` | `9070cbb` | Wallet-Reputation | fix: 붙어 있는 표시는 하나로 묶고 문단 속 낱말의 테두리가 다음 줄을 긋지 않게 한다 |
| `245f66a` | `4fc4cdf` | Wallet-Reputation | fix: 확대한 화면에 덱 머리말이 겹치지 않게 하고 강조 테두리가 옆 줄을 긋지 않게 한다 |
| `179729b` | `5d76ab1` | Wallet-Reputation | docs: 발표 자료 안내에 해설 영상 도구를 적고 영상 길이를 실제 값으로 고친다 |
| `1c5b8a1` | `b3d34ef` | Wallet-Reputation | fix: 두 시간짜리 소리를 30초씩 만들어 메모리가 넘치지 않게 한다 |
| `0fd9d11` | `f6388c2` | Wallet-Reputation | fix: 장이 바뀔 때 두 악장이 같은 구간에서 엇갈려 줄어들고 커지게 한다 |
| `84b7a8a` | `24eed18` | Wallet-Reputation | fix: 조각 기록을 쓰는 줄을 try 블록 안으로 옮긴다 |
| `af45148` | `b7c9c94` | Wallet-Reputation | fix: 영상 조각마다 새 페이지를 열고 실패한 조각은 다시 그린다 |
| `be1909a` | `e706c20` | Wallet-Reputation | perf: 영상 조각을 faster 프리셋, CRF 20으로 압축한다 |
| `101b325` | `3e2713b` | Wallet-Reputation | feat: 잘못 들린 내레이션 줄을 큰 Whisper로 다시 듣고 다시 읽는다 |
| `4309e0d` | `0ee9770` | Wallet-Reputation | docs: 해설 영상의 내레이션 대본과 설명서를 더한다 |
| `136f8af` | `006dda5` | Wallet-Reputation | fix: 카메라가 짧은 줄마다 들락날락하지 않게 하고 음성 합성을 더 빠르게 한다 |
| `f116f38` | `a281475` | Wallet-Reputation | perf: 음성 합성의 단계 수와 다시 읽기 기준을 낮춘다 |
| `761afdc` | `1b4c574` | Wallet-Reputation | fix: 여는 카드와 닫는 카드의 제목을 정한 자리에서 줄을 바꾼다 |
| `0bb3e64` | `199e8fa` | Wallet-Reputation | fix: 영상 카드의 그림을 제목에서 떼고 말 속도와 소리 파일 이름을 고친다 |
| `c569422` | `9225dbd` | Wallet-Reputation | feat: 발표 슬라이드로 유튜브 해설 영상을 만드는 도구를 더한다 |
| `9539668` | `e073b7f` | Wallet-Reputation | docs: 원고 포인터를 두 투고 원고를 고친 커밋 96910e8로 옮긴다 |
| `5365a6a` | `5333033` | Wallet-Reputation | feat: 발표 자료 한국어판의 인쇄판(클릭 단계마다 한 쪽, 304쪽)을 만든다 |
| `5b8ffb3` | `8b40eaa` | Wallet-Reputation | Merge pull request #11 from abitocodes/claude/brave-keller-pqexh6 |
| `603e832` | `91be6ac` | Wallet-Reputation | docs: 원고 포인터를 7790f76 본문으로 되돌리고 새 데이터의 수치를 넣은 원고 커밋 b96f0c1로 옮긴다 |
| `d815b68` | `dce85e4` | Wallet-Reputation | feat: 발표 자료의 한국어판과 영문판을 각각 HTML 한 파일로 묶어 올린다 |
| `cbc09b2` | `bdb3552` | Wallet-Reputation | wip: 영문판 네 가지 점수 절을 마치고 번역 중간 상태를 올린다 |
| `3abe074` | `d0fce38` | Wallet-Reputation | wip: 영문판 화살표의 무게 절을 마치고 번역 중간 상태를 올린다 |
| `70dd147` | `c602c3b` | Wallet-Reputation | wip: 영문판 페이지랭크 유도 절을 마치고 번역 중간 상태를 올린다 |
| `abb52aa` | `869c63f` | Wallet-Reputation | wip: 영문판 번역 중간 상태를 올린다 |
| `b02f89a` | `6154c19` | Wallet-Reputation | wip: 영문판 결과 절의 번역 중간 상태를 올린다 |
| `6f66b76` | `c866b11` | Wallet-Reputation | wip: 영문판 허락과 송금 절을 마치고 다른 절의 번역 중간 상태를 올린다 |
| `eee0949` | `9c0513a` | Wallet-Reputation | wip: 영문판 정리 절을 마치고 다른 절의 번역 중간 상태를 올린다 |
| `7d8c391` | `57bcd9d` | Wallet-Reputation | wip: 영문판 여는 질문 절을 마치고 다른 절의 번역 중간 상태를 올린다 |
| `f8a8b53` | `48ba747` | Wallet-Reputation | wip: 발표 자료에 영문판 골격과 한 파일 묶기 스크립트를 더한다(번역 중) |
| `5cbe86d` | `abd95d7` | Wallet-Reputation | docs: 한국어 번역본 overleaf-github-ko를 지우고 안내 문서에서 그 경로를 뺀다 |
| `0d7ecf7` | `fe89a9b` | Wallet-Reputation | docs: record the rclone OAuth client and cloud Drive access, drop old-folder ignore |
| `8356f3f` | `f37de84` | Wallet-Reputation | feat: 블록체인 parquet 데이터를 공개 Google Drive로 옮기고 수동 동기화 스크립트를 더한다 |
| `6ce5615` | `5040203` | Wallet-Reputation | chore: ignore leftover local data and advance manuscript pointer to main |
| `840ae8c` | `191f9d1` | Wallet-Reputation | docs: 저자 결정에 따라 추출 시점 표현을 이 연구 기준으로 맞추고 제목을 대비하는 문구를 뺀다 |
| `2f62376` | `c080d43` | Wallet-Reputation | feat: 학위논문 발표 자료(HTML 슬라이드 59장)를 검토 결과대로 고쳐 마무리한다 |
| `d4e8fdc` | `2d45fec` | Wallet-Reputation | wip: 발표 자료의 11개 절을 모두 채운다(59장, 검토 반영 전) |
| `46e9517` | `b88e3bc` | Wallet-Reputation | wip: 발표 자료의 여는 질문, 허락과 송금, 데이터의 세계 절을 채운다 |
| `91eb664` | `2d8fa1b` | Wallet-Reputation | docs: 원고 포인터를 투고 원고 두 편과 보조 분석을 컨트랙트 평판 연구로 다시 쓴 원고 커밋 38a2184로 옮긴다 |
| `6432db4` | `c67d465` | Wallet-Reputation | wip: 학위논문 발표 자료(HTML 슬라이드)의 골격, 데이터, 스토리보드를 올린다 |
| `d9302ad` | `844a625` | Wallet-Reputation | docs: 한국어 번역본의 용어를 장마다 하나로 맞추고 줄임말 표를 한 쪽에 넣는다 |
| `5141854` | `9f60cc8` | Wallet-Reputation | docs: 컨트랙트 평판 원고의 쉬운 한국어 번역본을 만든다 |
| `951923a` | `f7a63de` | Wallet-Reputation | refactor: 컨트랙트 평판 논문을 지갑 평판 폴더로 옮기고 지갑 평판 자료는 archive에 보관한다 |
| `4ab5575` | `17db6ce` | Contract-Reputation | docs: 원고 전 장을 수정 분석(USD, 상위 5개 토큰) 수치로 고치고 등록 분석은 부록 8.6에 남긴 뒤 main.pdf를 다시 빌드한다 |
| `77e71f5` | `ffd3919` | Contract-Reputation | feat: 수정 분석(USD, 상위 5개 토큰)의 평가 결과·digest·표를 만들고 3장과 부록 e를 개정한다 |
| `2705b28` | `52aa40b` | Contract-Reputation | docs: C-PR 승인 층 상한을 송금 99번째 백분위(USD 20,000)로 고치고 상수(m_T 200, m_A 62)를 수정 점수 계산 전에 커밋한다 |
| `09dfc32` | `d4796eb` | Contract-Reputation | docs: 수정 분석을 가격이 확인된 상위 5개 토큰(WETH, USDC, USD₮0, ARB, WBTC)으로 정하고 토큰·가격 입력을 수정 점수 계산 전에 커밋한다 |
| `a897475` | `1d4b9d6` | Contract-Reputation | docs: 금액을 USD로, 토큰을 가격 확인 목록으로 바꾸는 수정 계획(등록 이후 이탈)을 수정 점수 계산 전에 커밋한다 |
| `f6e993e` | `8f743b7` | Contract-Reputation | docs: 거버넌스 위험 인용을 동료 심사 논문(fritsch2024voting)으로 바꾸고, 1장·4장의 코호트 규칙 반복을 3장 참조로 줄이고 main.pdf를 다시 빌드한다 |
| `73b0ab4` | `8b3f689` | Wallet-Reputation | docs: 한국어판 원고의 초록 수정과 다시 빌드한 main.pdf를 커밋한다 |
| `f33a87a` | `7054746` | Contract-Reputation | docs: 컨트랙트 평판 논문 원고 전 장을 새 데이터로 개정하고 벤치마크와 데이터 설명을 더한다 |
| `8d8b568` | `344017e` | Contract-Reputation | feat: W1 등록 평가·강건성·Sybil 모형 결과와 표 내보내기, 원고 2장·앞부분 개정을 더한다 |
| `0d3a057` | `1747e64` | Contract-Reputation | feat: 컨트랙트 평판 논문의 추출·평가 코드와 W1 등록 문서를 2차 추출 전에 커밋한다 |
| `43d8045` | `d060f3a` | Contract-Reputation | feat: 컨트랙트 평판 논문의 분석 계획·설정·추출 SQL을 데이터 추출 전에 고정한다 |
| `4c60fb4` | `20e6e94` | Wallet-Reputation | docs: 원고 포인터를 원고 B를 IEEE Access 템플릿으로 옮기고 두 투고 원고를 채운 원고 main 7790f76으로 옮긴다 |
| `3f22872` | `da6c756` | Wallet-Reputation | docs: 원고 포인터를 결과 표 주석과 부록의 실험 폴더 경로를 새 위치로 고친 원고 main c034b38로 옮긴다 |
| `1c231fc` | `f27182d` | Wallet-Reputation | chore: 제안서와 논문 작업을 1-Dissertation-Works/<논문 제목>/ 아래 proposal·dissertation으로 합치고, 3-Career를 지우고 4·5번을 2·3번으로 당긴다 |
