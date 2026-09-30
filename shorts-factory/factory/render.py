"""Script JSON -> finished 1080x1920 Short in the classic style.

Layout per frame: same-clip blurred background, full-width foreground clip (1:1 by default, up to 9:16),
headline pinned at the top, big 1-3 word caption chunks synced to the narration, annotations on top.
Audio: narration + downloaded SFX on exact words, mixed to -14 LUFS. No music (added at upload).
"""
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
from .config import FPS, H, OUTPUT, SR, THEMES, W, WORK, load_channel, rel
from .media import fetch, open_reader, parse_aspect, source_meta
from .speech import detect as detect_speech
from .sfx import SfxLibrary, measure
from .voice import _norm_words, make_narrator

ANCHOR_RE = re.compile(r"(start|end|line\d+|word:[^+]+?)([+-]\d*\.?\d+)?")
PUNCT_END = re.compile(r"[.,!?;:…—]$")
CHUNK_WORDS = 3
CHUNK_CHARS = 18


def _ease_out(p):
    p = min(max(p, 0.0), 1.0)
    return 1 - (1 - p) ** 3


def _pop(p, start=0.35):
    """Scale curve for pop-ins: quick grow with a small overshoot, settles at 1."""
    if p >= 1:
        return 1.0
    return start + (1 - start) * _ease_out(p / 0.7) if p < 0.7 else 1.0 + 0.1 * math.sin((p - 0.7) / 0.3 * math.pi)


