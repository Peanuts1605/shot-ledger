# Shot Ledger One-Day Proof Contract

Date: 2026-07-17
Proof name: controlled_dailies_decision_packet

## Question

Can Shot Ledger preserve one controlled creative decision as a verifiable,
reloadable handoff rather than another generation gallery?

## Required Proof

1. One public-safe scene brief is locked.
2. Genblaze produces three takes with one declared variable changed.
3. All three assets and their Genblaze manifests are stored in Backblaze B2.
4. The review surface shows what stayed fixed and what changed.
5. A user selects one keeper and records a concrete reason.
6. A decision record links the keeper and rejected siblings to their manifest
   hashes and B2 objects.
7. The keeper manifest and asset hash verify.
8. A fresh app process reloads the complete scene from B2 without local state.
9. One failed take remains visible and retryable without erasing successful
   takes.

## Public-Safe Demo Brief

Create a clean tabletop campaign shot for an unbranded stainless-steel travel
mug. Keep the mug shape, handle, lid, background color, and 4:5 frame fixed.
Explore only the light direction: left window light, overhead softbox, and low
side light.

The scene avoids brands, people, client material, and protected characters.

## Decision Packet Minimum

- scene ID and brief
- locked variables
- changed variable
- three take IDs and statuses
- asset URI and SHA-256 per take
- provider, model, prompt, and parameters per take
- Genblaze manifest hash and URI per take
- keeper ID
- selection reason
- rejected sibling IDs
- creation time
- packet hash

## Pass Gates

- `LOCAL_SCHEMA_PASS`: three deterministic local assets produce valid Genblaze
  manifests and a tamper-evident decision packet.
- `REAL_PIPELINE_PASS`: at least one real provider call runs through a Genblaze
  pipeline.
- `B2_DURABILITY_PASS`: assets, manifests, and the decision record are written
  to and reloaded from B2.
- `HUMAN_HANDOFF_PASS`: a second person can answer how the keeper was made and
  why it won in under two minutes.
- `FAILURE_RECOVERY_PASS`: partial generation is visible and recoverable.

## Stop Conditions

- Genblaze or B2 is decorative rather than necessary to the working path.
- B2 reload cannot restore the full decision without hidden local data.
- The three takes do not make the changed variable understandable.
- The decision packet adds no useful information beyond a normal comment.
- The proof requires a broad editor, node canvas, team system, or asset manager.

## Explicitly Deferred

- accounts and permissions beyond the minimum proof
- teams, roles, and comments
- timeline editing
- arbitrary workflow graphs
- C2PA signing
- billing
- model marketplace
- search across many projects
- mobile-native app

## Review Decision

At the end of the proof, return exactly one product decision:

- `GO_FULL_BUILD`
- `GO_WITH_PATCH`
- `STOP_GENERIC`
- `STOP_TECHNICAL`

