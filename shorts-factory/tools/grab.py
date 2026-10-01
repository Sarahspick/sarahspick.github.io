"""Parallel footage downloader.   python tools/grab.py bili:BVxxx dm:xyz ...
Saves work/sources/<platform>_<id>.mp4 (+ .info.json), the same names the renderer looks for."""
import concurrent.futures as cf
import os
import sys

import yt_dlp

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from factory.media import SOURCES, playlist_item, source_url, ytdlp_opts  # noqa: E402


def grab(src):
    pre, _, vid = src.partition(":")
    key = f"{pre}_{vid}".replace("/", "_")   # same file name as media.fetch (x:<status>/<n>)
    if any(f.startswith(key + ".") and f.endswith(".mp4") for f in os.listdir(SOURCES)):
        return src, "cached"
    url = source_url(src)
    try:
        with yt_dlp.YoutubeDL(ytdlp_opts(skip_download=True, **playlist_item(src))) as y:
            info = y.extract_info(url, download=False)
            dur = (info["entries"][0] if info.get("entries") else info).get("duration") or 0
        cap = 1080 if dur <= 600 else 720
        opts = ytdlp_opts(outtmpl=os.path.join(SOURCES, key + ".%(ext)s"), noprogress=True,
                          format="bv*+ba/b", format_sort=[f"res:{cap}", "fps", "br"], merge_output_format="mp4",
                          writeinfojson=True, fragment_retries=5, concurrent_fragment_downloads=4,
                          **playlist_item(src))
        with yt_dlp.YoutubeDL(opts) as y:
            info = y.extract_info(url, download=True)
            info = info["entries"][0] if info.get("entries") else info
        return src, f"ok {info.get('width')}x{info.get('height')} {dur:.0f}s  {info.get('title', '')[:50]}"
    except Exception as e:
        return src, "FAIL " + str(e).splitlines()[0][:140]


if __name__ == "__main__":
    os.makedirs(SOURCES, exist_ok=True)
    with cf.ThreadPoolExecutor(4) as ex:
        for src, res in ex.map(grab, sys.argv[1:]):
            print(f"{src:22} {res}", flush=True)
