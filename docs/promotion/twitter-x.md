# X / Twitter thread draft

Attach the demo GIF to tweet 1 (media on the first tweet drives the most reach).

---

**1/**
```
Claude Code can't open a video file.

So I taught it to.

video-reader — a skill that turns any video (local or URL) into things Claude can actually read:
frames, transcripts, metadata, even audio spectrograms.

Open source, MIT 👇
[attach demo.gif]
```

**2/**
```
It drives ffmpeg / whisper / yt-dlp under the hood and hands Claude:

🖼️ frames it can see
📝 timestamped transcripts
ℹ️ metadata
🔊 a spectrogram so it can reason about SOUND without hearing it
🌐 URL downloads
```

**3/**
```
Two things I cared about:

• context-safe — frames are capped + downscaled so they don't blow up the model's context
• zero heavy deps — stdlib Python over CLIs you already have; only ffmpeg is required
```

**4/**
```
Install in Claude Code:

/plugin marketplace add MaximRomanMd/video-reader
/plugin install video-reader@maximromanmd

or drop the folder into ~/.claude/skills

Repo: https://github.com/MaximRomanMd/video-reader
```

**5/ (optional hook)**
```
Favorite trick: the model can't HEAR audio, but a spectrogram image lets it infer sound design —
constant broadband spikes = rapid fire, high-freq cascades = coin/sparkle SFX.

Giving agents a handle on audio, one PNG at a time.
```

---

**Hashtags/handles:** `#ClaudeCode` `#AI` — tag @AnthropicAI and reply under relevant Claude Code posts.
Keep hashtags to 1–2; more reads as spam.
