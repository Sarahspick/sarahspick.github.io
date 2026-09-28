"""Original sound effects, synthesized from scratch with numpy.

Nothing here is sampled from anywhere, so the library is free of third-party rights.
Run:  python3 sfx_synth.py            (writes 48 kHz stereo WAVs into ../assets/sfx)
"""
import os
import numpy as np
import soundfile as sf
from scipy import signal

SR = 48000
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "sfx")
rng = np.random.default_rng(7)


def t_axis(dur):
    return np.arange(int(dur * SR)) / SR


def noise(dur, color="white"):
    n = rng.standard_normal(int(dur * SR))
    if color == "pink":
        # Voss-McCartney style approximation via 1/f filtering in the frequency domain
        spec = np.fft.rfft(n)
        f = np.fft.rfftfreq(len(n), 1 / SR)
        f[0] = f[1]
        n = np.fft.irfft(spec / np.sqrt(f), len(n))
    return n / (np.max(np.abs(n)) + 1e-9)


def svf_bandpass(x, fc, q):
    """Time-varying state variable band-pass. fc: array of cutoff per sample."""
    y = np.zeros_like(x)
    low = band = 0.0
    damp = 1.0 / q
    for i in range(len(x)):
        f = 2 * np.sin(np.pi * min(fc[i], SR / 6) / SR)
        high = x[i] - low - damp * band
        band += f * high
        low += f * band
        y[i] = band
    return y


def svf_lowpass(x, fc, q=0.707):
    y = np.zeros_like(x)
    low = band = 0.0
    damp = 1.0 / q
    for i in range(len(x)):
        f = 2 * np.sin(np.pi * min(fc[i], SR / 6) / SR)
        high = x[i] - low - damp * band
        band += f * high
        low += f * band
        y[i] = low
    return y


