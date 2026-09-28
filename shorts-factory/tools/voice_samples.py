"""Render one line in several voices so the narrator can be picked by ear.

    python tools/voice_samples.py "This SUV can literally bounce itself out of sand." --rate +20%
"""
import argparse
import os
import sys

import soundfile as sf

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from factory.config import OUTPUT  # noqa: E402
from factory.voice import EdgeNarrator  # noqa: E402

VOICES = {
    "en": ["en-US-BrianMultilingualNeural", "en-US-AndrewMultilingualNeural", "en-US-ChristopherNeural",
           "en-US-GuyNeural", "en-US-AvaMultilingualNeural", "en-US-EmmaMultilingualNeural"],
    "ko": ["ko-KR-HyunsuMultilingualNeural", "ko-KR-InJoonNeural", "ko-KR-SunHiNeural"],
}

ap = argparse.ArgumentParser()
ap.add_argument("text", nargs="?", default="This guy just walked out of a store without paying... and nobody stopped him.")
ap.add_argument("--lang", default="en", choices=list(VOICES))
ap.add_argument("--rate", default="+20%")
args = ap.parse_args()

out = os.path.join(OUTPUT, "voice_samples")
os.makedirs(out, exist_ok=True)
for v in VOICES[args.lang]:
    n = EdgeNarrator(v, args.rate, lang=args.lang)
    audio, _ = n._synth(args.text)
    sf.write(os.path.join(out, v + ".wav"), audio, n.sr)
    print("sample", v)
