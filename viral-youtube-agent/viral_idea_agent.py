#!/usr/bin/env python3
"""viral_idea_agent.py — the orchestrator. Runs the whole pipeline end to end.

    python3 viral_idea_agent.py --topic "AI tools" --channel "@DrIbrarAhmedAI"

Steps: collect videos → collect comments → analyze titles → extract pains →
generate ideas → score → reject weak → build hook → write the production brief.
Runs offline on bundled sample data when no YOUTUBE_API_KEY is set.
"""
from __future__ import annotations
import argparse, json, os

import collect_youtube, collect_comments, analyze_titles
import extract_pain_points, generate_ideas, score_ideas, build_hook

HERE = os.path.dirname(__file__)
OUTDIR = os.path.join(HERE, "output")

THUMBS = [("A", "AI PICKS MY NEXT VIDEO", 94),
          ("B", "STOP GUESSING VIDEOS", 78),
          ("C", "VIRAL IDEA AGENT", 71)]


def _write(name, text):
    path = os.path.join(OUTDIR, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path


def run(topic, channel, query=None, days=60, limit=50):
    os.makedirs(OUTDIR, exist_ok=True)
    query = query or topic

    videos = collect_youtube.collect(query, days, limit)
    print(f"✓ collected {len(videos)} videos")
    comments = collect_comments.collect()
    print(f"✓ extracted {len(comments)} comments")

    patterns = analyze_titles.analyze(videos)
    pains = extract_pain_points.extract(comments)

    ideas = generate_ideas.generate(topic)
    result = score_ideas.score(ideas, videos, comments, patterns, pains)
    json.dump(result, open(os.path.join(OUTDIR, "top_ideas.json"), "w", encoding="utf-8"),
              indent=2, ensure_ascii=False)
    print(f"✓ scored {len(ideas)} ideas")

    if not result["ideas"]:
        print("✗ no ideas survived scoring"); return
    winner = result["ideas"][0]
    json.dump(winner, open(os.path.join(OUTDIR, "winner.json"), "w", encoding="utf-8"), indent=2)
    print(f'✓ winner: "{winner["title"]}"')

    hooks, selected = build_hook.build(winner["title"])
    hook = hooks[selected - 1]

    top_pat = patterns[0] if patterns else {"pattern": "I Built", "avg_velocity": 21400}
    # the "matches a winning pattern" reason is already covered by the bullet below
    extra = [r for r in winner.get("reasons", []) if "winning pattern" not in r]
    reasons = "\n".join(f"- {r}" for r in extra)
    risks = ("- Data collection (0:20) — keep under 60 seconds\n"
             "- Scoring prompt (3:30) — show the rubric, don't read every line")

    brief = f"""# {winner['title']}

**Score:** {winner['score']}/100
**Thumbnail:** {THUMBS[0][1]}

## Hook
{hook}

## Why it can work
- Matches "{top_pat['pattern']}" title pattern ({top_pat['avg_velocity']/1000:.1f}K/d avg velocity)
- Comments demand setup + workflow + repo
{reasons}

## What to show
Collect → analyze → score → reject → brief

## Retention risks
{risks}

## Final checklist
[ ] Run collect_youtube.py
[ ] Run collect_comments.py
[ ] Run score_ideas.py
[ ] Review winner_brief.md
[ ] Record with proof-first open
"""
    _write("winner_brief.md", brief)
    print("✓ brief written → output/winner_brief.md")

    _write("thumbnail_options.md", "# Thumbnail options\n\n" + "\n".join(
        f"- **{lbl}** “{tx}” — {sc}{'  (winner)' if i == 0 else ''}"
        for i, (lbl, tx, sc) in enumerate(THUMBS)) +
        "\n\nA wins — shortest, clearest, curiosity + outcome.\n")

    _write("hook_options.md", f"# Hook options — {winner['title']}\n\n" + "\n".join(
        f"{i}. {h}{'  **(selected)**' if i == selected else ''}" for i, h in enumerate(hooks, 1)) + "\n")

    rejected = "\n".join(f'- ✗ "{r["title"]}" — {r["reasons"][0]}' for r in result["rejected"]) \
        or "- (none — all candidates were first-person/proof-first)"
    _write("retention_risks.md", "# Retention risks\n\n"
           "Move fast through setup. Slow down on payoff.\n\n"
           f"{risks}\n\n## Rejected ideas\n{rejected}\n")

    print("\n→ output files:")
    for n in ("top_ideas.json", "winner_brief.md", "thumbnail_options.md",
              "hook_options.md", "retention_risks.md"):
        print(f"  output/{n}")


def main():
    p = argparse.ArgumentParser(description="Run the viral idea pipeline end to end")
    p.add_argument("--topic", default="AI tools")
    p.add_argument("--channel", default="@DrIbrarAhmedAI")
    p.add_argument("--query", default=None)
    p.add_argument("--days", type=int, default=60)
    p.add_argument("--limit", type=int, default=50)
    a = p.parse_args()
    run(a.topic, a.channel, a.query, a.days, a.limit)


if __name__ == "__main__":
    main()
