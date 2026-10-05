"""Peak ProMax editor: turns source clips into a commentary meme short from a JSON recipe.

The point is added value, not a re-upload: every short gets our own caption (the joke),
freeze frames that zoom in and explain the moment, red circles and arrows, slow-mo replays,
sound effects synthesized in sfx.py, a punchline clip, and a credit to the original creator.

Usage:  python3 peak_edit.py recipes/example.json

Recipe:
{
  "out": "out/my_short.mp4",
  "credit": "@original_creator",          # shown bottom left as "🎥 @original_creator"
  "segments": [
    {"clip": "src/a.mp4", "start": 0, "end": 5, "caption": "Bro had ONE job 😭",
     "speed": 1.0, "volume": 1.0, "label": "",
     "events": [
       {"t": 2.0, "sfx": "boom"},
       {"t": 2.0, "zoom": 1.8, "focus": [0.5, 0.4], "dur": 1.2},
       {"t": 2.0, "circle": [0.3, 0.3, 0.7, 0.6], "dur": 2},
       {"t": 2.3, "arrow": [0.5, 0.3], "angle": -120, "dur": 1.5},
       {"t": 2.0, "text": "OH!", "pos": [0.5, 0.2], "dur": 0.9},
       {"t": 2.0, "shake": 18},
       {"t": 2.0, "flash": true}
     ]},
    {"freeze": "src/a.mp4", "at": 3.4, "dur": 1.5, "caption": "Look at his face 💀", "events": [...]},
    {"clip": "src/a.mp4", "start": 2.5, "end": 4, "speed": 0.4, "label": "REPLAY", "caption": "..."},
    {"clip": "src/b.mp4", "start": 0, "end": 3, "caption": "My honest reaction:"}
  ]
}
Positions are fractions of the video area (0..1). Event times are seconds into the segment.
SFX names: boom, whoosh, pop, ding, kaching, stamp, sad_trombone, riser, bruh_horn, heartbeat, printer.
"""
import json
import os
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import sfx
from anim import (FPS, back_out, camera, cached_caption, clamp, draw_rich, ease_out, font, handle_sprite,
                  paste_scaled, prog, red_arrow, red_circle)
from meme_edit import W

MAX_H = 1920


def probe_size(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height:stream_side_data=rotation", "-of", "json", path],
                         capture_output=True, text=True, check=True).stdout
    s = json.loads(out)["streams"][0]
    w, h = s["width"], s["height"]
    rot = abs(int(next((d.get("rotation", 0) for d in s.get("side_data_list", [])), 0)))
    return (h, w) if rot in (90, 270) else (w, h)


def fit_filter(vw, vh):
    """Scale to cover the video area; letterboxed sources get a blurred fill instead of bars."""
    return (f"split[a][b];[a]scale={vw}:{vh}:force_original_aspect_ratio=increase,crop={vw}:{vh},"
            f"boxblur=30:2,eq=brightness=-0.15[bg];[b]scale={vw}:{vh}:force_original_aspect_ratio=decrease[fg];"
            f"[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1")


def read_frames(clip, start, end, speed, vw, vh):
    vf = f"setpts=PTS/{speed}," if speed != 1 else ""
    cmd = ["ffmpeg", "-v", "error", "-ss", str(start), "-to", str(end), "-i", clip,
           "-filter_complex", f"[0:v]{vf}fps={FPS},{fit_filter(vw, vh)}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    n = vw * vh * 3
    while True:
        buf = p.stdout.read(n)
        if len(buf) < n:
            break
        yield Image.frombytes("RGB", (vw, vh), buf).convert("RGBA")
    p.wait()


def read_audio(clip, start, end, speed, nsamples):
    tempo = []
    s = speed
    while s < 0.5:
        tempo.append("atempo=0.5")
        s /= 0.5
    tempo.append(f"atempo={s}")
    out = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(start), "-to", str(end), "-i", clip, "-vn",
                          "-af", ",".join(tempo), "-ac", "1", "-ar", str(sfx.SR), "-f", "f32le", "-"],
                         capture_output=True).stdout
    a = np.frombuffer(out, dtype="<f4").copy() if out else np.zeros(0, dtype=np.float32)
    a = np.pad(a, (0, max(0, nsamples - len(a))))[:nsamples]
    return a


SFX = {
    "boom": sfx.boom, "whoosh": sfx.whoosh, "pop": sfx.pop, "ding": sfx.ding, "kaching": sfx.kaching,
    "stamp": sfx.stamp, "sad_trombone": sfx.sad_trombone, "riser": sfx.riser, "bruh_horn": sfx.bruh_horn,
    "heartbeat": sfx.heartbeat, "printer": sfx.printer,
}


