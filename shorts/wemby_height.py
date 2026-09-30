"""Wemby Shorts test #1: "Wemby is not normal" height/wingspan/DPOY explainer.

Everything on screen is original graphics or openly licensed photos (CC BY 4.0 / public domain,
Wikimedia Commons, credited in CREDITS). No broadcast footage.

python3 shorts/wemby_height.py WORKDIR OUT.mp4
WORKDIR needs: vo.mp3 + words.json (ElevenLabs with-timestamps), img/ (Commons photos), fonts/Anton.ttf, fonts/Inter.ttf
Output: 1080x1920 H.264/AAC 30fps, loudness -14 LUFS.
"""
import json, math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

try:
    import imageio_ffmpeg
    FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    FFMPEG = "ffmpeg"

W, H, FPS = 1080, 1920, 30
SPEED = 1.08  # voiceover tempo; every timestamp below is in original VO seconds and gets divided by this
BG = (11, 13, 16)
GREEN = (124, 255, 107)
SILVER = (196, 204, 212)
WHITE = (255, 255, 255)

CREDITS = {
    "portrait": ("img/Victor_Wembanyama_San_Antonio_Spurs_2024.jpg", "Photo: Frenchieinportland, CC BY 4.0"),
    "cup": ("img/Victor_Wembanyama_San_Antonio_Spurs_2025.jpg", "Photo: Daiei Onoguchi, CC BY 4.0"),
    "finals": ("img/Wembanyama_and_Hart_2026_NBA_Finals.jpg", "Photo: The White House, public domain"),
}

# scene boundaries (original VO seconds)
S_HOOK, S_CHART, S_WEMBY, S_WING, S_DPOY, S_CTA = 0.0, 3.0, 9.2, 11.4, 16.8, 23.3
REVEAL = {"man": 4.63, "nba": 7.69, "wemby": 10.34, "wing": 13.11, "bed": 15.27,
          "dpoy": 17.9, "young": 18.38, "unan": 19.78}


def T(t):
    return t / SPEED


def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def pop(t, t0, dur=0.25):
    """0 -> 1 with a small overshoot, for text/card entrances."""
    x = (t - t0) / dur
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    return 1 + 0.12 * math.sin(x * math.pi) - (1 - x) ** 3


class Fonts:
    def __init__(self, d):
        self.cache, self.d = {}, d

    def __call__(self, name, size):
        k = (name, size)
        if k not in self.cache:
            self.cache[k] = ImageFont.truetype(os.path.join(self.d, "fonts", name + ".ttf"), size)
        return self.cache[k]


def cover(img, w, h, zoom=1.0, cx=0.5, cy=0.5):
    s = max(w / img.width, h / img.height) * zoom
    im = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.LANCZOS)
    x = int((im.width - w) * cx)
    y = int((im.height - h) * cy)
    return im.crop((x, y, x + w, y + h))


def text_c(d, xy, s, font, fill, stroke=0, stroke_fill=(0, 0, 0), anchor="mm"):
    d.text(xy, s, font=font, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill, anchor=anchor)


def vignette():
    """Mask: 255 keeps the frame in the middle, fading toward black at the edges."""
    w, h = 108, 192
    v = Image.new("L", (w, h))
    v.putdata([int(255 * max(0.0, min(1.0, 1.25 - 0.9 * math.hypot((x - w / 2) / (w / 2), (y - h / 2) / (h / 2)))))
               for y in range(h) for x in range(w)])
    return v.resize((W, H), Image.BICUBIC)


