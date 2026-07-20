"""Shared audio decode / QC helpers for prepare, analyze, and verify."""
from __future__ import annotations

import audioop
import math
import struct
import subprocess
import wave
from pathlib import Path

AUDIO_EXTS = {".wav", ".mp3", ".flac", ".m4a", ".ogg"}

# QC thresholds (dBFS / ratios) — kept in one place for consistent KEEP/DROP.
SILENCE_DBFS = -50.0
HOT_DBFS = -6.0
CLIP_HARD = 0.01
CLIP_SOFT = 0.005
CLIP_SOFT_DBFS = -14.0
SHORT_SPEECH_DBFS = -45.0


def list_audio_files(directory: Path) -> list[Path]:
    if not directory.is_dir():
        return []
    return sorted(
        p for p in directory.rglob("*") if p.is_file() and p.suffix.lower() in AUDIO_EXTS
    )


def rms_dbfs(pcm: bytes) -> float:
    if not pcm:
        return -96.0
    rms = audioop.rms(pcm, 2)
    if rms <= 0:
        return -96.0
    return 20.0 * math.log10(rms / 32768.0)


def clip_ratio(pcm: bytes, *, thresh: int = 32000) -> float:
    """Fraction of samples at/above digital clip threshold."""
    n = len(pcm) // 2
    if n <= 0:
        return 0.0
    # Chunk to avoid one giant unpack on long takes.
    clipped = 0
    step = 48000  # samples per chunk
    for i in range(0, n, step):
        count = min(step, n - i)
        chunk = pcm[i * 2 : (i + count) * 2]
        samples = struct.unpack("<" + "h" * count, chunk)
        clipped += sum(1 for s in samples if abs(s) >= thresh)
    return clipped / n


def label_metrics(rms: float, ratio: float) -> str:
    if rms <= SILENCE_DBFS:
        return "silence"
    if ratio >= CLIP_HARD:
        return "clipped"
    if rms > HOT_DBFS:
        return "noisy"
    if ratio >= CLIP_SOFT and rms > CLIP_SOFT_DBFS:
        return "noisy"
    return "clean"


def write_wav(path: Path, pcm: bytes, sample_rate: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm)


def load_mono_pcm16(
    path: Path, sample_rate: int, ffmpeg: str | None
) -> tuple[bytes, int]:
    """Return (pcm16le mono bytes, sample_rate). Prefer ffmpeg for format coverage."""
    if ffmpeg:
        proc = subprocess.run(
            [
                ffmpeg,
                "-hide_banner",
                "-loglevel",
                "error",
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
            ],
            check=True,
            capture_output=True,
        )
        return proc.stdout, sample_rate

    if path.suffix.lower() != ".wav":
        raise RuntimeError(f"Need ffmpeg to decode {path.suffix} ({path.name})")

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


def measure_wav(path: Path) -> dict[str, float | str]:
    """Measure an on-disk mono/stereo WAV without ffmpeg."""
    with wave.open(str(path), "rb") as wf:
        nch = wf.getnchannels()
        sw = wf.getsampwidth()
        sr = wf.getframerate() or 1
        nframes = wf.getnframes()
        raw = wf.readframes(nframes)
    dur = nframes / float(sr)
    if sw != 2:
        raw = audioop.lin2lin(raw, sw, 2)
    if nch > 1:
        raw = audioop.tomono(raw, 2, 0.5, 0.5)
    rms = rms_dbfs(raw)
    ratio = clip_ratio(raw)
    return {
        "duration_sec": dur,
        "rms_dbfs": rms,
        "clip_ratio": ratio,
        "label": label_metrics(rms, ratio),
    }


def duration_and_clip(path: Path, ffmpeg: str | None) -> tuple[float, float]:
    """Return (duration_sec, clip_ratio) for any supported audio file."""
    if path.suffix.lower() == ".wav":
        try:
            m = measure_wav(path)
            return float(m["duration_sec"]), float(m["clip_ratio"])
        except wave.Error:
            pass

    if not ffmpeg:
        raise RuntimeError(f"Cannot decode {path.name}. Install ffmpeg.")

    # Decode once at a known rate so duration = samples / rate.
    probe_rate = 48000
    pcm = subprocess.run(
        [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(path),
            "-ac",
            "1",
            "-ar",
            str(probe_rate),
            "-f",
            "s16le",
            "-acodec",
            "pcm_s16le",
            "pipe:1",
        ],
        check=True,
        capture_output=True,
    ).stdout
    n = len(pcm) // 2
    dur = n / float(probe_rate)
    return dur, clip_ratio(pcm)


def _frame_energies(pcm: bytes, sample_rate: int, frame_ms: int = 30) -> list[float]:
    frame = max(1, int(sample_rate * frame_ms / 1000))
    energies: list[float] = []
    width = frame * 2
    for i in range(0, len(pcm) - width + 1, width):
        energies.append(float(audioop.rms(pcm[i : i + width], 2)))
    return energies


def _silence_mask(energies: list[float], *, silence_db_below_peak: float = 28.0) -> list[bool]:
    peak = max(energies) if energies else 0.0
    if peak <= 1:
        return [True] * len(energies)
    thresh = peak * (10 ** (-silence_db_below_peak / 20.0))
    return [e < thresh for e in energies]


def split_on_silence(
    pcm: bytes,
    sample_rate: int,
    *,
    min_clip_sec: float,
    max_clip_sec: float,
    min_silence_ms: int = 400,
) -> list[bytes]:
    """Energy-based split into roughly [min_clip_sec, max_clip_sec] chunks."""
    if not pcm:
        return []
    total_sec = len(pcm) / 2 / sample_rate
    if total_sec <= max_clip_sec + 0.25:
        return [pcm]

    frame_ms = 30
    frame = max(1, int(sample_rate * frame_ms / 1000))
    energies = _frame_energies(pcm, sample_rate, frame_ms=frame_ms)
    if not energies:
        return [pcm]
    silent = _silence_mask(energies)
    min_sil_frames = max(1, int(min_silence_ms / frame_ms))

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
        regions.append((start, i))
        i = max(i, start + 1)

    if not regions:
        regions = [(0, n)]

    clips: list[bytes] = []
    max_frames = max(1, int(max_clip_sec * 1000 / frame_ms))
    min_frames = max(1, int(min_clip_sec * 1000 / frame_ms))
    min_bytes = int(min_clip_sec * sample_rate) * 2

    for start_f, end_f in regions:
        cursor = start_f
        while cursor < end_f:
            piece_end = min(end_f, cursor + max_frames)
            if piece_end < end_f and piece_end - cursor > min_frames:
                search_from = cursor + int((piece_end - cursor) * 0.75)
                if search_from < piece_end:
                    piece_end = min(
                        range(search_from, piece_end),
                        key=lambda k: energies[k],
                    )
            if piece_end <= cursor:
                piece_end = min(end_f, cursor + 1)
            chunk = pcm[cursor * frame * 2 : piece_end * frame * 2]
            if len(chunk) >= min_bytes:
                clips.append(chunk)
            elif chunk and rms_dbfs(chunk) > SHORT_SPEECH_DBFS:
                clips.append(chunk)
            cursor = piece_end

    return clips or [pcm]
