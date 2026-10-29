# manuscripts-ko — 투고 원고 A·B의 쉬운 한국어 해설판

투고 원고 A(PLOS ONE)와 B(IEEE Access)의 영문 원고(`../overleaf-github/manuscripts/`)를 저자가 읽으려고 쉬운 한국어로 풀어 쓴 해설판입니다. Overleaf와 원고 저장소에는 올리지 않습니다.

- 결과물: [`A-plos-one/main.pdf`](A-plos-one/main.pdf), [`B-ieee-access/main.pdf`](B-ieee-access/main.pdf)
- 옮긴 원문: 원고 저장소 커밋 `07391e9`의 `manuscripts/A-plos-one`과 `manuscripts/B-ieee-access`.

## 어떻게 썼나

- 문장 대 문장 번역이 아닙니다. 영문 원고의 절 순서를 따르되, 절마다 내용을 해요체로 풀어 썼습니다. 원고의 주장, 수치, 판정, 단서, 한계, 표, 그림, 식은 모두 들어 있고, 원고에 없는 주장은 넣지 않았습니다.
- 원고에 없는 읽기 도움 두 가지를 더했습니다. 회색 「요점」 상자(그 절의 핵심)와 파란 풀이 상자(개념, 작은 예, 표 읽는 법)입니다. 상자 밖 본문이 원고의 내용입니다.
- 앞부분에 「이 글을 읽는 법」, 「한눈에 보기: 초록」, 「먼저 알아 둘 말」(용어 풀이)을, 끝에 「투고 서류에 들어가는 것」(윤리, 자료 공개, 생성형 AI 사용, 감사의 말, 보조 자료)을 두었습니다.
- 용어는 학위논문 한국어판의 용어집(`../overleaf-github-ko/TRANSLATION-GUIDE.md` §5, §5b)을 따릅니다. 쓰기 기준 전체는 [`WRITING-GUIDE.md`](WRITING-GUIDE.md)에 있습니다.
- 표는 한국어로 다시 짰고 수는 영문 표와 같습니다. 그림은 영문 그림을 그리는 스크립트를 그대로 불러 글자만 한국어로 바꿔 그렸습니다.

## 폴더

| 경로 | 내용 |
|---|---|
| `WRITING-GUIDE.md` | 쓰기 기준: 말투, 용어, 문서 구성, 상자, 수치, 서술 규칙, LaTeX, 빌드와 점검 |
| `common/preamble.tex` | 두 해설판이 같이 쓰는 머리말(XeLaTeX, kotex, 글꼴, 상자, 제목 블록) |
| `A-plos-one/` | 원고 A: `main.tex`(앞부분과 용어 풀이)와 본문 `01-intro.tex`–`05-submission.tex`, 한국어 그림 `figures/fig1_ko.pdf`와 그 스크립트 `make_ko_figures.py` |
| `B-ieee-access/` | 원고 B: `main.tex`(앞부분과 용어 풀이)와 본문 `01-intro.tex`–`07-submission.tex`(영문 I–X절과 부록 A, 투고 서류), 한국어 그림 `figures/fig_contrasts.pdf`, `figures/fig_lambda_sweep.pdf`와 그 스크립트 `make_ko_figures.py`. 그림 1(층 구조)은 본문 안의 TikZ예요 |
| `build.ps1` | 빌드(xelatex → bibtex → xelatex 두 번)와 점검: 오류, 정의되지 않은 참조·인용, 1pt를 넘는 넘침, 글상자 밖 글자 |
| `check_numbers.py` | 해설판의 수를 영문 원고의 수와 대조 |
| `check_layout.py` | 글상자 밖으로 나간 글자 찾기(`build.ps1`이 부름) |
| `check_particles.py` | `\ref`·`\eqref` 뒤 조사를 실제 번호의 읽는 소리에 맞춰 검사(`build.ps1`이 부름, 고치려면 `--fix`) |

## 빌드와 점검

PowerShell에서 실행합니다(Git Bash의 xelatex는 쪽을 내보내다 멈춥니다).

```powershell
cd 1-Dissertation-Works\ERC20-Allowance-PageRank-Wallet-Reputation\dissertation\manuscripts-ko
.\build.ps1                                   # 둘 다, 또는 .\build.ps1 A-plos-one
python -I -X utf8 check_numbers.py A-plos-one
python -I -X utf8 check_numbers.py B-ieee-access
```

- 글꼴은 KoPubWorld 바탕·돋움을 쓰고, 없으면 Noto CJK KR, 그것도 없으면 Windows의 바탕·맑은 고딕을 씁니다. 참고문헌은 영문 원고의 `references.bib`를 그대로 읽습니다.
- `check_numbers.py`의 1번(한국어에만 있는 수)과 2번(부호가 다른 수) 목록은 비어 있어야 하고, 3번(한국어에 없는 수) 목록은 하나씩 확인합니다. 예를 들려고 지어낸 수는 `\ill{…}`로 감싸서 점검에서 뺍니다.

## 영문 원고가 바뀌었을 때

1. 바뀐 절만 같은 기준으로 다시 씁니다. 표의 수가 바뀌었으면 한국어 표도 고칩니다.
2. 그림이 바뀌었으면 그 폴더에서 `python -I -X utf8 make_ko_figures.py`를 다시 돌립니다. 영문 그림 스크립트가 읽는 `phd_works` 위치는 `PHD_WORKS`로 주거나, 이 저장소 안이면 저절로 찾습니다.
3. 빌드하고 `check_numbers.py`를 돌립니다. 제목 블록의 원문 커밋도 고칩니다.
