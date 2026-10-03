"""Mina-Video contract for evidence collection requested by Factory.

Mina may collect media-plane evidence for quality, rendering, provider, and
provenance investigations. It never receives Factory ownership authority.
Evidence is append-only in intent: collect, identify, return; do not rewrite
or suppress evidence to make a result pass.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class EvidenceScope(str, Enum):
    MEDIA_QUALITY = "media-quality"
    RENDER_DIAGNOSTICS = "render-diagnostics"
    PROVIDER_EXPERIMENT = "provider-experiment"
    PROVENANCE = "provenance"


FORBIDDEN_SCOPES = frozenset({
    "ownership",
    "billing",
    "credentials",
    "governance",
    "final-live-activation",
})


@dataclass(frozen=True)
class EvidenceAssignment:
    scope: EvidenceScope
    case_id: str
    evidence_required: bool = True
    expires_when: str = ""


def validate_evidence_assignment(assignment: EvidenceAssignment) -> bool:
    if not assignment.case_id.strip() or not assignment.expires_when.strip():
        return False
    return assignment.evidence_required and assignment.scope in set(EvidenceScope)
