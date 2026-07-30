"""
scripts/create_dummy_media.py

Create dummy media files for stub providers.
Requires ffmpeg to be installed.
"""

import os
import subprocess
from pathlib import Path


def create_silent_wav(output_path: Path, duration: int = 5):
    """Create a silent WAV file using ffmpeg."""
    cmd = [
        "ffmpeg",
        "-f", "lavfi",
        "-i", "anullsrc=r=44100:cl=mono",
        "-t", str(duration),
        "-acodec", "pcm_s16le",
        str(output_path),
        "-y",  # Overwrite existing file
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"Created silent WAV: {output_path}")


def create_black_mp4(output_path: Path, duration: int = 5):
    """Create a black screen MP4 file using ffmpeg."""
    cmd = [
        "ffmpeg",
        "-f", "lavfi",
        "-i", f"color=c=black:s=1920x1080:d={duration}:r=30",
        "-c:v", "libx264",
        "-t", str(duration),
        "-pix_fmt", "yuv420p",
        str(output_path),
        "-y",  # Overwrite existing file
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"Created black MP4: {output_path}")


def main():
    """Create all dummy media files."""
    # Ensure fixtures directory exists
    fixtures_dir = Path(__file__).parent.parent / "fixtures" / "stubs"
    fixtures_dir.mkdir(parents=True, exist_ok=True)

    # Create silent WAV
    wav_path = fixtures_dir / "silent_5s.wav"
    if not wav_path.exists():
        create_silent_wav(wav_path, duration=5)
    else:
        print(f"WAV already exists: {wav_path}")

    # Create black MP4
    mp4_path = fixtures_dir / "black_5s.mp4"
    if not mp4_path.exists():
        create_black_mp4(mp4_path, duration=5)
    else:
        print(f"MP4 already exists: {mp4_path}")

    print("\nDummy media files created successfully!")
    print(f"  - {wav_path} ({wav_path.stat().st_size} bytes)")
    print(f"  - {mp4_path} ({mp4_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()