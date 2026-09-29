"""Benchmark-style shorts renderer: JSON plan -> finished 1080x1920 / 30 fps MP4.

Built from what 40M+ view Shorts do (see ../BENCHMARK.md), nothing else:
  * layouts: "full" (9:16 crop), "meme" (clip in a box on a plain card, caption above), "blur" (clip on a blurred copy)
    Channel default since 2026-09 (DEFAULT_LAYOUT): "blur", 1:1 box at y=300, title above the box, captions
    ("cap" / "big") directly under it, TikTok Sans in white with *yellow* and ~orange~ solid highlights
  * per-shot camera: eased zoom/pan keyframes, punch-in zooms, slow motion (real frames when the source allows)
  * one short caption line that changes at story beats, italic *action* labels, reaction labels, chapter labels
  * callouts pinned to the subject: plain red arrow, hand-drawn red circle (they follow the crop)
  * natural sound from the source + a few SFX, loudness -14 LUFS, x264 + AAC
No badge, no title bar, no shake or glitch.

Usage: python3 bench.py plans/b1_xxx.json [--out file.mp4] [--frames 0,45,90 --stills dir]
"""
import argparse
import json
import math
import os
import subprocess
import sys
import tempfile

import cv2
import numpy as np
import pyloudnorm as pyln
import soundfile as sf
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import render as R  # noqa: E402  (text, emoji, crop and audio helpers)

W, H, FPS, SR = 1080, 1920, 30, 48000
ROOT = os.path.dirname(HERE)
SRC_DIR = os.environ.get("RS_SOURCES", os.path.join(ROOT, "work", "dvids"))
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
R.FONTS.update({"Inter ExtraBold": "Inter-ExtraBold.ttf", "Inter Bold": "Inter-Bold.ttf",
                "Inter SemiBold": "Inter-SemiBold.ttf", "Dela Gothic One": "DelaGothicOne-Regular.ttf",
                "Lilita One": "LilitaOne-Regular.ttf", "Titan One": "TitanOne-Regular.ttf", "Bungee": "Bungee-Regular.ttf",
                "Russo One": "RussoOne-Regular.ttf", "TikTok Sans SemiBold": "TikTokSans-SemiBold.ttf",
                "TikTok Sans Bold": "TikTokSans-Bold.ttf", "TikTok Sans ExtraBold": "TikTokSans-ExtraBold.ttf",
                "TikTok Sans Black": "TikTokSans-Black.ttf"})
# channel palette (profile picture = Super Saiyan): white text, *yellow* and ~orange~ as two separate solid
# highlight colors (the owner rejected the single yellow-orange gradient), black edge
SAIYAN = {"*": ((255, 236, 92), (255, 140, 0)), "~": ((255, 170, 40), (232, 62, 0)), "^": ((255, 255, 255), (255, 214, 120))}
YELLOW, ORANGE = (255, 214, 0), (255, 128, 0)
HILITE = {"*": YELLOW, "~": ORANGE}
EDGE = (0, 0, 0)
# caption font: TikTok Sans, the most common caption look in 40M+ view Shorts (see BENCHMARK.md, fonts)
CAP_FONT = "TikTok Sans"
# default layout: the clip in a 1:1 box (full width) on a blurred, darkened copy of itself
DEFAULT_LAYOUT = {"mode": "blur", "box_aspect": 1.0, "box_top": 300}
RED = (232, 28, 28)


def src_path(src):
    """"963333" -> work/dvids/963333.mp4 ; "archive/GettingR1951" or "commons/wsm_stones.webm" -> work/<path>."""
    if "/" in src:
        p = os.path.join(ROOT, "work", src)
        return p if os.path.splitext(p)[1] else p + ".mp4"
    return os.path.join(SRC_DIR, src + ".mp4")
# named ffmpeg audio chains for source sound ("af" on a shot or an audio clip)
AF = {
    # speech lifted out of a room: cut rumble and hiss, add presence, even out the level
    "voice": "highpass=f=90,lowpass=f=9000,equalizer=f=2800:t=q:w=1.2:g=3,"
             "acompressor=threshold=-26dB:ratio=3.5:attack=4:release=120:makeup=8",
    # old optical film soundtrack: tame hiss and rumble, keep the narrator forward
    "film": "highpass=f=80,lowpass=f=7500,afftdn=nr=10:nf=-32,"
            "acompressor=threshold=-24dB:ratio=2.5:attack=6:release=160:makeup=4",
    # quiet crowd / room ambience brought up without pumping
    "ambience": "highpass=f=70,acompressor=threshold=-40dB:ratio=2.5:attack=20:release=250:makeup=14",
}

