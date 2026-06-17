<div align="center">

# 🦾 Build And Secure Your Own AI Agent

### OpenClaw — install it, connect Telegram, run real projects, lock it down

Companion setup scripts for the video on
**[@DrIbrarAhmedAI](https://www.youtube.com/@DrIbrarAhmedAI)**.

<br/>

[![Watch on YouTube](https://img.shields.io/badge/▶_Watch_the_video-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/@DrIbrarAhmedAI)

`Install` → `Connect Telegram` → `Run real projects` → `Lock it down`

</div>

---

> **What is OpenClaw?** A *gateway* — a small service that runs on **your own host**
> and ties together any model, your channels (Telegram), persistent memory in
> plain files, and real tools (MCP) **on a leash**. It is **not** an AI itself;
> you pick the brain.

---

## 📑 Contents

- [Before you start](#-before-you-start)
- [The scripts](#-the-scripts)
- [Quick start](#-quick-start)
- [The 8-check proof](#-the-8-check-proof)
- [The workspace is just plain files](#-the-workspace-is-just-plain-files)
- [Two starter projects](#-two-starter-projects)
- [Schedules & heartbeats](#-schedules--heartbeats)
- [Security model](#-security-model)
- [Troubleshooting](#-troubleshooting)

---

## ⚠️ Before you start

| Requirement | Why |
|-------------|-----|
| A host **you control** (VPS or lab box) | The agent runs as a service on it. ~5 min to first message. |
| **Node 20+** and `curl` | Check with `node -v`. The installer needs both. |
| **Never** bind the web UI to `0.0.0.0` | Keep it on loopback; reach it over an SSH tunnel (`04-tunnel.sh`). |
| Treat tokens like passwords | Model redirect URLs and BotFather tokens are secrets. |

> 🛑 A capable agent on a public host is a **live attack surface**. Don't hand it
> full tools until logs, allowlists, and approvals work. **Demo fast, secure faster.**

---

## 🧰 The scripts

| # | Script | What it does | Slide |
|:-:|--------|--------------|-------|
| 1 | [`01-install.sh`](01-install.sh) | Checks Node/curl, installs OpenClaw, runs `openclaw doctor` | *Setup First* |
| 2 | [`02-onboard.sh`](02-onboard.sh) | Connects a model provider + pairs Telegram via BotFather | *Install + Telegram* |
| 3 | [`03-harden.sh`](03-harden.sh)  | Security audit, loopback bind, DM allowlist, `ufw` firewall | *Lock It Down* |
| 4 | [`04-tunnel.sh`](04-tunnel.sh)  | Opens an SSH tunnel to the loopback web UI | *Lock It Down* |

> Every script prints each command before running it and fails loudly (`set -euo pipefail`).

---

## ⚡ Quick start

```bash
chmod +x *.sh

./01-install.sh        # install + doctor
./02-onboard.sh        # model provider + Telegram pairing (interactive)
./03-harden.sh         # audit --fix, allowlist, firewall
./04-tunnel.sh srv-01  # reach the UI at http://127.0.0.1:8787
```

---

## ✅ The 8-check proof

You have a **real, working agent** when all eight go green:

| | | | |
|---|---|---|---|
| ✅ Node ready | ✅ OpenClaw installed | ✅ Model connected | ✅ Telegram paired |
| ✅ MCP configured | ✅ Allowlist enabled | ✅ Logs visible | ✅ Live test passed |

Re-check anytime:

```bash
openclaw doctor
openclaw security audit
```

---

## 📂 The workspace is just plain files

Everything the agent "knows" lives in `~/openclaw/workspace` — no mystery box:

| File | Purpose |
|------|---------|
| `BOOT.md`    | Startup routine — read first. |
| `soul.md`    | Core identity & canon facts — the deepest layer. |
| `MEMORY.md`  | Long-term memory + journal you can edit. |
| `USER.md`    | Who you are to the agent. |
| `TOOLS.md`   | What it is allowed to use. |
| `agents.mmd` | The agent graph. |

Open them, read them, audit them. Tell the agent a new core fact and it
propagates across **soul, identity, memory, and journal** at once — then it
shows you every change (slide 10):

> *"Your favorite is now canon. Update your soul, identity, and memory."*
> → `soul.md ✓` · `identity ✓` · `memory + journal ✓`

📁 **Ready-to-use templates ship in [`workspace/`](workspace/)** — copy them into
`~/openclaw/workspace` and edit `USER.md` / `MEMORY.md` so the agent speaks to you:

```bash
cp -R workspace/* ~/openclaw/workspace/
```

`agents.mmd` renders the gateway flow at [mermaid.live](https://mermaid.live).

---

## 🚀 Two starter projects

Prompts straight from the video — paste them into Telegram:

> **🗞 Project 1 — News briefing**
> *"Pull cybersecurity news from Reddit, Hacker News, and YouTube. Do not just
> dump links — rate each item for my time and build a dashboard."*

> **🖥 Project 2 — IT engineer**
> *"You are an IT engineer. Monitor the server you are on. Check health and
> security, do not break anything, then build me a live dashboard."*

---

## ⏰ Schedules & heartbeats

Ask in plain language on Telegram — the agent creates a **real cron job** (and
checks for duplicates first), so it keeps working when you're away:

> *"Every 30 minutes, remind me to drink coffee."*

| Schedule | Job | |
|----------|-----|---|
| `*/30 * * * *` | Coffee reminder | scheduled |
| `0 6 * * *`    | Morning news briefing | scheduled |
| `0 * * * *`    | Hourly check-in heartbeat | scheduled |

> Heartbeats are what make it feel *alive* — it acts on a timer, not just on reply.

---

## 🛡 Security model

| Control | What it governs |
|---------|-----------------|
| `tools.profile` | What the agent can **see**. |
| `tools.exec` | How approval works: `full \| allowlist \| deny`, ask `off \| always \| on-miss`. |
| **Red lines** | Instruction-level guidance — **not** a hard, deterministic guarantee. |

Allow exactly what you need; the risky actions should **ask first**:

```bash
openclaw mcp list
openclaw tools allow zapier.send_email   # everything else stays gated
openclaw logs --follow                    # watch every action fire
```

> ⚠️ **ClawHub skills:** 33,000+ exist and roughly **12% have carried malware**.
> Vet every skill before installing it.

---

## 🩺 Troubleshooting

| Symptom | Fix |
|---------|-----|
| `doctor` says *"model key: not set"* | Expected before onboarding — run `./02-onboard.sh`. |
| `openclaw: command not found` | Re-run `./01-install.sh`; ensure your shell `PATH` is reloaded. |
| Can't reach the web UI | It's on loopback by design — use `./04-tunnel.sh <host>`. |
| Audit shows a warning after hardening | One warning (e.g. SSH exposed) is expected; aim for **0 critical**. |

---

<div align="center">

**▶ [Watch the full build on YouTube](https://www.youtube.com/@DrIbrarAhmedAI)**

_Companion material only. If `openclaw.ai` commands have changed since recording,
defer to the tool's current official docs._

⭐ _Found this useful? Star the repo._

</div>
