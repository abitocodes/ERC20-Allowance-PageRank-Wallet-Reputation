#!/usr/bin/env python3
"""video/mix.py -- put the narration and the music under the rendered chunks and make the deliverables.

  python3 mix.py --lang ko --plan plan-ko.json --render RENDERDIR --audio AUDIODIR --music MUSICDIR \
                 --steps EXTRACT/ko/steps.json --out OUTDIR [--name NAME]

Writes OUTDIR/NAME.mp4 (1080p30 H.264 + AAC 192k, about -15 LUFS), NAME.srt (captions, timed to the
voice), NAME-chapters.txt (YouTube chapter list) and NAME-audio.wav.
Each line's start comes from the renderer's log (RENDERDIR/chunk-NN.json), so the voice lands on the
frame where its camera move and highlight begin. Music: one movement per chapter, looped with
crossfades, ducked under the voice (about -34 LUFS under speech, -27 in pauses, -24 under the cards).
"""
import argparse
import json
import os
import re
import subprocess

import numpy as np
import soundfile as sf
import pyloudnorm as pyln
from scipy.signal import resample_poly, lfilter

ap = argparse.ArgumentParser()
for k in ('lang', 'plan', 'render', 'audio', 'music', 'steps', 'out'):
    ap.add_argument('--' + k, required=True)
ap.add_argument('--name', default=None)
ap.add_argument('--target', type=float, default=-15.0)
A = ap.parse_args()
SR = 48000
plan = json.load(open(A.plan, encoding='utf-8'))
FPS = plan['fps']
name = A.name or ('thesis-explained-' + A.lang)
os.makedirs(A.out, exist_ok=True)
ex = json.load(open(A.steps, encoding='utf-8'))
sec_title = {s['id'][:3]: s['title'] for s in ex['sections']}

# ---------------------------------------------------------------- timeline from the render logs
chunks, t = [], 0.0
for i, s in enumerate(plan['slides']):
    log = json.load(open(os.path.join(A.render, 'chunk-%02d.json' % i)))
    chunks.append({'i': i, 'slide': s['id'], 't0': t, 'frames': log['frames'], 'lines': log['lines'], 'chapter': bool(s['chapter'])})
    t += log['frames'] / FPS
total = t
N = int(round(total * SR))
lines = {r['id']: r for r in json.load(open(os.path.join(A.audio, A.lang, 'lines.json'), encoding='utf-8'))}

