# Veo Monthly Limited Provider Policy

Status: EXPERIMENTAL
Owner: Factory Manager
Execution plane: Mina-Video

## Purpose
Use Google Veo as an optional, monthly-limited media provider only for scenes where it provides measurable value over the current baseline.

## Rules
- Veo is not a critical dependency.
- Media execution and provider adapters remain in Mina-Video.
- Factory owns policy, provider selection criteria, evidence, cost governance, and adoption decisions.
- Never place provider credentials in public code or public CI.
- Never assume a monthly quota amount without current provider/account evidence.
- Track usage from authoritative provider evidence; do not invent counters.
- Reserve a safety buffer and stop new Veo jobs when the configured safe threshold is reached.
- When Veo is unavailable or budget-exhausted, fall back to an approved alternative provider or local/open tooling.
- Veo failure or quota exhaustion must never stop the production pipeline.

## Decision flow
DISCOVERED -> TRIAGED -> EXPERIMENTAL -> VERIFIED -> APPROVED -> ACTIVE

For each Veo job the Manager should consider:
1. Is Veo materially better for this scene?
2. Can the baseline meet the requirement?
3. What is the measured quota/cost impact?
4. Is rights/security review complete?
5. Is there a fallback and rollback path?

## CI policy
Public-safe Veo adapter tests belong in Mina-Video public CI.
Tests requiring provider secrets belong only in Factory Private CI and remain WAITING_FOR_PRIVATE_CI until actually executed.

## Failure boundary
Provider failure, quota exhaustion, or API change must be isolated to the Veo adapter. Other providers and the rest of the factory must continue.
