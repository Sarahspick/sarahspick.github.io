"""Upload a documentary and its Shorts to YouTube (private), via tools/upload_youtube.py.

    python tools/upload_doc.py documentaries/walmart_machine.json [--dry-run] [--only long|<short name>]

Writes one upload script per video next to the documentary (documentaries/<id>.<part>.json, lang + upload block,
so the comment routine finds them later) and fills the long video's description with its chapter timestamps."""
import argparse
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def part_file(doc, part, body):
    path = os.path.join(ROOT, "documentaries", "uploads", f"{doc['id']}.{part}.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path):                       # keep a saved video_id from an earlier upload
        old = json.load(open(path))
        if old.get("upload", {}).get("video_id"):
            body["upload"]["video_id"] = old["upload"]["video_id"]
    json.dump(body, open(path, "w"), ensure_ascii=False, indent=2)
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("doc")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only")
    a = ap.parse_args()
    doc = json.load(open(a.doc))
    out = os.path.join(ROOT, "output")
    jobs = []
    if a.only in (None, "long"):
        chapters = open(os.path.join(out, f"{doc['id']}_chapters.txt")).read().strip()
        up = dict(doc["upload"])
        up["description"] = up["description"].replace("{chapters}", "Chapters\n" + chapters)
        path = part_file(doc, "long", {"id": doc["id"], "lang": doc["lang"], "format": "long", "upload": up})
        extra = ["--captions", os.path.join(out, f"{doc['id']}.en.srt")]
        thumb = os.path.join(out, f"{doc['id']}_thumb.jpg")
        if os.path.exists(thumb):
            extra += ["--thumbnail", thumb]
        jobs.append((path, os.path.join(out, f"{doc['id']}.mp4"), extra))
    for name, cfg in doc.get("shorts", {}).items():
        if a.only not in (None, name):
            continue
        path = part_file(doc, "short_" + name, {"id": f"{doc['id']}_short_{name}", "lang": doc["lang"], "upload": cfg["upload"]})
        jobs.append((path, os.path.join(out, f"{doc['id']}_short_{name}.mp4"), []))
    for path, video, extra in jobs:
        cmd = [sys.executable, os.path.join(ROOT, "tools", "upload_youtube.py"), path, "--video", video] + extra
        if a.dry_run:
            cmd.append("--dry-run")
        print("$", " ".join(os.path.relpath(c, ROOT) if c.startswith(ROOT) else c for c in cmd[1:]), flush=True)
        subprocess.run(cmd, check=False)


if __name__ == "__main__":
    main()
