# Mina Video 🎬

Standalone external media-execution engine for the AI Viral Content Factory.

## Role

`Mina-Video` is the execution plane. The private factory remains the control plane for content planning, quality, rights, policy, approval, publication authorization, idempotency, reconciliation, analytics and learning.

## Media ownership

All media execution capabilities belong here, not in the private Factory. This includes current and future:

- video generation and rendering;
- image generation and processing;
- voice, narration, speech and audio processing;
- music generation and processing;
- captions, thumbnails, effects and other media post-processing;
- adapters for approved external media providers.

See `media/capabilities.json` for the provider-neutral capability registry. New media tools can be added by registering a capability/provider implementation here without turning the Factory into a second media engine.

The Factory decides **what is authorized and required**. Mina-Video decides **how the approved media work is executed**.

## Current pipeline

```text
Factory approved package
        ↓
external-video/v1 manifest
        ↓
approved public asset host allowlist
        ↓
HTTPS + redirect + size verification
        ↓
multiple images per scene
        ↓
FFmpeg + eSpeak-ng
        ↓
1080×1920 MP4
        ↓
GitHub Release artifact
```

## Limits

- 1–20 scenes
- up to 6 images per scene
- up to 40 images per manifest
- up to 20 MB per image
- up to 50 MB per supplied audio file
- maximum final video duration: 180 seconds

These limits are safety and reliability boundaries, not a promise of unlimited production.

## Security boundary

Never put passwords, OAuth tokens, cookies, client secrets, private URLs, or private factory source into a manifest.

Production downloads are fail-closed unless the repository variable `MINA_VIDEO_ALLOWED_HOSTS` contains the exact approved public artifact-delivery hostnames. Multiple hosts may be supplied as a comma-separated list. Hostnames are canonicalized; redirects are checked against the same allowlist, so a permitted URL cannot redirect to an unapproved host.

Only HTTPS public assets that have already passed the factory's rights/policy gates should cross this boundary.

## Configuration

Set the GitHub repository variable `MINA_VIDEO_ALLOWED_HOSTS` to the authoritative host(s) defined by the Factory↔Mina-Video contract. Do not guess or broaden this list. An empty or malformed value intentionally prevents production rendering.

## Status

The renderer and workflow have been hardened with a fail-closed asset-host trust boundary and public regression coverage. A real Factory↔Mina-Video end-to-end render, using the owner-configured approved host, is still required before the integration can be called production-verified.
