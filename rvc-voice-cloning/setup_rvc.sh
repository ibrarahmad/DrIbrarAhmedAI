#!/usr/bin/env bash
# Complete setup for Retrieval-based-Voice-Conversion (official library + WebUI)
# Must match the video Slide 4 success lines:
#   [pin] library @7b284a634667
#   [pin] WebUI @c1e005f0e226 (hard fail if clone/pip/models fail)
#   [ok]  library · WebUI deps · download_models
#
# https://github.com/RVC-Project/Retrieval-based-Voice-Conversion
# WebUI lives next to the companion:
#   <parent>/Retrieval-based-Voice-Conversion-WebUI
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

PARENT="$(cd "$ROOT/.." && pwd)"
WEBUI="$PARENT/Retrieval-based-Voice-Conversion-WebUI"

# Tested pins (do not float on develop / HEAD)
RVC_LIB_PIN="7b284a634667c34103eaaeed972b48ccdb4b893e"
RVC_LIB_SHORT="7b284a634667"
WEBUI_PIN="c1e005f0e226a3c2a10adfc8a9be03a6944506d0"
WEBUI_SHORT="c1e005f0e226"

die() { echo "FAIL: $*" >&2; exit 1; }

echo "════════════════════════════════════════════════════"
echo " COMPLETE RVC SETUP (library + WebUI train deps)"
echo " Library pin: $RVC_LIB_PIN"
echo " WebUI pin:   $WEBUI_PIN"
echo " WebUI path:  $WEBUI"
echo "════════════════════════════════════════════════════"
echo ""

# --- Clean Mac gates ---
if [[ -z "${VIRTUAL_ENV:-}" ]]; then
  die "Activate the companion venv first:
  cd \"$ROOT\"
  python3 -m venv .venv && source .venv/bin/activate
  bash setup_rvc.sh"
fi

command -v brew >/dev/null 2>&1 || die "Homebrew is required on a clean Mac.
  Install: https://brew.sh
  Then: brew install ffmpeg git"

command -v git >/dev/null 2>&1 || die "git is required. brew install git"

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "[0/6] Installing FFmpeg via Homebrew…"
  brew install ffmpeg || die "brew install ffmpeg failed"
fi
ffmpeg -version | head -1

PY_OK="$(
  python3 - <<'PY'
import sys
v = sys.version_info
# Pinned RVC library requires Python >=3.10 (see package metadata). Cap at 3.11 for Gradio/torch stability.
ok = (v.major, v.minor) >= (3, 10) and (v.major, v.minor) < (3, 12)
print("1" if ok else "0")
PY
)" || die "python3 check failed"
if [[ "$PY_OK" != "1" ]]; then
  die "Need Python 3.10–3.11 for the pinned RVC library (you have $(python3 --version)).
  On a clean Mac:
    brew install python@3.11
    python3.11 -m venv .venv && source .venv/bin/activate
    bash setup_rvc.sh"
fi
echo "[ok] $(python3 --version) · venv=$VIRTUAL_ENV"

echo ""
echo "[1/6] pip install companion requirements…"
python3 -m pip install -U pip wheel || die "pip upgrade failed"
python3 -m pip install -r requirements.txt || die "companion requirements.txt failed"

echo ""
echo "[2/6] Install official RVC library (pinned — not develop)…"
# macOS + Homebrew FFmpeg 8: RVC pins av^11 which tries a source build and fails.
# Prefetch a modern av binary wheel, install RVC with --no-deps, then install the rest.
python3 -m pip install -U poetry-core \
  || die "poetry-core install failed (needed to build pinned RVC)"
python3 -m pip install "av==18.0.0" \
  || die "av binary wheel install failed (needed on FFmpeg 8 Macs)"
python3 -m pip install --no-deps \
  "git+https://github.com/RVC-Project/Retrieval-based-Voice-Conversion.git@${RVC_LIB_PIN}" \
  || die "pinned RVC library install failed (@${RVC_LIB_PIN})"
