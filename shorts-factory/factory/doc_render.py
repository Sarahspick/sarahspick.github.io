"""Long-form 16:9 documentary renderer.

    python make_doc.py documentaries/walmart_machine.json

Pipeline
  1. narration per segment (ElevenLabs, cached) -> timeline: title, chapter cards, segments, end card
  2. shots: every clip "KEY@t" snaps to the source shot that contains t (cuts pre-detected in shots.json), never
     runs across a source cut (slides back inside the shot, or slows down to at most 0.55x), conformed to
     1920x1080/30 (16:9 sources fill the frame; 4:3 archive is pillarboxed with a slow pan)
  3. graphics: map and diagram/cards/stats/citations rendered with PIL (doc_gfx, doc_map) as video layers
  4. audio: narration, chapter score (ducked under the voice), ElevenLabs SFX -> -14 LUFS, oversampled limiter
Original footage sound is never used.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

import numpy as np

from . import doc_audio, doc_gfx, doc_map
from .config import WORK, OUTPUT, asset
from .media import fetch

W, H, FPS, SR = 1920, 1080, 30, 48000
LEAD, GAP = 0.25, 0.55          # silence before / after each narration paragraph
CARD = 3.4                      # chapter card length (no narration)
EDGE = 0.10                     # stay this far from a source cut
RENDER_V = 2                    # bump when render_shot's look changes (invalidates the shot cache)


def run(cmd, **kw):
    kw.setdefault("text", True)
    r = subprocess.run(cmd, capture_output=True, **kw)
    if r.returncode:
        raise RuntimeError(" ".join(map(str, cmd[:6])) + "...\n" + r.stderr[-2000:])
    return r


# ------------------------------------------------------------------------------------------ timeline

def build_timeline(doc, work):
    voice_dir = os.path.join(work, "voice")
    texts = [s for s in doc["segments"] if s.get("text")]
    items, t, prev_ch, k = [], 0.0, None, 0
    for s in doc["segments"]:
        if s.get("title"):
            items.append({"kind": "title", "start": t, "dur": s["dur"], "clips": s["clips"], "seg": s})
            t += s["dur"]
            continue
        if s["ch"] != prev_ch and s["ch"] > 0:
            ch = doc["chapters"][s["ch"]]
            items.append({"kind": "chapter", "start": t, "dur": CARD, "ch": ch, "seg": s,
                          "clips": s.get("clips", [])[:1]})
            t += CARD
        prev_ch = s["ch"]
        i = texts.index(s)
        prev = texts[i - 1]["text"] if i > 0 else ""
        nxt = texts[i + 1]["text"] if i + 1 < len(texts) else ""
        mp3, words = doc_audio.narrate(s["text"], doc["voice"], voice_dir, prev, nxt)
        vd = doc_audio.duration(mp3)
        lead, gap = s.get("lead", LEAD), s.get("gap", GAP)
        dur = lead + vd + gap + (5.0 if s.get("end") else 0.0)
        items.append({"kind": "seg", "start": t, "dur": dur, "voice": mp3, "voice_at": t + lead, "vdur": vd,
                      "words": words, "seg": s, "clips": s.get("clips", []), "idx": k})
        k += 1
        t += dur
    # a chapter card continues straight into its segment's first shot (a hand-picked window is used up by the
    # card itself, so the segment starts on its next clip)
    for a, b in zip(items, items[1:]):
        if a["kind"] == "chapter" and b["clips"]:
            if "+" in str(b["clips"][0]) and len(b["clips"]) > 1:
                b["clips"] = b["clips"][1:]
            else:
                b["first_offset"] = a["dur"]
    return items, t


# ------------------------------------------------------------------------------------------ shots

def parse_clip(c, doc):
    opts = {}
    if isinstance(c, dict):
        opts = dict(c)
        c = opts.pop("c")
    m = re.fullmatch(r"([A-Z0-9]+)@([0-9.]+)(?:\+([0-9.]+))?", c)
    key, t = m.group(1), float(m.group(2))
    base = dict(doc.get("source_opts", {}).get(key, {}))
    base.update(opts)
    if m.group(3):                      # KEY@start+len: a hand-picked clean window (e.g. archive with dissolves)
        base["max"] = max(0.6, float(m.group(3)) - 0.35)   # keep clear of the next dissolve
    return key, t, base


def shot_bounds(shots, src_file, t):
    info = shots[os.path.basename(src_file)[:-4]]
    cuts = [0.0] + [c for c in info["cuts"]] + [info["dur"]]
    for a, b in zip(cuts, cuts[1:]):
        if a <= t < b:
            return a, b
    return cuts[-2], cuts[-1]


def resolve(shots, src_file, t, need, search=4.0, text=None):
    """(start, speed, note): a window near t whose first 0.7 s and last 0.45 s contain no source cut (no flash of
    another shot at our edit points). Cuts in the middle are the source's own editing and are allowed but cost a
    little; so do moving away from t and slowing down."""
    info = shots[os.path.basename(src_file)[:-4]]
    cuts = np.array(info["cuts"] + [info["dur"]])
    txt = np.array([x[0] for x in (text or {}).get(os.path.basename(src_file)[:-4], []) if x[1] >= 0.045] or [-99.0])
    best = None
    for speed in (1.0, 0.85, 0.7):
        span = need * speed
        for s in np.arange(max(0.0, t - search), t + search + 1e-6, 0.1):
            e = s + span
            if e > info["dur"] - 0.1:
                continue
            inner = cuts[(cuts > s) & (cuts < e)]
            if ((inner < s + 0.7 * speed) | (inner > e - 0.45 * speed)).any():
                continue
            if (np.abs(cuts - s) < EDGE).any():
                continue
            if ((txt > s - 0.8) & (txt < e + 0.8)).any():     # burned-in caption / title card in the window
                continue
            cost = abs(s - t) * 0.35 + len(inner) * 0.8 + (1 - speed) * 3
            if best is None or cost < best[0]:
                best = (cost, s, speed, len(inner))
    if best is None:
        if search < 12:
            return resolve(shots, src_file, t, need, search * 2, text)
        return t, 1.0, "NO CLEAN WINDOW"
    _, s, speed, ninner = best
    note = []
    if abs(s - t) > 1.5:
        note.append(f"moved {s - t:+.1f}s")
    if speed < 1:
        note.append(f"slow {speed}")
    if ninner:
        note.append(f"{ninner} inner cut")
    return float(s), speed, ", ".join(note)


def plan_shots(items, doc, shots, text=None):
    srcs = doc["footage"]
    plan = []
    for it in items:
        if it.get("map") or not it["clips"]:
            continue
        clips = it["clips"]
        n = len(clips)
        po = [parse_clip(c, doc)[2] for c in clips]
        if any(o.get("max") for o in po):    # hand-picked windows share the time by their length
            weights = [o.get("w", o.get("max", 4.0)) for o in po]
        else:
            weights = [o.get("w", 1.0) for o in po]
        tot = sum(weights)
        t = it["start"]
        for j, c in enumerate(clips):
            key, ts, opts = parse_clip(c, doc)
            need = it["dur"] * weights[j] / tot
            if j == 0 and it.get("first_offset"):
                ts += it["first_offset"]
            src = fetch(srcs[key])
            if opts.get("max"):
                speed = min(1.0, opts["max"] / need)
                start, note = ts, ("" if speed >= 0.55 else f"SHORT window {opts['max']}s for {need:.1f}s")
                speed = max(speed, 0.55)
            else:
                start, speed, note = resolve(shots, src, ts, need, text=text)
            nf = round((t + need) * FPS) - round(t * FPS)
            plan.append({"t": t, "dur": need, "nf": nf, "key": key, "src": src, "start": start, "speed": speed,
                         "opts": opts, "note": note, "want": ts})
            t += need
    return punch_ins(plan)


PUNCH = 3.6          # a 16:9 shot longer than this is recut once with a punch-in (same moment, tighter frame)


def punch_ins(plan):
    out = []
    for k, sh in enumerate(plan):
        w, h = _wh(sh["src"])
        if sh["dur"] <= PUNCH or sh["opts"].get("max") or w / h < 1.5 or sh["opts"].get("no_punch"):
            out.append(sh)
            continue
        d1 = round(sh["dur"] * 0.52 * FPS) / FPS
        a = dict(sh, dur=d1, nf=round((sh["t"] + d1) * FPS) - round(sh["t"] * FPS))
        fx, fy = ((0.3, 0.4), (0.7, 0.45), (0.5, 0.35))[k % 3]
        b = dict(sh, t=sh["t"] + d1, dur=sh["dur"] - d1, start=sh["start"] + d1 * sh["speed"],
                 opts=dict(sh["opts"], zoom=1.22, focus=[fx, fy]), note="")
        b["nf"] = round((b["t"] + b["dur"]) * FPS) - round(b["t"] * FPS)
        out += [a, b]
    return out


_WH = {}


def _wh(path):
    if path not in _WH:
        _WH[path] = probe_wh(path)
    return _WH[path]


def probe_wh(path):
    out = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
               "-of", "csv=p=0", path]).stdout.strip().split(",")
    return int(out[0]), int(out[1])


def render_shot(sh, out, idx):
    w, h = probe_wh(sh["src"])
    o = sh["opts"]
    vf = []
    if o.get("crop"):
        x0, y0, x1, y1 = o["crop"]
        vf.append(f"crop={int(w * (x1 - x0)) // 2 * 2}:{int(h * (y1 - y0)) // 2 * 2}:{int(w * x0)}:{int(h * y0)}")
        w, h = int(w * (x1 - x0)) // 2 * 2, int(h * (y1 - y0)) // 2 * 2
    for bx in o.get("blur", []):
        x0, y0, x1, y1 = bx
        bw, bh = max(8, int(w * (x1 - x0)) // 2 * 2), max(8, int(h * (y1 - y0)) // 2 * 2)
        vf.append(f"split[m{idx}][b{idx}];[b{idx}]crop={bw}:{bh}:{int(w * x0)}:{int(h * y0)},boxblur=12:3[bb{idx}];"
                  f"[m{idx}][bb{idx}]overlay={int(w * x0)}:{int(h * y0)}")
    if sh["speed"] != 1.0:
        vf.append(f"setpts=PTS/{sh['speed']:.4f}")
    vf.append(f"fps={FPS}")
    aspect = w / h
    T = sh["dur"]
    pan = o.get("pan", aspect < 1.5)        # archive: gentle drift so stills breathe
    if aspect < 1.5:                        # 4:3 archive -> pillarbox
        if pan:
            vf.append(f"scale=-2:{int(H * 1.07)}:flags=lanczos")
            vf.append(f"crop=iw/1.07:{H}:x='(iw-ow)*(0.15+0.7*t/{T:.3f})':y='(ih-oh)/2'")
        else:
            vf.append(f"scale=-2:{H}:flags=lanczos")
        vf.append(f"pad={W}:{H}:(ow-iw)/2:0:black")
    else:
        z = o.get("zoom", 1.0)
        vf.append(f"scale={int(W * z)}:{int(H * z)}:force_original_aspect_ratio=increase:flags=lanczos")
        fx, fy = o.get("focus", [0.5, 0.5])
        vf.append(f"crop={W}:{H}:(iw-ow)*{fx}:(ih-oh)*{fy}")
    if o.get("grain", aspect < 1.5):
        vf.append("noise=alls=5:allf=t")
    vf.append("eq=contrast=1.05:saturation=1.08,vignette=angle=PI/5")   # light cinematic grade
    vf.append("setsar=1,format=yuv420p")
    src_len = T * sh["speed"] + 0.2
    run(["ffmpeg", "-y", "-v", "error", "-ss", f"{sh['start']:.3f}", "-t", f"{src_len:.3f}", "-i", sh["src"], "-an",
         "-filter_complex", ",".join(vf), "-frames:v", str(sh["nf"]), "-c:v", "libx264", "-preset", "veryfast",
         "-crf", "16", "-r", str(FPS), out])


# ------------------------------------------------------------------------------------------ graphics layers

def write_frames(frame_fn, dur, out, alpha, n=None):
    """Pipe PIL frames into an encoder. alpha=True -> RGBA mov (png) for overlays; else opaque h264."""
    n = n or round(dur * FPS)
    if alpha:
        cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS),
               "-i", "-", "-c:v", "png", "-pix_fmt", "rgba", out]
    else:
        cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
               "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    for i in range(n):
        im = frame_fn(i / FPS)
        p.stdin.write(im.convert("RGBA" if alpha else "RGB").tobytes())
    p.stdin.close()
    if p.wait():
        raise RuntimeError(p.stderr.read().decode()[-1000:])


def word_time(words, pat):
    for w, s, e in words:
        if re.match(pat, w, re.I):
            return s
    return None


def cue(it, at, default=0.3):
    """Timeline time of a cue inside a segment: a word (regex on the narration) or a fraction of the voice."""
    if isinstance(at, str):
        w = word_time(it["words"], at)
        if w is not None:
            return it["voice_at"] + w
        at = default
    return it["voice_at"] + it["vdur"] * (at if at is not None else default)


SLAM = 2.9          # how long a number stays up


def graphic_events(items, doc):
    """[(start, dur, frame_fn, [(sfx, offset, gain_db)])] for every graphic drawn over footage."""
    out = []
    for it in items:
        s = it["seg"]
        if it["kind"] == "title":
            out.append((it["start"], it["dur"], doc_gfx.title_card(doc["title"], doc.get("subtitle", ""), it["dur"]),
                        [("title_hit", 0.02, -4), ("impact", 0.0, -8)]))
            out.append((it["start"], 0.3, doc_gfx.flash(0.3), []))
        elif it["kind"] == "chapter":
            ch = it["ch"]
            out.append((it["start"], it["dur"], doc_gfx.chapter(ch["n"], ch["title"], it["dur"]),
                        [("flash", -0.25, -9), ("impact", 0.02, -11)]))
            out.append((it["start"], 0.25, doc_gfx.flash(0.25, 0.7), []))
        elif it["kind"] == "seg":
            if s.get("end"):
                q = doc["end_quote"]
                st = cue(it, q.get("cue", "to")) - 0.3
                d = it["start"] + it["dur"] - st
                out.append((st, d, doc_gfx.quote_card(q["text"], q["who"], d, q.get("note", "")), []))
                continue
            if s.get("flash"):
                out.append((it["start"], 0.25, doc_gfx.flash(0.25, 0.75), [("flash", -0.2, -10)]))
            if s.get("diagram") == "crossdock":
                tt = word_time(it["words"], r"traditional") or 0.0
                tc = word_time(it["words"], r"cross-dock") or it["vdur"] * 0.5
                out.append((it["voice_at"] - 0.2, it["vdur"] + 0.6, doc_gfx.crossdock(it["vdur"] + 0.6, tt + 0.2, tc + 0.2),
                            [("whoosh", -0.3, -14)]))
            if s.get("cite") and not s.get("map"):
                out.append((it["start"], it["dur"] - 0.1, doc_gfx.source(s["cite"], it["dur"] - 0.1), []))
            if s.get("stats") and not s.get("map"):
                st = cue(it, s.get("stats_at", 0.3)) - 0.08
                d = min(SLAM + 0.4 * (len(s["stats"]) - 1), it["start"] + it["dur"] - st)
                fx = [("impact", 0.0, -9), ("counter", 0.02, -17)]
                if len(s["stats"]) > 1:
                    fx.append(("impact", 0.38, -11))
                out.append((st, d, doc_gfx.slam(s["stats"], d, vs=s.get("vs", False)), fx))
            c = s.get("card")
            if c:
                st = cue(it, c.get("at", 0.0)) - 0.15
                d = min(c.get("dur", 3.5), it["start"] + it["dur"] - st)
                if c["type"] == "doc":
                    fn = doc_gfx.doc_card(c["kind"], c["title"], c["meta"], c.get("body", ""), c.get("highlight", ""), d, 1.0)
                    fx = [("paper", 0.0, -9)]
                else:
                    fn = doc_gfx.headline(c["text"], c["kicker"], d)
                    fx = [("news", 0.0, -9)]
                out.append((st, d, fn, fx))
    return out


def overlays(items, doc):
    return [(st, d, fn) for st, d, fn, _ in graphic_events(items, doc)]


def map_items(items):
    """Group consecutive map segments into one continuous animation."""
    groups = []
    for it in items:
        m = it["seg"].get("map") if it["kind"] == "seg" else None
        if m:
            it["map"] = True
            if groups and groups[-1]["mode"] == m["mode"] and abs(groups[-1]["end"] - it["start"]) < 1e-6:
                groups[-1]["end"] = it["start"] + it["dur"]
            else:
                groups.append({"mode": m["mode"], "start": it["start"], "end": it["start"] + it["dur"]})
    return groups


# ------------------------------------------------------------------------------------------ audio

def decode(path, sr=SR):
    raw = run(["ffmpeg", "-v", "error", "-i", path, "-ac", "2", "-ar", str(sr), "-f", "f32le", "-"],
              text=False).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).copy()


def lufs(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "loudnorm=print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    return float(json.loads(r.stderr[r.stderr.rindex("{"):])["input_i"])


def place(buf, clip, t, gain=1.0):
    i = int(round(t * SR))
    if i >= len(buf):
        return
    n = min(len(clip), len(buf) - i)
    buf[i:i + n] += clip[:n] * gain


def env_fade(x, fin, fout):
    n = len(x)
    g = np.ones(n, dtype=np.float32)
    a, b = int(fin * SR), int(fout * SR)
    if a:
        g[:a] = np.linspace(0, 1, a)
    if b:
        g[-b:] *= np.linspace(1, 0, b)
    return x * g[:, None]


def db(v):
    return 10 ** (v / 20)


def mix_audio(items, doc, total, work, sfx_index):
    n = int(total * SR) + SR
    voice = np.zeros((n, 2), np.float32)
    for it in items:
        if it["kind"] == "seg":
            place(voice, decode(it["voice"]), it["voice_at"])
    # narration to about -16 LUFS
    vpath = os.path.join(work, "voice_track.wav")
    write_wav(vpath, voice)
    voice *= db(-16.0 - lufs(vpath))

    # score: one cue per chapter, starting at its card (cold open at 0), crossfaded
    music = np.zeros_like(voice)
    starts = {}
    for it in items:
        ch = it["seg"].get("ch", 0) if it["kind"] != "title" else 0
        if it["kind"] == "chapter":
            starts[it["ch"]["n"]] = it["start"]
    starts.setdefault(0, 0.0)
    order = sorted(starts.items(), key=lambda kv: kv[1])
    mdir = os.path.join(work, "music")
    for k, (chn, st) in enumerate(order):
        nxt = order[k + 1][1] if k + 1 < len(order) else total
        cue = decode(doc_audio.music(doc["chapters"][chn]["music"], doc["chapters"][chn]["_len"], mdir))
        cue = cue[: int((nxt - st + 2.5) * SR)]
        cue = env_fade(cue, 0.05 if k == 0 else 1.2, 2.5 if k + 1 < len(order) else 4.0)
        place(music, cue, max(0.0, st - (0.6 if k else 0.0)))
    mpath = os.path.join(work, "music_track.wav")
    write_wav(mpath, music)
    music *= db(-25.0 - lufs(mpath))
    # duck under narration: -8 dB with ~0.25 s attack / 0.9 s release
    act = np.abs(voice).max(1)
    hop = SR // 100
    frames = act[: len(act) // hop * hop].reshape(-1, hop).max(1) > db(-45)
    g = np.ones(len(frames), np.float32)
    duck = db(-8.0)
    cur = 1.0
    for i, on in enumerate(frames):
        tgt = duck if frames[max(0, i - 0):i + 25].any() else 1.0     # look ahead 0.25 s
        rate = 0.04 if tgt < cur else 0.011
        cur += (tgt - cur) * rate * 4
        g[i] = cur
    gain = np.repeat(g, hop)
    gain = np.concatenate([gain, np.full(len(music) - len(gain), gain[-1])])
    music *= gain[:, None]

    # sound effects
    fx = np.zeros_like(voice)
    for t, name, gdb in sfx_events(items, doc):
        clip = decode(sfx_index[name])
        place(fx, env_fade(clip, 0.02, min(0.6, len(clip) / SR / 3)), t, db(gdb))
    mix = voice + music + fx
    mix[-int(1.5 * SR):] *= np.linspace(1, 0, int(1.5 * SR))[:, None]
    raw = os.path.join(work, "mix_raw.wav")
    write_wav(raw, mix)
    final = os.path.join(work, "mix.wav")
    lu = lufs(raw)
    run(["ffmpeg", "-y", "-v", "error", "-i", raw, "-af",
         f"volume={-14.0 - lu:.2f}dB,aresample=192000,alimiter=limit=0.84:attack=2:release=40:level=false,aresample={SR}",
         "-c:a", "pcm_s16le", final])
    return final


def sfx_events(items, doc):
    ev = []
    for st, _, _, fx in graphic_events(items, doc):
        for name, off, gdb in fx:
            ev.append((st + off, name, gdb))
    for it in items:
        if it["kind"] == "seg":
            for name, off, gdb in it["seg"].get("sfx", []):
                ev.append((it["start"] + off, name, gdb))
    return ev


def write_wav(path, x):
    pcm = np.clip(x, -4, 4).astype(np.float32)
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                          "-c:a", "pcm_f32le", path], stdin=subprocess.PIPE)
    p.stdin.write(pcm.tobytes())
    p.stdin.close()
    p.wait()


# ------------------------------------------------------------------------------------------ captions + chapters

def srt(items, path):
    def ts(x):
        h, r = divmod(x, 3600)
        m, s = divmod(r, 60)
        return f"{int(h):02d}:{int(m):02d}:{s:06.3f}".replace(".", ",")
    cues = []
    for it in items:
        if it["kind"] != "seg":
            continue
        chunk = []
        for w, s, e in it["words"]:
            chunk.append((w, s, e))
            text = " ".join(x[0] for x in chunk)
            if len(text) > 70 or w[-1] in ".?!" and len(text) > 25:
                cues.append((it["voice_at"] + chunk[0][1], it["voice_at"] + chunk[-1][2], text))
                chunk = []
        if chunk:
            cues.append((it["voice_at"] + chunk[0][1], it["voice_at"] + chunk[-1][2], " ".join(x[0] for x in chunk)))
    with open(path, "w") as f:
        for i, (a, b, t) in enumerate(cues, 1):
            f.write(f"{i}\n{ts(a)} --> {ts(max(b, a + 0.8))}\n{t}\n\n")


def ass_captions(items, path):
    """Burned-in English captions: one short line at a time, timed to the narration's words."""
    def ts(x):
        h, r = divmod(max(0.0, x), 3600)
        m, sec = divmod(r, 60)
        return f"{int(h)}:{int(m):02d}:{sec:05.2f}"
    cues = []
    for it in items:
        if it["kind"] != "seg" or it["seg"].get("end"):
            continue
        chunk = []
        for w, a, b in it["words"]:
            chunk.append((w, a, b))
            text = " ".join(x[0] for x in chunk)
            if len(text) > 34 or (w[-1] in ".?!" and len(text) > 8) or (w[-1] in ",;:" and len(text) > 22):
                cues.append([it["voice_at"] + chunk[0][1], it["voice_at"] + chunk[-1][2], text])
                chunk = []
        if chunk:
            cues.append([it["voice_at"] + chunk[0][1], it["voice_at"] + chunk[-1][2], " ".join(x[0] for x in chunk)])
    for a, b in zip(cues, cues[1:]):                 # hold each line until the next one (short gaps only)
        if b[0] - a[1] < 0.6:
            a[1] = b[0] - 0.02
        else:
            a[1] += 0.25
    head = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Pretendard SemiBold,50,&H00FFFFFF,&H00FFFFFF,&H00101010,&H78000000,0,0,0,0,100,100,0.5,0,1,3.2,1.5,2,200,200,74,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    with open(path, "w") as f:
        f.write(head)
        for a, b, t in cues:
            f.write(f"Dialogue: 0,{ts(a)},{ts(b)},Cap,,0,0,0,,{t}\n")


