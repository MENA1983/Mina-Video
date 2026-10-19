import hashlib
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("mina_gpu_job_contract", ROOT / "video-runner" / "gpu_job_contract.py")
contract = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(contract)


def valid_args():
    data = b"small non-sensitive test artifact"
    digest = hashlib.sha256(data).hexdigest()
    input_digest = hashlib.sha256(b"test input").hexdigest()
    return dict(
        job_id="job-123",
        expected_job_id="job-123",
        input_sha256=input_digest,
        expected_input_sha256=input_digest,
        output=data,
        claimed_output_sha256=digest,
        provider="owned-test-worker",
        execution_evidence="test-run-001",
        max_output_bytes=1024,
    )


def test_valid_artifact_requires_job_identity_digest_and_provenance():
    result = contract.validate_artifact(**valid_args())
    assert result.job_id == "job-123"
    assert result.output_sha256 == hashlib.sha256(valid_args()["output"]).hexdigest()


def test_wrong_job_id_is_rejected():
    args = valid_args()
    args["job_id"] = "other-job"
    try:
        contract.validate_artifact(**args)
    except contract.UnsafeJobResult as exc:
        assert "job identity" in str(exc)
    else:
        raise AssertionError("mismatched job identity must fail")


def test_input_sha256_mismatch_is_rejected():
    args = valid_args()
    args["input_sha256"] = "0" * 64
    try:
        contract.validate_artifact(**args)
    except contract.UnsafeJobResult as exc:
        assert "input SHA-256" in str(exc)
    else:
        raise AssertionError("mismatched input digest must fail")


def test_output_sha256_mismatch_is_rejected():
    args = valid_args()
    args["claimed_output_sha256"] = "0" * 64
    try:
        contract.validate_artifact(**args)
    except contract.UnsafeJobResult as exc:
        assert "output SHA-256" in str(exc)
    else:
        raise AssertionError("mismatched output digest must fail")


def test_unknown_or_malformed_result_is_rejected():
    args = valid_args()
    args["output"] = b""
    try:
        contract.validate_artifact(**args)
    except contract.UnsafeJobResult as exc:
        assert "output is empty" in str(exc)
    else:
        raise AssertionError("empty output must fail")


def test_output_size_limit_is_enforced():
    args = valid_args()
    args["max_output_bytes"] = 2
    try:
        contract.validate_artifact(**args)
    except contract.UnsafeJobResult as exc:
        assert "size limit" in str(exc)
    else:
        raise AssertionError("oversized output must fail")


def test_missing_execution_evidence_is_rejected():
    args = valid_args()
    args["execution_evidence"] = ""
    try:
        contract.validate_artifact(**args)
    except contract.UnsafeJobResult as exc:
        assert "provenance" in str(exc)
    else:
        raise AssertionError("missing evidence must fail")


def test_timeout_unknown_outcome_never_blindly_retries():
    for outcome in ("timeout", "unknown", "connection_lost"):
        assert contract.retry_decision(outcome) == "HOLD_AND_RECONCILE"


def test_confirmed_not_sent_is_only_automatic_submit_case():
    assert contract.retry_decision("not_sent") == "SAFE_TO_SUBMIT"
    assert contract.retry_decision("completed") == "RECONCILE_RESULT"
    assert contract.retry_decision("failed_confirmed") == "REVIEW_BEFORE_RETRY"


def test_unknown_outcome_value_fails_closed():
    try:
        contract.retry_decision("maybe")
    except ValueError as exc:
        assert "unknown dispatch outcome" in str(exc)
    else:
        raise AssertionError("unrecognized outcomes must fail")
