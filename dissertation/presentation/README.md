# 학위 논문 발표 자료 (HTML 슬라이드)

**ERC-20 허락 화살표를 페이지랭크에 넣어 온체인 지갑 평판 점수를 더 좋게 만들기**
*Integrating ERC-20 Allowance Edges into PageRank for Enhanced On-Chain Wallet Reputation Scoring*

권태홍 (Taehong Kwon) · 지도교수 Prof. Ernest Mnkandla · 공동 지도교수 Prof. Donatien Koulla Moulla, Dr. David Sena Attipoe · University of South Africa · 2026년 10월

- 11개 섹션, 슬라이드 59장, 클릭 단계까지 합치면 화면 304개예요. 장마다 정해 둔 시간(노트 판에 보여요)을 더하면 약 44분이에요.
- 이 연구가 점수를 매긴 대상은 **스마트 계약**이에요. EOA는 화살표의 끝점으로만 나와요(`s02-04`).
- 모든 수식은 그림 → 작은 예 → 기호 → 식 순서로, 중학생도 따라올 수 있게 한 단계씩 끌어내요.
- 줄거리와 슬라이드마다의 화면 글, 움직임, 숫자 출처는 `STORYBOARD.md`에 있어요.
- 영문판(`index.en.html`)이 따로 있고, 두 판 모두 HTML 한 파일로 묶은 것이 `dist/`에 있어요(1절).
- 한국어판의 인쇄판 PDF(클릭 단계마다 한 쪽, 304쪽, 쪽마다 그 단계의 발표 노트)도 `dist/`에 있어요(1절).

---

## 1. 여는 법

### 두 번 눌러 열기 (인터넷 없이)

`index.html`을 크롬이나 엣지에서 두 번 눌러 열면 돼요(`file://`). 라이브러리, 글꼴, 데이터가 모두 이 폴더 안에 있어서 인터넷이 없어도 돌아가요.

### http로 열기

```bash
cd dissertation/presentation
python3 -m http.server 8000
# 브라우저에서 http://localhost:8000/
```

- 화면 비율은 16:9(설계 크기 1920×1080)예요. 창 크기에 맞춰 늘거나 줄어요. 1280×720과 1920×1080에서 확인했어요.
- 3D 장면(WebGL)이 있으니 하드웨어 가속을 켠 크롬·엣지를 권해요. 확인은 크로미움에서만 했어요(파이어폭스·사파리는 확인하지 않았어요).
- 운영체제에서 '동작 줄이기'를 켜 두면 움직임이 줄어든 판으로 보여요. 발표 중에는 `M` 키로 바꿀 수 있어요.

### 한 파일로 열기 (한국어판, 영문판)

| 파일 | 판 |
|---|---|
| `dist/presentation-ko.html` | 한국어판(`index.html`을 묶은 것) |
| `dist/presentation-en.html` | 영문판(`index.en.html`을 묶은 것) |

라이브러리, 글꼴, 데이터, 섹션을 모두 안에 넣은 HTML 한 파일이에요(각각 약 7MB). 이 파일 하나만 복사하거나 보내도 두 번 눌러 열면 돼요. 키, 주소로 바로 가기, 발표자 창(`P`)도 폴더 판과 똑같이 돌아요.

- 영문판의 원본은 `index.en.html`이에요. 엔진, 데이터, 라이브러리는 한국어판과 같고, 화면 글과 발표 노트만 `js/sections-en/`에 따로 있어요. 엔진이 직접 쓰는 말(도움말, 노트 판, 알림, 상태 표시)은 `<html lang>`을 보고 바꿔요(`Deck.lang`, `Deck.t`).
- 원본을 고친 뒤에는 다시 묶어요. 파이썬 표준 라이브러리만 쓰고, 원본이 같으면 바이트까지 같은 파일이 나와요.

```bash
python3 tools/build_single.py              # 두 파일 다
python3 tools/build_single.py --lang en    # 영문판만 (ko | en | all)
```

- 슬라이드 내용을 고칠 때는 `js/sections/`(한국어)와 `js/sections-en/`(영문)의 같은 파일을 함께 고치고 다시 묶어요.

### 인쇄판 (한국어)

`dist/presentation-ko-print.pdf`는 한국어판을 클릭 단계마다 한 쪽씩 담은 PDF예요(59장, 304쪽, 약 40MB).

