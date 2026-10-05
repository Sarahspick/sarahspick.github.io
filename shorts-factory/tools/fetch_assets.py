"""Download everything the factory needs: TTS/ASR models, fonts, icons, sound effects.

Idempotent: files that already exist are skipped. Pure Python (urllib/tarfile/zipfile), so it
runs the same on Linux cloud sessions and on Windows.

    python tools/fetch_assets.py            # fonts, icons, sound effects (all the default pipeline needs)
    python tools/fetch_assets.py models     # + offline Kokoro voice / SenseVoice (only for engine "kokoro")
"""
import io
import json
import os
import shutil
import sys
import tarfile
import urllib.request
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, "assets")

MODELS = {
    "kokoro-v1.0.onnx": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx",
    "voices-v1.0.bin": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin",
    "silero_vad.onnx": "https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/silero_vad.onnx",
}
SENSEVOICE = ("sensevoice", "https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/"
              "sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2025-09-09.tar.bz2")
PRETENDARD = "https://github.com/orioncactus/pretendard/releases/download/v1.3.9/Pretendard-1.3.9.zip"
FONT_WEIGHTS = ["Regular", "Medium", "SemiBold", "Bold", "ExtraBold", "Black"]
MDI = "https://registry.npmjs.org/@mdi/svg/-/svg-7.4.47.tgz"
MDI_ICONS = ["check-decagram", "cursor-default", "dots-horizontal", "arrow-down-bold", "incognito", "safe-square-outline"]


def log(*a):
    print("[fetch]", *a, flush=True)


def get(url, timeout=600):
    req = urllib.request.Request(url, headers={"User-Agent": "shorts-factory/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def download(url, dest):
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return False
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    tmp = dest + ".part"
    req = urllib.request.Request(url, headers={"User-Agent": "shorts-factory/1.0"})
    with urllib.request.urlopen(req, timeout=900) as r, open(tmp, "wb") as f:
        shutil.copyfileobj(r, f, 1 << 20)
    os.replace(tmp, dest)
    return True


def fetch_models():
    d = os.path.join(A, "models")
    for name, url in MODELS.items():
        if download(url, os.path.join(d, name)):
            log("model", name)
    name, url = SENSEVOICE
    target = os.path.join(d, name)
    if not os.path.exists(os.path.join(target, "model.int8.onnx")):
        log("model sensevoice (160 MB)")
        data = get(url)
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:bz2") as tf:
            for m in tf.getmembers():
                base = os.path.basename(m.name)
                if base in ("model.int8.onnx", "tokens.txt"):
                    m.name = base
                    tf.extract(m, target)


DOC_FONTS = {  # documentary graphics (google/fonts, OFL-1.1)
    "Inter-Variable.ttf": "ofl/inter/Inter%5Bopsz,wght%5D.ttf",
    "SourceSerif4-Variable.ttf": "ofl/sourceserif4/SourceSerif4%5Bopsz,wght%5D.ttf",
    "IBMPlexMono-Regular.ttf": "ofl/ibmplexmono/IBMPlexMono-Regular.ttf",
    "IBMPlexMono-Medium.ttf": "ofl/ibmplexmono/IBMPlexMono-Medium.ttf",
}


def fetch_fonts():
    d = os.path.join(A, "fonts")
    os.makedirs(d, exist_ok=True)
    for name, path in DOC_FONTS.items():
        if not os.path.exists(os.path.join(d, name)):
            log(f"font {name} (OFL-1.1)")
            with open(os.path.join(d, name), "wb") as f:
                f.write(get("https://raw.githubusercontent.com/google/fonts/main/" + path))
    want = [f"Pretendard-{w}.otf" for w in FONT_WEIGHTS]
    if all(os.path.exists(os.path.join(d, w)) for w in want):
        return
    log("fonts Pretendard (OFL-1.1)")
    os.makedirs(d, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(get(PRETENDARD))) as z:
        for n in z.namelist():
            base = os.path.basename(n)
            if n.startswith("public/static/") and base in want or base.upper().startswith("LICENSE"):
                with open(os.path.join(d, base), "wb") as f:
                    f.write(z.read(n))


def fetch_icons():
    d = os.path.join(A, "icons")
    if all(os.path.exists(os.path.join(d, i + ".svg")) for i in MDI_ICONS):
        return
    log("icons Material Design Icons (Apache-2.0)")
    os.makedirs(d, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(get(MDI)), mode="r:gz") as tf:
        for i in MDI_ICONS:
            with open(os.path.join(d, i + ".svg"), "wb") as f:
                f.write(tf.extractfile(f"package/svg/{i}.svg").read())
        with open(os.path.join(d, "MDI-LICENSE"), "wb") as f:
            f.write(tf.extractfile("package/LICENSE").read())


def fetch_sfx():
    lib = json.load(open(os.path.join(A, "sfx_library.json"), encoding="utf-8"))["sounds"]
    d = os.path.join(A, "sfx")
    os.makedirs(d, exist_ok=True)
    npm_cache = {}
    drive_dir = None
    for sid, s in lib.items():
        dest = os.path.join(d, s["file"])
        if os.path.exists(dest):
            continue
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        if "drive" in s:  # user's own sound folder on Google Drive (link-shared): one folder download covers all
            if drive_dir is None:
                import subprocess
                import tempfile
                drive_dir = tempfile.mkdtemp()
                folder = json.load(open(os.path.join(A, "sfx_library.json"), encoding="utf-8"))["_drive_folder"]
                subprocess.run([sys.executable, "-m", "gdown", "--folder", folder, "-O", drive_dir, "-q"], check=False)
            found = [os.path.join(r, s["drive"]) for r, _, fs in os.walk(drive_dir) if s["drive"] in fs]
            if found:
                shutil.copy(found[0], dest)
                log("sfx", sid, "<- drive:", s["drive"])
            continue
        if "url" in s:
            download(s["url"], dest)
        else:
            pkg = s["npm"]
            if pkg not in npm_cache:
                meta = json.loads(get(f"https://registry.npmjs.org/{pkg}/latest"))
                npm_cache[pkg] = tarfile.open(fileobj=io.BytesIO(get(meta["dist"]["tarball"])), mode="r:gz")
            with open(dest, "wb") as f:
                f.write(npm_cache[pkg].extractfile(s["path"]).read())
        log("sfx", sid, "<-", s.get("url") or f"npm:{s['npm']}/{s['path']}")


GROUPS = {"models": fetch_models, "fonts": fetch_fonts, "icons": fetch_icons, "sfx": fetch_sfx}

if __name__ == "__main__":
    for g in (sys.argv[1:] or ["fonts", "icons", "sfx"]):
        GROUPS[g]()
    log("done")
