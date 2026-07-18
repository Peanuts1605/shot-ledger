# Shot Ledger Judge-First Submission Packet

Date: 2026-07-18
Status: READY_FOR_REAL_PROOF

## Ten-Second Read

**Problem:** An approved AI shot usually loses the takes, recipe, and creative
reason that produced it.

**Outcome:** Shot Ledger keeps the approved shot, the takes it beat, the exact
Genblaze recipe, and the human reason it won as one verified B2 decision packet.

**Difference:** Generation does not grade itself. Genblaze supplies controlled
takes and machine provenance; a human supplies the keeper decision; B2 makes the
complete handoff durable and independently reloadable.

## Rubric Map

| Criterion | Judge-visible answer | Required proof |
|---|---|---|
| Real-World Utility | A creative lead can hand another person both the recipe and rationale for an approved shot. | Three-take review, keeper reason, downloaded packet |
| Production Readiness | Partial provider runs preserve completed takes; retry generates only missing work; public review is read-only. | Recovery state, selective retry test, public mutation rejection |
| B2 Storage and Data Orchestration | B2 is the system of record for images, manifests, retry state, decision packet, and reload receipt. | Private bucket objects, fresh-process seven-object reload, public signed retrieval |
| Use of Genblaze | Genblaze runs each controlled take and writes canonical provenance manifests through the storage sink. | Real run receipt, three manifests, provider/model shown in UI |

## First-Minute Storyboard

1. **0-12 seconds:** Show the approved shot beside the takes it beat. State the
   lonely-file problem.
2. **12-28 seconds:** Show what stayed fixed and the single variable that moved.
3. **28-48 seconds:** Select a keeper and give one visible, image-specific
   reason.
4. **48-60 seconds:** Reseal and show how + why together in one receipt.
5. **After 60 seconds:** Prove B2 reload, Genblaze provenance, read-only public
   access, and partial-run recovery.

## Evidence Order

1. Public B2-backed review, desktop
2. Three controlled real takes with scene lock visible
3. Sealed keeper receipt with concrete reason
4. Genblaze provider/model and manifest verification
5. Fresh-process B2 reload receipt
6. Partial-run recovery and selective retry
7. Mobile public review
8. GitHub CI and reproducible setup

## Submission Field Values

- **Project name:** Shot Ledger
- **Tagline:** The approved AI shot, the takes it beat, and the reason it won.
- **Category:** Generative image workflow / provenance-aware creator tool
- **Provider:** OpenAI
- **Model:** GPT Image 2
- **Orchestration:** Genblaze OpenAI adapter and object-storage sink
- **Storage:** Private Backblaze B2 bucket with read-only public retrieval
- **Repository:** https://github.com/Peanuts1605/shot-ledger
- **Working app:** PENDING_REAL_PROOF
- **Demo video:** PENDING_REAL_PROOF

## Final Claim Gate

Do not replace `PENDING_REAL_PROOF` until all of these agree:

- three real Genblaze manifests;
- three B2 image objects;
- sealed keeper and concrete human reason;
- seven-object fresh-process B2 reload;
- public read-only URL;
- repository HEAD and passing CI;
- final video showing the same keeper, model, reason, and proof state.

## Decision

`READY_FOR_SCOPED_B2_PREFLIGHT`
