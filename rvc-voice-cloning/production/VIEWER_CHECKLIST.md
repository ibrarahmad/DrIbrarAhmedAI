# Viewer checklist — finish the clone (macOS)

Follow the video. After every beat run:

```bash
python next_step.py
```

[ ] 1. `brew install ffmpeg`
[ ] 2. Clone repo · `python3 -m venv .venv` · `source .venv/bin/activate`
[ ] 3. `bash setup_rvc.sh` · `python configure_rvc.py --prefer-library`
[ ] 4. Record **10+ minutes** clean speech → `data/raw/` (`python open_recorder.py`)
[ ] 5. `python prepare.py --input data/raw --speaker myvoice` · `python analyze.py`
[ ] 6. `python train_prep.py` · open `docs/TRAIN_WEBUI.md`
[ ] 7. `cd ~/DrIbrarAhmedAI/Retrieval-based-Voice-Conversion-WebUI` · `python infer-web.py`
[ ] 8. Browser `http://localhost:7865` · Train tab · exact fields in TRAIN_WEBUI.md
[ ] 9. Preprocess → extract → train → build index
[ ] 10. Copy `myvoice.pth` + `.index` → `models/rvc/`
[ ] 11. `python configure_rvc.py --check` → **weights ready**
[ ] 12. `python infer.py --text-file scripts/clone_prove.txt --out output/clone_prove.wav`  # YOUR weights
[ ] 13. `python play_clone.py --wav output/clone_prove.wav`
[ ] 14. Comment **FREECLONE** on the video

Start file: `BEGINNER.md`  
Fixes: `docs/TROUBLESHOOT.md`

github.com/ibrarahmad/DrIbrarAhmedAI/rvc-voice-cloning
