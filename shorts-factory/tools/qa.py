"""QA a rendered short: alignment summary + 2 fps contact sheet.   python tools/qa.py <id> [...]"""
import glob
import json
import subprocess
import sys

for sid in sys.argv[1:]:
    tl = json.load(open(f"work/{sid}/timeline.json", encoding="utf-8"))
    bad = [(i["lines"], i["matched"], i["heard"]) for i in tl["items"] if i["matched"].split("/")[0] != i["matched"].split("/")[1]]
    print(f"== {sid}: {tl['duration']}s  placeholders={tl['placeholders']}  warnings={tl['warnings']}")
    for b in bad:
        print("   partial match:", b)
    print("   sfx:", [(c["t"], c["id"]) for c in tl["sfx"]])
    mp4 = sorted(glob.glob(f"output/*_{sid}_EN.mp4"))[-1]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mp4, "-vf", "fps=2,scale=216:384,tile=12x6", "-frames:v", "1",
                    f"work/qa/final_{sid}.png"], check=True)