def butter(x, kind, freq, order=4):
    sos = signal.butter(order, freq, btype=kind, fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def env_ad(n, attack, decay_shape=4.0):
    a = max(1, int(attack * SR))
    e = np.ones(n)
    e[:a] = np.linspace(0, 1, a) ** 2
    rest = n - a
    if rest > 0:
        e[a:] = np.exp(-decay_shape * np.linspace(0, 1, rest))
    return e


def sweep_sine(f0, f1, dur, curve="exp"):
    t = t_axis(dur)
    if curve == "exp":
        f = f0 * (f1 / f0) ** (t / dur)
    else:
        f = f0 + (f1 - f0) * (t / dur)
    phase = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(phase), f


def reverb(x, seconds=0.9, mix=0.25, predelay=0.012):
    n = int(seconds * SR)
    ir = rng.standard_normal(n) * np.exp(-6.0 * np.linspace(0, 1, n))
    ir = butter(ir, "lowpass", 6000, 2)
    ir[: int(predelay * SR)] = 0
    ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
    wet = signal.fftconvolve(np.concatenate([x, np.zeros(n)]), ir)[: len(x) + n]
    dry = np.concatenate([x, np.zeros(n)])
    return dry * (1 - mix) + wet * mix


def stereo(x, pan=None):
    """pan: None (center) or array in [-1, 1] per sample."""
    if pan is None:
        return np.stack([x, x], axis=1)
    l = np.cos((pan + 1) * np.pi / 4)
    r = np.sin((pan + 1) * np.pi / 4)
    return np.stack([x * l * 1.41, x * r * 1.41], axis=1)


def finish(x, peak_db=-1.0, fade_ms=4):
    if x.ndim == 1:
        x = stereo(x)
    f = int(fade_ms / 1000 * SR)
    if f > 0:
        x[:f] *= np.linspace(0, 1, f)[:, None]
        x[-f:] *= np.linspace(1, 0, f)[:, None]
    peak = np.max(np.abs(x)) + 1e-9
    return x / peak * (10 ** (peak_db / 20))


def save(name, x, **kw):
    os.makedirs(OUT, exist_ok=True)
    sf.write(os.path.join(OUT, name + ".wav"), finish(x, **kw), SR, subtype="PCM_16")


# ---------------------------------------------------------------- the library

def whoosh(dur=0.32, f0=350, f1=4200, q=1.3, peak_at=0.62, pan_sweep=True):
    n = int(dur * SR)
    x = noise(dur, "pink")
    t = np.linspace(0, 1, n)
    fc = f0 * (f1 / f0) ** t
    y = svf_bandpass(x, fc, q)
    e = np.where(t < peak_at, (t / peak_at) ** 2.2, np.exp(-7 * (t - peak_at) / (1 - peak_at)))
    y *= e
    pan = np.linspace(-0.8, 0.8, n) if pan_sweep else None
    return stereo(y, pan)


def reverse_swell(dur=0.55):
    y = whoosh(dur, 200, 3000, 1.0, peak_at=0.97, pan_sweep=False)
    return y


def swipe(dur=0.14):
    return whoosh(dur, 1800, 9000, 1.8, peak_at=0.45, pan_sweep=True)


def boom(dur=1.8, f_start=120, f_end=36, mid=180):
    t = t_axis(dur)
    s, _ = sweep_sine(f_start, f_end, 0.28)
    sub = np.concatenate([s, np.sin(2 * np.pi * f_end * t_axis(dur - 0.28) + 0)])
    # keep phase continuous-ish by crossfading the tail
    sub *= np.exp(-2.6 * t)
    thump = np.sin(2 * np.pi * mid * t) * np.exp(-22 * t) * 0.6
    crack = butter(noise(dur), "bandpass", [300, 3500], 2) * np.exp(-60 * t) * 0.9
    y = np.tanh(1.8 * (sub + thump + crack))
    y = reverb(y, 1.2, 0.18)[: int(dur * SR)]
    return y


def boom_meme(dur=1.6):
    """Deep 'bwomp' used for reveals: pitch-dropping tone with a strong 2nd harmonic."""
    t = t_axis(dur)
    f = 95 * (55 / 95) ** np.clip(t / 0.35, 0, 1)
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(ph) + 0.55 * np.sin(2 * ph + 0.3) + 0.2 * np.sin(3 * ph)
    y *= env_ad(len(t), 0.004, 5.5)
    y = np.tanh(2.2 * y)
    y = reverb(y, 1.4, 0.3)[: int(dur * SR)]
    return y


def bass_drop(dur=1.3):
    t = t_axis(dur)
    s, f = sweep_sine(170, 28, dur)
    y = np.tanh(2.5 * (s + 0.3 * np.sin(2 * np.pi * np.cumsum(2 * f) / SR))) * env_ad(len(t), 0.01, 2.2)
    return y


def punch(dur=0.32):
    t = t_axis(dur)
    s, _ = sweep_sine(140, 48, 0.12)
    body = np.concatenate([s, np.zeros(len(t) - len(s))]) * np.exp(-14 * t)
    crack = butter(noise(dur), "bandpass", [900, 5000], 2) * np.exp(-90 * t)
    return np.tanh(2.5 * (body + 0.7 * crack))


def pop(dur=0.09, f0=380, f1=1250):
    s, _ = sweep_sine(f0, f1, dur)
    e = env_ad(len(s), 0.002, 9)
    return s * e


def click(dur=0.025):
    t = t_axis(dur)
    return (np.sin(2 * np.pi * 3200 * t) * 0.6 + butter(noise(dur), "highpass", 2500, 2)) * np.exp(-220 * t)


def ding(dur=1.4, f0=1318.5):
    t = t_axis(dur)
    parts = [(1.0, 1.0, 3.2), (2.0, 0.35, 4.5), (2.76, 0.28, 6.0), (5.40, 0.10, 9.0), (8.93, 0.05, 12.0)]
    y = sum(a * np.sin(2 * np.pi * f0 * r * t + i) * np.exp(-d * t) for i, (r, a, d) in enumerate(parts))
    y *= env_ad(len(t), 0.002, 0.0001)
    return reverb(y, 1.0, 0.2)[: len(t)]


def success(dur=0.75):
    a = ding(0.75, 1318.5)
    b = ding(0.75, 1975.5)
    off = int(0.11 * SR)
    y = np.zeros(int(dur * SR) + off)
    y[: len(a)] += a * 0.8
    y[off: off + len(b)] += b
    return y[: int(dur * SR)]


def error_buzz(dur=0.5):
    t = t_axis(dur)
    sq = signal.square(2 * np.pi * 110 * t) + signal.square(2 * np.pi * 116.5 * t)
    y = butter(sq, "lowpass", 2400, 2) * (0.75 + 0.25 * np.sin(2 * np.pi * 18 * t))
    e = np.ones_like(t)
    e[-int(0.06 * SR):] = np.linspace(1, 0, int(0.06 * SR))
    return y * e


def riser(dur=2.0):
    t = t_axis(dur)
    n = len(t)
    ns = noise(dur)
    fc = 300 * (9000 / 300) ** (t / dur)
    ny = svf_bandpass(ns, fc, 0.9)
    f = 180 * (1400 / 180) ** ((t / dur) ** 1.4)
    saw = signal.sawtooth(2 * np.pi * np.cumsum(f) / SR) + signal.sawtooth(2 * np.pi * np.cumsum(f * 1.007) / SR)
    saw = butter(saw, "lowpass", 5000, 2) * 0.35
    e = (t / dur) ** 2.4
    y = (ny + saw) * e
    return stereo(y, 0.5 * np.sin(2 * np.pi * 3 * t) * (t / dur))


def record_scratch(dur=0.5):
    """Tape/vinyl scratch: a harmonic-rich tone read back with a back-and-forth playback rate."""
    base_dur = 1.0
    bt = t_axis(base_dur)
    src = (signal.sawtooth(2 * np.pi * 220 * bt) * 0.5 + noise(base_dur) * 0.5)
    src = butter(src, "bandpass", [150, 4000], 2)
    t = t_axis(dur)
    rate = 1.8 * np.sin(2 * np.pi * 2.2 * t) * np.exp(-1.5 * t) + 0.2
    pos = np.cumsum(rate) / SR * SR * 0.35 + 0.3 * SR
    pos = np.clip(pos, 0, len(src) - 2)
    y = np.interp(pos, np.arange(len(src)), src)
    y *= np.abs(rate) / (np.max(np.abs(rate)) + 1e-9)
    return y * env_ad(len(t), 0.003, 2.5)


def tape_stop(dur=0.7):
    """Pitch falls to zero: signals a slow-motion replay."""
    t = t_axis(dur)
    f = 440 * (1 - t / dur) ** 1.6 + 20
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = signal.sawtooth(ph) * 0.4 + np.sin(ph * 0.5) * 0.6
    y = butter(y, "lowpass", 1800, 2)
    return y * (1 - t / dur) ** 0.6


def rewind(dur=0.8):
    t = t_axis(dur)
    chirps = np.zeros_like(t)
    rate = 14 + 30 * (t / dur)
    ph = np.cumsum(rate) / SR
    gate = (np.sin(2 * np.pi * ph) > 0.2).astype(float)
    f = 900 + 2500 * (t / dur)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR)
    chirps = tone * gate
    chirps = butter(chirps, "bandpass", [400, 6000], 2)
    y = chirps * 0.6 + butter(noise(dur), "highpass", 3000, 2) * 0.15
    return y * env_ad(len(t), 0.02, 0.8)


