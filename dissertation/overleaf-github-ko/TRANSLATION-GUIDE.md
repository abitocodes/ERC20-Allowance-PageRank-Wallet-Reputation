# 번역 기준: 학위 논문 overleaf-github → overleaf-github-ko

## 0. 무엇을 하는가

영어 학위 논문(LaTeX, `../overleaf-github/`, 저장소 `phd-dissertation-draft-en`)을 **한국어로 번역**한다. 읽는 사람은 **초등학생**이라고 생각하고, 아주 쉬운 말로 옮긴다.

- **번역이다. 새로 쓰거나 줄이거나 요약하지 않는다.** 원문의 문장 하나하나에 대응하는 한국어 문장이 있어야 한다. 문단, 목록 항목, 표, 그림, 수식, 각주를 하나도 빼지 않는다. 내용을 덧붙이지도 않는다(예시·비유·의견 추가 금지).
- 허용되는 것: 긴 영어 문장 하나를 짧은 한국어 문장 두세 개로 나누기, 어려운 낱말 뒤에 괄호로 짧은 풀이 붙이기(그 장에서 처음 나올 때 한 번), 한국어 어순에 맞게 문장 순서를 문단 안에서 조금 바꾸기.
- 책 『허락의 화살표』처럼 이름을 바꾸지 않는다. 논문의 이름을 그대로 쓴다(엔도스랭크, AWP, C-PR, S-PR, F1, F2, F6, RQ1–RQ5, H1–H3, C1–C6, O1–O5, D1, D2, V1–V3).

## 1. 문체

- **해요체**로 쓴다: "~해요", "~이에요/예요", "~했어요", "~할 수 있어요". (표 머리글, 짧은 명사구 캡션, 목차 제목은 명사형으로 끝내도 된다.)
- 문장은 짧게. 한 문장에 한 가지 생각. 영어 한 문장이 길면 두세 문장으로 나눈다.
- 쉬운 말을 고른다. 한자어보다 쉬운 우리말: "활용하다"→"쓰다", "산출하다"→"계산하다/구하다", "기인하다"→"~때문이다", "상회하다"→"넘다", "도출하다"→"끌어내다", "수행하다"→"하다", "해당하다"→"~이다/~에 들다".
- 전문 용어는 §5 용어집의 말을 쓰고, **그 장에서 처음 나올 때** 괄호로 아주 짧게 풀이한다. 예: "켄달의 타우($\tau$, 두 줄 세우기가 얼마나 같은 순서인지 나타내는 수)". 두 번째부터는 풀이 없이 쓴다.
- 영어 고유명사와 약어는 그대로 둔다(ERC-20, ERC-4337, Safe, BigQuery, Arbitrum One 등). 처음 나올 때만 읽는 법이나 뜻을 괄호로 붙여도 된다: "아비트럼 원(Arbitrum One)".
- 저자 이름은 원문의 인용 명령이 찍어 주는 그대로 둔다(아래 §2의 `\textcite`, `\parencite`). `\textcite{key}`는 "Do, Do, and Nguyen (2023)"처럼 영어로 찍히므로, 바로 뒤에는 **받침과 상관없는 조사**(의, 에서, 에 따르면, 도, 처럼)를 쓴다: "\textcite{do2023awp}의 AWP는", "\textcite{page1999pagerank}에 따르면". 은/는, 이/가, 을/를을 붙여야 하면 "\textcite{x}의 연구는"처럼 바꾼다.
- "we"는 "이 연구에서는/우리는"으로 자연스럽게. "this thesis"는 "이 논문".
- 존댓말 일관성: 모든 본문 문장을 해요체로. "~다."로 끝나는 문장을 섞지 않는다.
- 기호·단위: "95\%"는 그대로 "95\%". "$n=5{,}521$" 그대로. "2.8\,GHz" 그대로.
- 날짜: "28~February~2026" → "2026년 2월 28일", "1~October~2026" → "2026년 10월 1일", "March to May~2026" → "2026년 3월부터 5월까지". "2025-12-01" 같은 ISO 표기는 그대로 둔다.
- 영어 따옴표 ``...'' 는 한국어 큰따옴표 “...”로 바꿔도 된다.

## 2. 반드시 그대로 두는 것(LaTeX)

