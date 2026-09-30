"""n2: Niall Darwen, 5th in 2025 to 2026 Classic Physique Olympia champion, in his own words (news, 2026-09-26).
Facts (fitnessvolt.com 2026 Classic Physique Olympia results, generationiron.com scorecards): Darwen (UK) won ahead of
Mike Sommerfeld and defending champion Ramon Dino (3rd); 11th, 5th, 1st in three Olympias; fifth man ever to win the
Classic Olympia. Interview: he was moved to the middle in the final callout of prejudging.
Voice: NPCNewsOnline interview hV40SXWvdJM (backstage, medal on). Pictures: interview in sync, his solo posing routine
W1WT_ofIRfE (Fitness Routine English, vertical phone clip in the middle of a 16:9 frame), final callout D199ZS-S4qU
(Fernando Arroyo, Niall in the middle).
Run: python3 plans11/build_n2.py && python3 pipeline/bench.py plans11/n2_niall_darwen_classic.json
"""
import sys

sys.path.insert(0, "plans11")
from newscommon import Short, Cutter, speech, word_captions  # noqa: E402

I, SOLO, CALL = "hV40SXWvdJM", "W1WT_ofIRfE", "D199ZS-S4qU"
o = Short("n2_niall_darwen_classic", "5th last year.\nNow *Classic Olympia* champ :trophy:",
          "5th last year, now Classic Olympia champion 🏆 Niall Darwen #shorts", folder="plans11")
c = Cutter(o)
sp = speech(o, I, 354)
TALK = dict(cx=0.63, cy=0.45, zoom=(1.15, 1.2))       # face, medal and chest; NPC straps cropped out
MID = dict(cx=0.5, cy=0.58, zoom=(1.6, 1.68))          # final callout: Niall in the middle
POSE = dict(cx=0.52, cy=0.5, zoom=(1.05, 1.1))         # the vertical phone strip

# 1. hook: called to the middle (callout picture from frame 0)
sp.add(113.02, 114.4, 0.0)
s = c.v(CALL, 12.0, 1.0, **MID)                          # arms up in the middle
c.hit_at(s, sp.out(113.57), zoom=1.12, amount=0.45, db=-4)
sp.add(115.66, 116.95, o.t + 0.1)
c.sync(sp, I, sp.out(116.95) + 0.1, **TALK)             # "I was just as shocked as a crowd"
# 2. the dream
sp.add(33.58, 35.85, o.t + 0.1)
c.v(CALL, 3.0, c.until(sp.out(35.85)), **MID)
sp.add(37.3, 40.4, o.t + 0.1)
s = c.v(SOLO, 9.0, c.until(sp.out(40.4) + 0.1), cx=0.56, cy=0.58, zoom=(1.3, 1.36))   # kneeling pose: "a fantasy"
c.hit_at(s, sp.out(38.97), zoom=1.12, amount=0.45, db=-5)
# 3. the medal and the trophy
sp.add(44.58, 49.25, o.t + 0.1)
s = c.sync(sp, I, sp.out(49.25) + 0.1, **TALK)
c.hit_at(s, sp.out(48.61), zoom=1.12, amount=0.45, db=-4)
# 4. don't mess this moment up
sp.add(121.05, 122.72, o.t + 0.1)
c.v(SOLO, 0.8, c.until(sp.out(122.72) + 0.1), **POSE)   # side chest on stage
# 5. harder every day
sp.add(244.18, 246.32, o.t + 0.1)
c.sync(sp, I, sp.out(246.32), **TALK)
sp.add(247.05, 250.08, o.t + 0.1)
s = c.v(SOLO, 34.0, c.until(sp.out(250.08) + 0.1), **POSE)                  # back double bi: "harder"
c.hit_at(s, sp.out(248.59), zoom=1.12, amount=0.45, db=-5)
# 6. 1%, all in
sp.add(258.6, 261.6, o.t + 0.1)
s = c.v(SOLO, 42.0, c.until(sp.out(261.6) + 0.1), **POSE)                   # most muscular: "all in"
c.hit_at(s, sp.out(259.09), zoom=1.12, amount=0.45, db=-5)
# 7. fifth to the winner
sp.add(267.56, 270.05, o.t + 0.1)
c.v(CALL, 14.5, c.until(sp.out(268.9)), **MID)          # "to jump from fifth place"
s = c.sync(sp, I, sp.out(270.05) + 0.1, **TALK)         # "to the winner"
c.hit_at(s, sp.out(269.73), zoom=1.15, amount=0.55, db=-1)
# 8. it's coming home
sp.add(322.3, 324.76, o.t + 0.1)
c.sync(sp, I, sp.out(324.76) + 0.05, **TALK)
sp.add(325.86, 327.3, o.t + 0.05)
s = c.sync(sp, I, sp.out(327.3) + 0.5, **TALK)
c.hit_at(s, sp.out(326.51), zoom=1.12, amount=0.5, db=-2)
o.caps = word_captions(sp.words, y=0.5, style="wordcap", palette=["*", "~"],
                       force={"middle", "shocked", "dream", "fantasy", "medal", "trophy", "moment", "every",
                              "harder", "1", "all", "fifth", "winner", "home", "did"})
o.save()
