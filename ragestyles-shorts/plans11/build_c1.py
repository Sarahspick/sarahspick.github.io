"""c1 v2: 2026 Classic Physique Olympia results, 5th to 1st, fast (owner, 2026-10-01: v1 too long and slow).
Owner's opening: the video starts on the 5th placer's Zyzz pose with "5TH PLACE" for about 0.5 s, then a cut, the
announcer says only the name, zoom punch + flash + boom. 5th, 4th, 3rd go by fast; no side bits (no "presented by
Thor"). Then the last two, the reveal, 2nd, and Niall's one line.
Facts (fitnessvolt.com 2026 Classic Physique Olympia results, generationiron.com, the announcer): 5 Terrence Ruffin
$6,000, 4 Wesley Vissers $10,000, 3 Ramon Dino $20,000, 2 Mike Sommerfeld $40,000 (published results), 1 Niall
Darwen $100,000.
Source: OlympiaTV "Olympia 2026: Classic Physique Official Footage" (https://youtu.be/pRWCqgRzN9c); Demucs vocals
work/youtube/cl_vox_1420.wav (1420 to 1680 s), cl_vox_1855.wav (1855 to 1905 s).
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


def say(a, b, t, db=4):
    o.vox(VOX, a, round(b - a, 2), t, db=db)


def big(t, d, text, y=0.5):
    o.cap(t, d, text, style="big", y=y)   # y 0.64 where a face would sit under the centre line


def place(label, pre, name_a, name_b, shot, d, text, y=0.5):
    """'5TH PLACE' over a short shot, then the cut: the announcer says only the name, punch + flash + boom."""
    t = o.t
    c.v(V, *pre)
    big(t, pre[1], label)
    say(name_a, name_b, o.t)
    s = c.v(V, shot[0], d, **shot[1])
    o.hit(s, 0.0, zoom=1.14, amount=0.55, db=-2)
    big(o.t - d, d, text, y)


place("*5TH* PLACE", (1469.6, 0.5, ), 1438.95, 1440.65,
      (1463.6, dict(cx=0.44, cy=0.5, zoom=(1.0, 1.05))), 1.8, "TERRENCE RUFFIN\n*$6,000*")
o.shots[0].update(cx=0.365, cy=0.5, zoom=[1.0, 1.02])          # the Zyzz pose, face clear of the caption
place("*4TH* PLACE", (1488.2, 0.45), 1475.4, 1477.55,
      (1503.0, dict(cx=0.36, cy=0.5, zoom=(1.0, 1.05))), 2.1, "WESLEY VISSERS\n*$10,000*")
o.shots[2].update(cx=0.66, cy=0.5, zoom=[1.0, 1.02])
place("*3RD* PLACE", (1549.0, 0.45), 1541.4, 1542.7,
      (1561.5, dict(cx=0.48, cy=0.5, zoom=(1.0, 1.05))), 1.9, "RAMON DINO\n*$20,000*", y=0.64)
o.shots[4].update(cx=0.55, cy=0.5, zoom=[1.0, 1.02])
# the last two
t = o.t
say(1584.2, 1586.4, t + 0.05)                                   # "Mike and Niall in the center, please"
c.v(V, 1611.0, 2.3, path=[[0, 1.0, 0.32, 0.5], [2.3, 1.0, 0.66, 0.5]])   # pan from Mike to Niall
big(t, 2.3, "LAST ~2~ STANDING")
t = o.t
say(1620.9, 1622.0, t)                                          # "to our winner"
c.v(V, 1632.5, 1.15, cx=0.5, cy=0.5, zoom=(1.0, 1.03), box_aspect=0.75)
big(t, 1.15, "MIKE OR NIALL?")
# the reveal
t = o.t
say(1635.4, 1638.6, t + 0.75)                                   # "Niall Darwen" and the crowd
s = c.v(V, 1634.7, 3.0, cx=0.62, cy=0.5, zoom=(1.0, 1.04))      # hands over his face, confetti
s.setdefault("tint", []).append({"at": 0.75, "dur": 0.45, "amount": 0.4, "color": [255, 200, 40]})
o.hit(s, 0.75, zoom=1.14, amount=0.55, db=-1)
say(1631.9, 1632.6, t, db=-6)                                   # the waiting arena under the first 0.75 s
big(t + 0.75, 2.25, "*NIALL DARWEN* WINS :trophy:\n*$100,000*", y=0.64)
t = o.t
c.v(V, 1651.0, 2.2, cx=0.38, cy=0.5, zoom=(1.0, 1.04))          # Mike and Niall hug
say(1645.3, 1647.6, t + 0.05)                                   # "that was that close, guys"
big(t, 2.2, "~2ND~ MIKE SOMMERFELD\n*$40,000*", y=0.66)
# Niall: 5th last year
sp = Speech(o, VOX, words(V))
sp.add(1876.6, 1878.45, o.t + 0.05)                             # "I was in the fifth place last year"
c.sync(sp, V, sp.out(1878.45) + 0.05, cx=0.4, cy=0.5, zoom=(1.0, 1.04))
sp.add(1885.35, 1887.4, o.t + 0.05)                             # "ten places in two years to the top"
c.v(V, 1637.2, c.until(sp.out(1886.72)), cx=0.62, cy=0.5, zoom=(1.0, 1.04))
s = c.sync(sp, V, sp.out(1887.4) + 0.5, cx=0.52, cy=0.5, zoom=(1.0, 1.04))
c.hit_at(s, sp.out(1887.1), zoom=1.12, amount=0.5, db=-2)       # "top"
o.caps += word_captions(sp.words, y=0.66, style="wordcap", palette=["*", "~"], force={"fifth", "ten", "top"})
o.save(open_fade=0.0)   # owner: the very first frame matters most, no fade
