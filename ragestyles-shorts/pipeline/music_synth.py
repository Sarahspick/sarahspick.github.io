"""Original background beds, synthesized like a drum machine (no samples, no generative AI).

Three moods, each an 8-bar loop:
  drive    140 BPM, half-time trap/phonk feel, 808 + cowbell riff   (hype, PR attempts)
  tension   90 BPM, dark pad + slow kick                             (suspense, story build)
  bounce   104 BPM, plucky major-key riff + claps                    (funny / light topics)
Run:  python3 music_synth.py   -> ../assets/music/<mood>.wav
"""
import os
import numpy as np
import soundfile as sf
from scipy import signal

SR = 48000
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work", "music_ref")  # loudness reference only
rng = np.random.default_rng(11)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def lp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, "lowpass", fs=SR, output="sos"), x)


def hp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, "highpass", fs=SR, output="sos"), x)


def bp(x, lo, hi, order=2):
    return signal.sosfilt(signal.butter(order, [lo, hi], "bandpass", fs=SR, output="sos"), x)


def t_of(d):
    return np.arange(int(d * SR)) / SR


def kick(d=0.45, f0=160, f1=46, punch=1.0):
    t = t_of(d)
    f = f1 + (f0 - f1) * np.exp(-t * 38)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
    clickn = hp(rng.standard_normal(len(t)), 3000) * np.exp(-t * 400) * 0.25 * punch
    return np.tanh(1.6 * (body + clickn))


def bass808(d, note, glide_from=None, drive=2.2):
    t = t_of(d)
    f_target = midi(note)
    if glide_from is not None:
        f = f_target + (midi(glide_from) - f_target) * np.exp(-t * 18)
    else:
        f = np.full_like(t, f_target)
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(ph) + 0.25 * np.sin(2 * ph)
    e = np.minimum(1, t / 0.005) * np.exp(-t * 1.2)
    e[-int(0.02 * SR):] *= np.linspace(1, 0, int(0.02 * SR))
    return np.tanh(drive * y * e) * 0.8


def snare(d=0.3, tone=190, bright=1.0):
    t = t_of(d)
    n = bp(rng.standard_normal(len(t)), 900, 9000) * np.exp(-t * 18) * bright
    b = np.sin(2 * np.pi * tone * t) * np.exp(-t * 30) * 0.6
    return np.tanh(1.3 * (n + b))


def clap(d=0.3):
    t = t_of(d)
    y = np.zeros_like(t)
    for k, off in enumerate([0, 0.011, 0.022]):
        s = int(off * SR)
        seg = bp(rng.standard_normal(len(t) - s), 1000, 7000) * np.exp(-t[: len(t) - s] * (60 if k < 2 else 16))
        y[s:] += seg * (0.7 if k < 2 else 1.0)
    return y * 0.8


def hat(d=0.06, open_=False):
    t = t_of(d if not open_ else 0.25)
    sq = sum(signal.square(2 * np.pi * f * t) for f in (3140, 4410, 5870, 6930, 8100, 9570))
    y = hp(sq + rng.standard_normal(len(t)) * 2, 7000) * np.exp(-t * (60 if not open_ else 12))
    return y * 0.12


def cowbell(d, note):
    t = t_of(d)
    ratio = midi(note) / 587.0
    y = signal.square(2 * np.pi * 587 * ratio * t) + signal.square(2 * np.pi * 845 * ratio * t)
    y = bp(y, 400 * ratio, 3500 * ratio)
    e = np.exp(-t * 9) * 0.8 + np.exp(-t * 40) * 0.4
    return y * e * 0.35


def pluck(d, note, bright=4000):
    t = t_of(d)
    f = midi(note)
    y = signal.square(2 * np.pi * f * t, 0.3) * 0.5 + signal.sawtooth(2 * np.pi * f * 1.004 * t) * 0.5
    y = lp(y, bright) * np.exp(-t * 7)
    return y * 0.35


def pad(d, notes, cutoff=1400):
    t = t_of(d)
    y = np.zeros_like(t)
    for n in notes:
        for det in (-0.08, 0.0, 0.07):
            y += signal.sawtooth(2 * np.pi * midi(n + det) * t + rng.uniform(0, 6))
    y = lp(y, cutoff, 4) / (len(notes) * 3)
    e = np.minimum(1, t / 0.4) * np.minimum(1, (t[-1] - t + 1e-3) / 0.3)
    return y * e * 0.8


class Track:
    def __init__(self, bpm, bars):
        self.bpm = bpm
        self.beat = 60.0 / bpm
        self.n = int(bars * 4 * self.beat * SR)
        self.bus = {k: np.zeros(self.n) for k in ("drums", "bass", "music")}

    def add(self, bus, x, beat_pos, gain=1.0):
        s = int(beat_pos * self.beat * SR)
        if s >= self.n:
            return
        e = min(self.n, s + len(x))
        self.bus[bus][s:e] += x[: e - s] * gain

    def mix(self, levels):
        y = sum(self.bus[k] * levels.get(k, 1.0) for k in self.bus)
        # glue: soft-knee compression by envelope follower + saturation
        env = signal.sosfilt(signal.butter(1, 8, "lowpass", fs=SR, output="sos"), np.abs(y))
        gain = 1.0 / (1.0 + 1.2 * np.maximum(0, env - 0.25))
        y = np.tanh(1.2 * y * gain)
        # simple stereo: widen music bus with a short delay on the right
        right = y.copy()
        d = int(0.011 * SR)
        mus = self.bus["music"] * levels.get("music", 1.0)
        right[d:] += 0.25 * mus[:-d]
        left = y + 0.25 * mus
        st = np.stack([left, right], axis=1)
        return st / (np.max(np.abs(st)) + 1e-9) * 0.89


