#!/usr/bin/env python3
"""video/music.py -- the background music, written from scratch in code (no samples, no loops from
anywhere else), so the video carries no third-party music rights.

Four calm movements in different keys (soft pads, a sparse electric-piano arpeggio, a sine bass, a
little air and a few bells), each about 3.5 minutes, at 70 BPM, with a convolution reverb. mix.py
lays them under the chapters and ducks them under the voice.

  python3 music.py OUTDIR            -> OUTDIR/m1.wav ... m4.wav  (48 kHz stereo float, about -20 LUFS)
"""
import os
import sys

import numpy as np
from scipy.signal import oaconvolve, butter, sosfilt

SR = 48000
BPM = 70.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT


def midi_hz(n):
    return 440.0 * 2 ** ((n - 69) / 12.0)


# ---------------------------------------------------------------- voices
def pad_note(f, dur, rng, bright=0.5):
    """detuned additive saw voice with slow attack/release"""
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for det in (-0.0045, 0.0, 0.0052):
        ph = rng.uniform(0, 2 * np.pi)
        ff = f * (1 + det) * (1 + 0.0012 * np.sin(2 * np.pi * rng.uniform(0.08, 0.2) * t + ph))
        phase = 2 * np.pi * np.cumsum(ff) / SR
        for h in range(1, 9):
            if f * h > 5000:
                break
            out += (bright ** (h - 1)) / h * np.sin(h * phase + ph * h)
    att, rel = min(1.6, dur * 0.4), min(2.0, dur * 0.45)
    env = np.ones(n)
    a = int(att * SR); r = int(rel * SR)
    env[:a] = np.sin(np.linspace(0, np.pi / 2, a)) ** 2
    env[-r:] *= np.cos(np.linspace(0, np.pi / 2, r)) ** 2
    return out * env / 3.0


def keys_note(f, dur, vel, rng):
    """soft electric piano: sine + a little FM bell, exponential decay"""
    n = int(dur * SR)
    t = np.arange(n) / SR
    idx = 1.6 * np.exp(-t / 0.35)
    mod = np.sin(2 * np.pi * f * 2.0 * t)
    car = np.sin(2 * np.pi * f * t + idx * mod)
    car += 0.18 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t / 0.5)
    env = np.exp(-t / 1.1) * (1 - np.exp(-t / 0.004))
    return vel * car * env


def bell(f, dur, vel):
    n = int(dur * SR)
    t = np.arange(n) / SR
    env = np.exp(-t / 1.8) * (1 - np.exp(-t / 0.002))
    s = np.sin(2 * np.pi * f * t + 2.2 * np.exp(-t / 0.25) * np.sin(2 * np.pi * f * 3.5 * t))
    s += 0.3 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / 0.6)
    return vel * s * env


def bass_note(f, dur, vel):
    n = int(dur * SR)
    t = np.arange(n) / SR
    env = (1 - np.exp(-t / 0.03)) * np.exp(-t / 2.2)
    rel = int(min(0.3, dur * 0.3) * SR)
    env[-rel:] *= np.linspace(1, 0, rel)
    return vel * (np.sin(2 * np.pi * f * t) + 0.12 * np.sin(4 * np.pi * f * t)) * env


def add(buf, x, start, pan):
    i = int(round(start * SR))
    if i < 0:
        x, i = x[-i:], 0
    if i >= buf.shape[1] or not len(x):
        return
    j = min(buf.shape[1], i + len(x))
    l = np.cos((pan + 1) * np.pi / 4)
    r = np.sin((pan + 1) * np.pi / 4)
    buf[0, i:j] += l * x[: j - i]
    buf[1, i:j] += r * x[: j - i]


def reverb_ir(seconds, rng):
    n = int(seconds * SR)
    t = np.arange(n) / SR
    ir = np.zeros((2, n))
    for c in range(2):
        noise = rng.standard_normal(n)
        # darker as it decays
        sos = butter(1, 3500, 'low', fs=SR, output='sos')
        dark = sosfilt(sos, noise)
        mix = np.exp(-t / 0.45)
        ir[c] = (mix * noise + (1 - mix) * dark) * np.exp(-t * 6.9 / seconds)
        ir[c, : int(0.012 * SR)] *= np.linspace(0, 1, int(0.012 * SR))
    ir /= np.sqrt((ir ** 2).sum(axis=1, keepdims=True))
    return ir


