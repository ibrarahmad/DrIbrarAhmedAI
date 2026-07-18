<div align="center">

# 🤖 Dr. Ibrar Ahmed AI

### Hands-on AI &amp; security builds — companion code for every video

A new build every week. Clone the repo, open the folder for the video you're
watching, and follow along.

<br/>

[![YouTube Channel](https://img.shields.io/badge/YouTube-%40DrIbrarAhmedAI-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/@DrIbrarAhmedAI)
[![Subscribe](https://img.shields.io/badge/Subscribe-Free-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/@DrIbrarAhmedAI?sub_confirmation=1)

[![License: MIT](https://img.shields.io/badge/License-MIT-22D3EE?style=flat-square)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-A855F7?style=flat-square)](CONTRIBUTING.md)
[![Made with ❤️](https://img.shields.io/badge/Made%20with-%E2%9D%A4-F472B6?style=flat-square)](https://www.youtube.com/@DrIbrarAhmedAI)

</div>

---

## 📑 Contents

- [About](#-about)
- [Builds](#-builds)
- [Quick start](#-quick-start)
- [Repository layout](#-repository-layout)
- [Safety first](#-safety-first)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 About

This repo holds the companion code, setup scripts, and resources for the YouTube
channel **[@DrIbrarAhmedAI](https://www.youtube.com/@DrIbrarAhmedAI)**.

Every build is **self-contained**: each folder maps to one video and ships its
own README with prerequisites, step-by-step scripts, and a security checklist.
No guesswork — what you see on screen is what runs here.

---

## 🚀 Builds

| Video | Folder | What you build |
|-------|--------|----------------|
| **Build And Secure Your Own AI Agent** | [`openclaw-setup-scripts/`](openclaw-setup-scripts/) | Install OpenClaw, connect Telegram, run real projects, and lock it down. |
| **OpenClaw Runs a Real Local Tool** | [`postgres-health-agent/`](postgres-health-agent/) | A safe, read-only PostgreSQL health check via a local agent — approval-gated, summarized by local Ollama, delivered to chat. |
| **I Let AI Pick My Next Viral YouTube Video** | [`viral-youtube-agent/`](viral-youtube-agent/) | A Python pipeline that scores video ideas from real YouTube signals (title velocity + comment demand) and writes a production brief. Runs offline on sample data. |
| **EP 02 — AI Beat My Hook by 48 Points** | [`hook-agent/`](hook-agent/) | One local command scores 10 video hooks on 3 signals (curiosity / specificity / pattern), rejects below 80, and writes a film-ready brief. No API key. |
| **Clone Your Voice Free — No ElevenLabs (RVC)** | [`rvc-voice-cloning/`](rvc-voice-cloning/) | Official [RVC library](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion) (`rvc infer`) + `demo_complete.py`. Record → train → play. No ElevenLabs. |
| **Fine-Tuning smolagents for Real-Time Crypto Analysis** | [`smolagents-crypto-analysis/`](smolagents-crypto-analysis/) | Paper-only telemetry loop: adapted model → CodeAgent tools → safety gate → paper logs. Run `demo_complete.py`. |

> 🆕 More builds added each week — ⭐ star the repo and 🔔 subscribe so you never miss one.

---

## ⚡ Quick start

```bash
# 1. Clone
git clone https://github.com/ibrarahmad/DrIbrarAhmedAI
cd DrIbrarAhmedAI

# 2. Open the folder for the video you're watching
cd openclaw-setup-scripts

# 3. Read its README, then run the scripts in order
cat README.md
```

Each folder's README spells out exactly which script to run and when.

---

## 🗂 Repository layout

```
DrIbrarAhmedAI/
├── README.md                 ← you are here
├── LICENSE                   ← MIT
├── CONTRIBUTING.md           ← how to help
├── SECURITY.md               ← responsible disclosure
├── openclaw-setup-scripts/   ← "Build And Secure Your Own AI Agent"
│   ├── README.md             ← full walkthrough + checklist
│   ├── 01-install.sh         ← install + doctor
│   ├── 02-onboard.sh         ← model provider + Telegram
│   ├── 03-harden.sh          ← audit, allowlist, firewall
│   ├── 04-tunnel.sh          ← SSH tunnel to the web UI
│   └── workspace/            ← plain-file templates (BOOT/soul/MEMORY/USER/TOOLS + agents.mmd)
├── postgres-health-agent/    ← "OpenClaw Runs a Real Local Tool"
│   ├── README.md             ← architecture, setup, troubleshooting
│   ├── health_reader.sql     ← least-privilege read-only role
│   ├── pg_health_readonly.sh ← the one approved tool
│   ├── openclaw.yaml         ← Ollama provider + tool policy
│   ├── .pgpass.example       ← passwordless auth template
│   └── openclaw-gateway.service ← hardened systemd unit
├── viral-youtube-agent/      ← "I Let AI Pick My Next Viral YouTube Video"
│   ├── README.md             ← how it works, config, rubric
│   ├── viral_idea_agent.py   ← orchestrator (runs the whole pipeline)
│   ├── collect_*.py / analyze_*.py / *_ideas.py / build_hook.py
│   ├── prompts/idea_score.txt← the scoring rubric
│   ├── data/ (sample CSVs)   └── output/ (generated brief)
├── hook-agent/               ← "EP 02 — AI Beat My Hook by 48 Points"
│   ├── README.md             ← signals, pipeline, recorded vs live
│   ├── hook_agent.py         ← the one command (recorded run + --live)
│   ├── scrape/extract/generate/score_*.py
│   ├── prompts/hook_score.txt← the 3-signal rubric
│   └── data/ (niche lib + recorded run)  └── output/ (generated brief)
├── rvc-voice-cloning/        ← "Clone Your Voice Free — No ElevenLabs (RVC)"
│   ├── README.md             ← walkthrough + tonight checklist 1→12
│   ├── record_voice.py       ← capture YOUR voice into data/raw/
│   ├── prepare.py / train_prep.py / infer.py / play_clone.py
│   ├── pipeline.py / quality_gate.py / compare.py
│   ├── consent.yaml / config.yaml
│   └── models/rvc/           ← place your .pth + .index here
└── smolagents-crypto-analysis/ ← "Fine-Tuning smolagents for Real-Time Crypto Analysis"
    ├── README.md             ← paper-only loop walkthrough
    ├── demo_complete.py      ← one-command complete demo
    ├── pipeline/ + tools/ + safety/
    ├── training/ + models/   ← specialty adapter
    └── eval/                 ← baseline fail · adapted win · golden
```

---

## 🛡 Safety first

These builds put capable agents and real tools on real hosts.

> **Demo fast. Secure faster.**
> Don't hand an agent full tools until logs, allowlists, and approvals are
> working. Every folder's README walks through the hardening steps — follow them.

See [SECURITY.md](SECURITY.md) for responsible disclosure.

---

## 🤝 Contributing

Spotted a bug, a broken command, or a clearer way to do something? Issues and
pull requests are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 📄 License

Released under the [MIT License](LICENSE). Use it, learn from it, build on it.

<div align="center">

<br/>

**▶ [youtube.com/@DrIbrarAhmedAI](https://www.youtube.com/@DrIbrarAhmedAI)** · Maintained by Ibrar Ahmed

⭐ _If these builds helped you, a star goes a long way._

</div>
