"""Shared helpers for the plans11 news shorts (2026 Olympia week). Voices come straight from the downloaded
interviews (no music under them, so no Demucs); words are faster-whisper medium.en (work/tr/<id>.json)."""
import json
import sys

sys.path.insert(0, "plans10")
sys.path.insert(0, "pipeline")
from rscommon import Short, Speech  # noqa: E402,F401
from wordcaps import word_captions  # noqa: E402,F401


def words(vid):
    """Whisper words of work/tr/<vid>.json; split tokens ("pre" "-workout", "$20" ",000", "125" "%") are joined back."""
    out = []
    for s in json.load(open(f"work/tr/{vid}.json")):
        for w in s["words"]:
            t = w["w"].strip()
            if out and t[:1] in ("-", ",", "%", "'") and w["s"] - out[-1][1] < 0.05:
                out[-1] = (out[-1][0], w["e"], out[-1][2] + t)
            else:
                out.append((w["s"], w["e"], t))
    return out


def speech(o, vid, dur):
    return Speech(o, [(vid + ".mp4", 0.0, dur)], words(vid))


class Cutter:
    """Picture helpers on one Short: v() lays a silent shot, until() and hit_at() work in output seconds, sync()
    runs a voice source's picture in step with the piece of that Speech playing at the current output time."""

    def __init__(self, o):
        self.o = o

    def v(self, src, t_in, dur, **k):
        k.setdefault("zoom", (1.05, 1.1))
        k.setdefault("audio", False)
        return self.o.shot(src, t_in, round(dur, 2), **k)

    def until(self, t_out):
        return round(t_out - self.o.t, 2)

    def hit_at(self, s, t_out, **k):
        self.o.hit(s, round(t_out - s["_t0"], 2), **k)

    def sync(self, sp, src, t_end, **k):
        o = self.o
        for a, b, t in sp.maps:
            if t - 0.35 <= o.t <= t + (b - a) + 0.01:   # may open a moment before the voice
                return self.v(src, a + (o.t - t), self.until(t_end), **k)
        raise ValueError(o.t)
