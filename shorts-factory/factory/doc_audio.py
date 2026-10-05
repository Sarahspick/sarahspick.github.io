"""ElevenLabs audio for long-form documentaries: narration (with word timings), score and sound effects.

Everything is cached under work/<doc id>/ keyed by a hash of the request, so re-renders never pay twice.
Key: ELEVENLABS_API_KEY.
"""
import base64
import hashlib
import json
import os
import subprocess
import time
import urllib.error
import urllib.request

API = "https://api.elevenlabs.io"


def _post(path, body, accept_json=True, retries=4):
    key = os.environ["ELEVENLABS_API_KEY"]
    data = json.dumps(body).encode()
    for attempt in range(retries):
        req = urllib.request.Request(API + path, data=data, method="POST",
                                     headers={"xi-api-key": key, "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                raw = r.read()
            return json.loads(raw) if accept_json else raw
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")[:400]
            if e.code in (429, 500, 502, 503) and attempt < retries - 1:
                time.sleep(4 * (attempt + 1))
                continue
            raise RuntimeError(f"ElevenLabs {path} {e.code}: {msg}")
        except (urllib.error.URLError, TimeoutError):
            if attempt == retries - 1:
                raise
            time.sleep(4 * (attempt + 1))


def _key(*parts):
    return hashlib.sha1("|".join(map(str, parts)).encode()).hexdigest()[:16]


def narrate(text, voice, cache_dir, prev_text="", next_text=""):
    """Speak one paragraph. Returns (mp3 path, words) where words = [(word, start, end), ...] in seconds."""
    os.makedirs(cache_dir, exist_ok=True)
    k = _key(voice["id"], voice.get("model"), json.dumps(voice.get("settings", {}), sort_keys=True), text, prev_text, next_text)
    mp3, js = os.path.join(cache_dir, k + ".mp3"), os.path.join(cache_dir, k + ".json")
    if not (os.path.exists(mp3) and os.path.exists(js)):
        body = {"text": text, "model_id": voice.get("model", "eleven_multilingual_v2"),
                "voice_settings": voice.get("settings", {})}
        if prev_text:
            body["previous_text"] = prev_text
        if next_text:
            body["next_text"] = next_text
        r = _post(f"/v1/text-to-speech/{voice['id']}/with-timestamps", body)
        with open(mp3, "wb") as f:
            f.write(base64.b64decode(r["audio_base64"]))
        with open(js, "w") as f:
            json.dump(r.get("alignment") or r.get("normalized_alignment"), f)
    al = json.load(open(js))
    return mp3, _words(al)


def _words(al):
    chars, st, en = al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]
    out, cur, s0, e0 = [], "", None, None
    for c, s, e in zip(chars, st, en):
        if c.isspace():
            if cur:
                out.append((cur, s0, e0))
            cur, s0 = "", None
            continue
        if s0 is None:
            s0 = s
        cur += c
        e0 = e
    if cur:
        out.append((cur, s0, e0))
    return out


def music(prompt, seconds, cache_dir):
    """Compose an instrumental cue of about `seconds` (ElevenLabs Music)."""
    os.makedirs(cache_dir, exist_ok=True)
    ms = int(max(10, min(300, seconds)) * 1000)
    path = os.path.join(cache_dir, f"music_{_key(prompt, ms)}.mp3")
    if not os.path.exists(path):
        raw = _post("/v1/music", {"prompt": prompt, "music_length_ms": ms}, accept_json=False)
        with open(path, "wb") as f:
            f.write(raw)
    return path


def sfx(text, seconds, cache_dir, influence=0.5, loop=False):
    os.makedirs(cache_dir, exist_ok=True)
    path = os.path.join(cache_dir, f"sfx_{_key(text, seconds, influence, loop)}.mp3")
    if not os.path.exists(path):
        body = {"text": text, "duration_seconds": seconds, "prompt_influence": influence}
        if loop:
            body["loop"] = True
        raw = _post("/v1/sound-generation", body, accept_json=False)
        with open(path, "wb") as f:
            f.write(raw)
    return path


def duration(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", path]).decode().strip())
