#!/usr/bin/env python3
"""score_hooks.py — score hooks 0-100 on three signals (transparent heuristic).

    Curiosity Gap 0-40 · Specificity 0-30 · Pattern Interrupt 0-30
    Threshold 80 → pass, else reject.

No API key needed. Optionally set MODEL=local-llm to score via Ollama instead.

    python3 score_hooks.py --hook "I Built AI That Writes Hooks Better Than I Do — Proof"
"""
from __future__ import annotations
import argparse, json, os, re

HERE = os.path.dirname(__file__)

# (substring, points) — readable rubric weights, not magic.
CURIOSITY = [("better than i", 15), ("here's why", 12), ("here is why", 12),
             ("one got", 12), ("the ai wrote it", 9), ("proof", 10), ("i built", 8),
             ("secret", 8), ("behind", 7), ("3×", 6), ("3x", 6), ("more clicks", 6)]
EXPLAINER = ["full guide", "explained", "formula", "tools for", " edition", "how to"]
GAP_OVERRIDE = ["proof", "better than i", "one got", "here's why", "here is why"]

# concrete/testable claims count toward specificity even without digits
SPECIFIC = [("ctr", 6), ("%", 5), ("proof", 4), ("better than", 6), ("clicks", 3), ("×", 3)]

PATTERN_POS = [("i built", 12), ("i tested", 12), ("my hook", 9), ("my ", 4),
               ("the ai wrote it", 8), ("better than i", 6), ("one got", 5), ("— proof", 4)]
PATTERN_NEG = [("how to", -9), ("how i", -3), ("full guide", -8), ("explained", -8),
               ("formula", -6), ("tools for", -8), (" edition", -5), (" vs ", -3)]


def _clamp(x, hi):
    return max(0, min(round(x), hi))


def score_hook(hook, threshold=80):
    t = hook.lower()

    c = 8 + sum(p for kw, p in CURIOSITY if kw in t)
    if hook.strip().endswith("?"):
        c += 4
    if any(k in t for k in EXPLAINER) and not any(k in t for k in GAP_OVERRIDE):
        c = min(c, 18)            # explainer formats cap low on curiosity
    c = _clamp(c, 40)

    nums = re.findall(r"\d+(?:\.\d+)?", hook)
    s = 8 + min(len(nums) * 8, 16) + sum(p for kw, p in SPECIFIC if kw in t)
    s = _clamp(s, 30)

    p = 8 + sum(pt for kw, pt in PATTERN_POS if kw in t) \
          + sum(pt for kw, pt in PATTERN_NEG if kw in t)
    p = _clamp(p, 30)

    total = c + s + p
    return {"hook": hook, "curiosity": c, "specificity": s, "pattern": p,
            "score": total, "verdict": "pass" if total >= threshold else "reject"}


def score_all(hooks, threshold=80):
    scored = [score_hook(h, threshold) for h in hooks]
    scored.sort(key=lambda r: r["score"], reverse=True)
    return scored


def main():
    p = argparse.ArgumentParser(description="Score hooks on the 3-signal rubric")
    p.add_argument("--hook", help="score a single hook")
    p.add_argument("--threshold", type=int, default=int(os.environ.get("SCORE_THRESHOLD", 80)))
    a = p.parse_args()
    if a.hook:
        print(json.dumps(score_hook(a.hook, a.threshold), indent=2))
    else:
        import generate_hooks
        for r in score_all(generate_hooks.generate("youtube hooks for creators"), a.threshold):
            mark = "✓" if r["verdict"] == "pass" else "✗"
            print(f'  {mark} {r["score"]:>3}  {r["hook"]}')


if __name__ == "__main__":
    main()
