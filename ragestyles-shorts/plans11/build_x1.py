"""x1: Samson Dauda, 2nd at the 2026 Mr. Olympia (4th the year before). Last year he was told he was big enough and
dieted down to about 280 lb, "a look that did not suit my frame at all"; this year he "did our own thing", came in at
310 lb and beat the reigning Mr. Olympia. Tony Doherty: "that's the biggest man I've ever seen", "you ain't seen
nothing yet".
Source: NPCNewsOnline "2026 IFBB Olympia Weekend Tony Doherty Interviews Mr Olympia 2nd Place" (https://youtu.be/jqUAJHdCVyM,
2026-09-27), no music: voices straight from the video. Samson stands left (face x 0.37 to 0.44, y about 0.2 of the
frame), Tony right; the close ups use countdown.zoom_in with his face measured per shot, so he is centred.
Run: python3 plans11/build_x1.py && python3 pipeline/bench.py plans11/x1_samson_dauda_big_enough.json
"""
import sys

sys.path.insert(0, "plans11")
from newscommon import Short, Speech, Cutter, words, word_captions  # noqa: E402
from countdown import zoom_in  # noqa: E402

V = "jqUAJHdCVyM"
o = Short("x1_samson_dauda_big_enough", "They said he was\n*big enough* :face-with-steam-from-nose:",
          "They said he was big enough 😤 #shorts", folder="plans11")
c = Cutter(o)
sp = Speech(o, [(V + ".mp4", 0.0, 311.0)], words(V))
WIDE = dict(cx=0.36, cy=0.5, zoom=(1.0, 1.04))       # Samson head to thighs, silver medal


def info(t, d, text, y=0.86):
    o.cap(t, d, text, style="big", y=y)


def say(a, b, t_in, gap=0.05, hit=None, close=None, fx=(0.38, 0.38), fy=0.2, **k):
    """One piece of speech over one shot of the same interview; close = zoom for a push in on Samson, whose face
    is at fx (start, end of the shot) and fy in the source frame (measured on a grid per shot)."""
    t = sp.add(a, b, o.t + gap)
    d = round(t + b - a + 0.05 - o.t, 2)
    if close:
        k = zoom_in(fx[0], fy, d, fx[1], zoom=close)
    s = c.v(V, t_in, d, **(k or WIDE))
    if hit is not None:
        o.hit(s, round(t + hit - a - s["_t0"], 2), zoom=1.08, amount=0.5, db=-3)
    return t


# 1. hook: Tony, "that's the biggest man I've ever seen"
say(101.42, 102.74, 101.42, gap=0.0, hit=101.74, cx=0.36, cy=0.5, zoom=(1.12, 1.18))
# 2. "fourth last year and came back to a close second this year"
say(17.7, 18.82, 17.7, close=1.5, fx=(0.42, 0.44))
say(19.56, 22.0, 19.6, hit=21.38, **WIDE)
# 3. Samson: "they say you're big enough, you're big enough. So last year we have really sucked down"
say(114.86, 118.24, 114.9, close=1.5, fx=(0.375, 0.36))
# "Came down to 280 ... and it was just a look that did not suit my frame at all"
t = say(122.98, 123.74, 123.0, hit=123.4, close=1.6, fx=(0.37, 0.38), fy=0.22)
info(t + 0.4, 0.5, "*280* LBS")
say(125.64, 128.1, 125.7, close=1.5, fx=(0.375, 0.375))
# 4. "We did our own thing this year. We trusted on ourselves. We didn't let anybody tell us what we needed to do"
say(47.72, 52.52, 47.8, hit=48.26, **WIDE)
# 5. Tony: "Weighing 310 pounds today"
t = say(192.72, 194.14, 192.8, hit=193.0, cx=0.36, cy=0.5, zoom=(1.1, 1.16))
info(t + 0.3, 1.2, "~280~ :right-arrow: *310* LBS :flexed-biceps:")
# 6. Tony: "let me just finish by saying you ain't seen nothing yet"
say(306.16, 308.66, 306.2, close=1.5, fx=(0.375, 0.44))
o.shots[-1]["dur"] = round(o.shots[-1]["dur"] + 0.4, 2); o.t = round(o.t + 0.4, 2)
c.hit_at(o.shots[-1], sp.out(308.0), zoom=1.08, amount=0.5, db=-2)
o.caps += word_captions(sp.words, y=0.7, style="wordcap", palette=["*", "~"],
                        force={"biggest", "fourth", "second", "big", "280", "frame", "own", "trusted", "310", "nothing"})
o.save(open_fade=0.0)
