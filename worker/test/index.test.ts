import { AwsClient } from "aws4fetch";
import { afterEach, describe, expect, it, vi } from "vitest";

import worker, {
  buildPublicScene,
  keyFromDurableUrl,
  receiptMatchesDecision,
} from "../src/index";

function localEnv(): Env {
  return {
    SCENE_ID: "public-safe-travel-mug-001",
    ASSETS: {
      fetch: async (input: RequestInfo | URL) => {
        const url = new URL(input instanceof Request ? input.url : input.toString());
        return new Response(JSON.stringify({ path: url.pathname }), {
          headers: { "Content-Type": "application/json" },
        });
      },
      connect: () => {
        throw new Error("not used");
      },
    },
    B2_APP_KEY: "",
    B2_BUCKET: "",
    B2_KEY_ID: "",
    B2_REGION: "",
  };
}

function b2Env(): Env {
  return {
    ...localEnv(),
    B2_APP_KEY: "secret-for-test",
    B2_BUCKET: "shot-ledger-test",
    B2_KEY_ID: "key-for-test",
    B2_REGION: "us-east-005",
  };
}

function mockB2Objects({ packetHash = "packet-123" }: { packetHash?: string } = {}) {
  const decision = {
    packet_hash: "packet-123",
    takes: ["take-a", "take-b", "take-c"].map((takeId) => ({
      asset_uri: `https://s3.us-east-005.backblazeb2.com/shot-ledger-test/media/${takeId}.png`,
      take_id: takeId,
    })),
  };
  const verification = {
    decision_hash_matches: true,
    media_integrity: { status: "verified", verified: true },
    packet_hash: packetHash,
    verified: true,
  };
  const generationState = {
    slots: ["take-a", "take-b", "take-c"].map((takeId) => ({
      status: "succeeded",
      take_id: takeId,
    })),
  };
  return vi.spyOn(AwsClient.prototype, "fetch").mockImplementation(async (input) => {
    const url = new URL(input instanceof Request ? input.url : input.toString());
    const path = url.pathname;
    if (path.endsWith("/decision.json")) return Response.json(decision);
    if (path.endsWith("/verification.json")) return Response.json(verification);
    if (path.endsWith("/generation-state.json")) return Response.json(generationState);
    if (path.endsWith("/media/take-a.png")) {
      return new Response(new Uint8Array([1, 2, 3]), {
        headers: { "Content-Type": "image/png" },
      });
    }
    return new Response("missing", { status: 404 });
  });
}

afterEach(() => {
  vi.restoreAllMocks();
});

describe("Shot Ledger edge", () => {
  it("serves a read-only health receipt", async () => {
    const response = await worker.fetch(
      new Request("https://example.test/healthz"),
      localEnv(),
    );

    expect(response.status).toBe(200);
    expect(await response.json()).toEqual({
      mode: "local",
      status: "ok",
      write_enabled: false,
    });
  });

  it("refuses public decision writes", async () => {
    const response = await worker.fetch(
      new Request("https://example.test/api/decision", { method: "POST" }),
      localEnv(),
    );

    expect(response.status).toBe(403);
  });

  it("maps local proof through the static asset binding", async () => {
    const response = await worker.fetch(
      new Request("https://example.test/api/scene"),
      localEnv(),
    );

    expect(await response.json()).toEqual({ path: "/proof/scene.json" });
  });

  it("reports the bundled preview as a complete run", async () => {
    const response = await worker.fetch(
      new Request("https://example.test/api/run-state"),
      localEnv(),
    );

    expect(response.status).toBe(200);
    expect(await response.json()).toEqual({ complete: true, succeeded_count: 3 });
  });

  it("builds a visibly B2-backed public scene", () => {
    const result = buildPublicScene(
      { packet_hash: "packet-123", takes: [{ take_id: "take-a" }] },
      {
        decision_hash_matches: true,
        media_integrity: { status: "verified", verified: true },
        packet_hash: "packet-123",
        verified: true,
      },
    );

    expect(result.proof_scope).toContain("Backblaze B2");
    expect(result.write_enabled).toBe(false);
    expect((result.takes as JsonRecord[])[0].preview_url).toBe("/api/assets/take-a");
  });

  it("accepts only durable URLs from the configured bucket", () => {
    expect(
      keyFromDurableUrl(
        "https://s3.us-east-005.backblazeb2.com/shot-ledger-bucket/a/b.png",
        "shot-ledger-bucket",
        "us-east-005",
      ),
    ).toBe("a/b.png");
    expect(() =>
      keyFromDurableUrl(
        "https://s3.us-east-005.backblazeb2.com/other/a.png",
        "shot-ledger-bucket",
        "us-east-005",
      ),
    ).toThrow("configured B2 bucket");
  });

  it("rejects foreign endpoints and traversal object keys", () => {
    expect(() =>
      keyFromDurableUrl(
        "https://example.com/shot-ledger-bucket/a.png",
        "shot-ledger-bucket",
        "us-east-005",
      ),
    ).toThrow("configured B2 endpoint");
    expect(() =>
      keyFromDurableUrl(
        "https://s3.us-east-005.backblazeb2.com/shot-ledger-bucket/%2E%2E/a.png",
        "shot-ledger-bucket",
        "us-east-005",
      ),
    ).toThrow();
  });

  it("requires the independent receipt to match the decision packet", () => {
    expect(
      receiptMatchesDecision(
        { packet_hash: "new" },
        {
          decision_hash_matches: true,
          media_integrity: { verified: true },
          packet_hash: "old",
          verified: true,
        },
      ),
    ).toBe(false);
  });

  it("serves a B2 scene only with a matching independent receipt", async () => {
    mockB2Objects();

    const response = await worker.fetch(
      new Request("https://example.test/api/scene"),
      b2Env(),
    );
    const scene = (await response.json()) as JsonRecord;

    expect(response.status).toBe(200);
    expect(scene.proof_scope).toContain("reloaded from Backblaze B2");
    expect(scene.write_enabled).toBe(false);
  });

  it("streams a verified B2 take without buffering it into JSON", async () => {
    mockB2Objects();

    const response = await worker.fetch(
      new Request("https://example.test/api/assets/take-a"),
      b2Env(),
    );

    expect(response.status).toBe(200);
    expect(response.headers.get("Content-Type")).toBe("image/png");
    expect(response.headers.get("Cache-Control")).toBe("no-store");
    expect([...new Uint8Array(await response.arrayBuffer())]).toEqual([1, 2, 3]);
  });

  it("refuses B2 media when the verification receipt is stale", async () => {
    mockB2Objects({ packetHash: "old-packet" });
    vi.spyOn(console, "error").mockImplementation(() => undefined);

    const response = await worker.fetch(
      new Request("https://example.test/api/assets/take-a"),
      b2Env(),
    );

    expect(response.status).toBe(503);
    expect(await response.json()).toEqual({ error: "proof temporarily unavailable" });
  });
});

type JsonRecord = Record<string, unknown>;