- 쪽은 가로 A4 비율(297 × 210mm)이에요. 위에 그 단계까지 진행된 슬라이드(16:9, 쪽 너비 가득), 아래에 그 단계의 발표 노트 한 문단(N 노트 판에서 ▶로 표시되는 문단)과 장 번호, 단계, 장 제목, 다음 안내가 있어요.
- A4 세로 한 장에 두 쪽씩('한 면에 2쪽') 인쇄하면 위아래가 꽉 차요. 한 쪽씩 인쇄하면 A4 가로에 맞아요.
- 화면은 '움직임 줄이기' 상태에서 각 단계가 끝난 모습을 찍어 인쇄용 밝은 색으로 바꾼 것이에요. 어두운 배경은 흰색, 밝은 글자는 짙은 회색이 되고, 허락(주황)·송금(하늘)·C-PR(보라)·차수(초록)·강조(분홍) 색은 색상을 지킨 채 흰 바탕에 맞게 조금 짙어져요. 범례도 같은 규칙으로 바뀌므로 색의 뜻은 그대로예요.
- 노트는 쪽마다 실제 글자로 들어가서 PDF에서 검색할 수 있어요.

다시 만들기(약 4분, 크로미움을 써요. 5절과 같은 준비가 필요해요):

```bash
cd tools
node build_print.mjs                         # → ../dist/presentation-ko-print.pdf
node build_print.mjs --dark                  # 화면 색(어두운 배경) 그대로
node build_print.mjs --only s04-pagerank     # 일부 장만(시험용, --out 다른파일.pdf와 함께)
node build_print.mjs --keep DIR              # 쪽 그림과 print.html을 DIR에 남김 → --from DIR로 배치만 다시
```

### 주소로 바로 가기

| 주소 끝 | 뜻 |
|---|---|
| `#s04-03` | 슬라이드 id로 가기 |
| `#s04-03/2` | 그 슬라이드의 2번째 클릭 단계 |
| `#s04-pagerank` | 섹션의 첫 장 |
| `#15` 또는 `#15/2` | 15번째 장(1부터 셈) |
| `#presenter` | 발표자 창 |

---

## 2. 발표할 때 쓰는 키

| 키 | 하는 일 |
|---|---|
| `→` `Space` `PageDown` 마우스 클릭 | 다음 단계, 단계가 끝나면 다음 장 |
| `←` `PageUp` `Backspace` | 한 단계 뒤로 |
| `↓` / `↑` | 다음 장 / 앞 장으로 바로 |
| `Home` / `End` | 첫 장 / 마지막 장 |
| 숫자 + `Enter` | 그 번호의 장으로 가기(오른쪽 위에 `n / 59`가 보여요) |
| `N` | 이 창에 발표 노트 열고 닫기(연습용) |
| `P` | 발표자 창 열기: 노트, 다음 장 미리 보기, 시계. 발표 창을 원격으로 움직여요(`file://`에서도 돼요) |
| `O` | 전체 장 한눈에 보기(카드를 누르거나 `Enter`로 이동) |
| `M` | 움직임 줄이기 켜고 끄기 |
| `F` | 전체 화면 |
| `?` 또는 `H` | 도움말 |
| `Esc` | 열린 판 닫기 |

- 3D 장면 가운데 `s03-06`, `s06-04`, `s10-03`은 마우스로 끌어서 돌리고, 휠로 당기거나 밀 수 있어요(`s08-02`는 카메라가 정해진 길로만 움직여요).
- 움직임이 도는 중에 다음 키를 누르면 그 움직임을 먼저 끝내고 넘어가요.
- 발표 노트는 모두 해요체 대본이에요. 장마다, 클릭 단계마다 한 문단씩 있어요.

### 결과 숫자 옆의 상태 표시

결과 숫자에는 오른쪽 아래에 상태 표시가 붙어요.

| 표시 | 영문판 표시 | 뜻 |
|---|---|---|
| 미리 정함(계획) | Fixed in advance (plan) | 분석 계획(커밋 43d8045)이 이 연구의 추출 전에 정한 비교: 규칙 A |
| 등록함(W1) | Registered (W1) | W1 등록(0d3a057)이 이 연구의 W1 추출 전에 정한 비교: 규칙 B 등 |
| 재분석 | Re-analysis | 그 규칙을 수정 점수에 다시 적용한 판정이에요. 등록 시험이 아니에요 |
| 사후(라벨 본 뒤) | Post hoc (after the labels) | 라벨을 본 뒤에 계산한 비교 |
| 탐색적 | Exploratory | 규칙 없이 살펴본 실행 |
| 의도한 구성개념 점검 | Intended-construct check | 같은 기간 점검. '검증'이 아니에요 |
| 등록 분석 | Registered analysis | 처음 등록한 분석(등록 digest)의 값. 회색으로 보여요 |
| 예시 / 논문 2장 예시 / 계산 | Example / Example from Chapter 2 / Calculated | 설명용 예, 원고 2장의 예, 공식에서 계산한 값 |

