"""Sarah's Pick reel editor. Only for clips we filmed, have the creator's written permission for, or got from the AliExpress Affiliate API (pipeline/ali_source.py).

python3 pipeline/edit.py IN.mp4 OUT.mp4 --hook "reading in bed just got prettier" [--cta "link in bio"] [--start 0 --end 0]

Output: 1080x1920 H.264/AAC, 30fps, Instagram Reels spec.
Edit recipe: trim, scale+crop to 9:16, gentle 1.00 -> 1.06 push-in over the clip, warm soft grade,
hook text top third for the first 3 s, CTA pill in the last 2.5 s, loudness normalized to -14 LUFS.
Text is drawn with libass (no emoji: libass cannot draw color emoji, keep emoji in the caption).
"""
import argparse, json, os, subprocess, tempfile

try:
    import imageio_ffmpeg
    FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    FFMPEG = "ffmpeg"

def duration(path):
    out = subprocess.run([FFMPEG, "-hide_banner", "-i", path], capture_output=True, text=True).stderr
    h, m, s = out.split("Duration: ")[1].split(",")[0].split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)

def ts(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def ass(hook, cta, dur, pos="low"):
    align, margin = (8, 360) if pos == "top" else (2, 720)  # "low" keeps clear of text creators burn in at the top
    return f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Hook,DejaVu Sans,64,&H00FFFFFF,&H00FFFFFF,&H00221E1A,&H64000000,1,0,0,0,100,100,0,0,1,4,2,{align},90,90,{margin},1
Style: Cta,DejaVu Sans,50,&H00222629,&H00222629,&H00F2F7FA,&H00F2F7FA,1,0,0,0,100,100,1,0,3,22,0,2,90,90,300,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,{ts(0.15)},{ts(min(3.2, dur))},Hook,,0,0,0,,{{\\fad(180,220)}}{hook}
Dialogue: 0,{ts(max(0, dur - 2.5))},{ts(dur)},Cta,,0,0,0,,{{\\fad(200,0)}}{cta}
"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp"); ap.add_argument("out")
    ap.add_argument("--hook", required=True)
    ap.add_argument("--cta", default="shop it, link in bio")
    ap.add_argument("--hook-pos", choices=["low", "top"], default="low")
    ap.add_argument("--start", type=float, default=0); ap.add_argument("--end", type=float, default=0)
    a = ap.parse_args()
    end = a.end or duration(a.inp)
    dur = end - a.start
    frames = max(1, int(dur * 30))
    with tempfile.TemporaryDirectory() as td:
        sub = os.path.join(td, "t.ass")
        open(sub, "w", encoding="utf-8").write(ass(a.hook, a.cta, dur, a.hook_pos))
        vf = (f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,"
              f"zoompan=z='1+0.06*on/{frames}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30,"
              f"eq=saturation=1.06:gamma=1.02,colorbalance=rm=0.02:bm=-0.02,"
              f"subtitles={sub}")
        cmd = [FFMPEG, "-y", "-v", "error", "-ss", str(a.start), "-t", str(dur), "-i", a.inp,
               "-vf", vf, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
               "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-profile:v", "high",
               "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-movflags", "+faststart", a.out]
        subprocess.run(cmd, check=True)
    print(json.dumps({"out": a.out, "seconds": round(dur, 2)}))

if __name__ == "__main__":
    main()
