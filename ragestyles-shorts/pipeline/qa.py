"""QA for a rendered short: contact sheet of frames + loudness / format report.

Usage: python3 qa.py video.mp4 sheet.jpg [t1 t2 ...]   (defaults to 12 evenly spaced frames)
Also lists silent stretches (below -50 dB for 1.5 s or more): the channel wants original sound all the way through.
"""
import json
import re
import subprocess
import sys

import cv2
import numpy as np


def probe(path):
    d = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", path],
                                  capture_output=True, text=True, check=True).stdout)
    v = [s for s in d["streams"] if s["codec_type"] == "video"][0]
    a = [s for s in d["streams"] if s["codec_type"] == "audio"]
    return {"w": v["width"], "h": v["height"], "fps": v["r_frame_rate"], "dur": float(d["format"]["duration"]),
            "size_mb": int(d["format"]["size"]) / 1e6, "audio": bool(a)}


def loudness(path):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    i = re.findall(r"I:\s+(-?[\d.]+) LUFS", err)
    tp = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", err)
    return (float(i[-1]) if i else None), (float(tp[-1]) if tp else None)


def silences(path, noise_db=-50, min_d=1.5):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af",
                          f"silencedetect=noise={noise_db}dB:d={min_d}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", err)]
    en = [float(x) for x in re.findall(r"silence_end: (-?[\d.]+)", err)]
    return [[round(max(0.0, a), 2), round(b, 2) if i < len(en) else None]
            for i, (a, b) in enumerate(zip(st, en + [None] * (len(st) - len(en))))]


def sheet(path, out, times, cols=6, tw=270):
    th = int(tw * 16 / 9)
    tiles = []
    for t in times:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", path, "-frames:v", "1",
                              "-vf", f"scale={tw}:{th}", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                             capture_output=True).stdout
        if len(raw) < tw * th * 3:
            continue
        im = np.frombuffer(raw[: tw * th * 3], np.uint8).reshape(th, tw, 3).copy()
        cv2.rectangle(im, (0, 0), (64, 22), (0, 0, 0), -1)
        cv2.putText(im, f"{t:.1f}s", (4, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        tiles.append(im)
    while len(tiles) % cols:
        tiles.append(np.zeros((th, tw, 3), np.uint8))
    img = np.vstack([np.hstack(tiles[r:r + cols]) for r in range(0, len(tiles), cols)])
    cv2.imwrite(out, img, [cv2.IMWRITE_JPEG_QUALITY, 85])


if __name__ == "__main__":
    video, out = sys.argv[1], sys.argv[2]
    info = probe(video)
    times = [float(x) for x in sys.argv[3:]] or list(np.linspace(0.3, info["dur"] - 0.3, 12))
    sheet(video, out, times)
    lufs, peak = loudness(video)
    info.update({"lufs": lufs, "true_peak_dbfs": peak})
    if info["audio"]:
        info["silent_gaps"] = silences(video)
    print(json.dumps(info))
    if info.get("silent_gaps"):
        print("WARNING: silent stretches", info["silent_gaps"], file=sys.stderr)
