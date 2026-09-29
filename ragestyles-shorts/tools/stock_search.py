"""Search and download modern stock footage from the Pexels and Pixabay APIs (free licenses, YouTube use OK).

Keys come from the environment: any variable whose name contains PEXELS or PIXABAY (e.g. PEXELS_API_KEY,
PIXABAY_API_KEY). Set them in the cloud environment settings; they are never printed or committed.

Usage (from ragestyles-shorts/):
  python3 tools/stock_search.py search "deadlift" "boxing training" [--provider pexels|pixabay|both] [--portrait]
  python3 tools/stock_search.py get pexels:1234567 pixabay:98765     # -> work/stock/<provider>_<id>.mp4
Every download is logged with author, page and license in work/stock/credits.json (credit is not required by
either license, but we keep it). Pixabay's CDN sometimes answers with a Cloudflare challenge page for
datacenter IPs: the script reports that and stops; it never tries to get around it.
"""
import argparse
import json
import os
import subprocess
import sys
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "work", "stock")
UA = "RageStylesShorts/1.0 (https://github.com/Sarahspick/sarahspick.github.io)"
LICENSES = {"pexels": "Pexels License (https://www.pexels.com/license/)",
            "pixabay": "Pixabay Content License (https://pixabay.com/service/license-summary/)"}


def key(provider):
    for k, v in os.environ.items():
        if provider.upper() in k.upper() and v.strip():
            return v.strip()
    sys.exit(f"no {provider} key: add an environment variable like {provider.upper()}_API_KEY in the environment settings")


def get_json(url, headers=()):
    cmd = ["curl", "-s", "--max-time", "40", "-A", UA, "-w", "\n%{http_code}"]
    for h in headers:
        cmd += ["-H", h]
    r = subprocess.run(cmd + [url], capture_output=True, text=True).stdout
    body, _, code = r.rpartition("\n")
    if code != "200":
        sys.exit(f"HTTP {code} from {url.split('?')[0]}: {body[:200]}")
    return json.loads(body)


def pexels(q, n, portrait):
    p = {"query": q, "per_page": n, "size": "medium"}
    if portrait:
        p["orientation"] = "portrait"
    d = get_json("https://api.pexels.com/videos/search?" + urllib.parse.urlencode(p), [f"Authorization: {key('pexels')}"])
    out = []
    for v in d.get("videos", []):
        files = sorted([f for f in v.get("video_files", []) if f.get("file_type") == "video/mp4" and f.get("height")],
                       key=lambda f: -(f["width"] * f["height"]))
        best = next((f for f in files if max(f["width"], f["height"]) <= 3840), files[0] if files else None)
        if best:
            out.append({"ref": f"pexels:{v['id']}", "dur": v.get("duration"), "w": best["width"], "h": best["height"],
                        "author": (v.get("user") or {}).get("name", ""), "page": v.get("url", ""), "file": best["link"]})
    return out


def pixabay(q, n, portrait):
    p = {"key": key("pixabay"), "q": q, "per_page": max(3, n), "safesearch": "true"}
    d = get_json("https://pixabay.com/api/videos/?" + urllib.parse.urlencode(p))
    out = []
    for v in d.get("hits", []):
        vids = v.get("videos", {})
        best = next((vids[s] for s in ("large", "medium", "small") if vids.get(s, {}).get("url")), None)
        if not best:
            continue
        if portrait and best.get("height", 0) < best.get("width", 1):
            continue
        out.append({"ref": f"pixabay:{v['id']}", "dur": v.get("duration"), "w": best.get("width"), "h": best.get("height"),
                    "author": v.get("user", ""), "page": v.get("pageURL", ""), "file": best["url"]})
    return out


def search(queries, provider, n, portrait):
    found = {}
    for q in queries:
        for prov in (["pexels", "pixabay"] if provider == "both" else [provider]):
            rows = (pexels if prov == "pexels" else pixabay)(q, n, portrait)
            print(f"== {prov} '{q}': {len(rows)}")
            for r in rows:
                found[r["ref"]] = dict(r, query=q)
                print(f"   {r['ref']:18s} {r['dur']:>4}s {r['w']}x{r['h']:<5} {r['author'][:22]:22s} {r['page']}")
    os.makedirs(OUT, exist_ok=True)
    cache = os.path.join(OUT, "last_search.json")
    old = json.load(open(cache)) if os.path.exists(cache) else {}
    old.update(found)
    json.dump(old, open(cache, "w"), indent=1)


def get(refs):
    cache = os.path.join(OUT, "last_search.json")
    found = json.load(open(cache)) if os.path.exists(cache) else {}
    credits_path = os.path.join(OUT, "credits.json")
    credits = json.load(open(credits_path)) if os.path.exists(credits_path) else {}
    for ref in refs:
        if ref not in found:
            print(f"  {ref}: run a search that lists it first")
            continue
        r = found[ref]
        prov, vid = ref.split(":")
        dst = os.path.join(OUT, f"{prov}_{vid}.mp4")
        code = subprocess.run(["curl", "-s", "-L", "--max-time", "900", "-A", UA, "-o", dst, "-w", "%{http_code}", r["file"]],
                              capture_output=True, text=True).stdout
        head = open(dst, "rb").read(512) if os.path.exists(dst) else b""
        if code != "200" or b"<html" in head.lower() or b"<!doctype" in head.lower():
            print(f"  FAIL {ref}: HTTP {code}" + (" (Cloudflare challenge page, not bypassing)" if b"Just a moment" in head else ""))
            if os.path.exists(dst):
                os.remove(dst)
            continue
        credits[ref] = {"file": os.path.relpath(dst, ROOT), "author": r["author"], "page": r["page"], "license": LICENSES[prov]}
        print(f"  ok   {ref} -> {os.path.relpath(dst, ROOT)} ({os.path.getsize(dst) / 1e6:.1f} MB)")
    json.dump(credits, open(credits_path, "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["search", "get"])
    ap.add_argument("items", nargs="+")
    ap.add_argument("--provider", default="both", choices=["pexels", "pixabay", "both"])
    ap.add_argument("-n", type=int, default=10)
    ap.add_argument("--portrait", action="store_true")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    search(a.items, a.provider, a.n, a.portrait) if a.cmd == "search" else get(a.items)
