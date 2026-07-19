# Shot Ledger Secure Proof Runner Receipt

Date: 2026-07-18
Agent: Orion_L
Status: PASS_LOCAL_WITH_EXTERNAL_AUTH_PENDING

## Artifact

- `scripts/proof`
- `ops/shot-ledger.op.env.example`
- `docs/SECURE_PROOF_RUNNER_HANDOFF_2026-07-18.md`
- `docs/REAL_PROOF_RUNBOOK_2026-07-18.md`
- `README.md`

## Result

Shot Ledger now has one reproducible operator command for provider/B2
preflight, three-take generation, retry, human finalization, and fresh-process
B2 verification. The runner accepts only `op://` references for B2 and OpenAI
credentials, so literal secrets cannot be placed in its environment reference
file by mistake.

The real reference file lives outside the repository at
`~/.config/shot-ledger/proof.env`. Repository ignores also reject `.env.op` and
`*.op.env` files.

## Checks

- Shell syntax passed.
- Runner help/command routing passed.
- 42 Python tests passed.
- 15 Worker tests passed.
- Ruff and Python format checks passed.
- TypeScript typecheck passed.
- Worker dry-run deployment passed.

## External State

- Private B2 bucket: `naumio-shot-ledger-proof-2026`
- Region: `us-east-005`
- Encryption: enabled
- Scoped application-key form is prepared for:
  - bucket-only access
  - prefix `shot-ledger/`
  - read/write
  - S3-compatible bucket listing
  - 90-day expiry
- Key creation is not claimed; it awaits the required action-time confirmation.
- GitHub commit exists locally as `4f5e9d5`; push awaits restoration of the
  existing GitHub CLI authorization.

## Decision

`CONTINUE_TO_SCOPED_B2_KEY`

This receipt does not claim the real Genblaze/B2 proof or contest completion.

The environment-style example is kept in GitHub but intentionally omitted from
the Drive mirror because the shared-proof scanner blocks risky filenames. The
mirrored Markdown handoff preserves its non-secret operating contract.

## Shared Proof

- Drive path:
  `/TMN_NAUMIO_HQ/06_DELIVERY/SHOT-LEDGER-SECURE-PROOF-RUNNER-2026-07-18/`
- Notion URL:
  https://app.notion.com/p/3a2b143d291781d3a8e1dd58369b61e0
- Hash verification: initial five-file mirror verified in
  `MIRROR_MANIFEST.json` run `20260719T000301301Z`; the reconciled receipt is
  mirrored again after these pointers are added.
