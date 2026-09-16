import json, csv, subprocess, os, base64, io
from PIL import Image

TAG = "hp302-20"
DISC = "As an Amazon Associate I earn from qualifying purchases."
def link(a): return f"https://www.amazon.com/dp/{a}?tag={TAG}"

items = [
 dict(slot=1, file="2026-09-09_@jess.favoritefinds_7683380807334956318.mp4", creator="jess.favoritefinds", t=0.5,
      asin="B0GQWK2D7L", cat="bedding",
      name="Mellow MarshMellow Comforter, pick your color", short="MarshMellow Comforter (10 colors)",
      sub="White, sand, pink, blue, sage, sunrise, espresso and more 🌈☁️",
      cap="every single color of the marshmallow comforter in one bed 🌈☁️ which one is you?",
      pin="all of these are the Mellow MarshMellow Comforter, just pick your color ☁️ grab it here 👉 {link}",
      tags="#marshmallowcomforter #bedroommakeover #amazonfinds #amazonhome #cozybedroom #colorfulhome #bedding #affiliate"),
 dict(slot=2, file="2026-02-06_@jess.favoritefinds_7603475581237251359.mp4", creator="jess.favoritefinds", t=3.0,
      asin="B0GQWK2D7L", cat="bedding",
      name="Mellow MarshMellow Comforter, White", short="MarshMellow Comforter",
      sub="Double stuffed and impossibly fluffy, no duvet cover needed ☁️",
      cap="i've never wanted to stay in bed this badly ☁️🤍 rainy days were made for this comforter",
      pin="this is the Mellow MarshMellow Comforter and it's every bit as fluffy as it looks 🤍 grab it here 👉 {link}",
      tags="#marshmallowcomforter #amazonfinds #amazonhome #cozybedroom #bedroominspo #rainydays #bedding #affiliate"),
 dict(slot=3, file="2026-09-02_@mrs.nikialexa_7680933683120835862.mp4", creator="mrs.nikialexa", t=3.0,
      asin="B0CKGXMBFR", cat="kitchen",
      name="SCOUPS Soft Top Silicone Ladle", short="SCOUPS Soft Top Ladle",
      sub="The soft edge hugs your pan and scrapes it clean 🍝",
      cap="not a single drop of sauce left behind 🍝 my kitchen finally feels peaceful",
      pin="it's the SCOUPS Soft Top Ladle and the soft edge really does hug the pan 🧡 grab it here 👉 {link}",
      tags="#amazonfinds #kitchengadgets #amazonkitchen #kitchenmusthaves #cookinghacks #homecooking #affiliate"),
 dict(slot=4, file="2026-03-12_@myaquasplash_7616067171260632333.mp4", creator="myaquasplash", t=1.0,
      asin="B0GQWK2D7L", cat="bedding",
      name="Mellow MarshMellow Comforter, Baby Pink", short="MarshMellow Comforter (Baby Pink)",
      sub="The pink marshmallow blanket from the video 🎀 same cloud fill, ten colors",
      cap="he got me the pink marshmallow blanket and i might cry a little 🎀🥹",
      pin="the pink one is the Mellow MarshMellow Comforter in Baby Pink 🎀 grab it here 👉 {link}",
      tags="#marshmallowcomforter #pinkbedroom #amazonfinds #amazonhome #cozybedroom #girlyroom #bedding #affiliate"),
 dict(slot=5, file="2025-11-06_@electro.galaxy.shop_7569279437561203988.mp4", creator="electro.galaxy.shop", t=4.0,
      asin="B0F59B1YD8", cat="gadgets",
      name="Flat LED Book Light", short="Flat LED Book Light",
      sub="Lights the whole page so softly, with a timer for when you drift off 📖",
      cap="reading in bed at 2am just got so much prettier 📖✨",
      pin="this little flat book light lights the whole page and turns itself off when you fall asleep 🥹 grab it here 👉 {link}",
      tags="#booktok #booklight #amazonfinds #bookish #readingnook #giftsforreaders #bedtimereading #affiliate"),
 dict(slot=6, file="2026-05-24_@hannahbentley_7643229668631383309.mp4", creator="hannahbentley", t=1.0,
      asin="B0GQWK2D7L", cat="bedding",
      name="Mellow MarshMellow Comforter, Baby Blue", short="MarshMellow Comforter (Baby Blue)",
      sub="Baby blue clouds for your bed 🩵 extreme fluff, machine washable",
      cap="baby blue clouds on my bed 🩵☁️ i'm not leaving, sorry",
      pin="it's the Mellow MarshMellow Comforter in Baby Blue and it's pure cloud 🩵 grab it here 👉 {link}",
      tags="#marshmallowcomforter #bluebedroom #amazonfinds #amazonhome #cozybedroom #bedroominspo #bedding #affiliate"),
 dict(slot=7, file="2026-04-21_@morrowmoon0_7630867654085053727.mp4", creator="morrowmoon0", t=1.5,
      asin="B0H44LLZLY", cat="personal-care",
      name="Pop Up Floss Pick Case, 2 pack", short="Pop Up Floss Pick Case",
      sub="One click and a floss pick pops out 🦷 tiny enough for any purse",
      cap="the cutest little thing in my bag 🦷💗 one click and a pick pops out",
      pin="it's a pop up floss pick case, pink and mint, and it lives in my purse now 💗 grab it here 👉 {link}",
      tags="#amazonfinds #tiktokmademebuyit #purseessentials #travelessentials #thatgirl #whatsinmybag #affiliate"),
 dict(slot=8, file="2026-02-07_@hannahbentley_7603860160955632909.mp4", creator="hannahbentley", t=12.0,
      asin="B0GZLX82G9", cat="bedding",
      name="Mellow MarshMellow Comforter, Sand", short="MarshMellow Comforter (Sand)",
      sub="The neutral one 🤎 warm cream, same marshmallow fill",
      cap="the sand color has my whole heart 🤎 it's like sleeping inside a latte",
      pin="this is the Mellow MarshMellow Comforter in Sand, the softest neutral ever 🤎 grab it here 👉 {link}",
      tags="#marshmallowcomforter #neutralbedroom #amazonfinds #amazonhome #cozybedroom #bedroominspo #bedding #affiliate"),
 dict(slot=9, file="2026-09-01_@megansue100_7680346025726463245.mp4", creator="megansue100", t=25.0,
      asin="B0GQWK2D7L", cat="bedding",
      name="Mellow MarshMellow Comforter, Espresso", short="MarshMellow Comforter (Espresso)",
      sub="Espresso comforter and marshmallow pillows, the coziest combo ☕🤍",
      cap="espresso comforter, marshmallow pillows, and a very happy me ☕🤍",
      pin="the brown one is the Mellow MarshMellow Comforter in Espresso and yes the pillows match ☕ grab it here 👉 {link}",
      tags="#marshmallowcomforter #moodybedroom #amazonfinds #amazonhome #cozybedroom #bedroominspo #bedding #affiliate"),
]

