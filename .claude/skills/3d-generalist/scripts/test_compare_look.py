"""Tests for compare_look.py with synthetic ffmpeg frames.

Run: uv run --no-project --with pytest --with numpy pytest scripts/test_compare_look.py
"""

import pathlib
import shutil
import subprocess
import sys

import pytest

SCRIPT = pathlib.Path(__file__).resolve().parent / "compare_look.py"

pytestmark = pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg is not installed")


def make_image(path, color, eq_filter=None):
    command = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c={color}:s=320x180", "-frames:v", "1"]
    if eq_filter:
        command += ["-vf", eq_filter]
    command.append(str(path))
    subprocess.run(command, check=True, capture_output=True)


def make_video(path, color):
    command = [
        "ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c={color}:s=320x180:r=10:d=3",
        "-pix_fmt", "yuv420p", str(path),
    ]
    subprocess.run(command, check=True, capture_output=True)


def run_compare(*arguments):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, arguments)], capture_output=True, text=True, encoding="utf-8"
    )


@pytest.fixture
def style_frame(tmp_path):
    path = tmp_path / "style.png"
    make_image(path, "0xC86E3C")
    return path


def test_same_look_passes(tmp_path, style_frame):
    same = tmp_path / "same.png"
    make_image(same, "0xC86E3C")
    result = run_compare("--style", style_frame, same)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "1 of 1 frames inside the look band" in result.stdout


def test_darker_greyer_blue_shifted_frame_fails(tmp_path, style_frame):
    drifted = tmp_path / "drifted.png"
    make_image(drifted, "0x303A4A")
    result = run_compare("--style", style_frame, drifted)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "darker" in result.stdout
    assert "greyer" in result.stdout
    assert "colour cast differs" in result.stdout


def test_video_sampled_at_one_fps_passes(tmp_path, style_frame):
    video = tmp_path / "shot.mp4"
    make_video(video, "0xC86E3C")
    result = run_compare("--style", style_frame, video, "--fps", "1")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "@ 0.0 s" in result.stdout
    assert "3 of 3 frames inside the look band" in result.stdout


def test_missing_file_exits_two(tmp_path, style_frame):
    result = run_compare("--style", style_frame, tmp_path / "does-not-exist.png")
    assert result.returncode == 2
    assert "cannot read" in result.stdout
