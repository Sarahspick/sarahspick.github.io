# Wemby Shorts (YouTube Shorts fan channel test)

Channel direction: English, US audience, one player (Victor Wembanyama). Original graphics + openly licensed photos + AI voiceover, so every Short is our own work and stays eligible for YPP ads. No broadcast footage, no reuploads.

## Test #1: "Wemby is not normal" (24 s)

Build:
1. Photos from Wikimedia Commons into `WORK/img/` (see credits below), fonts Anton and Inter (Google Fonts) converted to `WORK/fonts/*.ttf`.
2. `python3 shorts/make_vo.py WORK "Victor Wembanyama is not a normal human. The average American man? Five foot nine. The average NBA player? Six foot six. Wemby? Seven foot four. His wingspan? Eight feet. That's longer than a king size bed. And last season, he became the youngest ever, and the first unanimous, Defensive Player of the Year. Follow for daily Wemby."`
3. `python3 shorts/wemby_height.py WORK WORK/wemby_test1.mp4` (needs `pip install imageio-ffmpeg pillow`, about 1 minute)

Facts used (checked 2026-09-30, Wikipedia / NBA.com): listed 7'4" (2.24 m), wingspan about 8'0", 2025-26 DPOY (youngest ever, first unanimous), 3.1 blocks per game, league leader in blocks 2024 to 2026. King size bed is 80 in (6'8") long.

### Upload copy
Title: `Wemby is NOT normal 👽 #shorts #nba #wembanyama`

Description:
```
How tall is Victor Wembanyama really? 7'4", 8 foot wingspan, and the first unanimous DPOY ever 👽

#wembanyama #wemby #nba #spurs #basketball

Photos (Wikimedia Commons):
Victor Wembanyama San Antonio Spurs 2024 by Frenchieinportland, CC BY 4.0, https://commons.wikimedia.org/wiki/File:Victor_Wembanyama_San_Antonio_Spurs_2024.jpg
Victor Wembanyama San Antonio Spurs 2025 NBA Cup by Daiei Onoguchi, CC BY 4.0, https://commons.wikimedia.org/wiki/File:Victor_Wembanyama_San_Antonio_Spurs_2025_NBA_Cup.jpg
Wembanyama and Hart, 2026 NBA Finals by The White House, public domain, https://commons.wikimedia.org/wiki/File:Wembanyama_and_Hart,_2026_NBA_Finals.png
Photos cropped, blurred and color graded. License: https://creativecommons.org/licenses/by/4.0/
Voiceover is AI generated. Fan channel, not affiliated with the NBA or the San Antonio Spurs.
```
Upload setting: turn on "Altered or synthetic content" disclosure only if required for realistic AI; an AI narrator over real facts does not need it, but say AI voice in the description as above.
