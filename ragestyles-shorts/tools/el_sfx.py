"""Generate sound effects with the ElevenLabs sound generation API and store them as assets/sfx_el/<name>.wav
(48 kHz stereo), usable in plans as "el:<name>". Prompts are kept in assets/sfx_el/prompts.json so any session can
regenerate the same set; the wav files themselves are not committed. Needs ELEVENLABS_API_KEY (never printed).
  python3 tools/el_sfx.py                      # (re)generate every sound in prompts.json that is missing
  python3 tools/el_sfx.py NAME "prompt" [SECONDS]   # add one sound to prompts.json and generate it
"""
import json
import os
import subprocess
import sys
import tempfile
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(ROOT, "assets", "sfx_el")
MANIFEST = os.path.join(DIR, "prompts.json")


def generate(name, text, seconds=None, influence=0.6):
    body = {"text": text, "prompt_influence": influence}
    if seconds:
        body["duration_seconds"] = float(seconds)
    req = urllib.request.Request("https://api.elevenlabs.io/v1/sound-generation", data=json.dumps(body).encode(),
                                 headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"],
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r, tempfile.NamedTemporaryFile(suffix=".mp3") as f:
        f.write(r.read())
        f.flush()
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", f.name, "-ar", "48000", "-ac", "2",
                        os.path.join(DIR, name + ".wav")], check=True)
    print("el:" + name)


def main():
    os.makedirs(DIR, exist_ok=True)
    sounds = json.load(open(MANIFEST)) if os.path.exists(MANIFEST) else {}
    if len(sys.argv) >= 3:
        sounds[sys.argv[1]] = {"text": sys.argv[2], "seconds": float(sys.argv[3]) if len(sys.argv) > 3 else None}
        json.dump(sounds, open(MANIFEST, "w"), indent=1, ensure_ascii=False)
        generate(sys.argv[1], **sounds[sys.argv[1]])
        return
    for name, s in sounds.items():
        if not os.path.exists(os.path.join(DIR, name + ".wav")):
            generate(name, **s)


if __name__ == "__main__":
    main()
