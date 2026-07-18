# Shot Ledger - 90-Second Demo Script

Status: DRAFT - record only after the real B2 proof passes.

## 0:00-0:12 - The Problem

"AI can make another shot in seconds. The hard part is remembering what changed, why one take won, and whether another person can continue the work without the original chat."

Show the Shot Ledger scene header and proof status.

## 0:12-0:28 - Controlled Dailies

"Shot Ledger locks the subject, frame, background, and camera, then asks Genblaze for three takes where only light direction changes."

Show the scene lock and three generated takes.

## 0:28-0:48 - Human Decision

"The recipe records how each take was made. The reviewer adds the missing part: which take should survive, and why."

In the operator review surface, select a different take, write a visible reason, and show the receipt state change from `Sealed` to `Draft change`.

## 0:48-1:02 - Durable Receipt

"Resealing creates a new decision hash. The keeper, rejected siblings, exact prompt, parameters, provider, model, and human reason stay together."

The real proof never preselects a winner. Generation stops with three B2-backed review images; the keeper and concrete reason are supplied only after visual review.

Reseal and show the updated selected-take receipt.

## 1:02-1:18 - Public B2 And Genblaze Proof

Switch to the public URL.

"The public view is intentionally read-only. It reloads the sealed decision, all three private images, and all three Genblaze manifests from Backblaze B2. Shot Ledger verifies the decision hash, actual media bytes, manifest hashes, and recorded recipe separately."

Show `Backblaze B2`, `Hash Matches`, `Verified`, the provider/model fields, and the read-only status.

## 1:18-1:28 - Honest Failure Recovery

"If one provider call fails, completed siblings stay saved. The recovery view names the failed take, and retry runs only what is missing."

Show the recovery screenshot or prepared partial-run replay.

## 1:28-1:30 - Close

"Shot Ledger: how it was made, why it was chosen, and enough proof to continue."

End on the keeper receipt, not a marketing slide.

## Capture Checklist

- Real provider images are visible and public-safe.
- The operator review and public read-only URL are visually distinguishable.
- Top status reads `Backblaze B2`.
- Proof scope reads `Live provider evidence reloaded from Backblaze B2`.
- Decision hash and media/provenance both pass.
- No credentials, account IDs, bucket names, or browser tabs appear.
- Final duration is under 3 minutes; target 90 seconds.
