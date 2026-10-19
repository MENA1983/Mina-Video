import hashlib
import importlib.util
import json
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "video-runner" / "validate_gpu_authorization_event.py"
SPEC = importlib.util.spec_from_file_location("mina_gpu_authorization_event_validator", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


def authorization():
    return {
        "schema": "factory-gpu-authorization/v1",
        "job_id": "job-1",
        "task": "image.generate",
        "factory_approved": True,
        "factory_decision_ref": "factory:gpu-approval:job-1:image.generate",
        "production_required": True,
        "production_request_ref": "production:request:job-1:image.generate",
        "max_cost_usd": 0.0,
        "on_demand_only": True,
    }


def event_payload(auth=None):
    record = auth or authorization()
    digest = hashlib.sha256(module.canonical_authorization_bytes(record)).hexdigest()
    return {
        "schema": "factory-gpu-authorization-dispatch/v1",
        "authorization": record,
        "authorization_sha256": digest,
    }


def test_valid_event_is_verified_without_starting_execution():
    result = module.validate_authorization_event(event_payload())
    assert result["job_id"] == "job-1"
    assert result["task"] == "image.generate"
    assert result["execution"] == "NOT_STARTED"


def test_digest_mismatch_is_rejected():
    payload = event_payload()
    payload["authorization_sha256"] = "0" * 64
    try:
        module.validate_authorization_event(payload)
    except ValueError as exc:
        assert "digest mismatch" in str(exc)
    else:
        raise AssertionError("digest mismatch must fail closed")


def test_paid_scope_and_wrong_schema_are_rejected():
    paid = authorization()
    paid["max_cost_usd"] = 1
    try:
        module.validate_authorization_event(event_payload(paid))
    except ValueError:
        pass
    else:
        raise AssertionError("paid authorization must be rejected")
    payload = event_payload()
    payload["schema"] = "external-video/v1"
    try:
        module.validate_authorization_event(payload)
    except ValueError:
        pass
    else:
        raise AssertionError("wrong event schema must be rejected")


def test_unknown_fields_are_rejected():
    payload = event_payload()
    payload["extra"] = "no"
    try:
        module.validate_authorization_event(payload)
    except ValueError:
        pass
    else:
        raise AssertionError("unknown fields must be rejected")
