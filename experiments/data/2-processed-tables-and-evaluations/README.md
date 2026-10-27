# 2-processed-tables-and-evaluations

점수와 평가 요약입니다. 스크립트가 쓰는 대로 두고 손으로 고치지 않습니다. 컨트랙트별 점수 같은 큰 표는 parquet 조각이라 Drive에만 있고, GitHub에는 JSON 요약과 기록이 있습니다.

이 폴더 바로 아래는 등록 분석의 결과입니다. 같은 이름의 폴더가 `revised-usd/` 아래에 한 벌 더 있고, 그쪽이 수정 분석(논문의 주 결과)입니다. `cohort/`의 등록 코호트, `gmx/`의 해독한 종료, `registered-w1/extraction_manifest.json`은 두 분석이 함께 씁니다.

| 폴더 | 내용 | 쓰는 스크립트 |
|---|---|---|
| `same-window/` | 관측 기간 안의 평가 요약(`eval_summary.json`)과 코호트 점수 | `run_same_window.py` |
| `holdout-w0/` | 홀드아웃 W0의 평가 요약 | `run_holdout.py` |
| `registered-w1/` | 등록 창 W1의 평가 요약(등록 분석)과 7~9월 추출 기록(`extraction_manifest.json`) | `run_registered.py`, `extract_w1.py` |
| `revised-usd/window-w1/` | 수정 분석의 W1 평가 요약. 등록된 결과가 아니어서 폴더 이름을 달리 둡니다. | `run_registered.py` |
| `sybil-model/` | Sybil 비용 모형 | `sybil_model.py` |
| `robustness/` | 강건성과 민감도 | `run_robustness.py` |
| `benchmark/` | 계산 벤치마크와 규모 확장 | `run_benchmark.py` |
| `supplementary/` | 라벨을 본 뒤 계산한 대비 | `run_supplementary.py` |
| `describe/` | 기술 통계 | `describe_data.py` |
| `cohort/` | 매칭 코호트(`matched_cohort.json`과 조각) | `build_cohort.py`, 수정 분석은 `run_usd_pipeline.py` |
| `gmx/` | 해독한 GMX V2 종료(`gmx_contract_closes_*_decoded`) | `decode_gmx_events.py` |

논문이 인용하는 요약은 `publish_results.py`가 `../3-published-results-for-thesis/`로 복사합니다.
