"""Shared builder for the plans10 shorts (s1 suits, e1 Eddie Hall, d1 Goggins). Source times are seconds of the
downloaded file in work/youtube/<id>.mp4 (tools/yt_batch.sh). Owner style (2026-09-30): title on top, one caption in
the exact centre, zoom punch + flash + heavy boom on reveals, owner SFX pack (ow:) only, sometimes dim_in, no glow.
"""
import json
import os

G = {"sat": 1.06, "contrast": 1.07, "sharpen": 0.5}
CY = 0.5  # caption y (o1 final: exact centre)
# where the impact sits inside each owner sound (seconds), so cues land on the beat
PEAK = {"boom": 0.25, "punch": 0.43, "whoosh": 0.0, "transition": 0.9, "riser1": 1.98, "riser8": 3.66}


class Short:
    # owner layout (2026-09-30, checked on an iPhone): title from 155 px, the clip from 370 px in a 3:4 box, the same
    # clip blurred behind it
    LAYOUT = {"mode": "blur", "box_aspect": 0.75, "box_w": 1080, "box_top": 370, "darken": 0.5}
    TITLE_TOP = 155

    def __init__(self, sid, title, yt_title, folder="plans10", layout=None, title_y=None):
        self.id, self.title, self.yt_title, self.folder = sid, title, yt_title, folder
        self.layout = layout or dict(self.LAYOUT)
        self.title_y = title_y
        self.shots, self.caps, self.sfx, self.clips, self.marks = [], [], [], [], []
        self.t = 0.0

    def shot(self, src, t_in, dur, cx=0.5, cy=0.5, db=-8, zoom=(1.0, 1.03), audio=True, **k):
        s = {"src": "youtube/" + src, "in": round(t_in, 2), "dur": dur, "cx": cx, "cy": cy, "zoom": list(zoom),
             "audio": audio, "af": "voice", "audio_db": db, "grade": G}
        s.update(k)
        s["_t0"] = self.t
        self.shots.append(s)
        self.t = round(self.t + dur, 2)
        return s

    def cap(self, t, d, text, style="big", **k):
        c = {"t": round(t, 2), "d": round(d, 2), "text": text, "style": style, "y": CY}
        c.update(k)
        self.caps.append(c)
        return c

    def sound(self, t, name, db=-4):
        """Owner sound whose impact lands on output second t."""
        self.sfx.append({"t": round(t - PEAK.get(name, 0.0), 2), "name": "ow:" + name, "db": db})

    def hit(self, s, at, zoom=1.14, amount=0.5, db=-3, sound="boom"):
        """Reveal at `at` seconds into shot s: zoom punch (held to the end of the shot), flash and a heavy boom."""
        s.setdefault("punch", []).append({"at": at, "zoom": zoom, "ramp": 0.12})
        s.setdefault("flash", []).append({"at": at, "amount": amount, "dur": 0.5})
        if sound:
            self.sound(s["_t0"] + at, sound, db)

    def clip(self, src, t_in, dur, t, db=0, af="voice"):
        """Source sound laid at output second t. src is a work/youtube name; a name with an extension (the Demucs
        vocals .wav) is used as is."""
        self.clips.append({"src": "youtube/" + src, "in": round(t_in, 2), "dur": dur, "t": round(t, 2), "af": af,
                           "db": db, "fade": 0.05})

    def vox(self, parts, t_src, dur, t, db=0, af="voice"):
        """Like clip, but t_src is a second of the original video, looked up in Demucs copies [(file, start, end)]."""
        for name, a, b in parts:
            if a <= t_src and t_src + dur <= b + 0.01:
                return self.clip(name, t_src - a, dur, t, db, af)
        raise ValueError(f"no Demucs copy covers {t_src}+{dur}")

    def save(self, lufs=-14.0, title_end=None, open_fade=1.0):
        for s in self.shots:
            s.pop("_t0", None)
        pos = {"y": self.title_y} if self.title_y is not None else {"top": self.TITLE_TOP}
        caps = [dict({"t": 0, "d": title_end or self.t, "text": self.title, "style": "title", "anim": "none"}, **pos)] \
            if self.title else []
        caps += self.caps
        plan = {"id": self.id, "yt_title": self.yt_title, "layout": self.layout, "shots": self.shots,
                "captions": caps, "marks": self.marks, "sfx": self.sfx, "audio_clips": self.clips, "lufs": lufs,
                "open_fade": open_fade}
        os.makedirs(self.folder, exist_ok=True)
        json.dump(plan, open(f"{self.folder}/{self.id}.json", "w"), indent=1, ensure_ascii=False)
        print(self.id, "total", self.t)


class Speech:
    """Pieces of one speaker's voice laid back to back on the output timeline, and their words moved with them.
    words: [(start, end, word)] in source seconds. add() returns the output time where the piece starts."""

    def __init__(self, short, parts, words):
        self.o, self.parts, self.src_words, self.words, self.maps = short, parts, words, [], []

    def add(self, a, b, t, db=2):
        self.o.vox(self.parts, a, round(b - a, 2), t, db=db)
        self.maps.append((a, b, t))
        n = len(self.words)
        for s, e, w in self.src_words:
            if a <= s < b and w.strip():
                self.words.append((round(t + s - a, 2), round(t + min(e, b) - a, 2), w))
        if len(self.words) > n and not self.words[-1][2].rstrip().endswith((".", ",", "!", "?")):
            s_, e_, w_ = self.words[-1]
            self.words[-1] = (s_, e_, w_ + ".")  # a caption never runs across two pieces
        return t

    def out(self, src_t):
        """Output second of a source second inside an added piece."""
        for a, b, t in self.maps:
            if a <= src_t <= b:
                return round(t + src_t - a, 2)
        raise ValueError(src_t)
