# Shot Ledger Real Proof Runbook

Date: 2026-07-18
Status: READY_FOR_SCOPED_CREDENTIAL

This runbook keeps the first paid proof narrow, reproducible, and honest. It
contains no credentials.

## Infrastructure State

- Backblaze account: authenticated
- B2 region: `us-east-005`
- Proof bucket: private
- Default B2 encryption: enabled
- Object prefix: `shot-ledger/`
- Genblaze assets and manifests: `shot-ledger/genblaze/`
- Proof credential: pending creation as a 90-day, bucket-only read/write key
  with the `shot-ledger/` file prefix and **List all bucket names** enabled.
  Backblaze requires that capability for S3-compatible `HeadBucket` checks;
  object access remains restricted to the proof bucket and prefix.
- Public Worker credential: deferred until proof passes; it must be a separate
  read-only key

## Provider Plan

- Pipeline: Genblaze
- Adapter: `genblaze-openai`
- Provider model: `gpt-image-2`
- Output: one PNG per take
- Size: `1024x1280` (4:5)
- Quality: `medium`
- Takes: three, changing only `light_direction`

The current OpenAI calculator lists medium GPT Image 2 output at roughly
$0.041-$0.053 for nearby standard sizes. The three custom 4:5 outputs should
therefore stay below a conservative $0.20 generation cap, excluding only
negligible prompt-token cost. Paid generation still requires explicit spend
approval after the read-only preflight passes.

## Execution Order

1. Create and vault the bucket-only proof credential.
2. Store the B2 and OpenAI credentials in 1Password. Create
   `~/.config/shot-ledger/proof.env` from
   `ops/shot-ledger.op.env.example`, using only `op://` secret references, and
   set its file mode to `600`. Literal credentials never enter the repo or the
   reference file.
3. Run the read-only preflight:

   ```bash
   scripts/proof preflight
   ```

4. Require the receipt state `ready_for_spend_approval`.
5. After explicit approval for a maximum $0.20 provider charge, run:

   ```bash
   scripts/proof generate
   ```

6. Review all three B2-backed images in `proof/real/review/` and choose the
   keeper using a visible, image-specific reason.
7. Seal the decision with `scripts/proof finalize`.
8. Verify that the separate process reloads the decision, three assets, and
   three Genblaze manifests from B2.
9. Run the verifier and the full local quality gates again.
10. Create a separate read-only B2 credential for the public Worker, deploy,
    and test the public proof on desktop and mobile.

## Evidence Required Before Promotion

- preflight receipt with provider model and B2 bucket verification
- three Genblaze manifests and three image hashes
- generation-state receipt showing all takes succeeded
- human keeper reason and sealed decision hash
- fresh-process B2 reload receipt
- failure-recovery proof
- read-only public URL and desktop/mobile captures
- sub-three-minute demo video

## Current Decision

`CONTINUE_TO_SCOPED_CREDENTIAL`

## Pre-Spend Adversarial Finding

Genblaze owns and closes each run-scoped object-storage sink. The first version
of the proof reused one sink for all three paid takes, which could leave the
second and third takes using a closed B2 client. The implementation now creates
one fresh Genblaze sink per take while keeping the separate generation-state
backend open for checkpointing and review. A regression test verifies three
distinct sinks.

The same review found a second paid-run edge: an infrastructure exception after
generation but before manifest completion could stop the process while leaving
the take labeled `pending`. Shot Ledger now checkpoints that take as `failed`
and halts before any later take starts. The regression test preserves the first
successful sibling, records the second failure, leaves the third pending, and
brings the suite to 40 passing tests.
