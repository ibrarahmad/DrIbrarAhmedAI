<div align="center">

# Clone Your Voice Free (macOS + Windows)

### Beginner path: record → train WebUI → hear YOUR clone · free local RVC

Companion for **[@DrIbrarAhmedAI](https://www.youtube.com/@DrIbrarAhmedAI)**.

<br/>

[![Beginner guide](https://img.shields.io/badge/Start-BEGINNER.md-22C55E?style=for-the-badge)](BEGINNER.md)
[![Repo](https://img.shields.io/badge/Repo-ibrarahmad%2FDrIbrarAhmedAI-181717?style=for-the-badge&logo=github)](https://github.com/ibrarahmad/DrIbrarAhmedAI/tree/main/rvc-voice-cloning)

**Purpose:** Anyone who watches the full video can finish.  
Run `python next_step.py` anytime — it tells you the next command only.

</div>

---

## Start here (beginners)

1. Open **[BEGINNER.md](BEGINNER.md)** and do one step at a time.
2. After each step:

```bash
python next_step.py
```

3. Train fields and click order: **[docs/TRAIN_WEBUI.md](docs/TRAIN_WEBUI.md)**  
4. If stuck: **[docs/TROUBLESHOOT.md](docs/TROUBLESHOOT.md)**

You need **10+ minutes** of clean speech of **your** voice. One short take is not enough.

---

## Quick install (macOS)

```bash
brew install ffmpeg

git clone https://github.com/ibrarahmad/DrIbrarAhmedAI
cd DrIbrarAhmedAI/rvc-voice-cloning
python3 -m venv .venv && source .venv/bin/activate
bash setup_rvc.sh
python configure_rvc.py --prefer-library
python next_step.py
```

Pinned RVC commit is inside `setup_rvc.sh` (do not float on `develop`).

---

## Quick install (Windows · PowerShell)

```powershell
winget install Gyan.FFmpeg

git clone https://github.com/ibrarahmad/DrIbrarAhmedAI
cd DrIbrarAhmedAI\rvc-voice-cloning
python -m venv .venv
.\.venv\Scripts\Activate.ps1
Set-ExecutionPolicy -Scope Process Bypass
.\setup_rvc.ps1
python configure_rvc.py --prefer-library
python next_step.py
```

Pinned RVC + WebUI commits are inside `setup_rvc.ps1` (same pins as macOS; hard-fail on clone/pip/models).

---

## What success looks like

```bash
python infer.py --text-file scripts/clone_prove.txt --out output/clone_prove.wav
python play_clone.py --wav output/clone_prove.wav
```

You hear **new words** in **your** voice. Comment **FREECLONE** on the video.

---

## Main files

| File | Purpose |
|------|---------|
| `BEGINNER.md` | Full beginner path |
| `next_step.py` | Tells you the one next command |
| `docs/TRAIN_WEBUI.md` | Launch WebUI + every train field + export |
| `docs/TROUBLESHOOT.md` | Common failures |
| `setup_rvc.sh` | macOS: install pinned official RVC + WebUI |
| `setup_rvc.ps1` | Windows: same pins via PowerShell + winget |
| `open_recorder.py` | Record → `data/raw/` |
| `prepare.py` / `analyze.py` | Clean dataset |
| `train_prep.py` | Prints exact WebUI steps |
| `infer.py` / `play_clone.py` | Generate + hear clone |
| `demo_complete.py` | Full demo after weights exist |

---

## Ethics

Train and convert **only voices you own**. No impersonation. Set `consent.yaml` `attested: true` only for your recordings.

---

## Upstream

- Library: https://github.com/RVC-Project/Retrieval-based-Voice-Conversion  
- WebUI: https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI  

**▶ [youtube.com/@DrIbrarAhmedAI](https://www.youtube.com/@DrIbrarAhmedAI)**
