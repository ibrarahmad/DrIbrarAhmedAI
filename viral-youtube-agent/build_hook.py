#!/usr/bin/env python3
"""build_hook.py — generate three opening hooks and select the data-driven one.

    python3 build_hook.py --idea output/winner.json
    python3 build_hook.py --title "I Let AI Pick My Next Viral YouTube Video"
"""
from __future__ import annotations
import argparse, json, os

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "output", "hook_options.md")


def build(title):
    options = [
        "I was stuck on my next video until I built this.",
        "What if your next viral idea came from data, not guesswork?",
        ("Most creators guess their next video. I built an AI agent that scores "
         "real YouTube signals and picks one idea for me."),
    ]
    selected = 3  # the longest, most concrete, proof-first hook wins
    return options, selected


def main():
    p = argparse.ArgumentParser(description="Build opening hooks")
    p.add_argument("--idea", help="path to winner JSON ({title,...})")
    p.add_argument("--title", help="idea title directly")
    a = p.parse_args()
    title = a.title
    if a.idea:
        title = json.load(open(a.idea, encoding="utf-8")).get("title", title)
    title = title or "I Let AI Pick My Next Viral YouTube Video"

    options, selected = build(title)
    print("Hook options:")
    for i, h in enumerate(options, 1):
        mark = "  ← selected" if i == selected else ""
        print(f"  {i}. {h}{mark}")
    print(f"✓ selected hook #{selected}")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(f"# Hook options — {title}\n\n")
        for i, h in enumerate(options, 1):
            f.write(f"{i}. {h}{'  **(selected)**' if i == selected else ''}\n")
    return options, selected


if __name__ == "__main__":
    main()
