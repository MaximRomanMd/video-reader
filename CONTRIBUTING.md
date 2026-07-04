# Contributing to video-reader

Thanks for your interest! This is a small, focused Claude Code skill — contributions that keep it
small and dependency-light are very welcome.

## Ground rules
- **Stdlib-only Python** for the scripts (plus the external CLIs `ffmpeg`/`whisper`/`yt-dlp`). No pip
  packages beyond the optional transcription backend.
- **Fail loud, fail helpful.** If a binary is missing, print the exact per-OS install command (see
  `scripts/common.py`).
- **Protect the agent's context.** Frame/output counts stay capped and downscaled by default.
- Keep it cross-platform (Windows / macOS / Linux).

## Dev setup
```bash
git clone https://github.com/MaximRomanMd/video-reader
cd video-reader
# core dep
#   winget install Gyan.FFmpeg   |   brew install ffmpeg   |   apt install ffmpeg
python -m py_compile skills/video-reader/scripts/*.py     # syntax check
python skills/video-reader/scripts/probe.py some.mp4      # smoke test
```

## Ideas / good first issues
- A `--srt`/`--vtt` export flag surfaced more prominently
- Scene-detection tuning presets
- A `clip.py` helper (extract a sub-range to a new file)
- Batch mode over a folder
- Optional caching of extracted frames per input hash

## PRs
- One focused change per PR, with a line in the PR description on what you tested.
- If you add a script or flag, update `skills/video-reader/SKILL.md` so Claude knows how to use it.

By contributing you agree your work is licensed under the repository's [MIT License](LICENSE).
