"""Word-by-word captions from whisper word timestamps (the motivational "Peakz" look: 1 to 3 words on screen,
one keyword per group in a rotating neon colour, soft glow; style "word" in bench.py).

words: [(start, end, "word"), ...] in OUTPUT seconds (already shifted onto the short's timeline).
    caps = word_captions(words, y=0.5)
Keywords: numbers, money, a strong-word list, else the longest non-stopword of 5+ letters. Owner can force or
block colouring with force={"olympia"} / skip={"guys"}.
"""
import re

STOP = set("""a an and are as at be been but by can could did do does don't for from had has have he her him his
i i'm i'll if in is it it's its just me my of off on or our out so that the their them then there these they this
to too up was we were what when where which who will with would you you're your yourself yeah bro gonna want
wanna say said told saw every time any ever tell people""".split())
STRONG = set("""never lift floor woman kids car accident muscle fibers fight flight win won winner champion olympia
confidence believe negativity lesson tonight mutant title dream hate haters doubters strongest record""".split())
PALETTE = ["~", "^", "+", "%", "*"]  # red, green, cyan, purple, yellow


def clean(w):
    w = w.strip().replace("\u2019", "'")
    return w if w.lower() in ("mr.", "mrs.", "dr.") else w.strip(".,!?\"")


BREAK_BEFORE = set("and but if so because when then i'm i i'll you you're don't".split())
NO_END = set("a an the to of in on at for mr mr. mrs mrs. my your every any".split())
NO_START = set("it me that this too".split())


def groups(words, max_words=3, max_chars=16, gap=0.32):
    """Greedy phrase grouping: break on pauses, punctuation, a full group, or before a clause word (and, if,
    I'm, you...). Never end a group on an article or preposition (the, to, Mr.), never start one on it/me/that."""
    out, cur = [], []
    for s, e, w in words:
        c = clean(w).lower()
        if cur:
            prev = clean(cur[-1][2]).lower()
            chars = sum(len(clean(x[2])) for x in cur) + len(c)
            pause = s - cur[-1][1] > gap or re.search(r"[.,!?]$", cur[-1][2].strip())
            brk = pause or len(cur) >= max_words or chars > max_chars or c in BREAK_BEFORE
            if brk and (prev in NO_END and s - cur[-1][1] < 1.2) or (
                    brk and not pause and c in NO_START and len(cur) <= max_words):
                brk = False
            if brk:
                out.append(cur)
                cur = []
        cur.append((s, e, w))
    if cur:
        out.append(cur)
    # merge lone words: a function word joins the next group, any other word joins the previous one
    merged = []
    i = 0
    while i < len(out):
        g = out[i]
        if len(g) == 1 and i + 1 < len(out) and clean(g[0][2]).lower() in STOP and len(out[i + 1]) < 4 \
                and out[i + 1][0][0] - g[0][1] < 0.8:
            out[i + 1] = g + out[i + 1]
        elif len(g) == 1 and merged and len(merged[-1]) < 4 and g[0][0] - merged[-1][-1][1] < 0.6 \
                and clean(g[0][2]).lower() not in STRONG:
            merged[-1] = merged[-1] + g
        else:
            merged.append(g)
        i += 1
    return merged


def keyword(grp, force=(), skip=()):
    best, score = None, 0
    for i, (_, _, w) in enumerate(grp):
        c = clean(w).lower()
        if not c or c in skip:
            continue
        sc = 0
        if c in force:
            sc = 100
        elif re.search(r"\d", c) or c.startswith("$"):
            sc = 90
        elif c in STRONG:
            sc = 80
        elif c not in STOP and len(c) >= 5:
            sc = len(c)
        if sc > score:
            best, score = i, sc
    return best


def word_captions(words, y=0.5, force=(), skip=(), hold=0.25, style="word"):
    gs = groups(words)
    caps, k = [], 0
    for gi, g in enumerate(gs):
        ki = keyword(g, set(force), set(skip))
        toks = []
        for i, (_, _, w) in enumerate(g):
            c = clean(w).upper()
            if i == ki:
                mark = PALETTE[k % len(PALETTE)]
                c = f"{mark}{c}{mark}"
            toks.append(c)
        if ki is not None:
            k += 1
        t0 = g[0][0]
        nxt = gs[gi + 1][0][0] if gi + 1 < len(gs) else g[-1][1] + hold + 0.4
        t1 = min(nxt, g[-1][1] + hold + 0.6)
        caps.append({"t": round(t0, 2), "d": round(max(0.25, t1 - t0), 2), "text": " ".join(toks), "style": style,
                     "y": y, "anim": "pop"})
    return caps
