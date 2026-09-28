"""RageStyles shorts renderer (v2): JSON edit plan -> finished 1080x1920 / 30 fps MP4.

Style ("post" layout): the short looks like a post on X / a community board.
  * header: round RageStyles avatar, name, verified badge, @handle
  * post text (the hook), then the clip in a rounded media card
  * clean cuts only; optional brief punch-in zoom, slow motion, black-and-white freeze
  * overlay captions with quick pop / slam, inline emoji and country flags
  * red rings / arrows on the key detail, live leaderboard, country flag row
  * real meme SFX from assets/sfx (no music: the channel adds music at upload)

Usage:  python3 render.py plans/01_xxx.json [--preview] [--out file.mp4]
"""
import argparse
import json
import math
import os
import subprocess
import sys
import tempfile
from io import BytesIO

import cairosvg
import cv2
import numpy as np
import pyloudnorm as pyln
import soundfile as sf
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS, SR = 1080, 1920, 30, 48000
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(ROOT, "assets")
FONT_DIR = os.path.join(ASSETS, "fonts")
SFX_DIR = os.path.join(ASSETS, "sfx")
FLAG_DIR = os.path.join(ASSETS, "flags")
BRAND_DIR = os.path.join(ASSETS, "brand")
CLIP_DIR = os.environ.get("RS_CLIPS", os.path.join(ROOT, "work", "clips"))
EMOJI_JSON = os.path.join(ASSETS, "emoji", "noto-icons.json")

FONTS = {
    "Montserrat Black": "Montserrat-Black.ttf",
    "Montserrat ExtraBold": "Montserrat-ExtraBold.ttf",
    "Inter": "Inter-Regular.ttf",
    "Inter SemiBold": "Inter-SemiBold.ttf",
    "Inter Bold": "Inter-Bold.ttf",
    "Inter ExtraBold": "Inter-ExtraBold.ttf",
    "Anton": "Anton-Regular.ttf",
}
COLORS = {"*": (255, 214, 10), "~": (255, 59, 48), "^": (52, 230, 110), "@": (29, 155, 240)}
INK = (15, 20, 25)
GRAY = (83, 100, 113)
BRAND = {"name": "RageStyles", "handle": "@Rage_Styles"}


# ------------------------------------------------------------------ helpers

def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, FONTS[name]), size)


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def ease_in_out(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def ffprobe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,r_frame_rate:format=duration", "-of", "json", path],
                         capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    s = d["streams"][0]
    num, den = s["r_frame_rate"].split("/")
    return {"w": int(s["width"]), "h": int(s["height"]), "fps": float(num) / float(den),
            "dur": float(d["format"]["duration"])}


def svg_to_image(svg_text, w, h):
    png = cairosvg.svg2png(bytestring=svg_text.encode(), output_width=w, output_height=h)
    return Image.open(BytesIO(png)).convert("RGBA")


def round_corners(img, radius):
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, img.width - 1, img.height - 1), radius=radius, fill=255)
    out = img.copy()
    out.putalpha(Image.fromarray(np.minimum(np.asarray(img.split()[3]), np.asarray(mask))))
    return out


# ------------------------------------------------------------------ emoji + flags

_EMOJI = None


