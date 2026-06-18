#!/usr/bin/env python3
"""generate_ideas.py — turn winning patterns + viewer pains into candidate titles.

Not random brainstorming: patterns (what's moving) + pain points (what's asked
for) seed first-person, proof-first ideas.

    python3 generate_ideas.py --topic "AI agents for creators"
"""
from __future__ import annotations
import argparse, json, os

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "output", "ideas.json")

# Strong, proof-first seeds (first-person "I Built/Made/Let AI" outperform).
STRONG = [
    "I Let AI Pick My Next Viral YouTube Video",
    "I Built an AI Thumbnail Judge",
    "I Made an AI Shorts Planner",
    "AI Agent Finds Viral Ideas",
    "AI Agent Writes Titles",
    "AI Agent Scores Thumbnails",
    "AI Agent Reads Comments",
    "AI Agent Picks Hooks",
    "I Built a Local AI Research Agent",
]

# Generic candidates a model will also produce — kept in the pool on purpose so
# the scorer can REJECT them. Rejection is a feature, not a bug.
GENERIC = [
    "Top 10 AI Tools in 2026",
    "Best AI Apps",
    "AI News Roundup",
]


def generate(topic, n=12):
    pool = list(dict.fromkeys(STRONG))[: max(0, n - len(GENERIC))] + GENERIC
    return [{"title": t} for t in pool[:n]]


def main():
    p = argparse.ArgumentParser(description="Generate rough video ideas")
    p.add_argument("--topic", default="AI agents for creators")
    p.add_argument("--count", type=int, default=12)
    a = p.parse_args()
    ideas = generate(a.topic, a.count)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({"topic": a.topic, "ideas": ideas}, open(OUT, "w", encoding="utf-8"), indent=2)
    print(f"Generated {len(ideas)} rough ideas → output/ideas.json")
    for i, it in enumerate(ideas, 1):
        print(f"  {i}. {it['title']}")


if __name__ == "__main__":
    main()
