"""Graphics for the classic Shorts look: blurred same-clip background, full-width foreground clip,
top headline, big word-chunk captions, annotation sprites, citation cards and placeholder slates."""
import functools
import io
import math
import os
import re

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from .config import W, H, THEMES, asset

EMOJI_FONT = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
EMOJI_RE = re.compile("([\U0001F000-\U0001FAFF☀-➿⬀-⯿⌀-⏿])️?")

TITLE_TOP = 118          # headline block starts here
TITLE_MAX_W = W - 70
CAPTION_CY = H // 2      # captions sit in the exact centre of the frame (user rule, 2026-09-30)
CAPTION_MAX_W = W - 80
YELLOW = (255, 214, 0)
ACCENT = YELLOW          # highlight colour; each channel sets its own with set_accent()


def hex_rgb(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def set_accent(color):
    """Channel theme colour for highlighted words (headline, captions, labels)."""
    global ACCENT
    ACCENT = hex_rgb(color) if isinstance(color, str) else tuple(color)
    caption_image.cache_clear()


@functools.lru_cache(maxsize=64)
def font(weight, size):
    for cand in (asset("fonts", f"Pretendard-{weight}.otf"), "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        if os.path.exists(cand):
            return ImageFont.truetype(cand, size)
    raise FileNotFoundError("no font; run tools/fetch_assets.py fonts")


@functools.lru_cache(maxsize=256)
def emoji_img(ch, size):
    if not os.path.exists(EMOJI_FONT):
        return Image.new("RGBA", (1, 1))
    f = ImageFont.truetype(EMOJI_FONT, 109)
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((8, 8), ch, font=f, embedded_color=True)
    im = im.crop(im.getbbox() or (0, 0, 1, 1))
    s = size / max(im.size)
    return im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)


def _svg_to_png(svg, size):
    try:  # pure wheels on every OS
        import resvg_py
        return bytes(resvg_py.svg_to_bytes(svg_string=svg, width=size, height=size))
    except ImportError:
        import cairosvg  # needs the Cairo C library
        return cairosvg.svg2png(bytestring=svg.encode(), output_width=size, output_height=size)


@functools.lru_cache(maxsize=64)
def _svg_icon(name, size, color):
    svg = open(asset("icons", name + ".svg"), encoding="utf-8").read()
    svg = svg.replace("<path ", '<path fill="#%02x%02x%02x" ' % color)
    return Image.open(io.BytesIO(_svg_to_png(svg, size))).convert("RGBA")


def svg_icon(name, size, color):
    return _svg_icon(name, size, tuple(color[:3])).copy()


# ---------------------------------------------------------------- rich text
def parse_rich(text):
    """'*word*' marks highlighted spans. Returns [(token, highlighted)] with spaces as their own tokens."""
    out, hl = [], False
    for part in re.split(r"(\*)", text):
        if part == "*":
            hl = not hl
            continue
        for tok in re.split(r"( )", part):
            if tok:
                out.append((tok, hl))
    return out


def plain(text):
    return text.replace("*", "")


def _segments(tok):
    pos = 0
    for m in EMOJI_RE.finditer(tok):
        if m.start() > pos:
            yield tok[pos:m.start()], False
        yield m.group(1), True
        pos = m.end()
    if pos < len(tok):
        yield tok[pos:], False


def tok_width(tok, f):
    return sum(int(f.size * 1.08) + 4 if e else f.getlength(s) for s, e in _segments(tok))


def runs_width(runs, f):
    return sum(tok_width(t, f) for t, _ in runs)


def wrap_runs(runs, f, max_w):
    """Greedy wrap that only breaks at spaces (a highlighted word keeps its trailing punctuation)."""
    words, cur = [], []
    for tok, hl in runs:
        if tok == " ":
            if cur:
                words.append(cur)
                cur = []
        else:
            cur.append((tok, hl))
    if cur:
        words.append(cur)
    lines, line = [], []
    for w in words:
        trial = line + ([(" ", False)] if line else []) + w
        if line and runs_width(trial, f) > max_w:
            lines.append(line)
            line = list(w)
        else:
            line = trial
    if line:
        lines.append(line)
    return lines


def draw_runs(img, x, y, runs, f, color, hl_color, stroke=0, stroke_fill=(0, 0, 0)):
    d = ImageDraw.Draw(img)
    asc, _ = f.getmetrics()
    for tok, hl in runs:
        for seg, is_emoji in _segments(tok):
            if is_emoji:
                e = emoji_img(seg, int(f.size * 1.08))
                img.alpha_composite(e, (int(x) + 2, int(y + asc - e.height * 0.86)))
                x += int(f.size * 1.08) + 4
            else:
                d.text((x, y), seg, font=f, fill=hl_color if hl else color, stroke_width=stroke, stroke_fill=stroke_fill)
                x += f.getlength(seg)
    return x


def stroked_block(rows, f, color, hl_color, stroke, align="center", line_gap=1.12, shadow=True):
    """Render rows of runs as one RGBA image with thick outline and a soft drop shadow."""
    lh = int(f.size * line_gap)
    width = int(max(runs_width(r, f) for r in rows)) + 2 * stroke + 24
    height = lh * len(rows) + 2 * stroke + 30
    txt = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    for i, r in enumerate(rows):
        rw = runs_width(r, f)
        x = (width - rw) / 2 if align == "center" else stroke + 12
        draw_runs(txt, x, stroke + 6 + i * lh, r, f, color, hl_color, stroke=stroke)
    if not shadow:
        return txt
    sh = Image.new("RGBA", txt.size, (0, 0, 0, 0))
    sh.putalpha(txt.getchannel("A").point(lambda v: int(v * 0.55)))
    sh = sh.filter(ImageFilter.GaussianBlur(9))
    out = Image.new("RGBA", (width, height + 10), (0, 0, 0, 0))
    out.alpha_composite(sh, (0, 8))
    out.alpha_composite(txt, (0, 0))
    return out


# ---------------------------------------------------------------- layout
def title_layer(title, theme="dark"):
    """Headline pinned to the top of the frame for the whole video (the 'classic' top text)."""
    runs = parse_rich(title)
    for size in range(78, 51, -2):
        f = font("Black", size)
        rows = wrap_runs(runs, f, TITLE_MAX_W)
        if len(rows) <= 2:
            break
    img = stroked_block(rows, f, (255, 255, 255), ACCENT, stroke=max(7, size // 9))
    layer = Image.new("RGBA", (W, TITLE_TOP + img.height), (0, 0, 0, 0))
    layer.alpha_composite(img, ((W - img.width) // 2, TITLE_TOP))
    bottom = TITLE_TOP + int(size * 1.12) * len(rows) + 12
    return layer, bottom


def fg_box(aspect, title_bottom):
    """Foreground clip rectangle: full width, centred a little low so the headline has room above."""
    if aspect <= 9 / 16 + 0.02:
        return (0, 0, W, H)
    w = W
    h = int(round(w / aspect)) // 2 * 2
    y = max(title_bottom + 26, (H - h) // 2 + 40)
    y = min(y, H - h)
    return (0, y, w, h)


def blurred_bg(frame):
    """Same-clip background: cover-scale to 9:16, heavy blur, darken. Done at 1/18 scale for speed."""
    sw, sh = W // 18, H // 18
    fw, fh = frame.size
    s = max(sw / fw, sh / fh)
    small = frame.resize((max(sw, int(fw * s + 1)), max(sh, int(fh * s + 1))), Image.BILINEAR)
    x0, y0 = (small.width - sw) // 2, (small.height - sh) // 2
    small = small.crop((x0, y0, x0 + sw, y0 + sh)).filter(ImageFilter.GaussianBlur(2.2))
    arr = (np.asarray(small, np.float32) * 0.5).astype(np.uint8)
    return Image.fromarray(arr).resize((W, H), Image.BICUBIC)


@functools.lru_cache(maxsize=512)
def caption_image(words, max_w=CAPTION_MAX_W):
    """words: tuple of (text, highlighted). Big outlined caption chunk as RGBA."""
    runs = []
    for i, (t, hl) in enumerate(words):
        if i:
            runs.append((" ", False))
        runs.append((t, hl))
    for size in range(96, 63, -3):
        f = font("Black", size)
        if runs_width(runs, f) <= max_w:
            break
    rows = wrap_runs(runs, f, max_w)
    return stroked_block(rows, f, (255, 255, 255), ACCENT, stroke=max(8, size // 9))


# ---------------------------------------------------------------- sprites
def arrow_sprite(length=230, color=(255, 45, 45), angle=0):
    """Fat red arrow pointing along `angle` degrees (0 = right, 90 = down). Returns (img, tip_offset)."""
    s = 3
    L, t, hw, hl = length * s, 54 * s, 128 * s, 96 * s
    pad = 26 * s
    im = Image.new("RGBA", (L + 2 * pad, hw + 2 * pad), (0, 0, 0, 0))
    cy = im.height // 2
    pts = [(pad, cy - t // 2), (pad + L - hl, cy - t // 2), (pad + L - hl, cy - hw // 2), (pad + L, cy),
           (pad + L - hl, cy + hw // 2), (pad + L - hl, cy + t // 2), (pad, cy + t // 2)]
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).polygon([(px + 6 * s, py + 8 * s) for px, py in pts], fill=(0, 0, 0, 150))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6 * s)))
    d = ImageDraw.Draw(im)
    d.polygon(pts, fill=(255, 255, 255, 255))
    inner = [(pad + 9 * s, cy - t // 2 + 9 * s), (pad + L - hl + 9 * s, cy - t // 2 + 9 * s), (pad + L - hl + 9 * s, cy - hw // 2 + 26 * s),
             (pad + L - 17 * s, cy), (pad + L - hl + 9 * s, cy + hw // 2 - 26 * s), (pad + L - hl + 9 * s, cy + t // 2 - 9 * s),
             (pad + 9 * s, cy + t // 2 - 9 * s)]
    d.polygon(inner, fill=tuple(color) + (255,))
    im = im.resize((im.width // s, im.height // s), Image.LANCZOS)
    tip = (pad // s + L // s - im.width / 2, 0)
    rot = im.rotate(-angle, resample=Image.BICUBIC, expand=True)
    rad = math.radians(angle)
    return rot, (rot.width / 2 + tip[0] * math.cos(rad), rot.height / 2 + tip[0] * math.sin(rad))


def ring_sprite(r, color=(255, 45, 45), width=12):
    s = 3
    im = Image.new("RGBA", ((2 * r + 40) * s,) * 2, (0, 0, 0, 0))
    c = im.width // 2
    d = ImageDraw.Draw(im)
    d.ellipse((c - r * s - 4 * s, c - r * s - 4 * s, c + r * s + 4 * s, c + r * s + 4 * s), outline=(255, 255, 255, 255), width=(width + 8) * s)
    d.ellipse((c - r * s, c - r * s, c + r * s, c + r * s), outline=tuple(color) + (255,), width=width * s)
    return im.resize((im.width // s, im.height // s), Image.LANCZOS)


def cursor_sprite(size=96):
    black = svg_icon("cursor-default", size + 14, (0, 0, 0))
    white = svg_icon("cursor-default", size, (255, 255, 255))
    im = Image.new("RGBA", black.size, (0, 0, 0, 0))
    im.alpha_composite(black)
    im.alpha_composite(white, (6, 8))
    return im, (black.width * 0.29, black.height * 0.12)


def stamp_sprite(text="CLASSIFIED", color=(225, 30, 45), max_w=620):
    """Rubber-stamp sprite; long words shrink so the stamp never exceeds max_w before rotation."""
    size = 92
    tw = font("Black", size).getlength(text)
    if tw + 90 > max_w:
        size = max(48, int(size * (max_w - 90) / tw))
    k = size / 92
    f = font("Black", size)
    tw = int(f.getlength(text))
    pad, h = int(45 * k), int(170 * k)
    s = Image.new("RGBA", (tw + 2 * pad, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(s)
    d.rounded_rectangle((6, 6, s.width - 7, s.height - 7), int(18 * k), outline=tuple(color) + (255,), width=max(6, int(12 * k)))
    d.text((pad, int(30 * k)), text, font=f, fill=tuple(color) + (255,))
    return s.rotate(-12, resample=Image.BICUBIC, expand=True)


def rounded_mask(w, h, r, scale=3):
    m = Image.new("L", (w * scale, h * scale), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w * scale - 1, h * scale - 1), r * scale, fill=255)
    return m.resize((w, h), Image.LANCZOS)


# ---------------------------------------------------------------- cards & slates
def card_image(w, h, theme, outlet, headline, date="", kind="report"):
    """Citation card: who said it, when, and the claim (our own paraphrase or a short quote)."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    # paper sits in the upper ~75% of the box so the caption chunk below never covers the headline
    pw, ph = int(w * 0.9), int(h * 0.7)
    px, py = (w - pw) // 2, int(h * 0.05)
    paper = Image.new("RGBA", (pw, ph), (255, 255, 255, 255))
    d = ImageDraw.Draw(paper)
    tag = {"report": "REPORT", "quote": "STATEMENT", "news": "NEWS", "fact": "FACT"}.get(kind, kind.upper())
    ft = font("Black", 34)
    tagw = int(ft.getlength(tag)) + 40
    d.rounded_rectangle((44, 44, 44 + tagw, 98), 12, fill=(225, 30, 45))
    d.text((64, 50), tag, font=ft, fill=(255, 255, 255))
    fo = font("Bold", 38)
    d.text((44, 120), outlet + (f"  ·  {date}" if date else ""), font=fo, fill=(83, 100, 113))
    size = 96
    while True:
        fh = font("ExtraBold", size)
        rows = wrap_runs(parse_rich(headline), fh, pw - 88)
        if len(rows) * int(size * 1.25) <= ph - 230 or size <= 38:
            break
        size -= 2
    y = 190 + max(0, (ph - 230 - len(rows) * int(size * 1.25)) // 3)
    for r in rows:
        draw_runs(paper, 44, y, r, fh, (15, 20, 25), (225, 30, 45))
        y += int(size * 1.25)
    sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((px + 10, py + 16, px + pw + 10, py + ph + 16), 26, fill=(0, 0, 0, 150))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)))
    im.paste(paper, (px, py), rounded_mask(pw, ph, 26))
    return im


def slate_image(w, h, desc, src_hint=""):
    """Storyboard placeholder shown where real footage is missing."""
    im = Image.new("RGB", (w, h), (18, 22, 30))
    d = ImageDraw.Draw(im)
    for i in range(h):
        k = i / h
        d.line([(0, i), (w, i)], fill=(int(28 - 14 * k), int(34 - 16 * k), int(48 - 22 * k)))
    im = im.convert("RGBA")
    d = ImageDraw.Draw(im)
    fl = font("Black", 30)
    label = "SOURCE FOOTAGE GOES HERE"
    lw = fl.getlength(label)
    d.rounded_rectangle(((w - lw) / 2 - 22, 38, (w + lw) / 2 + 22, 88), 12, fill=(255, 212, 0))
    d.text(((w - lw) / 2, 45), label, font=fl, fill=(0, 0, 0))
    fd = font("ExtraBold", 50)
    rows = wrap_runs(parse_rich(desc), fd, w - 110)
    y = (h - len(rows) * 64) / 2
    for r in rows:
        draw_runs(im, (w - runs_width(r, fd)) / 2, y, r, fd, (240, 240, 240), (255, 212, 0))
        y += 64
    if src_hint:
        fs = font("Medium", 26)
        for r in wrap_runs(parse_rich(src_hint), fs, w - 80)[:2]:
            draw_runs(im, (w - runs_width(r, fs)) / 2, h - 90, r, fs, (150, 160, 175), (150, 160, 175))
    return im.convert("RGB")
