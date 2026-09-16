import json, datetime, base64

START = "2026-09-16"   # slot 1 goes live on this US date; slot N on START + (N-1) days
IG = "https://www.instagram.com/sarahspick/"
cat = json.load(open("catalog_embedded.json"))
start = datetime.date.fromisoformat(START)
for it in cat:
    it["date"] = (start + datetime.timedelta(days=it["publish_day"] - 1)).isoformat()
items_js = json.dumps([{k: it[k] for k in ("id","name","sub","url","date","thumb_data","category")} for it in cat])
profile = "data:image/jpeg;base64," + base64.b64encode(open("profile.jpg","rb").read()).decode()

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sarah's Pick</title>
<meta name="description" content="Cozy home finds and little luxuries, everything from my videos in one place 🤍">
<meta property="og:title" content="Sarah's Pick">
<meta property="og:description" content="Everything from my videos, all in one place 🤍">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🤍</text></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root {{
  --bg:#f6f1ea; --bg2:#efe7dd; --card:#fffdf9; --ink:#2a2420; --muted:#8c8177; --line:#e9e0d5;
  --btn:#2a2420; --btn-ink:#fffdf9; --accent:#b8775f; --ring:#ffffff; --shadow:0 10px 30px rgba(74,58,44,.08);
  --serif:"Cormorant Garamond", Georgia, "Times New Roman", serif;
  --sans:Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --bg:#1a1614; --bg2:#211c19; --card:#241f1b; --ink:#f3ece4; --muted:#a2958a; --line:#332c27;
    --btn:#f3ece4; --btn-ink:#1a1614; --accent:#d69a80; --ring:#2e2723; --shadow:0 10px 30px rgba(0,0,0,.35);
  }}
}}
:root[data-theme="dark"] {{
  --bg:#1a1614; --bg2:#211c19; --card:#241f1b; --ink:#f3ece4; --muted:#a2958a; --line:#332c27;
  --btn:#f3ece4; --btn-ink:#1a1614; --accent:#d69a80; --ring:#2e2723; --shadow:0 10px 30px rgba(0,0,0,.35);
}}
* {{ box-sizing:border-box; }}
html,body {{ margin:0; }}
body {{ background:linear-gradient(180deg,var(--bg2) 0,var(--bg) 320px); color:var(--ink); font-family:var(--sans);
  -webkit-font-smoothing:antialiased; min-height:100vh; }}
.wrap {{ max-width:560px; margin:0 auto; padding:40px 16px 56px; }}

header {{ text-align:center; padding:0 0 26px; }}
.avatar {{ width:112px; height:112px; border-radius:50%; object-fit:cover; display:block; margin:0 auto;
  box-shadow:0 0 0 5px var(--ring), var(--shadow); }}
h1 {{ font-family:var(--serif); font-weight:600; font-size:38px; line-height:1; margin:20px 0 8px; letter-spacing:-.01em; }}
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
.hero h2 {{ font-family:var(--serif); font-size:26px; font-weight:600; margin:0 0 6px; line-height:1.15; }}
.hero p {{ margin:0 0 14px; color:var(--muted); font-size:14px; line-height:1.5; }}
.btn {{ display:inline-flex; align-items:center; gap:8px; background:var(--btn); color:var(--btn-ink); font-weight:500; font-size:13px;
  letter-spacing:.02em; padding:12px 18px; border-radius:999px; }}

.section {{ display:flex; align-items:baseline; justify-content:space-between; margin:30px 0 14px; }}
.section h3 {{ font-family:var(--serif); font-size:22px; font-weight:600; margin:0; }}
.section span {{ font-size:12px; color:var(--muted); }}
.grid {{ display:grid; grid-template-columns:1fr 1fr; gap:14px; }}
.card {{ background:var(--card); border-radius:18px; overflow:hidden; box-shadow:var(--shadow); text-decoration:none; color:inherit;
  display:flex; flex-direction:column; }}
.card .img {{ aspect-ratio:4/5; overflow:hidden; }}
.card img {{ width:100%; height:100%; object-fit:cover; display:block; transition:transform .6s ease; }}
.card:hover img {{ transform:scale(1.04); }}
.card .txt {{ padding:12px 13px 14px; display:flex; flex-direction:column; gap:5px; flex:1; }}
.card h4 {{ margin:0; font-size:14px; font-weight:600; line-height:1.3; }}
.card p {{ margin:0; font-size:12px; color:var(--muted); line-height:1.45; }}
.card .shop {{ margin-top:auto; padding-top:8px; font-size:12px; font-weight:600; color:var(--accent); letter-spacing:.04em; }}

.links {{ display:grid; gap:12px; }}
.link {{ display:flex; align-items:center; justify-content:center; gap:10px; background:var(--card); border:1px solid var(--line);
  border-radius:16px; padding:18px; text-decoration:none; color:var(--ink); font-weight:500; font-size:15px; box-shadow:var(--shadow); }}
.link svg {{ width:18px; height:18px; }}

.empty {{ text-align:center; color:var(--muted); padding:48px 0; font-family:var(--serif); font-size:20px; }}
footer {{ margin-top:44px; color:var(--muted); font-size:11.5px; line-height:1.6; text-align:center; }}
footer .heart {{ font-family:var(--serif); font-size:15px; color:var(--ink); margin-bottom:8px; }}
@media (max-width:360px) {{ .grid {{ gap:10px; }} h1 {{ font-size:34px; }} }}
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
    <div class="section" id="section-head" hidden><h3>All my picks</h3><span id="count"></span></div>
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
const today = new Date(); today.setHours(0,0,0,0);
const live = ITEMS.filter(i => new Date(i.date + "T00:00:00") <= today).sort((a,b) => b.date.localeCompare(a.date));
const esc = s => s.replace(/[&<>"]/g, c => ({{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}})[c]);
if (!live.length) {{
  document.getElementById("empty").hidden = false;
}} else {{
  const [first, ...rest] = live;
  document.getElementById("hero").innerHTML = `
    <a class="hero" href="${{first.url}}" target="_blank" rel="noopener sponsored">
      <div class="img"><img src="${{first.thumb_data}}" alt=""><span class="badge">New today</span></div>
      <div class="txt"><h2>${{esc(first.name)}}</h2><p>${{esc(first.sub)}}</p><span class="btn">Shop on Amazon <span aria-hidden="true">→</span></span></div>
    </a>`;
  if (rest.length) {{
    document.getElementById("section-head").hidden = false;
    document.getElementById("count").textContent = rest.length + (rest.length === 1 ? " more find" : " more finds");
    document.getElementById("grid").innerHTML = rest.map(i => `
      <a class="card" href="${{i.url}}" target="_blank" rel="noopener sponsored">
        <div class="img"><img src="${{i.thumb_data}}" alt="" loading="lazy"></div>
        <div class="txt"><h4>${{esc(i.name)}}</h4><p>${{esc(i.sub)}}</p><span class="shop">Shop on Amazon →</span></div>
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
open("index.html","w").write(html)
print(len(html)//1024, "KB")
