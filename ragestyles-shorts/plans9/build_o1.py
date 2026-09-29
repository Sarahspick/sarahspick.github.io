"""Builds plans9/o1_olympia_2026_results.json (2026 Mr. Olympia results countdown with a leaderboard panel).

Source: "2026 Mr. Olympia Finals Official Footage", OlympiaTV (https://youtu.be/Cq7TbOxcwPc).
work/youtube/oly_vox.mp4 = source 3840 s to 4330 s with the arena music removed by Demucs (vocals stem),
so every time below is written in source seconds and shifted by O. All facts checked against frames and
the announcer: 5th Tonio Burton ($30,000), 4th Andrew Jacked, 3rd Derek Lunsford ($100,000, bronze),
last two Samson Dauda and Nick Walker, winner Nick Walker ($600,000, gold medal, Sandow).
Run from ragestyles-shorts/: python3 plans9/build_o1.py
"""
import json

O = 3840.0
V = "youtube/oly_vox"
G = {"sat": 1.05, "contrast": 1.06, "sharpen": 0.45}
TWO = {"layout": "blur", "box_aspect": 1.0, "darken": 0.45}


def shot(src, dur, cx=0.5, cy=0.5, db=-6, **k):
    d = {"src": V, "in": round(src - O, 2), "dur": dur, "cx": cx, "cy": cy, "zoom": [1.0, 1.04], "audio": True,
         "af": "voice", "audio_db": db, "grade": G}
    d.update(k)
    return d


shots = [
    shot(3902.0, 3.8, cx=0.46),                                      # 5th Tonio gets the medal, raises an arm
    shot(3969.2, 4.0, cx=0.5),                                       # 4th Andrew Jacked, V flex
    shot(4026.7, 3.8, cx=0.52, cy=0.45),                             # 3rd Derek, both arms up with the bronze
    shot(4124.5, 3.0, db=-16, **TWO),                                # the last two in the centre
    shot(4128.0, 2.6, cx=0.37, db=-16, zoom=[1.0, 1.06]),            # Nick
    shot(4131.0, 2.6, cx=0.62, db=-16, zoom=[1.0, 1.06]),            # Samson
    shot(4135.3, 4.4, db=0, ease="linear",                           # reveal: Nick throws his arms up (tracked)
         path=[[0.0, 1.0, 0.418, 0.495], [1.0, 1.0, 0.41, 0.47], [2.0, 1.0, 0.441, 0.452], [3.0, 1.0, 0.45, 0.486],
               [4.4, 1.0, 0.442, 0.506]]),
    shot(4139.7, 3.0, db=0, ease="linear",                           # hug with Samson, confetti
         path=[[0.0, 1.0, 0.444, 0.503], [1.5, 1.0, 0.42, 0.515], [3.0, 1.0, 0.443, 0.51]]),
    shot(4199.6, 3.6, cx=0.52, db=-8, zoom=[1.0, 1.06]),             # Nick wearing the gold medal
]
ts = [0.0]
for s in shots:
    ts.append(round(ts[-1] + s["dur"], 2))
T = ts[-1]
BY = 0.205


def cap(i, text, dt=0.0, d=None, y=BY):
    return {"t": round(ts[i] + dt, 2), "d": round(d if d else shots[i]["dur"] - dt, 2), "text": text, "style": "big", "y": y}


captions = [
    {"t": 0, "d": T, "text": "Who won the 2026\n*Mr. Olympia*? :trophy:", "style": "title", "anim": "none", "y": 0.085},
    cap(0, "*5TH* PLACE"),
    cap(1, "*4TH* PLACE"),
    cap(2, "*3RD* PLACE\n~LAST YEAR'S CHAMPION~", y=BY + 0.02),
    cap(3, "LAST ~2~ STANDING"),
    cap(4, "NICK WALKER"),
    cap(5, "OR SAMSON DAUDA?"),
    cap(6, "*NICK WALKER* WINS :trophy:", dt=0.6),
    cap(7, "THE NEW\n*MR. OLYMPIA*", y=BY + 0.02),
    cap(8, "HE BEAT ~3~ FORMER\nMR. OLYMPIAS :exploding-head:", y=BY + 0.02),
]


def clip(src, dur, t):
    return {"src": V, "in": round(src - O, 2), "dur": dur, "t": round(t, 2), "af": "voice", "db": 3, "fade": 0.05}


# the announcer pauses 3 to 6 s before each name: "...fifth place finisher" + the name, packed together
NAME = {0: 2.25, 1: 2.25, 2: 2.25}
audio_clips = [
    clip(3854.5, 2.05, ts[0] + 0.1), clip(3859.1, 1.55, ts[0] + NAME[0]),   # "fifth place finisher" + "Tonio Burton"
    clip(3917.5, 2.05, ts[1] + 0.1), clip(3923.6, 1.35, ts[1] + NAME[1]),   # "fourth place finisher" + "Andrew Jacked"
    clip(4001.5, 2.1, ts[2] + 0.1), clip(4008.6, 1.5, ts[2] + NAME[2]),     # "third place finisher" + "Derek Lunsford"
    clip(4073.9, 3.0, ts[3]),                                               # "if I can have Samson and Nick in the center"
    clip(4116.4, 2.8, ts[4]),                                               # "the first place check for $600,000"
    clip(4121.9, 2.7, ts[5]),                                               # "and the title of 2026 Mr. Olympia"
    clip(4156.4, 2.9, ts[8] + 0.2),                                         # "he defeated three former Mr. Olympia"
]
panel = {"type": "panel", "t": 0, "d": T, "x": 0.035, "y": 0.555, "w": 720, "size": 50, "header": "2026 MR. OLYMPIA",
         "rows": [
             {"t": round(ts[0] + NAME[0], 2), "text": "5TH  TONIO BURTON  *$30K*"},
             {"t": round(ts[1] + NAME[1], 2), "text": "4TH  ANDREW JACKED"},
             {"t": round(ts[2] + NAME[2], 2), "text": "3RD  DEREK LUNSFORD  *$100K*"},
             {"t": round(ts[6] + 0.6, 2), "text": "2ND  SAMSON DAUDA"},
             {"t": round(ts[6] + 0.6, 2), "text": "~1ST~  NICK WALKER  *$600K*"},
         ]}
plan = {"id": "o1_olympia_2026_results", "yt_title": "Who won the 2026 Mr. Olympia? 🏆 #shorts",
        "layout": {"mode": "full"}, "shots": shots, "captions": captions, "marks": [panel], "sfx": [],
        "audio_clips": audio_clips, "lufs": -14.0}
json.dump(plan, open("plans9/o1_olympia_2026_results.json", "w"), indent=1, ensure_ascii=False)
print("shots at", ts)
