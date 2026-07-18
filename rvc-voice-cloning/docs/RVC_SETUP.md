# Build & configure Retrieval-based Voice Conversion (required)

You must build and configure **RVC** yourself. This companion folder only
orchestrates record → prepare → infer → play. Training + conversion run in RVC.

## Upstream

- Library / API: https://github.com/RVC-Project/Retrieval-based-Voice-Conversion
- WebUI (train + infer — recommended): https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI

## One-shot setup

From `rvc-voice-cloning/`:

```bash
# 1) Clone + install RVC library and WebUI (next to this folder by default)
bash setup_rvc.sh

# 2) Wire paths into config.yaml
python configure_rvc.py --webui ../Retrieval-based-Voice-Conversion-WebUI

# 3) Verify
python configure_rvc.py --check
```

## What setup_rvc.sh does

1. `git clone` [Retrieval-based-Voice-Conversion](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion)
2. `pip install -e` that library (or git+ URL)
3. `git clone` [Retrieval-based-Voice-Conversion-WebUI](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI)
4. `pip install -r` WebUI requirements (install PyTorch for your GPU/CPU if needed)

## What configure_rvc.py writes

In `config.yaml`:

| Key | Meaning |
|-----|---------|
| `rvc_webui_root` | Absolute path to WebUI clone |
| `rvc_convert_command` | Calls `rvc_infer_bridge.py {base_wav} {out_wav} {model_dir}` |
| `rvc_model_dir` | `models/rvc` — put your `*.pth` (+ `*.index`) here |
| `rvc_f0method` | `rmvpe` (recommended) |
| `rvc_device` | `cpu` or `cuda` |

## Train in WebUI (after configure)

1. Launch WebUI (`python infer-web.py` inside the WebUI folder — see its README)
2. Train on clips from `data/segments/<speaker>/`
3. Export / copy best `G_*.pth` → `models/rvc/speaker.pth`
4. Copy FAISS `.index` next to it
5. `python configure_rvc.py --check` → should say READY
6. `python infer.py --text-file scripts/sample_line.txt`
7. `python play_clone.py`

## Manual configure (if paths differ)

```bash
python configure_rvc.py \
  --webui /absolute/path/to/Retrieval-based-Voice-Conversion-WebUI \
  --device cuda \
  --f0method rmvpe
```

Or edit `config.yaml` by hand, then `--check`.

## Dry-run without RVC

Leave `rvc_convert_command: ""` to run Edge TTS baseline only (not your clone).
That is useful to test the companion before RVC install finishes.
