#!/usr/bin/env python3
"""video/recheck.py -- second listening pass over the lines tts.py flagged.

  python3 recheck.py --lang ko --model MODELDIR --out AUDIODIR [--asr medium] [--threshold 0.2]
                     [--retries 4] [--steps 8] [--whisper-dir DIR]

tts.py hears every line with a small Whisper model, which mishears some Korean terms (람다, 디) and
writes acronyms in Latin letters. Here each line still above --threshold is heard again with a larger
model; if that hearing is fine the line is kept. Otherwise it is spoken again up to --retries times
(more denoising steps) and the take that the larger model hears best is kept. lines.json is updated.
"""
import argparse
import json
import os
import re
import sys

import numpy as np
import soundfile as sf

ap = argparse.ArgumentParser()
ap.add_argument('--lang', required=True)
ap.add_argument('--model', required=True)
ap.add_argument('--out', required=True)
ap.add_argument('--asr', default='medium')
ap.add_argument('--threshold', type=float, default=0.2)
ap.add_argument('--retries', type=int, default=4)
ap.add_argument('--steps', type=int, default=8)
ap.add_argument('--voice', default='F3')
ap.add_argument('--speed', type=float, default=None)
ap.add_argument('--whisper-dir', default=None)
A = ap.parse_args()
speed = A.speed or (1.22 if A.lang == 'ko' else 1.15)
sys.path.insert(0, os.path.dirname(os.path.abspath(A.model)))
sys.path.insert(0, A.model)
from helper import load_text_to_speech, load_voice_style  # noqa: E402
from faster_whisper import WhisperModel  # noqa: E402

outdir = os.path.join(A.out, A.lang)
index_path = os.path.join(outdir, 'lines.json')
recs = json.load(open(index_path, encoding='utf-8'))
todo = [r for r in recs if r['cer'] > A.threshold]
print(f'{len(todo)} lines above {A.threshold}', flush=True)
if not todo:
    sys.exit(0)
tts = load_text_to_speech(os.path.join(A.model, 'onnx'), False)
style = load_voice_style([os.path.join(A.model, 'voice_styles', A.voice + '.json')])
SR = tts.sample_rate
asr = WhisperModel(A.asr, device='cpu', compute_type='int8', download_root=A.whisper_dir)


def norm(s):
    s = s.lower()
    return ''.join(re.findall(r'[가-힣]' if A.lang == 'ko' else r'[a-z]', s))


def cer(ref, hyp):
    a, b = norm(ref), norm(hyp)
    if not a:
        return 0.0
    prev = list(range(len(b) + 1))
    for i in range(1, len(a) + 1):
        cur = [i] + [0] * len(b)
        for j in range(1, len(b) + 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] != b[j - 1]))
        prev = cur
    return prev[-1] / len(a)


def hear(w):
    x = np.interp(np.arange(0, len(w), SR / 16000.0), np.arange(len(w)), w).astype(np.float32)
    segs, _ = asr.transcribe(x, language=A.lang, beam_size=5, condition_on_previous_text=False)
    return ' '.join(s.text.strip() for s in segs)


def trim(w, keep=0.06):
    thr = 10 ** (-48 / 20) * max(1e-6, np.abs(w).max())
    idx = np.where(np.abs(w) > thr)[0]
    if not len(idx):
        return w
    k = int(keep * SR)
    return w[max(0, idx[0] - k): min(len(w), idx[-1] + k)]


def score(r, heard):
    return min(cer(r['tts'], heard), cer(r['sub'] or r['tts'], heard))


kept = redone = still = 0
for n, r in enumerate(todo):
    path = os.path.join(outdir, r['file'])
    w, _ = sf.read(path, dtype='float32')
    heard = hear(w)
    best = (score(r, heard), w, heard, False)
    tries = 0
    while best[0] > A.threshold and tries < A.retries:
        tries += 1
        wav, dur = tts(r['tts'], A.lang, style, A.steps, speed)
        w2 = trim(np.asarray(wav[0, : int(SR * dur[0].item())], dtype=np.float32))
        h2 = hear(w2)
        e2 = score(r, h2)
        if e2 < best[0]:
            best = (e2, w2, h2, True)
    e, w, heard, new = best
    if new:
        sf.write(path, w, SR, subtype='FLOAT')
        r['dur'] = round(len(w) / SR, 3)
        redone += 1
    else:
        kept += 1
    r['cer'] = round(e, 3); r['heard'] = heard; r['asr'] = A.asr
    if e > A.threshold:
        still += 1
    if (n + 1) % 10 == 0:
        print(f'{n + 1}/{len(todo)} checked; re-spoken {redone}, still above {still}', flush=True)
        json.dump(recs, open(index_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump(recs, open(index_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print(f'done: {kept} fine on a second hearing, {redone} re-spoken, {still} still above {A.threshold}')
for r in todo:
    if r['cer'] > A.threshold:
        print(f"  {r['id']} cer {r['cer']}: {r['tts']}  || heard: {r['heard']}")
