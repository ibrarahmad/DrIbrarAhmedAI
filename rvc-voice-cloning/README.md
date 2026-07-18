<div align="center">

# 🎙️ RVC Voice Cloning

### Train your voice once — Edge TTS → Retrieval-based Voice Conversion → YouTube narration

Companion code for **[@DrIbrarAhmedAI](https://www.youtube.com/@DrIbrarAhmedAI)**.

<br/>

[![Clone repo](https://img.shields.io/badge/Repo-ibrarahmad%2FDrIbrarAhmedAI-181717?style=for-the-badge&logo=github)](https://github.com/ibrarahmad/DrIbrarAhmedAI/tree/main/rvc-voice-cloning)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![RVC](https://img.shields.io/badge/RVC-Retrieval--based-22D3EE?style=flat-square)](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion)

`prepare` → `train (external RVC)` → `infer` → `export`

</div>

---

> **Purpose:** You do **not** need ElevenLabs or a paid voice API. Watch the full video, follow each numbered step, record your own voice, train once locally, and play your clone — free and simple.

---

## 📑 Contents

- [What you get](#-what-you-get)
- [Quick start](#-quick-start)
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
| `record_voice.py` | How to capture YOUR voice into `data/raw/` |
| `open_recorder.py` / `recorder.html` | Browser mic recorder → Save WAV |
| `play_clone.py` | Play the generated clone WAV |
| `pipeline.py` | One-command demo loop |
| `prepare.py` | Raw recordings → clean mono → `metadata.csv` |
| `analyze.py` | Clean vs noisy/reverb report |
| `train_prep.py` | Manifest + printed RVC train steps |
| `infer.py` | Edge TTS → optional RVC convert |
| `rvc_core.py` | Retrieval knobs + convert helper |
| `export.py` | Loudnorm WAV + MP3 |
| `quality_gate.py` | Consent + dataset gate |
| `compare.py` | Baseline FAIL vs RVC PASS report |
| `batch_produce.py` | Batch scripts → drop short clips |
| `golden_replay.py` | Golden replay test suite |
| `tools_overview.py` | Three allowed tools facade |
| `schemas/output_contract.json` | Output file contract |
| `production/CHECKLIST.md` | Ship checklist |
| `consent.yaml` | Own-voice-only boundary |
| `config.yaml` | Presets: natural / clear / broadcast |

This folder **orchestrates**. Full RVC training runs in [RVC](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion) / [WebUI](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI). Place `*.pth` (+ `*.index`) under `models/rvc/`.

---

## ⚡ Quick start

```bash
git clone https://github.com/ibrarahmad/DrIbrarAhmedAI
cd DrIbrarAhmedAI/rvc-voice-cloning

python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 1) Attest own-voice policy after you confirm recordings are yours
#    edit consent.yaml → attested: true

# 2) Dry-run the full loop (Edge TTS baseline until you wire RVC)
python pipeline.py --text-file scripts/sample_line.txt --skip-gate --baseline-only

# 3) After training, put speaker.pth + speaker.index in models/rvc/
#    set rvc_convert_command in config.yaml, then:
python pipeline.py --text-file scripts/sample_line.txt
```

Requires **ffmpeg** on `PATH` (`brew install ffmpeg`).

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
output/narration.wav → loudnorm export
```

---

## 🧭 Pipeline step by step

```bash
python prepare.py --input data/raw --speaker demo
python analyze.py
python train_prep.py          # prints external RVC steps; writes models/training_manifest.json
# … train in RVC/WebUI, copy weights to models/rvc/ …
python infer.py --text-file scripts/sample_line.txt --out output/narration.wav
python export.py --in-wav output/narration.wav --out-dir output --basename narration
python compare.py             # baseline FAIL vs RVC PASS when wired
python quality_gate.py        # consent + dataset checks
python batch_produce.py --skip-gate
python golden_replay.py --suite anomaly_v1
```

---

## 🎛 Config knobs

Presets in `config.yaml`:

| Preset | index_rate | protect | Use |
|--------|------------|---------|-----|
| natural | 0.75 | 0.45 | softer identity |
| clear | 0.80 | 0.40 | default narration |
| broadcast | 0.85 | 0.33 | stronger target timbre |

Also: `f0method=rmvpe`, `edge_tts_voice`, `rvc_convert_command` with `{base_wav}` `{out_wav}` `{model_dir}`.

---

## ✅ Production checklist

```
[ ] consent.yaml attested: true (own recordings only)
[ ] ≥ ~10 min clean speech; drop noisy/reverb rows
[ ] speaker.pth + .index in models/rvc/
[ ] rvc_convert_command wired to your RVC install
[ ] ffmpeg on PATH; loudnorm export before upload
[ ] backup weights; never commit .pth to public forks with others' voices
[ ] README: educational · own-voice-only · no impersonation
```

---

## 🛡 Ethics

Train and convert **only voices you own** or have written consent for. Do not use this to impersonate people. Deepfake misuse is on you — the gate exists to make consent a first-class engineering check.

---

## 🔗 Upstream

- Library: https://github.com/RVC-Project/Retrieval-based-Voice-Conversion
- WebUI: https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI
- Models: https://huggingface.co/lj1995/VoiceConversionWebUI

---

**▶ [youtube.com/@DrIbrarAhmedAI](https://www.youtube.com/@DrIbrarAhmedAI)** · Clone this folder and follow the video beat by beat.
