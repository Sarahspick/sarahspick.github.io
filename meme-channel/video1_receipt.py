"""Short #1: "POV: your aura receipt at the end of the day" (fully original)."""
import math
import random

from PIL import Image, ImageDraw

import sfx
from anim import (RED, back_out, camera, clamp, draw_rich, ease_out, emoji, font, paste_scaled, prog,
                  red_arrow, red_circle, render, stamp_img, text_w, wrap)

DUR = 15.0
REACT = 11.6
BG = (22, 16, 38)
PAPER = (250, 247, 238)
INK = (25, 25, 25)
GREEN = (20, 150, 70)

ITEMS = [
    ("Waved back at someone waving behind me", "-500"),
    ('Said "you too" when the waiter said enjoy your meal', "-300"),
    ("Pushed a door that clearly said PULL", "-200"),
    ("Laughed at a joke I didn't even hear", "-400"),
    ("Walked into the glass door at the gym 💀", "-1000"),
    ("Found $20 in old jeans", "+50"),
]
ITEM_T = [1.0, 2.1, 3.2, 4.3, 5.4, 8.0]
HL = 4  # highlighted item
TOTAL_T, STAMP_T = 9.2, 10.3
RW, PAD = 820, 46


def build_receipt():
    f_item, f_amt = font("Oswald.ttf", 40), font("Anton.ttf", 50)
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    rows, y = [], 250
    for text, amt in ITEMS:
        lines = wrap(probe, text, f_item, RW - 2 * PAD - 190)
        h = len(lines) * 50 + 30
        rows.append((lines, amt, y, h))
        y += h
    total_y = y + 30
    full_h = total_y + 330
    im = Image.new("RGBA", (RW, full_h), PAPER)
    d = ImageDraw.Draw(im)
    title = font("Anton.ttf", 84)
    d.text(((RW - d.textlength("AURA RECEIPT", font=title)) / 2, 30), "AURA RECEIPT", font=title, fill=INK)
    small = font("Oswald.ttf", 30)
    for i, s in enumerate(["STORE: your entire day", "10/05  11:59 PM   CASHIER: karma"]):
        d.text(((RW - d.textlength(s, font=small)) / 2, 142 + i * 38), s, font=small, fill=(90, 90, 90))
    for x in range(PAD, RW - PAD, 26):
        d.line((x, 232, x + 14, 232), fill=INK, width=3)
    for lines, amt, ry, h in rows:
        for j, ln in enumerate(lines):
            draw_rich(im, (PAD, ry + 8 + j * 50), ln, f_item, INK)
        col = GREEN if amt.startswith("+") else RED
        d.text((RW - PAD - d.textlength(amt, font=f_amt), ry + 6), amt, font=f_amt, fill=col)
    for x in range(PAD, RW - PAD, 26):
        d.line((x, total_y, x + 14, total_y), fill=INK, width=3)
    tf = font("Anton.ttf", 80)
    d.text((PAD, total_y + 24), "TOTAL", font=tf, fill=INK)
    d.text((RW - PAD - d.textlength("-2350", font=tf), total_y + 24), "-2350", font=tf, fill=RED)
    bx, by = PAD + 120, total_y + 160
    r = random.Random(4)
    while bx < RW - PAD - 120:
        bw = r.choice([4, 4, 8, 12])
        d.rectangle((bx, by, bx + bw, by + 80), fill=INK)
        bx += bw + r.choice([5, 7, 9])
    nf = font("Oswald.ttf", 30)
    s = "no refunds on aura"
    d.text(((RW - d.textlength(s, font=nf)) / 2, by + 95), s, font=nf, fill=INK)
    # zigzag tear at bottom
    zz = Image.new("RGBA", (RW, full_h + 24), (0, 0, 0, 0))
    zz.alpha_composite(im)
    zd = ImageDraw.Draw(zz)
    pts = [(0, full_h)]
    for k in range(0, RW + 24, 24):
        pts.append((k + 12, full_h + 22))
        pts.append((k + 24, full_h))
    zd.polygon(pts + [(RW, full_h)], fill=PAPER)
    stops = [ry + h for _, _, ry, h in rows] + [total_y + 130, full_h + 24]
    return zz, rows, total_y, stops


