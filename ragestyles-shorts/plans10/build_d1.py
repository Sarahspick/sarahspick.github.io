"""d1 v2: David Goggins, 297 lbs to Navy SEAL, told only in his own words.
Owner feedback on v1 (2026-09-30): the white card and the 16:9 clip are out (blur background, 9:16 or 3:4 box only),
the donut and milkshake B roll felt cheap, no story and no emotion. Now: his voice runs through the whole short, the
captions are his exact words 1 to 3 at a time, pictures are him (old photos, the scale, SEAL photos, the interview in
sync when he is talking). Goggins allows edits of his videos (owner).
Source: CNBC Make It, "David Goggins: How I Went From 300 Pounds To Becoming A Navy SEAL" (https://youtu.be/X3yNsomAUvw).
Music removed with Demucs: work/youtube/gg_vox.wav (0 to 290 s, same timeline). Words: faster-whisper medium.en
(work/youtube/gg_words_med.json), 269 to 275 from the small model (medium drifted there).
Story (source seconds):
  0.0 "My idea to become a Navy SEAL was me on my couch at 297 pounds" (to 4.66)
  13.44 "I got sick of being haunted by being nobody" (to 15.9)
  164.6 "People don't walk in the office trying to be a Navy SEAL weighing 297 pounds" (to 168.0)
  173.06 "And I remember looking in front of me was a height weight chart. For me, I'm 6 foot 1. I could only weigh
  191. I had to lose 106 pounds in less than three months." (to 182.9)
  191.9 "And in less than three months, I lost 106 pounds." (to 193.95)
  195.1 "I'm the only person in Navy SEAL history to be in three hell weeks in one year." (to 200.5)
  229.12 "I made a decision to myself, there's no more quitting." (to 231.8)
  269.08 "I started realizing that the mind is the most powerful weapon that we have." (to 272.95)
Pictures (CNBC seconds, no CNBC text cards in the crop): 0 to 1.5 Goggins running today, 1.5 to 2.2 running, 2.2 to
3.7 race bib 88, 3.7 to 5.0 his 297 lb photo; 13.5 to 16.3 interview (name strap cropped out); 164.5 to 169.5 photo
in a tank top (face in the pan 167.5 to 169.0 on the ffmpeg clock; OpenCV seeking reads this file about 1.2 s late); 172 to 180.5 the scale; 75 to 78.8 photo sitting (caption card cropped out); 180.6 to 183 interview;
192.6 to 194.3 SEAL portrait; 194.4 to 197.2 Hell Week photo; 201.9 log carry; 229 to 230.4 obstacle course;
230.5 cargo net; 269.6 to 273 interview.
Run: python3 plans10/build_d1.py && python3 pipeline/bench.py plans10/d1_goggins_297_to_seal.json
"""
import json
import sys

sys.path.insert(0, "plans10")
sys.path.insert(0, "pipeline")
from rscommon import Short, Speech  # noqa: E402
from wordcaps import word_captions  # noqa: E402

C = "X3yNsomAUvw"
VOX = [("gg_vox.wav", 0.0, 290.0)]
med = [tuple(w) for w in json.load(open("work/youtube/gg_words_med.json")) if not 266 <= w[0] < 275]
small = []
for line in open("work/youtube/X3yNsomAUvw_words.txt"):
    s, e, w = line.split(maxsplit=2)
    if 269.0 <= float(s) < 275:
        small.append((float(s), float(e), w.strip()))
words = sorted(med + small)

o = Short("d1_goggins_297_to_seal", "From *297 lbs*\nto Navy SEAL :fire:", "From 297 lbs to Navy SEAL 🔥 David Goggins #shorts",
          layout={"mode": "blur", "box_aspect": 0.75, "box_w": 1080, "box_top": 240, "darken": 0.5})
sp = Speech(o, VOX, words)
TALK = dict(cx=0.4, cy=0.42, zoom=(1.12, 1.18))       # interview, name strap kept out on the right


def v(t_in, dur, **k):
    k.setdefault("zoom", (1.05, 1.1))
    return o.shot(C, t_in, round(dur, 2), audio=False, **k)


def until(t_out):
    return t_out - o.t


def hit_at(s, t_out, **k):
    o.hit(s, round(t_out - s["_t0"], 2), **k)


