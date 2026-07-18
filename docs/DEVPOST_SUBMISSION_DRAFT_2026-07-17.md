# Shot Ledger - Devpost Submission Draft

Status: CONTENT-READY - replace only the three `PENDING_REAL_PROOF` fields after
the verified Genblaze/B2 run. Do not submit the synthetic preview as real proof.

## Tagline

The approved AI shot, the takes it beat, and the reason it won.

## One-Sentence Pitch

An approved AI shot often arrives as a lonely file. Shot Ledger keeps the
keeper, the takes it beat, the exact generation recipe, and the human reason it
won together as one verifiable B2 decision packet.

## Inspiration

Generative media makes it easy to produce another take. It does not make it
easy to remember what changed, recover the exact recipe, or explain why one
result was approved. In a normal handoff, the final file survives while the
rejected alternatives, provenance, and creative judgment disappear across
chats, downloads, and folders.

That is a quiet but expensive loss. The next editor cannot reliably reproduce,
defend, or branch the work. Shot Ledger treats approval as a production
artifact, not a comment that gets separated from the media.

## What It Does

1. Locks one scene brief and the variables that must remain fixed.
2. Uses Genblaze to generate three takes while changing one named creative
   variable.
3. Stores every take, manifest, and partial-run checkpoint in Backblaze B2.
4. Presents the B2-backed takes side by side for human review.
5. Records one keeper and a concrete, image-specific reason.
6. Seals the keeper, rejected siblings, prompt, parameters, provider/model,
   Genblaze manifests, media hashes, and human decision into one B2 decision
   packet.

The real proof does not preselect a winning take. Generation stops after the three B2-backed images are available for visual review; only then can a reviewer name the keeper and seal the reason it won.

The result answers two questions together: **How was this made? Why did we
choose it?**

Shot Ledger is not another prompt gallery and it does not ask a model to grade
its own output. Generation supplies the candidates and machine provenance. A
human supplies the creative decision.

## Why Backblaze B2 Matters

B2 is the system of record, not a backup destination. The real workflow writes
generated media, Genblaze manifests, retry state, and the sealed decision packet
to a private B2 bucket. A fresh verification process then reloads the decision,
all three images, and all three manifests from B2 alone and verifies their
hashes. The public review surface serves that sealed evidence read-only.

This makes partial runs recoverable and finished handoffs portable. A successful
take does not disappear because a later provider call failed, and a reviewer
does not need the original laptop or chat to understand the decision.

## Why Genblaze Matters

Genblaze orchestrates the controlled three-take pipeline through its OpenAI
adapter, writes canonical provenance manifests through an object-storage sink,
and gives every take the same durable recipe shape. Shot Ledger changes one
declared variable across the three runs while holding the scene contract fixed.
The app consumes those manifests directly when it builds and verifies the
decision packet.

## How We Built It

- Python powers the generation, storage, verification, and review service.
- Genblaze runs the controlled image pipeline and emits provenance manifests.
- Genblaze's OpenAI adapter and GPT Image 2 power the contest proof; the same
  orchestration boundary also supports a GMI Cloud route.
- Backblaze B2 stores generated images, Genblaze manifests, partial-run state, and the final decision packet.
- A separate verification process reloads all seven proof objects from B2: one decision packet, three images, and three manifests.
- The review UI distinguishes the decision hash from media/provenance verification and makes local synthetic evidence visibly different from real B2 evidence.

## Reliability And Recovery

Shot Ledger does not call a partial run complete. If one take fails, successful siblings remain in B2 and the generation-state receipt names the failed slot. The retry command generates only failed or pending takes, preserving original assets and provenance while avoiding duplicate generation cost.

The public B2 demo is read-only by default, so anonymous visitors cannot overwrite the shared keeper.

## Challenges

- Keeping the comparison genuinely controlled rather than changing several visual variables at once.
- Separating a valid decision hash from proof that the underlying media bytes and manifests still match.
- Recovering partial provider runs without throwing away successful, paid generations.
- Presenting enough provenance for trust without turning the review surface into an infrastructure console.

## Accomplishments

- A functional desktop and mobile review workflow.
- A tamper-evident keeper/rejection decision packet.
- Byte-level image verification plus Genblaze manifest and recipe verification.
- Selective retry that preserves completed, paid takes.
- A fresh-process B2 reload verifier.
- A read-only public review surface.
- A public-safe synthetic fallback that is visibly labeled and never
  impersonates provider-backed evidence.

## What We Learned

Provenance becomes useful only when it travels with a human decision. A perfect generation log cannot explain why a creative lead chose one take, and a comment cannot reconstruct the generation. The durable handoff needs both.

## What's Next

The next useful step is not a larger editor. It is a handoff test with working
creative teams, followed by export into the asset and approval systems they
already use. The same receipt model can later support controlled video and
audio dailies without changing the human-decision boundary.

## Links

- Source: https://github.com/Peanuts1605/shot-ledger
- Public synthetic preview: https://shot-ledger-preview.gigantic-stranger.workers.dev
- Public app: PENDING_REAL_PROOF
- Demo video: PENDING_REAL_PROOF
- B2 verification receipt: PENDING_REAL_PROOF

## Technologies

Python, Genblaze, Backblaze B2, OpenAI GPT Image 2, Cloudflare Workers, TypeScript, HTML, CSS, JavaScript
