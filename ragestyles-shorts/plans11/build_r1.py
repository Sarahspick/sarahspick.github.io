"""r1 v2: Raul Flores, 511 kg deadlift world record (Giants Live Strongman Open, Birmingham, 2026-09-05).
v2 follows the owner's two reference shorts (Eddie Hall 500 kg edits, 10M+ views, work/ref/): cuts every 1 to 2 s,
the lift shown in real time from several angles (broadcast front, side, crowd phone with the 511 kg sign, the coach),
a slow-motion face shot at lockout with a red wash, a chromatic hit and a boom, italic action captions
("*Thor's record: 510 kg*"), the celebration held, Hafthor raising his hand.
Facts (giants-live.com "Thor retains Open title as Flores pulls 511kg!", 2026-09-06): 26-year-old from Mexico, 511 kg
beats Hafthor Bjornsson's 510 kg; his late dog Tyson's tattoo; the dog's death first sent him to the gym.
Sources: Giants Live STRONGMAN 4oHrTDCgVAs (broadcast, voices via Demucs fl_vox_*.wav), Sebastian Oreb and Hafthor
Bjornsson Q3N1mrkxMto (side angle, Hafthor raising his hand), David Archer Mm3frQ6HAv4 (crowd phone, 511 kg sign).
Run: python3 plans11/build_r1.py && python3 pipeline/bench.py plans11/r1_raul_flores_511.json
"""
import sys

sys.path.insert(0, "plans11")
from newscommon import Short, Speech, Cutter, words, word_captions  # noqa: E402

V, SIDE, FAN = "4oHrTDCgVAs", "Q3N1mrkxMto", "Mm3frQ6HAv4"
o = Short("r1_raul_flores_511", "The heaviest deadlift\n*in history* :exploding-head:",
          "The heaviest deadlift in history 😳 #shorts", folder="plans11")
c = Cutter(o)
VOX = [("fl_vox_0.wav", 0.0, 14.0), ("fl_vox_140.wav", 140.0, 200.0), ("fl_vox_470.wav", 470.0, 502.0),
       ("fl_vox_660.wav", 660.0, 700.0)]
sp = Speech(o, VOX, words(V))
WIDE = dict(cx=0.5, cy=0.52, zoom=(1.4, 1.46))
SIDE_K = dict(cx=0.45, cy=0.46, zoom=(1.45, 1.55))
ACT = dict(style="wordcap", italic=True, y=0.66, size=58)     # "*action*" captions, under the spoken words


def act(t, d, text):
    o.cap(t, d, "\\*" + text + "\\*", **ACT)


def big_hit(s, at, db=-1):
    """The 10M-view hit: zoom punch + flash + red wash + chromatic split + boom."""
    o.hit(s, at, zoom=1.16, amount=0.55, db=db)
    s.setdefault("tint", []).append({"at": at, "dur": 0.45, "amount": 0.55, "color": [255, 30, 20]})
    s.setdefault("rgb", []).append({"at": at, "dur": 0.35, "px": 16})


# 1. hook: locked out, side angle (sharpest shot), the arena roar
s = c.v(SIDE, 83.6, 1.3, **SIDE_K)
o.clip(V + ".mp4", 189.4, 1.3, 0.0, db=-3, af="film")
big_hit(s, 0.05)
o.cap(0.0, 1.3, "*511 KG*", style="wordcap")
# 2. who he is
sp.add(1.15, 4.05, o.t + 0.05)
c.v(SIDE, 56.0, 1.4, cx=0.45, cy=0.45, zoom=(1.5, 1.6))                     # at the bar, side
c.v(V, 261.0, c.until(sp.out(4.05) + 0.05), cx=0.5, cy=0.42, zoom=(1.15, 1.2))   # "from Mexico"
sp.add(6.2, 9.1, o.t + 0.05)
s = c.v(V, 623.6, c.until(sp.out(9.1) + 0.1), still=True, cx=0.5, cy=0.4,
        path=[[0, 1.0, 0.5, 0.5], [2.8, 1.12, 0.5, 0.47]])                  # face, slow push in: "26 years of age"
