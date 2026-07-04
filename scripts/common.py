"""Shared helpers for the video-reader skill scripts.

Kept dependency-free (stdlib only). Each user-facing script imports from here
so dependency checks, output paths, and error formatting stay consistent.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# One-line install hints per platform, shown when a binary is missing.
INSTALL_HINTS = {
    "ffmpeg": {
        "win32": "winget install Gyan.FFmpeg",
        "darwin": "brew install ffmpeg",
        "linux": "sudo apt install ffmpeg  (or your distro's package manager)",
    },
    "ffprobe": {
        "win32": "winget install Gyan.FFmpeg",
        "darwin": "brew install ffmpeg",
        "linux": "sudo apt install ffmpeg",
    },
    "yt-dlp": {
        "win32": "pip install yt-dlp",
        "darwin": "pip install yt-dlp  (or brew install yt-dlp)",
        "linux": "pip install yt-dlp",
    },
}


def die(msg: str, code: int = 1) -> "None":
    """Print an error to stderr and exit."""
    print(f"video-reader: {msg}", file=sys.stderr)
    sys.exit(code)


def require(binary: str) -> str:
    """Return the resolved path to `binary`, or exit with an install hint."""
    found = shutil.which(binary)
    if found:
        return found
    hint = INSTALL_HINTS.get(binary, {}).get(sys.platform, f"install {binary} and put it on PATH")
    die(f"'{binary}' not found on PATH. Install it with:\n    {hint}")


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    """Run a command, capturing output; raise a clean error on failure."""
    proc = subprocess.run(cmd, capture_output=True, text=True, **kwargs)
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "").strip().splitlines()[-8:]
        die(f"command failed ({' '.join(Path(cmd[0]).name.split())}):\n" + "\n".join(tail))
    return proc


def out_dir(name_hint: str) -> Path:
    """A stable per-input output directory under the system temp dir.

    Reused across runs for the same input so we don't scatter temp files.
    """
    safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in Path(name_hint).stem)[:40]
    d = Path(tempfile.gettempdir()) / "video-reader" / (safe or "out")
    d.mkdir(parents=True, exist_ok=True)
    return d


def ffprobe_json(input_path: str) -> dict:
    """Return the parsed ffprobe JSON for an input (format + streams)."""
    ffprobe = require("ffprobe")
    proc = run([
        ffprobe, "-v", "quiet", "-print_format", "json",
        "-show_format", "-show_streams", input_path,
    ])
    return json.loads(proc.stdout)


def duration_seconds(input_path: str) -> float:
    """Best-effort media duration in seconds (0.0 if unknown)."""
    try:
        return float(ffprobe_json(input_path).get("format", {}).get("duration", 0.0))
    except Exception:
        return 0.0


def is_url(s: str) -> bool:
    return s.startswith(("http://", "https://"))
