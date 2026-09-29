"""Find burned-in subtitle / caption boxes in a source video, so a clip can blur exactly the text and nothing else.

Burned-in text stays put while a handheld camera moves, so a pixel counts as text when it sits on a sharp
bright/dark edge (white letters with a black outline, or dark letters in a white box) in the same place for
several consecutive frames. Nearby text pixels are grouped into boxes; boxes that stay the same over time become
one entry with its own start and end time.

    python tools/textboxes.py bili:BV1Crh26SEoC                 # print boxes for the whole video
    python tools/textboxes.py bili:BV1Crh26SEoC --band 0.3 0.85  # only look in this vertical band
    python tools/textboxes.py bili:BV1Crh26SEoC --json            # {"blur_boxes": [...]} for a clip spec
    python tools/textboxes.py bili:BV1Crh26SEoC --band 0.3 0.85 --centered --json   # subtitles only

Each entry is {"t0": s, "t1": s, "box": [x0, y0, x1, y1]} in source seconds and source fractions: the renderer
blurs the box only while the source time is inside [t0, t1].
"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from factory.media import fetch, probe  # noqa: E402

FPS = 10


def frames(path, w, h, t0=0.0, dur=None):
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{t0:.3f}", "-i", path]
    if dur:
        cmd += ["-t", f"{dur:.3f}"]
    cmd += ["-vf", f"fps={FPS},scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)


def dilate(mask, size):
    return np.asarray(Image.fromarray(mask.astype(np.uint8) * 255).filter(ImageFilter.MaxFilter(size))) > 0


def edge_mask(f):
    lo, hi = f.min(2), f.max(2)
    bright = lo > 205                 # white, unsaturated
    dark = hi < 60
    return (bright & dilate(dark, 5)) | (dark & dilate(bright, 5))


def boxes_in(mask, band, min_px=25, gap=18):
    """Group persistent text pixels into boxes: rows first (text lines), then split each line on wide gaps."""
    h, w = mask.shape
    y0, y1 = int(band[0] * h), int(band[1] * h)
    m = mask.copy()
    m[:y0] = False
    m[y1:] = False
    rows = np.where(m.sum(1) >= 3)[0]
    out = []
    if not len(rows):
        return out
    # consecutive rows (allowing small gaps, e.g. between two subtitle lines) form one block
    blocks, start, prev = [], rows[0], rows[0]
    for r in rows[1:]:
        if r - prev > gap:
            blocks.append((start, prev))
            start = r
        prev = r
    blocks.append((start, prev))
    for ry0, ry1 in blocks:
        cols = np.where(m[ry0:ry1 + 1].sum(0) > 0)[0]
        if len(cols) == 0 or m[ry0:ry1 + 1].sum() < min_px or ry1 - ry0 < 6:
            continue
        segs, cs, cp = [], cols[0], cols[0]
        for c in cols[1:]:
            if c - cp > gap * 2:
                segs.append((cs, cp))
                cs = c
            cp = c
        segs.append((cs, cp))
        for cx0, cx1 in segs:
            if cx1 - cx0 >= 12 and m[ry0:ry1 + 1, cx0:cx1 + 1].sum() >= min_px:
                out.append((cx0, ry0, cx1, ry1))
    return out


def detect(path, band=(0.0, 1.0), t0=0.0, dur=None, persist=5, pad=0.012):
    sw, sh, _ = probe(path)
    w = 360
    h = int(round(sh * w / sw)) // 2 * 2
    fr = frames(path, w, h, t0, dur)
    masks = np.stack([edge_mask(f) for f in fr])
    # text = an edge pixel that stays in place for `persist` frames (0.5 s); moving scenery does not
    k = persist
    per = np.zeros_like(masks)
    for i in range(len(masks)):
        a, b = max(0, i - k // 2), min(len(masks), i + k // 2 + 1)
        per[i] = masks[a:b].mean(0) >= 0.8
    found = []
    for i, m in enumerate(per):
        for b in boxes_in(m, band):
            found.append((t0 + i / FPS, b))
    # merge the same box across consecutive frames into one timed entry
    entries = []
    for t, b in found:
        for e in entries:
            if t - e["last"] <= 0.25 and _iou(e["box"], b) > 0.5:
                e["box"] = [min(e["box"][0], b[0]), min(e["box"][1], b[1]), max(e["box"][2], b[2]), max(e["box"][3], b[3])]
                e["last"] = t
                break
        else:
            entries.append({"t0": t, "last": t, "box": list(b)})
    out = []
    for e in entries:
        if e["last"] - e["t0"] < 0.3:   # flickers are not captions
            continue
        x0, y0, x1, y1 = e["box"]
        out.append({"t0": round(float(max(0.0, e["t0"] - 0.1)), 2), "t1": round(float(e["last"] + 0.15), 2),
                    "box": [round(float(max(0.0, x0 / w - pad)), 3), round(float(max(0.0, y0 / h - pad)), 3),
                            round(float(min(1.0, (x1 + 1) / w + pad)), 3), round(float(min(1.0, (y1 + 1) / h + pad)), 3)]})
    return out


def _iou(a, b):
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    ua = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / ua if ua else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--band", nargs=2, type=float, default=[0.0, 1.0])
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--dur", type=float)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--centered", action="store_true", help="keep only boxes centred horizontally (subtitles)")
    a = ap.parse_args()
    boxes = detect(fetch(a.src), tuple(a.band), a.start, a.dur)
    if a.centered:
        boxes = [b for b in boxes if abs((b["box"][0] + b["box"][2]) / 2 - 0.5) < 0.1]
    if a.json:
        print(json.dumps({"blur_boxes": boxes}))
    else:
        for b in boxes:
            print(f"{b['t0']:6.2f}-{b['t1']:6.2f}s  box {b['box']}")


if __name__ == "__main__":
    main()
