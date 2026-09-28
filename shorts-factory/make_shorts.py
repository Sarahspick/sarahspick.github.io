#!/usr/bin/env python3
"""야생CCTV shorts factory.

  python make_shorts.py build                 # catalog.py -> stories/json/*.json (needs metadata, ~1 GB cache)
  python make_shorts.py render                # json -> MP4s in ~/Downloads/야생CCTV
  python make_shorts.py render --only 1,5 --out ./out --workers 4
  python make_shorts.py preview 3             # 8-frame contact sheet for QA
  python make_shorts.py meta                  # upload titles / descriptions / pinned comments
  python make_shorts.py mine rare|events|fire|closeups <sp>|site <season> <site>|sheet <ids>
"""
import argparse
import csv
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
JSON_DIR = os.path.join(ROOT, "stories", "json")
DEFAULT_OUT = os.path.join(os.path.expanduser("~"), "Downloads", "야생CCTV")
CHANNEL = "야생CCTV"
HASHTAGS = ["#세렝게티", "#야생동물", "#무인카메라", "#동물", "#shorts"]


def story_files():
    return sorted(f for f in os.listdir(JSON_DIR) if f.endswith(".json"))


def load(n):
    f = [x for x in story_files() if x.startswith(f"{n:02d}_")][0]
    return json.load(open(os.path.join(JSON_DIR, f))), f[:-5]


# ------------------------------------------------------------------ build
def build():
    from factory import lila
    from stories.catalog import STORIES
    idx = lila.Index()
    cache = {}

    def shot(ref):
        if ref["cap"] not in cache:
            info = idx.capture(ref["cap"])
            sh = lila.shot_from_capture(info)
            # drop frames whose image is missing from the bucket (e.g. removed for privacy)
            keep = []
            for i, rel in enumerate(sh["frames"]):
                try:
                    lila.image(rel)
                    keep.append(i)
                except Exception:
                    pass
            sh["frames"] = [sh["frames"][i] for i in keep]
            sh["boxes"] = [sh["boxes"][i] for i in keep]
            sh["species"] = info["species"]
            cache[ref["cap"]] = sh
        return cache[ref["cap"]]

    def resolve(beat):
        b = dict(beat)
        if b.get("shot"):
            ref = b["shot"]
            b["shot"] = shot(ref)
            if ref.get("use") is not None:
                b["use"] = ref["use"]
            if ref.get("focus"):
                b["focus"] = ref["focus"]
        if b.get("items"):
            items = []
            for it in b["items"]:
                it = dict(it)
                ref = it["shot"]
                it["shot"] = shot(ref)
                if ref.get("use"):
                    it["frame"] = ref["use"][0]
                items.append(it)
            b["items"] = items
        return b

    os.makedirs(JSON_DIR, exist_ok=True)
    for n, st in enumerate(STORIES, 1):
        out = dict(st)
        out["id"] = f"{n:02d}"
        out["beats"] = [resolve(b) for b in st["beats"]]
        path = os.path.join(JSON_DIR, f"{n:02d}_{st['slug']}.json")
        json.dump(out, open(path, "w"), ensure_ascii=False, indent=1)
        print("built", path)


# ------------------------------------------------------------------ render
def file_title(st):
    t = " ".join(st["title"]).replace("{", "").replace("}", "")
    for ch in '\\/:*?"<>|':
        t = t.replace(ch, "")
    return t


def render_one(args):
    n, out_dir, work_root = args
    from factory import engine as E
    st, name = load(n)
    out = os.path.join(out_dir, f"{n:02d}_{file_title(st)}.mp4")
    t0 = time.time()
    r = E.Renderer(st, number=n, channel=CHANNEL)
    r.render(out, os.path.join(work_root, name))
    return out, r.total, time.time() - t0


def render(only, out_dir, workers):
    os.makedirs(out_dir, exist_ok=True)
    work_root = os.path.join(out_dir, ".work")
    nums = only or [int(f[:2]) for f in story_files()]
    jobs = [(n, out_dir, work_root) for n in nums]
    with ProcessPoolExecutor(workers) as ex:
        for out, dur, took in ex.map(render_one, jobs):
            print(f"done {os.path.basename(out)}  {dur:.1f}s video in {took:.0f}s")
    write_meta(out_dir)


