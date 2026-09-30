"""w1: word-by-word "motivational" short (the Peakz look) from Nick Walker's on-stage speech after winning.
Speech (source seconds, olysp_vox.mp4 = 4505 to 4565 s, music removed), pieces packed back to back:
  host 4523.70-4531.95 "you told me every time I saw you, I'm gonna do it, I'm gonna do it, and you did it,
       you did it Nick, you are Mr. Olympia"
  Nick 4537.85-4541.40 "I want everyone out there to take this and learn this lesson, don't"
       4542.90-4545.55 "ever believe any of the negativity that you hear"
       (4545.78-4548.5 "don't ever believe the bullshit that people tell you" left out: profanity)
       4548.50-4554.90 "if you truly believe in yourself and have the confidence, you guys can do whatever you
       want, and I did that tonight"
Captions are generated from the whisper word timestamps (pipeline/wordcaps.py). Run: python3 plans9/build_w1.py
"""
import json
import sys

sys.path.insert(0, "plans9")
sys.path.insert(0, "pipeline")
from olycommon import Short, REVEAL  # noqa: E402
from wordcaps import word_captions  # noqa: E402

PIECES = [(4523.70, 4531.95), (4537.85, 4541.40), (4542.90, 4545.55), (4548.50, 4554.90)]
o = Short("w1_nick_walker_message", "Nick Walker's message\nto every *doubter* :fire:",
          "Nick Walker's message to every doubter 🔥 #shorts")

# speech on the output timeline
t, maps = 0.0, []
for a, b in PIECES:
    o.clip(a, round(b - a, 2), t, db=2)
    maps.append((a, b, t))
    t += b - a
words = []
for seg in json.load(open("work/youtube/olyend_words.json")):
    for s, e, w in seg["w"]:
        s, e = s + 3570, e + 3570
        for a, b, t0 in maps:
            if a <= s < b and w.strip():
                words.append((round(t0 + s - a, 2), round(t0 + min(e, b) - a, 2), w))
fix = {"mr.": "MR.", "bullshit": None}
words = [(s, e, w) for s, e, w in words if fix.get(w.strip().lower(), w) is not None]

N = dict(audio=False)
# piece 1 (host, 8.25 s)
s = o.shot(3296.4, 1.6, **N); o.hit(s, 0.6, zoom=1.1, amount=0.35)            # front double biceps locks
s = o.shot(3303.9, 1.4, **N); o.hit(s, 0.6, zoom=1.1, amount=0.35)            # side chest
s = o.shot(REVEAL + 0.2, 3.3, ease="linear", **N,
           path=[[0.0, 1.0, 0.41, 0.47], [1.8, 1.0, 0.441, 0.452], [3.3, 1.0, 0.45, 0.486]])
o.hit(s, 0.46, zoom=1.15, amount=0.55, big=True)                                # "you did it" = arms up
s = o.shot(4199.6, 1.95, cx=0.52, zoom=(1.0, 1.05), **N); o.hit(s, 1.1, zoom=1.12, amount=0.45)  # "Olympia"
# piece 2 and 3 (Nick talking, close-up)
o.shot(4537.85, 3.55, cx=0.5, cy=0.42, zoom=(1.08, 1.14), **N)
o.shot(4542.9, 1.3, cx=0.5, cy=0.42, zoom=(1.14, 1.18), **N)
s = o.shot(3321.4, 1.35, **N); o.hit(s, 0.5, zoom=1.1, amount=0.35)            # rear lat spread, "negativity"
# piece 4
o.shot(4548.5, 1.9, cx=0.5, cy=0.42, zoom=(1.08, 1.14), **N)                            # "if you truly believe in yourself"
s = o.shot(3293.2, 1.4, **N); o.hit(s, 0.5, zoom=1.1, amount=0.35)             # front lat spread, "confidence"
o.shot(4139.7, 1.7, ease="linear", **N, path=[[0.0, 1.0, 0.444, 0.503], [1.7, 1.0, 0.43, 0.51]])  # confetti
s = o.shot(4199.6, 2.9, cx=0.52, zoom=(1.0, 1.05), **N); o.hit(s, 0.76, zoom=1.15, amount=0.55, big=True)  # "tonight"
assert abs(o.t - (t + 1.5)) < 0.05, (o.t, t)
o.caps = word_captions(words, y=0.5, force={"lesson", "negativity", "yourself", "confidence", "tonight"})
o.save()
