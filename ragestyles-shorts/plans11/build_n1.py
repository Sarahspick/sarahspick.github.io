"""n1: Nick Walker, 6th in 2025 to 2026 Mr. Olympia, in his own words (news, 2026-09-27).
Facts (fitnessvolt.com 2026 Mr. Olympia results, bleacherreport.com): Nick Walker won the 2026 Mr. Olympia in Las
Vegas (Sept 24 to 27) a year after placing 6th, plus the People's Champion award; Samson Dauda 2nd, Derek Lunsford 3rd.
Voice: NPCNewsOnline interview p3any6arrLM (backstage, clean) and Simon Fan's stage clip of the winning speech
eymGSjtTsAk (crowd under it, about 3.5 dB louder). Pictures: posing routine SL8THmjt3Pc (Simon Fan), parents backstage
K1AfIDawCM8 (Real Bodybuilding Podcast News), interview and speech in sync.
Story (source seconds):
  E 54.98 "I did it." (stage, hook)
  P 64.96 "When I'm on and I'm 100%, nobody's gonna out-condition me. No one will outwork me and no one will oppose me."
  P 83.44 "I don't listen to everyone has to say. I know what I can do. I know what I'm capable of and I just proved
          that tonight."
  E 140.48 "And I wouldn't be the mutant, I wouldn't be anything without my parents. And I might be Mr. Olympia, but
          they're the true winners tonight."
  E 239.21 "Don't ever believe any of the negativity that you hear. Don't ever believe the bullshit that people tell
          you. If you truly believe in yourself and have the confidence, you guys can do whatever you want, and I did
          that tonight."
Run: python3 plans11/build_n1.py && python3 pipeline/bench.py plans11/n1_nick_walker_olympia.json
"""
import sys

sys.path.insert(0, "plans11")
from newscommon import Short, Cutter, speech, word_captions  # noqa: E402

P, E, POSE, FAM = "p3any6arrLM", "eymGSjtTsAk", "SL8THmjt3Pc", "K1AfIDawCM8"
o = Short("n1_nick_walker_olympia", "6th last year.\nNow *Mr. Olympia* :trophy:",
          "6th last year, now Mr. Olympia 🏆 Nick Walker #shorts", folder="plans11")
c = Cutter(o)
sp_p, sp_e = speech(o, P, 236), speech(o, E, 288)
TALK = dict(cx=0.36, cy=0.45, zoom=(1.2, 1.25))        # interview: Nick's face and chest, NPC straps cropped out
STAGE = dict(cy=0.33, zoom=(1.6, 1.65))                  # phone clip of the speech: Nick fills the box

# 1. hook: "I did it." (stage, first frame already shows him with the medal)
sp_e.add(54.9, 55.6, 0.0, db=-2)
s = c.v(E, 54.9, 1.0, cx=0.48, **STAGE)
c.hit_at(s, sp_e.out(55.1), zoom=1.14, amount=0.5)
# 2. nobody out-conditions me
sp_p.add(64.96, 70.15, 1.05, db=1.5)
c.v(POSE, 8.6, c.until(sp_p.out(66.74)), cx=0.45, cy=0.5, zoom=(1.3, 1.36))        # front double bi: "when I'm 100%"
c.sync(sp_p, P, sp_p.out(68.1), **TALK)                                             # "nobody's gonna out-condition me"
s = c.v(POSE, 77.2, c.until(sp_p.out(70.15) + 0.1), cx=0.5, cy=0.5, zoom=(1.3, 1.36))   # most muscular: "outwork me"
c.hit_at(s, sp_p.out(68.5), zoom=1.13, amount=0.5, db=-4)
# 3. I know what I'm capable of
sp_p.add(83.44, 88.75, o.t + 0.1, db=1.5)
c.sync(sp_p, P, sp_p.out(85.46), **TALK)                                            # "I don't listen to everyone"
c.v(POSE, 44.6, c.until(sp_p.out(87.5)), cx=0.4, cy=0.44, zoom=(1.3, 1.36))         # "I know what I'm capable of"
s = c.v(E, 60.0, c.until(sp_p.out(88.75) + 0.15), cx=0.47, **STAGE)                # medal on stage: "proved that tonight"
c.hit_at(s, sp_p.out(87.96), zoom=1.14, amount=0.55, db=-2)
# 4. my parents
sp_e.add(140.45, 149.6, o.t + 0.1, db=-2)
c.sync(sp_e, E, sp_e.out(143.2), cx=0.37, **STAGE)                                  # "I wouldn't be the mutant"
c.v(FAM, 44.0, c.until(sp_e.out(146.1)), cx=0.5, cy=0.45, zoom=(1.0, 1.04))       # with mom and dad backstage
s = c.sync(sp_e, E, sp_e.out(149.6) + 0.1, cx=0.33, **STAGE)                        # "they're the true winners"
c.hit_at(s, sp_e.out(148.64), zoom=1.12, amount=0.45, db=-4)
# 5. the lesson
sp_e.add(239.15, 251.6, o.t + 0.1, db=-2)
c.sync(sp_e, E, sp_e.out(242.5), cx=0.53, **STAGE)                                 # "negativity"
c.v(POSE, 66.0, c.until(sp_e.out(245.1)), cx=0.4, cy=0.5, zoom=(1.3, 1.36))        # "the bullshit people tell you"
s = c.v(POSE, 68.6, c.until(sp_e.out(248.5)), cx=0.46, cy=0.5, zoom=(1.3, 1.4))     # biceps: "believe in yourself"
c.hit_at(s, sp_e.out(246.49), zoom=1.12, amount=0.45, db=-5)
s = c.sync(sp_e, E, sp_e.out(251.6) + 0.5, cx=0.53, **STAGE)                        # "and I did that tonight"
c.hit_at(s, sp_e.out(250.65), zoom=1.15, amount=0.55, db=-1)
o.caps = word_captions(sorted(sp_p.words + sp_e.words), y=0.5, style="wordcap", palette=["*", "~"],
                       force={"did", "100", "outwork", "capable", "proved", "mutant", "parents", "winners",
                              "negativity", "believe", "confidence", "tonight"},
                       skip={"bullshit"})
o.save()
