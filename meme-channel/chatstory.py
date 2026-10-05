"""Chat story engine for Peak ProMax shorts (fully original graphics + synthesized SFX).

A story is a dict (see stories.py): header, caption, theme and a script of steps.
Timing is automatic from text length so every line is readable.

Steps:
  ("msg", who, text)                         message; who == story["me"] is the right/blue side
  ("reply", who, text, qwho, qmeta, qtext)   message quoting an older one (qmeta like "Yesterday 3:12 AM")
  ("typing", who, seconds)                   typing bubble (heartbeat sfx)
  ("system", text)                           centered gray line ("Mike left the group")
  ("read", text)                             receipt under the last message ("Read 9:02 PM")
  ("unsend",)                                last message by me turns into "You unsent a message"
  ("react", emoji)                           reaction badge on the last message
  ("highlight", target)                      zoom + boom + red circle + arrow. target: "bubble", "quote", or a word
  ("stamp", text)                            final rubber stamp with boom
  ("sfx", name)                              extra sound now (bruh_horn, sad_trombone, kaching, ...)
  ("pause", seconds)
"""
import math

from PIL import Image, ImageDraw

import sfx
from anim import (back_out, camera, clamp, draw_rich, ease_out, emoji, font, paste_scaled, prog, red_arrow,
                  red_circle, render, stamp_img, text_w, wrap)

THEMES = {
    "light": dict(bg=(242, 242, 247), head=(250, 250, 252), line=(210, 210, 215), other=(229, 229, 234),
                  other_fg=(0, 0, 0), me=(10, 132, 255), me_fg=(255, 255, 255), quote=(0, 95, 210),
                  meta=(142, 142, 147), title=(0, 0, 0)),
    "dark": dict(bg=(0, 0, 0), head=(22, 22, 24), line=(50, 50, 54), other=(38, 38, 41),
                 other_fg=(255, 255, 255), me=(10, 132, 255), me_fg=(255, 255, 255), quote=(0, 95, 210),
                 meta=(142, 142, 147), title=(255, 255, 255)),
}
NAME_COLORS = [(255, 149, 0), (52, 199, 89), (175, 82, 222), (255, 45, 85), (90, 200, 250)]
F = font("RobotoCond.ttf", 60)
F_NAME = font("RobotoCond.ttf", 34)
F_QUOTE = font("RobotoCond.ttf", 40)
F_SYS = font("RobotoCond.ttf", 40)
MAXW = 720
HEAD = 150
_probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))


def read_time(text):
    return max(0.85, 0.5 + 0.036 * len(text))


