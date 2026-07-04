# Show HN draft

**Title (≤80 chars — no emoji, HN style):**
```
Show HN: Video-reader – let Claude Code read video and audio files
```

**URL:** https://github.com/MaximRomanMd/video-reader

**Text (the first comment you post right after submitting — HN convention):**

```
I kept wanting Claude Code to "look at" a screen recording or transcribe a clip, but it
can't open a video file directly. So I built a small skill that bridges the gap: it drives
ffmpeg/ffprobe (and optionally whisper + yt-dlp) to turn a video — local file or URL — into
things the model can actually read:

- frames it can see and describe
- a timestamped speech transcript
- metadata (duration/res/codecs)
- an audio spectrogram + waveform, so it can reason about sound design *without hearing it*

Two design choices I care about:
1. It's context-aware — frames are capped and downscaled by default so reading them doesn't
   blow up the model's context window.
2. Zero heavy deps — the scripts are Python stdlib wrappers around CLIs you probably already
   have; only ffmpeg is required for the core.

It installs as a Claude Code plugin (/plugin install) or a plain skill folder. MIT licensed.

The spectrogram trick was the fun part: the model obviously can't hear audio, but a
spectrogram image lets it infer "constant broadband transients here = rapid gunfire, a
high-freq cascade there = coin/sparkle sounds." Curious if others have better ideas for
giving agents a handle on audio.

Repo: https://github.com/MaximRomanMd/video-reader
```

**Notes**
- Post the repo as the URL; put the text above as the first comment.
- Don't editorialize the title ("cool", "amazing") — HN dislikes it.
- Be around for the first 2–3 hours to answer comments.
