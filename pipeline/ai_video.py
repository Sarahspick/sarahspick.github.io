"""Turn an official product photo into a short AI video clip (image-to-video) through Replicate.

The clip starts from the real product photo so the product looks like what the buyer gets. Keep prompts to camera
moves, light and mood; never ask the model to add features the product does not have. Mark the reel as AI made
when posting (Instagram "AI info" label).

Needs REPLICATE_API_TOKEN (environment secret, never commit it).

python3 pipeline/ai_video.py PHOTO.jpg OUT.mp4 --prompt "slow push in, cozy night bedroom, soft mist rising"
  [--model kwaivgi/kling-v2.1] [--image-field start_image] [--extra '{"duration": 5}'] [--dry-run]
The photo is center cropped to 9:16 (1080x1920) first, so the clip comes out vertical.
"""
import argparse, base64, io, json, os, sys, time, urllib.request
from PIL import Image

API = "https://api.replicate.com/v1"

def vertical(photo):
    im = Image.open(photo).convert("RGB")
    w, h = im.size
    if w / h > 9 / 16:
        nw = int(h * 9 / 16); im = im.crop(((w - nw) // 2, 0, (w + nw) // 2, h))
    else:
        nh = int(w * 16 / 9); im = im.crop((0, (h - nh) // 2, w, (h + nh) // 2))
    buf = io.BytesIO(); im.resize((1080, 1920), Image.LANCZOS).save(buf, "JPEG", quality=92)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

def req(url, body=None):
    r = urllib.request.Request(url, data=json.dumps(body).encode() if body else None, method="POST" if body else "GET",
                               headers={"Authorization": "Bearer " + os.environ["REPLICATE_API_TOKEN"],
                                        "Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=120) as f:
        return json.load(f)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("photo"); ap.add_argument("out"); ap.add_argument("--prompt", required=True)
    ap.add_argument("--model", default="kwaivgi/kling-v2.1"); ap.add_argument("--image-field", default="start_image")
    ap.add_argument("--extra", default="{}"); ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    inp = {"prompt": a.prompt, a.image_field: vertical(a.photo), **json.loads(a.extra)}
    if a.dry_run:
        print(json.dumps({"model": a.model, "input": {k: (v[:40] + "...") if isinstance(v, str) and len(v) > 80 else v
                                                      for k, v in inp.items()}}, indent=1)); return
    p = req(f"{API}/models/{a.model}/predictions", {"input": inp})
    while p["status"] not in ("succeeded", "failed", "canceled"):
        time.sleep(5); p = req(p["urls"]["get"])
    if p["status"] != "succeeded":
        sys.exit(f"Replicate {p['status']}: {p.get('error')}")
    url = p["output"][0] if isinstance(p["output"], list) else p["output"]
    urllib.request.urlretrieve(url, a.out)
    print(json.dumps({"out": a.out, "seconds": p.get("metrics", {}).get("predict_time")}))

if __name__ == "__main__":
    main()
