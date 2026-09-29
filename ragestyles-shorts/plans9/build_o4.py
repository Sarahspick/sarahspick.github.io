"""o4: Nick Walker's road to the title, told by the commentators over his winning posing routine.
Commentary (source seconds): 4190.2 "Nick Walker has been working for years, injuries, sickness, last year qualified
and didn't make it to the big stage, I don't think he was leaving without it this year" (to 4200.3),
4204.7 "a lot of doubters, a lot of haters" (to 4208.0). Poses checked at 1 s steps: front lat spread 3294,
front double biceps 3297, side chest 3304.5, back double biceps 3316.5, rear lat spread 3322.
Run: python3 plans9/build_o4.py
"""
import sys

sys.path.insert(0, "plans9")
from olycommon import Short, REVEAL, REVEAL_PATH  # noqa: E402

o = Short("o4_olympia_2026_nick_walker_story", "Nobody believed in\n*Nick Walker* :eyes:",
          "Nobody believed in Nick Walker 👀 #shorts")

poses = [(3293.2, 2.3), (3296.4, 2.3), (3303.9, 2.2), (3315.9, 2.3), (3321.4, 2.2)]
shots = [o.shot(t, d, db=-14) for t, d in poses]
for s in shots:
    o.hit(s, 0.7, zoom=1.08, amount=0.28)
# the commentary runs across the five poses
o.clip(4190.2, 10.2, 0.2)
o.clip(4205.5, 1.7, 10.6)          # "a lot of doubters"
T = [s["_t0"] for s in shots]
o.cap(0, T[1] + 0.4, "YEARS OF WORK :flexed-biceps:")
o.cap(T[1] + 0.4, T[2] + 0.3 - (T[1] + 0.4), "INJURIES. *SICKNESS.*")
o.cap(T[2] + 0.3, T[4] - 0.2 - (T[2] + 0.3), "QUALIFIED LAST YEAR\n~NEVER MADE IT ON STAGE~")
o.cap(T[4] - 0.2, o.t - (T[4] - 0.2), "A LOT OF *DOUBTERS* :eyes:")

s = o.shot(REVEAL, 3.8, db=0, ease="linear", path=REVEAL_PATH)
o.cap(s["_t0"] + 0.6, 3.2, "NOW HE'S\n*MR. OLYMPIA* :trophy:")
o.hit(s, 0.6, zoom=1.15, amount=0.55, big=True)
s = o.shot(4139.7, 2.8, db=0, ease="linear", path=[[0.0, 1.0, 0.444, 0.503], [1.5, 1.0, 0.42, 0.515], [2.8, 1.0, 0.443, 0.51]])
o.cap(s["_t0"], 2.8, "*$600,000* :money-bag:")
s = o.shot(4199.6, 3.0, cx=0.52, zoom=(1.0, 1.06), audio=False)
o.clip(4142.6, 3.0, s["_t0"], db=-4)  # crowd after the hug, not the commentary (it would repeat)
o.cap(s["_t0"], 3.0, "PROVED THEM ~WRONG~ :fire:")
o.save()
