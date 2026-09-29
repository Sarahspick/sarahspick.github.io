"""Dailymotion search (public API) for footage hunting.   python tools/dm_search.py "query" ..."""
import sys
import requests

for q in sys.argv[1:]:
    r = requests.get("https://api.dailymotion.com/videos", params={
        "search": q, "limit": 12, "sort": "relevance",
        "fields": "id,title,duration,owner.screenname,views_total,height"}, timeout=20)
    print(f"\n## {q}")
    for v in r.json().get("list", []):
        print(f"dm:{v['id']:10} {v['duration']:5}s {str(v.get('views_total')):>8}v {str(v.get('height')):>5}p  {v['owner.screenname'][:18]:18}  {v['title'][:80]}")
