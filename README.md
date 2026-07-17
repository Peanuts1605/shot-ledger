# Shot Ledger

Controlled dailies for generative media.

Shot Ledger gives every approved AI shot a portable handoff that answers two
questions together: **How was this made? Why did we choose it?**

The working product loop is deliberately narrow:

1. Lock one scene brief.
2. Generate three takes while changing one creative variable.
3. Compare the takes side by side.
4. Select one keeper and record the reason.
5. Save the keeper, rejected siblings, Genblaze manifests, hashes, and human
   decision as one B2-backed decision packet.

This repository begins with a local, zero-credential proof of the decision
packet. The contest proof must later execute real generation through Genblaze,
store assets and manifests in Backblaze B2, and reload the ledger from B2.

## Local Proof

```bash
python3.12 -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/python -m shot_ledger.proof_local
.venv/bin/pytest
```

The generated proof is written to `proof/local/`.

## Review Surface

After generating the local proof, start the review app:

```bash
.venv/bin/python -m shot_ledger.server
```

Open `http://127.0.0.1:4173`. The app compares the controlled takes, records a
keeper and concrete selection reason, recomputes the tamper-evident packet, and
exports the complete handoff.

## Real Genblaze to B2 Proof

The real proof reads credentials only from environment variables. Install the
optional provider and storage packages, configure the names in `.env.example`,
and run:

```bash
.venv/bin/pip install -e '.[dev,real]'
.venv/bin/python -m shot_ledger.real_proof
```

The command generates three controlled takes through Genblaze, stores every
asset and manifest in B2, writes the decision packet, then creates a fresh B2
client and reloads the packet without local state.


## Product Documents

- `docs/SHOT_LEDGER_PRODUCT_BET_2026-07-17.md`
- `docs/SHOT_LEDGER_ONE_DAY_PROOF_CONTRACT_2026-07-17.md`

## Contest

Backblaze Generative Media Hackathon: Build with Genblaze on B2.

- Deadline: August 3, 2026 at 5:00 PM ET
- Required: working app, repository, English description, and public demo under
  three minutes
- Judging: real-world utility, production readiness, B2 orchestration, and
  meaningful Genblaze use, weighted equally
