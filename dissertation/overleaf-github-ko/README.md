# overleaf-github-ko — 학위 논문 쉬운 한국어 번역본

영어 학위 논문 `../overleaf-github/`(원고 저장소 `phd-dissertation-draft-en`)를 **초등학생도 따라 읽을 수 있는 쉬운 한국어로 번역**한 LaTeX 프로젝트입니다.

- 결과물: [`main.pdf`](main.pdf)
- 번역한 원문: 원고 커밋 `6a5dfb6`(브랜치 `score-windows-12m`, 2026-10-28, 205쪽). 앞선 번역(원문 `a0affc5`)에서 영문이 그대로인 문단은 그 번역을 그대로 두고, 바뀐 문단만 다시 옮겼어요.
- 제목은 원문과 같이 승인된 제목을 씁니다: 「ERC-20 허락 화살표를 페이지랭크에 넣어 온체인 지갑 평판 점수를 더 좋게 만들기」.

## 번역 원칙

- 문장 하나하나를 옮겼어요. 줄이거나 덧붙이지 않았고, 어려운 낱말에는 그 장에서 처음 나올 때만 괄호로 짧은 풀이를 달았어요.
- 말투는 해요체예요. 긴 영어 문장은 짧은 한국어 문장 여러 개로 나누었어요.
- 숫자, 구간, 수식, 표의 값, 인용 명령과 키, 레이블과 참조는 원문과 하나도 다르지 않아요. `scripts/check_ko.py`로 파일마다 대조했어요.
- 방법 이름은 논문 그대로예요: 엔도스랭크(EndorseRank), AWP, C-PR, S-PR. 표 안에서는 영어 이름(EndorseRank, ER, AWP …)을 그대로 썼어요.
- 인용은 원문처럼 APA 7(biblatex)이고, 참고문헌 목록은 찾아보기 쉽도록 원래 언어(영어) 그대로 두었어요.
- 용어집과 문체 기준은 [`TRANSLATION-GUIDE.md`](TRANSLATION-GUIDE.md)에 있어요(§5b는 이 논문에서 더 쓰는 말). 원문이 바뀌어 번역을 고칠 때도 이 기준을 따르세요.

## 폴더

| 경로 | 내용 |
|---|---|
| `main.tex`, `Config/preamble.tex`, `Config/references.bib` | 원문과 같은 구성. 머리말에 한글 글꼴(kotex)과 한국어 이름표(그림, 표, 알고리즘)를 더했어요 |
| `01-Intro/` | 표지, 장 표지, 선언문, 초록, 차례, 줄임말과 기호 |
| `Chapter-01-…` ~ `Chapter-08-Appendix/` | 1~6장, 참고문헌, 부록 |
| `results/tables/` | 결과 표 30개(원문 표를 번역한 것, 숫자는 그대로) |
| `Figures/` | TikZ 그림 두 개(번역)와 `generated/`의 그래프 다섯 개(같은 자료와 같은 계산으로 한국어 글자를 넣어 다시 그림) |
| `scripts/check_ko.py` | 원문과 번역을 파일마다 대조(레이블, 참조, 인용 키, 수식, 숫자, 표 구조, 문단 수, 남은 영어 문장) |
| `scripts/check_particles.py` | 빌드 뒤 `\ref` 뒤의 조사를 실제 번호에 맞춰 검사(표 4.3과, 표 4.2와) |
| `scripts/make_toc.py` | 번역한 절 제목으로 `01-Intro/03-TOC.tex`를 다시 만듦 |
| `scripts/make_ko_figures.py` | `../../experiments/scripts/export_latex.py`의 그림 함수를 그대로 불러 한국어 그래프 다섯 개를 다시 그림 |

## 빌드

XeLaTeX, biber와 `kotex`(TeX Live의 `collection-langkorean`, MiKTeX는 자동 설치)가 필요해요. 글꼴은 나눔명조·나눔고딕이 있으면 쓰고, 없으면 Windows의 바탕·맑은 고딕을 써요.

```powershell
cd 1-Dissertation-Works\ERC20-Allowance-PageRank-Wallet-Reputation\dissertation\overleaf-github-ko
.\build.ps1
```

`build.ps1`은 원문과 같아서 전체 원고 뒤에 장별 PDF도 만들어요. 장별 PDF는 저장소에 올리지 않아요.

## 원문이 바뀌었을 때

1. 바뀐 원문 문단만 같은 기준으로 다시 번역해요.
2. `python scripts/check_ko.py ../overleaf-github/<파일> <파일>`로 대조해요. 원문 저장소를 다른 곳에 두었으면 `OVERLEAF_EN` 환경 변수로 그 경로를 알려 줘요(`make_toc.py`).
3. 빌드한 뒤 `python scripts/check_particles.py --fix`로 참조 번호 뒤의 조사를 맞추고 다시 빌드해요.
4. 절 제목이 바뀌었으면 `python scripts/make_toc.py`, 그래프 자료가 바뀌었으면 `CONTRACT_REP_VARIANT=usd12m python scripts/make_ko_figures.py`를 실행해요.
