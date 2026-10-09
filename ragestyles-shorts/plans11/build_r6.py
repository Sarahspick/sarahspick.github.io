"""r6: Ronnie Coleman at the 2006 Mr. Olympia, going for a 9th straight title, walks out dressed as Moses: hooded robe,
white beard, the stone tablets raised over his head. He drops the tablets, throws off the robe, rips off the beard,
and hits the poses. Jay Cutler won that night; Ronnie was 2nd (en.wikipedia.org/wiki/2006_Mr._Olympia).
No talking: the arena sound runs under it, short info captions, ElevenLabs hits.
Source: bilibili BV1MF4114732 "4K修复！2006年祖师爷上帝降临冲击九冠王然后就输了" (杀局长的凯恩, AI restored, 1920x1080 with
the picture in x 300..1620 px), downloaded with /tmp/claude-0/bili.py. Shots picked on a 1 s contact sheet, each inside
one camera shot.
Run: python3 plans11/build_r6.py && python3 pipeline/bench.py plans11/r6_ronnie_moses.json
"""
import sys

sys.path.insert(0, "plans11")
from newscommon import Short  # noqa: E402

V = "bl_BV1MF4114732"
o = Short("r6_ronnie_moses", "Ronnie came out\nas *Moses* :face-exhaling:",
          "Ronnie Coleman came out as Moses 😳 #shorts", folder="plans11")
INFO = dict(style="big", y=0.86)


def sh(t_in, dur, cx=0.5, cy=0.5, zoom=(1.0, 1.05), db=-6, **k):
    return o.shot(V, t_in, dur, cx=cx, cy=cy, zoom=zoom, db=db, af="film", **k)


# 1. hook: the tablets go up
s = sh(35.8, 1.4, cy=0.45, zoom=(1.05, 1.1))
o.hit(s, 0.05, zoom=1.05, amount=0.5, db=-3)
o.cap(0.0, 2.6, "2006 MR. OLYMPIA\n*GOING FOR #9*", **INFO)
sh(25.0, 1.2, zoom=(1.0, 1.06))                                  # the robe in the smoke
sh(33.4, 1.3, cy=0.45, zoom=(1.1, 1.16))                         # the beard, close
s = sh(39.0, 1.3)                                                # drops the tablets
o.hit(s, 0.4, zoom=1.04, amount=0.35, db=-6, sound="punch")
s = sh(46.2, 1.6)                                                # the robe comes off
o.cap(s["_t0"], 1.6, "UNDER THE *ROBE*...", **INFO)
sh(56.2, 1.4, cy=0.45, zoom=(1.0, 1.06))                         # beard and traps
sh(71.4, 1.2, zoom=(1.0, 1.04))                                  # legs
s = sh(75.0, 1.3, zoom=(1.0, 1.04))                              # the beard comes off
o.hit(s, 0.3, zoom=1.05, amount=0.4, db=-5, sound="punch")
sh(80.2, 1.6, cy=0.48, zoom=(1.0, 1.05))                         # bent over, most muscular
s = sh(85.0, 1.8, cy=0.45, zoom=(1.0, 1.06))                     # up: the front
o.hit(s, 0.1, zoom=1.08, amount=0.55, db=-1)
o.cap(s["_t0"] + 0.1, 1.7, "RONNIE *COLEMAN* :fire:", **INFO)
s = sh(100.6, 2.2, cy=0.45, zoom=(1.0, 1.06))                    # front double biceps
o.hit(s, 0.3, zoom=1.06, amount=0.45, db=-3)
o.sound(s["_t0"] + 0.3, "crowd_erupt", db=-12)
s = sh(164.0, 2.6, cy=0.45, zoom=(1.0, 1.08))                    # most muscular, glasses on
o.cap(s["_t0"], 2.6, "2ND PLACE...\n*JAY CUTLER* WON :broken-heart:", **INFO)
o.save(open_fade=0.0)
