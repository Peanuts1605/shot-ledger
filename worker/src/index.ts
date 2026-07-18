import { AwsClient } from "aws4fetch";

type JsonRecord = Record<string, unknown>;

function jsonResponse(payload: unknown, status = 200): Response {
  return Response.json(payload, {
    status,
    headers: { "Cache-Control": "no-store" },
  });
}

function objectUrl(env: Env, key: string): string {
  const encodedKey = key.split("/").map(encodeURIComponent).join("/");
  return `https://s3.${env.B2_REGION}.backblazeb2.com/${encodeURIComponent(env.B2_BUCKET)}/${encodedKey}`;
}

async function fetchB2(env: Env, key: string): Promise<Response> {
  const client = new AwsClient({
    accessKeyId: env.B2_KEY_ID,
    secretAccessKey: env.B2_APP_KEY,
    service: "s3",
    region: env.B2_REGION,
  });
  const response = await client.fetch(objectUrl(env, key));
  if (!response.ok) {
    throw new Error(`B2 object request failed with status ${response.status}`);
  }
  return response;
}

async function loadB2Json(env: Env, key: string): Promise<JsonRecord> {
  const response = await fetchB2(env, key);
  if (!response.body) throw new Error("B2 JSON object has no response body");
  const reader = response.body.getReader();
  const chunks: Uint8Array[] = [];
  let total = 0;
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    total += value.byteLength;
    if (total > 1_000_000) {
      await reader.cancel();
      throw new Error("B2 JSON object exceeds the one megabyte proof limit");
    }
    chunks.push(value);
  }
  const bytes = new Uint8Array(total);
  let offset = 0;
  for (const chunk of chunks) {
    bytes.set(chunk, offset);
    offset += chunk.byteLength;
  }
  return JSON.parse(new TextDecoder().decode(bytes)) as JsonRecord;
}

function sceneKey(env: Env, filename: string): string {
  return `shot-ledger/scenes/${env.SCENE_ID}/${filename}`;
}

function proofMode(env: Env): "b2" | "local" {
  return env.B2_KEY_ID && env.B2_APP_KEY && env.B2_BUCKET && env.B2_REGION
    ? "b2"
    : "local";
}

export function keyFromDurableUrl(uri: string, bucket: string, region: string): string {
  const url = new URL(uri);
  if (url.protocol !== "https:" || url.hostname !== `s3.${region}.backblazeb2.com`) {
    throw new Error("asset URI does not belong to the configured B2 endpoint");
  }
  const prefix = `/${bucket}/`;
  if (!url.pathname.startsWith(prefix)) {
    throw new Error("asset URI does not belong to the configured B2 bucket");
  }
  const key = decodeURIComponent(url.pathname.slice(prefix.length));
  if (!key || key.split("/").some((segment) => segment === "." || segment === "..")) {
    throw new Error("asset URI contains an invalid B2 object key");
  }
  return key;
}

function canonicalValue(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(canonicalValue);
  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value as JsonRecord)
        .sort(([left], [right]) => left.localeCompare(right))
        .map(([key, entry]) => [key, canonicalValue(entry)]),
    );
  }
  return value;
}

function decisionHashPayload(decision: JsonRecord): JsonRecord {
  const { packet_hash: _packetHash, ...payload } = decision;
  if (Array.isArray(payload.takes)) {
    payload.takes = payload.takes.map((entry) => {
      const { status: _status, ...take } = entry as JsonRecord;
      return take;
    });
  }
  return payload;
}

function decisionStructureValid(decision: JsonRecord): boolean {
  const takes = decision.takes;
  if (
    !Array.isArray(takes) ||
    takes.length !== 3 ||
    typeof decision.keeper_take_id !== "string" ||
    typeof decision.selection_reason !== "string" ||
    !decision.selection_reason.trim() ||
    typeof decision.packet_hash !== "string" ||
    !/^[0-9a-f]{64}$/.test(decision.packet_hash)
  ) {
    return false;
  }
  const takeIds = takes.map((entry) => (entry as JsonRecord).take_id);
  const changedVariables = takes.map((entry) => (entry as JsonRecord).changed_variable);
  if (
    takeIds.some((takeId) => typeof takeId !== "string") ||
    new Set(takeIds).size !== 3 ||
    !takeIds.includes(decision.keeper_take_id) ||
    new Set(changedVariables).size !== 1
  ) {
    return false;
  }
  return takes.every((entry) => {
    const take = entry as JsonRecord;
    const expectedStatus = take.take_id === decision.keeper_take_id ? "keeper" : "rejected";
    return (
      take.status === expectedStatus &&
      typeof take.asset_sha256 === "string" &&
      /^[0-9a-f]{64}$/.test(take.asset_sha256) &&
      typeof take.manifest_hash === "string" &&
      /^[0-9a-f]{64}$/.test(take.manifest_hash)
    );
  });
}

export async function computeDecisionHash(decision: JsonRecord): Promise<string> {
  const canonical = JSON.stringify(canonicalValue(decisionHashPayload(decision))).replace(
    /[\u007f-\uffff]/g,
    (character) => `\\u${character.charCodeAt(0).toString(16).padStart(4, "0")}`,
  );
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(canonical));
  return [...new Uint8Array(digest)]
    .map((byte) => byte.toString(16).padStart(2, "0"))
    .join("");
}

