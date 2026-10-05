"""Aura Receipts brand assets: profile picture and YouTube banner.

Run from meme-channel/:  python3 make_brand.py
Outputs brand/profile.png (800x800) and brand/banner.png (2560x1440).
"""
import random
from PIL import Image, ImageDraw, ImageFont

F = "fonts/"
ANTON = F + "Anton.ttf"
OSWALD = F + "Oswald.ttf"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"

PAPER = (250, 247, 238)
INK = (20, 20, 20)
RED = (232, 30, 50)
PURPLE = (124, 58, 237)
BG = (14, 12, 22)


def font(path, size):
    return ImageFont.truetype(path, size)


def emoji(ch, size):
    """Noto Color Emoji only renders at 109px; draw there and scale."""
    f = ImageFont.truetype(EMOJI, 109)
    im = Image.new("RGBA", (136, 128), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((0, 0), ch, font=f, embedded_color=True)
    im = im.crop(im.getbbox())
    return im.resize((size, int(size * im.height / im.width)), Image.LANCZOS)


def zigzag(d, x0, x1, y, tooth, color, down=True):
    pts = [(x0, y)]
    x, up = x0, True
    while x < x1:
        x += tooth
        pts.append((min(x, x1), y + (tooth if (up == down) else 0)))
        up = not up
    pts.append((x1, y))
    d.polygon(pts, fill=color)


def center_text(d, cx, y, text, f, fill):
    w = d.textlength(text, font=f)
    d.text((cx - w / 2, y), text, font=f, fill=fill)


def receipt(w, h, lines, total, stamp=True, tilt=0):
    """A paper receipt card with zigzag bottom, returned as RGBA."""
    im = Image.new("RGBA", (w, h + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, h), fill=PAPER)
    zigzag(d, 0, w, h, 20, PAPER)
    pad = int(w * 0.08)
    y = int(h * 0.06)
    center_text(d, w / 2, y, "AURA RECEIPT", font(ANTON, int(w * 0.11)), INK)
    y += int(w * 0.16)
    d.line((pad, y, w - pad, y), fill=INK, width=3)
    y += int(w * 0.04)
    lf = font(OSWALD, int(w * 0.058))
    for left, right in lines:
        d.text((pad, y), left, font=lf, fill=INK)
        rw = d.textlength(right, font=lf)
        d.text((w - pad - rw, y), right, font=lf, fill=RED)
        y += int(w * 0.085)
    d.line((pad, y + 6, w - pad, y + 6), fill=INK, width=3)
    y += int(w * 0.04)
    tf = font(ANTON, int(w * 0.09))
    d.text((pad, y), "TOTAL", font=tf, fill=INK)
    tw = d.textlength(total, font=tf)
    d.text((w - pad - tw, y), total, font=tf, fill=RED)
    if stamp:
        s = Image.new("RGBA", (int(w * 0.8), int(w * 0.24)), (0, 0, 0, 0))
        sd = ImageDraw.Draw(s)
        sd.rounded_rectangle((4, 4, s.width - 4, s.height - 4), radius=14, outline=RED, width=8)
        center_text(sd, s.width / 2, s.height * 0.08, "COOKED", font(ANTON, int(s.height * 0.68)), RED)
        s = s.rotate(14, expand=True, resample=Image.BICUBIC)
        im.alpha_composite(s, (int(w * 0.10), y + int(w * 0.16)))
    # barcode + footer
    by = h - int(w * 0.30)
    rb = random.Random(3)
    x = pad
    while x < w - pad:
        bw = rb.choice([3, 3, 6, 9])
        d.rectangle((x, by, x + bw, by + int(w * 0.12)), fill=INK)
        x += bw + rb.choice([4, 6, 8])
    center_text(d, w / 2, by + int(w * 0.14), "no refunds on aura", font(OSWALD, int(w * 0.05)), INK)
    if tilt:
        im = im.rotate(tilt, expand=True, resample=Image.BICUBIC)
    return im


def profile():
    S = 800
    im = Image.new("RGBA", (S, S), BG)
    d = ImageDraw.Draw(im)
    # purple glow ring = "aura"
    for r in range(380, 200, -6):
        a = int(140 * (1 - (r - 200) / 180) ** 2)
        d.ellipse((S / 2 - r, S / 2 - r, S / 2 + r, S / 2 + r), fill=PURPLE + (a,))
    rc = receipt(420, 600, [("1 stairs", "-500"), ("1 bench press", "-1000")], "-1500", stamp=True, tilt=-3)
    im.alpha_composite(rc, ((S - rc.width) // 2, (S - rc.height) // 2 + 10))
    sk = emoji("\U0001F62D", 150)  # loudly crying face
    im.alpha_composite(sk, (S - 285, S - 300))
    im.convert("RGB").save("brand/profile.png")


def banner():
    W, H = 2560, 1440
    im = Image.new("RGBA", (W, H), BG)
    d = ImageDraw.Draw(im)
    rnd = random.Random(7)
    # scattered "-1000 AURA" ticker text in the outer (TV only) area
    tf = font(ANTON, 54)
    words = ["-1000 AURA", "+500 AURA", "COOKED", "NEW FEAR UNLOCKED", "MY HONEST REACTION:"]
    for row, y in enumerate(range(20, H, 95)):
        line = "   \u2022   ".join(words[(row + i) % 5] for i in range(14))
        d.text((-((row * 173) % 600), y), line, font=tf, fill=(34, 29, 52))
    sx0, sy0 = (W - 1546) // 2, (H - 423) // 2
    d.rectangle((0, sy0 - 40, W, sy0 + 463), fill=BG)
    # safe area for all devices: 1546x423 centered
    sx0, sy0 = (W - 1546) // 2, (H - 423) // 2
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for r in range(700, 100, -10):
        a = int(90 * (1 - (r - 100) / 600) ** 2)
        gd.ellipse((W / 2 - r * 1.6, H / 2 - r * 0.5, W / 2 + r * 1.6, H / 2 + r * 0.5), fill=PURPLE + (a,))
    im.alpha_composite(glow)
    d = ImageDraw.Draw(im)
    # left receipt
    rc = receipt(300, 440, [("1 stairs", "-500"), ("1 bench", "-1000")], "-1500", stamp=True, tilt=6)
    im.alpha_composite(rc, (sx0 + 10, sy0 - 15))
    # title
    title = font(ANTON, 170)
    cx = W / 2 + 120
    t1 = "AURA RECEIPTS"
    tw = d.textlength(t1, font=title)
    d.text((cx - tw / 2 + 8, sy0 + 20 + 8), t1, font=title, fill=RED)
    d.text((cx - tw / 2, sy0 + 20), t1, font=title, fill=(255, 255, 255))
    sub = font(OSWALD, 60)
    center_text(d, cx, sy0 + 225, "every clip, somebody pays.", sub, (220, 210, 255))
    # sticker: My honest reaction
    st = Image.new("RGBA", (540, 110), (0, 0, 0, 0))
    sd = ImageDraw.Draw(st)
    sd.rounded_rectangle((0, 0, 539, 109), radius=22, fill=(255, 255, 255))
    center_text(sd, 270, 14, "My honest reaction:", font(OSWALD, 58), INK)
    st = st.rotate(-5, expand=True, resample=Image.BICUBIC)
    im.alpha_composite(st, (int(cx - st.width / 2), sy0 + 320))
    im.alpha_composite(emoji("\U0001F62D", 80), (int(cx + st.width / 2) + 10, sy0 + 315))
    im.alpha_composite(emoji("\U0001F64F", 72), (int(cx - st.width / 2) - 95, sy0 + 320))
    im.convert("RGB").save("brand/banner.png")
    # preview with the mobile safe area marked
    pv = im.copy()
    ImageDraw.Draw(pv).rectangle((sx0, sy0, sx0 + 1546, sy0 + 423), outline=(0, 255, 120), width=4)
    pv.convert("RGB").resize((1280, 720)).save("brand/banner_safe_area_preview.jpg", quality=88)


if __name__ == "__main__":
    profile()
    banner()
    print("brand/profile.png, brand/banner.png")
