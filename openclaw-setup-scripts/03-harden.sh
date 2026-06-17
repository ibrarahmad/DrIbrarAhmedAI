#!/usr/bin/env bash
#
# 03-harden.sh — Lock down the gateway before it gets real tools.
# Companion to "Build And Secure Your Own AI Agent" (@DrIbrarAhmedAI).
#
# Maps to the deck: "The Security Risks Are Real" -> "Audit, Tunnel, Firewall".
#
# Default posture:
#   - web UI on loopback (127.0.0.1), never 0.0.0.0
#   - DM allowlist enabled (only you can talk to it)
#   - firewall allows SSH only
#   - tools default to allowlist + ask-on-miss
set -euo pipefail

run() { echo "+ $*"; "$@"; }

if ! command -v openclaw >/dev/null 2>&1; then
  echo "ERROR: openclaw not found. Run ./01-install.sh first." >&2
  exit 1
fi

echo "==> Security audit (before)"
run openclaw security audit || true

echo
echo "==> Applying fixes (binds UI to 127.0.0.1, enables DM allowlist)"
run openclaw security audit --fix

echo
echo "==> Tool permissions: allowlist + ask on-miss"
run openclaw config set tools.exec.security allowlist
run openclaw config set tools.exec.ask on-miss

echo
echo "==> Firewall (SSH only)"
if command -v ufw >/dev/null 2>&1; then
  run sudo ufw allow 22/tcp
  run sudo ufw --force enable
  run sudo ufw status verbose
else
  echo "    ufw not found — skipping. Ensure your provider firewall allows only SSH (22)."
fi

echo
echo "==> Restarting gateway to apply"
run openclaw gateway restart

echo
echo "==> Security audit (after)"
run openclaw security audit

cat <<'EOF'

Aim for: 0 critical. A single warning (e.g. SSH exposed) is expected.

Reach the web UI safely with an SSH tunnel:
  ./04-tunnel.sh <ssh-host>

Then connect tools one at a time:
  openclaw mcp list
  openclaw tools allow <server>.<tool>   # everything else stays gated
  openclaw logs --follow                  # watch each action fire
EOF
