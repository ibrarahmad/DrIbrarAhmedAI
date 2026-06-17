<div align="center">

# 🐘 OpenClaw Runs a Real Local Tool

### A PostgreSQL health check through a safe, local agent workflow

Companion scripts for the video on
**[@DrIbrarAhmedAI](https://www.youtube.com/@DrIbrarAhmedAI)**.

<br/>

[![Watch on YouTube](https://img.shields.io/badge/▶_Watch_the_video-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/@DrIbrarAhmedAI)

`Telegram` → `OpenClaw Gateway` → `Ollama (local)` → `read-only psql` → `reply`

</div>

---

> **The whole idea:** the model **never touches PostgreSQL**. An approved,
> read-only tool reads PostgreSQL. OpenClaw controls the path and logs every hop.
> Not another chatbot demo — one safe local tool returning real server output in chat.

---

## 📑 Contents

- [Architecture](#-architecture)
- [The demo contract](#-the-demo-contract)
- [Files](#-files)
- [Prerequisites](#-prerequisites)
- [Setup, step by step](#-setup-step-by-step)
- [What each signal means](#-what-each-signal-means)
- [Refusal is part of the product](#-refusal-is-part-of-the-product)
- [Troubleshooting](#-troubleshooting)

---

## 🧭 Architecture

```
Chat App (Telegram / Discord)
        ↓
OpenClaw Gateway            ← tool policy enforced, every hop logged
        ↓
Ollama Model (localhost:11434)
        ↓
Tool Policy                 ← requires_approval: true
        ↓
pg_health_readonly.sh       ← runs as health_reader
        ↓
PostgreSQL                  ← pg_stat_activity · pg_stat_database (read-only)
        ↓
Reply → Chat                ← summary via Ollama
```

One controlled path. PostgreSQL is the practical test case.

---

## 📜 The demo contract

**Four rules. One tool.**

| ✅ Allowed | ❌ Blocked |
|-----------|-----------|
| Read-only `pg_stat` queries | `sudo` |
| `postgres_health_check` (approval required) | `rm`, `drop`, `delete`, `update`, `insert`, `alter` |
| Summaries via local Ollama | `cat ~/.ssh` and any secret access |

- No superuser access · No write SQL · No shell freedom · **Human approval before every tool run.**

---

## 📁 Files

| File | Purpose |
|------|---------|
| [`health_reader.sql`](health_reader.sql) | Creates the least-privilege `health_reader` role (`pg_monitor` only). |
| [`pg_health_readonly.sh`](pg_health_readonly.sh) | The one approved tool — read-only health probe. |
| [`openclaw.yaml`](openclaw.yaml) | Provider config (Ollama) + the single registered tool with its policy. |
| [`.pgpass.example`](.pgpass.example) | Template for passwordless auth — copy to `~/.pgpass`, `chmod 600`. |
| [`openclaw-gateway.service`](openclaw-gateway.service) | Sample systemd unit so the gateway runs as a hardened service. |

---

## ✅ Prerequisites

The stack exists *before* the demo starts — this is a version check, not a documentary:

```bash
hostname
node -v && npm -v          # v20.11.0  10.2.4
ollama --version           # ollama version 0.3.2
openclaw --version         # openclaw 2026.3.13
psql --version             # psql (PostgreSQL) 15.6
```

---

## 🚀 Setup, step by step

**1. Prove the database is reachable** (if this fails, OpenClaw is not the problem):

```bash
pg_isready -h localhost -p 5432
psql -h localhost -U postgres -d appdb -c "select version();"
```

**2. Create the read-only role** — edit the password placeholder first:

```bash
psql -h localhost -U postgres -d appdb -f health_reader.sql
```

**3. Verify the agent's account works (and is *not* `postgres`):**

```bash
PGPASSWORD='…' psql -h localhost -U health_reader -d appdb -c "select current_user;"
```

**4. Install the tool and test it OUTSIDE the agent:**

```bash
sudo install -m 0755 pg_health_readonly.sh /opt/openclaw/tools/pg_health_readonly.sh
/opt/openclaw/tools/pg_health_readonly.sh
```

> 🔐 **Secrets:** the script never hardcodes the password. Use the template:
> ```bash
> cp .pgpass.example ~/.pgpass && chmod 600 ~/.pgpass   # then edit the password
> ```
> (or export `PGPASSWORD` before running). Never commit the real password.

**5. Point Ollama + register the one tool** — split `openclaw.yaml` into:

```bash
~/.openclaw/config/providers.yaml      # provider block
~/.openclaw/tools/postgres-health.yaml # tool block
```

**5b. (Optional) Run the gateway as a hardened systemd service:**

```bash
sudo cp openclaw-gateway.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now openclaw-gateway
```

**6. Confirm the gateway before any request:**

```bash
openclaw status
# gateway: running · provider: ollama · model: qwen2.5-coder:7b
# channel: telegram connected · tools: restricted
```

**7. Ask in chat** — *"Check PostgreSQL health."* Approve the prompt, and watch
the gateway log the trace: `approval → execute → exit 0 → summary → reply`.

---

## 📊 What each signal means

| Signal | Meaning |
|--------|---------|
| **Server status** | Database accepts connections. |
| **Connections** | Load pressure on the server. |
| **Activity state** | Active vs idle query split. |
| **Cache hit ratio** | Memory effectiveness — **below 95% is a warning.** |
| **Database size** | Growth signal over time. |
| **Replication lag** | Standby delay — **above 60s needs action.** |

Same tool, different numbers → the agent escalates `Risk: Low → Medium` based on
the *real* output, not a script branch.

---

## 🛑 Refusal is part of the product

The policy blocks these **before the model ever sees them**:

| Request | Why it's blocked |
|---------|------------------|
| *"Drop old tables"* | matched `drop` pattern |
| *"Show SSH key"* | matched `cat ~/.ssh` |
| *"Restart PostgreSQL"* | no service-control tool is registered |

---

## 🩺 Troubleshooting

| Symptom | Fix |
|---------|-----|
| `pg_isready` fails | Fix PostgreSQL/connectivity first — not an OpenClaw issue. |
| `permission denied` in script | You're not using `health_reader`, or `pg_monitor` wasn't granted. |
| Model timeout (`provider=ollama`) | Logs first, restart second, status third: `journalctl -u openclaw-gateway -n 80 --no-pager` → `sudo systemctl restart openclaw-gateway` → `openclaw status`. |
| Tool runs without asking | Set `requires_approval: true` in the tool YAML and restart the gateway. |

---

## 🧾 End-to-end recap (pause &amp; copy)

```bash
pg_isready -h localhost -p 5432
/opt/openclaw/tools/pg_health_readonly.sh
ollama list
openclaw status
journalctl -u openclaw-gateway -n 40 --no-pager
openclaw pairing status
```

---

<div align="center">

**▶ [Watch the full build on YouTube](https://www.youtube.com/@DrIbrarAhmedAI)**

_Companion material only. Read-only by design — verify privileges in your own environment._

⭐ _Found this useful? Star the repo._

</div>
