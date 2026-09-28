"""Timeline strips for picking edit points: one labelled frame every `step` seconds."""
import os, subprocess, sys
import cv2, numpy as np

def strip(path, out, step=1.0, h=150, cols=8, rotate=0):
    n = 0
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                               capture_output=True, text=True).stdout.strip())
    vf = f"fps=1/{step},scale=-2:{h}"
    if rotate == 180:
        vf = "transpose=1,transpose=1," + vf
    elif rotate == 90:
        vf = "transpose=1," + vf
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", vf, "-f", "image2pipe", "-vcodec", "png", "-"],
                         capture_output=True).stdout
    frames = []
    i = 0
    while True:
        j = raw.find(b"\x89PNG", i + 1)
        chunk = raw[i:j] if j > 0 else raw[i:]
        if chunk:
            im = cv2.imdecode(np.frombuffer(chunk, np.uint8), cv2.IMREAD_COLOR)
            if im is not None:
                frames.append(im)
        if j < 0:
            break
        i = j
    if not frames:
        return
    fw = frames[0].shape[1]
    tiles = []
    for k, f in enumerate(frames):
        f = cv2.resize(f, (fw, h))
        cv2.rectangle(f, (0, 0), (74, 24), (0, 0, 0), -1)
        cv2.putText(f, f"{k*step:.1f}s", (4, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 1)
        tiles.append(f)
    while len(tiles) % cols:
        tiles.append(np.zeros_like(tiles[0]))
    rows = [np.hstack(tiles[r:r + cols]) for r in range(0, len(tiles), cols)]
    img = np.vstack(rows)
    title = np.zeros((30, img.shape[1], 3), np.uint8)
    cv2.putText(title, f"{os.path.basename(path)}  dur={dur:.1f}s", (6, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.imwrite(out, np.vstack([title, img]), [cv2.IMWRITE_JPEG_QUALITY, 82])

if __name__ == "__main__":
    src, out, step = sys.argv[1], sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
    rot = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    strip(src, out, step, rotate=rot)
