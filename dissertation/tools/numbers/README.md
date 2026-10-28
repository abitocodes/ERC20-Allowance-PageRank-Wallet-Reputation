# numbers — 원고 수치를 digest와 대조하는 도구

분석을 다시 돌려 결과 요약(`results_digest.md`)이 바뀌었을 때, 원고에 적힌 옛 수치를 새 수치로 옮기고 남은 것을 찾는 도구입니다. 문장을 판단하지는 않습니다. 확실한 것만 바꾸고 나머지는 검토 목록에 올립니다. 2026-10-28 점수 기간 변경(`../../notes/_change-record-score-windows.md`)에 처음 썼습니다.

| 파일 | 하는 일 |
|---|---|
| `numbers.py` | `scan`: 원고(.tex, 생성된 표 제외)의 모든 수를 옛 digest, 새 digest, 남는 digest(등록 분석)의 같은 키와 짝지어 CSV로 냄. `apply`: 확실한 것(unique)과 검토자가 고른 것만 바꿈. `audit`: 남은 옛 값을 찾음 |
| `triples.py` | "점추정 [하한, 상한]" 묶음을 어느 digest가 가졌는지 셈(새 것, 옛 것만, 등록 것만, 아무 데도 없음) |
| `digest_diff.py` | 두 digest를 키마다 비교하고 판정이 뒤집힌 줄을 보임 |

```bash
python numbers.py scan  --old OLD.md --new NEW.md --keep KEEP.md --out report.csv FILE.tex ...
python numbers.py apply --report report.csv
python numbers.py audit --old OLD.md --keep KEEP.md --new NEW.md FILE.tex ...
python triples.py --new NEW.md --old OLD.md --keep KEEP.md FILE.tex ...
```

- 수는 적힌 정밀도로 비교합니다. "0.41"은 digest 값이 그렇게 반올림되고 소수 자리가 적어도 같을 때만 맞습니다.
- 날짜, 시각, TikZ 좌표 줄은 수로 읽지 않습니다.
- 옛 digest는 `git show <커밋>:…/results_digest.md`로 꺼내 씁니다.
- 등록 분석 문장의 수는 남는 digest(`--keep`)의 값이라 바꾸지 않습니다.
