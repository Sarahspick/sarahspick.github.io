"""Voice sample reel: the same short sample read by every English and Korean voice, one numbered part per voice
on real footage (same layout, captions and SFX as a finished Short), joined into one video to pick a narrator by ear.

    python tools/voice_samples.py                         # ElevenLabs candidates -> output/<date>_voice_samples_elevenlabs_EN_KO.mp4
    python tools/voice_samples.py --lang ko               # Korean voices only
    python tools/voice_samples.py --engine edge --only Brian SunHi --rate +10%
    python tools/voice_samples.py --model eleven_multilingual_v2 --speed 1.0
    python tools/voice_samples.py --engine typecast --lang ko   # Typecast (key in TYPECAST_API_KEY)

ElevenLabs responses are cached under work/elevenlabs_cache, so re-rendering the reel costs no credits.
"""
import argparse
import datetime
import json
import os
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from factory import gfx  # noqa: E402
from factory.config import FPS, H, OUTPUT, SR, W, WORK  # noqa: E402
from factory.render import Short  # noqa: E402

# (edge voice, on-screen name, on-screen description)
EDGE_VOICES = {
    "en": [
        ("en-US-BrianMultilingualNeural", "Brian", "남성 · 미국 · *지금 영상에 쓰는 목소리*"),
        ("en-US-AndrewMultilingualNeural", "Andrew", "남성 · 미국 · 따뜻하고 자신감 있는"),
        ("en-US-ChristopherNeural", "Christopher", "남성 · 미국 · 뉴스·다큐 톤"),
        ("en-US-GuyNeural", "Guy", "남성 · 미국 · 열정적인"),
        ("en-US-EricNeural", "Eric", "남성 · 미국 · 차분하고 이성적인"),
        ("en-US-RogerNeural", "Roger", "남성 · 미국 · 활기찬"),
        ("en-US-SteffanNeural", "Steffan", "남성 · 미국 · 담백한 설명"),
        ("en-US-AvaMultilingualNeural", "Ava", "여성 · 미국 · 표현력 풍부"),
        ("en-US-EmmaMultilingualNeural", "Emma", "여성 · 미국 · 밝고 또렷한"),
        ("en-US-AriaNeural", "Aria", "여성 · 미국 · 자신감 있는 뉴스 톤"),
        ("en-US-JennyNeural", "Jenny", "여성 · 미국 · 친근한"),
        ("en-US-MichelleNeural", "Michelle", "여성 · 미국 · 부드러운"),
        ("en-GB-RyanNeural", "Ryan", "남성 · 영국 억양"),
        ("en-GB-ThomasNeural", "Thomas", "남성 · 영국 억양"),
        ("en-GB-SoniaNeural", "Sonia", "여성 · 영국 억양"),
        ("en-GB-LibbyNeural", "Libby", "여성 · 영국 억양"),
        ("en-AU-WilliamMultilingualNeural", "William", "남성 · 호주 억양"),
        ("en-AU-NatashaNeural", "Natasha", "여성 · 호주 억양"),
        ("en-CA-LiamNeural", "Liam", "남성 · 캐나다 억양"),
        ("en-CA-ClaraNeural", "Clara", "여성 · 캐나다 억양"),
    ],
    "ko": [
        ("ko-KR-HyunsuMultilingualNeural", "현수 Hyunsu", "남성 · 한국어 원어민"),
        ("ko-KR-InJoonNeural", "인준 InJoon", "남성 · 한국어 원어민"),
        ("ko-KR-SunHiNeural", "선희 SunHi", "여성 · 한국어 원어민"),
        ("en-US-BrianMultilingualNeural", "Brian", "남성 · 다국어 · *영어판과 같은 목소리*"),
        ("en-US-AndrewMultilingualNeural", "Andrew", "남성 · 다국어 (원래 영어)"),
        ("en-US-AvaMultilingualNeural", "Ava", "여성 · 다국어 (원래 영어)"),
        ("en-US-EmmaMultilingualNeural", "Emma", "여성 · 다국어 (원래 영어)"),
        ("en-AU-WilliamMultilingualNeural", "William", "남성 · 다국어 (원래 호주 영어)"),
        ("de-DE-FlorianMultilingualNeural", "Florian", "남성 · 다국어 (원래 독일어)"),
        ("de-DE-SeraphinaMultilingualNeural", "Seraphina", "여성 · 다국어 (원래 독일어)"),
        ("fr-FR-RemyMultilingualNeural", "Remy", "남성 · 다국어 (원래 프랑스어)"),
        ("fr-FR-VivienneMultilingualNeural", "Vivienne", "여성 · 다국어 (원래 프랑스어)"),
        ("it-IT-GiuseppeMultilingualNeural", "Giuseppe", "남성 · 다국어 (원래 이탈리아어)"),
        ("pt-BR-ThalitaMultilingualNeural", "Thalita", "여성 · 다국어 (원래 포르투갈어)"),
    ],
}

