"""Korean text rendering helpers (Pillow): {highlight} markup, word wrap,
stroked captions and rounded label pills."""
import os
import re
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "fonts")
FONTS = {
    "title": "BlackHanSans-Regular.ttf",
    "caption": "GothicA1-Black.ttf",
    "bold": "GothicA1-ExtraBold.ttf",
    "medium": "GothicA1-Bold.ttf",
    "hud": "VT323-Regular.ttf",
    "mono": "ShareTechMono-Regular.ttf",
}


@lru_cache(maxsize=64)
def font(kind, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, FONTS.get(kind, kind)), size)


def segments(text):
    """'평범한 {사자}가' -> [('평범한 ', False), ('사자', True), ('가', False)]"""
    out = []
    for part in re.split(r"(\{[^}]*\})", text):
        if not part:
            continue
        if part.startswith("{") and part.endswith("}"):
            out.append((part[1:-1], True))
        else:
            out.append((part, False))
    return out


def plain(text):
    return re.sub(r"[{}]", "", text).replace("_", " ")


COUNTERS = ("마리", "번", "분", "초", "시간", "시", "개", "명", "종", "년", "월", "일", "km", "m", "kg", "배", "살", "주")
NUMWORDS = ("한", "두", "세", "네", "다섯", "여섯", "일곱", "여덟", "아홉", "열", "수십", "수백", "몇")


def _tokens(para):
    """split on spaces but keep '두 마리', '3분 뒤' style number+counter pairs together"""
    raw = [w for w in para.split(" ") if w]
    words, buf = [], None
    for w in raw:  # keep {highlight groups} on one line
        if buf is not None:
            buf += "_" + w
            if "}" in w:
                words.append(buf)
                buf = None
        elif "{" in w and "}" not in w:
            buf = w
        else:
            words.append(w)
    if buf is not None:
        words.append(buf)
    out = []
    for w in words:
        prev = out[-1] if out else None
        bare = w.lstrip("{")
        if prev is not None:
            pb = prev.rstrip("}").split("_")[-1]
            if (pb in NUMWORDS or re.fullmatch(r"[0-9.,~%]+", pb)) and bare.startswith(COUNTERS):
                out[-1] = prev + "_" + w
                continue
        out.append(w)
    return out


def text_w(s, f):
    return f.getlength(s)


def _greedy(words, f, max_w):
    lines, cur = [], ""
    for w in words:
        cand = (cur + " " + w).strip() if cur else w
        if text_w(plain(cand), f) <= max_w or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


DEPENDENT = ("듯", "것", "수 ", "수가", "때", "뿐", "만큼", "척", "줄", "데", "중")


def _cost(parts, f):
    ws = [text_w(plain(x), f) for x in parts]
    c = max(ws)
    for i, p in enumerate(parts[:-1]):
        nxt = parts[i + 1]
        if nxt.lstrip("{").startswith(DEPENDENT):
            c += 150                                 # keep '박을 듯이', '찍은 것' together
        if nxt.startswith("{"):
            c -= 60                                  # nice to start a line with the highlight
        last = p.split(" ")[-1].strip("{}")
        if p.endswith(","):
            c -= 250                                 # prefer breaking after a comma
        if len(last) == 1:
            c += 80                                  # avoid a lonely 1-syllable word at line end
        if ws[i] > ws[i + 1]:
            c += 0.02 * (ws[i] - ws[i + 1])          # ties: shorter top line
    return c


def _balance(words, f, nlines):
    """split words into nlines lines minimising the widest line (+ Korean line-break taste)"""
    best, best_c = None, 1e9
    n = len(words)
    if nlines == 2:
        cands = [[" ".join(words[:k]), " ".join(words[k:])] for k in range(1, n)]
    elif nlines == 3:
        cands = [[" ".join(words[:i]), " ".join(words[i:j]), " ".join(words[j:])]
                 for i in range(1, n - 1) for j in range(i + 1, n)]
    else:
        cands = []
    for parts in cands:
        c = _cost(parts, f)
        if c < best_c:
            best, best_c = parts, c
    return best


def wrap(text, f, max_w):
    """Wrap on spaces keeping {markup} intact; explicit \\n forces a break.
    Lines are balanced so a caption never ends with a lonely short word."""
    lines = []
    for para in text.split("\n"):
        words = _tokens(para)
        g = _greedy(words, f, max_w)
        if len(g) in (2, 3):
            bal = _balance(words, f, len(g))
            if bal and all(text_w(plain(x), f) <= max_w for x in bal):
                g = bal
        lines.extend(g)
    fixed, carry = [], False
    for ln in lines:
        if carry:
            ln = "{" + ln
        opens, closes = ln.count("{"), ln.count("}")
        carry = opens > closes
        if carry:
            ln = ln + "}"
        fixed.append(ln.replace("_", " "))
    return fixed


def render_lines(lines, f, fill=(255, 255, 255), hl=(255, 214, 10), stroke=8,
                 stroke_fill=(0, 0, 0), spacing=1.18, align="center", shadow=True):
    """Render markup lines to a tight RGBA image."""
    asc, desc = f.getmetrics()
    lh = int((asc + desc) * spacing)
    widths = [text_w(plain(l), f) for l in lines]
    W = int(max(widths) + stroke * 2 + 12)
    H = int(lh * len(lines) + stroke * 2 + 12)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, ln in enumerate(lines):
        x = stroke + 6 + (0 if align == "left" else (W - stroke * 2 - 12 - widths[i]) / 2)
        y = stroke + 6 + i * lh
        for seg, is_hl in segments(ln):
            d.text((x, y), seg, font=f, fill=hl if is_hl else fill, stroke_width=stroke, stroke_fill=stroke_fill)
            x += text_w(seg, f)
    if shadow:
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        alpha = img.split()[3].filter(ImageFilter.GaussianBlur(6))
        sh.putalpha(alpha.point(lambda a: int(a * 0.55)))
        base = Image.new("RGBA", (W + 8, H + 8), (0, 0, 0, 0))
        base.alpha_composite(sh, (6, 8))
        base.alpha_composite(img, (0, 0))
        return base
    return img


def pill(text, f, fg=(0, 0, 0), bg=(255, 214, 10), pad=(22, 10), radius=18, arrow=None):
    """Rounded label with optional arrow ('down', 'up') used for callouts."""
    tw = int(text_w(text, f))
    asc, desc = f.getmetrics()
    w, h = tw + pad[0] * 2, asc + desc + pad[1] * 2
    ah = 22 if arrow else 0
    img = Image.new("RGBA", (w + 8, h + ah + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    oy = ah if arrow == "up" else 0
    d.rounded_rectangle((0, oy, w, oy + h), radius=radius, fill=bg + (255,), outline=(0, 0, 0, 255), width=4)
    d.text((pad[0], oy + pad[1] - 2), text, font=f, fill=fg)
    cx = w // 2
    if arrow == "down":
        d.polygon([(cx - 18, h - 2), (cx + 18, h - 2), (cx, h + ah)], fill=bg + (255,), outline=(0, 0, 0, 255))
    elif arrow == "up":
        d.polygon([(cx - 18, ah + 2), (cx + 18, ah + 2), (cx, 0)], fill=bg + (255,), outline=(0, 0, 0, 255))
    return img
