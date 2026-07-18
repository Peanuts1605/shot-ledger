# Shot Ledger Architecture

Shot Ledger separates generation, human approval, and verification so no layer
can quietly impersonate another.

```mermaid
flowchart TD
    A["Locked brief + one changed variable"] --> B["Genblaze orchestration"]
    B --> C1["Take A image + manifest"]
    B --> C2["Take B image + manifest"]
    B --> C3["Take C image + manifest"]
    C1 --> D["Backblaze B2 system of record"]
    C2 --> D
    C3 --> D
    B --> E["Hashed generation state"]
    E --> D
    D --> F["Three-take visual review"]
    F --> G["Explicit keeper + concrete reason"]
    G --> H["Tamper-evident decision packet"]
    H --> D
    D --> I["Fresh-process reload verifier"]
    I --> J["Decision hash result"]
    I --> K["Media + manifest result"]
    D --> L["Cloudflare Worker: read-only public evidence"]
```

## Durable Objects

| Object | Purpose |
|---|---|
| Three generated images | The actual candidates under review |
| Three Genblaze manifests | Provider, model, prompt, parameters, and provenance |
| Generation state | Attempts, partial failures, preserved successes, and retry scope |
| Decision packet | Keeper, rejected siblings, human reason, and packet hash |
| Reload receipt | Independent verification of decision, media, and manifests from B2 |

Cloudflare hosts only the review surface and signs read-only B2 requests at the
edge. It does not replace B2 as the durable system of record or Genblaze as the
generation and provenance layer.

## Sponsor-Critical Path

1. **Genblaze orchestration:** runs the three controlled provider calls and
   creates canonical provenance manifests.
2. **Backblaze B2 durability:** stores media, manifests, retry state, the sealed
   human decision, and the independent reload receipt.
3. **Shot Ledger decision layer:** joins machine recipe to human judgment without
   allowing generation to choose its own winner.
4. **Read-only edge:** exposes the verified packet to judges without exposing
   credentials or allowing public mutation.

Removing Genblaze loses the consistent orchestration and provenance boundary.
Removing B2 loses partial-run durability, fresh-process reconstruction, and the
portable evidence handoff. Both are required by the working product path.

## Trust Rules

- Generation stops before keeper selection.
- A partial run cannot be sealed.
- Retry touches only failed or pending takes.
- Decision integrity and media/provenance integrity are reported separately.
- The public Worker recomputes the canonical decision hash before serving B2
  media or packet exports; it does not trust a stored verification flag alone.
- The public edge serves B2 media only when the decision packet and independent verification receipt match.
- The public deployment is read-only by default.
- Credentials and signed URLs never enter the decision packet.

## Execution Path

1. `python -m shot_ledger.real_proof` generates and stores the three takes.
2. The B2-backed review images are inspected.
3. `python -m shot_ledger.finalize_real_proof` seals an explicit keeper and reason.
4. A separate process reloads all seven proof objects from B2 and writes the verification receipt.
5. The same packet is served through the read-only public review surface.
