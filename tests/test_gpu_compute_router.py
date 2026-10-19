import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("mina_gpu_router", ROOT / "video-runner" / "gpu_compute_router.py")
gpu = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(gpu)


def test_cpu_is_default_and_gpu_is_opt_in():
    plan = gpu.plan_compute("image.generate", {})
    assert plan.selected_device == "cpu"
    assert plan.status == "GPU_DISABLED"


def test_ffmpeg_render_stays_cpu_even_when_gpu_gate_enabled():
    plan = gpu.plan_compute("video.render", {gpu.GPU_EXPERIMENTAL_ENV: "true"})
    assert plan.selected_device == "cpu"
    assert plan.reason == "ffmpeg-cpu"


def test_unknown_task_fails_closed():
    try:
        gpu.plan_compute("publish.youtube", {})
    except ValueError as exc:
        assert "unsupported" in str(exc)
    else:
        raise AssertionError("unknown task must be rejected")


def test_paid_or_invalid_budget_never_selects_gpu():
    for budget in ("1", "-1", "not-a-number"):
        plan = gpu.plan_compute("image.generate", {
            gpu.GPU_EXPERIMENTAL_ENV: "true", gpu.GPU_PROVIDER_ENV: "huggingface_zerogpu",
            gpu.GPU_MAX_COST_ENV: budget,
        })
        assert plan.selected_device == "cpu"
        assert plan.status == "SAFE_HOLD"


def test_provider_name_alone_never_dispatches():
    plan = gpu.plan_compute("image.generate", {
        gpu.GPU_EXPERIMENTAL_ENV: "true", gpu.GPU_PROVIDER_ENV: "huggingface_zerogpu",
        gpu.GPU_MAX_COST_ENV: "0",
    })
    assert plan.selected_device == "cpu"
    assert plan.status == "GPU_UNAVAILABLE"


def verified_env():
    return {
        gpu.GPU_EXPERIMENTAL_ENV: "true",
        gpu.GPU_PROVIDER_ENV: "huggingface_zerogpu",
        gpu.GPU_MAX_COST_ENV: "0",
        "MINA_GPU_WORKER_URL": "https://example.hf.space/api/predict",
        "MINA_GPU_ALLOWED_HOSTS": "example.hf.space",
        "MINA_GPU_FREE_QUOTA_REMAINING_SECONDS": "300",
        "MINA_GPU_PROVIDER_VERIFIED": "true",
    }


def authorization(**overrides):
    payload = {
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
    payload.update(overrides)
    return payload


def test_missing_quota_or_verification_falls_back_to_cpu():
    env = verified_env()
    env.pop("MINA_GPU_PROVIDER_VERIFIED")
    plan = gpu.plan_compute("image.generate", env, authorization(), job_id="gpu-job-1")
    assert plan.selected_device == "cpu"
    assert plan.status == "GPU_UNAVAILABLE"


def test_exhausted_free_quota_falls_back_to_cpu():
    env = verified_env()
    env["MINA_GPU_FREE_QUOTA_REMAINING_SECONDS"] = "0"
    plan = gpu.plan_compute("image.generate", env, authorization(), job_id="gpu-job-1")
    assert plan.selected_device == "cpu"
    assert plan.status == "GPU_QUOTA_EXHAUSTED"


def test_factory_approval_record_is_required():
    plan = gpu.plan_compute("image.generate", verified_env())
    assert plan.selected_device == "cpu"
    assert plan.status == "GPU_NOT_APPROVED"


def test_missing_factory_approval_falls_back_to_cpu():
    payload = authorization(factory_approved=False, factory_decision_ref="")
    plan = gpu.plan_compute("image.generate", verified_env(), payload, job_id="gpu-job-1")
    assert plan.selected_device == "cpu"
    assert plan.status == "GPU_NOT_APPROVED"


def test_missing_production_need_falls_back_to_cpu():
    payload = authorization(production_required=False, production_request_ref="")
    plan = gpu.plan_compute("image.generate", verified_env(), payload, job_id="gpu-job-1")
    assert plan.selected_device == "cpu"
    assert plan.status == "GPU_NOT_REQUIRED"


def test_job_or_task_mismatch_in_factory_record_fails_closed():
    plan = gpu.plan_compute("video.generate", verified_env(), authorization(), job_id="gpu-job-1")
    assert plan.selected_device == "cpu"
    assert plan.status == "GPU_AUTH_SCOPE_MISMATCH"
    plan = gpu.plan_compute("image.generate", verified_env(), authorization(), job_id="different-job")
    assert plan.selected_device == "cpu"
    assert plan.status == "GPU_AUTH_SCOPE_MISMATCH"


def test_missing_job_id_fails_closed():
    plan = gpu.plan_compute("image.generate", verified_env(), authorization())
    assert plan.selected_device == "cpu"
    assert plan.status == "GPU_AUTH_SCOPE_MISMATCH"


def test_paid_or_malformed_authorization_fails_closed():
    for changed in (
        authorization(max_cost_usd=0.01),
        authorization(on_demand_only=False),
        authorization(provider="unexpected"),
        authorization(schema="external-video/v1"),
    ):
        plan = gpu.plan_compute("image.generate", verified_env(), changed, job_id="gpu-job-1")
        assert plan.selected_device == "cpu"
        assert plan.status == "SAFE_HOLD"


def test_valid_factory_and_production_decision_still_cannot_dispatch_without_adapter():
    plan = gpu.plan_compute("image.generate", verified_env(), authorization(), job_id="gpu-job-1")
    assert plan.selected_device == "cpu"
    assert plan.status == "GPU_ADAPTER_NOT_IMPLEMENTED"


def test_report_makes_non_activation_explicit():
    report = gpu.provider_capability_report()
    assert report["dispatch_enabled"] is False
    assert report["max_cost_usd"] == 0
    assert report["registered_providers"] == []
