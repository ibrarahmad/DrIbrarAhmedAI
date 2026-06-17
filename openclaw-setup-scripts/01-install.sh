#!/usr/bin/env bash
#
# 01-install.sh — Install OpenClaw and verify the host.
# Companion to "Build And Secure Your Own AI Agent" (@DrIbrarAhmedAI).
#
# Maps to the deck: "Setup First" -> "Install".
set -euo pipefail

run() { echo "+ $*"; "$@"; }

echo "==> Checking prerequisites"
if ! command -v curl >/dev/null 2>&1; then
  echo "ERROR: curl is required." >&2
  exit 1
fi

if ! command -v node >/dev/null 2>&1; then
  echo "ERROR: Node.js is required (Node 20+). Install it first." >&2
  exit 1
fi

NODE_VER="$(node -v)"
echo "    node ${NODE_VER}"
NODE_MAJOR="${NODE_VER#v}"; NODE_MAJOR="${NODE_MAJOR%%.*}"
if [ "${NODE_MAJOR}" -lt 20 ]; then
  echo "ERROR: Node 20+ required, found ${NODE_VER}." >&2
  exit 1
fi

if command -v openclaw >/dev/null 2>&1; then
  echo "==> OpenClaw already installed: $(openclaw --version 2>/dev/null || echo unknown)"
else
  echo "==> Installing OpenClaw (one-liner straight from the docs)"
  run bash -c 'curl -fsSL https://openclaw.ai/install.sh | bash'
fi

echo "==> Running doctor"
run openclaw doctor

cat <<'EOF'

Next:
  ./02-onboard.sh    # connect a model provider + pair Telegram

If doctor shows "model key: not set", that's expected — you set it during onboard.
EOF
