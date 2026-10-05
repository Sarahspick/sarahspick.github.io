"""Animated map of Walmart's US rollout, drawn from Thomas Holmes' public data
(store and distribution-center opening dates, 1962-2005, users.econ.umn.edu/~holmes/data/WalMart/).
Stores are placed at their ZIP centroid (Census 2020 ZCTA gazetteer), DCs at Holmes' coordinates.

grow(dur)  -> frame(t): the network spreading out from Bentonville, camera widening as it grows
full(dur)  -> frame(t): every store, with a 10-mile radius around each one shaded
"""
import csv
import json
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from .config import asset
from .doc_gfx import ACCENT, MUTED, SOFT, WHITE, _text, ease, ease_io, fade, font

W, H = 1920, 1080
BG = (7, 11, 18)
LAND = (19, 27, 39)
EDGE = (52, 66, 86)
STORE = (64, 160, 255)
DC = (255, 179, 64)

# Albers equal-area conic for the contiguous US
_P1, _P2, _P0, _L0 = map(math.radians, (29.5, 45.5, 37.5, -96.0))
_N = (math.sin(_P1) + math.sin(_P2)) / 2
_C = math.cos(_P1) ** 2 + 2 * _N * math.sin(_P1)
_R0 = math.sqrt(_C - 2 * _N * math.sin(_P0)) / _N
EARTH_MI = 3958.8


def proj(lat, lon):
    p, l = math.radians(lat), math.radians(lon)
    r = math.sqrt(_C - 2 * _N * math.sin(p)) / _N
    th = _N * (l - _L0)
    return r * math.sin(th), _R0 - r * math.cos(th)   # unit-sphere units; 1 unit = EARTH_MI miles


def _year(s):
    m, d, y = s.strip().split("/")
    return int(y) + (int(m) - 1) / 12


class Network:
    def __init__(self):
        zl = json.load(open(asset("data", "holmes_zip_latlon.json")))
        self.stores = []
        for r in csv.DictReader(open(asset("data", "holmes_store_openings.csv"))):
            z = r["ZIPCODE"].strip().zfill(5)
            if z in zl:
                self.stores.append((_year(r["OPENDATE"]), *proj(*zl[z])))
        self.stores.sort()
        self.dcs = []
        for r in csv.DictReader(open(asset("data", "holmes_dc_openings.csv"))):
            self.dcs.append((_year(r["OPENDATE"]), *proj(float(r["lat"]), float(r["long"]))))
        self.dcs.sort()
        gj = json.load(open(asset("data", "us_states.geojson")))
        self.states = []
        for f in gj["features"]:
            if f["properties"].get("name") in ("Alaska", "Hawaii", "Puerto Rico"):
                continue
            g = f["geometry"]
            polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
            for poly in polys:
                ring = poly[0]
                self.states.append(np.array([proj(lat, lon) for lon, lat in ring]))
        allp = np.concatenate(self.states)
        self.us_box = (allp[:, 0].min(), allp[:, 1].min(), allp[:, 0].max(), allp[:, 1].max())
        self.st = np.array([(x, y) for _, x, y in self.stores])
        self.st_year = np.array([y for y, _, _ in self.stores])
        self.dc = np.array([(x, y) for _, x, y in self.dcs])
        self.dc_year = np.array([y for y, _, _ in self.dcs])
        self.home = proj(36.37, -94.21)   # Bentonville

    def box_until(self, year, pad=0.18, min_w=0.16):
        m = self.st_year <= year
        pts = np.concatenate([self.st[m], self.dc[self.dc_year <= year], [self.home]])
        x0, y0 = pts.min(0)
        x1, y1 = pts.max(0)
        w, h = max(x1 - x0, min_w), max(y1 - y0, min_w * 9 / 16)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        return cx, cy, w * (1 + pad), h * (1 + pad)


def _camera_fit(cx, cy, w, h, frame_w=1540, frame_h=860):
    s = min(frame_w / w, frame_h / h)
    return cx, cy, s


class _Painter:
    def __init__(self, net):
        self.net = net

    def to_px(self, pts, cam):
        cx, cy, s = cam
        return np.stack([W / 2 + 150 + (pts[:, 0] - cx) * s, H / 2 - 10 - (pts[:, 1] - cy) * s], 1)

    def base(self, cam):
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        for ring in self.net.states:
            p = self.to_px(ring, cam)
            d.polygon([tuple(q) for q in p], fill=LAND)
        for ring in self.net.states:
            p = self.to_px(ring, cam)
            d.line([tuple(q) for q in p] + [tuple(p[0])], fill=EDGE, width=1)
        return img


