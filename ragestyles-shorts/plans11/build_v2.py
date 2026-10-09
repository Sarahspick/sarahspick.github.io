"""v2: Chris Bumstead picks one challenge in Jesse James West's $20,000 charity event: hang from a bar as long as
possible, the first three to drop are out. Brody "officially asleep", Greg out for touching the ground with his foot
("I guess I'm taller than I thought"), Brody burning and dropping: "I think it's the deadlifts that killed me".
Source: Jesse James West "20 Fitness YouTubers Fight For $20,000" (https://youtu.be/TWbA_Xw5BFM, 2026-09-27),
dead hang 916 to 1050 s. Music runs under it: voices from Demucs vocals work/youtube/jw3.wav (900 to 1110 s), words
work/tr/jw3.json.
Run: python3 plans11/build_v2.py && python3 pipeline/bench.py plans11/v2_cbum_dead_hang.json
"""
import sys

sys.path.insert(0, "plans11")
from newscommon import Short, Speech, Cutter, words, word_captions  # noqa: E402

V = "TWbA_Xw5BFM"
o = Short("v2_cbum_dead_hang", "CBum picked\n*this challenge* :face-exhaling:",
          "CBum picked this challenge 😳 #shorts", folder="plans11")
c = Cutter(o)
sp = Speech(o, [("jw3.wav", 900.0, 1110.0)], words("jw3"))


def say(a, b, t_in, gap=0.05, tail=0.05, **k):
    t = sp.add(a, b, o.t + gap)
    return c.v(V, t_in, round(t + b - a + tail - o.t, 2), **k)


# 1. hook: arms burning on the bar, CBum: "All you have to do is hang from a bar for as long as possible."
t = sp.add(927.18, 929.88, 0.0)
s = c.v(V, 1035.6, 1.4, cx=0.44, cy=0.42, zoom=(1.1, 1.18))
o.hit(s, 0.05, zoom=1.06, amount=0.5, db=-3)
c.v(V, 928.0, c.until(sp.out(929.88) + 0.05), cx=0.79, cy=0.4, zoom=(1.45, 1.5))       # CBum on the phone
o.cap(0.0, 1.4, "\\*Chris Bumstead's pick\\*", style="wordcap", italic=True, y=0.86, size=58)
# 2. "The first three people to drop are going to be eliminated."
say(930.58, 932.7, 957.0, cx=0.5, cy=0.5, zoom=(1.0, 1.05))                            # everyone jumps on
# 3. "Three, go!"
say(954.68, 955.9, 953.0, gap=0.0, cx=0.5, cy=0.5, zoom=(1.0, 1.05))
# 4. "Brody is officially asleep."
say(987.7, 988.74, 987.9, cx=0.46, cy=0.5, zoom=(1.0, 1.05))
# 5. Greg: "You're out." "I'm out?" "Your foot was touching the ground."
s = say(1006.32, 1007.3, 1001.6, cx=0.5, cy=0.5, zoom=(1.0, 1.05))                      # the foot on the floor
o.hit(s, 0.15, zoom=1.06, amount=0.45, db=-4)
o.cap(s["_t0"] + 0.15, round(s["dur"] - 0.15, 2), "*OUT* :cross-mark:", style="big", y=0.79)
say(1007.7, 1008.4, 1006.9, gap=0.0, cx=0.46, cy=0.42, zoom=(1.0, 1.05))
# "I guess I'm taller than I thought."
say(1014.44, 1016.02, 1018.0, cx=0.48, cy=0.5, zoom=(1.0, 1.04))
# 6. "He's burning. Brody's about to go."
say(1032.12, 1033.64, 1036.4, cx=0.44, cy=0.42, zoom=(1.12, 1.2))
# 7. "No! ... Oh, Brody's out!"
s = say(1042.54, 1043.34, 1040.5, tail=0.3, cx=0.49, cy=0.45, zoom=(1.0, 1.05))
o.hit(s, 0.45, zoom=1.08, amount=0.5, db=-3)
o.cap(s["_t0"] + 0.45, round(s["dur"] - 0.45, 2), "*OUT* :cross-mark:", style="big", y=0.79)
# 8. "I think it's the deadlifts that killed me."
say(1048.54, 1049.68, 1047.9, tail=0.5, cx=0.46, cy=0.45, zoom=(1.0, 1.05))
o.caps += word_captions(sp.words, y=0.72, style="wordcap", palette=["*", "~"],
                        force={"hang", "bar", "eliminated", "asleep", "foot", "ground", "taller", "burning", "out!",
                               "deadlifts"})
o.save(open_fade=0.0)
