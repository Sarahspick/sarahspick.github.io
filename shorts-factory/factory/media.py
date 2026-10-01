"""Footage handling: download (yt-dlp), probe, smart crop, and per-frame readers for video/image/card/slate."""
import hashlib
import json
import os
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from . import gfx
from .config import FPS, WORK, rel

SOURCES = os.path.join(WORK, "sources")
_failed = set()


def parse_aspect(a):
    if isinstance(a, (int, float)):
        return float(a)
    w, h = str(a).split(":")
    return float(w) / float(h)


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height:format=duration", "-of", "json", path], capture_output=True, text=True)
    d = json.loads(r.stdout or "{}")
    st = (d.get("streams") or [{}])[0]
    return st.get("width"), st.get("height"), float(d.get("format", {}).get("duration", 0) or 0)


PLATFORMS = {"yt": "https://www.youtube.com/watch?v={}", "bili": "https://www.bilibili.com/video/{}",
             "dm": "https://www.dailymotion.com/video/{}",
             "tt": "https://www.tiktok.com/@_/video/{}",   # tt:<video id>; TikTok resolves the account itself
             "x": "https://x.com/i/status/{}"}


def playlist_item(src):
    """yt-dlp options that pick the n-th video of an X post with several (x:<status id>/<n>)."""
    pre, _, vid = src.partition(":")
    if pre == "x" and "/" in vid:
        return {"playlist_items": vid.split("/", 1)[1]}
    return {}


def source_url(src):
    """'yt:ID' / 'bili:BVxxxx' shortcuts -> page URL (for downloads and credits)."""
    pre, _, vid = src.partition(":")
    if pre == "x" and "/" in vid:
        return f"https://x.com/i/status/{vid.split('/', 1)[0]}"
    return PLATFORMS[pre].format(vid) if pre in PLATFORMS and vid else src


def ytdlp_opts(**extra):
    """Base yt-dlp options. YouTube needs a signed-in cookie file (YT_COOKIES_B64, a base64 Netscape cookie file,
    written to work/ which git ignores) and a JavaScript runtime new enough for its challenge (Node 20+ on PATH
    may be too old; Node 22 is used when present)."""
    import base64
    import shutil
    opts = {"quiet": True, "no_warnings": True, "socket_timeout": 30, "retries": 5,
            "format_sort": ["res:1080", "fps", "br"], "format_sort_force": True}   # highest resolution up to 1080p first (TikTok 1080p is h265)
    b64 = os.environ.get("YT_COOKIES_B64", "")
    if b64:
        cookie = os.path.join(WORK, "yt_cookies.txt")
        if not os.path.exists(cookie):
            os.makedirs(WORK, exist_ok=True)
            with open(cookie, "wb") as f:
                f.write(base64.b64decode(b64))
            os.chmod(cookie, 0o600)
        opts["cookiefile"] = cookie
    for node in ("/opt/node22/bin/node", shutil.which("node")):
        if node and os.path.exists(node):
            opts["js_runtimes"] = {"node": {"path": node}}
            break
    opts.update(extra)
    return opts


def fetch(src):
    """Resolve a clip source to a local video file, downloading with yt-dlp if needed. None if unavailable."""
    if not src:
        return None
    pre, _, vid = src.partition(":")
    if pre == "x" and "/" in vid:   # x:<status id>/<n>: the n-th video of a post with several
        sid, n = vid.split("/", 1)
        url, key = f"https://x.com/i/status/{sid}", f"x_{sid}_{n}"
    elif pre in PLATFORMS and vid:
        url, key = PLATFORMS[pre].format(vid), f"{pre}_{vid}"
    elif src.startswith(("http://", "https://")):
        url, key = src, hashlib.sha1(src.encode()).hexdigest()[:12]
    else:
        p = rel(src)
        return p if os.path.exists(p) else None
    os.makedirs(SOURCES, exist_ok=True)
    for f in os.listdir(SOURCES):
        if f.startswith(key + ".") and f.endswith((".mp4", ".mkv", ".webm")):
            return os.path.join(SOURCES, f)
    if url in _failed:
        return None
    try:
        import yt_dlp
        opts = ytdlp_opts(outtmpl=os.path.join(SOURCES, key + ".%(ext)s"),
                          format="bv*+ba/b",   # the cap is format_sort res:1080 (shorter side, so vertical 1080p counts)
                          merge_output_format="mp4", writeinfojson=True, **playlist_item(src))
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if info.get("entries"):
                info = info["entries"][0]
            path = ydl.prepare_filename(info)
        base = os.path.splitext(path)[0]
        for ext in (".mp4", ".mkv", ".webm"):
            if os.path.exists(base + ext):
                return base + ext
    except Exception as e:
        print(f"[media] cannot fetch {url}: {str(e).splitlines()[0][:160]}")
    _failed.add(url)
    return None


