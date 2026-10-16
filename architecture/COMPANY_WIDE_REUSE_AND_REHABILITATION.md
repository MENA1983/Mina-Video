# Company-Wide Reuse, Rehabilitation, and Lifecycle Charter

**Authority:** Mena, sole owner and final authority  
**Canonical policy home:** AI Viral Content Factory (authoritative policy; this local copy defines the media-branch adoption rules)  
**Applies to:** every company function, employee/agent, repository, branch, workflow, service, tool, integration, provider, and future department.

## Non-negotiable principle

The company improves and reuses what it owns. It does not become a graveyard of abandoned tools, duplicated managers, stale branches, or agents with no measurable purpose. It also does not discard a working capability just because a newer candidate appeared.

This policy applies company-wide—not only to Mina-Video. The Factory's central control tower, research intelligence, secrets custody, editorial, rights and quality, publishing, analytics, maintenance, engineering, and every future branch must use the same lifecycle and evidence standards.

## 1. Lifecycle states

- **DISCOVERED:** candidate identified; no trust or production authority implied.
- **INVENTORIED:** owner, mission, consumers, permissions, dependencies, cost, and baseline are recorded.
- **TRIAGED:** overlap and risk are assessed; a primary incumbent and test plan are named.
- **EXPERIMENTAL:** isolated test only; least privilege; no production credentials or public effects unless separately approved.
- **VERIFIED:** representative tests and quality, security, privacy, rights, reliability, cost, and failure-recovery evidence meet explicit thresholds.
- **APPROVED:** Mena or the properly authorized decision-maker approves the specific intended scope.
- **ACTIVE:** the capability has a named consumer, an owner, health signals, audit evidence, a fallback, and a rollback plan.
- **REASSIGNED:** the former primary has a bounded, documented, useful secondary responsibility.
- **QUARANTINED:** unsafe, broken, unsupported, unexplained, or conflicting evidence; disabled from production until resolved.
- **RETIRE_CANDIDATE:** no longer primary, but retained during dependency checks, observation, and recovery validation.
- **RETIRED:** intentionally disabled, with code/artifacts and evidence retained according to policy for possible restoration.
- **DELETE_CANDIDATE:** proposed removal only; requires dependency/history/recovery review and explicit owner approval before deletion.

A PR merge, successful compile, provider announcement, or single happy-path demo is not proof that a capability is VERIFIED or ACTIVE.

## 2. The Keep → Test → Prove → Reassign → Retire → Delete rule

1. **Keep:** protect the current known-good capability as primary.
2. **Inventory:** identify its exact job, consumers, dependencies, permissions, costs, quality, failure modes, and unique behavior.
3. **Test:** evaluate a candidate in isolation against representative tasks and the incumbent baseline.
4. **Prove:** compare quality, reliability, latency, total cost, quotas, privacy, rights, security, maintainability, and recovery/rollback.
5. **Promote narrowly:** use the candidate only for the capability and scope it proved; do not infer broader competence.
6. **Reassign:** give the incumbent a useful role only if the role has a real consumer and measurable tests: fallback, specialist, independent QA, low-cost/batch worker, compatibility adapter, offline worker, or recovery path.
7. **Restore on failure:** if the candidate fails, restore the incumbent as primary; quarantine or revise the candidate without losing evidence.
8. **Retire:** require an observation window, dependency/consumer check, backup or recovery reference, rollback drill, and owner-approved plan.
9. **Delete:** only after explicit owner approval and evidence that no unique behavior, consumer, audit obligation, recovery value, or required history remains.

If a tool has no useful safe role, keep it quarantined or retire it after review rather than inventing a fake job just to keep it alive. The same rule applies to staff/agents: evaluate actual work and training opportunities, then reassign with clear scope and supervision.

## 3. Company inventory record

Every capability or role must record:
- stable ID, version/revision, lifecycle state, and previous state;
- mission and measurable acceptance criteria;
- accountable owner/manager and independent reviewer;
- primary/fallback designation and named consumers;
- inputs, outputs, contracts, dependencies, and source of truth;
- permissions, secret scope, privacy, rights, and safety boundaries;
- representative test results and dated evidence links;
- quality, reliability, latency, cost, quotas, and failure/recovery outcomes;
- overlaps and the decision for each overlapping tool/team;
- reassignment target, rollback procedure, observation window, and owner decision.

No credentials, tokens, private source, or secret values belong in this register.

## 4. One company, one authority per decision

- **Factory / central Control Tower:** company-wide policy, identity, approvals, secret-access policy, research orchestration, channel routing, durable job/publication truth, deduplication, reconciliation, and analytics.
- **Mina-Video:** media execution, rendering/encoding, media-provider adapters, artifact staging, digests, provenance, production queue, and render health.
- **Shared interfaces:** versioned contracts, stable job/correlation IDs, explicit states, evidence, and clear failure/reconciliation semantics.
- **Future branches:** inherit this charter and nominate one canonical authority for each function. They must not create a competing approval system, secret vault, publication ledger, scheduler, or management hierarchy.

Mina-Video must not become a second company control plane. The Factory must not grow a parallel media renderer. Secrets are accessed only by scoped authorized runtime components; agents and tools never receive secret values unnecessarily.

## 5. Repair and workforce rehabilitation

For a broken tool or workflow, record symptoms and evidence, isolate the failure, identify the root cause, preserve a reproducible failing test, repair on an isolated branch, run regression tests, obtain independent review, and use staged activation with rollback. Do not let a repair worker approve its own high-risk change or bypass protected CI.

For a staff role or agent, assess demonstrated strengths and missing skills; define a bounded new responsibility, training or adaptation plan, supervisor, success metrics, and review date. Do not equate "old" with "useless", nor "new" with "better".

## 6. Cleanup and anti-sprawl rules

- Inventory before cleanup; archive before destructive actions.
- Identify duplicate branches by commit SHA and unique diff, not just by branch name.
- Prefer one canonical implementation and reuse focused tests/logic rather than merging entire stale stacked branches.
- Keep historical evidence required for audit, incident analysis, or recovery.
- A wrapper is not a useful employee or service unless it has an observable responsibility and evidence output.
- Unknown state, conflicting evidence, broken security boundary, or unavailable independent review means **SAFE_HOLD**.
- Never delete legacy code, branches, workflows, artifacts, or history merely because a newer tool exists.

## 7. Adoption gate for new tools

Before a new tool is approved, the proposal must state:
1. the concrete gap it closes;
2. which current capability was assessed and why it is insufficient;
3. a baseline workload and measurable success/failure thresholds;
4. total cost, rate limits, privacy/data handling, rights, security, and operational burden;
5. integration and rollback plans;
6. the incumbent's future role if the candidate passes;
7. the owner approval needed for production activation.

## 8. Current implementation truth

The Factory reuse register is the canonical company inventory and lists the known open/closed PRs and cleanup candidates. Mina-Video keeps a local media capability inventory and references the same company-wide lifecycle. These registers are documentation and governance controls; they do not imply that every department is a deployed autonomous agent or that every listed repair/reassignment has been executed.

The current audit has not authorized public publishing, account linking, destructive branch deletion, credential changes, or irreversible cleanup.
