import json, datetime, base64, os

START_KST = "2026-09-16"   # slot 1's day in Korea; slot N goes live on START_KST + (N-1) days
POST_KST = "09:00"         # daily reel time in Korea (Buffer schedule). 09:00 KST = 00:00 UTC = 8pm US Eastern the evening before
IG = "https://www.instagram.com/sarahspick/"
# Reads catalog.json + thumbs/NN.jpg (both in the repo), so the site can be rebuilt without the videos.
# Falls back to catalog_embedded.json (output of build_batch2.py) when that file is present.
if os.path.exists("catalog_embedded.json"):
    cat = json.load(open("catalog_embedded.json", encoding="utf-8"))
else:
    cat = json.load(open("catalog.json", encoding="utf-8"))
    for it in cat:
        with open(f"thumbs/{it['slot']:02d}.jpg", "rb") as f:
            it["thumb_data"] = "data:image/jpeg;base64," + base64.b64encode(f.read()).decode()
KST = datetime.timezone(datetime.timedelta(hours=9))
h, m = map(int, POST_KST.split(":"))
start = datetime.datetime.combine(datetime.date.fromisoformat(START_KST), datetime.time(h, m), KST)
for it in cat:
    live = start + datetime.timedelta(days=it["publish_day"] - 1)
    it["live_at"] = live.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")  # exact moment, same for every viewer
    it.setdefault("product", it.get("asin") or it["id"])  # same product = one card on the site
items_js = json.dumps([{k: it[k] for k in ("id","name","url","live_at","thumb_data","category","product","publish_day")} for it in cat])
profile = "data:image/jpeg;base64," + base64.b64encode(open("profile.jpg","rb").read()).decode()

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light only">
<title>Sarah's Pick</title>
<meta name="description" content="Cozy home finds and little luxuries, everything from my videos in one place 🤍">
<meta property="og:title" content="Sarah's Pick">
<meta property="og:description" content="Everything from my videos, all in one place 🤍">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🤍</text></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root {{
  --bg:#ece4d8; --bg2:#e4dbcd; --card:#faf7f2; --ink:#2b2622; --muted:#857a6f; --line:#dfd5c7;
  --btn:#2b2622; --btn-ink:#faf7f2; --accent:#a86a52; --ring:#f7f2ea; --shadow:0 10px 30px rgba(74,58,44,.10);
  --serif:"Plus Jakarta Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  --sans:"Plus Jakarta Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}}
/* always ivory, no dark mode: the page should look the same on every phone. One font family (Plus Jakarta Sans) for everything. */
* {{ box-sizing:border-box; }}
html,body {{ margin:0; }}
body {{ background:var(--bg); background-image:linear-gradient(180deg,var(--bg2) 0,var(--bg) 320px); color:var(--ink); font-family:var(--sans);
  -webkit-font-smoothing:antialiased; min-height:100vh; }}
.wrap {{ max-width:560px; margin:0 auto; padding:40px 16px 56px; }}

header {{ text-align:center; padding:0 0 26px; }}
.avatar {{ width:112px; height:112px; border-radius:50%; object-fit:cover; display:block; margin:0 auto;
  box-shadow:0 0 0 5px var(--ring), var(--shadow); }}
h1 {{ font-family:var(--sans); font-weight:700; font-size:30px; line-height:1.1; margin:20px 0 8px; letter-spacing:-.02em; }}
.bio {{ margin:0; font-size:15px; color:var(--muted); line-height:1.5; }}
.bio b {{ color:var(--ink); font-weight:500; }}
.social {{ margin-top:16px; display:flex; justify-content:center; gap:10px; }}
.social a {{ display:inline-flex; align-items:center; gap:7px; font-size:13px; font-weight:500; color:var(--ink);
  text-decoration:none; border:1px solid var(--line); background:var(--card); padding:9px 14px; border-radius:999px; }}
.social svg {{ width:15px; height:15px; }}

.tabs {{ display:flex; gap:22px; justify-content:center; border-bottom:1px solid var(--line); margin:6px 0 22px; }}
.tab {{ background:none; border:0; padding:10px 2px 12px; font:500 13px var(--sans); letter-spacing:.14em; text-transform:uppercase;
  color:var(--muted); cursor:pointer; position:relative; }}
.tab[aria-selected="true"] {{ color:var(--ink); }}
.tab[aria-selected="true"]::after {{ content:""; position:absolute; left:0; right:0; bottom:-1px; height:1.5px; background:var(--ink); }}

.panel[hidden] {{ display:none; }}
.eyebrow {{ font-size:11px; letter-spacing:.16em; text-transform:uppercase; color:var(--accent); font-weight:600; }}

.hero {{ background:var(--card); border-radius:22px; overflow:hidden; box-shadow:var(--shadow); text-decoration:none; color:inherit; display:block; }}
.hero .img {{ position:relative; aspect-ratio:5/4; overflow:hidden; }}
.hero img {{ width:100%; height:100%; object-fit:cover; display:block; transition:transform .6s ease; }}
.hero:hover img {{ transform:scale(1.03); }}
.hero .badge {{ position:absolute; top:14px; left:14px; background:rgba(255,253,249,.92); color:#2a2420; font-size:11px; letter-spacing:.14em;
  text-transform:uppercase; font-weight:600; padding:7px 11px; border-radius:999px; }}
.hero .txt {{ padding:18px 20px 20px; }}
.hero h2 {{ font-family:var(--sans); font-size:21px; font-weight:600; margin:0 0 14px; line-height:1.3; letter-spacing:-.01em; }}
.btn {{ display:inline-flex; align-items:center; gap:8px; background:var(--btn); color:var(--btn-ink); font-weight:500; font-size:13px;
  letter-spacing:.02em; padding:12px 18px; border-radius:999px; }}

