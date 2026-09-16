import json, csv, subprocess, os, base64, io, sys
COPY_ONLY = "--copy-only" in sys.argv   # python3 build_batch2.py --copy-only  -> only writes the Buffer Document

TAG = "hp302-20"
# Instagram allows at most 5 hashtags per post: 4 topical + #affiliate (FTC disclosure).
# product: optional group key. Items with the same product (or, by default, the same ASIN) become ONE card on the site.
DISC = "As an Amazon Associate I earn from qualifying purchases."
def link(a): return f"https://www.amazon.com/dp/{a}?tag={TAG}"

items = [
 dict(slot=1, file="2026-09-09_@jess.favoritefinds_7683380807334956318.mp4", creator="jess.favoritefinds", t=0.5,
      asin="B0GQWK2D7L", cat="bedding",
      name="Mellow MarshMellow Comforter, pick your color ☁️🌈", short="MarshMellow Comforter (10 colors)",
      cap="every single color of the marshmallow comforter in one bed 🌈☁️ which one is you?",
      pin="all of these are the Mellow MarshMellow Comforter, just pick your color ☁️ grab it here 👉 {link}",
      tags="#marshmallowcomforter #amazonfinds #amazonhome #cozybedroom #affiliate"),
 dict(slot=2, file="2026-02-06_@jess.favoritefinds_7603475581237251359.mp4", creator="jess.favoritefinds", t=3.0,
      asin="B0GQWK2D7L", cat="bedding",
      name="Mellow MarshMellow Comforter, White ☁️🤍", short="MarshMellow Comforter",
      cap="i've never wanted to stay in bed this badly ☁️🤍 rainy days were made for this comforter",
      pin="this is the Mellow MarshMellow Comforter and it's every bit as fluffy as it looks 🤍 grab it here 👉 {link}",
      tags="#marshmallowcomforter #amazonfinds #cozybedroom #bedroominspo #affiliate"),
 dict(slot=3, file="2026-09-02_@mrs.nikialexa_7680933683120835862.mp4", creator="mrs.nikialexa", t=3.0,
      asin="B0CKGXMBFR", cat="kitchen",
      name="SCOUPS Soft Top Silicone Ladle 🍝", short="SCOUPS Soft Top Ladle",
      cap="not a single drop of sauce left behind 🍝 my kitchen finally feels peaceful",
      pin="it's the SCOUPS Soft Top Ladle and the soft edge really does hug the pan 🧡 grab it here 👉 {link}",
      tags="#amazonfinds #kitchengadgets #amazonkitchen #kitchenmusthaves #affiliate"),
 dict(slot=4, file="2026-03-12_@myaquasplash_7616067171260632333.mp4", creator="myaquasplash", t=1.0,
      asin="B0GQWK2D7L", cat="bedding",
      name="Mellow MarshMellow Comforter, Baby Pink 🎀", short="MarshMellow Comforter (Baby Pink)",
      cap="he got me the pink marshmallow blanket and i might cry a little 🎀🥹",
      pin="the pink one is the Mellow MarshMellow Comforter in Baby Pink 🎀 grab it here 👉 {link}",
      tags="#marshmallowcomforter #pinkbedroom #amazonfinds #cozybedroom #affiliate"),
 dict(slot=5, file="2025-11-06_@electro.galaxy.shop_7569279437561203988.mp4", creator="electro.galaxy.shop", t=4.0,
      asin="B0F59B1YD8", cat="gadgets",
      name="Flat LED Book Light 📖✨", short="Flat LED Book Light",
      cap="reading in bed at 2am just got so much prettier 📖✨",
      pin="this little flat book light lights the whole page and turns itself off when you fall asleep 🥹 grab it here 👉 {link}",
      tags="#booktok #booklight #amazonfinds #giftsforreaders #affiliate"),
 dict(slot=6, file="2026-05-24_@hannahbentley_7643229668631383309.mp4", creator="hannahbentley", t=1.0,
      asin="B0GQWK2D7L", cat="bedding",
      name="Mellow MarshMellow Comforter, Baby Blue 🩵☁️", short="MarshMellow Comforter (Baby Blue)",
      cap="baby blue clouds on my bed 🩵☁️ i'm not leaving, sorry",
      pin="it's the Mellow MarshMellow Comforter in Baby Blue and it's pure cloud 🩵 grab it here 👉 {link}",
      tags="#marshmallowcomforter #bluebedroom #amazonfinds #cozybedroom #affiliate"),
 dict(slot=7, file="2026-04-21_@morrowmoon0_7630867654085053727.mp4", creator="morrowmoon0", t=1.5,
      asin="B0H44LLZLY", cat="personal-care",
      name="Pop Up Floss Pick Case, 2 pack 🦷💗", short="Pop Up Floss Pick Case",
      cap="the cutest little thing in my bag 🦷💗 one click and a pick pops out",
      pin="it's a pop up floss pick case, pink and mint, and it lives in my purse now 💗 grab it here 👉 {link}",
      tags="#amazonfinds #tiktokmademebuyit #purseessentials #whatsinmybag #affiliate"),
 dict(slot=8, file="2026-02-07_@hannahbentley_7603860160955632909.mp4", creator="hannahbentley", t=12.0,
      asin="B0GZLX82G9", cat="bedding",
      name="Mellow MarshMellow Comforter, Sand 🤎", short="MarshMellow Comforter (Sand)",
      cap="the sand color has my whole heart 🤎 it's like sleeping inside a latte",
      pin="this is the Mellow MarshMellow Comforter in Sand, the softest neutral ever 🤎 grab it here 👉 {link}",
      tags="#marshmallowcomforter #neutralbedroom #amazonfinds #cozybedroom #affiliate"),
 dict(slot=9, file="2026-09-01_@megansue100_7680346025726463245.mp4", creator="megansue100", t=25.0,
      asin="B0GQWK2D7L", cat="bedding",
      name="Mellow MarshMellow Comforter, Espresso ☕🤍", short="MarshMellow Comforter (Espresso)",
      cap="espresso comforter, marshmallow pillows, and a very happy me ☕🤍",
      pin="the brown one is the Mellow MarshMellow Comforter in Espresso and yes the pillows match ☕ grab it here 👉 {link}",
      tags="#marshmallowcomforter #moodybedroom #amazonfinds #cozybedroom #affiliate"),
]

