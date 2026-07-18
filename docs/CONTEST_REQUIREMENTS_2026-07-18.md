# Backblaze Generative Media Hackathon Requirements

Verified: 2026-07-18
Official page: https://backblaze-generative-media.devpost.com/

## Submission Window

- Deadline: August 3, 2026 at 5:00 PM EDT
- Winners announced: August 12, 2026
- Current decision: `BUILD_AND_SUBMIT`

## Required Product Shape

The entry must be a functional generative-media application that uses both
Backblaze B2 and Genblaze. GMI Cloud is optional; Shot Ledger uses the OpenAI
adapter through Genblaze and stores generated images, state, decisions, and
provenance in B2.

## Required Submission Evidence

- working app URL that judges can access
- code repository with setup instructions
- named AI provider and model
- explanation of meaningful B2 and Genblaze usage
- short demo video of roughly three minutes

## Judging Criteria

1. **Real-World Utility** - a practical problem for a clear audience.
2. **Production Readiness** - reliable behavior beyond a simple demo.
3. **B2 Storage and Data Orchestration** - meaningful storage, organization,
   serving, or management of media, metadata, provenance, or app assets.
4. **Use of Genblaze** - meaningful generative-media orchestration across
   providers, models, or steps.

## Shot Ledger Fit

- **Utility:** creative teams compare controlled image takes and record one
  keeper decision instead of losing rationale in chat and filenames.
- **Production readiness:** resumable generation state, selective retry,
  tamper checks, explicit human review, and fresh-process verification.
- **B2:** private durable storage for all takes, manifests, state, and the
  sealed decision, followed by a separate read-only public proof surface.
- **Genblaze:** each take is generated through the Genblaze OpenAI adapter and
  receives a SHA-256-bound provenance manifest.

## Remaining Release Gate

The synthetic preview is not contest proof. Submission still requires the
provider-backed three-take run, B2 reload verification, read-only public
deployment, demo video, and completed Devpost form.
