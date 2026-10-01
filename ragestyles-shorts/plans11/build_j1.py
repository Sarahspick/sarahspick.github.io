"""j1: Jonah (jonah_calisthenics), 15 years old, takes on three calisthenics records in 30 minutes (2026-09-27).
Source: Andry Strong, "This 15-Year-Old Is Stronger Than World Champions" (https://youtu.be/tcDTdFKOXno), uploaded
2026-09-27. Results in the video: 51 planche push-ups in one minute (targets in the video: 47 unofficial best by Melvyn,
37 Guinness), 11 planche presses to handstand (record 17, Viktor Kamenov, not broken), 22 unbroken 90 degree handstand
push-ups (Guinness record 16, Willy Weldens, Paris 2014). These are the video's own attempts, judged by Andry, not
adjudicated by Guinness; the captions only use their words.
Music runs under the attempts, so every voice piece comes from the Demucs vocals (work/youtube/jo_vox_<start>.wav).
The first 50 s of the source carry the creator's own burnt-in captions, so those pictures are not used.
Run: python3 plans11/build_j1.py && python3 pipeline/bench.py plans11/j1_jonah_15_records.json
"""
import sys

sys.path.insert(0, "plans11")
from newscommon import Short, Speech, Cutter, words, word_captions  # noqa: E402

V = "tcDTdFKOXno"
o = Short("j1_jonah_15_records", "He's only *15* :flushed-face:",
          "He's only 15 😳 #calisthenics #shorts", folder="plans11")
c = Cutter(o)
VOX = [("jo_vox_0.wav", 0.0, 7.0), ("jo_vox_150.wav", 150.0, 196.0), ("jo_vox_212.wav", 212.0, 224.0),
       ("jo_vox_330.wav", 330.0, 336.0), ("jo_vox_825.wav", 825.0, 880.0)]
sp = Speech(o, VOX, words(V))

# counters and the creator's logo sit in the top 12 % of the frame: shots with them use zoom >= 1.15 and cy 0.56 (planche shots keep the whole counter and timer in instead: cx 0.74, zoom 1)
# 1. hook: "This kid is 15 years old and he can do skills that even world champions cannot do."
sp.add(0.0, 5.7, 0.0)
s = c.v(V, 118.6, 1.0, cx=0.74, cy=0.5, zoom=(1.0, 1.03))        # full planche on the parallettes, counter at 21
c.hit_at(s, 0.05, zoom=1.1, amount=0.45, db=-4)
c.v(V, 846.4, 1.6, cx=0.52, cy=0.56, zoom=(1.15, 1.18))               # 90 degree handstand push-up, rep 22
s = c.v(V, 124.0, c.until(sp.out(5.7) + 0.1), cx=0.74, cy=0.5, zoom=(1.0, 1.05))
c.hit_at(s, sp.out(4.4), zoom=1.1, amount=0.4, db=-5)              # "world champions"
# 2. planche push-ups in one minute: 50... 51
sp.add(152.8, 157.95, o.t + 0.1)
c.sync(sp, V, sp.out(157.95), cx=0.74, cy=0.5, zoom=(1.0, 1.03))
sp.add(165.6, 168.2, o.t + 0.05)
s = c.sync(sp, V, sp.out(168.2) + 0.1, cx=0.74, cy=0.5, zoom=(1.0, 1.04))   # whole frame: he stands up, counter reads 51
c.hit_at(s, sp.out(166.8), zoom=1.14, amount=0.55, db=-1)         # "51 reps"
sp.add(188.9, 193.95, o.t + 0.1)
c.sync(sp, V, sp.out(191.68), cx=0.4, cy=0.45, zoom=(1.1, 1.15))   # Andry: "you broke the world record"
s = c.v(V, 127.0, c.until(sp.out(193.95) + 0.1), cx=0.74, cy=0.5, zoom=(1.0, 1.05))   # "planche push-up in one minute"
# 3. Jonah: all I did was train
sp.add(214.88, 223.1, o.t + 0.1)
c.sync(sp, V, sp.out(219.1), cx=0.55, cy=0.45, zoom=(1.15, 1.2))   # close-up
s = c.sync(sp, V, sp.out(223.1) + 0.1, cx=0.7, cy=0.45, zoom=(1.1, 1.15))
c.hit_at(s, sp.out(222.52), zoom=1.1, amount=0.4, db=-5)           # "incorrectly"
# 4. never stopped because of pain
sp.add(332.8, 334.3, o.t + 0.1)
s = c.sync(sp, V, sp.out(334.3) + 0.1, cx=0.8, cy=0.4, zoom=(1.15, 1.2))
c.hit_at(s, sp.out(334.08), zoom=1.1, amount=0.4, db=-5, sound="punch")
# 5. handstand push-ups: 16, 17, 18 ... 22
sp.add(828.95, 835.35, o.t + 0.1)
c.sync(sp, V, sp.out(835.35), cx=0.52, cy=0.56, zoom=(1.15, 1.18))
sp.add(847.0, 849.6, o.t + 0.05)
s = c.sync(sp, V, sp.out(849.6) + 0.2, cx=0.52, cy=0.56, zoom=(1.15, 1.18))
c.hit_at(s, sp.out(849.26), zoom=1.15, amount=0.55, db=-1)        # "yeah!" rep 22 locked out
# 6. one of the strongest pushers in the world, only 15
sp.add(869.7, 873.45, o.t + 0.1)
c.sync(sp, V, sp.out(873.45), cx=0.52, cy=0.45, zoom=(1.0, 1.04))  # fist bump
sp.add(876.7, 877.98, o.t + 0.05)
s = c.sync(sp, V, sp.out(877.98) + 0.5, cx=0.78, cy=0.42, zoom=(1.15, 1.2))   # Jonah: "you are only 15"
c.hit_at(s, sp.out(877.62), zoom=1.12, amount=0.5, db=-2)
# Andry counts the last digit ("one, two, three" for 41, 42, 43); the on-screen counter shows the reps, so those
# words get no caption, only the milestones ("50 reps", "51 reps", 16 to 22 on the handstand push-ups) do
DIGITS = {"one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "okay"}
cw = [w for w in sp.words if not (w[0] < sp.out(168.2) + 0.01 and w[0] >= sp.out(152.8) - 0.01
                                  and w[2].strip(",.!?").lower() in DIGITS)]
o.caps = word_captions(cw, y=0.5, style="wordcap", palette=["*", "~"],
                       force={"15", "champions", "50", "51", "world", "record", "train", "progress", "incorrectly",
                              "pain", "16", "17", "18", "22", "strongest"})
o.save(open_fade=0.25)