# ---------------------------------------------------------------- movements
# chords as MIDI notes (pad voicing); bass root; scale for the arpeggio and bells
MOVEMENTS = {
    'm1': dict(seed=11, prog=[([50, 57, 61, 64, 69], 38), ([47, 54, 57, 62, 66], 35), ([43, 50, 54, 59, 62], 31), ([45, 52, 57, 59, 64], 33)],
               scale=[62, 64, 66, 69, 71, 74, 76, 78, 81], bright=0.52),     # D major: Dmaj9 Bm7 Gmaj7 A6sus
    'm2': dict(seed=23, prog=[([53, 60, 64, 67, 71], 41), ([45, 52, 55, 60, 64], 33), ([50, 57, 60, 64, 65], 38), ([48, 55, 60, 62, 67], 36)],
               scale=[60, 62, 64, 67, 69, 72, 74, 76, 79], bright=0.5),      # F lydian-ish: Fmaj7#11 Am7 Dm9 Cadd9
    'm3': dict(seed=37, prog=[([45, 52, 55, 60, 64], 33), ([41, 48, 52, 57, 64], 29), ([48, 55, 57, 64, 67], 36), ([43, 50, 55, 59, 62], 31)],
               scale=[57, 60, 62, 64, 67, 69, 72, 74, 76], bright=0.48),     # A minor: Am9 Fmaj7 C6 G
    'm4': dict(seed=53, prog=[([51, 58, 62, 65, 70], 39), ([48, 55, 58, 63, 67], 36), ([44, 51, 55, 60, 63], 32), ([46, 53, 58, 60, 65], 34)],
               scale=[63, 65, 67, 70, 72, 75, 77, 79, 82], bright=0.5),      # Eb major: Ebmaj7 Cm9 Abmaj7 Bb6
}
BARS = 64          # 64 bars at 70 BPM = 3 min 39 s


def movement(name):
    M = MOVEMENTS[name]
    rng = np.random.default_rng(M['seed'])
    total = BARS * BAR + 6.0
    buf = np.zeros((2, int(total * SR)))
    pads = np.zeros_like(buf)
    for bar in range(BARS):
        t0 = bar * BAR
        chord, root = M['prog'][bar % 4]
        section = bar // 16                     # four sections: thin, fuller, fullest, thin again
        # pad: each chord rings a little past its bar (overlap = smooth changes)
        for k, n in enumerate(chord):
            pan = (k / (len(chord) - 1) - 0.5) * 0.9
            add(pads, 0.050 * pad_note(midi_hz(n), BAR + 1.8, rng, M['bright']), t0 - 0.3, pan)
        # bass on beats 1 and 3 (not in the first and last four bars)
        if 4 <= bar < BARS - 4:
            add(buf, 0.11 * bass_note(midi_hz(root - 12 if root > 40 else root), 2 * BEAT, 1.0), t0, 0.0)
            add(buf, 0.07 * bass_note(midi_hz(root - 12 if root > 40 else root), 2 * BEAT, 0.9), t0 + 2 * BEAT, 0.0)
        # arpeggio on an 8th grid; density by section
        dens = [0.18, 0.38, 0.5, 0.25][section]
        tones = sorted(set([n + 12 for n in chord[1:]] + [s for s in M['scale'] if s % 12 in {c % 12 for c in chord}]))
        last = None
        for e in range(8):
            if rng.random() < dens or (e == 0 and section in (1, 2)):
                choices = [x for x in tones if x != last]
                n = int(rng.choice(choices)); last = n
                vel = rng.uniform(0.45, 0.85) * (1.0 if e % 2 == 0 else 0.75)
                add(buf, 0.06 * keys_note(midi_hz(n), 2.6, vel, rng), t0 + e * BEAT / 2 + rng.uniform(-0.012, 0.012), rng.uniform(-0.45, 0.45))
        # bells now and then
        if bar % 4 == 3 and rng.random() < 0.6:
            n = int(rng.choice(M['scale'][4:])) + 12
            add(buf, 0.03 * bell(midi_hz(n), 4.0, rng.uniform(0.5, 0.9)), t0 + rng.choice([1.5, 2.5, 3.0]) * BEAT, rng.uniform(-0.7, 0.7))
    # air: soft filtered noise breathing slowly
    n = buf.shape[1]
    t = np.arange(n) / SR
    noise = rng.standard_normal((2, n))
    sos = butter(2, [300, 2500], 'band', fs=SR, output='sos')
    air = sosfilt(sos, noise) * (0.0028 * (0.75 + 0.25 * np.sin(2 * np.pi * t / 23.0)))
    dry = buf + pads + air
    ir = reverb_ir(3.4, rng)
    wet = np.stack([oaconvolve(dry[c], ir[c])[:n] for c in range(2)])
    out = 0.72 * dry + 0.55 * wet
    sos = butter(2, 9000, 'low', fs=SR, output='sos')
    out = sosfilt(sos, out)
    # loop-friendly ends: 2 s fade in, 4 s fade out (mix.py crossfades movements and repeats)
    fi, fo = int(2 * SR), int(4 * SR)
    out[:, :fi] *= np.linspace(0, 1, fi)
    out[:, -fo:] *= np.linspace(1, 0, fo)
    return out.astype(np.float32)


if __name__ == '__main__':
    import soundfile as sf
    import pyloudnorm as pyln
    outdir = sys.argv[1]
    os.makedirs(outdir, exist_ok=True)
    meter = pyln.Meter(SR)
    for name in MOVEMENTS:
        x = movement(name)
        lufs = meter.integrated_loudness(x.T)
        x = (x * 10 ** ((-20.0 - lufs) / 20)).astype(np.float32)
        peak = float(np.abs(x).max())
        sf.write(os.path.join(outdir, name + '.wav'), x.T, SR, subtype='FLOAT')
        print(f'{name}: {x.shape[1] / SR:.1f} s, {lufs:.1f} LUFS -> -20 LUFS, peak {20 * np.log10(peak):.1f} dBFS', flush=True)
