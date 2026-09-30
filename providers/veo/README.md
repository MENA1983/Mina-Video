# Veo Provider Adapter Boundary

Status: EXPERIMENTAL

This directory reserves the provider boundary for an optional Google Veo adapter. It does not contain credentials and does not authorize production use by itself.

## Requirements
- Provider credentials remain outside source control and outside public CI.
- Usage/quota must be measured from authoritative provider/account evidence.
- The Manager may select Veo only when the scene has a documented benefit over the baseline.
- Quota exhaustion must fall back to another approved provider or local/open tooling.
- Provider errors must remain isolated to this adapter.
- Activation requires evidence, rights/security review, cost/quota review, rollback/fallback coverage, and the normal adoption gates.

No implementation is claimed as production-verified by this boundary file alone.
