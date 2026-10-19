"""Validate a Factory GPU authorization notification without executing GPU work."""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
from collections.abc import Mapping
from pathlib import Path
import importlib.util
import sys

_SPEC = importlib.util.spec_from_file_location(
    "mina_gpu_authorization_contract",
    Path(__file__).with_name("gpu_authorization_contract.py"),
)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError("GPU authorization contract is unavailable")
_MODULE = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _MODULE
_SPEC.loader.exec_module(_MODULE)
parse_gpu_authorization = _MODULE.parse_gpu_authorization

DISPATCH_SCHEMA = "factory-gpu-authorization-dispatch/v1"
_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")


def canonical_authorization_bytes(authorization: Mapping[str, object]) -> bytes:
    return json.dumps(
        dict(authorization), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def validate_authorization_event(client_payload: Mapping[str, object]) -> dict[str, str]:
    if not isinstance(client_payload, Mapping):
        raise ValueError("GPU authorization event payload must be an object")
    if set(client_payload) != {"schema", "authorization", "authorization_sha256"}:
        raise ValueError("GPU authorization event has unsupported or missing fields")
    if client_payload.get("schema") != DISPATCH_SCHEMA:
        raise ValueError("GPU authorization dispatch schema mismatch")
    authorization = client_payload.get("authorization")
    claimed_digest = client_payload.get("authorization_sha256")
    if not isinstance(authorization, Mapping):
        raise ValueError("GPU authorization record must be an object")
    if not isinstance(claimed_digest, str) or not _DIGEST_RE.fullmatch(claimed_digest):
        raise ValueError("GPU authorization digest is malformed")
    actual_digest = hashlib.sha256(canonical_authorization_bytes(authorization)).hexdigest()
    if not hmac.compare_digest(actual_digest, claimed_digest):
        raise ValueError("GPU authorization digest mismatch")
    parsed = parse_gpu_authorization(authorization)
    if not parsed.eligible:
        raise ValueError("GPU authorization is not eligible")
    return {
        "job_id": parsed.job_id,
        "task": parsed.task,
        "authorization_sha256": actual_digest,
        "execution": "NOT_STARTED",
    }


def main() -> int:
    raw = os.environ.get("MINA_GPU_AUTH_CLIENT_PAYLOAD", "")
    if not raw:
        raise ValueError("MINA_GPU_AUTH_CLIENT_PAYLOAD is required")
    client_payload = json.loads(raw)
    result = validate_authorization_event(client_payload)
    # Only constrained identifiers are printed. No credentials, content, or payload is logged.
    print(
        "GPU_AUTHORIZATION_VALIDATED "
        f"job_id={result['job_id']} task={result['task']} "
        f"sha256={result['authorization_sha256']} execution={result['execution']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
