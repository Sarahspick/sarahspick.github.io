"""OCR footage once and remember where burned-in text (captions, title cards, name tags) appears, so the
documentary shot picker can avoid it.   python tools/textscan.py work/doc_walmart yt_ID [yt_ID ...]

Writes <work>/text.json: {source key: [[t, max text height as a fraction of frame height, "text"], ...]}
(only frames that have text). Small watermarks (< 2.5% of the height) are ignored here; blur them instead."""
import json
import os
import subprocess
import sys

import cv2
import numpy as np
from rapidocr_onnxruntime import RapidOCR

STEP = 1.0


def scan(path, ocr):
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                                         "csv=p=0", path]).decode())
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps=1/{STEP},scale=768:432",
                          "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
    out, i = [], 0
    while True:
        buf = p.stdout.read(768 * 432 * 3)
        if len(buf) < 768 * 432 * 3:
            break
        img = np.frombuffer(buf, np.uint8).reshape(432, 768, 3)
        res, _ = ocr(img)
        hits = [(max(b[2][1], b[3][1]) - min(b[0][1], b[1][1])) / 432 for b, txt, conf in (res or [])
                if conf > 0.6 and len(txt.strip()) >= 3]
        if hits and max(hits) >= 0.025:
            out.append([round(i * STEP, 2), round(max(hits), 3), " | ".join(t for _, t, c in res if c > 0.6)[:60]])
        i += 1
    p.wait()
    return out


if __name__ == "__main__":
    work = sys.argv[1]
    path = os.path.join(work, "text.json")
    data = json.load(open(path)) if os.path.exists(path) else {}
    ocr = RapidOCR()
    for key in sys.argv[2:]:
        if key in data:
            continue
        data[key] = scan(os.path.join("work", "sources", key + ".mp4"), ocr)
        print(key, len(data[key]), flush=True)
        json.dump(data, open(path, "w"))
