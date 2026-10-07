#!/usr/bin/env python3
"""Synthesize audiobook chapters from the scripts with a Korean AI voice.

usage:
  synthesize.py --backend google [--voice NAME] [--rate 1.0] script/01-*.md ...
  synthesize.py --backend google --list-voices

Each script becomes audio/<same name>.mp3. Headings and paragraphs are
synthesized one at a time (cached in .cache/, so an interrupted run resumes)
and joined with short silences: longer around chapter and section titles.

Backends
  google  Google Cloud Text-to-Speech. Reads the API key from the environment
          variable GOOGLE_TTS_API_KEY. Default voice: the first Korean
          Chirp3-HD voice, else Neural2, else WaveNet.
  melo    MeloTTS Korean (open model, runs on the CPU). Needs the melotts
          package and its model files from Hugging Face.
"""
import argparse
import base64
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from normalize import segments  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache"
RATE_HZ = 24000
PAUSE = {"before_h1": 0.4, "after_h1": 1.6, "before_h2": 1.2, "after_h2": 0.8,
         "before_h3": 0.9, "after_h3": 0.6, "before_h4": 0.8, "after_h4": 0.5, "p": 0.55}


def sentences(text, limit):
    """Split text into chunks of whole sentences, each under `limit` bytes."""
    parts = re.split(r"(?<=[.?!])\s+", text)
    chunk = ""
    for s in parts:
        cand = (chunk + " " + s).strip()
        if len(cand.encode("utf-8")) > limit and chunk:
            yield chunk
            chunk = s
        else:
            chunk = cand
    if chunk:
        yield chunk


class Google:
    URL = "https://texttospeech.googleapis.com/v1"

    def __init__(self, voice=None, rate=1.0):
        import requests
        self.requests = requests
        self.key = os.environ.get("GOOGLE_TTS_API_KEY")
        if not self.key:
            sys.exit("GOOGLE_TTS_API_KEY is not set")
        self.voice = voice or self.default_voice()
        self.rate = rate
        self.limit = 4500

    def voices(self):
        r = self.requests.get(f"{self.URL}/voices", params={"languageCode": "ko-KR", "key": self.key}, timeout=60)
        r.raise_for_status()
        return [v["name"] for v in r.json().get("voices", [])]

    def default_voice(self):
        names = self.voices()
        for kind in ("Chirp3-HD", "Neural2", "Wavenet"):
            for n in sorted(names):
                if kind in n:
                    return n
        return names[0]

    def tag(self):
        return f"google:{self.voice}:{self.rate}"

    def pcm(self, text):
        body = {"input": {"text": text},
                "voice": {"languageCode": "ko-KR", "name": self.voice},
                "audioConfig": {"audioEncoding": "LINEAR16", "sampleRateHertz": RATE_HZ}}
        if self.rate != 1.0:
            body["audioConfig"]["speakingRate"] = self.rate
        for attempt in range(5):
            r = self.requests.post(f"{self.URL}/text:synthesize", params={"key": self.key}, json=body, timeout=120)
            if r.status_code == 200:
                break
            if r.status_code in (429, 500, 503) and attempt < 4:
                import time
                time.sleep(2 ** (attempt + 1))
                continue
            sys.exit(f"Google TTS error {r.status_code}: {r.text[:300]}")
        data = base64.b64decode(r.json()["audioContent"])
        with wave.open(io.BytesIO(data)) as w:
            assert w.getframerate() == RATE_HZ and w.getsampwidth() == 2 and w.getnchannels() == 1
            return w.readframes(w.getnframes())


class Melo:
    def __init__(self, voice=None, rate=1.0):
        from melo.api import TTS
        import numpy as np
        self.np = np
        self.model = TTS(language="KR", device="cpu")
        self.speaker = self.model.hps.data.spk2id["KR"]
        self.sr = self.model.hps.data.sampling_rate
        self.rate = rate
        self.limit = 600

    def tag(self):
        return f"melo:KR:{self.rate}"

    def pcm(self, text):
        audio = self.model.tts_to_file(text, self.speaker, None, speed=self.rate, quiet=True)
        audio = self.np.asarray(audio, dtype="float32")
        if self.sr != RATE_HZ:
            n = int(len(audio) * RATE_HZ / self.sr)
            audio = self.np.interp(self.np.linspace(0, len(audio) - 1, n), self.np.arange(len(audio)), audio)
        return (self.np.clip(audio, -1, 1) * 32767).astype("<i2").tobytes()


BACKENDS = {"google": Google, "melo": Melo}


def silence(seconds):
    return b"\x00\x00" * int(RATE_HZ * seconds)


def cached_pcm(engine, text):
    CACHE.mkdir(exist_ok=True)
    key = hashlib.sha256((engine.tag() + "\n" + text).encode("utf-8")).hexdigest()[:32]
    f = CACHE / f"{key}.pcm"
    if f.exists():
        return f.read_bytes()
    pcm = b"".join(engine.pcm(chunk) for chunk in sentences(text, engine.limit))
    f.write_bytes(pcm)
    return pcm


def ffmpeg():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return "ffmpeg"


def build(engine, script, outdir, track, total):
    source = script.read_text(encoding="utf-8")
    segs = list(segments(source))
    first = re.search(r"^#\s*(.+)$", source, flags=re.M)
    title = first.group(1).strip() if first else script.stem
    pcm = []
    for i, (kind, text) in enumerate(segs):
        if kind.startswith("h"):
            pcm.append(silence(PAUSE[f"before_{kind}"]))
            pcm.append(cached_pcm(engine, text))
            pcm.append(silence(PAUSE[f"after_{kind}"]))
        else:
            pcm.append(cached_pcm(engine, text))
            pcm.append(silence(PAUSE["p"]))
        print(f"  {script.name}: {i + 1}/{len(segs)}", end="\r", flush=True)
    raw = b"".join(pcm)
    out = outdir / (script.stem + ".mp3")
    cmd = [ffmpeg(), "-y", "-loglevel", "error", "-f", "s16le", "-ar", str(RATE_HZ), "-ac", "1", "-i", "-",
           "-codec:a", "libmp3lame", "-b:a", "64k",
           "-metadata", f"title={title}", "-metadata", "artist=권태홍",
           "-metadata", "album=허락 화살표 학위 논문 오디오북(쉬운 한국어)", "-metadata", f"track={track}/{total}",
           str(out)]
    subprocess.run(cmd, input=raw, check=True)
    seconds = len(raw) / 2 / RATE_HZ
    print(f"  {out.name}: {seconds / 60:.1f} min")
    return seconds


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", choices=sorted(BACKENDS), required=True)
    ap.add_argument("--voice")
    ap.add_argument("--rate", type=float, default=1.0)
    ap.add_argument("--list-voices", action="store_true")
    ap.add_argument("--out", default=str(ROOT / "audio"))
    ap.add_argument("scripts", nargs="*")
    a = ap.parse_args()
    engine = BACKENDS[a.backend](a.voice, a.rate)
    if a.list_voices:
        print("\n".join(engine.voices()))
        return
    outdir = Path(a.out)
    outdir.mkdir(exist_ok=True)
    scripts = [Path(s) for s in a.scripts] or sorted((ROOT / "script").glob("*.md"))
    print(f"voice: {engine.tag()}")
    total = 0.0
    for i, s in enumerate(scripts, 1):
        total += build(engine, s, outdir, i, len(scripts))
    print(f"total: {total / 3600:.2f} h")


if __name__ == "__main__":
    main()
