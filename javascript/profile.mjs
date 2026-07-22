#!/usr/bin/env node
// Fetch a username.md profile in each representation.
// Usage: node profile.mjs <handle> [base_url]

const handle = process.argv[2] ?? "chris";
const BASE = process.argv[3] ?? "https://username.md";
const url = `${BASE}/v1/users/${handle}/profile`;

// Structured JSON — what an agent or integration usually wants.
const profile = await (await fetch(url, { headers: { accept: "application/json" } })).json();
console.log(`handle : ${profile.handle}`);
console.log(`did    : ${profile.did}`);
console.log(`name   : ${profile.name ?? ""}`);
console.log(`links  : ${(profile.links ?? []).length}`);

// schema.org/Person JSON-LD — for knowledge graphs.
const jsonld = await (await fetch(url, { headers: { accept: "application/ld+json" } })).json();
console.log(`\nJSON-LD @type: ${jsonld["@type"]}`);

// Markdown — terminal- and LLM-friendly.
const md = await (await fetch(url, { headers: { accept: "text/markdown" } })).text();
console.log("\n--- markdown ---");
console.log(md.trim().slice(0, 400));

// Signed JWS bundle — the whole profile as a verifiable artifact.
const jws = await (await fetch(url, { headers: { accept: "application/jose+json" } })).text();
const header = JSON.parse(Buffer.from(jws.split(".")[0], "base64url").toString());
console.log(`\nJWS alg: ${header.alg} | segments: ${jws.split(".").length}`);
