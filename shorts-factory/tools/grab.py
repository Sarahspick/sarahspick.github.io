"""Parallel footage downloader.   python tools/grab.py bili:BVxxx dm:xyz ...
Saves work/sources/<platform>_<id>.mp4 (+ .info.json), the same names the renderer looks for."""
import concurrent.futures as cf
import os
import sys

import yt_dlp

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from factory.media import PLATFORMS, SOURCES  # noqa: E402


def grab(src):
    pre, _, vid = src.partition(":")
    key = f"{pre}_{vid}"
    if any(f.startswith(key + ".") and f.endswith(".mp4") for f in os.listdir(SOURCES)):
        return src, "cached"
    url = PLATFORMS[pre].format(vid)
    try:
        with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True, "skip_download": True}) as y:
            dur = y.extract_info(url, download=False).get("duration") or 0
        cap = 1080 if dur <= 600 else 720
        opts = {"outtmpl": os.path.join(SOURCES, key + ".%(ext)s"), "quiet": True, "no_warnings": True, "noprogress": True,
                "format": f"bv*[height<={cap}]+ba/b[height<={cap}]/b", "merge_output_format": "mp4",
                "writeinfojson": True, "socket_timeout": 30, "retries": 5, "fragment_retries": 5, "concurrent_fragment_downloads": 4}
        with yt_dlp.YoutubeDL(opts) as y:
            info = y.extract_info(url, download=True)
        return src, f"ok {info.get('width')}x{info.get('height')} {dur:.0f}s  {info.get('title', '')[:50]}"
    except Exception as e:
        return src, "FAIL " + str(e).splitlines()[0][:140]


if __name__ == "__main__":
    os.makedirs(SOURCES, exist_ok=True)
    with cf.ThreadPoolExecutor(4) as ex:
        for src, res in ex.map(grab, sys.argv[1:]):
            print(f"{src:22} {res}", flush=True)
