# Troubleshoot (macOS + Windows companion)

**WebUI path (always):**

```bash
# macOS / bash
cd ~/DrIbrarAhmedAI/Retrieval-based-Voice-Conversion-WebUI
```

```powershell
# Windows PowerShell
cd "$HOME\DrIbrarAhmedAI\Retrieval-based-Voice-Conversion-WebUI"
```

`setup_rvc.sh` / `setup_rvc.ps1` pin WebUI to `c1e005f0e226…` and **fail hard** if clone / pip / `download_models` break.

## Clean Mac first-boot fails

| Symptom | Fix |
|--------|-----|
| `FAIL: Activate the companion venv` | `python3 -m venv .venv && source .venv/bin/activate` |
| `FAIL: Homebrew is required` | Install https://brew.sh then `brew install ffmpeg git` |
| `FAIL: Need Python 3.10–3.11` | `brew install python@3.11` → new venv with `python3.11` |
| Apple Silicon torch / Gradio errors | Stay on **cpu** in Train tab; batch size `2` |
| WebUI pin checkout failed | Re-run `bash setup_rvc.sh` with network; see `docs/RVC_SETUP.md` |

## Clean Windows first-boot fails

| Symptom | Fix |
|--------|-----|
| `FAIL: Activate the companion venv` | `python -m venv .venv` then `.\.venv\Scripts\Activate.ps1` |
| Scripts disabled | `Set-ExecutionPolicy -Scope Process Bypass` then `.\setup_rvc.ps1` |
| `ffmpeg` / `git` missing | `winget install Gyan.FFmpeg` / `winget install Git.Git` (or re-run `.\setup_rvc.ps1`) |
| `FAIL: Need Python 3.10–3.11` | Install Python 3.11 from python.org (Add to PATH) → new venv |
| WebUI pin checkout failed | Re-run `.\setup_rvc.ps1` with network; see `docs/RVC_SETUP.md` |

## `rvc: command not found`

```bash
# macOS
cd ~/DrIbrarAhmedAI/rvc-voice-cloning
source .venv/bin/activate
python -m rvc.wrapper.cli.cli --help
```

```powershell
# Windows
cd $HOME\DrIbrarAhmedAI\rvc-voice-cloning
.\.venv\Scripts\Activate.ps1
python -m rvc.wrapper.cli.cli --help
```

If that fails, re-run `bash setup_rvc.sh` or `.\setup_rvc.ps1` with the venv active.

## Missing `.pth` / convert still fails

Train in WebUI, then copy:

- `assets/weights/myvoice.pth` → `models/rvc/speaker.pth`
- matching `.index` → `models/rvc/`

Then regenerate (do not reuse an old demo WAV):

```bash
python configure_rvc.py --check
python infer.py --text-file scripts/clone_prove.txt --out output/clone_prove.wav
# infer FAILS closed without *.pth (no fake clone)
python next_step.py   # must say: fresh + RVC
python play_clone.py --wav output/clone_prove.wav
```

If `next_step.py` says the prove WAV is older than `.pth`, re-run infer.

## Missing FFmpeg

```bash
# macOS
brew install ffmpeg
ffmpeg -version
```

```powershell
# Windows
winget install Gyan.FFmpeg
ffmpeg -version
```

## WebUI will not start / import errors

```bash
cd ~/DrIbrarAhmedAI/Retrieval-based-Voice-Conversion-WebUI
python3 -m pip install -r requirements.txt
python3 tools/download_models.py
python infer-web.py
```

If still broken and `run.sh` exists:

```bash
sh ./run.sh
```

Open [http://localhost:7865](http://localhost:7865).  
If the page is blank, wait for first-run downloads, then refresh.

## Unsupported / slow device / OOM

- **macOS (Apple Silicon):** Device = `cpu`. Lower batch size to `2` if RAM dies.
- **Windows + NVIDIA:** Device = CUDA / auto-detect. If **CUDA out of memory**, reduce batch size to `2`.
- **Windows + AMD / Intel:** Device = DirectML (when offered by the WebUI / torch-directml build).
- **No compatible GPU:** CPU fallback only — expect much slower training. CPU is not a “make Windows faster” switch.

## Empty or clipped / too-hot dataset

- Need **10+ minutes** clean speech total.
- Drop clipped / too-hot / silent clips after `python analyze.py`.
- Re-run `python prepare.py --input data/raw --speaker myvoice`.
- WebUI folder must stay WAV-only: `data/segments/myvoice/` (rejects live in `data/rejected/myvoice/`).


## `Failed building wheel for av` (FFmpeg 8)

Homebrew FFmpeg 8 breaks old `av==11` source builds. `setup_rvc.sh` prefetches `av==18.0.0` (binary wheel) and installs the pinned RVC package with `--no-deps`. Re-run:

```bash
source .venv/bin/activate
bash setup_rvc.sh
```