export async function receiptMatchesDecision(
  decision: JsonRecord,
  verification: JsonRecord,
): Promise<boolean> {
  const mediaIntegrity = verification.media_integrity as JsonRecord | undefined;
  try {
    return (
      decisionStructureValid(decision) &&
      verification.verified === true &&
      verification.decision_hash_matches === true &&
      mediaIntegrity?.verified === true &&
      typeof decision.packet_hash === "string" &&
      decision.packet_hash === verification.packet_hash &&
      decision.packet_hash === await computeDecisionHash(decision)
    );
  } catch {
    return false;
  }
}

export async function buildPublicScene(
  decision: JsonRecord,
  verification: JsonRecord,
): Promise<JsonRecord> {
  const takes = (decision.takes as JsonRecord[]).map((take) => ({
    ...take,
    preview_url: `/api/assets/${take.take_id as string}`,
  }));
  const proofVerified = await receiptMatchesDecision(decision, verification);
  return {
    ...decision,
    takes,
    integrity: proofVerified ? "hash matches" : "hash mismatch",
    media_integrity: verification.media_integrity,
    proof_scope: proofVerified
      ? "Live provider evidence reloaded from Backblaze B2"
      : "B2 provider evidence is present, but its verification receipt does not match",
    storage_mode: "Backblaze B2",
    write_enabled: false,
  };
}

async function localApi(request: Request, env: Env, path: string): Promise<Response> {
  if (path === "/api/scene") {
    return env.ASSETS.fetch(new URL("/proof/scene.json", request.url));
  }
  if (path === "/api/export") {
    return env.ASSETS.fetch(new URL("/proof/decision.json", request.url));
  }
  if (path === "/api/run-state") {
    return jsonResponse({ complete: true, succeeded_count: 3 });
  }
  const match = path.match(/^\/api\/assets\/(take-[abc])$/);
  if (match) {
    return env.ASSETS.fetch(new URL(`/proof/${match[1]}.png`, request.url));
  }
  return jsonResponse({ error: "not found" }, 404);
}

async function b2Api(env: Env, path: string): Promise<Response> {
  if (path === "/api/scene") {
    const [decision, verification] = await Promise.all([
      loadB2Json(env, sceneKey(env, "decision.json")),
      loadB2Json(env, sceneKey(env, "verification.json")),
    ]);
    return jsonResponse(await buildPublicScene(decision, verification));
  }
  if (path === "/api/export") {
    const [decision, verification] = await Promise.all([
      loadB2Json(env, sceneKey(env, "decision.json")),
      loadB2Json(env, sceneKey(env, "verification.json")),
    ]);
    if (!(await receiptMatchesDecision(decision, verification))) {
      throw new Error("B2 decision and verification receipt do not match");
    }
    return jsonResponse(decision);
  }
  if (path === "/api/run-state") {
    const state = await loadB2Json(env, sceneKey(env, "generation-state.json"));
    const slots = state.slots as JsonRecord[];
    const succeeded = slots.filter((slot) => slot.status === "succeeded");
    return jsonResponse({
      ...state,
      complete: succeeded.length === slots.length,
      pending_take_ids: slots
        .filter((slot) => slot.status !== "succeeded")
        .map((slot) => slot.take_id),
      retry_command: "python -m shot_ledger.retry_real_proof",
      storage_mode: "Backblaze B2",
      succeeded_count: succeeded.length,
    });
  }
  const match = path.match(/^\/api\/assets\/(take-[abc])$/);
  if (match) {
    const [decision, verification] = await Promise.all([
      loadB2Json(env, sceneKey(env, "decision.json")),
      loadB2Json(env, sceneKey(env, "verification.json")),
    ]);
    if (!(await receiptMatchesDecision(decision, verification))) {
      throw new Error("B2 decision and verification receipt do not match");
    }
    const take = (decision.takes as JsonRecord[]).find(
      (candidate) => candidate.take_id === match[1],
    );
    if (!take) return jsonResponse({ error: "take not found" }, 404);
    const response = await fetchB2(
      env,
      keyFromDurableUrl(take.asset_uri as string, env.B2_BUCKET, env.B2_REGION),
    );
    return new Response(response.body, {
      headers: {
        "Cache-Control": "no-store",
        "Content-Type": response.headers.get("Content-Type") || "image/png",
      },
    });
  }
  return jsonResponse({ error: "not found" }, 404);
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    if (url.pathname === "/healthz") {
      return jsonResponse({ mode: proofMode(env), status: "ok", write_enabled: false });
    }
    if (url.pathname === "/api/decision" && request.method === "POST") {
      return jsonResponse({ error: "public proof is read-only" }, 403);
    }
    if (url.pathname.startsWith("/api/") && request.method !== "GET") {
      return jsonResponse({ error: "method not allowed" }, 405);
    }
    try {
      if (url.pathname.startsWith("/api/")) {
        return proofMode(env) === "b2"
          ? await b2Api(env, url.pathname)
          : await localApi(request, env, url.pathname);
      }
      return await env.ASSETS.fetch(request);
    } catch (error) {
      console.error(JSON.stringify({
        event: "proof_request_failed",
        message: error instanceof Error ? error.message : "unknown error",
        path: url.pathname,
      }));
      return jsonResponse({ error: "proof temporarily unavailable" }, 503);
    }
  },
} satisfies ExportedHandler<Env>;
