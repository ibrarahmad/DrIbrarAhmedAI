#!/usr/bin/env python3
"""Prepare own-voice recordings: raw → mono 40 kHz → silence-split segments + metadata."""
from __future__ import annotations

import argparse
import audioop
import csv
import math
import shutil
import struct
import subprocess
import sys
import wave
from pathlib import Path

from _lib import ROOT, load_config, which


AUDIO_EXTS = {".wav", ".mp3", ".flac", ".m4a"}


def _load_mono_pcm16(path: Path, sample_rate: int, ffmpeg: str | None) -> tuple[bytes, int]:
    """Return (pcm16le mono bytes, sample_rate). Converts via ffmpeg when available."""
    if ffmpeg:
        cmd = [
            ffmpeg,
            "-y",
            "-i",
            str(path),
            "-ac",
            "1",
            "-ar",
            str(sample_rate),
            "-f",
            "s16le",
            "-acodec",
            "pcm_s16le",
            "pipe:1",
        ]
        proc = subprocess.run(cmd, check=True, capture_output=True)
        return proc.stdout, sample_rate

    with wave.open(str(path), "rb") as wf:
        nch = wf.getnchannels()
        sw = wf.getsampwidth()
        sr = wf.getframerate()
        raw = wf.readframes(wf.getnframes())
    if sw != 2:
        raw = audioop.lin2lin(raw, sw, 2)
    if nch > 1:
        raw = audioop.tomono(raw, 2, 0.5, 0.5)
    if sr != sample_rate:
        raw, _ = audioop.ratecv(raw, 2, 1, sr, sample_rate, None)
    return raw, sample_rate


def _write_wav(path: Path, pcm: bytes, sample_rate: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm)


def _rms_dbfs(pcm: bytes) -> float:
    if not pcm:
        return -96.0
    rms = audioop.rms(pcm, 2)
    if rms <= 0:
        return -96.0
    return 20.0 * math.log10(rms / 32768.0)


def _clip_ratio(pcm: bytes, thresh: int = 32000) -> float:
    if not pcm:
        return 0.0
    n = len(pcm) // 2
    if n == 0:
        return 0.0
    samples = struct.unpack("<" + "h" * n, pcm)
    clipped = sum(1 for s in samples if abs(s) >= thresh)
    return clipped / n


def _frame_energies(pcm: bytes, sample_rate: int, frame_ms: int = 30) -> list[float]:
    frame = max(1, int(sample_rate * frame_ms / 1000))
    step = frame  # non-overlapping
    energies: list[float] = []
    for i in range(0, len(pcm) - frame * 2 + 1, step * 2):
        chunk = pcm[i : i + frame * 2]
        energies.append(float(audioop.rms(chunk, 2)))
    return energies


def _silence_mask(energies: list[float], *, silence_db_below_peak: float = 28.0) -> list[bool]:
    peak = max(energies) if energies else 0.0
    if peak <= 1:
        return [True] * len(energies)
    thresh = peak * (10 ** (-silence_db_below_peak / 20.0))
    return [e < thresh for e in energies]


def _split_on_silence(
    pcm: bytes,
    sample_rate: int,
    *,
    min_clip_sec: float,
    max_clip_sec: float,
    min_silence_ms: int = 400,
) -> list[bytes]:
    """Energy-based split; pad/merge so clips land in [min, max] seconds when possible."""
    if not pcm:
        return []
    total_sec = len(pcm) / 2 / sample_rate
    # Short file: one clip (still measured — not a fake 4.0s stub).
    if total_sec <= max_clip_sec + 0.25:
        return [pcm] if total_sec >= min_clip_sec * 0.5 else [pcm]

    frame_ms = 30
    frame = max(1, int(sample_rate * frame_ms / 1000))
    energies = _frame_energies(pcm, sample_rate, frame_ms=frame_ms)
    silent = _silence_mask(energies)
    min_sil_frames = max(1, int(min_silence_ms / frame_ms))

    # Find speech islands bounded by long silence.
    regions: list[tuple[int, int]] = []
    i = 0
    n = len(silent)
    while i < n:
        while i < n and silent[i]:
            i += 1
        if i >= n:
            break
        start = i
        while i < n:
            if silent[i]:
                run = 0
                j = i
                while j < n and silent[j]:
                    run += 1
                    j += 1
                if run >= min_sil_frames:
                    break
                i = j
            else:
                i += 1
        end = i
        regions.append((start, end))
        i = end

    if not regions:
        regions = [(0, n)]

    clips: list[bytes] = []
    max_frames = max(1, int(max_clip_sec * 1000 / frame_ms))
    min_frames = max(1, int(min_clip_sec * 1000 / frame_ms))

    for start_f, end_f in regions:
        # Force-cut very long islands into max-sized chunks.
        cursor = start_f
        while cursor < end_f:
            piece_end = min(end_f, cursor + max_frames)
            # Prefer cutting near a quieter frame near the end of the window.
            if piece_end < end_f and piece_end - cursor > min_frames:
                window = energies[cursor:piece_end]
                if window:
                    # Search last 25% for lowest energy cut.
                    search_from = cursor + int((piece_end - cursor) * 0.75)
                    best = min(range(search_from, piece_end), key=lambda k: energies[k])
                    piece_end = best
            byte_start = cursor * frame * 2
            byte_end = piece_end * frame * 2
            chunk = pcm[byte_start:byte_end]
            if len(chunk) >= int(min_clip_sec * sample_rate) * 2:
                clips.append(chunk)
            elif chunk:
                # Keep short leftovers only if they have speech energy.
                if _rms_dbfs(chunk) > -45:
                    clips.append(chunk)
            cursor = max(piece_end, cursor + 1)

    return clips or [pcm]