def chapter_marks(items):
    marks = [(0.0, "Cold open")]
    for it in items:
        if it["kind"] == "chapter":
            marks.append((it["start"], it["ch"]["title"]))
    return [f"{int(t // 60)}:{int(t % 60):02d} {name}" for t, name in marks]


# ------------------------------------------------------------------------------------------ main

def render(doc_path, only_plan=False):
    doc = json.load(open(doc_path))
    work = os.path.join(WORK, doc.get("work", doc["id"]))
    os.makedirs(work, exist_ok=True)
    shots = json.load(open(os.path.join(work, "shots.json")))
    sfx_index = json.load(open(os.path.join(work, "sfx", "index.json")))
    for c in doc["chapters"]:
        c.setdefault("_len", c.get("len", 60))

    items, total = build_timeline(doc, work)
    groups = map_items(items)
    tpath = os.path.join(work, "text.json")
    text = json.load(open(tpath)) if os.path.exists(tpath) else {}
    avoid = {os.path.basename(fetch(doc["footage"][k]))[:-4] for k in doc.get("text_avoid", [])}
    ign = re.compile(doc.get("text_ignore", "$^"))
    text = {k: [x for x in v if not all(ign.search(tok.strip()) for tok in x[2].split("|"))]
            for k, v in text.items() if k in avoid}   # other sources: on-screen text is real signage
    plan = plan_shots(items, doc, shots, text)
    with open(os.path.join(work, "plan.json"), "w") as f:
        json.dump({"total": total, "items": [{k: v for k, v in it.items() if k not in ("words", "seg")} for it in items],
                   "shots": [{k: v for k, v in s.items() if k != "src"} for s in plan], "maps": groups}, f, indent=1)
    for s in plan:
        if s["note"]:
            print(f"  {s['t']:7.2f}s {s['key']}@{s['want']:.1f}: {s['note']}")
    print(f"timeline {total:.1f}s, {len(plan)} shots, {len(groups)} map sequences")
    if only_plan:
        return items, plan

    # 1. footage shots + map sequences -> base video
    sdir = os.path.join(work, "shotcache")       # shots are cached by their parameters
    os.makedirs(sdir, exist_ok=True)
    segs = []
    for i, sh in enumerate(plan):
        key = hashlib.sha1(json.dumps([sh["src"], round(sh["start"], 3), sh["speed"], sh["nf"], sh["opts"], RENDER_V],
                                      sort_keys=True).encode()).hexdigest()[:16]
        out = os.path.join(sdir, f"{key}.mp4")
        if not os.path.exists(out):
            render_shot(sh, out + ".tmp.mp4", i)
            os.replace(out + ".tmp.mp4", out)
        segs.append((sh["t"], out))
    for j, g in enumerate(groups):
        n = round(g["end"] * FPS) - round(g["start"] * FPS)
        out = os.path.join(sdir, f"map_{g['mode']}_{n}_{RENDER_V}.mp4")
        if not os.path.exists(out):
            fn = doc_map.grow(g["end"] - g["start"]) if g["mode"] == "grow" else doc_map.full(g["end"] - g["start"])
            write_frames(fn, g["end"] - g["start"], out + ".tmp.mp4", alpha=False, n=n)
            os.replace(out + ".tmp.mp4", out)
        segs.append((g["start"], out))
    segs.sort()
    lst = os.path.join(work, "concat.txt")
    with open(lst, "w") as f:
        for _, p in segs:
            f.write(f"file '{p}'\n")
    base = os.path.join(work, "base.mp4")
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", base])

    # 2. graphics layers
    odir = os.path.join(work, "overlays")
    shutil.rmtree(odir, ignore_errors=True)
    os.makedirs(odir)
    layers = []
    for k, (st, dur, fn) in enumerate(overlays(items, doc)):
        out = os.path.join(odir, f"o{k:03d}.mov")
        write_frames(fn, dur, out, alpha=True)
        layers.append((st, out))

    # 3. audio
    mix = mix_audio(items, doc, total, work, sfx_index)

    # 4. composite
    os.makedirs(OUTPUT, exist_ok=True)
    final = os.path.join(OUTPUT, f"{doc['id']}.mp4")
    inputs = ["-i", base]
    fc, last = [], "0:v"
    for k, (st, p) in enumerate(layers):
        inputs += ["-i", p]
        fc.append(f"[{k + 1}:v]setpts=PTS-STARTPTS+{st:.3f}/TB[o{k}]")
        fc.append(f"[{last}][o{k}]overlay=eof_action=pass:repeatlast=0[v{k}]")
        last = f"v{k}"
    ass = os.path.join(work, "captions.ass")
    ass_captions(items, ass)
    fc.append(f"[{last}]ass={ass}:fontsdir={asset('fonts')},fade=t=out:st={total - 1.2:.3f}:d=1.2,format=yuv420p[vout]")
    inputs += ["-i", mix]
    run(["ffmpeg", "-y", "-v", "error"] + inputs + ["-filter_complex", ";".join(fc), "-map", "[vout]",
         "-map", f"{len(layers) + 1}:a", "-t", f"{total:.3f}", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
         "-profile:v", "high", "-r", str(FPS), "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", final])
    srt(items, os.path.join(OUTPUT, f"{doc['id']}.en.srt"))
    with open(os.path.join(OUTPUT, f"{doc['id']}_chapters.txt"), "w") as f:
        f.write("\n".join(chapter_marks(items)) + "\n")
    print("wrote", final)
    return final
