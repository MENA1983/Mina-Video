import importlib.util
import os
from pathlib import Path
from unittest.mock import patch


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
        with patch.object(module.socket, "getaddrinfo", return_value=[(2, 1, 6, "", ("93.184.216.34", 443))]):
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


def test_production_asset_rejects_private_dns_target():
    previous = os.environ.get(module.ALLOWED_HOSTS_ENV)
    os.environ[module.ALLOWED_HOSTS_ENV] = "approved.example"
    try:
        with patch.object(module.socket, "getaddrinfo", return_value=[(2, 1, 6, "", ("127.0.0.1", 443))]):
            try:
                module.approved_asset_url("https://approved.example/a.jpg", "image")
            except module.RenderError as exc:
                assert "non-public IP" in str(exc)
                return
            raise AssertionError("private DNS target must be rejected")
    finally:
        if previous is None:
            os.environ.pop(module.ALLOWED_HOSTS_ENV, None)
        else:
            os.environ[module.ALLOWED_HOSTS_ENV] = previous


def test_production_asset_rejects_link_local_dns_target():
    previous = os.environ.get(module.ALLOWED_HOSTS_ENV)
    os.environ[module.ALLOWED_HOSTS_ENV] = "approved.example"
    try:
        with patch.object(module.socket, "getaddrinfo", return_value=[(10, 1, 6, "", ("169.254.1.1", 443))]):
            try:
                module.approved_asset_url("https://approved.example/a.jpg", "image")
            except module.RenderError as exc:
                assert "non-public IP" in str(exc)
                return
            raise AssertionError("link-local DNS target must be rejected")
    finally:
        if previous is None:
            os.environ.pop(module.ALLOWED_HOSTS_ENV, None)
        else:
            os.environ[module.ALLOWED_HOSTS_ENV] = previous


def test_allowlist_canonicalizes_trailing_dot_and_default_port():
    previous = os.environ.get(module.ALLOWED_HOSTS_ENV)
    os.environ[module.ALLOWED_HOSTS_ENV] = "Example.COM."
    try:
        with patch.object(module.socket, "getaddrinfo", return_value=[(2, 1, 6, "", ("93.184.216.34", 443))]):
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
