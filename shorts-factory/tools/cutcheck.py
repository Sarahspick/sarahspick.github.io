"""Find source-shot cuts at the edges of every clip window used in a render, and optionally fix them.

A clip that starts a few frames before a cut in the source shows a flash of the previous shot; one that
runs a few frames past a cut flashes the next shot. This reads work/<id>/timeline.json (so run it after a
render), scene-detects the source around each window, and with --fix moves the clip's "start" to the
nearest position whose edges are clean (middle cuts inside the source's own editing are fine).

    python tools/cutcheck.py mercedes_bounce kfc_recipe        # report
    python tools/cutcheck.py --fix scripts/*.json               # fix scripts in place (then re-render)
"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from factory.media import fetch  # noqa: E402

HEAD = 0.7   # output seconds at the start of a window that must not contain a cut
TAIL = 0.45  # output seconds at the end of a window that must not contain a cut
SEARCH = 3.0  # how far (source seconds) a start may move


def scene_cuts(path, start, dur, thr=0.3):
    start = max(0.0, start)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-ss", f"{start:.3f}", "-t", f"{dur:.3f}", "-i", path, "-an",
                        "-vf", f"scale=320:-2,select='gt(scene\\,{thr})',showinfo", "-f", "null", "-"],
                       capture_output=True, text=True)
    return [start + float(x) for x in re.findall(r"pts_time:([0-9.]+)", r.stderr)]


def bad_edges(cuts, s, length, speed):
    head, tail = HEAD * speed, TAIL * speed
    return [c for c in cuts if s < c < s + min(head, length / 2) or s + max(length - tail, length / 2) < c < s + length]


def cuts_inside(cuts, s, length):
    return sum(1 for c in cuts if s < c < s + length)


def check(script_path, fix=False):
    """Windows come from the CURRENT script (clip starts) + the last render's segment durations."""
    sc = json.load(open(script_path, encoding="utf-8"))
    sid = sc["id"]
    tl_path = f"work/{sid}/timeline.json"
    if not os.path.exists(tl_path):
        print(f"== {sid}: no timeline (render first)")
        return 0
    tl = json.load(open(tl_path, encoding="utf-8"))
    issues, changed, consumed = 0, False, {}
    print(f"== {sid}")
    for seg in tl["segments"]:
        cid = seg["clip"]
        spec = sc["clips"].get(cid)
        if spec is None:
            print(f"   {cid}: not in script any more (re-render first)")
            issues += 1
            continue
        dur = seg["t1"] - seg["t0"]
        off = consumed.get(cid, 0.0) if spec.get("continue", True) else 0.0
        consumed[cid] = off + dur
        kind = spec.get("kind") or ("card" if "headline" in spec else "video")
        if kind != "video":
            continue
        speed = float(spec.get("speed", 1.0))
        s0 = float(spec.get("start", 0))
        s = s0 + off * speed
        length = dur * speed
        path = fetch(spec["src"])
        cuts = scene_cuts(path, s - SEARCH, length + 2 * SEARCH)
        bad = bad_edges(cuts, s, length, speed)
        if not bad:
            continue
        issues += 1
        rel = ", ".join(f"{(c - s) / speed:+.2f}s" for c in bad)
        if off > 0:
            print(f"   {cid:16} (continued) cut at {rel} of a {dur:.2f}s window; set \"continue\": false or use another clip")
            continue
        cands = []
        k = -int(SEARCH / 0.05)
        while k <= int(SEARCH / 0.05):
            cand = s + k * 0.05
            if cand >= 0 and not bad_edges(cuts, cand, length, speed):
                cands.append((cuts_inside(cuts, cand, length), abs(k), cand))
            k += 1
        if not cands:
            print(f"   {cid:16} cut at {rel}: no clean window within +/-{SEARCH}s (shot too short for {dur:.2f}s; try speed < 1)")
            continue
        n_in, _, best = min(cands)
        print(f"   {cid:16} cut at {rel}: start {s0} -> {round(best, 2)}  ({n_in} cut(s) left inside)")
        if fix:
            spec["start"] = round(best, 2)
            changed = True
    if changed:
        json.dump(sc, open(script_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print("   script updated")
    if not issues:
        print("   clean")
    return issues


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--fix"]
    fix = "--fix" in sys.argv
    total = 0
    for a in args:
        path = a if a.endswith(".json") else f"scripts/{a}.en.json"
        total += check(path, fix)
    print(f"\n{total} window(s) with edge cuts")
