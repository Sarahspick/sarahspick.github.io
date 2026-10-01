"""Fast results countdown (owner's c1 v2 rules, 2026-10-01): each place opens on a short shot with "5TH PLACE" for
about 0.45 s, then the cut, the announcer says only the name, zoom punch + flash + boom; 5th to 3rd fast; no fade on
the first frame; captions drop to y 0.64 where a face would sit under the centre line."""
import sys

sys.path.insert(0, "plans11")
from newscommon import Short, Cutter  # noqa: E402,F401


class Countdown:
    def __init__(self, sid, title, yt_title, src, vox):
        self.o = Short(sid, title, yt_title, folder="plans11")
        self.c = Cutter(self.o)
        self.src, self.vox = src, vox

    def say(self, a, b, t, db=4):
        self.o.vox(self.vox, a, round(b - a, 2), t, db=db)

    def big(self, t, d, text, y=0.5):
        self.o.cap(t, d, text, style="big", y=y)

    def shot(self, t_in, dur, **k):
        k.setdefault("zoom", (1.0, 1.04))
        k.setdefault("cy", 0.5)
        return self.c.v(self.src, t_in, dur, **k)

    def place(self, label, pre_in, pre_cx, name, shot_in, shot_cx, d, text, y=0.5, pre_d=0.45):
        """label over a short shot, then the cut with only the name (name = (a, b) source seconds, or None)."""
        o = self.o
        t = o.t
        self.shot(pre_in, pre_d, cx=pre_cx, zoom=(1.0, 1.02))
        self.big(t, pre_d, label)
        if name:
            self.say(name[0], name[1], o.t)
        s = self.shot(shot_in, d, cx=shot_cx)
        o.hit(s, 0.0, zoom=1.14, amount=0.55, db=-2)
        self.big(o.t - d, d, text, y)
        return s

    def save(self):
        self.o.save(open_fade=0.0)
