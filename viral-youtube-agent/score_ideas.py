#!/usr/bin/env python3
"""score_ideas.py — score ideas 0-100 against the rubric, grounded in data.

The model scores; the data grounds it. With MODEL=local-llm and Ollama running,
the rubric in prompts/idea_score.txt is sent to a local model. Otherwise a
transparent heuristic (same rubric dimensions) runs — so it always works.

    python3 score_ideas.py --input output/ideas.json \
        --videos data/videos.csv --comments data/comments.csv
"""
from __future__ import annotations
import argparse, json, os, re

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "output", "top_ideas.json")
PROMPT = os.path.join(HERE, "prompts", "idea_score.txt")

REJECT_PAT = [r"^top \d+", r"^best ", r"news roundup", r"^\d+ best"]


def load_env(path=".env"):
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def _is_generic(title: str) -> bool:
    t = title.lower()
    return any(re.search(p, t) for p in REJECT_PAT)


FIRST_PERSON = ("i built", "i tried", "i made", "i let ai", "i let an")


def _heuristic(title, patterns, pains):
    t = title.lower()
    max_vel = max((p["avg_velocity"] for p in patterns), default=1)
    # First-person build/proof titles outperform; if the exact phrase isn't in the
    # data, they still inherit the best first-person pattern velocity.
    fp_vel = max((p["avg_velocity"] for p in patterns
                  if p["pattern"].lower() in FIRST_PERSON), default=0)
    exact_vel = max((p["avg_velocity"] for p in patterns if p["pattern"].lower() in t), default=0)
    pat_vel = max(exact_vel, fp_vel if t.startswith("i ") else 0)

    # Click potential — curiosity drives the click.
    curiosity = sum(b for w, b in
                    (("viral", 14), ("pick", 8), ("my next", 6), ("finds", 6),
                     ("judge", 5), ("reads", 4), ("writes", 4)) if w in t)
    click = 50 + (18 if t.startswith("i ") else 0) + curiosity
    proof = 50 + (35 if any(w in t for w in ["built", "made", "let ai", "agent", "judge", "planner"]) else 0)
    trend = round(40 + 60 * (pat_vel / max_vel)) if max_vel else 40
    demo = 60 + (25 if any(w in t for w in ["agent", "built", "scores", "reads", "pick", "finds"]) else 0)
    # shorter, concrete titles = lower retention risk = higher retention score
    retention = max(40, 95 - max(0, len(title.split()) - 9) * 5)
    fit = 60 + (25 if any(w in t for w in ["ai", "local", "agent"]) else 0)
    build = 85 if len(title.split()) <= 9 else 65
    pain_hits = sum(1 for p in pains if any(k in t for k in p["need"].split()))
    click = min(100, click + pain_hits * 3)

    subs = {"click": min(click, 100), "proof": min(proof, 100), "trend": min(trend, 100),
            "demo": min(demo, 100), "retention": retention, "fit": min(fit, 100), "build": build}
    weights = {"click": .22, "proof": .20, "trend": .16, "demo": .16,
               "retention": .10, "fit": .10, "build": .06}
    score = round(sum(subs[k] * w for k, w in weights.items()))
    reasons = []
    if pat_vel:
        reasons.append(f'matches a winning pattern (~{pat_vel/1000:.1f}K/d velocity)')
    if proof >= 80:
        reasons.append("strong demo: terminal, CSV, JSON visible")
    if pain_hits:
        reasons.append(f"addresses {pain_hits} top viewer request(s)")
    if not reasons:
        reasons.append("limited data signal")
    return score, subs, reasons


def _llm_score(ideas, videos, comments, patterns, pains):
    """Try Ollama; return list or None on any failure (caller falls back)."""
    if os.environ.get("MODEL", "heuristic") != "local-llm":
        return None
    try:
        import requests
    except ImportError:
        return None
    rubric = open(PROMPT, encoding="utf-8").read()
    payload = {
        "model": os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:7b"),
        "messages": [
            {"role": "system", "content": rubric},
            {"role": "user", "content": json.dumps({
                "ideas": [i["title"] for i in ideas],
                "patterns": patterns, "pains": pains}, ensure_ascii=False)}],
        "temperature": 0.2, "stream": False}
    url = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434/v1").rstrip("/") + "/chat/completions"
    try:
        r = requests.post(url, json=payload, timeout=60)
        r.raise_for_status()
        txt = r.json()["choices"][0]["message"]["content"]
        data = json.loads(re.search(r"\{.*\}", txt, re.S).group(0))
        return data["scores"]
    except Exception as e:
        print(f"→ local LLM unavailable ({e}); using heuristic scorer")
        return None


def score(ideas, videos, comments, patterns=None, pains=None):
    patterns = patterns or []
    pains = pains or []
    llm = _llm_score(ideas, videos, comments, patterns, pains)
    scored = []
    for it in ideas:
        title = it["title"]
        if _is_generic(title):
            scored.append({"title": title, "score": 0, "verdict": "reject",
                           "reasons": ["generic listicle — low authority, weak evergreen value"]})
            continue
        match = next((s for s in (llm or []) if s.get("title") == title), None)
        if match:
            scored.append({"title": title, "score": int(match["score"]),
                           "subscores": match.get("subscores", {}),
                           "reasons": match.get("reasons", []),
                           "verdict": match.get("verdict", "keep")})
        else:
            sc, subs, reasons = _heuristic(title, patterns, pains)
            scored.append({"title": title, "score": sc, "subscores": subs,
                           "reasons": reasons, "verdict": "keep"})

    keep = sorted([s for s in scored if s["verdict"] == "keep"],
                  key=lambda s: s["score"], reverse=True)
    for rank, s in enumerate(keep, 1):
        s["rank"] = rank
    rejected = [s for s in scored if s["verdict"] == "reject"]
    return {"ideas": keep, "rejected": rejected}


def main():
    load_env()
    p = argparse.ArgumentParser(description="Score ideas → output/top_ideas.json")
    p.add_argument("--input", default=os.path.join(HERE, "output", "ideas.json"))
    p.add_argument("--videos", default=os.path.join(HERE, "data", "videos.csv"))
    p.add_argument("--comments", default=os.path.join(HERE, "data", "comments.csv"))
    a = p.parse_args()

    import collect_youtube, collect_comments, analyze_titles, extract_pain_points
    ideas = json.load(open(a.input, encoding="utf-8"))["ideas"]
    videos = collect_youtube.read_videos(a.videos)
    comments = collect_comments.read_comments(a.comments)
    patterns = analyze_titles.analyze(videos)
    pains = extract_pain_points.extract(comments)

    result = score(ideas, videos, comments, patterns, pains)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(result, open(OUT, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"✓ scored {len(ideas)} ideas → output/top_ideas.json")
    for s in result["ideas"][:3]:
        print(f'  #{s["rank"]}  {s["score"]}  {s["title"]}')


if __name__ == "__main__":
    main()
