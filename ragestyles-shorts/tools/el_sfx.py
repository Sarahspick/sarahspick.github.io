"""Generate sound effects with the ElevenLabs sound generation API and store them as assets/sfx_el/<name>.wav
(lossless 48 kHz PCM from the API, 24 bit stereo), usable in plans as "el:<name>". The chosen wav files are committed (a prompt never gives the same sound
twice) and their prompts are kept in assets/sfx_el/prompts.json. Needs ELEVENLABS_API_KEY (never printed).
  python3 tools/el_sfx.py                      # generate any sound in prompts.json whose wav is missing
  python3 tools/el_sfx.py NAME "prompt" [SECONDS]   # add one sound to prompts.json and generate it
"""
import json
import os
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(ROOT, "assets", "sfx_el")
MANIFEST = os.path.join(DIR, "prompts.json")


def generate(name, text, seconds=None, influence=0.6):
    """Lossless 48 kHz PCM from the API (stereo s16le, interleaved), peak normalised to -1 dBFS, 24 bit wav."""
    import numpy as np
    import soundfile as sf
    body = {"text": text, "prompt_influence": influence}
    if seconds:
        body["duration_seconds"] = float(seconds)
    req = urllib.request.Request("https://api.elevenlabs.io/v1/sound-generation?output_format=pcm_48000",
                                 data=json.dumps(body).encode(),
                                 headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"],
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        x = np.frombuffer(r.read(), dtype="<i2").astype(np.float32).reshape(-1, 2) / 32768.0
    loud = np.nonzero(np.abs(x).max(1) > 1e-3)[0]
    x = x[:loud[-1] + 1] if len(loud) else x                                               # trim the silent tail
    x *= 10 ** (-1 / 20) / max(np.abs(x).max(), 1e-6)
    f = min(len(x) // 4, 480)                                                              # 10 ms fade out
    x[-f:] *= np.linspace(1, 0, f)[:, None]
    sf.write(os.path.join(DIR, name + ".wav"), x, 48000, subtype="PCM_24")
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
