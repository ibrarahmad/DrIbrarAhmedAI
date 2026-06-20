#!/usr/bin/env python3
"""scrape_videos.py — gather top videos in the niche (local, no API key).

Ships a bundled niche library (data/niche_videos.csv) so the agent runs fully
offline. Point it at a real source later if you want live data.

    python3 scrape_videos.py
"""
from __future__ import annotations
import argparse, csv, os

HERE = os.path.dirname(__file__)
LIB = os.path.join(HERE, "data", "niche_videos.csv")


def scrape(topic=None, limit=50, path=LIB):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["ctr"] = float(r["ctr"])
        r["views"] = int(r["views"])
    return rows[:limit]


def main():
    p = argparse.ArgumentParser(description="Scrape top videos in a niche")
    p.add_argument("--topic", default=None)
    p.add_argument("--limit", type=int, default=50)
    a = p.parse_args()
    rows = scrape(a.topic, a.limit)
    print(f"✓ {len(rows)} videos analyzed (bundled niche library, no API key)")


if __name__ == "__main__":
    main()
