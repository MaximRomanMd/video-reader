# dev.to / blog deep-dive draft

**Title:** Teaching Claude Code to Watch Video (and "Hear" Audio)

**Tags:** claude, ai, python, ffmpeg

**Canonical URL:** point back to your blog if you cross-post.

---

## The gap

Claude Code is great at reading code and text, but hand it a `screen-recording.mp4` and it's stuck —
LLMs don't ingest video. I hit this constantly: "what's in this clip?", "transcribe this", "find the
moment the bug shows up." So I built a small skill, **video-reader**, that closes the gap.

## The idea

Don't make the model read video. Make *tools* turn the video into things the model already reads:
**images and text.** The skill drives `ffmpeg`/`ffprobe` (plus optional `whisper` and `yt-dlp`) and
returns:

- **frames** → Claude sees and describes them
- **transcript** → timestamped speech (`.txt` + `.srt`)
- **metadata** → duration, resolution, codecs
- **audio spectrogram + waveform** → reason about sound *without hearing it*

## Two decisions that matter

**1. Protect the context window.** The naïve version dumps 200 full-res frames and torches the
model's context. video-reader caps frames (12 by default) and downscales them, and the SKILL.md
tells Claude to start small and only pull more if needed.

**2. Keep it dependency-light.** The scripts are Python **stdlib** wrappers around CLIs. Only
`ffmpeg` is required for the core; `whisper`/`yt-dlp` load lazily when you use them. Each script
prints the exact per-OS install command if a binary is missing.

## The audio trick

The model can't hear. But sound has a *picture*: a spectrogram. Render one and Claude can infer the
design — a dense stack of broadband transients reads as rapid gunfire; a cluster of 7–9 kHz spikes
reads as coin/sparkle SFX; one full-spectrum blast is a big-win stinger. It's not hearing, but it's
a real, useful handle on audio.

```python
# audiomap.py (excerpt) — a spectrogram Claude can read
ffmpeg -i input.mp4 -lavfi showspectrumpic=s=1280x480:legend=1 spectrogram.png
```

## Install

```
/plugin marketplace add MaximRomanMd/video-reader
/plugin install video-reader@maximromanmd
```

…or copy the `skills/video-reader` folder into `~/.claude/skills`.

## What's next

A `clip.py` sub-range extractor, batch-over-a-folder, and frame caching by input hash. PRs welcome —
it's MIT: **https://github.com/MaximRomanMd/video-reader**

*If you build agents, the general lesson generalizes: when a model can't consume a modality directly,
the win is usually a cheap tool that projects it into a modality the model already handles.*
