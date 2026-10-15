# JavaScript examples

Node 20+ — no dependencies (built-in `fetch` and `node:crypto`).

```bash
node profile.mjs chris             # fetch a profile (JSON / Markdown / JSON-LD)
node verify-signature.mjs chris    # verify the RFC 9421 response signature
node squad-check.mjs chris         # gamer presence: on now? where to join?
```

| File | What it shows |
|---|---|
| [`profile.mjs`](profile.mjs) | Content negotiation — one URL, four representations |
| [`verify-signature.mjs`](verify-signature.mjs) | Verify `Content-Digest` + Ed25519 `Signature` headers against the published JWKS |
| [`squad-check.mjs`](squad-check.mjs) | Gamer presence: resolve `_playing` SRV / `_presence` TXT (**in development** — empty until announced in [llms.txt](https://username.md/llms.txt)), fall back to the live profile API |

For owner operations (PATCH profile, claims, ATProto bind) the pattern is a
normal `fetch` with `Authorization: Bearer ${process.env.USERNAME_MD_TOKEN}` —
see the [curl examples](../curl/) for every endpoint and payload shape.
