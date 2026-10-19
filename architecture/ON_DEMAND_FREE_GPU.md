# On-Demand Free GPU Integration Gate

## Status

This is an experimental, fail-closed compute-selection gate, not a live GPU worker. CPU remains the active implementation. No GPU provider is currently registered, no GPU job is dispatched, and no cloud account/Space or credential was created.

## Decision rule: Factory authorization + production need

GPU use is task-specific and on-demand only. Mina-Video now expects a `factory-gpu-authorization/v1` record from trusted Factory orchestration. The record must be scoped to the exact task and job, carry an explicit Factory decision reference and production request reference, set allowed cost to exactly zero, and require on-demand execution. Missing, malformed, paid, or mismatched authorization keeps execution on CPU.

Schema validation does **not** authenticate the record's origin. The caller must obtain it from the trusted Factory control plane over an authenticated, reviewed handoff. That handoff is not yet wired into a live GPU dispatch path; no provider execution adapter exists.

The experimental opt-in and explicit zero-cost budget remain additional gates. A provider name, quota-shaped environment variable, or policy record alone cannot enable dispatch.

## Candidate

Hugging Face Spaces ZeroGPU is the first candidate for PyTorch-style inference. Its official documentation says it provides shared GPU access with per-account daily quotas, is Gradio-only, and can use prepaid credits after quota exhaustion for eligible accounts. The Factory must therefore treat a quota check and a hard no-paid-path guarantee as mandatory, not infer that a provider name means free capacity:
- https://huggingface.co/docs/hub/en/spaces-zerogpu
- https://huggingface.co/docs/hub/en/spaces-overview

Kaggle provides free GPU notebook sessions with weekly quota, but the documented workflow is notebook/session-oriented; it is not selected as an unattended production worker without a separately verified automation interface:
- https://www.kaggle.com/docs/efficient-gpu-usage
- https://www.kaggle.com/docs/notebooks

## Task-to-device policy

| Task | Current choice | Why |
|---|---|---|
| `video.render` / FFmpeg composition | CPU | Current renderer uses `libx264`; GPU helps only with a verified CUDA/NVENC path and representative benchmarks. |
| `image.generate` | GPU candidate | PyTorch model inference can benefit; must have an owned worker and verified quota, plus Factory approval and production need. |
| `video.generate` | GPU candidate | Model-dependent; only when the selected model/backend is CUDA-compatible. |
| `audio.tts`, `music.generate` | GPU candidate | Model-dependent; CPU remains fallback until a compatible model/worker is proven. |
| Image/audio processing, captions, thumbnails | CPU | Keep CPU until measured workloads justify GPU use. |

## Gate and cost policy

- `MINA_GPU_EXPERIMENTAL_ENABLED` must be explicitly enabled for candidate evaluation; default is off.
- `MINA_GPU_MAX_COST_USD` must be exactly zero. Invalid or non-zero values SAFE_HOLD.
- Candidate provider is `huggingface_zerogpu`; a provider name alone never enables execution.
- A live adapter must verify the authenticated provider's remaining free quota immediately before dispatch and prove it cannot use paid credits, billing, or a paid hardware tier.
- The worker must be on an explicitly allowlisted HTTPS host, accept only bounded task payloads, avoid Factory/YouTube credentials, and return a result bound to job ID, input digest, output digest, and provider execution evidence.
- Dispatch is on-demand only. No scheduled warmups, polling loops, auto-provisioning, or automatic billing.
- On quota exhaustion, provider outage, timeout, unknown remote outcome, or digest mismatch, stop and reconcile; do not blindly retry. Keep the CPU path available.
- A public Gradio Space must not receive private scripts, account data, OAuth credentials, secret URLs, or unlicensed assets. A dedicated owned Space/worker and explicit data handling review are prerequisites.

## What remains before real activation

1. Implement the trusted Factory-to-Mina-Video authorization handoff and validate its authenticated origin.
2. Create or identify an owner-controlled ZeroGPU Space and confirm its visibility, terms, quota, and data handling.
3. Implement and test a concrete adapter for the Space's actual Gradio API; do not guess endpoint names.
4. Implement authenticated quota verification and a hard no-paid-credit guard.
5. Define per-task input/output schemas and resource limits.
6. Verify downloaded artifacts by SHA-256 and bind evidence to the original task ID.
7. Run mocked tests, then an explicitly approved small non-sensitive private test; measure latency, quality, failure rate, and CPU comparison.
8. Keep provider in EXPERIMENTAL until representative quality, reliability, latency, and cost evidence passes. No public publishing is part of GPU testing.

The Factory remains the control plane. Mina-Video owns media execution and compute selection. This module does not alter the Factory's external-video/v1 manifest or add a second job/publication ledger.
