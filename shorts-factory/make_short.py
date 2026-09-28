"""Render Shorts from script JSON files.

    python make_short.py scripts/mercedes_bounce.en.json
    python make_short.py scripts/*.json --out "C:/Users/hw487/Downloads"
    python make_short.py scripts/x.json --theme light --voice af_heart --speed 1.15
"""
import argparse
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from factory.config import OUTPUT, ROOT  # noqa: E402
from factory.render import Short  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scripts", nargs="+")
    ap.add_argument("--channel", default=os.path.join(ROOT, "channel.json"))
    ap.add_argument("--out", default=OUTPUT)
    ap.add_argument("--theme", choices=["dark", "light"])
    ap.add_argument("--voice")
    ap.add_argument("--speed", type=float)
    ap.add_argument("--name", help="output file name (without .mp4); only with a single script")
    args = ap.parse_args()
    paths = [p for s in args.scripts for p in (glob.glob(s) or [s])]
    for p in paths:
        short = Short(p, args.channel, theme=args.theme, voice=args.voice, speed=args.speed)
        out, tl = short.build(args.out, args.name if len(paths) == 1 else None)
        print(f"\n[done] {out}  ({tl['duration']}s, rendered in {tl['render_seconds']}s, "
              f"loudness {tl['loudness_lufs_peak'][0]:.1f} LUFS / peak {tl['loudness_lufs_peak'][1]:.1f} dBFS)")
        if tl["placeholders"]:
            print(f"[note] {tl['placeholders']} segment(s) used placeholder slates (footage not reachable)")
        for w in tl["warnings"]:
            print("[warn]", w)


if __name__ == "__main__":
    main()
