# Mina-Video Media Execution Contract

## Purpose

Mina-Video is the Media Execution Plane for the AI Content Company.

It owns implementation and execution of media capabilities while the private Factory remains the Company Control Plane.

## Media capabilities owned here

- video generation and transformation
- video rendering and assembly
- image generation and processing
- voice, narration, TTS and speech processing
- audio generation and processing
- music generation and processing
- captions and subtitle rendering
- thumbnails, effects, transitions and media post-processing
- adapters for approved external media providers

## Factory responsibilities

The Factory owns:

- company planning and orchestration
- capability discovery and evaluation
- policy and rights decisions
- quality requirements and gates
- cost/quota policy
- authorization
- provider-neutral manifests/contracts
- publication authorization
- company-level audit, provenance and reconciliation

The Factory may discover, evaluate and recommend new media capabilities. It must not require provider-specific media implementation to be added to the private control plane.

## Mina-Video responsibilities

Mina-Video owns:

- provider adapters and SDK integrations
- media execution
- rendering and FFmpeg pipelines
- media-specific validation and resource limits
- execution evidence
- artifact creation
- public-safe media tests

## Future media tools

A newly discovered media tool is not rejected merely because it is new. If it is useful, safe, rights-compatible and passes the required evidence gates, it can be registered and tested here.

Canonical path:

`Discover → Evaluate → Experiment → Verify → Approve → Register/Activate → Measure`

A tool is not activated merely because it is free, new, popular or advertised as better.

## Capability registration

New media capabilities are registered in `media/capabilities.json` and remain provider-neutral at the Factory boundary.

Provider-specific implementation belongs under the Mina-Video execution plane. Adding a capability here does not grant publication, billing, credential, governance or ownership authority.

## Provider isolation

A provider failure must remain isolated to its provider/capability boundary. It must not silently disable unrelated providers or company functions.

Unknown, expired, unauthorized or integrity-failing execution requests fail closed.

## Secrets

API keys, OAuth secrets, access tokens, cookies and private credentials must never be committed to this repository or placed in media manifests.

Approved runtime secret mechanisms must provide credentials to the adapter at execution time.

## Factory boundary

Factory requests what capability is required. Mina-Video decides how an authorized capability is executed inside the allowed execution boundary.

Example:

Factory requests: `video.generate` with specified duration, dimensions, quality and policy requirements.

Mina-Video selects an authorized implementation, executes it, validates the artifact and returns structured execution evidence.

## Sovereignty

Capabilities may expand. Authority cannot self-expand.

Mina-Video may not:

- change company ownership or governance
- change Factory security gates
- spend money or change billing
- obtain or rotate company credentials without the approved mechanism
- publish directly to social platforms unless an explicitly authorized downstream contract permits it
- bypass Factory policy, rights or approval gates
