# OpenClaw — Build And Secure Your Own AI Agent

Companion setup scripts for the video **"Build And Secure Your Own AI Agent"**
by [@DrIbrarAhmedAI](https://github.com/ibrarahmad/DrIbrarAhmedAI).

> OpenClaw is a *gateway* — a small service that runs on your own host and ties
> together any model, your channels (Telegram), persistent memory in plain files,
> and real tools (MCP) on a leash. It is **not** an AI itself; you pick the brain.

These scripts walk you through the exact flow shown in the video:

```
Install  →  Connect Telegram  →  Run real projects  →  Lock it down
```

---

## ⚠️ Before you start

- Run on a host you control (a VPS or a lab box). ~5 minutes to first message.
- You need **Node 20+** and `curl`. Check with `node -v`.
- **Never** expose the web UI to `0.0.0.0`. Keep it on loopback and reach it over
  an SSH tunnel (see `04-tunnel.sh`).
- A capable agent on a public host is a live attack surface. Do **not** hand it
  full tools until logs, allowlists, and approvals are working. Demo fast,
  secure faster.

---

## Scripts

| # | Script | What it does | Maps to slides |
|---|--------|--------------|----------------|
| 1 | `01-install.sh` | Installs OpenClaw and runs `openclaw doctor` | Setup First / Install |
| 2 | `02-onboard.sh` | Connects a model provider and pairs Telegram (BotFather) | Install + Telegram |
| 3 | `03-harden.sh`  | Security audit, loopback bind, DM allowlist, `ufw` firewall | Security / Lock It Down |
| 4 | `04-tunnel.sh`  | Opens an SSH tunnel to the loopback web UI | Lock It Down |

All scripts are idempotent-friendly and print each command before running it.

### Quick start

```bash
chmod +x *.sh
./01-install.sh        # install + doctor
./02-onboard.sh        # model provider + Telegram pairing (interactive)
./03-harden.sh         # audit --fix, allowlist, firewall
./04-tunnel.sh srv-01  # reach the UI on http://127.0.0.1:8787
```

---

## The 8-check "real setup" proof

You have a real, working agent when all eight are green:

- [x] Node ready
- [x] OpenClaw installed
- [x] Model connected
- [x] Telegram paired
- [x] MCP configured
- [x] Allowlist enabled
- [x] Logs visible
- [x] Live test passed

Run `openclaw doctor` and `openclaw security audit` at any time to re-check.

---

## The workspace is just plain files

Everything the agent "knows" lives in `~/openclaw/workspace` — no mystery box:

| File | Purpose |
|------|---------|
| `BOOT.md`   | Startup routine — read first. |
| `MEMORY.md` | Long-term memory you can edit. |
| `USER.md`   | Who you are to the agent. |
| `TOOLS.md`  | What it is allowed to use. |
| `agents.mmd`| Agent graph. |

Open them, read them, audit them. Change one fact and the agent propagates it
across soul, identity, memory, and journal.

---

## Two starter projects (prompts from the video)

**Project 1 — News briefing**
> Pull cybersecurity news from Reddit, Hacker News, and YouTube. Do not just dump
> links — rate each item for my time and build a dashboard.

**Project 2 — IT engineer**
> You are an IT engineer. Monitor the server you are on. Check health and
> security, do not break anything, then build me a live dashboard.

---

## Security model (read this)

- `tools.profile` — what the agent can *see*.
- `tools.exec` — how approval works: `full | allowlist | deny`, ask `off | always | on-miss`.
- **Red lines** — instruction-level guidance, **not** a hard, deterministic guarantee.
- **ClawHub skills**: 33,000+ exist and roughly 12% have carried malware. Vet
  every skill before installing. Allow exactly the tools you need; the risky ones
  should *ask* first.

```bash
openclaw mcp list
openclaw tools allow zapier.send_email   # others stay gated
openclaw logs --follow                    # watch every action fire
```

---

_Companion material only. Replace `openclaw.ai` commands with the tool's current
official docs if anything has changed since recording._