def _label_clip(pcm: bytes, *, rms: float, clip_ratio: float) -> str:
    if not pcm or rms <= -50:
        return "silence"
    if clip_ratio >= 0.01:
        return "clipped"
    # Severely hot / saturating takes — not normal speech loudness (~-20 to -12 dBFS).
    if rms > -6.0:
        return "noisy"
    if clip_ratio >= 0.005 and rms > -14.0:
        return "noisy"
    return "clean"


def prepare(root: Path, input_dir: Path, speaker: str) -> Path:
    cfg = load_config(root)
    sample_rate = int(cfg.get("sample_rate") or 40000)
    min_clip = float(cfg.get("min_clip_length_sec") or 2.0)
    max_clip = float(cfg.get("max_clip_length_sec") or 12.0)

    raw_files = sorted(
        p for p in input_dir.rglob("*") if p.suffix.lower() in AUDIO_EXTS and p.is_file()
    )
    clean_dir = root / "data" / "clean" / speaker
    seg_dir = root / "data" / "segments" / speaker
    clean_dir.mkdir(parents=True, exist_ok=True)
    seg_dir.mkdir(parents=True, exist_ok=True)

    # Remove prior segments for this speaker so counts stay honest.
    for old in seg_dir.glob("seg_*.wav"):
        old.unlink()

    ffmpeg = which("ffmpeg")
    rows: list[dict[str, str]] = []

    if not raw_files:
        meta = seg_dir / "metadata.csv"
        if not meta.is_file():
            demo = ROOT / "data" / "segments" / "demo" / "metadata.csv"
            if demo.is_file():
                shutil.copy(demo, meta)
                print(f"no raw audio - copied demo metadata → {meta.relative_to(root)}")
            else:
                raise SystemExit(f"No audio in {input_dir} and no demo metadata.")
        return meta

    seg_i = 0
    for src_i, src in enumerate(raw_files, start=1):
        pcm, sr = _load_mono_pcm16(src, sample_rate, ffmpeg)
        dest = clean_dir / f"{speaker}_{src_i:03d}.wav"
        _write_wav(dest, pcm, sr)
        print(
            f"cleaned {src.name} → {dest.relative_to(root)} "
            f"({len(pcm)/2/sr:.1f}s · {_rms_dbfs(pcm):.1f} dBFS)"
        )

        clips = _split_on_silence(
            pcm, sr, min_clip_sec=min_clip, max_clip_sec=max_clip
        )
        for clip in clips:
            seg_i += 1
            seg_name = f"seg_{seg_i:03d}.wav"
            seg_path = seg_dir / seg_name
            _write_wav(seg_path, clip, sr)
            dur = len(clip) / 2 / sr
            rms = _rms_dbfs(clip)
            ratio = _clip_ratio(clip)
            label = _label_clip(clip, rms=rms, clip_ratio=ratio)
            rows.append(
                {
                    "path": seg_name,
                    "duration_sec": f"{dur:.3f}",
                    "rms_dbfs": f"{rms:.2f}",
                    "clip_ratio": f"{ratio:.4f}",
                    "label": label,
                }
            )
            print(
                f"  segment {seg_name}  {dur:.2f}s  rms={rms:.1f}  "
                f"clip={ratio:.3%}  → {label.upper()}"
            )

    meta_path = seg_dir / "metadata.csv"
    with meta_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["path", "duration_sec", "rms_dbfs", "clip_ratio", "label"],
        )
        writer.writeheader()
        writer.writerows(rows)

    clean_sec = sum(
        float(r["duration_sec"]) for r in rows if r["label"] == "clean"
    )
    print(
        f"wrote {meta_path.relative_to(root)} "
        f"({len(rows)} clips · {clean_sec/60:.2f} clean minutes)"
    )
    return meta_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--input", type=Path, default=None, help="Raw recordings dir")
    parser.add_argument("--speaker", type=str, default=None)
    args = parser.parse_args()
    cfg = load_config(args.root)
    speaker = args.speaker or cfg.get("speaker_name") or "myvoice"
    input_dir = args.input or (args.root / "data" / "raw")
    meta = prepare(args.root, input_dir, speaker)
    print(f"READY · metadata={meta.relative_to(args.root)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
