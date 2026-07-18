# Shot Ledger Product Bet

Date: 2026-07-17
Decision window: one-day proof before a full contest build

## Bet

Build a director-facing workspace that turns uncontrolled AI variations into a
reviewable creative decision.

One scene brief produces three takes where one creative variable changes. A
human chooses the keeper and records why. Shot Ledger preserves the chosen take,
rejected siblings, exact generation recipe, Genblaze provenance, and decision
rationale as one portable B2-backed handoff.

## Product Truth

Shot Ledger gives every approved AI shot a portable handoff that answers two
questions together: **How was this made? Why did we choose it?**

This is not a generic media generator, prompt history, authenticity checker, or
node canvas. Genblaze already records machine provenance. Shot Ledger adds the
missing human decision and makes controlled comparison the primary workflow.

## Audience

Primary: a solo creative director, editor, or small production team generating
visual options for a client or campaign.

The user currently loses time because the final asset, its generation recipe,
the rejected alternatives, and the approval rationale live in different tools.

## Product Contract

- One brief: scene, subject, non-negotiables, and intended use.
- One test variable: framing, lighting, motion, or model.
- Three takes: a baseline plus two controlled alternatives.
- One human decision: select the keeper and record a specific reason.
- One decision packet: keeper, rejected siblings, source, prompts, parameters,
  manifests, hashes, rationale, and replay data.
- One return action: reopen the packet and branch from the keeper.

## Competitive Boundary

- Scenario already supports batch generation, search, and reusable settings.
- ComfyUI already preserves reproducible node workflows.
- Frame.io already supports comments, versions, and approvals.
- Content Credentials already establishes media origin.
- Weights & Biases already tracks technical artifact lineage.

Shot Ledger must win on the combined handoff: machine recipe plus human reason,
presented as a compact visual decision rather than a production graph.

## Success Tests

Judge:

- Understands the problem and outcome in 10 seconds.
- Sees three controlled takes, one keeper, and one decision packet in 60 seconds.
- Can explain why B2 is operationally necessary and why Genblaze is doing real
  orchestration.
- Sees the app reload the complete decision from durable storage.

User:

- Creates or opens a scene without learning a node system.
- Understands exactly what changed between the three takes.
- Selects a keeper and states why in under two minutes.
- Hands the packet to another person who can recover both recipe and rationale.
- Can branch again without reconstructing the project from memory.

## Technical Spine

1. Genblaze creates three controlled takes from one locked base brief.
2. `ObjectStorageSink` writes assets and canonical manifests to Backblaze B2.
3. Shot Ledger writes a decision record that references all three manifest
   hashes and marks the keeper.
4. The app reloads the complete contact sheet and decision from B2.
5. Hash verification confirms the keeper still matches its manifest.

## Bet Size

- Available initial stake: one focused build day.
- Paid generation stake before proof: zero.
- First real generation stake after local proof: three medium-quality images
  through a supported Genblaze provider, after explicit spend approval.
- Probability of a working local decision packet: 90%.
- Provider and Backblaze accounts are verified; the remaining proof risk is
  scoped credential setup and the live three-take run.
- Probability of eligibility after a working hosted app: 90%.
- Probability of 60-second judge comprehension: 85%.
- Probability that a target user wants a second scene: 55% before playtesting.
- Prize placement estimate: 7% before product testing and field visibility.

## Most Important Unknown

Does recording the selection reason and rejected alternatives create enough
handoff value to beat a normal generation history plus comments?

## Evidence That Increases The Bet

- A second person can recover the keeper, source, recipe, and decision in under
  two minutes without coaching.
- A creator says the packet replaces a manual folder, spreadsheet, or chat
  handoff they already maintain.
- Reloading from B2 alone restores the complete decision state.
- Controlled single-variable takes produce a clearer decision than arbitrary
  prompt variations.

## Falsifier

Stop if four of five target creators can already use their current tools to
recover a chosen shot, source, prompt, model, settings, rejected alternatives,
and selection reason, then share that complete handoff in under two minutes.

Also stop if the reason field becomes ceremonial text that does not help another
person reproduce, approve, or branch the work.

## Decision

GO_WITH_PATCH.

Build the one-day proof. Do not commit to a full contest entry until the real
Genblaze-to-B2 chain and the decision-handoff test both pass.
