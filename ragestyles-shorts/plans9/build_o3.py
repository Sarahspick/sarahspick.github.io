"""Builds plans9/o3_olympia_2026_top10.json: the 2026 Mr. Olympia top 10, 10th to 1st, one signature pose each.

Source: "2026 Mr. Olympia Finals Official Footage", OlympiaTV (https://youtu.be/Cq7TbOxcwPc).
work/youtube/olyrt_vox.mp4 = source 1860 s to 3580 s (the individual posing routines), music removed by Demucs.
work/youtube/oly_vox.mp4   = source 3840 s to 4330 s (awards), music removed.
Placings: fitnessvolt.com/2026-mr-olympia-results (matches the stage: 5th Tonio, 4th Andrew Jacked, 3rd Derek,
2nd Samson, 1st Nick). Names and countries from the on-screen routine labels. Every pose time checked at 0.5 s steps.
Owner feedback applied: title on top, one caption in the exact centre, stronger zoom punch and flash than o1.
Run from ragestyles-shorts/: python3 plans9/build_o3.py
"""
import json

RT, RO = "youtube/olyrt_vox", 1858.1897
AW, AO = "youtube/oly_vox", 3840.0
G = {"sat": 1.06, "contrast": 1.07, "sharpen": 0.5}
LEAD = 1.2   # seconds of build-up before the pose hits
DUR = 2.6

# (place, name, flag, source second when the pose locks in, pose)
TOP10 = [
    ("10TH", "JAMES HOLLINGSHEAD", "gb", 2577.0, "front double biceps"),
    ("9TH", "BRANDON CURRY", "us", 2838.0, "front double biceps"),
    ("8TH", "BEHROOZ TABANI", "ir", 3130.0, "front double biceps"),
    ("7TH", "REGAN GRIMES", "ca", 2388.5, "front double biceps"),
    ("6TH", "MICHAL KRIZANEK", "sk", 2304.5, "back double biceps"),
    ("5TH", "TONIO BURTON", "us", 2179.7, "front double biceps"),
    ("4TH", "ANDREW JACKED", "ae", 1952.5, "front double biceps"),
    ("3RD", "DEREK LUNSFORD", "us", 3513.7, "back double biceps"),
    ("2ND", "SAMSON DAUDA", "gb", 3056.7, "front double biceps"),
    ("1ST", "NICK WALKER", "us", 3297.0, "front double biceps"),
]

shots, captions, sfx = [], [], []
t = 0.0
for i, (place, name, flag, hit, _pose) in enumerate(TOP10):
    last = i == len(TOP10) - 1
    dur = 3.0 if last else DUR
    s = {"src": RT, "in": round(hit - LEAD - RO, 2), "dur": dur, "cx": 0.5, "cy": 0.5, "zoom": [1.0, 1.03],
         "audio": True, "af": "voice", "audio_db": -8, "grade": G,
         "punch": [{"at": LEAD, "zoom": 1.15 if last else 1.13, "ramp": 0.13}],
         "flash": [{"at": LEAD, "amount": 0.55 if last else 0.48, "dur": 0.5}]}
    shots.append(s)
    captions.append({"t": round(t, 2), "d": LEAD, "text": f"*{place}*", "style": "big", "y": 0.5})
    captions.append({"t": round(t + LEAD, 2), "d": round(dur - LEAD, 2),
                     "text": f"{'~' + place + '~' if last else place} :flag-{flag}:\n*{name}*", "style": "big", "y": 0.5})
    sfx.append({"t": round(t + LEAD, 2), "name": "mk:2908_movie_trailer_epic_impact" if last else "mk:788_big_cinematic_impact",
                "in": 0.7 if last else 2.12, "db": -2 if last else -3})
    t += dur

# ending: the moment Nick is announced (arms up, confetti), tracked
end = {"src": AW, "in": round(4135.3 - AO, 2), "dur": 3.4, "audio": True, "af": "voice", "audio_db": 0, "grade": G,
       "ease": "linear", "path": [[0.0, 1.0, 0.418, 0.495], [1.0, 1.0, 0.41, 0.47], [2.0, 1.0, 0.441, 0.452],
                                   [3.4, 1.0, 0.45, 0.49]],
       "punch": [{"at": 0.6, "zoom": 1.1, "ramp": 0.13}], "flash": [{"at": 0.6, "amount": 0.5, "dur": 0.55}]}
shots.append(end)
captions.append({"t": round(t + 0.6, 2), "d": 2.8, "text": "THE NEW\n*MR. OLYMPIA* :trophy:", "style": "big", "y": 0.5})
t += end["dur"]
captions.insert(0, {"t": 0, "d": round(t, 2), "text": "2026 *Mr. Olympia*\nTop 10 :trophy:", "style": "title",
                    "anim": "none", "y": 0.085})

plan = {"id": "o3_olympia_2026_top10", "yt_title": "The 2026 Mr. Olympia top 10 in 30 seconds 🏆 #shorts",
        "layout": {"mode": "full"}, "shots": shots, "captions": captions, "marks": [], "sfx": sfx,
        "audio_clips": [], "lufs": -14.0}
json.dump(plan, open("plans9/o3_olympia_2026_top10.json", "w"), indent=1, ensure_ascii=False)
print("total", round(t, 2))