class Short:
    def __init__(self, script_path, channel_path=None, voice=None, rate=None):
        with open(script_path, encoding="utf-8") as f:
            self.sc = json.load(f)
        self.ch = load_channel(channel_path)
        self.theme = self.ch.get("theme", "dark")
        self.lang = self.sc.get("lang", self.ch.get("lang", "en"))
        vcfg = dict(self.ch.get("voices", {}).get(self.lang) or self.ch["voice"])  # per-language default voice
        vcfg.update(self.sc.get("voice", {}))
        if voice:
            vcfg["voice_id" if vcfg.get("engine") in ("elevenlabs", "typecast") else "name"] = voice
        if rate:
            vcfg["rate"] = rate
        self.vcfg = vcfg
        self.pron = {**self.ch.get("pronounce", {}), **self.sc.get("pronounce", {})}
        self.id = self.sc["id"]
        self.work = os.path.join(WORK, self.id if self.lang == "en" else f"{self.id}_{self.lang}")
        os.makedirs(self.work, exist_ok=True)
        self.brand = self.ch.get("channels", {}).get(self.lang, {})  # per-language channel: name, handle, accent
        gfx.set_accent(self.brand.get("accent", gfx.YELLOW))
        self.title_img, self.title_bottom = gfx.title_layer(self.sc["title"])
        self.sfx = SfxLibrary()
        self.warnings = []

    # ------------------------------------------------------------------ narration + timing
    def narrate(self):
        narr = make_narrator(self.vcfg, self.lang, self.pron)
        items = [dict(self.sc["hook"], _kind="hook")] + [dict(s, _kind="sent") for s in self.sc["sentences"]]
        t = float(self.sc.get("lead_in", 0.0))
        gap = float(self.sc.get("gap", 0.06))
        for it in items:
            r = narr.speak(it["lines"])
            it.update(_audio=r["audio"], _dur=r["dur"], _ls=[float(x) for x in r["line_starts"]], _tokens=r["tokens"],
                      _t0=t, _t1=t + r["dur"], _heard=r["heard"], _matched=r["matched"])
            for tk in it["_tokens"]:
                tk["t"] = float(tk["t"])
            t = it["_t1"] + float(it.get("pause_after", gap))
        self.items = items
        self.narr_sr = narr.sr
        self.total = items[-1]["_t1"] + float(self.sc.get("tail", 0.4))

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
            v = next((tk["t"] for tk in it["_tokens"] if target in tk["norm"]), None)
            if v is None:
                v = next((tk["t"] for tk in it["_tokens"] if any(n.startswith(target) for n in tk["norm"])), None)
            if v is None:
                self.warnings.append(f"anchor {spec!r} not found in {it['lines']}")
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
            s["box"] = gfx.fg_box(parse_aspect(spec.get("aspect", self.sc.get("aspect", "1:1"))), self.title_bottom)
        self.segs = segs

        cues, anns = [], []
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
                    cues.append({"t": a["t0"] + 0.38, "id": a.get("sfx", "mouse_click"), "gain": 0, "dur": None})
                if a["type"] == "stamp" and a.get("sfx", "stamp"):
                    cues.append({"t": a["t0"] + 0.1, "id": a.get("sfx", "stamp"), "gain": 0, "dur": None})
                if a["type"] in ("arrow", "circle") and a.get("sfx"):
                    cues.append({"t": a["t0"], "id": a["sfx"], "gain": 0, "dur": None})
        intro = self.sc.get("intro_sfx", self.ch.get("intro_sfx"))  # every Short opens on one sound at 0.0s
        if intro:
            cues.append({"t": 0.0, "id": intro, "gain": float(self.ch.get("intro_gain", 0)), "dur": None})
        allow = self.ch.get("sfx_allow")
        if allow is not None:
            for c in cues:
                if c["id"] not in allow:
                    self.warnings.append(f"sfx '{c['id']}' dropped: not in channel sfx_allow")
            cues = [c for c in cues if c["id"] in allow]
        self.cues = sorted(cues, key=lambda c: c["t"])
        self.anns = anns
        self.chunks = self._chunks()

    def _chunks(self):
        """Group narration tokens into 1-3 word caption chunks with absolute start/end times."""
        chunks = []
        for i, it in enumerate(self.items):
            toks = it["_tokens"]
            groups, cur = [], []
            for tk in toks:
                if cur:
                    text_len = len(" ".join(x["text"] for x in cur + [tk]))
                    if (len(cur) >= CHUNK_WORDS or text_len > CHUNK_CHARS or PUNCT_END.search(cur[-1]["text"])
                            or tk["line"] != cur[-1]["line"]):
                        groups.append(cur)
                        cur = []
                cur.append(tk)
            if cur:
                groups.append(cur)
            for g_i, g in enumerate(groups):
                t0 = it["_t0"] + g[0]["t"]
                last_end = it["_t0"] + (groups[g_i + 1][0]["t"] if g_i + 1 < len(groups) else it["_dur"])
                chunks.append({"t0": t0, "end": last_end, "words": tuple((tk["text"], tk["hl"]) for tk in g)})
        for k, c in enumerate(chunks):
            nxt = chunks[k + 1]["t0"] if k + 1 < len(chunks) else self.total
            c["t1"] = nxt if nxt - c["end"] < 0.6 else c["end"] + 0.35
        return chunks

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
        orig = self.original_audio()
        if orig:
            inputs += ["-i", orig]
            labels.append(f"[{len(inputs) // 2 - 1}:a]")
        bgm = self.background_music(narr)
        if bgm:
            inputs += ["-i", bgm]
            labels.append(f"[{len(inputs) // 2 - 1}:a]")
        base = len(inputs) // 2
        for n, c in enumerate(self.cues, start=base):
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
            tmp = final + ".tmp.wav"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af",
                            f"volume={-14.0 - lufs:.2f}dB,alimiter=limit=0.84:attack=2:release=40:level=false",
                            "-ar", str(SR), tmp], check=True)
            os.replace(tmp, final)
            src = final
            if abs(measure(final)[0] + 14.0) < 0.5:
                break
        self.mix = final
        self.loudness = measure(final)

    def background_music(self, narr):
        """Optional licensed music bed ("bgm": {"file": path, "lufs": -30, "start": 0}) in the script or channel.

        Looped to the Short's length, normalised, ducked under the narration (sidechain) and faded out at the end.
        Only use music the channel is allowed to use (YouTube Audio Library, a paid library, or tracks the user
        supplies); popular songs go in through YouTube's own editor instead."""
        cfg = self.sc.get("bgm", self.ch.get("bgm"))
        if not cfg or not cfg.get("file") or not os.path.exists(rel(cfg["file"])):
            return None
        src = rel(cfg["file"])
        lufs = measure(src)[0]
        gain = float(cfg.get("lufs", -30)) - lufs
        out = os.path.join(self.work, "bgm_ducked.wav")
        fade = min(1.5, self.total / 4)
        fc = (f"[0:a]atrim=start={float(cfg.get('start', 0)):.2f},asetpts=PTS-STARTPTS,volume={gain:.2f}dB,"
              f"atrim=0:{self.total:.3f},afade=t=out:st={self.total - fade:.3f}:d={fade:.3f}[m];"
              f"[m][1:a]sidechaincompress=threshold=0.03:ratio=6:attack=15:release=350[d]")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-stream_loop", "-1", "-i", src, "-i", narr,
                        "-filter_complex", fc, "-map", "[d]", "-ar", str(SR), "-ac", "2", out], check=True)
        return out

    def original_audio(self):
        """The footage's own sound under the narration, cut exactly like the picture (same starts, speeds, hard cuts).

        Script option "orig_audio": {"lufs": -30} sets the level (each source is loudness-normalised first);
        a clip can set "orig_gain" (dB, relative) or "orig_gain": null to mute it. Off when the script has no
        "orig_audio" (older scripts stay silent under the narration)."""
        oa = self.sc.get("orig_audio")
        if not oa:
            return None
        target = float(oa.get("lufs", -30))
        clips, consumed, levels = self.sc["clips"], {}, {}
        buf = np.zeros((int((self.total + 1) * SR), 2), np.float32)
        for seg in self.segs:
            spec = clips[seg["cid"]]
            dur = seg["t1"] - seg["t0"]
            off = consumed.get(seg["cid"], 0.0) if spec.get("continue", True) else 0.0
            consumed[seg["cid"]] = off + dur
            kind = spec.get("kind") or ("card" if "headline" in spec else "video")
            if kind != "video" or not spec.get("src") or ("orig_gain" in spec and spec["orig_gain"] is None):
                continue
            path = fetch(spec["src"])
            if not path:
                continue
            if path not in levels:
                levels[path] = measure(path)[0]
            if levels[path] < -60:  # silent source
                continue
            speed = float(spec.get("speed", 1.0))
            start = float(spec.get("start", 0)) + off * speed
            if not spec.get("orig_speech"):
                sp = detect_speech(path, start, dur * speed)
                if sp["speech"]:
                    self.warnings.append(f"orig audio muted for {seg['cid']} at {start:.1f}s: speech ({sp['lang']}) "
                                         f"\"{sp['text'][:40]}\"")
                    continue
            tempo, chain = speed, []
            while tempo < 0.5:
                chain.append("atempo=0.5")
                tempo /= 0.5
            while tempo > 2.0:
                chain.append("atempo=2.0")
                tempo /= 2.0
            chain.append(f"atempo={tempo:.4f}")
            gain = target - levels[path] + float(spec.get("orig_gain", 0))
            fade = min(0.012, dur / 4)
            af = ",".join(chain + [f"volume={gain:.2f}dB", f"afade=t=in:d={fade:.3f}",
                                   f"afade=t=out:st={max(0.0, dur - fade):.3f}:d={fade:.3f}"])
            r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{start:.3f}", "-t", f"{dur * speed + 0.05:.3f}", "-i", path,
                                "-vn", "-af", af, "-t", f"{dur:.3f}", "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                               capture_output=True)
            a = np.frombuffer(r.stdout, np.float32).reshape(-1, 2)
            i0 = int(round(seg["t0"] * SR))
            n = min(len(a), len(buf) - i0)
            buf[i0:i0 + n] += a[:n]
        out = os.path.join(self.work, "original_audio.wav")
        sf.write(out, buf[:int(self.total * SR)], SR)
        return out

    # ------------------------------------------------------------------ video
    def _seg_zoom(self, seg, spec, t):
        p = (t - seg["t0"]) / max(1e-3, seg["t1"] - seg["t0"])
        kind = spec.get("kind") or ("card" if "headline" in spec else "video")
        kb = spec.get("kb", [1.0, 1.05] if kind == "video" else [1.0, 1.06])
        z = kb[0] + (kb[1] - kb[0]) * p
        if seg["punch"] or spec.get("punch"):
            q = (t - seg["t0"]) / 0.2
            if q < 1:
                z *= 1 + 0.14 * (1 - _ease_out(q))
        return z

    def _sprite(self, key, make):
        if key not in self._sprites:
            self._sprites[key] = make()
        return self._sprites[key]

    def _draw_ann(self, frame, a, t, box):
        x, y, w, h = box
        p = (t - a["t0"]) / 0.24
        scale = 1.0 if (a["hook"] and a["t0"] <= 1e-3) else _pop(p)
        tx, ty = x + a.get("x", 0.5) * w, y + a.get("y", 0.5) * h
        typ = a["type"]
        red = THEMES[self.theme]["arrow"]
        if typ == "arrow":
            spr, tip = self._sprite(("arrow", a.get("angle", 35), a.get("len", 230)),
                                    lambda: gfx.arrow_sprite(a.get("len", 230), red, a.get("angle", 35)))
            bob = 10 * math.sin((t - a["t0"]) * 2 * math.pi / 0.8)
            rad = math.radians(a.get("angle", 35))
            tx -= bob * math.cos(rad)
            ty -= bob * math.sin(rad)
        elif typ == "circle":
            spr = self._sprite(("ring", a.get("r", 90)), lambda: gfx.ring_sprite(a.get("r", 90), red))
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

    def render(self, out_path):
        self._sprites = {}
        clips = self.sc["clips"]
        n_frames = int(math.ceil(self.total * FPS))
        title = self.title_img
        report, consumed = [], {}
        last_bg = Image.new("RGB", (W, H), (12, 12, 14))
        enc = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
             "-i", self.mix, "-map", "0:v", "-map", "1:a",
             "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
             "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-profile:v", "high",
             "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
             "-c:a", "aac", "-b:a", "192k", "-ar", str(SR), "-shortest", "-movflags", "+faststart", out_path],
            stdin=subprocess.PIPE)
        si, ci, reader, cover = -1, 0, None, None
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
            x, y, w, h = seg["box"]
            media = reader.frame(k - seg["k0"], self._seg_zoom(seg, spec, t), tuple(spec.get("kb_focus", (0.5, 0.5))))
            if getattr(reader, "rgba", False):
                frame = last_bg.copy()
                frame.paste(media, (x, y), media)
            elif (w, h) == (W, H):
                frame = media.copy()
            else:
                frame = gfx.blurred_bg(media)
                last_bg = frame.copy()
                frame.paste(media, (x, y))
            iz = float(self.ch.get("intro_zoom", 0))
            if iz and t < 1.0:  # slow push-in over the first second (user rule)
                z = 1 + iz * (t / 1.0) ** 0.8
                vw, vh = W / z, H / z
                frame = frame.resize((W, H), Image.BICUBIC, box=((W - vw) / 2, (H - vh) / 2, (W + vw) / 2, (H + vh) / 2))
            frame.paste(title, (0, 0), title)
            while ci + 1 < len(self.chunks) and self.chunks[ci + 1]["t0"] <= t + 1e-6:
                ci += 1
            c = self.chunks[ci] if self.chunks and self.chunks[ci]["t0"] <= t < self.chunks[ci]["t1"] else None
            if c:
                cap = gfx.caption_image(c["words"])
                s = _pop((t - c["t0"]) / 0.12, start=0.78) if t - c["t0"] < 0.12 else 1.0
                if s != 1.0:
                    cap = cap.resize((max(1, int(cap.width * s)), max(1, int(cap.height * s))), Image.BICUBIC)
                cc = reader.cover_center() if hasattr(reader, "cover_center") else None
                cy = cc[1] if cc else gfx.CAPTION_CY
                if cc and cap.height > cc[2] * 0.95:  # keep the caption inside its black box
                    f = cc[2] * 0.95 / cap.height
                    cap = cap.resize((max(1, int(cap.width * f)), max(1, int(cap.height * f))), Image.BICUBIC)
                frame.paste(cap, (int((W - cap.width) / 2), int(cy - cap.height / 2)), cap)
            for a in self.anns:
                if a["t0"] <= t < a["t1"]:
                    self._draw_ann(frame, a, t, seg["box"])
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
        tl = {
            "id": self.id, "lang": self.lang, "duration": round(self.total, 2), "voice": self.vcfg,
            "loudness_lufs_peak": self.loudness,
            "items": [{"t0": round(it["_t0"], 2), "dur": round(it["_dur"], 2), "line_starts": [round(x, 2) for x in it["_ls"]],
                       "lines": it["lines"], "heard": it["_heard"], "matched": it["_matched"]} for it in self.items],
            "segments": [{"clip": s["cid"], "t0": round(s["t0"], 2), "t1": round(s["t1"], 2), "box": s["box"]} for s in self.segs],
            "chunks": [{"t0": round(c["t0"], 2), "t1": round(c["t1"], 2), "text": " ".join(w for w, _ in c["words"])} for c in self.chunks],
            "sfx": [{"t": round(c["t"], 2), "id": c["id"]} for c in self.cues],
            "footage": self.report, "placeholders": sum(r["kind"] == "placeholder" for r in self.report),
            "warnings": self.warnings, "render_seconds": round(time.time() - t_start, 1),
        }
        with open(os.path.join(self.work, "timeline.json"), "w", encoding="utf-8") as f:
            json.dump(tl, f, indent=1, ensure_ascii=False)
        self.write_upload_notes(os.path.join(out_dir, name + "_upload.txt"))
        return out, tl

    def write_upload_notes(self, path):
        sc = self.sc
        up = sc.get("upload", {})
        ko = self.lang == "ko"
        lines = []
        if self.brand:
            lines += [f"CHANNEL: {self.brand.get('name', '')} {self.brand.get('handle', '')}".rstrip(), ""]
        lines += [f"TITLE: {up.get('title', gfx.plain(sc['title']))}", "", "DESCRIPTION:", up.get("description", "")]
        if sc.get("sources"):
            lines += ["", "출처:" if ko else "Sources:"] + [f"- {s['name']}: {s.get('url', '')}".rstrip(": ") for s in sc["sources"]]
        seen, credits = set(), []
        for r in self.report:
            if r["kind"] == "video" and r["src"] not in seen:
                seen.add(r["src"])
                m = source_meta(r["src"])
                if any((m.get("uploader") or "~").lower().lstrip("@") in c.lower() for c in sc.get("footage_credits", [])):
                    continue  # the script already credits this account by hand
                credits.append(f"- {m.get('title') or 'video'}" + (f" ({m['uploader']})" if m.get("uploader") else "") + f": {m['url']}")
        credits += [f"- {c}" for c in sc.get("footage_credits", [])
                    if not any(c.split(":")[-1].strip() and c.split(":")[-1].strip() in x for x in credits)]
        if credits:
            lines += ["", "영상 출처:" if ko else "Footage:"] + credits
        if up.get("hashtags"):
            lines += ["", " ".join(up["hashtags"])]
        if up.get("tags"):  # YouTube Studio "Tags" box, comma separated (500 character limit)
            lines += ["", "", "TAGS:", ", ".join(up["tags"])]
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines).strip() + "\n")
        # copy-paste file for YouTube Studio: title / description / tags / pinned comment, split by "___" lines
        desc = "\n".join(lines[lines.index("DESCRIPTION:") + 1:])
        desc = desc.split("\n\n\nTAGS:")[0].strip()
        parts = [up.get("title", gfx.plain(sc["title"])), desc, ", ".join(up.get("tags", [])), up.get("comment", "")]
        with open(path.replace("_upload.txt", "_text.txt"), "w", encoding="utf-8") as f:
            f.write("\n\n___\n\n".join(p.strip() for p in parts) + "\n")
