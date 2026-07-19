# Shot Ledger Secure Proof Runner Handoff

Date: 2026-07-18
Decision: `CONTINUE_TO_SCOPED_B2_KEY`

## Operator Surface

Use `scripts/proof` for every real-proof step:

```text
scripts/proof preflight
scripts/proof generate
scripts/proof retry
scripts/proof finalize --keeper <take-id> --reason <visible-reason>
scripts/proof verify
```

The runner loads secrets with 1Password CLI from
`~/.config/shot-ledger/proof.env`. It rejects the file unless `B2_KEY_ID`,
`B2_APP_KEY`, and `OPENAI_API_KEY` are `op://` references. Literal credentials
must never be written there.

The external reference file supplies these non-secret settings:

```text
B2_BUCKET=naumio-shot-ledger-proof-2026
B2_REGION=us-east-005
SHOT_LEDGER_PROVIDER=openai
SHOT_LEDGER_OPENAI_MODEL=gpt-image-2
```

## Current Gate

The B2 key form is prepared for one private bucket, the `shot-ledger/` prefix,
read/write access, S3-compatible bucket listing, and a 90-day expiry. Key
creation and vaulting remain pending until the required action-time
confirmation.

After key creation, the next command is `scripts/proof preflight`. Paid image
generation may start only when that command returns
`ready_for_spend_approval` and the separate maximum-$0.20 spend approval is
recorded.

## Shared-Proof Note

The repository's `ops/shot-ledger.op.env.example` is intentionally excluded
from Drive mirroring because the shared-proof scanner blocks environment-style
filenames. This Markdown handoff preserves the non-secret operating contract
without weakening that protection.