def shutter(dur=0.26):
    t = t_axis(dur)
    y = np.zeros_like(t)
    for start, amp in [(0.0, 1.0), (0.07, 0.7)]:
        s = int(start * SR)
        seg = butter(noise(0.03), "bandpass", [1500, 7000], 2) * np.exp(-160 * t_axis(0.03))
        y[s: s + len(seg)] += seg * amp
    return y


def glitch(dur=0.36):
    y = np.zeros(int(dur * SR))
    pos = 0
    while pos < len(y):
        seg = int(rng.uniform(0.012, 0.05) * SR)
        f = rng.uniform(80, 2000)
        tt = np.arange(seg) / SR
        kind = rng.integers(3)
        if kind == 0:
            s = signal.square(2 * np.pi * f * tt)
        elif kind == 1:
            s = rng.standard_normal(seg)
        else:
            s = np.sin(2 * np.pi * f * tt)
        s = np.round(s * 4) / 4  # bit crush
        y[pos: pos + seg] = s[: len(y) - pos] * rng.uniform(0.4, 1.0)
        pos += seg
    return butter(y, "lowpass", 7000, 2)


def tick(dur=0.06):
    t = t_axis(dur)
    return (np.sin(2 * np.pi * 1850 * t) + 0.4 * np.sin(2 * np.pi * 3700 * t)) * np.exp(-90 * t) + \
        butter(noise(dur), "highpass", 4000, 2) * np.exp(-300 * t) * 0.5


def heartbeat(dur=1.0):
    t = t_axis(dur)
    y = np.zeros_like(t)
    for start, amp in [(0.0, 1.0), (0.24, 0.75)]:
        s = int(start * SR)
        tt = t_axis(0.22)
        beat = np.sin(2 * np.pi * 55 * tt) * np.exp(-18 * tt) + np.sin(2 * np.pi * 110 * tt) * np.exp(-30 * tt) * 0.3
        y[s: s + len(beat)] += beat * amp
    return np.tanh(2 * y)


