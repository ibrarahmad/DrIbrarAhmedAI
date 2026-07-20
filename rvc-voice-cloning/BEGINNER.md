# Beginner path — clone YOUR voice (macOS + Windows)

Anyone who watches the full video can finish this. Free local open RVC.
Follow **one step at a time**. After every step run:

```bash
python next_step.py
```

**Windows:** use PowerShell and `.\setup_rvc.ps1` (see Step 0 / Step 1 Windows blocks). Do **not** run `bash setup_rvc.sh` on Windows — that script requires Homebrew.

It tells you the **next** command only.

---

## Goal

1. Record **your** voice (10+ minutes clean speech)
2. Train a local RVC model in WebUI
3. Generate new text in **your** voice
4. Play it

---

## Step 0 — one-time tools

**macOS**

```bash
# Homebrew required on a clean Mac: https://brew.sh
brew install ffmpeg git python@3.11
python3.11 --version
git --version
ffmpeg -version
```

**Windows (PowerShell)**

```powershell
winget install Gyan.FFmpeg
winget install Git.Git
python --version    # need 3.10 or 3.11 (not 3.9, not 3.12+)
# If needed: install Python 3.11 from python.org (Add to PATH)
```

---

## Step 1 — companion + official RVC

**macOS**

```bash
git clone https://github.com/ibrarahmad/DrIbrarAhmedAI.git
cd DrIbrarAhmedAI/rvc-voice-cloning
python3.11 -m venv .venv
source .venv/bin/activate
python --version
bash setup_rvc.sh
python configure_rvc.py --prefer-library
python next_step.py
```

**Windows (PowerShell)**

```powershell
git clone https://github.com/ibrarahmad/DrIbrarAhmedAI
cd DrIbrarAhmedAI\rvc-voice-cloning
python -m venv .venv
.\.venv\Scripts\Activate.ps1
Set-ExecutionPolicy -Scope Process Bypass
.\setup_rvc.ps1
python configure_rvc.py --prefer-library
python next_step.py
```

---

## Step 2 — record

Need **10+ minutes** total. Quiet room. Same mic.
One 20-second take is not enough.

**Primary (recommended):** repository recorder. The browser Save WAV goes to `~/Downloads/` — then move it into the repo.

```bash
python open_recorder.py
# Record → Stop → click Save WAV
mkdir -p data/raw
mv ~/Downloads/my_voice_*.wav data/raw/
ls -lh data/raw/*.wav
python verify_recordings.py --input data/raw --min-minutes 10
python next_step.py
```

Recorder output is mono WAV (device sample rate). `prepare.py` resamples to 40 kHz.

**Optional:** QuickTime Player often saves `.m4a`. Convert before prepare:

```bash
ffmpeg -i recording.m4a -ac 1 -ar 40000 data/raw/my_voice_01.wav
```

The pipeline expects WAV. Do not leave files as m4a.

---

## Step 3 — prepare

```bash
python prepare.py --input data/raw --speaker myvoice
python analyze.py
python next_step.py
```

`prepare.py` converts each raw take to mono 40 kHz, splits long recordings into training segments, measures duration/loudness/clipping, and writes `data/segments/myvoice/metadata.csv`. Use the same name (`myvoice`) as the WebUI experiment.

---

## Step 4 — train (WebUI) — do not skip

```bash
python train_prep.py
# Follow every field in docs/TRAIN_WEBUI.md
# Launch (macOS):
#   cd ~/DrIbrarAhmedAI/Retrieval-based-Voice-Conversion-WebUI
#   python infer-web.py
# Launch (Windows PowerShell):
#   cd "$HOME\DrIbrarAhmedAI\Retrieval-based-Voice-Conversion-WebUI"
#   python infer-web.py
# Browser: http://localhost:7865
# Copy .pth + .index → models/rvc/  (Windows: Copy-Item — see train_prep.py)
python configure_rvc.py --check
# Regenerate with YOUR weights (required):
python infer.py --text-file scripts/clone_prove.txt --out output/clone_prove.wav
python next_step.py
```

When check says **weights ready**, and infer wrote a **new** `output/clone_prove.wav`, continue.

---

## Step 5 — hear your clone

```bash
python play_clone.py --wav output/clone_prove.wav --label "PLAY CLONE"
# Optional visual proof (3–5s) — not a replacement for the scripted path:
# open -a "QuickTime Player" output/clone_prove.wav
```

Comment **FREECLONE** on the video when you hear yourself.

---

## If something breaks

Open `docs/TROUBLESHOOT.md` or run `python next_step.py` again.