# caption styles (sizes are for a 1080 px wide frame)
STYLES = {
    # channel style (2026-09 feedback): title at the top, captions directly under the video box
    "title": dict(font=CAP_FONT + " Black", size=74, color=(255, 255, 255), stroke=7, shadow=True, upper=False,
                  italic=0.0, colors=HILITE, stroke_color=EDGE, max_w=1000),
    "cap": dict(font=CAP_FONT + " ExtraBold", size=62, color=(255, 255, 255), stroke=6, shadow=True, upper=False,
                italic=0.0, colors=HILITE, stroke_color=EDGE, max_w=920),
    # big punch label under the video ("20.00 FLAT")
    "big": dict(font=CAP_FONT + " Black", size=84, color=(255, 255, 255), stroke=7, shadow=True, upper=True,
                italic=0.0, colors=HILITE, stroke_color=EDGE, max_w=940),
    # small pill ("TEST 3/10", "1910")
    "tag": dict(font=CAP_FONT + " ExtraBold", size=38, color=(20, 10, 0), stroke=0, shadow=False, upper=True,
                italic=0.0, bg=YELLOW, pad=(22, 10)),
    # the 2026-09 Dela Gothic One look with the gradient highlight (kept for old plans)
    "title_dela": dict(font="Dela Gothic One", size=68, color=(255, 255, 255), stroke=7, shadow=True, upper=False,
                       italic=0.0, gradients=SAIYAN, stroke_color=(28, 12, 0), max_w=1000),
    "cap_dela": dict(font="Dela Gothic One", size=58, color=(255, 255, 255), stroke=6, shadow=True, upper=False,
                     italic=0.0, gradients=SAIYAN, stroke_color=(28, 12, 0), max_w=920),
    # black text on the plain card, just above the clip ("Define Aura" format)
    "meme": dict(font="Inter ExtraBold", size=66, color=(0, 0, 0), stroke=0, shadow=False, upper=False, italic=0.0),
    # white bold italic with a dark edge, upper third of a full-screen clip ("Old gymnastics judging was INSANE")
    "top": dict(font="Montserrat ExtraBold", size=70, color=(255, 255, 255), stroke=7, shadow=True, upper=False,
                italic=0.18),
    # *action* label next to the moment ("*BIG hop*")
    "action": dict(font="Montserrat ExtraBold", size=58, color=(255, 255, 255), stroke=6, shadow=True, upper=False,
                   italic=0.18),
    # reaction label above a reaction shot ("His Teammate:")
    "label": dict(font="Inter SemiBold", size=58, color=(255, 255, 255), stroke=0, shadow=True, upper=False,
                  italic=0.0),
    # chapter marker ("2004" / "DAY 1")
    "chapter": dict(font="Anton", size=150, color=(255, 214, 10), stroke=9, shadow=True, upper=True, italic=0.16),
    # spoken-word subtitles (speech from the source), lower third
    "sub": dict(font="Montserrat ExtraBold", size=60, color=(255, 255, 255), stroke=7, shadow=True, upper=False,
                italic=0.0),
    # (old) condensed label under the clip ("6 CHIN-UPS")
    "big_anton": dict(font="Anton", size=104, color=(255, 214, 10), stroke=0, shadow=True, upper=True, italic=0.0),
    # (old) small counter pill
    "tag_old": dict(font="Montserrat ExtraBold", size=40, color=(20, 20, 20), stroke=0, shadow=False, upper=True,
                italic=0.0, bg=(255, 214, 10), pad=(22, 10)),
    # (old) title on a dark card
    "title_old": dict(font="Montserrat Black", size=74, color=(255, 255, 255), stroke=0, shadow=True, upper=False,
                  italic=0.0),
    # left-aligned multi-line list (summary card)
    "list": dict(font="Montserrat ExtraBold", size=44, color=(255, 255, 255), stroke=0, shadow=True, upper=False,
                 italic=0.0, align="left", max_lines=14, line_gap=0.32),
    # story line in a chapter ("HE FINISHED LAST")
    "story": dict(font="Anton", size=84, color=(255, 255, 255), stroke=7, shadow=True, upper=True, italic=0.1),
}


# ------------------------------------------------------------------ small helpers

