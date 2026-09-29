"""YouTube search restricted to Creative Commons videos (sp=EgIwAQ%3D%3D); prints id, views, duration, channel, title."""
import re, json, sys, subprocess, urllib.parse, time
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
def search(q):
    url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(q) + "&sp=EgIwAQ%253D%253D"
    h = subprocess.run(["curl", "-s", "--max-time", "30", "-A", UA, "-H", "Accept-Language: en-US,en;q=0.9", url], capture_output=True, text=True).stdout
    m = re.search(r"var ytInitialData = (\{.*?\});</script>", h, re.S)
    if not m: return []
    d = json.loads(m.group(1)); out = []
    def walk(o):
        if isinstance(o, dict):
            if "videoRenderer" in o:
                v = o["videoRenderer"]
                out.append((v.get("videoId"), v.get("viewCountText", {}).get("simpleText", ""), v.get("lengthText", {}).get("simpleText", ""),
                            "".join(r.get("text", "") for r in v.get("ownerText", {}).get("runs", [])),
                            "".join(r.get("text", "") for r in v.get("title", {}).get("runs", []))))
            for x in o.values(): walk(x)
        elif isinstance(o, list):
            for x in o: walk(x)
    walk(d)
    return out
for q in sys.argv[1:]:
    rs = search(q)
    print(f"== {q}: {len(rs)}")
    for r in rs[:12]:
        print(f"   {r[0]} {r[1][:16]:16s} {r[2]:>7s} {r[3][:22]:22s} | {r[4][:70]}")
    time.sleep(1)