class Story:
    def __init__(self, spec):
        self.s = spec
        self.th = THEMES[spec.get("theme", "light")]
        self.me = spec["me"]
        self.group = spec.get("group", False)
        names = [st[1] for st in spec["script"] if st[0] in ("msg", "reply", "typing") and st[1] != self.me]
        self.colors = {n: NAME_COLORS[i % len(NAME_COLORS)] for i, n in enumerate(dict.fromkeys(names))}
        self.msgs, self.events, self.audio = [], [], []
        self._compile()
        self._layout()
        self._scroll = {}

    # timeline
    def _compile(self):
        t = 0.6
        self.audio.append((0.1, sfx.whoosh(0.35), 0.6))
        for st in self.s["script"]:
            k = st[0]
            if k in ("msg", "reply", "system"):
                m = dict(kind=k, t=t, who=st[1] if k != "system" else "system",
                         text=st[2] if k != "system" else st[1])
                if k == "reply":
                    m["quote"] = st[3:6]
                self.msgs.append(m)
                if k == "system":
                    self.audio.append((t, sfx.pop(0.07, 900, 500), 0.6))
                elif m["who"] == self.me:
                    self.audio.append((t, sfx.pop(), 0.9))
                else:
                    self.audio.append((t, sfx.ding(990), 0.9))
                t += read_time(m["text"]) + (0.6 if k == "reply" else 0)
            elif k == "typing":
                self.events.append(dict(kind="typing", who=st[1], t0=t, t1=t + st[2]))
                self.audio.append((t, sfx.heartbeat(max(1, int(st[2] / 0.5)), 120), 0.8))
                t += st[2]
            elif k == "read":
                self.msgs[-1]["read"] = (t, st[1])
                self.audio.append((t, sfx.pop(0.06, 600, 900), 0.5))
                t += 1.1
            elif k == "unsend":
                m = [m for m in self.msgs if m["who"] == self.me][-1]
                m["unsent_at"] = t
                self.audio.append((t, sfx.whoosh(0.3), 0.8))
                t += 1.2
            elif k == "react":
                self.msgs[-1]["react"] = (t, st[1])
                self.audio.append((t, sfx.pop(0.08, 700, 1600), 0.8))
                t += 0.9
            elif k == "highlight":
                self.events.append(dict(kind="hl", msg=len(self.msgs) - 1, target=st[1], t=t))
                self.audio += [(t - 0.9, sfx.riser(0.9), 0.5), (t, sfx.boom(), 1.0), (t + 0.45, sfx.whoosh(0.3), 0.7)]
                t += 2.0
            elif k == "stamp":
                self.events.append(dict(kind="stamp", text=st[1], t=t))
                self.audio += [(t + 0.12, sfx.stamp(), 1.0), (t + 0.12, sfx.boom(), 0.9)]
                t += 2.2
            elif k == "sfx":
                fn = getattr(sfx, st[1])
                self.audio.append((t, fn(), 0.9))
                t += 0.3 if st[1] != "sad_trombone" else 1.4
            elif k == "pause":
                t += st[1]
        self.dur = t + 0.6

    def _layout(self):
        y = 40
        for i, m in enumerate(self.msgs):
            if m["kind"] == "system":
                w = text_w(_probe, m["text"], F_SYS)
                m.update(x=(1080 - w) / 2, y=y + 10, w=w, h=56, name_y=y)
                y += 96
                continue
            me = m["who"] == self.me
            lines = wrap(_probe, m["text"], F, MAXW)
            tw = max(text_w(_probe, ln, F) for ln in lines)
            bh = len(lines) * 72 + 40
            qh = 0
            if m.get("quote"):
                q = m["quote"]
                qw = max(text_w(_probe, q[2], F_QUOTE), _probe.textlength(f"{q[0]} · {q[1]}", font=F_NAME))
                tw = max(tw, min(qw, 900) + 100)
                qh = 140
            bw = min(tw + 56, 1000)
            prev = self.msgs[i - 1] if i else None
            show_name = self.group and not me and (not prev or prev["who"] != m["who"])
            name_h = 38 if show_name else 0
            x = 1080 - 40 - bw if me else 40
            m.update(me=me, lines=lines, x=x, y=y + name_h, w=bw, h=bh + qh, qh=qh, name_y=y, show_name=show_name)
            y += name_h + bh + qh + 18
            if m.get("read"):
                y += 44
            if m.get("react"):
                y += 30
        self.content_h = y
        for e in self.events:
            if e["kind"] == "hl":
                e["box"] = self._target_box(self.msgs[e["msg"]], e["target"])

    def _target_box(self, m, target):
        if m["kind"] == "system":
            return (m["x"] - 30, m["y"] - 12, m["x"] + m["w"] + 30, m["y"] + m["h"] + 6)
        if target == "quote":
            q = m["quote"]
            x = m["x"] + 40 + _probe.textlength(f"{q[0]} · ", font=F_NAME)
            return (x - 24, m["y"] + 12, x + _probe.textlength(q[1], font=F_NAME) + 24, m["y"] + 72)
        if target != "bubble":
            for j, ln in enumerate(m["lines"]):
                k = ln.find(target)
                if k >= 0:
                    x = m["x"] + 28 + text_w(_probe, ln[:k], F)
                    y = m["y"] + m["qh"] + 18 + j * 72
                    return (x - 22, y - 8, x + text_w(_probe, target, F) + 22, y + 82)
        return (m["x"] - 22, m["y"] - 16, m["x"] + m["w"] + 22, m["y"] + m["h"] + 16)

    # drawing
    def _bubble(self, im, m, t):
        p = prog(t, m["t"], 0.28)
        if p <= 0:
            return
        th = self.th
        if m["kind"] == "system":
            layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
            draw_rich(layer, (m["x"], m["y"]), m["text"], F_SYS, th["meta"] + (int(255 * clamp(p * 2)),))
            im.alpha_composite(layer)
            return
        if m.get("show_name"):
            ImageDraw.Draw(im).text((m["x"] + 22, m["name_y"]), m["who"], font=F_NAME, fill=self.colors[m["who"]])
        unsent = m.get("unsent_at") is not None and t >= m["unsent_at"]
        spr = Image.new("RGBA", (int(m["w"]), int(m["h"])), (0, 0, 0, 0))
        d = ImageDraw.Draw(spr)
        if unsent:
            d.rounded_rectangle((2, 2, m["w"] - 3, m["h"] - 3), radius=40, outline=th["meta"], width=4)
            s = "You unsent a message"
            d.text(((m["w"] - d.textlength(s, font=F_QUOTE)) / 2, (m["h"] - 50) / 2), s, font=F_QUOTE, fill=th["meta"])
        else:
            d.rounded_rectangle((0, 0, m["w"] - 1, m["h"] - 1), radius=40, fill=th["me"] if m["me"] else th["other"])
            fg = th["me_fg"] if m["me"] else th["other_fg"]
            y = 18
            if m.get("quote"):
                q = m["quote"]
                qc = th["quote"] if m["me"] else tuple(max(0, c - 25) for c in th["other"])
                d.rounded_rectangle((16, 14, m["w"] - 16, m["qh"]), radius=22, fill=qc)
                d.rectangle((16, 22, 24, m["qh"] - 8), fill=fg)
                d.text((40, 24), f"{q[0]} · {q[1]}", font=F_NAME, fill=fg + (190,) if len(fg) == 3 else fg)
                draw_rich(spr, (40, 66), q[2], F_QUOTE, fg)
                y += m["qh"]
            for ln in m["lines"]:
                draw_rich(spr, (28, y), ln, F, fg)
                y += 72
        s = back_out(clamp(p))
        sw, sh = max(1, int(spr.width * s)), max(1, int(spr.height * s))
        spr = spr.resize((sw, sh), Image.BICUBIC)
        ax = m["x"] + m["w"] if m["me"] else m["x"]
        im.alpha_composite(spr, (int(ax - sw if m["me"] else ax), int(m["y"] + m["h"] - sh)))
        if m.get("react") and t >= m["react"][0]:
            rp = back_out(prog(t, m["react"][0], 0.3))
            badge = Image.new("RGBA", (96, 96), (0, 0, 0, 0))
            ImageDraw.Draw(badge).ellipse((0, 0, 95, 95), fill=th["other"], outline=th["bg"], width=6)
            badge.alpha_composite(emoji(m["react"][1], 56), (20, 18))
            cx = m["x"] + 30 if m["me"] else m["x"] + m["w"] - 30
            paste_scaled(im, badge, (cx, m["y"] + m["h"] + 6), rp)
        if m.get("read") and t >= m["read"][0]:
            txt = m["read"][1]
            a = int(255 * clamp(prog(t, m["read"][0], 0.3)))
            layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
            ImageDraw.Draw(layer).text((m["x"] + m["w"] - _probe.textlength(txt, font=F_NAME) - 10,
                                        m["y"] + m["h"] + 6), txt, font=F_NAME, fill=th["meta"] + (a,))
            im.alpha_composite(layer)

    def _typing(self, im, y, who, t0, t):
        d = ImageDraw.Draw(im)
        if self.group:
            d.text((62, y), who, font=F_NAME, fill=self.colors.get(who, (150, 150, 150)))
            y += 38
        d.rounded_rectangle((40, y, 200, y + 84), radius=40, fill=self.th["other"])
        for k in range(3):
            a = 0.5 + 0.5 * math.sin((t - t0) * 9 - k * 0.9)
            r = 9 + 3 * a
            cx, cy = 82 + k * 38, y + 42 - 6 * a
            g = int(110 + 60 * a)
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(g, g, g))

    def _bottom(self, t):
        b = 0
        for m in self.msgs:
            if t >= m["t"]:
                b = m["y"] + m["h"] + (50 if m.get("read") and t >= m["read"][0] else 0)
        for e in self.events:
            if e["kind"] == "typing" and e["t0"] <= t < e["t1"]:
                b += 18 + 84 + (38 if self.group else 0)
        return b

    def _smooth_scroll(self, t, h):
        target = max(0, self._bottom(t) + 70 - h)
        key = round(t * 30)
        prev = self._scroll.get(key - 1, target)
        val = prev + (target - prev) * 0.25
        self._scroll[key] = val
        return val

    def _header(self, im, w):
        th = self.th
        d = ImageDraw.Draw(im)
        d.rectangle((0, 0, w, HEAD), fill=th["head"])
        d.line((0, HEAD, w, HEAD), fill=th["line"], width=2)
        d.ellipse((w / 2 - 36, 12, w / 2 + 36, 84), fill=(190, 190, 200))
        im.alpha_composite(emoji(self.s.get("avatar", "🙂"), 44), (int(w / 2 - 22), 26))
        title = self.s["chat"] + "  >"
        tf = font("RobotoCond.ttf", 34)
        draw_rich(im, ((w - text_w(d, title, tf)) / 2, 92), title, tf, th["title"])
        d.text((34, 40), "<", font=font("RobotoCond.ttf", 60), fill=th["me"])

    def content(self, t, w, h):
        th = self.th
        im = Image.new("RGBA", (w, h), th["bg"] + (255,))
        chat_h = h - HEAD
        scroll = self._smooth_scroll(t, chat_h)
        chat = Image.new("RGBA", (w, int(max(chat_h, self.content_h) + 400)), th["bg"] + (255,))
        for m in self.msgs:
            self._bubble(chat, m, t)
        for e in self.events:
            if e["kind"] == "typing" and e["t0"] <= t < e["t1"]:
                last = [m for m in self.msgs if m["t"] <= t]
                y = (last[-1]["y"] + last[-1]["h"] + 18) if last else 40
                self._typing(chat, y, e["who"], e["t0"], t)
        zoom, focus, shake, flash = 1.0, None, 0.0, False
        for e in self.events:
            if e["kind"] == "hl" and t >= e["t"]:
                box = e["box"]
                red_circle(chat, box, prog(t, e["t"], 0.4), width=10)
                if t < e["t"] + 2.0:
                    tip = ((box[0] + box[2]) / 2 + 40, box[1] - 4)
                    red_arrow(chat, tip, -60, 190, prog(t, e["t"] + 0.45, 0.3), width=18)
                z = ease_out(prog(t, e["t"] - 0.1, 0.25)) - ease_out(prog(t, e["t"] + 1.6, 0.35))
                if z > 0:
                    zoom = 1 + 0.65 * z
                    focus = ((box[0] + box[2]) / 2, HEAD + (box[1] + box[3]) / 2 - scroll)
                shake = max(shake, 16 * max(0, 1 - (t - e["t"]) / 0.45))
                flash = flash or e["t"] <= t < e["t"] + 0.08
        view = chat.crop((0, int(scroll), w, int(scroll) + chat_h))
        im.alpha_composite(view, (0, HEAD))
        self._header(im, w)
        for e in self.events:
            if e["kind"] == "stamp" and t >= e["t"]:
                g = im.convert("L").convert("RGBA")
                im = Image.blend(im, g, 0.55 * ease_out(prog(t, e["t"], 0.3)))
                p = prog(t, e["t"], 0.18)
                if "sprite" not in e:
                    e["sprite"] = stamp_img(e["text"], size=140, angle=-10)
                paste_scaled(im, e["sprite"], (w / 2, h * 0.5), 2.4 - 1.4 * ease_out(p), alpha=clamp(p * 3))
                shake = max(shake, 24 * max(0, 1 - (t - e["t"] - 0.15) / 0.5))
                flash = flash or e["t"] + 0.12 <= t < e["t"] + 0.2
        if flash:
            im = Image.blend(im, Image.new("RGBA", im.size, (255, 255, 255, 255)), 0.5)
        return camera(im, zoom, focus, shake)

    def render(self, out):
        music = sfx.beat_loop(self.dur, bpm=self.s.get("bpm", 100))
        for e in self.events:
            if e["kind"] == "hl":
                a, b = int((e["t"] - 0.1) * sfx.SR), int((e["t"] + 1.9) * sfx.SR)
                music[a:b] *= 0.2
            if e["kind"] == "stamp":
                music[int(e["t"] * sfx.SR):] *= 0.15
        cap = self.s["caption"]
        return render(out, self.dur, lambda t: cap, self.content, self.audio, music)
