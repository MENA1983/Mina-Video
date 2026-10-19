import importlib.util
import sys
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "video-runner" / "gpu_authorization_contract.py"
SPEC = importlib.util.spec_from_file_location("mina_test_gpu_authorization_contract", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


def valid_payload():
    return {
        "schema": "factory-gpu-authorization/v1",
        "job_id": "gpu-job-1",
        "task": "image.generate",
        "factory_approved": True,
        "factory_decision_ref": "factory:decision:42",
        "production_required": True,
        "production_request_ref": "production:request:9",
        "max_cost_usd": 0.0,
        "on_demand_only": True,
    }


def test_valid_factory_authorization_requires_both_decisions():
    parsed = module.parse_gpu_authorization(valid_payload())
    assert parsed.eligible is True


def test_missing_company_approval_is_not_eligible():
    payload = valid_payload()
    payload["factory_approved"] = False
    payload["factory_decision_ref"] = ""
    assert module.parse_gpu_authorization(payload).eligible is False


def test_missing_production_need_is_not_eligible():
    payload = valid_payload()
    payload["production_required"] = False
    payload["production_request_ref"] = ""
    assert module.parse_gpu_authorization(payload).eligible is False


def test_paid_or_scheduled_scope_is_rejected():
    payload = valid_payload()
    payload["max_cost_usd"] = 1
    try:
        module.parse_gpu_authorization(payload)
    except ValueError:
        pass
    else:
        raise AssertionError("paid GPU authorization must be rejected")
    payload = valid_payload()
    payload["on_demand_only"] = False
    try:
        module.parse_gpu_authorization(payload)
    except ValueError:
        pass
    else:
        raise AssertionError("non-on-demand authorization must be rejected")


def test_unknown_fields_and_wrong_schema_are_rejected():
    payload = valid_payload()
    payload["provider"] = "huggingface_zerogpu"
    try:
        module.parse_gpu_authorization(payload)
    except ValueError:
        pass
    else:
        raise AssertionError("unknown fields must be rejected")
    payload = valid_payload()
    payload["schema"] = "external-video/v1"
    try:
        module.parse_gpu_authorization(payload)
    except ValueError:
        pass
    else:
        raise AssertionError("wrong schema must be rejected")
