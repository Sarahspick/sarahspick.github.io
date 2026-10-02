#!/usr/bin/env bash
# Batch YouTube download for RageStyles sources.  Run from the repo root (matches the allow rule in .claude/settings.json):
#   bash ragestyles-shorts/tools/yt_batch.sh links.txt
#   bash ragestyles-shorts/tools/yt_batch.sh https://youtu.be/<id> <id> ...
# If YT_COOKIES_B64 (base64 of a spare account's cookies.txt) is set, it is decoded into a private temp file for
# --cookies and deleted on exit.  Cookie contents are never printed.  Output: ragestyles-shorts/work/youtube/<id>.mp4
set -euo pipefail
here="$(cd "$(dirname "$0")/.." && pwd)"

urls=()
for a in "$@"; do
  if [[ -f "$a" ]]; then
    while IFS= read -r line; do
      line="${line%%#*}"; line="$(echo "$line" | xargs)"
      [[ -n "$line" ]] && urls+=("$line")
    done < "$a"
  else
    urls+=("$a")
  fi
done
if [[ ${#urls[@]} -eq 0 ]]; then
  echo "usage: bash ragestyles-shorts/tools/yt_batch.sh <links.txt | URL ...>" >&2; exit 2
fi

cd "$here"
mkdir -p work/youtube
cookie_args=()
cookie_file=""
cleanup() { [[ -n "$cookie_file" ]] && rm -f "$cookie_file"; }
trap cleanup EXIT INT TERM
if [[ -n "${YT_COOKIES_B64:-}" ]]; then
  cookie_file="$(mktemp)"
  chmod 600 "$cookie_file"
  if ! printf '%s' "$YT_COOKIES_B64" | base64 -d > "$cookie_file" 2>/dev/null; then
    echo "YT_COOKIES_B64 is not valid base64" >&2; exit 1
  fi
  cookie_args=(--cookies "$cookie_file")
  echo "using cookies from YT_COOKIES_B64 ($(grep -c 'youtube.com' "$cookie_file" || true) youtube lines)"
fi

# yt-dlp needs node >= 22 for the n challenge; prefer /opt/node22 if the PATH node is older
node_bin="$(command -v node || true)"
[[ -x /opt/node22/bin/node ]] && node_bin=/opt/node22/bin/node
js_args=()
[[ -n "$node_bin" ]] && js_args=(--js-runtimes "node:$node_bin")

export YT_OUT="work/youtube/%(id)s.%(ext)s"
# optional: YT_SECTIONS="*1200-1813" downloads only that part (long videos get 403 on the full stream, 2026-10-02);
# YT_FORMAT overrides the format string
extra=()
[[ -n "${YT_SECTIONS:-}" ]] && extra+=(--download-sections "$YT_SECTIONS" --force-keyframes-at-cuts)
[[ -n "${YT_CLIENT:-}" ]] && extra+=(--extractor-args "youtube:player_client=$YT_CLIENT")   # e.g. tv, mweb, web_safari
fmt="${YT_FORMAT:-bv*[height<=1080][vcodec^=avc1]+ba[ext=m4a]/bv*[height<=1080][ext=mp4]+ba[ext=m4a]/bv*[height<=1080]+ba/b[height<=1080]/b}"
printf '%s\n' "${urls[@]}" | xargs -P 3 -I{} yt-dlp "${cookie_args[@]}" "${js_args[@]}" "${extra[@]}" -N 8 --no-progress --no-overwrites \
  -f "$fmt" \
  --merge-output-format mp4 --write-info-json -o "$YT_OUT" {} \
  || echo "some downloads failed (if every one says 'Sign in to confirm', the server IP or cookies are blocked)" >&2
ls -la work/youtube | tail -n +2
