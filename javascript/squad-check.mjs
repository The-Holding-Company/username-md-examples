#!/usr/bin/env node
// Squad check: is <handle> on right now, and where do you join?
//
// Resolution order:
//   1. SRV  _playing._tcp.<handle>.username.md  -> live join target   (IN DEVELOPMENT)
//   2. TXT  _presence.<handle>.username.md      -> structured presence (IN DEVELOPMENT)
//   3. GET  /v1/users/<handle>/profile          -> roster + links      (live today)
//
// Presence records are the gamer-tier surface (https://username.md/gamers.html)
// and are IN DEVELOPMENT: until announced in https://username.md/llms.txt, expect
// empty answers and the profile fallback. Treat NXDOMAIN / empty answers as
// "not published", never as an error.
//
// Usage: node squad-check.mjs chris     (Node 20+, no dependencies)

import { resolveSrv, resolveTxt } from "node:dns/promises";

const handle = process.argv[2] ?? "chris";
const zone = `${handle}.username.md`;

// "No records" is a normal answer here, not a failure.
const lookup = (fn, name) =>
  fn(name).catch((err) =>
    ["ENOTFOUND", "ENODATA", "ESERVFAIL", "ETIMEOUT"].includes(err.code) ? [] : Promise.reject(err)
  );

let online = false;

for (const srv of await lookup(resolveSrv, `_playing._tcp.${zone}`)) {
  online = true;
  console.log(`IN GAME — join ${srv.name}:${srv.port}`);
}

const presence = {};
for (const chunks of await lookup(resolveTxt, `_presence.${zone}`)) {
  for (const part of chunks) {
    const i = part.indexOf("=");
    if (i > 0) presence[part.slice(0, i)] = part.slice(i + 1);
  }
}
if (Object.keys(presence).length) {
  online = online || presence.live === "true";
  console.log("presence:", presence);
}

if (!online) {
  // Presence not published (in development) — the profile API is live today.
  console.log(`${handle}: no live presence published — falling back to the profile API`);
  const resp = await fetch(`https://username.md/v1/users/${handle}/profile`, {
    headers: { accept: "application/json" },
  });
  if (!resp.ok) throw new Error(`profile fetch failed: ${resp.status}`);
  const profile = await resp.json();
  console.log(`/u/${handle} — ${profile.name ?? handle}: ${profile.tagline ?? ""}`);
  for (const link of profile.links ?? []) console.log(`  ${link.label}: ${link.href}`);
}
