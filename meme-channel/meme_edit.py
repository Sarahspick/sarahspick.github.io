"""Aura Receipts short template, matching the benchmark format.

Layout (1080x1440, 3:4 like the benchmark): white caption bar on top,
clip below, small @handle watermark bottom right. Optional second clip
with the caption swapped to "My honest reaction:" (the punchline clip),
and optional pop text like "OH!" at a given time.

Only feed it clips you shot yourself or have written permission to use.

Example:
  python3 meme_edit.py main.mp4 "New fear unlocked 🙏😭" -o out.mp4 \
      --reaction reaction.mp4 --pop "OH!@2.5"
"""
import argparse
import os
import re
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
TEXT_FONT = os.path.join(HERE, "fonts", "RobotoCond.ttf")
EMOJI_FONT = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
W, H = 1080, 1440
HANDLE = "@AuraReceipts"

EMOJI_RE = re.compile("([\U0001F000-\U0001FAFF☀-➿⬀-⯿][️‍\U0001F3FB-\U0001F3FF]*)")


def runs(text):
    """Split a line into (is_emoji, str) runs."""
    return [(bool(EMOJI_RE.fullmatch(p)), p) for p in EMOJI_RE.split(text) if p]


def emoji_img(ch, size):
    f = ImageFont.truetype(EMOJI_FONT, 109)
    im = Image.new("RGBA", (160, 136), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((0, 0), ch, font=f, embedded_color=True)
    im = im.crop(im.getbbox())
    return im.resize((size, size), Image.LANCZOS)


def line_width(d, line, f, size):
    return sum(size if e else d.textlength(t, font=f) for e, t in runs(line))


def wrap(d, text, f, size, maxw):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for word in para.split(" "):
            test = (cur + " " + word).strip()
            if cur and line_width(d, test, f, size) > maxw:
                lines.append(cur)
                cur = word
            else:
                cur = test
        lines.append(cur)
    return lines


def caption_png(text, path, size=64):
    """White bar with centered bold caption; returns bar height."""
    f = ImageFont.truetype(TEXT_FONT, size)
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    lines = wrap(probe, text, f, size, W - 120)
    lh = int(size * 1.18)
    bar = max(200, len(lines) * lh + 80)
    im = Image.new("RGBA", (W, bar), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    y = (bar - len(lines) * lh) // 2
    for line in lines:
        x = (W - line_width(d, line, f, size)) / 2
        for is_emoji, t in runs(line):
            if is_emoji:
                im.alpha_composite(emoji_img(t, size), (int(x), y + int(size * 0.12)))
                x += size
            else:
                d.text((x, y), t, font=f, fill=(0, 0, 0))
                x += d.textlength(t, font=f)
        y += lh
    im.save(path)
    return bar


def pop_png(text, path, size=110):
    f = ImageFont.truetype(TEXT_FONT, size)
    d = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    w = int(d.textlength(text, font=f)) + 60
    im = Image.new("RGBA", (w, size + 50), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((30, 10), text, font=f, fill=(255, 255, 255), stroke_width=10, stroke_fill=(0, 0, 0))
    im.save(path)


def handle_png(path):
    f = ImageFont.truetype(TEXT_FONT, 34)
    im = Image.new("RGBA", (360, 50), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((0, 4), HANDLE, font=f, fill=(255, 255, 255, 120))
    im.save(path)


def has_audio(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
                          "-of", "csv=p=0", path], capture_output=True, text=True).stdout
    return bool(out.strip())


def segment(src, caption, dst, tmp, tag, pops=(), start=None, end=None):
    cap = os.path.join(tmp, f"cap_{tag}.png")
    bar = caption_png(caption, cap)
    hnd = os.path.join(tmp, "handle.png")
    handle_png(hnd)
    vh = H - bar
    inputs = []
    if start is not None:
        inputs += ["-ss", str(start)]
    if end is not None:
        inputs += ["-to", str(end)]
    inputs += ["-i", src, "-i", cap, "-i", hnd]
    fc = (f"[0:v]scale={W}:{vh}:force_original_aspect_ratio=increase,crop={W}:{vh},setsar=1,fps=30[v];"
          f"color=white:s={W}x{H}:r=30[bg];[bg][v]overlay=0:{bar}:shortest=1[a];"
          f"[a][1:v]overlay=0:0[b];[b][2:v]overlay=W-w-24:H-h-20[c0]")
    last = "c0"
    for i, (txt, t) in enumerate(pops):
        p = os.path.join(tmp, f"pop_{tag}_{i}.png")
        pop_png(txt, p)
        inputs += ["-i", p]
        idx = 3 + i
        fc += (f";[{last}][{idx}:v]overlay=(W-w)/2:{bar + vh // 3}:"
               f"enable='between(t,{t},{t + 0.8})'[c{i + 1}]")
        last = f"c{i + 1}"
    audio = ["-map", "0:a"] if has_audio(src) else []
    if not audio:
        inputs += ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo"]
        audio = ["-map", f"{3 + len(pops)}:a", "-shortest"]
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", fc, "-map", f"[{last}]", *audio,
                    "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-ar", "44100", "-ac", "2", dst], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("clip")
    ap.add_argument("caption")
    ap.add_argument("-o", "--out", default="out.mp4")
    ap.add_argument("--reaction", help="punchline clip shown under 'My honest reaction:'")
    ap.add_argument("--reaction-caption", default="My honest reaction:")
    ap.add_argument("--pop", action="append", default=[], help='pop text "OH!@2.5" (text@seconds)')
    ap.add_argument("--start", type=float)
    ap.add_argument("--end", type=float)
    a = ap.parse_args()
    pops = [(p.rsplit("@", 1)[0], float(p.rsplit("@", 1)[1])) for p in a.pop]
    with tempfile.TemporaryDirectory() as tmp:
        parts = [os.path.join(tmp, "p0.mp4")]
        segment(a.clip, a.caption, parts[0], tmp, "0", pops, a.start, a.end)
        if a.reaction:
            parts.append(os.path.join(tmp, "p1.mp4"))
            segment(a.reaction, a.reaction_caption, parts[1], tmp, "1")
        lst = os.path.join(tmp, "list.txt")
        with open(lst, "w") as f:
            f.writelines(f"file '{p}'\n" for p in parts)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst,
                        "-c", "copy", "-movflags", "+faststart", a.out], check=True)
    print(a.out)


if __name__ == "__main__":
    main()