# (voice id, on-screen name, on-screen description). Library voices work through the API without adding them to
# My Voices. English: warm, confident male narrators in the spirit of Edge "Andrew". Korean: native speakers only.
ELEVEN_VOICES = {
    "en": [
        ("gUABw7pXQjhjt0kNFBTF", "Andrew", "남성 · 미국 · 부드럽고 똑똑한 해설"),
        ("MFZUKuGQUsGJPQjTS4wC", "Jon", "남성 · 미국 · 따뜻하고 안정감 있는 이야기꾼"),
        ("ZthjuvLPty3kTMaNKVKb", "Peter", "남성 · 미국 · 자신감 있는 내레이션"),
        ("uju3wxzG5OhpWcoi3SMy", "Michael", "남성 · 미국 · 자신감 있고 표현력 풍부"),
        ("Dslrhjl3ZpzrctukrQSN", "Brad", "남성 · 미국 · 다큐멘터리 해설"),
        ("nPczCjzI2devNBz1zQrb", "Brian", "남성 · 미국 · 깊고 울림 있는"),
        ("cjVigY5qzO86Huf0OWal", "Eric", "남성 · 미국 · 매끄럽고 믿음직한"),
        ("PGoKnSD4gKn2aS99wOR2", "Brian S.", "남성 · 미국 · 쇼츠 내레이션용"),
        ("VCgLBmBjldJmfphyB8sZ", "Liam", "남성 · 미국 · 쇼츠 이야기꾼 (에너지 높음)"),
        ("UgBBYS2sOqTuMpoF3BR0", "Mark", "남성 · 미국 · 자연스러운 대화체 *(선택됨)*"),
    ],
    "ko": [
        ("PDoCXqBQFGsvfO0hNkEs", "Chris", "남성 · 20~30대 · 따뜻하고 또렷한 설명"),
        ("m3gJBS8OofDJfycyA2Ip", "Taehyung", "남성 · 20~30대 · 친근한 SNS 톤"),
        ("LKOcTG4J4tYTPR9DnLeM", "Mr. K", "남성 · 20~30대 · 크리에이터 톤"),
        ("1W00IGEmNmwmsDeYy7ag", "Krys", "남성 · 20~30대 · 밝고 신나는"),
        ("nbrxrAz3eYm9NgojrmFK", "Min-joon", "남성 · 20~30대 · 자신감 있는 내레이션"),
        ("ZJCNdZEjYwkOElxugmW2", "Hyuk", "남성 · 중년 · 차갑고 또렷한 (가장 많이 쓰임)"),
        ("4JJwo477JUAx3HV0T7n7", "Yohan Koo", "남성 · 중년 · 자신감 있는 대화체"),
        ("z6Kj0hecH20CdetSElRT", "Jennie", "여성 · 20~30대 · 자신감 있는 내레이션"),
        ("uyVNoMrnUku1dZyVEXwD", "Anna Kim", "여성 · 20~30대 · 차분하고 또렷한"),
    ],
}
# Typecast voices (tc_... ids from the Typecast site)
TYPECAST_VOICES = {
    "en": [],
    "ko": [("tc_68257f68bc6e3c161ab5078d", "필재", "남성 · Typecast *(선택됨)*")],
}
ENGINES = {"edge": EDGE_VOICES, "elevenlabs": ELEVEN_VOICES, "typecast": TYPECAST_VOICES}

