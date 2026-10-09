"""m2: Samson Dauda's posing routine at the 2026 Mr. Olympia finals in 4K (2nd place, 310 lb on stage per x1). Pure
visual: the biggest poses cut on the beat, his own stage music and the crowd under it.
Source: bilibili BV1tPhX6uEuF "回不去的巅峰，萨姆森2026年奥赛4K超清个人展示" (不爱动的仙人掌, vertical 1080x1920, no voice
over), downloaded with /tmp/claude-0/bili.py. Vertical source: the 3:4 box takes the full width and 75% of the height,
cy picks the part (0.42 upper body, 0.5 full).
Run: python3 plans11/build_m2.py && python3 pipeline/bench.py plans11/m2_samson_4k.json
"""
import sys

sys.path.insert(0, "plans11")
from newscommon import Short  # noqa: E402

V = "bl_BV1tPhX6uEuF"
o = Short("m2_samson_4k", "Samson Dauda\nin *4K* :fire:",
          "Samson Dauda in 4K 🔥 #shorts", folder="plans11")
INFO = dict(style="big", y=0.86)


def sh(t_in, dur, cy=0.42, zoom=(1.0, 1.05), db=-6, **k):
    return o.shot(V, t_in, dur, cx=0.5, cy=cy, zoom=zoom, db=db, af="film", **k)


s = sh(14.0, 1.4)                                                 # hook: front double biceps
o.hit(s, 0.05, zoom=1.05, amount=0.5, db=-3)
o.cap(0.0, 2.6, "SAMSON *DAUDA*", **INFO)
sh(0.5, 1.3)
sh(6.5, 1.3)
s = sh(26.0, 1.4)                                                 # side chest
o.cap(s["_t0"], 1.4, "*310 LB* ON STAGE", **INFO)
o.hit(s, 0.1, zoom=1.04, amount=0.35, db=-6, sound="punch")
s = sh(48.5, 1.6, cy=0.45)                                        # back double biceps
o.hit(s, 0.2, zoom=1.06, amount=0.45, db=-3)
sh(58.0, 1.3, cy=0.45)                                            # back lat spread
sh(76.0, 1.3)
sh(90.0, 1.5, cy=0.5)                                             # abs and thighs
s = sh(100.0, 1.3)
s = sh(110.0, 2.4)                                                # most muscular
o.hit(s, 0.15, zoom=1.08, amount=0.55, db=-1)
o.sound(s["_t0"] + 0.15, "crowd_erupt", db=-12)
o.cap(s["_t0"] + 0.15, 2.25, "2ND AT THE *2026 OLYMPIA*", **INFO)
o.save(open_fade=0.0)
