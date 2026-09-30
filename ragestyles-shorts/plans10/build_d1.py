"""d1: David Goggins, 297 lbs to Navy SEAL. Format from the owner's reference (DailyMotivationDosis Goggins shorts):
landscape clip on a white card, black explainer text above it with red keywords, red arrows, plus our zoom punch,
flash and heavy boom. Goggins allows edits of his videos (owner, 2026-09-30).
Sources: CNBC Make It, "David Goggins: How I Went From 300 Pounds To Becoming A Navy SEAL" (https://youtu.be/X3yNsomAUvw),
music removed with Demucs into gg_vox.wav (0 to 290 s, same timeline); The Tennessean, "Pull Ups World Record Attempt"
(https://youtu.be/C26OAQfZX7Q), video by Sanford Myers. CNBC shots with CNBC's own text cards are avoided.
Checked on frames and whisper word times (CNBC seconds):
  0.0 "My idea to become a Navy SEAL was me on my couch at 297 pounds" (to 4.66); 4.66 "with a box of mini donuts and a chocolate milkshake" (to 7.98)
  257.6 to 262.8 photo of Goggins overweight (tank top); donuts on screen 5 to 9
  173.4 to 180.5 scale close-up; 176.1 "For me I'm six foot one. I could only weigh 191." (to 179.0)
  179.87 "I'd have lose 106 pounds in less than three months" (to 182.9), interview on screen 180.6 to 183.4
  191.7 "And in less than three months I lost 106 pounds" (to 194.1), SEAL portrait photo 192.6 to 194.3
  194.85 "I'm the only person in Navy SEAL history to be in three hell weeks in one year" (to 200.3); shirtless photo
  194.4 to 197.2 (CNBC card from 197.4), log carry 201.8 to 204.5
  229.4 "I made decisions to myself. There's no more quitting. So that's when I went and got duct tape." (to 233.6)
  269.2 "I started realizing that the mind is the most powerful weapon that we have" (to 272.9), interview 269.6 to 273
Facts: Guinness record 4,030 pull-ups in 17 hours (January 2013); the Tennessean clip is one of his record attempts.
Run: python3 plans10/build_d1.py && python3 pipeline/bench.py plans10/d1_goggins_297_to_seal.json
"""
import sys

sys.path.insert(0, "plans10")
from rscommon import Short  # noqa: E402

C, T = "X3yNsomAUvw", "C26OAQfZX7Q"
VOX = [("gg_vox.wav", 0.0, 290.0)]
BOX_TOP = 1920 * 0.53 - 304     # 16:9 clip, 1080 wide, centred at y 0.53
o = Short("d1_goggins_297_to_seal", "", "From 297 lbs to Navy SEAL 🔥 David Goggins #shorts",
          layout={"mode": "meme", "bg": [255, 255, 255], "box_aspect": 1.7778, "box_w": 1080, "box_y": 0.53})


def v(src, t_in, dur, **k):
    return o.shot(src, t_in, dur, audio=False, cx=k.pop("cx", 0.5), cy=k.pop("cy", 0.5), zoom=k.pop("zoom", (1.0, 1.04)),
                  **k)


def say(t_src, dur, t, db=2):
    o.vox(VOX, t_src, dur, t, db=db)


def text(t, d, s):
    o.cap(t, d, s, style="memebar", y=None)
    o.caps[-1].pop("y")


def arrow(t, d, x, y, angle=135, ln=190):
    """Red arrow whose tip lands on (x, y) of the clip (0..1 inside the 16:9 box)."""
    o.marks.append({"type": "arrow", "t": round(t, 2), "d": round(d, 2), "x": x, "y": round((BOX_TOP + y * 608) / 1920, 4),
                    "angle": angle, "len": ln})


