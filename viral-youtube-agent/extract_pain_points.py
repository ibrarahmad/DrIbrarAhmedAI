#!/usr/bin/env python3
"""extract_pain_points.py — turn raw comments into ranked viewer needs.

    python3 extract_pain_points.py data/comments.csv
"""
from __future__ import annotations
import argparse, json, os

HERE = os.path.dirname(__file__)
COMMENTS = os.path.join(HERE, "data", "comments.csv")
OUT = os.path.join(HERE, "output", "pain_points.json")

# need -> keywords that signal it
NEEDS = {
    "show setup":          ["setup", "install", "step by step", "step-by-step", "guide"],
    "real terminal proof": ["terminal", "real proof", "actual code", "show me the", "not slides", "real machine"],
    "full workflow":       ["workflow", "end to end", "end-to-end", "pipeline", "process"],
    "no theory slides":    ["no theory", "stop with the theory", "just show", "less theory"],
    "share repo":          ["repo", "github", "source", "config files", "code"],
    "safe step-by-step":   ["safe", "locally", "on my server", "on my machine", "run this"],
}


def extract(comments):
    counts = {need: 0 for need in NEEDS}
    for c in comments:
        text = c["comment"].lower()
        weight = 1 + int(c.get("likes", 0) or 0) // 50  # liked comments count a bit more
        for need, kws in NEEDS.items():
            if any(k in text for k in kws):
                counts[need] += weight
    ranked = sorted(({"need": n, "mentions": m} for n, m in counts.items() if m),
                    key=lambda r: r["mentions"], reverse=True)
    return ranked


def main():
    p = argparse.ArgumentParser(description="Extract pain points from comments")
    p.add_argument("comments", nargs="?", default=COMMENTS)
    a = p.parse_args()
    import collect_comments
    rows = collect_comments.read_comments(a.comments)
    ranked = extract(rows)
    print("Top viewer needs:")
    for i, r in enumerate(ranked, 1):
        print(f'  {i}. {r["need"]:<22} ({r["mentions"]} mentions)')
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(ranked, open(OUT, "w", encoding="utf-8"), indent=2)


if __name__ == "__main__":
    main()
