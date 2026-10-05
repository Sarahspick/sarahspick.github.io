"""y1: David Goggins' knee (Joe Rogan Experience #1906). His meniscus was so hard from years of pounding that it broke
the surgeon's scalpel ("he's not human"); his X-ray shows zero space between the bones; a second surgeon: "I don't
know how you did anything with those knees, let alone run 200 miles back to back, 240 miles".
Source: "David Goggins Thought He'd Never Run Again" (JRE clip, https://youtu.be/WY7XPMThJ4Y, 2022-12-06), from the
archive.org mirror youtube-WY7XPMThJ4Y (1080p webm remuxed to work/youtube/ia_goggins_run.mp4). Podcast audio, no
music. Joe tells the scalpel story with the camera on him; Goggins tells the second surgeon's line on camera, so
every piece is lip synced (picture from the same seconds as the voice).
Run: python3 plans11/build_y1.py && python3 pipeline/bench.py plans11/y1_goggins_scalpel.json
"""
import sys

sys.path.insert(0, "plans11")
from newscommon import Short, Speech, Cutter, words, word_captions  # noqa: E402

V = "ia_goggins_run"
o = Short("y1_goggins_scalpel", "Goggins' knee broke\na *scalpel* :exploding-head:",
          "David Goggins' knee broke a scalpel 🤯 #shorts", folder="plans11")
c = Cutter(o)
sp = Speech(o, [(V + ".mp4", 0.0, 896.0)], words(V))
JOE = dict(cx=0.45, cy=0.42, zoom=(1.12, 1.18))
DG = dict(cx=0.5, cy=0.42, zoom=(1.12, 1.18))


def say(a, b, gap=0.05, hit=None, tail=0.05, **k):
    """Lip synced piece: the picture is the same source seconds as the voice."""
    t = sp.add(a, b, o.t + gap)
    s = c.v(V, a, round(t + b - a + tail - o.t, 2), **k)
    if hit is not None:
        o.hit(s, round(t + hit - a - s["_t0"], 2), zoom=1.08, amount=0.5, db=-3)
    return t


# 1. hook, Joe: "He goes like he's not human. He goes when I was cutting into meniscus, it broke the scalpel"
say(379.2, 384.28, gap=0.0, hit=383.02, **JOE)
# 2. "normally when you cut into meniscus it just slices right through like butter. He's like I couldn't cut it."
say(388.24, 394.54, hit=394.06, **JOE)
# 3. the X-ray: "Look at the fact that there's zero space between those bones"
t = say(110.44, 115.34, cx=0.75, cy=0.68, zoom=(1.6, 1.66))      # the X-ray inset, lower right (x 0.55 to 0.95, y 0.55 to 0.95)
o.cap(t + 2.2, 2.7, "*BONE ON BONE* :skull:", style="big", y=0.86)
# 4. Joe: "you've hardened your meniscus just through constant pressure and pounding"
say(406.92, 410.5, **JOE)
# 5. Goggins, the second surgeon: "I don't know how you did anything with those knees, anything, let alone run
#    200 miles back to back, 240 miles"
say(702.02, 704.56, **DG)
say(705.3, 710.78, hit=710.02, tail=0.5, **DG)
o.caps += word_captions(sp.words, y=0.72, style="wordcap", palette=["*", "~"],
                        force={"human", "scalpel", "butter", "cut", "zero", "bones", "hardened", "pounding",
                               "knees", "200", "240"})
o.save(open_fade=0.0)