def person(d, x, ground, h_px, color, width_scale=1.0):
    """Simple standing silhouette of height h_px with feet on `ground`."""
    if h_px < 60:
        return
    head_r = h_px * 0.062
    top = ground - h_px
    d.ellipse([x - head_r, top, x + head_r, top + head_r * 2], fill=color)
    neck = top + head_r * 2 + h_px * 0.01
    sh = h_px * 0.125 * width_scale  # half shoulder width
    hip = neck + h_px * 0.36
    d.rounded_rectangle([x - sh, neck, x + sh, hip], radius=int(sh * 0.45), fill=color)
    arm = sh * 0.28
    d.rounded_rectangle([x - sh - arm * 1.2, neck + 6, x - sh - arm * 0.1, hip + h_px * 0.08], radius=int(arm), fill=color)
    d.rounded_rectangle([x + sh + arm * 0.1, neck + 6, x + sh + arm * 1.2, hip + h_px * 0.08], radius=int(arm), fill=color)
    leg = sh * 0.46
    d.rounded_rectangle([x - sh + 4, hip - 10, x - sh + 4 + leg * 1.9, ground], radius=int(leg * 0.6), fill=color)
    d.rounded_rectangle([x + sh - 4 - leg * 1.9, hip - 10, x + sh - 4, ground], radius=int(leg * 0.6), fill=color)


