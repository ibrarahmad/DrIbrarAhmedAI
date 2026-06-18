<div align="center">

# 🎬 Viral YouTube Idea Agent

### I let AI pick my next viral video — scored from real YouTube data

Companion code for the video on
**[@DrIbrarAhmedAI](https://www.youtube.com/@DrIbrarAhmedAI)**.

<br/>

[![Watch on YouTube](https://img.shields.io/badge/▶_Watch_the_video-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/@DrIbrarAhmedAI)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Runs offline](https://img.shields.io/badge/runs-offline%20on%20sample%20data-34D399?style=flat-square)](#-quick-start)

`Collect` → `Analyze` → `Score` → `Reject` → `Brief`

</div>

---

> Most creators **guess** their next video. This is a small, inspectable pipeline
> that scores ideas from **real YouTube signals** — winning title patterns and
> what the comments actually ask for — then writes a production brief.
> **Not a magic viral button. A repeatable research workflow.**

---

## 📑 Contents

- [How it works](#-how-it-works)
- [Project structure](#-project-structure)
- [Quick start](#-quick-start)
- [Configuration](#-configuration)
- [The pipeline, step by step](#-the-pipeline-step-by-step)
- [Scoring rubric](#-scoring-rubric)
- [Output files](#-output-files)
- [Honest limits](#-honest-limits)

---

## 🧭 How it works

```
collect_youtube.py     → data/videos.csv      (view_velocity = views ÷ age_days)
collect_comments.py    → data/comments.csv    (spam removed)
analyze_titles.py      → winning title patterns by velocity
extract_pain_points.py → ranked viewer needs from comments
generate_ideas.py      → output/ideas.json    (12 candidates from patterns + pains)
score_ideas.py         → output/top_ideas.json (0-100, rejects generic listicles)
build_hook.py          → output/hook_options.md
viral_idea_agent.py    → orchestrates all of it → output/winner_brief.md
```

Views alone lie — **speed matters.** `view_velocity` is the column that tells you
what's actually moving.

---

## 📂 Project structure

```
viral-youtube-agent/
├── collect_youtube.py       ├── prompts/
├── collect_comments.py      │   └── idea_score.txt
├── analyze_titles.py        ├── data/
├── extract_pain_points.py   │   ├── videos.csv      (sample)
├── generate_ideas.py        │   └── comments.csv    (sample)
├── score_ideas.py           ├── output/             (generated)
├── build_hook.py            ├── .env.example
├── viral_idea_agent.py      └── requirements.txt
```

---

## ⚡ Quick start

**Runs offline out of the box** on the bundled sample data — no API key needed:

```bash
python3 viral_idea_agent.py --topic "AI tools" --channel "@DrIbrarAhmedAI"
```

```
✓ collected 12 videos
✓ extracted 16 comments
✓ scored 12 ideas
✓ winner: "I Let AI Pick My Next Viral YouTube Video"   (91/100)
✓ brief written → output/winner_brief.md
```

Want live data? Add a key (next section) and the same command pulls real videos
and comments instead of the sample.

---

## ⚙️ Configuration

```bash
cp .env.example .env     # then edit
```

| Var | Meaning |
|-----|---------|
| `YOUTUBE_API_KEY` | YouTube Data API v3 key. **Omit it to run on sample data.** Never commit it. |
| `TOPIC` | Niche to research. |
| `REGION` | Region code (e.g. `US`). |
| `MAX_RESULTS` / `MIN_VIEWS` / `DAYS_BACK` | Result cap, noise floor, recency window. |
| `MODEL` | `local-llm` (Ollama) or `heuristic` (no model needed). |
| `OLLAMA_URL` / `OLLAMA_MODEL` | Where the local model lives. |

> 🔐 The key is read from `.env`/environment only — masked in the deck, gitignored here.

---

## 🪜 The pipeline, step by step

Run the whole thing with `viral_idea_agent.py`, or each stage on its own:

```bash
python3 collect_youtube.py --query "AI agents" --days 60 --limit 50
python3 collect_comments.py --video-list data/videos.csv --limit 20
python3 analyze_titles.py data/videos.csv
python3 extract_pain_points.py data/comments.csv
python3 generate_ideas.py --topic "AI agents for creators"
python3 score_ideas.py --input output/ideas.json --videos data/videos.csv --comments data/comments.csv
python3 build_hook.py --title "I Let AI Pick My Next Viral YouTube Video"
```

---

## 🎯 Scoring rubric

The model scores; the data grounds it. The rubric lives in
[`prompts/idea_score.txt`](prompts/idea_score.txt) — readable, not magic:

| Dimension | Question |
|-----------|----------|
| Click potential | Title + thumbnail curiosity |
| Practical proof | Can I show real screens? |
| Trend fit | Matches velocity patterns |
| Demo strength | Terminal, CSV, JSON visible |
| Retention risk | Where viewers might drop |
| Channel fit | Matches the channel |
| Build difficulty | Can I ship this week? |

**Rejection is a feature.** Generic listicles (`Top 10 …`, `Best …`, `… News Roundup`)
are scored out:

```
✗ Top 10 AI Tools in 2026 — generic listicle, low authority, weak evergreen value
✗ Best AI Apps           — rejected
✗ AI News Roundup        — rejected
```

> With `MODEL=local-llm` and Ollama running, the rubric is sent to a local model.
> Otherwise the same dimensions run as a transparent heuristic — so it always works.

---

## 📦 Output files

Every run writes to `output/`:

| File | Contents |
|------|----------|
| `top_ideas.json` | All ideas scored + ranked, plus the rejected list. |
| `winner_brief.md` | Title, thumbnail, hook, why-it-works, retention risks, checklist. |
| `thumbnail_options.md` | A/B/C thumbnail text with scores. |
| `hook_options.md` | Three hooks; the data-driven one selected. |
| `retention_risks.md` | Drag-risk timeline + rejected ideas. |

---

## ⚖️ Honest limits

- ❌ Not a magic viral button.
- ❌ Not a replacement for judgment.
- ❌ Not fake trend guessing.
- ✅ **A repeatable research workflow** — run it before your next video.

> Idea scores are computed from the bundled sample data, so they're reproducible.
> Plug in a real API key + topic and the numbers reflect *your* niche.

---

<div align="center">

**▶ [Watch the full build on YouTube](https://www.youtube.com/@DrIbrarAhmedAI)**

_Comment **AGENT** on the video and I'll share the workflow template._

⭐ _Found this useful? Star the repo._

</div>
