"""w3: Sam Sulek on the 2026 Olympia stage. He presented the 212 fifth place award (the announcer: "representing
Gymshark, Mr. Sam Sulek... Sam, you've made it to the Olympia stage"), then talked about it in his vlog: "I actually had
to go up and hand out an award, put my tux on, it's freaking sweet", the big names who "did not place how they wanted",
and "there is nothing like that regrouping and refocusing effect that comes after a loss like that".
Sources: OlympiaTV "Olympia 2026: 212 Division Official Footage" (https://youtu.be/qpQ8iI8pJA8, 2026-09-26), voice
from Demucs vocals work/youtube/sam5.wav (1160 to 1192 s); Sam Sulek "The Bulk Rebirth Day 27"
(https://youtu.be/1h_dZRyIkoo, 2026-09-28), voice from work/youtube/sv1.wav (40 to 110 s), posing B roll from 1630 s on.
Sam's swearing is cut out between pieces. Word captions run low (y 0.7) and info lines at y 0.86 to keep faces clear; the
stage close ups stay near zoom 1.0 so Sam's head is never cropped.
Run: python3 plans11/build_w3.py && python3 pipeline/bench.py plans11/w3_sulek_olympia_stage.json
"""
import sys

sys.path.insert(0, "plans11")
from newscommon import Short, Speech, Cutter, words, word_captions  # noqa: E402

OL, SS = "qpQ8iI8pJA8", "1h_dZRyIkoo"
o = Short("w3_sulek_olympia_stage", "Sam Sulek made it to\nthe *Olympia stage* :fire:",
          "Sam Sulek made it to the Olympia stage 🔥 #shorts", folder="plans11")
c = Cutter(o)
ann = Speech(o, [("sam5.wav", 1160.0, 1192.0)],
             [(1169.94, 1170.06, "Mr."), (1170.22, 1170.36, "Sam"), (1170.36, 1170.84, "Sulek."),
              (1173.3, 1173.72, "Sam,"), (1175.8, 1176.44, "you've"), (1176.44, 1176.56, "made"),
              (1176.56, 1176.68, "it"), (1176.68, 1176.78, "to"), (1176.78, 1176.9, "the"),
              (1176.9, 1177.22, "Olympia"), (1177.22, 1177.56, "stage.")])
sam = Speech(o, [("sv1.wav", 40.0, 110.0)], [(s, e, "huge" if w.startswith("huge") else w) for s, e, w in words("sv1")])
CAR = dict(cx=0.18, cy=0.5, zoom=(1.0, 1.04))


def piece(sp, a, b, src, t_in, gap=0.05, hit=None, tail=0.05, **k):
    t = sp.add(a, b, o.t + gap)
    s = c.v(src, t_in, round(t + b - a + tail - o.t, 2), **k)
    if hit is not None:
        o.hit(s, round(t + hit - a - s["_t0"], 2), zoom=1.12, amount=0.5, db=-3)
    return t


def info(t, d, text, y=0.3):
    o.cap(t, d, text, style="big", y=y)


# 1. hook: "Mr. Sam Sulek." over Sam in his tux next to the champion, then the arena
piece(ann, 1169.94, 1170.9, OL, 1214.2, gap=0.0, hit=1170.22, cx=0.66, cy=0.45, zoom=(1.12, 1.18))
t = o.t
o.clip("sam5.wav", 1170.9 - 1160.0, 0.9, t, db=-2)
c.v(OL, 1216.0, 0.9, cx=0.66, cy=0.45, zoom=(1.12, 1.16))
# 2. "Sam, you've made it to the Olympia stage."
piece(ann, 1173.3, 1173.75, OL, 1217.0, cx=0.6, cy=0.5, zoom=(1.0, 1.03))
t = piece(ann, 1175.8, 1177.6, OL, 1217.5, cx=0.6, cy=0.5, zoom=(1.03, 1.08), hit=1176.9)
o.shots[-1]["path"] = [[0, 1.03, 0.58, 0.5], [1.9, 1.08, 0.76, 0.5]]   # follow him as he walks off
info(t + 1.1, 0.8, "*5TH PLACE* AWARD :trophy:", y=0.86)
# 3. Sam, in his car: "I actually had to go up and hand out an award, put my tux on, yeah, it's freaking sweet,
#    to fifth place in 212"
piece(sam, 55.98, 58.56, SS, 56.0, **CAR)
piece(sam, 58.96, 61.76, OL, 1211.6, cx=0.74, cy=0.5, zoom=(1.0, 1.04), hit=60.22)
# 4. "but I saw a couple of guys who I've seen on my feed, like just huge... dudes... they did not place how they wanted."
piece(sam, 62.32, 65.32, SS, 62.4, **CAR)
piece(sam, 65.62, 66.5, OL, 1199.0, cx=0.5, cy=0.42, zoom=(1.0, 1.05))            # the 212 line up
piece(sam, 67.22, 67.56, OL, 1196.6, cx=0.5, cy=0.42, zoom=(1.05, 1.08), gap=0.0)
piece(sam, 69.36, 70.7, SS, 69.4, **CAR)
# 5. "there is nothing like that regrouping and refocusing effect that comes after a loss like that... It teaches you
#    where you're really at."
piece(sam, 76.94, 80.46, SS, 77.0, **CAR)
piece(sam, 81.03, 85.54, SS, 1760.0, cx=0.47, cy=0.45, zoom=(1.0, 1.06))         # back double biceps
info(o.t - 2.2, 2.2, "*REGROUP* :flexed-biceps:", y=0.86)
piece(sam, 87.84, 89.12, SS, 1632.0, cx=0.48, cy=0.42, zoom=(1.05, 1.1), hit=88.58, tail=0.6)
o.caps += word_captions(ann.words + sam.words, y=0.7, style="wordcap", palette=["*", "~"],
                        force={"sulek", "olympia", "award", "tux", "212", "huge", "loss", "regrouping", "refocusing"})
o.save(open_fade=0.0)
