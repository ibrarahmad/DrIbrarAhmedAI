#!/usr/bin/env python3
"""collect_youtube.py — pull real YouTube signals into data/videos.csv.

Computes view_velocity = views / age_days, which surfaces what's actually
moving (raw views lie — speed matters).

Live mode needs YOUTUBE_API_KEY. With no key, the bundled sample
data/videos.csv is kept and reused so the whole pipeline still runs offline.

    python3 collect_youtube.py --query "AI agents" --days 60 --limit 50
"""
from __future__ import annotations
import argparse, csv, os, sys
from datetime import datetime, timedelta, timezone

DATA = os.path.join(os.path.dirname(__file__), "data", "videos.csv")
FIELDS = ["title", "channel", "views", "age_days", "likes",
          "comments", "duration", "view_velocity", "video_id"]


def load_env(path=".env"):
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def _iso_duration(s: str) -> str:
    """PT#H#M#S -> h:mm:ss / mm:ss."""
    import re
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", s or "")
    if not m:
        return "0:00"
    h, mi, se = (int(x) if x else 0 for x in m.groups())
    return f"{h}:{mi:02d}:{se:02d}" if h else f"{mi}:{se:02d}"


def collect(query, days=60, limit=50, region="US", min_views=0, out_path=DATA):
    key = os.environ.get("YOUTUBE_API_KEY", "").strip()
    if not key or key.startswith("*"):
        print("→ no YOUTUBE_API_KEY set — using bundled sample data/videos.csv")
        return read_videos(out_path)

    try:
        import requests
    except ImportError:
        sys.exit("requests not installed. `pip install -r requirements.txt` or unset the key for sample mode.")

    base = "https://www.googleapis.com/youtube/v3"
    after = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    print("→ fetching search results…")
    sr = requests.get(f"{base}/search", params={
        "key": key, "part": "snippet", "q": query, "type": "video",
        "order": "viewCount", "maxResults": min(limit, 50),
        "publishedAfter": after, "regionCode": region}, timeout=30)
    sr.raise_for_status()
    ids = [i["id"]["videoId"] for i in sr.json().get("items", [])]
    if not ids:
        print("→ no results; keeping sample data"); return read_videos(out_path)

    print("→ reading video stats…")
    vr = requests.get(f"{base}/videos", params={
        "key": key, "part": "snippet,statistics,contentDetails",
        "id": ",".join(ids)}, timeout=30)
    vr.raise_for_status()

    now = datetime.now(timezone.utc)
    rows = []
    for v in vr.json().get("items", []):
        sn, st = v["snippet"], v.get("statistics", {})
        views = int(st.get("viewCount", 0))
        if views < min_views:
            continue
        published = datetime.fromisoformat(sn["publishedAt"].replace("Z", "+00:00"))
        age = max((now - published).days, 1)
        rows.append({
            "title": sn["title"], "channel": "@" + sn["channelTitle"].replace(" ", ""),
            "views": views, "age_days": age, "likes": int(st.get("likeCount", 0)),
            "comments": int(st.get("commentCount", 0)),
            "duration": _iso_duration(v["contentDetails"]["duration"]),
            "view_velocity": views // age, "video_id": v["id"]})

    rows.sort(key=lambda r: r["view_velocity"], reverse=True)
    print(f"→ saving {out_path}…")
    write_videos(rows, out_path)
    print(f"✓ {len(rows)} videos collected")
    print(f"✓ saved {out_path}")
    return rows


def read_videos(path=DATA):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k in ("views", "age_days", "likes", "comments", "view_velocity"):
            r[k] = int(r[k])
    return rows


def write_videos(rows, path=DATA):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


def main():
    load_env()
    p = argparse.ArgumentParser(description="Collect YouTube videos into data/videos.csv")
    p.add_argument("--query", default=os.environ.get("TOPIC", "AI tools"))
    p.add_argument("--days", type=int, default=int(os.environ.get("DAYS_BACK", 60)))
    p.add_argument("--limit", type=int, default=int(os.environ.get("MAX_RESULTS", 50)))
    p.add_argument("--region", default=os.environ.get("REGION", "US"))
    p.add_argument("--min-views", type=int, default=int(os.environ.get("MIN_VIEWS", 0)))
    a = p.parse_args()
    rows = collect(a.query, a.days, a.limit, a.region, a.min_views)
    print(f"✓ {len(rows)} videos available in data/videos.csv")


if __name__ == "__main__":
    main()
