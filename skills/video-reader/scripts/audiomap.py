#!/usr/bin/env python3
"""Characterize a file's AUDIO without listening to it.

Sound effects and music aren't speech, so a transcript won't capture them. This
renders two images an agent *can* read to reason about audio design:

  * a spectrogram  (frequency content over time — bass hits, sparkles, stingers)
  * a waveform     (amplitude over time — where the loud events land)

and prints the loudest moments (mean/peak volume) as text. Pair the timestamps
with frames.py at the same --start to see what made the noise.

Usage:
    python audiomap.py INPUT [--out DIR]

Prints IMAGE: <path> lines for the rendered images (Read them).
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from common import require, run, out_dir, die


def render_spectrogram(ffmpeg: str, src: str, dest: Path) -> Path:
    out = dest / "spectrogram.png"
    run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", src,
         "-lavfi", "showspectrumpic=s=1280x480:legend=1:mode=combined:color=intensity",
         str(out)])
    return out


def render_waveform(ffmpeg: str, src: str, dest: Path) -> Path:
    out = dest / "waveform.png"
    run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", src,
         "-lavfi", "showwavespic=s=1280x240:split_channels=1",
         str(out)])
    return out


def volume_stats(ffmpeg: str, src: str) -> str:
    # volumedetect writes mean/max volume + histogram to stderr.
    proc = run([ffmpeg, "-hide_banner", "-i", src, "-af", "volumedetect",
                "-f", "null", "-"])
    text = (proc.stderr or "") + (proc.stdout or "")
    wanted = ("mean_volume", "max_volume", "n_samples")
    lines = [ln.split("] ", 1)[-1].strip()
        for ln in text.splitlines() if any(w in ln for w in wanted)]
    return "\n".join(lines) if lines else "(volume stats unavailable)"


def main() -> None:
    ap = argparse.ArgumentParser(description="Render audio spectrogram + waveform.")
    ap.add_argument("input")
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    ffmpeg = require("ffmpeg")
    # Fail early with a clear message if the file has no audio stream.
    from common import ffprobe_json
    if not any(s.get("codec_type") == "audio" for s in ffprobe_json(args.input).get("streams", [])):
        die("no audio stream in this file.")

    dest = Path(args.out) if args.out else out_dir(args.input)
    dest.mkdir(parents=True, exist_ok=True)

    spec = render_spectrogram(ffmpeg, args.input, dest)
    wave = render_waveform(ffmpeg, args.input, dest)
    print("Volume:")
    print(volume_stats(ffmpeg, args.input))
    print(f"IMAGE: {spec}")
    print(f"IMAGE: {wave}")


if __name__ == "__main__":
    main()