def ease(x, kind="inout"):
    x = min(1.0, max(0.0, x))
    if kind == "linear":
        return x
    if kind == "out":
        return 1 - (1 - x) ** 3
    return x * x * (3 - 2 * x)


def lerp(a, b, k):
    return a + (b - a) * k


def kf(v, k):
    """[start, end] keyframe pair or a constant."""
    return lerp(v[0], v[1], k) if isinstance(v, (list, tuple)) else v


def probe(path):
    d = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", path],
                                  capture_output=True, text=True, check=True).stdout)
    v = [s for s in d["streams"] if s["codec_type"] == "video"][0]
    num, den = (int(x) for x in v["r_frame_rate"].split("/"))
    return {"w": int(v["width"]), "h": int(v["height"]), "fps": num / den, "dur": float(d["format"]["duration"]),
            "audio": any(s["codec_type"] == "audio" for s in d["streams"])}


def shear(img, k):
    """Fake italic: slant an RGBA image to the right by k (x shift per y)."""
    if not k:
        return img
    w, h = img.size
    extra = int(abs(k) * h) + 2
    out = img.transform((w + extra, h), Image.AFFINE, (1, k, -k * h if k > 0 else 0, 0, 1, 0), Image.BICUBIC)
    return out.crop(out.getbbox()) if out.getbbox() else out


def caption_image(text, style, **over):
    st = dict(STYLES[style])
    st.update(over)
    img = R.render_text(text, font_name=st["font"], size=st["size"], color=tuple(st["color"]), stroke=st["stroke"],
                        shadow=st["shadow"], upper=st["upper"], max_w=st.get("max_w", 960),
                        max_lines=st.get("max_lines", 2), min_size=int(st["size"] * 0.6),
                        align=st.get("align", "center"), line_gap=st.get("line_gap", 0.08),
                        bg=tuple(st["bg"]) if st.get("bg") else None, pad=tuple(st.get("pad", (28, 18))),
                        gradients=st.get("gradients"), stroke_color=tuple(st.get("stroke_color", (0, 0, 0))),
                        outline=st.get("outline", 0), colors=st.get("colors"))
    return shear(img, st["italic"])


def arrow_image(length=190, width=30, head=78, color=RED):
    """Plain red arrow pointing right; the tip is the right-middle pixel."""
    pad = 14
    w, h = length + 2 * pad, head + 2 * pad
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cy = h / 2
    tip = w - pad
    base = tip - head * 0.95
    pts = [(pad, cy - width / 2), (base, cy - width / 2), (base, cy - head / 2), (tip, cy), (base, cy + head / 2),
           (base, cy + width / 2), (pad, cy + width / 2)]
    d.polygon(pts, fill=color + (255,), outline=(120, 0, 0, 255))
    d.line(pts + [pts[0]], fill=(125, 0, 0, 255), width=3)
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sh.putalpha(img.split()[3].point(lambda v: int(v * 0.45)))
    sh = sh.filter(ImageFilter.GaussianBlur(5))
    out = Image.new("RGBA", (w + 8, h + 8), (0, 0, 0, 0))
    out.alpha_composite(sh, (6, 7))
    out.alpha_composite(img, (0, 0))
    return out, (tip, cy)


def panel_image(m, k):
    """Info panel (dark rounded box, left-aligned rows) showing the header and the first k rows.
    m: {"header": "RESULTS", "rows": [{"t", "text"}], "w": px, "size": px}. Rows use the caption syntax
    (*yellow*, ~orange~, :emoji:). The box grows by one row each time a row appears."""
    size, w, pad = m.get("size", 46), int(m.get("w", 600)), 26
    txt = dict(font_name=CAP_FONT + " ExtraBold", size=size, stroke=4, shadow=False, upper=True, align="left",
               max_w=w - 2 * pad, max_lines=1, min_size=24, colors=HILITE, stroke_color=EDGE)
    head = R.render_text(m["header"], **dict(txt, size=int(size * 0.78), color=YELLOW)) if m.get("header") else None
    rows = [R.render_text(r["text"], **txt) for r in m["rows"]][:k]
    gap = int(size * 0.28)
    hh = head.height + gap if head else 0
    H_ = pad * 2 + hh + sum(r.height for r in rows) + gap * max(0, len(rows) - 1) - (gap if head and not rows else 0)
    img = Image.new("RGBA", (w, H_), (0, 0, 0, 0))
    ImageDraw.Draw(img).rounded_rectangle((0, 0, w - 1, H_ - 1), radius=28, fill=(10, 10, 14, int(255 * m.get("alpha", 0.62))))
    y = pad
    if head:
        img.alpha_composite(head, (pad, y))
        y += hh
    for r in rows:
        img.alpha_composite(r, (pad, y))
        y += r.height + gap
    return img