c.hit_at(s, sp.out(6.26), zoom=1.08, amount=0.35, db=-6, sound="punch")
# 3. the record he is chasing
sp.add(153.4, 161.1, o.t + 0.1)
t = o.t
c.v(V, 476.6, 1.7, cx=0.6, cy=0.5, zoom=(1.05, 1.1))                        # Hafthor
act(t, 1.7, "Thor's record: 510 kg")
c.v(FAN, 7.5, 1.8, cx=0.5, cy=0.6, zoom=(1.25, 1.3))                        # the 511 kg sign
c.v(V, 175.0, 1.5, cx=0.5, cy=0.5, zoom=(1.1, 1.18))                         # chalked hands, straps
s = c.v(SIDE, 66.0, c.until(sp.out(161.1) + 0.05), path=[[0, 1.45, 0.45, 0.5], [3, 1.8, 0.42, 0.42]])   # bent over the bar
c.hit_at(s, sp.out(157.6), zoom=1.08, amount=0.4, db=-5)                   # "511"
# 4. the lift, real time, every angle; the broadcast sound runs underneath
t = o.t
o.clip(V + ".mp4", 183.6, 13.3, t, db=-3, af="film")
c.v(V, 183.6, 2.0, **WIDE)                                                  # pull starts
c.v(FAN, 12.0, 1.6, cx=0.45, cy=0.5, zoom=(1.3, 1.36))                     # crowd phone, side
c.v(V, 178.4, 1.0, cx=0.62, cy=0.45, zoom=(1.15, 1.2))                      # his coach screaming
act(o.t - 1.0, 1.0, "his coach")
c.v(SIDE, 81.6, 2.0, **SIDE_K)                                              # coming up
s = c.v(V, 188.6, 2.4, speed=0.5, interp=True, cx=0.5, cy=0.4, zoom=(2.1, 2.3))   # slow motion, his face at lockout
big_hit(s, 0.6)
act(o.t - 2.4 + 0.6, 1.8, "511 KG")
c.v(SIDE, 84.5, 1.8, **SIDE_K)                                              # holding it, face up
s = c.v(V, 194.3, 2.5, **WIDE)                                              # drops it, sparks
o.hit(s, 1.0, zoom=1.12, amount=0.5, db=-3)
# 5. celebration and Thor
t = o.t
o.clip(V + ".mp4", 196.8, 3.9, t, db=-4, af="film")
c.v(V, 209.0, 0.9, cx=0.47, cy=0.38, zoom=(1.15, 1.2))                      # laughing
c.v(V, 211.0, 1.2, path=[[0, 1.15, 0.3, 0.4], [1.2, 1.15, 0.5, 0.4]], ease="linear")   # arms wide in the sparks
s = c.v(SIDE, 143.0, 1.8, cx=0.42, cy=0.45, zoom=(1.5, 1.55))               # Hafthor raises his hand
act(o.t - 1.8, 1.8, "Thor raises his hand")
o.hit(s, 0.3, zoom=1.1, amount=0.45, db=-4)
# 6. the tattoo: his late dog Tyson
sp.add(679.65, 684.85, o.t + 0.1)
c.v(V, 266.0, c.until(sp.out(682.9)), cx=0.5, cy=0.42, zoom=(1.15, 1.2))    # "started to go to the gym"
c.v(V, 711.0, c.until(sp.out(684.85) + 0.1), cx=0.64, cy=0.38, zoom=(1.15, 1.2))   # the tattoo: "his pet died"
sp.add(691.95, 696.2, o.t + 0.1)
s = c.v(V, 712.8, c.until(sp.out(696.2) + 0.1), cx=0.62, cy=0.38,
        path=[[0, 1.2, 0.62, 0.38], [4, 1.45, 0.6, 0.34]])                  # push in on the tattoo
c.hit_at(s, sp.out(695.6), zoom=1.1, amount=0.45, db=-4)                   # "famous"
# 7. Hafthor
sp.add(477.3, 480.85, o.t + 0.1)
sp.add(483.2, 485.95, o.t + 3.65)
c.sync(sp, V, sp.out(480.85) + 0.1, cx=0.6, cy=0.42, zoom=(1.2, 1.25))     # "26 years old, that's crazy"
s = c.sync(sp, V, sp.out(485.95), cx=0.6, cy=0.42, zoom=(1.25, 1.35))       # "the sky is the limit"
big_hit(s, round(sp.out(484.6) - s["_t0"], 2), db=-2)
# 8. out on the roar
t = o.t
o.clip(V + ".mp4", 195.3, 1.4, t, db=-4, af="film")
c.v(V, 211.2, 1.4, cx=0.42, cy=0.4, zoom=(1.15, 1.2))
o.caps += word_captions(sp.words, y=0.5, style="wordcap", palette=["*", "~"],
                        force={"star", "mexico", "26", "world", "511", "gym", "died", "famous", "crazy", "limit"})
o.save(open_fade=0.25)
