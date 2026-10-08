# START HERE: continuing RageStyles in a new Claude account (2026-10-08)

This folder holds the whole RageStyles shorts project: the editing pipeline, every edit plan, the owner's rules and
feedback, and the HQ masters. A new Claude session on another account can pick up exactly where the last one stopped
by reading the files below. The chat history itself cannot move between accounts; everything that mattered from it is
written down here.

## 1. Read in this order

1. `Downloads/CHANNEL_SUMMARY.txt`: what the channel covers, newest videos first, the current editing rules, and the
   new direction (bodybuilding legends + wider audience).
2. `HANDOFF.md`: the full handoff. Sections 2-4 and 3 (owner feedback, newest at the bottom) are the rules; section 5
   is the pipeline. Absolute rules are in section 2.
3. `plans11/build_*.py`: every recent edit, each with a docstring listing facts, sources and how it was cut.

## 2. Environment for the new account

Set these as environment secrets in the new Claude Code environment (values are the owner's; never print or commit
them): `YT_COOKIES_B64` (YouTube cookies.txt in base64), `ELEVENLABS_API_KEY`, `YT_CLIENT_ID`, `YT_CLIENT_SECRET`,
`YT_REFRESH_TOKEN_RS` (and the other `YT_REFRESH_TOKEN_*` if used). Then:

```
bash ragestyles-shorts/setup.sh --full      # render deps, models, core sources, SFX, smoke test
mkdir -p ragestyles-shorts/work/models && curl -L -o ragestyles-shorts/work/models/yunet.onnx \
  https://huggingface.co/opencv/face_detection_yunet/resolve/main/face_detection_yunet_2023mar.onnx
```

## 3. Sources are not in the repo (work/ is ignored)

Downloaded videos live in `work/youtube/` and must be fetched again before a plan can re-render.

* YouTube (`bash ragestyles-shorts/tools/yt_batch.sh <url>`), used by plans11: 0wGhJgjDAXU 1h_dZRyIkoo 8NRaqf9m5bA
  OrBoJkrn14Q SZvi5gYI-9A TWbA_Xw5BFM YVK2dN51a5o gGEMp9usg7g htrcV40AXSE jqUAJHdCVyM kF2FgCAfKgY pRWCqgRzN9c
  qpQ8iI8pJA8 tcDTdFKOXno. In the old cloud environment YouTube answered 403 for every video (server IP blocked even
  with fresh cookies); a new environment may get a working IP.
* archive.org (works without cookies, `curl -L`):
  * `https://archive.org/download/ronnie-coleman-the-king/Ronnie%20Coleman-%20The%20King.mp4` → `work/youtube/ia_ronnie_king.mp4`
  * `https://archive.org/download/youtube-WY7XPMThJ4Y/WY7XPMThJ4Y.webm` → remux with
    `ffmpeg -i in.webm -c copy -movflags +faststart work/youtube/ia_goggins_run.mp4`
* Demucs vocal stems and whisper word files (`work/youtube/*.wav`, `work/tr/*.json`) are rebuilt with the helper steps
  described in each build script's docstring (segment, Demucs `--two-stems vocals`, faster-whisper medium.en).

## 4. Where things stand

* Batches delivered: batch01 (7 videos, re-made 10-03 with pose to zoom countdowns and ElevenLabs SFX), batch02
  (5 videos: Samson Dauda, Larry Wheels, Sam Sulek sunrise were good; Max Searby and Tren Twins rejected), batch03
  (5 videos, 10-05: Goggins scalpel, Ronnie vodka, Ronnie 1998, Jay Cutler 2006, Ronnie 800 twice), owner feedback on
  batch03 not yet given.
* Upload text for each batch: `Downloads/batchNN/UPLOAD_ALL.txt`; HQ masters: `Downloads/hq/*_HQ.mp4`. In the new
  repo the download links become `https://github.com/<new account>/<repo>/raw/<branch>/ragestyles-shorts/Downloads/hq/<file>`.
* Owner wants: 5 to 7 videos per batch, one text file with title / description / tags / comment, HQ download links;
  bodybuilding legends (Ronnie Coleman, Jay Cutler callouts like "abs and thighs", Arnold, Dorian Yates, Kai Greene)
  and broader topics (Goggins, Joe Rogan) to grow past niche bodybuilding.

## 5. First message to paste into the new session

```
Read ragestyles-shorts/START_HERE.md, then Downloads/CHANNEL_SUMMARY.txt and HANDOFF.md, and continue the RageStyles
shorts work from where it stopped. Follow every rule in HANDOFF.md (faces centred and never cut, captions off faces,
ElevenLabs SFX only, no dashes in text, never print secrets).
```
