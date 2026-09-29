"""ElevenLabs VO (Mark) with character timestamps -> vo.mp3 + words.json.
Usage: python3 tts.py <short_dir>   (reads <short_dir>/script.txt)"""
import base64, json, os, sys, urllib.request

MARK = "UgBBYS2sOqTuMpoF3BR0"
d = sys.argv[1]
txt = open(os.path.join(d, "script.txt")).read().replace("\n", " ").strip()
body = {"text": txt, "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.4, "similarity_boost": 0.8, "style": 0.35,
                           "use_speaker_boost": True, "speed": 1.08}}
req = urllib.request.Request(
    f"https://api.elevenlabs.io/v1/text-to-speech/{MARK}/with-timestamps?output_format=mp3_44100_128",
    data=json.dumps(body).encode(),
    headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"], "Content-Type": "application/json"})
r = json.load(urllib.request.urlopen(req))
open(os.path.join(d, "vo.mp3"), "wb").write(base64.b64decode(r["audio_base64"]))
a = r["alignment"]
words, cur, s, e = [], "", 0.0, 0.0
for c, t0, t1 in zip(a["characters"], a["character_start_times_seconds"], a["character_end_times_seconds"]):
    if c == " ":
        if cur: words.append((cur, s, e)); cur = ""
        continue
    if not cur: s = t0
    cur += c; e = t1
if cur: words.append((cur, s, e))
json.dump(words, open(os.path.join(d, "words.json"), "w"))
print(len(txt), "chars,", round(words[-1][2], 2), "s")
