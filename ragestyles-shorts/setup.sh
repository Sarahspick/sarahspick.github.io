#!/usr/bin/env bash
# One-shot setup for a fresh session (any Claude account).  Run from anywhere:
#   bash ragestyles-shorts/setup.sh            # render deps + footage and SFX for the liked shorts
#   bash ragestyles-shorts/setup.sh --full     # also whisper, demucs (CPU torch) and the Demucs weights
# Needs network access to: archive.org, *.archive.org, images-assets.nasa.gov, assets.mixkit.co, pypi.org,
# files.pythonhosted.org (and for --full: huggingface.co, download.pytorch.org). See HANDOFF.md.
set -euo pipefail
cd "$(dirname "$0")"

if ! command -v ffmpeg >/dev/null; then
  echo "installing ffmpeg"; (apt-get update -qq && apt-get install -y -qq ffmpeg) || sudo apt-get install -y ffmpeg
fi

python3 -m pip install -q numpy opencv-python-headless pillow soundfile pyloudnorm scipy cairosvg
if [[ "${1:-}" == "--full" ]]; then
  python3 -m pip install -q --index-url https://download.pytorch.org/whl/cpu torch torchaudio
  python3 -m pip install -q faster-whisper demucs
fi

mkdir -p work/renders
if [[ "${1:-}" == "--full" ]]; then
  python3 pipeline/fetch_sources.py core sfx_mixkit models --derive
else
  python3 pipeline/fetch_sources.py core sfx_mixkit
fi

# smoke test: three stills of the restyled Sandow short
python3 pipeline/bench.py plans6/c4_sandow_1894_v2.json --frames 0,300,600 --stills work/renders/smoke >/dev/null
echo "setup ok: stills in ragestyles-shorts/work/renders/smoke"
