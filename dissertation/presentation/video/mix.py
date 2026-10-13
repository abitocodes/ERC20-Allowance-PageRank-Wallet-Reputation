#!/usr/bin/env python3
"""video/mix.py -- put the narration and the music under the rendered chunks and make the deliverables.

  python3 mix.py --lang ko --plan plan-ko.json --render RENDERDIR --audio AUDIODIR --music MUSICDIR \
                 --steps EXTRACT/ko/steps.json --out OUTDIR [--name NAME] [--target -15]

Writes OUTDIR/NAME.mp4 (1080p30 H.264 + AAC 192k, normalised to --target LUFS, true peak -1.5 dB),
NAME.srt (captions, timed to the voice), NAME-chapters.txt (YouTube chapter list) and NAME-audio.wav.
Each line's start comes from the renderer's log (RENDERDIR/chunk-NN.json), so the voice lands on the
frame where its camera move and highlight begin. Music: one movement per chapter, looped, crossfading
over 4 s at each chapter change, ducked under the voice (about -34 LUFS under speech, -27 in pauses,
-24 under the opening and closing cards). The sound is built 30 s at a time, so a two-hour video fits
in memory; the loudness is then set by ffmpeg's two-pass loudnorm (linear gain).
"""
import argparse
import json
import os
import subprocess

import numpy as np
import soundfile as sf
import pyloudnorm as pyln
from scipy.signal import resample_poly

ap = argparse.ArgumentParser()
for k in ('lang', 'plan', 'render', 'audio', 'music', 'steps', 'out'):
    ap.add_argument('--' + k, required=True)
ap.add_argument('--name', default=None)
ap.add_argument('--target', type=float, default=-15.0)
A = ap.parse_args()
SR = 48000
BLK = SR // 100                        # 10 ms: resolution of the ducking envelope
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
NB = N // BLK + 2
lines = {r['id']: r for r in json.load(open(os.path.join(A.audio, A.lang, 'lines.json'), encoding='utf-8'))}

placed = []
for c in chunks:
    for L in c['lines']:
        r = lines.get(L['id'])
        if r is None:
            print('missing audio for', L['id'])
            continue
        st = c['t0'] + L['frame'] / FPS
        info = sf.info(os.path.join(A.audio, A.lang, r['file']))
        placed.append({'id': L['id'], 'start': st, 'end': st + info.frames / info.samplerate, 'sub': r['sub'], 'file': r['file']})
placed.sort(key=lambda p: p['start'])

# voice loudness: duration-weighted energy of the per-line loudness (lines under 0.5 s skipped)
num = den = 0.0
for p in placed:
    w, sr = sf.read(os.path.join(A.audio, A.lang, p['file']), dtype='float32')
    if len(w) < sr // 2:
        continue
    l = pyln.Meter(sr).integrated_loudness(w)
    if np.isfinite(l):
        d = len(w) / sr
        num += d * 10 ** (l / 10); den += d
voice_lufs = 10 * np.log10(num / den)
voice_gain = 10 ** ((-16.0 - voice_lufs) / 20)

# ---------------------------------------------------------------- ducking envelope (100 Hz)
active = np.zeros(NB, dtype=np.float32)
for p in placed:
    active[int(p['start'] * 100): int(np.ceil(p['end'] * 100)) + 1] = 1.0


def smooth(x, up, down):
    a_up, a_dn = np.exp(-1 / (up * 100)), np.exp(-1 / (down * 100))
    y = np.empty_like(x); v = float(x[0])
    for j in range(len(x)):
        tgt = float(x[j])
        a = a_up if tgt > v else a_dn
        v = a * v + (1 - a) * tgt
        y[j] = v
    return y


speech = smooth(active, 0.25, 0.9)                     # 1 while speaking
first_step = min(p['start'] for p in placed if not p['id'].startswith(('intro', 'chapter')))
last_step = max(p['end'] for p in placed if not p['id'].startswith('outro'))
tt = np.arange(NB, dtype=np.float32) / 100.0
card = smooth(((tt < first_step - 1.0) | (tt > last_step + 1.5)).astype(np.float32), 1.0, 1.0)
gain_db = -7.0 - 7.0 * speech + 3.0 * card              # -7 dB in pauses, -14 under speech, +3 under the cards
env = ((10 ** (gain_db / 20)) * np.clip(tt / 2.5, 0, 1) * np.clip((total - tt) / 3.0, 0, 1)).astype(np.float32)

# ---------------------------------------------------------------- music bed, one movement per chapter
mov = {}
for k in ('m1', 'm2', 'm3', 'm4'):
    x, sr = sf.read(os.path.join(A.music, k + '.wav'), dtype='float32')
    mov[k] = np.ascontiguousarray(x.T)
