"""Find AliExpress products that come with an official product video, through the AliExpress Affiliate API.

The affiliate API hands these videos (product_video_url) to affiliates for promoting the product, so each
reel links to that same product with our AliExpress affiliate link, not to Amazon.

Needs environment secrets from portals.aliexpress.com + openservice.aliexpress.com (never commit them):
  ALI_APP_KEY, ALI_APP_SECRET, ALI_TRACKING_ID

python3 pipeline/ali_source.py --keywords "bedroom lamp" [--limit 10] [--download media/ali]
Prints a JSON list: id, title, price, sales, rating, video, link, image. --download saves each video as <id>.mp4.
"""
import argparse, hashlib, hmac, json, os, sys, time, urllib.parse, urllib.request

API = "https://api-sg.aliexpress.com/sync"
FIELDS = ("product_id,product_title,target_sale_price,target_original_price,lastest_volume,evaluate_rate,"
          "product_video_url,promotion_link,product_main_image_url,first_level_category_name")

def call(method, **biz):
    p = {"app_key": os.environ["ALI_APP_KEY"], "method": method, "sign_method": "sha256",
         "timestamp": str(int(time.time() * 1000)), **{k: str(v) for k, v in biz.items()}}
    base = "".join(k + p[k] for k in sorted(p))
    p["sign"] = hmac.new(os.environ["ALI_APP_SECRET"].encode(), base.encode(), hashlib.sha256).hexdigest().upper()
    with urllib.request.urlopen(API + "?" + urllib.parse.urlencode(p), timeout=60) as r:
        out = json.load(r)
    if "error_response" in out:
        sys.exit(f"AliExpress API error: {out['error_response']}")
    return next(iter(out.values()))["resp_result"]

def hot_products(keywords, limit):
    res = call("aliexpress.affiliate.hotproduct.query", keywords=keywords, fields=FIELDS, page_size=50,
               sort="LAST_VOLUME_DESC", target_currency="USD", target_language="EN", ship_to_country="US",
               tracking_id=os.environ["ALI_TRACKING_ID"])
    items = ((res.get("result") or {}).get("products") or {}).get("product") or []
    picks = []
    for it in items:
        if not it.get("product_video_url"):
            continue
        picks.append({"id": str(it["product_id"]), "title": it["product_title"], "price": it.get("target_sale_price"),
                      "sales": it.get("lastest_volume"), "rating": it.get("evaluate_rate"),
                      "category": it.get("first_level_category_name"), "video": it["product_video_url"],
                      "link": it.get("promotion_link"), "image": it.get("product_main_image_url")})
        if len(picks) >= limit:
            break
    return picks

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keywords", required=True); ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--download")
    a = ap.parse_args()
    picks = hot_products(a.keywords, a.limit)
    if a.download:
        os.makedirs(a.download, exist_ok=True)
        for p in picks:
            p["file"] = os.path.join(a.download, p["id"] + ".mp4")
            urllib.request.urlretrieve(p["video"], p["file"])
    print(json.dumps(picks, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main()