# Hook + two beats of the Mercedes short, so every voice is heard in the real format (clips borrowed from it).
FOOTAGE = os.path.join(ROOT, "scripts", "mercedes_bounce.en.json")
ARROW = [{"type": "arrow", "at": 0, "until": "line2", "x": 0.5, "y": 0.52, "angle": 30}]
SAMPLES = {
    "en": {
        "hook": {"lines": ["This SUV can bounce", "itself out of sand."], "clips": ["c_spray", "c_escape"], "annotate": ARROW,
                 "sfx": [{"id": "boom", "at": "word:bounce"}]},
        "sentences": [
            {"lines": ["The driver taps one button…"], "clip": "c_screen",
             "sfx": [{"id": "mouse_click", "at": "word:button"}]},
            {"lines": ["…and the whole car starts *rocking*."], "clip": "c_rock1", "punch": True,
             "sfx": [{"id": "boom", "at": "word:rocking"}]},
        ],
    },
    "ko": {
        "hook": {"lines": ["이 SUV, 모래에 빠져도", "혼자서 *튕겨* 나옵니다."], "clips": ["c_spray", "c_escape"], "annotate": ARROW,
                 "sfx": [{"id": "boom", "at": "word:튕겨"}]},
        "sentences": [
            {"lines": ["운전자가 버튼 하나를 누르자…"], "clip": "c_screen",
             "sfx": [{"id": "mouse_click", "at": "word:버튼"}]},
            {"lines": ["…차 전체가 *들썩이기* 시작합니다."], "clip": "c_rock1", "punch": True,
             "sfx": [{"id": "boom", "at": "word:들썩이기"}]},
        ],
    },
}
CLIP_START = {"c_rock1": 182.0}  # the rocking shot ends at 185.65s; start early so slower voices stay inside it
SECTION = {"en": "영어", "ko": "한국어"}