def source_meta(src):
    """Title / uploader / URL of a downloaded source (from yt-dlp's .info.json) for the credits list."""
    pre, _, vid = (src or "").partition(":")
    key = f"{pre}_{vid}" if pre in PLATFORMS and vid else None
    meta = {"url": source_url(src or "")}
    if key:
        p = os.path.join(SOURCES, key + ".info.json")
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                d = json.load(f)
            meta.update(title=d.get("title"), uploader=d.get("uploader") or d.get("channel"))
    return meta


def auto_focus(path, start, dur, aspect):
    """Pick the crop centre that keeps the most motion + detail inside the target aspect window."""
    sw, sh, _ = probe(path)
    if not sw:
        return 0.5, 0.5
    small_w = 192
    small_h = max(2, int(round(sh * small_w / sw / 2)) * 2)
    n = 10
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(start), "-i", path, "-t", str(max(dur, 0.5)),
                        "-vf", f"fps={n / max(dur, 0.5):.4f},scale={small_w}:{small_h},format=gray",
                        "-f", "rawvideo", "-"], capture_output=True)
    frames = np.frombuffer(r.stdout, np.uint8)
    k = len(frames) // (small_w * small_h)
    if k < 2:
        return 0.5, 0.5
    fr = frames[:k * small_w * small_h].reshape(k, small_h, small_w).astype(np.float32)
    motion = np.abs(np.diff(fr, axis=0)).mean(0)
    gy, gx = np.gradient(fr.mean(0))
    detail = np.hypot(gx, gy)
    sal = motion / (motion.mean() + 1e-3) + 0.5 * detail / (detail.mean() + 1e-3)
    src_aspect = sw / sh
    if src_aspect > aspect:  # choose horizontal window
        win = int(round(small_h * aspect))
        col = sal.sum(0)
        cs = np.convolve(col, np.ones(win), mode="valid")
        cx = (int(np.argmax(cs)) + win / 2) / small_w
        return float(np.clip(cx, 0, 1)), 0.5
    win = int(round(small_w / aspect))
    row = sal.sum(1)
    cs = np.convolve(row, np.ones(win), mode="valid")
    cy = (int(np.argmax(cs)) + win / 2) / small_h
    return 0.5, float(np.clip(cy, 0, 1))


def crop_rect(sw, sh, aspect, focus, zoom=1.0):
    if sw / sh > aspect:
        ch = sh / zoom
        cw = ch * aspect
    else:
        cw = sw / zoom
        ch = cw / aspect
    cx = min(max(focus[0] * sw - cw / 2, 0), sw - cw)
    cy = min(max(focus[1] * sh - ch / 2, 0), sh - ch)
    ev = lambda v: int(v) - int(v) % 2
    return ev(cw), ev(ch), ev(cx), ev(cy)


class _View:
    """Shared zoom/crop logic: prepared frames are larger than the box so punch/Ken-Burns zooms stay sharp."""

    def view(self, im, zoom, focus=(0.5, 0.5)):
        pw, ph = im.size
        w, h = self.box[2], self.box[3]
        vw, vh = pw / zoom, ph / zoom
        x0 = min(max(focus[0] * pw - vw / 2, 0), pw - vw)
        y0 = min(max(focus[1] * ph - vh / 2, 0), ph - vh)
        self._last_view = (x0, y0, vw, vh)
        return im.resize((w, h), Image.BICUBIC, box=(x0, y0, x0 + vw, y0 + vh))

    def cover_center(self):
        """Centre and height, in output-frame pixels, of the first black cover box (None if the clip has none)."""
        if not getattr(self, "covers", None) or not getattr(self, "_last_view", None):
            return None
        x0, y0, vw, vh = self._last_view
        bx0, by0, bx1, by1 = self.covers[0]
        sy = self.box[3] / vh
        return (self.box[0] + ((bx0 + bx1) / 2 - x0) * self.box[2] / vw,
                self.box[1] + ((by0 + by1) / 2 - y0) * sy, (by1 - by0) * sy)


