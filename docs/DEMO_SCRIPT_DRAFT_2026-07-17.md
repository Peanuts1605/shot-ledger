# Shot Ledger - 105-Second Demo Script

Status: DRAFT - record only after the real B2 proof passes.

## 0:00-0:12 - The Lonely File

"An approved AI shot often arrives as a lonely file. The next editor cannot see
what changed, how to reproduce it, or why this one won."

Show the Shot Ledger scene header and proof status.

## 0:12-0:28 - One Controlled Question

"Shot Ledger locks the subject, frame, background, and camera, then uses
Genblaze to create three takes where only light direction changes."

Show the scene lock and three generated takes.

## 0:28-0:48 - Human Decision

"The recipe records how each take was made. The reviewer adds the missing part: which take should survive, and why."

In the operator review surface, select a different take, write a visible reason, and show the receipt state change from `Sealed` to `Draft change`.

## 0:48-1:04 - The Decision Becomes An Artifact

"Resealing creates a new decision hash. The keeper, rejected siblings, exact prompt, parameters, provider, model, and human reason stay together."

The real proof never preselects a winner. Generation stops with three B2-backed review images; the keeper and concrete reason are supplied only after visual review.

Reseal and show the updated selected-take receipt.

## 1:04-1:24 - B2 Is The System Of Record

Switch to the public URL.

"B2 is the system of record, not a backup. A fresh process reloads the sealed
decision, all three images, and all three Genblaze manifests from B2. The public
view serves that verified evidence read-only."

Show `Backblaze B2`, `Hash Matches`, `Verified`, the provider/model fields, and the read-only status.

## 1:24-1:38 - A Failed Take Does Not Erase The Work

"If one provider call fails, completed siblings stay saved. The recovery view names the failed take, and retry runs only what is missing."

Show the recovery screenshot or prepared partial-run replay.

## 1:38-1:45 - Close

"Shot Ledger keeps how it was made, why it was chosen, and enough proof for the
next person to continue."

End on the keeper receipt, not a marketing slide.

## Capture Checklist

- Real provider images are visible and public-safe.
- The operator review and public read-only URL are visually distinguishable.
- Top status reads `Backblaze B2`.
- Proof scope reads `Live provider evidence reloaded from Backblaze B2`.
- Decision hash and media/provenance both pass.
- No credentials, account IDs, bucket names, or browser tabs appear.
- Final duration is under 3 minutes; target 105 seconds.

## Capture Order

1. Open on the three real B2-backed takes, with the scene lock and proof status
   visible in the first frame.
2. Move once through the take cards; do not scroll past the same UI twice.
3. Show the operator-only decision change and reseal.
4. Cut directly to the public read-only URL and the verified receipt.
5. Show the prepared partial-run recovery state as a short insert.
6. End on the keeper receipt and human reason.

## Adversarial Pre-Record Gate

- Refresh the public URL in a private browser window.
- Confirm all three images load from B2 and no local file URI is present.
- Confirm the public decision form cannot mutate the keeper.
- Download the packet and verify it opens as valid JSON.
- Tamper with a local packet copy and show the verifier rejects it; do not alter
  the public evidence.
- Confirm retry selects only failed or pending slots.
- Test every visible link at desktop and mobile widths.
- Record only after the repository, public URL, and receipt agree on provider,
  model, keeper, reason, and hashes.
