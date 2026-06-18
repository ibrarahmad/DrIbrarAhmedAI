#!/usr/bin/env python3
"""analyze_titles.py — extract winning title patterns by view_velocity.

    python3 analyze_titles.py data/videos.csv
"""
from __future__ import annotations
import argparse, json, os, sys

HERE = os.path.dirname(__file__)
VIDEOS = os.path.join(HERE, "data", "videos.csv")
OUT = os.path.join(HERE, "output", "title_patterns.json")

# Phrase patterns we look for at/near the start of a title.
PATTERNS = ["I Tried", "I Built", "I Made", "I Let AI", "Don't Use",
            "Don't Trust", "AI Agent", "Local AI", "Top 10", "Best"]


def analyze(videos):
    buckets = {}
    for v in videos:
        title = v["title"]
        for pat in PATTERNS:
            if pat.lower() in title.lower():
                buckets.setdefault(pat, []).append(int(v["view_velocity"]))
    out = []
    for pat, vels in buckets.items():
        out.append({"pattern": pat, "count": len(vels),
                    "avg_velocity": round(sum(vels) / len(vels))})
    out.sort(key=lambda r: r["avg_velocity"], reverse=True)
    return out


def main():
    p = argparse.ArgumentParser(description="Analyze title patterns")
    p.add_argument("videos", nargs="?", default=VIDEOS)
    a = p.parse_args()
    import collect_youtube
    rows = collect_youtube.read_videos(a.videos)
    patterns = analyze(rows)
    print("Patterns found:")
    for r in patterns:
        print(f'  "{r["pattern"]}…"  avg velocity {r["avg_velocity"]/1000:.1f}K/d  ({r["count"]} videos)')
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(patterns, open(OUT, "w", encoding="utf-8"), indent=2)
    if patterns:
        top = patterns[0]
        print(f'\nWinning pattern: "{top["pattern"]}" performs strong.')


if __name__ == "__main__":
    main()