def sync(t_end, **k):
    """Interview shot whose picture runs in sync with the voice piece playing at the current output time."""
    for a, b, t in sp.maps:
        if t - 0.01 <= o.t <= t + (b - a) + 0.01:
            return v(a + (o.t - t), until(t_end), **k)
    raise ValueError(o.t)


# 1. 297 lbs
sp.add(0.0, 4.72, 0.0)
v(0.4, 1.1, cx=0.45)                                   # running today (cut at about 1 s)
v(1.5, 0.7, cx=0.5)
v(2.3, 1.5, cx=0.46, cy=0.4)                           # race bib 88
s = v(3.75, until(sp.out(4.72) + 0.1), cx=0.47, cy=0.35, zoom=(1.2, 1.3))   # the 297 lb photo
hit_at(s, sp.out(3.36), zoom=1.14, amount=0.5)
# 2. haunted by being nobody (interview, in sync)
sp.add(13.4, 15.95, o.t)
sync(sp.out(15.95) + 0.1, **TALK)
# 3. the recruiter
sp.add(164.55, 168.0, o.t)
v(161.3, 1.35, cx=0.5)                                 # dialing the recruiter
s = v(166.9, until(sp.out(168.0)), cx=0.72, cy=0.4, path=[[0, 1.0, 0.7, 0.45], [2.1, 1.1, 0.74, 0.38]])   # the photo, face in the pan
hit_at(s, sp.out(167.06), zoom=1.1, amount=0.4, db=-6)
# 4. the height weight chart
sp.add(173.0, 182.95, o.t + 0.15)
v(172.85, until(sp.out(175.6)), cx=0.45)               # the scale: "a height weight chart"
v(75.6, until(sp.out(177.4)), cx=0.45, cy=0.3, zoom=(1.6, 1.65))   # the photo: "for me, I'm 6 foot 1"
s = v(177.3, until(sp.out(180.55)), cx=0.5, zoom=(1.1, 1.18))      # the scale: "I could only weigh 191"
hit_at(s, sp.out(178.64), zoom=1.12, amount=0.45, db=-5)
s = sync(sp.out(182.95) + 0.1, **TALK)                 # "106 pounds in less than three months"
hit_at(s, sp.out(181.08), zoom=1.1, amount=0.4, db=-6)
# 5. he did it
sp.add(191.85, 193.95, o.t + 0.1)
v(191.9, until(sp.out(192.65)), cx=0.5)                # training collage
s = v(192.65, until(sp.out(193.95) + 0.15), cx=0.5, cy=0.4, zoom=(1.15, 1.22))   # SEAL portrait
hit_at(s, sp.out(193.24), zoom=1.15, amount=0.55, db=-1)
# 6. three Hell Weeks
sp.add(195.05, 200.5, o.t + 0.1)
v(194.5, 2.6, cx=0.5, cy=0.35)                         # Hell Week photo
s = v(201.9, until(sp.out(200.5) + 0.1), cx=0.5)       # log carry
hit_at(s, sp.out(199.12), zoom=1.12, amount=0.5, db=-3)
# 7. no more quitting
sp.add(229.1, 231.85, o.t + 0.1)
v(229.0, until(sp.out(230.45)), cx=0.5)                # obstacle course
s = v(230.5, until(sp.out(231.85) + 0.55), cx=0.5)     # cargo net
hit_at(s, sp.out(231.36), zoom=1.12, amount=0.45, db=-4, sound="punch")
# 8. the mind (voice starts 0.55 s over the net so the interview picture starts clean at 269.6, in sync)
sp.add(269.05, 272.95, o.t - 0.55)
s = sync(sp.out(272.6), **TALK)            # CNBC cuts away at about 272.65
v(272.55, until(sp.out(272.95) + 0.1), still=True, cx=0.4, cy=0.42, zoom=(1.32, 1.33))   # hold his face through "have" (same framing as the punch)
hit_at(s, sp.out(272.08), zoom=1.12, amount=0.5, db=-3)   # "weapon"
o.caps = word_captions(sp.words, y=0.5, style="wordcap", palette=["*", "~"],
                       force={"297", "seal", "nobody", "haunted", "office", "chart", "191", "106", "months", "lost",
                              "hell", "quitting", "mind", "weapon"})
o.save()
