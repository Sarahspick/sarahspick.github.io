"""Beat-synced sports edit renderer for Shorts.

python3 shorts/edit_engine.py PLAN.json OUT.mp4

PLAN.json:
{
  "music": "music.mp3", "music_start": 3.1,      # seconds cut from the start of the track
  "bpm": 150, "drop": 1.70,                       # drop time in the OUTPUT timeline; beat grid is anchored here
  "font": "fonts/Anton.ttf", "watermark": "optional small text",
  "segments": [
    {"clip": "clips/a.mp4", "beats": 4, "src": 8.0, "speed": [1.0, 0.45], "split": 0.4,
     "text": "ALIEN MODE", "text_at": 0.25, "shake": true, "dark": false, "freeze_tail": 0.0}
  ]
}
The first segment runs from 0 to the drop ("beats" ignored); the rest are measured in beats.
speed: one number, or [before, after] with the switch at `split` (fraction of the segment).
Each cut gets a zoom punch and a white flash, every beat a small zoom bump, text pops in with an overshoot.
Paths in the plan are relative to the plan file. Output: 1080x1920, 30 fps, H.264/AAC, -14 LUFS.
"""
import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

try:
    import imageio_ffmpeg
    FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    FFMPEG = "ffmpeg"

W, H, FPS = 1080, 1920, 30
DEC_FPS = 60  # decode rate, gives slow motion real in-between frames to blend


