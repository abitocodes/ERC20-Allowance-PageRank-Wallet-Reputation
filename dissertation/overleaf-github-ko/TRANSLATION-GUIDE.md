# 번역 기준: 학위 논문 overleaf-github → overleaf-github-ko

## 0. 무엇을 하는가

영어 학위 논문(LaTeX)을 **한국어로 번역**한다. 읽는 사람은 **초등학생**이라고 생각하고, 아주 쉬운 말로 옮긴다.

- **번역이다. 새로 쓰거나 줄이거나 요약하지 않는다.** 원문의 문장 하나하나에 대응하는 한국어 문장이 있어야 한다. 문단, 목록 항목, 표, 그림, 수식, 각주를 하나도 빼지 않는다. 내용을 덧붙이지도 않는다(예시·비유·의견 추가 금지).
- 허용되는 것: 긴 영어 문장 하나를 짧은 한국어 문장 두세 개로 나누기, 어려운 낱말 뒤에 괄호로 짧은 풀이 붙이기(그 장에서 처음 나올 때 한 번), 한국어 어순에 맞게 문장 순서를 문단 안에서 조금 바꾸기.
- 책 『허락의 화살표』처럼 이름을 바꾸지 않는다. 논문의 이름을 그대로 쓴다(엔도스랭크, AWP, C-PR, S-PR, F1–F6, RQ1–RQ5, H1–H3, C1–C5, O1–O5).

## 1. 문체

- **해요체**로 쓴다: "~해요", "~이에요/예요", "~했어요", "~할 수 있어요". (표 머리글, 짧은 명사구 캡션, 목차 제목은 명사형으로 끝내도 된다.)
- 문장은 짧게. 한 문장에 한 가지 생각. 영어 한 문장이 길면 두세 문장으로 나눈다.
- 쉬운 말을 고른다. 한자어보다 쉬운 우리말: "활용하다"→"쓰다", "산출하다"→"계산하다/구하다", "기인하다"→"~때문이다", "상회하다"→"넘다", "도출하다"→"끌어내다", "수행하다"→"하다", "해당하다"→"~이다/~에 들다".
- 전문 용어는 §5 용어집의 말을 쓰고, **그 장에서 처음 나올 때** 괄호로 아주 짧게 풀이한다. 예: "켄달의 타우($\tau$, 두 줄 세우기가 얼마나 같은 순서인지 나타내는 수)". 두 번째부터는 풀이 없이 쓴다.
- 영어 고유명사와 약어는 그대로 둔다(GMX V2, ERC-20, BigQuery, Arbitrum One 등). 처음 나올 때만 읽는 법이나 뜻을 괄호로 붙여도 된다: "아비트럼 원(Arbitrum One)".
- 저자 이름은 라틴 글자 그대로 둔다: "Do와 Do\cend{4}는", "Do, Do, Nguyen\cend{3}이 제안한 AWP". 조사는 읽는 소리에 맞춘다(Do=도 → "Do는", Nguyen=응우옌 → "Nguyen이").
- "we"는 "이 연구에서는/우리는"으로 자연스럽게. "this thesis"는 "이 논문".
- 존댓말 일관성: 모든 본문 문장을 해요체로. "~다."로 끝나는 문장을 섞지 않는다.
- 기호·단위: "95\%"는 그대로 "95\%". "$n=5{,}521$" 그대로. "2.8\,GHz" 그대로.
- 날짜: "28~February~2026" → "2026년 2월 28일", "1~October~2026" → "2026년 10월 1일", "March to May~2026" → "2026년 3월부터 5월까지". "2025-12-01" 같은 ISO 표기는 그대로 둔다.
- 영어 따옴표 ``...'' 는 한국어 큰따옴표 “...”로 바꿔도 된다.

## 2. 반드시 그대로 두는 것(LaTeX)

