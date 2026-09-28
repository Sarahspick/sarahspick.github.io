"""List YouTube candidates for every footage slot in a script (needs network access to YouTube).

    python tools/find_footage.py scripts/mercedes_bounce.en.json          # all slots
    python tools/find_footage.py scripts/mercedes_bounce.en.json c_bounce # one slot

Prefers official channels (the brand's own uploads, press/newsroom channels) and Creative Commons uploads,
because reused footage from those sources is far less likely to get a Content ID claim.
"""
import json
import sys

import yt_dlp

OFFICIAL_HINTS = ("official", "newsroom", "media", "press", "mercedes-benz", "amazon", "samsung", "apple", "aws", "bmw", "hyundai")


def search(query, n=8):
    with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True, "extract_flat": True}) as y:
        res = y.extract_info(f"ytsearch{n}:{query}", download=False)
    out = []
    for e in res.get("entries", []):
        ch = (e.get("channel") or e.get("uploader") or "")
        score = 2 if any(h in ch.lower() for h in OFFICIAL_HINTS) else 0
        out.append((score, e.get("duration") or 0, ch, e.get("title"), e.get("url") or f"https://www.youtube.com/watch?v={e.get('id')}"))
    return sorted(out, key=lambda r: (-r[0], r[1] or 9999))


def main():
    sc = json.load(open(sys.argv[1], encoding="utf-8"))
    only = set(sys.argv[2:])
    for cid, spec in sc["clips"].items():
        if spec.get("kind") == "card" or (only and cid not in only):
            continue
        q = spec.get("search") or spec.get("desc")
        print(f"\n== {cid}: {spec.get('desc')}\n   query: {q}")
        for c in spec.get("candidates", []):
            print(f"   [given] {c}")
        try:
            for score, dur, ch, title, url in search(q):
                tag = "OFFICIAL?" if score else "         "
                print(f"   {tag} {int(dur) // 60:2d}:{int(dur) % 60:02d}  {ch[:28]:28}  {title[:70]}\n{'':15}{url}")
        except Exception as e:
            print("   search failed:", str(e).splitlines()[0])


if __name__ == "__main__":
    main()
