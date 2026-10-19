"""Consumer-side validator for Factory GPU authorization v1.

Validation is not authentication. The caller must obtain this record from the
trusted Factory control plane over an authenticated, reviewed handoff.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Mapping

SCHEMA = "factory-gpu-authorization/v1"
_JOB_RE = re.compile(r"^[A-Za-z0-9._-]{1,80}$")
_REF_RE = re.compile(r"^[A-Za-z0-9._:/#-]{1,160}$")
GPU_CANDIDATE_TASKS = frozenset({"image.generate", "video.generate", "audio.tts", "music.generate"})
_ALLOWED_KEYS = frozenset({
    "schema", "job_id", "task", "factory_approved", "factory_decision_ref",
    "production_required", "production_request_ref", "max_cost_usd", "on_demand_only",
})


@dataclass(frozen=True)
class GpuAuthorization:
    job_id: str
    task: str
    factory_approved: bool
    production_required: bool

    @property
    def eligible(self) -> bool:
        return self.task in GPU_CANDIDATE_TASKS and self.factory_approved and self.production_required


def parse_gpu_authorization(payload: Mapping[str, object]) -> GpuAuthorization:
    if not isinstance(payload, Mapping):
        raise ValueError("GPU authorization must be an object")
    if set(payload) != _ALLOWED_KEYS:
        raise ValueError("GPU authorization keys do not match factory-gpu-authorization/v1")
    if payload.get("schema") != SCHEMA:
        raise ValueError("GPU authorization schema mismatch")
    job_id = payload.get("job_id")
    task = payload.get("task")
    approved = payload.get("factory_approved")
    production_required = payload.get("production_required")
    decision_ref = payload.get("factory_decision_ref")
    production_ref = payload.get("production_request_ref")
    cost = payload.get("max_cost_usd")
    on_demand = payload.get("on_demand_only")
    if not isinstance(job_id, str) or not _JOB_RE.fullmatch(job_id):
        raise ValueError("GPU authorization job_id is invalid")
    if not isinstance(task, str) or task not in GPU_CANDIDATE_TASKS:
        raise ValueError("GPU authorization task is not eligible for GPU")
    if not isinstance(approved, bool) or not isinstance(production_required, bool):
        raise ValueError("GPU approval and production need must be explicit booleans")
    if approved and (not isinstance(decision_ref, str) or not _REF_RE.fullmatch(decision_ref)):
        raise ValueError("approved GPU work requires a Factory decision reference")
    if not approved and decision_ref != "":
        raise ValueError("unapproved GPU work must not carry a Factory decision reference")
    if production_required and (not isinstance(production_ref, str) or not _REF_RE.fullmatch(production_ref)):
        raise ValueError("GPU need requires a production request reference")
    if not production_required and production_ref != "":
        raise ValueError("unneeded GPU work must not carry a production request reference")
    if isinstance(cost, bool) or cost != 0:
        raise ValueError("GPU authorization must allow exactly zero cost")
    if on_demand is not True:
        raise ValueError("GPU authorization must be on-demand only")
    return GpuAuthorization(job_id, task, approved, production_required)