def label_layer(tag, name, desc):
    """Replaces the headline: big number + voice name, short description underneath."""
    f1 = gfx.font("Black", 92)
    top = gfx.stroked_block([gfx.parse_rich(f"*{tag}*  {name}")], f1, (255, 255, 255), gfx.YELLOW, stroke=10)
    runs = gfx.parse_rich(desc)
    for size in range(54, 35, -2):
        f2 = gfx.font("ExtraBold", size)
        if gfx.runs_width(runs, f2) <= W - 100:
            break
    sub = gfx.stroked_block([runs], f2, (235, 235, 235), gfx.YELLOW, stroke=7)
    y2 = gfx.TITLE_TOP + int(f1.size * 1.12) + 6
    layer = Image.new("RGBA", (W, y2 + sub.height), (0, 0, 0, 0))
    layer.alpha_composite(top, ((W - top.width) // 2, gfx.TITLE_TOP))
    layer.alpha_composite(sub, ((W - sub.width) // 2, y2))
    return layer, y2 + int(f2.size * 1.12) + 12


def render_part(path):
    with open(path, encoding="utf-8") as f:
        label = json.load(f)["label"]
    short = Short(path, os.path.join(ROOT, "channel.json"))
    short.title_img, short.title_bottom = label_layer(*label)
    return short.build(os.path.dirname(path), os.path.splitext(os.path.basename(path))[0])


def slate(path, rows, dur=1.6):
    """Silent section card, encoded like the parts so they concatenate cleanly."""
    im = Image.new("RGBA", (W, H), (12, 12, 14, 255))
    y = H // 2 - 60 * len(rows)
    for text, size in rows:
        blk = gfx.stroked_block([gfx.parse_rich(text)], gfx.font("Black", size), (255, 255, 255), gfx.YELLOW,
                                stroke=max(6, size // 10))
        im.alpha_composite(blk, ((W - blk.width) // 2, y))
        y += int(size * 1.45)
    png = path[:-4] + ".png"
    im.convert("RGB").save(png)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", str(FPS), "-i", png,
                    "-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=stereo", "-t", f"{dur}",
                    "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-profile:v", "high",
                    "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                    "-c:a", "aac", "-b:a", "192k", "-ar", str(SR), path], check=True)


def duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True, check=True)
    return float(r.stdout)


def join(parts, out, height, max_mb):
    """Concatenate and re-encode in two passes to a fixed size, so the reel fits chat/app upload limits."""
    lst = out[:-4] + ".concat.txt"
    log = out[:-4] + ".x264"
    with open(lst, "w", encoding="utf-8") as f:
        f.writelines(f"file '{os.path.abspath(p)}'\n" for p in parts)
    audio_k = 160
    video_k = int(max_mb * 8 * 1024 * 1024 * 0.97 / sum(duration(p) for p in parts) / 1000) - audio_k
    common = ["-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst,
              "-vf", f"scale=-2:{height}:flags=lanczos,format=yuv420p", "-c:v", "libx264", "-preset", "slow",
              "-b:v", f"{video_k}k", "-profile:v", "high", "-passlogfile", log,
              "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709"]
    subprocess.run(["ffmpeg", *common, "-pass", "1", "-an", "-f", "mp4", os.devnull], check=True)
    subprocess.run(["ffmpeg", *common, "-pass", "2", "-c:a", "aac", "-b:a", f"{audio_k}k", "-ar", str(SR),
                    "-movflags", "+faststart", out], check=True)
    for p in [lst] + [log + ext for ext in ("-0.log", "-0.log.mbtree")]:
        if os.path.exists(p):
            os.remove(p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", default="elevenlabs", choices=list(ENGINES))
    ap.add_argument("--lang", nargs="+", default=["en", "ko"], choices=["en", "ko"])
    ap.add_argument("--rate", default="+20%", help="edge speaking rate")
    ap.add_argument("--model", default="eleven_v4", help="ElevenLabs model")
    ap.add_argument("--speed", type=float, default=1.1, help="ElevenLabs speed (0.7-1.2) / Typecast tempo (0.5-2.0)")
    ap.add_argument("--tc-model", default="ssfm-v30", help="Typecast model")
    ap.add_argument("--format", default="mp3_44100_128", help="ElevenLabs output (mp3_44100_192 needs Creator+)")
    ap.add_argument("--only", nargs="*", help="voice names or ids to include, e.g. Brian SunHi")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--height", type=int, default=1280, help="output height (parts render at 1920)")
    ap.add_argument("--max-mb", type=float, default=28, help="target file size in MiB (app uploads stop at 30)")
    ap.add_argument("--out", default=OUTPUT)
    args = ap.parse_args()
    if args.engine == "edge":
        vbase, speed = {"engine": "edge", "rate": args.rate}, args.rate
    elif args.engine == "typecast":
        vbase = {"engine": "typecast", "model": args.tc_model, "tempo": args.speed}
        speed = f"x{args.speed:g}"
    else:
        vbase = {"engine": "elevenlabs", "model": args.model, "settings": {"speed": args.speed}, "format": args.format}
        speed = f"x{args.speed:g}"

    with open(FOOTAGE, encoding="utf-8") as f:
        clips = json.load(f)["clips"]
    work = os.path.join(WORK, "voice_samples")
    os.makedirs(work, exist_ok=True)
    jobs, order, listing = [], [], []
    for lang in args.lang:
        voices = [v for v in ENGINES[args.engine][lang]
                  if not args.only or any(o.lower() in (v[0] + " " + v[1]).lower() for o in args.only)]
        if not voices:
            continue
        native = sum(v[0].startswith(lang) for v in voices) if args.engine == "edge" else len(voices)
        note = f"원어민 {native} · 다국어 {len(voices) - native}" if 0 < native < len(voices) else "같은 문장, 목소리만 바뀝니다"
        sl = os.path.join(work, f"{lang}00_slate.mp4")
        slate(sl, [(f"*{SECTION[lang]}* 목소리 {len(voices)}개", 104), (f"{lang.upper()} 01 ~ {len(voices):02d}", 70),
                   (f"{note} · 속도 {speed}", 50)])
        order.append(sl)
        sample = SAMPLES[lang]
        used = {c for it in [sample["hook"]] + sample["sentences"] for c in it.get("clips", [it.get("clip")])}
        part_clips = {c: dict(clips[c], **({"start": CLIP_START[c]} if c in CLIP_START else {})) for c in used}
        for i, (voice, name, desc) in enumerate(voices, 1):
            tag = f"{lang.upper()} {i:02d}"
            sc = {"id": f"voice_samples/{lang}{i:02d}", "lang": lang, "title": f"{tag} {name}", "aspect": "1:1",
                  "gap": 0.05, "tail": 0.75, "voice": dict(vbase, **({"name": voice} if args.engine == "edge" else {"voice_id": voice})),
                  "label": [tag, name, desc], **json.loads(json.dumps(sample)), "clips": part_clips}
            path = os.path.join(work, f"{lang}{i:02d}.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(sc, f, ensure_ascii=False, indent=1)
            jobs.append(path)
            order.append(path[:-5] + ".mp4")
            listing.append(f"{tag}  {name:12} {voice:36} {gfx.plain(desc)}")

    with ProcessPoolExecutor(args.workers) as ex:
        for out, tl in ex.map(render_part, jobs):
            print(f"[part] {os.path.basename(out)}  {tl['duration']}s  words matched "
                  f"{' '.join(it['matched'] for it in tl['items'])}" + "".join(f"\n[warn] {w}" for w in tl["warnings"]))

    os.makedirs(args.out, exist_ok=True)
    stamp = datetime.date.today().strftime("%Y%m%d")
    out = os.path.join(args.out, f"{stamp}_voice_samples_{args.engine}_{'_'.join(x.upper() for x in args.lang)}.mp4")
    join(order, out, args.height, args.max_mb)
    with open(out[:-4] + ".txt", "w", encoding="utf-8") as f:
        f.write(f"{args.engine} {json.dumps(vbase)}\n" + "\n".join(listing) + "\n")
    print(f"\n[done] {out}")


if __name__ == "__main__":
    main()
