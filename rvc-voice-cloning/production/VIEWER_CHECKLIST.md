# TONIGHT — follow each step (no ElevenLabs · build RVC yourself)
[ ] 1. git clone https://github.com/ibrarahmad/DrIbrarAhmedAI
[ ] 2. cd rvc-voice-cloning && python3 -m venv .venv && pip install -r requirements.txt
[ ] 3. bash setup_rvc.sh
      (clones https://github.com/RVC-Project/Retrieval-based-Voice-Conversion + WebUI)
[ ] 4. python configure_rvc.py --webui ../Retrieval-based-Voice-Conversion-WebUI
[ ] 5. python configure_rvc.py --check
[ ] 6. python open_recorder.py  → Record → Save WAV → move into data/raw/
[ ] 7. python record_voice.py --check
[ ] 8. python prepare.py --input data/raw && python analyze.py
[ ] 9. consent.yaml → attested: true  (own voice only)
[ ] 10. python train_prep.py
[ ] 11. Train in RVC WebUI → copy speaker.pth + .index → models/rvc/
[ ] 12. python infer.py --text-file scripts/sample_line.txt
[ ] 13. python play_clone.py --wav output/narration.wav
[ ] 14. Hear YOUR clone. Comment FREECLONE on the video.

Build RVC → configure → record → train → play. Free. Local. Step by step.
See docs/RVC_SETUP.md

github.com/ibrarahmad/DrIbrarAhmedAI/rvc-voice-cloning
