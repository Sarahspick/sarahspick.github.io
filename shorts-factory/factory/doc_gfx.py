"""Documentary graphics (1920x1080 RGBA frames): stat cards, source citations, chapter and title cards, end card,
and the cross-docking diagram. Each element is a function frame(t) -> PIL.Image so the renderer can turn it into
a short alpha video placed on the timeline.

Look: restrained broadcast style. Source Serif for numbers and titles, Inter for labels, IBM Plex Mono for
citations, one accent colour (the channel's electric blue).
"""
import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from .config import asset

W, H = 1920, 1080
ACCENT = (22, 139, 255)
WHITE = (255, 255, 255)
SOFT = (214, 220, 228)
MUTED = (160, 168, 178)

_FONTS = {}


def font(kind, size, weight=None):
    key = (kind, size, weight)
    if key not in _FONTS:
        path = {"serif": "SourceSerif4-Variable.ttf", "sans": "Inter-Variable.ttf",
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


def _scrim(img, alpha, region="bottom-left"):
    """Soft dark gradient behind lower text so it reads on any footage."""
    if alpha <= 0:
        return
    g = Image.new("L", (W // 4, H // 4), 0)
    gd = ImageDraw.Draw(g)
    if region == "bottom-left":
        for i in range(40):
            r = 1 - i / 40
            gd.ellipse([-W // 4 * 0.55 * r - 20, H // 4 - H // 4 * 0.75 * r, W // 4 * 0.75 * r, H // 4 + H // 4 * 0.6 * r],
                       fill=int(190 * (i / 40) ** 0.8))
    else:  # full darken with vignette
        gd.rectangle([0, 0, W // 4, H // 4], fill=150)
    g = g.filter(ImageFilter.GaussianBlur(14)).resize((W, H), Image.BILINEAR)
    g = g.point(lambda v: int(v * alpha))
    black = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    black.putalpha(g)
    img.alpha_composite(black)


# ---------------------------------------------------------------- stats + citation (lower left)

def lower(stats, cite, dur, stat_start=0.0, cite_start=0.0):
    """Lower-left block: up to two big numbers with labels, and a source line under them."""
    def frame(t):
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        st = t - stat_start
        sa = fade(st, dur - stat_start, 0.55, 0.5) if stats and st >= 0 else 0.0
        ca = fade(t - cite_start, dur - cite_start, 0.6, 0.5) if cite and t >= cite_start else 0.0
        _scrim(img, max(sa, ca * 0.6))
        d = ImageDraw.Draw(img)
        x0, base = 112, H - 118
        if cite:
            fm = font("mono", 21)
            lab = "SOURCE"
            _text(d, (x0, base + 26), lab, font("mono_med", 21), ACCENT, ca, spacing=2)
            _text(d, (x0 + 112, base + 26), cite, fm, SOFT, ca * 0.92)
        if stats and sa > 0:
            rise = (1 - ease(st / 0.6)) * 26
            x = x0
            for i, s in enumerate(stats[:2]):
                a = sa if i == 0 else fade(st - 0.25, dur - stat_start - 0.25, 0.55, 0.5)
                if a <= 0:
                    continue
                fv = font("serif", 112, "SemiBold")
                fl = font("sans", 27, "Medium")
                y = base - 178 + rise
                # accent rule grows from the left
                rl = 64 * ease((st - 0.1 - 0.25 * i) / 0.5)
                d.rectangle([x, y - 14, x + rl, y - 10], fill=ACCENT + (int(255 * a),))
                vw = _text(d, (x, y), s["v"], fv, WHITE, a)
                lw = _text(d, (x + 2, y + 128), s["l"].upper(), fl, SOFT, a, spacing=2)
                x += max(vw, lw) + 96
                if i == 0 and len(stats) > 1:
                    d.rectangle([x - 48, y + 10, x - 47, y + 150], fill=(255, 255, 255, int(80 * a)))
        return img
    return frame


# ---------------------------------------------------------------- chapter card

def chapter(n, title, dur):
    def frame(t):
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        a = fade(t, dur, 0.5, 0.55)
        dk = Image.new("RGBA", (W, H), (4, 8, 14, int(150 * a)))
        img.alpha_composite(dk)
        d = ImageDraw.Draw(img)
        cx, cy = 150, H // 2
        lab = f"CHAPTER {n:02d}"
        _text(d, (cx, cy - 92), lab, font("mono_med", 28), ACCENT, a, spacing=6)
        ft = font("serif", 92, "Medium")
        # title reveals with a slight upward drift
        dy = (1 - ease((t - 0.15) / 0.8)) * 18
        ta = a * ease((t - 0.15) / 0.6)
        _text(d, (cx - 4, cy - 40 + dy), title, ft, WHITE, ta)
        lw = (d.textlength(title, font=ft)) * ease((t - 0.3) / 1.0)
        d.rectangle([cx, cy + 92, cx + lw, cy + 94], fill=(255, 255, 255, int(110 * a)))
        return img
    return frame


# ---------------------------------------------------------------- title + end

def title_card(title, sub, dur):
    def frame(t):
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        a = fade(t, dur, 0.9, 0.8)
        img.alpha_composite(Image.new("RGBA", (W, H), (2, 6, 12, int(130 * a))))
        d = ImageDraw.Draw(img)
        f = font("sans", 76, "Bold")
        sp = 16 - 6 * ease(t / dur)          # letters slowly tighten
        _text(d, (W // 2, H // 2 - 40), title.upper(), f, WHITE, a, spacing=sp, anchor="mm")
        rl = 220 * ease((t - 0.4) / 1.2)
        d.rectangle([W // 2 - rl / 2, H // 2 + 20, W // 2 + rl / 2, H // 2 + 22], fill=ACCENT + (int(255 * a),))
        sa = a * ease((t - 0.7) / 0.8)
        _text(d, (W // 2, H // 2 + 72), sub, font("serif", 36, "Regular"), SOFT, sa, anchor="mm")
        return img
    return frame


def quote_card(quote, who, dur, note=""):
    """Final card on black: the closing quote, then a quiet line pointing to the sources."""
    def frame(t):
        img = Image.new("RGBA", (W, H), (0, 0, 0, int(255 * ease(t / 0.8))))
        d = ImageDraw.Draw(img)
        a = fade(t - 0.5, dur - 0.5, 0.9, 0.9)
        fq = font("serif", 58, "Regular")
        lines = _wrap(d, f"“{quote}”", fq, 900)
        y = H // 2 - len(lines) * 40 - 30
        for ln in lines:
            _text(d, (W // 2, y), ln, fq, WHITE, a, anchor="mm")
            y += 80
        _text(d, (W // 2, y + 18), "— " + who.upper(), font("mono_med", 26), ACCENT, a * ease((t - 1.3) / 0.8), spacing=4, anchor="mm")
        if note:
            _text(d, (W // 2, H - 90), note, font("mono", 22), MUTED, a * ease((t - 2.2) / 0.8), anchor="mm")
        return img
    return frame


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
        lane(d, 400, a1, max(0, t - t_trad), "TRADITIONAL WAREHOUSE", "STORAGE", "days to weeks", flow_trad, (245, 166, 35))
        lane(d, 760, a2, max(0, t - t_cross), "CROSS-DOCK", "SORT", "hours", flow_cross, ACCENT)
        return img
    return frame


def _box(d, x, y, a, colour, s=16):
    d.rounded_rectangle([x - s, y - s, x + s, y + s], 4, fill=colour + (int(235 * a),))