def pop_text_sprite(text, size=120):
    f = font("Anton.ttf", size)
    d = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    w = int(d.textlength(text, font=f)) + 80
    im = Image.new("RGBA", (w, int(size * 1.6)), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((40, 10), text, font=f, fill=(255, 255, 255), stroke_width=12, stroke_fill=(0, 0, 0))
    return im


def label_sprite(text):
    f = font("Anton.ttf", 56)
    d = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    w = int(d.textlength(text, font=f)) + 50
    im = Image.new("RGBA", (w, 84), (0, 0, 0, 0))
    dd = ImageDraw.Draw(im)
    dd.rounded_rectangle((0, 0, w - 1, 83), radius=16, fill=(235, 25, 40))
    dd.text((25, 4), text, font=f, fill=(255, 255, 255))
    return im


def credit_sprite(handle):
    f = font("RobotoCond.ttf", 34)
    im = Image.new("RGBA", (700, 56), (0, 0, 0, 0))
    draw_rich(im, (0, 4), f"🎥 {handle}", f, (255, 255, 255, 200))
    return im


def apply_events(frame, lt, events, vw, vh):
    """Overlays and camera for one frame at segment time lt."""
    zoom, focus, shake = 1.0, None, 0.0
    for e in events:
        t0 = e["t"]
        if lt < t0:
            continue
        dur = e.get("dur", 99)
        if "circle" in e and lt < t0 + dur:
            x0, y0, x1, y1 = e["circle"]
            red_circle(frame, (x0 * vw, y0 * vh, x1 * vw, y1 * vh), prog(lt, t0, 0.35), width=e.get("width", 12))
        if "arrow" in e and lt < t0 + dur:
            ax, ay = e["arrow"]
            red_arrow(frame, (ax * vw, ay * vh), e.get("angle", -120), e.get("length", 220), prog(lt, t0, 0.3))
        if "text" in e and lt < t0 + e.get("dur", 0.9):
            px, py = e.get("pos", [0.5, 0.25])
            paste_scaled(frame, pop_text_sprite(e["text"], e.get("size", 120)), (px * vw, py * vh),
                         back_out(prog(lt, t0, 0.25)))
    for e in events:
        t0 = e["t"]
        if "zoom" in e:
            dur = e.get("dur", 1.0)
            z = ease_out(prog(lt, t0, 0.2)) - ease_out(prog(lt, t0 + dur, 0.25))
            if z > 0:
                zoom = 1 + (e["zoom"] - 1) * z
                fx, fy = e.get("focus", [0.5, 0.5])
                focus = (fx * vw, fy * vh)
        if "shake" in e and lt >= t0:
            shake = max(shake, e["shake"] * max(0, 1 - (lt - t0) / e.get("dur", 0.45)))
    frame = camera(frame, zoom, focus, shake)
    for e in events:
        if e.get("flash") and e["t"] <= lt < e["t"] + 0.08:
            frame = Image.blend(frame, Image.new("RGBA", frame.size, (255, 255, 255, 255)), 0.55)
    return frame


def segment_frames(seg, vw, vh):
    if "freeze" in seg:
        frames = list(read_frames(seg["freeze"], seg["at"], seg["at"] + 0.2, 1, vw, vh))[:1]
        still = frames[0]
        n = int(seg.get("dur", 1.5) * FPS)
        return (still.copy() for _ in range(n)), n
    speed = seg.get("speed", 1.0)
    n = int((seg["end"] - seg["start"]) / speed * FPS)
    return read_frames(seg["clip"], seg["start"], seg["end"], speed, vw, vh), n


def segment_audio(seg, n):
    ns = int(n / FPS * sfx.SR)
    if "freeze" in seg:
        return np.zeros(ns, dtype=np.float32)
    a = read_audio(seg["clip"], seg["start"], seg["end"], seg.get("speed", 1.0), ns)
    return a * seg.get("volume", 1.0)


def build(recipe):
    segs = recipe["segments"]
    bar = max(cached_caption(s.get("caption", " ")).height for s in segs)
    first = segs[0].get("clip") or segs[0]["freeze"]
    sw, sh = probe_size(first)
    vh = int(min(max(W * sh / sw, W * 0.75), MAX_H - bar)) // 2 * 2
    H = bar + vh
    out = recipe["out"]
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    credit = credit_sprite(recipe["credit"]) if recipe.get("credit") else None
    audio_parts, events_audio, t_global = [], [], 0.0
    with tempfile.TemporaryDirectory() as tmp:
        vid = os.path.join(tmp, "v.mp4")
        p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                              "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                              "-pix_fmt", "yuv420p", vid], stdin=subprocess.PIPE)
        for seg in segs:
            frames, n = segment_frames(seg, W, vh)
            cap = cached_caption(seg.get("caption", " "))
            label = label_sprite(seg["label"]) if seg.get("label") else None
            evs = seg.get("events", [])
            written = 0
            last = None
            for i in range(n):
                fr = next(frames, None)
                if fr is None:
                    fr = last.copy() if last else Image.new("RGBA", (W, vh), (0, 0, 0, 255))
                last = fr
                lt = i / FPS
                fr = apply_events(fr.copy(), lt, evs, W, vh)
                canvas = Image.new("RGBA", (W, H), (255, 255, 255, 255))
                canvas.alpha_composite(fr, (0, bar))
                canvas.alpha_composite(cap, (0, (bar - cap.height) // 2))
                if label and int(lt * 2.5) % 2 == 0:
                    canvas.alpha_composite(label, (30, bar + 30))
                if credit:
                    canvas.alpha_composite(credit, (24, H - 56))
                canvas.alpha_composite(handle_sprite(), (W - 210, H - 56))
                p.stdin.write(canvas.convert("RGB").tobytes())
                written += 1
            audio_parts.append(segment_audio(seg, written))
            for e in evs:
                if "sfx" in e:
                    events_audio.append((t_global + e["t"], SFX[e["sfx"]](), e.get("gain", 0.9)))
            t_global += written / FPS
        p.stdin.close()
        p.wait()
        base = np.concatenate(audio_parts) * 0.85
        mixed = sfx.mix(t_global, events_audio, base)
        wav = os.path.join(tmp, "a.wav")
        sfx.write_wav(wav, mixed)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vid, "-i", wav, "-c:v", "copy", "-c:a", "aac",
                        "-b:a", "192k", "-shortest", "-movflags", "+faststart", out], check=True)
    return out


if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        print(build(json.load(f)))
