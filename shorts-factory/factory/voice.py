"""Narration engines and word timing.

speak(lines) returns the sentence audio plus a start time for every *display token* (the words exactly as they
appear in the captions, markup included), so captions can be chunked and highlighted word by word.

Engines
  edge        Microsoft neural voices via edge-tts (free, exact word boundaries; needs internet)
  elevenlabs  ElevenLabs API (key in ELEVENLABS_API_KEY); exact character timings from /with-timestamps
  kokoro      offline Kokoro-82M; word times come from SenseVoice speech recognition
"""
import asyncio
import base64
import difflib
import json
import os
import re
import subprocess
import time
import urllib.error
import urllib.request

import numpy as np

from .config import asset

try:
    from num2words import num2words
except ImportError:  # alignment still works, numbers just fall back to interpolation
    num2words = None


def plain(text):
    return text.replace("*", "")


def _norm_words(text):
    """Lower-case alphanumeric word list with digits spelled out (so '1,000' matches 'one thousand')."""
    out = []
    for w in re.findall(r"[A-Za-z0-9가-힣][A-Za-z0-9가-힣,.'%]*", text.replace("-", " ")):
        w = w.strip(".,'")
        if re.fullmatch(r"[0-9][0-9,]*(\.[0-9]+)?", w) and num2words:
            num = w.replace(",", "")
            try:
                spelled = num2words(float(num) if "." in num else int(num))
                out.extend(p for p in re.split(r"[\s-]+", spelled.replace(",", "")) if p and p != "and")
                continue
            except Exception:
                pass
        p = re.sub(r"[^a-z0-9가-힣]", "", w.lower())
        if p:
            out.append(p)
    return out


def _snap(got, exp):
    """Replace near-miss ASR words ('mercede') with the expected word near the same relative position."""
    out = []
    for i, w in enumerate(got):
        centre = int(i * len(exp) / max(1, len(got)))
        best, score = w, 0.0
        for j in range(max(0, centre - 5), min(len(exp), centre + 6)):
            r = difflib.SequenceMatcher(None, w, exp[j]).ratio()
            if r > score:
                best, score = exp[j], r
        out.append(best if score >= 0.78 else w)
    return out


def tokenize(lines, pronounce):
    """Split caption lines into display tokens; '*' toggles highlight and may span several words."""
    toks = []
    for li, line in enumerate(lines):
        hl = False
        for raw in line.split():
            starts = hl or raw.startswith("*")
            hl = hl ^ (raw.count("*") % 2 == 1)
            say = plain(raw)
            for k, v in pronounce.items():
                say = re.sub(rf"(?<![\w-]){re.escape(k)}(?![\w-])", v, say)
            toks.append({"text": plain(raw), "hl": starts or raw.endswith("*"), "line": li,
                         "say": say, "norm": _norm_words(say)})
    return toks


def decode_audio(data, sr=24000):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", "pipe:0", "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                       input=data, capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.float32).copy()


def trim_silence(a, sr, lead=0.02, tail=0.06, thr_db=-42):
    """Return (trimmed audio, seconds removed from the start)."""
    win = max(1, int(sr * 0.01))
    env = np.sqrt(np.convolve(a ** 2, np.ones(win) / win, mode="same"))
    thr = max(1e-4, env.max() * 10 ** (thr_db / 20))
    idx = np.where(env > thr)[0]
    if len(idx) == 0:
        return a, 0.0
    s = max(0, idx[0] - int(lead * sr))
    e = min(len(a), idx[-1] + int(tail * sr))
    return a[s:e], s / sr


