# audio-to-youtube-video

Batch-encode a folder of audio tracks into YouTube-ready 1080p MP4s by looping a short video clip for the full duration of each track.

Drop your audio files in, double-click (on Mac), and get back a folder of upload-ready videos.

---

## Requirements

- **Python 3.8+** — [python.org](https://www.python.org/downloads/)
- **ffmpeg** — must be on your `PATH`
  - Mac: `brew install ffmpeg`
  - Windows: [ffmpeg.org/download.html](https://ffmpeg.org/download.html) → add `bin/` to PATH
  - Linux: `sudo apt install ffmpeg`

---

## Folder structure

```
audio-to-youtube-video/
├── make_videos.py          # main script
├── Make Videos.command     # macOS double-click launcher
├── tunes/                  # ← put your audio files here
│   └── (add .mp3 / .wav / .flac / .m4a / .ogg / .aac files)
├── videoloop/              # ← put your background here (video OR image)
│   └── (add one .mp4 looping clip, or a .jpg / .png still image)
└── output/                 # finished videos appear here (auto-created)
```

---

## Quick start

### Mac — double-click

1. Clone or download this repo
2. Drop your audio files into `tunes/`
3. Drop your looping video clip into `videoloop/`
4. Open `Make Videos.command` in a text editor and update the `--video-loop` path if your clip has a different name (see note below)
5. Double-click `Make Videos.command` — a Terminal window opens and encodes everything

> **Note:** The script defaults to looking for `videoloop/goldfat looping.mp4`.
> If your clip is named differently, either rename it to match, or pass `--video-loop path/to/yourclip.mp4` on the command line (see below).

### Command line (Mac / Linux / Windows)

```bash
# basic — uses defaults (tunes/, videoloop/goldfat looping.mp4, output/)
python3 make_videos.py

# specify your own paths
python3 make_videos.py \
  --audio-folder /path/to/audio \
  --video-loop   /path/to/loop.mp4 \
  --output       /path/to/output

# skip files already encoded (safe to re-run)
python3 make_videos.py --skip-existing

# preview commands without encoding
python3 make_videos.py --dry-run
```

---

## CLI options

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--audio-folder` | `-a` | `./tunes` | Folder containing audio files |
| `--background` | `-v` | `./videoloop/goldfat looping.mp4` | Looping video clip **or** still image (`.jpg`, `.png`, etc.) |
| `--output` | `-o` | `./output` | Output folder |
| `--preset` | | `slow` | x264 preset (`ultrafast` → `veryslow`). Slower = smaller file |
| `--crf` | | `18` | Quality 0–51, lower = better (18 is near-lossless) |
| `--audio-bitrate` | | `192k` | AAC audio bitrate |
| `--skip-existing` | | off | Skip tracks that already have an output file |
| `--dry-run` | | off | Print ffmpeg commands without running them |

---

## Supported audio formats

`.mp3` `.wav` `.flac` `.m4a` `.ogg` `.aac`

---

## Output

Each audio file produces a `1920×1080` H.264 / AAC MP4 optimised for YouTube (`-movflags +faststart`). The output filename matches the audio filename with a `.mp4` extension.
