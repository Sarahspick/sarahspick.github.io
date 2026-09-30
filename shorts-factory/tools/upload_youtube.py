"""Upload a finished Short to its channel with the YouTube Data API v3.

    python tools/upload_youtube.py scripts/amazon_drone.en.json               # private upload (default)
    python tools/upload_youtube.py scripts/amazon_drone.ko.json --public      # publish right away
    python tools/upload_youtube.py scripts/amazon_drone.en.json --dry-run     # print what would be sent

The video is output/<date>_<id>_<LANG>.mp4 (newest). Title, description, tags come from the script's
"upload" block (the same text as <name>_text.txt); the "comment" is posted as the first comment (pin it in
the app: the API cannot pin).

Credentials (environment variables, never in chat or git):
    YT_CLIENT_ID, YT_CLIENT_SECRET      OAuth client of the Google Cloud project
    YT_REFRESH_TOKEN_EN                  refresh token authorised as the Top Techs channel
    YT_REFRESH_TOKEN_KO                  refresh token authorised as the 기발한 회사들 channel
Scopes when creating the refresh tokens: youtube.upload and youtube.force-ssl (for the comment).
"""
import argparse
import glob
import json
import os
import sys

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN_URL = "https://oauth2.googleapis.com/token"
UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos"
COMMENT_URL = "https://www.googleapis.com/youtube/v3/commentThreads"


def access_token(lang):
    rt = os.environ.get(f"YT_REFRESH_TOKEN_{lang.upper()}")
    cid, secret = os.environ.get("YT_CLIENT_ID"), os.environ.get("YT_CLIENT_SECRET")
    missing = [n for n, v in (("YT_CLIENT_ID", cid), ("YT_CLIENT_SECRET", secret),
                              (f"YT_REFRESH_TOKEN_{lang.upper()}", rt)) if not v]
    if missing:
        sys.exit(f"missing environment variables: {', '.join(missing)}")
    r = requests.post(TOKEN_URL, data={"client_id": cid, "client_secret": secret, "refresh_token": rt,
                                       "grant_type": "refresh_token"}, timeout=30)
    if r.status_code != 200:
        sys.exit(f"token refresh failed ({r.status_code}): {r.text[:300]}")
    return r.json()["access_token"]


def build_body(sc, public):
    up = sc["upload"]
    parts = [up["description"]]
    if sc.get("sources"):
        parts.append(("출처:" if sc["lang"] == "ko" else "Sources:") + "\n" +
                     "\n".join(f"- {s['name']}: {s['url']}" for s in sc["sources"]))
    if up.get("hashtags"):
        parts.append(" ".join(up["hashtags"]))
    tags, total = [], 0
    for t in up.get("tags", []):  # YouTube caps tags at 500 characters in total
        if total + len(t) + 2 > 480:
            break
        tags.append(t)
        total += len(t) + 2
    return {"snippet": {"title": up["title"][:100], "description": "\n\n".join(parts)[:4900], "tags": tags,
                        "categoryId": "28", "defaultLanguage": sc["lang"], "defaultAudioLanguage": sc["lang"]},
            "status": {"privacyStatus": "public" if public else "private", "selfDeclaredMadeForKids": False}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script")
    ap.add_argument("--video", help="mp4 path (default: newest output/*_<id>_<LANG>.mp4)")
    ap.add_argument("--public", action="store_true", help="publish instead of uploading as private")
    ap.add_argument("--no-comment", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    sc = json.load(open(a.script, encoding="utf-8"))
    lang = sc["lang"]
    video = a.video or sorted(glob.glob(os.path.join(ROOT, "output", f"*_{sc['id']}_{lang.upper()}.mp4")))[-1]
    body = build_body(sc, a.public)
    if a.dry_run:
        print(video)
        print(json.dumps(body, ensure_ascii=False, indent=1))
        return
    tok = access_token(lang)
    size = os.path.getsize(video)
    init = requests.post(UPLOAD_URL, params={"uploadType": "resumable", "part": "snippet,status"},
                         headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json",
                                  "X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(size)},
                         data=json.dumps(body), timeout=60)
    if init.status_code != 200:
        sys.exit(f"upload init failed ({init.status_code}): {init.text[:500]}")
    with open(video, "rb") as f:
        r = requests.put(init.headers["Location"], data=f,
                         headers={"Authorization": f"Bearer {tok}", "Content-Type": "video/mp4"}, timeout=1800)
    if r.status_code not in (200, 201):
        sys.exit(f"upload failed ({r.status_code}): {r.text[:500]}")
    vid = r.json()["id"]
    print(f"uploaded {os.path.basename(video)} -> https://youtube.com/shorts/{vid} ({body['status']['privacyStatus']})")
    comment = sc["upload"].get("comment")
    if comment and not a.no_comment:
        c = requests.post(COMMENT_URL, params={"part": "snippet"}, headers={"Authorization": f"Bearer {tok}"},
                          json={"snippet": {"videoId": vid, "topLevelComment": {"snippet": {"textOriginal": comment}}}},
                          timeout=60)
        print("comment posted (pin it in the YouTube app)" if c.status_code == 200
              else f"comment failed ({c.status_code}): {c.text[:200]}")


if __name__ == "__main__":
    main()