class VideoReader(_View):
    def __init__(self, path, start, dur, box, aspect, focus, speed=1.0, src_zoom=1.0, headroom=1.12, blur=None,
                 blur_boxes=None, cover=None):
        self.box = box
        w, h = box[2], box[3]
        self.pw, self.ph = int(w * headroom) // 2 * 2, int(h * headroom) // 2 * 2
        sw, sh, sdur = probe(path)
        cw, ch, cx, cy = crop_rect(sw, sh, aspect, focus, src_zoom)
        # blur: [[x0, y0, x1, y1], ...] for the whole clip; blur_boxes: [{"t0", "t1", "box"}] only while the SOURCE
        # time is inside [t0, t1] (tools/textboxes.py finds these for burned-in subtitles). Source fractions.
        def to_crop(b):
            x0, y0, x1, y1 = b
            bx0, by0 = max(0, (x0 * sw - cx) * self.pw / cw), max(0, (y0 * sh - cy) * self.ph / ch)
            bx1, by1 = min(self.pw, (x1 * sw - cx) * self.pw / cw), min(self.ph, (y1 * sh - cy) * self.ph / ch)
            return tuple(int(v) for v in (bx0, by0, bx1, by1)) if bx1 > bx0 and by1 > by0 else None
        self.blur = [(None, None, r) for r in map(to_crop, blur or []) if r]
        self.blur += [(e["t0"], e["t1"], r) for e in blur_boxes or [] for r in [to_crop(e["box"])] if r]
        # cover: [[x0, y0, x1, y1]] source fractions of a burned-in caption band: painted solid black, and the
        # renderer puts this Short's own caption on top of it instead of the frame centre
        self.covers = [r for r in map(to_crop, cover or []) if r]
        self.start, self.speed = start, speed
        need = dur * speed
        self.n = int(round(dur * FPS)) + 2
        vf = (f"crop={cw}:{ch}:{cx}:{cy},scale={self.pw}:{self.ph}:flags=lanczos,"
              f"setpts=(PTS-STARTPTS)/{speed},fps={FPS},tpad=stop_mode=clone:stop_duration={dur + 1:.2f}")
        self.proc = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{start:.3f}", "-i", path, "-t", f"{need + 0.3:.3f}",
                                      "-an", "-vf", vf, "-frames:v", str(self.n), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                                     stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self.k, self.last = -1, None

    def frame(self, k, zoom=1.0, focus=(0.5, 0.5)):
        size = self.pw * self.ph * 3
        while self.k < k:
            buf = self.proc.stdout.read(size)
            if len(buf) < size:
                break
            self.last = Image.frombuffer("RGB", (self.pw, self.ph), buf, "raw", "RGB", 0, 1)
            if self.blur:
                ts = self.start + (self.k + 1) / FPS * self.speed
                live = [r for t0, t1, r in self.blur if t0 is None or t0 <= ts <= t1]
                if live:
                    self.last = self.last.copy()
                    for r in live:
                        self.last.paste(self.last.crop(r).filter(ImageFilter.GaussianBlur(14)), r[:2], _feather(r))
            if self.covers:
                self.last = self.last.copy()
                d = ImageDraw.Draw(self.last)
                for r in self.covers:
                    d.rectangle(r, fill=(0, 0, 0))
            self.k += 1
        if self.last is None:
            self.last = Image.new("RGB", (self.pw, self.ph), (20, 20, 20))
        return self.view(self.last, zoom, focus)

    def close(self):
        try:
            self.proc.stdout.close()
            self.proc.kill()
        except Exception:
            pass


