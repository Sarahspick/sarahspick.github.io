"""Render one vertical short from a public-domain film + ElevenLabs VO.

Pipeline: tighten VO gaps -> map shots to words -> decode each shot from the
source -> per-frame compose (Ken Burns, punch-in cuts, flash, captions,
event tracker, hook arrow) with Pillow -> synthesize SFX + beat -> mux.
Usage: python3 render.py [--preview]
"""
import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

HERE = os.environ.get("SHORT_DIR", os.path.dirname(os.path.abspath(__file__)))
SCR = os.environ.get("SHORTS_WORK", os.path.join(HERE, "work"))  # src/ and fonts/ live here
SRC = os.path.join(SCR, "src", "army480.mpeg")
FONT = os.path.join(SCR, "fonts", "Anton.ttf")
FONT2 = os.path.join(SCR, "fonts", "Mont900.ttf")
OUT = os.path.join(HERE, "out")
W, H, FPS = 1080, 1920, 30
SR = 44100
TEMPO = 1.06            # final VO speed-up
GAP_MAX = 0.16          # max silence kept between phrases (pre-tempo)
PREVIEW = "--preview" in sys.argv
HOOK_ARROW = False     # static ring misses moving subjects; off by default
YEL = (255, 212, 0)
RED = (235, 40, 40)

# footage window
FX, FY, FW, FH = 0, 510, 1080, 1100

# ---------------------------------------------------------------- VO + timing
def ffdecode(path):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "f32le",
                          "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()

words = json.load(open(os.path.join(HERE, "words.json")))
vo = ffdecode(os.path.join(HERE, "vo.mp3"))

# group words into phrases split by long gaps, then close up the gaps
pieces, new_words, t_out = [], [], 0.0
start = max(0.0, words[0][1] - 0.03)
grp = [words[0]]
def flush(grp, t_out):
    a = max(0.0, grp[0][1] - 0.03); b = grp[-1][2] + 0.06
    pieces.append(vo[int(a * SR):int(b * SR)])
    for w, s, e in grp:
        new_words.append([w, t_out + (s - a), t_out + (e - a)])
    return t_out + (b - a) + GAP_MAX
for prev, cur in zip(words, words[1:]):
    if cur[1] - prev[2] > GAP_MAX + 0.09:
        t_out = flush(grp, t_out); grp = []
    grp.append(cur)
t_out = flush(grp, t_out)
gap = np.zeros(int(GAP_MAX * SR), np.float32)
vo2 = np.concatenate([np.concatenate([p, gap]) for p in pieces])
# tempo via ffmpeg atempo (pitch preserved)
tmp_in, tmp_out = os.path.join(OUT, "vo_tight.f32"), os.path.join(OUT, "vo_fast.f32")
os.makedirs(OUT, exist_ok=True)
vo2.tofile(tmp_in)
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", tmp_in,
                "-af", f"atempo={TEMPO}", "-f", "f32le", tmp_out], check=True)
vo3 = np.fromfile(tmp_out, dtype=np.float32)
for w in new_words:
    w[1] /= TEMPO; w[2] /= TEMPO
LEAD = 0.0
DUR = len(vo3) / SR + 0.9
NF = int(DUR * FPS)
print(f"VO {len(vo3)/SR:.2f}s, video {DUR:.2f}s, {NF} frames")

def wt(i):
    return new_words[i][1]
def find(word, after=0):
    for i in range(after, len(new_words)):
        if new_words[i][0].strip(".,?!") == word:
            return i
    raise KeyError(word)

