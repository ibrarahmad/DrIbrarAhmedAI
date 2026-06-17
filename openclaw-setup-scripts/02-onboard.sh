#!/usr/bin/env bash
#
# 02-onboard.sh — Connect a model provider and pair Telegram.
# Companion to "Build And Secure Your Own AI Agent" (@DrIbrarAhmedAI).
#
# Maps to the deck: "Install, Then Connect Telegram".
# OpenClaw is a harness, not its own AI: pick the brain, then the channel.
set -euo pipefail

run() { echo "+ $*"; "$@"; }

if ! command -v openclaw >/dev/null 2>&1; then
  echo "ERROR: openclaw not found. Run ./01-install.sh first." >&2
  exit 1
fi

cat <<'EOF'
==> Onboarding

The interactive wizard will:
  1. Ask for a model provider (e.g. OpenAI) and open a device-auth URL.
     Open that URL in your LOCAL browser, approve, paste the redirect URL back.
  2. Ask for a channel — choose Telegram.
  3. Ask for a BotFather token:
       - Open Telegram, message @BotFather, send /newbot
       - Follow the prompts, copy the token it gives you
       - Paste it here to pair.

Treat the redirect URL and bot token like passwords. Do not share them.
EOF

run openclaw onboard

echo
echo "==> Verifying"
run openclaw doctor
run openclaw gateway status

cat <<'EOF'

If gateway status shows "● running" and doctor is green, message your bot
on Telegram to begin. Send a quick "status?" — a reply confirms the live test.

Tip: copy the templates in ./workspace into ~/openclaw/workspace and edit
USER.md / MEMORY.md so the agent speaks to you.

Next:
  ./03-harden.sh     # audit, allowlist, firewall — BEFORE giving it real tools
EOF
