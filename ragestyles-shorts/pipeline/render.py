"""RageStyles shorts renderer: JSON edit plan -> finished 1080x1920 / 30 fps MP4.

Everything CapCut does for this format is reproduced in code so it runs headless:
  * 9:16 reframe: video band + blurred background (landscape) or full-bleed crop (portrait)
  * Ken Burns zoom, punch-in zoom, freeze frame, slow motion (motion-interpolated); no camera shake
  * transitions: flash, whip pan, zoom blur (glitch is treated as a clean cut)
  * pop-in captions with highlighted words and inline emoji, fixed hook title, stickers (ring, arrow, pill)
  * SFX cues, source audio (tape-style pitch on speed ramps); the music bed is only a loudness
    reference now, so effects keep their v1 levels while the output carries no background music
  * live leaderboard + country flag row for competitions (ranking concept)
  * loudness normalised to -14 LUFS, x264 + AAC, +faststart

Usage:  python3 render.py plans/01_xxx.json [--preview]
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
FONT_DIR = os.path.join(ROOT, "assets", "fonts")
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
MUSIC_DIR = os.environ.get("RS_MUSIC_REF", os.path.join(ROOT, "work", "music_ref"))  # loudness reference only
FLAG_DIR = os.path.join(ROOT, "assets", "flags")
CLIP_DIR = os.environ.get("RS_CLIPS", os.path.join(ROOT, "work", "clips"))
EMOJI_JSON = os.environ.get("RS_EMOJI_JSON", os.path.join(ROOT, "assets", "emoji", "noto-icons.json"))

FONTS = {
    "Montserrat Black": "Montserrat-Black.ttf",
    "Montserrat ExtraBold": "Montserrat-ExtraBold.ttf",
    "Anton": "Anton-Regular.ttf",
    "Bebas Neue": "BebasNeue-Regular.ttf",
    "Archivo Black": "ArchivoBlack-Regular.ttf",
    "Luckiest Guy": "LuckiestGuy-Regular.ttf",
    "Bangers": "Bangers-Regular.ttf",
    "Poppins Black": "Poppins-Black.ttf",
    "Poppins ExtraBold": "Poppins-ExtraBold.ttf",
}
COLORS = {"*": (255, 214, 10), "~": (255, 59, 48), "^": (52, 230, 110), "white": (255, 255, 255)}


# ------------------------------------------------------------------ helpers

def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, FONTS[name]), size)


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def ease_out_back(x, s=1.9):
    x = min(max(x, 0.0), 1.0) - 1
    return x * x * ((s + 1) * x + s) + 1


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def ffprobe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,r_frame_rate,sample_aspect_ratio:format=duration",
                          "-of", "json", path], capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    s = d["streams"][0]
    num, den = s["r_frame_rate"].split("/")
    return {"w": int(s["width"]), "h": int(s["height"]), "fps": float(num) / float(den),
            "dur": float(d["format"]["duration"])}


def has_audio(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
                          "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip()
    return bool(out)


# ------------------------------------------------------------------ emoji

_EMOJI = None


def flag_image(code, h, border=True):
    """Country flag (flag-icons 4:3 SVG) with rounded corners, like an emoji flag."""
    w = int(round(h * 4 / 3))
    svg = open(os.path.join(FLAG_DIR, code + ".svg")).read()
    img = Image.open(BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=w, output_height=h))).convert("RGBA")
    r = max(3, h // 7)
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, h - 1), radius=r, fill=255)
    img.putalpha(Image.fromarray(np.minimum(np.asarray(img.split()[3]), np.asarray(mask))))
    if border:
        ImageDraw.Draw(img).rounded_rectangle((0, 0, w - 1, h - 1), radius=r, outline=(0, 0, 0, 60), width=max(1, h // 40))
    return img


def emoji_image(name, size):
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
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{size}" height="{size}">{icon["body"]}</svg>'
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=size, output_height=size)
    return Image.open(BytesIO(png)).convert("RGBA")


# ------------------------------------------------------------------ text rendering

def parse_tokens(text):
    """'Watch his *FACE* :skull:' -> [(word, color_key or None, is_emoji)] per line."""
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
            if active is None and word[0] in "*~^" and len(word) > 1:
                active = word[0]
                word = word[1:]
            key = active
            stripped = word.rstrip(".,!?'\")")
            tail = word[len(stripped):]
            if active and stripped.endswith(active) and not stripped.endswith("\\" + active):
                word = stripped[:-1] + tail
                active = None
            toks.append((word.replace("\\*", "*"), key, False))  # \* = a literal asterisk
        lines.append(toks)
    return lines


def wrap_tokens(lines, fnt, max_w, emoji_px):
    space = fnt.getlength(" ")
    out = []
    for toks in lines:
        cur, cur_w = [], 0
        for tok in toks:
            tw = emoji_px if tok[2] else fnt.getlength(tok[0])
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


def render_text(text, font_name="Montserrat Black", size=92, color=(255, 255, 255), accent=None,
                stroke=10, max_w=940, line_gap=0.08, shadow=True, upper=True, bg=None, pad=(28, 18),
                align="center", max_lines=2, min_size=60, gradients=None, stroke_color=(0, 0, 0), outline=0,
                outline_color=(255, 255, 255), colors=None):
    """Return an RGBA PIL image of the caption (tight bbox). Shrinks the font until it fits max_lines.
    colors: {"*": (r,g,b), "~": (r,g,b)} solid colors for the highlight spans (overrides COLORS).
    gradients: {"*": ((r,g,b) top, (r,g,b) bottom)} fills those highlight spans with a vertical gradient.
    outline: extra outer outline (sticker look) in outline_color, drawn behind the stroke."""
    if upper:
        text = "\n".join(" ".join(w if (w.startswith(":") and w.endswith(":")) else w.upper()
                                  for w in ln.split(" ")) for ln in text.split("\n"))
    base_size, base_stroke = size, stroke
    tokens = parse_tokens(text)
    explicit = text.count("\n") + 1
    while True:
        fnt = font(font_name, size)
        emoji_px = int(size * 1.05)
        lines = wrap_tokens(tokens, fnt, max_w, emoji_px)
        if len(lines) <= max(max_lines, explicit) or size <= min_size:
            break
        size = int(size * 0.93)
    # a short caption that only just spills onto a second line reads better as one slightly smaller line
    if len(lines) == 2 and explicit == 1:
        small = int(size * 0.86)
        f2 = font(font_name, small)
        if len(wrap_tokens(tokens, f2, max_w, int(small * 1.05))) == 1:
            size, fnt, emoji_px = small, f2, int(small * 1.05)
            lines = wrap_tokens(tokens, fnt, max_w, emoji_px)
    # balance line lengths: smallest width that keeps the same line count (no orphan words)
    if len(lines) > explicit:
        lo, hi = 50, max_w
        while hi - lo > 4:
            mid = (lo + hi) // 2
            if len(wrap_tokens(tokens, fnt, mid, emoji_px)) <= len(lines):
                hi = mid
            else:
                lo = mid
        lines = wrap_tokens(tokens, fnt, hi, emoji_px)
    stroke = max(2, int(round(base_stroke * size / base_size)))
    asc, desc = fnt.getmetrics()
    lh = int((asc + desc) * (1 + line_gap))
    space = fnt.getlength(" ")
    widths = [sum((emoji_px if t[2] else fnt.getlength(t[0])) for t in ln) + space * (len(ln) - 1) for ln in lines]
    tw = int(max(widths) if widths else 10)
    th = lh * len(lines)
    m = stroke + outline + 24
    img = Image.new("RGBA", (tw + 2 * m, th + 2 * m), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    g_masks, g_lines = {}, set()
    out_mask = Image.new("L", img.size, 0) if outline else None
    d_out = ImageDraw.Draw(out_mask) if outline else None
    emojis = []
    for i, ln in enumerate(lines):
        if align == "center":
            x = m + (tw - widths[i]) / 2
        else:
            x = m
        y = m + i * lh
        for word, key, is_emoji in ln:
            if is_emoji:
                emojis.append((int(x), int(y + (asc - emoji_px) * 0.5 + desc * 0.1), word))
                x += emoji_px + space
                continue
            if key and colors and key in colors:
                col = tuple(colors[key])
            elif key:
                col = COLORS[key] if accent is None or key != "*" else accent
            else:
                col = color
            if outline:
                d_out.text((x, y), word, font=fnt, fill=255, stroke_width=stroke + outline, stroke_fill=255)
            if gradients and key in gradients:
                d.text((x, y), word, font=fnt, fill=stroke_color + (255,), stroke_width=stroke,
                       stroke_fill=stroke_color + (255,))
                g_masks.setdefault(key, Image.new("L", img.size, 0))
                ImageDraw.Draw(g_masks[key]).text((x, y), word, font=fnt, fill=255)
                g_lines.add(i)
            else:
                d.text((x, y), word, font=fnt, fill=col + (255,), stroke_width=stroke,
                       stroke_fill=stroke_color + (255,))
            x += fnt.getlength(word) + space
    for key, gm in g_masks.items():
        top, bot = gradients[key]
        grad = np.zeros((img.height, img.width, 4), np.uint8)
        for li in g_lines:
            y0 = m + li * lh + int(asc * 0.18)
            y1 = m + li * lh + asc
            rows = np.clip((np.arange(img.height) - y0) / max(1, y1 - y0), 0, 1)
            band = (np.arange(img.height) >= m + li * lh - stroke) & (np.arange(img.height) < m + (li + 1) * lh + stroke)
            for c in range(3):
                col_rows = top[c] + (bot[c] - top[c]) * rows
                grad[band, :, c] = col_rows[band, None].astype(np.uint8)
        grad[..., 3] = np.asarray(gm)
        img.alpha_composite(Image.fromarray(grad, "RGBA"))
    if outline:
        base_o = Image.new("RGBA", img.size, outline_color + (0,))
        base_o.putalpha(out_mask)
        base_o.alpha_composite(img)
        img = base_o
    for ex, ey, name in emojis:
        try:
            em = emoji_image(name, emoji_px)
            img.alpha_composite(em, (ex, max(0, ey)))
        except KeyError:
            print("  ! unknown emoji", name, file=sys.stderr)
    if bg is not None:
        # pill background (for labels): rounded rect behind the text
        bbox = img.getbbox() or (0, 0, img.width, img.height)
        pw, ph = bbox[2] - bbox[0] + 2 * pad[0], bbox[3] - bbox[1] + 2 * pad[1]
        pill = Image.new("RGBA", (pw + 16, ph + 16), (0, 0, 0, 0))
        pd = ImageDraw.Draw(pill)
        pd.rounded_rectangle((8, 8, 8 + pw, 8 + ph), radius=min(ph // 2, 40), fill=bg + (255,))
        pill.alpha_composite(img.crop(bbox), (8 + pad[0], 8 + pad[1]))
        img = pill
    if shadow:
        a = img.split()[3]
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        sh.putalpha(a.point(lambda v: int(v * 0.55)))
        sh = sh.filter(ImageFilter.GaussianBlur(7))
        base = Image.new("RGBA", (img.width, img.height + 8), (0, 0, 0, 0))
        base.alpha_composite(sh, (0, 8))
        base.alpha_composite(img, (0, 0))
        img = base
    bbox = img.getbbox()
    return img.crop(bbox) if bbox else img


def to_np_rgba(img):
    a = np.asarray(img).astype(np.float32)
    return a[..., :3], a[..., 3:4] / 255.0


def blit(frame, rgb, alpha, cx, cy, scale=1.0, opacity=1.0):
    """Alpha-composite rgb/alpha (float arrays) centred at (cx, cy) onto frame (float32 HxWx3)."""
    if scale <= 0.01 or opacity <= 0.005:
        return
    if abs(scale - 1.0) > 1e-3:
        h, w = rgb.shape[:2]
        nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
        rgb = cv2.resize(rgb, (nw, nh), interpolation=cv2.INTER_LINEAR)
        alpha = cv2.resize(alpha, (nw, nh), interpolation=cv2.INTER_LINEAR)[..., None]
    h, w = rgb.shape[:2]
    x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    fx0, fy0, fx1, fy1 = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    if fx1 <= fx0 or fy1 <= fy0:
        return
    sx0, sy0 = fx0 - x0, fy0 - y0
    a = alpha[sy0:sy0 + fy1 - fy0, sx0:sx0 + fx1 - fx0] * opacity
    frame[fy0:fy1, fx0:fx1] = frame[fy0:fy1, fx0:fx1] * (1 - a) + rgb[sy0:sy0 + fy1 - fy0, sx0:sx0 + fx1 - fx0] * a


# ------------------------------------------------------------------ source decoding

def display_size(path, rotate=0):
    """Width/height after applying sample aspect ratio and an optional rotation (even numbers)."""
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
    """Decode a segment into a list of RGB uint8 frames at the output rate (speed already applied)."""
    path = os.path.join(CLIP_DIR, seg["clip"] + ".mp4")
    info = ffprobe(path)
    speed = float(seg.get("speed", 1.0))
    t_in, t_out = float(seg["in"]), float(seg["out"])
    src_dur = max(0.05, t_out - t_in)
    n_out = max(1, int(round(src_dur / speed * FPS)))
    rot = seg.get("rotate", 0)
    dw, dh = display_size(path, rot)
    filters = []
    if seg.get("deinterlace", False):
        filters.append("bwdif=mode=send_frame:deint=all")
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
    lo, hi = np.percentile(lum, 1.0), np.percentile(lum, 99.3)
    lo = lo * strength
    hi = 255 - (255 - hi) * strength
    if hi - lo < 40:
        return lambda f: f
    scale = 245.0 / (hi - lo)

    def fn(f):
        return np.clip((f - lo) * scale + 6, 0, 255)
    return fn


def grade(f, sat=1.14, contrast=1.06):
    mean = f.mean(axis=2, keepdims=True)
    f = mean + (f - mean) * sat
    f = (f - 128.0) * contrast + 128.0
    return np.clip(f, 0, 255)


def sharpen(img_u8, amount=0.6, radius=2.0):
    blur = cv2.GaussianBlur(img_u8, (0, 0), radius)
    return cv2.addWeighted(img_u8, 1 + amount, blur, -amount, 0)


# ------------------------------------------------------------------ framing

def crop_rect(src_w, src_h, out_aspect, zoom, fx, fy):
    """Largest out_aspect rect inside src, zoomed by `zoom` around focus (fx, fy) in [0,1]."""
    if src_w / src_h > out_aspect:
        ch = src_h
        cw = ch * out_aspect
    else:
        cw = src_w
        ch = cw / out_aspect
    cw /= zoom
    ch /= zoom
    cx = min(max(fx * src_w, cw / 2), src_w - cw / 2)
    cy = min(max(fy * src_h, ch / 2), src_h - ch / 2)
    return cx - cw / 2, cy - ch / 2, cw, ch


def warp_crop(src, rect, out_w, out_h, shake=(0, 0), interp=cv2.INTER_CUBIC):
    x, y, cw, ch = rect
    sx, sy = out_w / cw, out_h / ch
    M = np.array([[sx, 0, -x * sx + shake[0]], [0, sy, -y * sy + shake[1]]], dtype=np.float32)
    return cv2.warpAffine(src, M, (out_w, out_h), flags=interp, borderMode=cv2.BORDER_REFLECT)


def blurred_bg(src_u8, darken=0.42):
    small = cv2.resize(src_u8, (108, 192) if src_u8.shape[1] < src_u8.shape[0] else (192, 108),
                       interpolation=cv2.INTER_AREA)
    sh, sw = small.shape[:2]
    # cover-fit into 108x192 then blur
    scale = max(108 / sw, 192 / sh)
    small = cv2.resize(small, (int(sw * scale) + 1, int(sh * scale) + 1), interpolation=cv2.INTER_LINEAR)
    y0 = (small.shape[0] - 192) // 2
    x0 = (small.shape[1] - 108) // 2
    small = small[y0:y0 + 192, x0:x0 + 108]
    small = cv2.GaussianBlur(small, (0, 0), 6)
    bg = cv2.resize(small, (W, H), interpolation=cv2.INTER_LINEAR).astype(np.float32) * darken
    return bg


# ------------------------------------------------------------------ effects over time

def fx_value(fxlist, kind, t):
    """Sum of active effect envelopes of a kind at segment-local time t."""
    v = 0.0
    for fx in fxlist:
        if fx["type"] != kind:
            continue
        at, dur = fx.get("at", 0.0), fx.get("dur", 0.4)
        if at <= t < at + dur:
            x = (t - at) / dur
            if kind == "punch":
                # snap in fast, hold, ease back
                hold = fx.get("hold", 0.55)
                if x < 0.12:
                    e = ease_out(x / 0.12)
                elif x < hold:
                    e = 1.0
                else:
                    e = 1 - ease_out((x - hold) / (1 - hold))
                v += fx.get("amount", 0.25) * e
            elif kind == "shake":
                v += fx.get("amp", 16) * (1 - x) ** 1.5
            elif kind == "flash":
                v += (1 - x) ** 2 * fx.get("amount", 1.0)
    return v


# ------------------------------------------------------------------ main render

def voice_activity(v, hop=0.01, thr_db=-40.0, attack=0.02, release=0.3):
    """0..1 envelope that is 1 while the narrator speaks (fast attack, slow release between words)."""
    m = v.mean(axis=1) if v.ndim == 2 else v
    h = int(hop * SR)
    nh = len(m) // h + 1
    buf = np.zeros(nh * h, np.float32)
    buf[:len(m)] = m
    rms = np.sqrt((buf.reshape(nh, h) ** 2).mean(axis=1) + 1e-12)
    on = (20 * np.log10(rms) > thr_db).astype(np.float32)
    a_att, a_rel = np.exp(-hop / attack), np.exp(-hop / release)
    env, y = np.zeros(nh, np.float32), 0.0
    for i in range(nh):
        a = a_att if on[i] > y else a_rel
        y = a * y + (1 - a) * on[i]
        env[i] = y
    return np.interp(np.arange(len(m)), np.arange(nh) * h + h / 2, env).astype(np.float32)


def limiter(x, ceiling=0.84, lookahead=0.005, release=0.12):
    """Brick-wall look-ahead limiter on a (n, 2) float array."""
    from scipy.ndimage import minimum_filter1d
    peak = np.max(np.abs(x), axis=1)
    g = np.minimum(1.0, ceiling / np.maximum(peak, 1e-9))
    la = max(1, int(lookahead * SR))
    g = minimum_filter1d(g, size=2 * la + 1)
    rel = math.exp(-1.0 / (release * SR))
    out = np.empty_like(g)
    cur = 1.0
    for i in range(len(g)):
        gi = g[i]
        cur = gi if gi < cur else gi + (cur - gi) * rel
        out[i] = cur
    return (x * out[:, None]).astype(np.float32)


class Renderer:
    def __init__(self, plan, preview=False):
        self.p = plan
        self.preview = preview
        self.layout = plan.get("layout", "band")
        band = plan.get("band", {})
        self.band_y = band.get("y", 470)
        self.band_h = band.get("h", 780)
        self.rng = np.random.default_rng(plan.get("seed", 3))
        self.captions = []
        self.title = None

    # ---------- text assets
    def prepare_text(self):
        p = self.p
        if p.get("title"):
            t = p["title"]
            img = render_text(t["text"], t.get("font", "Montserrat Black"), t.get("size", 84),
                              accent=hex_rgb(t["accent"]) if t.get("accent") else None,
                              stroke=t.get("stroke", 9), max_w=t.get("max_w", 1000), upper=t.get("upper", True),
                              max_lines=t.get("max_lines", 2))
            self.title = (to_np_rgba(img), t.get("y", 290), t.get("start", 0.0), t.get("end", 1e9))
        for c in p.get("captions", []):
            style = c.get("style", "cap")
            if style == "pill":
                img = render_text(c["text"], c.get("font", "Montserrat Black"), c.get("size", 58),
                                  color=hex_rgb(c.get("color", "#111111")), stroke=0, shadow=True,
                                  bg=hex_rgb(c.get("bg", "#FFD60A")), max_w=c.get("max_w", 900))
            else:
                img = render_text(c["text"], c.get("font", "Montserrat Black"), c.get("size", 90),
                                  color=hex_rgb(c.get("color", "#FFFFFF")),
                                  accent=hex_rgb(c["accent"]) if c.get("accent") else None,
                                  stroke=c.get("stroke", 11), max_w=c.get("max_w", 880),
                                  upper=c.get("upper", True), max_lines=c.get("max_lines", 2))
            self.captions.append((c, to_np_rgba(img)))
        self.flag_h = 100
        self.badge = to_np_rgba(self.profile_badge()) if p.get("profile", True) else None
        lb = p.get("leaderboard")
        if lb:
            self.lb_row_h = 64
            self.lb_rows = {}
            for r in lb["rows"]:
                for hl in (False, True):
                    self.lb_rows[(id(r), hl)] = to_np_rgba(self.leaderboard_row(r, hl))
            self.lb_rank = [to_np_rgba(render_text(f"{i + 1}.", "Montserrat Black", 36, stroke=0, shadow=False,
                                                   upper=False, max_lines=1))
                            for i in range(len(lb["rows"]))]
            self.lb_title = to_np_rgba(render_text(lb.get("title", "LEADERBOARD"), "Montserrat Black", 26,
                                                   color=(255, 214, 10), stroke=0, shadow=False, max_lines=1))
        fr = p.get("flag_row")
        if fr:
            self.flag_imgs = [to_np_rgba(flag_image(c, 66)) for c in fr["flags"]]
            self.check_img = to_np_rgba(emoji_image("check-mark-button", 36))
            self.cross_img = to_np_rgba(emoji_image("cross-mark", 36))
        wm = p.get("watermark")
        self.watermark = None
        if wm:
            img = render_text(wm, "Montserrat ExtraBold", 30, stroke=3, shadow=False, upper=False, max_lines=1)
            self.watermark = to_np_rgba(img)

    def caption_y(self, c, h):
        """Centre y for a caption of rendered height h."""
        pos = c.get("pos", "low")
        if isinstance(pos, (int, float)):
            return pos
        if self.layout == "full":
            return {"low": 1330, "mid": 960, "top": 420, "upper": 700}.get(pos, 1330)
        bottom = self.band_y + self.band_h
        low = bottom + (self.flag_h if self.p.get("flag_row") else 0) + 18 + h / 2
        return {"low": low, "mid": self.band_y + self.band_h / 2,
                "top": self.band_y - 16 - h / 2, "upper": self.band_y + 36 + h / 2,
                "band_low": bottom - 28 - h / 2}.get(pos, low)

    def profile_badge(self):
        """Small channel badge: round avatar, name + verified tick, @handle underneath."""
        d = 58
        path = os.path.join(ROOT, "assets", "brand", "avatar.jpg")
        av = Image.open(path).convert("RGBA") if os.path.exists(path) else Image.new("RGBA", (d, d), (150, 20, 25, 255))
        sq = min(av.size)
        av = av.crop(((av.width - sq) // 2, (av.height - sq) // 2, (av.width + sq) // 2, (av.height + sq) // 2))
        av = av.resize((d, d), Image.LANCZOS)
        ss = 4
        mask = Image.new("L", (d * ss, d * ss), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, d * ss - 1, d * ss - 1), fill=255)
        av.putalpha(mask.resize((d, d), Image.LANCZOS))
        ring = Image.new("RGBA", (d + 4, d + 4), (0, 0, 0, 0))
        rm = Image.new("L", ((d + 4) * ss, (d + 4) * ss), 0)
        ImageDraw.Draw(rm).ellipse((0, 0, (d + 4) * ss - 1, (d + 4) * ss - 1), fill=255)
        ring.paste((255, 255, 255, 255), (0, 0), rm.resize((d + 4, d + 4), Image.LANCZOS))
        ring.alpha_composite(av, (2, 2))
        nf, hf = font("Montserrat ExtraBold", 30), font("Montserrat ExtraBold", 22)
        name, handle = "RageStyles", "@Rage_Styles"
        badge_svg = open(os.path.join(ROOT, "assets", "brand", "verified.svg")).read()
        tick = Image.open(BytesIO(cairosvg.svg2png(bytestring=badge_svg.encode(), output_width=26, output_height=26))).convert("RGBA")
        tw = int(nf.getlength(name))
        w = ring.width + 12 + max(tw + 6 + tick.width, int(hf.getlength(handle))) + 8
        img = Image.new("RGBA", (w, ring.height + 8), (0, 0, 0, 0))
        img.alpha_composite(ring, (0, 4))
        dr = ImageDraw.Draw(img)
        x = ring.width + 12
        dr.text((x, 4), name, font=nf, fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0, 170))
        img.alpha_composite(tick, (x + tw + 6, 9))
        dr.text((x, 38), handle, font=hf, fill=(225, 225, 225, 255), stroke_width=2, stroke_fill=(0, 0, 0, 150))
        return img

    def leaderboard_row(self, r, highlight):
        fh = 38
        fl = flag_image(r["flag"], fh)
        lf = font("Montserrat Black", 36)
        label, value = r.get("label", ""), f'{r["value"]:g} {r.get("unit", "KG")}'
        w = 330
        img = Image.new("RGBA", (w, self.lb_row_h), (0, 0, 0, 0))
        img.alpha_composite(fl, (0, (self.lb_row_h - fh) // 2))
        d = ImageDraw.Draw(img)
        d.text((fl.width + 14, 11), label, font=lf, fill=(255, 255, 255, 255))
        vc = (255, 214, 10, 255) if highlight else (255, 255, 255, 255)
        d.text((w - lf.getlength(value), 11), value, font=lf, fill=vc)
        return img

    def draw_leaderboard(self, frame, t):
        lb = self.p["leaderboard"]
        shown = [r for r in lb["rows"] if r["t"] <= t]
        if not shown:
            return
        t_evt = shown[-1]["t"]
        after = sorted(shown, key=lambda r: -r["value"])
        before = sorted(shown[:-1], key=lambda r: -r["value"])
        prog = ease_out((t - t_evt - 0.4) / 0.35) if t - t_evt > 0.4 else 0.0  # appears at the bottom, then climbs
        px, py = lb.get("pos", (0.02, 0.03))
        x0, y0 = px * W, self.band_y + py * self.band_h
        rh, pad = self.lb_row_h, 18
        n_rows = len(before) + (len(after) - len(before)) * min(1.0, ease_out((t - t_evt) / 0.25)) if before else len(after)
        pw, ph = 460, int(pad * 2 + 34 + rh * n_rows)
        frame[int(y0):min(H, int(y0 + ph)), int(x0):min(W, int(x0 + pw))] *= 0.38
        rgb, a = self.lb_title
        blit(frame, rgb, a, x0 + pad + rgb.shape[1] / 2, y0 + pad + 12)
        base_y = y0 + pad + 34
        for i in range(len(after)):
            rgb, a = self.lb_rank[i]
            blit(frame, rgb, a, x0 + pad + 20, base_y + i * rh + rh / 2)
        new = shown[-1]
        new_slot = None
        for r in after:  # existing rows first; the new row is drawn last, on its own card
            ra = after.index(r)
            if r is new:
                new_slot = len(before) + (ra - len(before)) * prog if before else ra
                continue
            rb = before.index(r)
            rgb, a = self.lb_rows[(id(r), False)]
            blit(frame, rgb, a, x0 + pad + 58 + rgb.shape[1] / 2, base_y + (rb + (ra - rb) * prog) * rh + rh / 2)
        if new_slot is not None:
            cy = base_y + new_slot * rh + rh / 2
            if 0.0 < prog < 1.0:
                card = frame[int(cy - rh / 2 + 3):int(cy + rh / 2 - 3), int(x0 + pad + 50):int(x0 + pw - 10)]
                card[:] = card * 0.15 + np.array([28, 28, 32], np.float32) * 0.85
            rgb, a = self.lb_rows[(id(new), t - t_evt < 2.0)]
            blit(frame, rgb, a, x0 + pad + 58 + rgb.shape[1] / 2, cy, opacity=min(1.0, (t - t_evt) / 0.2))

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
        gap = 38
        x = W / 2 - (n * fw + (n - 1) * gap) / 2 + fw / 2
        y = self.band_y + self.band_h + self.flag_h / 2 + 4
        for i in range(n):
            rgb, a = self.flag_imgs[i]
            is_act = i == active
            blit(frame, rgb, a, x, y, scale=1.2 if is_act else 1.0, opacity=1.0 if (is_act or i in marks) else 0.45)
            if is_act:
                cv2.rectangle(frame, (int(x - fw * 0.5), int(y + 48)), (int(x + fw * 0.5), int(y + 54)), (255, 214, 10), -1)
            if i in marks:
                kind, tm = marks[i]
                im = self.check_img if kind == "check" else self.cross_img
                blit(frame, im[0], im[1], x + fw * 0.46, y + 26, scale=1.0 + 0.35 * (1 - ease_out((t - tm) / 0.18)))
            x += fw + gap

    # ---------- per-frame drawing
    def draw_overlays(self, frame, t):
        if getattr(self, "badge", None) is not None:
            rgb, a = self.badge
            bx, by = self.p.get("profile_pos", (36, 112))
            blit(frame, rgb, a, bx + rgb.shape[1] / 2, by + rgb.shape[0] / 2, opacity=self.p.get("profile_opacity", 0.85))
        if self.title is not None:
            (rgb, a), y, t0, t1 = self.title
            if t0 <= t < t1:
                k = t - t0
                s = ease_out_back(k / 0.25) if k < 0.25 else 1.0
                blit(frame, rgb, a, W / 2, y, scale=s, opacity=min(1, k / 0.08 + 0.01))
        for c, (rgb, a) in self.captions:
            t0, d = c["t"], c.get("d", 1.5)
            if not (t0 <= t < t0 + d):
                continue
            k = t - t0
            anim = c.get("anim", "pop")
            s, op = 1.0, 1.0
            if anim == "pop":
                s = 0.55 + 0.45 * ease_out_back(k / 0.2) if k < 0.2 else 1.0
                op = min(1.0, k / 0.05)
            elif anim == "slam":
                s = 1.8 - 0.8 * ease_out(k / 0.14) if k < 0.14 else 1.0
                op = min(1.0, k / 0.04)
            elif anim == "fade":
                op = min(1.0, k / 0.15)
            elif anim == "snap":  # quick, subtle pop for fast phrase captions
                s = 0.88 + 0.12 * ease_out(k / 0.08) if k < 0.08 else 1.0
                op = min(1.0, k / 0.03)
            elif anim == "punch":  # toned-down slam for key words: small settle, no big zoom
                s = 1.22 - 0.22 * ease_out(k / 0.12) if k < 0.12 else 1.0
                op = min(1.0, k / 0.04)
            elif anim == "pulse":  # no wobble any more: same clean pop-in
                s = 0.55 + 0.45 * ease_out_back(k / 0.2) if k < 0.2 else 1.0
                op = min(1.0, k / 0.05)
            tail = t0 + d - t
            if tail < 0.07 and c.get("exit", "cut") == "fade":
                op *= tail / 0.07
            cx = c.get("x", 0.5) * W
            blit(frame, rgb, a, cx, self.caption_y(c, rgb.shape[0]), scale=s, opacity=op)
        if self.watermark is not None:
            rgb, a = self.watermark
            wy = self.p.get("watermark_y", self.band_y + 28 if self.layout == "band" else 1540)
            blit(frame, rgb, a, W - 24 - rgb.shape[1] / 2, wy, opacity=0.55)

    def draw_stickers(self, frame, t, band_rect):
        bx, by, bw, bh = band_rect
        for s in self.p.get("stickers", []):
            t0, d = s["t"], s.get("d", 1.2)
            if not (t0 <= t < t0 + d):
                continue
            k = t - t0
            x = bx + s.get("x", 0.5) * bw
            y = by + s.get("y", 0.5) * bh
            col = hex_rgb(s.get("color", "#FF2D2D"))[::-1]  # BGR not needed: frame is RGB
            col = hex_rgb(s.get("color", "#FF2D2D"))
            grow = ease_out_back(k / 0.22) if k < 0.22 else 1.0
            if s["type"] == "ring":
                rx = s.get("rx", s.get("r", 110)) * grow
                ry = s.get("ry", s.get("r", 110) * 0.86) * grow
                cv2.ellipse(frame, (int(x), int(y)), (max(1, int(rx)), max(1, int(ry))), -8, 0, 360,
                            (0, 0, 0), 20, cv2.LINE_AA)
                cv2.ellipse(frame, (int(x), int(y)), (max(1, int(rx)), max(1, int(ry))), -8, 0, 360,
                            col, 11, cv2.LINE_AA)
            elif s["type"] == "arrow":
                ang = math.radians(s.get("angle", 225))
                length = s.get("len", 190) * grow
                tip_gap = s.get("gap", 20)
                x1 = x + math.cos(ang) * tip_gap
                y1 = y - math.sin(ang) * tip_gap
                x0 = x1 + math.cos(ang) * length
                y0 = y1 - math.sin(ang) * length
                bob = 0.0
                p0 = (int(x0 + math.cos(ang) * bob), int(y0 - math.sin(ang) * bob))
                p1 = (int(x1 + math.cos(ang) * bob), int(y1 - math.sin(ang) * bob))
                cv2.arrowedLine(frame, p0, p1, (0, 0, 0), 26, cv2.LINE_AA, tipLength=0.35)
                cv2.arrowedLine(frame, p0, p1, col, 15, cv2.LINE_AA, tipLength=0.35)
            elif s["type"] == "emoji":
                if "_img" not in s:
                    s["_img"] = to_np_rgba(emoji_image(s["name"], s.get("size", 150)))
                rgb, a = s["_img"]
                bob = s.get("bob", 10) * math.sin(k * 7)
                blit(frame, rgb, a, x, y + bob, scale=grow * (1 + 0.03 * math.sin(k * 9)))
            elif s["type"] == "bar":
                # countdown / tension bar across the band top
                frac = min(1.0, k / d)
                cv2.rectangle(frame, (int(bx), int(by)), (int(bx + bw * frac), int(by + 12)), col, -1)

    # ---------- main
    def build_timeline(self):
        segs = []
        t = 0.0
        for i, seg in enumerate(self.p["segments"]):
            frames = decode_segment(seg)
            dur = len(frames) / FPS
            freeze = seg.get("freeze")
            fdur = freeze["dur"] if freeze else 0.0
            segs.append({"seg": seg, "frames": frames, "t0": t, "dur": dur + fdur, "play": dur})
            t += dur + fdur
        self.timeline = segs
        self.total = t
        return t

    def frame_at(self, i):
        t = i / FPS
        for sgi, s in enumerate(self.timeline):
            if s["t0"] <= t < s["t0"] + s["dur"] or sgi == len(self.timeline) - 1:
                return sgi, s, t - s["t0"]
        return len(self.timeline) - 1, self.timeline[-1], t - self.timeline[-1]["t0"]

    def render_video(self, out_video):
        n_total = int(round(self.total * FPS))
        levels = [auto_levels(s["frames"], s["seg"].get("levels", 1.0)) if s["seg"].get("auto_levels", True)
                  else (lambda f: f) for s in self.timeline]
        enc = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
               "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264",
               "-preset", "veryfast" if self.preview else "medium", "-crf", "24" if self.preview else "18",
               "-pix_fmt", "yuv420p", "-profile:v", "high", "-movflags", "+faststart", out_video]
        proc = subprocess.Popen(enc, stdin=subprocess.PIPE)
        trans_frames = 5
        for i in range(n_total):
            sgi, s, lt = self.frame_at(i)
            seg = s["seg"]
            frames = s["frames"]
            fi = min(int(lt * FPS), len(frames) - 1)
            frozen = lt >= s["play"]
            src = frames[fi]
            fxl = seg.get("fx", [])
            # ---- zoom path
            z0, z1 = seg.get("zoom", [1.0, 1.0])
            prog = min(1.0, lt / max(0.01, s["dur"]))
            zoom = z0 + (z1 - z0) * (prog * prog * (3 - 2 * prog))
            zoom += fx_value(fxl, "punch", lt)
            if frozen and seg.get("freeze", {}).get("zoom", 0):
                fz = seg["freeze"]
                zoom += fz["zoom"] * ease_out((lt - s["play"]) / fz["dur"])
            f0x, f0y = seg.get("focus", [0.5, 0.5])
            if "focus_to" in seg:
                f1x, f1y = seg["focus_to"]
                f0x += (f1x - f0x) * prog
                f0y += (f1y - f0y) * prog
            amp = 0.0  # camera shake removed: clean frame
            shake = (self.rng.uniform(-amp, amp), self.rng.uniform(-amp, amp)) if amp > 0.5 else (0, 0)
            sh, sw = src.shape[:2]
            if self.layout == "band":
                bx, by, bw, bh = 0, self.band_y, W, self.band_h
            else:
                bx, by, bw, bh = 0, 0, W, H
            rect = crop_rect(sw, sh, bw / bh, max(zoom, 1.0), f0x, f0y)
            frame = blurred_bg(src) if self.layout == "band" else np.zeros((H, W, 3), np.float32)
            vid = warp_crop(src, rect, bw, bh, shake)
            vid = levels[sgi](vid.astype(np.float32))
            vid = grade(vid, seg.get("sat", 1.14), seg.get("contrast", 1.06))
            if frozen and seg.get("freeze", {}).get("desat", False):
                g = vid.mean(axis=2, keepdims=True)
                vid = vid * 0.35 + g * 0.65
            is_bw = seg.get("bw") or (frozen and (seg.get("freeze") or {}).get("bw"))
            if is_bw:
                g = vid @ np.array([0.299, 0.587, 0.114], np.float32)
                vid = np.repeat(g[..., None], 3, axis=2)
                g2 = frame @ np.array([0.299, 0.587, 0.114], np.float32)
                frame = np.repeat(g2[..., None], 3, axis=2)
            vid = sharpen(np.clip(vid, 0, 255).astype(np.uint8), seg.get("sharpen", 0.55)).astype(np.float32)
            frame[by:by + bh, bx:bx + bw] = vid
            if self.layout == "band":
                # thin dark edge lines so the band reads as a card
                frame[by:by + 3] *= 0.3
                frame[by + bh - 3:by + bh] *= 0.3
            # ---- transitions at segment starts (applied on first frames of the segment)
            tr = seg.get("transition", "cut")
            k = int(lt * FPS)
            if tr not in ("cut", "glitch") and k < trans_frames and sgi > 0:
                x = 1 - k / trans_frames
                if tr == "flash":
                    frame = frame * (1 - x) + 255 * x
                elif tr == "whip":
                    ksz = int(10 + 90 * x) | 1
                    kern = np.zeros((1, ksz), np.float32)
                    kern[0, :] = 1.0 / ksz
                    frame = cv2.filter2D(frame, -1, kern)
                    shift = int(160 * x)
                    frame = np.roll(frame, -shift, axis=1)
                elif tr == "zoomblur":
                    acc = frame.copy()
                    for j in range(1, 5):
                        sc = 1 + 0.06 * j * x
                        M = cv2.getRotationMatrix2D((W / 2, by + bh / 2), 0, sc)
                        acc += cv2.warpAffine(frame, M, (W, H), borderMode=cv2.BORDER_REFLECT)
                    frame = acc / 5
                elif tr == "glitch":
                    off = int(24 * x) + 4
                    frame[..., 0] = np.roll(frame[..., 0], off, axis=1)
                    frame[..., 2] = np.roll(frame[..., 2], -off, axis=1)
                    for _ in range(6):
                        y0 = int(self.rng.uniform(0, H - 80))
                        hh = int(self.rng.uniform(20, 90))
                        frame[y0:y0 + hh] = np.roll(frame[y0:y0 + hh], int(self.rng.uniform(-60, 60)), axis=1)
            fl = fx_value(fxl, "flash", lt)
            if fl > 0:
                frame = frame * (1 - fl) + 255 * fl
            if seg.get("vignette") or (frozen and seg.get("freeze", {}).get("vignette", True)):
                if not hasattr(self, "_vig"):
                    yy, xx = np.mgrid[0:H, 0:W]
                    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
                    self._vig = np.clip(1.15 - 0.55 * r ** 2, 0.35, 1)[..., None].astype(np.float32)
                frame = frame * self._vig
            self.draw_stickers(frame, i / FPS, (bx, by, bw, bh))
            if self.p.get("leaderboard"):
                self.draw_leaderboard(frame, i / FPS)
            if self.p.get("flag_row"):
                self.draw_flag_row(frame, i / FPS)
            self.draw_overlays(frame, i / FPS)
            proc.stdin.write(np.clip(frame, 0, 255).astype(np.uint8).tobytes())
            if i % 90 == 0:
                print(f"  frame {i}/{n_total}", flush=True)
        proc.stdin.close()
        proc.wait()
        if proc.returncode:
            raise RuntimeError("encoder failed")

    # ---------- audio
    def render_audio(self, out_wav):
        n = int(round(self.total * SR)) + SR // 10
        mix = np.zeros((n, 2), np.float32)
        music_mix = np.zeros((n, 2), np.float32)
        # music bed: one mood, or a list of timed parts. It is only used as the loudness reference
        # (so SFX keep their v1 levels); it is not part of the output unless "music_in_output" is set.
        m = self.p.get("music")
        parts = m if isinstance(m, list) else ([m] if m else [])
        drops = (m.get("drops", []) if isinstance(m, dict) else self.p.get("music_drops", []))
        if parts and not all(os.path.exists(os.path.join(MUSIC_DIR, q["mood"] + ".wav")) for q in parts):
            subprocess.run([sys.executable, os.path.join(HERE, "music_synth.py")], check=True)  # deterministic
        for part in parts:
            bed, sr = sf.read(os.path.join(MUSIC_DIR, part["mood"] + ".wav"), dtype="float32")
            assert sr == SR
            a = int(part.get("from", 0.0) * SR)
            b = min(n, int(part.get("to", self.total) * SR)) if part.get("to") else n
            ln = max(0, b - a)
            off = int(part.get("offset", 0.0) * SR)
            reps = int(math.ceil((ln + off) / len(bed))) + 1
            seg = np.tile(bed, (reps, 1))[off:off + ln]
            env = np.ones(ln, np.float32)
            fin = min(ln, int(part.get("fade_in", 0.25) * SR))
            fout = min(ln, int(part.get("fade_out", 0.6 if b >= n - SR // 10 else 0.12) * SR))
            if fin:
                env[:fin] = np.linspace(0, 1, fin)
            if fout:
                env[-fout:] *= np.linspace(1, 0, fout)
            music_mix[a:a + ln] += seg * 10 ** (part.get("db", -16) / 20) * env[:, None]
        # optional music drops (silence the beds for impact moments)
        if drops:
            env = np.ones(n, np.float32)
            ramp = int(0.04 * SR)
            for drop in drops:
                a, b = int(drop[0] * SR), int(drop[1] * SR)
                env[a:b] = 0
                if a - ramp > 0:
                    env[a - ramp:a] *= np.linspace(1, 0, ramp)
                if b + ramp < n:
                    env[b:b + ramp] *= np.linspace(0, 1, ramp)
            music_mix *= env[:, None]
        # source audio
        src_db = self.p.get("source_audio_db")
        if src_db is not None:
            for s in self.timeline:
                seg = s["seg"]
                if seg.get("mute"):
                    continue
                path = os.path.join(CLIP_DIR, seg["clip"] + ".mp4")
                if not has_audio(path):
                    continue
                speed = float(seg.get("speed", 1.0))
                dur = float(seg["out"]) - float(seg["in"])
                af = f"asetrate={int(SR * speed)},aresample={SR}" if abs(speed - 1) > 1e-3 else f"aresample={SR}"
                cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", f"{seg['in']:.3f}", "-t", f"{dur:.3f}",
                       "-i", path, "-vn", "-ac", "2", "-af", af, "-f", "f32le", "-"]
                raw = subprocess.run(cmd, capture_output=True).stdout
                a = np.frombuffer(raw, np.float32).reshape(-1, 2)
                a = a[: int(s["play"] * SR)]
                g = 10 ** ((src_db + seg.get("audio_db", 0)) / 20)
                st = int(s["t0"] * SR)
                ln = min(len(a), n - st)
                fade = min(int(0.02 * SR), ln // 2)
                if ln <= 0:
                    continue
                env = np.ones(ln, np.float32)
                env[:fade] = np.linspace(0, 1, fade)
                env[-fade:] = np.linspace(1, 0, fade)
                mix[st:st + ln] += a[:ln] * g * env[:, None]
        # narration
        voice_bus = np.zeros((n, 2), np.float32)
        for vc in self.p.get("voice", []):
            x, sr = sf.read(os.path.join(ROOT, vc["file"]), dtype="float32")  # relative to ragestyles-shorts/
            assert sr == SR
            if x.ndim == 1:
                x = np.stack([x, x], 1)
            st = int(vc["t"] * SR)
            ln = min(len(x), n - st)
            if ln > 0:
                voice_bus[st:st + ln] += x[:ln] * 10 ** (vc.get("db", self.p.get("voice_db", 0.0)) / 20)
        # sfx
        sfx_bus = np.zeros((n, 2), np.float32)
        sfx_free = np.zeros((n, 2), np.float32)  # cues marked "duck": false (sub hits that sit under words)
        for cue in self.p.get("sfx", []):
            x, sr = sf.read(os.path.join(SFX_DIR, cue["name"] + ".wav"), dtype="float32")
            if x.ndim == 1:
                x = np.stack([x, x], 1)
            st = int(cue["t"] * SR)
            if st < 0:
                x, st = x[-st:], 0
            if st >= n:
                continue
            ln = min(len(x), n - st)
            bus = sfx_bus if cue.get("duck", True) else sfx_free
            bus[st:st + ln] += x[:ln] * 10 ** (cue.get("db", -6) / 20)
        # duck the effects while the narrator speaks, so a boom tail never covers a word
        duck_db = self.p.get("duck_sfx_db", -6.0)
        if self.p.get("voice") and duck_db:
            act = voice_activity(voice_bus)
            sfx_bus *= (1 - (1 - 10 ** (duck_db / 20)) * act)[:, None]
        mix += voice_bus + sfx_bus + sfx_free
        # loudness: normalise the full v1 mix (music + effects) to -14 LUFS, then apply that same gain
        # to the effects alone, so they sound exactly as loud as in v1 but without the music bed
        meter = pyln.Meter(SR)
        target = self.p.get("lufs", -14.0)
        full = mix + music_mix
        gain = 1.0
        for _ in range(3):
            loud = meter.integrated_loudness(full.astype(np.float64))
            if not np.isfinite(loud) or abs(loud - target) < 0.3:
                break
            g = 10 ** ((target - loud) / 20)
            full = limiter(full * g)
            gain *= g
        out = full if self.p.get("music_in_output") else limiter(mix * gain)
        stems = os.environ.get("RS_STEMS")  # debug: write voice / effects stems (post-gain) for balance checks
        if stems:
            n_out = int(round(self.total * SR))
            sf.write(os.path.join(stems, self.p["id"] + "_voice.wav"), (voice_bus * gain)[:n_out], SR, subtype="FLOAT")
            sf.write(os.path.join(stems, self.p["id"] + "_sfx.wav"), ((sfx_bus + sfx_free) * gain)[:n_out], SR,
                     subtype="FLOAT")
        sf.write(out_wav, out[: int(round(self.total * SR))], SR, subtype="PCM_16")

    def resolve_times(self):
        """Cues may be anchored to a segment: {"seg": i, "at": offset}. Missing "d" = until the segment ends."""
        for key in ("captions", "sfx", "stickers"):
            for c in self.p.get(key, []):
                if "seg" not in c:
                    continue
                s = self.timeline[c["seg"]]
                c["t"] = round(s["t0"] + c.get("at", 0.0), 3)
                if key != "sfx" and "d" not in c:
                    c["d"] = round(s["t0"] + s["dur"] - c["t"], 3)
                if key != "sfx" and c.get("d") == "seg+":
                    # run through the following segment too
                    s2 = self.timeline[min(c["seg"] + 1, len(self.timeline) - 1)]
                    c["d"] = round(s2["t0"] + s2["dur"] - c["t"], 3)
        seg_t = lambda r: self.timeline[r["seg"]]["t0"] + r.get("at", 0.0) if "seg" in r else r["t"]
        lb = self.p.get("leaderboard")
        if lb:
            for r in lb["rows"]:
                r["t"] = seg_t(r)
            lb["rows"].sort(key=lambda r: r["t"])
        for e in (self.p.get("flag_row") or {}).get("events", []):
            e["t"] = seg_t(e)
        drops = self.p.get("music_drops", [])
        for i, d in enumerate(drops):
            if isinstance(d, dict):
                s = self.timeline[d["seg"]]
                end = s["t0"] + d["to"] if "to" in d else s["t0"] + s["dur"] + d.get("extend", 0.0)
                drops[i] = [s["t0"] + d.get("at", 0.0), end]
        m = self.p.get("music")
        if isinstance(m, list):
            for part in m:
                for k in ("from", "to"):
                    if isinstance(part.get(k), dict):
                        part[k] = self.timeline[part[k]["seg"]]["t0"] + part[k].get("at", 0.0)

    def run(self, out_mp4):
        total = self.build_timeline()
        self.resolve_times()
        self.prepare_text()
        print(f"  timeline {total:.2f}s, {len(self.timeline)} segments", flush=True)
        with tempfile.TemporaryDirectory() as td:
            v = os.path.join(td, "v.mp4")
            a = os.path.join(td, "a.wav")
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
