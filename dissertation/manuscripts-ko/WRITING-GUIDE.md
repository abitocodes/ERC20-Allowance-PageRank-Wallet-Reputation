# 해설판 쓰기 기준: 투고 원고 A·B → 쉬운 한국어

## 0. 무엇을 쓰는가

투고 원고 A(PLOS ONE)와 B(IEEE Access)의 영문 원고(`../overleaf-github/manuscripts/`)를 **쉬운 한국어 해설판**으로 다시 써요. 저자가 자기 원고를 한국어로 정확하고 편하게 읽기 위한 판이고, Overleaf와 원고 저장소에는 올리지 않아요.

- **문장 대 문장 번역이 아니에요.** 원고의 절 순서를 따르되, 절마다 내용을 쉬운 한국어로 풀어 써요. 긴 문장은 나누고, 순서는 한국어로 읽기 좋게 바꾸고, 어려운 개념은 풀이 상자로 설명해요.
- **내용은 빠짐없이 담아요.** 원고의 주장, 수치, 구간, 판정, 단서(“라벨을 본 뒤 계산함”, “등록한 시험이 아님”, “표본이 작음” 같은 것), 한계, 표, 그림, 식이 모두 들어가야 해요.
- **원고에 없는 주장은 덧붙이지 않아요.** 풀이 상자도 원고의 정의와 결과 안에서만 설명해요. 해석, 평가, 추측, 앞으로의 계획을 새로 만들지 않아요.

## 1. 말투와 낱말

- 해요체로 써요(학위논문 한국어판 `../overleaf-github-ko/`과 같은 말투). 표 머리글, 캡션의 명사구, 목록의 짧은 항목은 명사형으로 끝내도 돼요.
- 한 문장에 한 생각. 쉬운 우리말을 골라요: 활용하다 → 쓰다, 산출하다 → 구하다, 상회하다 → 넘다, 수행하다 → 하다.
- 번역투를 피해요: “~에 대한”, “~를 통해”, “~에 있어서”, “~되어진다”, “~로 인해”, “~하는 것이 가능하다”.
- 용어는 `../overleaf-github-ko/TRANSLATION-GUIDE.md`의 §5, §5b를 그대로 따라요. 자주 나오는 말:

| 영어 | 한국어 |
|---|---|
| allowance / approval / approve | 허락 / 허락 / 허락하다 |
| owner / spender | 주인 / 스펜더 |
| transfer, sender, recipient | 송금, 보낸 쪽(송신자), 받는 쪽(수신자) |
| in-approve degree, count of approving owners | 받은 허락 수(허락한 주인 수) |
| transfer in-degree | 송금 입차수 |
| raw degree | 원시 차수(화살표를 그냥 센 수) |
| new approval pairs / new transfer senders | 새 허락 쌍 / 새 송금자 |
| EndorseRank, AWP, C-PR, S-PR | 엔도스랭크, AWP, C-PR, S-PR(표와 그림 안에서는 영어 이름) |
| activity restarts / uniform restarts | 활동 재시작 / 고르게 다시 출발하기(균등 재시작) |
| freeze, score window, label window | 동결, 점수 기간, 라벨 기간 |
| same window / out of window | 같은 기간 / 기간 밖 |
| registered analysis / revised analysis / re-analysis | 등록 분석 / 수정 분석 / 재분석 |
| liquidation-free close rate (LFCR) | 청산 없이 닫은 비율(LFCR) |
| profitable share / non-loss share / realized gain | 이익을 낸 비율 / 손실이 아닌 비율 / 실현 이익 |
| recipients (traders) | 허락을 받은 트레이더 |
| closed form, depth-one spender | 닫힌 식, 깊이 1인 스펜더 |
| intended-construct check | 의도한 구성개념 점검 |
| paired bootstrap, percentile interval | 짝지은 부트스트랩, 백분위 구간 |

## 2. 문서 구성

1. 제목 블록: 한국어 제목, 영문 제목, 저자(영문 그대로), 투고처, 원문의 판(원고 저장소 커밋).
2. 「이 글을 읽는 법」(반 쪽 안): 본문과 상자의 관계, 수와 구간 읽는 법.
3. 「한눈에 보기」(한 쪽 안팎): 질문, 자료, 비교한 점수, 주요 결과(수치와 함께), 꼭 붙여야 하는 단서.
4. 「먼저 알아 둘 말」: 용어 풀이 표.
5. 원고의 절을 순서대로, 번호를 붙여서. 절마다 맨 앞에 `yoji` 상자.
6. 「투고 서류에 들어가는 것」: 윤리, 자료 공개, 생성형 AI 사용, 감사의 말, 보조 자료 같은 투고 양식의 부분을 짧게.
7. 참고문헌(영문 그대로).

## 3. 상자

- `\begin{yoji} … \end{yoji}`: 그 절의 요점을 한두 문장으로. 원고의 내용만 담아요.
- `\begin{puri}[제목] … \end{puri}`: 개념 풀이, 작은 예, 표와 그림 읽는 법. 제목은 질문형이 좋아요(“켄달의 타우는 무엇인가요?”).
- 상자 밖의 본문이 원고의 내용이에요. 상자 두 종류는 원고에 없어요. 이 점을 「이 글을 읽는 법」에 적어요.

## 4. 수치

