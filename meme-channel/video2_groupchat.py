"""Short #2: "Bro really thought he could lie in the group chat" (fully original)."""
import math

from PIL import Image, ImageDraw

import sfx
from anim import (RED, back_out, camera, clamp, draw_rich, ease_out, font, paste_scaled, prog, red_arrow,
                  red_circle, render, stamp_img, text_w, wrap)

DUR = 17.0
BG = (242, 242, 247)
GRAY = (229, 229, 234)
BLUE = (10, 132, 255)
F = font("RobotoCond.ttf", 60)
F_NAME = font("RobotoCond.ttf", 34)
F_QUOTE = font("RobotoCond.ttf", 40)
MAXW = 720

# (time, sender, text, extra)
MSGS = [
    (0.6, "Jay", "who ate my leftover pizza 🍕", None),
    (1.7, "Sam", "not me", None),
    (2.7, "Mike", "bro i was asleep by 10 last night 😴", None),
    (4.0, "Jay", "then explain this 🤨", ("Mike", "Yesterday 3:12 AM", "yo is the pizza in the fridge still good 👀")),
    (9.0, "Mike", "that was my twin", None),
    (10.0, "Jay", "you don't have a twin", None),
    (11.6, "Mike", "he's very private", None),
    (12.9, "system", "Mike left the group", None),
]
TYPING = [(7.4, 9.0), (10.6, 11.6)]
HL_T, ARROW_T, ZOOM_OUT = 5.4, 5.9, 7.2
STAMP_T = 14.4
STAMP = stamp_img("-1000 AURA", size=140, angle=-10)
COLORS = {"Sam": (255, 149, 0), "Mike": (52, 199, 89)}

_probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))


def layout():
    """Positions every message once; returns list of dicts and the 3:12 AM box."""
    out, y, hl = [], 150, None
    for t, who, text, quote in MSGS:
        if who == "system":
            out.append(dict(t=t, who=who, text=text, y=y + 10, h=60))
            y += 90
            continue
        lines = wrap(_probe, text, F, MAXW)
        tw = max(text_w(_probe, ln, F) for ln in lines)
        bh = len(lines) * 72 + 40
        qh = 0
        if quote:
            qw = max(text_w(_probe, quote[2], F_QUOTE), _probe.textlength(quote[0] + " · " + quote[1], font=F_NAME))
            tw = max(tw, qw + 100)
            qh = 140
        bw = tw + 56
        name_h = 0 if who == "Jay" else 38
        me = who == "Jay"
        x = 1080 - 40 - bw if me else 40
        m = dict(t=t, who=who, lines=lines, quote=quote, x=x, y=y + name_h, w=bw, h=bh + qh, qh=qh, me=me,
                 name_y=y)
        if quote:
            stamp_x = x + 46 + _probe.textlength(quote[0] + " · Yesterday ", font=F_NAME)
            hl = (stamp_x - 26, m["y"] + 12, stamp_x + _probe.textlength("3:12 AM", font=F_NAME) + 26,
                  m["y"] + 72)
        out.append(m)
        y += name_h + bh + qh + 22
    return out, hl


LAYOUT, HL_BOX = layout()


def bubble(im, m, p):
    """Draw one message; p is its pop-in progress."""
    if p <= 0:
        return
    if m["who"] == "system":
        layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        s = m["text"]
        sf = font("RobotoCond.ttf", 40)
        d.text(((1080 - d.textlength(s, font=sf)) / 2, m["y"]), s, font=sf,
               fill=(142, 142, 147, int(255 * clamp(p * 2))))
        im.alpha_composite(layer)
        return
    spr = Image.new("RGBA", (int(m["w"]), int(m["h"])), (0, 0, 0, 0))
    d = ImageDraw.Draw(spr)
    d.rounded_rectangle((0, 0, m["w"] - 1, m["h"] - 1), radius=40, fill=BLUE if m["me"] else GRAY)
    fg = (255, 255, 255) if m["me"] else (0, 0, 0)
    y = 18
    if m["quote"]:
        q = m["quote"]
        d.rounded_rectangle((16, 14, m["w"] - 16, 14 + m["qh"] - 14), radius=22, fill=(0, 95, 210))
        d.rectangle((16, 22, 24, m["qh"] - 8), fill=(255, 255, 255))
        d.text((40, 24), f"{q[0]} · {q[1]}", font=F_NAME, fill=(200, 225, 255))
        draw_rich(spr, (40, 64), q[2], F_QUOTE, (255, 255, 255))
        y += m["qh"]
    for ln in m["lines"]:
        draw_rich(spr, (28, y), ln, F, fg)
        y += 72
    s = back_out(clamp(p))
    anchor_x = m["x"] + (m["w"] if m["me"] else 0)
    sw, sh = max(1, int(spr.width * s)), max(1, int(spr.height * s))
    spr = spr.resize((sw, sh), Image.BICUBIC)
    px = anchor_x - sw if m["me"] else anchor_x
    im.alpha_composite(spr, (int(px), int(m["y"] + m["h"] - sh)))
    if not m["me"] and p > 0.3:
        ImageDraw.Draw(im).text((m["x"] + 22, m["name_y"]), m["who"], font=F_NAME, fill=COLORS[m["who"]])


def typing(im, y, t0, t):
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((40, y, 200, y + 84), radius=40, fill=GRAY)
    for k in range(3):
        a = 0.5 + 0.5 * math.sin((t - t0) * 9 - k * 0.9)
        r = 9 + 3 * a
        cx, cy = 82 + k * 38, y + 42 - 6 * a
        g = int(150 - 60 * a)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(g, g, g))


