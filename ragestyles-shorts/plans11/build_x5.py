"""x5: Sam Sulek on training before sunrise (Bulk Rebirth Day 28, 2026-09-29): "if you're leaving the gym as the sun is
rising, that is a situation that has a little bit of extra hype... you just got it and everybody else is still barely
stirring awake, smacking the snooze button... give me five more minutes".
Source: Sam Sulek "The Bulk Rebirth Day 28 - Curls and Extensions 238.0 lbs" (https://youtu.be/8NRaqf9m5bA); the talk
is from the 6:42 am drive (music under it: Demucs vocals work/youtube/sm28.wav, 0 to 65 s). That footage is too dark
to show his face, so the picture is the lit part of the same drive (376 to 384 s) and the gym (860 to 1650 s).
The video is 1920x818, so a 3:4 crop is 0.32 of the width at zoom 1 (cx from 0.16 to 0.84).
Run: python3 plans11/build_x5.py && python3 pipeline/bench.py plans11/x5_sam_sulek_sunrise.json
"""
import sys

sys.path.insert(0, "plans11")
from newscommon import Short, Speech, Cutter, words, word_captions  # noqa: E402

V = "8NRaqf9m5bA"
o = Short("x5_sam_sulek_sunrise", "Gym before sunrise\n*hits different* :alarm-clock:",
          "Gym before sunrise hits different ⏰ #shorts", folder="plans11")
c = Cutter(o)
sp = Speech(o, [("sm28.wav", 0.0, 65.0)], words("sm28"))


def say(a, b, gap=0.05):
    return sp.add(a, b, o.t + gap)


def shots(t_end, *parts):
    """Lay shots (t_in, share, keys) to fill the output up to t_end; share is the fraction of the time."""
    total = round(t_end - o.t, 2)
    for i, (t_in, share, k) in enumerate(parts):
        d = round(total * share, 2) if i < len(parts) - 1 else round(t_end - o.t, 2)
        s = c.v(V, t_in, d, **k)
    return s


CAR = dict(cx=0.24, cy=0.45, zoom=(1.0, 1.04))
# 1. hook: "you're leaving the gym as the sun is rising"
t = say(32.68, 36.32, gap=0.0)                                    # from "you're" (a lone "if" made its own caption)
s = shots(sp.out(36.32) + 0.05, (376.0, 0.55, CAR), (382.0, 0.45, dict(CAR, cx=0.25)))
o.hit(o.shots[0], 0.0, zoom=1.06, amount=0.45, db=-4)
# 2. "that is a situation that has a little bit of extra hype"
say(37.4, 40.94)
s = shots(sp.out(40.94) + 0.05, (860.0, 1.0, dict(cx=0.3, cy=0.45, zoom=(1.0, 1.05))))
c.hit_at(s, sp.out(40.5), zoom=1.08, amount=0.5, db=-3)          # "hype"
# 3. "you just got it and everybody else is still barely stirring awake"
say(47.32, 53.26)
shots(sp.out(53.26) + 0.05, (1000.0, 0.45, dict(cx=0.62, cy=0.45, zoom=(1.0, 1.05))),
      (1641.0, 0.55, dict(cx=0.42, cy=0.45, zoom=(1.0, 1.04))))
# 4. "smacking the snooze button ... give me five more minutes"
say(53.26, 55.84)
sp.add(56.52, 57.54, sp.out(55.84) + 0.05)                        # right after the first piece, no shot between
s = shots(sp.out(57.54) + 0.6, (1645.0, 1.0, dict(cx=0.42, cy=0.45, zoom=(1.05, 1.1))))
c.hit_at(s, sp.out(54.72), zoom=1.08, amount=0.5, db=-3)         # "snooze"
o.cap(sp.out(56.52), 1.6, ":sleeping-face: *5 MORE MINUTES*", style="big", y=0.86)
o.caps += word_captions(sp.words, y=0.7, style="wordcap", palette=["*", "~"],
                        force={"gym", "sun", "rising", "hype", "got", "awake", "snooze"})
o.save(open_fade=0.0)
