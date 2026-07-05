# video-reader — MCP server

Exposes video-reader as an **MCP server** so any MCP client (Claude Desktop, IDEs,
other agents) can read video/audio files. The frame and spectrogram tools return
their images **inline in the tool result**, so the model sees them directly.

## Tools
| Tool | Returns |
|---|---|
| `get_video_info(path)` | metadata text (format, duration, resolution, codecs) |
| `extract_frames(path, mode, max_frames, width, …)` | frames as **inline images** |
| `transcribe(path, model, language)` | timestamped speech transcript |
| `audio_spectrogram(path)` | spectrogram + waveform **inline images** + volume |
| `fetch_video(url, audio_only, max_height)` | downloads a URL → local path |

## Requirements
- **Python 3.10+**
- **ffmpeg / ffprobe** on PATH (core) — the server also auto-discovers a WinGet
  ffmpeg install on Windows if PATH is minimal.
  `winget install Gyan.FFmpeg` · `brew install ffmpeg` · `apt install ffmpeg`
- Optional: `pip install faster-whisper` (transcription), `pip install yt-dlp` (URL download)

## Install
```bash
pip install "mcp[cli]"
# optional extras:
pip install faster-whisper yt-dlp
```

### Claude Desktop
Add to your `claude_desktop_config.json`
(macOS: `~/Library/Application Support/Claude/`, Windows: `%APPDATA%\Claude\`):

```json
{
  "mcpServers": {
    "video-reader": {
      "command": "python",
      "args": ["/ABSOLUTE/PATH/TO/video-reader/mcp/server.py"]
    }
  }
}
```
Windows example: `"args": ["C:\\Users\\<you>\\video-reader\\mcp\\server.py"]`.
Restart Claude Desktop; the `video-reader` tools appear in the tools menu.

### Claude Code
```bash
claude mcp add video-reader -- python /ABSOLUTE/PATH/TO/video-reader/mcp/server.py
```

### Any MCP client
Run the server over stdio: `python /path/to/video-reader/mcp/server.py`
(or `mcp dev server.py` to try it in the MCP Inspector).

## Notes
- Frames are downscaled (default 768px) and capped (default 12, max 40) so image
  payloads stay reasonable — raise `max_frames`/`width` when you need more detail.
- Outputs are written under your system temp dir (`<tmp>/video-reader-mcp/`).
- The tools take **local file paths**; for a URL, call `fetch_video(url)` first and
  pass the returned path to the others.

Same project also ships a Claude Code **skill** (`../skills/video-reader`) — see the
[top-level README](../README.md).