# 1. 297 lbs
s = v(C, 257.7, 4.7, zoom=(1.0, 1.06), dim_in={"hold": 0.3, "dur": 0.2, "from": 0.12})
say(0.0, 4.7, 0)
text(0, 4.7, "This is David Goggins\nat *297 pounds*")
arrow(0.5, 4.2, 0.36, 0.3, angle=20, ln=170)
o.hit(s, 3.3, zoom=1.12, amount=0.45)
# 2. donuts
s = v(C, 5.0, 3.4, zoom=(1.05, 1.12))
say(4.66, 3.4, s["_t0"])
text(s["_t0"], 3.4, "*Donuts* and a *milkshake*\nevery night")
# 3. the limit (scale close-up runs to 180.5)
s = v(C, 176.0, 3.75, zoom=(1.05, 1.1))
say(176.05, 3.05, s["_t0"])
text(s["_t0"], 3.05, "The Navy SEAL limit\nfor his height: *191 lbs*")
o.hit(s, 2.2, zoom=1.1, amount=0.35, db=-6)
# 4. 106 lbs in 3 months (voice starts over the scale, in sync with the interview from 180.55 to 183.05)
s = v(C, 180.55, 2.5, cx=0.5, zoom=(1.0, 1.05))
say(179.85, 3.2, s["_t0"] - 0.7)
text(s["_t0"] - 0.7, 3.2, "He had to lose *106 lbs*\nin *3 months*")
o.hit(s, 0.0, zoom=1.12, amount=0.4, db=-4)
# 5. he did it
t5 = o.t
s = v(C, 190.2, 1.3, zoom=(1.05, 1.1))
s = v(C, 192.75, 1.45, zoom=(1.0, 1.06))
say(191.7, 2.75, t5)
text(t5, 2.75, "...and he *did it* :fire:")
arrow(s["_t0"] + 0.1, 1.35, 0.46, 0.35, angle=160, ln=170)
o.hit(s, 0.2, zoom=1.14, amount=0.5, db=-2)
# 6. three Hell Weeks
t6 = o.t
s = v(C, 194.4, 2.8, zoom=(1.0, 1.06))
s2 = v(C, 201.9, 2.6, zoom=(1.05, 1.1))
say(194.85, 5.5, t6 - 0.05)
text(t6, 5.4, "The only man in SEAL history\nwith *3 Hell Weeks* in 1 year")
o.hit(s2, 0.2, zoom=1.12, amount=0.45, db=-4)
# 7. no more quitting
t7 = o.t
s = v(C, 226.2, 2.6, zoom=(1.0, 1.05))
s2 = v(C, 233.9, 1.6, zoom=(1.05, 1.1))
say(229.4, 4.25, t7)
text(t7, 2.6, "Stress fractures.\nNo more *quitting.*")
text(s2["_t0"], 1.6, "He *duct taped* his legs")
o.hit(s2, 0.0, zoom=1.12, amount=0.4, db=-5, sound="punch")
# 8. the pull-up record (Tennessean footage of an attempt, gym sound)
s = o.shot(T, 32.0, 2.8, cx=0.5, zoom=(1.0, 1.05), db=-10)
text(s["_t0"], 2.8, "Then he went after the\n*pull up world record*")
s = o.shot(T, 54.2, 2.6, cx=0.5, zoom=(1.0, 1.06), db=-10)
text(s["_t0"], 2.6, "*4,030 pull ups*\nin 17 hours :flexed-biceps:")
o.hit(s, 0.2, zoom=1.12, amount=0.45, db=-3)
# 9. the mind
s = v(C, 269.6, 3.4, cx=0.5, zoom=(1.0, 1.08))
say(269.2, 3.75, s["_t0"] - 0.35)
text(s["_t0"], 3.4, "\"The mind is the most\n*powerful weapon* we have\"")
o.hit(s, 2.45, zoom=1.12, amount=0.45, db=-4)
o.save(title_end=0.001)
o_plan = __import__("json").load(open(f"plans10/{o.id}.json"))
o_plan["captions"] = [c for c in o_plan["captions"] if c["style"] != "title"]   # the white card text is the title
__import__("json").dump(o_plan, open(f"plans10/{o.id}.json", "w"), indent=1, ensure_ascii=False)
