#!/usr/bin/env bash
# Build + install Retrieval-based Voice Conversion (free, local — no ElevenLabs).
# Upstream: https://github.com/RVC-Project/Retrieval-based-Voice-Conversion
# Training UI (recommended): https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
PARENT="$(cd "$ROOT/.." && pwd)"
RVC_LIB="${RVC_LIB_DIR:-$PARENT/Retrieval-based-Voice-Conversion}"
RVC_WEBUI="${RVC_WEBUI_DIR:-$PARENT/Retrieval-based-Voice-Conversion-WebUI}"

echo "════════════════════════════════════════"
echo " BUILD RVC (open-source voice conversion)"
echo "════════════════════════════════════════"
echo "Companion: $ROOT"
echo "RVC lib:   $RVC_LIB"
echo "RVC WebUI: $RVC_WEBUI"
echo ""

# --- 1) Library (API / CLI) ---
if [[ ! -d "$RVC_LIB/.git" ]]; then
  echo "[1/4] Clone Retrieval-based-Voice-Conversion…"
  git clone --depth 1 https://github.com/RVC-Project/Retrieval-based-Voice-Conversion.git "$RVC_LIB"
else
  echo "[1/4] RVC library already present → $RVC_LIB"
fi

echo "[2/4] Install RVC library into current Python (editable if possible)…"
python3 -m pip install -U pip
if [[ -f "$RVC_LIB/pyproject.toml" || -f "$RVC_LIB/setup.py" ]]; then
  python3 -m pip install -e "$RVC_LIB" || python3 -m pip install "git+https://github.com/RVC-Project/Retrieval-based-Voice-Conversion.git"
else
  python3 -m pip install "git+https://github.com/RVC-Project/Retrieval-based-Voice-Conversion.git" || true
  echo "  (library README may still be early — WebUI path below is the practical train/infer UI)"
fi

# --- 2) WebUI (train + infer — what most creators use) ---
if [[ ! -d "$RVC_WEBUI/.git" ]]; then
  echo "[3/4] Clone Retrieval-based-Voice-Conversion-WebUI…"
  git clone --depth 1 https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI.git "$RVC_WEBUI"
else
  echo "[3/4] RVC WebUI already present → $RVC_WEBUI"
fi

echo "[4/4] WebUI requirements (may take a few minutes)…"
if [[ -f "$RVC_WEBUI/requirements.txt" ]]; then
  python3 -m pip install -r "$RVC_WEBUI/requirements.txt" || {
    echo "  WARNING: full WebUI pip install failed — install PyTorch for your GPU/CPU from pytorch.org, then retry."
  }
else
  echo "  No requirements.txt found — follow WebUI README install steps."
fi

echo ""
echo "NEXT — configure this companion to use your RVC install:"
echo "  python configure_rvc.py --webui \"$RVC_WEBUI\""
echo ""
echo "Then record → prepare → train in WebUI → copy .pth+.index → models/rvc/ → infer → play"
echo "Docs: README.md  ·  Upstream: https://github.com/RVC-Project/Retrieval-based-Voice-Conversion"
