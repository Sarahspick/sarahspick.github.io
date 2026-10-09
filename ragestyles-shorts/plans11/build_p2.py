"""p2: the 2026 Mr. Olympia press conference turns into a posedown: "Bodybuilding fans, who wants to see a show?",
"Ladies and gentlemen, it is time to pose down", the Open athletes strip their jackets on the stage sofas and pose in
sweatpants, "they say shows are won from the back", "Derek, who do you got? I want to know who's taking second."
Nick Walker in the middle (he won two days later). The host's voice is the original audio, words in real time over the
same moment's picture.
Source: bilibili BV17Qhy6NEGb "2026奥赛新闻发布会！无差别巨兽Posedown！" (老派健美, 1920x1080, original English audio, Chinese and
English subtitles burned in at y > 0.88, a bilibili mark top left): crops keep cy 0.42 zoom >= 1.2 and cx >= 0.4.
Words: work/tr/bl_BV17Qhy6NEGb.json (faster-whisper medium.en; "pause down" = "pose down").
Run: python3 plans11/build_p2.py && python3 pipeline/bench.py plans11/p2_press_posedown.json
"""
import sys

sys.path.insert(0, "plans11")
from newscommon import Short, Speech, Cutter, words, word_captions  # noqa: E402

V = "bl_BV17Qhy6NEGb"
o = Short("p2_press_posedown", "Olympia press conference\nturned into a *posedown* :face-exhaling:",
          "The Olympia press conference turned into a posedown 😳 #shorts", folder="plans11")
c = Cutter(o)
wd = [(s, e, "pose" if w.lower().startswith("pause") else w) for s, e, w in words("bl_" + "BV17Qhy6NEGb")]
sp = Speech(o, [(V + ".mp4", 0.0, 108.0)], wd)
CROP = dict(cx=0.5, cy=0.42, zoom=(1.2, 1.25))


def say(a, b, t_in=None, gap=0.05, tail=0.05, **k):
    t = sp.add(a, b, o.t + gap)
    kk = dict(CROP)
    kk.update(k)
    return c.v(V, a if t_in is None else t_in, round(t + b - a + tail - o.t, 2), **kk)


# 1. hook: Nick Walker's front double biceps, "Ladies and gentlemen,"
s = say(15.46, 16.9, gap=0.0, cy=0.4)
o.hit(s, 0.05, zoom=1.05, amount=0.5, db=-3)
o.cap(0.0, 1.45, "\\*Nick Walker\\*", style="wordcap", italic=True, y=0.86, size=58)
s = say(17.76, 21.32)                                              # "it is time to pose down"
o.hit(s, round(sp.out(19.76) - s["_t0"], 2), zoom=1.05, amount=0.45, db=-4)
say(36.34, 39.58)                                                  # "It is officially on"
say(44.4, 48.14)                                                   # "Joe Weider's Olympia is off to a rip-roaring start"
say(68.64, 72.16, cy=0.42)                                         # "they say shows are won from the back"
say(74.84, 75.98, zoom=(1.15, 1.2))                                # "Who do you all got?"
say(80.02, 80.88, t_in=76.3, zoom=(1.15, 1.18))                                  # "Derek, who do you got?" over Nick
s = say(82.72, 83.52, t_in=77.2, gap=0.0, zoom=(1.18, 1.22))                 # "I want to know who's taking second."
o.hit(s, 0.3, zoom=1.06, amount=0.45, db=-3)
s = say(96.86, 98.76, tail=0.5)                                    # "Tomorrow night it all goes down"
o.cap(s["_t0"], s["dur"], "NICK WALKER WON :trophy:", style="big", y=0.86)
o.caps += word_captions(sp.words, y=0.72, style="wordcap", palette=["*", "~"],
                        force={"gentlemen,", "pose", "officially", "start", "back", "second."})
o.save(open_fade=0.0)
