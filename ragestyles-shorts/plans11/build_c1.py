"""c1: 2026 Classic Physique Olympia results countdown, 5th to 1st (the o1 format the owner says was a hit).
Facts (fitnessvolt.com 2026 Classic Physique Olympia results, generationiron.com scorecards, and the announcer):
5 Terrence Ruffin $6,000, 4 Wesley Vissers $10,000, 3 Ramon Dino (defending champion) $20,000, presented by Hafthor,
2 Mike Sommerfeld $40,000 (not said on stage, from the published results), 1 Niall Darwen $100,000.
Source: OlympiaTV "Olympia 2026: Classic Physique Official Footage" (https://youtu.be/pRWCqgRzN9c), awards 1426 to
1660 s, Niall on stage with Bob 1870 to 1890 s. Arena music removed with Demucs: work/youtube/cl_vox_1420.wav
(1420 to 1680 s), cl_vox_1855.wav (1855 to 1905 s).
Layout: 3:4 box from 370 px, title from 155 px, one big caption at the screen centre; every shot was checked so no
head sits under the title or the caption (owner, 2026-10-01).
Run: python3 plans11/build_c1.py && python3 pipeline/bench.py plans11/c1_classic_olympia_results.json
"""
import sys

sys.path.insert(0, "plans11")
from newscommon import Short, Speech, Cutter, words, word_captions  # noqa: E402

V = "pRWCqgRzN9c"
o = Short("c1_classic_olympia_results", "Who won the 2026\n*Classic Olympia*? :trophy:",
          "Who won the 2026 Classic Olympia? 🏆 #shorts", folder="plans11")
c = Cutter(o)
VOX = [("cl_vox_1420.wav", 1420.0, 1680.0), ("cl_vox_1855.wav", 1855.0, 1905.0)]


def say(a, b, t, db=3):
    o.vox(VOX, a, round(b - a, 2), t, db=db)


def big(t, d, text, y=0.5):
    o.cap(t, d, text, style="big", y=y)   # y 0.64 where a face would sit under the centre line


