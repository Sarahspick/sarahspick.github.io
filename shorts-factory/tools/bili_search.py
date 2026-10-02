"""Fast Bilibili video search (titles, durations, views) for footage hunting.

    python tools/bili_search.py "Mercedes G-Turn" "奔驰 G 原地掉头"
"""
import re
import sys
import html

import requests

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"


def session():
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Referer": "https://www.bilibili.com/"})
    s.get("https://www.bilibili.com/", timeout=20)
    return s


def search(s, q, page=1, order="totalrank"):
    r = s.get("https://api.bilibili.com/x/web-interface/search/type",
              params={"search_type": "video", "keyword": q, "page": page, "order": order}, timeout=20)
    d = r.json()
    out = []
    for v in (d.get("data") or {}).get("result") or []:
        t = html.unescape(re.sub(r"<[^>]+>", "", v.get("title", "")))
        out.append((v.get("bvid"), v.get("duration"), v.get("play"), v.get("author"), t))
    return out, d.get("code"), d.get("message")


if __name__ == "__main__":
    s = session()
    for q in sys.argv[1:]:
        res, code, msg = search(s, q)
        print(f"\n## {q}  (code {code} {msg if code else ''})")
        for bvid, dur, play, author, t in res[:14]:
            print(f"{bvid}  {str(dur):>6}  {str(play):>8}  {str(author)[:14]:14}  {t[:80]}")
