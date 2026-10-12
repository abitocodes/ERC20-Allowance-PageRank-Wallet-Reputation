# archive — 지갑 평판 연구 자료 (2026-10-11 보관)

2026-10-11에 논문을 컨트랙트 평판 연구로 바꾸면서, 그 전의 지갑 평판 연구(GMX V2 트레이더 지갑, 2025-12~2026-08 데이터) 자료를 이 폴더로 옮겼습니다. 내용은 고치지 않고 위치만 바꿨습니다.

| 폴더·파일 | 내용 | 옮기기 전 위치 |
|------|------|------|
| `wallet-reputation-experiments/` | 지갑 평판 연구의 실험 코드와 데이터 | `dissertation/wallet-reputation-experiments/` |
| `overleaf-github-ko/` | 지갑 평판 원고의 쉬운 한국어 번역본 | `dissertation/overleaf-github-ko/` |
| `local-other/` | 원고 PDF 초안, 한국어 초안(`kr/`), 교수님 피드백 원문(`sources/`), 요약·번역 | `dissertation/local-other/` |
| `customized-books/` | 어린이 책 『허락의 화살표』와 한국어 오디오북 | `dissertation/customized-books/` |
| `professor-feedback-summary.md` | 연구계획서·초안에 받은 교수님·심사위원 피드백 정리 | `dissertation/professor-feedback-summary.md` |

## 알아둘 것

- 여기 있는 문서 속 경로는 옮기기 전 위치를 기준으로 씁니다. 형제 폴더끼리의 상대 경로(`../wallet-reputation-experiments`, `../local-other` 등)는 그대로 맞습니다.
- 문서들이 가리키는 `../overleaf-github/`(영문 원고)는 이제 컨트랙트 평판 원고입니다. 지갑 평판 영문 원고는 원고 저장소 `phd-dissertation-draft-en`의 커밋 `7790f76`(투고 원고 `manuscripts/`와 보조 분석 `analysis/` 포함)에 남아 있습니다. `git -C ../dissertation/overleaf-github show 7790f76:main.tex`처럼 꺼내 볼 수 있습니다.
- `wallet-reputation-experiments/scripts/`는 새 실험의 테스트(`../experiments/tests/conftest.py`)가 읽기 전용 기준으로 불러옵니다. 옮기거나 지우지 마세요.
- 옛 실험 코드의 `project_paths.py`는 원고 폴더를 `archive/overleaf-github`로 찾기 때문에(없는 폴더) 새 원고를 덮어쓰지 않습니다.
- Windows 경로 길이 때문에 폴더를 한 단계 더 깊게 넣지 않았습니다.
- `wallet-reputation-experiments/data/`의 parquet 파일은 2026-10-12부터 GitHub에 없고 공개 Google Drive 폴더의 `wallet-reputation-archive/`에 있습니다. 데이터 문서(`data/README.md`)의 "GitHub에 올림" 설명은 그 전 기준입니다. 받으려면 `../experiments/`에서 `python scripts/drive_sync.py pull "archive/*"`를 실행합니다.
