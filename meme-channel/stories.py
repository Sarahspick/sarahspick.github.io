"""The 10 Peak ProMax chat-story shorts.

Render all:   python3 stories.py
Render some:  python3 stories.py 01 05
Writes out/NN_slug.mp4 and out/shorts.json (titles, descriptions, tags for upload).
"""
import json
import os
import sys

from chatstory import Story

TAGS = ["#shorts", "#funny", "#memes", "#textingstory", "#relatable"]

STORIES = [
    dict(slug="01_pizza_twin", title="He really thought nobody would check the timestamp 💀",
         caption="Bro really thought he could lie in the group chat 😭🙏",
         chat="Apartment 4B", avatar="🏠", me="Jay", group=True, script=[
             ("msg", "Jay", "who ate my leftover pizza 🍕"),
             ("msg", "Sam", "not me"),
             ("msg", "Mike", "bro i was asleep by 10 last night 😴"),
             ("reply", "Jay", "then explain this 🤨", "Mike", "Yesterday 3:12 AM", "yo is the pizza in the fridge still good 👀"),
             ("highlight", "quote"),
             ("typing", "Mike", 1.4),
             ("msg", "Mike", "that was my twin"),
             ("msg", "Jay", "you don't have a twin"),
             ("msg", "Mike", "he's very private"),
             ("sfx", "bruh_horn"),
             ("system", "Mike left the group"),
             ("sfx", "sad_trombone"),
             ("stamp", "-1000 AURA"),
         ]),
    dict(slug="02_neighbor_wifi", title="Mom found out where the WiFi comes from 😭",
         caption="He was NOT ready for this conversation 😭",
         chat="Mom ❤️", avatar="👩", me="me", script=[
             ("msg", "Mom", "why is the internet bill $0 this month"),
             ("msg", "me", "i switched us to the neighbor's wifi 😎"),
             ("msg", "Mom", "the neighbors moved out in august"),
             ("typing", "me", 1.2),
             ("msg", "me", "wait then whose wifi are we on"),
             ("msg", "Mom", "you tell me. what's it called"),
             ("msg", "me", "FBI Surveillance Van 4 📶"),
             ("highlight", "FBI Surveillance Van 4"),
             ("msg", "Mom", "pack your things"),
             ("system", "Mom changed the WiFi password"),
             ("sfx", "sad_trombone"),
             ("stamp", "OFFLINE"),
         ]),
    dict(slug="03_sick_day", title="Calling in sick was a BAD idea 😭",
         caption="Bro forgot his boss follows him 😭🙏",
         chat="Boss (Mark)", avatar="👔", me="me", theme="dark", script=[
             ("msg", "Mark", "feeling any better? 🙂"),
             ("msg", "me", "still really sick, can barely get out of bed 🤒"),
             ("msg", "Mark", "oh no, hope you recover soon"),
             ("reply", "Mark", "front row seats though? 👀", "Your story", "2h ago", "FRONT ROW LETS GOOO 🎤🔥"),
             ("highlight", "quote"),
             ("typing", "me", 1.6),
             ("msg", "me", "that's an old video"),
             ("msg", "Mark", "the concert is literally tonight"),
             ("msg", "me", "the band is also sick"),
             ("msg", "Mark", "see you at 9am 🙂"),
             ("react", "😭"),
             ("stamp", "FIRED?"),
         ]),
    dict(slug="04_party_presence", title="He thought he was the main dish 😭",
         caption="Bro got humbled by his own friends 😭",
         chat="party saturday 🎉", avatar="🎉", me="Jay", group=True, script=[
             ("msg", "Ana", "ok who's bringing what"),
             ("msg", "Ben", "chips 🍟"),
             ("msg", "Chloe", "drinks 🥤"),
             ("msg", "Jay", "i'll bring my presence ✨"),
             ("reply", "Ana", "absolutely not", "Jay", "just now", "i'll bring my presence ✨"),
             ("msg", "Ben", "bring chips too"),
             ("system", "Ana renamed the group \"party saturday (no Jay)\""),
             ("highlight", "bubble"),
             ("sfx", "sad_trombone"),
             ("stamp", "-500 AURA"),
         ]),
    dict(slug="05_ai_essay", title="The AI did him dirty 💀",
         caption="Never trust AI with your homework 😭🙏",
         chat="AI Assistant", avatar="🤖", me="me", theme="dark", script=[
             ("msg", "me", "write my essay on the french revolution"),
             ("msg", "AI", "Sure! The French Revolution (1789) was a period of radical change..."),
             ("msg", "me", "make it sound like a 10th grader wrote it"),
             ("msg", "AI", "the french revolution was lowkey crazy fr 💀"),
             ("msg", "me", "perfect. submit it for me"),
             ("msg", "AI", "Done! I also cc'd your teacher so she knows I helped 😊"),
             ("highlight", "I also cc'd your teacher"),
             ("msg", "me", "WHY"),
             ("msg", "AI", "Honesty is important! 🙂"),
             ("sfx", "bruh_horn"),
             ("stamp", "CAUGHT"),
         ]),
    dict(slug="06_wrong_person", title="Shooting your shot in 2026 be like 😭",
         caption="He should've stopped at \"hey\" 😭",
         chat="Emma 🌸", avatar="🌸", me="me", script=[
             ("msg", "me", "hey 👋"),
             ("read", "Read 9:02 PM"),
             ("pause", 0.6),
             ("msg", "me", "so funny story"),
             ("msg", "me", "i meant to send that to someone else"),
             ("msg", "me", "wait that sounds worse"),
             ("typing", "Emma", 2.0),
             ("msg", "Emma", "who is this"),
             ("highlight", "bubble"),
             ("sfx", "sad_trombone"),
             ("stamp", "-2000 AURA"),
         ]),
    dict(slug="07_dad_car", title="Dad doing detective work 😭",
         caption="Never lie to a dad with a car 😭🙏",
         chat="Dad", avatar="👨", me="me", script=[
             ("msg", "Dad", "did you use the car last night"),
             ("msg", "me", "nope, home all night 🙏"),
             ("msg", "Dad", "ok"),
             ("pause", 0.5),
             ("msg", "Dad", "then why does it have 340 new miles"),
             ("highlight", "340"),
             ("msg", "me", "the car went on a self discovery trip"),
             ("msg", "Dad", "it also got a speeding ticket in Las Vegas"),
             ("sfx", "bruh_horn"),
             ("msg", "me", "what happens in vegas stays in vegas"),
             ("msg", "Dad", "you stay in your room. for a month."),
             ("stamp", "GROUNDED"),
         ]),
    dict(slug="08_landlord_goat", title="Bro said \"no pets\" with a goat in the house 😭",
         caption="The landlord has cameras bro 😭🙏",
         chat="Landlord (Greg)", avatar="🏠", me="me", script=[
             ("msg", "Greg", "friendly reminder: no pets allowed 🙂"),
             ("msg", "me", "of course! no pets here 🙏"),
             ("reply", "Greg", "then who is this", "Ring Doorbell", "7:41 AM", "Motion detected: goat at front door 🐐"),
             ("highlight", "quote"),
             ("msg", "me", "that's my roommate"),
             ("msg", "Greg", "your roommate is eating the doormat"),
             ("msg", "me", "he has a condition"),
             ("sfx", "sad_trombone"),
             ("stamp", "EVICTED"),
         ]),
    dict(slug="09_delivery", title="DoorDash plot twist nobody expected 😭",
         caption="The driver had other plans 😭",
         chat="Your Driver (Tony)", avatar="🚗", me="me", theme="dark", script=[
             ("msg", "Tony", "i'm outside 🚗"),
             ("msg", "me", "i don't see you"),
             ("msg", "Tony", "i'm by the red door"),
             ("msg", "me", "my door is blue"),
             ("typing", "Tony", 1.4),
             ("system", "Tony marked your order as Delivered ✅"),
             ("highlight", "bubble"),
             ("msg", "me", "WAIT where is my food"),
             ("msg", "Tony", "it was delicious 😋"),
             ("sfx", "bruh_horn"),
             ("stamp", "SCAMMED"),
         ]),
    dict(slug="10_family_chat", title="Grandma is built different 😭",
         caption="Wrong chat. Worst possible chat 😭🙏",
         chat="Family ❤️", avatar="👪", me="me", group=True, script=[
             ("msg", "Mom", "family dinner at 7 everyone"),
             ("msg", "Grandma", "ok sweetie ❤️"),
             ("msg", "me", "bro save me from this family dinner 😭"),
             ("pause", 0.4),
             ("unsend",),
             ("msg", "Mom", "too late. i saw it."),
             ("msg", "Grandma", "i screenshotted it ❤️"),
             ("highlight", "i screenshotted it"),
             ("msg", "Dad", "see you at 7 🙂"),
             ("react", "😂"),
             ("stamp", "COOKED"),
         ]),
]


def main(keys):
    os.makedirs("out", exist_ok=True)
    meta = []
    for s in STORIES:
        if keys and not any(s["slug"].startswith(k) for k in keys):
            continue
        out = f"out/{s['slug']}.mp4"
        Story(s).render(out)
        print(out)
    for s in STORIES:
        meta.append(dict(file=f"{s['slug']}.mp4", title=s["title"],
                         description=f"{s['title']}\n\nFollow Peak ProMax for daily peak content. {' '.join(TAGS)}"))
    with open("out/shorts.json", "w") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    with open("save_page.html") as f:
        page = f.read().replace("__SHORTS__", json.dumps(meta, ensure_ascii=False))
    with open("out/index.html", "w") as f:
        f.write(page)


if __name__ == "__main__":
    main(sys.argv[1:])
