#!/usr/bin/env python3
"""video-reader MCP server.

Exposes the video-reader capabilities as MCP tools so any MCP client (Claude
Desktop, IDEs, etc.) can let the model read video/audio files. Unlike a plain
CLI, the frame/spectrogram tools return the images *inline* in the tool result,
so the model sees them directly — no separate file-read step.

Tools:
  get_video_info(path)          -> text metadata (ffprobe)
  extract_frames(path, ...)     -> frames as inline images (ffmpeg)
  transcribe(path, ...)         -> timestamped speech transcript (whisper)
  audio_spectrogram(path)       -> spectrogram + waveform inline images (ffmpeg)
  fetch_video(url, ...)         -> download a URL to a local file (yt-dlp)

Requires: ffmpeg/ffprobe on PATH (core). Optional: faster-whisper|openai-whisper
(transcription), yt-dlp (URL download). Run:  python server.py
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from mcp.server.fastmcp import FastMCP, Image

mcp = FastMCP("video-reader")

# ── binary resolution ────────────────────────────────────────────────────────
# Prefer PATH; fall back to common install locations so the server works even
# when the launching client has a minimal PATH (a frequent Claude Desktop gotcha).
_WIN_FFMPEG_GLOBS = [
    os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg*\**\bin"),
    r"C:\Program Files\ffmpeg\bin",
    r"C:\ffmpeg\bin",
]


def _resolve(binary: str) -> str:
    found = shutil.which(binary)
    if found:
        return found
    if sys.platform == "win32":
        import glob
        for pat in _WIN_FFMPEG_GLOBS:
            for d in glob.glob(pat, recursive=True):
                cand = Path(d) / f"{binary}.exe"
                if cand.exists():
                    return str(cand)
    raise RuntimeError(
        f"'{binary}' not found. Install ffmpeg "
        "(winget install Gyan.FFmpeg | brew install ffmpeg | apt install ffmpeg) "
        "and ensure it is on PATH."
    )


def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        tail = "\n".join((proc.stderr or proc.stdout or "").strip().splitlines()[-8:])
        raise RuntimeError(f"{Path(cmd[0]).name} failed:\n{tail}")
    return proc


def _ffprobe_json(path: str) -> dict:
    proc = _run([_resolve("ffprobe"), "-v", "quiet", "-print_format", "json",
                 "-show_format", "-show_streams", path])
    return json.loads(proc.stdout)


def _out_dir(hint: str) -> Path:
    safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in Path(hint).stem)[:40]
    d = Path(tempfile.gettempdir()) / "video-reader-mcp" / (safe or "out")
    d.mkdir(parents=True, exist_ok=True)
    return d


def _duration(path: str) -> float:
    try:
        return float(_ffprobe_json(path).get("format", {}).get("duration", 0.0))
    except Exception:
        return 0.0


def _check_input(path: str) -> None:
    if path.startswith(("http://", "https://")):
        raise ValueError("This tool takes a LOCAL file. Use fetch_video(url) first, "
                         "then pass the returned path.")
    if not Path(path).is_file():
        raise FileNotFoundError(f"No such file: {path}")


# ── tools ────────────────────────────────────────────────────────────────────
@mcp.tool()
def get_video_info(path: str) -> str:
    """Return a compact metadata summary of a local video/audio file
    (format, duration, resolution, codecs, streams)."""
    _check_input(path)
    data = _ffprobe_json(path)
    fmt, streams = data.get("format", {}), data.get("streams", [])
    dur = float(fmt.get("duration", 0) or 0)
    m, s = divmod(int(dur), 60)
    h, m = divmod(m, 60)
    lines = [
        f"File     : {fmt.get('filename', path)}",
        f"Format   : {fmt.get('format_long_name', fmt.get('format_name', '?'))}",
        f"Duration : {h}:{m:02d}:{s:02d}  ({dur:.1f}s)",
    ]
    if fmt.get("size"):
        lines.append(f"Size     : {int(fmt['size']) / 1_048_576:.1f} MB")
    for st in streams:
        k = st.get("codec_type")
        if k == "video":
            lines.append(f"Video    : {st.get('codec_name')}  "
                         f"{st.get('width')}x{st.get('height')}  ({st.get('pix_fmt')})")
        elif k == "audio":
            lines.append(f"Audio    : {st.get('codec_name')}  {st.get('sample_rate')} Hz  "
                         f"{st.get('channels')} ch")
    return "\n".join(lines)


@mcp.tool()
def extract_frames(path: str, mode: str = "interval", max_frames: int = 12,
                   width: int = 768, scene_threshold: float = 0.3,
                   start: float = 0.0, end: float = 0.0) -> list:
    """Extract still frames from a local video and return them as inline images
    so you can SEE the content.

    mode: "interval" (evenly spaced, default) or "scene" (only on scene changes).
    max_frames: cap on frames returned (keep modest — images cost context).
    width: downscale width in px (0 = full res). start/end: trim window in seconds.
    """
    _check_input(path)
    max_frames = max(1, min(int(max_frames), 40))
    dest = _out_dir(path)
    for f in dest.glob("frame_*.png"):
        f.unlink()
    scale = f",scale={int(width)}:-2" if width else ""
    trim: list[str] = []
    if start:
        trim += ["-ss", str(start)]
    if end and end > start:
        trim += ["-t", str(end - start)]

    if mode == "scene":
        vf, extra = f"select='gt(scene,{scene_threshold})'{scale}", ["-vsync", "vfr"]
    else:
        total = _duration(path) or 0
        span = max(1.0, (min(total, end) if end else total) - start)
        vf, extra = f"fps={max(max_frames / span, 1e-6):g}{scale}", []

    _run([_resolve("ffmpeg"), "-hide_banner", "-loglevel", "error", *trim, "-i", path,
          "-vf", vf, *extra, "-frames:v", str(max_frames), str(dest / "frame_%04d.png")])
    frames = sorted(dest.glob("frame_*.png"))
    if not frames:
        raise RuntimeError("No frames extracted — try mode='interval' or a lower "
                           "scene_threshold, or check the trim window.")
    out: list = [f"Extracted {len(frames)} frame(s) [{mode}] from {Path(path).name}"]
    out += [Image(path=str(f)) for f in frames]
    return out


@mcp.tool()
def transcribe(path: str, model: str = "base", language: str | None = None) -> str:
    """Transcribe speech from a local video/audio file to timestamped text.
    model: tiny|base|small|medium|large-v3 (default base). language: e.g. 'en'
    (omit to auto-detect). Needs faster-whisper or openai-whisper installed."""
    _check_input(path)
    dest = _out_dir(path)
    wav = dest / "audio.wav"
    _run([_resolve("ffmpeg"), "-hide_banner", "-loglevel", "error", "-y", "-i", path,
          "-vn", "-ac", "1", "-ar", "16000", "-f", "wav", str(wav)])

    def _ts(x: float) -> str:
        x = max(0.0, x)
        m, s = divmod(int(x), 60)
        h, m = divmod(m, 60)
        return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"

    segments: list[tuple[float, float, str]] = []
    try:
        from faster_whisper import WhisperModel  # type: ignore
        m = WhisperModel(model, device="cpu", compute_type="int8")
        segs, _ = m.transcribe(str(wav), language=language, vad_filter=True)
        segments = [(s.start, s.end, s.text.strip()) for s in segs]
    except ImportError:
        try:
            import whisper  # type: ignore
        except ImportError:
            raise RuntimeError("No transcription backend. Install one:\n"
                               "  pip install faster-whisper   (recommended)\n"
                               "  pip install openai-whisper")
        res = whisper.load_model(model).transcribe(str(wav), language=language)
        segments = [(s["start"], s["end"], s["text"].strip()) for s in res.get("segments", [])]

    lines = [f"[{_ts(a)} -> {_ts(b)}] {t}" for a, b, t in segments if t]
    return "\n".join(lines) if lines else "(no speech detected)"


@mcp.tool()
def audio_spectrogram(path: str) -> list:
    """Render a spectrogram + waveform of a local file's audio and return them as
    inline images, so you can reason about sound design (bass hits, sparkles,
    stingers) WITHOUT hearing it. Also returns mean/peak volume."""
    _check_input(path)
    if not any(s.get("codec_type") == "audio" for s in _ffprobe_json(path).get("streams", [])):
        raise ValueError("No audio stream in this file.")
    dest = _out_dir(path)
    ff = _resolve("ffmpeg")
    spec, wave = dest / "spectrogram.png", dest / "waveform.png"
    _run([ff, "-hide_banner", "-loglevel", "error", "-y", "-i", path, "-lavfi",
          "showspectrumpic=s=1280x480:legend=1:mode=combined:color=intensity", str(spec)])
    _run([ff, "-hide_banner", "-loglevel", "error", "-y", "-i", path, "-lavfi",
          "showwavespic=s=1280x240:split_channels=1", str(wave)])
    vproc = _run([ff, "-hide_banner", "-i", path, "-af", "volumedetect", "-f", "null", "-"])
    vol = [ln.split("] ", 1)[-1].strip() for ln in (vproc.stderr or "").splitlines()
           if "mean_volume" in ln or "max_volume" in ln]
    return [f"Audio of {Path(path).name}\n" + "\n".join(vol),
            Image(path=str(spec)), Image(path=str(wave))]


@mcp.tool()
def fetch_video(url: str, audio_only: bool = False, max_height: int = 720) -> str:
    """Download a video from a URL to a local file (via yt-dlp) and return its
    absolute path — pass that path to the other tools. audio_only=True fetches
    just audio (cheaper for transcription)."""
    if not url.startswith(("http://", "https://")):
        raise ValueError("Expected an http(s) URL.")
    ytdlp = _resolve("yt-dlp") if shutil.which("yt-dlp") else None
    if not ytdlp:
        raise RuntimeError("yt-dlp not found. Install it:  pip install yt-dlp")
    dest = _out_dir(url.rsplit("/", 1)[-1] or "download")
    fmt = ("bestaudio/best" if audio_only
           else f"bestvideo[height<={max_height}]+bestaudio/best[height<={max_height}]/best")
    before = set(dest.iterdir())
    _run([ytdlp, "-f", fmt, "--no-playlist", "--restrict-filenames",
          "-o", str(dest / "%(title).60s.%(ext)s"), url])
    new = [p for p in (set(dest.iterdir()) - before) if p.is_file()]
    if not new:
        new = sorted(dest.glob("*.*"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not new:
        raise RuntimeError("Download reported success but no file was found.")
    return str(max(new, key=lambda p: p.stat().st_mtime))


if __name__ == "__main__":
    mcp.run()