- 모든 LaTeX 명령, 환경, 옵션: `\begin{...}`, `\end{...}`, `\item`, `\footnote{...}`, `\emph{...}`, `\textbf{...}`, `\fitwidth{...}`, `\input{...}`, `\includegraphics[...]{...}`, `\caption[짧은]{긴}`, tabular의 열 수와 `&`, `\\`, `\toprule` 등.
- `\label{...}`, `\ref{...}`, `\eqref{...}`, `\pageref{...}`, `\hyperref[...]`의 키, `\cend{...}`(인용 번호)의 숫자. **인용 \cend{n}은 원문과 같은 개수, 같은 번호**가 남아야 한다. 인용 위치는 그 내용을 담은 한국어 문장 끝에 둔다.
- 절 제목 명령 `\dissertationSubheading[sec:...]{제목}`, `\dissertationSubsubheading[sub:...]{제목}`, `\chapter{제목}`, `\section{...}`: **[...] 안의 레이블은 그대로**, {...} 안의 제목만 번역한다.
- 수식(`$...$`, `\[...\]`, `equation`, `align` 환경)은 **그대로**. 수식 안의 영어 낱말만 번역한다: `\text{if } o_i>0` → `\text{만약 } o_i>0 \text{이면}` 처럼. 변수 이름, 첨자(`\mathrm{ER}`, `\text{approve}` 같은 그래프 이름 첨자)는 그대로 둔다.
- `\texttt{...}` 안(코드 이름, 파일 경로, 이벤트 이름, 설정 키), `\url{...}`, `\href{...}{...}`의 주소, verbatim 블록(SQL)은 **그대로**. SQL 안의 내용도 번역하지 않는다.
- 숫자: 원문에 있는 **모든 숫자(소수, 콤마, 부호, 구간 [a, b], 날짜 숫자, 백분율)** 가 번역문에도 그대로 있어야 한다. 반올림하거나 바꾸지 않는다. 영어로 쓴 수("five", "three", "one-ninth")는 "다섯", "세", "9분의 1"처럼 옮겨도 되고 숫자로 써도 된다.
- 각 파일의 첫 줄 `% !TEX root = ../main.tex` 같은 주석은 그대로 두고, 다른 % 주석은 번역하지 않아도 된다(그대로 둠).
- 원문의 줄 구성(문단 = 한 줄, 문단 사이 빈 줄)을 따른다. 문단 수를 바꾸지 않는다.

## 3. 상호 참조 표현

| 원문 | 번역 |
|---|---|
| `Table~\ref{x}` | `표~\ref{x}` |
| `Tables~\ref{a} and~\ref{b}` | `표~\ref{a}와~\ref{b}` (받침에 따라 과/와는 숫자 읽기 기준. 표 번호는 "4.3"처럼 나오므로 "와"를 기본으로 써도 된다) |
| `Tables~\ref{a}--\ref{b}` | `표~\ref{a}--\ref{b}` |
| `Figure~\ref{x}` | `그림~\ref{x}` |
| `Section~\ref{x}` | `\ref{x}절` |
| `Sections~\ref{a} and~\ref{b}` | `\ref{a}절과 \ref{b}절` |
| `Chapter~\ref{x}` | `\ref{x}장` |
| `Appendix~\ref{x}` | `부록~\ref{x}` |
| `Equation~\eqref{x}` | `식~\eqref{x}` |
| `Algorithm~\ref{x}` | `알고리즘~\ref{x}` |
| `(Section~\ref{x})` | `(\ref{x}절)` |

## 4. 캡션과 표

- `\caption[짧은 캡션]{긴 캡션}`: 둘 다 번역한다. 캡션은 해요체 문장이나 명사구 모두 괜찮다. 다만 한 캡션 안에서는 하나로 맞춘다.
- 표의 머리글과 행 이름을 번역한다. 방법 이름(EndorseRank, AWP, C-PR ($\lambda=0.5$), S-PR, ER)은 표 안에서는 **영어 그대로** 둔다(폭 때문). 본문에서는 "엔도스랭크"라고 쓴다.
- 표 안의 숫자, 구간, `---`, `$\times$`는 그대로.

## 5. 용어집 (반드시 이 말을 쓴다)

