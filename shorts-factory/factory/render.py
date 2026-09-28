"""Script JSON -> finished 1080x1920 Short: narration, synced captions, cut-on-sentence footage, SFX, hook cover."""
import datetime
import json
import math
import os
import re
import subprocess
import time

import numpy as np
import soundfile as sf
from PIL import Image

from . import gfx
from .config import FPS, H, OUTPUT, SR, THEMES, W, WORK, load_channel
from .media import open_reader, parse_aspect
from .sfx import SfxLibrary, measure
from .voice import Narrator, _norm_words

ANCHOR_RE = re.compile(r"(start|end|line\d+|word:[^+]+?)([+-]\d*\.?\d+)?")


def _ease_out(p):
    p = min(max(p, 0.0), 1.0)
    return 1 - (1 - p) ** 3


def _pop(p):
    """0 -> overshoot -> 1 scale curve for pop-in sprites."""
    if p >= 1:
        return 1.0
    return 0.35 + 0.65 * _ease_out(p / 0.7) if p < 0.7 else 1.0 + 0.12 * math.sin((p - 0.7) / 0.3 * math.pi)


class Short:
    def __init__(self, script_path, channel_path=None, theme=None, voice=None, speed=None):
        with open(script_path, encoding="utf-8") as f:
            self.sc = json.load(f)
        self.ch = load_channel(channel_path)
        if theme:
            self.ch["theme"] = theme
        self.theme = self.ch.get("theme", "dark")
        self.lang = self.sc.get("lang", self.ch.get("lang", "en"))
        vcfg = dict(self.ch["voice"])
        vcfg.update(self.sc.get("voice", {}))
        if voice:
            vcfg["name"] = voice
        if speed:
            vcfg["speed"] = speed
        self.vcfg = vcfg
        pron = dict(self.ch.get("pronounce", {}))
        pron.update(self.sc.get("pronounce", {}))
        self.pron = pron
        self.id = self.sc["id"]
        self.work = os.path.join(WORK, self.id)
        os.makedirs(self.work, exist_ok=True)
        self.page = gfx.Page(self.ch, self.sc["title"])
        self.sfx = SfxLibrary()
        self.warnings = []

    # ------------------------------------------------------------------ timing
    def narrate(self):
        narr = Narrator(self.vcfg["name"], self.vcfg.get("speed", 1.12), self.lang, self.pron)
        items = [dict(self.sc["hook"], _kind="hook")] + [dict(s, _kind="sent") for s in self.sc["sentences"]]
        t = float(self.sc.get("lead_in", 0.0))
        gap = float(self.sc.get("gap", 0.12))
        for it in items:
            lines = [it["say"]] if it["_kind"] == "hook" else it["lines"]
            r = narr.speak(lines)
            it.update(_audio=r["audio"], _dur=r["dur"], _ls=r["line_starts"], _words=r["words"],
                      _t0=t, _t1=t + r["dur"], _asr=r["asr"], _matched=r["matched"])
            t = it["_t1"] + float(it.get("pause_after", gap))
        self.items = items
        self.narr_sr = narr.sr
        self.total = items[-1]["_t1"] + float(self.sc.get("tail", 0.5))
        self.hook_end = items[1]["_t0"] if len(items) > 1 else self.total

    def at(self, it, spec, default="start"):
        spec = default if spec is None else spec
        if isinstance(spec, (int, float)):
            return it["_t0"] + float(spec)
        m = ANCHOR_RE.fullmatch(str(spec).strip())
        if not m:
            raise ValueError(f"bad time anchor {spec!r}")
        base, off = m.group(1), float(m.group(2) or 0)
        if base == "start":
            v = 0.0
        elif base == "end":
            v = it["_dur"]
        elif base.startswith("line"):
            ls = it["_ls"]
            v = ls[min(int(base[4:]) - 1, len(ls) - 1)]
        else:
            target = (_norm_words(base[5:]) or [""])[0]
            v = next((tt for w, tt in it["_words"] if w == target), None)
            if v is None:
                v = next((tt for w, tt in it["_words"] if w.startswith(target)), None)
            if v is None:
                self.warnings.append(f"anchor {spec!r} not found in: {it.get('lines') or it.get('say')}")
                v = 0.0
        return it["_t0"] + v + off

    def next_start(self, idx):
        return self.items[idx + 1]["_t0"] if idx + 1 < len(self.items) else self.total

    # ------------------------------------------------------------------ plan
    def plan(self):
        clips = self.sc["clips"]
        cuts = []
        for i, it in enumerate(self.items):
            if "clips" in it:
                for j, cid in enumerate(it["clips"]):
                    cuts.append((0.0 if (i == 0 and j == 0) else self.at(it, f"line{j + 1}" if j else "start"), cid, it))
            elif "clip" in it:
                cuts.append((0.0 if i == 0 else it["_t0"], it["clip"], it))
        cuts.sort(key=lambda c: c[0])
        segs = []
        for k, (t0, cid, it) in enumerate(cuts):
            t1 = cuts[k + 1][0] if k + 1 < len(cuts) else self.total
            if t1 - t0 < 1e-3:
                continue
            if cid not in clips:
                raise KeyError(f"clip id '{cid}' used but not defined in 'clips'")
            if segs and segs[-1]["cid"] == cid and not it.get("recut"):
                segs[-1]["t1"] = t1
                continue
            segs.append({"cid": cid, "t0": t0, "t1": t1, "punch": bool(it.get("punch"))})
        for s in segs:
            spec = clips[s["cid"]]
            s["box"] = self.page.media_box(parse_aspect(spec.get("aspect", self.sc.get("aspect", "4:3"))))
        self.segs = segs

        cues = []
        anns = []
        for i, it in enumerate(self.items):
            for c in it.get("sfx", []):
                cues.append({"t": self.at(it, c.get("at")), "id": c["id"], "gain": float(c.get("gain", 0)),
                             "dur": float(c["dur"]) if c.get("dur") else None})
            for a in it.get("annotate", []):
                a = dict(a)
                a["t0"] = self.at(it, a.get("at"))
                a["t1"] = self.at(it, a["until"]) if "until" in a else self.next_start(i)
                a["hook"] = it["_kind"] == "hook"
                anns.append(a)
                if a["type"] == "cursor" and a.get("click", True) and a.get("sfx", "mouse_click"):
                    cues.append({"t": a["t0"] + 0.38, "id": a.get("sfx", "mouse_click"), "gain": 0})
                if a["type"] == "stamp" and a.get("sfx", "stamp"):
                    cues.append({"t": a["t0"] + 0.1, "id": a.get("sfx", "stamp"), "gain": 0})
                if a["type"] in ("arrow", "circle") and a.get("sfx"):
                    cues.append({"t": a["t0"], "id": a["sfx"], "gain": 0})
        self.cues = sorted(cues, key=lambda c: c["t"])
        self.anns = anns

        caps = []
        for i, it in enumerate(self.items):
            if it["_kind"] == "hook":
                continue
            if not self.page.caption_font(it["lines"])[1]:
                self.warnings.append(f"caption line too long even at 50px (will wrap): {it['lines']}")
            end = self.next_start(i)
            for j in range(len(it["lines"])):
                t0 = it["_t0"] + (it["_ls"][j] if j else 0.0)
                t1 = it["_t0"] + it["_ls"][j + 1] if j + 1 < len(it["lines"]) else end
                caps.append((t0, t1, i, j + 1))
        self.caps = caps

    # ------------------------------------------------------------------ audio
    def mix_audio(self):
        sr = self.narr_sr
        buf = np.zeros(int((self.total + 1) * sr), np.float32)
        for it in self.items:
            s = int(round(it["_t0"] * sr))
            a = it["_audio"]
            buf[s:s + len(a)] += a[:max(0, len(buf) - s)]
        raw = os.path.join(self.work, "narration_raw.wav")
        sf.write(raw, buf[:int(self.total * sr)], sr)
        lufs, _ = measure(raw)
        narr = os.path.join(self.work, "narration.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", f"volume={-16 - lufs:.2f}dB",
                        "-ar", str(SR), "-ac", "2", narr], check=True)
        inputs, chains, labels = ["-i", narr], [], ["[0:a]"]
        for n, c in enumerate(self.cues, start=1):
            inputs += ["-i", self.sfx.path(c["id"])]
            d = max(0, int(round(c["t"] * 1000)))
            trim = ""
            if c.get("dur"):
                fade = min(0.35, c["dur"] / 3)
                trim = f"atrim=0:{c['dur']:.3f},afade=t=out:st={c['dur'] - fade:.3f}:d={fade:.3f},"
            chains.append(f"[{n}:a]{trim}adelay={d}:all=1,volume={c['gain']:.1f}dB[s{n}]")
            labels.append(f"[s{n}]")
        fc = ";".join(chains + [f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0:dropout_transition=0,"
                                f"apad,atrim=0:{self.total:.3f},alimiter=limit=0.89:level=false[m]"])
        mix = os.path.join(self.work, "mix_pre.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", fc, "-map", "[m]", "-ar", str(SR), mix], check=True)
        final = os.path.join(self.work, "mix.wav")
        src = mix
        for _ in range(2):  # gain toward -14 LUFS (YouTube reference); the limiter keeps true peaks under -1 dBFS
            lufs, _ = measure(src)
            g = -14.0 - lufs
            tmp = final + ".tmp.wav"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af",
                            f"volume={g:.2f}dB,alimiter=limit=0.84:attack=2:release=40:level=false",
                            "-ar", str(SR), tmp], check=True)
            os.replace(tmp, final)
            src = final
            if abs(measure(final)[0] + 14.0) < 0.5:
                break
        self.mix = final
        self.loudness = measure(final)

    # ------------------------------------------------------------------ video
    def _seg_zoom(self, seg, spec, t):
        p = (t - seg["t0"]) / max(1e-3, seg["t1"] - seg["t0"])
        kind = spec.get("kind") or ("card" if "headline" in spec else "video")
        kb = spec.get("kb", [1.0, 1.04] if kind == "video" else [1.0, 1.08])
        z = kb[0] + (kb[1] - kb[0]) * p
        if seg["punch"] or spec.get("punch"):
            q = (t - seg["t0"]) / 0.2
            if q < 1:
                z *= 1 + 0.14 * (1 - _ease_out(q))
        return z

    def _draw_ann(self, frame, a, t, box):
        x, y, w, h = box
        p = (t - a["t0"]) / 0.24
        scale = 1.0 if (a["hook"] and a["t0"] <= 1e-3) else _pop(p)
        tx, ty = x + a.get("x", 0.5) * w, y + a.get("y", 0.5) * h
        typ = a["type"]
        if typ == "arrow":
            spr, tip = self._sprite(("arrow", a.get("angle", 35), a.get("len", 230)),
                                    lambda: gfx.arrow_sprite(a.get("len", 230), THEMES[self.theme]["arrow"], a.get("angle", 35)))
            bob = 10 * math.sin((t - a["t0"]) * 2 * math.pi / 0.8)
            rad = math.radians(a.get("angle", 35))
            tx -= bob * math.cos(rad)
            ty -= bob * math.sin(rad)
        elif typ == "circle":
            spr = self._sprite(("ring", a.get("r", 90)), lambda: gfx.ring_sprite(a.get("r", 90), THEMES[self.theme]["arrow"]))
            tip = (spr.width / 2, spr.height / 2)
        elif typ == "cursor":
            spr, tip = self._sprite(("cursor",), gfx.cursor_sprite)
            q = _ease_out((t - a["t0"]) / 0.38)
            tx += (1 - q) * 0.22 * w
            ty += (1 - q) * 0.30 * h
            scale = 1.0
            ct = t - a["t0"] - 0.38
            if 0 <= ct < 0.35 and a.get("click", True):
                ring = gfx.ring_sprite(int(20 + 60 * ct / 0.35), (255, 255, 255), 6)
                ring.putalpha(ring.getchannel("A").point(lambda v: int(v * (1 - ct / 0.35))))
                frame.paste(ring, (int(tx - ring.width / 2), int(ty - ring.height / 2)), ring)
        elif typ == "stamp":
            spr = self._sprite(("stamp", a.get("text", "CLASSIFIED")), lambda: gfx.stamp_sprite(a.get("text", "CLASSIFIED")))
            tip = (spr.width / 2, spr.height / 2)
            q = (t - a["t0"]) / 0.12
            scale = 1.0 if q >= 1 else 1.9 - 0.9 * _ease_out(q)
        else:
            return
        if scale != 1.0:
            spr = spr.resize((max(1, int(spr.width * scale)), max(1, int(spr.height * scale))), Image.BICUBIC)
            tip = (tip[0] * scale, tip[1] * scale)
        frame.paste(spr, (int(tx - tip[0]), int(ty - tip[1])), spr)

    def _sprite(self, key, make):
        if key not in self._sprites:
            self._sprites[key] = make()
        return self._sprites[key]

    def render(self, out_path):
        self._sprites = {}
        clips = self.sc["clips"]
        n_frames = int(math.ceil(self.total * FPS))
        base = self.page.base.convert("RGB")
        hook_seg = self.segs[0]
        hook_ov = self.page.hook_overlay(self.sc["hook"]["big"], hook_seg["box"])
        cap_cache, decor = {}, {}
        report = []
        consumed = {}
        enc = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
             "-i", self.mix, "-map", "0:v", "-map", "1:a",
             "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
             "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-profile:v", "high",
             "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
             "-c:a", "aac", "-b:a", "192k", "-ar", str(SR), "-shortest", "-movflags", "+faststart", out_path],
            stdin=subprocess.PIPE)
        si, reader, cover = -1, None, None
        for k in range(n_frames):
            t = k / FPS
            while si + 1 < len(self.segs) and self.segs[si + 1]["t0"] <= t + 1e-6:
                if reader:
                    reader.close()
                si += 1
                seg = self.segs[si]
                spec = clips[seg["cid"]]
                off = consumed.get(seg["cid"], 0.0) if spec.get("continue", True) else 0.0
                reader = open_reader(spec, seg["box"], seg["t1"] - seg["t0"], off, self.theme, report)
                consumed[seg["cid"]] = off + (seg["t1"] - seg["t0"])
                seg["k0"] = k
            seg = self.segs[si]
            spec = clips[seg["cid"]]
            frame = base.copy()
            in_hook = t < self.hook_end
            if not in_hook:
                state = next(((i, n) for t0, t1, i, n in self.caps if t0 <= t < t1), None)
                if state:
                    if state not in cap_cache:
                        cap_cache[state] = self.page.caption_layer(self.items[state[0]]["lines"], state[1]).convert("RGB")
                    frame.paste(cap_cache[state], (0, self.page.cap_top))
            box = seg["box"]
            if box not in decor:
                decor[box] = self.page.media_frame_decor(box)
            mask, ring = decor[box]
            media = reader.frame(k - seg["k0"], self._seg_zoom(seg, spec, t), tuple(spec.get("kb_focus", (0.5, 0.5))))
            frame.paste(media, (box[0], box[1]), mask)
            frame.paste(ring, (box[0] - 2, box[1] - 2), ring)
            if in_hook:
                frame.paste(hook_ov, (0, 0), hook_ov)
            for a in self.anns:
                if a["t0"] <= t < a["t1"]:
                    self._draw_ann(frame, a, t, box)
            if k == 0:
                cover = frame.copy()
            enc.stdin.write(frame.tobytes())
        if reader:
            reader.close()
        enc.stdin.close()
        enc.wait()
        if enc.returncode:
            raise RuntimeError("ffmpeg encode failed")
        self.report = report
        return cover

    # ------------------------------------------------------------------ outputs
    def build(self, out_dir=None, name=None):
        t_start = time.time()
        out_dir = out_dir or OUTPUT
        os.makedirs(out_dir, exist_ok=True)
        self.narrate()
        self.plan()
        self.mix_audio()
        stamp = datetime.date.today().strftime("%Y%m%d")
        name = name or f"{stamp}_{self.id}_{self.lang.upper()}"
        out = os.path.join(out_dir, name + ".mp4")
        cover = self.render(out)
        cover.save(os.path.join(out_dir, name + "_cover.jpg"), quality=92)
        placeholders = [r for r in self.report if r["kind"] == "placeholder"]
        tl = {
            "id": self.id, "lang": self.lang, "duration": round(self.total, 2), "voice": self.vcfg, "theme": self.theme,
            "loudness_lufs_peak": self.loudness,
            "items": [{"t0": round(it["_t0"], 2), "dur": round(it["_dur"], 2), "line_starts": [round(x, 2) for x in it["_ls"]],
                       "text": it.get("lines") or it.get("say"), "asr": it["_asr"], "matched": it["_matched"]} for it in self.items],
            "segments": [{"clip": s["cid"], "t0": round(s["t0"], 2), "t1": round(s["t1"], 2), "box": s["box"]} for s in self.segs],
            "sfx": [{"t": round(c["t"], 2), "id": c["id"]} for c in self.cues],
            "footage": self.report, "placeholders": len(placeholders), "warnings": self.warnings,
            "render_seconds": round(time.time() - t_start, 1),
        }
        with open(os.path.join(self.work, "timeline.json"), "w", encoding="utf-8") as f:
            json.dump(tl, f, indent=1, ensure_ascii=False)
        self.write_upload_notes(os.path.join(out_dir, name + "_upload.txt"))
        return out, tl

    def write_upload_notes(self, path):
        sc = self.sc
        up = sc.get("upload", {})
        lines = [f"TITLE: {up.get('title', gfx.plain(sc['title']))}", "", "DESCRIPTION:", up.get("description", "")]
        if sc.get("sources"):
            lines += ["", "Sources & footage credits:"] + [f"- {s['name']}: {s.get('url', '')}".rstrip(": ") for s in sc["sources"]]
        tags = up.get("hashtags", [])
        if tags:
            lines += ["", " ".join(tags)]
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines).strip() + "\n")
