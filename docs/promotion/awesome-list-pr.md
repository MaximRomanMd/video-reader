# Awesome-list PR kit

Evergreen discovery: get listed on the community "awesome" indexes. These are curated GitHub lists
Claude Code users browse for skills/plugins. **You open the PRs** (they post under your account).

## Targets (search GitHub for the current canonical repos before submitting)
- `awesome-claude-code`
- `awesome-claude-code-skills` / `awesome-claude-skills`
- `awesome-claude-code-plugins`
- `awesome-mcp` / agent-tooling lists (if a "skills" or "tools" section fits)
- `awesome-ffmpeg` (as a downstream ffmpeg tool)

## Steps per list
1. Read the list's `CONTRIBUTING` — match its exact format, alphabetical order, and section.
2. Fork → add one line in the right section → PR.
3. Keep the PR description tiny and to their template.

## Line to add (Markdown — adjust to the list's format)
```
- [video-reader](https://github.com/MaximRomanMd/video-reader) — Let Claude read video/audio files: frames, transcripts, metadata, spectrograms, and URL downloads via ffmpeg/whisper/yt-dlp. Installs as a plugin or skill.
```

## One-liner variants (some lists want shorter)
```
video-reader — turn any video/URL into frames, transcripts, metadata & spectrograms Claude can read.
```

## PR description template
```
Adds **video-reader**, a Claude Code skill + plugin that lets Claude read video/audio files
(frames, transcripts, metadata, audio spectrograms, URL downloads) via ffmpeg/whisper/yt-dlp.
MIT licensed, cross-platform, stdlib-only Python.

Repo: https://github.com/MaximRomanMd/video-reader
```

**Tip:** if a list has an open "add your project" issue template instead of freeform PRs, use that.
