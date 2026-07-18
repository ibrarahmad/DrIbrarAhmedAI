# Build & configure Retrieval-based Voice Conversion (required)

You must build and configure **RVC** yourself. This companion folder
orchestrates record → prepare → infer → play. Training usually runs in WebUI;
conversion uses the **official library**.

## Upstream

- Library / API / CLI (required): https://github.com/RVC-Project/Retrieval-based-Voice-Conversion
- WebUI (train - recommended): https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI

## Official library (complete convert path)

```bash
pip install git+https://github.com/RVC-Project/Retrieval-based-Voice-Conversion.git@develop

# Working directory = rvc-voice-cloning/
rvc init          # creates assets/ + .env
rvc dlmodel       # download hubert / rmvpe / pretrained assets
# or: cp .env.example .env  and fix paths after dlmodel

# Convert (after you have models/rvc/speaker.pth):
rvc infer -m models/rvc/speaker.pth -i base.wav -o out.wav -fm rmvpe
```

Python API (same library):

```python
from pathlib import Path
from dotenv import load_dotenv
from scipy.io import wavfile
from rvc.modules.vc.modules import VC

load_dotenv(".env")
vc = VC()
vc.get_vc("models/rvc/speaker.pth")
tgt_sr, audio_opt, times, _ = vc.vc_inference(1, Path("base.wav"))
wavfile.write("out.wav", tgt_sr, audio_opt)
```

## One-shot setup (companion)

From `rvc-voice-cloning/`:

```bash
bash setup_rvc.sh
python configure_rvc.py --prefer-library
python configure_rvc.py --check
python demo_complete.py   # full educational demo
```

## What setup_rvc.sh does

1. `pip install` companion requirements
2. `pip install` official RVC library from GitHub `develop`
3. `rvc init` / `rvc dlmodel` (assets + `.env`)
4. Optional clone of WebUI next to this folder (training UI)
5. `configure_rvc.py --prefer-library` → wires `rvc_infer_bridge.py`

## What configure_rvc.py writes

| Key | Meaning |
|-----|---------|
| `rvc_backend` | `library` (default) or `webui` |
| `rvc_webui_root` | Absolute path to WebUI clone (train + fallback) |
| `rvc_convert_command` | Calls `rvc_infer_bridge.py {base_wav} {out_wav} {model_dir}` |
| `rvc_model_dir` | `models/rvc` - put your `*.pth` (+ `*.index`) here |
| `rvc_f0method` | `rmvpe` (recommended) |
| `rvc_device` | `cpu` or `cuda` |

`rvc_infer_bridge.py` order when `rvc_backend=library`:

1. Python API (`rvc.modules.vc.modules.VC`)
2. CLI (`rvc infer …`)
3. WebUI `tools/infer_cli.py` (if `rvc_webui_root` set)

## Train (WebUI still recommended)

Library `rvc train` is still a stub upstream. Use WebUI:

1. Launch WebUI (`python infer-web.py` inside the WebUI folder)
2. Train on clips from `data/segments/<speaker>/`
3. Copy best `G_*.pth` → `models/rvc/speaker.pth`
4. Copy FAISS `.index` next to it
5. `python configure_rvc.py --check` → READY
6. `python demo_complete.py` or `python infer.py` + `python play_clone.py`

## Complete demo

```bash
python demo_complete.py
# stages: library → configure → record check → prepare/train → infer → play
```

Dry-run without weights:

```bash
python demo_complete.py --baseline-only --skip-record-check --no-play
```

## Dry-run without RVC

Leave `rvc_convert_command: ""` to run Edge TTS baseline only (not your clone).
That is useful to test the companion before RVC install finishes.
