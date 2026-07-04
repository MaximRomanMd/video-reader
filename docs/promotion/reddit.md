# Reddit drafts

## r/ClaudeAI  and  r/ClaudeCode

**Title:**
```
I built a Claude Code skill that lets Claude read video and audio files (frames, transcripts, spectrograms)
```

**Body:**
```
Claude Code can't open a .mp4 — so I made a skill that turns a video (local file or URL) into
things it *can* read:

🖼️ frames it can see and describe
📝 timestamped speech transcript (whisper)
ℹ️ metadata (duration/res/codecs)
🔊 an audio spectrogram + waveform so it can reason about sound design without hearing it
🌐 URL downloads (yt-dlp)

It's context-safe (frames capped + downscaled so they don't nuke the context window) and
zero-heavy-dep (stdlib Python wrapping ffmpeg/whisper/yt-dlp; only ffmpeg required for the core).

Install as a plugin:
  /plugin marketplace add MaximRomanMd/video-reader
  /plugin install video-reader@maximromanmd

…or drop the skill folder into ~/.claude/skills. MIT licensed.

Repo + demo GIF: https://github.com/MaximRomanMd/video-reader

Happy to take feature requests — thinking about a clip-extract helper and batch-over-a-folder next.
```

---

## r/commandline  (frame it as the CLI tool, not the Claude angle)

**Title:**
```
video-reader: tiny stdlib-Python CLIs over ffmpeg/whisper/yt-dlp — frames, transcripts, spectrograms
```

**Body:**
```
Small set of dependency-light scripts I pulled out of a Claude Code skill — useful on their own:

  probe.py       → clean ffprobe metadata summary
  frames.py      → extract frames (interval or scene-cut), auto-downscaled + capped
  audiomap.py    → spectrogram + waveform + loudness stats
  transcribe.py  → whisper transcript (.txt + .srt), faster-whisper or openai-whisper
  fetch.py       → yt-dlp download (--audio-only supported)

Stdlib only (no pip deps beyond the optional whisper backend); ffmpeg does the heavy lifting.
MIT. https://github.com/MaximRomanMd/video-reader
```

**Notes**
- Read each sub's rules; some require flair or restrict "Show off" posts to a weekly thread.
- Reply to your own post with the "why" and answer questions quickly.
