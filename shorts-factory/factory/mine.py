"""Story mining over the Snapshot Serengeti metadata.

Every finder returns capture ids and writes a contact sheet (3 frames per
capture, with a 10% coordinate grid) so a human or an LLM can pick shots and
focus boxes quickly.

  python make_shorts.py mine rare
  python make_shorts.py mine closeups leopard
  python make_shorts.py mine events
  python make_shorts.py mine site S5 P03
  python make_shorts.py mine fire
  python make_shorts.py mine sheet "SER_S2#G12#3#162" "SER_S5#P03#3#705"
"""
import os

import pandas as pd
from PIL import Image, ImageDraw

from . import lila
from . import text as T

OUT = os.path.join(os.getcwd(), "mining")
PRED = {"lionfemale", "lionmale", "cheetah", "leopard", "hyenaspotted"}
PREY = {"gazellethomsons", "gazellegrants", "wildebeest", "zebra", "impala", "warthog", "topi",
        "hartebeest", "buffalo"}
RARE = ["rhinoceros", "honeybadger", "zorilla", "caracal", "leopard", "aardwolf", "serval",
        "aardvark", "porcupine", "batearedfox", "civet", "genet", "wildcat"]


class Miner:
    def __init__(self):
        self.idx = lila.Index()
        a = self.idx.ann.copy()
        a["sp"] = a.question__species.astype(str).str.lower()
        self.a = a
        self.nimg = self.idx._i.groupby(level=0).size()
        b = self.idx._b.reset_index()
        b["frac"] = (b.x1 - b.x0) * (b.y1 - b.y0)
        per_file = b.groupby("file").frac.max()
        img = self.idx._i.reset_index().set_index("image_path_rel")
        caps = img.loc[img.index.intersection(per_file.index), "capture_id"]
        self.closeness = per_file.loc[caps.index].groupby(caps.values).max()

    # ---------------------------------------------------------- helpers
    def label(self, cid):
        r = self.a[self.a.capture_id == cid]
        if not len(r):
            return cid
        r0 = r.iloc[0]
        sps = ",".join(sorted(set(r.sp)))
        f = self.closeness.get(cid)
        fs = f" 크기={f:.2f}" if f is not None else ""
        return (f"{cid}  {sps} n={r0.question__count_max} {r0.capture_date_local} {r0.capture_time_local}"
                f"{fs} 확신={r0.p_users_identified_this_species}")

    def sheet(self, cids, name, thumb=(420, 315)):
        os.makedirs(OUT, exist_ok=True)
        font = T.font("medium", 18)
        rows = [(c, self.idx.frames(c)[:3]) for c in cids]
        lila.prefetch([r for _, fr in rows for r in fr])
        W, H = thumb[0] * 3, (thumb[1] + 26) * len(rows)
        S = Image.new("RGB", (W, max(H, 1)), (25, 25, 25))
        d = ImageDraw.Draw(S)
        for i, (c, fr) in enumerate(rows):
            y = i * (thumb[1] + 26)
            d.text((6, y + 3), f"[{i}] " + self.label(c), fill=(255, 220, 0), font=font)
            for j, rel in enumerate(fr):
                try:
                    im = Image.open(lila.image(rel)).convert("RGB").resize(thumb)
                except Exception:
                    continue
                g = ImageDraw.Draw(im)
                for k in range(1, 10):
                    x, yy = k * thumb[0] // 10, k * thumb[1] // 10
                    g.line([(x, 0), (x, thumb[1])], fill=(255, 255, 0))
                    g.line([(0, yy), (thumb[0], yy)], fill=(0, 255, 255))
                S.paste(im, (j * thumb[0], y + 26))
        path = os.path.join(OUT, name + ".jpg")
        S.save(path, quality=82)
        with open(os.path.join(OUT, name + ".txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(self.label(c) for c in cids))
        return path

    def _spread(self, s, n):
        return list(s.iloc[::max(1, len(s) // n)].capture_id)[:n] if len(s) > n else list(s.capture_id)

    # ---------------------------------------------------------- finders
    def rare(self, n=8, min_conf=0.8):
        out = {}
        for sp in RARE:
            s = self.a[(self.a.sp == sp) & (self.a.p_users_identified_this_species >= min_conf)]
            s = s.sort_values("p_users_identified_this_species", ascending=False)
            out[sp] = self._spread(s, n)
        return out

    def closeups(self, sp, n=8, lo=0.2, hi=0.9):
        caps = self.closeness[(self.closeness > lo) & (self.closeness < hi)]
        s = self.a[(self.a.sp == sp) & self.a.capture_id.isin(caps.index)
                   & (self.a.p_users_identified_this_species > 0.7)].copy()
        s["frac"] = s.capture_id.map(caps)
        return self._spread(s.sort_values("frac", ascending=False), n)

    def events(self, window_s=900, n=16):
        """prey then predator (or predator then hyena) at the same camera within window_s"""
        x = self.a[(self.a.p_users_identified_this_species >= 0.8) & (~self.a.sp.isin(["blank", "human", "fire"]))].copy()
        x["ts"] = pd.to_datetime(x.capture_date_local + " " + x.capture_time_local, errors="coerce")
        x = x.dropna(subset=["ts"]).sort_values(["season", "site", "ts"]).reset_index(drop=True)
        found = []
        for k in range(1, 6):
            nx = x.shift(-k)
            gap = (nx.ts - x.ts).dt.total_seconds()
            ok = (x.season == nx.season) & (x.site == nx.site) & (gap > 0) & (gap <= window_s)
            m = ok & ((x.sp.isin(PREY) & nx.sp.isin(PRED)) |
                      (x.sp.isin(PRED - {"hyenaspotted"}) & (nx.sp == "hyenaspotted")))
            found.append(pd.DataFrame({"a": x.capture_id[m], "b": nx.capture_id[m], "gap": gap[m]}))
        ev = pd.concat(found).drop_duplicates("b").sort_values("gap")
        ids = []
        for r in ev.head(n // 2).itertuples():
            ids += [r.a, r.b]
        return ids

    def site(self, season, site, min_conf=0.8):
        """best (closest) capture of every species seen by one camera in one season"""
        s = self.a[(self.a.season == season) & (self.a.site == site) & (self.a.p_users_identified_this_species >= min_conf)
                   & (~self.a.sp.isin(["blank", "human"]))].copy()
        s["frac"] = s.capture_id.map(self.closeness).fillna(0)
        best = s.sort_values("frac", ascending=False).groupby("sp").head(1)
        return list(best.sort_values(["capture_date_local", "capture_time_local"]).capture_id)

    def fire(self):
        f = self.a[self.a.sp == "fire"]
        groups = f.groupby(["site", "capture_date_local"]).capture_id.apply(list)
        return [v[len(v) // 2] for _, v in groups.sort_values(key=lambda s: -s.str.len()).items()][:12]


def cli(args):
    m = Miner()
    cmd = args[0] if args else "rare"
    if cmd == "rare":
        for sp, ids in m.rare().items():
            print(sp, m.sheet(ids, f"rare_{sp}"))
    elif cmd == "closeups":
        print(m.sheet(m.closeups(args[1]), f"closeups_{args[1]}"))
    elif cmd == "events":
        ids = m.events()
        for i in range(0, len(ids), 8):
            print(m.sheet(ids[i:i + 8], f"events_{i // 8}"))
    elif cmd == "site":
        ids = m.site(args[1], args[2])
        for i in range(0, len(ids), 8):
            print(m.sheet(ids[i:i + 8], f"site_{args[1]}_{args[2]}_{i // 8}"))
    elif cmd == "fire":
        print(m.sheet(m.fire()[:8], "fire"))
    elif cmd == "sheet":
        print(m.sheet(args[1:], "sheet"))
    else:
        raise SystemExit(__doc__)
