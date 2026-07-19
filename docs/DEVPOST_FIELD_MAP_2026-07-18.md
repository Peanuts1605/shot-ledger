# Shot Ledger - Devpost Field Map

Updated: 2026-07-18

Status: READY_DRAFT. Paste these fields after the Devpost project record exists.
Replace only the three `PENDING_REAL_PROOF` values after the verified Genblaze
and B2 run. The synthetic preview is not the contest proof.

## Identity

**Project name**

Shot Ledger

**Tagline**

The approved AI shot, the takes it beat, and the reason it won.

**One-sentence pitch**

Shot Ledger keeps the approved AI shot, the takes it beat, the exact generation
recipe, and the human reason it won together as one verifiable B2 decision
packet.

**Submission category**

Generative media production workflow / creative operations.

**Team**

Solo entrant: Maggy Alvarado.

**Creator contribution**

I shaped the product direction, tested whether the workflow made sense to a
non-technical creative lead, and drove the final product and submission
decisions. I used AI-assisted development to build and test the implementation,
then required reproducible receipts for every claim in the demo.

## Inspiration

Generative media makes it easy to create another take. It does not make it easy
to remember what changed, recover the exact recipe, or explain why one result
was approved. In a normal handoff, the final file survives while the rejected
alternatives, provenance, and creative judgment disappear across chats,
downloads, and folders.

That is a quiet but expensive loss. The next editor cannot reliably reproduce,
defend, or branch the work. Shot Ledger treats approval as a production
artifact, not a comment that gets separated from the media.

## What It Does

Shot Ledger locks one scene brief, uses Genblaze to generate three takes while
changing one named creative variable, and stores every take, manifest, and
partial-run checkpoint in Backblaze B2. A human then reviews the B2-backed takes
side by side, chooses one keeper, and records an image-specific reason.

The app seals the keeper, rejected siblings, prompt, parameters,
provider/model, Genblaze manifests, media hashes, and human decision into one B2
decision packet. A fresh process reloads the packet, all three images, and all
three manifests from B2 alone and verifies their hashes.

The result answers two questions together: **How was this made? Why did we
choose it?**

Shot Ledger is not a prompt gallery and it does not ask a model to grade its own
output. Generation supplies the candidates and machine provenance. A human
supplies the creative decision.

## How We Built It

Python powers generation, storage, verification, and the operator review
service. Genblaze runs a controlled three-take pipeline through its OpenAI image
adapter and emits canonical provenance manifests. GPT Image 2 generates the
contest proof. Backblaze B2 stores the images, manifests, partial-run state, and
sealed decision packet.

The public review surface runs on Cloudflare Workers and serves the verified B2
evidence read-only. It recomputes the decision hash before serving media or
packet exports, even if an old stored receipt says the packet passed. An
authenticated operator can choose and reseal a keeper; an anonymous visitor
cannot overwrite the shared decision.

If a provider call fails, successful sibling takes remain in B2. Retry generates
only failed or pending takes, preserving the original assets, manifests, and
generation cost.

## How Backblaze B2 Is Used

B2 is the system of record, not a backup destination. The workflow writes
generated media, Genblaze manifests, retry state, and the sealed decision packet
to a private B2 bucket. A separate verification process then reloads seven proof
objects from B2: one decision packet, three images, and three manifests. It
verifies every hash before the public edge serves the evidence.

This makes partial runs recoverable and finished handoffs portable. The next
reviewer does not need the original laptop, browser session, or chat to
understand or reproduce the decision.

## How Genblaze Is Used

Genblaze orchestrates the controlled three-take pipeline, calls the provider
through its official OpenAI adapter, writes canonical provenance manifests
through an object-storage sink, and gives every take the same durable recipe
shape. Shot Ledger changes one declared variable across the runs while holding
the scene contract fixed, then consumes Genblaze's manifests directly when it
builds and verifies the decision packet.

## Challenges

- Keeping the comparison genuinely controlled instead of changing several
  visual variables at once.
- Separating a valid decision hash from proof that the underlying image bytes
  and provenance manifests still match.
- Recovering partial provider runs without discarding successful paid takes.
- Presenting enough provenance for trust without turning the review surface
  into an infrastructure console.

## Accomplishments

- Built a functional desktop and mobile review workflow.
- Created a tamper-evident keeper/rejection decision packet.
- Added byte-level image verification plus Genblaze manifest and recipe checks.
- Added selective retry that preserves completed paid takes.
- Built a fresh-process B2 reload verifier.
- Built a public edge that independently recomputes the decision hash.
- Kept the public B2 surface read-only by default.
- Kept synthetic fallback evidence visibly labeled so it cannot impersonate
  provider-backed proof.

## What We Learned

Provenance becomes useful only when it travels with a human decision. A perfect
generation log cannot explain why a creative lead chose one take, and a comment
cannot reconstruct the generation. The durable handoff needs both.

We also learned that recovery belongs in the product promise. A failed third
take should not erase the two successful takes already paid for and stored.

## What's Next

The next useful step is not a larger editor. It is a handoff test with working
creative teams, followed by exports into the asset and approval systems they
already use. The same receipt model can later support controlled video and
audio dailies without changing the human-decision boundary.

## Links

- Source code: https://github.com/Peanuts1605/shot-ledger
- Public synthetic preview: https://shot-ledger-preview.gigantic-stranger.workers.dev
- Public B2-backed app: `PENDING_REAL_PROOF`
- Public demo video: `PENDING_REAL_PROOF`
- B2 verification receipt: `PENDING_REAL_PROOF`

## Built With

Backblaze B2, Genblaze, OpenAI GPT Image 2, Python, Cloudflare Workers,
TypeScript, HTML, CSS, and JavaScript.

## Final Paste Gate

Before publishing the Devpost submission:

1. Replace all three `PENDING_REAL_PROOF` values with verified public URLs.
2. Confirm the app URL opens in a private browser window.
3. Confirm the video is public, plays without sign-in, and is under three
   minutes.
4. Confirm the repository, app, video, and B2 receipt name the same provider,
   model, keeper, reason, and hashes.
5. Do not paste credentials, bucket secrets, account IDs, or local file paths.
