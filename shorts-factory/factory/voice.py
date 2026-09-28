"""Narration: Kokoro TTS per sentence + SenseVoice alignment for caption-line and word timings."""
import difflib
import re

import numpy as np

from .config import asset
from .gfx import plain

try:
    from num2words import num2words
except ImportError:  # alignment still works, numbers just fall back to interpolation
    num2words = None

LANG_CODES = {"en": "en-us", "en-gb": "en-gb", "ko": "ko"}


def _norm_words(text):
    """Lower-case alphanumeric word list with digits spelled out (so '1,000' matches 'ONE THOUSAND')."""
    out = []
    for w in re.findall(r"[A-Za-z0-9][A-Za-z0-9,.'%]*", text.replace("-", " ")):
        w = w.strip(".,'")
        if re.fullmatch(r"[0-9][0-9,]*(\.[0-9]+)?", w) and num2words:
            num = w.replace(",", "")
            try:
                spelled = num2words(float(num) if "." in num else int(num))
                out.extend(p for p in re.split(r"[\s-]+", spelled.replace(",", "")) if p and p != "and")
                continue
            except Exception:
                pass
        p = re.sub(r"[^a-z0-9]", "", w.lower())
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


class Narrator:
    def __init__(self, voice="am_michael", speed=1.12, lang="en", pronounce=None):
        from kokoro_onnx import Kokoro
        self.kokoro = Kokoro(asset("models", "kokoro-v1.0.onnx"), asset("models", "voices-v1.0.bin"))
        self.voice, self.speed = voice, speed
        self.lang = LANG_CODES.get(lang, lang)
        self.pronounce = pronounce or {}
        self.sr = 24000
        self._asr = None

    # ------------------------------------------------------------ text
    def say_text(self, display):
        s = plain(display)
        for k, v in self.pronounce.items():
            s = re.sub(rf"(?<![\w-]){re.escape(k)}(?![\w-])", v, s)
        return s

    # ------------------------------------------------------------ audio
    def synth(self, text):
        a, sr = self.kokoro.create(text, voice=self.voice, speed=self.speed, lang=self.lang)
        assert sr == self.sr
        return self._trim(np.asarray(a, dtype=np.float32))

    def _trim(self, a, lead=0.03, tail=0.09):
        win = int(self.sr * 0.01)
        env = np.sqrt(np.convolve(a ** 2, np.ones(win) / win, mode="same"))
        thr = max(1e-4, env.max() * 10 ** (-40 / 20))
        idx = np.where(env > thr)[0]
        if len(idx) == 0:
            return a
        s = max(0, idx[0] - int(lead * self.sr))
        e = min(len(a), idx[-1] + int(tail * self.sr))
        return a[s:e]

    # ------------------------------------------------------------ alignment
    def _recognizer(self):
        if self._asr is None:
            import sherpa_onnx
            sv = asset("models", "sensevoice")
            self._asr = sherpa_onnx.OfflineRecognizer.from_sense_voice(
                model=sv + "/model.int8.onnx", tokens=sv + "/tokens.txt",
                language="en" if self.lang.startswith("en") else self.lang, use_itn=False, num_threads=4)
        return self._asr

    def asr_words(self, audio):
        n16 = int(len(audio) * 16000 / self.sr)
        x16 = np.interp(np.linspace(0, len(audio) - 1, n16), np.arange(len(audio)), audio).astype(np.float32)
        rec = self._recognizer()
        st = rec.create_stream()
        st.accept_waveform(16000, x16)
        rec.decode_stream(st)
        words = []
        for tok, ts in zip(st.result.tokens, st.result.timestamps):
            if not words or tok.startswith(" ") or tok.startswith("▁"):
                words.append([tok.strip(" ▁"), ts])
            else:
                words[-1][0] += tok
        return [(re.sub(r"[^a-z0-9]", "", w.lower()), t) for w, t in words if re.sub(r"[^a-z0-9]", "", w.lower())]

    def speak(self, lines):
        """Synthesize a sentence given its caption lines.

        Returns dict(audio, dur, line_starts, words=[(word, t)]) with times relative to the sentence start.
        """
        say_lines = [self.say_text(l) for l in lines]
        audio = self.synth(" ".join(say_lines))
        dur = len(audio) / self.sr
        # expected words, remembering which line each belongs to
        exp, line_of = [], []
        for i, sl in enumerate(say_lines):
            ws = _norm_words(sl)
            exp += ws
            line_of += [i] * len(ws)
        times = [None] * len(exp)
        try:
            got = self.asr_words(audio)
        except Exception as e:  # never block a render on alignment
            print("[voice] alignment failed:", e)
            got = []
        if got:
            sm = difflib.SequenceMatcher(None, exp, _snap([w for w, _ in got], exp), autojunk=False)
            for a, b, n in sm.get_matching_blocks():
                for k in range(n):
                    times[a + k] = max(0.0, got[b + k][1] - 0.06)
        matched = sum(t is not None for t in times)
        times = self._interpolate(exp, times, dur)
        line_starts = [0.0]
        for i in range(1, len(say_lines)):
            first = next((j for j, li in enumerate(line_of) if li == i), None)
            line_starts.append(times[first] if first is not None else dur * i / len(say_lines))
        for i in range(1, len(line_starts)):  # monotonic, and never before the previous line
            line_starts[i] = max(line_starts[i], line_starts[i - 1] + 0.25)
        return {"audio": audio, "dur": dur, "line_starts": line_starts,
                "words": list(zip(exp, times)), "say": " ".join(say_lines),
                "asr": " ".join(w for w, _ in got), "matched": f"{matched}/{len(exp)}"}

    @staticmethod
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
            # the word after the last known anchor starts after that anchor's own word
            first_share = (len(words[i0]) + 1) if i0 >= 0 else 0
            total = sum(lens) + first_share
            acc = first_share
            for g, L in zip(gap, lens):
                out[g] = start + span * acc / total
                acc += L
        return out
