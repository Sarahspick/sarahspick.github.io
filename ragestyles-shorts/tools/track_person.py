"""Follow the main person in a clip and print a camera `path` for a 9:16 "full" shot in bench.py plans.

Usage (from ragestyles-shorts/):
  python3 tools/track_person.py work/youtube/X.mp4 <in_sec> <dur_sec> [--zoom 1.0] [--step 1.0] [--pick largest|center]
Prints JSON: [[t, zoom, cx, cy], ...] (t relative to the shot start). Paste it as the shot's "path" and set
"ease": "linear" on the shot so the camera glides between keyframes. Detection: torchvision Faster R-CNN
(mobilenet v3, COCO "person"), 4 samples per second, the biggest (or most central) person, then smoothed.
Weights come from download.pytorch.org the first time.
"""
import argparse
import json
import subprocess

import numpy as np
import torch
import torchvision

p = argparse.ArgumentParser()
p.add_argument("video")
p.add_argument("start", type=float)
p.add_argument("dur", type=float)
p.add_argument("--zoom", type=float, default=1.0)
p.add_argument("--step", type=float, default=1.0)
p.add_argument("--pick", default="largest", choices=["largest", "center"])
p.add_argument("--head", type=float, default=0.45, help="vertical focus inside the box (0 top, 1 feet)")
a = p.parse_args()

SW, SH, FPS = 640, 360, 4
raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(a.start), "-t", str(a.dur), "-i", a.video,
                      "-vf", f"fps={FPS},scale={SW}:{SH}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                     capture_output=True).stdout
frames = np.frombuffer(raw, np.uint8).reshape(-1, SH, SW, 3)
model = torchvision.models.detection.fasterrcnn_mobilenet_v3_large_fpn(weights="DEFAULT").eval()
torch.set_num_threads(4)

xs, ys, prev = [], [], None
with torch.no_grad():
    for i in range(0, len(frames), 8):
        batch = [torch.from_numpy(f.copy()).permute(2, 0, 1).float() / 255 for f in frames[i:i + 8]]
        for r in model(batch):
            boxes = [b.tolist() for b, l, s in zip(r["boxes"], r["labels"], r["scores"]) if l == 1 and s > 0.6]
            if not boxes:
                xs.append(np.nan); ys.append(np.nan); continue
            if a.pick == "center" or prev is not None:
                ref = prev if prev is not None else (SW / 2, SH / 2)
                # prefer big boxes near the last position
                b = max(boxes, key=lambda b: (b[2] - b[0]) * (b[3] - b[1]) / (1 + abs((b[0] + b[2]) / 2 - ref[0]) / 60))
            else:
                b = max(boxes, key=lambda b: (b[2] - b[0]) * (b[3] - b[1]))
            cx, cy = (b[0] + b[2]) / 2, b[1] + (b[3] - b[1]) * a.head
            prev = (cx, cy)
            xs.append(cx / SW); ys.append(cy / SH)

xs, ys = np.array(xs), np.array(ys)
idx = np.arange(len(xs))
for arr in (xs, ys):
    ok = ~np.isnan(arr)
    arr[:] = np.interp(idx, idx[ok], arr[ok]) if ok.any() else 0.5
k = np.ones(7) / 7  # ~1.75 s moving average
xs = np.convolve(np.pad(xs, 3, mode="edge"), k, "valid")
ys = np.convolve(np.pad(ys, 3, mode="edge"), k, "valid")
path = []
t = 0.0
while t <= a.dur + 1e-6:
    j = min(len(xs) - 1, int(round(t * FPS)))
    path.append([round(t, 2), a.zoom, round(float(xs[j]), 3), round(float(ys[j]), 3)])
    t += a.step
if path[-1][0] < a.dur:
    path.append([round(a.dur, 2), a.zoom, path[-1][2], path[-1][3]])
print(json.dumps(path))
