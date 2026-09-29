"""Check the license line on YouTube watch pages (metadata only, nothing is downloaded).

Usage: python3 tools/youtube_license_check.py VIDEO_ID [VIDEO_ID ...]
Prints CC-BY / standard / unknown (bot page) with title, channel, publish date and views.
"""
import json
import re
import subprocess
import sys
import time

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"


def check(vid):
    h = subprocess.run(["curl", "-s", "--max-time", "30", "-A", UA, "-H", "Accept-Language: en-US,en;q=0.9",
                        f"https://www.youtube.com/watch?v={vid}"], capture_output=True, text=True).stdout
    title = re.search(r'<meta name="title" content="([^"]*)"', h)
    chan = re.search(r'"ownerChannelName":"([^"]*)"', h)
    date = re.search(r'"publishDate":"([^"]*)"', h)
    views = re.search(r'"viewCount":"(\d+)"', h)
    if "Creative Commons Attribution license (reuse allowed)" in h or '"license":"Creative Commons' in h:
        lic = "CC-BY"
    elif title and chan:
        lic = "standard"
    else:
        lic = "unknown"
    return {"id": vid, "license": lic, "title": title.group(1) if title else "", "channel": chan.group(1) if chan else "",
            "date": date.group(1)[:10] if date else "", "views": int(views.group(1)) if views else None}


if __name__ == "__main__":
    for v in sys.argv[1:]:
        r = check(v)
        print(json.dumps(r, ensure_ascii=False))
        time.sleep(1.5)
