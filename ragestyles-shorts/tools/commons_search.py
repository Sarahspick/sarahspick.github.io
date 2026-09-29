"""Wikimedia Commons video search -> JSON list with license, size, duration, url."""
import json, sys, time, urllib.parse, subprocess
UA = "RageStylesShortsResearch/1.0 (https://github.com/Sarahspick/sarahspick.github.io; video licensing research)"
API = "https://commons.wikimedia.org/w/api.php"
def get(params):
    url = API + "?" + urllib.parse.urlencode(params)
    for i in range(4):
        r = subprocess.run(["curl", "-s", "--max-time", "40", "-A", UA, url], capture_output=True, text=True)
        try:
            return json.loads(r.stdout)
        except Exception:
            time.sleep(2 + 3 * i)
    return {}
def search(q, limit=50):
    d = get({"action": "query", "format": "json", "generator": "search", "gsrnamespace": 6, "gsrlimit": limit,
             "gsrsearch": f"filetype:video {q}", "prop": "imageinfo", "iiprop": "url|size|mime|extmetadata|mediatype",
             "iiextmetadatafilter": "LicenseShortName|Artist|ImageDescription|DateTimeOriginal|Credit"})
    out = []
    for p in (d.get("query", {}).get("pages", {}) or {}).values():
        ii = (p.get("imageinfo") or [{}])[0]
        md = ii.get("extmetadata", {})
        out.append({"title": p["title"], "url": ii.get("url"), "w": ii.get("width"), "h": ii.get("height"),
                    "dur": ii.get("duration"), "size_mb": round((ii.get("size") or 0) / 1e6, 1), "mime": ii.get("mime"),
                    "license": md.get("LicenseShortName", {}).get("value"),
                    "artist": md.get("Artist", {}).get("value", "")[:120],
                    "desc": md.get("ImageDescription", {}).get("value", "")[:200], "q": q})
    return out
if __name__ == "__main__":
    allr = {}
    for q in sys.argv[2:]:
        rs = search(q)
        for r in rs: allr.setdefault(r["title"], r)
        print(f"{q!r}: {len(rs)}", file=sys.stderr)
        time.sleep(1.5)
    json.dump(list(allr.values()), open(sys.argv[1], "w"), indent=1, ensure_ascii=False)