def drive():
    tr = Track(140, 8)
    # F minor. 808 line per bar (beats), note, length
    bass_line = [(0, 29, 1.5), (1.5, 29, 1.0), (2.5, 32, 1.5), (0, 29, 1.5), (1.5, 29, 1.0), (2.5, 27, 1.5)]
    riff = [77, 80, 82, 80, 77, 84, 82, 80]  # cowbell riff (F5 Ab5 Bb5 Ab5 F5 C6 Bb5 Ab5)
    for bar in range(8):
        b0 = bar * 4
        # half-time drums: kick on 1 and 2.75, snare on 3
        tr.add("drums", kick(), b0 + 0)
        tr.add("drums", kick(0.3), b0 + 1.75, 0.8)
        if bar % 2 == 1:
            tr.add("drums", kick(0.3), b0 + 3.5, 0.7)
        tr.add("drums", snare(), b0 + 2, 0.9)
        tr.add("drums", clap(), b0 + 2, 0.5)
        for s in range(8):
            tr.add("drums", hat(), b0 + s * 0.5, 0.9 if s % 2 == 0 else 0.6)
        if bar % 4 == 3:  # hat roll at the end of each phrase
            for k in range(8):
                tr.add("drums", hat(0.03), b0 + 3 + k * 0.125, 0.5 + k * 0.05)
        pat = bass_line[:3] if bar % 2 == 0 else bass_line[3:]
        prev = None
        for pos, note, ln in pat:
            tr.add("bass", bass808(ln * tr.beat, note, glide_from=prev), b0 + pos)
            prev = note
        if bar >= 2:
            for k, n in enumerate(riff):
                tr.add("music", cowbell(0.35, n), b0 + k * 0.5, 0.9 if k % 2 == 0 else 0.7)
    return tr.mix({"drums": 1.0, "bass": 0.9, "music": 0.55})


def tension():
    tr = Track(90, 8)
    chords = [[53, 56, 60], [49, 53, 56], [56, 60, 63], [51, 55, 58]]  # Fm Db Ab Eb
    for bar in range(8):
        b0 = bar * 4
        tr.add("music", pad(4 * tr.beat, chords[bar % 4], 900 + 120 * bar), b0, 0.9)
        tr.add("bass", bass808(3.5 * tr.beat, chords[bar % 4][0] - 24, drive=1.5), b0, 0.8)
        tr.add("drums", kick(0.6, 120, 40), b0)
        if bar >= 2:
            tr.add("drums", kick(0.4, 120, 40), b0 + 2.5, 0.6)
            tr.add("drums", snare(0.5, 170, 0.8), b0 + 2, 0.55)
            for s in range(4):
                tr.add("drums", hat(0.05), b0 + s + 0.5, 0.5)
        # ticking pulse keeps suspense moving
        for s in range(8):
            tr.add("drums", hat(0.02), b0 + s * 0.5, 0.25)
    return tr.mix({"drums": 0.9, "bass": 0.8, "music": 0.9})


def bounce():
    tr = Track(104, 8)
    riff = [(0, 72), (0.5, 76), (1, 79), (1.75, 76), (2.5, 74), (3, 72), (3.5, 67)]  # C major pluck riff
    riff2 = [(0, 69), (0.5, 72), (1, 76), (1.75, 72), (2.5, 74), (3, 76), (3.5, 79)]
    roots = [48, 45, 41, 43]  # C Am F G
    for bar in range(8):
        b0 = bar * 4
        tr.add("drums", kick(0.35, 140, 55, 0.6), b0)
        tr.add("drums", kick(0.3, 140, 55, 0.6), b0 + 2.5, 0.7)
        tr.add("drums", clap(), b0 + 1, 0.8)
        tr.add("drums", clap(), b0 + 3, 0.8)
        for s in range(8):
            tr.add("drums", hat(0.04), b0 + s * 0.5 + 0.25 * (s % 2 == 1) * 0.2, 0.6)
        tr.add("bass", bass808(1.8 * tr.beat, roots[bar % 4] - 12, drive=1.3), b0, 0.7)
        tr.add("bass", bass808(1.2 * tr.beat, roots[bar % 4] - 12, drive=1.3), b0 + 2.5, 0.6)
        for pos, n in (riff if bar % 2 == 0 else riff2):
            tr.add("music", pluck(0.4, n), b0 + pos, 0.9)
    return tr.mix({"drums": 0.9, "bass": 0.8, "music": 0.8})


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, fn in (("drive", drive), ("tension", tension), ("bounce", bounce)):
        y = fn()
        sf.write(os.path.join(OUT, name + ".wav"), y, SR, subtype="PCM_16")
        print("wrote", name, round(len(y) / SR, 2), "s")
