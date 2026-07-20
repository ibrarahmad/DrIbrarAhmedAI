# Train your voice in RVC WebUI (macOS + Windows)

Library `rvc train` is still a stub upstream. Use the WebUI for training.

Upstream: https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI

**One WebUI path (use everywhere):**

```bash
# macOS / bash
cd ~/DrIbrarAhmedAI/Retrieval-based-Voice-Conversion-WebUI
```

```powershell
# Windows PowerShell
cd "$HOME\DrIbrarAhmedAI\Retrieval-based-Voice-Conversion-WebUI"
```

`setup_rvc.sh` (macOS) / `setup_rvc.ps1` (Windows) clones it next to the companion (`DrIbrarAhmedAI/rvc-voice-cloning` → sibling `Retrieval-based-Voice-Conversion-WebUI`) and installs WebUI `requirements.txt` plus `tools/download_models.py`.

## Before you train

1. Record **10+ minutes** of clean speech into `data/raw/` (same mic, quiet room).
2. Run:

```bash
python prepare.py --input data/raw --speaker myvoice
python analyze.py
```

3. Dataset folder for WebUI:

```text
~/DrIbrarAhmedAI/rvc-voice-cloning/data/segments/myvoice
```

## 1) Training setup — launch WebUI

```bash
cd ~/DrIbrarAhmedAI/Retrieval-based-Voice-Conversion-WebUI
python infer-web.py
```

If imports fail after a fresh clone, retry deps:

```bash
cd ~/DrIbrarAhmedAI/Retrieval-based-Voice-Conversion-WebUI
python3 -m pip install -r requirements.txt
python3 tools/download_models.py
# official macOS helper (when present):
sh ./run.sh
```

Open the browser:

```text
http://localhost:7865
```

Keep that terminal open. Open the **Train** tab.

## 2) Training configuration — exact values used in the video

| Field | Value |
|-------|--------|
| Experiment name | `myvoice` |
| Dataset folder | `~/DrIbrarAhmedAI/rvc-voice-cloning/data/segments/myvoice` |
| Sample rate | `40k` |
| F0 method | `rmvpe` |
| Device | **macOS:** `cpu` (Apple Silicon) · **Windows:** NVIDIA → CUDA / auto-detect · AMD/Intel → DirectML · none → CPU fallback (slower) |
| Epochs | `200` |
| Save every epoch | `25` |
| Batch size | `4` (use `2` if CUDA OOM / RAM is low) |
| Version | `v2` |
| Pretrained G | `assets/pretrained_v2/f0G40k.pth` |
| Pretrained D | `assets/pretrained_v2/f0D40k.pth` |

## 3) Train and export — click in this order

1. **Preprocess / process dataset**
2. **Extract pitch and features** (rmvpe)
3. **Train model**
4. **Train / build feature index**

### Where files land

| File | Typical path |
|------|----------------|
| Model `.pth` | `~/DrIbrarAhmedAI/Retrieval-based-Voice-Conversion-WebUI/assets/weights/myvoice.pth` |
| Index `.index` | Prefer `logs/myvoice/added_*.index` (also creates `trained_*.index`) |

### Copy into the companion

```bash
cd ~/DrIbrarAhmedAI/Retrieval-based-Voice-Conversion-WebUI

cp assets/weights/myvoice.pth \
  ../rvc-voice-cloning/models/rvc/speaker.pth

# RVC writes trained_*.index and added_*.index — copy the latest added_ index only
latest_index=$(ls -t logs/myvoice/added_*.index | head -1)
cp "$latest_index" \
  ../rvc-voice-cloning/models/rvc/myvoice.index

cd ../rvc-voice-cloning
python configure_rvc.py --check
```

You want:

```text
STATUS: weights ready
```

### Regenerate YOUR clone (required before A/B/C)

Do **not** reuse an old `output/clone_prove.wav` from the demo. Create a fresh file with **your** weights:

```bash
python infer.py --text-file scripts/clone_prove.txt --out output/clone_prove.wav
python play_clone.py --wav output/clone_prove.wav
```

## Notes

- One 20-second take is not enough. Aim for 10+ minutes total.
- Apple Silicon Macs typically train on **CPU** (slower, works).
- Anytime: `python next_step.py`
