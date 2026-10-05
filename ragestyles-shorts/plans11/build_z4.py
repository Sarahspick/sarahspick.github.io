"""z4: Ronnie Coleman after his surgeries. So many back operations that the next one goes in through the front ("you
got to take out my intestines"); asked about it, his answer is "I'm really disappointed I only squatted 800 twice",
"I could've got five easy reps", then 2,300 lb on the leg press for eight. Segment rk4 of the documentary
(plans11/ronnie.py): Ronnie before surgery, Jay Cutler telling the line, Ronnie's own interview.
Run: python3 plans11/build_z4.py && python3 pipeline/bench.py plans11/z4_ronnie_800_twice.json
"""
import sys

sys.path.insert(0, "plans11")
from ronnie import Doc  # noqa: E402

d = Doc("z4_ronnie_800_twice", "His only regret?\n*800 lb* :skull:",
        "Ronnie Coleman's only regret 💀 #shorts", "rk4")
# 1. hook: "he goes, well, I'm really disappointed I only squatted 800 twice."
d.say(5236.44, 5240.24, gap=0.0, hit=5239.84)
# 2. Ronnie before surgery: "because I've had so many back surgeries ... you got to take out my intestines to get to
#    the back"
d.say(5122.26, 5123.42)
d.say(5132.58, 5136.7, t_in=5130.5, hit=5133.48)                     # walking in on crutches, face on
# 3. Jay: "Ronnie's not gonna cry about anything."
d.say(5220.76, 5223.0, t_in=5212.0)                                   # Jay on camera (from "Ronnie's")
# 4. Ronnie: "I think I could've got five with 800 ... five easy reps."
d.say(5248.66, 5250.66)
d.say(5253.3, 5255.18, hit=5254.6)
# 5. "and then I went to the leg press, and I put 2,300 on there, and I got eight reps. So I kinda made up for it there."
t = d.say(5260.8, 5267.2, hit=5263.18, tail=0.6)
d.big(t + 2.3, 2.0, "*2,300 LB* X 8 :exploding-head:")
d.save(force={"800", "twice", "surgeries", "intestines", "cry", "five", "easy", "2,300", "eight"})
