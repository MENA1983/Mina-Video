import importlib.util
from pathlib import Path


RENDER = Path(__file__).resolve().parents[1] / "video-runner" / "render.py"
spec = importlib.util.spec_from_file_location("mina_render", RENDER)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_rejects_embedded_credentials():
    try:
        module.https_url("https://user:pass@example.com/a.jpg", "image")
    except module.RenderError:
        return
    raise AssertionError("embedded credentials must be rejected")


def test_accepts_https_without_credentials():
    assert module.https_url("https://example.com/a.jpg", "image") == "https://example.com/a.jpg"


def test_redirect_limit_is_bounded():
    assert module.MAX_REDIRECTS == 5


def test_total_image_budget_is_bounded():
    assert module.MAX_TOTAL_IMAGE_BYTES <= 300 * 1024 * 1024
