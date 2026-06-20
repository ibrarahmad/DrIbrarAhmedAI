#!/usr/bin/env python3
"""hook_agent.py — score 10 YouTube hooks, rank them, write a brief. Local, no API key.

    python3 hook_agent.py                       # replay the recorded EP02 run (matches the video)
    python3 hook_agent.py --topic "AI thumbnails" --live   # score a fresh topic with the heuristic
    python3 hook_agent.py --hook "your hook"     # score one hook

Pipeline (--live): scrape top videos → extract top-CTR patterns →
generate 10 variants → score on 3 signals → rank → output/hook_brief.md
"""
from __future__ import annotations
import argparse, json, os

import scrape_videos, extract_patterns, generate_hooks, score_hooks

HERE = os.path.dirname(__file__)
OUTDIR = os.path.join(HERE, "output")
EXAMPLE = os.path.join(HERE, "data", "example_hooks.json")


def load_env(path=".env"):
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def _write_brief(topic, threshold, hooks, my_hook, brief):
    os.makedirs(OUTDIR, exist_ok=True)
    json.dump({"topic": topic, "threshold": threshold, "my_hook": my_hook,
               "hooks": hooks, "winner_brief": brief},
              open(os.path.join(OUTDIR, "hooks_scored.json"), "w", encoding="utf-8"),
              indent=2, ensure_ascii=False)

    passed = [h for h in hooks if h["verdict"] == "pass"]
    rejected = [h for h in hooks if h["verdict"] == "reject"]
    w = brief
    lines = [f"# Hook Brief — {topic}", ""]
    lines += [f"**Winner score: {hooks[0]['score']}/100**  ·  threshold {threshold}", ""]
    lines += ["## Winner", "",
              f"- **Hook:** {w['hook']}",
              f"- **Thumbnail text:** {w['thumbnail_text']}",
              f"- **First line:** \"{w['first_line']}\"",
              f"- **Agent confidence:** {w['confidence']}",
              f"- **Signals:** Curiosity {hooks[0]['curiosity']}/40 · "
              f"Specificity {hooks[0]['specificity']}/30 · Pattern {hooks[0]['pattern']}/30", ""]
    lines += [f"## Passed (≥{threshold})", ""]
    for i, h in enumerate(passed, 1):
        lines.append(f"{i}. **{h['score']}** — {h['hook']}")
    lines += ["", "## Rejected (<%d)" % threshold, ""]
    for h in rejected:
        lines.append(f"- ✗ **{h['score']}** — {h['hook']}  \n  _{h['reason']}_" if h.get("reason")
                     else f"- ✗ **{h['score']}** — {h['hook']}")
    if my_hook:
        gap = hooks[0]["score"] - my_hook["score"]
        lines += ["", "## Your hook (baseline)", "",
                  f"\"{my_hook['hook']}\" — **{my_hook['score']}/100** "
                  f"({my_hook['curiosity']} + {my_hook['specificity']} + {my_hook['pattern']}). "
                  f"The winning hook beats it by **{gap} points**."]
    open(os.path.join(OUTDIR, "hook_brief.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")


def run_recorded():
    data = json.load(open(EXAMPLE, encoding="utf-8"))
    print(f'$ python3 hook_agent.py --topic "{data["topic"]}"')
    print("→ Scraping top 50 videos in niche...")
    print("✓ 50 videos analyzed")
    print("✓ Top 10% CTR patterns extracted")
    print("✓ 10 hook variants generated")
    print("✗ 7 hooks below threshold (score < 80)")
    print("✓ 3 hooks passed — ranked by score")
    _write_brief(data["topic"], data["threshold"], data["hooks"],
                 data.get("my_hook"), data["winner_brief"])
    print("✓ output/hook_brief.md ready")
    print(f'\n🏆 Winner {data["hooks"][0]["score"]}/100 — {data["hooks"][0]["hook"]}')
    print("   (recorded EP02 run — pass --live to score your own topic)")


def run_live(topic, threshold):
    videos = scrape_videos.scrape(topic)
    print(f"✓ {len(videos)} videos analyzed (bundled niche library, no API key)")
    pats = extract_patterns.extract(videos)
    print(f"✓ Top {pats.get('sample', 0)} CTR patterns extracted")
    hooks_txt = generate_hooks.generate(topic)
    print(f"✓ {len(hooks_txt)} hook variants generated")
    scored = score_hooks.score_all(hooks_txt, threshold)
    n_fail = sum(1 for h in scored if h["verdict"] == "reject")
    print(f"✗ {n_fail} hooks below threshold (score < {threshold})")
    print(f"✓ {len(scored) - n_fail} hooks passed — ranked by score")
    for h in scored:
        h.setdefault("reason", "below threshold on one or more signals"
                     if h["verdict"] == "reject" else "")
    win = scored[0]
    brief = {"hook": win["hook"], "thumbnail_text": "PROOF",
             "first_line": f"This hook scored {win['score']}. Here is why it wins.",
             "confidence": "High" if win["score"] >= 85 else "Medium"}
    _write_brief(topic, threshold, scored, None, brief)
    print("✓ output/hook_brief.md ready")
    print(f'\n🏆 Winner {win["score"]}/100 — {win["hook"]}')


def main():
    load_env()
    p = argparse.ArgumentParser(description="Score and rank YouTube hooks")
    p.add_argument("--topic", default=os.environ.get("TOPIC", "youtube hooks for creators"))
    p.add_argument("--live", action="store_true", help="score a fresh topic (heuristic) instead of replaying the recorded run")
    p.add_argument("--hook", help="score a single hook and exit")
    p.add_argument("--threshold", type=int, default=int(os.environ.get("SCORE_THRESHOLD", 80)))
    a = p.parse_args()

    if a.hook:
        print(json.dumps(score_hooks.score_hook(a.hook, a.threshold), indent=2))
        return
    if a.live:
        run_live(a.topic, a.threshold)
    else:
        run_recorded()


if __name__ == "__main__":
    main()
