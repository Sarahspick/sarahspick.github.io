"""Face finder for framing (2026-10-05): YuNet (work/models/yunet.onnx, from huggingface opencv/face_detection_yunet)
on single frames read with ffmpeg. face(src, t) gives the largest face as (x, y, h) fractions of the frame (centre and
height), or None. Results are cached in work/faces.json so plan builds stay fast and repeatable."""
import json
import os
import subprocess

import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "work", "faces.json")
_cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
_det = None


def _frame(path, t):
    w, h = map(int, subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                    "stream=width,height", "-of", "csv=p=0", path],
                                   capture_output=True, text=True).stdout.strip().split(",")[:2])
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", str(t), "-i", path, "-frames:v", "1", "-f", "rawvideo",
                          "-pix_fmt", "bgr24", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(h, w, 3) if len(raw) == w * h * 3 else None


def face(src, t):
    key = f"{src}@{t:.2f}"
    if key not in _cache:
        global _det
        img = _frame(os.path.join(ROOT, "work", "youtube", src + ".mp4"), t)
        res = None
        if img is not None:
            h, w = img.shape[:2]
            if _det is None:
                _det = cv2.FaceDetectorYN.create(os.path.join(ROOT, "work", "models", "yunet.onnx"), "", (w, h), 0.7)
            _det.setInputSize((w, h))
            _, faces = _det.detect(img)
            if faces is not None and len(faces):
                x, y, fw, fh = max(faces, key=lambda f: f[2] * f[3])[:4]
                res = [round(float(x + fw / 2) / w, 3), round(float(y + fh / 2) / h, 3), round(float(fh) / h, 3)]
        _cache[key] = res
        json.dump(_cache, open(CACHE, "w"))
    return _cache[key]


def framing(src, t_in, dur, zoom=1.15, aspect=16 / 9):
    """Shot keys that centre the speaker's face (found at a third and two thirds of the shot) with the face about a
    third of the way down the 3:4 box; None when no face is found."""
    pts = [p for p in (face(src, t_in + dur * f) for f in (0.33, 0.66)) if p]
    if not pts:
        return None
    x = sum(p[0] for p in pts) / len(pts)
    y = sum(p[1] for p in pts) / len(pts)
    w, h = 0.75 / aspect / zoom, 1.0 / zoom          # crop size of the 3:4 box in the source at this zoom
    cl = lambda v, half: round(min(max(v, half), 1 - half), 3)
    return {"cx": cl(x, w / 2), "cy": cl(y - 0.33 * h + h / 2, h / 2), "zoom": (zoom, zoom + 0.04)}


def cuts(src, a, b, thresh=0.3):
    """Source seconds of camera cuts between a and b (ffmpeg scene score), cached like the faces."""
    key = f"cuts:{src}@{a:.2f}-{b:.2f}"
    if key not in _cache:
        out = subprocess.run(["ffmpeg", "-hide_banner", "-ss", str(a), "-t", str(b - a), "-i",
                              os.path.join(ROOT, "work", "youtube", src + ".mp4"), "-vf",
                              f"select='gt(scene,{thresh})',showinfo", "-an", "-f", "null", "-"],
                             capture_output=True, text=True).stderr
        ts = [round(a + float(x.split("pts_time:")[1].split()[0]), 2) for x in out.splitlines() if "pts_time:" in x]
        _cache[key] = [t for t in ts if a + 0.15 < t < b - 0.15]
        json.dump(_cache, open(CACHE, "w"))
    return _cache[key]
