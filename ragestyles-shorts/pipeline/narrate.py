"""Narration-driven edit builder: a "beats" script -> voice clips (Kokoro TTS) + a timed render plan.

Each beat is one line of narration with the shot(s) shown while it is spoken. The line's voice length
sets the beat length, so the cut follows the narrator (fast, no dead air). Captions are split into short
phrases timed to the voice.

Usage: python3 narrate.py scripts/01_robot_arm_day.json   -> plans/01_robot_arm_day.json
Needs work/tts/kokoro-v1.0.onnx and voices-v1.0.bin (kokoro-onnx release "model-files-v1.0", Apache 2.0).
Beat fields:
  say        narration text (omit for a silent beat, then give "dur")
  caption    on-screen text (defaults to `say`); *yellow* ~red~ ^green^ :emoji: :flag-us:
  big        true -> one big slam caption for the whole beat instead of phrase chunks
  shots      [{clip, in, speed, zoom, focus, bw, hold, w}]  hold = freeze seconds at the end
  pad / min / dur, sfx [{at, name, db}], stickers [{at, d, ...}]
Top-level "leaderboard.rows" and "flag_row.events" may anchor to {"beat": i, "at": x}.
"""
import hashlib
import json
import os
import re
import subprocess
import sys

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TTS_DIR = os.path.join(ROOT, "work", "tts")
VOICE_DIR = os.path.join(ROOT, "work", "voice")
SR = 48000
_K = None

# broadcast-style voice chain: rumble cut, a little chest, gentle compression, peak safety
VOICE_FILTER = ("highpass=f=65,equalizer=f=140:t=q:w=1.0:g=2.5,equalizer=f=3200:t=q:w=1.2:g=1.5,"
                "acompressor=threshold=-20dB:ratio=3:attack=6:release=90:makeup=2,alimiter=limit=0.89")


def kokoro():
    global _K
    if _K is None:
        from kokoro_onnx import Kokoro
        _K = Kokoro(os.path.join(TTS_DIR, "kokoro-v1.0.onnx"), os.path.join(TTS_DIR, "voices-v1.0.bin"))
    return _K


def voice_style(spec):
    """"am_onyx" or {"am_onyx": 0.6, "am_michael": 0.4} (style blend)."""
    if isinstance(spec, str):
        return spec
    k = kokoro()
    return sum(k.get_voice_style(name) * w for name, w in spec.items())


def tts(text, voice, speed, lang):
    """Synthesize one line; cached by content. Returns (48 kHz wav path, seconds)."""
    os.makedirs(VOICE_DIR, exist_ok=True)
    key = hashlib.md5(json.dumps([text, voice, speed, lang, VOICE_FILTER], sort_keys=True).encode()).hexdigest()[:16]
    out = os.path.join(VOICE_DIR, key + ".wav")
    if not os.path.exists(out):
        samples, sr = kokoro().create(text, voice=voice_style(voice), speed=speed, lang=lang)
        raw = out + ".raw.wav"
        sf.write(raw, samples, sr)
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", raw, "-af", VOICE_FILTER,
                        "-ar", str(SR), "-ac", "1", out], check=True)
        os.remove(raw)
    info = sf.info(out)
    return out, info.frames / info.samplerate


def chunk_caption(text, max_words=3, max_chars=18):
    """Split caption text into short phrases, keeping emoji with their phrase and colour spans balanced.
    A "|" forces a phrase break."""
    chunks = []
    for part in text.split("|"):
        cur, n_words = [], 0
        for w in part.split():
            is_emoji = w.startswith(":") and w.endswith(":") and len(w) > 2
            if is_emoji:
                (cur if cur else (chunks[-1] if chunks else cur)).append(w)
                continue
            plain = re.sub(r"[*~^]", "", w)
            cur_len = len(" ".join(re.sub(r"[*~^]", "", x) for x in cur))
            if cur and (n_words >= max_words or cur_len + 1 + len(plain) > max_chars):
                chunks.append(cur)
                cur, n_words = [], 0
            cur.append(w)
            n_words += 1
        if cur:
            chunks.append(cur)
    # re-balance colour markers across chunk boundaries
    out, active = [], None
    for ch in chunks:
        ch = list(ch)
        if active:
            ch[0] = active + ch[0]
        for w in ch:
            core = w.rstrip(".,!?'\")")
            if core[:1] in "*~^" and active is None and not (len(core) > 1 and core.endswith(core[0])):
                active = core[0]
            elif active and core.endswith(active):
                active = None
        if active:
            ch[-1] = ch[-1] + active
        out.append(" ".join(ch))
    return out


