"""Publish a finished reel to Instagram through the official Instagram Graph API (Content Publishing).

Needs two environment secrets (set in the Claude Code environment settings, never commit them):
  IG_USER_ID       numeric Instagram professional account id
  IG_ACCESS_TOKEN  long-lived token with instagram_basic, instagram_content_publish,
                   instagram_manage_comments, pages_show_list, pages_read_engagement

The video must be reachable at a public HTTPS URL (we commit it under media/ so GitHub Pages serves it).

python3 pipeline/publish_ig.py --video-url https://sarahspick.github.io/media/x.mp4 --caption-file cap.txt [--comment-file pin.txt]
Prints the media id. The comment is posted as the first comment; Instagram's API cannot pin it, so pinning stays one tap in the app.
"""
import argparse, json, os, sys, time, urllib.parse, urllib.request

API = "https://graph.facebook.com/v21.0"

def call(method, path, **params):
    params["access_token"] = os.environ["IG_ACCESS_TOKEN"]
    data = urllib.parse.urlencode(params).encode()
    url = f"{API}/{path}"
    req = urllib.request.Request(url if method == "POST" else url + "?" + data.decode(), data=data if method == "POST" else None, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"Graph API error on {path}: {e.read().decode()}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video-url", required=True); ap.add_argument("--caption-file", required=True)
    ap.add_argument("--comment-file"); ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    caption = open(a.caption_file, encoding="utf-8").read().strip()
    if caption.count("#") > 5:
        sys.exit("Instagram allows at most 5 hashtags")
    if a.dry_run:
        print(json.dumps({"would_publish": a.video_url, "caption_chars": len(caption)})); return
    uid = os.environ["IG_USER_ID"]
    c = call("POST", f"{uid}/media", media_type="REELS", video_url=a.video_url, caption=caption, share_to_feed="true")
    cid = c["id"]
    for _ in range(60):  # Instagram fetches and transcodes the video, usually under 2 minutes
        st = call("GET", cid, fields="status_code,status")
        if st.get("status_code") == "FINISHED": break
        if st.get("status_code") == "ERROR": sys.exit(f"Instagram could not process the video: {st}")
        time.sleep(10)
    else:
        sys.exit("Timed out waiting for Instagram to process the video")
    media = call("POST", f"{uid}/media_publish", creation_id=cid)["id"]
    if a.comment_file:
        call("POST", f"{media}/comments", message=open(a.comment_file, encoding="utf-8").read().strip())
    print(json.dumps({"media_id": media}))

if __name__ == "__main__":
    main()
