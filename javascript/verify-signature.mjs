#!/usr/bin/env node
// Verify a username.md API response signature (RFC 9421 + RFC 9530).
// Usage: node verify-signature.mjs <handle> [base_url]

import { createPublicKey, createHash, verify } from "node:crypto";

const handle = process.argv[2] ?? "chris";
const BASE = process.argv[3] ?? "https://username.md";
const host = new URL(BASE).host;

// 1. Fetch the platform verification key (kid: platform-ed25519).
const jwks = await (await fetch(`${BASE}/.well-known/http-message-signatures-directory`)).json();
const jwk = jwks.keys.find((k) => k.kid === "platform-ed25519");
const key = createPublicKey({ key: jwk, format: "jwk" });

// 2. Fetch any API response.
const resp = await fetch(`${BASE}/v1/users/${handle}/profile`, {
  headers: { accept: "application/json" },
});
const body = Buffer.from(await resp.arrayBuffer());

// 3. Check the body digest (RFC 9530).
const digest = resp.headers.get("content-digest");
const expected = `sha-256=:${createHash("sha256").update(body).digest("base64")}:`;
if (digest !== expected) throw new Error("Content-Digest does not match body");

// 4. Rebuild the RFC 9421 §2.5 signature base and verify the Ed25519 signature.
const params = resp.headers.get("signature-input").replace(/^sig1=/, "");
const sig = Buffer.from(resp.headers.get("signature").slice("sig1=:".length, -1), "base64");
const base = Buffer.from(
  `"content-digest": ${digest}\n"@authority": ${host}\n"@signature-params": ${params}`,
);
if (!verify(null, base, key, sig)) throw new Error("signature verification FAILED");

console.log(`verified: response for '${handle}' signed by ${host}`);
