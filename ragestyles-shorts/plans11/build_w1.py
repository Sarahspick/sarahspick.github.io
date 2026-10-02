"""w1: the World's Strongest Man (Mitchell Hooper) vs a 405 lb bench, with Ronnie Coleman judging (2026-09-27).
Source: Jesse James West "20 Fitness YouTubers Fight For $20,000" (https://youtu.be/TWbA_Xw5BFM, uploaded
2026-09-27, St. Jude fundraiser). In the bench round each lifter takes 125% of body weight; Mitch's was over 400 lb
(405 on the bar); he had to beat 16 reps and got 10, so he is out. Ronnie Coleman (8x Mr. Olympia) is the guest
judge. Music runs under the video: voices from Demucs vocals work/youtube/jw1.wav (676 to 816 s).
The source carries its own burnt-in speaker captions at the bottom and a rep counter top left: shots are framed
(zoom >= 1.15, cy 0.45) to keep the bottom captions out. Faces fill the upper half of the close ups: word
captions run at y 0.7 and the info lines at y 0.86. Ronnie's line is written as the source's own caption has
it ("I think you get 50").
Run: python3 plans11/build_w1.py && python3 pipeline/bench.py plans11/w1_hooper_405_bench.json
"""
import sys

sys.path.insert(0, "plans11")
from newscommon import Short, Speech, Cutter, words, word_captions  # noqa: E402

V = "TWbA_Xw5BFM"
o = Short("w1_hooper_405_bench", "World's Strongest Man\nvs *405 lb* bench :exploding-head:",
          "World's Strongest Man vs 405 lb bench 🤯 #shorts", folder="plans11")
c = Cutter(o)
wd = [(s, e, "you" if (w.lower().startswith("i") and 758.9 < s < 759.3) else w) for s, e, w in words("jw1")]
wd = [x for x in wd if not (759.1 < x[0] < 759.42 and x[2].lower() == "can")]   # "I think I can get 50" -> "I think you get 50"
sp = Speech(o, [("jw1.wav", 676.0, 816.0)], wd)
K = dict(cy=0.45, zoom=(1.15, 1.2))


def info(t, d, text, y=0.86):
    o.cap(t, d, text, style="big", y=y)


# 1. hook: Ronnie Coleman, "Lightweight baby, lightweight, yeah!"
sp.add(684.1, 685.65, 0.0)
s = c.v(V, 689.6, 1.6, path=[[0, 1.15, 0.45, 0.42], [1.6, 1.18, 0.6, 0.42]])   # Ronnie in his chair, the camera follows him
o.hit(s, 0.0, zoom=1.12, amount=0.5, db=-3)
# 2. "... Mitchell Hooper, the world's strongest man"
sp.add(729.2, 732.05, o.t + 0.05)
s = c.v(V, 729.6, c.until(sp.out(732.05) + 0.05), cx=0.52, cy=0.45, zoom=(1.1, 1.18))
c.hit_at(s, sp.out(731.3), zoom=1.1, amount=0.4, db=-5)
# 3. "So 125% of his body weight was over 400 pounds"
sp.add(738.8, 741.95, o.t + 0.05)
s = c.v(V, 739.0, c.until(sp.out(741.95) + 0.05), cx=0.72, **K)            # the plates going on
c.hit_at(s, sp.out(741.22), zoom=1.12, amount=0.45, db=-4)
# 4. "we put 405 on the bench, what would you have hit?" "405, I would have got... 25." "25?"
sp.add(746.55, 748.15, o.t + 0.05)
c.v(V, 746.8, c.until(sp.out(748.15)), cx=0.5, cy=0.42, zoom=(1.2, 1.24))
sp.add(748.6, 750.25, o.t + 0.05)
c.v(V, 748.6, c.until(sp.out(750.25)), cx=0.42, cy=0.42, zoom=(1.2, 1.24))   # Ronnie
sp.add(751.85, 752.3, o.t + 0.05)
s = c.v(V, 751.4, c.until(sp.out(752.3) + 0.05), cx=0.42, cy=0.42, zoom=(1.2, 1.24))
c.hit_at(s, sp.out(751.88), zoom=1.12, amount=0.5, db=-3)
sp.add(752.85, 753.35, o.t + 0.05)
c.v(V, 752.9, c.until(sp.out(753.35) + 0.05), cx=0.58, **K)               # Mitch: "25?"
# 5. "What do you think I can tap into?" "I think you get 50." "50?!"
sp.add(756.95, 757.95, o.t + 0.05)
c.v(V, 756.9, c.until(sp.out(757.95)), cx=0.47, cy=0.42, zoom=(1.2, 1.24))
sp.add(758.65, 759.85, o.t + 0.05)
s = c.v(V, 758.7, c.until(sp.out(759.85)), cx=0.42, cy=0.42, zoom=(1.2, 1.24))
c.hit_at(s, sp.out(759.44), zoom=1.12, amount=0.5, db=-3)
sp.add(760.35, 760.85, o.t + 0.05)
c.v(V, 760.3, c.until(sp.out(760.85) + 0.15), cx=0.56, **K)               # "50?!"
t = o.t
o.clip("jw1.wav", 764.2 - 676.0, 1.3, t, db=0)
c.v(V, 764.2, 1.3, cx=0.48, cy=0.45, zoom=(1.0, 1.04))                     # Ronnie and Mitch, heads together laughing
# 6. the set: needs 16
sp.add(785.3, 790.35, o.t + 0.05)                                         # "8, 9, look for 10"
c.v(V, 785.0, c.until(sp.out(787.5)), cx=0.45, cy=0.45, zoom=(1.0, 1.03))
c.v(V, 789.0, c.until(sp.out(790.35)), cx=0.5, cy=0.5, zoom=(1.0, 1.04))
info(sp.out(785.3), sp.out(790.35) - sp.out(785.3), "NEEDS *16* REPS")
sp.add(794.2, 794.98, o.t + 0.05)                                         # "That's it, 10."
s = c.v(V, 794.3, c.until(sp.out(794.98) + 0.3), cx=0.45, cy=0.45, zoom=(1.0, 1.04))
c.hit_at(s, sp.out(794.92), zoom=1.14, amount=0.55, db=-1)
info(sp.out(794.92), 0.4, "*10* :skull:")
# 7. "Mitch is definitely out. See you later."
sp.add(810.3, 813.25, o.t + 0.05)
s = c.v(V, 812.85, c.until(sp.out(813.25) + 0.6), still=True, cx=0.56, **K)   # head down (held: the source then stamps a red X over him)
c.hit_at(s, sp.out(812.26), zoom=1.1, amount=0.4, db=-4, sound="punch")
o.caps += word_captions(sp.words, y=0.7, style="wordcap", palette=["*", "~"],
                        force={"lightweight", "strongest", "125", "400", "405", "25", "50", "10", "out"})
o.save(open_fade=0.0)
