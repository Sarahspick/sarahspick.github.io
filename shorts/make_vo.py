"""ElevenLabs voiceover with word timings for a Short.

python3 shorts/make_vo.py WORKDIR "script text" [--voice TX3LPaxmHKxFdv7VOQHJ]
Writes WORKDIR/vo.mp3 and WORKDIR/words.json ([word, start, end] in seconds). Needs ELEVENLABS_API_KEY.
Default voice: Liam (energetic, American, social media).
"""
import argparse, base64, json, os, urllib.request

ap = argparse.ArgumentParser()
ap.add_argument("work"); ap.add_argument("text")
ap.add_argument("--voice", default="TX3LPaxmHKxFdv7VOQHJ")
a = ap.parse_args()
body = json.dumps({"text": a.text, "model_id": "eleven_multilingual_v2",
                   "voice_settings": {"stability": 0.4, "similarity_boost": 0.8, "style": 0.35, "use_speaker_boost": True}}).encode()
req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{a.voice}/with-timestamps", data=body,
                             headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"], "Content-Type": "application/json"})
d = json.load(urllib.request.urlopen(req, timeout=120))
open(os.path.join(a.work, "vo.mp3"), "wb").write(base64.b64decode(d["audio_base64"]))
al = d["alignment"]
words, cur, s, e = [], "", None, None
for c, t0, t1 in zip(al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]):
    if c == " ":
        if cur:
            words.append((cur, s, e)); cur = ""
        continue
    if not cur:
        s = t0
    cur += c; e = t1
if cur:
    words.append((cur, s, e))
json.dump(words, open(os.path.join(a.work, "words.json"), "w"))
print(len(words), "words,", f"{words[-1][2]:.1f}s")
