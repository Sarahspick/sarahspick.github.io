"""Contact sheet of a source video with timestamps.   python tools/sheet.py bili:BVxxx [start] [dur] [every_s] [cols]"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from factory.media import fetch, probe  # noqa: E402

src = sys.argv[1]
start = float(sys.argv[2]) if len(sys.argv) > 2 else 0
p = next((os.path.join("work/sources", f) for f in os.listdir("work/sources") if f.startswith(src.replace(":", "_") + ".") and f.endswith(".mp4")), None)
if not p:
    sys.exit(f"{src} not downloaded yet")
w, h, dur = probe(p)
d = float(sys.argv[3]) if len(sys.argv) > 3 else dur - start
every = float(sys.argv[4]) if len(sys.argv) > 4 else max(1.0, d / 48)
cols = int(sys.argv[5]) if len(sys.argv) > 5 else 8
tw = 320 if w >= h else 160
th = int(tw * h / w) // 2 * 2
n = int(d / every) + 1
rows = (n + cols - 1) // cols
out = f"work/sheets/{src.replace(':', '_')}_{int(start)}.png"
os.makedirs("work/sheets", exist_ok=True)
font = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
# select (not fps) so each tile's label is the exact timestamp of the frame shown
vf = (f"select='isnan(prev_selected_t)+gte(t-prev_selected_t\\,{every})',scale={tw}:{th},"
      f"drawtext=fontfile={font}:text='%{{eif\\:t+{start}\\:d}}.%{{eif\\:mod((t+{start})*10\\,10)\\:d}}':"
      f"x=3:y=3:fontsize=15:fontcolor=yellow:box=1:boxcolor=black@0.6,tile={cols}x{rows}")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(start), "-t", str(d), "-i", p, "-vf", vf, "-fps_mode", "vfr", "-frames:v", "1", out], check=True)
print(out, f"{w}x{h} {dur:.1f}s every {every:.1f}s")
