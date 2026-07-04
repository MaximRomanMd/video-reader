#!/usr/bin/env python3
"""Download a video from a URL to a local file via yt-dlp.

Prints the absolute path of the downloaded file prefixed with 'FILE:' so the
calling agent can hand it to probe.py / frames.py / transcribe.py.

Usage:
    python fetch.py URL [--max-height H] [--audio-only] [--out DIR]
"""
from __future__ import annotations

import argparse
from pathlib import Path

from common import require, run, out_dir, die, is_url


def main() -> None:
    ap = argparse.ArgumentParser(description="Download a video by URL with yt-dlp.")
    ap.add_argument("url")
    ap.add_argument("--max-height", type=int, default=720,
                    help="cap video height to keep downloads small (default 720)")
    ap.add_argument("--audio-only", action="store_true",
                    help="fetch audio only (best for transcription)")
    ap.add_argument("--out", default="", help="output directory (default: temp)")
    args = ap.parse_args()

    if not is_url(args.url):
        die("argument does not look like a URL (expected http:// or https://).")

    ytdlp = require("yt-dlp")
    dest = Path(args.out) if args.out else out_dir(args.url.rsplit("/", 1)[-1] or "download")
    dest.mkdir(parents=True, exist_ok=True)
    template = str(dest / "%(title).60s.%(ext)s")

    if args.audio_only:
        fmt = "bestaudio/best"
    else:
        fmt = f"bestvideo[height<={args.max_height}]+bestaudio/best[height<={args.max_height}]/best"

    before = set(dest.iterdir())
    run([ytdlp, "-f", fmt, "--no-playlist", "--restrict-filenames",
         "-o", template, args.url])

    new = sorted(set(dest.iterdir()) - before, key=lambda p: p.stat().st_mtime, reverse=True)
    downloaded = next((p for p in new if p.is_file()), None)
    if not downloaded:
        # Re-download to an existing file is possible; fall back to newest media file.
        media = sorted(dest.glob("*.*"), key=lambda p: p.stat().st_mtime, reverse=True)
        downloaded = media[0] if media else None
    if not downloaded:
        die("download reported success but no file was found.")

    print(f"FILE: {downloaded}")


if __name__ == "__main__":
    main()
