# overleaf-github-ko — 학위 논문 쉬운 한국어 번역본

영어 학위 논문 `../overleaf-github/`(원고 저장소 `phd-dissertation-draft-en`)를 **초등학생도 따라 읽을 수 있는 쉬운 한국어로 번역**한 LaTeX 프로젝트입니다.

- 결과물: [`main.pdf`](main.pdf)
- 번역한 원문: 원고 커밋 `dc090f9`(2026-10-03, 183쪽)
- 『허락의 화살표』(`../customized-books/book-for-children/`)처럼 새로 쓴 책이 아니라 **번역**입니다. 장·절·문단·목록·표·그림·수식의 구성은 원문과 같습니다.

## 번역 원칙

- 문장 하나하나를 옮겼어요. 줄이거나 덧붙이지 않았고, 어려운 낱말에는 그 장에서 처음 나올 때만 괄호로 짧은 풀이를 달았어요.
- 말투는 해요체예요. 긴 영어 문장은 짧은 한국어 문장 여러 개로 나누었어요.
- 숫자, 구간, 수식, 표의 값, 인용 번호, 레이블과 참조는 원문과 하나도 다르지 않아요. `scripts/check_ko.py`로 파일마다 대조했어요.
- 방법 이름은 논문 그대로예요: 엔도스랭크(EndorseRank), AWP, C-PR, S-PR. 표 안에서는 영어 이름(EndorseRank, ER, AWP …)을 그대로 썼어요.
- 참고문헌 목록은 찾아보기 쉽도록 원래 언어(영어) 그대로 두었어요.
- 용어집과 문체 기준은 [`TRANSLATION-GUIDE.md`](TRANSLATION-GUIDE.md)에 있어요. 원문이 바뀌어 번역을 고칠 때도 이 기준을 따르세요.

## 폴더

| 경로 | 내용 |
|---|---|
| `main.tex`, `Config/preamble.tex` | 원문과 같은 구성. 머리말에 한글 글꼴(kotex)과 한국어 이름표(그림, 표, 알고리즘)를 더했어요 |
| `01-Intro/` | 표지, 초록, 차례, 줄임말과 기호 |
| `Chapter-01-…` ~ `Chapter-08-Appendix/` | 1~6장, 참고문헌, 부록 |
| `results/tables/` | 결과 표 28개(원문 표를 번역한 것, 숫자는 그대로) |
| `Figures/` | TikZ 그림 두 개(번역)와 `generated/`의 그래프 다섯 개(같은 자료로 한국어 글자를 넣어 다시 그림) |
| `scripts/check_ko.py` | 원문과 번역을 파일마다 대조(레이블, 참조, 인용, 수식, 숫자, 표 구조, 문단 수, 남은 영어 문장) |
| `scripts/check_particles.py` | 빌드 뒤 `\ref` 뒤의 조사를 실제 번호에 맞춰 검사(표 4.3은, 표 4.2는) |
| `scripts/make_toc.py` | 번역한 절 제목으로 `01-Intro/03-TOC.tex`를 다시 만듦 |
| `scripts/make_ko_figures.py` | `../wallet-reputation-experiments`의 자료로 한국어 그래프 다섯 개를 다시 그림 |

## 빌드

XeLaTeX와 `kotex`(TeX Live의 `collection-langkorean`, MiKTeX는 자동 설치)가 필요해요. 글꼴은 나눔명조·나눔고딕이 있으면 쓰고, 없으면 Windows의 바탕·맑은 고딕을 써요.

```powershell
cd 1-Dissertation-Works\ERC20-Allowance-PageRank-Wallet-Reputation\dissertation\overleaf-github-ko
.\build.ps1
```

## 원문이 바뀌었을 때

1. 바뀐 원문 문단만 같은 기준으로 다시 번역해요.
2. `python scripts/check_ko.py ../overleaf-github/<파일> <파일>`로 대조해요.
3. 빌드한 뒤 `python scripts/check_particles.py`로 참조 번호 뒤의 조사를 확인해요.
4. 절 제목이 바뀌었으면 `python scripts/make_toc.py`, 그래프 자료가 바뀌었으면 `python scripts/make_ko_figures.py`를 실행해요.
