"""x2: Max Searby, 25, benches 285 kg / 628 lb raw, the heaviest bench press ever done in the UK (any weight class or
age), and Eddie Hall comments "Well done mate great work".
Source: Lifters Club "25 Year Old Giant Broke The Bench Record (INSANE)" (https://youtu.be/gGEMp9usg7g, 2026-09-23),
which runs the meet footage under a narrator: Demucs left nothing but the narration (no_vocals at -65 dB), so the
picture is used silent and the sound is ElevenLabs crowd (crowd_tense, crowd_erupt) plus the usual hits. The clip's
own text (top left "285 Kg/628 Lb UK Record", bottom left sponsor names) sits outside the 3:4 crop; Eddie's comment
card (bottom, from 48 s) is cropped out with a zoom and written as our own caption instead.
On the bench his face is behind the spotters, so his face opens (the roar) and frames the lift (stare, sitting down).
Run: python3 plans11/build_x2.py && python3 pipeline/bench.py plans11/x2_max_searby_285_bench.json
"""
import sys

sys.path.insert(0, "plans11")
from newscommon import Short, Cutter  # noqa: E402

V = "gGEMp9usg7g"
o = Short("x2_max_searby_285_bench", "Heaviest bench\nin *UK history* :exploding-head:",
          "Heaviest bench in UK history 🤯 #shorts", folder="plans11")
c = Cutter(o)


def big(t, d, text, y=0.3):
    o.cap(t, d, text, style="big", y=y)


# 1. hook: the roar after the lift (comment card cropped out: zoom 1.4 keeps the top 80 % of the frame)
o.sound(0.0, "crowd_erupt", db=-16)
s = c.v(V, 48.35, 1.0, cx=0.56, cy=0.45, zoom=(1.4, 1.44),     # sitting up, roaring: tilt up with his head
        path=[[0, 1.4, 0.56, 0.47], [1.0, 1.44, 0.56, 0.36]])
o.hit(s, 0.0, zoom=1.06, amount=0.5, db=-3)
big(0.0, 1.0, "*285 KG* :exploding-head:", y=0.82)
# 2. who: Max Searby, 25
t = o.t
s = c.v(V, 20.5, 1.6, cx=0.55, cy=0.4, zoom=(1.3, 1.36))        # staring the bar down
o.hit(s, 0.0, zoom=1.05, amount=0.35, db=-6, sound="punch")
big(t, 1.6, "MAX SEARBY\n*25* YEARS OLD", y=0.75)
t = o.t
c.v(V, 23.0, 1.0, cx=0.54, cy=0.45, zoom=(1.25, 1.3))            # sits down on the bench
big(t, 1.0, "*628 LB* ON THE BAR", y=0.75)
# 3. the lift: handoff, down, press, rack
t = o.t
o.sound(t, "crowd_tense", db=-17)
s = c.v(V, 40.8, 6.9, cx=0.52, cy=0.5, zoom=(1.1, 1.18))
big(t, 2.4, "HEAVIEST BENCH\nEVER IN THE UK?", y=0.75)
o.hit(s, 5.6, zoom=1.08, amount=0.55, db=-2)                     # lockout (46.4)
s.setdefault("tint", []).append({"at": 5.6, "dur": 0.45, "amount": 0.35, "color": [255, 200, 40]})
big(t + 5.6, 1.3, "*GOOD LIFT* :fire:", y=0.75)
# 4. the roar, then Eddie Hall's comment
t = o.t
o.sound(t, "crowd_erupt", db=-14)
s = c.v(V, 47.7, 1.7, cx=0.55, cy=0.43, zoom=(1.35, 1.42),     # the source cuts to other footage at 50 s
        path=[[0, 1.35, 0.55, 0.47], [0.6, 1.36, 0.55, 0.47], [1.7, 1.42, 0.55, 0.36]])
o.hit(s, 0.3, zoom=1.06, amount=0.5, db=-3)
big(t + 0.3, 1.4, "*UK RECORD* :trophy:", y=0.82)
t = o.t
s = c.v(V, 49.4, 1.9, cx=0.55, cy=0.43, zoom=(1.35, 1.4), still=True)
big(t, 1.9, "EDDIE HALL:\n\"Well done mate\ngreat work\" :flexed-biceps:", y=0.78)
o.save(open_fade=0.0)