# ---------------------------------------------------------------- shot list
# (anchor word, occurrence-after-anchor, src seconds, crop center x (0..1), zoom dir)
i_no1 = find("No"); i_no2 = find("No", i_no1 + 1)
i_just = find("Just"); i_every = find("every"); i_ev1 = find("Event")
i_ev2 = find("Event", i_ev1 + 1); i_score = find("score")
i_ev3 = find("Event", i_ev2 + 1); i_ev4 = find("Event", i_ev3 + 1)
i_ev5 = find("event", i_ev4 + 1); i_five = find("Five", i_ev5 + 1)
i_pass = find("Pass", i_five); i_obs = find("Obstacles"); i_slide = find("Slide")
i_so = find("So")
i_fitness = find("fitness")
SHOTS = [
    (0,          1112.3, 0.40, "in"),   # hook: log close-up
    (i_no1,      360.4,  0.55, "in"),   # no machines: burpee chaos
    (i_no2,      390.2,  0.50, "in"),   # no protein shakes: instructor yelling
    (i_just,     1105.6, 0.45, "out"),  # just this: log line
    (find("lifted"), 1103.9, 0.30, "in"),  # log close-up 2
    (i_every,    395.3,  0.50, "in"),   # every recruit: mass formation
    (i_fitness,  400.5,  0.50, "in"),   # push-up grid
    (i_ev1,      572.0,  0.45, "in"),   # low crawl
    (i_ev2,      589.2,  0.40, "in"),   # horizontal ladder
    (i_score,    978.5,  0.50, "out"),  # ladder 2
    (i_ev3,      603.0,  0.40, "in"),   # dodge run jump
    (i_ev4,      610.6,  0.40, "in"),   # man carry
    (i_ev5,      626.0,  0.35, "in"),   # mile run
    (i_five,     391.4,  0.50, "in"),   # 500 points: instructor
    (i_pass,     1219.0, 0.55, "in"),   # confidence course
    (i_obs,      1230.2, 0.50, "out"),  # wall rope
    (i_slide,    1346.5, 0.62, "in"),   # slide for life
    (i_so,       1108.0, 0.40, "in"),   # loop back to log
]
shot_times = [0.0] + [max(0.0, wt(s[0]) - 0.06) for s in SHOTS[1:]] + [DUR]

# event tracker state: (time, lit count, label)
EVENTS = [(wt(i_every) - 0.05, 0, "5 EVENTS. 500 POINTS."),
          (wt(i_ev1), 1, "40 YARD LOW CRAWL"),
          (wt(i_ev2), 2, "HORIZONTAL LADDER"),
          (wt(i_ev3), 3, "DODGE, RUN & JUMP"),
          (wt(i_ev4), 4, "150 YARD MAN CARRY"),
          (wt(i_ev5), 5, "1 MILE RUN"),
          (wt(i_pass), 5, "CONFIDENCE COURSE"),
          (wt(i_so), 5, "COULD YOU PASS?")]
FLASHES = [wt(i) - 0.04 for i in (i_just, i_ev1, i_pass)]
STAMP = (wt(i_five), wt(i_pass) - 0.1)   # "500/500" stamp window

# ---------------------------------------------------------------- captions
KEY = {"1967,", "1967", "gym.", "log,", "five", "one.", "two.", "three.", "four.", "five.",
       "forty", "minute.", "hundred", "fifty", "mile", "perfect", "Tough", "One,", "Tarzan,",
       "Slide", "Life.", "pass", "Fast.", "machines.", "shakes.", "squad.", "crawl,", "ladder."}
chunks, cur = [], []
for i, (w, s, e) in enumerate(new_words):
    cur.append(i)
    if w[-1] in ".,?!" or len(cur) == 3 or len(" ".join(new_words[j][0] for j in cur)) > 14:
        chunks.append(cur); cur = []
if cur: chunks.append(cur)
cap_spans = []
for k, c in enumerate(chunks):
    s = new_words[c[0]][1]
    e = new_words[chunks[k + 1][0]][1] if k + 1 < len(chunks) else DUR
    e = min(e, new_words[c[-1]][2] + 0.6)
    cap_spans.append((s, e, c))

f_cap = ImageFont.truetype(FONT, 118)
f_title = ImageFont.truetype(FONT, 108)
f_small = ImageFont.truetype(FONT2, 34)
f_ev = ImageFont.truetype(FONT, 50)
f_stamp = ImageFont.truetype(FONT, 230)

