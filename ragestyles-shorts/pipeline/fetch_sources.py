"""Download the source footage, sound effects and models listed in sources/manifest.json.

Nothing in the manifest is committed (the repo is public), so a fresh session runs this first.

Usage (from ragestyles-shorts/):
  python3 pipeline/fetch_sources.py                 # core + sfx_mixkit (what the liked shorts need)
  python3 pipeline/fetch_sources.py commons models  # other groups
  python3 pipeline/fetch_sources.py --list          # show items and what is already on disk
  python3 pipeline/fetch_sources.py --derive        # also rebuild work/nasa/how_exercise_vocals.m4a with Demucs

upload.wikimedia.org answers 429 when hit too often: the script waits (default 240 s) between tries
instead of hammering it. Blocked hosts (403 from the egress proxy) are reported, never worked around.
"""
import argparse
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = "RageStylesShortsResearch/1.0 (https://github.com/Sarahspick/sarahspick.github.io; video licensing research)"
NASA_ID = "jsc2025m000002_How_Do_Astronauts_Exercise_in_Space_250106-MP4"


def have(item):
    p = os.path.join(ROOT, item["path"])
    if not os.path.exists(p):
        return False
    return os.path.getsize(p) == item["bytes"] if item.get("bytes") else os.path.getsize(p) > 0


def curl(url, out, resume=True):
    cmd = ["curl", "-s", "-L", "--fail-with-body", "--max-time", "3600", "-A", UA, "-w", "%{http_code}", "-o", out, url]
    if resume and os.path.exists(out):
        cmd[1:1] = ["-C", "-"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.stdout.strip()[-3:]


def fetch(item, wait, tries):
    out = os.path.join(ROOT, item["path"])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    part = out + ".part"
    slow = "wikimedia.org" in item["url"]
    for n in range(tries):
        code = curl(item["url"], part, resume=not slow)
        size = os.path.getsize(part) if os.path.exists(part) else 0
        ok = code in ("200", "206") and size > 0 and (not item.get("bytes") or size == item["bytes"])
        if ok:
            os.replace(part, out)
            print(f"  ok   {item['path']} ({size / 1e6:.1f} MB)", flush=True)
            if slow:
                time.sleep(45)
            return True
        if code == "416" and item.get("bytes") and size == item["bytes"]:
            os.replace(part, out)
            return True
        if code in ("403", "404", "000") and not slow:
            if os.path.exists(part):
                os.remove(part)
            print(f"  FAIL {item['path']}: HTTP {code} {item['url']}", flush=True)
            if code == "403":
                print("       403 usually means the environment's network policy blocks this host. Add it to the "
                      "allowlist (see HANDOFF.md) instead of working around it.", flush=True)
            return False
        if slow:
            if os.path.exists(part):
                os.remove(part)
            print(f"  wait {item['path']}: HTTP {code}, retry {n + 1}/{tries} in {wait} s", flush=True)
            time.sleep(wait)
        else:
            print(f"  retry {item['path']}: HTTP {code}", flush=True)
            time.sleep(5 * (n + 1))
    return False


def to_wav(item):
    src = os.path.join(ROOT, item["path"])
    dst = os.path.splitext(src)[0] + ".wav"
    if os.path.exists(dst) or not os.path.exists(src):
        return
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
                    "-ar", "48000", "-ac", "2", dst], check=True)


def derive_nasa_vocals():
    """Narration of the NASA exercise video without its music bed (used by c2_leg_day_in_space)."""
    out = os.path.join(ROOT, "work", "nasa", "how_exercise_vocals.m4a")
    if os.path.exists(out):
        return
    video = os.path.join(ROOT, "work", "nasa", NASA_ID + ".mp4")
    model_dir = os.path.join(ROOT, "work", "models", "demucs")
    if not (os.path.exists(video) and os.path.exists(os.path.join(model_dir, "htdemucs.th"))):
        print("  derive needs the core group and the models group first", flush=True)
        return
    tmp = os.path.join(ROOT, "work", "tmp_sep")
    os.makedirs(tmp, exist_ok=True)
    mix = os.path.join(tmp, "nasa_mix.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-vn", "-ar", "44100", "-ac", "2", mix], check=True)
    subprocess.run([sys.executable, "-m", "demucs", "--repo", model_dir, "-n", "htdemucs", "--two-stems", "vocals",
                    "-o", tmp, mix], check=True)
    vocals = os.path.join(tmp, "htdemucs", "nasa_mix", "vocals.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vocals, "-c:a", "aac", "-b:a", "256k", "-f", "mp4", out],
                   check=True)
    print("  ok   work/nasa/how_exercise_vocals.m4a", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("groups", nargs="*", default=["core", "sfx_mixkit"])
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--derive", action="store_true", help="rebuild derived files (Demucs vocals)")
    ap.add_argument("--wait", type=int, default=240, help="seconds between tries on rate limited hosts")
    ap.add_argument("--tries", type=int, default=12)
    a = ap.parse_args()
    man = json.load(open(os.path.join(ROOT, "sources", "manifest.json")))
    items = man["items"]
    if a.list:
        for it in items:
            mb = f"{it['bytes'] / 1e6:8.1f} MB" if it.get("bytes") else "         ?"
            print(f"{'[x]' if have(it) else '[ ]'} {it['group']:<13} {mb}  {it['path']}")
        return
    groups = set(a.groups)
    if a.derive:
        groups |= {"core", "models"}
    unknown = groups - set(man["groups"])
    if unknown:
        sys.exit(f"unknown group(s): {', '.join(sorted(unknown))}; choose from {', '.join(man['groups'])}")
    failed = []
    for it in items:
        if it["group"] not in groups:
            continue
        if not have(it):
            print(f"get  {it['path']}", flush=True)
            if not fetch(it, a.wait, a.tries):
                failed.append(it["path"])
                continue
        if it.get("convert_wav"):
            to_wav(it)
    if a.derive:
        derive_nasa_vocals()
    if failed:
        print("\nnot downloaded:\n  " + "\n  ".join(failed))
        sys.exit(1)
    print("all requested sources are in place")


if __name__ == "__main__":
    main()
