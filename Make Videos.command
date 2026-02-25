#!/bin/zsh
# Double-click this file in Finder to batch-encode all tunes → output/
# New tracks: just drop WAV/MP3 files into the tunes/ folder and run again.
# Already-encoded videos are skipped automatically.

cd "$(dirname "$0")"

echo "========================================="
echo "  YouTube Video Batch Encoder"
echo "========================================="
echo ""

python3 make_videos.py --preset slow --skip-existing

echo ""
echo "All done! Press any key to close."
read -k 1