- 모든 LaTeX 명령, 환경, 옵션: `\begin{...}`, `\end{...}`, `\item`, `\footnote{...}`, `\emph{...}`, `\textbf{...}`, `\fitwidth{...}`, `\input{...}`, `\includegraphics[...]{...}`, `\caption[짧은]{긴}`, tabular의 열 수와 `&`, `\\`, `\toprule` 등.
- `\label{...}`, `\ref{...}`, `\eqref{...}`, `\pageref{...}`, `\hyperref[...]`의 키.
- 인용 명령 `\textcite{key}`, `\parencite{key}`, `\parencite[p.~3]{key}`(biblatex, APA 7)는 **명령 이름과 키를 원문 그대로**, 같은 개수로 남긴다. `\textcite`를 `\parencite`로 바꾸거나 그 반대로 하지 않는다. `\parencite`는 그 내용을 담은 한국어 문장 끝(마침표 앞)에 둔다. 참고문헌 목록(7장)은 영어 그대로다.
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
| lending, borrower | 빌려주기(대출), 빌리는 사람 |
| credit score / credit risk / credit decision | 신용 점수 / 신용 위험 / 신용 결정 |
| reputation | 평판 |
| pseudonymity / pseudonymous | 가명성(진짜 이름 대신 주소로만 활동함) / 가명의 |
| Sybil attack | (2026-11-11 밤 저자 결정으로 원고에 쓰지 않음. 옛 번역: 시빌 공격) |
| link farm | 링크 농장 (닫힌 무리 점검의 근거 문장에만 나옴) |
| closed group (of contracts) | 닫힌 무리(밖으로 나가는 화살표가 없는 계약 묶음) |
| wash trading | 자전 거래(자기끼리 사고팔아 거래가 많은 척하기) |
| airdrop farming | 에어드롭 파밍(공짜 토큰을 노린 가짜 활동) |
| extractable value (MEV) | 추출 가능한 가치(거래 순서를 이용해 빼내는 이익) |
| gas | 가스(거래 수수료) |
| Layer-2 (L2), rollup | 레이어 2(L2), 롤업 |
| Arbitrum One | 아비트럼 원(Arbitrum One) |
| matched cohort | 매칭 코호트(모든 점수가 똑같이 점수를 매기는 계약 묶음) |
| cohort | 코호트(묶음) |
| spender cohort | 스펜더 코호트 |
| expanded wallet pool | 확장 지갑 풀(더 큰 주소 모음) |
| temporal holdout | 시간 홀드아웃(나중 기간을 떼어 두고 맞혀 보는 시험) |
| freeze (date), $t_1$ | 동결일(점수를 고정하는 날) |
| label window | 라벨 기간 |
| registered replication | 등록 재현(계획을 먼저 등록해 두고 새 자료로 다시 해 보기) |
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
| stability family (분석 계획의 이름은 Sybil-adjusted stability) | 안정성 가족, 처음 나올 때 (송금 상대가 얼마나 다양하고 활동이 얼마나 오래 이어졌는지 보는 지표 묶음); 표와 그림에서는 안정성. 2026-11-11 밤부터 원고에 Sybil을 쓰지 않음 |
| inverse risk | 위험 반대 (지표 / 가족), 처음 나올 때 (값이 클수록 손실이 적은 지표) |
| solver | 풀이 프로그램(solver) |
| ablation, seeded ablation | 빼 보기 실험, 씨앗을 쓰는 빼 보기 실험 |
| rank divergence | 순위 갈라짐 |
| glossary | 용어 풀이 |
| et al. | (인용 명령이 찍어 주는 영어 그대로 둠) |
| walk / coupled walk | 걷기 / 결합 걷기 |
| seed set (S-PR) / random seed | 씨앗 집합, 씨앗 지갑 / 시드 |
| spring holdout / same-window / out-of-window | 봄 홀드아웃 / 같은 기간 / 기간 밖 |
| protocol (DeFi) | 서비스(프로토콜) |
| point estimate | 점 추정값 |
| superiority / non-inferiority / verdict | 우월성 / 비열등성 / 판정 |

## 5b. 이 논문(컨트랙트 평판)에서 더 쓰는 말

이 논문은 **스마트 계약만** 점수를 매기고 평가해요. 주 분석(계약 그래프 분석)의 그래프는 점이 모두 계약이고, 사용자 계정(EOA, EIP-7702 계정, 스마트 계정)은 어떤 그래프에도 없어요. 사용자 계정은 발견 순서 검증의 중요도와 라벨에만 들어가요. 점수를 받는 대상은 "계약"이라고 옮긴다. **논문 제목**은 원문 제목 그대로 「ERC-20 허락 화살표를 페이지랭크에 넣어 온체인 지갑 평판 점수를 더 좋게 만들기」라고 옮긴다.

