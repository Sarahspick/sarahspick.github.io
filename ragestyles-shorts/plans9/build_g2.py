"""g2: Gymshark sled challenge, which training style wins? (5 women, sled push + pull 15 m, 80 kg then 100 kg on time)
Source: "GYMSHARK STRENGTH TEST | Powerlifter vs Crossfitter vs Olympic Lifter vs Hybrid", Gymshark
(https://youtu.be/XlZZRCaETAs), CC BY. work/youtube/gs_sled_vox.mp4 = source 75 to 275 s, music removed by Demucs.
Who is who (name labels in the intro, face icons on the result board at 4:06 to 4:27):
Lucy Davis, hybrid athlete: 0:56 (crown) / Samantha Cubbins, CrossFit: 1:02 / Lea Schreiner, German powerlifter,
benches 100 kg: 1:04 / Oyinda, functional training: 1:28 / Yazmin Stevens, Olympic weightlifter: 1:46.
Run: python3 plans9/build_g2.py
"""
import json

V, O = "youtube/gs_sled_vox", 75.0
G = {"sat": 1.05, "contrast": 1.06, "sharpen": 0.45}
shots, caps, sfx = [], [], []
t = 0.0


def shot(src, dur, cx=0.5, cy=0.5, db=-6, **k):
    global t
    s = {"src": V, "in": round(src - O, 2), "dur": dur, "cx": cx, "cy": cy, "zoom": [1.0, 1.04], "audio": True,
         "af": "voice", "audio_db": db, "grade": G}
    s.update(k)
    s["_t0"] = t
    shots.append(s)
    t = round(t + dur, 2)
    return s


def cap(s, text, dt=0.0, d=None):
    caps.append({"t": round(s["_t0"] + dt, 2), "d": round(d if d else s["dur"] - dt, 2), "text": text, "style": "big",
                 "y": 0.5})


def hit(s, at, zoom=1.13, amount=0.48, big=False):
    s.setdefault("punch", []).append({"at": at, "zoom": zoom, "ramp": 0.13})
    s.setdefault("flash", []).append({"at": at, "amount": amount, "dur": 0.5})
    sfx.append({"t": round(s["_t0"] + at, 2),
                "name": "mk:2908_movie_trailer_epic_impact" if big else "mk:788_big_cinematic_impact",
                "in": 0.7 if big else 2.12, "db": -2 if big else -3})


s = shot(87.0, 2.6, cx=0.45)          # round 1 push
cap(s, "SLED PUSH + PULL\n*80KG* :person-lifting-weights:")
s = shot(128.5, 2.2, cx=0.5)          # "round 2, 100kg"
hit(s, 0.3)
s = shot(135.0, 2.6, cx=0.45)         # "Lea, how much can you bench press?" "100"
cap(s, "THAT'S LEA'S\n*BENCH PRESS* :skull:")
s = shot(177.0, 2.4, cx=0.5)          # a racer pushing
cap(s, "NOW IT'S A *RACE* :stopwatch:")
s = shot(184.5, 2.4, cx=0.5)
cap(s, "PUSH 15M, *PULL* 15M")
# results: each placing over that athlete's own intro shot (name label in the source), so nobody is mislabelled
IV = "youtube/XlZZRCaETAs"


def intro(src, cx, text, big=False, dur=2.4):
    global t
    x = {"src": IV, "in": src, "dur": dur, "cx": cx, "cy": 0.5, "zoom": [1.0, 1.04], "audio": False, "grade": G}
    x["_t0"] = t
    shots.append(x)
    t = round(t + dur, 2)
    cap(x, text)
    hit(x, 0.2)
    return x


res0 = t
intro(22.6, 0.55, "~5TH~ YAZMIN\nOLYMPIC LIFTER *1:46*")
intro(43.0, 0.59, "~4TH~ OYINDA\nFUNCTIONAL *1:28*")
intro(36.0, 0.53, "~3RD~ LEA :flag-de:\nPOWERLIFTER *1:04*")
intro(53.6, 0.59, "~2ND~ SAMANTHA\nCROSSFIT *1:02*", dur=2.2)
intro(62.3, 0.52, "*1ST* LUCY :trophy:\nHYBRID ATHLETE *0:56*")
clips = [{"src": V, "in": round(248.0 - O, 2), "dur": round(t - res0, 2), "t": res0, "af": "voice", "db": -4, "fade": 0.2}]
s = shot(263.6, 3.2, cx=0.62, db=-2)   # Lucy celebrating, her crowned face icon at 00:56
cap(s, "THE HYBRID\n*BEAT THEM ALL* :fire:")
hit(s, 0.4, zoom=1.15, amount=0.55, big=True)
for x in shots:
    x.pop("_t0")
caps.insert(0, {"t": 0, "d": t, "text": "Powerlifter vs CrossFit\nvs *Hybrid* :thinking-face:",
                "style": "title", "anim": "none", "y": 0.085})
plan = {"id": "g2_gymshark_sled_race", "yt_title": "Powerlifter vs CrossFit vs Hybrid: who wins? 🤔 #shorts",
        "layout": {"mode": "full"}, "shots": shots, "captions": caps, "marks": [], "sfx": sfx, "audio_clips": clips,
        "lufs": -14.0}
json.dump(plan, open("plans9/g2_gymshark_sled_race.json", "w"), indent=1, ensure_ascii=False)
print("total", t)
