# Mina-Video Production Line Operations

**Branch manager:** Mina-Video execution owner under Factory's Company Director  
**Authority boundary:** Factory authorizes content and destinations; Mina-Video executes approved media work only.

## Production-line responsibilities

The Mina-Video branch manager owns:
- render queue health and worker capacity;
- rendering, encoding, audio/voice, and artifact assembly;
- deterministic render identity and duplicate-render prevention;
- manifest and asset-host validation;
- artifact digest and provenance evidence;
- production workflow health and incident escalation;
- post-repair verification and regression evidence.

The branch manager does not own channel policy, YouTube credentials, content approval, publication authorization, or public publishing.

## Monitoring already present

- Public media CI validates the renderer and its tests.
- The branch watchdog creates or updates an incident issue when monitored branch workflows fail or time out.
- The production-line watchdog runs every 15 minutes and inspects the latest GitHub Actions run for the canonical render workflow.
- A render that remains queued/in progress for 30 minutes or more is treated as stale.
- Failed, timed-out, cancelled, or unrecognized latest-run states create or update a bounded incident issue.
- The watchdog only reads workflow metadata and writes an incident report; it never cancels, reruns, or repairs a render.

## Incident path

```text
Render workflow
  → Read-only production-line watchdog
  → Health classification + evidence summary
  → Deduplicated GitHub incident issue
  → Mina-Video Branch Manager
  → Bounded investigation / proposed fix
  → Regression tests
  → Independent review / owner approval when required
  → Successful follow-up run
  → Close incident with evidence
```

The watchdog uses GitHub's built-in token with only Actions read, Contents read, and Issues write permissions. It does not read or transmit Factory secrets. Incident issues contain run metadata and links, not credential values.

## Health states

- **HEALTHY:** latest render run completed successfully.
- **RUNNING:** latest run is still within the 30-minute observation window.
- **STALE:** latest run remains queued or in progress for at least 30 minutes.
- **DEGRADED:** latest completed run failed, timed out, or was cancelled.
- **UNKNOWN:** run state or required evidence cannot be interpreted.
- **IDLE:** no render runs exist yet; absence of production traffic is not automatically an incident.

## Limits and safeguards

This is workflow-level monitoring, not full production observability. It does not inspect live CPU/memory metrics, verify MP4 visual quality, prove content rights, or verify the complete Factory-to-publication lifecycle. A successful render workflow is only one evidence item.

No automatic retry or repair is allowed for ambiguous work. Factory owns reconciliation and publication decisions. If a render run appears stuck, preserve its run URL, run ID, commit SHA, status, and timestamps before taking action.

The first real Factory-to-Mina-Video render still requires explicit owner approval because it creates a release artifact in the Mina-Video repository.