def at_time(at, dur, starts=()):
    """Offset inside a beat: a number, "end" / "end-1.5" (before the beat ends), or "s1" / "s1+0.1"
    (when sentence 1 of the narration line starts, 0-based)."""
    if isinstance(at, str):
        m = re.fullmatch(r"(end|s(\d+))([+-][\d.]+)?", at)
        base = dur if m.group(1) == "end" else starts[int(m.group(2))]
        return base + float(m.group(3) or 0)
    return at


def spoken_len(s):
    return max(1, len(re.sub(r":[a-z0-9-]+:|[^A-Za-z0-9]", "", s)))


def sentences(say):
    return [x for x in re.split(r"(?<=[.?!])\s+", say.strip()) if x]


def trim(x, thr_db=-45.0, pre=0.02, post=0.06):
    """Cut the silence the TTS leaves before and after a sentence (short fades, no clicks)."""
    hop = int(0.005 * SR)
    m = len(x) // hop
    rms = np.sqrt((x[:m * hop].reshape(m, hop) ** 2).mean(axis=1) + 1e-12)
    on = np.where(20 * np.log10(rms) > thr_db)[0]
    if len(on) == 0:
        return x
    x = x[max(0, on[0] * hop - int(pre * SR)): min(len(x), (on[-1] + 1) * hop + int(post * SR))].copy()
    f_in, f_out = min(len(x), int(0.005 * SR)), min(len(x), int(0.012 * SR))
    x[:f_in] *= np.linspace(0, 1, f_in)
    x[len(x) - f_out:] *= np.linspace(1, 0, f_out)
    return x


def tts_line(say, voice, speed, lang, gap=0.14):
    """One narration line, sentence by sentence (the TTS pauses unreliably between sentences), joined
    with a fixed gap. Returns (wav path, seconds, [(start, end)] of each sentence)."""
    parts = [trim(sf.read(tts(x, voice, speed, lang)[0], dtype="float32")[0]) for x in sentences(say)]
    spans, pos = [], 0.0
    for i, x in enumerate(parts):
        spans.append((pos, pos + len(x) / SR))
        pos += len(x) / SR + (gap if i + 1 < len(parts) else 0)
    key = hashlib.md5(json.dumps([say, voice, speed, lang, VOICE_FILTER, gap, "line2"], sort_keys=True).encode())
    out = os.path.join(VOICE_DIR, key.hexdigest()[:16] + "_line.wav")
    if not os.path.exists(out):
        silence = np.zeros(int(gap * SR), np.float32)
        joined = [y for i, x in enumerate(parts) for y in ((x, silence) if i + 1 < len(parts) else (x,))]
        sf.write(out, np.concatenate(joined), SR, subtype="PCM_24")
    return out, pos, spans


