"""s1: Bodybuilders in suits, 1999 Mr. Olympia press conference (Thursday Oct 21 1999, Mandalay Bay, Las Vegas).
Sources: GETBIG.TV "Press-conference & interviews - Mr. Olympia - 1999" (https://youtu.be/Y7xBTvYgoIY) 385 to 392 and 404.5 to 414
Ronnie in the blue suit (no Russian name bar there); "Press Conference & Backstage Pump Up - The Battle For The Olympia 1999", Mocvideo Productions
(https://youtu.be/OXJhEpJiPEU), 4:3 picture inside a 16:9 frame (x 250..1665 px).
Checked on frames and whisper word times (source seconds):
  52.0 suits at the table (Nasser leaning in, blue jacket, glasses)   93.0 "Jay Cutler" called, Jay (blond) raises a hand 94.5
  101.2 "Nasser El Sonbaty" called, Nasser waves 102 to 104            118.6 "Kevin Levrone" called, name plate in shot
  155 to 185 Ronnie Coleman close-up; 180.6 "while I can only eat chicken breast and turkey breast" (to 184.0)
  381.3 Dorian Yates (caption card at 292 "Six Times Mr. Olympia"): "If I had to put money on somebody, I'd get all my
  money and I'll put it on Ronnie Coleman" (to 386.3)
  placings card: 717 "2 KEN FLEX WHEELER", 721.5 "1999 Mr. Olympia" Ronnie (inset photo x 340..1100 px), 726 back pose
  732.5 Ronnie after the win: "Second time is the best time of all. Second time lets you know that it wasn't a mistake
  for the first time around" (to 741.8)
Facts (en.wikipedia.org/wiki/1999_Mr._Olympia): finals Oct 23 1999, Mandalay Bay Arena; 1 Coleman $110,000 (his 2nd
title), 2 Flex Wheeler, 4 Levrone, 6 El Sonbaty, 14 Cutler (Olympia debut). Coleman went on to win 8 in a row (1998 to
2005). Run: python3 plans10/build_s1.py && python3 pipeline/bench.py plans10/s1_suits_1999_olympia.json
"""
import sys

sys.path.insert(0, "plans10")
from rscommon import Short  # noqa: E402

V = "OXJhEpJiPEU"
o = Short("s1_suits_1999_olympia", "Bodybuilders in suits\nhit *different* :fire:",
          "Bodybuilders in suits hit different 🔥 1999 Mr. Olympia #shorts")

s = o.shot(V, 52.0, 2.6, cx=0.56, db=-12, dim_in={"hold": 0.35, "dur": 0.2, "from": 0.1})
o.cap(0, 2.6, "1999 MR. OLYMPIA\n*PRESS CONFERENCE*")
o.hit(s, 0.4, zoom=1.1, amount=0.4)
s = o.shot(V, 65.6, 1.6, cx=0.3, cy=0.45, zoom=(1.1, 1.14), db=-10)
o.cap(s["_t0"], 1.6, "JAY CUTLER\n*FIRST* OLYMPIA")
s = o.shot(V, 101.3, 2.5, cx=0.5, db=-6)
o.cap(s["_t0"], 2.5, "NASSER\n*EL SONBATY*")
s = o.shot(V, 118.3, 2.3, cx=0.5, db=-6)
o.cap(s["_t0"], 2.3, "KEVIN *LEVRONE*")
s = o.shot("Y7xBTvYgoIY", 405.0, 2.2, cx=0.5, cy=0.38, db=-16, zoom=(1.2, 1.26))
o.cap(s["_t0"], 2.2, "THE CHAMP\n~RONNIE COLEMAN~ :crown:")
o.hit(s, 0.15, zoom=1.12, amount=0.45)
s = o.shot(V, 180.55, 3.55, cx=0.54, cy=0.38, db=-4, zoom=(1.2, 1.26))
o.cap(s["_t0"], 3.55, "\"I CAN ONLY EAT\n*CHICKEN & TURKEY*\" :poultry-leg:")
s = o.shot(V, 381.15, 2.95, cx=0.5, db=-4)
o.cap(s["_t0"], 2.95, "6X MR. OLYMPIA\n*DORIAN YATES* BETS...")
s = o.shot("Y7xBTvYgoIY", 385.0, 2.5, cx=0.5, cy=0.38, zoom=(1.2, 1.24), db=-24)  # GETBIG.TV, Ronnie in the blue suit
o.clip(V, 384.1, 2.5, s["_t0"])
o.cap(s["_t0"], 2.5, "ALL HIS MONEY ON\n~RONNIE~ :money-bag:")
o.hit(s, 1.9, zoom=1.1, amount=0.4, db=-5)
# two days later, the official placings (Mocvideo's own cards; crop to the photo)
o.sound(o.t, "whoosh", db=-10)
s = o.shot(V, 717.3, 1.6, cx=0.34, cy=0.5, audio=False, zoom=(1.2, 1.22))
o.cap(s["_t0"], 1.6, "*2 DAYS* LATER...\n2ND: FLEX WHEELER")
o.sound(o.t, "riser1", db=-12)
s = o.shot(V, 721.7, 2.6, cx=0.34, cy=0.45, audio=False, zoom=(1.2, 1.24))
o.cap(s["_t0"], 1.3, "*1ST* :trophy:\nRONNIE COLEMAN")
o.hit(s, 0.0, zoom=1.15, amount=0.55, db=-1)
o.clip(V, 732.45, 1.3, s["_t0"] + 1.3)       # "Second time..." starts over the stage photo
s = o.shot(V, 733.75, 1.95, cx=0.52, db=0)
a = s["_t0"] - 1.3
s = o.shot(V, 726.9, 1.25, cx=0.34, audio=False, zoom=(1.2, 1.24))
o.clip(V, 735.7, 1.25, s["_t0"])
o.cap(a, s["_t0"] + 1.25 - a, "\"SECOND TIME IS\n*THE BEST* OF ALL\"")
s = o.shot(V, 736.95, 5.05, cx=0.52, db=0, zoom=(1.0, 1.08))
o.cap(s["_t0"], 2.85, "\"SECOND TIME\nLETS YOU KNOW...\"")
o.cap(s["_t0"] + 2.85, 2.2, "\"IT WASN'T\n*A MISTAKE*\" :fire:")
o.hit(s, 3.3, zoom=1.12, amount=0.45, db=-5)
o.save()
