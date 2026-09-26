import importlib.util
import os
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


def test_production_asset_requires_allowlist():
    previous = os.environ.pop(module.ALLOWED_HOSTS_ENV, None)
    try:
        try:
            module.approved_asset_url("https://example.com/a.jpg", "image")
        except module.RenderError as exc:
            assert module.ALLOWED_HOSTS_ENV in str(exc)
            return
        raise AssertionError("missing production allowlist must fail closed")
    finally:
        if previous is not None:
            os.environ[module.ALLOWED_HOSTS_ENV] = previous


def test_production_asset_accepts_exact_allowlisted_host():
    previous = os.environ.get(module.ALLOWED_HOSTS_ENV)
    os.environ[module.ALLOWED_HOSTS_ENV] = "example.com"
    try:
        assert module.approved_asset_url("https://example.com/a.jpg", "image") == "https://example.com/a.jpg"
    finally:
        if previous is None:
            os.environ.pop(module.ALLOWED_HOSTS_ENV, None)
        else:
            os.environ[module.ALLOWED_HOSTS_ENV] = previous


def test_production_asset_rejects_unapproved_host():
    previous = os.environ.get(module.ALLOWED_HOSTS_ENV)
    os.environ[module.ALLOWED_HOSTS_ENV] = "approved.example"
    try:
        try:
            module.approved_asset_url("https://evil.example/a.jpg", "image")
        except module.RenderError:
            return
        raise AssertionError("unapproved host must be rejected")
    finally:
        if previous is None:
            os.environ.pop(module.ALLOWED_HOSTS_ENV, None)
        else:
            os.environ[module.ALLOWED_HOSTS_ENV] = previous


def test_allowlist_canonicalizes_trailing_dot_and_default_port():
    previous = os.environ.get(module.ALLOWED_HOSTS_ENV)
    os.environ[module.ALLOWED_HOSTS_ENV] = "Example.COM."
    try:
        assert module.approved_asset_url("https://example.com:443/a.jpg", "image") == "https://example.com:443/a.jpg"
    finally:
        if previous is None:
            os.environ.pop(module.ALLOWED_HOSTS_ENV, None)
        else:
            os.environ[module.ALLOWED_HOSTS_ENV] = previous


def test_redirect_limit_is_bounded():
    assert module.MAX_REDIRECTS == 5


def test_total_image_budget_is_bounded():
    assert module.MAX_TOTAL_IMAGE_BYTES <= 300 * 1024 * 1024
