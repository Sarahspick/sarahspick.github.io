"""z3: 2006 Mr. Olympia, Jay Cutler beats Ronnie Coleman, who was going for a record ninth title. Jay: "I didn't beat
the best Ronnie Coleman ever... I just was better that day... I felt bad winning". Ronnie: "I thought it was pretty
much automatic that I was going to win number nine". Segment rk3 of the documentary (plans11/ronnie.py).
Run: python3 plans11/build_z3.py && python3 pipeline/bench.py plans11/z3_jay_beats_ronnie.json
"""
import sys

sys.path.insert(0, "plans11")
from ronnie import Doc  # noqa: E402

d = Doc("z3_jay_beats_ronnie", "\"I didn't beat the\n*best* Ronnie\" :broken-heart:",
        "Jay Cutler: I didn't beat the best Ronnie 💔 #shorts", "rk3")
# 1. hook, Jay: "I didn't beat the best Ronnie Coleman ever."
d.say(4077.18, 4078.78, gap=0.0, hit=4077.54)
# 2. "Ronnie was going for nine and didn't get nine. Jay Cutler beat him."
d.say(3979.3, 3984.0, hit=3983.72)
# 3. the announcer: "...the 2006 Mr. Olympia, Jay Cutler."
d.say(3986.74, 3993.6, hit=3990.24)
# 4. Ronnie: "I thought it was pretty much automatic that I was going to win number nine because I had won eight in a row"
d.say(4030.86, 4035.94)                                             # through "row"
# 5. Jay: "that wasn't Ronnie at his best. The injuries had shown up" ... "I just was better that day."
d.say(4069.38, 4073.38)
d.say(4084.82, 4085.76)
# 6. Jay: "But I felt bad for Ronnie. I felt bad winning"
d.say(4091.94, 4094.24, hit=4093.86, tail=0.6)
d.save(force={"best", "nine", "beat", "cutler", "automatic", "eight", "injuries", "better", "bad"})
