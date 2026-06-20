#!/usr/bin/env python3
"""generate_hooks.py — generate 10 hook variants for a topic.

Mirrors the structure of top-CTR hooks: a few strong proof/first-person angles
plus the weaker explainer/listicle formats (kept so scoring can reject them).

    python3 generate_hooks.py --topic "AI thumbnails"
"""
from __future__ import annotations
import argparse, json, os

HERE = os.path.dirname(__file__)

# Templates ordered strong → weak. {t} = topic phrase.
TEMPLATES = [
    "I Built an AI That Does {t} Better Than I Do — Proof",
    "My {t} Scored 8.3% CTR. The AI Did It. Here's Why.",
    "I Tested 10 AI {t} Ideas — One Got 3× More Clicks",
    "How I Used AI to Improve My {t}",
    "AI vs Human: Who's Better at {t}?",
    "The Secret Behind High-CTR {t}",
    "Using AI for {t} — Full Guide",
    "{t} Formula That Works in 2024",
    "AI Tools for {t} — Edition",
    "How to Do {t} with AI",
]


def generate(topic, n=10):
    t = topic.strip().title()
    return [tpl.format(t=t) for tpl in TEMPLATES][:n]


def main():
    p = argparse.ArgumentParser(description="Generate hook variants")
    p.add_argument("--topic", default="youtube hooks for creators")
    p.add_argument("--count", type=int, default=10)
    a = p.parse_args()
    hooks = generate(a.topic, a.count)
    print(f"✓ {len(hooks)} hook variants generated")
    for i, h in enumerate(hooks, 1):
        print(f"  {i}. {h}")


if __name__ == "__main__":
    main()