RECEIPT, ROWS, TOTAL_Y, STOPS = build_receipt()
STAMP = stamp_img("COOKED", size=170)
CRY = emoji("😭", 480)


_GLOW = {}


def glow(w, h, base, color, cy, rmax, xs):
    key = (w, h, base, color, cy, rmax, xs)
    if key not in _GLOW:
        im = Image.new("RGBA", (w, h), base + (255,))
        layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        for r in range(rmax, 60, -20):
            ring = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            ImageDraw.Draw(ring).ellipse((w / 2 - r * xs, cy - r, w / 2 + r * xs, cy + r),
                                         fill=color + (int(16 * (1 - r / rmax)),))
            layer.alpha_composite(ring)
        im.alpha_composite(layer)
        _GLOW[key] = im
    return _GLOW[key].copy()


def visible_len(t):
    """How much paper has come out of the printer at time t."""
    length = 0 if t < 0.3 else 240 * ease_out(prog(t, 0.3, 0.5))
    for i, ts in enumerate(ITEM_T):
        if t < ts:
            break
        start = STOPS[i - 1] if i else 240
        length = max(length, start + (STOPS[i] - start) * ease_out(prog(t, ts, 0.45)))
    if t >= TOTAL_T:
        last = STOPS[len(ITEMS) - 1]
        length = max(length, last + (STOPS[-2] - last) * ease_out(prog(t, TOTAL_T, 0.5)))
        length = max(length, STOPS[-2] + (STOPS[-1] - STOPS[-2]) * ease_out(prog(t, TOTAL_T + 0.5, 0.4)))
    return length


def receipt_scene(t, w, h):
    im = glow(w, h, BG, (124, 58, 237), h / 2, 520, 1.3)
    d = ImageDraw.Draw(im)
    slot_y = 60
    vis = visible_len(t)
    scroll = max(0, slot_y + vis - (h - 70))
    rx = (w - RW) // 2
    ry = slot_y + 14 - scroll
    paper = RECEIPT.crop((0, 0, RW, int(max(1, vis))))
    im.alpha_composite(paper, (rx, int(ry)))
    if scroll < slot_y + 40:
        d.rounded_rectangle((rx - 50, slot_y - 30 - scroll, rx + RW + 50, slot_y + 20 - scroll), radius=20,
                            fill=(60, 55, 75))
        d.rectangle((rx - 10, slot_y + 4 - scroll, rx + RW + 10, slot_y + 14 - scroll), fill=(10, 8, 16))
    # highlight on the gym door line
    _, _, hy, hh = ROWS[HL]
    box = (rx + 20, ry + hy - 10, rx + RW - 20, ry + hy + hh - 6)
    red_circle(im, box, prog(t, 5.95, 0.45))
    red_arrow(im, (rx + RW - 200, ry + hy + hh + 6), 55, 210, prog(t, 6.35, 0.3))
    if t >= TOTAL_T + 0.5:
        red_circle(im, (rx + RW - 330, ry + TOTAL_Y + 10, rx + RW - 10, ry + TOTAL_Y + 130),
                   prog(t, TOTAL_T + 0.6, 0.35), width=10)
    if t >= STAMP_T:
        p = prog(t, STAMP_T, 0.18)
        paste_scaled(im, STAMP, (w / 2 - 60, ry + TOTAL_Y + 170), 2.6 - 1.6 * ease_out(p), alpha=clamp(p * 3))
    # camera: punch in on the gym door line, then on the stamp
    zoom, focus, shake = 1.0, None, 0.0
    zin = ease_out(prog(t, 5.85, 0.25)) - ease_out(prog(t, 7.4, 0.35))
    if zin > 0:
        zoom, focus = 1 + 0.35 * zin, (w / 2, ry + hy + hh / 2 + 60)
    shake = 18 * max(0, 1 - (t - 5.9) / 0.5) if t >= 5.9 else 0
    if t >= STAMP_T:
        shake = max(shake, 26 * max(0, 1 - (t - STAMP_T - 0.15) / 0.5))
        zs = 0.18 * ease_out(prog(t, STAMP_T + 0.1, 0.2))
        zoom, focus = 1 + zs, (w / 2, ry + TOTAL_Y + 120)
    if 5.9 <= t < 6.0 or STAMP_T + 0.12 <= t < STAMP_T + 0.2:  # white flash
        im = Image.blend(im, Image.new("RGBA", im.size, (255, 255, 255, 255)), 0.55)
    return camera(im, zoom, focus, shake)


