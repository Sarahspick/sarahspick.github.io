"""v5: the deadlift group in Jesse James West's $20,000 charity event: two times your body weight for as many reps as
possible. Patty goes first with 250 lb (113 kg) and pulls 14 reps while the room counts: "Holy crap, 14? You are
jacked."
Source: Jesse James West "20 Fitness YouTubers Fight For $20,000" (https://youtu.be/TWbA_Xw5BFM, 2026-09-27),
325 to 383 s. Music runs under it: voices from Demucs vocals work/youtube/jw6.wav (300 to 700 s), words
work/tr/jw6.json. The count is laid in real time over JJW's own cuts.
Run: python3 plans11/build_v5.py && python3 pipeline/bench.py plans11/v5_patty_14_reps.json
"""
import sys

sys.path.insert(0, "plans11")
from newscommon import Short, Speech, Cutter, words, word_captions  # noqa: E402

V = "TWbA_Xw5BFM"
o = Short("v5_patty_14_reps", "2x her bodyweight\n*for reps* :exploding-head:",
          "2x her bodyweight for reps 🤯 #shorts", folder="plans11")
c = Cutter(o)
sp = Speech(o, [("jw6.wav", 300.0, 700.0)], words("jw6"))
LIVE = dict(cx=0.5, cy=0.5, zoom=(1.0, 1.03))


def say(a, b, t_in=None, gap=0.05, tail=0.05, **k):
    t = sp.add(a, b, o.t + gap)
    return c.v(V, a if t_in is None else t_in, round(t + b - a + tail - o.t, 2), **k)


# 1. hook: the last rep locked out, "Yes!"
sp.add(366.14, 366.62, 0.05)
s = c.v(V, 366.1, 1.25, cx=0.5, cy=0.5, zoom=(1.0, 1.0))      # flat: her head sits near the top of the frame
o.hit(s, 0.1, zoom=1.0, amount=0.5, db=-3)
o.cap(0.0, 1.25, "*250 LB* :flexed-biceps:", style="big", y=0.79)
# 2. "You're gonna have to deadlift two times your body weight."
say(326.52, 328.64, 325.9, cx=0.57, cy=0.5, zoom=(1.0, 1.04))
# 3. "Patty!" ... "250."
say(338.86, 339.3, 338.4, **LIVE)
s = say(342.14, 342.58, 342.25, gap=0.0, **LIVE)
o.cap(s["_t0"], s["dur"], "*113 KG*", style="big", y=0.79)
# 4. the count, live: "One." ... "Three. Come on. Four. Yes! Five. Six. Seven. Eight. Nine."
say(346.5, 346.68, tail=0.25, **LIVE)
say(351.4, 357.34, gap=0.0, **LIVE)
# 5. "If you get one more, you have to subscribe. Get it, get it, get it!"
say(362.56, 365.45, **LIVE)
# 6. "Holy crap, 14? You are jacked." and her "Thank you so much."
s = say(379.88, 381.2, gap=0.0, cx=0.5, cy=0.5, zoom=(1.0, 1.04))
o.hit(s, round(sp.out(380.32) - s["_t0"], 2), zoom=1.05, amount=0.45, db=-4)
o.cap(s["_t0"] + 0.4, round(s["dur"] - 0.4, 2), "*14 REPS* :exploding-head:", style="big", y=0.79)
say(381.2, 381.76, 381.2, gap=0.0, cx=0.32, cy=0.5, zoom=(1.0, 1.04))
say(382.16, 382.88, 382.2, tail=0.5, cx=0.25, cy=0.5, zoom=(1.0, 1.04))
o.caps += word_captions(sp.words, y=0.72, style="wordcap", palette=["*", "~"],
                        force={"two", "patty!", "250.", "nine.", "subscribe.", "14?", "jacked."})
o.save(open_fade=0.0)
