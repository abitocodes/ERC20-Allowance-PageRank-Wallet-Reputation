# Narration script guide: YouTube long-form, English edition

This script is the voice-over for a landscape YouTube video made from a PhD defence deck (59 slides, 304 click steps). A TTS engine (Supertonic 2) reads it; subtitles are shipped separately. The picture is the slide itself; on top of it we add motion graphics: camera zooms, highlight marks and small term cards.

## 1. Voice and content
- Warm, clear and patient, like a good teacher walking a curious newcomer through the idea. Plain words, short sentences, active voice. The speaker is the author of the thesis; first person ("I", "my thesis") is fine, as in the speaker notes.
- The speaker note (`note`) is the **source of truth**. Do not drop, change or inflate its claims, numbers or qualifications (for example "re-analysis", "post hoc", "exploratory", "registered", "fixed in advance", "a check, not a validation"). Never add a number, result or claim that is not in the note or on the slide.
- Make it friendly by: explaining each term in plain words the first time it appears, saying in one sentence why we are looking at something, guiding the eye ("look at the amber arrows on the left"), unpacking analogies the note already uses, and linking slides and chapters smoothly.
- Leave out what means nothing when heard: commit hashes, file paths, block numbers, bracketed stage directions such as "(wallet window)" (do not read these). Do say the key numbers that the slide shows large.
- Length: per step about **0.9 to 1.2 times the note** (the English notes are already long; tighten wordy ones). A step whose note is one or two sentences gets 2 to 4 sentences, adding guidance on what to look at. The whole video will run about 85 to 95 minutes. Do not repeat yourself.
- Do not oversell the findings. Say "better" or "worse" only as far as the note does. Where the raw count of approving owners wins, say so plainly.

## 2. One line
Each step has a `lines` array. One line is normally one sentence (at most two short ones). Each line has:
- `sub`: the subtitle text, with numbers and symbols written as on screen ("45.8% of allowances are unlimited", "τ_b", "C-PR", "W1").
- `tts`: what the TTS reads. It must **say exactly what `sub` says**, following section 3.
- `focus`: array of anchor ids the camera and highlight point at while this line plays (only ids from that step's `anchors`). `[]` when nothing needs pointing at.
- `zoom`: `"none"` (highlight only), `"soft"` (about 1.25x), `"close"` (about 1.6x). Use `"none"` when focus is empty.
- `mark`: `"ring"` (rounded outline), `"underline"` (good for a single line of text), `"spot"` (dims everything else a little), `"none"`.
- `card`: optional small card that pins down a key term the first time it appears: `{ "title": "Allowance", "body": "A record that lets a contract spend some of your tokens for you" }`. Title at most 24 characters, body at most 70. **At most one per slide**, only when it truly helps (around 30 in the whole script). While a card shows, the slide shrinks a little and the card floats under it.

## 3. `tts` text rules (most important)
The TTS engine does not read digits or symbols reliably. In `tts` use only **letters, spaces, apostrophes, hyphens and . , ? !**. No digits, no Greek letters, no %, /, =, +, (, ), ·, quotes or other symbols.
- Numbers in words: 15,107 → "fifteen thousand one hundred and seven"; 6,221,665 → "six million two hundred twenty-one thousand six hundred sixty-five"; 0.585 → "zero point five eight five"; 45.8% → "forty-five point eight percent"; October 2026 → "October twenty twenty-six"; 2/3 → "two thirds"; −0.028 → "minus zero point zero two eight"; [0.098, 0.122] → "from zero point zero nine eight to zero point one two two". Long figures may be rounded in `tts` **only if `sub` rounds them the same way**.
- Terms, said the same way everywhere:

| On screen | tts |
|---|---|
| EndorseRank | EndorseRank |
| PageRank | PageRank |
| C-PR | C P R |
| S-PR | S P R |
| AWP | A W P |
| EOA | E O A |
| ERC-20 | E R C twenty |
| USDC / USDT0 / WETH / WBTC / ARB | U S D C / U S D T zero / wrapped ether / wrapped bitcoin / A R B |
| GMX | G M X |
| W0 / W1 | W zero / W one |
| T_obs | T obs |
| τ, τ_b, Δτ | tau, tau b, delta tau |
| ρ (Spearman) | rho |
| λ, σ, δ, π | lambda, sigma, delta, pi |
| d, b, m, U, V, E | d, b, m, U, V, E (single letters are fine) |
| r_v | r of v |
| \|V\|, \|E\| | the number of nodes, the number of edges |
| ln 3 | the natural log of three |
| V(z) | V of z |
| RQ1 … RQ5 | research question one … five |
| H1, R1, F1 | H one, R one, F one |
| DefiLlama / Chainlink | DeFi Llama / Chainlink |
| transferFrom / approve / permit | transfer from / approve / permit |
| EIP-2612 / EIP-7702 | E I P twenty-six twelve / E I P seventy-seven oh two |
| Mnkandla / Moulla / Attipoe | Mnkandla / Moulla / Attipoe |
| USD, $ | dollars |

Keep each `tts` line under 220 characters.

## 4. Motion cues (`focus`, `zoom`, `mark`, `card`)
- Point at what the line talks about. Check anchor boxes and ids in `imageWithAnchors`. Do not zoom on anchors that cover most of the screen (large figures, kind "3d"); use `ring` or `none` for them.
- Do not move the camera on every line: neighbouring lines can share a focus, or use `[]`. Roughly 40 to 60 percent of lines with a focus is right. A step's first line usually points at whatever just appeared.
- Use `close` only for reading out small text, a formula or a number. Never zoom on kind "3d".
- Anchor ids are only valid inside their own step (they are renumbered for every step).

## 5. Chapters, opening and close
- A unit with `startsSection` true has a `chapter`: `{ "title": section title, "subtitle": one-line teaser (at most 40 characters), "sub": ..., "tts": ... }`, one or two sentences read over the chapter title card ("Chapter three: let's look at the data.").
- The first unit (`isFirstUnit`) has an `intro`: 3 to 5 lines read over the opening title card: a greeting, what this video explains, and what you will understand by the end. No hype.
- The last unit (`isLastUnit`) has an `outro`: 2 to 4 lines: thanks and a short wrap-up. Do not beg for likes or subscriptions.

## 6. Output format (a JSON file)
```json
{
  "unit": "u05", "lang": "en",
  "chapter": null,
  "intro": [],
  "steps": [
    { "slide": "s04-03", "step": 0,
      "lines": [
        { "sub": "...", "tts": "...", "focus": ["a4"], "zoom": "soft", "mark": "ring", "card": null }
      ] }
  ],
  "outro": []
}
```
- `steps` holds every step of the input, in order, with `slide` and `step` unchanged.
- `chapter`, `intro` and `outro` are `null` or `[]` when they do not apply.
- Lines in intro, outro and chapter need only `sub` and `tts`.