def preview(n, out_path=None, times=None):
    from PIL import Image
    from factory import engine as E
    st, name = load(n)
    r = E.Renderer(st, number=n, channel=CHANNEL)
    if not times:
        times = [b.t0 + min(b.dur * 0.6, b.dur - 0.05) for b in r.beats]
    work = os.path.join(ROOT, ".preview", name)
    paths = r.render(None, work, preview_frames=times)
    cols = 6
    rows = (len(paths) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 270, rows * 480), (0, 0, 0))
    for i, p in enumerate(paths):
        sheet.paste(Image.open(p).resize((270, 480)), ((i % cols) * 270, (i // cols) * 480))
    out_path = out_path or os.path.join(ROOT, ".preview", f"{name}.jpg")
    sheet.save(out_path, quality=85)
    print(out_path, f"{r.total:.1f}s")
    return out_path


# ------------------------------------------------------------------ upload metadata
def first_shot(st):
    for b in st["beats"]:
        if b.get("shot") and b.get("kind", "shot") == "shot":
            return b["shot"]
    return None


def meta_rows():
    rows = []
    for f in story_files():
        st = json.load(open(os.path.join(JSON_DIR, f)))
        n = int(f[:2])
        sh = first_shot(st) or {}
        tags = [t if t.startswith("#") else "#" + t for t in st.get("tags", [])]
        desc = (f"{st['desc']}\n\n"
                f"📍 촬영 장소: 탄자니아 세렝게티 국립공원 (무인카메라 {sh.get('site', '')})\n"
                f"📅 촬영 일시: {sh.get('date', '')} {sh.get('time', '')}\n\n"
                "실제 무인카메라 사진을 편집해 만든 영상입니다. AI로 만든 장면은 없습니다.\n"
                "영상 출처: Snapshot Serengeti (Swanson 외, 2015, Scientific Data) · LILA BC 공개 데이터셋\n"
                "라이선스: Community Data License Agreement Permissive 1.0 (상업적 이용 및 수정 허용)\n"
                "음악과 효과음: 채널 자체 제작\n\n"
                + " ".join(tags + HASHTAGS))
        pin = (f"동물: {st.get('animal', '')}\n"
               f"장소: 탄자니아 세렝게티 국립공원 · 무인카메라 {sh.get('site', '')}\n\n"
               f"{st.get('pin', '')}\n"
               "밥 먹으면서 보기 좋은 야생 CCTV 사건파일을 매일 올립니다. 구독하면 다음 사건도 놓치지 않아요!")
        rows.append({"no": n, "file": f"{n:02d}_{file_title(st)}.mp4", "title": st["yt_title"][:100],
                     "description": desc, "pinned_comment": pin, "tags": ",".join(t.lstrip("#") for t in tags)})
    return rows


def write_meta(out_dir):
    rows = [r for r in meta_rows() if os.path.exists(os.path.join(out_dir, r["file"]))] or meta_rows()
    with open(os.path.join(out_dir, "업로드_정보.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(out_dir, "업로드_정보.md"), "w", encoding="utf-8") as f:
        f.write(f"# {CHANNEL} 업로드 정보 ({len(rows)}편)\n\n")
        for r in rows:
            f.write(f"## {r['no']:02d}. {r['title']}\n\n파일: `{r['file']}`\n\n**설명란**\n\n```\n{r['description']}\n```\n\n"
                    f"**고정 댓글**\n\n```\n{r['pinned_comment']}\n```\n\n")
    print("wrote upload info to", out_dir)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["build", "render", "preview", "meta", "mine"])
    ap.add_argument("rest", nargs="*")
    ap.add_argument("--only", default="")
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 0))
    a = ap.parse_args()
    if a.cmd == "build":
        build()
    elif a.cmd == "render":
        only = [int(x) for x in a.only.split(",") if x.strip()]
        render(only, a.out, a.workers)
    elif a.cmd == "preview":
        preview(int(a.rest[0]))
    elif a.cmd == "mine":
        from factory import mine
        mine.cli(a.rest)
    elif a.cmd == "meta":
        os.makedirs(a.out, exist_ok=True)
        write_meta(a.out)


if __name__ == "__main__":
    main()