---

## 3. 섹션과 장 수

| # | 섹션 id | 제목 | 장 수 | 장 번호 | 주요 내용 |
|---|---|---|---|---|---|
| 01 | `s01-opening` | 여는 질문 | 3 | 1–3 | 제목, 연구 질문 RQ1–RQ5, 오늘의 길 |
| 02 | `s02-world` | 허락과 송금 | 5 | 4–8 | 송금과 허락의 차이, 무제한 허락, 점수 받는 쪽은 계약, 아비트럼 원 |
| 03 | `s03-data` | 데이터의 세계 | 6 | 9–14 | 3년 달력, 기록 수, 다섯 토큰과 달러 가격, 코호트 깔때기, 두 그래프 크기, 15,107개 계약 3D |
| 04 | `s04-pagerank` | 페이지랭크 유도 | 7 | 15–21 | 무작위 걷기 → 균형식 → 이동 행렬 → 새는 물과 함정 → 감쇠 계수 d → 거듭제곱 반복 |
| 05 | `s05-weights` | 화살표의 무게 | 6 | 22–27 | 시간 무게 σ(Δt), 금액 무게 V(z), b = ln 3 / m, 다시 출발, 달러 상한 U |
| 06 | `s06-methods` | 네 가지 점수 | 5 | 28–32 | 엔도스랭크, AWP와 원시 차수, C-PR(λ, 3D), S-PR |
| 07 | `s07-measure` | 맞았는지 재는 법 | 5 | 33–37 | 점검과 시험, 켄달의 타우, τ_b와 스피어먼 ρ, 부트스트랩, 짝지어 빼기와 허용 폭 |
| 08 | `s08-results` | 결과 | 8 | 38–45 | 같은 기간 점검, 두 점수의 순서(3D), 시간 홀드아웃, 송금 쪽·허락 쪽 결과, 사후 가설, 닫힌 식 |
| 09 | `s09-rules` | 미리 정한 규칙 | 5 | 46–50 | 언제 무엇을 정했나, 규칙 A, 규칙 B, 등록 분석과 수정 분석, R1–R3 |
| 10 | `s10-sybil-speed` | 공격 비용과 속도 | 4 | 51–54 | 가짜 주소 농장, 별 모양 농장, 꼭대기까지의 비용(3D), 속도는 화살표 수 \|E\|에서 |
| 11 | `s11-closing` | 정리 | 5 | 55–59 | 연구 질문의 답, 보탠 것, 한계, 지갑 프로그램에 주는 뜻과 다음 일, 감사 |
| | | **합계** | **59** | | |

3D 장면(three.js)이 있는 장: `s03-06`, `s06-04`, `s08-02`, `s10-03`. 수식(KaTeX)이 있는 장: `s03-03`, 04·05 섹션 전부, `s06-01`–`s06-05`, `s07-02`·`s07-03`·`s07-05`, `s08-01`·`s08-06`·`s08-07`, `s09-02`·`s09-03`·`s09-05`, 10 섹션 전부, `s11-02`.

---

## 4. 숫자는 어디서 오나

화면의 모든 숫자는 `data/*.js`에서 와요. 이 파일들은 `tools/build_data.py`가 `phd_works` 저장소의 실험 결과에서 읽어 만들어요. 손으로 고치지 않아요.