def flag_image(code, h, radius=None, border=True):
    """Country flag (flag-icons, 4:3) with rounded corners, like an emoji flag."""
    w = int(round(h * 4 / 3))
    svg = open(os.path.join(FLAG_DIR, code + ".svg")).read()
    img = svg_to_image(svg, w, h)
    img = round_corners(img, radius if radius is not None else max(3, h // 7))
    if border:
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((0, 0, w - 1, h - 1), radius=radius if radius is not None else max(3, h // 7),
                            outline=(0, 0, 0, 60), width=max(1, h // 40))
    return img


def emoji_image(name, size):
    """Noto emoji by name, or ':flag-us:' style country flags, on a size x size canvas."""
    if name.startswith("flag-"):
        fh = int(size * 0.72)
        fl = flag_image(name[5:], fh)
        canvas = Image.new("RGBA", (max(size, fl.width), size), (0, 0, 0, 0))
        canvas.alpha_composite(fl, ((canvas.width - fl.width) // 2, (size - fh) // 2))
        return canvas
    global _EMOJI
    if _EMOJI is None:
        _EMOJI = json.load(open(EMOJI_JSON))
    icon = _EMOJI["icons"][name]
    w = icon.get("width", _EMOJI.get("width", 128))
    h = icon.get("height", _EMOJI.get("height", 128))
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">{icon["body"]}</svg>'
    return svg_to_image(svg, size, size)


# ------------------------------------------------------------------ text

def parse_tokens(text):
    """'Watch his *FACE* :skull:' -> lines of (word, color_key or None, is_emoji)."""
    lines = []
    for raw_line in text.split("\n"):
        toks = []
        active = None  # highlight spans may cover several words: *600 lbs*
        for word in raw_line.split(" "):
            if not word:
                continue
            if word.startswith(":") and word.endswith(":") and len(word) > 2:
                toks.append((word[1:-1], None, True))
                continue
            if active is None and word[0] in COLORS and len(word) > 1:
                active = word[0]
                word = word[1:]
            key = active
            stripped = word.rstrip(".,!?'\")")
            tail = word[len(stripped):]
            if active and stripped.endswith(active):
                word = stripped[:-1] + tail
                active = None
            toks.append((word, key, False))
        lines.append(toks)
    return lines


def token_width(tok, fnt, emoji_px):
    if tok[2]:
        return int(emoji_px * 4 / 3 * 0.72) + 4 if tok[0].startswith("flag-") else emoji_px
    return fnt.getlength(tok[0])


def wrap_tokens(lines, fnt, max_w, emoji_px):
    space = fnt.getlength(" ")
    out = []
    for toks in lines:
        cur, cur_w = [], 0
        for tok in toks:
            tw = token_width(tok, fnt, emoji_px)
            add = tw + (space if cur else 0)
            if cur and cur_w + add > max_w:
                out.append(cur)
                cur, cur_w = [tok], tw
            else:
                cur.append(tok)
                cur_w += add
        if cur:
            out.append(cur)
    return out


def render_text(text, font_name="Montserrat Black", size=80, color=(255, 255, 255), stroke=9,
                max_w=900, line_gap=0.08, shadow=True, upper=True, align="center", max_lines=2,
                min_size=40, stroke_color=(0, 0, 0), balance=True, emoji_scale=1.05):
    """RGBA image of a caption, tight bbox. Shrinks the font until it fits max_lines."""
    if upper:
        text = "\n".join(" ".join(w if (w.startswith(":") and w.endswith(":")) else w.upper()
                                  for w in ln.split(" ")) for ln in text.split("\n"))
    base_size, base_stroke = size, stroke
    tokens = parse_tokens(text)
    explicit = text.count("\n") + 1
    while True:
        fnt = font(font_name, size)
        emoji_px = int(size * emoji_scale)
        lines = wrap_tokens(tokens, fnt, max_w, emoji_px)
        if len(lines) <= max(max_lines, explicit) or size <= min_size:
            break
        size = int(size * 0.93)
    if balance and len(lines) == 2 and explicit == 1:
        small = int(size * 0.86)
        f2 = font(font_name, small)
        if len(wrap_tokens(tokens, f2, max_w, int(small * emoji_scale))) == 1:
            size, fnt, emoji_px = small, f2, int(small * emoji_scale)
            lines = wrap_tokens(tokens, fnt, max_w, emoji_px)
    if balance and len(lines) > explicit:
        lo, hi = 50, max_w
        while hi - lo > 4:
            mid = (lo + hi) // 2
            if len(wrap_tokens(tokens, fnt, mid, emoji_px)) <= len(lines):
                hi = mid
            else:
                lo = mid
        lines = wrap_tokens(tokens, fnt, hi, emoji_px)
    stroke = max(0, int(round(base_stroke * size / base_size))) if base_stroke else 0
    asc, desc = fnt.getmetrics()
    lh = int((asc + desc) * (1 + line_gap))
    space = fnt.getlength(" ")
    widths = [sum(token_width(t, fnt, emoji_px) for t in ln) + space * (len(ln) - 1) for ln in lines]
    tw = int(max(widths) if widths else 10)
    m = stroke + 24
    img = Image.new("RGBA", (tw + 2 * m, lh * len(lines) + 2 * m), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    emojis = []
    for i, ln in enumerate(lines):
        x = m + ((tw - widths[i]) / 2 if align == "center" else 0)
        y = m + i * lh
        for word, key, is_emoji in ln:
            if is_emoji:
                ey = int(y + (asc + desc - emoji_px) * 0.5)
                emojis.append((int(x), ey, word))
                x += token_width((word, None, True), fnt, emoji_px) + space
                continue
            col = COLORS[key] if key else color
            if stroke:
                d.text((x, y), word, font=fnt, fill=col + (255,), stroke_width=stroke, stroke_fill=stroke_color + (255,))
            else:
                d.text((x, y), word, font=fnt, fill=col + (255,))
            x += fnt.getlength(word) + space
    for ex, ey, name in emojis:
        try:
            img.alpha_composite(emoji_image(name, emoji_px), (ex, max(0, ey)))
        except (KeyError, FileNotFoundError):
            print("  ! unknown emoji", name, file=sys.stderr)
    if shadow:
        a = img.split()[3]
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        sh.putalpha(a.point(lambda v: int(v * 0.5)))
        sh = sh.filter(ImageFilter.GaussianBlur(6))
        base = Image.new("RGBA", (img.width, img.height + 6), (0, 0, 0, 0))
        base.alpha_composite(sh, (0, 6))
        base.alpha_composite(img, (0, 0))
        img = base
    bbox = img.getbbox()
    return img.crop(bbox) if bbox else img


def to_np_rgba(img):
    a = np.asarray(img).astype(np.float32)
    return a[..., :3], a[..., 3:4] / 255.0


def blit(frame, rgb, alpha, cx, cy, scale=1.0, opacity=1.0):
    """Alpha-composite (float arrays) centred at (cx, cy) onto a float32 HxWx3 frame."""
    if scale <= 0.01 or opacity <= 0.005:
        return
    if abs(scale - 1.0) > 1e-3:
        h, w = rgb.shape[:2]
        nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
        rgb = cv2.resize(rgb, (nw, nh), interpolation=cv2.INTER_LINEAR)
        alpha = cv2.resize(alpha, (nw, nh), interpolation=cv2.INTER_LINEAR)[..., None]
    h, w = rgb.shape[:2]
    fh, fw = frame.shape[:2]
    x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    fx0, fy0, fx1, fy1 = max(0, x0), max(0, y0), min(fw, x0 + w), min(fh, y0 + h)
    if fx1 <= fx0 or fy1 <= fy0:
        return
    sx0, sy0 = fx0 - x0, fy0 - y0
    a = alpha[sy0:sy0 + fy1 - fy0, sx0:sx0 + fx1 - fx0] * opacity
    frame[fy0:fy1, fx0:fx1] = frame[fy0:fy1, fx0:fx1] * (1 - a) + rgb[sy0:sy0 + fy1 - fy0, sx0:sx0 + fx1 - fx0] * a


# ------------------------------------------------------------------ source video

def display_size(path, rotate=0):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,sample_aspect_ratio", "-of", "json", path],
                         capture_output=True, text=True, check=True).stdout
    s = json.loads(out)["streams"][0]
    w, h = int(s["width"]), int(s["height"])
    sar = s.get("sample_aspect_ratio", "1:1")
    if sar and ":" in sar and sar not in ("0:1", "N/A"):
        a, b = (int(x) for x in sar.split(":"))
        if a and b:
            w = int(round(w * a / b))
    w, h = w // 2 * 2, h // 2 * 2
    if rotate in (90, -90, 270):
        w, h = h, w
    return w, h


def decode_segment(seg):
    """RGB uint8 frames of a segment at the output rate (speed already applied)."""
    path = os.path.join(CLIP_DIR, seg["clip"] + ".mp4")
    info = ffprobe(path)
    speed = float(seg.get("speed", 1.0))
    t_in, t_out = float(seg["in"]), float(seg["out"])
    src_dur = max(0.05, t_out - t_in)
    n_out = max(1, int(round(src_dur / speed * FPS)))
    rot = seg.get("rotate", 0)
    dw, dh = display_size(path, rot)
    filters = []
    if seg.get("denoise"):
        filters.append("hqdn3d=2.5:2.5:4:4")
    if rot == 90:
        filters.append("transpose=1")
    elif rot in (-90, 270):
        filters.append("transpose=2")
    elif rot == 180:
        filters.append("hflip,vflip")
    filters.append(f"scale={dw}:{dh},setsar=1")
    if speed < 0.999:
        target = FPS / speed
        if seg.get("interp", "mci") == "mci":
            filters.append(f"minterpolate=fps={target:.3f}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1")
        else:
            filters.append(f"framerate=fps={target:.3f}")
    elif speed > 1.001:
        filters.append(f"setpts=PTS/{speed:.4f},fps={FPS}")
    else:
        filters.append(f"framerate=fps={FPS}" if abs(info["fps"] - FPS) > 0.5 else f"fps={FPS}")
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", f"{max(0, t_in - 1.0):.3f}", "-i", path,
           "-ss", f"{min(1.0, t_in):.3f}", "-t", f"{src_dur + 0.25:.3f}", "-vf", ",".join(filters),
           "-an", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    frames = np.frombuffer(raw, np.uint8)
    frames = frames[: len(frames) // (dw * dh * 3) * dw * dh * 3].reshape(-1, dh, dw, 3)
    if len(frames) == 0:
        raise RuntimeError(f"no frames decoded for {seg}")
    if len(frames) >= n_out:
        return [frames[i] for i in range(n_out)]
    idx = np.clip(np.round(np.linspace(0, len(frames) - 1, n_out)).astype(int), 0, len(frames) - 1)
    return [frames[i] for i in idx]


def auto_levels(frames, strength=1.0):
    sample = np.stack(frames[:: max(1, len(frames) // 12)]).astype(np.float32)
    lum = sample.mean(axis=3)
    lo, hi = np.percentile(lum, 1.0) * strength, 255 - (255 - np.percentile(lum, 99.3)) * strength
    if hi - lo < 40:
        return lambda f: f
    scale = 245.0 / (hi - lo)
    return lambda f: np.clip((f - lo) * scale + 6, 0, 255)


def grade(f, sat=1.1, contrast=1.05):
    mean = f.mean(axis=2, keepdims=True)
    f = mean + (f - mean) * sat
    return np.clip((f - 128.0) * contrast + 128.0, 0, 255)


def sharpen(img_u8, amount=0.5, radius=1.6):
    blur = cv2.GaussianBlur(img_u8, (0, 0), radius)
    return cv2.addWeighted(img_u8, 1 + amount, blur, -amount, 0)


def crop_rect(src_w, src_h, out_aspect, zoom, fx, fy):
    """Largest out_aspect rect inside src, zoomed by `zoom` around focus (fx, fy) in [0,1]."""
    if src_w / src_h > out_aspect:
        ch, cw = src_h, src_h * out_aspect
    else:
        cw, ch = src_w, src_w / out_aspect
    cw /= zoom
    ch /= zoom
    cx = min(max(fx * src_w, cw / 2), src_w - cw / 2)
    cy = min(max(fy * src_h, ch / 2), src_h - ch / 2)
    return cx - cw / 2, cy - ch / 2, cw, ch


def warp_crop(src, rect, out_w, out_h):
    x, y, cw, ch = rect
    sx, sy = out_w / cw, out_h / ch
    M = np.array([[sx, 0, -x * sx], [0, sy, -y * sy]], dtype=np.float32)
    return cv2.warpAffine(src, M, (out_w, out_h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)


def limiter(x, ceiling=0.84, lookahead=0.005, release=0.12):
    """Brick-wall look-ahead limiter on a (n, 2) float array."""
    from scipy.ndimage import minimum_filter1d
    peak = np.max(np.abs(x), axis=1)
    g = np.minimum(1.0, ceiling / np.maximum(peak, 1e-9))
    g = minimum_filter1d(g, size=2 * max(1, int(lookahead * SR)) + 1)
    rel = math.exp(-1.0 / (release * SR))
    out = np.empty_like(g)
    cur = 1.0
    for i in range(len(g)):
        gi = g[i]
        cur = gi if gi < cur else gi + (cur - gi) * rel
        out[i] = cur
    return (x * out[:, None]).astype(np.float32)


# ------------------------------------------------------------------ renderer

class Renderer:
    def __init__(self, plan, preview=False):
        self.p = plan
        self.preview = preview
        self.M = 36
        self.media_w = W - 2 * self.M
        self.media_h = int(round(self.media_w / plan.get("media_aspect", 4 / 3)))
        self.radius = 30

    # ---------- timeline
    def build_timeline(self):
        segs, t = [], 0.0
        for seg in self.p["segments"]:
            frames = decode_segment(seg)
            play = len(frames) / FPS
            fdur = seg["freeze"]["dur"] if seg.get("freeze") else 0.0
            segs.append({"seg": seg, "frames": frames, "t0": t, "dur": play + fdur, "play": play})
            t += play + fdur
        self.timeline, self.total = segs, t
        return t

    def seg_time(self, ref):
        """Resolve {"seg": i, "at": x} (or a plain number) to seconds."""
        if isinstance(ref, (int, float)):
            return float(ref)
        s = self.timeline[ref["seg"]]
        at = ref.get("at", 0.0)
        if at == "end":
            return s["t0"] + s["dur"]
        if at == "play_end":
            return s["t0"] + s["play"]
        return s["t0"] + at

    def resolve_times(self):
        for key in ("captions", "sfx", "stickers"):
            for c in self.p.get(key, []):
                if "seg" not in c:
                    continue
                s = self.timeline[c["seg"]]
                c["t"] = round(self.seg_time(c), 3)
                if key != "sfx":
                    if "d" not in c:
                        c["d"] = round(s["t0"] + s["dur"] - c["t"], 3)
                    elif c["d"] == "seg+":
                        s2 = self.timeline[min(c["seg"] + 1, len(self.timeline) - 1)]
                        c["d"] = round(s2["t0"] + s2["dur"] - c["t"], 3)
                    elif c["d"] == "end":
                        c["d"] = round(self.total - c["t"], 3)
        lb = self.p.get("leaderboard")
        if lb:
            for r in lb["rows"]:
                r["t"] = self.seg_time(r)
            lb["rows"].sort(key=lambda r: r["t"])
        fr = self.p.get("flag_row")
        if fr:
            for e in fr.get("events", []):
                e["t"] = self.seg_time(e)

    # ---------- static card
    def avatar_image(self, d):
        for name in ("avatar.png", "avatar.jpg", "avatar.jpeg", "avatar.webp"):
            path = os.path.join(BRAND_DIR, name)
            if os.path.exists(path):
                im = Image.open(path).convert("RGBA")
                s = min(im.size)
                im = im.crop(((im.width - s) // 2, (im.height - s) // 2, (im.width + s) // 2, (im.height + s) // 2))
                im = im.resize((d, d), Image.LANCZOS)
                break
        else:  # placeholder monogram until the real channel avatar is added
            im = Image.new("RGBA", (d, d), (0, 0, 0, 255))
            dr = ImageDraw.Draw(im)
            for r in range(d // 2, 0, -1):
                c = int(40 + 150 * (r / (d / 2)))
                dr.ellipse((d / 2 - r, d / 2 - r, d / 2 + r, d / 2 + r), fill=(c, 20, 25, 255))
            f = font("Montserrat Black", int(d * 0.38))
            tw = f.getlength("RS")
            dr.text(((d - tw) / 2, d * 0.27), "RS", font=f, fill=(255, 255, 255, 255))
        mask = Image.new("L", (d, d), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, d - 1, d - 1), fill=255)
        im.putalpha(mask)
        return im

    def prepare_static(self):
        p = self.p
        M = self.M
        post = p.get("post", {})
        text_img = render_text(post.get("text", ""), post.get("font", "Inter Bold"), post.get("size", 64),
                               color=INK, stroke=0, max_w=self.media_w, shadow=False, upper=False,
                               align="left", max_lines=post.get("max_lines", 3), balance=False,
                               line_gap=0.12, emoji_scale=1.0)
        av = 124
        flag_row_h = 150 if p.get("flag_row") else 0
        block = av + 26 + text_img.height + 26 + self.media_h + flag_row_h
        y0 = int(max(150, p.get("center_y", 930) - block / 2))
        img = Image.new("RGBA", (W, H), (255, 255, 255, 255))
        img.alpha_composite(self.avatar_image(av), (M, y0))
        nf = font("Inter ExtraBold", 52)
        d = ImageDraw.Draw(img)
        nx, ny = M + av + 26, y0 + 8
        d.text((nx, ny), BRAND["name"], font=nf, fill=INK + (255,))
        badge = svg_to_image(open(os.path.join(BRAND_DIR, "verified.svg")).read(), 52, 52)
        img.alpha_composite(badge, (int(nx + nf.getlength(BRAND["name"]) + 10), ny + 6))
        d.text((nx, ny + 64), BRAND["handle"], font=font("Inter", 42), fill=GRAY + (255,))
        ty = y0 + av + 26
        img.alpha_composite(text_img, (M - 24, ty - 24 + 6))
        self.media_y = ty + text_img.height + 26 - 30
        self.media_x = M
        # media card border
        d.rounded_rectangle((M - 2, self.media_y - 2, M + self.media_w + 1, self.media_y + self.media_h + 1),
                            radius=self.radius + 2, outline=(207, 217, 222, 255), width=2)
        self.flag_row_y = self.media_y + self.media_h + 92
        self.static = np.asarray(img.convert("RGB")).astype(np.float32)
        mask = Image.new("L", (self.media_w, self.media_h), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, self.media_w - 1, self.media_h - 1), radius=self.radius, fill=255)
        self.media_mask = (np.asarray(mask).astype(np.float32) / 255.0)[..., None]

    # ---------- overlays
    def prepare_overlays(self):
        self.captions = []
        for c in self.p.get("captions", []):
            style = c.get("style", "overlay")
            if style == "big":
                img = render_text(c["text"], c.get("font", "Montserrat Black"), c.get("size", 124),
                                  stroke=c.get("stroke", 12), max_w=c.get("max_w", 900), max_lines=2)
            else:
                img = render_text(c["text"], c.get("font", "Montserrat Black"), c.get("size", 70),
                                  stroke=c.get("stroke", 9), max_w=c.get("max_w", 880),
                                  max_lines=c.get("max_lines", 2), upper=c.get("upper", True))
            self.captions.append((c, to_np_rgba(img)))
        lb = self.p.get("leaderboard")
        if lb:
            self.lb_row_h = 62
            self.lb_rows = {}
            for r in lb["rows"]:
                for hl in (False, True):
                    self.lb_rows[(id(r), hl)] = to_np_rgba(self.leaderboard_row(r, hl))
            self.lb_rank = [to_np_rgba(render_text(f"{i + 1}.", "Inter ExtraBold", 36, stroke=0, shadow=False,
                                                   upper=False, max_lines=1, balance=False))
                            for i in range(len(lb["rows"]))]
            self.lb_title = to_np_rgba(render_text(lb.get("title", "LEADERBOARD"), "Inter ExtraBold", 26,
                                                   color=(255, 214, 10), stroke=0, shadow=False, max_lines=1,
                                                   balance=False))
        fr = self.p.get("flag_row")
        if fr:
            self.flag_imgs = [to_np_rgba(flag_image(c, 78)) for c in fr["flags"]]
            self.check_img = to_np_rgba(emoji_image("check-mark-button", 40))
            self.cross_img = to_np_rgba(emoji_image("cross-mark", 40))

    def leaderboard_row(self, r, highlight):
        fh = 36
        fl = flag_image(r["flag"], fh)
        lf = font("Inter ExtraBold", 36)
        label, value = r.get("label", ""), f'{r["value"]:g} {r.get("unit", "KG")}'
        w = 300
        img = Image.new("RGBA", (w, self.lb_row_h), (0, 0, 0, 0))
        img.alpha_composite(fl, (0, (self.lb_row_h - fh) // 2))
        d = ImageDraw.Draw(img)
        d.text((fl.width + 14, 10), label, font=lf, fill=(255, 255, 255, 255))
        vc = (255, 214, 10, 255) if highlight else (255, 255, 255, 255)
        d.text((w - lf.getlength(value), 10), value, font=lf, fill=vc)
        return img

    def media_pt(self, x, y):
        return self.media_x + x * self.media_w, self.media_y + y * self.media_h

    def draw_leaderboard(self, frame, t):
        lb = self.p["leaderboard"]
        rows = lb["rows"]
        shown = [r for r in rows if r["t"] <= t]
        if not shown:
            return
        k = len(shown) - 1
        t_evt = shown[-1]["t"]
        after = sorted(shown, key=lambda r: -r["value"])
        before = sorted(shown[:-1], key=lambda r: -r["value"])
        prog = ease_in_out((t - t_evt - 0.35) / 0.45)  # entry appears, then climbs to its rank
        x0, y0 = self.media_pt(*lb.get("pos", (0.025, 0.035)))
        rh = self.lb_row_h
        pad = 18
        n_after = len(after)
        n_before = max(1, len(before))
        n_rows = n_before + (n_after - n_before) * min(1.0, ease_out((t - t_evt) / 0.25)) if before else n_after
        pw, ph = 420, int(pad * 2 + 34 + rh * n_rows)
        panel = frame[int(y0):int(y0 + ph), int(x0):int(x0 + pw)]
        if panel.size:
            ov = np.zeros((ph, pw), np.uint8)
            cv2.rectangle(ov, (0, 0), (pw - 1, ph - 1), 255, -1)
            m = cv2.GaussianBlur(ov.astype(np.float32) / 255.0, (0, 0), 1.2)[: panel.shape[0], : panel.shape[1], None]
            panel[:] = panel * (1 - 0.62 * m)
        rgb, a = self.lb_title
        blit(frame, rgb, a, x0 + pad + rgb.shape[1] / 2, y0 + pad + 12)
        base_y = y0 + pad + 34
        for i in range(n_after):
            rgb, a = self.lb_rank[i]
            blit(frame, rgb, a, x0 + pad + 22, base_y + i * rh + rh / 2)
        new = shown[-1]
        for r in after:
            ra = after.index(r)
            if r is new:
                if before:
                    rb = len(before)  # enters at the bottom, then climbs
                    slot = rb + (ra - rb) * prog
                else:
                    slot = ra
                op = min(1.0, (t - t_evt) / 0.2)
            else:
                rb = before.index(r)
                slot = rb + (ra - rb) * prog
                op = 1.0
            hl = (r is new) and (t - t_evt < 2.0)
            rgb, a = self.lb_rows[(id(r), hl)]
            blit(frame, rgb, a, x0 + pad + 58 + rgb.shape[1] / 2, base_y + slot * rh + rh / 2, opacity=op)

    def draw_flag_row(self, frame, t):
        fr = self.p["flag_row"]
        n = len(fr["flags"])
        active, marks = None, {}
        for e in fr.get("events", []):
            if e["t"] <= t:
                if e.get("type", "active") == "active":
                    active = e["idx"]
                else:
                    marks[e["idx"]] = (e["type"], e["t"])
        fw = self.flag_imgs[0][0].shape[1]
        gap = 34
        total = n * fw + (n - 1) * gap
        x = W / 2 - total / 2 + fw / 2
        y = self.flag_row_y
        for i in range(n):
            rgb, a = self.flag_imgs[i]
            is_act = (i == active)
            s = 1.22 if is_act else 1.0
            op = 1.0 if is_act or i in marks else 0.4
            blit(frame, rgb, a, x, y, scale=s, opacity=op)
            if is_act:
                cv2.rectangle(frame, (int(x - fw * 0.5), int(y + 62)), (int(x + fw * 0.5), int(y + 69)),
                              (29, 155, 240), -1)
            if i in marks:
                kind, tm = marks[i]
                im = self.check_img if kind == "check" else self.cross_img
                sc = 1.0 + 0.4 * (1 - ease_out((t - tm) / 0.18))
                blit(frame, im[0], im[1], x + fw * 0.42, y + 30, scale=sc)
            x += fw + gap

    def draw_stickers(self, frame, t):
        for s in self.p.get("stickers", []):
            t0, d = s["t"], s.get("d", 1.2)
            if not (t0 <= t < t0 + d):
                continue
            k = t - t0
            grow = ease_out(k / 0.15)
            x, y = self.media_pt(s.get("x", 0.5), s.get("y", 0.5))
            col = hex_rgb(s.get("color", "#FF1E1E"))
            if s["type"] == "ring":
                rx, ry = s.get("rx", 110) * grow, s.get("ry", s.get("rx", 110) * 0.8) * grow
                cv2.ellipse(frame, (int(x), int(y)), (max(1, int(rx)), max(1, int(ry))), s.get("rot", -8), 0, 360,
                            col, s.get("th", 9), cv2.LINE_AA)
            elif s["type"] == "arrow":
                ang = math.radians(s.get("angle", 225))
                length = s.get("len", 170) * grow
                gap = s.get("gap", 24)
                x1, y1 = x + math.cos(ang) * gap, y - math.sin(ang) * gap
                x0, y0 = x1 + math.cos(ang) * length, y1 - math.sin(ang) * length
                cv2.arrowedLine(frame, (int(x0), int(y0)), (int(x1), int(y1)), col, s.get("th", 16), cv2.LINE_AA,
                                tipLength=0.38)

    def caption_center(self, c, h):
        pos = c.get("pos", "bottom")
        mx, my, mw, mh = self.media_x, self.media_y, self.media_w, self.media_h
        if isinstance(pos, (list, tuple)):
            return self.media_pt(*pos)
        return {"bottom": (W / 2, my + mh - 30 - h / 2), "center": (W / 2, my + mh / 2),
                "top": (W / 2, my + 30 + h / 2), "below": (W / 2, my + mh + 30 + h / 2)}[pos]

    def draw_captions(self, frame, t):
        for c, (rgb, a) in self.captions:
            t0, d = c["t"], c.get("d", 1.5)
            if not (t0 <= t < t0 + d):
                continue
            k = t - t0
            anim = c.get("anim", "pop")
            s, op = 1.0, 1.0
            if anim == "pop":
                s = 1.12 - 0.12 * ease_out(k / 0.1)
                op = min(1.0, k / 0.05)
            elif anim == "slam":
                s = 1.45 - 0.45 * ease_out(k / 0.12)
                op = min(1.0, k / 0.04)
            cx, cy = self.caption_center(c, rgb.shape[0])
            blit(frame, rgb, a, cx, cy, scale=s, opacity=op)

    # ---------- video
    def render_video(self, out_video):
        n_total = int(round(self.total * FPS))
        levels = [auto_levels(s["frames"], s["seg"].get("levels", 1.0)) if s["seg"].get("auto_levels", True)
                  else (lambda f: f) for s in self.timeline]
        enc = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
               "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264",
               "-preset", "veryfast" if self.preview else "slow", "-crf", "24" if self.preview else "17",
               "-pix_fmt", "yuv420p", "-profile:v", "high", "-movflags", "+faststart", out_video]
        proc = subprocess.Popen(enc, stdin=subprocess.PIPE)
        mw, mh = self.media_w, self.media_h
        for i in range(n_total):
            t = i / FPS
            sgi = next((j for j, s in enumerate(self.timeline) if s["t0"] <= t < s["t0"] + s["dur"]),
                       len(self.timeline) - 1)
            s = self.timeline[sgi]
            seg = s["seg"]
            lt = t - s["t0"]
            frames = s["frames"]
            src = frames[min(int(lt * FPS), len(frames) - 1)]
            frozen = lt >= s["play"]
            z0, z1 = seg.get("zoom", [1.0, 1.0])
            prog = ease_in_out(lt / max(0.01, s["play"]))
            zoom = z0 + (z1 - z0) * prog
            for fx in seg.get("fx", []):
                if fx["type"] == "punch" and fx.get("at", 0) <= lt < fx.get("at", 0) + fx.get("dur", 0.4):
                    x = (lt - fx.get("at", 0)) / fx.get("dur", 0.4)
                    e = ease_out(x / 0.2) if x < 0.2 else (1.0 if x < 0.6 else 1 - ease_in_out((x - 0.6) / 0.4))
                    zoom += fx.get("amount", 0.15) * e
            fz = seg.get("freeze") or {}
            if frozen and fz.get("zoom"):
                zoom += fz["zoom"] * ease_out((lt - s["play"]) / 0.35)
            fx0, fy0 = seg.get("focus", [0.5, 0.5])
            if "focus_to" in seg:
                fx0 += (seg["focus_to"][0] - fx0) * prog
                fy0 += (seg["focus_to"][1] - fy0) * prog
            sh, sw = src.shape[:2]
            rect = crop_rect(sw, sh, mw / mh, max(zoom, 1.0), fx0, fy0)
            vid = warp_crop(src, rect, mw, mh).astype(np.float32)
            vid = grade(levels[sgi](vid), seg.get("sat", 1.1), seg.get("contrast", 1.05))
            if (frozen and fz.get("bw")) or seg.get("bw"):
                g = vid @ np.array([0.299, 0.587, 0.114], np.float32)
                vid = np.repeat(g[..., None], 3, axis=2)
            vid = sharpen(np.clip(vid, 0, 255).astype(np.uint8), seg.get("sharpen", 0.5)).astype(np.float32)
            frame = self.static.copy()
            region = frame[self.media_y:self.media_y + mh, self.media_x:self.media_x + mw]
            region[:] = region * (1 - self.media_mask) + vid * self.media_mask
            self.draw_stickers(frame, t)
            if self.p.get("leaderboard"):
                self.draw_leaderboard(frame, t)
            if self.p.get("flag_row"):
                self.draw_flag_row(frame, t)
            self.draw_captions(frame, t)
            proc.stdin.write(np.clip(frame, 0, 255).astype(np.uint8).tobytes())
            if i % 90 == 0:
                print(f"  frame {i}/{n_total}", flush=True)
        proc.stdin.close()
        proc.wait()
        if proc.returncode:
            raise RuntimeError("encoder failed")

    # ---------- audio: real SFX only (music is added on YouTube at upload)
    def render_audio(self, out_wav):
        n = int(round(self.total * SR)) + SR // 10
        mix = np.zeros((n, 2), np.float32)
        for cue in self.p.get("sfx", []):
            x, sr = sf.read(os.path.join(SFX_DIR, cue["name"] + ".wav"), dtype="float32")
            if x.ndim == 1:
                x = np.stack([x, x], 1)
            if "max" in cue:
                x = x[: int(cue["max"] * SR)]
                f = min(len(x), int(0.05 * SR))
                x[-f:] *= np.linspace(1, 0, f)[:, None]
            st = int(cue["t"] * SR)
            if st >= n:
                continue
            ln = min(len(x), n - st)
            mix[st:st + ln] += x[:ln] * 10 ** (cue.get("db", -6) / 20)
        meter = pyln.Meter(SR)
        target = self.p.get("lufs", -16.0)
        if np.max(np.abs(mix)) > 0:
            for _ in range(3):
                loud = meter.integrated_loudness(mix.astype(np.float64))
                if not np.isfinite(loud) or abs(loud - target) < 0.3:
                    break
                mix = limiter(mix * 10 ** ((target - loud) / 20))
        sf.write(out_wav, mix[: int(round(self.total * SR))], SR, subtype="PCM_16")

    def run(self, out_mp4):
        total = self.build_timeline()
        self.resolve_times()
        self.prepare_static()
        self.prepare_overlays()
        print(f"  timeline {total:.2f}s, {len(self.timeline)} segments", flush=True)
        with tempfile.TemporaryDirectory() as td:
            v, a = os.path.join(td, "v.mp4"), os.path.join(td, "a.wav")
            self.render_video(v)
            self.render_audio(a)
            subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", v, "-i", a,
                            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest",
                            "-movflags", "+faststart", out_mp4], check=True)
        return out_mp4


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--out")
    ap.add_argument("--preview", action="store_true")
    args = ap.parse_args()
    plan = json.load(open(args.plan))
    out = args.out or os.path.join(ROOT, "work", "renders", plan["id"] + ".mp4")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    print("rendering", plan["id"])
    Renderer(plan, preview=args.preview).run(out)
    print("done", out)


if __name__ == "__main__":
    main()
