<div align="center">

# Fine-Tuning smolagents for Real-Time Crypto Analysis

### Paper-only telemetry → adapted model → CodeAgent tools → safety gate

Companion code for **[@DrIbrarAhmedAI](https://www.youtube.com/@DrIbrarAhmedAI)**.

<br/>

[![Clone repo](https://img.shields.io/badge/Repo-ibrarahmad%2FDrIbrarAhmedAI-181717?style=for-the-badge&logo=github)](https://github.com/ibrarahmad/DrIbrarAhmedAI/tree/main/smolagents-crypto-analysis)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Paper only](https://img.shields.io/badge/Mode-paper--only-22C55E?style=flat-square)](#-safety)
[![Not financial advice](https://img.shields.io/badge/Disclaimer-educational-F59E0B?style=flat-square)](#-safety)

**Educational demo. No live orders. Not financial advice.**

</div>

---

## What you get

A complete **paper-only** loop:

`adapter → adapted model → tools / CodeAgent → safety gate → paper logs`

| Piece | Path |
|-------|------|
| Input / output contracts | `schemas/` |
| Paper-only sandbox policy | `sandbox/policy.yaml` |
| Three allowed tools | `tools/signal_tools.py` |
| Dataset + adapt | `training/` |
| Specialty adapter | `models/telemetry-action-adapter/` |
| CodeAgent entry | `agent/run_signal_agent.py` |
| Subgraph adapter | `adapters/subgraph_adapter.py` |
| Safety gate | `safety/gate.py` |
| End-to-end pipeline | `pipeline/run.py` |
| Golden replays | `eval/golden_replay.py` |
| Production checklist | `production/CHECKLIST.md` |

---

## Quick start

```bash
git clone https://github.com/ibrarahmad/DrIbrarAhmedAI
cd DrIbrarAhmedAI/smolagents-crypto-analysis

python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Complete working system (matches the video — same idea as RVC demo_complete)
python demo_complete.py

# Or just the pipeline stream
python -m pipeline.run --symbols BTC,ETH,SOL --paper --verbose
```

Offline by default — the specialty adapter is local rules fitted from `train.jsonl`.
No exchange keys. No live orders.

---

## Build the system (video order)

```bash
# 1) Scaffold already done in this folder

# 2) Dataset + adapt the specialty model
python training/build_dataset.py --rows 2000
python training/adapt_model.py --train data/train.jsonl --out models/telemetry-action-adapter

# 2b) One-command complete demo (watch this first in the video)
python demo_complete.py

# 3) Baseline fail vs adapted win
python eval/run_generic.py --row sol_anomaly_31bps
python eval/run_adapted.py --row sol_anomaly_31bps

# 4) Agent tools (paper only)
python agent/run_signal_agent.py --paper

# 5) Adapter + stream producer
python -m adapters.subgraph_adapter --once
python stream_agent.py --adapter subgraph --paper

# 6) Gate + golden tests + latency
python -m safety.gate --proposal eval/adapted_model.out
python -m eval.golden_replay --suite anomaly_v1
python eval/latency_race.py --row sol_anomaly_31bps

# 7) Final full-loop replay
python -m pipeline.run --replay logs/fixtures/sol_anomaly.json --paper
```

---

## Safety

- **Paper-only** — `write_paper_signal` appends JSONL. There is no exchange client.
- `exchange_order` is intentionally missing and raises if called.
- Gate blocks low confidence, incomplete actions, unknown tools, and `live_order`.
- Do **not** put API keys in the browser. Server-side only if you add a remote LLM.

See `production/CHECKLIST.md` before you ever point this at real market data.

---

## Layout

```
smolagents-crypto-analysis/
├── schemas/          telemetry_event + action_object
├── sandbox/          policy.yaml paper-only
├── tools/            normalize · score · write_paper
├── training/         dataset + adapt_model
├── models/           specialty adapter + paper ledger
├── agent/            CodeAgent loop
├── adapters/         subgraph / replay
├── safety/           gate.py
├── eval/             baseline · adapted · golden · latency
├── pipeline/         run.py end-to-end
├── production/       CHECKLIST.md
└── logs/             paper_signals + review_queue + fixtures
```

---

## License

MIT — see the root [LICENSE](../LICENSE).

**▶ [youtube.com/@DrIbrarAhmedAI](https://www.youtube.com/@DrIbrarAhmedAI)**
