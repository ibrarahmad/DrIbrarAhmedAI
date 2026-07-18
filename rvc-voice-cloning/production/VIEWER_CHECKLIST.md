# TONIGHT — official RVC library + YOUR clone (no ElevenLabs)
[ ] 1. git clone https://github.com/ibrarahmad/DrIbrarAhmedAI
[ ] 2. cd rvc-voice-cloning && python3 -m venv .venv && pip install -r requirements.txt
[ ] 3. bash setup_rvc.sh
      → pip install git+https://github.com/RVC-Project/Retrieval-based-Voice-Conversion
      → rvc init && rvc dlmodel  (+ optional WebUI for train)
[ ] 4. python configure_rvc.py --prefer-library
[ ] 5. python configure_rvc.py --check
[ ] 6. python open_recorder.py  → Record → Save WAV → move into data/raw/
[ ] 7. python record_voice.py --check
[ ] 8. python prepare.py --input data/raw && python analyze.py
[ ] 9. consent.yaml → attested: true  (own voice only)
[ ] 10. python train_prep.py
[ ] 11. Train in RVC WebUI → copy speaker.pth + .index → models/rvc/
[ ] 12. python demo_complete.py
        (or: rvc infer -m models/rvc/speaker.pth -i base.wav -o out.wav)
[ ] 13. python play_clone.py --wav output/narration.wav
[ ] 14. Hear YOUR clone. Comment FREECLONE on the video.

pip install official RVC → configure → record → train → demo_complete. Free. Local.
See docs/RVC_SETUP.md

github.com/ibrarahmad/DrIbrarAhmedAI/rvc-voice-cloning
