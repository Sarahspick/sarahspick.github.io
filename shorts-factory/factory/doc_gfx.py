"""Documentary graphics (1920x1080 RGBA frames). Each element is a function frame(t) -> PIL.Image that the
renderer turns into a short alpha video on the timeline.

Look (v2, 2026-10-05, after studying CNBC / WSJ / Primal Space videos with 1M+ views):
  - numbers: huge Anton figures that count up and punch in, on dimmed footage, label in a yellow highlight box
  - documents and headlines: paper cards and headline bars with a yellow highlighter sweep
  - chapter cards: big yellow chapter number + Anton title, slide in after a white flash
  - sources: one small white line in the bottom-left corner
  - no thin accent rules anywhere
"""
import math
import re

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from .config import asset

W, H = 1920, 1080
YELLOW = (255, 199, 38)
ACCENT = YELLOW
WHITE = (255, 255, 255)
INK = (14, 14, 16)
SOFT = (222, 226, 232)
MUTED = (170, 176, 186)
PAPER = (244, 240, 230)

_FONTS = {}


def font(kind, size, weight=None):
    key = (kind, size, weight)
    if key not in _FONTS:
        path = {"serif": "SourceSerif4-Variable.ttf", "sans": "Inter-Variable.ttf", "display": "Anton-Regular.ttf",
                "mono": "IBMPlexMono-Regular.ttf", "mono_med": "IBMPlexMono-Medium.ttf"}[kind]
        f = ImageFont.truetype(asset("fonts", path), size)
        if weight:
            try:
                f.set_variation_by_name(weight)
            except Exception:
                pass
        _FONTS[key] = f
    return _FONTS[key]


