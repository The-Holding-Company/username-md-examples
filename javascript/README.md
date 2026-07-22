# JavaScript examples

Node 20+ — no dependencies (built-in `fetch` and `node:crypto`).

```bash
node profile.mjs chris             # fetch a profile (JSON / Markdown / JSON-LD)
node verify-signature.mjs chris    # verify the RFC 9421 response signature
```

| File | What it shows |
|---|---|
| [`profile.mjs`](profile.mjs) | Content negotiation — one URL, four representations |
| [`verify-signature.mjs`](verify-signature.mjs) | Verify `Content-Digest` + Ed25519 `Signature` headers against the published JWKS |

For owner operations (PATCH profile, claims, ATProto bind) the pattern is a
normal `fetch` with `Authorization: Bearer ${process.env.USERNAME_MD_TOKEN}` —
see the [curl examples](../curl/) for every endpoint and payload shape.