| 영어 | 한국어 (처음 나올 때 풀이 예) |
|---|---|
| (smart) contract | 스마트 계약 → 두 번째부터 계약 |
| spender contract | 스펜더 계약(허락을 받아 대신 쓰는 계약) |
| owner (approving side) | 주인(허락을 해 주는 쪽) |
| approval count, number of distinct owners that approve | 허락한 주인 수(서로 다른 주인 수) |
| wallet software | 지갑 프로그램 |
| registered analysis | 등록 분석(미리 등록한 그대로 한 분석) |
| revised analysis | 수정 분석(등록 분석의 결과를 안 뒤에 정한 분석) — 이 논문의 주 분석 |
| deviation (from the registration) | 등록에서 벗어난 변경 |
| re-analysis | 재분석 |
| analysis plan, the plan | 분석 계획, 계획 |
| registration, the registration | 등록, 등록 문서 |
| rule A / rule B | 규칙 A / 규칙 B |
| margin (0.01) | 허용 폭 |
| USD, dollar amount | 달러(USD), 달러 금액 |
| daily close (price) | 하루 종가(그날 마지막 가격) |
| price feed (Chainlink) | 가격 피드(블록체인에 올라오는 가격 정보) |
| value weight $V$, slope $b$ | 금액 무게 $V$, 기울기 $b$ |
| cap $U$ | 상한 $U$(이보다 큰 금액은 이 값으로 자름) |
| top five tokens | 상위 다섯 토큰 |
| ego network | 에고 네트워크(코호트 계약에 닿는 화살표만 모은 그래프) |
| observation window | 관측 기간 |
| holdout W0 / registered window W1 | 홀드아웃 W0 / 등록 기간 W1 |
| freeze, frozen | 동결, 동결한 |
| account type / bytecode | 계정 종류 / 바이트코드(계약 프로그램의 기계어) |
| EIP-7702 delegation designator | EIP-7702 위임 표시 |
| warm-up run / timed run | 준비 실행 / 시간 잰 실행 |
| solve time | 푸는 시간 |
| colluding addresses | 짜고 움직이는 주소 |
| percentile | 백분위 |
| attestation tool | 증명 도구 |
| by construction | 만든 방식 때문에 저절로 |
| intended construct | 의도한 구성개념 |
| value slope, value-slope check | 금액 기울기, 금액 기울기 점검 ("값 기울기"는 쓰지 않음) |
| raw in-approve degree | 원시 받은 허락 수 ("허락 입차수"는 첫 풀이 안에서만 씀) |
| revised scores / revised counts | 고친 점수 |
| revised cohort / revised matched cohort | 수정 코호트 / 수정 매칭 코호트 |
| the plan's cohort | 계획의 코호트 |
| registered results | 등록 분석의 결과 |
| registered verdict(s) | 등록 분석의 판정 |
| registered test(s) / registered rule(s) | 등록한 시험 / 등록한 규칙 |
| after the (registered) results were known | (등록 분석의) 결과를 안 뒤 |
| decision contrasts ($D_1$, $D_2$) | 판정 대비 |
| count-level (lead) | 그냥 센 수의 수준(에서 앞섬) |
| time decay, decay ($\sigma(\Delta t)$) | 로지스틱 감쇠 (감쇠만 따로 쓰지 않음: 감쇠 계수와 헷갈림) |
| time weight | 시간 무게 |
| damping, damping check | 감쇠 계수, 감쇠 계수 점검 (감쇠만 따로 쓰지 않음) |
| restart rule / restart mass / restart weight / restart vector | 다시 출발 규칙 / 다시 출발 몫 / 다시 출발 무게 / 재시작 벡터 |
| activity restarts | 활동 재시작(활발한 주소에서 더 자주 다시 출발하기) |
| family mean | 지표 가족 평균 (이름 붙은 가족은 허락 가족, 송금 가족처럼 줄여 씀) |
| single-layer (score, method, PageRank) | 한 층 (점수, 방법, 페이지랭크) |
| approval count / transfer count | 허락한 주인 수 / 송금 수 |
| ego tables / ego extraction | 에고 표 / 에고 추출 (등록 분석의 추출에만 씀) |
| daily token prices / daily US-dollar prices | 하루 토큰 가격 / 하루 달러 가격 |
| US dollars | 달러 ("미국 달러"는 쓰지 않음; 첫 풀이는 달러(USD)) |
| (RPC) endpoint | 접속 주소(블록체인 노드에 질문을 보내는 주소) |
| Chainlink, DefiLlama | Chainlink, DefiLlama (영어 그대로; 처음에 체인링크(Chainlink)로 써도 됨) |
| threshold (cohort) | 기준값 |
| Kendall coefficient(s) | 켄달의 타우 계수 / 켄달의 $\tau$ 계수 |

