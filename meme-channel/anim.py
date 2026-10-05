"""Small animation kit for original Peak ProMax shorts.

Frames are drawn with Pillow and piped to ffmpeg, audio comes from sfx.py.
Layout matches meme_edit.py: 1080x1440, white caption bar on top.
"""
import math
import os
import random
import subprocess
import tempfile
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFont

import sfx
from meme_edit import EMOJI_FONT, H, HANDLE, W, caption_img, runs

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 30
RED = (235, 25, 40)


@lru_cache(None)
def font(name, size):
    return ImageFont.truetype(os.path.join(HERE, "fonts", name), size)


@lru_cache(None)
def emoji(ch, size):
    f = ImageFont.truetype(EMOJI_FONT, 109)
    im = Image.new("RGBA", (160, 136), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((0, 0), ch, font=f, embedded_color=True)
    im = im.crop(im.getbbox())
    return im.resize((size, size), Image.LANCZOS)


def text_w(d, text, f):
    size = f.size
    return sum(size if e else d.textlength(t, font=f) for e, t in runs(text))


def draw_rich(im, xy, text, f, fill):
    """Text with color emoji inline."""
    d = ImageDraw.Draw(im)
    x, y = xy
    for is_emoji, t in runs(text):
        if is_emoji:
            im.alpha_composite(emoji(t, f.size), (int(x), int(y + f.size * 0.15)))
            x += f.size
        else:
            d.text((x, y), t, font=f, fill=fill)
            x += d.textlength(t, font=f)
    return x


def wrap(d, text, f, maxw):
    lines, cur = [], ""
    for word in text.split(" "):
        test = (cur + " " + word).strip()
        if cur and text_w(d, test, f) > maxw:
            lines.append(cur)
            cur = word
        else:
            cur = test
    return lines + [cur]


# easing
def clamp(x):
    return max(0.0, min(1.0, x))


def prog(t, start, dur):
    return clamp((t - start) / dur)


def ease_out(p):
    return 1 - (1 - p) ** 3


def back_out(p, s=1.9):
    p -= 1
    return p * p * ((s + 1) * p + s) + 1


def red_circle(im, box, p, width=12):
    """Hand-drawn style ellipse that draws itself on as p goes 0 to 1."""
    if p <= 0:
        return
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = box
    cx, cy, rx, ry = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2, (y1 - y0) / 2
    pts = []
    total = 2.15 * math.pi  # overshoot like a real marker loop
    for i in range(int(120 * p) + 2):
        a = -2.3 + total * min(p, i / 120)
        wob = 1 + 0.05 * math.sin(a * 3) + 0.04 * (a / total)
        pts.append((cx + rx * wob * math.cos(a), cy + ry * wob * math.sin(a)))
    d.line(pts, fill=RED, width=width, joint="curve")


def red_arrow(im, tip, angle_deg, length, p, width=22):
    """Arrow pointing at tip, flying in from angle direction."""
    if p <= 0:
        return
    a = math.radians(angle_deg)
    off = (1 - ease_out(p)) * 260
    tx, ty = tip[0] + math.cos(a) * off, tip[1] + math.sin(a) * off
    sx, sy = tx + math.cos(a) * length, ty + math.sin(a) * length
    d = ImageDraw.Draw(im)
    hx, hy = tx + math.cos(a) * 60, ty + math.sin(a) * 60
    for col, wd in (((255, 255, 255), width + 12), (RED, width)):
        d.line((sx, sy, hx, hy), fill=col, width=wd)
        head = [(tx, ty),
                (tx + math.cos(a + 0.5) * 95, ty + math.sin(a + 0.5) * 95),
                (tx + math.cos(a - 0.5) * 95, ty + math.sin(a - 0.5) * 95)]
        if wd > width:
            cx, cy = sum(x for x, _ in head) / 3, sum(y for _, y in head) / 3
            head = [(cx + (x - cx) * 1.25, cy + (y - cy) * 1.25) for x, y in head]
        d.polygon(head, fill=col)


def stamp_img(text, color=RED, size=150, angle=-12):
    f = font("Anton.ttf", size)
    d = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    w = int(d.textlength(text, font=f)) + 80
    im = Image.new("RGBA", (w, int(size * 1.55)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((6, 6, w - 6, im.height - 6), radius=24, outline=color, width=14)
    d.text((40, size * 0.12), text, font=f, fill=color)
    return im.rotate(angle, expand=True, resample=Image.BICUBIC)


def paste_scaled(im, sprite, center, scale, alpha=1.0):
    if scale <= 0.01 or alpha <= 0:
        return
    s = sprite.resize((max(1, int(sprite.width * scale)), max(1, int(sprite.height * scale))), Image.BICUBIC)
    if alpha < 1:
        s.putalpha(s.getchannel("A").point(lambda v: int(v * alpha)))
    im.alpha_composite(s, (int(center[0] - s.width / 2), int(center[1] - s.height / 2)))


def camera(im, zoom=1.0, focus=None, shake=0.0, rnd=random.Random(0)):
    """Zoom toward focus and shake; returns same-size image."""
    w, h = im.size
    if zoom > 1.001:
        fx, fy = focus or (w / 2, h / 2)
        cw, ch = w / zoom, h / zoom
        x0 = min(max(fx - cw / 2, 0), w - cw)
        y0 = min(max(fy - ch / 2, 0), h - ch)
        im = im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((w, h), Image.BICUBIC)
    if shake > 0:
        dx, dy = rnd.uniform(-shake, shake), rnd.uniform(-shake, shake)
        im = im.transform((w, h), Image.AFFINE, (1, 0, -dx, 0, 1, -dy), resample=Image.BILINEAR,
                          fillcolor=im.getpixel((5, 5)))
    return im


@lru_cache(None)
def handle_sprite():
    im = Image.new("RGBA", (360, 50), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((0, 4), HANDLE, font=font("RobotoCond.ttf", 34), fill=(255, 255, 255, 130))
    return im


@lru_cache(None)
def cached_caption(text):
    return caption_img(text)


def render(out, dur, caption_at, content_at, audio_events, music=None):
    """caption_at(t) -> caption text; content_at(t, w, h) -> RGBA content image."""
    with tempfile.TemporaryDirectory() as tmp:
        wav = os.path.join(tmp, "a.wav")
        sfx.write_wav(wav, sfx.mix(dur, audio_events, music))
        p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                              "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav,
                              "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                              "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out],
                             stdin=subprocess.PIPE)
        for i in range(int(dur * FPS)):
            t = i / FPS
            cap = cached_caption(caption_at(t))
            frame = Image.new("RGBA", (W, H), (255, 255, 255, 255))
            content = content_at(t, W, H - cap.height)
            frame.alpha_composite(content, (0, cap.height))
            frame.alpha_composite(cap, (0, 0))
            frame.alpha_composite(handle_sprite(), (W - 210, H - 56))
            p.stdin.write(frame.convert("RGB").tobytes())
        p.stdin.close()
        p.wait()
    return out
