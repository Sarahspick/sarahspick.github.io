"""Upload a finished Short to its channel with the YouTube Data API v3.

    python tools/upload_youtube.py scripts/amazon_drone.en.json               # private upload (default)
    python tools/upload_youtube.py scripts/amazon_drone.ko.json --public      # publish right away
    python tools/upload_youtube.py scripts/amazon_drone.en.json --dry-run     # print what would be sent
    python tools/upload_youtube.py scripts/amazon_drone.en.json --comment-on VIDEO_ID   # after making it public

The video is output/<date>_<id>_<LANG>.mp4 (newest). Title, description, tags come from the script's
"upload" block (the same text as <name>_text.txt); the "comment" is posted as the first comment (pin it in
the app: the API cannot pin). YouTube refuses comments on private videos, so a private upload skips the comment;
instead every upload first comments on the channel's earlier Shorts that are public by now and still have no
comment from the channel (the user's routine: upload A private -> user publishes A -> uploading B comments on A).
--catch-up does only that step. --comment-on posts one comment by hand. An upload whose title is already on the channel is refused
(use --force to upload again).

Credentials (environment variables, never in chat or git):
    YT_CLIENT_ID, YT_CLIENT_SECRET      OAuth client of the Google Cloud project
    YT_REFRESH_TOKEN_TT                  refresh token authorised as the Top Techs channel (English)
    YT_REFRESH_TOKEN_CC                  refresh token authorised as the 기발한 회사들 channel (Korean)
    (mapping in channel.json "youtube_token"; YT_REFRESH_TOKEN_RS belongs to another project, never used here)
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
API = "https://www.googleapis.com/youtube/v3"
COMMENT_URL = API + "/commentThreads"


def access_token(lang):
    var = json.load(open(os.path.join(ROOT, "channel.json"), encoding="utf-8")).get("youtube_token", {}).get(
        lang, f"YT_REFRESH_TOKEN_{lang.upper()}")
    rt = os.environ.get(var)
    cid, secret = os.environ.get("YT_CLIENT_ID"), os.environ.get("YT_CLIENT_SECRET")
    missing = [n for n, v in (("YT_CLIENT_ID", cid), ("YT_CLIENT_SECRET", secret),
                              (var, rt)) if not v]
    if missing:
        sys.exit(f"missing environment variables: {', '.join(missing)}")
    r = requests.post(TOKEN_URL, data={"client_id": cid, "client_secret": secret, "refresh_token": rt,
                                       "grant_type": "refresh_token"}, timeout=30)
    if r.status_code != 200:
        sys.exit(f"token refresh failed ({r.status_code}): {r.text[:300]}")
    return r.json()["access_token"]


def channel_uploads(tok):
    h = {"Authorization": f"Bearer {tok}"}
    ch = requests.get(API + "/channels", params={"part": "contentDetails", "mine": "true"}, headers=h, timeout=30).json()
    pl = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    r = requests.get(API + "/playlistItems", params={"part": "snippet", "playlistId": pl, "maxResults": 50},
                     headers=h, timeout=30).json()
    return {i["snippet"]["title"]: i["snippet"]["resourceId"]["videoId"] for i in r.get("items", [])}


def post_comment(tok, vid, text):
    c = requests.post(COMMENT_URL, params={"part": "snippet"}, headers={"Authorization": f"Bearer {tok}"},
                      json={"snippet": {"videoId": vid, "topLevelComment": {"snippet": {"textOriginal": text}}}},
                      timeout=60)
    print("comment posted" if c.status_code == 200
          else f"comment failed ({c.status_code}): {c.text[:200]}")


def comment_on_published(tok, lang):
    """Post each script's comment on its video once the user has made it public (matched by title)."""
    h = {"Authorization": f"Bearer {tok}"}
    me = requests.get(API + "/channels", params={"part": "contentDetails", "mine": "true"}, headers=h,
                      timeout=30).json()["items"][0]
    pl = me["contentDetails"]["relatedPlaylists"]["uploads"]
    items = requests.get(API + "/playlistItems", params={"part": "snippet,status", "playlistId": pl, "maxResults": 50},
                         headers=h, timeout=30).json().get("items", [])
    comments = {}  # video id (saved at upload) or title -> comment; the title match covers older uploads
    for path in glob.glob(os.path.join(ROOT, "scripts", f"*.{lang}.json")):
        up = json.load(open(path, encoding="utf-8")).get("upload", {})
        if up.get("comment"):
            for key in (up.get("video_id"), up.get("title", "")[:100]):
                if key:
                    comments[key] = up["comment"]
    for it in items:
        title, vid = it["snippet"]["title"], it["snippet"]["resourceId"]["videoId"]
        comment = comments.get(vid) or comments.get(title)
        if it["status"]["privacyStatus"] != "public" or not comment:
            continue
        r = requests.get(API + "/commentThreads", params={"part": "snippet", "videoId": vid, "maxResults": 100},
                         headers=h, timeout=30).json().get("items", [])
        if any(c["snippet"]["topLevelComment"]["snippet"].get("authorChannelId", {}).get("value") == me["id"]
               for c in r):
            continue
        print(f"published: {title}")
        post_comment(tok, vid, comment)


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
    ap.add_argument("--force", action="store_true", help="upload even if the title is already on the channel")
    ap.add_argument("--comment-on", metavar="VIDEO_ID", help="only post the script's comment on this (public) video")
    ap.add_argument("--catch-up", action="store_true", help="only comment on earlier Shorts that are public now")
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
    if a.comment_on:
        post_comment(tok, a.comment_on, sc["upload"]["comment"])
        return
    if not a.no_comment:
        comment_on_published(tok, lang)
    if a.catch_up:
        return
    existing = channel_uploads(tok).get(body["snippet"]["title"])
    if existing and not a.force:
        sys.exit(f"already on the channel: https://youtube.com/shorts/{existing} (--force to upload again)")
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
    sc["upload"]["video_id"] = vid  # lets a later upload find this video for its comment even if the title is edited
    json.dump(sc, open(a.script, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"uploaded {os.path.basename(video)} -> https://youtube.com/shorts/{vid} ({body['status']['privacyStatus']})")
    comment = sc["upload"].get("comment")
    if comment and not a.no_comment:
        if body["status"]["privacyStatus"] == "public":
            post_comment(tok, vid, comment)
        else:
            print("comment waits until you publish it (posted by the next upload, or --catch-up)")


if __name__ == "__main__":
    main()
