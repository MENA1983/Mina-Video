# Company Integration Contract

Mina-Video is the Media Execution Plane of one company. It is not a second company or independent control plane.

## Upstream

Factory provides a stable capability request containing the required media capability, constraints, quality requirements, provenance requirements and authorization context.

## Execution

Mina-Video owns provider-specific media execution for video, image, audio, voice, music, FFmpeg, rendering, compositing, captions and artifact assembly.

## Downstream

Mina-Video returns:
- artifact metadata;
- provenance;
- execution result;
- validation result;
- provider/capability identifier;
- relevant failure or uncertainty state.

## Factory remains authoritative for

- orchestration;
- policy;
- rights;
- security gates;
- quality gates;
- publication decisions;
- owner-only boundaries.

## Failure isolation

A provider failure must remain inside its execution boundary. Mina-Video must not disable unrelated providers or company lanes merely because one provider fails.

## Evidence

Mina-Video must not claim VERIFIED merely because a provider adapter exists. Verification requires an executed test or experiment with retained evidence.

## New media tools

New video/image/audio/music tools are candidates for Mina-Video. They follow the company lifecycle:
DISCOVERED -> TRIAGED -> EXPERIMENTAL -> VERIFIED -> APPROVED -> ACTIVE.

No new provider gains ownership, billing, governance, credential, security-gate or unrestricted publication authority.

## Anti-fragmentation

Every execution capability must have a defined Factory consumer and an evidence return path. Orphan execution systems are not production-ready.
