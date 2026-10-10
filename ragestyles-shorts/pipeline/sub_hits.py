"""Five soft sub hit impacts (2026-10-10, owner: "Sub Hit Impact, not harsh on the ears, bass feel").
Synthesized from scratch like sfx_synth.py (no third-party audio): sine bodies with pitch drops, a 4 to 8 ms raised
cosine attack instead of a click, gentle saturation only, everything low passed (no hiss or crack), a quiet second
harmonic so phones still hear it, peak normalised to -3 dBFS, 48 kHz stereo.
Run: python3 pipeline/sub_hits.py   (writes assets/sfx/sub_hit_soft.wav ... sub_hit_rumble.wav)
"""
import os
import sys

import numpy as np
import soundfile as sf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sfx_synth import SR, OUT, butter, noise, reverb, t_axis  # noqa: E402


def glide(f0, f1, rate, t):
    """Exponential pitch drop from f0 to f1 (rate: how fast it settles)."""
    return f1 + (f0 - f1) * np.exp(-t * rate)


def tone(f, t, harm=0.0):
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) + harm * np.sin(2 * ph)


def soft_attack(y, ms):
    n = int(ms / 1000 * SR)
    y[:n] *= 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, n))
    return y


def finish(y, lp, attack_ms, width=0.0):
    y = butter(y, "lowpass", lp, 4)
    y = soft_attack(y, attack_ms)
    tail = int(0.08 * SR)
    y[-tail:] *= np.linspace(1, 0, tail) ** 2
    y = y / (np.max(np.abs(y)) + 1e-9) * 10 ** (-3 / 20)
    if width:  # a few samples of delay on one side, mono compatible
        d = int(width * SR / 1000)
        r = np.concatenate([np.zeros(d), y[:-d]])
        return np.stack([y, 0.85 * y + 0.15 * r], 1)
    return np.stack([y, y], 1)


def sub_hit_soft(dur=1.4):
    """Round, deep and calm: 48 to 32 Hz, long smooth decay."""
    t = t_axis(dur)
    y = tone(glide(48, 32, 6, t), t, harm=0.12) * np.exp(-t * 2.6)
    return finish(np.tanh(1.2 * y), 600, 6)


def sub_hit_warm(dur=1.2):
    """Warmer and easier on phones: 60 to 38 Hz with a soft 2nd harmonic and a small room."""
    t = t_axis(dur)
    y = tone(glide(60, 38, 9, t), t, harm=0.28) * np.exp(-t * 3.4)
    knock = butter(noise(dur), "lowpass", 260, 2) * np.exp(-t * 55) * 0.25
    y = np.tanh(1.4 * (y + knock))
    y = reverb(y, 0.7, 0.12)[: len(t)]
    return finish(y, 1100, 5, width=0.6)


def sub_hit_drop(dur=1.7):
    """Pitch falls a long way, like a tape stop in the low end: 85 to 26 Hz."""
    t = t_axis(dur)
    f = 26 + 59 * np.clip(1 - (t / 0.9), 0, 1) ** 1.8
    y = tone(f, t, harm=0.15) * np.exp(-t * 2.1)
    return finish(np.tanh(1.3 * y), 700, 8)


def sub_hit_thud(dur=0.8):
    """Short and tight, kick drum like: 110 to 44 Hz, quick decay, no click."""
    t = t_axis(dur)
    y = tone(glide(110, 44, 22, t), t, harm=0.2) * np.exp(-t * 6.5)
    knock = butter(noise(dur), "lowpass", 350, 2) * np.exp(-t * 80) * 0.3
    return finish(np.tanh(1.5 * (y + knock)), 900, 4)


def sub_hit_rumble(dur=2.4):
    """Cinematic: a deep hit that opens into a dark rumble tail."""
    t = t_axis(dur)
    body = tone(glide(55, 30, 5, t), t, harm=0.1) * np.exp(-t * 2.0)
    rum = butter(noise(dur, "pink"), "lowpass", 140, 4) * np.exp(-t * 1.4) * (1 - np.exp(-t * 18)) * 0.45
    y = np.tanh(1.2 * (body + rum))
    y = reverb(y, 1.6, 0.18)[: len(t)]
    return finish(y, 500, 7, width=0.8)


SOUNDS = {"sub_hit_soft": sub_hit_soft, "sub_hit_warm": sub_hit_warm, "sub_hit_drop": sub_hit_drop,
          "sub_hit_thud": sub_hit_thud, "sub_hit_rumble": sub_hit_rumble}

if __name__ == "__main__":
    for name, fn in SOUNDS.items():
        sf.write(os.path.join(OUT, name + ".wav"), fn(), SR, subtype="PCM_24")
        print(name)
