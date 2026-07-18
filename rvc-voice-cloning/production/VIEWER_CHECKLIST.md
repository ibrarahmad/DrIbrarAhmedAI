# TONIGHT - official RVC library + your clone (no ElevenLabs)
[ ] 1. git clone https://github.com/ibrarahmad/DrIbrarAhmedAI
[ ] 2. cd rvc-voice-cloning && python3 -m venv .venv && pip install -r requirements.txt
[ ] 3. bash setup_rvc.sh
      → pip install git+https://github.com/RVC-Project/Retrieval-based-Voice-Conversion
      → rvc init && rvc dlmodel  (+ optional WebUI for train)
[ ] 4. python configure_rvc.py --prefer-library
[ ] 5. python configure_rvc.py --check
[ ] 6. python open_recorder.py  → Record → Save WAV → move into data/raw/
[ ] 7. python play_clone.py --wav data/raw/my_voice_01.wav   # hear your recording
[ ] 8. python record_voice.py --check
[ ] 9. python prepare.py --input data/raw && python analyze.py
[ ] 10. consent.yaml → attested: true  (own voice only)
[ ] 11. python train_prep.py
[ ] 12. Train in RVC WebUI → copy speaker.pth + .index → models/rvc/
[ ] 13. python infer.py --text-file scripts/clone_prove.txt --out output/clone_prove.wav
[ ] 14. python play_clone.py --wav output/clone_prove.wav   # clone says DIFFERENT text
[ ] 15. Hear your clone on new words. Comment FREECLONE on the video.

pip install official RVC → configure → record → train → demo_complete. Free. Local.
See docs/RVC_SETUP.md

github.com/ibrarahmad/DrIbrarAhmedAI/rvc-voice-cloning
