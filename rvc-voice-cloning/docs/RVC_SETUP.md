# Build & configure Retrieval-based Voice Conversion (required)

You must build and configure **RVC** yourself. This companion folder
orchestrates record → prepare → infer → play. Training usually runs in WebUI;
conversion uses the **official library**.

## Upstream

- Library / API / CLI (required): https://github.com/RVC-Project/Retrieval-based-Voice-Conversion
- WebUI (train - recommended): https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI

## Official library (complete convert path)

```bash
# Pin a tested commit (develop moves). Tested 2026-07-19 · macOS · Python 3.10–3.11 · FFmpeg 8.x
pip install git+https://github.com/RVC-Project/Retrieval-based-Voice-Conversion.git@7b284a634667c34103eaaeed972b48ccdb4b893e
```

WebUI (train UI) is a **different repo**. `setup_rvc.sh` pins it to:

```text
c1e005f0e226a3c2a10adfc8a9be03a6944506d0
```

Do not float on WebUI `HEAD`. Prefer `bash setup_rvc.sh` (venv required; hard-fails on clone/pip/models).

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

## What setup_rvc.sh does (hard-fail — matches video Slide 4)

1. Require active `.venv` + Homebrew + FFmpeg + Python **3.10–3.11**
2. `pip install` companion `requirements.txt`
3. Prefetch `av==18` binary wheel (FFmpeg 8 Macs), then install **pinned** RVC `@7b284a634667…` with `--no-deps` + runtime deps (never `develop` / HEAD)
4. `rvc init` / `rvc dlmodel` for companion convert assets
5. Clone WebUI next to this folder and **detach to** `c1e005f0e226…`
6. `pip install -r` WebUI `requirements.txt` + `python tools/download_models.py`
7. `configure_rvc.py --prefer-library` → wires `rvc_infer_bridge.py`

Success lines you should see:

```text
[pin] library @7b284a634667
[pin] WebUI @c1e005f0e226 (hard fail if clone/pip/models fail)
[ok]  library · WebUI deps · download_models
```

If any of those fail, the script exits non-zero. There is no `|| true` on pin/clone/pip/models.

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

## Train (WebUI — required for beginners)

Full field-by-field guide: **[docs/TRAIN_WEBUI.md](TRAIN_WEBUI.md)**  
Fixes: **[docs/TROUBLESHOOT.md](TROUBLESHOOT.md)**

1. Record **10+ minutes** clean speech → `prepare.py`
2. `cd ~/DrIbrarAhmedAI/Retrieval-based-Voice-Conversion-WebUI && python infer-web.py`
3. Browser: http://localhost:7865 → **Train** tab
4. Use exact fields in TRAIN_WEBUI.md (`myvoice`, 40k, rmvpe, cpu, 200 epochs, …)
5. Preprocess → extract features → train → build index
6. Copy `assets/weights/myvoice.pth` + `.index` → companion `models/rvc/`
7. `python configure_rvc.py --check` → **STATUS: weights ready**
8. `python infer.py` + `python play_clone.py`

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