order = ['m1', 'm2', 'm3', 'm4', 'm2', 'm1', 'm3', 'm4', 'm1', 'm3', 'm2', 'm4']
bounds = [0.0] + [c['t0'] for c in chunks if c['chapter'] and c['i'] > 0] + [total]
XF = int(4.0 * SR)
segs = []
for k in range(len(bounds) - 1):
    # each chapter's music starts at its boundary and rings XF into the next chapter, where the two crossfade
    a = int(bounds[k] * SR); b = min(N, int(bounds[k + 1] * SR) + XF)
    segs.append({'a': a, 'b': b, 'm': mov[order[k % len(order)]], 'fin': k > 0, 'fout': k < len(bounds) - 2})


def music(i0, i1):
    out = np.zeros((2, i1 - i0), dtype=np.float32)
    for s in segs:
        lo, hi = max(i0, s['a']), min(i1, s['b'])
        if lo >= hi:
            continue
        m = s['m']; L = m.shape[1]; hop = L - XF       # loops overlap by XF (the movement fades in and out)
        r0, r1 = lo - s['a'], hi - s['a']
        part = np.zeros((2, r1 - r0), dtype=np.float32)
        for j in range(max(0, (r0 - L) // hop), r1 // hop + 1):
            c0 = j * hop
            x0, x1 = max(r0, c0), min(r1, c0 + L)
            if x0 < x1:
                part[:, x0 - r0: x1 - r0] += m[:, x0 - c0: x1 - c0]
        pos = np.arange(r0, r1, dtype=np.float32)
        if s['fin']:
            part *= np.clip(pos / XF, 0, 1)[None, :]
        if s['fout']:
            part *= np.clip((s['b'] - s['a'] - pos) / XF, 0, 1)[None, :]
        out[:, lo - i0: hi - i0] += part
    return out


# ---------------------------------------------------------------- build the sound 30 s at a time
raw_path = os.path.join(A.out, name + '-premix.wav')
STEP = 30 * SR
nxt = 0                                                    # first placed line that may still sound
with sf.SoundFile(raw_path, 'w', samplerate=SR, channels=2, subtype='FLOAT') as f:
    for i0 in range(0, N, STEP):
        i1 = min(N, i0 + STEP)
        block = music(i0, i1)
        e = np.repeat(env[i0 // BLK: i1 // BLK + 2], BLK)
        off = i0 - (i0 // BLK) * BLK
        block *= e[off: off + (i1 - i0)][None, :]
        v = np.zeros(i1 - i0, dtype=np.float32)
        while nxt < len(placed) and placed[nxt]['end'] * SR < i0:
            nxt += 1
        for p in placed[nxt:]:
            s0 = int(round(p['start'] * SR))
            if s0 >= i1:
                break
            x, sr = sf.read(os.path.join(A.audio, A.lang, p['file']), dtype='float32')
            w = resample_poly(x, SR // 100, sr // 100).astype(np.float32) if sr != SR else x
            lo, hi = max(i0, s0), min(i1, s0 + len(w))
            if lo < hi:
                v[lo - i0: hi - i0] += w[lo - s0: hi - s0]
        block += voice_gain * v[None, :]
        f.write(block.T)

# ---------------------------------------------------------------- loudness: ffmpeg loudnorm, two passes, linear gain
m = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', raw_path, '-af',
                    f'loudnorm=I={A.target}:TP=-1.5:LRA=20:print_format=json', '-f', 'null', '-'],
                   capture_output=True, text=True).stderr
meas = json.loads(m[m.rindex('{'): m.rindex('}') + 1])
ln2 = (f"loudnorm=I={A.target}:TP=-1.5:LRA=20:measured_I={meas['input_i']}:measured_TP={meas['input_tp']}:"
       f"measured_LRA={meas['input_lra']}:measured_thresh={meas['input_thresh']}:offset={meas['target_offset']}:linear=true")
wav_path = os.path.join(A.out, name + '-audio.wav')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', raw_path, '-af', ln2, '-ar', str(SR), '-c:a', 'pcm_s24le', wav_path], check=True)
os.remove(raw_path)
print(f"audio {total / 60:.2f} min, voice {voice_lufs:.1f} LUFS -> -16, premix {meas['input_i']} LUFS "
      f"(true peak {meas['input_tp']}) -> {A.target} LUFS")

# ---------------------------------------------------------------- captions
def fmt(s):
    h = int(s // 3600); m_ = int(s % 3600 // 60); x = s % 60
    return '%02d:%02d:%06.3f' % (h, m_, x)


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
    for gr in groups:
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
title = plan['meta']['intro']['title']
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-i', wav_path,
                '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
                '-metadata', 'title=' + (' '.join(title) if isinstance(title, list) else title), '-movflags', '+faststart',
                '-shortest', out], check=True)
probe = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration,size', '-of', 'json', out], capture_output=True, text=True).stdout
fmt_ = json.loads(probe)['format']
print(f"{out}: {float(fmt_['duration']) / 60:.2f} min, {int(fmt_['size']) / 1e6:.0f} MB; {len(cues)} captions; {len(chap)} chapters")
