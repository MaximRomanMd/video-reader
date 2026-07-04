# video-reader — a Claude Code skill for reading video & audio

Claude (and most LLM agents) can't open a `.mp4`. This skill teaches Claude Code to
turn a video — local file **or** URL — into things it *can* read:

- 🖼️ **Frames** it can see and describe (via `ffmpeg`)
- 📝 **Timestamped transcripts** of speech (via `whisper`)
- ℹ️ **Metadata**: duration, resolution, codecs, streams (via `ffprobe`)

When you ask Claude something like *"what happens in demo.mp4?"*, *"transcribe this
recording"*, or *"find the part of the screencast where the error pops up"*, it loads
this skill and drives the right tool automatically.

## Install

Copy the `video-reader/` folder into your Claude Code skills directory:

| OS | Path |
|----|------|
| Windows | `%USERPROFILE%\.claude\skills\video-reader` |
| macOS / Linux | `~/.claude/skills/video-reader` |

That's it — Claude Code discovers skills there on the next session. (You can also add
it to a project at `.claude/skills/` or ship it inside a plugin.)

## Dependencies

The skill checks for these and prints the exact install command if one is missing.

| Capability | Needs | Install |
|---|---|---|
| Frames + metadata (core) | `ffmpeg` / `ffprobe` | `winget install Gyan.FFmpeg` · `brew install ffmpeg` · `apt install ffmpeg` |
| Transcription | `faster-whisper` (recommended) or `openai-whisper` | `pip install faster-whisper` |
| URL download | `yt-dlp` | `pip install yt-dlp` |

Only `ffmpeg` is required for the core experience; the rest are optional and pulled in
only when you use that feature.

## Use the scripts directly (no agent required)

```bash
python scripts/probe.py video.mp4
python scripts/frames.py video.mp4 --mode scene --max 8
python scripts/transcribe.py video.mp4 --model small --language en
python scripts/fetch.py "https://example.com/clip" --audio-only
```

Run any script with `-h` for its full option list.

## How it works

`SKILL.md` is the instruction sheet Claude follows; `scripts/` holds thin, stdlib-only
Python wrappers around `ffmpeg`/`ffprobe`/`whisper`/`yt-dlp`. Frames are downscaled and
capped by default so reading them doesn't blow up the agent's context window.

## License

MIT — see [LICENSE](LICENSE). Contributions welcome.
