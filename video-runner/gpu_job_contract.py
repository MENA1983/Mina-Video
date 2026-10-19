"""Pure validation helpers for externally returned media jobs.

This module deliberately performs no network calls and never retries a remote job.
A caller must persist the job ID and reconcile unknown outcomes before any retry.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import re

_SHA256 = re.compile(r"^[0-9a-f]{64}$")


class UnsafeJobResult(ValueError):
    """The returned job evidence is incomplete or fails integrity checks."""


@dataclass(frozen=True)
class VerifiedArtifact:
    job_id: str
    input_sha256: str
    output_sha256: str
    output_size_bytes: int
    provider: str
    execution_evidence: str


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_artifact(
    *,
    job_id: str,
    expected_job_id: str,
    input_sha256: str,
    expected_input_sha256: str,
    output: bytes,
    claimed_output_sha256: str,
    provider: str,
    execution_evidence: str,
    max_output_bytes: int,
) -> VerifiedArtifact:
    """Validate identity, bounded output, content digest, and provenance evidence."""
    if not job_id or job_id != expected_job_id:
        raise UnsafeJobResult("job identity missing or mismatched")
    if not _SHA256.fullmatch(input_sha256) or input_sha256 != expected_input_sha256:
        raise UnsafeJobResult("input SHA-256 missing or mismatched")
    if not isinstance(output, bytes) or not output:
        raise UnsafeJobResult("output is empty or not bytes")
    if max_output_bytes <= 0 or len(output) > max_output_bytes:
        raise UnsafeJobResult("output exceeds configured size limit")
    actual = sha256_hex(output)
    if not _SHA256.fullmatch(claimed_output_sha256) or claimed_output_sha256 != actual:
        raise UnsafeJobResult("output SHA-256 missing or mismatched")
    if not provider.strip() or not execution_evidence.strip():
        raise UnsafeJobResult("provider provenance or execution evidence missing")
    return VerifiedArtifact(
        job_id=job_id,
        input_sha256=input_sha256,
        output_sha256=actual,
        output_size_bytes=len(output),
        provider=provider,
        execution_evidence=execution_evidence,
    )


def retry_decision(outcome: str) -> str:
    """Return safe handling for a dispatch outcome; unknown outcomes are never retried."""
    normalized = outcome.strip().lower()
    if normalized == "not_sent":
        return "SAFE_TO_SUBMIT"
    if normalized == "completed":
        return "RECONCILE_RESULT"
    if normalized in {"timeout", "unknown", "connection_lost"}:
        return "HOLD_AND_RECONCILE"
    if normalized in {"rejected", "failed_confirmed"}:
        return "REVIEW_BEFORE_RETRY"
    raise ValueError(f"unknown dispatch outcome: {outcome}")
