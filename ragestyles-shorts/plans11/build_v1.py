"""v1: the deadlift ladder (Giants Live Strongman Open, Birmingham, 2026-09-05, max deadlift). The weight climbs and
the field falls away: 400 kg ("oh my word"), 454 kg ("1000 pounds is in the books"), 470 kg (Trey Mitchell "so
smooth", Evans Nana "bites back hard"), 480 kg (one fails, Hafthor makes it), then Raul Flores pulls 511 kg, one kilo
over Thor's 510 kg record: "there is a new sheriff in town". No interview: lifts, fails, sparks, the commentary.
Source: World Deadlift Championships 2026 broadcast, every attempt (9maLI002HLc), commentary and arena sound as is;
words work/tr/9maLI002HLc.json (faster-whisper medium.en).
Run: python3 plans11/build_v1.py && python3 pipeline/bench.py plans11/v1_deadlift_ladder.json
"""
import sys

sys.path.insert(0, "plans11")
from newscommon import Short, Speech, Cutter, words, word_captions  # noqa: E402

V = "9maLI002HLc"
o = Short("v1_deadlift_ladder", "Who can pull\n*511 kg?* :exploding-head:",
          "Who can pull 511 kg? 🤯 #shorts", folder="plans11")
c = Cutter(o)
sp = Speech(o, [(V + ".mp4", 0.0, 900.0)], words(V))
KG = dict(style="big", y=0.86)


def say(a, b, t_in, gap=0.05, tail=0.05, **k):
    """Commentary a..b laid at the current time with picture from t_in; returns the shot."""
    t = sp.add(a, b, o.t + gap)
    return c.v(V, t_in, round(t + b - a + tail - o.t, 2), **k)


def kg(s, text, at=0.0, d=None, hit=True):
    o.cap(s["_t0"] + at, d or round(s["dur"] - at, 2), text, **KG)
    if hit:
        o.hit(s, at, zoom=1.06, amount=0.4, db=-5)


def wow(s, at):
    """The big hit: punch, flash, red wash, chromatic split, boom."""
    o.hit(s, at, zoom=1.1, amount=0.55, db=-2)
    s.setdefault("tint", []).append({"at": at, "dur": 0.45, "amount": 0.5, "color": [255, 30, 20]})
    s.setdefault("rgb", []).append({"at": at, "dur": 0.35, "px": 14})


# 1. hook: Raul screaming in the sparks, arena roar
o.clip(V + ".mp4", 553.5, 1.25, 0.0, db=-2, af="film")
s = c.v(V, 553.5, 1.25, cx=0.3, cy=0.48, zoom=(1.05, 1.05), ease="linear",
        path=[[0, 1.05, 0.3, 0.48], [0.4, 1.05, 0.31, 0.48], [0.7, 1.05, 0.4, 0.48], [1.0, 1.05, 0.5, 0.48],
              [1.25, 1.05, 0.58, 0.48]])                                 # follow his face
wow(s, 0.05)
o.cap(0.0, 1.25, "*511 KG* :globe-showing-americas:", style="wordcap", y=0.72)
# 2. 400 kg: "400 kilograms the weight on the... oh my word"
s = say(42.04, 43.46, 42.0, cx=0.86, cy=0.62, zoom=(1.7, 1.8))
kg(s, "*400 KG* :check-mark-button:", 0.1, hit=False)
s = say(44.7, 45.8, 44.9, gap=0.0, cx=0.86, cy=0.52, zoom=(1.7, 1.75))
kg(s, "*400 KG* :check-mark-button:", 0.0)
# 3. 454 kg, Jeffers locks it out: "1000 pounds is in the books"
s = say(302.55, 304.47, 290.0, cx=0.24, cy=0.5, zoom=(1.0, 1.06))
kg(s, "*454 KG* :check-mark-button:", 0.1)
# 4. 470 kg, Hafthor up in one smooth pull: "Wow... so smooth"
s = say(351.23, 352.11, 349.4, cx=0.73, cy=0.45, zoom=(1.0, 1.05))
kg(s, "*470 KG* :check-mark-button:", 0.1)
say(353.37, 354.37, 350.6, gap=0.0, cx=0.73, cy=0.43, zoom=(1.08, 1.12))
# 5. 470 kg, Nana: "starts to pull, bites back hard ... that will do"
s = say(368.89, 371.73, 368.9, cx=0.5, cy=0.55, zoom=(1.15, 1.2))
kg(s, "*470 KG* :cross-mark:", 1.3)
say(376.47, 377.75, 375.6, gap=0.0, cx=0.5, cy=0.4, zoom=(1.0, 1.05))
# 6. 480 kg: "Oh, that one bit back hard"
s = say(454.32, 456.24, 454.3, cx=0.5, cy=0.5, zoom=(1.0, 1.04))
kg(s, "*480 KG* :cross-mark:", 0.6)
# 7. Hafthor at 480: "the strongest man of all time"
s = say(473.12, 475.86, 496.6, tail=0.7, cx=0.5, cy=0.42, zoom=(1.1, 1.2))
kg(s, "*480 KG* :check-mark-button:", 2.9)
o.cap(s["_t0"], 2.1, "\\*Thor's record: 510 kg\\*", style="wordcap", italic=True, y=0.86, size=58)
# 8. Raul Flores, 511 kg, live arena sound: setup, the pull, lockout
t = o.t + 0.05
o.clip(V + ".mp4", 527.2, 6.2, t, db=-2, af="film")
o.cap(t, 1.6, "\\*Raul Flores\\*", style="wordcap", italic=True, y=0.86, size=58)
c.v(V, 527.2, 1.8, cx=0.5, cy=0.42, zoom=(1.3, 1.35))                 # gripping the bar
c.v(V, 529.0, 1.6, cx=0.5, cy=0.45, zoom=(1.3, 1.4))                  # the pull
s = c.v(V, 530.6, 2.85, cx=0.5, cy=0.4, path=[[0, 1.35, 0.5, 0.42], [1.4, 1.75, 0.5, 0.33], [2.85, 1.8, 0.5, 0.33]])
wow(s, 1.5)                                                          # locked out
o.cap(s["_t0"] + 1.5, 1.35, "*511 KG* :globe-showing-americas:", **KG)
# sparks
o.clip(V + ".mp4", 538.0, 1.4, o.t, db=-3, af="film")
s = c.v(V, 538.0, 1.4, cx=0.5, cy=0.42, zoom=(1.1, 1.16))
o.hit(s, 0.15, zoom=1.08, amount=0.45, db=-4)
o.cap(s["_t0"], 1.4, "*WORLD RECORD*", **KG)
# 9. "there is a new sheriff in town"
s = say(568.72, 571.76, 566.2, gap=0.0, tail=0.4, cx=0.6, cy=0.45, zoom=(1.0, 1.0),
        path=[[0, 1.0, 0.6, 0.45], [1.5, 1.0, 0.55, 0.45], [3.3, 1.0, 0.38, 0.45], [3.6, 1.0, 0.38, 0.45]])
o.hit(s, round(sp.out(570.04) - s["_t0"], 2), zoom=1.06, amount=0.45, db=-4)
o.caps += word_captions(sp.words, y=0.72, style="wordcap", palette=["*", "~"],
                        force={"400", "1000", "wow", "smooth", "bites", "hard", "strongest", "sheriff"})
o.save(open_fade=0.0)
