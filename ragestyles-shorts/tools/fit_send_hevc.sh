#!/usr/bin/env bash
# High quality chat copy: two-pass HEVC (hvc1, plays on iPhone and uploads to YouTube) aimed just under the chat limit,
# audio copied. Use on a CRF 12 master (RS_CRF=12 RS_PRESET=veryslow RS_ABR=320k python3 pipeline/bench.py ...).
#   bash tools/fit_send_hevc.sh in.mp4 out.mp4 [target_mb=28]
set -euo pipefail
in="$1"; out="$2"; target_mb="${3:-28}"
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$in")
abr=$(ffprobe -v error -select_streams a -show_entries stream=bit_rate -of csv=p=0 "$in" | head -1)
vbr=$(python3 -c "print(min(16000, int(($target_mb*8e6*0.97/$dur - ${abr:-320000})/1000)))")
d=$(mktemp -d)
ffmpeg -loglevel error -y -i "$in" -c:v libx265 -preset slow -b:v ${vbr}k -x265-params pass=1:stats=$d/s.log:log-level=error -an -f mp4 /dev/null
ffmpeg -loglevel error -y -i "$in" -c:v libx265 -preset slow -b:v ${vbr}k -x265-params pass=2:stats=$d/s.log:log-level=error \
  -tag:v hvc1 -pix_fmt yuv420p -c:a copy -movflags +faststart "$out"
rm -rf "$d"
echo "hevc ${vbr} kbps, $(( $(stat -c %s "$out") / 1000000 )) MB"
