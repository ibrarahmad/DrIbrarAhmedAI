#!/usr/bin/env python3
"""collect_comments.py — pull comments from the top videos into data/comments.csv.

Comments tell you what to demo, not what to theorize about. Spam is dropped.
Live mode needs YOUTUBE_API_KEY; otherwise the bundled sample is reused.

    python3 collect_comments.py --video-list data/videos.csv --limit 20
"""
from __future__ import annotations
import argparse, csv, os, sys

HERE = os.path.dirname(__file__)
VIDEOS = os.path.join(HERE, "data", "videos.csv")
OUT = os.path.join(HERE, "data", "comments.csv")
FIELDS = ["video_title", "comment", "likes"]


def load_env(path=".env"):
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def _is_spam(text: str) -> bool:
    t = text.lower()
    return (len(text) < 6 or "http://" in t or "https://" in t
            or "subscribe to my" in t or "check my channel" in t)


def collect(video_list=VIDEOS, limit=20, out_path=OUT):
    key = os.environ.get("YOUTUBE_API_KEY", "").strip()
    if not key or key.startswith("*"):
        print("→ no YOUTUBE_API_KEY set — using bundled sample data/comments.csv")
        return read_comments(out_path)

    try:
        import requests
    except ImportError:
        sys.exit("requests not installed. `pip install -r requirements.txt` or unset the key for sample mode.")

    with open(video_list, newline="", encoding="utf-8") as f:
        vids = [r for r in csv.DictReader(f) if r.get("video_id")][:limit]

    base = "https://www.googleapis.com/youtube/v3/commentThreads"
    rows = []
    print(f"→ collecting comments from top {len(vids)} videos…")
    for v in vids:
        try:
            r = requests.get(base, params={
                "key": key, "part": "snippet", "videoId": v["video_id"],
                "maxResults": 100, "order": "relevance", "textFormat": "plainText"}, timeout=30)
            r.raise_for_status()
        except Exception as e:
            print(f"  · skipped {v['video_id']}: {e}"); continue
        for it in r.json().get("items", []):
            c = it["snippet"]["topLevelComment"]["snippet"]
            text = c["textDisplay"].replace("\n", " ").strip()
            if _is_spam(text):
                continue
            rows.append({"video_title": v["title"], "comment": text,
                         "likes": int(c.get("likeCount", 0))})

    print("→ removing spam…")
    print(f"→ saving {out_path}…")
    write_comments(rows, out_path)
    print(f"✓ {len(rows)} comments saved")
    return rows


def read_comments(path=OUT):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["likes"] = int(r.get("likes", 0) or 0)
    return rows


def write_comments(rows, path=OUT):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


def main():
    load_env()
    p = argparse.ArgumentParser(description="Collect comments into data/comments.csv")
    p.add_argument("--video-list", default=VIDEOS)
    p.add_argument("--limit", type=int, default=20)
    a = p.parse_args()
    rows = collect(a.video_list, a.limit)
    print(f"✓ {len(rows)} comments available in data/comments.csv")


if __name__ == "__main__":
    main()
