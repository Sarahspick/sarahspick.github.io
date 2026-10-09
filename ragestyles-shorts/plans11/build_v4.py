"""v4: the 500 m row in Jesse James West's $20,000 charity event, first three to 500 m move on. Will Tennyson forgot to
hit the start button (0 m while the others pass 100), chased the whole way, passed Patty at the end (473 to 455 m),
fell off the machine, and was still out: "Patty and Will, you two are out, unfortunately".
Source: Jesse James West "20 Fitness YouTubers Fight For $20,000" (https://youtu.be/TWbA_Xw5BFM, 2026-09-27), row
1210 to 1402 s. Music runs under it: voices from Demucs vocals work/youtube/jw7.wav (1150 to 1272 s) and jw4.wav
(1270 to 1430 s). The live leaderboard sits top left: the board shots crop to it (cx 0.21).
Run: python3 plans11/build_v4.py && python3 pipeline/bench.py plans11/v4_forgot_start.json
"""
import sys

sys.path.insert(0, "plans11")
from newscommon import Short, Speech, Cutter, words, word_captions  # noqa: E402

V = "TWbA_Xw5BFM"
o = Short("v4_forgot_start", "He forgot to\n*press start* :skull:",
          "He forgot to press start 💀 #shorts", folder="plans11")
c = Cutter(o)
sp = Speech(o, [("jw7.wav", 1150.0, 1272.0), ("jw4.wav", 1270.0, 1430.0)], words("jw7") + words("jw4"))
BOARD = dict(cx=0.21, cy=0.5, zoom=(1.0, 1.04))


def say(a, b, t_in, gap=0.05, tail=0.05, **k):
    t = sp.add(a, b, o.t + gap)
    return c.v(V, t_in, round(t + b - a + tail - o.t, 2), **k)


# 1. hook: Will falls off the rower, "Will actually forgot to hit the start button"
sp.add(1238.04, 1240.04, 0.0)
s = c.v(V, 1369.9, 1.2, cx=0.64, cy=0.45, zoom=(1.0, 1.06))
o.hit(s, 0.05, zoom=1.06, amount=0.5, db=-3)
c.v(V, 1371.15, c.until(sp.out(1240.04) + 0.05), cx=0.5, cy=0.5, zoom=(1.0, 1.04))   # up again, laughing
# 2. "row 500 meters as fast as you possibly can"
say(1216.12, 1218.4, 1226.0, cx=0.5, cy=0.5, zoom=(1.0, 1.05))
# 3. "while Luke, Patty and Jeremy excelled": the board, Will at 0
s = say(1236.32, 1238.04, 1236.0, **BOARD)
o.cap(s["_t0"] + 0.3, round(s["dur"] - 0.3, 2), "*WILL: 0 M* :skull:", style="big", y=0.79)
o.hit(s, 0.3, zoom=1.05, amount=0.35, db=-6, sound="punch")
# 4. "just hit start!"
say(1240.04, 1240.82, 1240.9, gap=0.0, tail=0.15, cx=0.55, cy=0.45, zoom=(1.0, 1.05))
# 5. "Will was not doing so well, as he was still trying to make up the ground he lost at the start"
t = sp.add(1343.34, 1348.44, o.t + 0.05)
c.v(V, 1342.7, 2.45, cx=0.5, cy=0.5, zoom=(1.0, 1.06))                               # from above, rowing flat out
c.v(V, 1345.25, c.until(sp.out(1348.44) + 0.05), cx=0.6, cy=0.5, zoom=(1.0, 1.04))
# 6. the finish: he passes Patty (473 to 455) but only three go through
o.clip("jw4.wav", 1367.15 - 1270.0, 2.0, o.t, db=-2)
s = c.v(V, 1367.15, 2.0, **BOARD)
o.cap(s["_t0"] + 0.2, 1.8, "*ONLY TOP 3 MOVE ON*", style="big", y=0.79)
o.hit(s, 0.2, zoom=1.06, amount=0.45, db=-4)
# 7. "Okay, Patty and Will, you two are out, unfortunately"
sp.add(1398.66, 1402.64, o.t + 0.05)
c.v(V, 1399.3, 1.3, cx=0.5, cy=0.5, zoom=(1.0, 1.04))
s = c.v(V, 1400.6, 1.3, cx=0.79, cy=0.5, zoom=(1.0, 1.04))                            # the crosses
s = c.v(V, 1401.85, c.until(sp.out(1402.64) + 0.35), still=True, cx=0.79, cy=0.5, zoom=(1.04, 1.1))  # held (the camera swings away)
o.hit(s, 0.0, zoom=1.06, amount=0.45, db=-3)
o.caps += word_captions(sp.words, y=0.72, style="wordcap", palette=["*", "~"],
                        force={"forgot", "500", "excelled", "start!", "ground", "out"})
o.save(open_fade=0.0)
