from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("renderer", ROOT / "video-runner" / "render.py")
renderer = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(renderer)


def test_run_times_out(monkeypatch):
    class Timeout:
        def __call__(self, *args, **kwargs):
            raise renderer.subprocess.TimeoutExpired(cmd=args[0], timeout=kwargs["timeout"])

    monkeypatch.setattr(renderer.subprocess, "run", Timeout())
    try:
        renderer.run(["ffmpeg", "-version"], timeout=1)
    except renderer.RenderError as exc:
        assert "timed out after 1s" in str(exc)
    else:
        raise AssertionError("timeout must fail closed")


def test_ffprobe_timeout_is_bounded(monkeypatch, tmp_path):
    def timeout(*args, **kwargs):
        assert kwargs["timeout"] == renderer.FFPROBE_TIMEOUT_SECONDS
        raise renderer.subprocess.TimeoutExpired(cmd=args[0], timeout=kwargs["timeout"])

    monkeypatch.setattr(renderer.subprocess, "run", timeout)
    try:
        renderer.duration(tmp_path / "missing.mp4")
    except renderer.RenderError as exc:
        assert "ffprobe timed out" in str(exc)
    else:
        raise AssertionError("ffprobe timeout must fail closed")
