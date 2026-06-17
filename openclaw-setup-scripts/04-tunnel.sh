#!/usr/bin/env bash
#
# 04-tunnel.sh — Reach the loopback web UI over an SSH tunnel.
# Companion to "Build And Secure Your Own AI Agent" (@DrIbrarAhmedAI).
#
# The web UI is bound to 127.0.0.1 on the server (see 03-harden.sh), so it is
# NOT reachable from the internet. This forwards a local port to it securely.
#
# Usage:
#   ./04-tunnel.sh <ssh-host> [remote-port] [local-port]
#
# Example:
#   ./04-tunnel.sh srv-01            # -> http://127.0.0.1:8787
#   ./04-tunnel.sh root@1.2.3.4 8787 9000
set -euo pipefail

HOST="${1:-}"
REMOTE_PORT="${2:-8787}"
LOCAL_PORT="${3:-8787}"

if [ -z "${HOST}" ]; then
  echo "Usage: $0 <ssh-host> [remote-port] [local-port]" >&2
  exit 1
fi

echo "==> Tunneling localhost:${LOCAL_PORT} -> ${HOST}:127.0.0.1:${REMOTE_PORT}"
echo "    Open http://127.0.0.1:${LOCAL_PORT} in your browser."
echo "    Press Ctrl-C to close the tunnel."
echo
echo "+ ssh -N -L ${LOCAL_PORT}:127.0.0.1:${REMOTE_PORT} ${HOST}"
exec ssh -N -L "${LOCAL_PORT}:127.0.0.1:${REMOTE_PORT}" "${HOST}"