| 출처 (`phd_works/1-Dissertation-Works/ERC20-Allowance-PageRank-Wallet-Reputation/` 아래) | 뜻 |
|---|---|
| `experiments/data/3-published-results-for-thesis/revised-usd/results_digest.md`와 그 폴더의 JSON | **수정 분석** — 논문의 주 분석 |
| `experiments/data/3-published-results-for-thesis/results_digest.md`와 그 폴더의 JSON | **등록 분석** — 화면에서 늘 '등록 분석'이라고 밝혀요 |
| `experiments/data/2-processed-tables-and-evaluations/revised-usd/…/*.parquet` | 계약별 점수(같은 기간 코호트, 홀드아웃 W0, 기간 W1의 스펜더·트레이더) |
| `experiments/data/0-usd-token-list-and-prices/` | 다섯 토큰, 하루 달러 가격, 상수 m_T·m_A |
| `experiments/config/contract_reputation.yaml`, `experiments/data/bq_ledger.json` | 설정값, 빅쿼리 비용 장부 |
| `git -C phd_works show <커밋>` | 43d8045, 0d3a057, a897475, 09dfc32, 2705b28의 커밋 시각 |

| 데이터 파일 | 담긴 것 |
|---|---|
| `data/meta.js` | 제목, 저자, 범위(계약만 점수), 모든 출처 파일의 SHA-256 |
| `data/params.js` | d, λ, 시간·금액 무게 상수, 상한 U 등 |
| `data/scale.js` | 기록 수, 그래프 크기 \|V\|·\|E\|, 코호트 깔때기 |
| `data/timeline.js` | 관측 기간, 동결일, 커밋 시각 |
| `data/prices.js` | 다섯 토큰의 하루 달러 가격 |
| `data/contracts.js` | 15,107개 계약의 점수 백분위(3D 장면용) |
| `data/results.js` | 켄달의 타우, 부트스트랩 구간, Δτ, 규칙 판정 |
| `data/holdout.js` | 홀드아웃 라벨을 10구간으로 나눈 기술 통계 |
| `data/traders.js` | GMX 트레이더 점수와 라벨 |
| `data/sybil.js` | 가짜 주소 농장 비용 곡선 |
| `data/benchmark.js` | 계산 시간과 메모리 |

- 숫자는 다시 맞추거나 다시 추정하지 않아요. parquet에서 끌어낸 몇 값(백분위, 10구간, 농장 비용 곡선, 8개 계약 예)은 `derived: true`와 설명이 붙어 있어요.
- 수정 분석 결과를 '등록 결과'라고 부르지 않아요. 사후·탐색적 결과는 그렇다고 표시해요. 원시 차수가 이기는 곳은 그대로 말해요. 속도 차이는 화살표 수 |E|에서 온다고 말해요.

### 데이터 다시 만들기

```bash
# 필요한 것: Python 3.9 이상, numpy, pandas, pyarrow, pyyaml, scipy(검사용)
python3 tools/build_data.py                 # phd_works 위치는 이 파일 위치에서 찾아요
python3 tools/build_data.py /path/to/phd_works --out data
python3 tools/build_data.py --no-verify     # 검사 건너뛰기
```

다 쓰고 나면 파일을 다시 읽어 두 digest와 parquet에서 다시 센 켄달 계수와 35개 값을 견줘 보고, 하나라도 틀리면 종료 코드 1로 끝나요. 2026년 10월 12일에 다시 만들어 보니 35/35가 맞았고, `meta.js`의 생성 시각 말고는 지금 파일과 바이트까지 같았어요.

---

## 5. 스크린샷 다시 찍기

`tools/shoot.mjs`가 모든 장과 클릭 단계를 돌며 PNG를 찍고, 콘솔 오류와 `window.__deckErrors`를 보고해요. 미리 깔린 크로미움(`/opt/pw-browsers/chromium-*/chrome-linux/chrome`, 또는 환경 변수 `CHROME_PATH`)을 써요. `playwright install`은 하지 않아요.

```bash
cd tools
npm install                                  # playwright-core만 깔아요
node shoot.mjs                               # file://, 1920×1080, 전체(약 15분) → tools/shots/<장>-<단계>.png
node shoot.mjs --only s04-pagerank           # 섹션, 장 id, id 앞부분(쉼표로 여러 개)
node shoot.mjs --size 1280x720               # → tools/shots/1280x720/
node shoot.mjs --http                        # http://127.0.0.1로 열어서 찍기
node shoot.mjs --reduced                     # 동작 줄이기 판 → tools/shots/reduced/
node shoot.mjs --first                       # 장마다 첫 화면만
node shoot.mjs --memcheck 3                  # 끝나고 앞뒤로 3번 돌며 메모리 보고
node shoot.mjs --page index.en.html          # 영문판 → tools/shots/index.en/
node shoot.mjs --page dist/presentation-en.html   # 한 파일 판 → tools/shots/presentation-en/
```

