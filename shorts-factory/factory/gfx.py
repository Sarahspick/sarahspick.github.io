"""Static graphics: X-style post chrome, captions, hook title, annotation sprites, cards, slates."""
import functools
import io
import math
import os
import re

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from .config import W, H, THEMES, asset, rel

EMOJI_FONT = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
EMOJI_RE = re.compile("([\U0001F000-\U0001FAFF☀-➿⬀-⯿⌀-⏿])️?")

PAD_X = 48
HEADER_Y = 150
AVATAR = 108
MEDIA_MAX_W = 1020
MEDIA_MAX_H = 920
MEDIA_BOTTOM_LIMIT = 1560


@functools.lru_cache(maxsize=64)
def font(weight, size):
    for cand in (asset("fonts", f"Pretendard-{weight}.otf"), "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        if os.path.exists(cand):
            return ImageFont.truetype(cand, size)
    raise FileNotFoundError("no font; run tools/fetch_assets.py fonts")


@functools.lru_cache(maxsize=256)
def emoji_img(ch, size):
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
        import cairosvg  # needs the Cairo C library (present on most Linux boxes)
        return cairosvg.svg2png(bytestring=svg.encode(), output_width=size, output_height=size)


@functools.lru_cache(maxsize=64)
def _svg_icon(name, size, color):
    svg = open(asset("icons", name + ".svg"), encoding="utf-8").read()
    hexcol = "#%02x%02x%02x" % tuple(color[:3])
    svg = svg.replace("<path ", f'<path fill="{hexcol}" ')
    return Image.open(io.BytesIO(_svg_to_png(svg, size))).convert("RGBA")


def svg_icon(name, size, color):
    return _svg_icon(name, size, tuple(color[:3])).copy()


# ---------------------------------------------------------------- rich text
def parse_rich(text):
    """'*word*' marks highlighted spans. Returns [(token, highlighted)] split on spaces (spaces kept)."""
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
    w = 0
    for seg, is_emoji in _segments(tok):
        w += int(f.size * 1.08) + 4 if is_emoji else f.getlength(seg)
    return w


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
                img.alpha_composite(e, (int(x) + 2, int(y + asc - e.height * 0.86))) if img.mode == "RGBA" else img.paste(e, (int(x) + 2, int(y + asc - e.height * 0.86)), e)
                x += int(f.size * 1.08) + 4
            else:
                d.text((x, y), seg, font=f, fill=hl_color if hl else color, stroke_width=stroke, stroke_fill=stroke_fill)
                x += f.getlength(seg)
    return x


# ---------------------------------------------------------------- shapes
def rounded_mask(w, h, r, scale=3):
    m = Image.new("L", (w * scale, h * scale), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w * scale - 1, h * scale - 1), r * scale, fill=255)
    return m.resize((w, h), Image.LANCZOS)