def decode(path, start, dur):
    """Frames of path[start:start+dur] scaled/cropped to 9:16, at DEC_FPS, as uint8 array."""
    cmd = [FFMPEG, "-v", "error", "-ss", f"{max(0, start):.3f}", "-t", f"{dur + 0.1:.3f}", "-i", path,
           "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={DEC_FPS}",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    n = len(raw) // (W * H * 3)
    return np.frombuffer(raw[: n * W * H * 3], dtype=np.uint8).reshape(n, H, W, 3)


def src_offset(local, seg_len, speed, split):
    """Source seconds elapsed after `local` output seconds, for a one or two step speed curve."""
    if not isinstance(speed, list):
        return local * speed
    cut = seg_len * split
    if local <= cut:
        return local * speed[0]
    return cut * speed[0] + (local - cut) * speed[1]


def ease_out(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def pop(x):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    return 1 + 0.15 * math.sin(x * math.pi) - (1 - x) ** 3


def grade(f, dark=False):
    x = f.astype(np.float32) / 255.0
    lum = x.mean(axis=2, keepdims=True)
    x = lum + (x - lum) * 1.25                     # saturation
    x = (x - 0.5) * 1.18 + 0.5                     # contrast
    x = x * np.array([1.02, 1.0, 0.96]) if not dark else x * np.array([0.8, 0.85, 1.0]) * 0.8
    return x


def main():
    plan_path, out = sys.argv[1], sys.argv[2]
    base = os.path.dirname(os.path.abspath(plan_path))
    P = json.load(open(plan_path))
    rel = lambda p: p if os.path.isabs(p) else os.path.join(base, p)
    beat = 60.0 / P["bpm"]
    drop = P["drop"]

    # timeline
    segs, t = [], 0.0
    for k, s in enumerate(P["segments"]):
        length = drop if k == 0 else s["beats"] * beat
        segs.append(dict(s, t0=t, t1=t + length))
        t += length
    total = t
    n = int(round(total * FPS))

    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    vig = 1.0 - 0.55 * np.clip(np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2)) - 0.45, 0, 1) ** 1.6
    vig = vig[..., None]

    font_path = rel(P["font"])
    fonts = {}
    def font(size):
        if size not in fonts:
            fonts[size] = ImageFont.truetype(font_path, size)
        return fonts[size]

    enc = subprocess.Popen([FFMPEG, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                            "-pix_fmt", "yuv420p", out + ".video.mp4"], stdin=subprocess.PIPE)

    cur, frames = None, None
    for i in range(n):
        t = i / FPS
        k = next(j for j, s in enumerate(segs) if t < s["t1"] or j == len(segs) - 1)
        s = segs[k]
        seg_len = s["t1"] - s["t0"]
        if cur != k:
            span = src_offset(seg_len, seg_len, s.get("speed", 1.0), s.get("split", 0.5))
            frames = decode(rel(s["clip"]), s.get("src", 0.0), span)
            cur = k
        local = t - s["t0"]
        freeze = s.get("freeze_tail", 0.0)
        if freeze and local > seg_len - freeze:
            local = seg_len - freeze
        pos = src_offset(local, seg_len, s.get("speed", 1.0), s.get("split", 0.5)) * DEC_FPS
        a = min(int(pos), len(frames) - 1)
        b = min(a + 1, len(frames) - 1)
        w = pos - int(pos)
        f = frames[a].astype(np.float32) * (1 - w) + frames[b].astype(np.float32) * w if w > 0.05 else frames[a]

        x = grade(f, s.get("dark", False)) * vig
        img = Image.fromarray((np.clip(x, 0, 1) * 255).astype(np.uint8))

        # zoom: punch on the cut, bump on every beat after the drop, slow push inside the segment
        z = 1.0 + 0.03 * local / max(seg_len, 0.1)
        if k > 0:
            z += 0.16 * (1 - ease_out((t - s["t0"]) / 0.28))
            since_beat = (t - drop) % beat
            z += 0.035 * (1 - ease_out(since_beat / 0.18))
        dx = dy = 0
        if s.get("shake") and k > 0 and (t - s["t0"]) < 0.3:
            amp = 18 * (1 - (t - s["t0"]) / 0.3)
            dx, dy = int(amp * math.sin(i * 2.1)), int(amp * math.cos(i * 1.7))
        if dx or dy:
            z = max(z, 1.04)  # room to shake inside the frame
        if z > 1.001:
            cw, ch = W / z, H / z
            l = min(max((W - cw) / 2 + dx, 0), W - cw)
            tp = min(max((H - ch) / 2 + dy, 0), H - ch)
            img = img.resize((W, H), Image.BILINEAR, box=(l, tp, l + cw, tp + ch))

        d = ImageDraw.Draw(img)
        if s.get("text"):
            p = pop((local - s.get("text_at", 0.0)) / 0.22)
            size = int(s.get("text_size", 170) * p)
            if size >= 8:
                d.text((W // 2, int(H * 0.36)), s["text"], font=font(size), fill=(255, 255, 255),
                       stroke_width=max(2, size // 16), stroke_fill=(0, 0, 0), anchor="mm")
        if P.get("watermark"):
            d.text((40, 70), P["watermark"], font=font(30), fill=(235, 235, 235), stroke_width=2, stroke_fill=(0, 0, 0))

        out_f = np.asarray(img).astype(np.float32)
        if k > 0 and (t - s["t0"]) < 0.07:
            out_f = out_f + (255 - out_f) * 0.55 * (1 - (t - s["t0"]) / 0.07)
        if t > total - 0.35:
            out_f *= max(0.0, (total - t) / 0.35)
        enc.stdin.write(np.clip(out_f, 0, 255).astype(np.uint8).tobytes())
    enc.stdin.close()
    enc.wait()

    subprocess.run([FFMPEG, "-y", "-v", "error", "-i", out + ".video.mp4", "-ss", str(P.get("music_start", 0)),
                    "-i", rel(P["music"]), "-filter_complex",
                    f"[1:a]atrim=0:{total:.3f},afade=t=out:st={total - 0.4:.3f}:d=0.4,loudnorm=I=-14:TP=-1.5:LRA=11[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
                    "-shortest", "-movflags", "+faststart", out], check=True)
    os.remove(out + ".video.mp4")
    print("wrote", out, f"{total:.2f}s")


if __name__ == "__main__":
    main()
