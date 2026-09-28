"""Procedural sound design: every sound effect and music bed is synthesized
from scratch with numpy, so the channel never depends on third-party audio
(no Content ID claims, no license bookkeeping).

All functions return float32 numpy arrays at SR, mono (n,) or stereo (n, 2).
"""
import numpy as np
from scipy import signal

SR = 48000
_rng = np.random.default_rng(7)


# ---------------------------------------------------------------- basics
def ns(dur):
    return int(dur * SR + 1e-6)


def t_axis(dur):
    return np.arange(ns(dur)) / SR


def noise(dur, rng=None):
    rng = rng or _rng
    return rng.standard_normal(ns(dur)).astype(np.float32)


def brown(dur, rng=None):
    x = np.cumsum(noise(dur, rng))
    x = signal.lfilter([1, -1], [1, -0.995], x)  # remove DC drift
    return (x / (np.abs(x).max() + 1e-9)).astype(np.float32)


def band(x, lo=None, hi=None, order=2):
    if lo and hi:
        b, a = signal.butter(order, [lo, hi], btype="band", fs=SR)
    elif lo:
        b, a = signal.butter(order, lo, btype="high", fs=SR)
    else:
        b, a = signal.butter(order, hi, btype="low", fs=SR)
    return signal.lfilter(b, a, x).astype(np.float32)


def env_exp(n, tau):
    return np.exp(-np.arange(n) / (tau * SR)).astype(np.float32)


def adsr(n, a=0.01, d=0.1, s=0.7, r=0.2):
    e = np.full(n, s, np.float32)
    na, nd, nr = int(a * SR), ns(d), int(r * SR)
    na = min(na, n)
    e[:na] = np.linspace(0, 1, na, endpoint=False)
    nd = min(nd, n - na)
    e[na:na + nd] = np.linspace(1, s, nd, endpoint=False)
    nr = min(nr, n)
    if nr:
        e[n - nr:] *= np.linspace(1, 0, nr)
    return e


def norm(x, peak=0.9):
    m = np.abs(x).max()
    return (x * (peak / m)).astype(np.float32) if m > 0 else x


def fade(x, fin=0.01, fout=0.05):
    n = len(x)
    a, b = min(int(fin * SR), n), min(int(fout * SR), n)
    y = x.copy()
    if a:
        y[:a] *= np.linspace(0, 1, a)[:, None] if y.ndim == 2 else np.linspace(0, 1, a)
    if b:
        y[n - b:] *= np.linspace(1, 0, b)[:, None] if y.ndim == 2 else np.linspace(1, 0, b)
    return y


def stereo(x, pan=0.0):
    """equal-power pan, pan in [-1, 1]"""
    th = (pan + 1) * np.pi / 4
    return np.stack([x * np.cos(th), x * np.sin(th)], axis=1).astype(np.float32)


def reverb_ir(dur=1.8, decay=0.45, rng=None, bright=6000):
    rng = rng or np.random.default_rng(11)
    n = ns(dur)
    ir = np.stack([rng.standard_normal(n), rng.standard_normal(n)], 1)
    ir *= env_exp(n, decay)[:, None]
    ir[:, 0] = band(ir[:, 0], hi=bright)
    ir[:, 1] = band(ir[:, 1], hi=bright)
    ir[: int(0.012 * SR)] = 0  # pre-delay
    return (ir / np.sqrt((ir ** 2).sum(0))).astype(np.float32)


def reverb(x, wet=0.25, ir=None):
    ir = reverb_ir() if ir is None else ir
    if x.ndim == 1:
        x = stereo(x)
    out = np.stack([signal.fftconvolve(x[:, c], ir[:, c])[: len(x)] for c in range(2)], 1)
    return ((1 - wet) * x + wet * out).astype(np.float32)


def sine(freq, dur, phase=0.0):
    t = t_axis(dur)
    if np.isscalar(freq):
        return np.sin(2 * np.pi * freq * t + phase).astype(np.float32)
    ph = 2 * np.pi * np.cumsum(freq) / SR
    return np.sin(ph + phase).astype(np.float32)


