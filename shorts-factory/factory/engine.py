"""Shorts renderer: story (JSON) -> 1080x1920 H.264 MP4.

Layout (Korean shorts convention, tuned to YouTube Shorts safe zones):
  y 0-440     tag line + 2-line hook title (stays on screen the whole time)
  y 440-1520  1080x1080 'CCTV monitor' with the camera-trap footage
              (REC dot, real capture timestamp, camera id, scanlines)
  y ~1200-1400 captions (pop-in, yellow keyword highlight)
Every frame is composed with Pillow and piped straight into ffmpeg.
"""
import math
import os
import random
import subprocess
from datetime import datetime, timedelta

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

from . import audio as A
from . import lila
from . import text as T

W, H, FPS = 1080, 1920, 30
MX, MY, MW, MH = 0, 440, 1080, 1080
BG = (8, 8, 10)
YELLOW = (255, 214, 10)
RED = (255, 59, 48)
CAPTION_BOTTOM = 1405
STRIP = 0.945          # keep top 94.5% of each camera image (drops the brand/time strip)
XFADE = 0.10           # crossfade between burst frames (s)


def ffmpeg_exe():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def loudnorm(ff, src, dst, target=-14.0):
    """two-pass EBU R128 normalisation to YouTube's -14 LUFS reference"""
    import json as _json
    p = subprocess.run([ff, "-hide_banner", "-i", src, "-af",
                        f"loudnorm=I={target}:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    txt = p.stderr
    m = _json.loads(txt[txt.rindex("{"):txt.rindex("}") + 1])
    af = (f"loudnorm=I={target}:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run([ff, "-y", "-loglevel", "error", "-i", src, "-af", af, "-ar", "48000", dst], check=True)


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def ease_out_back(x, s=1.7):
    x = min(1.0, max(0.0, x)) - 1
    return max(0.0, 1 + x * x * ((s + 1) * x + s))


def reading_time(txt):
    n = len(T.plain(txt).replace(" ", "").replace("\n", ""))
    return min(4.4, max(1.7, 0.95 + 0.078 * n))


# ------------------------------------------------------------------ sources
class Source:
    """A graded camera-trap photo plus derived versions (cached)."""
    _cache = {}

    def __init__(self, rel):
        im = Image.open(lila.image(rel)).convert("RGB")
        self.orig_size = im.size
        w, h = im.size
        im = im.crop((0, 0, w, int(h * STRIP)))
        arr = np.asarray(im.resize((64, 48))).astype(np.int16)
        self.gray = float(np.abs(arr[..., 0] - arr[..., 1]).mean() + np.abs(arr[..., 1] - arr[..., 2]).mean()) < 6
        im = ImageOps.autocontrast(im, cutoff=0.4 if self.gray else 0.8)
        if not self.gray:
            im = ImageEnhance.Color(im).enhance(1.16)
        im = ImageEnhance.Contrast(im).enhance(1.05)
        self.im = im
        self.size = im.size
        self._fit = None

    @classmethod
    def get(cls, rel):
        if rel not in cls._cache:
            cls._cache[rel] = Source(rel)
        return cls._cache[rel]

    def norm_box_to_px(self, b):
        """normalized box (relative to the ORIGINAL image) -> pixel box in graded image"""
        ow, oh = self.orig_size
        x0, y0, x1, y1 = b
        return (x0 * ow, min(y0 * oh, self.size[1] - 2), x1 * ow, min(y1 * oh, self.size[1] - 1))

    def fit_frame(self):
        """whole 4:3 photo on a blurred, darkened copy of itself"""
        if self._fit is None:
            bg = ImageOps.fit(self.im, (MW, MH), Image.BILINEAR).filter(ImageFilter.GaussianBlur(28))
            bg = ImageEnhance.Brightness(bg).enhance(0.45)
            fw = MW
            fh = int(self.size[1] * fw / self.size[0])
            fg = self.im.resize((fw, fh), Image.LANCZOS)
            bg.paste(fg, (0, (MH - fh) // 2))
            self._fit = bg
        return self._fit


def motion_box(rels):
    """Where is the animal? Difference of burst frames vs their median."""
    if len(rels) < 2:
        return None
    arrs = []
    for r in rels:
        im = Source.get(r).im.convert("L").resize((256, 184), Image.BILINEAR).filter(ImageFilter.GaussianBlur(2))
        arrs.append(np.asarray(im).astype(np.float32))
    stack = np.stack(arrs)
    med = np.median(stack, 0)
    diff = np.abs(stack - med).max(0)
    thr = max(18.0, diff.mean() + 3 * diff.std())
    ys, xs = np.nonzero(diff > thr)
    if len(xs) < 40:
        return None
    x0, x1 = np.percentile(xs, [3, 97])
    y0, y1 = np.percentile(ys, [3, 97])
    sw, sh = Source.get(rels[0]).orig_size
    return [x0 / 256, y0 / 184 * STRIP, x1 / 256, y1 / 184 * STRIP]


def union(boxes):
    if not boxes:
        return None
    return [min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes)]


# ------------------------------------------------------------------ overlays
def make_monitor_overlay():
    ov = Image.new("RGBA", (MW, MH), (0, 0, 0, 0))
    a = np.zeros((MH, MW), np.float32)
    yy, xx = np.mgrid[0:MH, 0:MW]
    r = np.sqrt(((xx - MW / 2) / (MW / 2)) ** 2 + ((yy - MH / 2) / (MH / 2)) ** 2)
    a += np.clip((r - 0.75) / 0.7, 0, 1) ** 1.5 * 150          # vignette
    a[::4, :] += 16                                               # scanlines
    grad = np.clip((yy - MH * 0.55) / (MH * 0.45), 0, 1) ** 1.3 * 120  # caption backing
    a += grad
    ov.putalpha(Image.fromarray(np.clip(a, 0, 235).astype(np.uint8)))
    d = ImageDraw.Draw(ov)
    L, th, m = 64, 5, 26                                          # viewfinder corners
    for (x, y, dx, dy) in ((m, m, 1, 1), (MW - m, m, -1, 1), (m, MH - m - 90, 1, -1), (MW - m, MH - m - 90, -1, -1)):
        d.line([(x, y), (x + dx * L, y)], fill=(255, 255, 255, 200), width=th)
        d.line([(x, y), (x, y + dy * L)], fill=(255, 255, 255, 200), width=th)
    return ov


def make_noise_frames(n=6, seed=1):
    rng = np.random.default_rng(seed)
    frames = []
    for _ in range(n):
        g = rng.integers(0, 255, (MH // 3, MW // 3), dtype=np.uint8)
        im = Image.fromarray(g).resize((MW, MH), Image.NEAREST).convert("RGB")
        d = ImageDraw.Draw(im)
        for _k in range(rng.integers(2, 5)):
            y = int(rng.integers(0, MH))
            d.rectangle((0, y, MW, y + int(rng.integers(8, 60))), fill=(int(rng.integers(0, 60)),) * 3)
        frames.append(im)
    return frames


def vhs(im, strength, rng):
    """rewind look: row jitter, chroma split, tracking bars"""
    a = np.asarray(im).copy()
    h = a.shape[0]
    for _ in range(int(10 * strength) + 2):
        y = int(rng.integers(0, h - 40))
        hh = int(rng.integers(6, 40))
        a[y:y + hh] = np.roll(a[y:y + hh], int(rng.integers(-60, 60) * strength), axis=1)
    sh = int(8 * strength) + 1
    a[..., 0] = np.roll(a[..., 0], sh, axis=1)
    a[..., 2] = np.roll(a[..., 2], -sh, axis=1)
    out = Image.fromarray(a)
    d = ImageDraw.Draw(out)
    cx, cy = 150, MH // 2
    for k in (0, 1):
        x = cx + k * 70
        d.polygon([(x + 60, cy - 50), (x + 60, cy + 50), (x, cy)], fill=(255, 255, 255))
    d.text((cx + 170, cy - 40), "REWIND", font=T.font("hud", 84), fill=(255, 255, 255))
    return out


# ------------------------------------------------------------------ story timing
class Beat:
    def __init__(self, d, idx):
        self.d = d
        self.idx = idx
        self.kind = d.get("kind", "shot")
        self.text = d.get("text", "")
        self.dur = float(d.get("dur") or reading_time(self.text) if self.text else d.get("dur", 2.0))
        self.trans = d.get("trans", "cut")
        self.cam = d.get("cam", "drift")
        self.shot = derive_shot(d.get("shot"), d.get("use"), d.get("focus"))
        self.sfx = d.get("sfx", [])
        self.callout = d.get("callout")
        self.t0 = 0.0


def derive_shot(shot, use=None, focus=None):
    """per-beat copy of a shot: optional frame subset and focus override"""
    if not shot:
        return None
    sh = dict(shot)
    idx = list(range(len(shot["frames"])))
    if use is not None:
        idx = [i for i in use if i < len(shot["frames"])] or idx[:1]
    sh["frames"] = [shot["frames"][i] for i in idx]
    sh["boxes"] = [shot.get("boxes", [[]] * len(shot["frames"]))[i] for i in idx]
    sh["offsets"] = idx
    if focus:
        sh["focus"] = focus
    return sh


def build_timeline(story):
    beats = [Beat(b, i) for i, b in enumerate(story["beats"])]
    t = 0.0
    for b in beats:
        b.t0 = t
        t += b.dur
    return beats, t


# ------------------------------------------------------------------ renderer
class Renderer:
    def __init__(self, story, number=None, channel="야생CCTV"):
        self.story = story
        self.number = number
        self.channel = channel
        self.beats, self.total = build_timeline(story)
        self.total = round(self.total + 0.35, 3)
        self.overlay = make_monitor_overlay()
        self.noise = make_noise_frames()
        self.rng = np.random.default_rng(abs(hash(story.get("id", "x"))) % 2 ** 32)
        self.static_bg = self.make_static()
        self.captions = {}
        self._prep_shots()

    # ---------------- static layer: bg + title + tag + credit
    def make_static(self):
        bg = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(bg)
        # tag line
        tag = f"{self.channel}  사건파일 #{self.number:02d}" if self.number else self.channel
        f = T.font("bold", 38)
        tw = T.text_w(tag, f)
        x = (W - tw - 40) / 2
        d.ellipse((x, 92, x + 26, 118), fill=RED)
        d.text((x + 40, 84), tag, font=f, fill=(190, 190, 190))
        # title
        tf = T.font("title", 102)
        lines = self.story["title"]
        img = T.render_lines(lines, tf, stroke=0, spacing=1.12, shadow=False)
        if img.width > W - 60:
            img = img.resize((W - 60, int(img.height * (W - 60) / img.width)), Image.LANCZOS)
        ty = 140 + (290 - img.height) // 2
        bg.paste(img, ((W - img.width) // 2, max(130, ty)), img)
        cf = T.font("medium", 26)
        credit = self.story.get("credit", "영상 출처: Snapshot Serengeti · LILA BC (CDLA Permissive)")
        d.text(((W - T.text_w(credit, cf)) / 2, MY + MH + 14), credit, font=cf, fill=(125, 125, 125))
        return bg

    # ---------------- shots: focus boxes, per-frame timestamps
    def _prep_shots(self):
        rels = set()
        for b in self.beats:
            for sh in self._beat_shots(b):
                rels.update(sh["frames"])
        lila.prefetch(sorted(rels))
        for b in self.beats:
            for sh in self._beat_shots(b):
                if "focus" in sh and sh["focus"]:
                    sh["_focus"] = sh["focus"]
                else:
                    boxes = [bx for fb in sh.get("boxes", []) for bx in fb]
                    sh["_focus"] = union(boxes) or motion_box(sh["frames"]) or None

    def _beat_shots(self, b):
        if b.kind == "grid":
            return [it["shot"] for it in b.d["items"]]
        if b.kind == "split":
            return [b.d["top"]["shot"], b.d["bottom"]["shot"]]
        return [b.shot] if b.shot else []

    # ---------------- camera
    _zmax, _fill = 2.7, 0.62

    def crop_box(self, src, focus, cam, u, bd, tb, zoom=None):
        sw, sh = src.size
        base = sh  # full-height square
        if focus:
            fx0, fy0, fx1, fy1 = src.norm_box_to_px(focus)
            fcx, fcy = (fx0 + fx1) / 2, (fy0 + fy1) / 2
            fsize = max(fx1 - fx0, (fy1 - fy0) * 1.0, 1)
            zf = min(self._zmax, max(1.0, base / (fsize / self._fill)))
        else:
            fcx, fcy, zf = sw / 2, sh / 2, 1.0
        cx0, cy0 = sw / 2, sh / 2
        if zoom:
            z = zoom[0] + (zoom[1] - zoom[0]) * ease(u)
            cx, cy = fcx, fcy
        elif cam == "push":
            e = ease(u)
            z = 1.0 + (zf - 1.0) * e
            cx, cy = cx0 + (fcx - cx0) * e, cy0 + (fcy - cy0) * e
        elif cam == "pull":
            e = ease(u)
            z = zf + (1.0 - zf) * e
            cx, cy = fcx + (cx0 - fcx) * e, fcy + (cy0 - fcy) * e
        elif cam == "punch":
            p = ease_out_back(tb / 0.28) if tb < 0.28 else 1.0
            z = 1.0 + (zf * 1.02 - 1.0) * p + 0.04 * zf * ease(u)
            cx, cy = cx0 + (fcx - cx0) * min(1, p), cy0 + (fcy - cy0) * min(1, p)
        elif cam == "hold":
            z = zf * (1 + 0.035 * ease(u))
            cx, cy = fcx, fcy
        elif cam in ("pan_lr", "pan_rl"):
            z = 1.02
            s = base / z
            a, b_ = s / 2, sw - s / 2
            e = ease(u)
            cx = a + (b_ - a) * (e if cam == "pan_lr" else 1 - e)
            cy = sh / 2
        else:  # drift
            z = 1.0 + 0.07 * ease(u)
            cx, cy = (fcx, fcy) if focus else (cx0, cy0)
        z = max(1.0, z)  # ease curves can dip a hair below 0 -> never crop outside the photo
        s = min(base / z, sh, sw)
        cx = min(max(cx, s / 2), sw - s / 2)
        cy = min(max(cy, s / 2), sh - s / 2)
        return (max(0.0, cx - s / 2), max(0.0, cy - s / 2), min(sw, cx + s / 2), min(sh, cy + s / 2))

    # ---------------- media for a beat at local time tb
    def frame_index(self, n, bd, tb, loop):
        if n == 1:
            return 0, 0, 0.0
        if loop:
            per = loop
            k = int(tb / per)
            i, j = k % n, (k + 1) % n
            local = tb - k * per
        else:
            per = bd / n
            i = min(n - 1, int(tb / per))
            j = min(n - 1, i + 1)
            local = tb - i * per
        a = 0.0
        if j != i and local > per - XFADE:
            a = (local - (per - XFADE)) / XFADE
        return i, j, min(1.0, a)

    def shot_image(self, sh, cam, bd, tb, loop=None, zoom=None, size=(MW, MH), fit=False):
        rels = sh["frames"]
        i, j, a = self.frame_index(len(rels), bd, tb, loop)
        src_i = Source.get(rels[i])
        u = tb / bd if bd > 0 else 0
        if fit or cam == "fit":
            im = src_i.fit_frame()
            if a > 0:
                im = Image.blend(im, Source.get(rels[j]).fit_frame(), a)
            return im if size == (MW, MH) else ImageOps.fit(im, size)
        box = self.crop_box(src_i, sh.get("_focus"), cam, u, bd, tb, zoom)
        if size == (MW, MH):
            self._last = (box, src_i, sh.get("_focus"))
        if size != (MW, MH):  # non-square target: adjust crop aspect
            bw = box[2] - box[0]
            want_h = bw * size[1] / size[0]
            cy = (box[1] + box[3]) / 2
            y0 = min(max(cy - want_h / 2, 0), src_i.size[1] - want_h)
            box = (box[0], y0, box[2], y0 + want_h)
        im = src_i.im.resize(size, Image.BILINEAR, box=box)
        if a > 0:
            im2 = Source.get(rels[j]).im.resize(size, Image.BILINEAR, box=box)
            im = Image.blend(im, im2, a)
        return im

    def hud_time(self, sh, bd, tb, loop):
        n = len(sh["frames"])
        i, _, _ = self.frame_index(n, bd, tb, loop)
        try:
            base = datetime.strptime(f'{sh["date"]} {sh["time"]}', "%Y-%m-%d %H:%M:%S")
        except Exception:
            return ""
        off = sh.get("offsets", list(range(n)))[i] if i < len(sh.get("offsets", [])) else i
        return (base + timedelta(seconds=off)).strftime("%Y.%m.%d  %H:%M:%S")

    def media(self, b, tb):
        bd = b.dur
        if b.kind == "grid":
            return self.grid_image(b, tb)
        if b.kind == "split":
            top = self.shot_image(b.d["top"]["shot"], b.d["top"].get("cam", "hold"), bd, tb, size=(MW, MH // 2))
            bot = self.shot_image(b.d["bottom"]["shot"], b.d["bottom"].get("cam", "hold"), bd, tb, size=(MW, MH // 2))
            im = Image.new("RGB", (MW, MH))
            im.paste(top, (0, 0))
            im.paste(bot, (0, MH // 2))
            d = ImageDraw.Draw(im)
            d.rectangle((0, MH // 2 - 3, MW, MH // 2 + 3), fill=(0, 0, 0))
            for lab, y in ((b.d["top"].get("label"), 40), (b.d["bottom"].get("label"), MH // 2 + 40)):
                if lab:
                    p = T.pill(lab, T.font("caption", 44))
                    im.paste(p, (40, y), p)
            return im
        if b.kind == "black":
            return Image.new("RGB", (MW, MH), (0, 0, 0))
        if b.kind == "card":
            return self.card_image(b, tb)
        self._zmax = b.d.get("zmax", 2.7)
        self._fill = b.d.get("fill", 0.62)
        self._last = None
        return self.shot_image(b.shot, b.cam, bd, tb, b.d.get("loop"), b.d.get("zoom"))

    def card_image(self, b, tb):
        """big-text info card over a blurred, darkened frame (stats, time skips)"""
        key = ("card", b.idx)
        if key not in self.captions:
            if b.shot:
                bg = ImageOps.fit(Source.get(b.shot["frames"][0]).im, (MW, MH), Image.BILINEAR)
                bg = ImageEnhance.Brightness(bg.filter(ImageFilter.GaussianBlur(22))).enhance(0.32)
            else:
                bg = Image.new("RGB", (MW, MH), (12, 12, 14))
            d = ImageDraw.Draw(bg)
            big = b.d.get("big", "")
            small = b.d.get("small", "")
            bf = T.font("title", b.d.get("big_size", 104))
            bl = T.render_lines(T.wrap(big, bf, 960), bf, stroke=0, spacing=1.1, shadow=False) if big else None
            sf = T.font("bold", 50)
            sl = T.render_lines(T.wrap(small, sf, 940), sf, fill=(225, 225, 225), stroke=0, spacing=1.25, shadow=False) if small else None
            hgt = (bl.height if bl else 0) + (sl.height + 30 if sl else 0)
            y = (MH - hgt) // 2 - 40
            if bl:
                bg.paste(bl, ((MW - bl.width) // 2, y), bl)
                y += bl.height + 30
            if sl:
                bg.paste(sl, ((MW - sl.width) // 2, y), sl)
            self.captions[key] = bg
        im = self.captions[key]
        z = 1.0 + 0.04 * ease(tb / max(b.dur, 0.01))
        if z > 1.001:
            w = MW / z
            im = im.resize((MW, MH), Image.BILINEAR, box=((MW - w) / 2, (MH - w) / 2, (MW + w) / 2, (MH + w) / 2))
        return im

    def focus_on_monitor(self):
        """monitor-space box of the current shot's focus (for callouts / circles)"""
        if not getattr(self, "_last", None):
            return None
        box, src, focus = self._last
        if not focus:
            return None
        fx0, fy0, fx1, fy1 = src.norm_box_to_px(focus)
        sx = MW / (box[2] - box[0])
        sy = MH / (box[3] - box[1])
        return ((fx0 - box[0]) * sx, (fy0 - box[1]) * sy, (fx1 - box[0]) * sx, (fy1 - box[1]) * sy)

    def grid_image(self, b, tb):
        items = b.d["items"]
        n = len(items)
        cols = 2 if n <= 4 else 3
        rows = math.ceil(n / cols)
        cw, ch = MW // cols, MH // rows
        key = ("grid", b.idx)
        if key not in self.captions:
            cells = []
            for it in items:
                sh = it["shot"]
                src = Source.get(sh["frames"][it.get("frame", 0)])
                box = self.crop_box(src, sh.get("_focus"), "hold", 0.5, 1, 1)
                bw = box[2] - box[0]
                want_h = bw * ch / cw
                cy = (box[1] + box[3]) / 2
                y0 = min(max(cy - want_h / 2, 0), src.size[1] - want_h)
                cell = src.im.resize((cw - 6, ch - 6), Image.LANCZOS, box=(box[0], y0, box[2], y0 + want_h))
                lab = T.pill(it["label"], T.font("caption", 40 if cols == 2 else 34))
                cell.paste(lab, ((cell.width - lab.width) // 2, cell.height - lab.height - 16), lab)
                cells.append(cell)
            self.captions[key] = cells
        cells = self.captions[key]
        im = Image.new("RGB", (MW, MH), (0, 0, 0))
        step = min(0.55, (b.dur * 0.7) / n)
        for k, cell in enumerate(cells):
            t_on = k * step
            if tb < t_on:
                continue
            p = ease_out_back(min(1, (tb - t_on) / 0.22))
            c = cell if p >= 0.999 else cell.resize((max(1, int(cell.width * p)), max(1, int(cell.height * p))))
            x = (k % cols) * cw + 3 + (cell.width - c.width) // 2
            y = (k // cols) * ch + 3 + (cell.height - c.height) // 2
            im.paste(c, (x, y))
        return im

    # ---------------- captions / callouts
    def caption_img(self, b):
        key = ("cap", b.idx)
        if key not in self.captions:
            f = T.font("caption", b.d.get("size", 66))
            lines = T.wrap(b.text, f, 900)
            self.captions[key] = T.render_lines(lines, f, stroke=9, spacing=1.2)
        return self.captions[key]

    def callout_img(self, b):
        key = ("call", b.idx)
        if key not in self.captions:
            c = b.callout
            self.captions[key] = T.pill(c["label"], T.font("caption", c.get("size", 46)), arrow=c.get("arrow", "down"))
        return self.captions[key]

    # ---------------- frame composition
    def compose(self, t):
        b = self.beat_at(t)
        tb = t - b.t0
        canvas = self.static_bg.copy()
        m = self.media(b, tb)
        # transitions in
        tr = b.trans
        if tr == "static" and tb < 0.24:
            nz = self.noise[int(t * FPS) % len(self.noise)]
            m = Image.blend(m, nz, 0.85 * (1 - tb / 0.24))
        elif tr == "flash" and tb < 0.16:
            m = Image.blend(m, Image.new("RGB", m.size, (255, 255, 255)), 0.8 * (1 - tb / 0.16))
        elif tr == "fade" and tb < 0.35:
            m = Image.blend(Image.new("RGB", m.size, (0, 0, 0)), m, tb / 0.35)
        elif tr == "rewind" and tb < 0.7:
            m = vhs(m, 1 - tb / 0.7 * 0.6, self.rng)
        # effects
        ox = oy = 0
        fx = b.d.get("fx", [])
        if "shake" in fx and tb < 0.5:
            amp = 18 * (1 - tb / 0.5)
            ox, oy = int(self.rng.uniform(-amp, amp)), int(self.rng.uniform(-amp, amp))
        if "flash" in fx and tb < 0.12:
            m = Image.blend(m, Image.new("RGB", m.size, (255, 255, 255)), 0.7 * (1 - tb / 0.12))
        if "freeze" in fx:
            m = ImageEnhance.Color(m).enhance(0.35)
        canvas.paste(m, (MX + ox, MY + oy))
        canvas.paste(self.overlay, (MX, MY), self.overlay)
        d = ImageDraw.Draw(canvas)
        # HUD
        fb = self.focus_on_monitor() if b.kind == "shot" else None
        if "circle" in fx and fb and tb >= b.d.get("circle_at", 0.3):
            p = ease_out_back(min(1, (tb - b.d.get("circle_at", 0.3)) / 0.25))
            cx, cy = (fb[0] + fb[2]) / 2, (fb[1] + fb[3]) / 2
            rx = min(MW * 0.42, max(70, (fb[2] - fb[0]) * 0.62)) * p
            ry = min(MH * 0.34, max(70, (fb[3] - fb[1]) * 0.62)) * p
            if p > 0.05:
                layer = Image.new("RGBA", (MW, MH), (0, 0, 0, 0))
                ImageDraw.Draw(layer).ellipse((cx - rx, cy - ry, cx + rx, cy + ry), outline=RED + (255,), width=10)
                canvas.paste(layer, (MX, MY), layer)
        if b.kind in ("shot", "split") and b.d.get("hud", True):
            hf = T.font("hud", 50)
            if int(t * 2) % 2 == 0:
                d.ellipse((MX + 52, MY + 50, MX + 80, MY + 78), fill=RED)
            d.text((MX + 92, MY + 38), "REC", font=hf, fill=(255, 255, 255))
            sh = b.shot if b.kind == "shot" else b.d["top"]["shot"]
            ts = "" if b.d.get("notime") else self.hud_time(sh, b.dur, tb, b.d.get("loop"))
            if ts:
                tw = T.text_w(ts, hf)
                d.text((MX + MW - 52 - tw, MY + 38), ts, font=hf, fill=(255, 255, 255))
            cam = f'CAM {sh.get("site", "")}  SERENGETI'
            d.text((MX + 52, MY + MH - 118), cam, font=T.font("hud", 40), fill=(230, 230, 230))
        # callout
        if b.callout and tb >= b.callout.get("at", 0.2):
            c = b.callout
            img = self.callout_img(b)
            p = ease_out_back(min(1, (tb - c.get("at", 0.2)) / 0.2))
            if p < 0.999:
                img = img.resize((max(1, int(img.width * p)), max(1, int(img.height * p))))
            if "pos" in c:
                px, py = c["pos"]  # normalized position of the arrow tip inside the monitor
            elif fb:
                px = (fb[0] + fb[2]) / 2 / MW
                py = fb[1] / MH - 0.01
            else:
                px, py = 0.5, 0.35
            px = min(0.85, max(0.15, px))
            py = min(0.62, max(0.16, py))
            if b.text and self.caption_pos(b) == "top":
                py = max(py, 0.36)
            x = int(MX + px * MW - img.width / 2)
            y = int(MY + py * MH - img.height)
            canvas.paste(img, (x, y), img)
        # caption
        if b.text:
            img = self.caption_img(b)
            p = ease_out_back(min(1, tb / 0.18), 2.2)
            if p < 0.999:
                img = img.resize((max(1, int(img.width * (0.75 + 0.25 * p))), max(1, int(img.height * (0.75 + 0.25 * p)))))
            if self.caption_pos(b) == "top":
                y = MY + 150 + b.d.get("dy", 0)
            else:
                y = CAPTION_BOTTOM - img.height + b.d.get("dy", 0)
            canvas.paste(img, ((W - img.width) // 2, y), img)
        # credit
        return canvas

    def caption_pos(self, b):
        """'top' when the animal sits in the lower part of the monitor (captions would cover it)"""
        if b.d.get("cap"):
            return b.d["cap"]
        key = ("cappos", b.idx)
        if key not in self.captions:
            pos = "bottom"
            if b.kind == "shot" and b.shot:
                self.media(b, b.dur * 0.6)
                fb = self.focus_on_monitor()
                if fb:
                    cy = (fb[1] + fb[3]) / 2
                    h = fb[3] - fb[1]
                    if cy > MH * 0.6 and h < MH * 0.75:
                        pos = "top"
            self.captions[key] = pos
        return self.captions[key]

    def beat_at(self, t):
        for b in reversed(self.beats):
            if t >= b.t0:
                return b
        return self.beats[0]

    # ---------------- audio cues
    def cues(self):
        cues = []
        for b in self.beats:
            t0 = b.t0
            if b.trans == "static":
                cues.append((max(0, t0 - 0.03), "static"))
            elif b.trans == "flash":
                cues.append((t0, "shutter", 1.2))
            elif b.trans == "rewind":
                cues.append((t0, "rewind"))
            elif b.trans == "whoosh":
                cues.append((max(0, t0 - 0.2), "whoosh"))
            if b.kind == "shot" and b.shot:
                n = len(b.shot["frames"])
                if n > 1:
                    loop = b.d.get("loop")
                    per = loop if loop else b.dur / n
                    k = 1
                    while k * per < b.dur - 0.05:
                        cues.append((t0 + k * per - XFADE / 2, "shutter", 0.55))
                        k += 1
            if b.kind == "grid":
                n = len(b.d["items"])
                step = min(0.55, (b.dur * 0.7) / n)
                for k in range(n):
                    cues.append((t0 + k * step, "pop", 0.8))
            if b.callout:
                cues.append((t0 + b.callout.get("at", 0.2), "pop"))
            for s in b.sfx:
                name, _, off = s.partition("@")
                cues.append((max(0, t0 + (float(off) if off else 0.0)), name))
        return cues

    def ambience_kind(self):
        if self.story.get("amb"):
            return self.story["amb"]
        for b in self.beats:
            if b.shot and b.shot.get("time"):
                h = int(b.shot["time"][:2])
                return "day" if 6 <= h < 19 else "night"
        return "day"

    # ---------------- render
    def render(self, out_path, workdir, preview_frames=None):
        os.makedirs(workdir, exist_ok=True)
        if preview_frames:
            paths = []
            for t in preview_frames:
                p = os.path.join(workdir, f"preview_{t:05.2f}.jpg")
                self.compose(t).save(p, quality=88)
                paths.append(p)
            return paths
        wav = os.path.join(workdir, "mix.wav")
        mixd = A.mix(self.total, self.cues(), self.story.get("mood", "suspense"), self.ambience_kind(),
                     seed=int(self.rng.integers(0, 1 << 30)),
                     music_gain=self.story.get("music_gain", 0.30), amb_gain=self.story.get("amb_gain", 0.30))
        A.write_wav(wav, mixd)
        ff = ffmpeg_exe()
        norm_wav = os.path.join(workdir, "mix_norm.wav")
        loudnorm(ff, wav, norm_wav)
        cmd = [ff, "-y", "-loglevel", "error",
               "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
               "-i", norm_wav,
               "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p",
               "-profile:v", "high", "-level", "4.1",
               "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
               "-shortest", "-movflags", "+faststart", out_path]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        nframes = int(round(self.total * FPS))
        for k in range(nframes):
            proc.stdin.write(self.compose(k / FPS).tobytes())
        proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError("ffmpeg failed for " + out_path)
        return out_path
