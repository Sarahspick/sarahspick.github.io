"""Speech guard for the footage's original sound.

The narration is the only voice a Short may have: a clip's own sound is kept under it only when it carries no
speech (engines, crowds, water, applause). Chinese speech in particular must never be heard. SenseVoice
(offline, assets/models/sensevoice) transcribes the exact window a clip uses and reports its language, and
render.original_audio mutes any window that contains words unless the clip sets "orig_speech": true.
"""
import hashlib
import json
import os
import re
import subprocess

import numpy as np

from .config import WORK, asset

_rec = None
_CACHE = os.path.join(WORK, "speech_cache.json")


def _recognizer():
    global _rec
    if _rec is None:
        import sherpa_onnx
        sv = asset("models", "sensevoice")
        _rec = sherpa_onnx.OfflineRecognizer.from_sense_voice(
            model=os.path.join(sv, "model.int8.onnx"), tokens=os.path.join(sv, "tokens.txt"),
            language="auto", use_itn=False, num_threads=4)
    return _rec


def detect(path, start, dur):
    """Return {"speech": bool, "lang": "zh"|"en"|..., "text": str} for source seconds [start, start + dur]."""
    key = hashlib.sha1(f"{os.path.abspath(path)}|{start:.2f}|{dur:.2f}".encode()).hexdigest()[:16]
    cache = {}
    if os.path.exists(_CACHE):
        with open(_CACHE, encoding="utf-8") as f:
            cache = json.load(f)
    if key in cache:
        return cache[key]
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{max(0.0, start):.3f}", "-t", f"{dur:.3f}", "-i", path,
                        "-vn", "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True)
    a = np.frombuffer(r.stdout, np.float32)
    out = {"speech": False, "lang": "", "text": ""}
    if len(a) > 1600 and float(np.sqrt(np.mean(a ** 2))) > 1e-3:
        rec = _recognizer()
        st = rec.create_stream()
        st.accept_waveform(16000, a)
        rec.decode_stream(st)
        res = st.result
        text = re.sub(r"<\|[^|]*\|>", "", res.text).strip()
        words = re.sub(r"[\W_]+", "", text)
        lang = (getattr(res, "lang", "") or "").strip("<|>")
        out = {"speech": len(words) >= 2, "lang": lang, "text": text[:80]}
    cache[key] = out
    os.makedirs(WORK, exist_ok=True)
    with open(_CACHE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False)
    return out
