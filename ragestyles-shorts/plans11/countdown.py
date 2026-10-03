"""Fast results countdown (owner's c1 v2 rules, 2026-10-01): each place opens on a short shot with "5TH PLACE" for
about 0.45 s, then the cut, the announcer says only the name, zoom punch + flash + boom; 5th to 3rd fast; no fade on
the first frame; captions drop to y 0.64 where a face would sit under the centre line.
Owner (2026-10-03): pose then medal shot is hard on the eyes; the cut after the label stays on the same pose, zoomed in,
athlete always centred with his head fully visible (place() and zoom_in())."""
import sys

sys.path.insert(0, "plans11")
from newscommon import Short, Cutter  # noqa: E402,F401


def zoom_in(cx, head_y, d, cx_end=None, zoom=1.3):
    """Shot keys for a push in on one athlete: centred (cx, or a pan to cx_end), head about a quarter down the box."""
    w, h = 0.42 / zoom, 1.0 / zoom          # crop size of the 3:4 box in a 16:9 source at this zoom
    cl = lambda v, half: round(min(max(v, half), 1 - half), 3)
    cy = cl(head_y - 0.25 * h + h / 2, h / 2)
    a, b = cl(cx, w / 2), cl(cx if cx_end is None else cx_end, w / 2)
    return {"cx": a, "cy": cy, "zoom": (zoom, zoom + 0.04),
            "path": [[0, zoom, a, cy], [d, zoom + 0.04, b, cy]]}


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

    def place(self, label, t0, cx, name, head_y, d, text, cx_end=None, zoom=1.3, y=0.66, pre_d=0.45):
        """Owner (2026-10-03): label over the athlete's pose, then the cut stays on the same pose (the very next
        frame of the source) zoomed in, athlete centred and the head clear in the top quarter. t0 = source second of
        the pose, cx = athlete's x in the source frame (cx_end if he drifts), head_y = his head's y in the source frame,
        name = (a, b) announcer seconds."""
        o = self.o
        t = o.t
        self.shot(t0, pre_d, cx=min(max(cx, 0.21), 0.79), cy=0.5, zoom=(1.0, 1.02))
        self.big(t, pre_d, label)
        if name:
            self.say(name[0], name[1], o.t)
        s = self.shot(t0 + pre_d, d, **zoom_in(cx, head_y, d, cx_end, zoom))
        o.hit(s, 0.0, zoom=1.06, amount=0.55, db=-2)
        self.big(o.t - d, d, text, y)
        return s

    def save(self):
        self.o.save(open_fade=0.0)
