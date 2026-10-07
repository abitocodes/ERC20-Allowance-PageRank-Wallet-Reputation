# Dissertation translations (EN / EN-KO)

| File | Description |
|------|-------------|
| `Full_Dissertation_DRAFT_070426_2209.docx` | English dissertation draft snapshot |
| `Full_Dissertation_DRAFT_070426_2209_EN-KO.docx` | Interlinear EN then KO (each English paragraph followed by matched Korean in italic) |
| `_ko_translation_cache_dissertation.json` | Translation cache (resume / rebuild) |

Matching is by exact English paragraph text → Korean map (not by sequential index).

Korean LaTeX working copy remains in `../kr/`.

Rebuild:

```powershell
python ..\..\..\proposal\scripts\build_interlinear_en_ko_docx.py `
  --src ".\Full_Dissertation_DRAFT_070426_2209.docx" `
  --dst ".\Full_Dissertation_DRAFT_070426_2209_EN-KO.docx" `
  --cache ".\_ko_translation_cache_dissertation.json"
```
