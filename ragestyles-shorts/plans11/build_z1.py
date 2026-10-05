"""z1: Ronnie Coleman and Kevin Levrone's vodka. Kevin kept winning; Ronnie, burnt out and carrying his weighed food
everywhere, knocked on his hotel door to ask the trick. Kevin: "You got to just relax, Ronnie", poured coffee and
vodka; Ronnie: "I don't drink no alcohol... bodybuilders can't do that"; by the fifth shot "this stuff pretty good";
next morning backstage Kevin's "jaw just dropped"; Ronnie: "I drank that coffee and that vodka and I went to the show
the next day and beat Kevin." Segment rk1 of the documentary (plans11/ronnie.py).
Run: python3 plans11/build_z1.py && python3 pipeline/bench.py plans11/z1_ronnie_vodka.json
"""
import sys

sys.path.insert(0, "plans11")
from ronnie import Doc  # noqa: E402

d = Doc("z1_ronnie_vodka", "Kevin Levrone gave\nRonnie *vodka* :exploding-head:",
        "Kevin Levrone gave Ronnie Coleman vodka 🤯 #shorts", "rk1")
# 1. hook, Kevin: "I looked at him, dude, and my jaw just dropped."
d.say(2920.0, 2923.0, gap=0.0, hit=2922.46)
# 2. Ronnie: "I remember Kevin is winning every show and I'm like, what the hell is he doing to win all these shows?"
d.say(2788.38, 2793.68)
# 3. Kevin: "You got to just relax, Ronnie."
d.say(2828.38, 2829.66)
# 4. "...pulls out a bottle of vodka" ... "and he says, drink that."
d.say(2839.5, 2841.08, hit=2840.62)
d.say(2846.04, 2848.56)
# 5. Ronnie: "I'm like, I don't drink no alcohol, Kevin." ... "Bodybuilders can't do that."
d.say(2850.28, 2852.38)
d.say(2854.48, 2855.24)
# 6. Kevin: "So about a fifth shot, he's like, man, this stuff pretty good. Let me have another shot of that."
t = d.say(2894.26, 2899.1)
d.big(t + 0.2, 1.5, "*5 SHOTS* LATER :face-with-steam-from-nose:")
# 7. Ronnie: "I drank that coffee and that vodka and I went to the show the next day and beat Kevin."
d.say(2928.4, 2933.68, hit=2933.42, tail=0.6)
d.save(force={"jaw", "dropped", "winning", "relax", "vodka", "drink", "alcohol", "shot", "beat", "kevin"})
