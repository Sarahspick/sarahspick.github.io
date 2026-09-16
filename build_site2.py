import json, datetime, base64, os

START_KST = "2026-09-16"   # slot 1's day in Korea; slot N goes live on START_KST + (N-1) days
POST_KST = "09:00"         # daily reel time in Korea (Buffer schedule). 09:00 KST = 00:00 UTC = 8pm US Eastern the evening before
IG = "https://www.instagram.com/sarahspick/"
NOTE = "treat yourself to something lovely today 🤍"

# Reads catalog.json + thumbs/ (both in the repo), so the site can be rebuilt without the videos.
# Falls back to catalog_embedded.json (output of build_batch2.py) when that file is present.
# Each catalog item may set "thumb" (a file path) to use a product photo instead of thumbs/NN.jpg.
if os.path.exists("catalog_embedded.json"):
    cat = json.load(open("catalog_embedded.json", encoding="utf-8"))
else:
    cat = json.load(open("catalog.json", encoding="utf-8"))
for it in cat:
    path = it.get("thumb") or f"thumbs/{it['slot']:02d}.jpg"
    if not it.get("thumb_data") or it.get("thumb"):
        with open(path, "rb") as f:
            it["thumb_data"] = "data:image/jpeg;base64," + base64.b64encode(f.read()).decode()

KST = datetime.timezone(datetime.timedelta(hours=9))
h, m = map(int, POST_KST.split(":"))
start = datetime.datetime.combine(datetime.date.fromisoformat(START_KST), datetime.time(h, m), KST)
cat = [it for it in cat if it.get("publish_day") is not None]   # publish_day null = paused, not on the site
for it in cat:
    live = start + datetime.timedelta(days=it["publish_day"] - 1)
    it["live_at"] = live.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")  # exact moment, same for every viewer
    it.setdefault("product", it.get("asin") or it["id"])  # same product = one card on the site
    it.setdefault("keywords", "")
items_js = json.dumps([{k: it[k] for k in ("id","name","url","live_at","thumb_data","category","product","publish_day","keywords")} for it in cat])
profile = "data:image/jpeg;base64," + base64.b64encode(open("profile.jpg","rb").read()).decode()

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light only">
<title>Sarah's Pick</title>
<meta name="description" content="Cozy home finds and little luxuries, everything from my videos in one place 💝">
<meta property="og:title" content="Sarah's Pick">
<meta property="og:description" content="Everything from my videos, all in one place 🤍">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🤍</text></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
/* Always ivory, no dark mode: the page looks the same on every phone. One font family for everything.
   On phones the whole screen is the deeper ivory. On wider screens that same deeper ivory becomes a
   rounded panel in the middle and the page around it is a lighter ivory. */