## 5c. 계약 그래프 분석과 발견 순서 검증의 말

주 분석은 계약 그래프 분석(변형 `contract12m`)이에요. 해설판(`../manuscripts-ko/`)과 발표 자료(`../presentation/`)도 이 말을 써요.

| 영어 | 한국어 (처음 나올 때 풀이 예) |
|---|---|
| main analysis / contract-graph analysis | 주 분석 / 계약 그래프 분석 |
| contract graph | 계약 그래프(점이 모두 계약인 그래프) |
| whole chain (edges read from) | 체인 전체(에서 읽은 화살표) |
| user account(s) | 사용자 계정(EOA, EIP-7702 계정, 스마트 계정을 함께 이르는 말) |
| smart account (Safe, ERC-4337 account) | 스마트 계정(계약 코드로 된 사용자 계정: Safe, ERC-4337 계정) |
| transaction, transaction sender | 트랜잭션(블록체인에 보내는 거래 요청), 트랜잭션을 보낸 주소 |
| code family / selector / EntryPoint / paymaster | 코드 계열 / 셀렉터(함수 식별 값) / EntryPoint / paymaster |
| system address (precompile) | 시스템 주소(프리컴파일) |
| typing window, account typing | 종류 판별 기간, 계정 종류 판별 |
| owner contract / spender contract | 주인 계약 / 스펜더 계약 |
| balance, balance reconstruction | 잔액, 잔액 재구성(송금 로그로 잔액을 다시 계산하기) |
| balance cap | 잔액 상한(허락을 동결 시점 주인의 잔액까지만 세기) |
| capped allowance / capped to zero | 상한을 씌운 허락 / 0으로 잘림 |
| uncapped (allowance layer) | 상한 없는 (허락 층) |
| thin (allowance layer) | 얇은 (허락 층)(허락 화살표가 아주 적음) |
| union graph / union in-degree | 합집합 그래프(두 층 가운데 어느 쪽에든 화살표가 있는 계약 쌍) / 합집합 입차수 |
| in-approve value | 받은 허락 금액 |
| out-of-window prediction | 기간 밖 예측 |
| discovery-order test | 발견 순서 검증 |
| crawl-ordering experiment (Cho et al.) | 크롤 순서 실험 |
| crawl / crawler | 크롤(계약을 하나씩 찾아 읽어 가기) / 크롤러 |
| ordering / ordered by X | 순서 규칙 / X로 순서를 정한 |
| visit / visit index $t_h$ | 방문 / 방문 번호 $t_h$ |
| frontier | 프런티어(찾았지만 아직 방문하지 않은 계약들) |
| seed (of a crawl) | 출발 계약 (S-PR의 씨앗, 무작위 시드와 섞지 않음) |
| reveal mode, \texttt{both}, \texttt{out} | 공개 방식(방문할 때 어떤 화살표가 드러나는지), \texttt{both}(들어오고 나가는 화살표), \texttt{out}(나가는 화살표만) |
| universe $\mathcal{U}$ | 우주 $\mathcal{U}$(크롤이 다닐 수 있는 계약 전체) |
| giant strongly connected component (giant SCC) | 거대 강연결 성분(서로 오갈 수 있는 가장 큰 계약 묶음, SCC) |
| weakly connected component (WCC) | 약연결 성분(방향을 무시하면 이어지는 묶음, WCC) |
| bow-tie decomposition (IN, OUT) | 나비넥타이 분해(IN, OUT은 그대로) |
| breadth-first (BFS) | 너비 우선(BFS, 찾은 차례대로 방문하기) |
| backlink / contract backlinks / number of contract backlinks | 역링크(그 계약으로 들어오는 화살표) / 계약 역링크 / 계약 역링크 수 |
| importance | 중요도 |
| user-account demand | 사용자 계정의 수요 |
| user-account inflow $I_T$ | 사용자 계정 유입 $I_T$(사용자 계정이 그 계약에 보낸 달러) |
| user-authorised value $I_A$ | 사용자 허락 금액 $I_A$(사용자 계정이 그 계약에 허락한 달러, 잔액 상한 적용) |
| hot set $H_q(I)$ / hot contract | 뜨거운 집합 $H_q(I)$(중요도가 가장 큰 계약들) / 뜨거운 계약 |
| ideal order | 이상적인 순서 |
| wasted visits | 헛 방문(중요도가 0인 계약에 간 방문) |
| hub | 허브(화살표가 아주 많이 들어오는 계약) |
| recompute share $\rho$ / recompute | 다시 계산 몫 $\rho$ / 다시 계산 |
| warm start | 이어 시작하기(앞 벡터에서 다시 계산을 시작함) |
| verdict V1, V2, V3 | 판정 V1, V2, V3 |
| structure pilot / stop flag | 구조 파일럿(무게 없이 그래프 모양만 본 예비 점검) / 멈춤 표시 |
| normalized in-strength $\delta'$ | 정규화한 들어오는 무게 $\delta'$ |
| deployment / factory | 배포(계약을 체인에 올리기) / 팩토리(계약을 찍어 내는 계약) |
| balance threshold $\theta$ | 잔액 문턱 $\theta$ |
| applied criteria (F1, F2) | 적용한 두 기준(F1, F2) |

