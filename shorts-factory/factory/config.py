import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
WORK = os.path.join(ROOT, "work")
OUTPUT = os.path.join(ROOT, "output")

W, H, FPS = 1080, 1920, 30
SR = 48000

# Colours follow X/Twitter's own palettes so the post looks native.
THEMES = {
    "dark": {
        "bg": (0, 0, 0), "text": (231, 233, 234), "subtext": (113, 118, 123), "border": (47, 51, 54),
        "caption": (255, 255, 255), "caption_hl": (255, 212, 0), "badge": (29, 155, 240),
        "hook_1": (255, 255, 255), "hook_2": (255, 212, 0), "stroke": (0, 0, 0),
        "arrow": (255, 45, 45), "dim": 0.62, "card_bg": (22, 24, 28), "card_text": (231, 233, 234),
    },
    "light": {
        "bg": (255, 255, 255), "text": (15, 20, 25), "subtext": (83, 100, 113), "border": (207, 217, 222),
        "caption": (15, 20, 25), "caption_hl": (29, 155, 240), "badge": (29, 155, 240),
        "hook_1": (255, 255, 255), "hook_2": (255, 212, 0), "stroke": (0, 0, 0),
        "arrow": (255, 45, 45), "dim": 0.62, "card_bg": (247, 249, 249), "card_text": (15, 20, 25),
    },
}

DEFAULT_CHANNEL = {
    "theme": "dark",
    "lang": "en",
    "voice": {"engine": "edge", "name": "en-US-BrianMultilingualNeural", "rate": "+20%"},
    "pronounce": {},
}


def load_channel(path=None):
    ch = json.loads(json.dumps(DEFAULT_CHANNEL))
    if path and os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            user = json.load(f)
        for k, v in user.items():
            if isinstance(v, dict) and isinstance(ch.get(k), dict):
                ch[k].update(v)
            else:
                ch[k] = v
    return ch


def asset(*p):
    return os.path.join(ASSETS, *p)


def rel(p):
    return p if os.path.isabs(p) else os.path.join(ROOT, p)
