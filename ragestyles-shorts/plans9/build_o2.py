"""o2: three former Mr. Olympias against Nick Walker, and where each one finished.
Facts: Brandon Curry won 2019 (9th tonight), Derek Lunsford won 2023 and 2025 (3rd), Samson Dauda won 2024 (2nd),
Nick Walker had never won it (1st). Past winners: fitnessvolt.com/mr-olympia-champions-since-1965, Wikipedia;
placings: fitnessvolt.com/2026-mr-olympia-results and the stage announcements. Run: python3 plans9/build_o2.py
"""
import sys

sys.path.insert(0, "plans9")
from olycommon import Short, REVEAL, REVEAL_PATH  # noqa: E402

o = Short("o2_olympia_2026_former_champs", "3 former Mr. Olympias\nvs *Nick Walker* :fire:",
          "3 former Mr. Olympias vs Nick Walker 🔥 #shorts")

# Brandon Curry: front double biceps locks in at 2838.0, then his placing
s = o.shot(2838.0 - 1.0, 4.4)
o.cap(s["_t0"], 2.6, "BRANDON CURRY :flag-us:\n*2019 MR. OLYMPIA*")
o.cap(s["_t0"] + 2.6, 1.8, "TONIGHT: ~9TH~")
o.hit(s, 1.0, zoom=1.08, amount=0.3)
s["punch"][0]["until"] = 2.6
o.hit(s, 2.6)

# Derek Lunsford: back double biceps at 3513.7, then his bronze medal moment
s = o.shot(3513.7 - 1.0, 2.6)
o.cap(s["_t0"], 2.6, "DEREK LUNSFORD :flag-us:\n*2023 & 2025 MR. OLYMPIA*")
o.hit(s, 1.0, zoom=1.08, amount=0.3)
s = o.shot(4026.7, 2.8, cx=0.52, cy=0.45)
o.cap(s["_t0"], 2.8, "TONIGHT: ~3RD~ :3rd-place-medal:")
o.hit(s, 0.15)

# Samson Dauda: front double biceps at 3056.7, then his head drops when Nick is announced
s = o.shot(3056.7 - 1.0, 2.6)
o.cap(s["_t0"], 2.6, "SAMSON DAUDA :flag-gb:\n*2024 MR. OLYMPIA*")
o.hit(s, 1.0, zoom=1.08, amount=0.3)
s = o.shot(REVEAL + 0.4, 2.6, cx=0.63, db=0, zoom=(1.05, 1.1))
o.cap(s["_t0"], 2.6, "TONIGHT: ~2ND~ :2nd-place-medal:")
o.hit(s, 0.15)

# Nick Walker: front double biceps at 3297.0, then the announcement
s = o.shot(3297.0 - 1.0, 2.6)
o.cap(s["_t0"], 2.6, "NICK WALKER :flag-us:\n*NEVER WON IT*")
o.hit(s, 1.0, zoom=1.08, amount=0.3)
s = o.shot(REVEAL, 3.6, db=0, ease="linear", path=REVEAL_PATH)
o.cap(s["_t0"] + 0.6, 3.0, "TONIGHT: *1ST* :trophy:")
o.hit(s, 0.6, zoom=1.15, amount=0.55, big=True)
s = o.shot(4199.6, 3.2, cx=0.52, db=-10, zoom=(1.0, 1.06))  # Nick with the gold medal
o.cap(s["_t0"], 3.2, "HE BEAT ALL ~3~ :exploding-head:")
o.clip(4156.4, 2.9, s["_t0"] + 0.1)  # "he defeated three former Mr. Olympia"
o.save()
