"""Fail-closed, on-demand compute planning for Mina-Video.

This module selects a compute profile but does not provision hardware. A provider is
not enabled until a real adapter, quota verification, artifact verification, and tests
are registered. CPU remains the safe default. No provider can incur paid usage here.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Mapping, NamedTuple

_AUTH_SPEC = importlib.util.spec_from_file_location(
    "mina_gpu_authorization_contract", Path(__file__).with_name("gpu_authorization_contract.py")
)
if _AUTH_SPEC is None or _AUTH_SPEC.loader is None:
    raise ImportError("GPU authorization contract is unavailable")
_AUTH_MODULE = importlib.util.module_from_spec(_AUTH_SPEC)
sys.modules[_AUTH_SPEC.name] = _AUTH_MODULE
_AUTH_SPEC.loader.exec_module(_AUTH_MODULE)
parse_gpu_authorization = _AUTH_MODULE.parse_gpu_authorization

GPU_EXPERIMENTAL_ENV = "MINA_GPU_EXPERIMENTAL_ENABLED"
GPU_PROVIDER_ENV = "MINA_GPU_PROVIDER"
GPU_MAX_COST_ENV = "MINA_GPU_MAX_COST_USD"
SUPPORTED_TASKS = frozenset({
    "video.render", "video.generate", "image.generate", "image.process",
    "audio.tts", "audio.process", "music.generate", "music.process",
    "captions.render", "thumbnail.render",
})

class ComputePlan(NamedTuple):
    task: str
    selected_device: str
    provider: str
    status: str
    reason: str
    max_cost_usd: float = 0.0

GPU_PROFILES: Mapping[str, str] = {
    "image.generate": "pytorch-inference",
    "video.generate": "pytorch-inference",
    "audio.tts": "model-inference",
    "music.generate": "pytorch-inference",
}
CPU_PROFILES: Mapping[str, str] = {
    "video.render": "ffmpeg-cpu",
    "image.process": "cpu-image-processing",
    "audio.process": "cpu-audio-processing",
    "music.process": "cpu-audio-processing",
    "captions.render": "cpu-caption-rendering",
    "thumbnail.render": "cpu-thumbnail-rendering",
}

def _enabled(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}

def _zero_budget(value: str | None) -> bool:
    if value is None or not value.strip():
        return False
    try:
        return float(value) == 0.0
    except (TypeError, ValueError):
        return False

def plan_compute(
    task: str,
    environ: Mapping[str, str] | None = None,
    authorization: Mapping[str, object] | None = None,
) -> ComputePlan:
    """Return a deterministic plan; never provisions or dispatches work.

    The authorization payload must originate from trusted Factory orchestration.
    Schema validation alone does not authenticate its source.
    """
    env = environ or {}
    if task not in SUPPORTED_TASKS:
        raise ValueError(f"unsupported media task: {task}")
    if task in CPU_PROFILES:
        return ComputePlan(task, "cpu", "local", "READY", CPU_PROFILES[task])
    if not _enabled(env.get(GPU_EXPERIMENTAL_ENV)):
        return ComputePlan(task, "cpu", "local", "GPU_DISABLED", "experimental GPU gate is off")
    if not _zero_budget(env.get(GPU_MAX_COST_ENV)):
        return ComputePlan(task, "cpu", "local", "SAFE_HOLD", "non-zero or invalid cost budget is forbidden")
    provider = (env.get(GPU_PROVIDER_ENV) or "").strip().lower()
    if provider != "huggingface_zerogpu":
        return ComputePlan(task, "cpu", "local", "GPU_UNAVAILABLE", "no verified free GPU provider is configured")
    required = (
        "MINA_GPU_WORKER_URL", "MINA_GPU_ALLOWED_HOSTS",
        "MINA_GPU_FREE_QUOTA_REMAINING_SECONDS", "MINA_GPU_PROVIDER_VERIFIED",
    )
    missing = [key for key in required if not (env.get(key) or "").strip()]
    if missing:
        return ComputePlan(task, "cpu", "local", "GPU_UNAVAILABLE", "missing provider verification/config: " + ", ".join(missing))
    if not _enabled(env.get("MINA_GPU_PROVIDER_VERIFIED")):
        return ComputePlan(task, "cpu", "local", "GPU_UNAVAILABLE", "provider has not passed verification")
    try:
        quota = int(env["MINA_GPU_FREE_QUOTA_REMAINING_SECONDS"])
    except (TypeError, ValueError):
        return ComputePlan(task, "cpu", "local", "SAFE_HOLD", "free GPU quota is invalid")
    if quota <= 0:
        return ComputePlan(task, "cpu", "local", "GPU_QUOTA_EXHAUSTED", "no verified free GPU quota remains")
    if authorization is None:
        return ComputePlan(task, "cpu", "local", "GPU_NOT_APPROVED", "Factory authorization record is absent")
    try:
        auth = parse_gpu_authorization(authorization)
    except (TypeError, ValueError) as exc:
        return ComputePlan(task, "cpu", "local", "SAFE_HOLD", f"Factory authorization record is invalid: {exc}")
    if auth.task != task:
        return ComputePlan(task, "cpu", "local", "GPU_AUTH_SCOPE_MISMATCH", "Factory authorization does not match the requested task")
    if not auth.factory_approved:
        return ComputePlan(task, "cpu", "local", "GPU_NOT_APPROVED", "Factory/company approval is absent")
    if not auth.production_required:
        return ComputePlan(task, "cpu", "local", "GPU_NOT_REQUIRED", "production has not declared GPU necessary for this task")
    return ComputePlan(task, "cpu", "local", "GPU_ADAPTER_NOT_IMPLEMENTED", "provider execution adapter is not implemented; no dispatch performed")

def provider_capability_report() -> dict[str, object]:
    return {
        "schema": "mina-video-gpu-provider-report/v1",
        "on_demand_only": True,
        "max_cost_usd": 0,
        "default_device": "cpu",
        "registered_providers": [],
        "candidate_provider": "huggingface_zerogpu",
        "candidate_status": "DISCOVERED",
        "dispatch_enabled": False,
        "reason": "No owned ZeroGPU Space, live free-quota check, or artifact-return adapter has been verified.",
    }
