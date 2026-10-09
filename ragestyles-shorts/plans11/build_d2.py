"""d2: Dorian Yates, 6x Mr. Olympia, training chest in 1996 (Blood & Guts era): incline machine with 4 plates a side
(80 kg per arm), the spotter forcing the last reps, his face doing the talking. Ends on him on stage.
Source: bilibili BV1MtLm6WEWy "白人背王多里安耶茨备赛后期极限体脂的胸肌训练" (健美大咖秀, 1440x1080, Chinese voice over and
Chinese subtitles at the bottom, y > 0.89): the voice over is not used and every crop keeps the bottom out (cy 0.44, zoom
>= 1.12). Sound: ElevenLabs gym room tone, plate clanks, a grunt, a tension drone (assets/sfx_el).
Run: python3 plans11/build_d2.py && python3 pipeline/bench.py plans11/d2_dorian_chest.json
"""
import sys

sys.path.insert(0, "plans11")
from newscommon import Short  # noqa: E402

V = "bl_BV1MtLm6WEWy"
o = Short("d2_dorian_chest", "Dorian Yates\ntrained like *this* :face-with-steam-from-nose:",
          "Dorian Yates trained like this 😤 #shorts", folder="plans11")
INFO = dict(style="big", y=0.86)


def sh(t_in, dur, cx=0.5, cy=0.44, zoom=(1.12, 1.18), **k):
    return o.shot(V, t_in, dur, cx=cx, cy=cy, zoom=zoom, audio=False, **k)


o.clips.append({"src": "../assets/sfx_el/gym_room.wav", "in": 0.0, "dur": 20.0, "t": 0.0, "af": "film", "db": -16,
                "fade": 0.3})
o.clips.append({"src": "../assets/sfx_el/drone.wav", "in": 0.0, "dur": 20.0, "t": 0.0, "af": "film", "db": -14,
                "fade": 0.3})
# 1. hook: the face, mid rep
s = sh(78.0, 1.4, zoom=(1.12, 1.2))
o.hit(s, 0.05, zoom=1.05, amount=0.5, db=-3)
o.sound(0.1, "grunt", db=-2)
o.cap(0.0, 2.6, "DORIAN YATES\n*1996* :fire:", **INFO)
sh(8.0, 1.3)                                                     # walking into the gym
s = sh(50.0, 1.6, cx=0.5)                                        # 4 plates a side on the incline machine
o.cap(s["_t0"], 1.6, "*80 KG* PER ARM", **INFO)
o.sound(s["_t0"] + 0.2, "plates", db=-4)
sh(56.0, 1.3)                                                    # pressing
sh(72.0, 1.3)
s = sh(86.0, 1.4, zoom=(1.12, 1.2))                              # eyes shut, last rep
o.hit(s, 0.3, zoom=1.05, amount=0.4, db=-5, sound="punch")
s = sh(136.0, 1.4)                                               # cables
o.sound(s["_t0"] + 0.2, "grunt", db=-5)
sh(140.0, 1.2, zoom=(1.12, 1.2))
# end: on stage
s = sh(3.4, 2.2, cy=0.42, zoom=(1.12, 1.16))
o.hit(s, 0.1, zoom=1.08, amount=0.55, db=-1)
o.cap(s["_t0"] + 0.1, 2.3, "6X MR. OLYMPIA :trophy:", **INFO)
o.save(open_fade=0.0)
