"""s4: Bodybuilders in suits, v3 (owner 2026-10-09: "only shots where the muscular body in the suit is clearly seen, with
names"). Every shot is a man in a suit with the whole upper body in frame, one name per shot.
Source: bilibili BV1PR4y1576i "当健美运动员穿上西装，是一种什么体验？" (健身动机, 1920x1080, a slideshow of photos and
clips with slow pans), downloaded with /tmp/claude-0/bili.py (bilibili playurl API). The uploader's marks: "健身动机
bilibili" top right (y < 0.07) and a small logo bottom centre (y 0.87..0.93): crops use zoom >= 1.1 with cy 0.55 so the
top mark is cut (cy 0.46 where a head sits at the top of the photo, the mark is outside those crops) and the name caption sits over the logo. Its music is not used.
Shots (source seconds, camera cuts from plans11/faces.cuts): Ronnie Coleman dancing in a suit 3.0..4.6, Nasser El Sonbaty in the turquoise suit 61.8..64.8, Jay Cutler 24.9..27.9, Phil Heath
49.7..50.9 and Kai Greene 51.0..52.2 (same photo, FLEX event), Arnold Schwarzenegger and Ronnie on stage 82.0..85.0.
Run: python3 plans11/build_s4.py && python3 pipeline/bench.py plans11/s4_suits_names.json
"""
import sys

sys.path.insert(0, "plans11")
from newscommon import Short  # noqa: E402

V = "bl_BV1PR4y1576i"
o = Short("s4_suits_names", "Bodybuilders in suits\nhit *different* :fire:",
          "Bodybuilders in suits hit different 🔥 #shorts", folder="plans11")
NAME = dict(style="big", y=0.86)


def suit(t_in, dur, cx, name, zoom=1.12, cx_end=None, hit=True, cy=0.55):
    k = {"path": [[0, zoom, cx, cy], [dur, zoom + 0.04, cx if cx_end is None else cx_end, cy]]}
    s = o.shot(V, t_in, dur, cx=cx, cy=cy, zoom=(zoom, zoom + 0.05), audio=False, **k)
    o.cap(s["_t0"], dur, name, **NAME)
    if hit:
        o.hit(s, 0.05, zoom=1.05, amount=0.45, db=-4)
    return s


o.sound(0.0, "crowd_tense", db=-20)
suit(3.0, 1.6, 0.55, "RONNIE *COLEMAN*")                         # dancing in a suit
suit(61.9, 2.8, 0.45, "NASSER *EL SONBATY*", zoom=1.1, cy=0.46)                     # the turquoise suit
suit(25.0, 2.8, 0.42, "JAY *CUTLER*")
suit(49.75, 1.15, 0.5, "PHIL *HEATH*", cx_end=0.66)
suit(51.05, 1.15, 0.42, "KAI *GREENE*", cx_end=0.5)
s = suit(82.1, 2.8, 0.46, "ARNOLD & *RONNIE* :crown:", zoom=1.1, cy=0.46)
o.sound(s["_t0"] + 0.05, "crowd_erupt", db=-12)
o.save(open_fade=0.0)
