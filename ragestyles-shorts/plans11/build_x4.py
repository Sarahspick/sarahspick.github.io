"""x4: Larry Wheels tears his right bicep in his first boxing match (vs Vitaly, Aiden Ross event, 2026-08-23): he hit
Vitaly once while he was down, "that was actually the punch that tore my bicep", the bout is a no contest. A week
later, in a sling: "Guys, I tore my bicep... Hey, it ain't all bad. At least they match now." (his left tore on a
nearly 400 lb Atlas stone).
Sources: Larry Wheels "I TORE My Bicep In My First Boxing Match!" (https://youtu.be/OrBoJkrn14Q, 2026-08-23): fight
240 to 253 s (picture only: the audio is a watch party), post fight interview 729 to 759 s (clean voice); Larry Wheels
"It happened...AGAIN" (https://youtu.be/YVK2dN51a5o, 2026-08-31), 0 to 20 s with music under it: Demucs vocals
work/youtube/lw0.wav. The fight feed's score bug (bottom left) is cropped out (zoom 1.3, cy 0.4).
Run: python3 plans11/build_x4.py && python3 pipeline/bench.py plans11/x4_larry_wheels_bicep.json
"""
import sys

sys.path.insert(0, "plans11")
from newscommon import Short, Speech, Cutter, words, word_captions  # noqa: E402
from countdown import zoom_in  # noqa: E402

F, A = "OrBoJkrn14Q", "YVK2dN51a5o"
o = Short("x4_larry_wheels_bicep", "Larry Wheels tore his\n*bicep* boxing :skull:",
          "Larry Wheels tore his bicep boxing 💀 #shorts", folder="plans11")
c = Cutter(o)
home = Speech(o, [("lw0.wav", 0.0, 20.0)], words(A))
ring = Speech(o, [(F + ".mp4", 0.0, 938.0)],
              [(s, e, "him" if (w == "me" and 757.7 < s < 757.9) else w) for s, e, w in words(F)])
FIGHT = dict(cy=0.4, zoom=(1.3, 1.35))


def say(sp, a, b, src, t_in, gap=0.05, hit=None, tail=0.05, **k):
    t = sp.add(a, b, o.t + gap)
    s = c.v(src, t_in, round(t + b - a + tail - o.t, 2), **k)
    if hit is not None:
        o.hit(s, round(t + hit - a - s["_t0"], 2), zoom=1.08, amount=0.5, db=-3)
    return t


# 1. hook: in a sling, "Guys, I tore my bicep."
say(home, 0.0, 1.36, A, 0.0, gap=0.0, hit=0.48, **zoom_in(0.47, 0.28, 1.41, zoom=1.5))
# 2. "This one tore from throwing a hook punch at Vitaly's face." over the fight
t = say(home, 14.88, 19.64, F, 238.0, cx=0.3, **FIGHT)
o.shots[-1]["path"] = [[0, 1.3, 0.3, 0.4], [2.0, 1.3, 0.55, 0.4], [4.8, 1.35, 0.5, 0.4]]
o.sound(t, "crowd_tense", db=-22)
c.hit_at(o.shots[-1], home.out(18.16), zoom=1.08, amount=0.5, db=-3)       # "punch"
# 3. interview: "I hit him once when he was down. Big mistake."
say(ring, 729.9, 731.08, F, 245.0, cx=0.45, **FIGHT)                         # Vitaly goes down
say(ring, 731.64, 732.3, F, 252.0, cx=0.42, cy=0.42, zoom=(1.2, 1.25))       # Larry looks up, the point is taken
# "and that was actually the punch that tore my bicep."
say(ring, 739.94, 741.68, F, 740.0, hit=740.88, **zoom_in(0.56, 0.25, 1.79, 0.56, zoom=1.4))
# "It's totally detached. Serves me right, hitting him when he's down."
say(ring, 755.26, 758.58, F, 755.3, hit=756.54, **zoom_in(0.45, 0.27, 3.37, 0.4, zoom=1.35))
# 4. ending, in the sling: "Hey, it ain't all bad. At least they match now."
say(home, 3.64, 5.6, A, 3.62, hit=5.12, **zoom_in(0.46, 0.22, 2.01, 0.5, zoom=1.15))   # the source cuts at 5.75
o.shots[-1]["dur"] = round(o.shots[-1]["dur"] + 0.06, 2); o.t = round(o.t + 0.06, 2)
c.v(A, 5.66, 0.45, still=True, **zoom_in(0.5, 0.22, 0.45, zoom=1.2))                      # hold his last frame
o.caps += word_captions(sorted(home.words + ring.words), y=0.72, style="wordcap", palette=["*", "~"],
                        force={"tore", "bicep", "hook", "punch", "down", "mistake", "detached", "match"})
o.save(open_fade=0.0)
