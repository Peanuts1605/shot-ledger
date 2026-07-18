# Shot Ledger Adversarial QA

Date: 2026-07-18
Decision: PASS_WITH_LIVE_PROOF_PENDING

## Strongest Claim Attacked

Shot Ledger claims that a public reviewer can trust the visible keeper, human
reason, media, and provenance as one verified decision packet.

The first public Worker implementation checked that `decision.packet_hash`
matched the stored verification receipt, but did not recompute the hash from the
decision content. A changed human reason could therefore appear beside an old
verified receipt. This contradicted the product thesis even though the Worker
was read-only to anonymous users.

## Corrections

1. The Worker now canonicalizes the B2 decision packet and recomputes its
   SHA-256 hash before it reports a verified scene.
2. The canonicalizer is regression-tested against a packet emitted by the
   Python decision builder, so the two runtimes share one hash contract.
3. The Worker revalidates the packet structure: three unique takes, one keeper,
   one controlled variable, correct derived statuses, non-empty human reason,
   and lowercase media/manifest SHA-256 values.
4. B2 packet export now requires the same current decision/verification match
   as B2 media retrieval.
5. Python B2 reload now rebuilds stored packets through the same invariants used
   at creation rather than validating only the digest.

## Reproduced Attacks

| Attack | Expected result | Evidence |
|---|---|---|
| Change the human reason after verification while leaving the packet hash untouched | Reject | Worker regression test |
| Duplicate a take ID and recompute a matching digest | Reject | Python and Worker structural tests |
| Pair the current decision with a stale verification receipt | Refuse media and export | Worker route tests |
| Submit a public keeper change | HTTP 403 | Worker route test |
| Point an asset URI at another endpoint, bucket, or traversal key | Reject | Worker URL-boundary tests |

## Current Gate

- 42 Python tests pass.
- 15 Worker tests pass.
- Ruff, Python format, TypeScript typecheck, dependency audit, and Worker dry
  run pass.
- Real Genblaze/B2 evidence remains pending and is not inferred from this local
  adversarial proof.

## Public Preview Replay

The hardened Worker was deployed to the synthetic preview after pinning the
project to its existing Cloudflare account. Live replay verified:

- URL: https://shot-ledger-preview.gigantic-stranger.workers.dev
- Worker version: `a87b4be7-1ac4-4b1c-87ea-4a7cd648b533`
- `/healthz`: HTTP 200, `mode=local`, `write_enabled=false`
- `/api/scene`: HTTP 200 with an explicit synthetic-not-B2 proof label
- `/api/export`: HTTP 200 with the same packet hash and three takes
- `/api/decision` POST: HTTP 403
- unsupported API method: HTTP 405
- all three preview assets: HTTP 200, `image/png`

This verifies the public fallback and read-only boundary. It remains separate
from the pending production B2 deployment.

## Decision

`CONTINUE_TO_SCOPED_B2_PREFLIGHT`