| 영어 | 한국어 (처음 나올 때 풀이 예) |
|---|---|
| thesis, dissertation | 이 논문 |
| chapter / section / appendix | 장 / 절 / 부록 |
| research question (RQ) | 연구 질문(RQ) |
| hypothesis (H) | 가설(H) |
| objective (O) | 목표(O) |
| claim (C) | 주장(C) |
| contribution | 기여(이 연구가 새로 보탠 것) |
| limitation | 한계 |
| threat to validity | 타당성을 위협하는 것 |
| construct | 구성개념(점수가 재려고 하는 생각) |
| construct validity | 구성 타당도(점수가 재려는 것을 정말 재는지) |
| external validation / validity | 외부 검증 / 외적 타당도(바깥 자료로도 맞는지) |
| intended-construct check | 의도한 구성개념 점검 |
| check | 점검 |
| proxy | 대리 지표(대신 재는 값) |
| (proxy) family | 지표 가족(비슷한 지표 묶음) |
| label (holdout) | 라벨(나중에 채점에 쓰는 정답 값) |
| baseline | 기준선(비교 기준) |
| benchmark | 벤치마크(속도 재기) |
| runtime, wall-clock time | 실행 시간, 실제 걸린 시간 |
| iteration | 반복(한 바퀴) |
| convergence | 수렴(값이 더는 거의 바뀌지 않게 됨) |
| tolerance | 허용 오차 |
| damping factor $d$ | 감쇠 계수 $d$(화살표를 따라갈 확률) |
| teleportation, restart | 순간 이동, 다시 출발(재시작) |
| restart distribution | 재시작 분포(어디서 다시 출발하는지의 비율) |
| uniform restarts | 고르게 다시 출발하기(균등 재시작) |
| dangling node | 매달린 점(나가는 화살표가 없는 점) |
| stationary distribution/vector | 정상 분포/벡터(오래 걸었을 때 각 점에 머무는 비율) |
| random walk / random surfer | 무작위 걷기 / 무작위로 돌아다니는 사람 |
| power iteration | 거듭제곱 반복(같은 계산을 되풀이하기) |
| graph | 그래프(점과 화살표로 이은 그림) |
| node, vertex | 점(노드) |
| edge | 화살표(엣지) |
| weight / weighted | 무게(가중치) / 무게를 단 |
| directed | 방향이 있는 |
| in-degree / out-degree | 들어오는 화살표 수(입차수) / 나가는 화살표 수 |
| raw degree | 원시 차수(화살표를 그냥 센 수) |
| in-approve degree | 받은 허락 수(허락 입차수) |
| transfer in-degree | 송금 입차수(송금을 보내온 서로 다른 주소 수) |
| in-value | 받은 양의 합 |
| out-strength | 나가는 무게의 합 |
| transition matrix | 이동 행렬(전이 행렬) |
| sparse / sparsity | 듬성듬성한 / 희소성(화살표가 적음) |
| smooth (PageRank smooths the degree) | 매끄럽게 다듬다(평활하다) |
| propagate / propagation | 퍼뜨리다 / 퍼뜨림(전파) |
| PageRank | 페이지랭크(PageRank) |
| EndorseRank | 엔도스랭크(EndorseRank) — 표 안에서는 EndorseRank 또는 ER |
| AWP, Adaptive Weighted PageRank | AWP(적응형 가중 페이지랭크) |
| C-PR, coupled PageRank | C-PR(결합 페이지랭크, 두 그래프를 함께 걷는 점수) |
| coupled operator | 결합 연산자 |
| S-PR, endorsement-seeded PageRank | S-PR(보증 씨앗 페이지랭크) |
| layer / layer walked alone | 층 / 한 층만 걷는 것 |
| mixing weight $\lambda$ | 섞는 비율 $\lambda$ |
| hybrid | 혼합 점수 |
| endorsement / endorse | 보증(믿고 맡김) / 보증하다 |
| endorsement graph | 보증 그래프 |
| allowance | 허락(allowance, 토큰을 얼마까지 대신 써도 된다는 허락) |
| approve / approval | 허락하기(approve) / 허락 |
| permit (EIP-2612) | 서명 허락(permit) |
| revoke / revocation | 허락 거두기 / 허락 취소 |
| unlimited approval | 무제한 허락 |
| latest allowance | 마지막 허락(가장 최근 허락) |
| owner | 주인(토큰 주인) |
| spender | 스펜더(spender, 허락을 받아 대신 쓰는 쪽) |
| transfer | 송금(transfer) |
| sender / receiver, recipient | 보낸 쪽(송신자) / 받는 쪽(수신자) |
| new approval pairs | 새 허락 쌍(새로 생긴 주인–스펜더 허락) |
| new transfer senders | 새 송금자(새로 송금을 보내온 주소) |
| wallet / address / account | 지갑 / 주소 / 계정 |
| EOA (externally owned account) | 외부 소유 계정(EOA, 개인 키로 움직이는 계정) |
| contract, smart contract | 계약, 스마트 계약(블록체인 위에서 저절로 실행되는 프로그램) |
| token, ERC-20 | 토큰, ERC-20(토큰 공통 규칙) |
| blockchain / ledger | 블록체인 / 장부 |
| on-chain / off-chain | 온체인(블록체인 위의) / 오프체인(블록체인 밖의) |
| log, event | 로그, 이벤트(계약이 남기는 기록) |
| DeFi | 디파이(DeFi, 탈중앙 금융) |
| collateral / over-collateralized | 담보 / 과담보(빌리는 돈보다 담보를 더 맡기는) |
| liquidation | 청산(손실이 너무 커져 거래가 강제로 끝나는 일) |
| liquidation-free close rate | 청산 없이 닫은 비율 |
| lending, borrower | 빌려주기(대출), 빌리는 사람 |
| credit score / credit risk | 신용 점수 / 신용 위험 |
| reputation | 평판 |
| pseudonymity / pseudonymous | 가명성(진짜 이름 대신 주소로만 활동함) / 가명의 |
| Sybil attack | 시빌 공격(가짜 주소를 많이 만들어 속이는 공격) |
| farm (Sybil farm) | 농장(공격자가 만든 가짜 주소 무리) |
| wash trading | 자전 거래(자기끼리 사고팔아 거래가 많은 척하기) |
| airdrop farming | 에어드롭 파밍(공짜 토큰을 노린 가짜 활동) |
| extractable value (MEV) | 추출 가능한 가치(거래 순서를 이용해 빼내는 이익) |
| gas | 가스(거래 수수료) |
| Layer-2 (L2), rollup | 레이어 2(L2), 롤업 |
| Arbitrum One | 아비트럼 원(Arbitrum One) |
| GMX V2, perpetual swap | GMX V2, 무기한 선물 거래 |
| close (a position) | (포지션) 닫기 |
| trader | 트레이더(거래하는 사람) |
| matched cohort | 매칭 코호트(모든 점수가 똑같이 점수를 매기는 지갑 묶음) |
| cohort | 코호트(묶음) |
| spender cohort | 스펜더 코호트 |
| trader cohort | 트레이더 코호트 |
| expanded wallet pool | 확장 지갑 풀(더 큰 주소 모음) |
| temporal holdout | 시간 홀드아웃(나중 기간을 떼어 두고 맞혀 보는 시험) |
| freeze (date), $t_1$ | 동결일(점수를 고정하는 날) |
| label window | 라벨 기간 |
| registered replication | 등록 재현(계획을 먼저 공개해 두고 새 자료로 다시 해 보기) |
| registration / pre-registered | 등록 / 미리 등록한 |
| rule fixed in advance | 미리 정한 규칙 |
| exploratory | 탐색적(미리 정하지 않고 살펴본) |
| post hoc / after the labels were known | 사후 / 라벨을 본 뒤 |
| sensitivity analysis | 민감도 분석(조건을 바꿔 결과가 얼마나 움직이는지 보기) |
| robustness check | 강건성 점검(조건을 바꿔도 결과가 버티는지 보기) |
| Kendall's $\tau$ | 켄달의 타우($\tau$) |
| Spearman's $\rho$ | 스피어먼의 로($\rho$) |
| tie / tie block | 동점 / 동점 덩어리 |
| concordant / discordant pair | 순서가 맞는 쌍 / 어긋나는 쌍 |
| bootstrap / paired bootstrap / resample | 부트스트랩(다시 뽑기) / 짝지은 부트스트랩 / 다시 뽑은 표본 |
| confidence interval (CI) | 신뢰구간(믿을 만한 범위) |
| percentile interval | 백분위 구간 |
| paired difference / contrast | 짝지은 차이 / 대비 |
| non-inferiority / margin | 비열등성(정한 폭보다 더 나쁘지 않음) / 허용 폭 |
| coefficient | 계수 |
| mean / median / interquartile range | 평균 / 중앙값 / 사분위 범위 |
| standard deviation (SD) | 표준편차(SD) |
| speedup | 속도 향상(몇 배 빠른지) |
| ceiling (attainable maximum) | 천장(얻을 수 있는 가장 큰 값) |
| isolated node | 외톨이 점(화살표가 하나도 없는 점) |
| common value | 공통 값 |
| logistic decay $\sigma(\Delta t)$ | 로지스틱 감쇠(오래된 일일수록 가볍게 세는 무게) |
| bounded value transform $V(z)$ | 상한이 있는 값 변환(금액이 아무리 커도 1을 넘지 않게 바꾸는 식) |
| activeness | 활발함(활동 정도) |
| raw base units | 원래 단위(소수점 조정을 하지 않은 가장 작은 단위) |
| decimals | 소수 자릿수 |
| BigQuery / query / dry run | 빅쿼리(BigQuery) / 질의 / 미리 돌려 보기 |
| pipeline | 처리 과정(파이프라인) |
| configuration file | 설정 파일 |
| repository / commit | 저장소 / 커밋 |
| reproducibility | 재현성(다른 사람이 똑같이 다시 해 볼 수 있음) |
| ethics clearance | 윤리 승인 |
| GF-PR | GF-PR |
| Human Passport, Gitcoin Passport | 휴먼 패스포트(Human Passport), 깃코인 패스포트(Gitcoin Passport) |
| attestation / credential / stamp | 증명 / 자격 증명 / 스탬프 |
| proof of personhood | 사람 증명 |
| validation | 검증 |
| prediction / predict | 예측 / 예측하다(미리 맞히다) |
| scalability / scaling | 규모 키우기 / 규모에 따른 변화 |
| significance (statistical) | (이 논문은 p값을 쓰지 않음) 구간이 0을 벗어난다 |
| alignment (점수와 대리 지표) / aligns with | 일치도 / ~와 잘 맞다 |
| domain alignment | 분야 일치도 |
| agreement (두 점수 사이) | 일치 |
| Sybil-adjusted stability / Sybil stability | 시빌 보정 안정성 / 시빌 안정성 (원문이 쓴 쪽을 따름) |
| inverse risk | 위험 반대 (지표 / 가족), 처음 나올 때 (값이 클수록 손실이 적은 지표) |
| solver | 풀이 프로그램(solver) |
| ablation, seeded ablation | 빼 보기 실험, 씨앗을 쓰는 빼 보기 실험 |
| rank divergence | 순위 갈라짐 |
| glossary | 용어 풀이 |
| et al. | 등 (예: Lin 등\cend{12}은) |
| walk / coupled walk | 걷기 / 결합 걷기 |
| seed set (S-PR) / random seed | 씨앗 집합, 씨앗 지갑 / 시드 |
| spring holdout / same-window / out-of-window | 봄 홀드아웃 / 같은 기간 / 기간 밖 |
| protocol (DeFi) | 서비스(프로토콜) |
| point estimate | 점 추정값 |
| superiority / non-inferiority / verdict | 우월성 / 비열등성 / 판정 |