def rotated_arrow(angle, length):
    """Arrow pointing along `angle` (degrees, screen coords: 0 = right, 90 = down). Returns image and tip offset."""
    img, (tx, ty) = arrow_image(length)
    cx, cy = img.width / 2, img.height / 2
    rot = img.rotate(-angle, resample=Image.BICUBIC, expand=True)
    a = math.radians(angle)
    dx, dy = tx - cx, ty - cy
    rx, ry = dx * math.cos(a) - dy * math.sin(a), dx * math.sin(a) + dy * math.cos(a)
    return rot, (rot.width / 2 + rx, rot.height / 2 + ry)


_VIG = {}


def R_vignette(w, h, amount):
    """Radial darkening mask, 1 in the middle, 1 - amount in the corners."""
    key = (w, h, amount)
    if key not in _VIG:
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2) / math.sqrt(2)
        _VIG[key] = (1 - amount * np.clip(r, 0, 1) ** 1.6).astype(np.float32)
    return _VIG[key]


# ------------------------------------------------------------------ video streams

class ShotStream:
    """Frames of one shot at the output rate, decoded on the fly (4K safe)."""

    def __init__(self, shot, n_frames):
        path = src_path(shot["src"])
        self.info = probe(path)
        speed = float(shot.get("speed", 1.0))
        rot = shot.get("rotate", 0)
        w, h = self.info["w"], self.info["h"]
        filters = []
        if rot == 90:
            filters.append("transpose=1")
            w, h = h, w
        elif rot in (-90, 270):
            filters.append("transpose=2")
            w, h = h, w
        pw = shot.get("prescale")
        if pw and pw < w:
            h = int(round(h * pw / w / 2)) * 2
            w = pw
            filters.append(f"scale={w}:{h}")
        if abs(speed - 1) > 1e-3:
            filters.append(f"setpts=PTS/{speed:.5f}")
            if self.info["fps"] / speed < FPS - 1 and shot.get("interp", True):
                filters.append(f"minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1")
        filters.append(f"fps={FPS}")
        self.w, self.h, self.n = w, h, n_frames
        n_read = 1 if shot.get("still") else n_frames + 2  # still: freeze the frame at `in` for the whole shot
        cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", f"{shot['in']:.3f}", "-i", path,
               "-vf", ",".join(filters), "-frames:v", str(n_read), "-an", "-f", "rawvideo", "-pix_fmt", "rgb24",
               "-"]
        self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self.last = None

    def read(self):
        size = self.w * self.h * 3
        buf = self.proc.stdout.read(size)
        if len(buf) == size:
            self.last = np.frombuffer(buf, np.uint8).reshape(self.h, self.w, 3)
        if self.last is None:
            raise RuntimeError("no frames decoded")
        return self.last

    def close(self):
        try:
            self.proc.stdout.close()
            self.proc.kill()
        except Exception:
            pass


# ------------------------------------------------------------------ renderer

