"""Fine strips of specific windows: python3 window_strip.py out.jpg clip:start:end:step[:rot] ..."""
import subprocess, sys, os
import cv2, numpy as np
CLIPS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "work", "clips")
rows = []
for spec in sys.argv[2:]:
    parts = spec.split(":")
    clip, a, b, step = parts[0], float(parts[1]), float(parts[2]), float(parts[3])
    rot = int(parts[4]) if len(parts) > 4 else 0
    vf = "scale=-2:120"
    if rot == 180:
        vf = "hflip,vflip," + vf
    tiles = []
    for t in np.arange(a, b + 1e-6, step):
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", f"{CLIPS}/{clip}.mp4", "-frames:v", "1",
                              "-vf", vf, "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
        im = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
        if im is None:
            continue
        cv2.rectangle(im, (0, 0), (60, 18), (0, 0, 0), -1)
        cv2.putText(im, f"{t:.1f}", (3, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)
        tiles.append(im)
    lab = np.zeros((120, 110, 3), np.uint8)
    cv2.putText(lab, clip[-6:], (4, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    row = np.hstack([lab] + tiles)
    rows.append(row)
wmax = max(r.shape[1] for r in rows)
rows = [np.hstack([r, np.zeros((r.shape[0], wmax - r.shape[1], 3), np.uint8)]) for r in rows]
cv2.imwrite(sys.argv[1], np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 82])
