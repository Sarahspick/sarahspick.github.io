"""o5: did Samson Dauda lose the 2026 Mr. Olympia on day one?
Facts: Samson won the 2024 Mr. Olympia, fell to 4th in 2025 (Derek won, Hadi Choopan 2nd; fitnessvolt.com
2025-mr-olympia-bodybuilding-results, bleacherreport.com); 2026: 2nd, $200,000. Commentary (source seconds) 4170.5 "I think if Samson would have looked the way
he did tonight last night, there could have been a different result" (to 4176.0). The Olympia is judged over two
days (prejudging the night before the finals), which is what "last night" refers to. Run: python3 plans9/build_o5.py
"""
import sys

sys.path.insert(0, "plans9")
from olycommon import Short, REVEAL  # noqa: E402

o = Short("o5_olympia_2026_samson_day_one", "Did Samson lose\n*Mr. Olympia* on day 1? :thinking-face:",
          "Did Samson Dauda lose Mr. Olympia on day 1? 🤔 #shorts")

s = o.shot(3056.7 - 1.0, 3.6)
o.cap(0, 1.9, "SAMSON DAUDA :flag-gb:\n2024: *1ST* :trophy:")
o.cap(1.9, 1.7, "SAMSON DAUDA :flag-gb:\n2025: ~4TH~ :chart-decreasing:")
o.hit(s, 1.0, zoom=1.1, amount=0.35)
s = o.shot(4124.5, 2.6, db=-14, layout="blur", box_aspect=1.0, darken=0.45)
o.cap(s["_t0"], 2.6, "LAST ~2~ STANDING")
o.clip(4073.9, 2.6, s["_t0"])        # "if I can have Samson and Nick in the center"
s = o.shot(4131.0, 2.4, cx=0.62, db=-14, zoom=(1.0, 1.06))
o.cap(s["_t0"], 2.4, "SAMSON vs NICK")
o.clip(4121.9, 2.5, s["_t0"])        # "and the title of 2026 Mr. Olympia"
s = o.shot(REVEAL + 0.4, 2.8, cx=0.63, db=0, zoom=(1.05, 1.1))
o.cap(s["_t0"] + 0.2, 2.6, "2026: *2ND* :broken-heart:")
o.hit(s, 0.2, zoom=1.15, amount=0.5, big=True)
# the commentary over two more of Samson's routine poses
a = o.shot(3034.0, 2.8, db=-16)
b = o.shot(3084.0, 2.9, db=-16)
o.clip(4170.5, 5.5, a["_t0"] + 0.1)
o.cap(a["_t0"], 2.8, "IF HE LOOKED LIKE THIS\n*ON DAY 1*...")
o.cap(b["_t0"], 2.9, "~DIFFERENT RESULT?~ :thinking-face:")
s = o.shot(2997.5, 2.8, db=-16)  # Samson himself (the confetti hug is Andrew Jacked, green trunks)
o.cap(s["_t0"], 2.8, "STILL *$200,000* :money-bag:")
o.save()