# Runtime deps from the pinned pyproject (av already satisfied at 18 for FFmpeg 8)
python3 -m pip install \
  "torch>=2.1.0" \
  "soundfile>=0.12.1,<0.13" \
  "librosa>=0.10.1,<0.11" \
  "praat-parselmouth>=0.4.3" \
  "pyworld>=0.3.4" \
  "torchcrepe>=0.0.22,<0.0.23" \
  "faiss-cpu>=1.7.4" \
  "python-dotenv>=1.0.0" \
  "pydub>=0.25.1" \
  "click>=8.1.7" \
  "tensorboardx>=2.6.2.2" \
  "poethepoet>=0.24.4,<0.25" \
  "python-multipart>=0.0.6,<0.0.7" \
  "numba==0.58.1" \
  "git+https://github.com/Tps-F/fairseq.git@main" \
  || die "RVC runtime dependencies failed"

# Prove the package imports (beginner-facing hard check)
python3 - <<'PY' || die "RVC library import failed after pip install"
import importlib.util
if importlib.util.find_spec("rvc") is None:
    raise SystemExit("import rvc failed")
print("  import rvc: OK")
PY
echo "[pin] library @${RVC_LIB_SHORT}"

echo ""
echo "[3/6] Initialize companion RVC assets (rvc init / dlmodel)…"
command -v rvc >/dev/null 2>&1 \
  || die "rvc CLI not on PATH after library install — confirm venv is active and re-run"
if [[ ! -d assets ]]; then
  rvc init || rvc env create || die "rvc init / env create failed"
fi
rvc dlmodel || die "rvc dlmodel failed — network or assets download error"

echo ""
echo "[4/6] Clone / pin WebUI…"
if [[ ! -d "$WEBUI/.git" ]]; then
  git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI.git "$WEBUI" \
    || die "git clone WebUI failed"
fi
(
  cd "$WEBUI" || die "cannot cd WebUI"
  # Fetch the exact pin (full SHA). No || true — pin must resolve.
  git fetch --depth 1 origin "$WEBUI_PIN" \
    || git fetch origin "$WEBUI_PIN" \
    || die "git fetch WebUI pin $WEBUI_PIN failed"
  git checkout --detach "$WEBUI_PIN" \
    || die "WebUI checkout $WEBUI_PIN failed"
  HEAD="$(git rev-parse HEAD)"
  [[ "$HEAD" == "$WEBUI_PIN" ]] \
    || die "WebUI HEAD is $HEAD — expected $WEBUI_PIN"
  echo "  WebUI at $(git rev-parse --short HEAD)"
)
echo "[pin] WebUI @${WEBUI_SHORT} (hard fail if clone/pip/models fail)"

echo ""
echo "[5/6] Install WebUI dependencies + download train assets…"
[[ -d "$WEBUI" ]] || die "WebUI folder missing: $WEBUI"
(
  cd "$WEBUI" || die "cannot cd WebUI"
  [[ -f requirements.txt ]] || die "WebUI requirements.txt missing"
  echo "  pip install -r requirements.txt (WebUI)"
  python3 -m pip install -r requirements.txt \
    || die "WebUI pip install failed — see docs/TROUBLESHOOT.md"
  [[ -f tools/download_models.py ]] \
    || die "tools/download_models.py missing on pinned WebUI — wrong revision?"
  echo "  python tools/download_models.py"
  python3 tools/download_models.py \
    || die "tools/download_models.py failed — retry inside WebUI folder"
)
echo "[ok]  library · WebUI deps · download_models"

echo ""
echo "[6/6] Wire companion config.yaml…"
python3 configure_rvc.py --prefer-library --webui "$WEBUI" \
  || die "configure_rvc.py failed"

echo ""
echo "DONE (hard checks passed)."
echo "  WebUI: $WEBUI"
echo ""
echo "Next:"
echo "  python configure_rvc.py --check"
echo "  python open_recorder.py          # 10+ min YOUR voice → data/raw/"
echo "  python prepare.py --input data/raw --speaker demo"
echo "  python next_step.py"
echo ""
echo "Train:"
echo "  cd \"$WEBUI\""
echo "  python infer-web.py"
echo "  # open http://localhost:7865 → Train tab"
echo "  # fields: docs/TRAIN_WEBUI.md"
echo "  # copy assets/weights/*.pth + logs/*/*.index → models/rvc/"
echo "  # THEN regenerate YOUR clone (do not reuse old WAV):"
echo "  cd \"$ROOT\""
echo "  python infer.py --text-file scripts/clone_prove.txt --out output/clone_prove.wav"
echo "  python play_clone.py --wav output/clone_prove.wav"
echo ""
echo "Docs: BEGINNER.md · docs/TRAIN_WEBUI.md · docs/TROUBLESHOOT.md"