def reaction_scene(t, w, h):
    lt = t - REACT
    im = glow(w, h, (12, 10, 20), (60, 120, 255), h * 0.42, 600, 1.0)
    d = ImageDraw.Draw(im)
    s = back_out(prog(lt, 0.1, 0.45))
    wob = math.sin(lt * 9) * 6 * clamp(lt - 0.5)
    face = CRY.rotate(wob, expand=True, resample=Image.BICUBIC)
    paste_scaled(im, face, (w / 2, h * 0.40), s * (1 + 0.04 * math.sin(lt * 14)))
    if lt > 1.6:
        tf = font("Anton.ttf", 150)
        txt = "-2350 AURA"
        p = back_out(prog(lt, 1.6, 0.35))
        spr = Image.new("RGBA", (int(text_w(d, txt, tf)) + 60, 220), (0, 0, 0, 0))
        ImageDraw.Draw(spr).text((30, 10), txt, font=tf, fill=RED, stroke_width=10, stroke_fill=(255, 255, 255))
        paste_scaled(im, spr, (w / 2, h * 0.80), p)
    shake = 14 * clamp(1 - abs(lt - 1.75) / 0.4) + (6 if 1.95 < lt < 3.2 else 0)
    return camera(im, 1.0, None, shake)


def content(t, w, h):
    return reaction_scene(t, w, h) if t >= REACT else receipt_scene(t, w, h)


def caption(t):
    return "My honest reaction:" if t >= REACT else "POV: you get your aura receipt at the end of the day 😭🙏"


def audio():
    ev = [(0.25, sfx.whoosh(), 0.9)]
    for i, ts in enumerate(ITEM_T):
        ev.append((ts, sfx.printer(0.45), 0.7))
        ev.append((ts + 0.45, sfx.pop(), 0.8))
    ev += [(4.9, sfx.riser(1.0), 0.6), (5.9, sfx.boom(), 1.0), (6.35, sfx.whoosh(0.3), 0.8),
           (8.45, sfx.kaching(), 0.9), (TOTAL_T, sfx.printer(0.9), 0.7), (TOTAL_T - 0.1, sfx.heartbeat(2), 0.8),
           (TOTAL_T + 0.6, sfx.pop(), 0.8), (STAMP_T + 0.12, sfx.stamp(), 1.0), (STAMP_T + 0.12, sfx.boom(), 0.9),
           (REACT - 0.1, sfx.whoosh(0.35), 0.7), (REACT + 0.15, sfx.sad_trombone(), 1.0)]
    music = sfx.beat_loop(REACT - 0.2, bpm=104)
    music[int(5.85 * sfx.SR):int(7.4 * sfx.SR)] *= 0.25  # duck under the boom
    return ev, music


if __name__ == "__main__":
    import sys
    ev, music = audio()
    out = sys.argv[1] if len(sys.argv) > 1 else "out/01_aura_receipt.mp4"
    print(render(out, DUR, caption, content, ev, music))
