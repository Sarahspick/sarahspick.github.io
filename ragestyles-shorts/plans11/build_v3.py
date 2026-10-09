"""v3: tug of war with a battle rope in Jesse James West's $20,000 charity event: Will Tennyson vs Hussein for the
place in the final against Luke. The room calls it "Natty vs Not", "at least you have an excuse"; the pull ends with
Will flat on his back and through. Hussein: "I didn't have any energy left, I gotta work on my cardio"
(he had collapsed after the row event).
Source: Jesse James West "20 Fitness YouTubers Fight For $20,000" (https://youtu.be/TWbA_Xw5BFM, 2026-09-27),
1560 to 1622 s. Music runs under it: voices and crowd from Demucs vocals work/youtube/jw5.wav (1470 to 1640 s), words
work/tr/jw5.json. Camera cuts from plans11/faces.cuts.
Run: python3 plans11/build_v3.py && python3 pipeline/bench.py plans11/v3_natty_vs_not.json
"""
import sys

sys.path.insert(0, "plans11")
from newscommon import Short, Speech, Cutter, words, word_captions  # noqa: E402

V, W = "TWbA_Xw5BFM", "jw5.wav"
o = Short("v3_natty_vs_not", "Natty vs not\n*tug of war* :face-exhaling:",
          "Natty vs not tug of war 😳 #shorts", folder="plans11")
c = Cutter(o)
sp = Speech(o, [(W, 1470.0, 1640.0)], words("jw5"))


def say(a, b, t_in, gap=0.05, tail=0.05, **k):
    t = sp.add(a, b, o.t + gap)
    return c.v(V, t_in, round(t + b - a + tail - o.t, 2), **k)


def crowd(a, d, db=-2):
    o.clip(W, round(a - 1470.0, 2), d, o.t, db=db)


# 1. hook: the fall, with "So this is Natty vs Not, right?"
sp.add(1575.7, 1578.08, 0.0)
s = c.v(V, 1600.35, 2.38, cx=0.24, cy=0.5, zoom=(1.0, 1.06))
o.hit(s, 0.05, zoom=1.06, amount=0.5, db=-3)
# 2. "This 1v1 decides who gets to face Luke in the final round for 20k."
t = sp.add(1560.42, 1564.42, o.t + 0.05)
c.v(V, 1573.85, 1.35, cx=0.47, cy=0.5, zoom=(1.0, 1.04))                                # Hussein
c.v(V, 1569.0, 1.55, cx=0.5, cy=0.5, zoom=(1.0, 1.04))                                  # Will
c.v(V, 1576.5, c.until(sp.out(1564.42) + 0.05), cx=0.5, cy=0.5, zoom=(1.0, 1.04))      # the room
o.cap(t, round(o.t - t, 2), "\\*Will Tennyson vs Hussein\\*", style="wordcap", italic=True, y=0.86, size=58)
# 3. "At least you have an excuse."
say(1579.14, 1580.14, 1579.2, cx=0.45, cy=0.5, zoom=(1.0, 1.04))                       # the line up laughing
# 4. "Three, two, one, go!"
say(1583.4, 1584.56, 1587.65, cx=0.5, cy=0.5, zoom=(1.0, 1.05))                         # from above
# 5. "Pull! Pull!"
say(1585.82, 1586.6, 1589.1, gap=0.0, cx=0.4, cy=0.5, zoom=(1.0, 1.05))
# 6. "Come on, come on, bro, let's go, let's go! You got that!"
say(1589.84, 1592.7, 1594.45, gap=0.0, cx=0.32, cy=0.5, zoom=(1.0, 1.05))
# 7. the shirt crosses, he flips over: the room's roar
crowd(1602.75, 2.05)
s = c.v(V, 1602.75, 2.05, cx=0.5, cy=0.5, zoom=(1.0, 1.04))
o.hit(s, 0.3, zoom=1.08, amount=0.5, db=-3)
crowd(1604.8, 1.2)
c.v(V, 1604.8, 1.2, cx=0.5, cy=0.5, zoom=(1.0, 1.04))
# 8. "He deserves it for the charity."
say(1607.68, 1610.62, 1607.8, gap=0.0, cx=0.5, cy=0.5, zoom=(1.0, 1.04))
# 9. Hussein: "I didn't have any energy left. I gotta work on my cardio."
say(1615.84, 1617.1, 1615.7, cx=0.5, cy=0.5, zoom=(1.0, 1.04))
say(1617.22, 1618.04, 1620.98, gap=0.0, tail=0.5, cx=0.79, cy=0.5, zoom=(1.0, 1.04))
o.caps += word_captions(sp.words, y=0.72, style="wordcap", palette=["*", "~"],
                        force={"natty", "luke", "20k.", "excuse.", "go!", "pull!", "charity.", "energy", "cardio."})
o.save(open_fade=0.0)
