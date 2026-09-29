"""List video candidates for every footage slot in a script.

    python tools/find_footage.py scripts/mercedes_bounce.en.json            # YouTube
    python tools/find_footage.py scripts/mercedes_bounce.en.json --site bili # Bilibili (often has official films re-uploaded)
    python tools/find_footage.py scripts/mercedes_bounce.en.json c_rock1     # one slot

Put the pick into the script as  "src": "yt:VIDEO_ID"  or  "src": "bili:BVxxxx"  plus "start" seconds.
Official brand / press channels are flagged first: reused footage from them is far less likely to get a Content ID claim.
"""
import argparse
import json

import yt_dlp

OFFICIAL_HINTS = ("official", "newsroom", "media", "press", "mercedes-benz", "amazon", "samsung", "apple", "aws", "bmw", "hyundai")
SEARCH = {"yt": "ytsearch{n}:{q}", "bili": "bilisearch{n}:{q}"}


def search(query, site, n=8):
    with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True, "extract_flat": True}) as y:
        res = y.extract_info(SEARCH[site].format(n=n, q=query), download=False)
        out = []
        for e in res.get("entries", []):
            if site == "bili" and not e.get("title"):  # flat bilibili results lack metadata: resolve each
                e = y.extract_info(e["url"], download=False)
            ch = e.get("channel") or e.get("uploader") or ""
            score = 2 if any(h in ch.lower() for h in OFFICIAL_HINTS) else 0
            out.append((score, e.get("duration") or 0, ch, e.get("title") or "", e.get("webpage_url") or e.get("url")))
    return sorted(out, key=lambda r: -r[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script")
    ap.add_argument("slots", nargs="*")
    ap.add_argument("--site", default="yt", choices=list(SEARCH))
    args = ap.parse_args()
    sc = json.load(open(args.script, encoding="utf-8"))
    for cid, spec in sc["clips"].items():
        if spec.get("kind") == "card" or (args.slots and cid not in args.slots):
            continue
        q = spec.get("search") or spec.get("desc") or cid
        print(f"\n== {cid}: {spec.get('desc', '')}\n   query: {q}   (current src: {spec.get('src')})")
        try:
            for score, dur, ch, title, url in search(q, args.site):
                tag = "OFFICIAL?" if score else "         "
                print(f"   {tag} {int(dur) // 60:2d}:{int(dur) % 60:02d}  {ch[:24]:24}  {title[:70]}\n{'':15}{url}")
        except Exception as e:
            print("   search failed:", str(e).splitlines()[0])


if __name__ == "__main__":
    main()
