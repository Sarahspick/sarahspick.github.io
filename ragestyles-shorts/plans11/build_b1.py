"""b1: Tigst Assefa, Berlin Marathon 2026-09-27: on world record pace, her right leg gives out in the last kilometre,
she still wins in 2:11:04 and collapses at the line, 68 seconds off the world record.
Facts (olympics.com "Berlin Marathon 2026: Ethiopia shines as Tigst Assefa narrowly misses world record", run247.com,
the broadcast): 3rd Berlin title, 2:11:04, a personal best by 49 s, missed the world record (2:09:56) by 68 s, the
third fastest women's marathon ever; projected finish on the broadcast graphic 2:09:53 at 1:07:10.
Sources: BMW BERLIN-MARATHON "Finish Women" (https://youtu.be/kF2FgCAfKgY, English commentary, no music) and Abbott
World Marathon Majors highlights (https://youtu.be/SZvi5gYI-9A, music under it: only its Demucs vocals stem
work/youtube/tg_vox_380.wav is used, as a crowd bed).
Run: python3 plans11/build_b1.py && python3 pipeline/bench.py plans11/b1_tigst_assefa_berlin.json
"""
import sys

sys.path.insert(0, "plans11")
from newscommon import Short, Speech, Cutter, words, word_captions  # noqa: E402

F, H = "kF2FgCAfKgY", "SZvi5gYI-9A"
o = Short("b1_tigst_assefa_berlin", "*68 seconds* from\nthe world record :broken-heart:",
          "68 seconds from the world record 💔 #shorts", folder="plans11")
c = Cutter(o)
sp = Speech(o, [(F + ".mp4", 0.0, 59.0)], words(F))
CROWD = [("tg_vox_380.wav", 380.0, 420.0)]


def info(t, d, text, y=0.5):
    o.cap(t, d, text, style="big", y=y)


def crowd(a, dur, t, db=-4):
    o.vox(CROWD, a, dur, t, db=db)


# 1. hook: she collapses after the line
crowd(409.0, 1.6, 0.0)
s = c.v(H, 409.2, 1.6, cx=0.5, cy=0.45, zoom=(1.05, 1.1))
o.hit(s, 0.0, zoom=1.12, amount=0.5, db=-3)
info(0.0, 1.6, "SHE WAS ON\n*WORLD RECORD* PACE", y=0.66)
# 2. the broadcast graphic: projected 2:09:53
t = o.t
crowd(381.0, 2.2, t, db=-8)
c.v(H, 154.6, 2.2, cx=0.27, cy=0.5, zoom=(1.0, 1.04))
info(t, 2.2, "PROJECTED *2:09:53*\nWORLD RECORD ~2:09:56~", y=0.62)
# 3. "and the wheels came off in the last kilometre or so"
sp.add(20.4, 24.7, o.t + 0.05)
d = c.until(sp.out(22.3))
c.v(H, 380.5, d, cx=0.5, cy=0.5, zoom=(1.1, 1.14),                           # running, whole body in (the camera
    path=[[0, 1.1, 0.5, 0.5], [d, 1.14, 0.4, 0.5]])                           # cuts to her legs at 384.4)
s = c.v(H, 389.4, c.until(sp.out(24.7) + 0.1), cx=0.48, cy=0.5, zoom=(1.3, 1.36))   # she stops, holding her leg
c.hit_at(s, sp.out(23.12), zoom=1.1, amount=0.4, db=-5)
# 4. she keeps going
t = o.t
o.clip(F + ".mp4", 36.8, 1.7, t, db=-6, af="film")
c.v(F, 36.8, 1.7, cx=0.5, cy=0.45, zoom=(1.05, 1.1))                       # her face, hurting
info(t, 1.7, "SHE KEEPS GOING :broken-heart:", y=0.68)
# 5. the line: 2:11:04
t = o.t
crowd(403.0, 2.6, t, db=-2)
s = c.v(H, 403.0, 2.6, cx=0.5, cy=0.5, zoom=(1.0, 1.04))                    # clock 2:11:02 to 2:11:04
o.hit(s, 1.6, zoom=1.12, amount=0.5, db=-2)
info(t + 1.6, 1.0, "*2:11:04* :trophy:", y=0.62)
# 6. "She is the Berlin Marathon champion once again"
sp.add(51.8, 56.15, o.t + 0.05)
c.v(H, 405.8, 1.4, cx=0.5, cy=0.5, zoom=(1.0, 1.04))
s = c.v(H, 407.0, c.until(sp.out(56.15) + 0.1), cx=0.42, cy=0.5, zoom=(1.0, 1.06))   # she goes down
c.hit_at(s, sp.out(53.7), zoom=1.1, amount=0.4, db=-5)
# 7. 68 seconds
t = o.t
crowd(412.0, 2.4, t, db=-6)
s = c.v(H, 412.0, 2.4, cx=0.5, cy=0.45, zoom=(1.05, 1.1))                  # kneeling, head down
o.hit(s, 0.0, zoom=1.1, amount=0.4, db=-4)
info(t, 2.4, "*68 SECONDS*\nOFF THE WORLD RECORD", y=0.68)
# 8. "It'll still put her third fastest in history"
sp.add(4.45, 9.3, o.t + 0.05)
d = c.until(sp.out(9.3) + 0.5)
s = c.v(H, 416.4, d, cx=0.52, cy=0.5, zoom=(1.0, 1.04),                    # helped away, kept on her
        path=[[0, 1.0, 0.52, 0.5], [1.6, 1.02, 0.47, 0.5], [2.4, 1.03, 0.49, 0.5], [d, 1.04, 0.38, 0.5]])
c.hit_at(s, sp.out(5.9), zoom=1.1, amount=0.45, db=-3)                     # "third"
o.caps += word_captions(sp.words, y=0.68, style="wordcap", palette=["*", "~"],
                        force={"wheels", "last", "kilometer", "champion", "again", "third", "fastest", "history"})
o.save(open_fade=0.0)