def circle_crop(im, size):
    im = im.convert("RGBA")
    s = min(im.size)
    im = im.crop(((im.width - s) // 2, (im.height - s) // 2, (im.width + s) // 2, (im.height + s) // 2)).resize((size, size), Image.LANCZOS)
    m = Image.new("L", (size * 4, size * 4), 0)
    ImageDraw.Draw(m).ellipse((0, 0, size * 4 - 1, size * 4 - 1), fill=255)
    im.putalpha(m.resize((size, size), Image.LANCZOS))
    return im


def placeholder_avatar(size, theme):
    """Stand-in profile picture until the real one is dropped into assets/branding/avatar.png."""
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse((0, 0, size - 1, size - 1), fill=(196, 22, 28))
    ic = svg_icon("incognito", int(size * 0.62), (255, 255, 255))
    im.alpha_composite(ic, ((size - ic.width) // 2, (size - ic.height) // 2 + 2))
    return circle_crop(im, size)


# ---------------------------------------------------------------- page layout
class Page:
    """Computes the X-post geometry for one video and renders its static layers."""

    def __init__(self, channel, title):
        self.ch = channel
        self.t = THEMES[channel.get("theme", "dark")]
        self.title = title
        self.f_name = font("Bold", 46)
        self.f_handle = font("Regular", 38)
        self.f_title = font("Medium", 52)
        self.f_cap = font("Bold", 60)
        self.title_lines = wrap_runs(parse_rich(title), self.f_title, W - 2 * PAD_X)[:3]
        self.title_y = HEADER_Y + AVATAR + 34
        self.title_lh = 68
        self.cap_top = self.title_y + len(self.title_lines) * self.title_lh + 26
        self.cap_lh = 76
        self.cap_h = self.cap_lh * 2
        self.media_top = self.cap_top + self.cap_h + 22
        self.base = self._render_base()

    def media_box(self, aspect):
        max_h = min(MEDIA_MAX_H, MEDIA_BOTTOM_LIMIT - self.media_top)
        w = min(MEDIA_MAX_W, round(max_h * aspect))
        h = round(w / aspect)
        w -= w % 2
        h -= h % 2
        return ((W - w) // 2, self.media_top, w, h)

    def _render_base(self):
        t, ch = self.t, self.ch
        im = Image.new("RGBA", (W, H), t["bg"] + (255,))
        av_path = rel(ch.get("avatar", ""))
        av = circle_crop(Image.open(av_path), AVATAR) if os.path.exists(av_path) else placeholder_avatar(AVATAR, t)
        im.alpha_composite(av, (PAD_X, HEADER_Y))
        d = ImageDraw.Draw(im)
        x = PAD_X + AVATAR + 22
        d.text((x, HEADER_Y + 8), ch["name"], font=self.f_name, fill=t["text"])
        bx = x + self.f_name.getlength(ch["name"]) + 10
        badge = svg_icon("check-decagram", 48, t["badge"])
        im.alpha_composite(badge, (int(bx), HEADER_Y + 12))
        d.text((x, HEADER_Y + 62), ch["handle"], font=self.f_handle, fill=t["subtext"])
        dots = svg_icon("dots-horizontal", 52, t["subtext"])
        im.alpha_composite(dots, (W - PAD_X - 52, HEADER_Y + 10))
        y = self.title_y
        for ln in self.title_lines:
            draw_runs(im, PAD_X, y, ln, self.f_title, t["text"], t["caption_hl"])
            y += self.title_lh
        return im

    CAP_MAX_W = W - 2 * 36

    def caption_font(self, lines):
        """Largest caption size (60 -> 50 px) at which every line of the sentence fits on one row."""
        for size in range(60, 49, -2):
            f = font("Bold", size)
            if all(runs_width(parse_rich(ln), f) <= self.CAP_MAX_W for ln in lines):
                return f, True
        return font("Bold", 50), False

    def caption_layer(self, lines, n_visible):
        """Caption zone image (W x cap_h): the sentence's lines revealed so far, newest two rows visible."""
        t = self.t
        f, _ = self.caption_font(lines)
        im = Image.new("RGBA", (W, self.cap_h), t["bg"] + (255,))
        rows = []
        for ln in lines[:n_visible]:
            rows.extend(wrap_runs(parse_rich(ln), f, self.CAP_MAX_W))
        rows = rows[-2:]
        y0 = 0 if len(rows) == 2 else self.cap_lh // 2
        dy = (60 - f.size) // 2
        for i, r in enumerate(rows):
            wdt = runs_width(r, f)
            draw_runs(im, (W - wdt) / 2, y0 + i * self.cap_lh + dy, r, f, t["caption"], t["caption_hl"])
        return im

    def media_frame_decor(self, box):
        """Rounded mask + 2px border ring for a media box size."""
        x, y, w, h = box
        mask = rounded_mask(w, h, 26)
        ring = Image.new("RGBA", (w + 4, h + 4), (0, 0, 0, 0))
        ImageDraw.Draw(ring).rounded_rectangle((0, 0, w + 3, h + 3), 28, outline=self.t["border"] + (255,), width=2)
        return mask, ring

    def hook_overlay(self, big_lines, box):
        """Dim everything except the media box, then stamp the huge two-line title on top."""
        t = self.t
        ov = Image.new("RGBA", (W, H), (0, 0, 0, int(255 * t["dim"])))
        x, y, w, h = box
        a = ov.getchannel("A")
        a.paste(Image.new("L", (W, y), int(255 * 0.9)), (0, 0))   # title band: hide the post text under it
        a.paste(Image.new("L", (w, h), 0), (x, y))                # media stays bright
        ov.putalpha(a)
        size = 124
        while True:
            f = font("Black", size)
            rows = []
            for i, ln in enumerate(big_lines):
                for r in wrap_runs(parse_rich(ln), f, W - 60):
                    rows.append((r, i))
            if len(rows) == len(big_lines) or size <= 78:
                break
            size -= 4
        lh = int(size * 1.12)
        block = lh * len(rows)
        region_top, region_bot = HEADER_Y - 20, self.media_top - 24
        y0 = region_top + max(0, (region_bot - region_top - block) // 2)
        for j, (r, i) in enumerate(rows):
            wdt = runs_width(r, f)
            col = t["hook_1"] if i == 0 else t["hook_2"]
            draw_runs(ov, (W - wdt) / 2, y0 + j * lh, r, f, col, t["hook_2"], stroke=max(6, size // 10), stroke_fill=t["stroke"])
        return ov


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
    sh = sh.filter(ImageFilter.GaussianBlur(6 * s))
    im.alpha_composite(sh)
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
    tip_rot = (tip[0] * math.cos(rad), tip[0] * math.sin(rad))
    return rot, (rot.width / 2 + tip_rot[0], rot.height / 2 + tip_rot[1])


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
    # MDI cursor tip sits at roughly (29%, 12%) of the icon box
    return im, (black.width * 0.29, black.height * 0.12)


def stamp_sprite(text="CLASSIFIED", color=(225, 30, 45)):
    f = font("Black", 92)
    tw = int(f.getlength(text))
    s = Image.new("RGBA", (tw + 90, 170), (0, 0, 0, 0))
    d = ImageDraw.Draw(s)
    d.rounded_rectangle((6, 6, s.width - 7, s.height - 7), 18, outline=tuple(color) + (255,), width=12)
    d.text((45, 30), text, font=f, fill=tuple(color) + (255,))
    return s.rotate(-12, resample=Image.BICUBIC, expand=True)


# ---------------------------------------------------------------- cards & slates
def card_image(w, h, theme, outlet, headline, date="", kind="report"):
    """Citation card: who said it, when, and the claim (our own paraphrase or a short quote)."""
    t = THEMES[theme]
    im = Image.new("RGBA", (w, h), t["card_bg"] + (255,))
    pw, ph = int(w * 0.88), int(h * 0.78)
    px, py = (w - pw) // 2, (h - ph) // 2
    paper = Image.new("RGBA", (pw, ph), (255, 255, 255, 255))
    d = ImageDraw.Draw(paper)
    tag = {"report": "REPORT", "quote": "STATEMENT", "news": "NEWS", "fact": "FACT"}.get(kind, kind.upper())
    ft = font("Black", 30)
    tagw = int(ft.getlength(tag)) + 36
    d.rounded_rectangle((40, 40, 40 + tagw, 88), 10, fill=(225, 30, 45))
    d.text((58, 46), tag, font=ft, fill=(255, 255, 255))
    fo = font("Bold", 34)
    d.text((40, 108), outlet + (f"  ·  {date}" if date else ""), font=fo, fill=(83, 100, 113))
    size = 84
    while True:
        fh = font("ExtraBold", size)
        rows = wrap_runs(parse_rich(headline), fh, pw - 80)
        if len(rows) * int(size * 1.28) <= ph - 210 or size <= 34:
            break
        size -= 2
    y = 170 + max(0, (ph - 210 - len(rows) * int(size * 1.28)) // 3)
    for r in rows:
        draw_runs(paper, 40, y, r, fh, (15, 20, 25), (225, 30, 45))
        y += int(fh.size * 1.28)
    sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((px + 8, py + 14, px + pw + 8, py + ph + 14), 22, fill=(0, 0, 0, 120))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    im.paste(paper, (px, py), rounded_mask(pw, ph, 22))
    return im.convert("RGB")


def slate_image(w, h, desc, src_hint=""):
    """Storyboard placeholder shown where real footage is missing (no network access to the source)."""
    im = Image.new("RGB", (w, h), (18, 22, 30))
    d = ImageDraw.Draw(im)
    for i in range(h):
        k = i / h
        d.line([(0, i), (w, i)], fill=(int(28 - 14 * k), int(34 - 16 * k), int(48 - 22 * k)))
    stripes = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stripes)
    for x in range(-h, w, 46):
        sd.line([(x, h), (x + h, 0)], fill=(255, 255, 255, 12), width=16)
    im = Image.alpha_composite(im.convert("RGBA"), stripes)
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
        rw = runs_width(r, fd)
        draw_runs(im, (w - rw) / 2, y, r, fd, (240, 240, 240), (255, 212, 0))
        y += 64
    if src_hint:
        fs = font("Medium", 26)
        rows = wrap_runs(parse_rich(src_hint), fs, w - 80)[:2]
        y = h - 40 - 34 * len(rows)
        for r in rows:
            rw = runs_width(r, fs)
            draw_runs(im, (w - rw) / 2, y, r, fs, (150, 160, 175), (150, 160, 175))
            y += 34
    return im.convert("RGB")
