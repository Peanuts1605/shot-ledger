# Shot Ledger - 90-Second Demo Script

Status: DRAFT - record only after the real B2 proof passes.

## 0:00-0:12 - The Problem

"AI can make another shot in seconds. The hard part is remembering what changed, why one take won, and whether another person can continue the work without the original chat."

Show the Shot Ledger scene header and proof status.

## 0:12-0:28 - Controlled Dailies

"Shot Ledger locks the subject, frame, background, and camera, then asks Genblaze for three takes where only light direction changes."

Show the scene lock and three generated takes.

## 0:28-0:45 - Human Decision

"The recipe records how each take was made. The reviewer adds the missing part: which take should survive, and why."

Select a different take, write a visible reason, and show the receipt state change from `Sealed` to `Draft change`.

## 0:45-1:00 - Durable Receipt

"Resealing creates a new decision hash. The keeper, rejected siblings, exact prompt, parameters, provider, model, and human reason stay together."

The real proof never preselects a winner. Generation stops with three B2-backed review images; the keeper and concrete reason are supplied only after visual review.

Reseal and show the updated selected-take receipt.

## 1:00-1:15 - B2 And Genblaze Proof

"The public demo reloads the decision, all three private images, and all three Genblaze manifests from Backblaze B2. Shot Ledger verifies the decision hash, the actual media bytes, the manifest hashes, and the recorded recipe separately."

Show `Backblaze B2`, `Hash Matches`, `Verified`, and the provider/model fields.

## 1:15-1:27 - Honest Failure Recovery

"If one provider call fails, completed siblings stay saved. The recovery view names the failed take, and retry runs only what is missing."

Show the recovery screenshot or prepared partial-run replay.

## 1:27-1:30 - Close

"Shot Ledger: how it was made, why it was chosen, and enough proof to continue."

End on the keeper receipt, not a marketing slide.

## Capture Checklist

- Real provider images are visible and public-safe.
- Top status reads `Backblaze B2`.
- Proof scope reads `Live provider evidence reloaded from Backblaze B2`.
- Decision hash and media/provenance both pass.
- No credentials, account IDs, bucket names, or browser tabs appear.
- Final duration is under 3 minutes; target 90 seconds.
