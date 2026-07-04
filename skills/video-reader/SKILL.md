---
name: video-reader
description: Read, watch, or transcribe a video or audio file that Claude cannot open natively. Turns a local file OR a URL into things an agent can actually read — still frames it can see, a timestamped speech transcript, and technical metadata. Use whenever the user references a video/movie/clip/recording/screencast/.mp4/.mov/.mkv/.webm/.avi (or an audio file) and wants to know what's in it, what's said, what it looks like, or its format/duration/resolution.
---

# video-reader

Claude has no native video input. This skill bridges that gap by shelling out to
`ffmpeg`/`ffprobe` (and optionally `whisper` and `yt-dlp`) to convert a video into
artifacts Claude *can* read: **frames** (images), a **transcript** (text), and
**metadata** (text).

All scripts live in `scripts/` next to this file. Run them with `python`
(Python 3.9+). They are stdlib-only except transcription, which needs a whisper
backend.

## Step 1 — Figure out what the user actually wants

Map the request to one or more capabilities. Don't do more than asked:

| The user wants… | Use | External dep |
|---|---|---|
| "what does it look like / show me / what's on screen / find the part where…" | `frames.py` | ffmpeg |
| "what do they say / transcribe / subtitles / summarize the talk" | `transcribe.py` | ffmpeg + whisper backend |
| "how long / what resolution / what codec / is it corrupt" | `probe.py` | ffprobe |
| The input is a URL | `fetch.py` first, then the above | yt-dlp |

If the intent is ambiguous (e.g. "tell me about this video"), start with `probe.py`
(cheap), glance at the metadata, then decide: a talking-head/lecture usually wants a
transcript; a silent/visual clip wants frames.

## Step 2 — If the input is a URL, download it first

```bash
python scripts/fetch.py "<URL>"                 # video (≤720p)
python scripts/fetch.py "<URL>" --audio-only    # cheaper, if you only need the transcript
```
It prints `FILE: <absolute path>`. Use that path as the input for the next step.

## Step 3 — Run the right script

**Metadata** (always safe, near-instant):
```bash
python scripts/probe.py "<input>"
```

**Frames** — extract a *small* set, then Read them. Frames cost context tokens, so
keep `--max` low (default 12) and let them stay downscaled.
```bash
python scripts/frames.py "<input>"                       # ~12 evenly-spaced, 768px wide
python scripts/frames.py "<input>" --mode scene          # only on scene changes
python scripts/frames.py "<input>" --start 30 --end 90   # just a time window
python scripts/frames.py "<input>" --max 6 --width 512   # even cheaper
```
It prints one `FRAME: <path>` line per image. **Read those image paths** with the
Read tool to actually see them, then describe/answer.

**Transcript** — timestamped speech to text:
```bash
python scripts/transcribe.py "<input>"                   # base model
python scripts/transcribe.py "<input>" --model small     # more accurate, slower
python scripts/transcribe.py "<input>" --language en      # skip auto-detect
```
It prints the transcript to stdout (and saves `.txt`/`.srt`). Read/quote from that.

## Step 3.5 — Locating a moment (visual + audio together)

To find "the part where X happens": get the transcript first (timestamps point you
at roughly-when), then pull frames from that window with `--start/--end` to confirm
visually. Cheaper and more precise than scanning the whole video frame-by-frame.

## Step 4 — Missing dependencies

If a script exits saying a binary is missing, it already printed the exact install
command for this OS. Relay that to the user and stop — don't try to work around it.
Common one-time setup:
- **ffmpeg/ffprobe** (needed by everything): `winget install Gyan.FFmpeg` (Windows),
  `brew install ffmpeg` (macOS), `sudo apt install ffmpeg` (Linux).
- **transcription backend**: `pip install faster-whisper` (recommended — no torch)
  or `pip install openai-whisper`.
- **URL download**: `pip install yt-dlp`.

## Guardrails

- **Protect your context.** Never extract dozens of frames "to be safe." Start small
  (6–12), Read them, and only pull more (or a specific window) if needed.
- **Prefer `--audio-only` fetch** when the user only wants a transcript.
- Outputs go to a temp dir (`<tmp>/video-reader/<name>/`); mention where files landed
  if the user may want the `.srt`/frames, but you don't need to clean up.
- Long videos: transcription scales with length. Warn before transcribing something
  very long with a large model; suggest `--model base` or a trimmed window.
