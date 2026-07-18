# TONIGHT — follow each step (no ElevenLabs)
[ ] 1. git clone https://github.com/ibrarahmad/DrIbrarAhmedAI
[ ] 2. cd rvc-voice-cloning && python3 -m venv .venv && pip install -r requirements.txt
[ ] 3. Record 10+ min of YOUR voice → data/raw/
      (easiest: python open_recorder.py → Save WAV → move into data/raw/)
[ ] 4. python record_voice.py --check
[ ] 5. python prepare.py --input data/raw
[ ] 6. python analyze.py   # DROP noisy/reverb
[ ] 7. consent.yaml → attested: true  (own voice only)
[ ] 8. python train_prep.py
[ ] 9. Train in RVC/WebUI → copy speaker.pth + .index → models/rvc/
[ ] 10. python infer.py --text-file scripts/sample_line.txt
[ ] 11. python play_clone.py --wav output/narration.wav
[ ] 12. Hear YOUR clone. Comment FREECLONE on the video.

No paid voice API. Free repo. Follow steps 1→12.

github.com/ibrarahmad/DrIbrarAhmedAI/rvc-voice-cloning
