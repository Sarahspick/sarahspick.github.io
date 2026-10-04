"""x3: The Tren Twins on training: "I only go heavy... I don't ever do over twelve reps. Barely over eight reps...
You don't need to do this lat pull down... I haven't done lat pull downs in months... Do pull ups if you're going to
do something like that." Swears are cut out between pieces (the words never appear).
Source: The Tren Twins "WE FCK!N WON" (https://youtu.be/htrcV40AXSE, 2026-10-02), gym part 249 to 300 s; music under
it, so voices come from Demucs vocals work/youtube/tt1.wav (240 to 335 s). Red cap twin sits centre left (face x 0.40
to 0.48), the twin in sunglasses stands right (face x 0.63 to 0.69, high in the frame).
Run: python3 plans11/build_x3.py && python3 pipeline/bench.py plans11/x3_tren_twins_lat_pulldowns.json
"""
import sys

sys.path.insert(0, "plans11")
from newscommon import Short, Speech, Cutter, words, word_captions  # noqa: E402

V = "htrcV40AXSE"
o = Short("x3_tren_twins_lat_pulldowns", "Tren Twins don't do\n*lat pulldowns* :face-with-steam-from-nose:",
          "Tren Twins don't do lat pulldowns 😤 #shorts", folder="plans11")
c = Cutter(o)
sp = Speech(o, [("tt1.wav", 240.0, 335.0)], words("tt1"))
RED = dict(cy=0.45, zoom=(1.15, 1.2))
SUN = dict(cx=0.66, cy=0.38, zoom=(1.15, 1.2))


def say(a, b, t_in, gap=0.05, hit=None, tail=0.05, **k):
    t = sp.add(a, b, o.t + gap)
    s = c.v(V, t_in, round(t + b - a + tail - o.t, 2), **k)
    if hit is not None:
        o.hit(s, round(t + hit - a - s["_t0"], 2), zoom=1.08, amount=0.5, db=-3)
    return t


# 1. hook: "You don't need to do this lat pull down"
say(256.56, 257.96, 256.5, gap=0.0, hit=257.46, **SUN)
# 2. "I only go heavy, man. I don't ever do over twelve ... reps. Barely over eight reps, man. Let's go heavy"
say(249.52, 250.54, 249.5, cx=0.47, **RED)
say(250.74, 252.04, 250.8, cx=0.46, hit=251.74, **RED)
say(252.40, 252.68, 252.4, cx=0.45, gap=0.0, **RED)
say(253.0, 254.18, 253.0, cx=0.44, hit=253.52, **RED)
say(254.8, 255.26, 254.8, cx=0.41, **RED)
# 3. "I haven't done lat pull downs in ... months. Do pull ups if you're going to do something like that."
say(258.70, 260.10, 258.7, hit=259.2, **SUN)
say(260.60, 261.10, 260.6, gap=0.0, cx=0.56, cy=0.45, zoom=(1.1, 1.14))   # sunglasses twin leaning in
say(263.74, 266.22, 263.8, hit=264.0, cx=0.67, cy=0.5, zoom=(1.0, 1.04))   # standing tall here: full height
# 4. payoff: the rows, "That is heavy"
t = o.t
o.clip("tt1.wav", 284.4 - 240.0, 1.6, t, db=-2)
s = c.v(V, 284.4, 1.6, cx=0.6, cy=0.5, zoom=(1.0, 1.05))     # seated at the row, face clear
o.hit(s, 0.0, zoom=1.06, amount=0.4, db=-5, sound="punch")
o.cap(t, 1.6, "*HEAVY* ONLY :flexed-biceps:", style="big", y=0.82)
say(291.36, 292.5, 291.4, tail=0.6, cx=0.45, cy=0.45, zoom=(1.0, 1.05))
o.caps += word_captions(sp.words, y=0.72, style="wordcap", palette=["*", "~"],
                        force={"heavy", "twelve", "eight", "lat", "months", "pull", "ups"})
o.save(open_fade=0.0)
