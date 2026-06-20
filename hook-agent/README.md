<div align="center">

# 🪝 Hook Agent — EP 02

### One local command scores 10 YouTube hooks and picks a winner

Companion code for **EP 02** on
**[@DrIbrarAhmedAI](https://www.youtube.com/@DrIbrarAhmedAI)** —
*"AI beat my hook by 48 points."*

<br/>

[![Watch on YouTube](https://img.shields.io/badge/▶_Watch_EP_02-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/@DrIbrarAhmedAI)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![No API key](https://img.shields.io/badge/no%20API%20key-runs%20locally-34D399?style=flat-square)](#-quick-start)

`Scrape` → `Extract` → `Generate` → `Rank` · under 60 seconds

</div>

---

> Most creators spend **5 minutes on the hook and hours on the video** — yet the
> hook can create a **4× click gap**. This agent scores 10 hooks on three signals,
> rejects everything under 80, and writes a brief you can film from. **Runs
> locally. No API key.**

---

## 📑 Contents

- [Quick start](#-quick-start)
- [The three signals](#-the-three-signals)
- [The pipeline](#-the-pipeline)
- [Files](#-files)
- [Recorded run vs live](#-recorded-run-vs-live)
- [Output](#-output)
- [Honest limits](#-honest-limits)

---

## ⚡ Quick start

```bash
git clone https://github.com/ibrarahmad/DrIbrarAhmedAI
cd DrIbrarAhmedAI/hook-agent
cp .env.example .env          # optional — set TOPIC=your niche
python3 hook_agent.py         # replays the recorded EP02 run
open output/hook_brief.md     # winner + top 3 + thumbnail text
```

```
✓ 50 videos analyzed
✓ Top 10% CTR patterns extracted
✓ 10 hook variants generated
✗ 7 hooks below threshold (score < 80)
✓ 3 hooks passed — ranked by score
🏆 Winner 89/100 — I Built AI That Writes Hooks Better Than I Do — Proof
```

Score **your own** niche:

```bash
python3 hook_agent.py --topic "AI thumbnails" --live
python3 hook_agent.py --hook "I Built an AI That Edits Faster Than Me — Proof"
```

> Pure standard library — nothing to install. `requests` is only needed if you
> opt into `MODEL=local-llm` (Ollama).

---

## 🎯 The three signals

100 points total. The rubric lives in [`prompts/hook_score.txt`](prompts/hook_score.txt):

| Signal | Max | What it rewards |
|--------|----:|-----------------|
| 🎯 **Curiosity Gap** | 40 | Promise something surprising and withhold the answer. |
| 🔢 **Specificity** | 30 | Numbers, names, concrete testable claims. |
| ⚡ **Pattern Interrupt** | 30 | Break the niche's expected format — challenge or confess. |

**Threshold 80.** Anything below is rejected — listicles, vague "how I…", and
"…Explained / Full Guide / Formula" formats score near zero on curiosity.

---

## 🧭 The pipeline

```
1. Scrape   top videos in the niche        (~15s)  scrape_videos.py
2. Extract  hook patterns from top 10% CTR (~8s)   extract_patterns.py
3. Generate 10 variants for your topic     (~25s)  generate_hooks.py
4. Rank     score on 3 signals, sort, flag (~10s)  score_hooks.py
                                                    → output/hook_brief.md
```

The top-decile titles in your niche **are** your hook pattern library.

---

## 📁 Files

| File | Purpose |
|------|---------|
| [`hook_agent.py`](hook_agent.py) | Orchestrator — the one command. |
| [`scrape_videos.py`](scrape_videos.py) | Top videos in the niche (bundled library, no API). |
| [`extract_patterns.py`](extract_patterns.py) | Patterns from the top 10% CTR. |
| [`generate_hooks.py`](generate_hooks.py) | 10 hook variants for a topic. |
| [`score_hooks.py`](score_hooks.py) | Transparent 3-signal scorer. |
| [`prompts/hook_score.txt`](prompts/hook_score.txt) | The scoring rubric. |
| [`data/`](data/) | Sample niche library + the recorded EP02 run. |

---

## 🎬 Recorded run vs live

- **`python3 hook_agent.py`** replays the **recorded EP02 run** from
  [`data/example_hooks.json`](data/example_hooks.json) — it reproduces the video
  exactly (winner **89/100**, your baseline hook **41/100**, a **48-point gap**).
- **`--live`** runs the genuine pipeline and scores via the transparent rubric in
  `score_hooks.py`. Your numbers will differ from the episode — they reflect
  *your* topic, not the recorded niche.

This split keeps the headline command faithful to the video **and** gives you a
real, inspectable scorer for your own hooks.

---

## 📦 Output

`output/hook_brief.md` — winner hook, thumbnail text, first line, confidence,
the passed/rejected split with reasons, and your baseline hook for comparison.
`output/hooks_scored.json` — the full scored data.

---

## ⚖️ Honest limits

**✗ Cannot** know your audience like you do · guarantee clicks (only predict) ·
replace creative instinct · score niche humour.
**✓ Can** kill blank-page paralysis · give 10 data-ranked options in 60s · show
*why* each scores · get you 80% there before you edit.

> CTR figures are projections — run it on your channel and share your real numbers.

---

<div align="center">

**▶ [Watch EP 02 on YouTube](https://www.youtube.com/@DrIbrarAhmedAI)** · EP 03 → *AI Writes Your First 30-Second Script*

_Comment **HOOK** on the video for the repo link._

⭐ _Found this useful? Star the repo._

</div>
