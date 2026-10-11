# Vendored libraries

Everything in `lib/` is a third-party file copied unchanged from the npm registry
(`npm pack <name>@<version>`), so the deck runs offline from `file://`.
Full licence texts are in `lib/licenses/`.

| File(s) in `lib/` | Library | Version | Licence |
|---|---|---|---|
| `gsap.min.js`, `Flip.min.js`, `MotionPathPlugin.min.js`, `DrawSVGPlugin.min.js`, `MorphSVGPlugin.min.js`, `SplitText.min.js`, `ScrambleTextPlugin.min.js`, `CustomEase.min.js` (from `dist/`) | GSAP (GreenSock) core and plugins | 3.15.0 | GSAP Standard "No Charge" License — free to use, not open source; terms at <https://gsap.com/standard-license> (the notice is kept in each file's header). |
| `three.min.js` (from `build/`) | three.js | r158 (npm 0.158.0) | MIT — `licenses/three.LICENSE.txt` |
| `katex/katex.min.js`, `katex/katex.min.css`, `katex/fonts/*.woff2`, `katex/fonts/*.woff` (from `dist/`) | KaTeX | 0.16.47 | MIT — `licenses/katex.LICENSE.txt` (the KaTeX fonts are MIT-licensed with KaTeX) |
| `d3.min.js` (from `dist/`) | D3 | 7.9.0 | ISC — `licenses/d3.LICENSE.txt` |
| `fonts/PretendardVariable.woff2` (from `dist/web/variable/woff2/`) | Pretendard (variable) | 1.3.9 | SIL Open Font License 1.1 — `licenses/pretendard.OFL.txt` (Reserved Font Name "Pretendard") |

Notes
- three.js r158 is the last line that still ships the classic `build/three.min.js`; it prints a
  one-line deprecation notice in the console, which is expected.
- The KaTeX `.ttf` fonts are not copied: browsers use the `.woff2` (or `.woff`) entries of `katex.min.css`.
- `css/deck.css` also maps the Hangul code points of the KaTeX font families to Pretendard, so Korean
  inside formulas never falls back to a missing glyph.
- To update a library: `npm pack <name>@<version>`, copy the same files, update this table.