:root {{
  --page:#f4efe7; --bg:#ece4d8; --bg2:#e4dbcd; --card:#faf7f2; --ink:#2b2622; --muted:#857a6f; --line:#dfd5c7;
  --btn:#2b2622; --btn-ink:#faf7f2; --accent:#a86a52; --ring:#f7f2ea; --shadow:0 10px 30px rgba(74,58,44,.10);
  --sans:"Plus Jakarta Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}}
* {{ box-sizing:border-box; }}
html,body {{ margin:0; }}
body {{ background:var(--bg); color:var(--ink); font-family:var(--sans); -webkit-font-smoothing:antialiased; min-height:100vh; }}
.wrap {{ max-width:560px; margin:0 auto; padding:40px 16px 56px; background:var(--bg);
  background-image:linear-gradient(180deg,var(--bg2) 0,var(--bg) 320px); }}
@media (min-width:640px) {{
  body {{ background:var(--page); padding:40px 24px; }}
  .wrap {{ border-radius:32px; padding:48px 32px 56px; box-shadow:0 20px 60px rgba(74,58,44,.08); }}
}}

header {{ text-align:center; padding:0 0 22px; }}
.avatar {{ width:112px; height:112px; border-radius:50%; object-fit:cover; display:block; margin:0 auto;
  box-shadow:0 0 0 5px var(--ring), var(--shadow); }}
h1 {{ font-weight:700; font-size:30px; line-height:1.1; margin:20px 0 8px; letter-spacing:-.02em; }}
.bio {{ margin:0; font-size:15px; color:var(--muted); line-height:1.5; }}
.bio b {{ color:var(--ink); font-weight:500; }}
.social {{ margin-top:16px; display:flex; justify-content:center; gap:10px; }}
.social a {{ display:inline-flex; align-items:center; gap:7px; font-size:13px; font-weight:500; color:var(--ink);
  text-decoration:none; border:1px solid var(--line); background:var(--card); padding:9px 14px; border-radius:999px; }}
.social svg {{ width:15px; height:15px; }}

.search {{ position:relative; margin:6px 0 24px; }}
.search svg {{ position:absolute; left:18px; top:50%; width:17px; height:17px; transform:translateY(-50%); color:var(--muted); pointer-events:none; }}
.search input {{ width:100%; border:1px solid var(--line); background:var(--card); color:var(--ink); font:500 15px var(--sans);
  padding:15px 44px 15px 46px; border-radius:999px; outline:none; box-shadow:var(--shadow); -webkit-appearance:none; }}
.search input::placeholder {{ color:var(--muted); font-weight:400; }}
.search input::-webkit-search-cancel-button, .search input::-webkit-search-decoration {{ -webkit-appearance:none; display:none; }}
.search input:focus {{ border-color:var(--ink); }}
.search button {{ position:absolute; right:10px; top:50%; transform:translateY(-50%); width:30px; height:30px; border:0; border-radius:50%;
  background:var(--line); color:var(--ink); font:600 14px var(--sans); cursor:pointer; display:none; align-items:center; justify-content:center; }}
.search.has button {{ display:flex; }}

.hero {{ background:var(--card); border-radius:22px; overflow:hidden; box-shadow:var(--shadow); text-decoration:none; color:inherit; display:block; }}
.hero .img {{ position:relative; aspect-ratio:5/4; overflow:hidden; background:#fff; }}
.hero img {{ width:100%; height:100%; object-fit:cover; display:block; transition:transform .6s ease; }}
.hero:hover img {{ transform:scale(1.03); }}
.hero .badge {{ position:absolute; top:14px; left:14px; background:rgba(250,247,242,.94); color:#2b2622; font-size:11px; letter-spacing:.14em;
  text-transform:uppercase; font-weight:600; padding:7px 11px; border-radius:999px; }}
.hero .txt {{ padding:18px 20px 20px; }}
.hero h2 {{ font-size:21px; font-weight:600; margin:0 0 14px; line-height:1.3; letter-spacing:-.01em; }}
.btn {{ display:inline-flex; align-items:center; gap:8px; background:var(--btn); color:var(--btn-ink); font-weight:500; font-size:13px;
  letter-spacing:.02em; padding:12px 18px; border-radius:999px; }}

.note {{ text-align:center; margin:32px 0 16px; font-size:15px; font-weight:500; color:var(--ink); line-height:1.5; }}
.grid {{ display:grid; grid-template-columns:1fr 1fr; gap:14px; }}
.card {{ background:var(--card); border-radius:18px; overflow:hidden; box-shadow:var(--shadow); text-decoration:none; color:inherit;
  display:flex; flex-direction:column; }}
.card .img {{ aspect-ratio:4/5; overflow:hidden; background:#fff; }}
.card img {{ width:100%; height:100%; object-fit:cover; display:block; transition:transform .6s ease; }}
.card:hover img {{ transform:scale(1.04); }}
.card .txt {{ padding:12px 13px 14px; display:flex; flex-direction:column; gap:5px; flex:1; }}
.card h4 {{ margin:0; font-size:14px; font-weight:600; line-height:1.4; letter-spacing:-.005em; }}
.card .shop {{ margin-top:auto; padding-top:8px; font-size:12px; font-weight:600; color:var(--accent); letter-spacing:.04em; }}

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

  <form class="search" id="search" role="search" onsubmit="return false">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
    <input id="q" type="search" placeholder="search my picks" autocomplete="off" aria-label="Search products">
    <button type="button" id="clear" aria-label="Clear search">×</button>
  </form>

  <section>
    <div id="hero"></div>
    <div class="note" id="note" hidden>{NOTE}</div>
    <div class="grid" id="grid"></div>
    <div class="empty" id="empty" hidden></div>
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
  if (!g) groups.set(i.product, {{...i, latest: i.live_at, text: (i.name + " " + i.keywords + " " + i.category).toLowerCase()}});
  else {{ if (i.live_at > g.latest) g.latest = i.live_at; g.text += " " + (i.name + " " + i.keywords).toLowerCase(); }}
}}
const live = [...groups.values()].sort((a,b) => b.latest.localeCompare(a.latest) || b.publish_day - a.publish_day);
const esc = s => s.replace(/[&<>"]/g, c => ({{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}})[c]);
const $ = id => document.getElementById(id);
const card = i => `
      <a class="card" href="${{i.url}}" target="_blank" rel="noopener sponsored">
        <div class="img"><img src="${{i.thumb_data}}" alt="" loading="lazy"></div>
        <div class="txt"><h4>${{esc(i.name)}}</h4><span class="shop">Shop on Amazon →</span></div>
      </a>`;
function render(q) {{
  q = q.trim().toLowerCase();
  const words = q.split(/\\s+/).filter(Boolean);
  const list = words.length ? live.filter(i => words.every(w => i.text.includes(w))) : live;
  $("hero").innerHTML = ""; $("grid").innerHTML = ""; $("note").hidden = true; $("empty").hidden = true;
  if (!live.length) {{ $("empty").hidden = false; $("empty").textContent = "something lovely is on its way, come back tomorrow 🤍"; return; }}
  if (!list.length) {{ $("empty").hidden = false; $("empty").textContent = "nothing here yet, try another word 🤍"; return; }}
  if (words.length) {{ $("grid").innerHTML = list.map(card).join(""); return; }}
  const [first, ...rest] = list;
  $("hero").innerHTML = `
    <a class="hero" href="${{first.url}}" target="_blank" rel="noopener sponsored">
      <div class="img"><img src="${{first.thumb_data}}" alt=""><span class="badge">New today</span></div>
      <div class="txt"><h2>${{esc(first.name)}}</h2><span class="btn">Shop on Amazon <span aria-hidden="true">→</span></span></div>
    </a>`;
  if (rest.length) {{ $("note").hidden = false; $("grid").innerHTML = rest.map(card).join(""); }}
}}
const q = $("q");
q.addEventListener("input", () => {{ $("search").classList.toggle("has", q.value.length > 0); render(q.value); }});
$("clear").addEventListener("click", () => {{ q.value = ""; $("search").classList.remove("has"); render(""); q.focus(); }});
render("");
</script>
</body>
</html>"""
open("index.html","w",encoding="utf-8").write(html)
print(len(html)//1024, "KB")
