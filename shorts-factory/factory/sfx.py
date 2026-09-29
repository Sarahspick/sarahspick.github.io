"""Sound-effect library: loudness-normalized copies of the downloaded SFX, cached as 48 kHz stereo WAV."""
import json
import os
import re
import subprocess

from .config import SR, WORK, asset


def measure(path):
    """Return (integrated LUFS, true-peak dBFS) using ffmpeg's ebur128 meter."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True)
    tail = r.stderr[r.stderr.rfind("Summary:"):]
    i = re.search(r"I:\s+(-?[\d.]+|-inf) LUFS", tail)
    p = re.search(r"Peak:\s+(-?[\d.]+|-inf) dBFS", tail)
    lufs = float(i.group(1)) if i and i.group(1) != "-inf" else -70.0
    peak = float(p.group(1)) if p and p.group(1) != "-inf" else -70.0
    return lufs, peak


class SfxLibrary:
    def __init__(self):
        with open(asset("sfx_library.json"), encoding="utf-8") as f:
            self.lib = json.load(f)["sounds"]
        self.cache = os.path.join(WORK, "sfx_cache")
        os.makedirs(self.cache, exist_ok=True)

    def ids(self):
        return list(self.lib)

    def path(self, sid):
        if sid not in self.lib:
            raise KeyError(f"unknown sfx '{sid}'. known: {', '.join(self.lib)}")
        src = asset("sfx", self.lib[sid]["file"])
        if not os.path.exists(src):
            raise FileNotFoundError(f"{src} missing - run: python tools/fetch_assets.py sfx")
        out = os.path.join(self.cache, sid + ".wav")
        if not os.path.exists(out):
            lufs, peak = measure(src)
            target = self.lib[sid].get("lufs", -19)
            if lufs > -60:
                gain = target - lufs
            else:  # too short for a loudness reading (clicks): peak-normalize instead
                gain = (target + 10) - peak
            gain = min(gain, -1.0 - peak)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af", f"volume={gain:.2f}dB",
                            "-ar", str(SR), "-ac", "2", out], check=True)
        return out