.note {{ text-align:center; margin:32px 0 16px; font-size:15px; font-weight:500; color:var(--ink); line-height:1.5; }}
.grid {{ display:grid; grid-template-columns:1fr 1fr; gap:14px; }}
.card {{ background:var(--card); border-radius:18px; overflow:hidden; box-shadow:var(--shadow); text-decoration:none; color:inherit;
  display:flex; flex-direction:column; }}
.card .img {{ aspect-ratio:4/5; overflow:hidden; }}
.card img {{ width:100%; height:100%; object-fit:cover; display:block; transition:transform .6s ease; }}
.card:hover img {{ transform:scale(1.04); }}
.card .txt {{ padding:12px 13px 14px; display:flex; flex-direction:column; gap:5px; flex:1; }}
.card h4 {{ margin:0; font-size:14px; font-weight:600; line-height:1.4; letter-spacing:-.005em; }}
.card .shop {{ margin-top:auto; padding-top:8px; font-size:12px; font-weight:600; color:var(--accent); letter-spacing:.04em; }}

.links {{ display:grid; gap:12px; }}
.link {{ display:flex; align-items:center; justify-content:center; gap:10px; background:var(--card); border:1px solid var(--line);
  border-radius:16px; padding:18px; text-decoration:none; color:var(--ink); font-weight:500; font-size:15px; box-shadow:var(--shadow); }}
.link svg {{ width:18px; height:18px; }}

.empty {{ text-align:center; color:var(--muted); padding:48px 0; font-size:16px; }}
footer {{ margin-top:44px; color:var(--muted); font-size:11.5px; line-height:1.6; text-align:center; }}
footer .heart {{ font-size:14px; font-weight:500; color:var(--ink); margin-bottom:8px; }}
@media (max-width:360px) {{ .grid {{ gap:10px; }} h1 {{ font-size:27px; }} }}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <img class="avatar" src="{profile}" alt="Sarah">
    <h1>Sarah's Pick</h1>
    <p class="bio">cozy home finds &amp; little luxuries 🤍<br><b>everything from my videos, all in one place</b></p>
    <div class="social">
      <a href="{IG}" target="_blank" rel="noopener">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none"/></svg>
        @sarahspick
      </a>
    </div>
  </header>

  <div class="tabs" role="tablist">
    <button class="tab" role="tab" aria-selected="true" data-tab="shop">Shop</button>
    <button class="tab" role="tab" aria-selected="false" data-tab="links">Links</button>
  </div>

  <section class="panel" id="shop">
    <div id="hero"></div>
    <div class="note" id="note" hidden>treat yourself to something lovely today 🤍</div>
    <div class="grid" id="grid"></div>
    <div class="empty" id="empty" hidden>something lovely is on its way, come back tomorrow 🤍</div>
  </section>

  <section class="panel" id="links" hidden>
    <div class="links">
      <a class="link" href="{IG}" target="_blank" rel="noopener">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none"/></svg>
        Instagram
      </a>
    </div>
  </section>

  <footer>
    <div class="heart">thank you for shopping with me 🤍</div>
    As an Amazon Associate I earn from qualifying purchases.<br>
    These are affiliate links, and shopping through them supports my little channel at no extra cost to you.
  </footer>
</div>
<script>
const ITEMS = {items_js};
const now = Date.now();
// One card per product: the first video's card represents it, and it moves to the top whenever a new video of it goes live.
const groups = new Map();
for (const i of ITEMS.filter(i => Date.parse(i.live_at) <= now).sort((a,b) => a.publish_day - b.publish_day)) {{
  const g = groups.get(i.product);
  if (!g) groups.set(i.product, {{...i, latest: i.live_at}});
  else if (i.live_at > g.latest) g.latest = i.live_at;
}}
const live = [...groups.values()].sort((a,b) => b.latest.localeCompare(a.latest) || b.publish_day - a.publish_day);
const esc = s => s.replace(/[&<>"]/g, c => ({{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}})[c]);
if (!live.length) {{
  document.getElementById("empty").hidden = false;
}} else {{
  const [first, ...rest] = live;
  document.getElementById("hero").innerHTML = `
    <a class="hero" href="${{first.url}}" target="_blank" rel="noopener sponsored">
      <div class="img"><img src="${{first.thumb_data}}" alt=""><span class="badge">New today</span></div>
      <div class="txt"><h2>${{esc(first.name)}}</h2><span class="btn">Shop on Amazon <span aria-hidden="true">→</span></span></div>
    </a>`;
  if (rest.length) {{
    document.getElementById("note").hidden = false;
    document.getElementById("grid").innerHTML = rest.map(i => `
      <a class="card" href="${{i.url}}" target="_blank" rel="noopener sponsored">
        <div class="img"><img src="${{i.thumb_data}}" alt="" loading="lazy"></div>
        <div class="txt"><h4>${{esc(i.name)}}</h4><span class="shop">Shop on Amazon →</span></div>
      </a>`).join("");
  }}
}}
document.querySelectorAll(".tab").forEach(t => t.addEventListener("click", () => {{
  document.querySelectorAll(".tab").forEach(x => x.setAttribute("aria-selected", x === t));
  document.querySelectorAll(".panel").forEach(p => p.hidden = p.id !== t.dataset.tab);
}}));
</script>
</body>
</html>"""
open("index.html","w",encoding="utf-8").write(html)
print(len(html)//1024, "KB")
