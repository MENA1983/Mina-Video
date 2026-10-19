# On-Demand Free GPU Integration Gate

## Status

This is an experimental, fail-closed compute-selection gate, not a live GPU worker. CPU remains the active implementation. No GPU provider is currently registered, no GPU job is dispatched, and no cloud account/Space or credential was created.

## Decision rule: company + production

GPU use is task-specific and on-demand only. A task can be considered for GPU only when **both** conditions are explicitly true:
- The Factory/company decision authorizes GPU for the current scope: `MINA_GPU_FACTORY_APPROVED=true`.
- The production team marks the specific task as needing GPU: `MINA_GPU_PRODUCTION_REQUIRED=true`.

The experimental opt-in and explicit zero-cost budget are additional gates, not substitutes for either decision. These flags are policy inputs for planning only; they do not authorize dispatch or prove that a provider is free. Missing approval or missing production need means CPU remains selected.

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
| `image.generate` | GPU candidate | PyTorch model inference can benefit; must have an owned worker and verified quota, plus company approval and production need. |
| `video.generate` | GPU candidate | Model-dependent; only when the selected model/backend is CUDA-compatible. |
| `audio.tts`, `music.generate` | GPU candidate | Model-dependent; CPU remains fallback until a compatible model/worker is proven. |
| Image/audio processing, captions, thumbnails | CPU | Keep CPU until measured workloads justify GPU use. |

## Gate and cost policy

- `MINA_GPU_EXPERIMENTAL_ENABLED` must be explicitly enabled for candidate evaluation; default is off.
- `MINA_GPU_MAX_COST_USD` must be exactly zero. Invalid or non-zero values SAFE_HOLD.
- Candidate provider is `huggingface_zerogpu`; a provider name alone never enables execution.
- `MINA_GPU_FACTORY_APPROVED` and `MINA_GPU_PRODUCTION_REQUIRED` must both be explicitly true after quota verification; missing values fail closed.
- A live adapter must verify the authenticated provider's remaining free quota immediately before dispatch and prove it cannot use paid credits, billing, or a paid hardware tier.
- The worker must be on an explicitly allowlisted HTTPS host, accept only bounded task payloads, avoid Factory/YouTube credentials, and return a result bound to job ID, input digest, output digest, and provider execution evidence.
- Dispatch is on-demand only. No scheduled warmups, polling loops, auto-provisioning, or automatic billing.
- On quota exhaustion, provider outage, timeout, unknown remote outcome, or digest mismatch, stop and reconcile; do not blindly retry. Keep the CPU path available.
- A public Gradio Space must not receive private scripts, account data, OAuth credentials, secret URLs, or unlicensed assets. A dedicated owned Space/worker and explicit data handling review are prerequisites.

## What remains before real activation

1. Create or identify an owner-controlled ZeroGPU Space and confirm its visibility, terms, quota, and data handling.
2. Implement and test a concrete adapter for the Space's actual Gradio API; do not guess endpoint names.
3. Implement authenticated quota verification and a hard no-paid-credit guard.
4. Define per-task input/output schemas and resource limits.
5. Verify downloaded artifacts by SHA-256 and bind evidence to the original task ID.
6. Run mocked tests, then an explicitly approved small non-sensitive private test; measure latency, quality, failure rate, and CPU comparison.
7. Keep provider in EXPERIMENTAL until representative quality, reliability, latency, and cost evidence passes. No public publishing is part of GPU testing.

The Factory remains the control plane. Mina-Video owns media execution and compute selection. This module does not alter the Factory's external-video/v1 manifest or add a second job/publication ledger.
