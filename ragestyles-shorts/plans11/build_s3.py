"""s3: Bodybuilders in suits, remade (owner 2026-10-09: "make the bulky bodies easier to see", 3:4 box). No talking:
the 1999 Mr. Olympia press conference in suits (Thursday, Mandalay Bay) cut fast, then two days later the same men on
stage, Ronnie Coleman and Flex Wheeler side by side, and Ronnie's win (his 2nd title).
Sources (bilibili, YouTube is blocked on this server):
  * bl_BV1uD421M7af "99年奥赛赛前发布会" (GL健美, Mocvideo press conference footage, upscaled, vertical 1080x1920
    with the picture in a band at y 580..1400 px): crop zoom 1.8 around cy 0.516 keeps inside the band.
    Name plates seen: Nasser El Sonbaty 2..9 s, Kevin Levrone 27..31 s, Michael Matarazzo 32..39 s, Lee Priest 40..44 s.
  * bl_BV1KT4y1Z74h "Mr. Olympia 时光机带你回到1999年的奥赛现场" (GETBIG.TV 1999 Olympia, 1920x1080 with the 4:3
    picture in x 0.125..0.875 and a GETBIG.TV mark at the bottom centre, y 0.86..0.90): stage crops stay at zoom >= 1.15
    with cy <= 0.42 so the mark (y 0.86 and down) is cut.
Faces from plans11/faces.py. Facts (en.wikipedia.org/wiki/1999_Mr._Olympia): Oct 23 1999, Mandalay Bay; 1 Coleman,
2 Flex Wheeler, 4 Levrone, 6 El Sonbaty.
Run: python3 plans11/build_s3.py && python3 pipeline/bench.py plans11/s3_suits_1999.json
"""
import sys

sys.path.insert(0, "plans11")
from newscommon import Short  # noqa: E402

P, ST = "bl_BV1uD421M7af", "bl_BV1KT4y1Z74h"
o = Short("s3_suits_1999", "Bodybuilders in suits\nhit *different* :fire:",
          "Bodybuilders in suits hit different 🔥 #shorts", folder="plans11")
BAND = dict(cy=0.516, zoom=(1.8, 1.86), audio=False)
INFO = dict(style="big", y=0.86)


def suit(t_in, dur, cx, cx_end=None):
    k = dict(BAND)
    if cx_end is not None:
        k["path"] = [[0, 1.8, cx, 0.516], [dur, 1.86, cx_end, 0.516]]
    return o.shot(P, t_in, dur, cx=cx, **k)


def stage(t_in, dur, cx, cy=0.42, zoom=(1.15, 1.2), db=-8, **k):
    return o.shot(ST, t_in, dur, cx=cx, cy=cy, zoom=zoom, db=db, **k)


# 1. Thursday: the press conference, suits stretched over the biggest men in the world
o.sound(0.0, "crowd_tense", db=-20)
s = suit(28.0, 1.2, 0.49)                                       # Kevin Levrone
o.hit(s, 0.05, zoom=1.04, amount=0.45, db=-4)
o.cap(0.0, 2.4, "1999 MR. OLYMPIA\n*PRESS CONFERENCE*", **INFO)
suit(7.9, 1.2, 0.38)                                            # Nasser El Sonbaty, arm up
suit(24.4, 1.15, 0.45)
s = suit(34.6, 1.15, 0.45, 0.57)                                # Matarazzo, peace sign
suit(40.7, 1.15, 0.34, 0.47)                                    # Lee Priest
s = suit(47.0, 1.3, 0.49)
o.cap(s["_t0"], 1.3, "*2 DAYS* LATER...", **INFO)
# 2. Saturday: the same men without the suits
s = stage(966.8, 2.4, 0.4, cy=0.4, path=[[0, 1.15, 0.4, 0.4], [2.4, 1.2, 0.62, 0.4]])   # Ronnie, then Flex
o.hit(s, 0.0, zoom=1.08, amount=0.55, db=-1)
o.cap(s["_t0"], 2.4, "RONNIE vs *FLEX* :fire:", **INFO)
s = stage(251.4, 1.4, 0.5, zoom=(1.2, 1.26))                    # back double biceps
o.hit(s, 0.1, zoom=1.06, amount=0.4, db=-5, sound="punch")
stage(324.0, 1.3, 0.48, cy=0.38, zoom=(1.15, 1.2))                    # abs and thighs
stage(438.4, 1.4, 0.45, cy=0.4, zoom=(1.2, 1.24))               # most muscular, side by side
s = stage(812.0, 2.0, 0.46, zoom=(1.15, 1.22))                  # the win
o.hit(s, 0.15, zoom=1.08, amount=0.55, db=-1)
o.cap(s["_t0"] + 0.15, 1.85, "*MR. OLYMPIA* :trophy:", **INFO)
o.sound(s["_t0"] + 0.15, "crowd_erupt", db=-10)
s = stage(1050.3, 2.2, 0.48, cy=0.4, zoom=(1.2, 1.26))          # backstage, after
o.cap(s["_t0"], 2.2, "RONNIE *COLEMAN* :crown:", **INFO)
o.save(open_fade=0.0)