def main():
    work, out = sys.argv[1], sys.argv[2]
    F = Fonts(work)
    words = json.load(open(os.path.join(work, "words.json")))
    vo_len = words[-1][2]
    total = T(vo_len) + 1.0
    n = int(total * FPS)

    photos = {k: Image.open(os.path.join(work, p)).convert("RGB") for k, (p, _) in CREDITS.items()}
    face = cover(photos["portrait"], 420, 420, zoom=1.0, cx=0.5, cy=0.12)
    mask = Image.new("L", face.size, 0)
    ImageDraw.Draw(mask).ellipse([0, 0, face.width, face.height], fill=255)
    face = face.resize((150, 150), Image.LANCZOS)
    mask = mask.resize((150, 150), Image.LANCZOS)
    vig = vignette()
    cup_bg = cover(photos["cup"], W, H, zoom=1.05, cx=0.5, cy=0.3).filter(ImageFilter.GaussianBlur(18))
    cup_bg = Image.blend(cup_bg, Image.new("RGB", (W, H), BG), 0.72)

    # word groups for captions: up to 3 words, break after punctuation
    groups, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) == 3 or w[0][-1] in ".?,":
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)

    # chart geometry: inches -> px
    ground, px_in = 1180, 7.4
    def hy(inches):
        return ground - inches * px_in

    proc = subprocess.Popen([FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                             "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                             "-crf", "18", "-pix_fmt", "yuv420p", os.path.join(work, "_video.mp4")], stdin=subprocess.PIPE)

    for i in range(n):
        t = i / FPS
        ot = t * SPEED  # original VO time
        shake = 0
        frame = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(frame)
        credit = None

        if ot < S_CHART or ot >= S_CTA:
            # hook / CTA: face photo, slow push in
            local = ot if ot < S_CHART else ot - S_CTA
            z = 1.0 + 0.04 * local
            frame.paste(cover(photos["portrait"], W, H, zoom=z, cx=0.5, cy=0.2), (0, 0))
            frame = Image.composite(frame, Image.new("RGB", (W, H), (0, 0, 0)), vig)
            d = ImageDraw.Draw(frame)
            credit = CREDITS["portrait"][1]
            if ot < S_CHART:
                p1, p2 = pop(ot, 0.1), pop(ot, 1.3)
                if p1:
                    text_c(d, (W // 2, 330), "WEMBY IS", F("Anton", int(130 * p1)), WHITE, 8)
                if p2:
                    text_c(d, (W // 2, 490), "NOT NORMAL", F("Anton", int(170 * p2)), GREEN, 10)
            else:
                p = pop(ot, S_CTA + 0.1)
                if p:
                    text_c(d, (W // 2, 360), "FOLLOW FOR", F("Anton", int(120 * p)), WHITE, 8)
                    text_c(d, (W // 2, 510), "DAILY WEMBY", F("Anton", int(160 * p)), GREEN, 10)

        elif ot < S_WING:
            # height chart
            for ft in range(4, 9):
                y = hy(ft * 12)
                d.line([110, y, W - 70, y], fill=(40, 46, 54), width=2)
                text_c(d, (70, y), f"{ft}'", F("Inter", 34), (110, 120, 130))
            d.line([90, ground, W - 60, ground], fill=SILVER, width=4)
            text_c(d, (W // 2, 150), "HOW TALL IS WEMBY?", F("Anton", 92), WHITE, 6)
            specs = [("AVG MAN", "5'9\"", 69, 270, REVEAL["man"], (120, 128, 138)),
                     ("AVG NBA", "6'6\"", 78, 540, REVEAL["nba"], (160, 168, 178)),
                     ("WEMBY", "7'4\"", 88, 810, REVEAL["wemby"], GREEN)]
            for label, hs, inches, x, t0, col in specs:
                g = ease((ot - (t0 - 0.35)) / 0.55)
                if g <= 0:
                    continue
                h_px = inches * px_in * g
                person(d, x, ground, h_px, col, 1.0 if label != "WEMBY" else 0.92)
                if label == "WEMBY" and g > 0.2:
                    fx, fy = x - 75, int(ground - h_px - 150 - 20)
                    frame.paste(face, (fx, fy), mask)
                    d.ellipse([fx - 3, fy - 3, fx + 153, fy + 153], outline=GREEN, width=6)
                p = pop(ot, t0)
                if p:
                    text_c(d, (x, ground - h_px - (215 if label == "WEMBY" else 55)), hs, F("Anton", int(78 * p)), col if label == "WEMBY" else WHITE, 5)
                    text_c(d, (x, ground + 50), label, F("Inter", 36), col if label == "WEMBY" else SILVER)
            if REVEAL["wemby"] <= ot < REVEAL["wemby"] + 0.35:
                shake = int(14 * (1 - (ot - REVEAL["wemby"]) / 0.35))

        elif ot < S_DPOY:
            # wingspan vs king bed
            frame.paste(cup_bg, (0, 0))
            d = ImageDraw.Draw(frame)
            credit = CREDITS["cup"][1]
            text_c(d, (W // 2, 230), "WINGSPAN", F("Anton", 120), WHITE, 7)
            px_ft = 110
            x0 = (W - 8 * px_ft) // 2
            g = ease((ot - (REVEAL["wing"] - 0.5)) / 0.6)
            if g > 0:
                y = 620
                x1 = x0 + int(8 * px_ft * g)
                d.rounded_rectangle([x0, y - 34, x1, y + 34], radius=34, fill=GREEN)
                p = pop(ot, REVEAL["wing"])
                if p:
                    text_c(d, (W // 2, y - 120), "8'0\"", F("Anton", int(150 * p)), GREEN, 8)
            gb = ease((ot - (REVEAL["bed"] - 0.4)) / 0.5)
            if gb > 0:
                y = 900
                x1 = x0 + int(80 / 12 * px_ft * gb)
                d.rounded_rectangle([x0, y - 34, x1, y + 34], radius=34, fill=(120, 128, 138))
                p = pop(ot, REVEAL["bed"])
                if p:
                    text_c(d, (x0, y + 90), "KING SIZE BED  6'8\"", F("Inter", int(44 * p)), SILVER, anchor="lm")
            if REVEAL["wing"] <= ot < REVEAL["wing"] + 0.3:
                shake = int(10 * (1 - (ot - REVEAL["wing"]) / 0.3))

        else:
            # DPOY
            local = ot - S_DPOY
            frame.paste(cover(photos["finals"], W, H, zoom=1.0 + 0.03 * local, cx=0.33, cy=0.4), (0, 0))
            frame = Image.composite(frame, Image.new("RGB", (W, H), (0, 0, 0)), vig)
            frame = Image.blend(frame, Image.new("RGB", (W, H), BG), 0.35)
            d = ImageDraw.Draw(frame)
            credit = CREDITS["finals"][1]
            cards = [("DEFENSIVE PLAYER", "OF THE YEAR", REVEAL["dpoy"], WHITE),
                     ("YOUNGEST", "EVER", REVEAL["young"], GREEN),
                     ("FIRST", "UNANIMOUS", REVEAL["unan"], GREEN)]
            for k, (a, b, t0, col) in enumerate(cards):
                p = pop(ot, t0)
                if not p:
                    continue
                cy = 300 + k * 250
                wbox = int(820 * p)
                d.rounded_rectangle([W // 2 - wbox // 2, cy - 100, W // 2 + wbox // 2, cy + 100], radius=28,
                                    fill=(12, 14, 18), outline=col, width=5)
                if p > 0.6:
                    text_c(d, (W // 2, cy - 38), a, F("Anton", 68), col)
                    text_c(d, (W // 2, cy + 42), b, F("Anton", 68), col)
            if ot > REVEAL["unan"] + 0.6:
                text_c(d, (W // 2, 1060), "2025-26  |  3.1 BLK/G  |  #1 IN BLOCKS 3 YEARS STRAIGHT",
                       F("Inter", 30), SILVER, 3)

        # captions: current 1-3 word group, spoken word highlighted
        for grp in groups:
            if T(grp[0][1]) - 0.05 <= t < T(grp[-1][2]) + 0.25:
                font = F("Inter", 76)
                parts = [w.upper() for w, _, _ in grp]
                widths = [d.textlength(p + " ", font=font) for p in parts]
                x = W // 2 - sum(widths) // 2
                for (w, s, e), wd in zip(grp, widths):
                    col = GREEN if T(s) <= t < T(e) + 0.05 else WHITE
                    d.text((x, 1330), w.upper(), font=font, fill=col, stroke_width=7, stroke_fill=(0, 0, 0), anchor="lm")
                    x += wd
                break

        if credit:
            # top left: the bottom of a Short is covered by the title/channel overlay
            d.text((40, 60), credit, font=F("Inter", 24), fill=(200, 200, 200), stroke_width=2, stroke_fill=(0, 0, 0), anchor="ls")

        if shake:
            dx = shake if i % 2 else -shake
            frame = frame.transform(frame.size, Image.AFFINE, (1, 0, dx, 0, 1, -dx // 2), fillcolor=BG)

        # short flash on scene cuts
        for cut in (S_CHART, S_WING, S_DPOY, S_CTA):
            if 0 <= ot - cut < 0.12:
                frame = Image.blend(frame, Image.new("RGB", (W, H), WHITE), 0.35 * (1 - (ot - cut) / 0.12))

        proc.stdin.write(frame.tobytes())
    proc.stdin.close()
    proc.wait()

    # audio: sped-up VO + synthesized boom on reveals + whoosh on cuts, normalized to -14 LUFS
    booms = [T(REVEAL[k]) for k in ("man", "nba", "wemby", "wing")]
    whooshes = [max(0, T(c) - 0.15) for c in (S_CHART, S_WING, S_DPOY, S_CTA)]
    inputs = ["-i", os.path.join(work, "_video.mp4"), "-i", os.path.join(work, "vo.mp3"),
              "-f", "lavfi", "-t", "0.7", "-i", "aevalsrc='0.9*sin(2*PI*t*(55+60*exp(-8*t)))*exp(-5*t)':s=44100",
              "-f", "lavfi", "-t", "0.35", "-i", "anoisesrc=d=0.35:c=pink:a=0.5,afade=t=in:d=0.2,afade=t=out:st=0.2:d=0.15,highpass=f=800"]
    fc = [f"[1:a]atempo={SPEED},aresample=44100[vo]"]
    fc.append(f"[2:a]asplit={len(booms)}" + "".join(f"[b{k}]" for k in range(len(booms))))
    fc.append(f"[3:a]asplit={len(whooshes)}" + "".join(f"[w{k}]" for k in range(len(whooshes))))
    mix = ["[vo]"]
    for k, bt in enumerate(booms):
        fc.append(f"[b{k}]volume=0.55,adelay={int(bt * 1000)}|{int(bt * 1000)}[bd{k}]")
        mix.append(f"[bd{k}]")
    for k, wt in enumerate(whooshes):
        fc.append(f"[w{k}]volume=0.35,adelay={int(wt * 1000)}|{int(wt * 1000)}[wd{k}]")
        mix.append(f"[wd{k}]")
    fc.append("".join(mix) + f"amix=inputs={len(mix)}:duration=first:normalize=0,apad,atrim=0:{total:.3f},loudnorm=I=-14:TP=-1.5:LRA=11[a]")
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(fc),
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
                    "-shortest", "-movflags", "+faststart", out], check=True)
    os.remove(os.path.join(work, "_video.mp4"))
    print("wrote", out, f"{total:.1f}s")


if __name__ == "__main__":
    main()