def text_img(txt, font, fill, stroke=10, stroke_fill=(0, 0, 0)):
    bb = font.getbbox(txt, stroke_width=stroke)
    im = Image.new("RGBA", (bb[2] - bb[0] + 8, bb[3] - bb[1] + 8), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((4 - bb[0], 4 - bb[1]), txt, font=font, fill=fill,
                            stroke_width=stroke, stroke_fill=stroke_fill)
    return im

cap_cache = {}
def caption_img(c, t):
    """Render chunk; the word being spoken is yellow, key words stay yellow."""
    active = max([j for j in c if new_words[j][1] <= t + 0.02] or [c[0]])
    key = (tuple(c), active)
    if key in cap_cache: return cap_cache[key]
    parts = []
    for j in c:
        w = new_words[j][0].upper()
        col = YEL if (j == active or new_words[j][0] in KEY) else (255, 255, 255)
        parts.append(text_img(w, f_cap, col, 11))
    gapx = 26
    wsum = sum(p.width for p in parts) + gapx * (len(parts) - 1)
    lines = [parts]
    if wsum > 1000:
        lines = [parts[:len(parts) // 2 + (len(parts) % 2)], parts[len(parts) // 2 + (len(parts) % 2):]]
    lw = [sum(p.width for p in l) + gapx * (len(l) - 1) for l in lines]
    lh = max(p.height for p in parts)
    im = Image.new("RGBA", (max(lw), lh * len(lines) - 10 * (len(lines) - 1)), (0, 0, 0, 0))
    y = 0
    for l, wl in zip(lines, lw):
        x = (im.width - wl) // 2
        for p in l:
            im.alpha_composite(p, (x, y)); x += p.width + gapx
        y += lh - 10
    cap_cache[key] = im
    return im

# ---------------------------------------------------------------- static layers
bg = Image.new("RGB", (W, H), (12, 12, 12))
d = ImageDraw.Draw(bg)
for y in range(H):   # subtle vertical gradient
    v = int(12 + 10 * (1 - abs(y - H / 2) / (H / 2)))
    d.line([(0, y), (W, y)], fill=(v, v, v))
# title
t1 = text_img("THE 1967 ARMY", f_title, (255, 255, 255), 0)
t2 = text_img("FITNESS TEST", f_title, YEL, 0)
title_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
title_layer.alpha_composite(t1, ((W - t1.width) // 2, 105))
title_layer.alpha_composite(t2, ((W - t2.width) // 2, 105 + t1.height - 4))
tag = text_img("REAL 1967 U.S. ARMY FOOTAGE", f_small, (170, 170, 170), 0)
title_layer.alpha_composite(tag, ((W - tag.width) // 2, 1630))

# vignette for footage
vy, vx = np.mgrid[0:FH, 0:FW]
r = np.sqrt(((vx - FW / 2) / (FW / 2)) ** 2 + ((vy - FH / 2) / (FH / 2)) ** 2)
vig = np.clip((r - 0.75) * 0.9, 0, 0.55)
vig_img = Image.fromarray((vig * 255).astype(np.uint8), "L")
vig_layer = Image.new("RGBA", (FW, FH), (0, 0, 0, 255)); vig_layer.putalpha(vig_img)

def arrow_layer():
    """Red hook arrow + ring (reference channel style)."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
    cx, cy, rr = 185, FY + 330, 175
    dr.ellipse([cx - rr, cy - rr * 0.7, cx + rr, cy + rr * 0.7], outline=RED, width=16)
    # arrow from lower-right to ring
    tip = (cx + rr * 0.85, cy - rr * 0.45)
    tail = (tip[0] + 260, tip[1] - 230)
    dr.line([tail, (tip[0] + 45, tip[1] - 40)], fill=RED, width=46)
    ang = math.atan2(tail[1] - tip[1], tail[0] - tip[0])
    L = 120
    p1 = (tip[0] + L * math.cos(ang + 0.5), tip[1] + L * math.sin(ang + 0.5))
    p2 = (tip[0] + L * math.cos(ang - 0.5), tip[1] + L * math.sin(ang - 0.5))
    dr.polygon([tip, p1, p2], fill=RED)
    return im
ARROW = arrow_layer()

def tracker(lit, label, age):
    im = Image.new("RGBA", (W, 130), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
    n, bw, gp = 5, 150, 16
    x0 = (W - (n * bw + (n - 1) * gp)) // 2
    for k in range(n):
        on = k < lit
        pop = on and k == lit - 1 and age < 0.25
        g = 6 if pop else 0
        box = [x0 + k * (bw + gp) - g, 8 - g, x0 + k * (bw + gp) + bw + g, 30 + g]
        dr.rounded_rectangle(box, 10, fill=YEL if on else (55, 55, 55))
    lab = text_img(label, f_ev, (255, 255, 255), 0)
    im.alpha_composite(lab, ((W - lab.width) // 2, 50))
    return im

# ---------------------------------------------------------------- decode shots
def decode(src_t, dur):
    n = int(math.ceil(dur * FPS)) + 2
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", f"{src_t:.3f}", "-i", SRC,
                          "-frames:v", str(n), "-vf", "yadif,scale=960:720,setsar=1,fps=30",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, 720, 960, 3)
    return fr

def ease(x): return 1 - (1 - min(max(x, 0), 1)) ** 3

# ---------------------------------------------------------------- render
cmd = ["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
       "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
       "-pix_fmt", "yuv420p", os.path.join(OUT, "video_noaudio.mp4")]
enc = None if PREVIEW else subprocess.Popen(cmd, stdin=subprocess.PIPE)
preview_times = [0.0, 0.5, 1.5, 3.0, 6.0, 9.0, 12.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0]
fi = 0
cut_times = shot_times[1:-1]
for si, shot in enumerate(SHOTS):
    t0, t1 = shot_times[si], shot_times[si + 1]
    f0, f1 = int(round(t0 * FPS)), int(round(t1 * FPS))
    if si == len(SHOTS) - 1: f1 = NF
    need = [f for f in range(f0, f1) if not PREVIEW or any(abs(f / FPS - p) < 0.5 / FPS for p in preview_times)]
    if not need: continue
    frames = decode(shot[1], (f1 - f0) / FPS)
    cxn, zdir = shot[2], shot[3]
    for f in need:
        t = f / FPS; lt = t - t0; prog = (f - f0) / max(1, f1 - f0)
        src = Image.fromarray(frames[min(f - f0, len(frames) - 1)])
        # Ken Burns + punch-in on cut
        z = 1.0 + (0.10 * prog if zdir == "in" else 0.10 * (1 - prog))
        z *= 1.0 + 0.12 * (1 - ease(lt / 0.22))
        ch = 720 / z; cw = ch * FW / FH
        cx = cxn * 960
        x0 = min(max(cx - cw / 2, 0), 960 - cw); y0 = (720 - ch) / 2
        foot = src.resize((FW, FH), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))
        foot = ImageEnhance.Contrast(foot).enhance(1.12)
        foot = ImageEnhance.Color(foot).enhance(1.18)
        frame = bg.copy()
        frame.paste(foot, (FX, FY))
        frame = frame.convert("RGBA")
        frame.alpha_composite(vig_layer, (FX, FY))
        frame.alpha_composite(title_layer)
        # hook arrow for first 2.2s
        if HOOK_ARROW and t < 2.2:
            a = ARROW.copy()
            if t > 1.9: a.putalpha(a.getchannel("A").point(lambda v: int(v * (2.2 - t) / 0.3)))
            frame.alpha_composite(a)
        # event tracker
        ev = [e for e in EVENTS if e[0] <= t]
        if ev:
            e = ev[-1]
            frame.alpha_composite(tracker(e[1], e[2], t - e[0]), (0, FY - 128))
        # 500 stamp
        if STAMP[0] <= t < STAMP[1]:
            st = text_img("500/500", f_stamp, YEL, 14)
            sc = 1.6 - 0.6 * ease((t - STAMP[0]) / 0.18)
            st = st.resize((int(st.width * sc), int(st.height * sc)), Image.BICUBIC).rotate(8, expand=True, resample=Image.BICUBIC)
            frame.alpha_composite(st, ((W - st.width) // 2, FY + 120 - (st.height - 300) // 2))
        # caption
        for s, e, c in cap_spans:
            if s <= t < e:
                ci = caption_img(c, t)
                sc = 0.82 + 0.18 * ease((t - s) / 0.09)
                if sc < 0.999:
                    ci = ci.resize((max(1, int(ci.width * sc)), max(1, int(ci.height * sc))), Image.BILINEAR)
                frame.alpha_composite(ci, ((W - ci.width) // 2, 1240 - ci.height // 2))
                break
        # white flash on section changes
        for ft in FLASHES:
            if 0 <= t - ft < 0.12:
                a = int(200 * (1 - (t - ft) / 0.12))
                frame.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, a)))
        out = frame.convert("RGB")
        if PREVIEW:
            out.resize((360, 640)).save(os.path.join(OUT, f"prev_{t:05.1f}.jpg"))
        else:
            enc.stdin.write(out.tobytes())
    print(f"shot {si} {shot[1]} done ({t0:.2f}-{t1:.2f})", flush=True)
if PREVIEW: sys.exit(0)
enc.stdin.close(); enc.wait()

# ---------------------------------------------------------------- audio
rng = np.random.default_rng(7)
N = int(DUR * SR)
mix = np.zeros(N, np.float32)
def add(sig, t, gain):
    i = int(t * SR)
    if i >= N: return
    seg = sig[:N - i]
    mix[i:i + len(seg)] += seg * gain

def onepole_sweep(x, f_start, f_end):
    y = np.zeros_like(x); s = 0.0
    fc = np.geomspace(f_start, f_end, len(x))
    a = np.exp(-2 * np.pi * fc / SR)
    for k in range(len(x)):
        s = a[k] * s + (1 - a[k]) * x[k]; y[k] = s
    return y

def whoosh(d=0.32):
    n = int(d * SR); x = rng.standard_normal(n).astype(np.float32)
    lp = onepole_sweep(x, 400, 6000); hp = lp - onepole_sweep(lp, 150, 150)
    env = np.sin(np.linspace(0, np.pi, n)) ** 2
    return (hp * env / (np.abs(hp).max() + 1e-6)).astype(np.float32)

def boom(d=0.9):
    n = int(d * SR); tt = np.arange(n) / SR
    f = 38 + 60 * np.exp(-tt * 18)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-tt * 4.5)
    click = rng.standard_normal(n) * np.exp(-tt * 90) * 0.5
    return (s + click).astype(np.float32)

def ding(freq=1318.5, d=0.5):
    tt = np.arange(int(d * SR)) / SR
    s = (np.sin(2 * np.pi * freq * tt) + 0.4 * np.sin(2 * np.pi * freq * 2.01 * tt)) * np.exp(-tt * 9)
    return s.astype(np.float32)

def riser(d=1.2):
    n = int(d * SR); x = rng.standard_normal(n).astype(np.float32)
    y = onepole_sweep(x, 200, 9000); env = np.linspace(0, 1, n) ** 2
    return (y * env / (np.abs(y).max() + 1e-6)).astype(np.float32)

# beat: 96 BPM, kick + dark bass + hats
bpm = 96; beat = 60 / bpm
def kick():
    tt = np.arange(int(0.35 * SR)) / SR
    f = 45 + 110 * np.exp(-tt * 30)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 9)).astype(np.float32)
def hat():
    tt = np.arange(int(0.06 * SR)) / SR
    x = rng.standard_normal(len(tt)); x = x - onepole_sweep(x.astype(np.float32), 5000, 5000)
    return (x * np.exp(-tt * 60)).astype(np.float32)
def bass(freq, d):
    tt = np.arange(int(d * SR)) / SR
    saw = 2 * ((tt * freq) % 1) - 1
    s = onepole_sweep(saw.astype(np.float32), 300, 300)
    env = np.minimum(1, tt / 0.02) * np.exp(-tt * 1.5)
    return (s * env).astype(np.float32)
K, HT = kick(), hat()
notes = [55.0, 43.65, 65.41, 49.0]   # A1 F1 C2 G1
music = np.zeros(N, np.float32)
nb = int(DUR / beat) + 1
start_beat = 0
for b in range(nb):
    t = b * beat
    i = int(t * SR)
    if i >= N: break
    seg = K[:N - i]; music[i:i + len(seg)] += seg * (0.9 if b % 2 == 0 else 0.6)
    for off in (0, 0.5):
        j = int((t + off * beat) * SR)
        if j < N: hs = HT[:N - j]; music[j:j + len(hs)] += hs * 0.25
    if b % 4 == 0:
        bs = bass(notes[(b // 4) % 4], beat * 4)[:N - i]; music[i:i + len(bs)] += bs * 0.5
music /= np.abs(music).max() + 1e-6
# drop the beat out briefly for the stamp, fade out at the end
tt = np.arange(N) / SR
duck = np.ones(N, np.float32)
duck[(tt > STAMP[0] - 0.05) & (tt < STAMP[0] + 0.6)] = 0.25
fade = np.clip((DUR - tt) / 0.8, 0, 1)
mix += music * 0.13 * duck * fade

vo_start = int(LEAD * SR)
mix[vo_start:vo_start + len(vo3)] += vo3[:N - vo_start] * 1.0
add(boom(), 0.0, 0.55)
W_ = whoosh()
for ct in cut_times:
    add(W_, max(0, ct - 0.12), 0.20)
for e in EVENTS[1:6]:
    add(ding(), e[0], 0.22)
add(boom(), STAMP[0], 0.6)
add(ding(1760), STAMP[0] + 0.05, 0.25)
add(riser(), max(0, wt(i_so) - 1.1), 0.12)
add(boom(), wt(i_so), 0.35)
peak = np.abs(mix).max()
mix = np.tanh(mix / peak * 1.4) * 0.89
wav = os.path.join(OUT, "mix.f32")
mix.astype(np.float32).tofile(wav)
final = os.path.join(OUT, "RageStyles_short_01_1967_army_test.mp4")
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", os.path.join(OUT, "video_noaudio.mp4"),
                "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", wav,
                "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ac", "2",
                "-af", "loudnorm=I=-14:TP=-1.0:LRA=9", "-ar", "48000", "-shortest", "-movflags", "+faststart", final], check=True)
json.dump({"words": new_words, "shots": SHOTS, "duration": DUR}, open(os.path.join(OUT, "timeline.json"), "w"), indent=1)
print("wrote", final)
