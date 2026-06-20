#!/usr/bin/env python3
"""extract_patterns.py — pull hook patterns from the top 10% CTR videos.

The top-decile titles in your niche ARE your hook pattern library.

    python3 extract_patterns.py
"""
from __future__ import annotations
import argparse, os, re

HERE = os.path.dirname(__file__)


def extract(videos):
    if not videos:
        return {}
    ranked = sorted(videos, key=lambda v: float(v["ctr"]), reverse=True)
    top = ranked[: max(1, len(ranked) // 10)]
    feats = {"first_person": 0, "has_number": 0, "proof_word": 0, "em_dash": 0, "open_loop": 0}
    for v in top:
        t = v["title"].lower()
        feats["first_person"] += int(t.startswith("i ") or t.startswith("my "))
        feats["has_number"] += int(bool(re.search(r"\d", t)))
        feats["proof_word"] += int(any(w in t for w in ["proof", "test", "result"]))
        feats["em_dash"] += int("—" in v["title"] or " - " in v["title"])
        feats["open_loop"] += int(any(w in t for w in ["here's why", "here is why", "what happened", "one "]))
    n = len(top)
    return {"sample": n, "avg_ctr_top": round(sum(float(v["ctr"]) for v in top) / n, 2),
            "patterns": {k: f"{round(100*c/n)}%" for k, c in feats.items()}}


def main():
    p = argparse.ArgumentParser(description="Extract top-CTR hook patterns")
    a = p.parse_args()
    import scrape_videos
    summary = extract(scrape_videos.scrape())
    print(f"✓ Top {summary['sample']} CTR patterns extracted (avg CTR {summary['avg_ctr_top']}%)")
    for k, v in summary["patterns"].items():
        print(f"  {k:<14} {v}")


if __name__ == "__main__":
    main()
