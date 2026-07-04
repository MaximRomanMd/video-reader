#!/usr/bin/env python3
"""Transcribe a video/audio file's speech to timestamped text.

Prefers `faster-whisper` (fast, no torch); falls back to `openai-whisper`.
Audio is extracted to 16 kHz mono WAV via ffmpeg first, so any container works.

Output: a plain timestamped transcript to stdout, e.g.
    [00:00 -> 00:04] Welcome back to the channel.
Also writes a .txt and .srt next to the input's temp dir.

Usage:
    python transcribe.py INPUT [--model MODEL] [--language LANG] [--out DIR]

MODEL: tiny | base | small | medium | large-v3  (default: base)
"""
from __future__ import annotations

import argparse
from pathlib import Path

from common import require, run, out_dir, die


def extract_audio(input_path: str, dest: Path) -> Path:
    ffmpeg = require("ffmpeg")
    wav = dest / "audio.wav"
    run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
         "-i", input_path, "-vn", "-ac", "1", "-ar", "16000",
         "-f", "wav", str(wav)])
    return wav


def ts(seconds: float) -> str:
    seconds = max(0.0, seconds)
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def srt_ts(seconds: float) -> str:
    ms = int((seconds - int(seconds)) * 1000)
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def transcribe(wav: Path, model: str, language: str | None):
    """Yield (start, end, text) segments using whichever backend is installed."""
    try:
        from faster_whisper import WhisperModel  # type: ignore
        m = WhisperModel(model, device="cpu", compute_type="int8")
        segments, _ = m.transcribe(str(wav), language=language, vad_filter=True)
        for seg in segments:
            yield seg.start, seg.end, seg.text.strip()
        return
    except ImportError:
        pass

    try:
        import whisper  # type: ignore
    except ImportError:
        die("no transcription backend found. Install one with:\n"
            "    pip install faster-whisper      (recommended, no torch)\n"
            "    pip install openai-whisper       (alternative)")

    m = whisper.load_model(model)
    result = m.transcribe(str(wav), language=language)
    for seg in result.get("segments", []):
        yield seg["start"], seg["end"], seg["text"].strip()


def main() -> None:
    ap = argparse.ArgumentParser(description="Transcribe speech from a video/audio file.")
    ap.add_argument("input")
    ap.add_argument("--model", default="base",
                    help="tiny|base|small|medium|large-v3 (default base)")
    ap.add_argument("--language", default=None, help="force a language code, e.g. en")
    ap.add_argument("--out", default="", help="output directory (default: temp)")
    args = ap.parse_args()

    dest = Path(args.out) if args.out else out_dir(args.input)
    dest.mkdir(parents=True, exist_ok=True)
    wav = extract_audio(args.input, dest)

    segments = list(transcribe(wav, args.model, args.language))
    if not segments:
        die("no speech detected.")

    lines, srt = [], []
    for i, (start, end, text) in enumerate(segments, 1):
        if not text:
            continue
        lines.append(f"[{ts(start)} -> {ts(end)}] {text}")
        srt.append(f"{i}\n{srt_ts(start)} --> {srt_ts(end)}\n{text}\n")

    transcript = "\n".join(lines)
    (dest / "transcript.txt").write_text(transcript + "\n", encoding="utf-8")
    (dest / "transcript.srt").write_text("\n".join(srt) + "\n", encoding="utf-8")

    print(transcript)
    print(f"\nSaved: {dest / 'transcript.txt'}  and  {dest / 'transcript.srt'}")


if __name__ == "__main__":
    main()
