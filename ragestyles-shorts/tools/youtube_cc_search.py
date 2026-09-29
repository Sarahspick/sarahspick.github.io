"""YouTube search restricted to Creative Commons (CC BY) videos: metadata only, nothing is downloaded.

Usage: python3 tools/youtube_cc_search.py "deadlift world record" "strongman" [--json out.json]
Prints id, views, length, age, channel, title. The CC filter (sp=EgIwAQ%3D%3D) only returns videos whose uploader
chose "Creative Commons Attribution license (reuse allowed)". Downloading from YouTube is blocked in the cloud
container (bot check), so the owner downloads the chosen files and uploads them to the chat.
"""
import json
import re
import subprocess
import sys
import time
import urllib.parse

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"


def text(o):
    if not o:
        return ""
    return o.get("simpleText") or "".join(r.get("text", "") for r in o.get("runs", []))


def search(q):
    url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(q) + "&sp=EgIwAQ%253D%253D"
    h = subprocess.run(["curl", "-s", "--max-time", "30", "-A", UA, "-H", "Accept-Language: en-US,en;q=0.9", url],
                       capture_output=True, text=True).stdout
    m = re.search(r"var ytInitialData = (\{.*?\});</script>", h, re.S)
    if not m:
        return []
    out = []

    def walk(o):
        if isinstance(o, dict):
            if "videoRenderer" in o:
                v = o["videoRenderer"]
                out.append({"id": v.get("videoId"), "views": text(v.get("viewCountText")), "length": text(v.get("lengthText")),
                             "age": text(v.get("publishedTimeText")), "channel": text(v.get("ownerText")),
                             "title": text(v.get("title")), "query": q})
            for x in o.values():
                walk(x)
        elif isinstance(o, list):
            for x in o:
                walk(x)
    walk(json.loads(m.group(1)))
    return out


if __name__ == "__main__":
    args = sys.argv[1:]
    out_json = None
    if "--json" in args:
        i = args.index("--json")
        out_json = args[i + 1]
        args = args[:i] + args[i + 2:]
    allr = {}
    for q in args:
        rs = search(q)
        print(f"== {q}: {len(rs)}")
        for r in rs[:15]:
            allr.setdefault(r["id"], r)
            print(f"   {r['id']} {r['views'][:18]:18s} {r['length']:>8s} {r['age'][:16]:16s} {r['channel'][:24]:24s} | {r['title'][:80]}")
        time.sleep(1.2)
    if out_json:
        json.dump(list(allr.values()), open(out_json, "w"), indent=1, ensure_ascii=False)
