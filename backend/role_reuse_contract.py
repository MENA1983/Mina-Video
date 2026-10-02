"""Mina-Video contract for bounded workforce reuse.

Mina-Video may accept temporary operational tasks from Factory (media quality
research, render diagnostics, evidence collection, adapter experiments), but
it never receives Factory ownership, billing, governance, credentials, or
final-live-activation authority.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class ExecutionTask(str, Enum):
    MEDIA_QUALITY_RESEARCH = "media_quality_research"
    RENDER_DIAGNOSTICS = "render_diagnostics"
    PROVIDER_EXPERIMENT = "provider_experiment"
    PROVENANCE_REVIEW = "provenance_review"


FORBIDDEN_SCOPES = frozenset({
    "ownership",
    "billing",
    "credentials",
    "governance",
    "final-live-activation",
})


@dataclass(frozen=True)
class TemporaryExecutionAssignment:
    task: ExecutionTask
    scope: str
    expires_when: str
    evidence_required: bool = True


def validate_assignment(assignment: TemporaryExecutionAssignment) -> bool:
    scope = assignment.scope.casefold().strip()
    if scope in {item.casefold() for item in FORBIDDEN_SCOPES}:
        return False
    return bool(assignment.expires_when.strip()) and assignment.evidence_required