def _feather(r, edge=6):
    """Soft-edged mask for a blur box so it blends in instead of showing a hard rectangle."""
    w, h = r[2] - r[0], r[3] - r[1]
    e = max(1, min(edge, w // 4, h // 4))
    m = Image.new("L", (w, h), 0)
    m.paste(255, (e, e, max(e + 1, w - e), max(e + 1, h - e)))
    return m.filter(ImageFilter.GaussianBlur(e / 2))


class ImageReader(_View):
    """Still image. focus/src_zoom pick the crop like a video clip; pan=[[fx, fy], [fx, fy]] slides the crop
    centre across the photo over the segment (a moving shot from a still)."""

    def __init__(self, img, box, headroom=1.2, focus=(0.5, 0.5), src_zoom=1.0, pan=None, dur=1.0):
        self.box = box
        self.rgba = img.mode == "RGBA"   # cards float over the previous shot's blurred background
        w, h = box[2], box[3]
        pw, ph = int(w * headroom), int(h * headroom)
        src = img if self.rgba else img.convert("RGB")
        self.pan, self.n = None, max(1, int(round(dur * FPS)))
        if pan:
            self.src, self.pw, self.ph = src, pw, ph
            self.pan = [tuple(pan[0]), tuple(pan[1])]
            self.cw, self.ch = crop_rect(src.width, src.height, w / h, (0.5, 0.5), src_zoom)[:2]
            return
        cw, ch, cx, cy = crop_rect(src.width, src.height, w / h, tuple(focus), src_zoom)
        self.img = src.crop((cx, cy, cx + cw, cy + ch)).resize((pw, ph), Image.LANCZOS)

    def frame(self, k, zoom=1.0, focus=(0.5, 0.5)):
        if self.pan:
            p = min(1.0, k / self.n)
            p = p * p * (3 - 2 * p)  # ease in-out
            fx = self.pan[0][0] + (self.pan[1][0] - self.pan[0][0]) * p
            fy = self.pan[0][1] + (self.pan[1][1] - self.pan[0][1]) * p
            sw, sh = self.src.size
            cx = min(max(fx * sw - self.cw / 2, 0), sw - self.cw)
            cy = min(max(fy * sh - self.ch / 2, 0), sh - self.ch)
            vw, vh = self.cw / zoom, self.ch / zoom
            x0, y0 = cx + (self.cw - vw) / 2, cy + (self.ch - vh) / 2
            return self.src.resize((self.box[2], self.box[3]), Image.BICUBIC, box=(x0, y0, x0 + vw, y0 + vh))
        return self.view(self.img, zoom, focus)

    def close(self):
        pass


def open_reader(spec, box, dur, offset, theme, report):
    """Build a frame reader for one timeline segment. `report` collects what was used (for credits/QA)."""
    kind = spec.get("kind") or ("card" if "headline" in spec else "video")
    aspect = box[2] / box[3]
    if kind == "card":
        img = gfx.card_image(box[2], box[3], theme, spec.get("outlet", ""), spec["headline"], spec.get("date", ""), spec.get("tag", "report"))
        report.append({"kind": "card", "outlet": spec.get("outlet"), "headline": spec["headline"]})
        return ImageReader(img, box, headroom=1.08)
    if kind == "image":
        p = rel(spec["src"])
        if not os.path.exists(p) and spec.get("url"):  # press photos are not kept in git: fetch them again
            os.makedirs(os.path.dirname(p), exist_ok=True)
            subprocess.run(["curl", "-sfL", "-A", "Mozilla/5.0", "-o", p, spec["url"]])
        if os.path.exists(p):
            report.append({"kind": "image", "src": spec["src"], "credit": spec.get("credit")})
            return ImageReader(Image.open(p), box, focus=spec.get("focus", (0.5, 0.5)), src_zoom=float(spec.get("src_zoom", 1.0)),
                               pan=spec.get("pan"), dur=dur)
    path = fetch(spec.get("src")) if kind in ("video", "image") else None
    if path:
        start = float(spec.get("start", 0)) + offset * float(spec.get("speed", 1.0))
        focus = spec.get("focus", "auto")
        if focus == "auto":
            focus = auto_focus(path, start, dur * float(spec.get("speed", 1.0)), aspect)
        report.append({"kind": "video", "src": spec.get("src"), "start": round(start, 2), "dur": round(dur, 2), "focus": focus})
        return VideoReader(path, start, dur, box, aspect, focus, float(spec.get("speed", 1.0)), float(spec.get("src_zoom", 1.0)),
                           blur=spec.get("blur"), blur_boxes=spec.get("blur_boxes"), cover=spec.get("cover"))
    hint = spec.get("src") or spec.get("search", "")
    if spec.get("start") is not None:
        hint += f"  •  {spec.get('start')}s–{spec.get('end', '?')}s"
    report.append({"kind": "placeholder", "desc": spec.get("desc"), "src": spec.get("src"), "search": spec.get("search")})
    return ImageReader(gfx.slate_image(int(box[2] * 1.2), int(box[3] * 1.2), spec.get("desc", "footage"), hint), box)
