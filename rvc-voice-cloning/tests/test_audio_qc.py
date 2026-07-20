#!/usr/bin/env python3
"""Unit tests for audio_qc + prepare segmentation (stdlib only)."""
from __future__ import annotations

import math
import struct
import sys
import tempfile
import unittest
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from audio_qc import (  # noqa: E402
    clip_ratio,
    label_metrics,
    measure_wav,
    rms_dbfs,
    split_on_silence,
    write_wav,
)
from prepare import prepare  # noqa: E402


def _tone(sr: int, sec: float, freq: float = 220.0, amp: float = 0.25) -> bytes:
    n = int(sr * sec)
    return b"".join(
        struct.pack("<h", int(amp * 32767 * math.sin(2 * math.pi * freq * i / sr)))
        for i in range(n)
    )


def _silence(sr: int, sec: float) -> bytes:
    return b"\x00\x00" * int(sr * sec)


class AudioQcTests(unittest.TestCase):
    def test_rms_and_label_clean(self) -> None:
        pcm = _tone(16000, 1.0, amp=0.2)
        rms = rms_dbfs(pcm)
        self.assertLess(rms, -6.0)
        self.assertEqual(label_metrics(rms, clip_ratio(pcm)), "clean")

    def test_label_silent(self) -> None:
        pcm = _silence(16000, 1.0)
        self.assertEqual(label_metrics(rms_dbfs(pcm), 0.0), "silent")

    def test_label_clipped(self) -> None:
        pcm = _tone(16000, 0.5, amp=1.0)
        self.assertEqual(label_metrics(rms_dbfs(pcm), clip_ratio(pcm)), "clipped")

    def test_split_long_take(self) -> None:
        sr = 16000
        pcm = (
            _tone(sr, 8)
            + _silence(sr, 1)
            + _tone(sr, 8, freq=330)
            + _silence(sr, 1)
            + _tone(sr, 7, freq=180)
        )
        clips = split_on_silence(pcm, sr, min_clip_sec=2.0, max_clip_sec=12.0)
        self.assertGreaterEqual(len(clips), 2)
        self.assertLessEqual(len(clips), 5)
        for clip in clips:
            dur = len(clip) / 2 / sr
            self.assertGreater(dur, 1.0)
            self.assertLessEqual(dur, 13.0)

    def test_prepare_writes_only_clean_to_train_folder(self) -> None:
        sr = 16000
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # Minimal config.yaml
            (root / "config.yaml").write_text(
                "sample_rate: 16000\n"
                "speaker_name: myvoice\n"
                "min_clip_length_sec: 2.0\n"
                "max_clip_length_sec: 12.0\n"
                "min_dataset_minutes: 10.0\n",
                encoding="utf-8",
            )
            raw = root / "data" / "raw"
            raw.mkdir(parents=True)
            pcm = (
                _tone(sr, 8)
                + _silence(sr, 1)
                + _tone(sr, 8, freq=330)
                + _silence(sr, 1)
                + _tone(sr, 7, freq=180)
            )
            write_wav(raw / "long.wav", pcm, sr)

            # Point prepare at temp root by monkeypatching load path via --root API
            meta = prepare(root, raw, "myvoice")
            self.assertTrue(meta.is_file())
            self.assertEqual(meta, root / "data" / "reports" / "myvoice.csv")
            seg = root / "data" / "segments" / "myvoice"
            keeps = list(seg.glob("seg_*.wav"))
            self.assertGreaterEqual(len(keeps), 2)
            # WebUI folder: WAV only — no metadata.csv, no rejected/
            self.assertFalse((seg / "metadata.csv").is_file())
            self.assertFalse((seg / "rejected").is_dir())
            self.assertEqual(list(seg.glob("drop_*.wav")), [])
            self.assertTrue((root / "data" / "rejected" / "myvoice").is_dir())
            for wav in keeps:
                m = measure_wav(wav)
                self.assertEqual(m["label"], "clean")
                self.assertNotAlmostEqual(float(m["duration_sec"]), 4.0, places=1)


if __name__ == "__main__":
    unittest.main()