class Narrator:
    """Base class: subclasses implement _synth(text) -> (audio, words or None)."""
    sr = 24000

    def __init__(self, lang="en", pronounce=None):
        self.lang = lang
        self.pronounce = pronounce or {}
        self._asr = None

    def speak(self, lines):
        toks = tokenize(lines, self.pronounce)
        say = " ".join(" ".join(t["say"] for t in toks if t["line"] == li) for li in range(len(lines)))
        audio, words = self._synth(say)
        dur = len(audio) / self.sr
        if not words:
            words = self._asr_words(audio)
            snap = True
        else:
            snap = False
        exp, owner = [], []
        for i, t in enumerate(toks):
            for w in t["norm"]:
                exp.append(w)
                owner.append(i)
        got = [w for w, _ in words]
        if snap:
            got = _snap(got, exp)
        times = [None] * len(exp)
        sm = difflib.SequenceMatcher(None, exp, got, autojunk=False)
        for a, b, n in sm.get_matching_blocks():
            for k in range(n):
                times[a + k] = max(0.0, words[b + k][1] - (0.06 if snap else 0.0))
        matched = sum(t is not None for t in times)
        times = _interpolate(exp, times, dur)
        for i, t in enumerate(toks):
            ws = [times[j] for j in range(len(exp)) if owner[j] == i]
            t["t"] = min(ws) if ws else None
        # tokens without spoken words (e.g. "—") inherit the next token's time
        nxt = dur
        for t in reversed(toks):
            if t["t"] is None:
                t["t"] = nxt
            nxt = t["t"]
        for i in range(1, len(toks)):
            toks[i]["t"] = max(toks[i]["t"], toks[i - 1]["t"])
        line_starts = [next((t["t"] for t in toks if t["line"] == li), 0.0) for li in range(len(lines))]
        line_starts[0] = 0.0
        return {"audio": audio, "dur": dur, "tokens": toks, "line_starts": line_starts, "say": say,
                "heard": " ".join(got), "matched": f"{matched}/{len(exp)}"}

    # ---------------------------------------------------------------- ASR fallback
    def _asr_words(self, audio):
        if self._asr is None:
            import sherpa_onnx
            sv = asset("models", "sensevoice")
            self._asr = sherpa_onnx.OfflineRecognizer.from_sense_voice(
                model=sv + "/model.int8.onnx", tokens=sv + "/tokens.txt",
                language="ko" if self.lang.startswith("ko") else "en", use_itn=False, num_threads=4)
        n16 = int(len(audio) * 16000 / self.sr)
        x16 = np.interp(np.linspace(0, len(audio) - 1, n16), np.arange(len(audio)), audio).astype(np.float32)
        st = self._asr.create_stream()
        st.accept_waveform(16000, x16)
        self._asr.decode_stream(st)
        words = []
        for tok, ts in zip(st.result.tokens, st.result.timestamps):
            if not words or tok.startswith(" ") or tok.startswith("▁"):
                words.append([tok.strip(" ▁"), ts])
            else:
                words[-1][0] += tok
        return [(re.sub(r"[^a-z0-9가-힣]", "", w.lower()), t) for w, t in words
                if re.sub(r"[^a-z0-9가-힣]", "", w.lower())]


def _interpolate(words, times, dur):
    """Fill unmatched word times proportionally to character length between known anchors."""
    n = len(words)
    if n == 0:
        return []
    known = [(i, t) for i, t in enumerate(times) if t is not None]
    anchors = [(-1, 0.0)] + known + [(n, dur)]
    out = list(times)
    for (i0, t0), (i1, t1) in zip(anchors, anchors[1:]):
        gap = list(range(i0 + 1, i1))
        if not gap:
            continue
        lens = [len(words[g]) + 1 for g in gap]
        start = t0 if i0 >= 0 else 0.0
        span = max(0.0, t1 - start)
        first_share = (len(words[i0]) + 1) if i0 >= 0 else 0
        total = sum(lens) + first_share
        acc = first_share
        for g, L in zip(gap, lens):
            out[g] = start + span * acc / total
            acc += L
    return out


class EdgeNarrator(Narrator):
    """Microsoft neural voices (e.g. en-US-BrianMultilingualNeural). Exact per-word boundaries."""

    def __init__(self, voice="en-US-BrianMultilingualNeural", rate="+20%", pitch="+0Hz", lang="en", pronounce=None):
        super().__init__(lang, pronounce)
        self.voice, self.rate, self.pitch = voice, rate, pitch
        _patch_edge_ssl()

    def _synth(self, text):
        import edge_tts

        async def run():
            c = edge_tts.Communicate(text, self.voice, rate=self.rate, pitch=self.pitch, boundary="WordBoundary")
            audio, words = bytearray(), []
            async for ch in c.stream():
                if ch["type"] == "audio":
                    audio += ch["data"]
                elif ch["type"] == "WordBoundary":
                    words.append((ch["text"], ch["offset"] / 1e7))
            return bytes(audio), words

        expected = max(1, len(_norm_words(text)))
        for attempt in range(5):
            try:
                data, raw_words = asyncio.run(run())
                audio = decode_audio(data, self.sr) if data else np.zeros(0, np.float32)
                audio, cut = trim_silence(audio, self.sr)
                words = []
                for w, t in raw_words:
                    for n in _norm_words(w):
                        words.append((n, max(0.0, t - cut)))
                # the service occasionally returns a truncated stream without raising: never accept one
                dur = len(audio) / self.sr
                if len(words) >= 0.8 * expected and dur >= 0.12 * expected:
                    return audio, words
                problem = f"truncated response ({len(words)}/{expected} words, {dur:.2f}s)"
            except Exception as e:  # transient network errors
                problem = str(e)
            if attempt == 4:
                raise RuntimeError(f"edge-tts failed for {text!r}: {problem}")
            print(f"[voice] edge-tts retry {attempt + 1}: {problem}")
            time.sleep(2 * (attempt + 1))


