# Shot Ledger Submission Evidence Matrix

Updated: 2026-07-18

This matrix distinguishes implemented behavior from provider-backed contest
evidence. `PENDING` is not presented as proof.

| Claim | Status | Evidence |
|---|---|---|
| Controlled three-take comparison | VERIFIED_LOCAL | `proof/local/decision.json` and three local takes |
| Keeper plus concrete human reason | VERIFIED_LOCAL | Interactive review surface and decision packet |
| Decision tamper detection | VERIFIED_LOCAL | Automated decision and review tests |
| Image bytes and manifest verification | VERIFIED_LOCAL | Automated verification tests |
| Partial-run recovery and selective retry | VERIFIED_LOCAL | Recovery UI, state tests, desktop/mobile captures |
| Human review required before real keeper selection | VERIFIED_CODE | Finalization tests and explicit sealing command |
| Desktop review clarity | VERIFIED_LOCAL | `proof/ui/shot-ledger-desktop.png` |
| Mobile review clarity | VERIFIED_LOCAL | `proof/ui/shot-ledger-mobile-top.png` and decision capture |
| Automated test suite | VERIFIED_LOCAL | 40 Python tests and 11 Worker tests pass; Ruff, typecheck, dependency check, and Worker dry-run pass |
| Clean-checkout CI | VERIFIED_PUBLIC | https://github.com/Peanuts1605/shot-ledger/actions/runs/29661921704 |
| Public source repository | VERIFIED_PUBLIC | https://github.com/Peanuts1605/shot-ledger |
| Read-only synthetic preview | VERIFIED_PUBLIC | https://shot-ledger-preview.gigantic-stranger.workers.dev |
| Public desktop and mobile layout | VERIFIED_PUBLIC | `proof/ui/shot-ledger-public-preview-desktop-full.png` and mobile capture |
| Real generation through Genblaze | PENDING | OpenAI credential is recorded in 1Password; the read-only auth preflight and paid three-take run remain |
| Private object storage in Backblaze B2 | VERIFIED_INFRA_PARTIAL | Private `us-east-005` proof bucket created July 18 with default B2 encryption enabled; the bucket-scoped application key and authenticated preflight remain pending |
| Fresh-process reload of seven B2 objects | PENDING | Runs immediately after the real decision is sealed |
| Read-only public B2 demo | PENDING | Promote the verified Worker from synthetic preview to B2 secrets after the real receipt passes |
| Sub-three-minute demo video | PENDING | Record against the public B2 proof |
| Devpost submission | PENDING | Register and submit after links and evidence are final |

## Release Gate

The submission is ready only when every provider-backed row above moves from
`PENDING` to a reproducible path or URL. Local synthetic proof remains clearly
labeled and is never substituted for Genblaze or B2 evidence.