정해 둔 문장(뜻을 바꾸지 않고 문장 꼴만 해요체에 맞춰요):

- 수정 분석의 정의(원문의 integrity sentence): "등록 분석의 결과를 안 뒤에 수정 분석을 정했어요. 금액은 다섯 토큰의 달러 금액이고, 점수는 각 동결 직전 12개월의 사건으로 만들어요. 그래프의 점은 스마트 계정이 아닌 계약이고, 화살표는 체인 전체에서 읽어요. 허락은 동결 시점 주인의 잔액까지만 세고, 잔액은 \texttt{Transfer} 로그로 다시 계산해요. 상수는 계약 그래프 위에서 정했어요. 발견 순서 검증도 이렇게 정한 것에 들어요."
- 발견 순서 검증의 지위: "발견 순서 검증은 등록 분석의 결과를 안 뒤에 정했고, 계획과 등록 문서의 어떤 규칙도 정하지 않아요."
- 규칙 B: "이 논문은 규칙 B의 등록된 기준 가운데 두 가지, F1과 F2를 적용해요. 등록 문서에 따르면 규칙 B는 자기 기준이 하나하나 모두 설 때만 충족돼요." 결과는 "규칙 B는 충족하지 못했어요."
- 판정 V2 문장(다이제스트 `decision.statements[0]`): "지금까지 읽은 계약들로 계산한 C-PR로 순서를 정하면, 거대 강연결 성분의 무작위 계약에서 출발한 크롤은 우주에서 사용자 계정 유입이 가장 큰 계약들과 사용자 허락 금액이 가장 큰 계약들에 너비 우선 크롤보다 빨리 닿았지만, 계약 역링크 수로 순서를 정한 크롤보다 빨리 닿지는 못했어요. 계약 역링크 수로 순서를 정한 크롤이 더 빨리 닿았어요."

## 5d. 모든 한국어 글이 지키는 규칙 (2026-11-07 저자 결정)

- 주 분석의 그래프에는 사용자 계정이 없어요. 등록 분석을 설명하는 곳 밖에서는 사용자 계정을 점(노드)으로 쓰지 않아요.
- GMX, 거래자(트레이더), 청산 결과, F3–F5를 쓰지 않아요. 무엇을 지웠다, 뺐다, 보고하지 않았다는 문장도 쓰지 않아요.
- 주 분석의 결과를 "등록된 결과"라고 부르지 않아요. 규칙 A와 B는 계약 그래프의 점수에 적용한 재분석이에요.
- 바꾼 이력을 쓰지 않아요("원래는", "처음에는", "줄였다", "바꿨다", "더 이상", "대신"). 등록 분석과 계획을 설명하는 문단만 예외예요.
- 신용은 시험하지 않은, 바라는 나중의 쓰임으로만 적어요.
- 발견 순서 검증은 미리 정했다, 등록했다고 쓰지 않고, 그 프로토콜을 언제 정했는지도 쓰지 않아요.
- (2026-11-11 저자 결정) 연구 내용을 써요. 연구 과정이 정당했다고 변호하지 않아요. 커밋 해시는 부록의 데이터 위치 안내에서 한 번만 써요(영어 원고와 같은 곳). 우리가 커밋하고, 자료를 뽑고, 계산을 돌린 날짜와 시각은 쓰지 않고, 필요할 때만 순서를 적어요. SHA-256 값, 초 단위 간격, 제3자 타임스탬프 이야기도 쓰지 않아요. 자료가 어느 기간의 것인지(점수·라벨 기간, 동결 시점, 블록 번호)는 그대로 적어요.

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
