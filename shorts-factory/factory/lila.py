"""Snapshot Serengeti (LILA BC) source adapter.

Data: Snapshot Serengeti seasons 1-11, released by the Snapshot Serengeti
team via LILA BC under the Community Data License Agreement, Permissive 1.0
(commercial use and modification allowed). Images are fetched directly from
the public Google Cloud Storage bucket.
"""
import concurrent.futures as cf
import json
import os
import urllib.request
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.environ.get("SHORTS_CACHE", os.path.join(os.path.expanduser("~"), ".cache", "yasaeng-cctv"))
GCS = "https://storage.googleapis.com/public-datasets-lila/"
IMG_BASE = GCS + "snapshotserengeti-unzipped/"
META = GCS + "snapshotserengeti-v-2-0/"

CREDIT = ("Snapshot Serengeti (Swanson et al. 2015, Scientific Data), via LILA BC, "
          "licensed CDLA-Permissive-1.0")
LICENSE_URL = "https://cdla.dev/permissive-1-0/"


def _get(url, out, tries=4):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    if os.path.exists(out) and os.path.getsize(out) > 0:
        return out
    last = None
    for _ in range(tries):
        try:
            tmp = out + ".part"
            with urllib.request.urlopen(url, timeout=120) as r, open(tmp, "wb") as f:
                while True:
                    b = r.read(1 << 20)
                    if not b:
                        break
                    f.write(b)
            os.replace(tmp, out)
            return out
        except Exception as e:  # network hiccup: retry
            last = e
    raise last


def image(rel):
    """Local path of a Serengeti image (downloaded once, then cached)."""
    return _get(IMG_BASE + rel, os.path.join(CACHE, "img", rel.replace("/", "__")))


def prefetch(rels, workers=16):
    with cf.ThreadPoolExecutor(workers) as ex:
        return list(ex.map(image, rels))


# ------------------------------------------------------------------ metadata
def metadata_tables():
    """Download (once) and load annotation / image / bbox tables as pandas.
    ~370 MB download, ~1 GB on disk; only needed for mining new stories."""
    import pandas as pd
    d = os.path.join(CACHE, "meta")
    pk_a, pk_i, pk_b = (os.path.join(d, n) for n in ("ann.pkl", "img.pkl", "bbox.pkl"))
    if not (os.path.exists(pk_a) and os.path.exists(pk_i)):
        z = _get(META + "SnapshotSerengeti_S1-11_v2_1.csv.zip", os.path.join(d, "ss_v2_1.csv.zip"))
        with zipfile.ZipFile(z) as zf:
            zf.extractall(d)
        pd.read_csv(os.path.join(d, "SnapshotSerengeti_v2_1_annotations.csv"), index_col=0,
                    low_memory=False).to_pickle(pk_a)
        pd.read_csv(os.path.join(d, "SnapshotSerengeti_v2_1_images.csv"), index_col=0).to_pickle(pk_i)
    if not os.path.exists(pk_b):
        j = _get(META + "SnapshotSerengetiBboxes_20190409.json", os.path.join(d, "bboxes.json"))
        b = json.load(open(j))
        rows = []
        size = {im["file_name"]: (im["width"], im["height"]) for im in b["images"]}
        for an in b["annotations"]:
            fn = an["image_id"] + ".JPG"
            w, h = size.get(fn, (2048, 1536))
            x, y, bw, bh = an["bbox"]
            rows.append((fn, an["category_id"], x / w, y / h, (x + bw) / w, (y + bh) / h))
        pd.DataFrame(rows, columns=["file", "cat", "x0", "y0", "x1", "y1"]).to_pickle(pk_b)
    return pd.read_pickle(pk_a), pd.read_pickle(pk_i), pd.read_pickle(pk_b)


class Index:
    """Query helper over the Serengeti tables (sorted indexes -> fast lookups)."""

    def __init__(self):
        ann, img, bbox = metadata_tables()
        self.ann = ann
        self._a = ann.set_index("capture_id").sort_index()
        self._i = img.set_index("capture_id").sort_index()
        self._b = bbox.set_index("file").sort_index()

    def frames(self, cid):
        try:
            r = self._i.loc[[cid]].sort_values("image_rank_in_capture")
        except KeyError:
            return []
        return list(r.image_path_rel)

    def boxes(self, rel):
        try:
            r = self._b.loc[[rel]]
        except KeyError:
            return []
        return r[["x0", "y0", "x1", "y1"]].values.round(4).tolist()

    def capture(self, cid):
        try:
            rows = self._a.loc[[cid]]
        except KeyError:
            raise KeyError(cid)
        r = rows.iloc[0]
        fr = self.frames(cid)
        return {
            "cap": cid,
            "site": r.site,
            "season": r.season,
            "date": r.capture_date_local,
            "time": r.capture_time_local,
            "species": sorted(set(rows.question__species.astype(str))),
            "count": str(r.question__count_max),
            "frames": fr,
            "boxes": [self.boxes(f) for f in fr],
        }


def shot_from_capture(info, frames=None):
    """Compact, self-contained shot description stored in story files so that
    rendering never needs the big metadata tables."""
    idx = frames if frames is not None else list(range(len(info["frames"])))
    return {
        "cap": info["cap"],
        "site": info["site"],
        "date": info["date"],
        "time": info["time"],
        "frames": [info["frames"][i] for i in idx],
        "boxes": [info["boxes"][i] for i in idx],
    }
