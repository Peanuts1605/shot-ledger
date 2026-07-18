# Shot Ledger - Devpost Submission Draft

Status: DRAFT - real Genblaze/B2 evidence, public URL, and video still pending.

## Tagline

The approved AI shot, its rejected siblings, and the reason it won.

## One-Sentence Pitch

Creative teams lose the reasoning behind an approved AI shot. Shot Ledger keeps the winner, rejected takes, exact recipe, and human reason together as a verifiable B2 receipt.

## Inspiration

Generative media makes it easy to produce another take. It does not make it easy to explain what changed, recover the exact recipe, or understand why one result was approved. Creative teams often hand off only the final file, while the rejected alternatives, provenance, and human judgment disappear across chats and folders.

Shot Ledger treats approval as a production artifact rather than a comment.

## What It Does

1. Locks one scene brief and the variables that must remain fixed.
2. Generates three takes while changing one named creative variable.
3. Presents the takes side by side for review.
4. Records one keeper and a concrete human reason.
5. Packages the keeper, rejected siblings, prompt, parameters, provider/model, Genblaze manifests, media hashes, and human decision into one B2-backed receipt.

The real proof does not preselect a winning take. Generation stops after the three B2-backed images are available for visual review; only then can a reviewer name the keeper and seal the reason it won.

The result answers two questions together: **How was this made? Why did we choose it?**

## How We Built It

- Python powers the generation, storage, verification, and review service.
- Genblaze runs the controlled image pipeline and emits provenance manifests.
- Genblaze's OpenAI adapter and GPT Image 2 are selected for the contest proof; the GMI Cloud route remains supported but is not required.
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
- Selective retry for partial generations.
- A fresh-process B2 reload verifier.
- A public-safe, synthetic fallback that never impersonates real provider proof.

## What We Learned

Provenance becomes useful only when it travels with a human decision. A perfect generation log cannot explain why a creative lead chose one take, and a comment cannot reconstruct the generation. The durable handoff needs both.

## What's Next

- Add authenticated multi-project workspaces.
- Support controlled video and audio dailies through the same receipt model.
- Add side-by-side difference views for motion, timing, and sound.
- Export decision packets into existing DAM and editorial workflows.

## Links

- Source: https://github.com/Peanuts1605/shot-ledger
- Public synthetic preview: https://shot-ledger-preview.gigantic-stranger.workers.dev
- Public app: PENDING_REAL_B2_DEPLOY
- Demo video: PENDING
- B2 verification receipt: PENDING_REAL_PROOF

## Technologies

Python, Genblaze, Backblaze B2, OpenAI GPT Image 2, Cloudflare Workers, TypeScript, HTML, CSS, JavaScript
