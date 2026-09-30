#!/usr/bin/env bash
# Re-encode a finished short so it fits the chat file limit (SendUserFile, 30 MB) at the best quality that fits:
# two-pass x264 aimed at a target size, audio copied. Files already under the target are copied as they are.
#   bash ragestyles-shorts/tools/fit_send.sh in.mp4 out.mp4 [target_mb=29]
set -euo pipefail
in="$1"; out="$2"; target_mb="${3:-29}"
size=$(stat -c %s "$in")
if (( size <= target_mb * 1000000 )); then cp "$in" "$out"; echo "copied ($((size / 1000000)) MB)"; exit 0; fi
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$in")
abr=$(ffprobe -v error -select_streams a -show_entries stream=bit_rate -of csv=p=0 "$in" | head -1)
abr=${abr:-192000}
# total bits * 0.97 (container overhead) minus audio, per second
vbr=$(python3 -c "print(int(($target_mb*8e6*0.97/$dur - $abr)/1000))")
log=$(mktemp -d)
ffmpeg -loglevel error -y -i "$in" -c:v libx264 -preset slow -b:v ${vbr}k -pass 1 -passlogfile "$log/p" -an -f mp4 /dev/null
ffmpeg -loglevel error -y -i "$in" -c:v libx264 -preset slow -b:v ${vbr}k -maxrate $((vbr * 2))k -bufsize $((vbr * 2))k \
  -pass 2 -passlogfile "$log/p" -pix_fmt yuv420p -c:a copy -movflags +faststart "$out"
rm -rf "$log"
echo "video ${vbr} kbps, $(( $(stat -c %s "$out") / 1000000 )) MB"