def _char_words(chars, starts, cut=0.0):
    """Per-character timings (ElevenLabs alignment) -> [(normalized word, start seconds)]."""
    words, cur, t0 = [], "", None
    for ch, t in zip(chars, starts):
        if ch.isspace():
            if cur:
                words.append((cur, t0))
            cur, t0 = "", None
            continue
        if t0 is None:
            t0 = t
        cur += ch
    if cur:
        words.append((cur, t0))
    return [(n, max(0.0, t - cut)) for w, t in words for n in _norm_words(w)]


class ElevenLabsNarrator(Narrator):
    """ElevenLabs voices through the API. The key comes from ELEVENLABS_API_KEY, never from the script."""
    API = "https://api.elevenlabs.io/v1"
    sr = 44100

    def __init__(self, voice_id, model="eleven_multilingual_v2", lang="en", pronounce=None, settings=None):
        super().__init__(lang, pronounce)
        self.key = os.environ.get("ELEVENLABS_API_KEY", "")
        if not self.key:
            raise RuntimeError("ELEVENLABS_API_KEY is not set: add it to the environment variables")
        self.voice_id, self.model, self.settings = voice_id, model, settings or {}

    def _synth(self, text):
        body = {"text": text, "model_id": self.model}
        if self.settings:
            body["voice_settings"] = self.settings
        url = f"{self.API}/text-to-speech/{self.voice_id}/with-timestamps?output_format=mp3_44100_128"
        expected = max(1, len(_norm_words(text)))
        for attempt in range(5):
            req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                         headers={"xi-api-key": self.key, "Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    d = json.load(r)
                audio = decode_audio(base64.b64decode(d["audio_base64"]), self.sr)
                audio, cut = trim_silence(audio, self.sr)
                al = d.get("alignment") or d["normalized_alignment"]
                words = _char_words(al["characters"], al["character_start_times_seconds"], cut)
                if len(words) >= 0.8 * expected and len(audio) / self.sr >= 0.12 * expected:
                    return audio, words
                problem = f"truncated response ({len(words)}/{expected} words)"
            except urllib.error.HTTPError as e:
                problem = f"HTTP {e.code}: {e.read().decode(errors='replace')[:300]}"
                if e.code in (400, 401, 403, 404, 422):  # bad key, voice or request: a retry cannot help
                    raise RuntimeError(f"ElevenLabs {problem}") from None
            except (urllib.error.URLError, TimeoutError, KeyError, ValueError) as e:  # network, bad payload
                problem = str(e)
            if attempt == 4:
                raise RuntimeError(f"ElevenLabs failed for {text!r}: {problem}")
            print(f"[voice] elevenlabs retry {attempt + 1}: {problem}")
            time.sleep(2 * (attempt + 1))


class KokoroNarrator(Narrator):
    """Offline fallback (Kokoro-82M). Word times via speech recognition."""

    LANG = {"en": "en-us", "en-gb": "en-gb"}

    def __init__(self, voice="am_michael", speed=1.2, lang="en", pronounce=None):
        super().__init__(lang, pronounce)
        from kokoro_onnx import Kokoro
        self.kokoro = Kokoro(asset("models", "kokoro-v1.0.onnx"), asset("models", "voices-v1.0.bin"))
        self.voice, self.speed = voice, speed

    def _synth(self, text):
        a, sr = self.kokoro.create(text, voice=self.voice, speed=self.speed, lang=self.LANG.get(self.lang, self.lang))
        a, _ = trim_silence(np.asarray(a, np.float32), sr)
        return a, None


def _patch_edge_ssl():
    """edge-tts pins certifi's CA bundle; also trust a corporate/proxy CA if the environment provides one."""
    import ssl
    import certifi
    import edge_tts.communicate as c
    extra = [p for p in (os.environ.get("SSL_CERT_FILE"), os.environ.get("REQUESTS_CA_BUNDLE")) if p and os.path.exists(p)]
    if not extra:
        return
    ctx = ssl.create_default_context(cafile=certifi.where())
    for p in extra:
        ctx.load_verify_locations(p)
    c._SSL_CTX = ctx


def make_narrator(vcfg, lang, pronounce):
    eng = vcfg.get("engine", "edge")
    if eng == "edge":
        return EdgeNarrator(vcfg.get("name", "en-US-BrianMultilingualNeural"), vcfg.get("rate", "+20%"),
                            vcfg.get("pitch", "+0Hz"), lang, pronounce)
    if eng == "elevenlabs":
        return ElevenLabsNarrator(vcfg.get("voice_id") or vcfg["name"], vcfg.get("model", "eleven_multilingual_v2"),
                                  lang, pronounce, vcfg.get("settings"))
    if eng == "kokoro":
        return KokoroNarrator(vcfg.get("name", "am_michael"), vcfg.get("speed", 1.2), lang, pronounce)
    raise ValueError(f"unknown voice engine {eng!r}")
