#!/usr/bin/env python3
"""Print a compact, human-readable summary of a video's metadata.

Usage:
    python probe.py INPUT [--json]

INPUT may be any local media file. (For URLs, fetch.py first.)
"""
from __future__ import annotations

import argparse
import json

from common import ffprobe_json, die


def fmt_duration(seconds: float) -> str:
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:d}:{s:02d}"


def human_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f}{unit}" if unit == "B" else f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}TB"


def main() -> None:
    ap = argparse.ArgumentParser(description="Summarize video metadata via ffprobe.")
    ap.add_argument("input")
    ap.add_argument("--json", action="store_true", help="emit raw ffprobe JSON")
    args = ap.parse_args()

    data = ffprobe_json(args.input)
    if args.json:
        print(json.dumps(data, indent=2))
        return

    fmt = data.get("format", {})
    streams = data.get("streams", [])
    if not fmt and not streams:
        die("no metadata found — is this a media file?")

    dur = float(fmt.get("duration", 0) or 0)
    size = int(fmt.get("size", 0) or 0)
    print(f"File     : {fmt.get('filename', args.input)}")
    print(f"Format   : {fmt.get('format_long_name', fmt.get('format_name', '?'))}")
    print(f"Duration : {fmt_duration(dur)}  ({dur:.1f}s)")
    if size:
        print(f"Size     : {human_size(size)}")
    if fmt.get("bit_rate"):
        print(f"Bitrate  : {int(fmt['bit_rate']) // 1000} kb/s")

    for st in streams:
        kind = st.get("codec_type", "?")
        codec = st.get("codec_name", "?")
        if kind == "video":
            fr = st.get("avg_frame_rate", "0/0")
            try:
                num, den = fr.split("/")
                fps = float(num) / float(den) if float(den) else 0
            except Exception:
                fps = 0
            print(f"Video    : {codec}  {st.get('width')}x{st.get('height')}  "
                  f"{fps:.2f} fps  ({st.get('pix_fmt', '?')})")
        elif kind == "audio":
            print(f"Audio    : {codec}  {st.get('sample_rate', '?')} Hz  "
                  f"{st.get('channels', '?')} ch  ({st.get('channel_layout', '?')})")
        elif kind == "subtitle":
            print(f"Subtitle : {codec}  ({st.get('tags', {}).get('language', '?')})")


if __name__ == "__main__":
    main()