# 5th: Terrence Ruffin
t = o.t
say(1430.9, 1434.3, t + 0.05)                                   # "the fifth place check for $6,000 and presented to"
say(1438.1, 1440.7, t + 3.5)                                    # "Rough Diesel Terrence Ruffin"
c.v(V, 1470.6, 3.5, cx=0.36, cy=0.5, zoom=(1.0, 1.04))          # first second: sharp, posing with the medal
s = c.v(V, 1463.6, 2.4, cx=0.44, cy=0.5, zoom=(1.0, 1.05))      # the medal going on
o.hit(s, 0.0, zoom=1.12, amount=0.5, db=-3)
big(t, 3.5, "*5TH* PLACE")
big(t + 3.5, 2.4, "TERRENCE RUFFIN\n*$6,000*")
# 4th: Wesley Vissers
t = o.t
say(1471.2, 1473.65, t + 0.05)                                  # "the check for $10,000 and presented to"
say(1476.1, 1477.6, t + 2.6)                                    # "Wesley Vissers"
c.v(V, 1498.2, 2.6, cx=0.4, cy=0.5, zoom=(1.0, 1.04))           # medal on
s = c.v(V, 1503.0, 2.6, cx=0.36, cy=0.5, zoom=(1.0, 1.05))      # front double biceps, laughing
o.hit(s, 0.0, zoom=1.12, amount=0.5, db=-3)
big(t, 2.6, "*4TH* PLACE")
big(t + 2.6, 2.6, "WESLEY VISSERS\n*$10,000*")
# 3rd: presented by Hafthor, Ramon Dino, last year's champion
t = o.t
say(1509.9, 1513.3, t + 0.05)                                   # "presenting the third place award is the world's largest human being"
c.v(V, 1510.8, 3.4, cx=0.3, cy=0.5, zoom=(1.0, 1.04))           # Thor walks on
big(t, 3.4, "PRESENTED BY\n~THOR~ :exploding-head:")
t = o.t
say(1534.2, 1538.45, t + 0.05)                                  # "the check for $20,000 and presented to"
c.v(V, 1547.0, 4.25, cx=0.55, cy=0.5, zoom=(1.0, 1.04))         # walking out
say(1541.5, 1542.75, o.t)                                       # "Ramon Dino"
say(1544.8, 1546.2, o.t + 1.3)                                  # "the crowd did not see that coming"
s = c.v(V, 1561.5, 2.8, cx=0.5, cy=0.5, zoom=(1.0, 1.04))       # Dino with the bronze next to Thor
o.hit(s, 0.0, zoom=1.12, amount=0.5, db=-3)
big(t, 4.25, "*3RD* PLACE\n~LAST YEAR'S CHAMPION~")
big(t + 4.25, 2.8, "RAMON DINO\n*$20,000*", y=0.64)
# the last two
t = o.t
say(1584.2, 1586.4, t + 0.05)                                   # "Mike and Niall in the center, please"
c.v(V, 1611.0, 2.4, path=[[0, 1.0, 0.32, 0.5], [2.4, 1.0, 0.66, 0.5]])   # pan from Mike to Niall
big(t, 2.4, "LAST ~2~ STANDING")
t = o.t
say(1609.4, 1612.5, t + 0.05)                                   # "the first place check for $100,000"
c.v(V, 1627.5, 3.1, cx=0.3, cy=0.5, zoom=(1.0, 1.05))           # Mike
big(t, 3.1, "MIKE SOMMERFELD")
t = o.t
say(1616.6, 1620.6, t + 0.05)                                   # "2026 Classic Physique Olympia champion"
c.v(V, 1630.6, 4.0, cx=0.66, cy=0.5, zoom=(1.0, 1.05))          # Niall
big(t, 4.0, "OR NIALL DARWEN?")
# the reveal
t = o.t
say(1620.9, 1622.0, t + 0.05)                                   # "to our winner"
say(1635.4, 1638.6, t + 1.3, db=4)                              # "Niall Darwen" and the crowd after it
say(1631.9, 1632.25, t + 1.05, db=-6)                           # a breath of the waiting arena so the pause is never dead air
s = c.v(V, 1634.6, 4.0, cx=0.62, cy=0.5, zoom=(1.0, 1.04))      # hands over his face, confetti
s.setdefault("tint", []).append({"at": 1.3, "dur": 0.45, "amount": 0.4, "color": [255, 200, 40]})
o.hit(s, 1.3, zoom=1.14, amount=0.55, db=-1)
big(t + 1.3, 2.7, "*NIALL DARWEN* WINS :trophy:\n*$100,000*", y=0.64)
t = o.t
say(1645.3, 1648.0, t + 0.05)                                   # "that was that close, guys. that was that close"
c.v(V, 1651.0, 3.0, cx=0.38, cy=0.5, zoom=(1.0, 1.04))          # Mike and Niall hug
big(t, 3.0, "~2ND~ MIKE SOMMERFELD\n*$40,000*", y=0.66)
# Niall: 5th last year
sp = Speech(o, VOX, words(V))
sp.add(1876.6, 1878.45, o.t + 0.1)                              # "I was in the fifth place last year"
c.sync(sp, V, sp.out(1878.45) + 0.05, cx=0.4, cy=0.5, zoom=(1.0, 1.04))
sp.add(1885.35, 1887.4, o.t + 0.05)                             # "ten places in two years to the top"
c.v(V, 1637.2, c.until(sp.out(1886.72)), cx=0.62, cy=0.5, zoom=(1.0, 1.04))
s = c.sync(sp, V, sp.out(1887.4) + 0.6, cx=0.4, cy=0.5, zoom=(1.0, 1.04))
c.hit_at(s, sp.out(1887.1), zoom=1.12, amount=0.5, db=-2)       # "top"
o.caps += word_captions(sp.words, y=0.66, style="wordcap", palette=["*", "~"], force={"fifth", "ten", "top"})
o.save(open_fade=0.25)
