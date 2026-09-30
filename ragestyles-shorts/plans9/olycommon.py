"""Shared pieces for the 2026 Mr. Olympia shorts (o2 to o5). Times are source seconds of
"2026 Mr. Olympia Finals Official Footage", OlympiaTV (https://youtu.be/Cq7TbOxcwPc).

Demucs (music removed) copies in work/youtube/: olyrt_vox.mp4 = 1858.19 to 3578 s (stream copy from the keyframe; audio delayed to match) (posing routines),
oly_vox.mp4 = 3840 to 4330 s (awards). Owner style (o1 feedback): title on top, one caption in the exact
centre, a quick zoom punch + flash + boom on every reveal, a bit stronger than o1.
"""
import json

SRC = [("youtube/olyrt_vox", 1858.1897, 3578.0), ("youtube/oly_vox", 3840.0, 4330.0), ("youtube/olysp_vox", 4505.0, 4565.0)]
G = {"sat": 1.06, "contrast": 1.07, "sharpen": 0.5}
CY = 0.5  # caption y


def where(t):
    for name, o, e in SRC:
        if o <= t < e:
            return name, o
    raise ValueError(f"no Demucs copy covers source second {t}")


class Short:
    def __init__(self, sid, title, yt_title):
        self.id, self.title, self.yt_title = sid, title, yt_title
        self.shots, self.caps, self.sfx, self.clips = [], [], [], []
        self.t = 0.0

    def shot(self, src, dur, cx=0.5, cy=0.5, db=-8, zoom=(1.0, 1.03), **k):
        name, o = where(src)
        s = {"src": name, "in": round(src - o, 2), "dur": dur, "cx": cx, "cy": cy, "zoom": list(zoom), "audio": True,
             "af": "voice", "audio_db": db, "grade": G}
        s.update(k)
        s["_t0"] = self.t
        self.shots.append(s)
        self.t = round(self.t + dur, 2)
        return s

    def cap(self, t, d, text):
        self.caps.append({"t": round(t, 2), "d": round(d, 2), "text": text, "style": "big", "y": CY})

    def hit(self, s, at, zoom=1.13, amount=0.48, big=False):
        """Reveal at `at` seconds into shot s: zoom punch (held to the end of the shot), flash and a boom."""
        s.setdefault("punch", []).append({"at": at, "zoom": zoom, "ramp": 0.13})
        s.setdefault("flash", []).append({"at": at, "amount": amount, "dur": 0.5})
        self.sfx.append({"t": round(s["_t0"] + at, 2),
                         "name": "mk:2908_movie_trailer_epic_impact" if big else "mk:788_big_cinematic_impact",
                         "in": 0.7 if big else 2.12, "db": -2 if big else -3})

    def clip(self, src, dur, t, db=3):
        name, o = where(src)
        self.clips.append({"src": name, "in": round(src - o, 2), "dur": dur, "t": round(t, 2), "af": "voice", "db": db,
                           "fade": 0.05})

    def save(self):
        for s in self.shots:
            s.pop("_t0", None)
        caps = [{"t": 0, "d": self.t, "text": self.title, "style": "title", "anim": "none", "y": 0.085}] + self.caps
        plan = {"id": self.id, "yt_title": self.yt_title, "layout": {"mode": "full"}, "shots": self.shots,
                "captions": caps, "marks": [], "sfx": self.sfx, "audio_clips": self.clips, "lufs": -14.0}
        json.dump(plan, open(f"plans9/{self.id}.json", "w"), indent=1, ensure_ascii=False)
        print(self.id, "total", self.t)


# Nick's reveal (arms up at 4135.9), tracked with tools/track_person.py
REVEAL = 4135.3
REVEAL_PATH = [[0.0, 1.0, 0.418, 0.495], [1.0, 1.0, 0.41, 0.47], [2.0, 1.0, 0.441, 0.452], [3.0, 1.0, 0.45, 0.486],
               [4.4, 1.0, 0.442, 0.506]]