- 원고의 수를 그대로 써요. 반올림하지 않고 부호를 지켜요. 음수는 본문에서 `−0.038`처럼 유니코드 빼기(U+2212)로 쓰고, 식 안에서만 `$-$`를 써요. 구간은 `[−0.043, −0.032]`.
- 예를 들려고 지어낸 수는 `\ill{…}`로 감싸요(점검에서 빠져요).
- 표는 한국어 머리글로 다시 짜되, 칸의 수는 영문 표와 같게 해요. 표 아래의 출처 경로(`revised-usd-12m/...`)는 짧게 남겨도 돼요.
- 글자 크기는 `\fontsize` 대신 `\small`, `\footnotesize`로 바꿔요.
- 점검: `python -I -X utf8 check_numbers.py <폴더>`. 「한국어에만 있는 수」와 「부호가 다른 수」는 0개여야 해요. 「한국어에 없는 수」는 하나씩 보고, 빠뜨린 내용이면 넣어요.

## 5. 지켜야 하는 서술 규칙

저장소의 모든 글에 적용되는 규칙이에요(`HANDOFF.md`, 학위논문 메모).

- 무엇이 공개되거나 GitHub에 올라간 날짜·시각을 쓰지 않아요. 커밋 시각과 BigQuery 작업 시각은 원고에 있는 그대로 써요. 계획과 등록은 “공개 저장소에 커밋했다”고 써요.
- “아직 추출하지 않았다, 보지 않았다”는 이 연구로 한정해요(“이 연구가 로그를 하나도 추출하기 전”). 다른 연구를 끌어오지 않아요.
- 수정 분석은 “등록 분석의 결과를 안 뒤에 정한 분석”이에요. 이렇게 말할 때는 늘 금액(달러), 토큰(다섯 개), 점수 기간(동결 직전 12개월)을 함께 적어요.
  - 12개월 점수 기간을 계획했거나 등록했다고 쓰지 않아요.
  - 수정 분석의 정의를 언제(날짜) 정했는지 쓰지 않아요.
  - 바꾼 이력을 말하는 낱말(“원래는”, “처음에는”, “줄였다”, “기간을 바꿨다”, 다른 기간의 결과)을 쓰지 않아요. 등록 분석과 계획을 설명하는 문단만 예외예요(“등록 분석은 2023년 10월 1일부터의 모든 사건으로 점수를 만들었어요”).
- 수정 분석의 결과를 “등록된 결과”라고 부르지 않아요. 수정 분석에 적용한 규칙의 판정은 “재분석”이라고 써요.
- 라벨을 본 뒤 고른 비교는 그렇다고 적어요(원고가 적은 곳마다).
- C-PR은 설계로 말해요. 원고가 적은 C-PR의 손실은 하나도 빼지 않아요.
- EOA(외부 소유 계정)는 점수를 매기지도 보고하지도 않아요. 이 점을 바꿔 쓰지 않아요.

## 6. LaTeX

- `\documentclass[11pt]{article}`, 그다음 `\input{../common/preamble}`. 머리글 제목은 `\renewcommand{\ShortTitle}{…}`.
- 인용은 원고와 같은 키로 `\cite{…}`. 참고문헌은 `\bibliographystyle{vancouver}`(A) 또는 `\bibliographystyle{IEEEtran}`(B, 양식 파일을 찾지 못하면 `unsrt`)와 `\bibliography{../../overleaf-github/manuscripts/<폴더>/references}`.
- 식은 원고와 같게 두고, 식 안의 영어 낱말만 한국어로 바꿔요.
- 참조: `표~\ref{}`, `그림~\ref{}`, `식~\eqref{}`, `\ref{}절`. 번호 뒤 조사는 읽는 소리에 맞춰요(표 1과, 표 2와, 표 3과, 표 4와, 표 5와, 표 6과). 빌드한 뒤 `check_particles.py`가 실제 번호로 검사해요.
- 용어 풀이 표는 여러 쪽에 걸치므로 `longtable`로 짜요. `longtable`은 캡션이 없어도 표 번호를 하나 쓰므로, 끝난 바로 뒤에 `\addtocounter{table}{-1}`을 넣어 표 번호를 영문 원고와 맞춰요.
- 그림은 영문 그림을 그리는 스크립트를 그대로 불러, 저장하기 직전에 글자만 한국어로 바꿔 그린 PDF를 써요(`<폴더>/figures/`). 자료와 계산과 축은 영문 그림과 같아요. 바꾸는 스크립트는 그 폴더의 `make_ko_figures.py`예요. TikZ 그림은 본문 안에 한국어로 다시 그려요.
- 그림 글꼴: matplotlib은 글꼴 목록을 따라 글자마다 대체 글꼴을 찾지만, `$…$`가 섞인 문자열의 보통 글자는 목록의 첫 글꼴로만 찍어요. 그런 문자열에 한글이 들어가면 맑은 고딕을 첫 글꼴로 두거나(B), 수식 부분을 따로 떼어 그려요(A의 패널 글자). 맑은 고딕에는 빼기 기호(U+2212)가 없어서, 목록에 Arial을 함께 둬요. 빠진 글자가 있으면 스크립트가 멈춰야 해요.
- 공통 파일(`common/`, `check_numbers.py`, `check_layout.py`, `check_particles.py`, `build.ps1`, 이 문서)은 두 해설판이 같이 써요.

## 7. 빌드와 점검

PowerShell에서(Git Bash의 xelatex는 쪽을 내보내다 멈춰요):

```powershell
cd 1-Dissertation-Works\ERC20-Allowance-PageRank-Wallet-Reputation\dissertation\manuscripts-ko
.\build.ps1 A-plos-one
python -I -X utf8 check_numbers.py A-plos-one
```

- `build.ps1`: 오류 0, 정의되지 않은 참조·인용 0, 1pt를 넘는 넘침 0, 글상자 밖 글자 0(`check_layout.py`), 참조 번호 뒤 조사 0(`check_particles.py`, 고치려면 `--fix`).
- `check_numbers.py`: 위 §4.
- 쪽 그림을 몇 장 떠서 표, 상자, 그림이 잘 놓였는지 눈으로 봐요.