# Posting schedule (KST 09:00 daily). Mochi's decision 2026-09-16: 16 comforter, 17 ladle, 18 book light, 19 floss case, then pause.
# slot -> day. Slots not listed are paused (kept in the document under "보류", not on the site).
SCHEDULE = {1: "2026-09-16", 3: "2026-09-17", 5: "2026-09-18", 7: "2026-09-19"}

def caption_of(it):
    return f"{it['cap']}\n\n🛒 link in bio, look for \"{it['short']}\"\n🎥 @{it['creator']}\n\n{it['tags']}"
def pinned_of(it):
    return it["pin"].format(link=it["link"]) + f"\n\n{DISC}"
def block(it, head):
    return [f"\n---\n\n## {head}\n", f"제품: **{it['name']}**  \n파일: `{it['file']}`  \nASIN: `{it['asin']}`  \n링크: {it['link']}\n",
            "\n### 인스타 캡션 (그대로 복사)\n```\n" + caption_of(it) + "\n```\n",
            "\n### 고정 댓글 (게시 후 인스타 앱에서 달고 고정)\n```\n" + pinned_of(it) + "\n```\n"]

os.makedirs("out/thumbs", exist_ok=True)
catalog, rows = [], []
md = ["# Buffer Document (Sarah's Pick, Batch 1)\n",
      "Buffer에 예약할 때 여기서 캡션을 그대로 복사한다. 매일 한국시각 오전 9시. 해시태그는 인스타 제한에 맞춰 5개(FTC용 #affiliate 포함).\n",
      "규칙: 대시 기호 없음, 한두 문장, 감성적으로, 이모지 사용. 고정댓글 마지막 줄의 아마존 고지문은 약관상 필수.\n",
      "크리에이터 태그는 틱톡 핸들 기준. 인스타 핸들이 다르면 @ 부분만 바꾼다.\n",
      "\n# 예약 순서\n"]
for it in items: it["link"] = link(it["asin"])
for slot, date in sorted(SCHEDULE.items(), key=lambda kv: kv[1]):
    it = next(i for i in items if i["slot"] == slot)
    md += block(it, f"{date} (KST 09:00), {it['name']}")
md += ["\n\n# 보류 (아직 예약하지 않음)\n"]
for it in items:
    if it["slot"] not in SCHEDULE: md += block(it, f"보류, 슬롯 {it['slot']}. {it['name']}")
open("out/Buffer Document.md","w",encoding="utf-8").write("\n".join(md))
if COPY_ONLY:
    print("Buffer Document written"); sys.exit()

from PIL import Image
for it in items:
    s = it["slot"]
    thumb = f"out/thumbs/{s:02d}.jpg"
    subprocess.run(["ffmpeg","-v","error","-y","-ss",str(it["t"]),"-i",it["file"],"-frames:v","1","-vf","scale=720:-1","-q:v","3",thumb],check=True)
    im = Image.open(thumb).convert("RGB"); w,h = im.size; th = int(w*5/4)
    if h > th: im = im.crop((0,(h-th)//2,w,(h-th)//2+th))
    im = im.resize((480,600)); b = io.BytesIO(); im.save(b,"JPEG",quality=72,optimize=True)
    open(thumb,"wb").write(b.getvalue())  # keep the exact bytes that get embedded, so the repo copy can rebuild the site
    data = "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()
    day = sorted(SCHEDULE.values()).index(SCHEDULE[s]) + 1 if s in SCHEDULE else None   # None = paused, not on the site
    catalog.append(dict(slot=s, id=f"b1-{s:02d}", name=it["name"], asin=it["asin"], url=it["link"], product=it.get("product", it["asin"]),
                        category=it["cat"], publish_day=day, creator=it["creator"], source_file=it["file"], thumb_data=data))
    rows.append(dict(slot=s, file=it["file"], creator=it["creator"], product=it["name"], asin=it["asin"], link=it["link"]))

json.dump(catalog, open("out/catalog_embedded.json","w"))
json.dump([{k:v for k,v in c.items() if k!="thumb_data"} for c in catalog], open("out/catalog.json","w"), indent=1, ensure_ascii=False)
print("ok", len(catalog))
