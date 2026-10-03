"""Mina-Video contract for bounded workforce reuse."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import re


class ExecutionTask(str, Enum):
    MEDIA_QUALITY_RESEARCH = "media_quality_research"
    RENDER_DIAGNOSTICS = "render_diagnostics"
    PROVIDER_EXPERIMENT = "provider_experiment"
    PROVENANCE_REVIEW = "provenance_review"


FORBIDDEN_SCOPES = frozenset({
    "ownership", "billing", "credentials", "governance", "final-live-activation",
})
_OPEN_ENDED_EXPIRY = frozenset({"permanent", "never", "indefinite", "no-expiry", "none"})


@dataclass(frozen=True)
class TemporaryExecutionAssignment:
    task: ExecutionTask
    scope: str
    expires_when: str
    evidence_required: bool = True


def _tokens(value: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", value.casefold()))


def validate_assignment(assignment: TemporaryExecutionAssignment) -> bool:
    if not assignment.expires_when.strip() or assignment.expires_when.casefold().strip() in _OPEN_ENDED_EXPIRY:
        return False
    if not assignment.evidence_required:
        return False
    scope_tokens = _tokens(assignment.scope)
    forbidden_tokens = set().union(*(_tokens(item) for item in FORBIDDEN_SCOPES))
    return not bool(scope_tokens & forbidden_tokens)
