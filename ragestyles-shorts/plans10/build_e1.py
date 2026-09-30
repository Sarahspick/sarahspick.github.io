"""e1 v2: How Eddie Hall lifted 500 kg, told only in his own words (World Deadlift Championships, Leeds, 2016).
Owner feedback on v1 (2026-09-30): quote summaries in "" felt like a robot, no story, no immersion, never a skull
ending. Reference: Peakzmotivation "Eddie Hall's secret that he used to lift 500 kilograms" (36M views): one continuous
story in the speaker's voice, captions are his exact words 1 to 3 at a time, speaker's face full frame, the lift lands
on the key line.
Source: Giants Live STRONGMAN, "Eddie STRONGMAN, UNSEEN footage "COST of 500kg on Eddie Hall"" (https://youtu.be/-K0chGkV0IE,
work/youtube/K0chGkV0IE.mp4). Sound only from Demucs vocals: eh_vox_a.wav 175 to 300 s, eh_vox_b.wav 455 to 545 s,
eh_vox_c.wav 585 to 603 s. Words: faster-whisper medium.en (work/youtube/eh_words_med.json); 193.98 "farming tequila"
is "five hundred kilo".
Story (source seconds):
  186.2 to 195.6 (on stage, before the lift) "People say it isn't possible. You know, people say going to the moon
  wasn't possible. Running a mile under four minutes wasn't possible. I'm here today to prove five hundred kilo
  deadlift is possible."
  462.0 to 475.0 (interview, 4 years later) "Basically, I trained my mind to a point where I was able to picture myself
  on a motorway, in a car accident, with my kids trapped under a car, lifting a car off of my kids."
  476.0 to 480.3 "And it wasn't until I locked out that deadlift, it was almost as if I just woke up"
  484.9 to 486.2 "and I don't remember doing the lift."
  597.3 to 600.9 "I get asked the question, if you could go back and do it all again... yeah." (he smiles, 600.8)
Pictures: front camera bar leaves the floor 240.3, lockout 242.3 (slowed to land on "lifting a car" and "locked out");
face close-ups 176, 192, 200, 209.6, 212.8 (before), 247.7 (at the top); 272.3 drop; interview 462 to 470 and 592 to 603.
Run: python3 plans10/build_e1.py && python3 pipeline/bench.py plans10/e1_eddie_hall_500kg.json
"""
import json
import sys

sys.path.insert(0, "plans10")
sys.path.insert(0, "pipeline")
from rscommon import Short, Speech  # noqa: E402
import wordcaps  # noqa: E402
from wordcaps import word_captions  # noqa: E402

wordcaps.STRONG.add("yeah")   # his answer stands alone

V = "K0chGkV0IE"
VOX = [("eh_vox_a.wav", 175.0, 300.0), ("eh_vox_b.wav", 455.0, 545.0), ("eh_vox_c.wav", 585.0, 603.0)]
FIX = {(193.98, "farming"): "five hundred", (194.28, "tequila"): "kilo", (185.5, "People"): None}
words = []
for f, ws in json.load(open("work/youtube/eh_words_med.json")).items():
    for s, e, w in ws:
        w2 = FIX.get((s, w), w)
        if w2:
            words.append((s, e, w2))
words.append((186.18, 186.34, "People"))
words = [(s, e, "again," if (s, w) == (600.3, "again") else w) for s, e, w in words]   # "yeah" on its own
words.sort()

o = Short("e1_eddie_hall_500kg", "How Eddie Hall lifted\n*500 KG* :exploding-head:",
          "How Eddie Hall lifted 500 kg 🤯 #shorts")
sp = Speech(o, VOX, words)
FACE = dict(cx=0.47, cy=0.4)                          # tight close-ups, face fills the frame
TALK = dict(cx=0.46, cy=0.33, zoom=(1.28, 1.34))      # interview talking head


def v(t_in, dur, **k):
    k.setdefault("zoom", (1.05, 1.1))
    return o.shot(V, t_in, round(dur, 2), audio=False, **k)


def hit_at(s, t_out, **k):
    o.hit(s, round(t_out - s["_t0"], 2), **k)


def until(t_out):
    return t_out - o.t


# 1. the hook: on stage before the lift
sp.add(186.1, 195.75, 0.0)
v(176.1, 1.1, **FACE)                                  # cut at about 1 s (owner)
v(169.7, 1.7, zoom=(1.0, 1.06))                        # the arena
v(185.5, 1.75, cx=0.45, zoom=(1.1, 1.16))              # walking to the bar
v(192.0, 1.7, **FACE)                                  # "wasn't possible"
v(193.6, 1.45, cx=0.47)                                # standing over the bar: "I'm here today"
s = v(209.3, until(sp.out(195.75)), **FACE)            # the roar
hit_at(s, sp.out(195.26), zoom=1.14, amount=0.5)       # "possible"
# 2. the secret (interview voice), picture moves from his face to the bar
t2 = sp.add(461.9, 475.3, o.t)
v(227.2, 1.8, cx=0.5)                                  # head down over the bar: "I trained my mind"
v(212.6, 1.5, **FACE)                                  # breathing
v(467.2 - (sp.out(467.2) - o.t), until(sp.out(468.5)), **TALK)   # talking, in sync: "picture myself"
v(180.6, until(sp.out(469.9)), **FACE)                 # eyes down: "on a motorway"
s = v(200.0, until(sp.out(471.5)), **FACE)             # "in a car accident"
hit_at(s, sp.out(470.36), zoom=1.1, amount=0.4, db=-6)
v(219.2, until(sp.out(473.3)), cx=0.5, zoom=(1.1, 1.14))   # hands on the bar: "kids trapped under a car"
# 3. the lift, slowed so the bar leaves the floor on "lifting a car" and locks out on "locked out"
sp.add(476.0, 480.3, sp.out(475.3) + 0.6)
lift_at, lock_at = sp.out(473.72), sp.out(477.3)
speed = round((242.3 - 240.3) / (lock_at - lift_at), 3)
start = o.t
end = lock_at + 0.9
s = v(240.3 - (lift_at - start) * speed, end - start, speed=speed, cx=0.47, cy=0.55,
      path=[[0, 1.0, 0.47, 0.55], [lock_at - start, 1.12, 0.47, 0.5], [end - start, 1.14, 0.47, 0.5]])
o.sound(lift_at, "riser1", db=-16)
hit_at(s, lock_at, zoom=1.15, amount=0.55, db=-1)
o.clip("eh_vox_a.wav", 242.3 - 175.0, 4.5, lock_at, db=-9)    # the arena erupts under his voice
v(247.7, until(sp.out(480.3) + 0.15), **FACE)          # at the top: "as if I just woke up"
# 4. "and I don't remember doing the lift"
sp.add(484.85, 486.3, o.t)
v(272.2, 1.45, cx=0.45, zoom=(1.0, 1.05))              # he drops to the floor
# 5. would he do it again
t5 = sp.add(597.25, 601.3, o.t + 0.1)
v(290.5, 1.6, cx=0.5, cy=0.4)                          # gasping, blood on his lip
s = v(597.25 + (o.t - t5), until(t5 + 4.05 + 0.8), **TALK)   # talking head, in sync, to the smile
hit_at(s, sp.out(600.76), zoom=1.12, amount=0.45, db=-4)      # "yeah"
o.caps = word_captions(sp.words, y=0.5, style="wordcap", palette=["*", "~"],
                       force={"possible", "moon", "minutes", "kilo", "mind", "motorway", "accident", "kids", "lifting",
                              "locked", "woke", "remember", "again", "yeah"})
o.save()