voice = np.zeros(N, dtype=np.float32)
active = np.zeros(N, dtype=np.float32)
placed = []
for c in chunks:
    for L in c['lines']:
        r = lines.get(L['id'])
        if r is None:
            print('missing audio for', L['id']); continue
        w, sr = sf.read(os.path.join(A.audio, A.lang, r['file']), dtype='float32')
        if sr != SR:
            w = resample_poly(w, SR // 100 * 1, sr // 100 * 1).astype(np.float32) if sr % 100 == 0 else w
        st = c['t0'] + L['frame'] / FPS
        i0 = int(round(st * SR)); i1 = min(N, i0 + len(w))
        voice[i0:i1] += w[: i1 - i0]
        active[i0:i1] = 1.0
        placed.append({'id': L['id'], 'start': st, 'end': st + len(w) / SR, 'sub': r['sub'], 'chunk': c['i']})

meter = pyln.Meter(SR)
vl = meter.integrated_loudness(voice[active > 0]) if active.any() else -30
voice *= 10 ** ((-16.0 - vl) / 20)

# ---------------------------------------------------------------- music bed
mov = {}
for k in ('m1', 'm2', 'm3', 'm4'):
    x, sr = sf.read(os.path.join(A.music, k + '.wav'), dtype='float32')
    mov[k] = x.T
order = ['m1', 'm2', 'm3', 'm4', 'm2', 'm1', 'm3', 'm4', 'm1', 'm3', 'm2', 'm4']
bounds = [0.0] + [c['t0'] for c in chunks if c['chapter'] and c['i'] > 0] + [total]
bed = np.zeros((2, N), dtype=np.float32)
XF = 4.0
for k in range(len(bounds) - 1):
    m = mov[order[k % len(order)]]
    # each chapter's music starts at its boundary and rings XF seconds into the next chapter, where the two
    # crossfade (this one fades out over its last XF seconds while the next fades in over its first XF)
    a = bounds[k]; b = min(total, bounds[k + 1] + XF)
    seg = np.zeros((2, int((b - a) * SR) + 1), dtype=np.float32)
    L = m.shape[1]; hop = L - int(XF * SR)
    pos = 0
    while pos < seg.shape[1]:
        n = min(L, seg.shape[1] - pos)
        seg[:, pos:pos + n] += m[:, :n]
        pos += hop
    # crossfade windows at both ends of the chapter's segment
    xf = int(XF * SR)
    if k:
        seg[:, :xf] *= np.linspace(0, 1, xf)
    if k < len(bounds) - 2:
        seg[:, -xf:] *= np.linspace(1, 0, xf)
    i0 = int(a * SR); i1 = min(N, i0 + seg.shape[1])
    bed[:, i0:i1] += seg[:, : i1 - i0]

# ducking: 0 under the voice, 1 in pauses; smoothed (attack 0.25 s, release 0.9 s)
def smooth(x, up, down):
    a_up, a_dn = np.exp(-1 / (up * SR)), np.exp(-1 / (down * SR))
    y = np.empty_like(x); v = x[0]
    # vectorised enough: process in blocks of 10 ms with per-block coefficient
    blk = SR // 100
    out = np.empty(len(x) // blk + 1, dtype=np.float32)
    for j in range(len(out)):
        tgt = x[j * blk: (j + 1) * blk].max() if j * blk < len(x) else v
        a = a_up ** blk if tgt > v else a_dn ** blk
        v = a * v + (1 - a) * tgt
        out[j] = v
    return np.repeat(out, blk)[: len(x)]

speech_env = smooth(active, 0.25, 0.9)                      # 1 while speaking
gain_db = -7.0 - 7.0 * speech_env                            # -7 dB in pauses, -14 under speech
# cards: the intro (until the first slide line) and the outro (after the last step line) sit a little higher
first_step = min(p['start'] for p in placed if not p['id'].startswith(('intro', 'chapter')))
last_step = max(p['end'] for p in placed if not p['id'].startswith('outro'))
tt = np.arange(N) / SR
card = ((tt < first_step - 1.0) | (tt > last_step + 1.5)).astype(np.float32)
card = smooth(card, 1.0, 1.0)
gain_db = gain_db + 3.0 * card
g = 10 ** (gain_db / 20)
fade_in = np.clip(tt / 2.5, 0, 1); fade_out = np.clip((total - tt) / 3.0, 0, 1)
bed *= (g * fade_in * fade_out)[None, :]

mix = bed + voice[None, :]
lufs = meter.integrated_loudness(mix.T)
mix *= 10 ** ((A.target - lufs) / 20)
# soft limiter above -1.5 dBFS
lim = 10 ** (-1.5 / 20)
over = np.abs(mix) > lim * 0.9
mix[over] = np.sign(mix[over]) * (lim * 0.9 + (lim * 0.1) * np.tanh((np.abs(mix[over]) - lim * 0.9) / (lim * 0.1)))
wav_path = os.path.join(A.out, name + '-audio.wav')
sf.write(wav_path, mix.T, SR, subtype='PCM_24')
print(f'audio {total / 60:.2f} min, voice {vl:.1f} LUFS -> -16, mix {lufs:.1f} -> {A.target} LUFS, peak {20 * np.log10(np.abs(mix).max()):.1f} dBFS')

# ---------------------------------------------------------------- captions
def fmt(s):
    h = int(s // 3600); m = int(s % 3600 // 60); x = s % 60
    return '%02d:%02d:%06.3f' % (h, m, x)


WIDTH = 24 if A.lang == 'ko' else 42


def wrap(text):
    words, rows, cur = text.split(), [], ''
    for w in words:
        if cur and len(cur) + 1 + len(w) > WIDTH:
            rows.append(cur); cur = w
        else:
            cur = (cur + ' ' + w).strip()
    if cur:
        rows.append(cur)
    return rows


cues = []
for p in placed:
    rows = wrap(p['sub'])
    if len(rows) <= 2:
        cues.append((p['start'], p['end'], '\n'.join(rows)))
        continue
    groups = [rows[i:i + 2] for i in range(0, len(rows), 2)]
    total_chars = sum(len(' '.join(g)) for g in groups)
    t0 = p['start']
    for gi, gr in enumerate(groups):
        d = (p['end'] - p['start']) * len(' '.join(gr)) / total_chars
        cues.append((t0, t0 + d, '\n'.join(gr)))
        t0 += d
with open(os.path.join(A.out, name + '.srt'), 'w', encoding='utf-8') as f:
    for k, (a, b, txt) in enumerate(cues, 1):
        f.write(f'{k}\n{fmt(a).replace(".", ",")} --> {fmt(b - 0.02).replace(".", ",")}\n{txt}\n\n')

# ---------------------------------------------------------------- YouTube chapters
def yt(s):
    s = int(s)
    return '%d:%02d:%02d' % (s // 3600, s % 3600 // 60, s % 60) if s >= 3600 else '%d:%02d' % (s // 60, s % 60)


chap = [('0:00', '인트로' if A.lang == 'ko' else 'Intro')]
for c in chunks:
    if c['chapter']:
        sec = c['slide'][:3]
        start = c['t0'] if c['i'] else min(p['start'] for p in placed if p['id'].startswith('chapter/'))
        chap.append((yt(start), '%s %s' % (sec[1:], sec_title.get(sec, sec))))
outro_t = min((p['start'] for p in placed if p['id'].startswith('outro')), default=None)
if outro_t:
    chap.append((yt(outro_t - 2), '마무리 인사' if A.lang == 'ko' else 'Thanks'))
with open(os.path.join(A.out, name + '-chapters.txt'), 'w', encoding='utf-8') as f:
    for a, b in chap:
        f.write(f'{a} {b}\n')

# ---------------------------------------------------------------- the video file
lst = os.path.join(A.out, name + '-chunks.txt')
with open(lst, 'w') as f:
    for c in chunks:
        f.write("file '%s'\n" % os.path.join(A.render, 'chunk-%02d.mp4' % c['i']))
out = os.path.join(A.out, name + '.mp4')
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-i', wav_path,
                '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
                '-metadata', 'title=' + ' '.join(plan['meta']['intro']['title']), '-movflags', '+faststart', '-shortest', out], check=True)
probe = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration,size', '-of', 'json', out], capture_output=True, text=True).stdout
fmt_ = json.loads(probe)['format']
print(f"{out}: {float(fmt_['duration']) / 60:.2f} min, {int(fmt_['size']) / 1e6:.0f} MB; {len(cues)} captions; {len(chap)} chapters")