## 6. 예시

원문:
> Decentralized Finance (DeFi) has transformed how capital is allocated on public blockchains: lending, borrowing, and leveraged trading can now run without traditional intermediaries \cend{1}. Most credit-like transactions are still heavily collateralized, though, because protocols cannot draw on off-chain identity frameworks or existing credit data \cend{2}. Under pseudonymity, the central issue is how to allocate capital efficiently among unknown parties.

번역:
> 디파이(DeFi, 탈중앙 금융)는 누구나 볼 수 있는 블록체인 위에서 돈이 오가는 방식을 크게 바꾸었어요. 이제는 은행 같은 중간 기관 없이도 돈을 빌려주고, 빌리고, 빌린 돈을 보태 거래할 수 있어요\cend{1}. 그런데 신용 거래 비슷한 일은 아직도 대부분 담보를 많이 맡겨야만 할 수 있어요. 디파이 프로그램은 블록체인 밖의 신분 확인 제도나 이미 쌓인 신용 기록을 쓸 수 없기 때문이에요\cend{2}. 진짜 이름 대신 주소로만 활동하는 세상(가명성)에서는, 서로 모르는 사람들 사이에 돈을 어떻게 잘 맡길지가 가장 큰 문제예요.

원문:
> Out of window no PageRank ranks a label as well as the raw degree of the same edge type.

