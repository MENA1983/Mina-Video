# Mina-Video Branch Watchdog Contract

Status: ACTIVE DESIGN / NOT PRODUCTION-VERIFIED

## Purpose
The watchdog observes completed GitHub Actions workflows in Mina-Video and turns failures into a durable, deduplicated incident signal. It does not publish media, retry ambiguous external operations, access Factory secrets, or modify code.

## Flow
1. Mina-Video workflow completes.
2. Branch Watchdog classifies the conclusion.
3. An open incident is reused for the same workflow/branch/conclusion instead of creating issue spam.
4. The incident contains run URL, commit SHA, severity, routing, and safety constraints.
5. Factory Branch Manager consumes the signal through a trusted monitor path.
6. Branch Manager requests bounded Maintenance/Repair/Development work according to its existing authority model.
7. Recovery is accepted only after a new authoritative workflow result.

## Routing
- failure/timed_out: BLOCKING -> Maintenance; Repair/Development may follow after investigation.
- cancelled: ATTENTION -> Monitor.
- action_required/stale: ATTENTION -> Research.
- unknown conclusion: UNKNOWN -> Research; never retry automatically.

## Security Boundary
Mina-Video remains the public/free media execution plane. No Factory secret is copied into Mina-Video. The watchdog uses only its repository-scoped GitHub token for its own issue signal. Factory credentials, governance, publication authority, and private CI remain outside this repository.

## Evidence Rule
Incident creation is not proof that a defect is fixed. A later successful workflow is the evidence used for recovery. Artifact attestations are reserved for release artifacts where provenance verification materially matters; routine test runs are not attested.