def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def ease_io(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def back(x, s=1.9):
    """Ease-out with a small overshoot (for punchy pops)."""
    x = max(0.0, min(1.0, x)) - 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


def fade(t, dur, fin=0.45, fout=0.45):
    """0..1 envelope: ease in over `fin`, hold, ease out over the last `fout` seconds."""
    a = ease(t / fin) if fin > 0 else 1.0
    b = ease((dur - t) / fout) if fout > 0 else 1.0
    return max(0.0, min(a, b))


def _text(d, xy, s, f, fill, alpha=1.0, spacing=0, anchor="la"):
    col = fill + (int(255 * alpha),)
    if not spacing:
        d.text(xy, s, font=f, fill=col, anchor=anchor)
        return d.textlength(s, font=f)
    x, y = xy
    if anchor[0] == "m":
        x -= _spaced_len(d, s, f, spacing) / 2
        anchor = "l" + anchor[1]
    for ch in s:
        d.text((x, y), ch, font=f, fill=col, anchor=anchor)
        x += d.textlength(ch, font=f) + spacing
    return x - xy[0]


def _spaced_len(d, s, f, spacing):
    return sum(d.textlength(c, font=f) for c in s) + spacing * max(0, len(s) - 1)


def _wrap(d, s, f, width):
    words, lines, cur = s.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if d.textlength(test, font=f) > width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = test
    if cur:
        lines.append(cur)
    return lines


def _dim(img, alpha, vignette=True):
    """Darken the footage under a graphic (stronger at the edges)."""
    if alpha <= 0:
        return
    g = Image.new("L", (96, 54), 0)
    gd = ImageDraw.Draw(g)
    for i in range(27):
        v = int(150 + 105 * (1 - i / 27) ** 2) if vignette else 200
        gd.rectangle([i * 1.7, i, 96 - i * 1.7, 54 - i], fill=v)
    g = g.filter(ImageFilter.GaussianBlur(6)).resize((W, H), Image.BILINEAR).point(lambda v: int(v * alpha))
    k = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    k.putalpha(g)
    img.alpha_composite(k)


def _shadow_text(img, xy, s, f, fill, alpha, anchor="mm", blur=10, sh=150, spacing=0):
    """Text with a soft drop shadow (drawn on its own layer so it stays crisp)."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    _text(ld, (xy[0] + 4, xy[1] + 6), s, f, (0, 0, 0), alpha * sh / 255, spacing=spacing, anchor=anchor)
    lay = lay.filter(ImageFilter.GaussianBlur(blur))
    img.alpha_composite(lay)
    _text(ImageDraw.Draw(img), xy, s, f, fill, alpha, spacing=spacing, anchor=anchor)


# ---------------------------------------------------------------- numbers

_NUM = re.compile(r"^([^0-9]*)([0-9][0-9,]*(?:\.[0-9]+)?)(.*)$")


def _count(v, k):
    """'1,891' at k=0.5 -> '946'. Non-numeric values are returned as they are."""
    m = _NUM.match(v)
    if not m or k >= 1:
        return v
    pre, num, post = m.groups()
    val = float(num.replace(",", ""))
    cur = val * ease(k)
    dec = len(num.split(".")[1]) if "." in num else 0
    s = f"{cur:,.{dec}f}" if "," in num else f"{cur:.{dec}f}"
    return pre + s + post


def _label_box(img, cx, top, text, alpha, size=34):
    d = ImageDraw.Draw(img)
    f = font("sans", size, "ExtraBold")
    tw = _spaced_len(d, text, f, 2)
    pad_x, pad_y = 22, 12
    box = [cx - tw / 2 - pad_x, top, cx + tw / 2 + pad_x, top + size + pad_y * 2]
    d.rectangle(box, fill=YELLOW + (int(255 * alpha),))
    _text(d, (cx, top + pad_y + size / 2 + 2), text, f, INK, alpha, spacing=2, anchor="mm")


def slam(stats, dur, vs=False):
    """One or two big numbers that punch in and count up, over dimmed footage. Labels in yellow boxes."""
    n = len(stats[:2])
    cxs = [W / 2] if n == 1 else ([W * 0.29, W * 0.71])
    size = 250 if n == 1 else 210
    f = font("display", size)

    def frame(t):
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        env = fade(t, dur, 0.18, 0.35)
        _dim(img, 0.62 * env)
        for i, s in enumerate(stats[:2]):
            ti = t - 0.38 * i
            if ti < 0:
                continue
            a = min(env, ease(ti / 0.12))
            sc = 1.0 + 0.35 * (1 - back(ti / 0.32))
            shake = 0
            if ti < 0.22:
                shake = math.sin(ti * 90) * 9 * (1 - ti / 0.22)
            txt = _count(s["v"], ti / 0.75)
            big = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            _shadow_text(big, (cxs[i] + shake, H * 0.43), txt, f, WHITE, a)
            if abs(sc - 1) > 0.004:
                bw, bh = int(W * sc), int(H * sc)
                big = big.resize((bw, bh), Image.BICUBIC)
                ox, oy = int((bw - W) * cxs[i] / W), int((bh - H) * 0.43)
                big = big.crop((ox, oy, ox + W, oy + H))
            img.alpha_composite(big)
            la = min(env, ease((ti - 0.18) / 0.25))
            if la > 0:
                _label_box(img, cxs[i], H * 0.43 + size * 0.55 + 6 + (1 - la) * 14, s["l"].upper(), la,
                           32 if n == 1 else 28)
        if vs and n == 2 and t > 0.25:
            a = min(env, ease((t - 0.25) / 0.2))
            _shadow_text(img, (W / 2, H * 0.43), "VS", font("display", 96), YELLOW, a)
        return img
    return frame


# ---------------------------------------------------------------- source line

def source(cite, dur):
    f = font("sans", 19, "Medium")

    def frame(t):
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        a = fade(t, dur, 0.5, 0.5) * 0.82
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        _text(ImageDraw.Draw(lay), (37, H - 27), "Source: " + cite, f, (0, 0, 0), a * 0.8, anchor="ls")
        img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(2)))
        _text(ImageDraw.Draw(img), (36, H - 28), "Source: " + cite, f, WHITE, a, anchor="ls")
        return img
    return frame


# ---------------------------------------------------------------- flash

def flash(dur=0.3, strength=0.85):
    def frame(t):
        a = strength * (1 - ease(t / dur))
        return Image.new("RGBA", (W, H), (255, 255, 255, int(255 * a)))
    return frame


# ---------------------------------------------------------------- chapter card

def chapter(n, title, dur):
    fn = font("display", 300)
    ft = font("display", 120)

    def frame(t):
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        env = fade(t, dur, 0.08, 0.4)
        img.alpha_composite(Image.new("RGBA", (W, H), (6, 6, 8, int(205 * env))))
        x0 = 150
        k = back(t / 0.45, 1.4)
        num_x = x0 - 140 * (1 - k)
        _shadow_text(img, (num_x, H / 2 - 40), f"{n:02d}", fn, YELLOW, env, anchor="ls", blur=14)
        tk = back((t - 0.12) / 0.45, 1.2)
        title_x = x0 + 360 * (1 - tk) if t > 0.12 else W
        lines = _wrap(ImageDraw.Draw(img), title.upper(), ft, 1500)
        y = H / 2 + 20
        for ln in lines:
            _shadow_text(img, (title_x, y), ln, ft, WHITE, env * ease((t - 0.12) / 0.2), anchor="lt", blur=12)
            y += 132
        return img
    return frame


# ---------------------------------------------------------------- title

def title_card(title, sub, dur):
    ft = font("display", 136)

    def frame(t):
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        env = fade(t, dur, 0.05, 0.6)
        _dim(img, 0.7 * env)
        sc = 1.0 + 0.5 * (1 - back(t / 0.35, 1.2)) + 0.03 * ease_io(t / dur)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        _shadow_text(lay, (W / 2, H / 2 - 40), title.upper(), ft, WHITE, env, spacing=4, blur=16)
        if abs(sc - 1) > 0.004:
            bw, bh = int(W * sc), int(H * sc)
            lay = lay.resize((bw, bh), Image.BICUBIC).crop(((bw - W) // 2, (bh - H) // 2, (bw - W) // 2 + W, (bh - H) // 2 + H))
        img.alpha_composite(lay)
        sa = env * ease((t - 0.6) / 0.5)
        if sa > 0:
            _label_box(img, W / 2, H / 2 + 70, sub.upper(), sa, 30)
        return img
    return frame


# ---------------------------------------------------------------- paper document with highlighter

def doc_card(kind, title, meta, body, highlight, dur, t_hi=1.0):
    """A paper sheet (journal article / report) sliding up over dimmed footage, with a yellow highlighter
    sweeping over `highlight` (a phrase in the title or the body, may span lines) starting at t_hi."""
    ft = font("serif", 50, "SemiBold")
    fm = font("sans", 22, "Medium")
    fk = font("sans", 20, "Bold")
    fb = font("serif", 31, "Regular")
    pw = 1180
    probe = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    rows = []                                    # (font, line, x, y, start offset in its block)
    x, y = 80, 122
    for blk, f, lh in ((title, ft, 64), (body, fb, 46)):
        if not blk:
            continue
        if blk is body:
            y += 40 + 32 * len(_wrap(probe, meta, fm, pw - 160)) + 58
        off = 0
        for ln in _wrap(probe, blk, f, pw - 160):
            rows.append((blk, f, ln, x, y, blk.index(ln, off)))
            off = blk.index(ln, off) + len(ln)
            y += lh
    meta_y = (rows[-1][4] + 74) if not body else None
    ph = (y + 110) if body else (meta_y + 32 * len(_wrap(probe, meta, fm, pw - 160)) + 70)

    def base():
        sheet = Image.new("RGBA", (pw, ph), PAPER + (255,))
        d = ImageDraw.Draw(sheet)
        _text(d, (80, 70), kind.upper(), fk, (150, 120, 40), 1, spacing=3)
        my = meta_y if meta_y else [r for r in rows if r[0] is title][-1][4] + 74
        for ln in _wrap(d, meta, fm, pw - 160):
            _text(d, (80, my), ln, fm, (90, 90, 96), 1)
            my += 32
        if body:
            d.rectangle([80, my + 22, pw - 80, my + 24], fill=(200, 194, 180))
        return sheet

    sheet0 = base()
    span = None
    for blk in (title, body):
        if blk and highlight and highlight in blk:
            i = blk.index(highlight)
            span = (blk, i, i + len(highlight))

    def frame(t):
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        env = fade(t, dur, 0.3, 0.45)
        _dim(img, 0.72 * env)
        sheet = sheet0.copy()
        d = ImageDraw.Draw(sheet)
        hk = ease((t - t_hi) / 0.8)
        if span and hk > 0:
            blk, a, b = span
            segs = [(r, max(a, r[5]), min(b, r[5] + len(r[2]))) for r in rows if r[0] is blk]
            segs = [(r, s0, s1) for r, s0, s1 in segs if s1 > s0]
            total = sum(s1 - s0 for _, s0, s1 in segs)
            done = 0
            for r, s0, s1 in segs:
                _, f, ln, x, y, off = r
                x0 = x + d.textlength(ln[:s0 - off], font=f)
                x1 = x + d.textlength(ln[:s1 - off], font=f)
                k = max(0.0, min(1.0, (hk * total - done) / (s1 - s0)))
                done += s1 - s0
                if k > 0:
                    d.rectangle([x0 - 4, y + f.size * 0.1, x0 - 4 + (x1 - x0 + 8) * k, y + f.size * 1.1],
                                fill=YELLOW + (235,))
        for _, f, ln, x, y, _o in rows:
            _text(d, (x, y), ln, f, INK, 1)
        rot = -1.6 + 0.6 * ease_io(t / dur)
        z = 0.92 + 0.08 * ease_io(t / dur)
        sh = sheet.resize((int(pw * z), int(ph * z)), Image.BICUBIC).rotate(rot, expand=True, resample=Image.BICUBIC)
        rise = (1 - ease(t / 0.5)) * 160
        px, py = (W - sh.width) // 2, int((H - sh.height) // 2 + rise)
        shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        m = sh.split()[3].point(lambda v: int(v * 0.55))
        shadow.paste(Image.new("RGBA", sh.size, (0, 0, 0, 255)), (px + 18, py + 26), m)
        img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(22)))
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        lay.paste(sh, (px, py), sh)
        if env < 1:
            lay.putalpha(lay.split()[3].point(lambda v: int(v * env)))
        img.alpha_composite(lay)
        return img
    return frame


# ---------------------------------------------------------------- headline bar

def headline(text, kicker, dur):
    """Big headline on a black bar with a yellow kicker tag, wiping in from the left."""
    fh = font("display", 92)
    fk = font("sans", 26, "ExtraBold")

    def frame(t):
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        env = fade(t, dur, 0.15, 0.4)
        _dim(img, 0.45 * env)
        d = ImageDraw.Draw(img)
        lines = _wrap(d, text.upper(), fh, 1500)
        bh = 60 + 104 * len(lines)
        y0 = H / 2 - bh / 2 + 30
        k = ease(t / 0.35)
        x1 = 120 + (W - 240) * k
        d.rectangle([120, y0, x1, y0 + bh], fill=(8, 8, 10, int(235 * env)))
        if k > 0.6:
            ta = env * ease((t - 0.2) / 0.25)
            y = y0 + 28
            for ln in lines:
                _text(d, (170, y), ln, fh, WHITE, ta)
                y += 104
        ka = env * ease((t - 0.3) / 0.25)
        if ka > 0:
            kw = _spaced_len(d, kicker.upper(), fk, 3)
            d.rectangle([120, y0 - 58, 120 + kw + 40, y0], fill=YELLOW + (int(255 * ka),))
            _text(d, (140, y0 - 29), kicker.upper(), fk, INK, ka, spacing=3, anchor="lm")
        return img
    return frame


# ---------------------------------------------------------------- end card

def quote_card(quote, who, dur, note=""):
    def frame(t):
        img = Image.new("RGBA", (W, H), (0, 0, 0, int(255 * ease(t / 0.8))))
        d = ImageDraw.Draw(img)
        a = fade(t - 0.5, dur - 0.5, 0.9, 0.9)
        fq = font("display", 96)
        lines = _wrap(d, f"“{quote.upper()}”", fq, 1500)
        y = H / 2 - len(lines) * 56 - 40
        for ln in lines:
            _text(d, (W // 2, y), ln, fq, WHITE, a, anchor="mm")
            y += 112
        wa = a * ease((t - 1.3) / 0.6)
        if wa > 0:
            _label_box(img, W / 2, y + 10, who.upper(), wa, 30)
        if note:
            _text(d, (W // 2, H - 70), note, font("sans", 22, "Medium"), MUTED, a * ease((t - 2.2) / 0.8), anchor="mm")
        return img
    return frame


# ---------------------------------------------------------------- cross-dock diagram

def crossdock(dur, t_trad, t_cross):
    """Two lanes. 'Traditional': boxes travel to storage and pile up there. 'Cross-dock': boxes pass through a
    sort point and straight out to the store. Lane 1 appears at t_trad, lane 2 at t_cross (narration times)."""
    def lane(d, y, a, t, label, mid_label, mid_sub, flow, colour):
        if a <= 0:
            return
        x1, x2, x3 = 330, 960, 1590
        f_lab = font("mono_med", 24)
        _text(d, (180, y - 92), label, f_lab, colour, a, spacing=4)
        line = (255, 255, 255, int(70 * a))
        d.line([(x1 + 90, y), (x3 - 90, y)], fill=line, width=3)
        for x, name in ((x1, "SUPPLIER"), (x3, "STORE")):
            d.rounded_rectangle([x - 90, y - 46, x + 90, y + 46], 14, outline=(255, 255, 255, int(200 * a)), width=3,
                                fill=(10, 16, 26, int(220 * a)))
            _text(d, (x, y), name, font("sans", 24, "SemiBold"), WHITE, a, spacing=2, anchor="mm")
        d.rounded_rectangle([x2 - 130, y - 58, x2 + 130, y + 58], 16, outline=colour + (int(255 * a),), width=4,
                            fill=(10, 16, 26, int(235 * a)))
        _text(d, (x2, y - 12), mid_label, font("sans", 26, "Bold"), WHITE, a, spacing=2, anchor="mm")
        _text(d, (x2, y + 24), mid_sub, font("mono", 21), colour, a, anchor="mm")
        flow(d, t, a, x1, x2, x3, y, colour)

    def flow_trad(d, t, a, x1, x2, x3, y, colour):
        # boxes arrive into storage and stack up; only a trickle leaves
        for k in range(10):
            p = (t * 0.55 - k * 0.32)
            if p < 0:
                continue
            if p < 1:
                x = x1 + 90 + (x2 - 130 - x1 - 90) * ease_io(p)
                _box(d, x, y, a, colour)
        n_stacked = min(9, int(max(0, t * 0.55 - 1) / 0.32) + 1) if t * 0.55 > 1 else 0
        for k in range(n_stacked):
            bx = x2 - 92 + (k % 5) * 38
            by = y + 82 + (k // 5) * 30
            _box(d, bx, by, a * 0.85, colour, s=13)
        p = (t * 0.18) % 1
        if t * 0.18 > 0.6:
            _box(d, x2 + 130 + (x3 - 90 - x2 - 130) * ease_io(p), y, a, colour)

    def flow_cross(d, t, a, x1, x2, x3, y, colour):
        for k in range(14):
            p = (t * 0.42 - k * 0.2)
            if p < 0 or p > 1:
                continue
            x = x1 + 90 + (x3 - 90 - x1 - 90) * p
            if abs(x - x2) < 130:
                continue
            _box(d, x, y, a, colour)

    def frame(t):
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        env = fade(t, dur, 0.6, 0.6)
        img.alpha_composite(Image.new("RGBA", (W, H), (3, 7, 13, int(185 * env))))
        d = ImageDraw.Draw(img)
        a1 = env * ease((t - t_trad) / 0.6)
        a2 = env * ease((t - t_cross) / 0.6)
        lane(d, 400, a1, max(0, t - t_trad), "TRADITIONAL WAREHOUSE", "STORAGE", "days to weeks", flow_trad, (240, 84, 66))
        lane(d, 760, a2, max(0, t - t_cross), "CROSS-DOCK", "SORT", "hours", flow_cross, ACCENT)
        return img
    return frame


def _box(d, x, y, a, colour, s=16):
    d.rounded_rectangle([x - s, y - s, x + s, y + s], 4, fill=colour + (int(235 * a),))
