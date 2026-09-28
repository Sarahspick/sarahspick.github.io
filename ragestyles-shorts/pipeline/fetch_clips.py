"""Download selected YFCC100M clips (CC BY / CC BY-SA only) and write attribution records.

Usage: python3 fetch_clips.py <catalog.sqlite> <photoid> [<photoid> ...]
Clips land in ../work/clips/<photoid>.mp4 ; attribution goes to ../sources/sources.json
"""
import json, os, sqlite3, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CLIPS = os.path.join(ROOT, "work", "clips")
SRC_JSON = os.path.join(ROOT, "sources", "sources.json")
BUCKET = "https://multimedia-commons.s3-us-west-2.amazonaws.com/data/videos/mp4"
ALLOWED = {"Attribution License": "CC BY 2.0", "Attribution-ShareAlike License": "CC BY-SA 2.0"}


def main():
    db = sqlite3.connect(sys.argv[1], check_same_thread=False)
    ids = [int(x) for x in sys.argv[2:]]
    os.makedirs(CLIPS, exist_ok=True)
    os.makedirs(os.path.dirname(SRC_JSON), exist_ok=True)
    sources = json.load(open(SRC_JSON)) if os.path.exists(SRC_JSON) else {}

    def one(pid):
        r = db.execute("select hash,title,unickname,uid,pageurl,licensename,licenseurl,datetaken,duration "
                       "from videos where photoid=?", (pid,)).fetchone()
        if not r:
            return pid, "missing"
        h, title, nick, uid, page, lic, licurl, taken, dur = r
        if lic not in ALLOWED:
            return pid, f"SKIP license {lic}"
        out = os.path.join(CLIPS, f"{pid}.mp4")
        if not os.path.exists(out):
            url = f"{BUCKET}/{h[:3]}/{h[3:6]}/{h}.mp4"
            data = urllib.request.urlopen(url, timeout=120).read()
            open(out + ".part", "wb").write(data)
            os.replace(out + ".part", out)
        sources[str(pid)] = {"title": title or "(untitled)", "author": nick, "flickr_user": uid,
                             "url": page.replace("http://", "https://"), "license": ALLOWED[lic],
                             "license_url": licurl, "date_taken": taken, "duration": dur,
                             "via": "YFCC100M / Multimedia Commons (s3://multimedia-commons)"}
        return pid, "ok"

    with ThreadPoolExecutor(8) as ex:
        for pid, st in ex.map(one, ids):
            if st != "ok":
                print(pid, st)
    json.dump(sources, open(SRC_JSON, "w"), indent=1, ensure_ascii=False)
    print("clips:", len(os.listdir(CLIPS)), "sources:", len(sources))


if __name__ == "__main__":
    main()