class Bench:
    def __init__(self, plan):
        self.p = plan
        lay = plan.get("layout", DEFAULT_LAYOUT)
        self.mode = lay.get("mode", "full")
        self.bg = tuple(lay.get("bg", (255, 255, 255)))
        self.box_aspect = lay.get("box_aspect", 1.0)
        self.box_y = lay.get("box_y", 0.47)
        self.box_top = lay.get("box_top")
        self.darken = lay.get("darken", 0.5)
        t = 0.0
        self.timeline = []
        for s in plan["shots"]:
            n = int(round(s["dur"] * FPS))
            self.timeline.append({"shot": s, "t0": t, "n": n, "i0": int(round(t * FPS))})
            t += n / FPS
        self.total = t
        self.n_frames = sum(x["n"] for x in self.timeline)
        self.caps = []
        for c in plan.get("captions", []):
            over = {k: c[k] for k in ("size", "color", "font", "italic", "stroke", "max_w", "max_lines", "align",
                                      "line_gap", "bg", "pad", "upper", "shadow") if k in c}
            img = caption_image(c["text"], c.get("style", "top"), **over)
            self.caps.append((c, R.to_np_rgba(img)))
        self.marks = []
        for m in plan.get("marks", []):
            if m["type"] == "arrow":
                img, tip = rotated_arrow(m.get("angle", 135), m.get("len", 190))
                self.marks.append((m, R.to_np_rgba(img), tip))
            elif m["type"] == "panel":  # leaderboard / info box whose rows appear one by one (owner: info panel)
                states = [R.to_np_rgba(panel_image(m, k)) for k in range(len(m["rows"]) + 1)]
                self.marks.append((m, states, None))
            else:
                self.marks.append((m, None, None))

    # region of the output frame that shows the clip
    def region(self, shot):
        mode = shot.get("layout", self.mode)
        if mode == "full":
            return 0, 0, W, H
        aspect = shot.get("box_aspect", self.box_aspect)
        rw = int(shot.get("box_w", self.p.get("layout", {}).get("box_w", W))) // 2 * 2
        rh = int(round(rw / aspect / 2)) * 2
        if self.box_top is not None and "box_y" not in shot:
            y = int(self.box_top)
        else:
            y = int(round(H * shot.get("box_y", self.box_y) - rh / 2))
        return (W - rw) // 2, y, rw, rh

    def cam(self, shot, lt):
        dur = shot["dur"]
        if "path" in shot:  # camera keyframes [[t, zoom, cx, cy], ...], eased between each pair (push in on a pose, hold)
            pts = shot["path"]
            zoom, cx, cy = pts[-1][1:4]
            for (t0, z0, x0, y0), (t1, z1, x1, y1) in zip(pts, pts[1:]):
                if lt < t1:
                    k = ease((lt - t0) / max(1e-6, t1 - t0), shot.get("ease", "inout")) if lt > t0 else 0.0
                    zoom, cx, cy = lerp(z0, z1, k), lerp(x0, x1, k), lerp(y0, y1, k)
                    break
        else:
            k = ease(lt / dur, shot.get("ease", "inout"))
            zoom, cx, cy = kf(shot.get("zoom", 1.0), k), kf(shot.get("cx", 0.5), k), kf(shot.get("cy", 0.5), k)
        for p in shot.get("punch", []):
            if lt >= p["at"] and lt < p.get("until", 1e9):
                u = ease((lt - p["at"]) / p.get("ramp", 0.16), "out")
                zoom = zoom * (1 + (p["zoom"] - 1) * u)
                cx = lerp(cx, p.get("cx", cx), u)
                cy = lerp(cy, p.get("cy", cy), u)
        return zoom, cx, cy

    def mapper(self, seg, lt, src_w, src_h):
        shot = seg["shot"]
        rx, ry, rw, rh = self.region(shot)
        zoom, cx, cy = self.cam(shot, lt)
        x, y, cw, ch = R.crop_rect(src_w, src_h, rw / rh, zoom, cx, cy)
        sx, sy = rw / cw, rh / ch
        return (lambda u, v: (rx + (u * src_w - x) * sx, ry + (v * src_h - y) * sy)), (x, y, cw, ch), (rx, ry, rw, rh)

    def frame(self, seg, lt, src):
        shot = seg["shot"]
        sh_, sw_ = src.shape[:2]
        to_out, rect, (rx, ry, rw, rh) = self.mapper(seg, lt, sw_, sh_)
        mode = shot.get("layout", self.mode)
        if mode == "blur":  # same clip, enlarged, blurred and darkened
            out = R.blurred_bg(src, darken=shot.get("darken", self.darken))
        elif mode == "meme":
            out = np.empty((H, W, 3), np.float32)
            out[:] = shot.get("bg", self.bg)
        else:
            out = np.zeros((H, W, 3), np.float32)
        vid = R.warp_crop(src, rect, rw, rh, interp=cv2.INTER_AREA if rect[2] > rw * 1.3 else cv2.INTER_CUBIC)
        g = shot.get("grade", {})
        vid = R.grade(vid.astype(np.float32), g.get("sat", 1.08), g.get("contrast", 1.05))
        vid = R.sharpen(np.clip(vid, 0, 255).astype(np.uint8), g.get("sharpen", 0.35)).astype(np.float32)
        if shot.get("bw"):
            vid = np.repeat((vid @ np.array([0.299, 0.587, 0.114], np.float32))[..., None], 3, axis=2)
        if shot.get("vid_darken"):  # e.g. 0.6 for the dark "skull edit" freeze
            vid *= shot["vid_darken"]
        if shot.get("vignette"):
            vid *= R_vignette(rw, rh, shot["vignette"])[..., None]
        wb = shot.get("whip_in", 0.0)  # motion blur that settles over the first `whip_in` seconds
        if wb and lt < wb:
            n = int(round(90 * (1 - ease(lt / wb, "out")))) // 2 * 2 + 1
            if n > 2:
                kern = np.zeros((n, n), np.float32)
                cv2.line(kern, (0, n - 1), (n - 1, 0), 1.0, 1)
                vid = cv2.filter2D(vid, -1, kern / kern.sum())
        fade = shot.get("fade_in", 0.0)
        if fade and lt < fade:
            vid *= lt / fade
        fo = shot.get("fade_out", 0.0)
        if fo and lt > shot["dur"] - fo:
            vid *= max(0.0, (shot["dur"] - lt) / fo)
        y0, y1 = max(0, ry), min(H, ry + rh)
        out[y0:y1, rx:rx + rw] = vid[y0 - ry:y1 - ry]
        return out, to_out

    def draw_marks(self, out, t, seg_idx, to_out):
        for m, art, tip in self.marks:
            if not (m["t"] <= t < m["t"] + m["d"]):
                continue
            if "shot" in m and m["shot"] != seg_idx:
                continue
            k = t - m["t"]
            if m["type"] == "progress":
                n, k_ = m.get("n", 10), m.get("k", 0)
                tw, hh, gap = m.get("w", 0.72) * W, m.get("h", 12), m.get("gap", 10)
                sw = (tw - gap * (n - 1)) / n
                x0, yc = (W - tw) / 2, m["y"] * H
                for i in range(n):
                    xs = x0 + i * (sw + gap)
                    col = tuple(m.get("fill", (255, 214, 10))) if i < k_ else tuple(m.get("empty", (70, 70, 70)))
                    cv2.rectangle(out, (int(xs), int(yc - hh / 2)), (int(xs + sw), int(yc + hh / 2)), col, -1)
                continue
            if m["type"] == "panel":
                shown = sum(1 for r in m["rows"] if r["t"] <= t)
                rgb, a = art[shown]
                h, w = rgb.shape[:2]
                op = min(1.0, k / 0.2)
                R.blit(out, rgb, a, m.get("x", 0.04) * W + w / 2, m.get("y", 0.6) * H + h / 2, opacity=op)
                continue
            if m["type"] == "dim":
                rx, ry, rw, rh = self.region(self.timeline[seg_idx]["shot"]) if m.get("region", "box") == "box" \
                    else (0, 0, W, H)
                amt = m.get("amount", 0.65) * min(1.0, k / m.get("ramp", 0.2))
                y0, y1 = max(0, ry), min(H, ry + rh)
                out[y0:y1, rx:rx + rw] *= (1 - amt)
                continue
            x, y = to_out(m["x"], m["y"]) if "shot" in m else (m["x"] * W, m["y"] * H)
            if m["type"] == "arrow":
                (rgb, a) = art
                s = 0.7 + 0.3 * ease(k / 0.1, "out")
                # place so the tip lands on (x, y)
                cx = x + (rgb.shape[1] / 2 - tip[0]) * s
                cy = y + (rgb.shape[0] / 2 - tip[1]) * s
                R.blit(out, rgb, a, cx, cy, scale=s, opacity=min(1.0, k / 0.05))
            else:
                self.circle(out, x, y, m.get("rx", 120), m.get("ry", 80), min(1.0, k / m.get("draw", 0.22)),
                            m.get("seed", 3), m.get("thick", 8))

    def circle(self, out, x, y, rx, ry, prog, seed=3, thick=8):
        rng = np.random.default_rng(seed)
        n = 90
        start = math.radians(205)
        sweep = math.radians(385) * prog
        ph = rng.uniform(0, 6.28, 3)
        pts = []
        for i in range(n + 1):
            a = start + sweep * i / n
            wob = 1 + 0.035 * math.sin(3 * a + ph[0]) + 0.025 * math.sin(5 * a + ph[1]) + 0.06 * (i / n)
            pts.append((x + rx * wob * math.cos(a), y + ry * wob * math.sin(a)))
        if len(pts) < 2:
            return
        layer = np.zeros((H, W), np.uint8)
        arr = np.array(pts, np.int32).reshape(-1, 1, 2)
        cv2.polylines(layer, [arr], False, 255, thick + 4, cv2.LINE_AA)
        dark = layer.astype(np.float32)[..., None] / 255 * 0.35
        out[:] = out * (1 - dark)
        layer[:] = 0
        cv2.polylines(layer, [arr], False, 255, thick, cv2.LINE_AA)
        a = layer.astype(np.float32)[..., None] / 255
        out[:] = out * (1 - a) + np.array(RED, np.float32) * a

    def draw_captions(self, out, t, seg, to_out):
        for c, (rgb, a) in self.caps:
            if not (c["t"] <= t < c["t"] + c["d"]):
                continue
            k = t - c["t"]
            s = 0.9 + 0.1 * ease(k / 0.08, "out") if c.get("anim", "pop") == "pop" else 1.0
            op = min(1.0, k / 0.05)
            if c["t"] <= 0.001:  # anything on screen at t=0 is fully visible on frame 1 (thumbnail)
                s, op = 1.0, 1.0
            tail = c["t"] + c["d"] - t
            if c.get("fade_out") and tail < c["fade_out"]:
                op *= tail / c["fade_out"]
            x, y = self.caption_pos(c, rgb.shape[0], seg, to_out)
            if c.get("anim") == "rise":  # flies up from below the screen and lands (skull edit emoji)
                u = min(1.0, k / c.get("rise", 0.45))
                y += (H - y + rgb.shape[0]) * (1 - ease(u, "out"))
                s, op = 1.0, 1.0
            R.blit(out, rgb, a, x, y, scale=s, opacity=op)

    def caption_pos(self, c, h, seg, to_out):
        style = c.get("style", "top")
        rx, ry, rw, rh = self.region(seg["shot"])
        if "shot" in c:  # pinned to the subject
            return to_out(c["x"], c["y"])
        x = c.get("x", 0.5) * W
        if "y" in c:
            return x, c["y"] * H
        if style == "meme":
            return x, ry - 26 - h / 2
        if style == "label":
            return x, (ry + 70 if seg["shot"].get("layout", self.mode) == "full" else ry - 26 - h / 2)
        if style in ("cap", "big", "cap_dela") or (style == "sub" and self.box_top is not None):
            return x, ry + rh + 26 + h / 2  # directly under the video box
        if style in ("title", "title_dela") and seg["shot"].get("layout", self.mode) != "full":
            return x, max(ry - 24 - h / 2, 90 + h / 2)  # just above the video box
        if style == "sub":
            return x, 0.74 * H
        if style == "chapter":
            return x, ry - 40 - h / 2 if seg["shot"].get("layout", self.mode) != "full" else 0.2 * H
        return x, 0.2 * H

    def render_video(self, out_path, only=None, stills=None):
        enc = None
        if only is None:
            enc = subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo",
                                    "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                    "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p",
                                    "-movflags", "+faststart", out_path], stdin=subprocess.PIPE)
        fi = 0
        for si, seg in enumerate(self.timeline):
            need = only is None or any(seg["i0"] <= f < seg["i0"] + seg["n"] for f in only)
            if not need:
                fi += seg["n"]
                continue
            stream = ShotStream(seg["shot"], seg["n"])
            for j in range(seg["n"]):
                src = stream.read()
                gi = seg["i0"] + j
                if only is not None and gi not in only:
                    continue
                t = gi / FPS
                lt = j / FPS
                out, to_out = self.frame(seg, lt, src)
                self.draw_marks(out, t, si, to_out)
                self.draw_captions(out, t, seg, to_out)
                img = np.clip(out, 0, 255).astype(np.uint8)
                if enc:
                    enc.stdin.write(img.tobytes())
                else:
                    cv2.imwrite(os.path.join(stills, f"{self.p['id']}_{gi:04d}.jpg"), img[..., ::-1],
                                [cv2.IMWRITE_JPEG_QUALITY, 88])
            stream.close()
            print(f"  shot {si + 1}/{len(self.timeline)} done", flush=True)
        if enc:
            enc.stdin.close()
            enc.wait()

    def render_audio(self, out_wav):
        n = int(round(self.total * SR))
        mix = np.zeros((n, 2), np.float32)
        for seg in self.timeline:
            s = seg["shot"]
            speed = float(s.get("speed", 1.0))
            if not s.get("audio", abs(speed - 1) < 1e-3):
                continue
            path = src_path(s["src"])
            src_dur = seg["n"] / FPS * speed
            af = f"atempo={speed:.4f}" if abs(speed - 1) > 1e-3 and s.get("audio_mode") == "tempo" else None
            if abs(speed - 1) > 1e-3 and not af:
                af = f"asetrate={int(SR * speed)},aresample={SR}"  # slowed tape: deeper and darker
            if s.get("af"):
                af = ",".join(x for x in (af, AF.get(s["af"], s["af"])) if x)
            cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", f"{s['in']:.3f}", "-t", f"{src_dur:.3f}",
                   "-i", path, "-vn", "-ac", "2", "-ar", str(SR)] + (["-af", af] if af else []) + \
                  ["-f", "f32le", "-"]
            a = np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.float32).reshape(-1, 2).copy()
            st = int(round(seg["t0"] * SR))
            ln = min(len(a), n - st, int(round(seg["n"] / FPS * SR)))
            if ln <= 0:
                continue
            a = a[:ln] * 10 ** (s.get("audio_db", 0.0) / 20)
            f = min(int(0.012 * SR), ln // 2)
            a[:f] *= np.linspace(0, 1, f)[:, None]
            a[-f:] *= np.linspace(1, 0, f)[:, None]
            if s.get("audio_fade_in"):
                fi = min(ln, int(s["audio_fade_in"] * SR))
                a[:fi] *= np.linspace(0, 1, fi)[:, None]
            if s.get("audio_fade_out"):
                fo = min(ln, int(s["audio_fade_out"] * SR))
                a[-fo:] *= np.linspace(1, 0, fo)[:, None]
            mix[st:st + ln] += a
        # audio lifted from a source and laid over other shots (e.g. a speech over B-roll)
        for c in self.p.get("audio_clips", []):
            path = src_path(c["src"])
            af = AF.get(c.get("af"), c.get("af"))
            cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", f"{c['in']:.3f}", "-t", f"{c['dur']:.3f}",
                   "-i", path, "-vn", "-ac", "2", "-ar", str(SR)] + (["-af", af] if af else []) + ["-f", "f32le", "-"]
            a = np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.float32).reshape(-1, 2).copy()
            st = int(round(c["t"] * SR))
            ln = min(len(a), n - st)
            if ln <= 0:
                continue
            a = a[:ln] * 10 ** (c.get("db", 0.0) / 20)
            f = min(int(c.get("fade", 0.03) * SR), ln // 2)
            a[:f] *= np.linspace(0, 1, f)[:, None]
            a[-f:] *= np.linspace(1, 0, f)[:, None]
            mix[st:st + ln] += a
        for cue in self.p.get("sfx", []):
            name = cue["name"]
            path = (os.path.join(ROOT, "assets", "sfx_mixkit", name[3:] + ".wav") if name.startswith("mk:")
                    else os.path.join(SFX_DIR, name + ".wav"))  # "mk:" = licensed Mixkit sound
            x, sr = sf.read(path, dtype="float32")
            if x.ndim == 1:
                x = np.stack([x, x], 1)
            st = int(cue["t"] * SR)
            if st < 0:
                x, st = x[-st:], 0
            ln = min(len(x), n - st)
            if ln > 0:
                mix[st:st + ln] += x[:ln] * 10 ** (cue.get("db", -8) / 20)
        meter = pyln.Meter(SR)
        target = self.p.get("lufs", -14.0)
        for _ in range(3):
            loud = meter.integrated_loudness(mix.astype(np.float64))
            if not np.isfinite(loud) or abs(loud - target) < 0.3:
                break
            mix = R.limiter(mix * 10 ** ((target - loud) / 20))
        sf.write(out_wav, R.limiter(mix), SR, subtype="PCM_16")

    def run(self, out_mp4):
        with tempfile.TemporaryDirectory() as td:
            v, a = os.path.join(td, "v.mp4"), os.path.join(td, "a.wav")
            self.render_video(v)
            self.render_audio(a)
            subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", v, "-i", a, "-c:v", "copy",
                            "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out_mp4], check=True)
        return out_mp4


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--out")
    ap.add_argument("--frames", help="comma separated frame numbers: write stills instead of a video")
    ap.add_argument("--stills", default=".")
    a = ap.parse_args()
    plan = json.load(open(a.plan))
    b = Bench(plan)
    if a.frames:
        os.makedirs(a.stills, exist_ok=True)
        b.render_video(None, only={int(x) for x in a.frames.split(",")}, stills=a.stills)
        return
    out = a.out or os.path.join(ROOT, "work", "renders", plan["id"] + ".mp4")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    print(f"rendering {plan['id']}: {b.total:.2f}s, {len(b.timeline)} shots", flush=True)
    b.run(out)
    print("done", out)


if __name__ == "__main__":
    main()