def drum_roll(dur=1.8):
    t = t_axis(dur)
    y = np.zeros_like(t)
    time = 0.0
    while time < dur - 0.05:
        rate = 9 + 22 * (time / dur)
        s = int(time * SR)
        hit_d = 0.07
        tt = t_axis(hit_d)
        hit = butter(noise(hit_d), "bandpass", [800, 6000], 2) * np.exp(-45 * tt) + np.sin(2 * np.pi * 210 * tt) * np.exp(-40 * tt) * 0.5
        amp = 0.35 + 0.65 * (time / dur) ** 1.5
        y[s: s + len(hit)] += hit[: len(y) - s] * amp
        time += 1.0 / rate
    return y


def air_horn(dur=0.9):
    t = t_axis(dur)
    bend = 1 - 0.03 * np.exp(-8 * t)
    y = sum(signal.sawtooth(2 * np.pi * np.cumsum(f * bend) / SR) for f in (440, 443, 554, 557, 659))
    y = butter(y, "bandpass", [300, 4000], 2)
    e = np.ones_like(t)
    e[:int(0.02 * SR)] = np.linspace(0, 1, int(0.02 * SR))
    e[-int(0.1 * SR):] = np.linspace(1, 0, int(0.1 * SR))
    return np.tanh(1.5 * y) * e


def camera_zoom(dur=0.35):
    """Short servo-like zoom: used under punch-in zooms."""
    t = t_axis(dur)
    f = 600 + 900 * (t / dur)
    y = signal.sawtooth(2 * np.pi * np.cumsum(f) / SR) * 0.3 + butter(noise(dur), "bandpass", [2000, 6000], 2) * 0.3
    return butter(y, "lowpass", 5000, 2) * np.sin(np.pi * t / dur)


def riser_soft(dur=1.6):
    """Gentle build-up: filtered air + a low gliding tone, no harsh top end."""
    t = t_axis(dur)
    n = len(t)
    air = svf_bandpass(noise(dur, "pink"), 180 * (2400 / 180) ** (t / dur), 0.8)
    f = 90 * (360 / 90) ** ((t / dur) ** 1.3)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.3 * np.sin(4 * np.pi * np.cumsum(f) / SR)
    y = butter(air * 0.8 + tone * 0.35, "lowpass", 3200, 4) * (t / dur) ** 2.2
    tail = int(0.04 * SR)
    y[-tail:] *= np.linspace(1, 0, tail)
    return stereo(y, 0.25 * np.sin(2 * np.pi * 1.5 * t) * (t / dur))


def sub_hit(dur=1.1):
    """Deep sub thump that you feel more than hear."""
    t = t_axis(dur)
    f = 36 + 44 * np.exp(-t * 9)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.2)
    knock = butter(noise(dur), "lowpass", 900, 2) * np.exp(-t * 70) * 0.5
    return np.tanh(2.0 * (body + knock))


def impact_deep(dur=2.4):
    """Cinematic impact with a long dark tail."""
    t = t_axis(dur)
    s, _ = sweep_sine(95, 32, 0.4)
    sub = np.concatenate([s, np.sin(2 * np.pi * 32 * t_axis(dur - 0.4))]) * np.exp(-1.9 * t)
    thump = np.sin(2 * np.pi * 140 * t) * np.exp(-26 * t) * 0.55
    crack = butter(noise(dur), "bandpass", [200, 2400], 2) * np.exp(-45 * t) * 0.7
    y = np.tanh(1.7 * (sub + thump + crack))
    y = butter(reverb(y, 1.8, 0.28)[: len(t)], "lowpass", 5000, 2)
    return y


LIBRARY = {
    "whoosh": lambda: whoosh(),
    "whoosh_slow": lambda: whoosh(0.62, 220, 2600, 1.0, 0.6),
    "reverse_swell": reverse_swell,
    "swipe": swipe,
    "boom": boom,
    "boom_meme": boom_meme,
    "bass_drop": bass_drop,
    "punch": punch,
    "pop": pop,
    "pop_low": lambda: pop(0.1, 220, 640),
    "click": click,
    "ding": ding,
    "success": success,
    "error": error_buzz,
    "riser": riser,
    "riser_short": lambda: riser(1.1),
    "record_scratch": record_scratch,
    "tape_stop": tape_stop,
    "rewind": rewind,
    "shutter": shutter,
    "glitch": glitch,
    "tick": tick,
    "heartbeat": heartbeat,
    "drum_roll": drum_roll,
    "air_horn": air_horn,
    "zoom": camera_zoom,
    # added later: keep at the end so the sounds above stay bit-identical (shared rng)
    "riser_soft": riser_soft,
    "sub_hit": sub_hit,
    "impact_deep": impact_deep,
}

if __name__ == "__main__":
    for name, fn in LIBRARY.items():
        save(name, fn())
        print("wrote", name)
