"""mp1: 2026 Men's Physique Olympia results, 5th to 1st (fast countdown, plans11/countdown.py).
Facts (fitnessvolt.com 2026 Men's Physique Olympia results, middleeasy.com, and the announcer): 5 Brandon Hendrickson
$6,000, 4 Erin Banks $7,000, 3 Kyron Holden $12,000, 2 Ali Bilal $20,000 (third straight 2nd), 1 Ryan Terry $50,000,
his 4th straight title (ties Jeremy Buendia's record).
Source: OlympiaTV "2026 Olympia Men's Physique - OFFICIAL REPLAY" (https://youtu.be/0wGhJgjDAXU); Demucs vocals
work/youtube/mp_vox.wav (980 to 1200 s). On stage Ryan Terry is on the right in blue shorts, Ali Bilal on the left
in white and maroon; Ryan drops into a squat at "and four-time" (1188), before his name (1189.4).
Run: python3 plans11/build_mp1.py && python3 pipeline/bench.py plans11/mp1_mens_physique_results.json
"""
import sys

sys.path.insert(0, "plans11")
from countdown import Countdown  # noqa: E402

k = Countdown("mp1_mens_physique_results", "Who won the 2026\n*Men's Physique* Olympia? :trophy:",
              "Who won the 2026 Men's Physique Olympia? 🏆 #shorts", "0wGhJgjDAXU", [("mp_vox.wav", 980.0, 1200.0)])
o = k.o
# label over the pose, then the same pose zoomed in (t0, athlete x, name, head y, ...)
k.place("*5TH* PLACE", 1016.2, 0.6, (1002.0, 1003.5), 0.35, 1.8, "BRANDON HENDRICKSON\n*$6,000*")
k.place("*4TH* PLACE", 1069.0, 0.55, (1037.5, 1038.9), 0.17, 1.8, "ERIN BANKS\n*$7,000*", cx_end=0.57)
k.place("*3RD* PLACE", 1120.3, 0.55, (1089.6, 1090.8), 0.17, 1.8, "KYRON HOLDEN\n*$12,000*", cx_end=0.62)
# the last two
t = o.t
k.say(1146.65, 1149.75, t + 0.05)                                  # "Ali and Ryan Terry in the center, please"
k.shot(1170.0, 3.1, path=[[0, 1.0, 0.34, 0.5], [3.1, 1.0, 0.6, 0.5]])   # pan from Ali to Ryan
k.big(t, 3.1, "LAST ~2~ STANDING")
t = o.t
k.say(1175.95, 1177.45, t)                                         # "to your winner"
k.shot(1180.0, 1.5, cx=0.47, zoom=(1.0, 1.02))
k.big(t, 1.5, "ALI OR RYAN?")
# the reveal: "and four-time ..." Ryan drops into a squat, then "Ryan Terry"
t = o.t
k.say(1185.9, 1190.6, t)
s = k.shot(1185.9, 4.7, cx=0.62, cy=0.47, zoom=(1.0, 1.0),     # follow Ryan, the source camera pushes in on him
           path=[[0, 1.0, 0.62, 0.47], [1.7, 1.0, 0.55, 0.47], [2.5, 1.0, 0.51, 0.47], [4.7, 1.0, 0.5, 0.47]])
s.setdefault("tint", []).append({"at": 2.1, "dur": 0.45, "amount": 0.4, "color": [255, 200, 40]})
o.hit(s, 2.1, zoom=1.06, amount=0.55, db=-1)                     # small punch: his hands on his head stay in
k.big(t + 2.1, 0.8, "*RYAN TERRY* WINS :trophy:\n*$50,000*", y=0.3)    # over his head while he squats
k.big(t + 2.9, 1.8, "*RYAN TERRY* WINS :trophy:\n*$50,000*", y=0.72)   # under it once he stands
t = o.t
k.say(1191.9, 1194.3, t)                                           # "congratulations Ryan, wow"
s = k.shot(1230.8, 2.4, cx=0.5)                                    # arms raised with the gold
o.hit(s, 0.0, zoom=1.1, amount=0.45, db=-4, sound="punch")
k.big(t, 2.4, "*4TH* TITLE IN A ROW :fire:", y=0.64)
t = o.t
k.say(1197.0, 1198.8, t)                                          # "congratulations Ali, you runner-up" (runs 1 s past the cut)
k.shot(1193.95, 0.6, cx=0.22, cy=0.45)  # Ali smiling, face clear (the camera swings off him at 1194.6)
k.shot(1196.5, 1.2, cx=0.38, cy=0.45)   # Ali and Ryan hug, Ali's face in profile
k.big(t, 1.8, "~2ND~ ALI BILAL\n*$20,000*", y=0.66)
k.save()
