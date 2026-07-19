# Shot Ledger Public Preview Privacy QA Receipt

Date: 2026-07-18
Agent: Orion_L
Status: PASS_WITH_PAID_PROOF_PENDING

## Artifact

- Public preview: https://shot-ledger-preview.gigantic-stranger.workers.dev
- Desktop capture: `proof/ui/shot-ledger-public-preview-desktop-2026-07-18.png`
- Mobile capture: `proof/ui/shot-ledger-public-preview-mobile-2026-07-18.png`
- Evidence matrix: `docs/SUBMISSION_EVIDENCE_MATRIX.md`

## Finding

The visibly synthetic public preview was honest about its evidence scope, but
its scene and decision JSON exposed absolute local filesystem URIs from the
machine that generated the deterministic proof.

## Patch

- Local synthetic proof now uses stable `synthetic://shot-ledger/...` artifact
  identifiers instead of `file://` URIs.
- The local repository resolves those identifiers only inside its configured
  proof directory.
- Exported public evidence now includes the three canonical Genblaze manifests
  without exposing local paths.
- Regression coverage checks both scene and downloadable decision JSON.

## Verification

- 42 Python tests passed.
- 15 Worker tests passed.
- Clean-checkout CI passed: https://github.com/Peanuts1605/shot-ledger/actions/runs/29670870921
- Ruff lint and format checks passed.
- TypeScript typecheck and Wrangler dry run passed.
- Worker version `2721733a-7d39-484e-b5d9-ba09ab463510` deployed.
- Live `/healthz`, `/api/scene`, and `/api/run-state` returned HTTP 200.
- Live media integrity is verified and all public artifact URIs are non-file
  synthetic identifiers.
- Browser replay found no console errors.
- Packet download emitted a browser download event.
- Three keeper radios and the reseal control are intentionally disabled in the
  read-only public preview.
- The 390px mobile viewport has no horizontal overflow.

## Rules Reconciliation

The official Devpost page and rules were rechecked on 2026-07-18. The deadline
remains August 3, 2026 at 5:00 PM Eastern Time. The required demo must be public
and under three minutes.

## Decision

`CONTINUE_TO_CAPPED_REAL_PROOF`

The synthetic preview is clean and trustworthy, but it remains explicitly
separate from the pending paid Genblaze/B2 proof.

## Shared Proof

- Git commit: `c248427a21a9971653052d643ba69d21ef71855e`
- Drive path: `/TMN_NAUMIO_HQ/06_DELIVERY/SHOT-LEDGER-PUBLIC-PREVIEW-PRIVACY-QA-2026-07-18/`
- Notion URL: https://app.notion.com/p/3a2b143d291781d3a8e1dd58369b61e0
- Hash verification: recorded in `MIRROR_MANIFEST.20260719T025403238Z.json`; reconciled receipt re-mirrored below
