"""Vertical Shorts cut from a finished documentary (1080x1920).

The 16:9 documentary frame sits in the middle over a blurred, darkened copy of itself; a headline sits above it,
phrase captions (from the narration's word timings) below it, and the last seconds point to the full film.
Audio is the documentary's own mix for the same span.

    python make_doc_short.py documentaries/walmart_machine.json shorts.<name>
"""
import json
import os
import subprocess

from PIL import Image, ImageDraw

from . import doc_gfx
from .config import OUTPUT, WORK
from .doc_gfx import ACCENT, SOFT, WHITE, ease, fade, font
from .doc_render import FPS, build_timeline, run

SW, SH = 1080, 1920
VID_Y = 640            # top of the 16:9 picture (608 px tall at 1080 wide)


def _ranges(items, seg_ranges):
    segs = [it for it in items if it["kind"] == "seg"]
    out = []
    for a, b in seg_ranges:
        s0, s1 = segs[a], segs[b]
        out.append((s0["start"], s1["start"] + s1["dur"] - 0.25, segs[a:b + 1]))
    return out


def _phrases(segs, offset):
    """[(start, end, text)] in short-local time, 2-4 words per phrase, split at punctuation."""
    out = []
    for it in segs:
        chunk = []
        for w, s, e in it["words"]:
            chunk.append((w, s, e))
            n = len(chunk)
            if n >= 4 or (n >= 2 and w[-1] in ",.?!:;"):
                out.append((it["voice_at"] + chunk[0][1], it["voice_at"] + chunk[-1][2], " ".join(x[0] for x in chunk)))
                chunk = []
        if chunk:
            out.append((it["voice_at"] + chunk[0][1], it["voice_at"] + chunk[-1][2], " ".join(x[0] for x in chunk)))
    return [(a - offset, b - offset, t) for a, b, t in out]


def overlay_fn(headline, phrases, dur, end_note):
    fh = font("sans", 82, "Black")
    fc = font("sans", 62, "ExtraBold")
    fe = font("sans", 44, "Bold")

    def frame(t):
        img = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        # headline: lines, the one wrapped in *stars* in accent colour
        a = 1.0                 # no fade: the first frame is the thumbnail people scroll past
        y = 300
        for line in headline:
            accent = line.startswith("*")
            txt = line.strip("*")
            w = d.textlength(txt, font=fh)
            d.text(((SW - w) / 2 + 3, y + 4), txt, font=fh, fill=(0, 0, 0, int(150 * a)))
            d.text(((SW - w) / 2, y), txt, font=fh, fill=(ACCENT if accent else WHITE) + (int(255 * a),))
            y += 96
        # caption under the picture
        cur = [p for p in phrases if p[0] - 0.05 <= t < p[1] + 0.15]
        if cur and t < dur - 3.0:
            txt = cur[-1][2].upper()
            lines = doc_gfx._wrap(d, txt, fc, 960)
            cy = VID_Y + 608 + 90
            for ln in lines[:2]:
                w = d.textlength(ln, font=fc)
                for dx, dy in ((-3, 0), (3, 0), (0, -3), (0, 3), (3, 4)):
                    d.text(((SW - w) / 2 + dx, cy + dy), ln, font=fc, fill=(0, 0, 0, 220))
                d.text(((SW - w) / 2, cy), ln, font=fc, fill=WHITE + (255,))
                cy += 76
        # end note
        if t > dur - 3.0:
            ea = ease((t - (dur - 3.0)) / 0.5)
            w = d.textlength(end_note, font=fe)
            d.rounded_rectangle([(SW - w) / 2 - 36, VID_Y + 608 + 70, (SW + w) / 2 + 36, VID_Y + 608 + 170], 20,
                                fill=ACCENT + (int(235 * ea),))
            d.text(((SW - w) / 2, VID_Y + 608 + 94), end_note, font=fe, fill=WHITE + (int(255 * ea),))
        return img
    return frame


def make(doc_path, name):
    doc = json.load(open(doc_path))
    cfg = doc["shorts"][name]
    work = os.path.join(WORK, doc.get("work", doc["id"]))
    items, total = build_timeline(doc, work)
    long_mp4 = os.path.join(OUTPUT, f"{doc['id']}.mp4")
    rngs = _ranges(items, cfg["segments"])
    sdir = os.path.join(work, "short_" + name)
    os.makedirs(sdir, exist_ok=True)
    parts, phrases, off = [], [], 0.0
    for k, (a, b, segs) in enumerate(rngs):
        p = os.path.join(sdir, f"part{k}.mp4")
        skip = max(0.0, 0.9 - a)   # the film fades in from black: hold its first clear frame instead
        run(["ffmpeg", "-y", "-v", "error", "-ss", f"{a + skip:.3f}", "-t", f"{b - a - skip:.3f}", "-i", long_mp4,
             "-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", long_mp4, "-map", "0:v", "-map", "1:a",
             "-vf", f"tpad=start_duration={skip:.3f}:start_mode=clone", "-af", "afade=t=in:d=0.08",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "15", "-c:a", "pcm_s16le", p.replace(".mp4", ".mov")])
        parts.append(p.replace(".mp4", ".mov"))
        phrases += _phrases(segs, a - off)
        off += b - a
    dur = off
    lst = os.path.join(sdir, "parts.txt")
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    joined = os.path.join(sdir, "joined.mov")
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", joined])

    ov = os.path.join(sdir, "overlay.mov")
    fn = overlay_fn(cfg["headline"], phrases, dur, cfg.get("end_note", "Full documentary on the channel"))
    _write_rgba(fn, dur, ov)

    out = os.path.join(OUTPUT, f"{doc['id']}_short_{name}.mp4")
    fc = (f"[0:v]split[a][b];[a]scale={SW}:{SH}:force_original_aspect_ratio=increase,crop={SW}:{SH},"
          f"gblur=sigma=38,eq=brightness=-0.28:saturation=0.8[bg];"
          f"[b]scale={SW}:-2[fg];[bg][fg]overlay=0:{VID_Y}[v1];[v1][1:v]overlay=0:0,"
          f"fade=t=out:st={dur - 0.5:.3f}:d=0.5,format=yuv420p[v]")
    run(["ffmpeg", "-y", "-v", "error", "-i", joined, "-i", ov, "-filter_complex", fc, "-map", "[v]", "-map", "0:a",
         "-af", f"loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=out:st={dur - 0.8:.3f}:d=0.8", "-ar", "48000",
         "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-r", str(FPS), "-c:a", "aac", "-b:a", "256k",
         "-movflags", "+faststart", out])
    print("wrote", out, f"{dur:.1f}s")
    return out


def _write_rgba(fn, dur, out):
    n = round(dur * FPS)
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{SW}x{SH}",
                          "-r", str(FPS), "-i", "-", "-c:v", "png", "-pix_fmt", "rgba", out], stdin=subprocess.PIPE)
    for i in range(n):
        p.stdin.write(fn(i / FPS).tobytes())
    p.stdin.close()
    p.wait()
