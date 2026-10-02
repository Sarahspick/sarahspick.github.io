"""w2: the final event of Jesse James West's "20 Fitness YouTubers Fight For $20,000" (2026-09-27): Will Tennyson vs
Luke Elsman. One of two pre-workout tubs holds a $100 bill that wins the $20,000 for St. Jude. Luke opens his tub
(empty) and tells Will the truth: "I don't have the money". Will reads it as a bluff ("I felt a voice crack"), steals
Luke's tub, opens it: nothing inside, so Luke wins. Luke: "I was telling you the truth. Everything was true."
Source: https://youtu.be/TWbA_Xw5BFM (uploaded 2026-09-27). Voices from Demucs vocals work/youtube/jw2.wav
(1628 to 1762 s), words in work/tr/jw2.json. Faces sit high in the close ups: word captions run low (y 0.68)
and the info lines at y 0.86.
Run: python3 plans11/build_w2.py && python3 pipeline/bench.py plans11/w2_tub_bluff.json
"""
import sys

sys.path.insert(0, "plans11")
from newscommon import Short, Speech, Cutter, words, word_captions  # noqa: E402

V = "TWbA_Xw5BFM"
o = Short("w2_tub_bluff", "He told the truth\nand *won $20,000* :flushed-face:",
          "He told the truth and won $20,000 😳 #shorts", folder="plans11")
c = Cutter(o)
sp = Speech(o, [("jw2.wav", 1628.0, 1762.0)], words("jw2"))
K = dict(cy=0.45, zoom=(1.1, 1.15))


def info(t, d, text, y=0.86):
    o.cap(t, d, text, style="big", y=y)


def say(a, b, src, t_in, gap=0.05, hit=None, **k):
    """One spoken piece over one shot; hit = source second of the punch."""
    t = sp.add(a, b, o.t + gap)
    s = c.v(src, t_in, round(t + b - a + 0.05 - o.t, 2), **k)
    if hit is not None:
        o.hit(s, round(t + hit - a - s["_t0"], 2), zoom=1.12, amount=0.5, db=-3)
    return s


# 1. hook: Luke, close up: "There's no money in the tub."
say(1708.36, 1709.38, V, 1708.3, gap=0.0, hit=1708.6, cx=0.59, **K)
# 2. the rules
say(1635.88, 1639.2, V, 1636.0, cx=0.5, cy=0.5, zoom=(1.05, 1.12))        # host with the two tubs
o.shots[-1]["dur"] = round(o.shots[-1]["dur"] - 1.5, 2); o.t = round(o.t - 1.5, 2)
c.v(V, 1640.0, c.until(sp.out(1639.2) + 0.05), cx=0.5, cy=0.5, zoom=(1.0, 1.06))   # overhead: the tubs
info(sp.out(1638.28), sp.out(1639.2) - sp.out(1638.28), ":money-bag: *$100* BILL")
say(1641.64, 1642.98, V, 1641.0, cx=0.5, cy=0.5, zoom=(1.06, 1.1), hit=1641.94)   # "you win the $20,000 for St. Jude"
say(1653.0, 1658.02, V, 1655.0, cx=0.5, **K)                                      # "...keep or steal from the other person"
info(sp.out(1656.3), sp.out(1658.02) - sp.out(1656.3), "KEEP or *STEAL*")
# 3. Luke opens his, empty, and says so
say(1673.22, 1673.6, V, 1673.4, cx=0.55, cy=0.4, zoom=(1.0, 1.04))
say(1674.5, 1675.52, V, 1674.6, cx=0.5, cy=0.5, zoom=(1.05, 1.1))                 # opening the tub
say(1690.16, 1691.08, V, 1690.2, cx=0.57, hit=1690.88, **K)                       # "I don't have the money."
# 4. Will's read
say(1706.96, 1707.72, V, 1706.9, cx=0.48, **K)                                    # "Is the money in the tub?"
say(1708.36, 1709.38, V, 1708.3, cx=0.59, **K)                                    # "There's no money in the tub."
say(1714.62, 1715.2, V, 1714.6, cx=0.33, cy=0.45, zoom=(1.12, 1.18), hit=1714.8)  # "I'm gonna steal it."
t = o.t
o.clip("jw2.wav", 1718.0 - 1628.0, 1.1, t, db=-2)
c.v(V, 1718.0, 1.1, cx=0.45, cy=0.5, zoom=(1.0, 1.05))                           # he takes Luke's tub
info(t, 1.1, "*STOLEN* :exploding-head:")
say(1720.8, 1724.14, V, 1721.9, cx=0.58, **K)                                     # Will: "I felt a voice crack..." over Luke grinning
# 5. the reveal
say(1729.96, 1731.7, V, 1730.6, cx=0.5, cy=0.5, zoom=(1.0, 1.04))                 # "If Will opens this and there's nothing"
say(1731.7, 1733.4, V, 1732.4, cx=0.42, cy=0.5, zoom=(1.0, 1.03), hit=1732.98)   # "...inside, Luke wins." Will looking in
say(1735.6, 1737.08, V, 1735.0, cx=0.5, cy=0.45, zoom=(1.05, 1.1))                # "You have nothing?" "No, I have nothing."
say(1737.52, 1739.42, V, 1737.3, cx=0.62, cy=0.45, zoom=(1.05, 1.1), hit=1738.6) # the room erupts, "Let's go!"
o.shots[-1]["path"] = [[0, 1.05, 0.62, 0.45], [1.0, 1.1, 0.68, 0.42]]            # follow Luke's jump
# 6. "I was telling you the truth. Everything was true. I'm 5'10 on a good day."
say(1750.04, 1751.98, V, 1750.0, cx=0.57, **K)
say(1752.1, 1753.12, V, 1752.0, cx=0.6, hit=1752.32, **K)
say(1754.5, 1757.4, V, 1754.4, cx=0.5, cy=0.5, zoom=(1.0, 1.05), hit=1756.84)    # "the gym bro, Luke Elsman, wins the competition!"
o.shots[-1]["dur"] = round(o.shots[-1]["dur"] + 0.5, 2); o.t = round(o.t + 0.5, 2)
wd = [(s, e, "Elsman," if w.startswith("Elson") else w) for s, e, w in sp.words]
o.caps += word_captions(wd, y=0.68, style="wordcap", palette=["*", "~"],
                        force={"money", "$100", "$20,000", "steal", "nothing", "truth", "wins", "crack"})
o.save(open_fade=0.0)