def saw(freq, dur, harmonics=24):
    t = t_axis(dur)
    y = np.zeros_like(t)
    for k in range(1, harmonics + 1):
        if k * freq > SR / 2.2:
            break
        y += ((-1) ** (k + 1)) * np.sin(2 * np.pi * k * freq * t) / k
    return (y * 0.6).astype(np.float32)


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# ---------------------------------------------------------------- SFX
def sfx_shutter(rng=None):
    rng = rng or np.random.default_rng()
    out = np.zeros(int(0.16 * SR), np.float32)
    for off, amp in ((0.0, 1.0), (0.055 + rng.uniform(-0.01, 0.01), 0.7)):
        n = int(0.006 * SR)
        c = band(rng.standard_normal(n).astype(np.float32), 1800, 7000) * env_exp(n, 0.0015)
        i = int(off * SR)
        out[i:i + n] += amp * c
    th = sine(140, 0.03) * env_exp(int(0.03 * SR), 0.006) * 0.35
    out[: len(th)] += th
    return norm(out, 0.8)


def sfx_static(dur=0.25, rng=None):
    rng = rng or np.random.default_rng()
    x = noise(dur, rng)
    x = band(x, 700, 9000)
    gate = (rng.random(len(x) // 240 + 1) > 0.35).astype(np.float32)
    gate = np.repeat(gate, 240)[: len(x)]
    gate = band(gate, hi=900) * 1.3
    hum = sine(120, dur) * 0.15
    return fade(norm(x * (0.35 + gate) + hum, 0.7), 0.003, 0.03)


def sfx_whoosh(dur=0.45, up=True, rng=None):
    rng = rng or np.random.default_rng()
    x = noise(dur, rng)
    n = len(x)
    out = np.zeros(n, np.float32)
    chunks = 24
    edges = np.linspace(0, n, chunks + 1).astype(int)
    for i in range(chunks):
        f = i / (chunks - 1)
        c = 300 + (4200 if up else 2500) * (f if up else (1 - f))
        seg = x[edges[i]:edges[i + 1]]
        out[edges[i]:edges[i + 1]] = band(seg, max(80, c * 0.5), min(16000, c * 1.6), 1)
    e = np.sin(np.linspace(0, np.pi, n)) ** 1.6
    return fade(norm(out * e, 0.8), 0.002, 0.02)


def sfx_impact(rng=None):
    dur = 1.4
    t = t_axis(dur)
    f = 38 + 70 * np.exp(-t / 0.06)
    boom = sine(f, dur) * env_exp(len(t), 0.35)
    sub = sine(32, dur) * env_exp(len(t), 0.6) * 0.5
    crack = band(noise(0.08, rng), 200, 5000) * env_exp(int(0.08 * SR), 0.015)
    x = boom + sub
    x[: len(crack)] += crack * 0.8
    x = np.tanh(x * 1.6)
    return fade(norm(x, 0.95), 0.001, 0.2)


def sfx_riser(dur=1.6, rng=None):
    t = t_axis(dur)
    f = 110 * (2 ** (3 * (t / dur) ** 1.5))
    tone = sine(f, dur) * 0.3 + sine(f * 1.5, dur) * 0.15
    nz = noise(dur, rng)
    n = len(nz)
    out = np.zeros(n, np.float32)
    edges = np.linspace(0, n, 21).astype(int)
    for i in range(20):
        c = 400 + 7000 * (i / 19) ** 2
        out[edges[i]:edges[i + 1]] = band(nz[edges[i]:edges[i + 1]], c * 0.6, min(18000, c * 1.4), 1)
    e = (t / dur) ** 2.2
    return fade(norm((tone + out * 0.6) * e, 0.8), 0.01, 0.005)


def sfx_ding(freq=1318.5):
    dur = 1.2
    t = t_axis(dur)
    x = np.zeros_like(t)
    for r, a, d in ((1, 1, 0.5), (2.76, 0.4, 0.25), (5.4, 0.2, 0.12), (8.93, 0.08, 0.06)):
        x += a * np.sin(2 * np.pi * freq * r * t) * np.exp(-t / d)
    return norm(x.astype(np.float32), 0.6)


def sfx_pop():
    dur = 0.09
    t = t_axis(dur)
    f = 500 + 1300 * (t / dur)
    return norm(sine(f, dur) * env_exp(len(t), 0.02), 0.6)


def sfx_heartbeat(bpm=70, dur=4.0):
    out = np.zeros(ns(dur), np.float32)
    beat = 60 / bpm
    thump_d = 0.18
    tt = t_axis(thump_d)
    thump = sine(48 + 30 * np.exp(-tt / 0.02), thump_d) * env_exp(len(tt), 0.05)
    thump = np.tanh(thump * 2)
    t0 = 0.0
    while t0 < dur - 0.4:
        for off, amp in ((0, 1.0), (0.26, 0.7)):
            i = int((t0 + off) * SR)
            j = min(len(out), i + len(thump))
            out[i:j] += amp * thump[: j - i]
        t0 += beat
    return norm(out, 0.9)


def sfx_rewind(dur=0.7, rng=None):
    t = t_axis(dur)
    f = 900 + 2600 * (t / dur) + 300 * np.sin(2 * np.pi * 23 * t)
    x = sine(f, dur) * 0.4 + band(noise(dur, rng), 2000, 9000) * 0.5
    x *= 0.6 + 0.4 * np.sin(2 * np.pi * 31 * t) ** 2
    return fade(norm(x, 0.7), 0.01, 0.05)


def sfx_beep(freq=1000, dur=0.08):
    return fade(sine(freq, dur) * 0.5, 0.003, 0.01)


def sfx_scratch(rng=None):
    dur = 0.35
    t = t_axis(dur)
    f = 300 + 900 * np.abs(np.sin(2 * np.pi * 3.2 * t))
    x = sine(f, dur) * 0.3 + band(noise(dur, rng), 600, 4000) * 0.5 * np.abs(np.sin(2 * np.pi * 3.2 * t))
    return fade(norm(x, 0.7), 0.002, 0.03)


def sfx_tick():
    n = int(0.012 * SR)
    return band(noise(0.012), 3000, 9000) * env_exp(n, 0.002) * 0.5


# ---------------------------------------------------------------- ambience
def amb_wind(dur, rng=None):
    rng = rng or np.random.default_rng()
    x = band(brown(dur, rng), 60, 900)
    lfo = 0.6 + 0.4 * np.sin(2 * np.pi * rng.uniform(0.05, 0.12) * t_axis(dur) + rng.uniform(0, 6))
    return norm(x * lfo, 0.5)


def amb_birds(dur, density=0.5, rng=None):
    rng = rng or np.random.default_rng()
    out = np.zeros(ns(dur), np.float32)
    ncalls = int(dur * density)
    for _ in range(ncalls):
        start = rng.uniform(0, max(0.01, dur - 0.6))
        base = rng.uniform(2200, 4800)
        notes = rng.integers(2, 6)
        tcur = start
        for _k in range(notes):
            d = rng.uniform(0.04, 0.12)
            tt = t_axis(d)
            sweep = base * (1 + rng.uniform(-0.25, 0.35) * tt / d)
            ch = sine(sweep, d) * np.sin(np.pi * tt / d) ** 2
            i = int(tcur * SR)
            j = min(len(out), i + len(ch))
            out[i:j] += ch[: j - i] * rng.uniform(0.2, 0.5)
            tcur += d + rng.uniform(0.02, 0.08)
    return out


def amb_crickets(dur, rng=None):
    rng = rng or np.random.default_rng()
    t = t_axis(dur)
    out = np.zeros_like(t, dtype=np.float32)
    for _ in range(3):
        fc = rng.uniform(3900, 5200)
        rate = rng.uniform(18, 32)
        chirp_period = rng.uniform(0.35, 0.8)
        car = np.sin(2 * np.pi * fc * t)
        pulses = (np.sin(2 * np.pi * rate * t) > 0.2).astype(np.float32)
        burst = ((t % chirp_period) < chirp_period * rng.uniform(0.3, 0.5)).astype(np.float32)
        burst = band(burst, hi=60)
        out += (car * pulses * burst).astype(np.float32) * rng.uniform(0.2, 0.4)
    return out


def ambience(dur, kind="day", seed=0):
    rng = np.random.default_rng(seed)
    if kind == "night":
        x = amb_crickets(dur, rng) * 0.10 + amb_wind(dur, rng) * 0.25
    elif kind == "fire":
        crack = np.zeros(ns(dur), np.float32)
        for _ in range(int(dur * 14)):
            i = int(rng.uniform(0, dur - 0.05) * SR)
            n = int(rng.uniform(0.003, 0.02) * SR)
            crack[i:i + n] += band(rng.standard_normal(n).astype(np.float32), 800, 7000) * rng.uniform(0.2, 1)
        x = band(brown(dur, rng), 40, 500) * 0.5 + crack * 0.35 + amb_wind(dur, rng) * 0.3
    else:
        x = amb_wind(dur, rng) * 0.3 + amb_birds(dur, 0.45, rng) * 0.25
    return stereo(fade(norm(x, 0.5), 0.5, 0.8), 0) * 1.0


# ---------------------------------------------------------------- instruments
def inst_pluck(freq, dur, bright=1.0):
    t = t_axis(dur)
    x = np.zeros_like(t)
    for k in range(1, 9):
        if k * freq > 16000:
            break
        x += (1 / k ** (1.4 - 0.4 * bright)) * np.sin(2 * np.pi * k * freq * t) * np.exp(-t * (3 + 2.5 * k))
    return fade(x.astype(np.float32), 0.002, 0.02)


def inst_piano(freq, dur):
    t = t_axis(dur)
    x = np.zeros_like(t)
    B = 0.0004
    for k in range(1, 12):
        fk = k * freq * np.sqrt(1 + B * k * k)
        if fk > 16000:
            break
        x += (0.9 ** k) / k * np.sin(2 * np.pi * fk * t) * np.exp(-t * (1.2 + 0.9 * k))
    hammer = band(noise(0.01), 1000, 6000) * 0.05
    x[: len(hammer)] += hammer
    return fade(x.astype(np.float32), 0.002, 0.08)


def inst_pad(freqs, dur, bright=0.5):
    x = np.zeros(ns(dur), np.float32)
    for f in freqs:
        for det in (-0.12, 0.0, 0.11):
            x += saw(f * 2 ** (det / 12), dur, harmonics=10)
    x = band(x, hi=900 + 2500 * bright)
    return x * adsr(len(x), a=min(0.8, dur * 0.3), d=0.2, s=0.8, r=min(1.0, dur * 0.3)) / (3 * len(freqs))


def inst_bass(freq, dur):
    t = t_axis(dur)
    x = np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(2 * np.pi * 2 * freq * t)
    x = np.tanh(1.5 * x) * adsr(len(t), 0.005, 0.1, 0.6, 0.08)
    return x.astype(np.float32)


def drum_kick():
    d = 0.35
    tt = t_axis(d)
    f = 45 + 110 * np.exp(-tt / 0.035)
    return np.tanh(2 * sine(f, d) * env_exp(len(tt), 0.09)).astype(np.float32)


def drum_snare(rng=None):
    d = 0.22
    n = ns(d)
    nz = band(noise(d, rng), 1500, 9000) * env_exp(n, 0.05)
    tone = sine(185, d) * env_exp(n, 0.03)
    return (nz * 0.7 + tone * 0.5).astype(np.float32)


def drum_hat(rng=None, open_=False):
    d = 0.25 if open_ else 0.05
    n = ns(d)
    return (band(noise(d, rng), 7000, None) * env_exp(n, 0.08 if open_ else 0.012) * 0.35).astype(np.float32)


def drum_taiko(rng=None):
    d = 0.8
    tt = t_axis(d)
    f = 60 + 50 * np.exp(-tt / 0.05)
    body = sine(f, d) * env_exp(len(tt), 0.25)
    slap = band(noise(0.04, rng), 300, 3000) * env_exp(int(0.04 * SR), 0.01)
    body[: len(slap)] += slap * 0.6
    return np.tanh(1.8 * body).astype(np.float32)


# ---------------------------------------------------------------- music
SCALES = {
    "minor": [0, 2, 3, 5, 7, 8, 10],
    "major": [0, 2, 4, 5, 7, 9, 11],
    "penta": [0, 2, 4, 7, 9],
    "minpenta": [0, 3, 5, 7, 10],
}
PROGS = {
    "suspense": [(57, "m"), (57, "m"), (53, "M"), (52, "M")],   # Am Am F E
    "mystery": [(50, "m"), (46, "M"), (50, "m"), (45, "M")],    # Dm Bb Dm A
    "cute": [(60, "M"), (57, "m"), (53, "M"), (55, "M")],       # C Am F G
    "epic": [(50, "m"), (46, "M"), (53, "M"), (48, "M")],       # Dm Bb F C
    "sad": [(57, "m"), (53, "M"), (48, "M"), (55, "M")],        # Am F C G
    "funny": [(55, "M"), (60, "M"), (55, "M"), (62, "M")],      # G C G D
}


def chord_notes(root, q):
    return [root, root + (3 if q == "m" else 4), root + 7]


def _place(buf, x, t0, gain=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= len(buf):
        return
    if x.ndim == 1:
        x = stereo(x, pan)
    j = min(len(buf), i + len(x))
    buf[i:j] += x[: j - i] * gain


def music(mood, dur, seed=0, bpm=None):
    """Generate a looping-friendly music bed for a mood."""
    rng = np.random.default_rng(seed)
    bpm = bpm or {"suspense": 84, "mystery": 72, "cute": 112, "epic": 92, "sad": 70, "funny": 118}[mood]
    beat = 60 / bpm
    bar = 4 * beat
    prog = PROGS[mood]
    if rng.random() < 0.5 and mood != "suspense":
        prog = prog[:2] + prog[2:][::-1]
    shift = int(rng.integers(-2, 3))
    buf = np.zeros((int((dur + 2) * SR), 2), np.float32)
    nbars = int(np.ceil(dur / bar)) + 1
    scale = SCALES["minor" if mood in ("suspense", "mystery", "sad", "epic") else "major"]
    for b in range(nbars):
        root, q = prog[b % len(prog)]
        root += shift
        t0 = b * bar
        notes = chord_notes(root, q)
        intensity = min(1.0, 0.45 + 0.55 * b / max(1, nbars - 1))  # builds over time
        if mood in ("suspense", "mystery", "epic", "sad"):
            _place(buf, inst_pad([mtof(n) for n in notes], bar + 0.3, 0.35 + 0.3 * intensity), t0, 0.5, 0)
        if mood == "suspense":
            for k in range(8):
                _place(buf, inst_bass(mtof(root - 12), beat * 0.45), t0 + k * beat / 2, 0.35 * (0.6 + 0.4 * intensity))
            if b % 2 == 1:
                for k in range(2):
                    n = notes[int(rng.integers(0, 3))] + 12 * int(rng.integers(1, 3))
                    _place(buf, inst_piano(mtof(n), 2.0), t0 + beat * (1 + 2 * k), 0.22, rng.uniform(-0.5, 0.5))
            _place(buf, drum_kick(), t0, 0.5 * intensity)
            _place(buf, drum_kick(), t0 + 2.5 * beat, 0.35 * intensity)
        elif mood == "mystery":
            _place(buf, inst_bass(mtof(root - 12), bar * 0.9), t0, 0.25)
            for k in range(4):
                if rng.random() < 0.6:
                    n = root + 12 + scale[int(rng.integers(0, len(scale)))]
                    _place(buf, inst_piano(mtof(n), 2.5), t0 + k * beat + rng.choice([0, beat / 2]), 0.18, rng.uniform(-0.7, 0.7))
        elif mood == "epic":
            for k in range(4):
                _place(buf, drum_taiko(rng), t0 + k * beat, (0.55 if k in (0, 2) else 0.35) * intensity)
            if intensity > 0.6:
                for k in range(8):
                    _place(buf, drum_taiko(rng) * 0.4, t0 + k * beat / 2 + beat / 4, 0.25 * intensity)
            _place(buf, inst_bass(mtof(root - 12), bar * 0.95), t0, 0.35)
            for k, n in enumerate(notes + [notes[0] + 12]):
                _place(buf, inst_pluck(mtof(n + 12), 0.6, 0.8), t0 + k * beat, 0.2, (k - 1.5) / 3)
        elif mood == "sad":
            arp = notes + [notes[1] + 12, notes[2], notes[1]]
            for k in range(8):
                n = arp[k % len(arp)] + 12
                _place(buf, inst_piano(mtof(n), 2.2), t0 + k * beat / 2, 0.24, (k % 3 - 1) * 0.4)
            _place(buf, inst_bass(mtof(root - 12), bar), t0, 0.22)
        else:  # cute / funny
            _place(buf, inst_bass(mtof(root - 12), beat * 0.9), t0, 0.35)
            _place(buf, inst_bass(mtof(root - 5), beat * 0.9), t0 + 2 * beat, 0.3)
            for k in range(4):
                _place(buf, drum_kick(), t0 + k * beat, 0.35 if k % 2 == 0 else 0.0)
                _place(buf, drum_snare(rng), t0 + k * beat, 0.25 if k % 2 == 1 else 0.0)
                for h in range(2):
                    _place(buf, drum_hat(rng), t0 + k * beat + h * beat / 2, 0.5, 0.3)
            # melody: chord tones on beats, scale passing notes on offbeats
            deg = int(rng.integers(0, 3))
            for k in range(8):
                if rng.random() < (0.75 if mood == "cute" else 0.6):
                    if k % 2 == 0:
                        n = notes[deg % 3] + 12
                    else:
                        n = root + 12 + scale[int(rng.integers(0, len(scale)))]
                    _place(buf, inst_pluck(mtof(n + 12), 0.5, 1.0), t0 + k * beat / 2, 0.28, rng.uniform(-0.4, 0.4))
                    deg += int(rng.integers(-1, 2))
    buf = buf[: ns(dur)]
    buf = reverb(buf, wet=0.28 if mood in ("mystery", "sad", "suspense") else 0.15)
    buf = np.tanh(buf * 1.2)
    return fade(norm(buf, 0.8), 0.4, 1.5)


# ---------------------------------------------------------------- mixing
SFX = {
    "shutter": lambda rng: sfx_shutter(rng),
    "static": lambda rng: sfx_static(0.28, rng),
    "whoosh": lambda rng: sfx_whoosh(0.45, True, rng),
    "whoosh_down": lambda rng: sfx_whoosh(0.5, False, rng),
    "impact": lambda rng: sfx_impact(rng),
    "riser": lambda rng: sfx_riser(1.5, rng),
    "ding": lambda rng: sfx_ding(),
    "pop": lambda rng: sfx_pop(),
    "rewind": lambda rng: sfx_rewind(0.7, rng),
    "beep": lambda rng: sfx_beep(),
    "scratch": lambda rng: sfx_scratch(rng),
    "tick": lambda rng: sfx_tick(),
}
SFX_GAIN = {"shutter": 0.35, "static": 0.45, "whoosh": 0.5, "whoosh_down": 0.45, "impact": 0.9,
            "riser": 0.45, "ding": 0.45, "pop": 0.5, "rewind": 0.5, "beep": 0.25, "scratch": 0.5, "tick": 0.3}


def mix(dur, cues, mood="suspense", amb="day", seed=0, music_gain=0.30, amb_gain=0.35, voice=None):
    """cues: list of (time_sec, sfx_name) or (time_sec, sfx_name, gain)"""
    rng = np.random.default_rng(seed)
    out = np.zeros((ns(dur), 2), np.float32)
    if mood:
        out += music(mood, dur, seed) * music_gain
    if amb:
        out += ambience(dur, amb, seed)[: len(out)] * amb_gain
    for cue in cues:
        t0, name = cue[0], cue[1]
        g = cue[2] if len(cue) > 2 else 1.0
        if name.startswith("heartbeat"):
            d = float(name.split(":")[1]) if ":" in name else 3.0
            _place(out, sfx_heartbeat(72, d), t0, 0.55 * g)
            continue
        if name.startswith("fire"):
            d = float(name.split(":")[1]) if ":" in name else 3.0
            _place(out, fade(ambience(d, "fire", int(t0 * 1000)), 0.05, 0.6), t0, 0.9 * g)
            continue
        _place(out, SFX[name](rng), t0, SFX_GAIN[name] * g, 0)
    if voice is not None:
        out[: len(voice)] += voice[: len(out)]
    peak = np.abs(out).max()
    if peak > 0.98:
        out = np.tanh(out / peak * 1.1) * 0.95
    return out.astype(np.float32)


def write_wav(path, x):
    import wave
    x = np.clip(x, -1, 1)
    pcm = (x * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2 if x.ndim == 2 else 1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
