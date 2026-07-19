# Shot Ledger Submission Evidence Matrix

Updated: 2026-07-18

This matrix distinguishes implemented behavior from provider-backed contest
evidence. `PENDING` is not presented as proof.

| Claim | Status | Evidence |
|---|---|---|
| Controlled three-take comparison | VERIFIED_LOCAL | `proof/local/decision.json` and three local takes |
| Keeper plus concrete human reason | VERIFIED_LOCAL | Interactive review surface and decision packet |
| Decision tamper detection | VERIFIED_LOCAL | Python reload and public Worker independently recompute the packet hash; stale exports are refused |
| Image bytes and manifest verification | VERIFIED_LOCAL | Automated verification tests |
| Partial-run recovery and selective retry | VERIFIED_LOCAL | Recovery UI, state tests, desktop/mobile captures |
| Human review required before real keeper selection | VERIFIED_CODE | Finalization tests and explicit sealing command |
| Desktop review clarity | VERIFIED_LOCAL | `proof/ui/shot-ledger-desktop.png` |
| Mobile review clarity | VERIFIED_LOCAL | `proof/ui/shot-ledger-mobile-top.png` and decision capture |
| Automated test suite | VERIFIED_LOCAL | 42 Python tests and 15 Worker tests pass; Ruff, typecheck, dependency check, and Worker dry-run pass |
| Clean-checkout CI | VERIFIED_PUBLIC | https://github.com/Peanuts1605/shot-ledger/actions/runs/29670870921 |
| Public source repository | VERIFIED_PUBLIC | https://github.com/Peanuts1605/shot-ledger |
| Read-only synthetic preview | VERIFIED_PUBLIC | https://shot-ledger-preview.gigantic-stranger.workers.dev - Worker version `2721733a-7d39-484e-b5d9-ba09ab463510`; live health, scene, download, read-only controls, and no-local-path replay passed |
| Public desktop and mobile layout | VERIFIED_PUBLIC | `proof/ui/shot-ledger-public-preview-desktop-2026-07-18.png` and `proof/ui/shot-ledger-public-preview-mobile-2026-07-18.png`; 390px mobile replay has no horizontal overflow |
| Real generation through Genblaze | PENDING_PAID_RUN | OpenAI model and credential passed the secure read-only preflight; the capped three-take run has not started |
| Private object storage in Backblaze B2 | VERIFIED_INFRA | Private `us-east-005` proof bucket, bucket-scoped credential, default encryption, and authenticated read-only preflight verified |
| Fresh-process reload of seven B2 objects | PENDING | Runs immediately after the real decision is sealed |
| Read-only public B2 demo | PENDING | Promote the verified Worker from synthetic preview to B2 secrets after the real receipt passes |
| Sub-three-minute demo video | PENDING | Record against the public B2 proof |
| Devpost registration | VERIFIED_EXTERNAL | Registered as a solo entrant on 2026-07-18; Backblaze account email and Genblaze repository star confirmed |
| Devpost project draft | CAPTCHA_PENDING | Project creation is open at the registered hackathon submission manager; the visual CAPTCHA must be cleared before the draft record is created |
| Devpost field copy | READY_DRAFT | `docs/DEVPOST_FIELD_MAP_2026-07-18.md` contains paste-ready submission fields and quarantines the three real-proof URLs |
| Naumio YouTube publishing packet | READY_DRAFT | `docs/NAUMIO_YOUTUBE_PUBLISHING_PACKET_2026-07-18.md` contains final title, description, settings, thumbnail direction, and story beats |
| Devpost final submission | PENDING | Submit after the real app, B2 receipt, and public demo video URLs are final |

Official deadline and judging criteria are reconciled in
`docs/CONTEST_REQUIREMENTS_2026-07-18.md`.

## Release Gate

The submission is ready only when every provider-backed row above moves from
`PENDING` to a reproducible path or URL. Local synthetic proof remains clearly
labeled and is never substituted for Genblaze or B2 evidence.
