# bili_dl.py BVID... : bilibili download (best avc1 up to 1080p via try_look, cid from x/player/pagelist because x/web-interface/view and yt-dlp get blocked) + best audio, exact 4 MB range chunks, to work/youtube/bl_<BV>.mp4. Run from anywhere: python3 ragestyles-shorts/tools/bili_dl.py BV...
import json, os, subprocess, sys, time, urllib.request
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124"
JAR = "/tmp/bili.jar"  # cookie jar, made first: curl -s -c /tmp/bili.jar -A "Mozilla/5.0" https://www.bilibili.com/ -o /dev/null
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "work", "youtube")
def api(url):
    r = subprocess.run(["curl", "-s", "-b", JAR, "-A", UA, "-e", "https://www.bilibili.com", url], capture_output=True, text=True)
    return json.loads(r.stdout)
def fetch(url, path):
    """Range requests of 4 MB with retries; every chunk must come back at its exact size (a 200 with the whole file
    instead of a 206 would corrupt a plain resume)."""
    h = subprocess.run(["curl", "-sI", "-A", UA, "-e", "https://www.bilibili.com", url], capture_output=True, text=True).stdout
    total = [int(l.split(":")[1]) for l in h.lower().splitlines() if l.startswith("content-length")][-1]
    step = 4 << 20
    with open(path, "wb") as f:
        pos = 0
        while pos < total:
            end = min(pos + step, total) - 1
            for i in range(30):
                r = subprocess.run(["curl", "-s", "-A", UA, "-e", "https://www.bilibili.com", "--max-time", "90",
                                    "-r", f"{pos}-{end}", url], capture_output=True)
                if r.returncode == 0 and len(r.stdout) == end - pos + 1:
                    break
                time.sleep(2)
            else:
                raise RuntimeError("chunk failed " + path)
            f.write(r.stdout)
            pos = end + 1
for bv in sys.argv[1:]:
    out = f"{OUT}/bl_{bv}.mp4"
    if os.path.exists(out):
        print("have", bv); continue
    v = api(f"https://api.bilibili.com/x/player/pagelist?bvid={bv}")["data"][0]
    json.dump(v, open(f"{OUT}/bl_{bv}.info.json", "w"), ensure_ascii=False)
    d = api(f"https://api.bilibili.com/x/player/playurl?bvid={bv}&cid={v['cid']}&qn=80&fnval=4048&fourk=1&try_look=1")["data"]["dash"]
    vid = max([x for x in d["video"] if x["codecs"].startswith("avc1")], key=lambda x: (x["height"] * x["width"], x["bandwidth"]))
    aud = max(d["audio"], key=lambda x: x["bandwidth"])
    fetch(vid["baseUrl"], f"{OUT}/{bv}.v.m4s"); fetch(aud["baseUrl"], f"{OUT}/{bv}.a.m4s")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", f"{OUT}/{bv}.v.m4s", "-i", f"{OUT}/{bv}.a.m4s",
                    "-c", "copy", "-movflags", "+faststart", out], check=True)
    os.remove(f"{OUT}/{bv}.v.m4s"); os.remove(f"{OUT}/{bv}.a.m4s")
    print("got", bv, vid["width"], vid["height"], v["part"][:50], flush=True)