os.makedirs("out/thumbs", exist_ok=True)
catalog, rows = [], []
md = ["# Sarah's Pick, Batch 1 문구 (9 slots)\n",
      "규칙: 대시 기호 없음, 한두 문장, 감성적으로, 이모지 사용. 고정댓글 마지막 줄의 아마존 고지문은 약관상 필수라 그대로 둠.\n",
      "크리에이터 태그는 틱톡 핸들 기준이야. 인스타 핸들이 다르면 @ 부분만 바꿔줘.\n"]
for it in items:
    s = it["slot"]; it["link"] = link(it["asin"])
    thumb = f"out/thumbs/{s:02d}.jpg"
    subprocess.run(["ffmpeg","-v","error","-y","-ss",str(it["t"]),"-i",it["file"],"-frames:v","1","-vf","scale=720:-1","-q:v","3",thumb],check=True)
    im = Image.open(thumb).convert("RGB"); w,h = im.size; th = int(w*5/4)
    if h > th: im = im.crop((0,(h-th)//2,w,(h-th)//2+th))
    im = im.resize((480,600)); b = io.BytesIO(); im.save(b,"JPEG",quality=72,optimize=True)
    open(thumb,"wb").write(b.getvalue())  # keep the exact bytes that get embedded, so the repo copy can rebuild the site
    data = "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()
    caption = f"{it['cap']}\n\n🛒 link in bio, look for \"{it['short']}\"\n🎥 @{it['creator']}\n\n{it['tags']} #sarahspick"
    pinned = it["pin"].format(link=it["link"]) + f"\n\n{DISC}"
    md += [f"\n---\n\n## Slot {s}. {it['name']}\n", f"파일: `{it['file']}`  \nASIN: `{it['asin']}`  \n링크: {it['link']}\n",
           "\n### 사이트\n", f"**{it['name']}**  \n{it['sub']}\n",
           "\n### 인스타 캡션\n```\n" + caption + "\n```\n", "\n### 고정 댓글\n```\n" + pinned + "\n```\n"]
    catalog.append(dict(slot=s, id=f"b1-{s:02d}", name=it["name"], sub=it["sub"], asin=it["asin"], url=it["link"],
                        category=it["cat"], publish_day=s, creator=it["creator"], source_file=it["file"], thumb_data=data))
    rows.append(dict(slot=s, file=it["file"], creator=it["creator"], product=it["name"], asin=it["asin"], link=it["link"]))

json.dump(catalog, open("out/catalog_embedded.json","w"))
json.dump([{k:v for k,v in c.items() if k!="thumb_data"} for c in catalog], open("out/catalog.json","w"), indent=1, ensure_ascii=False)
open("out/batch1_copy.md","w").write("\n".join(md))
print("ok", len(catalog))
