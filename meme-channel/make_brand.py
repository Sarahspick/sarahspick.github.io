"""Peak ProMax brand assets: profile picture and YouTube banner.

Run from meme-channel/:  python3 make_brand.py
Outputs brand/profile.png (800x800) and brand/banner.png (2560x1440).
Kept deliberately simple so it reads at 48px.
"""
from PIL import Image, ImageDraw, ImageFont

ANTON = "fonts/Anton.ttf"
BLACK = (12, 12, 14)
WHITE = (255, 255, 255)
ORANGE = (255, 92, 0)


def gradient(w, h, top, bottom):
    im = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(im)
    for y in range(h):
        k = y / (h - 1)
        d.line((0, y, w, y), fill=tuple(int(a + (b - a) * k) for a, b in zip(top, bottom)))
    return im


def centered(d, cx, y, text, f, fill):
    d.text((cx - d.textlength(text, font=f) / 2, y), text, font=f, fill=fill)


def profile():
    S = 800
    im = gradient(S, S, (255, 120, 0), (230, 20, 60))
    d = ImageDraw.Draw(im)
    d.polygon([(400, 120), (560, 330), (240, 330)], fill=WHITE)  # the peak
    centered(d, 400, 330, "PEAK", ImageFont.truetype(ANTON, 230), WHITE)
    im.save("brand/profile.png")


def banner():
    W, H = 2560, 1440
    im = Image.new("RGB", (W, H), BLACK)
    d = ImageDraw.Draw(im)
    sx0, sy0 = (W - 1546) // 2, (H - 423) // 2  # safe area on every device
    f = ImageFont.truetype(ANTON, 230)
    peak, pro = "PEAK ", "PROMAX"
    wp, wm = d.textlength(peak, font=f), d.textlength(pro, font=f)
    x = (W - wp - wm) / 2
    d.text((x, sy0 + 10), peak, font=f, fill=WHITE)
    d.text((x + wp, sy0 + 10), pro, font=f, fill=ORANGE)
    centered(d, W / 2, sy0 + 320, "only peak clips. zero mid.", ImageFont.truetype("fonts/Oswald.ttf", 64),
             (200, 200, 200))
    im.save("brand/banner.png")
    pv = im.copy()
    ImageDraw.Draw(pv).rectangle((sx0, sy0, sx0 + 1546, sy0 + 423), outline=(0, 255, 120), width=4)
    pv.resize((1280, 720)).save("brand/banner_safe_area_preview.jpg", quality=88)


if __name__ == "__main__":
    profile()
    banner()
    print("brand/profile.png, brand/banner.png")
