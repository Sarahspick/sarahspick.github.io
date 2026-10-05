"""z2: Ronnie Coleman's first Mr. Olympia, Madison Square Garden 1998. "My goal was just to place the top five";
fifth, sixth, fourth, third are called and he is still standing; "when he called out second place, he waited for a
long time... Flex Wheeler"; the famous "officer down" collapse; "you can't get no better feeling in the world than
that". Segment rk2 of the documentary (plans11/ronnie.py); the film's own 1998 stage footage runs under the voices.
Run: python3 plans11/build_z2.py && python3 pipeline/bench.py plans11/z2_ronnie_1998.json
"""
import sys

sys.path.insert(0, "plans11")
from ronnie import Doc  # noqa: E402

d = Doc("z2_ronnie_1998", "He only wanted\n*top 5* :face-screaming-in-fear:",
        "He only wanted top 5 at the Olympia 😱 #shorts", "rk2")
# 1. hook: "My goal was just to place the top five."
d.say(3161.26, 3162.52, t_in=3186.2, gap=0.0, hit=3162.34)            # Ronnie's own interview, face first
# 2. "And I remember they called, you know, like fifth and sixth, and I'm still standing there."
d.say(3168.04, 3172.86)
# 3. "Third, and I'm still standing there. I'm like, whoa."
d.say(3176.42, 3178.12, hit=3176.42)
# 4. "me and Flex standing there" ... "When he called out second place, he waited for a long time."
d.say(3180.46, 3181.74)
d.say(3188.78, 3192.84)
# 5. the announcer: "Flex Wheeler." (second place: Ronnie wins)
t = d.say(3196.12, 3196.56, hit=3196.12, tail=0.8)
d.big(t + 0.3, 1.0, "*RONNIE WINS* :trophy:")
# 6. "That's when he collapsed, of course. The famous Officer Down move that he did."
d.say(3205.86, 3210.86)
# 7. Ronnie: "To be at the top, the best in the whole world, that you can't get no better feeling in the world than that."
d.say(3229.44, 3235.62, hit=3234.5, tail=0.6)
d.save(force={"top", "five", "standing", "third", "flex", "wheeler", "collapsed", "officer", "best", "feeling"})
