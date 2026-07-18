#!/usr/bin/env bash
# Complete setup for Retrieval-based-Voice-Conversion (official library)
# https://github.com/RVC-Project/Retrieval-based-Voice-Conversion
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo "════════════════════════════════════════════════════"
echo " COMPLETE RVC SETUP (official library + optional WebUI)"
echo " https://github.com/RVC-Project/Retrieval-based-Voice-Conversion"
echo "════════════════════════════════════════════════════"
echo ""

python3 -m pip install -U pip wheel
python3 -m pip install -r requirements.txt

echo ""
echo "[1/4] Install official RVC library (pip)…"
python3 -m pip install -U "git+https://github.com/RVC-Project/Retrieval-based-Voice-Conversion.git@develop"

echo ""
echo "[2/4] Initialize RVC assets in this folder (rvc init / dlmodel)…"
# Prefer working directory = companion root so assets/ lives next to config.yaml
if command -v rvc >/dev/null 2>&1; then
  if [[ ! -d assets ]]; then
    rvc init || rvc env create || true
  fi
  rvc dlmodel || true
else
  echo "  WARNING: rvc CLI not on PATH yet - open a new shell or:"
  echo "    python -m rvc.wrapper.cli.cli --help"
fi

echo ""
echo "[3/4] Optional WebUI (recommended for TRAINING UI)…"
PARENT="$(cd "$ROOT/.." && pwd)"
WEBUI="$PARENT/Retrieval-based-Voice-Conversion-WebUI"
if [[ ! -d "$WEBUI/.git" ]]; then
  git clone --depth 1 https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI.git "$WEBUI" || true
else
  echo "  WebUI already at $WEBUI"
fi

echo ""
echo "[4/4] Wire companion config.yaml…"
python3 configure_rvc.py --prefer-library ${WEBUI:+--webui "$WEBUI"} || python3 configure_rvc.py --prefer-library

echo ""
echo "DONE. Next:"
echo "  python configure_rvc.py --check"
echo "  python open_recorder.py          # record YOUR voice → data/raw/"
echo "  python prepare.py --input data/raw"
echo "  # train in WebUI (or when library train lands), copy .pth → models/rvc/"
echo "  python demo_complete.py          # full demo: TTS→RVC→play"
echo ""
echo "Docs: docs/RVC_SETUP.md"