번역:
> 점수를 매긴 기간 밖에서는, 어떤 페이지랭크도 같은 종류 화살표의 원시 차수(화살표를 그냥 센 수)만큼 라벨을 잘 줄 세우지 못했어요.

원문 (캡션):
> \caption[Paired bootstrap tests of differences between Kendall $\tau$ coefficients.]{Paired bootstrap tests of differences ... (400 paired resamples, seed 42).}

번역:
> \caption[켄달의 $\tau$ 계수 사이 차이를 짝지은 부트스트랩으로 검사한 결과.]{켄달의 $\tau$ 계수 사이 차이를 짝지은 부트스트랩으로 검사한 결과예요 ... (짝지은 다시 뽑기 400번, 시드 42).}

## 7. 검사

번역한 파일마다 아래를 실행해 문제가 0개가 될 때까지 고친다.

```
python3 scripts/check_ko.py ../overleaf-github/<파일> <파일>
```

검사하는 것: 레이블·참조·인용·입력 파일·그림 파일, 환경 개수, \item 개수, 수식(글자 그대로), \texttt 내용, 숫자, 문단 수, 남은 영어 문장. "영어 문장이 남음"이 나오면 번역을 빠뜨린 것이다.

전체를 빌드한 뒤에는 \ref·\eqref 뒤의 조사(은/는, 이/가, 을/를, 과/와, (으)로)를 실제 번호의 읽는 소리에 맞춘다(표 4.3은, 표 4.2는, 표 4.10과).

```
python3 scripts/check_particles.py          # 맞지 않는 조사를 보여 줌
python3 scripts/check_particles.py --fix    # 고쳐 씀
```

## 8. 본보기

초록 번역 `01-Intro/02-Abstract.tex`를 말투와 용어의 본보기로 삼는다(원문: `../overleaf-github/01-Intro/02-Abstract.tex`).
