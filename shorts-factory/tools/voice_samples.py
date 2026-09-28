"""Render one line in several Kokoro voices so the narrator can be picked by ear.

    python tools/voice_samples.py "This SUV can literally bounce itself out of sand."
"""
import os
import subprocess
import sys

import soundfile as sf

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from factory.config import OUTPUT  # noqa: E402
from factory.voice import Narrator  # noqa: E402

VOICES = ["am_michael", "am_fenrir", "am_puck", "bm_george", "af_heart", "af_bella"]

text = sys.argv[1] if len(sys.argv) > 1 else "This guy just walked out of a store without paying... and nobody stopped him."
out = os.path.join(OUTPUT, "voice_samples")
os.makedirs(out, exist_ok=True)
for v in VOICES:
    n = Narrator(voice=v, speed=1.15)
    wav = os.path.join(out, v + ".wav")
    sf.write(wav, n.synth(text), n.sr)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wav, "-af", "loudnorm=I=-16:TP=-1.5", "-ar", "44100", "-b:a", "160k",
                    os.path.join(out, v + ".mp3")], check=True)
    os.remove(wav)
    print("sample", v)