오류가 하나라도 있으면 종료 코드 1이에요. `tools/node_modules/`와 `tools/shots/`는 `.gitignore`에 들어 있어요.

`tools/gallery.html`은 엔진 기능(공유 요소 이동, 글자 움직임, 3D 도우미 등)을 한 장씩 보여 주는 개발용 페이지예요. 발표에는 쓰지 않아요.

---

## 6. 폴더 구조

```
index.html            덱 한 장(고전 <script>만, 모듈·fetch 없음), 한국어판
index.en.html         영문판: 같은 엔진·데이터·라이브러리, 섹션만 js/sections-en/
css/deck.css          디자인 토큰, 글꼴, 레이아웃
js/deck.js            슬라이드 엔진(키, 단계, 전환, 3D·KaTeX·숫자 세기 도우미, 발표자 창)
js/components.js      여러 섹션이 같이 쓰는 그림 부품
js/sections/s01…s11   섹션마다 한 파일: Deck.section({ id, title, slides: [...] })
js/sections-en/       영문판 섹션(같은 파일 이름, 같은 장 id와 단계)
dist/                 한 파일 판: presentation-ko.html, presentation-en.html (tools/build_single.py가 만듦),
                      인쇄판: presentation-ko-print.pdf (tools/build_print.mjs가 만듦)
data/*.js             window.DECK_DATA (tools/build_data.py가 만듦)
lib/                  가져온 라이브러리와 글꼴(아래 표), lib/LICENSES.md, lib/licenses/
tools/                build_data.py, build_single.py, build_print.mjs, shoot.mjs, gallery.html
STORYBOARD.md         줄거리판: 장마다 화면 글, 움직임, 수식, 숫자 출처, 노트
```

슬라이드를 고칠 때는 `js/deck.js` 맨 위의 설명(슬라이드 항목, 단계 규칙, `ctx` 도우미)을 먼저 보세요.

---

## 7. 라이브러리와 라이선스

모두 npm 레지스트리에서 받은 파일을 그대로 `lib/`에 넣었어요(UMD 고전 빌드). 자세한 표와 라이선스 전문은 `lib/LICENSES.md`, `lib/licenses/`에 있어요. 한 파일 판(`dist/`)은 이 표와 전문을 파일 끝의 `<script type="text/plain" id="deck-licenses">`에 함께 담아요.

| 라이브러리 | 버전 | 라이선스 | 파일 |
|---|---|---|---|
| GSAP 코어와 플러그인(Flip, MotionPath, DrawSVG, MorphSVG, SplitText, ScrambleText, CustomEase) | 3.15.0 | GSAP Standard "No Charge" License(무료, 오픈 소스는 아님) | `lib/gsap.min.js` 외 |
| three.js | r158 (npm 0.158.0) | MIT | `lib/three.min.js` |
| KaTeX | 0.16.47 | MIT | `lib/katex/` |
| D3 | 7.9.0 | ISC | `lib/d3.min.js` |
| Pretendard (가변 글꼴) | 1.3.9 | SIL Open Font License 1.1 | `lib/fonts/PretendardVariable.woff2` |
| DejaVu Sans 부분 글꼴(✕, ⇄ 두 글자) | 2.37.3 | Bitstream Vera / DejaVu 라이선스 | `lib/fonts/DeckSymbols*.woff` |

도구: `tools/node_modules/`의 playwright-core 1.56.1(Apache-2.0)은 스크린샷용이고 덱에는 들어가지 않아요.

글꼴이 없을 때는 시스템 글꼴(Apple SD Gothic Neo, 맑은 고딕, Noto Sans KR 등)로 보여요.

---

## 8. 알아 둘 점

- three.js r158은 고전 `build/three.min.js`가 있는 마지막 줄기라서, 콘솔에 '곧 없어질 빌드'라는 안내가 한 줄 나와요. 오류가 아니에요.
- 3D 장면은 WebGL이 필요해요. 화면 공유 프로그램이나 원격 데스크톱에서 하드웨어 가속이 꺼져 있으면 3D 장이 느릴 수 있어요. 이럴 때는 `M`(동작 줄이기)을 켜면 자동 회전이 멈춰요.
- 발표자 창(`P`)은 브라우저 팝업이에요. 처음에 팝업 차단을 풀어 주세요.
- 전체 스크린샷(304장)은 소프트웨어 렌더링(SwiftShader)으로 약 15분 걸려요.
