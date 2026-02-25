#!/usr/bin/env python3
"""
Batch YouTube video creator
Uses a looping video clip OR a still image as the background for the full
duration of each audio file, then muxes them into a YouTube-ready 1080p MP4.

Usage:
    python3 make_videos.py [options]

Defaults (auto-detected from this repo layout):
    Audio folder : ./tunes/
    Background   : ./videoloop/goldfat looping.mp4
    Output folder: ./output/
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

AUDIO_EXTENSIONS = {".mp3", ".wav", ".flac", ".m4a", ".ogg", ".aac"}
IMAGE_EXTENSIONS  = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}

# ── Defaults (relative to this script's directory) ───────────────────────────
SCRIPT_DIR = Path(__file__).parent
DEFAULT_AUDIO_FOLDER  = SCRIPT_DIR / "tunes"
DEFAULT_BACKGROUND    = SCRIPT_DIR / "videoloop" / "goldfat looping.mp4"
DEFAULT_OUTPUT_FOLDER = SCRIPT_DIR / "output"


def get_duration(path: str) -> float:
    """Return media duration in seconds via ffprobe."""
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            path,
        ],
        capture_output=True, text=True, check=True,
    )
    return float(result.stdout.strip())


def build_ffmpeg_cmd(
    background: str,
    audio_path: str,
    output_path: str,
    duration: float,
    preset: str,
    crf: int,
    audio_bitrate: str,
) -> list[str]:
    is_image = Path(background).suffix.lower() in IMAGE_EXTENSIONS
    bg_input = ["-loop", "1", "-i", background] if is_image else ["-stream_loop", "-1", "-i", background]
    return [
        "ffmpeg", "-y",
        # ── Inputs ──────────────────────────────────────────────────────────
        *bg_input,              # input 0: still image or looping video
        "-i", audio_path,       # input 1: audio
        # ── Stream selection ────────────────────────────────────────────────
        "-map", "0:v:0",        # video from background
        "-map", "1:a:0",        # audio from audio file
        # ── Duration: stop when audio ends ──────────────────────────────────
        "-t", str(duration),
        # ── Video codec (YouTube-recommended H.264) ──────────────────────────
        "-c:v", "libx264",
        "-preset", preset,
        "-crf", str(crf),
        "-pix_fmt", "yuv420p",  # broad player compatibility
        # Scale to 1920×1080, letterbox/pillarbox if source differs
        "-vf", (
            "scale=1920:1080:force_original_aspect_ratio=decrease,"
            "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black"
        ),
        # ── Audio codec ──────────────────────────────────────────────────────
        "-c:a", "aac",
        "-b:a", audio_bitrate,
        "-ar", "44100",
        # ── Container ────────────────────────────────────────────────────────
        "-movflags", "+faststart",  # puts metadata at front → faster YouTube processing
        output_path,
    ]


def process_file(
    background: str,
    audio_path: Path,
    output_folder: Path,
    preset: str,
    crf: int,
    audio_bitrate: str,
    dry_run: bool,
    skip_existing: bool,
) -> bool:
    output_path = output_folder / (audio_path.stem + ".mp4")

    if skip_existing and output_path.exists():
        print(f"  Skipping (already exists): {output_path.name}")
        return True

    try:
        duration = get_duration(str(audio_path))
    except (subprocess.CalledProcessError, ValueError) as e:
        print(f"  ERROR reading duration: {e}")
        return False

    cmd = build_ffmpeg_cmd(
        background, str(audio_path), str(output_path),
        duration, preset, crf, audio_bitrate,
    )

    print(f"  Duration : {duration:.1f}s")
    print(f"  Output   : {output_path}")

    if dry_run:
        print(f"  [DRY RUN] {' '.join(cmd)}\n")
        return True

    try:
        subprocess.run(cmd, check=True)
        size_mb = output_path.stat().st_size / 1_048_576
        print(f"  Done — {size_mb:.1f} MB\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ERROR: ffmpeg exited with code {e.returncode}\n")
        return False


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--audio-folder", "-a", default=str(DEFAULT_AUDIO_FOLDER),
        help=f"Folder of audio files (default: {DEFAULT_AUDIO_FOLDER})",
    )
    parser.add_argument(
        "--background", "-v", default=str(DEFAULT_BACKGROUND),
        help=f"Looping video clip or still image (.jpg/.png/etc) (default: {DEFAULT_BACKGROUND})",
    )
    parser.add_argument(
        "--output", "-o", default=str(DEFAULT_OUTPUT_FOLDER),
        help=f"Output folder (default: {DEFAULT_OUTPUT_FOLDER})",
    )
    parser.add_argument(
        "--preset", default="slow",
        choices=["ultrafast","superfast","veryfast","faster","fast",
                 "medium","slow","slower","veryslow"],
        help="x264 encoding preset — slower = smaller file (default: slow)",
    )
    parser.add_argument(
        "--crf", type=int, default=18,
        help="Constant Rate Factor 0–51; lower = better quality (default: 18)",
    )
    parser.add_argument(
        "--audio-bitrate", default="192k",
        help="AAC audio bitrate (default: 192k)",
    )
    parser.add_argument(
        "--skip-existing", action="store_true",
        help="Skip output files that already exist",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print ffmpeg commands without running them",
    )
    args = parser.parse_args()

    audio_folder  = Path(args.audio_folder)
    background    = args.background
    output_folder = Path(args.output)

    # ── Validate ──────────────────────────────────────────────────────────────
    if not audio_folder.is_dir():
        sys.exit(f"ERROR: Audio folder not found: {audio_folder}")
    if not Path(background).is_file():
        sys.exit(f"ERROR: Background file not found: {background}")

    audio_files = sorted(
        f for f in audio_folder.iterdir()
        if f.suffix.lower() in AUDIO_EXTENSIONS
    )
    if not audio_files:
        sys.exit(f"ERROR: No audio files found in {audio_folder}")

    output_folder.mkdir(parents=True, exist_ok=True)

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"Audio folder : {audio_folder}")
    print(f"Background   : {background}")
    print(f"Output folder: {output_folder}")
    print(f"Tracks found : {len(audio_files)}")
    print(f"Preset/CRF   : {args.preset} / {args.crf}")
    print("─" * 60)

    succeeded, failed = 0, []

    for i, audio_file in enumerate(audio_files, 1):
        print(f"[{i}/{len(audio_files)}] {audio_file.name}")
        ok = process_file(
            background, audio_file, output_folder,
            args.preset, args.crf, args.audio_bitrate,
            args.dry_run, args.skip_existing,
        )
        if ok:
            succeeded += 1
        else:
            failed.append(audio_file.name)

    # ── Report ────────────────────────────────────────────────────────────────
    print("═" * 60)
    print(f"Done: {succeeded}/{len(audio_files)} succeeded.")
    if failed:
        print("Failed:")
        for name in failed:
            print(f"  • {name}")


if __name__ == "__main__":
    main()
