"""e1: Eddie Hall's 500 kg deadlift, the lift that almost killed him (World Deadlift Championships, Leeds, 2016).
Source: Giants Live STRONGMAN, "Eddie STRONGMAN, UNSEEN footage "COST of 500kg on Eddie Hall" | DEADLIFT WORLD RECORD
1102lbs" (https://youtu.be/-K0chGkV0IE, saved as work/youtube/K0chGkV0IE.mp4). The documentary has music under it, so
all sound comes from Demucs vocals copies: eh_vox_a.wav = 175 to 300 s, eh_vox_b.wav = 455 to 545 s,
eh_vox_c.wav = 585 to 603 s (voices and crowd only).
Checked on frames and whisper word times (source seconds):
  58.5 card "1 year later, 2016 World Deadlift Championships, Leeds, United Kingdom"
  174 to 181 Eddie's face before the lift; 184.0 "I'm here to prove a lot of people wrong today. People say it isn't
  possible" (to 187.6); 209 face, 219.5 hands and straps, 226.5 head down
  front camera: bar leaves the floor 240.3, lockout 242.3; 247.7 to 265 face close-up (nose bleeding from 250)
  272.4 he drops to the floor after the lift; 290.6 gasping, blood on the lip; 384 and 391 paramedics backstage
  interview (4 years later): 467.9 "picture myself on a motorway, in a car accident, with my kids trapped under a car,
  lifting a car off of my kids" (to 475.2); 484.9 "and I don't remember doing the lift. I just remember waking up at
  the top and then waking up at the bottom" (to 490.1); 529.4 "Blood pressure's unreadable, so over the 200s" (to
  532.7); 593.9 "Very lucky to be alive" (to 595.3)
Run: python3 plans10/build_e1.py && python3 pipeline/bench.py plans10/e1_eddie_hall_500kg.json
"""
import sys

sys.path.insert(0, "plans10")
from rscommon import Short  # noqa: E402

V = "K0chGkV0IE"
VOX = [("eh_vox_a.wav", 175.0, 300.0), ("eh_vox_b.wav", 455.0, 545.0), ("eh_vox_c.wav", 585.0, 603.0)]
o = Short("e1_eddie_hall_500kg", "The lift that almost\n*killed* Eddie Hall :skull:",
          "The lift that almost killed Eddie Hall 💀 500kg deadlift #shorts")


def v(t_in, dur, sound=True, db=0, **k):
    """Shot whose own (music free) sound plays under it."""
    s = o.shot(V, t_in, dur, audio=False, **k)
    if sound:
        o.vox(VOX, t_in, dur, s["_t0"], db=db)
    return s


def say(t_src, dur, t, db=2):
    o.vox(VOX, t_src, dur, t, db=db)


# 1. the face, before anything happens
s = v(256.8, 2.4, cx=0.5, cy=0.42, zoom=(1.05, 1.1), db=-6, dim_in={"hold": 0.35, "dur": 0.2, "from": 0.1})
o.cap(0, 2.4, "*500 KG* DEADLIFT\nLEEDS, 2016 :flag-gb:")
o.hit(s, 0.45, zoom=1.12, amount=0.45)
# 2. "People say it isn't possible"
s = v(174.2, 3.7, sound=False, cx=0.5, cy=0.42, zoom=(1.05, 1.12))
say(183.95, 3.7, s["_t0"])
o.cap(s["_t0"], 1.7, "\"I'M HERE TO PROVE\nPEOPLE *WRONG*\"")
o.cap(s["_t0"] + 1.7, 2.0, "\"PEOPLE SAY\n*IT ISN'T POSSIBLE*\"")
# 3. the mind trick, over the set up (interview voice)
t3 = o.t
s = v(209.0, 2.9, sound=False, cx=0.5, cy=0.42, zoom=(1.05, 1.1))
s = v(219.6, 2.4, sound=False, cx=0.5, zoom=(1.1, 1.16))
s = v(226.6, 2.1, sound=False, cx=0.5, zoom=(1.05, 1.12))
say(467.75, 7.45, t3)
o.cap(t3, 3.1, "HIS MIND TRICK :brain:\n\"A *CAR ACCIDENT*\"")
o.cap(t3 + 3.1, 2.55, "\"MY KIDS TRAPPED\n*UNDER A CAR*\"")
o.cap(t3 + 5.65, 1.8, "\"LIFTING A CAR\n*OFF MY KIDS*\"")
o.sound(t3 + 3.2, "boom", db=-9)
# 4. the lift (front camera), lockout 242.3
s = v(239.7, 3.2, db=0, cx=0.47, cy=0.55, path=[[0, 1.0, 0.47, 0.55], [2.5, 1.12, 0.47, 0.5], [3.2, 1.14, 0.47, 0.5]])
o.cap(s["_t0"], 2.6, "1,102 LBS...")
o.cap(s["_t0"] + 2.6, 0.6, "*WORLD RECORD* :trophy:")
o.sound(s["_t0"] + 2.6, "riser1", db=-14)
o.hit(s, 2.6, zoom=1.15, amount=0.55, db=-1)
# 5. what he remembers (interview voice over the drop and the gasp)
t5 = o.t
s = v(272.3, 2.5, sound=False, cx=0.45, zoom=(1.0, 1.05))
s = v(290.5, 2.9, sound=False, cx=0.5, cy=0.4, zoom=(1.05, 1.1))
say(272.3, 2.5, t5, db=-8)   # the arena under the voice
say(290.5, 2.9, t5 + 2.5, db=-10)
say(484.85, 5.35, t5 - 0.05, db=2)
o.cap(t5, 2.6, "\"I DON'T REMEMBER\n*DOING THE LIFT*\"")
o.cap(t5 + 2.6, 2.8, "\"WAKING UP\n*AT THE BOTTOM*\"")
# 6. backstage
s = v(384.2, 1.8, sound=False, cx=0.5, zoom=(1.0, 1.04))
s2 = v(391.2, 1.7, sound=False, cx=0.45, zoom=(1.05, 1.1))
say(529.4, 3.5, s["_t0"])
o.cap(s["_t0"], 3.5, "BLOOD PRESSURE\n*OVER 200* :anatomical-heart:")
o.hit(s, 0.3, zoom=1.1, amount=0.4, db=-6)
# 7. "Very lucky to be alive", then the skull ending on the bloody face
s = v(593.7, 1.9, cx=0.5, zoom=(1.05, 1.1))
o.cap(s["_t0"], 1.9, "\"VERY LUCKY\n*TO BE ALIVE*\"")
end = o.t
s = v(259.4, 3.0, sound=False, cx=0.5, cy=0.42, zoom=(1.12, 1.18), still=True, bw=True, vid_darken=0.62,
      vignette=0.7, whip_in=0.18)
say(295.0, 3.0, end, db=-8)      # the crowd keeps going
o.caps.append({"t": round(end - 0.05, 2), "d": 3.05, "text": ":skull:", "style": "big", "anim": "rise", "size": 190,
               "x": 0.5, "y": 0.52})
o.sound(end, "whoosh", db=-8)
o.save(title_end=end)
