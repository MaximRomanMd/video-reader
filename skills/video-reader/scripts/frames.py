#!/usr/bin/env python3
"""Extract still frames from a video so an agent can *see* its content.

Two selection modes:
  * interval (default): one frame every N seconds, evenly spread
  * scene: only frames where the picture changes a lot (scene cuts)

Frames are downscaled by default to keep them cheap to read. The script prints
the absolute path of every frame it wrote, one per line prefixed with 'FRAME:',
so the calling agent can Read them directly.

Usage:
    python frames.py INPUT [--mode interval|scene] [--max N] [--width W]
                           [--fps F] [--scene-threshold T]
                           [--start SECONDS] [--end SECONDS] [--out DIR]
"""
from __future__ import annotations

import argparse
from pathlib import Path

from common import require, run, out_dir, duration_seconds, die


def clear_old_frames(d: Path) -> None:
    for f in d.glob("frame_*.png"):
        f.unlink()


def main() -> None:
    ap = argparse.ArgumentParser(description="Extract frames from a video.")
    ap.add_argument("input")
    ap.add_argument("--mode", choices=["interval", "scene"], default="interval")
    ap.add_argument("--max", type=int, default=12,
                    help="max frames to emit (default 12; keeps agent context small)")
    ap.add_argument("--width", type=int, default=768,
                    help="downscale frames to this width, keeping aspect (0 = full res)")
    ap.add_argument("--fps", type=float, default=0.0,
                    help="interval mode: frames per second (overrides auto-spacing)")
    ap.add_argument("--scene-threshold", type=float, default=0.30,
                    help="scene mode: 0-1 change sensitivity (lower = more frames)")
    ap.add_argument("--start", type=float, default=0.0, help="start offset in seconds")
    ap.add_argument("--end", type=float, default=0.0, help="end offset in seconds (0 = end)")
    ap.add_argument("--out", default="", help="output directory (default: temp)")
    args = ap.parse_args()

    ffmpeg = require("ffmpeg")
    dest = Path(args.out) if args.out else out_dir(args.input)
    dest.mkdir(parents=True, exist_ok=True)
    clear_old_frames(dest)

    scale = f",scale={args.width}:-2" if args.width else ""

    # Trim window applied as input options for speed/accuracy.
    trim: list[str] = []
    if args.start:
        trim += ["-ss", str(args.start)]
    if args.end:
        length = max(0.0, args.end - args.start)
        if length:
            trim += ["-t", str(length)]

    if args.mode == "scene":
        vf = f"select='gt(scene,{args.scene_threshold})'{scale}"
        extra = ["-vsync", "vfr"]
    else:
        # Auto-space frames across the (possibly trimmed) duration to hit ~--max.
        if args.fps > 0:
            fps = args.fps
        else:
            total = duration_seconds(args.input)
            if args.end:
                total = min(total, args.end) if total else args.end
            span = max(1.0, (total or 0) - args.start)
            fps = max(args.max / span, 1e-6)
        vf = f"fps={fps:g}{scale}"
        extra = []

    pattern = str(dest / "frame_%04d.png")
    cmd = [ffmpeg, "-hide_banner", "-loglevel", "error", *trim,
           "-i", args.input, "-vf", vf, *extra,
           "-frames:v", str(args.max), pattern]
    run(cmd)

    frames = sorted(dest.glob("frame_*.png"))
    if not frames:
        die("no frames extracted — try --mode interval, a lower --scene-threshold, "
            "or check the trim window.")

    print(f"Extracted {len(frames)} frame(s) [{args.mode}] to {dest}")
    for f in frames:
        print(f"FRAME: {f}")


if __name__ == "__main__":
    main()
