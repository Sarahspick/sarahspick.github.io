"""Meme sound effects synthesized from scratch (no samples, no licensing issues).

Each function returns a float32 mono numpy array at SR. mix() places them on a timeline.
"""
import wave

import numpy as np

SR = 44100
rng = np.random.default_rng(1)


def _t(dur):
    return np.arange(int(SR * dur)) / SR


def _env(n, attack=0.005, decay=None):
    t = np.arange(n) / SR
    e = np.minimum(1, t / attack)
    if decay:
        e *= np.exp(-t / decay)
    return e


def _lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def boom(dur=1.4):
    """Vine-boom style: deep sweeping hit with a saturated punch."""
    t = _t(dur)
    f = 40 + 110 * np.exp(-t / 0.05)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.25 * np.sin(3 * ph)
    x *= _env(len(t), 0.002, 0.45)
    click = _lowpass(rng.standard_normal(len(t)), 900) * _env(len(t), 0.001, 0.015) * 3
    return np.tanh(2.2 * (x + click)) * 0.9


def whoosh(dur=0.45, up=True):
    t = _t(dur)
    n = rng.standard_normal(len(t))
    hp = n - _lowpass(n, 300)
    shaped = _lowpass(hp, 2500)
    e = np.sin(np.pi * t / dur) ** 2
    return (shaped * e / np.abs(shaped).max() * 0.7).astype(np.float32)


def pop(dur=0.09, f0=350, f1=1300):
    t = _t(dur)
    f = f0 + (f1 - f0) * (t / dur) ** 0.5
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(len(t), 0.001, 0.03)
    return x * 0.8


def ding(f=1320):
    """Notification ding: bell partials, fast decay."""
    t = _t(0.8)
    x = sum(a * np.sin(2 * np.pi * f * m * t) * np.exp(-t / (0.35 / m))
            for m, a in [(1, 1), (2.01, 0.45), (3.02, 0.2), (4.1, 0.1)])
    tone2 = sum(a * np.sin(2 * np.pi * f * 1.335 * m * t) * np.exp(-t / (0.35 / m))
                for m, a in [(1, 1), (2.01, 0.4)])
    x2 = np.concatenate([np.zeros(int(0.09 * SR)), tone2[: len(t) - int(0.09 * SR)]])
    return (x + x2) * _env(len(t), 0.001) * 0.35


def tick(dur=0.03):
    t = _t(dur)
    n = rng.standard_normal(len(t))
    return (n - _lowpass(n, 2000)) * _env(len(t), 0.0005, 0.006) * 0.6


def printer(dur=0.5):
    """Receipt printer: rapid ticks with a motor hum."""
    out = np.zeros(int(SR * dur))
    for s in np.arange(0, dur - 0.03, 0.028):
        i = int(s * SR)
        tk = tick()
        out[i:i + len(tk)] += tk * rng.uniform(0.6, 1)
    t = _t(dur)
    out += 0.08 * np.sign(np.sin(2 * np.pi * 95 * t)) * np.sin(np.pi * t / dur)
    return _lowpass(out, 5000) * 1.4


def kaching():
    t = _t(0.9)
    bell = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t / d)
               for f, a, d in [(2637, 0.6, 0.35), (3520, 0.45, 0.3), (5274, 0.25, 0.2)])
    late = np.concatenate([np.zeros(int(0.07 * SR)), bell[: len(t) - int(0.07 * SR)]])
    n = rng.standard_normal(len(t))
    rattle = (n - _lowpass(n, 3000)) * _env(len(t), 0.001, 0.05) * 0.5
    return (late * 0.5 + rattle) * 0.7


def stamp():
    """Rubber stamp thud: low knock + paper slap."""
    t = _t(0.35)
    knock = np.sin(2 * np.pi * (90 + 60 * np.exp(-t / 0.02)) * t) * _env(len(t), 0.001, 0.07)
    n = rng.standard_normal(len(t))
    slap = _lowpass(n, 1800) * _env(len(t), 0.0005, 0.025) * 2
    return np.tanh(1.8 * (knock + slap)) * 0.9


