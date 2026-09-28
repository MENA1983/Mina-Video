import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


class PublicMediaToolchainTests(unittest.TestCase):
    """Generate a tiny real MP4 + WAV path on public CI, with no secrets/providers."""

    def test_video_audio_and_motion_toolchain(self):
        for tool in ("ffmpeg", "ffprobe", "espeak-ng"):
            self.assertIsNotNone(shutil.which(tool), f"missing tool: {tool}")

        with tempfile.TemporaryDirectory(prefix="mina-public-media-test-") as tmp:
            root = Path(tmp)
            audio = root / "voice.wav"
            video = root / "motion.mp4"
            merged = root / "final.mp4"

            subprocess.run(
                ["espeak-ng", "-v", "en", "-s", "150", "-w", str(audio), "Mina Video public CI test"],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                [
                    "ffmpeg", "-y", "-f", "lavfi", "-i",
                    "testsrc=size=320x568:rate=24", "-t", "2",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", str(video),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                [
                    "ffmpeg", "-y", "-i", str(video), "-i", str(audio),
                    "-shortest", "-c:v", "copy", "-c:a", "aac", str(merged),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            probe = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=nw=1:nk=1", str(merged)],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertGreater(float(probe.stdout.strip()), 0.0)
            self.assertGreater(merged.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