def bottom_at(t):
    b = 0
    for m in LAYOUT:
        if t >= m["t"]:
            b = m["y"] + m["h"]
    for t0, t1 in TYPING:
        if t0 <= t < t1:
            b += 22 + 38 + 84
    return b


def content(t, w, h):
    head = 150
    im = Image.new("RGBA", (w, h), BG + (255,))
    chat_h = h - head
    scroll = smooth_scroll(t, chat_h)
    chat = Image.new("RGBA", (w, int(max(chat_h, bottom_at(DUR) + 300))), BG + (255,))
    for m in LAYOUT:
        bubble(chat, m, prog(t, m["t"], 0.28))
    for t0, t1 in TYPING:
        if t0 <= t < t1:
            last = [m for m in LAYOUT if m["t"] <= t][-1]
            y = last["y"] + last["h"] + 22
            ImageDraw.Draw(chat).text((62, y), "Mike", font=F_NAME, fill=COLORS["Mike"])
            typing(chat, y + 38, t0, t)
    red_circle(chat, HL_BOX, prog(t, HL_T, 0.4), width=9)
    tip = ((HL_BOX[0] + HL_BOX[2]) / 2 - 20, HL_BOX[1] - 4)
    if t < ZOOM_OUT + 0.2:
        red_arrow(chat, tip, -115, 200, prog(t, ARROW_T, 0.3), width=18)
    view = chat.crop((0, int(scroll), w, int(scroll) + chat_h))
    im.alpha_composite(view, (0, head))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, head), fill=(250, 250, 252))
    d.line((0, head, w, head), fill=(210, 210, 215), width=2)
    d.ellipse((w / 2 - 34, 14, w / 2 + 34, 82), fill=(190, 190, 200))
    draw_rich(im, (w / 2 - 24, 24), "🏠", font("RobotoCond.ttf", 40), (0, 0, 0))
    title = "Apartment 4B  >"
    tf = font("RobotoCond.ttf", 34)
    d.text(((w - d.textlength(title, font=tf)) / 2, 92), title, font=tf, fill=(0, 0, 0))
    d.text((34, 40), "<", font=font("RobotoCond.ttf", 60), fill=BLUE)
    # camera
    zin = ease_out(prog(t, HL_T - 0.1, 0.25)) - ease_out(prog(t, ZOOM_OUT, 0.35))
    zoom, focus = 1 + 0.55 * zin, ((HL_BOX[0] + HL_BOX[2]) / 2, head + HL_BOX[1] - scroll + 60)
    shake = 16 * max(0, 1 - (t - HL_T) / 0.45) if t >= HL_T else 0
    if t >= 11.65:
        shake = max(shake, 10 * max(0, 1 - (t - 11.65) / 0.8))
    if t >= STAMP_T:
        shake = max(shake, 24 * max(0, 1 - (t - STAMP_T - 0.15) / 0.5))
    if HL_T <= t < HL_T + 0.08 or STAMP_T + 0.12 <= t < STAMP_T + 0.2:
        im = Image.blend(im, Image.new("RGBA", im.size, (255, 255, 255, 255)), 0.5)
    if t >= 12.9:  # mood shift: desaturate after he leaves
        g = im.convert("L").convert("RGBA")
        im = Image.blend(im, g, 0.6 * ease_out(prog(t, 12.9, 0.8)))
        if t >= STAMP_T:
            p = prog(t, STAMP_T, 0.18)
            paste_scaled(im, STAMP, (w / 2, h * 0.52), 2.4 - 1.4 * ease_out(p), alpha=clamp(p * 3))
    return camera(im, zoom, focus, shake)


_SCROLL = {}


def smooth_scroll(t, h):
    """Scroll eases toward the newest message over ~0.3s."""
    target = max(0, bottom_at(t) + 60 - h)
    key = round(t * 30)
    prev = _SCROLL.get(key - 1, target)
    val = prev + (target - prev) * 0.25
    _SCROLL[key] = val
    return val


def caption(t):
    return "Bro really thought he could lie in the group chat 😭🙏"


def audio():
    ev = []
    for m in LAYOUT:
        if m["who"] == "system":
            continue
        ev.append((m["t"], sfx.pop() if m["me"] else sfx.ding(990), 0.9))
    ev += [(3.95, sfx.whoosh(0.3), 0.6), (4.4, sfx.riser(1.0), 0.55), (HL_T, sfx.boom(), 1.0),
           (ARROW_T, sfx.whoosh(0.3), 0.8), (7.4, sfx.heartbeat(3, 120), 0.9),
           (11.65, sfx.bruh_horn(), 0.8), (12.95, sfx.sad_trombone(), 1.0),
           (STAMP_T + 0.12, sfx.stamp(), 1.0), (STAMP_T + 0.12, sfx.boom(), 0.9)]
    music = sfx.beat_loop(12.8, bpm=96)
    music[int(5.3 * sfx.SR):int(7.3 * sfx.SR)] *= 0.2
    music[int(7.4 * sfx.SR):int(9.0 * sfx.SR)] *= 0.3
    return ev, music


if __name__ == "__main__":
    import sys
    ev, music = audio()
    out = sys.argv[1] if len(sys.argv) > 1 else "out/02_group_chat.mp4"
    print(render(out, DUR, caption, content, ev, music))
