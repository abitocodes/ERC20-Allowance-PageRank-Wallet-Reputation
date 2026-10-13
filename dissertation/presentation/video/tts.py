#!/usr/bin/env python3
"""video/tts.py -- speak every narration line with Supertonic 2 and check it by ear (Whisper).

  python3 tts.py --lang ko --scripts SCRIPTDIR --model MODELDIR --out AUDIODIR [--voice F3] [--speed 1.15]
                 [--asr small] [--retries 3] [--only ID,ID]

SCRIPTDIR/<lang>/u01.json ... (the narration scripts). Each line becomes AUDIODIR/<lang>/<n>.wav
(44.1 kHz mono float; silence trimmed to 60 ms at each end). The line is transcribed back with
faster-whisper and compared with what it should say (letters only, digits and symbols dropped on both
sides); when the character error rate is above 0.2 the line is spoken again with a new noise sample,
up to --retries times, and the best take is kept. AUDIODIR/<lang>/lines.json lists every line with its
id, text, file, duration and error rate; lines still above 0.2 are listed at the end for review.
Model: https://huggingface.co/Supertone/supertonic-2 (OpenRAIL-M); its helper.py from
https://github.com/supertone-inc/supertonic (MIT) must sit in MODELDIR/.. or on PYTHONPATH.
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys
import time

import numpy as np
import soundfile as sf

ap = argparse.ArgumentParser()
ap.add_argument('--lang', required=True)
ap.add_argument('--scripts', required=True)
ap.add_argument('--model', required=True, help='folder with onnx/ and voice_styles/')
ap.add_argument('--out', required=True)
ap.add_argument('--voice', default='F3')
ap.add_argument('--speed', type=float, default=None)
ap.add_argument('--steps', type=int, default=8)
ap.add_argument('--asr', default='small')
ap.add_argument('--retries', type=int, default=2)
ap.add_argument('--only', default=None)
ap.add_argument('--whisper-dir', default=None)
A = ap.parse_args()
speed = A.speed or (1.22 if A.lang == 'ko' else 1.15)
sys.path.insert(0, os.path.dirname(os.path.abspath(A.model)))
sys.path.insert(0, A.model)
from helper import load_text_to_speech, load_voice_style  # noqa: E402

# ---------------------------------------------------------------- lines in video order
units = sorted(glob.glob(os.path.join(A.scripts, A.lang, 'u*.json')))
lines = []
for u in units:
    sc = json.load(open(u, encoding='utf-8'))
    for i, ln in enumerate(sc.get('intro') or []):
        lines.append(('intro/%d' % i, ln))
    if sc.get('chapter'):
        sec = None
        for st in sc['steps']:
            sec = st['slide'][:3]
            break
        lines.append(('chapter/%s' % sec, sc['chapter']))
    for st in sc['steps']:
        for i, ln in enumerate(st['lines']):
            lines.append(('%s/%d/%d' % (st['slide'], st['step'], i), ln))
    for i, ln in enumerate(sc.get('outro') or []):
        lines.append(('outro/%d' % i, ln))
only = set(A.only.split(',')) if A.only else None
outdir = os.path.join(A.out, A.lang)
os.makedirs(outdir, exist_ok=True)
index_path = os.path.join(outdir, 'lines.json')
index = {r['id']: r for r in json.load(open(index_path, encoding='utf-8'))} if os.path.exists(index_path) else {}

tts = load_text_to_speech(os.path.join(A.model, 'onnx'), False)
style = load_voice_style([os.path.join(A.model, 'voice_styles', A.voice + '.json')])
SR = tts.sample_rate

from faster_whisper import WhisperModel  # noqa: E402
asr = WhisperModel(A.asr, device='cpu', compute_type='int8', download_root=A.whisper_dir)


def norm(s):
    s = s.lower()
    if A.lang == 'ko':
        return ''.join(re.findall(r'[가-힣]', s))
    return ''.join(re.findall(r'[a-z]', s))


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


def trim(w, keep=0.06):
    thr = 10 ** (-48 / 20) * max(1e-6, np.abs(w).max())
    idx = np.where(np.abs(w) > thr)[0]
    if not len(idx):
        return w
    k = int(keep * SR)
    return w[max(0, idx[0] - k): min(len(w), idx[-1] + k)]


def speak(text):
    wav, dur = tts(text, A.lang, style, A.steps, speed)
    w = wav[0, : int(SR * dur[0].item())] if wav.ndim == 2 else wav
    return trim(np.asarray(w, dtype=np.float32))


def hear(w):
    x = np.interp(np.arange(0, len(w), SR / 16000.0), np.arange(len(w)), w).astype(np.float32)
    segs, _ = asr.transcribe(x, language=A.lang, beam_size=5, vad_filter=False, condition_on_previous_text=False)
    return ' '.join(s.text.strip() for s in segs)


t0 = time.time()
done = 0
for n, (lid, ln) in enumerate(lines):
    if only and lid not in only:
        continue
    text = ln['tts'].strip()
    fname = lid.replace('/', '_') + '.wav'
    rec = index.get(lid)
    if rec and rec.get('tts') == text and os.path.exists(os.path.join(outdir, rec['file'])) and not only:
        continue
    best = None
    for attempt in range(1 + A.retries):
        w = speak(text)
        heard = hear(w)
        # compare with the subtitle when it has digits (Whisper writes numbers as digits), else with tts
        e = min(cer(text, heard), cer(ln.get('sub', text), heard))
        if best is None or e < best[0]:
            best = (e, w, heard)
        if e <= 0.2:
            break
    e, w, heard = best
    sf.write(os.path.join(outdir, fname), w, SR, subtype='FLOAT')
    index[lid] = {'id': lid, 'n': n, 'file': fname, 'tts': text, 'sub': ln.get('sub', ''), 'dur': round(len(w) / SR, 3),
                  'cer': round(e, 3), 'heard': heard}
    done += 1
    if done % 25 == 0:
        el = time.time() - t0
        print(f'{done} lines, {el / 60:.1f} min, last {lid} cer {e:.2f}', flush=True)
        json.dump(sorted(index.values(), key=lambda r: r['n']), open(index_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)

order = {lid: k for k, (lid, _) in enumerate(lines)}
recs = [r for r in index.values() if r['id'] in order]
for r in recs:
    r['n'] = order[r['id']]
recs.sort(key=lambda r: r['n'])
json.dump(recs, open(index_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
total = sum(r['dur'] for r in recs)
bad = [r for r in recs if r['cer'] > 0.2]
print(f'{len(recs)} lines, {total / 60:.1f} min of speech, {done} synthesized now in {(time.time() - t0) / 60:.1f} min')
print(f'lines with error rate > 0.2: {len(bad)}')
for r in bad:
    print(f"  {r['id']} cer {r['cer']}: {r['tts']}  || heard: {r['heard']}")
