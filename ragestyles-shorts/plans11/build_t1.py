"""t1: 2026 212 Olympia results, 5th to 1st (fast countdown, plans11/countdown.py).
Facts (fitnessvolt.com 2026 Men's 212 Olympia results, and the announcer): 5 Nihat Kaya $6,000 (award handed over
by Sam Sulek), 4 Vitor Porto $7,000, 3 Shaun Clarida $12,000, 2 Lucas Garcia $20,000, 1 Keone Pearson $50,000,
his 4th straight 212 title.
Source: OlympiaTV "Olympia 2026: 212 Division Official Footage" (https://youtu.be/qpQ8iI8pJA8); Demucs vocals
work/youtube/t212_vox.wav (1160 to 1470 s). Nihat Kaya's name is lost under the commentators, so 5th plays the
arena at that moment instead of a clean name call. On stage Lucas Garcia is on the left, Keone Pearson on the
right; Keone drops to his knees at his name (1424.5).
Run: python3 plans11/build_t1.py && python3 pipeline/bench.py plans11/t1_212_olympia_results.json
"""
import sys

sys.path.insert(0, "plans11")
from countdown import Countdown  # noqa: E402

k = Countdown("t1_212_olympia_results", "Who won the 2026\n*212 Olympia*? :trophy:",
              "Who won the 2026 212 Olympia? 🏆 #shorts", "qpQ8iI8pJA8", [("t212_vox.wav", 1160.0, 1470.0)])
o = k.o
# label over the pose, then the same pose zoomed in (t0, athlete x, name, head y, ...)
k.place("*5TH* PLACE", 1212.6, 0.46, (1188.1, 1189.9), 0.39, 1.8, "NIHAT KAYA\n*$6,000*", cx_end=0.44)
k.place("*4TH* PLACE", 1261.0, 0.5, (1239.9, 1242.2), 0.15, 1.8, "VITOR PORTO\n*$7,000*", zoom=1.6)
k.place("*3RD* PLACE", 1334.5, 0.42, (1290.8, 1293.3), 0.31, 1.8, "SHAUN CLARIDA\n*$12,000*", cx_end=0.34)
# the last two
t = o.t
k.say(1343.7, 1346.3, t + 0.05)                                    # "if I can have both gentlemen in the center please"
k.shot(1360.0, 2.6, path=[[0, 1.0, 0.32, 0.5], [2.6, 1.0, 0.58, 0.5]])   # pan from Lucas to Keone
k.big(t, 2.6, "LAST ~2~ STANDING")
t = o.t
k.say(1416.35, 1417.7, t)                                          # "to your winner"
k.shot(1415.0, 1.4, cx=0.46, zoom=(1.0, 1.02))
k.big(t, 1.4, "LUCAS OR KEONE?")
# the reveal: "... Olympia champion, Keone Pearson", Keone drops to his knees
t = o.t
k.say(1423.2, 1427.2, t)
s = k.shot(1423.2, 4.0, cx=0.55)
s.setdefault("tint", []).append({"at": 1.26, "dur": 0.45, "amount": 0.4, "color": [255, 200, 40]})
o.hit(s, 1.26, zoom=1.14, amount=0.55, db=-1)
k.big(t + 1.26, 2.74, "*KEONE PEARSON* WINS :trophy:\n*$50,000*", y=0.42)
t = o.t
k.say(1427.2, 1429.4, t, db=0)                                      # the arena after the name
s = k.shot(1476.0, 2.2, cx=0.5)                                    # with the gold
o.hit(s, 0.0, zoom=1.1, amount=0.45, db=-4, sound="punch")
k.big(t, 2.2, "*4TH* TITLE IN A ROW :fire:", y=0.66)
t = o.t
k.say(1451.6, 1453.6, t, db=0)
k.shot(1443.6, 1.9, cx=0.25)                                       # Lucas gets the silver
k.big(t, 1.9, "~2ND~ LUCAS GARCIA\n*$20,000*", y=0.66)
k.save()