def grow(dur, y0=1962.0, y1=2005.9, cite="Data: Holmes (2011), Econometrica 79(1). Store locations by ZIP code."):
    net = Network()
    pt = _Painter(net)
    full = _camera_fit(*_box_center(net.us_box))
    state = {"cam": None}
    t_end = dur * 0.86

    def year_at(t):
        return y0 + (y1 - y0) * ease_io(min(1.0, t / t_end)) ** 1.0

    def frame(t):
        yr = year_at(t)
        target = _camera_fit(*net.box_until(yr + 1.5))
        if target[2] < full[2]:
            target = full
        cam = state["cam"]
        if cam is None or t == 0:
            cam = _camera_fit(*net.box_until(y0 + 6))
        k = 0.06
        cam = tuple(c + (g - c) * k for c, g in zip(cam, target)) if state["cam"] is not None else cam
        state["cam"] = cam
        img = pt.base(cam)
        _dots(img, pt, cam, yr, net)
        d = ImageDraw.Draw(img, "RGBA")
        a = fade(t, dur, 0.6, 0.6)
        _text(d, (104, H - 470), f"{int(yr)}", font("serif", 132, "SemiBold"), WHITE, a)
        n_st = int((net.st_year <= yr).sum())
        n_dc = int((net.dc_year <= yr).sum())
        _legend(d, a, n_st, n_dc)
        _text(d, (110, H - 70), cite, font("mono", 20), MUTED, a)
        return img.convert("RGBA")
    return frame


def full(dur, cite="Stores as of 2005 (Holmes data). Shaded: within 10 miles of a store."):
    net = Network()
    pt = _Painter(net)
    cam0 = _camera_fit(*_box_center(net.us_box))
    cov_cache = {}

    def frame(t):
        z = 1 + 0.06 * ease_io(t / dur)
        cam = (cam0[0] + 0.02 * ease_io(t / dur), cam0[1] - 0.01 * ease_io(t / dur), cam0[2] * z)
        img = pt.base(cam)
        a_cov = ease((t - 0.8) / 2.0)
        if a_cov > 0:
            px = pt.to_px(net.st, cam)
            r = 10 / EARTH_MI * cam[2]
            cov = Image.new("L", (W, H), 0)
            cd = ImageDraw.Draw(cov)
            for x, y in px:
                cd.ellipse([x - r, y - r, x + r, y + r], fill=255)
            cov = cov.point(lambda v: int(v * 0.42 * a_cov))
            img.paste(Image.new("RGB", (W, H), STORE), (0, 0), cov)
        _dots(img, pt, cam, 9999, net, pop=False)
        d = ImageDraw.Draw(img, "RGBA")
        a = fade(t, dur, 0.6, 0.6)
        _text(d, (104, H - 330), "10 MILES", font("serif", 96, "SemiBold"), WHITE, a)
        _text(d, (110, H - 210), "AROUND EVERY STORE", font("sans", 26, "Medium"), SOFT, a, spacing=3)
        _text(d, (110, H - 70), cite, font("mono", 20), MUTED, a)
        return img.convert("RGBA")
    return frame


def _box_center(box):
    x0, y0, x1, y1 = box
    return (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) * 1.04, (y1 - y0) * 1.04


def _dots(img, pt, cam, yr, net, pop=True):
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    sharp = ImageDraw.Draw(img)
    m = net.st_year <= yr
    px = pt.to_px(net.st[m], cam)
    ages = yr - net.st_year[m]
    r0 = max(1.6, min(4.5, cam[2] * 0.0016))
    for (x, y), age in zip(px, ages):
        if pop and age < 0.8:
            k = age / 0.8
            rr = r0 + 9 * (1 - k)
            gd.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(140, 200, 255))
        gd.ellipse([x - r0 * 1.8, y - r0 * 1.8, x + r0 * 1.8, y + r0 * 1.8], fill=(30, 90, 170))
    for (x, y) in px:
        sharp.ellipse([x - r0, y - r0, x + r0, y + r0], fill=STORE)
    md = net.dc_year <= yr
    dpx = pt.to_px(net.dc[md], cam)
    dages = yr - net.dc_year[md]
    s = max(4.0, min(9.0, r0 * 2.1))
    for (x, y), age in zip(dpx, dages):
        if pop and age < 1.2:
            k = age / 1.2
            rr = s + 30 * k
            gd.ellipse([x - rr, y - rr, x + rr, y + rr], outline=(int(255 * (1 - k)), int(170 * (1 - k)), int(60 * (1 - k))), width=3)
        gd.rectangle([x - s * 1.6, y - s * 1.6, x + s * 1.6, y + s * 1.6], fill=(120, 80, 20))
    glow = glow.filter(ImageFilter.GaussianBlur(5))
    arr = np.minimum(255, np.asarray(img, dtype=np.int16) + np.asarray(glow, dtype=np.int16)).astype(np.uint8)
    img.paste(Image.fromarray(arr))
    sharp = ImageDraw.Draw(img)
    for (x, y) in dpx:
        sharp.rectangle([x - s, y - s, x + s, y + s], fill=DC, outline=(20, 14, 6))


def _legend(d, a, n_st, n_dc):
    x, y = 116, H - 300
    d.ellipse([x - 7, y + 10, x + 7, y + 24], fill=STORE + (int(255 * a),))
    _text(d, (x + 22, y), f"{n_st:,}", font("sans", 34, "SemiBold"), WHITE, a)
    _text(d, (x + 22, y + 42), "WALMART STORES", font("sans", 20, "Medium"), SOFT, a, spacing=3)
    y += 100
    d.rectangle([x - 7, y + 10, x + 7, y + 24], fill=DC + (int(255 * a),))
    _text(d, (x + 22, y), f"{n_dc:,}", font("sans", 34, "SemiBold"), WHITE, a)
    _text(d, (x + 22, y + 42), "DISTRIBUTION CENTERS", font("sans", 20, "Medium"), SOFT, a, spacing=3)
