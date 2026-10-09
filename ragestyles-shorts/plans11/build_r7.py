"""r7: Ronnie Coleman at the 2005 Mr. Olympia walks out as a king: crown, sceptre, a red and white royal cape. He drops
the cape and the crown, hits the poses, and wins his 8th straight title, tying Lee Haney's record
(en.wikipedia.org/wiki/2005_Mr._Olympia). Pairs with r6 (2006, Moses). No talking: the arena sound runs under it.
Source: bilibili BV1eP4y1u7ee "4K修复！2005年罗尼祖师爷王者形象回归！最后一冠！" (杀局长的凯恩, AI restored, 1920x1080 with
the picture in x 300..1620 px; the broadcast name bar at the bottom 26..41 s is avoided),
downloaded with /tmp/claude-0/bili.py. Shots picked on a 2 s contact sheet.
Run: python3 plans11/build_r7.py && python3 pipeline/bench.py plans11/r7_ronnie_king.json
"""
import sys

sys.path.insert(0, "plans11")
from newscommon import Short  # noqa: E402

V = "bl_BV1eP4y1u7ee"
o = Short("r7_ronnie_king", "Ronnie came out\nas a *king* :crown:",
          "Ronnie Coleman came out as a king 👑 #shorts", folder="plans11")
INFO = dict(style="big", y=0.86)


def sh(t_in, dur, cx=0.5, cy=0.45, zoom=(1.1, 1.15), db=-6, **k):
    return o.shot(V, t_in, dur, cx=cx, cy=cy, zoom=zoom, db=db, af="film", **k)


# 1. hook: the crown, close
s = sh(20.0, 1.4, cx=0.5, zoom=(1.0, 1.06), path=[[0, 1.0, 0.5, 0.45], [1.4, 1.06, 0.44, 0.45]])
o.hit(s, 0.05, zoom=1.05, amount=0.5, db=-3)
o.cap(0.0, 2.6, "2005 MR. OLYMPIA\n*GOING FOR #8*", **INFO)
sh(10.0, 1.3)                                                    # the cape at the back of the stage
sh(43.0, 1.4)                                                    # standing in the cape, sceptre
s = sh(50.0, 1.6)                                                # the cape comes off
o.hit(s, 0.6, zoom=1.04, amount=0.35, db=-6, sound="punch")
o.cap(s["_t0"], 1.6, "THEN THE *CAPE* COMES OFF...", **INFO)
s = sh(56.0, 1.6)                                                # front double biceps, cape on the floor
o.hit(s, 0.1, zoom=1.08, amount=0.55, db=-1)
sh(84.0, 1.4, zoom=(1.0, 1.06))                                  # most muscular, close
sh(130.5, 1.3, zoom=(1.0, 1.06))                                 # arms up, close
sh(133.0, 1.3, zoom=(1.0, 1.06))
s = sh(138.0, 1.6, zoom=(1.05, 1.1))                             # the splits
o.hit(s, 0.2, zoom=1.06, amount=0.45, db=-3)
o.cap(s["_t0"] + 0.2, 1.4, "THE *SPLITS* :exploding-head:", **INFO)
sh(165.5, 1.6)                                                   # back double biceps
s = sh(65.0, 2.4)                                                # front double biceps
o.hit(s, 0.2, zoom=1.08, amount=0.55, db=-1)
o.sound(s["_t0"] + 0.2, "crowd_erupt", db=-12)
o.cap(s["_t0"] + 0.2, 2.2, "8TH TITLE IN A ROW :crown:", **INFO)
o.save(open_fade=0.0)