def build(script_path):
    sc = json.load(open(script_path))
    v = sc.get("voice", {})
    voice, speed, lang = v.get("name", "am_onyx"), v.get("speed", 1.1), v.get("lang", "en-us")
    plan = {k: val for k, val in sc.items() if k not in ("beats", "voice")}
    plan.setdefault("layout", "band")
    segs, caps, sfx, stickers, voice_track, beat_info = [], [], [], [], [], []
    t = 0.0
    for bi, b in enumerate(sc["beats"]):
        say = b.get("say")
        lead = b.get("lead", 0.05)
        spans = []
        if say:
            path, vdur, spans = tts_line(say, voice, speed, lang, b.get("gap", sc.get("sentence_gap", 0.14)))
            dur = max(lead + vdur + b.get("pad", sc.get("pad", 0.1)), b.get("min", 0.0))
            voice_track.append({"t": round(t + lead, 3), "file": os.path.relpath(path, ROOT)})
            spans = [(lead + a, lead + c) for a, c in spans]  # relative to the beat start
        else:
            vdur = 0.0
            dur = b["dur"]
        starts = [a for a, _ in spans]
        beat_info.append((t, dur, starts))
        # shots: split the beat between its shots (weights), freeze "hold" inside the shot's share
        shots = b["shots"]
        ws = [s.get("w", 1.0) for s in shots]
        for s, w in zip(shots, ws):
            share = dur * w / sum(ws)
            hold = s.get("hold", 0.0)
            play = max(0.2, share - hold)
            spd = s.get("speed", 1.0)
            seg = {k: val for k, val in s.items() if k not in ("w", "hold")}
            seg["out"] = round(s["in"] + play * spd, 3)
            if hold:
                seg["freeze"] = {"dur": hold, "desat": s.get("desat", False), "bw": s.get("bw_hold", s.get("bw", False)),
                                 "zoom": s.get("hold_zoom", 0.06), "vignette": s.get("vignette", False)}
            segs.append(seg)
        # captions: "|" groups line up with the narration's sentences when the counts match
        text = b.get("caption", say)
        if text:
            groups = [g.strip() for g in text.split("|")]
            if not spans:
                windows = [(0.0, dur)]
                groups = [" ".join(groups)]
            elif len(groups) == len(spans):
                windows = spans
            else:
                windows = [(spans[0][0], spans[-1][1])]
                groups = [" | ".join(groups)]
            cues = []  # (start, text) relative to the beat
            for g, (w0, w1) in zip(groups, windows):
                if b.get("big"):
                    cues.append((w0, " ".join(g.replace("|", " ").split())))
                    continue
                parts = chunk_caption(g, b.get("max_words", 3), b.get("max_chars", 18))
                total = sum(spoken_len(x) for x in parts)
                c0 = w0
                for x in parts:
                    cues.append((c0, x))
                    c0 += (w1 - w0) * spoken_len(x) / total
            # first caption lands on the cut, the rest a hair before their words; each holds until the next
            st = [b.get("cap_at", 0.0)] + [max(0.0, c - 0.03) for c, _ in cues[1:]]
            for i, (_, x) in enumerate(cues):
                c0, c1 = st[i], (st[i + 1] if i + 1 < len(st) else dur)
                cap = {"t": round(t + c0, 3), "d": round(c1 - c0, 3), "text": x}
                if b.get("big"):
                    cap.update({"anim": b.get("anim", sc.get("big_anim", "punch")), "size": b.get("size", 108),
                                "max_lines": 1, "max_w": 1000})
                else:
                    cap.update({"anim": "snap", "size": b.get("size", 96), "max_lines": 2})
                caps.append(cap)
        for x in b.get("sfx", []):
            at = at_time(x.get("at", 0.0), dur, starts)
            sfx.append({"t": round(t + at, 3), "name": x["name"], "db": x.get("db", -8),
                        **({"duck": x["duck"]} if "duck" in x else {})})
        for st in b.get("stickers", []):
            st = dict(st)
            st["t"] = round(t + at_time(st.pop("at", 0.0), dur, starts), 3)
            st.setdefault("d", round(dur - (st["t"] - t), 3))
            stickers.append(st)
        t += dur

    def anchor(o):
        if "beat" in o:
            bt, bd, bs = beat_info[o.pop("beat")]
            o["t"] = round(bt + at_time(o.pop("at", 0.0), bd, bs), 3)
        return o
    if "leaderboard" in plan:
        plan["leaderboard"]["rows"] = [anchor(dict(r)) for r in plan["leaderboard"]["rows"]]
    if "flag_row" in plan:
        plan["flag_row"]["events"] = [anchor(dict(e)) for e in plan["flag_row"]["events"]]
    plan.update({"segments": segs, "captions": caps, "sfx": sfx, "stickers": stickers, "voice": voice_track,
                 "voice_name": voice, "lufs": sc.get("lufs", -14.0)})
    out = os.path.join(ROOT, "plans", os.path.basename(script_path))
    json.dump(plan, open(out, "w"), indent=1, ensure_ascii=False)
    print(f"{os.path.basename(out)}: {len(sc['beats'])} beats, {t:.2f}s, {len(caps)} captions, {len(sfx)} sfx")
    return out


if __name__ == "__main__":
    for p in sys.argv[1:]:
        build(p)