def sad_trombone():
    """wah wah wah waaah with growly brass timbre."""
    notes = [(233.1, 0.38), (220.0, 0.38), (207.7, 0.38), (196.0, 1.3)]
    out = []
    for i, (f, d) in enumerate(notes):
        t = _t(d)
        vib = 1 + (0.025 * np.sin(2 * np.pi * 6 * t) * np.minimum(1, t / 0.3) if i == 3 else 0)
        ph = 2 * np.pi * np.cumsum(f * vib) / SR
        saw = sum(np.sin(k * ph) / k for k in range(1, 12))
        wah = 0.35 + 0.65 * np.sin(np.pi * np.minimum(t / d, 1)) ** 0.6
        out.append(_lowpass(saw * wah, 1600) * _env(len(t), 0.02) * np.minimum(1, (d - t) / 0.05))
    return np.concatenate(out) * 0.5


def riser(dur=1.2):
    """Tension riser: rising detuned saws + noise."""
    t = _t(dur)
    f = 180 * 2 ** (2.2 * t / dur)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = sum(np.sin(k * ph) / k for k in range(1, 7)) + sum(np.sin(k * ph * 1.01) / k for k in range(1, 7))
    n = rng.standard_normal(len(t))
    x = x * 0.25 + (n - _lowpass(n, 1500)) * 0.15
    return x * (t / dur) ** 2 * 0.8


def bruh_horn():
    """Air horn burst (MLG style), three blasts."""
    out = []
    for d in (0.16, 0.16, 0.6):
        t = _t(d)
        ph = 2 * np.pi * 466 * t
        x = sum(np.sign(np.sin(k * ph + 0.3 * k)) / k for k in (1, 1.5, 2))
        out += [np.tanh(1.5 * x) * _env(len(t), 0.005) * np.minimum(1, (d - t) / 0.02) * 0.35,
                np.zeros(int(0.05 * SR))]
    return np.concatenate(out)


def heartbeat(beats=3, bpm=110):
    out = np.zeros(int(SR * beats * 60 / bpm) + SR // 2)
    t = _t(0.18)
    thump = np.sin(2 * np.pi * (55 + 30 * np.exp(-t / 0.03)) * t) * _env(len(t), 0.002, 0.05)
    for b in range(beats):
        i = int(b * 60 / bpm * SR)
        out[i:i + len(t)] += thump
        j = i + int(0.16 * SR)
        out[j:j + len(t)] += thump * 0.7
    return out * 0.9


def beat_loop(dur, bpm=100):
    """Quiet bouncy background beat: kick, clap, hats."""
    out = np.zeros(int(SR * dur) + SR)
    step = 60 / bpm / 2
    kt = _t(0.25)
    kick = np.sin(2 * np.pi * (50 + 90 * np.exp(-kt / 0.03)) * kt) * _env(len(kt), 0.001, 0.1)
    for k in range(int(dur / step)):
        i = int(k * step * SR)
        if k % 4 == 0:
            out[i:i + len(kick)] += kick
        if k % 4 == 2:
            n = rng.standard_normal(int(0.12 * SR))
            out[i:i + len(n)] += (n - _lowpass(n, 1200)) * _env(len(n), 0.001, 0.03) * 0.5
        h = tick(0.05) * 0.5
        out[i:i + len(h)] += h
    return out[: int(SR * dur)] * 0.35


def mix(dur, events, music=None):
    """events: list of (seconds, sound_array, gain)."""
    out = np.zeros(int(SR * dur) + SR * 3)
    if music is not None:
        out[: len(music)] += music
    for s, snd, g in events:
        i = int(s * SR)
        out[i:i + len(snd)] += snd * g
    out = out[: int(SR * dur)]
    peak = np.abs(out).max()
    if peak > 0.95:
        out = np.tanh(out / peak * 1.2) * 0.95
    return out.astype(np.float32)


def write_wav(path, x):
    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
