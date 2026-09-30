"""s2: Sam Sulek's "Bulk Rebirth", day 1 to day 27: 20 inch arms (news, 2026-09-28).
Facts: Sam Sulek made his pro debut at the 2026 Arnold Classic, 8th in Classic Physique (fitnessvolt.com 2026 Arnold
Classic Physique results); dieted through the summer ("Lean Summer is Over - Last Day of Dieting", 2026-09-01), started
"The Bulk Rebirth" on 2026-09-02, went to Olympia weekend in Las Vegas ("Back In Vegas Olympia Weekend", 2026-09-27),
day 27 on 2026-09-28 measured 20 inch arms pumped.
Sources (Sam Sulek, YouTube): Day 1 AGS3M83Nk-s, Day 27 1h_dZRyIkoo, Olympia weekend j3o0_zuSato.
Day 1 has music under the car talk: voices come from Demucs vocals (work/youtube/sa_vox_0.wav, sa_vox_1640.wav).
Run: python3 plans11/build_s2.py && python3 pipeline/bench.py plans11/s2_sam_sulek_bulk_rebirth.json
"""
import sys

sys.path.insert(0, "plans11")
from newscommon import Short, Speech, Cutter, words, word_captions  # noqa: E402

D1, D27, VEG = "AGS3M83Nk-s", "1h_dZRyIkoo", "j3o0_zuSato"
o = Short("s2_sam_sulek_bulk_rebirth", "Sam Sulek's Bulk Rebirth\nDay 27: *20 inch arms* :flexed-biceps:",
          "Sam Sulek's Bulk Rebirth, day 27: 20 inch arms 💪 #shorts", folder="plans11")
c = Cutter(o)
s1 = Speech(o, [("sa_vox_0.wav", 0.0, 80.0)], words(D1))
s27 = Speech(o, [("sa_vox_1640.wav", 1640.0, 1812.0)], words(D27))
CAR = dict(cx=0.33, cy=0.45, zoom=(1.08, 1.12))          # Day 1 car talk, his face

# 1. hook: the tape on his biceps. "Yeah, there we go. 20 inches pumped." ... "Hell freaking yeah."
s27.add(1719.3, 1722.7, 0.0)
s = c.sync(s27, D27, s27.out(1722.7), cx=0.45, cy=0.45, zoom=(1.1, 1.15))
c.hit_at(s, s27.out(1720.9), zoom=1.14, amount=0.55, db=-1)      # "20"
s27.add(1723.2, 1724.9, o.t + 0.05)
s = c.v(D27, 1685.6, c.until(s27.out(1724.9) + 0.1), cx=0.47, cy=0.42, zoom=(1.2, 1.25))   # front, after measuring
c.hit_at(s, s27.out(1723.9), zoom=1.1, amount=0.4, db=-5, sound="punch")
# 2. day 1: the bulk has begun
s1.add(0.9, 8.05, o.t + 0.1)
c.sync(s1, D1, s1.out(4.4), **CAR)                                 # "long, long, long freaking awaited"
s = c.v(D1, 1498.0, c.until(s1.out(8.05) + 0.1), cx=0.5, cy=0.42, zoom=(1.2, 1.25))   # day 1 physique
c.hit_at(s, s1.out(7.46), zoom=1.1, amount=0.45, db=-4)           # "begun"
# 3. nine months to rebuild it, the bulk rebirth
s1.add(11.3, 15.05, o.t + 0.1)
c.sync(s1, D1, s1.out(15.05), **CAR)                               # "it took your mom nine months to build your body"
s1.add(15.6, 22.75, o.t + 0.05)
c.v(D1, 1000.0, c.until(s1.out(19.9)), cx=0.5, cy=0.5, zoom=(1.1, 1.15))    # training: "another nine months to rebuild it"
s = c.sync(s1, D1, s1.out(22.75) + 0.1, **CAR)                     # "aka the bulk rebirth"
c.hit_at(s, s1.out(21.3), zoom=1.12, amount=0.5, db=-2)
# 4. next to my past self
s1.add(63.8, 70.9, o.t + 0.1)
c.v(D1, 1502.0, c.until(s1.out(67.44)), cx=0.5, cy=0.42, zoom=(1.2, 1.25))  # day 1: "stood next to my past self"
s = c.v(D27, 1759.5, c.until(s1.out(70.9) + 0.1), cx=0.5, cy=0.45, zoom=(1.15, 1.2))   # day 27 back double bi
c.hit_at(s, s1.out(69.38), zoom=1.12, amount=0.5, db=-3)          # "jarring difference"
# 5. Olympia week, back on track
s27.add(1790.45, 1797.1, o.t + 0.1)
c.v(VEG, 849.0, c.until(s27.out(1792.6)), cx=0.5, cy=0.5, zoom=(1.6, 1.65))   # Las Vegas, Olympia week: "the Olympia"
c.v(D27, 1688.6, c.until(s27.out(1795.1)), cx=0.45, cy=0.42, zoom=(1.15, 1.2))   # biceps in profile: "back home in Ohio" (in sync he pulls his shirt over his face)
c.v(D27, 1744.0, c.until(s27.out(1797.1)), cx=0.52, cy=0.42, zoom=(1.2, 1.25))    # front: "back on track"
s27.add(1800.1, 1801.5, o.t + 0.05)
s = c.v(D27, 1766.0, c.until(s27.out(1801.5) + 0.5), cx=0.55, cy=0.42, zoom=(1.2, 1.25))
c.hit_at(s, s27.out(1801.02), zoom=1.12, amount=0.5, db=-2)       # "pumped"
o.caps = word_captions(sorted(s1.words + s27.words), y=0.5, style="wordcap", palette=["*", "~"],
                       force={"20", "inches", "pumped", "yeah", "awaited", "begun", "nine", "rebuild", "rebirth",
                              "past", "jarring", "olympia", "ohio", "track", "giddy"})
o.save(open_fade=0.25)
