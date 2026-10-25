# dissertation

학위논문 원고, 발표 자료, 원고를 쓸 때 지키는 메모입니다.

| 폴더 | 내용 |
|---|---|
| `overleaf-github/` | 영문 원고(UNISA 양식 LaTeX, XeLaTeX와 biber). 별도 저장소 `phd-dissertation-draft-en`을 서브모듈로 두었고, Overleaf가 그 저장소의 `main`을 읽습니다. 원고 소스, 빌드한 `main.pdf`와 장별 PDF, 투고 원고 `manuscripts/`(`A-plos-one`, `B-ieee-access`), 그 보조 분석 `analysis/`가 있습니다. 폴더가 비어 있으면 저장소 최상위에서 `git submodule update --init`을 실행합니다. |
| [`presentation/`](presentation/) | 학위논문 발표 자료: HTML 슬라이드 59장(한국어판, 영문판), 한 파일 판과 한국어 인쇄판 PDF, 해설 영상 도구 |
| [`notes/`](notes/) | 원고 작성 규칙과 메모. 빌드에 들어가지 않습니다. |

서브모듈의 이름(`.gitmodules`의 `2-Dissertation-Draft/overleaf-github`)은 일부러 옛 이름 그대로 둡니다. 이름이 곧 작업본마다 서브모듈의 git 데이터를 두는 곳(`.git/modules/<이름>`)이라, 바꾸면 기존 작업본이 원고를 다시 받습니다.

## 원고 고치기

1. [`notes/`](notes/)의 규칙을 읽습니다. `_writing-brief.md`부터 읽습니다.
2. `overleaf-github/`의 장 파일(`Chapter-*/index.tex`)을 고칩니다. 원고 본문은 영어로 씁니다.
3. `overleaf-github/`에서 `.\build.ps1`로 통합본과 장별 PDF를 빌드합니다(xelatex → biber → xelatex 두 번). 오류 0, 정의되지 않은 참조 0을 확인합니다. MiKTeX에서는 PATH를 `/c/Program Files/MiKTeX/miktex/bin/x64:/c/Windows/System32:/c/Windows:/usr/bin`으로 줄여야 biber와 xelatex가 돕니다.
4. 서브모듈에서 커밋·푸시한 뒤, 이 저장소에서 서브모듈 포인터를 커밋합니다.

결과 표(`results/tables/*.tex`)와 그림(`Figures/generated/*.pdf`)은 손으로 고치지 않습니다. `../experiments/`에서 `CONTRACT_REP_VARIANT=usd python scripts/export_latex.py`로 다시 만듭니다. 원고의 수치는 `../experiments/data/3-published-results-for-thesis/revised-usd/results_digest.md`에서 가져옵니다.

## 투고 원고 2편

UNISA 학위를 받으려면 인정 학술지에 투고한 원고 2편이 필요합니다([`2-Graduation/`](../../../2-Graduation/)). 서브모듈의 `manuscripts/`에 A(PLOS ONE), B(IEEE Access) 원고가 있습니다. 2026-10-22 검토에서 학위논문 원고를 고친 내용은 아직 따르지 않았습니다.

## 남은 일

[`notes/_todo.md`](notes/_todo.md)에 있습니다. 지도교수 검토 전이고, 수정 분석을 주 분석으로 할지 지도교수가 아직 확인하지 않았습니다. 그 밖에 UNISA의 다른 공식 언어 두 가지로 된 제목·초록·핵심어(대학 언어 서비스가 번역), 연구 윤리 승인 번호와 날짜, 초록 길이 확인 등이 남아 있습니다.
