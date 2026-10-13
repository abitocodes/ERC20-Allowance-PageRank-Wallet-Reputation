#!/usr/bin/env bash
# video/build_video.sh — the whole video build for one language, in order.
#   bash build_video.sh ko WORKDIR          # or en
# Needs: node + playwright-core (npm install in ../tools), ffmpeg, Python 3.10+ with numpy, scipy,
# soundfile, pyloudnorm, onnxruntime, faster-whisper; Chromium as for tools/shoot.mjs; network once for
# the Supertonic 2 and Whisper models (Hugging Face). The narration scripts are in scripts/<lang>/.
set -euo pipefail
LANG_=${1:?usage: build_video.sh ko|en WORKDIR}; W=${2:?usage: build_video.sh ko|en WORKDIR}
HERE=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$W"
# 1. step list, anchors and reference shots (for the scripts and the camera boxes)
[ -f "$W/extract/$LANG_/steps.json" ] || node "$HERE/extract.mjs" --lang "$LANG_" --out "$W/extract/$LANG_"
# 2. the TTS model (Supertonic 2, OpenRAIL-M) and its helper (MIT)
if [ ! -f "$W/tts/model/onnx/vocoder.onnx" ]; then
  mkdir -p "$W/tts/model/onnx" "$W/tts/model/voice_styles"
  for f in onnx/duration_predictor.onnx onnx/text_encoder.onnx onnx/tts.json onnx/unicode_indexer.json onnx/vector_estimator.onnx \
           onnx/vocoder.onnx voice_styles/F3.json LICENSE; do
    curl -sL -o "$W/tts/model/$f" "https://huggingface.co/Supertone/supertonic-2/resolve/main/$f"
  done
  curl -sL -o "$W/tts/helper.py" https://raw.githubusercontent.com/supertone-inc/supertonic/main/py/helper.py
fi
# 3. speech, checked by ear (Whisper)
python3 "$HERE/tts.py" --lang "$LANG_" --scripts "$HERE/scripts" --model "$W/tts/model" --out "$W/audio" --whisper-dir "$W/whisper"
# 4. music (once for both languages)
[ -f "$W/music/m4.wav" ] || python3 "$HERE/music.py" "$W/music"
# 5. plan, picture, sound
python3 "$HERE/plan.py" --lang "$LANG_" --steps "$W/extract/$LANG_/steps.json" --scripts "$HERE/scripts" --audio "$W/audio" --out "$W/plan-$LANG_.json"
node "$HERE/render.mjs" --plan "$W/plan-$LANG_.json" --out "$W/render/$LANG_" --workers 3
python3 "$HERE/mix.py" --lang "$LANG_" --plan "$W/plan-$LANG_.json" --render "$W/render/$LANG_" --audio "$W/audio" \
  --music "$W/music" --steps "$W/extract/$LANG_/steps.json" --out "$W/out"
