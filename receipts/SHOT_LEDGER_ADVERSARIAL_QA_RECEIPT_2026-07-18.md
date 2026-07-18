# Shot Ledger Adversarial QA Receipt

Date: 2026-07-18
Agent: Orion_L
Status: PASS_WITH_LIVE_PROOF_PENDING

## Artifact

- `docs/ADVERSARIAL_QA_2026-07-18.md`

## Finding

The public Worker trusted a stored verification flag and matching packet-hash
field without recomputing the canonical decision hash from the content it was
about to show. That allowed changed human rationale to appear beside an old
verified receipt if the B2 decision object changed after verification.

## Patch

- Worker canonical hash recomputation before scene, media, or export trust.
- Cross-runtime hash regression against a Python-built packet.
- Worker packet-invariant validation.
- Python stored-packet invariant revalidation.
- Stale verification blocks both media and packet export.

## Checks

- 42 Python tests passed.
- 15 Worker tests passed.
- Ruff and Python format passed.
- TypeScript typecheck passed.
- Dependency audit found zero vulnerabilities at the configured gate.
- Worker dry run passed.

## Decision

`CONTINUE_TO_SCOPED_B2_PREFLIGHT`

The live Genblaze/B2 proof remains required. This receipt does not close the
contest goal.

## Shared Proof

- Git commit: PENDING_COMMIT
- Drive path: PENDING_MIRROR
- Notion URL: PENDING_POINTER
- Hash verification: PENDING_RECONCILIATION
