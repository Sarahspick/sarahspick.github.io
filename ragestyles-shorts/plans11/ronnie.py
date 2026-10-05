"""Shared builder for the Ronnie Coleman legend shorts (2026-10-05). Source: the documentary "Ronnie Coleman: The King"
(The Vladar Company, 2018), archive.org item ronnie-coleman-the-king, 1280x720, work/youtube/ia_ronnie_king.mp4.
Music runs under the interviews, so voices come from Demucs vocals of each segment (work/youtube/rk1.wav 2765 to
2965 s, rk2 3140 to 3245, rk3 3905 to 4105, rk4 5110 to 5275), words from medium.en (work/tr/rkN.json).
The film cuts to whoever is talking, so by default a piece's picture is the same source seconds as its voice (lip
synced); archive stage footage is laid over a voice with an explicit t_in. Each shot is centred on the face
found in it (plans11/faces.py) unless framing keys are given."""
import sys

sys.path.insert(0, "plans11")
from newscommon import Short, Speech, Cutter, words, word_captions  # noqa: E402,F401
from faces import framing, cuts  # noqa: E402

V = "ia_ronnie_king"
SEG = {"rk1": 2765.0, "rk2": 3140.0, "rk3": 3905.0, "rk4": 5110.0, "rk5": 5565.0}
FRAME = dict(cx=0.5, cy=0.45, zoom=(1.05, 1.1))      # interviews sit centre frame


class Doc:
    def __init__(self, sid, title, yt_title, seg):
        self.o = Short(sid, title, yt_title, folder="plans11")
        self.c = Cutter(self.o)
        self.sp = Speech(self.o, [(seg + ".wav", SEG[seg], SEG[seg] + 210.0)], words(seg))

    def say(self, a, b, t_in=None, gap=0.05, hit=None, tail=0.05, **k):
        """A piece of voice; the picture is the same source seconds unless t_in is given."""
        o = self.o
        t = self.sp.add(a, b, o.t + gap)
        src_t, d = (a if t_in is None else t_in), round(t + b - a + tail - o.t, 2)
        if k:
            s = self.c.v(V, src_t, d, **k)
        else:   # split at the film's own camera cuts, centre the face in each part (plans11/faces.py)
            edges = [src_t] + cuts(V, src_t, src_t + d) + [src_t + d]
            for x0, x1 in zip(edges, edges[1:]):
                s = self.c.v(V, x0, round(x1 - x0, 2), **(framing(V, x0, x1 - x0) or FRAME))
            if len(edges) > 2:
                s = self.o.shots[-(len(edges) - 1)]    # hits are timed from the first part
        if hit is not None:
            o.hit(s, round(t + hit - a - s["_t0"], 2), zoom=1.08, amount=0.5, db=-3)
        return t

    def big(self, t, d, text, y=0.86):
        self.o.cap(t, d, text, style="big", y=y)

    def save(self, force=()):
        self.o.caps += word_captions(self.sp.words, y=0.72, style="wordcap", palette=["*", "~"], force=set(force))
        self.o.save(open_fade=0.0)
