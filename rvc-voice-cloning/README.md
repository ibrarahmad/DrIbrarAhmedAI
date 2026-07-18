<div align="center">

# 🎙️ RVC Voice Cloning

### Train your voice once - Edge TTS → official RVC library → YouTube narration

Companion code for **[@DrIbrarAhmedAI](https://www.youtube.com/@DrIbrarAhmedAI)**.

<br/>

[![Clone repo](https://img.shields.io/badge/Repo-ibrarahmad%2FDrIbrarAhmedAI-181717?style=for-the-badge&logo=github)](https://github.com/ibrarahmad/DrIbrarAhmedAI/tree/main/rvc-voice-cloning)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![RVC](https://img.shields.io/badge/RVC-Retrieval--based-22D3EE?style=flat-square)](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion)

`setup_rvc` → `configure` → `record` → `train` → `demo_complete` / `infer` → `play`

</div>

---

> **Purpose:** You do **not** need ElevenLabs. You **do** need to build and configure open-source [Retrieval-based-Voice-Conversion](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion). Watch the full video, follow each step, record your voice, train locally, play your clone.

---

## 📑 Contents

- [What you get](#-what-you-get)
- [Quick start](#-quick-start)
- [Complete demo](#-complete-demo)
- [Architecture](#-architecture)
- [Pipeline step by step](#-pipeline-step-by-step)
- [Config knobs](#-config-knobs)
- [Production checklist](#-production-checklist)
- [Ethics](#-ethics)
- [Upstream](#-upstream)

---

## 🎯 What you get

| File | Purpose |
|------|---------|
| `setup_rvc.sh` | `pip install` official RVC library + optional WebUI |
| `configure_rvc.py` | Wire `config.yaml` (`--prefer-library`) |
| `rvc_infer_bridge.py` | Convert via library API → `rvc infer` → WebUI |
| `demo_complete.py` | Full educational demo (6 stages) |
| `smoke_test.py` | Prove prepare + play + infer + export work on this Mac |
| `docs/RVC_SETUP.md` | Full build + configure guide |
| `.env.example` | Template after `rvc init` / `rvc dlmodel` |
| `open_recorder.py` / `recorder.html` | Browser mic → Save WAV |
| `play_clone.py` | Play the generated clone WAV |
| `pipeline.py` | One-command orchestration loop |
| `prepare.py` | Raw recordings → clean mono → `metadata.csv` |
| `analyze.py` | Clean vs noisy/reverb report |
| `train_prep.py` | Manifest + printed RVC train steps |
| `infer.py` | Edge TTS → RVC convert |
| `rvc_core.py` | Retrieval knobs + convert helper |
| `export.py` | Loudnorm WAV + MP3 |
| `quality_gate.py` | Consent + dataset gate |
| `compare.py` | Baseline FAIL vs RVC PASS report |
| `batch_produce.py` | Batch scripts → drop short clips |
| `golden_replay.py` | Golden replay test suite |
| `consent.yaml` / `config.yaml` | Ethics + presets |

Convert uses the **official library**:
`pip install git+https://github.com/RVC-Project/Retrieval-based-Voice-Conversion`

Training still uses [WebUI](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI) (library `rvc train` is a stub upstream). Put `*.pth` (+ `*.index`) under `models/rvc/`.

---

## ⚡ Quick start

```bash
git clone https://github.com/ibrarahmad/DrIbrarAhmedAI
cd DrIbrarAhmedAI/rvc-voice-cloning

python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# REQUIRED for YOUR trained clone: official RVC library (not ElevenLabs)
# First prove the local path works:
python smoke_test.py

bash setup_rvc.sh
python configure_rvc.py --prefer-library
python configure_rvc.py --check

# Record → prepare → train in WebUI → copy .pth → complete demo
python open_recorder.py
python prepare.py --input data/raw
python train_prep.py
# … train in WebUI, copy speaker.pth + .index into models/rvc/ …
python demo_complete.py
```

Requires **ffmpeg** on `PATH` (`brew install ffmpeg`).
`python smoke_test.py` must print `SMOKE: PASS`.

---

## 🎬 Complete demo

```bash
python demo_complete.py
```

Stages:

1. Check official RVC library (`import rvc` / `rvc` CLI)
2. Configure companion (`rvc_infer_bridge`)
3. Record check (`data/raw/`)
4. Prepare + train reminder
5. Edge TTS → RVC convert (`rvc infer` / Python API)
6. Play clone

Without weights yet:

```bash
python demo_complete.py --baseline-only --skip-record-check --no-play
```

Official convert one-liner (after weights + `rvc init`):

```bash
rvc infer -m models/rvc/speaker.pth -i base.wav -o out.wav -fm rmvpe
```

---

## 🏗 Architecture

```
script text
    │
    ▼
Edge TTS ──────────────► base WAV (content + prosody)
    │
    ├─ HuBERT / ContentVec   content features
    ├─ F0 (rmvpe)            pitch
    ├─ FAISS index           retrieval blend (index_rate)
    └─ VITS synthesizer      your timbre
    │
    ▼
output/narration.wav → play_clone / loudnorm export
```

---

## 🧭 Pipeline step by step

```bash
python prepare.py --input data/raw --speaker demo
python analyze.py
python train_prep.py
# … train in WebUI, copy weights to models/rvc/ …
python infer.py --text-file scripts/sample_line.txt --out output/narration.wav
python play_clone.py
python export.py --in-wav output/narration.wav --out-dir output --basename narration
python compare.py
python quality_gate.py
```

---

## 🎛 Config knobs

Presets in `config.yaml`: natural / clear / broadcast (`index_rate`, `protect`).

Also: `rvc_backend=library`, `f0method=rmvpe`, `rvc_convert_command` → bridge.

---

## ✅ Production checklist

See `production/VIEWER_CHECKLIST.md` and `docs/RVC_SETUP.md`.

---

## 🛡 Ethics

Train and convert **only voices you own** or have written consent for. Do not impersonate people.

---

## 🔗 Upstream

- Library: https://github.com/RVC-Project/Retrieval-based-Voice-Conversion
- WebUI: https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI
- Models: https://huggingface.co/lj1995/VoiceConversionWebUI

---

**▶ [youtube.com/@DrIbrarAhmedAI](https://www.youtube.com/@DrIbrarAhmedAI)** · Clone this folder and follow the video beat by beat.
