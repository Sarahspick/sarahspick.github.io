"""r1: Raul Flores, 511 kg deadlift world record (Giants Live Strongman Open, Birmingham, 2026-09-05).
Facts (giants-live.com "Thor retains Open title as Flores pulls 511kg!", 2026-09-06): 26-year-old from Mexico, 511 kg
(1,127 lb) beats Hafthor Bjornsson's 510 kg; 504 kg in prep; his late dog's tattoo on his shoulder, the dog's death is
what first sent him to the gym; Hafthor came out to pay tribute. The commentators call him Raul "Tyson" Flores.
Source: Giants Live STRONGMAN "RAUL FLORES - NEW WORLD RECORD DEADLIFT - 511KG!" (https://youtu.be/4oHrTDCgVAs), 1080p.
Voice pieces use Demucs vocals (work/youtube/fl_vox_<start>.wav, arena music and crowd bed removed); the lift keeps
the original sound (crowd roar).
Owner notes 2026-09-30: first second is the sharpest, most striking shot; faces always inside the box.
Run: python3 plans11/build_r1.py && python3 pipeline/bench.py plans11/r1_raul_flores_511.json
"""
import sys

sys.path.insert(0, "plans11")
from newscommon import Short, Speech, Cutter, words, word_captions  # noqa: E402

V = "4oHrTDCgVAs"
o = Short("r1_raul_flores_511", "*511 KG* deadlift\nWORLD RECORD :flag-mx:",
          "511 KG deadlift world record 🇲🇽 Raul Flores #shorts", folder="plans11")
c = Cutter(o)
VOX = [("fl_vox_0.wav", 0.0, 14.0), ("fl_vox_140.wav", 140.0, 200.0), ("fl_vox_470.wav", 470.0, 502.0),
       ("fl_vox_660.wav", 660.0, 700.0), ("fl_vox_550.wav", 550.0, 575.0)]
sp = Speech(o, VOX, words(V))
WIDE = dict(cx=0.5, cy=0.52, zoom=(1.4, 1.46))          # platform: Flores fills the box, name strap cropped out

# 1. hook: the roar through the sparks right after the lift (original sound)
s = c.v(V, 209.0, 0.9, cx=0.47, cy=0.38, zoom=(1.15, 1.2))                  # laughing, hands on his chest
c.hit_at(s, 0.05, zoom=1.12, amount=0.5, db=-3)
c.v(V, 211.0, 1.2, path=[[0, 1.15, 0.3, 0.4], [1.2, 1.15, 0.5, 0.4]], ease="linear")   # arms wide in the sparks
o.clip(V + ".mp4", 196.4, 2.1, 0.0, db=-3, af="film")
o.cap(0.0, 2.1, "*511 KG*", style="wordcap")
# 2. rising star from Mexico, 26
sp.add(0.5, 9.1, o.t + 0.05, db=0)
c.v(V, 261.0, c.until(sp.out(4.02)), cx=0.5, cy=0.42, zoom=(1.15, 1.2))    # with the belt: "rising star from Mexico"
c.v(V, 623.6, c.until(sp.out(9.1) + 0.1), still=True, cx=0.5, cy=0.42, zoom=(1.25, 1.3))   # face to camera: "Raul Flores, 26"
# 3. the world record attempt
sp.add(153.2, 161.1, o.t + 0.1, db=0)
c.v(V, 175.0, c.until(sp.out(155.56)), cx=0.5, cy=0.5, zoom=(1.1, 1.15))   # hands strapped to the bar
s = c.v(V, 181.0, c.until(sp.out(161.1)), **WIDE)                           # set up: "511 kilograms"
c.hit_at(s, sp.out(157.6) - s["_t0"], zoom=1.1, amount=0.4, db=-5)
# 4. the lift, original sound
t = o.t
s = c.v(V, 183.6, 7.9, audio=True, db=-3, af="film", **WIDE)
c.hit_at(s, t + 5.8, zoom=1.14, amount=0.55, db=-1)                         # lockout
c.v(V, 195.3, 1.3, audio=True, db=-3, af="film", cx=0.5, cy=0.5, zoom=(1.3, 1.36))   # drops it, sparks
# 5. the tattoo: his late dog
sp.add(679.65, 684.85, o.t + 0.1, db=0)
c.v(V, 266.0, c.until(sp.out(682.9)), cx=0.5, cy=0.42, zoom=(1.15, 1.2))   # face to camera (held, the camera then pans to his shoulder): "started to go to the gym"
c.v(V, 711.0, c.until(sp.out(684.85) + 0.1), cx=0.64, cy=0.38, zoom=(1.15, 1.2))   # shows the tattoo: "his pet died"
sp.add(691.95, 696.2, o.t + 0.1, db=0)
s = c.v(V, 712.8, c.until(sp.out(696.2) + 0.1), cx=0.62, cy=0.38, zoom=(1.2, 1.25))
c.hit_at(s, sp.out(695.6), zoom=1.1, amount=0.45, db=-4)                    # "famous"
# 6. Hafthor, whose record he broke
sp.add(477.3, 480.85, o.t + 0.1, db=0)
sp.add(483.2, 485.95, o.t + 3.65, db=0)
c.sync(sp, V, sp.out(480.85) + 0.1, cx=0.6, cy=0.42, zoom=(1.2, 1.25))              # Hafthor: "26 years old, that's crazy"
s = c.sync(sp, V, sp.out(485.95) + 0.5, cx=0.6, cy=0.42, zoom=(1.2, 1.25))          # "the sky is the limit"
c.hit_at(s, sp.out(484.6), zoom=1.12, amount=0.5, db=-2)                    # "sky is the limit"
o.caps += word_captions(sp.words, y=0.5, style="wordcap", palette=["*", "~"],
                        force={"star", "mexico", "26", "world", "511", "tattoo", "gym", "died", "famous", "crazy",
                               "limit"})
o.save(open_fade=0.25)   # owner: the first second must grab, so only a short fade in
